"""Convierte el Markdown maestro editorial de mercados gastronomicos en un PDF
final disenado, estilo DataGastro / casas de pastas.

Fuente editorial unica:
    docs/mercados_caba/INFORME_FINAL_MERCADOS_GASTRONOMICOS_CABA_MARKDOWN_MASTER.md

No hace requests, no usa APIs, no cambia datos ni conteos. Toma el texto del
Markdown maestro, los CSV V4/V5 ya sanitizados y los visuales V5 existentes, y
arma un PDF de pocas paginas con buena densidad, sin cajas cortadas ni tablas
truncadas. Tambien genera un resumen ejecutivo y un pack entregable.

Layout via matplotlib PdfPages (mismo enfoque probado en V5.1). No toca
build_informe_final_v5_1.py ni los entregables V4/V5/V5.1.
"""
from __future__ import annotations

import argparse
import csv
import re
import shutil
import subprocess
import tempfile
import textwrap
import zipfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs" / "mercados_caba"
SAN = ROOT / "outputs" / "mercados_caba" / "sanitized"

MASTER_MD = DOCS / "INFORME_FINAL_MERCADOS_GASTRONOMICOS_CABA_MARKDOWN_MASTER.md"
NOTES_MD = DOCS / "NOTAS_CONVERSION_PDF_MERCADOS_VFINAL.md"

PDF = SAN / "INFORME_FINAL_MERCADOS_GASTRONOMICOS_CABA_FINAL.pdf"
PDF_RESUMEN = SAN / "RESUMEN_EJECUTIVO_MERCADOS_GASTRONOMICOS_CABA_FINAL.pdf"
PACK = SAN / "PACK_ENTREGABLE_MERCADOS_GASTRONOMICOS_CABA_FINAL.zip"
README = DOCS / "README_REGENERAR_INFORME_FINAL.md"

# Salidas V2: version visualmente corregida, sin sobrescribir el FINAL ni las
# versiones previas. Mismos datos y conteos; solo cambia maquetacion.
PDF_V2 = SAN / "INFORME_FINAL_MERCADOS_GASTRONOMICOS_CABA_FINAL_V2.pdf"
PDF_RESUMEN_V2 = SAN / "RESUMEN_EJECUTIVO_MERCADOS_GASTRONOMICOS_CABA_FINAL_V2.pdf"
PACK_V2 = SAN / "PACK_ENTREGABLE_MERCADOS_GASTRONOMICOS_CABA_FINAL_V2.zip"
README_V2 = DOCS / "README_REGENERAR_INFORME_FINAL_V2.md"
MAP_V2 = "mapa_sedes_fijas_mercados_gastronomicos_v5_2.png"

# Salidas V3: V2 intacta + una pagina nueva de lectura operativa de publicos.
PDF_V3 = SAN / "INFORME_FINAL_MERCADOS_GASTRONOMICOS_CABA_FINAL_V3.pdf"
PDF_RESUMEN_V3 = SAN / "RESUMEN_EJECUTIVO_MERCADOS_GASTRONOMICOS_CABA_FINAL_V3.pdf"
PACK_V3 = SAN / "PACK_ENTREGABLE_MERCADOS_GASTRONOMICOS_CABA_FINAL_V3.zip"
README_V3 = DOCS / "README_REGENERAR_INFORME_FINAL_V3.md"
PUBLICOS_CSV = SAN / "publicos_objetivo_mercados_vfinal.csv"
PUBLICOS_ANEXO_MD = DOCS / "ANEXO_PUBLICOS_OBJETIVO_ACTIVACION_TERRITORIAL.md"

A4 = (8.27, 11.69)
INK = "#1f3b57"
BLUE = "#2c7fb8"
ORANGE = "#c0762b"
RED = "#c0392b"
GREEN = "#1a9850"
GREY = "#555555"
LIGHT = "#eef2f6"
SOFT_ORANGE = "#f7ebdc"
SOFT_BLUE = "#eaf1f8"
WHITE = "#ffffff"
LINE = "#d9dee5"

# Limite inferior seguro: nada de contenido debajo de esta y (footer en 0.056).
FLOOR = 0.075

TYPE_LABEL = {
    "mercado_historico": "historico",
    "mercado_barrial_alimentario": "barrial alimentario",
    "food_hall": "food hall",
    "patio_gastronomico": "patio gastronomico",
    "mercado_de_productores": "mercado de productores",
    "feria_gastronomica": "feria gastronomica",
}

DECISION_CARDS = [
    ("Circuitos turisticos",
     "Articular los mercados de mayor atractivo turistico en recorridos integrados.",
     "San Telmo, Belgrano, Gourmand", BLUE),
    ("Productores y economia social",
     "Apoyar mercados y ferias de productores y consumo consciente.",
     "Bonpland, Sabe la Tierra, BA Market", GREEN),
    ("Patios publicos",
     "Usar los patios gastronomicos publicos como dinamizadores barriales.",
     "Lecheros, Smart Plaza, Costanera, Rodrigo Bueno", BLUE),
    ("Base candidata trazable",
     "Sostener un catalogo con tipologia y estado operativo, actualizable.",
     "Todos los activos identificados", ORANGE),
    ("Validacion territorial",
     "Ordenar la verificacion en terreno por respaldo documental.",
     "Empezar por respaldo medio o a validar", ORANGE),
    ("Informacion publica homogenea",
     "Publicar horarios, gestion y oferta de cada mercado de forma uniforme.",
     "Todos los activos identificados", BLUE),
]

PATRIMONIALES = [
    ("Mercado de San Telmo", "1897", "Icono turistico de la Ciudad.", ORANGE),
    ("Mercado de Belgrano", "1891", "Renovado con food court.", BLUE),
    ("Mercado del Progreso", "1889", "Sitio de interes cultural; clasico barrial de abasto.", GREEN),
    ("Mercado San Nicolas", "centenario", "Mercado renovado en Microcentro.", BLUE),
    ("Mercado Bonpland", "economia social", "Referente de consumo consciente.", GREEN),
]

NO_ACTIVOS = [
    ("Mercado Soho", "relevante no contabilizado",
     "Senales de cierre y falta de actividad reciente verificable.",
     "Vuelve al conteo si se valida actividad.", ORANGE),
    ("Mercat Caballito", "relevante no contabilizado",
     "Senales de cierre; en fuente oficial solo figura como mencion de evento.",
     "Requiere validacion antes de contar.", ORANGE),
    ("El Galpon", "relevante no contabilizado",
     "Situacion operativa no clara; match de Google inconsistente.",
     "Productores relevante; requiere validacion.", ORANGE),
    ("Mercado de los Carruajes", "cerrado documentado",
     "Cerro en abril de 2025 y se reconvierte a eventos.",
     "Antecedente relevante, no activo.", RED),
]

PUBLICOS_METODOLOGIA = (
    "Esta lectura de públicos constituye una aproximación operativa para orientar "
    "activaciones territoriales; no es una medición de afluencia ni una segmentación "
    "estadística, y requiere validación en terreno antes de programación operativa."
)

PUBLICOS_INSIGHTS = [
    ("Turístico / patrimonial",
     "San Telmo, Costanera Norte y Gourmand concentran mayor potencial para recorridos, "
     "paseo y consumo de experiencia.", ORANGE),
    ("Barrial / familiar",
     "Belgrano, Progreso, Lecheros y Buenos Aires Market muestran mejor encaje para "
     "activaciones de cercanía y hábito.", BLUE),
    ("Trabajadores / after office",
     "San Nicolas, Smart Plaza Parque Patricios y Mercat Villa Crespo permiten pensar "
     "franjas de almuerzo, post-trabajo y salida corta.", GREEN),
    ("Productores / consumo consciente",
     "Bonpland, Sabe la Tierra y Buenos Aires Market concentran la lógica de productores, "
     "economía social y consumo saludable.", GREEN),
    ("Comunitario / colectividades",
     "Rodrigo Bueno, Bonpland y Sabe la Tierra tienen potencial para activaciones de "
     "comunidad, colectividades y cocina cultural.", ORANGE),
]

PUBLICOS_COMPACT_MATRIX = [
    ["Turístico / patrimonial", "San Telmo, Costanera Norte, Gourmand",
     "recorridos, degustaciones, circuitos"],
    ["Barrial / familiar", "Belgrano, Progreso, Lecheros, Buenos Aires Market",
     "cercanía, hábito, fines de semana"],
    ["Trabajadores / after office", "San Nicolas, Smart Plaza, Mercat Villa Crespo",
     "almuerzo, after office, entre semana"],
    ["Productores / consumo consciente", "Bonpland, Sabe la Tierra, Buenos Aires Market",
     "ferias, talleres, consumo responsable"],
    ["Comunitario / colectividades", "Rodrigo Bueno, Bonpland, Sabe la Tierra",
     "cocina cultural, colectividades, identidad"],
]

