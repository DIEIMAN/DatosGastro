"""Build PolosGastro phase 16 editorial subzone maps and PDF V4.

Uses the already downloaded GCBA street GeoJSON from phase 15 as visual
context. It does not call APIs, does not touch source data, and writes only
phase 16 docs/outputs plus a versioned script.
"""
from __future__ import annotations

import csv
import importlib.util
import json
import math
import sys
import textwrap
from collections import Counter
from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "none"
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Ellipse, Polygon as MplPolygon  # noqa: E402
from reportlab.lib.pagesizes import A4  # noqa: E402
from reportlab.pdfgen import canvas  # noqa: E402


ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs" / "polos_gastro" / "fase16_mapas_editoriales_v4"
OUT = ROOT / "outputs" / "polos_gastro" / "fase16_mapas_editoriales_v4"
ASSETS = OUT / "assets"
TABLES = OUT / "tablas"

PHASE15_DOCS = ROOT / "docs" / "polos_gastro" / "fase15_mapas_callejeros_v3"
PHASE15_OUT = ROOT / "outputs" / "polos_gastro" / "fase15_mapas_callejeros_v3"

CALLEJERO = PHASE15_OUT / "assets" / "callejero_gcba_2026_06_02.geojson"
BARRIOS = ROOT / "data" / "raw" / "geo_barrios.geojson"

SUBZONAS_CSV = TABLES / "subzonas_editoriales_polos.csv"
SUBZONAS_GEOJSON = TABLES / "subzonas_editoriales_geometrias.geojson"
MD_BASE_V4 = DOCS / "INFORME_POLOS_GASTRO_DGDGAS_PDF_BASE_V4.md"
PDF_V4 = OUT / "INFORME_POLOS_GASTRO_DGDGAS_PRELIMINAR_V4.pdf"
QA_V4 = DOCS / "QA_PDF_V4_POLOS_GASTRO_DGDGAS.md"
CAMBIOS_V4 = DOCS / "CAMBIOS_V3_A_V4_POLOS_GASTRO.md"

SOURCE_V15_SCRIPT = ROOT / "scripts" / "polos_gastro" / "build_fase15_mapas_callejeros_v3.py"
spec = importlib.util.spec_from_file_location("fase15_v3", SOURCE_V15_SCRIPT)
v15 = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules["fase15_v3"] = v15
spec.loader.exec_module(v15)
v2 = v15.v2


INSTITUCION = "DGDGAS — Dirección General de Desarrollo Gastronómico"
GOBIERNO = "Gobierno de la Ciudad de Buenos Aires"
TITLE = "Polos gastronómicos de la Ciudad de Buenos Aires"
SUBTITLE = "Universo semilla, lectura territorial y subzonas de trabajo"

AZUL = "#1F3B57"
CELESTE = "#2C6E9E"
VERDE = "#1A9850"
NARANJA = "#C0762B"
ROJO = "#C0392B"
VIOLETA = "#7A5C99"
GRIS = "#555555"
LINEA = "#D9DEE5"
SOFT_AZUL = "#EAF1F8"
SOFT_VERDE = "#EAF5EE"
SOFT_NARANJA = "#F8EDE0"

W, H = A4
M = 44
DETAIL_ORDER = ["palermo", "puerto", "san_telmo", "corrientes", "belgrano"]

MAP_OUTPUTS = {
    "palermo": "mapa_v4_palermo_las_canitas_editorial",
    "puerto": "mapa_v4_puerto_madero_editorial",
    "san_telmo": "mapa_v4_san_telmo_editorial",
    "corrientes": "mapa_v4_corrientes_abasto_editorial",
    "belgrano": "mapa_v4_belgrano_subzonas_editorial",
}

MAP_CFG = {
    "palermo": {
        "title": "Palermo / Las Cañitas",
        "bbox": (-58.446, -34.596, -58.404, -34.560),
        "major": ["SANTA FE", "CORDOBA", "JUAN B. JUSTO", "SCALABRINI", "DORREGO", "DEL LIBERTADOR", "LUIS MARIA CAMPOS", "SARMIENTO"],
        "street_labels": [
            (-58.426, -34.579, "Av. Santa Fe"),
            (-58.428, -34.591, "Av. Córdoba"),
            (-58.438, -34.586, "Juan B. Justo"),
            (-58.435, -34.567, "Luis M. Campos"),
        ],
    },
    "puerto": {
        "title": "Puerto Madero",
        "bbox": (-58.392, -34.632, -58.354, -34.584),
        "water": True,
        "major": ["ALICIA MOREAU", "JUANA MANSO", "HUERGO", "MADERO", "ROSARIO VERA", "MACACHA GUEMES", "CORDOBA"],
        "street_labels": [
            (-58.371, -34.604, "A. Moreau de Justo"),
            (-58.364, -34.611, "Juana Manso"),
            (-58.382, -34.610, "Huergo / Madero"),
            (-58.364, -34.619, "Rosario Vera Peñaloza"),
        ],
    },
    "san_telmo": {
        "title": "San Telmo",
        "bbox": (-58.381, -34.631, -58.365, -34.615),
        "major": ["DEFENSA", "BOLIVAR", "CHILE", "ESTADOS UNIDOS", "CARLOS CALVO", "HUMBERTO", "SAN JUAN", "PASEO COLON"],
        "street_labels": [
            (-58.373, -34.622, "Defensa"),
            (-58.371, -34.628, "Av. San Juan"),
            (-58.377, -34.620, "Chile"),
            (-58.367, -34.624, "Paseo Colón"),
        ],
    },
    "corrientes": {
        "title": "Corrientes / Abasto",
        "bbox": (-58.418, -34.611, -58.374, -34.596),
        "major": ["CORRIENTES", "CALLAO", "9 DE JULIO", "URUGUAY", "PARANA", "RIOBAMBA", "PASTEUR", "PUEYRREDON", "ANCHORENA"],
        "street_labels": [
            (-58.389, -34.602, "Av. Corrientes"),
            (-58.392, -34.606, "Callao"),
            (-58.381, -34.606, "9 de Julio"),
            (-58.410, -34.600, "Abasto"),
        ],
    },
    "belgrano": {
        "title": "Belgrano",
        "bbox": (-58.467, -34.568, -58.436, -34.548),
        "major": ["JURAMENTO", "MENDOZA", "OLAZABAL", "ARRIBENOS", "MONTAÑESES", "DEL LIBERTADOR", "CABILDO", "LA PAMPA", "MIGUELETES"],
        "street_labels": [
            (-58.451, -34.556, "Juramento"),
            (-58.454, -34.559, "Mendoza"),
            (-58.441, -34.559, "Del Libertador"),
            (-58.458, -34.565, "Cabildo"),
        ],
    },
}


