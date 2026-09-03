# -*- coding: utf-8 -*-
"""FASE27 — Informe político integrado V2 (línea experimental paralela y auditable).

Integra en una nueva versión del informe político de Polos Gastronómicos:
- los assets cartográficos institucionales V3.1 (mapa general, Belgrano, Recoleta,
  Costanera Norte) como COPIAS recortadas de forma reproducible (los originales no
  se modifican; el recorte elimina solo franjas de título/pie internas duplicadas);
- mapas institucionales nuevos para Palermo (delimitación vigente, sin reabrir),
  Corrientes (corredor continuo v2.1, separado de Abasto), San Telmo (núcleo +
  Defensa contextual) y Puerto Madero (PM_PRES_C), renderizados desde las capas de
  presentación vigentes con el estilo cartográfico de la línea V3.1;
- los textos de la capa editable contenido_informe_politico_integrado_v2.yaml.

Reglas duras:
- NO modifica Fase 25 (oficina ni política experimental), Fase 26, corrida V3,
  correcciones V3.1, preintegración ni evidencia documental. Solo lectura.
- Sin red, sin APIs, sin Places, sin clustering, sin instalaciones.
- 10 páginas reales. Identidad visual DGDGAS heredada de la línea Fase 25 política.

Uso (desde la raíz del repo):
  .venv/Scripts/python.exe scripts/polos_gastro/fase27_informe_politico_integrado_v2/generar_informe_politico_integrado_v2.py
  Opciones: --no-pack (omite paquete de revisión y ZIP durante iteración de QA).
"""
from __future__ import annotations

import argparse
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

import fitz  # PyMuPDF
import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402
from PIL import Image  # noqa: E402
from reportlab.lib.pagesizes import A4  # noqa: E402
from reportlab.lib.utils import ImageReader  # noqa: E402
from reportlab.pdfbase import pdfmetrics  # noqa: E402
from reportlab.pdfbase.ttfonts import TTFont  # noqa: E402
from reportlab.pdfgen import canvas  # noqa: E402
from shapely.geometry import Polygon  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
FASE = "fase27_informe_politico_integrado_v2"
SCRIPTS = ROOT / "scripts" / "polos_gastro" / FASE
DOCS = ROOT / "docs" / "polos_gastro" / FASE
OUT = ROOT / "outputs" / "polos_gastro" / FASE
ASSETS = OUT / "assets"
META = OUT / "metadatos"
QA_PNG = OUT / "qa_png_INFORME_POLOS_GASTRO_POLITICO_INTEGRADO_V2"
CONTENT = SCRIPTS / "contenido_informe_politico_integrado_v2.yaml"
CONFIG = SCRIPTS / "config_integracion_v2.json"
PDF_OUT = OUT / "INFORME_POLOS_GASTRO_POLITICO_INTEGRADO_V2.pdf"
PACK = OUT / "REVISION_INFORME_POLITICO_INTEGRADO_V2"
ZIP_OUT = OUT / "REVISION_INFORME_POLITICO_INTEGRADO_V2.zip"

V31_MAPAS = ROOT / "outputs/polos_gastro/historico/correcciones_cartograficas_post_qa_v3_1/mapas"
PROTECTED_YAML = ROOT / "docs/polos_gastro/PROTECTED_SURFACES.yaml"
DATE = "2026-07-12"

# Predecesores controlados por hash (deben permanecer intactos).
PREDECESSORS = [
    "outputs/polos_gastro/historico/experimentos/fase25_politica_e_integracion_editorial_v1/INFORME_POLOS_GASTRO_FASE25_POLITICA_EXPERIMENTAL_V1.pdf",
    "scripts/polos_gastro/historico/experimentos/fase25_politica_e_integracion_editorial_v1/generar_fase25_politica_experimental_v1.py",
    "docs/polos_gastro/historico/experimentos/fase25_politica_e_integracion_editorial_v1/contenido_fase25_politica_experimental_v1.yaml",
    "docs/polos_gastro/historico/experimentos/fase25_politica_e_integracion_editorial_v1/kpis_lock_preliminar.json",
    "outputs/polos_gastro/fase25_microajustes_finales_oficina/INFORME_POLOS_GASTRO_DGDGAS_11P_OFICINA_FASE25.pdf",
    "scripts/polos_gastro/build_fase25_microajustes_finales_oficina.py",
    "outputs/polos_gastro/historico/corrida_territorial_v3/KPI_LOCK_CARTOGRAFICO_V3.csv",
    "outputs/polos_gastro/historico/correcciones_cartograficas_post_qa_v3_1/mapas/mapa_general_institucional_v3_1.png",
    "outputs/polos_gastro/historico/correcciones_cartograficas_post_qa_v3_1/mapas/belgrano_institucional_v3_1.png",
    "outputs/polos_gastro/historico/correcciones_cartograficas_post_qa_v3_1/mapas/recoleta_institucional_v3_1.png",
    "outputs/polos_gastro/historico/correcciones_cartograficas_post_qa_v3_1/mapas/costanera_norte_institucional_v3_1.png",
    "outputs/polos_gastro/historico/correcciones_cartograficas_post_qa_v3_1/mapas/costanera_norte_media_pagina_v3_1.png",
]

# --- Identidad DGDGAS (heredada de la línea Fase 25 política; misma paleta) --------
W, H = A4
M = 44
TOTAL_PAGES = 10

AZUL = "#1F3B57"
ROJO = "#A23A2C"
VERDE = "#2F6E5B"
CELESTE = "#2C7FB8"
SLATE = "#5E6B78"
GRIS = "#566573"
NEGRO = "#1E252B"
LINEA = "#DDE3E9"
SOFT_AZUL = "#EAF1F8"
SOFT_VERDE = "#EAF5EE"
SOFT_COBRE = "#F8EDE0"
GRIS_CLARO = "#8A97A3"
WHITE = "#FFFFFF"

