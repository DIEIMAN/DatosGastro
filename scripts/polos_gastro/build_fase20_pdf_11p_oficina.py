"""Build the PolosGastro 11-page office PDF for phase 20.

Scope: read only phase20 assets and write the requested phase20 PDF.
No APIs, scraping, source data, staging, commits, or prior phase edits.
"""
from __future__ import annotations

from pathlib import Path
import textwrap

from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs" / "polos_gastro" / "fase20_limpieza_mostrable_oficina"
ASSETS = OUT / "assets"
PDF_OUT = OUT / "INFORME_POLOS_GASTRO_DGDGAS_11P_OFICINA.pdf"

W, H = A4
M = 44
TOTAL_PAGES = 11

TITLE = "Polos gastronómicos de la Ciudad de Buenos Aires"
SUBTITLE = "Informe"
INSTITUCION = "DGDGAS — Dirección General de Desarrollo Gastronómico"
GOBIERNO = "Gobierno de la Ciudad de Buenos Aires"
DATE_LABEL = "Julio 2026"

AZUL = "#1F3B57"
ROJO = "#A23A2C"
VERDE = "#2F6E5B"
CELESTE = "#2C7FB8"
GRIS = "#566573"
NEGRO = "#1E252B"
LINEA = "#DDE3E9"
SOFT_AZUL = "#EAF1F8"
SOFT_VERDE = "#EAF5EE"
SOFT_COBRE = "#F8EDE0"
SOFT_GRIS = "#F4F6F8"
WHITE = "#FFFFFF"

FONT = "Arial"
FONT_BOLD = "Arial-Bold"


def register_fonts() -> None:
    regular = Path("C:/Windows/Fonts/arial.ttf")
    bold = Path("C:/Windows/Fonts/arialbd.ttf")
    if regular.exists() and bold.exists():
        pdfmetrics.registerFont(TTFont(FONT, str(regular)))
        pdfmetrics.registerFont(TTFont(FONT_BOLD, str(bold)))
    else:
        globals()["FONT"] = "Helvetica"
        globals()["FONT_BOLD"] = "Helvetica-Bold"


def hex_to_rgb(color: str) -> tuple[float, float, float]:
    color = color.lstrip("#")
    return tuple(int(color[i : i + 2], 16) / 255 for i in (0, 2, 4))


def set_fill(c: canvas.Canvas, color: str) -> None:
    c.setFillColorRGB(*hex_to_rgb(color))


def set_stroke(c: canvas.Canvas, color: str) -> None:
    c.setStrokeColorRGB(*hex_to_rgb(color))


def wrap_text(text: str, font_name: str, size: float, max_width: float) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        trial = " ".join([*current, word])
        if pdfmetrics.stringWidth(trial, font_name, size) <= max_width or not current:
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
    width: float,
    *,
    font_name: str = FONT,
    size: float = 10,
    color: str = NEGRO,
    leading: float | None = None,
) -> float:
    if leading is None:
        leading = size * 1.35
    c.setFont(font_name, size)
    set_fill(c, color)
    for line in wrap_text(text, font_name, size, width):
        c.drawString(x, y, line)
        y -= leading
    return y


def page_header(c: canvas.Canvas, page: int, title: str, subtitle: str | None = None) -> float:
    set_fill(c, AZUL)
    c.rect(0, H - 18, W, 18, fill=1, stroke=0)
    set_fill(c, ROJO)
    c.rect(0, H - 18, 70, 18, fill=1, stroke=0)
    y = H - 58
    c.setFont(FONT_BOLD, 16)
    set_fill(c, AZUL)
    c.drawString(M, y, title)
    c.setFont(FONT_BOLD, 9)
    set_fill(c, GRIS)
    c.drawRightString(W - M, y + 3, f"{page} / {TOTAL_PAGES}")
    y -= 23
    if subtitle:
        y = draw_wrapped(c, subtitle, M, y, W - 2 * M, font_name=FONT_BOLD, size=10.5, color=GRIS, leading=13)
    set_stroke(c, LINEA)
    c.line(M, y - 8, W - M, y - 8)
    return y - 28


def page_footer(c: canvas.Canvas) -> None:
    set_stroke(c, LINEA)
    c.line(M, 46, W - M, 46)
    c.setFont(FONT, 7.8)
    set_fill(c, GRIS)
    c.drawString(M, 29, INSTITUCION)
    c.drawRightString(W - M, 29, GOBIERNO)


def finish_page(c: canvas.Canvas) -> None:
    page_footer(c)
    c.showPage()


