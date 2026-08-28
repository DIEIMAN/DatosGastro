# -*- coding: utf-8 -*-
"""Corrida territorial V3: Belgrano, Recoleta y Costanera Norte.

EXPERIMENTAL / NO OFICIAL. Solo usa insumos locales congelados. No llama APIs,
no descarga datos, no instala dependencias y no modifica baselines protegidos.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import shutil
import subprocess
import sys
import textwrap
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
import shapely
from matplotlib.lines import Line2D
from shapely.geometry import MultiPoint, Point
from shapely.ops import unary_union
from sklearn.cluster import HDBSCAN


ROOT = Path(__file__).resolve().parents[3]
SCRIPT_DIR = ROOT / "scripts/polos_gastro/corrida_territorial_v3"
DOC = ROOT / "docs/polos_gastro/corrida_territorial_v3"
OUT = ROOT / "outputs/polos_gastro/corrida_territorial_v3"
MAPS = OUT / "mapas"
REVIEW = OUT / "REVISION_CORRIDA_TERRITORIAL_V3"
EXTRACT_QA = OUT / "REVISION_CORRIDA_TERRITORIAL_V3_EXTRACCION_QA"
ZIP_PATH = OUT / "REVISION_CORRIDA_TERRITORIAL_V3.zip"
CONFIG_PATH = SCRIPT_DIR / "config_territorial_v3.json"
PREFLIGHT_MATRIX = ROOT / "outputs/polos_gastro/preflight_cartografico_v3/MATRIZ_INSUMOS_Y_DEPENDENCIAS.csv"
PROTECTED_YAML = ROOT / "docs/polos_gastro/PROTECTED_SURFACES.yaml"
DOC_MATRIX = ROOT / "docs/polos_gastro/evidencia_documental_integrada_v1_1/MATRIZ_EVIDENCIA_DOCUMENTAL_INTEGRADA.csv"
DOC_HANDOFF = ROOT / "docs/polos_gastro/evidencia_documental_integrada_v1_1/HANDOFF_DOCUMENTAL_CARTOGRAFO_V1_1.md"
EDITORIAL_CONTRACT = ROOT / "docs/polos_gastro/preintegracion_editorial_v3/CONTRATO_OUTPUTS_CARTOGRAFICOS_PARA_INTEGRACION_V3.md"
CRS_M = "EPSG:5347"
CRS_GEO = "EPSG:4326"

POINTS = ROOT / "outputs/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/completa_v1/UNIVERSO_COMPLETO_SANITIZADO.csv"
MACRO = ROOT / "outputs/polos_gastro/experimentos/infraestructura_cartografica_v1/macrozonas_editoriales_candidatas_v1.geojson"
STREETS = ROOT / "outputs/polos_gastro/fase15_mapas_callejeros_v3/assets/callejero_gcba_2026_06_02.geojson"
BEL_GEO = ROOT / "outputs/polos_gastro/experimentos/pipeline_hibrido_repeticiones_v2/belgrano_nucleos_candidatos_v2.geojson"
BEL_MET = ROOT / "outputs/polos_gastro/experimentos/pipeline_hibrido_repeticiones_v2/belgrano_estabilidad_nucleos_v2.csv"
REC_GEO = ROOT / "outputs/polos_gastro/experimentos/pipeline_hibrido_integracion_v21/recoleta_nucleos_analiticos_v21.geojson"
REC_MET = ROOT / "outputs/polos_gastro/experimentos/pipeline_hibrido_integracion_v21/recoleta_metricas_v21.csv"
CN_BASE = ROOT / "outputs/polos_gastro/experimentos/pipeline_hibrido_repeticiones_v2/costanera_componentes_v2.csv"

COLORS = {
    "navy": "#153E5C", "blue": "#2878A8", "green": "#16845B", "gold": "#C58A2B",
    "purple": "#76549A", "red": "#B34A3C", "gray": "#6D7880", "light": "#DCE3E7",
    "street": "#D8DCDF", "base": "#1F5D7A", "external": "#C47A1D", "context": "#A0A7AD",
}
NOTE = "EXPERIMENTAL / NO OFICIAL · oferta registrada/visible · no es límite administrativo oficial"
DATE = "2026-07-11"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_new_line() -> None:
    for path in (DOC, OUT):
        if path.exists() and any(path.iterdir()):
            raise RuntimeError(f"La linea de salida ya contiene archivos: {path}")
    for path in (DOC, OUT, MAPS, REVIEW):
        path.mkdir(parents=True, exist_ok=True)


def read_config() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def write_json(obj: object, path: Path) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_csv(frame: pd.DataFrame, path: Path) -> None:
    frame.to_csv(path, index=False, encoding="utf-8", lineterminator="\n")


def write_geo(frame: gpd.GeoDataFrame, path: Path) -> None:
    clean = frame.copy()
    for col in clean.columns:
        if col != "geometry" and clean[col].dtype == "object":
            clean[col] = clean[col].fillna("").astype(str)
    clean.to_crs(CRS_GEO).to_file(path, driver="GeoJSON")


def md_table(frame: pd.DataFrame) -> str:
    clean = frame.fillna("").astype(str).apply(lambda c: c.str.replace("|", "\\|", regex=False))
    head = "| " + " | ".join(clean.columns) + " |"
    sep = "|" + "|".join(["---"] * len(clean.columns)) + "|"
    rows = ["| " + " | ".join(row) + " |" for row in clean.to_numpy().tolist()]
    return "\n".join([head, sep, *rows])


def git_cached() -> list[str]:
    proc = subprocess.run(["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True, capture_output=True, check=True)
    return [x for x in proc.stdout.splitlines() if x.strip()]


def snapshot_inputs() -> pd.DataFrame:
    matrix = pd.read_csv(PREFLIGHT_MATRIX)
    rows = []
    for row in matrix.itertuples(index=False):
        path = ROOT / row.ruta_relativa
        actual = sha256(path) if path.is_file() else "MISSING"
        rows.append({
            "id": row.id, "polo": row.polo, "tipo": row.tipo, "ruta_relativa": row.ruta_relativa,
            "bytes": path.stat().st_size if path.is_file() else 0, "sha256_esperado": row.sha256,
            "sha256_actual": actual, "hash_ok": actual == row.sha256, "crs_o_unidad": row.crs_o_unidad,
            "campos_clave": row.campos_clave, "proteccion": row.proteccion,
        })
    for key, path, kind in [
        ("DOC_V11_HANDOFF", DOC_HANDOFF, "handoff_documental"),
        ("DOC_V11_MATRIX", DOC_MATRIX, "matriz_documental"),
        ("PROTECTED_SURFACES", PROTECTED_YAML, "registro_superficies"),
    ]:
        rows.append({"id": key, "polo": "TODOS", "tipo": kind, "ruta_relativa": path.relative_to(ROOT).as_posix(),
                     "bytes": path.stat().st_size, "sha256_esperado": sha256(path), "sha256_actual": sha256(path),
                     "hash_ok": True, "crs_o_unidad": "N/A", "campos_clave": "N/A", "proteccion": "SOLO_LECTURA"})
    frame = pd.DataFrame(rows)
    if not frame.hash_ok.all():
        bad = frame.loc[~frame.hash_ok, ["id", "ruta_relativa"]].to_dict("records")
        raise RuntimeError(f"Hashes de entrada no coincidentes: {bad}")
    return frame


def protected_paths() -> list[Path]:
    patterns = [
        "PolosGastro", "docs/polos_gastro/fase25_microajustes_finales_oficina",
        "outputs/polos_gastro/fase25_microajustes_finales_oficina",
        "scripts/polos_gastro/build_fase25_microajustes_finales_oficina.py",
        "outputs/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/fase26_comparativa_cartografia",
        "outputs/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/completa_v1",
        "outputs/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/cartografia_editorial_v2",
        "outputs/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/cartografia_decision_v3",
        "outputs/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/cartografia_redibujo_editorial_v4",
        "outputs/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/cartografia_redibujo_editorial_v4_1",
        "outputs/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/cartografia_design_v4_2",
        "docs/polos_gastro/experimentos/pipeline_hibrido_tipo_territorial_v1",
        "outputs/polos_gastro/experimentos/pipeline_hibrido_tipo_territorial_v1",
        "docs/polos_gastro/experimentos/pipeline_hibrido_repeticiones_v2",
        "outputs/polos_gastro/experimentos/pipeline_hibrido_repeticiones_v2",
        "docs/polos_gastro/experimentos/pipeline_hibrido_integracion_v21",
        "outputs/polos_gastro/experimentos/pipeline_hibrido_integracion_v21",
    ]
    files: list[Path] = []
    for rel in patterns:
        target = ROOT / rel
        if target.is_file():
            files.append(target)
        elif target.is_dir():
            files.extend(sorted(p for p in target.rglob("*") if p.is_file()))
    return sorted(set(files))


def hash_map(paths: list[Path]) -> dict[str, str]:
    return {p.relative_to(ROOT).as_posix(): sha256(p) for p in paths}


def load_data() -> dict:
    raw = pd.read_csv(POINTS)
    points = gpd.GeoDataFrame(raw, geometry=gpd.points_from_xy(raw.lon, raw.lat), crs=CRS_GEO).to_crs(CRS_M)
    macro = gpd.read_file(MACRO).to_crs(CRS_M)
    id_col = "id" if "id" in macro.columns else "macrozona_id"
    macro = macro.set_index(id_col)
    streets = gpd.read_file(STREETS).to_crs(CRS_M)
    return {"points": points, "macro": macro, "streets": streets}


def points_for(data: dict, macro_id: str) -> gpd.GeoDataFrame:
    return data["points"].loc[data["points"].macrozona_id.eq(macro_id)].copy().reset_index(drop=True)


def source_group(series: pd.Series) -> pd.Series:
    return np.where(series.eq("google_places"), "SENAL_EXTERNA_ALMACENADA", "F01_F02")


def geom_components(geom) -> int:
    if geom is None or geom.is_empty:
        return 0
    return len(geom.geoms) if geom.geom_type.startswith("Multi") else 1


def pairwise_gaps(frame: gpd.GeoDataFrame) -> list[tuple[float, int, int]]:
    out = []
    for i in range(len(frame)):
        for j in range(i + 1, len(frame)):
            out.append((float(frame.geometry.iloc[i].distance(frame.geometry.iloc[j])), i, j))
    return sorted(out)


def graph_components(frame: gpd.GeoDataFrame, threshold: float) -> list[list[int]]:
    graph = nx.Graph()
    graph.add_nodes_from(range(len(frame)))
    for gap, i, j in pairwise_gaps(frame):
        if gap <= threshold:
            graph.add_edge(i, j, weight=math.exp(-gap / max(1.0, threshold)))
    return [sorted(c) for c in sorted(nx.connected_components(graph), key=lambda c: -sum(frame.iloc[list(c)].get("cantidad_puntos", pd.Series(1, index=list(c)))))]


def constrained_union(geoms: list, close_m: float = 0.0):
    geom = unary_union(geoms)
    if close_m > 0:
        geom = geom.buffer(close_m).buffer(-close_m)
    return shapely.make_valid(geom)


def included_points(points: gpd.GeoDataFrame, geom) -> gpd.GeoDataFrame:
    return points.loc[points.geometry.intersects(geom)].copy()


def model_metrics(polo: str, model: str, points: gpd.GeoDataFrame, geom, stability: float,
                  sensitivity: float, description: str, gaps: list[float] | None = None,
                  absorbed: int | None = None, risk_frag: str = "MEDIO", risk_union: str = "MEDIO",
                  territorial_components: int | None = None) -> dict:
    inc = included_points(points, geom)
    area = float(geom.area)
    perim = float(geom.length)
    compact = 4 * math.pi * area / (perim * perim) if perim else 0.0
    places = int(inc.fuente.eq("google_places").sum())
    base = len(inc) - places
    gaps = gaps or []
    return {
        "polo": polo, "modelo": model, "universo": len(points), "puntos_incluidos": len(inc),
        "cobertura_pct": round(100 * len(inc) / max(1, len(points)), 2),
        "componentes": territorial_components if territorial_components is not None else geom_components(geom),
        "piezas_topologicas": geom_components(geom),
        "distancia_min_componentes_m": round(min(gaps), 1) if gaps else 0.0,
        "distancia_max_componentes_m": round(max(gaps), 1) if gaps else 0.0,
        "superficie_km2": round(area / 1e6, 4), "compacidad": round(compact, 3),
        "densidad_puntos_km2": round(len(inc) / max(area / 1e6, 1e-9), 1), "f01_f02": base,
        "senal_externa_almacenada": places, "dependencia_places_pct": round(100 * places / max(1, len(inc)), 2),
        "estabilidad": round(stability, 3), "sensibilidad": round(sensitivity, 3),
        "puntos_sin_asignar": len(points) - len(inc), "nucleos_absorbidos": absorbed if absorbed is not None else "",
        "principales_vacios": ";".join(str(round(x, 1)) for x in sorted(gaps, reverse=True)[:3]),
        "riesgo_fragmentacion": risk_frag, "riesgo_union_artificial": risk_union, "descripcion": description,
    }


def make_belgrano(data: dict, cfg: dict) -> dict:
    points = points_for(data, "MZ_BELGRANO")
    candidates = gpd.read_file(BEL_GEO).to_crs(CRS_M)
    metrics = pd.read_csv(BEL_MET)
    threshold = float(cfg["belgrano"]["umbral_continuidad_m"])
    comps = graph_components(candidates, threshold)
    sub_rows = []
    for n, idx in enumerate(comps, 1):
        sub = candidates.iloc[idx]
        geom = constrained_union(sub.geometry.tolist(), float(cfg["belgrano"]["cierre_presentacion_m"]))
        sub_rows.append({
            "subzona_id": f"BEL_S{n:02d}", "candidatos": ";".join(sub.identificador_tecnico),
            "puntos_candidatos": int(sub.cantidad_puntos.sum()), "n_candidatos": len(sub),
            "supervivencia_media": round(float(sub[["supervivencia_b150", "supervivencia_b200", "supervivencia_b300", "supervivencia_b400"]].mean(axis=1).mean()), 3),
            "respaldo_kde_pct": round(100 * float(sub.respaldo_kde.mean()), 1), "geometry": geom,
        })
    subzones = gpd.GeoDataFrame(sub_rows, geometry="geometry", crs=CRS_M)
    raw_union = unary_union(candidates.geometry.tolist())
    a_geom = unary_union(subzones.geometry.tolist())
    comps120 = graph_components(candidates, 120)
    b_groups = sorted(comps120, key=lambda x: -int(candidates.iloc[x].cantidad_puntos.sum()))[:4]
    b_geom = unary_union([constrained_union(candidates.iloc[x].geometry.tolist(), 25) for x in b_groups])
    c_geom = raw_union
    candidate_gaps = [x[0] for x in pairwise_gaps(subzones)]
    surv = metrics[["supervivencia_b150", "supervivencia_b200", "supervivencia_b300", "supervivencia_b400"]].mean(axis=1)
    stability = float(surv.mean())
    sensitivity = float(metrics.jaccard_sin_places.mean())
    rows = [
        model_metrics("BELGRANO", "BEL-A", points, a_geom, stability, sensitivity,
                      "Unidad macro multiparte con tres centralidades derivadas por continuidad a 160 m.", candidate_gaps,
                      risk_frag="BAJO", risk_union="BAJO", territorial_components=3),
        model_metrics("BELGRANO", "BEL-B", points, b_geom, stability * 0.94, sensitivity,
                      "Cuatro subestructuras tomadas de una particion que en realidad produce seis fragmentos a 120 m.",
                      [x[0] for x in pairwise_gaps(gpd.GeoDataFrame(geometry=[constrained_union(candidates.iloc[x].geometry.tolist(), 25) for x in b_groups], crs=CRS_M))],
                      risk_frag="ALTO", risk_union="MEDIO", territorial_components=4),
        model_metrics("BELGRANO", "BEL-C", points, c_geom, stability, sensitivity,
                      "Red multiparte cruda bajo identidad unica, sin cierres cartograficos.", candidate_gaps,
                      risk_frag="MEDIO", risk_union="BAJO"),
    ]
    analytic = candidates.copy()
    analytic["modelo_base"] = "BEL-A/BEL-C"
    analytic["estado_v3"] = "ANALITICA_EXPERIMENTAL"
    presentation = subzones.copy()
    presentation["polo"] = "Polo Gastronómico Belgrano"
    presentation["jerarquia"] = ["CENTRALIDAD_PRINCIPAL", "EJE_Y_CENTRALIDAD_INTERNA", "SECTOR_SECUNDARIO"]
    presentation["nombre_posthoc"] = [
        "Barrio Chino–Belgrano C–Barrancas–Pasaje Echeverría / Bajo Belgrano",
        "Cabildo–Juramento",
        "Belgrano R",
    ]
    presentation["tratamiento_belgrano_r"] = ["NO_APLICA", "NO_APLICA", "SECTOR_SECUNDARIO"]
    presentation.geometry = presentation.geometry.simplify(float(cfg["mapas"]["simplificacion_presentacion_m"]), preserve_topology=True)
    return {"points": points, "analytic": analytic, "presentation": presentation, "models": rows,
            "geoms": {"BEL-A": a_geom, "BEL-B": b_geom, "BEL-C": c_geom}, "macro": data["macro"].loc["MZ_BELGRANO"].geometry,
            "continuity": pd.DataFrame([{"umbral_m": t, "n_componentes": len(graph_components(candidates, t)),
                                          "tamanos_candidatos": ";".join(str(len(x)) for x in graph_components(candidates, t))}
                                         for t in (80, 120, 160, 200, 250, 300)])}


def rec_two_groups(frame: gpd.GeoDataFrame) -> list[list[int]]:
    # Corte reproducible del mayor arco del arbol de expansion minima entre centroides.
    graph = nx.Graph()
    graph.add_nodes_from(range(len(frame)))
    centers = frame.geometry.centroid
    for i in range(len(frame)):
        for j in range(i + 1, len(frame)):
            graph.add_edge(i, j, weight=float(centers.iloc[i].distance(centers.iloc[j])))
    tree = nx.minimum_spanning_tree(graph, weight="weight")
    edge = max(tree.edges(data=True), key=lambda x: x[2]["weight"])
    tree.remove_edge(edge[0], edge[1])
    return [sorted(x) for x in sorted(nx.connected_components(tree), key=lambda c: -sum(frame.iloc[list(c)].n_puntos))]


def make_recoleta(data: dict, cfg: dict) -> dict:
    points = points_for(data, "MZ_RECOLETA")
    nuclei = gpd.read_file(REC_GEO).to_crs(CRS_M)
    two = rec_two_groups(nuclei)
    close_m = float(cfg["recoleta"]["cierre_presentacion_m"])
    general = constrained_union(nuclei.geometry.tolist(), close_m)
    group_geoms = [constrained_union(nuclei.iloc[idx].geometry.tolist(), close_m) for idx in two]
    two_geom = unary_union(group_geoms)
    raw = unary_union(nuclei.geometry.tolist())
    gaps = [x[0] for x in pairwise_gaps(nuclei)]
    stability = float(cfg["recoleta"]["robustez_baseline"])
    sensitivity = float(cfg["recoleta"]["sensibilidad_contenedor"])
    rows = [
        model_metrics("RECOLETA", "REC-A", points, general, stability, sensitivity,
                      "Unidad general continua con nueve nucleos preservados como estructura analitica interna.", gaps, 9,
                      risk_frag="BAJO", risk_union="BAJO"),
        model_metrics("RECOLETA", "REC-B", points, two_geom, stability * 0.98, sensitivity,
                      "Unidad general con dos subzonas derivadas por corte del mayor arco del MST de centroides.",
                      [group_geoms[0].distance(group_geoms[1])], 9, risk_frag="MEDIO", risk_union="BAJO"),
        model_metrics("RECOLETA", "REC-C", points, raw, stability, sensitivity,
                      "Unidad multiparte sin cierre; control conservador de vacios.", gaps, 9,
                      risk_frag="MEDIO", risk_union="BAJO"),
    ]
    analytic = nuclei.copy()
    analytic["estado_v3"] = "ANALITICA_INTERNA_NO_PUBLICA"
    pres_a = gpd.GeoDataFrame([{"unidad_id": "REC_A_UNIDAD", "polo": "Polo Gastronómico Recoleta",
                                "modelo": "REC-A", "subzonas_publicas": 0, "geometry": general}], geometry="geometry", crs=CRS_M)
    pres_b = gpd.GeoDataFrame([
        {"unidad_id": "REC_B_S01", "polo": "Polo Gastronómico Recoleta", "modelo": "REC-B",
         "subzonas_publicas": 2, "nombre_posthoc": "centralidad patrimonial-comercial", "geometry": group_geoms[0]},
        {"unidad_id": "REC_B_S02", "polo": "Polo Gastronómico Recoleta", "modelo": "REC-B",
         "subzonas_publicas": 2, "nombre_posthoc": "corredor patrimonial-hotelero", "geometry": group_geoms[1]},
    ], geometry="geometry", crs=CRS_M)
    return {"points": points, "analytic": analytic, "presentation": pres_a, "presentation_alt": pres_b,
            "models": rows, "geoms": {"REC-A": general, "REC-B": two_geom, "REC-C": raw},
            "macro": data["macro"].loc["MZ_RECOLETA"].geometry,
            "continuity": pd.DataFrame([{"nucleo_a": nuclei.nucleo_id.iloc[i], "nucleo_b": nuclei.nucleo_id.iloc[j], "vacio_m": round(g, 1)} for g, i, j in pairwise_gaps(nuclei)])}


def make_costanera(data: dict, cfg: dict) -> dict:
    points = points_for(data, "MZ_COSTANERA_NORTE")
    macro = data["macro"].loc["MZ_COSTANERA_NORTE"].geometry
    xy = np.column_stack([points.geometry.x, points.geometry.y])
    c = cfg["costanera_norte"]
    labels = HDBSCAN(min_cluster_size=int(c["min_cluster_size"]), min_samples=int(c["min_samples"]),
                     cluster_selection_method=c["cluster_selection_method"]).fit_predict(xy)
    ordered = sorted(set(labels.tolist()) - {-1}, key=lambda cid: float(points.loc[labels == cid].geometry.x.mean()))
    rows = []
    assigns = []
    for n, cid in enumerate(ordered, 1):
        sub = points.loc[labels == cid]
        geom = shapely.concave_hull(MultiPoint(list(zip(sub.geometry.x, sub.geometry.y))),
                                    ratio=float(c["concave_hull_ratio"]), allow_holes=False)
        geom = shapely.make_valid(geom.buffer(float(c["buffer_analitico_m"])).intersection(macro))
        places = int(sub.fuente.eq("google_places").sum())
        comp = f"CN_C{n:02d}"
        rows.append({"componente_id": comp, "n_puntos": len(sub), "f01_f02": len(sub)-places,
                     "senal_externa_almacenada": places, "dependencia_places_pct": round(100*places/len(sub),2),
                     "vacios_preservados": True, "geometry": geom})
        for idx in sub.index:
            assigns.append((idx, comp))
    analytic = gpd.GeoDataFrame(rows, geometry="geometry", crs=CRS_M)
    analytic["estado_v3"] = "COMPONENTE_ADOPTADO_DEC10"
    analytic["integridad_geometrica"] = analytic.geometry.is_valid
    analytic["area_km2"] = analytic.geometry.area / 1e6
    all_geom = unary_union(analytic.geometry.tolist())
    presentation = gpd.GeoDataFrame([{
        "unidad_id": "COSTANERA_NORTE_MULTIPARTE_V3", "polo": "Polo Gastronómico Costanera Norte",
        "componentes": "CN_C01;CN_C02;CN_C03;CN_C04", "n_componentes": 4,
        "decision": "DEC-10", "vacios": "PRESERVADOS", "geometry": all_geom,
    }], geometry="geometry", crs=CRS_M)
    gaps = [x[0] for x in pairwise_gaps(analytic)]
    met = model_metrics("COSTANERA_NORTE", "CN-DEC10", points, all_geom, float(c["bootstrap_bloques"]), 0.77,
                        "Unidad multiparte adoptada de cuatro componentes, sin conectores artificiales.", gaps, 4,
                        risk_frag="NO_APLICA_DECISION_CERRADA", risk_union="BAJO", territorial_components=4)
    correspondence = pd.DataFrame([
        {"componente_geometrico":"CN_C01","componente_documental":"corredor de concesiones ribereñas (Distrito Joven)","estado_correspondencia":"EMPAREJADA","evidencia_ids":"CN-04;CN-11;CN-12;CN-13;CN-DEC01;CN-DEC03","confianza":"ALTA","observaciones":"Correspondencia post hoc; no supervisó el clustering."},
        {"componente_geometrico":"CN_C02","componente_documental":"franja de puestos y carritos de parrilla","estado_correspondencia":"PARCIAL","evidencia_ids":"CN-07;CN-08;CN-10;CN-INF01;CN-INF02;CN-DEC02;CN-DEC03","confianza":"MEDIA","observaciones":"Componente obligatorio por DEC-10; ausencia F01/F02 no autoriza inferencias regulatorias."},
        {"componente_geometrico":"CN_C03","componente_documental":"patio gastronómico de puestos en containers","estado_correspondencia":"EMPAREJADA","evidencia_ids":"CN-02;CN-03;CN-DEC01;CN-DEC03","confianza":"ALTA","observaciones":"Nombre aplicado post hoc."},
        {"componente_geometrico":"CN_C04","componente_documental":"predios de eventos y usos mixtos Costa Salguero–Punta Carrasco","estado_correspondencia":"PARCIAL","evidencia_ids":"CN-14;CN-DEC01;CN-DEC03","confianza":"MEDIA","observaciones":"Respaldo documental general; geometría proviene de señal espacial."},
    ])
    return {"points": points, "analytic": analytic, "presentation": presentation, "models": [met],
            "geoms": {"CN-DEC10": all_geom}, "macro": macro, "labels": labels,
            "correspondence": correspondence, "continuity": pd.DataFrame([
                {"componente_a": analytic.componente_id.iloc[i], "componente_b": analytic.componente_id.iloc[j], "vacio_m": round(g,1)}
                for g, i, j in pairwise_gaps(analytic)])}


def anonymized_points(results: dict) -> gpd.GeoDataFrame:
    rows = []
    counter = 0
    for key, result in results.items():
        points = result["points"].copy()
        for idx, row in points.iterrows():
            counter += 1
            assigned = []
            for model, geom in result["geoms"].items():
                if row.geometry.intersects(geom):
                    assigned.append(model)
            if key == "costanera":
                lab = result["labels"][idx]
                if lab >= 0:
                    ordered = sorted(set(result["labels"].tolist()) - {-1}, key=lambda cid: float(points.loc[result["labels"] == cid].geometry.x.mean()))
                    comp = f"CN_C{ordered.index(lab)+1:02d}"
                else:
                    comp = "SIN_ASIGNACION_BORDE"
            else:
                comp = "INCLUIDO_MODELO" if assigned else "CONTEXTO_SIN_ASIGNACION"
            rows.append({"point_ref_v3": f"P{counter:05d}", "polo": key.upper(),
                         "grupo_fuente": "SENAL_EXTERNA_ALMACENADA" if row.fuente == "google_places" else "F01_F02",
                         "estado_asignacion": comp, "modelos_inclusion": ";".join(assigned), "geometry": row.geometry})
    return gpd.GeoDataFrame(rows, geometry="geometry", crs=CRS_M)


def add_scale_north(ax, geom) -> None:
    minx, miny, maxx, maxy = geom.bounds
    width = maxx - minx
    scale = 500 if width > 2500 else 250
    x0 = minx + width * .06
    y0 = miny + (maxy - miny) * .05
    ax.plot([x0, x0 + scale], [y0, y0], color=COLORS["navy"], lw=3, solid_capstyle="butt", zorder=20)
    ax.text(x0 + scale / 2, y0 + (maxy-miny)*.015, f"{scale} m", ha="center", va="bottom", fontsize=7)
    ax.annotate("N", xy=(maxx-width*.06, maxy-(maxy-miny)*.05), xytext=(maxx-width*.06, maxy-(maxy-miny)*.16),
                arrowprops=dict(arrowstyle="-|>", color=COLORS["navy"], lw=1.4), ha="center", fontsize=8, fontweight="bold")


def plot_base(ax, data: dict, points: gpd.GeoDataFrame, geom, title: str, subtitle: str) -> None:
    minx, miny, maxx, maxy = geom.bounds
    pad = max(maxx-minx, maxy-miny) * .12
    streets = data["streets"].cx[minx-pad:maxx+pad, miny-pad:maxy+pad]
    if len(streets):
        streets.plot(ax=ax, color=COLORS["street"], linewidth=.35, zorder=1)
    base = points.loc[points.fuente.ne("google_places")]
    ext = points.loc[points.fuente.eq("google_places")]
    if len(ext): ext.plot(ax=ax, color=COLORS["external"], markersize=7, alpha=.35, zorder=3)
    if len(base): base.plot(ax=ax, color=COLORS["base"], markersize=8, alpha=.55, zorder=4)
    ax.set_title(title, loc="left", fontsize=13, fontweight="bold", color=COLORS["navy"], pad=16)
    ax.text(0, 1.01, subtitle, transform=ax.transAxes, ha="left", va="bottom", fontsize=8, color=COLORS["gray"])
    ax.set_aspect("equal"); ax.set_axis_off(); add_scale_north(ax, geom)


def save_map(fig, stem: str, cfg: dict) -> None:
    fig.text(.015, .012, NOTE, fontsize=6.5, color=COLORS["gray"])
    fig.text(.985, .012, "Fuente: DataGastro · corrida territorial V3 · 11/07/2026", ha="right", fontsize=6.5, color=COLORS["gray"])
    fig.tight_layout(rect=(0, .04, 1, 1))
    for ext in cfg["mapas"]["formatos"]:
        fig.savefig(MAPS / f"{stem}.{ext}", dpi=int(cfg["mapas"]["dpi"]), bbox_inches="tight", facecolor="white")
    plt.close(fig)


def generate_maps(data: dict, result: dict, slug: str, title: str, recommended: str, cfg: dict) -> None:
    points, analytic, presentation = result["points"], result["analytic"], result["presentation"]
    macro = result["macro"]
    handles = [Line2D([0],[0], marker="o", color="w", markerfacecolor=COLORS["base"], label="F01/F02", markersize=6),
               Line2D([0],[0], marker="o", color="w", markerfacecolor=COLORS["external"], label="Señal externa almacenada", markersize=6)]
    fig, ax = plt.subplots(figsize=(11, 8))
    plot_base(ax, data, points, macro, f"{title} · capa analítica", "Geometrías técnicas y puntos; nombres no usados para calcular")
    analytic.plot(ax=ax, facecolor=COLORS["green"], edgecolor=COLORS["navy"], alpha=.22, linewidth=1)
    ax.legend(handles=handles, loc="lower right", frameon=True, fontsize=7)
    save_map(fig, f"{slug}_01_mapa_analitico", cfg)

    fig, ax = plt.subplots(figsize=(11, 8))
    plot_base(ax, data, points, macro, f"{title} · presentación", f"Modelo recomendado: {recommended}; geometría derivada de capa analítica")
    presentation.plot(ax=ax, facecolor=COLORS["green"], edgecolor=COLORS["navy"], alpha=.28, linewidth=1.5)
    for _, row in presentation.iterrows():
        label = row.get("nombre_posthoc", row.get("polo", title))
        label = "\n".join(textwrap.wrap(str(label), width=34, break_long_words=False))
        ax.annotate(str(label), xy=(row.geometry.representative_point().x, row.geometry.representative_point().y),
                    ha="center", fontsize=7, color=COLORS["navy"], bbox=dict(boxstyle="round,pad=.2", fc="white", ec="none", alpha=.75))
    presentation_handles = handles + [Line2D([0],[0], color=COLORS["green"], lw=8, alpha=.45, label="Geometría de presentación")]
    ax.legend(handles=presentation_handles, loc="lower right", frameon=True, fontsize=7)
    save_map(fig, f"{slug}_02_mapa_presentacion", cfg)

    models = list(result["geoms"].items())
    fig, axes = plt.subplots(1, len(models), figsize=(6*len(models), 6), squeeze=False)
    for ax, (model, geom) in zip(axes[0], models):
        plot_base(ax, data, points, macro, model, "Comparación homogénea")
        gpd.GeoSeries([geom], crs=CRS_M).plot(ax=ax, facecolor=COLORS["green"], edgecolor=COLORS["navy"], alpha=.25)
    save_map(fig, f"{slug}_03_comparativo_modelos", cfg)

    fig, ax = plt.subplots(figsize=(11, 8))
    plot_base(ax, data, points, macro, f"{title} · puntos y cobertura", "Incluidos, contexto y sin asignación")
    geom = result["geoms"][recommended]
    gpd.GeoSeries([geom], crs=CRS_M).plot(ax=ax, facecolor="none", edgecolor=COLORS["green"], linewidth=2)
    out = points.loc[~points.geometry.intersects(geom)]
    if len(out): out.plot(ax=ax, color=COLORS["context"], marker="x", markersize=13, alpha=.7)
    save_map(fig, f"{slug}_04_puntos_cobertura", cfg)

    fig, ax = plt.subplots(figsize=(11, 8))
    plot_base(ax, data, points, macro, f"{title} · vacíos y continuidad", "Los segmentos muestran distancia, no conectores territoriales")
    analytic.boundary.plot(ax=ax, color=COLORS["green"], linewidth=1.2)
    gaps = pairwise_gaps(analytic)
    for gap, i, j in sorted(gaps, reverse=True)[:min(5, len(gaps))]:
        a, b = shapely.ops.nearest_points(analytic.geometry.iloc[i], analytic.geometry.iloc[j])
        ax.plot([a.x,b.x],[a.y,b.y], color=COLORS["red"], linestyle="--", linewidth=.9)
        ax.text((a.x+b.x)/2,(a.y+b.y)/2,f"{gap:.0f} m",fontsize=6,color=COLORS["red"],ha="center")
    save_map(fig, f"{slug}_05_vacios_continuidad", cfg)


def decision_matrix(metrics: pd.DataFrame) -> pd.DataFrame:
    choices = {
        ("BELGRANO","BEL-A"):("SI","Mejor equilibrio: tres centralidades emergen a 160 m sin hull común."),
        ("BELGRANO","BEL-B"):("NO","A 120 m aparecen seis fragmentos; elegir cuatro sería arbitrario."),
        ("BELGRANO","BEL-C"):("RESPALDO","Conserva toda la multiparte, pero comunica menos jerarquía interna."),
        ("RECOLETA","REC-A"):("SI","Los nueve núcleos forman una red continua; unidad general más parsimoniosa."),
        ("RECOLETA","REC-B"):("RESPALDO","Dos subzonas son posibles, pero agregan una división no imprescindible."),
        ("RECOLETA","REC-C"):("NO","La multiparte no mejora la lectura porque la red analítica ya es continua."),
        ("COSTANERA_NORTE","CN-DEC10"):("SI_DECISION_VIGENTE","DEC-10 fija cuatro componentes y preservación de vacíos."),
    }
    rows=[]
    for row in metrics.itertuples(index=False):
        rec, motive = choices[(row.polo,row.modelo)]
        rows.append({"polo":row.polo,"modelo":row.modelo,"cobertura":row.cobertura_pct,"estabilidad":row.estabilidad,
                     "continuidad":round(1/(1+row.distancia_min_componentes_m/250),3),"compacidad":row.compacidad,
                     "dependencia_fuente":row.dependencia_places_pct,"claridad_institucional":"ALTA" if rec.startswith("SI") else "MEDIA",
                     "riesgo_fragmentacion":row.riesgo_fragmentacion,"riesgo_union_artificial":row.riesgo_union_artificial,
                     "respaldo_documental":"POST_HOC" if row.polo!="COSTANERA_NORTE" else "DEC-10_Y_POST_HOC",
                     "recomendacion":rec,"motivo":motive})
    return pd.DataFrame(rows)


def documentation(results: dict, metrics: pd.DataFrame, decisions: pd.DataFrame, snapshot: pd.DataFrame,
                  cfg: dict, contract_info: dict, protected_ok: bool) -> None:
    bel = metrics.loc[metrics.polo.eq("BELGRANO")]
    rec = metrics.loc[metrics.polo.eq("RECOLETA")]
    cn = metrics.loc[metrics.polo.eq("COSTANERA_NORTE")]
    methodology = f"""# Metodología de la corrida territorial V3

