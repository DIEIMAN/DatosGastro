"""Genera la version FINAL del informe Cafecito DataGastro.

Correccion minima (microcorreccion) sobre la maqueta V6: ajusta
terminologia de sedes (solo "marcas/cafeterias vinculadas") en 
anexo metodologico, apaga el color de la categoria minoritaria 
de genero para mayor consistencia visual. Y cambia DATAGASTRO a DataGastro.

No modifica contenido analitico, narrativa ni estructura general.
Lee el XLSX original en modo solo lectura y no lo modifica.

Reglas del PDF publico:
  - No incluye rutas, nombres de archivos, extensiones, scripts, hashes,
    identificadores de servicios externos ni referencias a versiones internas.
  - El publico encuestado solo se muestra agregado por comuna.
  - Las sedes de cafeterias se mapean solo si usar_en_mapa == "si".
  - No se afirma representatividad ni participacion fisica de cada sede.

Uso:
    python scripts/cafecito/generar_informe_datagastro_final.py
"""
from __future__ import annotations

import csv
import json
import re
import shutil
import sys
import textwrap
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.image as mpimg  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.cafecito import analizar_cafecito as base  # noqa: E402
from scripts.cafecito import mejorar_analitica_cafecito as mejora  # noqa: E402

DOCS_DIR = REPO_ROOT / "docs" / "cafecito"
OUT_DIR = REPO_ROOT / "outputs" / "cafecito"
GRAF_DIR = OUT_DIR / "graficos_datagastro"
FINAL_DIR = REPO_ROOT / "Cafesito" / "final"
RAW_DIR = REPO_ROOT / "data" / "raw"

REPORT_MD = DOCS_DIR / "INFORME_CAFECITO_EXPLORATORIO.md"
README_MD = DOCS_DIR / "README_CAFECITO.md"
PDF_FINAL = OUT_DIR / "INFORME_CAFECITO_DATAGASTRO_FINAL.pdf"
FINAL_PDF = FINAL_DIR / "INFORME_CAFECITO_DATAGASTRO_FINAL.pdf"

RANKING_COMUNAL = OUT_DIR / "ranking_comunal_cafecito.csv"
SEDES_CSV = OUT_DIR / "cafeterias_sedes_caba_geocodificadas.csv"
RESUMEN_SEDES_COMUNA = OUT_DIR / "resumen_sedes_cafeterias_por_comuna.csv"
RESUMEN_SEDES_BARRIO = OUT_DIR / "resumen_sedes_cafeterias_por_barrio.csv"

# Mapas remaquetados para la V4 (no sobrescriben los PNG de la V3).
MAPA_COMUNAL = GRAF_DIR / "mapa_comunal_publico_final.png"
MAPA_SEDES = GRAF_DIR / "mapa_sedes_cafeterias_final.png"
MAPA_COMBINADO = GRAF_DIR / "mapa_cafeterias_y_publico_final.png"
PLAN_BARRAS = GRAF_DIR / "tipo_plan_barras_final.png"

FOOTER = "DataGastro · Cafecito BA en tu barrio · Informe exploratorio"

A4 = (8.27, 11.69)
INK = "#1f3b57"
BLUE = "#2c7fb8"
ORANGE = "#c0762b"
GREEN = "#1a9850"
COFFEE = "#6f4e37"
GREY = "#555555"
LIGHT = "#eef2f6"
SOFT_BLUE = "#eaf1f8"
SOFT_ORANGE = "#f7ebdc"
SOFT_GREEN = "#eaf6ef"
LINE = "#d9dee5"
WHITE = "#ffffff"

DISPLAY = {
    "Si, es la primera vez": "Sí, es la primera vez",
    "No, ya participé de otros eventos": "Ya participó de otros eventos",
    "Si, acepto": "Sí, acepto",
    "Varon": "Varón",
    "No binario": "No binario",
    "65 o mas": "65 o más",
    "Pasteleria": "Pastelería",
    "Conocer propuestas gastronomicas nuevas": "Conocer propuestas nuevas",
    "Probar café / cafeterías": "Probar café / cafeterías",
    "Pase por la zona y lo ví": "Pasó por la zona",
    "Por amigos, familia o conocidos": "Amigos, familia o conocidos",
    "Web o pagina oficial de la Ciudad": "Web/página Ciudad",
    "Opciones sin tac": "Opciones sin TACC",
    "Opciones sin tacc": "Opciones sin TACC",
    "Por las opciones sin tacc": "Por las opciones sin TACC",
    "Por las opciones sin tac": "Por las opciones sin TACC",
    "En pareja": "En pareja",
    "Con amigos/as": "Con amigos/as",
    "Con familia": "Con familia",
}

TEXT_REPL = {
    "cafeterias": "cafeterías",
    "gastronomicas": "gastronómicas",
    "gastronomicos": "gastronómicos",
    "programacion": "programación",
    "comunicacion": "comunicación",
    "fidelizacion": "fidelización",
    "captacion": "captación",
    "difusion": "difusión",
    "decision": "decisión",
    "gestion": "gestión",
    "publico": "público",
    "publicos": "públicos",
    "senal": "señal",
    "senales": "señales",
    "metodologico": "metodológico",
    "metodologica": "metodológica",
    "pagina": "página",
    "validas": "válidas",
    "interes": "interés",
    "proximos": "próximos",
    "proximas": "próximas",
}


def clean_text(value: str) -> str:
    fixed = DISPLAY.get(value, value)
    for old, new in sorted(TEXT_REPL.items(), key=lambda x: len(x[0]), reverse=True):
        fixed = re.sub(rf"\b{re.escape(old)}\b", new, fixed)
    return fixed


def wrap_text(value: str, width: int) -> list[str]:
    return textwrap.wrap(clean_text(value), width=width, break_long_words=False) or [""]


def pct(n: int, d: int) -> float:
    return (n / d * 100) if d else 0.0


def pct_s(n: int, d: int, digits: int = 0) -> str:
    return f"{pct(n, d):.{digits}f}%"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


# --------------------------------------------------------------------- stats

def build_stats(records: list[dict]) -> dict[str, dict]:
    stats: dict[str, dict] = {}
    for key in base.CERRADAS_SIMPLES:
        counter = base.count_simple(records, key)
        stats[key] = {"items": base.ordered_items(key, counter), "base": sum(counter.values()), "multi": False}
    for key in base.CERRADAS_MULTI:
        counter, base_n = base.count_multi(records, key)
        stats[key] = {"items": counter.most_common(), "base": base_n, "multi": True}
    return stats


def items_dict(stats: dict, key: str) -> dict[str, int]:
    return dict(stats[key]["items"])


def young_adult_count(stats: dict) -> int:
    ages = items_dict(stats, "rango_edad")
    return ages.get("18 a 24", 0) + ages.get("25 a 34", 0) + ages.get("35 a 44", 0)


def stats_payload(records: list[dict], stats: dict) -> dict[str, int]:
    channel = items_dict(stats, "como_se_entero")
    interest = items_dict(stats, "que_intereso")
    future = items_dict(stats, "eventos_futuros")
    first = items_dict(stats, "primera_vez")
    contact = items_dict(stats, "acepta_contacto")
    where = items_dict(stats, "donde_vivis")
    gender = items_dict(stats, "genero")
    plan = items_dict(stats, "con_quien")
    return {
        "n": len(records),
        "young": young_adult_count(stats),
        "caba": where.get("CABA", 0),
        "instagram": channel.get("Instagram", 0),
        "interpersonal": channel.get("Por amigos, familia o conocidos", 0),
        "paso_zona": channel.get("Pase por la zona y lo ví", 0),
        "coffee": interest.get("Probar café / cafeterías", 0),
        "paseo": interest.get("Pasear o hacer una salida", 0),
        "nuevas": interest.get("Conocer propuestas gastronomicas nuevas", 0),
        "vino": future.get("Vino", 0),
        "pasteleria": future.get("Pasteleria", 0),
        "food_trucks": future.get("Food trucks", 0),
        "cafe_futuro": future.get("Café", 0),
        "ferias": future.get("Ferias y mercados", 0),
        "first_time": first.get("Si, es la primera vez", 0),
        "recurrent": first.get("No, ya participé de otros eventos", 0),
        "contact_yes": contact.get("Si, acepto", 0),
        "contact_base": stats["acepta_contacto"]["base"],
        "mujer": gender.get("Mujer", 0),
        "pareja": plan.get("En pareja", 0),
        "amigos": plan.get("Con amigos/as", 0),
        "familia": plan.get("Con familia", 0),
    }


