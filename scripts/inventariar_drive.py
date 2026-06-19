from __future__ import annotations

import argparse
import csv
import os
import re
import sys
import unicodedata
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterable

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "outputs" / "inventario_drive"

ANALYZED_EXTENSIONS = {
    ".csv",
    ".xlsx",
    ".xls",
    ".xlsm",
    ".ods",
    ".pdf",
    ".docx",
    ".txt",
    ".gsheet",
    ".gdoc",
    ".gform",
}
SPREADSHEET_EXTENSIONS = {".csv", ".xlsx", ".xls", ".xlsm", ".ods"}
GOOGLE_DOC_EXTENSIONS = {".gsheet", ".gdoc", ".gform"}
LOW_PRIORITY_EXTENSIONS = {".jpg", ".jpeg", ".png", ".mp4", ".mov", ".zip", ".rar", ".exe"}

KEYWORDS = [
    "gastronomia",
    "gastronomia",
    "gastro",
    "ba capital gastronomica",
    "bacg",
    "evento",
    "eventos",
    "feria",
    "ferias",
    "mercado",
    "mercados",
    "fiab",
    "facturacion",
    "facturacion",
    "ventas",
    "recaudacion",
    "recaudacion",
    "comercios",
    "comerciantes",
    "participantes",
    "proveedores",
    "permisos",
    "mesas",
    "sillas",
    "area gastronomica",
    "area gastronomica",
    "caminos y sabores",
    "cafecito",
    "distrito del vino",
    "bares notables",
]

CATEGORY_TERMS = {
    "facturacion": ["facturacion", "factura", "ventas", "recaudacion", "importe", "monto", "cobro", "pago"],
    "eventos_resultados": ["evento", "eventos", "resultado", "resultados", "reporte", "post evento", "asistencia"],
    "comercios_participantes": ["comercio", "comercios", "comerciante", "participante", "participantes", "proveedor", "proveedores"],
    "permisos_espacio_publico": ["permiso", "permisos", "mesas", "sillas", "area gastronomica", "espacio publico"],
    "ferias_mercados": ["feria", "ferias", "mercado", "mercados", "fiab"],
    "formularios_encuestas": ["formulario", "formularios", "encuesta", "encuestas", "relevamiento", "relevamientos"],
    "programas_gastronomicos": ["bacg", "ba capital gastronomica", "caminos y sabores", "cafecito", "distrito del vino", "bares notables"],
}

DATE_TERMS = ["fecha", "dia", "mes", "anio", "ano", "periodo", "vigencia"]
MONEY_TERMS = ["importe", "monto", "total", "precio", "valor", "venta", "ventas", "recaudacion", "factura", "facturacion", "pago", "cobro"]
EVENT_TERMS = ["evento", "eventos", "actividad", "programa", "edicion", "sede"]
GEO_TERMS = ["barrio", "comuna", "direccion", "domicilio", "lat", "lon", "localidad", "sede", "ubicacion"]
ID_TERMS = ["id", "codigo", "nro", "numero", "expediente", "tramite", "cuit", "cuil", "dni"]
SENSITIVE_HIGH_TERMS = ["dni", "cuit", "cuil", "email", "correo", "telefono", "celular", "cbu", "cuenta"]
SENSITIVE_MEDIUM_TERMS = [
    "nombre",
    "apellido",
    "razon social",
    "razon_social",
    "contacto",
    "direccion",
    "domicilio",
    "factura",
    "importe",
    "monto",
    "venta",
    "ventas",
    "recaudacion",
]


@dataclass
class FolderStats:
    ruta_carpeta: str
    cantidad_archivos: int = 0
    cantidad_spreadsheets: int = 0
    cantidad_pdfs: int = 0
    cantidad_docs: int = 0
    score_relevancia: int = 0
    palabras_clave_detectadas: set[str] = field(default_factory=set)
    observaciones: set[str] = field(default_factory=set)


