# -*- coding: utf-8 -*-
"""Tarea 6 — Prueba del pipeline de microzonas usando `macrozonas_v1_experimental` como
contenedor, sobre 2 casos: (A) Palermo Soho/Hollywood, (B) Avenida Corrientes.

EXPERIMENTAL. Mismo detector, mismos parametros que el prototipo V1
(`pipeline_microzonas_v1/s03_clustering_macrozonas.py`): NO se toca HDBSCAN. Lo unico
que cambia es el contenedor de entrada (macrozonas_v1_experimental.geojson en vez del
hull-de-semilla del prototipo).

Caso A (Palermo Soho + Hollywood) ya se corrio en detalle en la Etapa Infra-4
(`simular_pipeline_editorial_palermo_soho.py`); aca se reconfirma que el conteo de
entidades coincide con esta capa final (control de consistencia) sin repetir el analisis
completo.

Caso B (Avenida Corrientes, nuevo): filtrado espacial -> HDBSCAN -> segunda pasada si
corresponde -> comparacion contra el contenedor hull-de-semilla del prototipo V1 para
las mismas entidades.

Uso:
    .venv/Scripts/python.exe scripts/polos_gastro/historico/experimentos/infraestructura_cartografica_v1/probar_pipeline_macrozonas_v1.py
"""

from __future__ import annotations

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

HDBSCAN_MIN_SAMPLES = 5
HDBSCAN_EPSILON_M = 50.0
HDBSCAN_METHOD = "eom"
MIN_PUNTOS_MACROZONA = 30
GATE_SUPERFICIE_MAX_HA = 35.0
SEGUNDA_PASADA_EPSILON_M = 25.0

PALETA = ["#2a78d6", "#1baf7a", "#eda100", "#008300", "#4a3aa7", "#e34948",
          "#e87ba4", "#eb6834", "#0f766e", "#b45309", "#5b8db0", "#7a5c99"]


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


def clusterizar_con_segunda_pasada(xy: np.ndarray) -> tuple[np.ndarray, list[dict]]:
    n = len(xy)
    params = parametros_hdbscan(n)
    labels = HDBSCAN(**params).fit_predict(xy)

    resumen = []
    for cid in sorted({c for c in labels if c >= 0}):
        sub = xy[labels == cid]
        poli = poligono_concave(sub)
        resumen.append({
            "cluster_id": int(cid), "n": len(sub),
            "area_ha": round(poli.area / 10_000.0, 2),
            "diametro_m": round(float(pdist(sub).max()), 0) if len(sub) >= 2 else 0.0,
        })
    tabla = pd.DataFrame(resumen)
    oversized = tabla[tabla["area_ha"] > GATE_SUPERFICIE_MAX_HA] if len(tabla) else tabla

    labels_final = labels.copy()
    n_segunda_pasada = 0
    if len(oversized):
        siguiente_id = int(labels_final.max()) + 1
        for cid in oversized["cluster_id"]:
            mask = labels == cid
            sub_xy = xy[mask]
            n_sub = len(sub_xy)
            params_sp = {
                "min_cluster_size": max(5, int(np.ceil(0.03 * n_sub))),
                "min_samples": HDBSCAN_MIN_SAMPLES,
                "cluster_selection_epsilon": SEGUNDA_PASADA_EPSILON_M,
                "cluster_selection_method": "leaf",
            }
            sub_labels = HDBSCAN(**params_sp).fit_predict(sub_xy)
            nuevas = np.where(sub_labels >= 0, sub_labels + siguiente_id, -1)
            labels_final[mask] = nuevas
            n_hallados = len({c for c in sub_labels if c >= 0})
            siguiente_id += n_hallados
            n_segunda_pasada += 1

    return labels_final, resumen


