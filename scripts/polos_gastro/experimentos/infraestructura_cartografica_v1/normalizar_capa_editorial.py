# -*- coding: utf-8 -*-
"""Etapa Infra-4 — Normalizador: de un GeoJSON crudo (QGIS/geojson.io/script) al esquema
formal de la capa editorial (`02_DISENO_CAPA_EDITORIAL.md`).

EXPERIMENTAL. Cualquier herramienta de edicion (QGIS, geojson.io, o un script como
`construir_poligono_real_palermo_soho.py`) exporta geometria + a lo sumo unos pocos
campos. Este modulo completa los 16 atributos del esquema con valores por defecto
razonables, sin pisar los que ya vengan informados, y junta features sueltos en un unico
`macrozonas_editorial_vN.geojson`.

No inventa `nivel_confianza` ni `calles_limite`: si no vienen informados, quedan en null /
"sin_evidencia" para que quede explicito que falta revision editorial.

Uso (como libreria):
    from normalizar_capa_editorial import normalizar_features, ESQUEMA_CAMPOS
"""

from __future__ import annotations

from datetime import date

import geopandas as gpd

ESQUEMA_CAMPOS = [
    "id", "nombre", "nivel", "polo_id", "es_contenedor_clustering", "tipo_geometria",
    "metodo_construccion", "calles_limite", "fuente", "fecha_creacion",
    "fecha_actualizacion", "autor", "estado_revision", "nivel_confianza",
    "version_capa", "reemplaza_a", "contiene_semilla_ids", "observaciones",
]

DEFAULTS = {
    "nivel": "subzona",
    "polo_id": None,
    "es_contenedor_clustering": True,
    "tipo_geometria": "pendiente",
    "metodo_construccion": "sin documentar",
    "calles_limite": None,
    "fuente": "sin documentar",
    "fecha_actualizacion": None,  # se completa con fecha_creacion si falta
    "autor": "sin documentar",
    "estado_revision": "borrador",
    "nivel_confianza": "sin_evidencia",
    "version_capa": "v1_borrador",
    "reemplaza_a": None,
    "contiene_semilla_ids": None,
    "observaciones": "",
}


def normalizar_gdf(gdf: gpd.GeoDataFrame, hoy: str | None = None) -> gpd.GeoDataFrame:
    """Completa columnas faltantes del esquema con defaults; no pisa valores existentes."""
    hoy = hoy or date.today().isoformat()
    gdf = gdf.copy()

    if "id" not in gdf.columns:
        raise ValueError("Cada feature debe traer 'id' (no se genera automaticamente).")
    if "nombre" not in gdf.columns:
        raise ValueError("Cada feature debe traer 'nombre'.")
    if "fecha_creacion" not in gdf.columns:
        gdf["fecha_creacion"] = hoy

    for campo in ESQUEMA_CAMPOS:
        if campo not in gdf.columns:
            gdf[campo] = DEFAULTS.get(campo)
        else:
            gdf[campo] = gdf[campo].where(gdf[campo].notna(), DEFAULTS.get(campo))

    gdf["fecha_actualizacion"] = gdf["fecha_actualizacion"].fillna(gdf["fecha_creacion"])

    columnas = ESQUEMA_CAMPOS + ["geometry"]
    faltantes = [c for c in columnas if c not in gdf.columns]
    if faltantes:
        raise ValueError(f"Columnas inesperadamente ausentes tras normalizar: {faltantes}")
    return gdf[columnas]


def combinar_y_normalizar(rutas_geojson: list[str], destino: str) -> gpd.GeoDataFrame:
    """Junta varios GeoJSON de features individuales en una unica capa normalizada."""
    partes = [gpd.read_file(r) for r in rutas_geojson]
    combinado = gpd.pd.concat(partes, ignore_index=True)
    combinado = gpd.GeoDataFrame(combinado, geometry="geometry", crs=partes[0].crs)
    normalizado = normalizar_gdf(combinado)
    normalizado.to_file(destino, driver="GeoJSON")
    return normalizado


if __name__ == "__main__":
    import sys
    from pathlib import Path

    REPO = Path(__file__).resolve().parents[4]
    SALIDA = REPO / "outputs/polos_gastro/historico/experimentos/infraestructura_cartografica_v1"

    rutas = [
        str(SALIDA / "poligono_real_palermo_soho.geojson"),
        str(SALIDA / "poligono_real_palermo_hollywood.geojson"),
    ]
    destino = str(SALIDA / "macrozonas_editorial_v1_borrador.geojson")
    resultado = combinar_y_normalizar(rutas, destino)
    print(f"{len(resultado)} features normalizados -> {destino}")
    print(resultado[["id", "nombre", "nivel", "tipo_geometria", "estado_revision",
                     "nivel_confianza"]].to_string(index=False))
