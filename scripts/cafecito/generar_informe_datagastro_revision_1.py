"""Genera el informe Cafecito DataGastro · REVISIÓN 1.

Versión reorientada como **informe de resultados de encuesta**: datos duros,
preguntas del formulario, porcentajes y descripción de resultados. Tono
descriptivo en el cuerpo; síntesis y recomendaciones en potencial. Sin página
propia de metodología/privacidad. La red de cafeterías queda como anexo.

Reutiliza (importa) del generador FINAL el motor de datos, cálculo y dibujo
(mapas, primitivas de layout, parser YAML), sin duplicarlo y sin modificarlo.

Reglas del PDF público (idénticas al final): sin rutas, scripts, hashes,
versiones internas, ni datos personales. El público se muestra agregado.

NO sobrescribe:
  - INFORME_CAFECITO_DATAGASTRO_FINAL.pdf (outputs/ y Cafesito/final/)
  - INFORME_CAFECITO_DATAGASTRO_FINAL_EDITABLE_TEST.pdf

Salidas:
  - outputs/cafecito/INFORME_CAFECITO_DATAGASTRO_REVISION_1.pdf
  - Cafesito/final/INFORME_CAFECITO_DATAGASTRO_REVISION_1.pdf

Uso:
    python scripts/cafecito/generar_informe_datagastro_revision_1.py
"""
from __future__ import annotations

import shutil
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Motor del generador final: datos, calculos, mapas y primitivas de layout.
from scripts.cafecito import generar_informe_datagastro_final as final  # noqa: E402
from scripts.cafecito.generar_informe_datagastro_final_editable import _load_yaml, fmt  # noqa: E402
from scripts.cafecito.generar_informe_datagastro_final import (  # noqa: E402
    INK, ORANGE, GREEN, BLUE, GREY, WHITE, LIGHT, LINE,
    SOFT_BLUE, SOFT_ORANGE, SOFT_GREEN,
    add_box, add_image, clean_text, donut, footer as base_footer,
    hbar, header, items_dict, page, pct, pct_s, stacked, wrap_text,
)

DOCS_DIR = REPO_ROOT / "docs" / "cafecito"
OUT_DIR = REPO_ROOT / "outputs" / "cafecito"
FINAL_DIR = REPO_ROOT / "Cafesito" / "final"

CONTENIDO_YAML = DOCS_DIR / "contenido_editable_informe_cafecito_revision_1.yaml"

PDF_REV = OUT_DIR / "INFORME_CAFECITO_DATAGASTRO_REVISION_1.pdf"
FINAL_PDF_REV = FINAL_DIR / "INFORME_CAFECITO_DATAGASTRO_REVISION_1.pdf"

MAPA_SEDES = final.MAPA_SEDES
MAPA_COMBINADO = final.MAPA_COMBINADO

# Footer propio de la revisión (no toca el del módulo final globalmente más que
# durante la generación, igual que el editable).
FOOTER_REV = "DataGastro · DGDGAS · Cafecito BA en tu barrio · Resultados de encuestas"


# ----------------------------------------------------- preguntas del formulario
# Texto y objetivo extraídos del PDF "Formulario cafecito.pdf" (no inventado).
PREGUNTAS_FORMULARIO = [
    {
        "pregunta": "¿Cuál es tu rango de edad?",
        "tipo": "Cerrada, opción única",
        "objetivo": "Conocer la composición etaria del público para orientar la comunicación y la divulgación de los eventos.",
    },
    {
        "pregunta": "¿Con qué género te identificás?",
        "tipo": "Cerrada, opción única",
        "objetivo": "Sumar información general sobre la composición del público asistente y la llegada del evento por género.",
    },
    {
        "pregunta": "¿Dónde vivís actualmente? Indicanos tu barrio o localidad",
        "tipo": "Abierta (se presenta agregada)",
        "objetivo": "Entender el alcance territorial del evento y la relación entre su ubicación y la residencia del público.",
    },
    {
        "pregunta": "¿Es la primera vez que venís a un evento gastronómico de la Ciudad?",
        "tipo": "Cerrada, opción única",
        "objetivo": "Conocer qué proporción del público asiste por primera vez y qué proporción ya había participado.",
    },
    {
        "pregunta": "¿Con quién viniste al evento?",
        "tipo": "Cerrada, opción única",
        "objetivo": "Conocer cómo se organiza la asistencia: en pareja, con amigos, con familia u otros grupos.",
    },
    {
        "pregunta": "¿Cómo te enteraste del evento?",
        "tipo": "Multi-respuesta",
        "objetivo": "Evaluar qué canales de comunicación tienen mayor alcance y efectividad para la difusión.",
    },
    {
        "pregunta": "¿Qué fue lo que más te interesó del evento?",
        "tipo": "Cerrada, opción única",
        "objetivo": "Identificar los principales atractivos del evento desde la perspectiva del público.",
    },
    {
        "pregunta": "¿Qué tipo de eventos gastronómicos te interesa que se realicen próximamente?",
        "tipo": "Multi-respuesta",
        "objetivo": "Conocer los intereses del público como insumo para pensar formatos y temáticas futuras.",
    },
    {
        "pregunta": "¿Aceptás recibir información sobre próximos eventos y novedades gastronómicas de la Ciudad?",
        "tipo": "Consentimiento / contacto",
        "objetivo": "Identificar quiénes desean recibir información para construir una base de contactos, con su consentimiento.",
    },
]


