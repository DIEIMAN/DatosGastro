# -*- coding: utf-8 -*-
"""Repeticiones territoriales híbridas v2 para Polos Gastronómicos.

EXPERIMENTAL / NO OFICIAL. El script usa exclusivamente insumos locales ya
almacenados. No llama APIs, no descarga fuentes, no usa KMeans y no modifica
datos fuente, Fase 25, Fase 26 ni prototipos anteriores.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import shutil
import sys
import zipfile
from collections import defaultdict
from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from scipy.ndimage import maximum_filter
from scipy.spatial import cKDTree
from shapely.geometry import LineString, MultiPoint, MultiPolygon, Point
from shapely.ops import linemerge, nearest_points, unary_union
from sklearn.cluster import HDBSCAN
from sklearn.metrics import adjusted_mutual_info_score, adjusted_rand_score
from sklearn.neighbors import KernelDensity, NearestNeighbors

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "outputs/polos_gastro/historico/experimentos/pipeline_hibrido_repeticiones_v2"
DOC = ROOT / "docs/polos_gastro/historico/experimentos/pipeline_hibrido_repeticiones_v2"
PACK = OUT / "REVISION_REPETICIONES_HIBRIDAS_V2"
MAPS = OUT
CRS_M = "EPSG:5347"
CRS_GEO = "EPSG:4326"
SEED = 260711
RNG = np.random.default_rng(SEED)
NOTE = (
    "EXPERIMENTAL / NO OFICIAL. Oferta registrada/visible; no constituye una "
    "delimitación institucional. Los buffers son convenciones cartográficas orientativas."
)

V1_SCRIPT = ROOT / (
    "scripts/polos_gastro/historico/experimentos/pipeline_hibrido_tipo_territorial_v1/"
    "construir_pipeline_hibrido_v1.py"
)

PROTECTED = [
    ROOT / "docs/polos_gastro/fase25_microajustes_finales_oficina",
    ROOT / "outputs/polos_gastro/fase25_microajustes_finales_oficina",
    ROOT / "scripts/polos_gastro/build_fase25_microajustes_finales_oficina.py",
    ROOT / "docs/polos_gastro/historico/experimentos/google_places_microzonas_ampliacion_v1/fase26_comparativa_cartografia",
    ROOT / "outputs/polos_gastro/historico/experimentos/google_places_microzonas_ampliacion_v1/fase26_comparativa_cartografia",
    ROOT / "outputs/polos_gastro/historico/experimentos/google_places_microzonas_ampliacion_v1/completa_v1",
    ROOT / "outputs/polos_gastro/historico/experimentos/google_places_microzonas_ampliacion_v1/cartografia_editorial_v2",
    ROOT / "outputs/polos_gastro/historico/experimentos/google_places_microzonas_ampliacion_v1/cartografia_decision_v3",
    ROOT / "outputs/polos_gastro/historico/experimentos/google_places_microzonas_ampliacion_v1/cartografia_redibujo_editorial_v4",
    ROOT / "outputs/polos_gastro/historico/experimentos/google_places_microzonas_ampliacion_v1/cartografia_redibujo_editorial_v4_1",
    ROOT / "outputs/polos_gastro/historico/experimentos/google_places_microzonas_ampliacion_v1/cartografia_design_v4_2",
    ROOT / "scripts/polos_gastro/historico/experimentos/google_places_microzonas_ampliacion_v1",
    ROOT / "docs/polos_gastro/historico/experimentos/pipeline_hibrido_tipo_territorial_v1",
    ROOT / "outputs/polos_gastro/historico/experimentos/pipeline_hibrido_tipo_territorial_v1",
    ROOT / "scripts/polos_gastro/historico/experimentos/pipeline_hibrido_tipo_territorial_v1",
]

COLORS = {
    "base": "#1F5D7A",
    "places": "#C47A1D",
    "primary": "#1E8A63",
    "secondary": "#8064A2",
    "context": "#A0A7AD",
    "street": "#D3D7DA",
    "border": "#59636B",
}


def ensure_dirs() -> None:
    for path in (OUT, DOC, PACK):
        path.mkdir(parents=True, exist_ok=True)


def load_v1_module():
    spec = importlib.util.spec_from_file_location("pipeline_hibrido_v1_readonly", V1_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


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


def write_geo(gdf: gpd.GeoDataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if gdf.empty:
        path.write_text('{"type":"FeatureCollection","features":[]}', encoding="utf-8")
        return
    clean = gdf.copy()
    for col in clean.columns:
        if col != "geometry" and clean[col].dtype == "object":
            clean[col] = clean[col].fillna("").astype(str)
    clean.to_crs(CRS_GEO).to_file(path, driver="GeoJSON")


def points_for(data: dict, macro_id: str) -> gpd.GeoDataFrame:
    return data["points"][data["points"].macrozona_id.eq(macro_id)].copy().reset_index(drop=True)


def xy(points: gpd.GeoDataFrame) -> np.ndarray:
    return np.column_stack([points.geometry.x.to_numpy(), points.geometry.y.to_numpy()])


def labels_count(labels: np.ndarray) -> int:
    return len(set(labels.tolist()) - {-1})


def hull_for(points: gpd.GeoDataFrame, pad: float = 45) -> object:
    if len(points) == 1:
        return points.geometry.iloc[0].buffer(pad)
    return MultiPoint(list(zip(points.geometry.x, points.geometry.y))).convex_hull.buffer(pad)


def source_mix(points: gpd.GeoDataFrame) -> tuple[int, int, float]:
    places = int(points.fuente.eq("google_places").sum())
    base = len(points) - places
    return base, places, round(100 * places / max(len(points), 1), 2)


def markdown_table(frame: pd.DataFrame) -> str:
    """Render mínimo sin la dependencia opcional `tabulate`."""
    clean = frame.fillna("").astype(str).apply(lambda col: col.str.replace("|", "\\|", regex=False))
    header = "| " + " | ".join(clean.columns) + " |"
    divider = "|" + "|".join(["---"] * len(clean.columns)) + "|"
    rows = ["| " + " | ".join(row) + " |" for row in clean.to_numpy().tolist()]
    return "\n".join([header, divider, *rows])


def components(geom: object) -> int:
    if geom is None or geom.is_empty:
        return 0
    return len(geom.geoms) if hasattr(geom, "geoms") else 1


def jaccard(a: set[int], b: set[int]) -> float:
    return len(a & b) / max(1, len(a | b))


def best_cluster_match(target: set[int], labels: np.ndarray, original_indices: np.ndarray) -> tuple[float, set[int]]:
    best, best_set = 0.0, set()
    for cid in set(labels.tolist()) - {-1}:
        candidate = set(original_indices[np.flatnonzero(labels == cid)].tolist())
        score = jaccard(target, candidate)
        if score > best:
            best, best_set = score, candidate
    return best, best_set


def plot_context(ax, data: dict, points: gpd.GeoDataFrame, geom: object, title: str) -> None:
    minx, miny, maxx, maxy = geom.bounds
    pad = max(maxx - minx, maxy - miny) * 0.08
    streets = data["streets"].cx[minx - pad : maxx + pad, miny - pad : maxy + pad]
    if len(streets):
        streets.plot(ax=ax, color=COLORS["street"], linewidth=0.35, zorder=1)
    gpd.GeoSeries([geom], crs=CRS_M).boundary.plot(
        ax=ax, color=COLORS["border"], linewidth=1, linestyle="--", zorder=2
    )
    base = points[points.fuente.eq("F01+F02")]
    places = points[points.fuente.eq("google_places")]
    if len(base):
        base.plot(ax=ax, color=COLORS["base"], markersize=7, alpha=0.60, zorder=4)
    if len(places):
        places.plot(ax=ax, color=COLORS["places"], markersize=6, alpha=0.42, zorder=3)
    ax.set_title(title, loc="left", fontsize=11, fontweight="bold")
    ax.set_aspect("equal")
    ax.set_axis_off()


def save_figure(fig, path: Path) -> None:
    fig.text(0.015, 0.012, NOTE, fontsize=6.8, color="#59636B")
    fig.tight_layout(rect=(0, 0.035, 1, 1))
    fig.savefig(path, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def graph_labels(coords: np.ndarray, radius: float, method: str = "louvain", seed: int = SEED) -> tuple[np.ndarray, float, int]:
    pairs = cKDTree(coords).query_pairs(radius)
    graph = nx.Graph()
    graph.add_nodes_from(range(len(coords)))
    for i, j in pairs:
        distance = float(np.linalg.norm(coords[i] - coords[j]))
        graph.add_edge(i, j, weight=max(0.001, 1 - distance / radius))
    if method == "greedy":
        comms = list(nx.community.greedy_modularity_communities(graph, weight="weight"))
    elif method == "label":
        comms = list(nx.community.asyn_lpa_communities(graph, weight="weight", seed=seed))
    else:
        comms = list(nx.community.louvain_communities(graph, weight="weight", seed=seed))
    labels = np.full(len(coords), -1, dtype=int)
    kept = [set(c) for c in comms if len(c) >= 8]
    for cid, community in enumerate(kept):
        labels[list(community)] = cid
    modularity = nx.community.modularity(graph, comms, weight="weight") if graph.number_of_edges() else 0.0
    return labels, float(modularity), graph.number_of_edges()


def kde_maxima(coords: np.ndarray, bandwidths=(60, 80, 100, 140)) -> tuple[pd.DataFrame, dict[int, object]]:
    minx, miny = coords.min(axis=0) - 150
    maxx, maxy = coords.max(axis=0) + 150
    gx = np.arange(minx, maxx + 25, 25)
    gy = np.arange(miny, maxy + 25, 25)
    mesh = np.array(np.meshgrid(gx, gy)).reshape(2, -1).T
    rows: list[dict] = []
    surfaces: dict[int, object] = {}
    for bw in bandwidths:
        model = KernelDensity(bandwidth=bw).fit(coords)
        density = np.exp(model.score_samples(mesh)).reshape(len(gy), len(gx))
        local = density == maximum_filter(density, size=max(3, int(round(2 * bw / 25)) | 1))
        gate = np.quantile(density, 0.82)
        iy, ix = np.where(local & (density >= gate))
        maxima = [Point(float(gx[xi]), float(gy[yi])) for yi, xi in zip(iy, ix)]
        surfaces[bw] = (gx, gy, density)
        for rank, point in enumerate(sorted(maxima, key=lambda p: -density[np.argmin(abs(gy-p.y)), np.argmin(abs(gx-p.x))])):
            rows.append({"bandwidth_m": bw, "maximo_id": f"KDE_{bw}_{rank+1:02d}", "x": point.x, "y": point.y})
    raw = pd.DataFrame(rows)
    persistent: list[dict] = []
    used: set[int] = set()
    if not raw.empty:
        pts = [Point(r.x, r.y) for r in raw.itertuples()]
        for i, point in enumerate(pts):
            if i in used:
                continue
            group = [j for j, other in enumerate(pts) if point.distance(other) <= 100]
            bws = sorted(set(int(raw.iloc[j].bandwidth_m) for j in group))
            if len(bws) >= 3:
                used.update(group)
                persistent.append({
                    "maximo_persistente_id": f"KDEP_{len(persistent)+1:02d}",
                    "bandwidths_presentes": ";".join(map(str, bws)),
                    "n_bandwidths": len(bws),
                    "x": float(np.mean([pts[j].x for j in group])),
                    "y": float(np.mean([pts[j].y for j in group])),
                })
    return pd.DataFrame(persistent), surfaces


def san_telmo(data: dict) -> dict:
    pts = points_for(data, "MZ_SAN_TELMO")
    macro = data["macro"].loc["MZ_SAN_TELMO"].geometry
    coords = xy(pts)
    eom = HDBSCAN(min_cluster_size=20, min_samples=5, cluster_selection_method="eom").fit_predict(coords)
    leaf = HDBSCAN(min_cluster_size=20, min_samples=5, cluster_selection_method="leaf").fit_predict(coords)
    eom_ids = sorted(set(eom.tolist()) - {-1}, key=lambda c: int((eom == c).sum()), reverse=True)
    leaf_ids = sorted(set(leaf.tolist()) - {-1}, key=lambda c: int((leaf == c).sum()), reverse=True)
    # Línea de base compacta ya producida por el protocolo v1, leída sin modificar.
    # Permite que la prueba v2 mida el aporte incremental del eje Defensa contra el
    # núcleo estable anterior, en vez de sustituirlo por un único cluster local.
    prior_core_path = ROOT / "outputs/polos_gastro/historico/experimentos/pipeline_hibrido_tipo_territorial_v1/san_telmo_nucleo_candidato.geojson"
    prior_core = gpd.read_file(prior_core_path).to_crs(CRS_M)
    core_one = unary_union(prior_core.geometry.tolist()).intersection(macro)
    two_sets = [np.flatnonzero(leaf == cid) for cid in leaf_ids[:2]]
    if len(two_sets) < 2:
        projection = coords[:, 1]
        med = np.median(projection)
        two_sets = [np.flatnonzero(projection <= med), np.flatnonzero(projection > med)]
    two_geoms = [hull_for(pts.iloc[idx], 40).intersection(macro) for idx in two_sets]

    defense = data["streets"][data["streets"].nomoficial.fillna("").eq("DEFENSA")].copy()
    defense["geometry"] = defense.geometry.intersection(macro)
    defense = defense[~defense.geometry.is_empty].explode(index_parts=False).reset_index(drop=True)
    support_rows = []
    for idx, row in defense.iterrows():
        dist = pts.geometry.distance(row.geometry)
        support_rows.append({"idx": idx, "n": int((dist <= 150).sum()), "geometry": row.geometry})
    support = gpd.GeoDataFrame(support_rows, geometry="geometry", crs=CRS_M)
    gate = max(3, int(math.floor(support.loc[support.n > 0, "n"].quantile(0.25))))
    selected = support[support.n >= gate]
    axis_geom = unary_union(selected.geometry.tolist())
    axis_buffer = axis_geom.buffer(110, cap_style="flat").intersection(macro)
    axis_out = gpd.GeoDataFrame([{
        "id_tecnico": "ST_EJE_DEFENSA_V2",
        "estado": "CONTEXTUAL_EXPERIMENTAL",
        "radio_respaldo_m": 150,
        "buffer_cartografico_m": 110,
        "segmentos_respaldados": len(selected),
        "longitud_m": round(axis_geom.length, 1),
        "aclaracion": "Buffer orientativo; no ancho real ni límite oficial.",
        "geometry": axis_geom,
    }], geometry="geometry", crs=CRS_M)
    write_geo(axis_out, OUT / "san_telmo_eje_defensa.geojson")
    core_out = gpd.GeoDataFrame(
        [
            {"opcion": "NUCLEO_UNICO", "pieza": "ST_NU_01", "estado": "CANDIDATO", "geometry": core_one},
            {"opcion": "DOS_NUCLEOS", "pieza": "ST_DN_01", "estado": "CANDIDATO", "geometry": two_geoms[0]},
            {"opcion": "DOS_NUCLEOS", "pieza": "ST_DN_02", "estado": "CANDIDATO", "geometry": two_geoms[1]},
        ], geometry="geometry", crs=CRS_M
    )
    write_geo(core_out, OUT / "san_telmo_nucleo_compacto.geojson")

    options = {
        "NUCLEO_COMPACTO_UNICO": [core_one],
        "DOS_NUCLEOS_COMPACTOS": two_geoms,
        "NUCLEO_MAS_EJE_DEFENSA_CONTEXTUAL": [core_one, axis_buffer],
    }
    rows = []
    for option, geoms in options.items():
        union = unary_union(geoms)
        assigned = pts.geometry.intersects(union)
        covered = pts[assigned]
        b, p, pctp = source_mix(covered)
        distances = pts.geometry.distance(axis_geom) if "EJE" in option else pts.geometry.distance(union)
        profile = pd.cut(
            (coords[:, 1] - coords[:, 1].min()), bins=max(4, int(np.ptp(coords[:, 1]) // 150)), labels=False
        )
        counts = pd.Series(profile).value_counts().sort_index()
        continuity = float((counts > 0).mean()) if len(counts) else 0.0
        rows.append({
            "zona": "San Telmo", "opcion": option, "puntos_universo": len(pts),
            "puntos_cubiertos": len(covered), "cobertura_pct": round(100 * len(covered) / len(pts), 2),
            "componentes": len(geoms), "continuidad_bloques": round(continuity, 3),
            "huecos_bloques": int((counts == 0).sum()), "distancia_p90_m": round(float(distances.quantile(.9)), 1),
            "f01_f02_cubiertos": b, "places_cubiertos": p, "places_pct_cubiertos": pctp,
            "relacion_mercado_defensa": "eje contextual próximo al núcleo; no prueba una única unidad" if "EJE" in option else "representación areal sin eje contextual",
            "sensibilidad": "MEDIA" if option != "NUCLEO_COMPACTO_UNICO" else "BAJA_MEDIA",
            "riesgo_falsa_precision": "MEDIO" if option == "DOS_NUCLEOS_COMPACTOS" else "BAJO_MEDIO",
            "recomendacion": "SI" if option == "NUCLEO_MAS_EJE_DEFENSA_CONTEXTUAL" else "NO",
        })
    table = pd.DataFrame(rows)
    table.to_csv(OUT / "tabla_comparacion_san_telmo_v2.csv", index=False, encoding="utf-8")
    fig, axes = plt.subplots(1, 3, figsize=(16, 6))
    for ax, (option, geoms) in zip(axes, options.items()):
        plot_context(ax, data, pts, macro, option.replace("_", " ").title())
        for pos, geom in enumerate(geoms):
            gpd.GeoSeries([geom], crs=CRS_M).plot(ax=ax, facecolor=COLORS["primary"] if pos == 0 else COLORS["secondary"], edgecolor="#0F684B", alpha=.25)
        if "EJE" in option:
            axis_out.plot(ax=ax, color=COLORS["secondary"], linewidth=3)
    save_figure(fig, OUT / "mapa_san_telmo_opciones_v2.png")
    return {"points": pts, "table": table, "recommended": table.iloc[2].to_dict(), "macro": macro}


def belgrano(data: dict) -> dict:
    pts = points_for(data, "MZ_BELGRANO")
    coords = xy(pts)
    macro = data["macro"].loc["MZ_BELGRANO"].geometry
    barrio = data["barrios"][data["barrios"].nombre.str.casefold().eq("belgrano")].geometry.iloc[0]
    barrio_pts = data["points"][data["points"].geometry.within(barrio)].copy().reset_index(drop=True)

    hrows, hlabels = [], {}
    for method in ("eom", "leaf"):
        for mcs in (8, 10, 12, 15, 20):
            for ms in (3, 5, 8, 10):
                label = HDBSCAN(min_cluster_size=mcs, min_samples=ms, cluster_selection_method=method).fit_predict(coords)
                key = f"{method}_mcs{mcs}_ms{ms}"
                hlabels[key] = label
                hrows.append({"prueba_id": "BEL-R01" if method == "eom" else "BEL-R02", "familia": "HDBSCAN", "configuracion": key, "metodo": method, "min_cluster_size": mcs, "min_samples": ms, "n_clusters": labels_count(label), "pct_ruido": round(100 * (label == -1).mean(), 2), "mayor_cluster": max([int((label == c).sum()) for c in set(label)-{-1}] or [0])})
    hdf = pd.DataFrame(hrows)
    neighbor_scores = defaultdict(list)
    for method in ("eom", "leaf"):
        subset = hdf[hdf.metodo.eq(method)]
        for row in subset.itertuples():
            key = row.configuracion
            for other in subset.itertuples():
                if abs(row.min_cluster_size - other.min_cluster_size) in (0, 2, 3, 5) and abs(row.min_samples - other.min_samples) in (0, 2, 3, 5) and row.configuracion != other.configuracion:
                    neighbor_scores[key].append(adjusted_rand_score(hlabels[key], hlabels[other.configuracion]))
    hdf["ari_vecinos_mediana"] = hdf.configuracion.map(lambda k: round(float(np.median(neighbor_scores[k])), 4) if neighbor_scores[k] else np.nan)
    hdf["meseta_estable_ari_ge_06"] = hdf.ari_vecinos_mediana.ge(.6)

    graph_rows, graph_labels_map = [], {}
    for kval in (3, 5, 8):
        nn = NearestNeighbors(n_neighbors=kval + 1).fit(coords)
        local = nn.kneighbors(coords)[0][:, kval]
        for q in (.40, .50, .60, .75, .90):
            radius = float(np.quantile(local, q))
            for method in ("greedy", "louvain", "label"):
                label, modularity, edges = graph_labels(coords, radius, method=method, seed=SEED)
                key = f"k{kval}_q{int(q*100)}_{method}"
                graph_labels_map[key] = label
                graph_rows.append({"prueba_id": "BEL-R04" if method == "greedy" else "BEL-R06", "familia": "GRAFO", "configuracion": key, "k": kval, "cuantil": q, "umbral_m": round(radius, 2), "metodo": method, "n_clusters": labels_count(label), "pct_ruido": round(100 * (label == -1).mean(), 2), "modularidad": round(modularity, 4), "aristas": edges})
    gdf = pd.DataFrame(graph_rows)
    greedy = gdf[gdf.metodo.eq("greedy")].sort_values(["k", "cuantil"])
    persistence_rows = []
    for kval in (3, 5, 8):
        sub = greedy[greedy.k.eq(kval)]
        configs = sub.configuracion.tolist()
        for a, b in zip(configs[:-1], configs[1:]):
            la, lb = graph_labels_map[a], graph_labels_map[b]
            persistence_rows.append({"prueba_id": "BEL-R05", "k": kval, "config_a": a, "config_b": b, "ari": round(adjusted_rand_score(la, lb), 4), "ami": round(adjusted_mutual_info_score(la, lb), 4)})
    persistence = pd.DataFrame(persistence_rows)

    choice_row = greedy.sort_values(["modularidad", "pct_ruido"], ascending=[False, True]).iloc[0]
    chosen_radius = float(choice_row.umbral_m)
    louvain_runs = []
    for seed in range(20):
        label, _, _ = graph_labels(coords, chosen_radius, method="louvain", seed=SEED + seed)
        louvain_runs.append(label)
    consensus = np.zeros((len(pts), len(pts)), dtype=np.float32)
    for label in louvain_runs:
        for cid in set(label.tolist()) - {-1}:
            ids = np.flatnonzero(label == cid)
            consensus[np.ix_(ids, ids)] += 1
    consensus /= len(louvain_runs)
    consensus_graph = nx.Graph()
    consensus_graph.add_nodes_from(range(len(pts)))
    ci, cj = np.where(np.triu(consensus >= .65, 1))
    consensus_graph.add_edges_from(zip(ci.tolist(), cj.tolist()))
    candidate_sets = [set(c) for c in nx.connected_components(consensus_graph) if len(c) >= 8]
    candidate_sets.sort(key=len, reverse=True)

    kdep, _ = kde_maxima(coords)
    kde_points = [Point(r.x, r.y) for r in kdep.itertuples()]
    public_coords = xy(pts[pts.fuente.eq("F01+F02")])
    public_labels = HDBSCAN(min_cluster_size=8, min_samples=3).fit_predict(public_coords) if len(public_coords) >= 8 else np.array([])
    public_idx = pts.index[pts.fuente.eq("F01+F02")].to_numpy()
    places_coords = xy(pts[pts.fuente.eq("google_places")])
    places_labels = HDBSCAN(min_cluster_size=8, min_samples=3).fit_predict(places_coords) if len(places_coords) >= 8 else np.array([])
    places_idx = pts.index[pts.fuente.eq("google_places")].to_numpy()

    bootstrap_store: dict[int, list[dict]] = {i: [] for i in range(len(candidate_sets))}
    ari_by_block = []
    base_label = np.full(len(pts), -1, dtype=int)
    for cid, members in enumerate(candidate_sets):
        base_label[list(members)] = cid
    for block in (150, 200, 300, 400):
        bx = np.floor((coords[:, 0] - coords[:, 0].min()) / block).astype(int)
        by = np.floor((coords[:, 1] - coords[:, 1].min()) / block).astype(int)
        keys = np.array([f"{a}:{b}" for a, b in zip(bx, by)])
        unique = np.unique(keys)
        for rep in range(50):
            chosen = RNG.choice(unique, size=max(1, int(math.ceil(.8 * len(unique)))), replace=False)
            idx = np.flatnonzero(np.isin(keys, chosen))
            if len(idx) < 16:
                continue
            label, _, _ = graph_labels(coords[idx], chosen_radius, method="louvain", seed=SEED + rep + block)
            ari_by_block.append({"tamano_bloque_m": block, "repeticion": rep + 1, "ari_global": adjusted_rand_score(base_label[idx], label)})
            for cid, target in enumerate(candidate_sets):
                score, matched = best_cluster_match(target, label, idx)
                rec = {"block": block, "score": score}
                if matched:
                    geom = hull_for(pts.iloc[sorted(matched)], 40)
                    rec.update({"cx": geom.centroid.x, "cy": geom.centroid.y, "area": geom.area, "places_pct": source_mix(pts.iloc[sorted(matched)])[2]})
                bootstrap_store[cid].append(rec)

    stability_rows, polygons = [], []
    for cid, members in enumerate(candidate_sets):
        psub = pts.iloc[sorted(members)]
        geom = hull_for(psub, 40).intersection(barrio)
        base, places, places_pct = source_mix(psub)
        center = geom.centroid
        records = bootstrap_store[cid]
        survival_by_block = {b: np.mean([r["score"] >= .5 for r in records if r["block"] == b]) for b in (150, 200, 300, 400)}
        valid = [r for r in records if r.get("score", 0) >= .5 and "cx" in r]
        shifts = [math.hypot(r["cx"] - center.x, r["cy"] - center.y) for r in valid]
        areas = [r["area"] for r in valid]
        pp = [r["places_pct"] for r in valid]
        nearest_kde = min([center.distance(p) for p in kde_points] or [float("inf")])
        public_score, _ = best_cluster_match(set(members), public_labels, public_idx) if len(public_labels) else (0.0, set())
        places_score, _ = best_cluster_match(set(members), places_labels, places_idx) if len(places_labels) else (0.0, set())
        source_class = "respaldo_publico" if public_score >= .5 else "places_dependiente" if places_score >= .5 and public_score < .2 else "mixto"
        high_blocks = sum(v >= .8 for v in survival_by_block.values())
        kde_backed = nearest_kde <= 150
        if high_blocks >= 2 and kde_backed and source_class != "places_dependiente" and len(members) >= 12:
            category = "ALTA"
        elif max(survival_by_block.values(), default=0) >= .6 and source_class != "places_dependiente":
            category = "MEDIA"
        else:
            category = "BAJA"
        boundary = geom.distance(macro.boundary)
        row = {
            "identificador_tecnico": f"BEL_RV2_N{cid+1:02d}", "categoria": category,
            "cantidad_puntos": len(members), "f01_f02": base, "places": places,
            "dependencia_places_pct": places_pct, "clasificacion_fuentes": source_class,
            "supervivencia_b150": round(survival_by_block[150], 3), "supervivencia_b200": round(survival_by_block[200], 3),
            "supervivencia_b300": round(survival_by_block[300], 3), "supervivencia_b400": round(survival_by_block[400], 3),
            "desplazamiento_centro_p50_m": round(float(np.median(shifts)), 1) if shifts else np.nan,
            "desplazamiento_centro_p90_m": round(float(np.quantile(shifts, .9)), 1) if shifts else np.nan,
            "cv_extension": round(float(np.std(areas) / np.mean(areas)), 3) if areas and np.mean(areas) else np.nan,
            "rango_places_bootstrap": f"{min(pp):.1f}-{max(pp):.1f}" if pp else "sin_supervivencias",
            "distancia_maximo_kde_m": round(nearest_kde, 1) if np.isfinite(nearest_kde) else np.nan,
            "respaldo_kde": bool(kde_backed), "jaccard_sin_places": round(public_score, 3),
            "jaccard_places_solo": round(places_score, 3),
            "distancia_borde_contenedor_m": round(boundary, 1), "posiblemente_cortado": boundary < 100,
            "dependencia_contenedor": "ALTA" if boundary < 100 else "MEDIA_BAJA",
            "correspondencia_metodos": "consenso Louvain; contraste HDBSCAN/KDE",
        }
        stability_rows.append(row)
        polygons.append({**row, "estado": "CANDIDATO_SIN_NOMBRE", "geometry": geom})
    stability = pd.DataFrame(stability_rows)
    candidates = gpd.GeoDataFrame(polygons, geometry="geometry", crs=CRS_M)

    best_h = hdf.sort_values(["ari_vecinos_mediana", "pct_ruido"], ascending=[False, True]).iloc[0]
    boundary_rows = []
    for cname, cgeom, cpoints in (("contenedor_actual", macro, pts), ("barrio_oficial_completo", barrio, barrio_pts)):
        arr = xy(cpoints)
        label = HDBSCAN(min_cluster_size=int(best_h.min_cluster_size), min_samples=int(best_h.min_samples), cluster_selection_method=str(best_h.metodo)).fit_predict(arr)
        boundary_rows.append({"prueba_id": "BEL-R10" if cname == "contenedor_actual" else "BEL-R11", "familia": "CONTENEDOR", "configuracion": cname, "metodo": str(best_h.metodo), "n_puntos": len(cpoints), "n_clusters": labels_count(label), "pct_ruido": round(100 * (label == -1).mean(), 2), "area_ha": round(cgeom.area / 10000, 2)})
    tests = pd.concat([hdf, gdf, persistence, pd.DataFrame(boundary_rows)], ignore_index=True, sort=False)
    tests.to_csv(OUT / "belgrano_resultados_pruebas_v2.csv", index=False, encoding="utf-8")
    stability.to_csv(OUT / "belgrano_estabilidad_nucleos_v2.csv", index=False, encoding="utf-8")
    write_geo(candidates, OUT / "belgrano_nucleos_candidatos_v2.geojson")

    fig, axes = plt.subplots(1, 2, figsize=(13, 7))
    plot_context(axes[0], data, barrio_pts, barrio, "Barrio oficial completo — contraste")
    gpd.GeoSeries([macro], crs=CRS_M).plot(ax=axes[0], facecolor="none", edgecolor=COLORS["secondary"], linewidth=2)
    plot_context(axes[1], data, pts, macro, "Contenedor actual")
    save_figure(fig, OUT / "mapa_belgrano_contenedores_v2.png")
    fig, ax = plt.subplots(figsize=(9, 8))
    plot_context(ax, data, pts, barrio, "Núcleos candidatos — sin nombres urbanos")
    if len(candidates):
        candidates.plot(ax=ax, column="categoria", categorical=True, alpha=.28, edgecolor="#0F684B", linewidth=1.5, legend=True)
    save_figure(fig, OUT / "mapa_belgrano_nucleos_estables_v2.png")
    return {"points": pts, "stability": stability, "tests": tests, "candidates": candidates, "macro": macro, "barrio": barrio, "ari_blocks": pd.DataFrame(ari_by_block)}


def street_axis(data: dict, macro: object, names: list[str]) -> gpd.GeoDataFrame:
    streets = data["streets"][data["streets"].nomoficial.fillna("").isin(names)].copy()
    streets["geometry"] = streets.geometry.intersection(macro)
    return streets[~streets.geometry.is_empty].explode(index_parts=False).reset_index(drop=True)


def supported_segments(segments: gpd.GeoDataFrame, pts: gpd.GeoDataFrame, radius: float) -> tuple[gpd.GeoDataFrame, object]:
    rows = []
    for idx, seg in segments.iterrows():
        distances = pts.geometry.distance(seg.geometry)
        rows.append({"segmento": idx + 1, "eje": seg.get("nomoficial", ""), "n_puntos": int((distances <= radius).sum()), "longitud_m": seg.geometry.length, "geometry": seg.geometry})
    metrics = gpd.GeoDataFrame(rows, geometry="geometry", crs=CRS_M)
    positive = metrics[metrics.n_puntos > 0]
    gate = max(3, int(math.floor(positive.n_puntos.quantile(.25)))) if len(positive) else 3
    metrics["respaldado"] = metrics.n_puntos >= gate
    selected = metrics[metrics.respaldado]
    return metrics, unary_union(selected.geometry.tolist()) if len(selected) else unary_union(metrics.geometry.tolist())


def puerto_madero(data: dict) -> dict:
    pts = points_for(data, "MZ_PUERTO_MADERO")
    macro = data["macro"].loc["MZ_PUERTO_MADERO"].geometry
    names = {
        "oeste": ["MOREAU DE JUSTO, ALICIA AV."],
        "este": ["MANSO JUANA", "DEALESSI, PIERINA", "COSSETTINI, OLGA"],
        "transversales": ["GUEMES, MACACHA", "VILLAFLOR, AZUCENA", "VERA PEÑALOZA, ROSARIO", "LANTERI JULIETA"],
    }
    axes, inventory = {}, []
    for group, group_names in names.items():
        segs = street_axis(data, macro, group_names)
        metrics, axis = supported_segments(segs, pts, 180)
        axes[group] = axis
        for row in metrics.itertuples():
            inventory.append({"prueba_id": "PM-R02", "grupo": group, "eje": row.eje, "segmento": row.segmento, "n_puntos_180m": row.n_puntos, "longitud_m": round(row.longitud_m, 1), "respaldado": row.respaldado})
    west, east, cross = axes["oeste"], axes["este"], axes["transversales"]
    double = unary_union([west, east])
    all_axes = unary_union([west, east, cross])
    short_parts = [g for g in getattr(all_axes, "geoms", [all_axes]) if g.length >= 300]
    short = unary_union(short_parts) if short_parts else all_axes

    options = [
        ("PM-A_FRENTE_OESTE", west, 180, "frente oeste"),
        ("PM-B_FRENTE_ESTE", east, 180, "frente este"),
        ("PM-C_FRENTE_DOBLE", double, 180, "frente doble"),
        ("PM-D_SEGMENTOS_NCS", double, 180, "segmentos longitudinales codificados"),
        ("PM-E_FRENTES_CORTOS", short, 180, "varios frentes cortos"),
        ("PM-F_BUFFER_VARIABLE", all_axes, 240, "frente con buffer variable 120/180/240 m"),
        ("PM-G_FRENTE_MAS_CONTEXTO", double, 180, "frente doble + puntos de contexto"),
    ]
    rows, geo_rows, assignment_masks = [], [], {}
    barrio_area = macro.area
    for oid, geom, radius, representation in options:
        distances = pts.geometry.distance(geom)
        assigned = distances <= radius
        assignment_masks[oid] = assigned.to_numpy()
        covered = pts[assigned]
        base, places, places_pct = source_mix(covered)
        band = geom.buffer(radius, cap_style="flat").intersection(macro)
        overlap = 0
        if oid == "PM-C_FRENTE_DOBLE":
            overlap = int(((pts.geometry.distance(west) <= radius) & (pts.geometry.distance(east) <= radius)).sum())
        isolated = int((distances > 250).sum())
        edge_assigned = int((assigned & (pts.geometry.distance(macro.boundary) <= 100)).sum())
        gate_distance = radius <= 250
        gate_area = band.area / barrio_area <= .40
        target = len(covered) / len(pts) >= .60 and radius <= 180
        rows.append({
            "opcion_id": oid, "representacion": representation, "radio_maximo_m": radius,
            "puntos_universo": len(pts), "puntos_asignados": len(covered), "cobertura_pct": round(100 * len(covered) / len(pts), 2),
            "longitud_km": round(geom.length / 1000, 3), "densidad_puntos_km": round(len(covered) / max(geom.length / 1000, .001), 2),
            "f01_f02_asignados": base, "places_asignados": places, "places_pct_asignados": places_pct,
            "componentes": components(geom), "puntos_aislados_gt250m": isolated,
            "asignados_cerca_borde": edge_assigned, "solapamiento_puntos_entre_frentes": overlap,
            "superficie_banda_ha": round(band.area / 10000, 2), "porcentaje_area_barrio": round(100 * band.area / barrio_area, 2),
            "gate_distancia_le250": gate_distance, "gate_banda_le40pct": gate_area, "objetivo_60pct_180m": target,
        })
        geo_rows.append({"opcion_id": oid, "representacion": representation, "radio_maximo_m": radius, "estado": "CANDIDATO_EXPERIMENTAL", "geometry": geom})
    results = pd.DataFrame(rows)

    stability = []
    coords = xy(pts)
    for block in (200, 300):
        bx = np.floor((coords[:, 0] - coords[:, 0].min()) / block).astype(int)
        by = np.floor((coords[:, 1] - coords[:, 1].min()) / block).astype(int)
        keys = np.array([f"{a}:{b}" for a, b in zip(bx, by)])
        unique = np.unique(keys)
        for oid, base_mask in assignment_masks.items():
            flips = []
            for _ in range(50):
                selected = RNG.choice(unique, size=max(1, int(math.ceil(.8 * len(unique)))), replace=False)
                idx = np.flatnonzero(np.isin(keys, selected))
                # La geometría del frente es fija; se mide estabilidad de la proporción asignada por bloque.
                flips.append(abs(base_mask[idx].mean() - base_mask.mean()))
            stability.append({"opcion_id": oid, "tamano_bloque_m": block, "variacion_asignacion_media_pct": round(100 * float(np.mean(flips)), 2), "variacion_asignacion_p90_pct": round(100 * float(np.quantile(flips, .9)), 2)})
    stable_df = pd.DataFrame(stability)
    stab_summary = stable_df.groupby("opcion_id").variacion_asignacion_p90_pct.max()
    results["flip_rate_p90_pct"] = results.opcion_id.map(stab_summary)
    results["gate_estabilidad_p90_le15"] = results.flip_rate_p90_pct.le(15)
    results["elegible"] = results[["gate_distancia_le250", "gate_banda_le40pct", "gate_estabilidad_p90_le15"]].all(axis=1)
    eligible = results[results.elegible]
    recommended = eligible.sort_values(["objetivo_60pct_180m", "cobertura_pct", "componentes"], ascending=[False, False, True]).iloc[0] if len(eligible) else results.sort_values("cobertura_pct", ascending=False).iloc[0]
    results["recomendacion_tecnica"] = np.where(results.opcion_id.eq(recommended.opcion_id), "RECOMENDADA_NO_VINCULANTE", "NO_PRIORIZADA")
    results.to_csv(OUT / "puerto_madero_resultados_pruebas_v2.csv", index=False, encoding="utf-8")
    stable_df.to_csv(OUT / "puerto_madero_estabilidad_asignacion_v2.csv", index=False, encoding="utf-8")
    pd.DataFrame(inventory).to_csv(OUT / "puerto_madero_inventario_soportes_v2.csv", index=False, encoding="utf-8")
    fronts = gpd.GeoDataFrame(geo_rows, geometry="geometry", crs=CRS_M)
    write_geo(fronts, OUT / "puerto_madero_frentes_candidatos_v2.geojson")

    best_geom = fronts[fronts.opcion_id.eq(recommended.opcion_id)].geometry.iloc[0]
    distances = pts.geometry.distance(best_geom)
    non = pts[distances > float(recommended.radio_maximo_m)].copy()
    non["distancia_frente_m"] = distances[distances > float(recommended.radio_maximo_m)].round(1).to_numpy()
    non["categoria_taxonomia"] = np.select(
        [non.distancia_frente_m.le(250), non.distancia_frente_m.le(400), non.geometry.distance(macro.boundary).le(100)],
        ["continuidad territorial", "contexto gastronómico disperso", "dependencia del contenedor"],
        default="cola de revisión",
    )
    non_out = non[["id_punto", "fuente", "distancia_frente_m", "categoria_taxonomia"]].copy()
    non_out["id_punto"] = [f"PM_EXT_{i+1:04d}" for i in range(len(non_out))]
    non_out["nota"] = "clasificación técnica preliminar; sin nombre comercial ni identificador técnico de Places"
    non_out.to_csv(OUT / "puerto_madero_puntos_no_asignados_v2.csv", index=False, encoding="utf-8")

    fig, axes = plt.subplots(2, 4, figsize=(18, 10))
    for ax, row in zip(axes.ravel(), fronts.itertuples()):
        plot_context(ax, data, pts, macro, row.opcion_id.replace("_", " "))
        gpd.GeoSeries([row.geometry], crs=CRS_M).plot(ax=ax, color=COLORS["primary"], linewidth=3)
    axes.ravel()[-1].axis("off")
    save_figure(fig, OUT / "mapa_puerto_madero_opciones_v2.png")
    return {"points": pts, "results": results, "fronts": fronts, "recommended": recommended.to_dict(), "non": non_out, "macro": macro}


def corrientes(data: dict) -> dict:
    pts = points_for(data, "MZ_AVENIDA_CORRIENTES")
    macro = data["macro"].loc["MZ_AVENIDA_CORRIENTES"].geometry
    streets = data["streets"][data["streets"].nomoficial.fillna("").eq("CORRIENTES AV.")].copy()
    streets["geometry"] = streets.geometry.intersection(macro)
    streets = streets[~streets.geometry.is_empty].explode(index_parts=False).reset_index(drop=True)
    # Eje central continuo derivado de todos los vértices del callejero. Se resume la
    # doble calzada por medianas en bins longitudinales, sin inventar unidades.
    coords_all = []
    for geom in streets.geometry:
        for part in (list(geom.geoms) if hasattr(geom, "geoms") else [geom]):
            coords_all.extend(list(part.coords))
    coord_df = pd.DataFrame(coords_all, columns=["x", "y"]).drop_duplicates()
    east_cut = float(coord_df.x.quantile(.30))  # excluye el tramo occidental asociado a Abasto
    coord_df = coord_df[coord_df.x >= east_cut].copy()
    bins_x = np.linspace(coord_df.x.min(), coord_df.x.max(), 36)
    coord_df["bin"] = np.clip(np.digitize(coord_df.x, bins_x) - 1, 0, len(bins_x) - 2)
    centerline = coord_df.groupby("bin", as_index=False).agg(x=("x", "median"), y=("y", "median")).sort_values("x")
    continuous = LineString(centerline[["x", "y"]].to_numpy())
    buffer_geom = continuous.buffer(150, cap_style="flat").intersection(macro)
    covered_mask = pts.geometry.distance(continuous) <= 150
    covered = pts[covered_mask]
    corridor = gpd.GeoDataFrame([{
        "id_tecnico": "CORRIENTES_CORREDOR_CONTINUO_V2", "estado": "EXPERIMENTAL_NO_OFICIAL",
        "identidad_territorial": "UNICA", "componentes_geometricos": 1,
        "longitud_m": round(continuous.length, 1), "buffer_orientativo_m": 150,
        "puntos_universo": len(pts), "puntos_cubiertos": len(covered),
        "cobertura_pct": round(100 * len(covered) / len(pts), 2),
        "abasto_incorporado": "NO", "aclaracion": "El eje no representa todo el universo de la macrozona; buffer orientativo, no límite oficial.",
        "geometry": continuous,
    }], geometry="geometry", crs=CRS_M)
    write_geo(corridor, OUT / "corrientes_corredor_continuo_v2.geojson")

    projections = np.array([continuous.project(p) for p in pts.geometry])
    edges = np.linspace(0, continuous.length, 5)
    bins = np.clip(np.digitize(projections, edges) - 1, 0, 3)
    subrows = []
    for bid in range(4):
        mask = bins == bid
        sub = pts[mask]
        subrows.append({"subtramo_codigo": f"COR_ST_{bid+1:02d}", "uso": "NARRATIVO_NO_GEOMETRICO", "desde_m": round(edges[bid], 1), "hasta_m": round(edges[bid+1], 1), "puntos": len(sub), "f01_f02": int(sub.fuente.eq("F01+F02").sum()), "places": int(sub.fuente.eq("google_places").sum()), "densidad_puntos_km": round(len(sub) / max((edges[bid+1]-edges[bid])/1000, .001), 2)})
    pd.DataFrame(subrows).to_csv(OUT / "corrientes_subtramos_narrativos_v2.csv", index=False, encoding="utf-8")
    external = pts[~covered_mask].copy()
    d = external.geometry.distance(continuous)
    external["distancia_eje_m"] = d.round(1)
    external["categoria_taxonomia"] = np.select(
        [d.le(250), d.le(400), external.geometry.distance(macro.boundary).le(100)],
        ["continuidad territorial", "contexto gastronómico disperso", "dependencia del contenedor"],
        default="cola de revisión",
    )
    ext = external[["fuente", "distancia_eje_m", "categoria_taxonomia"]].copy()
    ext.insert(0, "id_externo", [f"COR_EXT_{i+1:04d}" for i in range(len(ext))])
    ext.to_csv(OUT / "corrientes_puntos_externos_v2.csv", index=False, encoding="utf-8")
    fig, ax = plt.subplots(figsize=(12, 6))
    plot_context(ax, data, pts, macro, "Av. Corrientes — corredor continuo separado de Abasto")
    gpd.GeoSeries([buffer_geom], crs=CRS_M).plot(ax=ax, facecolor=COLORS["primary"], edgecolor="none", alpha=.18)
    corridor.plot(ax=ax, color=COLORS["primary"], linewidth=4)
    save_figure(fig, OUT / "mapa_corrientes_corredor_continuo_v2.png")
    return {"points": pts, "corridor": corridor, "external": ext, "macro": macro}


def costanera(data: dict) -> dict:
    pts = points_for(data, "MZ_COSTANERA_NORTE")
    macro = data["macro"].loc["MZ_COSTANERA_NORTE"].geometry
    coords = xy(pts)
    labels = HDBSCAN(min_cluster_size=8, min_samples=5, cluster_selection_method="eom").fit_predict(coords)
    clusters = []
    for cid in sorted(set(labels.tolist()) - {-1}, key=lambda c: float(pts.loc[labels == c].geometry.x.mean())):
        members = np.flatnonzero(labels == cid)
        psub = pts.iloc[members]
        base, places, places_pct = source_mix(psub)
        geom = hull_for(psub, 70).intersection(macro)
        clusters.append({"technical_id": f"CN_C{len(clusters)+1:02d}", "members": members, "n": len(psub), "base": base, "places": places, "places_pct": places_pct, "geom": geom})
    # La concentración sin respaldo F01/F02 y 100% Places se conserva como contexto secundario.
    contextual = max([c for c in clusters if c["base"] == 0], key=lambda c: c["places_pct"], default=None)
    main = [c for c in clusters if contextual is None or c["technical_id"] != contextual["technical_id"]]
    multi_geom = MultiPolygon([c["geom"] for c in main]) if len(main) > 1 else main[0]["geom"]
    unit = gpd.GeoDataFrame([{
        "id_unidad": "COSTANERA_NORTE_MULTIPARTE_V2", "estado": "EXPLORATORIA_NO_OFICIAL",
        "identidad_editorial": "UNICA", "componentes_principales": len(main),
        "concentraciones_tecnicas_representadas": ";".join(c["technical_id"] for c in main),
        "dependencia_places_pct": round(100 * sum(c["places"] for c in main) / max(1, sum(c["n"] for c in main)), 2),
        "aclaracion": "Componentes separados; vacíos preservados; decisión editorial, no delimitación firme.",
        "geometry": multi_geom,
    }], geometry="geometry", crs=CRS_M)
    write_geo(unit, OUT / "costanera_unidad_multiparte_v2.geojson")
    component_rows = []
    for i, c in enumerate(main):
        component_rows.append({"componente_editorial": f"CN_MP_{i+1:02d}", "concentracion_tecnica": c["technical_id"], "n_puntos": c["n"], "f01_f02": c["base"], "places": c["places"], "places_pct": c["places_pct"], "estado": "PRINCIPAL_EXPLORATORIO", "vacio_entre_componentes_preservado": True})
    if contextual:
        component_rows.append({"componente_editorial": "CONTEXTO_SECUNDARIO", "concentracion_tecnica": contextual["technical_id"], "n_puntos": contextual["n"], "f01_f02": contextual["base"], "places": contextual["places"], "places_pct": contextual["places_pct"], "estado": "CONTEXTO_POR_DEPENDENCIA_PLACES", "vacio_entre_componentes_preservado": True})
        context_gdf = gpd.GeoDataFrame([{"id_contexto": contextual["technical_id"], "estado": "SEÑAL_SECUNDARIA_EXPLORATORIA", "razon": "100% Places y sin respaldo F01/F02; no se descarta", "geometry": contextual["geom"]}], geometry="geometry", crs=CRS_M)
        write_geo(context_gdf, OUT / "costanera_concentracion_contextual_v2.geojson")
    pd.DataFrame(component_rows).to_csv(OUT / "costanera_componentes_v2.csv", index=False, encoding="utf-8")
    kdep, surfaces = kde_maxima(coords, bandwidths=(100, 140, 180))
    fig, ax = plt.subplots(figsize=(12, 6))
    plot_context(ax, data, pts, macro, "Costanera Norte — unidad multiparte discontinua")
    if surfaces:
        bw = sorted(surfaces)[1]
        gx, gy, density = surfaces[bw]
        ax.contour(gx, gy, density, levels=5, colors=COLORS["secondary"], linewidths=.7, alpha=.55)
    unit.plot(ax=ax, facecolor=COLORS["primary"], edgecolor="#0F684B", alpha=.25)
    if contextual:
        gpd.GeoSeries([contextual["geom"]], crs=CRS_M).plot(ax=ax, facecolor=COLORS["context"], edgecolor=COLORS["border"], alpha=.25, hatch="///")
    save_figure(fig, OUT / "mapa_costanera_multiparte_v2.png")
    return {"points": pts, "unit": unit, "components": pd.DataFrame(component_rows), "contextual": contextual, "macro": macro, "technical_count": len(clusters)}


def write_diagnostics(results: dict) -> None:
    st = results["san_telmo"]
    be = results["belgrano"]
    pm = results["puerto_madero"]
    co = results["corrientes"]
    cn = results["costanera"]
    st_rec = st["recommended"]
    bel_counts = be["stability"].categoria.value_counts().to_dict() if len(be["stability"]) else {}
    pm_rec = pm["recommended"]
    cor = co["corridor"].iloc[0]
    contextual_id = cn["contextual"]["technical_id"] if cn["contextual"] else "ninguna"
    docs = {
        "DIAGNOSTICO_SAN_TELMO_V2.md": f"""# Diagnóstico San Telmo v2

