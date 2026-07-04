"""Build PolosGastro phase 17 editorial geometry map assets.

This phase only creates map assets, a contact sheet, a geometry CSV and a QA
note. It uses local street/context files already present in the repository and
does not call APIs, scrape sources, touch source data, stage changes, or build a
PDF.
"""
from __future__ import annotations

import csv
import math
import textwrap
from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "none"
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Circle, Polygon as MplPolygon  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402


ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs" / "polos_gastro" / "fase17_mapas_geometrias_editoriales"
OUT = ROOT / "outputs" / "polos_gastro" / "fase17_mapas_geometrias_editoriales"
ASSETS = OUT / "assets"
TABLES = OUT / "tablas"

CALLEJERO = ROOT / "outputs" / "polos_gastro" / "fase15_mapas_callejeros_v3" / "assets" / "callejero_gcba_2026_06_02.geojson"
BARRIOS = ROOT / "data" / "raw" / "geo_barrios.geojson"

GEOMETRIAS_CSV = TABLES / "geometrias_editoriales_v17.csv"
CONTACT_SHEET = OUT / "contact_sheet_mapas_v17.png"
QA_DOC = DOCS / "QA_MAPAS_V17_GEOMETRIAS_EDITORIALES.md"

INSTITUCION = "DGDGAS — Dirección General de Desarrollo Gastronómico"
FUENTE_BASE = "Base: Callejero GCBA (CC-BY-2.5-AR). Geometrías editoriales aproximadas; no límites oficiales."

AZUL = "#1F3B57"
CELESTE = "#2C6E9E"
VERDE = "#1A9850"
NARANJA = "#C0762B"
ROJO = "#C0392B"
VIOLETA = "#7A5C99"
GRIS = "#555555"
GRIS_CALLE = "#E2E8EE"
GRIS_AVENIDA = "#818D99"

DETAIL_ORDER = ["palermo", "puerto", "san_telmo", "corrientes", "belgrano"]

MAP_OUTPUTS = {
    "palermo": "mapa_v17_palermo_las_canitas",
    "puerto": "mapa_v17_puerto_madero",
    "san_telmo": "mapa_v17_san_telmo",
    "corrientes": "mapa_v17_corrientes_abasto",
    "belgrano": "mapa_v17_belgrano",
}

MAP_CFG = {
    "palermo": {
        "title": "Palermo / Las Cañitas",
        "bbox": (-58.446, -34.596, -58.404, -34.560),
        "major": ["SANTA FE", "CORDOBA", "JUAN B. JUSTO", "SCALABRINI", "DORREGO", "DEL LIBERTADOR", "LUIS MARIA CAMPOS", "BAEZ", "CHENAUT", "ORTEGA"],
        "street_labels": [
            (-58.424, -34.5818, "Av. Santa Fe"),
            (-58.429, -34.5922, "Av. Cordoba"),
            (-58.436, -34.5862, "Juan B. Justo"),
            (-58.422, -34.5887, "Scalabrini Ortiz"),
            (-58.434, -34.5668, "Luis M. Campos"),
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
            (-58.363, -34.621, "sector costero"),
        ],
    },
    "san_telmo": {
        "title": "San Telmo",
        "bbox": (-58.381, -34.631, -58.365, -34.615),
        "major": ["DEFENSA", "BOLIVAR", "CHILE", "ESTADOS UNIDOS", "CARLOS CALVO", "HUMBERTO", "SAN JUAN", "PASEO COLON"],
        "street_labels": [
            (-58.3723, -34.6232, "Defensa"),
            (-58.371, -34.628, "Av. San Juan"),
            (-58.376, -34.620, "Chile"),
            (-58.367, -34.624, "Paseo Colon"),
        ],
    },
    "corrientes": {
        "title": "Corrientes / Abasto",
        "bbox": (-58.418, -34.611, -58.374, -34.596),
        "major": ["CORRIENTES", "CALLAO", "9 DE JULIO", "URUGUAY", "PARANA", "RIOBAMBA", "PASTEUR", "PUEYRREDON", "ANCHORENA", "AGUERO"],
        "street_labels": [
            (-58.389, -34.6022, "Av. Corrientes"),
            (-58.392, -34.606, "Callao"),
            (-58.381, -34.606, "9 de Julio"),
            (-58.410, -34.6002, "Abasto"),
        ],
    },
    "belgrano": {
        "title": "Belgrano",
        "bbox": (-58.467, -34.568, -58.436, -34.548),
        "major": ["JURAMENTO", "MENDOZA", "OLAZABAL", "ARRIBENOS", "MONTA", "DEL LIBERTADOR", "CABILDO", "LA PAMPA", "MIGUELETES"],
        "street_labels": [
            (-58.451, -34.556, "Juramento"),
            (-58.454, -34.559, "Mendoza"),
            (-58.441, -34.559, "Del Libertador"),
            (-58.458, -34.565, "Cabildo"),
        ],
    },
}