def note_box(
    c: canvas.Canvas,
    x: float,
    y: float,
    w: float,
    h: float,
    title: str,
    body: str,
    *,
    border: str = CELESTE,
    fill: str = SOFT_AZUL,
    size: float = 8.8,
) -> None:
    set_fill(c, fill)
    set_stroke(c, border)
    c.roundRect(x, y, w, h, 5, fill=1, stroke=1)
    c.setFont(FONT_BOLD, size + 1.2)
    set_fill(c, AZUL)
    c.drawString(x + 12, y + h - 20, title)
    yy = y + h - 38
    for paragraph in body.split("\n"):
        yy = draw_wrapped(c, paragraph, x + 12, yy, w - 24, font_name=FONT, size=size, color=NEGRO, leading=size * 1.35)
        yy -= 4


def bullet_list(c: canvas.Canvas, items: list[str], x: float, y: float, width: float, *, size: float = 9.2) -> float:
    for item in items:
        c.setFont(FONT_BOLD, size + 1)
        set_fill(c, ROJO)
        c.drawString(x, y, "•")
        y = draw_wrapped(c, item, x + 16, y, width - 16, font_name=FONT, size=size, color=NEGRO, leading=size * 1.35)
        y -= 8
    return y


def draw_image_fit(c: canvas.Canvas, path: Path, x: float, y: float, w: float, h: float, *, border: bool = False) -> None:
    img = ImageReader(str(path))
    iw, ih = img.getSize()
    scale = min(w / iw, h / ih)
    dw, dh = iw * scale, ih * scale
    dx, dy = x + (w - dw) / 2, y + (h - dh) / 2
    if border:
        set_stroke(c, LINEA)
        c.rect(dx, dy, dw, dh, fill=0, stroke=1)
    c.drawImage(img, dx, dy, dw, dh, preserveAspectRatio=True, mask="auto")


def cover(c: canvas.Canvas) -> None:
    set_fill(c, AZUL)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    set_fill(c, ROJO)
    c.rect(0, 0, 18, H, fill=1, stroke=0)
    set_fill(c, WHITE)
    y = H - 190
    c.setFont(FONT_BOLD, 29)
    for line in wrap_text(TITLE, FONT_BOLD, 29, W - 2 * M - 20):
        c.drawString(M + 10, y, line)
        y -= 35
    c.setFont(FONT_BOLD, 18)
    c.drawString(M + 10, y - 14, SUBTITLE)
    c.setFont(FONT, 12.2)
    c.drawString(M + 10, y - 68, INSTITUCION)
    c.drawString(M + 10, y - 88, GOBIERNO)
    c.drawString(M + 10, y - 126, DATE_LABEL)
    c.setFont(FONT_BOLD, 9.5)
    c.drawRightString(W - M, 32, f"1 / {TOTAL_PAGES}")
    c.showPage()


def index_page(c: canvas.Canvas) -> None:
    page_header(c, 2, "Índice")
    entries = [
        "Portada",
        "Índice",
        "Resumen ejecutivo",
        "Alcance y criterio de lectura",
        "Mapa global de 22 polos/ejes",
        "Lectura territorial general",
        "Detalle: Palermo / Las Cañitas",
        "Detalle: Puerto Madero",
        "Detalle: San Telmo",
        "Detalle: Corrientes / Abasto",
        "Detalle: Belgrano",
    ]
    y = H - 132
    for idx, entry in enumerate(entries, start=1):
        c.setFont(FONT, 11.2)
        set_fill(c, NEGRO)
        c.drawString(M + 10, y, entry)
        set_stroke(c, LINEA)
        c.line(M + 210, y + 3, W - M - 36, y + 3)
        c.setFont(FONT_BOLD, 11.2)
        c.drawRightString(W - M - 10, y, str(idx))
        y -= 42
    finish_page(c)


def summary_page(c: canvas.Canvas) -> None:
    y = page_header(
        c,
        3,
        "Resumen ejecutivo",
        "Una lectura territorial inicial para ordenar el universo semilla de polos gastronómicos de la Ciudad.",
    )
    paragraphs = [
        "Este informe organiza un universo semilla de 22 polos y ejes gastronómicos de la Ciudad de Buenos Aires, con el objetivo de aportar una lectura territorial inicial para conversación institucional y ordenamiento de criterios.",
        "La pieza combina un mapa global de referencia, mapas de detalle por zonas seleccionadas y menciones destacadas del universo semilla. Las áreas representadas son aproximaciones de lectura territorial: no constituyen límites oficiales, padrón de locales ni ranking gastronómico.",
        "El valor principal del informe es ofrecer una primera lectura ordenada sobre zonas, ejes y subzonas gastronómicas, diferenciando áreas con mayor reconocimiento territorial de aquellas que requieren mayor trabajo documental o territorial en futuras instancias.",
    ]
    yy = y - 4
    for paragraph in paragraphs:
        yy = draw_wrapped(c, paragraph, M + 8, yy, W - 2 * M - 16, font_name=FONT, size=11.4, color=NEGRO, leading=16)
        yy -= 18
    note_box(
        c,
        M,
        142,
        W - 2 * M,
        104,
        "Lectura institucional",
        "La pieza está pensada como apoyo para conversación y ordenamiento territorial. La lectura de detalle se concentra en cinco zonas seleccionadas y mantiene el mapa global como referencia de conjunto.",
        border=VERDE,
        fill=SOFT_VERDE,
        size=9.2,
    )
    finish_page(c)


