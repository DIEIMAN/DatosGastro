"""Genera la version DataGastro del informe Cafecito.

Lee el XLSX original en modo solo lectura usando el analizador base, regenera
graficos cuidados, actualiza el Markdown/DOCX y crea un PDF institucional.
No modifica fuentes originales ni expone datos personales.

Uso:
    python scripts/cafecito/generar_informe_datagastro.py
"""
from __future__ import annotations

import csv
import re
import shutil
import sys
import textwrap
import zipfile
from collections import Counter
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle  # noqa: E402

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.cafecito import analizar_cafecito as base  # noqa: E402

OUT_DIR = REPO_ROOT / "outputs" / "cafecito"
GRAF_DG_DIR = OUT_DIR / "graficos_datagastro"
DOCS_DIR = REPO_ROOT / "docs" / "cafecito"
REPORT_MD = DOCS_DIR / "INFORME_CAFECITO_EXPLORATORIO.md"
README_MD = DOCS_DIR / "README_CAFECITO.md"
DOCX_REPORT = OUT_DIR / "INFORME_CAFECITO_GRAFICOS.docx"
PDF_REPORT = OUT_DIR / "INFORME_CAFECITO_DATAGASTRO.pdf"
FINAL_DIR = REPO_ROOT / "Cafesito" / "final"
FINAL_PDF = FINAL_DIR / "INFORME_CAFECITO_DATAGASTRO.pdf"

FOOTER = "DataGastro · Cafecito BA en tu barrio · Informe exploratorio"

INK = "#1F3B57"
BLUE = "#2C7FB8"
BLUE_DARK = "#17324D"
ORANGE = "#C0762B"
COFFEE = "#6F4E37"
WARM = "#E6B17E"
GREY = "#68717C"
LIGHT = "#EEF2F6"
LINE = "#D7DEE8"
BG = "#FAFBFC"
GREEN = "#2E7D6B"

POLISH_REPLACEMENTS = {
    "concentracion": "concentración",
    "programacion": "programación",
    "recomendacion": "recomendación",
    "informacion": "información",
    "comunicacion": "comunicación",
    "gestion": "gestión",
    "publico": "público",
    "publica": "pública",
    "publicas": "públicas",
    "publicos": "públicos",
    "electronico": "electrónico",
    "valida": "válida",
    "validas": "válidas",
    "tenia": "tenía",
    "tenian": "tenían",
    "esta": "está",
    "estan": "están",
    "mas": "más",
    "interes": "interés",
    "intereso": "interesó",
    "lineas": "líneas",
    "senal": "señal",
    "senales": "señales",
    "opcion": "opción",
    "opciones": "opciones",
    "canonica": "canónica",
    "canonicas": "canónicas",
    "friccion": "fricción",
    "conexion": "conexión",
    "graficos ": "gráficos ",
    "Grafico": "Gráfico",
    "Genero": "Género",
    "Como ": "Cómo ",
    "Que ": "Qué ",
    "Vinculo": "Vínculo",
    "dinamica": "dinámica",
    "analisis": "análisis",
    "metodologica": "metodológica",
    "metodologico": "metodológico",
    "gastronomica": "gastronómica",
    "gastronomicas": "gastronómicas",
    "tematica": "temática",
    "multiples": "múltiples",
    "pasteleria": "pastelería",
    "Pasteleria": "Pastelería",
    "cafe": "café",
    "Cafe": "Café",
    "territorial": "territorial",
    "anos": "años",
    "pagina": "página",
    "identificacion": "identificación",
}


def polish_text(text: str) -> str:
    for src, dst in sorted(POLISH_REPLACEMENTS.items(), key=lambda item: len(item[0]), reverse=True):
        if " " in src:
            text = text.replace(src, dst)
        else:
            text = re.sub(rf"(?<![\w]){re.escape(src)}(?![\w])", dst, text)
    return text


GRAPH_META = {
    "kpi_cards": {
        "file": "00_kpi_cards_datagastro.png",
        "title": "Indicadores de lectura rapida",
        "reading": "El relevamiento permite leer perfil, canales y potencial de contacto sin exponer datos personales.",
    },
    "edad": {
        "file": "01_edad_datagastro.png",
        "title": "Edad declarada",
        "reading": "La muestra se concentra en 25 a 34 y, en conjunto, en 18 a 44. Es una senal de publico joven-adulto dentro de quienes respondieron.",
    },
    "genero": {
        "file": "02_genero_datagastro.png",
        "title": "Genero declarado",
        "reading": "Predominan respuestas de mujeres. Es dato declarado de la muestra y no debe proyectarse al total del publico del evento.",
    },
    "procedencia": {
        "file": "03_procedencia_datagastro.png",
        "title": "Procedencia macro",
        "reading": "CABA concentra la mayor parte de las respuestas. La lectura territorial se mantiene a nivel macro para evitar granularidad identificable.",
    },
    "primera_vez": {
        "file": "04_primera_vez_datagastro.png",
        "title": "Vinculo previo con eventos gastronomicos",
        "reading": "Conviven publico recurrente y captacion nueva. Sirve para pensar fidelizacion sin perder capacidad de atraer primeras visitas.",
    },
    "con_quien": {
        "file": "05_con_quien_datagastro.png",
        "title": "Con quien vino",
        "reading": "Pareja, amigos y familia explican casi toda la asistencia declarada. La propuesta funciona como salida social y familiar.",
    },
    "canal_llegada": {
        "file": "06_canal_llegada_datagastro.png",
        "title": "Canales de llegada",
        "reading": "Instagram lidera la difusion y la recomendacion interpersonal aparece como segundo canal. La categoria con coma interna queda unificada.",
    },
    "interes": {
        "file": "07_interes_principal_datagastro.png",
        "title": "Atractivo principal",
        "reading": "Probar cafe/cafeterias fue el principal atractivo, seguido por salir a pasear. Hay valor tanto gastronomico como experiencial.",
    },
    "eventos_futuros": {
        "file": "08_eventos_futuros_datagastro.png",
        "title": "Intereses para eventos futuros",
        "reading": "Vino, pasteleria, food trucks, cafe y ferias/mercados aparecen como senales iniciales para programacion futura.",
    },
    "contacto": {
        "file": "09_contacto_datagastro.png",
        "title": "Consentimiento de contacto",
        "reading": "La aceptacion de contacto abre una oportunidad de comunicacion futura; los correos quedan excluidos de outputs publicos.",
    },
    "matriz": {
        "file": "10_matriz_preguntas_decisiones.png",
        "title": "Que pregunta permite decidir que",
        "reading": "El formulario sirve no solo para describir publico, sino para ordenar decisiones de comunicacion, programacion y operativo.",
    },
    "sintesis": {
        "file": "11_sintesis_conclusiones.png",
        "title": "Sintesis ejecutiva",
        "reading": "Las principales senales son: publico joven-adulto, llegada digital, recomendacion interpersonal y oportunidad de fidelizacion.",
    },
}


def pct(n: int, base_n: int) -> float:
    return (n / base_n * 100) if base_n else 0.0


def pct_s(n: int, base_n: int, digits: int = 1) -> str:
    return f"{pct(n, base_n):.{digits}f}%"


def wrap_label(label: str, width: int = 32) -> str:
    label = polish_text(label)
    return "\n".join(textwrap.wrap(label, width=width, break_long_words=False)) or label


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)).replace("\\", "/")


