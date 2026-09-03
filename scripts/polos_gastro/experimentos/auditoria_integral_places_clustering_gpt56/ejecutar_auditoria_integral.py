# -*- coding: utf-8 -*-
"""Auditoria local, experimental y no destructiva de Places y clustering.

Lee exclusivamente insumos ya existentes del proyecto. No llama APIs, no modifica
datos fuente, Fase 25, Fase 26 ni las cartografias v1-v4.2. Todos los derivados se
escriben dentro de la carpeta experimental solicitada.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import warnings
from collections import Counter
from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from shapely.geometry import MultiPoint
from sklearn import __version__ as sklearn_version
from sklearn.cluster import HDBSCAN, OPTICS
from sklearn.metrics import adjusted_rand_score, silhouette_score

warnings.filterwarnings("ignore", category=FutureWarning)

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "outputs/polos_gastro/historico/experimentos/auditoria_integral_places_clustering_gpt56"
DOC = ROOT / "docs/polos_gastro/historico/experimentos/auditoria_integral_places_clustering_gpt56"
GRAF = OUT / "graficos"

PROTO = ROOT / "outputs/polos_gastro/historico/experimentos/pipeline_microzonas_v1"
AMP = ROOT / "outputs/polos_gastro/historico/experimentos/google_places_microzonas_ampliacion_v1"
COMP = AMP / "completa_v1"
V2 = AMP / "cartografia_editorial_v2"
V3 = AMP / "cartografia_decision_v3"
V4 = AMP / "cartografia_redibujo_editorial_v4"
V41 = AMP / "cartografia_redibujo_editorial_v4_1"
V42 = AMP / "cartografia_design_v4_2"

CRS_GEO = "EPSG:4326"
CRS_M = "EPSG:5347"
RNG = np.random.default_rng(5607)


def asegurar_carpetas() -> None:
    for p in (OUT, DOC, GRAF):
        p.mkdir(parents=True, exist_ok=True)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for bloque in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(bloque)
    return h.hexdigest()


def archivos_criticos() -> list[Path]:
    explicitos = [
        ROOT / "data/processed/fact_establecimiento.csv",
        ROOT / "data/processed/fact_habilitacion_gastronomica.csv",
        ROOT / "data/processed/dim_ubicacion.csv",
        PROTO / "universo/universo_entidades_v1.csv",
        PROTO / "clustering/labels_clusters.csv",
        PROTO / "poligonos/poligonos_alternativas.geojson",
        COMP / "UNIVERSO_COMPLETO_SANITIZADO.csv",
        COMP / "MICROCLUSTERS_COMPLETA_V1.geojson",
        COMP / "POLIGONOS_MICROZONAS_COMPLETA_V1.geojson",
        V2 / "tabla_agrupamiento_editorial_v0.csv",
        V2 / "poligonos_editoriales_simplificados_v0.geojson",
        V3 / "tabla_decision_cartografia_v3.csv",
        V3 / "zonas_todas_decision_v3.geojson",
        V4 / "tabla_redibujo_editorial_v4.csv",
        V4 / "poligonos_editoriales_redibujados_v4.geojson",
        V41 / "poligonos_v4_1_decision_dibujo.geojson",
        V42 / "metadata_cartografia_v4_2.json",
        ROOT / "scripts/polos_gastro/build_fase25_microajustes_finales_oficina.py",
        ROOT / "outputs/polos_gastro/fase25_microajustes_finales_oficina/INFORME_POLOS_GASTRO_DGDGAS_11P_OFICINA_FASE25.pdf",
        AMP / "fase26_comparativa_cartografia/paquete_fase26_revision/README.md",
    ]
    scripts = []
    for base in [
        ROOT / "scripts/polos_gastro/historico/experimentos/pipeline_microzonas_v1",
        ROOT / "scripts/polos_gastro/historico/experimentos/google_places_microzonas_piloto",
        ROOT / "scripts/polos_gastro/historico/experimentos/google_places_microzonas_ampliacion_v1",
    ]:
        if base.exists():
            scripts.extend(sorted(base.glob("*.py")))
    return sorted({p for p in explicitos + scripts if p.exists()})


def snapshot_hashes(finalizar: bool) -> dict:
    filas = [
        {
            "ruta": str(p.relative_to(ROOT)).replace("\\", "/"),
            "bytes": p.stat().st_size,
            "sha256": sha256(p),
        }
        for p in archivos_criticos()
    ]
    actual = pd.DataFrame(filas)
    antes_path = OUT / "hashes_insumos_criticos_antes.csv"
    if not antes_path.exists():
        actual.to_csv(antes_path, index=False, encoding="utf-8")
    if finalizar:
        actual.to_csv(OUT / "hashes_insumos_criticos_despues.csv", index=False, encoding="utf-8")
        antes = pd.read_csv(antes_path)
        comp = antes.merge(actual, on="ruta", how="outer", suffixes=("_antes", "_despues"), indicator=True)
        comp["sin_cambios"] = (
            comp["_merge"].eq("both")
            & comp["sha256_antes"].eq(comp["sha256_despues"])
            & comp["bytes_antes"].eq(comp["bytes_despues"])
        )
        comp.to_csv(OUT / "comparacion_hashes_insumos_criticos.csv", index=False, encoding="utf-8")
        return {"archivos": len(comp), "sin_cambios": int(comp["sin_cambios"].sum()), "cambiados": int((~comp["sin_cambios"]).sum())}
    return {"archivos": len(actual), "snapshot": "antes"}


def cluster_labels(xy: np.ndarray, mcs_factor: float = 1.0, min_samples: int = 5,
                   epsilon: float = 50.0, method: str = "eom") -> tuple[np.ndarray, np.ndarray]:
    if len(xy) < 8:
        return np.full(len(xy), -1, dtype=int), np.zeros(len(xy))
    mcs = max(8, int(round(0.03 * len(xy) * mcs_factor)))
    mcs = min(mcs, max(2, len(xy) - 1))
    model = HDBSCAN(
        min_cluster_size=mcs,
        min_samples=min(min_samples, mcs),
        cluster_selection_epsilon=float(epsilon),
        cluster_selection_method=method,
        copy=True,
    ).fit(xy)
    return model.labels_, getattr(model, "probabilities_", np.full(len(xy), np.nan))


def n_clusters(labels: np.ndarray) -> int:
    return len(set(labels) - {-1})


def cluster_survival(base: np.ndarray, alt: np.ndarray) -> float:
    ids = sorted(set(base) - {-1})
    if not ids:
        return float("nan")
    ok = 0
    for cid in ids:
        a = set(np.flatnonzero(base == cid))
        best = 0.0
        for did in set(alt) - {-1}:
            b = set(np.flatnonzero(alt == did))
            if a or b:
                best = max(best, len(a & b) / max(1, len(a | b)))
        ok += best >= 0.5
    return ok / len(ids)


def safe_silhouette(xy: np.ndarray, labels: np.ndarray) -> float:
    mask = labels >= 0
    labs = labels[mask]
    if mask.sum() < 20 or len(set(labs)) < 2:
        return float("nan")
    idx = np.flatnonzero(mask)
    if len(idx) > 1500:
        idx = RNG.choice(idx, 1500, replace=False)
    return float(silhouette_score(xy[idx], labels[idx]))


def cargar_datos():
    universo = pd.read_csv(COMP / "UNIVERSO_COMPLETO_SANITIZADO.csv", low_memory=False)
    puntos = gpd.read_file(COMP / "MICROCLUSTERS_COMPLETA_V1.geojson").to_crs(CRS_M)
    poligonos = gpd.read_file(COMP / "POLIGONOS_MICROZONAS_COMPLETA_V1.geojson").to_crs(CRS_M)
    entidades = pd.read_csv(PROTO / "universo/universo_entidades_v1.csv", low_memory=False)
    v2map = pd.read_csv(V2 / "tabla_agrupamiento_editorial_v0.csv")
    v3 = pd.read_csv(V3 / "tabla_decision_cartografia_v3.csv")
    v4 = pd.read_csv(V4 / "tabla_redibujo_editorial_v4.csv")
    return universo, puntos, poligonos, entidades, v2map, v3, v4


def auditar_trazabilidad(universo, puntos, poligonos, v2map, v3, v4) -> dict:
    ids_uni = set(universo["id_punto"].astype(str))
    ids_pts = set(puntos["id_punto"].astype(str))
    micro = set(poligonos["cluster_id"].astype(str))
    v2_micro = set(v2map["microzona_id_original"].astype(str))
    grupos = set(v2map["grupo_editorial_v0"].astype(str))
    grupos_retenidos = set(
        v2map.loc[v2map["mantener_en_mapa"].astype(str).ne("NO"), "grupo_editorial_v0"].astype(str)
    )
    grupos_excluidos = grupos - grupos_retenidos
    v3_grupos = set(v3["grupo_editorial_v0"].astype(str))
    v4_origen = []
    for valor in v4["ids_grupos_v3_origen"].fillna("").astype(str):
        v4_origen.extend([x.strip() for x in valor.split(";") if x.strip()])
    v4_origen = set(v4_origen)
    asign = puntos[puntos["cluster_final"].astype(str).ne("ruido")]
    resumen = {
        "universo_csv": len(universo),
        "puntos_geojson": len(puntos),
        "ids_csv_igual_geojson": ids_uni == ids_pts,
        "ids_duplicados_csv": int(universo["id_punto"].duplicated().sum()),
        "puntos_asignados_cluster": int(len(asign)),
        "puntos_ruido": int((puntos["cluster_final"].astype(str) == "ruido").sum()),
        "puntos_asignados_mas_de_una_vez": int(asign["id_punto"].duplicated().sum()),
        "poligonos_163": len(poligonos),
        "microzonas_mapeadas_v2": len(v2_micro),
        "microzonas_faltantes_v2": sorted(micro - v2_micro),
        "microzonas_extra_v2": sorted(v2_micro - micro),
        "grupos_v2_totales_incluye_exclusiones": len(grupos),
        "grupos_v2_retenidos": len(grupos_retenidos),
        "grupos_v2_excluidos": len(grupos_excluidos),
        "grupos_v3": len(v3_grupos),
        "grupos_retenidos_faltantes_v3": sorted(grupos_retenidos - v3_grupos),
        "grupos_excluidos_que_no_pasan_v3": sorted(grupos_excluidos),
        "grupos_extra_v3": sorted(v3_grupos - grupos),
        "unidades_v4": len(v4),
        "grupos_origen_v4": len(v4_origen),
        "grupos_faltantes_v4": sorted(v3_grupos - v4_origen),
        "grupos_extra_v4": sorted(v4_origen - v3_grupos),
    }
    (OUT / "qa_trazabilidad_163_41_31.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")
    trace = v2map[["macrozona", "microzona_id_original", "grupo_editorial_v0"]].merge(
        v3[["grupo_editorial_v0", "familia_v3", "decision_visual"]], on="grupo_editorial_v0", how="left"
    )
    v4rows = []
    for _, r in v4.iterrows():
        for g in str(r["ids_grupos_v3_origen"]).split(";"):
            v4rows.append({"grupo_editorial_v0": g.strip(), "id_v4": r["id_v4"], "familia_v4": r["familia_v4"]})
    trace = trace.merge(pd.DataFrame(v4rows), on="grupo_editorial_v0", how="left")
    trace.to_csv(OUT / "trazabilidad_163_41_31.csv", index=False, encoding="utf-8")
    return resumen


def auditar_deduplicacion(universo, entidades) -> dict:
    g = gpd.GeoDataFrame(universo.copy(), geometry=gpd.points_from_xy(universo.lon, universo.lat), crs=CRS_GEO).to_crs(CRS_M)
    xy = np.column_stack([g.geometry.x, g.geometry.y])
    tree = cKDTree(xy)
    pairs40 = sorted(tree.query_pairs(40.0))
    filas = []
    exactas = 0
    cross = Counter()
    risk = Counter()
    for k, (i, j) in enumerate(pairs40, start=1):
        a, b = universo.iloc[i], universo.iloc[j]
        d = float(np.linalg.norm(xy[i] - xy[j]))
        same_source = a["fuente"] == b["fuente"]
        na = set(str(a.get("nombre_normalizado", "")).split())
        nb = set(str(b.get("nombre_normalizado", "")).split())
        compat = bool(na and nb and (" ".join(na) in " ".join(nb) or " ".join(nb) in " ".join(na) or len(na & nb) / max(1, min(len(na), len(nb))) >= 0.5))
        if d < 0.05:
            exactas += 1
        clave = "misma_fuente" if same_source else "cruzada"
        cross[(clave, "0_5" if d <= 5 else "5_15" if d <= 15 else "15_40")] += 1
        if same_source and compat:
            tipo = "FALSO_NEGATIVO_PROBABLE"
        elif not same_source and d <= 15 and not compat:
            tipo = "COLOCALIZACION_A_REVISAR"
        elif not same_source and compat:
            tipo = "FALSO_NEGATIVO_PROBABLE"
        else:
            tipo = "PROXIMIDAD_NO_CONCLUYENTE"
        risk[tipo] += 1
        filas.append({
            "caso_anonimo": f"DEDUP_{k:04d}",
            "par_fuentes": f"{a['fuente']}|{b['fuente']}",
            "distancia_m_redondeada": round(d, 1),
            "banda_distancia": "0-5" if d <= 5 else "5-15" if d <= 15 else "15-40",
            "nombres_compatibles": compat,
            "coordenada_exacta_repetida": d < 0.05,
            "clasificacion_revision": tipo,
            "incluidos_ambos_universo_final": True,
        })
    muestra = pd.DataFrame(filas)
    if len(muestra):
        orden = {"FALSO_NEGATIVO_PROBABLE": 0, "COLOCALIZACION_A_REVISAR": 1, "PROXIMIDAD_NO_CONCLUYENTE": 2}
        muestra["_orden"] = muestra["clasificacion_revision"].map(orden)
        muestra = muestra.sort_values(["_orden", "distancia_m_redondeada"]).drop(columns="_orden").head(80)
    muestra.to_csv(OUT / "muestra_casos_deduplicacion_revision.csv", index=False, encoding="utf-8")

    # Sensibilidad Places vs base, sin persistir nombres, IDs ni coordenadas.
    base = g[g["fuente"].eq("F01+F02")]
    places = g[g["fuente"].eq("google_places")]
    bt = cKDTree(np.column_stack([base.geometry.x, base.geometry.y]))
    dist, _ = bt.query(np.column_stack([places.geometry.x, places.geometry.y]), k=1)
    sensibilidad = []
    for t in (10, 15, 20, 30, 40, 50):
        sensibilidad.append({"umbral_m": t, "places_con_base_cercana": int((dist <= t).sum()), "porcentaje_places": round(100 * float((dist <= t).mean()), 2)})
    pd.DataFrame(sensibilidad).to_csv(OUT / "sensibilidad_umbral_deduplicacion.csv", index=False, encoding="utf-8")
    resumen = {
        "filas_universo": len(universo),
        "ids_unicos": int(universo.id_punto.nunique()),
        "filas_coordenada_exacta_repetida": int(universo.duplicated(["lat", "lon"], keep=False).sum()),
        "pares_hasta_40m": len(pairs40),
        "pares_coordenada_exacta": exactas,
        "pares_por_fuente_y_banda": {"|".join(k): v for k, v in cross.items()},
        "clasificacion_revision": dict(risk),
        "limitacion": "La proximidad y el nombre normalizado no prueban identidad; la muestra es una cola de revision anonimizada.",
    }
    (OUT / "qa_deduplicacion.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")
    return resumen


def auditar_clustering(universo, puntos, poligonos, entidades):
    ent_flags = entidades[["id_entidad", "en_f01", "en_f02"]].copy()
    ent_flags["id_entidad"] = ent_flags["id_entidad"].astype(str)
    universo2 = universo.merge(ent_flags, left_on="id_punto", right_on="id_entidad", how="left")
    filas_rob, filas_places, sensibilidad_det = [], [], []
    configs = [
        ("base", 1.0, 5, 50.0, "eom"),
        ("mcs_80", 0.8, 5, 50.0, "eom"),
        ("mcs_120", 1.2, 5, 50.0, "eom"),
        ("ms_3", 1.0, 3, 50.0, "eom"),
        ("ms_8", 1.0, 8, 50.0, "eom"),
        ("eps_0", 1.0, 5, 0.0, "eom"),
        ("eps_100", 1.0, 5, 100.0, "eom"),
        ("leaf", 1.0, 5, 50.0, "leaf"),
    ]
    for mz, idx in universo2.groupby("macrozona_id").groups.items():
        idx = np.array(list(idx), dtype=int)
        sub = universo2.loc[idx].reset_index(drop=True)
        gs = gpd.GeoDataFrame(sub, geometry=gpd.points_from_xy(sub.lon, sub.lat), crs=CRS_GEO).to_crs(CRS_M)
        xy = np.column_stack([gs.geometry.x, gs.geometry.y])
        base_labels, probs = cluster_labels(xy)
        base_mask = sub["fuente"].eq("F01+F02").to_numpy()
        places_mask = sub["fuente"].eq("google_places").to_numpy()
        base_only, _ = cluster_labels(xy[base_mask])
        f01_mask = base_mask & sub["en_f01"].fillna(False).astype(bool).to_numpy()
        f02_mask = base_mask & sub["en_f02"].fillna(False).astype(bool).to_numpy()
        f01_lab, _ = cluster_labels(xy[f01_mask]) if f01_mask.sum() >= 8 else (np.full(f01_mask.sum(), -1), np.array([]))
        f02_lab, _ = cluster_labels(xy[f02_mask]) if f02_mask.sum() >= 8 else (np.full(f02_mask.sum(), -1), np.array([]))

        stab = []
        for nombre, fac, ms, eps, method in configs:
            labs, _ = cluster_labels(xy, fac, ms, eps, method)
            ari = adjusted_rand_score(base_labels, labs)
            surv = cluster_survival(base_labels, labs)
            stab.append((nombre, ari, surv, n_clusters(labs), float((labs == -1).mean())))
            sensibilidad_det.append({
                "macrozona": mz, "configuracion": nombre, "ari_vs_base": round(ari, 4),
                "supervivencia_clusters_jaccard_05": round(surv, 4) if not math.isnan(surv) else np.nan,
                "clusters": n_clusters(labs), "pct_ruido": round(100 * float((labs == -1).mean()), 2),
            })

        boot_ari = []
        for rep in range(5):
            keep = np.sort(RNG.choice(len(xy), max(8, int(0.9 * len(xy))), replace=False))
            labs_b, _ = cluster_labels(xy[keep])
            boot_ari.append(adjusted_rand_score(base_labels[keep], labs_b))
        stab_dict = {x[0]: x for x in stab}
        local_names = ["mcs_80", "mcs_120", "ms_3", "ms_8", "eps_0"]
        ari_local = [stab_dict[n][1] for n in local_names]
        ari_local_med = float(np.median(ari_local))
        boot_med = float(np.mean(boot_ari))
        estabilidad_clase = (
            "ALTA" if ari_local_med >= 0.85 and boot_med >= 0.80
            else "MEDIA" if ari_local_med >= 0.60 and boot_med >= 0.50
            else "BAJA"
        )

        current = puntos[puntos["macrozona_id"].eq(mz)]
        comps = current[current["cluster_final"].astype(str).ne("ruido")].groupby("cluster_final")["fuente"].agg(lambda s: set(s.astype(str)))
        sin_places = int(sum("google_places" not in s for s in comps))
        con_places = int(sum("google_places" in s for s in comps))
        pct_places = 100 * float(places_mask.mean())
        change_clusters = n_clusters(base_labels) - n_clusters(base_only)
        noise_delta = 100 * (float((base_labels == -1).mean()) - float((base_only == -1).mean()))
        lectura = "CAMBIO_ESTRUCTURAL" if abs(change_clusters) >= 2 or abs(noise_delta) >= 10 else "CAMBIO_MODERADO" if abs(change_clusters) == 1 or abs(noise_delta) >= 5 else "AGREGA_VOLUMEN"
        dep = "ALTA" if pct_places >= 60 else "MEDIA" if pct_places >= 40 else "BAJA"

        filas_places.append({
            "macrozona": mz,
            "puntos_f01_f02": int(base_mask.sum()),
            "puntos_places_nuevos": int(places_mask.sum()),
            "incremento_porcentual": round(100 * places_mask.sum() / max(1, base_mask.sum()), 2),
            "porcentaje_places_final": round(pct_places, 2),
            "clusters_sin_places": sin_places,
            "clusters_con_places": con_places,
            "cambio_ruido": round(noise_delta, 2),
            "cambio_numero_clusters": int(change_clusters),
            "cambio_lectura_territorial": lectura,
            "dependencia_places": dep,
            "confianza": "MEDIA" if dep == "BAJA" and lectura != "CAMBIO_ESTRUCTURAL" else "BAJA" if dep == "ALTA" else "MEDIA_BAJA",
            "observaciones": "Comparacion HDBSCAN crudo con parametros vigentes; antes de subdivision KMeans.",
        })
        filas_rob.append({
            "macrozona": mz,
            "n_puntos": len(sub),
            "pct_places": round(pct_places, 2),
            "clusters_hdbscan_base": n_clusters(base_labels),
            "pct_ruido_hdbscan": round(100 * float((base_labels == -1).mean()), 2),
            "probabilidad_media_hdbscan": round(float(np.nanmean(probs)), 4),
            "silhouette_sin_ruido": round(safe_silhouette(xy, base_labels), 4),
            "ari_min_perturbaciones": round(min(x[1] for x in stab), 4),
            "ari_mediana_perturbaciones": round(float(np.median([x[1] for x in stab])), 4),
            "ari_mediana_perturbaciones_locales": round(ari_local_med, 4),
            "ari_leaf_vs_eom": round(stab_dict["leaf"][1], 4),
            "ari_epsilon_100_vs_50": round(stab_dict["eps_100"][1], 4),
            "supervivencia_min_clusters": round(min(x[2] for x in stab if not math.isnan(x[2])), 4) if n_clusters(base_labels) else np.nan,
            "ari_bootstrap_90_media": round(boot_med, 4),
            "estabilidad_sintetica": estabilidad_clase,
            "clusters_solo_f01f02": n_clusters(base_only),
            "pct_ruido_solo_f01f02": round(100 * float((base_only == -1).mean()), 2),
            "clusters_solo_f01": n_clusters(f01_lab),
            "pct_ruido_solo_f01": round(100 * float((f01_lab == -1).mean()), 2) if len(f01_lab) else np.nan,
            "clusters_solo_f02": n_clusters(f02_lab),
            "pct_ruido_solo_f02": round(100 * float((f02_lab == -1).mean()), 2) if len(f02_lab) else np.nan,
            "nota_silhouette": "Solo puntos no ruido; penaliza formas no convexas y no se usa como criterio principal.",
        })

    robust = pd.DataFrame(filas_rob).sort_values("macrozona")
    places = pd.DataFrame(filas_places).sort_values("macrozona")
    robust.to_csv(OUT / "metricas_robustez_por_zona.csv", index=False, encoding="utf-8")
    places.to_csv(OUT / "diagnostico_places_por_zona.csv", index=False, encoding="utf-8")
    pd.DataFrame(sensibilidad_det).to_csv(OUT / "sensibilidad_hdbscan_detalle.csv", index=False, encoding="utf-8")

    pol = poligonos.copy()
    pol["perimetro_m"] = pol.geometry.length
    pol["compacidad_polsby_popper"] = 4 * math.pi * pol.geometry.area / pol.geometry.length.pow(2)
    kdiag = (pol.groupby(["macrozona_id", "ronda"], dropna=False)
             .agg(poligonos=("cluster_id", "size"), puntos=("n_puntos", "sum"), area_ha=("area_ha", "sum"), compacidad_media=("compacidad_polsby_popper", "mean"))
             .reset_index())
    kdiag.to_csv(OUT / "diagnostico_subdivision_kmeans.csv", index=False, encoding="utf-8")

    # OPTICS: prueba controlada en cinco zonas tipologicamente distintas.
    optics_rows = []
    for mz in ["MZ_SAN_TELMO", "MZ_AVENIDA_CORRIENTES", "MZ_PALERMO_SOHO", "MZ_BELGRANO", "MZ_COSTANERA_NORTE"]:
        sub = universo2[universo2["macrozona_id"].eq(mz)]
        gs = gpd.GeoDataFrame(sub, geometry=gpd.points_from_xy(sub.lon, sub.lat), crs=CRS_GEO).to_crs(CRS_M)
        xy = np.column_stack([gs.geometry.x, gs.geometry.y])
        if len(xy) < 10:
            continue
        mcs = max(8, int(round(0.03 * len(xy))))
        for xi in (0.03, 0.05, 0.1):
            labs = OPTICS(min_samples=5, min_cluster_size=mcs, xi=xi, cluster_method="xi").fit_predict(xy)
            optics_rows.append({"macrozona": mz, "xi": xi, "clusters": n_clusters(labs), "pct_ruido": round(100 * float((labs == -1).mean()), 2)})
    pd.DataFrame(optics_rows).to_csv(OUT / "prueba_controlada_optics.csv", index=False, encoding="utf-8")

    # Graficos agregados, sin puntos ni identificadores individuales.
    fig, ax = plt.subplots(figsize=(10, 6))
    pplot = places.sort_values("porcentaje_places_final")
    ax.barh(pplot["macrozona"].str.replace("MZ_", "", regex=False), pplot["puntos_f01_f02"], label="F01+F02", color="#1f5d7a")
    ax.barh(pplot["macrozona"].str.replace("MZ_", "", regex=False), pplot["puntos_places_nuevos"], left=pplot["puntos_f01_f02"], label="Places nuevos", color="#c47a1d")
    ax.set_title("Composicion del universo por macrozona")
    ax.set_xlabel("Puntos de oferta registrada/visible")
    ax.legend()
    fig.tight_layout(); fig.savefig(GRAF / "composicion_fuentes_por_macrozona.png", dpi=180); plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 6))
    rplot = robust.sort_values("ari_min_perturbaciones")
    ax.barh(rplot["macrozona"].str.replace("MZ_", "", regex=False), rplot["ari_min_perturbaciones"], color="#3d7f68")
    ax.axvline(0.8, color="#b5543a", linestyle="--", linewidth=1)
    ax.set_xlim(0, 1); ax.set_xlabel("ARI minimo frente a perturbaciones"); ax.set_title("Estabilidad minima de HDBSCAN por macrozona")
    fig.tight_layout(); fig.savefig(GRAF / "estabilidad_hdbscan_por_macrozona.png", dpi=180); plt.close(fig)
    return robust, places, kdiag


def tablas_metodologicas(robust, places, kdiag):
    metodos = [
        ["HDBSCAN sin KMeans", "densidades variables sin tiles", "nucleos y redes", "Conserva formas densidad-variable", "Puede dejar manchas grandes", "puntos existentes", "MEDIO", "ALTA", "ALTA", "PROBAR", "ALTA"],
        ["HDBSCAN leaf/eom comparado", "seleccion jerarquica", "zonas multinucleares", "Expone subestructura", "Leaf puede sobrefragmentar", "puntos existentes", "BAJO", "ALTA", "MEDIA", "PROBAR", "ALTA"],
        ["KDE y contornos", "superficie continua", "nucleos difusos", "Buena lectura de intensidad", "Bandwidth y umbral sensibles", "puntos existentes", "MEDIO", "ALTA", "ALTA", "PROBAR", "ALTA"],
        ["Grafo de proximidad", "continuidad local", "corredores y redes", "Permite comunidades y puentes", "Umbral de arista sensible", "puntos existentes", "MEDIO", "ALTA", "MEDIA", "PROBAR", "ALTA"],
        ["Corredor sobre eje", "forma lineal", "Corrientes Caseros Cabildo Puerto Madero", "Representacion territorial honesta", "Requiere eje vial o trazado humano", "callejero local", "MEDIO", "ALTA", "ALTA", "PROBAR", "ALTA"],
        ["Concave hull", "nucleo compacto", "Soho San Telmo", "Contorno reproducible", "Puas y puentes con pocos puntos", "puntos existentes", "BAJO", "ALTA", "ALTA", "MANTENER_RESTRINGIDO", "MEDIA"],
        ["Alpha shapes", "contorno concavo alternativo", "nucleos compactos", "Control fino", "Parametro poco interpretable y dependencia nueva", "puntos existentes", "MEDIO", "MEDIA", "MEDIA", "NO_PRIORIZAR", "BAJA"],
        ["OPTICS", "densidades variables", "diagnostico puntual", "Reachability util", "Extraccion xi tambien sensible", "puntos existentes", "BAJO", "ALTA", "MEDIA", "DIAGNOSTICO", "MEDIA"],
        ["Clustering por red vial", "distancia urbana real", "corredores con barreras", "Respeta conectividad urbana", "Complejidad y capa vial limpia", "red vial enrutable", "ALTO", "MEDIA", "MEDIA", "FUTURO", "BAJA"],
        ["Heatmap sin poligono", "senal exploratoria", "Costanera y zonas debiles", "No finge limites", "No asigna unidades discretas", "puntos existentes", "BAJO", "ALTA", "ALTA", "USAR_EN_ANEXO", "ALTA"],
        ["KMeans territorial", "partir manchas grandes", "ninguna como metodo principal", "Simple y determinista", "Impone Voronoi convexos y tiles artificiales", "puntos existentes", "BAJO", "ALTA", "BAJA", "RESTRINGIR_O_ELIMINAR", "ALTA"],
        ["Voronoi", "particion exhaustiva", "ninguna", "Cubre todo sin huecos", "Crea fronteras sin fundamento", "puntos existentes", "BAJO", "ALTA", "BAJA", "DESCARTAR", "BAJA"],
        ["ST-DBSCAN", "cambio temporal", "ninguna con datos actuales", "Agrega dinamica", "No hay historia de actividad comparable", "serie temporal limpia", "ALTO", "BAJA", "BAJA", "NO_AHORA", "BAJA"],
    ]
    cols = ["metodo", "problema_objetivo", "zonas_aplicables", "ventaja", "desventaja", "datos_necesarios", "costo_implementacion", "reproducibilidad", "interpretabilidad_institucional", "recomendacion", "prioridad_prueba"]
    pd.DataFrame(metodos, columns=cols).to_csv(OUT / "MATRIZ_COMPARATIVA_METODOS.csv", index=False, encoding="utf-8")

    mappings = {
        "Palermo Soho": ("MZ_PALERMO_SOHO", "NUCLEO_COMPACTO", "POLIGONO"),
        "Palermo Hollywood": ("MZ_PALERMO_HOLLYWOOD", "RED_MULTINUCLEAR", "NUCLEOS_SEPARADOS"),
        "San Telmo": ("MZ_SAN_TELMO", "NUCLEO_COMPACTO", "POLIGONO"),
        "Corrientes": ("MZ_AVENIDA_CORRIENTES", "CORREDOR_LINEAL", "EJE_CON_BUFFER"),
        "Microcentro": ("MZ_MICROCENTRO_Y_CENTRO", "RED_MULTINUCLEAR", "NUCLEOS_SEPARADOS"),
        "Belgrano": ("MZ_BELGRANO", "RED_MULTINUCLEAR", "NUCLEOS_SEPARADOS"),
        "Caballito": ("MZ_CABALLITO", "RED_MULTINUCLEAR", "NUCLEOS_SEPARADOS"),
        "Recoleta": ("MZ_RECOLETA", "ZONA_EXTENSA_DIFUSA", "HEATMAP"),
        "Villa Crespo": ("MZ_VILLA_CRESPO", "RED_MULTINUCLEAR", "NUCLEOS_SEPARADOS"),
        "Chacarita": ("MZ_CHACARITA", "RED_MULTINUCLEAR", "NUCLEOS_SEPARADOS"),
        "Puerto Madero": ("MZ_PUERTO_MADERO", "FRENTE_GASTRONOMICO", "EJE_CON_BUFFER"),
        "Costanera Norte": ("MZ_COSTANERA_NORTE", "FRENTE_GASTRONOMICO", "PUNTOS"),
        "Caseros/Barracas": ("MZ_AVENIDA_CASEROS_BARRACAS", "CORREDOR_LINEAL", "CORREDOR"),
    }
    rr = robust.set_index("macrozona")
    pp = places.set_index("macrozona")
    rows = []
    for zona, (mz, tipo, rep) in mappings.items():
        r = rr.loc[mz]; p = pp.loc[mz]
        estable = r.estabilidad_sintetica
        apta = "SI_CON_NOTA" if estable != "BAJA" and p.dependencia_places != "ALTA" else "NO_MOSTRAR_AUN" if p.dependencia_places == "ALTA" else "SOLO_ANEXO"
        problema = "KMeans/poligono no representa la forma territorial" if tipo in ("CORREDOR_LINEAL", "FRENTE_GASTRONOMICO") else "Fragmentacion y limites editoriales manuales" if tipo == "RED_MULTINUCLEAR" else "Dependencia de umbral y contorno"
        rows.append({
            "zona": zona, "calidad_universo": "MEDIA", "dependencia_places": p.dependencia_places,
            "calidad_cluster": "MEDIA_ALTA" if estable == "ALTA" else "MEDIA" if estable == "MEDIA" else "BAJA",
            "estabilidad": estable, "tipo_territorial": tipo, "representacion_recomendada": rep,
            "problema_actual": problema, "decision_humana_requerida": "Validar nombre, jerarquia, inclusion y limite aproximado",
            "alternativa_recomendada": "HDBSCAN+KDE" if tipo == "NUCLEO_COMPACTO" else "Grafo/eje+buffer" if tipo in ("CORREDOR_LINEAL", "FRENTE_GASTRONOMICO") else "HDBSCAN sin KMeans+comunidades",
            "prioridad": "ALTA" if zona in ("Corrientes", "Microcentro", "Belgrano", "Caballito", "Puerto Madero") else "MEDIA",
            "apta_para_informe": apta, "observaciones": f"ARI minimo={r.ari_min_perturbaciones:.2f}; Places={p.porcentaje_places_final:.1f}%.",
        })
    pd.DataFrame(rows).to_csv(OUT / "DIAGNOSTICO_METODOLOGICO_POR_ZONA.csv", index=False, encoding="utf-8")

    fase25 = {
        "Palermo Soho": "Subzona aproximada dentro de Palermo/Las Canitas",
        "Palermo Hollywood": "Subzona aproximada dentro de Palermo/Las Canitas",
        "San Telmo": "Casco historico, Defensa y Mercado como lectura prudente",
        "Corrientes": "Eje aproximado 9 de Julio-Callao, separado de Abasto",
        "Microcentro": "Macrozona del mapa general sin detalle cuantitativo",
        "Belgrano": "Macroarea con Barrio Chino, Bajo Belgrano y Belgrano R",
        "Caballito": "Area/barrio de lectura en mapa general",
        "Recoleta": "Area/barrio de lectura en mapa general",
        "Villa Crespo": "Area/barrio de lectura en mapa general",
        "Chacarita": "Area/barrio de lectura en mapa general",
        "Puerto Madero": "Banda de docks y frente costero",
        "Costanera Norte": "Eje/corredor aproximado",
        "Caseros/Barracas": "Eje/corredor aproximado",
    }
    diag = pd.read_csv(OUT / "DIAGNOSTICO_METODOLOGICO_POR_ZONA.csv")
    comp = []
    for _, r in diag.iterrows():
        mejor = r["estabilidad"] != "BAJA" and r["dependencia_places"] != "ALTA"
        comp.append({
            "zona": r["zona"], "que_mostraba_fase25": fase25[r["zona"]],
            "que_muestra_pipeline_nuevo": f"{r['tipo_territorial']} con recomendacion {r['representacion_recomendada']}",
            "evidencia_nueva": r["observaciones"], "cambio_interpretacion": "SI" if r["zona"] in ("Microcentro", "Caballito", "Chacarita", "Villa Crespo") else "PARCIAL",
            "nuevo_poligono_es_mejor": "NO_COMO_LIMITE" if r["tipo_territorial"] in ("CORREDOR_LINEAL", "FRENTE_GASTRONOMICO") else "SOLO_COMO_EVIDENCIA" if not mejor else "PARCIALMENTE",
            "fase25_mas_prudente": "SI" if r["apta_para_informe"] != "SI_CON_NOTA" else "NO",
            "recomendacion_informe": "Conservar prudencia de Fase25 y actualizar evidencia" if r["apta_para_informe"] != "SI_CON_NOTA" else "Usar evidencia nueva con limite orientativo",
            "mejora_datos": "SI", "mejora_metodologica": "PARCIAL", "mejora_cartografica": "SI_EN_LEGIBILIDAD", "mejora_narrativa": "NO_EVALUADA", "problema_nuevo": r["problema_actual"],
        })
    pd.DataFrame(comp).to_csv(OUT / "comparacion_por_zona_fase25_nuevo.csv", index=False, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--finalize", action="store_true", help="Compara hashes finales contra snapshot inicial")
    args = parser.parse_args()
    asegurar_carpetas()
    hashes = snapshot_hashes(args.finalize)
    universo, puntos, poligonos, entidades, v2map, v3, v4 = cargar_datos()
    traz = auditar_trazabilidad(universo, puntos, poligonos, v2map, v3, v4)
    dedup = auditar_deduplicacion(universo, entidades)
    robust, places, kdiag = auditar_clustering(universo, puntos, poligonos, entidades)
    tablas_metodologicas(robust, places, kdiag)
    run = {
        "estado": "EXPERIMENTAL_NO_OFICIAL",
        "sin_api": True,
        "sin_google_places": True,
        "sklearn_version": sklearn_version,
        "hashes": hashes,
        "trazabilidad": traz,
        "deduplicacion": dedup,
        "archivos_generados": sorted(str(p.relative_to(ROOT)).replace("\\", "/") for p in OUT.rglob("*") if p.is_file()),
    }
    (OUT / "auditoria_run.json").write_text(json.dumps(run, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"ok": True, "out": str(OUT), "hashes": hashes, "trazabilidad": traz}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