PUBLICOS_FULL_MATRIX = [
    {
        "mercado": "Mercado de San Telmo",
        "perfil_principal": "Turistico / patrimonial",
        "perfil_secundario": "Barrial / paseo",
        "momento_recomendado": "Fines de semana, recorridos turisticos y franjas de paseo",
        "activacion_recomendada": "Recorridos patrimoniales, degustaciones y circuitos gastronomicos",
        "evidencia_principal": "GCBA Descubrir BA, Turismo BA y sitio propio del mercado",
        "tipo_evidencia": "oficial_gcba_turismo_sitio_propio",
        "nivel_confianza": "alto_documental",
        "urls_clave": "http://buenosaires.gob.ar/Descubrir%20BA/mercado-de-san-telmo; https://turismo.buenosaires.gob.ar/en/otros-establecimientos/san-telmo-market; https://www.mercadosantelmo.com.ar/",
    },
    {
        "mercado": "Mercado de Belgrano",
        "perfil_principal": "Barrial / familiar",
        "perfil_secundario": "Turistico / patrimonial",
        "momento_recomendado": "Compras de cercania, fines de semana y agenda familiar",
        "activacion_recomendada": "Degustaciones, talleres cortos y agenda barrial",
        "evidencia_principal": "GCBA Descubrir BA y respaldo documental multifuente",
        "tipo_evidencia": "oficial_gcba_prensa",
        "nivel_confianza": "alto_documental",
        "urls_clave": "https://buenosaires.gob.ar/Descubrir%20BA/mercado-de-belgrano; https://www.infogastronomica.com.ar/mercado-de-belgrano-historia-locales-y-mas/",
    },
    {
        "mercado": "Mercado del Progreso",
        "perfil_principal": "Barrial / familiar",
        "perfil_secundario": "Patrimonial / abasto",
        "momento_recomendado": "Compras de cercania, mediodia y fines de semana",
        "activacion_recomendada": "Activaciones de habito, cocina de mercado y recorridos barriales",
        "evidencia_principal": "Sitio propio del mercado y Turismo BA",
        "tipo_evidencia": "sitio_propio_oficial_turismo",
        "nivel_confianza": "alto_documental",
        "urls_clave": "https://mercadodelprogreso.com/; https://turismo.buenosaires.gob.ar/es/otros-establecimientos/mercado-del-progreso",
    },
    {
        "mercado": "Mercat Villa Crespo",
        "perfil_principal": "Trabajadores / after office",
        "perfil_secundario": "Mixto barrial / turistico medio",
        "momento_recomendado": "Almuerzo, tarde-noche y salida corta entre semana",
        "activacion_recomendada": "After office, menus de mediodia y experiencias de food hall",
        "evidencia_principal": "Turismo BA y respaldo documental multifuente",
        "tipo_evidencia": "oficial_turismo_multifuente",
        "nivel_confianza": "alto_documental",
        "urls_clave": "https://turismo.buenosaires.gob.ar/es/otros-establecimientos/mercat-villa-crespo",
    },
    {
        "mercado": "Patio de los Lecheros",
        "perfil_principal": "Barrial / familiar",
        "perfil_secundario": "Turistico / barrial",
        "momento_recomendado": "Tardes, fines de semana y agenda familiar",
        "activacion_recomendada": "Propuestas familiares, ferias de cercania y eventos barriales",
        "evidencia_principal": "Buenos Aires Ciudad y nota institucional de aniversario",
        "tipo_evidencia": "oficial_gcba",
        "nivel_confianza": "alto_documental",
        "urls_clave": "https://buenosaires.gob.ar/patio-de-los-lecheros; https://buenosaires.gob.ar/gcaba_historico/desarrolloeconomico/gastronomia/noticias/el-patio-de-los-lecheros-cumple-5-anos",
    },
    {
        "mercado": "Mercado Bonpland",
        "perfil_principal": "Productores / consumo consciente",
        "perfil_secundario": "Comunitario / economia social",
        "momento_recomendado": "Fines de semana y agenda de productores",
        "activacion_recomendada": "Talleres, consumo responsable, economia social y cocina cultural",
        "evidencia_principal": "Argentina.gob.ar, Turismo BA y respaldo interno sanitizado",
        "tipo_evidencia": "oficial_nacion_oficial_turismo_fuente_sanitizada",
        "nivel_confianza": "alto_documental",
        "urls_clave": "https://www.argentina.gob.ar/desarrollosocial/cronicasdeldesarrollo/mercado-bonpland-economia-solidaria-en-las-calles-de-palermo; https://turismo.buenosaires.gob.ar/es/otros-establecimientos/mercado-bonpland",
    },
    {
        "mercado": "Smart Plaza Parque Patricios",
        "perfil_principal": "Trabajadores / almuerzo / after office",
        "perfil_secundario": "Barrial / familiar",
        "momento_recomendado": "Almuerzo, tarde y salida corta post-trabajo",
        "activacion_recomendada": "Almuerzos, actividades en plaza y activaciones de cercania",
        "evidencia_principal": "Buenos Aires Ciudad y Turismo BA",
        "tipo_evidencia": "oficial_gcba_turismo",
        "nivel_confianza": "alto_documental",
        "urls_clave": "https://buenosaires.gob.ar/smart-plaza-patio-parque-patricios; https://turismo.buenosaires.gob.ar/es/otros-establecimientos/smart-plaza-patio-parque-patricios",
    },
    {
        "mercado": "Patio Costanera Norte",
        "perfil_principal": "Turistico / patrimonial",
        "perfil_secundario": "Paseo de ribera",
        "momento_recomendado": "Fines de semana, atardecer y franjas de paseo",
        "activacion_recomendada": "Circuitos de ribera, degustaciones y propuestas de experiencia",
        "evidencia_principal": "GCBA Desarrollo Economico y Turismo BA",
        "tipo_evidencia": "oficial_gcba_turismo",
        "nivel_confianza": "medio_documental",
        "urls_clave": "http://buenosaires.gob.ar/desarrolloeconomico/gastronomia/patio-costanera-norte; https://turismo.buenosaires.gob.ar/es/otros-establecimientos/patio-costanera-norte",
    },
    {
        "mercado": "Patio Gastronomico Rodrigo Bueno",
        "perfil_principal": "Comunitario / colectividades",
        "perfil_secundario": "Barrial / familiar",
        "momento_recomendado": "Fines de semana, visitas de paseo y agenda comunitaria",
        "activacion_recomendada": "Cocina cultural, identidad barrial y activaciones de comunidad",
        "evidencia_principal": "GCBA Desarrollo Economico e Instituto de Vivienda",
        "tipo_evidencia": "oficial_gcba_institucional",
        "nivel_confianza": "alto_documental",
        "urls_clave": "https://buenosaires.gob.ar/desarrolloeconomico/gastronomia/patio-rodrigo-bueno; https://vivienda.buenosaires.gob.ar/patio_gastronomico_rodrigo_bueno",
    },
    {
        "mercado": "Mercado San Nicolas",
        "perfil_principal": "Trabajadores / almuerzo / after office",
        "perfil_secundario": "Turistico / patrimonial",
        "momento_recomendado": "Almuerzo de Microcentro, post-trabajo y recorridos de centro",
        "activacion_recomendada": "Menus de mediodia, after office y recorridos gastronomicos del centro",
        "evidencia_principal": "Turismo BA, GCBA y respaldo interno sanitizado",
        "tipo_evidencia": "oficial_turismo_gcba_fuente_sanitizada",
        "nivel_confianza": "alto_documental",
        "urls_clave": "https://turismo.buenosaires.gob.ar/es/otros-establecimientos/mercado-de-san-nicolas; http://buenosaires.gob.ar/desarrolloeconomico/gastronomia/mercado-san-nicolas; https://buenosaires.gob.ar/noticias/reinauguro-el-mercado-san-nicolas",
    },
    {
        "mercado": "Buenos Aires Market",
        "perfil_principal": "Productores / consumo consciente",
        "perfil_secundario": "Barrial / familiar",
        "momento_recomendado": "Itinerante de fin de semana, segun sede programada",
        "activacion_recomendada": "Ferias saludables, productores, talleres y consumo responsable",
        "evidencia_principal": "Sitio propio y comunicacion GCBA sobre ferias itinerantes",
        "tipo_evidencia": "sitio_propio_oficial_gcba",
        "nivel_confianza": "alto_documental",
        "urls_clave": "https://www.buenosairesmarket.com/; https://buenosaires.gob.ar/noticias/donde-encontrar-las-ferias-ba-market-y-sabe-la-tierra",
    },
    {
        "mercado": "Sabe la Tierra",
        "perfil_principal": "Productores / consumo consciente",
        "perfil_secundario": "Comunitario / barrial",
        "momento_recomendado": "Itinerante de fin de semana y agenda saludable",
        "activacion_recomendada": "Productores sustentables, talleres, cocina saludable y comunidad",
        "evidencia_principal": "Sitio propio, GCBA y respaldo documental multifuente",
        "tipo_evidencia": "sitio_propio_oficial_gcba",
        "nivel_confianza": "alto_documental",
        "urls_clave": "https://sabelatierra.org/; https://buenosaires.gob.ar/gcaba_historico/sabe-la-tierra; https://buenosaires.gob.ar/noticias/donde-encontrar-las-ferias-ba-market-y-sabe-la-tierra",
    },
    {
        "mercado": "Gourmand Food Hall",
        "perfil_principal": "Turistico / patrimonial",
        "perfil_secundario": "Trabajadores / salida corta",
        "momento_recomendado": "Paseo en Retiro, almuerzo y after office",
        "activacion_recomendada": "Consumo de experiencia, degustaciones y recorridos gastronomicos",
        "evidencia_principal": "Sitio propio y validacion documental multifuente",
        "tipo_evidencia": "sitio_propio_documental_multifuente",
        "nivel_confianza": "alto_documental",
        "urls_clave": "https://gourmandfoodhall.com/",
    },
]


# --------------------------------------------------------------------------- #
# Lectura de insumos
# --------------------------------------------------------------------------- #
def read_csv(name: str) -> list[dict[str, str]]:
    with (SAN / name).open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def load_master_meta() -> dict[str, str]:
    """Lee del Markdown maestro la fecha y el headline, para no inventarlos."""
    text = MASTER_MD.read_text(encoding="utf-8")
    meta = {"fecha": "2026-06-24"}
    m = re.search(r"Diego Aleman.*?(\d{4}-\d{2}-\d{2})", text)
    if m:
        meta["fecha"] = m.group(1)
    return meta


# --------------------------------------------------------------------------- #
# Helpers de layout (estilo DataGastro)
# --------------------------------------------------------------------------- #
def page() -> plt.Figure:
    fig = plt.figure(figsize=A4)
    fig.patch.set_facecolor(WHITE)
    return fig


def footer(fig: plt.Figure, note: str = "") -> None:
    fig.lines.append(Line2D([0.07, 0.93], [0.056, 0.056], transform=fig.transFigure,
                            color="#dddddd", lw=0.8))
    fig.text(0.07, 0.036, "DataGastro · Mercados gastronómicos de CABA · Informe final",
             color=GREY, fontsize=7.8)
    if note:
        fig.text(0.93, 0.036, note, color=GREY, fontsize=7.5, ha="right")


