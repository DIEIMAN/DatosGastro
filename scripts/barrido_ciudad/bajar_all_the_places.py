"""All The Places (E07): recorte de la Ciudad desde la corrida semanal y capa por barrio.

QUÉ ES
------
All The Places corre unos cinco mil *spiders* contra los localizadores de sucursales de las
cadenas y publica el resultado semanal bajo **CC0 1.0**, o sea sin ninguna restricción de
redistribución. Es la fuente más permisiva de todas las que entran a la base.

Su límite es estructural y conviene decirlo antes de mirar el número: **cubre cadenas, no
comercios independientes.** Un spider existe porque una marca publica un localizador de
sucursales; el bodegón de la esquina no tiene uno. Para el objetivo del proyecto —dibujar polos
gastronómicos— eso la vuelve una fuente de corroboración puntual, no de cobertura.

**Y hay un dato medido que la achica todavía más:** de los POI de Overture en la Ciudad, 572
declaran a All The Places como aportante. Buena parte de lo que esta fuente tiene ya viaja adentro
de Overture, y por eso el esquema (§3) las pone en el mismo grupo de independencia. Lo que este
script mide es cuánto agrega *además* de eso.

CÓMO SE RECORTA SIN DESCOMPRIMIR TREINTA GIGABYTES A DISCO
-----------------------------------------------------------
La corrida completa son 2,95 GB comprimidos y **30,6 GB descomprimidos** en 4.898 archivos, con
cinco de ellos —padrones de direcciones de Australia y Nueva Zelanda— que pesan más de 1,5 GB cada
uno. Descomprimir a disco para después filtrar sería absurdo.

El archivo tiene una propiedad que lo resuelve: **cada `Feature` ocupa exactamente una línea.** Se
recorre el ZIP miembro por miembro, línea por línea, y se aplica un filtro de bytes antes de
parsear: una línea que no contenga `-58.` **no puede** ser un punto de la Ciudad, porque toda
longitud de la Ciudad empieza así. Recién las que pasan ese filtro se parsean como JSON. El costo
de descartar una línea baja de «parsear JSON» a «buscar cinco bytes».

El filtro es conservador a propósito: pide `-58.` y no `-58.4`, así que no puede perder un punto
por redondeo. Lo que descarta, lo descarta con certeza.

EL MAPEO DE CATEGORÍAS SE IMPORTA, NO SE COPIA
-----------------------------------------------
All The Places publica sus atributos **con el vocabulario de tags de OSM** (`amenity`, `shop`,
`cuisine`, `addr:*`). Así que el mapeo a los dos anillos es el mismo que ya está declarado en
`bajar_osm_gastro.py` y se importa de ahí. Copiarlo sería garantizar que las dos fuentes se
separen en la primera corrección que alguien haga en una sola de las dos.

USO
---
  python scripts/barrido_ciudad/bajar_all_the_places.py            # recorta desde el ZIP ya bajado
  python scripts/barrido_ciudad/bajar_all_the_places.py --reinformar   # rehace desde el recorte

La descarga del ZIP no la hace este script: son 2,95 GB y la URL sale de
`https://data.alltheplaces.xyz/runs/latest/info_embed.html`, que apunta al identificador de la
corrida vigente. Está anotada en `URL_CORRIDA` y se baja con `curl -C -` para poder reanudar.
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
import zipfile
from pathlib import Path

import geopandas as gpd
import pandas as pd

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from bajar_osm_gastro import (  # noqa: E402
    AMPLIADO_TAGS,
    CUISINE_NUCLEO,
    DESCARTADOS_TAGS,
    NUCLEO_TAGS,
)

BARRIDO = ROOT / "outputs" / "BARRIDO_CIUDAD_2026-08"
GEN = BARRIDO / "generado"
ATP_DIR = ROOT / "outputs" / "fuentes_externas" / "all_the_places"
RECORTE = ATP_DIR / "atp_caba.csv"

BARRIOS = ROOT / "data" / "raw" / "geo_barrios.geojson"
CAPA_PADRON = BARRIDO / "capa_homogenea_48_barrios.csv"
CAPA_OSM = GEN / "osm_gastro_48_barrios.csv"
CAPA_OVT = GEN / "overture_gastro_48_barrios.csv"

CORRIDA = "2026-08-01-13-32-15"
URL_CORRIDA = f"https://alltheplaces-data.openaddresses.io/runs/{CORRIDA}/output.zip"
LICENCIA = "CC0 1.0 · dominio público"
GRUPO_INDEPENDENCIA = "OVERTURE_FSQ_ATP"

# El filtro de bytes. Toda longitud de la Ciudad empieza con estos cinco caracteres; una línea que
# no los tenga no puede contener un punto de acá. Se pide también la latitud para bajar todavía más
# los falsos candidatos, y las dos condiciones son necesarias, nunca suficientes: el bbox real se
# aplica después sobre la coordenada parseada.
PREFILTRO_LON = b"-58."
PREFILTRO_LAT = b"-34."

# Campos que se conservan del `properties` de cada feature. Mismo criterio que en OSM: los tags de
# contacto (`phone`, `website`, `email`) no entran, aunque la licencia los permita.
CAMPOS = ["@spider", "ref", "name", "brand", "amenity", "shop", "craft", "cuisine",
          "addr:street", "addr:housenumber", "addr:full", "addr:city"]


def plegar(texto: object) -> str:
    return unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode().upper().strip()


def bbox_ciudad() -> tuple[float, float, float, float]:
    barrios = gpd.read_file(BARRIOS)
    minx, miny, maxx, maxy = barrios.total_bounds
    return float(minx), float(miny), float(maxx), float(maxy)


def zip_de_la_corrida() -> Path:
    candidatos = sorted(ATP_DIR.glob("output_*.zip"))
    if not candidatos:
        raise SystemExit(
            f"ABORTADO: falta el ZIP de la corrida en {ATP_DIR.relative_to(ROOT)}.\n"
            f"  curl -L -C - -o {ATP_DIR.relative_to(ROOT)}/output_{CORRIDA}.zip \\\n"
            f"    {URL_CORRIDA}")
    return candidatos[-1]


# --------------------------------------------------------------------------- el recorte

def recortar(archivo: Path, caja: tuple[float, float, float, float]) -> pd.DataFrame:
    """Una pasada por el ZIP entero, quedándose sólo con lo que cae en el rectángulo."""
    minx, miny, maxx, maxy = caja
    filas: list[dict] = []
    miembros_con_candidatos, lineas_candidatas, lineas_totales = 0, 0, 0

    with zipfile.ZipFile(archivo) as zf:
        miembros = [i for i in zf.infolist() if i.filename.endswith(".geojson")]
        for numero, info in enumerate(miembros, start=1):
            if numero % 500 == 0:
                print(f"    {numero}/{len(miembros)} spiders · {len(filas)} puntos en la Ciudad")
            aporta = False
            with zf.open(info) as fuente:
                for linea in io.BufferedReader(fuente, buffer_size=1 << 20):
                    lineas_totales += 1
                    if PREFILTRO_LON not in linea or PREFILTRO_LAT not in linea:
                        continue
                    lineas_candidatas += 1
                    try:
                        feature = json.loads(linea.rstrip(b",\n").decode("utf-8"))
                    except (ValueError, UnicodeDecodeError):
                        continue
                    geometria = feature.get("geometry") or {}
                    if geometria.get("type") != "Point":
                        continue
                    lon, lat = geometria["coordinates"][:2]
                    if not (minx <= lon <= maxx and miny <= lat <= maxy):
                        continue
                    propiedades = feature.get("properties", {})
                    fila = {campo: propiedades.get(campo, "") for campo in CAMPOS}
                    fila["atp_id"] = feature.get("id", "")
                    fila["lon"], fila["lat"] = float(lon), float(lat)
                    filas.append(fila)
                    aporta = True
            miembros_con_candidatos += int(aporta)

    tabla = pd.DataFrame(filas)
    tabla.attrs["spiders_totales"] = len(miembros)
    tabla.attrs["spiders_con_puntos"] = miembros_con_candidatos
    tabla.attrs["lineas_totales"] = lineas_totales
    tabla.attrs["lineas_candidatas"] = lineas_candidatas
    return tabla


def clasificar(tabla: pd.DataFrame) -> pd.DataFrame:
    """Anillo y rubro con el mapeo de OSM, que es el vocabulario que esta fuente usa."""
    tabla = tabla.copy()
    descartados = set(DESCARTADOS_TAGS)
    pares = list(zip(tabla.amenity.fillna(""), tabla.shop.fillna(""), tabla.craft.fillna("")))

    anillos, rubros = [], []
    for amenity, shop, craft in pares:
        presentes = {("amenity", amenity), ("shop", shop), ("craft", craft)}
        anillo, rubro = "fuera", ""
        for etiqueta, tags in NUCLEO_TAGS.items():
            if presentes & set(tags):
                anillo, rubro = "nucleo", etiqueta
                break
        else:
            for etiqueta, tags in AMPLIADO_TAGS.items():
                if presentes & set(tags):
                    anillo, rubro = "ampliado", etiqueta
                    break
            else:
                if presentes & descartados:
                    anillo = "descartado"
        anillos.append(anillo)
        rubros.append(rubro)

    tabla["anillo"] = anillos
    tabla["rubro"] = rubros
    cocinas = tabla.cuisine.fillna("").str.lower()
    for etiqueta, valores in CUISINE_NUCLEO.items():
        marca = (tabla.anillo == "nucleo") & cocinas.apply(
            lambda c, vs=valores: any(v in [p.strip() for p in c.split(";")] for v in vs))
        tabla.loc[marca, "rubro"] = etiqueta
    return tabla


def asignar_barrio(tabla: pd.DataFrame, barrios: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    puntos = gpd.GeoDataFrame(
        tabla.copy(), geometry=gpd.points_from_xy(tabla.lon, tabla.lat), crs="EPSG:4326")
    return gpd.sjoin(puntos, barrios[["nombre_barrio", "geometry"]], how="left", predicate="within")


def por_barrio(asignados: gpd.GeoDataFrame, barrios: gpd.GeoDataFrame) -> pd.DataFrame:
    gastro = asignados[asignados.anillo.isin(["nucleo", "ampliado"])]
    filas = {}
    for barrio in barrios.nombre_barrio:
        recorte = gastro[gastro.nombre_barrio == barrio]
        filas[plegar(barrio)] = {
            "atp_nucleo": int((recorte.anillo == "nucleo").sum()),
            "atp_ampliado": int(len(recorte)),
        }
    return pd.DataFrame(filas).T


def unir_con_las_otras(atp: pd.DataFrame) -> pd.DataFrame:
    tabla = atp
    padron = pd.read_csv(CAPA_PADRON, index_col=0, encoding="utf-8")
    padron.index = [plegar(i) for i in padron.index]
    tabla = tabla.join(padron[["dir_nucleo"]])
    for ruta, columnas in ((CAPA_OSM, ["osm_nucleo"]), (CAPA_OVT, ["ovt_nucleo"])):
        if ruta.exists():
            otra = pd.read_csv(ruta, index_col=0, encoding="utf-8")
            otra.index = [plegar(i) for i in otra.index]
            tabla = tabla.join(otra[columnas])
    return tabla.sort_values("atp_nucleo", ascending=False)


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


def informar(tabla: pd.DataFrame, asignados: gpd.GeoDataFrame,
             comparada: pd.DataFrame) -> tuple[str, dict]:
    salida = io.StringIO()

    def linea(texto: str = "") -> None:
        print(texto, file=salida)

    en_ciudad = asignados[asignados.nombre_barrio.notna()]
    gastro = en_ciudad[en_ciudad.anillo.isin(["nucleo", "ampliado"])]
    nucleo = gastro[gastro.anillo == "nucleo"]

    linea("=" * 98)
    linea(f"ALL THE PLACES (E07) · corrida {CORRIDA} · recorte de la Ciudad")
    linea("=" * 98)
    linea(f"licencia {LICENCIA} · costo: 0 · grupo de independencia {GRUPO_INDEPENDENCIA}")
    linea()

    linea("§1 · EL RECORTE")
    linea("-" * 98)
    linea(f"  spiders en la corrida                          : {tabla.attrs.get('spiders_totales', 0):>7}")
    linea(f"  spiders con al menos un punto en la Ciudad     : {tabla.attrs.get('spiders_con_puntos', 0):>7}")
    linea(f"  líneas recorridas (una por local en el mundo)  : {tabla.attrs.get('lineas_totales', 0):>7,}"
          .replace(",", "."))
    linea(f"  líneas que pasaron el filtro de bytes          : {tabla.attrs.get('lineas_candidatas', 0):>7,}"
          .replace(",", "."))
    linea(f"  puntos dentro del rectángulo de la Ciudad      : {len(tabla):>7}")
    linea(f"  puntos dentro de algún barrio                  : {len(en_ciudad):>7}")
    linea(f"  de ellos, gastronómicos (dos anillos)          : {len(gastro):>7}")
    linea(f"  de ellos, anillo núcleo                        : {len(nucleo):>7}")
    linea()

    linea("§2 · QUÉ TRAE, Y DE QUÉ MARCAS")
    linea("-" * 98)
    if len(gastro):
        por_spider = gastro["@spider"].value_counts()
        linea(f"  {len(por_spider)} spiders gastronómicos con presencia en la Ciudad. Los 20 mayores:")
        for spider, cuantos in por_spider.head(20).items():
            linea(f"    {spider:<44}{cuantos:>6}")
        linea()
        conteo = gastro.rubro.value_counts()
        linea("  por rubro: " + " · ".join(f"{k} {v}" for k, v in conteo.items()))
    else:
        linea("  Ningún punto gastronómico en la Ciudad. Ver §4.")
    linea()

    linea("§3 · COBERTURA POR BARRIO, CONTRA LAS OTRAS FUENTES")
    linea("-" * 98)
    columnas = [c for c in ["atp_nucleo", "osm_nucleo", "ovt_nucleo", "dir_nucleo"]
                if c in comparada]
    linea(comparada.head(15)[columnas].to_string())
    linea()
    barrios_con = int((comparada.atp_nucleo > 0).sum())
    linea(f"  barrios con al menos un punto núcleo de esta fuente: {barrios_con} de 48")
    linea()

    linea("§4 · QUÉ SE PUEDE Y QUÉ NO SE PUEDE HACER CON ESTO")
    linea("-" * 98)
    padron_nucleo = int(comparada.dir_nucleo.sum())
    for texto in _envolver(
        f"Los {len(nucleo)} puntos núcleo de esta fuente son el {_coma(100 * len(nucleo) / padron_nucleo, 2)} % "
        f"de las {f'{padron_nucleo:,}'.replace(',', '.')} direcciones núcleo del padrón. No es una "
        "fuente de cobertura y no se la va a usar como tal: cubre cadenas, porque un spider existe "
        "cuando una marca publica un localizador de sucursales, y el bodegón de la esquina no "
        "publica ninguno."):
        linea(f"  {texto}")
    linea()
    for texto in _envolver(
        "Para qué sirve, entonces. Primero, es CC0: cualquier local que aparezca acá tiene identidad "
        "publicable sin condición ninguna, ni siquiera la atribución de la ODbL. Segundo, son las "
        "cadenas, que son justamente los locales que las fuentes documentales registran peor —una "
        "cadena tramita una habilitación por sucursal y las sucursales nuevas tardan en aparecer—. "
        "Tercero, y es lo que la vuelve barata: ya está bajada y no cuesta un request."):
        linea(f"  {texto}")
    linea()
    for texto in _envolver(
        f"El solape con Overture hay que darlo por descontado y no contarlo dos veces: 572 POI de "
        "Overture en la Ciudad declaran a All The Places como aportante. Por eso las dos comparten "
        f"grupo de independencia (`{GRUPO_INDEPENDENCIA}`) y una corroboración entre ellas no cuenta "
        "como dos fuentes. Cuánto agrega de verdad sobre Overture se mide en el cruce, no acá."):
        linea(f"  {texto}")
    linea()
    linea("=" * 98)

    resumen = {
        "fecha_calculo": dt.date.today().isoformat(),
        "fuente": "E07 · All The Places",
        "corrida": CORRIDA,
        "licencia": LICENCIA,
        "grupo_independencia": GRUPO_INDEPENDENCIA,
        "costo": "0 requests de Places",
        "spiders_totales": tabla.attrs.get("spiders_totales", 0),
        "spiders_con_puntos_en_ciudad": tabla.attrs.get("spiders_con_puntos", 0),
        "puntos_en_bbox": int(len(tabla)),
        "puntos_en_ciudad": int(len(en_ciudad)),
        "atp_nucleo": int(len(nucleo)),
        "atp_ampliado": int(len(gastro)),
        "padron_nucleo_48": padron_nucleo,
        "atp_sobre_padron_ciudad": round(len(nucleo) / padron_nucleo, 4),
        "barrios_con_puntos": barrios_con,
        "spiders_gastronomicos": (gastro["@spider"].value_counts().to_dict()
                                  if len(gastro) else {}),
    }
    return salida.getvalue(), resumen


# --------------------------------------------------------------------------- orquestación

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reinformar", action="store_true",
                        help="rehace las tablas desde el recorte en disco, sin volver a abrir el ZIP")
    args = parser.parse_args()

    if args.reinformar:
        if not RECORTE.exists():
            raise SystemExit(f"ABORTADO: falta {RECORTE.relative_to(ROOT)}.")
        tabla = pd.read_csv(RECORTE, encoding="utf-8-sig", low_memory=False)
        metadatos = json.loads((ATP_DIR / "atp_recorte_meta.json").read_text(encoding="utf-8"))
        tabla.attrs.update(metadatos)
    else:
        archivo = zip_de_la_corrida()
        print(f"[recorte] {archivo.name} · {archivo.stat().st_size / 1e9:.2f} GB comprimidos")
        print("  una pasada por 4.898 spiders con filtro de bytes; tarda varios minutos...")
        tabla = recortar(archivo, bbox_ciudad())
        ATP_DIR.mkdir(parents=True, exist_ok=True)
        tabla.to_csv(RECORTE, index=False, encoding="utf-8-sig")
        (ATP_DIR / "atp_recorte_meta.json").write_text(
            json.dumps(dict(tabla.attrs), ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  recorte en {RECORTE.relative_to(ROOT)} · {len(tabla)} puntos")

    tabla = clasificar(tabla)
    barrios = gpd.read_file(BARRIOS)[["nombre", "geometry"]].rename(
        columns={"nombre": "nombre_barrio"})
    asignados = asignar_barrio(tabla, barrios)
    comparada = unir_con_las_otras(por_barrio(asignados, barrios))
    texto, resumen = informar(tabla, asignados, comparada)
    print(texto)

    GEN.mkdir(parents=True, exist_ok=True)
    comparada.to_csv(GEN / "atp_gastro_48_barrios.csv", encoding="utf-8")
    (GEN / "ATP_GASTRO_CIUDAD.txt").write_text(texto, encoding="utf-8")
    (GEN / "atp_gastro_resumen.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  publicado en {GEN.relative_to(ROOT)}: atp_gastro_48_barrios.csv, "
          "ATP_GASTRO_CIUDAD.txt, atp_gastro_resumen.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
