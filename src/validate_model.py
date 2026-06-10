from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

from config import DATA_ANALYTICS, DATA_PROCESSED


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
    "fact_establecimiento.csv": ["id_fuente", "url_fuente", "calidad_dato", "requiere_validacion", "motivo_validacion"],
    "fact_evento_gastronomico.csv": ["id_fuente", "url_fuente", "calidad_dato", "requiere_validacion", "motivo_validacion"],
    "fact_programa_politica.csv": ["id_fuente", "url_fuente", "calidad_dato", "requiere_validacion", "motivo_validacion"],
    "fact_mercado_feria.csv": ["id_fuente", "url_fuente", "calidad_dato", "requiere_validacion", "motivo_validacion"],
}


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def add(messages: list[tuple[str, str]], level: str, text: str) -> None:
    messages.append((level, text))
    print(f"{level:7s} {text}")


def validate() -> int:
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
        if "estado_datos" not in df.columns:
            add(messages, "WARNING", f"{filename} no tiene estado_datos")

    errors = sum(1 for level, _ in messages if level == "ERROR")
    warnings = sum(1 for level, _ in messages if level == "WARNING")
    print(f"\nResumen validacion: OK={sum(1 for level, _ in messages if level == 'OK')} WARNING={warnings} ERROR={errors}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(validate())
