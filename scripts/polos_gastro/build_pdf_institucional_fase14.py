"""Build the Fase 14 institutional PDF for PolosGastro.

The script reads already-generated map assets, creates sanitized copies for the
institutional layout, and writes a PDF plus an HTML preview. It does not call
external services, mutate source data, or touch previous report drafts.
"""
from __future__ import annotations

import html
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs" / "polos_gastro" / "fase14_pdf_institucional"
ASSETS = OUT / "assets"
SRC_MAPS = ROOT / "outputs" / "polos_gastro" / "fase13_mapas" / "assets"

PDF = OUT / "INFORME_POLOS_GASTRO_DGDGAS_PRELIMINAR.pdf"
HTML = OUT / "preview_informe_polos_gastro_dgdgas.html"

INSTITUCION = "DGDGAS — Dirección General de Desarrollo Gastronómico"
GOBIERNO = "Gobierno de la Ciudad de Buenos Aires"
TITLE = "Polos gastronómicos de la Ciudad de Buenos Aires"
SUBTITLE = "Universo semilla, lectura territorial y capa auxiliar de geolocalización"

W, H = A4
M = 48

AZUL = "#1F3B57"
AZUL2 = "#2C6E9E"
ROJO = "#C0392B"
GRIS = "#555555"
GRIS2 = "#6B7280"
LINEA = "#D9DEE5"
SOFT = "#EEF2F6"
SOFT_AZUL = "#EAF1F8"
SOFT_VERDE = "#EAF5EE"
SOFT_NARANJA = "#F8EDE0"
VERDE = "#1A9850"
NARANJA = "#C0762B"
NEGRO = "#222222"

TOTAL_PAGES = 18

FONT = "Helvetica"
FONT_BOLD = "Helvetica-Bold"


def register_fonts() -> None:
    global FONT, FONT_BOLD
    candidates = [
        (Path("C:/Windows/Fonts/arial.ttf"), Path("C:/Windows/Fonts/arialbd.ttf"), "ArialDG"),
        (Path("C:/Windows/Fonts/calibri.ttf"), Path("C:/Windows/Fonts/calibrib.ttf"), "CalibriDG"),
    ]
    for regular, bold, name in candidates:
        if regular.exists() and bold.exists():
            pdfmetrics.registerFont(TTFont(name, str(regular)))
            pdfmetrics.registerFont(TTFont(f"{name}-Bold", str(bold)))
            FONT = name
            FONT_BOLD = f"{name}-Bold"
            return


def hex_to_rgb(value: str) -> tuple[float, float, float]:
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) / 255 for i in (0, 2, 4))


def set_fill(c: canvas.Canvas, color: str) -> None:
    c.setFillColorRGB(*hex_to_rgb(color))


def set_stroke(c: canvas.Canvas, color: str) -> None:
    c.setStrokeColorRGB(*hex_to_rgb(color))


def wrap_text(text: str, font: str, size: float, max_width: float) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        trial = " ".join(current + [word])
        if pdfmetrics.stringWidth(trial, font, size) <= max_width or not current:
            current.append(word)
        else:
            lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines


def draw_wrapped(
    c: canvas.Canvas,
    text: str,
    x: float,
    y: float,
    max_width: float,
    *,
    font: str = FONT,
    size: float = 10,
    color: str = NEGRO,
    leading: float | None = None,
    max_lines: int | None = None,
) -> float:
    leading = leading or size * 1.28
    lines = wrap_text(text, font, size, max_width)
    if max_lines is not None:
        lines = lines[:max_lines]
    c.setFont(font, size)
    set_fill(c, color)
    for line in lines:
        c.drawString(x, y, line)
        y -= leading
    return y


def draw_title(c: canvas.Canvas, x: float, y: float, text: str, size: float = 19) -> float:
    set_fill(c, AZUL)
    c.setFont(FONT_BOLD, size)
    for line in wrap_text(text, FONT_BOLD, size, W - 2 * M):
        c.drawString(x, y, line)
        y -= size * 1.12
    set_stroke(c, ROJO)
    c.setLineWidth(2)
    c.line(x, y + 8, x + 165, y + 8)
    return y - 10


def header(c: canvas.Canvas, page_no: int, kicker: str, title: str, subtitle: str = "") -> float:
    set_fill(c, ROJO)
    c.setFont(FONT_BOLD, 8.5)
    c.drawString(M, H - 35, kicker.upper())
    set_fill(c, GRIS)
    c.setFont(FONT, 8.5)
    c.drawRightString(W - M, H - 35, f"{page_no} / {TOTAL_PAGES}")
    y = draw_title(c, M, H - 62, title, 18)
    if subtitle:
        y = draw_wrapped(c, subtitle, M, y, W - 2 * M, font=FONT, size=10, color=GRIS, leading=13)
    return y - 8