def scope_page(c: canvas.Canvas) -> None:
    y = page_header(c, 4, "Alcance y criterio de lectura", "Qué afirma y qué no afirma la pieza")
    note_box(
        c,
        M,
        y - 112,
        W - 2 * M,
        104,
        "Aclaración metodológica",
        "Este informe se construye a partir de un universo semilla de polos, ejes y menciones gastronómicas relevadas mediante fuentes abiertas, referencias territoriales y capas auxiliares de geolocalización. Las áreas representadas tienen carácter orientativo y sirven para ordenar una primera lectura territorial; no constituyen delimitaciones oficiales ni padrón exhaustivo de establecimientos.",
        border=AZUL,
        fill=SOFT_AZUL,
        size=8.3,
    )
    note_box(
        c,
        M,
        y - 222,
        W - 2 * M,
        82,
        "Universo semilla",
        "Las menciones destacadas no son ranking, no son recomendación comercial y no equivalen a padrón de locales activos.",
        border=VERDE,
        fill=SOFT_VERDE,
        size=9.2,
    )
    note_box(
        c,
        M,
        y - 326,
        W - 2 * M,
        86,
        "Subzonas",
        "Las subzonas son aproximaciones editoriales construidas para facilitar la lectura territorial. No son límites oficiales, polígonos normativos ni delimitaciones cerradas.",
        border=ROJO,
        fill=SOFT_COBRE,
        size=9.2,
    )
    finish_page(c)


def global_map_page(c: canvas.Canvas) -> None:
    page_header(
        c,
        5,
        "Mapa global de 22 polos/ejes",
        "Áreas, ejes y zonas de lectura territorial del universo semilla.",
    )
    draw_image_fit(c, ASSETS / "global_mapa_pdf_mostrable_ale.png", M - 4, 138, W - 2 * M + 8, 548, border=False)
    note_box(
        c,
        M,
        72,
        W - 2 * M,
        54,
        "Lectura",
        "El mapa global ordena una mirada general de la Ciudad y ubica los principales sectores de referencia en una misma pieza.",
        border=CELESTE,
        fill=SOFT_AZUL,
        size=8.3,
    )
    finish_page(c)


def territorial_page(c: canvas.Canvas) -> None:
    y = page_header(c, 6, "Lectura territorial general", "Cómo leer las zonas de detalle")
    note_box(
        c,
        M,
        y - 88,
        W - 2 * M,
        76,
        "Palermo y Puerto Madero",
        "Palermo concentra el mayor volumen de menciones y requiere distinguir subzonas internas. Puerto Madero se lee mejor como banda de docks y eje costero.",
        border=CELESTE,
        fill=SOFT_AZUL,
        size=9,
    )
    note_box(
        c,
        M,
        y - 190,
        W - 2 * M,
        82,
        "San Telmo y Corrientes / Abasto",
        "San Telmo se entiende a partir del Mercado y el casco histórico. Corrientes y Abasto se presentan como áreas vinculadas pero diferenciadas dentro de la lectura territorial.",
        border=VERDE,
        fill=SOFT_VERDE,
        size=9,
    )
    note_box(
        c,
        M,
        y - 292,
        W - 2 * M,
        74,
        "Belgrano",
        "Belgrano se presenta como macroárea con subzonas de referencia. Barrio Chino, Bajo Belgrano y Belgrano R se leen como sectores diferenciados.",
        border=ROJO,
        fill=SOFT_COBRE,
        size=9,
    )
    bullet_list(
        c,
        [
            "El mapa global sostiene la lectura de conjunto.",
            "Los mapas de detalle amplían cinco zonas seleccionadas.",
            "Las menciones laterales funcionan como referencias del universo semilla, sin ordenar preferencias.",
        ],
        M + 6,
        254,
        W - 2 * M - 12,
        size=9.5,
    )
    finish_page(c)