GEOMETRIES = [
    {
        "key": "palermo",
        "mapa": "Palermo / Las Cañitas",
        "subzona": "Palermo Soho",
        "tipo_geometria": "poligono_por_avenidas",
        "shape": "polygon",
        "coords": [(-58.4330, -34.5824), (-58.4210, -34.5824), (-58.4210, -34.5924), (-58.4355, -34.5924), (-58.4330, -34.5824)],
        "delimitacion_textual": "Av. Santa Fe, Av. Scalabrini Ortiz, Av. Cordoba y Av. Juan B. Justo.",
        "criterio_geografico": "Poligono rectilineo apoyado en avenidas principales para reemplazar la mancha/elipse del V4.",
        "etiqueta_visible": "PALERMO SOHO",
        "mostrar_etiqueta": "si",
        "estilo_visual": "relleno celeste semitransparente con borde blanco",
        "observacion": "Subzona aproximada de lectura; no delimitacion oficial.",
        "color": CELESTE,
        "label_pos": (-58.4268, -34.5889),
        "label_width": 13,
    },
    {
        "key": "palermo",
        "mapa": "Palermo / Las Cañitas",
        "subzona": "Palermo Hollywood",
        "tipo_geometria": "poligono_por_avenidas",
        "shape": "polygon",
        "coords": [(-58.4440, -34.5780), (-58.4330, -34.5824), (-58.4355, -34.5924), (-58.4445, -34.5922), (-58.4440, -34.5780)],
        "delimitacion_textual": "Av. Juan B. Justo, Av. Santa Fe, Av. Dorrego y Av. Cordoba.",
        "criterio_geografico": "Poligono de lectura apoyado en avenidas y borde occidental por Dorrego.",
        "etiqueta_visible": "PALERMO HOLLYWOOD",
        "mostrar_etiqueta": "si",
        "estilo_visual": "relleno verde semitransparente con borde blanco",
        "observacion": "Subzona aproximada de lectura; no delimitacion oficial.",
        "color": VERDE,
        "label_pos": (-58.4382, -34.5866),
        "label_width": 12,
    },
    {
        "key": "palermo",
        "mapa": "Palermo / Las Cañitas",
        "subzona": "Las Cañitas",
        "tipo_geometria": "poligono_por_avenidas",
        "shape": "polygon",
        "coords": [(-58.4395, -34.5652), (-58.4295, -34.5630), (-58.4258, -34.5687), (-58.4325, -34.5735), (-58.4405, -34.5705), (-58.4395, -34.5652)],
        "delimitacion_textual": "Area aproximada alrededor de Baez, Luis Maria Campos, Libertador, Ortega y Gasset / Chenaut.",
        "criterio_geografico": "Poligono orientado por cuadras del entorno Las Canitas, sin elipse principal.",
        "etiqueta_visible": "LAS CAÑITAS",
        "mostrar_etiqueta": "si",
        "estilo_visual": "relleno naranja semitransparente con borde blanco",
        "observacion": "Subzona aproximada de lectura; no delimitacion oficial.",
        "color": NARANJA,
        "label_pos": (-58.4342, -34.5685),
        "label_width": 12,
    },
    {
        "key": "puerto",
        "mapa": "Puerto Madero",
        "subzona": "Docks / eje costero",
        "tipo_geometria": "poligono_por_avenidas",
        "shape": "polygon",
        "coords": [(-58.3700, -34.5905), (-58.3592, -34.5905), (-58.3578, -34.6260), (-58.3662, -34.6272), (-58.3708, -34.6100), (-58.3700, -34.5905)],
        "delimitacion_textual": "Banda longitudinal de docks entre el frente de agua y el corredor Alicia Moreau de Justo / Juana Manso.",
        "criterio_geografico": "Forma longitudinal orientada al rio y a los docks, no circulo ni elipse.",
        "etiqueta_visible": "DOCKS",
        "mostrar_etiqueta": "si",
        "estilo_visual": "relleno celeste longitudinal con borde blanco",
        "observacion": "Area aproximada de lectura; no delimitacion oficial.",
        "color": CELESTE,
        "label_pos": (-58.3650, -34.6060),
        "label_width": 10,
    },
    {
        "key": "puerto",
        "mapa": "Puerto Madero",
        "subzona": "Sector costero",
        "tipo_geometria": "eje_lineal",
        "shape": "line",
        "coords": [(-58.3600, -34.5940), (-58.3602, -34.6245)],
        "delimitacion_textual": "Eje longitudinal paralelo al frente costero de Puerto Madero.",
        "criterio_geografico": "Eje de lectura costero para ordenar la pieza sin gran mancha.",
        "etiqueta_visible": "SECTOR COSTERO",
        "mostrar_etiqueta": "si",
        "estilo_visual": "linea naranja gruesa con buffer visual angosto",
        "observacion": "Eje aproximado; no delimitacion oficial.",
        "color": NARANJA,
        "label_pos": (-58.3575, -34.6095),
        "label_width": 10,
    },
    {
        "key": "puerto",
        "mapa": "Puerto Madero",
        "subzona": "Faena / El Mercado",
        "tipo_geometria": "hito_colectivo",
        "shape": "hito",
        "coords": [(-58.3642, -34.6172)],
        "delimitacion_textual": "Referencia puntual aproximada del entorno Faena / El Mercado.",
        "criterio_geografico": "Hito o area puntual, separado de la banda de docks.",
        "etiqueta_visible": "FAENA / EL MERCADO",
        "mostrar_etiqueta": "si",
        "estilo_visual": "marcador rojo con etiqueta externa",
        "observacion": "Hito de lectura; no representa limite ni local activo confirmado.",
        "color": ROJO,
        "label_pos": (-58.3725, -34.6210),
        "label_width": 12,
    },
    {
        "key": "san_telmo",
        "mapa": "San Telmo",
        "subzona": "Mercado de San Telmo",
        "tipo_geometria": "hito_colectivo",
        "shape": "hito",
        "coords": [(-58.3730, -34.6218)],
        "delimitacion_textual": "Hito colectivo Mercado de San Telmo.",
        "criterio_geografico": "Marcador editorial del mercado como ordenador territorial.",
        "etiqueta_visible": "MERCADO",
        "mostrar_etiqueta": "si",
        "estilo_visual": "marcador rojo con etiqueta cercana",
        "observacion": "Hito colectivo; no restaurante puntual.",
        "color": ROJO,
        "label_pos": (-58.3687, -34.6210),
        "label_width": 10,
    },
    {
        "key": "san_telmo",
        "mapa": "San Telmo",
        "subzona": "Casco historico / Defensa",
        "tipo_geometria": "eje_lineal",
        "shape": "line",
        "coords": [(-58.3732, -34.6185), (-58.3711, -34.6290)],
        "delimitacion_textual": "Eje Defensa y entorno patrimonial del casco historico.",
        "criterio_geografico": "Eje aproximado sobre Defensa para evitar una mancha generica.",
        "etiqueta_visible": "CASCO HISTORICO / DEFENSA",
        "mostrar_etiqueta": "si",
        "estilo_visual": "linea verde gruesa con buffer visual angosto",
        "observacion": "Eje aproximado de lectura; no delimitacion oficial.",
        "color": VERDE,
        "label_pos": (-58.3696, -34.6265),
        "label_width": 14,
    },
    {
        "key": "san_telmo",
        "mapa": "San Telmo",
        "subzona": "Area gastronomica cercana",
        "tipo_geometria": "poligono_por_avenidas",
        "shape": "polygon",
        "coords": [(-58.3780, -34.6192), (-58.3700, -34.6192), (-58.3700, -34.6244), (-58.3780, -34.6244), (-58.3780, -34.6192)],
        "delimitacion_textual": "Area aproximada alrededor del mercado, Chile, Estados Unidos y calles cercanas.",
        "criterio_geografico": "Rectangulo por cuadras proximas al mercado y al eje Defensa.",
        "etiqueta_visible": "AREA GASTRONOMICA",
        "mostrar_etiqueta": "si",
        "estilo_visual": "relleno naranja semitransparente con borde blanco",
        "observacion": "Subzona aproximada de lectura; no delimitacion oficial.",
        "color": NARANJA,
        "label_pos": (-58.3770, -34.6203),
        "label_width": 12,
    },
    {
        "key": "corrientes",
        "mapa": "Corrientes / Abasto",
        "subzona": "Corrientes 9 de Julio-Callao",
        "tipo_geometria": "eje_lineal",
        "shape": "line",
        "coords": [(-58.3815, -34.6038), (-58.3928, -34.6043)],
        "delimitacion_textual": "Av. Corrientes desde 9 de Julio hasta Callao.",
        "criterio_geografico": "Eje lineal claro sobre Corrientes, sin mancha territorial.",
        "etiqueta_visible": "CORRIENTES 9 DE JULIO-CALLAO",
        "mostrar_etiqueta": "si",
        "estilo_visual": "linea celeste gruesa con extremos marcados",
        "observacion": "Eje aproximado; no delimitacion oficial.",
        "color": CELESTE,
        "label_pos": (-58.3868, -34.6060),
        "label_width": 17,
    },
    {
        "key": "corrientes",
        "mapa": "Corrientes / Abasto",
        "subzona": "Obelisco / Teatros",
        "tipo_geometria": "area_influencia",
        "shape": "polygon",
        "coords": [(-58.3840, -34.6008), (-58.3782, -34.6008), (-58.3782, -34.6060), (-58.3840, -34.6060), (-58.3840, -34.6008)],
        "delimitacion_textual": "Caja chica alrededor de 9 de Julio y Corrientes.",
        "criterio_geografico": "Area contextual acotada para ubicar el eje teatral sin fusionarlo con Abasto.",
        "etiqueta_visible": "OBELISCO / TEATROS",
        "mostrar_etiqueta": "si",
        "estilo_visual": "relleno verde claro con borde blanco",
        "observacion": "Area de influencia aproximada.",
        "color": VERDE,
        "label_pos": (-58.3798, -34.6023),
        "label_width": 10,
    },
    {
        "key": "corrientes",
        "mapa": "Corrientes / Abasto",
        "subzona": "Abasto a reforzar",
        "tipo_geometria": "area_a_reforzar",
        "shape": "polygon",
        "coords": [(-58.4165, -34.5993), (-58.4050, -34.5993), (-58.4048, -34.6076), (-58.4167, -34.6076), (-58.4165, -34.5993)],
        "delimitacion_textual": "Area aproximada de cinco cuadras alrededor del Abasto Shopping.",
        "criterio_geografico": "Poligono separado del eje Corrientes para evitar lectura de fusion.",
        "etiqueta_visible": "ABASTO A REFORZAR",
        "mostrar_etiqueta": "si",
        "estilo_visual": "relleno naranja con borde blanco y etiqueta grande",
        "observacion": "Area a reforzar; no se presenta como polo consolidado.",
        "color": NARANJA,
        "label_pos": (-58.4108, -34.6035),
        "label_width": 12,
    },
    {
        "key": "belgrano",
        "mapa": "Belgrano",
        "subzona": "Barrio Chino",
        "tipo_geometria": "poligono_por_avenidas",
        "shape": "polygon",
        "coords": [(-58.4557, -34.5535), (-58.4480, -34.5535), (-58.4478, -34.5588), (-58.4552, -34.5593), (-58.4557, -34.5535)],
        "delimitacion_textual": "Entorno Arribenos, Juramento, Mendoza y vias.",
        "criterio_geografico": "Poligono por cuadras reconocibles del Barrio Chino.",
        "etiqueta_visible": "BARRIO CHINO",
        "mostrar_etiqueta": "si",
        "estilo_visual": "relleno celeste semitransparente con borde blanco",
        "observacion": "Subzona aproximada de lectura; no delimitacion oficial.",
        "color": CELESTE,
        "label_pos": (-58.4518, -34.5558),
        "label_width": 12,
    },
    {
        "key": "belgrano",
        "mapa": "Belgrano",
        "subzona": "Bajo Belgrano",
        "tipo_geometria": "area_influencia",
        "shape": "polygon",
        "coords": [(-58.4465, -34.5540), (-58.4368, -34.5542), (-58.4368, -34.5642), (-58.4462, -34.5648), (-58.4465, -34.5540)],
        "delimitacion_textual": "Area aproximada hacia Bajo Belgrano, vinculada a Libertador y calles del entorno.",
        "criterio_geografico": "Area de lectura orientada por cuadras, sin presentarla como limite oficial.",
        "etiqueta_visible": "BAJO BELGRANO",
        "mostrar_etiqueta": "si",
        "estilo_visual": "relleno verde semitransparente con borde blanco",
        "observacion": "Area aproximada; sedes a validar segun fases previas.",
        "color": VERDE,
        "label_pos": (-58.4416, -34.5596),
        "label_width": 12,
    },
    {
        "key": "belgrano",
        "mapa": "Belgrano",
        "subzona": "Belgrano R a reforzar",
        "tipo_geometria": "area_a_reforzar",
        "shape": "polygon",
        "coords": [(-58.4660, -34.5588), (-58.4578, -34.5588), (-58.4578, -34.5662), (-58.4664, -34.5662), (-58.4660, -34.5588)],
        "delimitacion_textual": "Area a reforzar alrededor de Belgrano R.",
        "criterio_geografico": "Poligono chico y deliberadamente no sobredimensionado al oeste de Cabildo.",
        "etiqueta_visible": "BELGRANO R A REFORZAR",
        "mostrar_etiqueta": "si",
        "estilo_visual": "relleno naranja semitransparente con borde blanco",
        "observacion": "Area a reforzar; no polo consolidado.",
        "color": NARANJA,
        "label_pos": (-58.4622, -34.5626),
        "label_width": 12,
    },
]


