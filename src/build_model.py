from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from datetime import date
from pathlib import Path

import pandas as pd
from shapely.geometry import shape

from clean_text import clean_dataframe_columns, normalize_proper_name, normalize_text
from config import DATA_PROCESSED, DATA_RAW, DATA_SEEDS, DOCS, PROFILE_OUTPUTS, SOURCE_CONFIG
from geocode_usig import CACHE_PATH as GEO_CACHE_PATH, cache_key as geo_cache_key
from normalize_addresses import UNKNOWN_LOCATION_ID, normalize_address_offline
from normalize_categories import classify_gastronomic_category, taxonomy_dataframe_rows
from source_contracts import SourceLoadResult, map_source_columns

TODAY = date.today().isoformat()
CABA_LAT_MIN = -34.75
CABA_LAT_MAX = -34.50
CABA_LON_MIN = -58.55
CABA_LON_MAX = -58.30
F02_2025_VALIDATION_MOTIVE = "Recurso 2025 con esquema distinto: contiene disposiciones de varios anios; no usar como flujo anual"

NULL_SENTINELS = {
    "",
    "No disponible",
    "No aplica",
    "No identificado",
    "No identificada",
    "No publicado en las fuentes consultadas",
    "No publicada en las fuentes consultadas",
    "No publicadas en las fuentes consultadas",
    "No publicados en las fuentes consultadas",
    "Requiere validacion",
    "Multiples barrios",
    "Multiples comunas",
    "Toda la Ciudad",
}


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        sample = path.read_text(encoding="utf-8-sig", errors="replace")[:8000]
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
        sep = dialect.delimiter
    except Exception:
        sep = None
    read_kwargs = {"dtype": str, "keep_default_na": False, "encoding": "utf-8-sig", "encoding_errors": "replace"}
    try:
        if sep:
            return pd.read_csv(path, sep=sep, **read_kwargs)
        return pd.read_csv(path, sep=None, engine="python", **read_kwargs)
    except TypeError:
        read_kwargs.pop("encoding_errors", None)
    except Exception:
        pass
    if sep:
        return pd.read_csv(path, dtype=str, keep_default_na=False, encoding="latin-1", sep=sep)
    return pd.read_csv(path, dtype=str, keep_default_na=False, encoding="latin-1", sep=None, engine="python")


def write_csv(df: pd.DataFrame, filename: str) -> None:
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    df.to_csv(DATA_PROCESSED / filename, index=False, encoding="utf-8")
    print(f"OK {filename}: {len(df)} filas")


def _resource_items(source_id: str, include_optional: bool = True) -> list[tuple[str, dict]]:
    items = [(key, value) for key, value in SOURCE_CONFIG.items() if value.get("id_fuente") == source_id and value.get("formato") == "csv"]
    if not include_optional:
        items = [(key, value) for key, value in items if value.get("required_strict")]
    return items


def discover_source_paths(source_id: str) -> tuple[list[tuple[Path, str, dict]], str]:
    resources = _resource_items(source_id)
    real_paths: list[Path] = []
    real_items: list[tuple[Path, str, dict]] = []
    for key, source in resources:
        candidates = []
        output_filename = source.get("output_filename")
        if output_filename:
            candidates.append(DATA_RAW / output_filename)
        for pattern in source.get("raw_patterns", []):
            candidates.extend(DATA_RAW.glob(pattern))
        for path in sorted({candidate for candidate in candidates if candidate.is_file() and candidate.suffix.lower() == ".csv"}):
            real_items.append((path, key, source))
    if real_items:
        return real_items, "real"

    seed_glob = next((source.get("seed_glob") for _, source in resources if source.get("seed_glob")), "")
    seed_items = [(path, source_id, {"id_fuente": source_id, "fecha_consulta": TODAY}) for path in sorted(DATA_SEEDS.glob(seed_glob))]
    return seed_items, "seed"


def load_source_data(source_id: str) -> tuple[pd.DataFrame, list[SourceLoadResult]]:
    paths, origin = discover_source_paths(source_id)
    frames = []
    reports: list[SourceLoadResult] = []
    for path, key, source in paths:
        raw = read_csv(path)
        mapped, report = map_source_columns(raw, source_id, origin, path)
        default_url = source.get("dataset_url", source.get("download_url", "No disponible"))
        if "url_fuente" in mapped.columns:
            mapped["url_fuente"] = mapped["url_fuente"].where(mapped["url_fuente"].astype(str).str.strip().ne(""), default_url)
        else:
            mapped["url_fuente"] = default_url
        mapped["download_url"] = source.get("download_url", "")
        mapped["fecha_consulta"] = source.get("fecha_consulta", TODAY)
        mapped["periodo_fuente"] = source.get("periodo_fuente", "")
        mapped["anio_fuente"] = source.get("anio_fuente", source.get("periodo_fuente", ""))
        mapped["estado_datos"] = "datos reales" if origin == "real" else "datos seed"
        frames.append(mapped)
        reports.append(
            SourceLoadResult(
                source_id=report.source_id,
                path=report.path,
                origin=report.origin,
                rows=report.rows,
                mapped_columns=f"recurso={key}; {report.mapped_columns}",
                missing_columns=report.missing_columns,
                extra_columns=report.extra_columns,
            )
        )
    if not frames:
        empty = pd.DataFrame()
        reports.append(
            SourceLoadResult(
                source_id=source_id,
                path="",
                origin="missing",
                rows=0,
                mapped_columns="",
                missing_columns="archivo no encontrado",
                extra_columns="",
            )
        )
        return empty, reports
    return pd.concat(frames, ignore_index=True), reports


def write_contract_reports(reports: list[SourceLoadResult]) -> None:
    PROFILE_OUTPUTS.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)
    rows = [report.__dict__ for report in reports]
    pd.DataFrame(rows).to_csv(PROFILE_OUTPUTS / "contratos_fuentes.csv", index=False, encoding="utf-8")

    lines = [
        "# Contratos de fuentes",
        "",
        f"Generado: {TODAY}",
        "",
        "Este reporte muestra que archivo se uso para cada fuente, si fue seed o real, y que columnas pudieron mapearse al contrato canonico.",
        "",
    ]
    for report in reports:
        lines.extend(
            [
                f"## {report.source_id}",
                "",
                f"- Archivo: `{report.path or 'No encontrado'}`",
                f"- Origen: {report.origin}",
                f"- Filas: {report.rows}",
                f"- Columnas mapeadas: {report.mapped_columns or 'Ninguna'}",
                f"- Columnas requeridas faltantes: {report.missing_columns or 'Ninguna'}",
                f"- Columnas extra no usadas: {report.extra_columns or 'Ninguna'}",
                "",
            ]
        )
    (DOCS / "contratos_fuentes.md").write_text("\n".join(lines), encoding="utf-8")


def read_seed_csv(filename: str) -> pd.DataFrame:
    return read_csv(DATA_SEEDS / filename)


def strict_real_errors(reports: list[SourceLoadResult], eventos: pd.DataFrame) -> list[str]:
    errors = []
    by_path = {Path(report.path).name: report for report in reports if report.path}
    required_resources = [
        source
        for _key, source in SOURCE_CONFIG.items()
        if source.get("required_strict") and source.get("formato") == "csv"
    ]
    for source in required_resources:
        expected_name = source["output_filename"]
        report = by_path.get(expected_name)
        if report is None or report.origin != "real":
            errors.append(f"{source['id_fuente']} {expected_name}: falta CSV real en data/raw; no se permite fallback seed en --strict-real")
            continue
        if report.rows == 0:
            errors.append(f"{source['id_fuente']} {expected_name}: el CSV real no tiene filas")
        if report.missing_columns:
            errors.append(f"{source['id_fuente']} {expected_name}: faltan columnas requeridas: {report.missing_columns}")
        path = Path(report.path)
        if path.exists() and path.stat().st_size < 1024:
            errors.append(f"{source['id_fuente']} {expected_name}: archivo real sospechosamente chico (<1 KB): {path}")
    return errors


def first_existing(*values, default="No disponible"):
    for value in values:
        cleaned = normalize_text(value)
        if cleaned:
            return cleaned
    return default


def is_sentinel(value: str) -> bool:
    return normalize_text(value) in NULL_SENTINELS


