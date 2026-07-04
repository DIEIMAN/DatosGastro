"""Genera el informe Cafecito · REVISIÓN 3 (DGDGAS).

Tercera revisión sobre la revisión 2 · formato. Aplica:

  - Numeración de secciones (1 a 12) coherente con el índice; subsecciones
    simples (1.1, 1.2, 2.1 implícita, 4.1, 4.2) donde aporta claridad.
  - Página de residencia con un top 5 agregado de barrios/localidades
    (normalización mínima: mayúsculas/tildes; las menciones únicas se agrupan
    como "Otras respuestas"; no se publican respuestas individuales).
  - Explicación completa de las preguntas multi-respuesta (canales e intereses),
    con menciones por opción en las etiquetas: "57% (45)".
  - Bases de gráfico siempre fuera de las cajas de lectura.

Mantiene marca DGDGAS (no DataGastro), enfoque de resultados de encuesta,
porcentajes, lectura descriptiva y recomendaciones en potencial.

Reglas del PDF público: sin rutas, scripts, hashes, versiones internas ni datos
personales. El público se muestra agregado.

NO sobrescribe el FINAL, el EDITABLE_TEST ni las revisiones 1, 2 o 2·formato.

Salidas:
  - outputs/cafecito/INFORME_CAFECITO_DGDGAS_REVISION_3.pdf
  - Cafesito/final/INFORME_CAFECITO_DGDGAS_REVISION_3.pdf

Uso:
    python scripts/cafecito/generar_informe_cafecito_revision_3.py
"""
from __future__ import annotations

import re
import shutil
import sys
import unicodedata
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.cafecito import generar_informe_datagastro_final as final  # noqa: E402
from scripts.cafecito.generar_informe_datagastro_final_editable import _load_yaml, fmt  # noqa: E402
from scripts.cafecito.generar_informe_datagastro_final import (  # noqa: E402
    INK, ORANGE, GREEN, BLUE, GREY, WHITE, LIGHT, LINE,
    SOFT_BLUE, SOFT_ORANGE, SOFT_GREEN,
    add_box, add_image, clean_text, donut, items_dict, page, pct, pct_s, stacked, wrap_text,
)
from scripts.cafecito.generar_informe_datagastro_final import header as _base_header  # noqa: E402
from scripts.cafecito.generar_informe_datagastro_revision_1 import (  # noqa: E402
    FRANJAS, PREGUNTAS_FORMULARIO,
    number_context, respuestas_por_dia_franja, descriptive_lines, _draw_franja_table,
)

DOCS_DIR = REPO_ROOT / "docs" / "cafecito"
OUT_DIR = REPO_ROOT / "outputs" / "cafecito"
FINAL_DIR = REPO_ROOT / "Cafesito" / "final"

CONTENIDO_YAML = DOCS_DIR / "contenido_editable_informe_cafecito_revision_3.yaml"

PDF_REV = OUT_DIR / "INFORME_CAFECITO_DGDGAS_REVISION_3.pdf"
FINAL_PDF_REV = FINAL_DIR / "INFORME_CAFECITO_DGDGAS_REVISION_3.pdf"

MAPA_SEDES = final.MAPA_SEDES
MAPA_COMBINADO = final.MAPA_COMBINADO

KICKER = "DGDGAS"
FOOTER_REV3 = "DGDGAS · Cafecito BA en tu barrio · Resultados de encuestas"


# ------------------------------------------------------- header / footer DGDGAS
def header(fig, page_no, title, subtitle=""):
    return _base_header(fig, page_no, title, subtitle, kicker=KICKER)


def footer(fig):
    fig.lines.append(Line2D([0.065, 0.935], [0.055, 0.055], color=LINE, lw=0.8, transform=fig.transFigure))
    fig.text(0.065, 0.035, FOOTER_REV3, color=GREY, fontsize=7.8, va="center")


# --------------------------------------------------- top de barrios/localidades
# Display preferido para los barrios/localidades más frecuentes (capitalización
# y tildes correctas). Solo afecta cómo se MUESTRA un valor ya agregado; no
# inventa ni reasigna respuestas.
BARRIO_DISPLAY = {
    "belgrano": "Belgrano",
    "caballito": "Caballito",
    "nunez": "Núñez",
    "saavedra": "Saavedra",
    "palermo": "Palermo",
    "san fernando": "San Fernando",
    "recoleta": "Recoleta",
    "mataderos": "Mataderos",
    "floresta": "Floresta",
}


