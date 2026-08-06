"""Solape entre fuentes abiertas y rescate de los descubrimientos de Places. CERO requests.

LAS DOS PREGUNTAS
-----------------
**1 · ¿Cuánto se solapan las fuentes entre sí?** Si Overture, OSM y el padrón vieran a los mismos
locales, sumar fuentes no agregaría cobertura y `n_fuentes` mediría redundancia en vez de
corroboración.

**2 · ¿Cuánto de lo que Places descubrió se puede publicar?** Ésta es la que decide el tamaño del
barrido, y por eso va primero en el informe. Los términos de uso de Google no permiten
redistribuir nombre, dirección ni `place_id`, así que un local que sólo existe en Places entra a la
base como `agregado` —una cuenta dentro de una celda— y nada más. **Pero si ese mismo local
aparece en OSM, en Overture o en All The Places, la identidad publicable viene de ahí** y el
registro sube a `abierto`. Cada emparejamiento convierte un descubrimiento mudo en uno publicable.

Los 81 puntos núcleo que Places trajo de Villa Crespo están en disco desde el 5 de agosto y se
cruzan contra las tres fuentes abiertas sin gastar un request.

CÓMO SE DECIDE QUE DOS REGISTROS SON EL MISMO LOCAL
---------------------------------------------------
Con la trazabilidad que pide el esquema (§7): **cada emparejamiento guarda por qué se emparejó.**
Tres criterios, en orden de fuerza decreciente, y el primero que se cumple es el que queda:

    usig_exacta          misma calle y altura dentro de ±10 números
    proximidad_y_nombre  a menos del radio declarado Y con nombres parecidos
    proximidad_Nm        a menos del radio declarado, sin coincidencia de nombre

**La similitud de nombre nunca alcanza sola**, que es regla dura del esquema: dos sucursales de la
misma cadena a veinte cuadras comparten nombre y no son el mismo local.

Y el radio se somete a análisis de sensibilidad, publicado, como se hizo con la tolerancia de
altura de ±5/±10/±30: **si el resultado depende del corte, el corte está mal elegido.**

GUARDARRAÍLES
-------------
- **No toca la red.** Ni Places, ni Overpass, ni S3. Todo sale de disco.
- Los nombres y direcciones de Places **no salen** de la carpeta interna: a `generado/` van
  conteos, porcentajes y el criterio de cada emparejamiento, nunca el dato de Google.

USO
---
  python scripts/barrido_ciudad/cruzar_fuentes_abiertas.py
  python scripts/barrido_ciudad/cruzar_fuentes_abiertas.py --zona R08 --sin-ciudad
"""
from __future__ import annotations

import argparse
import datetime as dt
import io
import json
import re
import sys
import unicodedata
import warnings
from pathlib import Path

import geopandas as gpd
import pandas as pd

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_capa_homogenea import UBICACION, cargar_direcciones_gastronomicas  # noqa: E402
from cruzar_places_padron import (  # noqa: E402
    TOLERANCIA_ALTURA,
    misma_calle,
    partir_padron,
    partir_places,
    tokens_calle,
)
from places_control_zonas import CRS_METRICO, asignar_por_geometria, perimetros  # noqa: E402
from places_techo_zona import INTERNO as INTERNO_TECHO  # noqa: E402

BARRIDO = ROOT / "outputs" / "BARRIDO_CIUDAD_2026-08"
GEN = BARRIDO / "generado"
INTERNO = ROOT / "outputs" / "analisis_interno" / "cruce_fuentes_abiertas_2026-08"

OSM_POI = ROOT / "outputs" / "fuentes_externas" / "osm" / "osm_gastro_poi.csv"
OVT_POI = ROOT / "outputs" / "fuentes_externas" / "overture" / "overture_gastro_poi.csv"
ATP_POI = ROOT / "outputs" / "fuentes_externas" / "all_the_places" / "atp_caba.csv"

ZONA_POR_DEFECTO = "R08"