SUBZONES = [
    {"mapa": "Palermo / Las Cañitas", "key": "palermo", "subzona": "Palermo Soho", "tipo_geometria": "elipse aproximada", "center": (-58.4235, -34.5880), "width": 0.0155, "height": 0.0120, "angle": -15, "criterio_geografico": "Área de lectura entre Santa Fe, Córdoba, Scalabrini Ortiz y Juan B. Justo, ajustada editorialmente.", "etiqueta_visible": "PALERMO SOHO", "label_pos": (-58.4235, -34.5913), "label_width": 14, "color_sugerido": CELESTE, "mostrar_en_mapa": "si", "observacion": "Subzona de trabajo; no límite oficial."},
    {"mapa": "Palermo / Las Cañitas", "key": "palermo", "subzona": "Palermo Hollywood", "tipo_geometria": "elipse aproximada", "center": (-58.4350, -34.5850), "width": 0.0165, "height": 0.0115, "angle": -10, "criterio_geografico": "Área de lectura al noroeste de Juan B. Justo, con apoyo en trama callejera y menciones del universo semilla.", "etiqueta_visible": "PALERMO HOLLYWOOD", "label_pos": (-58.4362, -34.5841), "label_width": 13, "color_sugerido": VERDE, "mostrar_en_mapa": "si", "observacion": "Subzona de trabajo; no límite oficial."},
    {"mapa": "Palermo / Las Cañitas", "key": "palermo", "subzona": "Las Cañitas", "tipo_geometria": "elipse aproximada", "center": (-58.4340, -34.5690), "width": 0.0155, "height": 0.0090, "angle": -8, "criterio_geografico": "Entorno de Luis María Campos y Libertador como referencia visual de Las Cañitas.", "etiqueta_visible": "LAS CAÑITAS", "label_pos": (-58.4347, -34.5684), "label_width": 14, "color_sugerido": NARANJA, "mostrar_en_mapa": "si", "observacion": "Subzona de trabajo; no límite oficial."},
    {"mapa": "Palermo / Las Cañitas", "key": "palermo", "subzona": "Palermo Chico", "tipo_geometria": "elipse aproximada", "center": (-58.4105, -34.5785), "width": 0.0120, "height": 0.0100, "angle": -18, "criterio_geografico": "Área contextual al este, incorporada para ordenar la lectura del mapa.", "etiqueta_visible": "PALERMO CHICO", "mostrar_etiqueta": "no", "color_sugerido": VIOLETA, "mostrar_en_mapa": "si", "observacion": "Contexto visual; no se usa para validar menciones."},
    {"mapa": "Palermo / Las Cañitas", "key": "palermo", "subzona": "Palermo Nuevo / Botánico", "tipo_geometria": "elipse aproximada", "center": (-58.4160, -34.5835), "width": 0.0140, "height": 0.0110, "angle": -12, "criterio_geografico": "Área contextual entre Botánico, Santa Fe y Libertador para dar escala territorial.", "etiqueta_visible": "PALERMO NUEVO / BOTÁNICO", "mostrar_etiqueta": "no", "color_sugerido": ROJO, "mostrar_en_mapa": "si", "observacion": "Contexto visual; no se presenta como polo consolidado."},
    {"mapa": "Puerto Madero", "key": "puerto", "subzona": "Docks / eje costero", "tipo_geometria": "polígono aproximado", "polygon": [(-58.3685, -34.5910), (-58.3598, -34.5910), (-58.3585, -34.6265), (-58.3665, -34.6270), (-58.3705, -34.6100)], "criterio_geografico": "Banda longitudinal de docks y frente costero, armada con callejero y referencias del barrio.", "etiqueta_visible": "DOCKS", "label_pos": (-58.3662, -34.6108), "label_width": 10, "color_sugerido": CELESTE, "mostrar_en_mapa": "si", "observacion": "Área aproximada de lectura; no límite oficial."},
    {"mapa": "Puerto Madero", "key": "puerto", "subzona": "Área Faena / El Mercado", "tipo_geometria": "elipse aproximada", "center": (-58.3638, -34.6175), "width": 0.0100, "height": 0.0080, "angle": -5, "criterio_geografico": "Entorno sur del corredor de docks, apoyado en menciones destacadas y calles visibles.", "etiqueta_visible": "FAENA / EL MERCADO", "label_pos": (-58.3665, -34.6212), "leader_line": "si", "label_width": 12, "color_sugerido": VERDE, "mostrar_en_mapa": "si", "observacion": "Subzona de trabajo; no límite oficial."},
    {"mapa": "Puerto Madero", "key": "puerto", "subzona": "Sector gastronómico costero", "tipo_geometria": "elipse aproximada", "center": (-58.3605, -34.6070), "width": 0.0120, "height": 0.0200, "angle": 2, "criterio_geografico": "Corredor costero con concentración de referencias gastronómicas del universo semilla.", "etiqueta_visible": "SECTOR COSTERO", "label_pos": (-58.3634, -34.6018), "leader_line": "si", "label_width": 12, "color_sugerido": NARANJA, "mostrar_en_mapa": "si", "observacion": "Área aproximada de lectura."},
    {"mapa": "Puerto Madero", "key": "puerto", "subzona": "Área a validar", "tipo_geometria": "elipse aproximada", "center": (-58.3738, -34.6040), "width": 0.0110, "height": 0.0120, "angle": -12, "criterio_geografico": "Sector oeste donde algunas sedes requieren validación antes de lectura operativa.", "etiqueta_visible": "ÁREA A VALIDAR", "label_pos": (-58.3762, -34.6038), "label_width": 12, "color_sugerido": VIOLETA, "mostrar_en_mapa": "si", "observacion": "No presentar como actividad confirmada."},
    {"mapa": "San Telmo", "key": "san_telmo", "subzona": "Entorno Mercado de San Telmo", "tipo_geometria": "elipse aproximada", "center": (-58.3730, -34.6220), "width": 0.0075, "height": 0.0060, "angle": 0, "criterio_geografico": "Radio visual alrededor del Mercado de San Telmo y calles cercanas.", "etiqueta_visible": "ENTORNO MERCADO", "mostrar_etiqueta": "no", "color_sugerido": CELESTE, "mostrar_en_mapa": "si", "observacion": "Hito colectivo tratado como referencia territorial."},
    {"mapa": "San Telmo", "key": "san_telmo", "subzona": "Casco histórico / Defensa", "tipo_geometria": "elipse aproximada", "center": (-58.3716, -34.6255), "width": 0.0080, "height": 0.0105, "angle": -10, "criterio_geografico": "Eje Defensa/Bolívar y entorno patrimonial del casco.", "etiqueta_visible": "CASCO HISTÓRICO / DEFENSA", "label_pos": (-58.3704, -34.6266), "label_width": 13, "color_sugerido": VERDE, "mostrar_en_mapa": "si", "observacion": "Área aproximada de lectura; no límite oficial."},
    {"mapa": "San Telmo", "key": "san_telmo", "subzona": "Área gastronómica cercana", "tipo_geometria": "elipse aproximada", "center": (-58.3755, -34.6205), "width": 0.0075, "height": 0.0065, "angle": 8, "criterio_geografico": "Entorno cercano a Chile, Estados Unidos y Defensa con menciones del universo semilla.", "etiqueta_visible": "ÁREA GASTRONÓMICA", "label_pos": (-58.3760, -34.6194), "label_width": 13, "color_sugerido": NARANJA, "mostrar_en_mapa": "si", "observacion": "Subzona de trabajo."},
    {"mapa": "San Telmo", "key": "san_telmo", "subzona": "Hito colectivo Mercado de San Telmo", "tipo_geometria": "punto de referencia editorial", "center": (-58.3730, -34.6218), "width": 0.0026, "height": 0.0022, "angle": 0, "criterio_geografico": "Marcador editorial del hito colectivo Mercado de San Telmo.", "etiqueta_visible": "MERCADO", "label_pos": (-58.3706, -34.6211), "leader_line": "si", "label_width": 10, "color_sugerido": ROJO, "mostrar_en_mapa": "si", "observacion": "No representa restaurante puntual."},
    {"mapa": "Corrientes / Abasto", "key": "corrientes", "subzona": "Eje Corrientes 9 de Julio-Callao", "tipo_geometria": "eje aproximado", "line": [(-58.3925, -34.6043), (-58.3815, -34.6038)], "criterio_geografico": "Tramo de Av. Corrientes entre Callao y 9 de Julio.", "etiqueta_visible": "CORRIENTES 9 DE JULIO-CALLAO", "label_pos": (-58.3866, -34.6050), "label_width": 13, "color_sugerido": CELESTE, "mostrar_en_mapa": "si", "observacion": "Eje aproximado; no define polígono oficial."},
    {"mapa": "Corrientes / Abasto", "key": "corrientes", "subzona": "Área Obelisco / teatros", "tipo_geometria": "elipse aproximada", "center": (-58.3812, -34.6038), "width": 0.0105, "height": 0.0060, "angle": 0, "criterio_geografico": "Entorno de 9 de Julio, Obelisco y teatros como referencia de escala.", "etiqueta_visible": "OBELISCO / TEATROS", "label_pos": (-58.3796, -34.6034), "label_width": 11, "color_sugerido": VERDE, "mostrar_en_mapa": "si", "observacion": "Subzona contextual."},
    {"mapa": "Corrientes / Abasto", "key": "corrientes", "subzona": "Área Abasto radio aproximado cinco cuadras", "tipo_geometria": "elipse aproximada", "center": (-58.4105, -34.6040), "width": 0.0145, "height": 0.0100, "angle": -5, "criterio_geografico": "Radio visual aproximado de cinco cuadras alrededor del Abasto.", "etiqueta_visible": "ABASTO A REFORZAR", "label_pos": (-58.4110, -34.6035), "label_width": 12, "color_sugerido": NARANJA, "mostrar_en_mapa": "si", "observacion": "Área a reforzar; no se fusiona con Corrientes."},
    {"mapa": "Corrientes / Abasto", "key": "corrientes", "subzona": "Conexión Corrientes-Abasto", "tipo_geometria": "eje aproximado", "line": [(-58.3925, -34.6042), (-58.4105, -34.6040)], "criterio_geografico": "Conexión visual sobre el corredor Corrientes para mostrar vínculo, no equivalencia.", "etiqueta_visible": "EJES VINCULADOS", "mostrar_etiqueta": "no", "color_sugerido": VIOLETA, "mostrar_en_mapa": "si", "observacion": "No implica que sean el mismo polo."},
    {"mapa": "Belgrano", "key": "belgrano", "subzona": "Barrio Chino", "tipo_geometria": "elipse aproximada", "center": (-58.4518, -34.5550), "width": 0.0100, "height": 0.0068, "angle": -8, "criterio_geografico": "Entorno Juramento/Arribeños y referencias del Barrio Chino.", "etiqueta_visible": "BARRIO CHINO", "label_pos": (-58.4515, -34.5548), "label_width": 12, "color_sugerido": CELESTE, "mostrar_en_mapa": "si", "observacion": "Subzona con identidad gastronómica clara."},
    {"mapa": "Belgrano", "key": "belgrano", "subzona": "Bajo Belgrano", "tipo_geometria": "elipse aproximada", "center": (-58.4438, -34.5590), "width": 0.0105, "height": 0.0080, "angle": -5, "criterio_geografico": "Área de lectura hacia Libertador y Bajo Belgrano.", "etiqueta_visible": "BAJO BELGRANO", "label_pos": (-58.4435, -34.5592), "label_width": 12, "color_sugerido": VERDE, "mostrar_en_mapa": "si", "observacion": "Sedes a validar; no actividad confirmada."},
    {"mapa": "Belgrano", "key": "belgrano", "subzona": "Belgrano R", "tipo_geometria": "elipse aproximada", "center": (-58.4600, -34.5625), "width": 0.0110, "height": 0.0070, "angle": -10, "criterio_geografico": "Área aproximada al oeste de Cabildo para mostrar subzona a reforzar.", "etiqueta_visible": "BELGRANO R A REFORZAR", "label_pos": (-58.4605, -34.5627), "label_width": 12, "color_sugerido": NARANJA, "mostrar_en_mapa": "si", "observacion": "Subzona a reforzar; no polo consolidado."},
    {"mapa": "Belgrano", "key": "belgrano", "subzona": "Área Cabildo/Juramento", "tipo_geometria": "elipse aproximada", "center": (-58.4552, -34.5574), "width": 0.0090, "height": 0.0070, "angle": -7, "criterio_geografico": "Intersección y entorno usado como referencia urbana de escala.", "etiqueta_visible": "CABILDO / JURAMENTO", "mostrar_etiqueta": "no", "color_sugerido": VIOLETA, "mostrar_en_mapa": "si", "observacion": "Contexto visual."},
]