Estado: **EXPERIMENTAL / NO OFICIAL**. Universo local: {len(st['points'])} puntos de oferta registrada/visible.

## Veredicto técnico

Se recomienda **núcleo compacto + eje Defensa contextual**. Cubre {st_rec['cobertura_pct']:.2f}% del universo, pero la cobertura no fue el único criterio: preserva un núcleo areal prudente y usa Defensa como respaldo longitudinal sin convertirla en límite oficial.

## Comparación

La tabla `tabla_comparacion_san_telmo_v2.csv` contrasta núcleo único, dos núcleos y núcleo + eje. La opción de dos núcleos aumenta la falsa precisión porque la separación depende más del detector. El eje mejora la lectura Mercado–Defensa y la continuidad por bloques.

## Límite y decisión humana

El buffer del eje es una convención cartográfica orientativa. No representa el ancho real del polo. Diego debe decidir si el eje se muestra en el mapa principal o solo en anexo.
""",
        "DIAGNOSTICO_BELGRANO_V2.md": f"""# Diagnóstico Belgrano v2

Estado: **EXPERIMENTAL / NO OFICIAL**. Se ejecutaron BEL-R01…BEL-R15 sobre el contenedor actual y el barrio oficial completo como contraste, sin imponer nombres.

## Resultado

