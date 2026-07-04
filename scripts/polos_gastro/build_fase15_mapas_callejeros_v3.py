"""Build PolosGastro phase 15 street-detail maps and PDF V3.

Reads only local phase artifacts plus the official GCBA street GeoJSON already
downloaded to the phase output folder. It does not call APIs, does not touch
source data, and writes only phase 15 docs/outputs.
"""
from __future__ import annotations

import csv
import importlib.util
import re
import shutil
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
from matplotlib.patches import Ellipse, Rectangle  # noqa: E402
from reportlab.lib.pagesizes import A4  # noqa: E402
from reportlab.pdfgen import canvas  # noqa: E402


ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs" / "polos_gastro" / "fase15_mapas_callejeros_v3"
OUT = ROOT / "outputs" / "polos_gastro" / "fase15_mapas_callejeros_v3"
ASSETS = OUT / "assets"
TABLES = OUT / "tablas"

PHASE14 = ROOT / "outputs" / "polos_gastro" / "fase14_pdf_institucional_revision_visual"
PHASE14_DOC = ROOT / "docs" / "polos_gastro" / "fase14_pdf_institucional_revision_visual"
PHASE13_TABLES = ROOT / "outputs" / "polos_gastro" / "fase13_mapas" / "tablas"
PHASE11_TABLES = ROOT / "outputs" / "polos_gastro" / "fase11_google_places_piloto" / "tablas"

CALLEJERO = ASSETS / "callejero_gcba_2026_06_02.geojson"
BARRIOS = ROOT / "data" / "raw" / "geo_barrios.geojson"
COMUNAS = ROOT / "data" / "raw" / "geo_comunas.geojson"

MENTIONS_V2 = PHASE14 / "menciones_destacadas_por_polo.csv"
LOCALES_REVISION = PHASE13_TABLES / "locales_para_mapa_revision.csv"
CONSOLIDADO = PHASE11_TABLES / "consolidado_tandas_google_places.csv"

LOCALES_V3 = TABLES / "locales_para_mapas_v3.csv"
MD_BASE_V3 = DOCS / "INFORME_POLOS_GASTRO_DGDGAS_PDF_BASE_V3.md"
PDF_V3 = OUT / "INFORME_POLOS_GASTRO_DGDGAS_PRELIMINAR_V3.pdf"
DIAGNOSTICO = DOCS / "DIAGNOSTICO_BASE_CALLEJERA.md"
CAMBIOS = DOCS / "CAMBIOS_V2_A_V3_POLOS_GASTRO.md"

SOURCE_V2_SCRIPT = ROOT / "scripts" / "polos_gastro" / "build_pdf_institucional_fase14_revision_visual.py"
spec = importlib.util.spec_from_file_location("fase14_v2", SOURCE_V2_SCRIPT)
v2 = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules["fase14_v2"] = v2
spec.loader.exec_module(v2)


INSTITUCION = "DGDGAS — Dirección General de Desarrollo Gastronómico"
GOBIERNO = "Gobierno de la Ciudad de Buenos Aires"
TITLE = "Polos gastronómicos de la Ciudad de Buenos Aires"
SUBTITLE = "Universo semilla, lectura territorial y capa auxiliar de geolocalización"

AZUL = "#1F3B57"
AZUL2 = "#2C6E9E"
ROJO = "#C0392B"
VERDE = "#1A9850"
NARANJA = "#C0762B"
GRIS = "#555555"
LINEA = "#D9DEE5"
SOFT_AZUL = "#EAF1F8"
SOFT_VERDE = "#EAF5EE"
SOFT_NARANJA = "#F8EDE0"

W, H = A4
M = 44

DETAIL_ORDER = ["palermo", "puerto", "san_telmo", "corrientes", "belgrano"]

MAP_OUTPUTS = {
    "palermo": "mapa_v3_palermo_las_canitas",
    "puerto": "mapa_v3_puerto_madero",
    "san_telmo": "mapa_v3_san_telmo",
    "corrientes": "mapa_v3_corrientes_abasto",
    "belgrano": "mapa_v3_belgrano_subzonas",
}