def normalize_yes_no(value: str, default: str = "si") -> str:
    cleaned = normalize_text(value, case="lower", remove_accents=True)
    if cleaned in {"si", "s", "yes", "true", "1"}:
        return "si"
    if cleaned in {"no", "n", "false", "0"}:
        return "no"
    if "requiere validacion" in cleaned:
        return "si"
    return default


def normalize_comuna_value(value: str) -> str:
    cleaned = normalize_text(value, case="lower", remove_accents=True)
    if not cleaned or cleaned in {"no determinada", "no determinado", "no disponible"}:
        return "No determinada"
    match = re.search(r"\b(1[0-5]|[1-9])\b", cleaned)
    if match:
        return str(int(match.group(1)))
    return "No determinada"


def normalize_dashboard_flag(value: str) -> str:
    cleaned = normalize_text(value, case="lower", remove_accents=True)
    if cleaned == "si":
        return "si"
    if cleaned == "no":
        return "no"
    if "requiere validacion" in cleaned:
        return "requiere_validacion"
    return "requiere_validacion"


def normalize_quality(value: str) -> tuple[str, str]:
    original = first_existing(value, default="Media")
    lowered = normalize_text(original, case="lower", remove_accents=True)
    if "/" in original or "media" in lowered:
        return "Media", original
    if "alta" in lowered:
        return "Alta", original
    if "baja" in lowered:
        return "Baja", original
    return original, original


def has_complete_date(value: str) -> bool:
    cleaned = normalize_text(value)
    if is_sentinel(cleaned):
        return False
    return bool(pd.to_datetime(pd.Series([cleaned]), errors="coerce").notna().iloc[0])


def parse_coordinate(value) -> float | None:
    text = normalize_text(value)
    if not text or is_sentinel(text):
        return None
    text = text.replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return None


def in_caba_bounds(lat: float | None, lon: float | None) -> bool:
    return (
        lat is not None
        and lon is not None
        and CABA_LAT_MIN <= lat <= CABA_LAT_MAX
        and CABA_LON_MIN <= lon <= CABA_LON_MAX
    )


def format_coordinate(value: float) -> str:
    return f"{value:.8f}".rstrip("0").rstrip(".")


def official_point_location(address, barrio, lat_value, lon_value, reason: str) -> dict:
    location = normalize_address_offline(address, barrio)
    lat = parse_coordinate(lat_value)
    lon = parse_coordinate(lon_value)
    if in_caba_bounds(lat, lon):
        location["latitud"] = format_coordinate(lat)
        location["longitud"] = format_coordinate(lon)
        location["calidad_geo"] = "fuente_oficial"
        location["requiere_validacion"] = "no"
        location["motivo_validacion"] = reason
    elif lat is not None or lon is not None:
        location["latitud"] = "No disponible"
        location["longitud"] = "No disponible"
        location["calidad_geo"] = "sospechosa"
        location["requiere_validacion"] = "si"
        location["motivo_validacion"] = "Coordenadas de fuente fuera del bounding box CABA; no mapear"
    return location


def cached_location(cache: dict[tuple[str, str], dict], address: str, barrio: str) -> dict:
    key = (normalize_text(address), normalize_text(barrio))
    if key not in cache:
        cache[key] = normalize_address_offline(address, barrio)
    return cache[key].copy()


def cached_official_location(cache: dict[tuple[str, str, str, str], dict], row: pd.Series, lat_col: str = "latitud", lon_col: str = "longitud") -> dict:
    key = (
        normalize_text(row.get("direccion_original")),
        normalize_text(row.get("barrio_original")),
        normalize_text(row.get(lat_col)),
        normalize_text(row.get(lon_col)),
    )
    if key not in cache:
        cache[key] = official_point_location(
            row.get("direccion_original"),
            row.get("barrio_original"),
            row.get(lat_col),
            row.get(lon_col),
            "Coordenadas provistas por fuente oficial",
        )
    return cache[key].copy()


def load_fiab_geojson() -> pd.DataFrame:
    path = DATA_RAW / "f03_fiab.geojson"
    if not path.exists():
        return pd.DataFrame()
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = []
    for feature in data.get("features", []):
        props = feature.get("properties") or {}
        geometry = feature.get("geometry") or {}
        coordinates = geometry.get("coordinates") or []
        lon = coordinates[0] if len(coordinates) >= 2 else None
        lat = coordinates[1] if len(coordinates) >= 2 else None
        rows.append(
            {
                "id_raw": f"FIAB-{props.get('id', len(rows) + 1)}",
                "id_fuente": "F03",
                "nombre_original": props.get("nombre", ""),
                "tipo_original": "FIAB",
                "direccion_original": props.get("direccion") or props.get("ubicacion") or "",
                "barrio_original": props.get("barrio", ""),
                "comuna_original": props.get("comuna", ""),
                "dias_horarios_original": props.get("dia", ""),
                "horario_original": props.get("horario", ""),
                "productos": props.get("productos", ""),
                "gestion_original": "Ministerio de Espacio Publico",
                "latitud": lat,
                "longitud": lon,
                "url_fuente": SOURCE_CONFIG["F03_FIAB_GEOJSON"].get("dataset_url", ""),
                "download_url": SOURCE_CONFIG["F03_FIAB_GEOJSON"].get("download_url", ""),
                "fecha_consulta": SOURCE_CONFIG["F03_FIAB_GEOJSON"].get("fecha_consulta", TODAY),
                "calidad_dato": "alta",
                "requiere_validacion": "no",
                "motivo_validacion": "Coordenadas provistas por GeoJSON FIAB",
                "observaciones_raw": first_existing(props.get("observacio"), default=""),
                "origen_dato": "datos reales",
                "estado_datos": "datos reales",
            }
        )
    return pd.DataFrame(rows)


def _source_value(source_key: str, field: str, default: str = "") -> str:
    value = SOURCE_CONFIG.get(source_key, {}).get(field, default)
    return "" if value is None else str(value)


def _f03_match_key(value) -> str:
    text = normalize_text(value, case="upper", remove_accents=True)
    return re.sub(r"\W+", " ", text).strip()


def load_f03_ferias_espacios() -> pd.DataFrame:
    path = DATA_RAW / "f03_ferias.csv"
    if not path.exists():
        return pd.DataFrame()
    raw = read_csv(path)
    source_key = "F03_FERIAS"
    rows = []
    for idx, row in raw.iterrows():
        rows.append(
            {
                "id_raw": first_existing(row.get("id"), default=f"FERIA-{idx + 1}"),
                "id_fuente": "F03",
                "tipo_espacio": "Feria especializada",
                "nombre": normalize_proper_name(row.get("nombre")),
                "descripcion": first_existing(row.get("tipo"), row.get("objeto"), default="Feria no alimentaria o especializada"),
                "direccion": first_existing(row.get("direc_norm"), row.get("direccion"), default="No disponible"),
                "barrio": first_existing(row.get("barrio"), default="No determinado"),
                "comuna": first_existing(row.get("comuna"), default="No determinada"),
                "latitud": row.get("lat", ""),
                "longitud": row.get("lng", ""),
                "dias_funcionamiento": first_existing(row.get("dias"), default="No disponible"),
                "horarios": "No disponible",
                "productos": first_existing(row.get("tipo"), default="No disponible"),
                "url_fuente": _source_value(source_key, "dataset_url"),
                "download_url": _source_value(source_key, "download_url"),
                "fecha_consulta": _source_value(source_key, "fecha_consulta", TODAY),
                "origen_dato": "datos reales",
                "estado_datos": "datos reales",
                "calidad_dato": "alta",
                "requiere_validacion": "no",
                "motivo_validacion": "Espacio de feria publicado por fuente oficial",
                "limitaciones": "Feria especializada/no alimentaria; no mezclar con FIAB sin aclaracion metodologica",
                "observaciones": first_existing(row.get("observacio"), default=""),
            }
        )
    return pd.DataFrame(rows)


def load_f03_ferias_lookup() -> dict[str, dict]:
    ferias = load_f03_ferias_espacios()
    if ferias.empty:
        return {}
    return {
        _f03_match_key(row.get("nombre")): row.to_dict()
        for _, row in ferias.iterrows()
        if _f03_match_key(row.get("nombre"))
    }


