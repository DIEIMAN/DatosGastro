"""Las 22 zonas del Atlas recortadas sobre el Relevamiento de Usos del Suelo.

Da el **segundo rango calibrado** del factor de captura, para poner al lado del que ya se calculó
contra habilitaciones. Decisión de Diego (2026-08-05): las habilitaciones siguen siendo la base
del rango de control —una sola regla de vigencia para toda la Ciudad y cuatro puntos de
calibración—; el Relevamiento entra como segunda columna, no la reemplaza.

Y con un requisito que no es opcional: **el Relevamiento es rotativo**, un año por barrio, y 19
de las 22 zonas cruzan más de un barrio. Casi toda zona recortada sobre esta fuente mezcla 2022,
2023 y 2024. Esa mezcla se calcula por zona y se declara junto al número. Un rango de control
calculado sin declararla arrastra ruido de añada que no tiene nada que ver con el método de
relevamiento, que es lo que el control quiere medir.

Decisiones de método, explícitas:
  - La unidad es la **parcela** (`SMP`), contada por centroide dentro de la envolvente, para que
    sea el mismo punto en polígono que se usa con las direcciones del padrón.
  - Se aplica la **misma precedencia de envolventes** que `build_capa_homogenea.py`, así las dos
    columnas hablan del mismo perímetro.
  - La mezcla de añadas se calcula sobre las parcelas efectivamente contadas, que es lo que pesa
    el número, y se contrasta contra el crosswalk de superficie que dejó Diego.

Insumo previo (no lo baja este script): el SHP del Relevamiento, descomprimido en
`outputs/fuentes_externas/usos_suelo/shp/`. URL en el docstring de `perfilar_usos_suelo.py`
(recurso SHP). El SHP viene en UTF-8 correcto: el doble encoding es un defecto del CSV, no de
esta fuente.

Uso:
  python scripts/barrido_ciudad/capa_rus_por_zona.py
"""
from __future__ import annotations

import glob
import io
import sys
import unicodedata
from pathlib import Path

import geopandas as gpd
import pandas as pd
import pyogrio

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_capa_homogenea import (  # noqa: E402  (import tras ajustar sys.path)
    CIFRAS_ATLAS,
    ENVOLVENTES,
    PRECEDENCIA_ENVOLVENTES,
)
from perfilar_usos_suelo import anillos  # noqa: E402

BARRIDO = ROOT / "outputs" / "BARRIDO_CIUDAD_2026-08"
OUT_DIR = BARRIDO / "generado"
SHP_DIR = ROOT / "outputs" / "fuentes_externas" / "usos_suelo" / "shp"
CROSSWALK = BARRIDO / "crosswalk_zona_barrio.csv"
BARRIOS = ROOT / "data" / "raw" / "geo_barrios.geojson"


def plegar(texto: object) -> str:
    return unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode().upper().strip()


def ruta_shp() -> str:
    rutas = glob.glob(str(SHP_DIR / "*.shp"))
    if not rutas:
        raise FileNotFoundError(f"falta el SHP del Relevamiento en {SHP_DIR}")
    return rutas[0]


def crs_fuente() -> object:
    """CRS nativo del SHP: Gauss-Krüger local de Buenos Aires, en metros.

    Todo el trabajo geométrico se hace en este CRS y no en grados. Dos razones: los centroides y
    las áreas en coordenadas geográficas salen mal, y el `bbox` de pyogrio se interpreta en el CRS
    del dataset —pasarle grados devuelve cero features sin error, que es como se perdieron los
    conteos la primera vez—.
    """
    return pyogrio.read_info(ruta_shp())["crs"]


def cargar_parcelas_gastronomicas() -> gpd.GeoDataFrame:
    """Parcelas unicomerciales del Relevamiento, con su anillo, año y estado, en CRS nativo."""
    nucleo, ampliado = anillos()
    parcelas = pyogrio.read_dataframe(
        ruta_shp(),
        columns=["SMP", "BARRIO", "TIPO1", "TIPO2", "ESTADO", "AÑO"],
        where="TIPO1 = 'UNICOMERCIAL'",
    )
    parcelas = parcelas[parcelas.TIPO2.isin(ampliado)].rename(columns={"AÑO": "ANIO"})
    parcelas["es_nucleo"] = parcelas.TIPO2.isin(nucleo)
    parcelas["es_activo"] = parcelas.ESTADO == "ACTIVO"
    parcelas["geometry"] = parcelas.geometry.centroid
    return parcelas


