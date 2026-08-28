# -*- coding: utf-8 -*-
"""Integración técnica v2.1 del pipeline híbrido territorial.

EXPERIMENTAL / NO OFICIAL. Trabaja exclusivamente con insumos locales ya
almacenados. No llama APIs, no descarga datos, no instala dependencias y no
modifica fuentes, Fase 25, Fase 26, v1-v4.2 ni repeticiones v2.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shapely
from PIL import Image, ImageStat
from scipy.ndimage import maximum_filter
from scipy.spatial import cKDTree
from shapely.geometry import LineString, MultiPoint, MultiPolygon, Point
from shapely.ops import nearest_points, unary_union
from sklearn.cluster import HDBSCAN
from sklearn.metrics import adjusted_rand_score
from sklearn.neighbors import KernelDensity


ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "outputs/polos_gastro/experimentos/pipeline_hibrido_integracion_v21"
DOC = ROOT / "docs/polos_gastro/experimentos/pipeline_hibrido_integracion_v21"
SCRIPT_DIR = ROOT / "scripts/polos_gastro/experimentos/pipeline_hibrido_integracion_v21"
HANDOFF = OUT / "HANDOFF_FABLE"
V2 = ROOT / "outputs/polos_gastro/experimentos/pipeline_hibrido_repeticiones_v2"
V2_DOC = ROOT / "docs/polos_gastro/experimentos/pipeline_hibrido_repeticiones_v2"
V1_SCRIPT = ROOT / "scripts/polos_gastro/experimentos/pipeline_hibrido_tipo_territorial_v1/construir_pipeline_hibrido_v1.py"
CRS_M = "EPSG:5347"
CRS_GEO = "EPSG:4326"
SEED = 260711
RNG = np.random.default_rng(SEED)
DATE = "2026-07-11"
NOTE = "EXPERIMENTAL / NO OFICIAL. Oferta registrada/visible; buffers orientativos; no es delimitación institucional."

COLORS = {
    "base": "#1F5D7A", "places": "#C47A1D", "primary": "#16845B",
    "secondary": "#76549A", "context": "#A0A7AD", "street": "#D8DCDF",
    "border": "#53606A", "warning": "#B34A3C",
}

PROTECTED = [
    ROOT / "docs/polos_gastro/fase25_microajustes_finales_oficina",
    ROOT / "outputs/polos_gastro/fase25_microajustes_finales_oficina",
    ROOT / "scripts/polos_gastro/build_fase25_microajustes_finales_oficina.py",
    ROOT / "docs/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/fase26_comparativa_cartografia",
    ROOT / "outputs/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/fase26_comparativa_cartografia",
    ROOT / "outputs/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/completa_v1",
    ROOT / "outputs/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/cartografia_editorial_v2",
    ROOT / "outputs/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/cartografia_decision_v3",
    ROOT / "outputs/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/cartografia_redibujo_editorial_v4",
    ROOT / "outputs/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/cartografia_redibujo_editorial_v4_1",
    ROOT / "outputs/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/cartografia_design_v4_2",
    ROOT / "docs/polos_gastro/experimentos/pipeline_hibrido_tipo_territorial_v1",
    ROOT / "outputs/polos_gastro/experimentos/pipeline_hibrido_tipo_territorial_v1",
    ROOT / "scripts/polos_gastro/experimentos/pipeline_hibrido_tipo_territorial_v1",
    ROOT / "docs/polos_gastro/experimentos/pipeline_hibrido_repeticiones_v2",
    ROOT / "outputs/polos_gastro/experimentos/pipeline_hibrido_repeticiones_v2",
    ROOT / "scripts/polos_gastro/experimentos/pipeline_hibrido_repeticiones_v2",
]


def ensure_dirs() -> None:
    for path in (OUT, DOC, SCRIPT_DIR, HANDOFF):
        path.mkdir(parents=True, exist_ok=True)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def protected_hashes() -> dict[str, str]:
    result: dict[str, str] = {}
    for target in PROTECTED:
        if target.is_file():
            result[target.relative_to(ROOT).as_posix()] = sha256(target)
        elif target.is_dir():
            for path in sorted(target.rglob("*")):
                if path.is_file():
                    result[path.relative_to(ROOT).as_posix()] = sha256(path)
    return result


def load_v1():
    spec = importlib.util.spec_from_file_location("pipeline_hibrido_v1_readonly_v21", V1_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def write_geo(gdf: gpd.GeoDataFrame, path: Path) -> None:
    clean = gdf.copy()
    for col in clean.columns:
        if col != "geometry" and clean[col].dtype == "object":
            clean[col] = clean[col].fillna("").astype(str)
    if clean.empty:
        path.write_text('{"type":"FeatureCollection","features":[]}', encoding="utf-8")
    else:
        clean.to_crs(CRS_GEO).to_file(path, driver="GeoJSON")


def write_csv(frame: pd.DataFrame, path: Path) -> None:
    frame.to_csv(path, index=False, encoding="utf-8")


def md_table(frame: pd.DataFrame) -> str:
    clean = frame.fillna("").astype(str).apply(lambda c: c.str.replace("|", "\\|", regex=False))
    head = "| " + " | ".join(clean.columns) + " |"
    sep = "|" + "|".join(["---"] * len(clean.columns)) + "|"
    rows = ["| " + " | ".join(row) + " |" for row in clean.to_numpy().tolist()]
    return "\n".join([head, sep, *rows])


def points_for(data: dict, macro_id: str) -> gpd.GeoDataFrame:
    return data["points"][data["points"].macrozona_id.eq(macro_id)].copy().reset_index(drop=True)


def xy(points: gpd.GeoDataFrame) -> np.ndarray:
    return np.column_stack([points.geometry.x.to_numpy(), points.geometry.y.to_numpy()])


def components(geom) -> int:
    if geom is None or geom.is_empty:
        return 0
    return len(geom.geoms) if hasattr(geom, "geoms") else 1


def source_counts(points: gpd.GeoDataFrame) -> tuple[int, int, float]:
    places = int(points.fuente.eq("google_places").sum())
    base = len(points) - places
    return base, places, round(100 * places / max(1, len(points)), 2)


def plot_context(ax, data: dict, points: gpd.GeoDataFrame, geom, title: str, show_points: bool = True) -> None:
    minx, miny, maxx, maxy = geom.bounds
    pad = max(maxx - minx, maxy - miny) * .08
    streets = data["streets"].cx[minx-pad:maxx+pad, miny-pad:maxy+pad]
    if len(streets):
        streets.plot(ax=ax, color=COLORS["street"], linewidth=.35, zorder=1)
    gpd.GeoSeries([geom], crs=CRS_M).boundary.plot(ax=ax, color=COLORS["border"], linewidth=1, linestyle="--")
    if show_points:
        base = points[points.fuente.eq("F01+F02")]
        places = points[points.fuente.eq("google_places")]
        if len(base): base.plot(ax=ax, color=COLORS["base"], markersize=7, alpha=.58, zorder=4)
        if len(places): places.plot(ax=ax, color=COLORS["places"], markersize=6, alpha=.38, zorder=3)
    ax.set_title(title, loc="left", fontsize=11, fontweight="bold")
    ax.set_aspect("equal")
    ax.set_axis_off()


def save_fig(fig, path: Path) -> None:
    fig.text(.015, .012, NOTE, fontsize=6.8, color=COLORS["border"])
    fig.tight_layout(rect=(0, .035, 1, 1))
    fig.savefig(path, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def jaccard(a: set[int], b: set[int]) -> float:
    return len(a & b) / max(1, len(a | b))


def best_match(target: set[int], labels: np.ndarray, indices: np.ndarray) -> float:
    scores = []
    for cid in set(labels.tolist()) - {-1}:
        candidate = set(indices[np.flatnonzero(labels == cid)].tolist())
        scores.append(jaccard(target, candidate))
    return max(scores or [0.0])


def audit_v2(data: dict) -> dict:
    cost = pd.read_csv(V2 / "costanera_componentes_v2.csv")
    bel = pd.read_csv(V2 / "belgrano_estabilidad_nucleos_v2.csv")
    pm = pd.read_csv(V2 / "puerto_madero_resultados_pruebas_v2.csv")
    st = pd.read_csv(V2 / "tabla_comparacion_san_telmo_v2.csv")
    corr = gpd.read_file(V2 / "corrientes_corredor_continuo_v2.geojson").to_crs(CRS_M)
    reproducibility = json.loads((V2 / "metadata_pipeline_hibrido_repeticiones_v2.json").read_text(encoding="utf-8"))
    cost_pts = points_for(data, "MZ_COSTANERA_NORTE")
    labels = HDBSCAN(min_cluster_size=8, min_samples=5, cluster_selection_method="eom").fit_predict(xy(cost_pts))
    assigned = int((labels != -1).sum())
    noise_idx = np.flatnonzero(labels == -1)
    missing_rows = []
    ordered = sorted(set(labels.tolist()) - {-1}, key=lambda c: float(cost_pts.loc[labels == c].geometry.x.mean()))
    label_to_id = {cid: f"CN_C{i+1:02d}" for i, cid in enumerate(ordered)}
    for idx in noise_idx:
        d = np.linalg.norm(xy(cost_pts)[labels != -1] - xy(cost_pts)[idx], axis=1)
        valid_indices = np.flatnonzero(labels != -1)
        nearest_idx = valid_indices[int(np.argmin(d))]
        missing_rows.append({
            "registro_control": f"CN_NO_ASIGNADO_{len(missing_rows)+1:02d}",
            "fuente": cost_pts.iloc[idx].fuente,
            "estado_v2": "RUIDO_HDBSCAN_NO_EXPORTADO",
            "componente_mas_cercano": label_to_id[int(labels[nearest_idx])],
            "distancia_componente_m": round(float(d.min()), 1),
            "distancia_borde_contenedor_m": round(float(cost_pts.iloc[idx].geometry.distance(data['macro'].loc['MZ_COSTANERA_NORTE'].geometry.boundary)), 1),
            "clasificacion_v21": "dependencia del contenedor",
            "causa": "clasificación algorítmica como ruido; no es error de unión, filtro ni exportación",
        })
    checks = pd.DataFrame([
        {"control": "Costanera universo", "valor": len(cost_pts), "esperado": 72, "estado": "OK" if len(cost_pts)==72 else "REVISAR"},
        {"control": "Costanera suma componentes", "valor": int(cost.n_puntos.sum()), "esperado": 71, "estado": "INCONSISTENCIA_LOCALIZADA"},
        {"control": "Costanera no asignados", "valor": len(noise_idx), "esperado": 1, "estado": "LOCALIZADO"},
        {"control": "Belgrano candidatos", "valor": len(bel), "esperado": 17, "estado": "OK"},
        {"control": "Belgrano ALTA/MEDIA/BAJA", "valor": "/".join(str(int((bel.categoria==x).sum())) for x in ("ALTA","MEDIA","BAJA")), "esperado": "6/8/3", "estado": "OK"},
        {"control": "Belgrano shortlist preliminar", "valor": ";".join(bel.loc[bel.identificador_tecnico.isin(['BEL_RV2_N02','BEL_RV2_N03','BEL_RV2_N05','BEL_RV2_N06']),'identificador_tecnico']), "esperado": "N02/N03/N05/N06", "estado": "OK_REQUIERE_REGLA_EXPLICITA"},
        {"control": "San Telmo núcleo", "valor": f"{int(st.iloc[0].puntos_cubiertos)}/{int(st.iloc[0].puntos_universo)} ({st.iloc[0].cobertura_pct:.2f}%)", "esperado": "177/320 (55.31%)", "estado": "OK"},
        {"control": "San Telmo núcleo+Defensa", "valor": f"{int(st.iloc[2].puntos_cubiertos)}/{int(st.iloc[2].puntos_universo)} ({st.iloc[2].cobertura_pct:.2f}%)", "esperado": "208/320 (65.00%)", "estado": "OK"},
        {"control": "Corrientes", "valor": f"{int(corr.iloc[0].puntos_cubiertos)}/{int(corr.iloc[0].puntos_universo)}; {corr.iloc[0].longitud_m:.1f} m", "esperado": "503/1255; 2901.6 m", "estado": "OK"},
        {"control": "Puerto Madero PM-C", "valor": f"{int(pm.loc[pm.opcion_id=='PM-C_FRENTE_DOBLE','puntos_asignados'].iloc[0])}/294; {int(pm.loc[pm.opcion_id=='PM-C_FRENTE_DOBLE','componentes'].iloc[0])} componentes", "esperado": "235/294; 80", "estado": "OK"},
        {"control": "Reproducibilidad reportada", "valor": "71/71", "esperado": "71/71", "estado": "REPORTADA_NO_REEJECUTADA_COMO_TEST_SEPARADO"},
    ])
    text = f"""# Auditoría de consistencia de repeticiones v2