def load_f03_mercados_espacios() -> pd.DataFrame:
    path = DATA_RAW / "f03_mercados.csv"
    if not path.exists():
        return pd.DataFrame()
    raw = read_csv(path)
    source_key = "F03_MERCADOS"
    rows = []
    for idx, row in raw.iterrows():
        rows.append(
            {
                "id_raw": first_existing(row.get("id"), row.get("nombre_map"), default=f"MERCADO-{idx + 1}"),
                "id_fuente": "F03",
                "tipo_espacio": "Mercado",
                "nombre": normalize_proper_name(row.get("nombre")),
                "descripcion": "Centro de abastecimiento municipal / mercado",
                "direccion": first_existing(row.get("ubicacion"), row.get("arc_street"), default="No disponible"),
                "barrio": first_existing(row.get("barrio"), default="No determinado"),
                "comuna": first_existing(row.get("comuna"), default="No determinada"),
                "latitud": "",
                "longitud": "",
                "dias_funcionamiento": "No disponible",
                "horarios": "No disponible",
                "productos": "No disponible",
                "url_fuente": _source_value(source_key, "dataset_url"),
                "download_url": _source_value(source_key, "download_url"),
                "fecha_consulta": _source_value(source_key, "fecha_consulta", TODAY),
                "origen_dato": "datos reales",
                "estado_datos": "datos reales",
                "calidad_dato": "alta",
                "requiere_validacion": "si",
                "motivo_validacion": "Mercado sin coordenadas de fuente; no geocodificado",
                "limitaciones": "Sin coordenadas de fuente; no mapear hasta contar con geometria oficial",
                "observaciones": first_existing(row.get("nombre_map"), default=""),
            }
        )
    return pd.DataFrame(rows)


def load_f03_mercados_lookup() -> dict[str, dict]:
    mercados = load_f03_mercados_espacios()
    if mercados.empty:
        return {}
    lookup = {}
    for _, row in mercados.iterrows():
        row_dict = row.to_dict()
        for name in (row.get("observaciones"), row.get("nombre")):
            key = _f03_match_key(name)
            if key:
                lookup[key] = row_dict
    return lookup


def top_rubros(values: pd.Series, limit: int = 3) -> str:
    rubros = values.astype(str).map(normalize_text)
    rubros = rubros[rubros.ne("")]
    if rubros.empty:
        return "No disponible"
    return " | ".join(rubros.value_counts().head(limit).index.tolist())


def load_f03_padron_ferias_espacios() -> pd.DataFrame:
    path = DATA_RAW / "f03_ferias_mercados.csv"
    if not path.exists():
        return pd.DataFrame()
    raw = read_csv(path)
    if raw.empty or "feria" not in raw.columns:
        return pd.DataFrame()

    ferias_lookup = load_f03_ferias_lookup()
    mercados_lookup = load_f03_mercados_lookup()
    source_key = "F03"
    rows = []
    category_cache = {}

    for idx, (feria, group) in enumerate(raw.groupby("feria", dropna=False)):
        nombre = first_existing(feria, default=f"Feria sin nombre {idx + 1}")
        key = _f03_match_key(nombre)
        mercado_match = mercados_lookup.get(key)
        feria_match = ferias_lookup.get(key)
        matched = mercado_match or feria_match or {}
        tipo = "Mercado" if mercado_match else "Feria padron"
        gastronomic_count = 0
        for rubro in group.get("rubro", pd.Series(dtype=str)).astype(str):
            cache_key = normalize_text(rubro, case="lower", remove_accents=True)
            category = category_cache.get(cache_key)
            if category is None:
                category = classify_gastronomic_category(rubro)
                category_cache[cache_key] = category
            if category.es_gastronomico == "si":
                gastronomic_count += 1
        es_gastronomico = "si" if tipo == "Mercado" or gastronomic_count > 0 else "no"
        cantidad_puestos = len(group)
        match_note = "con match exacto a mercados" if mercado_match else "con match exacto a ferias con geometria" if feria_match else "sin match exacto a catalogos geograficos F03"
        rows.append(
            {
                "id_raw": f"PADRON-FERIA-{idx + 1:03d}",
                "id_fuente": "F03",
                "tipo_espacio": tipo,
                "nombre": normalize_proper_name(nombre),
                "descripcion": "Espacio agregado desde padron de puestos F03",
                "direccion": first_existing(matched.get("direccion"), default="No disponible"),
                "barrio": first_existing(matched.get("barrio"), default="No determinado"),
                "comuna": first_existing(matched.get("comuna"), default="No determinada"),
                "latitud": first_existing(matched.get("latitud"), default=""),
                "longitud": first_existing(matched.get("longitud"), default=""),
                "dias_funcionamiento": first_existing(matched.get("dias_funcionamiento"), default="No disponible"),
                "horarios": first_existing(matched.get("horarios"), default="No disponible"),
                "productos": top_rubros(group.get("rubro", pd.Series(dtype=str))),
                "cantidad_puestos": str(cantidad_puestos),
                "rubros_principales": top_rubros(group.get("rubro", pd.Series(dtype=str))),
                "cantidad_puestos_gastronomicos": str(gastronomic_count),
                "es_gastronomico": es_gastronomico,
                "url_fuente": _source_value(source_key, "dataset_url"),
                "download_url": _source_value(source_key, "download_url"),
                "fecha_consulta": _source_value(source_key, "fecha_consulta", TODAY),
                "origen_dato": "datos reales",
                "estado_datos": "datos reales",
                "calidad_dato": "alta",
                "requiere_validacion": "si" if not matched else "no",
                "motivo_validacion": f"Padron agregado por feria; {match_note}; no contiene nombres ni apellidos",
                "limitaciones": "Grano espacio agregado desde padron de puestos. No exponer datos personales ni contar titulares/cotitulares como espacios.",
                "observaciones": f"cantidad_puestos={cantidad_puestos}; cantidad_puestos_gastronomicos={gastronomic_count}",
            }
        )
    return pd.DataFrame(rows)


def load_f03_puestos() -> pd.DataFrame:
    path = DATA_RAW / "f03_ferias_mercados.csv"
    if not path.exists():
        return pd.DataFrame()
    raw = read_csv(path)
    source_key = "F03"
    rows = []
    for idx, row in raw.iterrows():
        person_key = f"{normalize_text(row.get('apellido'), case='upper')}|{normalize_text(row.get('nombre'), case='upper')}"
        person_hash = hashlib.sha256(person_key.encode("utf-8")).hexdigest()[:16] if person_key.strip("|") else ""
        rows.append(
            {
                "id_puesto_feria": f"PUESTO{idx + 1:06d}",
                "id_fuente": "F03",
                "feria_nombre": normalize_proper_name(row.get("feria")),
                "puesto": first_existing(row.get("puesto"), default="No disponible"),
                "rubro_puesto": first_existing(row.get("rubro"), default="No disponible"),
                "categoria_titularidad": first_existing(row.get("categoria"), default="No disponible"),
                "persona_hash": person_hash,
                "url_fuente": _source_value(source_key, "dataset_url"),
                "fecha_consulta": _source_value(source_key, "fecha_consulta", TODAY),
                "origen_dato": "datos reales",
                "estado_datos": "datos reales",
                "calidad_dato": "alta",
                "requiere_validacion": "si",
                "motivo_validacion": "Padron de puestos/personas; grano no comparable con espacios",
                "apto_dashboard": "no",
                "uso": "auditoria_interna",
                "limitaciones": "Grano puesto/persona. No usar como KPI de ferias/mercados y no exponer datos personales.",
                "observaciones": "",
            }
        )
    return pd.DataFrame(rows)


def filter_gastronomic_habilitations(hab: pd.DataFrame) -> pd.DataFrame:
    if hab.empty:
        return hab
    category_cache = {}
    keep_indexes = []
    for idx, row in hab.iterrows():
        if not normalize_text(row.get("rubro_original")):
            continue
        category_key = (row.get("rubro_original"), row.get("categoria_gastronomica_inferida"))
        category = category_cache.get(category_key)
        if category is None:
            category = classify_gastronomic_category(*category_key)
            category_cache[category_key] = category
        if category.es_gastronomico == "si":
            keep_indexes.append(idx)
    return hab.loc[keep_indexes].copy()


def source_urls(dim_fuente: pd.DataFrame) -> dict:
    if dim_fuente.empty or "id_fuente" not in dim_fuente.columns:
        return {}
    url_column = "url_base" if "url_base" in dim_fuente.columns else "url"
    return dict(zip(dim_fuente["id_fuente"], dim_fuente.get(url_column, "")))