def _norm_barrio(s: str) -> str:
    """Normalización mínima y segura: trim, colapsar espacios, minúsculas, sin
    tildes. No corrige ortografía ni agrupa variantes dudosas."""
    s = re.sub(r"\s+", " ", (s or "").strip()).lower()
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    return s


def top_barrios(records: list[dict], top_n: int = 5, min_freq: int = 2):
    """Top agregado de barrios/localidades declarados.

    Devuelve (filas, total, otras) donde filas = [(display, n, pct)] del top_n,
    o None si no hay datos suficientes / hay riesgo de exposición.
    Solo se incluyen valores con frecuencia >= min_freq (agregados, no
    individuos); el resto se cuenta como "Otras respuestas".
    """
    vals = [r.get("barrio_localidad", "").strip() for r in records]
    nonblank = [v for v in vals if v]
    if len(nonblank) < 20:
        return None
    counts = Counter(_norm_barrio(v) for v in nonblank)
    total = len(nonblank)
    top = [(k, n) for k, n in counts.most_common() if n >= min_freq][:top_n]
    if not top:
        return None
    filas = []
    suma = 0
    for k, n in top:
        disp = BARRIO_DISPLAY.get(k, k.title())
        filas.append((disp, n, pct(n, total)))
        suma += n
    otras = total - suma
    return filas, total, otras


# -------------------------------------------------- helpers de layout (formato)
def question_block(fig, x, y_top, w, pregunta, tipo, observa, *, body_size=8.6):
    """Pregunta + tipo + qué observa, anclado arriba en y_top. Wrap calibrado al
    ancho real de la caja. Altura dinámica. Devuelve el y del borde inferior."""
    line_h = 0.0165
    pad = 0.013
    wrap_w = max(20, int((w - 2 * pad) * 100))
    bloques = [(pregunta, True), (tipo, False), (observa, False)]
    n_lines = sum(len(wrap_text(t, wrap_w)) for t, _ in bloques)
    h = 0.020 + line_h * n_lines
    y = y_top - h
    fig.patches.append(Rectangle((x, y), w, h, transform=fig.transFigure,
                                 facecolor=SOFT_BLUE, edgecolor=BLUE, lw=1.0))
    yy = y_top - 0.017
    for txt, bold in bloques:
        for line in wrap_text(txt, wrap_w):
            fig.text(x + pad, yy, line, color=INK if bold else "#333333",
                     fontsize=body_size, fontweight="bold" if bold else "normal", va="top")
            yy -= line_h
    return y


def hbar_pct(fig, rect, items, base_n, title, *, color=BLUE, accents=None,
             limit=None, multi=False, label_wrap=18, show_mentions=False):
    """Barras horizontales con etiquetas en PORCENTAJE.

    Si show_mentions=True (preguntas multi-respuesta) la etiqueta muestra el
    porcentaje y las menciones: "57% (45)". La nota de "Base" se dibuja en
    coordenadas de FIGURA, debajo del gráfico, nunca dentro de la caja de lectura.
    """
    accents = accents or set()
    chosen = items[:limit] if limit else items
    chosen = list(reversed(chosen))
    labels = ["\n".join(wrap_text(final.DISPLAY.get(label, label), label_wrap)) for label, _ in chosen]
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
        etiqueta = f"{pct_s(value, base_n)} ({value})" if show_mentions else pct_s(value, base_n)
        ax.text(value + max_v * 0.025, i, etiqueta, va="center",
                color=INK, fontsize=7.6, fontweight="bold")
    ax.axvline(0, color=LINE, lw=0.8)
    ax.set_xlim(label_x * 1.10, max_v * 1.30)
    ax.set_title(clean_text(title), loc="left", fontsize=10.5, color=INK, fontweight="bold", pad=12)
    if multi:
        note = f"Base: {base_n} respuestas · pregunta multi-respuesta: se muestran menciones por opción."
    else:
        note = f"Base: {base_n} respuestas."
    rx, ry, rw, rh = rect
    fig.text(rx, ry - 0.020, clean_text(note), fontsize=7.4, color=GREY, va="top")


