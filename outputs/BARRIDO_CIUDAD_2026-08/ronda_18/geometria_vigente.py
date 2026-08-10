# -*- coding: utf-8 -*-
"""Una sola definición de «el borde vigente de cada polo», para las tres salidas de la ronda.

El control de anclas, la tabla de solapes y la correspondencia con las concentraciones tienen que
medir contra **la misma** geometría. Cuando cada script la arma por su cuenta, se separan sin que
nadie lo note: alcanza con que uno incorpore una adopción nueva y el otro no.

El orden de precedencia es el de las rondas: soporte previo -> lo que cerró la ronda 17 -> lo que
adopta la ronda 18. Balvanera es la excepción y está declarada: su lectura 2 se mide y se entrega,
pero **no** entra como vigente, porque la decisión la firma quien escribe.
"""

from pathlib import Path

import geopandas as gpd
from shapely.ops import unary_union

BARRIDO = Path(__file__).resolve().parents[1]
SALIDA = Path(__file__).resolve().parent
CRS_M = "EPSG:5347"

SOPORTES = BARRIDO / "ronda_16_codex" / "geometria" / "soportes_41.geojson"
R17 = BARRIDO / "ronda_17" / "geometria" / "perimetros_cierre.geojson"
R18 = SALIDA / "geometria" / "perimetros_ronda_18.geojson"

# Mataderos entra con un borde TENTATIVO. Va marcado en cada salida para que ninguna tanda futura
# lo tome por un borde cerrado.
TENTATIVOS = {"Z33"}
# Los que no tienen un borde propio: dos no tienen ninguno (Villa Santa Rita y, hasta esta ronda,
# Mataderos) y dos publican el polígono de su barrio (Núñez y Retiro).
SIN_BORDE_PROPIO = {"Z27", "Z33", "Z41", "Z46"}


def limpia(g):
    return g if g.is_valid else g.buffer(0)


def cargar():
    """(bordes, procedencia, soportes) con los 41 polos y de dónde sale la geometría de cada uno."""
    soportes = gpd.read_file(SOPORTES).to_crs(CRS_M).set_index("polo_id")
    bordes = {pid: limpia(g) for pid, g in soportes.geometry.items()}
    procedencia = {pid: "soporte previo (ronda 16)" for pid in bordes}

    for ruta, etiqueta in ((R17, "ronda 17"), (R18, "ronda 18")):
        if not ruta.exists():
            raise SystemExit(f"falta {ruta}. No se arma una geometría vigente incompleta.")
        capa = gpd.read_file(ruta).to_crs(CRS_M)
        entera = capa[capa.pieza.astype(str).str.startswith("la zona entera")]
        for r in entera.itertuples():
            if r.zona_id not in bordes:
                continue
            if "lectura_2" in str(r.pieza):
                continue  # Balvanera: la decisión está abierta y vigente sigue la lectura 1
            bordes[r.zona_id] = limpia(r.geometry)
            procedencia[r.zona_id] = etiqueta

    vacios = [p for p, g in bordes.items() if g.is_empty]
    if vacios:
        raise SystemExit(f"geometría vacía en {vacios}. Una geometría vacía mide 0,00 ha y se "
                         f"lee como un dato. No se sigue.")
    return bordes, procedencia, soportes


def union(bordes):
    return limpia(unary_union([limpia(g) for g in bordes.values()]))
