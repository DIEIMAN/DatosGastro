# -*- coding: utf-8 -*-
"""Experimento v2: poligonos exploratorios PolosGastro (capa auxiliar estimada).

Segunda tanda del experimento de clustering. Dos estrategias complementarias:

A. DBSCAN global con grilla ampliada y 3 configuraciones candidatas
   (estricta / equilibrada / inclusiva), en lugar de una sola.
B. Poligonizacion asistida por etiquetas de polo/subzona existentes en el input
   ("poligonos exploratorios asistidos por subzona"): no es clustering puro,
   usa las zonas editoriales conocidas para agrupar los puntos semilla.

Todos los resultados son EXPLORATORIOS/AUXILIARES/ESTIMADOS: no constituyen
limites oficiales y requieren revision territorial. No modifica el experimento
v1 ni el informe vigente; escribe solo en carpetas *_v2.

Uso:
    .venv/Scripts/python.exe scripts/polos_gastro/historico/experimentos/generar_poligonos_clustering_v2.py
    [--input CSV] [--outdir DIR] [--solo-grilla]
"""

import argparse
import sys
from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shapely
from matplotlib.lines import Line2D
from scipy.spatial.distance import pdist
from shapely.geometry import LineString, MultiPoint

try:
    from sklearn.cluster import DBSCAN
except ImportError:
    sys.exit("Falta scikit-learn en .venv. No se improvisa un algoritmo alternativo.")

REPO = Path(__file__).resolve().parents[3]

INPUT_DEFAULT = REPO / "outputs/polos_gastro/fase13_mapas/tablas/locales_para_mapa_revision.csv"
OUTDIR_DEFAULT = REPO / "outputs/polos_gastro/historico/experimentos_clustering_v2"
BARRIOS_GEOJSON = REPO / "PolosGastro/cartografia/barrios_caba.geojson"
COMUNAS_GEOJSON = REPO / "PolosGastro/cartografia/comunas_caba.geojson"

CRS_GEO = "EPSG:4326"
CRS_METRICO = "EPSG:5347"  # POSGAR 2007 / Argentina faja 5

EPS_GRILLA = [150, 200, 250, 300, 400, 500, 650, 800, 1000]
MIN_SAMPLES_GRILLA = [2, 3, 4, 5, 6]

# Candidatas elegidas tras inspeccionar parametros_probados_dbscan_v2.csv
# (criterio en DIAGNOSTICO_RUIDO_DBSCAN.md y QA v2; no solo por menor ruido:
# eps grandes que fusionan zonas distantes se descartan aunque bajen el ruido).
CANDIDATAS_DBSCAN = {
    # estricta: exige mas evidencia por cluster (ms=4); menos clusters, mas ruido, mas puros.
    "estricto": (500, 4),
    # equilibrada: la elegida en v1; mantiene comparabilidad entre tandas.
    "equilibrado": (400, 3),
    # inclusiva: hallazgo de la grilla ampliada; baja el ruido a 29 % sin bandera de
    # fusion (diametro max 2.3 km ~ macrozona Palermo). No se eligio ms=2 (pares como
    # clusters = evidencia debil) ni eps>=800 (fusiona zonas distantes aunque baje el ruido).
    "inclusivo": (650, 4),
}
CANDIDATA_PARA_POLIGONOS = "equilibrado"

BUFFER_HULL_M = 40      # ensancha hulls para no dejar poligonos lineales
BUFFER_CAPSULA_M = 60   # grupos de 2 puntos: capsula prudente
BUFFER_PUNTUAL_M = 80   # grupos de 1 punto: buffer chico, baja confiabilidad
DIST_APARTADO_MIN_M = 1500  # depuracion intra-grupo de sedes apartadas

NOTA_POLIGONO = "Poligono exploratorio auxiliar. No constituye limite oficial."
NOTA_MAPA = (
    "Capa auxiliar exploratoria. No constituye limite oficial. Requiere revision territorial."
)

