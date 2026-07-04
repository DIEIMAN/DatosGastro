"""Genera la version visual V2 del informe Cafecito DataGastro.

Usa la mejora analitica ya generada, lee el XLSX original en modo solo
lectura y produce una nueva salida PDF sin sobrescribir la version anterior.
No publica correos, marcas temporales, barrios/localidades libres ni
respuestas individuales.

Uso:
    python scripts/cafecito/generar_informe_datagastro_v2.py
"""
from __future__ import annotations

import csv
import re
import shutil
import sys
import textwrap
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.image as mpimg  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.cafecito import analizar_cafecito as base  # noqa: E402
from scripts.cafecito import mejorar_analitica_cafecito as mejora  # noqa: E402

DOCS_DIR = REPO_ROOT / "docs" / "cafecito"
OUT_DIR = REPO_ROOT / "outputs" / "cafecito"
GRAF_DIR = OUT_DIR / "graficos_datagastro"
FINAL_DIR = REPO_ROOT / "Cafesito" / "final"

REPORT_MD = DOCS_DIR / "INFORME_CAFECITO_EXPLORATORIO.md"
README_MD = DOCS_DIR / "README_CAFECITO.md"
PDF_V2 = OUT_DIR / "INFORME_CAFECITO_DATAGASTRO_V2.pdf"
FINAL_PDF_V2 = FINAL_DIR / "INFORME_CAFECITO_DATAGASTRO_V2.pdf"

CONCLUSIONES_MD = DOCS_DIR / "conclusiones_por_categoria_cafecito.md"
CRUCES_MD = OUT_DIR / "cruces_interpretativos_cafecito.md"
RANKING_COMUNAL = OUT_DIR / "ranking_comunal_cafecito.csv"
RESUMEN_TERRITORIAL = OUT_DIR / "resumen_territorial_agregado.csv"
MAPA_COMUNAL = GRAF_DIR / "mapa_comunal_cafecito.png"
RANKING_COMUNAL_PNG = GRAF_DIR / "ranking_comunal_cafecito.png"

FOOTER = "DataGastro · Cafecito BA en tu barrio · Informe exploratorio"

A4 = (8.27, 11.69)
INK = "#1f3b57"
BLUE = "#2c7fb8"
ORANGE = "#c0762b"
GREEN = "#1a9850"
RED = "#c0392b"
GREY = "#555555"
MID_GREY = "#68717c"
LIGHT = "#eef2f6"
SOFT_BLUE = "#eaf1f8"
SOFT_ORANGE = "#f7ebdc"
SOFT_GREEN = "#eaf6ef"
LINE = "#d9dee5"
WHITE = "#ffffff"

DISPLAY = {
    "Si, es la primera vez": "Sí, es la primera vez",
    "Si, acepto": "Sí, acepto",
    "Varon": "Varón",
    "65 o mas": "65 o más",
    "Pasteleria": "Pastelería",
    "Conocer propuestas gastronomicas nuevas": "Conocer propuestas gastronómicas nuevas",
    "Web o pagina oficial de la Ciudad": "Web/página Ciudad",
    "Opciones sin tac": "Opciones sin TACC",
    "Por las opciones sin tacc": "Opción sin TACC",
}

TEXT_REPL = {
    "cafeterias": "cafeterías",
    "gastronomicas": "gastronómicas",
    "gastronomicos": "gastronómicos",
    "programacion": "programación",
    "comunicacion": "comunicación",
    "fidelizacion": "fidelización",
    "captacion": "captación",
    "decision": "decisión",
    "gestion": "gestión",
    "publico": "público",
    "publicos": "públicos",
    "senal": "señal",
    "senales": "señales",
    "metodologico": "metodológico",
    "metodologica": "metodológica",
    "tecnica": "técnica",
    "pagina": "página",
    "validas": "válidas",
    "mas": "más",
    "interes": "interés",
    "proximos": "próximos",
}


def clean_text(value: str) -> str:
    fixed = DISPLAY.get(value, value)
    for old, new in sorted(TEXT_REPL.items(), key=lambda x: len(x[0]), reverse=True):
        fixed = re.sub(rf"\b{re.escape(old)}\b", new, fixed)
    return fixed


def wrap_text(value: str, width: int) -> list[str]:
    return textwrap.wrap(clean_text(value), width=width, break_long_words=False) or [""]


def pct(n: int, d: int) -> float:
    return (n / d * 100) if d else 0.0


def pct_s(n: int, d: int, digits: int = 0) -> str:
    return f"{pct(n, d):.{digits}f}%"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def build_stats(records: list[dict]) -> dict[str, dict]:
    stats: dict[str, dict] = {}
    for key in base.CERRADAS_SIMPLES:
        counter = base.count_simple(records, key)
        stats[key] = {"items": base.ordered_items(key, counter), "base": sum(counter.values()), "multi": False}
    for key in base.CERRADAS_MULTI:
        counter, base_n = base.count_multi(records, key)
        stats[key] = {"items": counter.most_common(), "base": base_n, "multi": True}
    return stats


def items_dict(stats: dict, key: str) -> dict[str, int]:
    return dict(stats[key]["items"])


def young_adult_count(stats: dict) -> int:
    ages = items_dict(stats, "rango_edad")
    return ages.get("18 a 24", 0) + ages.get("25 a 34", 0) + ages.get("35 a 44", 0)


def ensure_analysis_outputs() -> None:
    needed = [CONCLUSIONES_MD, CRUCES_MD, RANKING_COMUNAL, RESUMEN_TERRITORIAL, MAPA_COMUNAL, RANKING_COMUNAL_PNG]
    if not all(path.exists() for path in needed):
        mejora.main()


def page() -> plt.Figure:
    fig = plt.figure(figsize=A4)
    fig.patch.set_facecolor("white")
    return fig


def footer(fig: plt.Figure) -> None:
    fig.lines.append(Line2D([0.065, 0.935], [0.055, 0.055], color=LINE, lw=0.8, transform=fig.transFigure))
    fig.text(0.065, 0.035, FOOTER, color=GREY, fontsize=7.8, va="center")


def header(fig: plt.Figure, page_no: int, title: str, subtitle: str = "", kicker: str = "DATAGASTRO") -> float:
    fig.text(0.065, 0.958, kicker, color=ORANGE, fontsize=8.5, fontweight="bold")
    fig.text(0.935, 0.958, f"{page_no:02d}", color=GREY, fontsize=8.5, ha="right")
    y = 0.925
    for line in wrap_text(title, 45):
        fig.text(0.065, y, line, color=INK, fontsize=18, fontweight="bold", va="top")
        y -= 0.032
    fig.lines.append(Line2D([0.065, 0.34], [y + 0.007, y + 0.007], color=ORANGE, lw=2.3, transform=fig.transFigure))
    if subtitle:
        for line in wrap_text(subtitle, 95):
            fig.text(0.065, y - 0.010, line, color=GREY, fontsize=10.2, style="italic", va="top")
            y -= 0.022
    return y - 0.026


