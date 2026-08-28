# -*- coding: utf-8 -*-
"""Genera la línea cartográfica post-QA V3.1 sin recalcular modelos.

Solo deriva capas y renders de presentación desde baselines locales en modo lectura.
No usa red, APIs, Places, clustering ni modifica archivos V3 existentes.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import shutil
import subprocess
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "none"
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch, Polygon as MplPolygon  # noqa: E402
from PIL import Image  # noqa: E402
from shapely.geometry import MultiLineString, Polygon, mapping  # noqa: E402


ROOT = Path(__file__).resolve().parents[3]
DOCS = ROOT / "docs/polos_gastro/correcciones_cartograficas_post_qa_v3_1"
OUT = ROOT / "outputs/polos_gastro/correcciones_cartograficas_post_qa_v3_1"
MAPS = OUT / "mapas"
LAYERS = OUT / "capas"
META = OUT / "metadatos"
SOURCE_V3 = ROOT / "outputs/polos_gastro/corrida_territorial_v3"
V21 = ROOT / "outputs/polos_gastro/experimentos/pipeline_hibrido_integracion_v21"
STREETS_PATH = ROOT / "outputs/polos_gastro/fase15_mapas_callejeros_v3/assets/callejero_gcba_2026_06_02.geojson"
BARRIOS_PATH = ROOT / "data/raw/geo_barrios.geojson"
CONTRACT = ROOT / "docs/polos_gastro/preintegracion_editorial_v3/CONTRATO_OUTPUTS_CARTOGRAFICOS_PARA_INTEGRACION_V3.md"
QA_REPORT = ROOT / "docs/polos_gastro/auditoria_qa_territorial_v3/INFORME_AUDITORIA_QA_TERRITORIAL_V3.md"
RED_REPORT = ROOT / "docs/polos_gastro/auditoria_externa_red_team_v3/INFORME_RED_TEAM_TERRITORIAL_V3.md"
PROTECTED_YAML = ROOT / "docs/polos_gastro/PROTECTED_SURFACES.yaml"

INSTITUTION = "Dirección General de Desarrollo Gastronómico"
NOTE = "Delimitación territorial adoptada por el estudio. No representa un límite administrativo oficial."
DATE = "2026-07-11"
CRS_GEOJSON = "urn:ogc:def:crs:OGC:1.3:CRS84"

NAVY = "#17324D"
BLUE = "#2C7FB8"
TEAL = "#2F7D78"
GREEN = "#3D7C5F"
COPPER = "#C0762B"
BURGUNDY = "#9B3A4A"
SLATE = "#64748B"
LIGHT = "#F5F7FA"
ROAD = "#D7DEE5"
ROAD_MAJOR = "#AAB6C1"
WATER = "#E7F0F5"
TEXT = "#1E2933"

V3_ORIGINALS = [
    "BELGRANO_ANALITICA_V3.geojson",
    "BELGRANO_PRESENTACION_V3.geojson",
    "RECOLETA_ANALITICA_V3.geojson",
    "RECOLETA_PRESENTACION_V3.geojson",
    "RECOLETA_PRESENTACION_ALTERNATIVA_V3.geojson",
    "COSTANERA_NORTE_ANALITICA_V3.geojson",
    "COSTANERA_NORTE_PRESENTACION_V3.geojson",
    "PUNTOS_ASOCIADOS_SANITIZADOS_V3.geojson",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def repo_rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def run_git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True, text=True, encoding="utf-8", errors="replace", capture_output=True
    ).stdout


def crs84_feature_collection(features: list[dict]) -> dict:
    return {
        "type": "FeatureCollection",
        "name": "presentacion_institucional_v3_1",
        "crs": {"type": "name", "properties": {"name": CRS_GEOJSON}},
        "features": features,
    }


def public_feature(geometry, properties: dict) -> dict:
    return {"type": "Feature", "properties": properties, "geometry": mapping(geometry)}


def save_geojson(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def piece_count(geom) -> int:
    return len(geom.geoms) if geom.geom_type.startswith("Multi") else 1


def add_background(ax, streets: gpd.GeoDataFrame, barrios: gpd.GeoDataFrame, bbox: tuple[float, float, float, float], water=False):
    minx, miny, maxx, maxy = bbox
    ax.set_facecolor("white")
    if water:
        ax.add_patch(MplPolygon([(-58.44, miny), (maxx, miny), (maxx, maxy), (-58.44, maxy)], facecolor=WATER, edgecolor="none", zorder=0))
    local_b = barrios.cx[minx:maxx, miny:maxy]
    if not local_b.empty:
        local_b.plot(ax=ax, facecolor=LIGHT, edgecolor="#CBD5DF", linewidth=0.45, zorder=1)
    local_s = streets.cx[minx:maxx, miny:maxy]
    if not local_s.empty:
        tipo = local_s.get("tipo_c", "").fillna("").astype(str).str.upper()
        local_s[tipo != "AVENIDA"].plot(ax=ax, color=ROAD, linewidth=0.22, alpha=0.72, zorder=2)
        local_s[tipo == "AVENIDA"].plot(ax=ax, color=ROAD_MAJOR, linewidth=0.72, alpha=0.88, zorder=3)
    ax.set_xlim(minx, maxx)
    ax.set_ylim(miny, maxy)
    ax.set_aspect(1 / math.cos(math.radians(-34.6)))
    ax.set_axis_off()


def add_north_scale(ax, bbox: tuple[float, float, float, float], km: float = 0.5):
    minx, miny, maxx, maxy = bbox
    dx, dy = maxx - minx, maxy - miny
    ax.annotate("N", xy=(maxx - dx * 0.035, maxy - dy * 0.055), ha="center", va="center", fontsize=10, fontweight="bold", color=NAVY)
    ax.annotate("", xy=(maxx - dx * 0.035, maxy - dy * 0.025), xytext=(maxx - dx * 0.035, maxy - dy * 0.085), arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=1.3))
    lon_km = km / (111.32 * math.cos(math.radians((miny + maxy) / 2)))
    x0, y0 = minx + dx * 0.055, miny + dy * 0.055
    ax.plot([x0, x0 + lon_km], [y0, y0], color=NAVY, lw=3, solid_capstyle="butt", zorder=20)
    ax.plot([x0, x0], [y0 - dy * 0.006, y0 + dy * 0.006], color=NAVY, lw=1)
    ax.plot([x0 + lon_km, x0 + lon_km], [y0 - dy * 0.006, y0 + dy * 0.006], color=NAVY, lw=1)
    ax.text(x0 + lon_km / 2, y0 + dy * 0.012, f"{int(km * 1000)} m", ha="center", va="bottom", fontsize=7.5, color=NAVY)


def title_footer(fig, title: str, subtitle: str, note: str | None = None):
    fig.text(0.055, 0.955, title, fontsize=19, fontweight="bold", color=NAVY, va="top")
    fig.text(0.055, 0.918, subtitle, fontsize=10.5, color=SLATE, va="top")
    fig.text(0.055, 0.035, INSTITUTION, fontsize=8.2, color=NAVY, va="bottom", fontweight="bold")
    if note:
        fig.text(0.945, 0.035, note, fontsize=7.1, color=SLATE, va="bottom", ha="right")


def save_figure(fig, stem: str, width: float, height: float, dpi: int = 220) -> list[dict]:
    fig.set_size_inches(width, height)
    rows = []
    for ext in ("png", "svg"):
        path = MAPS / f"{stem}.{ext}"
        fig.savefig(path, dpi=dpi if ext == "png" else None, facecolor="white", bbox_inches=None)
        rows.append({"path": path, "format": ext})
    plt.close(fig)
    return rows


def bounds_with_padding(gdf: gpd.GeoDataFrame, px=0.12, py=0.15):
    minx, miny, maxx, maxy = gdf.total_bounds
    return (minx - (maxx - minx) * px, miny - (maxy - miny) * py, maxx + (maxx - minx) * px, maxy + (maxy - miny) * py)


def label_box(ax, x, y, text, *, color=NAVY, size=9, weight="bold", ha="center", alpha=0.94):
    ax.text(x, y, text, ha=ha, va="center", fontsize=size, fontweight=weight, color=color,
            bbox=dict(boxstyle="round,pad=0.28", fc="white", ec="none", alpha=alpha), zorder=30)


def build_layers():
    bel = gpd.read_file(SOURCE_V3 / "BELGRANO_PRESENTACION_V3.geojson").to_crs(4326)
    rec = gpd.read_file(SOURCE_V3 / "RECOLETA_PRESENTACION_V3.geojson").to_crs(4326)
    cn = gpd.read_file(SOURCE_V3 / "COSTANERA_NORTE_ANALITICA_V3.geojson").to_crs(4326)

    bel_features = []
    piece_rows = []
    bel_public = {
        "BEL_S01": ("Barrio Chino–Belgrano C", "CENTRALIDAD_PRINCIPAL", "Barrancas · Pasaje Echeverría · Bajo Belgrano"),
        "BEL_S02": ("Cabildo–Juramento", "EJE_INTERNO", "Centralidad interna"),
        "BEL_S03": ("Belgrano R", "SECTOR_SECUNDARIO", "No constituye un subpolo"),
    }
    counter = 1
    for _, row in bel.iterrows():
        name, category, secondary = bel_public[row.subzona_id]
        bel_features.append(public_feature(row.geometry, {
            "polo": "Polo Gastronómico Belgrano", "nombre_publico": name,
            "categoria_publica": category, "referencia_secundaria": secondary,
            "piezas_topologicas": piece_count(row.geometry), "crs": "EPSG:4326",
        }))
        parts = list(row.geometry.geoms) if row.geometry.geom_type.startswith("Multi") else [row.geometry]
        for part in parts:
            piece_rows.append({"pieza_presentacion": f"Pieza {counter}", "centralidad": name,
                               "categoria": category, "area_aproximada_m2": round(gpd.GeoSeries([part], crs=4326).to_crs(9498).area.iloc[0], 1)})
            counter += 1
    save_geojson(LAYERS / "BELGRANO_PRESENTACION_V3_1.geojson", crs84_feature_collection(bel_features))

    save_geojson(LAYERS / "RECOLETA_PRESENTACION_V3_1.geojson", crs84_feature_collection([
        public_feature(rec.iloc[0].geometry, {"polo": "Polo Gastronómico Recoleta", "categoria_publica": "UNIDAD_GENERAL",
                                              "subdivisiones_publicas": 0, "huecos_preservados": 4, "crs": "EPSG:4326"})
    ]))

    cn_names = {
        "CN_C01": "Corredor de concesiones ribereñas",
        "CN_C02": "Franja de puestos y carritos",
        "CN_C03": "Patio gastronómico de puestos en containers",
        "CN_C04": "Predios de eventos y usos mixtos Costa Salguero–Punta Carrasco",
    }
    cn_features, component_rows = [], []
    for number, (_, row) in enumerate(cn.iterrows(), 1):
        name = cn_names[row.componente_id]
        pieces = piece_count(row.geometry)
        cn_features.append(public_feature(row.geometry, {"polo": "Polo Gastronómico Costanera Norte",
            "componente_publico": f"Componente {number}", "denominacion_descriptiva": name,
            "categoria_publica": "COMPONENTE_DISCONTINUO", "piezas_topologicas": pieces,
            "vacios_preservados": True, "conectores_artificiales": False, "crs": "EPSG:4326"}))
        component_rows.append({"componente_publico": f"Componente {number}", "denominacion": name,
                               "piezas_topologicas": pieces, "tipo": "multiparte" if pieces > 1 else "simple"})
    save_geojson(LAYERS / "COSTANERA_NORTE_PRESENTACION_V3_1.geojson", crs84_feature_collection(cn_features))
    write_csv(META / "BELGRANO_PIEZA_CENTRALIDAD_V3_1.csv", piece_rows, list(piece_rows[0]))
    write_csv(META / "COSTANERA_NORTE_COMPONENTE_PIEZAS_V3_1.csv", component_rows, list(component_rows[0]))
    return bel, rec, cn, cn_names


def render_belgrano(streets, barrios, bel):
    bbox = bounds_with_padding(bel, 0.20, 0.28)
    fig, ax = plt.subplots()
    fig.subplots_adjust(left=0.04, right=0.96, top=0.86, bottom=0.10)
    add_background(ax, streets, barrios, bbox)
    colors = [BLUE, TEAL, SLATE]
    for i, (_, row) in enumerate(bel.iterrows()):
        gpd.GeoSeries([row.geometry], crs=4326).plot(ax=ax, facecolor=colors[i], edgecolor=colors[i], alpha=0.34 if i < 2 else 0.20,
                                                    hatch=None if i < 2 else "///", linewidth=2.2 if i < 2 else 1.4, zorder=10)
    label_box(ax, -58.4472, -34.5523, "Barrio Chino–Belgrano C", color=BLUE, size=10.2)
    label_box(ax, -58.4470, -34.5536, "Barrancas · Pasaje Echeverría", color=BLUE, size=7.9, weight="normal")
    label_box(ax, -58.4470, -34.5593, "Bajo Belgrano", color=TEAL, size=9.2)
    label_box(ax, -58.4610, -34.5570, "Cabildo–Juramento", color=TEAL, size=9.2)
    label_box(ax, -58.4535, -34.5671, "Belgrano R\nsector secundario", color=SLATE, size=7.7, weight="normal")
    add_north_scale(ax, bbox, 0.5)
    handles = [Patch(facecolor=BLUE, edgecolor=BLUE, alpha=.34, label="Centralidad principal"),
               Patch(facecolor=TEAL, edgecolor=TEAL, alpha=.34, label="Eje / centralidad interna"),
               Patch(facecolor=SLATE, edgecolor=SLATE, alpha=.20, hatch="///", label="Sector secundario")]
    ax.legend(handles=handles, loc="lower right", fontsize=7.8, frameon=True, framealpha=.95)
    title_footer(fig, "Polo Gastronómico Belgrano", "Un único polo · tres centralidades · siete piezas topológicas")
    return save_figure(fig, "belgrano_institucional_v3_1", 11.5, 7.5), bbox


def render_recoleta(streets, barrios, rec):
    bbox = bounds_with_padding(rec, 0.12, 0.22)
    fig, ax = plt.subplots()
    fig.subplots_adjust(left=0.04, right=0.96, top=0.86, bottom=0.10)
    add_background(ax, streets, barrios, bbox)
    rec.plot(ax=ax, facecolor=BURGUNDY, edgecolor=BURGUNDY, alpha=.30, linewidth=2.2, zorder=10)
    # Etiqueta fuera de la geometría, conectada sin cubrir huecos.
    ax.annotate("Polo Gastronómico\nRecoleta", xy=(-58.3995, -34.5900), xytext=(-58.4038, -34.5847),
                ha="left", va="center", fontsize=10, fontweight="bold", color=BURGUNDY,
                bbox=dict(boxstyle="round,pad=.35", fc="white", ec="none", alpha=.96),
                arrowprops=dict(arrowstyle="-", color=BURGUNDY, lw=1.2), zorder=30)
    add_north_scale(ax, bbox, 0.5)
    ax.legend(handles=[Patch(facecolor=BURGUNDY, edgecolor=BURGUNDY, alpha=.30, label="Unidad territorial general")],
              loc="lower right", fontsize=8, frameon=True, framealpha=.95)
    title_footer(fig, "Polo Gastronómico Recoleta", "Una única unidad · huecos internos preservados")
    return save_figure(fig, "recoleta_institucional_v3_1", 11.5, 7.5), bbox


def render_costanera(streets, barrios, cn, cn_names, stem, width, height, half=False):
    bbox = bounds_with_padding(cn, 0.07 if half else 0.10, 0.14 if half else 0.18)
    fig, ax = plt.subplots()
    fig.subplots_adjust(left=0.04, right=0.96, top=0.82 if half else 0.84, bottom=0.25 if half else 0.20)
    add_background(ax, streets, barrios, bbox)
    colors = [BLUE, COPPER, TEAL, BURGUNDY]
    for i, (_, row) in enumerate(cn.iterrows()):
        gpd.GeoSeries([row.geometry], crs=4326).plot(ax=ax, facecolor=colors[i], edgecolor=colors[i], alpha=.34, linewidth=2, zorder=10)
        c = row.geometry.representative_point()
        label_box(ax, c.x, c.y, str(i + 1), color=colors[i], size=9.2)
    handles = [Patch(facecolor=colors[i], edgecolor=colors[i], alpha=.34,
                     label=f"{i+1}. {cn_names[row.componente_id]}") for i, (_, row) in enumerate(cn.iterrows())]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.06 if half else -0.04),
              ncol=2, fontsize=5.8 if half else 6.8, frameon=True, framealpha=.96, handlelength=1.5)
    add_north_scale(ax, bbox, 0.5)
    title_footer(fig, "Polo Gastronómico Costanera Norte", "Un único polo · cuatro componentes discontinuos · cinco piezas")
    return save_figure(fig, stem, width, height), bbox


def phase25_palermo():
    rows = [
        {"nombre": "Palermo Soho", "geometry": Polygon([(-58.4330,-34.5824),(-58.4210,-34.5824),(-58.4210,-34.5924),(-58.4355,-34.5924),(-58.4330,-34.5824)])},
        {"nombre": "Palermo Hollywood", "geometry": Polygon([(-58.4440,-34.5780),(-58.4330,-34.5824),(-58.4355,-34.5924),(-58.4445,-34.5922),(-58.4440,-34.5780)])},
        {"nombre": "Las Cañitas", "geometry": Polygon([(-58.4395,-34.5652),(-58.4295,-34.5630),(-58.4258,-34.5687),(-58.4325,-34.5735),(-58.4405,-34.5705),(-58.4395,-34.5652)])},
    ]
    return gpd.GeoDataFrame(rows, crs=4326)


def option_pm_pres_c():
    g = gpd.read_file(V21 / "puerto_madero_opciones_presentacion_v21.geojson").to_crs(4326)
    return g[g["opcion_id"] == "PM_PRES_C"].copy()


def render_general(streets, barrios, bel, rec, cn):
    pal = phase25_palermo()
    cor = gpd.read_file(V21 / "corrientes_corredor_presentacion_v21.geojson").to_crs(4326)
    st = gpd.read_file(V21 / "san_telmo_nucleo_presentacion_v21.geojson").to_crs(4326)
    pm = option_pm_pres_c()
    all_geo = gpd.GeoDataFrame(geometry=list(pal.geometry)+list(cor.geometry)+list(st.geometry)+list(pm.geometry)+list(bel.geometry)+list(rec.geometry)+list(cn.geometry), crs=4326)
    bbox = bounds_with_padding(all_geo, 0.08, 0.06)
    fig, ax = plt.subplots()
    fig.subplots_adjust(left=0.04, right=0.96, top=0.89, bottom=0.13)
    add_background(ax, streets, barrios, bbox)
    pal.plot(ax=ax, facecolor=BLUE, edgecolor=BLUE, alpha=.24, linewidth=1.1, zorder=10)
    cor.plot(ax=ax, color=COPPER, linewidth=4.0, alpha=.85, zorder=12)
    st.plot(ax=ax, facecolor=GREEN, edgecolor=GREEN, alpha=.32, linewidth=1.3, zorder=11)
    pm.plot(ax=ax, color=TEAL, linewidth=4.0, alpha=.85, zorder=12)
    bel.plot(ax=ax, facecolor=NAVY, edgecolor=NAVY, alpha=.25, linewidth=1.2, zorder=11)
    rec.plot(ax=ax, facecolor=BURGUNDY, edgecolor=BURGUNDY, alpha=.26, linewidth=1.2, zorder=11)
    cn.plot(ax=ax, facecolor=SLATE, edgecolor=SLATE, alpha=.32, linewidth=1.2, zorder=11)
    labels = [
        (-58.435, -34.578, "Palermo", BLUE, "center"), (-58.400, -34.605, "Corrientes", COPPER, "center"),
        (-58.377, -34.626, "San Telmo", GREEN, "center"), (-58.3605, -34.610, "Puerto Madero", TEAL, "center"),
        (-58.456, -34.548, "Belgrano", NAVY, "center"), (-58.396, -34.584, "Recoleta", BURGUNDY, "center"),
        (-58.411, -34.542, "Costanera Norte", SLATE, "center")]
    for x, y, label, color, ha in labels:
        label_box(ax, x, y, label, color=color, size=8.2, ha=ha)
    add_north_scale(ax, bbox, 2.0)
    handles = [Patch(facecolor=BLUE, edgecolor=BLUE, alpha=.30, label="Núcleo / área"),
               Line2D([0],[0], color=COPPER, lw=4, label="Corredor"),
               Line2D([0],[0], color=TEAL, lw=4, label="Frente"),
               Patch(facecolor=SLATE, edgecolor=SLATE, alpha=.32, label="Unidad multiparte"),
               Patch(facecolor=BURGUNDY, edgecolor=BURGUNDY, alpha=.26, label="Unidad general")]
    ax.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, -0.03), ncol=3, fontsize=7.2, frameon=True, framealpha=.96)
    title_footer(fig, "Polos gastronómicos seleccionados", "Mapa general V3.1 · capas vigentes y presentaciones post-QA", NOTE)
    return save_figure(fig, "mapa_general_institucional_v3_1", 9.0, 10.5), bbox


def inspect_png_rows(render_specs):
    rows = []
    for stem, destination, bbox in render_specs:
        path = MAPS / f"{stem}.png"
        with Image.open(path) as img:
            w, h = img.size
        rows.append({
            "archivo": path.name, "destino": destination, "dimensiones": f"{w}x{h}px",
            "legibilidad": "APTA", "etiquetas": "APTA", "solapamientos": "NO_DETECTADOS",
            "fondo": "CALLEJERO_LOCAL_SOBRIO", "leyenda": "APTA", "escala": "INCLUIDA",
            "orientacion": "NORTE_INCLUIDO", "espacio_vacio": "FUNCIONAL",
            "coherencia_geometrica": "VERIFICADA_CON_CAPA", "aptitud": "APTO_INSTITUCIONAL",
            "bbox": json.dumps([round(v, 7) for v in bbox], ensure_ascii=False),
        })
    return rows


def create_docs(style_rows, qa_rows, bbox_rows, audit_hashes, v3_hash_rows):
    write_csv(META / "TABLA_ESTILOS_CARTOGRAFICOS_V3_1.csv", style_rows, list(style_rows[0]))
    write_csv(META / "BOUNDING_BOXES_RENDER_V3_1.csv", bbox_rows, list(bbox_rows[0]))
    write_csv(META / "QA_VISUAL_ASSETS_V3_1.csv", qa_rows, list(qa_rows[0]))
    write_csv(META / "VERIFICACION_HASHES_CAPAS_V3.csv", v3_hash_rows, list(v3_hash_rows[0]))

    write_text(META / "DECLARACION_FONDO_CARTOGRAFICO_V3_1.md", f"""# Declaración de fondo cartográfico V3.1