def footer(c: canvas.Canvas, note: str | None = None) -> None:
    set_stroke(c, LINEA)
    c.setLineWidth(0.8)
    c.line(M, 47, W - M, 47)
    if note:
        draw_wrapped(c, note, M, 62, W - 2 * M, font=FONT, size=7.4, color=GRIS, leading=9)
    set_fill(c, AZUL)
    c.setFont(FONT_BOLD, 7.8)
    c.drawString(M, 30, f"{INSTITUCION} · {GOBIERNO}")


def finish(c: canvas.Canvas, note: str | None = None) -> None:
    footer(c, note)
    c.showPage()


def bullets(c: canvas.Canvas, items: list[str], x: float, y: float, max_width: float, *, size: float = 10.2,
            gap: float = 10) -> float:
    for item in items:
        lines = wrap_text(item, FONT, size, max_width - 18)
        set_fill(c, ROJO)
        c.setFont(FONT_BOLD, size)
        c.drawString(x, y, "•")
        set_fill(c, NEGRO)
        c.setFont(FONT, size)
        yy = y
        for line in lines:
            c.drawString(x + 16, yy, line)
            yy -= size * 1.28
        y = yy - gap
    return y


def note_box(c: canvas.Canvas, x: float, y: float, w: float, h: float, title: str, text: str,
             *, color: str = AZUL2, fill: str = SOFT_AZUL) -> None:
    set_fill(c, fill)
    set_stroke(c, color)
    c.setLineWidth(1.1)
    c.rect(x, y, w, h, fill=1, stroke=1)
    set_fill(c, color)
    c.rect(x, y, 8, h, fill=1, stroke=0)
    set_fill(c, color)
    c.setFont(FONT_BOLD, 9.2)
    c.drawString(x + 18, y + h - 19, title)
    draw_wrapped(c, text, x + 18, y + h - 37, w - 32, font=FONT, size=8.6, color=NEGRO, leading=11)


def kpi_card(c: canvas.Canvas, x: float, y: float, w: float, h: float, value: str, label: str, color: str) -> None:
    set_fill(c, SOFT)
    set_stroke(c, color)
    c.setLineWidth(1.3)
    c.roundRect(x, y, w, h, 3, fill=1, stroke=1)
    set_fill(c, color)
    c.setFont(FONT_BOLD, 22)
    c.drawCentredString(x + w / 2, y + h - 32, value)
    set_fill(c, GRIS)
    c.setFont(FONT, 7.8)
    yy = y + h - 49
    for line in wrap_text(label, FONT, 7.8, w - 14):
        c.drawCentredString(x + w / 2, yy, line)
        yy -= 9


def cards_row(c: canvas.Canvas, y: float, cards: list[tuple[str, str, str]], *, x: float = M, total_w: float | None = None,
              h: float = 70) -> None:
    total_w = total_w or (W - 2 * M)
    gap = 8
    card_w = (total_w - gap * (len(cards) - 1)) / len(cards)
    for i, (value, label, color) in enumerate(cards):
        kpi_card(c, x + i * (card_w + gap), y, card_w, h, value, label, color)


def image_box(c: canvas.Canvas, img_path: Path, x: float, y: float, max_w: float, max_h: float,
              *, border: bool = True) -> tuple[float, float]:
    img = Image.open(img_path)
    iw, ih = img.size
    scale = min(max_w / iw, max_h / ih)
    dw, dh = iw * scale, ih * scale
    dx = x + (max_w - dw) / 2
    dy = y + (max_h - dh) / 2
    if border:
        set_fill(c, "#FFFFFF")
        set_stroke(c, LINEA)
        c.rect(x, y, max_w, max_h, fill=1, stroke=1)
    c.drawImage(ImageReader(str(img_path)), dx, dy, width=dw, height=dh, mask="auto")
    return dw, dh


def legend_detail(c: canvas.Canvas, x: float, y: float) -> None:
    c.setFont(FONT, 8.5)
    set_fill(c, AZUL2)
    c.circle(x + 5, y + 4, 4, fill=1, stroke=0)
    set_fill(c, NEGRO)
    c.drawString(x + 17, y, "Coincidencia fuerte")
    set_fill(c, VERDE)
    c.circle(x + 145, y + 4, 4, fill=1, stroke=0)
    set_fill(c, NEGRO)
    c.drawString(x + 157, y, "Coincidencia razonable")
    set_stroke(c, NARANJA)
    set_fill(c, "#FFFFFF")
    p = c.beginPath()
    p.moveTo(x + 322, y + 11)
    p.lineTo(x + 314, y - 2)
    p.lineTo(x + 330, y - 2)
    p.close()
    c.drawPath(p, fill=1, stroke=1)
    set_fill(c, NEGRO)
    c.drawString(x + 340, y, "Zona o sede a revisar")