def add_box(
    fig: plt.Figure,
    x: float,
    y: float,
    w: float,
    h: float,
    title: str,
    body: str | list[str],
    *,
    face: str = LIGHT,
    edge: str = BLUE,
    title_color: str = INK,
    body_size: float = 8.8,
    title_size: float = 9.2,
    bullet: bool = False,
) -> None:
    fig.patches.append(Rectangle((x, y), w, h, transform=fig.transFigure, facecolor=face, edgecolor=edge, lw=1.1))
    fig.text(x + 0.015, y + h - 0.022, clean_text(title), color=title_color, fontsize=title_size, fontweight="bold", va="top")
    text_items = body if isinstance(body, list) else [body]
    yy = y + h - 0.048
    wrap_width = max(24, int(w * 118))
    for item in text_items:
        prefix = "• " if bullet else ""
        lines = wrap_text(prefix + item, wrap_width)
        for line in lines:
            if yy < y + 0.010:
                return
            fig.text(x + 0.015, yy, line, color="#222222", fontsize=body_size, va="top")
            yy -= 0.017
        yy -= 0.006


def add_kpi_cards(fig: plt.Figure, cards: list[tuple[str, str, str]], y: float, *, x: float = 0.065, w: float = 0.87, h: float = 0.105) -> None:
    gap = 0.012
    cw = (w - gap * (len(cards) - 1)) / len(cards)
    for i, (value, label, note) in enumerate(cards):
        xx = x + i * (cw + gap)
        primary = i == 0
        face = INK if primary else WHITE
        edge = INK if primary else LINE
        val_color = ORANGE if primary else INK
        lab_color = WHITE if primary else INK
        note_color = "#dfe8f1" if primary else GREY
        fig.patches.append(FancyBboxPatch(
            (xx, y), cw, h,
            boxstyle="round,pad=0.010,rounding_size=0.012",
            transform=fig.transFigure,
            facecolor=face,
            edgecolor=edge,
            lw=1.2,
        ))
        fig.text(xx + cw / 2, y + h * 0.64, clean_text(value), ha="center", va="center", color=val_color, fontsize=18, fontweight="bold")
        fig.text(xx + cw / 2, y + h * 0.38, clean_text(label), ha="center", va="center", color=lab_color, fontsize=8.4, fontweight="bold")
        fig.text(xx + cw / 2, y + h * 0.16, clean_text(note), ha="center", va="center", color=note_color, fontsize=7.2)


def style_axis(ax) -> None:
    ax.set_facecolor("white")
    for side in ("top", "right", "bottom"):
        ax.spines[side].set_visible(False)
    ax.spines["left"].set_color(LINE)
    ax.tick_params(axis="x", length=0, labelbottom=False)
    ax.tick_params(axis="y", labelsize=7.7, colors="#222222")


def hbar(
    fig: plt.Figure,
    rect: list[float],
    items: list[tuple[str, int]],
    base_n: int,
    title: str,
    *,
    color: str = BLUE,
    accents: set[str] | None = None,
    limit: int | None = None,
    multi: bool = False,
) -> None:
    accents = accents or set()
    chosen = items[:limit] if limit else items
    chosen = list(reversed(chosen))
    labels = ["\n".join(wrap_text(DISPLAY.get(label, label), 17)) for label, _ in chosen]
    values = [value for _, value in chosen]
    colors = [ORANGE if label in accents else color for label, _ in chosen]
    ax = fig.add_axes(rect)
    ypos = list(range(len(chosen)))
    ax.barh(ypos, values, color=colors, height=0.62)
    style_axis(ax)
    ax.set_yticks([])
    max_v = max(values) if values else 1
    label_x = -max_v * 0.62
    for i, label in enumerate(labels):
        ax.text(label_x * 0.96, i, label, va="center", ha="left", color="#222222", fontsize=7.4)
    for i, value in enumerate(values):
        ax.text(value + max_v * 0.025, i, f"{value} ({pct_s(value, base_n)})", va="center", color=INK, fontsize=7.6, fontweight="bold")
    ax.axvline(0, color=LINE, lw=0.8)
    ax.set_xlim(label_x * 1.08, max_v * 1.24)
    ax.set_title(clean_text(title), loc="left", fontsize=10.5, color=INK, fontweight="bold", pad=5)
    note = f"Base: n={base_n}" + (" · multi-respuesta" if multi else "")
    ax.text(0, -0.17, clean_text(note), transform=ax.transAxes, fontsize=7.4, color=GREY, va="top")


def donut(fig: plt.Figure, rect: list[float], items: list[tuple[str, int]], title: str, center: str, colors: list[str]) -> None:
    ax = fig.add_axes(rect)
    values = [value for _, value in items]
    labels = [clean_text(label) for label, _ in items]
    wedges, _ = ax.pie(values, startangle=90, counterclock=False, colors=colors[:len(items)],
                       wedgeprops={"width": 0.38, "edgecolor": "white", "linewidth": 1.6})
    ax.text(0, 0.03, clean_text(center), ha="center", va="center", color=INK, fontsize=13, fontweight="bold")
    legend = [f"{label}: {value}" for label, value in zip(labels, values)]
    ax.legend(wedges, legend, loc="lower center", bbox_to_anchor=(0.5, -0.18), frameon=False, fontsize=7.3, ncol=1)
    ax.set_title(clean_text(title), loc="left", fontsize=10.5, color=INK, fontweight="bold", pad=5)


def stacked(fig: plt.Figure, rect: list[float], items: list[tuple[str, int]], base_n: int, title: str, colors: list[str]) -> None:
    ax = fig.add_axes(rect)
    left = 0.0
    for i, (label, value) in enumerate(items):
        width = pct(value, base_n)
        ax.barh([0], [width], left=left, color=colors[i % len(colors)], height=0.46)
        if width >= 8:
            ax.text(left + width / 2, 0, f"{clean_text(label)}\n{width:.0f}%", ha="center", va="center", fontsize=7.2, color="white", fontweight="bold")
        left += width
    ax.set_xlim(0, 100)
    ax.set_ylim(-0.55, 0.55)
    ax.axis("off")
    ax.set_title(clean_text(title), loc="left", fontsize=10.5, color=INK, fontweight="bold", pad=5)
    ax.text(0, -0.32, f"Base: n={base_n}", transform=ax.transAxes, fontsize=7.4, color=GREY, va="top")


def crop_white_margins(img: np.ndarray, threshold: float = 0.985) -> np.ndarray:
    rgb = img[:, :, :3] if img.ndim == 3 else img
    mask = np.any(rgb < threshold, axis=2)
    coords = np.argwhere(mask)
    if coords.size == 0:
        return img
    y0, x0 = coords.min(axis=0)
    y1, x1 = coords.max(axis=0) + 1
    pad_y = max(8, int((y1 - y0) * 0.03))
    pad_x = max(8, int((x1 - x0) * 0.03))
    y0 = max(0, y0 - pad_y)
    x0 = max(0, x0 - pad_x)
    y1 = min(img.shape[0], y1 + pad_y)
    x1 = min(img.shape[1], x1 + pad_x)
    return img[y0:y1, x0:x1]