def lectura_box(fig, x, y_bottom, w, text, *, title="Lectura de resultados",
                face=SOFT_BLUE, edge=BLUE, body_size=9.4, min_h=0.075):
    """Caja de lectura con altura ajustada al texto. Devuelve el y del borde superior."""
    wrap_w = int((w - 0.030) * 118)
    lines = wrap_text(text, wrap_w)
    h = max(min_h, 0.030 + 0.017 * len(lines) + 0.022)
    add_box(fig, x, y_bottom, w, h, title, text, face=face, edge=edge, body_size=body_size)
    return y_bottom + h


def mini_top_table(fig, x, y_top, w, filas, otras, total, *, titulo, nota):
    """Tabla compacta del top de barrios/localidades: nombre · % · (n).
    Anclada arriba en y_top; devuelve el y del borde inferior."""
    fig.text(x, y_top, clean_text(titulo), color=INK, fontsize=10.5, fontweight="bold", va="top")
    row_h = 0.030
    y = y_top - 0.026
    filas_disp = list(filas) + [("Otras respuestas", otras, pct(otras, total))]
    for i, (nombre, n, p) in enumerate(filas_disp):
        face = LIGHT if i % 2 == 0 else WHITE
        es_otras = nombre == "Otras respuestas"
        fig.patches.append(Rectangle((x, y - row_h), w, row_h - 0.003, transform=fig.transFigure,
                                     facecolor=face, edgecolor=LINE, lw=0.5))
        fig.text(x + 0.012, y - row_h / 2 - 0.002, clean_text(nombre),
                 color=GREY if es_otras else INK, fontsize=8.6,
                 fontweight="normal" if es_otras else "bold", va="center")
        fig.text(x + w - 0.020, y - row_h / 2 - 0.002, f"{p:.0f}%  ({n})",
                 color="#222222", fontsize=8.6, va="center", ha="right")
        y -= row_h
    ny = y - 0.006
    for line in wrap_text(nota, int((w) * 118)):
        fig.text(x, ny, clean_text(line), color=GREY, fontsize=7.2, va="top")
        ny -= 0.013
    return ny


# --------------------------------------------------------------------- páginas
def cover_page(pdf, c, inst, ev):
    fig = page()
    fig.patches.append(Rectangle((0, 0.70), 1, 0.30, transform=fig.transFigure, facecolor=INK, edgecolor="none"))
    fig.patches.append(Rectangle((0, 0.688), 1, 0.012, transform=fig.transFigure, facecolor=ORANGE, edgecolor="none"))
    fig.text(0.065, 0.93, c["kicker_marca"], color=WHITE, fontsize=12, fontweight="bold")
    fig.text(0.935, 0.93, c["kicker_tipo"], color="#c9d6e4", fontsize=10, ha="right")
    fig.text(0.065, 0.84, c["titulo"], color=WHITE, fontsize=34, fontweight="bold", va="top", linespacing=0.95)
    fig.text(0.065, 0.728, c["subtitulo"], color="#dbe5ef", fontsize=12.5, va="center")
    descriptive_lines(fig, 0.065, 0.628, 0.87, c["descripcion"], fontsize=11.0, color=INK)
    fig.lines.append(Line2D([0.065, 0.55], [0.515, 0.515], color=LINE, lw=1.2, transform=fig.transFigure))
    datos = [
        ("Evento", ev["nombre"]),
        ("Lugar", ev["lugar"]),
        ("Dirección", ev["direccion"]),
        ("Fechas", f"{ev['fecha_sabado']}; {ev['fecha_domingo']}"),
        ("Presenta", f"{inst['sigla']} – {inst['nombre']}"),
    ]
    y = 0.470
    for k, v in datos:
        fig.text(0.065, y, k, color=ORANGE, fontsize=10.5, fontweight="bold", va="top")
        yy = y
        for line in wrap_text(v, 74):
            fig.text(0.215, yy, line, color="#222222", fontsize=10.5, va="top")
            yy -= 0.022
        y = min(yy, y - 0.022) - 0.012
    footer(fig)
    pdf.savefig(fig)
    final.plt.close(fig)