FONT = "Arial"
FONT_BOLD = "Arial-Bold"

MADUREZ_COLOR = {
    "lectura consolidada": AZUL,
    "lectura consolidada, con seguimiento": VERDE,
    "lectura en consolidación": SLATE,
    "delimitación adoptada": CELESTE,
}

# Estilo cartográfico V3.1 (tabla categoría→estilo del cartógrafo).
NAVY = "#17324D"
BLUE = "#2C7FB8"
TEAL = "#2F7D78"
GREEN = "#3D7C5F"
COPPER = "#C0762B"
LIGHT = "#F5F7FA"
ROAD = "#D7DEE5"
ROAD_MAJOR = "#AAB6C1"
MAP_SLATE = "#64748B"


# --- Utilidades -------------------------------------------------------------------

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


# --- Carga de contenido (YAML con fallback de subconjunto, como la línea V1) -------

def _strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        return value[1:-1]
    return value


def load_content(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        return yaml.safe_load(text)
    except ImportError:
        pass
    data: dict = {}
    section: dict | None = None
    current_list: list | None = None
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip())
        line = raw.strip()
        if indent == 0 and line.endswith(":"):
            section = {}
            data[line[:-1]] = section
            current_list = None
        elif indent == 2 and section is not None:
            if line.endswith(":"):
                current_list = []
                section[line[:-1]] = current_list
            else:
                key, _, value = line.partition(":")
                section[key.strip()] = _strip_quotes(value)
                current_list = None
        elif indent >= 4 and current_list is not None and line.startswith("- "):
            current_list.append(_strip_quotes(line[2:]))
        else:
            raise ValueError(f"Línea fuera del subconjunto YAML soportado: {raw!r}")
    return data


# --- Helpers de dibujo PDF (identidad heredada) -------------------------------------

def register_fonts() -> None:
    global FONT, FONT_BOLD
    regular = Path("C:/Windows/Fonts/arial.ttf")
    bold = Path("C:/Windows/Fonts/arialbd.ttf")
    if regular.exists() and bold.exists():
        pdfmetrics.registerFont(TTFont(FONT, str(regular)))
        pdfmetrics.registerFont(TTFont(FONT_BOLD, str(bold)))
    else:
        FONT, FONT_BOLD = "Helvetica", "Helvetica-Bold"


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


def draw_wrapped(c, text, x, y, width, *, font_name=None, size=10.0, color=NEGRO, leading=None) -> float:
    font_name = font_name or FONT
    leading = leading if leading is not None else size * 1.35
    c.setFont(font_name, size)
    set_fill(c, color)
    for line in wrap_text(text, font_name, size, width):
        c.drawString(x, y, line)
        y -= leading
    return y


def page_header(c, page: int, title: str, subtitle: str | None = None, estado: str | None = None) -> float:
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
    if estado:
        color = MADUREZ_COLOR.get(estado, GRIS_CLARO)
        label_w = pdfmetrics.stringWidth(estado, FONT, 8.2)
        cx = W - M - label_w - 12
        set_fill(c, color)
        c.circle(cx, y - 15, 2.6, fill=1, stroke=0)
        c.setFont(FONT, 8.2)
        set_fill(c, GRIS)
        c.drawString(cx + 8, y - 18, estado)
    y -= 23
    if subtitle:
        y = draw_wrapped(c, subtitle, M, y, W - 2 * M - 150, font_name=FONT_BOLD, size=10.5, color=GRIS, leading=13)
    set_stroke(c, LINEA)
    c.line(M, y - 8, W - M, y - 8)
    return y - 28


def page_footer(c, institucion: str, gobierno: str) -> None:
    set_stroke(c, LINEA)
    c.line(M, 46, W - M, 46)
    c.setFont(FONT, 7.8)
    set_fill(c, GRIS)
    c.drawString(M, 29, institucion)
    c.drawRightString(W - M, 29, gobierno)


def note_box(c, x, y, w, h, title, body, *, border=CELESTE, fill=SOFT_AZUL, size=8.8) -> None:
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


def draw_image_fit(c, path: Path, x, y, w, h) -> None:
    img = ImageReader(str(path))
    iw, ih = img.getSize()
    scale = min(w / iw, h / ih)
    dw, dh = iw * scale, ih * scale
    dx, dy = x + (w - dw) / 2, y + (h - dh) / 2
    c.drawImage(img, dx, dy, dw, dh, preserveAspectRatio=True, mask="auto")


# --- Preparación de assets ----------------------------------------------------------

def _trim_white(img: Image.Image, threshold: int = 253, pad: int = 12) -> Image.Image:
    arr = np.asarray(img.convert("L"))
    mask = arr < threshold
    rows = np.where(mask.any(axis=1))[0]
    cols = np.where(mask.any(axis=0))[0]
    if not len(rows) or not len(cols):
        return img
    top = max(int(rows[0]) - pad, 0)
    bottom = min(int(rows[-1]) + pad, img.height)
    left = max(int(cols[0]) - pad, 0)
    right = min(int(cols[-1]) + pad, img.width)
    return img.crop((left, top, right, bottom))