def add_image(fig: plt.Figure, path: Path, rect: list[float], title: str = "") -> None:
    ax = fig.add_axes(rect)
    ax.imshow(crop_white_margins(mpimg.imread(path)), aspect="auto")
    ax.axis("off")
    if title:
        ax.set_title(clean_text(title), loc="left", fontsize=10.5, color=INK, fontweight="bold", pad=4)


def mini_table(fig: plt.Figure, x: float, y: float, w: float, h: float, rows: list[tuple[str, str, str]], title: str) -> None:
    fig.text(x, y + h + 0.010, clean_text(title), color=INK, fontsize=10, fontweight="bold")
    row_h = h / max(1, len(rows))
    for i, (a, b, c) in enumerate(rows):
        yy = y + h - (i + 1) * row_h
        face = LIGHT if i % 2 == 0 else WHITE
        fig.patches.append(Rectangle((x, yy), w, row_h - 0.002, transform=fig.transFigure, facecolor=face, edgecolor=LINE, lw=0.5))
        fig.text(x + 0.010, yy + row_h * 0.56, clean_text(a), fontsize=7.6, color=INK, fontweight="bold", va="center")
        fig.text(x + w * 0.48, yy + row_h * 0.56, clean_text(b), fontsize=7.6, color="#222222", va="center", ha="center")
        fig.text(x + w * 0.83, yy + row_h * 0.56, clean_text(c), fontsize=7.6, color="#222222", va="center", ha="center")


def crosstab(records: list[dict], a_key: str, b_key: str) -> dict[str, Counter]:
    table: dict[str, Counter] = defaultdict(Counter)
    for record in records:
        a = base.norm_space(record.get(a_key, ""))
        b = base.norm_space(record.get(b_key, ""))
        if a and b:
            table[a][b] += 1
    return table


def age_group(age: str) -> str:
    if age in {"18 a 24", "25 a 34"}:
        return "18 a 34"
    if age == "35 a 44":
        return "35 a 44"
    if age in {"45 a 54", "55 a 64", "65 o más", "65 o mas"}:
        return "45 o más"
    return "Sin dato"


def stats_payload(records: list[dict], stats: dict) -> dict[str, int]:
    channel = items_dict(stats, "como_se_entero")
    interest = items_dict(stats, "que_intereso")
    future = items_dict(stats, "eventos_futuros")
    first = items_dict(stats, "primera_vez")
    contact = items_dict(stats, "acepta_contacto")
    where = items_dict(stats, "donde_vivis")
    gender = items_dict(stats, "genero")
    plan = items_dict(stats, "con_quien")
    return {
        "n": len(records),
        "young": young_adult_count(stats),
        "caba": where.get("CABA", 0),
        "instagram": channel.get("Instagram", 0),
        "interpersonal": channel.get("Por amigos, familia o conocidos", 0),
        "paso_zona": channel.get("Pase por la zona y lo ví", 0),
        "coffee": interest.get("Probar café / cafeterías", 0),
        "paseo": interest.get("Pasear o hacer una salida", 0),
        "nuevas": interest.get("Conocer propuestas gastronomicas nuevas", 0),
        "vino": future.get("Vino", 0),
        "pasteleria": future.get("Pasteleria", 0),
        "food_trucks": future.get("Food trucks", 0),
        "cafe_futuro": future.get("Café", 0),
        "ferias": future.get("Ferias y mercados", 0),
        "first_time": first.get("Si, es la primera vez", 0),
        "recurrent": first.get("No, ya participé de otros eventos", 0),
        "contact_yes": contact.get("Si, acepto", 0),
        "contact_base": stats["acepta_contacto"]["base"],
        "mujer": gender.get("Mujer", 0),
        "pareja": plan.get("En pareja", 0),
        "amigos": plan.get("Con amigos/as", 0),
        "familia": plan.get("Con familia", 0),
    }


def cover_page(pdf: PdfPages, stats: dict, p: dict) -> None:
    fig = page()
    fig.patches.append(Rectangle((0, 0.74), 1, 0.26, transform=fig.transFigure, facecolor=INK, edgecolor="none"))
    fig.patches.append(Rectangle((0, 0.70), 1, 0.045, transform=fig.transFigure, facecolor=ORANGE, edgecolor="none"))
    fig.text(0.065, 0.925, "DataGastro", color=WHITE, fontsize=14, fontweight="bold")
    fig.text(0.065, 0.855, "Cafecito BA\nen tu barrio", color=WHITE, fontsize=31, fontweight="bold", va="top", linespacing=0.92)
    fig.text(0.065, 0.748, "Informe exploratorio de respuestas del formulario", color=WHITE, fontsize=13)
    fig.text(0.065, 0.705, "Muestra exploratoria, no representativa del público total", color=INK, fontsize=10, fontweight="bold")
    cards = [
        ("79", "respuestas", "analizadas"),
        ("57", "CABA", "procedencia declarada"),
        ("45", "Instagram", "menciones"),
        ("56/78", "contacto", "acepta novedades"),
        ("16", "páginas", "versión V2"),
    ]
    add_kpi_cards(fig, cards, 0.555, h=0.118)
    add_box(
        fig, 0.065, 0.365, 0.42, 0.130, "Lectura ejecutiva",
        "El formulario permite leer señales útiles para comunicación, programación, captación, fidelización y próximos operativos de campo.",
        face=SOFT_BLUE, edge=BLUE, body_size=9.2,
    )
    add_box(
        fig, 0.515, 0.365, 0.42, 0.130, "Cuidado metodológico",
        "Los resultados describen a quienes respondieron. No representan al total de asistentes ni habilitan inferencias estadísticas.",
        face=SOFT_ORANGE, edge=ORANGE, body_size=9.2,
    )
    add_box(
        fig, 0.065, 0.185, 0.87, 0.125, "Qué incorpora esta versión",
        [
            "Conclusiones por categoría, conclusión general y recomendaciones operativas.",
            "Ranking y mapa comunal agregados, con umbrales para no publicar granularidad riesgosa.",
            "Cruces interpretativos leídos como hipótesis de gestión, no como segmentaciones concluyentes.",
        ],
        face=LIGHT, edge=INK, bullet=True, body_size=8.8,
    )
    footer(fig)
    pdf.savefig(fig)
    plt.close(fig)


