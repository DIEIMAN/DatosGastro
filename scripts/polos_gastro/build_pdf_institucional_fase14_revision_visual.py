"""Build the visual-revision PDF for PolosGastro.

This script only reads local artifacts from prior PolosGastro phases. It does
not call APIs, does not mutate source data, and does not overwrite the first
Fase 14 PDF.
"""
from __future__ import annotations

import csv
import html
import math
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[2]

DOCS_OUT = ROOT / "docs" / "polos_gastro" / "fase14_pdf_institucional_revision_visual"
OUT = ROOT / "outputs" / "polos_gastro" / "fase14_pdf_institucional_revision_visual"
ASSETS = OUT / "assets"

PHASE11 = ROOT / "outputs" / "polos_gastro" / "fase11_google_places_piloto" / "tablas"
PHASE13_ASSETS = ROOT / "outputs" / "polos_gastro" / "fase13_mapas" / "assets"
PHASE13_TABLES = ROOT / "outputs" / "polos_gastro" / "fase13_mapas" / "tablas"

CONSOLIDADO = PHASE11 / "consolidado_tandas_google_places.csv"
MAPA_REVISION = PHASE13_TABLES / "locales_para_mapa_revision.csv"
GLOBAL_MAP_SRC = PHASE13_ASSETS / "mapa_global_22_polos_ejes.png"

MENTIONS_CSV = OUT / "menciones_destacadas_por_polo.csv"
PDF = OUT / "INFORME_POLOS_GASTRO_DGDGAS_PRELIMINAR_V2.pdf"
HTML = OUT / "preview_informe_polos_gastro_dgdgas_v2.html"
MD_BASE = DOCS_OUT / "INFORME_POLOS_GASTRO_DGDGAS_PDF_BASE_REVISION_VISUAL.md"

INSTITUCION = "DGDGAS - Dirección General de Desarrollo Gastronómico"
GOBIERNO = "Gobierno de la Ciudad de Buenos Aires"
TITLE = "Polos gastronómicos de la Ciudad de Buenos Aires"
SUBTITLE = "Universo semilla, lectura territorial y capa auxiliar de geolocalización"

W, H = A4
M = 44
TOTAL_PAGES = 18

AZUL = "#1F3B57"
AZUL2 = "#2C6E9E"
ROJO = "#C0392B"
VERDE = "#1A9850"
NARANJA = "#C0762B"
NEGRO = "#222222"
GRIS = "#555555"
GRIS2 = "#6B7280"
LINEA = "#D9DEE5"
SOFT = "#F5F7FA"
SOFT_AZUL = "#EAF1F8"
SOFT_VERDE = "#EAF5EE"
SOFT_NARANJA = "#F8EDE0"
SOFT_ROJO = "#FBEAEA"

FONT = "Helvetica"
FONT_BOLD = "Helvetica-Bold"

SAFE_STATES = {"match_fuerte", "match_razonable_revisar_sede"}
EXCLUDED_STATES = {"vigencia_no_confirmada", "query_a_corregir", "duplicado_probable"}


@dataclass(frozen=True)
class Candidate:
    page: str
    polo: str
    subzona: str
    name: str
    tipo: str = "mención gastronómica"
    aliases: tuple[str, ...] = ()
    pdf_policy: str = "allowed"
    map_policy: str = "auto"


CANDIDATES: list[Candidate] = [
    Candidate("palermo", "Palermo", "Palermo / Las Cañitas", "Don Julio"),
    Candidate("palermo", "Palermo", "Palermo / Las Cañitas", "La Cabrera"),
    Candidate("palermo", "Palermo", "Palermo / Las Cañitas", "Niño Gordo", aliases=("Nino Gordo",)),
    Candidate("palermo", "Palermo", "Palermo / Las Cañitas", "Gran Dabbang"),
    Candidate("palermo", "Palermo", "Palermo / Las Cañitas", "Mishiguene"),
    Candidate("palermo", "Palermo", "Palermo / Las Cañitas", "La Mar"),
    Candidate("palermo", "Palermo", "Palermo / Las Cañitas", "Cosi Mi Piace"),
    Candidate("palermo", "Palermo", "Las Cañitas", "Campo Bravo"),
    Candidate("palermo", "Palermo", "Las Cañitas", "Kansas"),
    Candidate("palermo", "Palermo", "Las Cañitas", "SushiClub"),
    Candidate("palermo", "Palermo", "Palermo", "Café Registrado", aliases=("Cafe Registrado",), pdf_policy="caution_if_allowed"),
    Candidate("palermo", "Palermo", "Palermo / Las Cañitas", "Osaka"),
    Candidate("palermo", "Palermo", "Palermo / Las Cañitas", "Aldo's", aliases=("Aldo", "Aldo’s")),
    Candidate("palermo", "Palermo", "Palermo / Las Cañitas", "Las Pizarras Bistro"),
    Candidate("palermo", "Palermo", "Palermo / Las Cañitas", "Francisca del Fuego"),
    Candidate("palermo", "Palermo", "Las Cañitas", "Morelia"),
    Candidate("palermo", "Palermo", "Palermo / Las Cañitas", "Oporto"),

    Candidate("puerto", "Puerto Madero", "Zona costera / docks", "Cabaña Las Lilas", aliases=("Cabana Las Lilas",), pdf_policy="review_visible"),
    Candidate("puerto", "Puerto Madero", "Zona costera / docks", "Chila"),
    Candidate("puerto", "Puerto Madero", "Zona costera / docks", "Happening"),
    Candidate("puerto", "Puerto Madero", "Zona costera / docks", "Sottovoce"),
    Candidate("puerto", "Puerto Madero", "Zona costera / docks", "El Mercado / Faena", tipo="hito colectivo"),
    Candidate("puerto", "Puerto Madero", "Zona costera / docks", "La Parolaccia Casa Tua", pdf_policy="caution_if_allowed"),
    Candidate("puerto", "Puerto Madero", "Zona costera / docks", "Le Grill"),
    Candidate("puerto", "Puerto Madero", "Zona costera / docks", "Red Resto & Lounge", pdf_policy="review_visible"),
    Candidate("puerto", "Puerto Madero", "Zona costera / docks", "Patagonia Sur", pdf_policy="review_visible", map_policy="no"),

    Candidate("san_telmo", "San Telmo", "San Telmo", "Mercado de San Telmo", tipo="hito colectivo", pdf_policy="review_visible"),
    Candidate("san_telmo", "San Telmo", "San Telmo", "La Brigada"),
    Candidate("san_telmo", "San Telmo", "San Telmo", "El Preferido de San Telmo", pdf_policy="review_visible", map_policy="no"),
    Candidate("san_telmo", "San Telmo", "San Telmo", "Café San Juan", aliases=("Cafe San Juan",)),
    Candidate("san_telmo", "San Telmo", "San Telmo", "Pulpería Quilapán", aliases=("Pulperia Quilapan",), pdf_policy="review_visible"),
    Candidate("san_telmo", "San Telmo", "San Telmo", "Hierbabuena"),
    Candidate("san_telmo", "San Telmo", "San Telmo", "Napoles", pdf_policy="review_visible"),

    Candidate("corrientes", "Avenida Corrientes", "Corrientes", "Güerrín", aliases=("Guerrin",), pdf_policy="review_visible"),
    Candidate("corrientes", "Avenida Corrientes", "Corrientes", "Las Cuartetas"),
    Candidate("corrientes", "Avenida Corrientes", "Corrientes", "El Palacio de la Pizza"),
    Candidate("corrientes", "Avenida Corrientes", "Corrientes", "Pertutti"),
    Candidate("corrientes", "Avenida Corrientes", "Corrientes", "Moulin Bleu", pdf_policy="review_visible", map_policy="no"),
    Candidate("corrientes", "Avenida Corrientes", "Corrientes", "La Reina Kunti"),
    Candidate("corrientes", "Abasto", "Abasto", "Abasto - área a reforzar", tipo="área a reforzar", pdf_policy="manual_note", map_policy="no"),

    Candidate("belgrano", "Belgrano", "Barrio Chino", "Hong Kong Style"),
    Candidate("belgrano", "Belgrano", "Barrio Chino", "China Rose"),
    Candidate("belgrano", "Belgrano", "Barrio Chino", "Ichisou", pdf_policy="caution_if_allowed", map_policy="no"),
    Candidate("belgrano", "Belgrano", "Barrio Chino", "Ramen Neko", pdf_policy="review_visible", map_policy="no"),
    Candidate("belgrano", "Belgrano", "Barrio Chino", "Ichiban", pdf_policy="review_visible", map_policy="no"),
    Candidate("belgrano", "Belgrano", "Barrio Chino", "BAO Kitchen", pdf_policy="caution_if_allowed", map_policy="no"),
    Candidate("belgrano", "Belgrano", "Bajo Belgrano", "Tori Tori", pdf_policy="caution_if_allowed", map_policy="no"),
    Candidate("belgrano", "Belgrano", "Bajo Belgrano", "Anafe", aliases=("Anafe original",), map_policy="no"),
    Candidate("belgrano", "Belgrano", "Bajo Belgrano", "La Mar", pdf_policy="caution_if_allowed", map_policy="no"),
    Candidate("belgrano", "Belgrano", "Barrio Chino / Bajo Belgrano", "Casa China", pdf_policy="exclude_non_restaurant", map_policy="no"),
    Candidate("belgrano", "Belgrano", "Belgrano R", "Belgrano R - subzona a reforzar", tipo="área a reforzar", pdf_policy="manual_note", map_policy="no"),
]


