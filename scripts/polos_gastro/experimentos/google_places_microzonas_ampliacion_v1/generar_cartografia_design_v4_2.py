"""Cartografia design v4.2 sobre capas de dibujo v4.1.

Solo presentacion visual: no modifica datos fuente, no reasigna puntos, no llama APIs.
Lee capas de dibujo v4.1 y puntos v4 en modo lectura (hash-check antes y despues).

Fases:
    python generar_cartografia_design_v4_2.py            -> genera mapas + QA + metadata
    python generar_cartografia_design_v4_2.py --package  -> arma paquete de revision + ZIP
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path
from textwrap import wrap

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import pandas as pd
from matplotlib.colors import to_rgba
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch, Patch, Rectangle
from PIL import Image
from shapely.geometry import MultiPolygon
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "outputs" / "polos_gastro" / "historico" / "experimentos" / "google_places_microzonas_ampliacion_v1"
V4 = BASE / "cartografia_redibujo_editorial_v4"
V41 = BASE / "cartografia_redibujo_editorial_v4_1"
OUT = BASE / "cartografia_design_v4_2"
REVIEW = BASE / "REVISION_DESIGN_PRE_FASE26_V4_2"
ZIP_PATH = BASE / "REVISION_DESIGN_PRE_FASE26_V4_2.zip"

INPUTS = {
    V41 / "poligonos_v4_1_mapa_principal_dibujo.geojson": "capa dibujo principal",
    V41 / "poligonos_v4_1_decision_dibujo.geojson": "capa dibujo decision",
    V41 / "poligonos_v4_original_referencia_sin_cambios.geojson": "referencia v4",
    V41 / "solapes_topologia_v4_1.geojson": "solapes QA",
    V41 / "tabla_redibujo_editorial_v4_1.csv": "tabla v4.1",
    V41 / "qa_topologia_v4_1.json": "resumen QA topologico",
    V4 / "puntos_evidencia_v4.geojson": "puntos evidencia v4",
}

# --- sistema visual v4.2 (ver GUIA_VISUAL_CARTOGRAFIA_V4_2.md) ---
INK = "#1F3B57"
TEXT2 = "#46545C"
MUTED = "#5E6B78"
HAIR = "#D3DAE0"
PANEL_BG = "#F0F4F6"
CANVAS = "#FAFBFC"
EXTERIOR = "#ECF0F3"
LAND = "#FFFFFF"
BARRIO = "#D8DFE4"
COMUNA = "#B9C4CC"
LIMITE = "#93A3AE"
POINTS = "#36454F"
OVERLAP = "#D7263D"

ESTADO_FILL = {
    "CANDIDATA_FUERTE": "#1E8A63",
    "CANDIDATA_CON_OBSERVACIONES": "#2C7FB8",
    "REQUIERE_REVISION_HUMANA": "#C0762B",
    "EXPLORATORIA": "#8A62A8",
}
ESTADO_EDGE = {
    "CANDIDATA_FUERTE": "#155F45",
    "CANDIDATA_CON_OBSERVACIONES": "#1D5880",
    "REQUIERE_REVISION_HUMANA": "#8A5520",
    "EXPLORATORIA": "#63447D",
}
ESTADO_ALPHA = {
    "CANDIDATA_FUERTE": 0.50,
    "CANDIDATA_CON_OBSERVACIONES": 0.45,
    "REQUIERE_REVISION_HUMANA": 0.38,
    "EXPLORATORIA": 0.35,
}
ESTADO_LS = {
    "CANDIDATA_FUERTE": "solid",
    "CANDIDATA_CON_OBSERVACIONES": "solid",
    "REQUIERE_REVISION_HUMANA": (0, (5, 3)),
    "EXPLORATORIA": (0, (1.8, 2.2)),
}
ESTADO_NOMBRE = {
    "CANDIDATA_FUERTE": "Candidata fuerte",
    "CANDIDATA_CON_OBSERVACIONES": "Candidata con observaciones",
    "REQUIERE_REVISION_HUMANA": "Requiere revision",
    "EXPLORATORIA": "Exploratoria",
}
FAMILIA_FILL = {
    "MAPA_PRINCIPAL": "#1E8A63",
    "REQUIERE_REVISION": "#C0762B",
    "ANEXO_EXPLORATORIO": "#8A62A8",
}
FAMILIA_EDGE = {
    "MAPA_PRINCIPAL": "#155F45",
    "REQUIERE_REVISION": "#8A5520",
    "ANEXO_EXPLORATORIO": "#63447D",
}
FAMILIA_ALPHA = {
    "MAPA_PRINCIPAL": 0.48,
    "REQUIERE_REVISION": 0.38,
    "ANEXO_EXPLORATORIO": 0.35,
}
FAMILIA_LS = {
    "MAPA_PRINCIPAL": "solid",
    "REQUIERE_REVISION": (0, (5, 3)),
    "ANEXO_EXPLORATORIO": (0, (1.8, 2.2)),
}
FAMILIA_NOMBRE = {
    "MAPA_PRINCIPAL": "Mapa principal",
    "REQUIERE_REVISION": "Requiere revision",
    "ANEXO_EXPLORATORIO": "Anexo exploratorio",
}
STATUS_ORDER = {
    "CANDIDATA_FUERTE": 1,
    "CANDIDATA_CON_OBSERVACIONES": 2,
    "REQUIERE_REVISION_HUMANA": 3,
    "EXPLORATORIA": 4,
}
FAMILY_ORDER = {"MAPA_PRINCIPAL": 1, "REQUIERE_REVISION": 2, "ANEXO_EXPLORATORIO": 3}

KICKER = "DGDGAS - DIRECCION GENERAL DE DESARROLLO GASTRONOMICO"
FOOT_LEFT = "EXPERIMENTAL / NO OFICIAL - mapa de trabajo, no delimitacion institucional final"
FOOT_RIGHT = "Capas de dibujo v4.1 · puntos de evidencia v4 (6.461) · elaboracion DGDGAS"

plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Segoe UI", "Arial", "DejaVu Sans"],
        "svg.fonttype": "none",
    }
)

SHORT_NAMES = {
    "Palermo Hollywood / Fitz Roy": "Hollywood / Fitz Roy",
    "Palermo Soho / Plaza Serrano": "Soho / Plaza Serrano",
    "Recoleta oeste / Santa Fe-Alto Palermo": "Santa Fe / Alto Palermo",
    "Villa Crespo / Corrientes-limite Palermo": "V. Crespo / Corrientes",
    "Puerto Madero centro / diques": "P. Madero centro / diques",
    "Corrientes oeste / Abasto-Once": "Abasto / Once",
    "Corrientes centro / eje teatral-gastronomico": "Corrientes centro / teatral",
    "Corrientes centro teatral": "Corrientes teatral",
    "Chacarita central / Federico Lacroze": "Chacarita / Lacroze",
    "Avellaneda / zona comercial": "Avellaneda comercial",
    "Florida-Lavalle / Microcentro": "Florida-Lavalle",
    "Microcentro laboral / administrativo": "Microcentro laboral",
    "Costanera Norte / senal exploratoria": "Costanera Norte",
    "Costanera Norte / señal exploratoria": "Costanera Norte",
    "Av. Caseros / Barracas exploratoria": "Caseros / Barracas",
    "Puerto Madero / piezas exploratorias": "P. Madero exploratorio",
    "Caballito / senal exploratoria": "Caballito exploratorio",
    "Caballito / señal exploratoria": "Caballito exploratorio",
    "Libertador / Barrancas-Belgrano norte": "Libertador / Barrancas",
}


def short_name(value: str) -> str:
    return SHORT_NAMES.get(value, value)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def hash_inputs() -> dict[str, str]:
    missing = [str(p) for p in INPUTS if not p.exists()]
    if missing:
        raise FileNotFoundError(f"Faltan insumos: {missing}")
    return {p.name: sha256_file(p) for p in INPUTS}


def load_all():
    principal = gpd.read_file(V41 / "poligonos_v4_1_mapa_principal_dibujo.geojson")
    decision = gpd.read_file(V41 / "poligonos_v4_1_decision_dibujo.geojson")
    original = gpd.read_file(V41 / "poligonos_v4_original_referencia_sin_cambios.geojson")
    solapes = gpd.read_file(V41 / "solapes_topologia_v4_1.geojson")
    points = gpd.read_file(V4 / "puntos_evidencia_v4.geojson")
    table = pd.read_csv(V41 / "tabla_redibujo_editorial_v4_1.csv")
    qa_topo = json.loads((V41 / "qa_topologia_v4_1.json").read_text(encoding="utf-8"))
    metric_crs = decision.estimate_utm_crs() or "EPSG:32721"
    return principal, decision, original, solapes, points, table, qa_topo, metric_crs


def load_context(metric_crs):
    context = {}
    for key, path in {
        "barrios": ROOT / "data" / "raw" / "geo_barrios.geojson",
        "comunas": ROOT / "data" / "raw" / "geo_comunas.geojson",
    }.items():
        if path.exists():
            context[key] = gpd.read_file(path).to_crs(metric_crs)
    if "barrios" in context:
        context["limite_caba"] = gpd.GeoDataFrame(
            {"nombre": ["Limite CABA"]},
            geometry=[unary_union(context["barrios"].geometry)],
            crs=metric_crs,
        )
    return context


# ------------------------------------------------------------------ contexto
def plot_context(ax, context):
    ax.set_facecolor(EXTERIOR)
    if "limite_caba" in context:
        context["limite_caba"].plot(ax=ax, facecolor=LAND, edgecolor="none", zorder=1)
    if "barrios" in context:
        context["barrios"].boundary.plot(ax=ax, color=BARRIO, linewidth=0.4, zorder=2)
    if "comunas" in context:
        context["comunas"].boundary.plot(ax=ax, color=COMUNA, linewidth=0.6, zorder=3)
    if "limite_caba" in context:
        context["limite_caba"].boundary.plot(ax=ax, color=LIMITE, linewidth=0.9, zorder=4)


def plot_units(ax, g, mode):
    fill = ESTADO_FILL if mode == "status" else FAMILIA_FILL
    edge = ESTADO_EDGE if mode == "status" else FAMILIA_EDGE
    alpha = ESTADO_ALPHA if mode == "status" else FAMILIA_ALPHA
    ls = ESTADO_LS if mode == "status" else FAMILIA_LS
    col = "estado_institucional_sugerido" if mode == "status" else "familia_v4"
    for val, sub in g.groupby(col):
        sub.plot(
            ax=ax,
            facecolor=to_rgba(fill.get(val, "#8f8f8f"), alpha.get(val, 0.4)),
            edgecolor=edge.get(val, "#5f5f5f"),
            linewidth=1.15,
            linestyle=ls.get(val, "solid"),
            zorder=10,
        )


def halo(lw=2.6):
    return [pe.withStroke(linewidth=lw, foreground="white", alpha=0.95)]


def set_bounds(ax, bounds, pad=0.10):
    minx, miny, maxx, maxy = bounds
    dx, dy = maxx - minx, maxy - miny
    ax.set_xlim(minx - dx * pad, maxx + dx * pad)
    ax.set_ylim(miny - dy * pad, maxy + dy * pad)


def add_north_scale(ax):
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    w, h = x1 - x0, y1 - y0
    nx, ny = x0 + w * 0.045, y1 - h * 0.055
    ax.annotate(
        "",
        xy=(nx, ny),
        xytext=(nx, ny - h * 0.05),
        arrowprops=dict(arrowstyle="-|>", lw=1.1, color=INK),
        zorder=30,
    )
    ax.text(nx, ny - h * 0.075, "N", ha="center", va="center", fontsize=8.5, color=INK, weight="bold", zorder=30)
    scale_m = 500 if w < 5000 else 1000 if w < 9000 else 2000 if w < 18000 else 5000
    sx, sy = x0 + w * 0.045, y0 + h * 0.05
    tick = h * 0.006
    ax.plot([sx, sx + scale_m], [sy, sy], color=INK, lw=1.6, zorder=30, solid_capstyle="butt")
    for t in (0, 0.5, 1.0):
        ax.plot([sx + scale_m * t] * 2, [sy - tick, sy + tick], color=INK, lw=1.0, zorder=30)
    label = f"{scale_m / 1000:g} km" if scale_m >= 1000 else f"{scale_m} m"
    ax.text(sx + scale_m / 2, sy + tick * 2.2, label, ha="center", fontsize=7.5, color=INK, zorder=30)


# ------------------------------------------------------------- marco de pagina
def draw_header(fig, title, subtitle, x0=0.035, x1=0.965, y_kicker=0.962, y_title=0.925, y_sub=0.896, y_rule=0.878):
    fig.add_artist(Rectangle((x0, y_kicker - 0.004), 0.0055, 0.020, transform=fig.transFigure, facecolor=INK, edgecolor="none"))
    fig.text(x0 + 0.011, y_kicker, KICKER, fontsize=7.5, color=MUTED, va="bottom")
    fig.text(x0, y_title, title, fontsize=16.5, weight="bold", color=INK, va="bottom")
    fig.text(x0, y_sub, subtitle, fontsize=9.5, color=TEXT2, va="bottom")
    fig.add_artist(Line2D([x0, x1], [y_rule, y_rule], transform=fig.transFigure, color=HAIR, lw=0.9))


def draw_footer(fig, x0=0.035, x1=0.965, y_rule=0.055, band=False):
    if band:
        fig.add_artist(Rectangle((0, 0), 1, y_rule, transform=fig.transFigure, facecolor="#EDF1F4", edgecolor="none"))
        fig.add_artist(Line2D([0, 1], [y_rule, y_rule], transform=fig.transFigure, color=HAIR, lw=0.9))
        y_txt = y_rule / 2
    else:
        fig.add_artist(Line2D([x0, x1], [y_rule, y_rule], transform=fig.transFigure, color=HAIR, lw=0.9))
        y_txt = y_rule - 0.022
    fig.text(x0, y_txt, FOOT_LEFT, fontsize=7.2, color=MUTED, va="center")
    fig.text(x1, y_txt, FOOT_RIGHT, fontsize=7.2, color=MUTED, va="center", ha="right")


def draw_side_panel(fig, rect, legend_items, refs, refs_two_cols, notes):
    """legend_items: (label, fill, edge, alpha, ls, count). refs: [(num, nombre)]."""
    px, py, pw, ph = rect
    fig.add_artist(
        FancyBboxPatch(
            (px, py),
            pw,
            ph,
            transform=fig.transFigure,
            boxstyle="round,pad=0.006,rounding_size=0.010",
            facecolor=PANEL_BG,
            edgecolor=HAIR,
            linewidth=0.9,
        )
    )
    xin = px + 0.014
    y = py + ph - 0.030
    fig.text(xin, y, "LEYENDA", fontsize=8.5, weight="bold", color=INK, va="center")
    y -= 0.034
    for label, fill, edgec, alpha, ls, count in legend_items:
        fig.add_artist(
            Rectangle(
                (xin, y - 0.009),
                0.020,
                0.018,
                transform=fig.transFigure,
                facecolor=to_rgba(fill, alpha),
                edgecolor=edgec,
                linewidth=1.1,
                linestyle=ls,
            )
        )
        txt = f"{label} ({count})" if count is not None else label
        fig.text(xin + 0.028, y, txt, fontsize=7.4, color=TEXT2, va="center")
        y -= 0.030
    y -= 0.004
    for note in notes:
        fig.text(xin, y, note, fontsize=6.4, color=MUTED, va="top", style="italic")
        y -= 0.017 * (note.count("\n") + 1) + 0.006
    y -= 0.010
    fig.text(xin, y, "REFERENCIAS", fontsize=8.5, weight="bold", color=INK, va="center")
    y -= 0.026
    if refs_two_cols:
        import math

        per_col = math.ceil(len(refs) / 2)
        step = min(0.024, (y - py - 0.018) / per_col)
        for i, (num, name) in enumerate(refs):
            col = 0 if i < per_col else 1
            xx = xin if col == 0 else xin + pw / 2 - 0.006
            yy = y - (i if col == 0 else i - per_col) * step
            fig.text(xx, yy, f"{num}. {name}", fontsize=6.2, color=TEXT2, va="top")
    else:
        step = min(0.030, (y - py - 0.018) / max(len(refs), 1))
        for i, (num, name) in enumerate(refs):
            fig.text(xin, y - i * step, f"{num}. {name}", fontsize=7.2, color=TEXT2, va="top")


def label_numbers(ax, g):
    for idx, row in g.iterrows():
        geom = row.geometry
        pieces = list(geom.geoms) if isinstance(geom, MultiPolygon) else [geom]
        pieces = sorted(pieces, key=lambda p: p.area, reverse=True)
        for part_idx, part in enumerate(pieces):
            if part.is_empty:
                continue
            p = part.representative_point()
            txt = str(idx + 1) if part_idx == 0 else f"{idx + 1}.{part_idx + 1}"
            ax.text(
                p.x,
                p.y,
                txt,
                ha="center",
                va="center",
                fontsize=8 if part_idx == 0 else 6.8,
                weight="bold",
                color=INK,
                zorder=25,
                path_effects=halo(),
            )


def label_names(ax, g):
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    span_x, span_y = x1 - x0, y1 - y0
    min_area = 0.0022 * span_x * span_y
    placed: list[tuple[float, float]] = []

    def far_enough(x, y):
        return all(abs(x - px) > span_x * 0.15 or abs(y - py) > span_y * 0.075 for px, py in placed)

    rows = sorted(g.to_dict("records"), key=lambda r: r["geometry"].area, reverse=True)
    for row in rows:
        geom = row["geometry"]
        pieces = list(geom.geoms) if isinstance(geom, MultiPolygon) else [geom]
        pieces = sorted(pieces, key=lambda p: p.area, reverse=True)
        name = short_name(row["nombre_editorial_orientativo"])
        for part_idx, part in enumerate(pieces):
            if part.is_empty:
                continue
            p = part.representative_point()
            if part_idx == 0:
                txt = "\n".join(wrap(name, 16, break_long_words=False))
            else:
                txt = "\n".join(wrap(name, 16, break_long_words=False)) + f"\n(pieza {part_idx + 1})"
            fs = 8 if part_idx == 0 else 6.6
            if part.area >= min_area:
                ax.text(p.x, p.y, txt, ha="center", va="center", fontsize=fs, color=INK, zorder=25, path_effects=halo(2.2))
                placed.append((p.x, p.y))
                continue
            minx, miny, maxx, maxy = part.bounds
            candidates = [
                (p.x, maxy + span_y * 0.035, "center", "bottom", (p.x, p.y + span_y * 0.005, p.x, maxy + span_y * 0.027)),
                (p.x, miny - span_y * 0.035, "center", "top", (p.x, p.y - span_y * 0.005, p.x, miny - span_y * 0.027)),
                (minx - span_x * 0.018, p.y, "right", "center", (p.x - span_x * 0.004, p.y, minx - span_x * 0.012, p.y)),
            ]
            chosen = next((c for c in candidates if far_enough(c[0], c[1])), candidates[0])
            tx, ty, ha, va, (lx0, ly0, lx1, ly1) = chosen
            ax.plot([lx0, lx1], [ly0, ly1], color=LIMITE, lw=0.7, zorder=24)
            ax.text(tx, ty, txt, ha=ha, va=va, fontsize=fs, color=INK, zorder=25, path_effects=halo(2.2))
            placed.append((tx, ty))


def legend_row(fig, items, x0=0.035, y=0.862):
    x = x0
    for label, fill, edgec, alpha, ls in items:
        fig.add_artist(
            Rectangle(
                (x, y - 0.008),
                0.016,
                0.016,
                transform=fig.transFigure,
                facecolor=to_rgba(fill, alpha),
                edgecolor=edgec,
                linewidth=1.0,
                linestyle=ls,
            )
        )
        t = fig.text(x + 0.021, y, label, fontsize=7.4, color=TEXT2, va="center")
        renderer = fig.canvas.get_renderer() if fig.canvas else None
        x += 0.021 + 0.0042 * len(label) + 0.022
        _ = t, renderer


# ------------------------------------------------------------------ mapas
def plot_city_map(g, points, context, metric_crs, path, title, subtitle, mode, table, wide=False):
    g = g.to_crs(metric_crs).reset_index(drop=True)
    pts = points.to_crs(metric_crs)
    if wide:
        figsize, map_rect, panel_rect = (16, 9), [0.025, 0.105, 0.605, 0.755], [0.665, 0.105, 0.310, 0.755]
        header = dict(x0=0.025, x1=0.975, y_kicker=0.955, y_title=0.910, y_sub=0.878, y_rule=0.885)
        header["y_rule"] = 0.868
        footer = dict(x0=0.025, x1=0.975, y_rule=0.058, band=True)
    else:
        figsize, map_rect, panel_rect = (12.5, 10), [0.030, 0.080, 0.645, 0.775], [0.705, 0.080, 0.265, 0.775]
        header = dict(x0=0.035, x1=0.965)
        footer = dict(x0=0.035, x1=0.965)
    fig = plt.figure(figsize=figsize, facecolor=CANVAS)
    ax = fig.add_axes(map_rect)
    plot_context(ax, context)
    if len(pts):
        pts.plot(ax=ax, color=POINTS, markersize=1.4, alpha=0.05, zorder=5)
    plot_units(ax, g, mode)
    label_numbers(ax, g)
    set_bounds(ax, g.total_bounds, pad=0.10)
    add_north_scale(ax)
    ax.set_axis_off()

    draw_header(fig, title, subtitle, **header)
    draw_footer(fig, **footer)

    col = "estado_institucional_sugerido" if mode == "status" else "familia_v4"
    order = STATUS_ORDER if mode == "status" else FAMILY_ORDER
    nombres = ESTADO_NOMBRE if mode == "status" else FAMILIA_NOMBRE
    fill = ESTADO_FILL if mode == "status" else FAMILIA_FILL
    edge = ESTADO_EDGE if mode == "status" else FAMILIA_EDGE
    alpha = ESTADO_ALPHA if mode == "status" else FAMILIA_ALPHA
    ls = ESTADO_LS if mode == "status" else FAMILIA_LS
    counts = g[col].value_counts()
    legend_items = [
        (nombres[v], fill[v], edge[v], alpha[v], ls[v], int(counts[v]))
        for v in sorted(counts.index, key=lambda v: order.get(v, 9))
    ]
    refs = [(i + 1, short_name(row["nombre_editorial_orientativo"])) for i, row in g.iterrows()]
    notes = [
        "n.2 indica pieza secundaria de la unidad n.",
        "Borde discontinuo = requiere revision;\npunteado = exploratoria." if mode == "family" else "Limites orientativos de la capa de dibujo\nv4.1; sin valor de delimitacion oficial.",
    ]
    draw_side_panel(fig, panel_rect, legend_items, refs, refs_two_cols=len(refs) > 16, notes=notes)
    fig.savefig(path, dpi=220 if not wide else 200)
    plt.close(fig)


def zone_layout(bounds, pad=0.20, fig_w=11.0):
    """Altura de figura segun proporcion del encuadre para evitar espacio muerto."""
    minx, miny, maxx, maxy = bounds
    dxp = (maxx - minx) * (1 + 2 * pad)
    dyp = (maxy - miny) * (1 + 2 * pad)
    header_in, footer_in = 1.62, 0.78
    map_w_in = fig_w * 0.93
    map_h_in = map_w_in * dyp / max(dxp, 1)
    fig_h = min(11.0, max(5.6, map_h_in + header_in + footer_in))
    fr = {
        "y_kicker": 1 - 0.36 / fig_h,
        "y_title": 1 - 0.74 / fig_h,
        "y_sub": 1 - 1.02 / fig_h,
        "y_rule": 1 - 1.16 / fig_h,
        "y_legend": 1 - 1.42 / fig_h,
        "ax_rect": [0.035, 0.80 / fig_h, 0.93, 1 - (1.60 / fig_h) - (0.80 / fig_h)],
        "y_foot": 0.55 / fig_h,
    }
    return (fig_w, fig_h), fr


def plot_zone_map(g, points, context, metric_crs, path, title, subtitle):
    g = g.to_crs(metric_crs).reset_index(drop=True)
    pts = points.to_crs(metric_crs)
    pts = pts[pts["id_v4"].isin(g["id_v4"])]
    figsize, fr = zone_layout(g.total_bounds)
    fig = plt.figure(figsize=figsize, facecolor=CANVAS)
    ax = fig.add_axes(fr["ax_rect"])
    plot_context(ax, context)
    if len(pts):
        pts.plot(ax=ax, color=POINTS, markersize=3.0, alpha=0.10, zorder=5)
    plot_units(ax, g, "status")
    set_bounds(ax, g.total_bounds, pad=0.20)
    label_names(ax, g)
    add_north_scale(ax)
    ax.set_axis_off()
    draw_header(fig, title, subtitle, y_kicker=fr["y_kicker"], y_title=fr["y_title"], y_sub=fr["y_sub"], y_rule=fr["y_rule"])
    estados = sorted(g["estado_institucional_sugerido"].unique(), key=lambda v: STATUS_ORDER.get(v, 9))
    legend_row(
        fig,
        [(ESTADO_NOMBRE[v], ESTADO_FILL[v], ESTADO_EDGE[v], ESTADO_ALPHA[v], ESTADO_LS[v]) for v in estados],
        y=fr["y_legend"],
    )
    draw_footer(fig, y_rule=fr["y_foot"])
    fig.savefig(path, dpi=220)
    plt.close(fig)


def plot_anexo_map(g, points, context, metric_crs, path):
    g = g.to_crs(metric_crs).reset_index(drop=True)
    pts = points.to_crs(metric_crs)
    pts = pts[pts["id_v4"].isin(g["id_v4"])]
    figsize, fr = zone_layout(g.total_bounds, pad=0.14)
    fig = plt.figure(figsize=figsize, facecolor=CANVAS)
    ax = fig.add_axes(fr["ax_rect"])
    plot_context(ax, context)
    if len(pts):
        pts.plot(ax=ax, color=POINTS, markersize=3.0, alpha=0.14, zorder=5)
    plot_units(ax, g, "status")
    set_bounds(ax, g.total_bounds, pad=0.14)
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    span_y = y1 - y0
    for _, row in g.iterrows():
        geom = row.geometry
        pieces = list(geom.geoms) if isinstance(geom, MultiPolygon) else [geom]
        main = max(pieces, key=lambda p: p.area)
        p = main.representative_point()
        ax.scatter([p.x], [p.y], s=260, facecolors="none", edgecolors=INK, linewidths=1.3, zorder=24)
        ty = p.y + span_y * 0.045
        ax.plot([p.x, p.x], [p.y + span_y * 0.012, ty - span_y * 0.008], color=LIMITE, lw=0.7, zorder=24)
        ax.text(
            p.x,
            ty,
            "\n".join(wrap(short_name(row["nombre_editorial_orientativo"]), 16, break_long_words=False)),
            ha="center",
            va="bottom",
            fontsize=8,
            color=INK,
            zorder=25,
            path_effects=halo(2.2),
        )
        for extra in pieces:
            if extra is not main and not extra.is_empty:
                q = extra.representative_point()
                ax.scatter([q.x], [q.y], s=120, facecolors="none", edgecolors=INK, linewidths=0.9, zorder=24)
    add_north_scale(ax)
    ax.set_axis_off()
    draw_header(
        fig,
        "Anexo exploratorio - v4.2 design",
        "4 senales exploratorias; anillos marcadores porque las piezas son minusculas a escala ciudad.",
        y_kicker=fr["y_kicker"],
        y_title=fr["y_title"],
        y_sub=fr["y_sub"],
        y_rule=fr["y_rule"],
    )
    legend_row(
        fig,
        [
            ("Exploratoria", ESTADO_FILL["EXPLORATORIA"], ESTADO_EDGE["EXPLORATORIA"], ESTADO_ALPHA["EXPLORATORIA"], ESTADO_LS["EXPLORATORIA"]),
        ],
        y=fr["y_legend"],
    )
    fig.text(0.115, fr["y_legend"], "( ) anillo = ubicacion de la senal", fontsize=7.4, color=MUTED, va="center")
    draw_footer(fig, y_rule=fr["y_foot"])
    fig.savefig(path, dpi=220)
    plt.close(fig)


def plot_qa_map(original, drawing, solapes, points, context, metric_crs, qa_topo, path):
    o = original.to_crs(metric_crs)
    d = drawing.to_crs(metric_crs)
    ov = solapes.to_crs(metric_crs) if len(solapes) else solapes
    pts = points.to_crs(metric_crs)
    fig = plt.figure(figsize=(12.5, 10), facecolor=CANVAS)
    ax = fig.add_axes([0.030, 0.080, 0.94, 0.775])
    plot_context(ax, context)
    if len(pts):
        pts.plot(ax=ax, color=POINTS, markersize=1.6, alpha=0.06, zorder=5)
    o.boundary.plot(ax=ax, color=MUTED, linewidth=0.6, alpha=0.75, zorder=8)
    d.boundary.plot(ax=ax, color="#1E8A63", linewidth=0.95, zorder=9)
    if len(ov):
        ov.plot(ax=ax, color=OVERLAP, alpha=0.8, zorder=15)
    set_bounds(ax, o.total_bounds, pad=0.08)
    add_north_scale(ax)
    ax.set_axis_off()
    draw_header(
        fig,
        "QA de puntos y poligonos - v4.2 design",
        "Control tecnico: geometria v4, capa de dibujo v4.1 y solapes detectados. No usar como mapa final.",
    )
    handles = [
        Line2D([], [], color=MUTED, lw=1.2, label="Geometria v4 (analitica, referencia)"),
        Line2D([], [], color="#1E8A63", lw=1.4, label="Capa de dibujo v4.1 (solo visual)"),
        Patch(facecolor=to_rgba(OVERLAP, 0.8), edgecolor="none", label="Solape detectado en v4"),
        Line2D([], [], color=POINTS, marker=".", lw=0, markersize=6, alpha=0.6, label="Puntos de evidencia v4"),
    ]
    leg = ax.legend(handles=handles, loc="lower right", fontsize=7.4, frameon=True, framealpha=0.95, edgecolor=HAIR, facecolor="white")
    leg.set_zorder(40)
    q = qa_topo
    stats = (
        f"Pares con solape: {q['total_pares_solapados']}  ·  "
        f"superficie solapada: {q['superficie_solapada_ha_total']:.1f} ha\n"
        f"Poligonos ajustados solo en capa de dibujo: "
        f"{q['poligonos_ajustados_capa_decision']['cantidad_poligonos_ajustados']}  ·  "
        f"recorte visual: {q['poligonos_ajustados_capa_decision']['superficie_recortada_visual_ha_total']:.1f} ha\n"
        "El recorte no reasigna puntos ni cambia conteos."
    )
    ax.text(
        0.985,
        0.975,
        stats,
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=7.4,
        color=TEXT2,
        linespacing=1.5,
        bbox=dict(boxstyle="round,pad=0.55", facecolor="white", edgecolor=HAIR, linewidth=0.9),
        zorder=40,
    )
    draw_footer(fig)
    fig.savefig(path, dpi=220)
    plt.close(fig)


# ------------------------------------------------------------------ QA salidas
def png_qa(paths):
    rows = []
    for path in paths:
        img = Image.open(path).convert("RGB")
        w, h = img.size
        small = img.resize((max(1, w // 10), max(1, h // 10)))
        pixels = list(small.getdata())
        non_white = sum(1 for r, g, b in pixels if min(abs(r - 255), abs(g - 255), abs(b - 255)) > 10)
        unique = len(set(pixels))
        rows.append(
            {
                "archivo": path.name,
                "existe": True,
                "ancho_px": w,
                "alto_px": h,
                "colores_unicos_muestra": unique,
                "proporcion_no_blanco_muestra": round(non_white / max(len(pixels), 1), 4),
                "no_blanco": unique > 20 and non_white / max(len(pixels), 1) > 0.02,
            }
        )
    pd.DataFrame(rows).to_csv(OUT / "qa_png_no_blanco_v4_2.csv", index=False, encoding="utf-8-sig")
    return rows


def privacy_scan(paths):
    secret_phrase = "api" + r"[\s_-]?" + "key"
    technical_id = "place" + "_" + "id"
    checks = {
        "email": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
        "dni_cuit": re.compile(r"\b\d{2}-\d{8}-\d\b|(?:dni|cuit|cuil)[^\n]{0,20}\b\d{7,11}\b", re.IGNORECASE),
        "telefono": re.compile(
            r"(?:telefono|tel\.?|celular|whatsapp)[^\n]{0,24}\+?\d[\d\s().-]{7,}"
            r"|\+54[\s().-]*(?:9[\s().-]*)?(?:11|15)[\s().-]*\d{4}[\s().-]*\d{4}",
            re.IGNORECASE,
        ),
        "clave_api_literal": re.compile(secret_phrase, re.IGNORECASE),
        "identificador_places_literal": re.compile(technical_id, re.IGNORECASE),
        "archivo_entorno_literal": re.compile(r"(?<![\w])\.env(?![\w])", re.IGNORECASE),
        "link_privado": re.compile(r"https?://(?:drive\.google\.com|docs\.google\.com|sharepoint|onedrive)", re.IGNORECASE),
    }
    findings = []
    for path in paths:
        if path.suffix.lower() in {".png", ".zip"}:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for name, pattern in checks.items():
            matches = pattern.findall(text)
            if matches:
                findings.append({"archivo": str(path.relative_to(BASE)), "control": name, "cantidad": len(matches)})
    lines = [
        "QA privacidad v4.2",
        f"fecha: {datetime.now().isoformat(timespec='seconds')}",
        f"archivos_texto_revisados: {sum(1 for p in paths if p.suffix.lower() not in {'.png', '.zip'})}",
        f"hallazgos: {len(findings)}",
    ]
    if findings:
        lines += [f"- {i['archivo']} | {i['control']} | {i['cantidad']}" for i in findings]
    else:
        lines.append(
            "Sin hallazgos de correos, telefonos, CUIT/DNI, credenciales, links privados, "
            "identificadores tecnicos de plataformas ni archivos de entorno."
        )
    (OUT / "qa_privacidad_v4_2.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return findings


ZONES = {
    "palermo": (["MZ_PALERMO_SOHO", "MZ_PALERMO_HOLLYWOOD"], "mapa_palermo_v4_2_design.png", "Palermo - v4.2 design"),
    "san_telmo": (["MZ_SAN_TELMO"], "mapa_san_telmo_v4_2_design.png", "San Telmo - v4.2 design"),
    "belgrano": (["MZ_BELGRANO"], "mapa_belgrano_v4_2_design.png", "Belgrano - v4.2 design"),
    "corrientes_microcentro": (
        ["MZ_AVENIDA_CORRIENTES", "MZ_MICROCENTRO_Y_CENTRO"],
        "mapa_corrientes_microcentro_v4_2_design.png",
        "Corrientes / Microcentro - v4.2 design",
    ),
    "caballito": (["MZ_CABALLITO"], "mapa_caballito_v4_2_design.png", "Caballito - v4.2 design"),
    "recoleta": (["MZ_RECOLETA"], "mapa_recoleta_v4_2_design.png", "Recoleta - v4.2 design"),
    "villa_crespo": (["MZ_VILLA_CRESPO"], "mapa_villa_crespo_v4_2_design.png", "Villa Crespo - v4.2 design"),
    "chacarita": (["MZ_CHACARITA"], "mapa_chacarita_v4_2_design.png", "Chacarita - v4.2 design"),
    "puerto_madero": (["MZ_PUERTO_MADERO"], "mapa_puerto_madero_v4_2_design.png", "Puerto Madero - v4.2 design"),
}
ZONE_SUBTITLE = "Encuadre por macrozona sobre capa de dibujo v4.1. Limites orientativos; no usar para computos oficiales."


def generate_maps():
    before = hash_inputs()
    OUT.mkdir(parents=True, exist_ok=True)
    principal, decision, original, solapes, points, table, qa_topo, metric_crs = load_all()
    context = load_context(metric_crs)

    pngs = []

    p = OUT / "mapa_principal_editorial_v4_2_design.png"
    plot_city_map(
        principal, points, context, metric_crs, p,
        "Polos gastronomicos - mapa principal editorial",
        "13 unidades del mapa principal v4.1: 6 candidatas fuertes y 7 con observaciones. Version de diseno v4.2.",
        mode="status", table=table,
    )
    pngs.append(p)

    p = OUT / "mapa_general_decision_v4_2_design.png"
    plot_city_map(
        decision, points, context, metric_crs, p,
        "Polos gastronomicos - mapa general de decision",
        "31 unidades editoriales v4.1 por familia. Mapa de trabajo para decidir, no mapa final. Version de diseno v4.2.",
        mode="family", table=table,
    )
    pngs.append(p)

    p = OUT / "mapa_qa_puntos_y_poligonos_v4_2_design.png"
    plot_qa_map(original, decision, solapes, points, context, metric_crs, qa_topo, p)
    pngs.append(p)

    for _, (mzs, filename, title) in ZONES.items():
        sub = decision[decision["macrozona"].isin(mzs)]
        if not len(sub):
            continue
        p = OUT / filename
        plot_zone_map(sub, points, context, metric_crs, p, title, ZONE_SUBTITLE)
        pngs.append(p)

    anexo = decision[decision["familia_v4"].eq("ANEXO_EXPLORATORIO")]
    p = OUT / "mapa_anexo_exploratorio_v4_2_design.png"
    plot_anexo_map(anexo, points, context, metric_crs, p)
    pngs.append(p)

    p = OUT / "mapa_principal_editorial_v4_2_design_16x9.png"
    plot_city_map(
        principal, points, context, metric_crs, p,
        "Polos gastronomicos - mapa principal editorial",
        "13 unidades del mapa principal v4.1: 6 candidatas fuertes y 7 con observaciones. Version de diseno v4.2.",
        mode="status", table=table, wide=True,
    )
    pngs.append(p)

    p = OUT / "mapa_general_decision_v4_2_design_16x9.png"
    plot_city_map(
        decision, points, context, metric_crs, p,
        "Polos gastronomicos - mapa general de decision",
        "31 unidades editoriales v4.1 por familia. Mapa de trabajo para decidir, no mapa final. Version de diseno v4.2.",
        mode="family", table=table, wide=True,
    )
    pngs.append(p)

    png_rows = png_qa(pngs)
    privacy_findings = privacy_scan(sorted(OUT.rglob("*")))
    after = hash_inputs()

    principal_tbl = table[table["familia_v4"].eq("MAPA_PRINCIPAL")]
    metadata = {
        "fecha_generacion": datetime.now().isoformat(timespec="seconds"),
        "estado": "EXPERIMENTAL / no oficial",
        "version": "v4.2 (design)",
        "tipo": "mejora visual sobre capas de dibujo v4.1; sin cambios de datos, metodologia ni geometria analitica",
        "no_es": ["Fase 26", "v5", "redibujo urbano fino", "cambio metodologico"],
        "insumos_hashes_antes": before,
        "insumos_hashes_despues": after,
        "insumos_sin_cambios": before == after,
        "conteos_congelados": {
            "unidades_total": int(len(table)),
            "principal_total": int(len(principal_tbl)),
            "principal_fuertes": int(principal_tbl["estado_institucional_sugerido"].eq("CANDIDATA_FUERTE").sum()),
            "principal_observaciones": int(principal_tbl["estado_institucional_sugerido"].eq("CANDIDATA_CON_OBSERVACIONES").sum()),
            "puntos_evidencia": int(len(points)),
        },
        "sistema_visual": {
            "paleta_estados": ESTADO_FILL,
            "paleta_familias": FAMILIA_FILL,
            "validacion_paleta": "script de validacion dataviz: luminosidad, croma, CVD y contraste en PASS "
            "(par azul/verde en banda tritan 8-12, cubierto con etiquetas directas y estilo de borde)",
            "guia": "GUIA_VISUAL_CARTOGRAFIA_V4_2.md",
            "uso_claude_design_mcp": "list_design_systems consultado (sin design systems disponibles); se aplico el "
            "design pack DGDGAS y la especificacion Fase 18 derivada de la referencia Claude Design",
        },
        "qa_png": {"cantidad_png": len(png_rows), "png_no_blanco": sum(1 for r in png_rows if r["no_blanco"])},
        "qa_privacidad_hallazgos": privacy_findings,
        "restricciones_cumplidas": [
            "sin API",
            "sin Google Places",
            "sin modificacion de datos fuente",
            "sin reasignacion de puntos",
            "sin cambio de conteos",
            "sin modificacion de Fase 25",
            "sin modificacion de informes oficiales",
            "sin sobrescritura de v4.1",
            "sin staging",
            "sin commit",
            "sin push",
        ],
    }
    (OUT / "metadata_cartografia_v4_2.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"ok": True, "pngs": len(pngs), "no_blanco": metadata["qa_png"]["png_no_blanco"], "privacidad": len(privacy_findings), "hashes_ok": before == after}, ensure_ascii=False))


LEER_PRIMERO = """# Leer primero

