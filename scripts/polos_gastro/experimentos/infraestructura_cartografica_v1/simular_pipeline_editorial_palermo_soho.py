# -*- coding: utf-8 -*-
"""Etapa Infra-4 — Simulacion del pipeline con contorno editorial real (Palermo Soho).

EXPERIMENTAL. Compara DOS mundos sobre el mismo universo V1 (Etapa 1 del prototipo):

A) MUNDO ACTUAL (prototipo V1): el contenedor "Palermo" es un hull de la semilla completa
   (Soho+Hollywood+Las Cañitas+Chico+Botánico revueltos) + buffer 500 m; HDBSCAN encuentra
   8 clusters ahi dentro, dos de ellos (C2, C5) sobredimensionados (>70 ha, candidatos a
   segunda pasada, ver validacion V2-4).
B) MUNDO NUEVO (esta etapa): el contorno es el poligono real de Palermo Soho, trazado
   sobre el callejero GCBA a partir de las 4 calles limite documentadas en la ficha
   PG001A (Etapa Infra-4, `construir_poligono_real_palermo_soho.py`).

Flujo simulado: editorial.geojson -> filtrado espacial -> HDBSCAN -> (segunda pasada si
corresponde) -> microzonas. Se corre con los MISMOS parametros/formulas que el pipeline
V1 (nada de HDBSCAN cambia); lo unico distinto es el contorno de entrada.

Pregunta que responde: ¿el contorno real elimina los problemas de la validacion
(clusters sobredimensionados, mezcla de sub-nucleos, dependencia del ruido de semilla)?

Uso:
    .venv/Scripts/python.exe scripts/polos_gastro/historico/experimentos/infraestructura_cartografica_v1/simular_pipeline_editorial_palermo_soho.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shapely
from matplotlib.lines import Line2D
from scipy.spatial.distance import pdist
from shapely.geometry import MultiPoint
from sklearn.cluster import HDBSCAN

REPO = Path(__file__).resolve().parents[4]
PROTOTIPO = REPO / "outputs/polos_gastro/historico/experimentos/pipeline_microzonas_v1"
SALIDA = REPO / "outputs/polos_gastro/historico/experimentos/infraestructura_cartografica_v1"

CRS_GEO = "EPSG:4326"
CRS_METRICO = "EPSG:5347"

# Mismos parametros/formulas que s03_clustering_macrozonas.py del prototipo V1 (no se
# cambia HDBSCAN; solo cambia el contorno de entrada).
HDBSCAN_MIN_SAMPLES = 5
HDBSCAN_EPSILON_M = 50.0
HDBSCAN_METHOD = "eom"
MIN_PUNTOS_MACROZONA = 30
GATE_SUPERFICIE_MAX_HA = 35.0
SEGUNDA_PASADA_EPSILON_M = 25.0

PALETA = ["#2a78d6", "#1baf7a", "#eda100", "#008300", "#4a3aa7", "#e34948",
          "#e87ba4", "#eb6834", "#0f766e", "#b45309"]


def parametros_hdbscan(n: int) -> dict:
    return {
        "min_cluster_size": max(8, int(np.ceil(0.03 * n))),
        "min_samples": HDBSCAN_MIN_SAMPLES,
        "cluster_selection_epsilon": HDBSCAN_EPSILON_M,
        "cluster_selection_method": HDBSCAN_METHOD,
    }


def poligono_concave(xy: np.ndarray, buffer_m: float = 35.0):
    puntos = MultiPoint([tuple(p) for p in xy])
    if len(xy) < 4:
        return puntos.convex_hull.buffer(buffer_m)
    cand = shapely.concave_hull(puntos, ratio=0.5, allow_holes=False)
    base = cand if (cand is not None and not cand.is_empty and cand.is_valid) else puntos.convex_hull
    return base.buffer(buffer_m)


def metricas_cluster(xy: np.ndarray) -> dict:
    poli = poligono_concave(xy)
    diam = float(pdist(xy).max()) if len(xy) >= 2 else 0.0
    area_ha = poli.area / 10_000.0
    return {"area_ha": round(area_ha, 2), "densidad_ha": round(len(xy) / area_ha, 2),
            "diametro_m": round(diam, 0), "poligono": poli}


def main() -> None:
    # --- Universo V1 completo (no solo lo ya asignado al viejo contenedor "Palermo") ---
    ent = pd.read_csv(
        PROTOTIPO / "universo" / "universo_entidades_v1.csv", dtype={"id_ubicacion": str}
    )
    ent = ent[ent["apta_clustering"]].copy()
    gdf_universo = gpd.GeoDataFrame(
        ent, geometry=gpd.points_from_xy(ent["lon"], ent["lat"]), crs=CRS_GEO
    ).to_crs(CRS_METRICO)

    contorno_real = gpd.read_file(SALIDA / "poligono_real_palermo_soho.geojson").to_crs(CRS_METRICO)
    contorno_geom = contorno_real.geometry.iloc[0]

    # --- MUNDO B: filtrado espacial contra el contorno real ---
    dentro = gdf_universo[gdf_universo.geometry.within(contorno_geom)].copy()
    xy_b = np.column_stack([dentro.geometry.x, dentro.geometry.y])
    n_b = len(xy_b)
    print(f"Mundo B (contorno real Palermo Soho): {n_b} entidades filtradas espacialmente")

    if n_b >= MIN_PUNTOS_MACROZONA:
        params_b = parametros_hdbscan(n_b)
        labels_b = HDBSCAN(**params_b).fit_predict(xy_b)
    else:
        raise SystemExit(f"n={n_b} < {MIN_PUNTOS_MACROZONA}: no alcanza para HDBSCAN")

    clusters_b = sorted({c for c in labels_b if c >= 0})
    resumen_b = []
    for cid in clusters_b:
        sub = xy_b[labels_b == cid]
        m = metricas_cluster(sub)
        resumen_b.append({"cluster_id": cid, "n": len(sub), **{k: v for k, v in m.items() if k != "poligono"}})
    tabla_b = pd.DataFrame(resumen_b)
    oversized_b = tabla_b[tabla_b["area_ha"] > GATE_SUPERFICIE_MAX_HA]
    print(f"Mundo B: {len(clusters_b)} clusters, ruido "
          f"{100.0 * (labels_b == -1).sum() / n_b:.1f} %, "
          f"sobredimensionados (>{GATE_SUPERFICIE_MAX_HA} ha): {len(oversized_b)}")
    print(tabla_b.to_string(index=False))

    labels_b_final = labels_b.copy()
    segunda_pasada_aplicada = False
    if len(oversized_b):
        segunda_pasada_aplicada = True
        siguiente_id = labels_b_final.max() + 1
        for cid in oversized_b["cluster_id"]:
            mask = labels_b == cid
            sub_xy = xy_b[mask]
            n_sub = len(sub_xy)
            params_sp = {
                "min_cluster_size": max(5, int(np.ceil(0.03 * n_sub))),
                "min_samples": HDBSCAN_MIN_SAMPLES,
                "cluster_selection_epsilon": SEGUNDA_PASADA_EPSILON_M,
                "cluster_selection_method": "leaf",
            }
            sub_labels = HDBSCAN(**params_sp).fit_predict(sub_xy)
            nuevas = np.where(sub_labels >= 0, sub_labels + siguiente_id, -1)
            labels_b_final[mask] = nuevas
            siguiente_id += int(sub_labels.max()) + 1 if (sub_labels >= 0).any() else 0
            print(f"  segunda pasada sobre cluster {cid} (n={n_sub}) -> "
                  f"{len({c for c in sub_labels if c >= 0})} subclusters")

    # --- MUNDO A: lo que YA hizo el prototipo V1 (para los mismos puntos, si estan) ---
    labels_a = pd.read_csv(PROTOTIPO / "clustering" / "labels_clusters.csv")
    labels_a = labels_a[(labels_a["metodo"] == "hdbscan") & (labels_a["macrozona"] == "Palermo")]
    dentro_ids = set(dentro["id_entidad"])
    solapa = labels_a[labels_a["id_entidad"].isin(dentro_ids)]
    print(f"\nMundo A (prototipo V1, contenedor hull-de-semilla): de las {n_b} entidades "
          f"del poligono real, {len(solapa)} ya estaban asignadas a 'Palermo' en el "
          "prototipo original.")
    print("Distribucion de esas entidades entre los clusters viejos (C-1=ruido):")
    print(solapa["cluster_id"].value_counts().sort_index().to_string())

    # --- Mapa comparativo ---
    fig, axes = plt.subplots(1, 2, figsize=(16, 9))
    for ax in axes:
        ax.set_aspect("equal")
        ax.set_axis_off()

    ax = axes[0]
    gpd.GeoSeries([contorno_geom], crs=CRS_METRICO).boundary.plot(
        ax=ax, color="#1c1c1c", linewidth=1.8, linestyle=(0, (5, 3))
    )
    fuera = gdf_universo[~gdf_universo.geometry.within(contorno_geom)]
    minx, miny, maxx, maxy = contorno_geom.buffer(400).bounds
    fuera_zoom = fuera.cx[minx:maxx, miny:maxy]
    ax.scatter(fuera_zoom.geometry.x, fuera_zoom.geometry.y, c="#c9c7c2", s=10, zorder=2)
    for cid, sub in solapa.groupby("cluster_id"):
        pts = dentro[dentro["id_entidad"].isin(sub["id_entidad"])]
        color = "#a8a6a1" if cid == -1 else PALETA[int(cid) % len(PALETA)]
        marker = "x" if cid == -1 else "o"
        ax.scatter(pts.geometry.x, pts.geometry.y, c=color, marker=marker, s=26,
                   edgecolors="white" if cid >= 0 else None, linewidths=0.5, zorder=4)
    ax.set_xlim(minx, maxx)
    ax.set_ylim(miny, maxy)
    ax.set_title(
        "MUNDO A (actual): mismas entidades, coloreadas por el cluster\n"
        "que ya tenian en el prototipo V1 (contenedor = hull de semilla completa)",
        fontsize=11,
    )

    ax = axes[1]
    gpd.GeoSeries([contorno_geom], crs=CRS_METRICO).boundary.plot(
        ax=ax, color="#1c1c1c", linewidth=1.8, linestyle=(0, (5, 3))
    )
    ax.scatter(fuera_zoom.geometry.x, fuera_zoom.geometry.y, c="#c9c7c2", s=10, zorder=2)
    ruido_b = labels_b_final == -1
    ax.scatter(xy_b[ruido_b, 0], xy_b[ruido_b, 1], c="#a8a6a1", marker="x", s=22, zorder=3)
    for cid in sorted({c for c in labels_b_final if c >= 0}):
        sub = xy_b[labels_b_final == cid]
        ax.scatter(sub[:, 0], sub[:, 1], c=PALETA[int(cid) % len(PALETA)], s=26,
                   edgecolors="white", linewidths=0.5, zorder=4)
    ax.set_xlim(minx, maxx)
    ax.set_ylim(miny, maxy)
    n_cl_final = len({c for c in labels_b_final if c >= 0})
    pct_ruido_final = 100.0 * (labels_b_final == -1).sum() / n_b
    ax.set_title(
        f"MUNDO B (propuesto): HDBSCAN fresco solo dentro del contorno real\n"
        f"{n_cl_final} clusters finales, ruido {pct_ruido_final:.0f} %"
        + (" (incluye segunda pasada)" if segunda_pasada_aplicada else ""),
        fontsize=11,
    )

    fig.suptitle(
        "EXPERIMENTAL - Palermo Soho: contenedor hull-de-semilla vs. poligono editorial real",
        fontsize=13,
    )
    fig.text(
        0.5, 0.02,
        "Gris = entidades fuera del contorno de Palermo Soho o ruido. Borrador sujeto a "
        "revision editorial. No constituye limite oficial.",
        ha="center", fontsize=8.5, color="#52514e",
    )
    fig.savefig(SALIDA / "comparativo_mundo_a_vs_b_palermo_soho.png", dpi=145, bbox_inches="tight")
    plt.close(fig)

    tabla_b.to_csv(SALIDA / "resumen_clusters_mundo_b_palermo_soho.csv", index=False)
    print(f"\nMapa comparativo -> {SALIDA / 'comparativo_mundo_a_vs_b_palermo_soho.png'}")


if __name__ == "__main__":
    main()