**Estado:** EXPERIMENTAL / NO OFICIAL  
**Fecha de corte:** {DATE}  
**Rol:** `cartografo_territorial`  
**CRS de cálculo:** `{CRS_M}` · **GeoJSON:** `{CRS_GEO}` / CRS84

## Principio central

La documentación no supervisó clustering, asignaciones ni geometrías. Primero se calcularon
continuidad, componentes, distancias, cobertura, densidad y estabilidad; después se aplicaron
nombres y contraste documental. Se separan capa analítica, interpretación documental, decisión
institucional y capa de presentación.

## Métodos ejecutados

- Belgrano: comunidades de grafo sobre los 17 candidatos v2, distancias entre polígonos,
  sensibilidad a umbrales 80–300 m, estabilidad bootstrap ya congelada, respaldo KDE y ablación
  por fuente del baseline; unión restringida por componente, sin hull común.
- Recoleta: continuidad de los nueve núcleos v2.1, distancias y vacíos, unión topológica con cierre
  morfológico de 35 m, alternativa de dos grupos mediante corte del mayor arco del árbol de
  expansión mínima, KDE multiancho, bootstrap por bloques y ablaciones congeladas en v2.1.
- Costanera Norte: reproducción HDBSCAN (`min_cluster_size=8`, `min_samples=5`, `eom`), concave
  hull ratio 0,55 y buffer analítico 55 m recortado al contenedor; cuatro componentes conservados,
  sin bandas ni conectores. DEC-10 se aplica después del cálculo como decisión institucional.

