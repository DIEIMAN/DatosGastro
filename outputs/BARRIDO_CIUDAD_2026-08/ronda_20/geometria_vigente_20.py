# -*- coding: utf-8 -*-
"""La geometría vigente de los 41 polos, con la adopción de esta tanda ya aplicada.

QUÉ CAMBIA CONTRA LA TANDA ANTERIOR
-----------------------------------
Una sola cosa, y está firmada: **La Boca · Almirante Brown y Necochea pasa de 6,14 ha a la
lectura C** —extendida sólo sobre Av. Suárez y Olavarría, que la delimitación de la obra pública
ya nombraba—. La geometría no se vuelve a trazar acá: se toma **la misma pieza que la tanda
anterior midió y guardó** en `ronda_19/geometria/cinco_sin_ancla_versiones.geojson`, para que lo
adoptado sea exactamente lo que se midió y no una reconstrucción parecida.

Las otras cuatro páginas sin ancla adentro —Liniers, Balvanera y las dos de Nueva Pompeya— quedan
como estaban. La lectura extendida de cada una sigue publicada como alternativa medida y no entra
como vigente.

LO QUE SIGUE IGUAL, Y HAY QUE REPETIRLO PORQUE SE OLVIDA
--------------------------------------------------------
  - Mataderos tiene **borde transitorio**: existe, se publica y no es una delimitación cerrada.
  - Los polos **sin borde propio son tres**: Villa Santa Rita, que no tiene ningún trazado, y
    Núñez y Retiro, que publican el polígono de su barrio.
  - **Colegiales es un cuarto caso**, y esta tanda lo declara por primera vez: la capa lo trae
    como borde propio y mide 229,08 ha contra las 229,09 del barrio administrativo. La diferencia
    es de quince metros cuadrados, así que geométricamente **es** el barrio. Se marca aparte y no
    se lo mete en la lista de los tres: los tres son una decisión editorial escrita y esto es una
    coincidencia geométrica medida.

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
VERSIONES_19 = BARRIDO / "ronda_19" / "geometria" / "cinco_sin_ancla_versiones.geojson"

TRANSITORIOS = {"Z33"}
SIN_BORDE_PROPIO = {"Z27", "Z41", "Z46"}
DE_BARRIO = {"Z41", "Z46"}
# Declarado, no adoptado: la capa lo trae como borde propio y la medición dice que es el barrio.
COINCIDE_CON_SU_BARRIO = {"Z43": "Colegiales"}

# Lo que esta tanda adopta: (zona, la versión exacta que se toma de la capa medida).
ADOPCIONES = {
    "Z52": "C · sólo sobre calles que el perímetro escrito nombra",
}
POR_QUE = {
    "Z52": ("se extiende sobre Av. Suárez y Olavarría, que la delimitación de la obra pública ya "
            "nombraba, y contiene a Banchero, La Buena Medida y el Café Roma. No se extiende "
            "hasta los otros cinco porque llegar a ellos exige calles que ninguna fuente escribe"),
}


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

    # --- la adopción de esta tanda ------------------------------------------------------------
    if not VERSIONES_19.exists():
        raise SystemExit(f"falta {VERSIONES_19}: sin ella no se puede adoptar la pieza medida, y "
                         f"redibujarla sería otra geometría. No se sigue.")
    versiones = gpd.read_file(VERSIONES_19).to_crs(CRS_M)
    for pid, version in ADOPCIONES.items():
        sub = versiones[(versiones.zona_id == pid) & (versiones.version == version)]
        if len(sub) != 1:
            raise SystemExit(f"la versión «{version}» de {pid} aparece {len(sub)} veces en "
                             f"{VERSIONES_19.name}. Se esperaba exactamente una. No se sigue.")
        bordes[pid] = limpia(sub.geometry.iloc[0])
        procedencia[pid] = f"adoptado en esta tanda · {version}"

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