MAP_CONFIGS = {
    "palermo": {
        "title": "Palermo / Las Cañitas",
        "bbox": (-58.443, -34.597, -58.408, -34.562),
        "labels": [(-58.430, -34.587, "Palermo Soho / Hollywood"), (-58.431, -34.572, "Las Cañitas")],
        "areas": [(-58.428, -34.584, 0.030, 0.022, "núcleo Palermo"), (-58.431, -34.571, 0.016, 0.009, "Las Cañitas")],
    },
    "puerto": {
        "title": "Puerto Madero",
        "bbox": (-58.375, -34.621, -58.358, -34.598),
        "labels": [(-58.364, -34.609, "docks / eje costero")],
        "water": True,
        "areas": [(-58.365, -34.609, 0.010, 0.020, "eje costero")],
    },
    "san_telmo": {
        "title": "San Telmo",
        "bbox": (-58.378, -34.629, -58.367, -34.616),
        "labels": [(-58.372, -34.619, "entorno Mercado"), (-58.372, -34.625, "Caseros / Defensa")],
        "areas": [(-58.372, -34.621, 0.008, 0.010, "área barrial")],
    },
    "corrientes": {
        "title": "Corrientes / Abasto",
        "bbox": (-58.416, -34.608, -58.374, -34.598),
        "labels": [(-58.387, -34.603, "Corrientes 9 de Julio - Callao"), (-58.410, -34.604, "Abasto: reforzar")],
        "corrientes": True,
    },
    "belgrano": {
        "title": "Belgrano y subzonas",
        "bbox": (-58.462, -34.566, -58.438, -34.548),
        "labels": [(-58.452, -34.556, "Barrio Chino"), (-58.446, -34.560, "Bajo Belgrano"), (-58.458, -34.561, "Belgrano R: reforzar")],
        "areas": [(-58.452, -34.556, 0.010, 0.008, "Barrio Chino"), (-58.446, -34.560, 0.010, 0.008, "Bajo Belgrano"), (-58.458, -34.561, 0.008, 0.006, "Belgrano R")],
    },
}


DETAIL_TEXT = {
    "palermo": {
        "page": 7,
        "title": "Palermo / Las Cañitas",
        "subtitle": "Zona con mayor volumen de menciones y subzonas internas visibles.",
        "reading": "La lectura concentra el mayor volumen del universo semilla y permite distinguir subzonas internas. Se muestra como orientación territorial, no como ranking ni padrón oficial.",
        "caution": "Las menciones provienen del universo semilla y deben validarse antes de cualquier uso operativo. No se ordenan por calidad ni por desempeño.",
    },
    "puerto": {
        "page": 8,
        "title": "Puerto Madero",
        "subtitle": "Polo consolidado costero con hitos y sedes que requieren verificación fina.",
        "reading": "La zona se lee como corredor costero/docks. Los hitos colectivos ayudan a explicar el polo, pero no reemplazan la validación de sedes puntuales.",
        "caution": "Las menciones marcadas a validar no se usan como puntos activos. El recorte operativo debe revisar sede y tramo antes de circular.",
    },
    "san_telmo": {
        "page": 9,
        "title": "San Telmo",
        "subtitle": "Área patrimonial con hito colectivo y menciones gastronómicas del entorno.",
        "reading": "El Mercado de San Telmo se trata como hito colectivo. La lectura combina identidad barrial, patrimonio urbano y referencias gastronómicas cercanas.",
        "caution": "Los hitos colectivos no son restaurantes puntuales. Las sedes con duda se mantienen como a validar y no como oferta activa confirmada.",
    },
    "corrientes": {
        "page": 10,
        "title": "Corrientes / Abasto",
        "subtitle": "Ejes vinculados con delimitación distinta y sin doble conteo.",
        "reading": "Corrientes se representa como eje teatral-gastronómico entre 9 de Julio y Callao. Abasto se muestra como área a reforzar alrededor del shopping.",
        "caution": "Abasto no se fuerza con puntos propios cuando la evidencia queda duplicada o pendiente. La página separa ambos recortes para evitar doble conteo.",
    },
    "belgrano": {
        "page": 11,
        "title": "Belgrano y subzonas",
        "subtitle": "Macroárea con respaldo diferenciado por subzona.",
        "reading": "Barrio Chino tiene identidad gastronómica clara. Bajo Belgrano conserva sedes a validar y Belgrano R se presenta como subzona a reforzar documentalmente.",
        "caution": "No se sobredimensiona la macroárea: el mapa muestra subzonas de trabajo y no una delimitación oficial ni un padrón de locales activos.",
    },
}


def norm(value: str | None) -> str:
    value = value or ""
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    return value.lower().replace("'", "").replace("’", "").strip()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


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


def pil_font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    names = ["arialbd.ttf", "calibrib.ttf"] if bold else ["arial.ttf", "calibri.ttf"]
    for name in names:
        path = Path("C:/Windows/Fonts") / name
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def hex_rgb(color: str) -> tuple[int, int, int]:
    color = color.lstrip("#")
    return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))


def hex_to_rgb_float(color: str) -> tuple[float, float, float]:
    r, g, b = hex_rgb(color)
    return r / 255, g / 255, b / 255


def set_fill(c: canvas.Canvas, color: str) -> None:
    c.setFillColorRGB(*hex_to_rgb_float(color))


def set_stroke(c: canvas.Canvas, color: str) -> None:
    c.setStrokeColorRGB(*hex_to_rgb_float(color))


def wrap_text(text: str, font: str, size: float, max_width: float) -> list[str]:
    lines: list[str] = []
    for raw in text.splitlines() or [""]:
        words = raw.split()
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
        elif raw == "":
            lines.append("")
    return lines


def draw_wrapped(
    c: canvas.Canvas,
    text: str,
    x: float,
    y: float,
    max_width: float,
    *,
    font: str = FONT,
    size: float = 9.5,
    color: str = NEGRO,
    leading: float | None = None,
    max_lines: int | None = None,
) -> float:
    lines = wrap_text(text, font, size, max_width)
    if max_lines is not None:
        lines = lines[:max_lines]
    c.setFont(font, size)
    set_fill(c, color)
    leading = leading or size * 1.25
    for line in lines:
        c.drawString(x, y, line)
        y -= leading
    return y


