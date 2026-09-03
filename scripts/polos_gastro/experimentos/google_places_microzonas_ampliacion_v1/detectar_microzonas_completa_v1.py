# -*- coding: utf-8 -*-
"""Microclusters y mapas para integracion completa Places microzonas v1.

EXPERIMENTAL / no oficial. Lee `completa_v1/UNIVERSO_COMPLETO_SANITIZADO.csv`
y genera derivados versionados sin tocar el piloto ni el pipeline F01-F05.
"""
from __future__ import annotations

import json
import math
from itertools import combinations
from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from shapely import concave_hull
from shapely.geometry import MultiPoint
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[4]
BASE = (ROOT / "outputs" / "polos_gastro" / "historico" / "experimentos"
        / "google_places_microzonas_ampliacion_v1")
OUT = BASE / "completa_v1"
UNIVERSO = OUT / "UNIVERSO_COMPLETO_SANITIZADO.csv"
MACROZONAS = (ROOT / "outputs" / "polos_gastro" / "historico" / "experimentos"
              / "infraestructura_cartografica_v1" / "macrozonas_editoriales_candidatas_v1.geojson")
OUT_PUNTOS = OUT / "MICROCLUSTERS_COMPLETA_V1.geojson"
OUT_POLIGONOS = OUT / "POLIGONOS_MICROZONAS_COMPLETA_V1.geojson"
OUT_QA = OUT / "qa_clusters_completa_v1.json"
DIR_MAPAS = OUT / "mapas"
OUT_QA_VISUAL = OUT / "qa_visual_mapas_completa_v1.json"

CRS_GEO = "EPSG:4326"
CRS_METRICO = "EPSG:5347"
HDB_MIN_SAMPLES = 5
HDB_EPS_M = 50.0
MIN_PUNTOS_MACROZONA = 30
DBSCAN_FALLBACK = {"eps": 150.0, "min_samples": 4}
CONCAVE_RATIO = 0.4
BUFFER_FRENTE_M = 35.0
BUFFER_UNION_M = 70.0
AREA_MAX_HA = 18.0
AREA_OBJETIVO_HA = 10.0
DIAM_MAX_M = 1000.0
CORREDOR_ELONG_MIN = 3.0
CORREDOR_LARGO_MIN_M = 600.0
MIN_LOCALES = 5
DENSIDAD_MIN_HA = 1.0
MAX_RONDAS_SUBDIVISION = 2

TITULOS = {
    "palermo_soho_hollywood": "Palermo Soho / Palermo Hollywood",
    "corrientes_microcentro": "Avenida Corrientes / Microcentro y Centro",
    "belgrano": "Belgrano",
    "san_telmo": "San Telmo",
    "chacarita": "Chacarita",
    "puerto_madero": "Puerto Madero",
    "costanera_norte": "Costanera Norte",
    "caseros_barracas": "Av. Caseros / Barracas",
    "recoleta": "Recoleta",
    "villa_crespo": "Villa Crespo",
    "caballito": "Caballito",
}
COLORES_POLI = ["#1b9e77", "#d95f02", "#7570b3", "#e7298a", "#66a61e", "#e6ab02",
                "#a6761d", "#666666", "#1f78b4", "#b2df8a", "#fb9a99", "#fdbf6f"]
NOTA = ("EXPERIMENTAL - no es limite oficial. Mide oferta registrada/visible y "
        "habilitaciones historicas; Google Places es senal auxiliar no oficial.")


def hdbscan_labels(xy: np.ndarray) -> tuple[np.ndarray, str]:
    from sklearn.cluster import HDBSCAN
    mcs = max(8, int(round(0.03 * len(xy))))
    for eps in (HDB_EPS_M, 0.0):
        try:
            modelo = HDBSCAN(min_cluster_size=mcs, min_samples=HDB_MIN_SAMPLES,
                             cluster_selection_epsilon=eps,
                             cluster_selection_method="eom")
            return modelo.fit_predict(xy), f"hdbscan_eps_{int(eps)}"
        except TypeError:
            continue
    raise RuntimeError("HDBSCAN fallo incluso con epsilon=0")