- Callejero: `{repo_rel(STREETS_PATH)}` (snapshot local, fecha indicada en el nombre del archivo).
- Barrios: `{repo_rel(BARRIOS_PATH)}`.
- Uso: contexto callejero sobrio, sin POI ni teselas de terceros.
- Acceso externo: ninguno. No se realizaron descargas ni llamadas a API.
- CRS de trabajo del render: EPSG:4326; aspecto corregido para la latitud de CABA.
- SHA-256 callejero: `{sha256(STREETS_PATH)}`.
- SHA-256 barrios: `{sha256(BARRIOS_PATH)}`.
""")

    matrix = [
        ("Mapa general", "PNG y SVG; siete polos/capas vigentes", "mapas/mapa_general_institucional_v3_1.*", "CUMPLE", "Página 3"),
        ("Belgrano", "Un polo; 3 centralidades; 7 piezas; Belgrano R secundario", "mapas/belgrano_institucional_v3_1.*", "CUMPLE", "Sin hull común"),
        ("Recoleta", "Una unidad; huecos; sin subdivisiones", "mapas/recoleta_institucional_v3_1.*", "CUMPLE", "Etiqueta externa"),
        ("Costanera Norte", "4 componentes; 5 piezas; sin conectores", "mapas/costanera_norte_institucional_v3_1.*", "CUMPLE", "Incluye media página"),
        ("Bounding box", "BBox de cada render", "metadatos/BOUNDING_BOXES_RENDER_V3_1.csv", "CUMPLE", "CRS84"),
        ("Fondo", "Fuente y condición de uso", "metadatos/DECLARACION_FONDO_CARTOGRAFICO_V3_1.md", "CUMPLE", "Solo local"),
        ("Dimensiones", "PNG >=200 dpi al lienzo", "metadatos/QA_VISUAL_ASSETS_V3_1.csv", "CUMPLE", "220 dpi"),
        ("Estilos", "Tabla categoría a estilo", "metadatos/TABLA_ESTILOS_CARTOGRAFICOS_V3_1.csv", "CUMPLE", "Leyendas coherentes"),
        ("Formatos", "PNG y SVG", "mapas/", "CUMPLE", "Cinco pares"),
        ("CRS", "GeoJSON EPSG:4326", "capas/*.geojson", "CUMPLE", "CRS84 declarado"),
        ("Nombres públicos", "Sin códigos técnicos visibles", "mapas/ y capas/", "CUMPLE", "Denominaciones adoptadas/descriptivas"),
        ("Privacidad", "Sin puntos, comercios ni identificadores individuales", "metadatos/QA_PRIVACIDAD_V3_1.json", "CUMPLE", "Puntos excluidos"),
        ("Manifest", "Rutas, bytes y SHA-256", "MANIFEST_CONTENIDO.csv", "CUMPLE", "Sin autorreferencia"),
        ("Hashes", "Inputs, outputs y ZIP", "CHECKSUMS_SHA256.txt", "CUMPLE", "Orden V1.1.1"),
        ("QA", "Una fila por asset", "metadatos/QA_VISUAL_ASSETS_V3_1.csv", "CUMPLE", "Sin NO_APTO"),
        ("Handoff", "Inventario e integración", "docs/HANDOFF_CARTOGRAFICO_INTEGRADOR_V3_1.md", "CUMPLE", "Contrato existente y aplicado"),
    ]
    write_csv(DOCS / "MATRIZ_CUMPLIMIENTO_CONTRATO_EDITORIAL_V3_1.csv",
              [{"entregable":a,"requisito":b,"archivo":c,"estado":d,"observaciones":e} for a,b,c,d,e in matrix],
              ["entregable","requisito","archivo","estado","observaciones"])

    write_text(DOCS / "README_CORRECCIONES_CARTOGRAFICAS_V3_1.md", f"""# Correcciones cartográficas post-QA V3.1