def summary_page(pdf: PdfPages, stats: dict, p: dict, page_no: int) -> None:
    fig = page()
    y = header(fig, page_no, "Resumen ejecutivo", "Cinco señales iniciales para orientar decisiones de gestión.")
    add_kpi_cards(fig, [
        ("79", "respuestas", "base exploratoria"),
        (f"{p['young']}/79", "18 a 44", "bloque principal"),
        (f"{p['caba']}/79", "CABA", "procedencia macro"),
        (f"{p['instagram']}/79", "Instagram", "canal mencionado"),
        (f"{p['contact_yes']}/{p['contact_base']}", "contacto", "acepta novedades"),
    ], y - 0.105)
    bullets = [
        f"La muestra captada es joven-adulta: {p['young']}/79 respuestas están entre 18 y 44 años, con pico en 25 a 34.",
        f"Instagram lidera la llegada ({p['instagram']}/79), pero la recomendación interpersonal ({p['interpersonal']}/79) y el paso por la zona ({p['paso_zona']}/79) también importan.",
        f"La mayoría declara experiencia previa en eventos gastronómicos de la Ciudad ({p['recurrent']}/79), pero también hay captación nueva ({p['first_time']}/79).",
        f"La aceptación de contacto ({p['contact_yes']}/{p['contact_base']}) abre una oportunidad de fidelización y comunicación futura.",
        f"El atractivo combina producto y experiencia: probar café/cafeterías ({p['coffee']}/79) y pasear o hacer una salida ({p['paseo']}/79).",
        "El relevamiento funcionó como primer experimento de medición: conviene fortalecer QR, incentivos, encuestadores y articulación con locales adheridos.",
    ]
    add_box(fig, 0.065, 0.345, 0.56, 0.305, "Conclusiones ejecutivas", bullets, face=WHITE, edge=BLUE, bullet=True, body_size=8.7)
    add_box(fig, 0.655, 0.505, 0.28, 0.145, "Cuidado metodológico", "Las métricas son señales de la muestra encuestada. No deben presentarse como perfil total del evento.", face=SOFT_ORANGE, edge=ORANGE)
    add_box(fig, 0.655, 0.345, 0.28, 0.135, "Decisión habilitada", "Priorizar comunicación digital, reforzar difusión física y diseñar próximas mediciones con mayor captación.", face=SOFT_GREEN, edge=GREEN)
    hbar(fig, [0.065, 0.120, 0.40, 0.165], stats["como_se_entero"]["items"], stats["como_se_entero"]["base"], "Canales principales", accents={"Instagram", "Por amigos, familia o conocidos"}, limit=4, multi=True)
    hbar(fig, [0.535, 0.120, 0.40, 0.165], stats["eventos_futuros"]["items"], stats["eventos_futuros"]["base"], "Intereses futuros", color=ORANGE, accents={"Vino", "Pasteleria", "Food trucks", "Café"}, limit=5, multi=True)
    footer(fig)
    pdf.savefig(fig)
    plt.close(fig)


def decision_page(pdf: PdfPages, page_no: int) -> None:
    fig = page()
    header(fig, page_no, "Qué permite leer este relevamiento", "No solo qué respondió la gente: qué decisiones habilita cada bloque de preguntas.")
    cards = [
        ("Comunicación", "Ajustar canales, tono y piezas según cómo se enteran las personas."),
        ("Programación", "Usar intereses futuros como señales iniciales para nuevas acciones."),
        ("Captación", "Distinguir primeras visitas y público recurrente para crecer sin perder audiencia."),
        ("Fidelización", "Trabajar la aceptación de contacto como puerta de comunicación futura."),
        ("Formulario", "Separar preguntas útiles de preguntas con baja acción o fricción."),
        ("Operativo territorial", "Ubicar QR, encuestadores y difusión física donde mejor capturen respuestas."),
    ]
    x0, y0 = 0.065, 0.675
    for i, (title, body) in enumerate(cards):
        col = i % 2
        row = i // 2
        x = x0 + col * 0.455
        y = y0 - row * 0.155
        add_box(fig, x, y, 0.415, 0.115, title, body, face=WHITE if i % 2 else LIGHT, edge=BLUE if i < 3 else ORANGE)
    add_box(
        fig, 0.065, 0.165, 0.87, 0.225, "Síntesis tipo “qué decisión habilita”",
        [
            "Perfil: ajustar mensajes sin sobregeneralizar la muestra.",
            "Territorio: leer cercanía y sesgo posible del punto de captación.",
            "Canales: sostener Instagram y activar recomendación/locales adheridos.",
            "Operativo: aumentar muestra con incentivos, QR visibles y equipo encuestador.",
        ],
        face=SOFT_BLUE, edge=INK, bullet=True, body_size=9.2,
    )
    footer(fig)
    pdf.savefig(fig)
    plt.close(fig)


def profile_page(pdf: PdfPages, stats: dict, p: dict, page_no: int) -> None:
    fig = page()
    header(fig, page_no, "Perfil de la muestra", "Edad, género y procedencia describen respondentes, no el público total.")
    hbar(fig, [0.075, 0.545, 0.405, 0.285], stats["rango_edad"]["items"], stats["rango_edad"]["base"], "Rango de edad", accents={"18 a 24", "25 a 34", "35 a 44"})
    stacked(fig, [0.545, 0.690, 0.355, 0.120], stats["genero"]["items"], stats["genero"]["base"], "Género declarado", [INK, ORANGE, GREY])
    caba = p["caba"]
    no_caba = p["n"] - caba
    donut(fig, [0.555, 0.425, 0.320, 0.225], [("CABA", caba), ("No CABA", no_caba)], "Procedencia macro", f"{pct_s(caba, p['n'])}\nCABA", [BLUE, "#e6b17e"])
    add_box(fig, 0.065, 0.265, 0.415, 0.130, "Lectura ejecutiva", f"El bloque 18 a 44 suma {p['young']}/79 respuestas. La muestra captada es joven-adulta y mayoritariamente femenina, pero no se proyecta al total del evento.", face=SOFT_BLUE, edge=BLUE)
    add_box(fig, 0.520, 0.265, 0.415, 0.130, "Cuidado metodológico", "La procedencia macro se publica agregada. El barrio/localidad libre queda fuera de outputs públicos por privacidad y calidad del dato.", face=SOFT_ORANGE, edge=ORANGE)
    footer(fig)
    pdf.savefig(fig)
    plt.close(fig)


def territory_page(pdf: PdfPages, ranking_rows: list[dict], page_no: int) -> None:
    fig = page()
    header(fig, page_no, "Lectura territorial agregada", "CABA vs no CABA, ranking comunal y mapa sin publicar barrios/localidades libres.")
    add_image(fig, MAPA_COMUNAL, [0.055, 0.215, 0.47, 0.600], "Mapa comunal")
    add_image(fig, RANKING_COMUNAL_PNG, [0.535, 0.375, 0.40, 0.420], "Ranking comunal")
    top = [r for r in ranking_rows if str(r["comuna"]).isdigit()][:5]
    top_txt = ", ".join(f"Comuna {r['comuna']} ({r['cantidad_respuestas']})" for r in top)
    grouped = next((r for r in ranking_rows if not str(r["comuna"]).isdigit()), None)
    grouped_txt = f" Las comunas por debajo del umbral se agrupan: {grouped['cantidad_respuestas']} respuestas." if grouped else ""
    add_box(fig, 0.535, 0.220, 0.40, 0.115, "Lectura ejecutiva", f"Ranking agregado: {top_txt}.{grouped_txt}", face=SOFT_BLUE, edge=BLUE, body_size=8.5)
    add_box(fig, 0.065, 0.105, 0.87, 0.075, "Cuidado metodológico", "El peso de Comuna 13 puede reflejar cercanía a Belgrano y al punto/horario de captación. Es señal territorial, no mapa representativo de asistencia.", face=SOFT_ORANGE, edge=ORANGE, body_size=8.8)
    footer(fig)
    pdf.savefig(fig)
    plt.close(fig)