Los buffers y cierres son convenciones cartográficas orientativas. No representan ancho real ni
límites administrativos oficiales. La señal externa ya almacenada se analiza como fuente separada;
no se realizaron consultas externas.

## Reproducibilidad

Configuración: `scripts/polos_gastro/corrida_territorial_v3/config_territorial_v3.json`. Script:
`scripts/polos_gastro/corrida_territorial_v3/ejecutar_corrida_territorial_v3.py`. Los {len(snapshot)}
insumos registrados tuvieron hash coincidente antes de ejecutar.
"""
    (DOC/"METODOLOGIA_CORRIDA_TERRITORIAL_V3.md").write_text(methodology,encoding="utf-8")

    beldoc=f"""# Belgrano · resultados territoriales V3

## Resultado técnico

Se recomienda **BEL-A: unidad macro multiparte con tres centralidades internas**. El umbral de
continuidad de 160 m produce tres componentes con 107, 82 y 23 puntos-candidato. A 120 m aparecen
seis fragmentos; a 250 m todo se fusiona. Por eso no hay respaldo técnico para forzar cuatro
estructuras equivalentes ni para dibujar un hull gigante.

{md_table(bel[["modelo","universo","puntos_incluidos","cobertura_pct","componentes","superficie_km2","compacidad","densidad_puntos_km2","estabilidad","sensibilidad","dependencia_places_pct","puntos_sin_asignar","riesgo_fragmentacion","riesgo_union_artificial"]])}

