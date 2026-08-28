# -*- coding: utf-8 -*-
"""Mapas de `macrozonas_v1_experimental.geojson` (Tarea 5).

EXPERIMENTAL. Genera:
  1. mapa_general_macrozonas_v1.png       - las 14 macrozonas sobre barrios CABA
  2. mapa_entidades_macrozonas_v1.png     - lo mismo + entidades del universo V1
  3. mapa_confianza_macrozonas_v1.png     - coloreado por nivel_confianza
  4. mapas_individuales/mapa_<macrozona>.png - un mapa por macrozona con callejero,
     entidades dentro/cerca-fuera y contorno

Uso:
    .venv/Scripts/python.exe scripts/polos_gastro/experimentos/infraestructura_cartografica_v1/generar_mapas_macrozonas_v1.py
"""

from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D

REPO = Path(__file__).resolve().parents[4]
SALIDA = REPO / "outputs/polos_gastro/experimentos/infraestructura_cartografica_v1"
PROTOTIPO = REPO / "outputs/polos_gastro/experimentos/pipeline_microzonas_v1"
BARRIOS_PATH = REPO / "PolosGastro/cartografia/barrios_caba.geojson"
CALLEJERO_PATH = REPO / "outputs/polos_gastro/fase15_mapas_callejeros_v3/assets/callejero_gcba_2026_06_02.geojson"

CRS_GEO = "EPSG:4326"
CRS_METRICO = "EPSG:5347"

NOTA = (
    "Salida experimental (macrozonas_v1_experimental, borrador). No constituye limite "
    "oficial; niveles de confianza alta/media/baja documentados en METODOLOGIA_MACROZONAS_V1.md."
)

COLOR_CONFIANZA = {"alta": "#1a9850", "media": "#eda100", "baja": "#e34948"}
PALETA_NOMBRE = [
    "#2a78d6", "#1baf7a", "#eda100", "#008300", "#4a3aa7", "#e34948", "#e87ba4",
    "#eb6834", "#0f766e", "#b45309", "#5b8db0", "#7a5c99", "#c0392b", "#16697a",
]


def cargar_universo() -> gpd.GeoDataFrame:
    ent = pd.read_csv(
        PROTOTIPO / "universo" / "universo_entidades_v1.csv", dtype={"id_ubicacion": str}
    )
    ent = ent[ent["apta_clustering"]].copy()
    return gpd.GeoDataFrame(
        ent, geometry=gpd.points_from_xy(ent["lon"], ent["lat"]), crs=CRS_GEO
    )


def base_ax(ax, barrios):
    barrios.plot(ax=ax, color="#f2f1ee", edgecolor="white", linewidth=0.5, zorder=1)
    ax.set_axis_off()


def etiqueta(ax, x, y, texto, fontsize=8, color="#0b0b0b"):
    ax.annotate(
        texto, (x, y), fontsize=fontsize, ha="center", color=color, zorder=6,
        path_effects=[pe.withStroke(linewidth=2.2, foreground="white")],
    )


def mapa_general(gdf, barrios, path_png):
    fig, ax = plt.subplots(figsize=(12, 14))
    base_ax(ax, barrios)
    for i, (_, r) in enumerate(gdf.iterrows()):
        color = PALETA_NOMBRE[i % len(PALETA_NOMBRE)]
        gpd.GeoSeries([r.geometry], crs=CRS_GEO).plot(
            ax=ax, color=color, alpha=0.45, edgecolor=color, linewidth=1.2, zorder=3
        )
        c = r.geometry.centroid
        etiqueta(ax, c.x, c.y, r["nombre"], fontsize=7.5)
    ax.set_title(
        "EXPERIMENTAL - macrozonas_v1_experimental (14 features: 12 polos + 2 subzonas)",
        fontsize=13,
    )
    fig.text(0.5, 0.015, NOTA, ha="center", fontsize=8, color="#52514e")
    fig.savefig(path_png, dpi=145, bbox_inches="tight")
    plt.close(fig)


def mapa_entidades(gdf, barrios, universo, path_png):
    fig, ax = plt.subplots(figsize=(12, 14))
    base_ax(ax, barrios)
    ax.scatter(universo.geometry.x, universo.geometry.y, c="#c9c7c2", s=3, zorder=2, alpha=0.6)
    for i, (_, r) in enumerate(gdf.iterrows()):
        color = PALETA_NOMBRE[i % len(PALETA_NOMBRE)]
        gpd.GeoSeries([r.geometry], crs=CRS_GEO).boundary.plot(
            ax=ax, color=color, linewidth=1.4, zorder=3
        )
        c = r.geometry.centroid
        etiqueta(ax, c.x, c.y, r["nombre"], fontsize=7.5)
    ax.set_title(
        f"EXPERIMENTAL - macrozonas_v1 + {len(universo):,} entidades del universo V1",
        fontsize=13,
    )
    leyenda = [Line2D([], [], marker="o", linestyle="", markerfacecolor="#c9c7c2",
                      markersize=5, label="Entidad del universo V1 (F01+F02)")]
    ax.legend(handles=leyenda, loc="upper left", fontsize=9, frameon=True)
    fig.text(0.5, 0.015, NOTA, ha="center", fontsize=8, color="#52514e")
    fig.savefig(path_png, dpi=145, bbox_inches="tight")
    plt.close(fig)