DETAIL_TEXT = {
    "palermo": {
        "page": 7,
        "title": "Palermo / Las Cañitas",
        "subtitle": "Subzonas coloreadas sobre callejero, con etiquetas grandes y puntos fuera del rol principal.",
        "reading": "La pieza diferencia Palermo Soho, Palermo Hollywood y Las Cañitas como áreas aproximadas. Palermo Chico y Palermo Nuevo/Botánico operan como contexto visual para orientar la lectura.",
        "caution": "Área aproximada de lectura territorial, no delimitación oficial. Las menciones destacadas se conservan en cajas y no funcionan como ranking.",
    },
    "puerto": {
        "page": 8,
        "title": "Puerto Madero",
        "subtitle": "Docks, eje costero y sectores a validar en clave editorial.",
        "reading": "El mapa prioriza la banda de docks y el frente costero como forma reconocible. Las áreas con sedes pendientes quedan diferenciadas sin presentarse como actividad confirmada.",
        "caution": "Zona de lectura, no delimitación oficial. Las sedes a validar requieren revisión antes de cualquier uso operativo.",
    },
    "san_telmo": {
        "page": 9,
        "title": "San Telmo",
        "subtitle": "Mercado, casco histórico y área gastronómica cercana como subzonas de trabajo.",
        "reading": "El Mercado de San Telmo se muestra como hito colectivo. Defensa y el casco histórico ordenan la lectura territorial sin convertir el mapa en padrón de locales.",
        "caution": "Subzonas de trabajo, no límites oficiales. Los hitos colectivos no equivalen a restaurantes puntuales.",
    },
    "corrientes": {
        "page": 10,
        "title": "Corrientes / Abasto",
        "subtitle": "Ejes vinculados, diferenciados visualmente y sin doble conteo.",
        "reading": "Corrientes se representa como eje teatral-gastronómico entre 9 de Julio y Callao. Abasto queda separado como área aproximada a reforzar alrededor del shopping.",
        "caution": "Ejes aproximados, no delimitaciones oficiales. Abasto queda marcado como área a reforzar y no se fusiona con Corrientes.",
    },
    "belgrano": {
        "page": 11,
        "title": "Belgrano",
        "subtitle": "Barrio Chino, Bajo Belgrano y Belgrano R con distinto grado de respaldo.",
        "reading": "Barrio Chino se muestra como subzona de identidad clara. Bajo Belgrano y Belgrano R se leen como áreas a revisar o reforzar, no como polos consolidados.",
        "caution": "Subzonas de trabajo, no límites oficiales. Belgrano R queda expresamente marcado como subzona a reforzar.",
    },
}