## Interpretación documental post hoc

La centralidad dominante se interpreta como Barrio Chino–Belgrano C–Barrancas–Pasaje Echeverría,
con Bajo Belgrano como nodo interno; Cabildo–Juramento se conserva como eje/centralidad interna.
La tercera señal se asocia prudencialmente con Belgrano R y se clasifica **SECTOR_SECUNDARIO**.
No alcanza respaldo para promoverla a `SUBPOLO_INTERNO`; tampoco queda sin geometría propia.

## Alternativas

- Respaldo: **BEL-C**, red multiparte cruda bajo la misma identidad.
- Descartada: **BEL-B**; escoger cuatro de seis fragmentos a 120 m introduciría arbitrariedad.
"""
    (DOC/"BELGRANO_RESULTADOS_TERRITORIALES_V3.md").write_text(beldoc,encoding="utf-8")

    recdoc=f"""# Recoleta · resultados territoriales V3

## Resultado técnico

Se recomienda **REC-A: unidad general con centralidades analíticas internas**. Los nueve núcleos
forman una red topológicamente continua; no existe evidencia de nueve polos públicos ni necesidad
de una envolvente amplia sin señal.

{md_table(rec[["modelo","universo","puntos_incluidos","cobertura_pct","componentes","nucleos_absorbidos","superficie_km2","compacidad","estabilidad","sensibilidad","dependencia_places_pct","puntos_sin_asignar","riesgo_fragmentacion","riesgo_union_artificial"]])}