def build_dim_fuente() -> pd.DataFrame:
    raw = read_seed_csv("raw_fuentes_relevadas.csv")
    rows = []
    for _, row in raw.iterrows():
        rows.append(
            {
                "id_fuente": first_existing(row.get("id_fuente_raw"), row.get("id_fuente")),
                "nombre_fuente": first_existing(row.get("nombre_fuente")),
                "tipo_fuente": first_existing(row.get("tipo_fuente")),
                "organismo_entidad": first_existing(row.get("organismo")),
                "url_base": first_existing(row.get("url")),
                "confiabilidad": first_existing(row.get("calidad_estimada"), default="No disponible"),
                "frecuencia_actualizacion": "No disponible",
                "fecha_consulta": first_existing(row.get("fecha_consulta"), default=TODAY),
                "notas": first_existing(row.get("observaciones"), default=""),
            }
        )
    for source_id in ("F01", "F02", "F03", "F04", "F05"):
        resources = _resource_items(source_id)
        if not resources:
            continue
        first_resource = resources[0][1]
        rows.append(
            {
                "id_fuente": source_id,
                "nombre_fuente": first_resource.get("nombre", first_resource.get("name", source_id)),
                "tipo_fuente": "Oficial / dato abierto",
                "organismo_entidad": first_resource.get("organismo", "GCBA / Buenos Aires Data"),
                "url_base": first_resource.get("dataset_url", "No disponible"),
                "confiabilidad": "Alta" if source_id in {"F02", "F03"} else "Media-Alta",
                "frecuencia_actualizacion": "No disponible",
                "fecha_consulta": first_resource.get("fecha_consulta", TODAY),
                "notas": first_resource.get("limitaciones", ""),
            }
        )
    return pd.DataFrame(rows).drop_duplicates("id_fuente", keep="last")


def build_dim_categoria() -> pd.DataFrame:
    return pd.DataFrame(taxonomy_dataframe_rows())



def _geojson_features(filename: str) -> list[dict]:
    path = DATA_RAW / filename
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    return list(data.get("features") or [])


def _feature_centroid(feature: dict) -> tuple[str, str, str, str]:
    try:
        geom = shape(feature.get("geometry") or {})
        if geom.is_empty:
            return "No disponible", "No disponible", "sin_geo", "Geometria vacia"
        point = geom.centroid
        lon = float(point.x)
        lat = float(point.y)
        if CABA_LAT_MIN <= lat <= CABA_LAT_MAX and CABA_LON_MIN <= lon <= CABA_LON_MAX:
            return f"{lat:.8f}", f"{lon:.8f}", "fuente_oficial", "Centroide calculado desde poligono oficial"
        return f"{lat:.8f}", f"{lon:.8f}", "sospechosa", "Centroide fuera de bounding box CABA"
    except Exception as exc:
        return "No disponible", "No disponible", "sin_geo", f"No se pudo calcular centroide: {exc}"


def _territory_value(props: dict, names: list[str], default: str = "No disponible") -> str:
    for name in names:
        value = props.get(name)
        if value is not None and normalize_text(value):
            return normalize_text(value)
    return default


def build_dim_territorio() -> pd.DataFrame:
    columns = [
        "id_territorio",
        "barrio",
        "barrio_normalizado",
        "comuna",
        "centroide_latitud",
        "centroide_longitud",
        "fuente_geojson",
        "fecha_consulta",
        "calidad_geo",
        "requiere_validacion",
        "motivo_validacion",
    ]
    features = _geojson_features("geo_barrios.geojson")
    rows = []
    for idx, feature in enumerate(features, start=1):
        props = feature.get("properties") or {}
        barrio = _territory_value(props, ["barrio", "BARRIO", "nombre", "NOMBRE", "name"], default=f"Barrio {idx}")
        comuna = normalize_comuna_value(_territory_value(props, ["comuna", "COMUNA"], default="No determinada"))
        lat, lon, quality, motive = _feature_centroid(feature)
        rows.append(
            {
                "id_territorio": f"T{idx:03d}",
                "barrio": normalize_proper_name(barrio),
                "barrio_normalizado": normalize_text(barrio, case="upper", remove_accents=True),
                "comuna": comuna,
                "centroide_latitud": lat,
                "centroide_longitud": lon,
                "fuente_geojson": "geo_barrios.geojson",
                "fecha_consulta": SOURCE_CONFIG.get("BARRIOS_GEOJSON", {}).get("fecha_consulta", TODAY),
                "calidad_geo": quality,
                "requiere_validacion": "no" if quality == "fuente_oficial" else "si",
                "motivo_validacion": motive,
            }
        )
    if not rows:
        return pd.DataFrame(columns=columns)
    return pd.DataFrame(rows, columns=columns).drop_duplicates("barrio_normalizado", keep="first")

def build_locations(est: pd.DataFrame, hab: pd.DataFrame, espacios_f03: pd.DataFrame, eventos: pd.DataFrame) -> pd.DataFrame:
    rows = [
        {
            "id_ubicacion": UNKNOWN_LOCATION_ID,
            "direccion_original": "No determinada",
            "direccion_normalizada": "No determinada",
            "barrio": "No determinado",
            "comuna": "No determinada",
            "latitud": "No disponible",
            "longitud": "No disponible",
            "codigo_postal": "No disponible",
            "zona": "No clasificada",
            "calidad_geo": "sin_geo",
            "requiere_validacion": "si",
            "motivo_validacion": "Ubicacion centinela para eventos o registros sin sede fija/determinada",
        }
    ]
    location_cache: dict[tuple[str, str], dict] = {}
    official_location_cache: dict[tuple[str, str, str, str], dict] = {}

    for df, address_col, barrio_col in (
        (hab, "direccion_original", "barrio_original"),
    ):
        for _, row in df.iterrows():
            rows.append(cached_location(location_cache, row.get(address_col), row.get(barrio_col)))

    for _, row in eventos.iterrows():
        location = first_existing(row.get("direccion_original"), row.get("ubicacion_original"), default="")
        barrio_raw = normalize_text(row.get("barrio_original"))
        if is_sentinel(location) or is_sentinel(barrio_raw) or any(marker in location.lower() for marker in ("adherid", "a relevar", "500+")):
            continue
        rows.append(cached_location(location_cache, location, barrio_raw))

    for _, row in est.iterrows():
        rows.append(cached_official_location(official_location_cache, row))

    for _, row in espacios_f03.iterrows():
        location_row = pd.Series(
            {
                "direccion_original": row.get("direccion"),
                "barrio_original": row.get("barrio"),
                "latitud": row.get("latitud"),
                "longitud": row.get("longitud"),
            }
        )
        if normalize_text(row.get("latitud")) and normalize_text(row.get("longitud")):
            rows.append(cached_official_location(official_location_cache, location_row))
        else:
            rows.append(cached_location(location_cache, row.get("direccion"), row.get("barrio")))

    df = pd.DataFrame(rows).drop_duplicates("id_ubicacion", keep="last")
    return enrich_locations_with_geo_cache(df)


def enrich_locations_with_geo_cache(dim_ubicacion: pd.DataFrame, cache_path: Path = GEO_CACHE_PATH) -> pd.DataFrame:
    if dim_ubicacion.empty or not cache_path.exists():
        return dim_ubicacion
    cache = read_csv(cache_path)
    required = {"direccion_original", "latitud", "longitud", "estado", "fecha_consulta"}
    if cache.empty or not required.issubset(cache.columns):
        return dim_ubicacion

    usable = cache[cache["estado"].astype(str).isin(["exacta", "aproximada"])].copy()
    if usable.empty:
        return dim_ubicacion
    usable["lat_num"] = usable["latitud"].map(parse_coordinate)
    usable["lon_num"] = usable["longitud"].map(parse_coordinate)
    usable = usable[
        usable.apply(lambda row: in_caba_bounds(row["lat_num"], row["lon_num"]), axis=1)
        & usable["fecha_consulta"].astype(str).str.strip().ne("")
    ].copy()
    if usable.empty:
        return dim_ubicacion

    by_address = {
        geo_cache_key(row["direccion_original"]): row
        for _, row in usable.iterrows()
        if geo_cache_key(row.get("direccion_original"))
    }
    result = dim_ubicacion.copy()
    for idx, row in result.iterrows():
        if row.get("calidad_geo") == "fuente_oficial":
            continue
        match = by_address.get(geo_cache_key(row.get("direccion_original")))
        if match is None:
            continue
        estado = str(match.get("estado", ""))
        result.at[idx, "latitud"] = format_coordinate(parse_coordinate(match.get("latitud")))
        result.at[idx, "longitud"] = format_coordinate(parse_coordinate(match.get("longitud")))
        result.at[idx, "calidad_geo"] = "usig_exacta" if estado == "exacta" else "usig_aproximada"
        result.at[idx, "direccion_normalizada"] = first_existing(match.get("direccion_normalizada"), row.get("direccion_normalizada"), default="Pendiente USIG")
        barrio_usig = first_existing(match.get("barrio_usig"), default="")
        comuna_usig = first_existing(match.get("comuna_usig"), default="")
        if barrio_usig:
            result.at[idx, "barrio"] = barrio_usig
        if comuna_usig:
            result.at[idx, "comuna"] = normalize_comuna_value(comuna_usig)
        result.at[idx, "requiere_validacion"] = "no" if estado == "exacta" else "si"
        result.at[idx, "motivo_validacion"] = f"Geocodificacion USIG desde geo_cache.csv; estado={estado}; precision={first_existing(match.get('precision'), default='No disponible')}"
    return result


