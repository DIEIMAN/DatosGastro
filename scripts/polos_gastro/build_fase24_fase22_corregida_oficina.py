# -*- coding: utf-8 -*-
"""Fase24: version de oficina corregida partiendo de fase22 (NO de fase23).

Alcance:
- Reconstruye el PDF de 11 paginas con el layout de fase22 (heredado de fase20)
  y los textos finales de fase22, corrigiendo el encoding de acentos que en
  fase22 quedaron como "?" en el texto del PDF.
- Regenera los 5 mapas de detalle con la misma configuracion visual de los
  assets de fase20 (los que usa fase22), aplicando solo microajustes:
  tildes internas, etiquetas superpuestas y rotulos pegados a bordes.
- Regenera el mapa global (fase13 + recorte fase14) separando las etiquetas
  "Abasto"/"Corrientes" y "DoHo"/"Villa Urquiza".

No usa APIs, no usa Google Places, no hace scraping, no toca datos fuente,
no modifica fases anteriores. Solo lee assets locales y escribe en fase24.
"""
from __future__ import annotations

import importlib.util
import math
import sys
import textwrap
from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "none"
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch, Polygon as MplPolygon  # noqa: E402
from PIL import Image  # noqa: E402
from reportlab.lib.pagesizes import A4  # noqa: E402
from reportlab.lib.utils import ImageReader  # noqa: E402
from reportlab.pdfbase import pdfmetrics  # noqa: E402
from reportlab.pdfbase.ttfonts import TTFont  # noqa: E402
from reportlab.pdfgen import canvas  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs" / "polos_gastro" / "fase24_fase22_corregida_oficina"
ASSETS = OUT / "assets"
PDF_OUT = OUT / "INFORME_POLOS_GASTRO_DGDGAS_11P_OFICINA_FASE24.pdf"

CALLEJERO = ROOT / "outputs" / "polos_gastro" / "fase15_mapas_callejeros_v3" / "assets" / "callejero_gcba_2026_06_02.geojson"
BARRIOS = ROOT / "data" / "raw" / "geo_barrios.geojson"

FASE13_SCRIPT = ROOT / "scripts" / "polos_gastro" / "generar_mapas_fase13.py"

W, H = A4
M = 44
TOTAL_PAGES = 11

TITLE = "Polos gastronómicos de la Ciudad de Buenos Aires"
SUBTITLE = "Informe"
INSTITUCION = "DGDGAS — Dirección General de Desarrollo Gastronómico"
GOBIERNO = "Gobierno de la Ciudad de Buenos Aires"
DATE_LABEL = "Julio 2026"

AZUL = "#1F3B57"
ROJO = "#A23A2C"
VERDE = "#2F6E5B"
CELESTE = "#2C7FB8"
COBRE = "#C0762B"
SLATE = "#5E6B78"
GRIS = "#566573"
NEGRO = "#1E252B"
LINEA = "#DDE3E9"
SOFT_AZUL = "#EAF1F8"
SOFT_VERDE = "#EAF5EE"
SOFT_COBRE = "#F8EDE0"
WHITE = "#FFFFFF"

FONT = "Arial"
FONT_BOLD = "Arial-Bold"

# Relacion de aspecto de los mapas de detalle de fase20/fase22 (lon/lat CABA).
MAP_ASPECT = 1.0 / math.cos(math.radians(34.6))

MAP_OUTPUTS = {
    "palermo": "mapa_fase24_palermo_las_canitas",
    "puerto": "mapa_fase24_puerto_madero",
    "san_telmo": "mapa_fase24_san_telmo",
    "corrientes": "mapa_fase24_corrientes_abasto",
    "belgrano": "mapa_fase24_belgrano",
}

DETAIL_ORDER = ["palermo", "puerto", "san_telmo", "corrientes", "belgrano"]