def envolventes_en_crs_fuente() -> gpd.GeoDataFrame:
    return gpd.read_file(ENVOLVENTES)[["referencia_id", "nombre", "geometry"]].to_crs(crs_fuente())


def perimetros_con_precedencia() -> list[tuple[str, str, object]]:
    """Envolventes editoriales con el solape ya descontado, igual que en la capa de barrios."""
    envolventes = envolventes_en_crs_fuente().sort_values(PRECEDENCIA_ENVOLVENTES)
    envolventes = envolventes.reset_index(drop=True)

    resultado = []
    for posicion, zona in envolventes.iterrows():
        perimetro = zona.geometry
        for previa in envolventes.iloc[:posicion].itertuples():
            if perimetro.intersects(previa.geometry):
                perimetro = perimetro.difference(previa.geometry)
        resultado.append((zona.referencia_id, zona.nombre, perimetro))
    return resultado


def parcelas_relevadas_por_zona(perimetros: list[tuple[str, str, object]]) -> dict[str, int]:
    """Cuántas parcelas de cualquier uso relevó la fuente dentro de cada perímetro.

    Hace falta para distinguir dos ceros que no significan lo mismo: «no hay gastronomía acá» y
    «la fuente no cubre este perímetro». R07 · Costanera Norte es el segundo caso —cero parcelas
    de cualquier tipo, porque es tierra no parcelada sobre el río— y ahí el factor de captura no
    existe, no es 0 %.
    """
    conteo = {}
    for rid, _, perimetro in perimetros:
        todas = pyogrio.read_dataframe(ruta_shp(), columns=["SMP"], bbox=perimetro.bounds)
        if len(todas):
            todas["geometry"] = todas.geometry.centroid
            conteo[rid] = int(todas[todas.within(perimetro)].SMP.nunique())
        else:
            conteo[rid] = 0
    return conteo


# Umbrales de cobertura, en parcelas relevadas por hectárea. La Ciudad entera tiene 15,6
# parcelas/ha relevadas y la zona más floja de las 22 —fuera de las dos excepciones— tiene 10,8.
# R07 · Costanera Norte tiene 0,03 y R04 · Puerto Madero 1,48: son tierra no parcelada sobre el
# río y grandes lotes de diques. Entre 0,03 y 10,8 no hay ninguna zona, así que el corte no está
# ajustado a mano: separa dos situaciones que la fuente distingue por sí misma.
COBERTURA_NULA = 1.0
COBERTURA_PARCIAL = 5.0


def clasificar_cobertura(parcelas_por_ha: float) -> str:
    if parcelas_por_ha < COBERTURA_NULA:
        return "sin cobertura"
    if parcelas_por_ha < COBERTURA_PARCIAL:
        return "cobertura parcial"
    return "si"


def capa_por_zona(parcelas: gpd.GeoDataFrame) -> pd.DataFrame:
    """Parcelas gastronómicas por zona, con la mezcla de añadas de las parcelas contadas."""
    perimetros = perimetros_con_precedencia()
    relevadas = parcelas_relevadas_por_zona(perimetros)

    filas = {}
    for rid, nombre, perimetro in perimetros:
        dentro = parcelas[parcelas.within(perimetro)]
        activas = dentro[dentro.es_activo]
        nucleo = activas[activas.es_nucleo]

        hectareas = perimetro.area / 10_000
        densidad = round(relevadas[rid] / hectareas, 2)
        mezcla = nucleo.ANIO.value_counts(normalize=True).mul(100).round(1).sort_index()
        filas[rid] = {
            "zona": nombre,
            "hectareas": round(hectareas, 1),
            "parcelas_relevadas": relevadas[rid],
            "parcelas_por_ha": densidad,
            "cobertura_rus": clasificar_cobertura(densidad),
            "rus_nucleo": int(nucleo.SMP.nunique()),
            "rus_ampliado": int(activas.SMP.nunique()),
            "rus_inactivo": int(dentro[~dentro.es_activo].SMP.nunique()),
            "anios": "/".join(str(a) for a in sorted(nucleo.ANIO.unique())),
            "mezcla_anadas": " ".join(f"{a}:{pct:g}%" for a, pct in mezcla.items()),
            "anada_dominante_pct": float(mezcla.max()) if len(mezcla) else float("nan"),
            "barrios_tocados": int(nucleo.BARRIO.nunique()),
        }
    return pd.DataFrame(filas).T.rename_axis("rid")


