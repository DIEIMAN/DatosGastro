"""Genera la correccion final V4_1 del informe de mercados CABA.

V4_1 no sobrescribe V4. Mantiene el orden y la estructura de V4, corrige
microcopy institucional, tildes visibles y nombres homogeneos, y vuelve a
componer el PDF final con numeracion correcta. No hace requests ni usa APIs.
"""
from __future__ import annotations

import csv
import importlib.util
import re
import shutil
import subprocess
import tempfile
import textwrap
import zipfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs" / "mercados_caba"
SAN = ROOT / "outputs" / "mercados_caba" / "sanitized"

V3_SOURCE = ROOT / "src" / "mercados_caba" / "build_pdf_from_markdown_master.py"

PDF_V4_1 = SAN / "INFORME_FINAL_MERCADOS_GASTRONOMICOS_CABA_FINAL_V4_1.pdf"
SUMMARY_V4_1 = SAN / "RESUMEN_EJECUTIVO_MERCADOS_GASTRONOMICOS_CABA_FINAL_V4_1.pdf"
PACK_V4_1 = SAN / "PACK_ENTREGABLE_MERCADOS_GASTRONOMICOS_CABA_FINAL_V4_1.zip"
README_V4_1 = DOCS / "README_REGENERAR_INFORME_FINAL_V4_1.md"
OPORTUNIDAD_V4_1 = DOCS / "OPORTUNIDAD_GESTION_MERCADOS_CABA_V4_1.md"
ANEXO_METODOLOGIA_V4_1 = DOCS / "ANEXO_FUENTES_Y_METODOLOGIA_MERCADOS_V4_1.md"
OPORTUNIDADES_CSV_V4_1 = SAN / "oportunidades_gestion_mercados_v4_1.csv"
PILOTOS_CSV_V4_1 = SAN / "pilotos_recomendados_mercados_v4_1.csv"
PUBLICOS_CSV_V4_1 = SAN / "publicos_objetivo_mercados_v4_1.csv"

OPORTUNIDAD_V4 = DOCS / "OPORTUNIDAD_GESTION_MERCADOS_CABA_V4.md"
ANEXO_METODOLOGIA_V4 = DOCS / "ANEXO_FUENTES_Y_METODOLOGIA_MERCADOS_V4.md"
OPORTUNIDADES_CSV_V4 = SAN / "oportunidades_gestion_mercados_v4.csv"
PILOTOS_CSV_V4 = SAN / "pilotos_recomendados_mercados_v4.csv"
PUBLICOS_CSV_V4 = SAN / "publicos_objetivo_mercados_vfinal.csv"

A4 = (8.27, 11.69)
INK = "#1f3b57"
BLUE = "#2c7fb8"
ORANGE = "#c0762b"
GREEN = "#1a9850"
RED = "#c0392b"
GREY = "#555555"
SOFT_BLUE = "#eaf1f8"
SOFT_ORANGE = "#f7ebdc"
WHITE = "#ffffff"
LINE = "#d9dee5"


def run(cmd: list[str], cwd: Path | None = None) -> str:
    result = subprocess.run(
        cmd,
        cwd=cwd or ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"Fallo {' '.join(cmd[:1])}: {detail}")
    return result.stdout