def cargar_universo() -> gpd.GeoDataFrame:
    ent = pd.read_csv(
        PROTOTIPO / "universo" / "universo_entidades_v1.csv", dtype={"id_ubicacion": str}
    )
    ent = ent[ent["apta_clustering"]].copy()
    return gpd.GeoDataFrame(
        ent, geometry=gpd.points_from_xy(ent["lon"], ent["lat"]), crs=CRS_GEO
    ).to_crs(CRS_METRICO)


def labels_prototipo_v1(macrozona_vieja: str) -> pd.DataFrame:
    labels = pd.read_csv(PROTOTIPO / "clustering" / "labels_clusters.csv")
    return labels[(labels["metodo"] == "hdbscan") & (labels["macrozona"] == macrozona_vieja)]


def correr_caso(nombre_mz: str, id_mz: str, universo_m: gpd.GeoDataFrame,
               gdf_macrozonas: gpd.GeoDataFrame, macrozona_vieja_equivalente: str) -> dict:
    contorno = gdf_macrozonas[gdf_macrozonas["id"] == id_mz].geometry.iloc[0]
    dentro = universo_m[universo_m.within(contorno)].copy()
    n = len(dentro)
    print(f"\n{'=' * 70}\n{nombre_mz} ({id_mz}): {n} entidades dentro del contorno v1")

    if n < MIN_PUNTOS_MACROZONA:
        print(f"n={n} < {MIN_PUNTOS_MACROZONA}: no alcanza para HDBSCAN")
        return {"nombre": nombre_mz, "n_entidades": n, "clusters": 0}

    xy = np.column_stack([dentro.geometry.x, dentro.geometry.y])
    labels, resumen_antes_sp = clusterizar_con_segunda_pasada(xy)
    n_clusters = len({c for c in labels if c >= 0})
    pct_ruido = 100.0 * (labels == -1).sum() / n
    n_oversized = sum(1 for r in resumen_antes_sp if r["area_ha"] > GATE_SUPERFICIE_MAX_HA)
    print(f"HDBSCAN: {len(resumen_antes_sp)} clusters primarios "
          f"({n_oversized} sobredimensionados) -> {n_clusters} clusters finales tras "
          f"segunda pasada, ruido {pct_ruido:.1f}%")

    # Comparacion contra el prototipo V1 (contenedor viejo)
    labels_viejos = labels_prototipo_v1(macrozona_vieja_equivalente)
    dentro_ids = set(dentro["id_entidad"])
    solapa = labels_viejos[labels_viejos["id_entidad"].isin(dentro_ids)]
    dist_vieja = solapa["cluster_id"].value_counts().sort_index()
    print(f"De esas {n} entidades, {len(solapa)} ya estaban en el contenedor viejo "
          f"'{macrozona_vieja_equivalente}'. Distribucion en clusters viejos (-1=ruido):")
    print(dist_vieja.to_string())

    return {
        "nombre": nombre_mz, "n_entidades": n, "clusters_primarios": len(resumen_antes_sp),
        "clusters_finales": n_clusters, "pct_ruido": round(pct_ruido, 1),
        "oversized_primarios": n_oversized,
        "n_en_contenedor_viejo": len(solapa),
        "dist_clusters_viejos": dist_vieja.to_dict(),
        "dentro": dentro, "labels": labels, "contorno": contorno,
    }