def ensure_dirs() -> None:
    DOCS.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)


def norm(value: str) -> str:
    return (
        value.upper()
        .replace("Á", "A")
        .replace("É", "E")
        .replace("Í", "I")
        .replace("Ó", "O")
        .replace("Ú", "U")
        .replace("Ñ", "N")
    )


def contains_any(value: str, patterns: list[str]) -> bool:
    value_norm = norm(value or "")
    return any(norm(pattern) in value_norm for pattern in patterns)


def line_buffer_polygon(points: list[tuple[float, float]], width: float = 0.0012) -> list[tuple[float, float]]:
    (x1, y1), (x2, y2) = points[0], points[-1]
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / length * width, dx / length * width
    return [(x1 + nx, y1 + ny), (x2 + nx, y2 + ny), (x2 - nx, y2 - ny), (x1 - nx, y1 - ny), (x1 + nx, y1 + ny)]


def shape_points(row: dict[str, object]) -> list[tuple[float, float]]:
    coords = row["coords"]
    if row["shape"] == "line":
        return line_buffer_polygon(coords, width=0.00105)
    if row["shape"] == "hito":
        lon, lat = coords[0]
        size = 0.0014
        return [(lon, lat + size), (lon + size, lat), (lon, lat - size), (lon - size, lat), (lon, lat + size)]
    return coords