Paquete de revision de diseno pre-Fase 26 para la cartografia v4.2 (design) de Polos Gastronomicos.

La v4.2 es solo una capa de diseno sobre la v4.1: no cambia datos, metodologia, clustering,
puntos, conteos ni geometrias analiticas.

Abrir primero:

1. RESUMEN_CAMBIOS_DESIGN_V4_2.md
2. HANDOFF_CARTOGRAFIA_DESIGN_V4_2.md
3. 01_MAPAS_DESIGN_V4_2/mapa_principal_editorial_v4_2_design.png
"""

NOTAS_CHATGPT = """# Notas para ChatGPT

La v4.2 es una capa de diseno sobre la v4.1. No es Fase 26, no es v5 y no cambia metodologia.

Puntos duros:

- no cambiar metodologia ni clustering;
- no llamar APIs ni Google Places;
- no tocar Fase 25 ni informes oficiales;
- no sobrescribir v4 ni v4.1;
- las capas de dibujo son solo para visualizacion, no para computo;
- los conteos estan congelados: 31 unidades, 13 en principal (6 fuertes, 7 con observaciones),
  6.461 puntos de evidencia.

Mapas a mirar primero: principal design, decision design, QA de puntos y poligonos.
La guia de sistema visual esta en 02_GUIA_Y_RESUMEN/GUIA_VISUAL_CARTOGRAFIA_V4_2.md.
"""


def build_package():
    dirs = ["00_LEER_PRIMERO", "01_MAPAS_DESIGN_V4_2", "02_GUIA_Y_RESUMEN", "03_REFERENCIA_V4_1", "04_NOTAS_PARA_CHATGPT"]
    for d in dirs:
        (REVIEW / d).mkdir(parents=True, exist_ok=True)

    for name in [
        "RESUMEN_CAMBIOS_DESIGN_V4_2.md",
        "HANDOFF_CARTOGRAFIA_DESIGN_V4_2.md",
        "metadata_cartografia_v4_2.json",
        "qa_privacidad_v4_2.txt",
        "qa_png_no_blanco_v4_2.csv",
    ]:
        src = OUT / name
        if src.exists():
            shutil.copy2(src, REVIEW / "00_LEER_PRIMERO" / name)
    (REVIEW / "00_LEER_PRIMERO" / "LEER_PRIMERO.md").write_text(LEER_PRIMERO, encoding="utf-8")

    for path in sorted(OUT.glob("*.png")):
        shutil.copy2(path, REVIEW / "01_MAPAS_DESIGN_V4_2" / path.name)

    for name in ["GUIA_VISUAL_CARTOGRAFIA_V4_2.md", "RESUMEN_CAMBIOS_DESIGN_V4_2.md"]:
        src = OUT / name
        if src.exists():
            shutil.copy2(src, REVIEW / "02_GUIA_Y_RESUMEN" / name)

    for name in [
        "mapa_principal_editorial_v4_1.png",
        "mapa_general_decision_v4_1.png",
        "mapa_qa_topologia_v4_1.png",
        "RESUMEN_CARTOGRAFIA_V4_1.md",
    ]:
        src = V41 / name
        if src.exists():
            shutil.copy2(src, REVIEW / "03_REFERENCIA_V4_1" / name)

    (REVIEW / "04_NOTAS_PARA_CHATGPT" / "NOTAS_CHATGPT_DESIGN_V4_2.md").write_text(NOTAS_CHATGPT, encoding="utf-8")

    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(REVIEW.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(REVIEW.parent))

    counts = {}
    for d in [REVIEW] + [p for p in REVIEW.iterdir() if p.is_dir()]:
        counts[str(d.relative_to(REVIEW.parent))] = sum(1 for p in d.rglob("*") if p.is_file())
    meta_path = OUT / "metadata_cartografia_v4_2.json"
    metadata = json.loads(meta_path.read_text(encoding="utf-8"))
    metadata["paquete_revision"] = {
        "ruta": str(REVIEW.relative_to(ROOT)),
        "zip": str(ZIP_PATH.relative_to(ROOT)),
        "zip_bytes": ZIP_PATH.stat().st_size,
        "archivos_por_carpeta": counts,
    }
    meta_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    shutil.copy2(meta_path, REVIEW / "00_LEER_PRIMERO" / "metadata_cartografia_v4_2.json")
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(REVIEW.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(REVIEW.parent))
    print(json.dumps({"ok": True, "zip": str(ZIP_PATH.relative_to(ROOT)), "zip_bytes": ZIP_PATH.stat().st_size, "carpetas": counts}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    if "--package" in sys.argv:
        build_package()
    else:
        generate_maps()