def header(fig: plt.Figure, page_no: int, title: str, subtitle: str = "",
           kicker: str = "DataGastro | Mercados CABA") -> float:
    fig.text(0.07, 0.957, kicker, color=RED, fontsize=8.3, fontweight="bold")
    fig.text(0.93, 0.957, f"Pág. {page_no}", color=GREY, fontsize=8.3, ha="right")
    lines = textwrap.wrap(title, 43)
    for i, line in enumerate(lines):
        fig.text(0.07, 0.925 - i * 0.030, line, color=INK, fontsize=16.5,
                 fontweight="bold", va="top")
    y = 0.925 - len(lines) * 0.030
    fig.lines.append(Line2D([0.07, 0.35], [y + 0.004, y + 0.004],
                            transform=fig.transFigure, color=RED, lw=2.2))
    if subtitle:
        for i, line in enumerate(textwrap.wrap(subtitle, 92)):
            fig.text(0.07, y - 0.014 - i * 0.020, line, color=GREY, fontsize=9.5,
                     style="italic", va="top")
        y -= 0.014 + len(textwrap.wrap(subtitle, 92)) * 0.020
    return y - 0.018


def kpi_cards(fig: plt.Figure, y: float, items: list[tuple[str, str, str]],
              h: float = 0.115) -> None:
    width = 0.86 / len(items)
    for i, (num, lab, col) in enumerate(items):
        x = 0.07 + width * i
        fig.patches.append(Rectangle((x + 0.006, y), width - 0.012, h,
                                     transform=fig.transFigure, facecolor=LIGHT,
                                     edgecolor=col, lw=1.5))
        fig.text(x + width / 2, y + h * 0.60, num, color=col, ha="center",
                 va="center", fontsize=19, fontweight="bold")
        fig.text(x + width / 2, y + h * 0.24, lab, color=GREY, ha="center",
                 va="center", fontsize=8.0)


def box(fig: plt.Figure, x: float, y: float, w: float, h: float, title: str,
        text: str, kind: str = "resp") -> None:
    color = BLUE if kind == "resp" else ORANGE
    bg = SOFT_BLUE if kind == "resp" else SOFT_ORANGE
    fig.patches.append(Rectangle((x, y), w, h, transform=fig.transFigure,
                                 facecolor=bg, edgecolor=color, lw=1.1))
    fig.patches.append(Rectangle((x, y), 0.012, h, transform=fig.transFigure,
                                 facecolor=color, edgecolor=color))
    fig.text(x + 0.025, y + h - 0.024, title, color=color, fontsize=9.2,
             fontweight="bold", va="top")
    wrap = 86 if w > 0.78 else (60 if w > 0.55 else 39)
    lines = textwrap.wrap(text, wrap)
    for i, line in enumerate(lines[:8]):
        ytxt = y + h - 0.050 - i * 0.018
        if ytxt < y + 0.006:  # no escribir fuera de la caja
            break
        fig.text(x + 0.025, ytxt, line, color="#222222", fontsize=8.7, va="top")


def image(fig: plt.Figure, path: str, rect: list[float]) -> None:
    ax = fig.add_axes(rect)
    ax.imshow(plt.imread(SAN / path))
    ax.axis("off")


def image_fit(fig: plt.Figure, path: str, x: float, top: float, w: float) -> float:
    """Coloca una imagen anclada por su borde superior, calculando la altura del
    axes a partir del aspect real del PNG. Evita el aire vacío que deja imshow al
    centrar una imagen ancha dentro de un axes alto. Devuelve la y del borde
    inferior (en fraccion de figura) para encadenar contenido debajo.

    La conversion usa la relacion de aspecto fisico de A4 (ancho/alto en pulgadas)
    para que el axes mantenga la proporcion de pixeles de la imagen.
    """
    img = plt.imread(SAN / path)
    px_h, px_w = img.shape[0], img.shape[1]
    aspect_px = px_w / px_h
    fig_w_in, fig_h_in = A4
    # alto_frac = ancho_frac * (fig_w/fig_h) / aspect_px
    h = w * (fig_w_in / fig_h_in) / aspect_px
    bottom = top - h
    ax = fig.add_axes([x, bottom, w, h])
    ax.imshow(img)
    ax.axis("off")
    return bottom


def table(fig: plt.Figure, rect: list[float], data: list[list[str]],
          col_labels: list[str], font: float = 7.0, yscale: float = 1.2,
          col_widths: list[float] | None = None) -> None:
    ax = fig.add_axes(rect)
    ax.axis("off")
    tbl = ax.table(cellText=data, colLabels=col_labels, loc="upper left",
                   cellLoc="left", colWidths=col_widths)
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(font)
    tbl.scale(1, yscale)
    for (r, _c), cell in tbl.get_celld().items():
        cell.set_edgecolor(LINE)
        cell.set_linewidth(0.5)
        if r == 0:
            cell.set_facecolor(INK)
            cell.set_text_props(color=WHITE, fontweight="bold")
        else:
            cell.set_facecolor(WHITE if r % 2 else "#f7f9fb")


def bullet_column(fig: plt.Figure, x: float, y: float, items: list[str],
                  wrap: int = 48, size: float = 9.2, gap: float = 0.050) -> float:
    yy = y
    for item in items:
        lines = textwrap.wrap(item, wrap)
        fig.text(x, yy, "•", color=RED, fontsize=size, va="top")
        for j, line in enumerate(lines):
            fig.text(x + 0.020, yy - j * 0.019, line, color="#222222", fontsize=size, va="top")
        yy -= gap + max(0, len(lines) - 1) * 0.019
    return yy


def info_card(fig: plt.Figure, x: float, y: float, w: float, h: float, title: str,
              rows: list[tuple[str, str]], accent: str = BLUE,
              title_size: float = 8.6, body_size: float = 7.8) -> None:
    """Card con barra de titulo y filas etiqueta/valor.

    El ancho de wrap se calcula del ancho real de la card para que el texto
    nunca se salga del borde ni pise la card vecina. El titulo se ajusta a dos
    lineas dentro de la barra de color si hace falta.
    """
    # Ancho util interno y caracteres por linea calibrados (mas conservador que
    # la version previa, que dejaba que el texto desbordara la card).
    pad = 0.014
    inner_w = w - 2 * pad
    # ~0.0058 de figura por caracter a 7.8pt: estimacion conservadora.
    chars_body = max(14, int(inner_w / 0.0058))
    chars_title = max(12, int(inner_w / 0.0066))

    title_lines = textwrap.wrap(title, chars_title)[:2]
    bar_h = 0.030 if len(title_lines) <= 1 else 0.046

    fig.patches.append(Rectangle((x, y), w, h, transform=fig.transFigure,
                                 facecolor=WHITE, edgecolor=LINE, lw=1.0))
    fig.patches.append(Rectangle((x, y + h - bar_h), w, bar_h, transform=fig.transFigure,
                                 facecolor=accent, edgecolor=accent))
    for j, line in enumerate(title_lines):
        fig.text(x + pad, y + h - 0.010 - j * 0.016, line, color=WHITE,
                 fontsize=title_size, fontweight="bold", va="top")

    yy = y + h - bar_h - 0.018
    for label, value in rows:
        fig.text(x + pad, yy, label, color=accent, fontsize=body_size - 0.4,
                 fontweight="bold", va="top")
        wrapped = textwrap.wrap(value, chars_body)
        for j, line in enumerate(wrapped):
            fig.text(x + pad, yy - 0.014 - j * 0.0150, line, color="#222222",
                     fontsize=body_size, va="top")
        yy -= 0.030 + len(wrapped) * 0.0150


# --------------------------------------------------------------------------- #
# Portada
# --------------------------------------------------------------------------- #
def cover(pdf: PdfPages, meta: dict[str, str], resumen: bool = False) -> None:
    fig = page()
    fig.patches.append(Rectangle((0, 0.74), 1, 0.26, transform=fig.transFigure,
                                 facecolor=INK, edgecolor=INK))
    fig.patches.append(Rectangle((0.07, 0.69), 0.22, 0.018, transform=fig.transFigure,
                                 facecolor=ORANGE, edgecolor=ORANGE))
    fig.text(0.07, 0.91, "DataGastro", color=WHITE, fontsize=15, fontweight="bold")
    # Titulo partido en dos lineas: nunca se corta horizontalmente.
    fig.text(0.07, 0.855, "Mercados gastronómicos en la Ciudad", color=WHITE,
             fontsize=20.5, fontweight="bold")
    fig.text(0.07, 0.815, "de Buenos Aires", color=WHITE, fontsize=20.5, fontweight="bold")
    fig.text(0.07, 0.775, "Universo activo identificado · sedes fijas e itinerancia",
             color="#d9e6f2", fontsize=12.0)
    fig.text(0.07, 0.63, "Análisis y desarrollo: Diego Aleman", color=INK,
             fontsize=11.5, fontweight="bold")
    fig.text(0.07, 0.595, f"Informe final · {meta['fecha']}", color=GREY, fontsize=10)
    bajada = (
        "Relevamiento documental y multifuente para orientar validaciones territoriales "
        "y decisiones de política pública. Base candidata trazable; no es censo ni padrón oficial."
    )
    for i, line in enumerate(textwrap.wrap(bajada, 80)):
        fig.text(0.07, 0.515 - i * 0.028, line, color="#222222", fontsize=13, va="top")
    kpi_cards(fig, 0.275, [
        ("13", "mercados activos\nidentificados", ORANGE),
        ("11", "sedes fijas", BLUE),
        ("2", "itinerantes", GREEN),
    ])
    fig.text(0.07, 0.14, "No constituye censo ni padrón oficial. Requiere validación territorial "
             "para decisiones operativas.", color=GREY, fontsize=9.5)
    if resumen:
        fig.text(0.07, 0.105, "Resumen ejecutivo", color=RED, fontsize=10, fontweight="bold")
    footer(fig, "No constituye padrón oficial")
    pdf.savefig(fig)
    plt.close(fig)


