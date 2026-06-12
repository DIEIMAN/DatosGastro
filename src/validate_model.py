from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

from config import DATA_ANALYTICS, DATA_PROCESSED, DATA_RAW, SOURCE_CONFIG

CABA_LAT_MIN = -34.75
CABA_LAT_MAX = -34.50
CABA_LON_MIN = -58.55
CABA_LON_MAX = -58.30


EXPECTED_TABLES = {
    "dim_fuente.csv": "id_fuente",
    "dim_ubicacion.csv": "id_ubicacion",
    "dim_territorio.csv": "id_territorio",
    "dim_categoria_gastronomica.csv": "id_categoria",
    "dim_organizador.csv": "id_organizador",
    "fact_establecimiento.csv": "id_establecimiento",
    "fact_habilitacion_gastronomica.csv": "id_habilitacion",
    "fact_evento_gastronomico.csv": "id_evento",
    "fact_programa_politica.csv": "id_programa",
    "fact_espacio_feria_mercado.csv": "id_espacio",
    "fact_puesto_feria.csv": "id_puesto_feria",
    "fact_mercado_feria.csv": "id_mercado_feria",
    "puente_evento_programa.csv": "",
}

EXPECTED_ANALYTICS = [
    "analytics_eventos_por_barrio.csv",
    "analytics_eventos_por_tipo.csv",
    "analytics_eventos_por_anio.csv",
    "analytics_eventos_cualitativos.csv",
    "analytics_establecimientos_por_categoria_barrio.csv",
    "analytics_habilitaciones_por_anio.csv",
    "analytics_habilitaciones_por_barrio.csv",
    "analytics_habilitaciones_por_categoria.csv",
    "analytics_habilitaciones_recientes.csv",
    "analytics_espacios_ferias_mercados_por_tipo.csv",
    "analytics_espacios_ferias_mercados_por_comuna.csv",
    "analytics_fiab_por_comuna.csv",
    "analytics_programas_por_anio.csv",
    "analytics_programas_por_tipo.csv",
    "analytics_programas_por_estado.csv",
    "analytics_programas_catalogo.csv",
    "analytics_programas_cualitativos.csv",
    "analytics_mapa_oportunidades.csv",
    "analytics_resumen_ejecutivo.csv",
]

FK_CHECKS = [
    ("fact_evento_gastronomico.csv", "id_ubicacion", "dim_ubicacion.csv", "id_ubicacion"),
    ("fact_evento_gastronomico.csv", "id_organizador", "dim_organizador.csv", "id_organizador"),
    ("puente_evento_programa.csv", "id_evento", "fact_evento_gastronomico.csv", "id_evento"),
    ("puente_evento_programa.csv", "id_programa", "fact_programa_politica.csv", "id_programa"),
    ("fact_establecimiento.csv", "id_categoria", "dim_categoria_gastronomica.csv", "id_categoria"),
    ("fact_establecimiento.csv", "id_ubicacion", "dim_ubicacion.csv", "id_ubicacion"),
    ("fact_habilitacion_gastronomica.csv", "id_ubicacion", "dim_ubicacion.csv", "id_ubicacion"),
    ("fact_espacio_feria_mercado.csv", "id_ubicacion", "dim_ubicacion.csv", "id_ubicacion"),
    ("fact_mercado_feria.csv", "id_ubicacion", "dim_ubicacion.csv", "id_ubicacion"),
]