TEXT_REPLACEMENTS = {
    "Icono": "Ícono",
    "turistico": "turístico",
    "turisticos": "turísticos",
    "turistica": "turística",
    "interes": "interés",
    "clasico": "clásico",
    "economia": "economía",
    "Senales": "Señales",
    "senales": "señales",
    "mencion": "mención",
    "Situacion": "Situación",
    "situacion": "situación",
    "Cerro": "Cerró",
    "validacion": "validación",
    "validaciones": "validaciones",
    "publica": "pública",
    "publico": "público",
    "publicos": "públicos",
    "gastronomico": "gastronómico",
    "gastronomicos": "gastronómicos",
    "Gastronomico": "Gastronómico",
    "Gastronomicos": "Gastronómicos",
    "San Nicolas": "San Nicolás",
    "El Galpon": "El Galpón",
    "Patio Gastronomico Rodrigo Bueno": "Patio Gastronómico Rodrigo Bueno",
    "BA Market": "Buenos Aires Market",
    "post-trabajo": "franja post-laboral",
    "after office": "franja post-laboral",
    "clase express": "demostración gastronómica breve",
    "evento mensual con puestos": "activación mensual articulada con puestos",
    "recorrido gastronómico curado": "recorrido gastronómico diseñado",
    "Aprendizaje Madrid -> CABA aplicado al universo activo identificado.": (
        "Aprendizajes de Madrid para Buenos Aires, aplicados al universo activo identificado."
    ),
    "Aprendizaje Madrid -> oportunidad Buenos Aires": "Aprendizajes de Madrid para Buenos Aires",
    "La oportunidad no es solo contar mercados: es convertirlos en una agenda pública de experiencias urbanas.": (
        "La oportunidad no es solo contar mercados: es convertirlos en una agenda pública "
        "de experiencias gastronómicas, barriales y turísticas."
    ),
    "opcion": "opción",
    "menus": "menús",
    "Mediodia": "Mediodía",
    "mediodia": "mediodía",
    "cercania": "cercanía",
    "habito": "hábito",
    "comunicacion": "comunicación",
    "programacion": "programación",
    "accion": "acción",
    "Accion": "Acción",
    "gestion": "gestión",
    "Gestion": "Gestión",
    "diferenciacion": "diferenciación",
    "innovacion": "innovación",
    "incubacion": "incubación",
    "estacion": "estación",
    "linea": "línea",
    "produccion": "producción",
    "segun": "según",
    "disenar": "diseñar",
    "Diseñar una activacion mensual liviana": "Diseñar una activación mensual liviana",
}


def fix_text(value: str) -> str:
    fixed = value
    for old, new in TEXT_REPLACEMENTS.items():
        if " " in old or "->" in old or "+" in old:
            fixed = fixed.replace(old, new)
        else:
            fixed = re.sub(rf"\b{re.escape(old)}\b", new, fixed)
    return fixed


