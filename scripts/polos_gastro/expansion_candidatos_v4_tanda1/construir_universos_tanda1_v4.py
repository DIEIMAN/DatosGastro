from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import geopandas as gpd
import networkx as nx
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from shapely import concave_hull
from shapely.geometry import MultiPoint
from sklearn.cluster import HDBSCAN

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "outputs/polos_gastro/expansion_candidatos_v4_tanda1"
UNIVERSE = ROOT / "outputs/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/completa_v1/UNIVERSO_COMPLETO_SANITIZADO.csv"
AREAS = ROOT / "outputs/polos_gastro/expansion_candidatos_v4_preflight/AREAS_CONSULTA_CANDIDATOS_V4.geojson"
ZONES = {"Z01": "Villa Crespo", "Z02": "Chacarita", "Z03": "Caballito multinodo", "Z04": "Boulevard Caseros — Parque Lezama"}


def stable_id(raw: str) -> str:
    return "T1P-" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:14].upper()


def area_km2(geom) -> float:
    return float(geom.area / 1_000_000) if geom is not None and not geom.is_empty else 0.0


def cluster_model(coords: np.ndarray, strict: bool = False) -> np.ndarray:
    if len(coords) < 10:
        return np.full(len(coords), -1, dtype=int)
    min_size = max(8 if not strict else 14, int(math.ceil(len(coords) * (0.035 if not strict else 0.06))))
    model = HDBSCAN(min_cluster_size=min_size, min_samples=5 if not strict else 8,
                    cluster_selection_epsilon=0.0, store_centers=None, copy=True)
    try:
        return model.fit_predict(coords)
    except (TypeError, ValueError):
        # Coincident points in a bootstrap sample can create a degenerate condensed tree.
        # This is treated as no stable cluster, never as positive evidence.
        return np.full(len(coords), -1, dtype=int)


def graph_metrics(coords: np.ndarray, threshold: float = 250.0) -> tuple[int, float, float]:
    if not len(coords):
        return 0, 0.0, float("nan")
    tree = cKDTree(coords)
    pairs = tree.query_pairs(threshold)
    graph = nx.Graph()
    graph.add_nodes_from(range(len(coords)))
    graph.add_edges_from(pairs)
    comps = list(nx.connected_components(graph))
    largest = max((len(c) for c in comps), default=0) / len(coords)
    d, _ = tree.query(coords, k=min(2, len(coords)))
    nn = float(np.median(d[:, 1])) if len(coords) > 1 else float("nan")
    return len(comps), float(largest), nn


def bootstrap_presence(coords: np.ndarray, seed: int = 42) -> float:
    if len(coords) < 15:
        return 0.0
    rng = np.random.default_rng(seed)
    blocks = np.floor(coords / 250).astype(int)
    keys = np.unique(blocks, axis=0)
    successes = 0
    for _ in range(20):
        selected = keys[rng.random(len(keys)) >= 0.2]
        mask = np.array([any(np.array_equal(b, s) for s in selected) for b in blocks])
        if mask.sum() >= 10 and np.any(cluster_model(coords[mask]) >= 0):
            successes += 1
    return successes / 20


def polygons_for_labels(gdf: gpd.GeoDataFrame, label_col: str, model: str) -> gpd.GeoDataFrame:
    rows = []
    for label in sorted(x for x in gdf[label_col].unique() if x >= 0):
        points = gdf[gdf[label_col] == label]
        mp = MultiPoint(list(points.geometry))
        geom = concave_hull(mp, ratio=0.25, allow_holes=False) if len(points) >= 4 else mp.convex_hull.buffer(60)
        if geom.geom_type not in {"Polygon", "MultiPolygon"}:
            geom = geom.buffer(60)
        rows.append({"modelo": model, "cluster_id": int(label), "n_puntos": len(points), "geometry": geom})
    if not rows:
        return gpd.GeoDataFrame(columns=["modelo", "cluster_id", "n_puntos", "geometry"],
                                geometry="geometry", crs=gdf.crs)
    return gpd.GeoDataFrame(rows, geometry="geometry", crs=gdf.crs)