def ensure_dirs() -> None:
    DOCS.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)


def contains_any(value: str, patterns: list[str]) -> bool:
    value_norm = v15.norm(value).upper()
    return any(v15.norm(p).upper() in value_norm for p in patterns)


def ellipse_coords(center: tuple[float, float], width: float, height: float, angle: float, steps: int = 72) -> list[list[float]]:
    lon, lat = center
    theta = math.radians(angle)
    coords: list[list[float]] = []
    for i in range(steps + 1):
        t = 2 * math.pi * i / steps
        x = (width / 2) * math.cos(t)
        y = (height / 2) * math.sin(t)
        xr = x * math.cos(theta) - y * math.sin(theta)
        yr = x * math.sin(theta) + y * math.cos(theta)
        coords.append([lon + xr, lat + yr])
    return coords


def line_buffer_polygon(line: list[tuple[float, float]], width: float = 0.0023) -> list[list[float]]:
    (x1, y1), (x2, y2) = line
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy) or 1
    nx, ny = -dy / length * width, dx / length * width
    return [[x1 + nx, y1 + ny], [x2 + nx, y2 + ny], [x2 - nx, y2 - ny], [x1 - nx, y1 - ny], [x1 + nx, y1 + ny]]


def feature_geometry(row: dict[str, object]) -> dict[str, object]:
    if "polygon" in row:
        coords = [[list(p) for p in row["polygon"]] + [list(row["polygon"][0])]]
        return {"type": "Polygon", "coordinates": coords}
    if "line" in row and row["tipo_geometria"] == "eje aproximado":
        return {"type": "LineString", "coordinates": [list(p) for p in row["line"]]}
    return {
        "type": "Polygon",
        "coordinates": [ellipse_coords(row["center"], float(row["width"]), float(row["height"]), float(row["angle"]))],
    }


