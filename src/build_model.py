from __future__ import annotations

import argparse
import csv
from datetime import date
from pathlib import Path

import pandas as pd

from clean_text import clean_dataframe_columns, normalize_proper_name, normalize_text
from config import DATA_PROCESSED, DATA_RAW, DATA_SEEDS, DOCS, PROFILE_OUTPUTS, SOURCE_CONFIG
from normalize_addresses import UNKNOWN_LOCATION_ID, normalize_address_offline
from normalize_categories import classify_gastronomic_category, taxonomy_dataframe_rows
from source_contracts import SourceLoadResult, map_source_columns

TODAY = date.today().isoformat()


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
        mapped["url_fuente"] = source.get("dataset_url", source.get("download_url", "No disponible"))
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


def cached_location(cache: dict[tuple[str, str], dict], address: str, barrio: str) -> dict:
    key = (normalize_text(address), normalize_text(barrio))
    if key not in cache:
        cache[key] = normalize_address_offline(address, barrio)
    return cache[key].copy()


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
    for source_id in ("F01", "F02", "F03"):
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


def build_locations(est: pd.DataFrame, hab: pd.DataFrame, ferias: pd.DataFrame, eventos: pd.DataFrame) -> pd.DataFrame:
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

    for df, address_col, barrio_col in (
        (est, "direccion_original", "barrio_original"),
        (hab, "direccion_original", "barrio_original"),
        (ferias, "direccion_original", "barrio_original"),
    ):
        for _, row in df.iterrows():
            rows.append(cached_location(location_cache, row.get(address_col), row.get(barrio_col)))

    for _, row in eventos.iterrows():
        location = normalize_text(row.get("ubicacion_original"))
        if any(marker in location.lower() for marker in ("adherid", "a relevar", "500+")):
            continue
        barrio = ""
        for candidate in ("Palermo", "San Telmo", "Monserrat", "Balvanera"):
            if candidate.lower() in location.lower():
                barrio = candidate
                break
        rows.append(cached_location(location_cache, location, barrio))

    df = pd.DataFrame(rows).drop_duplicates("id_ubicacion")
    return df


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
    known = {
        "afadhya": ("O001", "AFADHYA", "privado/mixto"),
        "appyce": ("O002", "APPYCE", "privado/mixto"),
        "dg desarrollo gastronomico": ("O003", "DG Desarrollo Gastronomico", "publico"),
        "ba capital gastronomica": ("O004", "BA Capital Gastronomica", "publico/mixto"),
    }
    seen = {row["id_organizador"] for row in rows}
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
    return pd.DataFrame(rows).sort_values("id_organizador")


def infer_organizer_id(value: str) -> str:
    text = normalize_text(value, case="lower", remove_accents=True)
    if "afadhya" in text:
        return "O001"
    if "appyce" in text:
        return "O002"
    if "ba capital gastronomica" in text or "dg desarrollo gastronomico" in text:
        return "O004"
    if "privado" in text:
        return "O999"
    return "O000"


def build_fact_establecimiento(est: pd.DataFrame, dim_fuente: pd.DataFrame) -> pd.DataFrame:
    urls = source_urls(dim_fuente)
    rows = []
    category_cache = {}
    location_cache: dict[tuple[str, str], dict] = {}
    for idx, row in est.iterrows():
        category_key = (row.get("categoria_original"), row.get("nombre_original"))
        category = category_cache.get(category_key)
        if category is None:
            category = classify_gastronomic_category(*category_key)
            category_cache[category_key] = category
        location_id = cached_location(location_cache, row.get("direccion_original"), row.get("barrio_original"))["id_ubicacion"]
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
        location = cached_location(location_cache, row.get("direccion_original"), row.get("barrio_original"))
        if location["comuna"] == "No determinada" and normalize_text(row.get("comuna_original")):
            location["comuna"] = normalize_text(row.get("comuna_original"))
        source_url = first_existing(row.get("url_fuente"), default=urls.get(source_id, "No disponible"))
        rows.append(
            {
                "id_habilitacion": f"HAB{idx + 1:07d}",
                "id_fuente": source_id,
                "url_fuente": source_url,
                "fecha_consulta": first_existing(row.get("fecha_consulta"), default=TODAY),
                "periodo_fuente": first_existing(row.get("periodo_fuente"), default=""),
                "anio_fuente": first_existing(row.get("anio_fuente"), default=""),
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
                "requiere_validacion": first_existing(row.get("requiere_validacion"), default="si"),
                "motivo_validacion": first_existing(row.get("motivo_validacion"), default="Clasificacion gastronomica inferida desde rubro F02; validar casos ambiguos"),
                "observaciones": first_existing(row.get("observaciones_raw"), default=""),
            }
        )
    return pd.DataFrame(rows)


