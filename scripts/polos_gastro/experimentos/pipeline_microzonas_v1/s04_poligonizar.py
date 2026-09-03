# -*- coding: utf-8 -*-
"""Etapa 4 — Poligonizacion experimental: alternativas comparables por cluster.

EXPERIMENTAL. Genera VARIAS alternativas de poligono por cada cluster del
detector principal (Etapa 3) sin decidir cual gana:

- convex_hull_buffer        referencia/control (se sabe que sobreestima)
- concave_hull_r03_buffer   concave hull agresivo (ratio 0.3) + buffer frente
- concave_hull_r05_buffer   concave hull moderado (ratio 0.5) + buffer frente
- buffer_union_r70          cierre morfologico buffer(+70) -> union -> buffer(-35)
- kde_contorno_40pct        contorno KDE del cluster (bw 100 m, 40 % del max)
- capsula_pca               solo corredores (elongacion > 3 y largo > 600 m):
                            capsula sobre el eje principal PCA, semiancho 60 m

Todos los poligonos se recortan al contenedor de su macrozona (que ya esta
recortado a CABA). Clusters con n < 3 no se poligonizan (marcador puntual).

Salidas:
- poligonos/poligonos_alternativas.geojson  (todas las variantes, con metodo)
- poligonos/mapas/comparativa_<macrozona>.png (grilla de metodos)

Uso:
    .venv/Scripts/python.exe scripts/polos_gastro/historico/experimentos/pipeline_microzonas_v1/s04_poligonizar.py
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
from shapely.geometry import LineString, MultiPoint, Polygon
from shapely.ops import unary_union
from sklearn.neighbors import KernelDensity

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config  # noqa: E402

PALETA = ["#2a78d6", "#1baf7a", "#eda100", "#008300", "#4a3aa7", "#e34948",
          "#e87ba4", "#eb6834", "#0f766e", "#b45309", "#5b8db0", "#7a5c99"]

BUFFER_FRENTE = config.PARAMETROS["poligonizacion"]["buffer_frente_m"]["valor"]
R_UNION = config.PARAMETROS["poligonizacion"]["buffer_union_r_m"]["valor"]
SEMIANCHO = config.PARAMETROS["poligonizacion"]["capsula_semiancho_m"]["valor"]
ELONG_MIN = config.PARAMETROS["poligonizacion"]["corredor_elongacion_min"]["valor"]
LARGO_MIN = config.PARAMETROS["poligonizacion"]["corredor_largo_min_m"]["valor"]
KDE_BW = config.PARAMETROS["clustering"]["kde_bandwidth_m"]["valor"]
KDE_CELDA = config.PARAMETROS["clustering"]["kde_grilla_m"]["valor"]
KDE_UMBRAL = config.PARAMETROS["clustering"]["kde_umbral_relativo"]["valor"]


def forma_pca(xy: np.ndarray) -> dict:
    """Elongacion (raiz del cociente de autovalores) y eje principal."""
    centro = xy.mean(axis=0)
    if len(xy) < 3:
        return {"elongacion": 1.0, "largo_m": 0.0, "centro": centro,
                "eje": np.array([1.0, 0.0])}
    cov = np.cov((xy - centro).T)
    valores, vectores = np.linalg.eigh(cov)
    eje = vectores[:, -1]
    proy = (xy - centro) @ eje
    menor = max(float(valores[0]), 1e-9)
    return {
        "elongacion": float(np.sqrt(valores[-1] / menor)),
        "largo_m": float(proy.max() - proy.min()),
        "centro": centro,
        "eje": eje,
        "proy_min": float(proy.min()),
        "proy_max": float(proy.max()),
    }


def poligono_valido(geom):
    if geom is None or geom.is_empty or not geom.is_valid or geom.area <= 0:
        return None
    return geom


def alternativas_cluster(xy: np.ndarray, contenedor) -> dict:
    """Genera todas las alternativas de poligono para un cluster (>= 3 pts)."""
    puntos = MultiPoint([tuple(p) for p in xy])
    forma = forma_pca(xy)
    out: dict[str, dict] = {}

    def agregar(nombre, geom, nota=""):
        geom = poligono_valido(geom)
        if geom is None:
            return
        geom = poligono_valido(geom.intersection(contenedor))
        if geom is None:
            return
        out[nombre] = {"geometry": geom, "nota_metodo": nota}

    agregar("convex_hull_buffer", puntos.convex_hull.buffer(BUFFER_FRENTE),
            "referencia; se sabe que sobreestima formas no convexas")
    if len(xy) >= 4:
        for ratio, nombre in ((0.3, "concave_hull_r03_buffer"),
                              (0.5, "concave_hull_r05_buffer")):
            cand = shapely.concave_hull(puntos, ratio=ratio, allow_holes=False)
            agregar(nombre, cand.buffer(BUFFER_FRENTE) if cand is not None else None)

    union = unary_union([shapely.geometry.Point(p).buffer(R_UNION) for p in xy])
    agregar("buffer_union_r70", union.buffer(-(R_UNION - BUFFER_FRENTE)),
            f"cierre morfologico +{R_UNION}/-{R_UNION - BUFFER_FRENTE} m")

    # KDE del cluster: contorno al 40 % del maximo local del cluster
    if len(xy) >= 8:
        margen = 250
        minx, miny = xy.min(axis=0) - margen
        maxx, maxy = xy.max(axis=0) + margen
        gx = np.arange(minx, maxx + KDE_CELDA, KDE_CELDA)
        gy = np.arange(miny, maxy + KDE_CELDA, KDE_CELDA)
        mx, my = np.meshgrid(gx, gy)
        grilla = np.column_stack([mx.ravel(), my.ravel()])
        kde = KernelDensity(kernel="gaussian", bandwidth=KDE_BW).fit(xy)
        dens = np.exp(kde.score_samples(grilla)).reshape(mx.shape)
        fig, ax = plt.subplots()
        cs = ax.contour(mx, my, dens, levels=[KDE_UMBRAL * dens.max()])
        partes = []
        for path in cs.get_paths():
            for coords in path.to_polygons():
                if len(coords) >= 4:
                    p = Polygon(coords)
                    if p.is_valid and p.area > 0 and any(
                        p.contains(shapely.geometry.Point(q)) for q in xy
                    ):
                        partes.append(p)
        plt.close(fig)
        if partes:
            agregar("kde_contorno_40pct", unary_union(partes))

    # Capsula PCA solo cuando el cluster ES un corredor (doc 01 s4.6)
    if forma["elongacion"] > ELONG_MIN and forma["largo_m"] > LARGO_MIN:
        a = forma["centro"] + forma["eje"] * forma["proy_min"]
        b = forma["centro"] + forma["eje"] * forma["proy_max"]
        agregar("capsula_pca", LineString([a, b]).buffer(SEMIANCHO),
                "cluster con forma de corredor; eje principal PCA "
                "(pendiente: eje vial real GCBA)")

    return out, forma


def main() -> None:
    config.asegurar_salidas("poligonos", "poligonos/mapas")

    asig = pd.read_csv(
        config.SALIDA / "macrozonas" / "asignacion_entidades_macrozona.csv",
        dtype={"id_ubicacion": str},
    )
    labels = pd.read_csv(config.SALIDA / "clustering" / "labels_clusters.csv")
    principal = labels[labels["metodo"] == "hdbscan"][["id_entidad", "cluster_id"]]
    asig = asig.merge(principal, on="id_entidad", how="left")

    cont = gpd.read_file(
        config.SALIDA / "macrozonas" / "macrozonas_contenedores.geojson"
    ).to_crs(config.CRS_METRICO)

    gdf = gpd.GeoDataFrame(
        asig, geometry=gpd.points_from_xy(asig["lon"], asig["lat"]),
        crs=config.CRS_GEO,
    ).to_crs(config.CRS_METRICO)

    filas = []
    sin_poligono = []
    for macro, sub in gdf.groupby("macrozona"):
        contenedor = cont.loc[cont["macrozona"] == macro, "geometry"].iloc[0]
        for cid, pts in sub[sub["cluster_id"] >= 0].groupby("cluster_id"):
            xy = np.column_stack([pts.geometry.x, pts.geometry.y])
            if len(xy) < 3:
                sin_poligono.append({"macrozona": macro, "cluster_id": int(cid),
                                     "n_puntos": len(xy),
                                     "motivo": "n<3: marcador puntual"})
                continue
            alts, forma = alternativas_cluster(xy, contenedor)
            for metodo, det in alts.items():
                filas.append(
                    {
                        "macrozona": macro,
                        "cluster_id": int(cid),
                        "metodo": metodo,
                        "n_puntos_cluster": len(xy),
                        "elongacion_pca": round(forma["elongacion"], 2),
                        "largo_eje_m": round(forma["largo_m"], 0),
                        "es_corredor": bool(
                            forma["elongacion"] > ELONG_MIN and forma["largo_m"] > LARGO_MIN
                        ),
                        "area_ha": round(det["geometry"].area / 10_000.0, 2),
                        "nota_metodo": det["nota_metodo"],
                        "nota": config.NOTA_EXPERIMENTAL,
                        "geometry": det["geometry"],
                    }
                )

    poligonos = gpd.GeoDataFrame(filas, crs=config.CRS_METRICO)
    poligonos.to_crs(config.CRS_GEO).to_file(
        config.SALIDA / "poligonos" / "poligonos_alternativas.geojson", driver="GeoJSON"
    )
    pd.DataFrame(sin_poligono).to_csv(
        config.SALIDA / "poligonos" / "clusters_sin_poligono.csv", index=False
    )

    # Mapas comparativos: una grilla de metodos por macrozona
    metodos = [m for m in config.PARAMETROS["poligonizacion"]["metodos"]["valor"]]
    barrios = gpd.read_file(config.BARRIOS_GEOJSON).to_crs(config.CRS_METRICO)
    for macro, sub in gdf.groupby("macrozona"):
        polis_macro = poligonos[poligonos["macrozona"] == macro]
        if not len(polis_macro):
            continue
        contenedor = cont.loc[cont["macrozona"] == macro, "geometry"].iloc[0]
        minx, miny, maxx, maxy = contenedor.buffer(200).bounds
        fig, axes = plt.subplots(2, 3, figsize=(16, 11))
        for ax, metodo in zip(axes.ravel(), metodos):
            barrios.plot(ax=ax, color="#f0efec", edgecolor="#ffffff", linewidth=0.5)
            gpd.GeoSeries([contenedor], crs=config.CRS_METRICO).boundary.plot(
                ax=ax, color="#52514e", linewidth=1.0, linestyle=(0, (5, 4))
            )
            ruido = sub[sub["cluster_id"] < 0]
            ax.scatter(ruido.geometry.x, ruido.geometry.y, c="#c9c7c2", marker=".",
                       s=6, zorder=2)
            capa = polis_macro[polis_macro["metodo"] == metodo]
            for _, r in capa.iterrows():
                color = PALETA[int(r["cluster_id"]) % len(PALETA)]
                gpd.GeoSeries([r.geometry], crs=config.CRS_METRICO).plot(
                    ax=ax, color=color, alpha=0.45, edgecolor=color, linewidth=1.2
                )
            nucleo = sub[sub["cluster_id"] >= 0]
            colores = [PALETA[int(c) % len(PALETA)] for c in nucleo["cluster_id"]]
            ax.scatter(nucleo.geometry.x, nucleo.geometry.y, c=colores, s=7,
                       edgecolors="white", linewidths=0.2, zorder=4)
            n_variantes = len(capa)
            ax.set_title(f"{metodo} ({n_variantes} poligonos)", fontsize=10)
            ax.set_xlim(minx, maxx)
            ax.set_ylim(miny, maxy)
            ax.set_axis_off()
        fig.suptitle(
            f"EXPERIMENTAL - Alternativas de poligonizacion: {macro}\n"
            "Mismos clusters (detector principal), seis construcciones de poligono. "
            "Ningun metodo esta elegido.",
            fontsize=13,
        )
        fig.text(0.5, 0.015, config.NOTA_EXPERIMENTAL, ha="center", fontsize=8,
                 color="#52514e")
        nombre = macro.lower().replace(" ", "_").replace("/", "_")
        fig.savefig(config.SALIDA / "poligonos" / "mapas" / f"comparativa_{nombre}.png",
                    dpi=130, bbox_inches="tight")
        plt.close(fig)
        print(f"{macro}: {len(polis_macro)} poligonos "
              f"({polis_macro['cluster_id'].nunique()} clusters x metodos aplicables)")

    print(f"\nTotal poligonos: {len(poligonos)} | clusters sin poligono: {len(sin_poligono)}")
    print(f"Salidas en {config.SALIDA / 'poligonos'}")


if __name__ == "__main__":
    main()