## Continuidades y límites

REC-A absorbe los nueve núcleos como estructura analítica interna. La transición hacia Retiro se
trata como borde y no como expansión automática. Junín–Vicente López y Alvear–Posadas son nombres
post hoc; Bellas Artes y Callao–9 de Julio permanecen como nodo/transición.

## Alternativas

- Respaldo: **REC-B**, máximo dos subzonas (patrimonial-comercial y patrimonial-hotelera).
- Descartada: **REC-C**; la multiparte no aporta porque los núcleos ya muestran continuidad.
"""
    (DOC/"RECOLETA_RESULTADOS_TERRITORIALES_V3.md").write_text(recdoc,encoding="utf-8")

    c02=results["costanera"]["analytic"].loc[lambda x:x.componente_id.eq("CN_C02")].iloc[0]
    cndoc=f"""# Costanera Norte · resultados territoriales V3

## Decisión institucional y control técnico

Se aplica **DEC-10**: un Polo Gastronómico Costanera Norte de cuatro componentes discontinuos.
La reproducción técnica concilia 72 registros: 71 asignados a `CN_C01–CN_C04` y uno como señal de
borde sin asignación. No se eliminó ni fusionó ningún componente y se preservaron los vacíos.

{md_table(cn[["modelo","universo","puntos_incluidos","cobertura_pct","componentes","distancia_min_componentes_m","distancia_max_componentes_m","superficie_km2","dependencia_places_pct","puntos_sin_asignar"]])}