def polygon_for_plot(row: dict[str, object]) -> list[list[float]]:
    if "polygon" in row:
        return [list(p) for p in row["polygon"]]
    if "line" in row:
        return line_buffer_polygon(row["line"], width=0.0015 if "Conexión" in row["subzona"] else 0.0024)
    return ellipse_coords(row["center"], float(row["width"]), float(row["height"]), float(row["angle"]), steps=80)


def label_point(row: dict[str, object]) -> tuple[float, float]:
    if "center" in row:
        return row["center"]
    if "line" in row:
        pts = row["line"]
        return ((pts[0][0] + pts[-1][0]) / 2, (pts[0][1] + pts[-1][1]) / 2)
    pts = row["polygon"]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return (sum(xs) / len(xs), sum(ys) / len(ys))


def write_subzone_tables() -> None:
    fieldnames = ["mapa", "subzona", "tipo_geometria", "criterio_geografico", "etiqueta_visible", "color_sugerido", "mostrar_en_mapa", "observacion"]
    with SUBZONAS_CSV.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in SUBZONES:
            writer.writerow({field: row[field] for field in fieldnames})

    features = []
    for row in SUBZONES:
        props = {field: row[field] for field in fieldnames}
        features.append({"type": "Feature", "properties": props, "geometry": feature_geometry(row)})
    SUBZONAS_GEOJSON.write_text(json.dumps({"type": "FeatureCollection", "name": "subzonas_editoriales_polos", "crs": {"type": "name", "properties": {"name": "EPSG:4326"}}, "features": features}, ensure_ascii=False, indent=2), encoding="utf-8")


def draw_street_labels(ax, labels: list[tuple[float, float, str]]) -> None:
    for lon, lat, label in labels:
        ax.text(
            lon,
            lat,
            label,
            fontsize=7.2,
            color="#667381",
            ha="center",
            va="center",
            bbox={"boxstyle": "round,pad=0.18", "fc": "white", "ec": "#DDE3EA", "lw": 0.45, "alpha": 0.82},
            zorder=6,
        )


def draw_subzones(ax, page: str) -> int:
    count = 0
    rows = [row for row in SUBZONES if row["key"] == page and row["mostrar_en_mapa"] == "si"]
    for row in rows:
        coords = polygon_for_plot(row)
        poly = MplPolygon(coords, closed=True, facecolor=row["color_sugerido"], edgecolor="white", alpha=0.33, linewidth=2.2, zorder=4)
        ax.add_patch(poly)
        count += 1
    for row in rows:
        if row.get("mostrar_etiqueta") == "no":
            continue
        src_lon, src_lat = label_point(row)
        lon, lat = label_point(row)
        if "label_pos" in row:
            lon, lat = row["label_pos"]
        if "label_offset" in row:
            dx, dy = row["label_offset"]
            lon += dx
            lat += dy
        label = row["etiqueta_visible"]
        if not label:
            continue
        if row.get("leader_line") == "si":
            ax.plot([src_lon, lon], [src_lat, lat], color="#6E7A86", linewidth=0.7, alpha=0.9, zorder=7)
        size = float(row.get("label_size", 13.2))
        if len(label) > 18:
            size = min(size, 11.2)
        if len(label) > 26:
            size = min(size, 9.6)
        wrap_width = int(row.get("label_width", 15))
        ax.text(
            lon,
            lat,
            textwrap.fill(label, width=wrap_width),
            fontsize=size,
            color=AZUL,
            ha="center",
            va="center",
            weight="bold",
            linespacing=0.88,
            bbox={"boxstyle": "round,pad=0.22", "fc": "white", "ec": "none", "alpha": 0.72},
            zorder=8,
        )
    return count


def render_editorial_map(page: str, streets: gpd.GeoDataFrame, barrios: gpd.GeoDataFrame) -> dict[str, str]:
    cfg = MAP_CFG[page]
    minx, miny, maxx, maxy = cfg["bbox"]
    fig, ax = plt.subplots(figsize=(8.0, 6.0), dpi=230)
    ax.set_facecolor("#FBFCFD")

    if cfg.get("water"):
        ax.add_patch(MplPolygon([(-58.3635, miny), (maxx, miny), (maxx, maxy), (-58.3635, maxy)], facecolor="#DDECF7", edgecolor="none", alpha=0.85, zorder=0))
        ax.text(-58.3587, -34.608, "frente costero", rotation=90, fontsize=9.5, color="#5D7F98", ha="center", va="center", zorder=2)

    local_barrios = barrios.cx[minx:maxx, miny:maxy]
    if not local_barrios.empty:
        local_barrios.plot(ax=ax, facecolor="#F3F6F9", edgecolor="#D6DDE5", linewidth=0.55, zorder=1)

    local_streets = streets.cx[minx:maxx, miny:maxy]
    if not local_streets.empty:
        minor = local_streets[local_streets["tipo_c"].fillna("").str.upper() != "AVENIDA"]
        avenues = local_streets[local_streets["tipo_c"].fillna("").str.upper() == "AVENIDA"]
        if not minor.empty:
            minor.plot(ax=ax, color="#E2E8EE", linewidth=0.22, alpha=0.55, zorder=2)
        if not avenues.empty:
            avenues.plot(ax=ax, color="#C1CAD4", linewidth=0.62, alpha=0.75, zorder=3)
        major = local_streets[
            local_streets["nom_mapa"].fillna("").map(lambda value: contains_any(value, cfg["major"]))
            | local_streets["nomoficial"].fillna("").map(lambda value: contains_any(value, cfg["major"]))
        ]
        if not major.empty:
            major.plot(ax=ax, color="#818D99", linewidth=1.15, alpha=0.86, zorder=3)

    subzone_count = draw_subzones(ax, page)
    draw_street_labels(ax, cfg["street_labels"])

    legend_handles = [
        Line2D([0], [0], color=CELESTE, lw=7, alpha=0.38, label="subzona de trabajo"),
        Line2D([0], [0], color=NARANJA, lw=7, alpha=0.38, label="área a reforzar / validar"),
        Line2D([0], [0], color="#818D99", lw=1.5, label="avenidas y ejes de referencia"),
    ]
    ax.legend(handles=legend_handles, loc="lower left", fontsize=8.0, frameon=True, framealpha=0.94, facecolor="white", edgecolor="#D9DEE5")

    ax.set_xlim(minx, maxx)
    ax.set_ylim(miny, maxy)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_edgecolor("#C9D1DA")
        spine.set_linewidth(0.8)
    ax.set_title(cfg["title"], loc="left", color=AZUL, fontweight="bold", fontsize=16, pad=10)
    fig.text(0.04, 0.035, "áreas aproximadas de lectura; no delimitación oficial", fontsize=8.0, color=GRIS, ha="left")
    fig.text(0.965, 0.035, "Base: Callejero GCBA (CC-BY-2.5-AR)", fontsize=8.0, color=GRIS, ha="right")
    fig.subplots_adjust(left=0.035, right=0.985, top=0.905, bottom=0.115)

    base = MAP_OUTPUTS[page]
    png = ASSETS / f"{base}.png"
    svg = ASSETS / f"{base}.svg"
    fig.savefig(png, dpi=230)
    fig.savefig(svg)
    plt.close(fig)
    return {"png": str(png), "svg": str(svg), "subzonas": str(subzone_count)}


