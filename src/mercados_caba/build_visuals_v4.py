"""Graficos y mapa V4 (estilo DataGastro) para mercados gastronomicos de CABA.

Lee los CSV V4 sanitizados y produce barras horizontales limpias + KPI cards + mapa.
Paleta: azul tinta base, naranja acento, grises suaves. No expone datos sensibles.
No hace requests.
"""
from __future__ import annotations

import csv
from collections import Counter, OrderedDict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

REPO = Path(__file__).resolve().parents[2]
SAN = REPO / "outputs" / "mercados_caba" / "sanitized"

INK = "#1f3b5b"
INK2 = "#365f91"
ORANGE = "#e07b2e"
GREY = "#8a93a0"
GREYBG = "#f2f4f7"

COORDS = {
    "MG-0001": (-34.6211, -58.3731), "MG-0002": (-34.5618, -58.4565),
    "MG-0013": (-34.5990, -58.3920), "MG-0003": (-34.6193, -58.4413),
    "MG-0004": (-34.5970, -58.4380), "MG-0017": (-34.5910, -58.3790),
    "MG-0006": (-34.6118, -58.4392), "MG-0010": (-34.6360, -58.4010),
    "MG-0011": (-34.5460, -58.4090), "MG-0012": (-34.6180, -58.3540),
    "MG-0008": (-34.5882, -58.4360),
}
TIPO_COLOR = {
    "mercado_historico": INK, "mercado_barrial_alimentario": "#9467bd",
    "food_hall": ORANGE, "patio_gastronomico": "#2e8b8b",
    "mercado_de_productores": "#6a8d2f", "feria_gastronomica": "#c2553f",
}
TIPO_LABEL = {
    "mercado_historico": "Mercado historico", "mercado_barrial_alimentario": "Barrial alimentario",
    "food_hall": "Food hall", "patio_gastronomico": "Patio gastronomico",
    "mercado_de_productores": "Mercado de productores", "feria_gastronomica": "Feria gastronomica",
}