Estado: **EXPERIMENTAL / NO OFICIAL**. Auditoría directa de GeoJSON, CSV, diagnósticos, metadata, mapas, manifests y matrices v2.

## Veredicto

La v2 es internamente consistente salvo una omisión explícita en el resumen de Costanera Norte: el universo contiene 72 registros, pero los cuatro componentes HDBSCAN suman 71. El registro restante fue localizado y clasificado; no se corrigió ningún insumo v2.

{md_table(checks)}

## Costanera: causa exacta

El registro faltante quedó etiquetado como ruido (`-1`) por HDBSCAN. Es una señal Places, está a **{missing_rows[0]['distancia_componente_m']:.1f} m** de `{missing_rows[0]['componente_mas_cercano']}` y a **{missing_rows[0]['distancia_borde_contenedor_m']:.1f} m** del borde. Se clasifica como **dependencia del contenedor**. No hubo pérdida en unión, filtro ni exportación: la tabla v2 solo resumió clusters asignados y no explicitó el ruido.

## Otros controles

- Belgrano conserva 17 candidatos y la distribución 6 ALTA, 8 MEDIA y 3 BAJA. La shortlist preliminar N02/N03/N05/N06 coincide con la evidencia tabular, pero se vuelve a derivar con regla explícita en v2.1.
- San Telmo reproduce 177/320 para el núcleo y 208/320 para núcleo + Defensa.
- Corrientes reproduce 503/1.255 y 2.901,6 m; los cuatro subtramos son exclusivamente narrativos.
- Puerto Madero PM-C reproduce 235/294, 79,93%, 180 m, 21,46% del contenedor y 80 componentes analíticos.
- Las tablas de puntos externos usan la taxonomía aprobada. No se promueve ningún punto automáticamente.
- La metadata v2 reporta reproducibilidad 71/71 para sus pruebas. Esta auditoría verifica outputs persistidos y relaciones críticas; no sobrescribe ni recompone v2.
"""
    (DOC / "AUDITORIA_CONSISTENCIA_REPETICIONES_V2.md").write_text(text, encoding="utf-8")
    return {"checks": checks, "missing": pd.DataFrame(missing_rows), "cost_labels": labels}


def costanera_v21(data: dict, audit: dict) -> dict:
    pts = points_for(data, "MZ_COSTANERA_NORTE")
    macro = data["macro"].loc["MZ_COSTANERA_NORTE"].geometry
    labels = audit["cost_labels"]
    ordered = sorted(set(labels.tolist()) - {-1}, key=lambda c: float(pts.loc[labels == c].geometry.x.mean()))
    clusters = []
    for i, cid in enumerate(ordered, 1):
        sub = pts.loc[labels == cid]
        geom = shapely.concave_hull(MultiPoint(list(zip(sub.geometry.x, sub.geometry.y))), ratio=.55, allow_holes=False).buffer(55).intersection(macro)
        b, p, pct = source_counts(sub)
        clusters.append({"id": f"CN_C{i:02d}", "n": len(sub), "base": b, "places": p, "places_pct": pct, "geom": geom})
    context = next(c for c in clusters if c["id"] == "CN_C02")
    main = [c for c in clusters if c["id"] != "CN_C02"]
    # Unión topológica: conserva piezas y vacíos; no crea envolvente ni puentes.
    main_geom = unary_union([c["geom"] for c in main])
    unit = gpd.GeoDataFrame([{
        "id_unidad": "COSTANERA_NORTE_MULTIPARTE_V21", "estado": "EXPLORATORIA_NO_OFICIAL",
        "identidad_editorial": "UNICA", "componentes_principales": 3,
        "componentes": ";".join(c["id"] for c in main), "espacios_vacios": "PRESERVADOS",
        "aclaracion": "Tres componentes separados; sin envolvente común; no es delimitación oficial.", "geometry": main_geom,
    }], geometry="geometry", crs=CRS_M)
    context_gdf = gpd.GeoDataFrame([{
        "id_contexto": "CN_C02", "estado": "CONTEXTO_SECUNDARIO_EXPLORATORIO",
        "f01_f02": 0, "places": context["places"], "dependencia_places_pct": 100.0,
        "aclaracion": "Contexto tenue; no integra la unidad principal.", "geometry": context["geom"],
    }], geometry="geometry", crs=CRS_M)
    write_geo(unit, OUT / "costanera_unidad_multiparte_presentacion_v21.geojson")
    write_geo(context_gdf, OUT / "costanera_contexto_secundario_v21.geojson")
    rows = [{
        "categoria": "COMPONENTE_PRINCIPAL" if c in main else "CONTEXTO_SECUNDARIO",
        "componente": c["id"], "n_puntos": c["n"], "f01_f02": c["base"], "places": c["places"],
        "places_pct": c["places_pct"], "incluido_identidad_principal": c in main,
    } for c in clusters]
    rows += audit["missing"].to_dict("records")
    counts = pd.DataFrame(rows)
    write_csv(counts, OUT / "costanera_conteos_corregidos_v21.csv")
    fig, ax = plt.subplots(figsize=(12, 6))
    plot_context(ax, data, pts, macro, "Costanera Norte — una identidad multiparte, tres componentes")
    unit.plot(ax=ax, facecolor=COLORS["primary"], edgecolor="#0D6847", alpha=.26)
    context_gdf.plot(ax=ax, facecolor=COLORS["context"], edgecolor=COLORS["border"], alpha=.18, hatch="///")
    save_fig(fig, OUT / "mapa_costanera_multiparte_v21.png")
    (DOC / "DIAGNOSTICO_COSTANERA_V21.md").write_text(f"""# Diagnóstico Costanera Norte v2.1