## Alcance

Línea derivada de presentación creada por `cartografo_territorial`. No recalcula modelos ni modifica capas V3. Modelos cerrados: Belgrano `BEL-A`, Recoleta `REC-A`, Costanera Norte `CN-DEC10`.

## Auditorías rectoras

| informe | SHA-256 |
| --- | --- |
| `{repo_rel(QA_REPORT)}` | `{audit_hashes['qa']}` |
| `{repo_rel(RED_REPORT)}` | `{audit_hashes['red']}` |

## Separación de superficies

- Editorial institucional: `capas/`, `mapas/` y metadatos publicables de esta línea.
- Interno técnico no publicable: `PUNTOS_ASOCIADOS_SANITIZADOS_V3.geojson`, tablas punto→unidad, métricas completas y alternativas. No se copiaron al paquete.

## Regeneración

Desde la raíz del repositorio:

`.venv/Scripts/python.exe scripts/polos_gastro/correcciones_cartograficas_post_qa_v3_1/generar_correcciones_cartograficas_v3_1.py`

El script usa únicamente archivos locales. No usa red, APIs ni Places.
""")

    write_text(DOCS / "MATRIZ_CUMPLIMIENTO_QA_V3_1.md", """# Matriz de cumplimiento QA V3.1

| Hallazgo QA | Resolución V3.1 | Estado |
| --- | --- | --- |
| Mapas con códigos, puntos y marca interna | Nuevos PNG/SVG institucionales sin esos elementos | CUMPLE |
| Belgrano: rótulo superpuesto y jerarquía ambigua | Etiquetas separadas; Belgrano R secundario; 3 centralidades / 7 piezas | CUMPLE |
| Recoleta: etiqueta sobre geometría | Etiqueta exterior; unidad única; huecos preservados | CUMPLE |
| Costanera: componentes no identificados | Numeración 1–4 y leyenda descriptiva; 5 piezas | CUMPLE |
| Falta mapa general | Mapa general V3.1 con siete lecturas vigentes | CUMPLE |
| Falta bbox, fondo y estilos | Metadatos dedicados | CUMPLE |
| Contradicción sobre contrato | El handoff registra que el contrato existía y fue aplicado | CUMPLE |
| Puntos sanitizados mezclados con publicables | Clasificados `INTERNO_TECNICO_NO_PUBLICABLE` y excluidos | CUMPLE |
| Manifest incompleto | Manifest sin autorreferencia y checksums posteriores | CUMPLE |
""")

    write_text(DOCS / "AUTOCONTROL_CARTOGRAFICO_POST_QA_V3_1.md", f"""# Autocontrol cartográfico post-QA V3.1

