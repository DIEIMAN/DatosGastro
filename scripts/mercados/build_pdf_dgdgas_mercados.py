"""Informe institucional DGDGAS — Mercados gastronómicos de la Ciudad de Buenos Aires.

Versión documental: el cuerpo principal es expositivo (qué mercados hay, dónde están,
cómo se caracterizan, tipologías/gestión, horarios documentados, casos patrimoniales, tabla
final) y las capas de gestión (metodología, oportunidad, públicos operativos, decisiones,
pilotos, límites) van a anexos. NO recalcula datos ni cambia conteos, universo ni estados:
toma el contenido editorial ya trabajado y reutiliza los visuales V5 sanitizados.

Marca institucional DGDGAS — Dirección General de Gastronomía (Gobierno de la Ciudad de
Buenos Aires). NO usa "DataGastro" como marca pública. No incluye etiquetas de "prueba",
"borrador", "revisión institucional" ni "documento interno". No hace requests. No commitea.
No toca los scripts productivos de mercados_caba ni los entregables previos.

Salida (nueva, NO sobrescribe entregables previos):
  outputs/mercados/INFORME_MERCADOS_DGDGAS.pdf
"""
from __future__ import annotations

import textwrap
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
SAN = ROOT / "outputs" / "mercados_caba" / "sanitized"
OUT = ROOT / "outputs" / "mercados"
PDF = OUT / "INFORME_MERCADOS_DGDGAS.pdf"

INSTITUCION = "DGDGAS — Dirección General de Gastronomía"
GOBIERNO = "Gobierno de la Ciudad de Buenos Aires"
TITULO = "Mercados gastronómicos de la Ciudad de Buenos Aires — Informe"

A4 = (8.27, 11.69)
AZUL = "#1f3b57"
AZUL2 = "#2c7fb8"
ROJO = "#c0392b"
GRIS = "#555555"
GRISCLARO = "#eef2f6"
VERDE = "#1a9850"
NARANJA = "#c0762b"
LINEA = "#d9dee5"
SOFT_AZUL = "#eaf1f8"
SOFT_NARANJA = "#f7ebdc"

TOTAL_PAG = 17


def page():
    fig = plt.figure(figsize=A4)
    fig.patch.set_facecolor("white")
    return fig


def numpag(n):
    return f"{n} / {TOTAL_PAG}"


def head(fig, kicker, titulo, subtitulo, num, tsize=18):
    fig.text(0.07, 0.955, kicker, color=ROJO, fontsize=8.5, fontweight="bold")
    fig.text(0.93, 0.955, num, color=GRIS, fontsize=8.5, ha="right")
    for j, ln in enumerate(textwrap.wrap(titulo, 46)):
        fig.text(0.07, 0.928 - j * 0.030, ln, color=AZUL, fontsize=tsize, fontweight="bold", va="top")
    base = 0.928 - len(textwrap.wrap(titulo, 46)) * 0.030
    fig.lines.append(Line2D([0.07, 0.34], [base + 0.004, base + 0.004], color=ROJO, lw=2.2, transform=fig.transFigure))
    if subtitulo:
        for j, ln in enumerate(textwrap.wrap(subtitulo, 92)):
            fig.text(0.07, base - 0.012 - j * 0.020, ln, color=GRIS, fontsize=10.5, style="italic", va="top")
    return base


def bullets(fig, y0, items, size=10.5, gap=0.039, wrap=88, x=0.085):
    y = y0
    for it in items:
        lines = textwrap.wrap(it.strip(), wrap) or [""]
        fig.text(x, y, "•", fontsize=size, color=ROJO, va="top")
        for j, ln in enumerate(lines):
            fig.text(x + 0.022, y - j * 0.0225, ln, fontsize=size, color="#222222", va="top")
        y -= gap + (len(lines) - 1) * 0.0225
    return y


def insight(fig, y, texto, color=AZUL, h=0.075, fc=GRISCLARO):
    fig.patches.append(Rectangle((0.07, y), 0.86, h, transform=fig.transFigure, facecolor=fc,
                                 edgecolor=color, lw=1.3))
    lines = textwrap.wrap(texto, 96)
    for j, ln in enumerate(lines):
        fig.text(0.09, y + h - 0.022 - j * 0.019, ln, fontsize=9.3, color="#222222", va="top", fontweight="bold")


def cards(fig, y, items, h=0.10):
    n = len(items)
    w = 0.86 / n
    for i, (val, lab, col) in enumerate(items):
        x = 0.07 + i * w
        fig.patches.append(Rectangle((x + 0.008, y), w - 0.016, h, transform=fig.transFigure,
                                     facecolor=GRISCLARO, edgecolor=col, lw=1.6))
        fig.text(x + w / 2, y + h * 0.60, str(val), ha="center", fontsize=19, fontweight="bold", color=col)
        for k, sub in enumerate(lab.split("\n")):
            fig.text(x + w / 2, y + h * 0.27 - k * 0.017, sub, ha="center", fontsize=7.8, color=GRIS)


def foot(fig, nota=None):
    """Pie institucional DGDGAS. `nota` opcional (con mayúscula inicial) por encima de la
    firma, con espaciado calculado según nº de líneas para no solaparse."""
    footer_y = 0.031
    rule_y = 0.050
    note_last_line_y = 0.064
    note_line_gap = 0.0145
    fig.lines.append(Line2D([0.07, 0.93], [rule_y, rule_y], color="#dddddd", lw=0.8, transform=fig.transFigure))
    if nota:
        note = nota[0].upper() + nota[1:] if nota else nota
        note_lines = textwrap.wrap(note, 116)
        note_y = note_last_line_y + (len(note_lines) - 1) * note_line_gap
        for j, ln in enumerate(note_lines):
            fig.text(0.07, note_y - j * note_line_gap, ln, color=GRIS, fontsize=7.4,
                     va="top", style="italic")
    fig.text(0.07, footer_y, f"{INSTITUCION} · {GOBIERNO}", color=AZUL, fontsize=7.6,
             va="top", fontweight="bold")