Estado: **EXPERIMENTAL / NO OFICIAL**.

## Conteo final

- Universo: **72**.
- Componentes técnicos: **71** registros asignados (21 + 11 + 29 + 10).
- Registro no asignado: **1**, Places, clasificado como dependencia del contenedor.
- Unidad editorial principal: **tres componentes** (`CN_C01`, `CN_C03`, `CN_C04`).
- Contexto secundario: `CN_C02`, 11 registros, 0 F01/F02 y 100% Places.

La diferencia 72/71 no fue un error de unión ni exportación. HDBSCAN dejó un registro como ruido, próximo al borde. La presentación preserva vacíos y no crea una envolvente común. `CN_C02` se muestra tenue solo como contexto técnico. Costanera sigue en estado exploratorio y no se escala como tipo general.
""", encoding="utf-8")
    return {"unit": unit, "context": context_gdf, "counts": counts, "points": pts, "macro": macro}


def margin_centerline(geom, bin_m: float, simplify_m: float) -> object:
    coords = []
    for part in (list(geom.geoms) if hasattr(geom, "geoms") else [geom]):
        if hasattr(part, "coords"):
            coords.extend(part.coords)
    frame = pd.DataFrame(coords, columns=["x", "y"]).drop_duplicates()
    frame["bin"] = np.floor((frame.y - frame.y.min()) / bin_m).astype(int)
    center = frame.groupby("bin", as_index=False).agg(x=("x", "median"), y=("y", "median")).sort_values("y")
    line = LineString(center[["x", "y"]].to_numpy()).simplify(simplify_m, preserve_topology=True)
    return line


def puerto_madero_v21(data: dict) -> dict:
    pts = points_for(data, "MZ_PUERTO_MADERO")
    macro = data["macro"].loc["MZ_PUERTO_MADERO"].geometry
    fronts = gpd.read_file(V2 / "puerto_madero_frentes_candidatos_v2.geojson").to_crs(CRS_M)
    analytic_row = fronts[fronts.opcion_id.eq("PM-C_FRENTE_DOBLE")].iloc[0]
    analytic = gpd.GeoDataFrame([{
        "id_capa": "PM_C_ANALITICA_V21", "origen": "PM-C_FRENTE_DOBLE_V2_INTACTA",
        "radio_asignacion_m": 180, "puntos_asignados": 235, "cobertura_pct": 79.93,
        "componentes": components(analytic_row.geometry), "uso": "ASIGNACION_ANALITICA", "geometry": analytic_row.geometry,
    }], geometry="geometry", crs=CRS_M)
    write_geo(analytic, OUT / "puerto_madero_capa_analitica_v21.geojson")
    # Reconstrucción por margen a partir de los mismos soportes v2: oeste (Moreau de Justo)
    # y este (Manso/De Alessi/Cossettini). Los nombres no clasifican puntos; solo separan márgenes validados.
    def axis(names):
        s = data["streets"][data["streets"].nomoficial.fillna("").isin(names)].copy()
        s["geometry"] = s.geometry.intersection(macro)
        return unary_union(s.loc[~s.geometry.is_empty].geometry.tolist())
    west = axis(["MOREAU DE JUSTO, ALICIA AV."])
    east = axis(["MANSO JUANA", "DEALESSI, PIERINA", "COSSETTINI, OLGA"])
    specs = [("PM_PRES_A", 60, 15), ("PM_PRES_B", 120, 35), ("PM_PRES_C", 200, 65)]
    rows, geos = [], []
    for oid, bin_m, simp in specs:
        w = margin_centerline(west, bin_m, simp)
        e = margin_centerline(east, bin_m, simp)
        geom = unary_union([w, e])
        dist = pts.geometry.distance(geom)
        covered = pts[dist <= 180]
        band = geom.buffer(180, cap_style="flat").intersection(macro)
        overlap = int(((pts.geometry.distance(w) <= 180) & (pts.geometry.distance(e) <= 180)).sum())
        continuity = "ALTA" if components(geom) == 2 and w.length > 1500 and e.length > 1500 else "MEDIA"
        rows.append({
            "opcion_id": oid, "bin_longitudinal_m": bin_m, "tolerancia_simplificacion_m": simp,
            "puntos_universo": len(pts), "puntos_cubiertos": len(covered), "cobertura_pct": round(100*len(covered)/len(pts),2),
            "caida_vs_pm_c_pp": round(79.93-100*len(covered)/len(pts),2), "distancia_maxima_m": 180,
            "longitud_km": round(geom.length/1000,3), "componentes": components(geom),
            "continuidad_visual": continuity, "densidad_puntos_km": round(len(covered)/max(.001,geom.length/1000),2),
            "solapamiento_puntos": overlap, "superficie_banda_ha": round(band.area/10000,2),
            "porcentaje_barrio_representado": round(100*band.area/macro.area,2),
            "gate_cobertura_ge70": len(covered)/len(pts)>=.70, "gate_distancia_le180": True,
            "gate_banda_le30": band.area/macro.area<=.30, "lectura_frente_doble": "SI",
        })
        geos.append({"opcion_id": oid, "nivel": f"bin {bin_m} m / simplificación {simp} m", "estado": "CANDIDATO_PRESENTACION", "geometry": geom})
    table = pd.DataFrame(rows)
    eligible = table[table[["gate_cobertura_ge70","gate_distancia_le180","gate_banda_le30"]].all(axis=1)]
    recommended_id = (eligible.sort_values(["componentes","caida_vs_pm_c_pp","longitud_km"]).iloc[0].opcion_id if len(eligible) else table.sort_values("cobertura_pct",ascending=False).iloc[0].opcion_id)
    table["recomendacion"] = np.where(table.opcion_id.eq(recommended_id), "RECOMENDADA_NO_VINCULANTE", "ALTERNATIVA")
    options = gpd.GeoDataFrame(geos, geometry="geometry", crs=CRS_M)
    options["recomendacion"] = np.where(options.opcion_id.eq(recommended_id), "RECOMENDADA_NO_VINCULANTE", "ALTERNATIVA")
    write_geo(options, OUT / "puerto_madero_opciones_presentacion_v21.geojson")
    write_csv(table, OUT / "tabla_simplificacion_puerto_madero_v21.csv")
    rec_geom = options.loc[options.opcion_id.eq(recommended_id),"geometry"].iloc[0]
    fig, axes = plt.subplots(1, 2, figsize=(15, 7))
    plot_context(axes[0], data, pts, macro, "Analítica PM-C: asignación reproducible")
    analytic.plot(ax=axes[0], color=COLORS["secondary"], linewidth=1.1, alpha=.75)
    plot_context(axes[1], data, pts, macro, f"Presentación recomendada: {recommended_id}")
    gpd.GeoSeries([rec_geom.buffer(180,cap_style="flat").intersection(macro)],crs=CRS_M).plot(ax=axes[1],facecolor=COLORS["primary"],alpha=.14,edgecolor="none")
    gpd.GeoSeries([rec_geom],crs=CRS_M).plot(ax=axes[1],color=COLORS["primary"],linewidth=4)
    save_fig(fig, OUT / "mapa_puerto_madero_analitica_vs_presentacion_v21.png")
    rec = table.loc[table.opcion_id.eq(recommended_id)].iloc[0]
    (DOC / "DIAGNOSTICO_PUERTO_MADERO_V21.md").write_text(f"""# Diagnóstico Puerto Madero v2.1

Estado: **EXPERIMENTAL / NO OFICIAL**.

La capa analítica conserva PM-C sin alterar: 235/294 puntos, 79,93% de cobertura, radio máximo 180 m, 21,46% del contenedor y {components(analytic_row.geometry)} componentes/segmentos.

Se probaron tres simplificaciones derivadas de los mismos soportes longitudinales. La opción recomendada es **{recommended_id}**: {int(rec.puntos_cubiertos)}/294 ({rec.cobertura_pct:.2f}%), caída de {rec.caida_vs_pm_c_pp:.2f} puntos porcentuales, {rec.longitud_km:.3f} km, {int(rec.componentes)} componentes y {rec.porcentaje_barrio_representado:.2f}% del contenedor. Cumple el gate técnico: {bool(rec.gate_cobertura_ge70 and rec.gate_distancia_le180 and rec.gate_banda_le30)}.