def sanitize_maps() -> dict[str, Path]:
    ASSETS.mkdir(parents=True, exist_ok=True)
    specs = {
        "global": ("mapa_global_22_polos_ejes.png", (105, 360, 1985, 2465), None),
        "palermo": ("mapa_detalle_palermo_las_canitas.png", (0, 170, None, 1325), None),
        "puerto": ("mapa_detalle_puerto_madero.png", (0, 170, None, 1325), None),
        "san_telmo": ("mapa_detalle_san_telmo.png", (0, 170, None, 1325), None),
        "corrientes": ("mapa_detalle_corrientes_abasto.png", (0, 170, None, 1300), None),
        "belgrano": ("mapa_detalle_belgrano.png", (0, 170, None, 1660), "detail"),
    }
    out: dict[str, Path] = {}
    for key, (name, crop, kind) in specs.items():
        src = SRC_MAPS / name
        img = Image.open(src).convert("RGBA")
        left, top, right, bottom = crop
        right = right or img.size[0]
        img = img.crop((left, top, right, bottom))
        base = Image.new("RGB", img.size, "white")
        base.paste(img, mask=img.split()[-1])
        if kind in {"detail", "detail_tall"}:
            draw = ImageDraw.Draw(base)
            w, h = base.size
            top_mask = h - (390 if kind == "detail_tall" else 330)
            draw.rectangle((0, top_mask, min(1080, w), h - 8), fill="white")
        dest = ASSETS / f"{key}_mapa_pdf.png"
        base.save(dest, optimize=True)
        out[key] = dest
    return out


def cover(c: canvas.Canvas) -> None:
    set_fill(c, AZUL)
    c.rect(0, H * 0.68, W, H * 0.32, fill=1, stroke=0)
    set_fill(c, ROJO)
    c.rect(0, H * 0.675, W, 5, fill=1, stroke=0)
    set_fill(c, "#FFFFFF")
    c.setFont(FONT_BOLD, 22)
    c.drawString(M, H - 58, "DGDGAS")
    set_stroke(c, ROJO)
    c.setLineWidth(2.2)
    c.line(M, H - 72, M + 110, H - 72)
    c.setFont(FONT_BOLD, 12.5)
    c.drawString(M, H - 95, "Dirección General de Desarrollo Gastronómico")
    c.setFont(FONT_BOLD, 9)
    set_fill(c, "#CDD9E5")
    c.drawString(M, H - 117, GOBIERNO.upper())
    set_fill(c, "#FFFFFF")
    c.setFont(FONT_BOLD, 25)
    c.drawString(M, H - 210, "Polos gastronómicos de la")
    c.drawString(M, H - 240, "Ciudad de Buenos Aires")
    set_fill(c, "#CDD9E5")
    c.setFont(FONT_BOLD, 14)
    c.drawString(M, H - 275, "Informe")
    set_fill(c, AZUL)
    c.setFont(FONT_BOLD, 13.5)
    c.drawString(M, H - 350, SUBTITLE)
    set_stroke(c, ROJO)
    c.setLineWidth(2.5)
    c.line(M, H - 370, M + 370, H - 370)
    bajada = (
        "Lectura institucional del universo semilla de polos y ejes gastronómicos, "
        "con mapas territoriales y una capa auxiliar para orientar validación. "
        "Base de trabajo para revisión territorial; no constituye padrón oficial."
    )
    draw_wrapped(c, bajada, M, H - 410, W - 2 * M, font=FONT, size=11.2, color=NEGRO, leading=15)
    set_stroke(c, LINEA)
    c.setLineWidth(0.8)
    c.line(M, 120, W - M, 120)
    set_fill(c, AZUL)
    c.setFont(FONT_BOLD, 10.5)
    c.drawString(M, 98, INSTITUCION)
    set_fill(c, GRIS)
    c.setFont(FONT, 9.2)
    c.drawString(M, 76, GOBIERNO)
    c.drawString(M, 54, "Julio 2026")
    c.showPage()


