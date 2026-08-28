# -*- coding: utf-8 -*-
"""Piloto Google Places + microzonas — Etapa 3: HDBSCAN + KDE + polígonos chicos.

EXPERIMENTO CONTROLADO. No toca Fase 25 ni el pipeline F01-F05.

Por cada macrozona piloto:
- HDBSCAN con los parámetros ya justificados en pipeline_microzonas_v1/config.py
  (min_cluster_size = max(8, 3%), min_samples = 5, epsilon 50 m, eom).
- KDE (bw 100 m, grilla 20 m, umbral relativo 40%) como CONTRASTE de densidad:
  se reporta qué fracción de cada polígono cae en núcleo KDE.
- Polígonos por cluster: concave_hull(ratio 0.4) + buffer 35 m (frente edificado);
  fallback buffer-unión (70/-35) si el hull degenera. Recortados a la macrozona.
- CONTROL DE TAMAÑO (objetivo del piloto: núcleos CHICOS, no macrozonas enteras):
  * área > AREA_MAX_HA o diámetro > DIAM_MAX_M (no corredor) => se SUBDIVIDE con KMeans
    (k = ceil(área / AREA_OBJETIVO_HA)), hasta 2 rondas.
  * gates de descarte del doc 01 s6: < 5 puntos o densidad < 1 local/ha.

Outputs: MICROCLUSTERS_PILOTO.geojson, POLIGONOS_MICROZONAS_PILOTO.geojson,
qa_clusters_piloto.json.

Uso:
    .venv/Scripts/python.exe scripts/polos_gastro/experimentos/google_places_microzonas_piloto/detectar_microzonas_piloto.py
"""
from __future__ import annotations

import json
import math
from itertools import combinations
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely import concave_hull
from shapely.geometry import MultiPoint
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[4]
SALIDA = ROOT / "outputs" / "polos_gastro" / "experimentos" / "google_places_microzonas_piloto"
UNIVERSO = SALIDA / "UNIVERSO_PILOTO_SANITIZADO.csv"
MACROZONAS = (ROOT / "outputs" / "polos_gastro" / "experimentos"
              / "infraestructura_cartografica_v1" / "macrozonas_editoriales_candidatas_v1.geojson")
OUT_PUNTOS = SALIDA / "MICROCLUSTERS_PILOTO.geojson"
OUT_POLIGONOS = SALIDA / "POLIGONOS_MICROZONAS_PILOTO.geojson"
OUT_QA = SALIDA / "qa_clusters_piloto.json"

CRS_GEO = "EPSG:4326"
CRS_METRICO = "EPSG:5347"

# --- Parámetros de clustering (mismos valores/justificación que pipeline_microzonas_v1) ---
HDB_MIN_SAMPLES = 5
HDB_EPS_M = 50.0
HDB_METODO = "eom"
MIN_PUNTOS_MACROZONA = 30
DBSCAN_FALLBACK = {"eps": 150.0, "min_samples": 4}
KDE_BW_M = 100.0
KDE_GRILLA_M = 20.0
KDE_UMBRAL_REL = 0.4
# --- Polígonos ---
CONCAVE_RATIO = 0.4
BUFFER_FRENTE_M = 35.0
BUFFER_UNION_M = 70.0
# --- Control de tamaño (piloto: microzonas chicas; flag 20 ha del doc 01 s6 como techo) ---
AREA_MAX_HA = 18.0       # dispara subdivisión
AREA_OBJETIVO_HA = 10.0  # tamaño objetivo de cada pieza al subdividir
DIAM_MAX_M = 1000.0      # diámetro máximo no-corredor
CORREDOR_ELONG_MIN = 3.0
CORREDOR_LARGO_MIN_M = 600.0
MIN_LOCALES = 5
DENSIDAD_MIN_HA = 1.0
MAX_RONDAS_SUBDIVISION = 2