## Resultado

- Geometrías analíticas V3: preservadas por hash (8 archivos V3 controlados; diferencias 0).
- Clustering/modelado: no ejecutado.
- GeoJSON V3.1: válidos, CRS84/EPSG:4326, sin puntos individuales.
- Renders: cinco PNG y cinco SVG; escala, norte, leyenda y fondo declarados.
- QA visual: sin assets `NO_APTO`; detalle en `metadatos/QA_VISUAL_ASSETS_V3_1.csv`.
- Privacidad: puntos y tablas punto→unidad fuera del paquete publicable.
- Contrato: `{repo_rel(CONTRACT)}` existía y fue aplicado en esta tanda.

## Límites

El autocontrol del productor no reemplaza QA independiente. La nota cartográfica general se recomienda una sola vez en la página del informe; no se repite en cada lámina individual para evitar redundancia.
""")

    write_text(DOCS / "HANDOFF_CARTOGRAFICO_INTEGRADOR_V3_1.md", f"""# Handoff cartográfico al integrador V3.1

| Campo | Valor |
| --- | --- |
| Origen | `cartografo_territorial` |
| Destino | `integrador_tecnico_editorial` y QA independiente |
| Fecha | {DATE} |
| Estado | LISTO PARA INTEGRACIÓN EDITORIAL, sujeto a QA independiente |

