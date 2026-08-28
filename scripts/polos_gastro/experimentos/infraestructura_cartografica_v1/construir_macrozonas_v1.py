# -*- coding: utf-8 -*-
"""Construccion de `macrozonas_v1_experimental.geojson` (12 polos + 2 subzonas Palermo).

EXPERIMENTAL. Primera version operativa de la capa editorial (esquema de
`02_DISENO_CAPA_EDITORIAL.md`). Cada macrozona se construye con el MEJOR metodo posible
segun lo que exista (orden de prioridad pedido explicitamente):

  1. calles_reales      : ya construido en la Etapa Infra-4 (solo Palermo Soho/Hollywood,
                           las 2 fichas con las 4 calles limite documentadas) -> alta
  2. barrio_semilla      : barrio oficial GCBA recortado a un buffer alrededor de los
                           puntos semilla depurados (excluye apartados/duplicados
                           probables) -> media
  3. barrio_solo         : barrio oficial GCBA completo, sin recorte (cuando el barrio ya
                           es del tamano correcto, p. ej. Puerto Madero, o cuando no hay
                           semilla utilizable para recortar, p. ej. Microcentro) -> media
  4. fase16_heredado     : union de las elipses editoriales ya existentes (fase16),
                           recortada al barrio -> baja (es una aproximacion heredada, no
                           una construccion nueva)
  5. corredor_real       : buffer sobre el eje real de una avenida (callejero GCBA),
                           acotado a un entorno donde esta la evidencia -> media o baja
                           segun cuanta evidencia de semilla exista en ese entorno

NINGUN metodo se elige por conveniencia oculta: cada macrozona documenta su metodo,
fuente y nivel de confianza en el propio feature (y en detalle en
`METODOLOGIA_MACROZONAS_V1.md`).

Uso:
    .venv/Scripts/python.exe scripts/polos_gastro/experimentos/infraestructura_cartografica_v1/construir_macrozonas_v1.py
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import box
from shapely.ops import unary_union

REPO = Path(__file__).resolve().parents[4]
SALIDA = REPO / "outputs/polos_gastro/experimentos/infraestructura_cartografica_v1"
CALLEJERO_PATH = REPO / "outputs/polos_gastro/fase15_mapas_callejeros_v3/assets/callejero_gcba_2026_06_02.geojson"
BARRIOS_PATH = REPO / "PolosGastro/cartografia/barrios_caba.geojson"
COMUNAS_PATH = REPO / "PolosGastro/cartografia/comunas_caba.geojson"
SUBZONAS_FASE16_PATH = REPO / "outputs/polos_gastro/fase16_mapas_editoriales_v4/tablas/subzonas_editoriales_geometrias.geojson"
SEMILLA_CSV = REPO / "outputs/polos_gastro/fase13_mapas/tablas/locales_para_mapa_revision.csv"

CRS_GEO = "EPSG:4326"
CRS_METRICO = "EPSG:5347"

# Misma regla de depuracion de sedes apartadas que el prototipo V1
# (config.py, macrozonas.radio_max_semilla_m): evita que sedes mal geocodificadas
# distorsionen el buffer.
RADIO_MAX_SEMILLA_M = 2300.0


def limpiar_texto(s) -> str:
    return str(s).replace("�", "ñ")


def limpiar_geometria(geom):
    """Normaliza el resultado de intersecciones/uniones a Polygon/MultiPolygon valido.

    `intersection()` entre un buffer de puntos y un barrio puede devolver una
    GeometryCollection (mezcla de poligonos con lineas/puntos de tangencia) o un
    poligono con autointersecciones menores; ambos casos rompen el gate G1 del QA."""
    if geom.geom_type == "GeometryCollection":
        poligonos = [g for g in geom.geoms if g.geom_type in ("Polygon", "MultiPolygon")]
        geom = unary_union(poligonos) if poligonos else geom
    if not geom.is_valid:
        geom = geom.buffer(0)
    return geom


# ---------------------------------------------------------------------------
# Config por polo: metodo + parametros. Editable y auditable a simple vista.
# ---------------------------------------------------------------------------

CONFIG_POLOS = {
    "Palermo": {
        "metodo": "barrio_solo", "barrio": "Palermo",
        "nivel_confianza": "baja", "es_contenedor_clustering": False,
        "fuente": ["barrio_oficial:Palermo"],
        "observaciones": (
            "Contorno contextual (polo completo), NO usado como contenedor de "
            "clustering: para eso se usan las subzonas Palermo Soho y Palermo Hollywood "
            "(alta confianza, calles reales). Las Cañitas, Palermo Chico y Palermo "
            "Nuevo/Botanico quedan sin subzona propia en esta v1."
        ),
    },
    "San Telmo": {
        "metodo": "barrio_semilla", "barrio": "San Telmo", "radio_semilla_m": 700,
        "nivel_confianza": "media",
        "fuente": ["barrio_oficial:San Telmo", "semilla_fase13:San Telmo"],
        "observaciones": (
            "Barrio oficial recortado al entorno de los puntos semilla (700 m). La "
            "validacion de la Etapa V2-3 encontro 2 clusters HDBSCAN fuera de toda "
            "elipse editorial de San Telmo (uno al norte, uno al sur): revisar si "
            "este nuevo contorno los deja afuera correctamente o si el radio de 700 m "
            "los sigue incluyendo."
        ),
    },
    "Belgrano": {
        "metodo": "fase16_heredado", "clave_fase16": "Belgrano", "barrio": "Belgrano",
        "nivel_confianza": "baja",
        "fuente": ["fase16_elipses_editoriales:Belgrano", "barrio_oficial:Belgrano"],
        "observaciones": (
            "Union de las 4 elipses de fase16 (Barrio Chino, Bajo Belgrano, Belgrano R, "
            "Cabildo/Juramento), recortada al barrio oficial. Son elipses dibujadas a "
            "mano (Infra-1): esta macrozona hereda esa aproximacion, no es una "
            "construccion nueva. La validacion (V2-3) encontro que el cluster "
            "dominante de Belgrano probablemente mezcla las 3 identidades (Barrio "
            "Chino / Bajo Belgrano / Belgrano R) - revisar si conviene subdividir esta "
            "macrozona en subzonas en la proxima version."
        ),
    },
    "Chacarita": {
        "metodo": "barrio_solo", "barrio": "Chacarita",
        "nivel_confianza": "baja",
        "fuente": ["barrio_oficial:Chacarita"],
        "observaciones": (
            "Se intento 'barrio_semilla' primero, pero de los 6 puntos semilla "
            "depurados (excluido 1 duplicado_probable), 4 caen a 3-6 km del barrio "
            "administrativo Chacarita (p. ej. 'Bar Chacabuco' y 'Cantina Urondo' a la "
            "altura de Parque Patricios/Nueva Pompeya, 'Bar Roma' cerca de Almagro): "
            "el buffer(700 m) resultante no llegaba a intersectar el barrio real "
            "(area 0). Se uso el barrio oficial completo como fallback honesto en vez "
            "de forzar un recorte con semilla no confiable. Revisar sedes de estos 4 "
            "locales en la cola de calidad del universo (posible error de Fase 11/13)."
        ),
    },
    "Villa Crespo": {
        "metodo": "barrio_semilla", "barrio": "Villa Crespo", "radio_semilla_m": 700,
        "nivel_confianza": "media",
        "fuente": ["barrio_oficial:Villa Crespo", "semilla_fase13:Villa Crespo"],
        "observaciones": "Barrio oficial recortado al entorno de la semilla (700 m).",
    },
    "Puerto Madero": {
        "metodo": "barrio_solo", "barrio": "Puerto Madero",
        "nivel_confianza": "media",
        "fuente": ["barrio_oficial:Puerto Madero"],
        "observaciones": (
            "Barrio oficial completo, sin recortar: Puerto Madero es un barrio "
            "compacto (la peninsula de diques) que ya coincide razonablemente con la "
            "zona gastronomica; no se uso semilla porque 1 de 9 puntos semilla "
            "(Puerto Cristal) esta mal geocodificado a 6 km de distancia (Infra "
            "anterior) y hubiera distorsionado un recorte por buffer."
        ),
    },
    "Recoleta": {
        "metodo": "barrio_semilla", "barrio": "Recoleta", "radio_semilla_m": 700,
        "nivel_confianza": "media",
        "fuente": ["barrio_oficial:Recoleta", "semilla_fase13:Recoleta"],
        "observaciones": "Barrio oficial recortado al entorno de la semilla (700 m).",
    },
    "Caballito": {
        "metodo": "barrio_semilla", "barrio": "Caballito", "radio_semilla_m": 700,
        "nivel_confianza": "media",
        "fuente": ["barrio_oficial:Caballito", "semilla_fase13:Caballito"],
        "observaciones": "Barrio oficial recortado al entorno de la semilla (700 m).",
    },
    "Costanera Norte": {
        "metodo": "corredor_real", "calle": "OBLIGADO RAFAEL, AV.COSTANERA",
        "bbox": (-58.445, -34.575, -58.400, -34.535), "semiancho_m": 350,
        "nivel_confianza": "baja",
        "fuente": ["callejero_gcba:Av. Costanera Rafael Obligado"],
        "observaciones": (
            "Corredor sobre el eje real de la Costanera Rafael Obligado, NO anclado a "
            "la semilla: de los 6 puntos semilla, 1 (Puerto Cristal) esta a 6 km de "
            "distancia (mal geocodificado) y otros 2 estan marcados "
            "'zona_sucursal_a_revisar'. Esta es la macrozona con menos evidencia de "
            "las 12 (2 entidades del universo V1 caen dentro en el prototipo actual); "
            "el semiancho de 350 m es una decision editorial sin calibrar."
        ),
    },
    "Avenida Caseros / Barracas": {
        "metodo": "corredor_barrio", "calle": "CASEROS AV.", "barrio": "Barracas",
        "bbox": (-58.42, -34.655, -58.36, -34.615), "semiancho_m": 300,
        "nivel_confianza": "baja",
        "fuente": ["callejero_gcba:Av. Caseros", "barrio_oficial:Barracas"],
        "observaciones": (
            "Corredor sobre el eje real de Av. Caseros, recortado al barrio Barracas. "
            "De los 5 puntos semilla, 3 estan marcados 'duplicado_probable' y 1 "
            "'zona_sucursal_a_revisar' (Cafe Registrado, en realidad una sede de "
            "Palermo): la semilla de este polo es mayormente ruido, por eso no se usa "
            "para recortar (a diferencia de San Telmo/Chacarita/etc.)."
        ),
    },
    "Avenida Corrientes": {
        "metodo": "corredor_real", "calle": "CORRIENTES AV.",
        "bbox": (-58.42, -34.615, -58.375, -34.585), "semiancho_m": 350,
        "nivel_confianza": "media",
        "fuente": ["callejero_gcba:Av. Corrientes", "semilla_fase13:Avenida Corrientes+Abasto"],
        "observaciones": (
            "Corredor sobre el eje real de Av. Corrientes desde el entorno de Callao/9 "
            "de Julio hasta Abasto (decision editorial vigente: Abasto es subzona de "
            "este polo, no se re-litiga). El semiancho (350 m) es mayor que en otros "
            "corredores porque el polo incluye oferta a varias cuadras del eje "
            "(confirmado por la semilla de Corrientes+Abasto). La validacion (V2-3) "
            "encontro que el cluster mas grande de esta macrozona cae en San Nicolas, "
            "fuera de la elipse editorial 'Corrientes 9 de Julio-Callao': revisar si "
            "este corredor la conserva o la deja afuera."
        ),
    },
    "Microcentro y Centro": {
        "metodo": "barrio_solo", "barrio": "San Nicolas",
        "nivel_confianza": "media",
        "fuente": ["barrio_oficial:San Nicolas"],
        "observaciones": (
            "Se usa el barrio San Nicolas (el 'microcentro' tradicional) como "
            "aproximacion; la ficha PG011 dice 'Retiro y area central, sin "
            "delimitacion fina' - este contorno NO incluye Retiro. Revisar si el "
            "polo deberia extenderse hacia Retiro en una proxima version."
        ),
    },
}

MACROZONAS_SUBZONA_PALERMO = ["palermo_soho", "palermo_hollywood"]


def cargar_semilla_depurada(polo_csv_nombre: str, semilla: pd.DataFrame) -> gpd.GeoDataFrame | None:
    sub = semilla[semilla["polo"] == polo_csv_nombre].copy()
    sub = sub[sub["estado_consolidado"] != "duplicado_probable"]
    sub = sub.dropna(subset=["lat", "lon"])
    if not len(sub):
        return None
    gdf = gpd.GeoDataFrame(
        sub, geometry=gpd.points_from_xy(sub["lon"], sub["lat"]), crs=CRS_GEO
    ).to_crs(CRS_METRICO)
    if len(gdf) >= 3:
        cx, cy = gdf.geometry.x.median(), gdf.geometry.y.median()
        dist = np.hypot(gdf.geometry.x - cx, gdf.geometry.y - cy)
        gdf = gdf[dist <= RADIO_MAX_SEMILLA_M]
    return gdf if len(gdf) else None


def metodo_barrio_semilla(nombre_polo, cfg, barrios_m, semilla, caba_m):
    barrio = barrios_m[barrios_m["nombre"] == cfg["barrio"]].geometry.iloc[0]
    csv_key = "Abasto" if nombre_polo == "Avenida Corrientes" else nombre_polo
    gdf_semilla = cargar_semilla_depurada(csv_key, semilla)
    if nombre_polo == "Avenida Corrientes":
        extra = cargar_semilla_depurada("Avenida Corrientes", semilla)
        if extra is not None:
            gdf_semilla = extra if gdf_semilla is None else pd.concat([gdf_semilla, extra])
    if gdf_semilla is None or not len(gdf_semilla):
        raise ValueError(f"{nombre_polo}: sin semilla utilizable para 'barrio_semilla'")
    buffer_semilla = unary_union(gdf_semilla.buffer(cfg["radio_semilla_m"]))
    return limpiar_geometria(barrio.intersection(buffer_semilla).intersection(caba_m))


def metodo_barrio_solo(nombre_polo, cfg, barrios_m, caba_m):
    barrio = barrios_m[barrios_m["nombre"] == cfg["barrio"]].geometry.iloc[0]
    return limpiar_geometria(barrio.intersection(caba_m))


def metodo_fase16_heredado(nombre_polo, cfg, barrios_m, subzonas_fase16_m, caba_m):
    subzonas_fase16_m = subzonas_fase16_m.copy()
    subzonas_fase16_m["mapa_limpio"] = subzonas_fase16_m["mapa"].map(limpiar_texto)
    capa = subzonas_fase16_m[
        subzonas_fase16_m["mapa_limpio"].str.contains(cfg["clave_fase16"], case=False, na=False)
    ]
    if not len(capa):
        raise ValueError(f"{nombre_polo}: sin elipses de fase16 para '{cfg['clave_fase16']}'")
    union_elipses = unary_union(capa.geometry)
    barrio = barrios_m[barrios_m["nombre"] == cfg["barrio"]].geometry.iloc[0]
    return limpiar_geometria(union_elipses.intersection(barrio).intersection(caba_m))


def metodo_corredor(nombre_polo, cfg, callejero_m, caba_m, barrio_geom=None):
    minx, miny, maxx, maxy = cfg["bbox"]
    bbox_geo = box(minx, miny, maxx, maxy)
    bbox_m = gpd.GeoSeries([bbox_geo], crs=CRS_GEO).to_crs(CRS_METRICO).iloc[0]
    tramo = callejero_m[
        (callejero_m["nomoficial"] == cfg["calle"]) & callejero_m.geometry.intersects(bbox_m)
    ]
    if not len(tramo):
        raise ValueError(f"{nombre_polo}: sin tramos de '{cfg['calle']}' en el bbox")
    eje = unary_union(tramo.geometry)
    corredor = eje.buffer(cfg["semiancho_m"])
    corredor = corredor.intersection(bbox_m).intersection(caba_m)
    if barrio_geom is not None:
        corredor = corredor.intersection(barrio_geom)
    return limpiar_geometria(corredor)


def construir_todo() -> gpd.GeoDataFrame:
    barrios_m = gpd.read_file(BARRIOS_PATH).to_crs(CRS_METRICO)
    comunas_m = gpd.read_file(COMUNAS_PATH).to_crs(CRS_METRICO)
    caba_m = comunas_m.union_all()
    callejero_m = gpd.read_file(CALLEJERO_PATH).to_crs(CRS_METRICO)
    subzonas_fase16_m = gpd.read_file(SUBZONAS_FASE16_PATH).to_crs(CRS_METRICO)
    semilla = pd.read_csv(SEMILLA_CSV)

    hoy = date.today().isoformat()
    filas = []

    # --- 2 subzonas ya construidas en Infra-4 (calles reales, alta confianza) ---
    for clave, id_, nombre in [
        ("palermo_soho", "MZ_PALERMO_SOHO", "Palermo Soho"),
        ("palermo_hollywood", "MZ_PALERMO_HOLLYWOOD", "Palermo Hollywood"),
    ]:
        gdf = gpd.read_file(SALIDA / f"poligono_real_{clave}.geojson").to_crs(CRS_METRICO)
        geom = gdf.geometry.iloc[0]
        fila_previa = gdf.iloc[0].to_dict()
        filas.append({
            "id": id_, "nombre": nombre, "nivel": "subzona", "polo_id": "MZ_PALERMO",
            "es_contenedor_clustering": True, "tipo_geometria": "poligono_real",
            "metodo_construccion": fila_previa.get("metodo_construccion", ""),
            "calles_limite": fila_previa.get("calles_limite", ""),
            "fuente": fila_previa.get("fuente", ""),
            "fecha_creacion": "2026-07-08", "fecha_actualizacion": hoy,
            "autor": "Claude (asistido) - pendiente revision Diego",
            "estado_revision": "borrador", "nivel_confianza": "alta",
            "version_capa": "v1_experimental", "reemplaza_a": None,
            "contiene_semilla_ids": None,
            "observaciones": "Construido en Etapa Infra-4 (integracion experimental).",
            "geometry": geom,
        })

    # --- 12 polos segun CONFIG_POLOS ---
    for nombre_polo, cfg in CONFIG_POLOS.items():
        metodo = cfg["metodo"]
        if metodo == "barrio_semilla":
            geom = metodo_barrio_semilla(nombre_polo, cfg, barrios_m, semilla, caba_m)
        elif metodo == "barrio_solo":
            geom = metodo_barrio_solo(nombre_polo, cfg, barrios_m, caba_m)
        elif metodo == "fase16_heredado":
            geom = metodo_fase16_heredado(nombre_polo, cfg, barrios_m, subzonas_fase16_m, caba_m)
        elif metodo == "corredor_real":
            geom = metodo_corredor(nombre_polo, cfg, callejero_m, caba_m)
        elif metodo == "corredor_barrio":
            barrio_geom = barrios_m[barrios_m["nombre"] == cfg["barrio"]].geometry.iloc[0]
            geom = metodo_corredor(nombre_polo, cfg, callejero_m, caba_m, barrio_geom=barrio_geom)
        else:
            raise ValueError(f"Metodo desconocido: {metodo}")

        id_ = "MZ_" + nombre_polo.upper().replace(" ", "_").replace("/", "").replace("__", "_")
        filas.append({
            "id": id_, "nombre": nombre_polo, "nivel": "polo", "polo_id": None,
            "es_contenedor_clustering": cfg.get("es_contenedor_clustering", True),
            "tipo_geometria": (
                "poligono_aproximado" if metodo in ("barrio_semilla", "barrio_solo", "corredor_real", "corredor_barrio")
                else "elipse_editorial"
            ),
            "metodo_construccion": f"metodo={metodo}; parametros={ {k: v for k, v in cfg.items() if k not in ('fuente', 'observaciones', 'nivel_confianza', 'es_contenedor_clustering')} }",
            "calles_limite": cfg.get("calle"),
            "fuente": "; ".join(cfg["fuente"]),
            "fecha_creacion": hoy, "fecha_actualizacion": hoy,
            "autor": "Claude (asistido) - pendiente revision Diego",
            "estado_revision": "borrador", "nivel_confianza": cfg["nivel_confianza"],
            "version_capa": "v1_experimental", "reemplaza_a": None,
            "contiene_semilla_ids": None,
            "observaciones": cfg["observaciones"],
            "geometry": geom,
        })

    gdf_final = gpd.GeoDataFrame(filas, crs=CRS_METRICO)
    return gdf_final


def main() -> None:
    gdf = construir_todo()
    gdf_geo = gdf.to_crs(CRS_GEO)
    # La reproyeccion metrico->geografico puede introducir autointersecciones minimas
    # por precision de coma flotante en poligonos complejos (visto en Caballito): se
    # limpia otra vez despues de reproyectar, no solo antes.
    gdf_geo["geometry"] = gdf_geo["geometry"].apply(limpiar_geometria)
    ruta = SALIDA / "macrozonas_v1_experimental.geojson"
    gdf_geo.to_file(ruta, driver="GeoJSON")

    resumen = gdf.copy()
    resumen["area_ha"] = (resumen.geometry.area / 10_000.0).round(1)
    print(f"{len(gdf)} features -> {ruta}")
    print(resumen[["id", "nombre", "nivel", "nivel_confianza", "es_contenedor_clustering",
                   "area_ha"]].to_string(index=False))
    print("\nPor nivel_confianza:")
    print(resumen["nivel_confianza"].value_counts().to_string())


if __name__ == "__main__":
    main()
