"""El borrador de polos, dibujado. BORRADOR — no se publica ni entra a ningún informe.

Cuatro láminas, porque las preguntas no se contestan en la misma imagen:

  1. `borrador_polos_ciudad.png` — los polos del borrador sobre los 48 barrios, con los puntos
     dispersos de fondo. Es el mapa que responde «¿dónde hay polos?» y, sobre todo, el que hace
     visible el 43 % de locales que no está en ninguno.
  2. `borrador_vs_22_zonas.png` — el borrador contra las 22 envolventes publicadas. Es el que
     responde «¿qué encontró y qué no?»: se ven las zonas del Atlas que el clustering no dibuja y
     los polos que el Atlas no tiene.
  3. `borrador_polos_clase_densidad.png` — los polos coloreados por su clase de densidad. Es la
     lámina que impide leer el mapa como si todas las manchas fueran la misma cosa: sin ella, un
     polo de 1 local/ha y uno de 15 se dibujan idénticos.
  4. `borrador_polos_anada.png` — los polos por añada del Relevamiento de Usos del Suelo de su
     barrio. El Relevamiento es rotativo y sostiene el mapa, así que qué año sostiene a cada polo
     es parte de lo que hay que ver, no una nota al pie.

DOS COSAS VAN ADENTRO DE LA IMAGEN, NO EN EL HANDOFF NI EN EL NOMBRE DEL ARCHIVO:
  · el rótulo BORRADOR, porque un PNG sin rótulo se separa de su carpeta la primera vez que
    alguien lo pega en una presentación;
  · **la advertencia de la añada rotativa**, porque el mapa depende de una fuente que midió cada
    barrio en un año distinto y esa advertencia tiene que viajar pegada al dibujo.

Uso:
  .venv/Scripts/python.exe scripts/barrido_ciudad/mapa_borrador_polos.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

BARRIDO = ROOT / "outputs" / "BARRIDO_CIUDAD_2026-08"
OUT = BARRIDO / "borrador_polos"
POLOS = OUT / "borrador_polos_v3.geojson"
POLOS_V1 = OUT / "borrador_polos.geojson"
PERTENENCIA = OUT / "pertenencia_local_polo_v3.csv"
BASE = BARRIDO / "base" / "local.csv"
BARRIOS = ROOT / "data" / "raw" / "geo_barrios.geojson"
ZONAS_22 = ROOT / "outputs" / "polos_gastro" / "ATLAS_V2" / "capas" / "envolventes_editoriales_v2.geojson"

CRS_METRICO = "EPSG:5347"
COLORES = {
    "fondo": "#FFFFFF", "barrio": "#EDF0F2", "borde": "#C7CFD5",
    "polo": "#16845B", "polo_borde": "#0E5C40",
    "zona22": "#B34A3C", "disperso": "#9AA6AE", "texto": "#153E5C",
}
# De más denso a menos: una rampa de un solo tono, para que la clase se lea como un orden y no
# como tres categorías sin relación entre sí. La clase ES un orden.
COLOR_CLASE = {
    "concentración": "#16845B",
    "concentración extendida": "#A8D8BF",
}
# Tres años distintos, tres colores sin orden: la añada NO es una escala. 2022 no es «menos» que
# 2024, es otro momento de medición. Una rampa acá sugeriría una gradación que no existe.
COLOR_ANADA = {2022: "#C1666B", 2023: "#E0A458", 2024: "#4A7C9B"}

NOTA = ("BORRADOR · no publicado · oferta registrada en siete fuentes abiertas · "
        "no es límite administrativo oficial")
# Esta advertencia va adentro de todas las láminas, sin excepción. El mapa se apoya en una fuente
# que midió cada barrio en un año distinto, y sin esto dos polos de años distintos se leen como
# si fueran comparables.
LIMITACION_DENOMINADOR = (
    "LÍMITE DECLARADO · no existe ni va a existir un denominador externo de completitud contra el "
    "cual contrastar esta base.\nLa parejidad de cobertura se apoya sólo en dos proxies internos. "
    "Con los indicadores disponibles la cobertura es pareja; no está verificada contra un tercero.")
ADVERTENCIA_ANADA = (
    "ADVERTENCIA · el Relevamiento de Usos del Suelo sostiene este mapa y es ROTATIVO: relevó cada "
    "barrio en un año distinto (2022 / 2023 / 2024).\nDos polos de añadas distintas no son "
    "comparables entre sí. La añada de cada polo está en borrador_polos_v3.csv.")


def cargar():
    polos = gpd.read_file(POLOS).to_crs(CRS_METRICO)
    barrios = gpd.read_file(BARRIOS).to_crs(CRS_METRICO)
    zonas = gpd.read_file(ZONAS_22).to_crs(CRS_METRICO)
    base = pd.read_csv(BASE, low_memory=False)
    pertenencia = pd.read_csv(PERTENENCIA)
    # `polo_unido` es la pertenencia FINAL: después de partir y después de unir. Usar `polo_final`
    # dibujaría como dispersos a los locales que la unión volvió a meter en un polo.
    sin_polo = pertenencia.polo_unido.isna() | (pertenencia.polo_unido == "")
    dispersos = base[base.local_id.isin(pertenencia.loc[sin_polo, "local_id"])]
    dispersos = gpd.GeoDataFrame(
        dispersos, geometry=gpd.points_from_xy(dispersos.lon, dispersos.lat),
        crs="EPSG:4326").to_crs(CRS_METRICO)
    return polos, barrios, zonas, dispersos


def marco(ax, barrios, titulo, subtitulo):
    barrios.plot(ax=ax, facecolor=COLORES["barrio"], edgecolor=COLORES["borde"], linewidth=0.5)
    ax.set_axis_off()
    ax.set_title(titulo, fontsize=15, color=COLORES["texto"], loc="left", pad=14, weight="bold")
    ax.text(0, 1.008, subtitulo, transform=ax.transAxes, fontsize=9.5,
            color=COLORES["texto"], va="bottom")
    ax.text(0, -0.02, NOTA, transform=ax.transAxes, fontsize=7.5, color=COLORES["disperso"])
    # La advertencia de la añada va en TODAS las láminas y con caja propia, para que no se lea
    # como parte del pie de página ni se pierda al recortar la imagen.
    ax.text(0, -0.055, ADVERTENCIA_ANADA, transform=ax.transAxes, fontsize=7.5,
            color="#8A4B1F", va="top",
            bbox=dict(boxstyle="round,pad=0.45", fc="#FDF3E7", ec="#E0A458", linewidth=0.8))
    ax.text(0, -0.105, LIMITACION_DENOMINADOR, transform=ax.transAxes, fontsize=7.5,
            color="#4A4A6A", va="top",
            bbox=dict(boxstyle="round,pad=0.45", fc="#F2F2F7", ec="#9A9AB5", linewidth=0.8))


def lamina_polos(polos, barrios, dispersos, ruta: Path):
    fig, ax = plt.subplots(figsize=(13, 13), dpi=200)
    marco(ax, barrios,
          f"Borrador · {len(polos)} polos gastronómicos en toda la Ciudad",
          "un solo juego de parámetros para los 48 barrios · anillo núcleo · sólo puntos aptos")
    dispersos.plot(ax=ax, color=COLORES["disperso"], markersize=1.2, alpha=0.45, zorder=2)
    polos.plot(ax=ax, facecolor=COLORES["polo"], edgecolor=COLORES["polo_borde"],
               alpha=0.55, linewidth=0.7, zorder=3)
    ax.legend(handles=[
        Patch(facecolor=COLORES["polo"], alpha=0.55, edgecolor=COLORES["polo_borde"],
              label=f"polo del borrador ({len(polos)})"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=COLORES["disperso"],
               markersize=5, label=f"local fuera de todo polo ({len(dispersos):,})"),
    ], loc="lower right", frameon=False, fontsize=9)
    fig.savefig(ruta, bbox_inches="tight", facecolor=COLORES["fondo"])
    plt.close(fig)


def lamina_cotejo(polos, barrios, zonas, ruta: Path):
    fig, ax = plt.subplots(figsize=(13, 13), dpi=200)
    marco(ax, barrios,
          "Borrador contra las 22 zonas publicadas del Atlas",
          "en rojo lo publicado, en verde lo que dibuja el clustering desde la base")
    polos.plot(ax=ax, facecolor=COLORES["polo"], edgecolor="none", alpha=0.5, zorder=3)
    zonas.plot(ax=ax, facecolor="none", edgecolor=COLORES["zona22"], linewidth=1.4, zorder=4)
    for zona in zonas.itertuples():
        punto = zona.geometry.representative_point()
        ax.annotate(zona.referencia_id, (punto.x, punto.y), fontsize=6.5,
                    color=COLORES["zona22"], ha="center", va="center", zorder=5,
                    bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.8))
    ax.legend(handles=[
        Patch(facecolor=COLORES["polo"], alpha=0.5, edgecolor="none",
              label=f"polo del borrador ({len(polos)})"),
        Patch(facecolor="none", edgecolor=COLORES["zona22"], linewidth=1.4,
              label=f"zona publicada del Atlas ({len(zonas)})"),
    ], loc="lower right", frameon=False, fontsize=9)
    fig.savefig(ruta, bbox_inches="tight", facecolor=COLORES["fondo"])
    plt.close(fig)


def lamina_clase_densidad(polos, barrios, ruta: Path):
    """La lámina que impide leer todas las manchas como si fueran la misma cosa.

    Sin ella el mapa dibuja con la misma nitidez un polo de 1 local/ha y uno de 15, que es
    exactamente el problema que la clase de densidad viene a resolver. El color hace visible en
    el dibujo lo que la tabla ya dice en una columna.
    """
    fig, ax = plt.subplots(figsize=(13, 13), dpi=200)
    marco(ax, barrios,
          f"Borrador · {len(polos)} polos por clase de densidad",
          "la densidad es atributo, no compuerta · dos clases: la frontera densa/media no era reproducible")
    manejadores = []
    for clase, color in COLOR_CLASE.items():
        subconjunto = polos[polos.clase_densidad == clase]
        if not len(subconjunto):
            continue
        subconjunto.plot(ax=ax, facecolor=color, edgecolor=COLORES["polo_borde"],
                         linewidth=0.5, alpha=0.85, zorder=3)
        manejadores.append(Patch(
            facecolor=color, edgecolor=COLORES["polo_borde"],
            label=f"{clase} — {len(subconjunto)} polos, "
                  f"{subconjunto.locales_x_ha.min():.1f}–{subconjunto.locales_x_ha.max():.1f} loc/ha"))
    ax.legend(handles=manejadores, loc="lower right", frameon=False, fontsize=8.5)
    ax.text(0.0, 0.02,
            "El corte es ÓPTIMO, no natural: la distribución de densidad es continua y no tiene\n"
            "huecos. Se publican DOS clases y no tres porque la frontera densa/media no resistió la\n"
            "prueba de robustez —conservaba 2 de 26 polos—; ésta conserva el 95 %.\n"
            "La densidad exacta de cada polo está en borrador_polos_v3.csv y se lee ANTES que la clase.",
            transform=ax.transAxes, fontsize=7.5, color=COLORES["texto"], va="bottom")
    fig.savefig(ruta, bbox_inches="tight", facecolor=COLORES["fondo"])
    plt.close(fig)


def lamina_anada(polos, barrios, ruta: Path):
    """Qué año del Relevamiento sostiene a cada polo, dibujado."""
    fig, ax = plt.subplots(figsize=(13, 13), dpi=200)
    marco(ax, barrios,
          "Borrador · qué año del Relevamiento sostiene a cada polo",
          "la fuente es rotativa y su año NO está repartido al azar: es un gradiente geográfico")
    manejadores = []
    for anio, color in COLOR_ANADA.items():
        subconjunto = polos[polos.anada_relevamiento == anio]
        if not len(subconjunto):
            continue
        subconjunto.plot(ax=ax, facecolor=color, edgecolor="white", linewidth=0.4,
                         alpha=0.9, zorder=3)
        manejadores.append(Patch(facecolor=color, edgecolor="white",
                                 label=f"relevado en {anio} — {len(subconjunto)} polos, "
                                       f"{int(subconjunto.locales.sum()):,} locales"))
    mixtos = polos[polos.anada_mixta.fillna(False).astype(bool)]
    mixtos.plot(ax=ax, facecolor="none", edgecolor="#3B3B3B", linewidth=1.1, hatch="///",
                zorder=4)
    manejadores.append(Patch(facecolor="none", edgecolor="#3B3B3B", hatch="///",
                             label=f"añada mixta: abarca barrios de años distintos ({len(mixtos)})"))
    ax.legend(handles=manejadores, loc="lower right", frameon=False, fontsize=8.5)
    fig.savefig(ruta, bbox_inches="tight", facecolor=COLORES["fondo"])
    plt.close(fig)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if not POLOS.exists():
        print(f"falta {POLOS.name} — correr antes polos_atributos_clases.py")
        return 1
    polos, barrios, zonas, dispersos = cargar()
    laminas = {
        "borrador_polos_ciudad.png": lambda r: lamina_polos(polos, barrios, dispersos, r),
        "borrador_vs_22_zonas.png": lambda r: lamina_cotejo(polos, barrios, zonas, r),
        "borrador_polos_clase_densidad.png": lambda r: lamina_clase_densidad(polos, barrios, r),
        "borrador_polos_anada.png": lambda r: lamina_anada(polos, barrios, r),
    }
    for nombre, dibujar in laminas.items():
        dibujar(OUT / nombre)
    print(f"escrito en {OUT.relative_to(ROOT)}: {', '.join(laminas)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