# ---------------------------------------------------------------- page utils

def page() -> plt.Figure:
    fig = plt.figure(figsize=A4)
    fig.patch.set_facecolor("white")
    return fig


def footer(fig: plt.Figure) -> None:
    fig.lines.append(Line2D([0.065, 0.935], [0.055, 0.055], color=LINE, lw=0.8, transform=fig.transFigure))
    fig.text(0.065, 0.035, FOOTER, color=GREY, fontsize=7.8, va="center")


def header(fig: plt.Figure, page_no: int, title: str, subtitle: str = "", kicker: str = "DataGastro") -> float:
    fig.text(0.065, 0.958, kicker, color=ORANGE, fontsize=8.5, fontweight="bold")
    fig.text(0.935, 0.958, f"Pág. {page_no}", color=GREY, fontsize=8.5, ha="right")
    y = 0.925
    for line in wrap_text(title, 45):
        fig.text(0.065, y, line, color=INK, fontsize=18, fontweight="bold", va="top")
        y -= 0.032
    fig.lines.append(Line2D([0.065, 0.34], [y + 0.007, y + 0.007], color=ORANGE, lw=2.3, transform=fig.transFigure))
    if subtitle:
        for line in wrap_text(subtitle, 95):
            fig.text(0.065, y - 0.010, line, color=GREY, fontsize=10.2, style="italic", va="top")
            y -= 0.022
    return y - 0.026


def add_box(
    fig: plt.Figure,
    x: float,
    y: float,
    w: float,
    h: float,
    title: str,
    body: str | list[str],
    *,
    face: str = LIGHT,
    edge: str = BLUE,
    title_color: str = INK,
    body_size: float = 8.8,
    title_size: float = 9.2,
    bullet: bool = False,
) -> None:
    fig.patches.append(Rectangle((x, y), w, h, transform=fig.transFigure, facecolor=face, edgecolor=edge, lw=1.1))
    fig.text(x + 0.015, y + h - 0.022, clean_text(title), color=title_color, fontsize=title_size, fontweight="bold", va="top")
    text_items = body if isinstance(body, list) else [body]
    yy = y + h - 0.048
    wrap_width = max(24, int(w * 118))
    for item in text_items:
        prefix = "• " if bullet else ""
        lines = wrap_text(prefix + item, wrap_width)
        for line in lines:
            if yy < y + 0.010:
                return
            fig.text(x + 0.015, yy, line, color="#222222", fontsize=body_size, va="top")
            yy -= 0.017
        yy -= 0.006


def add_kpi_cards(fig: plt.Figure, cards: list[tuple[str, str, str]], y: float, *, x: float = 0.065, w: float = 0.87, h: float = 0.105) -> None:
    gap = 0.014
    cw = (w - gap * (len(cards) - 1)) / len(cards)
    for i, (value, label, note) in enumerate(cards):
        xx = x + i * (cw + gap)
        primary = i == 0
        face = INK if primary else WHITE
        edge = INK if primary else LINE
        val_color = ORANGE if primary else INK
        lab_color = WHITE if primary else INK
        note_color = "#dfe8f1" if primary else GREY
        fig.patches.append(FancyBboxPatch(
            (xx, y), cw, h,
            boxstyle="round,pad=0.010,rounding_size=0.012",
            transform=fig.transFigure,
            facecolor=face,
            edgecolor=edge,
            lw=1.2,
        ))
        fig.text(xx + cw / 2, y + h * 0.64, clean_text(value), ha="center", va="center", color=val_color, fontsize=18, fontweight="bold")
        fig.text(xx + cw / 2, y + h * 0.38, clean_text(label), ha="center", va="center", color=lab_color, fontsize=8.4, fontweight="bold")
        fig.text(xx + cw / 2, y + h * 0.16, clean_text(note), ha="center", va="center", color=note_color, fontsize=7.2)


def style_axis(ax) -> None:
    ax.set_facecolor("white")
    for side in ("top", "right", "bottom"):
        ax.spines[side].set_visible(False)
    ax.spines["left"].set_color(LINE)
    ax.tick_params(axis="x", length=0, labelbottom=False)
    ax.tick_params(axis="y", labelsize=7.7, colors="#222222")


def hbar(
    fig: plt.Figure,
    rect: list[float],
    items: list[tuple[str, int]],
    base_n: int,
    title: str,
    *,
    color: str = BLUE,
    accents: set[str] | None = None,
    limit: int | None = None,
    multi: bool = False,
) -> None:
    accents = accents or set()
    chosen = items[:limit] if limit else items
    chosen = list(reversed(chosen))
    labels = ["\n".join(wrap_text(DISPLAY.get(label, label), 18)) for label, _ in chosen]
    values = [value for _, value in chosen]
    colors = [ORANGE if label in accents else color for label, _ in chosen]
    ax = fig.add_axes(rect)
    ypos = list(range(len(chosen)))
    ax.barh(ypos, values, color=colors, height=0.62)
    style_axis(ax)
    ax.set_yticks([])
    max_v = max(values) if values else 1
    label_x = -max_v * 0.66
    for i, label in enumerate(labels):
        ax.text(label_x * 0.96, i, label, va="center", ha="left", color="#222222", fontsize=7.4)
    for i, value in enumerate(values):
        ax.text(value + max_v * 0.025, i, f"{value} ({pct_s(value, base_n)})", va="center", color=INK, fontsize=7.6, fontweight="bold")
    ax.axvline(0, color=LINE, lw=0.8)
    ax.set_xlim(label_x * 1.10, max_v * 1.26)
    ax.set_title(clean_text(title), loc="left", fontsize=10.5, color=INK, fontweight="bold", pad=12)
    note = f"Base: n={base_n}" + (" · multi-respuesta" if multi else "")
    ax.text(0, -0.175, clean_text(note), transform=ax.transAxes, fontsize=7.4, color=GREY, va="top")


def donut(fig: plt.Figure, rect: list[float], items: list[tuple[str, int]], title: str, center: str, colors: list[str]) -> None:
    ax = fig.add_axes(rect)
    values = [value for _, value in items]
    labels = [clean_text(label) for label, _ in items]
    wedges, _ = ax.pie(values, startangle=90, counterclock=False, colors=colors[:len(items)],
                       wedgeprops={"width": 0.38, "edgecolor": "white", "linewidth": 1.6})
    ax.text(0, 0.03, clean_text(center), ha="center", va="center", color=INK, fontsize=13, fontweight="bold")
    legend = [f"{label}: {value}" for label, value in zip(labels, values)]
    ax.legend(wedges, legend, loc="lower center", bbox_to_anchor=(0.5, -0.20), frameon=False, fontsize=7.3, ncol=1)
    ax.set_title(clean_text(title), loc="left", fontsize=10.5, color=INK, fontweight="bold", pad=10)


def stacked(fig: plt.Figure, rect: list[float], items: list[tuple[str, int]], base_n: int, title: str, colors: list[str]) -> None:
    ax = fig.add_axes(rect)
    left = 0.0
    for i, (label, value) in enumerate(items):
        width = pct(value, base_n)
        ax.barh([0], [width], left=left, color=colors[i % len(colors)], height=0.46)
        if width >= 8:
            ax.text(left + width / 2, 0, f"{clean_text(label)}\n{width:.0f}%", ha="center", va="center", fontsize=7.2, color="white", fontweight="bold")
        left += width
    ax.set_xlim(0, 100)
    ax.set_ylim(-0.55, 0.55)
    ax.axis("off")
    ax.set_title(clean_text(title), loc="left", fontsize=10.5, color=INK, fontweight="bold", pad=10)
    ax.text(0, -0.42, f"Base: n={base_n}", transform=ax.transAxes, fontsize=7.4, color=GREY, va="top")


