"""Genera mapas y graficos ejecutivos V3 para mercados gastronomicos (CABA).

Lee outputs/mercados_caba/sanitized/mercados_gastronomicos_activos_v3.csv y produce:
  - mapa_mercados_gastronomicos_v3.html (folium)
  - mapa_mercados_gastronomicos_v3.png  (matplotlib, esquematico)
  - grafico_tipo_mercado_v3.png / grafico_gestion_v3.png /
    grafico_comuna_barrio_v3.png / grafico_horarios_v3.png

Coordenadas APROXIMADAS por barrio (lugares publicos; para lectura territorial).
No expone place_id, telefonos, emails ni datos sensibles. No hace requests.
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = Path(__file__).resolve().parents[2]
SAN = REPO / "outputs" / "mercados_caba" / "sanitized"
ACT = SAN / "mercados_gastronomicos_activos_v3.csv"

# Ubicacion aproximada por barrio (lat, lon). Solo para visualizacion territorial.
COORDS = {
    "MG-0001": (-34.6211, -58.3731), "MG-0002": (-34.5618, -58.4565),
    "MG-0003": (-34.6193, -58.4413), "MG-0004": (-34.5970, -58.4380),
    "MG-0006": (-34.6118, -58.4392), "MG-0008": (-34.5882, -58.4360),
    "MG-0010": (-34.6360, -58.4010), "MG-0011": (-34.5460, -58.4090),
    "MG-0012": (-34.6180, -58.3540), "MG-0013": (-34.5990, -58.3920),
    "MG-0017": (-34.5910, -58.3790),
}
TIPO_COLOR = {
    "mercado_historico": "#8B0000", "food_hall": "#1f77b4",
    "patio_gastronomico": "#2ca02c", "mercado_de_productores": "#ff7f0e",
    "mercado_barrial_alimentario": "#9467bd", "feria_gastronomica": "#17becf",
}
TIPO_LABEL = {
    "mercado_historico": "Mercado historico", "food_hall": "Food hall",
    "patio_gastronomico": "Patio gastronomico", "mercado_de_productores": "Mercado de productores",
    "mercado_barrial_alimentario": "Barrial alimentario", "feria_gastronomica": "Feria itinerante",
}


def load():
    with ACT.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def _save(fig, name):
    fig.savefig(SAN / name, dpi=130, bbox_inches="tight")
    plt.close(fig)
    print("  ok:", name)


def bar(counter, title, name, color="#365f91"):
    items = counter.most_common()
    labels = [k for k, _ in items]
    vals = [v for _, v in items]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(range(len(vals)), vals, color=color)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=25, ha="right", fontsize=8)
    ax.set_title(title, fontsize=12, weight="bold")
    for i, v in enumerate(vals):
        ax.text(i, v + 0.05, str(v), ha="center", fontsize=9)
    ax.set_ylim(0, max(vals) + 1)
    ax.spines[["top", "right"]].set_visible(False)
    _save(fig, name)


def graficos(rows):
    bar(Counter(TIPO_LABEL.get(r["tipo"], r["tipo"]) for r in rows),
        "Mercados activos por tipo (13)", "grafico_tipo_mercado_v3.png")
    bar(Counter(r["gestion"].capitalize() for r in rows),
        "Mercados activos por gestion (13)", "grafico_gestion_v3.png", color="#2ca02c")
    bar(Counter(("Itinerante" if r["comuna"] == "0" else f"Comuna {r['comuna']}") for r in rows),
        "Mercados activos por comuna (13)", "grafico_comuna_barrio_v3.png", color="#8B5A00")
    freq = Counter()
    for r in rows:
        d = r["dias_apertura"].lower()
        if "fines de semana" in d:
            freq["Itinerante (fin de semana)"] += 1
        elif "todos los dias" in d or "domingo" in d and "lunes" in d:
            freq["Diaria / casi diaria"] += 1
        else:
            freq["Dias especificos"] += 1
    bar(freq, "Mercados activos por frecuencia de apertura (13)",
        "grafico_horarios_v3.png", color="#9467bd")


def mapa_png(rows):
    fig, ax = plt.subplots(figsize=(7.5, 7.5))
    seen = set()
    for r in rows:
        c = COORDS.get(r["id"])
        if not c:
            continue
        col = TIPO_COLOR.get(r["tipo"], "#555555")
        lbl = TIPO_LABEL.get(r["tipo"], r["tipo"])
        ax.scatter(c[1], c[0], c=col, s=90, edgecolors="black", linewidths=0.5,
                   label=lbl if lbl not in seen else None, zorder=3)
        seen.add(lbl)
        ax.annotate(r["nombre"].replace("Mercado ", "").replace("Patio ", "")[:18],
                    (c[1], c[0]), fontsize=6.5, xytext=(3, 3), textcoords="offset points")
    ax.set_title("Mapa territorial de mercados gastronomicos activos\n(ubicacion aproximada por barrio; itinerantes no mapeados)",
                 fontsize=11, weight="bold")
    ax.set_xlabel("Longitud"); ax.set_ylabel("Latitud")
    ax.legend(fontsize=7, loc="lower left", framealpha=0.9)
    ax.grid(True, ls=":", alpha=0.4)
    _save(fig, "mapa_mercados_gastronomicos_v3.png")


def mapa_html(rows):
    import folium
    m = folium.Map(location=[-34.605, -58.41], zoom_start=12, tiles="cartodbpositron")
    for r in rows:
        c = COORDS.get(r["id"])
        if not c:
            continue
        col = TIPO_COLOR.get(r["tipo"], "#555555")
        popup = f"<b>{r['nombre']}</b><br>{TIPO_LABEL.get(r['tipo'], r['tipo'])}<br>Gestion: {r['gestion']}<br>{r['barrio']} (Comuna {r['comuna']})<br>{r['horario_resumido']}"
        folium.CircleMarker(location=[c[0], c[1]], radius=8, color="black", weight=1,
                            fill=True, fill_color=col, fill_opacity=0.85,
                            popup=folium.Popup(popup, max_width=260),
                            tooltip=r["nombre"]).add_to(m)
    legend = "<div style='position:fixed;bottom:24px;left:24px;z-index:9999;background:white;padding:8px 10px;border:1px solid #999;border-radius:6px;font-size:12px'><b>Tipo de mercado</b><br>"
    for t, col in TIPO_COLOR.items():
        legend += f"<span style='color:{col}'>&#9679;</span> {TIPO_LABEL[t]}<br>"
    legend += "<i>Itinerantes (BA Market, Sabe la Tierra) no mapeados</i></div>"
    m.get_root().html.add_child(folium.Element(legend))
    out = SAN / "mapa_mercados_gastronomicos_v3.html"
    m.save(str(out))
    print("  ok:", out.name)


def main():
    rows = load()
    print(f"Activos leidos: {len(rows)}")
    graficos(rows)
    mapa_png(rows)
    mapa_html(rows)
    print("Visuales V3 generados en", SAN)


if __name__ == "__main__":
    main()