def prepare_v31_assets(cfg: dict) -> list[dict]:
    rows = []
    src_dir = ROOT / cfg["assets_v3_1"]["origen"]
    for dest_name, spec in cfg["assets_v3_1"]["insertados"].items():
        src = src_dir / spec["fuente"]
        img = Image.open(src).convert("RGB")
        left, top, right, bottom = spec["crop_pixels"]
        img = img.crop((left, top, min(right, img.width), min(bottom, img.height)))
        img = _trim_white(img)
        dest = ASSETS / dest_name
        img.save(dest, optimize=True)
        rows.append({
            "asset_insertado": dest_name, "origen": repo_rel(src), "sha256_origen": sha256(src),
            "sha256_insertado": sha256(dest), "transformacion": f"crop{spec['crop_pixels']} + trim_white",
            "linea_origen": "correcciones_cartograficas_post_qa_v3_1",
        })
    return rows


def add_background(ax, streets, barrios, bbox):
    minx, miny, maxx, maxy = bbox
    ax.set_facecolor("white")
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


def add_north_scale(ax, bbox, km=0.5):
    minx, miny, maxx, maxy = bbox
    dx, dy = maxx - minx, maxy - miny
    ax.annotate("N", xy=(maxx - dx * 0.045, maxy - dy * 0.06), ha="center", va="center", fontsize=10, fontweight="bold", color=NAVY)
    ax.annotate("", xy=(maxx - dx * 0.045, maxy - dy * 0.028), xytext=(maxx - dx * 0.045, maxy - dy * 0.092),
                arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=1.3))
    lon_km = km / (111.32 * math.cos(math.radians((miny + maxy) / 2)))
    x0, y0 = minx + dx * 0.06, miny + dy * 0.06
    ax.plot([x0, x0 + lon_km], [y0, y0], color=NAVY, lw=3, solid_capstyle="butt", zorder=20)
    ax.plot([x0, x0], [y0 - dy * 0.007, y0 + dy * 0.007], color=NAVY, lw=1)
    ax.plot([x0 + lon_km, x0 + lon_km], [y0 - dy * 0.007, y0 + dy * 0.007], color=NAVY, lw=1)
    ax.text(x0 + lon_km / 2, y0 + dy * 0.014, f"{int(km * 1000)} m", ha="center", va="bottom", fontsize=7.5, color=NAVY)


def label_box(ax, x, y, text, *, color=NAVY, size=9, weight="bold", ha="center"):
    ax.text(x, y, text, ha=ha, va="center", fontsize=size, fontweight=weight, color=color,
            bbox=dict(boxstyle="round,pad=0.28", fc="white", ec="none", alpha=0.94), zorder=30)


def bounds_with_padding(gdf, px=0.12, py=0.15):
    minx, miny, maxx, maxy = gdf.total_bounds
    return (minx - (maxx - minx) * px, miny - (maxy - miny) * py,
            maxx + (maxx - minx) * px, maxy + (maxy - miny) * py)


def save_map(fig, name: str, dpi: int) -> Path:
    dest = ASSETS / name
    fig.savefig(dest, dpi=dpi, facecolor="white")
    plt.close(fig)
    img = Image.open(dest).convert("RGB")
    _trim_white(img).save(dest, optimize=True)
    return dest