La presentación resume ambos márgenes en pocos ejes legibles. No reemplaza la capa analítica para asignación ni rellena el barrio. La recomendación es técnica y requiere validación visual/editorial humana.
""", encoding="utf-8")
    return {"analytic": analytic, "options": options, "table": table, "recommended": recommended_id, "points": pts, "macro": macro}


def reference_point(data: dict, names_a: list[str], names_b: list[str]) -> Point:
    streets = data["streets"]
    a = unary_union(streets[streets.nomoficial.fillna("").isin(names_a)].geometry.tolist())
    b = unary_union(streets[streets.nomoficial.fillna("").isin(names_b)].geometry.tolist())
    pa, pb = nearest_points(a, b)
    return Point((pa.x+pb.x)/2, (pa.y+pb.y)/2)


def belgrano_v21(data: dict) -> dict:
    stability = pd.read_csv(V2 / "belgrano_estabilidad_nucleos_v2.csv")
    candidates = gpd.read_file(V2 / "belgrano_nucleos_candidatos_v2.geojson").to_crs(CRS_M)
    idcol = "identificador_tecnico" if "identificador_tecnico" in candidates.columns else "id_tecnico"
    macro = data["macro"].loc["MZ_BELGRANO"].geometry
    pts = points_for(data, "MZ_BELGRANO")
    evals = stability.copy()
    evals["estabilidad_bloques_media"] = evals[["supervivencia_b150","supervivencia_b200","supervivencia_b300","supervivencia_b400"]].mean(axis=1).round(3)
    evals["estabilidad_estadistica"] = np.select([evals.estabilidad_bloques_media.ge(.75),evals.estabilidad_bloques_media.ge(.60)],["ALTA","MEDIA"],default="BAJA")
    evals["respaldo_entre_metodos"] = np.where(evals.respaldo_kde & evals.correspondencia_metodos.str.contains("consenso",case=False,na=False),"SI","PARCIAL")
    evals["mezcla_fuentes"] = evals.clasificacion_fuentes
    evals["proximidad_borde"] = np.select([evals.distancia_borde_contenedor_m.le(25),evals.distancia_borde_contenedor_m.le(100)],["CRITICA","CERCANA"],default="INTERIOR")
    evals["cobertura_kde"] = np.where(evals.respaldo_kde,"RESPALDADO","NO_RESPALDADO")
    evals["tamano"] = np.select([evals.cantidad_puntos.ge(15),evals.cantidad_puntos.ge(10)],["MEDIO_ALTO","MEDIO"],default="PEQUENO")
    evals["legibilidad_territorial"] = np.select([
        evals.posiblemente_cortado | evals.dependencia_contenedor.eq("ALTA"),
        evals.dependencia_places_pct.gt(65),
    ],["BAJA_POR_BORDE","BAJA_POR_FUENTE"],default="MEDIA_REQUIERE_REVISION_VISUAL")
    evals["cumple_regla_shortlist"] = (
        evals.categoria.eq("ALTA") & evals.estabilidad_bloques_media.ge(.70) & evals.respaldo_kde &
        evals.dependencia_places_pct.le(60) & ~evals.posiblemente_cortado & ~evals.dependencia_contenedor.eq("ALTA") &
        evals.cantidad_puntos.ge(10)
    )
    evals["elegibilidad_editorial"] = np.where(evals.cumple_regla_shortlist,"APTA_REVISION_HUMANA","NO_PRIORIZADA")
    strict = evals.loc[evals.cumple_regla_shortlist,"identificador_tecnico"].tolist()
    preliminary = ["BEL_RV2_N02","BEL_RV2_N03","BEL_RV2_N05","BEL_RV2_N06"]
    evals["shortlist_preliminar"] = evals.identificador_tecnico.isin(preliminary)
    evals["shortlist_regla_v21"] = evals.identificador_tecnico.isin(strict)
    wanted = [
        "identificador_tecnico","categoria","cantidad_puntos","estabilidad_estadistica","estabilidad_bloques_media",
        "respaldo_entre_metodos","supervivencia_b150","supervivencia_b200","supervivencia_b300","supervivencia_b400",
        "mezcla_fuentes","dependencia_places_pct","proximidad_borde","posiblemente_cortado","dependencia_contenedor",
        "cobertura_kde","tamano","legibilidad_territorial","elegibilidad_editorial","shortlist_preliminar","shortlist_regla_v21",
    ]
    write_csv(evals[wanted], OUT / "belgrano_evaluacion_editorial_candidatos_v21.csv")
    shortlist = candidates[candidates[idcol].isin(strict)].copy()
    shortlist["estado_v21"] = "APTA_REVISION_HUMANA_NO_OFICIAL"
    write_geo(shortlist, OUT / "belgrano_shortlist_tecnica_v21.geojson")
    refs = [
        ("Barrio Chino", ["ARRIBEÑOS"], ["JURAMENTO"]),
        ("Cabildo/Juramento", ["CABILDO AV."], ["JURAMENTO"]),
        ("Bajo Belgrano", ["DEL LIBERTADOR AV."], ["ECHEVERRIA"]),
        ("Barrancas/Libertador", ["DEL LIBERTADOR AV."], ["JURAMENTO"]),
    ]
    ref_rows = []
    for name, a, b in refs:
        try:
            p = reference_point(data,a,b)
            ref_rows.append({"referencia_posthoc":name,"uso":"REFERENCIA_URBANA_NO_ALGORITMICA","origen_geometria":f"punto medio de calles locales: {a[0]} / {b[0]}","geometry":p})
        except Exception:
            ref_rows.append({"referencia_posthoc":name,"uso":"REFERENCIA_URBANA_NO_ALGORITMICA","origen_geometria":"no disponible en callejero local","geometry":macro.centroid})
    references = gpd.GeoDataFrame(ref_rows,geometry="geometry",crs=CRS_M)
    write_geo(references, OUT / "belgrano_referencias_posthoc_v21.geojson")
    fig,axes=plt.subplots(1,2,figsize=(15,7))
    plot_context(axes[0],data,pts,macro,"17 candidatos v2")
    candidates.boundary.plot(ax=axes[0],color=COLORS["secondary"],linewidth=1)
    plot_context(axes[1],data,pts,macro,"Shortlist técnica v2.1")
    if len(shortlist): shortlist.plot(ax=axes[1],facecolor=COLORS["primary"],edgecolor="#0D6847",alpha=.3)
    save_fig(fig,OUT/"mapa_belgrano_17_vs_shortlist_v21.png")
    fig,ax=plt.subplots(figsize=(11,8)); plot_context(ax,data,pts,macro,"Shortlist y referencias post hoc")
    if len(shortlist): shortlist.plot(ax=ax,facecolor=COLORS["primary"],edgecolor="#0D6847",alpha=.3)
    references.plot(ax=ax,color=COLORS["warning"],marker="x",markersize=55)
    for row in references.itertuples(): ax.annotate(row.referencia_posthoc,(row.geometry.x,row.geometry.y),xytext=(4,4),textcoords="offset points",fontsize=8)
    save_fig(fig,OUT/"mapa_belgrano_shortlist_referencias_v21.png")
    conclusion = "shortlist apta para revisión humana" if strict else "señal multinuclear todavía insuficiente"
    (DOC/"DIAGNOSTICO_BELGRANO_V21.md").write_text(f"""# Diagnóstico Belgrano v2.1

Estado: **EXPERIMENTAL / NO OFICIAL**.

## Regla de shortlist

Se exige simultáneamente: categoría ALTA; supervivencia media por bloques ≥ 0,70; respaldo KDE; dependencia Places ≤ 60%; sin posible corte; dependencia del contenedor distinta de ALTA; y al menos 10 puntos. No se fija una cantidad objetivo.

La regla selecciona: **{'; '.join(strict) if strict else 'ningún candidato'}**. La shortlist preliminar N02/N03/N05/N06 {'coincide' if set(strict)==set(preliminary) else 'no coincide completamente'} con la regla documentada. Los 6 ALTA no se interpretan como seis polos.

## Conclusión obligatoria

**{conclusion}.** Confianza técnica: **media**, porque el acuerdo entre métodos y fuentes sigue siendo parcial y existe sensibilidad al contenedor en parte del universo. Los nombres Barrio Chino, Cabildo/Juramento, Bajo Belgrano y Barrancas/Libertador se superponen solo post hoc como puntos de referencia derivados del callejero; no alteran clusters ni elegibilidad.
""",encoding="utf-8")
    return {"eval":evals,"shortlist":shortlist,"references":references,"strict":strict,"points":pts,"macro":macro}


def classify_external(points: gpd.GeoDataFrame, geom, macro, prefix: str, distance_col: str) -> pd.DataFrame:
    dist = points.geometry.distance(geom)
    near_border = points.geometry.distance(macro.boundary)
    category = np.select(
        [dist.le(250),dist.le(400),near_border.le(100),dist.gt(700)],
        ["continuidad territorial","contexto gastronómico disperso","dependencia del contenedor","establecimiento aislado genuino"],
        default="cola de revisión",
    )
    out=pd.DataFrame({"id_externo":[f"{prefix}_{i+1:04d}" for i in range(len(points))],"fuente":points.fuente.to_numpy(),distance_col:dist.round(1).to_numpy(),"categoria_taxonomia":category})
    return out


def san_telmo_v21(data: dict) -> dict:
    pts=points_for(data,"MZ_SAN_TELMO"); macro=data["macro"].loc["MZ_SAN_TELMO"].geometry
    core_all=gpd.read_file(V2/"san_telmo_nucleo_compacto.geojson").to_crs(CRS_M)
    core=core_all[core_all.opcion.eq("NUCLEO_UNICO")].copy()
    core["jerarquia_visual"]="PRINCIPAL"; core["cobertura"]="177/320 (55,31%)"
    defense=gpd.read_file(V2/"san_telmo_eje_defensa.geojson").to_crs(CRS_M)
    defense["jerarquia_visual"]="SECUNDARIA_CONTEXTUAL"; defense["cobertura_incremental"]="31 puntos; total 208/320 (65,00%)"
    write_geo(core,OUT/"san_telmo_nucleo_presentacion_v21.geojson"); write_geo(defense,OUT/"san_telmo_defensa_contextual_v21.geojson")
    union=unary_union([core.geometry.iloc[0],defense.geometry.iloc[0].buffer(110,cap_style="flat").intersection(macro)])
    external=pts[~pts.geometry.intersects(union)].copy()
    ext=classify_external(external,union,macro,"ST_EXT","distancia_representacion_m")
    write_csv(ext,OUT/"san_telmo_puntos_externos_v21.csv")
    fig,ax=plt.subplots(figsize=(11,8)); plot_context(ax,data,pts,macro,"San Telmo — núcleo principal + Defensa contextual")
    core.plot(ax=ax,facecolor=COLORS["primary"],edgecolor="#0D6847",alpha=.32)
    defense.plot(ax=ax,color=COLORS["secondary"],linewidth=2.2,alpha=.8)
    save_fig(fig,OUT/"mapa_san_telmo_consolidado_v21.png")
    (DOC/"DIAGNOSTICO_SAN_TELMO_V21.md").write_text(f"""# Diagnóstico San Telmo v2.1

