# -*- coding: utf-8 -*-
"""Genera el informe ejecutivo de DataGastro en PDF con ReportLab.

Fuente principal de reproduccion del informe. Lee unicamente los outputs ya
generados por el pipeline (no recalcula metricas ni toca datos), produce las
figuras en outputs/informe/figures/ y arma el PDF en outputs/informe/.

Uso (desde la raiz del proyecto o desde scripts/):
    python scripts/generar_informe_pdf.py

Dependencias: ver requirements_informe.txt
"""
from __future__ import annotations

import json
import unicodedata
from datetime import date
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.cm as cmx
from matplotlib.patches import Polygon as MplPoly
from matplotlib.collections import PatchCollection
import pandas as pd

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
                                Image, Table, TableStyle, PageBreak, KeepTogether, NextPageTemplate)

# --------------------------------------------------------------------------- #
# Rutas relativas: detecta la raiz del proyecto (donde existe data/processed)
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parent
while not (ROOT / "data" / "processed").exists() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
PROC = ROOT / "data" / "processed"
ANALYTICS = ROOT / "data" / "analytics"
RAW = ROOT / "data" / "raw"
OUT_DIR = ROOT / "outputs" / "informe"
FIG_DIR = OUT_DIR / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

FECHA = "Junio de 2026"


def leer(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, keep_default_na=False) if Path(path).exists() else pd.DataFrame()


def miles(n) -> str:
    return f"{int(n):,}".replace(",", ".")


def norm(s) -> str:
    return unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().upper().strip()


# --------------------------------------------------------------------------- #
# Carga de outputs (no se recalcula nada: solo se leen)
# --------------------------------------------------------------------------- #
resumen = leer(ANALYTICS / "analytics_resumen_ejecutivo.csv")
hab_anio = leer(ANALYTICS / "analytics_habilitaciones_por_anio.csv")
hab_cat = leer(ANALYTICS / "analytics_habilitaciones_por_categoria.csv")
ubic = leer(PROC / "dim_ubicacion.csv")
fact_est = leer(PROC / "fact_establecimiento.csv")
fact_hab = leer(PROC / "fact_habilitacion_gastronomica.csv")
fact_esp = leer(PROC / "fact_espacio_feria_mercado.csv")


def ind(nombre: str) -> int:
    if resumen.empty or "indicador" not in resumen.columns:
        return 0
    fila = resumen[resumen["indicador"] == nombre]
    if fila.empty:
        return 0
    try:
        return int(float(fila.iloc[0]["valor"]))
    except Exception:
        return 0


# Cifras clave derivadas de los outputs
F01 = ind("establecimientos_oferta_gastronomica_f01")
F02 = ind("habilitaciones_gastronomicas_f02")
F02_GEO = ind("habilitaciones_f02_geocodificadas")
F02_GEO_PCT = round(F02_GEO / F02 * 100) if F02 else 0
F03 = ind("espacios_ferias_mercados_f03")
MERCADOS = ind("mercados_f03")
FERIAS = ind("ferias_f03")
FIAB = ind("fiab_f03")
F04 = ind("eventos_gastronomicos_reales_f04_aptos")
F05 = ind("programas_politicas_reales_f05_aptos")

# Serie comparable
_ha = hab_anio.copy()
if "comparable_como_flujo_anual" in _ha.columns:
    _ha["n"] = pd.to_numeric(_ha["cantidad_habilitaciones"], errors="coerce").fillna(0).astype(int)
    _comp = _ha[_ha["comparable_como_flujo_anual"] == "si"].sort_values("anio_fuente")
    SERIE_ANIOS = f"{_comp['anio_fuente'].iloc[0]}–{_comp['anio_fuente'].iloc[-1]}" if not _comp.empty else "2019–2024"
else:
    _comp = _ha
    SERIE_ANIOS = "2019–2024"

# Coordenadas para los mapas
ubic["lat"] = pd.to_numeric(ubic.get("latitud"), errors="coerce")
ubic["lon"] = pd.to_numeric(ubic.get("longitud"), errors="coerce")
_geo = ubic[["id_ubicacion", "lat", "lon"]].copy()
_geo["cg"] = ubic.get("calidad_geo", "")


def puntos(fact: pd.DataFrame, calidad: str) -> pd.DataFrame:
    if fact.empty:
        return pd.DataFrame(columns=["lat", "lon"])
    m = fact[["id_ubicacion"]].merge(_geo, on="id_ubicacion", how="left")
    return m[(m["cg"] == calidad) & m["lat"].notna()]


# Poligonos de barrios
def cargar_barrios():
    p = RAW / "geo_barrios.geojson"
    if not p.exists():
        return []
    feats = json.loads(p.read_text(encoding="utf-8")).get("features", [])
    out = []
    for f in feats:
        g = f["geometry"]
        coords = g["coordinates"]
        parts = coords if g["type"] == "Polygon" else [r for mp in coords for r in mp]
        out.append({"nombre": f["properties"].get("nombre", ""),
                    "area": float(f["properties"].get("area_metro", 0) or 0) / 1e6,
                    "rings": [[(pt[0], pt[1]) for pt in ring] for ring in parts]})
    return out


BARRIOS = cargar_barrios()