# Paleta categorica validada (dataviz skill, modo claro) + etiquetas directas.
PALETA = ["#2a78d6", "#1baf7a", "#eda100", "#008300", "#4a3aa7", "#e34948", "#e87ba4", "#eb6834"]
# Confianza (ordinal) -> rampa secuencial de un solo tono (azul), claro -> oscuro.
COLOR_CONFIANZA = {"baja": "#b7d3f6", "media": "#6da7ec", "alta": "#1c5cab"}
COLOR_RUIDO = "#898781"
COLOR_BARRIOS = "#f0efec"
COLOR_TEXTO = "#0b0b0b"
COLOR_TEXTO_SEC = "#52514e"


def limpiar_texto(s):
    """El CSV de Fase 13 trae un U+FFFD literal en 'Las Ca?itas' (defecto del
    archivo fuente, que no se modifica). Se sanea solo para mostrar."""
    return str(s).replace("�", "ñ")


def color_cluster(cid: int) -> str:
    return PALETA[cid % len(PALETA)]


# ----------------------------------------------------------------------------
# Carga y validacion (mismos criterios que v1)
# ----------------------------------------------------------------------------

def cargar_puntos(path_input: Path):
    df = pd.read_csv(path_input)
    qa = {"puntos_cargados": len(df), "descartes": []}

    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
    sin_coord = df["lat"].isna() | df["lon"].isna()
    if sin_coord.any():
        qa["descartes"].append(("sin coordenadas numericas", int(sin_coord.sum())))
    df = df[~sin_coord].copy()

    if "estado_consolidado" in df.columns:
        dup = df["estado_consolidado"].eq("duplicado_probable")
        if dup.any():
            qa["descartes"].append(("estado_consolidado=duplicado_probable", int(dup.sum())))
        df = df[~dup].copy()

    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df["lon"], df["lat"]), crs=CRS_GEO)
    limite_caba = gpd.read_file(COMUNAS_GEOJSON).to_crs(CRS_GEO).union_all()
    fuera = ~gdf.geometry.within(limite_caba)
    if fuera.any():
        qa["descartes"].append(("fuera del limite de CABA", int(fuera.sum())))
    gdf = gdf[~fuera].copy()

    qa["puntos_validos"] = len(gdf)
    return gdf.to_crs(CRS_METRICO), qa


# ----------------------------------------------------------------------------
# Estrategia A: DBSCAN global, grilla ampliada
# ----------------------------------------------------------------------------

def diametro_maximo(xy: np.ndarray, labels: np.ndarray) -> float:
    """Diametro (max distancia interna, en m) del cluster mas extendido."""
    dmax = 0.0
    for cid in set(labels):
        if cid == -1:
            continue
        pts = xy[labels == cid]
        if len(pts) >= 2:
            dmax = max(dmax, float(pdist(pts).max()))
    return round(dmax, 0)


def observacion_config(n_clusters, pct_ruido, tam_max, muy_chicos, diam_max, n_puntos):
    flags = []
    if n_clusters == 0:
        return "sin estructura (todo ruido)"
    if tam_max > 0.4 * n_puntos:
        flags.append(f"posible fusion: cluster dominante de {tam_max} pts")
    if diam_max > 2500:
        flags.append(f"fusiona zonas distantes (diametro max {int(diam_max)} m)")
    if pct_ruido > 65:
        flags.append("ruido dominante")
    if n_clusters and muy_chicos > n_clusters / 2:
        flags.append("fragmentacion en pares/miniclusters")
    return "; ".join(flags) if flags else "estructura razonable"