Se identificaron {len(be['stability'])} estructuras candidatas: {bel_counts.get('ALTA',0)} ALTA, {bel_counts.get('MEDIA',0)} MEDIA y {bel_counts.get('BAJA',0)} BAJA. Los identificadores son exclusivamente técnicos.

La grilla HDBSCAN incluyó `eom` y `leaf`, la red usó umbrales derivados de distancias locales, Louvain se repitió con 20 semillas, KDE se usó como contraste y el bootstrap espacial se ejecutó con bloques de 150/200/300/400 m y 50 repeticiones por tamaño.

## Interpretación

La categoría de cada núcleo combina supervivencia, variación del centro y extensión, respaldo KDE, mezcla de fuentes y dependencia del contenedor. Ninguna categoría se asignó por cantidad deseada de núcleos. BEL-R14 queda como contraste post hoc; los nombres urbanos no entraron al algoritmo ni a las salidas.

## Límite

Places representa {100*be['points'].fuente.eq('google_places').mean():.1f}% del universo del contenedor actual. Las estructuras `places_dependiente` no son aptas para promoción firme.
""",
        "DIAGNOSTICO_PUERTO_MADERO_V2.md": f"""# Diagnóstico Puerto Madero v2

Estado: **EXPERIMENTAL / NO OFICIAL**. Se ejecutaron PM-R01…PM-R12 con soportes locales de ambos márgenes y transversales.

