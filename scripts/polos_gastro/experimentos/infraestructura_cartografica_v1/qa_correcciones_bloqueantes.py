# -*- coding: utf-8 -*-
"""Etapa Cal-4 — QA unicamente sobre las 4 macrozonas modificadas (Microcentro, Belgrano,
Costanera Norte, Chacarita) + su interaccion con las vecinas (Avenida Corrientes, Palermo,
Villa Crespo, Recoleta, Caballito) que NO se tocaron.

EXPERIMENTAL. Controles pedidos: solapamientos, huecos, geometrias invalidas, cobertura,
entidades duplicadas (en mas de una macrozona), entidades fuera de contenedor (que antes
estaban dentro y la correccion dejo afuera).

Uso:
    .venv/Scripts/python.exe scripts/polos_gastro/historico/experimentos/infraestructura_cartografica_v1/qa_correcciones_bloqueantes.py
"""

from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.validation import explain_validity

REPO = Path(__file__).resolve().parents[4]
SALIDA = REPO / "outputs/polos_gastro/historico/experimentos/infraestructura_cartografica_v1"
CORRECCIONES_DIR = SALIDA / "correcciones_bloqueantes"
PROTOTIPO = REPO / "outputs/polos_gastro/historico/experimentos/pipeline_microzonas_v1"

CRS_METRICO = "EPSG:5347"
IDS_MODIFICADOS = ["MZ_MICROCENTRO_Y_CENTRO", "MZ_BELGRANO", "MZ_COSTANERA_NORTE", "MZ_CHACARITA"]
IDS_VECINOS_A_REVISAR = [
    "MZ_AVENIDA_CORRIENTES", "MZ_PALERMO", "MZ_PALERMO_SOHO", "MZ_PALERMO_HOLLYWOOD",
    "MZ_VILLA_CRESPO", "MZ_RECOLETA", "MZ_CABALLITO",
]


def cargar_universo() -> gpd.GeoDataFrame:
    ent = pd.read_csv(
        PROTOTIPO / "universo" / "universo_entidades_v1.csv", dtype={"id_ubicacion": str}
    )
    ent = ent[ent["apta_clustering"]].copy()
    return gpd.GeoDataFrame(
        ent, geometry=gpd.points_from_xy(ent["lon"], ent["lat"]), crs="EPSG:4326"
    ).to_crs(CRS_METRICO)


def construir_capa_post_correccion() -> gpd.GeoDataFrame:
    base = gpd.read_file(SALIDA / "macrozonas_v1_experimental.geojson")
    correcciones = gpd.read_file(CORRECCIONES_DIR / "geometrias_corregidas.geojson")
    base = base.set_index("id")
    for _, fila in correcciones.iterrows():
        base.loc[fila["id"], "geometry"] = fila["geometry"]
    return base.reset_index()