MAP_CFG = {
    "palermo": {
        "title": "Palermo / Las Cañitas",
        "bbox": (-58.444, -34.596, -58.407, -34.561),
        "barrios": ["Palermo"],
        "areas": [
            (-58.428, -34.586, 0.030, 0.018, "Palermo Soho / Hollywood", AZUL2),
            (-58.431, -34.571, 0.018, 0.010, "Las Cañitas", VERDE),
        ],
        "labels": [
            (-58.432, -34.586, "Palermo Soho / Hollywood"),
            (-58.436, -34.571, "Las Cañitas"),
        ],
        "major": ["SANTA FE", "CORDOBA", "JUAN B. JUSTO", "SCALABRINI", "DORREGO", "DEL LIBERTADOR", "LUIS MARIA CAMPOS", "OLLeros"],
        "street_labels": [
            (-58.425, -34.579, "Av. Santa Fe"),
            (-58.427, -34.591, "Av. Córdoba"),
            (-58.438, -34.585, "Av. Juan B. Justo"),
            (-58.415, -34.585, "Scalabrini Ortiz"),
            (-58.434, -34.566, "Av. Luis M. Campos"),
        ],
    },
    "puerto": {
        "title": "Puerto Madero",
        "bbox": (-58.392, -34.632, -58.354, -34.584),
        "barrios": ["Puerto Madero"],
        "water": True,
        "areas": [(-58.364, -34.611, 0.014, 0.034, "docks / eje costero", AZUL2)],
        "labels": [(-58.365, -34.610, "docks / eje costero")],
        "major": ["ALICIA MOREAU", "JUANA MANSO", "HUERGO", "MADERO", "ROSARIO VERA", "MACACHA GUEMES", "CORDOBA"],
        "street_labels": [
            (-58.370, -34.603, "A. Moreau de Justo"),
            (-58.363, -34.611, "Juana Manso"),
            (-58.382, -34.610, "Huergo / Madero"),
            (-58.364, -34.618, "Rosario Vera Peñaloza"),
        ],
    },
    "san_telmo": {
        "title": "San Telmo",
        "bbox": (-58.381, -34.631, -58.365, -34.615),
        "barrios": ["San Telmo", "Monserrat", "Constitucion"],
        "areas": [(-58.372, -34.621, 0.010, 0.011, "entorno Mercado", AZUL2)],
        "labels": [(-58.373, -34.619, "Mercado de San Telmo"), (-58.372, -34.626, "Casco histórico")],
        "major": ["DEFENSA", "BOLIVAR", "CHILE", "ESTADOS UNIDOS", "CARLOS CALVO", "HUMBERTO", "SAN JUAN", "PASEO COLON"],
        "street_labels": [
            (-58.373, -34.622, "Defensa / Bolívar"),
            (-58.371, -34.628, "Av. San Juan"),
            (-58.377, -34.620, "Chile"),
            (-58.367, -34.624, "Paseo Colón"),
        ],
    },
    "corrientes": {
        "title": "Corrientes / Abasto",
        "bbox": (-58.418, -34.611, -58.374, -34.596),
        "barrios": ["San Nicolas", "Balvanera", "Almagro"],
        "corrientes": True,
        "areas": [(-58.4105, -34.6038, 0.014, 0.010, "Abasto: radio aprox. 5 cuadras", NARANJA)],
        "labels": [(-58.389, -34.603, "Corrientes 9 de Julio - Callao"), (-58.410, -34.606, "Abasto: a reforzar")],
        "major": ["CORRIENTES", "CALLAO", "9 DE JULIO", "URUGUAY", "PARANA", "RIOBAMBA", "PASTEUR", "PUEYRREDON", "ANCHORENA"],
        "street_labels": [
            (-58.391, -34.602, "Av. Corrientes"),
            (-58.392, -34.606, "Callao"),
            (-58.381, -34.606, "9 de Julio"),
            (-58.410, -34.600, "Abasto"),
        ],
    },
    "belgrano": {
        "title": "Belgrano y subzonas",
        "bbox": (-58.465, -34.567, -58.437, -34.548),
        "barrios": ["Belgrano"],
        "areas": [
            (-58.452, -34.555, 0.010, 0.008, "Barrio Chino", AZUL2),
            (-58.445, -34.559, 0.010, 0.008, "Bajo Belgrano", VERDE),
            (-58.459, -34.562, 0.009, 0.006, "Belgrano R: reforzar", NARANJA),
        ],
        "labels": [(-58.452, -34.554, "Barrio Chino"), (-58.446, -34.559, "Bajo Belgrano"), (-58.459, -34.562, "Belgrano R")],
        "major": ["JURAMENTO", "MENDOZA", "OLAZABAL", "ARRIBENOS", "MONTAÑESES", "DEL LIBERTADOR", "CABILDO", "LA PAMPA", "MIGUELETES"],
        "street_labels": [
            (-58.451, -34.556, "Juramento"),
            (-58.454, -34.559, "Mendoza"),
            (-58.441, -34.559, "Av. del Libertador"),
            (-58.457, -34.565, "Cabildo"),
        ],
    },
}