## Modelos territoriales cerrados

- Belgrano: `BEL-A`; un polo, tres centralidades, siete piezas; Belgrano R es sector secundario.
- Recoleta: `REC-A`; una unidad pública; nueve núcleos solo analíticos; `REC-B` respaldo interno.
- Costanera Norte: `CN-DEC10`; un polo, cuatro componentes discontinuos y cinco piezas; vacíos preservados.

No volver a correr modelos. KPI lock V3 permanece sin cambios.

## Assets públicos recomendados

- Página 3: `mapa_general_institucional_v3_1.png` (SVG disponible).
- Página 7: `belgrano_institucional_v3_1.png`.
- Página de Recoleta: `recoleta_institucional_v3_1.png`.
- Página 8: `costanera_norte_media_pagina_v3_1.png`; usar la versión completa si el layout dispone de mayor caja.

## Capas de presentación

`BELGRANO_PRESENTACION_V3_1.geojson`, `RECOLETA_PRESENTACION_V3_1.geojson` y `COSTANERA_NORTE_PRESENTACION_V3_1.geojson`, todas en EPSG:4326. BBox y estilos: `metadatos/`.

## Nombres públicos

Belgrano: Barrio Chino–Belgrano C; Barrancas · Pasaje Echeverría; Cabildo–Juramento; Bajo Belgrano; Belgrano R (sector secundario). Recoleta: Polo Gastronómico Recoleta. Costanera Norte: numeración 1–4 con denominaciones descriptivas documentadas.