def index_page(c: canvas.Canvas) -> None:
    header(c, 2, "Contenido", "Índice")
    items = [
        ("Resumen ejecutivo", "3"),
        ("Alcance y criterio de lectura", "4"),
        ("Mapa global de 22 polos/ejes", "5"),
        ("Lectura territorial general", "6"),
        ("Detalle: Palermo / Las Cañitas", "7"),
        ("Detalle: Puerto Madero", "8"),
        ("Detalle: San Telmo", "9"),
        ("Corrientes / Abasto", "10"),
        ("Belgrano y subzonas", "11"),
        ("Hallazgos de la capa auxiliar", "12"),
        ("Decisiones pendientes", "13"),
        ("Recomendaciones prudentes", "14"),
        ("Próximos pasos", "15"),
        ("Anexos", "16-18"),
    ]
    y = H - 150
    for label, page in items:
        set_fill(c, NEGRO)
        c.setFont(FONT, 10.8)
        c.drawString(M + 18, y, label)
        set_stroke(c, "#E6E8EC")
        c.setLineWidth(0.6)
        c.line(M + 18, y - 5, W - M - 32, y - 5)
        set_fill(c, GRIS)
        c.drawRightString(W - M, y, page)
        y -= 31
    finish(c)


def summary_page(c: canvas.Canvas) -> None:
    y = header(c, 3, "Resumen ejecutivo", "Qué ordena este informe",
               "Universo semilla, lectura territorial y señales para orientar validación.")
    cards_row(c, y - 70, [
        ("22", "polos/ejes del universo semilla", AZUL),
        ("106", "menciones de locales relevadas", VERDE),
        ("59", "coincidencias razonables o fuertes", AZUL2),
    ])
    cards_row(c, y - 150, [
        ("8", "casos con vigencia no confirmada", NARANJA),
        ("0", "resultados fuera de CABA", ROJO),
    ], x=M + 84, total_w=W - 2 * M - 168)
    y2 = y - 200
    bullets(c, [
        "El informe ordena un universo semilla de polos y ejes gastronómicos, sin descartar zonas por falta de locales explícitos.",
        "La capa auxiliar permite ubicar menciones, detectar duplicados y distinguir casos que requieren validación.",
        "El mapa global muestra los 22 polos/ejes como áreas, ejes o zonas de lectura; no representa un padrón de locales activos.",
        "Los casos cerrados, duplicados o a corregir no se presentan como activos.",
    ], M, y2, W - 2 * M, gap=9)
    note_box(
        c, M, 115, W - 2 * M, 80,
        "Cómo leer los números",
        "Son magnitudes del universo semilla y de la capa auxiliar de trabajo. Sirven para orientar revisión territorial y decisiones de gestión; no equivalen a un censo ni a validación definitiva de actividad vigente.",
        color=AZUL,
        fill=SOFT_AZUL,
    )
    finish(c)


def scope_page(c: canvas.Canvas) -> None:
    y = header(c, 4, "Alcance y criterio de lectura", "Qué afirma y qué no afirma la pieza")
    note_box(c, M, y - 92, W - 2 * M, 72, "Universo semilla",
             "Conjunto inicial de 22 polos/ejes y 106 menciones de locales. Todos los polos se conservan en la lectura global, incluso aquellos sin locales explícitos.",
             color=AZUL2, fill=SOFT_AZUL)
    note_box(c, M, y - 182, W - 2 * M, 72, "Capa auxiliar",
             "Aporta ubicación, consistencia territorial y alertas de calidad. Acompaña la lectura; no reemplaza fuentes oficiales ni validación territorial.",
             color=VERDE, fill=SOFT_VERDE)
    set_fill(c, AZUL)
    c.setFont(FONT_BOLD, 11)
    c.drawString(M, y - 230, "El informe no afirma")
    bullets(c, [
        "que las 106 menciones correspondan a locales activos;",
        "que los límites territoriales sean oficiales;",
        "que una herramienta de geolocalización valide por sí sola un polo o una sede;",
        "que las zonas con menor evidencia deban descartarse.",
    ], M, y - 260, W - 2 * M, gap=8)
    note_box(c, M, 112, W - 2 * M, 82, "Criterio institucional",
             "La pieza prioriza claridad para conducción: hallazgos principales en el cuerpo, detalles metodológicos en anexos y lenguaje prudente frente a casos no confirmados.",
             color=NARANJA, fill=SOFT_NARANJA)
    finish(c)


def global_map_page(c: canvas.Canvas, maps: dict[str, Path]) -> None:
    y = header(c, 5, "Mapa global", "22 polos/ejes del universo semilla",
               "Áreas, ejes y zonas de lectura territorial; no delimitaciones oficiales.")
    image_box(c, maps["global"], M + 20, 112, W - 2 * M - 40, y - 120, border=False)
    finish(c, "El mapa representa el universo semilla completo y no reemplaza validación territorial.")