def crop_white_margins(img: np.ndarray, threshold: float = 0.985) -> np.ndarray:
    rgb = img[:, :, :3] if img.ndim == 3 else img
    mask = np.any(rgb < threshold, axis=2)
    coords = np.argwhere(mask)
    if coords.size == 0:
        return img
    y0, x0 = coords.min(axis=0)
    y1, x1 = coords.max(axis=0) + 1
    pad_y = max(8, int((y1 - y0) * 0.03))
    pad_x = max(8, int((x1 - x0) * 0.03))
    y0 = max(0, y0 - pad_y)
    x0 = max(0, x0 - pad_x)
    y1 = min(img.shape[0], y1 + pad_y)
    x1 = min(img.shape[1], x1 + pad_x)
    return img[y0:y1, x0:x1]


def add_image(fig: plt.Figure, path: Path, rect: list[float], title: str = "") -> None:
    ax = fig.add_axes(rect)
    ax.imshow(crop_white_margins(mpimg.imread(path)), aspect="auto")
    ax.axis("off")
    if title:
        ax.set_title(clean_text(title), loc="left", fontsize=10.5, color=INK, fontweight="bold", pad=4)


def mini_table(fig: plt.Figure, x: float, y: float, w: float, h: float, rows: list[tuple[str, str, str]], title: str) -> None:
    fig.text(x, y + h + 0.010, clean_text(title), color=INK, fontsize=10, fontweight="bold")
    row_h = h / max(1, len(rows))
    for i, (a, b, c) in enumerate(rows):
        yy = y + h - (i + 1) * row_h
        face = LIGHT if i % 2 == 0 else WHITE
        fig.patches.append(Rectangle((x, yy), w, row_h - 0.002, transform=fig.transFigure, facecolor=face, edgecolor=LINE, lw=0.5))
        fig.text(x + 0.012, yy + row_h * 0.56, clean_text(a), fontsize=7.8, color=INK, fontweight="bold", va="center")
        fig.text(x + w * 0.55, yy + row_h * 0.56, clean_text(b), fontsize=7.8, color="#222222", va="center", ha="center")
        fig.text(x + w * 0.83, yy + row_h * 0.56, clean_text(c), fontsize=7.8, color="#222222", va="center", ha="center")


def crosstab(records: list[dict], a_key: str, b_key: str) -> dict[str, Counter]:
    table: dict[str, Counter] = defaultdict(Counter)
    for record in records:
        a = base.norm_space(record.get(a_key, ""))
        b = base.norm_space(record.get(b_key, ""))
        if a and b:
            table[a][b] += 1
    return table


# ------------------------------------------------------------- nuevos graficos

def load_geo(name: str) -> dict | None:
    path = RAW_DIR / name
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def rings(geom: dict) -> list[list[list[float]]]:
    if geom["type"] == "Polygon":
        return [geom["coordinates"][0]]
    if geom["type"] == "MultiPolygon":
        return [poly[0] for poly in geom["coordinates"]]
    return []


CMAP = plt.get_cmap("Blues")
# Paleta sobria para resaltar las marcas con mas sedes (Opcion A).
TOP_BRAND_COLORS = ["#1f3b57", "#c0762b", "#1a9850", "#2c7fb8"]
OTHER_BRAND_COLOR = "#9aa3ad"


def _draw_comuna_polygons(ax, data: dict, counts: dict[int, int] | None) -> float:
    """Dibuja poligonos comunales. Si hay counts colorea coropletico; etiqueta C{n}."""
    max_count = max(counts.values()) if counts else 1
    for feature in data["features"]:
        comuna = int(feature["properties"]["comuna"])
        if counts is not None:
            count = counts.get(comuna, 0)
            color = CMAP(0.18 + 0.72 * (count / max_count)) if count else "#eef1f5"
        else:
            color = "#eef2f7"
        for ring in rings(feature["geometry"]):
            xs = [p[0] for p in ring]
            ys = [p[1] for p in ring]
            ax.fill(xs, ys, facecolor=color, edgecolor="white", lw=1.3, zorder=1)
        coords = [p for ring in rings(feature["geometry"]) for p in ring]
        if coords:
            cx = sum(p[0] for p in coords) / len(coords)
            cy = sum(p[1] for p in coords) / len(coords)
            if counts is not None:
                count = counts.get(comuna, 0)
                if count:
                    tcolor = "white" if count >= max_count * 0.55 else INK
                    ax.text(cx, cy, f"C{comuna}", ha="center", va="bottom", fontsize=8.0,
                            color=tcolor, fontweight="bold", zorder=3)
                    ax.text(cx, cy, f"{count}", ha="center", va="top", fontsize=10.5,
                            color=tcolor, fontweight="bold", zorder=3)
                else:
                    ax.text(cx, cy, f"C{comuna}", ha="center", va="center", fontsize=7.2,
                            color="#9aa3ad", fontweight="bold", zorder=3)
            else:
                ax.text(cx, cy, f"C{comuna}", ha="center", va="center", fontsize=7.6,
                        color="#8a929c", fontweight="bold", zorder=3)
    return max_count


def _scale_legend(fig, ax, max_count: int) -> None:
    """Mini-escala de color (claro=menos, oscuro=mas respuestas)."""
    import matplotlib.colors as mcolors
    cax = fig.add_axes([0.16, 0.085, 0.30, 0.022])
    grad = np.linspace(0, 1, 256).reshape(1, -1)
    cax.imshow(grad, aspect="auto", cmap=mcolors.ListedColormap([CMAP(0.18 + 0.72 * t) for t in np.linspace(0, 1, 256)]))
    cax.set_xticks([0, 255])
    cax.set_xticklabels(["menos", f"más ({max_count})"], fontsize=7.6, color=INK)
    cax.set_yticks([])
    cax.tick_params(length=0)
    for s in cax.spines.values():
        s.set_visible(False)
    cax.text(0, 1.9, "Respuestas por comuna", transform=cax.transAxes, fontsize=8.0, color=INK, fontweight="bold")


def _title_block(ax, title: str, subtitle: str) -> None:
    """Titulo y subtitulo separados, con espacio suficiente para no superponerse."""
    ax.set_title(clean_text(title), loc="left", color=INK, fontsize=14, fontweight="bold", pad=20)
    ax.text(0, 1.045, clean_text(subtitle), transform=ax.transAxes, fontsize=9.0, color=GREY, va="bottom")


def draw_mapa_comunal_publico(ranking_rows: list[dict]) -> bool:
    data = load_geo("geo_comunas.geojson")
    if not data:
        return False
    counts = {int(r["comuna"]): int(r["cantidad_respuestas"]) for r in ranking_rows if str(r["comuna"]).isdigit()}
    fig, ax = plt.subplots(figsize=(9.0, 9.4))
    max_count = _draw_comuna_polygons(ax, data, counts=counts)
    ax.set_aspect("equal")
    ax.axis("off")
    _scale_legend(fig, ax, max_count)
    fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.13)
    GRAF_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(MAPA_COMUNAL, dpi=210, facecolor="white")
    plt.close(fig)
    return True


def _brand_color_map(sedes: list[dict]) -> tuple[dict[str, str], list[tuple[str, int, str]]]:
    """Asigna color a las marcas con mas sedes; resto en gris. Devuelve (mapa, leyenda)."""
    counts = Counter(s["nombre_comercial"] for s in sedes)
    top = counts.most_common(4)
    color_of: dict[str, str] = {}
    legend: list[tuple[str, int, str]] = []
    for i, (brand, n) in enumerate(top):
        color_of[brand] = TOP_BRAND_COLORS[i]
        legend.append((brand, n, TOP_BRAND_COLORS[i]))
    otras = sum(n for b, n in counts.items() if b not in color_of)
    if otras:
        legend.append(("Otras marcas", otras, OTHER_BRAND_COLOR))
    return color_of, legend


def draw_mapa_sedes(sedes: list[dict]) -> bool:
    data = load_geo("geo_comunas.geojson")
    if not data:
        return False
    color_of, legend = _brand_color_map(sedes)
    fig, ax = plt.subplots(figsize=(9.0, 9.4))
    _draw_comuna_polygons(ax, data, counts=None)
    for s in sedes:
        c = color_of.get(s["nombre_comercial"], OTHER_BRAND_COLOR)
        ax.scatter(float(s["longitud"]), float(s["latitud"]), s=78, color=c,
                   edgecolor="white", lw=1.1, zorder=4, alpha=0.95)
    ax.set_aspect("equal")
    ax.axis("off")
    handles = [Line2D([0], [0], marker="o", color="none", markerfacecolor=col,
                      markeredgecolor="white", markersize=11,
                      label=f"{clean_text(b)} ({n})") for b, n, col in legend]
    ax.legend(handles=handles, loc="lower left", frameon=False, fontsize=8.8,
              title="Sedes por marca", title_fontproperties={"weight": "bold", "size": 9.2})
    fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.05)
    GRAF_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(MAPA_SEDES, dpi=210, facecolor="white")
    plt.close(fig)
    return True


