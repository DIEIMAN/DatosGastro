"""Capa homogénea de toda la Ciudad: 48 barrios y recorte por las 22 envolventes del Atlas.

Porta al repositorio el cálculo de `outputs/BARRIDO_CIUDAD_2026-08/`, que hasta ahora se hacía
fuera del código. Aplica las cinco reglas de conteo fijadas en
`METODO_COMPARABILIDAD_2026-08.md`:

1. La unidad es la **dirección normalizada** (`id_ubicacion`), no la habilitación.
2. Dos anillos de rubro y se informan los dos (núcleo y ampliado).
3. Las direcciones con más de 20 habilitaciones se **marcan aparte** (`dir_outlier`) y quedan
   fuera del conteo de direcciones; sus habilitaciones sí siguen sumando en `habilitaciones`.
4. Asignación territorial **por geometría** (punto en polígono). El campo `barrio` de
   `fact_habilitacion_gastronomica.csv` viene entero en «No determinado» y no se usa.
5. Ventana 2015-2025 sin bajas: el número es «direcciones que alguna vez tuvieron habilitación
   gastronómica en la década», nunca «locales abiertos hoy».

Solo lectura sobre `data/processed/`, `data/raw/` y `outputs/polos_gastro/ATLAS_V2/capas/`.
Escribe únicamente en `outputs/BARRIDO_CIUDAD_2026-08/generado/`; no toca los CSV de referencia
ni el pipeline público F01-F05.

Uso:
  python scripts/barrido_ciudad/build_capa_homogenea.py            # genera las tres tablas
  python scripts/barrido_ciudad/build_capa_homogenea.py --check    # genera y compara con la referencia
"""
from __future__ import annotations

import argparse
import sys
import unicodedata
from pathlib import Path

import geopandas as gpd
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
BARRIDO = ROOT / "outputs" / "BARRIDO_CIUDAD_2026-08"
OUT_DIR = BARRIDO / "generado"

# --- Insumos (solo lectura) -------------------------------------------------------------
UBICACION = ROOT / "data" / "processed" / "dim_ubicacion.csv"
HABILITACIONES = ROOT / "data" / "processed" / "fact_habilitacion_gastronomica.csv"
F01_RAW = ROOT / "data" / "raw" / "f01_oferta_establecimientos_gastronomicos.csv"
BARRIOS = ROOT / "data" / "raw" / "geo_barrios.geojson"
ENVOLVENTES = ROOT / "outputs" / "polos_gastro" / "ATLAS_V2" / "capas" / "envolventes_editoriales_v2.geojson"
CIFRAS_ATLAS = BARRIDO / "insumos" / "cifras_publicadas_atlas_22.csv"

# --- Regla 2: los dos anillos de rubro --------------------------------------------------
ANILLO_NUCLEO = ["Restaurante", "Bar", "Cafe", "Pizzeria", "Parrilla", "Comida al paso", "Heladeria"]
ANILLO_AMPLIADO = ANILLO_NUCLEO + ["Panaderia", "Pasteleria", "Catering"]

# --- Regla 3: umbral de dirección anómala -----------------------------------------------
UMBRAL_OUTLIER = 20

# Precedencia cuando dos envolventes editoriales se superponen: el perímetro de menor
# referencia_id retiene la superficie compartida, para que ninguna dirección se cuente dos
# veces en el mismo cuadro. Hoy solo hay dos pares superpuestos: R02 sobre R12 (el eje
# Corrientes atraviesa el microcentro segmentado) y R12 sobre R18 (Esmeralda-Paraguay está
# contenido en el microcentro en un 64 % de su superficie).
PRECEDENCIA_ENVOLVENTES = "referencia_id"


def plegar(texto: object) -> str:
    """Nombre de barrio sin tildes ni mayúsculas, para cruzar fuentes con grafías distintas."""
    return unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode()