DETAIL_TEXT_V3 = {
    "palermo": {
        "page": 7,
        "title": "Palermo / Las Cañitas",
        "subtitle": "Zoom con callejero oficial, subzonas diferenciadas y menciones fuera del mapa.",
        "reading": "La página separa Palermo Soho/Hollywood de Las Cañitas mediante trama vial y áreas de lectura. Los puntos acompañan la orientación territorial y no ordenan locales.",
        "caution": "Lectura territorial orientativa, no delimitación oficial. Las menciones requieren validación antes de cualquier uso operativo.",
    },
    "puerto": {
        "page": 8,
        "title": "Puerto Madero",
        "subtitle": "Docks, corredor costero y sedes a validar tratadas con cautela.",
        "reading": "La trama de docks y avenidas permite ubicar el corredor costero sin sobredimensionar sedes con evidencia pendiente.",
        "caution": "Lectura territorial orientativa, no delimitación oficial. Las sedes a validar no se presentan como actividad activa confirmada.",
    },
    "san_telmo": {
        "page": 9,
        "title": "San Telmo",
        "subtitle": "Entorno Mercado de San Telmo y casco barrial con referencias urbanas.",
        "reading": "El Mercado de San Telmo se muestra como hito colectivo. Las menciones cercanas se leen como referencias del entorno patrimonial y gastronómico.",
        "caution": "Lectura territorial orientativa, no delimitación oficial. Los hitos colectivos no equivalen a restaurantes puntuales.",
    },
    "corrientes": {
        "page": 10,
        "title": "Corrientes / Abasto",
        "subtitle": "Ejes vinculados, recortes distintos y sin doble conteo.",
        "reading": "Corrientes se representa como eje 9 de Julio-Callao. Abasto queda como área a reforzar alrededor del shopping, visualmente separada.",
        "caution": "Lectura territorial orientativa, no delimitación oficial. Abasto no se fuerza con puntos propios cuando la evidencia queda pendiente.",
    },
    "belgrano": {
        "page": 11,
        "title": "Belgrano y subzonas",
        "subtitle": "Barrio Chino, Bajo Belgrano y Belgrano R con respaldo diferenciado.",
        "reading": "Barrio Chino se lee con mayor identidad gastronómica; Bajo Belgrano conserva sedes a validar y Belgrano R queda como subzona a reforzar.",
        "caution": "Lectura territorial orientativa, no delimitación oficial. Belgrano R no se presenta como polo consolidado.",
    },
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def norm(text: str | None) -> str:
    return v2.norm(text)


def ensure_dirs() -> None:
    DOCS.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)


def point_index() -> dict[tuple[str, str], dict[str, str]]:
    rows = read_csv(LOCALES_REVISION)
    idx: dict[tuple[str, str], dict[str, str]] = {}
    for row in rows:
        idx[(norm(row.get("polo")), norm(row.get("nombre_lugar")))] = row
        idx[(norm(row.get("nombre_lugar")), norm(row.get("nombre_lugar")))] = row
    return idx


def find_point(row: dict[str, str], idx: dict[tuple[str, str], dict[str, str]]) -> dict[str, str] | None:
    keys = [
        (norm(row.get("polo")), norm(row.get("nombre_lugar"))),
        (norm(row.get("nombre_lugar")), norm(row.get("nombre_lugar"))),
    ]
    if norm(row.get("polo")) == "avenida corrientes":
        keys.append((norm("Avenida Corrientes"), norm(row.get("nombre_lugar"))))
    for key in keys:
        if key in idx:
            return idx[key]
    return None


def status_visual(row: dict[str, str]) -> str:
    if row.get("tipo_mencion") == "hito colectivo":
        return "hito_colectivo"
    if row.get("incluir_en_mapa_detalle") == "si_validar" or row.get("incluir_en_pdf") == "si_con_cautela":
        return "sede_zona_a_validar"
    return "mencion_incluida_con_prudencia"


def public_status(row: dict[str, str]) -> str:
    if row.get("incluir_en_pdf") == "si":
        return "incluida con prudencia"
    if row.get("incluir_en_pdf") == "si_con_cautela":
        return "a validar"
    return "excluida"


def build_locales_v3(mentions: list[dict[str, str]]) -> list[dict[str, str]]:
    idx = point_index()
    rows_out: list[dict[str, str]] = []
    for row in mentions:
        if row.get("incluir_en_pdf") not in {"si", "si_con_cautela"}:
            continue
        point = find_point(row, idx)
        lat = point.get("lat", "") if point else ""
        lon = point.get("lon", "") if point else ""
        include_detail = row.get("incluir_en_mapa_detalle")
        if include_detail not in {"si", "si_validar"}:
            include_detail = "no"
        rows_out.append(
            {
                "polo": row.get("polo", ""),
                "subzona": row.get("subzona", ""),
                "nombre_lugar": row.get("nombre_lugar", ""),
                "lat": lat,
                "lon": lon,
                "estado_consolidado": point.get("estado_consolidado", row.get("estado_para_informe", "")) if point else row.get("estado_para_informe", ""),
                "estado_para_informe": public_status(row),
                "categoria_visual": status_visual(row),
                "incluir_mapa_detalle": include_detail,
                "incluir_mapa_publico": "si_prudente" if include_detail == "si" else ("a_validar" if include_detail == "si_validar" else "no"),
                "incluir_como_mencion_destacada": "si",
                "observacion_publica": "Referencia del universo semilla; no equivale a padrón oficial ni confirma actividad vigente.",
                "page": row.get("page", ""),
                "tipo_mencion": row.get("tipo_mencion", ""),
            }
        )
    fieldnames = [
        "polo",
        "subzona",
        "nombre_lugar",
        "lat",
        "lon",
        "estado_consolidado",
        "estado_para_informe",
        "categoria_visual",
        "incluir_mapa_detalle",
        "incluir_mapa_publico",
        "incluir_como_mencion_destacada",
        "observacion_publica",
    ]
    with LOCALES_V3.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for item in rows_out:
            writer.writerow({k: item[k] for k in fieldnames})
    return rows_out