def loyalty_page(pdf: PdfPages, stats: dict, p: dict, records: list[dict], page_no: int) -> None:
    fig = page()
    header(fig, page_no, "Vínculo con eventos de la Ciudad", "Captación nueva, público recurrente y aceptación de contacto.")
    stacked(fig, [0.080, 0.690, 0.420, 0.130], stats["primera_vez"]["items"], stats["primera_vez"]["base"], "Primera vez vs recurrentes", [INK, ORANGE, GREY])
    donut(fig, [0.590, 0.590, 0.255, 0.235], stats["acepta_contacto"]["items"], "Acepta recibir novedades", f"{pct_s(p['contact_yes'], p['contact_base'])}", [GREEN, GREY])
    table = crosstab(records, "primera_vez", "acepta_contacto")
    rows = []
    for label in ["No, ya participé de otros eventos", "Si, es la primera vez", "No estoy seguro/a"]:
        row = table.get(label, Counter())
        if row:
            rows.append((label.replace("No, ya participé de otros eventos", "Recurrentes"), str(row.get("Si, acepto", 0)), str(sum(row.values()))))
    mini_table(fig, 0.090, 0.400, 0.765, 0.125, rows, "Aceptación de contacto por vínculo previo")
    add_box(fig, 0.065, 0.220, 0.405, 0.115, "Lectura ejecutiva", f"El evento combina fidelización ({p['recurrent']}/79 recurrentes) y captación ({p['first_time']}/79 primeras visitas).", face=SOFT_BLUE, edge=BLUE)
    add_box(fig, 0.530, 0.220, 0.405, 0.115, "Qué decisión habilita", "Diseñar comunicación posterior diferenciando continuidad para recurrentes y bienvenida/retención para primeras visitas.", face=SOFT_GREEN, edge=GREEN)
    footer(fig)
    pdf.savefig(fig)
    plt.close(fig)


def plan_page(pdf: PdfPages, stats: dict, p: dict, page_no: int) -> None:
    fig = page()
    header(fig, page_no, "Tipo de plan", "Con quién vino la persona y qué implica para el diseño del evento.")
    donut(fig, [0.075, 0.475, 0.380, 0.330], stats["con_quien"]["items"], "Composición declarada del plan", "plan\nsocial", [INK, ORANGE, BLUE, "#e6b17e", GREY])
    hbar(fig, [0.535, 0.475, 0.355, 0.330], stats["con_quien"]["items"], stats["con_quien"]["base"], "Ranking de acompañamiento", color=ORANGE, accents={"En pareja", "Con amigos/as", "Con familia"})
    add_box(fig, 0.065, 0.265, 0.405, 0.125, "Lectura ejecutiva", f"Pareja ({p['pareja']}), amigos/as ({p['amigos']}) y familia ({p['familia']}) concentran la mayor parte de las respuestas.", face=SOFT_BLUE, edge=BLUE)
    add_box(fig, 0.530, 0.265, 0.405, 0.125, "Qué decisión habilita", "Pensar señalética, mesas, descanso, circulación, horarios y propuestas complementarias para planes sociales y familiares.", face=SOFT_GREEN, edge=GREEN)
    add_box(fig, 0.065, 0.135, 0.87, 0.075, "Cuidado metodológico", "La pregunta mide modo de asistencia declarado; no mide tamaño real del grupo, consumo ni permanencia.", face=SOFT_ORANGE, edge=ORANGE, body_size=8.8)
    footer(fig)
    pdf.savefig(fig)
    plt.close(fig)


def channels_page(pdf: PdfPages, stats: dict, p: dict, page_no: int) -> None:
    fig = page()
    header(fig, page_no, "Canales de llegada", "Redes, recomendación interpersonal y visibilidad territorial.")
    hbar(fig, [0.075, 0.455, 0.50, 0.365], stats["como_se_entero"]["items"], stats["como_se_entero"]["base"], "Cómo se enteraron del evento", color=BLUE, accents={"Instagram", "Por amigos, familia o conocidos", "Pase por la zona y lo ví"}, multi=True)
    add_box(fig, 0.625, 0.660, 0.31, 0.145, "Lectura ejecutiva", f"Instagram aparece como canal principal ({p['instagram']}/79). La recomendación interpersonal suma {p['interpersonal']}/79 y el paso por la zona {p['paso_zona']}/79.", face=SOFT_BLUE, edge=BLUE)
    add_box(fig, 0.625, 0.480, 0.31, 0.145, "Oportunidad", "No aparece un canal fuerte asociado a cafeterías/locales adheridos. Conviene activarlos con historias, reposts, folletería, cartelería y QR.", face=SOFT_GREEN, edge=GREEN)
    add_box(fig, 0.065, 0.190, 0.87, 0.145, "Qué decisión habilita", [
        "Sostener Instagram como canal prioritario, pero no depender solo de redes.",
        "Usar locales físicos y cartelería para públicos mayores o menos digitalizados.",
        "Diseñar piezas para que locales participantes comuniquen antes y durante el evento.",
    ], face=WHITE, edge=ORANGE, bullet=True)
    footer(fig)
    pdf.savefig(fig)
    plt.close(fig)


def motivations_page(pdf: PdfPages, stats: dict, p: dict, page_no: int) -> None:
    fig = page()
    header(fig, page_no, "Motivaciones del evento", "Producto gastronómico y experiencia urbana aparecen juntos.")
    hbar(fig, [0.080, 0.430, 0.520, 0.390], stats["que_intereso"]["items"], stats["que_intereso"]["base"], "Qué fue lo que más interesó", color="#6f4e37", accents={"Probar café / cafeterías", "Pasear o hacer una salida", "Conocer propuestas gastronomicas nuevas"})
    add_box(fig, 0.635, 0.665, 0.30, 0.130, "Lectura ejecutiva", f"Probar café/cafeterías ({p['coffee']}/79) lidera, seguido por paseo/salida ({p['paseo']}/79) y propuestas nuevas ({p['nuevas']}/79).", face=SOFT_BLUE, edge=BLUE)
    add_box(fig, 0.635, 0.505, 0.30, 0.130, "Qué decisión habilita", "Comunicar Cafecito como experiencia completa: café, paseo, salida, música, descubrimiento y ciudad.", face=SOFT_GREEN, edge=GREEN)
    add_box(fig, 0.065, 0.185, 0.87, 0.115, "Cuidado metodológico", "La pregunta captura un atractivo principal por persona. No agota motivaciones múltiples ni mide satisfacción directa.", face=SOFT_ORANGE, edge=ORANGE)
    footer(fig)
    pdf.savefig(fig)
    plt.close(fig)


