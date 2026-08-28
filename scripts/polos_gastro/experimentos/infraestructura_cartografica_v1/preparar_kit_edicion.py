# -*- coding: utf-8 -*-
"""Etapa Infra-3 — Kit de edicion de contornos por macrozona (solo lectura).

EXPERIMENTAL. No es la herramienta de edicion en si (esa es QGIS / geojson.io, ver
`03_HERRAMIENTA_EDICION.md`): este script arma, para una macrozona, todas las capas de
referencia que un editor humano necesita cargar antes de trazar el poligono, para no
tener que ir a buscarlas a mano por todo el repo.

Para cada macrozona pedida exporta a una carpeta propia:
- callejero_referencia.geojson   : tramos de calle GCBA recortados al contenedor + 400 m
- entidades_universo_v1.geojson  : entidades del universo V1 (Etapa 1 del prototipo) que
                                    cayeron en esa macrozona, con nombre cuando existe
- microclusters_hdbscan.geojson  : puntos del prototipo V1 coloreados por cluster HDBSCAN
- poligonos_prototipo_v1.geojson : los poligonos hibridos ya generados (Etapa 4 del
                                    prototipo), como referencia de "lo que da el algoritmo"
- elipse_editorial_fase16.geojson: si la macrozona tiene subzonas en fase16, se incluyen
                                    como referencia de la demarcacion editorial previa
- semilla_fase13.geojson         : puntos semilla (Fase 13) de esa macrozona, con nombre
- LEEME.md                       : que es cada archivo y sugerencia de orden de carga

No modifica ninguna fuente. Solo lee `outputs/polos_gastro/experimentos/
pipeline_microzonas_v1/` (prototipo V1 ya corrido) y capas base del repo.

Uso:
    .venv/Scripts/python.exe scripts/polos_gastro/experimentos/infraestructura_cartografica_v1/preparar_kit_edicion.py "Palermo"
    .venv/Scripts/python.exe scripts/polos_gastro/experimentos/infraestructura_cartografica_v1/preparar_kit_edicion.py --todas
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd

REPO = Path(__file__).resolve().parents[4]
PROTOTIPO = REPO / "outputs" / "polos_gastro" / "experimentos" / "pipeline_microzonas_v1"
SALIDA = REPO / "outputs" / "polos_gastro" / "experimentos" / "infraestructura_cartografica_v1" / "kits_edicion"

CALLEJERO = REPO / "outputs/polos_gastro/fase15_mapas_callejeros_v3/assets/callejero_gcba_2026_06_02.geojson"
SUBZONAS_FASE16 = REPO / "outputs/polos_gastro/fase16_mapas_editoriales_v4/tablas/subzonas_editoriales_geometrias.geojson"
SEMILLA_CSV = REPO / "outputs/polos_gastro/fase13_mapas/tablas/locales_para_mapa_revision.csv"

CRS_GEO = "EPSG:4326"
CRS_METRICO = "EPSG:5347"
MARGEN_CALLEJERO_M = 400

MAPA_EDITORIAL_FASE16 = {
    "Palermo": "Palermo",
    "Avenida Corrientes": "Corrientes",
    "San Telmo": "San Telmo",
    "Belgrano": "Belgrano",
    "Puerto Madero": "Puerto Madero",
}


def limpiar_texto(s) -> str:
    return str(s).replace("�", "ñ")


def cargar_contenedor(macro: str) -> gpd.GeoSeries:
    cont = gpd.read_file(PROTOTIPO / "macrozonas" / "macrozonas_contenedores.geojson")
    fila = cont[cont["macrozona"] == macro]
    if not len(fila):
        raise SystemExit(f"Macrozona '{macro}' no tiene contenedor en el prototipo V1.")
    return fila.to_crs(CRS_METRICO).geometry.iloc[0]


def exportar_kit(macro: str) -> None:
    nombre_dir = macro.lower().replace(" ", "_").replace("/", "_")
    outdir = SALIDA / nombre_dir
    outdir.mkdir(parents=True, exist_ok=True)

    contenedor_m = cargar_contenedor(macro)
    extent_m = contenedor_m.buffer(MARGEN_CALLEJERO_M)
    extent_geo = gpd.GeoSeries([extent_m], crs=CRS_METRICO).to_crs(CRS_GEO).iloc[0]
    minx, miny, maxx, maxy = extent_geo.bounds

    # 1. Callejero recortado
    callejero = gpd.read_file(CALLEJERO)
    calles_zona = callejero.cx[minx:maxx, miny:maxy]
    calles_zona.to_file(outdir / "callejero_referencia.geojson", driver="GeoJSON")

    # 2. Entidades del universo V1 en esta macrozona
    asig = pd.read_csv(
        PROTOTIPO / "macrozonas" / "asignacion_entidades_macrozona.csv",
        dtype={"id_ubicacion": str},
    )
    labels = pd.read_csv(PROTOTIPO / "clustering" / "labels_clusters.csv")
    principal = labels[labels["metodo"] == "hdbscan"][["id_entidad", "cluster_id"]]
    asig = asig.merge(principal, on="id_entidad", how="left")
    sub = asig[asig["macrozona"] == macro].copy()
    gdf_ent = gpd.GeoDataFrame(
        sub, geometry=gpd.points_from_xy(sub["lon"], sub["lat"]), crs=CRS_GEO
    )
    gdf_ent[["id_entidad", "nombre_canonico", "categoria_canonica", "en_f01", "en_f02",
             "cluster_id", "geometry"]].to_file(
        outdir / "entidades_universo_v1.geojson", driver="GeoJSON"
    )

    # 3. Microclusters (mismo archivo, ya trae cluster_id: -1 = ruido)
    gdf_ent[["id_entidad", "cluster_id", "geometry"]].to_file(
        outdir / "microclusters_hdbscan.geojson", driver="GeoJSON"
    )

    # 4. Poligonos hibridos del prototipo (referencia de lo que da hoy el algoritmo)
    poligonos = gpd.read_file(PROTOTIPO / "poligonos" / "poligonos_alternativas.geojson")
    poligonos_macro = poligonos[
        (poligonos["macrozona"] == macro) & (poligonos["metodo"] == "concave_hull_r05_buffer")
    ]
    if len(poligonos_macro):
        poligonos_macro.to_file(outdir / "poligonos_prototipo_v1.geojson", driver="GeoJSON")

    # 5. Elipses editoriales fase16, si existen para esta macrozona
    clave = MAPA_EDITORIAL_FASE16.get(macro)
    if clave:
        subzonas = gpd.read_file(SUBZONAS_FASE16)
        subzonas["mapa_limpio"] = subzonas["mapa"].map(limpiar_texto)
        capa = subzonas[subzonas["mapa_limpio"].str.contains(clave, case=False, na=False)]
        if len(capa):
            capa.drop(columns="mapa_limpio").to_file(
                outdir / "elipse_editorial_fase16.geojson", driver="GeoJSON"
            )

    # 6. Semilla Fase 13
    semilla = pd.read_csv(SEMILLA_CSV)
    semilla["macrozona_norm"] = semilla["polo"].map(limpiar_texto).replace(
        {"Abasto": "Avenida Corrientes"}
    )
    sub_semilla = semilla[semilla["macrozona_norm"] == macro].dropna(subset=["lat", "lon"])
    if len(sub_semilla):
        gdf_semilla = gpd.GeoDataFrame(
            sub_semilla, geometry=gpd.points_from_xy(sub_semilla["lon"], sub_semilla["lat"]),
            crs=CRS_GEO,
        )
        gdf_semilla[["polo", "subzona", "nombre_lugar", "estado_consolidado", "geometry"]].to_file(
            outdir / "semilla_fase13.geojson", driver="GeoJSON"
        )

    leeme = f"""# Kit de edicion — {macro}