def anchor_point(row: dict[str, object]) -> tuple[float, float]:
    coords = row["coords"]
    if row["shape"] == "hito":
        return coords[0]
    if row["shape"] == "line":
        return ((coords[0][0] + coords[-1][0]) / 2, (coords[0][1] + coords[-1][1]) / 2)
    xs = [point[0] for point in coords[:-1]]
    ys = [point[1] for point in coords[:-1]]
    return (sum(xs) / len(xs), sum(ys) / len(ys))


def write_geometry_csv() -> None:
    fieldnames = [
        "mapa",
        "subzona",
        "tipo_geometria",
        "delimitacion_textual",
        "criterio_geografico",
        "etiqueta_visible",
        "mostrar_etiqueta",
        "estilo_visual",
        "observacion",
    ]
    with GEOMETRIAS_CSV.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in GEOMETRIES:
            writer.writerow({field: row[field] for field in fieldnames})


def draw_street_context(ax, page: str, streets: gpd.GeoDataFrame, barrios: gpd.GeoDataFrame) -> None:
    cfg = MAP_CFG[page]
    minx, miny, maxx, maxy = cfg["bbox"]
    if cfg.get("water"):
        ax.add_patch(MplPolygon([(-58.3635, miny), (maxx, miny), (maxx, maxy), (-58.3635, maxy)], facecolor="#DDECF7", edgecolor="none", alpha=0.88, zorder=0))
        ax.text(-58.3582, -34.608, "frente costero", rotation=90, fontsize=9.2, color="#5D7F98", ha="center", va="center", zorder=2)

    local_barrios = barrios.cx[minx:maxx, miny:maxy]
    if not local_barrios.empty:
        local_barrios.plot(ax=ax, facecolor="#F3F6F9", edgecolor="#D6DDE5", linewidth=0.55, zorder=1)

    local_streets = streets.cx[minx:maxx, miny:maxy]
    if local_streets.empty:
        return
    tipo = local_streets["tipo_c"].fillna("").str.upper()
    minor = local_streets[tipo != "AVENIDA"]
    avenues = local_streets[tipo == "AVENIDA"]
    if not minor.empty:
        minor.plot(ax=ax, color=GRIS_CALLE, linewidth=0.20, alpha=0.56, zorder=2)
    if not avenues.empty:
        avenues.plot(ax=ax, color="#C1CAD4", linewidth=0.62, alpha=0.76, zorder=3)
    major = local_streets[
        local_streets["nom_mapa"].fillna("").map(lambda value: contains_any(value, cfg["major"]))
        | local_streets["nomoficial"].fillna("").map(lambda value: contains_any(value, cfg["major"]))
    ]
    if not major.empty:
        major.plot(ax=ax, color=GRIS_AVENIDA, linewidth=1.16, alpha=0.90, zorder=4)