def build_fact_evento(eventos: pd.DataFrame, dim_fuente: pd.DataFrame) -> pd.DataFrame:
    urls = source_urls(dim_fuente)
    rows = []
    columns = [
        "id_evento",
        "nombre_evento",
        "descripcion",
        "fecha_inicio",
        "fecha_fin",
        "periodicidad",
        "id_ubicacion",
        "id_organizador",
        "id_fuente",
        "url_fuente",
        "fecha_consulta",
        "tipo_evento",
        "gratuito",
        "requiere_inscripcion",
        "cantidad_asistentes_estimada",
        "cantidad_puestos_estimada",
        "estado",
        "link_evento",
        "calidad_dato",
        "requiere_validacion",
        "motivo_validacion",
        "observaciones",
        "origen_dato",
        "estado_datos",
    ]
    for idx, row in eventos.iterrows():
        location = normalize_text(row.get("ubicacion_original"))
        if any(marker in location.lower() for marker in ("adherid", "a relevar", "500+")):
            location_id = UNKNOWN_LOCATION_ID
        else:
            barrio = "Palermo" if "palermo" in location.lower() else ""
            location_id = normalize_address_offline(location, barrio)["id_ubicacion"]
        source_id = first_existing(row.get("id_fuente"), default="F08")
        rows.append(
            {
                "id_evento": f"EVT{idx + 1:05d}",
                "nombre_evento": normalize_proper_name(row.get("nombre_evento_original")),
                "descripcion": first_existing(row.get("observaciones_raw"), default=""),
                "fecha_inicio": first_existing(row.get("fecha_original"), default="No disponible"),
                "fecha_fin": "No disponible",
                "periodicidad": "anual/ciclo" if "anual" in normalize_text(row.get("fecha_original"), case="lower") else "evento puntual",
                "id_ubicacion": location_id,
                "id_organizador": infer_organizer_id(row.get("organizador_original")),
                "id_fuente": source_id,
                "url_fuente": urls.get(source_id, "No disponible"),
                "fecha_consulta": first_existing(row.get("fecha_consulta"), default=TODAY),
                "tipo_evento": "evento gastronomico",
                "gratuito": "Requiere validacion",
                "requiere_inscripcion": "No disponible",
                "cantidad_asistentes_estimada": "No disponible",
                "cantidad_puestos_estimada": "No disponible",
                "estado": "sin_verificar",
                "link_evento": "No disponible",
                "calidad_dato": first_existing(row.get("calidad_dato"), default="media"),
                "requiere_validacion": first_existing(row.get("requiere_validacion"), default="si"),
                "motivo_validacion": first_existing(row.get("motivo_validacion"), default="Evento seed pendiente de estructuracion"),
                "observaciones": first_existing(row.get("observaciones_raw"), default=""),
                "origen_dato": first_existing(row.get("origen_dato"), default="datos seed"),
                "estado_datos": first_existing(row.get("estado_datos"), default="datos seed"),
            }
        )
    return pd.DataFrame(rows, columns=columns)


def build_fact_mercado_feria(ferias: pd.DataFrame, dim_fuente: pd.DataFrame) -> pd.DataFrame:
    urls = source_urls(dim_fuente)
    rows = []
    for idx, row in ferias.iterrows():
        source_id = first_existing(row.get("id_fuente"), default="F03")
        rows.append(
            {
                "id_mercado_feria": f"MF{idx + 1:05d}",
                "nombre": normalize_proper_name(row.get("nombre_original")),
                "tipo_espacio": first_existing(row.get("tipo_original"), default="Feria"),
                "id_ubicacion": normalize_address_offline(row.get("direccion_original"), row.get("barrio_original"))["id_ubicacion"],
                "gestion": first_existing(row.get("gestion_original"), default="No disponible"),
                "dias_funcionamiento": first_existing(row.get("dias_horarios_original"), default="No disponible"),
                "horarios": first_existing(row.get("dias_horarios_original"), default="No disponible"),
                "cantidad_puestos": "No disponible",
                "rubros": "No disponible",
                "estado": "activo" if first_existing(row.get("requiere_validacion"), default="no") == "no" else "sin_verificar",
                "id_fuente": source_id,
                "url_fuente": first_existing(row.get("url_fuente"), default=urls.get(source_id, "No disponible")),
                "fecha_consulta": first_existing(row.get("fecha_consulta"), default=TODAY),
                "link": "No disponible",
                "calidad_dato": first_existing(row.get("calidad_dato"), default="alta"),
                "requiere_validacion": first_existing(row.get("requiere_validacion"), default="no"),
                "motivo_validacion": first_existing(row.get("motivo_validacion"), default=""),
                "observaciones": first_existing(row.get("observaciones_raw"), default=""),
                "origen_dato": first_existing(row.get("origen_dato"), default="datos seed"),
                "estado_datos": first_existing(row.get("estado_datos"), default="datos seed"),
            }
        )
    return pd.DataFrame(rows)