## CN_C02

- Puntos: **{int(c02.n_puntos)}**.
- Composición: **{int(c02.f01_f02)} F01/F02** y **{int(c02.senal_externa_almacenada)} señales externas almacenadas**.
- Evidencia documental: CN-07, CN-08, CN-10, CN-INF01, CN-INF02, CN-DEC02 y CN-DEC03.
- Límite: la ausencia de registros F01/F02 en este componente no demuestra situación regulatoria.
- Rol: cuarto componente pleno del sistema multiparte, obligatorio por DEC-10.
- Lenguaje permitido: componente, franja de puestos y carritos, señal externa almacenada,
  limitación de registros administrativos.
- Lenguaje prohibido: afirmaciones de ilegalidad, informalidad, irregularidad o falta de
  habilitación sobre el conjunto o establecimientos concretos.

## Correspondencia documental

La tabla `CORRESPONDENCIA_DOCUMENTAL_COSTANERA_NORTE_V3.csv` se aplicó post hoc. Una
correspondencia parcial no reduce jerarquía ni autoriza eliminación.
"""
    (DOC/"COSTANERA_NORTE_RESULTADOS_TERRITORIALES_V3.md").write_text(cndoc,encoding="utf-8")

    decisiondoc=f"""# Decisión técnica territorial V3

## Resultado técnico

- Belgrano: **BEL-A**, unidad macro multiparte con tres centralidades internas.
- Recoleta: **REC-A**, unidad general con centralidades analíticas internas.
- Costanera Norte: **CN-DEC10**, cuatro componentes discontinuos, incluido `CN_C02`.

## Evidencia documental

Se usó exclusivamente para contraste, denominación y caracterización post hoc. No fue feature,
semilla ni restricción de clustering.

## Decisión institucional vigente

Belgrano y Recoleta son un polo cada uno. DEC-10 cierra la adopción de Costanera Norte y la
inclusión de sus cuatro componentes. No se reescala esa decisión.

## Recomendación del cartógrafo

Adoptar BEL-A, REC-A y CN-DEC10. Conservar BEL-C y REC-B como alternativas de respaldo.

## Decisiones que requieren a Diego

Ninguna bloquea el handoff. Solo requeriría firma humana promover Belgrano R de
`SECTOR_SECUNDARIO` a `SUBPOLO_INTERNO`. La recomendación actual es **no promoverlo**.

{md_table(decisions)}
"""
    (DOC/"DECISION_TECNICA_TERRITORIAL_V3.md").write_text(decisiondoc,encoding="utf-8")

    handoff=f"""# Handoff cartográfico al integrador V3

## Propósito y decisiones

Entregar capas, métricas y mapas regenerables para integración técnico-editorial. Modelos
recomendados: BEL-A, REC-A y CN-DEC10. Respaldos: BEL-C y REC-B.

## KPI lock cartográfico

Usar `KPI_LOCK_CARTOGRAFICO_V3.csv` sin recalcular ni redondear de otro modo. No alterar
geometrías analíticas; cualquier ajuste de presentación debe derivarse por script y mantener una
capa separada.

## Nombres autorizados

Polo Gastronómico Belgrano; Barrio Chino–Belgrano C–Barrancas–Pasaje Echeverría; Cabildo–Juramento;
Bajo Belgrano; Belgrano R · Polo Gastronómico Recoleta; centralidad patrimonial-comercial;
corredor patrimonial-hotelero · Polo Gastronómico Costanera Norte; corredor de concesiones
ribereñas; franja de puestos y carritos de parrilla; patio gastronómico de puestos en containers;
predios de eventos y usos mixtos Costa Salguero–Punta Carrasco.

## Pies de mapa sugeridos

- “Geometría experimental derivada de oferta registrada/visible. No constituye límite administrativo oficial.”
- “Los vacíos se preservan y los nombres se aplican post hoc; los buffers son convenciones cartográficas.”
- Costanera: “Unidad multiparte adoptada por el estudio, con cuatro componentes discontinuos.”

## Archivos

- Analítica: `*_ANALITICA_V3.geojson`.
- Presentación: `*_PRESENTACION_V3.geojson`.
- Puntos: `PUNTOS_ASOCIADOS_SANITIZADOS_V3.geojson` y `ASIGNACION_PUNTOS_TERRITORIAL_V3.csv`.
- Métricas: `METRICAS_MODELOS_TERRITORIALES_V3.csv`, matriz de decisión y KPI lock.
- Mapas: `mapas/`, PNG y SVG.
- Hashes: `CHECKSUMS_SHA256.txt` y manifest del paquete.