def draw_street_labels(ax, labels: list[tuple[float, float, str]]) -> None:
    for lon, lat, label in labels:
        ax.text(
            lon,
            lat,
            label,
            fontsize=7.1,
            color="#667381",
            ha="center",
            va="center",
            bbox={"boxstyle": "round,pad=0.18", "fc": "white", "ec": "#DDE3EA", "lw": 0.45, "alpha": 0.84},
            zorder=8,
        )


def draw_geometries(ax, page: str) -> int:
    rows = [row for row in GEOMETRIES if row["key"] == page]
    for row in rows:
        color = row["color"]
        if row["shape"] == "line":
            coords = row["coords"]
            ax.plot([coords[0][0], coords[-1][0]], [coords[0][1], coords[-1][1]], color=color, linewidth=9.0, alpha=0.35, solid_capstyle="round", zorder=5)
            ax.plot([coords[0][0], coords[-1][0]], [coords[0][1], coords[-1][1]], color=color, linewidth=2.0, alpha=0.95, solid_capstyle="round", zorder=6)
            ax.scatter([coords[0][0], coords[-1][0]], [coords[0][1], coords[-1][1]], s=16, color=color, zorder=7)
        elif row["shape"] == "hito":
            lon, lat = row["coords"][0]
            ax.add_patch(Circle((lon, lat), radius=0.00105, facecolor=color, edgecolor="white", linewidth=1.3, alpha=0.92, zorder=7))
        else:
            poly = MplPolygon(shape_points(row), closed=True, facecolor=color, edgecolor="white", alpha=0.34, linewidth=2.1, zorder=5)
            ax.add_patch(poly)

    for row in rows:
        if row["mostrar_etiqueta"] != "si":
            continue
        src_lon, src_lat = anchor_point(row)
        lon, lat = row.get("label_pos", (src_lon, src_lat))
        if (src_lon, src_lat) != (lon, lat):
            ax.plot([src_lon, lon], [src_lat, lat], color="#6E7A86", linewidth=0.72, alpha=0.85, zorder=8)
        label = row["etiqueta_visible"]
        size = 12.4
        if len(label) > 18:
            size = 10.8
        if len(label) > 26:
            size = 9.4
        ax.text(
            lon,
            lat,
            textwrap.fill(label, width=int(row.get("label_width", 13))),
            fontsize=size,
            color=AZUL,
            ha="center",
            va="center",
            weight="bold",
            linespacing=0.88,
            bbox={"boxstyle": "round,pad=0.23", "fc": "white", "ec": "none", "alpha": 0.78},
            zorder=9,
        )
    return len(rows)


