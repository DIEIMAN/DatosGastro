from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

from config import DATA_ANALYTICS, DATA_PROCESSED, DATA_RAW, SOURCE_CONFIG


EXPECTED_TABLES = {
    "dim_fuente.csv": "id_fuente",
    "dim_ubicacion.csv": "id_ubicacion",
    "dim_categoria_gastronomica.csv": "id_categoria",
    "dim_organizador.csv": "id_organizador",
    "fact_establecimiento.csv": "id_establecimiento",
    "fact_evento_gastronomico.csv": "id_evento",
    "fact_programa_politica.csv": "id_programa",
    "fact_mercado_feria.csv": "id_mercado_feria",
}

EXPECTED_ANALYTICS = [
    "analytics_eventos_por_barrio.csv",
    "analytics_establecimientos_por_categoria_barrio.csv",
    "analytics_programas_por_anio.csv",
    "analytics_mapa_oportunidades.csv",
    "analytics_resumen_ejecutivo.csv",
]

FK_CHECKS = [
    ("fact_evento_gastronomico.csv", "id_ubicacion", "dim_ubicacion.csv", "id_ubicacion"),
    ("fact_evento_gastronomico.csv", "id_organizador", "dim_organizador.csv", "id_organizador"),
    ("fact_establecimiento.csv", "id_categoria", "dim_categoria_gastronomica.csv", "id_categoria"),
    ("fact_establecimiento.csv", "id_ubicacion", "dim_ubicacion.csv", "id_ubicacion"),
    ("fact_mercado_feria.csv", "id_ubicacion", "dim_ubicacion.csv", "id_ubicacion"),
]

TRACEABILITY_COLUMNS = {
    "fact_establecimiento.csv": ["id_fuente", "url_fuente", "fecha_consulta", "calidad_dato", "requiere_validacion", "motivo_validacion", "origen_dato", "estado_datos"],
    "fact_evento_gastronomico.csv": ["id_fuente", "url_fuente", "fecha_consulta", "calidad_dato", "requiere_validacion", "motivo_validacion", "origen_dato", "estado_datos"],
    "fact_programa_politica.csv": ["id_fuente", "url_fuente", "fecha_consulta", "calidad_dato", "requiere_validacion", "motivo_validacion", "origen_dato", "estado_datos"],
    "fact_mercado_feria.csv": ["id_fuente", "url_fuente", "fecha_consulta", "calidad_dato", "requiere_validacion", "motivo_validacion", "origen_dato", "estado_datos"],
}

IMPORTANT_FACTS = [
    "fact_establecimiento.csv",
    "fact_mercado_feria.csv",
]

IMPORTANT_ANALYTICS = [
    "analytics_establecimientos_por_categoria_barrio.csv",
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

    hab = tables.get("fact_establecimiento.csv")
    if strict_real and hab is not None and not (hab.get("id_fuente", pd.Series(dtype=str)).astype(str) == "F02").any():
        add(messages, "ERROR", "F02 no aporta registros a fact_establecimiento; no hay monitor de habilitaciones recientes")

    errors = sum(1 for level, _ in messages if level == "ERROR")
    warnings = sum(1 for level, _ in messages if level == "WARNING")
    print(f"\nResumen validacion: OK={sum(1 for level, _ in messages if level == 'OK')} WARNING={warnings} ERROR={errors}")
    return 1 if errors else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Valida modelo, analytics y trazabilidad.")
    parser.add_argument("--strict-real", action="store_true", help="Falla si hay seeds o analytics no aptas para dashboard.")
    args = parser.parse_args()
    sys.exit(validate(strict_real=args.strict_real))