def draw_title(c: canvas.Canvas, x: float, y: float, text: str, size: float = 18) -> float:
    set_fill(c, AZUL)
    c.setFont(FONT_BOLD, size)
    for line in wrap_text(text, FONT_BOLD, size, W - 2 * M):
        c.drawString(x, y, line)
        y -= size * 1.12
    set_stroke(c, ROJO)
    c.setLineWidth(2)
    c.line(x, y + 8, x + 150, y + 8)
    return y - 10


def header(c: canvas.Canvas, page_no: int, kicker: str, title: str, subtitle: str = "") -> float:
    set_fill(c, ROJO)
    c.setFont(FONT_BOLD, 8.3)
    c.drawString(M, H - 34, kicker.upper())
    set_fill(c, GRIS)
    c.setFont(FONT, 8.3)
    c.drawRightString(W - M, H - 34, f"{page_no} / {TOTAL_PAGES}")
    y = draw_title(c, M, H - 62, title)
    if subtitle:
        y = draw_wrapped(c, subtitle, M, y, W - 2 * M, font=FONT, size=9.5, color=GRIS, leading=12)
    return y - 8


def footer(c: canvas.Canvas, note: str | None = None) -> None:
    if note:
        draw_wrapped(c, note, M, 63, W - 2 * M, font=FONT, size=7.2, color=GRIS, leading=8.5)
    set_stroke(c, LINEA)
    c.setLineWidth(0.8)
    c.line(M, 47, W - M, 47)
    set_fill(c, AZUL)
    c.setFont(FONT_BOLD, 7.8)
    c.drawString(M, 30, f"{INSTITUCION} · {GOBIERNO}")


def finish(c: canvas.Canvas, note: str | None = None) -> None:
    footer(c, note)
    c.showPage()


def note_box(
    c: canvas.Canvas,
    x: float,
    y: float,
    w: float,
    h: float,
    title: str,
    text: str,
    *,
    color: str = AZUL2,
    fill: str = SOFT_AZUL,
    size: float = 8.5,
) -> None:
    set_fill(c, fill)
    set_stroke(c, color)
    c.setLineWidth(1.0)
    c.roundRect(x, y, w, h, 4, fill=1, stroke=1)
    set_fill(c, color)
    c.rect(x, y, 7, h, fill=1, stroke=0)
    set_fill(c, color)
    c.setFont(FONT_BOLD, 8.8)
    title_y = y + h - 17
    title_lines = wrap_text(title, FONT_BOLD, 8.8, w - 28)
    for line in title_lines:
        c.drawString(x + 16, title_y, line)
        title_y -= 10.5
    draw_wrapped(c, text, x + 16, title_y - 4, w - 28, font=FONT, size=size, color=NEGRO, leading=size * 1.23)


def bullet_list(
    c: canvas.Canvas,
    items: list[str],
    x: float,
    y: float,
    max_width: float,
    *,
    size: float = 9.5,
    gap: float = 8,
) -> float:
    for item in items:
        set_fill(c, ROJO)
        c.setFont(FONT_BOLD, size)
        c.drawString(x, y, "•")
        lines = wrap_text(item, FONT, size, max_width - 17)
        set_fill(c, NEGRO)
        c.setFont(FONT, size)
        yy = y
        for line in lines:
            c.drawString(x + 15, yy, line)
            yy -= size * 1.23
        y = yy - gap
    return y


def kpi_card(c: canvas.Canvas, x: float, y: float, w: float, h: float, value: str, label: str, color: str) -> None:
    set_fill(c, SOFT)
    set_stroke(c, color)
    c.setLineWidth(1.2)
    c.roundRect(x, y, w, h, 4, fill=1, stroke=1)
    set_fill(c, color)
    c.setFont(FONT_BOLD, 21)
    c.drawCentredString(x + w / 2, y + h - 30, value)
    set_fill(c, GRIS)
    c.setFont(FONT, 7.7)
    yy = y + h - 48
    for line in wrap_text(label, FONT, 7.7, w - 12):
        c.drawCentredString(x + w / 2, yy, line)
        yy -= 8.8


def cards_row(c: canvas.Canvas, y: float, cards: list[tuple[str, str, str]], *, x: float = M, total_w: float | None = None) -> None:
    total_w = total_w or W - 2 * M
    gap = 8
    card_w = (total_w - gap * (len(cards) - 1)) / len(cards)
    for idx, (value, label, color) in enumerate(cards):
        kpi_card(c, x + idx * (card_w + gap), y, card_w, 68, value, label, color)


def image_box(c: canvas.Canvas, img_path: Path, x: float, y: float, max_w: float, max_h: float, *, border: bool = True) -> None:
    if border:
        set_fill(c, "#FFFFFF")
        set_stroke(c, LINEA)
        c.roundRect(x, y, max_w, max_h, 4, fill=1, stroke=1)
    img = Image.open(img_path)
    iw, ih = img.size
    scale = min(max_w / iw, max_h / ih)
    dw, dh = iw * scale, ih * scale
    dx = x + (max_w - dw) / 2
    dy = y + (max_h - dh) / 2
    c.drawImage(ImageReader(str(img_path)), dx, dy, width=dw, height=dh, mask="auto")


def find_row(rows: list[dict[str, str]], cand: Candidate) -> dict[str, str] | None:
    aliases = {norm(cand.name), *(norm(a) for a in cand.aliases)}
    candidates = [r for r in rows if norm(r.get("polo")) == norm(cand.polo)]
    if not candidates and cand.polo == "Abasto":
        candidates = [r for r in rows if norm(r.get("polo")) == "abasto"]
    for row in candidates:
        row_name = norm(row.get("nombre_lugar_original"))
        if any(alias and (alias in row_name or row_name in alias) for alias in aliases):
            return row
    for row in rows:
        row_name = norm(row.get("nombre_lugar_original"))
        if any(alias and (alias in row_name or row_name in alias) for alias in aliases):
            return row
    return None


def map_row_index(rows: list[dict[str, str]]) -> dict[tuple[str, str], dict[str, str]]:
    index: dict[tuple[str, str], dict[str, str]] = {}
    for row in rows:
        index[(norm(row.get("polo")), norm(row.get("nombre_lugar")))] = row
    return index


def inside_bbox(row: dict[str, str] | None, bbox: tuple[float, float, float, float]) -> bool:
    if not row:
        return False
    try:
        lat = float(row.get("lat", ""))
        lon = float(row.get("lon", ""))
    except ValueError:
        return False
    min_lon, min_lat, max_lon, max_lat = bbox
    return min_lon <= lon <= max_lon and min_lat <= lat <= max_lat