def main() -> None:
    gdf = construir_capa_post_correccion()
    gdf_m = gdf.to_crs(CRS_METRICO)
    universo_m = cargar_universo()

    print("=" * 72)
    print("QA — solo macrozonas modificadas (Microcentro, Belgrano, Costanera Norte, Chacarita)")
    print("=" * 72)

    # --- Geometrias validas + huecos ---
    print("\n1) VALIDEZ Y HUECOS")
    for id_ in IDS_MODIFICADOS:
        geom = gdf_m[gdf_m["id"] == id_].geometry.iloc[0]
        valido = geom.is_valid
        n_huecos = (
            len(geom.interiors) if geom.geom_type == "Polygon"
            else sum(len(p.interiors) for p in geom.geoms) if geom.geom_type == "MultiPolygon"
            else 0
        )
        estado = "OK" if valido else f"INVALIDA: {explain_validity(geom)}"
        print(f"  {id_}: {estado}; huecos={n_huecos}")

    # --- Solapamientos entre modificadas y vecinas (incluye Corrientes) ---
    print("\n2) SOLAPAMIENTOS (modificadas x vecinas relevantes, umbral > 2% del area menor)")
    ids_relevantes = list(set(IDS_MODIFICADOS + IDS_VECINOS_A_REVISAR))
    sub = gdf_m[gdf_m["id"].isin(ids_relevantes)]
    ids, nombres, geoms = sub["id"].tolist(), sub["nombre"].tolist(), sub.geometry.tolist()
    solapes_detectados = []
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            if ids[i] not in IDS_MODIFICADOS and ids[j] not in IDS_MODIFICADOS:
                continue  # solo nos interesan pares donde participa algo modificado
            inter = geoms[i].intersection(geoms[j])
            if inter.area <= 0:
                continue
            area_min = min(geoms[i].area, geoms[j].area)
            pct = 100.0 * inter.area / area_min
            if pct > 2.0:
                n_ent = len(universo_m[universo_m.within(inter)])
                solapes_detectados.append(
                    f"{ids[i]} ({nombres[i]}) x {ids[j]} ({nombres[j]}): {pct:.1f}% "
                    f"del area menor, {n_ent} entidades en el solape"
                )
    if solapes_detectados:
        for s in solapes_detectados:
            print(f"  [!] {s}")
    else:
        print("  Ninguno por encima del 2% (el solapamiento Corrientes/Microcentro quedo resuelto).")

    # --- Entidades duplicadas: en mas de una macrozona-contenedor de clustering ---
    print("\n3) ENTIDADES DUPLICADAS (en mas de una macrozona nivel polo, es_contenedor=true)")
    polos = gdf_m[(gdf_m["nivel"] == "polo") & (gdf_m["es_contenedor_clustering"])]
    conteo = pd.Series(0, index=universo_m.index)
    for _, fila in polos.iterrows():
        dentro = universo_m.within(fila.geometry)
        conteo += dentro.astype(int)
    n_duplicadas = int((conteo > 1).sum())
    print(f"  Entidades en >=2 macrozonas-polo simultaneamente: {n_duplicadas} "
          f"(antes de esta correccion: 406 solo por Corrientes/Microcentro)")

    # --- Entidades que quedaron fuera tras la correccion (antes dentro) ---
    print("\n4) ENTIDADES QUE QUEDARON FUERA TRAS LA CORRECCION")
    base_original = gpd.read_file(SALIDA / "macrozonas_v1_experimental.geojson").to_crs(CRS_METRICO)
    for id_ in IDS_MODIFICADOS:
        geom_antes = base_original[base_original["id"] == id_].geometry.iloc[0]
        geom_despues = gdf_m[gdf_m["id"] == id_].geometry.iloc[0]
        antes_ids = set(universo_m[universo_m.within(geom_antes)].index)
        despues_ids = set(universo_m[universo_m.within(geom_despues)].index)
        perdidas = antes_ids - despues_ids
        ganadas = despues_ids - antes_ids
        # Cuantas de las "perdidas" siguen cubiertas por OTRA macrozona (no quedan huerfanas)
        otras_geoms = gdf_m[~gdf_m["id"].isin([id_])].geometry
        cobertura_otras = gpd.GeoSeries(list(otras_geoms), crs=CRS_METRICO).union_all()
        perdidas_gdf = universo_m.loc[list(perdidas)] if perdidas else universo_m.iloc[0:0]
        huerfanas = perdidas_gdf[~perdidas_gdf.within(cobertura_otras)] if len(perdidas_gdf) else perdidas_gdf
        print(f"  {id_}: -{len(perdidas)} / +{len(ganadas)} entidades "
              f"({len(huerfanas)} de las perdidas quedan sin ninguna macrozona)")

    # --- Cobertura total de CABA (nivel polo, contenedores de clustering) ---
    print("\n5) COBERTURA DE CABA (nivel polo, contenedores de clustering)")
    from shapely.ops import unary_union
    comunas_m = gpd.read_file(REPO / "PolosGastro/cartografia/comunas_caba.geojson").to_crs(CRS_METRICO)
    caba_m = comunas_m.union_all()
    cubierto = unary_union(polos.geometry.tolist())
    pct = 100.0 * cubierto.intersection(caba_m).area / caba_m.area
    print(f"  Cobertura: {pct:.2f}% (antes de estas correcciones: 19.66%)")

    print("\n" + "=" * 72)
    print("Fin del QA de macrozonas modificadas.")


if __name__ == "__main__":
    main()