DETAILS = {
    7: {
        "title": "Detalle: Palermo / Las Cañitas",
        "subtitle": "Subzonas aproximadas de lectura territorial.",
        "image": "mapa_mostrable_palermo_las_canitas.png",
        "mentions": "Palermo / Las Cañitas: Don Julio; La Cabrera; Niño Gordo; Gran Dabbang; Mishiguene; La Mar; Cosi Mi Piace.\nLas Cañitas: Campo Bravo; Kansas; SushiClub.\nReferencias complementarias: Café Registrado.",
        "reading": "Se distinguen Palermo Soho, Palermo Hollywood y Las Cañitas como subzonas aproximadas. La lectura permite ordenar un sector amplio con alta presencia gastronómica y diferentes identidades internas.",
    },
    8: {
        "title": "Detalle: Puerto Madero",
        "subtitle": "Banda de docks, frente costero e hitos de lectura.",
        "image": "mapa_mostrable_puerto_madero.png",
        "mentions": "Zona costera / docks: Happening; Sottovoce; El Mercado / Faena; Le Grill.\nReferencias complementarias: Cabaña Las Lilas; La Parolaccia Casa Tua; Red Resto & Lounge; Patagonia Sur.",
        "reading": "Puerto Madero se representa como banda de docks y frente costero. Faena / El Mercado funciona como hito de lectura territorial.",
    },
    9: {
        "title": "Detalle: San Telmo",
        "subtitle": "Casco histórico, eje Defensa y Mercado de San Telmo.",
        "image": "mapa_mostrable_san_telmo.png",
        "mentions": "San Telmo: La Brigada; Café San Juan; Hierbabuena.\nReferencias complementarias: Mercado de San Telmo; El Preferido de San Telmo; Pulpería Quilapán; Napoles.",
        "reading": "El Mercado de San Telmo se muestra como hito colectivo. Defensa y el casco histórico ordenan la lectura territorial del entorno.",
    },
    10: {
        "title": "Detalle: Corrientes / Abasto",
        "subtitle": "Áreas vinculadas pero diferenciadas.",
        "image": "mapa_mostrable_corrientes_abasto.png",
        "mentions": "Corrientes: Las Cuartetas; El Palacio de la Pizza; Pertutti.\nReferencias complementarias: Güerrín; Moulin Bleu; Abasto.\nAbasto: área de lectura asociada al entorno del shopping.",
        "reading": "Corrientes se presenta como eje teatral-gastronómico aproximado entre 9 de Julio y Callao. Corrientes y Abasto se presentan como áreas vinculadas pero diferenciadas dentro de la lectura territorial.",
    },
    11: {
        "title": "Detalle: Belgrano",
        "subtitle": "Macroárea con subzonas de referencia.",
        "image": "mapa_mostrable_belgrano.png",
        "mentions": "Barrio Chino: Hong Kong Style; China Rose.\nReferencias complementarias: Ichisou; Ramen Neko; Ichiban; BAO Kitchen; Tori Tori; La Mar; Belgrano R.\nBelgrano R: subzona de referencia dentro de la macroárea.",
        "reading": "Barrio Chino, Bajo Belgrano y Belgrano R se presentan como subzonas diferenciadas dentro de la macroárea.",
    },
}


def detail_page(c: canvas.Canvas, page: int) -> None:
    cfg = DETAILS[page]
    page_header(c, page, cfg["title"], cfg["subtitle"])
    draw_image_fit(c, ASSETS / cfg["image"], M - 4, 308, W - 2 * M + 8, 394, border=False)
    box_w = (W - 2 * M - 14) / 2
    note_box(
        c,
        M,
        118,
        box_w,
        162,
        "Menciones destacadas",
        cfg["mentions"],
        border=CELESTE,
        fill=SOFT_AZUL,
        size=7.4,
    )
    note_box(
        c,
        M + box_w + 14,
        118,
        box_w,
        162,
        "Lectura territorial",
        cfg["reading"],
        border=VERDE,
        fill=SOFT_VERDE,
        size=7.8,
    )
    finish_page(c)


def build_pdf() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(PDF_OUT), pagesize=A4)
    c.setTitle(TITLE)
    c.setAuthor(INSTITUCION)
    c.setSubject("Informe DGDGAS")
    cover(c)
    index_page(c)
    summary_page(c)
    scope_page(c)
    global_map_page(c)
    territorial_page(c)
    for page in range(7, 12):
        detail_page(c, page)
    c.save()


def main() -> None:
    register_fonts()
    build_pdf()
    print(PDF_OUT)


if __name__ == "__main__":
    main()
