# -*- coding: utf-8 -*-
"""Etapa Infra-4 — Construccion de UN poligono editorial real (Palermo Soho).

EXPERIMENTAL / BORRADOR. Unico caso donde el inventario (Infra-1) encontro las 4 calles
limite documentadas explicitamente (ficha PG001A): Scalabrini Ortiz, Cordoba, Juan B.
Justo y Santa Fe. Este script traza el poligono real usando esas calles del callejero
GCBA (no una elipse, no un hull de semilla), como caso de prueba de la Etapa Infra-4.

Metodo (documentado para revision humana, no definitivo):
1. Extraer los tramos de cada avenida limite del callejero, acotados al entorno de
   Palermo (evita capturar homonimos en otras zonas de la Ciudad).
2. Ajustar una recta (cuadrados minimos) a los vertices de cada avenida y extenderla
   varios km: las avenidas son casi rectas en esta escala, y una recta extendida sirve
   como "corte" para particionar el plano.
3. Particionar un rectangulo amplio de Palermo con las 4 rectas (Scalabrini Ortiz,
   Cordoba, Juan B. Justo, Santa Fe para Soho; se corre tambien con Dorrego en vez de
   Scalabrini para Palermo Hollywood, como control cruzado).
4. De las piezas resultantes, quedarse con la que contiene el centro editorial de la
   elipse de fase16 para esa subzona (unico dato ya validado que dice "el nucleo de Soho
   esta aca"; NO se usa como geometria final, solo como localizador de la pieza correcta).
5. Recortar contra el limite de CABA.

Salida: `outputs/.../infraestructura_cartografica_v1/poligono_real_palermo_soho.geojson`
(borrador, pendiente de revision editorial) + el mismo control para Palermo Hollywood
(comparacion, no pedido explicitamente pero gratis con el mismo metodo).

Uso:
    .venv/Scripts/python.exe scripts/polos_gastro/experimentos/infraestructura_cartografica_v1/construir_poligono_real_palermo_soho.py
"""

from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import numpy as np
from shapely.geometry import LineString, Point, box
from shapely.ops import split, unary_union

REPO = Path(__file__).resolve().parents[4]
CALLEJERO = REPO / "outputs/polos_gastro/fase15_mapas_callejeros_v3/assets/callejero_gcba_2026_06_02.geojson"
COMUNAS = REPO / "PolosGastro/cartografia/comunas_caba.geojson"
SALIDA = REPO / "outputs/polos_gastro/experimentos/infraestructura_cartografica_v1"

CRS_GEO = "EPSG:4326"
CRS_METRICO = "EPSG:5347"

# Bounding box amplio de Palermo (evita capturar tramos homonimos en otras zonas)
BBOX_PALERMO = (-58.455, -34.605, -58.400, -34.565)  # minx, miny, maxx, maxy

CALLES = {
    "santa_fe": "SANTA FE AV.",
    "cordoba": "CORDOBA AV.",
    "jb_justo": "JUSTO, JUAN B. AV.",
    "scalabrini_ortiz": "SCALABRINI ORTIZ, RAUL AV.",
    "dorrego": "DORREGO AV.",
}

# Centros editoriales de fase16 (subzonas_editoriales_geometrias.geojson), en EPSG:4326.
# Se usan SOLO como localizador de la pieza correcta tras partir el plano, no como geometria.
CENTRO_SOHO = Point(-58.4235, -34.5880)
CENTRO_HOLLYWOOD = Point(-58.4350, -34.5850)

EXTENSION_RECTA_M = 4000.0


def recta_ajustada(gdf_calle: gpd.GeoDataFrame) -> LineString:
    """Ajusta una recta (cuadrados minimos) a todos los vertices de la calle y la
    extiende +/- EXTENSION_RECTA_M para usarla como corte del plano."""
    coords = []
    for geom in gdf_calle.geometry:
        coords.extend(list(geom.coords))
    xy = np.array(coords)
    x, y = xy[:, 0], xy[:, 1]

    # Regresion total (PCA de 1 componente): evita el problema de rectas verticales
    # que arruinaria un ajuste y = a + bx clasico.
    centro = xy.mean(axis=0)
    _, _, vt = np.linalg.svd(xy - centro)
    direccion = vt[0]

    p1 = centro - direccion * EXTENSION_RECTA_M
    p2 = centro + direccion * EXTENSION_RECTA_M
    return LineString([p1, p2])