def build_dim_organizador(eventos: pd.DataFrame) -> pd.DataFrame:
    rows = [
        {
            "id_organizador": "O000",
            "nombre_organizador": "No normalizado",
            "tipo_organizador": "No determinado",
            "sector": "gastronomia",
            "web": "No disponible",
            "observaciones": "Centinela para organizadores pendientes de normalizacion",
        },
        {
            "id_organizador": "O999",
            "nombre_organizador": "Privado / mixto no normalizado",
            "tipo_organizador": "privado/mixto",
            "sector": "gastronomia",
            "web": "No disponible",
            "observaciones": "Organizador detectado en texto, requiere normalizacion manual",
        },
    ]
    seen = {row["id_organizador"] for row in rows}
    by_name: dict[str, str] = {}
    known = {
        "afadhya": ("O001", "AFADHYA", "privado/mixto"),
        "apyce": ("O002", "APYCE", "privado/mixto"),
        "appyce": ("O002", "APYCE", "privado/mixto"),
        "dg desarrollo gastronomico": ("O003", "DG Desarrollo Gastronomico", "publico"),
        "ba capital gastronomica": ("O004", "BA Capital Gastronomica", "publico/mixto"),
    }
    for _, row in eventos.iterrows():
        text = normalize_text(row.get("organizador_original"), case="lower", remove_accents=True)
        for keyword, (org_id, name, org_type) in known.items():
            if keyword in text and org_id not in seen:
                rows.append(
                    {
                        "id_organizador": org_id,
                        "nombre_organizador": name,
                        "tipo_organizador": org_type,
                        "sector": "gastronomia",
                        "web": "No disponible",
                        "observaciones": "Inferido desde raw_eventos_gastronomicos.csv",
                    }
                )
                seen.add(org_id)
                by_name[normalize_text(name, case="lower", remove_accents=True)] = org_id
        original = first_existing(row.get("organizador_original"), default="")
        if not original or is_sentinel(original):
            continue
        normalized = normalize_text(original, case="lower", remove_accents=True)
        if normalized in by_name:
            continue
        if any(keyword in normalized for keyword in known):
            continue
        org_id = f"O{len(rows):03d}"
        rows.append(
            {
                "id_organizador": org_id,
                "nombre_organizador": normalize_proper_name(original),
                "tipo_organizador": first_existing(row.get("tipo_organizador"), default="No determinado"),
                "sector": "gastronomia",
                "web": "No disponible",
                "observaciones": "Inferido desde F04 relevamiento manual trazable",
            }
        )
        seen.add(org_id)
        by_name[normalized] = org_id
    return pd.DataFrame(rows).drop_duplicates("id_organizador").sort_values("id_organizador")


def infer_organizer_id(value: str) -> str:
    text = normalize_text(value, case="lower", remove_accents=True)
    if "afadhya" in text:
        return "O001"
    if "appyce" in text or "apyce" in text:
        return "O002"
    if "ba capital gastronomica" in text or "dg desarrollo gastronomico" in text:
        return "O004"
    if "privado" in text:
        return "O999"
    return "O000"


def organizer_lookup(dim_organizador: pd.DataFrame) -> dict[str, str]:
    if dim_organizador.empty:
        return {}
    return {
        normalize_text(row["nombre_organizador"], case="lower", remove_accents=True): row["id_organizador"]
        for _, row in dim_organizador.iterrows()
    }


def build_fact_establecimiento(est: pd.DataFrame, dim_fuente: pd.DataFrame) -> pd.DataFrame:
    urls = source_urls(dim_fuente)
    rows = []
    category_cache = {}
    location_cache: dict[tuple[str, str, str, str], dict] = {}
    for idx, row in est.iterrows():
        category_key = (row.get("categoria_original"), row.get("nombre_original"))
        category = category_cache.get(category_key)
        if category is None:
            category = classify_gastronomic_category(*category_key)
            category_cache[category_key] = category
        location_id = cached_official_location(location_cache, row)["id_ubicacion"]
        source_id = first_existing(row.get("id_fuente"), default="F01")
        rows.append(
            {
                "id_establecimiento": f"EST{idx + 1:05d}",
                "nombre": normalize_proper_name(row.get("nombre_original")),
                "id_categoria": category.id_categoria,
                "id_ubicacion": location_id,
                "id_fuente": source_id,
                "url_fuente": first_existing(row.get("url_fuente"), default=urls.get(source_id, "No disponible")),
                "fecha_consulta": first_existing(row.get("fecha_consulta"), default=TODAY),
                "estado": "sin_verificar",
                "web": "No disponible",
                "redes": "No disponible",
                "telefono": "No disponible",
                "fecha_alta_detectada": "No disponible",
                "fecha_ultima_actualizacion": first_existing(row.get("fecha_extraccion"), default=TODAY),
                "calidad_dato": first_existing(row.get("calidad_dato"), default="media"),
                "requiere_validacion": first_existing(row.get("requiere_validacion"), default="si"),
                "motivo_validacion": first_existing(row.get("motivo_validacion"), default="Seed pendiente de cruce con fuente real"),
                "observaciones": first_existing(row.get("observaciones_raw"), default=""),
                "es_gastronomico": category.es_gastronomico,
                "categoria_gastronomica_inferida": category.categoria_gastronomica_inferida,
                "confianza_categoria": category.confianza_categoria,
                "motivo_categoria": category.motivo_categoria,
                "origen_dato": first_existing(row.get("origen_dato"), default="datos seed"),
                "estado_datos": first_existing(row.get("estado_datos"), default="datos seed"),
                "anio_fuente": "",
                "periodo_fuente": "",
            }
        )

    return pd.DataFrame(rows)