def correr_grilla(xy: np.ndarray, gdf) -> pd.DataFrame:
    filas = []
    n = len(xy)
    for eps in EPS_GRILLA:
        for ms in MIN_SAMPLES_GRILLA:
            labels = DBSCAN(eps=eps, min_samples=ms).fit(xy).labels_
            tam = pd.Series(labels[labels >= 0]).value_counts()
            n_ruido = int((labels == -1).sum())
            n_clusters = int(tam.shape[0])
            tam_max = int(tam.max()) if n_clusters else 0
            muy_chicos = int((tam < 3).sum())
            diam = diametro_maximo(xy, labels)
            filas.append(
                {
                    "eps_m": eps,
                    "min_samples": ms,
                    "cantidad_clusters": n_clusters,
                    "puntos_ruido": n_ruido,
                    "porcentaje_ruido": round(100.0 * n_ruido / n, 1),
                    "tamanio_min_cluster": int(tam.min()) if n_clusters else 0,
                    "tamanio_max_cluster": tam_max,
                    "tamanio_mediano_cluster": float(tam.median()) if n_clusters else 0.0,
                    "clusters_muy_chicos": muy_chicos,
                    "diametro_max_m": diam,
                    "observacion": observacion_config(
                        n_clusters, 100.0 * n_ruido / n, tam_max, muy_chicos, diam, n
                    ),
                }
            )
    return pd.DataFrame(filas)


def hull_con_buffer(geoms):
    """Hull de un conjunto de puntos (>=3): concave si es valido, si no convex.

    En grupos dispersos (diametro > 2500 m) se usa convex hull: el concave con
    ratio fijo genera puas largas y finas que sugieren una forma que los datos
    no respaldan; el convexo muestra de manera transparente que el grupo es
    extendido."""
    mp = MultiPoint(list(geoms))
    metodo = "convex_hull"
    hull = mp.convex_hull
    coords = np.array([(g.x, g.y) for g in mp.geoms])
    diam = float(pdist(coords).max()) if len(coords) >= 2 else 0.0
    if hasattr(shapely, "concave_hull") and len(mp.geoms) >= 4 and diam <= 2500:
        cand = shapely.concave_hull(mp, ratio=0.5, allow_holes=False)
        if cand is not None and not cand.is_empty and cand.is_valid and cand.area > 0:
            hull, metodo = cand, "concave_hull(ratio=0.5)"
    return hull.buffer(BUFFER_HULL_M), f"{metodo}+buffer{BUFFER_HULL_M}m"


def poligonos_dbscan(gdf, labels, eps, ms):
    filas = []
    for cid in sorted({c for c in labels if c >= 0}):
        sub = gdf[labels == cid]
        if len(sub) >= 3:
            poli, metodo = hull_con_buffer(sub.geometry)
        else:  # min_samples=2 puede dejar clusters de 2 puntos
            poli = LineString([(g.x, g.y) for g in sub.geometry]).buffer(BUFFER_CAPSULA_M)
            metodo = f"capsula_2pts+buffer{BUFFER_CAPSULA_M}m"
        vc = sub["polo"].value_counts()
        filas.append(
            {
                "cluster_id": int(cid),
                "n_puntos": len(sub),
                "algoritmo": f"DBSCAN(eps={eps},min_samples={ms}) + {metodo}",
                "eps_m": eps,
                "min_samples": ms,
                "area_m2": round(poli.area, 1),
                "area_ha": round(poli.area / 10_000.0, 2),
                "polo_mayoritario": vc.index[0],
                "porcentaje_polo_mayoritario": round(100.0 * vc.iloc[0] / len(sub), 1),
                "distribucion_polos": "; ".join(f"{p}: {n}" for p, n in vc.items()),
                "nota": NOTA_POLIGONO,
                "geometry": poli,
            }
        )
    return gpd.GeoDataFrame(filas, crs=CRS_METRICO)


# ----------------------------------------------------------------------------
# Estrategia B: poligonizacion asistida por polo/subzona
# ----------------------------------------------------------------------------

def confianza_por_n(n: int) -> str:
    if n >= 5:
        return "alta"
    if n >= 3:
        return "media"
    return "baja"


def depurar_apartados(sub):
    """Excluye del hull los puntos apartados de su propio grupo (sedes/sucursales
    geocodificadas lejos de su zona). Umbral: max(1500 m, 3 x distancia mediana
    al centro mediano del grupo). Solo se aplica con n >= 3."""
    if len(sub) < 3:
        return sub, sub.iloc[0:0]
    cx, cy = sub.geometry.x.median(), sub.geometry.y.median()
    dist = np.hypot(sub.geometry.x - cx, sub.geometry.y - cy)
    umbral = max(DIST_APARTADO_MIN_M, 3.0 * float(dist.median()))
    lejos = dist > umbral
    return sub[~lejos], sub[lejos]