def classify(zone: str, n: int, n_clusters: int, largest_share: float, stability: float, places_share: float) -> tuple[str, str, str]:
    if n < 25 or n_clusters == 0:
        return "EVIDENCIA_INSUFICIENTE", "OFERTA_DISPERSA", "No adoptar; revisar tras cubrir brechas."
    if zone == "Z04":
        primary = "CORREDOR_ADOPTABLE" if largest_share >= 0.55 and stability >= 0.6 else "MICROCENTRALIDAD"
        return primary, "AREA_ASOCIADA", "Revisión humana del tramo; no extender a Parque Patricios."
    if zone == "Z03":
        primary = "POLO_MULTIPARTE" if n_clusters >= 2 else "MICROCENTRALIDAD"
        return primary, "OFERTA_DISPERSA", "Mantener nodos separados hasta decisión humana."
    if zone == "Z01":
        primary = "POLO_MULTIPARTE" if n_clusters >= 2 else "SUBPOLO_DE_UNIDAD_EXISTENTE"
        return primary, "TRANSICION_ENTRE_POLOS", "Resolver independencia respecto de Palermo y transición con Chacarita."
    primary = "POLO_MULTIPARTE" if n_clusters >= 2 else "MICROCENTRALIDAD"
    return primary, "TRANSICION_ENTRE_POLOS", "Resolver Newbery y Dorrego por separado; Lacroze queda como control."