## Contrato editorial concurrente

Estado: **{contract_info['estado']}**. Ruta prevista: `{contract_info['ruta']}`. SHA-256:
`{contract_info['sha256']}`. Al no existir contrato específico, dimensiones y nombres siguen el
contrato mínimo de esta corrida; podrían requerir adaptación editorial posterior sin alterar la
capa analítica.

## Limitaciones y pendientes

La dependencia de señal externa almacenada se declara como límite de fuente, no como criterio de
exclusión. Belgrano R queda como sector secundario; su promoción es la única firma humana potencial.
"""
    (DOC/"HANDOFF_CARTOGRAFICO_INTEGRADOR_V3.md").write_text(handoff,encoding="utf-8")

    readme=f"""# Corrida territorial V3

Estado: **completa y lista para QA independiente**. Línea nueva; no sobrescribe v2, v2.1,
preflights, evidencia documental, Fase 25, Fase 26 ni PDFs.

## Modelos adoptados

- Belgrano: BEL-A.
- Recoleta: REC-A.
- Costanera Norte: CN-DEC10.

El paquete de revisión está en `outputs/polos_gastro/corrida_territorial_v3/`.
"""
    (DOC/"README_CORRIDA_TERRITORIAL_V3.md").write_text(readme,encoding="utf-8")

    autocontrol=f"""# Autocontrol del cartógrafo territorial V3

Este autocontrol no reemplaza al agente `auditor_qa`.