def hdbscan_labels(xy: np.ndarray) -> tuple[np.ndarray, float]:
    """Devuelve (labels, epsilon_usado). sklearn 1.9 tiene un bug dependiente de los
    datos en epsilon_search (TypeError); si salta, se reintenta con epsilon=0 y queda
    registrado en el QA (puede fragmentar núcleos separados por una calle)."""
    from sklearn.cluster import HDBSCAN
    mcs = max(8, int(round(0.03 * len(xy))))
    for eps in (HDB_EPS_M, 0.0):
        try:
            modelo = HDBSCAN(min_cluster_size=mcs, min_samples=HDB_MIN_SAMPLES,
                             cluster_selection_epsilon=eps,
                             cluster_selection_method=HDB_METODO)
            return modelo.fit_predict(xy), eps
        except TypeError:
            continue
    raise RuntimeError("HDBSCAN falló incluso con epsilon=0")


def dbscan_labels(xy: np.ndarray) -> np.ndarray:
    from sklearn.cluster import DBSCAN
    return DBSCAN(eps=DBSCAN_FALLBACK["eps"],
                  min_samples=DBSCAN_FALLBACK["min_samples"]).fit_predict(xy)


def nucleo_kde(xy: np.ndarray, geom_mz) -> gpd.GeoSeries | None:
    """Celdas de grilla con densidad KDE >= 40% del máximo de la macrozona."""
    from shapely.geometry import box
    from sklearn.neighbors import KernelDensity
    if len(xy) < MIN_LOCALES:
        return None
    kde = KernelDensity(bandwidth=KDE_BW_M, kernel="gaussian").fit(xy)
    minx, miny, maxx, maxy = geom_mz.bounds
    gx = np.arange(minx, maxx + KDE_GRILLA_M, KDE_GRILLA_M)
    gy = np.arange(miny, maxy + KDE_GRILLA_M, KDE_GRILLA_M)
    xx, yy = np.meshgrid(gx, gy)
    pts = np.column_stack([xx.ravel(), yy.ravel()])
    dens = np.exp(kde.score_samples(pts))
    umbral = KDE_UMBRAL_REL * dens.max()
    celdas = [box(x - KDE_GRILLA_M / 2, y - KDE_GRILLA_M / 2,
                  x + KDE_GRILLA_M / 2, y + KDE_GRILLA_M / 2)
              for (x, y), d in zip(pts, dens) if d >= umbral]
    if not celdas:
        return None
    nucleo = unary_union(celdas).intersection(geom_mz)
    return nucleo if not nucleo.is_empty else None


def poligonizar(xy: np.ndarray, geom_mz):
    """(polígono, método). concave_hull + buffer; fallback buffer-unión."""
    mp = MultiPoint([tuple(p) for p in xy])
    metodo = f"concave_hull_r{CONCAVE_RATIO}_buffer{int(BUFFER_FRENTE_M)}"
    try:
        hull = concave_hull(mp, ratio=CONCAVE_RATIO, allow_holes=False)
        poli = hull.buffer(BUFFER_FRENTE_M)
    except Exception:
        poli = None
    if poli is None or poli.is_empty or poli.geom_type not in ("Polygon", "MultiPolygon"):
        poli = unary_union([mp.buffer(0)]).buffer(BUFFER_UNION_M).buffer(-BUFFER_FRENTE_M)
        metodo = f"buffer_union_{int(BUFFER_UNION_M)}_erosion_{int(BUFFER_FRENTE_M)}"
    poli = poli.intersection(geom_mz)
    return poli, metodo


def metricas(poli, xy: np.ndarray) -> dict:
    area_ha = poli.area / 10_000.0
    hull = MultiPoint([tuple(p) for p in xy]).convex_hull
    coords = list(hull.exterior.coords) if hull.geom_type == "Polygon" else list(hull.coords)
    diam = max((math.dist(a, b) for a, b in combinations(coords, 2)), default=0.0)
    rect = poli.minimum_rotated_rectangle
    rc = list(rect.exterior.coords) if rect.geom_type == "Polygon" else []
    if len(rc) >= 4:
        l1, l2 = math.dist(rc[0], rc[1]), math.dist(rc[1], rc[2])
        largo, ancho = max(l1, l2), max(min(l1, l2), 1.0)
    else:
        largo, ancho = diam, 1.0
    return {"area_ha": round(area_ha, 2), "diametro_m": round(diam, 1),
            "elongacion": round(largo / ancho, 2), "largo_m": round(largo, 1),
            "densidad_ha": round(len(xy) / max(area_ha, 1e-6), 2)}