def build_fact_programa(dim_fuente: pd.DataFrame, use_seed: bool = True) -> pd.DataFrame:
    urls = source_urls(dim_fuente)
    raw = clean_dataframe_columns(read_seed_csv("raw_programas_politicas.csv")) if use_seed else pd.DataFrame()
    if raw.empty:
        return pd.DataFrame(
            columns=[
                "id_programa",
                "nombre_programa",
                "organismo_responsable",
                "fecha_inicio",
                "fecha_fin",
                "estado",
                "tipo_programa",
                "objetivo",
                "beneficiarios",
                "alcance_geografico",
                "resultados",
                "metricas_publicadas",
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
        )
    raw = raw.rename(
        columns={
            "id_raw": "id_programa",
            "nombre_original": "nombre_programa",
            "organismo_original": "organismo_responsable",
            "estado_original": "estado",
            "descripcion_original": "objetivo",
            "observaciones_raw": "observaciones",
        }
    )
    if "url_fuente" not in raw.columns:
        raw["url_fuente"] = raw.get("id_fuente", "").map(urls).fillna("No disponible")
    raw["origen_dato"] = "datos seed"
    raw["estado_datos"] = "datos seed"
    raw["fecha_consulta"] = TODAY
    raw["fecha_inicio"] = raw.get("fecha_inicio", "No disponible")
    raw["fecha_fin"] = raw.get("fecha_fin", "No disponible")
    raw["tipo_programa"] = raw.get("tipo_programa", "promocion/financiamiento/normativa")
    raw["beneficiarios"] = raw.get("beneficiarios", "Comercios gastronomicos / vecinos / turistas")
    raw["alcance_geografico"] = raw.get("alcance_geografico", "CABA")
    raw["resultados"] = raw.get("resultados", "No encontrado en fuente publica")
    raw["metricas_publicadas"] = raw.get("metricas_publicadas", "No encontrado en fuente publica")
    raw["link"] = raw.get("link", "No disponible")
    columns = [
        "id_programa",
        "nombre_programa",
        "organismo_responsable",
        "fecha_inicio",
        "fecha_fin",
        "estado",
        "tipo_programa",
        "objetivo",
        "beneficiarios",
        "alcance_geografico",
        "resultados",
        "metricas_publicadas",
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
    for column in columns:
        if column not in raw.columns:
            raw[column] = ""
    return raw[columns]


def main() -> int:
    parser = argparse.ArgumentParser(description="Construye data/processed desde datos reales o seeds de desarrollo.")
    parser.add_argument("--strict-real", action="store_true", help="Falla si se usan seeds o faltan F01/F02/F03 reales.")
    args = parser.parse_args()

    est, est_reports = load_source_data("F01")
    hab, hab_reports = load_source_data("F02")
    ferias, ferias_reports = load_source_data("F03")
    eventos = pd.DataFrame() if args.strict_real else clean_dataframe_columns(read_seed_csv("raw_eventos_gastronomicos.csv"))
    hab_gastronomica = filter_gastronomic_habilitations(hab)
    reports = [*est_reports, *hab_reports, *ferias_reports]
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
            print("Accion: cargar CSV reales F01/F02/F03 en data/raw/ y volver a correr.")
            return 1

    dim_fuente = build_dim_fuente()
    dim_categoria = build_dim_categoria()
    dim_ubicacion = build_locations(est, hab_gastronomica, ferias, eventos)
    dim_organizador = build_dim_organizador(eventos)
    fact_establecimiento = build_fact_establecimiento(est, dim_fuente)
    fact_habilitacion = build_fact_habilitacion_gastronomica(hab_gastronomica, dim_fuente)
    fact_evento = build_fact_evento(eventos, dim_fuente)
    fact_mercado = build_fact_mercado_feria(ferias, dim_fuente)
    fact_programa = build_fact_programa(dim_fuente, use_seed=not args.strict_real)

    write_csv(dim_fuente, "dim_fuente.csv")
    write_csv(dim_ubicacion, "dim_ubicacion.csv")
    write_csv(dim_categoria, "dim_categoria_gastronomica.csv")
    write_csv(dim_organizador, "dim_organizador.csv")
    write_csv(fact_establecimiento, "fact_establecimiento.csv")
    write_csv(fact_habilitacion, "fact_habilitacion_gastronomica.csv")
    write_csv(fact_evento, "fact_evento_gastronomico.csv")
    write_csv(fact_programa, "fact_programa_politica.csv")
    write_csv(fact_mercado, "fact_mercado_feria.csv")

    for name in ("puente_evento_categoria.csv", "puente_evento_establecimiento.csv", "puente_programa_establecimiento.csv"):
        path = DATA_PROCESSED / name
        if not path.exists():
            pd.DataFrame().to_csv(path, index=False)

    print("OK modelo procesado reconstruido. Revisar contratos_fuentes.csv para confirmar origen real/seed por fuente.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
