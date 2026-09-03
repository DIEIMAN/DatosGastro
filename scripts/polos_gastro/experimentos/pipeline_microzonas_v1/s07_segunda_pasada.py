# -*- coding: utf-8 -*-
"""Etapa V2-4 — Segunda pasada jerarquica sobre clusters HDBSCAN sobredimensionados.

EXPERIMENTAL. NO reemplaza el detector de la Etapa 3 ni cambia ningun parametro global.
Es una prueba paralela: para cada cluster que supera el gate de superficie (> 35 ha,
`metricas/metricas_microzonas.csv`, metodo hibrido_reglas), se toman SOLO sus puntos y se
corre HDBSCAN una segunda vez, con:

- min_cluster_size = max(5, 3% de los puntos del cluster) -- misma formula relativa que la
  Etapa 3, pero recalculada sobre el subconjunto (no un numero fijo menor "a mano").
- cluster_selection_epsilon = 25 m (mitad del valor de la Etapa 3: al subdividir un nucleo
  ya denso, la separacion util es mas fina, del orden de una vereda/media cuadra).
- cluster_selection_method = "leaf": extrae las hojas de la jerarquia en vez de los
  clusters mas estables (eom); leaf tiende a dar mas granularidad, que es lo que se busca
  al forzar una segunda division (doc 02 s2.1).

Se comparan metricas antes/despues (n subclusters, ruido, diametro, area por subcluster) y
se genera un mapa de dos paneles (monolito vs. segunda pasada) por caso.

Uso:
    .venv/Scripts/python.exe scripts/polos_gastro/historico/experimentos/pipeline_microzonas_v1/s07_segunda_pasada.py
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
from scipy.spatial.distance import pdist
from shapely.geometry import MultiPoint
from sklearn.cluster import HDBSCAN

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config  # noqa: E402

PALETA = ["#2a78d6", "#1baf7a", "#eda100", "#008300", "#4a3aa7", "#e34948",
          "#e87ba4", "#eb6834", "#0f766e", "#b45309"]
COLOR_RUIDO = "#a8a6a1"
BUFFER_FRENTE = config.PARAMETROS["poligonizacion"]["buffer_frente_m"]["valor"]

EPSILON_SEGUNDA_PASADA_M = 25.0  # mitad del epsilon de la Etapa 3 (50 m); justificacion arriba.


def poligono_concave(xy: np.ndarray):
    puntos = MultiPoint([tuple(p) for p in xy])
    if len(xy) < 4:
        return puntos.convex_hull.buffer(BUFFER_FRENTE)
    cand = shapely.concave_hull(puntos, ratio=0.5, allow_holes=False)
    base = cand if (cand is not None and not cand.is_empty and cand.is_valid) else puntos.convex_hull
    return base.buffer(BUFFER_FRENTE)


def identificar_oversized() -> pd.DataFrame:
    met = pd.read_csv(config.SALIDA / "metricas" / "metricas_microzonas.csv")
    hib = met[met["metodo"] == "hibrido_reglas"]
    oversized = hib[hib["gate_superficie_max"]][
        ["macrozona", "cluster_id", "n_locales_cluster", "superficie_ha", "diametro_m"]
    ].drop_duplicates()
    return oversized.sort_values("n_locales_cluster", ascending=False)


def segunda_pasada(xy: np.ndarray) -> np.ndarray:
    n = len(xy)
    params = {
        "min_cluster_size": max(5, int(np.ceil(0.03 * n))),
        "min_samples": config.PARAMETROS["clustering"]["hdbscan_min_samples"]["valor"],
        "cluster_selection_epsilon": EPSILON_SEGUNDA_PASADA_M,
        "cluster_selection_method": "leaf",
    }
    labels = HDBSCAN(**params).fit_predict(xy)
    return labels, params


def metricas_subclusters(xy: np.ndarray, labels: np.ndarray) -> list[dict]:
    filas = []
    for cid in sorted({c for c in labels if c >= 0}):
        sub = xy[labels == cid]
        poli = poligono_concave(sub)
        diam = float(pdist(sub).max()) if len(sub) >= 2 else 0.0
        filas.append(
            {
                "subcluster_id": int(cid),
                "n_locales": len(sub),
                "area_ha": round(poli.area / 10_000.0, 2),
                "densidad_ha": round(len(sub) / (poli.area / 10_000.0), 2),
                "diametro_m": round(diam, 0),
            }
        )
    return filas


def mapa_antes_despues(macro, cid, xy, labels_despues, params, path_png):
    fig, axes = plt.subplots(1, 2, figsize=(14, 7.5))
    for ax in axes:
        ax.set_aspect("equal")
        ax.set_axis_off()

    ax = axes[0]
    poli_mono = poligono_concave(xy)
    gpd.GeoSeries([poli_mono], crs=config.CRS_METRICO).plot(
        ax=ax, color=PALETA[0], alpha=0.30, edgecolor=PALETA[0], linewidth=1.4
    )
    ax.scatter(xy[:, 0], xy[:, 1], c=PALETA[0], s=20, edgecolors="white", linewidths=0.4)
    ax.set_title(f"ANTES: 1 cluster monolitico (n={len(xy)})", fontsize=11)

    ax = axes[1]
    ruido = labels_despues == -1
    if ruido.any():
        ax.scatter(xy[ruido, 0], xy[ruido, 1], c=COLOR_RUIDO, marker="x", s=18,
                   linewidths=0.8, alpha=0.8)
    n_sub = 0
    for scid in sorted({c for c in labels_despues if c >= 0}):
        sub = xy[labels_despues == scid]
        color = PALETA[scid % len(PALETA)]
        poli = poligono_concave(sub)
        gpd.GeoSeries([poli], crs=config.CRS_METRICO).plot(
            ax=ax, color=color, alpha=0.35, edgecolor=color, linewidth=1.4
        )
        ax.scatter(sub[:, 0], sub[:, 1], c=color, s=20, edgecolors="white", linewidths=0.4)
        n_sub += 1
    pct_ruido = 100.0 * ruido.sum() / len(labels_despues)
    ax.set_title(
        f"DESPUES: HDBSCAN leaf sobre el cluster (mcs={params['min_cluster_size']}, "
        f"eps={params['cluster_selection_epsilon']:.0f} m)\n"
        f"{n_sub} subclusters, ruido {pct_ruido:.0f} %",
        fontsize=11,
    )
    margen = 60
    minx, miny = xy.min(axis=0) - margen
    maxx, maxy = xy.max(axis=0) + margen
    for a in axes:
        a.set_xlim(minx, maxx)
        a.set_ylim(miny, maxy)
    fig.suptitle(
        f"EXPERIMENTAL - Segunda pasada jerarquica: {macro} / cluster C{cid} "
        "(candidato por superar 35 ha)",
        fontsize=13,
    )
    fig.text(0.5, 0.02, config.NOTA_EXPERIMENTAL, ha="center", fontsize=8, color="#52514e")
    fig.savefig(path_png, dpi=140, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    outdir = config.SALIDA / "segunda_pasada"
    (outdir / "mapas").mkdir(parents=True, exist_ok=True)

    oversized = identificar_oversized()
    print(f"Clusters sobredimensionados a probar: {len(oversized)}")
    print(oversized.to_string(index=False))

    asig = pd.read_csv(
        config.SALIDA / "macrozonas" / "asignacion_entidades_macrozona.csv",
        dtype={"id_ubicacion": str},
    )
    labels = pd.read_csv(config.SALIDA / "clustering" / "labels_clusters.csv")
    principal = labels[labels["metodo"] == "hdbscan"][["id_entidad", "cluster_id"]]
    asig = asig.merge(principal, on="id_entidad", how="left")
    gdf = gpd.GeoDataFrame(
        asig, geometry=gpd.points_from_xy(asig["lon"], asig["lat"]), crs=config.CRS_GEO
    ).to_crs(config.CRS_METRICO)

    filas_resumen = []
    for _, caso in oversized.iterrows():
        macro, cid = caso["macrozona"], int(caso["cluster_id"])
        sub = gdf[(gdf["macrozona"] == macro) & (gdf["cluster_id"] == cid)]
        xy = np.column_stack([sub.geometry.x, sub.geometry.y])

        labels_despues, params = segunda_pasada(xy)
        n_sub = len({c for c in labels_despues if c >= 0})
        pct_ruido_despues = round(100.0 * (labels_despues == -1).sum() / len(labels_despues), 1)
        metricas_sub = metricas_subclusters(xy, labels_despues)

        nombre = f"{macro.lower().replace(' ', '_').replace('/', '_')}_c{cid}"
        mapa_antes_despues(
            macro, cid, xy, labels_despues, params,
            outdir / "mapas" / f"segunda_pasada_{nombre}.png",
        )

        filas_resumen.append(
            {
                "macrozona": macro,
                "cluster_id": cid,
                "n_locales_original": len(xy),
                "area_ha_original": caso["superficie_ha"],
                "diametro_m_original": caso["diametro_m"],
                "subclusters_encontrados": n_sub,
                "pct_ruido_segunda_pasada": pct_ruido_despues,
                "min_cluster_size_usado": params["min_cluster_size"],
                "cluster_selection_epsilon_usado": params["cluster_selection_epsilon"],
                "mejora": (
                    "SI: se separaron sub-nucleos" if n_sub >= 2
                    else "NO: sigue siendo 1 bloque (o todo ruido)"
                ),
            }
        )
        for m in metricas_sub:
            m.update({"macrozona": macro, "cluster_id_original": cid})
        pd.DataFrame(metricas_sub).to_csv(
            outdir / f"subclusters_{nombre}.csv", index=False
        )
        print(f"{macro} C{cid} (n={len(xy)}, {caso['superficie_ha']} ha) -> "
              f"{n_sub} subclusters, ruido {pct_ruido_despues}%")

    resumen = pd.DataFrame(filas_resumen)
    resumen.to_csv(outdir / "resumen_segunda_pasada.csv", index=False)
    print(f"\nResumen -> {outdir / 'resumen_segunda_pasada.csv'}")
    print(f"Mejoraron (>=2 subclusters): {(resumen['subclusters_encontrados'] >= 2).sum()} "
          f"de {len(resumen)}")


if __name__ == "__main__":
    main()
