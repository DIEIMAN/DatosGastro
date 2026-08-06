#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Salidas de revision del bloque B2 (punto de corte AG-2 / AG-3).

Produce, sin tocar ningun insumo:
  qa/AG2_HOJA_CONTACTOS_ENVOLVENTES_22.png  antes (Atlas V1) | despues (envolvente V2)
  qa/AG3_BORRADOR_MAPA_GENERAL.png          borrador del mapa de CABA con las 22 formas

Es material de revision en raster: el Atlas V2 dibujara estas mismas geometrias como
vectores nativos del PDF (D-2). Aca solo se trata de poder mirarlas.
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
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from PIL import Image, ImageDraw, ImageFont
from shapely.ops import unary_union

plt.rcParams.update({"font.family": "DejaVu Sans", "axes.unicode_minus": False})

SCRIPT = Path(__file__).resolve()
OUT = SCRIPT.parent.parent


def repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / ".git").exists():
            return candidate
    raise RuntimeError("No se encontro la raiz del repositorio")


REPO = repo_root(SCRIPT)
CAPAS = OUT / "capas"
QA = OUT / "qa"
TMP = QA / "_miniaturas"

ATLAS_V1_MAPS = (REPO / "outputs/polos_gastro/INFORMEFINAL/claude"
                 / "atlas_22_edicion_institucional_v1/assets_derivados/mapas_publicacion")

MAIN_NAMES = {
    "R01": "R01_PALERMO.png", "R02": "R02_AVENIDA_CORRIENTES.png",
    "R03": "R03_SAN_TELMO.png", "R04": "R04_PUERTO_MADERO.png",
    "R05": "R05_BELGRANO.png", "R06": "R06_RECOLETA.png",
    "R07": "R07_COSTANERA_NORTE.png", "R08": "R08_VILLA_CRESPO.png",
    "R09": "R09_CHACARITA.png", "R10": "R10_CABALLITO.png",
    "R11": "R11_BOULEVARD_CASEROS.png", "R12": "R12_CENTRO_MICROCENTRO_SEGMENTADO.png",
    "R13": "R13_ABASTO.png", "R14": "R14_AVENIDA_BOEDO.png",
    "R15": "R15_DEVOTO.png", "R16": "R16_DONADO_HOLMBERG.png",
    "R17": "R17_VILLA_URQUIZA.png", "R18": "R18_ESMERALDA_PARAGUAY.png",
    "R19": "R19_FEDERICO_LACROZE_POR_TRAMOS.png", "R20": "R20_GARCIA_DEL_RIO.png",
    "R21": "R21_LA_PATERNAL.png", "R22": "R22_VILLA_PUEYRREDON.png",
}

CRS_M = "EPSG:5347"
GRIS_BARRIO = "#F2F5F8"
GRIS_BORDE = "#D5DCE4"
GRIS_CALLE = "#DFE5EB"


def fuente(size: int, bold: bool = False):
    base = REPO / ".venv/Lib/site-packages/matplotlib/mpl-data/fonts/ttf"
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(str(base / name), size)


def cargar():
    env = gpd.read_file(CAPAS / "envolventes_editoriales_v2.geojson").to_crs(CRS_M)
    barrios = gpd.read_file(REPO / "data/raw/geo_barrios.geojson").to_crs(CRS_M)
    comunas = gpd.read_file(REPO / "data/raw/geo_comunas.geojson").to_crs(CRS_M)
    calles = gpd.read_file(
        REPO / "outputs/polos_gastro/FASE5-29/fase15_mapas_callejeros_v3/assets"
             / "callejero_gcba_2026_06_02.geojson").to_crs(CRS_M)
    return env.sort_values("referencia_id"), barrios, comunas, calles


def barra_escala(ax, metros: int) -> None:
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    px = x0 + 0.06 * (x1 - x0)
    py = y0 + 0.06 * (y1 - y0)
    ax.plot([px, px + metros], [py, py], color="#111827", lw=3.5, solid_capstyle="butt", zorder=40)
    ax.text(px + metros / 2, py + 0.022 * (y1 - y0), f"{metros} m", ha="center", va="bottom",
            fontsize=8, color="#111827", zorder=40)


