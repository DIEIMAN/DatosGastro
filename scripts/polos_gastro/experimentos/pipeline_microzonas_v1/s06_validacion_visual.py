# -*- coding: utf-8 -*-
"""Etapa V2-2 — Tableros de validacion visual (revision humana, no publicacion).

EXPERIMENTAL. Para cada macrozona de `CASOS_ESTUDIO`, un mapa unico con TODAS las capas
superpuestas para que una persona que conoce la zona pueda juzgar el resultado:

- contenedor de la macrozona (aproximado, doc 01 s4.4)
- subzonas editoriales de referencia (fase16), donde existen, con su etiqueta
- callejero GCBA (avenidas mas marcadas que calles locales) como referencia territorial
- entidades del universo V1, coloreadas por cluster HDBSCAN (gris = ruido)
- poligono "hibrido por reglas" de cada cluster (mismo criterio que s05: corredor -> capsula;
  n<10 -> buffer-union; resto -> concave hull r05)
- nombres de los locales mas relevantes por cluster (hasta 2 por cluster, con nombre real
  -> solo entidades en F01), para no sobrecargar el mapa

Uso:
    .venv/Scripts/python.exe scripts/polos_gastro/experimentos/pipeline_microzonas_v1/s06_validacion_visual.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config  # noqa: E402

CALLEJERO_GEOJSON = (
    config.REPO / "outputs" / "polos_gastro" / "fase15_mapas_callejeros_v3" / "assets"
    / "callejero_gcba_2026_06_02.geojson"
)
SUBZONAS_EDITORIALES_GEOJSON = (
    config.REPO / "outputs" / "polos_gastro" / "fase16_mapas_editoriales_v4" / "tablas"
    / "subzonas_editoriales_geometrias.geojson"
)

CASOS_ESTUDIO = [
    "Palermo", "Avenida Corrientes", "San Telmo", "Belgrano",
    "Chacarita", "Villa Crespo", "Avenida Caseros / Barracas", "Costanera Norte",
]

# Coincidencia por substring contra el campo 'mapa' (con problemas de encoding de origen).
MAPA_EDITORIAL = {
    "Palermo": "Palermo",
    "Avenida Corrientes": "Corrientes",
    "San Telmo": "San Telmo",
    "Belgrano": "Belgrano",
}

PALETA = ["#2a78d6", "#1baf7a", "#eda100", "#008300", "#4a3aa7", "#e34948",
          "#e87ba4", "#eb6834", "#0f766e", "#b45309", "#5b8db0", "#7a5c99"]
COLOR_RUIDO = "#a8a6a1"
COLOR_BARRIOS = "#f2f1ee"
COLOR_CALLE = "#d8d5cf"
COLOR_AVENIDA = "#b9b5ac"
COLOR_CONTENEDOR = "#3a3a3a"


def limpiar_texto(s) -> str:
    return str(s).replace("�", "ñ")


def elegir_metodo_hibrido(sub: pd.DataFrame) -> str:
    disponibles = set(sub["metodo"])
    if sub["es_corredor"].iloc[0] and "capsula_pca" in disponibles:
        return "capsula_pca"
    if sub["n_puntos_cluster"].iloc[0] < 10 and "buffer_union_r70" in disponibles:
        return "buffer_union_r70"
    if "concave_hull_r05_buffer" in disponibles:
        return "concave_hull_r05_buffer"
    return "convex_hull_buffer"


def cargar_capas():
    cont = gpd.read_file(
        config.SALIDA / "macrozonas" / "macrozonas_contenedores.geojson"
    ).to_crs(config.CRS_METRICO)
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

    poligonos = gpd.read_file(
        config.SALIDA / "poligonos" / "poligonos_alternativas.geojson"
    ).to_crs(config.CRS_METRICO)

    callejero = gpd.read_file(CALLEJERO_GEOJSON).to_crs(config.CRS_METRICO)
    barrios = gpd.read_file(config.BARRIOS_GEOJSON).to_crs(config.CRS_METRICO)

    subzonas = gpd.read_file(SUBZONAS_EDITORIALES_GEOJSON).to_crs(config.CRS_METRICO)
    subzonas["mapa"] = subzonas["mapa"].map(limpiar_texto)
    subzonas["etiqueta_visible"] = subzonas["etiqueta_visible"].map(limpiar_texto)

    return cont, gdf, poligonos, callejero, barrios, subzonas


def seleccionar_nombres(sub_gdf: gpd.GeoDataFrame, max_por_cluster: int = 2) -> gpd.GeoDataFrame:
    con_nombre = sub_gdf[
        sub_gdf["en_f01"].astype(bool) & sub_gdf["nombre_canonico"].notna()
        & sub_gdf["nombre_canonico"].astype(str).str.strip().ne("")
        & (sub_gdf["cluster_id"] >= 0)
    ].copy()
    if not len(con_nombre):
        return con_nombre
    con_nombre["importancia"] = (
        con_nombre["en_f01"].astype(int) + con_nombre["en_f02"].astype(int)
        + 0.05 * (con_nombre["n_registros_f01"].fillna(0) + con_nombre["n_registros_f02"].fillna(0))
    )
    return (
        con_nombre.sort_values("importancia", ascending=False)
        .groupby("cluster_id", group_keys=False)
        .head(max_por_cluster)
    )


OFFSETS = [(8, 8), (8, -14), (-8, 8), (-8, -14)]


def etiqueta(ax, x, y, texto, orden, fontsize=8, color="#0b0b0b", peso="normal"):
    dx, dy = OFFSETS[orden % len(OFFSETS)]
    ax.annotate(
        texto, (x, y), xytext=(dx, dy), textcoords="offset points", fontsize=fontsize,
        weight=peso, color=color, ha="left" if dx > 0 else "right",
        va="bottom" if dy > 0 else "top", zorder=9,
        path_effects=[pe.withStroke(linewidth=2.2, foreground="white")],
    )


def tablero_macrozona(macro, cont, gdf, poligonos, callejero, barrios, subzonas, path_png):
    contenedor = cont.loc[cont["macrozona"] == macro, "geometry"].iloc[0]
    sub = gdf[gdf["macrozona"] == macro].copy()
    polis_macro = poligonos[poligonos["macrozona"] == macro]

    minx, miny, maxx, maxy = contenedor.buffer(250).bounds

    fig, ax = plt.subplots(figsize=(15, 15))
    barrios.plot(ax=ax, color=COLOR_BARRIOS, edgecolor="#ffffff", linewidth=0.7, zorder=1)

    calles_zona = callejero.cx[minx:maxx, miny:maxy]
    locales = calles_zona[calles_zona["red_jerarq"] == "VÍA LOCAL"]
    principales = calles_zona[calles_zona["red_jerarq"] != "VÍA LOCAL"]
    locales.plot(ax=ax, color=COLOR_CALLE, linewidth=0.35, zorder=2)
    principales.plot(ax=ax, color=COLOR_AVENIDA, linewidth=0.9, zorder=2)

    clave = MAPA_EDITORIAL.get(macro)
    if clave:
        capa = subzonas[subzonas["mapa"].str.contains(clave, case=False, na=False)]
        for i, (_, r) in enumerate(capa.iterrows()):
            gpd.GeoSeries([r.geometry], crs=config.CRS_METRICO).boundary.plot(
                ax=ax, color=r["color_sugerido"], linewidth=1.3,
                linestyle=(0, (6, 4)), zorder=3, alpha=0.85,
            )
            c = r.geometry.centroid
            ax.annotate(
                r["etiqueta_visible"], (c.x, c.y), fontsize=8.5, style="italic",
                color=r["color_sugerido"], ha="center", zorder=3, alpha=0.95,
                path_effects=[pe.withStroke(linewidth=2.5, foreground="white")],
            )

    gpd.GeoSeries([contenedor], crs=config.CRS_METRICO).boundary.plot(
        ax=ax, color=COLOR_CONTENEDOR, linewidth=1.6, linestyle=(0, (5, 3)), zorder=4
    )

    n_clusters_validos = 0
    for cid, pts in sub[sub["cluster_id"] >= 0].groupby("cluster_id"):
        color = PALETA[int(cid) % len(PALETA)]
        capa_cid = polis_macro[polis_macro["cluster_id"] == cid]
        if len(capa_cid):
            metodo_elegido = elegir_metodo_hibrido(capa_cid)
            geom = capa_cid[capa_cid["metodo"] == metodo_elegido]
            if len(geom):
                gpd.GeoSeries([geom.geometry.iloc[0]], crs=config.CRS_METRICO).plot(
                    ax=ax, color=color, alpha=0.28, edgecolor=color, linewidth=1.6, zorder=5
                )
        ax.scatter(pts.geometry.x, pts.geometry.y, c=color, s=24, edgecolors="white",
                   linewidths=0.5, zorder=6)
        n_clusters_validos += 1

    ruido = sub[sub["cluster_id"] < 0]
    if len(ruido):
        ax.scatter(ruido.geometry.x, ruido.geometry.y, c=COLOR_RUIDO, marker="x", s=20,
                   linewidths=0.9, zorder=5, alpha=0.75)

    nombres = seleccionar_nombres(sub)
    for i, (_, r) in enumerate(nombres.iterrows()):
        etiqueta(ax, r.geometry.x, r.geometry.y, limpiar_texto(r["nombre_canonico"]), i)
    for cid, pts in sub[sub["cluster_id"] >= 0].groupby("cluster_id"):
        cx, cy = pts.geometry.x.mean(), pts.geometry.y.mean()
        ax.annotate(
            f"C{int(cid)} (n={len(pts)})", (cx, cy), fontsize=11, weight="bold",
            ha="center", va="center", color="#0b0b0b", zorder=8,
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec=PALETA[int(cid) % len(PALETA)],
                      alpha=0.85, linewidth=1.4),
        )

    ax.set_xlim(minx, maxx)
    ax.set_ylim(miny, maxy)
    ax.set_axis_off()

    n_ent = len(sub)
    pct_ruido = 100.0 * len(ruido) / n_ent if n_ent else 0.0
    ax.set_title(
        f"VALIDACION VISUAL (interna) - {macro}\n"
        f"{n_ent} entidades del universo V1 | {n_clusters_validos} clusters HDBSCAN | "
        f"ruido {pct_ruido:.0f} % | poligono = metodo hibrido por reglas",
        fontsize=13.5,
    )
    leyenda = [
        Line2D([], [], marker="o", linestyle="", markerfacecolor=PALETA[0],
               markeredgecolor="white", markersize=8, label="Entidad en cluster (color=cluster)"),
        Line2D([], [], marker="x", linestyle="", color=COLOR_RUIDO, markersize=8,
               label="Ruido (sin cluster)"),
        Line2D([], [], color=COLOR_CONTENEDOR, linewidth=1.6, linestyle=(0, (5, 3)),
               label="Contenedor de macrozona (aproximado)"),
        Line2D([], [], color=COLOR_AVENIDA, linewidth=1.4, label="Avenida / via principal"),
        Line2D([], [], color=COLOR_CALLE, linewidth=1.0, label="Calle local"),
    ]
    if clave:
        leyenda.append(Line2D([], [], color="#7a5c99", linewidth=1.3, linestyle=(0, (6, 4)),
                              label="Subzona editorial de referencia (fase 16)"))
    ax.legend(handles=leyenda, loc="upper left", fontsize=9, frameon=True)
    fig.text(
        0.5, 0.01,
        "Material de revision humana, NO de publicacion. " + config.NOTA_EXPERIMENTAL,
        ha="center", fontsize=8, color="#52514e", wrap=True,
    )
    fig.savefig(path_png, dpi=155, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    outdir = config.SALIDA / "validacion" / "tableros"
    outdir.mkdir(parents=True, exist_ok=True)

    cont, gdf, poligonos, callejero, barrios, subzonas = cargar_capas()

    for macro in CASOS_ESTUDIO:
        if macro not in set(cont["macrozona"]):
            print(f"AVISO: {macro} no tiene contenedor (sin semilla suficiente); se omite.")
            continue
        nombre = macro.lower().replace(" ", "_").replace("/", "_")
        ruta = outdir / f"tablero_{nombre}.png"
        tablero_macrozona(macro, cont, gdf, poligonos, callejero, barrios, subzonas, ruta)
        print(f"{macro}: tablero -> {ruta.name}")

    print(f"\nTableros en {outdir}")


if __name__ == "__main__":
    main()