# Configuracion identica a los assets de fase20 usados por fase22, con
# microajustes documentados en CAMBIOS_FASE22_A_FASE24.md:
# - tildes en rotulos internos (Av. Córdoba, Paseo Colón, Área, histórico);
# - etiquetas de calles corridas para no quedar tapadas por rotulos de zona;
# - rotulo "Dársena Sur" separado de la leyenda (pagina 8);
# - rotulo vertical "frente costero" fuera de la banda de docks (pagina 8);
# - se quita la etiqueta chica duplicada "Abasto" (pagina 10).
MAP_CFG = {
    "palermo": {
        "title": "Palermo / Las Cañitas",
        "bbox": (-58.446, -34.596, -58.404, -34.560),
        "major": ["SANTA FE", "CORDOBA", "JUAN B. JUSTO", "SCALABRINI", "DORREGO", "DEL LIBERTADOR", "LUIS MARIA CAMPOS", "BAEZ", "CHENAUT", "ORTEGA"],
        "labels": [
            (-58.424, -34.5818, "Av. Santa Fe"),
            (-58.4176, -34.5930, "Av. Córdoba"),
            (-58.4332, -34.5837, "Juan B. Justo"),
            (-58.4124, -34.5899, "Scalabrini Ortiz"),
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
            (-58.3794, -34.6186, "Chile"),
            (-58.367, -34.624, "Paseo Colón"),
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
        ],
    },
    "belgrano": {
        "title": "Belgrano",
        "bbox": (-58.467, -34.568, -58.436, -34.548),
        "major": ["JURAMENTO", "MENDOZA", "OLAZABAL", "ARRIBENOS", "MONTA", "DEL LIBERTADOR", "CABILDO", "LA PAMPA", "MIGUELETES"],
        "labels": [
            (-58.4581, -34.5528, "Juramento"),
            (-58.454, -34.559, "Mendoza"),
            (-58.4408, -34.5507, "Del Libertador"),
            (-58.458, -34.565, "Cabildo"),
        ],
    },
}