def evaluate_candidate(
    cand: Candidate,
    consolidado: list[dict[str, str]],
    maps_by_key: dict[tuple[str, str], dict[str, str]],
) -> dict[str, str]:
    if cand.pdf_policy == "manual_note":
        return {
            "page": cand.page,
            "polo": cand.polo,
            "subzona": cand.subzona,
            "nombre_lugar": cand.name,
            "tipo_mencion": cand.tipo,
            "estado_para_informe": "área a reforzar",
            "incluir_en_pdf": "si_con_cautela",
            "incluir_en_mapa_detalle": "no",
            "observacion": "Se presenta como subzona de lectura, sin locales propios sólidos en esta instancia.",
        }

    row = find_row(consolidado, cand)
    if not row:
        return {
            "page": cand.page,
            "polo": cand.polo,
            "subzona": cand.subzona,
            "nombre_lugar": cand.name,
            "tipo_mencion": cand.tipo,
            "estado_para_informe": "no encontrado en consolidado",
            "incluir_en_pdf": "no",
            "incluir_en_mapa_detalle": "no",
            "observacion": "No se encontró una coincidencia local suficiente en el consolidado usado para esta versión.",
        }

    state = row.get("estado_consolidado", "")
    decision = row.get("decision_borrador4", "")
    map_row = maps_by_key.get((norm(row.get("polo")), norm(row.get("nombre_lugar_original"))))
    cfg = MAP_CONFIGS.get(cand.page)
    in_area = inside_bbox(map_row, cfg["bbox"]) if cfg else False

    include_pdf = "no"
    include_map = "no"
    status = ""
    obs = ""

    if cand.pdf_policy == "exclude_non_restaurant":
        status = "excluido por prudencia"
        obs = "Se conserva como referencia semilla, pero no se presenta como mención gastronómica destacada sin validación específica."
    elif state in EXCLUDED_STATES:
        status = "excluido por prudencia"
        obs = f"Estado {state}; no se incluye como destacado visible ni como punto de detalle."
    elif state == "zona_sucursal_a_revisar":
        if cand.pdf_policy == "review_visible":
            include_pdf = "si_con_cautela"
            include_map = "si_validar" if cand.map_policy != "no" and in_area else "no"
            status = "a validar"
            obs = "Sede o zona pendiente; puede mencionarse con cautela, sin tratarlo como punto activo confirmado."
        else:
            status = "a validar"
            obs = "Sede o zona pendiente; se excluye de destacados visibles hasta validación."
    elif state in SAFE_STATES and decision == "puede_mencionarse_con_prudencia":
        if cand.pdf_policy == "caution_if_allowed":
            include_pdf = "si_con_cautela"
            status = "incluido con cautela"
            obs = "Mención permitida por el consolidado, con sede/subzona a validar antes de uso operativo."
        else:
            include_pdf = "si"
            status = "incluido con prudencia"
            obs = "Coincidencia razonable o fuerte en el consolidado; no equivale a padrón oficial."
        include_map = "si" if cand.map_policy != "no" and in_area else "no"
    else:
        status = "a validar"
        obs = "Requiere decisión humana antes de figurar como destacado visible."

    return {
        "page": cand.page,
        "polo": cand.polo,
        "subzona": cand.subzona,
        "nombre_lugar": cand.name,
        "tipo_mencion": cand.tipo,
        "estado_para_informe": status,
        "incluir_en_pdf": include_pdf,
        "incluir_en_mapa_detalle": include_map,
        "observacion": obs,
    }


def build_mentions() -> list[dict[str, str]]:
    consolidado = read_csv(CONSOLIDADO)
    mapa_rows = read_csv(MAPA_REVISION)
    maps_by_key = map_row_index(mapa_rows)
    mentions = [evaluate_candidate(cand, consolidado, maps_by_key) for cand in CANDIDATES]
    OUT.mkdir(parents=True, exist_ok=True)
    with MENTIONS_CSV.open("w", encoding="utf-8-sig", newline="") as fh:
        fieldnames = [
            "polo",
            "subzona",
            "nombre_lugar",
            "tipo_mencion",
            "estado_para_informe",
            "incluir_en_pdf",
            "incluir_en_mapa_detalle",
            "observacion",
        ]
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in mentions:
            writer.writerow({k: row[k] for k in fieldnames})
    return mentions


def copy_global_map() -> Path:
    ASSETS.mkdir(parents=True, exist_ok=True)
    dest = ASSETS / "global_mapa_pdf_v2.png"
    img = Image.open(GLOBAL_MAP_SRC).convert("RGBA")
    crop = img.crop((105, 360, 1985, 2465))
    base = Image.new("RGB", crop.size, "white")
    base.paste(crop, mask=crop.split()[-1])
    base.save(dest, optimize=True)
    return dest


def draw_rounded_rect(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], radius: int, fill: str, outline: str, width: int = 2) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def latlon_to_xy(
    lon: float,
    lat: float,
    bbox: tuple[float, float, float, float],
    panel: tuple[int, int, int, int],
) -> tuple[int, int]:
    min_lon, min_lat, max_lon, max_lat = bbox
    x0, y0, x1, y1 = panel
    x = x0 + (lon - min_lon) / (max_lon - min_lon) * (x1 - x0)
    y = y1 - (lat - min_lat) / (max_lat - min_lat) * (y1 - y0)
    return int(x), int(y)


def draw_ellipse_geo(
    draw: ImageDraw.ImageDraw,
    bbox: tuple[float, float, float, float],
    panel: tuple[int, int, int, int],
    lon: float,
    lat: float,
    w_lon: float,
    h_lat: float,
    *,
    fill: str,
    outline: str,
) -> None:
    x0, y0 = latlon_to_xy(lon - w_lon / 2, lat + h_lat / 2, bbox, panel)
    x1, y1 = latlon_to_xy(lon + w_lon / 2, lat - h_lat / 2, bbox, panel)
    draw.ellipse((x0, y0, x1, y1), fill=fill, outline=outline, width=3)


def draw_triangle(draw: ImageDraw.ImageDraw, x: int, y: int, color: str) -> None:
    pts = [(x, y - 12), (x - 11, y + 9), (x + 11, y + 9)]
    draw.polygon(pts, fill="white", outline=hex_rgb(color))
    draw.line([pts[0], pts[1], pts[2], pts[0]], fill=hex_rgb(color), width=4)


def draw_diamond(draw: ImageDraw.ImageDraw, x: int, y: int, color: str) -> None:
    pts = [(x, y - 13), (x - 13, y), (x, y + 13), (x + 13, y)]
    draw.polygon(pts, fill=hex_rgb(color), outline="white")


def candidate_by_name(page: str, name: str) -> Candidate | None:
    nn = norm(name)
    for cand in CANDIDATES:
        if cand.page == page and (norm(cand.name) == nn or nn in {norm(a) for a in cand.aliases}):
            return cand
    return None