def render_new_maps(cfg: dict) -> list[dict]:
    dpi = cfg["render"]["dpi"]
    streets = gpd.read_file(ROOT / cfg["fondo"]["callejero"]).to_crs(4326)
    barrios = gpd.read_file(ROOT / cfg["fondo"]["barrios"]).to_crs(4326)
    rows = []

    def registrar(name, fuentes, nota):
        rows.append({
            "asset_insertado": name,
            "origen": "; ".join(repo_rel(ROOT / f) for f in fuentes),
            "sha256_origen": "; ".join(sha256(ROOT / f) for f in fuentes),
            "sha256_insertado": sha256(ASSETS / name),
            "transformacion": nota, "linea_origen": "render fase27 (estilo V3.1)",
        })

    # Palermo — delimitación vigente (misma del mapa general institucional V3.1).
    pal = gpd.GeoDataFrame(
        [{"nombre": nombre, "geometry": Polygon(coords)}
         for nombre, coords in cfg["palermo_delimitacion_vigente"]["poligonos"].items()], crs=4326)
    bbox = bounds_with_padding(pal, 0.20, 0.16)
    fig, ax = plt.subplots(figsize=(8.2, 9.6))
    fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02)
    add_background(ax, streets, barrios, bbox)
    pal.plot(ax=ax, facecolor=BLUE, edgecolor=BLUE, alpha=0.26, linewidth=1.6, zorder=10)
    label_box(ax, -58.4262, -34.5874, "Palermo Soho", color=BLUE, size=10)
    label_box(ax, -58.4398, -34.5852, "Palermo Hollywood", color=BLUE, size=10)
    label_box(ax, -58.4327, -34.5684, "Las Cañitas", color=BLUE, size=10)
    ax.legend(handles=[Patch(facecolor=BLUE, edgecolor=BLUE, alpha=0.26, label="Núcleo / área de identidad")],
              loc="lower right", fontsize=8, frameon=True, framealpha=0.95)
    add_north_scale(ax, bbox, 0.5)
    save_map(fig, "palermo_integrado_v2.png", dpi)
    registrar("palermo_integrado_v2.png", [cfg["fondo"]["callejero"], cfg["fondo"]["barrios"]],
              "render desde delimitación vigente (config; idéntica al mapa general V3.1)")

    # Corrientes — corredor continuo v2.1, separado de Abasto.
    cor = gpd.read_file(ROOT / cfg["capas_v21"]["corrientes"]).to_crs(4326)
    minx, miny, maxx, maxy = cor.total_bounds
    # Contexto vertical fijo: relación de aspecto ~1.8 para evitar una franja finita.
    lon_span = (maxx - minx) * 1.16
    lat_span = lon_span * math.cos(math.radians(-34.6)) / 1.8
    cx0, cy0 = (minx + maxx) / 2, (miny + maxy) / 2
    bbox = (cx0 - lon_span / 2, cy0 - lat_span / 2, cx0 + lon_span / 2, cy0 + lat_span / 2)
    fig, ax = plt.subplots(figsize=(11.4, 6.8))
    fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02)
    add_background(ax, streets, barrios, bbox)
    cor.plot(ax=ax, color=COPPER, linewidth=4.2, alpha=0.88, zorder=12, capstyle="round")
    label_box(ax, cx0, cy0 + lat_span * 0.16, "Av. Corrientes — corredor continuo", color=COPPER, size=10)
    ax.legend(handles=[Line2D([0], [0], color=COPPER, lw=4, label="Corredor gastronómico y cultural")],
              loc="lower right", fontsize=8, frameon=True, framealpha=0.95)
    add_north_scale(ax, bbox, 0.5)
    save_map(fig, "corrientes_integrado_v2.png", dpi)
    registrar("corrientes_integrado_v2.png",
              [cfg["capas_v21"]["corrientes"], cfg["fondo"]["callejero"], cfg["fondo"]["barrios"]],
              "render corredor v2.1 (línea 4pt, estilo CORREDOR V3.1); Abasto fuera de traza por decisión")

    # San Telmo — núcleo + eje Defensa contextual (v2.1).
    st_nucleo = gpd.read_file(ROOT / cfg["capas_v21"]["san_telmo_nucleo"]).to_crs(4326)
    st_defensa = gpd.read_file(ROOT / cfg["capas_v21"]["san_telmo_defensa"]).to_crs(4326)
    ambos = gpd.GeoDataFrame(geometry=list(st_nucleo.geometry) + list(st_defensa.geometry), crs=4326)
    bbox = bounds_with_padding(ambos, 0.30, 0.12)
    fig, ax = plt.subplots(figsize=(6.8, 8.6))
    fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02)
    add_background(ax, streets, barrios, bbox)
    st_defensa.plot(ax=ax, color=MAP_SLATE, linewidth=2.4, alpha=0.85, linestyle=(0, (4, 2)), zorder=11)
    st_nucleo.plot(ax=ax, facecolor=GREEN, edgecolor=GREEN, alpha=0.32, linewidth=1.8, zorder=12)
    nc = st_nucleo.iloc[0].geometry.representative_point()
    label_box(ax, nc.x, nc.y, "Núcleo\ngastronómico", color=GREEN, size=9)
    ax.legend(handles=[Patch(facecolor=GREEN, edgecolor=GREEN, alpha=0.32, label="Núcleo gastronómico"),
                       Line2D([0], [0], color=MAP_SLATE, lw=2.4, linestyle=(0, (4, 2)), label="Eje Defensa (contexto)")],
              loc="lower right", fontsize=7.6, frameon=True, framealpha=0.95)
    add_north_scale(ax, bbox, 0.5)
    save_map(fig, "san_telmo_integrado_v2.png", dpi)
    registrar("san_telmo_integrado_v2.png",
              [cfg["capas_v21"]["san_telmo_nucleo"], cfg["capas_v21"]["san_telmo_defensa"],
               cfg["fondo"]["callejero"], cfg["fondo"]["barrios"]],
              "render núcleo v2.1 + eje Defensa contextual (trazo discontinuo)")

    # Puerto Madero — frente doble PM_PRES_C (v2.1).
    pm_all = gpd.read_file(ROOT / cfg["capas_v21"]["puerto_madero_opciones"]).to_crs(4326)
    pm = pm_all[pm_all["opcion_id"] == cfg["capas_v21"]["puerto_madero_opcion_id"]].copy()
    assert len(pm) >= 1, "PM_PRES_C no encontrada"
    bbox = bounds_with_padding(pm, 0.85, 0.10)
    fig, ax = plt.subplots(figsize=(6.4, 9.2))
    fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02)
    add_background(ax, streets, barrios, bbox)
    pm.plot(ax=ax, color=TEAL, linewidth=4.0, alpha=0.88, zorder=12, capstyle="round")
    label_box(ax, bbox[0] + (bbox[2] - bbox[0]) * 0.24, (bbox[1] + bbox[3]) / 2, "Frente de\nlos diques", color=TEAL, size=9.4)
    ax.legend(handles=[Line2D([0], [0], color=TEAL, lw=4, label="Frente gastronómico (ambos márgenes)")],
              loc="lower left", fontsize=7.6, frameon=True, framealpha=0.95)
    add_north_scale(ax, bbox, 0.5)
    save_map(fig, "puerto_madero_integrado_v2.png", dpi)
    registrar("puerto_madero_integrado_v2.png",
              [cfg["capas_v21"]["puerto_madero_opciones"], cfg["fondo"]["callejero"], cfg["fondo"]["barrios"]],
              "render opción PM_PRES_C (frente doble, estilo FRENTE V3.1)")
    return rows


# --- Páginas ------------------------------------------------------------------------

def cover(c, meta: dict) -> None:
    set_fill(c, AZUL)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    set_fill(c, ROJO)
    c.rect(0, 0, 18, H, fill=1, stroke=0)
    set_fill(c, WHITE)
    y = H - 190
    c.setFont(FONT_BOLD, 29)
    for line in wrap_text(meta["titulo"], FONT_BOLD, 29, W - 2 * M - 20):
        c.drawString(M + 10, y, line)
        y -= 35
    c.setFont(FONT_BOLD, 17)
    for line in wrap_text(meta["subtitulo"], FONT_BOLD, 17, W - 2 * M - 20):
        c.drawString(M + 10, y - 14, line)
        y -= 24
    c.setFont(FONT, 12.2)
    c.drawString(M + 10, y - 68, meta["institucion"])
    c.drawString(M + 10, y - 88, meta["gobierno"])
    c.drawString(M + 10, y - 126, meta["fecha"])
    c.setFont(FONT_BOLD, 9.5)
    c.drawRightString(W - M, 32, f"1 / {TOTAL_PAGES}")
    c.showPage()