GEOMETRIES = [
    {
        "key": "palermo", "subzona": "Palermo Soho", "state": "consolidada", "shape": "polygon",
        "coords": [(-58.4330, -34.5824), (-58.4210, -34.5824), (-58.4210, -34.5924), (-58.4355, -34.5924), (-58.4330, -34.5824)],
        "label": "Palermo Soho", "tag": "SUBZONA APROX.", "color": CELESTE, "label_pos": (-58.4268, -34.5889), "label_width": 13,
    },
    {
        "key": "palermo", "subzona": "Palermo Hollywood", "state": "consolidada", "shape": "polygon",
        "coords": [(-58.4440, -34.5780), (-58.4330, -34.5824), (-58.4355, -34.5924), (-58.4445, -34.5922), (-58.4440, -34.5780)],
        "label": "Palermo Hollywood", "tag": "SUBZONA APROX.", "color": VERDE, "label_pos": (-58.4382, -34.5866), "label_width": 12,
    },
    {
        "key": "palermo", "subzona": "Las Cañitas", "state": "consolidada", "shape": "polygon",
        "coords": [(-58.4395, -34.5652), (-58.4295, -34.5630), (-58.4258, -34.5687), (-58.4325, -34.5735), (-58.4405, -34.5705), (-58.4395, -34.5652)],
        "label": "Las Cañitas", "tag": "SUBZONA APROX.", "color": COBRE, "label_pos": (-58.4342, -34.5685), "label_width": 12,
    },
    {
        "key": "puerto", "subzona": "Docks / eje costero", "state": "consolidada", "shape": "polygon",
        "coords": [(-58.3700, -34.5905), (-58.3592, -34.5905), (-58.3578, -34.6260), (-58.3662, -34.6272), (-58.3708, -34.6100), (-58.3700, -34.5905)],
        "label": "Docks", "tag": "ÁREA DE LECTURA", "color": CELESTE, "label_pos": (-58.3666, -34.6048), "label_width": 10,
    },
    {
        "key": "puerto", "subzona": "Sector costero", "state": "consolidada", "shape": "line",
        "coords": [(-58.3600, -34.5940), (-58.3602, -34.6245)],
        "label": "Sector costero", "tag": "EJE APROX.", "color": COBRE, "label_pos": (-58.3570, -34.6118), "label_width": 10,
    },
    {
        "key": "puerto", "subzona": "Faena / El Mercado", "state": "hito", "shape": "hito",
        "coords": [(-58.3642, -34.6172)],
        "label": "Faena / El Mercado", "tag": "HITO", "color": ROJO, "label_pos": (-58.3736, -34.6170), "label_width": 12,
    },
    {
        "key": "puerto", "subzona": "Dársena Sur", "state": "a_reforzar", "shape": "polygon",
        "coords": [(-58.3732, -34.6195), (-58.3658, -34.6196), (-58.3654, -34.6284), (-58.3736, -34.6282), (-58.3732, -34.6195)],
        "label": "Dársena Sur", "tag": "ÁREA DE LECTURA", "color": SLATE, "label_pos": (-58.3662, -34.6252), "label_width": 11,
    },
    {
        "key": "san_telmo", "subzona": "Mercado de San Telmo", "state": "hito", "shape": "hito",
        "coords": [(-58.3730, -34.6218)],
        "label": "Mercado", "tag": "HITO COLECTIVO", "color": ROJO, "label_pos": (-58.3678, -34.6210), "label_width": 10,
    },
    {
        "key": "san_telmo", "subzona": "Casco histórico / Defensa", "state": "consolidada", "shape": "line",
        "coords": [(-58.3732, -34.6185), (-58.3711, -34.6290)],
        "label": "Casco histórico / Defensa", "tag": "EJE APROX.", "color": VERDE, "label_pos": (-58.3696, -34.6265), "label_width": 14,
    },
    {
        "key": "san_telmo", "subzona": "Área gastronómica cercana", "state": "consolidada", "shape": "polygon",
        "coords": [(-58.3780, -34.6192), (-58.3700, -34.6192), (-58.3700, -34.6244), (-58.3780, -34.6244), (-58.3780, -34.6192)],
        "label": "Área gastronómica", "tag": "ÁREA DE LECTURA", "color": COBRE, "label_pos": (-58.3770, -34.6203), "label_width": 12,
    },
    {
        "key": "corrientes", "subzona": "Corrientes 9 de Julio-Callao", "state": "consolidada", "shape": "line",
        "coords": [(-58.3815, -34.6038), (-58.3928, -34.6043)],
        "label": "Corrientes 9 de Julio-Callao", "tag": "EJE APROX.", "color": CELESTE, "label_pos": (-58.3868, -34.6060), "label_width": 17,
    },
    {
        "key": "corrientes", "subzona": "Obelisco / teatros", "state": "hito", "shape": "hito",
        "coords": [(-58.3812, -34.6038)],
        "label": "Obelisco / teatros", "tag": "NODO", "color": VERDE, "label_pos": (-58.3798, -34.6023), "label_width": 10,
    },
    {
        "key": "corrientes", "subzona": "Abasto", "state": "a_reforzar", "shape": "polygon",
        "coords": [(-58.4165, -34.5993), (-58.4050, -34.5993), (-58.4048, -34.6076), (-58.4167, -34.6076), (-58.4165, -34.5993)],
        "label": "Abasto", "tag": "ÁREA DE LECTURA", "color": SLATE, "label_pos": (-58.4108, -34.6035), "label_width": 12,
    },
    {
        "key": "belgrano", "subzona": "Barrio Chino", "state": "consolidada", "shape": "polygon",
        "coords": [(-58.4557, -34.5535), (-58.4480, -34.5535), (-58.4478, -34.5588), (-58.4552, -34.5593), (-58.4557, -34.5535)],
        "label": "Barrio Chino", "tag": "IDENTIDAD CLARA", "color": VERDE, "label_pos": (-58.4518, -34.5558), "label_width": 12,
    },
    {
        "key": "belgrano", "subzona": "Bajo Belgrano", "state": "a_reforzar", "shape": "polygon",
        "coords": [(-58.4465, -34.5540), (-58.4368, -34.5542), (-58.4368, -34.5642), (-58.4462, -34.5648), (-58.4465, -34.5540)],
        "label": "Bajo Belgrano", "tag": "ÁREA DE LECTURA", "color": SLATE, "label_pos": (-58.4416, -34.5596), "label_width": 12,
    },
    {
        "key": "belgrano", "subzona": "Belgrano R", "state": "a_reforzar", "shape": "polygon",
        "coords": [(-58.4660, -34.5588), (-58.4578, -34.5588), (-58.4578, -34.5662), (-58.4664, -34.5662), (-58.4660, -34.5588)],
        "label": "Belgrano R", "tag": "SUBZONA DE REFERENCIA", "color": SLATE, "label_pos": (-58.4622, -34.5626), "label_width": 12,
    },
]


# ---------------------------------------------------------------------------
# Mapas de detalle
# ---------------------------------------------------------------------------

def norm_text(value: str) -> str:
    import unicodedata

    return "".join(ch for ch in unicodedata.normalize("NFD", value or "") if unicodedata.category(ch) != "Mn")


def contains_any(value: str, patterns: list[str]) -> bool:
    value_norm = norm_text(value).upper()
    return any(norm_text(p).upper() in value_norm for p in patterns)


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


def draw_street_context(ax, page: str, streets: gpd.GeoDataFrame, barrios: gpd.GeoDataFrame) -> None:
    cfg = MAP_CFG[page]
    minx, miny, maxx, maxy = cfg["bbox"]
    if cfg.get("water"):
        ax.add_patch(MplPolygon([(-58.3635, miny), (maxx, miny), (maxx, maxy), (-58.3635, maxy)], facecolor="#E6EDF3", edgecolor="none", alpha=0.92, zorder=0))
        ax.text(-58.3563, -34.608, "frente costero", rotation=90, fontsize=9.2, color="#5D7F98", ha="center", va="center", zorder=2)

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