def cargar_direcciones_gastronomicas() -> tuple[gpd.GeoDataFrame, pd.DataFrame]:
    """Direcciones georreferenciadas con su recuento de habilitaciones y sus dos anillos.

    Devuelve (direcciones como puntos, habilitaciones georreferenciadas).
    """
    ubic = pd.read_csv(UBICACION, low_memory=False)
    ubic["lat"] = pd.to_numeric(ubic.latitud, errors="coerce")
    ubic["lon"] = pd.to_numeric(ubic.longitud, errors="coerce")
    con_coord = ubic[ubic.lat.notna() & ubic.lon.notna()][["id_ubicacion", "lat", "lon"]]

    hab = pd.read_csv(HABILITACIONES, low_memory=False)
    hab = hab[hab.es_gastronomico == "si"]
    # Regla 4: solo entran las direcciones con coordenada; la asignación es geométrica.
    hab = hab.merge(con_coord, on="id_ubicacion", how="inner")

    por_direccion = hab.groupby("id_ubicacion").size()
    nucleo = set(hab[hab.categoria_gastronomica_inferida.isin(ANILLO_NUCLEO)].id_ubicacion)
    ampliado = set(hab[hab.categoria_gastronomica_inferida.isin(ANILLO_AMPLIADO)].id_ubicacion)

    dirs = con_coord[con_coord.id_ubicacion.isin(hab.id_ubicacion)].drop_duplicates("id_ubicacion").copy()
    dirs["habilitaciones"] = dirs.id_ubicacion.map(por_direccion)
    dirs["es_outlier"] = dirs.habilitaciones > UMBRAL_OUTLIER  # Regla 3
    dirs["es_nucleo"] = dirs.id_ubicacion.isin(nucleo)
    dirs["es_ampliado"] = dirs.id_ubicacion.isin(ampliado)

    puntos = gpd.GeoDataFrame(
        dirs, geometry=gpd.points_from_xy(dirs.lon, dirs.lat), crs="EPSG:4326"
    )
    return puntos, hab


