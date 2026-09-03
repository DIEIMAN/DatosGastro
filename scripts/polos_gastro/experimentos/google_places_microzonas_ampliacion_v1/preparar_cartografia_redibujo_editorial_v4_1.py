from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from textwrap import wrap

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image
from shapely.geometry import GeometryCollection, MultiPolygon, Polygon
from shapely.ops import unary_union
from shapely.validation import make_valid


ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "outputs" / "polos_gastro" / "historico" / "experimentos" / "google_places_microzonas_ampliacion_v1"
V4 = BASE / "cartografia_redibujo_editorial_v4"
OUT = BASE / "cartografia_redibujo_editorial_v4_1"
REVIEW = BASE / "REVISION_CLAUDE_PRE_FASE26_V4_1"
ZIP_PATH = BASE / "REVISION_CLAUDE_PRE_FASE26_V4_1.zip"

INPUTS = [
    "tabla_redibujo_editorial_v4.csv",
    "poligonos_editoriales_redibujados_v4.geojson",
    "poligonos_v4_mapa_principal.geojson",
    "poligonos_v4_requieren_revision.geojson",
    "poligonos_v4_anexo_exploratorio.geojson",
    "puntos_evidencia_v4.geojson",
    "RESUMEN_CARTOGRAFIA_REDIBUJO_EDITORIAL_V4.md",
    "HANDOFF_CARTOGRAFIA_REDIBUJO_EDITORIAL_V4.md",
]

NOTE_DRAWING = (
    "Capa de dibujo sin solapes visuales; no usar para computo de entidades "
    "ni superficies oficiales"
)

FAMILY_ORDER = {
    "MAPA_PRINCIPAL": 1,
    "REQUIERE_REVISION": 2,
    "ANEXO_EXPLORATORIO": 3,
    "EXCLUIR": 4,
}

STATUS_ORDER = {
    "CANDIDATA_FUERTE": 1,
    "CANDIDATA_CON_OBSERVACIONES": 2,
    "REQUIERE_REVISION_HUMANA": 3,
    "EXPLORATORIA": 4,
}

PALETTE = {
    "CANDIDATA_FUERTE": "#1E6F5C",
    "CANDIDATA_CON_OBSERVACIONES": "#2F80B7",
    "REQUIERE_REVISION_HUMANA": "#C9832B",
    "EXPLORATORIA": "#8A6A9E",
}