def build_stats(records: list[dict]) -> dict[str, dict]:
    stats: dict[str, dict] = {}
    for key in base.CERRADAS_SIMPLES:
        counter = base.count_simple(records, key)
        items = base.ordered_items(key, counter)
        stats[key] = {"items": items, "base": sum(counter.values()), "multi": False}
    for key in base.CERRADAS_MULTI:
        counter, base_n = base.count_multi(records, key)
        stats[key] = {"items": counter.most_common(), "base": base_n, "multi": True}
    return stats


def items_dict(stats: dict, key: str) -> dict[str, int]:
    return dict(stats[key]["items"])


def top_item(stats: dict, key: str) -> tuple[str, int, int]:
    items = stats[key]["items"]
    base_n = stats[key]["base"]
    if not items:
        return "sin datos", 0, base_n
    label, value = max(items, key=lambda item: item[1])
    return label, value, base_n


def young_adult_count(stats: dict) -> int:
    d = items_dict(stats, "rango_edad")
    return d.get("18 a 24", 0) + d.get("25 a 34", 0) + d.get("35 a 44", 0)


def no_caba_count(stats: dict) -> int:
    d = items_dict(stats, "donde_vivis")
    total = stats["donde_vivis"]["base"]
    return total - d.get("CABA", 0)


def style_axes(ax) -> None:
    ax.set_facecolor("white")
    for side in ["top", "right", "bottom"]:
        ax.spines[side].set_visible(False)
    ax.spines["left"].set_color(LINE)
    ax.tick_params(axis="x", length=0, labelbottom=False)
    ax.tick_params(axis="y", labelsize=9.5, colors=INK)


def save_fig(fig, filename: str) -> str:
    GRAF_DG_DIR.mkdir(parents=True, exist_ok=True)
    out = GRAF_DG_DIR / filename
    fig.savefig(out, dpi=190, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return out.name


def hbar_chart(
    key: str,
    items: list[tuple[str, int]],
    base_n: int,
    title: str,
    subtitle: str,
    filename: str,
    accent_labels: set[str] | None = None,
    multi: bool = False,
    color: str = BLUE,
) -> str:
    accent_labels = accent_labels or set()
    items = list(reversed(items))
    labels = [wrap_label(label, 34) for label, _ in items]
    values = [value for _, value in items]
    colors_ = [ORANGE if label in accent_labels else color for label, _ in items]
    fig, ax = plt.subplots(figsize=(8.8, max(3.3, 0.55 * len(items) + 1.8)))
    ax.barh(labels, values, color=colors_, height=0.62)
    style_axes(ax)
    max_v = max(values) if values else 1
    for i, value in enumerate(values):
        ax.text(value + max_v * 0.018, i, f"{value} ({pct_s(value, base_n, 0)})",
                va="center", fontsize=9.2, color=INK, fontweight="bold")
    ax.set_xlim(0, max_v * 1.25)
    ax.set_title(polish_text(title), loc="left", fontsize=15, color=INK, fontweight="bold", pad=16)
    ax.text(0, 1.01, polish_text(subtitle), transform=ax.transAxes, fontsize=9.5, color=GREY, va="bottom")
    note = f"Base: n={base_n}" + (" · multi-respuesta (suma >100%)" if multi else "")
    fig.text(0.02, 0.02, polish_text(f"{note} · Muestra exploratoria, no representativa"), fontsize=8, color=GREY)
    fig.tight_layout(rect=[0, 0.06, 1, 0.92])
    return save_fig(fig, filename)


def stacked_100(
    items: list[tuple[str, int]],
    base_n: int,
    title: str,
    subtitle: str,
    filename: str,
    colors_: list[str],
) -> str:
    fig, ax = plt.subplots(figsize=(8.8, 2.6))
    left = 0.0
    for i, (label, value) in enumerate(items):
        width = pct(value, base_n)
        ax.barh([0], [width], left=left, color=colors_[i % len(colors_)], height=0.44)
        if width >= 8:
            ax.text(left + width / 2, 0, f"{polish_text(label)}\n{width:.0f}%", ha="center", va="center",
                    fontsize=8.8, color="white", fontweight="bold")
        left += width
    ax.set_xlim(0, 100)
    ax.set_ylim(-0.55, 0.55)
    ax.axis("off")
    ax.set_title(polish_text(title), loc="left", fontsize=15, color=INK, fontweight="bold", pad=16)
    ax.text(0, 0.88, polish_text(subtitle), transform=ax.transAxes, fontsize=9.5, color=GREY)
    fig.text(0.02, 0.07, polish_text(f"Base: n={base_n} · Muestra exploratoria, no representativa"), fontsize=8, color=GREY)
    fig.tight_layout(rect=[0, 0.1, 1, 0.92])
    return save_fig(fig, filename)


def donut_chart(
    items: list[tuple[str, int]],
    base_n: int,
    title: str,
    subtitle: str,
    filename: str,
    colors_: list[str],
    center_label: str,
) -> str:
    labels = [label for label, _ in items]
    values = [value for _, value in items]
    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    wedges, _ = ax.pie(
        values,
        startangle=90,
        counterclock=False,
        colors=colors_[:len(values)],
        wedgeprops={"width": 0.38, "edgecolor": "white", "linewidth": 2},
    )
    ax.text(0, 0.04, center_label, ha="center", va="center", fontsize=19, color=INK, fontweight="bold")
    ax.text(0, -0.17, f"n={base_n}", ha="center", va="center", fontsize=9, color=GREY)
    legend_labels = [polish_text(f"{label}: {value} ({pct_s(value, base_n, 0)})") for label, value in items]
    ax.legend(wedges, legend_labels, loc="center left", bbox_to_anchor=(1.0, 0.5),
              frameon=False, fontsize=9.2)
    ax.set_title(polish_text(title), loc="left", fontsize=15, color=INK, fontweight="bold", pad=16)
    fig.text(0.02, 0.04, polish_text(subtitle + " · Muestra exploratoria, no representativa"), fontsize=8, color=GREY)
    fig.tight_layout(rect=[0, 0.07, 0.95, 0.95])
    return save_fig(fig, filename)


def draw_kpi_cards(stats: dict, n_total: int) -> str:
    edad, edad_n, edad_base = top_item(stats, "rango_edad")
    caba = items_dict(stats, "donde_vivis").get("CABA", 0)
    instagram = items_dict(stats, "como_se_entero").get("Instagram", 0)
    acepta = items_dict(stats, "acepta_contacto").get("Si, acepto", 0)
    acepta_base = stats["acepta_contacto"]["base"]
    cards = [
        ("79", "respuestas\nanalizadas", "Base exploratoria"),
        (edad, "principal rango\netario", f"{edad_n}/{edad_base} respuestas"),
        (pct_s(caba, n_total, 0), "reside en CABA", f"{caba}/{n_total} respuestas"),
        (pct_s(instagram, n_total, 0), "menciono\nInstagram", f"{instagram}/{n_total} respuestas"),
        (pct_s(acepta, acepta_base, 0), "acepta recibir\ninformacion", f"{acepta}/{acepta_base} respuestas validas"),
    ]
    fig, axes = plt.subplots(1, 5, figsize=(12.8, 3.1))
    for i, (ax, (value, label, note)) in enumerate(zip(axes, cards)):
        ax.axis("off")
        face = INK if i == 0 else "white"
        edge = INK if i == 0 else LINE
        val_color = ORANGE if i == 0 else INK
        lab_color = "white" if i == 0 else BLUE_DARK
        note_color = "#E7EEF5" if i == 0 else GREY
        ax.add_patch(FancyBboxPatch(
            (0.03, 0.08), 0.94, 0.84,
            boxstyle="round,pad=0.018,rounding_size=0.035",
            transform=ax.transAxes,
            facecolor=face,
            edgecolor=edge,
            linewidth=1.2,
        ))
        ax.text(0.5, 0.63, value, ha="center", va="center", fontsize=20, color=val_color, fontweight="bold")
        ax.text(0.5, 0.39, polish_text(label), ha="center", va="center", fontsize=9.5, color=lab_color, fontweight="bold")
        ax.text(0.5, 0.18, polish_text(note), ha="center", va="center", fontsize=7.5, color=note_color)
    fig.suptitle(polish_text("Cafecito BA en tu barrio - indicadores de la muestra"), x=0.035, ha="left",
                 fontsize=15, fontweight="bold", color=INK)
    fig.text(0.035, 0.03, polish_text("Fuente: formulario Cafecito · no incluye datos personales"), fontsize=8, color=GREY)
    fig.tight_layout(rect=[0, 0.08, 1, 0.88])
    return save_fig(fig, GRAPH_META["kpi_cards"]["file"])


def draw_matriz() -> str:
    rows = [
        ("Edad y genero", "Ajustar tono y segmentacion de comunicacion", "No extrapolar al total del evento"),
        ("Procedencia macro", "Evaluar alcance territorial de la convocatoria", "No publicar barrio libre granular"),
        ("Primera vez", "Separar captacion nueva y fidelizacion", "Autodeclarado"),
        ("Con quien vino", "Pensar servicios para planes sociales/familiares", "No mide tamano real del grupo"),
        ("Canal de llegada", "Priorizar pauta, redes y recomendacion", "Multi-respuesta"),
        ("Intereses futuros", "Orientar programacion tematica", "Senales, no demanda representativa"),
    ]
    fig, ax = plt.subplots(figsize=(11.5, 5.2))
    ax.axis("off")
    ax.set_title(polish_text("De pregunta a decision de gestion"), loc="left", fontsize=16, color=INK, fontweight="bold", pad=12)
    col_x = [0.03, 0.31, 0.72]
    headers = ["Pregunta", "Decision que habilita", "Limite de lectura"]
    for x, h in zip(col_x, headers):
        ax.text(x, 0.88, polish_text(h), transform=ax.transAxes, fontsize=10.2, color=INK, fontweight="bold")
    y = 0.78
    for i, (q, decision, limitacion) in enumerate(rows):
        bg = "#F6F8FA" if i % 2 == 0 else "white"
        ax.add_patch(Rectangle((0.02, y - 0.055), 0.95, 0.09, transform=ax.transAxes,
                               facecolor=bg, edgecolor=LINE, linewidth=0.5))
        ax.text(col_x[0], y, polish_text(q), transform=ax.transAxes, fontsize=9.5, color=BLUE_DARK, fontweight="bold", va="center")
        ax.text(col_x[1], y, textwrap.fill(polish_text(decision), 42), transform=ax.transAxes, fontsize=9.0, color=INK, va="center")
        ax.text(col_x[2], y, textwrap.fill(polish_text(limitacion), 32), transform=ax.transAxes, fontsize=9.0, color=GREY, va="center")
        y -= 0.105
    fig.text(0.03, 0.04, polish_text("Lectura: cada pregunta debe alimentar una decision concreta y una advertencia metodologica visible."),
             fontsize=8.5, color=GREY)
    fig.tight_layout()
    return save_fig(fig, GRAPH_META["matriz"]["file"])


def draw_sintesis(stats: dict, n_total: int) -> str:
    caba = items_dict(stats, "donde_vivis").get("CABA", 0)
    instagram = items_dict(stats, "como_se_entero").get("Instagram", 0)
    amigos = items_dict(stats, "como_se_entero").get("Por amigos, familia o conocidos", 0)
    interes = items_dict(stats, "que_intereso").get("Probar café / cafeterías", 0)
    vino = items_dict(stats, "eventos_futuros").get("Vino", 0)
    bullets = [
        f"{young_adult_count(stats)}/{n_total} respuestas estan entre 18 y 44 anos.",
        f"{caba}/{n_total} declaran residir en CABA.",
        f"Instagram ({instagram}/{n_total}) y recomendacion interpersonal ({amigos}/{n_total}) son los canales mas fuertes.",
        f"Probar cafe/cafeterias ({interes}/{n_total}) fue el atractivo principal.",
        f"Vino ({vino}/{n_total}) lidera intereses futuros; lectura multi-respuesta.",
    ]
    fig, ax = plt.subplots(figsize=(10.8, 5.3))
    ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 1, 1, transform=ax.transAxes, facecolor=BG, edgecolor="none"))
    ax.text(0.04, 0.88, polish_text("Sintesis ejecutiva"), transform=ax.transAxes, fontsize=18, color=INK, fontweight="bold")
    ax.text(0.04, 0.80, polish_text("Cinco senales iniciales para planificar nuevas mediciones y acciones."),
            transform=ax.transAxes, fontsize=10, color=GREY)
    y = 0.66
    for i, bullet in enumerate(bullets, 1):
        ax.add_patch(FancyBboxPatch((0.04, y - 0.045), 0.90, 0.075,
                                    boxstyle="round,pad=0.012,rounding_size=0.02",
                                    transform=ax.transAxes, facecolor="white", edgecolor=LINE))
        ax.text(0.07, y - 0.005, str(i), transform=ax.transAxes, ha="center", va="center",
                fontsize=11, color="white", fontweight="bold",
                bbox=dict(boxstyle="circle,pad=0.33", facecolor=ORANGE, edgecolor=ORANGE))
        ax.text(0.12, y - 0.005, polish_text(bullet), transform=ax.transAxes, fontsize=10.3, color=INK, va="center")
        y -= 0.12
    ax.text(0.04, 0.08, polish_text("Nota: resultados exploratorios, sin representatividad estadistica."),
            transform=ax.transAxes, fontsize=8.8, color=GREY)
    fig.tight_layout()
    return save_fig(fig, GRAPH_META["sintesis"]["file"])