TRACEABILITY_COLUMNS = {
    "fact_establecimiento.csv": ["id_fuente", "url_fuente", "fecha_consulta", "calidad_dato", "requiere_validacion", "motivo_validacion", "origen_dato", "estado_datos"],
    "fact_habilitacion_gastronomica.csv": ["id_fuente", "url_fuente", "fecha_consulta", "periodo_fuente", "anio_fuente", "calidad_dato", "requiere_validacion", "motivo_validacion", "origen_dato", "estado_datos"],
    "fact_evento_gastronomico.csv": ["id_fuente", "url_fuente", "fecha_consulta", "tipo_vinculo_gcba", "apto_dashboard", "calidad_dato", "requiere_validacion", "motivo_validacion", "origen_dato", "estado_datos"],
    "fact_programa_politica.csv": ["id_fuente", "url_fuente", "fecha_consulta", "tipo_programa", "estado", "apto_dashboard", "calidad_dato", "requiere_validacion", "motivo_validacion", "origen_dato", "estado_datos"],
    "fact_espacio_feria_mercado.csv": ["id_fuente", "url_fuente", "fecha_consulta", "calidad_dato", "requiere_validacion", "motivo_validacion", "origen_dato", "estado_datos", "limitaciones"],
    "fact_puesto_feria.csv": ["id_fuente", "url_fuente", "fecha_consulta", "calidad_dato", "requiere_validacion", "motivo_validacion", "origen_dato", "estado_datos", "apto_dashboard", "uso", "limitaciones"],
    "fact_mercado_feria.csv": ["id_fuente", "url_fuente", "fecha_consulta", "calidad_dato", "requiere_validacion", "motivo_validacion", "origen_dato", "estado_datos"],
}

IMPORTANT_FACTS = [
    "fact_establecimiento.csv",
    "fact_habilitacion_gastronomica.csv",
    "fact_espacio_feria_mercado.csv",
    "fact_mercado_feria.csv",
]

IMPORTANT_ANALYTICS = [
    "analytics_establecimientos_por_categoria_barrio.csv",
    "analytics_habilitaciones_por_anio.csv",
    "analytics_habilitaciones_por_barrio.csv",
    "analytics_habilitaciones_por_categoria.csv",
    "analytics_habilitaciones_recientes.csv",
    "analytics_espacios_ferias_mercados_por_tipo.csv",
    "analytics_espacios_ferias_mercados_por_comuna.csv",
    "analytics_fiab_por_comuna.csv",
    "analytics_eventos_por_barrio.csv",
    "analytics_eventos_por_tipo.csv",
    "analytics_eventos_por_anio.csv",
    "analytics_programas_por_tipo.csv",
    "analytics_programas_por_estado.csv",
    "analytics_programas_catalogo.csv",
    "analytics_mapa_oportunidades.csv",
    "analytics_resumen_ejecutivo.csv",
]

ANALYTICS_TRACEABILITY_COLUMNS = [
    "estado_datos",
    "fuentes_utilizadas",
    "urls_fuentes",
    "fecha_consulta_min",
    "fecha_consulta_max",
    "nota_metodologica",
    "limitaciones",
    "apto_dashboard",
]


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def add(messages: list[tuple[str, str]], level: str, text: str) -> None:
    messages.append((level, text))
    print(f"{level:7s} {text}")


def _coordinate_series(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series.astype(str).str.replace(",", ".", regex=False), errors="coerce")




def _is_number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _iter_geojson_coordinate_pairs(coordinates):
    """Yield (lat, lon) pairs from any GeoJSON coordinates nesting.

    GeoJSON stores coordinate positions as [longitude, latitude, ...]. Barrios and
    comunas are polygonal resources, so the validator must walk nested Polygon
    and MultiPolygon coordinate arrays instead of expecting flat lat/lon fields.
    """
    if isinstance(coordinates, (list, tuple)):
        if len(coordinates) >= 2 and _is_number(coordinates[0]) and _is_number(coordinates[1]):
            yield float(coordinates[1]), float(coordinates[0])
        else:
            for item in coordinates:
                yield from _iter_geojson_coordinate_pairs(item)


def _iter_geojson_geometries(geometry):
    if not isinstance(geometry, dict):
        return
    geometry_type = str(geometry.get("type", ""))
    if geometry_type == "GeometryCollection":
        for child in geometry.get("geometries", []) or []:
            yield from _iter_geojson_geometries(child)
        return
    if "coordinates" in geometry:
        yield geometry


def _geometry_coordinate_pairs(geometry) -> list[tuple[float, float]]:
    pairs: list[tuple[float, float]] = []
    for geom in _iter_geojson_geometries(geometry):
        pairs.extend(_iter_geojson_coordinate_pairs(geom.get("coordinates", [])))
    return pairs