def index_page(pdf, c, fecha_doc, page_no):
    """Índice con numeración y subsecciones indentadas (sin recargar)."""
    fig = page()
    header(fig, page_no, c["titulo"], c["subtitulo"])
    y = 0.800
    for entrada in c["entradas"]:
        num = entrada.get("num", "")
        texto = entrada["texto"]
        pagina = entrada["pagina"]
        es_sub = str(entrada.get("sub", "")).strip().lower() in ("si", "sí", "true", "1")
        if es_sub:
            fig.text(0.115, y, f"{num}", color=GREY, fontsize=9.0, va="top")
            fig.text(0.165, y, clean_text(texto), color="#444444", fontsize=9.0, va="top")
            fig.text(0.930, y, str(pagina), color="#444444", fontsize=9.0, va="top", ha="right")
            fig.lines.append(Line2D([0.165, 0.915], [y - 0.011, y - 0.011], color=LINE, lw=0.5,
                                    linestyle=(0, (1, 3)), transform=fig.transFigure))
            y -= 0.032
        else:
            fig.text(0.075, y, f"{num}.", color=ORANGE, fontsize=10.5, fontweight="bold", va="top")
            fig.text(0.120, y, clean_text(texto), color=INK, fontsize=10.5, fontweight="bold", va="top")
            fig.text(0.930, y, str(pagina), color=INK, fontsize=10.5, fontweight="bold", va="top", ha="right")
            fig.lines.append(Line2D([0.120, 0.915], [y - 0.012, y - 0.012], color=LINE, lw=0.6,
                                    linestyle=(0, (1, 2.5)), transform=fig.transFigure))
            y -= 0.036
    fig.text(0.065, 0.075, f"{c['titulo']} · {fecha_doc}", color=GREY, fontsize=8.5, va="center")
    footer(fig)
    pdf.savefig(fig)
    final.plt.close(fig)


def general_data_page(pdf, c, inst, ev, filas, con_ts, n_total, page_no):
    fig = page()
    header(fig, page_no, c["titulo"], c["subtitulo"])
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
    descriptive_lines(fig, 0.065, 0.530, 0.87, c["modalidad_texto"], fontsize=9.0)
    fig.text(0.065, 0.455, clean_text(c["distribucion_titulo"]), color=INK, fontsize=11, fontweight="bold", va="top")
    descriptive_lines(fig, 0.065, 0.432, 0.87, c["distribucion_intro"], fontsize=8.8, color="#333333")
    if filas:
        _draw_franja_table(fig, filas, x=0.065, y=0.250, w=0.87, h=0.145)
    else:
        descriptive_lines(fig, 0.065, 0.380, 0.87,
                          "No fue posible desagregar las respuestas por día y franja horaria a partir de los datos disponibles.",
                          fontsize=9.0)
    footer(fig)
    pdf.savefig(fig)
    final.plt.close(fig)


