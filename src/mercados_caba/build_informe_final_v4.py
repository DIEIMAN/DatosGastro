"""Genera el PDF DISENADO V4 (estilo DataGastro) del informe de mercados gastronomicos.

Usa ReportLab (no pandoc). Portada con banda oscura, KPI cards, cajas Respuesta /
Cuidado metodologico, graficos embebidos, footer institucional y numero de pagina.
Lee CSV V4 sanitizados. No expone datos sensibles. No hace requests.

Salidas:
  outputs/mercados_caba/sanitized/INFORME_FINAL_MERCADOS_GASTRONOMICOS_CABA_V4.pdf
  outputs/mercados_caba/sanitized/RESUMEN_EJECUTIVO_MERCADOS_GASTRONOMICOS_CABA_V4.pdf
"""
from __future__ import annotations

import csv
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                Image, PageBreak)

REPO = Path(__file__).resolve().parents[2]
SAN = REPO / "outputs" / "mercados_caba" / "sanitized"

INK = colors.HexColor("#1f3b5b")
INK2 = colors.HexColor("#365f91")
ORANGE = colors.HexColor("#e07b2e")
GREY = colors.HexColor("#6b7280")
RESP_BG = colors.HexColor("#eaf0f7")
CUID_BG = colors.HexColor("#fbeede")
LINEC = colors.HexColor("#d4d9e0")

FOOTER = "DataGastro · Mercados gastronómicos de CABA"


def S():
    ss = getSampleStyleSheet()
    ss.add(ParagraphStyle("H", parent=ss["Heading2"], textColor=INK, fontSize=13.5,
                          spaceBefore=12, spaceAfter=6))
    ss.add(ParagraphStyle("Body", parent=ss["BodyText"], fontSize=9.7, leading=13.5, spaceAfter=5))
    ss.add(ParagraphStyle("RespT", parent=ss["BodyText"], fontSize=9.7, leading=13.5,
                          textColor=colors.HexColor("#13283f")))
    ss.add(ParagraphStyle("CuidT", parent=ss["BodyText"], fontSize=8.8, leading=12,
                          textColor=colors.HexColor("#7a4410")))
    ss.add(ParagraphStyle("KpiN", parent=ss["BodyText"], fontSize=22, leading=24,
                          alignment=1, textColor=ORANGE))
    ss.add(ParagraphStyle("KpiL", parent=ss["BodyText"], fontSize=8.5, leading=10,
                          alignment=1, textColor=colors.white))
    ss.add(ParagraphStyle("Cell", parent=ss["BodyText"], fontSize=7.8, leading=9.5))
    ss.add(ParagraphStyle("CellH", parent=ss["BodyText"], fontSize=7.8, leading=9.5,
                          textColor=colors.white))
    return ss