def copy_global_map() -> Path:
    src = PHASE14 / "assets" / "global_mapa_pdf_v2.png"
    if not src.exists():
        src = ROOT / "outputs" / "polos_gastro" / "fase13_mapas" / "assets" / "mapa_global_22_polos_ejes.png"
    dest = ASSETS / "global_mapa_pdf_v3.png"
    shutil.copyfile(src, dest)
    return dest


def contains_any(value: str, patterns: list[str]) -> bool:
    value_norm = norm(value).upper()
    return any(norm(p).upper() in value_norm for p in patterns)


def label_lines(ax, labels: list[tuple[float, float, str]]) -> None:
    for lon, lat, label in labels:
        ax.text(
            lon,
            lat,
            label,
            fontsize=7.6,
            color="#536170",
            ha="center",
            va="center",
            bbox={"boxstyle": "round,pad=0.18", "fc": "white", "ec": "#D9DEE5", "lw": 0.5, "alpha": 0.82},
            zorder=7,
        )


def plot_areas(ax, cfg: dict[str, object]) -> None:
    for lon, lat, w_lon, h_lat, label, color in cfg.get("areas", []):
        patch = Ellipse(
            (lon, lat),
            width=w_lon,
            height=h_lat,
            facecolor=color,
            edgecolor=color,
            alpha=0.15,
            linewidth=1.6,
            zorder=3,
        )
        ax.add_patch(patch)
        ax.text(lon, lat, label, fontsize=8, color=color, ha="center", va="center", weight="bold", zorder=8)


def plot_points(ax, page: str, rows: list[dict[str, str]]) -> int:
    plotted = 0
    for row in rows:
        if row["page"] != page or row["incluir_mapa_detalle"] not in {"si", "si_validar"}:
            continue
        try:
            lat = float(row["lat"])
            lon = float(row["lon"])
        except ValueError:
            continue
        minx, miny, maxx, maxy = MAP_CFG[page]["bbox"]
        if not (minx <= lon <= maxx and miny <= lat <= maxy):
            continue
        cat = row["categoria_visual"]
        if cat == "hito_colectivo":
            ax.scatter(lon, lat, marker="D", s=58, color=ROJO, edgecolor="white", linewidth=0.8, zorder=10)
            ax.text(lon + 0.00045, lat + 0.0004, row["nombre_lugar"], fontsize=7.2, color=ROJO, weight="bold", zorder=11)
        elif cat == "sede_zona_a_validar":
            ax.scatter(lon, lat, marker="^", s=58, color=NARANJA, edgecolor="white", linewidth=0.8, zorder=10)
        else:
            ax.scatter(lon, lat, marker="o", s=52, color=AZUL2, edgecolor="white", linewidth=0.8, zorder=10)
        plotted += 1
    return plotted


def render_map(page: str, streets: gpd.GeoDataFrame, barrios: gpd.GeoDataFrame, rows: list[dict[str, str]]) -> dict[str, str]:
    cfg = MAP_CFG[page]
    minx, miny, maxx, maxy = cfg["bbox"]
    fig, ax = plt.subplots(figsize=(7.9, 6.0), dpi=220)
    ax.set_facecolor("#FAFBFC")

    if cfg.get("water"):
        ax.add_patch(Rectangle((-58.3635, miny), maxx + 0.010 - (-58.3635), maxy - miny, facecolor="#DDECF7", edgecolor="none", zorder=0))
        ax.text(-58.3595, miny + (maxy - miny) * 0.54, "frente costero", rotation=90, color="#6A879F", fontsize=8, ha="center", zorder=1)

    relevant_barrios = barrios.cx[minx:maxx, miny:maxy]
    if not relevant_barrios.empty:
        relevant_barrios.plot(ax=ax, facecolor="#F3F6F9", edgecolor="#C9D1DA", linewidth=0.6, zorder=1)

    local_streets = streets.cx[minx:maxx, miny:maxy]
    if not local_streets.empty:
        minor = local_streets[local_streets["tipo_c"].fillna("").str.upper() != "AVENIDA"]
        avenues = local_streets[local_streets["tipo_c"].fillna("").str.upper() == "AVENIDA"]
        if not minor.empty:
            minor.plot(ax=ax, color="#DDE3EA", linewidth=0.28, alpha=0.75, zorder=2)
        if not avenues.empty:
            avenues.plot(ax=ax, color="#B8C2CC", linewidth=0.75, alpha=0.90, zorder=3)
        major = local_streets[
            local_streets["nom_mapa"].fillna("").map(lambda value: contains_any(value, cfg["major"]))
            | local_streets["nomoficial"].fillna("").map(lambda value: contains_any(value, cfg["major"]))
        ]
        if not major.empty:
            major.plot(ax=ax, color="#7A8795", linewidth=1.25, alpha=0.95, zorder=4)

    if cfg.get("corrientes"):
        ax.plot([-58.3927, -58.3816], [-34.6043, -34.6038], color=AZUL, linewidth=3.2, solid_capstyle="round", zorder=5)
        ax.text(-58.3865, -34.6020, "Corrientes: 9 de Julio - Callao", fontsize=8, color=AZUL, weight="bold", ha="center", zorder=8)

    plot_areas(ax, cfg)
    label_lines(ax, cfg.get("street_labels", []))
    label_lines(ax, cfg.get("labels", []))
    plotted = plot_points(ax, page, rows)

    legend_handles = [
        Line2D([0], [0], marker="o", color="none", label="mención incluida con prudencia", markerfacecolor=AZUL2, markeredgecolor="white", markersize=7),
        Line2D([0], [0], marker="^", color="none", label="sede/zona a validar", markerfacecolor=NARANJA, markeredgecolor="white", markersize=7),
        Line2D([0], [0], marker="D", color="none", label="hito colectivo", markerfacecolor=ROJO, markeredgecolor="white", markersize=6.5),
    ]
    ax.legend(handles=legend_handles, loc="lower left", fontsize=7.2, frameon=True, framealpha=0.92, facecolor="white", edgecolor="#D9DEE5")

    ax.set_xlim(minx, maxx)
    ax.set_ylim(miny, maxy)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_edgecolor("#C9D1DA")
        spine.set_linewidth(0.8)
    ax.set_title(cfg["title"], loc="left", color=AZUL, fontweight="bold", fontsize=14, pad=10)
    ax.text(minx, miny - (maxy - miny) * 0.055, "lectura territorial orientativa, no delimitación oficial", fontsize=7.4, color=GRIS, ha="left")
    ax.text(maxx, miny - (maxy - miny) * 0.055, "Fuente base: Callejero GCBA (CC-BY-2.5-AR)", fontsize=7.4, color=GRIS, ha="right")
    fig.subplots_adjust(left=0.035, right=0.985, top=0.91, bottom=0.085)

    base = MAP_OUTPUTS[page]
    png = ASSETS / f"{base}.png"
    svg = ASSETS / f"{base}.svg"
    fig.savefig(png, dpi=220)
    fig.savefig(svg)
    plt.close(fig)
    return {"png": str(png), "svg": str(svg), "plotted": str(plotted)}