FAMILY_PALETTE = {
    "MAPA_PRINCIPAL": "#1E6F5C",
    "REQUIERE_REVISION": "#C9832B",
    "ANEXO_EXPLORATORIO": "#8A6A9E",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_inputs() -> dict[str, str]:
    missing = [name for name in INPUTS if not (V4 / name).exists()]
    if missing:
        raise FileNotFoundError(f"Faltan insumos v4: {missing}")
    return {name: sha256_file(V4 / name) for name in INPUTS}


def valid_geom(geom):
    if geom is None or geom.is_empty:
        return geom
    geom = make_valid(geom)
    if isinstance(geom, GeometryCollection):
        polys = [g for g in geom.geoms if isinstance(g, (Polygon, MultiPolygon)) and not g.is_empty]
        if not polys:
            return GeometryCollection()
        return unary_union(polys)
    return geom


def load_layers():
    all_gdf = gpd.read_file(V4 / "poligonos_editoriales_redibujados_v4.geojson")
    principal = gpd.read_file(V4 / "poligonos_v4_mapa_principal.geojson")
    revision = gpd.read_file(V4 / "poligonos_v4_requieren_revision.geojson")
    anexo = gpd.read_file(V4 / "poligonos_v4_anexo_exploratorio.geojson")
    points = gpd.read_file(V4 / "puntos_evidencia_v4.geojson")
    table = pd.read_csv(V4 / "tabla_redibujo_editorial_v4.csv")

    for gdf in [all_gdf, principal, revision, anexo]:
        gdf["geometry"] = gdf.geometry.map(valid_geom)

    metric_crs = all_gdf.estimate_utm_crs() or "EPSG:32721"
    return all_gdf, principal, revision, anexo, points, table, metric_crs


def load_context(metric_crs):
    context = {}
    paths = {
        "barrios": ROOT / "data" / "raw" / "geo_barrios.geojson",
        "comunas": ROOT / "data" / "raw" / "geo_comunas.geojson",
    }
    for key, path in paths.items():
        if path.exists():
            try:
                context[key] = gpd.read_file(path).to_crs(metric_crs)
            except Exception as exc:
                context[f"{key}_error"] = str(exc)
    if "barrios" in context:
        context["limite_caba"] = gpd.GeoDataFrame(
            {"nombre": ["Limite CABA"]},
            geometry=[unary_union(context["barrios"].geometry)],
            crs=metric_crs,
        )
    return context


def area_ha(gdf_metric: gpd.GeoDataFrame) -> pd.Series:
    return gdf_metric.geometry.area / 10_000


def overlap_qa(all_gdf: gpd.GeoDataFrame, metric_crs) -> tuple[pd.DataFrame, gpd.GeoDataFrame]:
    metric = all_gdf.to_crs(metric_crs).copy()
    metric["area_original_ha_metric"] = area_ha(metric)
    rows = []
    geoms = []
    for i in range(len(metric)):
        a = metric.iloc[i]
        for j in range(i + 1, len(metric)):
            b = metric.iloc[j]
            if not a.geometry.intersects(b.geometry):
                continue
            inter = valid_geom(a.geometry.intersection(b.geometry))
            if inter is None or inter.is_empty:
                continue
            ha = inter.area / 10_000
            if ha <= 0.0001:
                continue
            same_family = a["familia_v4"] == b["familia_v4"]
            if a["familia_v4"] == "MAPA_PRINCIPAL" and b["familia_v4"] == "MAPA_PRINCIPAL":
                scope = "solape_mapa_principal"
            elif a["familia_v4"] == "REQUIERE_REVISION" and b["familia_v4"] == "REQUIERE_REVISION":
                scope = "solape_revision"
            elif a["familia_v4"] == "ANEXO_EXPLORATORIO" and b["familia_v4"] == "ANEXO_EXPLORATORIO":
                scope = "solape_anexo"
            elif not same_family:
                scope = "solape_entre_familias"
            else:
                scope = "solape_otra_familia"
            rows.append(
                {
                    "scope": scope,
                    "id_v4_a": a["id_v4"],
                    "id_v4_b": b["id_v4"],
                    "familia_v4_a": a["familia_v4"],
                    "familia_v4_b": b["familia_v4"],
                    "nombre_a": a["nombre_editorial_orientativo"],
                    "nombre_b": b["nombre_editorial_orientativo"],
                    "superficie_solapada_ha": round(ha, 4),
                    "porcentaje_poligono_a": round(ha / max(a["area_original_ha_metric"], 0.000001) * 100, 2),
                    "porcentaje_poligono_b": round(ha / max(b["area_original_ha_metric"], 0.000001) * 100, 2),
                }
            )
            geoms.append(inter)
    qa = pd.DataFrame(rows)
    if geoms:
        overlap_gdf = gpd.GeoDataFrame(qa.copy(), geometry=geoms, crs=metric_crs).to_crs(all_gdf.crs)
    else:
        overlap_gdf = gpd.GeoDataFrame(qa.copy(), geometry=[], crs=all_gdf.crs)
    return qa, overlap_gdf


def make_drawing_layer(gdf: gpd.GeoDataFrame, metric_crs) -> tuple[gpd.GeoDataFrame, dict]:
    metric = gdf.to_crs(metric_crs).copy()
    metric["area_original_dibujo_ha"] = area_ha(metric)
    metric["_family_order"] = metric["familia_v4"].map(FAMILY_ORDER).fillna(9)
    metric["_status_order"] = metric["estado_institucional_sugerido"].map(STATUS_ORDER).fillna(9)
    metric = metric.sort_values(
        ["_family_order", "_status_order", "area_original_dibujo_ha"],
        ascending=[True, True, False],
    )

    occupied = None
    visual_geoms = []
    adjusted_ids = set()
    clipped_ha_by_id = {}
    for _, row in metric.iterrows():
        geom = valid_geom(row.geometry)
        before = geom.area / 10_000 if geom is not None and not geom.is_empty else 0
        if occupied is not None and geom is not None and not geom.is_empty:
            clipped = valid_geom(geom.difference(occupied))
        else:
            clipped = geom
        after = clipped.area / 10_000 if clipped is not None and not clipped.is_empty else 0
        if before - after > 0.0001:
            adjusted_ids.add(row["id_v4"])
            clipped_ha_by_id[row["id_v4"]] = round(before - after, 4)
        if clipped is None or clipped.is_empty:
            clipped = geom
        visual_geoms.append(clipped)
        occupied = geom if occupied is None else valid_geom(unary_union([occupied, geom]))

    metric["geometry"] = visual_geoms
    metric["geometria_para_visualizacion"] = True
    metric["nota_capa"] = NOTE_DRAWING
    metric["superficie_dibujo_ha"] = [round(g.area / 10_000, 4) if g is not None and not g.is_empty else 0 for g in visual_geoms]
    metric["ajuste_visual_realizado"] = metric["id_v4"].isin(adjusted_ids)
    metric["superficie_recortada_visual_ha"] = metric["id_v4"].map(clipped_ha_by_id).fillna(0.0)
    metric = metric.drop(columns=["_family_order", "_status_order"])
    return metric.to_crs(gdf.crs), {
        "poligonos_ajustados": sorted(adjusted_ids),
        "cantidad_poligonos_ajustados": len(adjusted_ids),
        "superficie_recortada_visual_ha_total": round(sum(clipped_ha_by_id.values()), 4),
    }


def short_name(value: str) -> str:
    replacements = {
        "Palermo Hollywood / Fitz Roy": "Hollywood / Fitz Roy",
        "Palermo Soho / Plaza Serrano": "Soho / Plaza Serrano",
        "Recoleta oeste / Santa Fe-Alto Palermo": "Santa Fe / Alto Palermo",
        "Villa Crespo / Corrientes-limite Palermo": "V. Crespo / Corrientes",
        "Puerto Madero centro / diques": "P. Madero centro / diques",
        "Corrientes oeste / Abasto-Once": "Abasto / Once",
        "Corrientes centro / eje teatral-gastronomico": "Corrientes centro / teatral",
        "Corrientes centro teatral": "Corrientes teatral",
        "Corrientes este / Centro": "Corrientes este / Centro",
        "Cabildo / Juramento": "Cabildo / Juramento",
        "Barrio Chino / Barrancas": "Barrio Chino / Barrancas",
        "Libertador / Barrancas-Belgrano norte": "Libertador / Barrancas",
        "Chacarita central / Federico Lacroze": "Chacarita / Lacroze",
        "Avellaneda / zona comercial": "Avellaneda comercial",
        "Florida-Lavalle / Microcentro": "Florida-Lavalle",
        "Microcentro laboral / administrativo": "Microcentro laboral",
        "Costanera Norte / señal exploratoria": "Costanera Norte",
        "Av. Caseros / Barracas exploratoria": "Caseros / Barracas",
        "Puerto Madero / piezas exploratorias": "P. Madero exploratorio",
        "Caballito / señal exploratoria": "Caballito exploratorio",
    }
    return replacements.get(value, value)


def wrapped(value: str, width: int = 20) -> str:
    return "\n".join(wrap(str(value), width=width, break_long_words=False))


def add_north_scale(ax):
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    width = x1 - x0
    height = y1 - y0
    nx = x0 + width * 0.06
    ny = y1 - height * 0.10
    ax.annotate("N", xy=(nx, ny), xytext=(nx, ny - height * 0.07), ha="center", va="center",
                arrowprops=dict(arrowstyle="-|>", lw=1.2, color="#222"), fontsize=9, color="#222")
    scale_m = 1000 if width < 8000 else 2000 if width < 18000 else 5000
    sx = x0 + width * 0.06
    sy = y0 + height * 0.06
    ax.plot([sx, sx + scale_m], [sy, sy], color="#222", lw=2)
    ax.plot([sx, sx], [sy - height * 0.006, sy + height * 0.006], color="#222", lw=1)
    ax.plot([sx + scale_m, sx + scale_m], [sy - height * 0.006, sy + height * 0.006], color="#222", lw=1)
    ax.text(sx + scale_m / 2, sy + height * 0.015, f"{scale_m // 1000} km", ha="center", fontsize=8, color="#222")


def plot_context(ax, context):
    if "barrios" in context:
        context["barrios"].boundary.plot(ax=ax, color="#c6ced3", linewidth=0.35, alpha=0.9, zorder=1)
    if "comunas" in context:
        context["comunas"].boundary.plot(ax=ax, color="#9aa7ad", linewidth=0.65, alpha=0.9, zorder=2)
    if "limite_caba" in context:
        context["limite_caba"].boundary.plot(ax=ax, color="#4d565c", linewidth=0.8, alpha=0.9, zorder=3)


def label_geoms(ax, gdf, label_col="map_label", numbers=False):
    import matplotlib.patheffects as pe

    for idx, row in gdf.iterrows():
        geom = row.geometry
        pieces = list(geom.geoms) if isinstance(geom, MultiPolygon) else [geom]
        pieces = sorted(pieces, key=lambda g: g.area, reverse=True)
        for part_idx, part in enumerate(pieces):
            if part.is_empty:
                continue
            p = part.representative_point()
            if numbers:
                txt = str(idx + 1) if part_idx == 0 else f"{idx + 1}.{part_idx + 1}"
                fs = 7.5
                weight = "bold"
            else:
                base = short_name(row[label_col])
                txt = wrapped(base, 18) if part_idx == 0 else f"{idx + 1}.{part_idx + 1}"
                fs = 6.4 if part_idx == 0 else 5.8
                weight = "regular"
            ax.text(
                p.x,
                p.y,
                txt,
                ha="center",
                va="center",
                fontsize=fs,
                weight=weight,
                color="#263238",
                zorder=20,
                path_effects=[pe.withStroke(linewidth=2.2, foreground="white", alpha=0.95)],
            )


def set_bounds(ax, bounds, pad=0.08):
    minx, miny, maxx, maxy = bounds
    dx = maxx - minx
    dy = maxy - miny
    ax.set_xlim(minx - dx * pad, maxx + dx * pad)
    ax.set_ylim(miny - dy * pad, maxy + dy * pad)


def plot_decision_map(gdf, points, context, metric_crs, path, title, subtitle, mode="family", figsize=(12, 10), numbers=False):
    g = gdf.to_crs(metric_crs).copy()
    pts = points.to_crs(metric_crs)
    fig = plt.figure(figsize=figsize, facecolor="#f7f8f6")
    ax = fig.add_axes([0.04, 0.08, 0.70, 0.82])
    side = fig.add_axes([0.77, 0.08, 0.20, 0.82])
    side.axis("off")
    ax.set_facecolor("#f7f8f6")
    plot_context(ax, context)
    if len(pts) > 0:
        pts.plot(ax=ax, color="#222222", markersize=1.2, alpha=0.035, zorder=4)
    color_col = "familia_v4" if mode == "family" else "estado_institucional_sugerido"
    palette = FAMILY_PALETTE if mode == "family" else PALETTE
    for val, sub in g.groupby(color_col):
        sub.plot(
            ax=ax,
            facecolor=palette.get(val, "#8f8f8f"),
            edgecolor="#24323a",
            linewidth=0.8,
            alpha=0.58,
            zorder=10,
        )
    g = g.reset_index(drop=True)
    g["map_label"] = g["nombre_editorial_orientativo"]
    label_geoms(ax, g, numbers=numbers)
    set_bounds(ax, g.total_bounds, pad=0.14)
    add_north_scale(ax)
    ax.set_axis_off()
    fig.text(0.04, 0.965, title, fontsize=15, weight="bold", color="#1f2a30")
    fig.text(0.04, 0.935, subtitle, fontsize=9, color="#46545c")
    fig.text(0.04, 0.025, "Experimental / no oficial. Mapa de decision y visualizacion, no delimitacion institucional final.", fontsize=8, color="#58666d")

    side.text(0, 1.0, "Leyenda", fontsize=10, weight="bold", color="#1f2a30", va="top")
    y = 0.94
    for val in sorted(g[color_col].dropna().unique(), key=lambda x: FAMILY_ORDER.get(x, STATUS_ORDER.get(x, 9))):
        side.add_patch(plt.Rectangle((0, y - 0.018), 0.045, 0.025, color=palette.get(val, "#8f8f8f"), alpha=0.75))
        side.text(0.06, y, val.replace("_", " ").title(), fontsize=7.5, va="center", color="#263238")
        y -= 0.05
    if numbers:
        y -= 0.02
        side.text(0, y, "Referencias", fontsize=9, weight="bold", color="#1f2a30", va="top")
        y -= 0.04
        if len(g) > 22:
            per_col = math.ceil(len(g) / 2)
            y_start = y
            step = min(0.031, max(0.022, 0.86 / per_col))
            for i, row in g.iterrows():
                col = 0 if i < per_col else 1
                local_i = i if i < per_col else i - per_col
                x = 0 if col == 0 else 0.51
                yy = y_start - local_i * step
                side.text(x, yy, f"{i + 1}. {short_name(row['nombre_editorial_orientativo'])}", fontsize=5.0, color="#263238", va="top")
        else:
            for i, row in g.iterrows():
                if y < 0.02:
                    break
                side.text(0, y, f"{i + 1}. {short_name(row['nombre_editorial_orientativo'])}", fontsize=6.8, color="#263238", va="top")
                y -= 0.034
    fig.savefig(path, dpi=220)
    plt.close(fig)


def plot_zone_map(gdf, points, context, metric_crs, path, title):
    g = gdf.to_crs(metric_crs).copy()
    pts = points.to_crs(metric_crs)
    bounds_poly = unary_union(g.geometry)
    pts = pts[pts.geometry.within(bounds_poly.buffer(500))]
    fig, ax = plt.subplots(figsize=(10, 8), facecolor="#f7f8f6")
    ax.set_facecolor("#f7f8f6")
    plot_context(ax, context)
    if len(pts) > 0:
        pts.plot(ax=ax, color="#36454f", markersize=2.2, alpha=0.07, zorder=4)
    for val, sub in g.groupby("familia_v4"):
        sub.plot(
            ax=ax,
            facecolor=FAMILY_PALETTE.get(val, "#8f8f8f"),
            edgecolor="#24323a",
            linewidth=1.0,
            alpha=0.58,
            zorder=10,
        )
    g = g.reset_index(drop=True)
    g["map_label"] = g["nombre_editorial_orientativo"]
    label_geoms(ax, g, numbers=False)
    set_bounds(ax, g.total_bounds, pad=0.22)
    add_north_scale(ax)
    ax.set_axis_off()
    fig.text(0.05, 0.955, title, fontsize=14, weight="bold", color="#1f2a30")
    fig.text(0.05, 0.925, "Correccion visual v4.1. Limites orientativos; no usar para computos oficiales.", fontsize=8.5, color="#46545c")
    fig.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def plot_topology_map(original, drawing, overlaps, context, metric_crs, path):
    g = original.to_crs(metric_crs)
    d = drawing.to_crs(metric_crs)
    ov = overlaps.to_crs(metric_crs) if len(overlaps) else overlaps
    fig, ax = plt.subplots(figsize=(12, 9), facecolor="#f7f8f6")
    ax.set_facecolor("#f7f8f6")
    plot_context(ax, context)
    g.boundary.plot(ax=ax, color="#607D8B", linewidth=0.5, alpha=0.65, zorder=5)
    d.boundary.plot(ax=ax, color="#1E6F5C", linewidth=0.8, alpha=0.9, zorder=6)
    if len(ov):
        ov.plot(ax=ax, color="#D7263D", alpha=0.75, zorder=20)
    set_bounds(ax, g.total_bounds, pad=0.12)
    add_north_scale(ax)
    ax.set_axis_off()
    fig.text(0.05, 0.955, "QA topologico v4.1", fontsize=15, weight="bold", color="#1f2a30")
    fig.text(0.05, 0.925, "Rojo: solapes detectados en geometria v4. Verde: capa de dibujo recortada para visualizacion.", fontsize=8.5, color="#46545c")
    fig.text(0.05, 0.025, "No usar como mapa final. El recorte no reasigna puntos ni cambia conteos.", fontsize=8, color="#58666d")
    fig.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def write_table_v4_1(table, all_gdf, adjusted_ids):
    geom_info = all_gdf[["id_v4", "geometry"]].copy()
    geom_info["multipoligono"] = geom_info.geometry.geom_type.eq("MultiPolygon")
    table2 = table.merge(geom_info[["id_v4", "multipoligono"]], on="id_v4", how="left")
    table2["nombre_mapa_v4_1"] = table2["nombre_editorial_orientativo"].map(short_name)
    table2["nota_visual_v4_1"] = (
        "Simplificacion editorial v4.1. Principal no significa validada final; limites orientativos."
    )
    puerto = table2["id_v4"].eq("V4_PUERTO_MADERO_CENTRO_DIQUES")
    table2.loc[puerto, "nota_visual_v4_1"] = (
        "Queda en mapa principal por concentracion territorial y lectura de frentes gastronomicos; "
        "las piezas debiles bajan a revision/anexo y sus limites son orientativos."
    )
    table2["requiere_leyenda"] = True
    table2["etiqueta_multipieza"] = table2["multipoligono"].map(
        lambda x: "Etiqueta por pieza en mapas v4.1" if bool(x) else "No aplica"
    )
    table2["ajuste_visual_realizado"] = table2["id_v4"].isin(adjusted_ids)
    table2["usar_en_fase26"] = table2["familia_v4"].map(
        {
            "MAPA_PRINCIPAL": "SI, como insumo de comparacion pre-Fase 26",
            "REQUIERE_REVISION": "NO sin revision humana previa",
            "ANEXO_EXPLORATORIO": "NO; mantener como anexo exploratorio",
        }
    ).fillna("NO")
    table2["advertencia_fase26"] = (
        "v4.1 corrige visualizacion y QA topologico; no cambia metodologia, puntos ni conteos."
    )
    table2.loc[puerto, "advertencia_fase26"] = (
        "Puerto Madero centro/diques puede compararse como candidata con observaciones; "
        "sus limites siguen siendo orientativos."
    )
    table2.to_csv(OUT / "tabla_redibujo_editorial_v4_1.csv", index=False, encoding="utf-8-sig")
    return table2


def write_docs(summary, table_counts, context_notes):
    resumen = f"""# Resumen cartografia v4.1

## Veredicto

La v4.1 es una correccion visual y topologica minima de la simplificacion editorial v4. No es v5, no es Fase 26 y no cambia datos, metodologia, puntos, conteos ni asignaciones.

## Que corrige

- Genera QA topologico formal sobre las 31 unidades v4.
- Crea capas de dibujo sin solapes visuales para mapas, sin uso computacional.
- Corrige terminologia: se usa "simplificacion editorial v4.1" o "correccion visual v4.1".
- Agrega leyenda, norte, escala, contexto urbano local disponible y notas de uso.
- Declara que el mapa principal tiene 13 unidades: 6 candidatas fuertes y 7 candidatas con observaciones.

## Que no cambia

- No se reasignan puntos.
- No se modifica entidades_total, cantidad_places ni cantidad_f01_f02.
- No se toca la tabla base de evidencia.
- No se llama a APIs ni a Google Places.
- No se modifica Fase 25 ni informes oficiales.
- No se sobrescribe v4.

## QA topologico

- Pares con solape detectado: {summary['overlap_pairs']}.
- Pares del mapa principal con solape: {summary['overlap_pairs_principal']}.
- Poligonos ajustados solo en capa de dibujo: {summary['drawing_adjusted_polygons']}.
- Superficie recortada solo para visualizacion: {summary['drawing_clipped_ha']} ha.

## Puerto Madero

Puerto Madero centro / diques queda en el mapa principal como candidata con observaciones por concentracion territorial, lectura de frentes gastronomicos y separacion de piezas debiles hacia revision/anexo. Sus limites son orientativos y no deben leerse como delimitacion final.

## Ubicaciones que quedan en revision

Corrientes/Microcentro, Belgrano y Caballito quedan correctamente ubicadas en REQUIERE_REVISION. No se las promueve en v4.1 porque requieren redibujo urbano fino posterior.

## Contexto urbano

{context_notes}

## Listo para comparacion

La carpeta v4.1 queda lista para revision visual y para comparacion previa a Fase 26. La Fase 26 debe usar las capas originales como referencia metodologica y las capas de dibujo solo para comunicacion visual.

## Pendiente

Queda pendiente una etapa posterior de redibujo urbano fino sobre calles, avenidas y frentes reales, con auditoria antes de cualquier cambio metodologico.
"""
    (OUT / "RESUMEN_CARTOGRAFIA_V4_1.md").write_text(resumen, encoding="utf-8")

    handoff = f"""# Handoff cartografia v4.1

## Mirar primero

1. mapa_principal_editorial_v4_1.png
2. mapa_general_decision_v4_1.png
3. mapa_qa_topologia_v4_1.png
4. tabla_redibujo_editorial_v4_1.csv

## Capas para Fase 26

- Usar poligonos_v4_original_referencia_sin_cambios.geojson como referencia de geometria v4.
- Usar tabla_redibujo_editorial_v4_1.csv para advertencias, nombres de mapa y estado pre-Fase 26.
- Usar poligonos_v4_1_mapa_principal_dibujo.geojson solo para visualizacion en slides o revision.
- Usar poligonos_v4_1_decision_dibujo.geojson solo para mapa de decision.

## Capas que no se usan para computo

- poligonos_v4_1_mapa_principal_dibujo.geojson
- poligonos_v4_1_decision_dibujo.geojson

Ambas tienen geometria_para_visualizacion = true y no deben usarse para entidades, superficies oficiales ni reasignacion de puntos.

## Claude Design MCP

El paquete REVISION_CLAUDE_PRE_FASE26_V4_1 incluye un prompt especifico para mejorar sistema visual, paleta, jerarquia tipografica, layout 16:9 y estilo de etiquetas sin tocar datos ni llamar APIs.

## Redibujo urbano futuro

El redibujo urbano fino sobre calles queda pendiente. v4.1 solo reduce solapes visuales y mejora legibilidad.

## Conteos congelados

- Unidades v4.1: {table_counts['unidades_total']}.
- Mapa principal: {table_counts['principal_total']} unidades.
- Candidatas fuertes en principal: {table_counts['principal_fuertes']}.
- Candidatas con observaciones en principal: {table_counts['principal_observaciones']}.
- Puntos de evidencia v4: {table_counts['puntos_evidencia']}.
"""
    (OUT / "HANDOFF_CARTOGRAFIA_V4_1.md").write_text(handoff, encoding="utf-8")


def png_qa(paths):
    rows = []
    for path in paths:
        img = Image.open(path).convert("RGB")
        w, h = img.size
        small = img.resize((max(1, w // 10), max(1, h // 10)))
        pixels = list(small.getdata())
        non_white = sum(1 for r, g, b in pixels if min(abs(r - 255), abs(g - 255), abs(b - 255)) > 10 and (r, g, b) != (255, 255, 255))
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
    pd.DataFrame(rows).to_csv(OUT / "qa_png_no_blanco_v4_1.csv", index=False, encoding="utf-8-sig")
    return rows


def privacy_scan(paths):
    secret_phrase = "api" + r"[\s_-]?" + "key"
    technical_id = "place" + "_" + "id"
    checks = {
        "email": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
        "dni_cuit": re.compile(
            r"\b\d{2}-\d{8}-\d\b|(?:dni|cuit|cuil)[^\n]{0,20}\b\d{7,11}\b",
            re.IGNORECASE,
        ),
        "telefono": re.compile(
            r"(?:telefono|tel\.?|celular|whatsapp)[^\n]{0,24}\+?\d[\d\s().-]{7,}"
            r"|\+54[\s().-]*(?:9[\s().-]*)?(?:11|15)[\s().-]*\d{4}[\s().-]*\d{4}",
            re.IGNORECASE,
        ),
        "clave_api_literal": re.compile(secret_phrase, re.IGNORECASE),
        "identificador_places_literal": re.compile(technical_id, re.IGNORECASE),
        "archivo_entorno_literal": re.compile(r"(?<![\w])\.env(?![\w])", re.IGNORECASE),
        "ruta_privada_literal": re.compile(r"interno[\\/]", re.IGNORECASE),
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
        "QA privacidad v4.1",
        f"fecha: {datetime.now().isoformat(timespec='seconds')}",
        f"archivos_texto_revisados: {sum(1 for p in paths if p.suffix.lower() not in {'.png', '.zip'})}",
        f"hallazgos: {len(findings)}",
    ]
    if findings:
        for item in findings:
            lines.append(f"- {item['archivo']} | {item['control']} | {item['cantidad']}")
    else:
        lines.append("Sin hallazgos de correos, telefonos, CUIT/DNI, credenciales, links privados, identificadores tecnicos de Places, archivos de entorno ni rutas privadas.")
    (OUT / "qa_privacidad_v4_1.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return findings


def copy_into_package():
    dirs = [
        "00_LEER_PRIMERO",
        "01_MAPAS_V4_1",
        "02_TABLAS_V4_1",
        "03_GEOJSON_V4_1",
        "04_REFERENCIA_V4",
        "05_PROMPT_PARA_CLAUDE_DESIGN",
        "06_NOTAS_PARA_CHATGPT",
    ]
    for d in dirs:
        (REVIEW / d).mkdir(parents=True, exist_ok=True)

    for name in ["RESUMEN_CARTOGRAFIA_V4_1.md", "HANDOFF_CARTOGRAFIA_V4_1.md", "metadata_cartografia_v4_1.json", "qa_privacidad_v4_1.txt"]:
        src = OUT / name
        if src.exists():
            shutil.copy2(src, REVIEW / "00_LEER_PRIMERO" / name)
    for path in OUT.glob("*.png"):
        shutil.copy2(path, REVIEW / "01_MAPAS_V4_1" / path.name)
    for pattern in ["*.csv", "*.json"]:
        for path in OUT.glob(pattern):
            if path.name == "metadata_cartografia_v4_1.json":
                continue
            shutil.copy2(path, REVIEW / "02_TABLAS_V4_1" / path.name)
    for path in OUT.glob("*.geojson"):
        shutil.copy2(path, REVIEW / "03_GEOJSON_V4_1" / path.name)
    for name in ["mapa_principal_editorial_v4.png", "mapa_general_decision_v4.png", "mapa_qa_puntos_y_poligonos_v4.png"]:
        if (V4 / name).exists():
            shutil.copy2(V4 / name, REVIEW / "04_REFERENCIA_V4" / name)

    prompt = """# Prompt Claude Design MCP - cartografia v4.1

Objetivo: mejorar el sistema visual de los mapas v4.1 de Polos Gastronomicos antes de Fase 26.

Trabajar solo sobre presentacion visual. No tocar datos, no cambiar geometria base, no reasignar puntos, no llamar APIs y auditar antes de modificar.

Revisar:

- paleta institucional para mapa principal, mapa de decision y anexo;
- jerarquia tipografica para titulos, notas, leyendas y etiquetas;
- layout 16:9 para presentaciones;
- etiquetas con halo o lineas guia para evitar colisiones;
- tratamiento diferenciado de mapa principal, revision y anexo exploratorio;
- consistencia de escala, norte, leyendas y disclaimers.

Mantener la advertencia: las capas de dibujo no se usan para computo ni superficies oficiales.
"""
    (REVIEW / "05_PROMPT_PARA_CLAUDE_DESIGN" / "PROMPT_CLAUDE_DESIGN_V4_1.md").write_text(prompt, encoding="utf-8")

    notes = """# Notas para ChatGPT

La v4.1 es una correccion visual/topologica minima de v4. No es Fase 26 ni v5.

Puntos duros:

- no cambiar metodologia;
- no llamar APIs;
- no usar Google Places;
- no tocar Fase 25;
- no tocar informes oficiales;
- no sobrescribir v4;
- usar capas de dibujo solo para visualizacion.

Mapas a mirar primero: principal, decision, QA topologico.
"""
    (REVIEW / "06_NOTAS_PARA_CHATGPT" / "NOTAS_CHATGPT_V4_1.md").write_text(notes, encoding="utf-8")

    leer = """# Leer primero

Paquete de revision pre-Fase 26 para cartografia editorial v4.1.

Abrir primero RESUMEN_CARTOGRAFIA_V4_1.md y HANDOFF_CARTOGRAFIA_V4_1.md.
"""
    (REVIEW / "00_LEER_PRIMERO" / "LEER_PRIMERO.md").write_text(leer, encoding="utf-8")


def zip_package():
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in REVIEW.rglob("*"):
            if path.is_file():
                zf.write(path, path.relative_to(REVIEW.parent))
    return ZIP_PATH.stat().st_size


def file_counts_by_folder(root: Path):
    counts = {}
    for d in [root] + [p for p in root.iterdir() if p.is_dir()]:
        counts[str(d.relative_to(root.parent))] = sum(1 for p in d.rglob("*") if p.is_file())
    return counts


def main():
    before_hashes = ensure_inputs()
    OUT.mkdir(parents=True, exist_ok=True)

    all_gdf, principal, revision, anexo, points, table, metric_crs = load_layers()
    context = load_context(metric_crs)
    context_notes = "Se usaron capas locales de barrios y comunas; el limite CABA se derivo de barrios."
    if "barrios" not in context:
        context_notes = "No se encontraron capas urbanas locales suficientes; registrar limitacion."

    qa, overlap_gdf = overlap_qa(all_gdf, metric_crs)
    qa.to_csv(OUT / "qa_topologia_v4_1.csv", index=False, encoding="utf-8-sig")
    overlap_gdf.to_file(OUT / "solapes_topologia_v4_1.geojson", driver="GeoJSON")

    principal_draw, principal_draw_summary = make_drawing_layer(principal, metric_crs)
    decision_draw, decision_draw_summary = make_drawing_layer(all_gdf, metric_crs)
    principal_draw.to_file(OUT / "poligonos_v4_1_mapa_principal_dibujo.geojson", driver="GeoJSON")
    decision_draw.to_file(OUT / "poligonos_v4_1_decision_dibujo.geojson", driver="GeoJSON")
    shutil.copy2(V4 / "poligonos_editoriales_redibujados_v4.geojson", OUT / "poligonos_v4_original_referencia_sin_cambios.geojson")

    adjusted_ids = set(decision_draw_summary["poligonos_ajustados"])
    table2 = write_table_v4_1(table, all_gdf, adjusted_ids)

    qa_summary = {
        "fecha": datetime.now().isoformat(timespec="seconds"),
        "crs_metrico_para_areas": str(metric_crs),
        "total_pares_solapados": int(len(qa)),
        "pares_por_scope": qa["scope"].value_counts().to_dict() if len(qa) else {},
        "superficie_solapada_ha_total": round(float(qa["superficie_solapada_ha"].sum()), 4) if len(qa) else 0,
        "poligonos_ajustados_capa_decision": decision_draw_summary,
        "poligonos_ajustados_capa_principal": principal_draw_summary,
        "nota": "Los recortes son solo para capas de dibujo y no alteran datos, puntos ni conteos.",
    }
    (OUT / "qa_topologia_v4_1.json").write_text(json.dumps(qa_summary, ensure_ascii=False, indent=2), encoding="utf-8")

    principal_count = table2[table2["familia_v4"].eq("MAPA_PRINCIPAL")]
    table_counts = {
        "unidades_total": int(len(table2)),
        "principal_total": int(len(principal_count)),
        "principal_fuertes": int(principal_count["estado_institucional_sugerido"].eq("CANDIDATA_FUERTE").sum()),
        "principal_observaciones": int(principal_count["estado_institucional_sugerido"].eq("CANDIDATA_CON_OBSERVACIONES").sum()),
        "puntos_evidencia": int(len(points)),
    }
    doc_summary = {
        "overlap_pairs": int(len(qa)),
        "overlap_pairs_principal": int((qa["scope"].eq("solape_mapa_principal")).sum()) if len(qa) else 0,
        "drawing_adjusted_polygons": int(decision_draw_summary["cantidad_poligonos_ajustados"]),
        "drawing_clipped_ha": decision_draw_summary["superficie_recortada_visual_ha_total"],
    }
    write_docs(doc_summary, table_counts, context_notes)

    pngs = []
    plot_decision_map(
        principal_draw,
        points,
        context,
        metric_crs,
        OUT / "mapa_principal_editorial_v4_1.png",
        "Polos Gastronomicos - mapa principal editorial v4.1",
        "13 unidades principales: 6 fuertes, 7 con observaciones",
        mode="status",
        figsize=(12, 10),
        numbers=True,
    )
    pngs.append(OUT / "mapa_principal_editorial_v4_1.png")
    plot_decision_map(
        decision_draw,
        points,
        context,
        metric_crs,
        OUT / "mapa_general_decision_v4_1.png",
        "Polos Gastronomicos - mapa de decision v4.1",
        "Mapa de decision, no mapa final. Jerarquia: principal, revision, anexo.",
        mode="family",
        figsize=(13, 10),
        numbers=True,
    )
    pngs.append(OUT / "mapa_general_decision_v4_1.png")
    plot_topology_map(all_gdf, decision_draw, overlap_gdf, context, metric_crs, OUT / "mapa_qa_topologia_v4_1.png")
    pngs.append(OUT / "mapa_qa_topologia_v4_1.png")
    plot_decision_map(
        principal_draw,
        points,
        context,
        metric_crs,
        OUT / "mapa_principal_editorial_v4_1_16x9.png",
        "Polos Gastronomicos - mapa principal editorial v4.1",
        "13 unidades principales: 6 fuertes, 7 con observaciones",
        mode="status",
        figsize=(16, 9),
        numbers=True,
    )
    pngs.append(OUT / "mapa_principal_editorial_v4_1_16x9.png")
    plot_decision_map(
        decision_draw,
        points,
        context,
        metric_crs,
        OUT / "mapa_general_decision_v4_1_16x9.png",
        "Polos Gastronomicos - mapa de decision v4.1",
        "Mapa de decision, no mapa final.",
        mode="family",
        figsize=(16, 9),
        numbers=True,
    )
    pngs.append(OUT / "mapa_general_decision_v4_1_16x9.png")

    zones = {
        "palermo": ("PALERMO", "mapa_palermo_v4_1.png", "Palermo - v4.1"),
        "san_telmo": ("SAN_TELMO", "mapa_san_telmo_v4_1.png", "San Telmo - v4.1"),
        "belgrano": ("BELGRANO", "mapa_belgrano_v4_1.png", "Belgrano - v4.1"),
        "corrientes_microcentro": ("CORRIENTES", "mapa_corrientes_microcentro_v4_1.png", "Corrientes / Microcentro - v4.1"),
        "caballito": ("CABALLITO", "mapa_caballito_v4_1.png", "Caballito - v4.1"),
        "recoleta": ("RECOLETA", "mapa_recoleta_v4_1.png", "Recoleta - v4.1"),
        "villa_crespo": ("VILLA_CRESPO", "mapa_villa_crespo_v4_1.png", "Villa Crespo - v4.1"),
        "chacarita": ("CHACARITA", "mapa_chacarita_v4_1.png", "Chacarita - v4.1"),
        "puerto_madero": ("PUERTO_MADERO", "mapa_puerto_madero_v4_1.png", "Puerto Madero - v4.1"),
    }
    for _, (needle, filename, title) in zones.items():
        sub = decision_draw[
            decision_draw["id_v4"].str.contains(needle, case=False, na=False)
            | decision_draw["macrozona"].str.contains(needle, case=False, na=False)
        ]
        if len(sub):
            plot_zone_map(sub, points[points["id_v4"].isin(sub["id_v4"])], context, metric_crs, OUT / filename, title)
            pngs.append(OUT / filename)

    anexo_draw = decision_draw[decision_draw["familia_v4"].eq("ANEXO_EXPLORATORIO")]
    plot_zone_map(anexo_draw, points[points["id_v4"].isin(anexo_draw["id_v4"])], context, metric_crs, OUT / "mapa_anexo_exploratorio_v4_1.png", "Anexo exploratorio - v4.1")
    pngs.append(OUT / "mapa_anexo_exploratorio_v4_1.png")

    png_rows = png_qa(pngs)
    privacy_findings = privacy_scan(list(OUT.rglob("*")))

    after_hashes = {name: sha256_file(V4 / name) for name in INPUTS}
    hashes_ok = before_hashes == after_hashes

    metadata = {
        "fecha_generacion": datetime.now().isoformat(timespec="seconds"),
        "estado": "EXPERIMENTAL / no oficial",
        "version": "v4.1",
        "tipo": "correccion visual y QA topologico minimo de v4",
        "no_es": ["Fase 26", "v5", "redibujo urbano fino"],
        "insumos_v4_hashes_antes": before_hashes,
        "insumos_v4_hashes_despues": after_hashes,
        "insumos_v4_sin_cambios": hashes_ok,
        "conteos": table_counts,
        "qa_topologia": qa_summary,
        "qa_png": {
            "cantidad_png": len(png_rows),
            "png_no_blanco": sum(1 for row in png_rows if row["no_blanco"]),
        },
        "qa_privacidad_hallazgos": privacy_findings,
        "contexto_urbano": {
            "barrios_local": "barrios" in context,
            "comunas_local": "comunas" in context,
            "limite_caba_derivado": "limite_caba" in context,
            "avenidas_calles_plazas_manzanas": "no localizadas en esta tanda",
        },
        "restricciones_cumplidas": [
            "sin API",
            "sin Google Places",
            "sin modificacion de datos fuente",
            "sin reasignacion de puntos",
            "sin modificacion de Fase 25",
            "sin modificacion de informes oficiales",
            "sin staging",
            "sin commit",
            "sin push",
        ],
    }
    (OUT / "metadata_cartografia_v4_1.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    copy_into_package()
    # Refresh metadata in package after it exists.
    shutil.copy2(OUT / "metadata_cartografia_v4_1.json", REVIEW / "00_LEER_PRIMERO" / "metadata_cartografia_v4_1.json")
    zip_size = zip_package()

    metadata["paquete_revision"] = {
        "ruta": str(REVIEW.relative_to(ROOT)),
        "zip": str(ZIP_PATH.relative_to(ROOT)),
        "zip_bytes": zip_size,
        "archivos_por_carpeta": file_counts_by_folder(REVIEW),
    }
    (OUT / "metadata_cartografia_v4_1.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    shutil.copy2(OUT / "metadata_cartografia_v4_1.json", REVIEW / "00_LEER_PRIMERO" / "metadata_cartografia_v4_1.json")
    # Rebuild ZIP once metadata has package counts.
    zip_size = zip_package()
    metadata["paquete_revision"]["zip_bytes"] = zip_size
    (OUT / "metadata_cartografia_v4_1.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    shutil.copy2(OUT / "metadata_cartografia_v4_1.json", REVIEW / "00_LEER_PRIMERO" / "metadata_cartografia_v4_1.json")
    zip_size = zip_package()

    print(json.dumps({
        "ok": True,
        "out": str(OUT.relative_to(ROOT)),
        "review": str(REVIEW.relative_to(ROOT)),
        "zip": str(ZIP_PATH.relative_to(ROOT)),
        "zip_bytes": zip_size,
        "overlap_pairs": len(qa),
        "adjusted_polygons_decision": decision_draw_summary["cantidad_poligonos_ajustados"],
        "pngs": len(pngs),
        "privacy_findings": len(privacy_findings),
        "hashes_ok": hashes_ok,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