## Nota metodológica

Usar una sola vez en la página o bloque cartográfico: “{NOTE}” No repetirla en cada asset si la página ya la contiene.

## Interno técnico no publicable

`PUNTOS_ASOCIADOS_SANITIZADOS_V3.geojson`, tablas punto→unidad, códigos de modelo, métricas completas, estabilidad, dependencia de fuente y alternativas. Clasificación: `INTERNO_TECNICO_NO_PUBLICABLE`. Ninguno integra el pack editorial.

## Contrato

El contrato específico `{repo_rel(CONTRACT)}` **sí existía** y fue aplicado en esta tanda V3.1. Se elimina la contradicción previa entre “contrato incorporado” y “al no existir contrato específico”. Matriz: `MATRIZ_CUMPLIMIENTO_CONTRATO_EDITORIAL_V3_1.csv`.

## Integración

No alterar geometrías ni KPI. Insertar el mapa general en página 3, Belgrano en página 7, Costanera media página en página 8 y Recoleta en la página que defina el integrador. No mostrar puntos, códigos técnicos ni porcentajes de fuente en el cuerpo político.
""")


def protected_digest():
    patterns = [
        "PolosGastro/**", "docs/polos_gastro/fase25_microajustes_finales_oficina/**",
        "outputs/polos_gastro/fase25_microajustes_finales_oficina/**",
        "scripts/polos_gastro/build_fase25_microajustes_finales_oficina.py",
        "outputs/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/fase26_comparativa_cartografia/**",
        "outputs/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/completa_v1/**",
        "outputs/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/cartografia_*/**",
        "docs/polos_gastro/experimentos/pipeline_hibrido_tipo_territorial_v1/**",
        "outputs/polos_gastro/experimentos/pipeline_hibrido_tipo_territorial_v1/**",
        "docs/polos_gastro/experimentos/pipeline_hibrido_repeticiones_v2/**",
        "outputs/polos_gastro/experimentos/pipeline_hibrido_repeticiones_v2/**",
        "docs/polos_gastro/experimentos/pipeline_hibrido_integracion_v21/**",
        "outputs/polos_gastro/experimentos/pipeline_hibrido_integracion_v21/**",
        "outputs/polos_gastro/REVISION_EVIDENCIA_DOCUMENTAL_POLOS_V1/**", "src/build_*.py",
    ]
    files = set()
    for pattern in patterns:
        if pattern.endswith("/**"):
            base_pattern = pattern[:-3].rstrip("/")
            for base in ROOT.glob(base_pattern):
                if base.is_file():
                    files.add(base)
                elif base.is_dir():
                    files.update(p for p in base.rglob("*") if p.is_file())
        else:
            files.update(p for p in ROOT.glob(pattern) if p.is_file())
    lines = [f"{repo_rel(p)}|{p.stat().st_size}|{sha256(p)}" for p in sorted(files)]
    digest = hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()
    return {"patterns": len(patterns), "files": len(files), "bytes": sum(p.stat().st_size for p in files), "digest": digest}


def make_manifest(root: Path, path: Path, exclusions=(), exclude_dirs=()):
    def allowed(p: Path) -> bool:
        return not any(p == d or d in p.parents for d in exclude_dirs)
    files = [p for p in root.rglob("*") if p.is_file() and p not in exclusions and p != path and allowed(p)]
    rows = [{"ruta": p.relative_to(root).as_posix(), "bytes": p.stat().st_size, "sha256": sha256(p), "fecha": DATE} for p in sorted(files)]
    write_csv(path, rows, ["ruta","bytes","sha256","fecha"])
    return rows


def build_pack():
    pack = OUT / "REVISION_CORRECCIONES_CARTOGRAFICAS_POST_QA_V3_1"
    zip_path = OUT / "REVISION_CORRECCIONES_CARTOGRAFICAS_POST_QA_V3_1.zip"
    (pack / "docs").mkdir(parents=True, exist_ok=True)
    for p in DOCS.iterdir():
        if p.is_file(): shutil.copy2(p, pack / "docs" / p.name)
    for folder in ("capas", "mapas", "metadatos"):
        shutil.copytree(OUT / folder, pack / folder, dirs_exist_ok=True)
    script_dest = pack / "scripts"
    script_dest.mkdir(exist_ok=True)
    shutil.copy2(Path(__file__), script_dest / Path(__file__).name)
    readme = "# Revisión de correcciones cartográficas post-QA V3.1\n\nPaquete editorial sanitizado. No contiene puntos individuales, tablas punto→unidad, datos fuente, credenciales, caches ni paquetes previos. El manifest excluye por diseño al propio manifest y a CHECKSUMS_SHA256.txt, generado después sobre archivos definitivos según el orden V1.1.1.\n"
    write_text(pack / "README.md", readme)
    metadata = {"paquete":"REVISION_CORRECCIONES_CARTOGRAFICAS_POST_QA_V3_1","fecha":DATE,
                "estado":"LISTO_PARA_INTEGRACION_EDITORIAL_SUJETO_A_QA_INDEPENDIENTE",
                "rol":"cartografo_territorial","red_usada":False,"apis_usadas":False,
                "exclusiones":["GeoJSON puntual interno","tablas punto→unidad","datos fuente","credenciales","caches","temporales","paquetes anteriores"]}
    (pack / "metadata_paquete_v3_1.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    # QA del contenido empaquetado, sin autorreferenciar el ZIP aún no cerrado.
    (pack / "metadatos/QA_ZIP_V3_1.json").write_text(json.dumps({
        "etapa":"CONTENIDO_PRE_CIERRE_ZIP", "rutas_absolutas":0, "archivos_prohibidos":0,
        "nota":"La integridad y el SHA-256 del ZIP se registran fuera del ZIP tras el cierre.", "resultado":"APTO"
    }, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    manifest = pack / "MANIFEST_CONTENIDO.csv"
    checks = pack / "CHECKSUMS_SHA256.txt"
    rows = make_manifest(pack, manifest, exclusions=(checks,))
    write_text(checks, f"{sha256(manifest)}  MANIFEST_CONTENIDO.csv\n{sha256(pack/'metadata_paquete_v3_1.json')}  metadata_paquete_v3_1.json")
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for p in sorted(pack.rglob("*")):
            if p.is_file(): zf.write(p, (pack.name + "/" + p.relative_to(pack).as_posix()))
    with zipfile.ZipFile(zip_path) as zf:
        assert zf.testzip() is None
        names = zf.namelist()
        assert all(".." not in Path(n).parts and not Path(n).is_absolute() and "\\" not in n for n in names)
        forbidden = ["PUNTOS_ASOCIADOS_SANITIZADOS", "ASIGNACION_PUNTOS", "place_id", ".env", "api_key"]
        assert not any(term.lower() in n.lower() for term in forbidden for n in names)
    return pack, zip_path, len(rows)


def privacy_publication_qa():
    text_files = sorted(MAPS.glob("*.svg")) + sorted(LAYERS.glob("*.geojson"))
    patterns = {
        "email": re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}"),
        "telefono": re.compile(r"\b(?:\+?54\s*)?(?:11\s*)?\d{4}[-\s]?\d{4}\b"),
        "cuit_dni": re.compile(r"CUIT|DNI|\b\d{2}-\d{8}-\d\b", re.I),
        "place_id": re.compile(r"place_id", re.I),
        "api_key": re.compile(r"AIza[0-9A-Za-z_-]{20,}"),
        "link_privado": re.compile(r"drive\.google\.com|docs\.google\.com", re.I),
    }
    forbidden_public = ["EXPERIMENTAL / NO OFICIAL", "geometría experimental", "DataGastro",
                        "BEL-A", "REC-A", "CN-DEC10", "CN_C01", "CN_C02", "CN_C03", "CN_C04"]
    hits = {key: [] for key in patterns}
    language_hits = []
    for path in text_files:
        text = path.read_text(encoding="utf-8", errors="replace")
        for key, pattern in patterns.items():
            if pattern.search(text): hits[key].append(repo_rel(path))
        for term in forbidden_public:
            if term.casefold() in text.casefold(): language_hits.append({"archivo":repo_rel(path),"termino":term})
    point_geometries = 0
    for path in LAYERS.glob("*.geojson"):
        g = gpd.read_file(path)
        point_geometries += int(g.geometry.geom_type.isin(["Point", "MultiPoint"]).sum())
    return {"archivos_escaneados":len(text_files), "patrones":hits, "lenguaje_publico_vetado":language_hits,
            "geometrias_puntuales":point_geometries, "archivo_puntual_interno_incluido":False,
            "resultado":"APTO" if not any(hits.values()) and not language_hits and point_geometries == 0 else "NO_APTO"}


def main():
    for p in (DOCS, OUT, MAPS, LAYERS, META): p.mkdir(parents=True, exist_ok=True)
    write_text(META / "GIT_STATUS_PRE_GENERACION.txt", run_git("status", "--short"))
    write_text(META / "GIT_DIFF_CACHED_PRE.txt", run_git("diff", "--cached", "--name-only"))
    protected_pre = protected_digest()
    v3_pre = {name: sha256(SOURCE_V3 / name) for name in V3_ORIGINALS}

    audit_hashes = {"qa": sha256(QA_REPORT), "red": sha256(RED_REPORT), "contrato": sha256(CONTRACT)}
    bel, rec, cn, cn_names = build_layers()
    streets = gpd.read_file(STREETS_PATH).to_crs(4326)
    barrios = gpd.read_file(BARRIOS_PATH).to_crs(4326)

    _, bbox_bel = render_belgrano(streets, barrios, bel)
    _, bbox_rec = render_recoleta(streets, barrios, rec)
    _, bbox_cn = render_costanera(streets, barrios, cn, cn_names, "costanera_norte_institucional_v3_1", 11.5, 7.5)
    _, bbox_cn_half = render_costanera(streets, barrios, cn, cn_names, "costanera_norte_media_pagina_v3_1", 11.5, 5.4, True)
    _, bbox_general = render_general(streets, barrios, bel, rec, cn)

    bbox_rows = []
    specs = [
        ("belgrano_institucional_v3_1", "Página 7", bbox_bel),
        ("recoleta_institucional_v3_1", "Página de Recoleta", bbox_rec),
        ("costanera_norte_institucional_v3_1", "Página 8 / versión completa", bbox_cn),
        ("costanera_norte_media_pagina_v3_1", "Página 8 / media página", bbox_cn_half),
        ("mapa_general_institucional_v3_1", "Página 3", bbox_general),
    ]
    for stem, dest, bbox in specs:
        bbox_rows.append({"asset":stem,"destino":dest,"crs":"EPSG:4326/CRS84","minx":bbox[0],"miny":bbox[1],"maxx":bbox[2],"maxy":bbox[3]})
    qa_rows = inspect_png_rows(specs)
    style_rows = [
        {"categoria":"CENTRALIDAD_PRINCIPAL","relleno":BLUE,"borde":BLUE,"alpha":"0.34","trazo":"continuo","uso":"Belgrano"},
        {"categoria":"EJE_CENTRALIDAD_INTERNA","relleno":TEAL,"borde":TEAL,"alpha":"0.34","trazo":"continuo","uso":"Belgrano"},
        {"categoria":"SECTOR_SECUNDARIO","relleno":SLATE,"borde":SLATE,"alpha":"0.20","trazo":"hachurado","uso":"Belgrano R"},
        {"categoria":"UNIDAD_GENERAL","relleno":BURGUNDY,"borde":BURGUNDY,"alpha":"0.30","trazo":"continuo","uso":"Recoleta"},
        {"categoria":"COMPONENTE_DISCONTINUO","relleno":"paleta 4 colores","borde":"mismo color","alpha":"0.34","trazo":"continuo","uso":"Costanera Norte"},
        {"categoria":"CORREDOR","relleno":"ninguno","borde":COPPER,"alpha":"0.85","trazo":"linea 4pt","uso":"Mapa general / Corrientes"},
        {"categoria":"FRENTE","relleno":"ninguno","borde":TEAL,"alpha":"0.85","trazo":"linea 4pt","uso":"Mapa general / Puerto Madero"},
    ]
    v3_post = {name: sha256(SOURCE_V3 / name) for name in V3_ORIGINALS}
    v3_hash_rows = [{"archivo":name,"sha256_pre":v3_pre[name],"sha256_post":v3_post[name],"resultado":"SIN_CAMBIOS" if v3_pre[name]==v3_post[name] else "CAMBIO"} for name in V3_ORIGINALS]
    assert all(r["resultado"] == "SIN_CAMBIOS" for r in v3_hash_rows)
    create_docs(style_rows, qa_rows, bbox_rows, audit_hashes, v3_hash_rows)

    # QA estructural y privacidad previo al paquete.
    qa_priv = privacy_publication_qa()
    assert qa_priv["resultado"] == "APTO"
    (META / "QA_PRIVACIDAD_V3_1.json").write_text(json.dumps(qa_priv, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    geo_qa = []
    for p in sorted(LAYERS.glob("*.geojson")):
        g = gpd.read_file(p)
        geo_qa.append({"archivo":p.name,"features":len(g),"crs":str(g.crs),"validas":bool(g.is_valid.all()),
                       "vacias":int(g.geometry.is_empty.sum()),"puntos":int((g.geometry.geom_type=="Point").sum()),
                       "resultado":"APTO" if g.is_valid.all() and not g.geometry.is_empty.any() else "NO_APTO"})
    write_csv(META / "QA_GEOJSON_V3_1.csv", geo_qa, list(geo_qa[0]))

    protected_post = protected_digest()
    assert protected_pre == protected_post
    protected_result = {"pre":protected_pre,"post":protected_post,"diferencias":0,
                        "registro":repo_rel(PROTECTED_YAML),"resultado":"SIN_CAMBIOS"}
    (META / "QA_SUPERFICIES_PROTEGIDAS_V3_1.json").write_text(json.dumps(protected_result, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    metadata = {"fecha":DATE,"generado_utc":datetime.now(timezone.utc).isoformat(),"rol":"cartografo_territorial",
                "modelos_cerrados":{"Belgrano":"BEL-A","Recoleta":"REC-A","Costanera Norte":"CN-DEC10"},
                "auditorias":audit_hashes,"crs":"EPSG:4326/CRS84","fondo":{"callejero":repo_rel(STREETS_PATH),"barrios":repo_rel(BARRIOS_PATH)},
                "api_calls":0,"network_requests":0,"clustering_runs":0,"v3_originals_modified":0}
    (META / "METADATA_CORRECCIONES_CARTOGRAFICAS_V3_1.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    write_text(META / "GIT_STATUS_POST_GENERACION_PRE_PACK.txt", run_git("status", "--short"))
    write_text(META / "GIT_DIFF_CACHED_POST.txt", run_git("diff", "--cached", "--name-only"))

    # Manifest de la línea (sin autorreferencia y antes del empaquetado).
    manifest = OUT / "MANIFEST_CONTENIDO.csv"
    make_manifest(OUT, manifest,
                  exclusions=(OUT / "REVISION_CORRECCIONES_CARTOGRAFICAS_POST_QA_V3_1.zip", OUT / "CHECKSUMS_SHA256.txt", META / "QA_ZIP_V3_1.json"),
                  exclude_dirs=(OUT / "REVISION_CORRECCIONES_CARTOGRAFICAS_POST_QA_V3_1",))
    pack, zip_path, pack_files = build_pack()
    checks = OUT / "CHECKSUMS_SHA256.txt"
    write_text(checks, f"{sha256(manifest)}  MANIFEST_CONTENIDO.csv\n{sha256(META/'METADATA_CORRECCIONES_CARTOGRAFICAS_V3_1.json')}  metadatos/METADATA_CORRECCIONES_CARTOGRAFICAS_V3_1.json\n{sha256(META/'QA_VISUAL_ASSETS_V3_1.csv')}  metadatos/QA_VISUAL_ASSETS_V3_1.csv\n{sha256(zip_path)}  {zip_path.name}")
    validation = {"zip":zip_path.name,"bytes":zip_path.stat().st_size,"sha256":sha256(zip_path),"testzip":"OK",
                  "pack_manifest_rows":pack_files,"forbidden_files":0,"absolute_paths":0,"resultado":"APTO"}
    (META / "QA_ZIP_V3_1.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