# ---------------------------------------------------------- franjas horarias
EXCEL_EPOCH = datetime(1899, 12, 30)
FRANJAS = ["Mañana (10–12)", "Mediodía (12–14)", "Tarde (14–18)"]
DIAS_NOMBRE = {5: "Sábado", 6: "Domingo", 0: "Lunes", 1: "Martes", 2: "Miércoles", 3: "Jueves", 4: "Viernes"}


def franja_de(dt: datetime) -> str:
    h = dt.hour + dt.minute / 60
    if h < 12:
        return FRANJAS[0]
    if h < 14:
        return FRANJAS[1]
    return FRANJAS[2]


def respuestas_por_dia_franja(records: list[dict]) -> tuple[list[dict], int]:
    """Agrega respuestas por día y franja a partir de las marcas temporales.

    Solo produce conteos AGREGADOS (no expone marcas temporales individuales).
    Devuelve (filas, con_timestamp). Si no hay timestamps utilizables, filas
    queda vacío y el informe lo documenta sin inventar.
    """
    por_dia: dict[datetime.date, Counter] = defaultdict(Counter)
    con_ts = 0
    for r in records:
        raw = (r.get("marca_temporal", "") or "").strip()
        if not raw:
            continue
        try:
            dt = EXCEL_EPOCH + timedelta(days=float(raw))
        except ValueError:
            continue
        con_ts += 1
        por_dia[dt.date()][franja_de(dt)] += 1
    filas = []
    for dia in sorted(por_dia):
        c = por_dia[dia]
        filas.append({
            "dia": f"{DIAS_NOMBRE.get(dia.weekday(), '')} {dia.day}/{dia.month}",
            "franjas": {f: c.get(f, 0) for f in FRANJAS},
            "total": sum(c.values()),
        })
    return filas, con_ts


# --------------------------------------------------------------- numeros %
def number_context(p: dict, stats: dict, ranking_rows: list[dict], sedes_comuna: list[dict]) -> dict:
    """Diccionario de marcadores {clave} con porcentajes ya formateados."""
    edad = items_dict(stats, "rango_edad")
    base_edad = stats["rango_edad"]["base"]
    p1844 = edad.get("18 a 24", 0) + edad.get("25 a 34", 0) + edad.get("35 a 44", 0)
    gen = items_dict(stats, "genero")
    res = items_dict(stats, "donde_vivis")
    canal = items_dict(stats, "como_se_entero")
    base_canal = stats["como_se_entero"]["base"]
    interes = items_dict(stats, "que_intereso")
    base_int = stats["que_intereso"]["base"]
    futuro = items_dict(stats, "eventos_futuros")
    base_fut = stats["eventos_futuros"]["base"]
    primera = items_dict(stats, "primera_vez")
    base_pv = stats["primera_vez"]["base"]
    plan = items_dict(stats, "con_quien")
    base_plan = stats["con_quien"]["base"]

    def P(n, d):
        return f"{pct(n, d):.0f}%"

    return {
        "n": p["n"],
        "sigla": "DGDGAS",
        "nombre": "Dirección General de Desarrollo Gastronómico",
        # perfil
        "edad_top_pct": P(edad.get("25 a 34", 0), base_edad),
        "p1844_pct": P(p1844, base_edad),
        "mujer_pct": P(gen.get("Mujer", 0), stats["genero"]["base"]),
        # residencia
        "caba_pct": P(res.get("CABA", 0), stats["donde_vivis"]["base"]),
        # vinculo
        "recurrente_pct": P(primera.get("No, ya participé de otros eventos", 0), base_pv),
        "primera_pct": P(primera.get("Si, es la primera vez", 0), base_pv),
        "contacto_pct": P(p["contact_yes"], p["contact_base"]),
        # canales
        "instagram_pct": P(canal.get("Instagram", 0), base_canal),
        "amigos_pct": P(canal.get("Por amigos, familia o conocidos", 0), base_canal),
        "paso_pct": P(canal.get("Pase por la zona y lo ví", 0), base_canal),
        # acompanamiento / motivaciones
        "pareja_pct": P(plan.get("En pareja", 0), base_plan),
        "amigos_acomp_pct": P(plan.get("Con amigos/as", 0), base_plan),
        "familia_pct": P(plan.get("Con familia", 0), base_plan),
        "cafe_pct": P(interes.get("Probar café / cafeterías", 0), base_int),
        "paseo_pct": P(interes.get("Pasear o hacer una salida", 0), base_int),
        # intereses futuros
        "vino_pct": P(futuro.get("Vino", 0), base_fut),
        "pasteleria_pct": P(futuro.get("Pasteleria", 0), base_fut),
        "food_trucks_pct": P(futuro.get("Food trucks", 0), base_fut),
        "cafe_futuro_pct": P(futuro.get("Café", 0), base_fut),
        "ferias_pct": P(futuro.get("Ferias y mercados", 0), base_fut),
    }