def box(fig, x, y, w, h, title, text, kind="resp"):
    color = AZUL2 if kind == "resp" else NARANJA
    bg = SOFT_AZUL if kind == "resp" else SOFT_NARANJA
    fig.patches.append(Rectangle((x, y), w, h, transform=fig.transFigure, facecolor=bg,
                                 edgecolor=color, lw=1.1))
    fig.patches.append(Rectangle((x, y), 0.012, h, transform=fig.transFigure, facecolor=color, edgecolor=color))
    fig.text(x + 0.026, y + h - 0.024, title, color=color, fontsize=9.4, fontweight="bold", va="top")
    wrap = 96 if w > 0.78 else (58 if w > 0.5 else 40)
    for i, line in enumerate(textwrap.wrap(text, wrap)):
        ytxt = y + h - 0.050 - i * 0.018
        if ytxt < y + 0.006:
            break
        fig.text(x + 0.026, ytxt, line, color="#222222", fontsize=8.7, va="top")


def image_fit(fig, path, x, top, w):
    img = plt.imread(SAN / path)
    px_h, px_w = img.shape[0], img.shape[1]
    aspect_px = px_w / px_h
    fig_w_in, fig_h_in = A4
    h = w * (fig_w_in / fig_h_in) / aspect_px
    bottom = top - h
    ax = fig.add_axes([x, bottom, w, h])
    ax.imshow(img)
    ax.axis("off")
    return bottom


def table(fig, rect, data, col_labels, font=7.6, yscale=1.35, col_widths=None):
    ax = fig.add_axes(rect)
    ax.axis("off")
    tbl = ax.table(cellText=data, colLabels=col_labels, loc="upper left",
                   cellLoc="left", colWidths=col_widths)
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(font)
    tbl.scale(1, yscale)
    for (r, _c), cell in tbl.get_celld().items():
        cell.set_edgecolor(LINEA)
        cell.set_linewidth(0.5)
        cell.set_text_props(wrap=True)
        if r == 0:
            cell.set_facecolor(AZUL)
            cell.set_text_props(color="white", fontweight="bold")
        else:
            cell.set_facecolor("white" if r % 2 else "#f7f9fb")


def matrix(fig, x, top, w, col_labels, rows, col_widths, font=7.3, header_font=7.4,
           min_row_h=0.072, line_gap=0.0145, pad_x=0.011, pad_y=0.011):
    """Tabla manual para anexos con textos largos y altura de fila calculada."""
    widths = [w * cw for cw in col_widths]
    starts = [x]
    for cw in widths[:-1]:
        starts.append(starts[-1] + cw)

    def wrap_cell(text, cw):
        chars = max(9, int((cw - 2 * pad_x) / 0.0076))
        lines = []
        for chunk in str(text).split("\n"):
            lines.extend(textwrap.wrap(chunk, chars) or [""])
        return lines or [""]

    header_h = 0.044
    y = top - header_h
    for i, label in enumerate(col_labels):
        fig.patches.append(Rectangle((starts[i], y), widths[i], header_h, transform=fig.transFigure,
                                     facecolor=AZUL, edgecolor="white", lw=0.7))
        header_lines = wrap_cell(label, widths[i])[:2]
        for j, line in enumerate(header_lines):
            fig.text(starts[i] + pad_x, y + header_h - 0.012 - j * 0.014, line, color="white",
                     fontsize=header_font, fontweight="bold", va="top")

    y = y
    for r, row in enumerate(rows):
        wrapped = [wrap_cell(cell, widths[i]) for i, cell in enumerate(row)]
        max_lines = max(len(lines) for lines in wrapped)
        row_h = max(min_row_h, pad_y * 2 + max_lines * line_gap + 0.004)
        y -= row_h
        bg = "white" if r % 2 == 0 else "#f7f9fb"
        for i, lines in enumerate(wrapped):
            fig.patches.append(Rectangle((starts[i], y), widths[i], row_h, transform=fig.transFigure,
                                         facecolor=bg, edgecolor=LINEA, lw=0.6))
            color = AZUL if i == 0 else "#222222"
            weight = "bold" if i == 0 else "normal"
            for j, line in enumerate(lines):
                fig.text(starts[i] + pad_x, y + row_h - pad_y - j * line_gap, line,
                         color=color, fontsize=font, fontweight=weight, va="top")
    return y


def info_card(fig, x, y, w, h, title, rows, accent=AZUL, title_size=8.5, body_size=8.0):
    pad = 0.014
    inner_w = w - 2 * pad
    chars_body = max(16, int(inner_w / 0.0066))
    chars_title = max(12, int(inner_w / 0.0086))
    title_lines = textwrap.wrap(title, chars_title)[:2]
    bar_h = 0.030 if len(title_lines) <= 1 else 0.046
    fig.patches.append(Rectangle((x, y), w, h, transform=fig.transFigure,
                                 facecolor="white", edgecolor=LINEA, lw=1.0))
    fig.patches.append(Rectangle((x, y + h - bar_h), w, bar_h, transform=fig.transFigure,
                                 facecolor=accent, edgecolor=accent))
    for j, line in enumerate(title_lines):
        fig.text(x + pad, y + h - 0.011 - j * 0.016, line, color="white",
                 fontsize=title_size, fontweight="bold", va="top")
    yy = y + h - bar_h - 0.020
    for label, value in rows:
        if yy < y + 0.010:
            break
        fig.text(x + pad, yy, label, color=accent, fontsize=body_size - 0.4,
                 fontweight="bold", va="top")
        wrapped = textwrap.wrap(value, chars_body)
        for j, line in enumerate(wrapped):
            ytxt = yy - 0.014 - j * 0.0150
            if ytxt < y + 0.008:
                break
            fig.text(x + pad, ytxt, line, color="#222222", fontsize=body_size, va="top")
        yy -= 0.030 + len(wrapped) * 0.0150


