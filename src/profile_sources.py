from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

import pandas as pd

try:
    import chardet
except ImportError:  # pragma: no cover - optional dependency
    chardet = None

from clean_text import has_suspect_encoding, is_empty_like, normalize_text
from config import DATA_RAW, DATA_SEEDS, DOCS, PROFILE_OUTPUTS

ENCODINGS_TO_TRY = ("utf-8-sig", "utf-8", "latin-1", "cp1252")
SEPARATORS = (",", ";", "\t", "|")
GEO_HINTS = ("barrio", "comuna", "direccion", "domicilio", "lat", "lon", "calle", "ubicacion")
DATE_HINTS = ("fecha", "anio", "año", "periodo", "desde", "hasta")


def detect_encoding(path: Path, nbytes: int = 200_000) -> str:
    raw = path.read_bytes()[:nbytes]
    if chardet:
        detected = chardet.detect(raw).get("encoding")
        if detected:
            return detected
    for encoding in ENCODINGS_TO_TRY:
        try:
            raw.decode(encoding)
            return encoding
        except UnicodeDecodeError:
            continue
    return "latin-1"


def detect_separator(path: Path, encoding: str) -> str:
    sample = path.read_text(encoding=encoding, errors="replace")[:8000]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters="".join(SEPARATORS))
        return dialect.delimiter
    except csv.Error:
        first_line = sample.splitlines()[0] if sample else ""
        return max(SEPARATORS, key=lambda sep: first_line.count(sep))


def read_csv_profile(path: Path) -> tuple[pd.DataFrame, str, str]:
    encoding = detect_encoding(path)
    separator = detect_separator(path, encoding)
    last_error = None
    for candidate_encoding in (encoding, *ENCODINGS_TO_TRY):
        try:
            df = pd.read_csv(
                path,
                sep=separator,
                encoding=candidate_encoding,
                dtype=str,
                keep_default_na=False,
                on_bad_lines="skip",
            )
            return df, candidate_encoding, separator
        except Exception as exc:
            last_error = exc
    raise RuntimeError(f"No se pudo leer {path}: {last_error}")


def _matching_columns(columns, hints) -> list[str]:
    found = []
    for column in columns:
        key = normalize_text(column, case="lower", remove_accents=True)
        if any(hint in key for hint in hints):
            found.append(column)
    return found


def _frequent_problem_values(df: pd.DataFrame) -> str:
    values = []
    sample = df.head(5000)
    for column in sample.columns:
        series = sample[column].astype(str).map(normalize_text)
        problem = series[series.map(lambda value: is_empty_like(value) or has_suspect_encoding(value))]
        for value, count in problem.value_counts().head(3).items():
            values.append(f"{column}={value or '<vacio>'} ({count})")
    return "; ".join(values[:12])


def profile_file(path: Path, layer: str) -> tuple[dict, pd.DataFrame]:
    df, encoding, separator = read_csv_profile(path)
    size_bytes = path.stat().st_size
    empty_percent = {}
    for column in df.columns:
        if len(df):
            normalized = df[column].astype(str).str.strip().str.lower()
            empty_percent[column] = round(normalized.isin(["", "nan", "none", "null", "s/d", "sd", "sin dato", "no disponible"]).mean() * 100, 2)
        else:
            empty_percent[column] = 0.0
    sample = df.head(5000)
    suspected_mojibake = int(sample.astype(str).map(has_suspect_encoding).sum().sum()) if not df.empty else 0
    geo_columns = _matching_columns(df.columns, GEO_HINTS)
    temporal_columns = _matching_columns(df.columns, DATE_HINTS)
    dataset_kind = "seed/manual" if path.name.startswith("raw_") or len(df) < 1000 else "dataset completo probable"

    recommendation = "usar como seed/fallback"
    if dataset_kind == "dataset completo probable":
        recommendation = "usar como insumo real luego de validar columnas y FKs"
    if suspected_mojibake:
        recommendation += "; corregir mojibake"

    summary = {
        "archivo": path.name,
        "ruta": str(path),
        "capa": layer,
        "tamano_bytes": size_bytes,
        "encoding": encoding,
        "separador": repr(separator),
        "filas": len(df),
        "columnas_cantidad": len(df.columns),
        "columnas": " | ".join(map(str, df.columns)),
        "nulos_por_columna_pct": " | ".join(f"{col}:{pct}" for col, pct in empty_percent.items()),
        "duplicados": int(df.duplicated().sum()) if len(df) <= 250_000 else int(df.head(250_000).duplicated().sum()),
        "campos_geograficos": " | ".join(geo_columns),
        "campos_temporales": " | ".join(temporal_columns),
        "posible_mojibake_celdas_muestra": suspected_mojibake,
        "valores_problematicos_frecuentes": _frequent_problem_values(df),
        "tipo_estimado": dataset_kind,
        "recomendacion_uso": recommendation + ("; duplicados calculados sobre muestra de 250k filas" if len(df) > 250_000 else ""),
    }
    return summary, df


def write_outputs(summaries: list[dict]) -> None:
    PROFILE_OUTPUTS.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)
    summary_df = pd.DataFrame(summaries)
    summary_df.to_csv(PROFILE_OUTPUTS / "perfilado_fuentes_resumen.csv", index=False, encoding="utf-8")
    summary_df.to_csv(PROFILE_OUTPUTS / "perfilado_fuentes.csv", index=False, encoding="utf-8")

    lines = [
        "# Perfilado de fuentes",
        "",
        f"Generado: {datetime.now().date().isoformat()}",
        "",
        "El perfilado corre sobre los CSV disponibles en `data/raw/` y `data/seeds/`. `data/raw/` se reserva para datos reales; `data/seeds/` contiene fallback de desarrollo.",
        "",
    ]
    for item in summaries:
        lines.extend(
            [
                f"## {item['archivo']}",
                "",
                f"- Ruta: `{item['ruta']}`",
                f"- Tamano: {item['tamano_bytes']} bytes",
                f"- Encoding: {item['encoding']}",
                f"- Separador: {item['separador']}",
                f"- Filas x columnas: {item['filas']} x {item['columnas_cantidad']}",
                f"- Columnas: {item['columnas']}",
                f"- Duplicados: {item['duplicados']}",
                f"- Campos geograficos: {item['campos_geograficos'] or 'No detectados'}",
                f"- Campos temporales: {item['campos_temporales'] or 'No detectados'}",
                f"- Posible mojibake en muestra: {item['posible_mojibake_celdas_muestra']}",
                f"- Tipo estimado: {item['tipo_estimado']}",
                f"- Recomendacion: {item['recomendacion_uso']}",
                "",
            ]
        )
    (DOCS / "perfilado_fuentes.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    csvs = [(path, "raw_real") for path in sorted(DATA_RAW.glob("*.csv"))]
    csvs.extend((path, "seed") for path in sorted(DATA_SEEDS.glob("*.csv")))
    if not csvs:
        print(f"WARNING no hay CSV en {DATA_RAW} ni en {DATA_SEEDS}")
        return 0

    summaries = []
    errors = []
    for path, layer in csvs:
        try:
            summary, _df = profile_file(path, layer)
            summaries.append(summary)
            print(f"OK {layer} {path.name}: {summary['filas']} filas, {summary['columnas_cantidad']} columnas")
        except Exception as exc:
            errors.append((path.name, exc))
            print(f"ERROR {path.name}: {exc}")

    if summaries:
        write_outputs(summaries)
        print(f"OK resumen: {PROFILE_OUTPUTS / 'perfilado_fuentes_resumen.csv'}")
        print(f"OK docs: {DOCS / 'perfilado_fuentes.md'}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