def render_map(page: str, streets: gpd.GeoDataFrame, barrios: gpd.GeoDataFrame) -> dict[str, Path | int]:
    cfg = MAP_CFG[page]
    minx, miny, maxx, maxy = cfg["bbox"]
    fig, ax = plt.subplots(figsize=(8.0, 6.0), dpi=230)
    ax.set_facecolor("#FBFCFD")

    draw_street_context(ax, page, streets, barrios)
    count = draw_geometries(ax, page)
    draw_street_labels(ax, cfg["street_labels"])

    legend_handles = [
        Line2D([0], [0], color=CELESTE, lw=7, alpha=0.40, label="subzona aproximada de lectura"),
        Line2D([0], [0], color=NARANJA, lw=7, alpha=0.40, label="area a reforzar / influencia"),
        Line2D([0], [0], color=GRIS_AVENIDA, lw=1.6, label="avenidas y ejes de referencia"),
    ]
    ax.legend(handles=legend_handles, loc="lower left", fontsize=7.8, frameon=True, framealpha=0.94, facecolor="white", edgecolor="#D9DEE5")

    ax.set_xlim(minx, maxx)
    ax.set_ylim(miny, maxy)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_edgecolor("#C9D1DA")
        spine.set_linewidth(0.8)
    ax.set_title(cfg["title"], loc="left", color=AZUL, fontweight="bold", fontsize=16, pad=10)
    fig.text(0.04, 0.047, "subzonas/ejes aproximados; no límites oficiales", fontsize=8.0, color=GRIS, ha="left")
    fig.text(0.965, 0.030, INSTITUCION, fontsize=8.0, color=GRIS, ha="right")
    fig.text(0.965, 0.014, "Base: Callejero GCBA", fontsize=7.4, color=GRIS, ha="right")
    fig.subplots_adjust(left=0.035, right=0.985, top=0.905, bottom=0.130)

    base = MAP_OUTPUTS[page]
    png = ASSETS / f"{base}.png"
    svg = ASSETS / f"{base}.svg"
    fig.savefig(png, dpi=230)
    fig.savefig(svg)
    plt.close(fig)
    return {"png": png, "svg": svg, "geometrias": count}