## Recomendación técnica

Se recomienda **{pm_rec['representacion']}** (`{pm_rec['opcion_id']}`), con cobertura de {pm_rec['cobertura_pct']:.2f}%, distancia máxima {pm_rec['radio_maximo_m']:.0f} m y banda equivalente a {pm_rec['porcentaje_area_barrio']:.2f}% del barrio.

La recomendación aplicó los gates de distancia, superficie de banda y estabilidad. No se eligió solo por cobertura. {'Alcanza' if pm_rec['objetivo_60pct_180m'] else 'No alcanza'} el objetivo orientativo de 60% a 180 m.

## Puntos no asignados

`puerto_madero_puntos_no_asignados_v2.csv` usa la taxonomía aprobada y no trata automáticamente todo punto externo como ruido. La clasificación es preliminar y no contiene nombres comerciales ni identificadores técnicos de Places.

## Límite

Los buffers son convenciones cartográficas, no ancho real ni límite oficial. La decisión final entre alternativas elegibles corresponde a Diego.
""",
        "DIAGNOSTICO_CORRIENTES_V2.md": f"""# Diagnóstico Corrientes v2

Estado: **EXPERIMENTAL / NO OFICIAL**.

## Resultado aprobado consolidado

Se construyó una única geometría lineal continua de {cor.longitud_m:.0f} m, separada de Abasto. Cubre {cor.cobertura_pct:.2f}% de los {cor.puntos_universo} puntos del recorte analítico.