def dibujar_referencia(ax, fila, barrios, calles) -> None:
    geom = fila.geometry
    minx, miny, maxx, maxy = geom.bounds
    dx, dy = maxx - minx, maxy - miny
    pad = 0.16 * max(dx, dy)
    minx, maxx = minx - pad, maxx + pad
    miny, maxy = miny - pad, maxy + pad

    loc_b = barrios.cx[minx:maxx, miny:maxy]
    if not loc_b.empty:
        loc_b.plot(ax=ax, facecolor=GRIS_BARRIO, edgecolor=GRIS_BORDE, linewidth=0.5, zorder=0)
    loc_c = calles.cx[minx:maxx, miny:maxy]
    if not loc_c.empty:
        loc_c.plot(ax=ax, color=GRIS_CALLE, linewidth=0.35, zorder=1)

    punteado = fila.trazo == "punteado"
    gpd.GeoSeries([geom], crs=CRS_M).plot(
        ax=ax, facecolor=fila.color, alpha=0.20 if punteado else 0.30,
        edgecolor=fila.color, linewidth=1.4,
        linestyle=(0, (4, 2.4)) if punteado else "solid", zorder=5)

    ax.set_xlim(minx, maxx)
    ax.set_ylim(miny, maxy)
    ax.set_aspect("equal")
    ax.axis("off")
    barra_escala(ax, 250 if max(dx, dy) < 2200 else 500)


def render_nuevo(fila, barrios, calles, destino: Path, px: int = 620) -> Path:
    fig = plt.figure(figsize=(px / 100, px * 1.15 / 100), dpi=100)
    ax = fig.add_axes([0.02, 0.02, 0.96, 0.90])
    dibujar_referencia(ax, fila, barrios, calles)
    piezas = "1 pieza" if fila.piezas == 1 else f"{fila.piezas} piezas"
    fig.text(0.03, 0.965, f"{fila.referencia_id}  {fila.nombre}", fontsize=11,
             fontweight="bold", color="#1F3B57", va="top")
    fig.text(0.03, 0.925, f"{fila.familia_etiqueta} · {fila.registro} · {piezas} · "
                          f"{fila.area_km2:.2f} km²", fontsize=7.5, color="#555555", va="top")
    fig.savefig(destino, facecolor="white")
    plt.close(fig)
    return destino


def hoja_contactos(env, barrios, calles) -> Path:
    TMP.mkdir(parents=True, exist_ok=True)
    cw, ch = 340, 430
    cols, rows = 4, 6
    margen_sup = 120
    sheet = Image.new("RGB", (cols * cw * 2 + 40, rows * ch + margen_sup + 30), "white")
    draw = ImageDraw.Draw(sheet)
    draw.text((24, 26), "AG-2 · Envolventes editoriales V2 — antes / despues",
              fill="#1F3B57", font=fuente(34, True))
    draw.text((24, 72), "Izquierda: mapa vigente del Atlas V1 (PNG rasterizado). "
                        "Derecha: envolvente V2 recortada por linea media. "
                        "Trazo punteado = area de consulta declarada.",
              fill="#555555", font=fuente(19))

    for idx, (_, fila) in enumerate(env.iterrows()):
        col, row = idx % cols, idx // cols
        x0 = 20 + col * cw * 2
        y0 = margen_sup + row * ch

        antes_path = ATLAS_V1_MAPS / MAIN_NAMES[fila.referencia_id]
        antes = Image.open(antes_path).convert("RGB").crop((240, 330, 1360, 1590))
        antes.thumbnail((cw - 12, ch - 40), Image.Resampling.LANCZOS)
        sheet.paste(antes, (x0 + 6, y0 + 30))

        nuevo_path = render_nuevo(fila, barrios, calles, TMP / f"{fila.referencia_id}.png")
        nuevo = Image.open(nuevo_path).convert("RGB")
        nuevo.thumbnail((cw - 12, ch - 40), Image.Resampling.LANCZOS)
        sheet.paste(nuevo, (x0 + cw + 6, y0 + 30))

        draw.rectangle((x0 + 4, y0 + 2, x0 + cw * 2 - 8, y0 + 26), fill="#1F3B57")
        draw.text((x0 + 12, y0 + 6), f"{fila.referencia_id}  {fila.nombre[:34]}",
                  fill="white", font=fuente(16, True))
        draw.rectangle((x0 + 4, y0 + 2, x0 + cw * 2 - 8, y0 + ch - 6),
                       outline="#B8C2CE", width=2)

    destino = QA / "AG2_HOJA_CONTACTOS_ENVOLVENTES_22.png"
    sheet.save(destino, optimize=True)
    return destino