def opportunity_card(fig, x, y, w, h, title, rows, accent=AZUL, title_size=8.0, body_size=7.1):
    """Card compacta para Anexo B, con wrap más prudente que evita desbordes."""
    pad = 0.014
    inner_w = w - 2 * pad
    chars_body = max(18, int(inner_w / 0.0082))
    chars_title = max(14, int(inner_w / 0.0092))
    title_lines = textwrap.wrap(title, chars_title)[:2]
    bar_h = 0.032 if len(title_lines) <= 1 else 0.048
    fig.patches.append(Rectangle((x, y), w, h, transform=fig.transFigure,
                                 facecolor="white", edgecolor=LINEA, lw=1.0))
    fig.patches.append(Rectangle((x, y + h - bar_h), w, bar_h, transform=fig.transFigure,
                                 facecolor=accent, edgecolor=accent))
    for j, line in enumerate(title_lines):
        fig.text(x + pad, y + h - 0.011 - j * 0.016, line, color="white",
                 fontsize=title_size, fontweight="bold", va="top")
    yy = y + h - bar_h - 0.018
    for label, value in rows:
        if yy < y + 0.012:
            break
        fig.text(x + pad, yy, label, color=accent, fontsize=body_size - 0.3,
                 fontweight="bold", va="top")
        wrapped = textwrap.wrap(value, chars_body)
        for j, line in enumerate(wrapped):
            ytxt = yy - 0.014 - j * 0.0143
            if ytxt < y + 0.008:
                break
            fig.text(x + pad, ytxt, line, color="#222222", fontsize=body_size, va="top")
        yy -= 0.026 + len(wrapped) * 0.0143


# --------------------------------------------------------------------------- #
# Datos (contenido editorial ya trabajado; sin recalcular)
# --------------------------------------------------------------------------- #
TIPOLOGIAS = [
    ["Patio gastronómico", "4", "Lecheros, Smart Plaza, Costanera Norte, Rodrigo Bueno"],
    ["Mercado histórico", "3", "San Telmo, Belgrano, San Nicolás"],
    ["Food hall", "2", "Mercat Villa Crespo, Gourmand Food Hall"],
    ["Mercado de productores", "2", "Bonpland, Sabe la Tierra"],
    ["Mercado barrial alimentario", "1", "Mercado del Progreso"],
    ["Feria gastronómica", "1", "Buenos Aires Market"],
]

HORARIOS = [
    ["Mercado de San Telmo", "Lunes a domingo", "9 a 22", "Turístico y barrial"],
    ["Mercado de Belgrano", "Lunes a domingo", "Frescos 8:30-20; gastronomía 11-24", "Frescos y gastronomía"],
    ["Mercado San Nicolás", "Lunes a sábado", "Mercado 8-18; gastronomía 11-24", "Almuerzo y post-laboral"],
    ["Mercado del Progreso", "Lunes a sábado", "Lun-Vie 7:30-13 y 17-20; Sáb hasta 14", "Clásico barrial de abasto"],
    ["Mercat Villa Crespo", "Martes a domingo", "12 a 23 (Vie-Sáb hasta 01)", "Almuerzo y tarde-noche"],
    ["Gourmand Food Hall", "Todos los días", "Dom-Jue 10-23; Vie-Sáb 10-1", "Food hall"],
    ["Patio de los Lecheros", "Todos los días", "9 a 24 (Vie-Sáb hasta 3)", "Operación extendida"],
    ["Smart Plaza Parque Patricios", "Todos los días", "11 a 24 (Vie-Sáb hasta 1)", "Almuerzo y post-laboral"],
    ["Patio Costanera Norte", "Miércoles a domingo", "Mié 12-19; Jue-Sáb 12-24; Dom 12-21", "Paseo de ribera"],
    ["Patio Rodrigo Bueno", "Viernes a domingo", "11 a 23", "Fin de semana"],
    ["Mercado Bonpland", "Mar, mié, vie y sáb", "10 a 19/20", "Días específicos; productores"],
    ["Sabe la Tierra", "Fines de semana", "Según sede y programación", "Sin horario fijo único"],
    ["Buenos Aires Market", "Fines de semana", "Según sede y programación", "Sin horario fijo único"],
]

PATRIMONIALES = [
    ("Mercado de San Telmo", "1897", "Ícono turístico de la Ciudad.", NARANJA),
    ("Mercado de Belgrano", "1891", "Renovado con food court.", AZUL2),
    ("Mercado del Progreso", "1889", "Sitio de interés cultural; clásico barrial.", VERDE),
    ("Mercado San Nicolás", "centenario", "Renovado en Microcentro.", AZUL2),
    ("Mercado Bonpland", "economía social", "Referente de consumo consciente.", VERDE),
]

NO_ACTIVOS = [
    ("Mercado Soho",
     [("Estado", "Relevante no contabilizado"),
      ("Motivo", "Señales de cierre y falta de actividad reciente verificable."),
      ("Lectura", "Vuelve al conteo si se valida actividad.")], NARANJA),
    ("Mercat Caballito",
     [("Estado", "Relevante no contabilizado"),
      ("Motivo", "Señales de cierre; en fuente oficial solo figura como evento."),
      ("Lectura", "Requiere validación antes de contar.")], NARANJA),
    ("El Galpón",
     [("Estado", "Relevante no contabilizado"),
      ("Motivo", "Situación operativa no clara; match de Google inconsistente."),
      ("Lectura", "Productores; requiere validación.")], NARANJA),
    ("Mercado de los Carruajes",
     [("Estado", "Cerrado documentado"),
      ("Motivo", "Cerró en abril de 2025 y se reconvierte a eventos."),
      ("Lectura", "Antecedente relevante, no activo.")], ROJO),
]

ACTIVOS = [
    ["Mercado de San Telmo", "histórico", "mixta", "San Telmo / 1", "sede fija", "alto"],
    ["Mercado de Belgrano", "histórico", "mixta", "Belgrano / 13", "sede fija", "alto"],
    ["Mercado San Nicolás", "histórico", "mixta", "San Nicolás / 1", "sede fija", "alto"],
    ["Mercado del Progreso", "barrial alim.", "privada", "Caballito / 6", "sede fija", "alto"],
    ["Mercat Villa Crespo", "food hall", "privada", "Villa Crespo / 15", "sede fija", "alto"],
    ["Gourmand Food Hall", "food hall", "privada", "Retiro / 1", "sede fija", "alto"],
    ["Patio de los Lecheros", "patio gastron.", "pública", "Caballito / 6", "sede fija", "alto"],
    ["Smart Plaza Parque Patricios", "patio gastron.", "pública", "P. Patricios / 4", "sede fija", "alto"],
    ["Patio Costanera Norte", "patio gastron.", "mixta", "Costanera N. / 13", "sede fija", "medio"],
    ["Patio Rodrigo Bueno", "patio gastron.", "pública", "Puerto Madero / 1", "sede fija", "alto"],
    ["Mercado Bonpland", "productores", "mixta", "Palermo / 14", "sede fija", "alto"],
    ["Sabe la Tierra", "productores", "privada", "itinerante", "itinerante", "alto"],
    ["Buenos Aires Market", "feria gastron.", "privada", "itinerante", "itinerante", "alto"],
]

