from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd

from clean_text import clean_dataframe_columns, normalize_proper_name, normalize_text
from config import DATA_PROCESSED, DATA_RAW, DOCS, PROFILE_OUTPUTS, SOURCE_CONFIG
from normalize_addresses import UNKNOWN_LOCATION_ID, normalize_address_offline
from normalize_categories import classify_gastronomic_category, taxonomy_dataframe_rows
from source_contracts import SourceLoadResult, map_source_columns

TODAY = date.today().isoformat()


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    for encoding in ("utf-8-sig", "utf-8", "latin-1", "cp1252"):
        try:
            return pd.read_csv(path, dtype=str, keep_default_na=False, encoding=encoding)
        except UnicodeDecodeError:
            continue
    return pd.read_csv(path, dtype=str, keep_default_na=False, encoding="latin-1")


def write_csv(df: pd.DataFrame, filename: str) -> None:
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    df.to_csv(DATA_PROCESSED / filename, index=False, encoding="utf-8")
    print(f"OK {filename}: {len(df)} filas")


def discover_source_paths(source_id: str) -> tuple[list[Path], str]:
    source = SOURCE_CONFIG[source_id]
    real_paths: list[Path] = []
    for pattern in source.get("raw_patterns", []):
        real_paths.extend(DATA_RAW.glob(pattern))
    real_paths = sorted(
        {
            path
            for path in real_paths
            if path.is_file()
            and path.suffix.lower() == ".csv"
            and not path.name.startswith("raw_")
        }
    )
    if real_paths:
        return real_paths, "real"

    seed_paths = sorted(DATA_RAW.glob(source["seed_glob"]))
    return seed_paths, "seed"


def load_source_data(source_id: str) -> tuple[pd.DataFrame, list[SourceLoadResult]]:
    paths, origin = discover_source_paths(source_id)
    frames = []
    reports: list[SourceLoadResult] = []
    for path in paths:
        raw = clean_dataframe_columns(read_csv(path))
        mapped, report = map_source_columns(raw, source_id, origin, path)
        frames.append(mapped)
        reports.append(report)
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


def first_existing(*values, default="No disponible"):
    for value in values:
        cleaned = normalize_text(value)
        if cleaned:
            return cleaned
    return default


def source_urls(dim_fuente: pd.DataFrame) -> dict:
    if dim_fuente.empty or "id_fuente" not in dim_fuente.columns:
        return {}
    url_column = "url_base" if "url_base" in dim_fuente.columns else "url"
    return dict(zip(dim_fuente["id_fuente"], dim_fuente.get(url_column, "")))


def build_dim_fuente() -> pd.DataFrame:
    raw = read_csv(DATA_RAW / "raw_fuentes_relevadas.csv")
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
    defaults = {
        "F01": ("Oferta y Establecimientos Gastronomicos", "https://data.buenosaires.gob.ar/dataset/oferta-establecimientos-gastronomicos"),
        "F02": ("Habilitaciones Aprobadas", "https://data.buenosaires.gob.ar/dataset/habilitaciones-aprobadas"),
        "F03": ("Ferias y Mercados", "https://data.buenosaires.gob.ar/dataset/ferias-mercados"),
    }
    existing = {row["id_fuente"] for row in rows}
    for source_id, (name, url) in defaults.items():
        if source_id not in existing:
            rows.append(
                {
                    "id_fuente": source_id,
                    "nombre_fuente": name,
                    "tipo_fuente": "Oficial / dato abierto",
                    "organismo_entidad": "GCBA / BA Data",
                    "url_base": url,
                    "confiabilidad": "Pendiente",
                    "frecuencia_actualizacion": "No disponible",
                    "fecha_consulta": TODAY,
                    "notas": "Fuente esperada; falta completar URL directa de descarga si no hay CSV real.",
                }
            )
    return pd.DataFrame(rows).drop_duplicates("id_fuente")


def build_dim_categoria() -> pd.DataFrame:
    return pd.DataFrame(taxonomy_dataframe_rows())


def build_locations(est: pd.DataFrame, ferias: pd.DataFrame, eventos: pd.DataFrame) -> pd.DataFrame:
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

    for df, address_col, barrio_col in (
        (est, "direccion_original", "barrio_original"),
        (ferias, "direccion_original", "barrio_original"),
    ):
        for _, row in df.iterrows():
            rows.append(normalize_address_offline(row.get(address_col), row.get(barrio_col)))

    for _, row in eventos.iterrows():
        location = normalize_text(row.get("ubicacion_original"))
        if any(marker in location.lower() for marker in ("adherid", "a relevar", "500+")):
            continue
        barrio = ""
        for candidate in ("Palermo", "San Telmo", "Monserrat", "Balvanera"):
            if candidate.lower() in location.lower():
                barrio = candidate
                break
        rows.append(normalize_address_offline(location, barrio))

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