def _contorno(ax):
    ax.add_collection(PatchCollection([MplPoly(r, closed=True) for b in BARRIOS for r in b["rings"]],
                                      facecolor="#eef1f3", edgecolor="#c4ccd2", linewidths=0.5))


def _enc(ax, x=(-58.54, -58.33), y=(-34.71, -34.53)):
    ax.set_xlim(*x); ax.set_ylim(*y); ax.set_aspect(1 / 0.82); ax.set_xticks([]); ax.set_yticks([])


# --------------------------------------------------------------------------- #
# Generacion de figuras
# --------------------------------------------------------------------------- #
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.titlesize": 13, "axes.titleweight": "bold",
                     "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": "#888",
                     "figure.facecolor": "white", "axes.facecolor": "white"})


def fig_kpis():
    df = pd.DataFrame([
        ("Oferta registrada (F01)", F01, "#c0622d"),
        ("Habilitaciones aprobadas (F02)", F02, "#7d9b4e"),
        ("Espacios publicos (F03)", F03, "#2f8f6b"),
        ("Eventos verificados (F04)", F04, "#3a6ea5"),
        ("Programas vigentes (F05)", F05, "#8d5bb0"),
    ], columns=["k", "v", "c"]).sort_values("v")
    fig, ax = plt.subplots(figsize=(9.4, 3.9))
    b = ax.barh(df["k"], df["v"], color=df["c"])
    ax.set_xlabel("Cantidad de registros (cada barra es un universo distinto)")
    ax.set_title("Los numeros principales — no se suman entre si")
    for bar, v in zip(b, df["v"]):
        ax.text(v, bar.get_y() + bar.get_height() / 2, f"  {miles(v)}", va="center", fontsize=10, fontweight="bold")
    ax.margins(x=0.13); plt.tight_layout()
    fig.savefig(FIG_DIR / "01_kpis.png", dpi=150, bbox_inches="tight"); plt.close(fig)


def fig_mapa():
    f01p = puntos(fact_est, "fuente_oficial")
    f03p = puntos(fact_esp, "fuente_oficial")
    f02p = puntos(fact_hab, "usig_exacta")
    fig, (a, b) = plt.subplots(1, 2, figsize=(13, 6.6))
    for ax in (a, b):
        _contorno(ax); _enc(ax)
    a.scatter(f01p["lon"], f01p["lat"], s=6, c="#3a6ea5", alpha=0.55, linewidths=0, label=f"Oferta registrada ({miles(len(f01p))})")
    a.scatter(f03p["lon"], f03p["lat"], s=30, c="#2f8f6b", alpha=0.95, marker="^", linewidths=0, label=f"Ferias/mercados/FIAB ({miles(len(f03p))})")
    a.set_title("Oferta registrada y espacios publicos"); a.legend(loc="lower left", fontsize=8.5, framealpha=0.92)
    b.scatter(f02p["lon"], f02p["lat"], s=3.5, c="#c0622d", alpha=0.15, linewidths=0, label=f"Habilitaciones ubicadas ({miles(len(f02p))})")
    b.scatter(f01p["lon"], f01p["lat"], s=4.5, c="#3a6ea5", alpha=0.42, linewidths=0, label=f"Oferta registrada ({miles(len(f01p))})")
    b.set_title("Con habilitaciones aprobadas geolocalizadas"); b.legend(loc="lower left", fontsize=8.5, framealpha=0.92)
    plt.tight_layout(); fig.savefig(FIG_DIR / "02_mapa.png", dpi=150, bbox_inches="tight"); plt.close(fig)


def _corop(ax, val, tit, suf="", topn=7):
    mx = max(val.values()); nc = mcolors.PowerNorm(0.6, vmin=0, vmax=mx); cm = plt.colormaps["YlOrRd"]
    P, C, L = [], [], []
    for bb in BARRIOS:
        n = norm(bb["nombre"]); v = val.get(n, 0)
        for r in bb["rings"]:
            P.append(MplPoly(r, closed=True)); C.append(cm(nc(v)))
        if v > 0:
            pts = [p for r in bb["rings"] for p in r]
            L.append((sum(x for x, _ in pts) / len(pts), sum(y for _, y in pts) / len(pts), bb["nombre"], v))
    ax.add_collection(PatchCollection(P, facecolor=C, edgecolor="#999", linewidths=0.4)); _enc(ax); ax.set_title(tit)
    top = {n for n, _ in sorted(val.items(), key=lambda x: -x[1])[:topn]}
    for cx, cy, nm, v in L:
        if norm(nm) in top:
            ax.annotate(f"{nm}\n{int(round(v))}{suf}", (cx, cy), ha="center", va="center", fontsize=7.5,
                        fontweight="bold", bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.8))
    sm = cmx.ScalarMappable(norm=nc, cmap=cm); sm.set_array([]); return sm


def densidad_dicts():
    m = fact_est[["id_ubicacion"]].merge(ubic[["id_ubicacion", "barrio"]], on="id_ubicacion", how="left")
    m = m[~m["barrio"].isin(["No determinado", ""])]
    conteo = m["barrio"].map(norm).value_counts().to_dict()
    area = {norm(b["nombre"]): b["area"] for b in BARRIOS if b["area"] > 0}
    dens = {n: conteo[n] / area[n] for n in conteo if area.get(n)}
    return conteo, dens