def cargar_f01(barrios: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Oferta gastronómica F01 con barrio declarado por la fuente y validado contra el polígono.

    F01 trae su propio campo `barrio`; se conserva cuando el punto cae efectivamente dentro de
    ese polígono y se reemplaza por el barrio geométrico cuando no (frontera mal declarada).
    Los puntos que no caen en ningún barrio —hay uno, sobre los diques— quedan sin asignar.
    El archivo viene en latin-1, separado por punto y coma y con decimales por coma.
    """
    f01 = pd.read_csv(F01_RAW, sep=";", encoding="latin-1", low_memory=False)
    f01["lat"] = pd.to_numeric(f01["lat"].str.replace(",", "."), errors="coerce")
    f01["lon"] = pd.to_numeric(f01["long"].str.replace(",", "."), errors="coerce")

    # El campo `barrio` de F01 mezcla grafías ("Boca" por "La Boca") y trae "Nuñez" con doble
    # codificación; se resuelve por plegado y, si no matchea, cae en el barrio geométrico.
    oficial = {plegar(n): n for n in barrios.nombre}
    alias = {"Boca": "La Boca"}
    declarado = f01.barrio.map(plegar).map(lambda x: alias.get(x, x))
    f01["barrio_declarado"] = declarado.map(oficial.get)

    puntos = gpd.GeoDataFrame(f01, geometry=gpd.points_from_xy(f01.lon, f01.lat), crs="EPSG:4326")
    # F01 ya trae una columna `nombre` (el nombre del local); el barrio geométrico va aparte.
    poligonos = barrios[["nombre", "geometry"]].rename(columns={"nombre": "barrio_geometrico"})
    puntos = gpd.sjoin(puntos, poligonos, how="left", predicate="within")
    puntos["barrio"] = [
        fila.barrio_declarado if fila.barrio_declarado == fila.barrio_geometrico else fila.barrio_geometrico
        for fila in puntos.itertuples()
    ]
    return puntos


def indicadores(direcciones: pd.DataFrame, f01: int) -> dict[str, int]:
    """Los cinco indicadores de la capa homogénea para un recorte territorial."""
    contables = direcciones[~direcciones.es_outlier]  # Regla 3
    return {
        "dir_nucleo": int(contables.es_nucleo.sum()),
        "dir_ampliado": int(contables.es_ampliado.sum()),
        "habilitaciones": int(direcciones.habilitaciones.sum()),
        "f01_locales": f01,
        "dir_outlier": int(direcciones.es_outlier.sum()),
    }


def capa_48_barrios(puntos: gpd.GeoDataFrame, f01: gpd.GeoDataFrame, barrios: gpd.GeoDataFrame) -> pd.DataFrame:
    """Los 48 barrios con los cuatro indicadores y las direcciones anómalas."""
    asignadas = gpd.sjoin(puntos, barrios[["nombre", "geometry"]], how="left", predicate="within")
    f01_por_barrio = f01.barrio.value_counts()

    filas = {}
    for barrio in barrios.nombre:
        recorte = asignadas[asignadas.nombre == barrio]
        filas[barrio] = indicadores(recorte, int(f01_por_barrio.get(barrio, 0)))

    tabla = pd.DataFrame(filas).T
    # Orden de presentación: por base núcleo y, a igualdad, por oferta F01.
    return tabla.sort_values(["dir_nucleo", "f01_locales"], ascending=False)


def capa_22_zonas(puntos: gpd.GeoDataFrame, f01: gpd.GeoDataFrame, envolventes: gpd.GeoDataFrame) -> pd.DataFrame:
    """La misma capa recortada por las envolventes editoriales del Atlas, sin doble conteo."""
    envolventes = envolventes.sort_values(PRECEDENCIA_ENVOLVENTES).reset_index(drop=True)

    filas = {}
    for posicion, zona in envolventes.iterrows():
        perimetro = zona.geometry
        # Se descuenta la superficie ya retenida por las envolventes de mayor precedencia.
        for previa in envolventes.iloc[:posicion].itertuples():
            if perimetro.intersects(previa.geometry):
                perimetro = perimetro.difference(previa.geometry)
        etiqueta = f"{zona.referencia_id} · {zona.nombre}"
        filas[etiqueta] = indicadores(
            puntos[puntos.within(perimetro)], int(f01.within(perimetro).sum())
        )

    tabla = pd.DataFrame(filas).T
    return tabla.sort_index()


def factor_captura(zonas: pd.DataFrame) -> pd.DataFrame:
    """Compara la base homogénea de cada zona contra la cifra publicada del Atlas.

    Las cifras publicadas y el método de cada zona no se derivan de los datos: se declaran en
    `insumos/cifras_publicadas_atlas_22.csv`. Ninguna cifra del Atlas se recalcula acá.
    """
    cifras = pd.read_csv(CIFRAS_ATLAS)
    base = zonas.copy()
    base["rid"] = [etiqueta.split(" · ")[0] for etiqueta in base.index]
    tabla = cifras.merge(base, on="rid", how="left")

    tabla["captura_%"] = (100 * tabla.dir_nucleo / tabla.relevado).round(1)
    tabla = tabla.rename(columns={"zona_publicada": "zona", "habilitaciones": "habilit", "f01_locales": "f01"})
    return tabla[["rid", "zona", "metodo", "naturaleza", "relevado",
                  "dir_nucleo", "dir_ampliado", "habilit", "f01", "captura_%"]]


def comparar(generado: pd.DataFrame, referencia: Path, columnas: list[str], indice_rid: bool = False) -> bool:
    """Control de aceptación: igualdad exacta celda por celda contra la tabla de referencia.

    PENDIENTES AGRUPADOS AL PRÓXIMO RECONGELAMIENTO. Reescribir la referencia destruye este
    control, así que ningún cambio cosmético lo justifica por sí solo. Cuando haya que recongelar
    por un motivo de fondo, estos dos entran en esa misma corrida y no antes:

      1. renombrar la columna `habilitaciones` a `tramites` en los CSV. Hoy el lector ya está
         protegido por `DICCIONARIO_COLUMNAS.md`, el aviso del encabezado y la daga por barrio:
         el nombre agrega claridad, no protección;
      2. el mapeo `confiteria -> Pasteleria`, si Diego lo resuelve — está descripto en el
         encabezado de `perfilar_usos_suelo.py` y se cambia en las dos bases a la vez.

    Los dos se hacen en el generador y en la referencia al mismo tiempo, y se vuelve a congelar.
    """
    if not referencia.exists():
        print(f"  [!] falta la referencia {referencia.name}")
        return False
    ref = pd.read_csv(referencia, index_col=0, encoding="utf-8")

    gen = generado.copy()
    if indice_rid:
        gen = gen.set_index("rid")
        ref.index = [str(i).split(" · ")[0] for i in ref.index]
    else:
        ref.index = [plegar(i) for i in ref.index]
        gen.index = [plegar(i) for i in gen.index]

    faltan = sorted(set(ref.index) - set(gen.index))
    sobran = sorted(set(gen.index) - set(ref.index))
    if faltan or sobran:
        print(f"  [X] {referencia.name}: filas que faltan {faltan} / que sobran {sobran}")
        return False

    ok = True
    gen = gen.reindex(ref.index)
    for columna in columnas:
        if columna not in ref.columns:
            continue
        izq = pd.to_numeric(gen[columna], errors="coerce")
        der = pd.to_numeric(ref[columna], errors="coerce")
        distintas = (izq != der) & ~(izq.isna() & der.isna())
        if distintas.any():
            ok = False
            detalle = {i: (izq[i], der[i]) for i in ref.index[distintas]}
            print(f"  [X] {referencia.name} · {columna}: {int(distintas.sum())} celdas distintas {detalle}")
    if ok:
        orden = "" if indice_rid else f", orden de filas {'igual' if list(gen.index) == list(ref.index) else 'DISTINTO'}"
        print(f"  [OK] {referencia.name}: {len(ref)} filas x {len(columnas)} columnas idénticas{orden}")
    return ok


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="comparar con los CSV de referencia")
    args = parser.parse_args()

    barrios = gpd.read_file(BARRIOS)[["nombre", "geometry"]]
    envolventes = gpd.read_file(ENVOLVENTES)[["referencia_id", "nombre", "geometry"]]
    puntos, hab = cargar_direcciones_gastronomicas()
    f01 = cargar_f01(barrios)

    print(f"habilitaciones gastronómicas georreferenciadas: {len(hab):,}".replace(",", "."))
    print(f"direcciones distintas: {puntos.id_ubicacion.nunique():,}".replace(",", "."))
    print(f"habilitaciones por dirección: {len(hab) / len(puntos):.1f}")
    outliers = puntos[puntos.es_outlier]
    print(
        f"direcciones anómalas (>{UMBRAL_OUTLIER} habilitaciones): {len(outliers)} "
        f"= {100 * outliers.habilitaciones.sum() / len(hab):.1f} % de los registros"
    )
    print(f"direcciones núcleo en CABA: {int(puntos.es_nucleo.sum()):,}".replace(",", "."))
    print(f"direcciones ampliado en CABA: {int(puntos.es_ampliado.sum()):,}".replace(",", "."))

    # Conciliación de los dos totales de direcciones núcleo que circulan. No es una discrepancia:
    # el titular de CABA incluye las direcciones anómalas y la suma por barrio las excluye, que es
    # lo que manda la regla 3. Contra parcelas del Relevamiento se compara la suma sin anómalas,
    # porque una dirección anómala no es un local.
    nucleo_total = int(puntos.es_nucleo.sum())
    nucleo_anomalo = int((puntos.es_outlier & puntos.es_nucleo).sum())
    print(
        f"  conciliación: {nucleo_total:,} en CABA = {nucleo_total - nucleo_anomalo:,} sumadas por "
        f"barrio + {nucleo_anomalo} anómalas que son núcleo".replace(",", ".")
    )

    tabla_barrios = capa_48_barrios(puntos, f01, barrios)
    tabla_zonas = capa_22_zonas(puntos, f01, envolventes)
    tabla_captura = factor_captura(tabla_zonas)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tabla_barrios.to_csv(OUT_DIR / "capa_homogenea_48_barrios.csv", encoding="utf-8")
    tabla_zonas.to_csv(OUT_DIR / "capa_homogenea_22_zonas.csv", encoding="utf-8")
    tabla_captura.to_csv(OUT_DIR / "factor_captura_22_zonas.csv", index=False, encoding="utf-8")
    print(f"\nescrito en {OUT_DIR.relative_to(ROOT)}")

    if not args.check:
        return 0

    print("\ncontrol de aceptación contra la referencia de agosto 2026:")
    indicadores_ = ["dir_nucleo", "dir_ampliado", "habilitaciones", "f01_locales", "dir_outlier"]
    ok = comparar(tabla_barrios, BARRIDO / "capa_homogenea_48_barrios.csv", indicadores_)
    ok &= comparar(tabla_zonas, BARRIDO / "capa_homogenea_22_zonas.csv", indicadores_)
    ok &= comparar(
        tabla_captura,
        BARRIDO / "factor_captura_22_zonas.csv",
        ["relevado", "dir_nucleo", "dir_ampliado", "habilit", "f01", "captura_%"],
        indice_rid=True,
    )
    print("\nRESULTADO:", "reproduce la capa exacta" if ok else "HAY DIFERENCIAS, revisar")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