def make_clean_map(page: str, mentions: list[dict[str, str]]) -> Path:
    cfg = MAP_CONFIGS[page]
    img = Image.new("RGB", (1200, 1040), "white")
    draw = ImageDraw.Draw(img)
    f_title = pil_font(42, bold=True)
    f_label = pil_font(26, bold=True)
    f_small = pil_font(22)
    f_tiny = pil_font(18)
    panel = (78, 118, 1122, 875)

    draw.rectangle((0, 0, 1200, 1040), fill=hex_rgb("#FFFFFF"))
    draw.text((76, 44), cfg["title"], fill=hex_rgb(AZUL), font=f_title)
    draw.line((78, 96, 392, 96), fill=hex_rgb(ROJO), width=6)
    draw_rounded_rect(draw, panel, 20, "#F7F9FB", LINEA, width=3)

    if cfg.get("water"):
        draw.rectangle((850, panel[1] + 2, panel[2] - 2, panel[3] - 2), fill=hex_rgb("#DDECF7"))
        draw.text((875, 164), "frente costero", fill=hex_rgb("#55748F"), font=f_small)

    for idx in range(1, 6):
        x = panel[0] + idx * (panel[2] - panel[0]) // 6
        y = panel[1] + idx * (panel[3] - panel[1]) // 6
        draw.line((x, panel[1] + 10, x, panel[3] - 10), fill=hex_rgb("#E6EAF0"), width=2)
        draw.line((panel[0] + 10, y, panel[2] - 10, y), fill=hex_rgb("#E6EAF0"), width=2)

    if cfg.get("corrientes"):
        x_left, y_axis = latlon_to_xy(-58.412, -34.6037, cfg["bbox"], panel)
        x_right, y_axis2 = latlon_to_xy(-58.376, -34.6030, cfg["bbox"], panel)
        draw.line((x_left, y_axis, x_right, y_axis2), fill=hex_rgb(AZUL), width=11)
        draw.text((x_left + 35, y_axis - 55), "Corrientes: eje 9 de Julio - Callao", fill=hex_rgb(AZUL), font=f_label)
        ax, ay = latlon_to_xy(-58.410, -34.6038, cfg["bbox"], panel)
        draw.ellipse((ax - 108, ay - 108, ax + 108, ay + 108), fill=hex_rgb("#F8EDE0"), outline=hex_rgb(NARANJA), width=4)
        draw.text((ax - 94, ay + 115), "Abasto: área a reforzar", fill=hex_rgb(NARANJA), font=f_small)
    else:
        for lon, lat, w_lon, h_lat, _ in cfg.get("areas", []):
            draw_ellipse_geo(draw, cfg["bbox"], panel, lon, lat, w_lon, h_lat, fill="#EAF1F8", outline=AZUL2)

    for lon, lat, label in cfg.get("labels", []):
        x, y = latlon_to_xy(lon, lat, cfg["bbox"], panel)
        draw.text((x + 10, y - 18), label, fill=hex_rgb(GRIS), font=f_small)

    mapa_rows = read_csv(MAPA_REVISION)
    rows_by_key = map_row_index(mapa_rows)
    plotted = []
    for mention in mentions:
        if mention["page"] != page:
            continue
        if mention["incluir_en_mapa_detalle"] not in {"si", "si_validar"}:
            continue
        row = rows_by_key.get((norm(mention["polo"]), norm(mention["nombre_lugar"])))
        if not row:
            row = rows_by_key.get((norm("Avenida Corrientes"), norm(mention["nombre_lugar"])))
        if not row or not inside_bbox(row, cfg["bbox"]):
            continue
        lon = float(row["lon"])
        lat = float(row["lat"])
        x, y = latlon_to_xy(lon, lat, cfg["bbox"], panel)
        state = mention["incluir_en_mapa_detalle"]
        tipo = mention["tipo_mencion"]
        if tipo == "hito colectivo":
            draw_diamond(draw, x, y, ROJO)
        elif state == "si_validar":
            draw_triangle(draw, x, y, NARANJA)
        else:
            fill = AZUL2 if mention["estado_para_informe"] == "incluido con prudencia" else VERDE
            draw.ellipse((x - 13, y - 13, x + 13, y + 13), fill=hex_rgb(fill), outline="white", width=3)
        plotted.append((x, y, mention["nombre_lugar"]))

    legend_y = 910
    draw.ellipse((82, legend_y, 110, legend_y + 28), fill=hex_rgb(AZUL2), outline="white", width=2)
    draw.text((124, legend_y - 1), "mención incluida con prudencia", fill=hex_rgb(NEGRO), font=f_small)
    draw_triangle(draw, 510, legend_y + 14, NARANJA)
    draw.text((538, legend_y - 1), "sede o zona a validar", fill=hex_rgb(NEGRO), font=f_small)
    draw_diamond(draw, 880, legend_y + 14, ROJO)
    draw.text((907, legend_y - 1), "hito colectivo", fill=hex_rgb(NEGRO), font=f_small)
    draw.text((78, 972), "Mapa esquemático de lectura territorial. No delimita oficialmente áreas ni confirma actividad vigente.", fill=hex_rgb(GRIS2), font=f_small)

    dest = ASSETS / f"mapa_detalle_{page}_v2.png"
    img.save(dest, optimize=True)
    return dest


def build_assets(mentions: list[dict[str, str]]) -> dict[str, Path]:
    ASSETS.mkdir(parents=True, exist_ok=True)
    paths = {"global": copy_global_map()}
    for page in DETAIL_TEXT:
        paths[page] = make_clean_map(page, mentions)
    return paths


def visible_mentions(mentions: list[dict[str, str]], page: str) -> str:
    included = [m for m in mentions if m["page"] == page and m["incluir_en_pdf"] == "si"]
    caution = [m for m in mentions if m["page"] == page and m["incluir_en_pdf"] == "si_con_cautela"]
    lines: list[str] = []
    if included:
        by_sub: dict[str, list[str]] = {}
        for m in included:
            by_sub.setdefault(m["subzona"], []).append(m["nombre_lugar"])
        for subzona, names in by_sub.items():
            lines.append(f"{subzona}: " + "; ".join(names) + ".")
    if caution:
        names = "; ".join(m["nombre_lugar"] for m in caution)
        lines.append(f"A validar o tratar como hito: {names}.")
    if page == "corrientes":
        lines.append("Abasto: área a reforzar documentalmente, sin puntos propios sólidos en esta versión.")
    if page == "belgrano":
        lines.append("Belgrano R: subzona a reforzar documentalmente.")
    return "\n".join(lines)


def excluded_summary(mentions: list[dict[str, str]]) -> str:
    excluded = [m for m in mentions if m["incluir_en_pdf"] == "no"]
    return (
        f"Se documentaron {len(excluded)} candidatos excluidos de destacados visibles por prudencia: "
        "vigencia no confirmada, búsqueda a corregir, duplicado probable, sede no resuelta o falta de correspondencia gastronómica suficiente."
    )


def cover(c: canvas.Canvas) -> None:
    set_fill(c, AZUL)
    c.rect(0, H * 0.67, W, H * 0.33, fill=1, stroke=0)
    set_fill(c, ROJO)
    c.rect(0, H * 0.665, W, 5, fill=1, stroke=0)
    set_fill(c, "#FFFFFF")
    c.setFont(FONT_BOLD, 22)
    c.drawString(M, H - 58, "DGDGAS")
    set_stroke(c, ROJO)
    c.setLineWidth(2.2)
    c.line(M, H - 72, M + 105, H - 72)
    c.setFont(FONT_BOLD, 12.5)
    c.drawString(M, H - 95, "Dirección General de Desarrollo Gastronómico")
    set_fill(c, "#CDD9E5")
    c.setFont(FONT_BOLD, 9)
    c.drawString(M, H - 117, GOBIERNO.upper())
    set_fill(c, "#FFFFFF")
    c.setFont(FONT_BOLD, 25)
    c.drawString(M, H - 210, "Polos gastronómicos de la")
    c.drawString(M, H - 240, "Ciudad de Buenos Aires")
    set_fill(c, "#CDD9E5")
    c.setFont(FONT_BOLD, 14)
    c.drawString(M, H - 275, "Informe")
    set_fill(c, AZUL)
    c.setFont(FONT_BOLD, 13.2)
    c.drawString(M, H - 350, SUBTITLE)
    set_stroke(c, ROJO)
    c.setLineWidth(2.4)
    c.line(M, H - 370, M + 365, H - 370)
    bajada = (
        "Lectura institucional del universo semilla de polos y ejes gastronómicos, "
        "con mapa global, páginas territoriales reforzadas y menciones destacadas tratadas "
        "con criterio prudente. No constituye padrón oficial ni ranking."
    )
    draw_wrapped(c, bajada, M, H - 410, W - 2 * M, font=FONT, size=11, color=NEGRO, leading=14.5)
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
        ("Criterio de menciones", "12"),
        ("Hallazgos de la capa auxiliar", "13"),
        ("Decisiones pendientes", "14"),
        ("Recomendaciones prudentes", "15"),
        ("Próximos pasos", "16"),
        ("Anexos", "17-18"),
    ]
    y = H - 144
    for label, page in items:
        set_fill(c, NEGRO)
        c.setFont(FONT, 10.5)
        c.drawString(M + 16, y, label)
        set_stroke(c, "#E6E8EC")
        c.setLineWidth(0.6)
        c.line(M + 16, y - 5, W - M - 32, y - 5)
        set_fill(c, GRIS)
        c.drawRightString(W - M, y, page)
        y -= 30
    finish(c)