def questions_page(pdf, c, page_no):
    fig = page()
    header(fig, page_no, c["titulo"], c["subtitulo"])
    descriptive_lines(fig, 0.065, 0.843, 0.87, c["intro"], fontsize=8.8, color="#333333")
    x, w = 0.065, 0.87
    col_preg_w = 0.40
    gap = 0.02
    x_obj = x + col_preg_w + gap
    nota_lines = wrap_text(c["nota_pie"], 150) if c.get("nota_pie") else []
    y_floor = 0.105 + 0.013 * len(nota_lines) + 0.010
    y = 0.805
    row_gap = 0.0105
    for i, q in enumerate(PREGUNTAS_FORMULARIO, 1):
        preg_lines = wrap_text(f"{i}. {q['pregunta']}", 46)
        tipo_line = f"Tipo: {q['tipo']}."
        obj_lines = wrap_text(q["objetivo"], 62)
        rows = max(len(preg_lines) + 1, len(obj_lines))
        h = 0.012 + 0.0150 * rows
        y_box = y - h
        face = "#f4f7fa" if i % 2 else WHITE
        fig.patches.append(Rectangle((x, y_box), w, h, transform=fig.transFigure,
                                     facecolor=face, edgecolor=LINE, lw=0.6))
        fig.patches.append(Rectangle((x, y_box), 0.005, h, transform=fig.transFigure,
                                     facecolor=ORANGE, edgecolor="none"))
        ty = y - 0.013
        for line in preg_lines:
            fig.text(x + 0.016, ty, clean_text(line), color=INK, fontsize=8.3, fontweight="bold", va="top")
            ty -= 0.0150
        fig.text(x + 0.016, ty, clean_text(tipo_line), color=BLUE, fontsize=7.9, va="top")
        ty = y - 0.013
        for line in obj_lines:
            fig.text(x_obj + 0.010, ty, clean_text(line), color="#333333", fontsize=8.0, va="top")
            ty -= 0.0150
        y = y_box - row_gap
    if nota_lines and (y - 0.010) > y_floor:
        ny = 0.116 + 0.013 * (len(nota_lines) - 1)
        for line in nota_lines:
            fig.text(0.065, ny, clean_text(line), color=GREY, fontsize=7.3, va="top")
            ny -= 0.013
    footer(fig)
    pdf.savefig(fig)
    final.plt.close(fig)


def profile_page(pdf, c, stats, page_no):
    fig = page()
    header(fig, page_no, c["titulo"], c["subtitulo"])
    bl = question_block(fig, 0.065, 0.775, 0.42, c["pregunta_edad"], c["tipo_edad"], c["observa_edad"])
    br = question_block(fig, 0.515, 0.775, 0.42, c["pregunta_genero"], c["tipo_genero"], c["observa_genero"])
    top = min(bl, br) - 0.050
    hbar_pct(fig, [0.090, top - 0.250, 0.39, 0.250], stats["rango_edad"]["items"], stats["rango_edad"]["base"],
             "Rango de edad", accents={"25 a 34"})
    stacked(fig, [0.560, top - 0.095, 0.360, 0.072], stats["genero"]["items"], stats["genero"]["base"],
            "Género declarado", [INK, ORANGE, GREY])
    lectura_box(fig, 0.065, 0.150, 0.87, c["lectura"])
    footer(fig)
    pdf.savefig(fig)
    final.plt.close(fig)


def residence_page(pdf, c, stats, barrios, page_no):
    """Residencia: pregunta + gráfico macro (izq) + top barrios (der) + lectura."""
    fig = page()
    header(fig, page_no, c["titulo"], c["subtitulo"])
    b = question_block(fig, 0.065, 0.780, 0.87, c["pregunta"], c["tipo"], c["observa"])
    top = b - 0.030
    # Columna izquierda: gráfico macro CABA/GBA/PBA/Otra provincia.
    fig.text(0.065, top, clean_text(c["macro_titulo"]), color=INK, fontsize=10.5, fontweight="bold", va="top")
    hbar_pct(fig, [0.130, top - 0.300, 0.34, 0.250], stats["donde_vivis"]["items"], stats["donde_vivis"]["base"],
             "Por zona (CABA / GBA / PBA)", label_wrap=16)
    # Columna derecha: top 5 barrios/localidades (si los datos lo permiten).
    if barrios:
        filas, total, otras = barrios
        mini_top_table(fig, 0.520, top - 0.012, 0.415, filas, otras, total,
                       titulo=c["barrios_titulo"], nota=c["barrios_nota"])
    else:
        descriptive_lines(fig, 0.520, top - 0.030, 0.415,
                          "El detalle por barrio/localidad no se publica para no exponer respuestas individuales.",
                          fontsize=8.6, color=GREY)
    lectura_box(fig, 0.065, 0.150, 0.87, c["lectura"])
    footer(fig)
    pdf.savefig(fig)
    final.plt.close(fig)