# --------------------------------------------------------------------------- #
# PDF principal (10 paginas)
# --------------------------------------------------------------------------- #
def build_pdf(meta: dict[str, str]) -> None:
    active = read_csv("mercados_gastronomicos_activos_v4.csv")
    respaldo = read_csv("respaldo_fuentes_mercados_v4.csv")

    with PdfPages(PDF) as pdf:
        # --- Pagina 1: portada ---
        cover(pdf, meta)

        # --- Pagina 2: resumen ejecutivo + indicadores ---
        fig = page()
        header(fig, 2, "Resumen ejecutivo e indicadores clave",
               "13 activos identificados; 11 con sede fija y 2 itinerantes, en 6 comunas.")
        kpi_cards(fig, 0.735, [
            ("13", "activos\nidentificados", ORANGE),
            ("11", "sedes fijas", BLUE),
            ("2", "itinerantes", GREEN),
            ("6", "comunas", BLUE),
            ("13", "multifuente", ORANGE),
            ("12", "respaldo alto", GREEN),
        ], h=0.105)
        bullet_column(fig, 0.08, 0.640, [
            "La Ciudad cuenta con 13 mercados gastronómicos activos identificados: 11 con sede fija y 2 itinerantes.",
            "Los 13 son multifuente; 12 alcanzan respaldo documental alto y 1 medio.",
            "Conviven gestión pública (3), privada (5) y mixta (5) en seis comunas.",
            "Se documentan, aparte, 3 espacios relevantes no contabilizados y 1 cerrado documentado.",
        ], wrap=84, gap=0.052)
        box(fig, 0.07, 0.300, 0.86, 0.11, "Cuidado metodológico",
            "\"Activos identificados\" significa respaldo documental cruzado, no validación territorial "
            "confirmada en terreno. Es respaldo documental, no padrón oficial.", "cuid")
        box(fig, 0.07, 0.150, 0.86, 0.115, "Cómo se leyó el universo",
            "El relevamiento integra fuentes públicas oficiales, sitios propios, fuentes internas "
            "sanitizadas, Google Places como señal auxiliar no oficial y revisión documental complementaria.")
        footer(fig, "Base candidata no oficial")
        pdf.savefig(fig); plt.close(fig)

        # --- Pagina 3: universo y respaldo multifuente ---
        fig = page()
        header(fig, 3, "Cómo se construyó el universo identificado",
               "Cruce documental y multifuente, explicado sin sobreprometer.")
        image(fig, "grafico_respaldo_fuentes_v5.png", [0.08, 0.49, 0.84, 0.33])
        box(fig, 0.07, 0.315, 0.41, 0.135, "Lectura ejecutiva",
            "La fortaleza no está en una única fuente, sino en la convergencia entre fuentes "
            "públicas, sitios propios, señal operativa no oficial y revisión documental.")
        box(fig, 0.52, 0.315, 0.41, 0.135, "Cuidado metodológico",
            "Google Places se trata como señal auxiliar no oficial: no reemplaza una fuente "
            "administrativa ni una validación territorial.", "cuid")
        data = [[r["nombre"], r["cantidad_tipos_fuente"],
                 r["nivel_respaldo_documental"].replace("_", " ")] for r in respaldo[:6]]
        table(fig, [0.08, 0.105, 0.84, 0.17], data,
              ["Ejemplos", "Tipos de fuente", "Respaldo"], 7.1, 1.30)
        footer(fig, "Google es señal auxiliar no oficial")
        pdf.savefig(fig); plt.close(fig)

        # --- Pagina 4: mapa territorial ---
        fig = page()
        header(fig, 4, "Dónde están: sedes fijas e itinerancia",
               "Mapa principal de las 11 sedes fijas, sobre geometría local de barrios y comunas.")
        image(fig, "mapa_sedes_fijas_mercados_gastronomicos_v5.png", [0.055, 0.30, 0.89, 0.55])
        image(fig, "visual_itinerantes_mercados_gastronomicos_v5.png", [0.10, 0.155, 0.80, 0.13])
        box(fig, 0.07, 0.078, 0.86, 0.062, "Nota metodológica",
            "El mapa muestra solo mercados con sede fija. Los itinerantes —Buenos Aires Market y "
            "Sabe la Tierra— no se georreferencian como punto permanente: operan con sedes variables.",
            "cuid")
        footer(fig, "Puntos aproximados para lectura territorial")
        pdf.savefig(fig); plt.close(fig)

        # --- Pagina 5: tipologias + gestion ---
        fig = page()
        header(fig, 5, "Tipologías y gestión",
               "Tipología primaria única (suma 13 sin doble conteo) y modelos de gestión.")
        image(fig, "grafico_tipo_primario_v5.png", [0.05, 0.50, 0.45, 0.33])
        image(fig, "grafico_gestion_v5.png", [0.52, 0.50, 0.43, 0.33])
        box(fig, 0.07, 0.300, 0.86, 0.115, "Lectura ejecutiva",
            "Patios gastronómicos (4) y mercados históricos (3) concentran el núcleo; food halls (2) "
            "y mercados de productores (2) completan, con un barrial alimentario y una feria gastronómica. "
            "La gestión combina iniciativa privada (5), esquemas mixtos (5) y gestión pública (3).")
        box(fig, 0.07, 0.150, 0.86, 0.115, "Cuidado metodológico",
            "Cada mercado tiene un tipo primario único, de modo que las categorías suman exactamente 13. "
            "\"Itinerante\" y \"perfil de productores\" se tratan como atributos, no como tipología adicional.",
            "cuid")
        footer(fig, "Tipo primario único por mercado")
        pdf.savefig(fig); plt.close(fig)

        # --- Pagina 6: horarios + publicos ---
        fig = page()
        header(fig, 6, "Horarios y públicos objetivo",
               "Frecuencia de apertura y perfiles de público, como lectura orientativa.")
        image(fig, "grafico_horarios_v5.png", [0.05, 0.50, 0.45, 0.33])
        image(fig, "grafico_publicos_objetivo_v5.png", [0.52, 0.50, 0.43, 0.33])
        box(fig, 0.07, 0.300, 0.86, 0.115, "Lectura ejecutiva",
            "Conviven mercados de operación diaria o casi diaria, de días específicos e itinerantes de "
            "fin de semana. 11 de 13 tienen horario documentado. Predominan los perfiles barrial y "
            "turístico/barrial, con un núcleo de consumo consciente.")
        box(fig, 0.07, 0.150, 0.86, 0.115, "Cuidado metodológico",
            "Los horarios son autodeclarados y a veces divergentes; San Telmo presenta fuentes "
            "divergentes y los itinerantes dependen de la sede. El perfil de público es una lectura "
            "cualitativa, no una medición de afluencia.", "cuid")
        footer(fig, "Horarios documentales; pueden cambiar")
        pdf.savefig(fig); plt.close(fig)

        # --- Pagina 7: patrimoniales + no contabilizados (cards) ---
        fig = page()
        header(fig, 7, "Casos patrimoniales y espacios no contabilizados",
               "Identidad histórica documentada y casos fuera del conteo activo, sin tablas anchas.")
        fig.text(0.07, 0.838, "Casos patrimoniales y emblemáticos", color=INK,
                 fontsize=10.5, fontweight="bold")
        pat_pos = [(0.07, 0.690), (0.265, 0.690), (0.46, 0.690), (0.655, 0.690)]
        for pos, (nombre, anio, lectura, accent) in zip(pat_pos, PATRIMONIALES[:4]):
            info_card(fig, pos[0], pos[1], 0.185, 0.125, nombre,
                      [(anio, lectura)], accent)
        fig.text(0.07, 0.560, "Espacios relevantes no contabilizados y cerrados",
                 color=INK, fontsize=10.5, fontweight="bold")
        nc_pos = [(0.07, 0.350), (0.305, 0.350), (0.54, 0.350), (0.775, 0.350)]
        for pos, (nombre, estado, motivo, lectura, accent) in zip(nc_pos, NO_ACTIVOS):
            info_card(fig, pos[0], pos[1], 0.155, 0.190, nombre, [
                ("Estado", estado),
                ("Motivo", motivo),
                ("Lectura", lectura),
            ], accent)
        box(fig, 0.07, 0.150, 0.86, 0.16, "Cuidado metodológico",
            "No son errores ni descartes definitivos: se documentan como categorías diferenciadas. "
            "Los relevantes no contabilizados vuelven al conteo si se valida actividad vigente. "
            "Quedan, además, fuera de alcance distritos comerciales, abasto barrial, pulgas y outlet, "
            "por no ser mercados gastronómicos únicos.", "cuid")
        footer(fig, "No mezclar activos con casos en revisión")
        pdf.savefig(fig); plt.close(fig)

        # --- Pagina 8: decisiones de gestion (6 cards) ---
        fig = page()
        header(fig, 8, "Qué decisión permite tomar este informe",
               "Seis líneas de acción concretas, en cards ejecutivas.")
        dec_pos = [(0.07, 0.560), (0.365, 0.560), (0.66, 0.560),
                   (0.07, 0.300), (0.365, 0.300), (0.66, 0.300)]
        for pos, (title, uso, ejemplo, accent) in zip(dec_pos, DECISION_CARDS):
            info_card(fig, pos[0], pos[1], 0.265, 0.215, title, [
                ("Uso", uso),
                ("Aplica a", ejemplo),
            ], accent)
        box(fig, 0.07, 0.150, 0.86, 0.11, "Cierre ejecutivo",
            "El informe funciona como herramienta de gestión: muestra dónde mirar, qué validar y qué no "
            "mezclar. Las decisiones que afectan el estado operativo de un caso en revisión requieren "
            "validación territorial previa.")
        footer(fig, "Base candidata trazable")
        pdf.savefig(fig); plt.close(fig)

        # --- Pagina 9: tabla final compacta ---
        fig = page()
        header(fig, 9, "Tabla final de mercados activos identificados",
               "13 activos (11 sede fija + 2 itinerantes), en formato compacto y legible.")
        rows = []
        for r in active:
            comuna = r["comuna"] if r["comuna"] != "0" else "itin."
            rows.append([
                r["nombre"].replace("Patio Gastronomico", "Patio"),
                TYPE_LABEL.get(r["tipo_primario"], r["tipo_primario"]),
                r["gestion"],
                f"{r['barrio']} / {comuna}",
                "itinerante" if r["es_itinerante"] == "si" else "sede fija",
                r["nivel_respaldo_documental"].replace("_documental", ""),
            ])
        table(fig, [0.045, 0.165, 0.91, 0.66], rows,
              ["Nombre", "Tipo", "Gestión", "Barrio / comuna", "Sede", "Respaldo"], 6.3, 1.16)
        fig.text(0.07, 0.135, "Suma exacta: 13 activos identificados (11 de sede fija + 2 itinerantes).",
                 color=GREY, fontsize=8.5, style="italic")
        footer(fig, "Tabla compacta")
        pdf.savefig(fig); plt.close(fig)

        # --- Pagina 10: limitaciones + proximos pasos + cierre ---
        fig = page()
        header(fig, 10, "Limitaciones, próximos pasos y cierre",
               "Cierre separado para evitar cajas cortadas al pie.")
        box(fig, 0.07, 0.640, 0.86, 0.155, "Limitaciones",
            "Relevamiento documental y multifuente. No reemplaza la validación territorial ni el "
            "registro oficial. Google Places es señal auxiliar no oficial. Horarios autodeclarados y "
            "a veces divergentes. Coordenadas aproximadas por barrio. El respaldo documental alto o "
            "medio no equivale a confianza territorial.", "cuid")
        fig.text(0.07, 0.600, "Próximos pasos", color=INK, fontsize=10.5, fontweight="bold")
        bullet_column(fig, 0.085, 0.560, [
            "Validar en terreno los casos de respaldo medio o a validar.",
            "Monitorear los espacios con señales de cierre (Soho, Mercat Caballito, El Galpón).",
            "Homogeneizar la información pública de horarios, gestión y oferta.",
            "Mantener la base candidata como insumo actualizable, no como total definitivo.",
        ], wrap=84, gap=0.048)
        box(fig, 0.07, 0.155, 0.86, 0.155, "Qué aporta DataGastro",
            "Un método replicable —registro oficial, sitios propios, señal operativa, fuente interna "
            "y revisión documental— para construir una base candidata trazable, distinguir tipologías "
            "y separar con claridad activos identificados, casos en revisión, cerrados y fuera de "
            "alcance. Es una base candidata, no oficial.")
        footer(fig, "No es censo ni padrón oficial")
        pdf.savefig(fig); plt.close(fig)

    print(f"ok: {PDF}")