def generate_datagastro_charts(stats: dict, n_total: int) -> list[str]:
    generated: list[str] = []
    generated.append(draw_kpi_cards(stats, n_total))

    edad_items = stats["rango_edad"]["items"]
    generated.append(hbar_chart(
        "rango_edad", edad_items, stats["rango_edad"]["base"],
        "Rango de edad de las personas encuestadas",
        "Foco de lectura: concentracion en 25-34 y bloque 18-44.",
        GRAPH_META["edad"]["file"],
        accent_labels={"25 a 34", "18 a 24", "35 a 44"},
        color=BLUE,
    ))

    generated.append(stacked_100(
        stats["genero"]["items"], stats["genero"]["base"],
        "Genero declarado",
        "Dato autodeclarado. No se proyecta al total del publico del evento.",
        GRAPH_META["genero"]["file"],
        [INK, ORANGE, GREY],
    ))

    caba = items_dict(stats, "donde_vivis").get("CABA", 0)
    no_caba = no_caba_count(stats)
    generated.append(donut_chart(
        [("CABA", caba), ("No CABA", no_caba)], stats["donde_vivis"]["base"],
        "Procedencia macro",
        "Agrupacion macro para proteger granularidad territorial.",
        GRAPH_META["procedencia"]["file"],
        [BLUE, WARM],
        center_label=f"{pct_s(caba, stats['donde_vivis']['base'], 0)}\nCABA",
    ))

    generated.append(stacked_100(
        stats["primera_vez"]["items"], stats["primera_vez"]["base"],
        "Primera vez vs asistencia previa",
        "Permite distinguir captacion nueva y publico recurrente.",
        GRAPH_META["primera_vez"]["file"],
        [INK, ORANGE, GREY],
    ))

    generated.append(donut_chart(
        stats["con_quien"]["items"], stats["con_quien"]["base"],
        "Composicion declarada del plan",
        "Lectura de dinamica social de asistencia.",
        GRAPH_META["con_quien"]["file"],
        [INK, ORANGE, BLUE, WARM, GREY],
        center_label="plan\nsocial",
    ))

    generated.append(hbar_chart(
        "como_se_entero", stats["como_se_entero"]["items"], stats["como_se_entero"]["base"],
        "Como se enteraron del evento",
        "Instagram lidera; la recomendacion interpersonal queda unificada como categoria.",
        GRAPH_META["canal_llegada"]["file"],
        accent_labels={"Instagram", "Por amigos, familia o conocidos"},
        multi=True,
        color=BLUE,
    ))

    generated.append(hbar_chart(
        "que_intereso", stats["que_intereso"]["items"], stats["que_intereso"]["base"],
        "Que fue lo que mas intereso",
        "El atractivo gastronomico convive con la logica de salida/paseo.",
        GRAPH_META["interes"]["file"],
        accent_labels={"Probar café / cafeterías", "Pasear o hacer una salida"},
        color=COFFEE,
    ))

    generated.append(hbar_chart(
        "eventos_futuros", stats["eventos_futuros"]["items"][:12], stats["eventos_futuros"]["base"],
        "Eventos gastronomicos de interes futuro",
        "Multi-respuesta: leer como senales iniciales, no como ranking representativo.",
        GRAPH_META["eventos_futuros"]["file"],
        accent_labels={"Vino", "Pasteleria", "Food trucks", "Café", "Ferias y mercados"},
        multi=True,
        color=BLUE,
    ))

    generated.append(donut_chart(
        stats["acepta_contacto"]["items"], stats["acepta_contacto"]["base"],
        "Aceptacion para recibir informacion",
        "Oportunidad de comunicacion futura sin publicar correos.",
        GRAPH_META["contacto"]["file"],
        [GREEN, GREY],
        center_label=pct_s(items_dict(stats, "acepta_contacto").get("Si, acepto", 0),
                           stats["acepta_contacto"]["base"], 0),
    ))

    generated.append(draw_matriz())
    generated.append(draw_sintesis(stats, n_total))
    return generated


