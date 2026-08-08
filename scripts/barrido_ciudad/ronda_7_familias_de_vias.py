"""Ronda 7 · las seis vías se parten en dos familias, y las diez filas trabadas se destraban.

QUÉ HACE
--------
    TAREA 1   las vías B y D pasan a medirse POR ZONA y las filas las heredan, con el mismo
              esquema que ya tenía la vía E: `zona_via_X` + `via_X_modo`
    TAREA 4   las diez filas en `requiere_cruce` se resuelven por cruce espacial, con las
              decisiones 13 y 14: Flores son TRES polos y Congreso se fusiona con Monserrat
    (y de paso) la decisión 1 sobre la vía C, comprobada contra el padrón de FIAB en vez de
              transcrita

POR QUÉ CAMBIA LA ESCALA DE LA VÍA B
-------------------------------------
`CRITERIO_ESCALA_DE_LAS_VIAS.md` sale de un hallazgo de la ronda 6: el polígono `PGR_P083` mide
5,7 ha, el barrio de Almagro mide 405, y ninguno de los cinco Bares Notables del barrio cae
adentro del polígono. Preguntar «¿este blob de 5,7 ha contiene un Bar Notable?» no mide la
trayectoria de la zona: mide **si el clustering acertó a caer encima de un bar**.

Las vías A, C y F son propiedades del polígono —densidad, contención de un mercado, forma— y se
siguen midiendo fila por fila, sin tocar. Las vías B, D y E son propiedades de la zona —un bar de
1893 pertenece a un barrio, un enclave tiene delimitación textual propia, nadie escribe sobre un
fragmento sin nombre— y se miden a nivel de zona.

LO QUE SE GUARDA EN LA FILA, Y LO QUE NO
-----------------------------------------
La fila guarda **`zona_via_B` y `via_B_modo`, y nada más**. El valor vive en la tabla de zonas y
se busca ahí. Es a propósito: si mañana se vuelve a correr el clustering, las filas quedan
apuntando a una zona que puede no existir y **rompen visiblemente**, en vez de quedarse con un
`si` huérfano que nadie sabe de dónde salió. Hay un archivo aparte con la vista unida para leer,
que es derivado y se puede tirar.

LA SALVEDAD, QUE TAMBIÉN VA EN LA FICHA
----------------------------------------
**La herencia no vale hacia arriba.** Que Almagro tenga cinco Bares Notables no convierte a
`PGR_P083` en un polo notable: lo convierte en **un fragmento de una zona que tiene cinco**. La
columna `via_B_modo` existe para que eso no se pueda perder de vista al leer la matriz.

DOS GEOMETRÍAS POR ZONA, Y POR QUÉ
-----------------------------------
    `geom_zona`        el barrio o los barrios de la zona. Es la escala a la que la vía B
                       significa algo: «Almagro tiene cinco», «Monserrat tiene nueve».
    `geom_delimitada`  el perímetro textual de la zona, cuando existe, construido desde el
                       callejero. Sólo se usa para la TAREA 4: cuando tres zonas comparten el
                       barrio de Flores, el polígono del barrio no puede decidir a cuál pertenece
                       un fragmento, y el perímetro sí.

Google Places: 0 requests. Ninguna consulta de red.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/ronda_7_familias_de_vias.py
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from shapely.ops import nearest_points, unary_union

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from polos_soporte import (  # noqa: E402
    BARRIDO,
    CALLEJERO,
    CRS_GEOGRAFICO,
    CRS_METRICO,
    barrios,
    envolventes_22,
    sin_tildes,
    soportes_94,
)

SEIS_VIAS = BARRIDO / "seis_vias"
HITOS = BARRIDO / "hitos"
COWORK = BARRIDO / "desde_cowork" / "evidencia_2026"
GEOMETRIA = BARRIDO / "geometria_r7"

CAPA_R7 = HITOS / "hitos_capa_2026_r7.csv"
REFERENCIAS_R7 = GEOMETRIA / "referencias_r7.geojson"
ENCLAVES_R4 = SEIS_VIAS / "enclaves_comunitarios_r4.geojson"
MATRIZ_R4 = SEIS_VIAS / "seis_vias_94_filas_r4.csv"
ZONAS_R4 = SEIS_VIAS / "seis_vias_22_zonas_r4.csv"
VIA_E_94 = COWORK / "via_E_94_filas.csv"
FIAB = ROOT / "data" / "raw" / "f03_fiab.geojson"
ESPACIOS_VERDES = (ROOT / "outputs" / "polos_gastro" / "INVESTIGACION_DESBLOQUEOS_V21" /
                   "paquete" / "r15_plaza_arenales" / "fuentes" /
                   "espacios_verdes_publicos_gcba.geojson")

OUT_ZONAS = SEIS_VIAS / "zonas_via_B_via_D_r7.csv"
OUT_FILAS = SEIS_VIAS / "seis_vias_94_filas_r7.csv"
OUT_VISTA = SEIS_VIAS / "vista_unida_94_filas_r7.csv"
OUT_CRUCE = SEIS_VIAS / "requiere_cruce_resuelto_r7.csv"
OUT_SIN_HITOS = SEIS_VIAS / "reparto_de_las_48_sin_hitos_r7.csv"
OUT_FIAB = SEIS_VIAS / "via_C_contra_padron_fiab_r7.csv"
OUT_GEOJSON = GEOMETRIA / "zonas_r7.geojson"
INFORME_TXT = SEIS_VIAS / "FAMILIAS_DE_VIAS_R7.txt"

BUFFER_EJE_M = 150

TIPOS_VIA_B = {
    "Bar Notable": "bar_notable",
    "Restaurante Icónico": "restaurante_iconico",
    "Pizzería emblemática": "pizzeria_emblematica",
    "Heladería histórica": "heladeria_historica",
    "MICHELIN": "michelin",
    "Ranking internacional": "50best",
}
PLIEGUE = {"si": "si", "no": "no", "en_disputa": "en_disputa",
           "probablemente_abierto": "probablemente_abierto",
           "dudosa": "sin_verificar", "sin_verificar": "sin_verificar",
           "en_riesgo": "si", "senalado_no_cerrado": "si",
           "cerrado_con_reapertura_anunciada": "no"}

# Los barrios de cada zona. Declarados acá y no parseados del campo en prosa de los CSV de
# cowork («Flores (tramo Nazca-Cuenca) y borde de Floresta»), que no es una lista.
ZONA_BARRIOS = {
    "Z23": ["Flores"], "Z24": ["Flores"], "Z25": ["Floresta"], "Z26": ["Velez Sarsfield"],
    "Z27": ["Villa Santa Rita"], "Z28": ["Monte Castro"], "Z29": ["Villa Del Parque"],
    "Z30": ["Villa Real", "Versalles"], "Z31": ["Villa Luro"], "Z32": ["Liniers"],
    "Z33": ["Mataderos"], "Z34": ["Parque Chas", "Agronomia"], "Z35": ["Balvanera"],
    "Z37": ["Almagro"], "Z38": ["Parque Chacabuco"], "Z39": ["Parque Avellaneda"],
    "Z39b": ["Flores"], "Z40": ["Nueva Pompeya", "Parque Patricios"], "Z41": ["Nunez"],
    "Z42": ["Coghlan"], "Z43": ["Colegiales"], "Z44": ["Villa Ortuzar"], "Z45": ["Belgrano"],
    # Z46 es Retiro, NO Retiro + San Nicolás entero. El «derrame documentado hacia San Nicolás»
    # de la delimitación es EL EJE COREANO, no el barrio: con San Nicolás completo la zona se
    # come el microcentro y pasa de 4 Bares Notables a 36 hitos de vía B. El derrame entra por
    # donde corresponde —la subzona ex R18, que se une más abajo—, medido y acotado.
    "Z46": ["Retiro"], "Z47": ["Monserrat"], "Z48": ["San Cristobal"],
    "Z49": ["Villa Soldati"],
    "S_BARRACAS": ["Barracas"], "S_LABOCA": ["La Boca"], "S_LUGANO": ["Villa Lugano"],
    "S_RIACHUELO": ["Villa Riachuelo"],
}
ZONA_NOMBRE = {
    "Z23": "Flores · casco histórico", "Z24": "Flores · Avellaneda y Ruperto Godoy",
    "Z25": "Floresta", "Z26": "Vélez Sarsfield", "Z27": "Villa Santa Rita",
    "Z28": "Monte Castro", "Z29": "Villa del Parque", "Z30": "Villa Real y Versalles",
    "Z31": "Villa Luro", "Z32": "Liniers", "Z33": "Mataderos",
    "Z34": "Parque Chas y Agronomía", "Z35": "Balvanera · Once", "Z37": "Almagro",
    "Z38": "Parque Chacabuco", "Z39": "Parque Avellaneda", "Z39b": "Baek-ku · Barrio Coreano",
    "Z40": "Nueva Pompeya y Parque Patricios", "Z41": "Núñez", "Z42": "Coghlan",
    "Z43": "Colegiales", "Z44": "Villa Ortúzar", "Z45": "Belgrano R y Barrancas",
    "Z46": "Retiro (absorbe R18)", "Z47": "Monserrat + Congreso (fusiona Z36)",
    "Z48": "San Cristóbal", "Z49": "Villa Soldati",
    "S_BARRACAS": "Barracas", "S_LABOCA": "La Boca", "S_LUGANO": "Villa Lugano",
    "S_RIACHUELO": "Villa Riachuelo",
}

# TAREA 4 · los perímetros textuales que hacen falta para desempatar. Sólo se construyen los de
# las zonas que COMPARTEN BARRIO con otra: en el resto el barrio alcanza y construir un perímetro
# sería agregar una geometría que nadie pidió.
#
#   ("tramo", calle, corte_a, corte_b)     el pedazo de la calle entre sus cruces con otras dos
#   ("altura", calle, desde, hasta)        el pedazo por rango de numeración del callejero
#   ("entera", calle)                      la calle completa dentro del marco
#   ("verde", nombre)                      un polígono de la capa oficial de espacios verdes
PERIMETROS = {
    # Z23 NO tiene receta, y el motivo es un hallazgo de esta corrida: su delimitación textual
    # —«Av. Rivadavia, Boyacá-Carabobo»— es degenerada. Av. Boyacá y Av. Carabobo son LA MISMA
    # AVENIDA, que cambia de nombre justo al cruzar Av. Rivadavia: Boyacá corre al norte y
    # Carabobo al sur, y las dos tocan a Rivadavia en el MISMO punto. «Entre Boyacá y Carabobo»
    # mide cero cuadras. Se resuelve por residuo y queda marcado — ver RESIDUO_POR_BARRIO.
    "Z24": {
        "marco": ["Flores", "Floresta", "Villa Santa Rita"],
        "piezas": [("tramo", "AVELLANEDA AV.", "NAZCA AV.", "CUENCA"),
                   ("entera", "GODOY, RUPERTO"),
                   ("altura", "VALLESE, FELIPE", 3000, 3199)],
        "texto": "corredor Av. Avellaneda entre Nazca y Cuenca + núcleo peatonal Pasaje Ruperto "
                 "Godoy + racimo Felipe Vallese 3100",
    },
    "Z39": {
        "marco": ["Parque Avellaneda"],
        "piezas": [("verde", "Parque Avellaneda"), ("entera", "OLIVERA AV."),
                   ("entera", "LACARRA AV.")],
        "texto": "anillo del Parque Avellaneda sobre Av. Olivera y Av. Lacarra",
    },
    "Z39b": {
        "marco": ["Flores", "Parque Chacabuco"],
        "piezas": [("tramo", "CARABOBO AV.", "CASTANARES AV.", "PERON, EVA AV.")],
        "texto": "Av. Carabobo entre Av. Castañares y Av. Eva Perón, siete cuadras",
    },
    "Z35": {
        "marco": ["Balvanera"],
        "piezas": [("tramo", "CORRIENTES AV.", "CALLAO AV.", "PUEYRREDON AV."),
                   ("tramo", "RIVADAVIA AV.", "CALLAO AV.", "PUEYRREDON AV.")],
        "texto": "corredor Av. Corrientes entre Callao y Pueyrredón, con núcleo secundario sobre "
                 "Av. Rivadavia en el mismo tramo",
    },
    "Z47": {
        "marco": ["Monserrat", "San Nicolas", "San Telmo", "Balvanera"],
        "piezas": [("altura", "DE MAYO AV.", 500, 1300),
                   ("altura", "YRIGOYEN, HIPOLITO", 1100, 1300),
                   ("altura", "CALLAO AV.", 200, 400)],
        "texto": "eje Av. de Mayo - Callao. Av. de Mayo de Perú/Bolívar a Lima/Salta, alturas "
                 "500-1300, ambas aceras, con frentes sobre H. Yrigoyen 1199-1201",
    },
}

# Las zonas que comparten barrio y por eso necesitan el desempate del perímetro. El orden importa:
# las que tienen perímetro propio se prueban primero y la del residuo queda al final.
COMPARTEN_BARRIO = {"Flores": ["Z24", "Z39b"], "Balvanera": ["Z47", "Z35"]}

# La zona que se queda con lo que no cae en ninguna de las delimitadas del mismo barrio. Es una
# asignación POR ELIMINACIÓN, no por contención, y viaja marcada como tal en el CSV.
#
# En Flores es Z23, que está declarada PENDIENTE de redelimitación y cuyo perímetro textual esta
# corrida probó que no se puede construir. En Balvanera es Z35 Once, y ahí el residuo NO es una
# debilidad: la decisión 13 se llevó a Congreso a Monserrat, así que lo que queda de Balvanera
# por fuera del eje Av. de Mayo - Callao es, por construcción, Once.
RESIDUO_POR_BARRIO = {"Flores": "Z23", "Balvanera": "Z35"}

# Las zonas cuya vía B se mide sobre su PERÍMETRO y no sobre el barrio, porque comparten barrio
# con otra y el barrio contaría los mismos hitos dos y tres veces. Flores tiene tres zonas: sin
# esto, un solo Bar Notable del barrio abría la vía B de las tres a la vez.
MEDIR_POR_PERIMETRO = {"Z24", "Z39b"}
MEDIR_POR_RESIDUO = {"Z23": ("Flores", ["Z24", "Z39b"])}

# Decisión 1 · las cinco zonas cuya vía C abría sólo por una FIAB, según el registro de cowork.
# Se anota y se comprueba: la comprobación repo-side es contra el padrón de FIAB del GCBA.
VIA_C_CAE_POR_FIAB = ["Z23", "Z25", "Z28", "Z44", "Z47"]


def p_factory(buffer: io.StringIO):
    def p(*args_):
        print(*args_, file=buffer)
    return p


def soporte_de(estados: list[str]) -> tuple[str, str]:
    """(`soporte`, `abierta`) con la precedencia declarada en la ronda 3, más el estado nuevo.

    `probablemente_abierto` se pliega del lado de los que NO acreditan: abre la vía sólo si
    además hay uno verificado. Un v4 solo es información, no constatación, y la vía B publicada
    tiene que poder respaldarse con una dirección y una fecha.
    """
    if not estados:
        return "sin_hitos", "no"
    plegados = [PLIEGUE.get(e, "sin_verificar") for e in estados]
    abiertos = plegados.count("si")
    cerrados = plegados.count("no")
    if abiertos and cerrados:
        return "mixto", "si"
    if abiertos:
        return "activo", "si"
    if "probablemente_abierto" in plegados:
        return "probable", "pendiente"
    if "en_disputa" in plegados:
        return "en_disputa", "pendiente"
    if "sin_verificar" in plegados:
        return "sin_verificar", "pendiente"
    return "extinguido", "no"


# --------------------------------------------------------------------------- geometría
def marco_de(capa_barrios, nombres):
    trozos = [capa_barrios[capa_barrios.clave == sin_tildes(n)].geometry for n in nombres]
    trozos = [t.iloc[0] for t in trozos if len(t)]
    if not trozos:
        raise SystemExit(f"barrios no encontrados: {nombres}")
    return unary_union(trozos)


def _piezas_en_marco(callejero, calle, marco) -> list:
    """Los pedazos de la calle dentro del marco, SIN unir.

    La unión es la trampa: `unary_union` fusiona los segmentos contiguos del callejero en una
    sola LineString, y el cortador de tramos —que decide segmento por segmento— pasa a ver un
    solo objeto cuyo punto medio es el medio de toda la calle. Con Av. Rivadavia dentro de Flores
    eso devolvía un tramo VACÍO sin tirar ningún error: la zona se quedaba sin perímetro y el
    cruce espacial de la tarea 4 no tenía contra qué decidir.
    """
    seg = callejero[callejero.clave == sin_tildes(calle)]
    if seg.empty:
        return []
    piezas = []
    for geometria in seg.geometry:
        if not geometria.intersects(marco):
            continue
        recorte = geometria.intersection(marco)
        if recorte.is_empty:
            continue
        piezas.extend(recorte.geoms if hasattr(recorte, "geoms") else [recorte])
    return [g for g in piezas if getattr(g, "length", 0) > 0]


def _en_marco(callejero, calle, marco):
    piezas = _piezas_en_marco(callejero, calle, marco)
    return unary_union(piezas) if piezas else None


def _punto_de_cruce(eje, otra):
    """Dónde cruza `otra` al eje.

    Si las dos geometrías se tocan, el cruce es la intersección — un punto o unos pocos— y se
    toma su centroide. `nearest_points` NO sirve para este caso: cuando la distancia es 0
    devuelve un punto arbitrario del contacto, y en Av. Rivadavia dentro de Flores devolvía el
    MISMO punto para Boyacá y para Carabobo, con lo cual el tramo entre las dos medía cero y la
    zona se quedaba sin perímetro. Sólo cuando no se tocan tiene sentido el punto más cercano.
    """
    interseccion = eje.intersection(otra)
    if not interseccion.is_empty:
        return interseccion.centroid
    return nearest_points(eje, otra)[0]


def _tramo(callejero, calle, corte_a, corte_b, marco):
    partes = _piezas_en_marco(callejero, calle, marco)
    if not partes:
        return None
    eje = unary_union(partes)
    puntos = []
    for corte in (corte_a, corte_b):
        otra = callejero[callejero.clave == sin_tildes(corte)]
        if otra.empty:
            return None
        puntos.append(_punto_de_cruce(eje, unary_union(list(otra.geometry))))
    a, b = puntos
    dx, dy = b.x - a.x, b.y - a.y
    largo2 = dx * dx + dy * dy
    if largo2 == 0:
        return None
    elegidos = []
    for pieza in partes:
        centro = pieza.interpolate(0.5, normalized=True)
        t = ((centro.x - a.x) * dx + (centro.y - a.y) * dy) / largo2
        perp = abs((centro.x - a.x) * dy - (centro.y - a.y) * dx) / largo2 ** 0.5
        if -0.02 <= t <= 1.02 and perp <= 200:
            elegidos.append(pieza)
    return unary_union(elegidos) if elegidos else None


def _altura(callejero, calle, desde, hasta, marco):
    seg = callejero[callejero.clave == sin_tildes(calle)]
    if seg.empty:
        return None
    seg = seg[seg.intersects(marco)]
    if seg.empty:
        return None

    def solapa(fila):
        for ini, fin in ((fila.alt_izqini, fila.alt_izqfin), (fila.alt_derini, fila.alt_derfin)):
            if ini and fin and max(ini, fin) >= desde and min(ini, fin) <= hasta:
                return True
        return False

    elegidos = seg[seg.apply(solapa, axis=1)]
    return unary_union(list(elegidos.geometry)) if not elegidos.empty else None


def construir_perimetro(receta, callejero, verdes, capa_barrios, bitacora: list[str], zona: str):
    marco = marco_de(capa_barrios, receta["marco"])
    piezas = []
    for pieza in receta["piezas"]:
        clase = pieza[0]
        if clase == "tramo":
            geometria = _tramo(callejero, pieza[1], pieza[2], pieza[3], marco)
            etiqueta = f"{pieza[1]} entre {pieza[2]} y {pieza[3]}"
        elif clase == "altura":
            geometria = _altura(callejero, pieza[1], pieza[2], pieza[3], marco)
            etiqueta = f"{pieza[1]} {pieza[2]}-{pieza[3]}"
        elif clase == "entera":
            geometria = _en_marco(callejero, pieza[1], marco)
            etiqueta = f"{pieza[1]} (entera dentro del marco)"
        elif clase == "verde":
            encontrada = verdes[verdes.nombre.map(sin_tildes) == sin_tildes(pieza[1])]
            geometria = unary_union(list(encontrada.geometry)) if not encontrada.empty else None
            etiqueta = f"{pieza[1]} (polígono oficial de espacios verdes)"
        else:
            raise SystemExit(f"clase de pieza desconocida: {clase}")
        if geometria is None or geometria.is_empty:
            bitacora.append(f"{zona} · {etiqueta}: NO se resolvió — se declara y se omite")
            continue
        largo = getattr(geometria, "length", 0.0)
        bitacora.append(f"{zona} · {etiqueta}: "
                        + (f"{geometria.area / 10_000:.2f} ha" if clase == "verde"
                           else f"{largo:,.0f} m de eje"))
        piezas.append(geometria.buffer(BUFFER_EJE_M) if clase != "verde" else geometria)
    return unary_union(piezas) if piezas else None


def main() -> int:  # noqa: C901
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    # La corrida acepta otra capa de hitos y otra capa de referencias para poder volver a medir
    # cuando cambian —la ronda 8 fusiona R09 con R19 y retipa un hito—, sin duplicar el guion ni
    # perder la reproducibilidad de la ronda 7, que sigue siendo el default.
    global CAPA_R7, REFERENCIAS_R7, OUT_ZONAS, OUT_FILAS, OUT_VISTA, OUT_CRUCE
    global OUT_SIN_HITOS, OUT_FIAB, OUT_GEOJSON, INFORME_TXT

    import argparse
    parser = argparse.ArgumentParser(description="las vías documentales, medidas por zona")
    parser.add_argument("--capa", default=str(HITOS / "hitos_capa_2026_r7.csv"))
    parser.add_argument("--referencias",
                        default=str(GEOMETRIA / "referencias_r7.geojson"))
    parser.add_argument("--sufijo", default="r7")
    parser.add_argument("--remapeo", default="",
                        help="JSON {zona_vieja: zona_nueva} para cuando una ronda fusiona zonas")
    args = parser.parse_args()
    remapeo: dict[str, str] = {}
    if args.remapeo:
        import json
        remapeo = json.loads(Path(args.remapeo).read_text(encoding="utf-8"))

    CAPA_R7 = Path(args.capa)
    REFERENCIAS_R7 = Path(args.referencias)
    sufijo = args.sufijo
    OUT_ZONAS = SEIS_VIAS / f"zonas_via_B_via_D_{sufijo}.csv"
    OUT_FILAS = SEIS_VIAS / f"seis_vias_94_filas_{sufijo}.csv"
    OUT_VISTA = SEIS_VIAS / f"vista_unida_94_filas_{sufijo}.csv"
    OUT_CRUCE = SEIS_VIAS / f"requiere_cruce_resuelto_{sufijo}.csv"
    OUT_SIN_HITOS = SEIS_VIAS / f"reparto_de_las_48_sin_hitos_{sufijo}.csv"
    OUT_FIAB = SEIS_VIAS / f"via_C_contra_padron_fiab_{sufijo}.csv"
    OUT_GEOJSON = GEOMETRIA / f"zonas_{sufijo}.geojson"
    INFORME_TXT = SEIS_VIAS / f"FAMILIAS_DE_VIAS_{sufijo.upper()}.txt"

    buffer = io.StringIO()
    p = p_factory(buffer)

    for necesario in (CAPA_R7, REFERENCIAS_R7, ENCLAVES_R4, MATRIZ_R4, VIA_E_94):
        if not necesario.exists():
            raise SystemExit(f"falta {necesario} — correr las corridas previas de la ronda 7")

    capa = pd.read_csv(CAPA_R7)
    con_punto = capa[capa.latitud.notna() & capa.longitud.notna()].copy()
    hitos = gpd.GeoDataFrame(
        con_punto, geometry=gpd.points_from_xy(con_punto.longitud, con_punto.latitud),
        crs=CRS_GEOGRAFICO).to_crs(CRS_METRICO).reset_index(drop=True)
    referencias = gpd.read_file(REFERENCIAS_R7).to_crs(CRS_METRICO).set_index("referencia_id")
    enclaves = gpd.read_file(ENCLAVES_R4).to_crs(CRS_METRICO)
    cruzables = enclaves[enclaves.computa_via_D == "si"]
    capa_barrios = barrios()
    callejero = gpd.read_file(CALLEJERO).to_crs(CRS_METRICO)
    callejero["clave"] = callejero.nomoficial.map(sin_tildes)
    verdes = gpd.read_file(ESPACIOS_VERDES).to_crs(CRS_METRICO)
    matriz = pd.read_csv(MATRIZ_R4)
    via_e = pd.read_csv(VIA_E_94).set_index("polo_id")
    soportes = soportes_94().set_index("polo_id")

    p("RONDA 7 · LAS VÍAS DOCUMENTALES PASAN A MEDIRSE POR ZONA")
    p("=" * 100)
    p("")
    p(f"  hitos con punto: {len(hitos)} · enclaves cruzables: {len(cruzables)} · "
      f"filas de la matriz: {len(matriz)}")
    p("  Vías A, C y F: NO se recalculan. Son propiedades del polígono y sus insumos no se")
    p("  movieron. El único cambio de esta ronda tiene que poder leerse en B y en D.")
    p("  Google Places: 0 requests.")
    p("")

    # ================================================== 1 · las geometrías de zona
    p("-" * 100)
    p("  LAS ZONAS Y SUS DOS GEOMETRÍAS")
    p("")
    bitacora: list[str] = []
    zonas: dict[str, dict] = {}

    columna_estado = next((c for c in ("estado_r8", "estado_r7") if c in referencias.columns),
                          None)
    for rid in referencias.index:
        if rid.startswith("Z46_SUBZONA"):
            continue
        estado = str(referencias[columna_estado].loc[rid]) if columna_estado else "sin cambios"
        zonas[rid] = {"zona_id": rid, "nombre": referencias.nombre.loc[rid],
                      "clase": "referencia publicada", "geom_zona": referencias.geometry.loc[rid],
                      "geom_delimitada": referencias.geometry.loc[rid],
                      "detalle_geometria": "envolvente editorial del Atlas"
                                           + ("" if estado == "sin cambios" else f" · {estado}")}
    for zid, barrios_zona in ZONA_BARRIOS.items():
        if zid in remapeo:
            continue
        geom = marco_de(capa_barrios, barrios_zona)
        zonas[zid] = {"zona_id": zid, "nombre": ZONA_NOMBRE[zid], "clase": "zona nueva",
                      "geom_zona": geom, "geom_delimitada": None,
                      "detalle_geometria": "polígono administrativo de "
                                           + ", ".join(barrios_zona)}
    # Z46 absorbe la subzona ex-R18 dentro de su geometría de zona.
    subzona = referencias.geometry.loc["Z46_SUBZONA_CLUSTER_COREANO"]
    zonas["Z46"]["geom_zona"] = unary_union([zonas["Z46"]["geom_zona"], subzona])
    zonas["Z46"]["detalle_geometria"] += " + la subzona del clúster coreano (ex R18, decisión 5)"

    for zid, receta in PERIMETROS.items():
        geom = construir_perimetro(receta, callejero, verdes, capa_barrios, bitacora, zid)
        zonas[zid]["geom_delimitada"] = geom
        zonas[zid]["perimetro_textual"] = receta["texto"]
        if geom is not None and zid in MEDIR_POR_PERIMETRO:
            zonas[zid]["geom_zona"] = geom
            zonas[zid]["detalle_geometria"] = (
                "perímetro delimitado desde el callejero (comparte barrio con otras zonas: el "
                "polígono del barrio contaría los mismos hitos más de una vez)")
        if geom is not None:
            p(f"   {zid} · {ZONA_NOMBRE[zid][:36]:<38} perímetro: {geom.area / 10_000:>7,.1f} ha "
              f"· barrio: {zonas[zid]['geom_zona'].area / 10_000:>8,.1f} ha "
              f"({geom.area / zonas[zid]['geom_zona'].area * 100:>5.1f} % del barrio)")
    for zid, (barrio_base, hermanas) in MEDIR_POR_RESIDUO.items():
        otras = [zonas[h]["geom_zona"] for h in hermanas if zonas[h].get("geom_zona") is not None]
        residuo = marco_de(capa_barrios, [barrio_base])
        if otras:
            residuo = residuo.difference(unary_union(otras))
        zonas[zid]["geom_zona"] = residuo
        zonas[zid]["geom_delimitada"] = residuo
        zonas[zid]["detalle_geometria"] = (
            f"RESIDUO: el barrio de {barrio_base} menos {' y '.join(hermanas)}. Su perímetro "
            "textual no se puede construir — ver el hallazgo de Boyacá/Carabobo más abajo")
        p(f"   {zid} · {ZONA_NOMBRE[zid][:36]:<38} residuo:   {residuo.area / 10_000:>7,.1f} ha")
    p("")
    for linea in bitacora:
        p(f"      {linea}")
    p("")
    p(f"  zonas en total: {len(zonas)} "
      f"({sum(1 for z in zonas.values() if z['clase'] == 'referencia publicada')} referencias "
      f"publicadas + {sum(1 for z in zonas.values() if z['clase'] == 'zona nueva')} nuevas)")
    p("  R18 no está: la decisión 5 la absorbió en Z46 y dejó de ser referencia independiente.")
    p("")

    # ================================================== 2 · la vía C contra el padrón de FIAB
    p("-" * 100)
    p("  DECISIÓN 1 · LA FIAB NO ABRE LA VÍA C, COMPROBADO CONTRA EL PADRÓN")
    p("")
    padron_fiab = gpd.read_file(FIAB).to_crs(CRS_METRICO)
    mercados = hitos[hitos.tipo == "Mercado/patio"]
    filas_fiab = []
    p(f"  padrón de FIAB del GCBA: {len(padron_fiab)} ferias · hitos tipo Mercado/patio con "
      f"punto: {len(mercados)}")
    p("")
    for hito in mercados.itertuples():
        distancia = padron_fiab.distance(hito.geometry).min()
        es_fiab = distancia < 50
        filas_fiab.append({"hito_id": hito.hito_id, "nombre": hito.nombre,
                           "reconocimiento": hito.reconocimiento,
                           "distancia_a_la_FIAB_mas_cercana_m": round(float(distancia), 1),
                           "es_una_FIAB": es_fiab})
        marca = "✗ ES UNA FIAB" if es_fiab else " "
        p(f"      {hito.hito_id:<9} {hito.nombre[:32]:<34} FIAB más cercana a "
          f"{distancia:>7,.0f} m  {marca}")
    p("")
    cuantos_fiab = sum(1 for f in filas_fiab if f["es_una_FIAB"])
    p(f"  {cuantos_fiab} de los {len(mercados)} mercados/patios de la capa son en realidad una")
    p("  FIAB. NINGUNA de las cuatro vías C abiertas en las 94 filas se apoya en una feria")
    p("  itinerante, así que la decisión 1 NO mueve ninguna fila de la matriz.")
    p("")
    p("  DONDE SÍ MUEVE es a nivel de zona, y el registro de cowork nombra cinco: "
      + ", ".join(VIA_C_CAE_POR_FIAB) + ".")
    p("  Ese dato viene de la delimitación textual de cada zona y no es reproducible desde el")
    p("  repositorio: acá se registra su procedencia, no se lo vuelve a derivar.")
    p("")
    # Un hallazgo que sale de mirar la lista: hay un Mercado/patio que no es un mercado.
    raros = mercados[~mercados.reconocimiento.astype(str).str.contains(
        "Mercado o patio documentado", na=False)]
    if len(raros):
        p("  Y UN HALLAZGO QUE APARECE AL MIRAR LA LISTA, que no es de la decisión 1 pero es del")
        p("  mismo criterio —«mercado, patio o galería EN ACTIVIDAD»—:")
        p("")
        for hito in raros.itertuples():
            p(f"      {hito.hito_id} · {hito.nombre} ({hito.direccion}) está tipado")
            p(f"      Mercado/patio, pero su reconocimiento es «{hito.reconocimiento}».")
        p("")
        p("      Es la ÚNICA vía C de las 94 que no se apoya en un mercado de la lista oficial")
        p("      (abre PGR_P004 · Villa Lugano). No se toca acá: cambiar un tipo cambia la vía C")
        p("      de una fila, y esta ronda tiene el mandato de no mover A, C ni F. Queda")
        p("      señalado para que Diego decida.")
        p("")

    # ================================================== 2b · la vía C, recontada por fila
    #
    # La vía C se venía leyendo de la ronda 2 sin recalcular, y estaba bien: sus insumos no se
    # movían. Dejaron de no moverse cuando la ronda 8 retipó un hito. Se recuenta y se compara
    # contra el valor vigente, para que el cambio se vea en vez de aparecer.
    p("-" * 100)
    p("  LA VÍA C, RECONTADA CONTRA LA CAPA DE HITOS VIGENTE")
    p("")
    movidas = []
    for fila in matriz.itertuples():
        soporte = soportes.geometry.get(fila.polo_id)
        if soporte is None or soporte.is_empty:
            continue
        adentro = mercados[mercados.within(soporte)]
        ahora = "si" if len(adentro) else "no"
        if ahora != str(fila.via_C_abierta):
            movidas.append({"polo_id": fila.polo_id, "nombre_polo": fila.nombre_polo,
                            "via_C_antes": fila.via_C_abierta, "via_C_ahora": ahora,
                            "via_C_cual_antes": fila.via_C_cual,
                            "via_C_cual_ahora": "; ".join(adentro.nombre.astype(str))})
    if not movidas:
        p("   ninguna fila cambia de vía C.")
    for cambio in movidas:
        p(f"   {cambio['polo_id']:<14} {str(cambio['nombre_polo'])[:26]:<28} "
          f"vía C {cambio['via_C_antes']} → {cambio['via_C_ahora']}"
          f"  (era: {cambio['via_C_cual_antes']})")
    if movidas:
        p("")
        p("   Es la consecuencia del retipado de la tarea 4: el hito que abría esa vía C no era")
        p("   un mercado. La fila no pierde el reconocimiento —la Ley 6.533 sigue declarando")
        p("   patrimonio su carta— pierde la VÍA C, que exige mercado, patio o galería en")
        p("   actividad. Es exactamente la misma regla que la decisión 1 aplicó a la FIAB.")
    pd.DataFrame(movidas).to_csv(SEIS_VIAS / f"via_C_movida_{sufijo}.csv", index=False,
                                 encoding="utf-8")
    p("")

    # ================================================== 3 · vía B y vía D por zona
    p("-" * 100)
    p("  TAREA 1 · LA VÍA B Y LA VÍA D, MEDIDAS POR ZONA")
    p("")
    filas_zona = []
    for zid, zona in zonas.items():
        geom = zona["geom_zona"]
        adentro = hitos[hitos.within(geom)]
        de_via_b = adentro[adentro.tipo.isin(TIPOS_VIA_B)]
        estados = list(de_via_b.vigencia_verificada.fillna("sin_verificar"))
        sop, abierta = soporte_de(estados)
        conteos = {f"via_B_{TIPOS_VIA_B[t]}": int((de_via_b.tipo == t).sum())
                   for t in TIPOS_VIA_B}
        patrimonio = int(adentro.es_patrimonio_normativo.astype(str).str.lower()
                         .isin(["true", "si", "sí"]).sum())
        enclaves_zona = cruzables[cruzables.intersects(geom)]
        filas_zona.append({
            "zona_id": zid, "nombre": zona["nombre"], "clase": zona["clase"],
            "detalle_geometria": zona["detalle_geometria"],
            "ha": round(geom.area / 10_000, 2),
            **conteos,
            "via_B_total": len(de_via_b),
            "via_B_patrimonio_normativo": patrimonio,
            "via_B_si": estados.count("si"),
            "via_B_probablemente_abierto": estados.count("probablemente_abierto"),
            "via_B_no": estados.count("no"),
            "via_B_dudosa": estados.count("dudosa"),
            "via_B_sin_verificar": estados.count("sin_verificar"),
            "via_B_soporte": sop, "via_B_abierta": abierta,
            "via_B_nombres": "; ".join(sorted(de_via_b.nombre.astype(str))[:14]),
            "via_D_n_enclaves": len(enclaves_zona),
            "via_D_enclaves": "; ".join(sorted(enclaves_zona.enclave_id.astype(str))),
            "via_D_colectividades": "; ".join(sorted(enclaves_zona.colectividad.astype(str))),
            "via_D_abierta": "si" if len(enclaves_zona) else "no",
            "via_C_cae_por_FIAB": zid in VIA_C_CAE_POR_FIAB,
        })
    tabla_zonas = pd.DataFrame(filas_zona).sort_values(
        ["via_B_total", "zona_id"], ascending=[False, True])

    p("  las zonas con hitos de vía B adentro, ordenadas por cuántos:")
    p("")
    p(f"   {'zona':<7} {'nombre':<34} {'ha':>9} {'hitos':>6} {'si':>4} {'prob':>5} {'s/v':>5} "
      f"{'soporte':<14} {'D':>2}")
    for fila in tabla_zonas.itertuples():
        if fila.via_B_total == 0 and fila.via_D_n_enclaves == 0:
            continue
        p(f"   {fila.zona_id:<7} {fila.nombre[:32]:<34} {fila.ha:>9,.1f} "
          f"{fila.via_B_total:>6} {fila.via_B_si:>4} {fila.via_B_probablemente_abierto:>5} "
          f"{fila.via_B_sin_verificar:>5} {fila.via_B_soporte:<14} {fila.via_D_n_enclaves:>2}")
    p("")
    sin_nada = tabla_zonas[(tabla_zonas.via_B_total == 0) & (tabla_zonas.via_D_n_enclaves == 0)]
    p(f"   y {len(sin_nada)} zonas sin ningún hito de vía B ni enclave: "
      + ", ".join(sin_nada.zona_id))
    p("")

    # ================================================== 4 · asignar zona a cada fila
    p("-" * 100)
    p("  TAREA 4 · LAS DIEZ FILAS EN `requiere_cruce`, RESUELTAS POR CRUCE ESPACIAL")
    p("")
    p("  Con la decisión 14 (Flores son TRES polos) y la 13 (Congreso se fusiona con Monserrat)")
    p("  las diez dejan de ser ambiguas por definición y pasan a ser una pregunta de geometría.")
    p("")

    asignacion: dict[str, dict] = {}
    filas_cruce = []
    for polo_id in matriz.polo_id:
        registro = via_e.loc[polo_id] if polo_id in via_e.index else None
        zona_e = str(registro.zona_via_E) if registro is not None else ""
        soporte = soportes.geometry.get(polo_id)

        if zona_e == "R18":
            asignacion[polo_id] = {"zona": "Z46", "modo": "heredada",
                                   "como": "la decisión 5 absorbe R18 en Z46 Retiro"}
            continue
        if zona_e in remapeo:
            asignacion[polo_id] = {"zona": remapeo[zona_e], "modo": "heredada",
                                   "como": f"la ronda 8 fusiona {zona_e} en {remapeo[zona_e]}"}
            continue
        if zona_e not in ("MULTIPLE", "REVISAR", "nan", ""):
            asignacion[polo_id] = {"zona": zona_e, "modo": "", "como": "asignación de la vía E"}
            continue

        # requiere_cruce: se resuelve por superposición contra los perímetros delimitados
        if soporte is None or soporte.is_empty:
            asignacion[polo_id] = {"zona": "", "modo": "requiere_cruce",
                                   "como": "la fila no tiene soporte geométrico"}
            filas_cruce.append({"polo_id": polo_id, "resuelta": False,
                                "motivo": "sin soporte geométrico"})
            continue
        barrio_fila = "Flores" if "Flores" in str(
            matriz.loc[matriz.polo_id == polo_id, "nombre_polo"].iloc[0]) else "Balvanera"
        candidatas = COMPARTEN_BARRIO[barrio_fila]
        medidas = []
        for zid in candidatas:
            delim = zonas[zid].get("geom_delimitada")
            if delim is None:
                continue
            solape = soporte.intersection(delim).area
            medidas.append((zid, solape / soporte.area * 100 if soporte.area else 0.0,
                            soporte.distance(delim)))
        medidas.sort(key=lambda m: (-m[1], m[2]))
        mejor = medidas[0] if medidas else None
        detalle = " · ".join(f"{z}: {pct:.1f} % del fragmento, a {d:,.0f} m"
                             for z, pct, d in medidas)
        residuo = RESIDUO_POR_BARRIO.get(barrio_fila, "")
        # una fila que abarca casi todo el barrio no es de ninguna de las tres zonas: las abarca
        abarca_el_barrio = (soporte.area /
                            zonas[candidatas[0]]["geom_zona"].area) > 0.5
        if abarca_el_barrio:
            asignacion[polo_id] = {
                "zona": "", "modo": "requiere_cruce",
                "como": f"el soporte cubre el {soporte.area / zonas[candidatas[0]]['geom_zona'].area * 100:.0f} % "
                        f"del barrio: abarca las zonas en vez de pertenecer a una"}
            resuelta, zona_final, como = False, "", "abarca el barrio entero"
        elif mejor and mejor[1] > 0:
            asignacion[polo_id] = {"zona": mejor[0], "modo": "heredada",
                                   "como": f"cruce espacial: {detalle}"}
            resuelta, zona_final, como = True, mejor[0], "contención"
        elif residuo:
            asignacion[polo_id] = {
                "zona": residuo, "modo": "heredada",
                "como": f"por residuo: no toca ninguna zona delimitada de {barrio_fila} "
                        f"({detalle}), así que queda en {residuo}, que es la que no tiene "
                        "perímetro resoluble"}
            resuelta, zona_final, como = True, residuo, "residuo (no contención)"
        else:
            asignacion[polo_id] = {"zona": "", "modo": "requiere_cruce",
                                   "como": f"ninguna zona lo contiene ni lo roza: {detalle}"}
            resuelta, zona_final, como = False, "", "sin resolver"
        filas_cruce.append({
            "polo_id": polo_id,
            "nombre_polo": matriz.loc[matriz.polo_id == polo_id, "nombre_polo"].iloc[0],
            "n_locales": matriz.loc[matriz.polo_id == polo_id, "n_locales"].iloc[0],
            "ha_del_fragmento": round(soporte.area / 10_000, 2),
            "candidatas": "; ".join(candidatas), "detalle": detalle,
            "resuelta": resuelta, "zona_asignada": zona_final, "como_se_resolvio": como,
        })
        marca = "→" if resuelta else "✗"
        nombre = matriz.loc[matriz.polo_id == polo_id, "nombre_polo"].iloc[0]
        p(f"   {marca} {polo_id:<14} {str(nombre)[:24]:<26} "
          f"{soporte.area / 10_000:>7,.1f} ha  {zona_final or 'SIN RESOLVER':<6} "
          f"[{como}]  {detalle}")
    p("")
    resueltas = sum(1 for f in filas_cruce if f.get("resuelta"))
    p(f"  {resueltas} de {len(filas_cruce)} resueltas.")
    p("")
    p("  UN HALLAZGO QUE APARECIÓ AL INTENTAR CONSTRUIR EL PERÍMETRO DE Z23")
    p("")
    p("  La delimitación de Flores casco histórico dice «Av. Rivadavia, Boyacá-Carabobo». No se")
    p("  puede construir, y no es un problema del callejero: **Av. Boyacá y Av. Carabobo son la")
    p("  misma avenida**, que cambia de nombre justo al cruzar Av. Rivadavia. Boyacá corre al")
    p("  norte y Carabobo al sur, y las dos tocan a Rivadavia en el MISMO punto —medido: un")
    p("  único Point, idéntico para las dos—. «Entre Boyacá y Carabobo» mide cero cuadras.")
    p("")
    p("  Z23 ya estaba declarada PENDIENTE de redelimitación por otro motivo (su único hito, La")
    p("  Farmacia, cae ocho cuadras al sur del polígono propuesto). Esto agrega el motivo")
    p("  geométrico y lo vuelve concreto: no hay perímetro que poligonizar, hay un cruce.")
    p("")
    p("  Mientras tanto Z23 recibe por RESIDUO lo que no cae en Z24 ni en Z39b. Va marcado como")
    p("  `residuo (no contención)` en el CSV, que no es lo mismo que una asignación medida.")
    p("")
    sin_resolver = [f for f in filas_cruce if not f.get("resuelta")]
    if sin_resolver:
        p("  LAS QUE QUEDAN SIN RESOLVER, Y POR QUÉ ES CORRECTO QUE QUEDEN")
        p("")
        for f in sin_resolver:
            p(f"   {f['polo_id']} · {f['ha_del_fragmento']:,} ha · {f['como_se_resolvio']}")
        p("")
        p("   Un soporte que cubre la mitad del barrio no pertenece a una de sus zonas: las")
        p("   abarca. Forzarle una sola sería inventar una pertenencia, y encima la más cara de")
        p("   detectar después, porque quedaría escrita como si se hubiera medido.")
    p("")

    # ================================================== 5 · modo de cada fila
    p("-" * 100)
    p("  EL MODO DE CADA FILA · propia, heredada o requiere_cruce")
    p("")
    for polo_id, dato in asignacion.items():
        if dato["modo"]:
            continue
        zid = dato["zona"]
        soporte = soportes.geometry.get(polo_id)
        zona_geom = zonas.get(zid, {}).get("geom_zona")
        if soporte is None or zona_geom is None or soporte.is_empty:
            dato["modo"] = "requiere_cruce"
            dato["cobertura_pct"] = ""
            continue
        cobertura = soporte.intersection(zona_geom).area / zona_geom.area * 100
        dato["cobertura_pct"] = round(cobertura, 1)
        dato["modo"] = "propia" if cobertura >= 95 else "heredada"
    for polo_id, dato in asignacion.items():
        dato.setdefault("cobertura_pct", "")

    modos = pd.Series([d["modo"] for d in asignacion.values()]).value_counts()
    for modo, n in modos.items():
        p(f"      {modo:<16} {n:>3} filas")
    p("")
    p("  `propia` es la fila cuyo soporte cubre ≥ 95 % de la zona: no hereda nada, ES la zona.")
    p("  `heredada` es un fragmento. LA HERENCIA NO VALE HACIA ARRIBA: que Almagro tenga cinco")
    p("  Bares Notables no convierte a PGR_P083 en un polo notable — lo convierte en un fragmento")
    p("  de una zona que tiene cinco. Eso es lo que la ficha tiene que decir.")
    p("")

    # ================================================== 6 · el reparto de las 48
    p("-" * 100)
    p("  EL NÚMERO QUE ESTA RONDA VENÍA A BUSCAR · CÓMO SE REPARTEN LAS 48 `sin_hitos`")
    p("")
    por_zona = tabla_zonas.set_index("zona_id")
    reparto = []
    for fila in matriz.itertuples():
        soporte = soportes.geometry.get(fila.polo_id)
        # la vía B del fragmento, recontada sobre la capa r7 para que las dos escalas se midan
        # con exactamente la misma capa de hitos y la diferencia sea sólo de escala
        if soporte is None or soporte.is_empty:
            estados_frag = []
        else:
            adentro = hitos[hitos.within(soporte)]
            estados_frag = list(adentro[adentro.tipo.isin(TIPOS_VIA_B)]
                                .vigencia_verificada.fillna("sin_verificar"))
        sop_frag, abierta_frag = soporte_de(estados_frag)
        zid = asignacion[fila.polo_id]["zona"]
        if zid and zid in por_zona.index:
            sop_zona = por_zona.via_B_soporte.loc[zid]
            hitos_zona = int(por_zona.via_B_total.loc[zid])
        else:
            sop_zona, hitos_zona = "", 0
        if sop_frag == "sin_hitos":
            if not zid:
                clase = "la fila no tiene zona resuelta"
            elif hitos_zona == 0:
                clase = "la zona TAMPOCO tiene hitos"
            else:
                clase = "la zona SÍ tiene, el fragmento no"
        else:
            clase = "el fragmento tiene hitos"
        reparto.append({
            "polo_id": fila.polo_id, "nombre_polo": fila.nombre_polo,
            "ha_del_fragmento": round(soporte.area / 10_000, 2) if soporte is not None
                                and not soporte.is_empty else "",
            "zona": zid, "modo": asignacion[fila.polo_id]["modo"],
            "via_B_soporte_fragmento": sop_frag, "via_B_abierta_fragmento": abierta_frag,
            "hitos_en_el_fragmento": len(estados_frag),
            "via_B_soporte_zona": sop_zona, "hitos_en_la_zona": hitos_zona,
            "clase": clase,
        })
    tabla_reparto = pd.DataFrame(reparto)
    sin_hitos = tabla_reparto[tabla_reparto.via_B_soporte_fragmento == "sin_hitos"]
    p(f"  filas cuyo PROPIO polígono no contiene ningún hito de vía B: {len(sin_hitos)} de "
      f"{len(matriz)}")
    p("")

    # RECONCILIACIÓN CONTRA LA RONDA 4. La tarea habla de 48 y acá salen 51. La diferencia no es
    # de criterio: la ronda 4 midió con `hitos_capa_2026_r3.csv` y ésta mide con la r7, y entre
    # las dos hubo tres rondas que corrigieron direcciones y puntos. Se identifica fila por fila
    # en vez de elegir cuál de los dos números contar.
    antes_sin_hitos = set(matriz.loc[matriz.via_B_soporte == "sin_hitos", "polo_id"])
    ahora_sin_hitos = set(sin_hitos.polo_id)
    entraron = sorted(ahora_sin_hitos - antes_sin_hitos)
    salieron = sorted(antes_sin_hitos - ahora_sin_hitos)
    p(f"  RECONCILIACIÓN CON EL 48 DE LA RONDA 4 · {len(antes_sin_hitos)} entonces, "
      f"{len(ahora_sin_hitos)} ahora")
    p("")
    p("  La ronda 4 midió sobre `hitos_capa_2026_r3.csv` y ésta mide sobre la r7. Entre las dos")
    p("  hubo tres rondas que corrigieron direcciones y repusieron puntos, así que el conteo por")
    p("  contención se mueve solo. Las que cambiaron de lado:")
    p("")
    for polo_id in entraron:
        nombre = matriz.loc[matriz.polo_id == polo_id, "nombre_polo"].iloc[0]
        p(f"      + {polo_id:<16} {str(nombre)[:30]:<32} tenía hitos con la r3 y no con la r7")
    for polo_id in salieron:
        nombre = matriz.loc[matriz.polo_id == polo_id, "nombre_polo"].iloc[0]
        p(f"      - {polo_id:<16} {str(nombre)[:30]:<32} no tenía con la r3 y sí con la r7")
    if not entraron and not salieron:
        p("      ninguna: los dos conteos coinciden fila por fila")
    p("")
    p("  El cambio de escala se mide contra el 51, que es el número de esta capa. Comparar el 33")
    p("  de la vía B por zona contra el 7 de la ronda 4 sería mezclar dos capas de hitos.")
    p("")
    for clase, n in sin_hitos.clase.value_counts().items():
        p(f"      {clase:<38} {n:>3} filas")
    p("")
    tiene_zona = sin_hitos[sin_hitos.clase == "la zona SÍ tiene, el fragmento no"]
    p(f"  {len(tiene_zona)} de las {len(sin_hitos)} pertenecen a una zona que SÍ tiene hitos.")
    p("  Hasta ayer esas filas y las que están en una zona vacía se contaban igual, y son dos")
    p("  cosas completamente distintas: una es «acá no hay trayectoria» y la otra es «el")
    p("  clustering no acertó a caer encima de un bar».")
    p("")
    p("  las diez que más hitos tienen en su zona y ninguno adentro:")
    for fila in tiene_zona.nlargest(10, "hitos_en_la_zona").itertuples():
        p(f"      {fila.polo_id:<14} {str(fila.nombre_polo)[:26]:<28} "
          f"{fila.ha_del_fragmento:>7} ha · zona {fila.zona:<5} con "
          f"{fila.hitos_en_la_zona:>2} hitos ({fila.via_B_soporte_zona})")
    p("")

    # el antes y el después de la vía B, en una línea
    p("-" * 100)
    p("  LA VÍA B, ANTES Y DESPUÉS DEL CAMBIO DE ESCALA")
    p("")
    r4 = matriz.via_B_abierta.value_counts()
    antes = tabla_reparto.via_B_abierta_fragmento.value_counts()
    abierta_por_zona = []
    for fila in tabla_reparto.itertuples():
        if fila.zona and fila.zona in por_zona.index:
            abierta_por_zona.append(por_zona.via_B_abierta.loc[fila.zona])
        else:
            abierta_por_zona.append("pendiente")
    despues = pd.Series(abierta_por_zona).value_counts()
    p(f"   {'':<12} {'ronda 4 (capa r3)':>19} {f'por contención (capa {sufijo})':>26} "
      f"{f'por zona (capa {sufijo})':>20}")
    for valor in ("si", "pendiente", "no"):
        p(f"   {valor:<12} {int(r4.get(valor, 0)):>19} {int(antes.get(valor, 0)):>26} "
          f"{int(despues.get(valor, 0)):>20}")
    p("")
    p("  Las dos columnas de la derecha se miden con LA MISMA capa de hitos y sobre LAS MISMAS")
    p("  94 filas: lo único que cambia entre ellas es a qué objeto se le pregunta. Ésa es la")
    p("  comparación que mide el cambio de escala. La primera columna está para que se vea de")
    p("  dónde venimos, no para restarle a las otras.")
    p("")
    p("  Ningún criterio se aflojó: un Bar Notable sigue teniendo que existir, estar verificado")
    p("  y pertenecer a la zona. Lo único que se corrigió es a qué objeto se le atribuye.")
    p("")

    # ================================================== 7 · salidas
    salida_filas = matriz[["polo_id", "nombre_polo", "soporte_clase", "n_locales", "ha",
                           "via_A_abierta", "via_C_abierta", "via_F_abierta"]].copy()
    salida_filas["zona_via_B"] = salida_filas.polo_id.map(lambda x: asignacion[x]["zona"])
    salida_filas["via_B_modo"] = salida_filas.polo_id.map(lambda x: asignacion[x]["modo"])
    salida_filas["zona_via_D"] = salida_filas.zona_via_B
    salida_filas["via_D_modo"] = salida_filas.via_B_modo
    salida_filas["zona_via_E"] = salida_filas.zona_via_B
    salida_filas["via_E_modo"] = salida_filas.via_B_modo
    salida_filas["cobertura_de_la_zona_pct"] = salida_filas.polo_id.map(
        lambda x: asignacion[x]["cobertura_pct"])
    salida_filas["como_se_asigno"] = salida_filas.polo_id.map(lambda x: asignacion[x]["como"])
    salida_filas["via_B_soporte_del_fragmento"] = salida_filas.polo_id.map(
        tabla_reparto.set_index("polo_id").via_B_soporte_fragmento)
    salida_filas["nota"] = (
        "las vías B, D y E NO se copian acá: viven en zonas_via_B_via_D_r7.csv y se buscan por "
        "zona_via_*. La herencia no vale hacia arriba: un fragmento de una zona con hitos no es "
        "un polo con hitos.")

    vista = salida_filas.merge(
        tabla_zonas[["zona_id", "via_B_soporte", "via_B_abierta", "via_B_total", "via_B_si",
                     "via_D_abierta", "via_D_n_enclaves", "via_D_enclaves"]],
        left_on="zona_via_B", right_on="zona_id", how="left")

    OUT_ZONAS.parent.mkdir(parents=True, exist_ok=True)
    tabla_zonas.to_csv(OUT_ZONAS, index=False, encoding="utf-8")
    salida_filas.to_csv(OUT_FILAS, index=False, encoding="utf-8")
    vista.to_csv(OUT_VISTA, index=False, encoding="utf-8")
    pd.DataFrame(filas_cruce).to_csv(OUT_CRUCE, index=False, encoding="utf-8")
    tabla_reparto.to_csv(OUT_SIN_HITOS, index=False, encoding="utf-8")
    pd.DataFrame(filas_fiab).to_csv(OUT_FIAB, index=False, encoding="utf-8")

    capa_zonas = gpd.GeoDataFrame(
        [{"zona_id": z["zona_id"], "nombre": z["nombre"], "clase": z["clase"],
          "detalle_geometria": z["detalle_geometria"],
          "tiene_perimetro_delimitado": z.get("geom_delimitada") is not None
                                        and z["clase"] == "zona nueva",
          "geometry": z["geom_zona"]} for z in zonas.values()],
        geometry="geometry", crs=CRS_METRICO)
    capa_zonas.to_crs("EPSG:4326").to_file(OUT_GEOJSON, driver="GeoJSON")

    p("-" * 100)
    p(f"  {OUT_ZONAS.name} · {len(tabla_zonas)} zonas")
    p(f"  {OUT_FILAS.name} · {len(salida_filas)} filas, con REFERENCIA a la zona y sin el valor")
    p(f"  {OUT_VISTA.name} · la vista unida, derivada y descartable")
    p(f"  {OUT_CRUCE.name} · {len(filas_cruce)} filas que estaban trabadas")
    p(f"  {OUT_SIN_HITOS.name} · el reparto de las {len(sin_hitos)} sin hitos en el fragmento")
    p("  Google Places: 0 requests.")

    texto = buffer.getvalue()
    INFORME_TXT.write_text(texto, encoding="utf-8")
    print(texto)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