# --- Contenido de anexos de gestión ---
OPORTUNIDAD = [
    ("Turismo y marca ciudad",
     "Convertir mercados seleccionados en puertas de entrada a barrios y circuitos "
     "gastronómicos y patrimoniales, bajo una narrativa común de ciudad.",
     "San Telmo, Gourmand, Costanera Norte, San Nicolás, Belgrano", AZUL2),
    ("Activación barrial",
     "Usar los mercados como espacios de encuentro, hábito y agenda de cercanía para "
     "vecinos, familias y trabajadores del entorno.",
     "Belgrano, Progreso, Lecheros, Smart Plaza, Mercat V. Crespo, BA Market", VERDE),
    ("Productores y economía social",
     "Visibilizar origen, producción local, consumo responsable y economía social como "
     "parte de la identidad gastronómica de la Ciudad.",
     "Bonpland, Sabe la Tierra, BA Market, Rodrigo Bueno", VERDE),
    ("Agenda gastronómica y cultural",
     "Pasar de actividades aisladas a una programación reconocible y comunicable a escala "
     "ciudad, con hitos temáticos.",
     "San Telmo, Belgrano, San Nicolás, Bonpland, Lecheros, Rodrigo Bueno", NARANJA),
    ("Gestión pública ordenada",
     "Usar la base como instrumento de priorización, comunicación y seguimiento, sin "
     "presentarla como padrón oficial ni validación cerrada.",
     "Todos los activos identificados", AZUL2),
]

PUBLICOS = [
    ("Turístico / patrimonial",
     "San Telmo, Costanera Norte y Gourmand: mayor potencial para recorridos, paseo y "
     "consumo de experiencia.", NARANJA),
    ("Barrial / familiar",
     "Belgrano, Progreso, Lecheros y Buenos Aires Market: encaje para activaciones de "
     "cercanía y hábito.", AZUL2),
    ("Trabajadores / post-laboral",
     "San Nicolás, Smart Plaza Parque Patricios y Mercat Villa Crespo: franjas de almuerzo, "
     "post-trabajo y salida corta.", VERDE),
    ("Productores / consumo consciente",
     "Bonpland, Sabe la Tierra y Buenos Aires Market: lógica de productores, economía "
     "social y consumo saludable.", VERDE),
    ("Comunitario / colectividades",
     "Rodrigo Bueno, Bonpland y Sabe la Tierra: activaciones de comunidad, colectividades "
     "y cocina cultural.", NARANJA),
]

PUBLICOS_MATRIZ = [
    ["Turístico / patrimonial", "San Telmo, Costanera Norte, Gourmand", "Recorridos, degustaciones, circuitos"],
    ["Barrial / familiar", "Belgrano, Progreso, Lecheros, BA Market", "Cercanía, hábito, fines de semana"],
    ["Trabajadores / post-laboral", "San Nicolás, Smart Plaza, Mercat V. Crespo", "Almuerzo, after office, entre semana"],
    ["Productores / consumo consciente", "Bonpland, Sabe la Tierra, BA Market", "Ferias, talleres, consumo responsable"],
    ["Comunitario / colectividades", "Rodrigo Bueno, Bonpland, Sabe la Tierra", "Cocina cultural, colectividades, identidad"],
]

DECISIONES = [
    ("Circuitos turísticos",
     "Articular los mercados de mayor atractivo turístico en recorridos integrados.",
     "San Telmo, Belgrano, Gourmand", AZUL2),
    ("Productores y economía social",
     "Apoyar mercados y ferias de productores y consumo consciente.",
     "Bonpland, Sabe la Tierra, BA Market", VERDE),
    ("Patios públicos",
     "Usar los patios gastronómicos públicos como dinamizadores barriales.",
     "Lecheros, Smart Plaza, Costanera, Rodrigo Bueno", AZUL2),
    ("Base candidata trazable",
     "Sostener un catálogo con tipología y estado operativo, actualizable.",
     "Todos los activos identificados", NARANJA),
    ("Validación territorial",
     "Ordenar la verificación en terreno por respaldo documental.",
     "Empezar por respaldo medio o a validar", NARANJA),
    ("Información pública uniforme",
     "Publicar horarios, gestión y oferta de cada mercado de forma homogénea.",
     "Todos los activos identificados", AZUL2),
]

PILOTOS = [
    ("San Nicolás — Almuerzo cultural",
     [("Público / franja", "Trabajadores y visitantes; mediodía laboral y salida corta"),
      ("Objetivo", "Opción reconocible de almuerzo y experiencia breve en Microcentro"),
      ("Primer paso", "Menús de mediodía, recorrido corto e historia, con validación previa")], AZUL2),
    ("Belgrano — Activación post-laboral barrial",
     [("Público / franja", "Barrial / familiar; tarde-noche entre semana y fines de semana"),
      ("Objetivo", "Punto de encuentro con consumo, degustación y agenda barrial"),
      ("Primer paso", "Activación mensual liviana con comerciantes y comunicación barrial")], VERDE),
    ("Bonpland / Sabe la Tierra / BA Market — Productores",
     [("Público / franja", "Productores / consumo consciente; fines de semana"),
      ("Objetivo", "Línea vinculada a origen, producción responsable y consumo saludable"),
      ("Primer paso", "Seleccionar productores y relatos; serie de contenidos y taller piloto")], VERDE),
    ("San Telmo / Gourmand — Circuito turístico",
     [("Público / franja", "Turístico / patrimonial; fines de semana, mediodía y tarde"),
      ("Objetivo", "Recorrido gastronómico y patrimonial de alto atractivo urbano"),
      ("Primer paso", "Definir guion y paradas; validar antes de comunicarlo")], NARANJA),
    ("Rodrigo Bueno — Cocina comunitaria y colectividades",
     [("Público / franja", "Comunitario / colectividades; fines de semana"),
      ("Objetivo", "Identidad barrial, cocina cultural y encuentro comunitario"),
      ("Primer paso", "Relevar actores y construir piloto con validación local")], AZUL2),
]


