"""Genera el informe Cafecito · REVISIÓN 2 (a nombre de DGDGAS).

Segunda revisión del informe Cafecito. Mantiene el enfoque de RESULTADOS de
encuesta de la revisión 1 (datos duros, preguntas, porcentajes, lectura
descriptiva, recomendaciones en potencial) y aplica:

  - Marca institucional DGDGAS en TODO el PDF público (se quita "DataGastro"
    de portada, header, footer, índice, notas y cualquier texto visible).
  - Portada limpia, sin información duplicada ni "Entrada libre y gratuita".
  - Índice con números de página reales.
  - Datos generales sin la nota de horario.
  - Preguntas del formulario compactadas en una sola página.
  - Página de perfil reordenada (edad y género sin solapamientos).

Reutiliza (importa) el motor de la revisión 1 y del generador final: datos,
cálculo, mapas y primitivas de layout. No los modifica.

Reglas del PDF público: sin rutas, scripts, hashes, versiones internas, ni
datos personales. El público se muestra agregado.

NO sobrescribe el FINAL, el EDITABLE_TEST ni la REVISIÓN 1.

Salidas:
  - outputs/cafecito/INFORME_CAFECITO_DGDGAS_REVISION_2.pdf
  - Cafesito/final/INFORME_CAFECITO_DGDGAS_REVISION_2.pdf

Uso:
    python scripts/cafecito/generar_informe_cafecito_revision_2.py
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Motor del generador final (datos, cálculo, mapas, primitivas de layout).
from scripts.cafecito import generar_informe_datagastro_final as final  # noqa: E402
from scripts.cafecito.generar_informe_datagastro_final_editable import _load_yaml, fmt  # noqa: E402
from scripts.cafecito.generar_informe_datagastro_final import (  # noqa: E402
    INK, ORANGE, GREEN, BLUE, GREY, WHITE, LIGHT, LINE,
    SOFT_BLUE, SOFT_ORANGE, SOFT_GREEN,
    add_box, add_image, clean_text, donut, items_dict, page, pct_s, stacked, wrap_text,
)
from scripts.cafecito.generar_informe_datagastro_final import header as _base_header  # noqa: E402

# Motor de la revisión 1: porcentajes, franjas horarias, preguntas, helpers de
# dibujo descriptivo (question_block, hbar_pct, descriptive_lines, tabla).
from scripts.cafecito import generar_informe_datagastro_revision_1 as rev1  # noqa: E402
from scripts.cafecito.generar_informe_datagastro_revision_1 import (  # noqa: E402
    FRANJAS, PREGUNTAS_FORMULARIO,
    number_context, respuestas_por_dia_franja,
    hbar_pct, question_block, descriptive_lines, _draw_franja_table,
)

DOCS_DIR = REPO_ROOT / "docs" / "cafecito"
OUT_DIR = REPO_ROOT / "outputs" / "cafecito"
FINAL_DIR = REPO_ROOT / "Cafesito" / "final"

CONTENIDO_YAML = DOCS_DIR / "contenido_editable_informe_cafecito_revision_2.yaml"

PDF_REV = OUT_DIR / "INFORME_CAFECITO_DGDGAS_REVISION_2.pdf"
FINAL_PDF_REV = FINAL_DIR / "INFORME_CAFECITO_DGDGAS_REVISION_2.pdf"

MAPA_SEDES = final.MAPA_SEDES
MAPA_COMBINADO = final.MAPA_COMBINADO

# Marca institucional: ya NO es DataGastro.
KICKER = "DGDGAS"
FOOTER_REV2 = "DGDGAS · Cafecito BA en tu barrio · Resultados de encuestas"


# ------------------------------------------------------- header / footer DGDGAS
def header(fig, page_no, title, subtitle=""):
    """Encabezado de página con kicker institucional DGDGAS (no DataGastro)."""
    return _base_header(fig, page_no, title, subtitle, kicker=KICKER)


def footer(fig):
    fig.lines.append(Line2D([0.065, 0.935], [0.055, 0.055], color=LINE, lw=0.8, transform=fig.transFigure))
    fig.text(0.065, 0.035, FOOTER_REV2, color=GREY, fontsize=7.8, va="center")


# --------------------------------------------------------------------- páginas
def cover_page(pdf, c, inst, ev):
    """Portada limpia: marca DGDGAS, una sola vez cada dato, sin 'Entrada'."""
    fig = page()
    fig.patches.append(Rectangle((0, 0.70), 1, 0.30, transform=fig.transFigure, facecolor=INK, edgecolor="none"))
    fig.patches.append(Rectangle((0, 0.688), 1, 0.012, transform=fig.transFigure, facecolor=ORANGE, edgecolor="none"))
    # Kicker institucional (reemplaza a "DataGastro").
    fig.text(0.065, 0.93, c["kicker_marca"], color=WHITE, fontsize=12, fontweight="bold")
    fig.text(0.935, 0.93, c["kicker_tipo"], color="#c9d6e4", fontsize=10, ha="right")
    fig.text(0.065, 0.84, c["titulo"], color=WHITE, fontsize=34, fontweight="bold", va="top", linespacing=0.95)
    fig.text(0.065, 0.728, c["subtitulo"], color="#dbe5ef", fontsize=12.5, va="center")
    # Descripción en oraciones completas.
    descriptive_lines(fig, 0.065, 0.628, 0.87, c["descripcion"], fontsize=11.0, color=INK)
    # Ficha del evento (cada dato UNA sola vez; "Presenta" va acá, no duplicado).
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
    """Índice con números de página reales y línea de puntos guía."""
    fig = page()
    header(fig, page_no, c["titulo"], c["subtitulo"])
    y = 0.800
    for i, entrada in enumerate(c["entradas"], 1):
        texto = entrada["texto"]
        pagina = entrada["pagina"]
        fig.text(0.075, y, f"{i}.", color=ORANGE, fontsize=11, fontweight="bold", va="top")
        fig.text(0.110, y, clean_text(texto), color=INK, fontsize=11, va="top")
        fig.text(0.930, y, str(pagina), color=INK, fontsize=11, fontweight="bold", va="top", ha="right")
        # Línea de puntos guía entre el título y el número de página.
        fig.lines.append(Line2D([0.110, 0.915], [y - 0.013, y - 0.013], color=LINE, lw=0.6,
                                linestyle=(0, (1, 2.5)), transform=fig.transFigure))
        y -= 0.046
    fig.text(0.065, 0.075, f"{c['titulo']} · {fecha_doc}", color=GREY, fontsize=8.5, va="center")
    footer(fig)
    pdf.savefig(fig)
    final.plt.close(fig)


def general_data_page(pdf, c, inst, ev, filas, con_ts, n_total, page_no):
    """Datos generales. Sin la nota de horario; mantiene la tabla de franjas."""
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
        # Nota de horario eliminada en la revisión 2 (no hace falta aclararlo).
    else:
        descriptive_lines(fig, 0.065, 0.380, 0.87,
                          "No fue posible desagregar las respuestas por día y franja horaria a partir de los datos disponibles.",
                          fontsize=9.0)
    footer(fig)
    pdf.savefig(fig)
    final.plt.close(fig)


def questions_page(pdf, c, page_no):
    """Las 9 preguntas + tipo + objetivo en una SOLA página, formato compacto.

    Cada pregunta es una fila de dos columnas: a la izquierda la pregunta y su
    tipo; a la derecha el objetivo. Altura por fila calculada según el texto,
    para que nada se corte ni desborde.
    """
    fig = page()
    header(fig, page_no, c["titulo"], c["subtitulo"])
    descriptive_lines(fig, 0.065, 0.840, 0.87, c["intro"], fontsize=8.8, color="#333333")

    x, w = 0.065, 0.87
    col_preg_w = 0.40   # ancho de la columna pregunta+tipo
    gap = 0.02
    x_obj = x + col_preg_w + gap
    obj_w = w - col_preg_w - gap

    nota_lines = wrap_text(c["nota_pie"], 150) if c.get("nota_pie") else []
    # Reservar espacio para la nota al pie (si entra).
    y_floor = 0.105 + 0.014 * len(nota_lines) + 0.010

    y = 0.800
    row_gap = 0.008
    for i, q in enumerate(PREGUNTAS_FORMULARIO, 1):
        preg_lines = wrap_text(f"{i}. {q['pregunta']}", 44)
        tipo_line = f"Tipo: {q['tipo']}."
        obj_lines = wrap_text(q["objetivo"], 60)
        n_left = len(preg_lines) + 1
        n_right = len(obj_lines)
        rows = max(n_left, n_right)
        h = 0.012 + 0.0148 * rows
        y_box = y - h
        # Fila con fondo alterno para legibilidad.
        face = "#f4f7fa" if i % 2 else WHITE
        fig.patches.append(Rectangle((x, y_box), w, h, transform=fig.transFigure,
                                     facecolor=face, edgecolor=LINE, lw=0.6))
        fig.patches.append(Rectangle((x, y_box), 0.005, h, transform=fig.transFigure,
                                     facecolor=ORANGE, edgecolor="none"))
        # Columna izquierda: pregunta (negrita) + tipo.
        ty = y - 0.012
        for j, line in enumerate(preg_lines):
            fig.text(x + 0.016, ty, clean_text(line), color=INK, fontsize=8.2,
                     fontweight="bold", va="top")
            ty -= 0.0148
        fig.text(x + 0.016, ty, clean_text(tipo_line), color=BLUE, fontsize=7.8, va="top")
        # Columna derecha: objetivo.
        ty = y - 0.012
        for line in obj_lines:
            fig.text(x_obj + 0.010, ty, clean_text(line), color="#333333", fontsize=7.9, va="top")
            ty -= 0.0148
        y = y_box - row_gap

    # Nota breve al pie (solo si entra por encima del piso reservado).
    if nota_lines and (y - 0.010) > y_floor:
        ny = 0.118 + 0.014 * (len(nota_lines) - 1)
        for line in nota_lines:
            fig.text(0.065, ny, clean_text(line), color=GREY, fontsize=7.4, va="top")
            ny -= 0.014
    footer(fig)
    pdf.savefig(fig)
    final.plt.close(fig)


def profile_page(pdf, c, stats, page_no):
    """Perfil reordenado: edad (izquierda) y género (derecha) en bloques
    verticales pregunta→gráfico, sin solapamientos ni títulos tapados."""
    fig = page()
    header(fig, page_no, c["titulo"], c["subtitulo"])
    # Dos columnas independientes; cada una: bloque de pregunta y su gráfico.
    bl = question_block(fig, 0.065, 0.775, 0.42, c["pregunta_edad"], c["tipo_edad"], c["observa_edad"])
    br = question_block(fig, 0.515, 0.775, 0.42, c["pregunta_genero"], c["tipo_genero"], c["observa_genero"])
    top = min(bl, br) - 0.045
    # Edad: barras horizontales por rango.
    hbar_pct(fig, [0.090, top - 0.250, 0.39, 0.250], stats["rango_edad"]["items"], stats["rango_edad"]["base"],
             "Rango de edad", accents={"25 a 34"})
    # Género: barra apilada, con su título separado del bloque de pregunta.
    stacked(fig, [0.560, top - 0.090, 0.360, 0.072], stats["genero"]["items"], stats["genero"]["base"],
            "Género declarado", [INK, ORANGE, GREY])
    add_box(fig, 0.065, 0.150, 0.87, 0.175, "Lectura de resultados", c["lectura"],
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
             "Cómo se enteraron del evento", color=BLUE, accents={"Instagram"}, multi=True)
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
def write_pdf(content, records, stats, p, ranking_rows, sedes_comuna, filas, con_ts):
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
        residence_page(pdf, pc("residencia"), stats, 6)
        link_page(pdf, pc("vinculo"), stats, p, 7)
        channels_page(pdf, pc("canales"), stats, 8)
        company_motivation_page(pdf, pc("acompanamiento"), stats, 9)
        interests_page(pdf, pc("intereses"), stats, 10)
        synthesis_page(pdf, pc("sintesis"), 11)
        considerations_page(pdf, pc("aspectos"), 12)
        annex_network_page(pdf, pc("anexo_red"), sedes_comuna, 13)
    shutil.copy2(PDF_REV, FINAL_PDF_REV)
    return 13


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

    # Mapas del anexo: idénticos a los del final (mismas rutas PNG).
    final.draw_mapa_comunal_publico(ranking_rows)
    final.draw_mapa_sedes(sedes_mapa)
    final.draw_mapa_combinado(sedes_mapa, ranking_rows)

    filas, con_ts = respuestas_por_dia_franja(records)

    pages = write_pdf(content, records, stats, p, ranking_rows, sedes_comuna, filas, con_ts)

    print("=" * 72)
    print("Informe Cafecito DGDGAS · REVISIÓN 2")
    print(f"  Contenido editable: {CONTENIDO_YAML.relative_to(REPO_ROOT)}")
    print(f"  Respuestas: {len(records)}  ·  con marca temporal: {con_ts}")
    if filas:
        for f in filas:
            print(f"    {f['dia']}: total {f['total']}  -> " +
                  ", ".join(f"{k.split(' ')[0]} {v}" for k, v in f['franjas'].items()))
    print(f"  Páginas PDF: {pages}")
    print(f"  PDF revisión 2: {PDF_REV.relative_to(REPO_ROOT)}")
    print(f"  Copia: {FINAL_PDF_REV.relative_to(REPO_ROOT)}")
    print("  (FINAL, EDITABLE_TEST y REVISIÓN 1 NO fueron modificados.)")
    print("=" * 72)


if __name__ == "__main__":
    main()