def territorial_page(c: canvas.Canvas) -> None:
    y = header(c, 6, "Lectura territorial general", "Qué muestra la distribución")
    note_box(c, M, y - 92, W - 2 * M, 76, "Polos consolidados",
             "Palermo concentra la mayor cantidad de menciones. Puerto Madero, San Telmo, Recoleta, Microcentro/Centro y Villa Crespo permiten una lectura inicial de zonas reconocibles.",
             color=AZUL2, fill=SOFT_AZUL)
    note_box(c, M, y - 192, W - 2 * M, 82, "Corredores y ejes",
             "Avenida Corrientes, Costanera Norte y Caseros/Barracas conviene leerlos como corredores o tramos, no como polígonos cerrados. El recorte operativo requiere validación.",
             color=VERDE, fill=SOFT_VERDE)
    note_box(c, M, y - 302, W - 2 * M, 96, "Áreas a validar o fortalecer",
             "Los polos sin locales explícitos integran el mapa global y requieren refuerzo documental. Belgrano se presenta como macroárea con subzonas de respaldo desigual.",
             color=NARANJA, fill=SOFT_NARANJA)
    bullets(c, [
        "Corrientes se trabaja como eje teatral-gastronómico entre 9 de Julio y Callao.",
        "Abasto se trabaja como área alrededor del shopping, con radio aproximado de cinco cuadras.",
        "Ambos están vinculados, pero tienen delimitación distinta y deben evitar doble conteo.",
    ], M, 250, W - 2 * M, gap=9)
    finish(c)


def detail_map_page(
    c: canvas.Canvas,
    page_no: int,
    key: str,
    title: str,
    subtitle: str,
    text: str,
    caution: str,
    maps: dict[str, Path],
    *,
    caution_color: str = AZUL2,
) -> None:
    y = header(c, page_no, "Detalle territorial", title, subtitle)
    image_box(c, maps[key], M + 16, 252, W - 2 * M - 32, y - 270, border=True)
    legend_detail(c, M + 42, 222)
    draw_wrapped(c, text, M, 184, W - 2 * M, font=FONT, size=9.4, color=NEGRO, leading=12)
    note_box(c, M, 91, W - 2 * M, 64, "Nota de lectura", caution, color=caution_color,
             fill=SOFT_AZUL if caution_color != NARANJA else SOFT_NARANJA)
    finish(c)


def auxiliary_page(c: canvas.Canvas) -> None:
    y = header(c, 12, "Capa auxiliar", "Hallazgos para orientar validación")
    cards_row(c, y - 70, [
        ("59", "coincidencias razonables o fuertes", VERDE),
        ("8", "vigencia no confirmada", NARANJA),
        ("11", "duplicados probables", AZUL2),
    ])
    cards_row(c, y - 150, [
        ("25", "zona o sede a revisar", NARANJA),
        ("3", "búsquedas a corregir", ROJO),
    ], x=M + 84, total_w=W - 2 * M - 168)
    bullets(c, [
        "Las coincidencias razonables o fuertes permiten orientar la revisión territorial.",
        "Los casos con vigencia no confirmada se conservan como referencia semilla, pero no se presentan como activos.",
        "Los duplicados deben resolverse antes de mapas operativos para evitar doble conteo.",
        "Las zonas o sedes a revisar se tratan como alertas, no como evidencia cerrada.",
    ], M, y - 215, W - 2 * M, gap=9)
    note_box(c, M, 112, W - 2 * M, 82, "Uso recomendado",
             "Usar esta capa para priorizar revisión con la contraparte y ajustar mapas de detalle. No presentarla como fuente oficial ni como validación definitiva.",
             color=AZUL, fill=SOFT_AZUL)
    finish(c)


def pending_page(c: canvas.Canvas) -> None:
    y = header(c, 13, "Decisiones pendientes", "Qué cerrar antes de la versión final")
    bullets(c, [
        "Validar con Ale el recorte de Corrientes y Abasto.",
        "Definir si los mapas de detalle muestran nombres de locales, solo puntos o zonas.",
        "Resolver sedes en duplicados y cadenas antes de cualquier mapa operativo.",
        "Revisar polos con menos evidencia explícita y decidir si requieren refuerzo documental.",
        "Definir si las recomendaciones quedan en el cuerpo o se trasladan a anexos.",
    ], M, y - 12, W - 2 * M, gap=13)
    note_box(c, M, 160, W - 2 * M, 92, "Bloqueo principal",
             "La versión final depende de cerrar criterios de publicación territorial: delimitaciones, sedes, nombres visibles y tratamiento de zonas con evidencia menor.",
             color=ROJO, fill="#FBEAEA")
    finish(c)