def mapa_confianza(gdf, barrios, path_png):
    fig, ax = plt.subplots(figsize=(12, 14))
    base_ax(ax, barrios)
    for _, r in gdf.iterrows():
        color = COLOR_CONFIANZA[r["nivel_confianza"]]
        gpd.GeoSeries([r.geometry], crs=CRS_GEO).plot(
            ax=ax, color=color, alpha=0.55, edgecolor=color, linewidth=1.2, zorder=3
        )
        c = r.geometry.centroid
        etiqueta(ax, c.x, c.y, r["nombre"], fontsize=7.5)
    n_por_confianza = gdf["nivel_confianza"].value_counts()
    ax.set_title(
        "EXPERIMENTAL - macrozonas_v1 por nivel de confianza\n"
        f"alta={n_por_confianza.get('alta', 0)}  "
        f"media={n_por_confianza.get('media', 0)}  "
        f"baja={n_por_confianza.get('baja', 0)}",
        fontsize=13,
    )
    leyenda = [
        Line2D([], [], marker="s", linestyle="", markerfacecolor=COLOR_CONFIANZA["alta"],
               markersize=10, label="Confianza alta (calles limite reales)"),
        Line2D([], [], marker="s", linestyle="", markerfacecolor=COLOR_CONFIANZA["media"],
               markersize=10, label="Confianza media (barrio oficial +/- semilla o corredor)"),
        Line2D([], [], marker="s", linestyle="", markerfacecolor=COLOR_CONFIANZA["baja"],
               markersize=10, label="Confianza baja (heredado/sin evidencia suficiente)"),
    ]
    ax.legend(handles=leyenda, loc="upper left", fontsize=9, frameon=True)
    fig.text(0.5, 0.015, NOTA, ha="center", fontsize=8, color="#52514e")
    fig.savefig(path_png, dpi=145, bbox_inches="tight")
    plt.close(fig)


def mapas_individuales(gdf, barrios, universo, callejero, outdir):
    outdir.mkdir(parents=True, exist_ok=True)
    universo_m = universo.to_crs(CRS_METRICO)
    for _, r in gdf.iterrows():
        geom_geo = r.geometry
        geom_m = gpd.GeoSeries([geom_geo], crs=CRS_GEO).to_crs(CRS_METRICO).iloc[0]
        minx, miny, maxx, maxy = gpd.GeoSeries([geom_geo], crs=CRS_GEO).total_bounds
        margen = 0.006
        minx, miny, maxx, maxy = minx - margen, miny - margen, maxx + margen, maxy + margen

        fig, ax = plt.subplots(figsize=(10, 10))
        base_ax(ax, barrios)
        calles_zona = callejero.cx[minx:maxx, miny:maxy]
        locales = calles_zona[calles_zona["red_jerarq"] == "VÍA LOCAL"]
        principales = calles_zona[calles_zona["red_jerarq"] != "VÍA LOCAL"]
        locales.plot(ax=ax, color="#d8d5cf", linewidth=0.3, zorder=2)
        principales.plot(ax=ax, color="#b9b5ac", linewidth=0.8, zorder=2)

        gpd.GeoSeries([geom_geo], crs=CRS_GEO).plot(
            ax=ax, color="#2a78d6", alpha=0.30, edgecolor="#2a78d6", linewidth=1.6, zorder=3
        )

        dentro = universo_m[universo_m.within(geom_m)]
        cerca_fuera = universo_m[
            universo_m.within(geom_m.buffer(150)) & ~universo_m.within(geom_m)
        ]
        cerca_fuera_geo = cerca_fuera.to_crs(CRS_GEO)
        dentro_geo = dentro.to_crs(CRS_GEO)
        ax.scatter(cerca_fuera_geo.geometry.x, cerca_fuera_geo.geometry.y, c="#e34948",
                   marker="x", s=16, zorder=4, alpha=0.8)
        ax.scatter(dentro_geo.geometry.x, dentro_geo.geometry.y, c="#1c5cab", s=10,
                   zorder=5, alpha=0.85)

        ax.set_xlim(minx, maxx)
        ax.set_ylim(miny, maxy)
        ax.set_title(
            f"EXPERIMENTAL - {r['nombre']} (confianza {r['nivel_confianza']})\n"
            f"{len(dentro)} entidades dentro, {len(cerca_fuera)} a <=150 m fuera del contorno",
            fontsize=11.5,
        )
        leyenda = [
            Line2D([], [], marker="o", linestyle="", markerfacecolor="#1c5cab",
                   markersize=7, label="Entidad dentro del contorno"),
            Line2D([], [], marker="x", linestyle="", color="#e34948", markersize=7,
                   label="Entidad cercana (<=150 m) pero fuera"),
        ]
        ax.legend(handles=leyenda, loc="upper left", fontsize=8, frameon=True)
        fig.text(0.5, 0.015, NOTA, ha="center", fontsize=7.5, color="#52514e")
        nombre_archivo = r["id"].lower() + ".png"
        fig.savefig(outdir / f"mapa_{nombre_archivo}", dpi=140, bbox_inches="tight")
        plt.close(fig)
        print(f"  {r['nombre']}: mapa individual OK")


def main() -> None:
    import sys
    nombre_archivo = sys.argv[1] if len(sys.argv) > 1 else "macrozonas_v1_experimental.geojson"
    sufijo = Path(nombre_archivo).stem

    gdf = gpd.read_file(SALIDA / nombre_archivo)
    barrios = gpd.read_file(BARRIOS_PATH)
    universo = cargar_universo()
    callejero = gpd.read_file(CALLEJERO_PATH)

    mapa_general(gdf, barrios, SALIDA / f"mapa_general_{sufijo}.png")
    print("mapa general OK")
    mapa_entidades(gdf, barrios, universo, SALIDA / f"mapa_entidades_{sufijo}.png")
    print("mapa entidades OK")
    mapa_confianza(gdf, barrios, SALIDA / f"mapa_confianza_{sufijo}.png")
    print("mapa confianza OK")
    mapas_individuales(gdf, barrios, universo, callejero, SALIDA / f"mapas_individuales_{sufijo}")

    print(f"\nMapas en {SALIDA}")


if __name__ == "__main__":
    main()