def build_maps() -> dict[str, dict[str, Path | int]]:
    streets = gpd.read_file(CALLEJERO)
    barrios = gpd.read_file(BARRIOS)
    return {page: render_map(page, streets, barrios) for page in DETAIL_ORDER}


def build_contact_sheet(stats: dict[str, dict[str, Path | int]]) -> None:
    thumbs: list[tuple[str, Image.Image]] = []
    for page in DETAIL_ORDER:
        image = Image.open(stats[page]["png"]).convert("RGB")
        image.thumbnail((760, 570), Image.Resampling.LANCZOS)
        thumbs.append((MAP_CFG[page]["title"], image))

    margin = 36
    title_h = 52
    label_h = 28
    cell_w = 820
    cell_h = 650
    sheet = Image.new("RGB", (cell_w * 2 + margin * 3, title_h + cell_h * 3 + margin * 4), "white")
    draw = ImageDraw.Draw(sheet)
    try:
        title_font = ImageFont.truetype("arial.ttf", 24)
        label_font = ImageFont.truetype("arial.ttf", 18)
        note_font = ImageFont.truetype("arial.ttf", 14)
    except OSError:
        title_font = label_font = note_font = ImageFont.load_default()

    draw.text((margin, 18), "Fase 17 - mapas editoriales con geometrías por calles/ejes", fill=AZUL, font=title_font)
    for idx, (title, image) in enumerate(thumbs):
        col = idx % 2
        row = idx // 2
        x = margin + col * (cell_w + margin)
        y = title_h + margin + row * cell_h
        draw.text((x, y), title, fill=AZUL, font=label_font)
        sheet.paste(image, (x, y + label_h))
    draw.text((margin, sheet.height - 28), "DGDGAS - activos de revisión. No PDF generado.", fill=GRIS, font=note_font)
    sheet.save(CONTACT_SHEET)