def build_maps(rows: list[dict[str, str]]) -> tuple[dict[str, Path], dict[str, dict[str, str]]]:
    streets = gpd.read_file(CALLEJERO)
    barrios = gpd.read_file(BARRIOS)
    maps: dict[str, Path] = {"global": copy_global_map()}
    stats: dict[str, dict[str, str]] = {}
    for page in DETAIL_ORDER:
        stat = render_map(page, streets, barrios, rows)
        maps[page] = Path(stat["png"])
        stats[page] = stat
    return maps, stats


def visible_mentions(mentions: list[dict[str, str]], page: str) -> str:
    return v2.visible_mentions(mentions, page)


def summary_page(c: canvas.Canvas) -> None:
    y = v2.header(c, 3, "Resumen ejecutivo", "Qué ordena este informe", "Universo semilla, lectura territorial y señales para orientar validación.")
    v2.cards_row(c, y - 68, [
        ("22", "polos/ejes del universo semilla", AZUL),
        ("106", "menciones de locales relevadas", VERDE),
        ("59", "coincidencias razonables o fuertes", AZUL2),
    ])
    v2.cards_row(c, y - 146, [
        ("5", "mapas de detalle con callejero", AZUL2),
        ("0", "resultados fuera de CABA", ROJO),
    ], x=M + 88, total_w=W - 2 * M - 176)
    v2.bullet_list(c, [
        "El informe mantiene el mapa global de 22 polos/ejes como lectura principal del universo semilla.",
        "Las páginas de detalle incorporan callejero oficial de GCBA, avenidas visibles, referencias urbanas y cajas de menciones destacadas.",
        "Las menciones no son ranking ni listado de calidad: son referencias del universo semilla con tratamiento prudente.",
        "Casos cerrados, búsquedas a corregir, duplicados probables y sedes no resueltas no se presentan como oferta activa.",
    ], M, y - 205, W - 2 * M, size=9.6, gap=8.5)
    v2.note_box(c, M, 112, W - 2 * M, 78, "Cómo leer los números",
                "Son magnitudes del universo semilla y de la capa auxiliar de trabajo. Sirven para orientar validación territorial y decisiones de gestión; no equivalen a un censo ni a confirmación de actividad vigente.",
                color=AZUL, fill=SOFT_AZUL)
    v2.finish(c)


def territorial_page(c: canvas.Canvas) -> None:
    y = v2.header(c, 6, "Lectura territorial general", "Qué muestra la distribución")
    v2.note_box(c, M, y - 86, W - 2 * M, 70, "Polos consolidados",
                "Palermo concentra la mayor cantidad de menciones. Puerto Madero y San Telmo ganan lectura al sumar docks, avenidas y entorno barrial.",
                color=AZUL2, fill=SOFT_AZUL)
    v2.note_box(c, M, y - 176, W - 2 * M, 76, "Corredores y ejes",
                "Avenida Corrientes se trabaja como eje 9 de Julio-Callao. Abasto se separa visualmente como área alrededor del shopping y requiere refuerzo documental.",
                color=VERDE, fill=SOFT_VERDE)
    v2.note_box(c, M, y - 272, W - 2 * M, 82, "Macroáreas y subzonas",
                "Belgrano se presenta como macroárea de trabajo: Barrio Chino, Bajo Belgrano y Belgrano R tienen respaldo diferenciado y no deben leerse como una misma evidencia.",
                color=NARANJA, fill=SOFT_NARANJA)
    v2.bullet_list(c, [
        "Los mapas de detalle usan el callejero GCBA como contexto visual y reducen etiquetas para evitar saturación.",
        "Los nombres destacados se muestran fuera del mapa para preservar legibilidad.",
        "Las sedes a validar se separan de las menciones incluidas con mayor respaldo.",
    ], M, 240, W - 2 * M, gap=10)
    v2.finish(c)