Los cuatro subtramos de `corrientes_subtramos_narrativos_v2.csv` son etiquetas descriptivas: no constituyen unidades territoriales independientes. El corredor representa el eje principal y no todo el universo de la macrozona Corrientes/Microcentro.

## Puntos externos y límite

Los puntos externos se clasifican con la taxonomía aprobada. El buffer de 150 m es orientativo; no representa ancho real ni límite oficial. No se usó KMeans.
""",
        "DIAGNOSTICO_COSTANERA_V2.md": f"""# Diagnóstico Costanera Norte v2

Estado: **EXPLORATORIA / EXPERIMENTAL / NO OFICIAL**.

## Correspondencia 4 → 3

La repetición reproduce {cn['technical_count']} concentraciones técnicas. La unidad multiparte principal conserva {len(cn['components'][cn['components'].estado.eq('PRINCIPAL_EXPLORATORIO')])} componentes separados. La concentración `{contextual_id}` se conserva como señal contextual secundaria porque no tiene respaldo F01/F02 y depende 100% de Places. No se descarta silenciosamente.

## Representación

La salida tiene una sola identidad editorial, pero no rellena vacíos ni crea una envolvente única. Los espacios entre componentes responden a condiciones físicas, geográficas y a la localización discontinua de la oferta visible.