# ----------------------------------------------------------- helpers dibujo
def footer(fig) -> None:
    fig.lines.append(Line2D([0.065, 0.935], [0.055, 0.055], color=LINE, lw=0.8, transform=fig.transFigure))
    fig.text(0.065, 0.035, FOOTER_REV, color=GREY, fontsize=7.8, va="center")


def hbar_pct(fig, rect, items, base_n, title, *, color=BLUE, accents=None, limit=None, multi=False):
    """Barras horizontales con etiquetas en PORCENTAJE (formato principal)."""
    accents = accents or set()
    chosen = items[:limit] if limit else items
    chosen = list(reversed(chosen))
    labels = ["\n".join(wrap_text(final.DISPLAY.get(label, label), 18)) for label, _ in chosen]
    values = [v for _, v in chosen]
    colors = [ORANGE if label in accents else color for label, _ in chosen]
    ax = fig.add_axes(rect)
    ypos = list(range(len(chosen)))
    ax.barh(ypos, values, color=colors, height=0.62)
    final.style_axis(ax)
    ax.set_yticks([])
    max_v = max(values) if values else 1
    label_x = -max_v * 0.66
    for i, label in enumerate(labels):
        ax.text(label_x * 0.96, i, label, va="center", ha="left", color="#222222", fontsize=7.4)
    for i, value in enumerate(values):
        ax.text(value + max_v * 0.025, i, f"{pct_s(value, base_n)}", va="center", color=INK, fontsize=7.8, fontweight="bold")
    ax.axvline(0, color=LINE, lw=0.8)
    ax.set_xlim(label_x * 1.10, max_v * 1.20)
    ax.set_title(clean_text(title), loc="left", fontsize=10.5, color=INK, fontweight="bold", pad=12)
    note = f"Base: {base_n} respuestas" + (" · multi-respuesta (los % pueden superar 100%)" if multi else "")
    ax.text(0, -0.16, clean_text(note), transform=ax.transAxes, fontsize=7.4, color=GREY, va="top")


def question_block(fig, x, y_top, w, pregunta, tipo, observa, *, body_size=8.6):
    """Bloque previo a un gráfico: pregunta analizada + tipo + qué observa.

    La caja se dibuja con altura dinámica según el texto, anclada arriba en
    y_top (el borde superior queda en y_top), para no desbordar ni solaparse
    con el gráfico que va debajo. Devuelve el y del borde inferior de la caja.
    """
    line_h = 0.0165
    wrap_w = int(w * 130)
    bloques = [(pregunta, True), (tipo, False), (observa, False)]
    n_lines = sum(len(wrap_text(t, wrap_w)) for t, _ in bloques)
    h = 0.018 + line_h * n_lines
    y = y_top - h
    fig.patches.append(Rectangle((x, y), w, h, transform=fig.transFigure,
                                 facecolor=SOFT_BLUE, edgecolor=BLUE, lw=1.0))
    yy = y_top - 0.016
    for txt, bold in bloques:
        for line in wrap_text(txt, wrap_w):
            fig.text(x + 0.013, yy, line, color=INK if bold else "#333333",
                     fontsize=body_size, fontweight="bold" if bold else "normal", va="top")
            yy -= line_h
    return y


def descriptive_lines(fig, x, y, w, text, *, fontsize=9.2, color="#222222"):
    """Párrafo descriptivo en oraciones completas."""
    yy = y
    for line in wrap_text(text, int(w * 118)):
        fig.text(x, yy, line, color=color, fontsize=fontsize, va="top")
        yy -= 0.0175
    return yy


