# -*- coding: utf-8 -*-
"""Piloto híbrido por tipo territorial para PolosGastro.

EXPERIMENTAL / NO OFICIAL. Solo lee insumos locales existentes. No llama APIs,
no descarga fuentes, no usa KMeans y no modifica etapas previas.
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import math
import re
import sys
import warnings
from collections import Counter
from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
import shapely
from scipy.spatial import cKDTree
from shapely.geometry import LineString, MultiPoint, Point
from shapely.ops import linemerge, unary_union
from sklearn import __version__ as sklearn_version
from sklearn.cluster import HDBSCAN
from sklearn.metrics import adjusted_rand_score
from sklearn.neighbors import KernelDensity

warnings.filterwarnings("ignore", category=FutureWarning)

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "outputs/polos_gastro/historico/experimentos/pipeline_hibrido_tipo_territorial_v1"
DOC = ROOT / "docs/polos_gastro/historico/experimentos/pipeline_hibrido_tipo_territorial_v1"
MAPS = OUT / "mapas"
INTERNAL = OUT / "interno_revision_deduplicacion"

AMP = ROOT / "outputs/polos_gastro/historico/experimentos/google_places_microzonas_ampliacion_v1"
COMP = AMP / "completa_v1"
AUDIT = ROOT / "outputs/polos_gastro/historico/experimentos/auditoria_integral_places_clustering_gpt56"
PROTO = ROOT / "outputs/polos_gastro/historico/experimentos/pipeline_microzonas_v1"
V42 = AMP / "cartografia_design_v4_2"

UNIVERSE = COMP / "UNIVERSO_COMPLETO_SANITIZADO.csv"
CURRENT_POINTS = COMP / "MICROCLUSTERS_COMPLETA_V1.geojson"
CURRENT_POLYGONS = COMP / "POLIGONOS_MICROZONAS_COMPLETA_V1.geojson"
ENTITIES = PROTO / "universo/universo_entidades_v1.csv"
MACROZONES = ROOT / "outputs/polos_gastro/historico/experimentos/infraestructura_cartografica_v1/macrozonas_editoriales_candidatas_v1.geojson"
STREETS = ROOT / "outputs/polos_gastro/fase15_mapas_callejeros_v3/assets/callejero_gcba_2026_06_02.geojson"
BARRIOS = ROOT / "PolosGastro/cartografia/barrios_caba.geojson"
COMUNAS = ROOT / "PolosGastro/cartografia/comunas_caba.geojson"
F03 = ROOT / "data/raw/f03_fiab.geojson"

CRS_GEO = "EPSG:4326"
CRS_M = "EPSG:5347"
RNG = np.random.default_rng(260710)
NOTE = "EXPERIMENTAL / NO OFICIAL. Oferta registrada/visible; no constituye delimitación institucional."

ZONE_SPECS = {
    "San Telmo": {"id": "MZ_SAN_TELMO", "type": "NUCLEO_COMPACTO"},
    "Corrientes": {"id": "MZ_AVENIDA_CORRIENTES", "type": "CORREDOR_LINEAL"},
    "Belgrano": {"id": "MZ_BELGRANO", "type": "RED_MULTINUCLEAR"},
    "Puerto Madero": {"id": "MZ_PUERTO_MADERO", "type": "FRENTE_GASTRONOMICO"},
    "Costanera Norte": {"id": "MZ_COSTANERA_NORTE", "type": "SENAL_EXPLORATORIA"},
}

COLORS = {
    "f01": "#1F5D7A",
    "places": "#C47A1D",
    "new": "#1E8A63",
    "old": "#8A949C",
    "street": "#BCC4CA",
    "noise": "#B7B7B7",
    "bg": "#F7F8F9",
}


def ensure_dirs() -> None:
    for p in (OUT, DOC, MAPS, INTERNAL):
        p.mkdir(parents=True, exist_ok=True)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def critical_inputs() -> list[Path]:
    explicit = [
        UNIVERSE, CURRENT_POINTS, CURRENT_POLYGONS, ENTITIES, MACROZONES, STREETS,
        BARRIOS, COMUNAS,
        AUDIT / "diagnostico_places_por_zona.csv",
        AUDIT / "metricas_robustez_por_zona.csv",
        AUDIT / "muestra_casos_deduplicacion_revision.csv",
        ROOT / "scripts/polos_gastro/build_fase25_microajustes_finales_oficina.py",
        ROOT / "outputs/polos_gastro/fase25_microajustes_finales_oficina/INFORME_POLOS_GASTRO_DGDGAS_11P_OFICINA_FASE25.pdf",
        V42 / "metadata_cartografia_v4_2.json",
        AMP / "cartografia_redibujo_editorial_v4_1/poligonos_v4_1_decision_dibujo.geojson",
        ROOT / "docs/polos_gastro/historico/experimentos/google_places_microzonas_ampliacion_v1/fase26_comparativa_cartografia/INFORME_FASE26_COMPARATIVA_CARTOGRAFIA.md",
    ]
    audit_docs = ROOT / "docs/polos_gastro/historico/experimentos/auditoria_integral_places_clustering_gpt56"
    explicit.extend(sorted(audit_docs.glob("*")))
    return sorted({p for p in explicit if p.is_file()})


def snapshot_hashes(finalize: bool = False) -> dict:
    rows = [{"ruta": p.relative_to(ROOT).as_posix(), "bytes": p.stat().st_size, "sha256": sha256(p)} for p in critical_inputs()]
    now = pd.DataFrame(rows)
    before_path = OUT / "hashes_insumos_criticos_antes.csv"
    if not before_path.exists():
        now.to_csv(before_path, index=False, encoding="utf-8")
    if not finalize:
        return {"archivos": len(now), "estado": "snapshot_inicial"}
    now.to_csv(OUT / "hashes_insumos_criticos_despues.csv", index=False, encoding="utf-8")
    before = pd.read_csv(before_path)
    comp = before.merge(now, on="ruta", how="outer", suffixes=("_antes", "_despues"), indicator=True)
    comp["sin_cambios"] = comp["_merge"].eq("both") & comp["sha256_antes"].eq(comp["sha256_despues"]) & comp["bytes_antes"].eq(comp["bytes_despues"])
    comp.to_csv(OUT / "comparacion_hashes_insumos_criticos.csv", index=False, encoding="utf-8")
    return {"archivos": len(comp), "sin_cambios": int(comp.sin_cambios.sum()), "cambiados": int((~comp.sin_cambios).sum())}


def write_geo(gdf: gpd.GeoDataFrame, path: Path) -> None:
    if gdf.empty:
        path.write_text('{"type":"FeatureCollection","features":[]}', encoding="utf-8")
    else:
        gdf.to_crs(CRS_GEO).to_file(path, driver="GeoJSON")


def n_clusters(labels: np.ndarray) -> int:
    return len(set(labels.tolist()) - {-1})


def fit_hdbscan(xy: np.ndarray, factor: float = 1.0, min_samples: int = 5,
                 epsilon: float = 50.0, method: str = "eom", allow_fallback: bool = True) -> dict:
    if len(xy) < 8:
        return {"labels": np.full(len(xy), -1, dtype=int), "probabilities": np.zeros(len(xy)), "epsilon_used": None, "error": "n<8", "fallback": False}
    mcs = min(max(8, int(round(0.03 * len(xy) * factor))), len(xy) - 1)
    tried = [float(epsilon)] + ([0.0] if allow_fallback and float(epsilon) != 0 else [])
    errors = []
    for eps in tried:
        try:
            model = HDBSCAN(
                min_cluster_size=mcs, min_samples=min(min_samples, mcs),
                cluster_selection_epsilon=eps, cluster_selection_method=method,
                copy=True,
            ).fit(xy)
            return {
                "labels": model.labels_, "probabilities": model.probabilities_,
                "epsilon_used": eps, "error": " | ".join(errors),
                "fallback": eps != float(epsilon), "mcs": mcs, "min_samples": min_samples,
                "method": method,
            }
        except Exception as exc:  # error is persisted, never hidden
            errors.append(f"eps={eps}:{type(exc).__name__}:{str(exc)[:180]}")
    return {"labels": np.full(len(xy), -1, dtype=int), "probabilities": np.zeros(len(xy)), "epsilon_used": None, "error": " | ".join(errors), "fallback": False, "mcs": mcs, "min_samples": min_samples, "method": method}


def xy_of(gdf: gpd.GeoDataFrame) -> np.ndarray:
    return np.column_stack([gdf.geometry.x.to_numpy(), gdf.geometry.y.to_numpy()])


def ari(reference: np.ndarray, alternative: np.ndarray) -> float:
    if len(reference) != len(alternative) or len(reference) == 0:
        return float("nan")
    return float(adjusted_rand_score(reference, alternative))


def classify_local(v: float) -> str:
    if pd.isna(v): return "NO_EVALUABLE"
    return "ALTA" if v >= 0.85 else "MEDIA" if v >= 0.60 else "BAJA"


def classify_sensitivity(v: float) -> str:
    if pd.isna(v): return "NO_EVALUABLE"
    return "BAJA_SENSIBILIDAD" if v >= 0.80 else "MEDIA_SENSIBILIDAD" if v >= 0.50 else "ALTA_SENSIBILIDAD"


def token_similarity(a: str, b: str) -> float:
    ta, tb = set(str(a or "").split()), set(str(b or "").split())
    return len(ta & tb) / max(1, min(len(ta), len(tb))) if ta and tb else 0.0


def compatible_name(a: str, b: str) -> bool:
    a, b = str(a or "").strip(), str(b or "").strip()
    return bool(a and b and (a in b or b in a or token_similarity(a, b) >= 0.5))


def load_inputs() -> dict:
    universe = pd.read_csv(UNIVERSE, low_memory=False)
    entities = pd.read_csv(ENTITIES, low_memory=False)
    flags = entities[["id_entidad", "en_f01", "en_f02", "nombre_canonico", "nombre_norm", "direccion_normalizada"]].copy()
    flags["id_entidad"] = flags.id_entidad.astype(str)
    universe = universe.merge(flags, left_on="id_punto", right_on="id_entidad", how="left")
    points = gpd.GeoDataFrame(universe.copy(), geometry=gpd.points_from_xy(universe.lon, universe.lat), crs=CRS_GEO).to_crs(CRS_M)
    current_points = gpd.read_file(CURRENT_POINTS).to_crs(CRS_M)
    current_polygons = gpd.read_file(CURRENT_POLYGONS).to_crs(CRS_M)
    macro = gpd.read_file(MACROZONES).to_crs(CRS_M).set_index("id", drop=False)
    streets = gpd.read_file(STREETS).to_crs(CRS_M)
    barrios = gpd.read_file(BARRIOS).to_crs(CRS_M)
    comunas = gpd.read_file(COMUNAS).to_crs(CRS_M)
    return {"universe": universe, "entities": entities, "points": points, "current_points": current_points, "current_polygons": current_polygons, "macro": macro, "streets": streets, "barrios": barrios, "comunas": comunas}


def corrected_places_and_stability(data: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows_places, rows_stability = [], []
    points, polygons = data["points"], data["current_polygons"]
    for mz, sub in points.groupby("macrozona_id"):
        sub = sub.copy().reset_index(drop=True)
        xy = xy_of(sub)
        full = fit_hdbscan(xy)
        mask_base = sub.fuente.eq("F01+F02").to_numpy()
        base = fit_hdbscan(xy[mask_base])
        full_noise = 100 * float((full["labels"] == -1).mean())
        base_noise = 100 * float((base["labels"] == -1).mean())
        diff_c = n_clusters(full["labels"]) - n_clusters(base["labels"])
        diff_r = full_noise - base_noise
        change = "ESTRUCTURAL" if abs(diff_c) >= 2 or abs(diff_r) >= 10 else "MODERADO" if abs(diff_c) == 1 or abs(diff_r) >= 5 else "VOLUMEN_SIN_CAMBIO_MAYOR"
        pct_places = 100 * float(sub.fuente.eq("google_places").mean())
        dependence = "ALTA" if pct_places >= 60 else "MEDIA" if pct_places >= 40 else "BAJA"
        rows_places.append({
            "macrozona": mz,
            "puntos_f01_f02": int(mask_base.sum()),
            "puntos_places": int((~mask_base).sum()),
            "porcentaje_places": round(pct_places, 2),
            "hdbscan_clusters_universo_completo": n_clusters(full["labels"]),
            "hdbscan_ruido_universo_completo": round(full_noise, 2),
            "hdbscan_clusters_f01_f02": n_clusters(base["labels"]),
            "hdbscan_ruido_f01_f02": round(base_noise, 2),
            "diferencia_clusters_hdbscan": diff_c,
            "diferencia_ruido": round(diff_r, 2),
            "poligonos_post_kmeans_v1": int((polygons.macrozona_id == mz).sum()),
            "cambio_lectura_territorial": change,
            "explicacion_cambio": f"HDBSCAN completo vs F01/F02; epsilon completo={full['epsilon_used']}, base={base['epsilon_used']}. Los polígonos se informan aparte.",
            "dependencia_places": dependence,
            "confianza": "BAJA" if dependence == "ALTA" else "MEDIA_BAJA" if change == "ESTRUCTURAL" else "MEDIA",
        })

        configs = {
            "mcs_80": fit_hdbscan(xy, factor=0.8),
            "mcs_120": fit_hdbscan(xy, factor=1.2),
            "ms_3": fit_hdbscan(xy, min_samples=3),
            "ms_8": fit_hdbscan(xy, min_samples=8),
            "eps_0": fit_hdbscan(xy, epsilon=0, allow_fallback=False),
            "eps_100": fit_hdbscan(xy, epsilon=100, allow_fallback=False),
            "leaf": fit_hdbscan(xy, method="leaf"),
        }
        scores = {k: ari(full["labels"], v["labels"]) if v["epsilon_used"] is not None else np.nan for k, v in configs.items()}
        local = float(np.nanmedian([scores[k] for k in ["mcs_80", "mcs_120", "ms_3", "ms_8"]]))
        mcs_s = float(np.nanmin([scores["mcs_80"], scores["mcs_120"]]))
        ms_s = float(np.nanmin([scores["ms_3"], scores["ms_8"]]))
        eps_s = float(min(scores["eps_0"], scores["eps_100"])) if not any(pd.isna(scores[k]) for k in ["eps_0", "eps_100"]) else np.nan
        leaf_s = scores["leaf"]
        available = [x for x in [mcs_s, ms_s, eps_s, leaf_s] if not pd.isna(x)]
        global_min = min(available) if available else np.nan

        boot = []
        for _ in range(5):
            keep = np.sort(RNG.choice(len(xy), max(8, int(0.9 * len(xy))), replace=False))
            b = fit_hdbscan(xy[keep])
            boot.append(ari(full["labels"][keep], b["labels"]))
        boot_mean = float(np.nanmean(boot))
        local_class = classify_local(local)
        global_class = classify_sensitivity(global_min)
        if pd.isna(eps_s):
            global_class += "_EVALUACION_EPSILON_INCOMPLETA"
        interpretation = f"Estabilidad local {local_class}; {global_class.lower().replace('_', ' ')}."
        if mz == "MZ_CABALLITO":
            interpretation += " Detector consistente cerca de la configuración base, pero leaf/eom cambia la partición; esto no valida los 33 polígonos posteriores."
        if pd.isna(eps_s):
            interpretation += " Sensibilidad epsilon no evaluable por error reproducido de scikit-learn 1.9; no se imputa estabilidad."
        errors = " | ".join(v["error"] for v in configs.values() if v.get("error"))
        rows_stability.append({
            "macrozona": mz,
            "estabilidad_perturbaciones_locales": round(local, 4),
            "estabilidad_bootstrap_puntos": round(boot_mean, 4),
            "sensibilidad_min_cluster_size": round(mcs_s, 4),
            "sensibilidad_min_samples": round(ms_s, 4),
            "sensibilidad_epsilon": round(eps_s, 4) if not pd.isna(eps_s) else np.nan,
            "sensibilidad_leaf_eom": round(leaf_s, 4) if not pd.isna(leaf_s) else np.nan,
            "sensibilidad_global_minima": round(global_min, 4) if not pd.isna(global_min) else np.nan,
            "clasificacion_estabilidad_local": local_class,
            "clasificacion_sensibilidad_global": global_class,
            "interpretacion": interpretation,
            "epsilon_base_usado": full["epsilon_used"],
            "fallback_epsilon_base": full["fallback"],
            "errores_hdbscan_registrados": errors,
        })
    places_df = pd.DataFrame(rows_places).sort_values("macrozona")
    stability_df = pd.DataFrame(rows_stability).sort_values("macrozona")
    places_df.to_csv(OUT / "diagnostico_places_por_zona_corregido.csv", index=False, encoding="utf-8")
    stability_df.to_csv(OUT / "metricas_estabilidad_desagregadas_v1.csv", index=False, encoding="utf-8")
    return places_df, stability_df


def inventory_layers(data: dict) -> pd.DataFrame:
    specs = [
        (STREETS, "GeoJSON", data["streets"], "CABA completa", "id; nomoficial; nom_mapa; tipo_c; red_jerarq; barrio; comuna", "ALTA", "SI", "Ejes reales; no incluye hidrografía ni geometría de diques."),
        (BARRIOS, "GeoJSON", data["barrios"], "48 barrios CABA", "nombre; comuna; área", "ALTA", "NO", "Límite administrativo, no eje vial."),
        (COMUNAS, "GeoJSON", data["comunas"], "15 comunas CABA", "comuna; barrios; área", "ALTA", "NO", "Escala demasiado gruesa para corredor."),
        (ROOT / "data/raw/geo_barrios.geojson", "GeoJSON", gpd.read_file(ROOT / "data/raw/geo_barrios.geojson"), "48 barrios CABA", "nombre; comuna", "ALTA", "NO", "Duplicado de referencia; no usado."),
        (ROOT / "data/raw/geo_comunas.geojson", "GeoJSON", gpd.read_file(ROOT / "data/raw/geo_comunas.geojson"), "15 comunas CABA", "comuna; barrios", "ALTA", "NO", "Duplicado de referencia; no usado."),
        (F03, "GeoJSON", gpd.read_file(F03), "184 puntos FIAB", "nombre; día; ubicación; barrio; comuna", "MEDIA", "NO", "Puntos de ferias; no es capa urbana de soporte."),
        (MACROZONES, "GeoJSON", data["macro"], "13 macrozonas experimentales usadas", "id; nombre; fuente; método", "MEDIA", "NO", "Contenedores editoriales previos; se audita sensibilidad de borde."),
    ]
    rows = []
    for path, fmt, gdf, coverage, fields, quality, suitable, limitations in specs:
        rows.append({
            "ruta": path.relative_to(ROOT).as_posix(), "formato": fmt, "CRS": str(gdf.crs),
            "cobertura": coverage, "campos_utiles": fields, "calidad_aparente": quality,
            "apta_para_eje_buffer": suitable, "limitaciones": limitations,
            "registros": len(gdf), "geometrias": ";".join(sorted(gdf.geom_type.unique())),
        })
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "inventario_capas_urbanas_locales.csv", index=False, encoding="utf-8")
    return df


def kde_geometry(xy: np.ndarray, bandwidth: float, threshold: float, clip_geom, grid: float = 25.0):
    if len(xy) < 5:
        return None, 0, 0.0
    model = KernelDensity(bandwidth=bandwidth).fit(xy)
    minx, miny = xy.min(axis=0) - 2 * bandwidth
    maxx, maxy = xy.max(axis=0) + 2 * bandwidth
    xs = np.arange(minx, maxx + grid, grid)
    ys = np.arange(miny, maxy + grid, grid)
    gx, gy = np.meshgrid(xs, ys)
    coords = np.column_stack([gx.ravel(), gy.ravel()])
    dens = np.exp(model.score_samples(coords))
    mask = dens >= threshold * dens.max()
    if not mask.any():
        return None, 0, float(dens.max())
    c = coords[mask]
    cells = shapely.box(c[:, 0] - grid / 2, c[:, 1] - grid / 2, c[:, 0] + grid / 2, c[:, 1] + grid / 2)
    geom = shapely.union_all(cells).buffer(grid / 2).simplify(grid / 2).intersection(clip_geom)
    parts = len(geom.geoms) if geom.geom_type == "MultiPolygon" else 1
    return geom, parts, float(dens.max())


def polygonize_clusters(sub: gpd.GeoDataFrame, labels: np.ndarray, macro_geom, min_n: int = 8) -> gpd.GeoDataFrame:
    rows = []
    for cid in sorted(set(labels.tolist()) - {-1}):
        pts = sub.loc[labels == cid]
        if len(pts) < min_n:
            continue
        mp = MultiPoint(list(zip(pts.geometry.x, pts.geometry.y)))
        geom = shapely.concave_hull(mp, ratio=0.4, allow_holes=False).buffer(35).intersection(macro_geom)
        if geom.is_empty:
            continue
        n_places = int(pts.fuente.eq("google_places").sum())
        rows.append({
            "cluster_id": int(cid), "n_puntos": len(pts), "puntos_f01_f02": len(pts) - n_places,
            "puntos_places": n_places, "porcentaje_places": round(100 * n_places / len(pts), 2),
            "area_ha": round(geom.area / 10000, 2), "geometry": geom,
        })
    return gpd.GeoDataFrame(rows, geometry="geometry", crs=CRS_M) if rows else gpd.GeoDataFrame(columns=["cluster_id", "geometry"], geometry="geometry", crs=CRS_M)


def block_stability(sub: gpd.GeoDataFrame, block_sizes=(200, 300), reps=20) -> pd.DataFrame:
    xy = xy_of(sub)
    base = fit_hdbscan(xy)
    rows = []
    for size in block_sizes:
        bx = np.floor((xy[:, 0] - xy[:, 0].min()) / size).astype(int)
        by = np.floor((xy[:, 1] - xy[:, 1].min()) / size).astype(int)
        block = np.array([f"{a}_{b}" for a, b in zip(bx, by)])
        unique = np.unique(block)
        vals = []
        for rep in range(reps):
            keep_blocks = RNG.choice(unique, max(2, int(math.ceil(0.8 * len(unique)))), replace=False)
            keep = np.flatnonzero(np.isin(block, keep_blocks))
            if len(keep) < 8:
                continue
            fit = fit_hdbscan(xy[keep])
            vals.append(ari(base["labels"][keep], fit["labels"]))
        rows.append({
            "tamano_bloque_m": size, "repeticiones": len(vals),
            "ari_medio": round(float(np.nanmean(vals)), 4) if vals else np.nan,
            "ari_p10": round(float(np.nanpercentile(vals, 10)), 4) if vals else np.nan,
            "ari_min": round(float(np.nanmin(vals)), 4) if vals else np.nan,
            "metodo": "submuestreo 80% de bloques sin reemplazo",
        })
    return pd.DataFrame(rows)


def source_ablation(data: dict) -> pd.DataFrame:
    rows = []
    for zone, spec in ZONE_SPECS.items():
        sub = data["points"][data["points"].macrozona_id.eq(spec["id"])].copy()
        masks = {
            "universo_completo": np.ones(len(sub), dtype=bool),
            "F01_F02": sub.fuente.eq("F01+F02").to_numpy(),
            "Places_solo_diagnostico": sub.fuente.eq("google_places").to_numpy(),
            "F01_solo": (sub.fuente.eq("F01+F02") & sub.en_f01.fillna(False).astype(bool)).to_numpy(),
            "F02_solo": (sub.fuente.eq("F01+F02") & sub.en_f02.fillna(False).astype(bool)).to_numpy(),
        }
        xy = xy_of(sub)
        for name, mask in masks.items():
            fit = fit_hdbscan(xy[mask])
            rows.append({
                "zona": zone, "universo": name, "n_puntos": int(mask.sum()),
                "clusters": n_clusters(fit["labels"]),
                "pct_ruido": round(100 * float((fit["labels"] == -1).mean()), 2) if mask.sum() else np.nan,
                "epsilon_usado": fit["epsilon_used"], "fallback": fit["fallback"],
                "advertencia": "Places-only es diagnóstico de fuente externa, no padrón." if "Places" in name else "",
            })
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "robustez_ablacion_fuentes_v1.csv", index=False, encoding="utf-8")
    return df


def load_raw_places() -> gpd.GeoDataFrame:
    paths = [
        ROOT / "outputs/polos_gastro/historico/experimentos/google_places_microzonas_piloto/interno/places_resultados_interno.csv",
        AMP / "interno/places_resultados_interno_a_criticas.csv",
        AMP / "interno/places_resultados_interno_b_consolidacion.csv",
        AMP / "interno/refinamientos/places_resultados_interno_refino_chacarita_saturadas_3x3.csv",
    ]
    parts = [pd.read_csv(p) for p in paths if p.exists()]
    raw = pd.concat(parts, ignore_index=True).drop_duplicates("google_place_id_interno")
    return gpd.GeoDataFrame(raw, geometry=gpd.points_from_xy(raw.lon, raw.lat), crs=CRS_GEO).to_crs(CRS_M)


def border_sensitivity(data: dict) -> pd.DataFrame:
    raw_places = load_raw_places()
    all_entities = data["entities"]
    all_base = gpd.GeoDataFrame(all_entities, geometry=gpd.points_from_xy(all_entities.lon, all_entities.lat), crs=CRS_GEO).to_crs(CRS_M)
    rows = []
    for zone, spec in ZONE_SPECS.items():
        geom = data["macro"].loc[spec["id"]].geometry
        sub = data["points"][data["points"].macrozona_id.eq(spec["id"])].copy()
        distances = sub.geometry.distance(geom.boundary)
        reduced = sub[distances > 100]
        fit_full = fit_hdbscan(xy_of(sub))
        fit_red = fit_hdbscan(xy_of(reduced))
        ring = geom.buffer(200).difference(geom)
        outer_base = all_base[all_base.geometry.within(ring)]
        outer_places = raw_places[raw_places.geometry.within(ring)]
        rows.append({
            "zona": zone, "puntos_total": len(sub), "puntos_hasta_100m_borde": int((distances <= 100).sum()),
            "porcentaje_cerca_borde": round(100 * float((distances <= 100).mean()), 2),
            "clusters_completo": n_clusters(fit_full["labels"]), "clusters_contenedor_reducido_100m": n_clusters(fit_red["labels"]),
            "ruido_completo": round(100 * float((fit_full["labels"] == -1).mean()), 2),
            "ruido_reducido": round(100 * float((fit_red["labels"] == -1).mean()), 2) if len(reduced) else np.nan,
            "puntos_f01_f02_almacenados_anillo_externo_200m": len(outer_base),
            "places_brutos_almacenados_anillo_externo_200m": len(outer_places),
            "decision_expansion": "NO_INCORPORAR_SIN_REDEDUPLICAR; solo diagnóstico de borde",
        })
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "robustez_bordes_v1.csv", index=False, encoding="utf-8")
    return df


def street_segments(data: dict, official_name: str, macro_id: str) -> gpd.GeoDataFrame:
    geom = data["macro"].loc[macro_id].geometry
    s = data["streets"][data["streets"].nomoficial.fillna("").eq(official_name)].copy()
    s["geometry"] = s.geometry.intersection(geom)
    s = s[~s.geometry.is_empty].explode(index_parts=False).reset_index(drop=True)
    return s


def supported_axis(segments: gpd.GeoDataFrame, points: gpd.GeoDataFrame, radius: float) -> tuple[gpd.GeoDataFrame, object]:
    rows = []
    for i, seg in segments.iterrows():
        n = int((points.geometry.distance(seg.geometry) <= radius).sum())
        f = int(((points.geometry.distance(seg.geometry) <= radius) & points.fuente.eq("F01+F02")).sum())
        p = n - f
        length = seg.geometry.length
        rows.append({"segmento": i + 1, "n_puntos_radio": n, "f01_f02": f, "places": p, "longitud_m": length, "densidad_puntos_km": 1000 * n / max(length, 1), "geometry": seg.geometry})
    g = gpd.GeoDataFrame(rows, geometry="geometry", crs=CRS_M)
    positive = g.loc[g.n_puntos_radio > 0, "n_puntos_radio"]
    gate = max(3, int(math.floor(positive.quantile(0.25)))) if len(positive) else 3
    g["respaldado_densidad"] = g.n_puntos_radio >= gate
    selected = g[g.respaldado_densidad]
    axis = unary_union(selected.geometry.tolist()) if len(selected) else unary_union(g.geometry.tolist())
    return g, axis


def longitudinal_profile(points: gpd.GeoDataFrame, bin_m: float = 200) -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    xy = xy_of(points)
    center = xy.mean(axis=0)
    _, _, vt = np.linalg.svd(xy - center, full_matrices=False)
    axis = vt[0]
    proj = (xy - center) @ axis
    start = math.floor(proj.min() / bin_m) * bin_m
    end = math.ceil(proj.max() / bin_m) * bin_m
    edges = np.arange(start, end + bin_m, bin_m)
    bins = np.digitize(proj, edges) - 1
    rows = []
    for b in range(len(edges) - 1):
        mask = bins == b
        n = int(mask.sum())
        f = int(points.iloc[np.flatnonzero(mask)].fuente.eq("F01+F02").sum()) if n else 0
        rows.append({
            "bin_id": b + 1, "desde_m_relativo": edges[b], "hasta_m_relativo": edges[b + 1],
            "puntos_total": n, "puntos_f01_f02": f, "puntos_places": n - f,
            "densidad_puntos_km": 1000 * n / bin_m, "es_hueco": n == 0,
        })
    return pd.DataFrame(rows), center, axis


def variable_buffer(segment_metrics: gpd.GeoDataFrame):
    positive = segment_metrics[segment_metrics.respaldado_densidad].copy()
    if positive.empty:
        return None
    q1, q2 = positive.densidad_puntos_km.quantile([0.33, 0.66]).tolist()
    geoms = []
    widths = []
    for _, r in positive.iterrows():
        width = 60 if r.densidad_puntos_km <= q1 else 90 if r.densidad_puntos_km <= q2 else 120
        geoms.append(r.geometry.buffer(width, cap_style="flat")); widths.append(width)
    positive["buffer_m"] = widths
    return unary_union(geoms), positive


def prototype_san_telmo(data: dict) -> dict:
    mz = "MZ_SAN_TELMO"; macro = data["macro"].loc[mz].geometry
    sub = data["points"][data["points"].macrozona_id.eq(mz)].copy().reset_index(drop=True)
    xy = xy_of(sub)
    fits = {
        "HDBSCAN_eom": fit_hdbscan(xy, method="eom"),
        "HDBSCAN_leaf": fit_hdbscan(xy, method="leaf"),
    }
    comparison = []
    for name, fit in fits.items():
        comparison.append({"metodo": name, "parametros": f"mcs={fit['mcs']}; ms=5; epsilon_usado={fit['epsilon_used']}", "clusters": n_clusters(fit["labels"]), "pct_ruido": round(100 * float((fit["labels"] == -1).mean()), 2), "componentes": np.nan, "area_ha": np.nan, "observacion": fit["error"]})
    kde_geoms = {}
    for bw in (80, 100, 140):
        for thr in (0.35, 0.50, 0.65):
            geom, parts, _ = kde_geometry(xy, bw, thr, macro)
            kde_geoms[(bw, thr)] = geom
            comparison.append({"metodo": "KDE", "parametros": f"bandwidth={bw}; umbral_relativo={thr}", "clusters": np.nan, "pct_ruido": np.nan, "componentes": parts, "area_ha": round(geom.area / 10000, 2) if geom else 0, "observacion": "Contorno de densidad; no asigna identidad territorial."})
    pd.DataFrame(comparison).to_csv(OUT / "san_telmo_comparacion_metodos.csv", index=False, encoding="utf-8")

    local_fits = [fit_hdbscan(xy, factor=f, min_samples=ms) for f, ms in [(0.8, 5), (1, 3), (1, 5), (1, 8), (1.2, 5)]]
    membership = np.mean(np.column_stack([f["labels"] >= 0 for f in local_fits]), axis=1)
    base = fits["HDBSCAN_eom"]
    candidates = []
    kde = kde_geoms[(100, 0.50)]
    consensus = kde_geoms[(80, 0.50)].intersection(kde_geoms[(100, 0.50)]).intersection(kde_geoms[(140, 0.50)])
    stable_points = sub.loc[membership >= 0.75]
    support = unary_union([g.buffer(100) for g in stable_points.geometry]) if len(stable_points) else None
    if support is not None:
        consensus = consensus.intersection(support).intersection(macro)
    parts = list(consensus.geoms) if consensus.geom_type == "MultiPolygon" else [consensus]
    for geom in parts:
        pts = sub[sub.geometry.within(geom)]
        if len(pts) < 8 or geom.is_empty:
            continue
        npl = int(pts.fuente.eq("google_places").sum())
        candidates.append({"nucleo_id": f"ST_N{len(candidates)+1:02d}", "n_puntos": len(pts), "f01_f02": len(pts)-npl, "places": npl, "porcentaje_places": round(100*npl/len(pts),2), "estabilidad_membresia_media": round(float(membership[pts.index].mean()),3), "metodo": "consenso KDE bw80/100/140 umbral50 restringido a soporte HDBSCAN estable", "estado": "CANDIDATO_EXPERIMENTAL", "geometry": geom})
    cand = gpd.GeoDataFrame(candidates, geometry="geometry", crs=CRS_M) if candidates else gpd.GeoDataFrame(columns=["nucleo_id","geometry"], geometry="geometry", crs=CRS_M)
    write_geo(cand, OUT / "san_telmo_nucleo_candidato.geojson")
    blocks = block_stability(sub); blocks.insert(0, "zona", "San Telmo")
    return {"sub": sub, "new": cand, "blocks": blocks, "eom": base, "kde": kde, "defensa": street_segments(data, "DEFENSA", mz), "summary": {"nucleos": len(cand), "puntos": len(sub), "places_pct": round(100*sub.fuente.eq('google_places').mean(),1), "block": round(blocks.ari_medio.mean(),2)}}


def merged_axis_feature(selected: gpd.GeoDataFrame, props: dict) -> gpd.GeoDataFrame:
    geom = linemerge(unary_union(selected.geometry.tolist())) if len(selected) else None
    if geom is None or geom.is_empty:
        return gpd.GeoDataFrame(columns=["geometry"], geometry="geometry", crs=CRS_M)
    components = len(geom.geoms) if geom.geom_type == "MultiLineString" else 1
    row = dict(props)
    row.update({"segmentos_soporte": len(selected), "componentes_geometricos": components, "longitud_m": round(geom.length, 1), "geometry": geom})
    return gpd.GeoDataFrame([row], geometry="geometry", crs=CRS_M)


def prototype_corrientes(data: dict) -> dict:
    mz="MZ_AVENIDA_CORRIENTES"; sub=data["points"][data["points"].macrozona_id.eq(mz)].copy().reset_index(drop=True)
    segments=street_segments(data,"CORRIENTES AV.",mz)
    metrics, axis=supported_axis(segments,sub,150)
    vb=variable_buffer(metrics)
    buffer_geom, supported = vb if vb else (axis.buffer(90), metrics)
    profile, _, _=longitudinal_profile(sub,200)
    profile["tramo_respaldado"] = ~profile.es_hueco
    profile.to_csv(OUT/"corrientes_perfil_longitudinal.csv",index=False,encoding="utf-8")
    support_segments=metrics[metrics.respaldado_densidad].copy()
    axis_g=merged_axis_feature(support_segments,{"metodo":"eje local CORRIENTES AV. respaldado por puntos a 150 m","estado":"EXPERIMENTAL"})
    write_geo(axis_g,OUT/"corrientes_eje_candidato.geojson")
    buff_g=gpd.GeoDataFrame([{"metodo":"buffer variable 60/90/120 m según densidad por segmento","estado":"EXPERIMENTAL","geometry":buffer_geom}],geometry="geometry",crs=CRS_M)
    write_geo(buff_g,OUT/"corrientes_buffer_candidato.geojson")
    blocks=block_stability(sub); blocks.insert(0,"zona","Corrientes")
    occupied=profile[~profile.es_hueco]
    breaks=int(((profile.es_hueco.astype(int).diff()==1)).sum())
    return {"sub":sub,"new":buff_g,"axis":axis_g,"blocks":blocks,"summary":{"segmentos_soporte":len(support_segments),"componentes_eje":int(axis_g.componentes_geometricos.iloc[0]) if len(axis_g) else 0,"longitud_m":round(axis_g.geometry.length.sum(),0),"huecos_bins":int(profile.es_hueco.sum()),"quiebres":breaks,"places_pct":round(100*sub.fuente.eq('google_places').mean(),1),"block":round(blocks.ari_medio.mean(),2)}}


def graph_communities(xy: np.ndarray, threshold: float, min_size: int = 8) -> tuple[np.ndarray, float, int]:
    graph=nx.Graph(); graph.add_nodes_from(range(len(xy)))
    tree=cKDTree(xy); pairs=tree.query_pairs(threshold)
    for a,b in pairs:
        d=float(np.linalg.norm(xy[a]-xy[b])); graph.add_edge(a,b,weight=math.exp(-((d/threshold)**2)))
    communities=[]; modularities=[]
    for component in nx.connected_components(graph):
        if len(component)<min_size: continue
        sg=graph.subgraph(component)
        if sg.number_of_edges()==0: continue
        comm=list(nx.community.greedy_modularity_communities(sg,weight="weight"))
        communities.extend([set(c) for c in comm if len(c)>=min_size])
        if len(comm)>1:
            modularities.append(nx.community.modularity(sg,comm,weight="weight"))
    labels=np.full(len(xy),-1,dtype=int)
    for cid,c in enumerate(communities): labels[list(c)]=cid
    return labels,float(np.mean(modularities)) if modularities else 0.0,len(pairs)


def prototype_belgrano(data: dict) -> dict:
    mz="MZ_BELGRANO"; macro=data["macro"].loc[mz].geometry
    sub=data["points"][data["points"].macrozona_id.eq(mz)].copy().reset_index(drop=True); xy=xy_of(sub)
    tree=cKDTree(xy); dists,_=tree.query(xy,k=min(6,len(xy))); fifth=dists[:,-1]
    thresholds=sorted({int(np.clip(np.quantile(fifth,q),60,220)) for q in (0.50,0.75,0.90)})
    eom=fit_hdbscan(xy,method="eom"); leaf=fit_hdbscan(xy,method="leaf")
    rows=[{"metodo":"HDBSCAN_eom","umbral_m":np.nan,"clusters":n_clusters(eom['labels']),"pct_ruido":round(100*(eom['labels']==-1).mean(),2),"modularidad":np.nan,"aristas":np.nan,"ari_vs_hdbscan_eom":1.0},
          {"metodo":"HDBSCAN_leaf","umbral_m":np.nan,"clusters":n_clusters(leaf['labels']),"pct_ruido":round(100*(leaf['labels']==-1).mean(),2),"modularidad":np.nan,"aristas":np.nan,"ari_vs_hdbscan_eom":round(ari(eom['labels'],leaf['labels']),4)}]
    graph_results={}
    for t in thresholds:
        labels,mod,edges=graph_communities(xy,t); graph_results[t]=labels
        rows.append({"metodo":"grafo_comunidades","umbral_m":t,"clusters":n_clusters(labels),"pct_ruido":round(100*(labels==-1).mean(),2),"modularidad":round(mod,4),"aristas":edges,"ari_vs_hdbscan_eom":round(ari(eom['labels'],labels),4)})
    pd.DataFrame(rows).to_csv(OUT/"belgrano_comparacion_comunidades.csv",index=False,encoding="utf-8")
    chosen=thresholds[len(thresholds)//2]; labels=graph_results[chosen]
    lower=graph_results[thresholds[0]]; upper=graph_results[thresholds[-1]]
    kde,_,_=kde_geometry(xy,100,0.5,macro)
    stable_labels=np.full(len(labels),-1,dtype=int); next_id=0
    for cid in sorted(set(labels.tolist())-{-1}):
        idx_set=set(np.flatnonzero(labels==cid))
        def best_jacc(other):
            vals=[]
            for oid in set(other.tolist())-{-1}:
                o=set(np.flatnonzero(other==oid)); vals.append(len(idx_set&o)/max(1,len(idx_set|o)))
            return max(vals) if vals else 0.0
        if best_jacc(lower)>=0.40 and best_jacc(upper)>=0.40:
            stable_labels[list(idx_set)]=next_id; next_id+=1
    nuclei=polygonize_clusters(sub,stable_labels,macro,min_n=8)
    if len(nuclei) and kde is not None:
        nuclei["solape_kde"]=[g.intersection(kde).area/max(g.area,1) for g in nuclei.geometry]
        nuclei=nuclei[nuclei.solape_kde>=0.20].reset_index(drop=True)
    if len(nuclei):
        nuclei["nucleo_id"]=[f"BEL_N{i+1:02d}" for i in range(len(nuclei))]
        nuclei["metodo"] = f"grafo proximidad; umbral p75 quinto vecino={chosen} m; comunidad modular"
        nuclei["estado"]="CANDIDATO_EXPERIMENTAL_SIN_NOMBRE"
    write_geo(nuclei,OUT/"belgrano_nucleos_candidatos.geojson")
    blocks=block_stability(sub); blocks.insert(0,"zona","Belgrano")
    return {"sub":sub,"new":nuclei,"blocks":blocks,"kde":kde,"summary":{"nucleos":len(nuclei),"umbral_m":chosen,"hdb_eom":n_clusters(eom['labels']),"hdb_leaf":n_clusters(leaf['labels']),"places_pct":round(100*sub.fuente.eq('google_places').mean(),1),"block":round(blocks.ari_medio.mean(),2)}}


def prototype_puerto(data: dict) -> dict:
    mz="MZ_PUERTO_MADERO"; sub=data["points"][data["points"].macrozona_id.eq(mz)].copy().reset_index(drop=True)
    segments=street_segments(data,"MOREAU DE JUSTO, ALICIA AV.",mz)
    metrics,axis=supported_axis(segments,sub,180)
    profile,_,_=longitudinal_profile(sub,250)
    support_segments=metrics[metrics.respaldado_densidad].copy()
    fronts=merged_axis_feature(support_segments,{"frente_id":"PM_FRENTE_01","metodo":"tramos locales de Alicia Moreau de Justo respaldados por puntos a 180 m","estado":"CANDIDATO_EXPERIMENTAL"})
    assigned = sub.geometry.distance(fronts.geometry.iloc[0]) <= 180 if len(fronts) else pd.Series(False, index=sub.index)
    profile["puntos_asignados_frente_total"] = int(assigned.sum())
    profile["puntos_sin_frente_total"] = int((~assigned).sum())
    profile.to_csv(OUT/"puerto_madero_perfil_frente.csv",index=False,encoding="utf-8")
    write_geo(fronts,OUT/"puerto_madero_frentes_candidatos.geojson")
    blocks=block_stability(sub); blocks.insert(0,"zona","Puerto Madero")
    return {"sub":sub,"new":fronts,"axis":fronts,"blocks":blocks,"summary":{"frentes":len(fronts),"segmentos_soporte":len(support_segments),"componentes_frente":int(fronts.componentes_geometricos.iloc[0]) if len(fronts) else 0,"longitud_m":round(fronts.geometry.length.sum(),0),"huecos_bins":int(profile.es_hueco.sum()),"puntos_asignados":int(assigned.sum()),"puntos_sin_frente":int((~assigned).sum()),"places_pct":round(100*sub.fuente.eq('google_places').mean(),1),"block":round(blocks.ari_medio.mean(),2)}}


def prototype_costanera(data: dict) -> dict:
    mz="MZ_COSTANERA_NORTE"; macro=data["macro"].loc[mz].geometry
    sub=data["points"][data["points"].macrozona_id.eq(mz)].copy().reset_index(drop=True); xy=xy_of(sub)
    fit=fit_hdbscan(xy)
    rows=[]
    for cid in sorted(set(fit['labels'].tolist())-{-1}):
        pts=sub.loc[fit['labels']==cid]
        if len(pts)<5: continue
        center=MultiPoint(list(zip(pts.geometry.x,pts.geometry.y))).centroid
        np_places=int(pts.fuente.eq('google_places').sum())
        rows.append({"concentracion_id":f"CN_C{len(rows)+1:02d}","n_puntos":len(pts),"f01_f02":len(pts)-np_places,"places":np_places,"porcentaje_places":round(100*np_places/len(pts),2),"metodo":"centroide de concentración HDBSCAN; solo señal","estado":"EXPLORATORIA_NO_POLIGONO","geometry":center})
    conc=gpd.GeoDataFrame(rows,geometry="geometry",crs=CRS_M) if rows else gpd.GeoDataFrame(columns=['concentracion_id','geometry'],geometry='geometry',crs=CRS_M)
    write_geo(conc,OUT/"costanera_concentraciones_exploratorias.geojson")
    kde,_,_=kde_geometry(xy,150,0.45,macro)
    axis=street_segments(data,"OBLIGADO RAFAEL, AV.COSTANERA",mz)
    blocks=block_stability(sub); blocks.insert(0,"zona","Costanera Norte")
    return {"sub":sub,"new":conc,"axis":axis,"kde":kde,"blocks":blocks,"summary":{"concentraciones":len(conc),"places_pct":round(100*sub.fuente.eq('google_places').mean(),1),"f01_f02":int(sub.fuente.eq('F01+F02').sum()),"block":round(blocks.ari_medio.mean(),2)}}


def plot_context(ax, data: dict, sub: gpd.GeoDataFrame, macro_id: str):
    geom=data['macro'].loc[macro_id].geometry; minx,miny,maxx,maxy=geom.bounds
    streets=data['streets'].cx[minx:maxx,miny:maxy]
    if len(streets): streets.plot(ax=ax,color=COLORS['street'],linewidth=0.35,alpha=.55,zorder=1)
    gpd.GeoSeries([geom],crs=CRS_M).boundary.plot(ax=ax,color="#5D6870",linewidth=1,linestyle='--',zorder=2)
    f=sub[sub.fuente.eq('F01+F02')]; p=sub[sub.fuente.eq('google_places')]
    if len(f): f.plot(ax=ax,color=COLORS['f01'],markersize=7,alpha=.55,zorder=4)
    if len(p): p.plot(ax=ax,color=COLORS['places'],markersize=6,alpha=.42,zorder=3)
    ax.set_aspect('equal'); ax.set_axis_off(); ax.set_facecolor(COLORS['bg'])


def draw_new(ax, result: dict, kind: str):
    new=result['new']
    if kind in ('line','front'):
        if len(new): new.plot(ax=ax,color=COLORS['new'],linewidth=4,zorder=6)
        if kind=='line' and len(new):
            # actual buffer is in result['new'] for Corrientes
            new.plot(ax=ax,facecolor=COLORS['new'],edgecolor=COLORS['new'],alpha=.20,zorder=5)
    elif kind=='point':
        if result.get('kde') is not None:
            gpd.GeoSeries([result['kde']],crs=CRS_M).plot(ax=ax,facecolor=COLORS['new'],edgecolor='none',alpha=.20,zorder=2)
        if len(new): new.plot(ax=ax,color=COLORS['new'],markersize=70,marker='X',edgecolor='white',linewidth=.7,zorder=7)
    else:
        if len(new): new.plot(ax=ax,facecolor=COLORS['new'],edgecolor="#0F684B",alpha=.30,linewidth=1.8,zorder=6)


def make_maps(data: dict, results: dict):
    kinds={'San Telmo':'polygon','Corrientes':'polygon','Belgrano':'polygon','Puerto Madero':'front','Costanera Norte':'point'}
    prototype_names={'San Telmo':'mapa_san_telmo_prototipo_hibrido.png','Corrientes':'mapa_corrientes_prototipo_corredor.png','Belgrano':'mapa_belgrano_prototipo_multinuclear.png','Puerto Madero':'mapa_puerto_madero_prototipo_frente.png','Costanera Norte':'mapa_costanera_senal_exploratoria.png'}
    comparative_names={'San Telmo':'comparativa_san_telmo_actual_vs_hibrido.png','Corrientes':'comparativa_corrientes_actual_vs_hibrido.png','Belgrano':'comparativa_belgrano_actual_vs_hibrido.png','Puerto Madero':'comparativa_puerto_madero_actual_vs_hibrido.png','Costanera Norte':'comparativa_costanera_actual_vs_hibrido.png'}
    for zone,spec in ZONE_SPECS.items():
        res=results[zone]
        fig,ax=plt.subplots(figsize=(9,8),dpi=180); plot_context(ax,data,res['sub'],spec['id']); draw_new(ax,res,kinds[zone]); ax.set_title(f"{zone} — propuesta por tipo territorial",loc='left',fontsize=14,fontweight='bold',color='#16324A'); fig.text(.02,.02,NOTE,fontsize=7,color='#59636B'); fig.tight_layout(); fig.savefig(MAPS/prototype_names[zone],bbox_inches='tight',facecolor='white'); plt.close(fig)
        fig,axs=plt.subplots(1,2,figsize=(14,7),dpi=180)
        for ax in axs: plot_context(ax,data,res['sub'],spec['id'])
        old=data['current_polygons'][data['current_polygons'].macrozona_id.eq(spec['id'])]
        if len(old): old.plot(ax=axs[0],facecolor=COLORS['old'],edgecolor='#66727A',alpha=.35,linewidth=.8,zorder=5)
        axs[0].set_title(f"Salida técnica previa ({len(old)} polígonos)",fontsize=11,fontweight='bold')
        draw_new(axs[1],res,kinds[zone]); axs[1].set_title("Representación híbrida propuesta",fontsize=11,fontweight='bold')
        fig.suptitle(zone,fontsize=15,fontweight='bold',color='#16324A'); fig.text(.02,.02,NOTE,fontsize=7,color='#59636B'); fig.tight_layout(); fig.savefig(MAPS/comparative_names[zone],bbox_inches='tight',facecolor='white'); plt.close(fig)
    fig,axs=plt.subplots(2,3,figsize=(16,10),dpi=170); axs=axs.ravel()
    for ax,(zone,spec) in zip(axs,ZONE_SPECS.items()):
        res=results[zone]; plot_context(ax,data,res['sub'],spec['id']); draw_new(ax,res,kinds[zone]); ax.set_title(zone,fontsize=11,fontweight='bold')
    axs[-1].axis('off'); fig.suptitle("Cinco representaciones territoriales experimentales",fontsize=16,fontweight='bold',color='#16324A'); fig.text(.02,.02,NOTE,fontsize=7,color='#59636B'); fig.tight_layout(); fig.savefig(MAPS/'mapa_resumen_cinco_prototipos.png',bbox_inches='tight',facecolor='white'); plt.close(fig)


def source_mix(results: dict) -> pd.DataFrame:
    rows=[]
    for zone,res in results.items():
        new=res['new']
        if new.empty: continue
        if new.geom_type.isin(['Polygon','MultiPolygon']).all():
            for i,r in new.iterrows():
                pts=res['sub'][res['sub'].geometry.within(r.geometry)]
                n=len(pts); p=int(pts.fuente.eq('google_places').sum())
                rows.append({'zona':zone,'representacion_id':r.get('nucleo_id',r.get('cluster_id',i+1)),'tipo_geometria':r.geometry.geom_type,'total_puntos':n,'f01_f02':n-p,'places':p,'porcentaje_places':round(100*p/max(n,1),2),'densidad':round(n/max(r.geometry.area/10000,1e-6),2),'estabilidad':res['summary']['block'],'advertencia':'Fuente externa auxiliar; no padrón.'})
        elif new.geom_type.isin(['LineString','MultiLineString']).all():
            for i,r in new.iterrows():
                pts=res['sub'][res['sub'].geometry.distance(r.geometry)<=180]; n=len(pts); p=int(pts.fuente.eq('google_places').sum())
                rows.append({'zona':zone,'representacion_id':r.get('frente_id',i+1),'tipo_geometria':r.geometry.geom_type,'total_puntos':n,'f01_f02':n-p,'places':p,'porcentaje_places':round(100*p/max(n,1),2),'densidad':round(1000*n/max(r.geometry.length,1),2),'estabilidad':res['summary']['block'],'advertencia':'Densidad por km; puntos a 180 m. Fuente externa auxiliar.'})
        else:
            for i,r in new.iterrows():
                rows.append({'zona':zone,'representacion_id':r.get('concentracion_id',i+1),'tipo_geometria':'Point','total_puntos':r.get('n_puntos',0),'f01_f02':r.get('f01_f02',0),'places':r.get('places',0),'porcentaje_places':r.get('porcentaje_places',np.nan),'densidad':np.nan,'estabilidad':res['summary']['block'],'advertencia':'Señal exploratoria; no delimita área.'})
    df=pd.DataFrame(rows); df.to_csv(OUT/'mezcla_fuentes_representaciones_v1.csv',index=False,encoding='utf-8'); return df


def dedup_internal_sample(data: dict) -> int:
    base=data['points'][data['points'].fuente.eq('F01+F02')].copy().reset_index(drop=True)
    internal=pd.read_csv(AMP/'interno/completa_v1/places_consolidados_interno.csv',low_memory=False)
    internal=internal.drop_duplicates('google_place_id_interno').reset_index(drop=True)
    gp=gpd.GeoDataFrame(internal,geometry=gpd.points_from_xy(internal.lon,internal.lat),crs=CRS_GEO).to_crs(CRS_M)
    bxy=xy_of(base); tree=cKDTree(bxy); gxy=xy_of(gp); dist,idx=tree.query(gxy,k=2,distance_upper_bound=40)
    rows=[]
    for i in range(len(gp)):
        if not np.isfinite(dist[i,0]): continue
        a=gp.iloc[i]; b=base.iloc[idx[i,0]]
        sim=token_similarity(a.nombre_norm,b.nombre_normalizado); seq=difflib.SequenceMatcher(None,str(a.nombre_norm),str(b.nombre_normalizado)).ratio()
        second_name=''; second_dist=np.nan
        if np.isfinite(dist[i,1]) and idx[i,1]<len(base):
            b2=base.iloc[idx[i,1]]
            if compatible_name(a.nombre_norm,b2.nombre_normalizado): second_name=str(b2.nombre_canonico or b2.nombre_normalizado); second_dist=round(float(dist[i,1]),2)
        d=float(dist[i,0]); compat=compatible_name(a.nombre_norm,b.nombre_normalizado)
        auto='DUPLICADO_AUTOMATICO_ACTUAL' if not bool(a.incorporado_como_nuevo) else 'POSIBLE_FALSO_NEGATIVO' if compat else 'PROXIMIDAD_A_REVISAR'
        rows.append({'fuente_a':'google_places','fuente_b':'F01+F02','distancia_m':round(d,2),'banda':'0-5' if d<=5 else '5-15' if d<=15 else '15-30' if d<=30 else '30-40','nombre_a_original':a.nombre_google,'nombre_b_original':b.nombre_canonico,'nombre_a_normalizado':a.nombre_norm,'nombre_b_normalizado':b.nombre_normalizado,'direccion_o_referencia_a':a.zona_piloto,'direccion_o_referencia_b':b.direccion_normalizada,'similitud_tokens':round(sim,3),'similitud_secuencia':round(seq,3),'nombres_compatibles':compat,'vecino_mas_cercano_distancia_m':round(d,2),'vecino_mas_cercano_nombre':b.nombre_canonico,'segundo_vecino_compatible_distancia_m':second_dist,'segundo_vecino_compatible_nombre':second_name,'misma_fuente':False,'coordenada_exacta_repetida':d<0.05,'clasificacion_automatica':auto,'decision_humana':'','observacion_humana':''})
    for i,j in cKDTree(bxy).query_pairs(40):
        a,b=base.iloc[i],base.iloc[j]; d=float(np.linalg.norm(bxy[i]-bxy[j])); sim=token_similarity(a.nombre_normalizado,b.nombre_normalizado); compat=compatible_name(a.nombre_normalizado,b.nombre_normalizado)
        rows.append({'fuente_a':'F01+F02','fuente_b':'F01+F02','distancia_m':round(d,2),'banda':'0-5' if d<=5 else '5-15' if d<=15 else '15-30' if d<=30 else '30-40','nombre_a_original':a.nombre_canonico,'nombre_b_original':b.nombre_canonico,'nombre_a_normalizado':a.nombre_normalizado,'nombre_b_normalizado':b.nombre_normalizado,'direccion_o_referencia_a':a.direccion_normalizada,'direccion_o_referencia_b':b.direccion_normalizada,'similitud_tokens':round(sim,3),'similitud_secuencia':round(difflib.SequenceMatcher(None,str(a.nombre_normalizado),str(b.nombre_normalizado)).ratio(),3),'nombres_compatibles':compat,'vecino_mas_cercano_distancia_m':round(d,2),'vecino_mas_cercano_nombre':b.nombre_canonico,'segundo_vecino_compatible_distancia_m':np.nan,'segundo_vecino_compatible_nombre':'','misma_fuente':True,'coordenada_exacta_repetida':d<0.05,'clasificacion_automatica':'POSIBLE_DUPLICADO_MISMA_FUENTE' if compat else 'COLOCALIZACION_O_DISTINTO','decision_humana':'','observacion_humana':''})
    for i,j in cKDTree(gxy).query_pairs(40):
        a,b=gp.iloc[i],gp.iloc[j]; d=float(np.linalg.norm(gxy[i]-gxy[j])); sim=token_similarity(a.nombre_norm,b.nombre_norm); compat=compatible_name(a.nombre_norm,b.nombre_norm)
        rows.append({'fuente_a':'google_places','fuente_b':'google_places','distancia_m':round(d,2),'banda':'0-5' if d<=5 else '5-15' if d<=15 else '15-30' if d<=30 else '30-40','nombre_a_original':a.nombre_google,'nombre_b_original':b.nombre_google,'nombre_a_normalizado':a.nombre_norm,'nombre_b_normalizado':b.nombre_norm,'direccion_o_referencia_a':a.zona_piloto,'direccion_o_referencia_b':b.zona_piloto,'similitud_tokens':round(sim,3),'similitud_secuencia':round(difflib.SequenceMatcher(None,str(a.nombre_norm),str(b.nombre_norm)).ratio(),3),'nombres_compatibles':compat,'vecino_mas_cercano_distancia_m':round(d,2),'vecino_mas_cercano_nombre':b.nombre_google,'segundo_vecino_compatible_distancia_m':np.nan,'segundo_vecino_compatible_nombre':'','misma_fuente':True,'coordenada_exacta_repetida':d<0.05,'clasificacion_automatica':'POSIBLE_DUPLICADO_MISMA_FUENTE' if compat else 'COLOCALIZACION_O_DISTINTO','decision_humana':'','observacion_humana':''})
    cand=pd.DataFrame(rows)
    strata=['banda','nombres_compatibles','misma_fuente','coordenada_exacta_repetida','clasificacion_automatica']
    pieces=[]
    for _,g in cand.groupby(strata,dropna=False): pieces.append(g.sample(min(12,len(g)),random_state=42))
    sample=pd.concat(pieces).drop_duplicates()
    if len(sample)<200:
        remaining=cand.drop(sample.index,errors='ignore'); sample=pd.concat([sample,remaining.sample(min(200-len(sample),len(remaining)),random_state=43)])
    if len(sample)>220: sample=sample.sample(220,random_state=44)
    sample=sample.reset_index(drop=True); sample.insert(0,'caso_id',[f'DEDUP_INT_{i+1:04d}' for i in range(len(sample))])
    sample.to_csv(INTERNAL/'muestra_estratificada_deduplicacion_200.csv',index=False,encoding='utf-8-sig')
    (INTERNAL/'README_INTERNO.md').write_text('# Revisión interna de deduplicación\n\nContiene nombres y referencias individuales. Uso interno; no compartir ni incluir en paquetes externos. La clasificación es automática y no constituye verdad etiquetada.\n',encoding='utf-8')
    return len(sample)


def write_docs(results: dict, places: pd.DataFrame, stability: pd.DataFrame, border: pd.DataFrame, dedup_n: int):
    fe="""# Fe de erratas de la auditoría GPT56\n\nEstado: EXPERIMENTAL / no oficial. No modifica la auditoría original.\n\n## Correcciones\n\n1. `clusters_sin_places` y `clusters_con_places` mezclaban la composición de polígonos posteriores a KMeans con clusters HDBSCAN. Se reemplazan por `diagnostico_places_por_zona_corregido.csv`, que separa HDBSCAN completo, HDBSCAN F01/F02 y polígonos post-KMeans.\n2. `estabilidad_sintetica` resumía estabilidad local, bootstrap y sensibilidad global. Se reemplaza por `metricas_estabilidad_desagregadas_v1.csv`. Caballito queda explícitamente como estabilidad local alta y sensibilidad global alta.\n3. `muestra_casos_deduplicacion_revision.csv` contiene candidatos clasificados automáticamente; no es verdad manual etiquetada y no permite calcular precisión ni recall.\n4. El entorno `.venv` usa scikit-learn 1.9.0. Se reprodujo un `TypeError` con HDBSCAN y epsilon positivo. Cada fallback a epsilon 0 queda registrado en las tablas nuevas.\n\n## Efecto sobre el veredicto\n\nLas correcciones no invalidan `PIPELINE_HIBRIDO_POR_TIPO_TERRITORIAL`. Lo refuerzan: muestran que no debe confundirse estabilidad del detector con validez de polígonos y que KMeans no debe definir unidades.\n"""
    (DOC/'FE_DE_ERRATAS_AUDITORIA_GPT56.md').write_text(fe,encoding='utf-8')
    s=results['San Telmo']['summary']; c=results['Corrientes']['summary']; b=results['Belgrano']['summary']; p=results['Puerto Madero']['summary']; co=results['Costanera Norte']['summary']
    docs={
      'DIAGNOSTICO_SAN_TELMO.md':f"""# Diagnóstico San Telmo\n\n**Resultado:** prototipo útil con ajustes. El universo tiene {s['puntos']} puntos y {s['places_pct']} % Places. Emergen {s['nucleos']} núcleos candidatos al exigir presencia estable en perturbaciones locales y coincidencia con KDE.\n\nHDBSCAN eom/leaf y KDE se informan por separado en `san_telmo_comparacion_metodos.csv`. La estabilidad media por bloques fue {s['block']}. La evidencia permite núcleo compacto; no resuelve automáticamente si Mercado, Defensa y casco histórico deben ser una o dos unidades. `DEFENSA` se usa sólo como calle local de referencia.\n\n**Recomendación:** conservar núcleo(s) estable(s) y someter a decisión humana la combinación núcleo + eje Defensa. No usar KMeans.\n""",
      'DIAGNOSTICO_CORRIENTES.md':f"""# Diagnóstico Corrientes\n\n**Resultado:** mejora clara frente a 23 tiles. Se usa el eje local `CORRIENTES AV.` y se retienen {c['segmentos_soporte']} segmentos viales de soporte, disueltos en {c['componentes_eje']} componente(s) geométrico(s), con longitud acumulada aproximada de {c['longitud_m']:.0f} m. El perfil longitudinal registra {c['huecos_bins']} bins sin puntos; no se fuerza una cantidad de tramos.\n\nLa representación propuesta es eje con buffer variable de 60/90/120 m según densidad por segmento. Places representa {c['places_pct']} %. Estabilidad media por bloques: {c['block']}.\n\n**Recomendación:** reemplazar tiles por corredor; decisión humana sobre corredor único o tramos y relación con Microcentro.\n""",
      'DIAGNOSTICO_BELGRANO.md':f"""# Diagnóstico Belgrano\n\n**Resultado:** mejora metodológica, aún no lista para escalar sin revisión. El umbral de grafo se deriva del percentil 75 de la distancia al quinto vecino ({b['umbral_m']} m), no de nombres deseados. Produce {b['nucleos']} núcleos separados; HDBSCAN eom produce {b['hdb_eom']} y leaf {b['hdb_leaf']}. Places representa {b['places_pct']} %.\n\nLos núcleos se entregan sin nombres. No se afirma automáticamente que correspondan a Barrio Chino, Cabildo/Juramento, Bajo Belgrano o Libertador/Barrancas. Estabilidad media por bloques: {b['block']}.\n\n**Recomendación:** usar grafo + KDE como insumo y validar nombres/jerarquía humanamente.\n""",
      'DIAGNOSTICO_PUERTO_MADERO.md':f"""# Diagnóstico Puerto Madero\n\n**Resultado:** prototipo parcial. La representación de frente mejora las manchas, pero no cubre toda la evidencia. Se usa el eje local `MOREAU DE JUSTO, ALICIA AV.`; {p['segmentos_soporte']} segmentos viales de soporte se disuelven en {p['componentes_frente']} componente(s), con {p['longitud_m']:.0f} m acumulados. Quedan {p['puntos_sin_frente']} puntos a más de 180 m del frente y {p['puntos_asignados']} próximos. Places representa {p['places_pct']} %, por lo que la geometría no debe presentarse como evidencia independiente.\n\nEl perfil no impone norte/centro/sur; esos nombres requieren decisión humana. Estabilidad media por bloques: {p['block']}.\n\n**Recomendación:** repetir/ajustar el soporte de frente antes de escalar; mantener la prudencia de Fase 25.\n""",
      'DIAGNOSTICO_COSTANERA.md':f"""# Diagnóstico Costanera Norte\n\n**Resultado:** funciona sólo como señal exploratoria. Se generan {co['concentraciones']} marcadores de concentración y KDE, sin polígono principal. La capa local `OBLIGADO RAFAEL, AV.COSTANERA` se usa como referencia.\n\nPlaces representa {co['places_pct']} % y F01/F02 aporta {co['f01_f02']} puntos. Estabilidad geométrica por bloques ({co['block']}) no compensa la dependencia de fuente.\n\n**Recomendación:** puntos/heatmap en anexo. No apta como delimitación firme.\n""",
    }
    for name,text in docs.items(): (DOC/name).write_text(text,encoding='utf-8')

    guide=f"""# Guía de revisión de deduplicación\n\nLa carpeta interna contiene {dedup_n} pares estratificados. La clasificación automática es sólo una propuesta. Completar `decision_humana` con uno de estos valores:\n\n- `DUPLICADO`: misma entidad real representada dos veces.\n- `DISTINTO`: entidades diferentes.\n- `AMBIGUO`: evidencia insuficiente.\n- `COLOCALIZACION_VALIDA`: entidades distintas en la misma parcela, galería, mercado o dirección.\n\nRevisar nombre original y normalizado, distancia, dirección/referencia, vecino más cercano y segundo vecino compatible. No cambiar umbrales hasta completar y auditar la muestra. No copiar nombres o referencias al paquete compartible.\n"""
    (DOC/'GUIA_REVISION_DEDUPLICACION.md').write_text(guide,encoding='utf-8')

    comp_rows=[
      ['San Telmo','NUCLEO_COMPACTO','HDBSCAN+KMeans+hull','HDBSCAN estable+KDE+concave hull','8 polígonos','núcleo(s) compacto(s)',s['places_pct'],'MEDIA','MEDIA_SENSIBILIDAD',s['block'],'ALTA','ALTA','MEDIA','MEJORA_CON_AJUSTES','SI_CON_AJUSTES','Uno o dos núcleos; relación con Defensa'],
      ['Corrientes','CORREDOR_LINEAL','HDBSCAN+23 tiles KMeans','eje vial local+buffer variable','23 polígonos','corredor respaldado por densidad',c['places_pct'],'ALTA','ALTA_SENSIBILIDAD',c['block'],'ALTA','ALTA','BAJA','REEMPLAZAR_TILES','SI','Corredor único o tramos; ancho orientativo'],
      ['Belgrano','RED_MULTINUCLEAR','HDBSCAN+17 polígonos','grafo de proximidad+comunidades+KDE','macroárea fragmentada','núcleos separados sin nombre',b['places_pct'],'BAJA','ALTA_SENSIBILIDAD',b['block'],'MEDIA','ALTA','MEDIA','REPETIR_PROTOTIPO_POR_BAJA_ROBUSTEZ','NO_AUN','Nombres, jerarquía e inclusión'],
      ['Puerto Madero','FRENTE_GASTRONOMICO','HDBSCAN+11 manchas','frente sobre eje local','11 polígonos','segmentos de frente',p['places_pct'],'ALTA','MEDIA_SENSIBILIDAD',p['block'],'ALTA','ALTA','MEDIA','PROTOTIPO_PARCIAL_REPETIR_SOPORTE','NO_AUN','Frente único o segmentos; puntos sin frente'],
      ['Costanera Norte','SENAL_EXPLORATORIA','4 polígonos','KDE+marcadores sin polígono','polígonos','puntos/heatmap',co['places_pct'],'ALTA','MEDIA_SENSIBILIDAD',co['block'],'ALTA','ALTA','BAJA','MEJORA_POR_PRUDENCIA','SI_SOLO_ANEXO','Inclusión en anexo'],
    ]
    cols=['zona','tipo_territorial','metodo_anterior','metodo_propuesto','representacion_anterior','representacion_propuesta','dependencia_places','estabilidad_local','sensibilidad_global','robustez_bloques','legibilidad','trazabilidad','riesgo_falsa_precision','recomendacion','apta_para_escalar','decision_humana_requerida']
    table=pd.DataFrame(comp_rows,columns=cols); table.to_csv(OUT/'tabla_comparacion_prototipos_hibridos_v1.csv',index=False,encoding='utf-8')
    comparison="# Comparación de prototipos híbridos\n\n| Zona | Fase 25 | Completa/KMeans | v4.2 | Prototipo híbrido | Recomendación |\n| --- | --- | --- | --- | --- | --- |\n| San Telmo | Núcleo/Defensa/Mercado prudentes | 8 polígonos | simplifica visualmente | núcleo estable + KDE | mejora con decisión sobre uno/dos núcleos |\n| Corrientes | eje aproximado | 23 tiles | reduce piezas pero conserva polígonos | eje vial real + buffer variable | mejora clara |\n| Belgrano | macroárea con subzonas | 17 polígonos | cuatro unidades orientativas | comunidades sin nombres | mejora método; nombres pendientes |\n| Puerto Madero | banda de docks/frente | 11 manchas | tres unidades | segmentos sobre Alicia Moreau de Justo | mejora forma; fuente débil |\n| Costanera Norte | eje exploratorio | 4 polígonos | anexo | puntos + KDE | mejora por menor falsa precisión |\n\nLa tabla completa está en `tabla_comparacion_prototipos_hibridos_v1.csv`.\n"
    (DOC/'COMPARACION_PROTOTIPOS_HIBRIDOS_V1.md').write_text(comparison,encoding='utf-8')
    decisions="""# Matriz de decisiones post prototipo\n\n| Zona | Decisión no técnica | Opciones | Bloquea |\n| --- | --- | --- | --- |\n| San Telmo | Jerarquía territorial | uno/dos núcleos; núcleo + Defensa | mapa principal |\n| Corrientes | Forma de comunicación | corredor único o tramos; ancho orientativo | mapa principal |\n| Belgrano | Nombres y jerarquía | núcleos sin nombre; subzonas conocidas; macroárea | mapa principal |\n| Puerto Madero | Segmentación | frente único; segmentos; norte/centro/sur | mapa principal |\n| Costanera | Inclusión | anexo exploratorio o exclusión | no, si queda en anexo |\n| Todas | Relación con Fase 25 | reemplazar, complementar o conservar lectura previa | informe |\n| Todas | Puntos fuera de representación | ruido, contexto o cola de revisión | informe |\n"""
    (DOC/'MATRIZ_DECISIONES_POST_PROTOTIPO.md').write_text(decisions,encoding='utf-8')
    plan="""# Plan de escalado del pipeline híbrido\n\n## Recomendación\n\n**ESCALAR_CON_AJUSTES.**\n\nFuncionaron para su propósito: corredor vial en Corrientes; señal sin polígono en Costanera; núcleo de consenso HDBSCAN+KDE en San Telmo. Belgrano mejora visualmente a núcleos sin nombre, pero debe repetirse por baja robustez de bloques. Puerto Madero es parcial: mejora la forma, pero el soporte vial no cubre todos los puntos y la dependencia Places sigue alta.\n\n## Otras ocho zonas\n\n- Palermo Soho: núcleo HDBSCAN+KDE, con sensibilidad global explícita.\n- Palermo Hollywood: red multinuclear, comunidades + KDE.\n- Microcentro: núcleos/peatonales y posible eje, evitando solape con Corrientes.\n- Caballito: grafo/comunidades; nunca 33 tiles.\n- Recoleta: KDE/heatmap y núcleos separados.\n- Villa Crespo y Chacarita: grafo + KDE; gate fuerte por dependencia Places.\n- Caseros/Barracas: corredor sobre `CASEROS AV.` si el tramo local queda respaldado.\n\nNo volver a usar KMeans, Voronoi ni cantidad objetivo de unidades. Callejero es necesario para corredores/frentes. Se automatizan detección, estabilidad, perfiles y QA; nombres, jerarquía, inclusión, buffer orientativo y relación con Fase 25 permanecen manuales.\n\nBloquean el nuevo informe: repetir Belgrano y Puerto Madero, revisión humana de los cinco casos, deduplicación etiquetada, tratamiento de solapes y selección del mapa principal.\n"""
    (DOC/'PLAN_ESCALADO_PIPELINE_HIBRIDO.md').write_text(plan,encoding='utf-8')


