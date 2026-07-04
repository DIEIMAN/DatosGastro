# -*- coding: utf-8 -*-
"""Fase25: microajustes finales sobre fase24.

Parte del generador de fase24 y aplica solo correcciones puntuales:
- indice pagina 2 sin linea guia pisando texto;
- Puerto Madero con rotulos menos superpuestos;
- Barrio Chino con tag neutro;
- cajas 7-11 como "Referencias del universo semilla";
- frase de pagina 3 y rotulo Corrientes ajustados.

No usa APIs, no usa Google Places, no hace scraping, no toca datos fuente
ni modifica fases anteriores. Solo lee assets locales y escribe en fase25.
"""
from __future__ import annotations

import importlib.util
import sys
import textwrap
from pathlib import Path

from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import matplotlib.pyplot as plt
from PIL import Image
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[2]
FASE24_SCRIPT = ROOT / "scripts" / "polos_gastro" / "build_fase24_fase22_corregida_oficina.py"

spec = importlib.util.spec_from_file_location("fase24_base", FASE24_SCRIPT)
fase24 = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules["fase24_base"] = fase24
spec.loader.exec_module(fase24)

OUT = ROOT / "outputs" / "polos_gastro" / "fase25_microajustes_finales_oficina"
ASSETS = OUT / "assets"
PDF_OUT = OUT / "INFORME_POLOS_GASTRO_DGDGAS_11P_OFICINA_FASE25.pdf"

fase24.OUT = OUT
fase24.ASSETS = ASSETS
fase24.PDF_OUT = PDF_OUT
fase24.MAP_OUTPUTS = {
    "palermo": "mapa_fase25_palermo_las_canitas",
    "puerto": "mapa_fase25_puerto_madero",
    "san_telmo": "mapa_fase25_san_telmo",
    "corrientes": "mapa_fase25_corrientes_abasto",
    "belgrano": "mapa_fase25_belgrano",
}

# Pagina 8: mover etiquetas de calle y simplificar el texto vertical redundante.
fase24.MAP_CFG["puerto"]["labels"] = [
    (-58.3780, -34.5996, "A. Moreau de Justo"),
    (-58.3676, -34.6138, "Juana Manso"),
    (-58.382, -34.610, "Huergo / Madero"),
]

for geometry in fase24.GEOMETRIES:
    if geometry["key"] == "puerto" and geometry["label"] == "Docks":
        geometry["label_pos"] = (-58.3656, -34.6006)
    if geometry["key"] == "puerto" and geometry["label"] == "Sector costero":
        geometry["label_pos"] = (-58.3565, -34.6144)
    if geometry["key"] == "puerto" and geometry["label"] == "Faena / El Mercado":
        geometry["label_pos"] = (-58.3739, -34.6165)
    if geometry["key"] == "corrientes" and geometry["subzona"] == "Corrientes 9 de Julio-Callao":
        geometry["subzona"] = "Corrientes (9 de Julio – Callao)"
        geometry["label"] = "Corrientes (9 de Julio – Callao)"
        geometry["label_width"] = 18
    if geometry["key"] == "belgrano" and geometry["subzona"] == "Barrio Chino":
        geometry["tag"] = "SUBZONA APROX."


def draw_street_context_f25(ax, page: str, streets, barrios) -> None:
    cfg = fase24.MAP_CFG[page]
    minx, miny, maxx, maxy = cfg["bbox"]
    if cfg.get("water"):
        ax.add_patch(
            fase24.MplPolygon(
                [(-58.3635, miny), (maxx, miny), (maxx, maxy), (-58.3635, maxy)],
                facecolor="#E6EDF3",
                edgecolor="none",
                alpha=0.92,
                zorder=0,
            )
        )

    local_barrios = barrios.cx[minx:maxx, miny:maxy]
    if not local_barrios.empty:
        local_barrios.plot(ax=ax, facecolor="#F6F8FA", edgecolor="#D6DDE5", linewidth=0.50, zorder=1)

    local_streets = streets.cx[minx:maxx, miny:maxy]
    if local_streets.empty:
        return
    tipo = local_streets["tipo_c"].fillna("").str.upper()
    minor = local_streets[tipo != "AVENIDA"]
    avenues = local_streets[tipo == "AVENIDA"]
    if not minor.empty:
        minor.plot(ax=ax, color="#E8EDF1", linewidth=0.20, alpha=0.52, zorder=2)
    if not avenues.empty:
        avenues.plot(ax=ax, color="#D3DAE0", linewidth=0.62, alpha=0.76, zorder=3)
    major = local_streets[
        local_streets["nom_mapa"].fillna("").map(lambda value: fase24.contains_any(value, cfg["major"]))
        | local_streets["nomoficial"].fillna("").map(lambda value: fase24.contains_any(value, cfg["major"]))
    ]
    if not major.empty:
        major.plot(ax=ax, color="#8A97A3", linewidth=1.08, alpha=0.88, zorder=4)