def recommendations_page(c: canvas.Canvas) -> None:
    y = header(c, 14, "Recomendaciones prudentes", "Uso institucional de la pieza")
    note_box(c, M, y - 84, W - 2 * M, 66, "Mapa global",
             "Usarlo como lectura institucional del universo semilla, con nota clara de que no define límites oficiales.",
             color=AZUL2, fill=SOFT_AZUL)
    note_box(c, M, y - 168, W - 2 * M, 66, "Mapas de detalle",
             "Usarlos como apoyo para revisión territorial. Evitar tratarlos como listado operativo hasta resolver sedes y duplicados.",
             color=VERDE, fill=SOFT_VERDE)
    note_box(c, M, y - 252, W - 2 * M, 66, "Nomenclatura",
             "Consolidar nombres de polos, subzonas y ejes para que la pieza sea consistente en mapas, texto y anexos.",
             color=NARANJA, fill=SOFT_NARANJA)
    bullets(c, [
        "Separar siempre hallazgos, límites y próximos pasos.",
        "Mantener la capa auxiliar como insumo de orientación, no como fuente oficial.",
        "Validar territorialmente antes de publicar detalle operativo.",
    ], M, 240, W - 2 * M, gap=11)
    finish(c)


def next_steps_page(c: canvas.Canvas) -> None:
    y = header(c, 15, "Próximos pasos", "Secuencia sugerida")
    steps = [
        ("1", "Revisión con Ale", "Cerrar delimitaciones, sedes y criterios de publicación."),
        ("2", "Ajuste de mapas", "Corregir mapa final según decisiones de Corrientes, Abasto y Belgrano."),
        ("3", "Versión ejecutiva", "Preparar una síntesis más breve si el destino requiere lectura de conducción."),
        ("4", "PDF final", "Generar la versión final después de cerrar decisiones territoriales y visuales."),
    ]
    y0 = y - 20
    for n, title, text in steps:
        set_fill(c, ROJO)
        c.circle(M + 12, y0 - 2, 11, fill=1, stroke=0)
        set_fill(c, "#FFFFFF")
        c.setFont(FONT_BOLD, 10)
        c.drawCentredString(M + 12, y0 - 6, n)
        set_fill(c, AZUL)
        c.setFont(FONT_BOLD, 11)
        c.drawString(M + 38, y0 + 3, title)
        draw_wrapped(c, text, M + 38, y0 - 15, W - 2 * M - 38, font=FONT, size=9.6, color=NEGRO, leading=12)
        y0 -= 92
    note_box(c, M, 120, W - 2 * M, 72, "Criterio de cierre",
             "La pieza final debe mantener el mismo estándar: marca DGDGAS, sin datos sensibles, sin rutas ni referencias técnicas, y con cautelas visibles sobre alcance.",
             color=AZUL, fill=SOFT_AZUL)
    finish(c)


def annex_universe(c: canvas.Canvas) -> None:
    header(c, 16, "Anexo A", "Universo semilla de 22 polos/ejes")
    rows = [
        ("Palermo", "Polo consolidado con subpolos", "19"),
        ("Villa Crespo", "Polo de barrio", "9"),
        ("Puerto Madero", "Polo consolidado costero", "9"),
        ("San Telmo", "Polo consolidado con hito colectivo", "8"),
        ("Chacarita", "Polo de barrio", "7"),
        ("Belgrano", "Macroárea con subzonas", "11"),
        ("Recoleta", "Polo de barrio", "8"),
        ("Caballito", "Polo de barrio", "5"),
        ("Costanera Norte", "Corredor / área costera", "6"),
        ("Avenida Caseros / Barracas", "Corredor / eje", "5"),
        ("Microcentro y Centro", "Área central", "7"),
        ("Avenida Corrientes", "Eje cultural-gastronómico", "6"),
        ("Abasto", "Subzona vinculada a Corrientes", "6"),
        ("Avenida Boedo", "Corredor / eje", "0"),
        ("Devoto", "Polo de barrio", "0"),
        ("Corredor DoHo / Donado-Holmberg", "Corredor / eje", "0"),
        ("Villa Urquiza", "Polo de barrio", "0"),
        ("Nuevo Bajo Retiro / Esmeralda y Paraguay", "Subzona central", "0"),
        ("Avenida Federico Lacroze", "Corredor / eje", "0"),
        ("Parque Saavedra / Av. García del Río", "Zona / corredor barrial", "0"),
        ("Circuito gastronómico de Paternal", "Área de revisión", "0"),
        ("Villa Pueyrredón / Av. San Martín", "Barrio / corredor", "0"),
    ]
    x = M
    y = H - 138
    col_w = [220, 210, 70]
    row_h = 20
    set_fill(c, AZUL)
    c.rect(x, y, sum(col_w), row_h, fill=1, stroke=0)
    set_fill(c, "#FFFFFF")
    c.setFont(FONT_BOLD, 8.4)
    c.drawString(x + 7, y + 6, "Polo/eje")
    c.drawString(x + col_w[0] + 7, y + 6, "Tipo de lectura")
    c.drawRightString(x + sum(col_w) - 7, y + 6, "Menciones")
    y -= row_h
    c.setFont(FONT, 7.6)
    for idx, row in enumerate(rows):
        set_fill(c, "#FFFFFF" if idx % 2 == 0 else "#F7F9FB")
        c.rect(x, y, sum(col_w), row_h, fill=1, stroke=0)
        set_stroke(c, LINEA)
        c.rect(x, y, sum(col_w), row_h, fill=0, stroke=1)
        set_fill(c, AZUL if row[2] == "0" else NEGRO)
        c.drawString(x + 7, y + 6, row[0])
        set_fill(c, NEGRO)
        c.drawString(x + col_w[0] + 7, y + 6, row[1])
        c.drawRightString(x + sum(col_w) - 7, y + 6, row[2])
        y -= row_h
    note_box(c, M, 88, W - 2 * M, 60, "Nota",
             "Los polos con cero menciones explícitas permanecen en el universo semilla y se representan en el mapa global como áreas o ejes a fortalecer.",
             color=AZUL2, fill=SOFT_AZUL)
    finish(c)


