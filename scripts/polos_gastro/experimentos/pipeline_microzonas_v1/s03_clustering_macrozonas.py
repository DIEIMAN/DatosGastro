# -*- coding: utf-8 -*-
"""Etapa 3 — Clustering intra-macrozona sobre el universo V1.

EXPERIMENTAL. No define limites oficiales; requiere revision humana.

Flujo:
1. Contenedores de macrozona: hull convexo de los puntos semilla por polo
   (Fase 13, con depuracion de sedes apartadas) + buffer de 500 m, recortado a
   CABA. Abasto se integra al contenedor de Avenida Corrientes (decision
   editorial vigente). Los contenedores son una capa de trabajo APROXIMADA.
2. Asignacion: cada entidad apta del universo V1 cae en un solo contenedor
   (el de hull base mas cercano si hay solapamiento). El residuo queda en la
   capa diagnostica `entidades_fuera_de_macrozona.csv` (posibles zonas
   emergentes; no se descarta).
3. Por macrozona: HDBSCAN (detector principal) si hay >= 30 puntos; si no,
   DBSCAN(150 m, 4) declarado como alternativa por evidencia insuficiente.
   Ademas: DBSCAN(650 m, 4) de continuidad con la Tanda 2 y DBSCAN(150 m, 4)
   local en todas las macrozonas, para la comparacion de la Etapa 6.
4. KDE de control por macrozona (bw 100 m, grilla 20 m, umbral 40 % del
   maximo local) -> contornos como GeoJSON + mapa por macrozona.

Todos los parametros salen de config.PARAMETROS y quedan en
`parametros_pipeline_v1.json` + `clustering/parametros_corrida.json`.

Uso:
    .venv/Scripts/python.exe scripts/polos_gastro/experimentos/pipeline_microzonas_v1/s03_clustering_macrozonas.py
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from scipy.spatial import cKDTree
from shapely.geometry import MultiPoint, Polygon
from sklearn.cluster import DBSCAN, HDBSCAN
from sklearn.neighbors import KernelDensity

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config  # noqa: E402

PALETA = ["#2a78d6", "#1baf7a", "#eda100", "#008300", "#4a3aa7", "#e34948",
          "#e87ba4", "#eb6834", "#0f766e", "#b45309"]
COLOR_RUIDO = "#898781"
COLOR_BARRIOS = "#f0efec"


def limpiar_texto(s: str) -> str:
    return str(s).replace("�", "ñ")


# ---------------------------------------------------------------------------
# 1. Contenedores de macrozona
# ---------------------------------------------------------------------------

def construir_contenedores() -> tuple[gpd.GeoDataFrame, dict]:
    log: dict = {}
    semilla = pd.read_csv(config.SEMILLA_CSV)
    semilla = semilla[semilla["estado_consolidado"] != "duplicado_probable"].copy()
    semilla = semilla.dropna(subset=["lat", "lon"])
    semilla["macrozona"] = semilla["polo"].map(limpiar_texto)
    if config.PARAMETROS["macrozonas"]["abasto_en_corrientes"]["valor"]:
        semilla.loc[semilla["macrozona"] == "Abasto", "macrozona"] = "Avenida Corrientes"

    gdf = gpd.GeoDataFrame(
        semilla, geometry=gpd.points_from_xy(semilla["lon"], semilla["lat"]),
        crs=config.CRS_GEO,
    ).to_crs(config.CRS_METRICO)

    caba = gpd.read_file(config.COMUNAS_GEOJSON).to_crs(config.CRS_METRICO).union_all()
    buffer_m = config.PARAMETROS["macrozonas"]["buffer_contenedor_m"]["valor"]

    radio_max = float(config.PARAMETROS["macrozonas"]["radio_max_semilla_m"]["valor"])
    min_semilla = config.PARAMETROS["macrozonas"]["min_semilla_contenedor"]["valor"]

    filas = []
    for macro, sub in gdf.groupby("macrozona"):
        # Depuracion de sedes apartadas: radio maximo editorial fijo (ver config;
        # la regla relativa de Tanda 2 fallaba con varias sedes malas por polo).
        cx, cy = sub.geometry.x.median(), sub.geometry.y.median()
        dist = np.hypot(sub.geometry.x - cx, sub.geometry.y - cy)
        apartados = int((dist > radio_max).sum())
        sub = sub[dist <= radio_max]
        hull_base = MultiPoint(list(sub.geometry)).convex_hull
        contenedor = hull_base.buffer(buffer_m).intersection(caba)
        filas.append(
            {
                "macrozona": macro,
                "n_semilla": len(sub),
                "n_semilla_apartados": apartados,
                "contenedor_degradado": bool(len(sub) < min_semilla),
                "area_contenedor_ha": round(contenedor.area / 10_000.0, 1),
                "hull_base_wkt": hull_base.wkt,
                "geometry": contenedor,
            }
        )
    cont = gpd.GeoDataFrame(filas, crs=config.CRS_METRICO)
    log["macrozonas"] = len(cont)
    log["semilla_usada"] = int(cont["n_semilla"].sum())
    log["semilla_apartados_excluidos"] = int(cont["n_semilla_apartados"].sum())
    return cont, log


def asignar_entidades(ent: pd.DataFrame, cont: gpd.GeoDataFrame, log: dict):
    gdf = gpd.GeoDataFrame(
        ent, geometry=gpd.points_from_xy(ent["lon"], ent["lat"]), crs=config.CRS_GEO
    ).to_crs(config.CRS_METRICO)

    from shapely import wkt as shapely_wkt
    hulls_base = {r["macrozona"]: shapely_wkt.loads(r["hull_base_wkt"]) for _, r in cont.iterrows()}
    areas_hull = {m: h.area for m, h in hulls_base.items()}

    join = gpd.sjoin(
        gdf[["id_entidad", "geometry"]],
        cont[["macrozona", "geometry"]],
        how="left", predicate="within",
    )
    # Puntos en mas de un contenedor: menor distancia al hull base; ante empate
    # (dentro de dos hulls solapados), el hull mas chico = macrozona mas
    # especifica (doc 01 s4.4 + parametro macrozonas.asignacion_multiple).
    multi = join.index[join.index.duplicated(keep=False)].unique()
    resueltos = {}
    for idx in multi:
        candidatas = join.loc[[idx], "macrozona"].tolist()
        punto = gdf.geometry.loc[idx]
        resueltos[idx] = min(
            candidatas, key=lambda m: (round(punto.distance(hulls_base[m]), 1), areas_hull[m])
        )
    join = join[~join.index.duplicated(keep="first")]
    asign = join["macrozona"].copy()
    for idx, m in resueltos.items():
        asign.loc[idx] = m

    gdf["macrozona"] = asign
    log["entidades_en_alguna_macrozona"] = int(gdf["macrozona"].notna().sum())
    log["entidades_fuera_de_macrozona"] = int(gdf["macrozona"].isna().sum())
    log["entidades_en_contenedores_solapados"] = len(multi)

    # Sensibilidad del buffer del contenedor
    sens = {}
    for b in config.PARAMETROS["macrozonas"]["buffers_sensibilidad_m"]["valor"]:
        capa = cont.copy()
        from shapely import wkt as _wkt
        caba = gpd.read_file(config.COMUNAS_GEOJSON).to_crs(config.CRS_METRICO).union_all()
        capa["geometry"] = [
            _wkt.loads(r["hull_base_wkt"]).buffer(b).intersection(caba)
            for _, r in capa.iterrows()
        ]
        j = gpd.sjoin(gdf[["geometry"]], capa[["macrozona", "geometry"]],
                      how="inner", predicate="within")
        sens[f"buffer_{b}m"] = int(j.index.nunique())
    sens[f"buffer_{config.PARAMETROS['macrozonas']['buffer_contenedor_m']['valor']}m_elegido"] = (
        log["entidades_en_alguna_macrozona"]
    )
    log["sensibilidad_buffer_contenedor"] = sens
    return gdf


# ---------------------------------------------------------------------------
# 3. Clustering por macrozona
# ---------------------------------------------------------------------------

def parametros_hdbscan(n: int) -> dict:
    return {
        "min_cluster_size": max(8, int(np.ceil(0.03 * n))),
        "min_samples": config.PARAMETROS["clustering"]["hdbscan_min_samples"]["valor"],
        "cluster_selection_epsilon": float(
            config.PARAMETROS["clustering"]["hdbscan_cluster_selection_epsilon_m"]["valor"]
        ),
        "cluster_selection_method": config.PARAMETROS["clustering"][
            "hdbscan_cluster_selection_method"]["valor"],
    }


def clusterizar_macrozona(xy: np.ndarray, registro: dict) -> dict[str, np.ndarray]:
    """Devuelve labels por metodo y completa el registro de parametros."""
    n = len(xy)
    minimo = config.PARAMETROS["clustering"]["minimo_puntos_macrozona"]["valor"]
    resultados: dict[str, np.ndarray] = {}

    if n >= minimo:
        params = parametros_hdbscan(n)
        modelo = HDBSCAN(**params)
        resultados["hdbscan"] = modelo.fit_predict(xy)
        registro["metodo_principal"] = "hdbscan"
        registro["hdbscan_params"] = params
        registro["justificacion_metodo"] = (
            f"n={n} >= {minimo}: HDBSCAN aplicable (detector principal, doc 02 s2.2)."
        )
    else:
        fb = config.PARAMETROS["clustering"]["dbscan_fallback"]["valor"]
        resultados["hdbscan"] = DBSCAN(eps=fb["eps_m"], min_samples=fb["min_samples"]).fit_predict(xy)
        registro["metodo_principal"] = "dbscan_fallback"
        registro["dbscan_fallback_params"] = fb
        registro["justificacion_metodo"] = (
            f"n={n} < {minimo}: HDBSCAN fragmenta o no encuentra estructura con tan pocos "
            f"puntos (doc 02 s2.1). Se corre DBSCAN(eps={fb['eps_m']} m, ms={fb['min_samples']}) "
            "y la macrozona queda marcada `evidencia_insuficiente`."
        )
        registro["evidencia_insuficiente"] = True

    cont = config.PARAMETROS["clustering"]["dbscan_continuidad"]["valor"]
    resultados["dbscan_continuidad"] = DBSCAN(
        eps=cont["eps_m"], min_samples=cont["min_samples"]
    ).fit_predict(xy)
    fb = config.PARAMETROS["clustering"]["dbscan_fallback"]["valor"]
    resultados["dbscan_local"] = DBSCAN(
        eps=fb["eps_m"], min_samples=fb["min_samples"]
    ).fit_predict(xy)
    registro["dbscan_continuidad_params"] = cont
    registro["dbscan_local_params"] = fb
    return resultados


def contornos_kde(xy: np.ndarray, contenedor) -> tuple[list[Polygon], dict]:
    """Contornos KDE >= umbral relativo del maximo de la macrozona."""
    bw = config.PARAMETROS["clustering"]["kde_bandwidth_m"]["valor"]
    celda = config.PARAMETROS["clustering"]["kde_grilla_m"]["valor"]
    umbral_rel = config.PARAMETROS["clustering"]["kde_umbral_relativo"]["valor"]

    minx, miny, maxx, maxy = contenedor.bounds
    gx = np.arange(minx, maxx + celda, celda)
    gy = np.arange(miny, maxy + celda, celda)
    mx, my = np.meshgrid(gx, gy)
    grilla = np.column_stack([mx.ravel(), my.ravel()])

    kde = KernelDensity(kernel="gaussian", bandwidth=bw).fit(xy)
    dens = np.exp(kde.score_samples(grilla)).reshape(mx.shape)
    nivel = umbral_rel * dens.max()

    fig, ax = plt.subplots()
    cs = ax.contour(mx, my, dens, levels=[nivel])
    poligonos = []
    for path in cs.get_paths():
        for coords in path.to_polygons():
            if len(coords) >= 4:
                p = Polygon(coords)
                if p.is_valid and p.area > 0:
                    poligonos.append(p.intersection(contenedor))
    plt.close(fig)
    info = {"bandwidth_m": bw, "celda_m": celda, "umbral_relativo": umbral_rel,
            "densidad_max": float(dens.max()), "n_contornos": len(poligonos)}
    return [p for p in poligonos if not p.is_empty], info


# ---------------------------------------------------------------------------
# Mapas de control
# ---------------------------------------------------------------------------

def mapa_macrozona(macro, sub, labels, kde_polis, contenedor, registro, path_png):
    fig, ax = plt.subplots(figsize=(10, 10))
    barrios = gpd.read_file(config.BARRIOS_GEOJSON).to_crs(config.CRS_METRICO)
    barrios.plot(ax=ax, color=COLOR_BARRIOS, edgecolor="#ffffff", linewidth=0.6)
    gpd.GeoSeries([contenedor], crs=config.CRS_METRICO).boundary.plot(
        ax=ax, color="#52514e", linewidth=1.2, linestyle=(0, (5, 4))
    )
    for poli in kde_polis:
        gpd.GeoSeries([poli], crs=config.CRS_METRICO).boundary.plot(
            ax=ax, color="#d95926", linewidth=1.6
        )
    ruido = sub[labels == -1]
    if len(ruido):
        ax.scatter(ruido.geometry.x, ruido.geometry.y, c=COLOR_RUIDO, marker="x",
                   s=14, linewidths=0.8, zorder=3, alpha=0.7)
    for cid in sorted({c for c in labels if c >= 0}):
        pts = sub[labels == cid]
        ax.scatter(pts.geometry.x, pts.geometry.y, c=PALETA[cid % len(PALETA)],
                   s=18, edgecolors="white", linewidths=0.4, zorder=4)
        cx, cy = pts.geometry.x.mean(), pts.geometry.y.mean()
        ax.annotate(f"C{cid} ({len(pts)})", (cx, cy), fontsize=10, weight="bold",
                    ha="center", color="#0b0b0b", zorder=6,
                    bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.75))
    minx, miny, maxx, maxy = contenedor.buffer(300).bounds
    ax.set_xlim(minx, maxx)
    ax.set_ylim(miny, maxy)
    ax.set_axis_off()
    metodo = registro["metodo_principal"]
    n_cl = len({c for c in labels if c >= 0})
    pct_ruido = 100.0 * (labels == -1).sum() / max(len(labels), 1)
    ax.set_title(
        f"EXPERIMENTAL - {macro}\n"
        f"{metodo.upper()}: {len(sub)} entidades, {n_cl} clusters, ruido {pct_ruido:.0f} % | "
        "contorno naranja: nucleo KDE (40 % del max local)",
        fontsize=11,
    )
    leyenda = [
        Line2D([], [], marker="o", linestyle="", markerfacecolor=PALETA[0],
               markeredgecolor="white", markersize=7, label="Entidad en cluster"),
        Line2D([], [], marker="x", linestyle="", color=COLOR_RUIDO, markersize=7,
               label="Ruido (sin cluster)"),
        Line2D([], [], color="#d95926", linewidth=1.6, label="Nucleo KDE (control)"),
        Line2D([], [], color="#52514e", linewidth=1.2, linestyle=(0, (5, 4)),
               label="Contenedor macrozona (aproximado)"),
    ]
    ax.legend(handles=leyenda, loc="upper left", fontsize=8, frameon=True)
    fig.text(0.5, 0.02, config.NOTA_EXPERIMENTAL, ha="center", fontsize=7.5,
             color="#52514e", wrap=True)
    fig.savefig(path_png, dpi=140, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    config.asegurar_salidas("clustering", "clustering/mapas", "macrozonas")
    log: dict = {"fecha_corrida": date.today().isoformat()}

    ent = pd.read_csv(
        config.SALIDA / "universo" / "universo_entidades_v1.csv",
        dtype={"id_ubicacion": str},
    )
    ent = ent[ent["apta_clustering"]].copy()

    cont, log_cont = construir_contenedores()
    log.update(log_cont)
    cont.drop(columns=["hull_base_wkt"]).to_crs(config.CRS_GEO).to_file(
        config.SALIDA / "macrozonas" / "macrozonas_contenedores.geojson", driver="GeoJSON"
    )

    gdf = asignar_entidades(ent, cont, log)
    fuera = gdf[gdf["macrozona"].isna()]
    fuera.drop(columns="geometry").to_csv(
        config.SALIDA / "macrozonas" / "entidades_fuera_de_macrozona.csv", index=False
    )
    asignadas = gdf[gdf["macrozona"].notna()].copy()
    asignadas.drop(columns="geometry").to_csv(
        config.SALIDA / "macrozonas" / "asignacion_entidades_macrozona.csv", index=False
    )

    filas_labels = []
    filas_kde = []
    registros = {}
    for macro, sub in asignadas.groupby("macrozona"):
        sub = sub.copy()
        xy = np.column_stack([sub.geometry.x, sub.geometry.y])
        contenedor = cont.loc[cont["macrozona"] == macro, "geometry"].iloc[0]
        registro = {
            "n_entidades": len(sub),
            "area_contenedor_ha": float(
                cont.loc[cont["macrozona"] == macro, "area_contenedor_ha"].iloc[0]
            ),
        }
        registro["densidad_entidades_ha"] = round(
            len(sub) / registro["area_contenedor_ha"], 2
        )

        labels_por_metodo = clusterizar_macrozona(xy, registro)
        for metodo, labels in labels_por_metodo.items():
            registro.setdefault("resumen", {})[metodo] = {
                "clusters": int(len({c for c in labels if c >= 0})),
                "ruido": int((labels == -1).sum()),
                "pct_ruido": round(100.0 * (labels == -1).sum() / len(labels), 1),
            }
            for idx, lab in zip(sub["id_entidad"], labels):
                filas_labels.append(
                    {"id_entidad": idx, "macrozona": macro, "metodo": metodo,
                     "cluster_id": int(lab)}
                )

        kde_polis, kde_info = contornos_kde(xy, contenedor)
        registro["kde"] = kde_info
        for i, poli in enumerate(kde_polis):
            filas_kde.append(
                {"macrozona": macro, "kde_nucleo_id": i,
                 "area_ha": round(poli.area / 10_000.0, 2), "geometry": poli}
            )

        mapa_macrozona(
            macro, sub, labels_por_metodo["hdbscan"], kde_polis, contenedor, registro,
            config.SALIDA / "clustering" / "mapas"
            / f"clusters_{macro.lower().replace(' ', '_').replace('/', '_')}.png",
        )
        registros[macro] = registro
        r = registro["resumen"]["hdbscan"]
        print(f"{macro}: n={len(sub)} dens={registro['densidad_entidades_ha']}/ha "
              f"[{registro['metodo_principal']}] clusters={r['clusters']} "
              f"ruido={r['pct_ruido']}%")

    pd.DataFrame(filas_labels).to_csv(
        config.SALIDA / "clustering" / "labels_clusters.csv", index=False
    )
    if filas_kde:
        gpd.GeoDataFrame(filas_kde, crs=config.CRS_METRICO).to_crs(config.CRS_GEO).to_file(
            config.SALIDA / "clustering" / "nucleos_kde.geojson", driver="GeoJSON"
        )
    log["por_macrozona"] = registros
    with open(config.SALIDA / "clustering" / "parametros_corrida.json", "w",
              encoding="utf-8") as fh:
        json.dump(log, fh, ensure_ascii=False, indent=2)
    config.exportar_parametros()

    print(f"\nFuera de macrozona (capa diagnostica): {log['entidades_fuera_de_macrozona']:,}")
    print(f"Salidas en {config.SALIDA / 'clustering'}")


if __name__ == "__main__":
    main()