def mapa_general(env, barrios, comunas) -> Path:
    caba = unary_union(list(barrios.geometry))
    fig = plt.figure(figsize=(9.5, 11.5), dpi=150)
    ax = fig.add_axes([0.02, 0.10, 0.96, 0.84])

    comunas.plot(ax=ax, facecolor="#F7F9FB", edgecolor="#DCE3EA", linewidth=0.7, zorder=0)
    gpd.GeoSeries([caba], crs=CRS_M).plot(ax=ax, facecolor="none", edgecolor="#93A3B5",
                                          linewidth=1.6, zorder=2)

    for _, fila in env.iterrows():
        punteado = fila.trazo == "punteado"
        gpd.GeoSeries([fila.geometry], crs=CRS_M).plot(
            ax=ax, facecolor=fila.color, alpha=0.55 if not punteado else 0.35,
            edgecolor=fila.color, linewidth=1.1,
            linestyle=(0, (3, 2)) if punteado else "solid", zorder=6)

    for _, fila in env.iterrows():
        piezas = (list(fila.geometry.geoms) if fila.geometry.geom_type == "MultiPolygon"
                  else [fila.geometry])
        p = max(piezas, key=lambda g: g.area).representative_point()
        ax.annotate(fila.referencia_id[1:], xy=(p.x, p.y), ha="center", va="center",
                    fontsize=7.5, fontweight="bold", color="white", zorder=10,
                    bbox=dict(boxstyle="circle,pad=0.28", fc=fila.color, ec="white", lw=0.9))

    ax.set_aspect("equal")
    ax.axis("off")

    vistos, handles = set(), []
    for _, fila in env.iterrows():
        if fila.familia_etiqueta in vistos:
            continue
        vistos.add(fila.familia_etiqueta)
        handles.append(Patch(facecolor=fila.color, alpha=0.55, edgecolor=fila.color,
                             label=fila.familia_etiqueta))
    handles.append(Line2D([0], [0], color="#555555", lw=1.3, linestyle=(0, (3, 2)),
                          label="trazo punteado: area de consulta declarada,\n"
                                "no envolvente de oferta observada"))
    ax.legend(handles=handles, loc="lower left", fontsize=8.5, frameon=True,
              framealpha=0.95, edgecolor="#D9DEE5", borderpad=0.8)

    fig.text(0.03, 0.975, "AG-3 · Borrador del mapa general de la Ciudad",
             fontsize=17, fontweight="bold", color="#1F3B57", va="top")
    fig.text(0.03, 0.947, "22 referencias gastronomicas · borrador sin tabla lateral ni recuadros de zoom",
             fontsize=9.5, color="#555555", va="top")
    fig.text(0.03, 0.055,
             "Las areas son aproximaciones de lectura territorial: no son limites oficiales, "
             "padron de locales ni recomendacion comercial.\n"
             "Las cifras de cada referencia no se suman entre si ni se ordenan en un ranking general.",
             fontsize=8.5, color="#555555", va="top")

    destino = QA / "AG3_BORRADOR_MAPA_GENERAL.png"
    fig.savefig(destino, facecolor="white")
    plt.close(fig)
    return destino


def main() -> int:
    QA.mkdir(parents=True, exist_ok=True)
    env, barrios, comunas, calles = cargar()
    print("hoja de contactos:", hoja_contactos(env, barrios, calles))
    print("mapa general     :", mapa_general(env, barrios, comunas))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