def poligonos_asistidos(gdf):
    gdf = gdf.copy()
    gdf["subzona_efectiva"] = gdf["subzona"].fillna("").astype(str).str.strip()
    gdf.loc[gdf["subzona_efectiva"] == "", "subzona_efectiva"] = gdf["polo"]

    polos_multigrupo = (
        gdf.groupby("polo")["subzona_efectiva"].nunique().loc[lambda s: s > 1].index
    )
    filas, apartados_idx = [], []
    for i, ((polo, subzona), sub) in enumerate(
        sorted(gdf.groupby(["polo", "subzona_efectiva"]), key=lambda kv: kv[0])
    ):
        usados, apartados = depurar_apartados(sub)
        apartados_idx.extend(apartados.index.tolist())
        n = len(usados)
        if n >= 3:
            poli, metodo = hull_con_buffer(usados.geometry)
        elif n == 2:
            poli = LineString([(g.x, g.y) for g in usados.geometry]).buffer(BUFFER_CAPSULA_M)
            metodo = f"capsula_2pts+buffer{BUFFER_CAPSULA_M}m"
        else:
            poli = usados.geometry.iloc[0].buffer(BUFFER_PUNTUAL_M)
            metodo = f"buffer_puntual_{BUFFER_PUNTUAL_M}m (baja confiabilidad)"
        etiqueta = limpiar_texto(polo)
        if polo in polos_multigrupo:
            subzona_corta = limpiar_texto(subzona).split(";")[0].strip()
            etiqueta = f"{limpiar_texto(polo)} - {subzona_corta}"
        filas.append(
            {
                "zona_id": f"Z{i:02d}",
                "polo": polo,
                "subzona": subzona,
                "etiqueta": etiqueta,
                "n_puntos": n,
                "n_apartados_excluidos": len(apartados),
                "metodo": metodo,
                "area_m2": round(poli.area, 1),
                "area_ha": round(poli.area / 10_000.0, 2),
                "confianza": confianza_por_n(n),
                # Hull mucho mas grande que un nucleo barrial (~4 km2): el grupo es
                # disperso o arrastra sedes dudosas; el poligono no es interpretable
                # como area de concentracion sin revision humana.
                "extension_a_revisar": bool(poli.area / 10_000.0 > 400),
                "nota": NOTA_POLIGONO,
                "geometry": poli,
            }
        )
    return gpd.GeoDataFrame(filas, crs=CRS_METRICO), gdf.loc[apartados_idx]


# ----------------------------------------------------------------------------
# Mapas
# ----------------------------------------------------------------------------

def dibujar_base(ax):
    barrios = gpd.read_file(BARRIOS_GEOJSON).to_crs(CRS_METRICO)
    barrios.plot(ax=ax, color=COLOR_BARRIOS, edgecolor="#ffffff", linewidth=0.6)
    ax.set_axis_off()


def pie_de_mapa(fig, fuente_input):
    fig.text(0.5, 0.035, NOTA_MAPA, ha="center", fontsize=9.5, color=COLOR_TEXTO, weight="bold")
    fig.text(
        0.5, 0.015,
        f"Fuente de puntos: {fuente_input} (universo semilla, no censo). DGDGAS - uso interno.",
        ha="center", fontsize=7.5, color=COLOR_TEXTO_SEC,
    )


OFFSETS_ETIQUETA = [(9, 9), (9, -18), (-9, 9), (-9, -18)]  # alterna para reducir choques