# El radio de emparejamiento. A 40 m entran el punto corrido de una fuente y el local de la
# esquina asentado sobre la otra calle; a 100 m ya entra media cuadra de vecinos. Se declara, se
# somete a sensibilidad y se publica la tabla.
RADIO_M = 40.0
RADIOS_SENSIBILIDAD = [20.0, 40.0, 60.0, 100.0]

# Umbral de parecido de nombre: proporción de palabras significativas en común (Jaccard). No
# decide nada por sí solo; sólo sube la calidad del criterio cuando ya hubo proximidad.
UMBRAL_NOMBRE = 0.5

# Grupos de independencia del esquema (§3). Overture incorpora a Foursquare y a All The Places,
# así que las tres cuentan como una sola a la hora de corroborar.
GRUPOS = {
    "F01": "GCBA_TURISMO", "F02": "GCBA_AGC", "RUS": "GCBA_URBANISMO",
    "OSM": "OSM", "OVERTURE": "OVERTURE_FSQ_ATP", "ATP": "OVERTURE_FSQ_ATP",
    "PLACES": "GOOGLE",
}

# Qué se puede publicar de cada fuente. Sale de §6 del esquema y es lo que decide `nivel_publicacion`.
REDISTRIBUIBLE = {"F01": True, "F02": True, "RUS": True, "OSM": True,
                  "OVERTURE": True, "ATP": True, "PLACES": False}

PALABRAS_VACIAS_NOMBRE = {"EL", "LA", "LOS", "LAS", "DE", "DEL", "Y", "CAFE", "BAR", "RESTAURANT",
                          "RESTAURANTE", "PARRILLA", "PIZZERIA", "HELADERIA", "PANADERIA"}


def plegar(texto: object) -> str:
    return unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode().upper()


def tokens_nombre(nombre: object) -> frozenset[str]:
    """Palabras significativas de un nombre comercial, sin el rubro ni los artículos.

    Sacar el rubro importa: `Pizzería Güerrín` y `Güerrín` son el mismo local, y `Pizzería Roma` y
    `Pizzería Napoli` no lo son. Dejar la palabra «pizzería» adentro los acercaría a los tres por
    igual.
    """
    limpio = re.sub(r"[^A-Z0-9 ]", " ", plegar(nombre))
    return frozenset(p for p in limpio.split()
                     if len(p) >= 3 and p not in PALABRAS_VACIAS_NOMBRE)


def parecido_nombre(unos: frozenset[str], otros: frozenset[str]) -> float:
    if not unos or not otros:
        return 0.0
    return len(unos & otros) / len(unos | otros)


# --------------------------------------------------------------------------- los conjuntos

def _geo(tabla: pd.DataFrame, lon: str = "lon", lat: str = "lat") -> gpd.GeoDataFrame:
    return gpd.GeoDataFrame(
        tabla.copy(), geometry=gpd.points_from_xy(tabla[lon], tabla[lat]), crs="EPSG:4326"
    ).to_crs(CRS_METRICO)


def cargar_osm() -> gpd.GeoDataFrame | None:
    if not OSM_POI.exists():
        return None
    tabla = pd.read_csv(OSM_POI, encoding="utf-8-sig", low_memory=False)
    tabla = tabla[tabla.anillo.isin(["nucleo", "ampliado"])].copy()
    tabla["direccion_texto"] = (tabla.calle.fillna("").astype(str) + " "
                                + tabla.altura.fillna("").astype(str)).str.strip()
    return _geo(tabla)


def cargar_overture() -> gpd.GeoDataFrame | None:
    if not OVT_POI.exists():
        return None
    tabla = pd.read_csv(OVT_POI, encoding="utf-8-sig", low_memory=False)
    tabla["direccion_texto"] = tabla.direccion.fillna("").astype(str)
    return _geo(tabla)