Generado por `preparar_kit_edicion.py` (solo lectura, experimental).

Capas incluidas (cargar en QGIS o geojson.io en este orden sugerido):

1. `callejero_referencia.geojson` — tramos de calle GCBA (base para trazar el contorno
   siguiendo calles reales).
2. `entidades_universo_v1.geojson` — {len(gdf_ent)} entidades del universo V1 (oferta
   registrada F01+F02) asignadas hoy a esta macrozona. Coloreadas por `cluster_id` en tu
   herramienta (-1 = ruido).
3. `microclusters_hdbscan.geojson` — mismos puntos, solo con el cluster (capa liviana).
4. `poligonos_prototipo_v1.geojson` — poligonos que ya produce el prototipo V1 (metodo
   concave_hull_r05_buffer) con el contenedor actual (hull de semilla). Sirve para ver
   donde el algoritmo detecto nucleos y decidir si el contorno editorial nuevo los separa
   bien o los agrupa distinto.
5. `elipse_editorial_fase16.geojson` — {"incluida" if clave else "NO existe para esta macrozona"}:
   demarcacion editorial previa (aproximada, no oficial) usada en los informes hasta Fase 25.
6. `semilla_fase13.geojson` — puntos curados a mano (Fase 13); todo poligono nuevo deberia
   contenerlos (es el control de calidad minimo, ver Etapa Infra-6).

Al terminar de editar, exportar el poligono nuevo como GeoJSON y pasarlo por
`normalizar_capa_editorial.py` (Etapa Infra-4) para completar los atributos del esquema
(`02_DISENO_CAPA_EDITORIAL.md`) antes de sumarlo a `macrozonas_editorial_vN.geojson`.
"""
    (outdir / "LEEME.md").write_text(leeme, encoding="utf-8")
    print(f"{macro}: kit en {outdir} "
          f"({len(gdf_ent)} entidades, {len(calles_zona)} tramos de calle)")


MACROZONAS_VALIDAS = [
    "Palermo", "Avenida Corrientes", "San Telmo", "Belgrano", "Chacarita",
    "Villa Crespo", "Avenida Caseros / Barracas", "Costanera Norte",
    "Caballito", "Microcentro y Centro", "Puerto Madero", "Recoleta",
]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("macrozona", nargs="?", help="Nombre exacto de la macrozona")
    parser.add_argument("--todas", action="store_true", help="Generar el kit para las 12 macrozonas")
    args = parser.parse_args()

    if args.todas:
        for macro in MACROZONAS_VALIDAS:
            exportar_kit(macro)
    elif args.macrozona:
        exportar_kit(args.macrozona)
    else:
        sys.exit("Especificar una macrozona o --todas.")


if __name__ == "__main__":
    main()