def future_page(pdf: PdfPages, stats: dict, p: dict, page_no: int) -> None:
    fig = page()
    header(fig, page_no, "Intereses futuros", "Señales iniciales para programación, no demanda representativa.")
    hbar(fig, [0.075, 0.385, 0.58, 0.445], stats["eventos_futuros"]["items"], stats["eventos_futuros"]["base"], "Eventos gastronómicos de interés futuro", color=BLUE, accents={"Vino", "Pasteleria", "Food trucks", "Café", "Ferias y mercados"}, limit=10, multi=True)
    add_box(fig, 0.690, 0.665, 0.245, 0.140, "Top señales", [
        f"Vino: {p['vino']}/79.",
        f"Pastelería: {p['pasteleria']}/79.",
        f"Food trucks: {p['food_trucks']}/79.",
        f"Café: {p['cafe_futuro']}/79.",
        f"Ferias/mercados: {p['ferias']}/79.",
    ], face=SOFT_BLUE, edge=BLUE, bullet=True, body_size=8.2)
    add_box(fig, 0.690, 0.455, 0.245, 0.165, "Qué decisión habilita", "Usar estas respuestas como primera agenda de hipótesis para testear próximos eventos, piezas de comunicación y alianzas.", face=SOFT_GREEN, edge=GREEN)
    add_box(fig, 0.065, 0.165, 0.87, 0.095, "Cuidado metodológico", "Es una pregunta multi-respuesta: los porcentajes no son excluyentes y pueden sumar más de 100%.", face=SOFT_ORANGE, edge=ORANGE)
    footer(fig)
    pdf.savefig(fig)
    plt.close(fig)


