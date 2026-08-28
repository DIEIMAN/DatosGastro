# -*- coding: utf-8 -*-
"""Experimento: poligonos exploratorios de concentracion gastronomica (PolosGastro).

Genera una capa auxiliar de poligonos estimados via clustering espacial (DBSCAN)
sobre los locales semilla georreferenciados de Fase 13. Los resultados son
EXPLORATORIOS: no constituyen limites oficiales y requieren revision territorial.

No modifica el informe vigente, ni Fase 25, ni PDFs finales, ni datos fuente.
Solo lee inputs existentes del repo y escribe en la carpeta experimental.

Uso:
    .venv/Scripts/python.exe scripts/polos_gastro/experimentos/generar_poligonos_clustering.py
    [--input CSV] [--outdir DIR] [--eps METROS] [--min-samples N]

Si no se fuerzan --eps/--min-samples, prueba una grilla y elige una configuracion
segun un criterio documentado (ver METODOLOGIA_POLIGONOS_CLUSTERING.md).
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
from shapely.geometry import MultiPoint

try:
    from sklearn.cluster import DBSCAN
except ImportError:
    sys.exit(
        "Falta scikit-learn en .venv (pip install scikit-learn). "
        "No se improvisa un algoritmo alternativo."
    )

REPO = Path(__file__).resolve().parents[3]

INPUT_DEFAULT = REPO / "outputs/polos_gastro/fase13_mapas/tablas/locales_para_mapa_revision.csv"
OUTDIR_DEFAULT = REPO / "outputs/polos_gastro/experimentos_clustering"
BARRIOS_GEOJSON = REPO / "PolosGastro/cartografia/barrios_caba.geojson"
COMUNAS_GEOJSON = REPO / "PolosGastro/cartografia/comunas_caba.geojson"
SUBZONAS_EDITORIALES = (
    REPO / "outputs/polos_gastro/fase16_mapas_editoriales_v4/tablas/subzonas_editoriales_geometrias.geojson"
)

CRS_GEO = "EPSG:4326"
CRS_METRICO = "EPSG:5347"  # POSGAR 2007 / Argentina faja 5 (metrico, cubre CABA)

EPS_GRILLA = [150, 200, 250, 300, 400, 500]
MIN_SAMPLES_GRILLA = [3, 4, 5, 6]
BUFFER_SUAVE_M = 40  # ensancha el hull para que el poligono no quede lineal

NOTA_EXPLORATORIA = "Poligono exploratorio auxiliar. No constituye limite oficial."
NOTA_MAPA = (
    "Capa auxiliar exploratoria. No constituye limite oficial. Requiere revision territorial."
)

# Paleta categorica validada (dataviz skill, modo claro). La identidad de cluster
# nunca depende solo del color: cada cluster lleva etiqueta directa "C<n>".
PALETA = ["#2a78d6", "#1baf7a", "#eda100", "#008300", "#4a3aa7", "#e34948", "#e87ba4", "#eb6834"]
COLOR_RUIDO = "#898781"
COLOR_BARRIOS = "#f0efec"
COLOR_BORDE_BARRIOS = "#ffffff"
COLOR_TEXTO = "#0b0b0b"
COLOR_TEXTO_SEC = "#52514e"


def color_cluster(cid: int) -> str:
    return PALETA[cid % len(PALETA)]


def cargar_puntos(path_input: Path):
    """Carga y valida puntos. Devuelve (gdf_validos_metrico, qa: dict)."""
    df = pd.read_csv(path_input)
    qa = {"puntos_cargados": len(df), "descartes": []}

    for col in ("lat", "lon"):
        if col not in df.columns:
            sys.exit(f"El input no tiene columna '{col}': {path_input}")
    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lon"] = pd.to_numeric(df["lon"], errors="coerce")

    sin_coord = df["lat"].isna() | df["lon"].isna()
    if sin_coord.any():
        qa["descartes"].append(("sin coordenadas numericas", int(sin_coord.sum())))
    df = df[~sin_coord].copy()

    # Duplicados probables: no doble-contar densidad (ver metodologia).
    if "estado_consolidado" in df.columns:
        dup = df["estado_consolidado"].eq("duplicado_probable")
        if dup.any():
            qa["descartes"].append(("estado_consolidado=duplicado_probable", int(dup.sum())))
        df = df[~dup].copy()

    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df["lon"], df["lat"]), crs=CRS_GEO)

    comunas = gpd.read_file(COMUNAS_GEOJSON).to_crs(CRS_GEO)
    limite_caba = comunas.union_all()
    fuera = ~gdf.geometry.within(limite_caba)
    if fuera.any():
        qa["descartes"].append(("fuera del limite de CABA", int(fuera.sum())))
        for _, r in gdf[fuera].iterrows():
            qa.setdefault("detalle_fuera_caba", []).append(
                f"{r.get('polo', 's/d')} | lat={r['lat']:.5f} lon={r['lon']:.5f}"
            )
    gdf = gdf[~fuera].copy()

    qa["puntos_validos"] = len(gdf)
    return gdf.to_crs(CRS_METRICO), qa


def pesos_auxiliares(gdf) -> np.ndarray:
    """Peso auxiliar por punto. Con rating/reviews: 1 + max(rating-3.5,0)*log1p(reviews).

    El input elegido (Fase 13) no trae rating/reviews, asi que el peso es 1 para
    todos los puntos. El score auxiliar nunca se usa para afirmar calidad comercial.
    """
    col_rating = next((c for c in gdf.columns if "rating" in c.lower() and "total" not in c.lower()), None)
    col_reviews = next(
        (c for c in gdf.columns if "user_ratings" in c.lower() or "reviews" in c.lower()), None
    )
    if col_rating and col_reviews:
        rating = pd.to_numeric(gdf[col_rating], errors="coerce").fillna(0.0)
        reviews = pd.to_numeric(gdf[col_reviews], errors="coerce").fillna(0.0)
        score_aux = np.maximum(rating - 3.5, 0.0) * np.log1p(reviews)
        return (1.0 + score_aux).to_numpy()
    return np.ones(len(gdf))


def correr_grilla(xy: np.ndarray, pesos: np.ndarray) -> pd.DataFrame:
    filas = []
    n = len(xy)
    for eps in EPS_GRILLA:
        for ms in MIN_SAMPLES_GRILLA:
            labels = DBSCAN(eps=eps, min_samples=ms).fit(xy, sample_weight=pesos).labels_
            tamanios = pd.Series(labels[labels >= 0]).value_counts()
            n_ruido = int((labels == -1).sum())
            filas.append(
                {
                    "eps_m": eps,
                    "min_samples": ms,
                    "n_clusters": int(tamanios.shape[0]),
                    "n_ruido": n_ruido,
                    "pct_ruido": round(100.0 * n_ruido / n, 1),
                    "tamanio_min": int(tamanios.min()) if len(tamanios) else 0,
                    "tamanio_max": int(tamanios.max()) if len(tamanios) else 0,
                    "tamanio_mediano": float(tamanios.median()) if len(tamanios) else 0.0,
                }
            )
    return pd.DataFrame(filas)


def elegir_configuracion(tabla: pd.DataFrame, n_puntos: int, n_polos: int):
    """Criterio documentado (no a ciegas):

    Candidatas: 6 <= n_clusters <= 20, pct_ruido <= 55 % y ningun cluster con mas
    del 50 % de los puntos (evita fusionar media Ciudad en un cluster).
    El techo de ruido es alto a proposito: el universo semilla es ralo (~7 puntos
    por polo) y en DBSCAN "ruido" significa punto sin acompanamiento local
    suficiente, no dato invalido; con esta densidad ninguna configuracion de la
    grilla baja del 43 % de ruido (ver parametros_probados.csv).
    Entre candidatas se minimiza |n_clusters - n_polos| + pct_ruido/10 (cercania a
    la escala editorial conocida penalizando ruido). Empate: menor eps (poligonos
    mas compactos y auditables).
    """
    cand = tabla[
        (tabla["n_clusters"].between(6, 20))
        & (tabla["pct_ruido"] <= 55.0)
        & (tabla["tamanio_max"] <= 0.5 * n_puntos)
    ].copy()
    if cand.empty:
        return None
    cand["criterio"] = (cand["n_clusters"] - n_polos).abs() + cand["pct_ruido"] / 10.0
    cand = cand.sort_values(["criterio", "eps_m", "min_samples"])
    fila = cand.iloc[0]
    return int(fila["eps_m"]), int(fila["min_samples"])


def poligono_de_cluster(puntos_metricos):
    """Hull del cluster: concave si shapely lo permite y es valido; si no, convex.

    Siempre se aplica un buffer suave para que puntos colineales no dejen un
    poligono degenerado (linea o punto).
    """
    mp = MultiPoint(list(puntos_metricos))
    algoritmo = "convex_hull"
    hull = mp.convex_hull
    if hasattr(shapely, "concave_hull") and len(mp.geoms) >= 4:
        candidato = shapely.concave_hull(mp, ratio=0.5, allow_holes=False)
        if candidato is not None and not candidato.is_empty and candidato.is_valid and candidato.area > 0:
            hull = candidato
            algoritmo = "concave_hull(ratio=0.5)"
    poligono = hull.buffer(BUFFER_SUAVE_M)
    return poligono, f"DBSCAN + {algoritmo} + buffer {BUFFER_SUAVE_M} m"


def distribucion_polos(sub: pd.DataFrame):
    if "polo" not in sub.columns:
        return None, None, None
    vc = sub["polo"].value_counts()
    mayoritario = vc.index[0]
    pct = round(100.0 * vc.iloc[0] / len(sub), 1)
    distrib = "; ".join(f"{polo}: {n}" for polo, n in vc.items())
    return mayoritario, pct, distrib


def construir_poligonos(gdf, labels, eps, ms, fuente_input):
    filas = []
    for cid in sorted(set(labels)):
        if cid == -1:
            continue
        sub = gdf[labels == cid]
        poligono, algoritmo = poligono_de_cluster(sub.geometry)
        mayoritario, pct, distrib = distribucion_polos(sub)
        filas.append(
            {
                "cluster_id": int(cid),
                "n_puntos": len(sub),
                "algoritmo": algoritmo,
                "eps_m": eps,
                "min_samples": ms,
                "area_m2": round(poligono.area, 1),
                "area_ha": round(poligono.area / 10_000.0, 2),
                "fuente_input": fuente_input,
                "polo_mayoritario": mayoritario,
                "porcentaje_polo_mayoritario": pct,
                "distribucion_polos": distrib,
                "nota": NOTA_EXPLORATORIA,
                "geometry": poligono,
            }
        )
    return gpd.GeoDataFrame(filas, crs=CRS_METRICO)


def pie_de_mapa(fig, fuente_input):
    fig.text(0.5, 0.035, NOTA_MAPA, ha="center", fontsize=9.5, color=COLOR_TEXTO, weight="bold")
    fig.text(
        0.5, 0.015,
        f"Fuente de puntos: {fuente_input} (universo semilla, no censo). DGDGAS - uso interno.",
        ha="center", fontsize=7.5, color=COLOR_TEXTO_SEC,
    )


def dibujar_base(ax):
    barrios = gpd.read_file(BARRIOS_GEOJSON).to_crs(CRS_METRICO)
    barrios.plot(ax=ax, color=COLOR_BARRIOS, edgecolor=COLOR_BORDE_BARRIOS, linewidth=0.6)
    ax.set_axis_off()
    return barrios


def etiquetas_clusters(ax, gdf_poligonos):
    for _, r in gdf_poligonos.iterrows():
        c = r.geometry.centroid
        ax.annotate(
            f"C{r['cluster_id']}", (c.x, c.y), xytext=(9, 9), textcoords="offset points",
            fontsize=9.5, weight="bold", color=COLOR_TEXTO, ha="left", va="bottom", zorder=7,
            path_effects=[pe.withStroke(linewidth=2.5, foreground="white")],
        )


def mapa_puntos(gdf, labels, gdf_poligonos, eps, ms, fuente_input, path_png):
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
    etiquetas_clusters(ax, gdf_poligonos)
    ax.set_title(
        "EXPERIMENTAL - Clusters espaciales de locales del universo semilla PolosGastro\n"
        f"DBSCAN eps={eps} m, min_samples={ms} (CRS {CRS_METRICO})",
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


def mapa_poligonos(gdf, labels, gdf_poligonos, eps, ms, fuente_input, path_png):
    fig, ax = plt.subplots(figsize=(10.5, 12))
    dibujar_base(ax)
    # Capa editorial de referencia (solo lectura, solo contorno).
    hay_editorial = SUBZONAS_EDITORIALES.exists()
    if hay_editorial:
        editorial = gpd.read_file(SUBZONAS_EDITORIALES).to_crs(CRS_METRICO)
        editorial.boundary.plot(ax=ax, color="#a9a8a1", linewidth=0.8,
                                linestyle="--", zorder=2)
    for _, r in gdf_poligonos.iterrows():
        col = color_cluster(int(r["cluster_id"]))
        gpd.GeoSeries([r.geometry], crs=CRS_METRICO).plot(
            ax=ax, color=col, alpha=0.45, edgecolor=col, linewidth=2.2, zorder=3
        )
    ruido = gdf[labels == -1]
    if len(ruido):
        ax.scatter(ruido.geometry.x, ruido.geometry.y, c=COLOR_RUIDO, marker="x", s=24,
                   linewidths=1.0, zorder=4)
    validos = gdf[labels >= 0]
    ax.scatter(validos.geometry.x, validos.geometry.y, c=COLOR_TEXTO_SEC, s=6, zorder=4)
    etiquetas_clusters(ax, gdf_poligonos)
    ax.set_title(
        "EXPERIMENTAL - Poligonos exploratorios de concentracion (capa auxiliar estimada)\n"
        f"DBSCAN eps={eps} m, min_samples={ms} + hull por cluster",
        fontsize=12, color=COLOR_TEXTO,
    )
    leyenda = [
        Line2D([], [], marker="s", linestyle="", markerfacecolor=PALETA[0], alpha=0.5,
               markeredgecolor=PALETA[0], markersize=9, label="Poligono exploratorio (color por cluster)"),
        Line2D([], [], marker="x", linestyle="", color=COLOR_RUIDO, markersize=7,
               label="Ruido / outlier (sin cluster)"),
    ]
    if hay_editorial:
        leyenda.append(Line2D([], [], linestyle="--", color=COLOR_TEXTO_SEC,
                              label="Subzonas editoriales V4 (referencia, sin modificar)"))
    ax.legend(handles=leyenda, loc="upper left", fontsize=8, frameon=True)
    pie_de_mapa(fig, fuente_input)
    fig.savefig(path_png, dpi=150, bbox_inches="tight")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=INPUT_DEFAULT)
    parser.add_argument("--outdir", type=Path, default=OUTDIR_DEFAULT)
    parser.add_argument("--eps", type=float, default=None, help="Forzar eps en metros")
    parser.add_argument("--min-samples", type=int, default=None, help="Forzar min_samples")
    args = parser.parse_args()

    args.outdir.mkdir(parents=True, exist_ok=True)
    fuente_input = str(args.input.relative_to(REPO)) if args.input.is_absolute() else str(args.input)

    gdf, qa = cargar_puntos(args.input)
    if len(gdf) < 10:
        sys.exit(f"Solo {len(gdf)} puntos validos: insuficiente para el experimento.")
    xy = np.column_stack([gdf.geometry.x, gdf.geometry.y])
    pesos = pesos_auxiliares(gdf)
    n_polos = gdf["polo"].nunique() if "polo" in gdf.columns else 0

    tabla = correr_grilla(xy, pesos)
    tabla.to_csv(args.outdir / "parametros_probados.csv", index=False)

    if args.eps is not None and args.min_samples is not None:
        eps, ms = args.eps, args.min_samples
        modo_eleccion = "forzada por CLI"
    else:
        eleccion = elegir_configuracion(tabla, len(gdf), n_polos)
        if eleccion is None:
            sys.exit(
                "Ninguna configuracion de la grilla cumple el criterio documentado. "
                "Revisar parametros_probados.csv y forzar --eps/--min-samples."
            )
        eps, ms = eleccion
        modo_eleccion = "automatica segun criterio documentado"

    labels = DBSCAN(eps=eps, min_samples=ms).fit(xy, sample_weight=pesos).labels_
    gdf = gdf.copy()
    gdf["cluster_id"] = labels
    gdf["nota"] = NOTA_EXPLORATORIA

    gdf_poligonos = construir_poligonos(gdf, labels, eps, ms, fuente_input)

    # --- Exportes ---
    cols_puntos = [c for c in ("polo", "subzona", "nombre_lugar", "estado_consolidado",
                               "cluster_id", "nota", "geometry") if c in gdf.columns]
    gdf[cols_puntos].to_crs(CRS_GEO).to_file(
        args.outdir / "puntos_clustering_experimental.geojson", driver="GeoJSON"
    )
    gdf_poligonos.to_crs(CRS_GEO).to_file(
        args.outdir / "poligonos_clustering_experimental.geojson", driver="GeoJSON"
    )
    gdf_poligonos.drop(columns="geometry").to_csv(args.outdir / "resumen_clusters.csv", index=False)

    mapa_puntos(gdf, labels, gdf_poligonos, eps, ms, fuente_input,
                args.outdir / "mapa_clusters_experimental.png")
    mapa_poligonos(gdf, labels, gdf_poligonos, eps, ms, fuente_input,
                   args.outdir / "mapa_poligonos_experimental.png")

    # --- Resumen QA por consola ---
    n_ruido = int((labels == -1).sum())
    print("=" * 72)
    print("EXPERIMENTO CLUSTERING POLOS - RESUMEN (capa auxiliar exploratoria)")
    print("=" * 72)
    print(f"input: {fuente_input}")
    print(f"puntos cargados: {qa['puntos_cargados']}")
    for motivo, n in qa["descartes"]:
        print(f"  descartados ({motivo}): {n}")
    for det in qa.get("detalle_fuera_caba", []):
        print(f"    fuera de CABA -> {det}")
    print(f"puntos validos: {qa['puntos_validos']}")
    print(f"CRS metrico: {CRS_METRICO} | pesos: "
          f"{'score_aux (rating/reviews)' if pesos.max() > 1 else 'uniformes = 1'}")
    print(f"configuracion: eps={eps} m, min_samples={ms} ({modo_eleccion})")
    print(f"clusters: {len(gdf_poligonos)} | ruido: {n_ruido} "
          f"({100.0 * n_ruido / len(gdf):.1f} %)")
    if len(gdf_poligonos):
        print(f"area_ha: min={gdf_poligonos['area_ha'].min():.2f} "
              f"max={gdf_poligonos['area_ha'].max():.2f} "
              f"mediana={gdf_poligonos['area_ha'].median():.2f}")
    print("\ncluster -> polos (n puntos):")
    for _, r in gdf_poligonos.iterrows():
        print(f"  C{r['cluster_id']} ({r['n_puntos']} pts, {r['area_ha']:.1f} ha): "
              f"{r['distribucion_polos']}")
    if "polo" in gdf.columns and n_ruido:
        print("\nruido por polo:")
        for polo, n in gdf.loc[labels == -1, "polo"].value_counts().items():
            print(f"  {polo}: {n}")
    if "polo" in gdf.columns:
        print("\npolo -> clusters:")
        asign = gdf.assign(c=labels)
        for polo, sub in asign.groupby("polo"):
            partes = ", ".join(
                f"C{c}: {n}" if c >= 0 else f"ruido: {n}"
                for c, n in sub["c"].value_counts().sort_index().items()
            )
            print(f"  {polo}: {partes}")
    print("\nNota: " + NOTA_MAPA)


if __name__ == "__main__":
    main()