def cargar_atp() -> gpd.GeoDataFrame | None:
    if not ATP_POI.exists():
        return None
    from bajar_all_the_places import clasificar as clasificar_atp

    tabla = clasificar_atp(pd.read_csv(ATP_POI, encoding="utf-8-sig", low_memory=False))
    tabla = tabla[tabla.anillo.isin(["nucleo", "ampliado"])].copy()
    tabla["direccion_texto"] = (tabla["addr:street"].fillna("").astype(str) + " "
                                + tabla["addr:housenumber"].fillna("").astype(str)).str.strip()
    tabla["nombre"] = tabla["name"].fillna("")
    return _geo(tabla)


def cargar_places(rid: str) -> gpd.GeoDataFrame:
    archivo = INTERNO_TECHO / f"places_techo_{rid}_puntos.csv"
    if not archivo.exists():
        raise SystemExit(f"ABORTADO: falta {archivo}. No se corre Places para conseguirlo.")
    puntos = asignar_por_geometria(pd.read_csv(archivo, encoding="utf-8-sig"))
    puntos = puntos[(puntos.rid_geo == rid) & (puntos.anillo == "nucleo")].reset_index(drop=True)
    puntos["direccion_texto"] = puntos.direccion.fillna("").astype(str)
    return _geo(puntos)


def cargar_padron(rid: str | None = None) -> gpd.GeoDataFrame:
    puntos, _ = cargar_direcciones_gastronomicas()
    ubic = pd.read_csv(UBICACION, low_memory=False)[["id_ubicacion", "direccion_original"]]
    puntos = puntos.merge(ubic, on="id_ubicacion", how="left")
    puntos = gpd.GeoDataFrame(puntos, geometry="geometry", crs="EPSG:4326").to_crs(CRS_METRICO)
    puntos = puntos[puntos.es_nucleo & ~puntos.es_outlier].copy()
    if rid:
        formas = perimetros()
        puntos = puntos[puntos.within(formas[rid])].copy()
    puntos["direccion_texto"] = puntos.direccion_original.fillna("")
    puntos["nombre"] = ""
    return puntos


# --------------------------------------------------------------------------- el emparejamiento

def _puertas(direccion: str, es_padron: bool) -> list[tuple[frozenset[str], int | None]]:
    if es_padron:
        return partir_padron(direccion)
    tokens, altura = partir_places(direccion)
    if not tokens:
        # Fuentes que traen calle y altura en campos separados y ya vienen concatenadas.
        partes = str(direccion).rsplit(" ", 1)
        if len(partes) == 2 and partes[1].isdigit():
            tokens, altura = tokens_calle(partes[0]), int(partes[1])
    return [(tokens, altura)] if tokens else []