def conclusions_page_1(pdf: PdfPages, p: dict, page_no: int) -> None:
    fig = page()
    header(fig, page_no, "Conclusiones por categoría", "Lecturas principales para comunicación, fidelización, perfil y territorio.")
    boxes = [
        ("Comunicación", f"Instagram lidera ({p['instagram']}/79), pero recomendación interpersonal y paso por la zona amplían la lectura de llegada."),
        ("Fidelización y captación", f"Conviven recurrentes ({p['recurrent']}/79), primeras visitas ({p['first_time']}/79) y alta aceptación de contacto ({p['contact_yes']}/{p['contact_base']})."),
        ("Perfil captado", f"Predomina la muestra joven-adulta ({p['young']}/79), mayoritariamente femenina ({p['mujer']}/79) y residente en CABA ({p['caba']}/79)."),
        ("Territorio", "Comuna 13 aparece fuerte en el agregado, con lectura cautelosa por cercanía a Belgrano y al punto de captación."),
    ]
    for i, (title, body) in enumerate(boxes):
        add_box(fig, 0.065 + (i % 2) * 0.455, 0.650 - (i // 2) * 0.190, 0.415, 0.145, title, body, face=WHITE if i % 2 else LIGHT, edge=BLUE)
    add_box(fig, 0.065, 0.195, 0.87, 0.145, "Conclusión general", "El relevamiento no representa al total del público, pero sí muestra señales útiles: perfil de respondentes, canales de llegada, potencial de contacto, motivaciones y ajustes necesarios para próximas mediciones.", face=SOFT_BLUE, edge=INK, body_size=9.2)
    footer(fig)
    pdf.savefig(fig)
    plt.close(fig)


def conclusions_page_2(pdf: PdfPages, p: dict, page_no: int) -> None:
    fig = page()
    header(fig, page_no, "Qué aprendimos", "Experiencia, programación futura y operativo/formulario.")
    boxes = [
        ("Experiencia", "Cafecito funciona como plan social: pareja, amistades y familia estructuran la asistencia declarada."),
        ("Programación futura", "Vino, pastelería, food trucks, café y ferias/mercados aparecen como primeras hipótesis de agenda."),
        ("Formulario", "Las preguntas cerradas funcionaron; las multi-respuesta requieren opciones canónicas y tratamiento documentado."),
        ("Operativo", "La captación puede mejorar con QR visibles, incentivo claro, encuestadores y apoyo de productora/locales."),
    ]
    for i, (title, body) in enumerate(boxes):
        add_box(fig, 0.065 + (i % 2) * 0.455, 0.650 - (i // 2) * 0.180, 0.415, 0.135, title, body, face=WHITE if i % 2 else LIGHT, edge=ORANGE if i > 1 else BLUE)
    add_box(fig, 0.065, 0.165, 0.87, 0.175, "Síntesis institucional", [
        "Comunicar el evento como experiencia, no solo como consumo.",
        "Activar locales adheridos como canal físico y digital.",
        "Aumentar muestra y reducir sesgo de captación en próximos relevamientos.",
        "Mantener privacidad: outputs públicos solo agregados.",
    ], face=SOFT_GREEN, edge=GREEN, bullet=True, body_size=9.2)
    footer(fig)
    pdf.savefig(fig)
    plt.close(fig)


def operations_page(pdf: PdfPages, page_no: int) -> None:
    fig = page()
    header(fig, page_no, "Aprendizajes del formulario y operativo", "Qué funcionó y qué ajustar antes del próximo relevamiento.")
    add_box(fig, 0.065, 0.600, 0.415, 0.215, "Qué funcionó", [
        "El formulario cubre perfil, procedencia, vínculo previo, canales, motivación e intereses futuros.",
        "Las preguntas cerradas permiten producir agregados claros y reproducibles.",
        "El consentimiento de contacto habilita una lectura de fidelización sin publicar datos personales.",
    ], face=SOFT_BLUE, edge=BLUE, bullet=True)
    add_box(fig, 0.520, 0.600, 0.415, 0.215, "Qué ajustar", [
        "Hacer el formulario más breve y accionable.",
        "Separar información sensible de outputs públicos desde el diseño.",
        "Definir antes qué decisión alimenta cada pregunta.",
        "Resolver conectividad/offline y disponibilidad de dispositivos.",
    ], face=SOFT_ORANGE, edge=ORANGE, bullet=True)
    add_box(fig, 0.065, 0.320, 0.415, 0.205, "Captación en campo", [
        "Recompensas claras por completar correctamente.",
        "Más incentivos disponibles si la dinámica lo permite.",
        "QR visibles en puntos de circulación y descanso.",
        "Equipo o productora con personas dedicadas a encuestar.",
    ], face=WHITE, edge=GREEN, bullet=True)
    add_box(fig, 0.520, 0.320, 0.415, 0.205, "Locales adheridos", [
        "Publicar historias y repostear piezas oficiales.",
        "Colocar folletería, cartelería y QR en el local.",
        "Funcionar como puntos físicos de difusión para público menos digital.",
    ], face=WHITE, edge=GREEN, bullet=True)
    footer(fig)
    pdf.savefig(fig)
    plt.close(fig)


def recommendations_page(pdf: PdfPages, page_no: int) -> None:
    fig = page()
    header(fig, page_no, "Recomendaciones para próximos relevamientos", "Acciones concretas para aumentar utilidad, muestra y calidad.")
    recs = [
        ("Aumentar muestra", "Planificar momentos y puntos de captación antes, durante y después del pico de circulación."),
        ("Mejorar incentivo", "Explicar recompensa, condición de participación y disponibilidad real."),
        ("QR visibles", "Ubicarlos en accesos, mesas, filas, puestos y piezas impresas."),
        ("Equipo encuestador", "Asignar personas responsables, con guion breve y seguimiento de cuotas operativas."),
        ("Locales adheridos", "Convertir cafeterías participantes en canal físico y digital de difusión."),
        ("Preguntas accionables", "Eliminar o simplificar preguntas que no alimentan decisiones concretas."),
        ("Horarios", "Medir captación por franjas para detectar sesgos operativos."),
        ("Offline", "Tener alternativa ante conectividad baja o saturación de red."),
    ]
    for i, (title, body) in enumerate(recs):
        x = 0.065 + (i % 2) * 0.455
        y = 0.710 - (i // 2) * 0.142
        add_box(fig, x, y, 0.415, 0.105, title, body, face=WHITE if i % 2 else LIGHT, edge=BLUE if i < 4 else ORANGE, body_size=8.2)
    add_box(fig, 0.065, 0.110, 0.87, 0.070, "Principio rector", "El objetivo no es acumular respuestas: es producir evidencia exploratoria útil, segura y accionable para gestión.", face=SOFT_GREEN, edge=GREEN, body_size=9.2)
    footer(fig)
    pdf.savefig(fig)
    plt.close(fig)


def crosstab_page(pdf: PdfPages, records: list[dict], stats: dict, page_no: int) -> None:
    fig = page()
    header(fig, page_no, "Cruces interpretativos", "Hipótesis prudentes: no se fuerzan conclusiones con celdas chicas.")
    enriched = []
    for r in records:
        rr = dict(r)
        parts = base.split_multi(rr.get("como_se_entero", ""), "como_se_entero")
        rr["canal_principal"] = parts[0] if parts else ""
        rr["edad_grupo"] = age_group(base.norm_space(rr.get("rango_edad", "")))
        rr["paso_zona"] = "pasó por la zona" if "Pase por la zona y lo ví" in parts else "otros canales"
        enriched.append(rr)
    table_age = crosstab(enriched, "edad_grupo", "canal_principal")
    rows_age = []
    for seg in ["18 a 34", "35 a 44", "45 o más"]:
        row = table_age.get(seg, Counter())
        rows_age.append((seg, f"Instagram {row.get('Instagram', 0)}", f"Interpersonal {row.get('Por amigos, familia o conocidos', 0)}"))
    mini_table(fig, 0.080, 0.645, 0.78, 0.145, rows_age, "Edad x canal principal")
    table_contact = crosstab(records, "primera_vez", "acepta_contacto")
    rows_contact = []
    for seg in ["No, ya participé de otros eventos", "Si, es la primera vez"]:
        row = table_contact.get(seg, Counter())
        rows_contact.append((seg.replace("No, ya participé de otros eventos", "Recurrentes"), f"Acepta {row.get('Si, acepto', 0)}", f"Total {sum(row.values())}"))
    mini_table(fig, 0.080, 0.430, 0.78, 0.110, rows_contact, "Primera vez x aceptación de contacto")
    add_box(fig, 0.065, 0.230, 0.405, 0.125, "Lectura ejecutiva", "Los cruces refuerzan tres señales: Instagram pesa en segmentos jóvenes, el paso por zona aparece como hipótesis en mayores y la aceptación de contacto atraviesa recurrentes y primeras visitas.", face=SOFT_BLUE, edge=BLUE)
    add_box(fig, 0.530, 0.230, 0.405, 0.125, "Cuidado metodológico", "Las celdas chicas se leen como hipótesis operativas. No se usan para segmentaciones concluyentes ni inferencias representativas.", face=SOFT_ORANGE, edge=ORANGE)
    footer(fig)
    pdf.savefig(fig)
    plt.close(fig)


def annex_page(pdf: PdfPages, page_no: int) -> None:
    fig = page()
    header(fig, page_no, "Anexo metodológico", "Fuente, privacidad, tratamiento territorial y reproducibilidad.")
    add_box(fig, 0.065, 0.650, 0.415, 0.165, "Fuente y base", [
        "Formulario Cafecito BA en tu barrio.",
        "79 respuestas analizadas.",
        "Lectura del XLSX original en modo solo lectura.",
        "Sin requests ni uso de APIs.",
    ], face=WHITE, edge=BLUE, bullet=True)
    add_box(fig, 0.520, 0.650, 0.415, 0.165, "Privacidad", [
        "No se publican correos, nombres, teléfonos ni marcas temporales.",
        "No se listan barrios/localidades libres.",
        "No se publican respuestas individuales ni identificadores.",
    ], face=SOFT_ORANGE, edge=ORANGE, bullet=True)
    add_box(fig, 0.065, 0.405, 0.415, 0.170, "Multi-respuesta", [
        "Canales e intereses futuros se leen por menciones.",
        "Los porcentajes pueden sumar más de 100%.",
        "La categoría “Por amigos, familia o conocidos” se conserva unificada.",
    ], face=LIGHT, edge=INK, bullet=True)
    add_box(fig, 0.520, 0.405, 0.415, 0.170, "Territorio", [
        "CABA vs no CABA se publica a nivel macro.",
        "Comuna se publica agregada con umbral mínimo.",
        "Comunas chicas quedan agrupadas para evitar granularidad riesgosa.",
    ], face=LIGHT, edge=INK, bullet=True)
    add_box(fig, 0.065, 0.180, 0.87, 0.115, "Archivos V2", [
        "scripts/cafecito/generar_informe_datagastro_v2.py",
        "outputs/cafecito/INFORME_CAFECITO_DATAGASTRO_V2.pdf",
        "Cafesito/final/INFORME_CAFECITO_DATAGASTRO_V2.pdf",
    ], face=SOFT_GREEN, edge=GREEN, bullet=True, body_size=8.4)
    footer(fig)
    pdf.savefig(fig)
    plt.close(fig)


def write_pdf(records: list[dict], stats: dict, ranking_rows: list[dict]) -> int:
    p = stats_payload(records, stats)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    with PdfPages(PDF_V2) as pdf:
        cover_page(pdf, stats, p)
        summary_page(pdf, stats, p, 2)
        decision_page(pdf, 3)
        profile_page(pdf, stats, p, 4)
        territory_page(pdf, ranking_rows, 5)
        loyalty_page(pdf, stats, p, records, 6)
        plan_page(pdf, stats, p, 7)
        channels_page(pdf, stats, p, 8)
        motivations_page(pdf, stats, p, 9)
        future_page(pdf, stats, p, 10)
        conclusions_page_1(pdf, p, 11)
        conclusions_page_2(pdf, p, 12)
        operations_page(pdf, 13)
        recommendations_page(pdf, 14)
        crosstab_page(pdf, records, stats, 15)
        annex_page(pdf, 16)
    shutil.copy2(PDF_V2, FINAL_PDF_V2)
    return 16


def write_markdown_v2(records: list[dict], stats: dict, ranking_rows: list[dict]) -> None:
    p = stats_payload(records, stats)
    top_ranking = ", ".join(
        f"Comuna {r['comuna']} ({r['cantidad_respuestas']})"
        for r in ranking_rows
        if str(r["comuna"]).isdigit()
    )
    lines = [
        "# DataGastro - Cafecito BA en tu barrio",
        "",
        "## Informe exploratorio de respuestas del formulario - Versión visual V2",
        "",
        "**Nota metodológica:** muestra exploratoria, no representativa del público total del evento. No se publican correos, marcas temporales, barrios/localidades libres, teléfonos ni identificadores personales.",
        "",
        "## 1. Resumen ejecutivo",
        "",
        f"El relevamiento analiza **{p['n']} respuestas**. Permite leer señales iniciales para comunicación, programación, captación, fidelización y mejora del operativo territorial.",
        "",
        "- La muestra captada es joven-adulta: 18 a 44 suma **{young}/79** respuestas.".format(young=p["young"]),
        "- Instagram es el canal principal mencionado: **{}/79**.".format(p["instagram"]),
        "- La recomendación interpersonal suma **{}/79** y el paso por la zona **{}/79**.".format(p["interpersonal"], p["paso_zona"]),
        "- El evento combina público recurrente (**{}/79**) y primeras visitas (**{}/79**).".format(p["recurrent"], p["first_time"]),
        "- La aceptación de contacto (**{}/{})** sugiere potencial de fidelización y comunicación futura.".format(p["contact_yes"], p["contact_base"]),
        "",
        "## 2. Qué decisión habilita cada bloque",
        "",
        "- **Comunicación:** sostener Instagram y reforzar difusión física/interpersonal.",
        "- **Programación:** leer intereses futuros como hipótesis de agenda.",
        "- **Captación:** separar primera visita y recurrencia.",
        "- **Fidelización:** trabajar contacto futuro sin publicar datos personales.",
        "- **Formulario:** mantener preguntas con decisión asociada.",
        "- **Operativo:** mejorar QR, incentivo, encuestadores y locales adheridos.",
        "",
        "## 3. Perfil de la muestra",
        "",
        f"El bloque 18 a 44 suma {p['young']}/79 respuestas; mujeres, {p['mujer']}/79; CABA, {p['caba']}/79. Son datos de respondentes, no del total de asistentes.",
        "",
        "## 4. Lectura territorial",
        "",
        f"Ranking comunal agregado: {top_ranking}. Las comunas por debajo del umbral mínimo se agrupan. Si Comuna 13 aparece fuerte, se interpreta con cautela por cercanía a Belgrano y al punto de captación.",
        "",
        "## 5. Fidelización y captación",
        "",
        f"Ya habían participado en eventos gastronómicos de la Ciudad {p['recurrent']}/79 personas; {p['first_time']}/79 eran primera visita. Aceptan recibir novedades {p['contact_yes']}/{p['contact_base']} respuestas válidas.",
        "",
        "## 6. Canales de llegada",
        "",
        f"Instagram lidera ({p['instagram']}/79). La recomendación interpersonal ({p['interpersonal']}/79) y el paso por la zona ({p['paso_zona']}/79) completan la lectura. No aparece un canal fuerte asociado a cafeterías/locales adheridos, lo que abre una oportunidad de mejora.",
        "",
        "## 7. Motivaciones e intereses futuros",
        "",
        f"El principal atractivo fue probar café/cafeterías ({p['coffee']}/79), seguido por pasear o hacer una salida ({p['paseo']}/79). Intereses futuros destacados: vino ({p['vino']}), pastelería ({p['pasteleria']}), food trucks ({p['food_trucks']}), café ({p['cafe_futuro']}) y ferias/mercados ({p['ferias']}).",
        "",
        "## 8. Recomendaciones operativas",
        "",
        "- Aumentar muestra con puntos y horarios de captación definidos.",
        "- Mejorar incentivo y disponibilidad de recompensas.",
        "- Colocar QR visibles en accesos, filas, mesas y puestos.",
        "- Asignar equipo encuestador o apoyo de productora.",
        "- Activar locales adheridos como canal físico y digital.",
        "- Simplificar preguntas y asegurar conectividad/offline.",
        "",
        "## 9. Archivos V2",
        "",
        "- `scripts/cafecito/generar_informe_datagastro_v2.py`",
        "- `outputs/cafecito/INFORME_CAFECITO_DATAGASTRO_V2.pdf`",
        "- `Cafesito/final/INFORME_CAFECITO_DATAGASTRO_V2.pdf`",
        "- `outputs/cafecito/graficos_datagastro/mapa_comunal_cafecito.png`",
        "- `outputs/cafecito/graficos_datagastro/ranking_comunal_cafecito.png`",
        "",
        "## 10. Anexo metodológico",
        "",
        "- Fuente principal: `Cafesito/Formulario Cafecito (Respuestas).xlsx`.",
        "- Respuestas analizadas: 79.",
        "- Tratamiento multi-respuesta: porcentajes por menciones, no excluyentes.",
        "- Categoría protegida: `Por amigos, familia o conocidos` se conserva unificada.",
        "- Tratamiento territorial: publicación macro y comunal agregada; sin barrios/localidades libres.",
        "- PDF V2: 16 páginas con footer homogéneo `DataGastro · Cafecito BA en tu barrio · Informe exploratorio`.",
        "",
    ]
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def update_readme_v2() -> None:
    text = README_MD.read_text(encoding="utf-8") if README_MD.exists() else "# Cafecito\n"
    block = """## Versión DataGastro V2

Para regenerar la versión final visual V2:

```powershell
python scripts/cafecito/generar_informe_datagastro_v2.py
```

Salidas V2:

- PDF institucional V2: `outputs/cafecito/INFORME_CAFECITO_DATAGASTRO_V2.pdf`
- Copia final V2: `Cafesito/final/INFORME_CAFECITO_DATAGASTRO_V2.pdf`
- Script generador: `scripts/cafecito/generar_informe_datagastro_v2.py`

La V2 usa la mejora analítica territorial e interpretativa:

- `docs/cafecito/conclusiones_por_categoria_cafecito.md`
- `outputs/cafecito/ranking_comunal_cafecito.csv`
- `outputs/cafecito/resumen_territorial_agregado.csv`
- `outputs/cafecito/cruces_interpretativos_cafecito.md`
- `outputs/cafecito/graficos_datagastro/mapa_comunal_cafecito.png`
- `outputs/cafecito/graficos_datagastro/ranking_comunal_cafecito.png`

La versión anterior se conserva y no se sobrescribe.
"""
    pattern = r"(?ms)^## Versión DataGastro V2\n.*?(?=^## |\Z)"
    if re.search(pattern, text):
        text = re.sub(pattern, block.rstrip() + "\n\n", text)
    else:
        text = text.rstrip() + "\n\n" + block
    README_MD.write_text(text.rstrip() + "\n", encoding="utf-8")


def main() -> None:
    ensure_analysis_outputs()
    records = base.read_xlsx(base.XLSX)
    stats = build_stats(records)
    ranking_rows = read_csv(RANKING_COMUNAL)
    pages = write_pdf(records, stats, ranking_rows)
    write_markdown_v2(records, stats, ranking_rows)
    update_readme_v2()
    print("=" * 72)
    print("Informe Cafecito DataGastro V2")
    print(f"  Respuestas: {len(records)}")
    print(f"  Paginas: {pages}")
    print(f"  PDF: {PDF_V2}")
    print(f"  Copia final: {FINAL_PDF_V2}")
    print("=" * 72)


if __name__ == "__main__":
    main()
