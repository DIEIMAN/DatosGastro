# -*- coding: utf-8 -*-
"""FASE25_POLITICA_EXPERIMENTAL_V1 — generador paralelo (NO oficial).

Pieza experimental de 10 páginas para funcionarios y decisores, construida en
paralelo a la Fase 25 oficial (que permanece intacta). Reglas:

- NO importa ni ejecuta los generadores oficiales (fase13/fase22/fase24/fase25);
  replica su identidad visual (paleta, tipografía, layout) como constantes propias.
- Los mapas son COPIAS de los assets de Fase 25 usadas como placeholders internos,
  sujetas a reemplazo por las capas de presentación v2.1 de Codex
  (ver MATRIZ_ASSETS_PENDIENTES_CODEX.csv). El origen se lee, nunca se modifica.
- Textos desde contenido_fase25_politica_experimental_v1.yaml (banco TXT-nn).
- Sin APIs, sin Google Places, sin scraping, sin datos nuevos, sin clustering.
- La marca "experimental" va en los metadatos del PDF y en la documentación,
  no como sello visual en las páginas (decisión editorial de la tanda 2026-07-11).

Uso:  .venv/Scripts/python.exe scripts/polos_gastro/historico/experimentos/\
fase25_politica_e_integracion_editorial_v1/generar_fase25_politica_experimental_v1.py
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[4]
EXP = "fase25_politica_e_integracion_editorial_v1"
DOCS = ROOT / "docs" / "polos_gastro" / "historico" / "experimentos" / EXP
OUT = ROOT / "outputs" / "polos_gastro" / "historico" / "experimentos" / EXP
ASSETS = OUT / "assets"
CONTENT = DOCS / "contenido_fase25_politica_experimental_v1.yaml"
PDF_OUT = OUT / "INFORME_POLOS_GASTRO_FASE25_POLITICA_EXPERIMENTAL_V1.pdf"

# Origen de los placeholders (solo lectura; assets oficiales de Fase 25).
# Las copias locales se reencuadran (se quita la franja de título interno de los
# mapas de detalle —el nombre de la zona ya está en el encabezado de la página—
# y los márgenes blancos del lienzo). Los archivos oficiales NO se modifican.
F25_ASSETS = ROOT / "outputs" / "polos_gastro" / "fase25_microajustes_finales_oficina" / "assets"
PLACEHOLDERS = {
    # nombre: recorte de franja de título interno (fracción de la altura, desde arriba)
    "global_mapa_fase25.png": 0.0,
    "mapa_fase25_palermo_las_canitas.png": 0.095,
    # Corrientes es una franja ancha: los ejes quedan centrados verticalmente en la
    # figura y el título interno ("Corrientes / Abasto", no autorizado por DEC-20)
    # cae ~22% por debajo del borde superior.
    "mapa_fase25_corrientes_abasto.png": 0.23,
    "mapa_fase25_san_telmo.png": 0.095,
    "mapa_fase25_puerto_madero.png": 0.095,
    "mapa_fase25_belgrano.png": 0.095,
}

# --- Identidad DGDGAS (misma paleta/tipografía que fase20→fase25) ---------------
W, H = A4
M = 44
TOTAL_PAGES = 10

AZUL = "#1F3B57"
ROJO = "#A23A2C"
VERDE = "#2F6E5B"
CELESTE = "#2C7FB8"
SLATE = "#5E6B78"
GRIS = "#566573"
NEGRO = "#1E252B"
LINEA = "#DDE3E9"
SOFT_AZUL = "#EAF1F8"
SOFT_VERDE = "#EAF5EE"
SOFT_COBRE = "#F8EDE0"
GRIS_CLARO = "#8A97A3"
WHITE = "#FFFFFF"

FONT = "Arial"
FONT_BOLD = "Arial-Bold"

# Distintivo de madurez (SISTEMA_TIPO_Y_MADUREZ_TERRITORIAL.md §4.2).
MADUREZ_COLOR = {
    "lectura consolidada": AZUL,
    "lectura consolidada, con seguimiento": VERDE,
    "lectura en consolidación": SLATE,
    "lectura exploratoria": GRIS_CLARO,
}


# --- Carga de contenido (YAML con fallback de subconjunto) ----------------------

def _strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        return value[1:-1]
    return value


def load_content(path: Path) -> dict:
    """Carga el YAML de contenido. Usa PyYAML si está; si no, parsea el
    subconjunto restringido documentado en el propio archivo (2 niveles + listas
    de cadenas, escalares en una sola línea)."""
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        return yaml.safe_load(text)
    except ImportError:
        pass

    data: dict = {}
    section: dict | None = None
    current_list: list | None = None
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip())
        line = raw.strip()
        if indent == 0 and line.endswith(":"):
            section = {}
            data[line[:-1]] = section
            current_list = None
        elif indent == 2 and section is not None:
            if line.endswith(":"):
                current_list = []
                section[line[:-1]] = current_list
            else:
                key, _, value = line.partition(":")
                section[key.strip()] = _strip_quotes(value)
                current_list = None
        elif indent >= 4 and current_list is not None and line.startswith("- "):
            current_list.append(_strip_quotes(line[2:]))
        else:
            raise ValueError(f"Línea fuera del subconjunto YAML soportado: {raw!r}")
    return data


# --- Helpers de dibujo (identidad heredada) --------------------------------------

def register_fonts() -> None:
    global FONT, FONT_BOLD
    regular = Path("C:/Windows/Fonts/arial.ttf")
    bold = Path("C:/Windows/Fonts/arialbd.ttf")
    if regular.exists() and bold.exists():
        pdfmetrics.registerFont(TTFont(FONT, str(regular)))
        pdfmetrics.registerFont(TTFont(FONT_BOLD, str(bold)))
    else:
        FONT, FONT_BOLD = "Helvetica", "Helvetica-Bold"


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


def draw_wrapped(c, text, x, y, width, *, font_name=None, size=10.0, color=NEGRO, leading=None) -> float:
    font_name = font_name or FONT
    leading = leading if leading is not None else size * 1.35
    c.setFont(font_name, size)
    set_fill(c, color)
    for line in wrap_text(text, font_name, size, width):
        c.drawString(x, y, line)
        y -= leading
    return y


def wrapped_height(text: str, font_name: str, size: float, width: float, leading: float | None = None) -> float:
    leading = leading if leading is not None else size * 1.35
    return len(wrap_text(text, font_name, size, width)) * leading


def page_header(c, page: int, title: str, subtitle: str | None = None, estado: str | None = None) -> float:
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
    if estado:
        # Distintivo discreto de madurez: punto + rótulo, alineado a la derecha.
        color = MADUREZ_COLOR.get(estado, GRIS_CLARO)
        label_w = pdfmetrics.stringWidth(estado, FONT, 8.2)
        cx = W - M - label_w - 12
        set_fill(c, color)
        c.circle(cx, y - 15, 2.6, fill=1, stroke=0)
        c.setFont(FONT, 8.2)
        set_fill(c, GRIS)
        c.drawString(cx + 8, y - 18, estado)
    y -= 23
    if subtitle:
        y = draw_wrapped(c, subtitle, M, y, W - 2 * M - 150, font_name=FONT_BOLD, size=10.5, color=GRIS, leading=13)
    set_stroke(c, LINEA)
    c.line(M, y - 8, W - M, y - 8)
    return y - 28


def page_footer(c, institucion: str, gobierno: str) -> None:
    set_stroke(c, LINEA)
    c.line(M, 46, W - M, 46)
    c.setFont(FONT, 7.8)
    set_fill(c, GRIS)
    c.drawString(M, 29, institucion)
    c.drawRightString(W - M, 29, gobierno)


def note_box(c, x, y, w, h, title, body, *, border=CELESTE, fill=SOFT_AZUL, size=8.8) -> None:
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


def draw_image_fit(c, path: Path, x, y, w, h) -> tuple[float, float, float, float]:
    img = ImageReader(str(path))
    iw, ih = img.getSize()
    scale = min(w / iw, h / ih)
    dw, dh = iw * scale, ih * scale
    dx, dy = x + (w - dw) / 2, y + (h - dh) / 2
    c.drawImage(img, dx, dy, dw, dh, preserveAspectRatio=True, mask="auto")
    return dx, dy, dw, dh


# --- Páginas ----------------------------------------------------------------------

def cover(c, meta: dict) -> None:
    set_fill(c, AZUL)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    set_fill(c, ROJO)
    c.rect(0, 0, 18, H, fill=1, stroke=0)
    set_fill(c, WHITE)
    y = H - 190
    c.setFont(FONT_BOLD, 29)
    for line in wrap_text(meta["titulo"], FONT_BOLD, 29, W - 2 * M - 20):
        c.drawString(M + 10, y, line)
        y -= 35
    c.setFont(FONT_BOLD, 17)
    for line in wrap_text(meta["subtitulo"], FONT_BOLD, 17, W - 2 * M - 20):
        c.drawString(M + 10, y - 14, line)
        y -= 24
    c.setFont(FONT, 12.2)
    c.drawString(M + 10, y - 68, meta["institucion"])
    c.drawString(M + 10, y - 88, meta["gobierno"])
    c.drawString(M + 10, y - 126, meta["fecha"])
    c.setFont(FONT, 8.6)
    set_fill(c, "#B9C6D4")
    c.drawString(M + 10, y - 148, meta["version_interna"])
    set_fill(c, WHITE)
    c.setFont(FONT_BOLD, 9.5)
    c.drawRightString(W - M, 32, f"1 / {TOTAL_PAGES}")
    c.showPage()


def sintesis_page(c, data: dict, meta: dict) -> None:
    sec = data["sintesis"]
    y = page_header(c, 2, sec["titulo"], sec["bajada"])
    yy = y - 2
    for paragraph in sec["parrafos"]:
        yy = draw_wrapped(c, paragraph, M + 8, yy, W - 2 * M - 16, size=11.3, leading=16)
        yy -= 15
    yy -= 4
    yy = draw_wrapped(c, sec["encuadre"], M + 8, yy, W - 2 * M - 16, font_name=FONT_BOLD, size=10.6, color=AZUL, leading=15)
    note_box(c, M, 128, W - 2 * M, 128, sec["como_leer_titulo"], sec["como_leer"], border=CELESTE, fill=SOFT_AZUL, size=8.8)
    c.setFont(FONT, 8.4)
    set_fill(c, GRIS)
    for i, line in enumerate(wrap_text(sec["alcance_pie"], FONT, 8.4, W - 2 * M - 16)):
        c.drawString(M + 8, 72 - i * 11, line)
    page_footer(c, meta["institucion"], meta["gobierno"])
    c.showPage()


def mapa_general_page(c, data: dict, meta: dict) -> None:
    sec = data["mapa_general"]
    y = page_header(c, 3, sec["titulo"], sec["bajada"])
    # Mapa dominante: ocupa casi toda la página (ajuste alta prioridad de la auditoría).
    draw_image_fit(c, ASSETS / sec["asset"], M - 6, 200, W - 2 * M + 12, y - 208)
    box_h = 92
    note_box(c, M, 96, W - 2 * M, box_h, sec["lectura_titulo"], sec["lectura"], border=VERDE, fill=SOFT_VERDE, size=9.0)
    c.setFont(FONT, 7.9)
    set_fill(c, GRIS)
    for i, line in enumerate(wrap_text(sec["nota_pie"], FONT, 7.9, W - 2 * M - 16)):
        c.drawString(M + 8, 78 - i * 10, line)
    page_footer(c, meta["institucion"], meta["gobierno"])
    c.showPage()


def detalle_page(c, page: int, sec: dict, meta: dict, extra_key: str | None = None, extra_title_key: str | None = None) -> None:
    y = page_header(c, page, sec["titulo"], sec["bajada"], estado=sec.get("estado_lectura"))
    if extra_key:
        box_h, box_top = 158, 118 + 158
        draw_image_fit(c, ASSETS / sec["asset"], M - 4, box_top + 14, W - 2 * M + 8, y - box_top - 22)
        box_w = (W - 2 * M - 14) / 2
        note_box(c, M, 118, box_w, box_h, sec["lectura_titulo"], sec["lectura"], border=VERDE, fill=SOFT_VERDE, size=8.2)
        note_box(c, M + box_w + 14, 118, box_w, box_h, sec[extra_title_key], sec[extra_key], border=CELESTE, fill=SOFT_AZUL, size=8.2)
    else:
        box_h, box_top = 122, 128 + 122
        draw_image_fit(c, ASSETS / sec["asset"], M - 4, box_top + 14, W - 2 * M + 8, y - box_top - 22)
        note_box(c, M, 128, W - 2 * M, box_h, sec["lectura_titulo"], sec["lectura"], border=VERDE, fill=SOFT_VERDE, size=9.0)
    page_footer(c, meta["institucion"], meta["gobierno"])
    c.showPage()


def san_telmo_puerto_page(c, data: dict, meta: dict) -> None:
    sec = data["san_telmo_puerto_madero"]
    y = page_header(c, 6, sec["titulo"], sec["bajada"], estado=sec.get("estado_lectura"))
    col_w = (W - 2 * M - 18) / 2
    box_h, box_top = 172, 112 + 172
    map_h = y - box_top - 22
    draw_image_fit(c, ASSETS / sec["asset_san_telmo"], M, box_top + 14, col_w, map_h)
    draw_image_fit(c, ASSETS / sec["asset_puerto"], M + col_w + 18, box_top + 14, col_w, map_h)
    note_box(c, M, 112, col_w, box_h, sec["san_telmo_titulo"], sec["san_telmo"], border=VERDE, fill=SOFT_VERDE, size=8.2)
    note_box(c, M + col_w + 18, 112, col_w, box_h, sec["puerto_titulo"], sec["puerto"], border=CELESTE, fill=SOFT_AZUL, size=8.2)
    page_footer(c, meta["institucion"], meta["gobierno"])
    c.showPage()


def costanera_page(c, data: dict, meta: dict) -> None:
    sec = data["costanera"]
    y = page_header(c, 8, sec["titulo"], sec["bajada"], estado=sec.get("estado_lectura"))
    yy = draw_wrapped(c, sec["lectura"], M + 8, y - 2, W - 2 * M - 16, size=11.3, leading=16)
    box_w = (W - 2 * M - 14) / 2
    top = yy - 26
    note_box(c, M, top - 150, box_w, 150, sec["exploratoria_titulo"], sec["exploratoria"], border=CELESTE, fill=SOFT_AZUL, size=8.4)
    note_box(c, M + box_w + 14, top - 150, box_w, 150, sec["territorio_titulo"], sec["territorio"], border=VERDE, fill=SOFT_VERDE, size=8.4)
    note_box(c, M, top - 150 - 112, W - 2 * M, 96, sec["seguimiento_titulo"], sec["seguimiento"], border=ROJO, fill=SOFT_COBRE, size=8.8)
    page_footer(c, meta["institucion"], meta["gobierno"])
    c.showPage()


def proximos_pasos_page(c, data: dict, meta: dict) -> None:
    sec = data["proximos_pasos"]
    y = page_header(c, 9, sec["titulo"], sec["bajada"])
    yy = y - 6
    for item in sec["items"]:
        c.setFont(FONT_BOLD, 11)
        set_fill(c, ROJO)
        c.drawString(M + 8, yy, "•")
        yy = draw_wrapped(c, item, M + 26, yy, W - 2 * M - 34, size=10.8, leading=15.5)
        yy -= 14
    yy -= 4
    yy = draw_wrapped(c, sec["cierre"], M + 8, yy, W - 2 * M - 16, font_name=FONT_BOLD, size=10.4, color=AZUL, leading=15)
    note_box(c, M, 118, W - 2 * M, 118, sec["relacion_titulo"], sec["relacion"], border=VERDE, fill=SOFT_VERDE, size=8.8)
    page_footer(c, meta["institucion"], meta["gobierno"])
    c.showPage()


def nota_metodologica_page(c, data: dict, meta: dict) -> None:
    sec = data["nota_metodologica"]
    y = page_header(c, 10, sec["titulo"], sec["bajada"])
    yy = y - 4
    for key in ("fuentes", "representacion", "alcance"):
        c.setFont(FONT_BOLD, 11.2)
        set_fill(c, AZUL)
        c.drawString(M + 8, yy, sec[f"{key}_titulo"])
        yy -= 18
        yy = draw_wrapped(c, sec[key], M + 8, yy, W - 2 * M - 16, size=10.2, leading=15)
        yy -= 22
    page_footer(c, meta["institucion"], meta["gobierno"])
    c.showPage()


# --- Main -------------------------------------------------------------------------

def _trim_white(img: Image.Image, threshold: int = 253, pad: int = 12) -> Image.Image:
    """Recorta los márgenes blancos del lienzo (el fondo cartográfico #FAFBFC y
    los barrios quedan por debajo del umbral, así que se conservan)."""
    arr = np.asarray(img.convert("L"))
    mask = arr < threshold
    rows = np.where(mask.any(axis=1))[0]
    cols = np.where(mask.any(axis=0))[0]
    if not len(rows) or not len(cols):
        return img
    top = max(int(rows[0]) - pad, 0)
    bottom = min(int(rows[-1]) + pad, img.height)
    left = max(int(cols[0]) - pad, 0)
    right = min(int(cols[-1]) + pad, img.width)
    return img.crop((left, top, right, bottom))


def _pil_font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf")
    return ImageFont.truetype(str(path), size=size)


def _replace_label(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], text: str, *, size: int = 22) -> None:
    """Reemplaza jerga heredada dentro de una copia experimental del mapa."""
    draw.rounded_rectangle(box, radius=7, fill="#FAFAFA")
    draw.multiline_text(
        ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2),
        text,
        font=_pil_font(size, bold=True),
        fill="#566573",
        anchor="mm",
        align="center",
        spacing=2,
    )


def _replace_legend(img: Image.Image, box: tuple[int, int, int, int], labels: list[str]) -> None:
    """Redibuja la leyenda sin vocabulario aproximativo ni códigos internos."""
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle(box, radius=7, fill="#FFFFFF", outline="#DDE3E9", width=3)
    x0, y0, x1, y1 = box
    row_h = (y1 - y0 - 14) / len(labels)
    colors = ["#B8D7EA", "#B7DEC9", "#E9D3B8", "#C83A2A"] if len(labels) == 4 else ["#B8D7EA", "#5E6B78", "#8A97A3"]
    for idx, (label, color) in enumerate(zip(labels, colors)):
        cy = y0 + 7 + row_h * (idx + 0.5)
        if idx == len(labels) - 1 and len(labels) == 4:
            draw.line((x0 + 15, cy, x0 + 62, cy), fill=color, width=6)
        elif idx == 1 and len(labels) == 3:
            draw.line((x0 + 15, cy, x0 + 62, cy), fill=color, width=5)
        elif idx == 2 and len(labels) == 3:
            draw.line((x0 + 15, cy, x0 + 62, cy), fill=color, width=4)
        else:
            draw.rectangle((x0 + 15, cy - 8, x0 + 62, cy + 8), fill=color, outline="#93A3B0")
        draw.text((x0 + 78, cy), label, font=_pil_font(20), fill="#1E252B", anchor="lm")


def _sanitize_placeholder(name: str, img: Image.Image) -> Image.Image:
    """Limpia solo las copias experimentales; nunca modifica los assets oficiales."""
    draw = ImageDraw.Draw(img)
    if name == "global_mapa_fase25.png":
        _replace_legend(
            img,
            (44, 1430, 470, 1645),
            ["Área / barrio de lectura", "Macrozona con subzonas", "Área de lectura", "Eje / corredor de lectura"],
        )
    elif name == "mapa_fase25_palermo_las_canitas.png":
        for box in ((190, 270, 414, 310), (86, 827, 318, 870), (365, 873, 608, 917)):
            _replace_label(draw, box, "ÁREA DE LECTURA", size=19)
        _replace_legend(img, (18, 944, 395, 1065), ["área de lectura", "eje de contexto", "avenidas de referencia"])
    elif name == "mapa_fase25_corrientes_abasto.png":
        _replace_label(draw, (1170, 494, 1375, 535), "EJE DE LECTURA", size=20)
        _replace_legend(img, (18, 565, 405, 716), ["área de lectura", "eje de contexto", "avenidas de referencia"])
    elif name == "mapa_fase25_san_telmo.png":
        _replace_label(draw, (635, 419, 875, 458), "HITO URBANO", size=19)
        _replace_label(draw, (568, 816, 780, 858), "EJE DE CONTEXTO", size=18)
        _replace_legend(img, (18, 942, 400, 1067), ["área de lectura", "eje de contexto", "avenidas de referencia"])
    elif name == "mapa_fase25_puerto_madero.png":
        _replace_label(draw, (402, 330, 648, 426), "FRENTE DE LOS\nDIQUES", size=23)
        _replace_label(draw, (210, 674, 570, 812), "ENTORNO DE\nLOS DIQUES", size=23)
        _replace_label(draw, (594, 727, 754, 770), "EJE DE LECTURA", size=16)
        _replace_legend(img, (18, 942, 400, 1067), ["área de lectura", "eje de contexto", "avenidas de referencia"])
    elif name == "mapa_fase25_belgrano.png":
        _replace_label(draw, (565, 437, 815, 480), "ÁREA DE LECTURA", size=19)
        _replace_label(draw, (64, 797, 420, 843), "ÁREA DE LECTURA", size=19)
        _replace_legend(img, (18, 942, 400, 1067), ["área de lectura", "eje de contexto", "avenidas de referencia"])
    return img


def copy_placeholders() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    for name, title_frac in PLACEHOLDERS.items():
        src = F25_ASSETS / name
        if not src.exists():
            raise FileNotFoundError(f"Asset de Fase 25 no encontrado (solo lectura): {src}")
        img = Image.open(src).convert("RGB")
        if title_frac:
            img = img.crop((0, int(img.height * title_frac), img.width, img.height))
        img = _trim_white(img)
        img = _sanitize_placeholder(name, img)
        img.save(ASSETS / name, optimize=True)


def main() -> None:
    register_fonts()
    data = load_content(CONTENT)
    meta = data["meta"]
    copy_placeholders()
    OUT.mkdir(parents=True, exist_ok=True)

    c = canvas.Canvas(str(PDF_OUT), pagesize=A4)
    c.setTitle(f"{meta['titulo']} — {meta['subtitulo']}")
    c.setAuthor(meta["institucion"])
    c.setSubject(meta["pdf_subject"])
    c.setKeywords("FASE25_POLITICA_EXPERIMENTAL_V1; version interna de trabajo; placeholders pendientes de handoff Codex v2.1")

    cover(c, meta)
    sintesis_page(c, data, meta)
    mapa_general_page(c, data, meta)
    detalle_page(c, 4, data["palermo"], meta)
    detalle_page(c, 5, data["corrientes"], meta, extra_key="abasto", extra_title_key="abasto_titulo")
    san_telmo_puerto_page(c, data, meta)
    detalle_page(c, 7, data["belgrano"], meta, extra_key="observacion", extra_title_key="observacion_titulo")
    costanera_page(c, data, meta)
    proximos_pasos_page(c, data, meta)
    nota_metodologica_page(c, data, meta)
    c.save()
    print(f"OK: {PDF_OUT} ({PDF_OUT.stat().st_size} bytes, {TOTAL_PAGES} páginas)")


if __name__ == "__main__":
    main()