def load_v3_module():
    spec = importlib.util.spec_from_file_location("mercados_v3_builder", V3_SOURCE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"No se pudo importar {V3_SOURCE}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def patch_v3_module(module, tmp: Path) -> None:
    module.PDF_V2 = tmp / "base_v2_1.pdf"
    module.PDF_RESUMEN_V2 = tmp / "resumen_v2_1.pdf"
    module.PDF_V3 = tmp / "base_v3_1.pdf"
    module.PDF_RESUMEN_V3 = tmp / "resumen_v3_1.pdf"

    module.TYPE_LABEL = {
        "mercado_historico": "histórico",
        "mercado_barrial_alimentario": "barrial alimentario",
        "food_hall": "food hall",
        "patio_gastronomico": "patio gastronómico",
        "mercado_de_productores": "mercado de productores",
        "feria_gastronomica": "feria gastronómica",
    }
    module.PATRIMONIALES = [
        ("Mercado de San Telmo", "1897", "Ícono turístico de la Ciudad.", module.ORANGE),
        ("Mercado de Belgrano", "1891", "Renovado con food court.", module.BLUE),
        ("Mercado del Progreso", "1889", "Sitio de interés cultural; clásico barrial de abasto.", module.GREEN),
        ("Mercado San Nicolás", "centenario", "Mercado renovado en Microcentro.", module.BLUE),
        ("Mercado Bonpland", "economía social", "Referente de consumo consciente.", module.GREEN),
    ]
    module.NO_ACTIVOS = [
        (
            "Mercado Soho",
            "relevante no contabilizado",
            "Señales de cierre y falta de actividad reciente verificable.",
            "Vuelve al conteo si se valida actividad.",
            module.ORANGE,
        ),
        (
            "Mercat Caballito",
            "relevante no contabilizado",
            "Señales de cierre; en fuente oficial solo figura como mención de evento.",
            "Requiere validación antes de contar.",
            module.ORANGE,
        ),
        (
            "El Galpón",
            "relevante no contabilizado",
            "Situación operativa no clara; match de Google inconsistente.",
            "Productores relevante; requiere validación.",
            module.ORANGE,
        ),
        (
            "Mercado de los Carruajes",
            "cerrado documentado",
            "Cerró en abril de 2025 y se reconvierte a eventos.",
            "Antecedente relevante, no activo.",
            module.RED,
        ),
    ]
    module.DECISION_CARDS_V2 = [
        (
            "Circuitos turísticos",
            "Articular los mercados de mayor atractivo turístico en recorridos integrados.",
            "San Telmo, Belgrano, Gourmand",
            module.BLUE,
        ),
        (
            "Productores y economía social",
            "Apoyar mercados y ferias de productores y consumo consciente.",
            "Bonpland, Sabe la Tierra, Buenos Aires Market",
            module.GREEN,
        ),
        (
            "Patios públicos",
            "Usar los patios gastronómicos públicos como dinamizadores barriales.",
            "Lecheros, Smart Plaza, Costanera, Rodrigo Bueno",
            module.BLUE,
        ),
        (
            "Base candidata trazable",
            "Sostener un catálogo con tipología y estado operativo, actualizable.",
            "Todos los activos identificados",
            module.ORANGE,
        ),
        (
            "Validación territorial",
            "Ordenar la verificación en terreno por respaldo documental.",
            "Empezar por respaldo medio o a validar",
            module.ORANGE,
        ),
        (
            "Información pública uniforme",
            "Publicar horarios, gestión y oferta de cada mercado de forma homogénea.",
            "Todos los activos identificados",
            module.BLUE,
        ),
    ]
    module.PUBLICOS_INSIGHTS = [
        (
            "Turístico / patrimonial",
            "San Telmo, Costanera Norte y Gourmand concentran mayor potencial para recorridos, paseo y consumo de experiencia.",
            module.ORANGE,
        ),
        (
            "Barrial / familiar",
            "Belgrano, Progreso, Lecheros y Buenos Aires Market muestran mejor encaje para activaciones de cercanía y hábito.",
            module.BLUE,
        ),
        (
            "Trabajadores / franja post-laboral",
            "San Nicolás, Smart Plaza Parque Patricios y Mercat Villa Crespo: almuerzo laboral.",
            module.GREEN,
        ),
        (
            "Productores / consumo consciente",
            "Bonpland, Sabe la Tierra y Buenos Aires Market concentran la lógica de productores, economía social y consumo saludable.",
            module.GREEN,
        ),
        (
            "Comunitario / colectividades",
            "Rodrigo Bueno, Bonpland y Sabe la Tierra tienen potencial para activaciones de comunidad, colectividades y cocina cultural.",
            module.ORANGE,
        ),
    ]
    module.PUBLICOS_COMPACT_MATRIX = [
        ["Turístico / patrimonial", "San Telmo, Costanera Norte, Gourmand", "recorridos, degustaciones, circuitos"],
        ["Barrial / familiar", "Belgrano, Progreso, Lecheros, Buenos Aires Market", "cercanía, hábito, fines de semana"],
        ["Trabajadores / franja post-laboral", "San Nicolás, Smart Plaza, Mercat Villa Crespo", "almuerzo, salida post-laboral, entre semana"],
        ["Productores / consumo consciente", "Bonpland, Sabe la Tierra, Buenos Aires Market", "ferias, talleres, consumo responsable"],
        ["Comunitario / colectividades", "Rodrigo Bueno, Bonpland, Sabe la Tierra", "cocina cultural, colectividades, identidad"],
    ]

    original_read_csv = module.read_csv

    def read_csv_fixed(name: str) -> list[dict[str, str]]:
        rows = original_read_csv(name)
        fixed_rows: list[dict[str, str]] = []
        for row in rows:
            fixed = dict(row)
            for key in ["nombre", "gestion", "barrio"]:
                if key in fixed:
                    fixed[key] = fix_text(fixed[key])
            fixed_rows.append(fixed)
        return fixed_rows

    module.read_csv = read_csv_fixed

    original_box = module.box

    def box_fixed(fig, x, y, w, h, title, text, kind="resp"):
        if title == "Nota metodológica" and text.startswith("El mapa muestra solo mercados con sede fija"):
            return original_box(fig, x, 0.066, w, 0.092, title, text, kind)
        return original_box(fig, x, y, w, h, title, text, kind)

    module.box = box_fixed


def page() -> plt.Figure:
    fig = plt.figure(figsize=A4)
    fig.patch.set_facecolor(WHITE)
    return fig


def footer(fig: plt.Figure, note: str = "") -> None:
    fig.lines.append(Line2D([0.07, 0.93], [0.056, 0.056], transform=fig.transFigure, color="#dddddd", lw=0.8))
    fig.text(0.07, 0.036, "DataGastro · Mercados gastronómicos de CABA · Informe final", color=GREY, fontsize=7.8)
    if note:
        fig.text(0.93, 0.036, note, color=GREY, fontsize=7.5, ha="right")


def header(fig: plt.Figure, page_no: int, title: str, subtitle: str = "") -> float:
    fig.text(0.07, 0.957, "DataGastro | Mercados CABA", color=RED, fontsize=8.3, fontweight="bold")
    fig.text(0.93, 0.957, f"Pág. {page_no}", color=GREY, fontsize=8.3, ha="right")
    lines = textwrap.wrap(title, 48)
    for i, line in enumerate(lines):
        fig.text(0.07, 0.925 - i * 0.030, line, color=INK, fontsize=16.5, fontweight="bold", va="top")
    y = 0.925 - len(lines) * 0.030
    fig.lines.append(Line2D([0.07, 0.35], [y + 0.004, y + 0.004], transform=fig.transFigure, color=ORANGE, lw=2.2))
    if subtitle:
        sub_lines = textwrap.wrap(subtitle, 92)
        for i, line in enumerate(sub_lines):
            fig.text(0.07, y - 0.014 - i * 0.020, line, color=GREY, fontsize=9.5, style="italic", va="top")
        y -= 0.014 + len(sub_lines) * 0.020
    return y - 0.028


def wrap_text(text: str, width: int) -> list[str]:
    return textwrap.wrap(text, width=width, break_long_words=False)


def panel(
    fig: plt.Figure,
    x: float,
    y: float,
    w: float,
    h: float,
    title: str,
    body: str,
    accent: str = BLUE,
    bg: str = SOFT_BLUE,
    title_size: float = 9.0,
    body_size: float = 8.4,
) -> None:
    fig.patches.append(Rectangle((x, y), w, h, transform=fig.transFigure, facecolor=bg, edgecolor=accent, lw=1.0))
    fig.patches.append(Rectangle((x, y), 0.012, h, transform=fig.transFigure, facecolor=accent, edgecolor=accent))
    fig.text(x + 0.025, y + h - 0.026, title, color=accent, fontsize=title_size, fontweight="bold", va="top")
    yy = y + h - 0.055
    for line in wrap_text(body, max(34, int(w / 0.0088)))[:7]:
        if yy < y + 0.014:
            break
        fig.text(x + 0.025, yy, line, color="#222222", fontsize=body_size, va="top")
        yy -= 0.018


def opportunity_card(fig: plt.Figure, x: float, y: float, w: float, h: float, title: str, markets: str, action: str, accent: str) -> None:
    fig.patches.append(Rectangle((x, y), w, h, transform=fig.transFigure, facecolor=WHITE, edgecolor=LINE, lw=1.0))
    fig.patches.append(Rectangle((x, y + h - 0.038), w, 0.038, transform=fig.transFigure, facecolor=accent, edgecolor=accent))
    fig.text(x + 0.016, y + h - 0.012, title, color=WHITE, fontsize=8.8, fontweight="bold", va="top")
    yy = y + h - 0.058
    fig.text(x + 0.016, yy, "Mercados", color=accent, fontsize=7.7, fontweight="bold", va="top")
    yy -= 0.018
    for line in wrap_text(markets, 45)[:3]:
        fig.text(x + 0.016, yy, line, color="#222222", fontsize=7.8, va="top")
        yy -= 0.016
    yy -= 0.010
    fig.text(x + 0.016, yy, "Acción", color=accent, fontsize=7.7, fontweight="bold", va="top")
    yy -= 0.018
    for line in wrap_text(action, 45)[:3]:
        fig.text(x + 0.016, yy, line, color="#222222", fontsize=7.8, va="top")
        yy -= 0.016


def pilot_card(fig: plt.Figure, x: float, y: float, w: float, h: float, title: str, rows: list[tuple[str, str]], accent: str) -> None:
    fig.patches.append(Rectangle((x, y), w, h, transform=fig.transFigure, facecolor=WHITE, edgecolor=LINE, lw=1.0))
    fig.patches.append(Rectangle((x, y + h - 0.040), w, 0.040, transform=fig.transFigure, facecolor=accent, edgecolor=accent))
    for i, line in enumerate(wrap_text(title, 42)[:2]):
        fig.text(x + 0.014, y + h - 0.011 - i * 0.014, line, color=WHITE, fontsize=7.6, fontweight="bold", va="top")
    yy = y + h - 0.058
    for label, value in rows:
        fig.text(x + 0.014, yy, label, color=accent, fontsize=7.0, fontweight="bold", va="top")
        yy -= 0.014
        for line in wrap_text(value, 43)[:2]:
            fig.text(x + 0.014, yy, line, color="#222222", fontsize=7.1, va="top")
            yy -= 0.014
        yy -= 0.006


def build_new_pages(path: Path) -> None:
    with PdfPages(path) as pdf:
        fig = page()
        header(
            fig,
            3,
            "Oportunidad de gestión: mercados como red de experiencias",
            "Aprendizajes de Madrid para Buenos Aires, aplicados al universo activo identificado.",
        )
        panel(
            fig,
            0.07,
            0.730,
            0.86,
            0.105,
            "Tesis",
            "CABA cuenta con una red diversa de mercados gastronómicos que puede transformarse en una herramienta de activación barrial, turística, cultural y productiva.",
            ORANGE,
            SOFT_ORANGE,
            body_size=8.7,
        )
        panel(
            fig,
            0.07,
            0.590,
            0.86,
            0.110,
            "Aprendizaje Madrid",
            "La experiencia de Madrid muestra que los mercados contemporáneos no se posicionan solo por su oferta comercial: se vuelven destinos cuando comunican experiencia, identidad, comunidad y gastronomía.",
            BLUE,
            SOFT_BLUE,
            body_size=8.5,
        )
        cards = [
            ("Turismo y marca ciudad", "San Telmo, Gourmand, Costanera Norte y mercados históricos.", "Circuitos gastronómicos y culturales.", BLUE),
            ("Activación barrial", "Belgrano, Progreso, Lecheros, Rodrigo Bueno y Smart Plaza.", "Programación de cercanía y eventos de hábito.", GREEN),
            ("Productores y economía social", "Bonpland, Sabe la Tierra y Buenos Aires Market.", "Consumo responsable, productores y ferias temáticas.", GREEN),
            ("Gestión pública ordenada", "Todos los activos identificados.", "Base candidata para validar, comunicar, programar y no mezclar universos.", ORANGE),
        ]
        positions = [(0.07, 0.385), (0.52, 0.385), (0.07, 0.205), (0.52, 0.205)]
        for (x, y), item in zip(positions, cards):
            opportunity_card(fig, x, y, 0.41, 0.160, *item)
        panel(
            fig,
            0.07,
            0.075,
            0.86,
            0.105,
            "Cierre ejecutivo",
            "La oportunidad no es solo contar mercados: es convertirlos en una agenda pública de experiencias gastronómicas, barriales y turísticas.",
            ORANGE,
            SOFT_ORANGE,
            body_size=8.4,
        )
        footer(fig, "Lectura de oportunidad; no cambia conteos")
        pdf.savefig(fig)
        plt.close(fig)

        fig = page()
        header(
            fig,
            12,
            "Pilotos recomendados de activación",
            "Hipótesis operativas para pasar de inventario a agenda pública.",
        )
        pilots = [
            (
                "San Nicolás - Almuerzo cultural para trabajadores",
                [("Público", "trabajadores de Microcentro / Tribunales"), ("Franja", "miércoles 12:30 a 14:30"), ("Primer paso", "degustación + demostración gastronómica breve")],
                BLUE,
            ),
            (
                "Belgrano - Activación en franja post-laboral barrial",
                [("Público", "vecinos, familias, adultos"), ("Franja", "martes 17:00 a 19:00"), ("Primer paso", "activación mensual articulada con puestos")],
                GREEN,
            ),
            (
                "Bonpland / Sabe la Tierra / Buenos Aires Market - Productores",
                [("Público", "consumo consciente, familias, productores"), ("Franja", "fin de semana o viernes tarde"), ("Primer paso", "feria temática + taller corto")],
                ORANGE,
            ),
            (
                "San Telmo / Gourmand - Circuito turístico gastronómico",
                [("Público", "turistas, visitantes, consumo de experiencia"), ("Franja", "fin de semana o tarde-noche"), ("Primer paso", "recorrido gastronómico diseñado")],
                BLUE,
            ),
            (
                "Rodrigo Bueno - Cocina comunitaria y colectividades",
                [("Público", "comunidad, colectividades, vecinos"), ("Franja", "fin de semana / tarde-noche"), ("Primer paso", "edición latinoamericana o de colectividades")],
                GREEN,
            ),
        ]
        positions = [(0.07, 0.675), (0.52, 0.675), (0.07, 0.455), (0.52, 0.455), (0.07, 0.235)]
        for (x, y), (title, rows, accent) in zip(positions, pilots):
            pilot_card(fig, x, y, 0.41, 0.170, title, rows, accent)
        panel(
            fig,
            0.52,
            0.265,
            0.41,
            0.140,
            "Cuidado metodológico",
            "Los pilotos son hipótesis operativas. Requieren validación territorial, articulación con operadores y definición presupuestaria.",
            ORANGE,
            SOFT_ORANGE,
            body_size=8.1,
        )
        panel(
            fig,
            0.07,
            0.100,
            0.86,
            0.090,
            "Uso recomendado",
            "Priorizar pilotos simples, medibles y comunicables antes de escalar una agenda metropolitana de mercados.",
            BLUE,
            SOFT_BLUE,
            body_size=8.4,
        )
        footer(fig, "Pilotos sujetos a validación territorial")
        pdf.savefig(fig)
        plt.close(fig)


def tex_page(source: str, source_page: int, final_page: int) -> str:
    if final_page == 1:
        overlay = (
            r"\AddToShipoutPictureFG*{"
            rf"\put(553,813){{\makebox[0pt][r]{{\textcolor{{white}}{{\small Pág. {final_page}}}}}}}"
            r"}%"
        )
    else:
        overlay = (
            r"\AddToShipoutPictureFG*{"
            r"\put(488,806){\color{white}\rule{94pt}{18pt}}"
            rf"\put(553,813){{\makebox[0pt][r]{{\textcolor{{gray}}{{\small Pág. {final_page}}}}}}}"
            r"}%"
        )
    return "\n".join(
        [
            rf"\AddToShipoutPictureBG*{{\AtPageLowerLeft{{\includegraphics[page={source_page},width=\paperwidth,height=\paperheight]{{{source}}}}}}}%",
            overlay,
            r"\null\newpage",
        ]
    )


def build_final_pdf_with_overlays(base_v3: Path, new_pages: Path, tmp: Path) -> None:
    tmp_base = tmp / "base_v3_1.pdf"
    tmp_new_pages = tmp / "new_pages_v4_1.pdf"
    if base_v3.resolve() != tmp_base.resolve():
        shutil.copyfile(base_v3, tmp_base)
    if new_pages.resolve() != tmp_new_pages.resolve():
        shutil.copyfile(new_pages, tmp_new_pages)
    sequence = [
        ("base_v3_1.pdf", 1),
        ("base_v3_1.pdf", 2),
        ("new_pages_v4_1.pdf", 1),
        ("base_v3_1.pdf", 3),
        ("base_v3_1.pdf", 4),
        ("base_v3_1.pdf", 5),
        ("base_v3_1.pdf", 6),
        ("base_v3_1.pdf", 7),
        ("base_v3_1.pdf", 8),
        ("base_v3_1.pdf", 9),
        ("base_v3_1.pdf", 10),
        ("new_pages_v4_1.pdf", 2),
        ("base_v3_1.pdf", 11),
        ("base_v3_1.pdf", 12),
    ]
    pages = [tex_page(source, source_page, final_page) for final_page, (source, source_page) in enumerate(sequence, start=1)]
    tex = "\n".join(
        [
            r"\documentclass[a4paper]{article}",
            r"\usepackage[utf8]{inputenc}",
            r"\usepackage[T1]{fontenc}",
            r"\usepackage[margin=0pt]{geometry}",
            r"\usepackage{graphicx}",
            r"\usepackage{xcolor}",
            r"\usepackage{eso-pic}",
            r"\pagestyle{empty}",
            r"\setlength{\parindent}{0pt}",
            r"\begin{document}",
            *pages,
            r"\end{document}",
        ]
    )
    tex_path = tmp / "informe_v4_1.tex"
    tex_path.write_text(tex, encoding="utf-8")
    run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "-output-directory", str(tmp), str(tex_path)], cwd=tmp)
    shutil.copyfile(tmp / "informe_v4_1.pdf", PDF_V4_1)