def link_page(pdf, c, stats, p, page_no):
    fig = page()
    header(fig, page_no, c["titulo"], c["subtitulo"])
    b1 = question_block(fig, 0.065, 0.775, 0.42, c["pregunta_primera"], c["tipo_primera"], c["observa_primera"])
    b2 = question_block(fig, 0.515, 0.775, 0.42, c["pregunta_contacto"], c["tipo_contacto"], c["observa_contacto"])
    top = min(b1, b2) - 0.040
    stacked(fig, [0.085, top - 0.110, 0.420, 0.110], stats["primera_vez"]["items"], stats["primera_vez"]["base"],
            "Primera vez o ya había participado", [INK, ORANGE, GREY])
    donut(fig, [0.585, top - 0.205, 0.250, 0.210], stats["acepta_contacto"]["items"], "Acepta recibir información",
          f"{pct_s(p['contact_yes'], p['contact_base'])}", [GREEN, GREY])
    lectura_box(fig, 0.065, 0.165, 0.87, c["lectura"])
    footer(fig)
    pdf.savefig(fig)
    final.plt.close(fig)


def channels_page(pdf, c, stats, page_no):
    fig = page()
    header(fig, page_no, c["titulo"], c["subtitulo"])
    b = question_block(fig, 0.065, 0.790, 0.87, c["pregunta"], c["tipo"], c["observa"])
    # Nota explicativa de multi-respuesta (frase completa), debajo de la pregunta.
    ny = descriptive_lines(fig, 0.065, b - 0.012, 0.87, c["nota_multi"], fontsize=8.4, color="#444444")
    top = ny - 0.034
    hbar_pct(fig, [0.150, top - 0.250, 0.55, 0.250], stats["como_se_entero"]["items"], stats["como_se_entero"]["base"],
             "Cómo se enteraron del evento", color=BLUE, accents={"Instagram"},
             multi=True, show_mentions=True, label_wrap=22)
    lectura_box(fig, 0.065, 0.150, 0.87, c["lectura"])
    footer(fig)
    pdf.savefig(fig)
    final.plt.close(fig)


def acompanamiento_page(pdf, c, stats, page_no):
    fig = page()
    header(fig, page_no, c["titulo"], c["subtitulo"])
    b = question_block(fig, 0.065, 0.775, 0.87, c["pregunta_con_quien"], c["tipo_con_quien"], c["observa_con_quien"])
    top = b - 0.040
    hbar_pct(fig, [0.230, top - 0.270, 0.50, 0.270], stats["con_quien"]["items"], stats["con_quien"]["base"],
             "Con quién asistió al evento", accents={"En pareja"}, label_wrap=26)
    lectura_box(fig, 0.065, 0.150, 0.87, c["lectura"])
    footer(fig)
    pdf.savefig(fig)
    final.plt.close(fig)


def motivaciones_page(pdf, c, stats, page_no):
    fig = page()
    header(fig, page_no, c["titulo"], c["subtitulo"])
    b = question_block(fig, 0.065, 0.775, 0.87, c["pregunta_intereso"], c["tipo_intereso"], c["observa_intereso"])
    top = b - 0.040
    hbar_pct(fig, [0.230, top - 0.290, 0.50, 0.290], stats["que_intereso"]["items"], stats["que_intereso"]["base"],
             "Qué fue lo que más le interesó", color=final.COFFEE,
             accents={"Probar café / cafeterías"}, label_wrap=26)
    lectura_box(fig, 0.065, 0.150, 0.87, c["lectura"])
    footer(fig)
    pdf.savefig(fig)
    final.plt.close(fig)


def interests_page(pdf, c, stats, page_no):
    fig = page()
    header(fig, page_no, c["titulo"], c["subtitulo"])
    b = question_block(fig, 0.065, 0.790, 0.87, c["pregunta"], c["tipo"], c["observa"])
    ny = descriptive_lines(fig, 0.065, b - 0.012, 0.87, c["nota_multi"], fontsize=8.4, color="#444444")
    # Caja de lectura primero (anclada abajo); gráfico apoyado encima con margen.
    lec_top = lectura_box(fig, 0.065, 0.135, 0.87, c["lectura"])
    graf_top = ny - 0.028
    graf_bottom = lec_top + 0.035
    hbar_pct(fig, [0.150, graf_bottom, 0.42, graf_top - graf_bottom],
             stats["eventos_futuros"]["items"], stats["eventos_futuros"]["base"],
             "Intereses para próximas ediciones", color=BLUE, limit=8,
             multi=True, show_mentions=True, label_wrap=22)
    footer(fig)
    pdf.savefig(fig)
    final.plt.close(fig)