# --------------------------------------------------------------------- páginas
def cover_page(pdf, c, inst, ev):
    fig = page()
    fig.patches.append(Rectangle((0, 0.70), 1, 0.30, transform=fig.transFigure, facecolor=INK, edgecolor="none"))
    fig.patches.append(Rectangle((0, 0.688), 1, 0.012, transform=fig.transFigure, facecolor=ORANGE, edgecolor="none"))
    fig.text(0.065, 0.93, c["kicker_marca"], color=WHITE, fontsize=13, fontweight="bold")
    fig.text(0.935, 0.93, c["kicker_tipo"], color="#c9d6e4", fontsize=10, ha="right")
    fig.text(0.065, 0.84, c["titulo"], color=WHITE, fontsize=34, fontweight="bold", va="top", linespacing=0.95)
    fig.text(0.065, 0.728, c["subtitulo"], color="#dbe5ef", fontsize=12.5, va="center")
    # Descripción en oraciones completas.
    descriptive_lines(fig, 0.065, 0.625, 0.87, c["descripcion"], fontsize=11.0, color=INK)
    # Ficha de evento (qué, dónde, cuándo, marco).
    fig.lines.append(Line2D([0.065, 0.55], [0.515, 0.515], color=LINE, lw=1.2, transform=fig.transFigure))
    datos = [
        ("Evento", ev["nombre"]),
        ("Lugar", f"{ev['lugar']} ({ev['direccion']})"),
        ("Fechas", f"{ev['fecha_sabado']}; {ev['fecha_domingo']}"),
        ("Marco", inst["marco"]),
        ("Presenta", f"{inst['sigla']} – {inst['nombre']}"),
    ]
    y = 0.470
    for k, v in datos:
        fig.text(0.065, y, k, color=ORANGE, fontsize=10, fontweight="bold", va="top")
        yy = y
        for line in wrap_text(v, 78):
            fig.text(0.205, yy, line, color="#222222", fontsize=10, va="top")
            yy -= 0.020
        y = min(yy, y - 0.020) - 0.008
    # Fecha del documento, discreta.
    fig.text(0.065, 0.115, c.get("pie_institucional", ""), color=GREY, fontsize=9.5, va="center")
    fig.text(0.065, 0.090, f"{ev['entrada']}.", color=GREY, fontsize=9.5, va="center")
    footer(fig)
    pdf.savefig(fig)
    final.plt.close(fig)


def index_page(pdf, c, fecha_doc, page_no):
    fig = page()
    header(fig, page_no, c["titulo"], c["subtitulo"])
    y = 0.800
    for i, entrada in enumerate(c["entradas"], 1):
        fig.text(0.075, y, f"{i}.", color=ORANGE, fontsize=11, fontweight="bold", va="top")
        fig.text(0.115, y, clean_text(entrada), color=INK, fontsize=11, va="top")
        # línea de guía punteada sutil
        fig.lines.append(Line2D([0.075, 0.935], [y - 0.012, y - 0.012], color=LINE, lw=0.5,
                                linestyle=(0, (1, 3)), transform=fig.transFigure))
        y -= 0.046
    fig.text(0.065, 0.075, f"{c['titulo']} · {fecha_doc}", color=GREY, fontsize=8.5, va="center")
    footer(fig)
    pdf.savefig(fig)
    final.plt.close(fig)