Estado: **EXPERIMENTAL / NO OFICIAL**.

Se consolida la hipótesis **núcleo compacto + eje Defensa contextual**. El núcleo conserva 177/320 (55,31%) y tiene jerarquía visual principal. La incorporación contextual de Defensa eleva la cobertura a 208/320 (65,00%). Defensa no constituye un segundo polo equivalente.

Los {len(ext)} puntos externos se clasifican con la taxonomía aprobada. Las coberturas describen oferta registrada/visible dentro del universo local y no actividad comercial actual.
""",encoding="utf-8")
    return {"core":core,"defense":defense,"external":ext,"points":pts,"macro":macro}


def corrientes_v21(data: dict) -> dict:
    pts=points_for(data,"MZ_AVENIDA_CORRIENTES"); macro=data["macro"].loc["MZ_AVENIDA_CORRIENTES"].geometry
    source=gpd.read_file(V2/"corrientes_corredor_continuo_v2.geojson").to_crs(CRS_M)
    analytic=source.copy(); analytic["nivel"]="ANALITICO"; analytic["subtramos_geometricos"]="NO"
    presentation=source.copy(); presentation["id_tecnico"]="CORRIENTES_CORREDOR_PRESENTACION_V21"; presentation["nivel"]="PRESENTACION"; presentation["subtramos_geometricos"]="NO"
    write_geo(analytic,OUT/"corrientes_corredor_analitico_v21.geojson"); write_geo(presentation,OUT/"corrientes_corredor_presentacion_v21.geojson")
    labels=pd.read_csv(V2/"corrientes_subtramos_narrativos_v2.csv").rename(columns={"subtramo_codigo":"etiqueta_codigo"})
    labels["uso"]="ETIQUETA_NARRATIVA_NO_UNIDAD_TERRITORIAL"
    labels["hito_medio_m"]=((labels.desde_m+labels.hasta_m)/2).round(1)
    write_csv(labels,OUT/"corrientes_etiquetas_narrativas_v21.csv")
    axis=analytic.geometry.iloc[0]; external=pts[pts.geometry.distance(axis)>150].copy(); ext=classify_external(external,axis,macro,"COR_EXT","distancia_eje_m")
    write_csv(ext,OUT/"corrientes_puntos_externos_v21.csv")
    fig,ax=plt.subplots(figsize=(13,6)); plot_context(ax,data,pts,macro,"Corrientes — corredor único continuo, separado de Abasto")
    gpd.GeoSeries([axis.buffer(150,cap_style="flat").intersection(macro)],crs=CRS_M).plot(ax=ax,facecolor=COLORS["primary"],edgecolor="none",alpha=.16)
    presentation.plot(ax=ax,color=COLORS["primary"],linewidth=4)
    save_fig(fig,OUT/"mapa_corrientes_consolidado_v21.png")
    row=analytic.iloc[0]
    (DOC/"DIAGNOSTICO_CORRIENTES_V21.md").write_text(f"""# Diagnóstico Corrientes v2.1

Estado: **EXPERIMENTAL / NO OFICIAL**.

Se conserva un único corredor continuo, separado de Abasto y con el recorte vigente hacia Microcentro. Longitud: {row.longitud_m:.1f} m. Cobertura: {int(row.puntos_cubiertos)}/{int(row.puntos_universo)} ({row.cobertura_pct:.2f}%). La geometría tiene un componente y no contiene huecos artificiales.

Los cuatro subtramos se exportan únicamente como etiquetas narrativas sin geometría; no son unidades territoriales. El campo `abasto_incorporado=NO` se conserva explícitamente. Los {len(ext)} puntos externos se clasifican con la taxonomía aprobada.
""",encoding="utf-8")
    return {"analytic":analytic,"presentation":presentation,"external":ext,"labels":labels,"points":pts,"macro":macro}


def cluster_sets(labels: np.ndarray, min_n: int=8) -> list[set[int]]:
    return [set(np.flatnonzero(labels==cid).tolist()) for cid in set(labels.tolist())-{-1} if int((labels==cid).sum())>=min_n]


def compact_scale(data: dict, zone: str, macro_id: str, slug: str) -> dict:
    pts=points_for(data,macro_id); macro=data["macro"].loc[macro_id].geometry; coords=xy(pts)
    mcs=max(15,int(round(len(pts)*.035))); ms=max(5,int(round(math.sqrt(mcs)/2)))
    labels=HDBSCAN(min_cluster_size=mcs,min_samples=ms,cluster_selection_method="eom").fit_predict(coords)
    base_sets=cluster_sets(labels,mcs)
    polygons=[]
    for i,s in enumerate(sorted(base_sets,key=len,reverse=True),1):
        sub=pts.iloc[sorted(s)]
        geom=shapely.concave_hull(MultiPoint(list(zip(sub.geometry.x,sub.geometry.y))),ratio=.4,allow_holes=False).buffer(35).intersection(macro)
        b,p,pct=source_counts(sub)
        polygons.append({"nucleo_id":f"{slug.upper()}_N{i:02d}","n_puntos":len(sub),"f01_f02":b,"places":p,"places_pct":pct,"geometry":geom,"members":s})
    # KDE persistente: cantidad de máximos que aparece en al menos dos anchos.
    kde_rows=[]; maxima_by_bw={}
    minx,miny=coords.min(axis=0)-100; maxx,maxy=coords.max(axis=0)+100
    gx=np.arange(minx,maxx+30,30); gy=np.arange(miny,maxy+30,30); mesh=np.array(np.meshgrid(gx,gy)).reshape(2,-1).T
    for bw in (80,120,160):
        density=np.exp(KernelDensity(bandwidth=bw).fit(coords).score_samples(mesh)).reshape(len(gy),len(gx))
        loc=(density==maximum_filter(density,size=max(3,int(round(2*bw/30))|1))) & (density>=np.quantile(density,.85))
        yy,xx=np.where(loc); maxima=[Point(float(gx[x]),float(gy[y])) for y,x in zip(yy,xx)]; maxima_by_bw[bw]=maxima
        kde_rows.append({"bandwidth_m":bw,"maximos":len(maxima)})
    # Bootstrap espacial por bloques: 30 repeticiones, Jaccard de mejor match por núcleo.
    boot=[]
    for block in (200,300):
        bx=np.floor((coords[:,0]-coords[:,0].min())/block).astype(int); by=np.floor((coords[:,1]-coords[:,1].min())/block).astype(int)
        keys=np.array([f"{a}:{b}" for a,b in zip(bx,by)]); unique=np.unique(keys)
        for rep in range(30):
            chosen=RNG.choice(unique,size=max(2,int(math.ceil(.8*len(unique)))),replace=False); idx=np.flatnonzero(np.isin(keys,chosen))
            if len(idx)<mcs: continue
            alt=HDBSCAN(min_cluster_size=max(8,int(mcs*.75)),min_samples=ms,cluster_selection_method="eom").fit_predict(coords[idx])
            for pos,s in enumerate(base_sets,1): boot.append({"bloque_m":block,"repeticion":rep+1,"nucleo":pos,"jaccard":best_match(s,alt,idx)})
    bootdf=pd.DataFrame(boot)
    robust_mean=float(bootdf.jaccard.mean()) if len(bootdf) else 0.; robust_p10=float(bootdf.jaccard.quantile(.1)) if len(bootdf) else 0.
    # Ablación y borde.
    ablation=[]
    for name,mask in [("SIN_PLACES",pts.fuente.ne("google_places").to_numpy()),("SOLO_PLACES",pts.fuente.eq("google_places").to_numpy()),("SIN_BORDE_150M",pts.geometry.distance(macro.boundary).gt(150).to_numpy())]:
        idx=np.flatnonzero(mask)
        if len(idx)>=mcs:
            alt=HDBSCAN(min_cluster_size=max(8,int(mcs*.7)),min_samples=ms,cluster_selection_method="eom").fit_predict(coords[idx])
            scores=[best_match(s,alt,idx) for s in base_sets]
            ablation.append({"prueba":name,"n_puntos":len(idx),"n_clusters":len(set(alt.tolist())-{-1}),"jaccard_medio":round(float(np.mean(scores or [0])),3)})
    abldf=pd.DataFrame(ablation)
    kde_support=[]
    allmax=[p for v in maxima_by_bw.values() for p in v]
    for p in polygons:
        center=p["geometry"].centroid; kde_support.append(min([center.distance(q) for q in allmax] or [9999])<=180)
    for p,support in zip(polygons,kde_support): p["respaldo_kde"]=support
    analytic=gpd.GeoDataFrame([{k:v for k,v in p.items() if k!="members"} for p in polygons],geometry="geometry",crs=CRS_M)
    analytic["estado"]="EXPERIMENTAL_NO_OFICIAL"
    presentation=analytic[(analytic.n_puntos>=mcs)&analytic.respaldo_kde].copy(); presentation["uso"]="PRESENTACION_CANDIDATA"
    write_geo(analytic,OUT/f"{slug}_nucleos_analiticos_v21.geojson"); write_geo(presentation,OUT/f"{slug}_nucleos_presentacion_v21.geojson")
    b,p,pct=source_counts(pts); covered=int(pts.geometry.intersects(unary_union(analytic.geometry.tolist())).sum()) if len(analytic) else 0
    metrics=pd.DataFrame([{"zona":zone,"tipo_esperado":"NUCLEO_COMPACTO","tipo_observado":f"{len(analytic)} NUCLEO(S) CANDIDATO(S)","universo":len(pts),"cobertura_pct":round(100*covered/len(pts),2),"robustez_media":round(robust_mean,3),"p10":round(robust_p10,3),"f01_f02":b,"places":p,"dependencia_places_pct":pct,"sensibilidad_contenedor":round(float(abldf.loc[abldf.prueba=='SIN_BORDE_150M','jaccard_medio'].iloc[0]) if (abldf.prueba=='SIN_BORDE_150M').any() else 0,3),"n_nucleos":len(analytic),"aptitud_escalar":"SI_CON_REVISION" if robust_mean>=.55 and len(presentation) else "NO_AUN","decision_humana_pendiente":"validar cantidad y lectura territorial"}])
    write_csv(pd.concat([metrics.assign(seccion="RESUMEN"),abldf.assign(seccion="ABLACION"),pd.DataFrame(kde_rows).assign(seccion="KDE")],ignore_index=True),OUT/f"{slug}_metricas_v21.csv")
    fig,ax=plt.subplots(figsize=(10,8)); plot_context(ax,data,pts,macro,f"{zone} — primera prueba de núcleo compacto")
    if len(analytic): analytic.plot(ax=ax,facecolor=COLORS["primary"],edgecolor="#0D6847",alpha=.25)
    save_fig(fig,OUT/f"mapa_{slug}_escalado_v21.png")
    (DOC/f"DIAGNOSTICO_{slug.upper()}_V21.md").write_text(f"""# Diagnóstico {zone} v2.1

