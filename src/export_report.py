from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


ROOT = Path(__file__).resolve().parents[1]
RESUMEN_CSV = ROOT / "data" / "analytics" / "analytics_resumen_ejecutivo.csv"
OUTPUT_PDF = ROOT / "outputs" / "resumen_ejecutivo_datagastro.pdf"

INDICADORES_PRINCIPALES = {
    "establecimientos_oferta_gastronomica_f01": "Oferta registrada en guia oficial (F01)",
    "habilitaciones_gastronomicas_f02": "Habilitaciones aprobadas (F02)",
    "habilitaciones_f02_geocodificadas": "Habilitaciones aprobadas geocodificadas con USIG (F02)",
    "espacios_ferias_mercados_f03": "Espacios de ferias, mercados y FIAB (F03)",
    "eventos_gastronomicos_reales_f04_aptos": "Eventos gastronomicos verificados (F04)",
    "programas_politicas_reales_f05_aptos": "Programas y politicas verificados (F05)",
}

QUE_RESPONDE = [
    "Donde se concentra la oferta gastronomica registrada, en volumen y densidad.",
    "Como evolucionan las habilitaciones aprobadas y que rubros se habilitan.",
    "Donde se aprueba actividad gastronomica formal cuando la geocodificacion F02 es valida.",
    "Que espacios publicos, eventos y programas gastronomicos sostiene o acompana la Ciudad.",
]

QUE_NO_RESPONDE = [
    "Cuantos locales gastronomicos estan activos hoy: no hay padron vivo con bajas.",
    "Cuantos locales cerraron ni cuanto sobreviven.",
    "Impacto economico, empleo o ventas del sector.",
    "Saturacion real de barrios sin denominadores de demanda, poblacion o vigencia comercial.",
]


def read_resumen() -> list[dict[str, str]]:
    if not RESUMEN_CSV.exists():
        raise SystemExit(f"ERROR: no existe {RESUMEN_CSV}. Ejecuta primero el pipeline de analytics.")
    with RESUMEN_CSV.open("r", encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))
    if not rows:
        raise SystemExit(f"ERROR: {RESUMEN_CSV} esta vacio. No se generaron numeros.")
    required = {"indicador", "valor"}
    missing = required - set(rows[0])
    if missing:
        raise SystemExit(f"ERROR: {RESUMEN_CSV} no tiene columnas requeridas: {', '.join(sorted(missing))}.")
    return rows


def by_indicator(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row.get("indicador", ""): row for row in rows}


def format_number(value: str) -> str:
    try:
        number = int(float(str(value).replace(".", "").replace(",", ".")))
    except Exception:
        return str(value)
    return f"{number:,}".replace(",", ".")


def data_date(rows: list[dict[str, str]]) -> str:
    dates = [
        row.get("fecha_consulta_max", "").strip()
        for row in rows
        if row.get("fecha_consulta_max", "").strip()
    ]
    return max(dates) if dates else "No disponible"


def source_text(row: dict[str, str]) -> str:
    sources = row.get("fuentes_utilizadas", "").strip()
    warning = row.get("advertencia_grano", "").strip()
    if warning:
        return f"{sources}. {warning}" if sources else warning
    return sources or "No disponible"


def build_indicator_table(rows: list[dict[str, str]]) -> Table:
    indexed = by_indicator(rows)
    table_rows = [["Indicador separado", "Valor", "Fuente / advertencia"]]
    for indicator, label in INDICADORES_PRINCIPALES.items():
        row = indexed.get(indicator)
        if not row:
            table_rows.append([label, "No disponible", "Indicador ausente en analytics_resumen_ejecutivo.csv"])
            continue
        table_rows.append([label, format_number(row.get("valor", "")), source_text(row)])

    table = Table(table_rows, colWidths=[6.0 * cm, 2.6 * cm, 8.0 * cm], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4e5f")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#d0d7de")),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8fafc")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f6f8")]),
            ]
        )
    )
    return table


def bullet_list(items: list[str]) -> str:
    return "<br/>".join(f"- {item}" for item in items)


def build_pdf(rows: list[dict[str, str]]) -> None:
    OUTPUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("DataGastro — Resumen Ejecutivo", styles["Title"]))
    story.append(Paragraph(f"Fecha de datos: {data_date(rows)}", styles["Normal"]))
    story.append(Paragraph(f"Fecha de generacion: {date.today().isoformat()}", styles["Normal"]))
    story.append(Spacer(1, 0.5 * cm))
    story.append(
        Paragraph(
            "Los indicadores se presentan separados por fuente. No se suma F01 + F02 + F03 porque miden universos distintos.",
            styles["BodyText"],
        )
    )
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph("Indicadores principales", styles["Heading2"]))
    story.append(build_indicator_table(rows))
    story.append(Spacer(1, 0.6 * cm))
    story.append(Paragraph("Que responde hoy", styles["Heading2"]))
    story.append(Paragraph(bullet_list(QUE_RESPONDE), styles["BodyText"]))
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph("Que no responde todavia", styles["Heading2"]))
    story.append(Paragraph(bullet_list(QUE_NO_RESPONDE), styles["BodyText"]))

    doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        title="DataGastro — Resumen Ejecutivo",
    )
    doc.build(story)


def main() -> None:
    rows = read_resumen()
    build_pdf(rows)
    print(f"OK: resumen ejecutivo generado en {OUTPUT_PDF}")


if __name__ == "__main__":
    main()