def summary_page(c: canvas.Canvas) -> None:
    y = header(c, 3, "Resumen ejecutivo", "Qué ordena este informe", "Universo semilla, lectura territorial y señales para orientar validación.")
    cards_row(c, y - 68, [
        ("22", "polos/ejes del universo semilla", AZUL),
        ("106", "menciones de locales relevadas", VERDE),
        ("59", "coincidencias razonables o fuertes", AZUL2),
    ])
    cards_row(c, y - 146, [
        ("8", "casos con vigencia no confirmada", NARANJA),
        ("0", "resultados fuera de CABA", ROJO),
    ], x=M + 88, total_w=W - 2 * M - 176)
    bullet_list(c, [
        "El informe mantiene el mapa global de 22 polos/ejes como lectura principal del universo semilla.",
        "Las páginas de detalle combinan mapa esquemático, menciones destacadas, lectura territorial y nota de cautela.",
        "Las menciones no son ranking ni listado de calidad: son referencias del universo semilla con tratamiento prudente.",
        "Casos cerrados, búsquedas a corregir, duplicados probables y sedes no resueltas no se presentan como oferta activa.",
    ], M, y - 205, W - 2 * M, size=9.6, gap=8.5)
    note_box(c, M, 112, W - 2 * M, 78, "Cómo leer los números",
             "Son magnitudes del universo semilla y de la capa auxiliar de trabajo. Sirven para orientar validación territorial y decisiones de gestión; no equivalen a un censo ni a confirmación de actividad vigente.",
             color=AZUL, fill=SOFT_AZUL)
    finish(c)


def scope_page(c: canvas.Canvas) -> None:
    y = header(c, 4, "Alcance y criterio de lectura", "Qué afirma y qué no afirma la pieza")
    note_box(c, M, y - 88, W - 2 * M, 70, "Universo semilla",
             "Conjunto inicial de 22 polos/ejes y 106 menciones. Todos los polos se conservan en la lectura global, incluso aquellos sin locales explícitos.",
             color=AZUL2, fill=SOFT_AZUL)
    note_box(c, M, y - 176, W - 2 * M, 70, "Capa auxiliar",
             "Aporta ubicación orientativa, consistencia territorial y alertas de calidad. Acompaña la lectura; no reemplaza fuentes oficiales ni validación territorial.",
             color=VERDE, fill=SOFT_VERDE)
    set_fill(c, AZUL)
    c.setFont(FONT_BOLD, 11)
    c.drawString(M, y - 222, "El informe no afirma")
    bullet_list(c, [
        "que las 106 menciones correspondan a locales activos;",
        "que los límites territoriales sean oficiales;",
        "que la capa auxiliar valide por sí sola un polo o una sede;",
        "que las zonas con menor evidencia deban descartarse.",
    ], M, y - 250, W - 2 * M, gap=8.5)
    note_box(c, M, 108, W - 2 * M, 78, "Criterio institucional",
             "La pieza prioriza claridad para conducción: hallazgos principales en el cuerpo, menciones tratadas con cautela y decisiones pendientes separadas de los resultados.",
             color=NARANJA, fill=SOFT_NARANJA)
    finish(c)


def global_map_page(c: canvas.Canvas, maps: dict[str, Path]) -> None:
    y = header(c, 5, "Mapa global", "22 polos/ejes del universo semilla", "Áreas, ejes y zonas de lectura territorial; no delimitaciones oficiales.")
    image_box(c, maps["global"], M + 18, 108, W - 2 * M - 36, y - 116, border=False)
    finish(c, "El mapa representa el universo semilla completo y no reemplaza validación territorial.")


def territorial_page(c: canvas.Canvas) -> None:
    y = header(c, 6, "Lectura territorial general", "Qué muestra la distribución")
    note_box(c, M, y - 86, W - 2 * M, 70, "Polos consolidados",
             "Palermo concentra la mayor cantidad de menciones. Puerto Madero y San Telmo permiten una lectura clara cuando se separan hitos, sedes a validar y menciones permitidas.",
             color=AZUL2, fill=SOFT_AZUL)
    note_box(c, M, y - 176, W - 2 * M, 76, "Corredores y ejes",
             "Avenida Corrientes se trabaja como eje 9 de Julio-Callao. Abasto se trata como área alrededor del shopping y requiere refuerzo documental específico.",
             color=VERDE, fill=SOFT_VERDE)
    note_box(c, M, y - 272, W - 2 * M, 82, "Macroáreas y subzonas",
             "Belgrano se presenta como macroárea de trabajo: Barrio Chino, Bajo Belgrano y Belgrano R tienen respaldo diferenciado y no deben leerse como una misma evidencia.",
             color=NARANJA, fill=SOFT_NARANJA)
    bullet_list(c, [
        "Los mapas de detalle se reducen y se integran con cajas de lectura para evitar páginas dominadas por puntos débiles.",
        "Los nombres destacados se muestran fuera del mapa para preservar legibilidad.",
        "Las sedes a validar se separan de las menciones incluidas con mayor respaldo.",
    ], M, 240, W - 2 * M, gap=10)
    finish(c)


def detail_page(c: canvas.Canvas, page: str, maps: dict[str, Path], mentions: list[dict[str, str]]) -> None:
    cfg = DETAIL_TEXT[page]
    y = header(c, cfg["page"], "Detalle territorial", cfg["title"], cfg["subtitle"])
    map_x, map_y, map_w, map_h = M, 332, 316, 318
    side_x = M + 330
    side_w = W - M - side_x
    image_box(c, maps[page], map_x, map_y, map_w, map_h, border=True)
    note_box(c, side_x, 462, side_w, 188, "Menciones destacadas del universo semilla",
             visible_mentions(mentions, page), color=AZUL2, fill=SOFT_AZUL, size=7.2)
    note_box(c, side_x, 332, side_w, 112, "Lectura territorial",
             cfg["reading"], color=VERDE, fill=SOFT_VERDE, size=7.5)
    note_box(c, M, 145, W - 2 * M, 92, "Nota de cautela",
             cfg["caution"], color=NARANJA, fill=SOFT_NARANJA, size=8.7)
    draw_wrapped(c, "No es ranking, no es padrón oficial y no confirma actividad vigente.", M, 118, W - 2 * M, font=FONT_BOLD, size=8.4, color=GRIS, leading=10)
    finish(c)


def mentions_criteria_page(c: canvas.Canvas, mentions: list[dict[str, str]]) -> None:
    y = header(c, 12, "Criterio de menciones", "Cómo se seleccionan las referencias visibles")
    included = sum(1 for m in mentions if m["incluir_en_pdf"] == "si")
    caution = sum(1 for m in mentions if m["incluir_en_pdf"] == "si_con_cautela")
    excluded = sum(1 for m in mentions if m["incluir_en_pdf"] == "no")
    cards_row(c, y - 68, [
        (str(included), "menciones incluidas con prudencia", VERDE),
        (str(caution), "menciones o hitos a validar", NARANJA),
        (str(excluded), "candidatos excluidos del cuerpo", ROJO),
    ])
    bullet_list(c, [
        "Las menciones visibles provienen del universo semilla y se presentan como referencias, no como orden de mérito.",
        "Las sedes o hitos a validar se separan de las menciones con mayor respaldo.",
        "No se incorporan cerrados, vigencia no confirmada, duplicados probables ni búsquedas a corregir como destacados.",
        "Las páginas de detalle priorizan lectura territorial y evitan depender de puntos débiles.",
    ], M, y - 145, W - 2 * M, gap=9)
    note_box(c, M, 112, W - 2 * M, 82, "Criterio de prudencia",
             excluded_summary(mentions), color=AZUL, fill=SOFT_AZUL)
    finish(c)


