#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D-4: comparacion de paletas de familia, en color y en escala de grises.

La paleta A es la aprobada en el plan. La paleta B corrige el fallo de contraste:
sus cinco familias estan separadas por una escalera de luminancia, de modo que
siguen siendo distinguibles cuando el Atlas se imprime en blanco y negro.
"""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
sys.dont_write_bytecode = True

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from PIL import Image
from shapely.ops import unary_union

plt.rcParams.update({"font.family": "DejaVu Sans", "axes.unicode_minus": False})

SCRIPT = Path(__file__).resolve()
OUT = SCRIPT.parent.parent


def repo_root(start: Path) -> Path:
    for c in (start, *start.parents):
        if (c / ".git").exists():
            return c
    raise RuntimeError("sin raiz")


REPO = repo_root(SCRIPT)
QA = OUT / "qa"
CRS_M = "EPSG:5347"

PALETA_A = {
    "polo": "#1F3B57", "multiparte": "#2C7FB8", "eje": "#C0762B",
    "segmentada": "#2D7A68", "dispersa": "#7353A6",
}
PALETA_B = {
    "polo": "#1A3A5A", "dispersa": "#895BB2", "segmentada": "#3CA18D",
    "multiparte": "#7BB4D9", "eje": "#E6C194",
}
ETIQUETA = {
    "polo": "Polo", "multiparte": "Polo con subzonas / multiparte",
    "eje": "Eje o corredor", "segmentada": "Area segmentada",
    "dispersa": "Referencia dispersa",
}


def panel(env, barrios, comunas, paleta, alpha, destino: Path) -> Path:
    caba = unary_union(list(barrios.geometry))
    fig = plt.figure(figsize=(7.2, 8.4), dpi=140)
    ax = fig.add_axes([0.02, 0.02, 0.96, 0.96])
    comunas.plot(ax=ax, facecolor="#F7F9FB", edgecolor="#DCE3EA", linewidth=0.6, zorder=0)
    gpd.GeoSeries([caba], crs=CRS_M).plot(ax=ax, facecolor="none", edgecolor="#93A3B5",
                                          linewidth=1.4, zorder=2)
    for _, f in env.iterrows():
        color = paleta[f.familia]
        punteado = f.trazo == "punteado"
        gpd.GeoSeries([f.geometry], crs=CRS_M).plot(
            ax=ax, facecolor=color, alpha=alpha if not punteado else alpha * 0.72,
            edgecolor=color, linewidth=1.1,
            linestyle=(0, (3, 2)) if punteado else "solid", zorder=6)
    for _, f in env.iterrows():
        piezas = (list(f.geometry.geoms) if f.geometry.geom_type == "MultiPolygon"
                  else [f.geometry])
        p = max(piezas, key=lambda g: g.area).representative_point()
        ax.annotate(f.referencia_id[1:], xy=(p.x, p.y), ha="center", va="center",
                    fontsize=6.5, fontweight="bold", color="white", zorder=10,
                    bbox=dict(boxstyle="circle,pad=0.26", fc=paleta[f.familia],
                              ec="white", lw=0.8))
    ax.set_aspect("equal")
    ax.axis("off")
    ax.legend(handles=[Patch(facecolor=paleta[k], alpha=alpha, edgecolor=paleta[k],
                             label=ETIQUETA[k]) for k in ETIQUETA],
              loc="lower left", fontsize=7, frameon=True, framealpha=0.95,
              edgecolor="#D9DEE5")
    fig.savefig(destino, facecolor="white")
    plt.close(fig)
    return destino


def main() -> int:
    env = gpd.read_file(OUT / "capas/envolventes_editoriales_v2.geojson").to_crs(CRS_M)
    barrios = gpd.read_file(REPO / "data/raw/geo_barrios.geojson").to_crs(CRS_M)
    comunas = gpd.read_file(REPO / "data/raw/geo_comunas.geojson").to_crs(CRS_M)
    tmp = QA / "_paletas"
    tmp.mkdir(parents=True, exist_ok=True)

    a = panel(env, barrios, comunas, PALETA_A, 0.55, tmp / "a.png")
    b = panel(env, barrios, comunas, PALETA_B, 0.55, tmp / "b.png")
    ia, ib = Image.open(a).convert("RGB"), Image.open(b).convert("RGB")
    ga, gb = ia.convert("L").convert("RGB"), ib.convert("L").convert("RGB")

    w, h = ia.size
    banda = 54
    hoja = Image.new("RGB", (w * 2, (h + banda) * 2), "white")
    from PIL import ImageDraw, ImageFont
    f_dir = REPO / ".venv/Lib/site-packages/matplotlib/mpl-data/fonts/ttf"
    fb = ImageFont.truetype(str(f_dir / "DejaVuSans-Bold.ttf"), 24)
    fr = ImageFont.truetype(str(f_dir / "DejaVuSans.ttf"), 17)
    d = ImageDraw.Draw(hoja)
    celdas = [
        (0, 0, ia, "PALETA A (aprobada en el plan) · color",
         "6 de 10 pares indistinguibles en gris"),
        (w, 0, ib, "PALETA B (reemplazo propuesto) · color",
         "escalera de luminancia; 10 de 10 pares separables"),
        (0, h + banda, ga, "PALETA A · escala de grises",
         "las familias colapsan: no se puede leer impresa en blanco y negro"),
        (w, h + banda, gb, "PALETA B · escala de grises",
         "las cinco familias siguen ordenadas de oscuro a claro"),
    ]
    for x, y, im, titulo, nota in celdas:
        d.text((x + 16, y + 8), titulo, fill="#1F3B57", font=fb)
        d.text((x + 16, y + 34), nota, fill="#555555", font=fr)
        hoja.paste(im, (x, y + banda))

    destino = QA / "AG3_PALETAS_COMPARACION.png"
    hoja.save(destino, optimize=True)
    print("comparacion de paletas:", destino)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
