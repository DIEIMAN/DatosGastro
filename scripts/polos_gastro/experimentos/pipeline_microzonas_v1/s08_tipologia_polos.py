# -*- coding: utf-8 -*-
"""Etapa V2-5 — Tipologia automatica de polos.

EXPERIMENTAL. Clasifica cada macrozona en una categoria segun metricas ya calculadas
(Etapas 3-5), con umbrales explicitos (sin ajuste fino a mano por macrozona):

1. EVIDENCIA_INSUFICIENTE   : < 30 entidades asignadas O 0 clusters HDBSCAN.
2. CONTENEDOR_BAJA_CONFIANZA: contenedor degradado (< 3 puntos semilla tras depurar) O
                               < 80 entidades asignadas.
3. CORREDOR_DOMINANTE       : existe >=1 cluster marcado `es_corredor` cuya suma de
                               locales es >= 30 % de los locales clusterizados de la
                               macrozona.
4. NUCLEO_DOMINANTE_SATELITES: el cluster mas grande concentra >= 45 % de los locales
                               clusterizados (y no es corredor).
5. MULTI_NUCLEO             : >= 3 clusters con >= 15 locales cada uno y ningun cluster
                               supera el 45 % (caso restante, el mas "sano": varios
                               nucleos comparables).
6. POLO_DISPERSO            : lo que no encaja arriba (pocos clusters chicos, ruido alto,
                               sin nucleo ni corredor claro).

Los umbrales (30 % para corredor, 45 % para dominante, 15 locales/3 clusters para
multi-nucleo) son heuristicos y estan pensados para ORDENAR el debate editorial, no para
cerrarlo.

Uso:
    .venv/Scripts/python.exe scripts/polos_gastro/experimentos/pipeline_microzonas_v1/s08_tipologia_polos.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config  # noqa: E402

UMBRAL_MIN_ENTIDADES_EVIDENCIA = 30
UMBRAL_MIN_ENTIDADES_CONFIANZA = 80
UMBRAL_PCT_CORREDOR_DOMINANTE = 30.0
UMBRAL_PCT_NUCLEO_DOMINANTE = 45.0
UMBRAL_N_CLUSTERS_MULTINUCLEO = 3
UMBRAL_MIN_LOCALES_SIGNIFICATIVO = 15


def clasificar(fila: pd.Series) -> tuple[str, str]:
    if fila["n_entidades_macrozona"] < UMBRAL_MIN_ENTIDADES_EVIDENCIA or fila["clusters"] == 0:
        return "EVIDENCIA_INSUFICIENTE", (
            f"{fila['n_entidades_macrozona']} entidades (< {UMBRAL_MIN_ENTIDADES_EVIDENCIA}) "
            f"o 0 clusters: no hay universo para clusterizar de forma confiable."
        )
    if fila["contenedor_degradado"] or fila["n_entidades_macrozona"] < UMBRAL_MIN_ENTIDADES_CONFIANZA:
        return "CONTENEDOR_BAJA_CONFIANZA", (
            f"contenedor degradado={fila['contenedor_degradado']} o solo "
            f"{fila['n_entidades_macrozona']} entidades (< {UMBRAL_MIN_ENTIDADES_CONFIANZA}): "
            "el resultado es plausible pero el contenedor mismo es poco confiable."
        )
    if fila["pct_locales_en_corredores"] >= UMBRAL_PCT_CORREDOR_DOMINANTE:
        return "CORREDOR_DOMINANTE", (
            f"{fila['pct_locales_en_corredores']:.0f} % de los locales clusterizados "
            f"caen en clusters marcados como corredor (>= {UMBRAL_PCT_CORREDOR_DOMINANTE:.0f} %)."
        )
    if fila["pct_puntos_en_cluster_dominante"] >= UMBRAL_PCT_NUCLEO_DOMINANTE:
        return "NUCLEO_DOMINANTE_SATELITES", (
            f"el cluster mas grande concentra {fila['pct_puntos_en_cluster_dominante']:.0f} % "
            f"de los locales clusterizados (>= {UMBRAL_PCT_NUCLEO_DOMINANTE:.0f} %)."
        )
    if (
        fila["n_clusters_significativos"] >= UMBRAL_N_CLUSTERS_MULTINUCLEO
        and fila["pct_puntos_en_cluster_dominante"] < UMBRAL_PCT_NUCLEO_DOMINANTE
    ):
        return "MULTI_NUCLEO", (
            f"{fila['n_clusters_significativos']} clusters con >= "
            f"{UMBRAL_MIN_LOCALES_SIGNIFICATIVO} locales cada uno, ninguno domina."
        )
    return "POLO_DISPERSO", (
        "no cumple ningun criterio anterior: clusters chicos y fragmentados sin nucleo "
        "ni corredor identificable."
    )


def main() -> None:
    det = pd.read_csv(config.SALIDA / "metricas" / "comparacion_detectores.csv")
    det = det[det["detector"] == "hdbscan"].set_index("macrozona")

    met = pd.read_csv(config.SALIDA / "metricas" / "metricas_microzonas.csv")
    hib = met[met["metodo"] == "hibrido_reglas"]

    cont = gpd.read_file(config.SALIDA / "macrozonas" / "macrozonas_contenedores.geojson")
    cont = cont.set_index("macrozona")

    asig = pd.read_csv(
        config.SALIDA / "macrozonas" / "asignacion_entidades_macrozona.csv",
        dtype={"id_ubicacion": str},
    )
    n_por_macro = asig.groupby("macrozona").size()

    filas = []
    for macro in cont.index:
        n_ent = int(n_por_macro.get(macro, 0))
        if macro in det.index:
            d = det.loc[macro]
            clusters = int(d["clusters"])
            pct_dominante = float(d["pct_puntos_en_cluster_dominante"])
        else:
            clusters, pct_dominante = 0, 0.0

        clusters_macro = hib[hib["macrozona"] == macro].drop_duplicates("cluster_id")
        n_clusteriz = int(clusters_macro["n_locales_cluster"].sum())
        n_corredor = int(clusters_macro.loc[clusters_macro["es_corredor"], "n_locales_cluster"].sum())
        pct_corredor = 100.0 * n_corredor / n_clusteriz if n_clusteriz else 0.0
        n_signif = int((clusters_macro["n_locales_cluster"] >= UMBRAL_MIN_LOCALES_SIGNIFICATIVO).sum())

        filas.append(
            {
                "macrozona": macro,
                "n_entidades_macrozona": n_ent,
                "contenedor_degradado": bool(cont.loc[macro, "contenedor_degradado"]),
                "clusters": clusters,
                "n_clusters_significativos": n_signif,
                "pct_puntos_en_cluster_dominante": pct_dominante,
                "pct_locales_en_corredores": pct_corredor,
            }
        )

    tabla = pd.DataFrame(filas)
    clasif = tabla.apply(clasificar, axis=1, result_type="expand")
    clasif.columns = ["tipologia", "justificacion"]
    tabla = pd.concat([tabla, clasif], axis=1)

    outdir = config.SALIDA / "validacion"
    outdir.mkdir(parents=True, exist_ok=True)
    tabla.to_csv(outdir / "tipologia_polos.csv", index=False)

    print(tabla[["macrozona", "n_entidades_macrozona", "clusters",
                 "pct_puntos_en_cluster_dominante", "pct_locales_en_corredores",
                 "tipologia"]].to_string(index=False))
    print(f"\nDistribucion de tipologias:\n{tabla['tipologia'].value_counts().to_string()}")
    print(f"\n-> {outdir / 'tipologia_polos.csv'}")


if __name__ == "__main__":
    main()
