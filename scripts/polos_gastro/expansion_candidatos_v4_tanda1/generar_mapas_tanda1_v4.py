from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from scipy.spatial import cKDTree
from shapely.geometry import LineString

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "outputs/polos_gastro/historico/expansion_candidatos_v4_tanda1"
AREAS = ROOT / "outputs/polos_gastro/historico/expansion_candidatos_v4_preflight/AREAS_CONSULTA_CANDIDATOS_V4.geojson"
ZONES = {"Z01": "Villa Crespo", "Z02": "Chacarita", "Z03": "Caballito multinodo", "Z04": "Boulevard Caseros — Parque Lezama"}


def load_points(zone: str, universe: str) -> gpd.GeoDataFrame:
    df = pd.read_csv(OUT / "universos" / f"{zone}_UNIVERSO_{universe}.csv", encoding="utf-8-sig")
    return gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon, df.lat), crs="EPSG:4326")


def save(fig, zone: str, stem: str) -> None:
    folder = OUT / "mapas" / zone
    folder.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "svg"):
        fig.savefig(folder / f"{stem}.{ext}", dpi=180 if ext == "png" else None,
                    bbox_inches="tight", facecolor="white")
    plt.close(fig)


def base_ax(area, title: str):
    fig, ax = plt.subplots(figsize=(8, 8))
    area.boundary.plot(ax=ax, color="#283747", linewidth=1.2)
    ax.set_title(title, loc="left", fontsize=13, fontweight="bold")
    ax.set_axis_off()
    ax.text(0.01, 0.01, "EXPERIMENTAL / NO OFICIAL · puntos sanitizados · corte 2026-07-12",
            transform=ax.transAxes, fontsize=7, color="#555555")
    return fig, ax


def main() -> int:
    areas = gpd.read_file(AREAS).to_crs("EPSG:4326")
    clusters = gpd.read_file(OUT / "capas" / "CLUSTERS_ANALITICOS_TANDA1_V4.geojson")
    for zone, name in ZONES.items():
        za = areas[areas["zona_id"] == zone]
        main_area = za[za["geometry_role"] == "AREA_PRINCIPAL"]
        subunits = za[za["geometry_role"] == "SUBUNIDAD_ANALITICA"]
        admin, places, combined = (load_points(zone, u) for u in ("ADMINISTRATIVO", "PLACES", "COMBINADO"))
        for key, pts, color, label in (
            ("01_universo_administrativo", admin, "#246B9E", "Universo administrativo"),
            ("02_universo_places", places, "#D97706", "Universo Places reutilizado"),
            ("03_universo_combinado", combined, "#5B2C6F", "Universo combinado"),
        ):
            fig, ax = base_ax(main_area, f"{name} · {label}")
            pts.plot(ax=ax, color=color, markersize=8, alpha=.65)
            save(fig, zone, key)
        fig, ax = base_ax(main_area, f"{name} · modelo analítico HDBSCAN")
        zc = clusters[(clusters["zona_id"] == zone) & (clusters["universo"] == "COMBINADO")]
        if not zc.empty:
            zc.plot(ax=ax, column="cluster_id", alpha=.25, edgecolor="#7D3C98", linewidth=1.2, cmap="tab20")
        combined.plot(ax=ax, color="#283747", markersize=5, alpha=.45)
        save(fig, zone, "04_mapa_analitico")
        fig, ax = base_ax(main_area, f"{name} · comparación de fuentes/modelos")
        admin.plot(ax=ax, color="#246B9E", markersize=7, alpha=.55, label="F01/F02")
        places.plot(ax=ax, color="#D97706", markersize=7, alpha=.45, label="Places")
        if not zc.empty:
            zc.boundary.plot(ax=ax, color="#7D3C98", linewidth=1.0)
        ax.legend(loc="upper right", fontsize=8)
        save(fig, zone, "05_comparacion_modelos")
        fig, ax = base_ax(main_area, f"{name} · continuidad y vacíos")
        combined.plot(ax=ax, color="#34495E", markersize=6, alpha=.55)
        coords = combined[["lon", "lat"]].to_numpy()
        if len(coords) > 1:
            tree = cKDTree(coords)
            dist, idx = tree.query(coords, k=2)
            gaps = [LineString([coords[i], coords[idx[i, 1]]]) for i in range(len(coords)) if dist[i, 1] > .003]
            if gaps:
                gpd.GeoSeries(gaps, crs="EPSG:4326").plot(ax=ax, color="#C0392B", linewidth=.7, alpha=.55)
        save(fig, zone, "06_continuidad_vacios")
        fig, ax = base_ax(main_area, f"{name} · presentación provisional")
        if not zc.empty:
            zc.plot(ax=ax, color="#8E6E53", alpha=.30, edgecolor="#5D4037", linewidth=1.5)
        if not subunits.empty:
            subunits.boundary.plot(ax=ax, color="#566573", linewidth=.8, linestyle="--")
        save(fig, zone, "07_presentacion_provisional")
    print("MAPAS_OK_56")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