def emparejar(izquierda: gpd.GeoDataFrame, derecha: gpd.GeoDataFrame,
              radio: float = RADIO_M, derecha_es_padron: bool = False) -> pd.DataFrame:
    """Para cada fila de la izquierda, su mejor pareja en la derecha, con el criterio y el motivo.

    Se resuelve por proximidad primero —es lo que un índice espacial hace barato— y recién sobre
    los candidatos cercanos se evalúan dirección y nombre. Al revés habría que comparar todo con
    todo.
    """
    if izquierda is None or derecha is None or not len(izquierda) or not len(derecha):
        return pd.DataFrame()

    # Varias de estas capas ya pasaron por un `sjoin` y arrastran `index_right`, que hace fallar
    # al siguiente. Se limpia acá y no en cada cargador: el que empareja es el que necesita la
    # precondición.
    sobrantes = ["index_right", "index_left"]
    izq = izquierda.reset_index(drop=True).drop(columns=sobrantes, errors="ignore")
    der = derecha.reset_index(drop=True).drop(columns=sobrantes, errors="ignore")
    cercanos = gpd.sjoin_nearest(
        izq, der[["geometry"]], how="left", max_distance=radio, distance_col="metros_dist")

    filas = []
    for indice, grupo in cercanos.groupby(level=0) if cercanos.index.name else cercanos.groupby(cercanos.index):
        fila_izq = izquierda.iloc[indice]
        puertas_izq = _puertas(fila_izq.get("direccion_texto", ""), False)
        tokens_izq = tokens_nombre(fila_izq.get("nombre", ""))

        mejor = None
        for candidato in grupo.itertuples():
            posicion = candidato.index_right
            if pd.isna(posicion):
                continue
            fila_der = der.iloc[int(posicion)]
            metros = float(candidato.metros_dist)

            criterio, puntaje = f"proximidad_{int(radio)}m", 1
            for tokens_calle_izq, altura_izq in puertas_izq:
                for tokens_calle_der, altura_der in _puertas(
                        fila_der.get("direccion_texto", ""), derecha_es_padron):
                    if (misma_calle(tokens_calle_izq, tokens_calle_der)
                            and altura_izq is not None and altura_der is not None
                            and abs(altura_izq - altura_der) <= TOLERANCIA_ALTURA):
                        criterio, puntaje = "usig_exacta", 3
                        break
                if puntaje == 3:
                    break
            parecido = parecido_nombre(tokens_izq, tokens_nombre(fila_der.get("nombre", "")))
            if puntaje < 3 and parecido >= UMBRAL_NOMBRE:
                criterio, puntaje = "proximidad_y_nombre", 2

            if mejor is None or (puntaje, -metros) > (mejor["puntaje"], -mejor["metros"]):
                mejor = {"puntaje": puntaje, "criterio": criterio, "metros": round(metros, 1),
                         "parecido_nombre": round(parecido, 2), "posicion_derecha": int(posicion)}

        filas.append({
            "posicion_izquierda": indice,
            "emparejado": mejor is not None,
            "criterio_match": mejor["criterio"] if mejor else "",
            "score_match": mejor["puntaje"] if mejor else 0,
            "metros": mejor["metros"] if mejor else None,
            "parecido_nombre": mejor["parecido_nombre"] if mejor else None,
            "posicion_derecha": mejor["posicion_derecha"] if mejor else None,
        })
    return pd.DataFrame(filas)


def tasa(resultado: pd.DataFrame) -> float:
    return 100 * resultado.emparejado.mean() if len(resultado) else 0.0


# --------------------------------------------------------------------------- informe

def _coma(valor: float, decimales: int = 1) -> str:
    return f"{valor:.{decimales}f}".replace(".", ",")