def draw_mapa_combinado(sedes: list[dict], ranking_rows: list[dict]) -> bool:
    data = load_geo("geo_comunas.geojson")
    if not data:
        return False
    counts = {int(r["comuna"]): int(r["cantidad_respuestas"]) for r in ranking_rows if str(r["comuna"]).isdigit()}
    fig, ax = plt.subplots(figsize=(9.0, 9.6))
    max_count = _draw_comuna_polygons(ax, data, counts=counts)
    xs = [float(s["longitud"]) for s in sedes]
    ys = [float(s["latitud"]) for s in sedes]
    ax.scatter(xs, ys, s=70, color=COFFEE, edgecolor="white", lw=1.2, zorder=4, alpha=0.96)
    ax.set_aspect("equal")
    ax.axis("off")
    handles = [
        Line2D([0], [0], marker="s", color="none", markerfacecolor=CMAP(0.75), markersize=12, label="Más público (por comuna)"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=COFFEE, markeredgecolor="white", markersize=11, label="Sede de cafetería (red potencial)"),
    ]
    ax.legend(handles=handles, loc="lower left", frameon=False, fontsize=8.8)
    _scale_legend(fig, ax, max_count)
    fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.13)
    GRAF_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(MAPA_COMBINADO, dpi=210, facecolor="white")
    plt.close(fig)
    return True