def build_maps() -> tuple[dict[str, Path], dict[str, dict[str, str]]]:
    streets = gpd.read_file(CALLEJERO)
    barrios = gpd.read_file(BARRIOS)
    maps = {"global": PHASE15_OUT / "assets" / "global_mapa_pdf_v3.png"}
    stats: dict[str, dict[str, str]] = {}
    for page in DETAIL_ORDER:
        stat = render_editorial_map(page, streets, barrios)
        maps[page] = Path(stat["png"])
        stats[page] = stat
    return maps, stats


def configure_modules() -> None:
    v15.DOCS = DOCS
    v15.OUT = OUT
    v15.ASSETS = ASSETS
    v15.TABLES = TABLES
    v15.MD_BASE_V3 = MD_BASE_V4
    v15.PDF_V3 = PDF_V4
    v15.MAP_OUTPUTS = MAP_OUTPUTS
    v15.INSTITUCION = INSTITUCION
    v15.GOBIERNO = GOBIERNO
    v15.TITLE = TITLE
    v15.SUBTITLE = SUBTITLE

    v2.DOCS_OUT = DOCS
    v2.OUT = OUT
    v2.ASSETS = ASSETS
    v2.MENTIONS_CSV = TABLES / "menciones_destacadas_por_polo_v4_base.csv"
    v2.PDF = PDF_V4
    v2.MD_BASE = MD_BASE_V4
    v2.INSTITUCION = INSTITUCION
    v2.GOBIERNO = GOBIERNO
    v2.TITLE = TITLE
    v2.SUBTITLE = SUBTITLE
    v2.register_fonts()


def summary_page(c: canvas.Canvas) -> None:
    y = v2.header(c, 3, "Resumen ejecutivo", "Qué ordena este informe", "Universo semilla, lectura territorial y señales para orientar validación.")
    v2.cards_row(c, y - 68, [
        ("22", "polos/ejes del universo semilla", AZUL),
        ("106", "menciones de locales relevadas", VERDE),
        ("5", "mapas editoriales de subzonas", CELESTE),
    ])
    v2.cards_row(c, y - 146, [
        ("0", "mapas con puntos como protagonista", NARANJA),
        ("0", "delimitaciones oficiales nuevas", ROJO),
    ], x=M + 88, total_w=W - 2 * M - 176)
    v2.bullet_list(c, [
        "El informe mantiene el mapa global de 22 polos/ejes como lectura principal del universo semilla.",
        "Las páginas de detalle se reorganizan con áreas coloreadas, etiquetas grandes y callejero suave.",
        "Las menciones destacadas permanecen en cajas laterales para evitar que el mapa funcione como ranking.",
        "Las subzonas son aproximaciones editoriales para lectura territorial y no límites oficiales.",
    ], M, y - 205, W - 2 * M, size=9.6, gap=8.5)
    v2.note_box(c, M, 112, W - 2 * M, 78, "Cómo leer los mapas",
                "Las áreas coloreadas ordenan la lectura visual de cada polo o eje. No constituyen polígonos oficiales, padrón operativo ni confirmación de actividad vigente.",
                color=AZUL, fill=SOFT_AZUL)
    v2.finish(c)


def territorial_page(c: canvas.Canvas) -> None:
    y = v2.header(c, 6, "Lectura territorial general", "Qué muestra la distribución")
    v2.note_box(c, M, y - 86, W - 2 * M, 70, "Cambio visual principal",
                "Los mapas de detalle dejan de depender de puntos y pasan a organizarse por subzonas coloreadas, ejes aproximados y etiquetas de lectura rápida.",
                color=CELESTE, fill=SOFT_AZUL)
    v2.note_box(c, M, y - 176, W - 2 * M, 76, "Ejes que requieren cuidado",
                "Avenida Corrientes y Abasto se muestran como ejes vinculados pero diferenciados. Belgrano R se conserva como subzona a reforzar, no como polo consolidado.",
                color=VERDE, fill=SOFT_VERDE)
    v2.note_box(c, M, y - 272, W - 2 * M, 82, "Uso previsto",
                "La pieza sirve para lectura ejecutiva y conversación de validación territorial. No reemplaza trabajo de campo, definición normativa ni validación de sedes.",
                color=NARANJA, fill=SOFT_NARANJA)
    v2.bullet_list(c, [
        "El callejero queda como soporte visual suave y no como salida técnica.",
        "Las subzonas tienen color, borde claro y etiqueta grande.",
        "Las menciones destacadas siguen fuera del mapa, en cajas de lectura.",
    ], M, 240, W - 2 * M, gap=10)
    v2.finish(c)