def es_corredor(m: dict) -> bool:
    return m["elongacion"] >= CORREDOR_ELONG_MIN and m["largo_m"] >= CORREDOR_LARGO_MIN_M


def subdividir(xy: np.ndarray, area_ha: float) -> np.ndarray:
    from sklearn.cluster import KMeans
    k = max(2, math.ceil(area_ha / AREA_OBJETIVO_HA))
    k = min(k, max(2, len(xy) // MIN_LOCALES))
    return KMeans(n_clusters=k, n_init=10, random_state=42).fit_predict(xy)


def procesar_cluster(cid: str, idx: np.ndarray, xy: np.ndarray, geom_mz, ronda: int,
                     poligonos: list, descartes: list, asignacion: dict) -> None:
    """Valida un cluster; lo acepta, descarta o subdivide (recursivo, máx. 2 rondas)."""
    sub_xy = xy[idx]
    if len(sub_xy) < MIN_LOCALES:
        descartes.append({"cluster": cid, "razon": f"menos de {MIN_LOCALES} puntos",
                          "n_puntos": int(len(sub_xy))})
        return
    poli, metodo = poligonizar(sub_xy, geom_mz)
    if poli.is_empty:
        descartes.append({"cluster": cid, "razon": "poligono vacio tras recorte",
                          "n_puntos": int(len(sub_xy))})
        return
    m = metricas(poli, sub_xy)
    if m["densidad_ha"] < DENSIDAD_MIN_HA:
        descartes.append({"cluster": cid, "razon": "densidad < 1 local/ha",
                          "n_puntos": int(len(sub_xy)), **m})
        return
    grande = m["area_ha"] > AREA_MAX_HA or (m["diametro_m"] > DIAM_MAX_M and not es_corredor(m))
    if grande and ronda < MAX_RONDAS_SUBDIVISION:
        sub_labels = subdividir(sub_xy, m["area_ha"])
        for sl in sorted(set(sub_labels)):
            procesar_cluster(f"{cid}.{sl + 1}", idx[sub_labels == sl], xy, geom_mz,
                             ronda + 1, poligonos, descartes, asignacion)
        return
    estado = "ok" if not grande else "grande_no_subdividible"
    for i in idx:
        asignacion[int(i)] = cid
    poligonos.append({"cluster_id": cid, "n_puntos": int(len(sub_xy)), "metodo": metodo,
                      "estado": estado, "es_corredor": es_corredor(m), "ronda": ronda,
                      **m, "geometry": poli})


def main() -> int:
    uni = pd.read_csv(UNIVERSO)
    mz = gpd.read_file(MACROZONAS).to_crs(CRS_METRICO)
    mz = mz.set_index("id")

    g_uni = gpd.GeoDataFrame(uni, geometry=gpd.points_from_xy(uni["lon"], uni["lat"]),
                             crs=CRS_GEO).to_crs(CRS_METRICO)
    g_uni["cluster_final"] = "ruido"

    todos_poligonos, qa_zonas = [], {}
    for mz_id, grupo in g_uni.groupby("macrozona_id"):
        geom_mz = mz.loc[mz_id].geometry
        xy = np.column_stack([grupo.geometry.x.values, grupo.geometry.y.values])
        algoritmo = "hdbscan"
        if len(xy) < MIN_PUNTOS_MACROZONA:
            labels = dbscan_labels(xy)
            algoritmo = "dbscan_fallback"
        else:
            labels, eps_usado = hdbscan_labels(xy)
            if eps_usado != HDB_EPS_M:
                algoritmo = f"hdbscan_epsilon_{int(eps_usado)}_por_bug_sklearn"

        poligonos, descartes, asignacion = [], [], {}
        pos = np.arange(len(xy))
        for lab in sorted(set(labels) - {-1}):
            procesar_cluster(f"{mz_id}_K{lab + 1:02d}", pos[labels == lab], xy, geom_mz,
                             0, poligonos, descartes, asignacion)

        # KDE de contraste: fracción del área de cada polígono dentro del núcleo KDE.
        nucleo = nucleo_kde(xy, geom_mz)
        area_nucleo_ha = round(nucleo.area / 10_000, 2) if nucleo is not None else 0.0
        for p in poligonos:
            if nucleo is not None and p["geometry"].area > 0:
                p["frac_en_nucleo_kde"] = round(
                    p["geometry"].intersection(nucleo).area / p["geometry"].area, 2)
            else:
                p["frac_en_nucleo_kde"] = None

        idx_grupo = grupo.index.to_numpy()
        for local_i, cid in asignacion.items():
            g_uni.loc[idx_grupo[local_i], "cluster_final"] = cid

        area_mz_ha = geom_mz.area / 10_000
        qa_zonas[mz_id] = {
            "algoritmo": algoritmo,
            "n_puntos": int(len(xy)),
            "puntos_por_fuente": grupo.groupby("fuente").size().to_dict(),
            "clusters_brutos": int(len(set(labels) - {-1})),
            "pct_ruido": round(100 * float((labels == -1).mean()), 1),
            "poligonos_aceptados": len(poligonos),
            "descartados": descartes,
            "subdivididos": sorted({p["cluster_id"].split(".")[0] for p in poligonos
                                    if p["ronda"] > 0}),
            "area_macrozona_ha": round(area_mz_ha, 1),
            "area_poligonos_ha": round(sum(p["area_ha"] for p in poligonos), 1),
            "pct_macrozona_cubierta": round(
                100 * sum(p["area_ha"] for p in poligonos) / max(area_mz_ha, 1e-6), 1),
            "area_max_poligono_ha": max((p["area_ha"] for p in poligonos), default=0.0),
            "poligonos_grandes_no_subdivisibles": [p["cluster_id"] for p in poligonos
                                                   if p["estado"] != "ok"],
            "area_nucleo_kde_ha": area_nucleo_ha,
        }
        for p in poligonos:
            p["macrozona_id"] = mz_id
            p["zona_piloto"] = grupo["zona_piloto"].iloc[0]
        todos_poligonos.extend(poligonos)

    nota = ("EXPERIMENTAL - piloto microzonas. No es limite oficial; mide oferta "
            "registrada/habilitaciones historicas + enriquecimiento Places (si lo hay), "
            "no 'locales activos'. Requiere revision humana (DGDGAS).")

    g_poli = gpd.GeoDataFrame(todos_poligonos, geometry="geometry", crs=CRS_METRICO)
    g_poli["nota"] = nota
    g_poli.to_crs(CRS_GEO).to_file(OUT_POLIGONOS, driver="GeoJSON")

    puntos_out = g_uni[["id_punto", "zona_piloto", "macrozona_id", "fuente",
                        "categoria", "cluster_final", "geometry"]].copy()
    puntos_out.to_crs(CRS_GEO).to_file(OUT_PUNTOS, driver="GeoJSON")

    OUT_QA.write_text(json.dumps({"nota": nota, "parametros": {
        "hdbscan": {"min_cluster_size": "max(8, 3%)", "min_samples": HDB_MIN_SAMPLES,
                    "epsilon_m": HDB_EPS_M, "metodo": HDB_METODO},
        "kde": {"bw_m": KDE_BW_M, "grilla_m": KDE_GRILLA_M, "umbral_rel": KDE_UMBRAL_REL},
        "poligonos": {"concave_ratio": CONCAVE_RATIO, "buffer_frente_m": BUFFER_FRENTE_M},
        "control_tamano": {"area_max_ha": AREA_MAX_HA, "area_objetivo_ha": AREA_OBJETIVO_HA,
                           "diam_max_m": DIAM_MAX_M, "min_locales": MIN_LOCALES,
                           "densidad_min_ha": DENSIDAD_MIN_HA},
    }, "zonas": qa_zonas}, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[clusters] {len(todos_poligonos)} poligonos aceptados -> {OUT_POLIGONOS}")
    print(f"[clusters] puntos etiquetados -> {OUT_PUNTOS}")
    print(f"[clusters] QA -> {OUT_QA}")
    for mz_id, q in qa_zonas.items():
        print(f"  {mz_id}: {q['n_puntos']} pts | {q['clusters_brutos']} brutos -> "
              f"{q['poligonos_aceptados']} poligonos | max {q['area_max_poligono_ha']} ha | "
              f"cubre {q['pct_macrozona_cubierta']}% de la macrozona | ruido {q['pct_ruido']}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
