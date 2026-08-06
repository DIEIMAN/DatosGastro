"""Dataset abierto de Bares Notables: los 95 de Wikidata, geocodificados con USIG.

POR QUÉ ESTE DATASET
--------------------
Hoy el índice abierto más completo de los Bares Notables de la Ciudad está en **Wikidata y no en
el portal del Gobierno**. La consulta por declaratoria patrimonial (P1435) devuelve 95 ítems; la
consulta por tipo de establecimiento devuelve 17, porque 81 de los 95 están cargados en Wikidata
como «edificio» y no como bar. Preguntar por el tipo pierde el 82 % del listado: hay que preguntar
por la declaratoria.

El dato es de la Dirección o de Patrimonio, así que corresponde publicarlo.

LOS DOS RECAUDOS QUE VIAJAN CON EL DATO, NO EN UNA NOTA APARTE
--------------------------------------------------------------
1. **El listado NO es exhaustivo.** Son los Bares Notables que Wikidata tiene cargados con su
   declaratoria, no el registro oficial completo. Publicarlo como «los Bares Notables de la
   Ciudad» sería afirmar una completitud que no se verificó contra el registro.
2. **«Bar Notable» es una DECLARATORIA —un acto administrativo— y no una calificación de
   calidad.** Un bar declarado notable lo es porque un acto de gobierno lo declaró por su valor
   patrimonial, arquitectónico o cultural; no porque nadie haya evaluado lo que sirve. Los dos
   recaudos van en el CSV, en el GeoJSON y en el README del dataset.

LAS COORDENADAS SE GEOCODIFICAN, NO SE IMPORTAN
-----------------------------------------------
Las coordenadas de Wikidata NO se usan: según el propio wiki de OSM, buena parte llegó por la
cadena Wikipedia → Google Maps, y eso es procedencia viciada para un dato que la Dirección va a
publicar. Se geocodifica desde la dirección postal declarada con el **normalizador de USIG**, que
es el servicio oficial del GCBA, gratuito y sin credenciales.

USIG devuelve candidatos de varios partidos para la misma altura, así que **se filtra por
`cod_partido == "caba"`**; sin ese filtro entran direcciones homónimas de Almirante Brown y otros
partidos del conurbano, que es un error silencioso y difícil de ver después.

La respuesta cruda de cada consulta se cachea: una corrida nueva no vuelve a pegarle al servicio.

Google Places no interviene. 0 requests a Places.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/dataset_bares_notables.py
  .venv/Scripts/python.exe scripts/barrido_ciudad/dataset_bares_notables.py --refrescar
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import warnings
from pathlib import Path

import geopandas as gpd
import pandas as pd
import requests

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]

ENTRADA = ROOT / "outputs" / "fuentes_externas" / "wikidata" / "wikidata_bares_notables.csv"
BARRIOS = ROOT / "data" / "raw" / "geo_barrios.geojson"
OUT = ROOT / "outputs" / "BARRIDO_CIUDAD_2026-08" / "dataset_bares_notables"
CACHE = OUT / "_cache_usig.json"

USIG = "https://servicios.usig.buenosaires.gob.ar/normalizar/"
PAUSA_S = 0.35   # cortesía con un servicio público gratuito; 95 consultas no justifican apurarlo

DECLARATORIA = "Bar Notable (declaratoria patrimonial de la Ciudad Autónoma de Buenos Aires)"
NO_EXHAUSTIVO = ("Listado NO exhaustivo: son los Bares Notables cargados en Wikidata con su "
                 "declaratoria patrimonial, no el registro oficial completo.")
NO_ES_CALIDAD = ("«Bar Notable» es una declaratoria, es decir un acto administrativo por valor "
                 "patrimonial, arquitectónico o cultural. NO es una calificación de calidad "
                 "gastronómica y no debe leerse como recomendación.")


def limpiar(direccion: str) -> str:
    """La dirección postal de Wikidata, reducida a lo que USIG puede normalizar.

    Vienen con colas del tipo «. Ciudad Autónoma de Buenos Aires. Argentina» y con la palabra
    «esquina», que el normalizador entiende mejor como «y».
    """
    texto = str(direccion or "").strip()
    # La cola de país/ciudad viene con punto o sin punto, así que el punto es opcional. Y se corta
    # por «Ciudad Autónoma», NO por «Ciudad» a secas: hay una calle Ciudad de la Paz en Belgrano y
    # cortar ahí la decapitaría.
    texto = re.split(r"[.,]?\s*(?:Ciudad Autónoma|Ciudad Autonoma|C\.?A\.?B\.?A\.?|Argentina)\b",
                     texto, flags=re.I)[0]
    # Rango de alturas «1148/50/52»: USIG no lo entiende y se queda con la primera, que es la que
    # figura en la declaratoria.
    texto = re.sub(r"(\d+)\s*(?:/\s*\d+)+", r"\1", texto)
    # «esq.» y «esquina» → « y », PERO con límite de palabra. Sin él, `esq` matchea adentro de
    # «Esquiu 1393» y la deja como « y iu 1393», que USIG no resuelve y que no se ve en la tabla:
    # la fila sale «sin resolver» y parece un problema del servicio.
    texto = re.sub(r"\s*(?:\besq\.|\besquina\b)\s*", " y ", texto, flags=re.I)
    return re.sub(r"\s+", " ", texto).strip(" .,")


def consultar(direccion: str, cache: dict) -> dict | None:
    """Una consulta al normalizador, cacheada. Devuelve el candidato de CABA o None."""
    if direccion not in cache:
        respuesta = requests.get(USIG, params={"direccion": direccion, "geocodificar": "true"},
                                 timeout=25)
        respuesta.raise_for_status()
        cache[direccion] = respuesta.json()
        time.sleep(PAUSA_S)
    candidatos = cache[direccion].get("direccionesNormalizadas", [])
    # El filtro que evita el error silencioso: sin él entra la misma altura de otro partido.
    for candidato in candidatos:
        if candidato.get("cod_partido") == "caba":
            return candidato
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--refrescar", action="store_true",
                        help="ignora el caché y vuelve a consultar USIG")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    OUT.mkdir(parents=True, exist_ok=True)
    if not ENTRADA.exists():
        print(f"falta {ENTRADA.relative_to(ROOT)} — correr antes bajar_wikidata_gastro.py")
        return 1

    cache = {} if args.refrescar or not CACHE.exists() else json.loads(
        CACHE.read_text(encoding="utf-8"))
    entrada = pd.read_csv(ENTRADA)

    filas = []
    for fila in entrada.itertuples():
        consulta = limpiar(fila.direccion)
        candidato = consultar(consulta, cache) if consulta else None
        coordenadas = (candidato or {}).get("coordenadas") or {}
        filas.append({
            "wikidata_id": fila.item,
            "nombre": fila.nombre,
            "declaratoria": DECLARATORIA,
            "direccion_declarada": fila.direccion,
            "direccion_consultada": consulta,
            "direccion_normalizada": (candidato or {}).get("direccion"),
            "tipo_normalizacion": (candidato or {}).get("tipo"),
            "lon": float(coordenadas["x"]) if coordenadas else None,
            "lat": float(coordenadas["y"]) if coordenadas else None,
            "fundacion": fila.fundacion,
            "sitio_web": fila.sitio_web,
            "barrio_declarado_en_wikidata": fila.comuna_o_barrio,
            "clase_en_wikidata": fila.clase_wikidata,
            "geocodificacion": "USIG · normalizador GCBA" if candidato else "sin resolver",
            "listado_no_exhaustivo": NO_EXHAUSTIVO,
            "la_declaratoria_no_es_calidad": NO_ES_CALIDAD,
            "fuente": "Wikidata (CC0 1.0) · geocodificación USIG (GCBA)",
        })
    CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    tabla = pd.DataFrame(filas)

    # El barrio se toma de la geometría, no del texto de Wikidata: es el mismo criterio que usa
    # toda la base y evita arrastrar el «Buenos Aires» genérico que traen varios ítems.
    resueltos = tabla[tabla.lat.notna()].copy()
    puntos = gpd.GeoDataFrame(
        resueltos, geometry=gpd.points_from_xy(resueltos.lon, resueltos.lat), crs="EPSG:4326")
    barrios = gpd.read_file(BARRIOS)[["nombre", "comuna", "geometry"]].to_crs("EPSG:4326")
    ubicados = gpd.sjoin(puntos, barrios, how="left", predicate="within")
    tabla["barrio"] = tabla.wikidata_id.map(
        dict(zip(ubicados.wikidata_id, ubicados.nombre_right)))
    tabla["comuna"] = tabla.wikidata_id.map(dict(zip(ubicados.wikidata_id, ubicados.comuna)))

    sin_resolver = tabla[tabla.lat.isna()]
    fuera = tabla[tabla.lat.notna() & tabla.barrio.isna()]

    lineas = [
        "DATASET ABIERTO · Bares Notables de la Ciudad",
        "=" * 100, "",
        f"registros: {len(tabla)}",
        f"geocodificados con USIG: {int(tabla.lat.notna().sum())} "
        f"({tabla.lat.notna().mean() * 100:.1f} %)",
        f"sin resolver: {len(sin_resolver)}",
        f"geocodificados pero fuera de los 48 barrios: {len(fuera)}", "",
        "LOS DOS RECAUDOS, QUE VAN EN CADA FILA DEL CSV Y EN EL GEOJSON",
        f"  1 · {NO_EXHAUSTIVO}",
        f"  2 · {NO_ES_CALIDAD}", "",
        "POR QUÉ LA DECLARATORIA Y NO EL TIPO",
        "  81 de los 95 están cargados en Wikidata como «edificio» y no como bar o cafetería.",
        "  La consulta por tipo devuelve 17; la consulta por declaratoria devuelve 95. Preguntar",
        "  por el tipo pierde el 82 % del listado.", "",
        "POR QUÉ NO SE USARON LAS COORDENADAS DE WIKIDATA",
        "  Procedencia viciada: según el wiki de OSM, buena parte llegó por Wikipedia → Google",
        "  Maps. Se geocodificó desde la dirección postal con el normalizador oficial de USIG,",
        "  filtrando `cod_partido = caba` para no traer homónimos del conurbano.", "",
        "REPARTO POR BARRIO", "",
        tabla.barrio.value_counts().head(15).to_string(), "",
    ]
    if len(sin_resolver):
        lineas += ["SIN RESOLVER · quedan en el dataset con la dirección declarada y sin punto",
                   sin_resolver[["wikidata_id", "nombre", "direccion_declarada"]].to_string(
                       index=False), ""]
    if len(fuera):
        lineas += ["GEOCODIFICADOS FUERA DE LOS 48 BARRIOS · revisar a mano antes de publicar",
                   fuera[["wikidata_id", "nombre", "direccion_normalizada", "lon", "lat"]].to_string(
                       index=False), ""]

    salida = "\n".join(lineas)
    (OUT / "BARES_NOTABLES.txt").write_text(salida, encoding="utf-8")
    tabla.to_csv(OUT / "bares_notables_caba.csv", index=False, encoding="utf-8")
    if len(resueltos):
        publicable = tabla[tabla.lat.notna()].copy()
        gpd.GeoDataFrame(
            publicable, geometry=gpd.points_from_xy(publicable.lon, publicable.lat),
            crs="EPSG:4326").to_file(OUT / "bares_notables_caba.geojson", driver="GeoJSON")
    (OUT / "README.md").write_text(
        "# Bares Notables de la Ciudad · dataset abierto\n\n"
        f"{len(tabla)} registros. {int(tabla.lat.notna().sum())} con punto.\n\n"
        "## Dos recaudos que hay que leer antes de usarlo\n\n"
        f"1. **{NO_EXHAUSTIVO}**\n"
        f"2. **{NO_ES_CALIDAD}**\n\n"
        "## Procedencia\n\n"
        "- Listado y atributos: Wikidata, consulta por declaratoria patrimonial (P1435), CC0 1.0.\n"
        "- Coordenadas: normalizador de USIG (GCBA) desde la dirección postal declarada. **No se\n"
        "  usaron las coordenadas de Wikidata**: buena parte tiene procedencia Wikipedia → Google\n"
        "  Maps según el wiki de OSM.\n"
        "- Barrio y comuna: asignados por geometría contra los barrios oficiales.\n\n"
        "## Por qué se consulta por declaratoria y no por tipo\n\n"
        "81 de los 95 ítems están cargados en Wikidata como «edificio». La consulta por tipo\n"
        "devuelve 17 y la consulta por declaratoria devuelve 95.\n",
        encoding="utf-8")

    print(salida)
    print(f"escrito en {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