def fig_densidad():
    conteo, dens = densidad_dicts()
    fig, (a, b) = plt.subplots(1, 2, figsize=(13, 6.6))
    s1 = _corop(a, conteo, "En cantidad absoluta")
    s2 = _corop(b, dens, "En densidad (por km²)", suf="/km²")
    fig.colorbar(s1, ax=a, fraction=0.04, pad=0.02).set_label("locales", fontsize=8)
    fig.colorbar(s2, ax=b, fraction=0.04, pad=0.02).set_label("locales/km²", fontsize=8)
    plt.tight_layout(); fig.savefig(FIG_DIR / "03_densidad.png", dpi=150, bbox_inches="tight"); plt.close(fig)


def fig_serie():
    comp = _comp.copy()
    fig, ax = plt.subplots(figsize=(9.4, 4.2))
    bars = ax.bar(comp["anio_fuente"].astype(str), comp["n"], color="#7d9b4e", width=0.6)
    md = comp["n"].mean()
    ax.axhline(md, color="#c0622d", ls="--", lw=1.4, label=f"Promedio: {miles(int(md))}")
    ax.set_title(f"Habilitaciones aprobadas por anio (serie comparable {SERIE_ANIOS})")
    ax.set_ylabel("Habilitaciones"); ax.legend(fontsize=9)
    for bar, v in zip(bars, comp["n"]):
        ax.annotate(miles(v), (bar.get_x() + bar.get_width() / 2, v), ha="center", va="bottom", fontsize=9, fontweight="bold")
    plt.tight_layout(); fig.savefig(FIG_DIR / "04_serie.png", dpi=150, bbox_inches="tight"); plt.close(fig)


def fig_categorias():
    cat = hab_cat.copy()
    cat["n"] = pd.to_numeric(cat["cantidad_habilitaciones"], errors="coerce").fillna(0).astype(int)
    cat = cat[cat["n"] > 0].sort_values("n")
    fig, ax = plt.subplots(figsize=(9.4, 5.2))
    bb = ax.barh(cat["categoria_gastronomica_inferida"], cat["n"], color="#3a6ea5")
    ax.set_title("Habilitaciones por tipo de gastronomia")
    ax.set_xlabel("Habilitaciones aprobadas (base F02 integrada)")
    for bar, v in zip(bb, cat["n"]):
        ax.text(v, bar.get_y() + bar.get_height() / 2, f"  {miles(v)}", va="center", fontsize=8.5)
    ax.margins(x=0.12); plt.tight_layout()
    fig.savefig(FIG_DIR / "05_categorias.png", dpi=150, bbox_inches="tight"); plt.close(fig)


def fig_espacios():
    t = fact_esp["tipo_espacio"].value_counts()
    fig, ax = plt.subplots(figsize=(9.4, 3.4))
    bb = ax.barh(t.index[::-1], t.values[::-1], color="#2f8f6b")
    ax.set_title("Espacios publicos de abastecimiento por tipo")
    ax.set_xlabel("Cantidad de espacios")
    for bar, v in zip(bb, t.values[::-1]):
        ax.text(v, bar.get_y() + bar.get_height() / 2, f"  {miles(v)}", va="center", fontsize=9)
    ax.margins(x=0.14); plt.tight_layout()
    fig.savefig(FIG_DIR / "06_espacios.png", dpi=150, bbox_inches="tight"); plt.close(fig)


def generar_figuras():
    fig_kpis(); fig_mapa(); fig_densidad(); fig_serie(); fig_categorias(); fig_espacios()
    print(f"Figuras generadas en {FIG_DIR}")


# --------------------------------------------------------------------------- #
# Estilos y PDF
# --------------------------------------------------------------------------- #
INK = colors.HexColor("#22384a"); INK2 = colors.HexColor("#37536b"); ACCENT = colors.HexColor("#c0622d")
SOFT = colors.HexColor("#eef1f3"); SOFT2 = colors.HexColor("#f6ede6"); GREY = colors.HexColor("#5b6b78")
LINE = colors.HexColor("#d4dbe0")
W, H = A4
styles = getSampleStyleSheet()


def _S(name, **kw):
    base = kw.pop("parent", styles["Normal"])
    return ParagraphStyle(name, parent=base, **kw)


body = _S("body", fontName="Helvetica", fontSize=10, leading=15, alignment=TA_JUSTIFY, textColor=colors.HexColor("#2b2b2b"), spaceAfter=6)
h1 = _S("h1", fontName="Helvetica-Bold", fontSize=16, leading=20, textColor=INK, spaceBefore=4, spaceAfter=8)
h2 = _S("h2", fontName="Helvetica-Bold", fontSize=12, leading=16, textColor=INK2, spaceBefore=10, spaceAfter=4)
kicker = _S("kicker", fontName="Helvetica-Bold", fontSize=8.5, leading=11, textColor=ACCENT, spaceAfter=2)
lead = _S("lead", parent=body, fontSize=10.5, leading=16, textColor=colors.HexColor("#3a3a3a"))
small = _S("small", fontName="Helvetica", fontSize=8, leading=11, textColor=GREY)
readingS = _S("reading", fontName="Helvetica", fontSize=9.5, leading=14, textColor=INK, alignment=TA_LEFT, leftIndent=8, rightIndent=8)
bullet = _S("bullet", parent=body, leftIndent=14, bulletIndent=4, spaceAfter=3)
qS = _S("q", fontName="Helvetica-Bold", fontSize=10.5, leading=14, textColor=INK2, spaceBefore=8, spaceAfter=2)
caption = _S("caption", fontName="Helvetica-Oblique", fontSize=8, leading=10, textColor=GREY, spaceAfter=10)
cellH = _S("cellH", fontName="Helvetica-Bold", fontSize=8.5, leading=11, textColor=colors.white)
cell = _S("cell", fontName="Helvetica", fontSize=8.2, leading=10.5, textColor=colors.HexColor("#2b2b2b"))


