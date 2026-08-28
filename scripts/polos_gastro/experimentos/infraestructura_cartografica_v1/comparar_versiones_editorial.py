# -*- coding: utf-8 -*-
"""Etapa Infra-5 — Diff automatico entre dos versiones de la capa editorial.

EXPERIMENTAL. Dados dos GeoJSON (`macrozonas_editorial_vN...` y su sucesor), reporta por
`id`: agregadas, eliminadas, geometria modificada (umbral: diferencia simetrica de area
> 1% del area original) y atributos modificados. Pensado para verificar que el
CHANGELOG.md escrito a mano coincide con lo que realmente cambio (Etapa Infra-5).

Uso:
    .venv/Scripts/python.exe scripts/polos_gastro/experimentos/infraestructura_cartografica_v1/comparar_versiones_editorial.py v1.geojson v2.geojson
"""

from __future__ import annotations

import argparse

import geopandas as gpd

CRS_METRICO = "EPSG:5347"
UMBRAL_CAMBIO_GEOM_PCT = 1.0

CAMPOS_ATRIBUTO = [
    "nombre", "nivel", "polo_id", "tipo_geometria", "metodo_construccion",
    "calles_limite", "fuente", "estado_revision", "nivel_confianza", "version_capa",
]


def cargar(ruta: str) -> gpd.GeoDataFrame:
    gdf = gpd.read_file(ruta)
    if "id" not in gdf.columns:
        raise SystemExit(f"{ruta}: falta la columna 'id' (esquema Infra-2).")
    return gdf.set_index("id").to_crs(CRS_METRICO)


def comparar(ruta_a: str, ruta_b: str) -> None:
    a = cargar(ruta_a)
    b = cargar(ruta_b)

    ids_a, ids_b = set(a.index), set(b.index)
    agregadas = sorted(ids_b - ids_a)
    eliminadas = sorted(ids_a - ids_b)
    comunes = sorted(ids_a & ids_b)

    geom_modificadas, atributos_modificados, sin_cambios = [], [], []
    for id_ in comunes:
        geom_a, geom_b = a.loc[id_, "geometry"], b.loc[id_, "geometry"]
        area_a = geom_a.area
        dif_area = geom_a.symmetric_difference(geom_b).area
        pct_dif = 100.0 * dif_area / area_a if area_a > 0 else (0.0 if dif_area == 0 else 100.0)
        cambio_geom = pct_dif > UMBRAL_CAMBIO_GEOM_PCT

        cambios_attr = [
            campo for campo in CAMPOS_ATRIBUTO
            if campo in a.columns and campo in b.columns
            and str(a.loc[id_, campo]) != str(b.loc[id_, campo])
        ]

        if cambio_geom:
            geom_modificadas.append((id_, round(pct_dif, 1)))
        if cambios_attr:
            atributos_modificados.append((id_, cambios_attr))
        if not cambio_geom and not cambios_attr:
            sin_cambios.append(id_)

    print(f"Comparando {ruta_a} -> {ruta_b}")
    print(f"\nAgregadas ({len(agregadas)}):")
    for id_ in agregadas:
        print(f"  + {id_} ({b.loc[id_, 'nombre']})")
    print(f"\nEliminadas ({len(eliminadas)}):")
    for id_ in eliminadas:
        print(f"  - {id_} ({a.loc[id_, 'nombre']})")
    print(f"\nGeometria modificada ({len(geom_modificadas)}):")
    for id_, pct in geom_modificadas:
        print(f"  ~ {id_}: {pct}% de diferencia simetrica de area")
    print(f"\nAtributos modificados ({len(atributos_modificados)}):")
    for id_, campos in atributos_modificados:
        print(f"  ~ {id_}: {', '.join(campos)}")
    print(f"\nSin cambios: {len(sin_cambios)} de {len(comunes)} features comunes")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version_anterior")
    parser.add_argument("version_nueva")
    args = parser.parse_args()
    comparar(args.version_anterior, args.version_nueva)


if __name__ == "__main__":
    main()