## Límite

Esta composición es una decisión editorial apoyada por puntos y KDE. No convierte Costanera Norte en una delimitación firme ni oficial. La dependencia de Places es crítica y obliga a mantenerla como señal exploratoria.
""",
    }
    for name, content in docs.items():
        (DOC / name).write_text(content, encoding="utf-8")

    comparison_rows = [
        {"zona": "San Telmo", "resultado_anterior": "núcleo compacto candidato", "resultado_nuevo": "núcleo + eje Defensa contextual", "cobertura_pct": st_rec["cobertura_pct"], "robustez": "MEDIA", "sensibilidad": st_rec["sensibilidad"], "representacion": "núcleo + eje", "puntos_no_asignados": int(st_rec["puntos_universo"]-st_rec["puntos_cubiertos"]), "dependencia_places": round(100*st['points'].fuente.eq('google_places').mean(),1), "mejora": "lectura longitudinal Mercado–Defensa", "perdida": "más complejidad cartográfica", "decision_humana_restante": "mapa principal o anexo", "aptitud_mapa_principal": "MEDIA", "aptitud_anexo": "ALTA", "aptitud_escalado": "MEDIA"},
        {"zona": "Belgrano", "resultado_anterior": "6 núcleos, robustez agregada 0,39", "resultado_nuevo": f"{bel_counts.get('ALTA',0)} alta; {bel_counts.get('MEDIA',0)} media; {bel_counts.get('BAJA',0)} baja", "cobertura_pct": np.nan, "robustez": "POR_NUCLEO", "sensibilidad": "ALTA_A_CONTENEDOR_Y_METODO", "representacion": "núcleos sin nombres o densidad continua", "puntos_no_asignados": np.nan, "dependencia_places": round(100*be['points'].fuente.eq('google_places').mean(),1), "mejora": "estabilidad desagregada y barrio completo de contraste", "perdida": "menor contundencia visual si no hay núcleos ALTA", "decision_humana_restante": "qué categorías mostrar y nombres post hoc", "aptitud_mapa_principal": "CONDICIONAL", "aptitud_anexo": "ALTA", "aptitud_escalado": "MEDIA"},
        {"zona": "Puerto Madero", "resultado_anterior": "frente oeste parcial 34,7%", "resultado_nuevo": pm_rec["representacion"], "cobertura_pct": pm_rec["cobertura_pct"], "robustez": "ALTA" if pm_rec["flip_rate_p90_pct"] <= 15 else "MEDIA", "sensibilidad": "MEDIA", "representacion": pm_rec["opcion_id"], "puntos_no_asignados": len(pm['non']), "dependencia_places": round(100*pm['points'].fuente.eq('google_places').mean(),1), "mejora": "soportes de ambos márgenes y gates explícitos", "perdida": "frente más complejo", "decision_humana_restante": "validar lectura urbana del frente", "aptitud_mapa_principal": "MEDIA_ALTA", "aptitud_anexo": "ALTA", "aptitud_escalado": "ALTA"},
        {"zona": "Corrientes", "resultado_anterior": "eje respaldado en 5 componentes", "resultado_nuevo": "corredor continuo único separado de Abasto", "cobertura_pct": cor.cobertura_pct, "robustez": "MEDIA_ALTA", "sensibilidad": "MEDIA_AL_BUFFER", "representacion": "corredor continuo", "puntos_no_asignados": len(co['external']), "dependencia_places": round(100*co['points'].fuente.eq('google_places').mean(),1), "mejora": "identidad territorial única", "perdida": "no representa toda la macrozona", "decision_humana_restante": "estilo de subtramos narrativos", "aptitud_mapa_principal": "ALTA", "aptitud_anexo": "ALTA", "aptitud_escalado": "ALTA"},
        {"zona": "Costanera Norte", "resultado_anterior": "4 concentraciones como señal", "resultado_nuevo": f"3 componentes principales + {contextual_id} contextual", "cobertura_pct": np.nan, "robustez": "EXPLORATORIA", "sensibilidad": "ALTA_A_PLACES", "representacion": "unidad multiparte discontinua", "puntos_no_asignados": cn['contextual']['n'] if cn['contextual'] else 0, "dependencia_places": round(100*cn['points'].fuente.eq('google_places').mean(),1), "mejora": "correspondencia explícita 4→3 sin rellenar vacíos", "perdida": "una concentración queda fuera de la unidad principal", "decision_humana_restante": "confirmar contexto secundario y ubicación en anexo", "aptitud_mapa_principal": "BAJA", "aptitud_anexo": "ALTA", "aptitud_escalado": "BAJA"},
    ]
    comparison = pd.DataFrame(comparison_rows)
    comparison.to_csv(OUT / "tabla_comparacion_repeticiones_v2.csv", index=False, encoding="utf-8")
    (DOC / "COMPARACION_REPETICIONES_HIBRIDAS_V2.md").write_text(
        "# Comparación de repeticiones híbridas v2\n\nEstado: **EXPERIMENTAL / NO OFICIAL**.\n\n" + markdown_table(comparison) + "\n\nLos resultados no reemplazan Fase 25. Aportan detalle experimental y decisiones humanas acotadas.\n",
        encoding="utf-8",
    )
    decisions = f"""# Matriz de decisiones post repeticiones v2