def build_fact_habilitacion_gastronomica(hab: pd.DataFrame, dim_fuente: pd.DataFrame) -> pd.DataFrame:
    urls = source_urls(dim_fuente)
    rows = []
    category_cache = {}
    location_cache: dict[tuple[str, str], dict] = {}
    for idx, row in hab.iterrows():
        if not normalize_text(row.get("rubro_original")):
            continue
        category_key = (row.get("rubro_original"), row.get("categoria_gastronomica_inferida"))
        category = category_cache.get(category_key)
        if category is None:
            category = classify_gastronomic_category(*category_key)
            category_cache[category_key] = category
        if category.es_gastronomico != "si":
            continue
        source_id = first_existing(row.get("id_fuente"), default="F02")
        periodo_fuente = first_existing(row.get("periodo_fuente"), default="")
        anio_fuente = first_existing(row.get("anio_fuente"), default="")
        is_f02_2025 = source_id == "F02" and (periodo_fuente == "2025" or anio_fuente == "2025")
        location = cached_location(location_cache, row.get("direccion_original"), row.get("barrio_original"))
        if location["comuna"] == "No determinada" and normalize_text(row.get("comuna_original")):
            location["comuna"] = normalize_comuna_value(row.get("comuna_original"))
        else:
            location["comuna"] = normalize_comuna_value(location["comuna"])
        requiere_validacion = "si" if is_f02_2025 else first_existing(row.get("requiere_validacion"), default="si")
        motivo_validacion = F02_2025_VALIDATION_MOTIVE if is_f02_2025 else first_existing(
            row.get("motivo_validacion"),
            default="Clasificacion gastronomica inferida desde rubro F02; validar casos ambiguos",
        )
        source_url = first_existing(row.get("url_fuente"), default=urls.get(source_id, "No disponible"))
        rows.append(
            {
                "id_habilitacion": f"HAB{idx + 1:07d}",
                "id_fuente": source_id,
                "url_fuente": source_url,
                "fecha_consulta": first_existing(row.get("fecha_consulta"), default=TODAY),
                "periodo_fuente": periodo_fuente,
                "anio_fuente": anio_fuente,
                "fecha_habilitacion": first_existing(row.get("fecha_habilitacion"), default="No disponible"),
                "descripcion_rubro_original": first_existing(row.get("rubro_original"), default="No disponible"),
                "descripcion_rubro_normalizada": normalize_text(row.get("rubro_original"), case="lower", remove_accents=True),
                "es_gastronomico": category.es_gastronomico,
                "categoria_gastronomica_inferida": category.categoria_gastronomica_inferida,
                "confianza_categoria": category.confianza_categoria,
                "motivo_categoria": category.motivo_categoria,
                "id_ubicacion": location["id_ubicacion"],
                "direccion_original": first_existing(row.get("direccion_original"), default="No disponible"),
                "barrio": location["barrio"],
                "comuna": location["comuna"],
                "superficie": first_existing(row.get("superficie"), default="No disponible"),
                "origen_dato": first_existing(row.get("origen_dato"), default="datos reales parciales"),
                "estado_datos": first_existing(row.get("estado_datos"), default="datos reales"),
                "calidad_dato": first_existing(row.get("calidad_dato"), default="alta"),
                "requiere_validacion": requiere_validacion,
                "motivo_validacion": motivo_validacion,
                "observaciones": first_existing(row.get("observaciones_raw"), default=""),
            }
        )
    return pd.DataFrame(rows)


def build_fact_evento(eventos: pd.DataFrame, dim_fuente: pd.DataFrame, dim_organizador: pd.DataFrame) -> pd.DataFrame:
    urls = source_urls(dim_fuente)
    org_lookup = organizer_lookup(dim_organizador)
    location_cache: dict[tuple[str, str], dict] = {}
    rows = []
    columns = [
        "id_evento",
        "nombre_evento",
        "descripcion",
        "fecha_inicio",
        "fecha_fin",
        "anio",
        "periodicidad",
        "id_ubicacion",
        "ubicacion_original",
        "direccion_original",
        "barrio",
        "comuna",
        "id_organizador",
        "tipo_organizador",
        "id_fuente",
        "url_fuente",
        "fecha_consulta",
        "tipo_evento",
        "categoria_gastronomica",
        "gratuito",
        "requiere_inscripcion",
        "cantidad_asistentes_estimada",
        "cantidad_puestos_estimada",
        "apoyo_gcba",
        "organismo_gcba_relacionado",
        "area_gcba_relacionada",
        "tipo_vinculo_gcba",
        "estado",
        "link_evento",
        "fuente",
        "tipo_fuente",
        "calidad_dato_original",
        "calidad_dato_normalizada",
        "calidad_dato",
        "requiere_validacion",
        "motivo_validacion",
        "apto_dashboard",
        "fecha_completa",
        "limitaciones",
        "observaciones",
        "origen_dato",
        "estado_datos",
    ]
    for idx, row in eventos.iterrows():
        location_text = first_existing(row.get("direccion_original"), row.get("ubicacion_original"), default="")
        barrio_raw = normalize_text(row.get("barrio_original"))
        if is_sentinel(location_text) or is_sentinel(barrio_raw):
            location = {
                "id_ubicacion": UNKNOWN_LOCATION_ID,
                "barrio": first_existing(row.get("barrio_original"), default="No determinado"),
                "comuna": first_existing(row.get("comuna_original"), default="No determinada"),
            }
        else:
            location = cached_location(location_cache, location_text, barrio_raw)
            if normalize_text(row.get("comuna_original")):
                location["comuna"] = normalize_text(row.get("comuna_original"))
        source_id = first_existing(row.get("id_fuente"), default="F04")
        if source_id != "F04":
            source_id = "F04"
        organizer_name = first_existing(row.get("organizador_original"), default="")
        org_id = org_lookup.get(normalize_text(organizer_name, case="lower", remove_accents=True), infer_organizer_id(organizer_name))
        quality, quality_original = normalize_quality(row.get("calidad_dato"))
        apto = normalize_dashboard_flag(row.get("apto_dashboard"))
        requiere_validacion = normalize_yes_no(row.get("requiere_validacion"), default="si")
        fecha_completa = "si" if has_complete_date(row.get("fecha_inicio")) and has_complete_date(row.get("fecha_fin")) else "no"
        rows.append(
            {
                "id_evento": first_existing(row.get("id_raw"), default=f"F04-{idx + 1:03d}"),
                "nombre_evento": normalize_proper_name(row.get("nombre_evento")),
                "descripcion": first_existing(row.get("descripcion"), default=""),
                "fecha_inicio": first_existing(row.get("fecha_inicio"), default="No disponible"),
                "fecha_fin": first_existing(row.get("fecha_fin"), default="No disponible"),
                "anio": first_existing(row.get("anio"), default="No disponible"),
                "periodicidad": first_existing(row.get("periodicidad"), default="No disponible"),
                "id_ubicacion": location["id_ubicacion"],
                "ubicacion_original": first_existing(row.get("ubicacion_original"), default="No disponible"),
                "direccion_original": first_existing(row.get("direccion_original"), default="No disponible"),
                "barrio": location["barrio"],
                "comuna": location["comuna"],
                "id_organizador": org_id,
                "tipo_organizador": first_existing(row.get("tipo_organizador"), default="No disponible"),
                "id_fuente": source_id,
                "url_fuente": first_existing(row.get("url_fuente"), default=urls.get(source_id, "No disponible")),
                "fecha_consulta": first_existing(row.get("fecha_consulta"), default=TODAY),
                "tipo_evento": first_existing(row.get("tipo_evento"), default="evento gastronomico"),
                "categoria_gastronomica": first_existing(row.get("categoria_gastronomica"), default="No disponible"),
                "gratuito": first_existing(row.get("gratuito"), default="No disponible"),
                "requiere_inscripcion": first_existing(row.get("requiere_inscripcion"), default="No disponible"),
                "cantidad_asistentes_estimada": first_existing(row.get("cantidad_asistentes"), default="No disponible"),
                "cantidad_puestos_estimada": first_existing(row.get("cantidad_puestos"), default="No disponible"),
                "apoyo_gcba": first_existing(row.get("apoyo_gcba"), default="No disponible"),
                "organismo_gcba_relacionado": first_existing(row.get("organismo_gcba_relacionado"), default="No disponible"),
                "area_gcba_relacionada": first_existing(row.get("area_gcba_relacionada"), default="No disponible"),
                "tipo_vinculo_gcba": first_existing(row.get("tipo_vinculo_gcba"), default="Requiere validacion"),
                "estado": "semiestructurado",
                "link_evento": first_existing(row.get("url_fuente"), default="No disponible"),
                "fuente": first_existing(row.get("fuente"), default="No disponible"),
                "tipo_fuente": first_existing(row.get("tipo_fuente"), default="No disponible"),
                "calidad_dato_original": quality_original,
                "calidad_dato_normalizada": quality,
                "calidad_dato": quality,
                "requiere_validacion": requiere_validacion,
                "motivo_validacion": first_existing(row.get("motivo_validacion"), default="No disponible"),
                "apto_dashboard": apto,
                "fecha_completa": fecha_completa,
                "limitaciones": first_existing(row.get("limitaciones"), default="No disponible"),
                "observaciones": first_existing(row.get("observaciones_raw"), default=""),
                "origen_dato": "relevamiento_manual_trazable",
                "estado_datos": "datos reales semiestructurados",
            }
        )
    return pd.DataFrame(rows, columns=columns)


def _space_location(row: pd.Series, official_location_cache: dict, location_cache: dict) -> dict:
    location_row = pd.Series(
        {
            "direccion_original": row.get("direccion"),
            "barrio_original": row.get("barrio"),
            "latitud": row.get("latitud"),
            "longitud": row.get("longitud"),
        }
    )
    if normalize_text(row.get("latitud")) and normalize_text(row.get("longitud")):
        return cached_official_location(official_location_cache, location_row)
    return cached_location(location_cache, row.get("direccion"), row.get("barrio"))