def general_data_page(pdf, c, inst, ev, filas, con_ts, n_total, page_no):
    fig = page()
    header(fig, page_no, c["titulo"], c["subtitulo"])
    # Ficha del relevamiento (datos duros).
    ficha = [
        ("Evento", ev["nombre"]),
        ("Lugar", ev["lugar"]),
        ("Dirección", ev["direccion"]),
        ("Sábado", ev["fecha_sabado"]),
        ("Domingo", ev["fecha_domingo"]),
        ("Respuestas obtenidas", f"{n_total}"),
        ("Modalidad", "Encuesta en formulario digital"),
        ("Presenta", f"{inst['sigla']} – {inst['nombre']}"),
    ]
    x, y, w, h = 0.065, 0.560, 0.87, 0.250
    fig.patches.append(Rectangle((x, y), w, h, transform=fig.transFigure, facecolor=LIGHT, edgecolor=BLUE, lw=1.1))
    fig.text(x + 0.015, y + h - 0.022, clean_text(c["ficha_titulo"]), color=INK, fontsize=10.5, fontweight="bold", va="top")
    yy = y + h - 0.050
    for k, v in ficha:
        fig.text(x + 0.015, yy, k, color=ORANGE, fontsize=8.8, fontweight="bold", va="top")
        for line in wrap_text(v, 70):
            fig.text(x + 0.255, yy, line, color="#222222", fontsize=8.8, va="top")
            yy -= 0.0175
        yy -= 0.004
    # Modalidad (oración completa).
    descriptive_lines(fig, 0.065, 0.530, 0.87, c["modalidad_texto"], fontsize=9.0)
    # Tabla respuestas por día y franja.
    fig.text(0.065, 0.455, clean_text(c["distribucion_titulo"]), color=INK, fontsize=11, fontweight="bold", va="top")
    descriptive_lines(fig, 0.065, 0.432, 0.87, c["distribucion_intro"], fontsize=8.8, color="#333333")
    if filas:
        _draw_franja_table(fig, filas, x=0.065, y=0.250, w=0.87, h=0.150)
        ny = 0.230
        for line in wrap_text(c["nota_sabado"], 120):
            fig.text(0.065, ny, clean_text(line), color=GREY, fontsize=8.0, va="top")
            ny -= 0.016
    else:
        descriptive_lines(fig, 0.065, 0.380, 0.87,
                          "No fue posible desagregar las respuestas por día y franja horaria a partir de los datos disponibles.",
                          fontsize=9.0)
    footer(fig)
    pdf.savefig(fig)
    final.plt.close(fig)


def _draw_franja_table(fig, filas, x, y, w, h):
    cols = ["Día"] + FRANJAS + ["Total"]
    ncol = len(cols)
    col_w = [0.20, 0.20, 0.22, 0.20, 0.18]
    # encabezado
    row_h = h / (len(filas) + 1)
    cx = x
    yy = y + h - row_h
    fig.patches.append(Rectangle((x, yy), w, row_h, transform=fig.transFigure, facecolor=INK, edgecolor=WHITE, lw=0.6))
    for ci, col in enumerate(cols):
        fig.text(cx + w * col_w[ci] / 2, yy + row_h / 2, clean_text(col), color=WHITE, fontsize=8.0,
                 fontweight="bold", ha="center", va="center")
        cx += w * col_w[ci]
    # filas
    for ri, fila in enumerate(filas):
        yy = y + h - row_h * (ri + 2)
        face = LIGHT if ri % 2 == 0 else WHITE
        fig.patches.append(Rectangle((x, yy), w, row_h, transform=fig.transFigure, facecolor=face, edgecolor=LINE, lw=0.5))
        cx = x
        valores = [fila["dia"]] + [str(fila["franjas"][f]) for f in FRANJAS] + [str(fila["total"])]
        for ci, val in enumerate(valores):
            bold = (ci == 0) or (ci == ncol - 1)
            fig.text(cx + w * col_w[ci] / 2, yy + row_h / 2, clean_text(val),
                     color=INK if bold else "#222222", fontsize=8.2,
                     fontweight="bold" if bold else "normal", ha="center", va="center")
            cx += w * col_w[ci]


def questions_page_1(pdf, c, page_no):
    fig = page()
    header(fig, page_no, c["titulo"], c["subtitulo"])
    y_intro = descriptive_lines(fig, 0.065, 0.835, 0.87, c["intro"], fontsize=9.2, color="#333333")
    _draw_questions(fig, PREGUNTAS_FORMULARIO[:5], y_top=y_intro - 0.015)
    footer(fig)
    pdf.savefig(fig)
    final.plt.close(fig)


def questions_page_2(pdf, c, page_no):
    fig = page()
    header(fig, page_no, c["titulo"], c["subtitulo"])
    _draw_questions(fig, PREGUNTAS_FORMULARIO[5:], y_top=0.835)
    descriptive_lines(fig, 0.065, 0.175, 0.87, c["nota_pie"], fontsize=8.4, color=GREY)
    footer(fig)
    pdf.savefig(fig)
    final.plt.close(fig)