def normalize_text(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def fmt_set(values: Iterable[str]) -> str:
    return " | ".join(sorted({str(value) for value in values if str(value).strip()}))


def rel_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def path_depth(path: Path, root: Path) -> int:
    relative = rel_path(path, root)
    if relative in {"", "."}:
        return 0
    return len(Path(relative).parts)


def detect_keywords(text: str) -> list[str]:
    normalized = normalize_text(text)
    found = []
    for keyword in sorted(set(KEYWORDS), key=len, reverse=True):
        if normalize_text(keyword) in normalized:
            found.append(keyword)
    return sorted(set(found))


def score_for(path_text: str, extension: str, size_mb: float) -> tuple[int, list[str], str, str]:
    keywords = detect_keywords(path_text)
    score = len(keywords) * 10
    normalized = normalize_text(path_text)
    categories = []
    for category, terms in CATEGORY_TERMS.items():
        if any(term in normalized for term in terms):
            categories.append(category)
            score += 8
    if extension in SPREADSHEET_EXTENSIONS:
        score += 8
    elif extension in {".pdf", ".docx", ".txt"}:
        score += 4
    elif extension in GOOGLE_DOC_EXTENSIONS:
        score += 6
    elif extension in LOW_PRIORITY_EXTENSIONS:
        score -= 8
    if size_mb >= 50:
        score -= 2
    category = " | ".join(categories) if categories else "sin_clasificar"
    return max(score, 0), keywords, category, normalized


def column_matches(columns: list[str], terms: list[str]) -> list[str]:
    result = []
    for column in columns:
        normalized = normalize_text(column)
        if any(term in normalized for term in terms):
            result.append(column)
    return result


def sensitivity_for_columns(columns: list[str]) -> tuple[str, list[str]]:
    high = column_matches(columns, SENSITIVE_HIGH_TERMS)
    medium = column_matches(columns, SENSITIVE_MEDIUM_TERMS)
    if high:
        return "alto", sorted(set(high + medium))
    if medium:
        return "medio", sorted(set(medium))
    return "bajo", []


def boolean_text(value: bool) -> str:
    return "si" if value else "no"


def detect_table_flags(columns: list[str]) -> dict[str, object]:
    date_cols = column_matches(columns, DATE_TERMS)
    money_cols = column_matches(columns, MONEY_TERMS)
    event_cols = column_matches(columns, EVENT_TERMS)
    geo_cols = column_matches(columns, GEO_TERMS)
    id_cols = column_matches(columns, ID_TERMS)
    risk, sensitive_cols = sensitivity_for_columns(columns)
    normalized_join = " ".join(normalize_text(col) for col in columns)
    return {
        "columnas_fecha_detectadas": fmt_set(date_cols),
        "columnas_monetarias_detectadas": fmt_set(money_cols),
        "columnas_evento_detectadas": fmt_set(event_cols),
        "columnas_geograficas_detectadas": fmt_set(geo_cols),
        "columnas_identificadoras_detectadas": fmt_set(id_cols),
        "columnas_sensibles_detectadas": fmt_set(sensitive_cols),
        "riesgo_sensibilidad": risk,
        "posible_base_facturacion": boolean_text(bool(money_cols) or "facturacion" in normalized_join or "factura" in normalized_join),
        "posible_base_eventos": boolean_text(bool(event_cols) or "evento" in normalized_join),
        "posible_base_participantes": boolean_text(any(term in normalized_join for term in ["participante", "comercio", "proveedor", "asistente"])),
        "posible_base_permisos": boolean_text(any(term in normalized_join for term in ["permiso", "mesas", "sillas", "expediente", "tramite"])),
    }


def safe_mtime(path: Path) -> str:
    try:
        return datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds")
    except OSError:
        return ""


def safe_size_mb(path: Path) -> float:
    try:
        return round(path.stat().st_size / (1024 * 1024), 3)
    except OSError:
        return 0.0


def csv_row_count(path: Path, encoding: str, max_mb: float) -> int | str:
    if safe_size_mb(path) > max_mb:
        return "no_calculado_pesado"
    try:
        with path.open("r", encoding=encoding, errors="replace", newline="") as file:
            count = sum(1 for _ in file)
        return max(count - 1, 0)
    except Exception:
        return "no_disponible"


def read_csv_structure(path: Path, relative: str, max_mb: float, sample_rows: int) -> list[dict[str, object]]:
    rows = []
    last_error = ""
    for encoding in ("utf-8-sig", "utf-8", "latin1"):
        try:
            df = pd.read_csv(path, nrows=sample_rows, sep=None, engine="python", dtype=str, encoding=encoding)
            columns = [str(col) for col in df.columns]
            flags = detect_table_flags(columns)
            rows.append(
                {
                    "ruta_relativa": relative,
                    "nombre_archivo": path.name,
                    "hoja": "",
                    "filas": csv_row_count(path, encoding, max_mb),
                    "columnas": len(columns),
                    "nombres_columnas": fmt_set(columns),
                    "porcentaje_nulos_promedio": round(float(df.isna().mean().mean() * 100), 2) if not df.empty else 0.0,
                    "observaciones": f"CSV leido con encoding {encoding}; solo estructura y muestra tecnica de {sample_rows} filas.",
                    **flags,
                }
            )
            return rows
        except Exception as exc:
            last_error = str(exc)
    return [
        {
            "ruta_relativa": relative,
            "nombre_archivo": path.name,
            "hoja": "",
            "filas": "no_disponible",
            "columnas": 0,
            "nombres_columnas": "",
            "columnas_fecha_detectadas": "",
            "columnas_monetarias_detectadas": "",
            "columnas_evento_detectadas": "",
            "columnas_geograficas_detectadas": "",
            "columnas_identificadoras_detectadas": "",
            "columnas_sensibles_detectadas": "",
            "porcentaje_nulos_promedio": "",
            "posible_base_facturacion": "no",
            "posible_base_eventos": "no",
            "posible_base_participantes": "no",
            "posible_base_permisos": "no",
            "riesgo_sensibilidad": "bajo",
            "observaciones": f"No se pudo leer estructura CSV: {last_error[:180]}",
        }
    ]


def read_excel_structure(path: Path, relative: str, sample_rows: int) -> list[dict[str, object]]:
    table_rows = []
    try:
        workbook = pd.ExcelFile(path)
    except Exception as exc:
        return [
            {
                "ruta_relativa": relative,
                "nombre_archivo": path.name,
                "hoja": "",
                "filas": "no_disponible",
                "columnas": 0,
                "nombres_columnas": "",
                "columnas_fecha_detectadas": "",
                "columnas_monetarias_detectadas": "",
                "columnas_evento_detectadas": "",
                "columnas_geograficas_detectadas": "",
                "columnas_identificadoras_detectadas": "",
                "columnas_sensibles_detectadas": "",
                "porcentaje_nulos_promedio": "",
                "posible_base_facturacion": "no",
                "posible_base_eventos": "no",
                "posible_base_participantes": "no",
                "posible_base_permisos": "no",
                "riesgo_sensibilidad": "bajo",
                "observaciones": f"No se pudo abrir planilla: {str(exc)[:180]}",
            }
        ]

    for sheet in workbook.sheet_names:
        try:
            df = pd.read_excel(workbook, sheet_name=sheet, nrows=sample_rows, dtype=str)
            columns = [str(col) for col in df.columns]
            flags = detect_table_flags(columns)
            table_rows.append(
                {
                    "ruta_relativa": relative,
                    "nombre_archivo": path.name,
                    "hoja": sheet,
                    "filas": "no_calculado_solo_muestra",
                    "columnas": len(columns),
                    "nombres_columnas": fmt_set(columns),
                    "porcentaje_nulos_promedio": round(float(df.isna().mean().mean() * 100), 2) if not df.empty else 0.0,
                    "observaciones": f"Hoja leida parcialmente; solo estructura y muestra tecnica de {sample_rows} filas.",
                    **flags,
                }
            )
        except Exception as exc:
            table_rows.append(
                {
                    "ruta_relativa": relative,
                    "nombre_archivo": path.name,
                    "hoja": sheet,
                    "filas": "no_disponible",
                    "columnas": 0,
                    "nombres_columnas": "",
                    "columnas_fecha_detectadas": "",
                    "columnas_monetarias_detectadas": "",
                    "columnas_evento_detectadas": "",
                    "columnas_geograficas_detectadas": "",
                    "columnas_identificadoras_detectadas": "",
                    "columnas_sensibles_detectadas": "",
                    "porcentaje_nulos_promedio": "",
                    "posible_base_facturacion": "no",
                    "posible_base_eventos": "no",
                    "posible_base_participantes": "no",
                    "posible_base_permisos": "no",
                    "riesgo_sensibilidad": "bajo",
                    "observaciones": f"No se pudo leer hoja: {str(exc)[:180]}",
                }
            )
    return table_rows


def table_inventory_for(path: Path, relative: str, max_table_mb: float, sample_rows: int) -> tuple[list[dict[str, object]], str]:
    size_mb = safe_size_mb(path)
    if size_mb > max_table_mb:
        return [], f"pesado: no procesado en profundidad por superar {max_table_mb} MB"
    if path.suffix.lower() == ".csv":
        return read_csv_structure(path, relative, max_table_mb, sample_rows), "estructura_csv_leida"
    if path.suffix.lower() in {".xlsx", ".xls", ".xlsm", ".ods"}:
        return read_excel_structure(path, relative, sample_rows), "estructura_planilla_leida"
    return [], ""


def column_inventory_from_tables(table_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    column_rows = []
    for table in table_rows:
        columns = [col for col in str(table.get("nombres_columnas", "")).split(" | ") if col]
        for column in columns:
            risk, sensitive = sensitivity_for_columns([column])
            normalized = normalize_text(column)
            categories = []
            if any(term in normalized for term in DATE_TERMS):
                categories.append("fecha")
            if any(term in normalized for term in MONEY_TERMS):
                categories.append("monetaria")
            if any(term in normalized for term in EVENT_TERMS):
                categories.append("evento")
            if any(term in normalized for term in GEO_TERMS):
                categories.append("geografica")
            if any(term in normalized for term in ID_TERMS):
                categories.append("identificadora")
            column_rows.append(
                {
                    "ruta_relativa": table.get("ruta_relativa", ""),
                    "nombre_archivo": table.get("nombre_archivo", ""),
                    "hoja": table.get("hoja", ""),
                    "columna": column,
                    "categoria_columna": fmt_set(categories) or "sin_clasificar",
                    "sensible": boolean_text(bool(sensitive)),
                    "riesgo_sensibilidad": risk,
                }
            )
    return column_rows


def iter_tree(root: Path, max_depth: int | None) -> Iterable[Path]:
    stack = [root]
    while stack:
        current = stack.pop()
        yield current
        if max_depth is not None and path_depth(current, root) >= max_depth:
            continue
        try:
            entries = list(os.scandir(current))
        except OSError:
            continue
        dirs = []
        for entry in entries:
            try:
                entry_path = Path(entry.path)
                if entry.is_dir(follow_symlinks=False):
                    dirs.append(entry_path)
                else:
                    yield entry_path
            except OSError:
                continue
        stack.extend(sorted(dirs, reverse=True, key=lambda p: str(p).lower()))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def top_rows(rows: list[dict[str, object]], limit: int, score_key: str = "score_relevancia") -> list[dict[str, object]]:
    return sorted(rows, key=lambda row: (int(row.get(score_key, 0) or 0), str(row.get("ruta_relativa") or row.get("ruta_carpeta") or "")), reverse=True)[:limit]


def redact_path(value: object) -> str:
    text = str(value or "")
    text = re.sub(r"(?i)(cuit|cuil|dni)[ _-]*\d+", r"\1 [redactado]", text)
    text = re.sub(r"\b\d{8,11}\b", "[numero_redactado]", text)
    return text


def md_list(rows: list[dict[str, object]], path_key: str, extra_key: str = "categoria_probable", limit: int = 10) -> str:
    if not rows:
        return "- No se detectaron candidatos.\n"
    lines = []
    for row in rows[:limit]:
        score = row.get("score_relevancia", "")
        extra = row.get(extra_key, "")
        lines.append(f"- `{redact_path(row.get(path_key, ''))}` - score {score} - {extra}")
    return "\n".join(lines) + "\n"


def matching_files(file_rows: list[dict[str, object]], category: str) -> list[dict[str, object]]:
    rows = [row for row in file_rows if category in str(row.get("categoria_probable", ""))]
    return top_rows(rows, 50)


def build_summary(
    file_rows: list[dict[str, object]],
    folder_rows: list[dict[str, object]],
    table_rows: list[dict[str, object]],
    google_rows: list[dict[str, object]],
) -> str:
    spreadsheets = [row for row in file_rows if row.get("extension") in SPREADSHEET_EXTENSIONS]
    pdf_docs = [row for row in file_rows if row.get("extension") in {".pdf", ".docx", ".txt", ".gdoc"}]
    high_risk_paths = sorted(
        {
            str(row.get("ruta_relativa", ""))
            for row in table_rows
            if row.get("riesgo_sensibilidad") == "alto"
        }
    )
    facturacion = matching_files(file_rows, "facturacion")
    eventos = matching_files(file_rows, "eventos_resultados")
    participantes = matching_files(file_rows, "comercios_participantes")
    permisos = matching_files(file_rows, "permisos_espacio_publico")
    top_files = top_rows(file_rows, 30)
    folder_candidates = [row for row in folder_rows if row.get("ruta_carpeta") not in {"", "."}]
    top_folders = top_rows(folder_candidates, 20)
    recommended = top_files[0].get("ruta_relativa", "No disponible") if top_files else "No disponible"

    return "\n".join(
        [
            "# Inventario local de Google Drive para DataGastro",
            "",
            "Exploracion local en modo lectura. No integra fuentes internas al pipeline F01-F05.",
            "",
            "## Totales",
            f"- Total de archivos inventariados: {len(file_rows)}",
            f"- Total de carpetas inventariadas: {len(folder_rows)}",
            f"- Cantidad de planillas: {len(spreadsheets)}",
            f"- Cantidad de PDFs/docs/txt/gdoc: {len(pdf_docs)}",
            "",
            "## Top 20 carpetas mas relevantes",
            md_list(top_folders, "ruta_carpeta", "palabras_clave_detectadas", 20),
            "## Top 30 archivos mas relevantes",
            md_list(top_files, "ruta_relativa", "categoria_probable", 30),
            "## Archivos que parecen contener facturacion",
            md_list(facturacion, "ruta_relativa", "hoja", 30),
            "## Archivos que parecen contener resultados de eventos",
            md_list(eventos, "ruta_relativa", "hoja", 30),
            "## Archivos que parecen contener comercios o participantes",
            md_list(participantes, "ruta_relativa", "hoja", 30),
            "## Archivos que parecen contener permisos o espacio publico",
            md_list(permisos, "ruta_relativa", "hoja", 30),
            "## Archivos con riesgo alto de sensibilidad",
            "\n".join(f"- `{redact_path(path)}`" for path in high_risk_paths[:50]) + ("\n" if high_risk_paths else "- No se detectaron candidatos de riesgo alto en columnas.\n"),
            "## Google Sheets/Docs/Forms que convendria exportar",
            md_list(google_rows, "ruta_relativa", "observaciones", 50),
            "## Recomendacion de analisis inicial",
            f"- Analizar primero: `{recommended}`.",
            "- Priorizar planillas con score alto y riesgo bajo/medio para evaluar estructura antes de cualquier integracion.",
            "- Si el candidato es `.gsheet`, `.gdoc` o `.gform`, exportarlo manualmente o por API en una carpeta controlada antes de analizar contenido.",
            "- Mantener fuentes internas separadas de F01-F05 hasta definir contrato, sensibilidad y permisos de uso.",
            "",
            "## Propuesta de fuentes internas candidatas",
            "- I01 facturacion de eventos.",
            "- I02 participantes/comercios de eventos.",
            "- I03 permisos internos y espacio publico.",
            "- I04 encuestas/formularios.",
            "- I05 resultados o reportes post-evento.",
            "",
        ]
    )


def inventory(args: argparse.Namespace) -> dict[str, object]:
    root = Path(args.root).expanduser()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"ERROR: no existe la carpeta raiz o no es directorio: {root}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    file_rows: list[dict[str, object]] = []
    table_rows: list[dict[str, object]] = []
    google_rows: list[dict[str, object]] = []
    folder_stats: dict[str, FolderStats] = {}

    for path in iter_tree(root, args.max_depth):
        relative = rel_path(path, root)
        if path.is_dir():
            score, keywords, _, _ = score_for(relative, "", 0)
            folder_stats[relative] = FolderStats(
                ruta_carpeta=relative,
                score_relevancia=score,
                palabras_clave_detectadas=set(keywords),
            )
            continue

        extension = path.suffix.lower()
        size_mb = safe_size_mb(path)
        score, keywords, category, _ = score_for(f"{relative} {path.parent}", extension, size_mb)
        supported = extension in ANALYZED_EXTENSIONS
        low_priority = extension in LOW_PRIORITY_EXTENSIONS
        if args.solo_relevantes and score <= 0 and not supported:
            continue

        observations = []
        processed = "no"
        if not supported:
            observations.append("extension_no_analizada")
        if low_priority:
            observations.append("baja_prioridad_por_extension")
        if size_mb > args.max_table_mb and extension in SPREADSHEET_EXTENSIONS:
            observations.append("pesado")
        if extension in GOOGLE_DOC_EXTENSIONS:
            observations.append("requiere_export_manual_o_API")

        row = {
            "ruta_relativa": relative,
            "ruta_absoluta": str(path),
            "carpeta": rel_path(path.parent, root),
            "nombre_archivo": path.name,
            "extension": extension,
            "tamaño_mb": size_mb,
            "fecha_modificacion": safe_mtime(path),
            "profundidad_carpeta": path_depth(path.parent, root),
            "score_relevancia": score,
            "palabras_clave_detectadas": fmt_set(keywords),
            "categoria_probable": category,
            "procesado_en_profundidad": processed,
            "riesgo_sensibilidad": "no_evaluado",
            "observaciones": fmt_set(observations),
        }

        new_table_rows: list[dict[str, object]] = []
        if extension in SPREADSHEET_EXTENSIONS and supported:
            new_table_rows, table_observation = table_inventory_for(path, relative, args.max_table_mb, args.sample_rows)
            if table_observation:
                observations.append(table_observation)
            if new_table_rows:
                processed = "si" if "pesado" not in observations else "no"
                risks = {str(item.get("riesgo_sensibilidad", "bajo")) for item in new_table_rows}
                if "alto" in risks:
                    row["riesgo_sensibilidad"] = "alto"
                elif "medio" in risks:
                    row["riesgo_sensibilidad"] = "medio"
                else:
                    row["riesgo_sensibilidad"] = "bajo"
                table_rows.extend(new_table_rows)

        row["procesado_en_profundidad"] = processed
        row["observaciones"] = fmt_set(observations)
        file_rows.append(row)

        if extension in GOOGLE_DOC_EXTENSIONS:
            google_rows.append(
                {
                    "ruta_relativa": relative,
                    "ruta_absoluta": str(path),
        "tipo": extension.replace(".", ""),
                    "score_relevancia": score,
                    "palabras_clave_detectadas": fmt_set(keywords),
                    "observaciones": "requiere_export_manual_o_API",
                }
            )

        folder_key = rel_path(path.parent, root)
        stats = folder_stats.setdefault(folder_key, FolderStats(ruta_carpeta=folder_key))
        stats.cantidad_archivos += 1
        if extension in SPREADSHEET_EXTENSIONS:
            stats.cantidad_spreadsheets += 1
        if extension == ".pdf":
            stats.cantidad_pdfs += 1
        if extension in {".docx", ".txt", ".gdoc"}:
            stats.cantidad_docs += 1
        stats.score_relevancia += score
        stats.palabras_clave_detectadas.update(keywords)
        if low_priority:
            stats.observaciones.add("contiene_archivos_baja_prioridad")

    if args.solo_relevantes:
        file_rows = [row for row in file_rows if int(row.get("score_relevancia", 0) or 0) > 0 or row.get("extension") in GOOGLE_DOC_EXTENSIONS]
        table_paths = {row["ruta_relativa"] for row in file_rows}
        table_rows = [row for row in table_rows if row.get("ruta_relativa") in table_paths]

    folder_rows = [
        {
            "ruta_carpeta": stats.ruta_carpeta,
            "cantidad_archivos": stats.cantidad_archivos,
            "cantidad_spreadsheets": stats.cantidad_spreadsheets,
            "cantidad_pdfs": stats.cantidad_pdfs,
            "cantidad_docs": stats.cantidad_docs,
            "score_relevancia": stats.score_relevancia,
            "palabras_clave_detectadas": fmt_set(stats.palabras_clave_detectadas),
            "observaciones": fmt_set(stats.observaciones),
        }
        for stats in folder_stats.values()
        if not args.solo_relevantes or stats.score_relevancia > 0
    ]
    column_rows = column_inventory_from_tables(table_rows)

    write_csv(
        OUTPUT_DIR / "inventario_archivos.csv",
        file_rows,
        [
            "ruta_relativa",
            "ruta_absoluta",
            "carpeta",
            "nombre_archivo",
            "extension",
            "tamaño_mb",
            "fecha_modificacion",
            "profundidad_carpeta",
            "score_relevancia",
            "palabras_clave_detectadas",
            "categoria_probable",
            "procesado_en_profundidad",
            "riesgo_sensibilidad",
            "observaciones",
        ],
    )
    write_csv(
        OUTPUT_DIR / "inventario_carpetas.csv",
        folder_rows,
        [
            "ruta_carpeta",
            "cantidad_archivos",
            "cantidad_spreadsheets",
            "cantidad_pdfs",
            "cantidad_docs",
            "score_relevancia",
            "palabras_clave_detectadas",
            "observaciones",
        ],
    )
    table_fields = [
        "ruta_relativa",
        "nombre_archivo",
        "hoja",
        "filas",
        "columnas",
        "nombres_columnas",
        "columnas_fecha_detectadas",
        "columnas_monetarias_detectadas",
        "columnas_evento_detectadas",
        "columnas_geograficas_detectadas",
        "columnas_identificadoras_detectadas",
        "columnas_sensibles_detectadas",
        "porcentaje_nulos_promedio",
        "posible_base_facturacion",
        "posible_base_eventos",
        "posible_base_participantes",
        "posible_base_permisos",
        "riesgo_sensibilidad",
        "observaciones",
    ]
    write_csv(OUTPUT_DIR / "inventario_tablas.csv", table_rows, table_fields)
    write_csv(
        OUTPUT_DIR / "inventario_columnas.csv",
        column_rows,
        ["ruta_relativa", "nombre_archivo", "hoja", "columna", "categoria_columna", "sensible", "riesgo_sensibilidad"],
    )
    write_csv(
        OUTPUT_DIR / "google_docs_a_exportar.csv",
        google_rows,
        ["ruta_relativa", "ruta_absoluta", "tipo", "score_relevancia", "palabras_clave_detectadas", "observaciones"],
    )
    summary = build_summary(file_rows, folder_rows, table_rows, google_rows)
    (OUTPUT_DIR / "resumen_inventario_drive.md").write_text(summary, encoding="utf-8")

    return {
        "file_rows": file_rows,
        "folder_rows": folder_rows,
        "table_rows": table_rows,
        "google_rows": google_rows,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inventaria archivos locales de Google Drive para evaluar nuevas fuentes internas de DataGastro.")
    parser.add_argument("--root", required=True, help="Carpeta raiz del Drive sincronizado, por ejemplo G:\\My Drive")
    parser.add_argument("--max-depth", type=int, default=None, help="Profundidad maxima relativa a la raiz.")
    parser.add_argument("--solo-relevantes", action="store_true", help="Guarda solo archivos/carpetas con score de relevancia mayor a cero.")
    parser.add_argument("--max-table-mb", type=float, default=25.0, help="Tamaño maximo para analizar estructura de planillas.")
    parser.add_argument("--sample-rows", type=int, default=200, help="Cantidad maxima de filas tecnicas para inferir columnas/nulos.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = inventory(args)
    file_rows = result["file_rows"]
    folder_rows = result["folder_rows"]
    table_rows = result["table_rows"]
    google_rows = result["google_rows"]
    top_files = top_rows(file_rows, 5)
    folder_candidates = [row for row in folder_rows if row.get("ruta_carpeta") not in {"", "."}]
    top_folders = top_rows(folder_candidates, 5)
    facturacion = [row for row in table_rows if row.get("posible_base_facturacion") == "si"]
    eventos = [row for row in table_rows if row.get("posible_base_eventos") == "si"]
    high_risk = sorted({str(row.get("ruta_relativa", "")) for row in table_rows if row.get("riesgo_sensibilidad") == "alto"})

    print(f"OK: inventario generado en {OUTPUT_DIR}")
    print(f"Archivos escaneados: {len(file_rows)}")
    print(f"Carpetas escaneadas: {len(folder_rows)}")
    print(f"Planillas detectadas: {sum(1 for row in file_rows if row.get('extension') in SPREADSHEET_EXTENSIONS)}")
    print("Top carpetas relevantes:")
    for row in top_folders:
        print(f"- {row.get('ruta_carpeta')} (score {row.get('score_relevancia')})")
    print("Top archivos relevantes:")
    for row in top_files:
        print(f"- {row.get('ruta_relativa')} (score {row.get('score_relevancia')})")
    print(f"Posibles bases de facturacion: {len(facturacion)}")
    print(f"Posibles bases de eventos: {len(eventos)}")
    print(f"Archivos con riesgo alto detectado por columnas: {len(high_risk)}")
    print(f"Google Sheets/Docs a exportar: {len(google_rows)}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrumpido por el usuario.", file=sys.stderr)
        raise SystemExit(130)