fase24.draw_street_context = draw_street_context_f25


def build_global_map_f25() -> Path:
    spec_f13 = importlib.util.spec_from_file_location("fase13_mapas", fase24.FASE13_SCRIPT)
    f13 = importlib.util.module_from_spec(spec_f13)
    assert spec_f13 and spec_f13.loader
    sys.modules["fase13_mapas"] = f13
    spec_f13.loader.exec_module(f13)
    f13.INSTITUCION = fase24.INSTITUCION

    config = {name: dict(cfg) for name, cfg in f13.POLO_CONFIG.items()}
    config["Abasto"]["offset"] = (-0.0045, -0.0100)
    config["Corredor DoHo / Donado-Holmberg"]["offset"] = (0.0068, 0.0082)
    config["Villa Pueyrredon / Avenida San Martin"]["etiqueta"] = "Villa Pueyrredón / San Martín"

    barrios = f13.load_geojson(f13.GEO_BARRIOS)
    fig, ax = plt.subplots(figsize=(11, 12.5))
    f13.draw_base(ax, barrios)
    for name in f13.POLO_CONFIG:
        f13.draw_shape(ax, barrios, config[name], alpha=0.22, label=True)
    legend = [
        Patch(facecolor=f13.TIPO_COLOR["area_barrio"], alpha=0.30, edgecolor=f13.TIPO_COLOR["area_barrio"], label="Área / barrio de lectura"),
        Patch(facecolor=f13.TIPO_COLOR["macroarea"], alpha=0.30, edgecolor=f13.TIPO_COLOR["macroarea"], label="Macroárea con subzonas"),
        Patch(facecolor=f13.TIPO_COLOR["area_aproximada"], alpha=0.30, edgecolor=f13.TIPO_COLOR["area_aproximada"], label="Área aproximada"),
        Line2D([0], [0], color=f13.TIPO_COLOR["eje_aproximado"], lw=2.5, label="Eje / corredor aproximado"),
    ]
    ax.legend(handles=legend, loc="lower left", bbox_to_anchor=(0.02, 0.035), frameon=True, fontsize=8.2)
    f13.finish_map(
        ax,
        "Mapa general de polos y ejes gastronómicos",
        "Áreas y ejes del universo semilla. No representa locales individuales.",
        "Lectura territorial. Base cartográfica local de barrios CABA. Áreas/ejes aproximados; no son delimitaciones oficiales ni padrón de locales.",
    )
    full_png = ASSETS / "mapa_global_fase25_completo.png"
    fig.savefig(full_png, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    img = Image.open(full_png).convert("RGBA")
    crop = img.crop((105, 360, 1985, 2465))
    base = Image.new("RGB", crop.size, "white")
    base.paste(crop, mask=crop.split()[-1])
    dest = ASSETS / "global_mapa_fase25.png"
    base.save(dest, optimize=True)
    return dest


fase24.build_global_map = build_global_map_f25


def index_page_f25(c: canvas.Canvas) -> None:
    fase24.page_header(c, 2, "Índice")
    entries = [
        "Portada",
        "Índice",
        "Resumen ejecutivo",
        "Alcance y criterio de lectura",
        "Mapa general de polos y ejes gastronómicos",
        "Lectura territorial general",
        "Detalle: Palermo / Las Cañitas",
        "Detalle: Puerto Madero",
        "Detalle: San Telmo",
        "Detalle: Corrientes / Abasto",
        "Detalle: Belgrano",
    ]
    y = fase24.H - 132
    for idx, entry in enumerate(entries, start=1):
        c.setFont(fase24.FONT, 11.2)
        fase24.set_fill(c, fase24.NEGRO)
        c.drawString(fase24.M + 10, y, entry)
        text_end = fase24.M + 10 + fase24.pdfmetrics.stringWidth(entry, fase24.FONT, 11.2) + 18
        line_start = max(fase24.M + 210, text_end)
        line_end = fase24.W - fase24.M - 36
        if line_start < line_end - 14:
            fase24.set_stroke(c, fase24.LINEA)
            c.line(line_start, y + 3, line_end, y + 3)
        c.setFont(fase24.FONT_BOLD, 11.2)
        c.drawRightString(fase24.W - fase24.M - 10, y, str(idx))
        y -= 42
    fase24.finish_page(c)


fase24.index_page = index_page_f25


def summary_page_f25(c: canvas.Canvas) -> None:
    y = fase24.page_header(
        c,
        3,
        "Resumen ejecutivo",
        "Una lectura territorial inicial de los polos gastronómicos de la Ciudad.",
    )
    paragraphs = [
        "Este informe organiza un universo semilla de 22 polos y ejes gastronómicos de la Ciudad de Buenos Aires, con el objetivo de aportar un insumo para la discusión institucional y el ordenamiento de criterios.",
        "La pieza combina un mapa global de referencia, mapas de detalle por zonas seleccionadas y referencias del universo semilla. Las áreas representadas son aproximaciones de lectura territorial: no constituyen límites oficiales, padrón de locales ni ranking gastronómico.",
        "El valor principal del informe es ofrecer una primera lectura ordenada sobre zonas, ejes y subzonas gastronómicas, diferenciando áreas con mayor reconocimiento territorial de aquellas que pueden profundizarse en próximas etapas de trabajo.",
    ]
    yy = y - 4
    for paragraph in paragraphs:
        yy = fase24.draw_wrapped(c, paragraph, fase24.M + 8, yy, fase24.W - 2 * fase24.M - 16, font_name=fase24.FONT, size=11.4, color=fase24.NEGRO, leading=16)
        yy -= 18
    fase24.note_box(
        c,
        fase24.M,
        142,
        fase24.W - 2 * fase24.M,
        104,
        "Lectura institucional",
        "La pieza está pensada como apoyo para conversación y ordenamiento territorial. La lectura de detalle se concentra en cinco zonas seleccionadas y mantiene el mapa global como referencia de conjunto.",
        border=fase24.VERDE,
        fill=fase24.SOFT_VERDE,
        size=9.2,
    )
    fase24.finish_page(c)


fase24.summary_page = summary_page_f25


def scope_page_f25(c: canvas.Canvas) -> None:
    y = fase24.page_header(c, 4, "Alcance y criterio de lectura", "Qué afirma y qué no afirma la pieza")
    fase24.note_box(
        c,
        fase24.M,
        y - 112,
        fase24.W - 2 * fase24.M,
        104,
        "Aclaración metodológica",
        "Este informe se construye a partir de un universo semilla de polos, ejes y menciones gastronómicas relevadas mediante fuentes abiertas, referencias territoriales y capas auxiliares de geolocalización. Las áreas representadas funcionan como herramienta de lectura territorial y no buscan fijar límites oficiales ni reemplazar padrones institucionales.",
        border=fase24.AZUL,
        fill=fase24.SOFT_AZUL,
        size=8.3,
    )
    fase24.note_box(
        c,
        fase24.M,
        y - 222,
        fase24.W - 2 * fase24.M,
        82,
        "Universo semilla",
        "El universo semilla es un insumo de trabajo. Las referencias del universo semilla no son ranking, no son recomendación comercial y no acreditan actividad vigente por sí mismas.",
        border=fase24.VERDE,
        fill=fase24.SOFT_VERDE,
        size=9.2,
    )
    fase24.note_box(
        c,
        fase24.M,
        y - 326,
        fase24.W - 2 * fase24.M,
        86,
        "Subzonas",
        "Las subzonas son aproximaciones editoriales construidas para facilitar la lectura territorial. No son límites oficiales, polígonos normativos ni delimitaciones cerradas.",
        border=fase24.ROJO,
        fill=fase24.SOFT_COBRE,
        size=9.2,
    )
    fase24.finish_page(c)


fase24.scope_page = scope_page_f25


def detail_page_f25(c: canvas.Canvas, page: int, maps: dict[str, Path]) -> None:
    cfg = fase24.DETAILS[page]
    fase24.page_header(c, page, cfg["title"], cfg["subtitle"])
    fase24.draw_image_fit(c, maps[cfg["key"]], fase24.M - 4, 308, fase24.W - 2 * fase24.M + 8, 394)
    box_w = (fase24.W - 2 * fase24.M - 14) / 2
    fase24.note_box(
        c,
        fase24.M,
        118,
        box_w,
        162,
        "Referencias del universo semilla",
        cfg["mentions"],
        border=fase24.CELESTE,
        fill=fase24.SOFT_AZUL,
        size=7.25,
    )
    fase24.note_box(
        c,
        fase24.M + box_w + 14,
        118,
        box_w,
        162,
        "Lectura territorial",
        cfg["reading"],
        border=fase24.VERDE,
        fill=fase24.SOFT_VERDE,
        size=7.8,
    )
    fase24.finish_page(c)


fase24.detail_page = detail_page_f25


def main() -> None:
    fase24.main()


if __name__ == "__main__":
    main()