def _draw_questions(fig, preguntas, y_top):
    x, w = 0.065, 0.87
    y = y_top
    for i, q in enumerate(preguntas, 1):
        # altura estimada segun longitud del objetivo
        obj_lines = wrap_text(q["objetivo"], 108)
        preg_lines = wrap_text(q["pregunta"], 95)
        h = 0.030 + 0.018 * len(preg_lines) + 0.0165 * len(obj_lines)
        yy = y
        fig.patches.append(Rectangle((x, yy - h), w, h, transform=fig.transFigure,
                                     facecolor=WHITE, edgecolor=LINE, lw=0.8))
        fig.patches.append(Rectangle((x, yy - h), 0.006, h, transform=fig.transFigure,
                                     facecolor=ORANGE, edgecolor="none"))
        ty = yy - 0.020
        for j, line in enumerate(preg_lines):
            prefix = f"Pregunta {i}: " if j == 0 else ""
            fig.text(x + 0.018, ty, clean_text(prefix + line), color=INK, fontsize=9.2, fontweight="bold", va="top")
            ty -= 0.018
        fig.text(x + 0.018, ty, clean_text(f"Tipo: {q['tipo']}."), color=BLUE, fontsize=8.4, va="top")
        ty -= 0.017
        for line in obj_lines:
            fig.text(x + 0.018, ty, clean_text(line), color="#333333", fontsize=8.4, va="top")
            ty -= 0.0165
        y = yy - h - 0.012


def profile_page(pdf, c, stats, page_no):
    fig = page()
    header(fig, page_no, c["titulo"], c["subtitulo"])
    b1 = question_block(fig, 0.065, 0.770, 0.42, c["pregunta_edad"], c["tipo_edad"], c["observa_edad"])
    b2 = question_block(fig, 0.515, 0.770, 0.42, c["pregunta_genero"], c["tipo_genero"], c["observa_genero"])
    top = min(b1, b2) - 0.030
    hbar_pct(fig, [0.085, top - 0.255, 0.40, 0.255], stats["rango_edad"]["items"], stats["rango_edad"]["base"],
             "Rango de edad", accents={"25 a 34"})
    stacked(fig, [0.560, top - 0.060, 0.360, 0.072], stats["genero"]["items"], stats["genero"]["base"],
            "Género declarado", [INK, ORANGE, GREY])
    add_box(fig, 0.065, 0.150, 0.87, 0.180, "Lectura de resultados", c["lectura"],
            face=SOFT_BLUE, edge=BLUE, body_size=9.4)
    footer(fig)
    pdf.savefig(fig)
    final.plt.close(fig)


def residence_page(pdf, c, stats, page_no):
    fig = page()
    header(fig, page_no, c["titulo"], c["subtitulo"])
    b = question_block(fig, 0.065, 0.770, 0.87, c["pregunta"], c["tipo"], c["observa"])
    top = b - 0.035
    hbar_pct(fig, [0.150, top - 0.250, 0.42, 0.250], stats["donde_vivis"]["items"], stats["donde_vivis"]["base"],
             "Lugar de residencia declarado")
    add_box(fig, 0.065, 0.165, 0.87, 0.230, "Lectura de resultados", c["lectura"],
            face=SOFT_BLUE, edge=BLUE, body_size=9.4)
    footer(fig)
    pdf.savefig(fig)
    final.plt.close(fig)


def link_page(pdf, c, stats, p, page_no):
    fig = page()
    header(fig, page_no, c["titulo"], c["subtitulo"])
    b1 = question_block(fig, 0.065, 0.770, 0.42, c["pregunta_primera"], c["tipo_primera"], c["observa_primera"])
    b2 = question_block(fig, 0.515, 0.770, 0.42, c["pregunta_contacto"], c["tipo_contacto"], c["observa_contacto"])
    top = min(b1, b2) - 0.030
    stacked(fig, [0.085, top - 0.110, 0.420, 0.110], stats["primera_vez"]["items"], stats["primera_vez"]["base"],
            "Primera vez o ya había participado", [INK, ORANGE, GREY])
    donut(fig, [0.585, top - 0.195, 0.250, 0.210], stats["acepta_contacto"]["items"], "Acepta recibir información",
          f"{pct_s(p['contact_yes'], p['contact_base'])}", [GREEN, GREY])
    add_box(fig, 0.065, 0.165, 0.87, 0.200, "Lectura de resultados", c["lectura"],
            face=SOFT_BLUE, edge=BLUE, body_size=9.4)
    footer(fig)
    pdf.savefig(fig)
    final.plt.close(fig)


def channels_page(pdf, c, stats, page_no):
    fig = page()
    header(fig, page_no, c["titulo"], c["subtitulo"])
    b = question_block(fig, 0.065, 0.770, 0.87, c["pregunta"], c["tipo"], c["observa"])
    top = b - 0.035
    hbar_pct(fig, [0.135, top - 0.290, 0.55, 0.290], stats["como_se_entero"]["items"], stats["como_se_entero"]["base"],
             "Cómo se enteraron del evento", color=BLUE,
             accents={"Instagram"}, multi=True)
    add_box(fig, 0.065, 0.150, 0.87, 0.180, "Lectura de resultados", c["lectura"],
            face=SOFT_BLUE, edge=BLUE, body_size=9.4)
    footer(fig)
    pdf.savefig(fig)
    final.plt.close(fig)