def read(name):
    with (SAN / name).open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def _save(fig, name):
    fig.savefig(SAN / name, dpi=130, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("  ok:", name)


def hbar(pairs, title, name, accent_top=True):
    pairs = list(pairs)
    labels = [k for k, _ in pairs]
    vals = [v for _, v in pairs]
    order = sorted(range(len(vals)), key=lambda i: vals[i])
    labels = [labels[i] for i in order]
    vals = [vals[i] for i in order]
    colors = [INK2] * len(vals)
    if accent_top and vals:
        colors[-1] = ORANGE
    fig, ax = plt.subplots(figsize=(7.2, 0.55 * len(vals) + 1.2))
    ax.barh(range(len(vals)), vals, color=colors, height=0.62)
    ax.set_yticks(range(len(vals)))
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_title(title, fontsize=12, weight="bold", color=INK, loc="left", pad=10)
    for i, v in enumerate(vals):
        ax.text(v + max(vals) * 0.01, i, str(v), va="center", fontsize=9, weight="bold", color=INK)
    ax.set_xlim(0, max(vals) * 1.12)
    ax.spines[["top", "right", "bottom"]].set_visible(False)
    ax.tick_params(axis="x", length=0, labelbottom=False)
    ax.spines["left"].set_color(GREY)
    _save(fig, name)


def kpi_cards():
    cards = [
        ("13", "mercados activos\nidentificados"), ("11 + 2", "sede fija +\nitinerantes"),
        ("13", "multifuente\n(respaldo cruzado)"), ("12", "respaldo\ndocumental alto"),
        ("6", "comunas con\npresencia"), ("3", "espacios relevantes\nno contabilizados"),
    ]
    fig, axes = plt.subplots(2, 3, figsize=(9, 3.4))
    for ax, (num, lab) in zip(axes.ravel(), cards):
        ax.axis("off")
        ax.add_patch(FancyBboxPatch((0.04, 0.08), 0.92, 0.84, boxstyle="round,pad=0.02,rounding_size=0.06",
                                    linewidth=0, facecolor=INK, transform=ax.transAxes))
        ax.text(0.5, 0.62, num, ha="center", va="center", fontsize=26, weight="bold",
                color=ORANGE, transform=ax.transAxes)
        ax.text(0.5, 0.26, lab, ha="center", va="center", fontsize=10, color="white",
                transform=ax.transAxes)
    fig.suptitle("Mercados gastronomicos de CABA — indicadores clave",
                 fontsize=13, weight="bold", color=INK, x=0.06, ha="left")
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    _save(fig, "grafico_kpi_cards_v4.png")


def publico_bucket(s):
    s = s.lower()
    if "consciente" in s:
        return "Consumo consciente"
    if "turistico" in s and "barrial" in s:
        return "Turistico y barrial"
    if "turistico" in s:
        return "Turistico"
    if "mixto" in s:
        return "Mixto"
    return "Barrial"


def frecuencia_bucket(s):
    s = s.lower()
    if "fines de semana" in s:
        return "Itinerante (fin de semana)"
    if "todos los dias" in s or ("domingo" in s and "lunes" in s):
        return "Diaria / casi diaria"
    return "Dias especificos"


def graficos():
    act = read("mercados_gastronomicos_activos_v4.csv")
    tip = read("tipologias_mercados_v4.csv")
    resp = read("respaldo_fuentes_mercados_v4.csv")

    kpi_cards()
    tpairs = [(TIPO_LABEL.get(r["tipo_primario"], r["tipo_primario"]), int(r["cantidad"]))
              for r in tip if r["tipo_primario"].upper() != "TOTAL"]
    hbar(tpairs, "Mercados activos por tipo primario (suman 13)", "grafico_tipo_primario_v4.png")
    hbar(Counter(r["gestion"].capitalize() for r in act).items(),
         "Mercados activos por gestion", "grafico_gestion_v4.png")
    fcount = OrderedDict([
        ("Fuente oficial GCBA/Turismo", sum(r["fuente_oficial_gcba_turismo"] == "si" for r in resp)),
        ("Sitio propio", sum(r["sitio_propio"] == "si" for r in resp)),
        ("Google OPERATIONAL", sum(r["google_places_operational"] == "si" for r in resp)),
        ("Documental / prensa", sum(r["documental_prensa"] == "si" for r in resp)),
        ("Fuente interna sanitizada", sum(r["fuente_interna_sanitizada"] == "si" for r in resp)),
        ("Multifuente (>=2 tipos)", sum(r["es_multifuente"] == "si" for r in resp)),
    ])
    hbar(fcount.items(), "Respaldo documental por tipo de fuente", "grafico_respaldo_fuentes_v4.png")
    hbar(Counter(frecuencia_bucket(r["dias_apertura"]) for r in act).items(),
         "Mercados activos por frecuencia de apertura", "grafico_horarios_v4.png")
    hbar(Counter(publico_bucket(r["publico_objetivo"]) for r in act).items(),
         "Mercados activos por publico objetivo", "grafico_publicos_objetivo_v4.png")


ABBR = {
    "MG-0001": "San Telmo", "MG-0002": "Belgrano", "MG-0013": "San Nicolas",
    "MG-0003": "Mercado del Progreso", "MG-0004": "Mercat V. Crespo", "MG-0017": "Gourmand F.H.",
    "MG-0006": "P. de los Lecheros", "MG-0010": "Smart Plaza", "MG-0011": "P. Costanera Norte",
    "MG-0012": "P. Rodrigo Bueno", "MG-0008": "Bonpland",
}


def mapa_png():
    act = read("mercados_gastronomicos_activos_v4.csv")
    fig, ax = plt.subplots(figsize=(8.4, 8.0))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("#f7f9fb")
    seen = set()
    pts = [(r, COORDS[r["id"]]) for r in act if r["id"] in COORDS]
    lons = [c[1] for _, c in pts]
    lats = [c[0] for _, c in pts]
    padx = (max(lons) - min(lons)) * 0.22 + 0.004
    pady = (max(lats) - min(lats)) * 0.14 + 0.004
    ax.set_xlim(min(lons) - padx, max(lons) + padx * 1.4)
    ax.set_ylim(min(lats) - pady, max(lats) + pady)
    for r, c in pts:
        col = TIPO_COLOR.get(r["tipo_primario"], GREY)
        lbl = TIPO_LABEL.get(r["tipo_primario"], r["tipo_primario"])
        ax.scatter(c[1], c[0], c=col, s=200, edgecolors="white", linewidths=1.6,
                   label=lbl if lbl not in seen else None, zorder=3)
        seen.add(lbl)
        # etiqueta a la derecha del punto, con caja suave, sin recortes
        ax.annotate(ABBR.get(r["id"], r["nombre"]), (c[1], c[0]), fontsize=9, color=INK,
                    xytext=(9, 0), textcoords="offset points", va="center", ha="left",
                    zorder=4, clip_on=False,
                    bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="#e0e0e0", alpha=0.85))
    ax.set_title("Mapa esquemático territorial — mercados gastronómicos activos identificados",
                 fontsize=12.5, weight="bold", color=INK, loc="left", pad=24)
    ax.text(0.0, 1.025,
            "Esquema por ubicación aproximada de barrio (no es geolocalización exacta). "
            "Los itinerantes no se mapean por tener sede variable.",
            transform=ax.transAxes, fontsize=8.5, color=GREY)
    ax.set_xticks([]); ax.set_yticks([])
    leg = ax.legend(fontsize=8.5, loc="lower left", framealpha=0.95, title="Tipo primario")
    leg.get_title().set_color(INK); leg.get_title().set_fontweight("bold")
    for sp in ax.spines.values():
        sp.set_color("#e0e0e0")
    _save(fig, "mapa_mercados_gastronomicos_v4.png")


def mapa_html():
    import folium
    act = read("mercados_gastronomicos_activos_v4.csv")
    m = folium.Map(location=[-34.605, -58.41], zoom_start=12, tiles="cartodbpositron")
    for r in act:
        c = COORDS.get(r["id"])
        if not c:
            continue
        col = TIPO_COLOR.get(r["tipo_primario"], GREY)
        popup = f"<b>{r['nombre']}</b><br>{TIPO_LABEL.get(r['tipo_primario'], r['tipo_primario'])}<br>Gestion: {r['gestion']}<br>{r['barrio']} (Comuna {r['comuna']})<br>Respaldo: {r['nivel_respaldo_documental']}"
        folium.CircleMarker([c[0], c[1]], radius=8, color="white", weight=1.5, fill=True,
                            fill_color=col, fill_opacity=0.9, tooltip=r["nombre"],
                            popup=folium.Popup(popup, max_width=260)).add_to(m)
    leg = "<div style='position:fixed;bottom:24px;left:24px;z-index:9999;background:white;padding:8px 10px;border:1px solid #999;border-radius:6px;font-size:12px'><b>Tipo primario</b><br>"
    for t, col in TIPO_COLOR.items():
        leg += f"<span style='color:{col}'>&#9679;</span> {TIPO_LABEL[t]}<br>"
    leg += "<i>Itinerantes no mapeados (sede variable)</i></div>"
    m.get_root().html.add_child(folium.Element(leg))
    m.save(str(SAN / "mapa_mercados_gastronomicos_v4.html"))
    print("  ok: mapa_mercados_gastronomicos_v4.html")


def main():
    graficos()
    mapa_png()
    mapa_html()
    print("Visuales V4 generados.")


if __name__ == "__main__":
    main()