def build_fact_espacio_feria_mercado(espacios: pd.DataFrame) -> pd.DataFrame:
    rows = []
    location_cache: dict[tuple[str, str, str, str], dict] = {}
    official_location_cache: dict[tuple[str, str, str, str], dict] = {}
    for idx, row in espacios.iterrows():
        source_id = first_existing(row.get("id_fuente"), default="F03")
        location = _space_location(row, official_location_cache, location_cache)
        if location["comuna"] == "No determinada" and normalize_text(row.get("comuna")):
            location["comuna"] = normalize_comuna_value(row.get("comuna"))
        else:
            location["comuna"] = normalize_comuna_value(location["comuna"])
        tipo = first_existing(row.get("tipo_espacio"), default="No disponible")
        prefix = "FIAB" if tipo == "FIAB" else "ESP"
        es_gastronomico = first_existing(row.get("es_gastronomico"), default="si" if tipo in {"FIAB", "Mercado"} else "no")
        cantidad_puestos = first_existing(row.get("cantidad_puestos"), default="No aplica")
        rubros_principales = first_existing(row.get("rubros_principales"), row.get("productos"), default="No disponible")
        cantidad_puestos_gastronomicos = first_existing(row.get("cantidad_puestos_gastronomicos"), default="No aplica")
        rows.append(
            {
                "id_espacio": f"{prefix}{idx + 1:05d}",
                "id_fuente": source_id,
                "tipo_espacio": tipo,
                "nombre": normalize_proper_name(row.get("nombre")),
                "descripcion": first_existing(row.get("descripcion"), default="No disponible"),
                "direccion": first_existing(row.get("direccion"), default="No disponible"),
                "barrio": location["barrio"],
                "comuna": location["comuna"],
                "latitud": location["latitud"],
                "longitud": location["longitud"],
                "calidad_geo": location["calidad_geo"],
                "dias_funcionamiento": first_existing(row.get("dias_funcionamiento"), default="No disponible"),
                "horarios": first_existing(row.get("horarios"), default="No disponible"),
                "productos": first_existing(row.get("productos"), default="No disponible"),
                "cantidad_puestos": cantidad_puestos,
                "rubros_principales": rubros_principales,
                "cantidad_puestos_gastronomicos": cantidad_puestos_gastronomicos,
                "es_gastronomico": es_gastronomico,
                "url_fuente": first_existing(row.get("url_fuente"), default="No disponible"),
                "fecha_consulta": first_existing(row.get("fecha_consulta"), default=TODAY),
                "origen_dato": first_existing(row.get("origen_dato"), default="datos reales"),
                "estado_datos": first_existing(row.get("estado_datos"), default="datos reales"),
                "calidad_dato": first_existing(row.get("calidad_dato"), default="alta"),
                "requiere_validacion": first_existing(row.get("requiere_validacion"), default=location["requiere_validacion"]),
                "motivo_validacion": first_existing(row.get("motivo_validacion"), default=location["motivo_validacion"]),
                "limitaciones": first_existing(row.get("limitaciones"), default="No disponible"),
                "observaciones": first_existing(row.get("observaciones"), default=""),
                "id_ubicacion": location["id_ubicacion"],
            }
        )
    return pd.DataFrame(rows)


def build_fact_mercado_feria_compat(espacios: pd.DataFrame) -> pd.DataFrame:
    if espacios.empty:
        return pd.DataFrame()
    compat = espacios.copy()
    compat["id_mercado_feria"] = compat["id_espacio"]
    compat["gestion"] = "No disponible"
    if "cantidad_puestos" not in compat.columns:
        compat["cantidad_puestos"] = "No aplica"
    compat["rubros"] = compat.get("rubros_principales", compat.get("productos", "No disponible"))
    compat["estado"] = "activo"
    compat["link"] = compat.get("url_fuente", "No disponible")
    return compat[
        [
            "id_mercado_feria",
            "nombre",
            "tipo_espacio",
            "id_ubicacion",
            "gestion",
            "dias_funcionamiento",
            "horarios",
            "cantidad_puestos",
            "rubros",
            "cantidad_puestos_gastronomicos",
            "es_gastronomico",
            "estado",
            "id_fuente",
            "url_fuente",
            "fecha_consulta",
            "link",
            "calidad_dato",
            "requiere_validacion",
            "motivo_validacion",
            "observaciones",
            "origen_dato",
            "estado_datos",
        ]
    ]


def build_fact_programa(programas: pd.DataFrame, dim_fuente: pd.DataFrame) -> pd.DataFrame:
    urls = source_urls(dim_fuente)
    columns = [
        "id_programa",
        "nombre_programa",
        "organismo_responsable",
        "area_dependiente",
        "fecha_inicio",
        "fecha_fin",
        "anio_inicio",
        "estado",
        "tipo_programa",
        "descripcion",
        "objetivo",
        "beneficiarios",
        "alcance_geografico",
        "barrios_comunas",
        "normativa_relacionada",
        "presupuesto",
        "resultados",
        "metricas_publicadas",
        "id_fuente",
        "url_fuente",
        "fecha_consulta",
        "link",
        "fuente",
        "tipo_fuente",
        "calidad_dato_original",
        "calidad_dato_normalizada",
        "calidad_dato",
        "requiere_validacion",
        "motivo_validacion",
        "apto_dashboard",
        "vigencia_clara",
        "limitaciones",
        "observaciones",
        "origen_dato",
        "estado_datos",
    ]
    if programas.empty:
        return pd.DataFrame(columns=columns)
    rows = []
    for idx, row in programas.iterrows():
        source_id = first_existing(row.get("id_fuente"), default="F05")
        if source_id != "F05":
            source_id = "F05"
        quality, quality_original = normalize_quality(row.get("calidad_dato"))
        estado = first_existing(row.get("estado"), default="No disponible")
        rows.append(
            {
                "id_programa": first_existing(row.get("id_raw"), default=f"F05-{idx + 1:03d}"),
                "nombre_programa": normalize_proper_name(row.get("nombre_programa")),
                "organismo_responsable": first_existing(row.get("organismo_responsable"), default="No disponible"),
                "area_dependiente": first_existing(row.get("area_dependiente"), default="No disponible"),
                "fecha_inicio": first_existing(row.get("fecha_inicio"), default="No disponible"),
                "fecha_fin": first_existing(row.get("fecha_fin"), default="No disponible"),
                "anio_inicio": first_existing(row.get("anio_inicio"), default="No disponible"),
                "estado": estado,
                "tipo_programa": first_existing(row.get("tipo_programa"), default="No disponible"),
                "descripcion": first_existing(row.get("descripcion"), default=""),
                "objetivo": first_existing(row.get("objetivo"), default="No disponible"),
                "beneficiarios": first_existing(row.get("beneficiarios"), default="No disponible"),
                "alcance_geografico": first_existing(row.get("alcance_geografico"), default="No disponible"),
                "barrios_comunas": first_existing(row.get("barrios_comunas"), default="No disponible"),
                "normativa_relacionada": first_existing(row.get("normativa_relacionada"), default="No disponible"),
                "presupuesto": first_existing(row.get("presupuesto"), default="No disponible"),
                "resultados": first_existing(row.get("resultados_publicados"), default="No disponible"),
                "metricas_publicadas": first_existing(row.get("metricas_publicadas"), default="No disponible"),
                "id_fuente": source_id,
                "url_fuente": first_existing(row.get("url_fuente"), default=urls.get(source_id, "No disponible")),
                "fecha_consulta": first_existing(row.get("fecha_consulta"), default=TODAY),
                "link": first_existing(row.get("url_fuente"), default="No disponible"),
                "fuente": first_existing(row.get("fuente"), default="No disponible"),
                "tipo_fuente": first_existing(row.get("tipo_fuente"), default="No disponible"),
                "calidad_dato_original": quality_original,
                "calidad_dato_normalizada": quality,
                "calidad_dato": quality,
                "requiere_validacion": normalize_yes_no(row.get("requiere_validacion"), default="si"),
                "motivo_validacion": first_existing(row.get("motivo_validacion"), default="No disponible"),
                "apto_dashboard": normalize_dashboard_flag(row.get("apto_dashboard")),
                "vigencia_clara": "no" if "requiere validacion" in normalize_text(estado, case="lower", remove_accents=True) else "si",
                "limitaciones": first_existing(row.get("limitaciones"), default="No disponible"),
                "observaciones": first_existing(row.get("observaciones_raw"), default=""),
                "origen_dato": "relevamiento_manual_trazable",
                "estado_datos": "datos reales semiestructurados",
            }
        )
    return pd.DataFrame(rows, columns=columns)


