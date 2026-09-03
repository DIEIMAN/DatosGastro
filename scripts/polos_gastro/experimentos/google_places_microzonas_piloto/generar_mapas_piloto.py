# -*- coding: utf-8 -*-
"""Piloto Google Places + microzonas — Etapa 4: mapas PNG por zona piloto.

EXPERIMENTAL. Un PNG por zona piloto con: contorno de macrozona(s), puntos F01+F02,
puntos Google Places (si los hay), polígonos de microzonas aceptados y puntos ruido.

Uso:
    .venv/Scripts/python.exe scripts/polos_gastro/historico/experimentos/google_places_microzonas_piloto/generar_mapas_piloto.py
"""
from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parents[4]
SALIDA = ROOT / "outputs" / "polos_gastro" / "historico" / "experimentos" / "google_places_microzonas_piloto"
MACROZONAS = (ROOT / "outputs" / "polos_gastro" / "historico" / "experimentos"
              / "infraestructura_cartografica_v1" / "macrozonas_editoriales_candidatas_v1.geojson")
PUNTOS = SALIDA / "MICROCLUSTERS_PILOTO.geojson"
POLIGONOS = SALIDA / "POLIGONOS_MICROZONAS_PILOTO.geojson"
DIR_MAPAS = SALIDA / "mapas"

CRS_METRICO = "EPSG:5347"

ZONAS_PILOTO = {
    "palermo_soho_hollywood": ["MZ_PALERMO_SOHO", "MZ_PALERMO_HOLLYWOOD"],
    "corrientes_microcentro": ["MZ_AVENIDA_CORRIENTES", "MZ_MICROCENTRO_Y_CENTRO"],
    "belgrano": ["MZ_BELGRANO"],
    "san_telmo": ["MZ_SAN_TELMO"],
}
TITULOS = {
    "palermo_soho_hollywood": "Palermo Soho / Palermo Hollywood",
    "corrientes_microcentro": "Avenida Corrientes / Microcentro y Centro",
    "belgrano": "Belgrano",
    "san_telmo": "San Telmo",
}
NOTA = ("EXPERIMENTAL - piloto microzonas (HDBSCAN + poligonos chicos). No es limite "
        "oficial. Mide oferta registrada/habilitaciones, no 'locales activos'. DGDGAS - uso interno.")

COLORES_POLI = ["#1b9e77", "#d95f02", "#7570b3", "#e7298a", "#66a61e", "#e6ab02",
                "#a6761d", "#666666", "#1f78b4", "#b2df8a", "#fb9a99", "#fdbf6f"]


def main() -> int:
    mz = gpd.read_file(MACROZONAS).to_crs(CRS_METRICO)
    puntos = gpd.read_file(PUNTOS).to_crs(CRS_METRICO)
    try:
        poligonos = gpd.read_file(POLIGONOS).to_crs(CRS_METRICO)
    except Exception:
        poligonos = gpd.GeoDataFrame(columns=["zona_piloto", "cluster_id", "geometry"],
                                     geometry="geometry", crs=CRS_METRICO)
    DIR_MAPAS.mkdir(parents=True, exist_ok=True)

    for zona, mz_ids in ZONAS_PILOTO.items():
        f_mz = mz[mz["id"].isin(mz_ids)]
        f_pts = puntos[puntos["zona_piloto"] == zona]
        f_pol = poligonos[poligonos["zona_piloto"] == zona] if len(poligonos) else poligonos

        fig, ax = plt.subplots(figsize=(11, 11))
        f_mz.boundary.plot(ax=ax, color="#444444", linewidth=1.4, linestyle="--")

        ruido = f_pts[f_pts["cluster_final"] == "ruido"]
        en_cluster = f_pts[f_pts["cluster_final"] != "ruido"]
        base = ruido[ruido["fuente"] == "F01+F02"]
        base_pl = ruido[ruido["fuente"] == "google_places"]
        if len(base):
            base.plot(ax=ax, color="#b0b0b0", markersize=6, alpha=0.6)
        if len(base_pl):
            base_pl.plot(ax=ax, color="#e6ab02", marker="^", markersize=10, alpha=0.6)

        leyenda = [
            Line2D([], [], color="#444444", linestyle="--", label="Macrozona contenedora"),
            Line2D([], [], color="#b0b0b0", marker="o", linestyle="", label="F01+F02 (ruido)"),
            Line2D([], [], color="#2b2b2b", marker="o", linestyle="", label="F01+F02 (en cluster)"),
        ]
        if (f_pts["fuente"] == "google_places").any():
            leyenda += [Line2D([], [], color="#e6ab02", marker="^", linestyle="",
                               label="Google Places (sanitizado)")]

        for i, (_, p) in enumerate(f_pol.iterrows()):
            color = COLORES_POLI[i % len(COLORES_POLI)]
            gpd.GeoSeries([p.geometry], crs=CRS_METRICO).plot(
                ax=ax, facecolor=color, edgecolor=color, alpha=0.30, linewidth=1.8)
            pts_cl = en_cluster[en_cluster["cluster_final"] == p["cluster_id"]]
            pf = pts_cl[pts_cl["fuente"] == "F01+F02"]
            pg = pts_cl[pts_cl["fuente"] == "google_places"]
            if len(pf):
                pf.plot(ax=ax, color="#2b2b2b", markersize=9)
            if len(pg):
                pg.plot(ax=ax, color="#e6ab02", marker="^", markersize=14,
                        edgecolor="#2b2b2b", linewidth=0.4)
            c = p.geometry.centroid
            ax.annotate(f"{p['cluster_id'].split('_K')[-1]}\n{p['area_ha']} ha",
                        (c.x, c.y), fontsize=7, ha="center", color="#1a1a1a",
                        bbox=dict(facecolor="white", alpha=0.65, edgecolor="none", pad=1))
        if len(f_pol):
            leyenda.append(Patch(facecolor="#1b9e77", alpha=0.35,
                                 label=f"Microzonas aceptadas ({len(f_pol)})"))

        ax.set_title(f"Piloto microzonas — {TITULOS[zona]}", fontsize=13)
        ax.legend(handles=leyenda, loc="upper right", fontsize=8, framealpha=0.9)
        ax.set_aspect("equal")
        ax.set_axis_off()
        fig.text(0.5, 0.015, NOTA, ha="center", fontsize=7, color="#555555")
        ruta = DIR_MAPAS / f"mapa_piloto_{zona}.png"
        fig.savefig(ruta, dpi=150, bbox_inches="tight")
        plt.close(fig)
        print(f"[mapa] {ruta}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
