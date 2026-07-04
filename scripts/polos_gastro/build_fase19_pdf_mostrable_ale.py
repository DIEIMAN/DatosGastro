"""Build PolosGastro phase 19 shown-to-Ale PDF.

This is a side-by-side, presentation-oriented phase. It reads only local
PolosGastro assets and writes only phase 19 docs/outputs. It does not call
APIs, scrape platforms, touch source data, stage changes, or modify previous
draft phases.
"""
from __future__ import annotations

import csv
import importlib.util
import math
import re
import shutil
import sys
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
from reportlab.lib.pagesizes import A4  # noqa: E402
from reportlab.pdfgen import canvas  # noqa: E402


ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs" / "polos_gastro" / "fase19_pdf_mostrable_ale"
OUT = ROOT / "outputs" / "polos_gastro" / "fase19_pdf_mostrable_ale"
ASSETS = OUT / "assets"
TABLES = OUT / "tablas"

CALLEJERO = ROOT / "outputs" / "polos_gastro" / "fase15_mapas_callejeros_v3" / "assets" / "callejero_gcba_2026_06_02.geojson"
BARRIOS = ROOT / "data" / "raw" / "geo_barrios.geojson"
GLOBAL_MAP = ROOT / "outputs" / "polos_gastro" / "fase15_mapas_callejeros_v3" / "assets" / "global_mapa_pdf_v3.png"

MD_BASE = DOCS / "INFORME_POLOS_GASTRO_DGDGAS_PDF_BASE_MOSTRABLE_ALE.md"
PDF_OUT = OUT / "INFORME_POLOS_GASTRO_DGDGAS_MOSTRABLE_ALE.pdf"
QA_DOC = DOCS / "QA_PDF_MOSTRABLE_ALE.md"
NOTE_DOC = DOCS / "NOTA_PARA_PRESENTAR_A_ALE.md"
GEOM_CSV = TABLES / "geometrias_mostrable_ale.csv"
CONTACT_SHEET = ASSETS / "contact_sheet_mapas_mostrable_ale.png"

SOURCE_V2_SCRIPT = ROOT / "scripts" / "polos_gastro" / "build_pdf_institucional_fase14_revision_visual.py"
spec = importlib.util.spec_from_file_location("fase14_v2", SOURCE_V2_SCRIPT)
v2 = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules["fase14_v2"] = v2
spec.loader.exec_module(v2)


INSTITUCION = "DGDGAS - Dirección General de Desarrollo Gastronómico"
GOBIERNO = "Gobierno de la Ciudad de Buenos Aires"
TITLE = "Polos gastronómicos de la Ciudad de Buenos Aires"
SUBTITLE = "Informe"
DATE_LABEL = "Julio 2026"

W, H = A4
M = 44
DETAIL_ORDER = ["palermo", "puerto", "san_telmo", "corrientes", "belgrano"]

AZUL = "#1F3B57"
VERDE = "#2F6E5B"
CELESTE = "#2C7FB8"
COBRE = "#C0762B"
SLATE = "#5E6B78"
ROJO = "#A23A2C"
GRIS = "#566573"
LINEA = "#DDE3E9"
SOFT_AZUL = "#EAF1F8"
SOFT_VERDE = "#EAF5EE"
SOFT_COBRE = "#F8EDE0"
SOFT_GRIS = "#F4F6F8"

MAP_OUTPUTS = {
    "palermo": "mapa_mostrable_palermo_las_canitas",
    "puerto": "mapa_mostrable_puerto_madero",
    "san_telmo": "mapa_mostrable_san_telmo",
    "corrientes": "mapa_mostrable_corrientes_abasto",
    "belgrano": "mapa_mostrable_belgrano",
}