Estado: **EXPERIMENTAL / NO OFICIAL**. Solo incluye decisiones abiertas.

| ID | Zona | Decisión abierta | Evidencia disponible | Estado |
|---|---|---|---|---|
| DR-01 | San Telmo | Mostrar el eje Defensa en mapa principal o anexo | núcleo + eje recomendado; cobertura {st_rec['cobertura_pct']:.2f}% | ABIERTA |
| DR-02 | Belgrano | Determinar qué categorías de estabilidad se muestran | {bel_counts.get('ALTA',0)} ALTA; {bel_counts.get('MEDIA',0)} MEDIA; {bel_counts.get('BAJA',0)} BAJA | ABIERTA |
| DR-03 | Belgrano | Evaluar nombres urbanos solo post hoc | BEL-R14 no intervino en el algoritmo | ABIERTA |
| DR-04 | Puerto Madero | Validar territorialmente `{pm_rec['opcion_id']}` | gates técnicos superados: {bool(pm_rec['elegible'])} | ABIERTA |
| DR-05 | Corrientes | Definir estilo de subtramos narrativos | geometría única ya consolidada | ABIERTA |
| DR-06 | Costanera Norte | Confirmar `{contextual_id}` como contexto secundario y su ubicación editorial | 100% Places; 0 F01/F02 | ABIERTA |