def sintesis_page(c, data: dict, meta: dict) -> None:
    sec = data["sintesis"]
    y = page_header(c, 2, sec["titulo"], sec["bajada"])
    yy = y - 2
    for paragraph in sec["parrafos"]:
        yy = draw_wrapped(c, paragraph, M + 8, yy, W - 2 * M - 16, size=11.0, leading=15.5)
        yy -= 13
    yy -= 4
    draw_wrapped(c, sec["encuadre"], M + 8, yy, W - 2 * M - 16, font_name=FONT_BOLD, size=10.6, color=AZUL, leading=15)
    note_box(c, M, 128, W - 2 * M, 128, sec["como_leer_titulo"], sec["como_leer"], border=CELESTE, fill=SOFT_AZUL, size=8.8)
    c.setFont(FONT, 8.4)
    set_fill(c, GRIS)
    for i, line in enumerate(wrap_text(sec["alcance_pie"], FONT, 8.4, W - 2 * M - 16)):
        c.drawString(M + 8, 72 - i * 11, line)
    page_footer(c, meta["institucion"], meta["gobierno"])
    c.showPage()


def mapa_general_page(c, data: dict, meta: dict) -> None:
    sec = data["mapa_general"]
    y = page_header(c, 3, sec["titulo"], sec["bajada"])
    box_h = 110
    box_y = 100
    draw_image_fit(c, ASSETS / sec["asset"], M - 6, box_y + box_h + 14, W - 2 * M + 12, y - box_y - box_h - 22)
    note_box(c, M, box_y, W - 2 * M, box_h, sec["lectura_titulo"], sec["lectura"], border=VERDE, fill=SOFT_VERDE, size=9.0)
    c.setFont(FONT, 7.9)
    set_fill(c, GRIS)
    for i, line in enumerate(wrap_text(sec["nota_pie"], FONT, 7.9, W - 2 * M - 16)):
        c.drawString(M + 8, 82 - i * 10, line)
    page_footer(c, meta["institucion"], meta["gobierno"])
    c.showPage()


def detalle_page(c, page: int, sec: dict, meta: dict, extra_key: str | None = None, extra_title_key: str | None = None) -> None:
    y = page_header(c, page, sec["titulo"], sec["bajada"], estado=sec.get("estado_lectura"))
    if extra_key:
        box_h, box_top = 158, 118 + 158
        draw_image_fit(c, ASSETS / sec["asset"], M - 4, box_top + 14, W - 2 * M + 8, y - box_top - 22)
        box_w = (W - 2 * M - 14) / 2
        note_box(c, M, 118, box_w, box_h, sec["lectura_titulo"], sec["lectura"], border=VERDE, fill=SOFT_VERDE, size=8.2)
        note_box(c, M + box_w + 14, 118, box_w, box_h, sec[extra_title_key], sec[extra_key], border=CELESTE, fill=SOFT_AZUL, size=8.2)
    else:
        box_h, box_top = 122, 128 + 122
        draw_image_fit(c, ASSETS / sec["asset"], M - 4, box_top + 14, W - 2 * M + 8, y - box_top - 22)
        note_box(c, M, 128, W - 2 * M, box_h, sec["lectura_titulo"], sec["lectura"], border=VERDE, fill=SOFT_VERDE, size=9.0)
    page_footer(c, meta["institucion"], meta["gobierno"])
    c.showPage()


def san_telmo_puerto_page(c, data: dict, meta: dict) -> None:
    sec = data["san_telmo_puerto_madero"]
    y = page_header(c, 6, sec["titulo"], sec["bajada"], estado=sec.get("estado_lectura"))
    col_w = (W - 2 * M - 18) / 2
    box_h, box_top = 150, 112 + 150
    map_h = y - box_top - 22
    draw_image_fit(c, ASSETS / sec["asset_san_telmo"], M, box_top + 14, col_w, map_h)
    draw_image_fit(c, ASSETS / sec["asset_puerto"], M + col_w + 18, box_top + 14, col_w, map_h)
    note_box(c, M, 112, col_w, box_h, sec["san_telmo_titulo"], sec["san_telmo"], border=VERDE, fill=SOFT_VERDE, size=8.2)
    note_box(c, M + col_w + 18, 112, col_w, box_h, sec["puerto_titulo"], sec["puerto"], border=CELESTE, fill=SOFT_AZUL, size=8.2)
    page_footer(c, meta["institucion"], meta["gobierno"])
    c.showPage()


def recoleta_page(c, data: dict, meta: dict) -> None:
    sec = data["recoleta"]
    y = page_header(c, 8, sec["titulo"], sec["bajada"], estado=sec.get("estado_lectura"))
    box_h, box_top = 150, 118 + 150
    draw_image_fit(c, ASSETS / sec["asset"], M - 4, box_top + 14, W - 2 * M + 8, y - box_top - 22)
    box_w = (W - 2 * M - 14) / 2
    note_box(c, M, 118, box_w, box_h, sec["lectura_titulo"], sec["lectura"], border=VERDE, fill=SOFT_VERDE, size=8.2)
    note_box(c, M + box_w + 14, 118, box_w, box_h, sec["diversidad_titulo"], sec["diversidad"], border=CELESTE, fill=SOFT_AZUL, size=8.2)
    page_footer(c, meta["institucion"], meta["gobierno"])
    c.showPage()