def synthesis_page(pdf, c, page_no):
    fig = page()
    header(fig, page_no, c["titulo"], c["subtitulo"])
    descriptive_lines(fig, 0.065, 0.820, 0.87, c["intro"], fontsize=10.0, color=INK)
    yy = 0.770
    for punto in c["puntos"]:
        for line in wrap_text("•  " + punto, 100):
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
        for line in wrap_text("•  " + punto, 98):
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
    top_sedes = [r for r in sedes_comuna if str(r["comuna"]).isdigit()][:5]
    top_txt = ", ".join(f"Comuna {r['comuna']} ({r['cantidad_sedes']})" for r in top_sedes)
    add_box(fig, 0.515, 0.300, 0.42, 0.130, "Comunas con más sedes",
            f"{top_txt}.", face=SOFT_BLUE, edge=BLUE, body_size=8.6)
    add_box(fig, 0.065, 0.150, 0.87, 0.120, "Nota sobre esta lectura", c["nota_prudente"],
            face=SOFT_ORANGE, edge=ORANGE, body_size=9.0)
    footer(fig)
    pdf.savefig(fig)
    final.plt.close(fig)


# ----------------------------------------------------------------------- build
def write_pdf(content, records, stats, p, ranking_rows, sedes_comuna, filas, con_ts, barrios):
    pages = content["paginas"]
    inst = content["institucion"]
    ev = content["evento"]
    fecha_doc = content.get("fecha_documento", "")
    numbers = number_context(p, stats, ranking_rows, sedes_comuna)
    numbers = {**numbers, **inst}

    def pc(key):
        return {k: fmt(v, numbers) for k, v in pages[key].items()}

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    with PdfPages(PDF_REV) as pdf:
        cover_page(pdf, pc("portada"), inst, ev)
        index_page(pdf, pc("indice"), fecha_doc, 2)
        general_data_page(pdf, pc("datos_generales"), inst, ev, filas, con_ts, p["n"], 3)
        questions_page(pdf, pc("preguntas"), 4)
        profile_page(pdf, pc("perfil"), stats, 5)
        residence_page(pdf, pc("residencia"), stats, barrios, 6)
        link_page(pdf, pc("vinculo"), stats, p, 7)
        channels_page(pdf, pc("canales"), stats, 8)
        acompanamiento_page(pdf, pc("acompanamiento"), stats, 9)
        motivaciones_page(pdf, pc("motivaciones"), stats, 10)
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

    final.draw_mapa_comunal_publico(ranking_rows)
    final.draw_mapa_sedes(sedes_mapa)
    final.draw_mapa_combinado(sedes_mapa, ranking_rows)

    filas, con_ts = respuestas_por_dia_franja(records)
    barrios = top_barrios(records, top_n=5, min_freq=2)

    pages = write_pdf(content, records, stats, p, ranking_rows, sedes_comuna, filas, con_ts, barrios)

    print("=" * 72)
    print("Informe Cafecito DGDGAS · REVISIÓN 3")
    print(f"  Contenido editable: {CONTENIDO_YAML.relative_to(REPO_ROOT)}")
    print(f"  Respuestas: {len(records)}  ·  con marca temporal: {con_ts}")
    if barrios:
        filas_b, total_b, otras_b = barrios
        print(f"  Top barrios/localidades (base {total_b}):")
        for nombre, n, pp in filas_b:
            print(f"    {nombre}: {n} ({pp:.0f}%)")
        print(f"    Otras respuestas: {otras_b}")
    else:
        print("  Top barrios/localidades: NO se publica (datos insuficientes o riesgo de exposición)")
    print(f"  Páginas PDF: {pages}")
    print(f"  PDF: {PDF_REV.relative_to(REPO_ROOT)}")
    print(f"  Copia: {FINAL_PDF_REV.relative_to(REPO_ROOT)}")
    print("  (FINAL, EDITABLE_TEST y revisiones 1/2/2-formato NO fueron modificados.)")
    print("=" * 72)


if __name__ == "__main__":
    main()