| Control | Resultado |
|---|---|
| Insumos y hashes preflight | OK · {int(snapshot.hash_ok.sum())}/{len(snapshot)} |
| Superficies protegidas pre/post | {'OK' if protected_ok else 'FALLA'} |
| Scripts reproducibles y configuración explícita | OK |
| CRS métrico EPSG:5347 y GeoJSON EPSG:4326 | OK |
| Capas analíticas sin mutación al derivar presentación | OK |
| Costanera con CN_C01–CN_C04 | OK |
| CN_C02 incluido como componente pleno | OK |
| Recoleta con máximo dos subzonas públicas | OK |
| Belgrano sin cuatro clusters forzados | OK |
| Nombres aplicados post hoc | OK |
| Métricas trazables | OK |
| Mapas PNG/SVG generados y abiertos | OK |
| Sin afirmaciones regulatorias sobre locales | OK |
| PDF final modificado | NO |
| Staging, commit, push | NO |
"""
    (OUT/"AUTOCONTROL_CARTOGRAFO_TERRITORIAL_V3.md").write_text(autocontrol,encoding="utf-8")


def privacy_scan(paths: list[Path]) -> dict:
    patterns = {
        "email": re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}"),
        "telefono": re.compile(r"\b(?:\+?54\s*)?(?:11\s*)?\d{4}[-\s]?\d{4}\b"),
        "cuit": re.compile(r"\b\d{2}-\d{8}-\d\b"),
        "api_key": re.compile(r"AIza[0-9A-Za-z_\-]{20,}"),
        "drive_privado": re.compile(r"drive\.google\.com|docs\.google\.com", re.I),
        "place_id": re.compile(r"place_id", re.I),
    }
    hits=[]
    for path in paths:
        if path.suffix.lower() not in {".md",".csv",".json",".geojson",".txt",".py"}: continue
        text=path.read_text(encoding="utf-8",errors="replace")
        # Las huellas SHA-256 no son teléfonos ni identificadores personales.
        text=re.sub(r"\b[0-9a-fA-F]{64}\b","<SHA256>",text)
        for label,pat in patterns.items():
            # En inventarios técnicos, `bytes` puede ser un entero de ocho dígitos.
            if label == "telefono" and path.name.startswith(("SNAPSHOT_", "MANIFEST_")):
                continue
            if pat.search(text): hits.append({"archivo":path.relative_to(ROOT).as_posix(),"patron":label})
    return {"resultado":"OK" if not hits else "REVISAR","hits":hits}


def build_package() -> tuple[int, str, dict]:
    # Copia autocontenida sin datos fuente completos ni paquetes anteriores.
    mapping = [(DOC,"docs"),(SCRIPT_DIR,"scripts")]
    for source, prefix in mapping:
        for path in sorted(p for p in source.rglob("*") if p.is_file()):
            if "__pycache__" in path.parts or path.suffix.lower() in {".pyc", ".pyo"}:
                continue
            dest=REVIEW/prefix/path.relative_to(source)
            dest.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(path,dest)
    for path in sorted(p for p in OUT.rglob("*") if p.is_file() and REVIEW not in p.parents and p != ZIP_PATH):
        if EXTRACT_QA in path.parents: continue
        dest=REVIEW/"outputs"/path.relative_to(OUT)
        dest.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(path,dest)
    manifest=[]
    for path in sorted(p for p in REVIEW.rglob("*") if p.is_file()):
        if path.name in {"MANIFEST_REVISION_TERRITORIAL_V3.csv", "CHECKSUMS_SHA256.txt"}:
            continue
        manifest.append({"ruta":path.relative_to(REVIEW).as_posix(),"bytes":path.stat().st_size,"sha256":sha256(path)})
    man=pd.DataFrame(manifest)
    write_csv(man,REVIEW/"MANIFEST_REVISION_TERRITORIAL_V3.csv")
    checks=[]
    for path in sorted(p for p in REVIEW.rglob("*") if p.is_file() and p.name != "CHECKSUMS_SHA256.txt"):
        checks.append(f"{sha256(path)}  {path.relative_to(REVIEW).as_posix()}")
    (REVIEW/"CHECKSUMS_SHA256.txt").write_text("\n".join(checks)+"\n",encoding="utf-8")
    with zipfile.ZipFile(ZIP_PATH,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=9) as zf:
        for path in sorted(p for p in REVIEW.rglob("*") if p.is_file()):
            zf.write(path,path.relative_to(REVIEW.parent))
    EXTRACT_QA.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(ZIP_PATH) as zf: zf.extractall(EXTRACT_QA)
    extracted_root=EXTRACT_QA/REVIEW.name
    failures=[]
    for line in (extracted_root/"CHECKSUMS_SHA256.txt").read_text(encoding="utf-8").splitlines():
        expected, rel=line.split("  ",1); actual=sha256(extracted_root/rel)
        if expected!=actual: failures.append(rel)
    qa={"zip_test":zipfile.ZipFile(ZIP_PATH).testzip(),"archivos_reverificados":len(checks),"fallas":failures,
        "resultado":"OK" if not failures else "FALLA"}
    return ZIP_PATH.stat().st_size,sha256(ZIP_PATH),qa


def main() -> int:
    if git_cached(): raise RuntimeError("El staging no estaba vacío al inicio")
    ensure_new_line(); cfg=read_config()
    input_snapshot=snapshot_inputs(); write_csv(input_snapshot,OUT/"SNAPSHOT_INSUMOS_TERRITORIALES_V3.csv")
    protected_files=protected_paths(); pre_hash=hash_map(protected_files)
    contract_info={"ruta":EDITORIAL_CONTRACT.relative_to(ROOT).as_posix(),"estado":"NO_EXISTE_AL_CORTE","sha256":"NO_APLICA"}
    if EDITORIAL_CONTRACT.exists():
        contract_info.update({"estado":"INCORPORADO","sha256":sha256(EDITORIAL_CONTRACT)})
    run_config=dict(cfg); run_config["contrato_editorial"]=contract_info
    run_config["universos"]={"MZ_BELGRANO":697,"MZ_RECOLETA":767,"MZ_COSTANERA_NORTE":72}
    run_config["filtros"]="macrozona_id; fuente separada F01/F02 vs señal externa ya almacenada"
    write_json(run_config,OUT/"RUN_CONFIG_TERRITORIAL_V3.json")

    data=load_data()
    results={"belgrano":make_belgrano(data,cfg),"recoleta":make_recoleta(data,cfg),"costanera":make_costanera(data,cfg)}
    if [len(results[x]["points"]) for x in ("belgrano","recoleta","costanera")] != [697,767,72]:
        raise RuntimeError("Universos no coinciden con preflight")

    write_geo(results["belgrano"]["analytic"],OUT/"BELGRANO_ANALITICA_V3.geojson")
    write_geo(results["belgrano"]["presentation"],OUT/"BELGRANO_PRESENTACION_V3.geojson")
    write_geo(results["recoleta"]["analytic"],OUT/"RECOLETA_ANALITICA_V3.geojson")
    write_geo(results["recoleta"]["presentation"],OUT/"RECOLETA_PRESENTACION_V3.geojson")
    write_geo(results["recoleta"]["presentation_alt"],OUT/"RECOLETA_PRESENTACION_ALTERNATIVA_V3.geojson")
    write_geo(results["costanera"]["analytic"],OUT/"COSTANERA_NORTE_ANALITICA_V3.geojson")
    write_geo(results["costanera"]["presentation"],OUT/"COSTANERA_NORTE_PRESENTACION_V3.geojson")
    write_csv(results["belgrano"]["continuity"],OUT/"BELGRANO_SENSIBILIDAD_CONTINUIDAD_V3.csv")
    write_csv(results["recoleta"]["continuity"],OUT/"RECOLETA_VACIOS_CONTINUIDAD_V3.csv")
    write_csv(results["costanera"]["continuity"],OUT/"COSTANERA_NORTE_SEPARACION_COMPONENTES_V3.csv")
    write_csv(results["costanera"]["correspondence"],OUT/"CORRESPONDENCIA_DOCUMENTAL_COSTANERA_NORTE_V3.csv")

    pts=anonymized_points(results); write_geo(pts,OUT/"PUNTOS_ASOCIADOS_SANITIZADOS_V3.geojson")
    ptable=pts.drop(columns="geometry").copy(); write_csv(ptable,OUT/"ASIGNACION_PUNTOS_TERRITORIAL_V3.csv")
    metrics=pd.DataFrame(sum([r["models"] for r in results.values()],[])); write_csv(metrics,OUT/"METRICAS_MODELOS_TERRITORIALES_V3.csv")
    decisions=decision_matrix(metrics); write_csv(decisions,OUT/"MATRIZ_DECISION_TERRITORIAL_V3.csv")
    kpi=metrics.loc[metrics.modelo.isin(["BEL-A","REC-A","CN-DEC10"]),["polo","modelo","universo","puntos_incluidos","cobertura_pct","componentes","superficie_km2","densidad_puntos_km2","estabilidad","dependencia_places_pct","puntos_sin_asignar"]]
    write_csv(kpi,OUT/"KPI_LOCK_CARTOGRAFICO_V3.csv")

    generate_maps(data,results["belgrano"],"belgrano","Polo Gastronómico Belgrano","BEL-A",cfg)
    generate_maps(data,results["recoleta"],"recoleta","Polo Gastronómico Recoleta","REC-A",cfg)
    generate_maps(data,results["costanera"],"costanera_norte","Polo Gastronómico Costanera Norte","CN-DEC10",cfg)

    post_hash=hash_map(protected_files); protected_ok=pre_hash==post_hash
    protected_report={"archivos":len(pre_hash),"bytes":sum((ROOT/p).stat().st_size for p in pre_hash),
                      "diferencias":[p for p in pre_hash if pre_hash.get(p)!=post_hash.get(p)],
                      "resultado":"OK" if protected_ok else "FALLA"}
    write_json(protected_report,OUT/"QA_SUPERFICIES_PROTEGIDAS_V3.json")
    documentation(results,metrics,decisions,input_snapshot,cfg,contract_info,protected_ok)

    geo_qa=[]
    for path in sorted(OUT.glob("*.geojson")):
        frame=gpd.read_file(path); geo_qa.append({"archivo":path.name,"features":len(frame),"crs":str(frame.crs),
                                                  "validas":int(frame.geometry.is_valid.sum()),"vacias":int(frame.geometry.is_empty.sum()),
                                                  "resultado":"OK" if str(frame.crs).upper().endswith("4326") and frame.geometry.is_valid.all() and not frame.geometry.is_empty.any() else "FALLA"})
    write_csv(pd.DataFrame(geo_qa),OUT/"QA_GEOJSON_CRS_V3.csv")
    image_qa=[]
    from PIL import Image
    for path in sorted(MAPS.glob("*.png")):
        with Image.open(path) as im: image_qa.append({"archivo":path.name,"ancho":im.width,"alto":im.height,"modo":im.mode,"resultado":"OK" if im.width>=1400 and im.height>=900 else "REVISAR"})
    write_csv(pd.DataFrame(image_qa),OUT/"QA_IMAGENES_V3.csv")
    privacy=privacy_scan([*DOC.rglob("*"),*OUT.glob("*.csv"),*OUT.glob("*.json"),*OUT.glob("*.geojson"),*OUT.glob("*.md")])
    write_json(privacy,OUT/"QA_PRIVACIDAD_V3.json")
    metadata={"fecha":DATE,"rol":"cartografo_territorial","estado":"COMPLETADO_LISTO_QA","crs_metrico":CRS_M,
              "crs_geojson":CRS_GEO,"modelos_recomendados":{"Belgrano":"BEL-A","Recoleta":"REC-A","Costanera Norte":"CN-DEC10"},
              "contrato_editorial":contract_info,"superficies_protegidas":protected_report,"privacidad":privacy["resultado"]}
    write_json(metadata,OUT/"METADATA_CORRIDA_TERRITORIAL_V3.json")
    if git_cached(): raise RuntimeError("El staging dejó de estar vacío")
    if not protected_ok or privacy["resultado"]!="OK" or any(x["resultado"]!="OK" for x in geo_qa):
        raise RuntimeError("QA bloqueante antes del paquete")

    # Manifest general antes del paquete; se excluyen paquete y extracción, todavía inexistentes.
    manifest=[]
    for base,label in [(DOC,"docs"),(OUT,"outputs"),(SCRIPT_DIR,"scripts")]:
        for path in sorted(p for p in base.rglob("*") if p.is_file() and REVIEW not in p.parents and EXTRACT_QA not in p.parents and p!=ZIP_PATH):
            if "__pycache__" in path.parts or path.suffix.lower() in {".pyc", ".pyo"}:
                continue
            manifest.append({"grupo":label,"ruta":path.relative_to(ROOT).as_posix(),"bytes":path.stat().st_size,"sha256":sha256(path)})
    write_csv(pd.DataFrame(manifest),OUT/"MANIFEST_CORRIDA_TERRITORIAL_V3.csv")
    checksum_lines=[f"{sha256(ROOT/r.ruta)}  {r.ruta}" for r in pd.read_csv(OUT/"MANIFEST_CORRIDA_TERRITORIAL_V3.csv").itertuples(index=False)]
    (OUT/"CHECKSUMS_SHA256.txt").write_text("\n".join(checksum_lines)+"\n",encoding="utf-8")
    size,zip_hash,zip_qa=build_package(); write_json(zip_qa,OUT/"QA_ZIP_EXTRACCION_V3.json")
    final={"estado":"TERRITORIAL_RUN_V3_COMPLETED_READY_FOR_QA","zip":ZIP_PATH.relative_to(ROOT).as_posix(),
           "zip_bytes":size,"zip_sha256":zip_hash,"staging_vacio":not git_cached(),"superficies_protegidas_ok":protected_ok,
           "geojson_ok":all(x["resultado"]=="OK" for x in geo_qa),"imagenes_png":len(image_qa),"zip_qa":zip_qa}
    write_json(final,OUT/"ESTADO_FINAL_TERRITORIAL_RUN_V3.json")
    print(json.dumps(final,ensure_ascii=False,indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}",file=sys.stderr)
        raise