def costanera_page(c, data: dict, meta: dict) -> None:
    sec = data["costanera"]
    y = page_header(c, 9, sec["titulo"], sec["bajada"], estado=sec.get("estado_lectura"))
    yy = draw_wrapped(c, sec["lectura"], M + 8, y - 2, W - 2 * M - 16, size=11.0, leading=15.5)
    box_w = (W - 2 * M - 14) / 2
    box_h = 128
    top = yy - 20
    note_box(c, M, top - box_h, box_w, box_h, sec["adoptada_titulo"], sec["adoptada"], border=CELESTE, fill=SOFT_AZUL, size=8.2)
    note_box(c, M + box_w + 14, top - box_h, box_w, box_h, sec["territorio_titulo"], sec["territorio"], border=VERDE, fill=SOFT_VERDE, size=8.2)
    map_top = top - box_h - 14
    draw_image_fit(c, ASSETS / sec["asset"], M - 4, 62, W - 2 * M + 8, map_top - 62)
    page_footer(c, meta["institucion"], meta["gobierno"])
    c.showPage()


def cierre_page(c, data: dict, meta: dict) -> None:
    sec = data["cierre"]
    y = page_header(c, 10, sec["titulo"], sec["bajada"])
    yy = y - 4
    for item in sec["items"]:
        c.setFont(FONT_BOLD, 11)
        set_fill(c, ROJO)
        c.drawString(M + 8, yy, "•")
        yy = draw_wrapped(c, item, M + 26, yy, W - 2 * M - 34, size=10.4, leading=14.5)
        yy -= 10
    yy -= 2
    yy = draw_wrapped(c, sec["cierre"], M + 8, yy, W - 2 * M - 16, font_name=FONT_BOLD, size=10.2, color=AZUL, leading=14.5)
    yy -= 18
    for key in ("fuentes", "representacion", "alcance"):
        c.setFont(FONT_BOLD, 11.0)
        set_fill(c, AZUL)
        c.drawString(M + 8, yy, sec[f"{key}_titulo"])
        yy -= 17
        yy = draw_wrapped(c, sec[key], M + 8, yy, W - 2 * M - 16, size=9.6, leading=13.5)
        yy -= 16
    page_footer(c, meta["institucion"], meta["gobierno"])
    c.showPage()


def build_pdf(data: dict) -> None:
    meta = data["meta"]
    c = canvas.Canvas(str(PDF_OUT), pagesize=A4)
    c.setTitle(f"{meta['titulo']} — {meta['subtitulo']}")
    c.setAuthor(meta["institucion"])
    c.setSubject(meta["pdf_subject"])
    cover(c, meta)
    sintesis_page(c, data, meta)
    mapa_general_page(c, data, meta)
    detalle_page(c, 4, data["palermo"], meta)
    detalle_page(c, 5, data["corrientes"], meta, extra_key="abasto", extra_title_key="abasto_titulo")
    san_telmo_puerto_page(c, data, meta)
    detalle_page(c, 7, data["belgrano"], meta, extra_key="observacion", extra_title_key="observacion_titulo")
    recoleta_page(c, data, meta)
    costanera_page(c, data, meta)
    cierre_page(c, data, meta)
    c.save()


# --- QA -----------------------------------------------------------------------------

def render_pages() -> list[Path]:
    QA_PNG.mkdir(parents=True, exist_ok=True)
    paths = []
    with fitz.open(PDF_OUT) as doc:
        for i, page in enumerate(doc, 1):
            pix = page.get_pixmap(dpi=150)
            dest = QA_PNG / f"pagina_{i:02d}.png"
            pix.save(dest)
            paths.append(dest)
    return paths


def structural_qa() -> dict:
    result = {"archivo": repo_rel(PDF_OUT), "abre": True}
    with fitz.open(PDF_OUT) as doc:
        result["paginas"] = doc.page_count
        sizes = {f"{round(p.rect.width, 2)}x{round(p.rect.height, 2)}" for p in doc}
        result["dimensiones"] = sorted(sizes)
        result["dimensiones_consistentes"] = len(sizes) == 1
        fonts = set()
        blank_pages, out_of_page, text_pages = [], [], 0
        for i, page in enumerate(doc, 1):
            fonts.update(f[3] for f in page.get_fonts(full=True))
            text = page.get_text().strip()
            if text:
                text_pages += 1
            pix = page.get_pixmap(dpi=60)
            arr = np.frombuffer(pix.samples, dtype=np.uint8)
            if float(arr.std()) < 1.0:
                blank_pages.append(i)
            for block in page.get_text("blocks"):
                bx0, by0, bx1, by1 = block[:4]
                if bx0 < -2 or by0 < -2 or bx1 > page.rect.width + 2 or by1 > page.rect.height + 2:
                    out_of_page.append(i)
        result["fuentes"] = sorted(fonts)
        result["paginas_con_texto_extraible"] = text_pages
        result["paginas_en_blanco"] = blank_pages
        result["bloques_fuera_de_pagina"] = sorted(set(out_of_page))
    result["resultado"] = ("APTO" if result["paginas"] == TOTAL_PAGES and result["dimensiones_consistentes"]
                           and not result["paginas_en_blanco"] and not result["bloques_fuera_de_pagina"] else "NO_APTO")
    return result


TEXTUAL_TERMS = ["DataGastro", "EXPERIMENTAL", "NO OFICIAL", "BEL-A", "REC-A", "CN-DEC10", "CN_C0",
                 "Places", "placeholder", "exploratoria", "candidata", "preliminar", "borrador",
                 "prueba", "containers", "Dirección General de Gastronomía"]