def write_fixed_text_file(src: Path, dst: Path) -> None:
    text = src.read_text(encoding="utf-8")
    text = fix_text(text)
    text = text.replace("->", "para")
    dst.write_text(text, encoding="utf-8")


def write_fixed_csv(src: Path, dst: Path) -> None:
    with src.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
        fieldnames = fh.readline()
    # Re-read fieldnames because DictReader consumes them internally.
    with src.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        names = reader.fieldnames or []
        rows = list(reader)
    with dst.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=names)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: fix_text(value) for key, value in row.items()})


def build_support_files() -> None:
    write_fixed_text_file(OPORTUNIDAD_V4, OPORTUNIDAD_V4_1)
    write_fixed_text_file(ANEXO_METODOLOGIA_V4, ANEXO_METODOLOGIA_V4_1)
    write_fixed_csv(OPORTUNIDADES_CSV_V4, OPORTUNIDADES_CSV_V4_1)
    write_fixed_csv(PILOTOS_CSV_V4, PILOTOS_CSV_V4_1)
    write_fixed_csv(PUBLICOS_CSV_V4, PUBLICOS_CSV_V4_1)
    README_V4_1.write_text(
        "\n".join(
            [
                "# Regenerar informe final V4_1 de mercados gastronómicos CABA",
                "",
                "V4_1 es una corrección formal quirúrgica de V4:",
                "",
                "- mantiene 14 páginas y el mismo orden;",
                "- no cambia datos, conteos, universo ni estados;",
                "- corrige tildes, nombres y microcopy institucional;",
                "- reemplaza el separador técnico Madrid -> CABA por una frase institucional;",
                "- genera un pack V4_1 separado para comparar con V4.",
                "",
                "## Comandos",
                "",
                "```powershell",
                "python src\\mercados_caba\\build_pdf_final_v4_1_from_v3.py",
                "python src\\mercados_caba\\validate_mercados_final_v4_1.py",
                "```",
            ]
        ),
        encoding="utf-8",
    )