def auxiliary_page(c: canvas.Canvas) -> None:
    y = header(c, 13, "Capa auxiliar", "Hallazgos para orientar validación")
    cards_row(c, y - 68, [
        ("59", "coincidencias razonables o fuertes", VERDE),
        ("8", "vigencia no confirmada", NARANJA),
        ("11", "duplicados probables", AZUL2),
    ])
    cards_row(c, y - 146, [
        ("25", "zona o sede a validar", NARANJA),
        ("3", "búsquedas a corregir", ROJO),
    ], x=M + 88, total_w=W - 2 * M - 176)
    bullet_list(c, [
        "Las coincidencias razonables o fuertes permiten orientar la validación territorial.",
        "Los casos con vigencia no confirmada se conservan como referencia semilla, pero no se presentan como activos.",
        "Los duplicados deben resolverse antes de mapas operativos para evitar doble conteo.",
        "Las zonas o sedes a validar se tratan como alertas, no como evidencia cerrada.",
    ], M, y - 210, W - 2 * M, gap=8.5)
    note_box(c, M, 112, W - 2 * M, 78, "Uso recomendado",
             "Usar esta capa para priorizar validación con la contraparte y ajustar mapas de detalle. No presentarla como fuente oficial ni como validación definitiva.",
             color=AZUL, fill=SOFT_AZUL)
    finish(c)


def pending_page(c: canvas.Canvas) -> None:
    y = header(c, 14, "Decisiones pendientes", "Qué cerrar antes de la versión final")
    bullet_list(c, [
        "Validar con Ale el recorte de Corrientes y Abasto.",
        "Definir si los mapas finales muestran nombres de locales, solo puntos o zonas.",
        "Resolver sedes en duplicados y cadenas antes de cualquier mapa operativo.",
        "Revisar subzonas con menor evidencia explícita, especialmente Belgrano R y Abasto.",
        "Definir si las recomendaciones quedan en el cuerpo o se trasladan a anexos.",
    ], M, y - 10, W - 2 * M, gap=12)
    note_box(c, M, 140, W - 2 * M, 88, "Bloqueo principal",
             "La versión final depende de cerrar criterios de publicación territorial: delimitaciones, sedes, nombres visibles y tratamiento de zonas con evidencia menor.",
             color=ROJO, fill=SOFT_ROJO)
    finish(c)


def recommendations_page(c: canvas.Canvas) -> None:
    y = header(c, 15, "Recomendaciones prudentes", "Uso institucional de la pieza")
    note_box(c, M, y - 82, W - 2 * M, 64, "Mapa global",
             "Usarlo como lectura institucional del universo semilla, con nota clara de que no define límites oficiales.",
             color=AZUL2, fill=SOFT_AZUL)
    note_box(c, M, y - 164, W - 2 * M, 64, "Mapas de detalle",
             "Usarlos como apoyo para validación territorial. Evitar tratarlos como listado operativo hasta resolver sedes y duplicados.",
             color=VERDE, fill=SOFT_VERDE)
    note_box(c, M, y - 246, W - 2 * M, 64, "Nomenclatura",
             "Consolidar nombres de polos, subzonas y ejes para que la pieza sea consistente en mapas, texto y anexos.",
             color=NARANJA, fill=SOFT_NARANJA)
    bullet_list(c, [
        "Separar siempre hallazgos, límites y próximos pasos.",
        "Mantener la capa auxiliar como insumo de orientación, no como fuente oficial.",
        "Validar territorialmente antes de publicar detalle operativo.",
    ], M, 230, W - 2 * M, gap=10)
    finish(c)


def next_steps_page(c: canvas.Canvas) -> None:
    y = header(c, 16, "Próximos pasos", "Secuencia sugerida")
    steps = [
        ("1", "Validación con Ale", "Cerrar delimitaciones, sedes y criterios de publicación."),
        ("2", "Ajuste cartográfico", "Corregir mapas finales según decisiones de Corrientes, Abasto y Belgrano."),
        ("3", "Síntesis ejecutiva", "Preparar una versión más breve si el destino requiere lectura de conducción."),
        ("4", "Versión final", "Generar la pieza final después de cerrar decisiones territoriales y visuales."),
    ]
    y0 = y - 20
    for n, title, text in steps:
        set_fill(c, ROJO)
        c.circle(M + 12, y0 - 2, 11, fill=1, stroke=0)
        set_fill(c, "#FFFFFF")
        c.setFont(FONT_BOLD, 10)
        c.drawCentredString(M + 12, y0 - 6, n)
        set_fill(c, AZUL)
        c.setFont(FONT_BOLD, 10.8)
        c.drawString(M + 38, y0 + 3, title)
        draw_wrapped(c, text, M + 38, y0 - 15, W - 2 * M - 38, font=FONT, size=9.3, color=NEGRO, leading=11.5)
        y0 -= 88
    note_box(c, M, 112, W - 2 * M, 74, "Criterio de cierre",
             "La pieza final debe mantener el mismo estándar: marca DGDGAS, sin datos sensibles, sin rutas ni referencias técnicas y con cautelas visibles sobre alcance.",
             color=AZUL, fill=SOFT_AZUL)
    finish(c)


def annex_universe(c: canvas.Canvas) -> None:
    header(c, 17, "Anexo A", "Universo semilla de 22 polos/ejes")
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
    x, y = M, H - 136
    col_w = [214, 216, 74]
    row_h = 19
    set_fill(c, AZUL)
    c.rect(x, y, sum(col_w), row_h, fill=1, stroke=0)
    set_fill(c, "#FFFFFF")
    c.setFont(FONT_BOLD, 7.9)
    c.drawString(x + 6, y + 6, "Polo/eje")
    c.drawString(x + col_w[0] + 6, y + 6, "Tipo de lectura")
    c.drawRightString(x + sum(col_w) - 6, y + 6, "Menciones")
    y -= row_h
    c.setFont(FONT, 7.1)
    for idx, row in enumerate(rows):
        set_fill(c, "#FFFFFF" if idx % 2 == 0 else "#F7F9FB")
        c.rect(x, y, sum(col_w), row_h, fill=1, stroke=0)
        set_stroke(c, LINEA)
        c.rect(x, y, sum(col_w), row_h, fill=0, stroke=1)
        set_fill(c, NEGRO)
        c.drawString(x + 6, y + 6, row[0])
        c.drawString(x + col_w[0] + 6, y + 6, row[1])
        c.drawRightString(x + sum(col_w) - 6, y + 6, row[2])
        y -= row_h
    note_box(c, M, 88, W - 2 * M, 56, "Nota",
             "Los polos con cero menciones explícitas permanecen en el universo semilla y se representan en el mapa global como áreas o ejes a fortalecer.",
             color=AZUL2, fill=SOFT_AZUL, size=8.2)
    finish(c)


def annex_method(c: canvas.Canvas) -> None:
    y = header(c, 18, "Anexo B", "Criterio cartográfico y limitaciones")
    bullet_list(c, [
        "El mapa global representa áreas, macroáreas, ejes o zonas aproximadas del universo semilla.",
        "Los polos sin locales explícitos se muestran como parte del universo y requieren refuerzo documental.",
        "Los mapas de detalle usan puntos y símbolos como apoyo visual, no como validación oficial.",
        "Los casos con vigencia no confirmada, duplicados sin resolver y búsquedas a corregir quedan fuera de mapas operativos.",
        "Los hitos colectivos se tratan como referencia territorial, no como restaurante puntual.",
    ], M, y - 10, W - 2 * M, gap=9)
    note_box(c, M, 134, W - 2 * M, 86, "Lectura metodológica",
             "Ningún mapa define límites oficiales ni confirma actividad vigente. La cartografía acompaña una lectura institucional y debe ajustarse con validación territorial antes de circular como herramienta operativa.",
             color=NARANJA, fill=SOFT_NARANJA)
    finish(c)