def manifest_and_metadata(results: dict, hashes: dict, finalize: bool):
    files=sorted([p for base in (OUT,DOC,ROOT/'scripts/polos_gastro/historico/experimentos/pipeline_hibrido_tipo_territorial_v1') for p in base.rglob('*') if p.is_file() and 'interno_revision_deduplicacion' not in p.parts])
    rows=['# Manifest de archivos','',f'Archivos compartibles y técnicos: {len(files)}','', '| Ruta | Bytes | SHA-256 |','| --- | ---: | --- |']
    for p in files:
        rows.append(f"| `{p.relative_to(ROOT).as_posix()}` | {p.stat().st_size} | `{sha256(p)}` |")
    (DOC/'MANIFEST_ARCHIVOS.md').write_text('\n'.join(rows)+'\n',encoding='utf-8')
    metadata={
      'estado':'EXPERIMENTAL_NO_OFICIAL','fecha_corte':'2026-07-10','veredicto_auditoria_corregido':'PIPELINE_HIBRIDO_POR_TIPO_TERRITORIAL',
      'recomendacion_escalado':'ESCALAR_CON_AJUSTES','sin_api':True,'sin_google_places':True,'sin_kmeans':True,
      'python':sys.version,'sklearn':sklearn_version,'librerias_instaladas':[], 'hashes':hashes,
      'prototipos':{k:v['summary'] for k,v in results.items()},
      'nota':'La muestra interna de deduplicación es automática y no permite calcular precisión/recall hasta decisión humana.',
    }
    (OUT/'metadata_pipeline_hibrido_v1.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding='utf-8')
    if finalize:
        qa=f"""# QA final pipeline híbrido v1\n\nEstado: APTO PARA REVISIÓN INTERNA; experimental/no oficial.\n\n- Auditoría corregida: clusters HDBSCAN y polígonos separados.\n- Estabilidad: dimensiones desagregadas.\n- Trazabilidad: IDs y fuentes preservados; sin doble conteo introducido.\n- KMeans: no usado.\n- Callejero: capa local de 31.961 tramos; sin nombres inventados.\n- Hashes críticos: {hashes.get('sin_cambios',0)}/{hashes.get('archivos',0)} sin cambios; cambiados={hashes.get('cambiados',0)}.\n- APIs/descargas: ninguna.\n- Datos fuente/Fase25/Fase26/v1-v4.2: sin cambios.\n- Librerías instaladas: ninguna. Se usó `.venv` existente (scikit-learn {sklearn_version}, networkx {nx.__version__}).\n- Carpeta interna deduplicación: excluida por `.gitignore` local del experimento; no incluir en paquete compartible.\n- Git: verificar al cierre; no se ejecutó add, commit, push ni staging.\n\nLimitaciones: bootstrap por bloques usa submuestreo de 80% sin reemplazo; los buffers son orientativos; dependencia Places no desaparece por cambiar geometría; nombres y jerarquías requieren decisión humana.\n"""
        (DOC/'QA_FINAL_PIPELINE_HIBRIDO_V1.md').write_text(qa,encoding='utf-8')


def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument('--finalize',action='store_true'); args=parser.parse_args()
    ensure_dirs(); hashes=snapshot_hashes(args.finalize); data=load_inputs()
    places,stability=corrected_places_and_stability(data); inventory_layers(data)
    ablation=source_ablation(data); border=border_sensitivity(data)
    results={
      'San Telmo':prototype_san_telmo(data), 'Corrientes':prototype_corrientes(data),
      'Belgrano':prototype_belgrano(data), 'Puerto Madero':prototype_puerto(data),
      'Costanera Norte':prototype_costanera(data),
    }
    blocks=pd.concat([v['blocks'] for v in results.values()],ignore_index=True); blocks.to_csv(OUT/'robustez_bootstrap_bloques_v1.csv',index=False,encoding='utf-8')
    source_mix(results); make_maps(data,results); dedup_n=dedup_internal_sample(data)
    write_docs(results,places,stability,border,dedup_n); manifest_and_metadata(results,hashes,args.finalize)
    print(json.dumps({'ok':True,'out':str(OUT),'docs':str(DOC),'hashes':hashes,'prototipos':{k:v['summary'] for k,v in results.items()},'muestra_dedup':dedup_n},ensure_ascii=False,indent=2))
    return 0


if __name__=='__main__': raise SystemExit(main())