def list_counts(stats: dict, key: str, limit: int | None = None) -> list[str]:
    items = stats[key]["items"][:limit] if limit else stats[key]["items"]
    base_n = stats[key]["base"]
    return [f"- **{label}**: {value} ({pct_s(value, base_n)})" for label, value in items]


def question_table_rows(stats: dict, n_total: int, con_correo: int) -> list[list[str]]:
    d_contacto = items_dict(stats, "acepta_contacto")
    d_edad = items_dict(stats, "rango_edad")
    d_genero = items_dict(stats, "genero")
    d_vivis = items_dict(stats, "donde_vivis")
    d_primera = items_dict(stats, "primera_vez")
    d_quien = items_dict(stats, "con_quien")
    d_canal = items_dict(stats, "como_se_entero")
    d_interes = items_dict(stats, "que_intereso")
    d_futuro = items_dict(stats, "eventos_futuros")
    contacto_base = stats["acepta_contacto"]["base"]
    return [
        [
            "Correo electronico",
            "Identificar respuestas y habilitar una eventual base de contacto con consentimiento.",
            f"{con_correo}/{n_total} respuestas tenian correo.",
            "Sirve para gestion de contacto solo en circuito interno y con consentimiento.",
            "Dato personal directo: no se publica ni se analiza como variable publica.",
        ],
        [
            "Consentimiento de contacto",
            "Saber si la persona acepta recibir novedades gastronomicas.",
            f"{d_contacto.get('Si, acepto', 0)}/{contacto_base} respuestas validas aceptan.",
            "Hay oportunidad para construir un canal de comunicacion futura.",
            "Mide intencion declarada; no equivale a contacto efectivo.",
        ],
        [
            "Edad",
            "Orientar tono, canales y propuestas segun tramo etario.",
            f"25 a 34 lidera con {d_edad.get('25 a 34', 0)}/{n_total}; 18 a 44 suma {young_adult_count(stats)}/{n_total}.",
            "Senala mayor presencia joven-adulta entre respondentes.",
            "No representa la estructura etaria total del evento.",
        ],
        [
            "Genero",
            "Conocer composicion declarada de la muestra.",
            f"Mujer: {d_genero.get('Mujer', 0)}/{n_total}; Varon: {d_genero.get('Varon', 0)}/{n_total}.",
            "Permite revisar si la comunicacion llega de forma equilibrada.",
            "Dato autodeclarado; no sobregeneralizar por muestra chica.",
        ],
        [
            "Procedencia macro",
            "Entender alcance territorial del evento.",
            f"CABA: {d_vivis.get('CABA', 0)}/{n_total}; no CABA: {no_caba_count(stats)}/{n_total}.",
            "Ayuda a evaluar convocatoria local y llegada metropolitana.",
            "No reemplaza analisis territorial fino.",
        ],
        [
            "Barrio/localidad",
            "Capturar detalle territorial potencial.",
            "Se recolecto como texto libre, pero no se publica granularmente.",
            "Puede servir internamente para revisar zonas de captacion si se agregan umbrales.",
            "Texto libre potencialmente identificable; no listar valores individuales.",
        ],
        [
            "Primera vez",
            "Distinguir publico nuevo de asistentes recurrentes.",
            f"Ya habia participado: {d_primera.get('No, ya participé de otros eventos', 0)}/{n_total}; primera vez: {d_primera.get('Si, es la primera vez', 0)}/{n_total}.",
            "Permite pensar captacion y fidelizacion al mismo tiempo.",
            "Autodeclarado; no verifica historial real.",
        ],
        [
            "Con quien vino",
            "Entender tipo de plan y dinamica de asistencia.",
            f"En pareja: {d_quien.get('En pareja', 0)}; amigos/as: {d_quien.get('Con amigos/as', 0)}; familia: {d_quien.get('Con familia', 0)}.",
            "Orienta servicios, programacion y espacios para planes sociales/familiares.",
            "No mide tamano real del grupo ni consumo.",
        ],
        [
            "Como se entero",
            "Evaluar canales de difusion.",
            f"Instagram: {d_canal.get('Instagram', 0)}/{n_total}; amigos/familia/conocidos: {d_canal.get('Por amigos, familia o conocidos', 0)}/{n_total}.",
            "Refuerza rol de redes e indica valor de recomendacion interpersonal.",
            "Multi-respuesta: porcentajes no son excluyentes.",
        ],
        [
            "Que le intereso",
            "Identificar el atractivo principal del evento.",
            f"Probar cafe/cafeterias: {d_interes.get('Probar café / cafeterías', 0)}/{n_total}; salida/paseo: {d_interes.get('Pasear o hacer una salida', 0)}/{n_total}.",
            "Ayuda a equilibrar propuesta gastronomica y experiencia de paseo.",
            "Una opcion por persona; simplifica motivaciones multiples.",
        ],
        [
            "Eventos futuros",
            "Explorar intereses para nuevas propuestas.",
            f"Vino: {d_futuro.get('Vino', 0)}; pasteleria: {d_futuro.get('Pasteleria', 0)}; food trucks: {d_futuro.get('Food trucks', 0)}; cafe: {d_futuro.get('Café', 0)}.",
            "Sirve como insumo inicial para programacion tematica.",
            "Multi-respuesta y muestra chica: no es demanda representativa.",
        ],
    ]