def draw_geometries(ax, page: str) -> None:
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
            ax.add_patch(MplPolygon(shape_points(row), closed=True, facecolor=AZUL, edgecolor="white", linewidth=1.1, alpha=0.96, zorder=7))
        else:
            fill_alpha = 0.18 if state == "consolidada" else 0.10
            linestyle = "-" if state == "consolidada" else (0, (4, 3))
            edge_color = row["color"] if state == "consolidada" else SLATE
            ax.add_patch(
                MplPolygon(
                    shape_points(row),
                    closed=True,
                    facecolor=color,
                    edgecolor=edge_color,
                    alpha=fill_alpha,
                    linewidth=1.9 if state == "consolidada" else 1.55,
                    linestyle=linestyle,
                    zorder=5,
                )
            )
    for row in rows:
        draw_label(ax, row)


def render_detail_map(page: str, streets: gpd.GeoDataFrame, barrios: gpd.GeoDataFrame) -> Path:
    cfg = MAP_CFG[page]
    minx, miny, maxx, maxy = cfg["bbox"]
    fig, ax = plt.subplots(figsize=(8.0, 6.0), dpi=230)
    ax.set_facecolor("#FAFBFC")
    draw_street_context(ax, page, streets, barrios)
    draw_geometries(ax, page)
    draw_street_labels(ax, cfg["labels"])

    legend_handles = [
        Line2D([0], [0], color=CELESTE, lw=7, alpha=0.34, label="subzona aproximada"),
        Line2D([0], [0], color=SLATE, lw=2.0, linestyle=(0, (4, 3)), label="área de lectura"),
        Line2D([0], [0], color="#8A97A3", lw=1.4, label="avenidas de referencia"),
    ]
    ax.legend(handles=legend_handles, loc="lower left", fontsize=7.6, frameon=True, framealpha=0.94, facecolor="white", edgecolor="#DDE3E9")

    ax.set_xlim(minx, maxx)
    ax.set_ylim(miny, maxy)
    ax.set_aspect(MAP_ASPECT, adjustable="box")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_edgecolor("#DDE3E9")
        spine.set_linewidth(0.8)
    ax.set_title(cfg["title"], loc="left", color=AZUL, fontweight="bold", fontsize=16, pad=10)
    fig.subplots_adjust(left=0.035, right=0.985, top=0.905, bottom=0.130)

    base = MAP_OUTPUTS[page]
    png = ASSETS / f"{base}.png"
    fig.savefig(png, dpi=230)
    fig.savefig(ASSETS / f"{base}.svg")
    plt.close(fig)
    return png


# ---------------------------------------------------------------------------
# Mapa global (fase13 + recorte fase14)
# ---------------------------------------------------------------------------