def build_qa(stats: dict[str, dict[str, Path | int]]) -> None:
    maps = "\n".join(
        f"- `{stats[page]['png'].relative_to(ROOT)}` y `{stats[page]['svg'].relative_to(ROOT)}` ({stats[page]['geometrias']} geometria(s))."
        for page in DETAIL_ORDER
    )
    content = f"""# QA mapas V17 - geometrias editoriales PolosGastro

Fecha de control: 3 de julio de 2026.

## Resultado general

- Estado: assets creados para revision visual, sin generar PDF.
- Marca visible usada en los mapas: **DGDGAS — Dirección General de Desarrollo Gastronómico**.
- Base cartografica: callejero GCBA local ya disponible en el repo.
- Criterio: subzona aproximada de lectura, eje aproximado o area a reforzar; no limites oficiales.

## Mapas creados

{maps}

Hoja de contacto:

- `{CONTACT_SHEET.relative_to(ROOT)}`

Tabla de geometrias:

- `{GEOMETRIAS_CSV.relative_to(ROOT)}`

## QA visual

- [x] Se redujeron elipses como forma principal: no se usa ninguna elipse en la capa V17.
- [x] Palermo / Las Canitas usa poligonos apoyados en avenidas para Palermo Soho, Palermo Hollywood y Las Canitas.
- [x] Corrientes se representa como eje lineal claro entre 9 de Julio y Callao.
- [x] Abasto queda como area a reforzar separada del eje Corrientes.
- [x] Belgrano usa poligonos/areas orientadas por cuadras; Belgrano R queda acotado y no sobredimensionado.
- [x] San Telmo combina hito Mercado, eje Defensa y area gastronomica cercana sin circulos genericos.
- [x] Puerto Madero prioriza formas longitudinales orientadas a docks/rio.
- [x] Las etiquetas principales son legibles y no se detectan superposiciones fuertes en la hoja de contacto.
- [x] Los puntos de locales no son protagonistas: no se graficaron puntos de locales en esta pasada.
- [x] La lectura visual se acerca mas al ejemplo de Diego porque las zonas pasan de manchas a formas por calles, cuadras y ejes.

## QA editorial y privacidad

- [x] No se presentan subzonas como limites oficiales.
- [x] No se usa DataGastro como marca publica visible.
- [x] No se incluyen `place_id`, `rating`, `user_ratings_total`, raw JSON, rutas locales, API keys ni links privados en los mapas.
- [x] No se incluyen nombres de archivos CSV internos dentro de los mapas.
- [x] No se generaron capturas de Google Maps.
- [x] No se generaron datos de locales ni filas individuales sensibles.

## Alcance de ejecucion

- [x] No API.
- [x] No llamadas Google Places.
- [x] No scraping.
- [x] No PDF.
- [x] No datos fuente tocados.
- [x] No `data/` modificado.
- [x] No Cafecito, Mercados ni Casas de Pastas tocados.
- [x] No Borrador 2 ni Borrador 3 tocados.
- [x] No commit, push ni staging.

## Que mejora respecto al V4

- Palermo deja de apoyarse en elipses y usa recortes aproximados por avenidas.
- Corrientes queda como linea/eje y Abasto como area separada.
- Puerto Madero se lee como banda longitudinal y no como areas circulares.
- San Telmo y Belgrano reemplazan manchas genericas por piezas mas orientadas por cuadras.
- Los locales quedan fuera del mapa: la pieza queda mas limpia para revision institucional.

## Que sigue flojo o requiere decision

- Las geometrias siguen siendo editoriales y aproximadas; necesitan validacion humana antes de circular como PDF.
- Palermo podria requerir ajuste fino si Diego quiere incluir o excluir contexto Botanico/Palermo Chico.
- Abasto y Belgrano R siguen marcados como areas a reforzar; no conviene tratarlos como polos consolidados.
- Falta prueba de insercion en pagina A4 antes de recomendar PDF final.

## Recomendacion

Recomiendo pasar a una prueba PDF V5 solo despues de revision humana de estos cinco PNG/SVG. La base visual esta mejor encaminada que V4, pero conviene aprobar recortes y etiquetas antes de maquetar.
"""
    QA_DOC.write_text(content, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    write_geometry_csv()
    stats = build_maps()
    build_contact_sheet(stats)
    build_qa(stats)
    print(f"CSV: {GEOMETRIAS_CSV}")
    print(f"Contact sheet: {CONTACT_SHEET}")
    print(f"QA: {QA_DOC}")
    for page in DETAIL_ORDER:
        print(stats[page]["png"])
        print(stats[page]["svg"])


if __name__ == "__main__":
    main()