def build_executive_conclusions(stats: dict, n_total: int) -> list[str]:
    d_canal = items_dict(stats, "como_se_entero")
    d_interes = items_dict(stats, "que_intereso")
    d_futuro = items_dict(stats, "eventos_futuros")
    d_contacto = items_dict(stats, "acepta_contacto")
    contacto_base = stats["acepta_contacto"]["base"]
    return [
        f"La muestra tiene una concentracion joven-adulta: {young_adult_count(stats)}/{n_total} respuestas estan entre 18 y 44 anos, con pico en 25 a 34.",
        f"La llegada combina canal digital e interpersonal: Instagram suma {d_canal.get('Instagram', 0)}/{n_total} menciones y la recomendacion de amigos, familia o conocidos {d_canal.get('Por amigos, familia o conocidos', 0)}/{n_total}.",
        f"El interes principal fue probar cafe/cafeterias ({d_interes.get('Probar café / cafeterías', 0)}/{n_total}), seguido por salir o pasear ({d_interes.get('Pasear o hacer una salida', 0)}/{n_total}).",
        f"Los intereses futuros abren lineas de programacion: vino ({d_futuro.get('Vino', 0)}), pasteleria ({d_futuro.get('Pasteleria', 0)}), food trucks ({d_futuro.get('Food trucks', 0)}), cafe ({d_futuro.get('Café', 0)}) y ferias/mercados ({d_futuro.get('Ferias y mercados', 0)}).",
        f"La aceptacion de contacto ({d_contacto.get('Si, acepto', 0)}/{contacto_base} respuestas validas) es una oportunidad de fidelizacion, siempre sin publicar correos.",
    ]


def build_recommendations() -> list[str]:
    return [
        "Comunicación: sostener Instagram como canal prioritario y probar piezas que incentiven la recomendacion interpersonal.",
        "Programación: usar cafe, pasteleria, vino, food trucks y ferias/mercados como primeras hipotesis para futuras acciones.",
        "Formulario: mantener preguntas con decision asociada y simplificar las que generen baja utilidad o friccion.",
        "Operativo de campo: planificar puntos, horarios y dispositivos para aumentar muestra y reducir sesgo de captacion.",
        "Calidad de datos: documentar opciones canonicas multi-respuesta y evitar comas internas sin tratamiento.",
        "Privacidad: mantener correos y barrio/localidad fuera de outputs publicos; trabajar solo con agregados.",
    ]


def build_cross_readings(records: list[dict]) -> list[str]:
    for r in records:
        parts = base.split_multi(r.get("como_se_entero", ""), "como_se_entero")
        r["canal_principal"] = parts[0] if parts else ""
        r["residencia_grupo"] = "CABA" if r.get("donde_vivis") == "CABA" else "No CABA"

    first_contact = base.crosstab(records, "primera_vez", "acepta_contacto", min_cell_base=8)
    residence_interest = base.crosstab(records, "residencia_grupo", "que_intereso", min_cell_base=8)
    age_channel = base.crosstab(records, "rango_edad", "canal_principal", min_cell_base=8)
    readings = []

    if first_contact:
        table, base_n = first_contact
        first_yes = table.get("Si, es la primera vez", {}).get("Si, acepto", 0)
        recurrent_yes = table.get("No, ya participé de otros eventos", {}).get("Si, acepto", 0)
        readings.append(
            f"Primera vez x contacto (base {base_n}): tanto el publico nuevo ({first_yes} aceptaciones) "
            f"como el recurrente ({recurrent_yes} aceptaciones) aportan potencial de comunicacion futura. "
            "La lectura es orientativa porque no verifica comportamiento posterior."
        )
    if residence_interest:
        table, base_n = residence_interest
        caba_top = table.get("CABA", Counter()).most_common(1)
        no_caba_top = table.get("No CABA", Counter()).most_common(1)
        if caba_top and no_caba_top:
            readings.append(
                f"Procedencia x atractivo (base {base_n}): en CABA predomina '{caba_top[0][0]}' "
                f"({caba_top[0][1]}), y fuera de CABA '{no_caba_top[0][0]}' ({no_caba_top[0][1]}). "
                "No se fuerza una diferencia territorial por el tamaño de celdas."
            )
    if age_channel:
        table, base_n = age_channel
        age_25_34 = table.get("25 a 34", Counter())
        if age_25_34:
            top = age_25_34.most_common(1)[0]
            readings.append(
                f"Edad x canal principal (base {base_n}): en 25 a 34 el canal principal mas frecuente fue "
                f"'{top[0]}' ({top[1]}). La señal ayuda a ajustar comunicacion, no a segmentar de forma concluyente."
            )
    return readings[:3]