def etiqueta_halo(ax, x, y, texto, fontsize=9.5, orden=0):
    dx, dy = OFFSETS_ETIQUETA[orden % len(OFFSETS_ETIQUETA)]
    ax.annotate(
        texto, (x, y), xytext=(dx, dy), textcoords="offset points", fontsize=fontsize,
        weight="bold", color=COLOR_TEXTO, ha="left" if dx > 0 else "right",
        va="bottom" if dy > 0 else "top", zorder=7,
        path_effects=[pe.withStroke(linewidth=2.5, foreground="white")],
    )


def mapa_dbscan(gdf, labels, nombre, eps, ms, fuente_input, path_png):
    fig, ax = plt.subplots(figsize=(10.5, 12))
    dibujar_base(ax)
    ruido = gdf[labels == -1]
    if len(ruido):
        ax.scatter(ruido.geometry.x, ruido.geometry.y, c=COLOR_RUIDO, marker="x", s=30,
                   linewidths=1.2, zorder=3)
    for cid in sorted({c for c in labels if c >= 0}):
        sub = gdf[labels == cid]
        ax.scatter(sub.geometry.x, sub.geometry.y, c=color_cluster(cid), s=36,
                   edgecolors="white", linewidths=0.6, zorder=4)
        cx, cy = sub.geometry.x.mean(), sub.geometry.y.mean()
        etiqueta_halo(ax, cx, cy, f"C{cid}")
    pct = 100.0 * (labels == -1).sum() / len(gdf)
    ax.set_title(
        f"EXPERIMENTAL - DBSCAN candidata '{nombre}' (eps={eps} m, min_samples={ms})\n"
        f"{int((labels >= 0).sum())} pts en {len(set(labels)) - (1 if -1 in labels else 0)} "
        f"clusters, ruido {pct:.1f} % - universo semilla PolosGastro",
        fontsize=12, color=COLOR_TEXTO,
    )
    leyenda = [
        Line2D([], [], marker="o", linestyle="", markerfacecolor=PALETA[0],
               markeredgecolor="white", markersize=8, label="Punto en cluster (color por cluster)"),
        Line2D([], [], marker="x", linestyle="", color=COLOR_RUIDO, markersize=8,
               label="Ruido / outlier (sin cluster)"),
    ]
    ax.legend(handles=leyenda, loc="upper left", fontsize=8, frameon=True)
    pie_de_mapa(fig, fuente_input)
    fig.savefig(path_png, dpi=150, bbox_inches="tight")
    plt.close(fig)


def mapa_asistido(gdf_zonas, gdf_apartados, fuente_input, path_png):
    fig, ax = plt.subplots(figsize=(10.5, 12))
    dibujar_base(ax)
    for orden, (_, r) in enumerate(gdf_zonas.iterrows()):
        col = COLOR_CONFIANZA[r["confianza"]]
        borde = "#d03b3b" if r["extension_a_revisar"] else "#104281"
        estilo = (0, (4, 3)) if r["extension_a_revisar"] else "solid"
        gpd.GeoSeries([r.geometry], crs=CRS_METRICO).plot(
            ax=ax, color=col, alpha=0.55, edgecolor=borde, linewidth=1.4,
            linestyle=estilo, zorder=3
        )
        c = r.geometry.centroid
        etiqueta_halo(ax, c.x, c.y, r["etiqueta"], fontsize=8.5, orden=orden)
    if len(gdf_apartados):
        ax.scatter(gdf_apartados.geometry.x, gdf_apartados.geometry.y, c=COLOR_RUIDO,
                   marker="x", s=30, linewidths=1.2, zorder=4)
    ax.set_title(
        "EXPERIMENTAL - Poligonos exploratorios asistidos por subzona (capa auxiliar estimada)\n"
        "Agrupamiento por polo/subzona editorial + hull prudente por grupo",
        fontsize=12, color=COLOR_TEXTO,
    )
    leyenda = [
        Line2D([], [], marker="s", linestyle="", markerfacecolor=COLOR_CONFIANZA["alta"],
               markersize=9, label="Confianza alta (>= 5 puntos)"),
        Line2D([], [], marker="s", linestyle="", markerfacecolor=COLOR_CONFIANZA["media"],
               markersize=9, label="Confianza media (3-4 puntos)"),
        Line2D([], [], marker="s", linestyle="", markerfacecolor=COLOR_CONFIANZA["baja"],
               markersize=9, label="Confianza baja (1-2 puntos)"),
        Line2D([], [], marker="x", linestyle="", color=COLOR_RUIDO, markersize=8,
               label="Punto apartado de su zona (excluido del hull)"),
        Line2D([], [], linestyle=(0, (4, 3)), color="#d03b3b", linewidth=1.6,
               label="Borde rojo: extension a revisar (grupo disperso)"),
    ]
    ax.legend(handles=leyenda, loc="upper left", fontsize=8, frameon=True)
    pie_de_mapa(fig, fuente_input)
    fig.savefig(path_png, dpi=150, bbox_inches="tight")
    plt.close(fig)