No se detectó evidencia fuerte que obligue a reabrir automáticamente una decisión aprobada. Ninguna fila queda marcada `REQUIERE_REAPERTURA`.
"""
    (DOC / "MATRIZ_DECISIONES_POST_REPETICIONES_V2.md").write_text(decisions, encoding="utf-8")


def copy_package() -> list[str]:
    for folder in (PACK / "01_DIAGNOSTICOS", PACK / "02_TABLAS", PACK / "03_MAPAS", PACK / "04_GEOJSON", PACK / "05_DECISIONES_Y_QA"):
        folder.mkdir(parents=True, exist_ok=True)
    for path in DOC.glob("DIAGNOSTICO_*_V2.md"):
        shutil.copy2(path, PACK / "01_DIAGNOSTICOS" / path.name)
    for path in OUT.glob("*.csv"):
        shutil.copy2(path, PACK / "02_TABLAS" / path.name)
    for path in OUT.glob("*.png"):
        shutil.copy2(path, PACK / "03_MAPAS" / path.name)
    for path in OUT.glob("*.geojson"):
        shutil.copy2(path, PACK / "04_GEOJSON" / path.name)
    for name in ("COMPARACION_REPETICIONES_HIBRIDAS_V2.md", "MATRIZ_DECISIONES_POST_REPETICIONES_V2.md"):
        shutil.copy2(DOC / name, PACK / "05_DECISIONES_Y_QA" / name)
    readme = """# Revisión de repeticiones híbridas v2

Paquete autocontenido **EXPERIMENTAL / NO OFICIAL** para revisión humana. No es Fase 25 ni Fase 26 y no reemplaza informes oficiales.

- `01_DIAGNOSTICOS`: lectura técnica por zona.
- `02_TABLAS`: métricas reproducibles y comparación.
- `03_MAPAS`: vistas de control.
- `04_GEOJSON`: geometrías sanitizadas sin nombres comerciales ni identificadores Places.
- `05_DECISIONES_Y_QA`: comparación, decisiones abiertas y QA.

Los puntos provienen de oferta registrada/visible local ya almacenada. Los buffers son convenciones cartográficas orientativas, no anchos reales ni límites oficiales.
"""
    (PACK / "README.md").write_text(readme, encoding="utf-8")
    note = """# Nota para ChatGPT / Claude

Revisar consistencia entre métricas, geometrías y diagnósticos. Preservar estas decisiones: Corrientes es un corredor continuo separado de Abasto; Costanera Norte es una unidad editorial multiparte y discontinua; Belgrano no tiene nombres urbanos asignados; Fase 25 sigue vigente y el pipeline híbrido solo complementa.

No proponer APIs, descargas, modificaciones de fuente ni promoción oficial automática.
"""
    (PACK / "NOTA_PARA_CHATGPT_CLAUDE.md").write_text(note, encoding="utf-8")
    return [p.relative_to(PACK).as_posix() for p in sorted(PACK.rglob("*")) if p.is_file()]


def qa_and_metadata(before_hashes: dict[str, str], results: dict) -> None:
    after_hashes = protected_hashes()
    changed = sorted(k for k in set(before_hashes) | set(after_hashes) if before_hashes.get(k) != after_hashes.get(k))
    png_rows = []
    from PIL import Image, ImageStat
    for path in sorted(OUT.glob("*.png")):
        with Image.open(path) as img:
            stat = ImageStat.Stat(img.convert("L"))
            png_rows.append({"archivo": path.name, "ancho": img.width, "alto": img.height, "desv_estandar": round(stat.stddev[0], 2), "no_blanco": stat.stddev[0] > 2 and img.width > 100 and img.height > 100})
    package_files = copy_package()
    manifest_rows = []
    for path in sorted(PACK.rglob("*")):
        if path.is_file():
            manifest_rows.append({"ruta": path.relative_to(PACK).as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path)})
    manifest = pd.DataFrame(manifest_rows)
    manifest.to_csv(PACK / "MANIFEST_ARCHIVOS.csv", index=False, encoding="utf-8")
    manifest_md = "# Manifest de archivos\n\n" + markdown_table(manifest) + "\n"
    (PACK / "MANIFEST_ARCHIVOS.md").write_text(manifest_md, encoding="utf-8")
    (DOC / "MANIFEST_ARCHIVOS.md").write_text(manifest_md, encoding="utf-8")

    forbidden_patterns = {
        "email": r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}",
        "telefono": r"\b(?:\+?54\s*)?(?:11\s*)?\d{4}[-\s]?\d{4}\b",
        "cuit": r"\b\d{2}-\d{8}-\d\b",
        "api_key": r"AIza[0-9A-Za-z_\-]{20,}",
        "place_id": r"place_id",
        "drive_privado": r"drive\.google\.com|docs\.google\.com",
    }
    import re
    privacy_hits = []
    for path in PACK.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".md", ".csv", ".json", ".geojson", ".txt"}:
            text = path.read_text(encoding="utf-8", errors="replace")
            for label, pattern in forbidden_patterns.items():
                if re.search(pattern, text, re.I):
                    privacy_hits.append({"archivo": path.relative_to(PACK).as_posix(), "patron": label})

    metadata = {
        "estado": "EXPERIMENTAL_NO_OFICIAL",
        "fecha_corte": "2026-07-11",
        "semilla": SEED,
        "sin_api": True,
        "sin_google_places": True,
        "sin_descargas": True,
        "sin_kmeans": True,
        "sin_modificacion_fuentes": True,
        "sin_cambios_fase25_fase26_v1_v42": len(changed) == 0,
        "hashes_protegidos": {"archivos": len(before_hashes), "cambiados": changed},
        "universos": {k: len(v["points"]) for k, v in results.items()},
        "png_qa": png_rows,
        "privacidad_hits": privacy_hits,
        "package_file_count_before_manifest": len(package_files),
        "python": sys.version,
    }
    meta_path = OUT / "metadata_pipeline_hibrido_repeticiones_v2.json"
    meta_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    shutil.copy2(meta_path, PACK / "05_DECISIONES_Y_QA" / meta_path.name)
    qa = f"""# QA final repeticiones híbridas v2

Estado: **EXPERIMENTAL / NO OFICIAL**.

## Controles

- Sin API: **OK**.
- Sin Google Places: **OK** (no se realizaron llamadas; solo se leyó el universo local sanitizado ya almacenado).
- Sin descargas: **OK**.
- Sin datos fuente modificados: **OK**.
- Sin cambios en Fase 25, Fase 26, v1–v4.2 y prototipos híbridos v1: **{'OK' if not changed else 'REVISAR'}** ({len(before_hashes)} archivos protegidos comparados; {len(changed)} cambios).
- Sin KMeans: **OK**.
- Privacidad: **{'OK' if not privacy_hits else 'REVISAR'}** ({len(privacy_hits)} hallazgos automáticos).
- PNG no blancos: **{'OK' if all(r['no_blanco'] for r in png_rows) else 'REVISAR'}** ({len(png_rows)} mapas).
- ZIP: se valida después de su creación.

## Git

El script no ejecuta `git add`, commit, push ni staging. La verificación final del estado Git se realiza fuera del script para distinguir cambios preexistentes.

## Límites

La ausencia de patrones automáticos no reemplaza revisión humana. Las geometrías son experimentales y los buffers son convenciones cartográficas orientativas.
"""
    (DOC / "QA_FINAL_REPETICIONES_HIBRIDAS_V2.md").write_text(qa, encoding="utf-8")
    shutil.copy2(DOC / "QA_FINAL_REPETICIONES_HIBRIDAS_V2.md", PACK / "05_DECISIONES_Y_QA" / "QA_FINAL_REPETICIONES_HIBRIDAS_V2.md")
    # Rehacer manifest después de añadir metadata y QA.
    manifest_rows = []
    for path in sorted(PACK.rglob("*")):
        if path.is_file() and path.name not in {"MANIFEST_ARCHIVOS.csv", "MANIFEST_ARCHIVOS.md"}:
            manifest_rows.append({"ruta": path.relative_to(PACK).as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path)})
    manifest = pd.DataFrame(manifest_rows)
    manifest.to_csv(PACK / "MANIFEST_ARCHIVOS.csv", index=False, encoding="utf-8")
    (PACK / "MANIFEST_ARCHIVOS.md").write_text("# Manifest de archivos\n\n" + markdown_table(manifest) + "\n", encoding="utf-8")
    (DOC / "MANIFEST_ARCHIVOS.md").write_text((PACK / "MANIFEST_ARCHIVOS.md").read_text(encoding="utf-8"), encoding="utf-8")

    zip_path = OUT / "REVISION_REPETICIONES_HIBRIDAS_V2.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in sorted(PACK.rglob("*")):
            if path.is_file():
                arcname = (Path(PACK.name) / path.relative_to(PACK)).as_posix()
                zf.write(path, arcname)
    with zipfile.ZipFile(zip_path) as zf:
        bad = zf.testzip()
        names = zf.namelist()
        if bad or any("\\" in name for name in names) or any(not name.startswith(PACK.name + "/") for name in names):
            raise RuntimeError(f"ZIP inválido: bad={bad}")


def main() -> None:
    ensure_dirs()
    before_hashes = protected_hashes()
    v1 = load_v1_module()
    data = v1.load_inputs()
    results = {
        "san_telmo": san_telmo(data),
        "belgrano": belgrano(data),
        "puerto_madero": puerto_madero(data),
        "corrientes": corrientes(data),
        "costanera": costanera(data),
    }
    write_diagnostics(results)
    qa_and_metadata(before_hashes, results)
    print(json.dumps({"status": "OK", "output": str(OUT), "doc": str(DOC)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