def write_markdown_report(records: list[dict], stats: dict, generated: list[str], con_correo: int) -> None:
    n_total = len(records)
    conclusions = build_executive_conclusions(stats, n_total)
    recommendations = build_recommendations()
    question_rows = question_table_rows(stats, n_total, con_correo)
    cross_readings = build_cross_readings([dict(r) for r in records])
    lines: list[str] = [
        "# DataGastro - Cafecito BA en tu barrio",
        "",
        "## Informe exploratorio de respuestas del formulario",
        "",
        "**Nota metodológica:** muestra exploratoria, no representativa del público total del evento. No se publican correos, marcas temporales, barrios/localidades libres ni identificadores personales.",
        "",
        "## 1. Resumen ejecutivo",
        "",
        f"El relevamiento analizó **{n_total} respuestas** del formulario aplicado en Cafecito BA en tu barrio. El objetivo fue conocer mejor a quienes respondieron, validar el instrumento de medición y generar insumos para comunicación, programación y próximos operativos de campo.",
        "",
        "### Indicadores principales",
        "",
        f"- Respuestas analizadas: **{n_total}**.",
        f"- Principal rango etario: **25 a 34** ({items_dict(stats, 'rango_edad').get('25 a 34', 0)}/{n_total}).",
        f"- Procedencia principal: **CABA** ({items_dict(stats, 'donde_vivis').get('CABA', 0)}/{n_total}).",
        f"- Canal principal mencionado: **Instagram** ({items_dict(stats, 'como_se_entero').get('Instagram', 0)}/{n_total}).",
        f"- Acepta recibir información: **{items_dict(stats, 'acepta_contacto').get('Si, acepto', 0)}/{stats['acepta_contacto']['base']}** respuestas válidas.",
        "",
        "### Conclusiones ejecutivas",
        "",
        *(f"- {c}" for c in conclusions[:4]),
        "",
        "## 2. Objetivo y alcance",
        "",
        "El formulario buscó relevar perfil básico, procedencia, vínculo previo con eventos gastronómicos, canales de llegada, motivaciones e intereses futuros. También permitió validar qué preguntas generan información útil para gestión y cuáles requieren ajustes.",
        "",
        "La muestra debe leerse como una primera aproximación exploratoria: sirve para detectar señales y mejorar próximos relevamientos, pero no permite inferencias representativas sobre la totalidad del público del evento.",
        "",
        "## 3. Perfil de la muestra",
        "",
        "### Edad",
        "",
        *list_counts(stats, "rango_edad"),
        "",
        f"Lectura: el bloque 18 a 44 concentra {young_adult_count(stats)}/{n_total} respuestas. La señal ayuda a ajustar tono y canales, sin afirmar que ese sea el perfil completo del evento.",
        "",
        "### Género",
        "",
        *list_counts(stats, "genero"),
        "",
        "Lectura: predominan respuestas de mujeres, pero se trata de dato declarado en una muestra chica. No corresponde extrapolarlo al público total.",
        "",
        "### Procedencia macro",
        "",
        *list_counts(stats, "donde_vivis"),
        "",
        "Lectura: CABA concentra la mayoría de respuestas, con llegada también desde GBA y Provincia. El barrio/localidad libre no se publica por privacidad y calidad del dato.",
        "",
        "## 4. Vínculo con el evento",
        "",
        "### Primera vez vs asistencia previa",
        "",
        *list_counts(stats, "primera_vez"),
        "",
        "### Con quién vino",
        "",
        *list_counts(stats, "con_quien"),
        "",
        "Lectura: pareja, amigos y familia estructuran la mayor parte de la asistencia declarada. La propuesta funciona como plan social y familiar, además de experiencia gastronómica.",
        "",
        "## 5. Canales de llegada",
        "",
        "La pregunta es multi-respuesta. La categoría **Por amigos, familia o conocidos** se conserva unificada aunque tenga coma interna.",
        "",
        *list_counts(stats, "como_se_entero"),
        "",
        "Lectura: Instagram opera como canal principal de difusión y la recomendación interpersonal aparece como segundo motor. El paso por la zona también muestra valor del emplazamiento y la visibilidad territorial.",
        "",
        "## 6. Motivaciones e intereses",
        "",
        "### Qué fue lo que más interesó",
        "",
        *list_counts(stats, "que_intereso"),
        "",
        "Lectura: el atractivo más fuerte fue probar café/cafeterías, seguido por pasear o hacer una salida. La programación debe sostener el corazón gastronómico sin perder la dimensión de experiencia urbana.",
        "",
        "### Eventos gastronómicos de interés futuro",
        "",
        *list_counts(stats, "eventos_futuros", limit=12),
        "",
        "Lectura: las respuestas son multi-respuesta y no excluyentes. Funcionan como señales iniciales para programación futura, no como demanda representativa.",
        "",
        "## 7. Lectura pregunta por pregunta",
        "",
        "| Pregunta | Objetivo original | Resultado observado | Lectura de gestión | Limitación |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in question_rows:
        safe = [cell.replace("|", "/") for cell in row]
        lines.append("| " + " | ".join(safe) + " |")

    lines.extend([
        "",
        "## 8. Cruces exploratorios",
        "",
        "Los cruces se leen como señales preliminares. No se fuerzan conclusiones cuando hay celdas chicas.",
        "",
        *(f"- {reading}" for reading in cross_readings),
        "",
        "## 9. Aprendizajes sobre el formulario",
        "",
        "- Funcionaron bien las preguntas de edad, procedencia macro, primera vez, con quién vino, canal de llegada, atractivo principal e intereses futuros.",
        "- La pregunta de correo debe quedar separada de outputs públicos: sirve para contacto interno con consentimiento, no para análisis publicable.",
        "- Barrio/localidad aporta potencial territorial, pero requiere agregación y umbrales antes de publicarse.",
        "- Las multi-respuesta necesitan opciones canónicas documentadas para no partir categorías con coma interna.",
        "- Conviene revisar opciones con baja frecuencia y campos abiertos para reducir fricción y mejorar calidad.",
        "",
        "## 10. Conclusiones finales",
        "",
        *(f"{i}. {c}" for i, c in enumerate(conclusions, 1)),
        "",
        "## 11. Recomendaciones",
        "",
        *(f"{i}. {r}" for i, r in enumerate(recommendations, 1)),
        "",
        "## 12. Anexo metodológico",
        "",
        f"- Fuente principal: `{rel(base.XLSX)}`.",
        f"- Respuestas analizadas: {n_total}.",
        "- Tratamiento de privacidad: se excluyen correo, marca temporal y barrio/localidad libre de outputs públicos.",
        "- Tratamiento multi-respuesta: se desagrega por opción y se protege `Por amigos, familia o conocidos` como categoría única.",
        "- Los porcentajes de multi-respuesta se calculan sobre respondentes y pueden sumar más de 100%.",
        f"- Gráficos DataGastro: `{rel(GRAF_DG_DIR)}`.",
        f"- PDF DataGastro: `{rel(PDF_REPORT)}` y copia final en `{rel(FINAL_PDF)}`.",
        "",
        "## Gráficos generados",
        "",
        *(f"- `{rel(GRAF_DG_DIR / name)}`" for name in generated),
        "",
    ])
    REPORT_MD.write_text(polish_text("\n".join(lines)), encoding="utf-8")


def update_readme() -> None:
    text = README_MD.read_text(encoding="utf-8") if README_MD.exists() else "# Cafecito\n"
    block = """

## Versión DataGastro

Para regenerar la versión visual/narrativa DataGastro:

```powershell
python scripts/cafecito/generar_informe_datagastro.py
```

Outputs principales:

- Gráficos DataGastro: `outputs/cafecito/graficos_datagastro/`
- PDF institucional: `outputs/cafecito/INFORME_CAFECITO_DATAGASTRO.pdf`
- Copia final: `Cafesito/final/INFORME_CAFECITO_DATAGASTRO.pdf`
- Markdown textual completo: `docs/cafecito/INFORME_CAFECITO_EXPLORATORIO.md`
- DOCX resumido con gráficos: `outputs/cafecito/INFORME_CAFECITO_GRAFICOS.docx`
"""
    if "## Versión DataGastro" not in text:
        text = text.rstrip() + "\n\n" + block.lstrip()
    README_MD.write_text(text, encoding="utf-8")


def docx_paragraph(text: str = "", size: int = 22, bold: bool = False, spacing: int = 140) -> str:
    text = polish_text(text)
    b = "<w:b/>" if bold else ""
    return (
        f'<w:p><w:pPr><w:spacing w:after="{spacing}"/></w:pPr>'
        f"<w:r><w:rPr>{b}<w:sz w:val=\"{size}\"/></w:rPr>"
        f'<w:t xml:space="preserve">{xml_escape(text)}</w:t></w:r></w:p>'
    )


def docx_heading(text: str, level: int = 1) -> str:
    size = 34 if level == 1 else 27
    return docx_paragraph(text, size=size, bold=True, spacing=180)


def image_extent(path: Path) -> tuple[int, int]:
    emu_per_inch = 914400
    max_cx = int(6.2 * emu_per_inch)
    max_cy = int(4.2 * emu_per_inch)
    try:
        from PIL import Image as PILImage
        with PILImage.open(path) as im:
            width, height = im.size
    except Exception:
        return max_cx, int(3.0 * emu_per_inch)
    cx = max_cx
    cy = int(cx * height / width)
    if cy > max_cy:
        cy = max_cy
        cx = int(cy * width / height)
    return cx, cy


def docx_image(rid: str, name: str, docpr_id: int, cx: int, cy: int) -> str:
    return f"""
<w:p><w:r><w:drawing>
<wp:inline distT="0" distB="0" distL="0" distR="0">
<wp:extent cx="{cx}" cy="{cy}"/>
<wp:docPr id="{docpr_id}" name="{xml_escape(name)}"/>
<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
<pic:pic>
<pic:nvPicPr><pic:cNvPr id="0" name="{xml_escape(name)}"/><pic:cNvPicPr/></pic:nvPicPr>
<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>
<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"/></pic:spPr>
</pic:pic>
</a:graphicData></a:graphic>
</wp:inline>
</w:drawing></w:r></w:p>
"""


def write_docx_report(stats: dict, n_total: int, generated: list[str]) -> None:
    conclusions = build_executive_conclusions(stats, n_total)
    recommendations = build_recommendations()
    body: list[str] = []
    images: list[tuple[str, Path]] = []
    body.append(docx_heading("DataGastro - Cafecito BA en tu barrio", 1))
    body.append(docx_paragraph("Informe exploratorio de respuestas del formulario", size=25, bold=True))
    body.append(docx_paragraph(f"Respuestas analizadas: {n_total}. Muestra exploratoria, no representativa."))
    body.append(docx_paragraph("No incluye correos, nombres, telefonos, barrios/localidades libres ni identificadores personales."))
    body.append(docx_heading("Resumen ejecutivo", 2))
    for c in conclusions[:4]:
        body.append(docx_paragraph("- " + c))
    body.append(docx_heading("Graficos DataGastro", 2))
    for name in generated:
        if name not in {GRAPH_META[k]["file"] for k in GRAPH_META}:
            continue
        img = GRAF_DG_DIR / name
        meta = next(v for v in GRAPH_META.values() if v["file"] == name)
        body.append(docx_heading(meta["title"], 2))
        rid = f"rId{len(images) + 1}"
        media_name = f"image{len(images) + 1}.png"
        cx, cy = image_extent(img)
        body.append(docx_image(rid, img.name, len(images) + 1, cx, cy))
        body.append(docx_paragraph("Lectura: " + meta["reading"]))
        images.append((media_name, img))
    body.append(docx_heading("Recomendaciones", 2))
    for r in recommendations:
        body.append(docx_paragraph("- " + r))

    document_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
 xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
 xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
 xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">
<w:body>
{''.join(body)}
<w:sectPr><w:pgSz w:w="12240" w:h="15840"/><w:pgMar w:top="1440" w:right="1080" w:bottom="1440" w:left="1080"/></w:sectPr>
</w:body></w:document>"""

    rels_xml = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">']
    for i, (media_name, _) in enumerate(images, 1):
        rels_xml.append(
            f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/{media_name}"/>'
        )
    rels_xml.append("</Relationships>")

    content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Default Extension="png" ContentType="image/png"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""
    package_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""

    with zipfile.ZipFile(DOCX_REPORT, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", package_rels)
        zf.writestr("word/document.xml", document_xml)
        zf.writestr("word/_rels/document.xml.rels", "".join(rels_xml))
        for media_name, img in images:
            zf.write(img, f"word/media/{media_name}")


def pdf_styles() -> dict[str, ParagraphStyle]:
    base_styles = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("TitleDG", parent=base_styles["Title"], fontName="Helvetica-Bold",
                                fontSize=27, leading=32, textColor=colors.HexColor(INK), alignment=TA_LEFT),
        "subtitle": ParagraphStyle("SubtitleDG", parent=base_styles["Normal"], fontSize=13.5, leading=18,
                                   textColor=colors.HexColor(GREY)),
        "h1": ParagraphStyle("H1DG", parent=base_styles["Heading1"], fontName="Helvetica-Bold",
                             fontSize=17, leading=22, textColor=colors.HexColor(INK), spaceAfter=9),
        "h2": ParagraphStyle("H2DG", parent=base_styles["Heading2"], fontName="Helvetica-Bold",
                             fontSize=13, leading=16, textColor=colors.HexColor(BLUE_DARK), spaceAfter=6),
        "body": ParagraphStyle("BodyDG", parent=base_styles["BodyText"], fontSize=9.4, leading=13.2,
                               textColor=colors.HexColor("#263442"), spaceAfter=6),
        "small": ParagraphStyle("SmallDG", parent=base_styles["BodyText"], fontSize=7.6, leading=10.2,
                                textColor=colors.HexColor(GREY), spaceAfter=4),
        "card_num": ParagraphStyle("CardNumDG", parent=base_styles["Normal"], fontName="Helvetica-Bold",
                                   fontSize=16, leading=18, textColor=colors.HexColor(ORANGE), alignment=TA_CENTER),
        "card_lab": ParagraphStyle("CardLabDG", parent=base_styles["Normal"], fontName="Helvetica-Bold",
                                   fontSize=7.6, leading=9.0, textColor=colors.white, alignment=TA_CENTER),
        "center": ParagraphStyle("CenterDG", parent=base_styles["BodyText"], fontSize=9, leading=12,
                                 textColor=colors.HexColor("#263442"), alignment=TA_CENTER),
    }


def p(text: str, styles: dict, style: str = "body") -> Paragraph:
    return Paragraph(polish_text(text), styles[style])


def bullet_list(items: list[str], styles: dict) -> ListFlowable:
    return ListFlowable(
        [ListItem(p(item, styles, "body"), bulletColor=colors.HexColor(ORANGE)) for item in items],
        bulletType="bullet",
        leftIndent=12,
    )


def add_chart(story: list, name: str, styles: dict, width: float = 15.8 * cm) -> None:
    path = GRAF_DG_DIR / GRAPH_META[name]["file"]
    story.append(Paragraph(GRAPH_META[name]["title"], styles["h2"]))
    story.append(Image(str(path), width=width, height=width * 0.52))
    story.append(Paragraph("Lectura: " + GRAPH_META[name]["reading"], styles["small"]))
    story.append(Spacer(1, 0.2 * cm))


def kpi_table(stats: dict, n_total: int, styles: dict) -> Table:
    d = {
        "edad": items_dict(stats, "rango_edad").get("25 a 34", 0),
        "caba": items_dict(stats, "donde_vivis").get("CABA", 0),
        "instagram": items_dict(stats, "como_se_entero").get("Instagram", 0),
        "acepta": items_dict(stats, "acepta_contacto").get("Si, acepto", 0),
        "acepta_base": stats["acepta_contacto"]["base"],
    }
    cells = [
        [p("79", styles, "card_num"), p("respuestas<br/>analizadas", styles, "card_lab")],
        [p("25-34", styles, "card_num"), p(f"principal rango<br/>{d['edad']}/{n_total}", styles, "card_lab")],
        [p(pct_s(d["caba"], n_total, 0), styles, "card_num"), p("reside<br/>en CABA", styles, "card_lab")],
        [p(pct_s(d["instagram"], n_total, 0), styles, "card_num"), p("menciona<br/>Instagram", styles, "card_lab")],
        [p(pct_s(d["acepta"], d["acepta_base"], 0), styles, "card_num"), p("acepta recibir<br/>informacion", styles, "card_lab")],
    ]
    table_data = [[Table([[c[0]], [c[1]]], colWidths=[2.55 * cm], rowHeights=[0.7 * cm, 0.8 * cm]) for c in cells]]
    t = Table(table_data, colWidths=[3.0 * cm] * 5)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(INK)),
        ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor(INK)),
        ("INNERGRID", (0, 0), (-1, -1), 5, colors.white),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def question_pdf_table(rows: list[list[str]], styles: dict) -> Table:
    headers = ["Pregunta", "Objetivo", "Resultado", "Lectura", "Limitacion"]
    data = [[p(h, styles, "small") for h in headers]]
    for row in rows:
        data.append([p(cell, styles, "small") for cell in row])
    table = Table(data, colWidths=[2.6 * cm, 3.5 * cm, 3.4 * cm, 3.6 * cm, 3.2 * cm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(INK)),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor(LINE)),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7F9FB")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return table


def on_pdf_page(canvas, doc) -> None:
    canvas.saveState()
    width, height = A4
    canvas.setStrokeColor(colors.HexColor(LINE))
    canvas.line(1.45 * cm, 1.15 * cm, width - 1.45 * cm, 1.15 * cm)
    canvas.setFillColor(colors.HexColor(GREY))
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(1.45 * cm, 0.74 * cm, FOOTER)
    canvas.drawRightString(width - 1.45 * cm, 0.74 * cm, f"p. {doc.page}")
    canvas.restoreState()


def write_pdf_report(records: list[dict], stats: dict, con_correo: int) -> int:
    n_total = len(records)
    styles = pdf_styles()
    conclusions = build_executive_conclusions(stats, n_total)
    recommendations = build_recommendations()
    question_rows = question_table_rows(stats, n_total, con_correo)
    cross_readings = build_cross_readings([dict(r) for r in records])
    doc = SimpleDocTemplate(
        str(PDF_REPORT),
        pagesize=A4,
        rightMargin=1.55 * cm,
        leftMargin=1.55 * cm,
        topMargin=1.55 * cm,
        bottomMargin=1.45 * cm,
        title="DataGastro - Cafecito BA en tu barrio",
        author="DataGastro",
    )
    story: list = []

    story.append(Spacer(1, 1.1 * cm))
    story.append(p("DataGastro", styles, "subtitle"))
    story.append(p("Cafecito BA en tu barrio", styles, "title"))
    story.append(p("Informe exploratorio de respuestas del formulario", styles, "subtitle"))
    story.append(Spacer(1, 0.8 * cm))
    story.append(kpi_table(stats, n_total, styles))
    story.append(Spacer(1, 0.6 * cm))
    story.append(p("Muestra exploratoria, no representativa. No se publican correos, marcas temporales, barrios/localidades libres ni identificadores personales.", styles, "body"))
    story.append(p("Versión DataGastro - junio 2026", styles, "small"))
    story.append(PageBreak())

    story.append(p("1. Resumen ejecutivo", styles, "h1"))
    story.append(p(f"El formulario reunió {n_total} respuestas y permite identificar señales iniciales sobre perfil, canales de llegada, motivaciones e intereses futuros. La lectura es útil para gestión, pero no tiene diseño muestral representativo.", styles))
    story.append(bullet_list(conclusions[:4], styles))
    story.append(Spacer(1, 0.35 * cm))
    add_chart(story, "kpi_cards", styles)
    story.append(PageBreak())

    story.append(p("2. Objetivo y alcance", styles, "h1"))
    story.append(p("El objetivo fue conocer mejor a quienes respondieron, evaluar canales de comunicación, identificar intereses y validar el formulario como herramienta de próximos relevamientos gastronómicos.", styles))
    story.append(p("El relevamiento sirve porque transforma una acción puntual en aprendizaje operativo: qué preguntar, cómo captar, qué canales mirar y qué decisiones puede alimentar cada respuesta.", styles))
    story.append(p("Limitaciones: muestra chica, captación no probabilística, posibles sesgos por horario/punto de encuesta, respuestas autodeclaradas y preguntas multi-respuesta con porcentajes no aditivos.", styles))
    story.append(PageBreak())

    story.append(p("3. Perfil de la muestra", styles, "h1"))
    add_chart(story, "edad", styles)
    add_chart(story, "genero", styles)
    add_chart(story, "procedencia", styles)
    story.append(PageBreak())

    story.append(p("4. Vínculo con el evento", styles, "h1"))
    add_chart(story, "primera_vez", styles)
    add_chart(story, "con_quien", styles)
    story.append(PageBreak())

    story.append(p("5. Canales de llegada", styles, "h1"))
    story.append(p("La opción 'Por amigos, familia o conocidos' se procesa como una sola categoría. La lectura combina alcance digital, recomendación interpersonal y visibilidad territorial del evento.", styles))
    add_chart(story, "canal_llegada", styles)
    story.append(PageBreak())

    story.append(p("6. Motivaciones e intereses", styles, "h1"))
    add_chart(story, "interes", styles)
    add_chart(story, "eventos_futuros", styles)
    story.append(PageBreak())

    story.append(p("7. Lectura pregunta por pregunta", styles, "h1"))
    story.append(p("Cada pregunta se evalúa por su objetivo original, resultado observado, decisión que habilita y límite metodológico.", styles))
    story.append(question_pdf_table(question_rows, styles))
    story.append(PageBreak())

    story.append(p("8. Cruces exploratorios", styles, "h1"))
    story.append(p("Se priorizan lecturas textuales antes que tablas grandes. Los cruces orientan hipótesis, no conclusiones fuertes por segmento.", styles))
    story.append(bullet_list(cross_readings, styles))
    story.append(Spacer(1, 0.35 * cm))
    add_chart(story, "matriz", styles)
    story.append(PageBreak())

    story.append(p("9. Aprendizajes sobre el formulario", styles, "h1"))
    story.append(bullet_list([
        "Las preguntas cerradas generan lectura ejecutiva rápida y comparabilidad futura.",
        "Correo y consentimiento deben permanecer separados: el correo es dato personal; el consentimiento es indicador agregado.",
        "Barrio/localidad debe tratarse con umbrales o agregación para evitar identificación.",
        "Las preguntas multi-respuesta requieren opciones canónicas para evitar errores de partición.",
        "Conviene reducir campos abiertos si no hay un plan claro de codificación y uso.",
    ], styles))
    story.append(PageBreak())

    story.append(p("10. Conclusiones finales", styles, "h1"))
    story.append(bullet_list(conclusions, styles))
    story.append(Spacer(1, 0.35 * cm))
    add_chart(story, "sintesis", styles)
    story.append(PageBreak())

    story.append(p("11. Recomendaciones", styles, "h1"))
    story.append(bullet_list(recommendations, styles))
    story.append(Spacer(1, 0.3 * cm))
    add_chart(story, "contacto", styles)
    story.append(PageBreak())

    story.append(p("12. Anexo metodológico", styles, "h1"))
    story.append(bullet_list([
        f"Fuente principal: {rel(base.XLSX)}.",
        f"Respuestas analizadas: {n_total}.",
        f"Correo presente en {con_correo}/{n_total} respuestas, excluido de outputs publicos.",
        "Marca temporal y barrio/localidad libre se excluyen de outputs publicos.",
        "Las preguntas multi-respuesta se desagregan por opción; los porcentajes pueden sumar más de 100%.",
        "La categoría 'Por amigos, familia o conocidos' se protege como opción canónica con coma interna.",
        f"Gráficos DataGastro: {rel(GRAF_DG_DIR)}.",
    ], styles))

    doc.build(story, onFirstPage=on_pdf_page, onLaterPages=on_pdf_page)
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PDF_REPORT, FINAL_PDF)
    return len(story)


def main() -> int:
    # Regenera outputs base y conserva la reproducibilidad existente.
    base.DECISIONES.clear()
    base.main()

    records = base.read_xlsx(base.XLSX)
    n_total = len(records)
    con_correo = sum(1 for r in records if not base.is_blank(r.get("correo", "")))
    stats = build_stats(records)
    GRAF_DG_DIR.mkdir(parents=True, exist_ok=True)
    generated = generate_datagastro_charts(stats, n_total)
    write_markdown_report(records, stats, generated, con_correo)
    update_readme()
    write_docx_report(stats, n_total, generated)
    write_pdf_report(records, stats, con_correo)

    print("=" * 72)
    print("Informe Cafecito DataGastro")
    print(f"  Respuestas: {n_total}")
    print(f"  Graficos DataGastro: {len(generated)} -> {rel(GRAF_DG_DIR)}")
    print(f"  Markdown: {rel(REPORT_MD)}")
    print(f"  DOCX: {rel(DOCX_REPORT)}")
    print(f"  PDF: {rel(PDF_REPORT)}")
    print(f"  Copia final: {rel(FINAL_PDF)}")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