def cargar_calle(callejero: gpd.GeoDataFrame, nomoficial: str) -> gpd.GeoDataFrame:
    sub = callejero[callejero["nomoficial"] == nomoficial]
    if not len(sub):
        raise SystemExit(f"No se encontraron tramos para '{nomoficial}'")
    return sub


def construir_pieza(rectas_m: dict[str, LineString], bbox_m, centro_geo: Point,
                    nombres_lados: list[str]) -> "shapely.geometry.Polygon":
    poligono_base = box(*bbox_m)
    lineas = unary_union([rectas_m[n] for n in nombres_lados])
    piezas = split(poligono_base, lineas)
    centro_m = gpd.GeoSeries([centro_geo], crs=CRS_GEO).to_crs(CRS_METRICO).iloc[0]
    candidatas = [g for g in piezas.geoms if g.contains(centro_m)]
    if len(candidatas) != 1:
        raise SystemExit(
            f"Particion ambigua para {nombres_lados}: {len(candidatas)} piezas contienen "
            "el centro editorial (se esperaba 1). Revisar bbox o rectas."
        )
    return candidatas[0]


def main() -> None:
    SALIDA.mkdir(parents=True, exist_ok=True)
    callejero = gpd.read_file(CALLEJERO)

    calles_m = {}
    for clave, nomoficial in CALLES.items():
        sub = cargar_calle(callejero, nomoficial)
        sub_zona = sub.cx[BBOX_PALERMO[0]:BBOX_PALERMO[2], BBOX_PALERMO[1]:BBOX_PALERMO[3]]
        if not len(sub_zona):
            raise SystemExit(f"'{nomoficial}' no tiene tramos dentro del bbox de Palermo")
        calles_m[clave] = sub_zona.to_crs(CRS_METRICO)

    rectas_m = {clave: recta_ajustada(gdf) for clave, gdf in calles_m.items()}

    bbox_geo = box(*BBOX_PALERMO)
    bbox_m = gpd.GeoSeries([bbox_geo], crs=CRS_GEO).to_crs(CRS_METRICO).iloc[0].bounds

    comunas = gpd.read_file(COMUNAS).to_crs(CRS_METRICO)
    limite_caba = comunas.union_all()

    resultados = {}
    for nombre, centro, lados in [
        ("palermo_soho", CENTRO_SOHO,
         ["santa_fe", "cordoba", "jb_justo", "scalabrini_ortiz"]),
        ("palermo_hollywood", CENTRO_HOLLYWOOD,
         ["santa_fe", "cordoba", "jb_justo", "dorrego"]),
    ]:
        pieza = construir_pieza(rectas_m, bbox_m, centro, lados)
        pieza_recortada = pieza.intersection(limite_caba)
        resultados[nombre] = pieza_recortada
        area_ha = pieza_recortada.area / 10_000.0
        print(f"{nombre}: area {area_ha:.1f} ha, calles limite = {lados}")

        gdf_out = gpd.GeoDataFrame(
            [{
                "id": f"MZ_{nombre.upper()}",
                "nombre": nombre.replace('_', ' ').title(),
                "nivel": "subzona",
                "polo_id": "MZ_PALERMO",
                "tipo_geometria": "poligono_real",
                "metodo_construccion": (
                    f"Recta de cuadrados minimos sobre tramos reales del callejero GCBA "
                    f"para cada calle limite ({', '.join(CALLES[l] for l in lados)}); "
                    "particion del plano y seleccion de la pieza que contiene el centro "
                    "editorial de fase16 (localizador, no geometria final)."
                ),
                "calles_limite": ", ".join(CALLES[l] for l in lados),
                "fuente": "ficha:PG001A_PALERMO_SOHO" if nombre == "palermo_soho"
                          else "ficha:PG001B_PALERMO_HOLLYWOOD",
                "estado_revision": "borrador",
                "nivel_confianza": "alta",
                "version_capa": "v1_borrador",
                "geometry": pieza_recortada,
            }],
            crs=CRS_METRICO,
        )
        gdf_out.to_crs(CRS_GEO).to_file(
            SALIDA / f"poligono_real_{nombre}.geojson", driver="GeoJSON"
        )

    print(f"\nSalidas en {SALIDA}")


if __name__ == "__main__":
    main()