def reparto_por_barrio(perimetros: list[tuple[str, str, object]]) -> dict[str, dict[str, float]]:
    """Porcentaje de la superficie de cada zona que cae en cada barrio, umbral 1 %.

    El denominador es la superficie total de la zona, no la suma de los recortes por barrio: hay
    zonas con superficie sobre el río que no pertenece a ningún barrio (R07 tiene un 3,8 % así) y
    esa parte tiene que seguir contando en el denominador.
    """
    barrios = gpd.read_file(BARRIOS)[["nombre", "geometry"]].to_crs(crs_fuente())
    reparto = {}
    for rid, _, proyectado in perimetros:
        total = proyectado.area
        recortes = barrios[barrios.intersects(proyectado)].copy()
        # Ojo: no llamar a esta columna `area`. GeoDataFrame ya tiene una propiedad `.area` con el
        # área de las geometrías completas y el atributo gana sobre la columna.
        recortes["area_recorte"] = [g.intersection(proyectado).area for g in recortes.geometry]
        reparto[rid] = {
            plegar(r.nombre): round(100 * r.area_recorte / total, 1)
            for r in recortes.itertuples() if 100 * r.area_recorte / total >= 1
        }
    return reparto


def verificar_crosswalk(p) -> None:
    """Contrasta el crosswalk de Diego contra las dos geometrías posibles de cada zona.

    El crosswalk se calculó sobre las envolventes **crudas**. La capa de conteo usa las
    envolventes con el solape descontado. Para 20 de las 22 zonas es lo mismo; para R12 y R18 no,
    y ahí la mezcla de añadas que corresponde declarar es la del perímetro que efectivamente se
    contó, no la del crosswalk.
    """
    if not CROSSWALK.exists():
        p("  [!] no está el crosswalk; se omite el contraste")
        return

    crosswalk = pd.read_csv(CROSSWALK)
    crudas = [(z.referencia_id, z.nombre, z.geometry)
              for z in envolventes_en_crs_fuente().itertuples()]

    sin_precedencia = reparto_por_barrio(crudas)
    con_precedencia = reparto_por_barrio(perimetros_con_precedencia())

    def desvio(rid: str, calculado: dict[str, float]) -> tuple[float, list[str], list[str]]:
        declarado = {plegar(r.barrio): r.pct_zona_en_barrio
                     for r in crosswalk[crosswalk.rid == rid].itertuples()}
        comunes = set(declarado) & set(calculado)
        return (
            max((abs(declarado[b] - calculado[b]) for b in comunes), default=0.0),
            sorted(set(declarado) - set(calculado)),
            sorted(set(calculado) - set(declarado)),
        )

    p("CONTRASTE contra crosswalk_zona_barrio.csv (umbral 1 % de superficie)")
    exactas = sum(1 for rid in crosswalk.rid.unique() if desvio(rid, sin_precedencia[rid])[0] <= 0.1)
    p(f"  contra envolventes crudas: {exactas} de {crosswalk.rid.nunique()} zonas reproducen "
      "el crosswalk con desvío ≤ 0,1 pp")
    p("  el crosswalk está calculado sobre las envolventes crudas, sin descontar el solape.")
    p("")
    p("  zonas donde la precedencia cambia el reparto por barrio (y por lo tanto la añada):")
    for rid in sorted(crosswalk.rid.unique()):
        d_crudo = desvio(rid, sin_precedencia[rid])[0]
        d_prec, faltan, sobran = desvio(rid, con_precedencia[rid])
        if d_prec > 1.0:
            p(f"    {rid}: desvío {d_prec:.1f} pp contra el crosswalk "
              f"(sobre envolvente cruda sería {d_crudo:.1f} pp) | faltan {faltan} sobran {sobran}")
            p(f"      crosswalk {crosswalk[crosswalk.rid == rid].set_index('barrio').pct_zona_en_barrio.to_dict()}")
            p(f"      perímetro contado {con_precedencia[rid]}")
    p(f"  zonas que cruzan más de un barrio: "
      f"{int((crosswalk.groupby('rid').size() > 1).sum())} de {crosswalk.rid.nunique()}")
    p("")