def build_fact_establecimiento(est: pd.DataFrame, hab: pd.DataFrame, dim_fuente: pd.DataFrame) -> pd.DataFrame:
    urls = source_urls(dim_fuente)
    rows = []
    for idx, row in est.iterrows():
        category = classify_gastronomic_category(row.get("categoria_original"), row.get("nombre_original"))
        location_id = normalize_address_offline(row.get("direccion_original"), row.get("barrio_original"))["id_ubicacion"]
        source_id = first_existing(row.get("id_fuente"), default="F01")
        rows.append(
            {
                "id_establecimiento": f"EST{idx + 1:05d}",
                "nombre": normalize_proper_name(row.get("nombre_original")),
                "id_categoria": category.id_categoria,
                "id_ubicacion": location_id,
                "id_fuente": source_id,
                "url_fuente": urls.get(source_id, "No disponible"),
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
            }
        )

    start = len(rows)
    for idx, row in hab.iterrows():
        if not normalize_text(row.get("rubro_original")):
            continue
        category = classify_gastronomic_category(row.get("rubro_original"), row.get("categoria_gastronomica_inferida"))
        if category.es_gastronomico == "no":
            continue
        source_id = first_existing(row.get("id_fuente"), default="F02")
        location_id = normalize_address_offline(row.get("direccion_original"), "")["id_ubicacion"]
        rows.append(
            {
                "id_establecimiento": f"HAB{start + idx + 1:05d}",
                "nombre": "No disponible",
                "id_categoria": category.id_categoria,
                "id_ubicacion": location_id,
                "id_fuente": source_id,
                "url_fuente": urls.get(source_id, "No disponible"),
                "estado": "habilitacion_detectada",
                "web": "No disponible",
                "redes": "No disponible",
                "telefono": "No disponible",
                "fecha_alta_detectada": first_existing(row.get("fecha_habilitacion"), default="No disponible"),
                "fecha_ultima_actualizacion": first_existing(row.get("fecha_extraccion"), default=TODAY),
                "calidad_dato": first_existing(row.get("calidad_dato"), default="alta"),
                "requiere_validacion": first_existing(row.get("requiere_validacion"), default="si"),
                "motivo_validacion": first_existing(row.get("motivo_validacion"), default="F02 requiere normalizacion de rubro/direccion"),
                "observaciones": first_existing(row.get("observaciones_raw"), default=""),
                "es_gastronomico": category.es_gastronomico,
                "categoria_gastronomica_inferida": category.categoria_gastronomica_inferida,
                "confianza_categoria": category.confianza_categoria,
                "motivo_categoria": category.motivo_categoria,
                "origen_dato": first_existing(row.get("origen_dato"), default="datos reales parciales"),
            }
        )
    return pd.DataFrame(rows)


def build_fact_evento(eventos: pd.DataFrame, dim_fuente: pd.DataFrame) -> pd.DataFrame:
    urls = source_urls(dim_fuente)
    rows = []
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
            }
        )
    return pd.DataFrame(rows)


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
                "url_fuente": urls.get(source_id, "No disponible"),
                "link": "No disponible",
                "calidad_dato": first_existing(row.get("calidad_dato"), default="alta"),
                "requiere_validacion": first_existing(row.get("requiere_validacion"), default="no"),
                "motivo_validacion": first_existing(row.get("motivo_validacion"), default=""),
                "observaciones": first_existing(row.get("observaciones_raw"), default=""),
                "origen_dato": "datos seed",
            }
        )
    return pd.DataFrame(rows)


def build_fact_programa(dim_fuente: pd.DataFrame) -> pd.DataFrame:
    urls = source_urls(dim_fuente)
    raw = clean_dataframe_columns(read_csv(DATA_RAW / "raw_programas_politicas.csv"))
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
                "link",
                "calidad_dato",
                "requiere_validacion",
                "motivo_validacion",
                "observaciones",
                "origen_dato",
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
        "link",
        "calidad_dato",
        "requiere_validacion",
        "motivo_validacion",
        "observaciones",
        "origen_dato",
    ]
    for column in columns:
        if column not in raw.columns:
            raw[column] = ""
    return raw[columns]


def main() -> int:
    est, est_reports = load_source_data("F01")
    hab, hab_reports = load_source_data("F02")
    ferias, ferias_reports = load_source_data("F03")
    eventos = clean_dataframe_columns(read_csv(DATA_RAW / "raw_eventos_gastronomicos.csv"))
    write_contract_reports([*est_reports, *hab_reports, *ferias_reports])

    dim_fuente = build_dim_fuente()
    dim_categoria = build_dim_categoria()
    dim_ubicacion = build_locations(est, ferias, eventos)
    dim_organizador = build_dim_organizador(eventos)
    fact_establecimiento = build_fact_establecimiento(est, hab, dim_fuente)
    fact_evento = build_fact_evento(eventos, dim_fuente)
    fact_mercado = build_fact_mercado_feria(ferias, dim_fuente)
    fact_programa = build_fact_programa(dim_fuente)

    write_csv(dim_fuente, "dim_fuente.csv")
    write_csv(dim_ubicacion, "dim_ubicacion.csv")
    write_csv(dim_categoria, "dim_categoria_gastronomica.csv")
    write_csv(dim_organizador, "dim_organizador.csv")
    write_csv(fact_establecimiento, "fact_establecimiento.csv")
    write_csv(fact_evento, "fact_evento_gastronomico.csv")
    write_csv(fact_programa, "fact_programa_politica.csv")
    write_csv(fact_mercado, "fact_mercado_feria.csv")

    for name in ("puente_evento_categoria.csv", "puente_evento_establecimiento.csv", "puente_programa_establecimiento.csv"):
        path = DATA_PROCESSED / name
        if not path.exists():
            pd.DataFrame().to_csv(path, index=False)

    print("OK modelo procesado reconstruido desde data/raw con seeds como fallback.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
