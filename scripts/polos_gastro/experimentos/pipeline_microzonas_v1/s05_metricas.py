# -*- coding: utf-8 -*-
"""Etapa 5 — Metricas objetivas por microzona candidata (y por metodo).

EXPERIMENTAL. Para cada poligono alternativo de la Etapa 4 calcula:

- cantidad de locales del cluster y locales dentro del poligono,
- superficie (ha) y densidad (locales/ha),
- porcentaje de cobertura sobre los locales de la macrozona,
- cantidad de locales del cluster excluidos por el poligono,
- porcentaje de contencion (locales del cluster dentro del poligono),
- elongacion (PCA), compacidad (Polsby-Popper 4*pi*A/P^2),
- distancia media al vecino mas cercano intra-cluster, diametro maximo,
- gates duros y banderas de QA (doc 01 s6).

Ademas:
- selecciona la variante `hibrido_reglas` por cluster (regla del doc 02 s3:
  corredor -> capsula; n < 10 -> buffer-union; resto -> concave 0.5),
- resume por metodo (mediana de area, contencion, % que pasa gates),
- resume los tres detectores (hdbscan / dbscan_continuidad / dbscan_local)
  para la comparacion de la Etapa 6.

Salidas en outputs/.../pipeline_microzonas_v1/metricas/.

Uso:
    .venv/Scripts/python.exe scripts/polos_gastro/experimentos/pipeline_microzonas_v1/s05_metricas.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from scipy.spatial.distance import pdist

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config  # noqa: E402

QA = {k: v["valor"] for k, v in config.PARAMETROS["qa_gates"].items()}
ELONG_MIN = config.PARAMETROS["poligonizacion"]["corredor_elongacion_min"]["valor"]


def metricas_puntos(xy: np.ndarray) -> dict:
    if len(xy) < 2:
        return {"dist_media_vecino_m": 0.0, "diametro_m": 0.0}
    arbol = cKDTree(xy)
    dist, _ = arbol.query(xy, k=2)
    return {
        "dist_media_vecino_m": round(float(dist[:, 1].mean()), 1),
        "diametro_m": round(float(pdist(xy).max()), 0),
    }


def main() -> None:
    config.asegurar_salidas("metricas")

    asig = pd.read_csv(
        config.SALIDA / "macrozonas" / "asignacion_entidades_macrozona.csv",
        dtype={"id_ubicacion": str},
    )
    labels = pd.read_csv(config.SALIDA / "clustering" / "labels_clusters.csv")
    principal = labels[labels["metodo"] == "hdbscan"][["id_entidad", "cluster_id"]]
    asig = asig.merge(principal, on="id_entidad", how="left")
    gdf = gpd.GeoDataFrame(
        asig, geometry=gpd.points_from_xy(asig["lon"], asig["lat"]),
        crs=config.CRS_GEO,
    ).to_crs(config.CRS_METRICO)

    polis = gpd.read_file(
        config.SALIDA / "poligonos" / "poligonos_alternativas.geojson"
    ).to_crs(config.CRS_METRICO)

    filas = []
    for (macro, cid), grupo in polis.groupby(["macrozona", "cluster_id"]):
        pts_macro = gdf[gdf["macrozona"] == macro]
        pts_cluster = pts_macro[pts_macro["cluster_id"] == cid]
        xy = np.column_stack([pts_cluster.geometry.x, pts_cluster.geometry.y])
        base = metricas_puntos(xy)
        for _, r in grupo.iterrows():
            geom = r.geometry
            dentro_cluster = pts_cluster.geometry.within(geom)
            dentro_macro = pts_macro.geometry.within(geom)
            n_cluster = len(pts_cluster)
            n_dentro = int(dentro_cluster.sum())
            area_ha = geom.area / 10_000.0
            perim = geom.length
            compacidad = 4 * np.pi * geom.area / (perim ** 2) if perim > 0 else 0.0
            es_corredor = bool(r["es_corredor"])
            gates = {
                "gate_superficie_max": area_ha > QA["superficie_max_ha"],
                "gate_min_locales": n_cluster < QA["min_locales"],
                "gate_densidad_min": (n_dentro / area_ha if area_ha else 0)
                < QA["densidad_min_ha"],
                "gate_diametro_no_corredor": (
                    not es_corredor and base["diametro_m"] > QA["diametro_max_no_corredor_m"]
                ),
            }
            flags = {
                "flag_superficie": area_ha > QA["superficie_flag_ha"],
                "flag_corredor_no_declarado": (
                    r["elongacion_pca"] > ELONG_MIN and not es_corredor
                ),
            }
            filas.append(
                {
                    "macrozona": macro,
                    "cluster_id": int(cid),
                    "metodo": r["metodo"],
                    "n_locales_cluster": n_cluster,
                    "n_locales_en_poligono": int(dentro_macro.sum()),
                    "n_excluidos_del_cluster": n_cluster - n_dentro,
                    "pct_contencion_cluster": round(100.0 * n_dentro / n_cluster, 1),
                    "pct_cobertura_macrozona": round(
                        100.0 * dentro_macro.sum() / len(pts_macro), 1
                    ),
                    "superficie_ha": round(area_ha, 2),
                    "densidad_locales_ha": round(n_dentro / area_ha, 2) if area_ha else 0,
                    "elongacion_pca": r["elongacion_pca"],
                    "es_corredor": es_corredor,
                    "compacidad_polsby_popper": round(float(compacidad), 3),
                    **base,
                    **gates,
                    "pasa_gates": not any(gates.values()),
                    **flags,
                }
            )

    met = pd.DataFrame(filas)

    # Seleccion hibrida por cluster (regla doc 02 s3, sin decidir un ganador
    # global: es UNA alternativa mas a comparar)
    def variante_hibrida(grupo: pd.DataFrame) -> str:
        disponibles = set(grupo["metodo"])
        if grupo["es_corredor"].iloc[0] and "capsula_pca" in disponibles:
            return "capsula_pca"
        if grupo["n_locales_cluster"].iloc[0] < 10 and "buffer_union_r70" in disponibles:
            return "buffer_union_r70"
        if "concave_hull_r05_buffer" in disponibles:
            return "concave_hull_r05_buffer"
        return "convex_hull_buffer"

    elecciones = (
        met.groupby(["macrozona", "cluster_id"])
        .apply(variante_hibrida, include_groups=False)
        .rename("metodo")
        .reset_index()
    )
    hibrido = met.merge(elecciones, on=["macrozona", "cluster_id", "metodo"])
    hibrido = hibrido.assign(metodo="hibrido_reglas")
    met_total = pd.concat([met, hibrido], ignore_index=True)
    met_total.to_csv(config.SALIDA / "metricas" / "metricas_microzonas.csv", index=False)

    resumen = (
        met_total.groupby("metodo")
        .agg(
            poligonos=("metodo", "size"),
            superficie_mediana_ha=("superficie_ha", "median"),
            superficie_max_ha=("superficie_ha", "max"),
            densidad_mediana_ha=("densidad_locales_ha", "median"),
            contencion_mediana_pct=("pct_contencion_cluster", "median"),
            excluidos_promedio=("n_excluidos_del_cluster", "mean"),
            compacidad_mediana=("compacidad_polsby_popper", "median"),
            pct_pasa_gates=("pasa_gates", lambda s: round(100.0 * s.mean(), 1)),
        )
        .round(2)
        .sort_values("pct_pasa_gates", ascending=False)
    )
    resumen.to_csv(config.SALIDA / "metricas" / "resumen_por_metodo.csv")

    # Comparacion de detectores para la Etapa 6
    filas_det = []
    gdf_idx = gdf.set_index("id_entidad")
    for (macro, metodo), grupo in labels.groupby(["macrozona", "metodo"]):
        serie = grupo.set_index("id_entidad")["cluster_id"]
        pts = gdf_idx.loc[serie.index]
        xy_all = np.column_stack([pts.geometry.x, pts.geometry.y])
        labs = serie.to_numpy()
        tam = pd.Series(labs[labs >= 0]).value_counts()
        diam_max = 0.0
        for c in tam.index:
            sub = xy_all[labs == c]
            if len(sub) >= 2:
                diam_max = max(diam_max, float(pdist(sub).max()))
        filas_det.append(
            {
                "macrozona": macro,
                "detector": metodo,
                "n_puntos": len(labs),
                "clusters": int(len(tam)),
                "pct_ruido": round(100.0 * (labs == -1).sum() / len(labs), 1),
                "tamanio_mediano": float(tam.median()) if len(tam) else 0,
                "tamanio_max": int(tam.max()) if len(tam) else 0,
                "pct_puntos_en_cluster_dominante": round(
                    100.0 * tam.max() / max((labs >= 0).sum(), 1), 1
                ) if len(tam) else 0,
                "diametro_max_m": round(diam_max, 0),
            }
        )
    det = pd.DataFrame(filas_det).sort_values(["macrozona", "detector"])
    det.to_csv(config.SALIDA / "metricas" / "comparacion_detectores.csv", index=False)

    print("Resumen por metodo de poligonizacion:")
    print(resumen.to_string())
    print(f"\nMetricas: {len(met_total)} filas -> metricas_microzonas.csv")
    print("Comparacion de detectores -> comparacion_detectores.csv")


if __name__ == "__main__":
    main()