def textual_scan() -> list[dict]:
    rows = []
    corpora = {}
    with fitz.open(PDF_OUT) as doc:
        for i, page in enumerate(doc, 1):
            corpora[f"PDF pagina {i}"] = page.get_text()
        pdf_meta = doc.metadata or {}
    corpora["PDF metadatos"] = " ".join(str(v) for v in pdf_meta.values() if v)
    corpora["YAML contenido"] = CONTENT.read_text(encoding="utf-8")
    svg_dir = V31_MAPAS
    for svg in sorted(svg_dir.glob("*.svg")):
        corpora[f"SVG fuente V3.1 {svg.name}"] = svg.read_text(encoding="utf-8", errors="replace")
    for origin, text in corpora.items():
        low = text.casefold()
        for term in TEXTUAL_TERMS:
            t = term.casefold()
            start = 0
            while True:
                idx = low.find(t, start)
                if idx < 0:
                    break
                # Evitar falsos positivos por subcadenas dentro de palabras (p.ej. "aprueba").
                before = low[idx - 1] if idx > 0 else " "
                after = low[idx + len(t)] if idx + len(t) < len(low) else " "
                if not (before.isalnum() or after.isalnum()) or term in ("CN_C0",):
                    ctx = re.sub(r"\s+", " ", text[max(0, idx - 45): idx + len(t) + 45]).strip()
                    rows.append({"origen": origin, "termino": term, "contexto": ctx})
                start = idx + len(t)
    return rows