# --------------------------------------------------------------------------- #
# Resumen ejecutivo (2 paginas)
# --------------------------------------------------------------------------- #
def build_summary_pdf(meta: dict[str, str]) -> None:
    with PdfPages(PDF_RESUMEN) as pdf:
        cover(pdf, meta, resumen=True)
        fig = page()
        header(fig, 2, "Resumen ejecutivo",
               "Lectura corta para circulación: número, respaldo, territorio y cautelas.")
        kpi_cards(fig, 0.735, [
            ("13", "activos\nidentificados", ORANGE),
            ("11", "sedes fijas", BLUE),
            ("2", "itinerantes", GREEN),
            ("6", "comunas", BLUE),
            ("13", "multifuente", ORANGE),
            ("12", "respaldo alto", GREEN),
        ], h=0.105)
        bullet_column(fig, 0.08, 0.600, [
            "Los 13 mercados activos identificados combinan mercados históricos, patios gastronómicos, "
            "food halls, mercados de productores, un barrial alimentario y una feria gastronómica itinerante.",
            "El mapa muestra solo sedes fijas sobre geometría local; los itinerantes quedan aclarados "
            "como actores activos sin punto fijo.",
            "La base permite priorizar circuitos turísticos, productores y economía social, patios "
            "públicos y validaciones territoriales.",
        ], wrap=82, gap=0.066)
        box(fig, 0.07, 0.225, 0.86, 0.125, "Aclaración",
            "No se cuentan como activos Mercado Soho, Mercat Caballito y El Galpón; Carruajes figura "
            "como cerrado documentado. Relevamiento documental y multifuente: no es censo ni padrón "
            "oficial, y Google Places es señal auxiliar no oficial.", "cuid")
        footer(fig, "Resumen ejecutivo")
        pdf.savefig(fig); plt.close(fig)
    print(f"ok: {PDF_RESUMEN}")


# --------------------------------------------------------------------------- #
# README + pack
# --------------------------------------------------------------------------- #
def build_readme() -> None:
    README.write_text("\n".join([
        "# Regenerar informe final de mercados gastronómicos (Markdown-first)",
        "",
        "El PDF final se construye a partir del Markdown maestro editorial, sin requests ni APIs.",
        "Lee CSV V4 sanitizados y visuales V5 ya generados; no cambia datos ni conteos.",
        "",
        "## Fuente editorial",
        "",
        "- `docs/mercados_caba/INFORME_FINAL_MERCADOS_GASTRONOMICOS_CABA_MARKDOWN_MASTER.md`",
        "- `docs/mercados_caba/NOTAS_CONVERSION_PDF_MERCADOS_VFINAL.md`",
        "",
        "## Regenerar",
        "",
        "```powershell",
        "python src\\mercados_caba\\build_visuals_v5.py            # solo si faltan visuales",
        "python src\\mercados_caba\\build_pdf_from_markdown_master.py",
        "python src\\mercados_caba\\validate_mercados_final.py",
        "```",
        "",
        "## Salidas",
        "",
        "- `outputs/mercados_caba/sanitized/INFORME_FINAL_MERCADOS_GASTRONOMICOS_CABA_FINAL.pdf`",
        "- `outputs/mercados_caba/sanitized/RESUMEN_EJECUTIVO_MERCADOS_GASTRONOMICOS_CABA_FINAL.pdf`",
        "- `outputs/mercados_caba/sanitized/PACK_ENTREGABLE_MERCADOS_GASTRONOMICOS_CABA_FINAL.zip`",
        "",
        "No genera PDF de casas de pastas ni DataGastro V2. No toca V4/V5/V5.1.",
    ]), encoding="utf-8")
    print(f"ok: {README}")