def visible_mentions(mentions: list[dict[str, str]], page: str) -> str:
    return v15.visible_mentions(mentions, page)


def detail_page(c: canvas.Canvas, page: str, maps: dict[str, Path], mentions: list[dict[str, str]]) -> None:
    cfg = DETAIL_TEXT[page]
    v2.header(c, cfg["page"], "Detalle territorial", cfg["title"], cfg["subtitle"])
    map_x, map_y, map_w, map_h = M, 320, 328, 330
    side_x = M + 342
    side_w = W - M - side_x
    v2.image_box(c, maps[page], map_x, map_y, map_w, map_h, border=True)
    v2.note_box(c, side_x, 462, side_w, 188, "Menciones destacadas del universo semilla",
                visible_mentions(mentions, page), color=CELESTE, fill=SOFT_AZUL, size=7.2)
    v2.note_box(c, side_x, 320, side_w, 124, "Lectura territorial",
                cfg["reading"], color=VERDE, fill=SOFT_VERDE, size=7.5)
    v2.note_box(c, M, 145, W - 2 * M, 92, "Nota de cautela",
                cfg["caution"], color=NARANJA, fill=SOFT_NARANJA, size=8.7)
    v2.draw_wrapped(c, "No es ranking, no es padrón oficial y no confirma actividad vigente.", M, 118, W - 2 * M, font=v2.FONT_BOLD, size=8.4, color=GRIS, leading=10)
    v2.finish(c)


def annex_method(c: canvas.Canvas) -> None:
    y = v2.header(c, 18, "Anexo B", "Criterio cartográfico y limitaciones")
    v2.bullet_list(c, [
        "El mapa global se conserva como lectura principal de 22 polos/ejes del universo semilla.",
        "Los mapas de detalle usan Callejero GCBA como base visual y subzonas editoriales aproximadas.",
        "Las geometrías se construyeron con coordenadas de referencia, callejero, barrios y puntos sanitizados como apoyo indirecto.",
        "Las áreas coloreadas no definen límites oficiales ni implican reconocimiento normativo.",
        "Los casos con vigencia no confirmada, duplicados sin resolver y búsquedas a corregir quedan fuera de la lectura como oferta activa.",
        "Los hitos colectivos se tratan como referencia territorial, no como restaurante puntual.",
    ], M, y - 10, W - 2 * M, gap=8.5)
    v2.note_box(c, M, 120, W - 2 * M, 98, "Fuente cartográfica",
                "Base callejera: dataset público Calles / Callejero (GeoJson), Buenos Aires Data - GCBA. Licencia CC-BY-2.5-AR. Actualización publicada por el portal: 2 de junio de 2026. Descarga realizada el 3 de julio de 2026.",
                color=CELESTE, fill=SOFT_AZUL, size=8.1)
    v2.finish(c)


def build_pdf(maps: dict[str, Path], mentions: list[dict[str, str]]) -> None:
    c = canvas.Canvas(str(PDF_V4), pagesize=A4)
    c.setTitle(TITLE)
    c.setAuthor(INSTITUCION)
    v2.cover(c)
    v2.index_page(c)
    summary_page(c)
    v2.scope_page(c)
    v2.global_map_page(c, maps)
    territorial_page(c)
    for page in DETAIL_ORDER:
        detail_page(c, page, maps, mentions)
    v2.mentions_criteria_page(c, mentions)
    v2.auxiliary_page(c)
    v2.pending_page(c)
    v2.recommendations_page(c)
    v2.next_steps_page(c)
    v2.annex_universe(c)
    annex_method(c)
    c.save()


def md_mentions(mentions: list[dict[str, str]], page: str) -> str:
    text = visible_mentions(mentions, page)
    return "\n".join(f"- {line}" for line in text.splitlines() if line.strip())


