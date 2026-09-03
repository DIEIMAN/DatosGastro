# -*- coding: utf-8 -*-
"""QA de `macrozonas_v1_experimental.geojson` (Tarea 4 del pedido de macrozonas_v1).

EXPERIMENTAL. Reusa los gates/banderas genericos de `qa_capa_editorial.py` (geometria,
atributos, jerarquia) y agrega los controles pedidos especificamente para esta capa:

  - entidades contenidas: cuantas entidades del universo V1 caen dentro de cada macrozona
  - entidades cercanas fuera: entidades a <= 150 m del borde pero FUERA del poligono
    (candidatas a que el limite este mal trazado, no ruido a ignorar)
  - areas demasiado grandes: bandera > 600 ha (una macrozona, no una microzona: escala
    distinta a los 35 ha del prototipo de clustering)
  - areas demasiado chicas: bandera < 40 ha
  - solapamiento entre macrozonas nivel 'polo' que NO son padre/hijo (ya lo hace
    qa_capa_editorial, se reporta aca con detalle de que entidades quedan en la zona
    de solape, para facilitar la revision)

Uso:
    .venv/Scripts/python.exe scripts/polos_gastro/historico/experimentos/infraestructura_cartografica_v1/qa_macrozonas_v1.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from qa_capa_editorial import banderas as banderas_genericas  # noqa: E402
from qa_capa_editorial import gates_duros  # noqa: E402

REPO = Path(__file__).resolve().parents[4]
SALIDA = REPO / "outputs/polos_gastro/historico/experimentos/infraestructura_cartografica_v1"
PROTOTIPO = REPO / "outputs/polos_gastro/historico/experimentos/pipeline_microzonas_v1"

CRS_METRICO = "EPSG:5347"
AREA_MAX_HA = 600.0
AREA_MIN_HA = 40.0
DIST_CERCANIA_M = 150.0


def cargar_universo() -> gpd.GeoDataFrame:
    ent = pd.read_csv(
        PROTOTIPO / "universo" / "universo_entidades_v1.csv", dtype={"id_ubicacion": str}
    )
    ent = ent[ent["apta_clustering"]].copy()
    return gpd.GeoDataFrame(
        ent, geometry=gpd.points_from_xy(ent["lon"], ent["lat"]), crs="EPSG:4326"
    ).to_crs(CRS_METRICO)


def gates_y_banderas_tamanio(gdf_m: gpd.GeoDataFrame) -> tuple[list[str], list[str]]:
    errores, avisos = [], []
    for _, fila in gdf_m.iterrows():
        if fila["nivel"] != "polo" or not fila.get("es_contenedor_clustering", True):
            continue  # Palermo (contextual) no se juzga con la escala de contenedores
        area_ha = fila.geometry.area / 10_000.0
        if area_ha > AREA_MAX_HA:
            avisos.append(f"AREA_GRANDE: {fila['id']} ({fila['nombre']}) = {area_ha:.1f} ha "
                          f"(> {AREA_MAX_HA} ha)")
        if area_ha < AREA_MIN_HA:
            avisos.append(f"AREA_CHICA: {fila['id']} ({fila['nombre']}) = {area_ha:.1f} ha "
                          f"(< {AREA_MIN_HA} ha)")
    return errores, avisos


def entidades_contenidas_y_cercanas(gdf_m: gpd.GeoDataFrame, universo: gpd.GeoDataFrame) -> pd.DataFrame:
    filas = []
    for _, fila in gdf_m.iterrows():
        geom = fila.geometry
        dentro = universo[universo.within(geom)]
        cerca_fuera = universo[
            universo.within(geom.buffer(DIST_CERCANIA_M)) & ~universo.within(geom)
        ]
        filas.append({
            "id": fila["id"], "nombre": fila["nombre"], "nivel": fila["nivel"],
            "area_ha": round(geom.area / 10_000.0, 1),
            "n_entidades_contenidas": len(dentro),
            "densidad_ha": round(len(dentro) / (geom.area / 10_000.0), 2),
            "n_entidades_cercanas_fuera": len(cerca_fuera),
        })
    return pd.DataFrame(filas)


def solapamientos_detallados(gdf_m: gpd.GeoDataFrame, universo: gpd.GeoDataFrame) -> list[str]:
    avisos = []
    polos = gdf_m[(gdf_m["nivel"] == "polo") & (gdf_m["es_contenedor_clustering"])]
    ids, geoms = polos["id"].tolist(), polos.geometry.tolist()
    nombres = polos["nombre"].tolist()
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            inter = geoms[i].intersection(geoms[j])
            if inter.area <= 0:
                continue
            area_min = min(geoms[i].area, geoms[j].area)
            pct = 100.0 * inter.area / area_min
            if pct > 2.0:
                n_ent_solape = len(universo[universo.within(inter)])
                avisos.append(
                    f"SOLAPE: {ids[i]} ({nombres[i]}) x {ids[j]} ({nombres[j]}): "
                    f"{pct:.1f}% del area menor, {n_ent_solape} entidades en la zona "
                    "de solape (quedarian duplicadas si ambas macrozonas clusterizan)"
                )
    return avisos


def main() -> None:
    import sys
    nombre_archivo = sys.argv[1] if len(sys.argv) > 1 else "macrozonas_v1_experimental.geojson"
    ruta = SALIDA / nombre_archivo
    gdf = gpd.read_file(ruta)
    gdf_m = gdf.to_crs(CRS_METRICO)
    universo = cargar_universo()

    errores = gates_duros(gdf)
    avisos = banderas_genericas(gdf)
    errores_tam, avisos_tam = gates_y_banderas_tamanio(gdf_m)
    avisos_solape = solapamientos_detallados(gdf_m, universo)

    tabla_contencion = entidades_contenidas_y_cercanas(gdf_m, universo)
    sufijo = Path(nombre_archivo).stem
    tabla_contencion.to_csv(SALIDA / f"qa_contencion_entidades_{sufijo}.csv", index=False)

    print(f"QA de {ruta.name} — {len(gdf)} features")
    print("=" * 72)
    print(f"\nGATES DUROS (genericos): {len(errores)}")
    for e in errores:
        print(f"  [X] {e}")
    print(f"\nGATES DUROS (tamanio): {len(errores_tam)}")
    for e in errores_tam:
        print(f"  [X] {e}")
    print(f"\nBANDERAS (genericas): {len(avisos)}")
    for a in avisos:
        print(f"  [!] {a}")
    print(f"\nBANDERAS (tamanio): {len(avisos_tam)}")
    for a in avisos_tam:
        print(f"  [!] {a}")
    print(f"\nBANDERAS (solapamiento detallado, no generico): {len(avisos_solape)}")
    for a in avisos_solape:
        print(f"  [!] {a}")

    print(f"\nContencion de entidades por macrozona (-> qa_contencion_entidades.csv):")
    print(tabla_contencion.to_string(index=False))

    total_errores = len(errores) + len(errores_tam)
    print("\n" + "=" * 72)
    if total_errores:
        print(f"RESULTADO: NO PUBLICABLE — {total_errores} gate(s) duro(s) sin resolver.")
    else:
        print("RESULTADO: pasa los gates duros. Revisar banderas antes de aprobar version.")


if __name__ == "__main__":
    main()