def annex_method(c: canvas.Canvas) -> None:
    y = header(c, 17, "Anexo B", "Criterio cartográfico y uso de mapas")
    bullets(c, [
        "El mapa global representa áreas, macroáreas, ejes o zonas aproximadas del universo semilla.",
        "Los polos sin locales explícitos se muestran como parte del universo y requieren refuerzo documental.",
        "Los mapas de detalle usan puntos de la capa auxiliar para orientar validación de sedes.",
        "Los casos con vigencia no confirmada, duplicados sin resolver y búsquedas a corregir quedan fuera de mapas operativos.",
        "Los hitos colectivos se tratan como referencia territorial, no como restaurante puntual.",
    ], M, y - 12, W - 2 * M, gap=10)
    note_box(c, M, 132, W - 2 * M, 86, "Lectura metodológica",
             "Ningún mapa define límites oficiales ni confirma actividad vigente. La cartografía acompaña una lectura institucional y debe ajustarse con validación territorial antes de circular como herramienta operativa.",
             color=NARANJA, fill=SOFT_NARANJA)
    finish(c)


def annex_limits(c: canvas.Canvas) -> None:
    y = header(c, 18, "Anexos C, D y E", "Capa auxiliar, casos no mapeables y limitaciones")
    note_box(c, M, y - 80, W - 2 * M, 64, "Capa auxiliar de geolocalización",
             "Se usa para ubicar menciones, detectar duplicados, marcar vigencia no confirmada y distinguir zonas o sedes a revisar.",
             color=AZUL2, fill=SOFT_AZUL)
    note_box(c, M, y - 166, W - 2 * M, 70, "Casos no mapeables hasta validar",
             "No se incorporan al mapa operativo casos cerrados o con vigencia no confirmada, duplicados sin sede resuelta, búsquedas a corregir ni zonas/sedes sin confirmación suficiente.",
             color=ROJO, fill="#FBEAEA")
    set_fill(c, AZUL)
    c.setFont(FONT_BOLD, 11)
    c.drawString(M, y - 210, "Limitaciones principales")
    bullets(c, [
        "El universo surge de una base semilla y requiere validación territorial.",
        "Las áreas y ejes son aproximados y no tienen carácter oficial.",
        "La capa auxiliar no confirma actividad vigente.",
        "Las subzonas con menor respaldo requieren refuerzo documental.",
        "La versión final debe cerrar criterios de publicación de mapas y nomenclatura.",
    ], M, y - 238, W - 2 * M, gap=9)
    finish(c)