def company_motivation_page(pdf, c, stats, page_no):
    fig = page()
    header(fig, page_no, c["titulo"], c["subtitulo"])
    b1 = question_block(fig, 0.065, 0.770, 0.42, c["pregunta_con_quien"], c["tipo_con_quien"], c["observa_con_quien"])
    b2 = question_block(fig, 0.515, 0.770, 0.42, c["pregunta_intereso"], c["tipo_intereso"], c["observa_intereso"])
    top = min(b1, b2) - 0.030
    hbar_pct(fig, [0.130, top - 0.260, 0.34, 0.260], stats["con_quien"]["items"], stats["con_quien"]["base"],
             "Con quién asistió", accents={"En pareja"})
    hbar_pct(fig, [0.610, top - 0.260, 0.33, 0.260], stats["que_intereso"]["items"], stats["que_intereso"]["base"],
             "Qué fue lo que más le interesó", color=final.COFFEE, accents={"Probar café / cafeterías"})
    add_box(fig, 0.065, 0.150, 0.87, 0.180, "Lectura de resultados", c["lectura"],
            face=SOFT_BLUE, edge=BLUE, body_size=9.4)
    footer(fig)
    pdf.savefig(fig)
    final.plt.close(fig)


def interests_page(pdf, c, stats, page_no):
    fig = page()
    header(fig, page_no, c["titulo"], c["subtitulo"])
    b = question_block(fig, 0.065, 0.770, 0.87, c["pregunta"], c["tipo"], c["observa"])
    top = b - 0.035
    hbar_pct(fig, [0.150, top - 0.370, 0.42, 0.370], stats["eventos_futuros"]["items"], stats["eventos_futuros"]["base"],
             "Intereses para próximas ediciones", color=BLUE, limit=8, multi=True)
    add_box(fig, 0.065, 0.150, 0.87, 0.160, "Lectura de resultados", c["lectura"],
            face=SOFT_BLUE, edge=BLUE, body_size=9.2)
    footer(fig)
    pdf.savefig(fig)
    final.plt.close(fig)


def synthesis_page(pdf, c, page_no):
    fig = page()
    header(fig, page_no, c["titulo"], c["subtitulo"])
    descriptive_lines(fig, 0.065, 0.820, 0.87, c["intro"], fontsize=10.0, color=INK)
    yy = 0.770
    for punto in c["puntos"]:
        lines = wrap_text("•  " + punto, 100)
        for line in lines:
            fig.text(0.075, yy, line, color="#222222", fontsize=9.8, va="top")
            yy -= 0.020
        yy -= 0.010
    add_box(fig, 0.065, 0.130, 0.87, 0.110, "Sobre estos resultados", c["nota"],
            face=LIGHT, edge=GREY, body_size=8.8, title_color=GREY)
    footer(fig)
    pdf.savefig(fig)
    final.plt.close(fig)


def considerations_page(pdf, c, page_no):
    fig = page()
    header(fig, page_no, c["titulo"], c["subtitulo"])
    descriptive_lines(fig, 0.065, 0.820, 0.87, c["intro"], fontsize=10.0, color=INK)
    yy = 0.760
    for punto in c["puntos"]:
        lines = wrap_text("•  " + punto, 98)
        for line in lines:
            fig.text(0.075, yy, line, color="#222222", fontsize=9.8, va="top")
            yy -= 0.020
        yy -= 0.012
    add_box(fig, 0.065, 0.135, 0.87, 0.100, "Alcance de estas consideraciones", c["nota"],
            face=SOFT_ORANGE, edge=ORANGE, body_size=8.8)
    footer(fig)
    pdf.savefig(fig)
    final.plt.close(fig)