def build_pack_v4_1() -> None:
    files = [
        PDF_V4_1,
        SUMMARY_V4_1,
        README_V4_1,
        OPORTUNIDAD_V4_1,
        ANEXO_METODOLOGIA_V4_1,
        OPORTUNIDADES_CSV_V4_1,
        PILOTOS_CSV_V4_1,
        PUBLICOS_CSV_V4_1,
    ]
    with zipfile.ZipFile(PACK_V4_1, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in files:
            zf.write(path, path.relative_to(ROOT).as_posix())


def main() -> int:
    required = [
        V3_SOURCE,
        OPORTUNIDAD_V4,
        ANEXO_METODOLOGIA_V4,
        OPORTUNIDADES_CSV_V4,
        PILOTOS_CSV_V4,
        PUBLICOS_CSV_V4,
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError("Faltan insumos V4_1:\n" + "\n".join(missing))

    with tempfile.TemporaryDirectory(prefix="mercados_v4_1_") as tmp_name:
        tmp = Path(tmp_name)
        module = load_v3_module()
        patch_v3_module(module, tmp)
        meta = module.load_master_meta()
        module.build_pdf_v2(meta)
        module.build_summary_pdf_v2(meta)
        module.build_pdf_v3(meta)
        new_pages = tmp / "new_pages_v4_1.pdf"
        build_new_pages(new_pages)
        build_final_pdf_with_overlays(module.PDF_V3, new_pages, tmp)
        shutil.copyfile(module.PDF_RESUMEN_V2, SUMMARY_V4_1)

    build_support_files()
    build_pack_v4_1()
    print(f"ok: {PDF_V4_1}")
    print(f"ok: {SUMMARY_V4_1}")
    print(f"ok: {PACK_V4_1}")
    print(f"ok: {README_V4_1}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