def main():
    OUT.mkdir(parents=True, exist_ok=True)

    with PdfPages(PDF) as pdf:
        # ------------------------------------------------------------------ #
        # 1. Portada institucional limpia (sin KPIs).
        # ------------------------------------------------------------------ #
        fig = page()
        fig.patches.append(Rectangle((0, 0.68), 1, 0.32, transform=fig.transFigure, facecolor=AZUL, zorder=0))
        fig.patches.append(Rectangle((0, 0.674), 1, 0.006, transform=fig.transFigure, facecolor=ROJO, zorder=1))
        fig.text(0.07, 0.945, "DGDGAS", color="white", fontsize=22, fontweight="bold")
        fig.lines.append(Line2D([0.07, 0.205], [0.927, 0.927], color=ROJO, lw=2.2, transform=fig.transFigure))
        fig.text(0.07, 0.905, "Dirección General de Gastronomía", color="white",
                 fontsize=12.5, fontweight="bold")
        fig.text(0.07, 0.878, GOBIERNO.upper(), color="#cdd9e5", fontsize=9.5, fontweight="bold")
        fig.text(0.07, 0.775, "Mercados gastronómicos de la\nCiudad de Buenos Aires", color="white",
                 fontsize=25, fontweight="bold", va="center")
        fig.text(0.07, 0.705, "Informe", color="#cdd9e5", fontsize=15, fontweight="bold", va="center")
        fig.text(0.07, 0.585, "Universo identificado, caracterización y lectura territorial",
                 fontsize=13.5, color=AZUL, fontweight="bold")
        fig.lines.append(Line2D([0.07, 0.60], [0.555, 0.555], color=ROJO, lw=2.5, transform=fig.transFigure))
        bajada = ("Un relevamiento documental de los mercados gastronómicos de la Ciudad: qué hay, dónde "
                  "están y cómo se caracterizan. Base candidata trazable, orientada a ordenar la "
                  "información disponible; no constituye censo ni padrón oficial.")
        yb = 0.500
        for ln in textwrap.wrap(bajada, 88):
            fig.text(0.07, yb, ln, fontsize=11.5, color="#333333", va="top")
            yb -= 0.028
        fig.lines.append(Line2D([0.07, 0.93], [0.135, 0.135], color="#dddddd", lw=0.8, transform=fig.transFigure))
        fig.text(0.07, 0.115, INSTITUCION, fontsize=10.5, color=AZUL, fontweight="bold", va="top")
        fig.text(0.07, 0.088, GOBIERNO, fontsize=9.5, color=GRIS, va="top")
        fig.text(0.07, 0.062, "Base candidata trazable, no oficial · requiere validación territorial.",
                 fontsize=8.5, color=GRIS, style="italic", va="top")
        pdf.savefig(fig); plt.close(fig)

        # ------------------------------------------------------------------ #
        # 2. Índice.
        # ------------------------------------------------------------------ #
        fig = page()
        head(fig, "CONTENIDO", "Índice", "", numpag(2))
        indice = [
            ("1.  Resumen ejecutivo", "3", False),
            ("2.  Objetivo y alcance", "4", False),
            ("3.  Universo, tipologías y gestión", "5", False),
            ("4.  Distribución territorial", "6", False),
            ("5.  Frecuencia y horarios documentados", "7", False),
            ("6.  Casos patrimoniales y emblemáticos", "8", False),
            ("7.  Espacios no contabilizados y cerrado documentado", "9", False),
            ("8.  Tabla final de mercados activos identificados", "10", False),
            ("9.  Cierre documental", "11", False),
            ("Anexos", "", True),
            ("A.  Metodología y fuentes", "12", False),
            ("B.  Oportunidad de gestión: mercados como red de experiencias", "13", False),
            ("C.  Lectura operativa de públicos y activación territorial", "14", False),
            ("D.  Qué decisión permite tomar este informe", "15", False),
            ("E.  Pilotos recomendados de activación", "16", False),
            ("F.  Limitaciones y próximos pasos", "17", False),
        ]
        y = 0.86
        for txt, pg, es_titulo in indice:
            color = AZUL if es_titulo else "#222222"
            fw = "bold" if es_titulo else "normal"
            fig.text(0.09, y, txt, fontsize=11 if es_titulo else 10.5, color=color, va="top", fontweight=fw)
            if pg:
                fig.text(0.91, y, pg, fontsize=10.5, color=GRIS, va="top", ha="right")
                fig.lines.append(Line2D([0.09, 0.90], [y - 0.006, y - 0.006], color="#e8e8e8",
                                        lw=0.6, transform=fig.transFigure, zorder=0))
            y -= 0.038
        foot(fig)
        pdf.savefig(fig); plt.close(fig)

        # ================================================================== #
        # CUERPO DOCUMENTAL
        # ================================================================== #

        # 3. Sección 1 — Resumen ejecutivo (documental, sin recomendaciones).
        fig = page()
        head(fig, "SECCIÓN 1", "Resumen ejecutivo",
             "Qué mercados hay, de qué tipo, dónde y con qué antecedentes.", numpag(3))
        cards(fig, 0.755, [(13, "activos identificados", AZUL), (11, "sedes fijas", VERDE),
                           (2, "itinerantes", NARANJA)], h=0.10)
        bullets(fig, 0.645, [
            "La Ciudad cuenta con 13 mercados gastronómicos activos identificados: 11 con sede fija y 2 "
            "itinerantes.",
            "El universo combina mercados históricos, patios gastronómicos, food halls, mercados de "
            "productores, un mercado barrial alimentario y una feria gastronómica.",
            "La presencia se distribuye en varias comunas, con mayor concentración en el centro histórico "
            "(Comuna 1) y en Caballito.",
            "Varios mercados tienen identidad histórica o patrimonial documentada (San Telmo, Belgrano, "
            "Progreso, San Nicolás, Bonpland).",
            "Aparte del conteo activo, se documentan 3 espacios relevantes no contabilizados y 1 cerrado, "
            "como categorías diferenciadas.",
        ], gap=0.048)
        box(fig, 0.07, 0.185, 0.86, 0.115, "Cómo leer este informe",
            "\"Activos identificados\" significa información documental disponible, no validación territorial "
            "confirmada en terreno. El relevamiento se basa en fuentes documentales y registros "
            "disponibles, con validación pendiente de campo. Es una base candidata trazable; no es censo "
            "ni padrón oficial.", "cuid")
        foot(fig)
        pdf.savefig(fig); plt.close(fig)

        # 4. Sección 2 — Objetivo y alcance (breve).
        fig = page()
        head(fig, "SECCIÓN 2", "Objetivo y alcance",
             "Qué busca ordenar el informe y qué queda fuera.", numpag(4))
        fig.text(0.07, 0.83, "Objetivo", color=AZUL, fontsize=11, fontweight="bold", va="top")
        bullets(fig, 0.795, [
            "Ordenar y caracterizar el universo de mercados gastronómicos activos de la Ciudad: qué hay, "
            "dónde están, de qué tipo son y con qué antecedentes cuentan.",
        ], gap=0.03)
        fig.text(0.07, 0.71, "Alcance", color=AZUL, fontsize=11, fontweight="bold", va="top")
        bullets(fig, 0.675, [
            "Incluye mercados históricos, patios gastronómicos, food halls, mercados de productores, "
            "mercado barrial alimentario y feria gastronómica, con sedes fijas e itinerantes.",
            "El relevamiento se basa en fuentes documentales y registros disponibles, con validación "
            "pendiente de campo (metodología en el Anexo A).",
        ], gap=0.045)
        fig.text(0.07, 0.545, "Qué queda fuera del alcance", color=AZUL, fontsize=11,
                 fontweight="bold", va="top")
        bullets(fig, 0.51, [
            "No es un censo ni un padrón oficial, ni reemplaza la validación territorial.",
            "No se cuentan como mercados gastronómicos únicos los distritos comerciales, el abasto barrial, "
            "el Mercado de las Pulgas ni el Distrito Arcos.",
            "Las coordenadas son aproximadas por barrio, para lectura territorial; no es geolocalización "
            "exacta.",
        ], gap=0.045)
        foot(fig)
        pdf.savefig(fig); plt.close(fig)

        # 5. Sección 3 — Universo, tipologías y gestión.
        fig = page()
        head(fig, "SECCIÓN 3", "Universo, tipologías y gestión",
             "Composición del universo identificado, sin doble conteo.", numpag(5))
        bullets(fig, 0.825, [
            "El relevamiento ordena 13 mercados activos identificados: 11 sedes fijas y 2 itinerantes.",
            "Cada mercado tiene una tipología primaria única; la gestión se lee como atributo operativo.",
        ], size=9.3, gap=0.034, wrap=95)
        fig.text(0.07, 0.735, "Síntesis por tipología primaria",
                 color=AZUL, fontsize=10.2, fontweight="bold", va="top")
        table(fig, [0.055, 0.545, 0.89, 0.165], TIPOLOGIAS,
              ["Tipología primaria", "N.º", "Ejemplos"],
              font=7.0, yscale=1.26, col_widths=[0.27, 0.06, 0.55])
        fig.text(0.07, 0.500, "Distribución visual",
                 color=AZUL, fontsize=10.2, fontweight="bold", va="top")
        image_fit(fig, "grafico_tipo_primario_v5.png", 0.055, 0.475, 0.47)
        image_fit(fig, "grafico_gestion_v5.png", 0.585, 0.465, 0.35)
        box(fig, 0.07, 0.130, 0.86, 0.145, "Lectura documental",
            "Predominan los patios gastronómicos (4) y los mercados históricos (3), que reúnen más de la "
            "mitad del universo. La gestión combina iniciativa privada (5), esquemas mixtos (5) y gestión "
            "pública del GCBA (3). \"Itinerante\" y \"perfil de productores\" se registran como atributos, "
            "no como tipología adicional.")
        foot(fig)
        pdf.savefig(fig); plt.close(fig)

        # 6. Sección 4 — Distribución territorial (mapa).
        fig = page()
        head(fig, "SECCIÓN 4", "Distribución territorial",
             "Mapa de las 11 sedes fijas; los itinerantes se informan aparte.", numpag(6))
        image_fit(fig, "mapa_sedes_fijas_mercados_gastronomicos_v5_2.png", 0.08, 0.83, 0.84)
        box(fig, 0.07, 0.145, 0.86, 0.115, "Itinerantes: no se mapean como punto fijo",
            "Buenos Aires Market y Sabe la Tierra integran el conteo activo identificado, pero operan con "
            "sedes variables y sin evidencia suficiente para fijar una coordenada única. Se registran como "
            "atributo de itinerancia, no como tipología adicional.", "cuid")
        foot(fig, "Ubicación aproximada por barrio, para lectura territorial; no es geolocalización exacta.")
        pdf.savefig(fig); plt.close(fig)

        # 7. Sección 5 — Frecuencia y horarios documentados.
        fig = page()
        head(fig, "SECCIÓN 5", "Frecuencia y horarios documentados",
             "Cuadro de frecuencia y horario documentado por mercado.", numpag(7))
        table(fig, [0.035, 0.335, 0.93, 0.475], HORARIOS,
              ["Mercado", "Frecuencia", "Horario documentado", "Observación"],
              font=6.45, yscale=1.24, col_widths=[0.235, 0.15, 0.35, 0.185])
        fig.text(0.07, 0.285, "Lectura", color=AZUL, fontsize=10.2, fontweight="bold", va="top")
        bullets(fig, 0.255, [
            "Conviven mercados diarios o casi diarios, mercados de días específicos e itinerantes de fin de semana.",
            "Predominan perfiles barriales y turísticos/barriales; se trata de una lectura orientativa, no una medición de afluencia.",
            "En itinerantes, el horario depende de sede y programación.",
        ], size=8.4, gap=0.030, wrap=103)
        foot(fig, "Los horarios son orientativos y deben validarse antes de su publicación operativa.")
        pdf.savefig(fig); plt.close(fig)

        # 8. Sección 6 — Casos patrimoniales.
        fig = page()
        head(fig, "SECCIÓN 6", "Casos patrimoniales y emblemáticos",
             "Identidad histórica documentada, dentro del conteo activo identificado.", numpag(8))
        pat_row1 = [(0.07, 0.60), (0.365, 0.60), (0.66, 0.60)]
        for pos, (nombre, anio, lectura, accent) in zip(pat_row1, PATRIMONIALES[:3]):
            info_card(fig, pos[0], pos[1], 0.265, 0.195, nombre,
                      [("Hito", anio), ("Lectura", lectura)], accent)
        pat_row2 = [(0.07, 0.355), (0.365, 0.355)]
        for pos, (nombre, anio, lectura, accent) in zip(pat_row2, PATRIMONIALES[3:5]):
            info_card(fig, pos[0], pos[1], 0.265, 0.195, nombre,
                      [("Hito", anio), ("Lectura", lectura)], accent)
        box(fig, 0.07, 0.15, 0.86, 0.13, "Nota",
            "Estos casos integran el conteo de 13 activos identificados: se destacan por su valor "
            "patrimonial o emblemático, no como categoría separada. El año o hito proviene de "
            "documentación pública y no constituye validación territorial.")
        foot(fig)
        pdf.savefig(fig); plt.close(fig)

        # 9. Sección 7 — Espacios no contabilizados y cerrado.
        fig = page()
        head(fig, "SECCIÓN 7", "Espacios no contabilizados y cerrado documentado",
             "Casos fuera del conteo activo, documentados como categorías diferenciadas.", numpag(9))
        nc_pos = [(0.07, 0.585), (0.52, 0.585), (0.07, 0.335), (0.52, 0.335)]
        for pos, (nombre, rows, accent) in zip(nc_pos, NO_ACTIVOS):
            info_card(fig, pos[0], pos[1], 0.41, 0.225, nombre, rows, accent)
        box(fig, 0.07, 0.13, 0.86, 0.155, "No son errores ni descartes definitivos",
            "Se documentan como categorías diferenciadas. Los relevantes no contabilizados vuelven al "
            "conteo si se valida actividad vigente. Quedan, además, fuera de alcance distritos comerciales, "
            "abasto barrial, el Mercado de las Pulgas y el Distrito Arcos, por no ser mercados "
            "gastronómicos únicos.", "cuid")
        foot(fig, "No mezclar activos con casos en revisión.")
        pdf.savefig(fig); plt.close(fig)

        # 10. Sección 8 — Tabla final.
        fig = page()
        head(fig, "SECCIÓN 8", "Tabla final de mercados activos identificados",
             "13 activos (11 de sede fija + 2 itinerantes).", numpag(10))
        table(fig, [0.05, 0.20, 0.90, 0.64], ACTIVOS,
              ["Nombre", "Tipo", "Gestión", "Barrio / comuna", "Sede", "Respaldo"],
              font=7.8, yscale=1.5, col_widths=[0.27, 0.15, 0.11, 0.20, 0.14, 0.13])
        fig.text(0.07, 0.16, "Suma exacta: 13 activos identificados (11 de sede fija + 2 itinerantes).",
                 color=GRIS, fontsize=8.5, style="italic", va="top")
        foot(fig)
        pdf.savefig(fig); plt.close(fig)

        # 11. Sección 9 — Cierre documental breve.
        fig = page()
        head(fig, "SECCIÓN 9", "Cierre documental",
             "Qué deja ordenado el informe, qué no afirma y qué queda para validar.", numpag(11))
        fig.text(0.07, 0.83, "Qué deja ordenado", color=AZUL, fontsize=11, fontweight="bold", va="top")
        bullets(fig, 0.795, [
            "Un universo identificado de 13 mercados gastronómicos activos, con tipología, gestión, "
            "distribución territorial, horarios y antecedentes patrimoniales.",
            "Una distinción clara entre activos identificados, espacios no contabilizados, cerrados y casos "
            "fuera de alcance.",
        ], gap=0.045)
        fig.text(0.07, 0.61, "Qué no afirma", color=AZUL, fontsize=11, fontweight="bold", va="top")
        bullets(fig, 0.575, [
            "No es un censo ni un padrón oficial, ni confirma la actividad en terreno de cada mercado.",
            "La información relevada no equivale a confianza territorial.",
        ], gap=0.045)
        fig.text(0.07, 0.44, "Qué queda para validar", color=AZUL, fontsize=11, fontweight="bold", va="top")
        bullets(fig, 0.405, [
            "La verificación en terreno de horarios, estado operativo y casos de respaldo medio o a validar.",
            "Las lecturas de gestión, públicos, decisiones y pilotos se desarrollan en los anexos, como "
            "insumos sujetos a validación.",
        ], gap=0.045)
        foot(fig, "No es censo ni padrón oficial.")
        pdf.savefig(fig); plt.close(fig)

        # ================================================================== #
        # ANEXOS (capas de gestión y metodología)
        # ================================================================== #

        # 12. Anexo A — Metodología y fuentes.
        fig = page()
        head(fig, "ANEXO A", "Metodología y fuentes",
             "Cómo se construyó el universo identificado.", numpag(12))
        bullets(fig, 0.84, [
            "El universo se armó cruzando fuentes públicas oficiales, sitios propios, fuentes internas "
            "sanitizadas, Google Places (señal auxiliar no oficial) y revisión documental.",
            "Un mercado se cuenta como activo cuando tiene respaldo en más de una fuente; los casos con "
            "señales contradictorias quedan documentados aparte, sin descartarse.",
            "Cada mercado tiene un tipo primario único, de modo que las categorías suman exactamente 13.",
        ], gap=0.05)
        image_fit(fig, "grafico_respaldo_fuentes_v5.png", 0.13, 0.63, 0.62)
        box(fig, 0.07, 0.20, 0.86, 0.11, "Cuidado metodológico",
            "\"Activo identificado\" es respaldo documental cruzado, no validación en terreno. Google Places "
            "es señal auxiliar no oficial. El respaldo documental (alto / medio) refleja cantidad y "
            "diversidad de fuentes; no equivale a confianza territorial.", "cuid")
        foot(fig)
        pdf.savefig(fig); plt.close(fig)

        # 13. Anexo B — Oportunidad de gestión.
        fig = page()
        head(fig, "ANEXO B", "Oportunidad de gestión: mercados como red de experiencias",
             "Los mercados pueden comunicarse como experiencias urbanas, no solo como infraestructura.",
             numpag(13))
        op_pos = [(0.07, 0.585), (0.52, 0.585), (0.07, 0.340), (0.52, 0.340)]
        for pos, (title, uso, aplica, accent) in zip(op_pos, OPORTUNIDAD[:4]):
            opportunity_card(fig, pos[0], pos[1], 0.41, 0.220, title,
                             [("Qué permite", uso), ("Dónde aplica", aplica)], accent)
        opportunity_card(fig, 0.07, 0.125, 0.86, 0.185, OPORTUNIDAD[4][0],
                         [("Qué permite", OPORTUNIDAD[4][1]), ("Dónde aplica", OPORTUNIDAD[4][2])],
                         OPORTUNIDAD[4][3], title_size=8.2, body_size=7.2)
        foot(fig, "Lectura de gestión orientativa; las activaciones requieren validación territorial previa.")
        pdf.savefig(fig); plt.close(fig)

        # 14. Anexo C — Lectura operativa de públicos.
        fig = page()
        head(fig, "ANEXO C", "Lectura operativa de públicos y activación territorial",
             "Matriz compacta para orientar programación y comunicación.", numpag(14))
        fig.text(0.07, 0.835, "Lectura operativa por perfil", color=AZUL,
                 fontsize=10.5, fontweight="bold", va="top")
        matrix(fig, 0.07, 0.795, 0.86,
               ["Perfil operativo", "Mercados principales", "Uso recomendado"],
               PUBLICOS_MATRIZ, [0.28, 0.37, 0.35],
               font=8.2, header_font=8.0, min_row_h=0.090, line_gap=0.017)
        box(fig, 0.07, 0.205, 0.86, 0.095, "Cómo usar la matriz",
            "Los perfiles orientan programación y comunicación. No miden afluencia ni reemplazan la "
            "validación territorial de horarios, público efectivo y operación.", "cuid")
        foot(fig, "Lectura orientativa para programación y comunicación; requiere validación en terreno.")
        pdf.savefig(fig); plt.close(fig)

        # 15. Anexo D — Qué decisión permite tomar.
        fig = page()
        head(fig, "ANEXO D", "Qué decisión permite tomar este informe",
             "Seis líneas de acción posibles para la gestión.", numpag(15))
        decisiones_tabla = [[title, uso, ejemplo] for title, uso, ejemplo, _accent in DECISIONES]
        matrix(fig, 0.07, 0.805, 0.86,
               ["Línea de acción", "Uso", "Aplica a"],
               decisiones_tabla, [0.26, 0.42, 0.32],
               font=7.5, header_font=7.5, min_row_h=0.078, line_gap=0.0152)
        box(fig, 0.07, 0.120, 0.86, 0.082, "Cierre de gestión",
            "Muestra dónde mirar, qué validar y qué no mezclar. Las decisiones sobre casos en revisión "
            "requieren validación territorial previa.")
        foot(fig)
        pdf.savefig(fig); plt.close(fig)

        # 16. Anexo E — Pilotos recomendados.
        fig = page()
        head(fig, "ANEXO E", "Pilotos recomendados de activación",
             "Hipótesis operativas para volver el informe accionable, sujetas a validación.", numpag(16))
        pilotos_tabla = []
        for title, rows, _accent in PILOTOS:
            values = dict(rows)
            pilotos_tabla.append([
                title,
                values["Público / franja"],
                values["Objetivo"],
                values["Primer paso"],
            ])
        matrix(fig, 0.055, 0.815, 0.89,
               ["Piloto", "Público / franja", "Objetivo", "Primer paso"],
               pilotos_tabla, [0.24, 0.23, 0.27, 0.26],
               font=6.95, header_font=7.0, min_row_h=0.106, line_gap=0.0140, pad_x=0.009)
        foot(fig, "Son hipótesis operativas de gestión; cada piloto requiere validación territorial antes de ejecutarse.")
        pdf.savefig(fig); plt.close(fig)

        # 17. Anexo F — Limitaciones y próximos pasos.
        fig = page()
        head(fig, "ANEXO F", "Limitaciones y próximos pasos",
             "Qué no afirma el informe y qué conviene validar.", numpag(17))
        box(fig, 0.07, 0.66, 0.86, 0.15, "Limitaciones",
            "Relevamiento documental y multifuente. No reemplaza la validación territorial ni el registro "
            "oficial. Google Places es señal auxiliar no oficial. Horarios autodeclarados y a veces "
            "divergentes. Coordenadas aproximadas por barrio. El respaldo documental no equivale a "
            "confianza territorial.", "cuid")
        fig.text(0.07, 0.615, "Próximos pasos", color=AZUL, fontsize=10.5, fontweight="bold", va="top")
        bullets(fig, 0.58, [
            "Validar en terreno los casos de respaldo medio o a validar.",
            "Monitorear los espacios con señales de cierre (Soho, Mercat Caballito, El Galpón).",
            "Homogeneizar la información pública de horarios, gestión y oferta.",
            "Mantener la base candidata como insumo actualizable, no como total definitivo.",
        ], gap=0.045)
        box(fig, 0.07, 0.16, 0.86, 0.145, "Qué aporta este relevamiento",
            "Una base candidata trazable que distingue tipologías, separa con claridad activos "
            "identificados, casos en revisión, cerrados y fuera de alcance, y ordena la información "
            "disponible para decidir y validar. Es una base para trabajar, no un padrón oficial.")
        foot(fig, "No es censo ni padrón oficial.")
        pdf.savefig(fig); plt.close(fig)

        d = pdf.infodict()
        d["Title"] = TITULO
        d["Author"] = INSTITUCION
        d["Subject"] = "Base candidata trazable, no oficial. Relevamiento documental de mercados gastronómicos de CABA."

    print(f"PDF generado: {PDF}")
    print(f"Páginas: {TOTAL_PAG} | tamaño: {PDF.stat().st_size/1024:.0f} KB")


if __name__ == "__main__":
    main()