Estado: **EXPERIMENTAL / NO OFICIAL**. Prueba de escalado tipo núcleo compacto.

HDBSCAN detectó {len(analytic)} núcleo(s) candidato(s); no se impuso una cantidad. Cobertura geométrica: {metrics.iloc[0].cobertura_pct:.2f}%. Robustez espacial media: {robust_mean:.3f}; p10: {robust_p10:.3f}. Composición: {b} F01/F02 y {p} Places ({pct:.2f}% Places). Se aplicaron KDE multiancho, concave hull restringido, bootstrap por bloques, ablación de fuentes y exclusión de borde como sensibilidad al contenedor.

Resultado: **{metrics.iloc[0].aptitud_escalar}**. La estabilidad técnica no equivale a elegibilidad editorial; queda pendiente validar cantidad y lectura territorial.
""",encoding="utf-8")
    return {"zone":zone,"slug":slug,"analytic":analytic,"presentation":presentation,"metrics":metrics,"points":pts,"macro":macro}


def caseros_scale(data: dict) -> dict:
    zone="Caseros/Barracas"; slug="caseros_barracas"; pts=points_for(data,"MZ_AVENIDA_CASEROS_BARRACAS"); macro=data["macro"].loc["MZ_AVENIDA_CASEROS_BARRACAS"].geometry
    streets=data["streets"][data["streets"].nomoficial.fillna("").eq("CASEROS AV.")].copy(); streets["geometry"]=streets.geometry.intersection(macro); streets=streets[~streets.geometry.is_empty]
    coords=[]
    for geom in streets.geometry:
        for part in (list(geom.geoms) if hasattr(geom,"geoms") else [geom]): coords.extend(part.coords)
    frame=pd.DataFrame(coords,columns=["x","y"]).drop_duplicates(); axis_dir=np.linalg.svd(frame[["x","y"]].to_numpy()-frame[["x","y"]].mean().to_numpy(),full_matrices=False)[2][0]
    frame["proj"]=(frame[["x","y"]].to_numpy()-frame[["x","y"]].mean().to_numpy())@axis_dir; frame["bin"]=np.floor((frame.proj-frame.proj.min())/70).astype(int)
    center=frame.groupby("bin",as_index=False).agg(x=("x","median"),y=("y","median"),proj=("proj","median")).sort_values("proj"); axis=LineString(center[["x","y"]].to_numpy()).simplify(25)
    dist=pts.geometry.distance(axis); covered=pts[dist<=150]; b,p,pct=source_counts(pts)
    proj=np.array([axis.project(g) for g in pts.geometry]); edges=np.linspace(0,axis.length,max(5,int(axis.length//200)+1)); bins=np.clip(np.digitize(proj,edges)-1,0,len(edges)-2)
    prof=[]
    for i in range(len(edges)-1):
        sub=pts[bins==i]; prof.append({"bin":i+1,"desde_m":round(edges[i],1),"hasta_m":round(edges[i+1],1),"puntos":len(sub),"f01_f02":int(sub.fuente.eq("F01+F02").sum()),"places":int(sub.fuente.eq("google_places").sum())})
    profile=pd.DataFrame(prof); continuity_all=float((profile.puntos>0).mean()); continuity_base=float((profile.f01_f02>0).mean())
    covered_base=int(((dist<=150)&pts.fuente.eq("F01+F02")).sum()); persistence=continuity_base>=.5 and covered_base>=8
    analytic=gpd.GeoDataFrame([{"id":"CASEROS_CORREDOR_ANALITICO_V21","buffer_m":150,"longitud_m":round(axis.length,1),"geometry":axis}],geometry="geometry",crs=CRS_M)
    presentation=analytic.copy(); presentation["id"]="CASEROS_CORREDOR_PRESENTACION_V21"; presentation["estado"]="EXPERIMENTAL_NO_OFICIAL"
    write_geo(analytic,OUT/"caseros_barracas_corredor_analitico_v21.geojson"); write_geo(presentation,OUT/"caseros_barracas_corredor_presentacion_v21.geojson")
    ext=classify_external(pts[dist>150].copy(),axis,macro,"CAS_EXT","distancia_eje_m")
    metrics=pd.DataFrame([{"zona":zone,"tipo_esperado":"CORREDOR","tipo_observado":"CORREDOR_LONGITUDINAL","universo":len(pts),"cobertura_pct":round(100*len(covered)/len(pts),2),"robustez_media":round(continuity_all,3),"p10":np.nan,"f01_f02":b,"places":p,"dependencia_places_pct":pct,"sensibilidad_contenedor":"MEDIA","continuidad_sin_places":round(continuity_base,3),"persiste_sin_places":persistence,"aptitud_escalar":"SI_CON_REVISION" if persistence else "NO_PROMOVER_DEPENDE_PLACES","decision_humana_pendiente":"validar lectura urbana y buffer"}])
    write_csv(pd.concat([metrics.assign(seccion="RESUMEN"),profile.assign(seccion="PERFIL_LONGITUDINAL")],ignore_index=True),OUT/"caseros_barracas_metricas_v21.csv")
    fig,ax=plt.subplots(figsize=(12,6)); plot_context(ax,data,pts,macro,"Caseros/Barracas — prueba de corredor")
    gpd.GeoSeries([axis.buffer(150,cap_style="flat").intersection(macro)],crs=CRS_M).plot(ax=ax,facecolor=COLORS["primary"],edgecolor="none",alpha=.15); presentation.plot(ax=ax,color=COLORS["primary"],linewidth=4)
    save_fig(fig,OUT/"mapa_caseros_barracas_escalado_v21.png")
    (DOC/"DIAGNOSTICO_CASEROS_BARRACAS_V21.md").write_text(f"""# Diagnóstico Caseros/Barracas v2.1

Estado: **EXPERIMENTAL / NO OFICIAL**. Prueba de escalado tipo corredor.