def main() -> int:
    (OUT / "universos").mkdir(parents=True, exist_ok=True)
    (OUT / "capas").mkdir(parents=True, exist_ok=True)
    raw = pd.read_csv(UNIVERSE, encoding="utf-8-sig")
    raw = raw.dropna(subset=["lat", "lon"]).copy()
    raw["point_id_sanitizado"] = raw["id_punto"].astype(str).map(stable_id)
    raw["fecha_fuente"] = raw["fecha_consulta"].fillna("NO_DISPONIBLE")
    raw["categoria_normalizada"] = raw["categoria"].fillna("sin_categoria")
    raw["qa_status"] = "OK"
    raw["coincidencia_entre_fuentes"] = "NO_DISPONIBLE_EN_UNIVERSO_SANITIZADO"
    raw["publicable"] = "SI"
    points = gpd.GeoDataFrame(raw, geometry=gpd.points_from_xy(raw.lon, raw.lat), crs="EPSG:4326").to_crs("EPSG:5347")
    areas = gpd.read_file(AREAS).to_crs("EPSG:5347")
    metrics, alternatives, decisions, assignments = [], [], [], []
    all_polys = []

    for zone, zone_name in ZONES.items():
        zone_areas = areas[areas["zona_id"] == zone].copy()
        main_area = zone_areas[zone_areas["geometry_role"] == "AREA_PRINCIPAL"].geometry.iloc[0]
        zp = points[points.geometry.intersects(main_area)].copy()
        for r in zone_areas[zone_areas["geometry_role"] == "SUBUNIDAD_ANALITICA"].itertuples():
            for pid in points[points.geometry.intersects(r.geometry)].point_id_sanitizado:
                assignments.append({"point_id_sanitizado": pid, "zona_id": zone,
                                    "subunidad_id": r.subunidad_id, "subunidad_nombre": r.nombre,
                                    "metodo_asignacion": "INTERSECCION_GEOMETRICA"})
        for pid in zp.point_id_sanitizado:
            assignments.append({"point_id_sanitizado": pid, "zona_id": zone,
                                "subunidad_id": "AREA_PRINCIPAL", "subunidad_nombre": zone_name,
                                "metodo_asignacion": "INTERSECCION_GEOMETRICA"})
        export_cols = ["point_id_sanitizado", "fuente", "categoria_normalizada", "lat", "lon",
                       "fecha_fuente", "coincidencia_entre_fuentes", "qa_status", "publicable"]
        for universe_name, mask in {
            "ADMINISTRATIVO": zp["fuente"].eq("F01+F02"),
            "PLACES": zp["fuente"].eq("google_places"),
            "COMBINADO": pd.Series(True, index=zp.index),
        }.items():
            u = zp[mask].copy()
            u[export_cols].to_csv(OUT / "universos" / f"{zone}_UNIVERSO_{universe_name}.csv",
                                  index=False, encoding="utf-8-sig")
            coords = np.c_[u.geometry.x, u.geometry.y]
            labels = cluster_model(coords, strict=False)
            strict_labels = cluster_model(coords, strict=True)
            u["cluster_principal"] = labels
            u["cluster_conservador"] = strict_labels
            n_clusters = len(set(labels) - {-1})
            graph_components, largest_share, nn_med = graph_metrics(coords)
            clustered_share = float(np.mean(labels >= 0)) if len(labels) else 0.0
            stability = bootstrap_presence(coords, seed=42 + list(ZONES).index(zone))
            polys = polygons_for_labels(u, "cluster_principal", "PRINCIPAL_HDBSCAN")
            if not polys.empty:
                polys["zona_id"], polys["universo"] = zone, universe_name
                all_polys.append(polys)
            surface = float(polys.geometry.area.sum() / 1_000_000) if not polys.empty else 0.0
            places_share = float(u["fuente"].eq("google_places").mean()) if len(u) else 0.0
            metrics.append({
                "zona_id": zone, "zona": zone_name, "universo": universe_name,
                "puntos": len(u), "puntos_f01_f02": int(u["fuente"].eq("F01+F02").sum()),
                "puntos_places": int(u["fuente"].eq("google_places").sum()),
                "coincidencias": "NO_DISPONIBLE", "dependencia_places_pct": round(places_share * 100, 2),
                "dependencia_places_mayor_70": "SI" if places_share > 0.70 else "NO",
                "clusters_hdbscan": n_clusters, "componentes_grafo_250m": graph_components,
                "participacion_mayor_componente": round(largest_share, 4),
                "cobertura_cluster_pct": round(clustered_share * 100, 2),
                "estabilidad_bootstrap_bloques": round(stability, 3),
                "distancia_vecino_mediana_m": round(nn_med, 2) if np.isfinite(nn_med) else "",
                "superficie_clusters_km2": round(surface, 4),
                "densidad_puntos_km2_area_principal": round(len(u) / area_km2(main_area), 2),
                "continuidad": "ALTA" if largest_share >= .7 else "MEDIA" if largest_share >= .45 else "BAJA",
                "riesgo_artificialidad": "ALTO" if places_share > .7 or clustered_share < .35 else "MEDIO" if stability < .6 else "BAJO",
            })
            alternatives += [
                {"zona_id": zone, "universo": universe_name, "alternativa": "PRINCIPAL",
                 "metodo": "HDBSCAN", "componentes": n_clusters, "estado": "EXPERIMENTAL"},
                {"zona_id": zone, "universo": universe_name, "alternativa": "CONSERVADORA",
                 "metodo": "HDBSCAN_ESTRICTO", "componentes": len(set(strict_labels) - {-1}), "estado": "EXPERIMENTAL"},
                {"zona_id": zone, "universo": universe_name, "alternativa": "RESPALDO",
                 "metodo": "GRAFO_250M", "componentes": graph_components, "estado": "EXPERIMENTAL"},
            ]
        m = metrics[-1]
        primary, alt, human = classify(zone, m["puntos"], m["clusters_hdbscan"],
                                       m["participacion_mayor_componente"], m["estabilidad_bootstrap_bloques"],
                                       m["dependencia_places_pct"] / 100)
        decisions.append({"zona_id": zone, "zona": zone_name, "resultado_tecnico_principal": primary,
                          "alternativa": alt, "motivo": "Clasificación prudencial sobre universo combinado reutilizado; brechas nuevas no cubiertas.",
                          "decision_humana_necesaria": human, "adopcion_institucional": "NO"})

    pd.DataFrame(metrics).to_csv(OUT / "METRICAS_COMPARACION_FUENTES_TANDA1_V4.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(alternatives).to_csv(OUT / "ALTERNATIVAS_MODELOS_TANDA1_V4.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(decisions).to_csv(OUT / "MATRIZ_DECISION_TECNICA_TANDA1_V4.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(assignments).drop_duplicates().to_csv(OUT / "ASIGNACIONES_GEOMETRICAS_TANDA1_V4.csv", index=False, encoding="utf-8-sig")
    if all_polys:
        clusters = pd.concat(all_polys, ignore_index=True)
        clusters = gpd.GeoDataFrame(clusters, geometry="geometry", crs="EPSG:5347").to_crs("EPSG:4326")
        clusters.to_file(OUT / "capas" / "CLUSTERS_ANALITICOS_TANDA1_V4.geojson", driver="GeoJSON")
        provisional = clusters[clusters["universo"] == "COMBINADO"].copy()
        provisional["estado"] = "PROVISIONAL_NO_OFICIAL"
        provisional["nombre_tecnico"] = provisional["zona_id"].map(ZONES)
        provisional.to_file(OUT / "capas" / "GEOMETRIAS_PROVISIONALES_TANDA1_V4.geojson", driver="GeoJSON")
    summary = {
        "estado": "REUSE_ONLY", "universo_base": 6461,
        "f01_f02_base": int(raw["fuente"].eq("F01+F02").sum()),
        "places_base": int(raw["fuente"].eq("google_places").sum()),
        "filas_api_nuevas": 0, "zonas": list(ZONES),
    }
    (OUT / "RESUMEN_UNIVERSOS_TANDA1_V4.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