def build_html(maps: dict[str, Path]) -> None:
    rel = {key: f"assets/{path.name}" for key, path in maps.items()}
    sections = [
        ("Resumen ejecutivo", "22 polos/ejes, 106 menciones de locales, 59 coincidencias razonables o fuertes, 8 casos con vigencia no confirmada y 0 resultados fuera de CABA."),
        ("Alcance", "Base de trabajo para revisión territorial. No constituye padrón oficial ni delimitación territorial definitiva."),
        ("Mapa global", "<img src='%s' alt='Mapa global de polos gastronomicos'>" % rel["global"]),
        ("Palermo / Las Cañitas", "<img src='%s' alt='Mapa de detalle de Palermo y Las Canitas'>" % rel["palermo"]),
        ("Puerto Madero", "<img src='%s' alt='Mapa de detalle de Puerto Madero'>" % rel["puerto"]),
        ("San Telmo", "<img src='%s' alt='Mapa de detalle de San Telmo'>" % rel["san_telmo"]),
        ("Corrientes / Abasto", "<img src='%s' alt='Mapa de detalle de Corrientes y Abasto'>" % rel["corrientes"]),
        ("Belgrano", "<img src='%s' alt='Mapa de detalle de Belgrano'>" % rel["belgrano"]),
    ]
    body = "\n".join(
        f"<section><h2>{html.escape(title)}</h2><p>{content}</p></section>" if not content.startswith("<img")
        else f"<section><h2>{html.escape(title)}</h2>{content}</section>"
        for title, content in sections
    )
    HTML.write_text(f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <title>{html.escape(TITLE)}</title>
  <style>
    body {{ margin: 0; font-family: Arial, sans-serif; color: #222; background: #f4f6f8; }}
    header {{ background: {AZUL}; color: white; padding: 48px 64px 42px; border-bottom: 6px solid {ROJO}; }}
    header .brand {{ font-weight: 700; letter-spacing: .02em; color: #cdd9e5; }}
    header h1 {{ margin: 42px 0 12px; font-size: 40px; max-width: 880px; line-height: 1.08; }}
    header p {{ margin: 0; font-size: 18px; color: #e9eef5; max-width: 920px; }}
    main {{ max-width: 1040px; margin: 32px auto 64px; padding: 0 24px; }}
    section {{ background: white; border: 1px solid #d9dee5; margin: 18px 0; padding: 28px; }}
    h2 {{ color: {AZUL}; margin: 0 0 14px; font-size: 24px; }}
    p {{ line-height: 1.55; }}
    img {{ width: 100%; height: auto; display: block; border: 1px solid #d9dee5; }}
    .note {{ background: {SOFT_AZUL}; border-left: 6px solid {AZUL2}; padding: 16px; }}
  </style>
</head>
<body>
  <header>
    <div class="brand">{html.escape(INSTITUCION)} · {html.escape(GOBIERNO)}</div>
    <h1>{html.escape(TITLE)}</h1>
    <p>{html.escape(SUBTITLE)}</p>
  </header>
  <main>
    <section class="note">Base de trabajo para revisión territorial; no constituye padrón oficial.</section>
    {body}
  </main>
</body>
</html>
""", encoding="utf-8")


def build_pdf(maps: dict[str, Path]) -> None:
    c = canvas.Canvas(str(PDF), pagesize=A4)
    c.setTitle(TITLE)
    c.setAuthor(INSTITUCION)
    cover(c)
    index_page(c)
    summary_page(c)
    scope_page(c)
    global_map_page(c, maps)
    territorial_page(c)
    detail_map_page(
        c, 7, "palermo", "Palermo / Las Cañitas",
        "Zona con mayor volumen de menciones y distribución interna visible.",
        "Permite observar una concentración relevante dentro del universo semilla y orientar ajustes de subzonas.",
        "Usar como lectura territorial inicial. Los puntos acompañan la revisión y no constituyen padrón oficial.",
        maps,
    )
    detail_map_page(
        c, 8, "puerto", "Puerto Madero",
        "Universo acotado, con necesidad de revisar sedes o zonas puntuales.",
        "El mapa ayuda a ordenar el corredor costero y detectar ajustes antes de una versión operativa.",
        "Conviene validar sedes y recorte fino antes de comunicar detalle operativo.",
        maps,
    )
    detail_map_page(
        c, 9, "san_telmo", "San Telmo",
        "Área con presencia de referencias colectivas y sedes a revisar.",
        "El Mercado de San Telmo debe tratarse como hito territorial o referencia colectiva, no como restaurante puntual.",
        "El detalle sirve para orientar validación de sedes y tratamiento de hitos colectivos.",
        maps,
    )
    detail_map_page(
        c, 10, "corrientes", "Corrientes / Abasto",
        "Ejes vinculados, con delimitación distinta y riesgo de doble conteo.",
        "Corrientes se lee como eje 9 de Julio-Callao; Abasto, como área alrededor del shopping en un radio aproximado de cinco cuadras.",
        "Usar con cautela: Abasto requiere refuerzo antes de publicar detalle operativo.",
        maps,
        caution_color=NARANJA,
    )
    detail_map_page(
        c, 11, "belgrano", "Belgrano y subzonas",
        "Macroárea con respaldo diferenciado entre Barrio Chino, Bajo Belgrano y Belgrano R.",
        "El mapa muestra una lectura posible, pero no conviene sobredimensionar el detalle sin validación adicional.",
        "Presentar como zona a revisar y fortalecer, especialmente para subzonas con menor respaldo.",
        maps,
        caution_color=NARANJA,
    )
    auxiliary_page(c)
    pending_page(c)
    recommendations_page(c)
    next_steps_page(c)
    annex_universe(c)
    annex_method(c)
    annex_limits(c)
    c.save()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    register_fonts()
    maps = sanitize_maps()
    build_pdf(maps)
    build_html(maps)
    print(PDF)
    print(HTML)


if __name__ == "__main__":
    main()