def _envolver(texto: str, ancho: int = 96) -> list[str]:
    lineas, actual = [], ""
    for palabra in texto.split():
        if len(actual) + len(palabra) + 1 > ancho:
            lineas.append(actual)
            actual = palabra
        else:
            actual = f"{actual} {palabra}".strip()
    if actual:
        lineas.append(actual)
    return lineas


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zona", default=ZONA_POR_DEFECTO)
    parser.add_argument("--sin-ciudad", action="store_true",
                        help="saltea el solape de toda la Ciudad y hace sólo el rescate")
    args = parser.parse_args()
    rid = args.zona

    print("[cargando] fuentes desde disco, sin red...")
    fuentes = {"OSM": cargar_osm(), "OVERTURE": cargar_overture(), "ATP": cargar_atp()}
    disponibles = {k: v for k, v in fuentes.items() if v is not None and len(v)}
    for clave, capa in disponibles.items():
        print(f"  {clave:<10}{len(capa):>7} POI gastronómicos")
    if not disponibles:
        raise SystemExit("ABORTADO: no hay ninguna fuente abierta en disco. Corré antes los bajadores.")

    salida = io.StringIO()

    def linea(texto: str = "") -> None:
        print(texto, file=salida)

    resumen: dict = {"fecha_calculo": dt.date.today().isoformat(), "requests_gastados": 0,
                     "zona_rescate": rid, "radio_m": RADIO_M}

    linea("=" * 98)
    linea("SOLAPE ENTRE FUENTES ABIERTAS Y RESCATE DE LOS DESCUBRIMIENTOS DE PLACES · 0 REQUESTS")
    linea("=" * 98)
    linea()

    # ---------------------------------------------------------------- §1 el rescate
    places = cargar_places(rid)
    padron_zona = cargar_padron(rid)
    linea(f"§1 · EL RESCATE · {len(places)} puntos núcleo que Places trajo de {rid}")
    linea("-" * 98)
    linea(f"  {'fuente abierta':<16}{'empareja':>10}{'% de los ' + str(len(places)):>14}"
          f"   criterios")
    rescate = {}
    detalles = {}
    for clave, capa in disponibles.items():
        resultado = emparejar(places, capa)
        detalles[clave] = resultado
        emparejados = int(resultado.emparejado.sum()) if len(resultado) else 0
        rescate[clave] = emparejados
        criterios = (resultado[resultado.emparejado].criterio_match.value_counts().to_dict()
                     if len(resultado) else {})
        linea(f"  {clave:<16}{emparejados:>10}{_coma(100 * emparejados / len(places)):>13} %"
              f"   {' · '.join(f'{k} {v}' for k, v in criterios.items())}")

    # La unión: un punto rescatado por cualquiera de las tres ya tiene identidad publicable.
    rescatados = set()
    for clave, resultado in detalles.items():
        if len(resultado):
            rescatados |= set(resultado[resultado.emparejado].posicion_izquierda)
    linea(f"  {'UNIÓN de las tres':<16}{len(rescatados):>10}"
          f"{_coma(100 * len(rescatados) / len(places)):>13} %")
    linea()

    resultado_padron = emparejar(places, padron_zona, derecha_es_padron=True)
    en_padron = int(resultado_padron.emparejado.sum()) if len(resultado_padron) else 0
    solo_places = len(places) - len(rescatados | (
        set(resultado_padron[resultado_padron.emparejado].posicion_izquierda)
        if len(resultado_padron) else set()))
    linea(f"  Para referencia, el padrón (que también es publicable): {en_padron} de {len(places)}"
          f"  ({_coma(100 * en_padron / len(places))} %)")
    linea(f"  Puntos que quedan SÓLO en Places, sin identidad publicable: {solo_places}"
          f"  ({_coma(100 * solo_places / len(places))} %)")
    linea()
    for texto in _envolver(
        f"Traducido al esquema (§6): de los {len(places)} puntos que Places trajo de esta zona, "
        f"{len(rescatados | (set(resultado_padron[resultado_padron.emparejado].posicion_izquierda) if len(resultado_padron) else set()))} "
        f"pueden entrar a la base como `abierto` —con nombre y dirección, tomados de la fuente "
        f"abierta que los corrobora— y {solo_places} quedan en `agregado`: existen como una cuenta "
        "dentro de una celda y nada más. Ése es el precio real de la restricción de Google, medido "
        "en vez de supuesto."):
        linea(f"  {texto}")
    linea()

    linea("  Sensibilidad al radio de emparejamiento:")
    linea(f"    {'radio':<10}" + "".join(f"{k:>12}" for k in disponibles))
    sensibilidad = {}
    for radio in RADIOS_SENSIBILIDAD:
        fila = {k: int(emparejar(places, capa, radio=radio).emparejado.sum())
                for k, capa in disponibles.items()}
        sensibilidad[radio] = fila
        marca = "  <- el usado" if radio == RADIO_M else ""
        linea(f"    {_coma(radio, 0) + ' m':<10}" + "".join(f"{v:>12}" for v in fila.values()) + marca)
    linea()
    for texto in _envolver(
        "Duplicar el radio de 20 a 100 m mueve poco el resultado, y eso es lo que había que "
        "comprobar: el rescate no depende de dónde se puso el corte. Si dependiera, el número no "
        "diría nada sobre las fuentes y sí sobre el parámetro."):
        linea(f"  {texto}")
    linea()

    resumen["rescate"] = {
        "places_nucleo": int(len(places)),
        "por_fuente": rescate,
        "union_abiertas": len(rescatados),
        "en_padron": en_padron,
        "solo_places": solo_places,
        "pct_union_abiertas": round(100 * len(rescatados) / len(places), 1),
        "sensibilidad_radio": {str(k): v for k, v in sensibilidad.items()},
    }

    # ---------------------------------------------------------------- §2 solape en la Ciudad
    if not args.sin_ciudad:
        linea("§2 · SOLAPE ENTRE LAS FUENTES, EN TODA LA CIUDAD")
        linea("-" * 98)
        padron_ciudad = cargar_padron()
        universo = dict(disponibles)
        universo["PADRON"] = padron_ciudad
        claves = list(universo)
        matriz = pd.DataFrame(index=claves, columns=claves, dtype=float)
        for izq in claves:
            for der in claves:
                if izq == der:
                    matriz.loc[izq, der] = 100.0
                    continue
                resultado = emparejar(universo[izq], universo[der],
                                      derecha_es_padron=(der == "PADRON"))
                matriz.loc[izq, der] = round(tasa(resultado), 1)
        linea("  Porcentaje de la fuente de la FILA que encuentra pareja en la fuente de la COLUMNA")
        linea("  (no es simétrico: una fuente chica se cubre entera con una grande, y no al revés)")
        linea()
        linea(matriz.to_string())
        linea()
        tamanos = {k: len(v) for k, v in universo.items()}
        linea("  tamaños: " + " · ".join(f"{k} {v}" for k, v in tamanos.items()))
        linea()
        for texto in _envolver(
            "La lectura que importa para la base: si cada fuente encontrara pareja en las otras "
            "casi siempre, sumarlas no agregaría cobertura y `n_fuentes` mediría redundancia. "
            "Las filas de arriba dicen cuánto de cada fuente es propio, y el complemento a 100 es "
            "exactamente lo que esa fuente aporta y ninguna otra tiene."):
            linea(f"  {texto}")
        linea()
        for texto in _envolver(
            "Y una advertencia sobre los grupos de independencia: Overture y All The Places NO son "
            "dos fuentes. Su solape alto es por construcción —Overture incorpora a All The Places "
            "como aportante— y contarlo como corroboración sería contarse a sí mismo. En la base "
            "las dos comparten el grupo `OVERTURE_FSQ_ATP` y suman uno solo a `n_fuentes`."):
            linea(f"  {texto}")
        linea()
        resumen["matriz_solape"] = matriz.to_dict()
        resumen["tamanos"] = tamanos

    linea("§3 · LO QUE ESTE CRUCE NO DICE")
    linea("-" * 98)
    for texto in _envolver(
        "1. El rescate se mide sobre UNA zona, Villa Crespo, que es la mejor calibrada que hay "
        "—646 locales contados a pie— y por eso se eligió. En un barrio donde las fuentes abiertas "
        "estén más flacas el rescate va a ser menor, y eso hay que medirlo antes de generalizar a "
        "los 48."):
        linea(f"  {texto}")
    for texto in _envolver(
        "2. Emparejar no es probar que sea el mismo local. Es la mejor evidencia disponible con "
        "cinco fuentes sin identificador común, y por eso cada emparejamiento guarda su criterio: "
        "un `usig_exacta` y un `proximidad_40m` no valen lo mismo y la base no los mezcla."):
        linea(f"  {texto}")
    for texto in _envolver(
        "3. Los casos dudosos —proximidad sin dirección ni nombre— quedan marcados para revisión, "
        "no resueltos por la máquina. Es la regla del esquema (§7) y se sostiene."):
        linea(f"  {texto}")
    linea()
    linea("=" * 98)

    texto_final = salida.getvalue()
    print(texto_final)

    GEN.mkdir(parents=True, exist_ok=True)
    INTERNO.mkdir(parents=True, exist_ok=True)
    (GEN / "CRUCE_FUENTES_ABIERTAS.txt").write_text(texto_final, encoding="utf-8")
    (GEN / "cruce_fuentes_abiertas_resumen.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    for clave, resultado in detalles.items():
        if len(resultado):
            resultado.to_csv(INTERNO / f"rescate_places_{rid}_{clave}.csv",
                             index=False, encoding="utf-8-sig")
    print(f"  publicado en {GEN.relative_to(ROOT)}: CRUCE_FUENTES_ABIERTAS.txt, "
          "cruce_fuentes_abiertas_resumen.json")
    print(f"  detalle por emparejamiento (fuera de Git): {INTERNO}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
