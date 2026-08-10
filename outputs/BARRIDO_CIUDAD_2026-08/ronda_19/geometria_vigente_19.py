# -*- coding: utf-8 -*-
"""Una sola definición de «el borde vigente de cada polo» para todas las salidas de esta tanda.

Es la misma capa que dejó la tanda anterior, con las adopciones ya firmadas. Se repite acá, con
las rutas explícitas, porque las cuatro salidas de esta carpeta —solapes, correspondencia, las
cinco páginas y los establecimientos cerca del borde— tienen que medir contra **la misma**
geometría. Cuando cada script la arma por su cuenta se separan sin que nadie lo note.

QUÉ QUEDÓ ADOPTADO, Y CÓMO ENTRA ACÁ
------------------------------------
  - La Boca · Caminito: 4,15 ha, el borde extendido sobre Av. Don Pedro de Mendoza.
  - Mataderos: 43,99 ha, **borde transitorio** —no es un borde cerrado— y va marcado en cada
    salida para que ninguna tanda futura lo tome por cerrado.
  - Villa Ortúzar: 34,39 ha, las dos aceras de Av. Álvarez Thomas.
  - Balvanera · Once: se adopta **la lectura del enclave**, 19,18 ha. La lectura extendida
    —44,75 ha— queda publicada como alternativa medida y **no** entra como vigente.

LOS QUE NO TIENEN BORDE PROPIO SON TRES
---------------------------------------
Núñez y Retiro publican el polígono de su barrio; Villa Santa Rita no tiene ningún trazado y
publica su soporte. Mataderos ya no está en esa lista: tiene un borde, transitorio, y por eso se
cuenta aparte y no adentro de los tres.

Se mide en EPSG:5347 y se guarda en EPSG:4326.
"""

from pathlib import Path

import geopandas as gpd
from shapely.ops import unary_union

SALIDA = Path(__file__).resolve().parent
BARRIDO = SALIDA.parent
CRS_M, CRS_G = "EPSG:5347", "EPSG:4326"

SOPORTES = BARRIDO / "ronda_16_codex" / "geometria" / "soportes_41.geojson"
R17 = BARRIDO / "ronda_17" / "geometria" / "perimetros_cierre.geojson"
R18 = BARRIDO / "ronda_18" / "geometria" / "perimetros_ronda_18.geojson"

# Borde transitorio: existe, se publica y no es una delimitación cerrada.
TRANSITORIOS = {"Z33"}
# Sin borde propio: Villa Santa Rita (sin trazado), Núñez y Retiro (polígono de su barrio).
SIN_BORDE_PROPIO = {"Z27", "Z41", "Z46"}
DE_BARRIO = {"Z41", "Z46"}


def limpia(g):
    return g if g.is_valid else g.buffer(0)


def cargar():
    """(bordes, procedencia, soportes) con los 41 polos y de dónde sale la geometría de cada uno."""
    soportes = gpd.read_file(SOPORTES).to_crs(CRS_M).set_index("polo_id")
    bordes = {pid: limpia(g) for pid, g in soportes.geometry.items()}
    procedencia = {pid: "soporte previo" for pid in bordes}

    for ruta, etiqueta in ((R17, "cierre geométrico"), (R18, "última tanda de bordes")):
        if not ruta.exists():
            raise SystemExit(f"falta {ruta}. No se arma una geometría vigente incompleta.")
        capa = gpd.read_file(ruta).to_crs(CRS_M)
        entera = capa[capa.pieza.astype(str).str.startswith("la zona entera")]
        for r in entera.itertuples():
            if r.zona_id not in bordes:
                continue
            if "lectura_2" in str(r.pieza):
                continue  # Balvanera: lo adoptado es el enclave; la extendida se publica aparte
            bordes[r.zona_id] = limpia(r.geometry)
            procedencia[r.zona_id] = etiqueta

    vacios = [p for p, g in bordes.items() if g.is_empty]
    if vacios:
        raise SystemExit(f"geometría vacía en {vacios}. Una geometría vacía mide 0,00 ha y se "
                         f"lee como un dato. No se sigue.")
    return bordes, procedencia, soportes


def union(bordes):
    return limpia(unary_union([limpia(g) for g in bordes.values()]))


def caracter(pid):
    if pid in TRANSITORIOS:
        return "borde transitorio"
    if pid in DE_BARRIO:
        return "polígono del barrio, no del polo"
    if pid in SIN_BORDE_PROPIO:
        return "sin borde propio"
    return "borde cerrado"