def reading(txt):
    t = Table([[Paragraph("<b>Lectura.</b> " + txt, readingS)]], colWidths=[165 * mm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), SOFT2), ("LEFTPADDING", (0, 0), (-1, -1), 10),
                           ("RIGHTPADDING", (0, 0), (-1, -1), 10), ("TOPPADDING", (0, 0), (-1, -1), 7),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 7), ("LINEBEFORE", (0, 0), (0, -1), 3, ACCENT)]))
    return t


def figure(name, w=165, cap=None):
    from PIL import Image as PILImage
    path = FIG_DIR / name
    iw, ih = PILImage.open(path).size
    width = w * mm; height = width * ih / iw
    items = [Image(str(path), width=width, height=height)]
    if cap:
        items.append(Paragraph(cap, caption))
    return KeepTogether(items)


def datos(fuente):
    return Paragraph("Datos: " + fuente, small)


def _P(txt, st):
    return Paragraph(txt.replace("\n", "<br/>"), st)


def construir_story():
    story = []

    def H1(kick, title):
        story.append(Spacer(1, 2)); story.append(Paragraph(kick, kicker)); story.append(Paragraph(title, h1))

    story.append(NextPageTemplate("content")); story.append(Spacer(1, 250)); story.append(PageBreak())

    # RESUMEN EJECUTIVO
    H1("INFORME EJECUTIVO", "Resumen ejecutivo")
    story.append(Paragraph(
        "DataGastro es un prototipo de base analitica que integra, en un unico modelo ordenado y trazable, la "
        "informacion publica dispersa sobre el sector gastronomico de la Ciudad de Buenos Aires. Reune cinco "
        "registros oficiales y relevamientos propios, y los mantiene separados porque cada uno mide una dimension "
        "distinta del mismo fenomeno.", lead))
    story.append(Spacer(1, 4)); story.append(Paragraph("Hallazgos principales", h2))
    for t in [
        f"<b>El sector formal esta documentado a gran escala:</b> {miles(F01)} locales en la guia oficial de oferta y "
        f"{miles(F02)} habilitaciones gastronomicas aprobadas integradas en la base, con serie comparable {SERIE_ANIOS} "
        f"y periodos no comparables (2015–2018 y 2025) identificados por separado.",
        f"<b>Por primera vez se puede observar, calle por calle, donde se aprueba actividad gastronomica formal:</b> el "
        f"{F02_GEO_PCT}% de las habilitaciones ({miles(F02_GEO)}) fue ubicado en el mapa con el sistema de "
        f"geolocalizacion oficial del Gobierno de la Ciudad, con una tasa exacta de geocodificacion cercana al 99% y "
        f"un control de consistencia territorial por comuna.",
        "<b>Volumen y concentracion no coinciden:</b> si se mide densidad de oferta registrada, San Nicolas y el "
        "centro historico aparecen como el nucleo de mayor intensidad territorial, mientras Palermo lidera en cantidad "
        "absoluta. Esta lectura surge de la oferta registrada, no de locales activos.",
        f"<b>La Ciudad gestiona {miles(F03)} espacios publicos de abastecimiento:</b> {MERCADOS} mercados, {FERIAS} "
        f"ferias y {FIAB} puntos de ferias itinerantes de abastecimiento barrial, distribuidos territorialmente en las "
        f"comunas de la Ciudad.",
        "<b>Todo el trabajo es trazable y validado:</b> cada numero informa su fuente, su fecha y sus limites; el "
        "proceso pasa 62 controles de calidad automaticos sin errores y 22 tests automaticos ejecutados correctamente.",
    ]:
        story.append(Paragraph("•  " + t, bullet))
    story.append(Spacer(1, 4))
    story.append(reading("La fortaleza del prototipo es metodologica: no inventa un numero unico del sector, sino que "
                         "ordena la evidencia disponible y deja explicito que se puede afirmar y que no. Eso lo hace "
                         "confiable como insumo de gestion."))
    story.append(PageBreak())

    # 1. QUE ES
    H1("OBJETIVO", "Que es DataGastro y para que sirve")
    story.append(Paragraph(
        "La Ciudad tiene un sector gastronomico muy activo, pero la informacion sobre ese sector vive dispersa en "
        "registros que nunca se habian integrado: una guia de oferta, un registro de habilitaciones, padrones de "
        "ferias y mercados, noticias de eventos, documentos de programas. Cada uno describe algo diferente.", body))
    story.append(Paragraph("DataGastro es un prototipo construido para resolver ese problema. No para producir un "
                           "numero unico que sume todo, sino para:", body))
    for t in ["Integrar las fuentes disponibles en un modelo de datos unico, reproducible y trazable.",
              "Separar correctamente los universos, de manera que cada cifra tenga una definicion clara y defendible.",
              "Convertir la informacion en insumos utiles para conversacion publica, planificacion territorial y diseno de politicas.",
              "Dejar en claro que se sabe, que no se sabe y con que fuente se sostiene cada afirmacion."]:
        story.append(Paragraph("•  " + t, bullet))
    story.append(Spacer(1, 6)); story.append(Paragraph("Preguntas que guiaron el trabajo", h2))
    story.append(Paragraph("El analisis se organizo alrededor de ocho preguntas concretas, respondidas al final de este informe:", body))
    for i, t in enumerate([
        "Donde se concentra la oferta gastronomica registrada?",
        "Que tipos de gastronomia predominan?",
        "Como evoluciono la actividad formal ano a ano?",
        "Donde, en terminos de calles y barrios, se aprueba actividad gastronomica formal?",
        "Que espacios publicos de abastecimiento existen y como se distribuyen?",
        "Que eventos y programas impulsa la Ciudad?",
        "Hay diferencia entre donde hay muchos locales y donde estan mas concentrados?",
        "Que no se puede responder con estos datos y por que?"], 1):
        story.append(Paragraph(f"<b>{i}.</b>  {t}", bullet))
    story.append(PageBreak())

    # 2. FUENTES
    H1("FUENTES", "Las cinco fuentes: que mide cada una")
    story.append(Paragraph(
        "El principal riesgo al trabajar con estos datos es mezclar universos y comunicar conclusiones que los datos "
        "no sostienen. El ejemplo mas comun seria sumar la oferta registrada con las habilitaciones aprobadas y hablar "
        "de “X establecimientos gastronomicos”: ese numero no existe, porque cada fuente describe algo distinto.", body))
    rows = [["Fuente", "Organismo de origen", "Que mide", "Que NO dice"],
            ["Oferta gastronomica\nregistrada (F01)", "Ente de Turismo\ndel GCBA", "Establecimientos publicados en la guia oficial de gastronomia", "No confirma si cada local sigue abierto hoy"],
            ["Habilitaciones\naprobadas (F02)", "Agencia Gubernamental\nde Control (AGC)", "Tramites de habilitacion aprobados por rubro gastronomico (recursos 2015–2025)", "No son locales activos ni registran cierres"],
            ["Ferias, mercados\ny FIAB (F03)", "Direccion General\nde Ferias del GCBA", "Espacios reales de abastecimiento publico", "No cuenta puestos ni personas, solo espacios"],
            ["Eventos\nrelevados (F04)", "Relevamiento propio\ncon fuente por fila", "Inventario trazable de eventos del sector", "No es el universo completo de eventos"],
            ["Programas y\npoliticas (F05)", "Relevamiento propio\ncon fuente por fila", "Catalogo institucional de programas vigentes", "No mide impacto, empleo ni presupuesto"]]
    data = [[_P(c, cellH) for c in rows[0]]] + [[_P(c, cell) for c in r] for r in rows[1:]]
    tb = Table(data, colWidths=[34 * mm, 33 * mm, 52 * mm, 46 * mm])
    tstyle = [("BACKGROUND", (0, 0), (-1, 0), INK), ("VALIGN", (0, 0), (-1, -1), "TOP"),
              ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
              ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7),
              ("LINEBELOW", (0, 0), (-1, -1), 0.5, LINE), ("LINEAFTER", (0, 0), (-2, -1), 0.5, LINE)]
    for i in range(1, len(rows)):
        if i % 2 == 0:
            tstyle.append(("BACKGROUND", (0, i), (-1, i), SOFT))
    tb.setStyle(TableStyle(tstyle))
    story.append(Spacer(1, 4)); story.append(tb); story.append(Spacer(1, 6))
    story.append(Paragraph("Una aclaracion tecnica importante", h2))
    story.append(Paragraph(
        "La cifra de habilitaciones surgio de un trabajo de depuracion cuidadoso. Una primera version del clasificador "
        "inflaba el total a 87.934 porque asignaba rubros gastronomicos a actividades como talabarteria o venta de "
        "productos envasados, que contienen palabras parecidas pero no son gastronomia de servicio. El clasificador "
        f"definitivo, por coincidencia exacta de terminos, llega a {miles(F02)} habilitaciones genuinamente "
        "gastronomicas, integradas desde los recursos anuales de la Agencia Gubernamental de Control.", body))
    story.append(PageBreak())

    # 3. NUMEROS
    H1("PANORAMA", "Los numeros principales, separados")
    story.append(datos("resumen analitico del proyecto sobre los registros oficiales del GCBA"))
    story.append(figure("01_kpis.png"))
    story.append(reading("Las habilitaciones tienen un volumen mucho mayor porque acumulan tramites desde 2015. La "
                         "oferta registrada es una guia estatica. Los espacios publicos son pocos pero geograficamente "
                         "relevantes. Eventos y programas son catalogos documentados, no estadisticas. Por eso ninguno "
                         "se suma con otro."))
    story.append(PageBreak())

    # 4. MAPA
    H1("TERRITORIO", "El mapa del ecosistema")
    story.append(Paragraph(
        "Las coordenadas de la oferta registrada y de los espacios publicos vienen directamente de las fuentes "
        "oficiales. Las de las habilitaciones se obtuvieron con el sistema de geolocalizacion del Gobierno de la "
        "Ciudad. Solo se muestran puntos con ubicacion validada.", body))
    story.append(figure("02_mapa.png",
                        cap="Izquierda: oferta registrada y espacios publicos. Derecha: sumando las habilitaciones aprobadas geolocalizadas."))
    story.append(reading("La actividad se concentra con fuerza en el corredor norte (Palermo, Recoleta, Belgrano) y el "
                         "centro historico (San Nicolas, Monserrat, San Telmo), y se afina hacia el sur. La capa de "
                         "habilitaciones geolocalizadas es la unica que permite observar, calle por calle, donde se "
                         "aprueba actividad formal. Son habilitaciones aprobadas, no locales activos."))
    story.append(PageBreak())

    # 5. DENSIDAD
    H1("TERRITORIO", "Donde se concentra? Volumen frente a densidad")
    story.append(Paragraph(
        "Hay un matiz que cambia la lectura sobre donde esta el nucleo de mayor intensidad. En cantidad absoluta, "
        "Palermo lidera; pero Palermo es muy extenso. Si se mide la densidad —locales por kilometro cuadrado— "
        "San Nicolas y el centro historico aparecen como las zonas de mayor concentracion. Esta lectura corresponde a "
        "la oferta registrada, no a locales activos.", body))
    story.append(figure("03_densidad.png",
                        cap="Misma fuente, dos lecturas. La densidad revela una concentracion territorial que el conteo absoluto no muestra."))
    story.append(reading("Palermo lidera en volumen, pero por su tamano la oferta queda diluida. Si se mide densidad de "
                         "oferta registrada, San Nicolas y el centro historico aparecen como el nucleo de mayor "
                         "intensidad territorial. La diferencia tiene implicancias concretas para uso del suelo, "
                         "gestion del transito y evaluacion de permisos de espacio publico."))
    story.append(PageBreak())

    # 6. SERIE
    H1("DINAMICA", "Cuanto se habilita por ano?")
    story.append(datos("Agencia Gubernamental de Control (AGC), registros publicados en datos abiertos"))
    story.append(Paragraph(
        "Una habilitacion aprobada es la autorizacion formal para operar un rubro en un domicilio: marca donde el "
        f"sector formal esta invirtiendo. El grafico muestra solo los anos comparables entre si ({SERIE_ANIOS}).", body))
    story.append(figure("04_serie.png"))
    story.append(reading(f"La serie comparable permite observar la dinamica anual del sector formal, con el impacto "
                         "visible de la pandemia en 2020 y la recuperacion posterior. Los periodos 2015–2018 "
                         "(consolidado en un solo archivo) y 2025 (esquema distinto, con disposiciones de varios anos) "
                         "se informan por separado para no falsear la comparacion, y por eso no se incluyen en este grafico."))
    story.append(PageBreak())

    # 7. CATEGORIAS
    H1("COMPOSICION", "Que tipo de gastronomia se habilita?")
    story.append(datos("Agencia Gubernamental de Control (AGC); categoria inferida del rubro declarado"))
    story.append(figure("05_categorias.png"))
    story.append(reading("La distribucion por categoria muestra que rubros concentran la mayor actividad formal sobre "
                         "el total integrado de la base. La venta de alimentos sin servicio de mesa se separo del "
                         "conteo gastronomico porque no representa el mismo tipo de actividad."))
    story.append(PageBreak())

    # 8. ESPACIOS
    H1("ABASTECIMIENTO", "Los espacios publicos de la Ciudad")
    story.append(datos("Direccion General de Ferias del GCBA y archivo oficial georreferenciado de ferias itinerantes"))
    story.append(Paragraph(
        "Este es el componente publico y territorial del ecosistema: los espacios que la Ciudad gestiona directamente "
        "para la comercializacion de alimentos. Se cuentan espacios reales (la feria como unidad), no los puestos "
        "individuales.", body))
    story.append(figure("06_espacios.png"))
    story.append(reading(f"Los {miles(F03)} espacios se reparten en mercados municipales (permanentes), ferias "
                         f"especializadas y {FIAB} puntos de ferias itinerantes de abastecimiento barrial, que rotan por "
                         "los barrios con productos frescos y basicos. Es la red de abastecimiento de proximidad de la "
                         "Ciudad, presente en las 15 comunas y distribuida de forma mas equilibrada que la oferta privada."))
    story.append(PageBreak())

    # 9. EVENTOS Y PROGRAMAS
    H1("INSTITUCIONAL", "Eventos y programas que impulsa la Ciudad")
    story.append(datos("relevamiento propio sobre comunicaciones oficiales del GCBA y normativa, con fuente por registro"))
    story.append(Paragraph(
        f"La dimension institucional del ecosistema: las acciones que el Gobierno de la Ciudad impulsa para el sector. "
        f"Se documentaron {F04} eventos verificados (festivales, ciclos de mercado, concursos, jornadas de descuentos) "
        f"y {F05} programas vigentes:", body))
    for t in ["<b>BA Capital Gastronomica</b> — programa marco de promocion del sector.",
              "<b>Distrito del Vino</b> — incentivos territoriales en la Comuna 11.",
              "<b>Bares Notables</b> — proteccion patrimonial de establecimientos historicos.",
              "<b>Permisos de area gastronomica</b> — regimen de mesas y sillas en la via publica."]:
        story.append(Paragraph("•  " + t, bullet))
    story.append(Paragraph(
        "Sobre el regimen de permisos de area gastronomica: esta identificado en el catalogo de programas, pero su "
        "dataset operativo (los permisos efectivamente otorgados y vigentes) todavia no esta integrado como fuente "
        "analitica del proyecto. Su incorporacion figura en la hoja de ruta.", body))
    story.append(reading("La Ciudad tiene una agenda gastronomica activa y diversa. Este es un inventario documentado "
                         "y trazable —cada registro tiene su fuente anotada— pero no un universo "
                         "estadisticamente completo."))
    story.append(PageBreak())

    # 10. PREGUNTAS
    H1("RESPUESTAS", "Que responde el analisis")
    qa = [
        ("Donde se concentra la oferta registrada?", "En el corredor norte (Palermo, Recoleta, Belgrano) y el centro historico (San Nicolas, Monserrat, San Telmo). Palermo tiene el mayor numero absoluto."),
        ("Que tipos de gastronomia predominan?", "Restaurantes, bares y confiterias, y locales de comida rapida concentran el grueso de las habilitaciones."),
        ("Como evoluciono la actividad formal?", f"La serie comparable {SERIE_ANIOS} muestra la dinamica anual, con la caida de 2020 por la pandemia y la recuperacion posterior. Los periodos 2015–2018 y 2025 se informan aparte por no ser comparables."),
        ("Donde se aprueba actividad formal, calle por calle?", f"El {F02_GEO_PCT}% de las habilitaciones fue geolocalizado con el sistema oficial del GCBA, con tasa exacta cercana al 99% y consistencia territorial por comuna. Las comunas del centro y el corredor norte concentran la mayor densidad."),
        ("Que espacios publicos existen y como se distribuyen?", f"{miles(F03)} espacios: {MERCADOS} mercados, {FERIAS} ferias y {FIAB} puntos de abastecimiento barrial, distribuidos territorialmente en las 15 comunas con criterio de proximidad."),
        ("Que impulsa la Ciudad en el sector?", f"{F04} eventos verificados y {F05} programas vigentes de promocion, incentivos territoriales, patrimonio y uso del espacio publico."),
        ("Hay diferencia entre cantidad y concentracion?", "Si. Si se mide densidad de oferta registrada, San Nicolas y el centro historico aparecen como el nucleo de mayor intensidad territorial, mientras Palermo lidera en cantidad absoluta."),
    ]
    for q, a in qa:
        story.append(Paragraph(q, qS)); story.append(Paragraph(a, body))
    story.append(Spacer(1, 4)); story.append(Paragraph("Que NO se puede responder todavia, y por que?", qS))
    for t in ["Cuantos locales estan <b>activos hoy</b>: no existe un padron con bajas actualizado.",
              "Cuantos <b>abrieron o cerraron</b> en terminos netos: las habilitaciones no registran bajas.",
              "El <b>impacto economico</b> del sector: empleo, ventas o facturacion.",
              "Si un barrio esta <b>saturado o subatendido</b>: falta un denominador de demanda.",
              "El <b>impacto de eventos o programas</b>: no hay metricas de resultado publicadas."]:
        story.append(Paragraph("•  " + t, bullet))
    story.append(Spacer(1, 3))
    story.append(reading("Esta honestidad sobre los limites es lo que hace confiable la base: cada afirmacion esta "
                         "respaldada, y las que no tienen respaldo no se hacen."))
    story.append(PageBreak())

    # 11. HOJA DE RUTA
    H1("HOJA DE RUTA", "Que falta y como se podria mejorar")
    story.append(Paragraph(
        "Un prototipo honesto tambien deja en claro que no puede responder todavia y como avanzar. Estas son las "
        "brechas principales y las acciones que las cubririan.", body))
    gaps = [["Brecha", "Por que importa", "Accion posible"],
            ["Sin padron de\nlocales activos", "No se sabe cuantos establecimientos siguen abiertos", "Incorporar el dataset operativo de permisos de area gastronomica (mesas y sillas): un permiso vigente puede funcionar como senal parcial de actividad actual en calle"],
            ["Las habilitaciones\nno registran cierres", "No representan aperturas netas del sector", "Solicitar el registro de bajas a la AGC"],
            ["Sin datos de empleo\no facturacion", "No se puede medir impacto economico", "Ministerio de Trabajo, AFIP, encuestas sectoriales"],
            ["Agenda de eventos\nsin estructura", "El inventario de eventos es parcial", "Colaboracion con Turismo y Cultura para un dataset actualizable"],
            ["Sin denominador\nde demanda", "No se puede saber si un barrio esta saturado", "Flujo peatonal, turismo y poblacion por zona"]]
    dataG = [[_P(c, cellH) for c in gaps[0]]] + [[_P(c, cell) for c in r] for r in gaps[1:]]
    tg = Table(dataG, colWidths=[40 * mm, 52 * mm, 73 * mm])
    gstyle = [("BACKGROUND", (0, 0), (-1, 0), ACCENT), ("VALIGN", (0, 0), (-1, -1), "TOP"),
              ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
              ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7),
              ("LINEBELOW", (0, 0), (-1, -1), 0.5, LINE), ("LINEAFTER", (0, 0), (-2, -1), 0.5, LINE)]
    for i in range(1, len(gaps)):
        if i % 2 == 0:
            gstyle.append(("BACKGROUND", (0, i), (-1, i), SOFT2))
    tg.setStyle(TableStyle(gstyle))
    story.append(Spacer(1, 4)); story.append(tg); story.append(Spacer(1, 10))
    story.append(Paragraph("Proximos pasos en orden de prioridad", h2))
    for t in ["<b>Incorporar el dataset operativo de permisos de area gastronomica</b> como senal parcial de actividad "
              "en calle: cubre la brecha mas importante, la ausencia de un padron de locales activos. No todos los "
              "locales tienen permiso de mesas y sillas, por lo que no seria un padron completo, sino una senal parcial.",
              "<b>Profundizar el analisis territorial</b> con herramientas de analisis de redes sobre los puntos "
              "geolocalizados, para detectar polos y corredores. Seria un modulo exploratorio, no un indicador oficial.",
              "<b>Mantener la base actualizada</b> reejecutando el proceso cuando las fuentes publiquen nuevos datos."]:
        story.append(Paragraph("•  " + t, bullet))
    story.append(Spacer(1, 8)); story.append(Paragraph("Estado actual del trabajo", h2))
    story.append(Paragraph(
        "El prototipo tiene hoy un proceso de datos completo y validado, de extremo a extremo: integracion de fuentes, "
        "limpieza, normalizacion, geolocalizacion y controles de calidad. Pasa 62 controles de calidad automaticos sin "
        "errores ni advertencias y 22 tests automaticos ejecutados correctamente, e incluye una herramienta interactiva "
        "de exploracion ademas de este informe. El proceso es reproducible: cuando las fuentes se actualicen, la base se "
        "reconstruye con la misma metodologia.", body))
    story.append(Spacer(1, 14))
    story.append(Paragraph("DataGastro · Datos abiertos del Gobierno de la Ciudad de Buenos Aires y relevamientos "
                           "trazables. Cada numero informa su fuente, su fecha y sus limites.", small))
    return story