def detail_page(c: canvas.Canvas, page: str, maps: dict[str, Path], mentions: list[dict[str, str]]) -> None:
    cfg = DETAIL_TEXT_V3[page]
    v2.header(c, cfg["page"], "Detalle territorial", cfg["title"], cfg["subtitle"])
    map_x, map_y, map_w, map_h = M, 320, 328, 330
    side_x = M + 342
    side_w = W - M - side_x
    v2.image_box(c, maps[page], map_x, map_y, map_w, map_h, border=True)
    v2.note_box(c, side_x, 462, side_w, 188, "Menciones destacadas del universo semilla",
                visible_mentions(mentions, page), color=AZUL2, fill=SOFT_AZUL, size=7.2)
    v2.note_box(c, side_x, 320, side_w, 124, "Lectura territorial",
                cfg["reading"], color=VERDE, fill=SOFT_VERDE, size=7.5)
    v2.note_box(c, M, 145, W - 2 * M, 92, "Nota de cautela",
                cfg["caution"], color=NARANJA, fill=SOFT_NARANJA, size=8.7)
    v2.draw_wrapped(c, "No es ranking, no es padrón oficial y no confirma actividad vigente.", M, 118, W - 2 * M, font=v2.FONT_BOLD, size=8.4, color=GRIS, leading=10)
    v2.finish(c)


def annex_method(c: canvas.Canvas) -> None:
    y = v2.header(c, 18, "Anexo B", "Criterio cartográfico y limitaciones")
    v2.bullet_list(c, [
        "El mapa global representa áreas, macroáreas, ejes o zonas aproximadas del universo semilla.",
        "Los mapas de detalle usan Callejero GCBA como base de calles y avenidas, con simplificación visual para lectura en PDF.",
        "Los polos sin locales explícitos se muestran como parte del universo y requieren refuerzo documental.",
        "Los puntos y símbolos acompañan la lectura territorial; no validan oficialmente actividad vigente.",
        "Los casos con vigencia no confirmada, duplicados sin resolver y búsquedas a corregir quedan fuera de mapas operativos.",
        "Los hitos colectivos se tratan como referencia territorial, no como restaurante puntual.",
    ], M, y - 10, W - 2 * M, gap=8.5)
    v2.note_box(c, M, 120, W - 2 * M, 98, "Fuente cartográfica",
                "Base callejera: dataset público Calles / Callejero (GeoJson), Buenos Aires Data - GCBA. Licencia CC-BY-2.5-AR. Actualización publicada por el portal: 2 de junio de 2026. Descarga realizada el 3 de julio de 2026.",
                color=AZUL2, fill=SOFT_AZUL, size=8.1)
    v2.finish(c)


def build_pdf(maps: dict[str, Path], mentions: list[dict[str, str]]) -> None:
    c = canvas.Canvas(str(PDF_V3), pagesize=A4)
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

## Universo semilla, lectura territorial y capa auxiliar de geolocalización

**{INSTITUCION}**  
**{GOBIERNO}**  
Fecha de elaboración: julio de 2026

Este documento es la base editorial de la pieza PDF con mapas de detalle callejeros. Ordena el universo semilla de 22 polos/ejes, mantiene el mapa global como pieza principal y refuerza las páginas de detalle con callejero oficial, referencias urbanas y menciones destacadas tratadas con prudencia. No constituye padrón oficial, ranking ni confirmación de actividad vigente.

## 1. Resumen ejecutivo

Se ordena un universo semilla de **22 polos/ejes gastronómicos** de la Ciudad y **106 menciones de locales** asociadas a ese universo. La capa auxiliar permite distinguir coincidencias razonables o fuertes, sedes a validar, casos con vigencia no confirmada, duplicados probables y búsquedas a corregir.

La mejora visual de esta versión se concentra en las páginas territoriales: mapas con base callejera GCBA, avenidas visibles, subzonas transparentes, puntos legibles, cajas de menciones destacadas y notas de cautela.

## 2. Alcance y criterio de lectura

El universo semilla es un insumo de trabajo. Las menciones destacadas no son ranking, no son recomendación comercial y no equivalen a padrón de locales activos.

La capa auxiliar aporta ubicación orientativa y alertas de calidad. No reemplaza fuentes oficiales ni validación territorial.

## 3. Mapa global de 22 polos/ejes

El mapa global se conserva como mapa principal. Representa áreas, ejes y zonas de lectura territorial del universo semilla, sin definir límites oficiales.

## 4. Lectura territorial general