def build_pack() -> None:
    files = [
        MASTER_MD,
        NOTES_MD,
        README,
        PDF,
        PDF_RESUMEN,
        SAN / "grafico_kpi_cards_v5.png",
        SAN / "grafico_tipo_primario_v5.png",
        SAN / "grafico_gestion_v5.png",
        SAN / "grafico_horarios_v5.png",
        SAN / "grafico_publicos_objetivo_v5.png",
        SAN / "grafico_respaldo_fuentes_v5.png",
        SAN / "mapa_sedes_fijas_mercados_gastronomicos_v5.png",
        SAN / "visual_itinerantes_mercados_gastronomicos_v5.png",
        SAN / "mercados_sedes_fijas_v5.csv",
        SAN / "mercados_gastronomicos_activos_v4.csv",
        SAN / "mercados_gastronomicos_no_activos_v4.csv",
        SAN / "indicadores_mercados_gastronomicos_v4.csv",
        SAN / "respaldo_fuentes_mercados_v4.csv",
        SAN / "tipologias_mercados_v4.csv",
        SAN / "decisiones_que_permite_tomar_v4.csv",
        SAN / "referencias_documentales_visibles_v4.csv",
    ]
    with zipfile.ZipFile(PACK, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in files:
            zf.write(path, path.relative_to(ROOT).as_posix())
    print(f"ok: {PACK}")


# --------------------------------------------------------------------------- #
# Helpers V2 (maquetacion corregida)
# --------------------------------------------------------------------------- #
def kpi_cards_v2(fig: plt.Figure, y: float, items: list[tuple[str, str, str]],
                 h: float = 0.105, note: str = "") -> None:
    """KPI cards mas limpios (4 protagonistas) con una mini linea metodologica
    opcional debajo, en gris, para los indicadores secundarios."""
    kpi_cards(fig, y, items, h=h)
    if note:
        fig.text(0.07, y - 0.022, note, color=GREY, fontsize=9.0, style="italic", va="top")


def info_card_v2(fig: plt.Figure, x: float, y: float, w: float, h: float,
                 title: str, rows: list[tuple[str, str]], accent: str = BLUE,
                 title_size: float = 9.0, body_size: float = 8.2) -> None:
    """Card con titulo y filas etiqueta/valor, con wrap calibrado al ancho real
    de la card para que el texto nunca se salga del borde ni pise la vecina.

    Calibrado mas conservador que info_card original: ~0.0066 de figura por
    caracter del cuerpo (antes 0.0058, que desbordaba en cards angostas).
    """
    pad = 0.014
    inner_w = w - 2 * pad
    chars_body = max(16, int(inner_w / 0.0066))
    chars_title = max(12, int(inner_w / 0.0072))

    title_lines = textwrap.wrap(title, chars_title)[:2]
    bar_h = 0.030 if len(title_lines) <= 1 else 0.046

    fig.patches.append(Rectangle((x, y), w, h, transform=fig.transFigure,
                                 facecolor=WHITE, edgecolor=LINE, lw=1.0))
    fig.patches.append(Rectangle((x, y + h - bar_h), w, bar_h, transform=fig.transFigure,
                                 facecolor=accent, edgecolor=accent))
    for j, line in enumerate(title_lines):
        fig.text(x + pad, y + h - 0.011 - j * 0.016, line, color=WHITE,
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


# Titulos de decision acortados para que entren en la barra de color sin cortarse.
DECISION_CARDS_V2 = [
    ("Circuitos turísticos",
     "Articular los mercados de mayor atractivo turístico en recorridos integrados.",
     "San Telmo, Belgrano, Gourmand", BLUE),
    ("Productores y economía social",
     "Apoyar mercados y ferias de productores y consumo consciente.",
     "Bonpland, Sabe la Tierra, BA Market", GREEN),
    ("Patios públicos",
     "Usar los patios gastronómicos públicos como dinamizadores barriales.",
     "Lecheros, Smart Plaza, Costanera, Rodrigo Bueno", BLUE),
    ("Base candidata trazable",
     "Sostener un catálogo con tipología y estado operativo, actualizable.",
     "Todos los activos identificados", ORANGE),
    ("Validación territorial",
     "Ordenar la verificación en terreno por respaldo documental.",
     "Empezar por respaldo medio o a validar", ORANGE),
    ("Información pública uniforme",
     "Publicar horarios, gestión y oferta de cada mercado de forma homogénea.",
     "Todos los activos identificados", BLUE),
]


# --------------------------------------------------------------------------- #
# PDF principal V2 (11 paginas: pag. 7 dividida en patrimoniales / no activos)
# --------------------------------------------------------------------------- #
def build_pdf_v2(meta: dict[str, str]) -> None:
    active = read_csv("mercados_gastronomicos_activos_v4.csv")
    respaldo = read_csv("respaldo_fuentes_mercados_v4.csv")

    with PdfPages(PDF_V2) as pdf:
        # --- Pagina 1: portada ---
        cover(pdf, meta)

        # --- Pagina 2: resumen ejecutivo + indicadores (4 KPI + mini linea) ---
        fig = page()
        header(fig, 2, "Resumen ejecutivo e indicadores clave",
               "13 activos identificados; 11 con sede fija y 2 itinerantes, en 6 comunas.")
        kpi_cards_v2(fig, 0.745, [
            ("13", "activos\nidentificados", ORANGE),
            ("11", "sedes fijas", BLUE),
            ("2", "itinerantes", GREEN),
            ("6", "comunas", BLUE),
        ], h=0.115,
            note="Respaldo documental: los 13 son multifuente · 12 con respaldo alto · 1 medio.")
        bullet_column(fig, 0.08, 0.620, [
            "La Ciudad cuenta con 13 mercados gastronómicos activos identificados: 11 con sede fija y 2 itinerantes.",
            "Los 13 son multifuente; 12 alcanzan respaldo documental alto y 1 medio.",
            "Conviven gestión pública (3), privada (5) y mixta (5) en seis comunas.",
            "Se documentan, aparte, 3 espacios relevantes no contabilizados y 1 cerrado documentado.",
        ], wrap=84, gap=0.052)
        box(fig, 0.07, 0.300, 0.86, 0.11, "Cuidado metodológico",
            "\"Activos identificados\" significa respaldo documental cruzado, no validación territorial "
            "confirmada en terreno. Es respaldo documental, no padrón oficial.", "cuid")
        box(fig, 0.07, 0.150, 0.86, 0.115, "Cómo se leyó el universo",
            "El relevamiento integra fuentes públicas oficiales, sitios propios, fuentes internas "
            "sanitizadas, Google Places como señal auxiliar no oficial y revisión documental complementaria.")
        footer(fig, "Base candidata no oficial")
        pdf.savefig(fig); plt.close(fig)

        # --- Pagina 3: universo y respaldo multifuente ---
        fig = page()
        header(fig, 3, "Cómo se construyó el universo identificado",
               "Cruce documental y multifuente, explicado sin sobreprometer.")
        image_fit(fig, "grafico_respaldo_fuentes_v5.png", 0.07, 0.840, 0.86)
        box(fig, 0.07, 0.315, 0.41, 0.135, "Lectura ejecutiva",
            "La fortaleza no está en una única fuente, sino en la convergencia entre fuentes "
            "públicas, sitios propios, señal operativa no oficial y revisión documental.")
        box(fig, 0.52, 0.315, 0.41, 0.135, "Cuidado metodológico",
            "Google Places se trata como señal auxiliar no oficial: no reemplaza una fuente "
            "administrativa ni una validación territorial.", "cuid")
        data = [[r["nombre"], r["cantidad_tipos_fuente"],
                 r["nivel_respaldo_documental"].replace("_", " ")] for r in respaldo[:6]]
        table(fig, [0.08, 0.105, 0.84, 0.17], data,
              ["Ejemplos", "Tipos de fuente", "Respaldo"], 7.4, 1.34)
        footer(fig, "Google es señal auxiliar no oficial")
        pdf.savefig(fig); plt.close(fig)

        # --- Pagina 4: mapa territorial (mapa V2 con nombres completos) ---
        fig = page()
        header(fig, 4, "Dónde están: sedes fijas e itinerancia",
               "Mapa principal de las 11 sedes fijas, sobre geometría local de barrios y comunas.")
        image(fig, MAP_V2, [0.05, 0.345, 0.90, 0.52])
        box(fig, 0.07, 0.175, 0.86, 0.115, "Itinerantes: no se mapean como punto fijo",
            "Buenos Aires Market y Sabe la Tierra integran el conteo activo identificado, pero operan "
            "con sedes variables y sin evidencia suficiente para fijar una coordenada única. "
            "Se tratan como atributo de itinerancia, no como tipología adicional.", "cuid")
        box(fig, 0.07, 0.090, 0.86, 0.068, "Nota metodológica",
            "El mapa muestra solo mercados con sede fija, con coordenadas aproximadas para lectura "
            "territorial; no es geolocalización exacta ni validación en terreno.")
        footer(fig, "Puntos aproximados para lectura territorial")
        pdf.savefig(fig); plt.close(fig)

        # --- Pagina 5: tipologias + gestion (graficos agrandados) ---
        fig = page()
        header(fig, 5, "Tipologías y gestión",
               "Tipología primaria única (suma 13 sin doble conteo) y modelos de gestión.")
        image_fit(fig, "grafico_tipo_primario_v5.png", 0.055, 0.815, 0.50)
        image_fit(fig, "grafico_gestion_v5.png", 0.565, 0.795, 0.40)
        box(fig, 0.07, 0.470, 0.86, 0.130, "Lectura ejecutiva",
            "Patios gastronómicos (4) y mercados históricos (3) concentran el núcleo; food halls (2) "
            "y mercados de productores (2) completan, con un barrial alimentario y una feria gastronómica. "
            "La gestión combina iniciativa privada (5), esquemas mixtos (5) y gestión pública (3).")
        box(fig, 0.07, 0.300, 0.86, 0.130, "Cuidado metodológico",
            "Cada mercado tiene un tipo primario único, de modo que las categorías suman exactamente 13. "
            "\"Itinerante\" y \"perfil de productores\" se tratan como atributos, no como tipología adicional.",
            "cuid")
        footer(fig, "Tipo primario único por mercado")
        pdf.savefig(fig); plt.close(fig)

        # --- Pagina 6: horarios + publicos (graficos agrandados) ---
        fig = page()
        header(fig, 6, "Horarios y públicos objetivo",
               "Frecuencia de apertura y perfiles de público, como lectura orientativa.")
        image_fit(fig, "grafico_horarios_v5.png", 0.055, 0.795, 0.50)
        image_fit(fig, "grafico_publicos_objetivo_v5.png", 0.565, 0.815, 0.40)
        box(fig, 0.07, 0.470, 0.86, 0.130, "Lectura ejecutiva",
            "Conviven mercados de operación diaria o casi diaria, de días específicos e itinerantes de "
            "fin de semana. 11 de 13 tienen horario documentado. Predominan los perfiles barrial y "
            "turístico/barrial, con un núcleo de consumo consciente.")
        box(fig, 0.07, 0.300, 0.86, 0.130, "Cuidado metodológico",
            "Los horarios son autodeclarados y a veces divergentes; San Telmo presenta fuentes "
            "divergentes y los itinerantes dependen de la sede. El perfil de público es una lectura "
            "cualitativa, no una medición de afluencia.", "cuid")
        footer(fig, "Horarios documentales; pueden cambiar")
        pdf.savefig(fig); plt.close(fig)

        # --- Pagina 7: casos patrimoniales y emblematicos (5 cards anchas) ---
        fig = page()
        header(fig, 7, "Casos patrimoniales y emblemáticos",
               "Identidad histórica documentada, dentro del conteo activo identificado.")
        # Fila 1: 3 cards anchas; Fila 2: 2 cards anchas.
        pat_row1 = [(0.07, 0.560), (0.365, 0.560), (0.66, 0.560)]
        for pos, (nombre, anio, lectura, accent) in zip(pat_row1, PATRIMONIALES[:3]):
            info_card_v2(fig, pos[0], pos[1], 0.265, 0.190, nombre,
                         [("Hito", anio), ("Lectura", lectura)], accent)
        pat_row2 = [(0.07, 0.310), (0.365, 0.310)]
        for pos, (nombre, anio, lectura, accent) in zip(pat_row2, PATRIMONIALES[3:5]):
            info_card_v2(fig, pos[0], pos[1], 0.265, 0.190, nombre,
                         [("Hito", anio), ("Lectura", lectura)], accent)
        box(fig, 0.07, 0.105, 0.86, 0.130, "Cuidado metodológico",
            "Estos casos sí integran el conteo de 13 activos identificados: se destacan por su valor "
            "patrimonial o emblemático, no como categoría separada. El año o hito indicado proviene de "
            "documentación pública y no constituye validación territorial.", "cuid")
        footer(fig, "Patrimoniales dentro del conteo activo")
        pdf.savefig(fig); plt.close(fig)

        # --- Pagina 8: espacios no contabilizados y cerrado (4 cards anchas) ---
        fig = page()
        header(fig, 8, "Espacios relevantes no contabilizados y cerrado documentado",
               "Casos fuera del conteo activo, documentados como categorías diferenciadas.")
        nc_pos = [(0.07, 0.520), (0.52, 0.520), (0.07, 0.270), (0.52, 0.270)]
        for pos, (nombre, estado, motivo, lectura, accent) in zip(nc_pos, NO_ACTIVOS):
            info_card_v2(fig, pos[0], pos[1], 0.41, 0.230, nombre, [
                ("Estado", estado),
                ("Motivo", motivo),
                ("Lectura", lectura),
            ], accent)
        box(fig, 0.07, 0.105, 0.86, 0.130, "Cuidado metodológico",
            "No son errores ni descartes definitivos: se documentan como categorías diferenciadas. "
            "Los relevantes no contabilizados vuelven al conteo si se valida actividad vigente. "
            "Quedan, además, fuera de alcance distritos comerciales, abasto barrial, pulgas y outlet, "
            "por no ser mercados gastronómicos únicos.", "cuid")
        footer(fig, "No mezclar activos con casos en revisión")
        pdf.savefig(fig); plt.close(fig)

        # --- Pagina 9: decisiones de gestion (2 columnas x 3 filas) ---
        fig = page()
        header(fig, 9, "Qué decisión permite tomar este informe",
               "Seis líneas de acción concretas, en cards ejecutivas.")
        dec_pos = [(0.07, 0.620), (0.52, 0.620),
                   (0.07, 0.420), (0.52, 0.420),
                   (0.07, 0.220), (0.52, 0.220)]
        for pos, (title, uso, ejemplo, accent) in zip(dec_pos, DECISION_CARDS_V2):
            info_card_v2(fig, pos[0], pos[1], 0.41, 0.170, title, [
                ("Uso", uso),
                ("Aplica a", ejemplo),
            ], accent)
        box(fig, 0.07, 0.090, 0.86, 0.105, "Cierre ejecutivo",
            "El informe funciona como herramienta de gestión: muestra dónde mirar, qué validar y qué no "
            "mezclar. Las decisiones que afectan el estado operativo de un caso en revisión requieren "
            "validación territorial previa.")
        footer(fig, "Base candidata trazable")
        pdf.savefig(fig); plt.close(fig)

        # --- Pagina 10: tabla final (mas legible, nombres completos) ---
        fig = page()
        header(fig, 10, "Tabla final de mercados activos identificados",
               "13 activos (11 sede fija + 2 itinerantes), en formato legible.")
        rows = []
        for r in active:
            comuna = r["comuna"] if r["comuna"] != "0" else "itin."
            rows.append([
                r["nombre"],
                TYPE_LABEL.get(r["tipo_primario"], r["tipo_primario"]),
                r["gestion"],
                f"{r['barrio']} / {comuna}",
                "itinerante" if r["es_itinerante"] == "si" else "sede fija",
                r["nivel_respaldo_documental"].replace("_documental", ""),
            ])
        table(fig, [0.045, 0.215, 0.91, 0.60], rows,
              ["Nombre", "Tipo", "Gestión", "Barrio / comuna", "Sede", "Respaldo"], 7.2, 1.62,
              col_widths=[0.275, 0.180, 0.100, 0.185, 0.130, 0.130])
        fig.text(0.07, 0.165, "Suma exacta: 13 activos identificados (11 de sede fija + 2 itinerantes).",
                 color=GREY, fontsize=9.0, style="italic")
        footer(fig, "Tabla final")
        pdf.savefig(fig); plt.close(fig)

        # --- Pagina 11: limitaciones + proximos pasos + cierre ---
        fig = page()
        header(fig, 11, "Limitaciones, próximos pasos y cierre",
               "Cierre separado para evitar cajas cortadas al pie.")
        box(fig, 0.07, 0.640, 0.86, 0.155, "Limitaciones",
            "Relevamiento documental y multifuente. No reemplaza la validación territorial ni el "
            "registro oficial. Google Places es señal auxiliar no oficial. Horarios autodeclarados y "
            "a veces divergentes. Coordenadas aproximadas por barrio. El respaldo documental alto o "
            "medio no equivale a confianza territorial.", "cuid")
        fig.text(0.07, 0.600, "Próximos pasos", color=INK, fontsize=10.5, fontweight="bold")
        bullet_column(fig, 0.085, 0.560, [
            "Validar en terreno los casos de respaldo medio o a validar.",
            "Monitorear los espacios con señales de cierre (Soho, Mercat Caballito, El Galpón).",
            "Homogeneizar la información pública de horarios, gestión y oferta.",
            "Mantener la base candidata como insumo actualizable, no como total definitivo.",
        ], wrap=84, gap=0.048)
        box(fig, 0.07, 0.155, 0.86, 0.155, "Qué aporta DataGastro",
            "Un método replicable —registro oficial, sitios propios, señal operativa, fuente interna "
            "y revisión documental— para construir una base candidata trazable, distinguir tipologías "
            "y separar con claridad activos identificados, casos en revisión, cerrados y fuera de "
            "alcance. Es una base candidata, no oficial.")
        footer(fig, "No es censo ni padrón oficial")
        pdf.savefig(fig); plt.close(fig)

    print(f"ok: {PDF_V2}")


# --------------------------------------------------------------------------- #
# Resumen ejecutivo V2 (2 paginas, 4 KPI + mini linea)
# --------------------------------------------------------------------------- #
def build_summary_pdf_v2(meta: dict[str, str]) -> None:
    with PdfPages(PDF_RESUMEN_V2) as pdf:
        cover(pdf, meta, resumen=True)
        fig = page()
        header(fig, 2, "Resumen ejecutivo",
               "Lectura corta para circulación: número, respaldo, territorio y cautelas.")
        kpi_cards_v2(fig, 0.745, [
            ("13", "activos\nidentificados", ORANGE),
            ("11", "sedes fijas", BLUE),
            ("2", "itinerantes", GREEN),
            ("6", "comunas", BLUE),
        ], h=0.115,
            note="Respaldo documental: los 13 son multifuente · 12 con respaldo alto · 1 medio.")
        bullet_column(fig, 0.08, 0.600, [
            "Los 13 mercados activos identificados combinan mercados históricos, patios gastronómicos, "
            "food halls, mercados de productores, un barrial alimentario y una feria gastronómica itinerante.",
            "El mapa muestra solo sedes fijas sobre geometría local; los itinerantes quedan aclarados "
            "como actores activos sin punto fijo.",
            "La base permite priorizar circuitos turísticos, productores y economía social, patios "
            "públicos y validaciones territoriales.",
        ], wrap=82, gap=0.066)
        box(fig, 0.07, 0.225, 0.86, 0.125, "Aclaración",
            "No se cuentan como activos Mercado Soho, Mercat Caballito y El Galpón; Carruajes figura "
            "como cerrado documentado. Relevamiento documental y multifuente: no es censo ni padrón "
            "oficial, y Google Places es señal auxiliar no oficial.", "cuid")
        footer(fig, "Resumen ejecutivo")
        pdf.savefig(fig); plt.close(fig)
    print(f"ok: {PDF_RESUMEN_V2}")


# --------------------------------------------------------------------------- #
# README + pack V2
# --------------------------------------------------------------------------- #
def build_readme_v2() -> None:
    README_V2.write_text("\n".join([
        "# Regenerar informe final V2 de mercados gastronómicos (visualmente corregido)",
        "",
        "V2 es la versión con maquetación corregida del informe final. Mismos datos,",
        "mismos conteos y misma fuente editorial que el FINAL; solo cambia el layout.",
        "No hace requests ni usa APIs.",
        "",
        "## Correcciones de diseño respecto del FINAL",
        "",
        "- Página 2: KPI reducidos a 4 (13 / 11 / 2 / 6 comunas) + mini línea metodológica.",
        "- Página 4: mapa con nombres completos y callouts; nota metodológica sin cortes.",
        "- Páginas 5 y 6: gráficos agrandados, menos aire vacío.",
        "- Páginas 7 y 8: casos patrimoniales y no contabilizados separados en dos páginas.",
        "- Página 9: cards de decisión en 2 columnas, sin texto que se salga ni se pise.",
        "- Página 10: tabla final más legible, con nombres completos.",
        "- El informe pasa de 10 a 11 páginas.",
        "",
        "## Regenerar",
        "",
        "```powershell",
        "python src\\mercados_caba\\build_visuals_v5.py            # genera mapa V2 (v5_2)",
        "python src\\mercados_caba\\build_pdf_from_markdown_master.py",
        "python src\\mercados_caba\\validate_mercados_final_v2.py",
        "```",
        "",
        "## Salidas V2",
        "",
        "- `outputs/mercados_caba/sanitized/INFORME_FINAL_MERCADOS_GASTRONOMICOS_CABA_FINAL_V2.pdf`",
        "- `outputs/mercados_caba/sanitized/RESUMEN_EJECUTIVO_MERCADOS_GASTRONOMICOS_CABA_FINAL_V2.pdf`",
        "- `outputs/mercados_caba/sanitized/PACK_ENTREGABLE_MERCADOS_GASTRONOMICOS_CABA_FINAL_V2.zip`",
        "",
        "No sobrescribe el FINAL ni V4/V5/V5.1. No toca casas de pastas ni DataGastro V2.",
    ]), encoding="utf-8")
    print(f"ok: {README_V2}")


def build_pack_v2() -> None:
    files = [
        MASTER_MD,
        NOTES_MD,
        README_V2,
        PDF_V2,
        PDF_RESUMEN_V2,
        SAN / "grafico_kpi_cards_v5.png",
        SAN / "grafico_tipo_primario_v5.png",
        SAN / "grafico_gestion_v5.png",
        SAN / "grafico_horarios_v5.png",
        SAN / "grafico_publicos_objetivo_v5.png",
        SAN / "grafico_respaldo_fuentes_v5.png",
        SAN / MAP_V2,
        SAN / "mercados_sedes_fijas_v5.csv",
        SAN / "mercados_gastronomicos_activos_v4.csv",
        SAN / "mercados_gastronomicos_no_activos_v4.csv",
        SAN / "indicadores_mercados_gastronomicos_v4.csv",
        SAN / "respaldo_fuentes_mercados_v4.csv",
        SAN / "tipologias_mercados_v4.csv",
        SAN / "decisiones_que_permite_tomar_v4.csv",
        SAN / "referencias_documentales_visibles_v4.csv",
    ]
    with zipfile.ZipFile(PACK_V2, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in files:
            zf.write(path, path.relative_to(ROOT).as_posix())
    print(f"ok: {PACK_V2}")


# --------------------------------------------------------------------------- #
# Soporte V3: matriz de publicos + anexo
# --------------------------------------------------------------------------- #
def build_publicos_support_files() -> None:
    fieldnames = [
        "mercado",
        "perfil_principal",
        "perfil_secundario",
        "momento_recomendado",
        "activacion_recomendada",
        "evidencia_principal",
        "tipo_evidencia",
        "nivel_confianza",
        "urls_clave",
    ]

    with PUBLICOS_CSV.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(PUBLICOS_FULL_MATRIX)

    table_lines = [
        "| Mercado | Perfil principal | Perfil secundario | Momento recomendado | Activacion recomendada | Evidencia | Confianza |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in PUBLICOS_FULL_MATRIX:
        table_lines.append(
            "| {mercado} | {perfil_principal} | {perfil_secundario} | "
            "{momento_recomendado} | {activacion_recomendada} | "
            "{tipo_evidencia} | {nivel_confianza} |".format(**row)
        )

    urls = []
    for row in PUBLICOS_FULL_MATRIX:
        urls.extend([url.strip() for url in row["urls_clave"].split(";") if url.strip()])
    unique_urls = sorted(set(urls))

    anexo_lines = [
        "# Anexo - Públicos objetivo y activación territorial",
        "",
        "## Metodología breve",
        "",
        PUBLICOS_METODOLOGIA,
        "",
        "La matriz consolida lecturas cualitativas ya trabajadas en el relevamiento de mercados "
        "gastronómicos: perfil documentado, tipología primaria, gestión, itinerancia, respaldo "
        "multifuente y usos posibles de programación. No modifica conteos, estados ni universo.",
        "",
        "## Síntesis ejecutiva",
        "",
    ]
    for title, text, _color in PUBLICOS_INSIGHTS:
        anexo_lines.extend([f"- **{title}.** {text}"])

    anexo_lines.extend([
        "",
        "## Matriz completa de los 13 mercados",
        "",
        *table_lines,
        "",
        "## URLs clave",
        "",
    ])
    anexo_lines.extend([f"- {url}" for url in unique_urls])
    anexo_lines.extend([
        "",
        "## Frase metodológica de prudencia",
        "",
        PUBLICOS_METODOLOGIA,
        "",
    ])

    PUBLICOS_ANEXO_MD.write_text("\n".join(anexo_lines), encoding="utf-8")
    print(f"ok: {PUBLICOS_CSV}")
    print(f"ok: {PUBLICOS_ANEXO_MD}")


def publicos_operativos_page_v3(pdf: PdfPages) -> None:
    fig = page()
    header(fig, 7, "Lectura operativa de públicos y activación territorial")
    box(fig, 0.07, 0.735, 0.86, 0.115, "Frase metodológica",
        PUBLICOS_METODOLOGIA, "cuid")

    fig.text(0.07, 0.700, "Insights ejecutivos", color=INK, fontsize=10.5,
             fontweight="bold")
    row1 = [(0.07, 0.555), (0.365, 0.555), (0.66, 0.555)]
    for pos, (title, text, accent) in zip(row1, PUBLICOS_INSIGHTS[:3]):
        info_card_v2(fig, pos[0], pos[1], 0.265, 0.125, title,
                     [("Uso", text)], accent, title_size=8.0, body_size=7.1)
    row2 = [(0.07, 0.405), (0.52, 0.405)]
    for pos, (title, text, accent) in zip(row2, PUBLICOS_INSIGHTS[3:]):
        info_card_v2(fig, pos[0], pos[1], 0.41, 0.125, title,
                     [("Uso", text)], accent, title_size=8.0, body_size=7.1)

    fig.text(0.07, 0.360, "Mini matriz compacta", color=INK, fontsize=10.5,
             fontweight="bold")
    table(fig, [0.045, 0.105, 0.91, 0.230], PUBLICOS_COMPACT_MATRIX,
          ["Perfil operativo", "Mercados principales", "Uso recomendado"],
          font=6.7, yscale=1.35, col_widths=[0.245, 0.385, 0.370])
    footer(fig, "Lectura orientativa; requiere validación en terreno")
    pdf.savefig(fig)
    plt.close(fig)


# --------------------------------------------------------------------------- #
# PDF principal V3 (12 paginas: V2 + pagina nueva de publicos)
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
# README + pack V3
# --------------------------------------------------------------------------- #
def build_readme_v3() -> None:
    README_V3.write_text("\n".join([
        "# Regenerar informe final V3 de mercados gastronomicos",
        "",
        "V3 parte de la version visualmente corregida V2 y agrega una sola pagina nueva:",
        "`Lectura operativa de publicos y activacion territorial`.",
        "",
        "No hace requests ni usa APIs. No cambia conteos, universo, estados, mapa, graficos,",
        "portada, KPI cards, tabla final ni paginas existentes, salvo la numeracion corrida",
        "por la insercion de una pagina nueva.",
        "",
        "## Regenerar solo V3",
        "",
        "```powershell",
        "python src\\mercados_caba\\build_pdf_from_markdown_master.py --only-v3",
        "python src\\mercados_caba\\validate_mercados_final_v3.py",
        "```",
        "",
        "## Salidas V3",
        "",
        "- `outputs/mercados_caba/sanitized/INFORME_FINAL_MERCADOS_GASTRONOMICOS_CABA_FINAL_V3.pdf`",
        "- `outputs/mercados_caba/sanitized/RESUMEN_EJECUTIVO_MERCADOS_GASTRONOMICOS_CABA_FINAL_V3.pdf`",
        "- `outputs/mercados_caba/sanitized/PACK_ENTREGABLE_MERCADOS_GASTRONOMICOS_CABA_FINAL_V3.zip`",
        "- `outputs/mercados_caba/sanitized/publicos_objetivo_mercados_vfinal.csv`",
        "- `docs/mercados_caba/ANEXO_PUBLICOS_OBJETIVO_ACTIVACION_TERRITORIAL.md`",
        "",
        "El informe final V3 queda en 12 paginas: paginas 1 a 6 iguales a V2,",
        "pagina 7 nueva, paginas 8 a 12 equivalentes a paginas 7 a 11 de V2.",
    ]), encoding="utf-8")
    print(f"ok: {README_V3}")


def build_pack_v3() -> None:
    files = [
        MASTER_MD,
        NOTES_MD,
        README_V3,
        PUBLICOS_ANEXO_MD,
        PUBLICOS_CSV,
        PDF_V3,
        PDF_RESUMEN_V3,
        SAN / "grafico_kpi_cards_v5.png",
        SAN / "grafico_tipo_primario_v5.png",
        SAN / "grafico_gestion_v5.png",
        SAN / "grafico_horarios_v5.png",
        SAN / "grafico_publicos_objetivo_v5.png",
        SAN / "grafico_respaldo_fuentes_v5.png",
        SAN / MAP_V2,
        SAN / "mercados_sedes_fijas_v5.csv",
        SAN / "mercados_gastronomicos_activos_v4.csv",
        SAN / "mercados_gastronomicos_no_activos_v4.csv",
        SAN / "indicadores_mercados_gastronomicos_v4.csv",
        SAN / "respaldo_fuentes_mercados_v4.csv",
        SAN / "tipologias_mercados_v4.csv",
        SAN / "decisiones_que_permite_tomar_v4.csv",
        SAN / "referencias_documentales_visibles_v4.csv",
    ]
    with zipfile.ZipFile(PACK_V3, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in files:
            zf.write(path, path.relative_to(ROOT).as_posix())
    print(f"ok: {PACK_V3}")


def run_pdf_tool(cmd: list[str]) -> None:
    result = subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"Fallo {' '.join(cmd[:1])}: {detail}")


def build_pdf_v3(meta: dict[str, str]) -> None:
    """Compone V3 desde el PDF V2 existente para preservar sus paginas.

    La V3 no re-renderiza portada, mapa, graficos, KPI cards ni paginas
    existentes: separa V2 en paginas, inserta una pagina nueva y vuelve a unir.
    """
    _ = meta  # La portada y las paginas existentes vienen del PDF V2.
    if not PDF_V2.exists():
        raise FileNotFoundError(f"No existe PDF base V2: {PDF_V2}")

    with tempfile.TemporaryDirectory(prefix="mercados_v3_") as tmp_name:
        tmp = Path(tmp_name)
        page_pattern = tmp / "v2_page_%02d.pdf"
        run_pdf_tool(["pdfseparate", str(PDF_V2), str(page_pattern)])
        v2_pages = sorted(tmp.glob("v2_page_*.pdf"))
        if len(v2_pages) != 11:
            raise RuntimeError(f"Se esperaban 11 paginas V2 y se obtuvieron {len(v2_pages)}")

        publicos_page = tmp / "publicos_operativos_v3.pdf"
        with PdfPages(publicos_page) as pdf:
            publicos_operativos_page_v3(pdf)

        ordered_pages = v2_pages[:6] + [publicos_page] + v2_pages[6:]
        run_pdf_tool(["pdfunite", *[str(path) for path in ordered_pages], str(PDF_V3)])

    print(f"ok: {PDF_V3}")


def build_summary_pdf_v3(meta: dict[str, str]) -> None:
    _ = meta
    if not PDF_RESUMEN_V2.exists():
        raise FileNotFoundError(f"No existe resumen base V2: {PDF_RESUMEN_V2}")
    shutil.copyfile(PDF_RESUMEN_V2, PDF_RESUMEN_V3)
    print(f"ok: {PDF_RESUMEN_V3}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Genera informes finales de mercados CABA.")
    parser.add_argument("--only-v3", action="store_true",
                        help="Genera solo salidas V3 para no sobrescribir FINAL ni V2.")
    args = parser.parse_args()

    meta = load_master_meta()
    if args.only_v3:
        build_readme_v3()
        build_publicos_support_files()
        build_pdf_v3(meta)
        build_summary_pdf_v3(meta)
        build_pack_v3()
        return 0

    build_readme()
    build_pdf(meta)
    build_summary_pdf(meta)
    build_pack()
    # Version visualmente corregida (V2). No sobrescribe el FINAL ni las previas.
    build_readme_v2()
    build_pdf_v2(meta)
    build_summary_pdf_v2(meta)
    build_pack_v2()
    # Version comparativa (V3): V2 + una pagina operativa de publicos.
    build_readme_v3()
    build_publicos_support_files()
    build_pdf_v3(meta)
    build_summary_pdf_v3(meta)
    build_pack_v3()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