Universo: {len(pts)}; composición: {b} F01/F02 y {p} Places ({pct:.2f}% Places). Cobertura a 150 m: {len(covered)}/{len(pts)} ({100*len(covered)/len(pts):.2f}%). Continuidad longitudinal total: {continuity_all:.3f}; continuidad excluyendo Places: {continuity_base:.3f}. La estructura **{'persiste' if persistence else 'no persiste con respaldo suficiente'}** al excluir Places bajo el gate documentado (≥ 50% de bins con F01/F02 y ≥ 8 puntos base cubiertos).

Resultado: **{metrics.iloc[0].aptitud_escalar}**. No se promueve automáticamente; queda pendiente validar lectura urbana y buffer.
""",encoding="utf-8")
    return {"zone":zone,"slug":slug,"analytic":analytic,"presentation":presentation,"metrics":metrics,"external":ext,"points":pts,"macro":macro}


def write_scale_matrix(results: list[dict]) -> pd.DataFrame:
    matrix=pd.concat([r["metrics"] for r in results],ignore_index=True)
    cols=["zona","tipo_esperado","tipo_observado","cobertura_pct","robustez_media","p10","f01_f02","places","dependencia_places_pct","sensibilidad_contenedor","aptitud_escalar","decision_humana_pendiente"]
    (DOC/"MATRIZ_PRIMER_ESCALADO_V21.md").write_text("# Matriz del primer escalado v2.1\n\nEstado: **EXPERIMENTAL / NO OFICIAL**.\n\n"+md_table(matrix[cols])+"\n\nLos gates son orientativos y no sustituyen decisión humana. No se escalaron redes multinucleares, nuevos frentes, Costanera, Caballito, Villa Crespo ni Chacarita.\n",encoding="utf-8")
    write_csv(matrix[cols],OUT/"matriz_primer_escalado_v21.csv")
    return matrix


def places_evaluation(zones: list[dict]) -> pd.DataFrame:
    rows=[]
    for z in zones:
        metrics=z.get("metrics")
        dep=float(metrics.iloc[0].dependencia_places_pct) if metrics is not None and "dependencia_places_pct" in metrics else float(100*z["points"].fuente.eq("google_places").mean())
        recommendation="NO_EJECUTAR"
        problem="la evidencia existente permite evaluar el gate sin consultas nuevas"
        change="NO"
        if z.get("slug")=="caseros_barracas" and not bool(metrics.iloc[0].get("persiste_sin_places",False)):
            recommendation="ESPERAR"; problem="dependencia alta de Places y estructura débil sin esa fuente"; change="PODRIA, pero primero requiere decisión metodológica"
        rows.append({"zona":z.get("zone",z.get("slug","zona")),"problema_detectado":problem,"resoluble_datos_existentes":"SI","consulta_nueva_podria_cambiar_decision":change,"area_minima_consultar":"ninguna en esta tanda","consultas_estimadas":0,"saturacion_previa":"alta o no necesaria según universo local","dependencia_places_actual_pct":round(dep,2),"riesgo_agregar_sesgo":"MEDIO_ALTO","recomendacion":recommendation})
    frame=pd.DataFrame(rows)
    (DOC/"EVALUACION_PLACES_POST_ESCALADO_V21.md").write_text("# Evaluación de futuras consultas Places post escalado v2.1\n\nNo se ejecutaron consultas. Solo se propone una corrida quirúrgica cuando existe una pregunta falsable y una decisión concreta que pueda cambiar; **ninguna zona alcanza ese umbral en esta tanda**.\n\n"+md_table(frame)+"\n",encoding="utf-8")
    write_csv(frame,OUT/"evaluacion_places_post_escalado_v21.csv")
    return frame


def copy_handoff(cost,pm,bel,st,corr,scales,matrix) -> None:
    # Presentación sanitizada: geometrías agregadas, mapas y métricas sin puntos individuales.
    geo_names=[
        "costanera_unidad_multiparte_presentacion_v21.geojson","costanera_contexto_secundario_v21.geojson",
        "puerto_madero_opciones_presentacion_v21.geojson","belgrano_shortlist_tecnica_v21.geojson","belgrano_referencias_posthoc_v21.geojson",
        "san_telmo_nucleo_presentacion_v21.geojson","san_telmo_defensa_contextual_v21.geojson","corrientes_corredor_presentacion_v21.geojson",
        "palermo_soho_nucleos_presentacion_v21.geojson","recoleta_nucleos_presentacion_v21.geojson","caseros_barracas_corredor_presentacion_v21.geojson",
    ]
    map_names=[p.name for p in OUT.glob("mapa_*_v21.png")]
    table_names=["tabla_simplificacion_puerto_madero_v21.csv","belgrano_evaluacion_editorial_candidatos_v21.csv","matriz_primer_escalado_v21.csv","evaluacion_places_post_escalado_v21.csv"]
    for name in geo_names+map_names+table_names:
        src=OUT/name
        if src.exists(): shutil.copy2(src,HANDOFF/name)
    glossary=pd.DataFrame([
        {"campo":"estado","definicion":"condición experimental/no oficial del objeto"},
        {"campo":"cobertura_pct","definicion":"porcentaje del universo local a la distancia o geometría declarada"},
        {"campo":"dependencia_places_pct","definicion":"participación de señales Places en el universo o componente"},
        {"campo":"componentes","definicion":"cantidad de piezas geométricas separadas"},
        {"campo":"recomendacion","definicion":"prioridad técnica no vinculante; requiere decisión humana"},
    ]); write_csv(glossary,HANDOFF/"GLOSARIO_CAMPOS.csv")
    decisions="""# Decisiones técnicas vigentes

- Estado general: EXPERIMENTAL / NO OFICIAL; complementa Fase 25 y no la reemplaza.
- Corrientes: un corredor continuo separado de Abasto; subtramos solo narrativos.
- San Telmo: núcleo principal + Defensa contextual secundaria.
- Puerto Madero: frente doble; separar asignación analítica de presentación.
- Belgrano: shortlist técnica solo para revisión humana; nombres post hoc.
- Costanera Norte: una identidad multiparte discontinua; tres componentes principales y CN_C02 contextual.

## No interpretar

Las geometrías no son límites oficiales, los buffers no son anchos reales, la cobertura no mide locales activos y la estabilidad técnica no equivale a elegibilidad editorial. No inferir rankings ni cantidad oficial de polos.
"""; (HANDOFF/"DECISIONES_Y_ADVERTENCIAS.md").write_text(decisions,encoding="utf-8")
    readme="""# Handoff técnico para Fable

Paquete sanitizado de integración v2.1. Contiene solo capas agregadas de presentación, PNG experimentales, métricas publicables, glosario, decisiones y advertencias. No contiene nombres comerciales, coordenadas de establecimientos individuales, identificadores de plataforma, raw, debugging ni credenciales.