def annex_network_page(pdf, c, sedes_comuna, page_no):
    fig = page()
    header(fig, page_no, c["titulo"], c["subtitulo"])
    y_intro = descriptive_lines(fig, 0.065, 0.825, 0.87, c["intro"], fontsize=9.0, color="#333333")
    top = y_intro - 0.030
    add_image(fig, MAPA_SEDES, [0.060, top - 0.300, 0.45, 0.300], c["mapa_sedes_titulo"])
    add_image(fig, MAPA_COMBINADO, [0.520, top - 0.300, 0.45, 0.300], c["mapa_combinado_titulo"])
    add_box(fig, 0.065, 0.300, 0.42, 0.130, c["en_numeros_titulo"], c["en_numeros"],
            face=WHITE, edge=BLUE, bullet=True, body_size=8.4)
    top = [r for r in sedes_comuna if str(r["comuna"]).isdigit()][:5]
    top_txt = ", ".join(f"Comuna {r['comuna']} ({r['cantidad_sedes']})" for r in top)
    add_box(fig, 0.515, 0.300, 0.42, 0.130, "Comunas con más sedes",
            f"{top_txt}.", face=SOFT_BLUE, edge=BLUE, body_size=8.6)
    add_box(fig, 0.065, 0.150, 0.87, 0.120, "Nota sobre esta lectura", c["nota_prudente"],
            face=SOFT_ORANGE, edge=ORANGE, body_size=9.0)
    footer(fig)
    pdf.savefig(fig)
    final.plt.close(fig)


# ----------------------------------------------------------------------- build
def write_pdf(content, records, stats, p, ranking_rows, sedes_comuna, filas, con_ts):
    pages = content["paginas"]
    inst = content["institucion"]
    ev = content["evento"]
    fecha_doc = content.get("fecha_documento", "")
    numbers = number_context(p, stats, ranking_rows, sedes_comuna)
    # mezclar institucion en numbers para marcadores {sigla}/{nombre} de portada
    numbers = {**numbers, **inst}

    def pc(key):
        return {k: fmt(v, numbers) for k, v in pages[key].items()}

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    with PdfPages(PDF_REV) as pdf:
        cover_page(pdf, pc("portada"), inst, ev)
        index_page(pdf, pc("indice"), fecha_doc, 2)
        general_data_page(pdf, pc("datos_generales"), inst, ev, filas, con_ts, p["n"], 3)
        questions_page_1(pdf, pc("preguntas_1"), 4)
        questions_page_2(pdf, pc("preguntas_2"), 5)
        profile_page(pdf, pc("perfil"), stats, 6)
        residence_page(pdf, pc("residencia"), stats, 7)
        link_page(pdf, pc("vinculo"), stats, p, 8)
        channels_page(pdf, pc("canales"), stats, 9)
        company_motivation_page(pdf, pc("acompanamiento"), stats, 10)
        interests_page(pdf, pc("intereses"), stats, 11)
        synthesis_page(pdf, pc("sintesis"), 12)
        considerations_page(pdf, pc("aspectos"), 13)
        annex_network_page(pdf, pc("anexo_red"), sedes_comuna, 14)
    shutil.copy2(PDF_REV, FINAL_PDF_REV)
    return 14


def main():
    if not CONTENIDO_YAML.exists():
        raise SystemExit(f"No se encontró el contenido editable: {CONTENIDO_YAML}")
    content = _load_yaml(CONTENIDO_YAML)

    final.ensure_analysis_outputs()
    records = final.base.read_xlsx(final.base.XLSX)
    stats = final.build_stats(records)
    p = final.stats_payload(records, stats)
    ranking_rows = final.read_csv(final.RANKING_COMUNAL)
    sedes_comuna = final.read_csv(final.RESUMEN_SEDES_COMUNA)
    sedes_all = final.read_csv(final.SEDES_CSV)
    sedes_mapa = [s for s in sedes_all if s.get("usar_en_mapa", "").strip() == "si"]

    # Mapas del anexo: se generan idénticos a los del final (mismas rutas PNG).
    final.draw_mapa_comunal_publico(ranking_rows)
    final.draw_mapa_sedes(sedes_mapa)
    final.draw_mapa_combinado(sedes_mapa, ranking_rows)

    filas, con_ts = respuestas_por_dia_franja(records)

    pages = write_pdf(content, records, stats, p, ranking_rows, sedes_comuna, filas, con_ts)

    print("=" * 72)
    print("Informe Cafecito DataGastro · REVISIÓN 1")
    print(f"  Contenido editable: {CONTENIDO_YAML.relative_to(REPO_ROOT)}")
    print(f"  Respuestas: {len(records)}  ·  con marca temporal: {con_ts}")
    if filas:
        for f in filas:
            print(f"    {f['dia']}: total {f['total']}  -> " +
                  ", ".join(f"{k.split(' ')[0]} {v}" for k, v in f['franjas'].items()))
    print(f"  Páginas PDF: {pages}")
    print(f"  PDF revisión: {PDF_REV.relative_to(REPO_ROOT)}")
    print(f"  Copia: {FINAL_PDF_REV.relative_to(REPO_ROOT)}")
    print("  (El PDF FINAL original y el EDITABLE_TEST NO fueron modificados.)")
    print("=" * 72)


if __name__ == "__main__":
    main()