Palermo concentra el mayor volumen de menciones. Puerto Madero y San Telmo permiten lecturas territoriales claras si se separan hitos colectivos, sedes a validar y menciones con mayor respaldo. Corrientes y Abasto se mantienen diferenciados para evitar doble conteo. Belgrano se presenta como macroárea con subzonas de respaldo desigual.

## 5. Detalles territoriales

### Palermo / Las Cañitas

{md_mentions(mentions, "palermo")}

Lectura: mayor volumen del universo semilla y subzonas internas visibles. El mapa usa callejero GCBA y referencias viales para distinguir Palermo Soho/Hollywood y Las Cañitas.

### Puerto Madero

{md_mentions(mentions, "puerto")}

Lectura: polo consolidado costero. Los docks, el corredor costero y las sedes a validar se muestran con pesos visuales diferenciados.

### San Telmo

{md_mentions(mentions, "san_telmo")}

Lectura: área patrimonial/gastronómica. El Mercado de San Telmo se trata como hito colectivo, no como restaurante puntual.

### Corrientes / Abasto

{md_mentions(mentions, "corrientes")}

Lectura: Corrientes es eje teatral-gastronómico 9 de Julio-Callao. Abasto se presenta como área a reforzar alrededor del shopping y no se fusiona con Corrientes.

### Belgrano y subzonas

{md_mentions(mentions, "belgrano")}

Lectura: Barrio Chino tiene identidad gastronómica clara; Bajo Belgrano conserva sedes a validar; Belgrano R queda como subzona a reforzar.

## 6. Hallazgos de la capa auxiliar

- 59 coincidencias razonables o fuertes.
- 8 casos con vigencia no confirmada.
- 11 duplicados probables.
- 25 zonas o sedes a validar.
- 3 búsquedas a corregir.

Los casos cerrados, las búsquedas a corregir y los duplicados no se presentan como activos. Las sedes a validar se tratan como alertas, no como evidencia cerrada.

## 7. Fuente cartográfica

Base callejera usada: **Calles / Callejero (GeoJson)** de Buenos Aires Data - GCBA. Licencia **CC-BY-2.5-AR**. Fecha de actualización publicada por el portal: **2 de junio de 2026**. Descarga local para esta fase: **3 de julio de 2026**.

## 8. Decisiones pendientes

- Validar delimitaciones de Corrientes y Abasto.
- Resolver sedes en duplicados y cadenas antes de cualquier mapa operativo.
- Revisar tratamiento de Belgrano por subzonas.
- Definir nivel de exposición de nombres en mapas finales.

## 9. Recomendaciones prudentes

- Usar el mapa global como lectura institucional del universo semilla.
- Usar los mapas de detalle como apoyo visual, no como padrón operativo.
- Mantener separadas las menciones incluidas, las sedes a validar y los casos excluidos por prudencia.
- Validar territorialmente antes de publicar detalle operativo.

## 10. Próximos pasos

1. Revisar con Ale delimitaciones, sedes y criterios de publicación.
2. Ajustar mapas finales según definiciones territoriales.
3. Preparar una síntesis ejecutiva si el destino requiere lectura de conducción.
4. Generar la versión final después de cerrar decisiones.

## Anexos

La tabla de menciones destacadas se conserva como respaldo en el output de esta fase. Los casos excluidos no se listan en el cuerpo del PDF.
"""
    MD_BASE_V3.write_text(content, encoding="utf-8")


def build_diagnostico() -> None:
    exists = lambda p: "sí" if p.exists() else "no"
    content = f"""# Diagnóstico de base callejera V3 - PolosGastro DGDGAS

Fecha de trabajo: 3 de julio de 2026.

## Capas geo existentes en el repo

| Capa | Ruta | Estado | Uso |
| --- | --- | --- | --- |
| Barrios CABA | `data/raw/geo_barrios.geojson` | {exists(BARRIOS)} | Marco territorial oficial por barrio. |
| Comunas CABA | `data/raw/geo_comunas.geojson` | {exists(COMUNAS)} | Marco territorial oficial por comuna. |
| Callejero GCBA | `outputs/polos_gastro/fase15_mapas_callejeros_v3/assets/callejero_gcba_2026_06_02.geojson` | {exists(CALLEJERO)} | Base callejera de detalle para mapas V3. |

## ¿Hay una capa de calles ya disponible?

Al iniciar la fase no había una capa de calles descargada en `data/` ni en las fases previas de PolosGastro. Se detectaban capas de barrios y comunas, pero no un callejero completo.

Para cumplir el objetivo V3 se descargó una copia del recurso público **Callejero (GeoJson)** del dataset **Calles** de Buenos Aires Data, dentro de la carpeta de outputs de esta fase. No se modificó `data/` ni ninguna fuente original del proyecto.

## ¿Alcanza con barrios/comunas para marco?

Barrios y comunas alcanzan para marco territorial general y para el mapa global, pero no alcanzan para los zooms de detalle. Para las páginas 7 a 11 se requiere trama urbana: calles, avenidas, docks, ejes y referencias de cuadras.

## Fuente usada para calles