def protected_digest() -> dict:
    patterns = [
        "PolosGastro/**", "docs/polos_gastro/fase25_microajustes_finales_oficina/**",
        "outputs/polos_gastro/fase25_microajustes_finales_oficina/**",
        "scripts/polos_gastro/build_fase25_microajustes_finales_oficina.py",
        "outputs/polos_gastro/historico/experimentos/google_places_microzonas_ampliacion_v1/fase26_comparativa_cartografia/**",
        "outputs/polos_gastro/historico/experimentos/google_places_microzonas_ampliacion_v1/completa_v1/**",
        "outputs/polos_gastro/historico/experimentos/google_places_microzonas_ampliacion_v1/cartografia_*/**",
        "docs/polos_gastro/historico/experimentos/pipeline_hibrido_tipo_territorial_v1/**",
        "outputs/polos_gastro/historico/experimentos/pipeline_hibrido_tipo_territorial_v1/**",
        "docs/polos_gastro/historico/experimentos/pipeline_hibrido_repeticiones_v2/**",
        "outputs/polos_gastro/historico/experimentos/pipeline_hibrido_repeticiones_v2/**",
        "docs/polos_gastro/historico/experimentos/pipeline_hibrido_integracion_v21/**",
        "outputs/polos_gastro/historico/experimentos/pipeline_hibrido_integracion_v21/**",
        "outputs/polos_gastro/historico/REVISION_EVIDENCIA_DOCUMENTAL_POLOS_V1/**", "src/build_*.py",
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
    rows = [{"ruta": p.relative_to(root).as_posix(), "bytes": p.stat().st_size, "sha256": sha256(p), "fecha": DATE}
            for p in sorted(files)]
    write_csv(path, rows, ["ruta", "bytes", "sha256", "fecha"])
    return rows


def build_pack() -> dict:
    if PACK.exists():
        shutil.rmtree(PACK)
    (PACK / "docs").mkdir(parents=True, exist_ok=True)
    for p in sorted(DOCS.iterdir()):
        if p.is_file():
            shutil.copy2(p, PACK / "docs" / p.name)
    shutil.copy2(PDF_OUT, PACK / PDF_OUT.name)
    shutil.copytree(QA_PNG, PACK / QA_PNG.name)
    shutil.copytree(ASSETS, PACK / "assets")
    (PACK / "metadatos").mkdir(exist_ok=True)
    for p in sorted(META.iterdir()):
        if p.is_file():
            shutil.copy2(p, PACK / "metadatos" / p.name)
    script_dest = PACK / "scripts"
    script_dest.mkdir(exist_ok=True)
    for name in (Path(__file__).name, CONTENT.name, CONFIG.name, "README_REPRODUCCION.md"):
        src = SCRIPTS / name
        if src.exists():
            shutil.copy2(src, script_dest / name)
    write_text(PACK / "README.md",
               "# Revisión — Informe político integrado V2 (fase27)\n\n"
               "Paquete de revisión de la línea experimental integrada V2. Contiene el PDF de 10 páginas, "
               "las páginas renderizadas, los assets efectivamente insertados, la capa editable, el generador, "
               "la documentación de QA y el handoff al auditor final. No contiene datos fuente, puntos "
               "individuales, GeoJSON interno, credenciales, cachés ni paquetes históricos. El manifest excluye "
               "por diseño al propio manifest y a CHECKSUMS_SHA256.txt (generado después, orden V1.1.1).\n")
    metadata = {"paquete": "REVISION_INFORME_POLITICO_INTEGRADO_V2", "fecha": DATE,
                "estado": "PENDIENTE_QA_FINAL_INDEPENDIENTE_Y_REVISION_DIEGO",
                "rol": "integrador_tecnico_editorial", "red_usada": False, "apis_usadas": False,
                "exclusiones": ["datos fuente", "puntos individuales", "GeoJSON interno", "paquetes históricos",
                                 "credenciales", "caches", "temporales", ".git", ".graphify", "node_modules"]}
    (PACK / "metadata_paquete_v2.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest = PACK / "MANIFEST_CONTENIDO.csv"
    checks = PACK / "CHECKSUMS_SHA256.txt"
    rows = make_manifest(PACK, manifest, exclusions=(checks,))
    write_text(checks, "\n".join(f"{r['sha256']}  {r['ruta']}" for r in rows) +
               f"\n{sha256(manifest)}  MANIFEST_CONTENIDO.csv")
    with zipfile.ZipFile(ZIP_OUT, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for p in sorted(PACK.rglob("*")):
            if p.is_file():
                zf.write(p, PACK.name + "/" + p.relative_to(PACK).as_posix())
    with zipfile.ZipFile(ZIP_OUT) as zf:
        assert zf.testzip() is None
        names = zf.namelist()
        assert all(".." not in Path(n).parts and not Path(n).is_absolute() and "\\" not in n for n in names)
        forbidden = ["PUNTOS_ASOCIADOS", "ASIGNACION_PUNTOS", "place_id", ".env", "api_key", "node_modules", ".graphify"]
        assert not any(term.lower() in n.lower() for term in forbidden for n in names)
    return {"zip": ZIP_OUT.name, "bytes": ZIP_OUT.stat().st_size, "sha256": sha256(ZIP_OUT),
            "testzip": "OK", "archivos_manifest": len(rows), "resultado": "APTO"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-pack", action="store_true", help="omite paquete de revisión y ZIP")
    args = parser.parse_args()

    for p in (OUT, ASSETS, META):
        p.mkdir(parents=True, exist_ok=True)

    write_text(META / "GIT_STATUS_PRE_GENERACION.txt", run_git("status", "--short"))
    write_text(META / "GIT_DIFF_CACHED_PRE.txt", run_git("diff", "--cached", "--name-only"))
    protected_pre = protected_digest()
    pred_pre = {p: sha256(ROOT / p) for p in PREDECESSORS}

    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    register_fonts()
    data = load_content(CONTENT)

    asset_rows = prepare_v31_assets(cfg) + render_new_maps(cfg)
    write_csv(META / "ASSETS_TRAZABILIDAD_V2.csv", asset_rows, list(asset_rows[0]))

    build_pdf(data)
    render_pages()

    qa = structural_qa()
    (META / "QA_ESTRUCTURAL_V2.json").write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    scan_rows = textual_scan()
    write_csv(META / "QA_TEXTUAL_SCAN_RAW_V2.csv", scan_rows or
              [{"origen": "(sin coincidencias)", "termino": "", "contexto": ""}], ["origen", "termino", "contexto"])

    protected_post = protected_digest()
    assert protected_pre == protected_post, "Superficies protegidas modificadas"
    pred_post = {p: sha256(ROOT / p) for p in PREDECESSORS}
    pred_rows = [{"archivo": p, "sha256_pre": pred_pre[p], "sha256_post": pred_post[p],
                  "resultado": "SIN_CAMBIOS" if pred_pre[p] == pred_post[p] else "CAMBIO"} for p in PREDECESSORS]
    assert all(r["resultado"] == "SIN_CAMBIOS" for r in pred_rows)
    write_csv(META / "VERIFICACION_PREDECESORES_V2.csv", pred_rows, ["archivo", "sha256_pre", "sha256_post", "resultado"])
    (META / "QA_SUPERFICIES_PROTEGIDAS_V2.json").write_text(json.dumps(
        {"pre": protected_pre, "post": protected_post, "diferencias": 0,
         "registro": repo_rel(PROTECTED_YAML), "resultado": "SIN_CAMBIOS"}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")

    metadata = {"fase": FASE, "fecha": DATE, "generado_utc": datetime.now(timezone.utc).isoformat(),
                "rol": "integrador_tecnico_editorial", "infraestructura": "V1.1.1",
                "pdf": repo_rel(PDF_OUT), "pdf_sha256": sha256(PDF_OUT), "paginas": TOTAL_PAGES,
                "base_editorial": {p: pred_pre[p] for p in PREDECESSORS[:4]},
                "api_calls": 0, "network_requests": 0, "clustering_runs": 0,
                "decisiones_aplicadas": ["7 zonas seleccionadas", "Belgrano un polo / 3 centralidades / Belgrano R sector secundario",
                                          "Recoleta unidad pública única", "Costanera Norte polo multiparte de 4 componentes (CN_C02 pleno)",
                                          "Corrientes corredor continuo v2.1 separado de Abasto", "San Telmo núcleo + Defensa contextual",
                                          "Puerto Madero PM_PRES_C", "Palermo delimitación vigente"]}
    (META / "METADATA_INFORME_POLITICO_INTEGRADO_V2.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_text(META / "GIT_STATUS_POST_GENERACION.txt", run_git("status", "--short"))
    write_text(META / "GIT_DIFF_CACHED_POST.txt", run_git("diff", "--cached", "--name-only"))

    manifest = OUT / "MANIFEST_CONTENIDO.csv"
    make_manifest(OUT, manifest,
                  exclusions=(ZIP_OUT, OUT / "CHECKSUMS_SHA256.txt"),
                  exclude_dirs=(PACK,))
    summary = {"pdf": repo_rel(PDF_OUT), "paginas": qa["paginas"], "qa_estructural": qa["resultado"],
               "hallazgos_scan_textual": len(scan_rows)}
    if not args.no_pack:
        pack_info = build_pack()
        write_text(OUT / "CHECKSUMS_SHA256.txt",
                   f"{sha256(manifest)}  MANIFEST_CONTENIDO.csv\n"
                   f"{sha256(PDF_OUT)}  {PDF_OUT.name}\n"
                   f"{sha256(ZIP_OUT)}  {ZIP_OUT.name}")
        summary["zip"] = pack_info
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
