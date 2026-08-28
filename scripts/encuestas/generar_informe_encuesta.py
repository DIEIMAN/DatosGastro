"""Motor reusable para informes de encuestas DataGastro.

Este script genera salidas publicables y agregadas desde una planilla de
respuestas, sin modificar la fuente. Esta pensado como herramienta paralela:
no reemplaza informes existentes de Cafecito ni otros proyectos.

Uso:
    python scripts/encuestas/generar_informe_encuesta.py \
        --config config/encuestas/cafecito_belgrano_template_test.json
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
import textwrap
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = REPO_ROOT / "config" / "encuestas" / "cafecito_belgrano_template_test.json"
SAFE_OUTPUT_ROOT = REPO_ROOT / "outputs" / "encuestas"
FORBIDDEN_WRITE_ROOTS = [
    REPO_ROOT / "outputs" / "cafecito",
    REPO_ROOT / "docs" / "cafecito",
    REPO_ROOT / "scripts" / "cafecito",
    REPO_ROOT / "Cafesito",
]
SENSITIVE_PATTERNS = {
    "arroba": re.compile(r"@"),
    "email": re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}"),
    "telefono": re.compile(r"\b(?:\+?54\s*)?(?:11\s*)?\d{4}[-\s]?\d{4}\b"),
    "cuit": re.compile(r"CUIT|C\.U\.I\.T\.|\b\d{2}-\d{8}-\d\b", re.I),
    "dni": re.compile(r"DNI|D\.N\.I\.|\b\d{7,8}\b", re.I),
    "drive_docs": re.compile(r"drive\.google\.com|docs\.google\.com", re.I),
    "api_key_google": re.compile(r"AIza[0-9A-Za-z_\-]{20,}"),
    "place_id": re.compile(r"place_id", re.I),
}


@dataclass
class Question:
    key: str
    column: str
    label: str
    kind: str
    public: bool
    objective: str = ""
    note: str = ""
    order: list[str] | None = None
    canonical_options_with_commas: list[str] | None = None


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def resolve_repo_path(value: str) -> Path:
    p = Path(value)
    if not p.is_absolute():
        p = REPO_ROOT / p
    return p.resolve()


def is_relative_to(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def assert_safe_write_path(path: Path) -> None:
    resolved = path.resolve()
    if not is_relative_to(resolved, SAFE_OUTPUT_ROOT.resolve()):
        raise RuntimeError(
            f"Salida bloqueada: {rel(resolved)}. El motor experimental solo escribe bajo "
            f"{rel(SAFE_OUTPUT_ROOT)}."
        )
    for forbidden in FORBIDDEN_WRITE_ROOTS:
        if is_relative_to(resolved, forbidden.resolve()):
            raise RuntimeError(f"Salida bloqueada por guardrail: {rel(resolved)}")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_config(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_questions(config: dict[str, Any]) -> list[Question]:
    out = []
    for raw in config["questions"]:
        out.append(
            Question(
                key=raw["key"],
                column=raw["column"],
                label=raw["label"],
                kind=raw["type"],
                public=bool(raw.get("public", True)),
                objective=raw.get("objective", ""),
                note=raw.get("note", ""),
                order=raw.get("order"),
                canonical_options_with_commas=raw.get("canonical_options_with_commas", []),
            )
        )
    return out


def read_source(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path, dtype=str, keep_default_na=False)
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(path, dtype=str, keep_default_na=False)
    raise RuntimeError(f"Formato de fuente no soportado: {path.suffix}")


def clean_cell(value: Any) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value).strip())


def split_multi(value: str, question: Question) -> list[str]:
    text = clean_cell(value)
    if not text:
        return []
    protected: dict[str, str] = {}
    for idx, option in enumerate(question.canonical_options_with_commas or []):
        token = f"<<OPT_{idx}>>"
        if option in text:
            text = text.replace(option, token)
            protected[token] = option
    parts = []
    for piece in re.split(r"[,;|]", text):
        piece = clean_cell(piece)
        if not piece:
            continue
        parts.append(protected.get(piece, piece))
    return parts


def ordered_items(counter: Counter[str], question: Question) -> list[tuple[str, int]]:
    if question.order:
        known = [(label, counter[label]) for label in question.order if counter.get(label, 0)]
        extras = [(k, v) for k, v in counter.items() if k not in set(question.order)]
        return known + sorted(extras, key=lambda item: (-item[1], item[0]))
    return sorted(counter.items(), key=lambda item: (-item[1], item[0]))


def pct(value: int, base: int) -> float:
    return round((value / base * 100), 1) if base else 0.0


def analyze(df: pd.DataFrame, questions: list[Question]) -> dict[str, Any]:
    missing = [q.column for q in questions if q.column not in df.columns]
    if missing:
        raise RuntimeError("Columnas faltantes en la fuente: " + ", ".join(missing))

    total_rows = len(df)
    variables = []
    closed_rows = []
    open_rows = []
    stats: dict[str, Any] = {}

    for question in questions:
        values = [clean_cell(v) for v in df[question.column].tolist()]
        non_empty = [v for v in values if v]
        variables.append(
            {
                "key": question.key,
                "column": question.column,
                "label": question.label,
                "type": question.kind,
                "public": "si" if question.public else "no",
                "n_respuestas": len(non_empty),
                "n_vacios": total_rows - len(non_empty),
                "sensitive_risk": "si" if (question.kind == "sensitive" or not question.public) else "no",
                "objective": question.objective,
            }
        )

        if not question.public or question.kind == "sensitive":
            stats[question.key] = {
                "question": question,
                "base": len(non_empty),
                "items": [],
                "excluded": True,
            }
            continue

        if question.kind == "single":
            counter = Counter(non_empty)
            items = ordered_items(counter, question)
            base = len(non_empty)
            for option, count in items:
                closed_rows.append(
                    {
                        "key": question.key,
                        "pregunta": question.label,
                        "tipo": "seleccion_unica",
                        "categoria": option,
                        "n": count,
                        "porcentaje": pct(count, base),
                        "base": base,
                    }
                )
            stats[question.key] = {"question": question, "base": base, "items": items, "multi": False}

        elif question.kind == "multi":
            counter: Counter[str] = Counter()
            base = 0
            for value in values:
                parts = split_multi(value, question)
                if parts:
                    base += 1
                for part in parts:
                    counter[part] += 1
            items = ordered_items(counter, question)
            for option, count in items:
                closed_rows.append(
                    {
                        "key": question.key,
                        "pregunta": question.label,
                        "tipo": "multi_respuesta",
                        "categoria": option,
                        "n": count,
                        "porcentaje_sobre_respondentes": pct(count, base),
                        "base": base,
                    }
                )
            stats[question.key] = {"question": question, "base": base, "items": items, "multi": True}

        elif question.kind == "open":
            open_rows.append(
                {
                    "key": question.key,
                    "pregunta": question.label,
                    "n_respuestas_no_vacias": len(non_empty),
                    "tratamiento": "No se publican respuestas textuales; solo conteo agregado.",
                }
            )
            stats[question.key] = {"question": question, "base": len(non_empty), "items": [], "open": True}
        else:
            raise RuntimeError(f"Tipo de pregunta no soportado: {question.kind}")

    return {
        "total_rows": total_rows,
        "variables": variables,
        "closed_rows": closed_rows,
        "open_rows": open_rows,
        "stats": stats,
    }


def ensure_dirs(output_dir: Path) -> dict[str, Path]:
    assert_safe_write_path(output_dir)
    chart_dir = output_dir / "graficos"
    table_dir = output_dir / "tablas"
    for path in [output_dir, chart_dir, table_dir]:
        assert_safe_write_path(path)
        path.mkdir(parents=True, exist_ok=True)
    return {"root": output_dir, "charts": chart_dir, "tables": table_dir}


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    assert_safe_write_path(path)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames: list[str] = []
    for row in rows:
        for key in row.keys():
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def chart_slug(key: str) -> str:
    return re.sub(r"[^a-z0-9_]+", "_", key.lower()).strip("_")


def make_chart(items: list[tuple[str, int]], question: Question, base: int, multi: bool, output: Path) -> bool:
    if not items:
        return False
    assert_safe_write_path(output)
    labels = [item[0] for item in items]
    values = [item[1] for item in items]
    height = max(2.8, 0.46 * len(labels) + 1.2)
    fig, ax = plt.subplots(figsize=(8.0, height))
    palette = ["#1F3B57", "#C47C2C", "#678C6C", "#A7B1BA", "#7C5A92", "#556B7B"]
    ax.barh(range(len(labels)), values, color=[palette[i % len(palette)] for i in range(len(labels))])
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels([textwrap.shorten(label, width=46, placeholder="...") for label in labels], fontsize=8.5)
    ax.invert_yaxis()
    max_value = max(values) if values else 1
    ax.set_xlim(0, max(1, max_value * 1.22))
    for i, value in enumerate(values):
        ax.text(value + max_value * 0.02, i, f"{value} ({pct(value, base):.1f}%)", va="center", fontsize=8)
    subtitle = f"Base: {base} respuestas"
    if multi:
        subtitle += " - multi-respuesta; los porcentajes pueden superar 100%."
    ax.set_title(f"{question.label}\n{subtitle}", loc="left", fontsize=10.5)
    ax.set_xlabel("Menciones" if multi else "Respuestas")
    ax.grid(axis="x", alpha=0.18)
    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)
    fig.text(0.01, 0.01, "Fuente: formulario de prueba. Salida agregada, sin datos personales.", fontsize=7, color="#555555")
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(output, dpi=140)
    plt.close(fig)
    return True


def top_sentence(stat: dict[str, Any]) -> str:
    question = stat["question"]
    items = stat.get("items", [])
    base = stat.get("base", 0)
    if stat.get("excluded"):
        return f"{question.label}: excluida de salidas publicas por criterio de privacidad."
    if stat.get("open"):
        return f"{question.label}: {base} respuestas abiertas no vacias; no se publican textos individuales."
    if not items:
        return f"{question.label}: sin respuestas publicables."
    label, count = sorted(items, key=lambda item: (-item[1], item[0]))[0]
    suffix = "menciones" if stat.get("multi") else "respuestas"
    return f"{question.label}: la categoria principal fue '{label}' con {count} {suffix} sobre base {base}."


def build_markdown(config: dict[str, Any], analysis: dict[str, Any], charts: dict[str, Path]) -> str:
    lines = [
        f"# {config['title']}",
        "",
        f"**Subtitulo:** {config.get('subtitle', '')}",
        "",
        "**Documento de prueba.** Este output valida el motor reusable de encuestas y no reemplaza informes vigentes.",
        "",
        "## Alcance",
        "",
        config.get("scope_note", "Muestra exploratoria sin diseno muestral representativo."),
        "",
        "## Datos generales",
        "",
        f"- Respuestas procesadas: {analysis['total_rows']}",
        f"- Fuente declarada: {config.get('source_label', 'formulario')}",
        f"- Fecha de corte declarada: {config.get('cutoff_date', 'sin declarar')}",
        "",
        "## Resultados principales",
        "",
    ]
    for key in config.get("chart_questions", []):
        stat = analysis["stats"].get(key)
        if not stat:
            continue
        lines.append(f"- {top_sentence(stat)}")
    lines += [
        "",
        "## Limitaciones",
        "",
        "- Lectura exploratoria sobre respuestas obtenidas.",
        "- No permite inferencias representativas sobre todo el publico del evento.",
        "- Las preguntas multi-respuesta se informan como menciones; los porcentajes pueden sumar mas de 100%.",
        "- No se publican datos personales, identificadores ni respuestas abiertas textuales.",
        "",
        "## Graficos generados",
        "",
    ]
    for key, path in charts.items():
        lines.append(f"- {key}: `{rel(path)}`")
    lines += [
        "",
        "## Recomendaciones de uso",
        "",
        "- Usar este motor como base tecnica para nuevos informes de encuestas.",
        "- Ajustar el JSON de config para cada evento antes de producir una version real.",
        "- Revisar privacidad y bases n antes de compartir cualquier PDF.",
    ]
    return "\n".join(lines) + "\n"


def paragraph(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(text.replace("&", "&amp;"), style)


def build_pdf(config: dict[str, Any], analysis: dict[str, Any], charts: dict[str, Path], output: Path) -> None:
    assert_safe_write_path(output)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "DGTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        textColor=colors.HexColor("#1F3B57"),
        spaceAfter=12,
    )
    h_style = ParagraphStyle(
        "DGH",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#1F3B57"),
        spaceBefore=8,
        spaceAfter=6,
    )
    body = ParagraphStyle(
        "DGBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#1F2933"),
        spaceAfter=6,
    )
    note = ParagraphStyle(
        "DGNote",
        parent=body,
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#5D6975"),
    )
    story = [
        paragraph("DOCUMENTO DE PRUEBA - NO REEMPLAZA INFORMES VIGENTES", note),
        Spacer(1, 0.3 * cm),
        paragraph(config["title"], title_style),
        paragraph(config.get("subtitle", ""), body),
        Spacer(1, 0.2 * cm),
    ]
    meta_rows = [
        ["Evento", config.get("event_name", "")],
        ["Edicion", config.get("event_edition", "")],
        ["Respuestas procesadas", str(analysis["total_rows"])],
        ["Fuente", config.get("source_label", "formulario")],
        ["Fecha de corte", config.get("cutoff_date", "sin declarar")],
    ]
    table = Table(meta_rows, colWidths=[4.2 * cm, 11.0 * cm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EAF1F8")),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#1F2933")),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#D4DCE4")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story += [
        table,
        Spacer(1, 0.35 * cm),
        paragraph("Alcance y metodologia", h_style),
        paragraph(config.get("scope_note", "Muestra exploratoria sin diseno muestral representativo."), body),
        paragraph(
            "El procesamiento se realiza sin modificar la fuente. Las salidas publicas se limitan a agregados, conteos y graficos.",
            body,
        ),
        paragraph("Resultados principales", h_style),
    ]
    for key in config.get("chart_questions", []):
        stat = analysis["stats"].get(key)
        if stat:
            story.append(paragraph(top_sentence(stat), body))

    story += [
        paragraph("Limitaciones", h_style),
        paragraph(
            "Los resultados describen un conjunto de respuestas obtenidas y no permiten inferencias representativas sobre la totalidad del publico.",
            body,
        ),
        paragraph(
            "En preguntas multi-respuesta, cada opcion se informa como mencion; por lo tanto los porcentajes pueden superar 100%.",
            body,
        ),
        PageBreak(),
        paragraph("Graficos agregados", h_style),
    ]
    for key, chart in charts.items():
        stat = analysis["stats"].get(key, {})
        question = stat.get("question")
        if question:
            story.append(paragraph(question.label, h_style))
        story.append(Image(str(chart), width=16.2 * cm, height=8.8 * cm, kind="proportional"))
        story.append(Spacer(1, 0.2 * cm))

    doc = SimpleDocTemplate(
        str(output),
        pagesize=A4,
        rightMargin=1.8 * cm,
        leftMargin=1.8 * cm,
        topMargin=1.6 * cm,
        bottomMargin=1.4 * cm,
        title=config["title"],
        author="DataGastro",
    )
    doc.build(story)


def scan_text_for_privacy(text: str) -> dict[str, int]:
    return {name: len(pattern.findall(text)) for name, pattern in SENSITIVE_PATTERNS.items()}


def write_privacy_qa(
    output: Path,
    config: dict[str, Any],
    source_hash_before: str,
    source_hash_after: str,
    generated_texts: list[str],
    generated_files: list[Path],
) -> None:
    assert_safe_write_path(output)
    combined = "\n".join(generated_texts)
    findings = scan_text_for_privacy(combined)
    lines = [
        "# QA privacidad - motor encuestas",
        "",
        "## Alcance",
        "",
        "- Revision sobre textos publicables generados por el motor.",
        "- No se revisan datos fuente fila por fila ni se modifica la fuente.",
        "",
        "## Fuente",
        "",
        f"- Fuente declarada: {config.get('source_label', 'formulario')}",
        f"- Hash antes: `{source_hash_before}`",
        f"- Hash despues: `{source_hash_after}`",
        f"- Fuente sin cambios: {'si' if source_hash_before == source_hash_after else 'no'}",
        "",
        "## Patrones revisados",
        "",
    ]
    for name, count in findings.items():
        lines.append(f"- {name}: {count}")
    lines += [
        "",
        "## Archivos generados",
        "",
    ]
    for file in generated_files:
        lines.append(f"- `{rel(file)}`")
    lines += [
        "",
        "## Cierre",
        "",
        "- No se publican filas individuales.",
        "- No se publican respuestas abiertas textuales.",
        "- No se escribio en carpetas de Cafecito ni en datos fuente.",
    ]
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_readme(output: Path, config_path: Path, config: dict[str, Any], generated_files: list[Path]) -> None:
    assert_safe_write_path(output)
    lines = [
        "# README regeneracion - motor encuestas",
        "",
        "Este directorio es una prueba aislada del motor reusable de informes de encuestas.",
        "No reemplaza el informe vigente de Cafecito Belgrano ni modifica outputs existentes.",
        "",
        "## Regenerar",
        "",
        "```powershell",
        f"python scripts/encuestas/generar_informe_encuesta.py --config {rel(config_path)}",
        "```",
        "",
        "## Configuracion",
        "",
        f"- Config: `{rel(config_path)}`",
        f"- Fuente declarada: {config.get('source_label', 'formulario')}",
        f"- Output: `{config.get('output_dir')}`",
        "",
        "## Archivos generados",
        "",
    ]
    for file in generated_files:
        lines.append(f"- `{rel(file)}`")
    lines += [
        "",
        "## Guardrails",
        "",
        "- El motor solo escribe bajo `outputs/encuestas/`.",
        "- La fuente se lee en modo analitico y se valida con hash antes/despues.",
        "- Las columnas sensibles quedan excluidas de salidas publicas.",
    ]
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(config_path: Path) -> list[Path]:
    config_path = config_path.resolve()
    config = load_config(config_path)
    source_path = resolve_repo_path(config["source_path"])
    output_dir = resolve_repo_path(config["output_dir"])
    assert_safe_write_path(output_dir)

    source_hash_before = sha256_file(source_path)
    df = read_source(source_path)
    questions = load_questions(config)
    analysis = analyze(df, questions)
    paths = ensure_dirs(output_dir)

    tables_dir = paths["tables"]
    charts_dir = paths["charts"]
    generated_files: list[Path] = []

    variables_csv = tables_dir / "resumen_variables.csv"
    closed_csv = tables_dir / "resumen_respuestas_cerradas.csv"
    open_csv = tables_dir / "resumen_respuestas_abiertas.csv"
    write_csv(variables_csv, analysis["variables"])
    write_csv(closed_csv, analysis["closed_rows"])
    write_csv(open_csv, analysis["open_rows"])
    generated_files += [variables_csv, closed_csv, open_csv]

    chart_paths: dict[str, Path] = {}
    for key in config.get("chart_questions", []):
        stat = analysis["stats"].get(key)
        if not stat or stat.get("excluded") or stat.get("open"):
            continue
        chart_path = charts_dir / f"{chart_slug(key)}.png"
        if make_chart(stat["items"], stat["question"], stat["base"], bool(stat.get("multi")), chart_path):
            chart_paths[key] = chart_path
            generated_files.append(chart_path)

    md_text = build_markdown(config, analysis, chart_paths)
    md_path = output_dir / "informe_template_test.md"
    md_path.write_text(md_text, encoding="utf-8")
    generated_files.append(md_path)

    pdf_path = output_dir / "INFORME_ENCUESTA_TEMPLATE_TEST.pdf"
    build_pdf(config, analysis, chart_paths, pdf_path)
    generated_files.append(pdf_path)

    source_hash_after = sha256_file(source_path)
    qa_path = output_dir / "QA_PRIVACIDAD_TEMPLATE_TEST.md"
    generated_texts = [
        md_text,
        json.dumps(config, ensure_ascii=True),
        "\n".join(",".join(map(str, row.values())) for row in analysis["variables"]),
        "\n".join(",".join(map(str, row.values())) for row in analysis["closed_rows"]),
        "\n".join(",".join(map(str, row.values())) for row in analysis["open_rows"]),
    ]
    write_privacy_qa(qa_path, config, source_hash_before, source_hash_after, generated_texts, generated_files)
    generated_files.append(qa_path)

    readme_path = output_dir / "README_REGENERACION.md"
    write_readme(readme_path, config_path, config, generated_files)
    generated_files.append(readme_path)

    manifest = {
        "config": rel(config_path),
        "source": rel(source_path),
        "output_dir": rel(output_dir),
        "source_hash_before": source_hash_before,
        "source_hash_after": source_hash_after,
        "source_unchanged": source_hash_before == source_hash_after,
        "total_rows": analysis["total_rows"],
        "generated_files": [rel(path) for path in generated_files],
    }
    manifest_path = output_dir / "manifest_template_test.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    generated_files.append(manifest_path)

    # Reescribe README y QA al final para que el inventario incluya tambien el
    # manifiesto y los propios archivos de cierre.
    write_readme(readme_path, config_path, config, generated_files)
    write_privacy_qa(qa_path, config, source_hash_before, source_hash_after, generated_texts, generated_files)
    return generated_files


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Genera informe reusable de encuesta DataGastro.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    args = parser.parse_args(argv)
    try:
        generated = run(args.config)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print("Archivos generados:")
    for path in generated:
        print(f"- {rel(path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