def build_global_map() -> Path:
    spec = importlib.util.spec_from_file_location("fase13_mapas", FASE13_SCRIPT)
    f13 = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules["fase13_mapas"] = f13
    spec.loader.exec_module(f13)

    # Marca institucional correcta aunque el texto quede fuera del recorte.
    f13.INSTITUCION = INSTITUCION

    config = {name: dict(cfg) for name, cfg in f13.POLO_CONFIG.items()}
    # Microajustes fase24: separar etiquetas superpuestas del mapa global.
    config["Abasto"]["offset"] = (-0.0045, -0.0100)
    config["Corredor DoHo / Donado-Holmberg"]["offset"] = (0.0068, 0.0082)
    # Tildes en la etiqueta de Villa Pueyrredon / San Martin.
    config["Villa Pueyrredon / Avenida San Martin"]["etiqueta"] = "Villa Pueyrredón / San Martín"

    barrios = f13.load_geojson(f13.GEO_BARRIOS)

    fig, ax = plt.subplots(figsize=(11, 12.5))
    f13.draw_base(ax, barrios)
    for name in f13.POLO_CONFIG:
        f13.draw_shape(ax, barrios, config[name], alpha=0.22, label=True)
    legend = [
        Patch(facecolor=f13.TIPO_COLOR["area_barrio"], alpha=0.30, edgecolor=f13.TIPO_COLOR["area_barrio"], label="Área / barrio de lectura"),
        Patch(facecolor=f13.TIPO_COLOR["macroarea"], alpha=0.30, edgecolor=f13.TIPO_COLOR["macroarea"], label="Macroárea con subzonas"),
        Patch(facecolor=f13.TIPO_COLOR["area_aproximada"], alpha=0.30, edgecolor=f13.TIPO_COLOR["area_aproximada"], label="Área aproximada"),
        Line2D([0], [0], color=f13.TIPO_COLOR["eje_aproximado"], lw=2.5, label="Eje / corredor aproximado"),
    ]
    ax.legend(handles=legend, loc="lower left", bbox_to_anchor=(0.02, 0.035), frameon=True, fontsize=8.2)
    f13.finish_map(
        ax,
        "Mapa general de polos y ejes gastronómicos",
        "Áreas y ejes del universo semilla. No representa locales individuales.",
        "Lectura territorial. Base cartográfica local de barrios CABA. Áreas/ejes aproximados; no son delimitaciones oficiales ni padrón de locales.",
    )
    full_png = ASSETS / "mapa_global_fase24_completo.png"
    fig.savefig(full_png, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    img = Image.open(full_png).convert("RGBA")
    if abs(img.size[0] - 2076) > 20 or abs(img.size[1] - 2624) > 20:
        print(f"AVISO: tamaño del mapa global regenerado {img.size}; se esperaba ~(2076, 2624) como en fase13.")
    crop = img.crop((105, 360, 1985, 2465))
    base = Image.new("RGB", crop.size, "white")
    base.paste(crop, mask=crop.split()[-1])
    dest = ASSETS / "global_mapa_fase24.png"
    base.save(dest, optimize=True)
    return dest


# ---------------------------------------------------------------------------
# PDF de 11 paginas (layout fase20/fase22, textos fase22)
# ---------------------------------------------------------------------------

def register_fonts() -> None:
    regular = Path("C:/Windows/Fonts/arial.ttf")
    bold = Path("C:/Windows/Fonts/arialbd.ttf")
    if regular.exists() and bold.exists():
        pdfmetrics.registerFont(TTFont(FONT, str(regular)))
        pdfmetrics.registerFont(TTFont(FONT_BOLD, str(bold)))
    else:
        globals()["FONT"] = "Helvetica"
        globals()["FONT_BOLD"] = "Helvetica-Bold"


def hex_to_rgb(color: str) -> tuple[float, float, float]:
    color = color.lstrip("#")
    return tuple(int(color[i : i + 2], 16) / 255 for i in (0, 2, 4))


def set_fill(c: canvas.Canvas, color: str) -> None:
    c.setFillColorRGB(*hex_to_rgb(color))


def set_stroke(c: canvas.Canvas, color: str) -> None:
    c.setStrokeColorRGB(*hex_to_rgb(color))


def wrap_text(text: str, font_name: str, size: float, max_width: float) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        trial = " ".join([*current, word])
        if pdfmetrics.stringWidth(trial, font_name, size) <= max_width or not current:
            current.append(word)
        else:
            lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines


def draw_wrapped(
    c: canvas.Canvas,
    text: str,
    x: float,
    y: float,
    width: float,
    *,
    font_name: str | None = None,
    size: float = 10,
    color: str = NEGRO,
    leading: float | None = None,
) -> float:
    if font_name is None:
        font_name = FONT
    if leading is None:
        leading = size * 1.35
    c.setFont(font_name, size)
    set_fill(c, color)
    for line in wrap_text(text, font_name, size, width):
        c.drawString(x, y, line)
        y -= leading
    return y


def page_header(c: canvas.Canvas, page: int, title: str, subtitle: str | None = None) -> float:
    set_fill(c, AZUL)
    c.rect(0, H - 18, W, 18, fill=1, stroke=0)
    set_fill(c, ROJO)
    c.rect(0, H - 18, 70, 18, fill=1, stroke=0)
    y = H - 58
    c.setFont(FONT_BOLD, 16)
    set_fill(c, AZUL)
    c.drawString(M, y, title)
    c.setFont(FONT_BOLD, 9)
    set_fill(c, GRIS)
    c.drawRightString(W - M, y + 3, f"{page} / {TOTAL_PAGES}")
    y -= 23
    if subtitle:
        y = draw_wrapped(c, subtitle, M, y, W - 2 * M, font_name=FONT_BOLD, size=10.5, color=GRIS, leading=13)
    set_stroke(c, LINEA)
    c.line(M, y - 8, W - M, y - 8)
    return y - 28


def page_footer(c: canvas.Canvas) -> None:
    set_stroke(c, LINEA)
    c.line(M, 46, W - M, 46)
    c.setFont(FONT, 7.8)
    set_fill(c, GRIS)
    c.drawString(M, 29, INSTITUCION)
    c.drawRightString(W - M, 29, GOBIERNO)


def finish_page(c: canvas.Canvas) -> None:
    page_footer(c)
    c.showPage()


def note_box(
    c: canvas.Canvas,
    x: float,
    y: float,
    w: float,
    h: float,
    title: str,
    body: str,
    *,
    border: str = CELESTE,
    fill: str = SOFT_AZUL,
    size: float = 8.8,
) -> None:
    set_fill(c, fill)
    set_stroke(c, border)
    c.roundRect(x, y, w, h, 5, fill=1, stroke=1)
    c.setFont(FONT_BOLD, size + 1.2)
    set_fill(c, AZUL)
    c.drawString(x + 12, y + h - 20, title)
    yy = y + h - 38
    for paragraph in body.split("\n"):
        yy = draw_wrapped(c, paragraph, x + 12, yy, w - 24, font_name=FONT, size=size, color=NEGRO, leading=size * 1.35)
        yy -= 4


def bullet_list(c: canvas.Canvas, items: list[str], x: float, y: float, width: float, *, size: float = 9.2) -> float:
    for item in items:
        c.setFont(FONT_BOLD, size + 1)
        set_fill(c, ROJO)
        c.drawString(x, y, "•")
        y = draw_wrapped(c, item, x + 16, y, width - 16, font_name=FONT, size=size, color=NEGRO, leading=size * 1.35)
        y -= 8
    return y


def draw_image_fit(c: canvas.Canvas, path: Path, x: float, y: float, w: float, h: float) -> None:
    img = ImageReader(str(path))
    iw, ih = img.getSize()
    scale = min(w / iw, h / ih)
    dw, dh = iw * scale, ih * scale
    dx, dy = x + (w - dw) / 2, y + (h - dh) / 2
    c.drawImage(img, dx, dy, dw, dh, preserveAspectRatio=True, mask="auto")


def cover(c: canvas.Canvas) -> None:
    set_fill(c, AZUL)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    set_fill(c, ROJO)
    c.rect(0, 0, 18, H, fill=1, stroke=0)
    set_fill(c, WHITE)
    y = H - 190
    c.setFont(FONT_BOLD, 29)
    for line in wrap_text(TITLE, FONT_BOLD, 29, W - 2 * M - 20):
        c.drawString(M + 10, y, line)
        y -= 35
    c.setFont(FONT_BOLD, 18)
    c.drawString(M + 10, y - 14, SUBTITLE)
    c.setFont(FONT, 12.2)
    c.drawString(M + 10, y - 68, INSTITUCION)
    c.drawString(M + 10, y - 88, GOBIERNO)
    c.drawString(M + 10, y - 126, DATE_LABEL)
    c.setFont(FONT_BOLD, 9.5)
    c.drawRightString(W - M, 32, f"1 / {TOTAL_PAGES}")
    c.showPage()


def index_page(c: canvas.Canvas) -> None:
    page_header(c, 2, "Índice")
    entries = [
        "Portada",
        "Índice",
        "Resumen ejecutivo",
        "Alcance y criterio de lectura",
        "Mapa general de polos y ejes gastronómicos",
        "Lectura territorial general",
        "Detalle: Palermo / Las Cañitas",
        "Detalle: Puerto Madero",
        "Detalle: San Telmo",
        "Detalle: Corrientes / Abasto",
        "Detalle: Belgrano",
    ]
    y = H - 132
    for idx, entry in enumerate(entries, start=1):
        c.setFont(FONT, 11.2)
        set_fill(c, NEGRO)
        c.drawString(M + 10, y, entry)
        set_stroke(c, LINEA)
        c.line(M + 210, y + 3, W - M - 36, y + 3)
        c.setFont(FONT_BOLD, 11.2)
        c.drawRightString(W - M - 10, y, str(idx))
        y -= 42
    finish_page(c)


def summary_page(c: canvas.Canvas) -> None:
    y = page_header(
        c,
        3,
        "Resumen ejecutivo",
        "Una lectura territorial inicial de los polos gastronómicos de la Ciudad.",
    )
    paragraphs = [
        "Este informe organiza un universo semilla de 22 polos y ejes gastronómicos de la Ciudad de Buenos Aires, con el objetivo de aportar un insumo para la discusión institucional y el ordenamiento de criterios.",
        "La pieza combina un mapa global de referencia, mapas de detalle por zonas seleccionadas y menciones destacadas del universo semilla. Las áreas representadas son aproximaciones de lectura territorial: no constituyen límites oficiales, padrón de locales ni ranking gastronómico.",
        "El valor principal del informe es ofrecer una primera lectura ordenada sobre zonas, ejes y subzonas gastronómicas, diferenciando áreas con mayor reconocimiento territorial de aquellas que pueden profundizarse en próximas etapas de trabajo.",
    ]
    yy = y - 4
    for paragraph in paragraphs:
        yy = draw_wrapped(c, paragraph, M + 8, yy, W - 2 * M - 16, font_name=FONT, size=11.4, color=NEGRO, leading=16)
        yy -= 18
    note_box(
        c,
        M,
        142,
        W - 2 * M,
        104,
        "Lectura institucional",
        "La pieza está pensada como apoyo para conversación y ordenamiento territorial. La lectura de detalle se concentra en cinco zonas seleccionadas y mantiene el mapa global como referencia de conjunto.",
        border=VERDE,
        fill=SOFT_VERDE,
        size=9.2,
    )
    finish_page(c)


def scope_page(c: canvas.Canvas) -> None:
    y = page_header(c, 4, "Alcance y criterio de lectura", "Qué afirma y qué no afirma la pieza")
    note_box(
        c,
        M,
        y - 112,
        W - 2 * M,
        104,
        "Aclaración metodológica",
        "Este informe se construye a partir de un universo semilla de polos, ejes y menciones gastronómicas relevadas mediante fuentes abiertas, referencias territoriales y capas auxiliares de geolocalización. Las áreas representadas funcionan como herramienta de lectura territorial y no buscan fijar límites oficiales ni reemplazar padrones institucionales.",
        border=AZUL,
        fill=SOFT_AZUL,
        size=8.3,
    )
    note_box(
        c,
        M,
        y - 222,
        W - 2 * M,
        82,
        "Universo semilla",
        "El universo semilla es un insumo de trabajo. Las menciones destacadas funcionan como referencias del universo semilla: no son ranking, no son recomendación comercial y no acreditan actividad vigente por sí mismas.",
        border=VERDE,
        fill=SOFT_VERDE,
        size=9.2,
    )
    note_box(
        c,
        M,
        y - 326,
        W - 2 * M,
        86,
        "Subzonas",
        "Las subzonas son aproximaciones editoriales construidas para facilitar la lectura territorial. No son límites oficiales, polígonos normativos ni delimitaciones cerradas.",
        border=ROJO,
        fill=SOFT_COBRE,
        size=9.2,
    )
    finish_page(c)


def global_map_page(c: canvas.Canvas, global_map: Path) -> None:
    page_header(
        c,
        5,
        "Mapa general de polos y ejes gastronómicos",
        "Lectura territorial del universo semilla de 22 polos y ejes.",
    )
    draw_image_fit(c, global_map, M - 4, 138, W - 2 * M + 8, 548)
    note_box(
        c,
        M,
        72,
        W - 2 * M,
        54,
        "Lectura",
        "El mapa global ordena una mirada general de la Ciudad y ubica los principales sectores de referencia en una misma pieza.",
        border=CELESTE,
        fill=SOFT_AZUL,
        size=8.3,
    )
    finish_page(c)


def territorial_page(c: canvas.Canvas) -> None:
    y = page_header(c, 6, "Lectura territorial general", "Cómo leer las zonas de detalle")
    note_box(
        c,
        M,
        y - 88,
        W - 2 * M,
        76,
        "Palermo y Puerto Madero",
        "Palermo concentra el mayor volumen de menciones y requiere distinguir subzonas internas. Puerto Madero se lee mejor como banda de docks y eje costero.",
        border=CELESTE,
        fill=SOFT_AZUL,
        size=9,
    )
    note_box(
        c,
        M,
        y - 190,
        W - 2 * M,
        82,
        "San Telmo y Corrientes / Abasto",
        "San Telmo se entiende a partir del Mercado y el casco histórico. Corrientes y Abasto se presentan como áreas vinculadas pero diferenciadas dentro de la lectura territorial.",
        border=VERDE,
        fill=SOFT_VERDE,
        size=9,
    )
    note_box(
        c,
        M,
        y - 292,
        W - 2 * M,
        74,
        "Belgrano",
        "Belgrano se presenta como macroárea con subzonas de referencia. Barrio Chino, Bajo Belgrano y Belgrano R se leen como sectores diferenciados.",
        border=ROJO,
        fill=SOFT_COBRE,
        size=9,
    )
    bullet_list(
        c,
        [
            "El mapa global sostiene la lectura de conjunto.",
            "Los mapas de detalle amplían cinco zonas seleccionadas.",
            "Las menciones laterales funcionan como referencias del universo semilla, sin ordenar preferencias.",
        ],
        M + 6,
        254,
        W - 2 * M - 12,
        size=9.5,
    )
    finish_page(c)


DETAILS = {
    7: {
        "key": "palermo",
        "title": "Detalle: Palermo / Las Cañitas",
        "subtitle": "Subzonas aproximadas de lectura territorial.",
        "mentions": "Palermo / Las Cañitas: Don Julio; La Cabrera; Niño Gordo; Gran Dabbang; Mishiguene; La Mar; Cosi Mi Piace.\nLas Cañitas: Campo Bravo; Kansas; SushiClub.\nOtras referencias de la zona: Café Registrado.",
        "reading": "Se distinguen Palermo Soho, Palermo Hollywood y Las Cañitas como subzonas aproximadas. La lectura permite ordenar un sector amplio con alta presencia gastronómica y diferentes identidades internas.",
    },
    8: {
        "key": "puerto",
        "title": "Detalle: Puerto Madero",
        "subtitle": "Banda de docks, frente costero e hitos de lectura.",
        "mentions": "Zona costera / docks: Happening; Sottovoce; El Mercado / Faena; Le Grill.\nOtras referencias de la zona: Cabaña Las Lilas; La Parolaccia Casa Tua; Red Resto & Lounge; Patagonia Sur.",
        "reading": "Puerto Madero se representa como banda de docks y frente costero. Faena / El Mercado funciona como hito de lectura territorial.",
    },
    9: {
        "key": "san_telmo",
        "title": "Detalle: San Telmo",
        "subtitle": "Casco histórico, eje Defensa y Mercado de San Telmo.",
        "mentions": "San Telmo: La Brigada; Café San Juan; Hierbabuena.\nOtras referencias de la zona: Mercado de San Telmo; El Preferido de San Telmo; Pulpería Quilapán; Nápoles.",
        "reading": "El Mercado de San Telmo se muestra como hito colectivo. Defensa y el casco histórico ordenan la lectura territorial del entorno.",
    },
    10: {
        "key": "corrientes",
        "title": "Detalle: Corrientes / Abasto",
        "subtitle": "Áreas vinculadas pero diferenciadas.",
        "mentions": "Corrientes: Las Cuartetas; El Palacio de la Pizza; Pertutti.\nOtras referencias de la zona: Güerrín; Moulin Bleu.\nAbasto: área de lectura asociada al entorno del Shopping Abasto.",
        "reading": "Corrientes se presenta como eje teatral-gastronómico aproximado entre 9 de Julio y Callao. Corrientes y Abasto se presentan como áreas vinculadas pero diferenciadas dentro de la lectura territorial.",
    },
    11: {
        "key": "belgrano",
        "title": "Detalle: Belgrano",
        "subtitle": "Macroárea con subzonas de referencia.",
        "mentions": "Barrio Chino: Hong Kong Style; China Rose.\nOtras referencias de la zona: Ichisou; Ramen Neko; Ichiban; BAO Kitchen; Tori Tori.\nBelgrano R: subzona de referencia dentro de la macroárea.",
        "reading": "Barrio Chino, Bajo Belgrano y Belgrano R se presentan como subzonas diferenciadas dentro de la macroárea.",
    },
}


def detail_page(c: canvas.Canvas, page: int, maps: dict[str, Path]) -> None:
    cfg = DETAILS[page]
    page_header(c, page, cfg["title"], cfg["subtitle"])
    draw_image_fit(c, maps[cfg["key"]], M - 4, 308, W - 2 * M + 8, 394)
    box_w = (W - 2 * M - 14) / 2
    note_box(
        c,
        M,
        118,
        box_w,
        162,
        "Menciones destacadas",
        cfg["mentions"],
        border=CELESTE,
        fill=SOFT_AZUL,
        size=7.4,
    )
    note_box(
        c,
        M + box_w + 14,
        118,
        box_w,
        162,
        "Lectura territorial",
        cfg["reading"],
        border=VERDE,
        fill=SOFT_VERDE,
        size=7.8,
    )
    finish_page(c)


def build_pdf(maps: dict[str, Path], global_map: Path) -> None:
    c = canvas.Canvas(str(PDF_OUT), pagesize=A4)
    c.setTitle(TITLE)
    c.setAuthor(INSTITUCION)
    c.setSubject("Informe DGDGAS")
    cover(c)
    index_page(c)
    summary_page(c)
    scope_page(c)
    global_map_page(c, global_map)
    territorial_page(c)
    for page in range(7, 12):
        detail_page(c, page, maps)
    c.save()


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    register_fonts()
    streets = gpd.read_file(CALLEJERO)
    barrios = gpd.read_file(BARRIOS)
    maps: dict[str, Path] = {}
    for page in DETAIL_ORDER:
        maps[page] = render_detail_map(page, streets, barrios)
        print(f"mapa {page}: {maps[page]}")
    global_map = build_global_map()
    print(f"mapa global: {global_map}")
    build_pdf(maps, global_map)
    print(f"PDF: {PDF_OUT}")


if __name__ == "__main__":
    main()