def cover(c, doc):
    c.saveState()
    c.setFillColor(INK); c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(ACCENT); c.rect(0, H - 300, W, 8, fill=1, stroke=0)
    c.setFillColor(colors.white); c.setFont("Helvetica-Bold", 52); c.drawString(40 * mm, H - 150, "DataGastro")
    c.setFillColor(colors.HexColor("#d8e0e6")); c.setFont("Helvetica", 15.5)
    c.drawString(40 * mm, H - 172, "Prototipo de base analitica del ecosistema gastronomico")
    c.drawString(40 * mm, H - 191, "de la Ciudad de Buenos Aires")
    c.setStrokeColor(ACCENT); c.setLineWidth(2); c.line(40 * mm, H - 210, 40 * mm + 70 * mm, H - 210)
    c.setFillColor(colors.HexColor("#aebcc7")); c.setFont("Helvetica", 11)
    c.drawString(40 * mm, H - 235, "Informe de analisis · " + FECHA)
    c.setFillColor(colors.HexColor("#9fb0bd")); c.setFont("Helvetica", 9.5)
    for k, l in enumerate(["Integra cinco registros oficiales y relevamientos propios en un modelo unico y trazable.",
                           "Construido sobre datos abiertos del Gobierno de la Ciudad de Buenos Aires.",
                           "Cada fuente se mantiene separada: las cifras no se suman entre si."]):
        c.drawString(40 * mm, 120 - k * 16, "•  " + l)
    c.restoreState()