- Fuente: Buenos Aires Data / GCBA, dataset **Calles**, recurso **Callejero (GeoJson)**.
- URL dataset: https://data.buenosaires.gob.ar/dataset/calles
- URL de descarga usada: https://cdn.buenosaires.gob.ar/datosabiertos/datasets/jefatura-de-gabinete-de-ministros/calles/callejero.geojson
- Responsable informado por el portal: Jefatura de Gabinete de Ministros; Secretaría de Innovación y Transformación Digital; DG Gobernanza de Datos Abiertos; Gerencia Operativa de Explotación de Datos Geoespaciales.
- Licencia informada por el portal: **CC-BY-2.5-AR**.
- Fecha de publicación del dataset informada por el portal: 10 de mayo de 2021.
- Fecha de actualización informada por el portal: 2 de junio de 2026.
- Fecha de descarga local para esta fase: 3 de julio de 2026.

## Limitaciones

- El callejero se usa como contexto visual, no como fuente para validar locales ni actividad vigente.
- Los mapas de detalle simplifican la red vial para lectura en PDF: se muestran calles suaves, avenidas más visibles y pocas etiquetas.
- Las subzonas de Palermo, Belgrano, Corrientes/Abasto y Puerto Madero son lecturas preliminares, no delimitaciones oficiales.
- Los puntos provienen de la capa auxiliar ya sanitizada y no constituyen padrón oficial.
- No se ejecutaron APIs ni llamadas Google Places en esta fase.
"""
    DIAGNOSTICO.write_text(content, encoding="utf-8")


def build_cambios(stats: dict[str, dict[str, str]]) -> None:
    lines = "\n".join(f"- {MAP_CFG[p]['title']}: mapa PNG/SVG con callejero GCBA; puntos trazados: {stats[p]['plotted']}." for p in DETAIL_ORDER)
    content = f"""# Cambios V2 a V3 - PolosGastro DGDGAS

## Qué cambió en mapas

- Se reemplazaron los cinco mapas de detalle por mapas con base callejera oficial GCBA.
- Se conservaron el mapa global y la estructura general del PDF.
- Se reforzaron avenidas/ejes principales, calles suaves, subzonas con transparencia y símbolos diferenciados.
- Las menciones destacadas permanecen fuera del mapa, en cajas laterales, para evitar saturación.
- Corrientes y Abasto se separan visualmente como ejes vinculados con recortes distintos.
- Belgrano R queda representado como subzona a reforzar, no como polo consolidado.

## Fuente callejera usada

Dataset **Calles / Callejero (GeoJson)** de Buenos Aires Data - GCBA. Licencia **CC-BY-2.5-AR**. Fecha de actualización publicada: **2 de junio de 2026**. Descarga local: **3 de julio de 2026**.

## Mapas mejorados

{lines}

## Limitaciones que siguen

- Los mapas no definen límites oficiales.
- Las menciones no equivalen a padrón de locales activos.
- Algunas sedes permanecen a validar y se muestran con símbolo diferenciado o solo en caja.
- Abasto y Belgrano requieren revisión territorial humana antes de una pieza final.
- La base callejera mejora la lectura, pero no resuelve por sí sola sedes, duplicados ni vigencia.

## Qué queda para versión final

- Validar con Ale/Diego el recorte de Corrientes, Abasto y Belgrano.
- Resolver criterios de sedes, cadenas y duplicados.
- Definir si la versión final conserva puntos o prioriza solo áreas/ejes.
- Revisar si conviene reducir aún más etiquetas de calle en impresión final.

## Qué revisar con Diego/Ale

- Si las sedes a validar deben mantenerse visibles como triángulos o pasar solo a caja.
- Si Belgrano R debe quedar en página de detalle o únicamente como nota.
- Si Abasto debe tener un mapa propio o mantenerse vinculado a Corrientes.
- Si la fuente callejera GCBA satisface el estándar institucional esperado para circulación ejecutiva.
"""
    CAMBIOS.write_text(content, encoding="utf-8")


def configure_v2_module() -> None:
    v2.DOCS_OUT = DOCS
    v2.OUT = OUT
    v2.ASSETS = ASSETS
    v2.MENTIONS_CSV = TABLES / "menciones_destacadas_por_polo_v3_base.csv"
    v2.PDF = PDF_V3
    v2.MD_BASE = MD_BASE_V3
    v2.INSTITUCION = INSTITUCION
    v2.GOBIERNO = GOBIERNO
    v2.TITLE = TITLE
    v2.SUBTITLE = SUBTITLE
    v2.register_fonts()


def main() -> None:
    ensure_dirs()
    configure_v2_module()
    mentions = v2.build_mentions()
    rows_v3 = build_locales_v3(mentions)
    maps, stats = build_maps(rows_v3)
    build_markdown(mentions)
    build_pdf(maps, mentions)
    build_diagnostico()
    build_cambios(stats)
    print(f"PDF: {PDF_V3}")
    print(f"Tabla: {LOCALES_V3}")
    print("Mapas:", ", ".join(MAP_OUTPUTS.values()))
    print("Estados informe:", dict(Counter(r["estado_para_informe"] for r in rows_v3)))


if __name__ == "__main__":
    main()