def build_markdown(mentions: list[dict[str, str]]) -> None:
    content = f"""# Polos gastronómicos de la Ciudad de Buenos Aires

## Universo semilla, lectura territorial y subzonas de trabajo

**{INSTITUCION}**  
**{GOBIERNO}**  
Fecha de elaboración: julio de 2026

Este documento es la base editorial de la pieza PDF con mapas editoriales de detalle. Ordena el universo semilla de 22 polos/ejes, mantiene el mapa global como pieza principal y reemplaza la centralidad de los puntos por subzonas coloreadas, ejes aproximados y etiquetas grandes. No constituye padrón oficial, ranking ni confirmación de actividad vigente.

## 1. Resumen ejecutivo

Se ordena un universo semilla de **22 polos/ejes gastronómicos** de la Ciudad y **106 menciones de locales** asociadas a ese universo. La capa auxiliar permite distinguir coincidencias razonables o fuertes, sedes a validar, casos con vigencia no confirmada, duplicados probables y búsquedas a corregir.

La mejora visual de esta versión se concentra en las páginas territoriales: mapas con callejero GCBA suavizado, áreas de color semitransparentes, bordes claros, etiquetas grandes y leyenda mínima. Los puntos dejan de ser el elemento principal.

## 2. Alcance y criterio de lectura

El universo semilla es un insumo de trabajo. Las menciones destacadas no son ranking, no son recomendación comercial y no equivalen a padrón de locales activos.

Las subzonas son aproximaciones editoriales construidas para facilitar la lectura territorial. No son límites oficiales, polígonos normativos ni delimitaciones cerradas.

## 3. Mapa global de 22 polos/ejes

El mapa global se conserva como mapa principal. Representa áreas, ejes y zonas de lectura territorial del universo semilla, sin definir límites oficiales.

## 4. Lectura territorial general

Palermo concentra el mayor volumen de menciones y requiere distinguir subzonas internas. Puerto Madero se lee mejor como banda de docks y eje costero. San Telmo se entiende a partir del Mercado y el casco histórico. Corrientes y Abasto se mantienen vinculados pero diferenciados. Belgrano se presenta como macroárea con subzonas de respaldo desigual.

## 5. Detalles territoriales

### Palermo / Las Cañitas

{md_mentions(mentions, "palermo")}

Lectura: se distinguen Palermo Soho, Palermo Hollywood y Las Cañitas como áreas aproximadas. Palermo Chico y Palermo Nuevo/Botánico se usan como contexto visual.

### Puerto Madero

{md_mentions(mentions, "puerto")}

Lectura: el mapa prioriza docks, eje costero, área Faena/El Mercado y sectores a validar.

### San Telmo

{md_mentions(mentions, "san_telmo")}

Lectura: el Mercado de San Telmo se trata como hito colectivo. El casco histórico y el eje Defensa ordenan la pieza.

### Corrientes / Abasto

{md_mentions(mentions, "corrientes")}

Lectura: Corrientes es eje teatral-gastronómico 9 de Julio-Callao. Abasto se presenta como área a reforzar alrededor del shopping y no se fusiona con Corrientes.

### Belgrano

{md_mentions(mentions, "belgrano")}

Lectura: Barrio Chino tiene identidad gastronómica clara; Bajo Belgrano conserva sedes a validar; Belgrano R queda como subzona a reforzar.

## 6. Fuente cartográfica y geometrías

Base callejera usada: **Calles / Callejero (GeoJson)** de Buenos Aires Data - GCBA. Licencia **CC-BY-2.5-AR**. Fecha de actualización publicada por el portal: **2 de junio de 2026**. Descarga local para esta línea de trabajo: **3 de julio de 2026**.

Las geometrías editoriales se documentan en la tabla y el GeoJSON de esta fase. Fueron armadas con coordenadas de referencia, barrios, callejero, puntos sanitizados como apoyo y criterio editorial documentado.

## 7. Decisiones pendientes

- Validar con Ale el recorte de Corrientes y Abasto.
- Definir si Belgrano R queda visible en la versión final o solo como nota de trabajo.
- Resolver sedes, cadenas y duplicados antes de cualquier mapa operativo.
- Ajustar paleta y cantidad de etiquetas si la pieza final requiere mayor sobriedad.

## 8. Recomendaciones prudentes

- Usar el mapa global como lectura institucional del universo semilla.
- Usar los mapas editoriales como apoyo visual de conversación, no como padrón operativo.
- Mantener separadas las menciones incluidas, las sedes a validar y los casos excluidos por prudencia.
- Validar territorialmente antes de publicar detalle operativo.
"""
    MD_BASE_V4.write_text(content, encoding="utf-8")


def build_cambios(stats: dict[str, dict[str, str]]) -> None:
    lines = "\n".join(f"- {MAP_CFG[p]['title']}: {stats[p]['subzonas']} subzonas/ejes editoriales visibles." for p in DETAIL_ORDER)
    content = f"""# Cambios V3 a V4 - PolosGastro DGDGAS

## Qué cambió

- Se creó una Fase 16 paralela con mapas editoriales de subzonas.
- Se mantuvo el mapa global de 22 polos/ejes.
- Se reemplazaron los cinco mapas de detalle por piezas donde predominan áreas coloreadas y etiquetas grandes.
- Los puntos dejaron de ser el elemento principal: las menciones quedan en cajas laterales del PDF.
- Se creó una tabla de subzonas y un GeoJSON con geometrías aproximadas para trazabilidad.

## Por qué se abandonó la centralidad de los puntos

El PDF anterior incorporó callejero, pero la lectura seguía pareciendo una salida técnica de puntos. Para una pieza ejecutiva, el objetivo es entender zonas, ejes y relaciones territoriales. Por eso el mapa pasa a mostrar áreas de lectura, subzonas y ejes aproximados, mientras que los nombres de locales quedan como menciones destacadas fuera del mapa.

## Cómo se construyeron las subzonas aproximadas

Las geometrías se armaron con coordenadas de referencia, barrios/comunas como marco, callejero GCBA, puntos sanitizados como apoyo indirecto y criterio editorial documentado. Se usaron elipses, polígonos y ejes aproximados. No son límites oficiales ni deben tratarse como delimitaciones normativas.

## Mapas generados

{lines}

## Qué mapas quedaron más claros

- Palermo / Las Cañitas: ahora separa Palermo Soho, Palermo Hollywood y Las Cañitas con etiquetas grandes.
- Puerto Madero: se entiende mejor como banda de docks y eje costero.
- San Telmo: el Mercado aparece como hito colectivo y el casco histórico ordena la lectura.
- Corrientes / Abasto: muestra vínculo, pero diferencia el eje Corrientes del área Abasto.
- Belgrano: separa Barrio Chino, Bajo Belgrano y Belgrano R, con Belgrano R como subzona a reforzar.

## Limitaciones que siguen

- Las subzonas son aproximadas y no límites oficiales.
- No se valida actividad vigente de locales.
- Abasto y Belgrano R requieren decisión humana antes de una versión final.
- Las menciones destacadas siguen siendo universo semilla, no padrón operativo.

## Qué queda para decisión final con Ale

- Cerrar si Abasto queda como área vinculada o página propia.
- Decidir si Belgrano R sigue visible o pasa a nota.
- Validar si Palermo requiere todas las subzonas contextuales o solo las principales.
- Definir nivel final de color y densidad de etiquetas para circulación institucional.
"""
    CAMBIOS_V4.write_text(content, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    configure_modules()
    mentions = v2.build_mentions()
    write_subzone_tables()
    maps, stats = build_maps()
    build_markdown(mentions)
    build_pdf(maps, mentions)
    build_cambios(stats)
    print(f"PDF: {PDF_V4}")
    print(f"Tabla subzonas: {SUBZONAS_CSV}")
    print(f"GeoJSON subzonas: {SUBZONAS_GEOJSON}")
    print("Mapas:", ", ".join(MAP_OUTPUTS.values()))
    print("Subzonas por mapa:", dict(Counter(row["key"] for row in SUBZONES if row["mostrar_en_mapa"] == "si")))


if __name__ == "__main__":
    main()