def factor_captura_dos_bases(zonas: pd.DataFrame, p) -> pd.DataFrame:
    """El factor de captura con las dos bases: habilitaciones (control) y Relevamiento (columna)."""
    cifras = pd.read_csv(CIFRAS_ATLAS)
    habilitaciones = pd.read_csv(BARRIDO / "factor_captura_22_zonas.csv")

    tabla = cifras.merge(
        habilitaciones[["rid", "dir_nucleo", "captura_%"]].rename(
            columns={"dir_nucleo": "hab_nucleo", "captura_%": "captura_hab_%"}
        ),
        on="rid", how="left",
    ).merge(zonas.reset_index()[["rid", "rus_nucleo", "parcelas_relevadas", "parcelas_por_ha",
                                 "cobertura_rus", "mezcla_anadas", "anada_dominante_pct",
                                 "barrios_tocados"]],
            on="rid", how="left")

    tabla["captura_rus_%"] = (100 * tabla.rus_nucleo.astype(float) / tabla.relevado).round(1)
    tabla["rus_sobre_hab"] = (tabla.rus_nucleo.astype(float) / tabla.hab_nucleo).round(2)
    # Donde la fuente no tiene parcelas, el factor de captura no existe: no es 0 %. Si se dejara
    # en 0 entraría en las medianas y en el rango como si fuera una medición.
    sin_cobertura = tabla.cobertura_rus == "sin cobertura"
    tabla.loc[sin_cobertura, ["captura_rus_%", "rus_sobre_hab"]] = float("nan")

    con_cifra = tabla[tabla.relevado.notna()]
    p("FACTOR DE CAPTURA CON LAS DOS BASES")
    p("  base de control: habilitaciones. Segunda columna: Relevamiento de Usos del Suelo.")
    p("")
    columnas = ["rid", "zona_publicada", "metodo", "relevado", "hab_nucleo", "captura_hab_%",
                "rus_nucleo", "captura_rus_%", "anada_dominante_pct", "barrios_tocados"]
    p(con_cifra[columnas].sort_values("captura_hab_%", ascending=False).to_string(index=False))
    p("")

    p("  rangos por método, con las dos bases:")
    resumen = con_cifra.groupby("metodo").agg(
        zonas=("rid", "size"),
        captura_hab_mediana=("captura_hab_%", "median"),
        captura_hab_min=("captura_hab_%", "min"),
        captura_hab_max=("captura_hab_%", "max"),
        captura_rus_mediana=("captura_rus_%", "median"),
        captura_rus_min=("captura_rus_%", "min"),
        captura_rus_max=("captura_rus_%", "max"),
    ).round(1)
    p(resumen.to_string())
    p("")

    propio = con_cifra[con_cifra.metodo == "relevamiento propio"]
    p(f"  rango de control con habilitaciones (relevamiento propio, 4 zonas): "
      f"{propio['captura_hab_%'].min():.1f} – {propio['captura_hab_%'].max():.1f} %")
    p(f"  rango con Relevamiento, para la misma cuatro:                      "
      f"{propio['captura_rus_%'].min():.1f} – {propio['captura_rus_%'].max():.1f} %")
    p("")
    p("  mezcla de añadas de cada zona con cifra publicada (esto se declara en la ficha):")
    for fila in con_cifra.sort_values("anada_dominante_pct").itertuples():
        p(f"    {fila.rid} · {fila.zona_publicada:<32} {fila.mezcla_anadas}")
    p("")
    return tabla


def main() -> int:
    buffer = io.StringIO()

    def p(*args):
        print(*args, file=buffer)

    parcelas = cargar_parcelas_gastronomicas()
    p("Las 22 zonas del Atlas sobre el Relevamiento de Usos del Suelo")
    p("=" * 78)
    p("")
    p(f"parcelas gastronómicas unicomerciales leídas del SHP: {len(parcelas):,}")
    p(f"  activas: {int(parcelas.es_activo.sum()):,} | del anillo núcleo: {int(parcelas.es_nucleo.sum()):,}")
    p("")

    zonas = capa_por_zona(parcelas)
    verificar_crosswalk(p)
    tabla = factor_captura_dos_bases(zonas, p)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    zonas.to_csv(OUT_DIR / "capa_rus_22_zonas.csv", encoding="utf-8")
    tabla.to_csv(OUT_DIR / "factor_captura_22_zonas_dos_bases.csv", index=False, encoding="utf-8")
    (OUT_DIR / "CONTROLES_RUS_22_ZONAS.txt").write_text(buffer.getvalue(), encoding="utf-8")

    print(buffer.getvalue())
    print(f"escrito en {OUT_DIR.relative_to(ROOT)}: capa_rus_22_zonas.csv, "
          "factor_captura_22_zonas_dos_bases.csv, CONTROLES_RUS_22_ZONAS.txt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