def later(c, doc):
    c.saveState()
    c.setFillColor(INK); c.rect(0, H - 18 * mm, W, 18 * mm, fill=1, stroke=0)
    c.setFillColor(colors.white); c.setFont("Helvetica-Bold", 10); c.drawString(20 * mm, H - 12 * mm, "DataGastro")
    c.setFillColor(colors.HexColor("#bcccd8")); c.setFont("Helvetica", 8)
    c.drawRightString(W - 20 * mm, H - 12 * mm, "Ecosistema gastronomico de la Ciudad de Buenos Aires")
    c.setStrokeColor(LINE); c.setLineWidth(0.5); c.line(20 * mm, 16 * mm, W - 20 * mm, 16 * mm)
    c.setFillColor(GREY); c.setFont("Helvetica", 8)
    c.drawString(20 * mm, 11 * mm, "Informe de analisis · " + FECHA)
    c.drawRightString(W - 20 * mm, 11 * mm, "Pagina %d" % (doc.page - 1))
    c.restoreState()


def generar_pdf():
    pdf_path = OUT_DIR / "DataGastro_Informe.pdf"
    frame_cover = Frame(0, 0, W, H, id="cover")
    frame_content = Frame(20 * mm, 18 * mm, W - 40 * mm, H - 18 * mm - 24 * mm, id="content")
    doc = BaseDocTemplate(str(pdf_path), pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm,
                          topMargin=24 * mm, bottomMargin=18 * mm,
                          title="DataGastro - Informe de analisis", author="DataGastro")
    doc.addPageTemplates([PageTemplate(id="cover", frames=[frame_cover], onPage=cover),
                          PageTemplate(id="content", frames=[frame_content], onPage=later)])
    doc.build(construir_story())
    print(f"PDF generado en {pdf_path}")


def main():
    print(f"Raiz del proyecto: {ROOT}")
    generar_figuras()
    generar_pdf()


if __name__ == "__main__":
    main()