def mapa_comparativo(gdf, gdf_dbscan, gdf_zonas, eps, ms, fuente_input, path_png):
    fig, ax = plt.subplots(figsize=(10.5, 12))
    dibujar_base(ax)
    # Capa 1: poligonos asistidos (contorno naranja discontinuo, sin relleno).
    # Los marcados extension_a_revisar van tenues: no son interpretables sin revision.
    ok = gdf_zonas[~gdf_zonas["extension_a_revisar"]]
    dudosos = gdf_zonas[gdf_zonas["extension_a_revisar"]]
    ok.boundary.plot(ax=ax, color="#d95926", linewidth=1.7, linestyle="--", zorder=4)
    if len(dudosos):
        dudosos.boundary.plot(ax=ax, color="#efb5a0", linewidth=1.0, linestyle="--", zorder=3)
    # Capa 2: poligonos DBSCAN candidata elegida (relleno azul).
    for _, r in gdf_dbscan.iterrows():
        gpd.GeoSeries([r.geometry], crs=CRS_METRICO).plot(
            ax=ax, color="#2a78d6", alpha=0.40, edgecolor="#1c5cab", linewidth=1.4, zorder=3
        )
    ax.scatter(gdf.geometry.x, gdf.geometry.y, c=COLOR_TEXTO_SEC, s=8, zorder=5)
    for orden, (_, r) in enumerate(gdf_zonas.iterrows()):
        c = r.geometry.centroid
        etiqueta_halo(ax, c.x, c.y, r["etiqueta"], fontsize=7.5, orden=orden)
    ax.set_title(
        "EXPERIMENTAL - Comparativo: DBSCAN global vs poligonos asistidos por subzona\n"
        f"Relleno azul: DBSCAN '{CANDIDATA_PARA_POLIGONOS}' (eps={eps} m, ms={ms}). "
        "Contorno naranja: capa auxiliar por subzona.",
        fontsize=11.5, color=COLOR_TEXTO,
    )
    leyenda = [
        Line2D([], [], marker="s", linestyle="", markerfacecolor="#2a78d6", alpha=0.5,
               markeredgecolor="#1c5cab", markersize=9,
               label="Poligono DBSCAN (concentracion emergente)"),
        Line2D([], [], linestyle="--", color="#d95926", linewidth=1.7,
               label="Poligono asistido por subzona (zona editorial)"),
        Line2D([], [], linestyle="--", color="#efb5a0", linewidth=1.0,
               label="Asistido con extension a revisar (grupo disperso)"),
        Line2D([], [], marker="o", linestyle="", color=COLOR_TEXTO_SEC, markersize=5,
               label="Punto semilla"),
    ]
    ax.legend(handles=leyenda, loc="upper left", fontsize=8, frameon=True)
    pie_de_mapa(fig, fuente_input)
    fig.savefig(path_png, dpi=150, bbox_inches="tight")
    plt.close(fig)


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=INPUT_DEFAULT)
    parser.add_argument("--outdir", type=Path, default=OUTDIR_DEFAULT)
    parser.add_argument("--solo-grilla", action="store_true",
                        help="Solo genera la tabla de la grilla DBSCAN y termina")
    args = parser.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)
    fuente_input = str(args.input.relative_to(REPO)) if args.input.is_absolute() else str(args.input)

    gdf, qa = cargar_puntos(args.input)
    xy = np.column_stack([gdf.geometry.x, gdf.geometry.y])

    print("=" * 72)
    print("EXPERIMENTO CLUSTERING V2 - RESUMEN (capa auxiliar exploratoria)")
    print("=" * 72)
    print(f"input: {fuente_input}")
    print(f"puntos cargados: {qa['puntos_cargados']} | validos: {qa['puntos_validos']}")
    for motivo, n in qa["descartes"]:
        print(f"  descartados ({motivo}): {n}")

    # --- A. Grilla DBSCAN ampliada ---
    tabla = correr_grilla(xy, gdf)
    tabla.to_csv(args.outdir / "parametros_probados_dbscan_v2.csv", index=False)
    print(f"\nGrilla DBSCAN: {len(tabla)} configuraciones -> parametros_probados_dbscan_v2.csv")
    if args.solo_grilla:
        print(tabla.to_string(index=False))
        return

    gdf_dbscan_eq = None
    for nombre, (eps, ms) in CANDIDATAS_DBSCAN.items():
        labels = DBSCAN(eps=eps, min_samples=ms).fit(xy).labels_
        mapa_dbscan(gdf, labels, nombre, eps, ms, fuente_input,
                    args.outdir / f"mapa_clusters_dbscan_{nombre}.png")
        n_cl = len({c for c in labels if c >= 0})
        n_ru = int((labels == -1).sum())
        print(f"candidata '{nombre}' (eps={eps}, ms={ms}): {n_cl} clusters, "
              f"ruido {n_ru} ({100.0 * n_ru / len(gdf):.1f} %)")
        if nombre == CANDIDATA_PARA_POLIGONOS:
            gdf_dbscan_eq = poligonos_dbscan(gdf, labels, eps, ms)
            gdf_dbscan_eq.to_crs(CRS_GEO).to_file(
                args.outdir / "poligonos_dbscan_equilibrado.geojson", driver="GeoJSON"
            )
            labels_eq = labels

    # --- B. Poligonos asistidos por subzona ---
    gdf_zonas, gdf_apartados = poligonos_asistidos(gdf)
    gdf_zonas.to_crs(CRS_GEO).to_file(
        args.outdir / "poligonos_asistidos_subzona_experimental.geojson", driver="GeoJSON"
    )
    gdf_zonas.drop(columns="geometry").to_csv(
        args.outdir / "resumen_poligonos_asistidos_subzona.csv", index=False
    )
    mapa_asistido(gdf_zonas, gdf_apartados, fuente_input,
                  args.outdir / "mapa_poligonos_asistidos_subzona_experimental.png")

    # --- Comparativo ---
    eps_eq, ms_eq = CANDIDATAS_DBSCAN[CANDIDATA_PARA_POLIGONOS]
    mapa_comparativo(gdf, gdf_dbscan_eq, gdf_zonas, eps_eq, ms_eq, fuente_input,
                     args.outdir / "comparativo_dbscan_vs_asistido.png")

    # --- Resumen consola ---
    print(f"\nPoligonos asistidos por subzona: {len(gdf_zonas)} grupos")
    for _, r in gdf_zonas.iterrows():
        extra = f" (+{r['n_apartados_excluidos']} apartados)" if r["n_apartados_excluidos"] else ""
        print(f"  {r['zona_id']} {r['etiqueta']}: {r['n_puntos']} pts{extra}, "
              f"{r['area_ha']:.1f} ha, confianza {r['confianza']}, {r['metodo']}")
    print(f"\npuntos apartados excluidos de su zona: {len(gdf_apartados)}")
    for _, r in gdf_apartados.iterrows():
        print(f"  {r['polo']} | {r.get('nombre_lugar', 's/d')} | lat={r['lat']:.5f} lon={r['lon']:.5f}")
    print("\nNota: " + NOTA_MAPA)


if __name__ == "__main__":
    main()