def build_pdf(maps: dict[str, Path], mentions: list[dict[str, str]]) -> None:
    c = canvas.Canvas(str(PDF), pagesize=A4)
    c.setTitle(TITLE)
    c.setAuthor(INSTITUCION)
    cover(c)
    index_page(c)
    summary_page(c)
    scope_page(c)
    global_map_page(c, maps)
    territorial_page(c)
    for page in ["palermo", "puerto", "san_telmo", "corrientes", "belgrano"]:
        detail_page(c, page, maps, mentions)
    mentions_criteria_page(c, mentions)
    auxiliary_page(c)
    pending_page(c)
    recommendations_page(c)
    next_steps_page(c)
    annex_universe(c)
    annex_method(c)
    c.save()


def md_mentions(mentions: list[dict[str, str]], page: str) -> str:
    text = visible_mentions(mentions, page)
    return "\n".join(f"- {line}" for line in text.splitlines() if line.strip())


def build_markdown(mentions: list[dict[str, str]]) -> None:
    DOCS_OUT.mkdir(parents=True, exist_ok=True)
    content = f"""# Polos gastronómicos de la Ciudad de Buenos Aires

## Universo semilla, lectura territorial y capa auxiliar de geolocalización

**{INSTITUCION}**  
**{GOBIERNO}**  
Fecha de elaboración: julio de 2026

Este documento es la base editorial de la versión PDF con revisión visual. Ordena el universo semilla de 22 polos/ejes, mantiene el mapa global como pieza principal y refuerza las páginas de detalle con menciones destacadas del universo semilla. No constituye padrón oficial, ranking ni confirmación de actividad vigente.

## 1. Resumen ejecutivo

Se ordena un universo semilla de **22 polos/ejes gastronómicos** de la Ciudad y **106 menciones de locales** asociadas a ese universo. La capa auxiliar permite distinguir coincidencias razonables o fuertes, sedes a validar, casos con vigencia no confirmada, duplicados probables y búsquedas a corregir.

La mejora visual de esta versión se concentra en las páginas territoriales: mapas más limpios, puntos más legibles, cajas de menciones destacadas y notas de cautela visibles.

## 2. Alcance y criterio de lectura

El universo semilla es un insumo de trabajo. Las menciones destacadas no son ranking, no son recomendación comercial y no equivalen a padrón de locales activos.

La capa auxiliar aporta ubicación orientativa y alertas de calidad. No reemplaza fuentes oficiales ni validación territorial.

## 3. Mapa global de 22 polos/ejes

El mapa global se conserva como mapa principal. Representa áreas, ejes y zonas de lectura territorial del universo semilla, sin definir límites oficiales.

## 4. Lectura territorial general

Palermo concentra el mayor volumen de menciones. Puerto Madero y San Telmo permiten lecturas territoriales claras si se separan hitos colectivos, sedes a validar y menciones con mayor respaldo. Corrientes y Abasto se mantienen diferenciados para evitar doble conteo. Belgrano se presenta como macroárea con subzonas de respaldo desigual.

## 5. Detalles territoriales

### Palermo / Las Cañitas

{md_mentions(mentions, "palermo")}

Lectura: mayor volumen del universo semilla y subzonas internas visibles. No es ranking ni padrón oficial.

### Puerto Madero

{md_mentions(mentions, "puerto")}

Lectura: polo consolidado costero. Los hitos colectivos y sedes a validar deben diferenciarse de las menciones con mayor respaldo.

### San Telmo

{md_mentions(mentions, "san_telmo")}

Lectura: área patrimonial/gastronómica. El Mercado de San Telmo se trata como hito colectivo, no como restaurante puntual.

### Corrientes / Abasto

{md_mentions(mentions, "corrientes")}

Lectura: Corrientes es eje teatral-gastronómico 9 de Julio-Callao. Abasto se presenta como área a reforzar alrededor del shopping.

### Belgrano y subzonas

{md_mentions(mentions, "belgrano")}

Lectura: Barrio Chino tiene identidad gastronómica clara; Bajo Belgrano conserva sedes a validar; Belgrano R queda como subzona a reforzar.

## 6. Hallazgos de la capa auxiliar

- 59 coincidencias razonables o fuertes.
- 8 casos con vigencia no confirmada.
- 11 duplicados probables.
- 25 zonas o sedes a validar.
- 3 búsquedas a corregir.

Los casos cerrados, las búsquedas a corregir y los duplicados no se presentan como activos. Las sedes a validar se tratan como alertas, no como evidencia cerrada.

## 7. Decisiones pendientes

- Validar delimitaciones de Corrientes y Abasto.
- Resolver sedes en duplicados y cadenas antes de cualquier mapa operativo.
- Revisar tratamiento de Belgrano por subzonas.
- Definir nivel de exposición de nombres en mapas finales.

## 8. Recomendaciones prudentes

- Usar el mapa global como lectura institucional del universo semilla.
- Usar los mapas de detalle como apoyo visual, no como padrón operativo.
- Mantener separadas las menciones incluidas, las sedes a validar y los casos excluidos por prudencia.
- Validar territorialmente antes de publicar detalle operativo.

## 9. Próximos pasos

1. Revisar con Ale delimitaciones, sedes y criterios de publicación.
2. Ajustar mapas finales según definiciones territoriales.
3. Preparar una síntesis ejecutiva si el destino requiere lectura de conducción.
4. Generar la versión final después de cerrar decisiones.

## Anexos

La tabla de menciones destacadas se conserva como respaldo en el output de esta fase. Los casos excluidos no se listan en el cuerpo del PDF.
"""
    MD_BASE.write_text(content, encoding="utf-8")


def build_html(maps: dict[str, Path], mentions: list[dict[str, str]]) -> None:
    rel = {key: f"assets/{path.name}" for key, path in maps.items()}
    blocks = []
    for page in ["palermo", "puerto", "san_telmo", "corrientes", "belgrano"]:
        cfg = DETAIL_TEXT[page]
        blocks.append(
            f"<section><h2>{html.escape(cfg['title'])}</h2>"
            f"<img src='{html.escape(rel[page])}' alt='Mapa {html.escape(cfg['title'])}'>"
            f"<p>{html.escape(visible_mentions(mentions, page)).replace(chr(10), '<br>')}</p></section>"
        )
    body = "\n".join(blocks)
    HTML.write_text(f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <title>{html.escape(TITLE)}</title>
  <style>
    body {{ margin: 0; font-family: Arial, sans-serif; color: #222; background: #f4f6f8; }}
    header {{ background: {AZUL}; color: white; padding: 44px 64px 38px; border-bottom: 6px solid {ROJO}; }}
    header .brand {{ font-weight: 700; color: #cdd9e5; }}
    header h1 {{ margin: 38px 0 12px; font-size: 38px; max-width: 880px; line-height: 1.08; }}
    header p {{ margin: 0; font-size: 18px; color: #e9eef5; max-width: 920px; }}
    main {{ max-width: 1040px; margin: 32px auto 64px; padding: 0 24px; }}
    section {{ background: white; border: 1px solid #d9dee5; margin: 18px 0; padding: 28px; }}
    h2 {{ color: {AZUL}; margin: 0 0 14px; font-size: 24px; }}
    p {{ line-height: 1.55; }}
    img {{ width: 100%; height: auto; display: block; border: 1px solid #d9dee5; }}
  </style>
</head>
<body>
  <header>
    <div class="brand">{html.escape(INSTITUCION)} · {html.escape(GOBIERNO)}</div>
    <h1>{html.escape(TITLE)}</h1>
    <p>{html.escape(SUBTITLE)}</p>
  </header>
  <main>
    <section><h2>Mapa global</h2><img src="{html.escape(rel['global'])}" alt="Mapa global"></section>
    {body}
  </main>
</body>
</html>
""", encoding="utf-8")


def main() -> None:
    DOCS_OUT.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)
    register_fonts()
    mentions = build_mentions()
    maps = build_assets(mentions)
    build_markdown(mentions)
    build_pdf(maps, mentions)
    build_html(maps, mentions)
    print(PDF)
    print(MENTIONS_CSV)
    print(MD_BASE)


if __name__ == "__main__":
    main()