def _bounds_intersects_caba(pairs: list[tuple[float, float]]) -> bool:
    lats = [lat for lat, _lon in pairs]
    lons = [lon for _lat, lon in pairs]
    min_lat, max_lat = min(lats), max(lats)
    min_lon, max_lon = min(lons), max(lons)
    return not (
        max_lat < CABA_LAT_MIN
        or min_lat > CABA_LAT_MAX
        or max_lon < CABA_LON_MIN
        or min_lon > CABA_LON_MAX
    )


def _validate_geojson_bounds(path: Path) -> tuple[bool, int, str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return False, 0, f"no se pudo leer {path.name}: {exc}"

    if not isinstance(data, dict):
        return False, 0, f"{path.name} no es un GeoJSON valido"

    if data.get("type") == "FeatureCollection":
        features = data.get("features", [])
    elif data.get("type") == "Feature":
        features = [data]
    elif "coordinates" in data or data.get("type") == "GeometryCollection":
        features = [{"type": "Feature", "geometry": data, "properties": {}}]
    else:
        return False, 0, f"{path.name} no tiene features ni geometria GeoJSON reconocible"

    if not isinstance(features, list) or not features:
        return False, 0, f"{path.name} no tiene features"

    total_vertices = 0
    empty_geometries = 0
    outside_geometries = 0
    valid_geometries = 0

    for feature in features:
        if not isinstance(feature, dict):
            empty_geometries += 1
            continue
        geometry = feature.get("geometry")
        pairs = _geometry_coordinate_pairs(geometry)
        if not pairs:
            empty_geometries += 1
            continue
        total_vertices += len(pairs)
        valid_geometries += 1
        if not _bounds_intersects_caba(pairs):
            outside_geometries += 1

    if valid_geometries == 0:
        return False, 0, f"{path.name} no contiene geometrias con coordenadas"
    if empty_geometries:
        return False, total_vertices, f"{path.name} tiene {empty_geometries} features sin geometria/coordenadas"
    if outside_geometries:
        return False, total_vertices, f"{path.name} tiene {outside_geometries} geometrias fuera de CABA"

    return (
        True,
        total_vertices,
        f"{path.name} contiene {valid_geometries} geometrias validas dentro/intersectando bounding box CABA ({total_vertices} vertices)",
    )

def _real_source_files() -> list[Path]:
    paths = []
    for source in SOURCE_CONFIG.values():
        for pattern in source.get("raw_patterns", []):
            paths.extend(DATA_RAW.glob(pattern))
    return sorted({path for path in paths if path.is_file() and path.suffix.lower() == ".csv"})


def _required_real_resources() -> list[dict]:
    return [
        source
        for source in SOURCE_CONFIG.values()
        if source.get("required_strict") and source.get("formato") == "csv"
    ]


def validate(strict_real: bool = False) -> int:
    messages: list[tuple[str, str]] = []
    tables: dict[str, pd.DataFrame] = {}

    for filename, pk in EXPECTED_TABLES.items():
        path = DATA_PROCESSED / filename
        if not path.exists():
            add(messages, "ERROR", f"falta tabla esperada {filename}")
            continue
        df = read_csv(path)
        tables[filename] = df
        add(messages, "OK", f"existe {filename} ({len(df)} filas)")
        if not pk:
            continue
        if pk not in df.columns:
            add(messages, "ERROR", f"{filename} no tiene PK {pk}")
            continue
        if df[pk].eq("").any():
            add(messages, "ERROR", f"{filename}.{pk} tiene nulos/vacios")
        duplicates = int(df[pk].duplicated().sum())
        if duplicates:
            add(messages, "ERROR", f"{filename}.{pk} tiene {duplicates} duplicados")

    for fact_name, fact_key, dim_name, dim_key in FK_CHECKS:
        if fact_name not in tables or dim_name not in tables:
            continue
        fact = tables[fact_name]
        dim = tables[dim_name]
        if fact_key not in fact.columns or dim_key not in dim.columns:
            add(messages, "ERROR", f"no se puede validar FK {fact_name}.{fact_key} -> {dim_name}.{dim_key}")
            continue
        missing = sorted(set(fact[fact_key].dropna()) - set(dim[dim_key].dropna()) - {""})
        if missing:
            add(messages, "ERROR", f"FK sin match {fact_name}.{fact_key}: {missing[:10]}")
        else:
            add(messages, "OK", f"FK valida {fact_name}.{fact_key} -> {dim_name}.{dim_key}")

    ubicaciones = tables.get("dim_ubicacion.csv")
    if ubicaciones is not None and {"latitud", "longitud"}.issubset(ubicaciones.columns):
        lat = _coordinate_series(ubicaciones["latitud"])
        lon = _coordinate_series(ubicaciones["longitud"])
        has_lat = lat.notna()
        has_lon = lon.notna()
        incomplete = ubicaciones[has_lat ^ has_lon]
        if not incomplete.empty:
            add(messages, "ERROR", f"dim_ubicacion tiene {len(incomplete)} filas con coordenada incompleta")
        mapped = ubicaciones[has_lat & has_lon].copy()
        mapped_lat = lat[has_lat & has_lon]
        mapped_lon = lon[has_lat & has_lon]
        out_of_bounds = mapped[
            ~(
                mapped_lat.between(CABA_LAT_MIN, CABA_LAT_MAX)
                & mapped_lon.between(CABA_LON_MIN, CABA_LON_MAX)
            )
        ]
        if out_of_bounds.empty:
            add(messages, "OK", f"dim_ubicacion coordenadas dentro de bounding box CABA ({len(mapped)} filas mapeables)")
        else:
            add(messages, "ERROR", f"dim_ubicacion tiene {len(out_of_bounds)} filas con coordenadas fuera de CABA")



    dim_territorio = tables.get("dim_territorio.csv")
    if dim_territorio is not None:
        if dim_territorio.empty:
            add(messages, "WARNING", "dim_territorio esta vacia: faltan geo_barrios.geojson/geo_comunas.geojson opcionales")
        elif {"barrio", "comuna", "centroide_latitud", "centroide_longitud", "calidad_geo"}.issubset(dim_territorio.columns):
            valid_comunas = {str(value) for value in range(1, 16)} | {"No determinada"}
            bad_comuna = dim_territorio[~dim_territorio["comuna"].astype(str).isin(valid_comunas)]
            if bad_comuna.empty:
                add(messages, "OK", "dim_territorio comunas dentro de dominio 1-15")
            else:
                add(messages, "ERROR", f"dim_territorio tiene {len(bad_comuna)} comunas fuera de dominio")
            lat = _coordinate_series(dim_territorio["centroide_latitud"])
            lon = _coordinate_series(dim_territorio["centroide_longitud"])
            mapped = dim_territorio[lat.notna() & lon.notna()]
            out_of_bounds = mapped[~(lat[lat.notna() & lon.notna()].between(CABA_LAT_MIN, CABA_LAT_MAX) & lon[lat.notna() & lon.notna()].between(CABA_LON_MIN, CABA_LON_MAX))]
            if out_of_bounds.empty:
                add(messages, "OK", f"dim_territorio centroides dentro de bounding box CABA ({len(mapped)} filas)")
            else:
                add(messages, "ERROR", f"dim_territorio tiene {len(out_of_bounds)} centroides fuera de CABA")
        else:
            add(messages, "ERROR", "dim_territorio no tiene columnas territoriales esperadas")

    if strict_real:
        for geo_name in ("geo_barrios.geojson", "geo_comunas.geojson"):
            geo_path = DATA_RAW / geo_name
            if not geo_path.exists():
                add(messages, "WARNING", f"falta recurso territorial opcional {geo_name}; coropleta queda pendiente")
            else:
                ok, _count, text = _validate_geojson_bounds(geo_path)
                add(messages, "OK" if ok else "ERROR", text)


    for filename, columns in TRACEABILITY_COLUMNS.items():
        df = tables.get(filename)
        if df is None:
            continue
        missing_columns = [column for column in columns if column not in df.columns]
        if missing_columns:
            add(messages, "ERROR", f"{filename} no tiene columnas de trazabilidad: {missing_columns}")
        else:
            add(messages, "OK", f"{filename} tiene trazabilidad minima")
        if "origen_dato" in df.columns:
            has_seed = df["origen_dato"].astype(str).str.contains("seed", case=False, na=False).any()
            if has_seed:
                level = "ERROR" if strict_real and filename in IMPORTANT_FACTS else "WARNING"
                add(messages, level, f"{filename} contiene registros seed; no presentar como datos reales")
            if strict_real and filename in IMPORTANT_FACTS and df["origen_dato"].astype(str).eq("").any():
                add(messages, "ERROR", f"{filename} tiene origen_dato vacio")

    est = tables.get("fact_establecimiento.csv")
    if est is not None and len(est) <= 6 and "origen_dato" in est.columns and est["origen_dato"].astype(str).str.contains("seed", case=False, na=False).all():
        level = "ERROR" if strict_real else "WARNING"
        add(messages, level, "fact_establecimiento parece ser solo seed de 6 filas; no apto para dashboard")
    if est is not None and "id_fuente" in est.columns and (est["id_fuente"].astype(str) == "F02").any():
        add(messages, "ERROR", "fact_establecimiento contiene registros F02; las habilitaciones deben vivir en fact_habilitacion_gastronomica")

    if strict_real:
        for source in _required_real_resources():
            path = DATA_RAW / source["output_filename"]
            if not path.exists():
                add(messages, "ERROR", f"{source['id_fuente']} no tiene CSV real requerido en data/raw: {source['output_filename']}")
            elif path.stat().st_size < 1024:
                add(messages, "ERROR", f"{source['id_fuente']} archivo real menor a 1 KB: {path}")

    for filename in EXPECTED_ANALYTICS:
        path = DATA_ANALYTICS / filename
        if not path.exists():
            add(messages, "ERROR", f"falta analytics {filename}")
            continue
        df = read_csv(path)
        if df.empty:
            add(messages, "ERROR", f"analytics vacia {filename}")
        else:
            add(messages, "OK", f"analytics no vacia {filename} ({len(df)} filas)")
        missing_analytics_columns = [column for column in ANALYTICS_TRACEABILITY_COLUMNS if column not in df.columns]
        if missing_analytics_columns:
            add(messages, "ERROR", f"{filename} no tiene trazabilidad analytics: {missing_analytics_columns}")
            continue
        if df["estado_datos"].astype(str).eq("").any():
            add(messages, "ERROR", f"{filename} tiene estado_datos vacio")
        if df["fuentes_utilizadas"].astype(str).isin(["", "No disponible"]).any():
            level = "ERROR" if filename in IMPORTANT_ANALYTICS else "WARNING"
            add(messages, level, f"{filename} tiene fuentes_utilizadas vacio/no disponible")
        if df["urls_fuentes"].astype(str).isin(["", "No disponible"]).any():
            level = "ERROR" if strict_real and filename in IMPORTANT_ANALYTICS else "WARNING"
            add(messages, level, f"{filename} tiene urls_fuentes vacio/no disponible")
        if df["estado_datos"].astype(str).str.contains("seed", case=False, na=False).any():
            level = "ERROR" if strict_real and filename in IMPORTANT_ANALYTICS else "WARNING"
            add(messages, level, f"{filename} esta basada en seeds")
        if filename in IMPORTANT_ANALYTICS and df["apto_dashboard"].astype(str).ne("si").any():
            level = "ERROR" if strict_real else "WARNING"
            add(messages, level, f"{filename} no es apta para dashboard hoy")

    hab = tables.get("fact_habilitacion_gastronomica.csv")
    if strict_real and hab is not None:
        if hab.empty:
            add(messages, "ERROR", "fact_habilitacion_gastronomica esta vacia; no hay monitor de habilitaciones recientes")
        elif not (hab.get("id_fuente", pd.Series(dtype=str)).astype(str) == "F02").all():
            add(messages, "ERROR", "fact_habilitacion_gastronomica debe contener solo registros F02")
        for column in ("descripcion_rubro_original", "categoria_gastronomica_inferida", "confianza_categoria", "motivo_categoria"):
            if column not in hab.columns:
                add(messages, "ERROR", f"fact_habilitacion_gastronomica no tiene {column}")
        if "comuna" in hab.columns:
            valid_comunas = {str(value) for value in range(1, 16)} | {"No determinada"}
            bad_comuna = hab[~hab["comuna"].astype(str).isin(valid_comunas)]
            if bad_comuna.empty:
                add(messages, "OK", "fact_habilitacion_gastronomica.comuna usa solo 1-15 o No determinada")
            else:
                add(messages, "ERROR", f"fact_habilitacion_gastronomica tiene {len(bad_comuna)} comunas fuera de dominio")
        else:
            add(messages, "ERROR", "fact_habilitacion_gastronomica no tiene comuna")
        if {"anio_fuente", "requiere_validacion", "motivo_validacion"}.issubset(hab.columns):
            motive = "Recurso 2025 con esquema distinto: contiene disposiciones de varios anios; no usar como flujo anual"
            rows_2025 = hab[hab["anio_fuente"].astype(str) == "2025"]
            bad_2025 = rows_2025[
                (rows_2025["requiere_validacion"].astype(str) != "si")
                | (rows_2025["motivo_validacion"].astype(str) != motive)
            ]
            if bad_2025.empty:
                add(messages, "OK", "F02 2025 queda marcado como no comparable y requiere validacion")
            else:
                add(messages, "ERROR", f"{len(bad_2025)} filas F02 2025 no tienen advertencia metodologica esperada")

    espacios = tables.get("fact_espacio_feria_mercado.csv")
    puestos = tables.get("fact_puesto_feria.csv")
    mercado_feria = tables.get("fact_mercado_feria.csv")
    if strict_real and espacios is not None:
        if espacios.empty:
            add(messages, "ERROR", "fact_espacio_feria_mercado esta vacia; F03 espacios reales no se integro")
        forbidden_space_columns = {"apellido", "nombre_persona", "categoria_titularidad", "persona_hash", "puesto", "rubro_puesto", "uso", "apto_dashboard"}
        leaked_columns = sorted(forbidden_space_columns & set(espacios.columns))
        if leaked_columns:
            add(messages, "ERROR", f"fact_espacio_feria_mercado mezcla campos de puestos/personas: {leaked_columns}")
        if "tipo_espacio" in espacios.columns:
            bad_types = espacios[espacios["tipo_espacio"].astype(str).str.contains("TITULAR|COTITULAR|PUESTO", case=False, na=False)]
            if not bad_types.empty:
                add(messages, "ERROR", f"fact_espacio_feria_mercado contiene {len(bad_types)} filas con tipo de puesto/persona")
            if (DATA_RAW / "f03_fiab.geojson").exists() and not (espacios["tipo_espacio"].astype(str) == "FIAB").any():
                add(messages, "ERROR", "f03_fiab.geojson existe pero no hay espacios FIAB integrados")
        for column in ("es_gastronomico", "cantidad_puestos", "rubros_principales", "cantidad_puestos_gastronomicos"):
            if column not in espacios.columns:
                add(messages, "ERROR", f"fact_espacio_feria_mercado no tiene columna agregada {column}")
    if strict_real and puestos is not None:
        pii_columns = {"apellido", "nombre", "nombre_persona"}
        leaked_pii = sorted(pii_columns & set(puestos.columns))
        if leaked_pii:
            add(messages, "ERROR", f"fact_puesto_feria expone nombres de personas fisicas: {leaked_pii}")
        if "apto_dashboard" not in puestos.columns or puestos["apto_dashboard"].astype(str).ne("no").any():
            add(messages, "ERROR", "fact_puesto_feria debe quedar apto_dashboard=no")
        if "uso" not in puestos.columns or puestos["uso"].astype(str).ne("auditoria_interna").any():
            add(messages, "ERROR", "fact_puesto_feria debe quedar con uso=auditoria_interna")
    if strict_real and mercado_feria is not None:
        pii_columns = {"apellido", "nombre_persona", "persona_hash", "categoria_titularidad", "rubro_puesto"}
        leaked_pii = sorted(pii_columns & set(mercado_feria.columns))
        if leaked_pii:
            add(messages, "ERROR", f"fact_mercado_feria expone campos personales o de puesto: {leaked_pii}")
        if "tipo_espacio" in mercado_feria.columns:
            bad_types = mercado_feria[mercado_feria["tipo_espacio"].astype(str).str.contains("TITULAR|COTITULAR|PUESTO", case=False, na=False)]
            if bad_types.empty:
                add(messages, "OK", "fact_mercado_feria no contiene tipos TITULAR/COTITULAR/PUESTO")
            else:
                add(messages, "ERROR", f"fact_mercado_feria contiene {len(bad_types)} filas de grano puesto/persona")

    eventos = tables.get("fact_evento_gastronomico.csv")
    if strict_real and eventos is not None:
        if eventos.empty:
            add(messages, "ERROR", "fact_evento_gastronomico esta vacia; F04 no se integro")
        elif not (eventos.get("id_fuente", pd.Series(dtype=str)).astype(str) == "F04").all():
            add(messages, "ERROR", "fact_evento_gastronomico debe contener solo registros F04 en esta integracion")
        for column in ("url_fuente", "apto_dashboard", "tipo_vinculo_gcba"):
            if column not in eventos.columns:
                add(messages, "ERROR", f"fact_evento_gastronomico no tiene {column}")
            elif eventos[column].astype(str).isin(["", "No disponible"]).any():
                add(messages, "ERROR", f"fact_evento_gastronomico tiene {column} vacio/no disponible")
        if "fecha_completa" in eventos.columns and "apto_dashboard" in eventos.columns and "requiere_validacion" in eventos.columns:
            bad_dates = eventos[
                (eventos["fecha_completa"].astype(str) != "si")
                & (eventos["apto_dashboard"].astype(str) == "si")
                & (eventos["requiere_validacion"].astype(str) != "si")
            ]
            if not bad_dates.empty:
                add(messages, "ERROR", f"{len(bad_dates)} eventos F04 con fecha incompleta quedaron aptos para metrica fuerte")
        if {"tipo_organizador", "tipo_vinculo_gcba", "apto_dashboard"}.issubset(eventos.columns):
            private_only_diffusion = eventos[
                eventos["tipo_organizador"].astype(str).str.contains("Privado", case=False, na=False)
                & eventos["tipo_vinculo_gcba"].astype(str).str.contains("Difusion oficial|Requiere validacion", case=False, na=False)
                & (eventos["apto_dashboard"].astype(str) == "si")
            ]
            if not private_only_diffusion.empty:
                add(messages, "ERROR", f"{len(private_only_diffusion)} eventos privados sin vinculo GCBA confirmado quedaron aptos")

    programas = tables.get("fact_programa_politica.csv")
    if strict_real and programas is not None:
        if programas.empty:
            add(messages, "ERROR", "fact_programa_politica esta vacia; F05 no se integro")
        elif not (programas.get("id_fuente", pd.Series(dtype=str)).astype(str) == "F05").all():
            add(messages, "ERROR", "fact_programa_politica debe contener solo registros F05 en esta integracion")
        for column in ("url_fuente", "apto_dashboard", "tipo_programa", "estado"):
            if column not in programas.columns:
                add(messages, "ERROR", f"fact_programa_politica no tiene {column}")
            elif programas[column].astype(str).isin(["", "No disponible"]).any():
                add(messages, "ERROR", f"fact_programa_politica tiene {column} vacio/no disponible")
        if "vigencia_clara" in programas.columns and "apto_dashboard" in programas.columns:
            bad_vigencia = programas[
                (programas["vigencia_clara"].astype(str) != "si")
                & (programas["apto_dashboard"].astype(str) == "si")
            ]
            if not bad_vigencia.empty:
                add(messages, "ERROR", f"{len(bad_vigencia)} programas F05 sin vigencia clara quedaron aptos")

    resumen_path = DATA_ANALYTICS / "analytics_resumen_ejecutivo.csv"
    if strict_real and resumen_path.exists():
        resumen = read_csv(resumen_path)
        indicadores = set(resumen.get("indicador", pd.Series(dtype=str)).astype(str))
        if "ferias_mercados_f03" in indicadores:
            add(messages, "ERROR", "analytics_resumen_ejecutivo conserva KPI ambiguo ferias_mercados_f03")
        if "espacios_ferias_mercados_f03" not in indicadores:
            add(messages, "ERROR", "analytics_resumen_ejecutivo no incluye espacios_ferias_mercados_f03")
        if "puestos_feria_f03" in indicadores and "uso" in resumen.columns:
            puesto_rows = resumen[resumen["indicador"].astype(str) == "puestos_feria_f03"]
            if not puesto_rows.empty and not puesto_rows["uso"].astype(str).eq("auditoria_interna").all():
                add(messages, "ERROR", "puestos_feria_f03 debe marcarse como auditoria_interna")

    hab_anio_path = DATA_ANALYTICS / "analytics_habilitaciones_por_anio.csv"
    if strict_real and hab_anio_path.exists():
        hab_anio = read_csv(hab_anio_path)
        required_columns = {"nota_serie", "comparable_como_flujo_anual"}
        missing_columns = sorted(required_columns - set(hab_anio.columns))
        if missing_columns:
            add(messages, "ERROR", f"analytics_habilitaciones_por_anio no tiene columnas metodologicas: {missing_columns}")
        else:
            non_comparable = hab_anio[hab_anio["anio_fuente"].astype(str).isin(["2015-2018", "2025"])]
            if not non_comparable.empty and non_comparable["comparable_como_flujo_anual"].astype(str).eq("no").all():
                add(messages, "OK", "analytics_habilitaciones_por_anio marca 2015-2018 y 2025 como no comparables")
            else:
                add(messages, "ERROR", "analytics_habilitaciones_por_anio no marca correctamente periodos no comparables")

    mapa_path = DATA_ANALYTICS / "analytics_mapa_oportunidades.csv"
    if strict_real and mapa_path.exists():
        mapa = read_csv(mapa_path)
        forbidden_columns = {"presencia_de_polos", "nivel_actividad_gastronomica", "oportunidades_detectadas"}
        leaked_columns = sorted(forbidden_columns & set(mapa.columns))
        if leaked_columns:
            add(messages, "ERROR", f"analytics_mapa_oportunidades conserva columnas placeholder: {leaked_columns}")
        required_columns = {
            "comuna",
            "cantidad_establecimientos_f01",
            "cantidad_habilitaciones_f02_con_comuna",
            "cantidad_espacios_f03",
            "cantidad_eventos_f04_aptos",
        }
        missing_columns = sorted(required_columns - set(mapa.columns))
        if missing_columns:
            add(messages, "ERROR", f"analytics_mapa_oportunidades no tiene columnas por universo/comuna: {missing_columns}")
        else:
            add(messages, "OK", "analytics_mapa_oportunidades usa grano comuna y universos separados")

    if strict_real:
        pii_names = {"apellido", "nombre_persona", "persona_hash", "categoria_titularidad"}
        for path in DATA_ANALYTICS.glob("analytics_*.csv"):
            df = read_csv(path)
            if "apto_dashboard" in df.columns and df["apto_dashboard"].astype(str).eq("si").any():
                leaked = sorted(pii_names & set(df.columns))
                if leaked:
                    add(messages, "ERROR", f"{path.name} apta para dashboard expone campos personales: {leaked}")

    errors = sum(1 for level, _ in messages if level == "ERROR")
    warnings = sum(1 for level, _ in messages if level == "WARNING")
    print(f"\nResumen validacion: OK={sum(1 for level, _ in messages if level == 'OK')} WARNING={warnings} ERROR={errors}")
    return 1 if errors else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Valida modelo, analytics y trazabilidad.")
    parser.add_argument("--strict-real", action="store_true", help="Falla si hay seeds o analytics no aptas para dashboard.")
    args = parser.parse_args()
    sys.exit(validate(strict_real=args.strict_real))