def dbscan_labels(xy: np.ndarray) -> tuple[np.ndarray, str]:
    from sklearn.cluster import DBSCAN
    labels = DBSCAN(eps=DBSCAN_FALLBACK["eps"],
                    min_samples=DBSCAN_FALLBACK["min_samples"]).fit_predict(xy)
    return labels, "dbscan_fallback"


def poligonizar(xy: np.ndarray, geom_mz):
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
    return poli.intersection(geom_mz), metodo


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
    sub_xy = xy[idx]
    if len(sub_xy) < MIN_LOCALES:
        descartes.append({"cluster": cid, "razon": "menos_de_5_puntos",
                          "n_puntos": int(len(sub_xy))})
        return
    poli, metodo = poligonizar(sub_xy, geom_mz)
    if poli.is_empty:
        descartes.append({"cluster": cid, "razon": "poligono_vacio",
                          "n_puntos": int(len(sub_xy))})
        return
    m = metricas(poli, sub_xy)
    if m["densidad_ha"] < DENSIDAD_MIN_HA:
        descartes.append({"cluster": cid, "razon": "densidad_baja",
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


def generar_mapas(puntos: gpd.GeoDataFrame, poligonos: gpd.GeoDataFrame, mz: gpd.GeoDataFrame) -> dict:
    DIR_MAPAS.mkdir(parents=True, exist_ok=True)
    qa = {}
    for zona in sorted(puntos["zona_piloto"].unique()):
        f_pts = puntos[puntos["zona_piloto"] == zona]
        mz_ids = sorted(f_pts["macrozona_id"].unique())
        f_mz = mz[mz["id"].isin(mz_ids)]
        f_pol = poligonos[poligonos["zona_piloto"] == zona] if len(poligonos) else poligonos

        fig, ax = plt.subplots(figsize=(11, 11))
        f_mz.boundary.plot(ax=ax, color="#444444", linewidth=1.3, linestyle="--")
        ruido = f_pts[f_pts["cluster_final"] == "ruido"]
        en_cluster = f_pts[f_pts["cluster_final"] != "ruido"]
        ruido_f = ruido[ruido["fuente"] == "F01+F02"]
        ruido_g = ruido[ruido["fuente"] == "google_places"]
        if len(ruido_f):
            ruido_f.plot(ax=ax, color="#b0b0b0", markersize=5, alpha=0.55)
        if len(ruido_g):
            ruido_g.plot(ax=ax, color="#e6ab02", marker="^", markersize=8, alpha=0.5)
        for i, (_, p) in enumerate(f_pol.iterrows()):
            color = COLORES_POLI[i % len(COLORES_POLI)]
            gpd.GeoSeries([p.geometry], crs=CRS_METRICO).plot(
                ax=ax, facecolor=color, edgecolor=color, alpha=0.28, linewidth=1.5)
            pts_cl = en_cluster[en_cluster["cluster_final"] == p["cluster_id"]]
            pf = pts_cl[pts_cl["fuente"] == "F01+F02"]
            pg = pts_cl[pts_cl["fuente"] == "google_places"]
            if len(pf):
                pf.plot(ax=ax, color="#2b2b2b", markersize=8)
            if len(pg):
                pg.plot(ax=ax, color="#e6ab02", marker="^", markersize=12,
                        edgecolor="#2b2b2b", linewidth=0.35)
        legend = [
            Line2D([], [], color="#444444", linestyle="--", label="Macrozona"),
            Line2D([], [], color="#b0b0b0", marker="o", linestyle="", label="F01+F02"),
            Line2D([], [], color="#e6ab02", marker="^", linestyle="", label="Google Places"),
            Patch(facecolor="#1b9e77", alpha=0.30, label=f"Microzonas ({len(f_pol)})"),
        ]
        ax.legend(handles=legend, loc="upper right", fontsize=8, framealpha=0.9)
        ax.set_title(f"Microzonas experimentales - {TITULOS.get(zona, zona)}", fontsize=13)
        ax.set_aspect("equal")
        ax.set_axis_off()
        fig.text(0.5, 0.015, NOTA, ha="center", fontsize=7, color="#555555")
        ruta = DIR_MAPAS / f"mapa_completa_v1_{zona}.png"
        fig.savefig(ruta, dpi=150, bbox_inches="tight")
        plt.close(fig)
        qa[str(ruta)] = {"bytes": ruta.stat().st_size, "puntos": int(len(f_pts)),
                         "poligonos": int(len(f_pol))}
        print(f"[mapa] {ruta}")
    return qa


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    uni = pd.read_csv(UNIVERSO)
    mz = gpd.read_file(MACROZONAS).to_crs(CRS_METRICO).set_index("id", drop=False)
    g_uni = gpd.GeoDataFrame(uni, geometry=gpd.points_from_xy(uni["lon"], uni["lat"]),
                             crs=CRS_GEO).to_crs(CRS_METRICO)
    g_uni["cluster_final"] = "ruido"

    todos_poligonos, qa_zonas = [], {}
    for mz_id, grupo in g_uni.groupby("macrozona_id"):
        geom_mz = mz.loc[mz_id].geometry
        xy = np.column_stack([grupo.geometry.x.values, grupo.geometry.y.values])
        if len(xy) < MIN_PUNTOS_MACROZONA:
            labels, algoritmo = dbscan_labels(xy)
        else:
            labels, algoritmo = hdbscan_labels(xy)
        poligonos, descartes, asignacion = [], [], {}
        pos = np.arange(len(xy))
        for lab in sorted(set(labels) - {-1}):
            procesar_cluster(f"{mz_id}_K{lab + 1:02d}", pos[labels == lab], xy, geom_mz,
                             0, poligonos, descartes, asignacion)
        idx_grupo = grupo.index.to_numpy()
        for local_i, cid in asignacion.items():
            g_uni.loc[idx_grupo[local_i], "cluster_final"] = cid
        area_mz_ha = geom_mz.area / 10_000
        qa_zonas[mz_id] = {
            "zona_piloto": grupo["zona_piloto"].iloc[0],
            "algoritmo": algoritmo,
            "n_puntos": int(len(xy)),
            "puntos_por_fuente": grupo.groupby("fuente").size().to_dict(),
            "clusters_brutos": int(len(set(labels) - {-1})),
            "pct_ruido": round(100 * float((labels == -1).mean()), 1),
            "poligonos_aceptados": len(poligonos),
            "descartados": descartes,
            "area_macrozona_ha": round(area_mz_ha, 1),
            "area_poligonos_ha": round(sum(p["area_ha"] for p in poligonos), 1),
            "pct_macrozona_cubierta": round(
                100 * sum(p["area_ha"] for p in poligonos) / max(area_mz_ha, 1e-6), 1),
            "area_max_poligono_ha": max((p["area_ha"] for p in poligonos), default=0.0),
            "poligonos_grandes_no_subdivisibles": [p["cluster_id"] for p in poligonos
                                                   if p["estado"] != "ok"],
        }
        for p in poligonos:
            p["macrozona_id"] = mz_id
            p["zona_piloto"] = grupo["zona_piloto"].iloc[0]
            p["nota"] = NOTA
        todos_poligonos.extend(poligonos)

    g_poli = gpd.GeoDataFrame(todos_poligonos, geometry="geometry", crs=CRS_METRICO)
    g_poli.to_crs(CRS_GEO).to_file(OUT_POLIGONOS, driver="GeoJSON")
    g_uni[["id_punto", "zona_piloto", "macrozona_id", "fuente", "origen_places",
           "categoria", "cluster_final", "geometry"]].to_crs(CRS_GEO).to_file(
        OUT_PUNTOS, driver="GeoJSON")
    qa_visual = generar_mapas(g_uni, g_poli, mz)
    OUT_QA_VISUAL.write_text(json.dumps(qa_visual, ensure_ascii=False, indent=2),
                             encoding="utf-8")
    OUT_QA.write_text(json.dumps({"nota": NOTA, "zonas": qa_zonas}, ensure_ascii=False,
                                 indent=2), encoding="utf-8")
    print(f"[clusters] {len(todos_poligonos)} poligonos -> {OUT_POLIGONOS}")
    print(f"[clusters] puntos -> {OUT_PUNTOS}")
    print(f"[clusters] QA -> {OUT_QA}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