def mapa_comparativo(resultado: dict, macrozona_vieja: str, path_png: Path) -> None:
    dentro, labels, contorno = resultado["dentro"], resultado["labels"], resultado["contorno"]
    labels_viejos_df = labels_prototipo_v1(macrozona_vieja).set_index("id_entidad")["cluster_id"]

    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    for ax in axes:
        ax.set_aspect("equal")
        ax.set_axis_off()

    minx, miny, maxx, maxy = contorno.buffer(300).bounds

    ax = axes[0]
    gpd.GeoSeries([contorno], crs=CRS_METRICO).boundary.plot(
        ax=ax, color="#1c1c1c", linewidth=1.5, linestyle=(0, (5, 3))
    )
    cluster_viejo = dentro["id_entidad"].map(labels_viejos_df).fillna(-99).astype(int).to_numpy()
    for cid in sorted(set(cluster_viejo)):
        mask = cluster_viejo == cid
        sub = dentro[mask]
        color = "#a8a6a1" if cid in (-1, -99) else PALETA[int(cid) % len(PALETA)]
        marker = "x" if cid in (-1, -99) else "o"
        ax.scatter(sub.geometry.x, sub.geometry.y, c=color, marker=marker, s=14, zorder=3)
    ax.set_xlim(minx, maxx)
    ax.set_ylim(miny, maxy)
    ax.set_title(f"ANTES: cluster que ya tenian en el contenedor viejo\n"
                f"('{macrozona_vieja}', hull-de-semilla)", fontsize=11)

    ax = axes[1]
    gpd.GeoSeries([contorno], crs=CRS_METRICO).boundary.plot(
        ax=ax, color="#1c1c1c", linewidth=1.5, linestyle=(0, (5, 3))
    )
    ruido = labels == -1
    ax.scatter(dentro.geometry.x[ruido], dentro.geometry.y[ruido], c="#a8a6a1", marker="x", s=14, zorder=3)
    for cid in sorted({c for c in labels if c >= 0}):
        mask = labels == cid
        ax.scatter(dentro.geometry.x[mask], dentro.geometry.y[mask],
                   c=PALETA[int(cid) % len(PALETA)], s=14, zorder=4)
    ax.set_xlim(minx, maxx)
    ax.set_ylim(miny, maxy)
    ax.set_title(f"DESPUES: HDBSCAN fresco dentro del contorno v1 real\n"
                f"{resultado['clusters_finales']} clusters, ruido {resultado['pct_ruido']}%",
                fontsize=11)

    fig.suptitle(f"EXPERIMENTAL - {resultado['nombre']}: contenedor viejo vs. macrozonas_v1", fontsize=13)
    fig.text(0.5, 0.02, "Borrador experimental. No constituye limite oficial.",
            ha="center", fontsize=8.5, color="#52514e")
    fig.savefig(path_png, dpi=140, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    universo_m = cargar_universo()
    gdf_macrozonas = gpd.read_file(SALIDA / "macrozonas_v1_experimental.geojson").to_crs(CRS_METRICO)

    # --- Caso A: control de consistencia Palermo Soho/Hollywood (ya testeado en Infra-4) ---
    for nombre, id_mz in [("Palermo Soho", "MZ_PALERMO_SOHO"),
                           ("Palermo Hollywood", "MZ_PALERMO_HOLLYWOOD")]:
        contorno = gdf_macrozonas[gdf_macrozonas["id"] == id_mz].geometry.iloc[0]
        n = len(universo_m[universo_m.within(contorno)])
        print(f"Control de consistencia {nombre}: {n} entidades "
              "(Infra-4 reporto 373 para Soho, ~213 para Hollywood)")

    # --- Caso B: Avenida Corrientes (nuevo) ---
    resultado_b = correr_caso(
        "Avenida Corrientes", "MZ_AVENIDA_CORRIENTES", universo_m, gdf_macrozonas,
        macrozona_vieja_equivalente="Avenida Corrientes",
    )
    if resultado_b.get("clusters_finales", 0) or resultado_b.get("n_entidades", 0) >= MIN_PUNTOS_MACROZONA:
        mapa_comparativo(resultado_b, "Avenida Corrientes",
                         SALIDA / "comparativo_mundo_a_vs_b_avenida_corrientes.png")
        print(f"\nMapa -> {SALIDA / 'comparativo_mundo_a_vs_b_avenida_corrientes.png'}")

    resumen = pd.DataFrame([{
        k: v for k, v in resultado_b.items() if k not in ("dentro", "labels", "contorno", "dist_clusters_viejos")
    }])
    resumen.to_csv(SALIDA / "resumen_prueba_pipeline_avenida_corrientes.csv", index=False)


if __name__ == "__main__":
    main()