MAP_CFG = {
    "palermo": {
        "title": "Palermo / Las Cañitas",
        "bbox": (-58.446, -34.596, -58.404, -34.560),
        "major": ["SANTA FE", "CORDOBA", "JUAN B. JUSTO", "SCALABRINI", "DORREGO", "DEL LIBERTADOR", "LUIS MARIA CAMPOS", "BAEZ", "CHENAUT", "ORTEGA"],
        "labels": [
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
        "labels": [
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
        "labels": [
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
        "labels": [
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
        "labels": [
            (-58.451, -34.556, "Juramento"),
            (-58.454, -34.559, "Mendoza"),
            (-58.441, -34.559, "Del Libertador"),
            (-58.458, -34.565, "Cabildo"),
        ],
    },
}


GEOMETRIES = [
    {
        "key": "palermo", "subzona": "Palermo Soho", "state": "consolidada", "shape": "polygon",
        "coords": [(-58.4330, -34.5824), (-58.4210, -34.5824), (-58.4210, -34.5924), (-58.4355, -34.5924), (-58.4330, -34.5824)],
        "label": "Palermo Soho", "tag": "SUBZONA APROX.", "color": CELESTE, "label_pos": (-58.4268, -34.5889), "label_width": 13,
        "criterio": "Av. Santa Fe, Av. Scalabrini Ortiz, Av. Cordoba y Av. Juan B. Justo.",
    },
    {
        "key": "palermo", "subzona": "Palermo Hollywood", "state": "consolidada", "shape": "polygon",
        "coords": [(-58.4440, -34.5780), (-58.4330, -34.5824), (-58.4355, -34.5924), (-58.4445, -34.5922), (-58.4440, -34.5780)],
        "label": "Palermo Hollywood", "tag": "SUBZONA APROX.", "color": VERDE, "label_pos": (-58.4382, -34.5866), "label_width": 12,
        "criterio": "Av. Juan B. Justo, Av. Santa Fe, Av. Dorrego y Av. Cordoba.",
    },
    {
        "key": "palermo", "subzona": "Las Cañitas", "state": "consolidada", "shape": "polygon",
        "coords": [(-58.4395, -34.5652), (-58.4295, -34.5630), (-58.4258, -34.5687), (-58.4325, -34.5735), (-58.4405, -34.5705), (-58.4395, -34.5652)],
        "label": "Las Cañitas", "tag": "SUBZONA APROX.", "color": COBRE, "label_pos": (-58.4342, -34.5685), "label_width": 12,
        "criterio": "Area Baez / Luis Maria Campos / Libertador / Ortega y Gasset o Chenaut.",
    },
    {
        "key": "puerto", "subzona": "Docks / eje costero", "state": "consolidada", "shape": "polygon",
        "coords": [(-58.3700, -34.5905), (-58.3592, -34.5905), (-58.3578, -34.6260), (-58.3662, -34.6272), (-58.3708, -34.6100), (-58.3700, -34.5905)],
        "label": "Docks", "tag": "AREA DE LECTURA", "color": CELESTE, "label_pos": (-58.3666, -34.6048), "label_width": 10,
        "criterio": "Banda longitudinal de docks entre frente de agua y corredor A. Moreau de Justo / Juana Manso.",
    },
    {
        "key": "puerto", "subzona": "Sector costero", "state": "consolidada", "shape": "line",
        "coords": [(-58.3600, -34.5940), (-58.3602, -34.6245)],
        "label": "Sector costero", "tag": "EJE APROX.", "color": COBRE, "label_pos": (-58.3570, -34.6118), "label_width": 10,
        "criterio": "Eje longitudinal paralelo al frente costero.",
    },
    {
        "key": "puerto", "subzona": "Faena / El Mercado", "state": "hito", "shape": "hito",
        "coords": [(-58.3642, -34.6172)],
        "label": "Faena / El Mercado", "tag": "HITO", "color": ROJO, "label_pos": (-58.3736, -34.6170), "label_width": 12,
        "criterio": "Hito de lectura; no local puntual ni limite oficial.",
    },
    {
        "key": "puerto", "subzona": "Dársena Sur", "state": "a_reforzar", "shape": "polygon",
        "coords": [(-58.3732, -34.6195), (-58.3658, -34.6196), (-58.3654, -34.6284), (-58.3736, -34.6282), (-58.3732, -34.6195)],
        "label": "Dársena Sur", "tag": "AREA A VALIDAR", "color": SLATE, "label_pos": (-58.3694, -34.6270), "label_width": 11,
        "criterio": "Area a validar para no sobredimensionar el sector sur.",
    },
    {
        "key": "san_telmo", "subzona": "Mercado de San Telmo", "state": "hito", "shape": "hito",
        "coords": [(-58.3730, -34.6218)],
        "label": "Mercado", "tag": "HITO COLECTIVO", "color": ROJO, "label_pos": (-58.3678, -34.6210), "label_width": 10,
        "criterio": "Hito colectivo; no restaurante puntual.",
    },
    {
        "key": "san_telmo", "subzona": "Casco historico / Defensa", "state": "consolidada", "shape": "line",
        "coords": [(-58.3732, -34.6185), (-58.3711, -34.6290)],
        "label": "Casco historico / Defensa", "tag": "EJE APROX.", "color": VERDE, "label_pos": (-58.3696, -34.6265), "label_width": 14,
        "criterio": "Eje Defensa y entorno patrimonial del casco.",
    },
    {
        "key": "san_telmo", "subzona": "Area gastronomica cercana", "state": "consolidada", "shape": "polygon",
        "coords": [(-58.3780, -34.6192), (-58.3700, -34.6192), (-58.3700, -34.6244), (-58.3780, -34.6244), (-58.3780, -34.6192)],
        "label": "Area gastronomica", "tag": "AREA DE LECTURA", "color": COBRE, "label_pos": (-58.3770, -34.6203), "label_width": 12,
        "criterio": "Area proxima a mercado, Chile, Estados Unidos y Defensa.",
    },
    {
        "key": "corrientes", "subzona": "Corrientes 9 de Julio-Callao", "state": "consolidada", "shape": "line",
        "coords": [(-58.3815, -34.6038), (-58.3928, -34.6043)],
        "label": "Corrientes 9 de Julio-Callao", "tag": "EJE APROX.", "color": CELESTE, "label_pos": (-58.3868, -34.6060), "label_width": 17,
        "criterio": "Av. Corrientes desde 9 de Julio hasta Callao.",
    },
    {
        "key": "corrientes", "subzona": "Obelisco / teatros", "state": "hito", "shape": "hito",
        "coords": [(-58.3812, -34.6038)],
        "label": "Obelisco / teatros", "tag": "NODO", "color": VERDE, "label_pos": (-58.3798, -34.6023), "label_width": 10,
        "criterio": "Nodo contextual acotado para ubicar el eje teatral.",
    },
    {
        "key": "corrientes", "subzona": "Abasto a reforzar", "state": "a_reforzar", "shape": "polygon",
        "coords": [(-58.4165, -34.5993), (-58.4050, -34.5993), (-58.4048, -34.6076), (-58.4167, -34.6076), (-58.4165, -34.5993)],
        "label": "Abasto a reforzar", "tag": "AREA A REFORZAR", "color": SLATE, "label_pos": (-58.4108, -34.6035), "label_width": 12,
        "criterio": "Area aproximada cinco cuadras alrededor del Abasto Shopping, separada de Corrientes.",
    },
    {
        "key": "belgrano", "subzona": "Barrio Chino", "state": "consolidada", "shape": "polygon",
        "coords": [(-58.4557, -34.5535), (-58.4480, -34.5535), (-58.4478, -34.5588), (-58.4552, -34.5593), (-58.4557, -34.5535)],
        "label": "Barrio Chino", "tag": "IDENTIDAD CLARA", "color": VERDE, "label_pos": (-58.4518, -34.5558), "label_width": 12,
        "criterio": "Entorno Arribenos, Juramento, Mendoza y vias.",
    },
    {
        "key": "belgrano", "subzona": "Bajo Belgrano", "state": "a_reforzar", "shape": "polygon",
        "coords": [(-58.4465, -34.5540), (-58.4368, -34.5542), (-58.4368, -34.5642), (-58.4462, -34.5648), (-58.4465, -34.5540)],
        "label": "Bajo Belgrano", "tag": "AREA A REVISAR", "color": SLATE, "label_pos": (-58.4416, -34.5596), "label_width": 12,
        "criterio": "Area aproximada hacia Bajo Belgrano, vinculada a Libertador y calles del entorno.",
    },
    {
        "key": "belgrano", "subzona": "Belgrano R a reforzar", "state": "a_reforzar", "shape": "polygon",
        "coords": [(-58.4660, -34.5588), (-58.4578, -34.5588), (-58.4578, -34.5662), (-58.4664, -34.5662), (-58.4660, -34.5588)],
        "label": "Belgrano R", "tag": "SUBZONA A REFORZAR", "color": SLATE, "label_pos": (-58.4622, -34.5626), "label_width": 12,
        "criterio": "Poligono chico y deliberadamente no sobredimensionado al oeste de Cabildo.",
    },
]

DETAIL_TEXT = {
    "palermo": {
        "page": 7,
        "title": "Palermo / Las Cañitas",
        "subtitle": "Tres subzonas principales como lectura inicial, sin sobrecargar contexto.",
        "reading": "El mapa separa Palermo Soho, Palermo Hollywood y Las Cañitas con poligonos apoyados en avenidas. Las menciones quedan fuera del mapa para sostener una lectura rapida.",
        "caution": "Subzonas aproximadas de lectura territorial. No son limites oficiales, padron operativo ni ranking gastronómico.",
    },
    "puerto": {
        "page": 8,
        "title": "Puerto Madero",
        "subtitle": "Lectura longitudinal de docks y frente costero.",
        "reading": "Puerto Madero se representa como banda de docks y eje costero. Faena / El Mercado funciona como hito de lectura, no como punto de oferta activa.",
        "caution": "Area de lectura aproximada. Las sedes a validar requieren confirmacion documental antes de cualquier uso operativo.",
    },
    "san_telmo": {
        "page": 9,
        "title": "San Telmo",
        "subtitle": "Mercado, eje Defensa y entorno gastronómico cercano.",
        "reading": "El Mercado de San Telmo se muestra como hito colectivo. Defensa y el casco historico ordenan la lectura territorial sin convertir la pagina en listado de locales.",
        "caution": "Area de lectura y eje aproximado. Los hitos colectivos no equivalen a restaurantes puntuales.",
    },
    "corrientes": {
        "page": 10,
        "title": "Corrientes / Abasto",
        "subtitle": "Eje y area vinculados, pero visualmente separados.",
        "reading": "Corrientes se presenta como eje teatral-gastronómico entre 9 de Julio y Callao. Abasto queda separado como area a reforzar alrededor del shopping.",
        "caution": "Vinculo, no continuidad. Abasto no se fusiona con Corrientes y debe validarse antes de tratarlo como polo propio.",
    },
    "belgrano": {
        "page": 11,
        "title": "Belgrano",
        "subtitle": "Macroarea con subzonas de respaldo desigual.",
        "reading": "Barrio Chino se muestra como la subzona mas clara. Bajo Belgrano y Belgrano R quedan con borde discontinuo como areas a revisar o reforzar.",
        "caution": "Belgrano R no se sobredimensiona ni se presenta como polo consolidado. Las subzonas son aproximaciones de lectura.",
    },
}


def ensure_dirs() -> None:
    DOCS.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)


def norm(value: str | None) -> str:
    return v2.norm(value or "")


def contains_any(value: str, patterns: list[str]) -> bool:
    value_norm = norm(value).upper()
    return any(norm(pattern).upper() in value_norm for pattern in patterns)


def line_buffer_polygon(points: list[tuple[float, float]], width: float = 0.00105) -> list[tuple[float, float]]:
    (x1, y1), (x2, y2) = points[0], points[-1]
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / length * width, dx / length * width
    return [(x1 + nx, y1 + ny), (x2 + nx, y2 + ny), (x2 - nx, y2 - ny), (x1 - nx, y1 - ny), (x1 + nx, y1 + ny)]


def shape_points(row: dict[str, object]) -> list[tuple[float, float]]:
    coords = row["coords"]
    if row["shape"] == "line":
        return line_buffer_polygon(coords)
    if row["shape"] == "hito":
        lon, lat = coords[0]
        size = 0.00135
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
    fields = ["mapa", "subzona", "estado_visual", "tipo_geometria", "criterio", "observacion"]
    with GEOM_CSV.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for row in GEOMETRIES:
            writer.writerow(
                {
                    "mapa": MAP_CFG[row["key"]]["title"],
                    "subzona": row["subzona"],
                    "estado_visual": row["state"],
                    "tipo_geometria": row["shape"],
                    "criterio": row["criterio"],
                    "observacion": "Subzona/eje aproximado de lectura; no limite oficial.",
                }
            )


def draw_street_context(ax, page: str, streets: gpd.GeoDataFrame, barrios: gpd.GeoDataFrame) -> None:
    cfg = MAP_CFG[page]
    minx, miny, maxx, maxy = cfg["bbox"]
    if cfg.get("water"):
        ax.add_patch(MplPolygon([(-58.3635, miny), (maxx, miny), (maxx, maxy), (-58.3635, maxy)], facecolor="#E6EDF3", edgecolor="none", alpha=0.92, zorder=0))
        ax.text(-58.3582, -34.608, "frente costero", rotation=90, fontsize=9.2, color="#5D7F98", ha="center", va="center", zorder=2)

    local_barrios = barrios.cx[minx:maxx, miny:maxy]
    if not local_barrios.empty:
        local_barrios.plot(ax=ax, facecolor="#F6F8FA", edgecolor="#D6DDE5", linewidth=0.50, zorder=1)

    local_streets = streets.cx[minx:maxx, miny:maxy]
    if local_streets.empty:
        return
    tipo = local_streets["tipo_c"].fillna("").str.upper()
    minor = local_streets[tipo != "AVENIDA"]
    avenues = local_streets[tipo == "AVENIDA"]
    if not minor.empty:
        minor.plot(ax=ax, color="#E8EDF1", linewidth=0.20, alpha=0.52, zorder=2)
    if not avenues.empty:
        avenues.plot(ax=ax, color="#D3DAE0", linewidth=0.62, alpha=0.76, zorder=3)
    major = local_streets[
        local_streets["nom_mapa"].fillna("").map(lambda value: contains_any(value, cfg["major"]))
        | local_streets["nomoficial"].fillna("").map(lambda value: contains_any(value, cfg["major"]))
    ]
    if not major.empty:
        major.plot(ax=ax, color="#8A97A3", linewidth=1.08, alpha=0.88, zorder=4)


def draw_street_labels(ax, labels: list[tuple[float, float, str]]) -> None:
    for lon, lat, label in labels:
        ax.text(
            lon,
            lat,
            label,
            fontsize=7.0,
            color="#667381",
            ha="center",
            va="center",
            bbox={"boxstyle": "round,pad=0.18", "fc": "white", "ec": "#DDE3EA", "lw": 0.42, "alpha": 0.84},
            zorder=8,
        )


def draw_label(ax, row: dict[str, object]) -> None:
    src_lon, src_lat = anchor_point(row)
    lon, lat = row.get("label_pos", (src_lon, src_lat))
    if (src_lon, src_lat) != (lon, lat):
        ax.plot([src_lon, lon], [src_lat, lat], color="#8A97A3", linewidth=0.75, alpha=0.85, zorder=8)
        ax.scatter([src_lon], [src_lat], s=10, color="#8A97A3", zorder=9)
    label = row["label"]
    tag = row["tag"]
    label_size = 12.2
    if len(label) > 18:
        label_size = 10.6
    if len(label) > 26:
        label_size = 9.3
    wrapped = textwrap.fill(label, width=int(row.get("label_width", 13)))
    ax.text(
        lon,
        lat,
        wrapped,
        fontsize=label_size,
        color=AZUL,
        ha="center",
        va="center",
        weight="bold",
        linespacing=0.82,
        bbox={"boxstyle": "round,pad=0.27", "fc": "white", "ec": "none", "alpha": 0.82},
        zorder=10,
    )
    cfg = MAP_CFG[row["key"]]
    minx, miny, maxx, maxy = cfg["bbox"]
    tag_y = lat - (maxy - miny) * (0.038 if "\n" not in wrapped else 0.062)
    ax.text(
        lon,
        tag_y,
        tag,
        fontsize=6.3,
        color="#4C5964" if row["state"] != "a_reforzar" else SLATE,
        ha="center",
        va="center",
        weight="bold",
        bbox={"boxstyle": "round,pad=0.15", "fc": "white", "ec": "none", "alpha": 0.72},
        zorder=11,
    )


def draw_geometries(ax, page: str) -> int:
    rows = [row for row in GEOMETRIES if row["key"] == page]
    for row in rows:
        color = row["color"]
        state = row["state"]
        if row["shape"] == "line":
            coords = row["coords"]
            ax.plot([coords[0][0], coords[-1][0]], [coords[0][1], coords[-1][1]], color=color, linewidth=10.0, alpha=0.22, solid_capstyle="round", zorder=5)
            ax.plot([coords[0][0], coords[-1][0]], [coords[0][1], coords[-1][1]], color=color, linewidth=2.1, alpha=0.95, solid_capstyle="round", zorder=6)
            ax.scatter([coords[0][0], coords[-1][0]], [coords[0][1], coords[-1][1]], s=16, color=color, zorder=7)
        elif row["shape"] == "hito":
            lon, lat = row["coords"][0]
            ax.add_patch(MplPolygon(shape_points(row), closed=True, facecolor=AZUL, edgecolor="white", linewidth=1.1, alpha=0.96, zorder=7))
        else:
            fill_alpha = 0.18 if state == "consolidada" else 0.10
            linestyle = "-" if state == "consolidada" else (0, (4, 3))
            edge_color = color if state == "consolidada" else SLATE
            poly = MplPolygon(
                shape_points(row),
                closed=True,
                facecolor=color,
                edgecolor=edge_color,
                alpha=fill_alpha,
                linewidth=1.9 if state == "consolidada" else 1.55,
                linestyle=linestyle,
                zorder=5,
            )
            ax.add_patch(poly)

    for row in rows:
        draw_label(ax, row)
    return len(rows)


def render_map(page: str, streets: gpd.GeoDataFrame, barrios: gpd.GeoDataFrame) -> dict[str, Path | int]:
    cfg = MAP_CFG[page]
    minx, miny, maxx, maxy = cfg["bbox"]
    fig, ax = plt.subplots(figsize=(8.0, 6.0), dpi=230)
    ax.set_facecolor("#FAFBFC")
    draw_street_context(ax, page, streets, barrios)
    count = draw_geometries(ax, page)
    draw_street_labels(ax, cfg["labels"])

    legend_handles = [
        Line2D([0], [0], color=CELESTE, lw=7, alpha=0.34, label="subzona aproximada"),
        Line2D([0], [0], color=SLATE, lw=2.0, linestyle=(0, (4, 3)), label="area a reforzar / validar"),
        Line2D([0], [0], color="#8A97A3", lw=1.4, label="avenidas de referencia"),
    ]
    ax.legend(handles=legend_handles, loc="lower left", fontsize=7.6, frameon=True, framealpha=0.94, facecolor="white", edgecolor="#DDE3E9")

    ax.set_xlim(minx, maxx)
    ax.set_ylim(miny, maxy)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_edgecolor("#DDE3E9")
        spine.set_linewidth(0.8)
    ax.set_title(cfg["title"], loc="left", color=AZUL, fontweight="bold", fontsize=16, pad=10)
    fig.text(0.04, 0.045, "Referencia territorial - subzonas aproximadas - no delimita oficialmente polos", fontsize=8.0, color=ROJO, ha="left")
    fig.text(0.965, 0.028, INSTITUCION, fontsize=8.0, color=GRIS, ha="right")
    fig.text(0.965, 0.014, "Base: Callejero GCBA", fontsize=7.4, color=GRIS, ha="right")
    fig.subplots_adjust(left=0.035, right=0.985, top=0.905, bottom=0.130)

    base = MAP_OUTPUTS[page]
    png = ASSETS / f"{base}.png"
    svg = ASSETS / f"{base}.svg"
    fig.savefig(png, dpi=230)
    fig.savefig(svg)
    plt.close(fig)
    return {"png": png, "svg": svg, "geometrias": count}


def build_maps() -> dict[str, Path]:
    streets = gpd.read_file(CALLEJERO)
    barrios = gpd.read_file(BARRIOS)
    maps = {"global": ASSETS / "global_mapa_pdf_mostrable_ale.png"}
    shutil.copyfile(GLOBAL_MAP, maps["global"])
    for page in DETAIL_ORDER:
        result = render_map(page, streets, barrios)
        maps[page] = result["png"]
    return maps


def build_contact_sheet() -> None:
    thumbs: list[tuple[str, Image.Image]] = []
    for page in DETAIL_ORDER:
        img = Image.open(ASSETS / f"{MAP_OUTPUTS[page]}.png").convert("RGB")
        img.thumbnail((760, 570), Image.Resampling.LANCZOS)
        thumbs.append((MAP_CFG[page]["title"], img))
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
    draw.text((margin, 18), "Mapas mostrables para Ale - DGDGAS", fill=AZUL, font=title_font)
    for idx, (title, img) in enumerate(thumbs):
        col = idx % 2
        row = idx // 2
        x = margin + col * (cell_w + margin)
        y = title_h + margin + row * cell_h
        draw.text((x, y), title, fill=AZUL, font=label_font)
        sheet.paste(img, (x, y + label_h))
    draw.text((margin, sheet.height - 28), "Referencia territorial - no delimita oficialmente polos", fill=GRIS, font=note_font)
    sheet.save(CONTACT_SHEET)


def configure_pdf_module() -> None:
    v2.DOCS_OUT = DOCS
    v2.OUT = OUT
    v2.ASSETS = ASSETS
    v2.MENTIONS_CSV = TABLES / "menciones_destacadas_por_polo_mostrable_ale.csv"
    v2.PDF = PDF_OUT
    v2.MD_BASE = MD_BASE
    v2.INSTITUCION = INSTITUCION
    v2.GOBIERNO = GOBIERNO
    v2.TITLE = TITLE
    v2.SUBTITLE = SUBTITLE
    v2.register_fonts()


def cover(c: canvas.Canvas) -> None:
    c.setFillColorRGB(31 / 255, 59 / 255, 87 / 255)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColorRGB(162 / 255, 58 / 255, 44 / 255)
    c.rect(0, 0, 16, H, fill=1, stroke=0)
    c.setFillColorRGB(1, 1, 1)
    c.setFont(v2.FONT_BOLD, 29)
    y = H - 190
    for line in v2.wrap_text(TITLE, v2.FONT_BOLD, 29, W - 2 * M - 20):
        c.drawString(M + 8, y, line)
        y -= 35
    c.setFont(v2.FONT_BOLD, 18)
    c.drawString(M + 8, y - 12, "Informe")
    c.setFont(v2.FONT, 12)
    c.drawString(M + 8, y - 60, INSTITUCION)
    c.drawString(M + 8, y - 78, GOBIERNO)
    c.drawString(M + 8, y - 112, DATE_LABEL)
    c.showPage()


def summary_page(c: canvas.Canvas) -> None:
    y = v2.header(c, 3, "Resumen ejecutivo", "Una lectura territorial inicial para ordenar el universo semilla de polos gastronómicos de la Ciudad.")
    paragraphs = [
        "Este informe organiza un universo semilla de 22 polos y ejes gastronómicos de la Ciudad de Buenos Aires, con el objetivo de aportar una lectura territorial inicial para conversacion institucional, validacion interna y priorizacion de proximos pasos.",
        "La pieza combina un mapa global de referencia, mapas de detalle por zonas seleccionadas y menciones destacadas del universo semilla. Las areas representadas son aproximaciones de lectura territorial: no constituyen limites oficiales, padron de locales ni ranking gastronómico.",
        "El valor principal del informe es ordenar criterios: que zonas aparecen mas consolidadas, que ejes requieren validacion adicional y que decisiones conviene cerrar antes de avanzar hacia una version final o de uso operativo.",
    ]
    yy = y - 12
    for paragraph in paragraphs:
        yy = v2.draw_wrapped(c, paragraph, M, yy, W - 2 * M, font=v2.FONT, size=10.6, color=v2.NEGRO, leading=14.2)
        yy -= 12
    v2.note_box(
        c,
        M,
        132,
        W - 2 * M,
        132,
        "Para validar con Ale",
        "1. Criterio de lectura para Corrientes y Abasto.\n2. Tratamiento de Belgrano como macroarea con subzonas.\n3. Nivel de detalle deseado en mapas.\n4. Ubicacion de recomendaciones en cuerpo o anexo.",
        color=AZUL,
        fill=SOFT_AZUL,
        size=9.1,
    )
    v2.finish(c)


def territorial_page(c: canvas.Canvas) -> None:
    y = v2.header(c, 6, "Lectura territorial general", "Como leer las zonas de detalle")
    v2.note_box(c, M, y - 84, W - 2 * M, 70, "Criterio visual",
                "Los mapas priorizan zonas coloreadas, ejes aproximados y etiquetas grandes. El callejero queda como soporte suave para orientar la lectura.", color=CELESTE, fill=SOFT_AZUL)
    v2.note_box(c, M, y - 172, W - 2 * M, 76, "Criterio territorial",
                "Corrientes y Abasto se mantienen vinculados pero separados. Belgrano se lee como macroarea con Barrio Chino, Bajo Belgrano y Belgrano R en distinto grado de respaldo.", color=VERDE, fill=SOFT_VERDE)
    v2.note_box(c, M, y - 266, W - 2 * M, 82, "Uso previsto",
                "La version es mostrable para conversacion institucional. Sirve para ordenar decisiones, no para publicar limites ni operar un padron.", color=COBRE, fill=SOFT_COBRE)
    v2.bullet_list(c, [
        "Mapa global: lectura del universo semilla completo.",
        "Mapas de detalle: lectura territorial por subzona, eje o area a reforzar.",
        "Menciones destacadas: referencias del universo semilla en cajas laterales, sin ranking.",
    ], M, 235, W - 2 * M, gap=10)
    v2.finish(c)


def detail_page(c: canvas.Canvas, page: str, maps: dict[str, Path], mentions: list[dict[str, str]]) -> None:
    cfg = DETAIL_TEXT[page]
    v2.header(c, cfg["page"], "Detalle territorial", cfg["title"], cfg["subtitle"])
    map_x, map_y, map_w, map_h = M, 314, 344, 344
    side_x = M + 358
    side_w = W - M - side_x
    v2.image_box(c, maps[page], map_x, map_y, map_w, map_h, border=True)
    v2.note_box(c, side_x, 474, side_w, 184, "Menciones destacadas",
                v2.visible_mentions(mentions, page), color=CELESTE, fill=SOFT_AZUL, size=7.1)
    v2.note_box(c, side_x, 314, side_w, 142, "Lectura",
                cfg["reading"], color=VERDE, fill=SOFT_VERDE, size=7.45)
    v2.note_box(c, M, 144, W - 2 * M, 90, "Nota de cautela",
                cfg["caution"], color=COBRE, fill=SOFT_COBRE, size=8.6)
    v2.draw_wrapped(c, "Referencia territorial - no delimita oficialmente polos. No es ranking, padron ni validacion definitiva.", M, 116, W - 2 * M, font=v2.FONT_BOLD, size=8.4, color=GRIS, leading=10)
    v2.finish(c)


def mentions_criteria_page(c: canvas.Canvas, mentions: list[dict[str, str]]) -> None:
    y = v2.header(c, 12, "Criterio de menciones", "Como se leen las referencias visibles")
    v2.note_box(c, M, y - 82, W - 2 * M, 72, "Alcance",
                "Las menciones visibles provienen del universo semilla y se presentan como referencias para conversacion territorial. No son recomendacion comercial, orden de merito ni listado exhaustivo.", color=AZUL, fill=SOFT_AZUL)
    v2.note_box(c, M, y - 174, W - 2 * M, 78, "Tratamiento prudente",
                "Las sedes o hitos a validar se separan de las menciones con mayor respaldo. Los casos con vigencia no confirmada, duplicados o busquedas a corregir no se convierten en oferta activa.", color=COBRE, fill=SOFT_COBRE)
    v2.bullet_list(c, [
        "Los nombres de locales no se colocan dentro del mapa para evitar saturacion visual.",
        "Los hitos colectivos se tratan como referencia territorial, no como restaurante puntual.",
        "Antes de una version final conviene validar vigencia, sedes, cadenas y duplicados.",
    ], M, y - 235, W - 2 * M, gap=10)
    v2.finish(c)


def auxiliary_page(c: canvas.Canvas) -> None:
    y = v2.header(c, 13, "Hallazgos y cautelas", "Que habilita esta version")
    v2.note_box(c, M, y - 78, W - 2 * M, 66, "Hallazgo principal",
                "La lectura territorial permite distinguir zonas de mayor consolidacion visual y areas que necesitan decision humana antes de circular como pieza final.", color=VERDE, fill=SOFT_VERDE)
    v2.note_box(c, M, y - 164, W - 2 * M, 70, "Limite metodologico",
                "La cartografia acompana una conversacion institucional. No valida actividad vigente, no define limites oficiales y no reemplaza trabajo de campo ni fuentes oficiales.", color=COBRE, fill=SOFT_COBRE)
    v2.note_box(c, M, y - 254, W - 2 * M, 72, "Decision pendiente",
                "Abasto, Belgrano R y Bajo Belgrano deben conservarse como areas a reforzar hasta contar con una definicion institucional o evidencia adicional.", color=AZUL, fill=SOFT_AZUL)
    v2.bullet_list(c, [
        "Palermo es el mapa mas cuidado y funciona como referencia de estilo.",
        "Corrientes y Abasto quedan diferenciados en una misma pagina.",
        "Belgrano muestra jerarquia: Barrio Chino mas claro; Belgrano R y Bajo Belgrano a reforzar.",
    ], M, 226, W - 2 * M, gap=10)
    v2.finish(c)


def pending_page(c: canvas.Canvas) -> None:
    y = v2.header(c, 14, "Decisiones pendientes", "Que cerrar con Ale")
    v2.bullet_list(c, [
        "Corrientes y Abasto: confirmar que se leen como vinculados pero separados.",
        "Abasto: definir si queda en esta pagina o requiere pagina propia.",
        "Belgrano: validar macroarea con Barrio Chino, Bajo Belgrano y Belgrano R a reforzar.",
        "Mapas: definir si la version final conserva zonas, suma puntos o mantiene solo menciones laterales.",
        "Recomendaciones: decidir si quedan en cuerpo o pasan a anexo.",
    ], M, y - 10, W - 2 * M, gap=12)
    v2.note_box(c, M, 134, W - 2 * M, 88, "Criterio recomendado",
                "Mostrar esta version como insumo de decision, no como cierre metodologico. La aprobacion debe concentrarse en recortes, jerarquia de subzonas y densidad visual deseada.", color=AZUL, fill=SOFT_AZUL)
    v2.finish(c)


def recommendations_page(c: canvas.Canvas) -> None:
    y = v2.header(c, 15, "Recomendaciones", "Uso institucional de la pieza")
    v2.note_box(c, M, y - 76, W - 2 * M, 62, "Para la reunion",
                "Usar el PDF para conversar criterio territorial y no para aprobar limites definitivos.", color=AZUL, fill=SOFT_AZUL)
    v2.note_box(c, M, y - 156, W - 2 * M, 62, "Para version final",
                "Mantener cautelas visibles y resolver previamente sedes a validar, duplicados y tratamiento de subzonas debiles.", color=VERDE, fill=SOFT_VERDE)
    v2.note_box(c, M, y - 236, W - 2 * M, 62, "Para circulacion",
                "Evitar lenguaje de ranking, censo o validacion definitiva. Mantener una unica marca publica: DGDGAS.", color=COBRE, fill=SOFT_COBRE)
    v2.bullet_list(c, [
        "Conservar el mapa global como lectura del universo semilla.",
        "Mantener nombres de locales fuera de los mapas salvo decision expresa.",
        "Documentar cambios si Ale ajusta recortes o prioridades.",
    ], M, 242, W - 2 * M, gap=10)
    v2.finish(c)


def annex_method(c: canvas.Canvas) -> None:
    y = v2.header(c, 18, "Anexo B", "Criterio cartografico y limitaciones")
    v2.bullet_list(c, [
        "El mapa global representa areas, macroareas, ejes o zonas aproximadas del universo semilla.",
        "Los mapas de detalle usan Callejero GCBA como base visual y subzonas editoriales aproximadas.",
        "Las geometrias se construyeron como lectura por avenidas, cuadras y ejes; no son limites oficiales.",
        "Los hitos colectivos se tratan como referencia territorial, no como restaurante puntual.",
        "Los casos con vigencia no confirmada, duplicados o busquedas a corregir no se presentan como oferta activa.",
    ], M, y - 10, W - 2 * M, gap=8.5)
    v2.note_box(c, M, 120, W - 2 * M, 98, "Fuente cartografica",
                "Base callejera: dataset publico Calles / Callejero (GeoJson), Buenos Aires Data - GCBA. Licencia CC-BY-2.5-AR. Actualizacion publicada por el portal: 2 de junio de 2026. Descarga local ya disponible en el proyecto.", color=CELESTE, fill=SOFT_AZUL, size=8.1)
    v2.finish(c)


def annex_universe(c: canvas.Canvas) -> None:
    v2.header(c, 17, "Anexo A", "Universo semilla de 22 polos/ejes")
    rows = [
        ("Palermo", "Polo consolidado con subpolos", "19"),
        ("Villa Crespo", "Polo de barrio", "9"),
        ("Puerto Madero", "Polo consolidado costero", "9"),
        ("San Telmo", "Polo consolidado con hito colectivo", "8"),
        ("Chacarita", "Polo de barrio", "7"),
        ("Belgrano", "Macroarea con subzonas", "11"),
        ("Recoleta", "Polo de barrio", "8"),
        ("Caballito", "Polo de barrio", "5"),
        ("Costanera Norte", "Corredor / area costera", "6"),
        ("Avenida Caseros / Barracas", "Corredor / eje", "5"),
        ("Microcentro y Centro", "Area central", "7"),
        ("Avenida Corrientes", "Eje cultural-gastronomico", "6"),
        ("Abasto", "Subzona vinculada a Corrientes", "6"),
        ("Avenida Boedo", "Corredor / eje", "0"),
        ("Devoto", "Polo de barrio", "0"),
        ("Corredor DoHo / Donado-Holmberg", "Corredor / eje", "0"),
        ("Villa Urquiza", "Polo de barrio", "0"),
        ("Nuevo Bajo Retiro / Esmeralda y Paraguay", "Subzona central", "0"),
        ("Avenida Federico Lacroze", "Corredor / eje", "0"),
        ("Parque Saavedra / Av. Garcia del Rio", "Zona / corredor barrial", "0"),
        ("Circuito gastronomico de Paternal", "Area a validar", "0"),
        ("Villa Pueyrredon / Av. San Martin", "Barrio / corredor", "0"),
    ]
    x, y = M, H - 136
    col_w = [214, 216, 74]
    row_h = 19
    v2.set_fill(c, AZUL)
    c.rect(x, y, sum(col_w), row_h, fill=1, stroke=0)
    v2.set_fill(c, "#FFFFFF")
    c.setFont(v2.FONT_BOLD, 7.9)
    c.drawString(x + 6, y + 6, "Polo/eje")
    c.drawString(x + col_w[0] + 6, y + 6, "Tipo de lectura")
    c.drawRightString(x + sum(col_w) - 6, y + 6, "Menciones")
    y -= row_h
    c.setFont(v2.FONT, 7.1)
    for idx, row in enumerate(rows):
        v2.set_fill(c, "#FFFFFF" if idx % 2 == 0 else "#F7F9FB")
        c.rect(x, y, sum(col_w), row_h, fill=1, stroke=0)
        v2.set_stroke(c, LINEA)
        c.rect(x, y, sum(col_w), row_h, fill=0, stroke=1)
        v2.set_fill(c, v2.NEGRO)
        c.drawString(x + 6, y + 6, row[0])
        c.drawString(x + col_w[0] + 6, y + 6, row[1])
        c.drawRightString(x + sum(col_w) - 6, y + 6, row[2])
        y -= row_h
    v2.note_box(c, M, 88, W - 2 * M, 56, "Nota",
                "Los polos con cero menciones explicitas permanecen en el universo semilla y se representan en el mapa global como areas o ejes a fortalecer.",
                color=CELESTE, fill=SOFT_AZUL, size=8.2)
    v2.finish(c)


def build_pdf(maps: dict[str, Path], mentions: list[dict[str, str]]) -> None:
    c = canvas.Canvas(str(PDF_OUT), pagesize=A4)
    c.setTitle(TITLE)
    c.setAuthor(INSTITUCION)
    cover(c)
    v2.index_page(c)
    summary_page(c)
    v2.scope_page(c)
    v2.global_map_page(c, maps)
    territorial_page(c)
    for page in DETAIL_ORDER:
        detail_page(c, page, maps, mentions)
    mentions_criteria_page(c, mentions)
    auxiliary_page(c)
    pending_page(c)
    recommendations_page(c)
    v2.next_steps_page(c)
    annex_universe(c)
    annex_method(c)
    c.save()


def build_markdown(mentions: list[dict[str, str]]) -> None:
    def md_mentions(page: str) -> str:
        text = v2.visible_mentions(mentions, page)
        return "\n".join(f"- {line}" for line in text.splitlines() if line.strip())

    content = f"""# Polos gastronómicos de la Ciudad de Buenos Aires

## Informe

**{INSTITUCION}**  
**{GOBIERNO}**  
Fecha de elaboracion: julio de 2026

Este documento es la base editorial de la version PDF mostrable para Ale. Ordena el universo semilla de 22 polos/ejes gastronómicos de la Ciudad, mantiene el mapa global como pieza principal y mejora los cinco mapas de detalle con zonas coloreadas, ejes aproximados y menciones destacadas en cajas laterales.

No constituye padron oficial, ranking, censo gastronómico ni confirmacion de actividad vigente. Las subzonas son aproximaciones de lectura territorial.

## 1. Resumen ejecutivo

Este informe organiza un universo semilla de 22 polos y ejes gastronómicos de la Ciudad de Buenos Aires, con el objetivo de aportar una lectura territorial inicial para conversacion institucional, validacion interna y priorizacion de proximos pasos.

La pieza combina un mapa global de referencia, mapas de detalle por zonas seleccionadas y menciones destacadas del universo semilla. Las areas representadas son aproximaciones de lectura territorial: no constituyen limites oficiales, padron de locales ni ranking gastronómico.

El valor principal del informe es ordenar criterios: que zonas aparecen mas consolidadas, que ejes requieren validacion adicional y que decisiones conviene cerrar antes de avanzar hacia una version final o de uso operativo.

Para validar con Ale:
- criterio de lectura para Corrientes y Abasto;
- tratamiento de Belgrano como macroarea con subzonas;
- nivel de detalle deseado en mapas;
- ubicacion de recomendaciones en cuerpo o anexo.

## 2. Alcance y criterio de lectura

El universo semilla es un insumo de trabajo. Las menciones destacadas no son ranking, no son recomendacion comercial y no equivalen a padron de locales activos.

Las subzonas son aproximaciones editoriales construidas para facilitar la lectura territorial. No son limites oficiales, poligonos normativos ni delimitaciones cerradas.

## 3. Mapa global de 22 polos/ejes

El mapa global se conserva como mapa principal. Representa areas, ejes y zonas de lectura territorial del universo semilla, sin definir limites oficiales.

## 4. Lectura territorial general

Palermo concentra el mayor volumen de menciones y requiere distinguir subzonas internas. Puerto Madero se lee mejor como banda de docks y eje costero. San Telmo se entiende a partir del Mercado y el casco historico. Corrientes y Abasto se mantienen vinculados pero diferenciados. Belgrano se presenta como macroarea con subzonas de respaldo desigual.

## 5. Detalles territoriales

### Palermo / Las Cañitas

{md_mentions("palermo")}

Lectura: se distinguen Palermo Soho, Palermo Hollywood y Las Cañitas como subzonas aproximadas. Las menciones quedan en caja lateral.

### Puerto Madero

{md_mentions("puerto")}

Lectura: el mapa prioriza docks, eje costero, Faena / El Mercado como hito y Dársena Sur como area a validar.

### San Telmo

{md_mentions("san_telmo")}

Lectura: el Mercado de San Telmo se trata como hito colectivo. El casco historico y el eje Defensa ordenan la pieza.

### Corrientes / Abasto

{md_mentions("corrientes")}

Lectura: Corrientes es eje teatral-gastronómico 9 de Julio-Callao. Abasto se presenta como area a reforzar alrededor del shopping y no se fusiona con Corrientes.

### Belgrano

{md_mentions("belgrano")}

Lectura: Barrio Chino tiene identidad gastronomica clara; Bajo Belgrano conserva sedes a validar; Belgrano R queda como subzona a reforzar.

## 6. Fuente cartografica y geometrias

Base callejera usada: **Calles / Callejero (GeoJson)** de Buenos Aires Data - GCBA. Licencia **CC-BY-2.5-AR**. Fecha de actualizacion publicada por el portal: **2 de junio de 2026**. Descarga local ya disponible en el proyecto.

Las geometrias editoriales se documentan en la tabla de esta fase. Fueron armadas con callejero, referencias urbanas y criterio editorial documentado.

## 7. Decisiones pendientes

- Validar con Ale el recorte de Corrientes y Abasto.
- Definir si Belgrano R queda visible en la version final o solo como nota de trabajo.
- Resolver sedes, cadenas y duplicados antes de cualquier mapa operativo.
- Ajustar paleta y cantidad de etiquetas si la pieza final requiere mayor sobriedad.

## 8. Recomendaciones prudentes

- Usar el mapa global como lectura institucional del universo semilla.
- Usar los mapas editoriales como apoyo visual de conversacion, no como padron operativo.
- Mantener separadas las menciones incluidas, las sedes a validar y los casos excluidos por prudencia.
- Validar territorialmente antes de publicar detalle operativo.

## 9. Proximos pasos

1. Revisar con Ale delimitaciones, sedes y criterios de publicacion.
2. Ajustar mapas finales segun definiciones territoriales.
3. Definir si las recomendaciones quedan en cuerpo o anexo.
4. Generar la version final despues de cerrar decisiones.

## Anexos

La tabla de menciones destacadas y la tabla de geometrias quedan como respaldo en los outputs de esta fase.
"""
    MD_BASE.write_text(content, encoding="utf-8")


def build_note_for_ale() -> None:
    content = """# Nota para presentar a Ale

Esta version es mostrable, no final. Sirve para conversar criterio territorial, no para aprobar limites oficiales ni publicar un padron.

El universo semilla ya esta ordenado. Los mapas son una lectura territorial aproximada: ayudan a ver zonas, ejes y areas a reforzar, pero no son delimitaciones oficiales.

Las menciones no son ranking ni recomendacion comercial. Funcionan como referencias del universo semilla y quedan fuera del mapa para sostener legibilidad.

Decisiones a validar con Ale:

1. Corrientes y Abasto: vinculados pero separados.
2. Belgrano: macroarea con Barrio Chino, Bajo Belgrano y Belgrano R a reforzar.
3. Nivel de detalle de mapas: zonas, puntos o nombres.
4. Si las recomendaciones quedan en cuerpo o anexo.
"""
    NOTE_DOC.write_text(content, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    configure_pdf_module()
    mentions = v2.build_mentions()
    write_geometry_csv()
    maps = build_maps()
    build_contact_sheet()
    build_markdown(mentions)
    build_pdf(maps, mentions)
    build_note_for_ale()
    print(f"PDF: {PDF_OUT}")
    print(f"Markdown: {MD_BASE}")
    print(f"Nota Ale: {NOTE_DOC}")
    print(f"Contact sheet: {CONTACT_SHEET}")


if __name__ == "__main__":
    main()