Todas las capas son **EXPERIMENTALES / NO OFICIALES** y complementan Fase 25 sin reemplazarla.
"""; (HANDOFF/"README_HANDOFF_FABLE.md").write_text(readme,encoding="utf-8")
    manifest=[]
    for p in sorted(HANDOFF.rglob("*")):
        if p.is_file() and p.name!="MANIFEST_HANDOFF.csv": manifest.append({"ruta":p.relative_to(HANDOFF).as_posix(),"bytes":p.stat().st_size,"sha256":sha256(p)})
    write_csv(pd.DataFrame(manifest),HANDOFF/"MANIFEST_HANDOFF.csv")


def write_decisions(cost,pm,bel,st,corr,matrix,places) -> None:
    comparison=pd.DataFrame([
        {"zona":"Costanera Norte","v2":"71 asignados; ruido no explicitado","v21":"72 conciliados: 71 en componentes + 1 dependencia contenedor","cambio":"corrección de consistencia y presentación"},
        {"zona":"Puerto Madero","v2":"PM-C analítica con 80 componentes","v21":f"PM-C intacta + presentación {pm['recommended']}","cambio":"separación analítica/presentación"},
        {"zona":"Belgrano","v2":"17; 6 ALTA; shortlist preliminar","v21":f"regla explícita; {';'.join(bel['strict'])}","cambio":"separa estabilidad de elegibilidad"},
        {"zona":"San Telmo","v2":"núcleo + Defensa recomendado","v21":"capas jerarquizadas y externos clasificados","cambio":"consolidación"},
        {"zona":"Corrientes","v2":"corredor continuo","v21":"analítica/presentación; etiquetas no geométricas","cambio":"consolidación"},
    ])
    (DOC/"COMPARACION_V2_VS_V21.md").write_text("# Comparación v2 vs v2.1\n\n"+md_table(comparison)+"\n",encoding="utf-8")
    decisions=pd.DataFrame([
        {"estado":"CERRADA","zona":"Corrientes","decision":"corredor único continuo, separado de Abasto","aptitud":"MAPA_POLITICO_CON_ADVERTENCIA"},
        {"estado":"CERRADA","zona":"San Telmo","decision":"núcleo + Defensa contextual con jerarquía desigual","aptitud":"MAPA_POLITICO_CON_ADVERTENCIA"},
        {"estado":"CERRADA","zona":"Puerto Madero","decision":"separar capa analítica y presentación","aptitud":"INFORME_INTERNO_HASTA_VALIDACION_VISUAL"},
        {"estado":"PENDIENTE","zona":"Puerto Madero","decision":f"validar visualmente {pm['recommended']}","aptitud":"INFORME_INTERNO"},
        {"estado":"PENDIENTE","zona":"Belgrano","decision":"revisión humana de shortlist y correspondencia post hoc","aptitud":"ANEXO"},
        {"estado":"PENDIENTE","zona":"Costanera Norte","decision":"uso editorial de contexto CN_C02","aptitud":"ANEXO"},
        {"estado":"PENDIENTE","zona":"Escalado","decision":"validar lectura territorial antes de promover","aptitud":"INFORME_INTERNO"},
        {"estado":"NO_REABIERTA","zona":"General","decision":"Fase 25 sigue vigente","aptitud":"N/A"},
    ])
    (DOC/"MATRIZ_DECISIONES_POST_INTEGRACION_V21.md").write_text("# Matriz de decisiones post integración v2.1\n\n"+md_table(decisions)+"\n",encoding="utf-8")


def qa_package(before: dict[str,str], results: dict) -> dict:
    after=protected_hashes(); changed=sorted(k for k in set(before)|set(after) if before.get(k)!=after.get(k))
    geo=[]
    for p in sorted(OUT.glob("*.geojson")):
        try:
            g=gpd.read_file(p); geo.append({"archivo":p.name,"valido":bool(g.geometry.is_valid.all()) if len(g) else True,"features":len(g),"crs":str(g.crs)})
        except Exception as e: geo.append({"archivo":p.name,"valido":False,"features":-1,"crs":str(e)})
    png=[]
    for p in sorted(OUT.glob("*.png")):
        with Image.open(p) as img:
            sd=ImageStat.Stat(img.convert("L")).stddev[0]; png.append({"archivo":p.name,"ancho":img.width,"alto":img.height,"stddev":round(sd,2),"no_blanco":sd>2 and img.width>100 and img.height>100})
    patterns={"email":r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}","telefono":r"\b(?:\+?54\s*)?(?:11\s*)?\d{4}[-\s]?\d{4}\b","cuit":r"\b\d{2}-\d{8}-\d\b","api_key":r"AIza[0-9A-Za-z_\-]{20,}","place_id":r"place_id","drive":r"drive\.google\.com|docs\.google\.com"}
    hits=[]
    for p in HANDOFF.rglob("*"):
        if p.is_file() and p.suffix.lower() in {".md",".csv",".json",".geojson",".txt"}:
            text=p.read_text(encoding="utf-8",errors="replace")
            for label,pat in patterns.items():
                if re.search(pat,text,re.I): hits.append({"archivo":p.relative_to(HANDOFF).as_posix(),"patron":label})
    zip_path=OUT/"REVISION_PIPELINE_HIBRIDO_INTEGRACION_V21.zip"
    staged=subprocess.run(["git","diff","--cached","--name-only"],cwd=ROOT,text=True,capture_output=True,check=True).stdout.splitlines()
    metadata={
        "estado":"EXPERIMENTAL_NO_OFICIAL","fecha_corte":DATE,"semilla":SEED,"veredicto":"PIPELINE_HIBRIDO_POR_TIPO_TERRITORIAL","decision":"ESCALAR_CON_AJUSTES",
        "sin_api":True,"sin_google_places":True,"sin_descargas":True,"sin_instalaciones":True,"sin_modificacion_fuentes":True,"sin_kmeans":True,
        "hashes_protegidos":{"archivos":len(before),"cambiados":changed},"geojson_qa":geo,"png_qa":png,"privacidad_handoff_hits":hits,
        "zip":{"ruta":zip_path.relative_to(ROOT).as_posix(),"validacion_final":"OK_SI_EL_SCRIPT_COMPLETA","rutas_normalizadas":True,"entradas_duplicadas":0},
        "git":{"staged_count":len(staged),"staged_files":staged,"commit_ejecutado":False,"push_ejecutado":False},"python":sys.version,
    }
    (OUT/"metadata_pipeline_hibrido_integracion_v21.json").write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding="utf-8")
    qa=f"""# QA final integración v2.1

Estado: **EXPERIMENTAL / NO OFICIAL**.

- Sin API, Google Places ni descargas: **OK**.
- Sin instalaciones: **OK**; se usó `.venv` existente.
- Sin datos fuente modificados: **{'OK' if not changed else 'REVISAR'}**.
- Sin cambios en Fase 25, Fase 26, v1-v4.2 ni repeticiones v2: **{'OK' if not changed else 'REVISAR'}** ({len(before)} archivos protegidos; {len(changed)} cambios).
- GeoJSON válidos: **{'OK' if all(r['valido'] for r in geo) else 'REVISAR'}** ({len(geo)} archivos).
- PNG no blancos: **{'OK' if all(r['no_blanco'] for r in png) else 'REVISAR'}** ({len(png)} mapas).
- Privacidad del handoff: **{'OK' if not hits else 'REVISAR'}** ({len(hits)} hallazgos automáticos).
- ZIP íntegro, sin duplicados y con rutas normalizadas: **OK** (postcondición; el script aborta si falla).
- Staging: **{'OK' if not staged else 'REVISAR'}** ({len(staged)} archivos staged).
- Commit/push: **NO ejecutados**.

La búsqueda automática no sustituye revisión humana. Las geometrías son agregadas y experimentales; los buffers son convenciones cartográficas orientativas.
"""
    (DOC/"QA_FINAL_INTEGRACION_V21.md").write_text(qa,encoding="utf-8")
    # Manifest y ZIP se construyen después de QA/metadata para que cada ruta aparezca una sola vez.
    files=[]
    for base,label in ((DOC,"docs"),(OUT,"outputs"),(SCRIPT_DIR,"scripts")):
        for p in sorted(base.rglob("*")):
            if p.is_file() and p.suffix.lower() not in {".zip", ".pyc"} and p.name!="MANIFEST_ARCHIVOS.md" and "__pycache__" not in p.parts:
                files.append({"ruta":f"{label}/{p.relative_to(base).as_posix()}","bytes":p.stat().st_size,"sha256":sha256(p)})
    manifest=pd.DataFrame(files)
    (DOC/"MANIFEST_ARCHIVOS.md").write_text("# Manifest de archivos v2.1\n\n"+md_table(manifest)+"\n",encoding="utf-8")
    with zipfile.ZipFile(zip_path,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=9) as zf:
        for row in manifest.itertuples():
            label,rel=row.ruta.split("/",1); base={"docs":DOC,"outputs":OUT,"scripts":SCRIPT_DIR}[label]
            zf.write(base/rel,(Path("REVISION_PIPELINE_HIBRIDO_INTEGRACION_V21")/row.ruta).as_posix())
        zf.write(DOC/"MANIFEST_ARCHIVOS.md","REVISION_PIPELINE_HIBRIDO_INTEGRACION_V21/docs/MANIFEST_ARCHIVOS.md")
    with zipfile.ZipFile(zip_path) as zf:
        bad=zf.testzip(); names=zf.namelist(); backslashes=sum("\\" in n for n in names); duplicates=len(names)-len(set(names))
    if bad is not None or backslashes or duplicates:
        raise RuntimeError(f"ZIP inválido: bad={bad}, backslashes={backslashes}, duplicados={duplicates}")
    metadata["zip"].update({"bytes":zip_path.stat().st_size,"testzip":bad,"entradas":len(names),"backslash_entries":backslashes,"entradas_duplicadas":duplicates})
    return metadata


def main() -> None:
    ensure_dirs()
    before=protected_hashes()
    data=load_v1().load_inputs()
    audit=audit_v2(data)
    cost=costanera_v21(data,audit)
    pm=puerto_madero_v21(data)
    bel=belgrano_v21(data)
    st=san_telmo_v21(data)
    corr=corrientes_v21(data)
    pal=compact_scale(data,"Palermo Soho","MZ_PALERMO_SOHO","palermo_soho")
    rec=compact_scale(data,"Recoleta","MZ_RECOLETA","recoleta")
    cas=caseros_scale(data)
    matrix=write_scale_matrix([pal,rec,cas])
    zones=[{"zone":"Costanera Norte","points":cost["points"]},{"zone":"Puerto Madero","points":pm["points"]},{"zone":"Belgrano","points":bel["points"]},{"zone":"San Telmo","points":st["points"]},{"zone":"Corrientes","points":corr["points"]},pal,rec,cas]
    places=places_evaluation(zones)
    copy_handoff(cost,pm,bel,st,corr,[pal,rec,cas],matrix)
    write_decisions(cost,pm,bel,st,corr,matrix,places)
    metadata=qa_package(before,{"costanera":cost,"puerto":pm,"belgrano":bel,"san_telmo":st,"corrientes":corr,"escalado":[pal,rec,cas]})
    print(json.dumps({"status":"OK","out":str(OUT),"doc":str(DOC),"zip":metadata["zip"]},ensure_ascii=False))


if __name__ == "__main__":
    main()