def box(text, kind, ss):
    bg = RESP_BG if kind == "resp" else CUID_BG
    bar = INK2 if kind == "resp" else ORANGE
    st = ss["RespT"] if kind == "resp" else ss["CuidT"]
    pref = "<b>Respuesta:</b> " if kind == "resp" else "<b>Cuidado metodológico:</b> "
    t = Table([["", Paragraph(pref + text, st)]], colWidths=[0.18 * cm, None])
    t.setStyle(TableStyle([
        ("BACKGROUND", (1, 0), (1, 0), bg), ("BACKGROUND", (0, 0), (0, 0), bar),
        ("LEFTPADDING", (1, 0), (1, 0), 8), ("RIGHTPADDING", (1, 0), (1, 0), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t


def le_box(bullets, ss):
    items = "".join(f"<para spaceAfter='2'>• {b}</para>" for b in bullets)
    inner = [[Paragraph("<b>Lectura ejecutiva</b>", ss["RespT"])]]
    for b in bullets:
        inner.append([Paragraph("•&nbsp; " + b, ss["RespT"])])
    t = Table(inner, colWidths=[None])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f2f4f7")),
        ("LINEBEFORE", (0, 0), (0, -1), 2.2, INK2),
        ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    return t


def img(name, ss, maxw):
    p = SAN / name
    if not p.is_file():
        return Paragraph(f"[falta {name}]", ss["Body"])
    iw, ih = ImageReader(str(p)).getSize()
    w = min(maxw, iw)
    h = w * ih / iw
    if h > 11 * cm:
        h = 11 * cm
        w = h * iw / ih
    return Image(str(p), width=w, height=h)


def kpi_cards(ss, width):
    data = [("13", "mercados activos<br/>identificados"), ("11 + 2", "sede fija +<br/>itinerantes"),
            ("13", "multifuente<br/>(respaldo cruzado)"), ("12", "respaldo<br/>documental alto"),
            ("6", "comunas con<br/>presencia"), ("3", "relevantes no<br/>contabilizados")]
    cells = []
    for num, lab in data:
        inner = Table([[Paragraph(num, ss["KpiN"])], [Paragraph(lab, ss["KpiL"])]])
        inner.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), INK),
                                   ("TOPPADDING", (0, 0), (-1, -1), 6),
                                   ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
        cells.append(inner)
    rows = [cells[0:3], cells[3:6]]
    t = Table(rows, colWidths=[width / 3.0] * 3)
    t.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                           ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                           ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    return t


def final_table(ss, width):
    with (SAN / "mercados_gastronomicos_activos_v4.csv").open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    head = ["Nombre", "Tipo primario", "Gestión", "Barrio", "Com.", "Respaldo"]
    data = [[Paragraph(h, ss["CellH"]) for h in head]]
    for r in rows:
        tp = r["tipo_primario"].replace("_", " ")
        com = r["comuna"] if r["comuna"] != "0" else "itin."
        resp = r["nivel_respaldo_documental"].replace("_documental", "")
        data.append([Paragraph(x, ss["Cell"]) for x in
                     [r["nombre"], tp, r["gestion"], r["barrio"], com, resp]])
    t = Table(data, colWidths=[width * w for w in (0.30, 0.22, 0.12, 0.16, 0.08, 0.12)], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), INK), ("GRID", (0, 0), (-1, -1), 0.4, LINEC),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2f4f7")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]))
    return t


def _cover(c, doc, title, subtitle):
    w, h = A4
    c.setFillColor(INK)
    c.rect(0, h - 11 * cm, w, 11 * cm, fill=1, stroke=0)
    c.setFillColor(ORANGE)
    c.rect(0, h - 11 * cm, w, 0.28 * cm, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, h - 2.2 * cm, "DataGastro — Diagnóstico territorial gastronómico")
    c.setFont("Helvetica-Bold", 23)
    c.drawString(2 * cm, h - 4.2 * cm, title)
    c.setFont("Helvetica", 13)
    c.drawString(2 * cm, h - 5.5 * cm, subtitle)
    c.setFont("Helvetica", 11)
    c.drawString(2 * cm, h - 7.6 * cm, "Análisis y desarrollo: Diego Aleman")
    c.drawString(2 * cm, h - 8.3 * cm, "Versión V4 · 2026-06-24")
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Oblique", 9.5)
    c.drawString(2 * cm, h - 9.7 * cm, "Relevamiento documental y multifuente. No es censo ni padrón oficial.")
    _footer(c, doc)


def _footer(c, doc):
    w, _ = A4
    c.setStrokeColor(LINEC)
    c.line(2 * cm, 1.4 * cm, w - 2 * cm, 1.4 * cm)
    c.setFillColor(GREY)
    c.setFont("Helvetica", 8)
    c.drawString(2 * cm, 1.0 * cm, FOOTER)
    c.drawRightString(w - 2 * cm, 1.0 * cm, f"Pág. {doc.page}")


def build(out_name, title, subtitle, flow_builder):
    doc = SimpleDocTemplate(str(SAN / out_name), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                            topMargin=2 * cm, bottomMargin=1.8 * cm, title=title)
    ss = S()
    flow = [Spacer(1, 1), PageBreak()] + flow_builder(ss, doc.width)
    doc.build(flow, onFirstPage=lambda c, d: _cover(c, d, title, subtitle),
              onLaterPages=_footer)
    print(f"  PDF: {out_name} ({(SAN / out_name).stat().st_size} bytes)")


def informe_flow(ss, width):
    f = []
    _first = [True]

    def H(t):
        if not _first[0]:
            f.append(PageBreak())
        _first[0] = False
        f.append(Paragraph(t, ss["H"]))
    B = lambda t: f.append(Paragraph(t, ss["Body"]))
    R = lambda t: f.append(box(t, "resp", ss))
    C = lambda t: f.append(box(t, "cuid", ss))
    LE = lambda bs: (f.append(Spacer(1, 6)), f.append(le_box(bs, ss)))
    IM = lambda n: (f.append(Spacer(1, 4)), f.append(img(n, ss, width)), f.append(Spacer(1, 4)))
    sp = lambda: f.append(Spacer(1, 6))

    H("Resumen ejecutivo")
    f.append(kpi_cards(ss, width)); sp()
    R("La Ciudad cuenta con <b>13 mercados gastronómicos activos identificados</b> (11 de sede fija + 2 itinerantes), en 6 comunas, con gestión 3 pública / 5 privada / 5 mixta. Los 13 tienen respaldo multifuente y 12 respaldo documental alto.")
    C("“Identificados” no equivale a “confirmados en terreno”: es respaldo documental, no validación territorial.")

    H("¿Cómo se construyó el universo identificado?")
    R("Se integraron fuentes públicas oficiales (GCBA, Turismo BA), sitios propios, fuentes internas sanitizadas (DGDGAS, solo metadata), Google Places (señal operativa no oficial) y revisión documental con URL visible.")
    C("Los casos con señales contradictorias se excluyen del conteo activo hasta nueva validación; no se descartan, quedan documentados.")
    LE(["Cinco familias de fuente (oficial, sitio propio, interna, operativa y documental) se cruzan por mercado.",
        "El respaldo cruzado prioriza qué validar primero en terreno."])

    H("¿Cuántos mercados activos hay y de qué tipo?")
    R("13 activos identificados. Cada mercado tiene un tipo primario único, de modo que las categorías suman exactamente 13, sin doble conteo.")
    IM("grafico_tipo_primario_v4.png")
    C("“Itinerante” y “productores” se tratan como atributos, no como tipo, para no inflar el conteo.")

    H("¿Dónde están?")
    R("Presencia en 6 comunas, con concentración en la Comuna 1 (San Telmo, San Nicolás, Rodrigo Bueno, Gourmand) y en Caballito (Progreso, Lecheros).")
    IM("mapa_mercados_gastronomicos_v4.png")
    C("Coordenadas aproximadas por barrio; los itinerantes no se mapean por tener sede variable.")

    H("¿Quién los gestiona?")
    R("La oferta combina iniciativa privada (5), gestión mixta de concesión o economía social (5) y gestión pública del GCBA (3).")
    IM("grafico_gestion_v4.png")
    C("La gestión exacta de algunos casos mixtos se apoya en normativa pública y puede precisarse con el pliego.")

    H("¿Cuándo abren?")
    R("Conviven mercados de operación diaria o casi diaria, de días específicos e itinerantes de fin de semana.")
    IM("grafico_horarios_v4.png")
    C("11 de 13 tienen horario documentado; San Telmo presenta fuentes divergentes y los itinerantes dependen de la sede.")

    H("¿A quién apuntan?")
    R("Predominan los perfiles barrial y turístico/barrial, con un núcleo de consumo consciente (productores) y casos de fuerte perfil turístico.")
    IM("grafico_publicos_objetivo_v4.png")
    C("El perfil de público es una lectura cualitativa orientativa, no una medición de afluencia.")

    H("Casos patrimoniales y mercados con identidad histórica")
    R("Varios activos tienen identidad histórica, barrial o patrimonial documentada: Mercado de San Telmo (1897), Mercado de Belgrano (1891), Mercado del Progreso (1889), Mercado San Nicolás (centenario renovado) y Mercado Bonpland (economía social).")
    C("Se señalan por su trayectoria documentada; no es un ranking histórico exhaustivo.")
    LE(["Cuatro de los activos superan los 100 años de trayectoria documentada.",
        "El patrimonio histórico es un activo de valor turístico y de identidad barrial."])

    H("¿Qué espacios quedaron afuera y por qué?")
    R("Fuera del conteo activo (sin descartarse): 3 espacios relevantes no contabilizados por señales de cierre o falta de actividad reciente (Mercado Soho, Mercat Caballito, El Galpón); 1 cerrado documentado (Mercado de los Carruajes); y casos no gastronómicos / fuera de alcance (distritos, abasto barrial, pulgas, outlet).")
    C("No son errores; son categorías diferenciadas para no mezclar universos.")

    H("¿Qué decisión permite tomar este informe?")
    R("1) Priorizar circuitos turísticos gastronómicos. 2) Fortalecer mercados de productores y economía social. 3) Usar patios públicos como dinamizadores barriales. 4) Construir un registro unificado y actualizable de mercados gastronómicos.")
    C("Las decisiones que afectan estado operativo (casos en revisión) requieren validación territorial previa.")

    H("Referencias documentales visibles")
    R("Cada mercado se apoya en fuentes con URL visible (GCBA, Turismo BA, Argentina.gob.ar, sitios propios, prensa y Boletín Oficial). Detalle en referencias_documentales_visibles_v4.csv.")
    IM("grafico_respaldo_fuentes_v4.png")
    C("Aparecer en más de una fuente aumenta el respaldo documental, no prueba por sí solo la actividad actual.")

    H("Limitaciones y cuidado metodológico")
    B("Relevamiento documental; no reemplaza la validación territorial ni al registro oficial. Google Places es señal no oficial. Horarios autodeclarados y a veces divergentes. Coordenadas aproximadas por barrio. El respaldo documental alto/medio/básico no equivale a confianza territorial.")
    LE(["El próximo paso natural es la validación en terreno, empezando por los casos en revisión.",
        "Las cifras se expresan en orden de magnitud, sujetas a actualización."])

    H("Tabla final de mercados activos (13)")
    f.append(final_table(ss, width))

    H("Qué aporta la metodología DataGastro")
    B("Un método replicable —registro oficial + sitios propios + señal operativa + fuente interna + revisión documental— para mapear un rubro, distinguir tipologías, medir respaldo cruzado y separar con claridad activos, casos en revisión, cerrados y fuera de alcance. Base analítica candidata, no oficial.")
    LE(["El mismo método aplica a otros rubros gastronómicos de la Ciudad.",
        "Permite actualizar el padrón de forma periódica y trazable con DataGastro."])
    return f


def resumen_flow(ss, width):
    f = []
    H = lambda t: f.append(Paragraph(t, ss["H"]))
    B = lambda t: f.append(Paragraph(t, ss["Body"]))
    f.append(kpi_cards(ss, width)); f.append(Spacer(1, 8))
    H("El número")
    B("<b>13 mercados gastronómicos activos identificados</b>: 11 de sede fija + 2 itinerantes, en 6 comunas. Gestión: 3 públicos / 5 privados / 5 mixtos.")
    H("Tipos (suman 13)")
    B("Patios gastronómicos 4 · Mercados históricos 3 · Food halls 2 · Mercados de productores 2 · Barrial alimentario 1 · Feria gastronómica 1.")
    H("Horarios y públicos")
    B("Operación diaria, días específicos e itinerantes de fin de semana. Perfil barrial y turístico/barrial, con núcleo de consumo consciente (productores).")
    H("Respaldo documental")
    B("Los 13 son multifuente; 12 con respaldo documental alto y 1 medio. Es respaldo documental, no confianza territorial.")
    H("Oportunidades")
    B("1) Circuitos turísticos gastronómicos. 2) Mercados de productores y economía social. 3) Patios públicos como dinamizadores barriales. 4) Registro unificado y actualizable.")
    H("Aclaración")
    B("No se cuentan como activos: Mercado Soho, Mercat Caballito y El Galpón (señales de cierre / falta de actividad reciente, en revisión) ni el Mercado de los Carruajes (cerrado en 2025). Vuelven al conteo si se valida su actividad. No es censo ni padrón oficial.")
    return f


def main():
    build("INFORME_FINAL_MERCADOS_GASTRONOMICOS_CABA_V4.pdf",
          "Mercados gastronómicos de CABA", "Universo activo identificado y lectura territorial",
          informe_flow)
    build("RESUMEN_EJECUTIVO_MERCADOS_GASTRONOMICOS_CABA_V4.pdf",
          "Mercados gastronómicos de CABA", "Resumen ejecutivo", resumen_flow)


if __name__ == "__main__":
    main()