def draw_plan_barras(stats: dict) -> None:
    items = stats["con_quien"]["items"]
    base_n = stats["con_quien"]["base"]
    chosen = list(reversed(items))
    labels = [clean_text(DISPLAY.get(label, label)) for label, _ in chosen]
    values = [v for _, v in chosen]
    accents = {"En pareja", "Con amigos/as", "Con familia"}
    colors = [ORANGE if label in accents else BLUE for label, _ in chosen]
    fig, ax = plt.subplots(figsize=(8.6, 4.4))
    ax.barh(range(len(values)), values, color=colors, height=0.62)
    ax.set_yticks(range(len(values)))
    ax.set_yticklabels(labels, fontsize=10, color="#222222")
    for side in ("top", "right", "bottom"):
        ax.spines[side].set_visible(False)
    ax.spines["left"].set_color(LINE)
    ax.tick_params(axis="x", length=0, labelbottom=False)
    max_v = max(values)
    for i, v in enumerate(values):
        ax.text(v + max_v * 0.02, i, f"{v} ({pct_s(v, base_n)})", va="center", color=INK, fontsize=9.4, fontweight="bold")
    ax.set_xlim(0, max_v * 1.22)
    ax.set_title("Con quién asistió al evento", loc="left", color=INK, fontsize=14, fontweight="bold", pad=12)
    fig.text(0.02, 0.03, f"Base: n={base_n} respuestas válidas. Modo de asistencia declarado.", color=GREY, fontsize=8.4)
    fig.tight_layout(rect=[0, 0.05, 1, 0.97])
    GRAF_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(PLAN_BARRAS, dpi=190, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# --------------------------------------------------------------------- páginas

NETWORK_NOTE = (
    "El mapa muestra sedes públicas conocidas en CABA de marcas/cafeterías "
    "vinculadas al evento. No implica que todas esas sedes hayan "
    "participado físicamente en la edición relevada; se utiliza como aproximación "
    "a la red territorial potencial de difusión."
)


def cover_page(pdf: PdfPages) -> None:
    fig = page()
    # Bloque institucional superior, sobrio.
    fig.patches.append(Rectangle((0, 0.70), 1, 0.30, transform=fig.transFigure, facecolor=INK, edgecolor="none"))
    fig.patches.append(Rectangle((0, 0.688), 1, 0.012, transform=fig.transFigure, facecolor=ORANGE, edgecolor="none"))
    fig.text(0.065, 0.93, "DataGastro", color=WHITE, fontsize=13, fontweight="bold")
    fig.text(0.935, 0.93, "Informe exploratorio", color="#c9d6e4", fontsize=10, ha="right")
    fig.text(0.065, 0.84, "Cafecito BA\nen tu barrio", color=WHITE, fontsize=34, fontweight="bold", va="top", linespacing=0.95)
    fig.text(0.065, 0.728, "Lectura de público, territorio y red de cafeterías vinculadas",
             color="#dbe5ef", fontsize=12.5, va="center")
    # Franja inferior limpia con una sola advertencia metodológica.
    fig.text(0.065, 0.585, "Una primera lectura del público que respondió el formulario del evento,",
             color=INK, fontsize=12.5, va="center")
    fig.text(0.065, 0.555, "su distribución territorial y la red de cafeterías que puede amplificar la difusión.",
             color=INK, fontsize=12.5, va="center")
    # Una línea de jerarquía con tres ejes (texto, sin cajas KPI cargadas).
    fig.lines.append(Line2D([0.065, 0.55], [0.50, 0.50], color=LINE, lw=1.2, transform=fig.transFigure))
    ejes = [
        ("Público", "Quiénes respondieron y desde dónde."),
        ("Territorio", "Dónde está el público y dónde la red de cafeterías."),
        ("Decisiones", "Difusión, fidelización y próximas ediciones."),
    ]
    y = 0.455
    for titulo, desc in ejes:
        fig.text(0.065, y, titulo, color=ORANGE, fontsize=11, fontweight="bold", va="center")
        fig.text(0.235, y, desc, color="#333333", fontsize=10.5, va="center")
        y -= 0.040
    # Advertencia metodológica sobria, una sola caja.
    add_box(
        fig, 0.065, 0.175, 0.87, 0.085, "Advertencia metodológica",
        "Muestra exploratoria, no representativa del público total del evento. Los datos describen a quienes respondieron el formulario y se publican de forma agregada.",
        face=SOFT_ORANGE, edge=ORANGE, body_size=10.0, title_size=10.5,
    )
    footer(fig)
    pdf.savefig(fig)
    plt.close(fig)


def summary_page(pdf: PdfPages, p: dict, page_no: int) -> None:
    fig = page()
    y = header(fig, page_no, "Resumen ejecutivo",
               "Qué sabemos, qué oportunidad abre y qué decisiones habilita esta lectura.")
    add_kpi_cards(fig, [
        ("79", "respuestas", "base exploratoria"),
        (f"{p['instagram']}/79", "Instagram", "principal canal"),
        (f"{p['contact_yes']}/{p['contact_base']}", "contacto", "acepta novedades"),
        ("39", "sedes mapeables", "red potencial"),
    ], y - 0.105)
    add_box(fig, 0.065, 0.420, 0.42, 0.245, "Qué sabemos", [
        f"Respondió un público joven-adulto ({p['young']}/79 entre 18 y 44) y mayormente de CABA ({p['caba']}/79).",
        f"Instagram es el canal dominante de llegada ({p['instagram']}/79); la recomendación ({p['interpersonal']}/79) y el paso por la zona ({p['paso_zona']}/79) completan el cuadro.",
        f"Conviven recurrentes ({p['recurrent']}/79) y primeras visitas ({p['first_time']}/79).",
    ], face=WHITE, edge=BLUE, bullet=True, body_size=8.9)
    add_box(fig, 0.515, 0.420, 0.42, 0.245, "Qué oportunidad abre", [
        f"Alta aceptación de contacto ({p['contact_yes']}/{p['contact_base']}): base para fidelizar y comunicar.",
        "Una red de 39 sedes conocidas de cafeterías en CABA que hoy no aparece como canal de llegada: red potencial de difusión aún sin activar.",
        "Interés futuro en vino, pastelería, food trucks y café: pistas para programación.",
    ], face=SOFT_BLUE, edge=BLUE, bullet=True, body_size=8.9)
    add_box(fig, 0.065, 0.225, 0.42, 0.170, "Qué decisiones habilita", [
        "Sostener Instagram y sumar difusión física vía locales adheridos.",
        "Diseñar comunicación posterior con quienes aceptaron contacto.",
        "Usar la red de cafeterías para ampliar alcance por comuna.",
    ], face=SOFT_GREEN, edge=GREEN, bullet=True, body_size=8.9)
    add_box(fig, 0.515, 0.225, 0.42, 0.170, "Recomendaciones principales", [
        "Activar cafeterías como puntos de difusión (QR, cartelería, reposts).",
        "Aumentar muestra y registrar el canal de llegada con más detalle.",
        "Programar próximas ediciones según los intereses declarados.",
    ], face=WHITE, edge=ORANGE, bullet=True, body_size=8.9)
    add_box(fig, 0.065, 0.105, 0.87, 0.085, "Cuidado metodológico",
            "Las cifras describen a quienes respondieron, no al público total. No habilitan inferencias estadísticas ni proyecciones al universo de asistentes.",
            face=SOFT_ORANGE, edge=ORANGE, body_size=9.0)
    footer(fig)
    pdf.savefig(fig)
    plt.close(fig)


def decision_page(pdf: PdfPages, page_no: int) -> None:
    fig = page()
    header(fig, page_no, "Qué permite decidir este relevamiento",
           "No solo qué respondió la gente: qué acción de gestión habilita cada bloque.")
    cards = [
        ("Comunicación", "Ajustar canales y piezas según cómo se enteran las personas, sin depender solo de redes."),
        ("Difusión territorial", "Usar la red de cafeterías como puntos físicos de difusión por comuna."),
        ("Fidelización", "Trabajar la aceptación de contacto como puerta de comunicación futura."),
        ("Captación", "Distinguir primeras visitas y público recurrente para crecer sin perder audiencia."),
        ("Programación", "Leer los intereses futuros como primeras hipótesis de agenda."),
        ("Operativo de campo", "Mejorar QR, incentivos, encuestadores y registro del canal de llegada."),
    ]
    x0, y0 = 0.065, 0.660
    for i, (title, body) in enumerate(cards):
        col = i % 2
        row = i // 2
        x = x0 + col * 0.455
        y = y0 - row * 0.150
        add_box(fig, x, y, 0.415, 0.115, title, body, face=WHITE if i % 2 else LIGHT, edge=BLUE if i < 4 else ORANGE)
    add_box(
        fig, 0.065, 0.150, 0.87, 0.140, "Lectura ejecutiva",
        "El valor del relevamiento no es medir al público total, sino orientar decisiones concretas: dónde reforzar la difusión, cómo sostener el vínculo con quienes ya asistieron y qué proponer en las próximas ediciones.",
        face=SOFT_BLUE, edge=INK, body_size=9.4,
    )
    footer(fig)
    pdf.savefig(fig)
    plt.close(fig)


def profile_page(pdf: PdfPages, stats: dict, p: dict, page_no: int) -> None:
    fig = page()
    header(fig, page_no, "Perfil de la muestra",
           "Edad, género y procedencia describen a quienes respondieron, no al público total.")
    hbar(fig, [0.085, 0.500, 0.40, 0.300], stats["rango_edad"]["items"], stats["rango_edad"]["base"],
         "Rango de edad", accents={"18 a 24", "25 a 34", "35 a 44"})
    stacked(fig, [0.560, 0.745, 0.360, 0.072], stats["genero"]["items"], stats["genero"]["base"],
            "Género declarado", [INK, ORANGE, GREY])
    caba = p["caba"]
    no_caba = p["n"] - caba
    fig.text(0.575, 0.655, "Procedencia (nivel macro)", color=INK, fontsize=10.5, fontweight="bold", va="top")
    donut(fig, [0.575, 0.480, 0.320, 0.165], [("CABA", caba), ("No CABA", no_caba)],
          "", f"{pct_s(caba, p['n'])}\nCABA", [BLUE, "#e6b17e"])
    add_box(fig, 0.065, 0.255, 0.42, 0.180, "Lectura ejecutiva",
            f"El bloque 18 a 44 suma {p['young']}/79 respuestas, con pico en 25 a 34. La muestra captada es joven-adulta, mayoritariamente femenina ({p['mujer']}/79) y de CABA ({p['caba']}/79).",
            face=SOFT_BLUE, edge=BLUE, body_size=9.2)
    gen = items_dict(stats, "genero")
    nb = gen.get("No binario", 0)
    add_box(fig, 0.515, 0.255, 0.42, 0.180, "Cuidado metodológico",
            f"La procedencia se publica a nivel macro (CABA / no CABA) y agregada por comuna. El barrio/localidad libre queda fuera por privacidad. Género: incluye categoría minoritaria (No binario: {nb}). Porcentajes redondeados.",
            face=SOFT_ORANGE, edge=ORANGE, body_size=9.2)
    add_box(fig, 0.065, 0.105, 0.87, 0.115, "Qué decisión habilita",
            "Ajustar el tono y los canales de comunicación al perfil que efectivamente responde, sin sobregeneralizar al total de asistentes.",
            face=SOFT_GREEN, edge=GREEN, body_size=9.2)
    footer(fig)
    pdf.savefig(fig)
    plt.close(fig)


def public_territory_page(pdf: PdfPages, ranking_rows: list[dict], page_no: int) -> None:
    fig = page()
    header(fig, page_no, "Lectura territorial del público",
           "Distribución agregada por comuna de quienes respondieron.")
    # Mapa como pieza central, usando casi todo el ancho de la pagina.
    add_image(fig, MAPA_COMUNAL, [0.065, 0.375, 0.87, 0.475])
    numeric = [r for r in ranking_rows if str(r["comuna"]).isdigit()][:5]
    top_txt = ", ".join(f"Comuna {r['comuna']} ({r['cantidad_respuestas']})" for r in numeric)
    add_box(fig, 0.065, 0.235, 0.42, 0.115, "Cómo leer el mapa",
            f"Las respuestas con comuna identificable se concentran en {top_txt}. El resto se agrupa para no exponer celdas chicas.",
            face=SOFT_BLUE, edge=BLUE, body_size=8.4)
    add_box(fig, 0.515, 0.235, 0.42, 0.115, "Cuidado metodológico",
            "El peso de Comuna 13 puede reflejar cercanía a Belgrano y al punto/horario de captación. Es señal territorial de la muestra, no un mapa de asistencia.",
            face=SOFT_ORANGE, edge=ORANGE, body_size=8.4)
    add_box(fig, 0.065, 0.105, 0.87, 0.100, "Lectura ejecutiva",
            "El público que respondió se concentra en pocas comunas cercanas al evento. Eso orienta dónde reforzar la difusión local y dónde hay margen para ampliar el alcance en próximas ediciones.",
            face=SOFT_GREEN, edge=GREEN, body_size=9.0)
    footer(fig)
    pdf.savefig(fig)
    plt.close(fig)


def network_page(pdf: PdfPages, sedes_comuna: list[dict], page_no: int) -> None:
    fig = page()
    header(fig, page_no, "Red territorial de cafeterías vinculadas",
           "Sedes públicas conocidas en CABA como red potencial de difusión.")
    add_image(fig, MAPA_SEDES, [0.065, 0.395, 0.87, 0.455])
    add_box(fig, 0.065, 0.230, 0.255, 0.125, "La red en números", [
        "14 marcas analizadas.",
        "39 sedes mapeables en CABA.",
        "2 marcas pendientes de validación.",
    ], face=WHITE, edge=BLUE, bullet=True, body_size=8.1)
    top = [r for r in sedes_comuna if str(r["comuna"]).isdigit()][:6]
    top_txt = ", ".join(f"Comuna {r['comuna']} ({r['cantidad_sedes']})" for r in top)
    add_box(fig, 0.345, 0.230, 0.590, 0.125, "Comunas con más sedes",
            f"{top_txt}. Palermo, Belgrano y el corredor central concentran la mayor densidad.",
            face=SOFT_BLUE, edge=BLUE, body_size=8.4)
    add_box(fig, 0.065, 0.105, 0.87, 0.095, "Cómo leer esta red", NETWORK_NOTE,
            face=SOFT_ORANGE, edge=ORANGE, body_size=8.8)
    footer(fig)
    pdf.savefig(fig)
    plt.close(fig)


def public_vs_network_page(pdf: PdfPages, page_no: int) -> None:
    fig = page()
    header(fig, page_no, "Público y red de difusión",
           "Dónde coincide el público que respondió con la red de cafeterías.")
    add_image(fig, MAPA_COMBINADO, [0.065, 0.395, 0.87, 0.455])
    add_box(fig, 0.065, 0.230, 0.42, 0.125, "Coincidencias", [
        "Comuna 13 (Belgrano) aparece fuerte en respuestas y también con sedes.",
        "Palermo (Comuna 14) concentra muchas sedes, con menor peso del público.",
    ], face=SOFT_BLUE, edge=BLUE, bullet=True, body_size=8.3)
    add_box(fig, 0.515, 0.230, 0.42, 0.125, "Oportunidad", [
        "La red cubre comunas con poco público registrado.",
        "Son zonas para ampliar la difusión física en próximas ediciones.",
    ], face=SOFT_GREEN, edge=GREEN, bullet=True, body_size=8.3)
    add_box(fig, 0.065, 0.105, 0.87, 0.095, "Cuidado metodológico",
            "El peso de Comuna 13 / Belgrano debe leerse con cautela por la cercanía al evento y el punto de captación. No se afirma causalidad entre la ubicación de las sedes y el origen del público.",
            face=SOFT_ORANGE, edge=ORANGE, body_size=8.8)
    footer(fig)
    pdf.savefig(fig)
    plt.close(fig)


def channels_page(pdf: PdfPages, stats: dict, p: dict, page_no: int) -> None:
    fig = page()
    header(fig, page_no, "Canales de llegada y locales adheridos",
           "Cómo se enteró el público y por qué los locales físicos son una oportunidad.")
    hbar(fig, [0.080, 0.470, 0.50, 0.350], stats["como_se_entero"]["items"], stats["como_se_entero"]["base"],
         "Cómo se enteraron del evento", color=BLUE,
         accents={"Instagram", "Por amigos, familia o conocidos", "Pase por la zona y lo ví"}, multi=True)
    add_box(fig, 0.620, 0.660, 0.315, 0.160, "Lectura ejecutiva",
            f"Instagram lidera ({p['instagram']}/79). La recomendación ({p['interpersonal']}/79) y el paso por la zona ({p['paso_zona']}/79) completan la llegada. Casi nadie declaró haberse enterado por una cafetería o local adherido.",
            face=SOFT_BLUE, edge=BLUE, body_size=8.8)
    add_box(fig, 0.620, 0.470, 0.315, 0.170, "Oportunidad de mejora",
            "Ese vacío revela un canal sin explotar: los locales adheridos pueden anticipar y reforzar la difusión, sobre todo para público menos digitalizado o que no vive cerca del evento.",
            face=SOFT_GREEN, edge=GREEN, body_size=8.8)
    add_box(fig, 0.065, 0.230, 0.87, 0.190, "Qué pedir a los locales adheridos", [
        "Publicar historias y repostear las piezas oficiales del evento.",
        "Colocar un QR del evento o del formulario en el mostrador.",
        "Sumar folletería y cartelería física en el local.",
        "Diseñar piezas específicas por barrio o comuna.",
        "El local físico puede ser un canal clave para enterarse antes de la fecha, no solo por pasar casualmente por la zona.",
    ], face=WHITE, edge=ORANGE, bullet=True, body_size=8.8)
    add_box(fig, 0.065, 0.105, 0.87, 0.095, "Para próximas ediciones",
            "Registrar cómo se enteró cada persona con más detalle: Instagram oficial, Instagram de una cafetería, local físico adherido, recomendación, paso por la zona u otro canal.",
            face=SOFT_ORANGE, edge=ORANGE, body_size=9.0)
    footer(fig)
    pdf.savefig(fig)
    plt.close(fig)


def loyalty_page(pdf: PdfPages, stats: dict, p: dict, records: list[dict], page_no: int) -> None:
    fig = page()
    header(fig, page_no, "Vínculo con eventos de la Ciudad y fidelización",
           "Captación nueva, público recurrente y aceptación de contacto.")
    stacked(fig, [0.085, 0.700, 0.420, 0.110], stats["primera_vez"]["items"], stats["primera_vez"]["base"],
            "Primera vez vs. recurrentes", [INK, ORANGE, GREY])
    donut(fig, [0.600, 0.610, 0.250, 0.210], stats["acepta_contacto"]["items"], "Acepta recibir novedades",
          f"{pct_s(p['contact_yes'], p['contact_base'])}", [GREEN, GREY])
    table = crosstab(records, "primera_vez", "acepta_contacto")
    rows = []
    label_disp = {
        "No, ya participé de otros eventos": "Recurrentes",
        "Si, es la primera vez": "Primera vez",
        "No estoy seguro/a": "No está seguro/a",
    }
    total_acepta = total_base = 0
    for label, disp in label_disp.items():
        row = table.get(label, Counter())
        if row:
            acepta = row.get("Si, acepto", 0)
            base_n = sum(row.values())
            total_acepta += acepta
            total_base += base_n
            rows.append((disp, str(acepta), str(base_n)))
    rows.append(("Total", str(total_acepta), str(total_base)))
    mini_table(fig, 0.090, 0.405, 0.760, 0.120, rows, "Aceptan contacto / total, por vínculo previo")
    add_box(fig, 0.065, 0.235, 0.42, 0.150, "Lectura ejecutiva",
            f"El evento combina fidelización ({p['recurrent']}/79 ya participaron de otros eventos) y captación ({p['first_time']}/79 primeras visitas), con alta aceptación de contacto ({p['contact_yes']}/{p['contact_base']}).",
            face=SOFT_BLUE, edge=BLUE, body_size=9.2)
    add_box(fig, 0.515, 0.235, 0.42, 0.150, "Qué decisión habilita",
            "Diseñar comunicación posterior diferenciada: continuidad para recurrentes y bienvenida/retención para primeras visitas, siempre sin publicar datos personales.",
            face=SOFT_GREEN, edge=GREEN, body_size=9.2)
    add_box(fig, 0.065, 0.110, 0.87, 0.100, "Cuidado metodológico",
            "La aceptación de contacto se mide sobre respuestas válidas. Los correos no se publican ni se usan en ningún resultado público.",
            face=SOFT_ORANGE, edge=ORANGE, body_size=9.0)
    footer(fig)
    pdf.savefig(fig)
    plt.close(fig)


def motivations_page(pdf: PdfPages, stats: dict, p: dict, page_no: int) -> None:
    fig = page()
    header(fig, page_no, "Motivaciones e intereses futuros",
           "Qué atrajo del evento y qué programación habilita a futuro.")
    hbar(fig, [0.085, 0.560, 0.40, 0.250], stats["que_intereso"]["items"], stats["que_intereso"]["base"],
         "Qué atrajo de esta edición", color=COFFEE,
         accents={"Probar café / cafeterías", "Pasear o hacer una salida"})
    hbar(fig, [0.560, 0.470, 0.375, 0.340], stats["eventos_futuros"]["items"], stats["eventos_futuros"]["base"],
         "Intereses futuros", color=BLUE,
         accents={"Vino", "Pasteleria", "Food trucks", "Café", "Ferias y mercados"}, limit=8, multi=True)
    add_box(fig, 0.065, 0.295, 0.42, 0.140, "Qué atrajo de esta edición",
            f"Probar café/cafeterías ({p['coffee']}/79) lidera, seguido por pasear o hacer una salida ({p['paseo']}/79) y conocer propuestas nuevas ({p['nuevas']}/79). El atractivo combina producto y experiencia urbana.",
            face=SOFT_BLUE, edge=BLUE, body_size=9.0)
    add_box(fig, 0.515, 0.295, 0.42, 0.140, "Programación futura",
            f"Como agenda de hipótesis: vino ({p['vino']}), pastelería ({p['pasteleria']}), food trucks ({p['food_trucks']}), café ({p['cafe_futuro']}) y ferias/mercados ({p['ferias']}), más otras señales menores.",
            face=SOFT_GREEN, edge=GREEN, body_size=9.0)
    add_box(fig, 0.065, 0.110, 0.87, 0.155, "Cuidado metodológico", [
        "“Qué interesó del evento” captura un atractivo principal por persona.",
        "“Intereses futuros” es una pregunta multi-respuesta: las cifras son menciones sobre 79 respondentes y una persona pudo elegir más de una opción; no representan personas ni demanda cerrada.",
    ], face=SOFT_ORANGE, edge=ORANGE, bullet=True, body_size=9.0)
    footer(fig)
    pdf.savefig(fig)
    plt.close(fig)


def conclusions_page(pdf: PdfPages, p: dict, page_no: int) -> None:
    fig = page()
    header(fig, page_no, "Conclusiones y recomendaciones",
           "Síntesis ejecutiva para orientar las próximas ediciones.")
    fig.text(0.065, 0.805, "Lo que muestra el relevamiento", color=INK, fontsize=11.5, fontweight="bold", va="top")
    cierre = [
        f"Cafecito captó principalmente público joven-adulto de CABA, con alta presencia femenina, que combina recurrentes ({p['recurrent']}/79) y primeras visitas ({p['first_time']}/79).",
        f"Instagram concentra la llegada ({p['instagram']}/79), pero la recomendación y el paso por la zona también importan; los locales adheridos casi no aparecen como canal.",
        f"La aceptación de contacto ({p['contact_yes']}/{p['contact_base']}) abre una base concreta para fidelizar y comunicar a futuro.",
        "La red de 39 sedes conocidas de cafeterías vinculadas ofrece una infraestructura territorial de difusión potencial todavía sin activar, que cubre comunas más allá del entorno inmediato del evento.",
    ]
    yy = 0.778
    for t in cierre:
        for line in wrap_text("• " + t, 108):
            fig.text(0.065, yy, line, color="#222222", fontsize=9.6, va="top")
            yy -= 0.0185
        yy -= 0.007
    add_box(fig, 0.065, 0.395, 0.42, 0.120, "Decisión habilitada",
            "Convertir la red de cafeterías en canal de difusión y construir comunicación con quienes aceptaron contacto.",
            face=SOFT_GREEN, edge=GREEN, body_size=9.2)
    add_box(fig, 0.515, 0.395, 0.42, 0.120, "Recomendación principal",
            "Activar locales adheridos con QR, cartelería y reposts, y registrar mejor el canal de llegada en próximas ediciones.",
            face=WHITE, edge=ORANGE, body_size=9.2)
    add_box(fig, 0.065, 0.250, 0.42, 0.120, "Lectura ejecutiva",
            "El relevamiento no mide al público total, pero da señales accionables sobre perfil, canales, potencial de contacto y red de difusión.",
            face=SOFT_BLUE, edge=BLUE, body_size=9.2)
    add_box(fig, 0.515, 0.250, 0.42, 0.120, "Cuidado metodológico",
            "Toda la lectura es exploratoria. No se proyecta al universo de asistentes ni se afirma representatividad.",
            face=SOFT_ORANGE, edge=ORANGE, body_size=9.2)
    add_box(fig, 0.065, 0.105, 0.87, 0.115, "Recomendaciones para próximas ediciones", [
        "Aumentar la muestra con puntos y horarios de captación definidos y equipo encuestador.",
        "Activar la red de cafeterías como canal físico y digital de difusión por comuna.",
        "Programar según los intereses declarados y sostener Instagram sin depender solo de redes.",
    ], face=LIGHT, edge=INK, bullet=True, body_size=8.8)
    footer(fig)
    pdf.savefig(fig)
    plt.close(fig)


def annex_page(pdf: PdfPages, page_no: int) -> None:
    fig = page()
    header(fig, page_no, "Anexo metodológico y privacidad",
           "Base, tratamiento de datos y criterios de la red territorial.")
    add_box(fig, 0.065, 0.610, 0.42, 0.205, "Base y alcance", [
        "Formulario del evento Cafecito BA en tu barrio.",
        "79 respuestas analizadas.",
        "Muestra exploratoria, no representativa del público total.",
        "Los porcentajes se calculan sobre respuestas válidas por pregunta.",
    ], face=WHITE, edge=BLUE, bullet=True, body_size=8.6)
    add_box(fig, 0.515, 0.610, 0.42, 0.205, "Privacidad", [
        "No se publican correos, nombres, teléfonos ni marcas temporales.",
        "No se listan barrios/localidades individuales.",
        "No se publican respuestas individuales: solo agregados.",
        "El público se muestra agregado por comuna o agregación segura.",
    ], face=SOFT_ORANGE, edge=ORANGE, bullet=True, body_size=8.6)
    add_box(fig, 0.065, 0.380, 0.42, 0.205, "Preguntas multi-respuesta", [
        "Canales de llegada e intereses futuros se leen por menciones.",
        "Los porcentajes pueden sumar más de 100%.",
        "La categoría “Por amigos, familia o conocidos” se conserva unificada.",
    ], face=LIGHT, edge=INK, bullet=True, body_size=8.6)
    add_box(fig, 0.515, 0.380, 0.42, 0.205, "Red de cafeterías", [
        "Sedes públicas conocidas en CABA de marcas/cafeterías vinculadas al evento.",
        "Solo se mapean sedes con validación suficiente para el mapa.",
        "No implica participación física de cada sede: es red potencial de difusión.",
        "Las marcas sin sede validada quedan pendientes y fuera del mapa.",
    ], face=LIGHT, edge=INK, bullet=True, body_size=8.6)
    add_box(fig, 0.065, 0.190, 0.87, 0.155, "Cómo leer la red territorial", NETWORK_NOTE,
            face=SOFT_BLUE, edge=BLUE, body_size=9.2)
    footer(fig)
    pdf.savefig(fig)
    plt.close(fig)


# ----------------------------------------------------------------------- build

def write_pdf(records: list[dict], stats: dict, ranking_rows: list[dict], sedes_comuna: list[dict]) -> int:
    p = stats_payload(records, stats)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    with PdfPages(PDF_FINAL) as pdf:
        cover_page(pdf)
        summary_page(pdf, p, 2)
        decision_page(pdf, 3)
        profile_page(pdf, stats, p, 4)
        public_territory_page(pdf, ranking_rows, 5)
        network_page(pdf, sedes_comuna, 6)
        public_vs_network_page(pdf, 7)
        channels_page(pdf, stats, p, 8)
        loyalty_page(pdf, stats, p, records, 9)
        motivations_page(pdf, stats, p, 10)
        conclusions_page(pdf, p, 11)
        annex_page(pdf, 12)
    shutil.copy2(PDF_FINAL, FINAL_PDF)
    return 12


def write_markdown_report(records: list[dict], stats: dict, ranking_rows: list[dict], sedes_comuna: list[dict]) -> None:
    p = stats_payload(records, stats)
    top_ranking = ", ".join(
        f"Comuna {r['comuna']} ({r['cantidad_respuestas']})"
        for r in ranking_rows if str(r["comuna"]).isdigit()
    )
    top_sedes = ", ".join(
        f"Comuna {r['comuna']} ({r['cantidad_sedes']})"
        for r in sedes_comuna if str(r["comuna"]).isdigit()
    )
    lines = [
        "# DataGastro - Cafecito BA en tu barrio",
        "",
        "## Informe exploratorio de respuestas del formulario",
        "",
        "**Nota metodológica:** muestra exploratoria, no representativa del público total del evento. No se publican correos, marcas temporales, barrios/localidades libres, teléfonos ni identificadores personales. El público se presenta agregado por comuna o agregación segura.",
        "",
        "## 1. Resumen ejecutivo",
        "",
        f"El relevamiento analiza **{p['n']} respuestas**. Permite leer qué sabemos del público que respondió, qué oportunidad abre y qué decisiones habilita para comunicación, difusión territorial, fidelización y programación.",
        "",
        f"- Público joven-adulto: 18 a 44 suma **{p['young']}/79** respuestas, mayormente de CABA (**{p['caba']}/79**).",
        f"- Instagram es el canal principal (**{p['instagram']}/79**); la recomendación (**{p['interpersonal']}/79**) y el paso por la zona (**{p['paso_zona']}/79**) completan la llegada.",
        f"- Conviven recurrentes (**{p['recurrent']}/79**) y primeras visitas (**{p['first_time']}/79**); la aceptación de contacto (**{p['contact_yes']}/{p['contact_base']}**) abre la fidelización.",
        "- La red de **39 sedes mapeables** de cafeterías vinculadas ofrece una red potencial de difusión territorial todavía sin activar.",
        "",
        "## 2. Qué permite decidir este relevamiento",
        "",
        "- **Comunicación:** sostener Instagram y reforzar difusión física/interpersonal.",
        "- **Difusión territorial:** usar la red de cafeterías como puntos físicos de difusión por comuna.",
        "- **Fidelización:** trabajar la aceptación de contacto sin publicar datos personales.",
        "- **Captación:** distinguir primera visita y recurrencia.",
        "- **Programación:** leer intereses futuros como hipótesis de agenda.",
        "- **Operativo:** mejorar QR, incentivos, encuestadores y registro del canal de llegada.",
        "",
        "## 3. Perfil de la muestra",
        "",
        f"El bloque 18 a 44 suma {p['young']}/79 respuestas; mujeres, {p['mujer']}/79; CABA, {p['caba']}/79. Son datos de quienes respondieron, no del total de asistentes.",
        "",
        "## 4. Lectura territorial del público",
        "",
        f"Ranking comunal agregado: {top_ranking}. Las comunas por debajo del umbral mínimo se agrupan. Si Comuna 13 aparece fuerte, se interpreta con cautela por la cercanía a Belgrano y al punto de captación.",
        "",
        "## 5. Red territorial de cafeterías vinculadas",
        "",
        "El mapa muestra sedes públicas conocidas en CABA de marcas/cafeterías vinculadas al evento. No implica que todas esas sedes hayan participado físicamente en la edición relevada; se utiliza como aproximación a la red territorial potencial de difusión.",
        "",
        f"Se analizaron 14 marcas; 39 sedes resultaron mapeables y 2 marcas quedaron pendientes de validación. Comunas con más sedes: {top_sedes}. Palermo, Belgrano y el corredor central concentran la mayor densidad.",
        "",
        "## 6. Público y red de difusión",
        "",
        "Comuna 13 / Belgrano aparece fuerte tanto en respuestas como en sedes, lo que debe leerse con cautela por cercanía y sesgo de captación. La red de cafeterías cubre además comunas con poco público registrado: una oportunidad para ampliar la difusión. No se afirma causalidad entre la ubicación de las sedes y el origen del público.",
        "",
        "## 7. Canales de llegada y locales adheridos",
        "",
        f"Instagram lidera ({p['instagram']}/79). La recomendación interpersonal ({p['interpersonal']}/79) y el paso por la zona ({p['paso_zona']}/79) completan la lectura. Casi nadie declaró haberse enterado por una cafetería o local adherido, lo que revela una oportunidad de mejora: pedir reposts e historias, colocar QR en mostrador, sumar folletería/cartelería y diseñar piezas por barrio/comuna. Para público menos digitalizado o que no vive cerca, el local físico puede ser un canal clave para enterarse antes de la fecha.",
        "",
        "## 8. Vínculo con eventos de la Ciudad y fidelización",
        "",
        f"Ya habían participado en eventos gastronómicos de la Ciudad {p['recurrent']}/79 personas; {p['first_time']}/79 eran primera visita. Aceptan recibir novedades {p['contact_yes']}/{p['contact_base']} respuestas válidas.",
        "",
        "## 9. Motivaciones e intereses futuros",
        "",
        f"El principal atractivo fue probar café/cafeterías ({p['coffee']}/79), seguido por pasear o hacer una salida ({p['paseo']}/79). Intereses futuros (menciones sobre 79 respondentes; una persona podía elegir más de una opción): vino ({p['vino']}), pastelería ({p['pasteleria']}), food trucks ({p['food_trucks']}), café ({p['cafe_futuro']}) y ferias/mercados ({p['ferias']}).",
        "",
        "## 10. Conclusiones y recomendaciones",
        "",
        "- Convertir la red de cafeterías en canal físico y digital de difusión por comuna.",
        "- Construir comunicación posterior con quienes aceptaron contacto.",
        "- Aumentar la muestra y registrar mejor el canal de llegada en próximas ediciones.",
        "- Programar según los intereses declarados, sosteniendo Instagram sin depender solo de redes.",
        "",
        "## 11. Anexo metodológico y privacidad",
        "",
        "- Base: 79 respuestas del formulario del evento; lectura en modo solo lectura del archivo original.",
        "- Tratamiento multi-respuesta: porcentajes por menciones, no excluyentes.",
        "- Categoría protegida: `Por amigos, familia o conocidos` se conserva unificada.",
        "- Tratamiento territorial: publicación macro y comunal agregada; sin barrios/localidades libres.",
        "- Red de cafeterías: sedes públicas conocidas en CABA, mapeadas solo con validación suficiente; no implica participación física de cada sede.",
        "",
    ]
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def update_readme() -> None:
    text = README_MD.read_text(encoding="utf-8") if README_MD.exists() else "# Cafecito\n"
    block_final = """## Version DataGastro FINAL

Para regenerar la version final institucional:

```powershell
python scripts/cafecito/generar_informe_datagastro_final.py
```

Salidas FINAL:

- PDF institucional FINAL: `outputs/cafecito/INFORME_CAFECITO_DATAGASTRO_FINAL.pdf`
- Copia final FINAL: `Cafesito/final/INFORME_CAFECITO_DATAGASTRO_FINAL.pdf`
- Script generador: `scripts/cafecito/generar_informe_datagastro_final.py`

Insumos territoriales y de red de cafeterias:

- `outputs/cafecito/ranking_comunal_cafecito.csv`
- `outputs/cafecito/cafeterias_sedes_caba_geocodificadas.csv`
- `outputs/cafecito/resumen_sedes_cafeterias_por_comuna.csv`
- `outputs/cafecito/resumen_sedes_cafeterias_por_barrio.csv`

Mapas generados por la version FINAL:

- `outputs/cafecito/graficos_datagastro/mapa_comunal_publico_final.png`
- `outputs/cafecito/graficos_datagastro/mapa_sedes_cafeterias_final.png`
- `outputs/cafecito/graficos_datagastro/mapa_cafeterias_y_publico_final.png`

Cambios respecto de V6_1:

- Mantiene marca DataGastro, numeracion `Pág. X` y terminologia prudente.
- Remaqueta paginas 5, 6 y 7 para que los mapas ocupen el ancho superior y las cajas de lectura queden abajo.
- Conserva 12 paginas y no modifica datos fuente ni narrativa general.
"""
    pattern_final = r"(?ms)^## Version DataGastro FINAL\n.*?(?=^## |\Z)"
    if re.search(pattern_final, text):
        text = re.sub(pattern_final, block_final.rstrip() + "\n\n", text)
    else:
        text = text.rstrip() + "\n\n" + block_final
    README_MD.write_text(text.rstrip() + "\n", encoding="utf-8")


def ensure_analysis_outputs() -> None:
    # Solo se necesita el ranking comunal agregado del publico; los mapas de la
    # V4 se generan en este mismo script.
    if not RANKING_COMUNAL.exists():
        mejora.main()


def main() -> None:
    ensure_analysis_outputs()
    records = base.read_xlsx(base.XLSX)
    stats = build_stats(records)
    ranking_rows = read_csv(RANKING_COMUNAL)
    sedes_comuna = read_csv(RESUMEN_SEDES_COMUNA)

    sedes_all = read_csv(SEDES_CSV)
    sedes_mapa = [s for s in sedes_all if s.get("usar_en_mapa", "").strip() == "si"]

    draw_mapa_comunal_publico(ranking_rows)
    draw_plan_barras(stats)
    map_sedes = draw_mapa_sedes(sedes_mapa)
    map_combo = draw_mapa_combinado(sedes_mapa, ranking_rows)

    pages = write_pdf(records, stats, ranking_rows, sedes_comuna)
    write_markdown_report(records, stats, ranking_rows, sedes_comuna)
    update_readme()

    print("=" * 72)
    print("Informe Cafecito DataGastro FINAL")
    print(f"  Respuestas: {len(records)}")
    print(f"  Sedes mapeadas (usar_en_mapa=si): {len(sedes_mapa)}")
    print(f"  Mapa sedes generado: {map_sedes} · Mapa combinado: {map_combo}")
    print(f"  Paginas PDF: {pages}")
    print(f"  PDF: {PDF_FINAL}")
    print(f"  Copia final: {FINAL_PDF}")
    print("=" * 72)


if __name__ == "__main__":
    main()