def build_puente_evento_programa(fact_evento: pd.DataFrame, fact_programa: pd.DataFrame) -> pd.DataFrame:
    event_ids = set(fact_evento.get("id_evento", pd.Series(dtype=str)))
    program_ids = set(fact_programa.get("id_programa", pd.Series(dtype=str)))
    links = [
        ("F04-001", "F05-001", "Cafecito BA vinculado al programa marco BA Capital Gastronomica"),
        ("F04-001", "F05-009", "Convocatoria Cafecito BA 2026 como instrumento puntual"),
        ("F04-015", "F05-008", "Sabores del Mundo realizado en mercados/patios gastronomicos"),
        ("F04-016", "F05-008", "Sabores del Mundo realizado en mercados/patios gastronomicos"),
        ("F04-017", "F05-008", "Sabores del Mundo realizado en mercados/patios gastronomicos"),
        ("F04-018", "F05-008", "Sabores del Mundo realizado en mercados/patios gastronomicos"),
        ("F04-024", "F05-003", "Concurso Mejor Cafe Notable vinculado a Bares Notables"),
        ("F04-007", "F05-002", "Vendimia BA vinculada al Distrito del Vino"),
        ("F04-010", "F05-001", "Pinto Bodegon vinculado al programa marco BA Capital Gastronomica"),
        ("F04-011", "F05-001", "Pinto Bodegon vinculado al programa marco BA Capital Gastronomica"),
    ]
    rows = [
        {"id_evento": event_id, "id_programa": program_id, "tipo_vinculo": "vinculo_explicito", "observaciones": note}
        for event_id, program_id, note in links
        if event_id in event_ids and program_id in program_ids
    ]
    return pd.DataFrame(rows, columns=["id_evento", "id_programa", "tipo_vinculo", "observaciones"])


def main() -> int:
    parser = argparse.ArgumentParser(description="Construye data/processed desde datos reales o seeds de desarrollo.")
    parser.add_argument("--strict-real", action="store_true", help="Falla si se usan seeds o faltan F01/F02/F03 reales o F04/F05 semiestructurados.")
    args = parser.parse_args()

    est, est_reports = load_source_data("F01")
    hab, hab_reports = load_source_data("F02")
    _f03_contract, ferias_reports = load_source_data("F03")
    f03_padron_ferias = load_f03_padron_ferias_espacios()
    f03_ferias_catalogo = load_f03_ferias_espacios()
    f03_mercados_catalogo = load_f03_mercados_espacios()
    padron_keys = set(f03_padron_ferias["nombre"].map(_f03_match_key)) if not f03_padron_ferias.empty else set()
    if not f03_ferias_catalogo.empty:
        f03_ferias_catalogo = f03_ferias_catalogo[
            ~f03_ferias_catalogo["nombre"].map(_f03_match_key).isin(padron_keys)
        ].copy()
        f03_ferias_catalogo["cantidad_puestos"] = "No disponible"
        f03_ferias_catalogo["rubros_principales"] = f03_ferias_catalogo.get("productos", "No disponible")
        f03_ferias_catalogo["cantidad_puestos_gastronomicos"] = "No disponible"
        f03_ferias_catalogo["es_gastronomico"] = "no"
    if not f03_mercados_catalogo.empty:
        f03_mercados_catalogo = f03_mercados_catalogo[
            ~f03_mercados_catalogo["observaciones"].map(_f03_match_key).isin(padron_keys)
            & ~f03_mercados_catalogo["nombre"].map(_f03_match_key).isin(padron_keys)
        ].copy()
        f03_mercados_catalogo["cantidad_puestos"] = "No disponible"
        f03_mercados_catalogo["rubros_principales"] = f03_mercados_catalogo.get("productos", "No disponible")
        f03_mercados_catalogo["cantidad_puestos_gastronomicos"] = "No disponible"
        f03_mercados_catalogo["es_gastronomico"] = "si"
    fiab = load_fiab_geojson()
    fiab_espacios = fiab.rename(
        columns={
            "nombre_original": "nombre",
            "direccion_original": "direccion",
            "barrio_original": "barrio",
            "comuna_original": "comuna",
            "dias_horarios_original": "dias_funcionamiento",
            "horario_original": "horarios",
            "tipo_original": "tipo_espacio",
        }
    )
    if not fiab_espacios.empty:
        fiab_espacios["cantidad_puestos"] = "No aplica"
        fiab_espacios["rubros_principales"] = fiab_espacios.get("productos", "No disponible")
        fiab_espacios["cantidad_puestos_gastronomicos"] = "No aplica"
        fiab_espacios["es_gastronomico"] = "si"
        fiab_espacios["limitaciones"] = "FIAB es capa de abastecimiento barrial; no mezclar con ferias especializadas sin aclaracion."
    f03_espacios = pd.concat([f03_padron_ferias, f03_ferias_catalogo, f03_mercados_catalogo, fiab_espacios], ignore_index=True)
    f03_puestos = load_f03_puestos()
    eventos, eventos_reports = load_source_data("F04")
    programas, programas_reports = load_source_data("F05")
    hab_gastronomica = filter_gastronomic_habilitations(hab)
    reports = [*est_reports, *hab_reports, *ferias_reports, *eventos_reports, *programas_reports]
    write_contract_reports(reports)
    for report in reports:
        if report.origin == "seed":
            print(f"WARNING {report.source_id}: usando fallback seed desde {report.path}; no apto para dashboard real")
        elif report.origin == "real":
            print(f"OK {report.source_id}: usando CSV real desde {report.path}")
        else:
            print(f"WARNING {report.source_id}: no se encontro archivo real ni seed")

    if args.strict_real:
        errors = strict_real_errors(reports, eventos)
        if errors:
            print("ERROR --strict-real no puede construir el modelo:")
            for error in errors:
                print(f"ERROR {error}")
            print("Accion: cargar CSV reales F01/F02/F03 y CSV semiestructurados F04/F05 en data/raw/ y volver a correr.")
            return 1

    dim_fuente = build_dim_fuente()
    dim_categoria = build_dim_categoria()
    dim_ubicacion = build_locations(est, hab_gastronomica, f03_espacios, eventos)
    dim_territorio = build_dim_territorio()
    dim_organizador = build_dim_organizador(eventos)
    fact_establecimiento = build_fact_establecimiento(est, dim_fuente)
    fact_habilitacion = build_fact_habilitacion_gastronomica(hab_gastronomica, dim_fuente)
    fact_evento = build_fact_evento(eventos, dim_fuente, dim_organizador)
    fact_espacio_feria_mercado = build_fact_espacio_feria_mercado(f03_espacios)
    fact_mercado = build_fact_mercado_feria_compat(fact_espacio_feria_mercado)
    fact_programa = build_fact_programa(programas, dim_fuente)
    puente_evento_programa = build_puente_evento_programa(fact_evento, fact_programa)

    write_csv(dim_fuente, "dim_fuente.csv")
    write_csv(dim_ubicacion, "dim_ubicacion.csv")
    write_csv(dim_territorio, "dim_territorio.csv")
    write_csv(dim_categoria, "dim_categoria_gastronomica.csv")
    write_csv(dim_organizador, "dim_organizador.csv")
    write_csv(fact_establecimiento, "fact_establecimiento.csv")
    write_csv(fact_habilitacion, "fact_habilitacion_gastronomica.csv")
    write_csv(fact_evento, "fact_evento_gastronomico.csv")
    write_csv(fact_programa, "fact_programa_politica.csv")
    write_csv(fact_espacio_feria_mercado, "fact_espacio_feria_mercado.csv")
    write_csv(f03_puestos, "fact_puesto_feria.csv")
    write_csv(fact_mercado, "fact_mercado_feria.csv")
    write_csv(puente_evento_programa, "puente_evento_programa.csv")

    for name in ("puente_evento_categoria.csv", "puente_evento_establecimiento.csv", "puente_programa_establecimiento.csv"):
        path = DATA_PROCESSED / name
        if not path.exists():
            pd.DataFrame().to_csv(path, index=False)

    print("OK modelo procesado reconstruido. Revisar contratos_fuentes.csv para confirmar origen real/seed por fuente.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
