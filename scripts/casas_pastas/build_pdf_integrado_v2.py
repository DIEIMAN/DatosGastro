"""Informe ejecutivo MEJORADO (V2) — Casas de pastas en CABA, padrón candidato integrado.

Versión institucional/visual, apta para compartir internamente. Usa SOLO agregados y mapas
anonimizados (sin nombres, direcciones, razón social, place_id, teléfonos, emails ni API key).

Fuentes (sin requests): padrón v2, resumen v2, auditoría de calidad, cobertura de cadenas y
fuentes históricas (CSV con respaldo). Regenera el geojson sanitizado desde el padrón v2.

Salidas:
  outputs/casas_pastas_reporte/INFORME_CASAS_PASTAS_INTEGRADO_V2.pdf
  outputs/casas_pastas_reporte/INFORME_CASAS_PASTAS_INTEGRADO_V2.md
  outputs/casas_pastas_reporte/integrado_sanitizado/mapa_puntos_sanitizado.geojson  (v2)
"""
from __future__ import annotations

import csv
import datetime as dt
import json
import textwrap
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
INT = ROOT / "outputs" / "casas_pastas_integrado"
REP = ROOT / "outputs" / "casas_pastas_reporte"
SAN = REP / "integrado_sanitizado"
GEO = ROOT / "data" / "raw"
PDF = REP / "INFORME_CASAS_PASTAS_INTEGRADO_V2.pdf"
MD = REP / "INFORME_CASAS_PASTAS_INTEGRADO_V2.md"

A4 = (8.27, 11.69)
AZUL = "#1f3b57"
AZUL2 = "#2c7fb8"
ROJO = "#c0392b"
GRIS = "#555555"
GRISCLARO = "#eef2f6"

CLASE_COLOR = {
    "A_integrado_multifuente": "#1a9850",
    "A_agc_oficial_estricto": "#2c7fb8",
    "A_google_probable": "#f08c00",
    "A_osm_auxiliar": "#7b5ea7",
    "B_revision_manual": "#999999",
}
CLASE_LABEL = {
    "A_integrado_multifuente": "Multifuente (≥2 fuentes)",
    "A_agc_oficial_estricto": "AGC oficial estricto",
    "A_google_probable": "Google (operativo no oficial)",
    "A_osm_auxiliar": "OpenStreetMap (auxiliar)",
    "B_revision_manual": "Revisión manual",
}
CADENA_CAPS = {
    "la juvenil": "LA JUVENIL", "multipasta": "MULTIPASTA", "caprizzi": "CAPRIZZI",
    "master pastas / pastas master": "MASTER PASTAS / PASTAS MASTER",
    "milena pastas artesanales": "MILENA PASTAS ARTESANALES",
    "pastas mazzeo": "PASTAS MAZZEO", "raviolon": "RAVIOLON", "biasatti": "BIASATTI",
    "pastas bayo": "PASTAS BAYO",
}


def read_csv(p):
    with p.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def kv(rows):
    return {r["indicador"]: r["valor"] for r in rows}


def fnum(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


# ---------- helpers de diseño ----------
def page(pdf):
    fig = plt.figure(figsize=A4)
    fig.patch.set_facecolor("white")
    return fig


def head(fig, kicker, titulo, subtitulo, num):
    fig.text(0.07, 0.955, kicker, color=GRIS, fontsize=8.5, fontweight="bold")
    fig.text(0.93, 0.955, num, color=GRIS, fontsize=8.5, ha="right")
    fig.text(0.07, 0.925, titulo, color=AZUL, fontsize=19, fontweight="bold", va="top")
    fig.lines.append(Line2D([0.07, 0.40], [0.905, 0.905], color=ROJO, lw=2.4, transform=fig.transFigure))
    if subtitulo:
        fig.text(0.07, 0.888, subtitulo, color=GRIS, fontsize=10.5, style="italic", va="top")


def bullets(fig, y0, items, size=10.5, gap=0.039, wrap=84, x=0.085):
    y = y0
    for it in items:
        lines = textwrap.wrap(it.strip(), wrap) or [""]
        fig.text(x, y, "•", fontsize=size, color=ROJO, va="top")
        for j, ln in enumerate(lines):
            fig.text(x + 0.022, y - j * 0.0225, ln, fontsize=size, color="#222222", va="top")
        y -= gap + (len(lines) - 1) * 0.0225
    return y


def cards(fig, y, items, h=0.11):
    n = len(items)
    w = 0.86 / n
    for i, (val, lab, col) in enumerate(items):
        x = 0.07 + i * w
        fig.patches.append(Rectangle((x + 0.008, y), w - 0.016, h, transform=fig.transFigure,
                                     facecolor=GRISCLARO, edgecolor=col, lw=1.6))
        fig.text(x + w / 2, y + h * 0.60, str(val), ha="center", fontsize=23,
                 fontweight="bold", color=col)
        fig.text(x + w / 2, y + h * 0.22, lab, ha="center", fontsize=8.5, color=GRIS)


def foot(fig, txt):
    fig.lines.append(Line2D([0.07, 0.93], [0.058, 0.058], color="#dddddd", lw=0.8, transform=fig.transFigure))
    fig.text(0.07, 0.045, txt, color=GRIS, fontsize=7.8, va="top")


def barh(fig, rect, labels, values, color, title, xlabel, valfmt="{:.0f}"):
    ax = fig.add_axes(rect)
    bars = ax.barh(labels, values, color=color)
    ax.set_title(title, color=AZUL, fontsize=11, loc="left", pad=6)
    ax.set_xlabel(xlabel, fontsize=8.5)
    ax.tick_params(labelsize=8.5)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    mx = max(values) if values else 1
    for b, v in zip(bars, values):
        ax.text(b.get_width() + mx * 0.01, b.get_y() + b.get_height() / 2,
                valfmt.format(v), va="center", fontsize=8, color=GRIS)
    ax.set_xlim(0, mx * 1.12)
    return ax


def poligonos(geom):
    if geom["type"] == "Polygon":
        rings = [geom["coordinates"][0]]
    elif geom["type"] == "MultiPolygon":
        rings = [poly[0] for poly in geom["coordinates"]]
    else:
        return []
    return [([c[0] for c in r], [c[1] for c in r]) for r in rings]


def main():
    hoy = dt.date.today().isoformat()
    rv2 = kv(read_csv(INT / "resumen_integrado_v2.csv"))
    rqc = kv(read_csv(INT / "auditoria_calidad" / "resumen_auditoria_calidad.csv"))
    cobertura = read_csv(SAN / "cobertura_cadenas_e_independientes.csv")
    hist = read_csv(REP / "fuentes_historicas_casas_pastas.csv")
    pad = read_csv(INT / "padron_candidato_integrado_v2.csv")

    gc = json.load((GEO / "geo_comunas.geojson").open(encoding="utf-8"))
    gb = json.load((GEO / "geo_barrios.geojson").open(encoding="utf-8"))
    acom = {str(f["properties"]["comuna"]): f["properties"]["area"] / 1e6 for f in gc["features"]}
    abar = {f["properties"]["nombre"].title(): f["properties"]["area_metro"] / 1e6 for f in gb["features"]}
    bar_poly = {f["properties"]["nombre"].title(): f["geometry"] for f in gb["features"]}

    # agregados desde v2
    com = Counter(r["comuna"] for r in pad if r["comuna"])
    bar = Counter(r["barrio"] for r in pad if r["barrio"])
    dens_com = sorted(((c, n, n / acom[c]) for c, n in com.items() if c in acom), key=lambda x: -x[2])
    dens_bar = sorted(((b, n, n / abar[b]) for b, n in bar.items() if b in abar), key=lambda x: -x[2])
    combos = Counter(r["fuentes_detectan"] for r in pad)

    # puntos anonimizados desde v2 (solo clase/comuna/barrio/geom) + geojson sanitizado v2
    pts = []
    feats = []
    for i, r in enumerate(pad, 1):
        la, lo = fnum(r["lat"]), fnum(r["lon"])
        if la is None or lo is None:
            continue
        p = {"lat": la, "lon": lo, "clase": r["clase_integrada"], "barrio": r["barrio"],
             "comuna": r["comuna"], "tipo": r["tipo_establecimiento"]}
        pts.append(p)
        feats.append({"type": "Feature", "geometry": {"type": "Point", "coordinates": [lo, la]},
                      "properties": {"id_anonimo": f"PT{i:04d}", "clasificacion_integrada": r["clase_integrada"],
                                     "es_cadena_detectada": r["es_cadena_detectada"], "comuna": r["comuna"],
                                     "barrio": r["barrio"]}})
    SAN.mkdir(parents=True, exist_ok=True)
    (SAN / "mapa_puntos_sanitizado.geojson").write_text(
        json.dumps({"type": "FeatureCollection", "features": feats}, ensure_ascii=False, indent=1),
        encoding="utf-8")

    n_tot, n_ind, n_cad = rv2["candidatos_unicos"], int(rv2["independientes"]), int(rv2["cadenas"])
    n_rev, n_multi = rv2["revision_manual_prioritaria"], rv2["multifuente"]

    def mapa_base(ax, puntos, comunas=True):
        if comunas:
            for f in gc["features"]:
                for xs, ys in poligonos(f["geometry"]):
                    ax.plot(xs, ys, color="#cfcfcf", lw=0.6, zorder=1)
        for p in puntos:
            ax.scatter(p["lon"], p["lat"], s=15, color=CLASE_COLOR.get(p["clase"], "#999"),
                       edgecolor="white", lw=0.25, zorder=3)
        ax.set_aspect(1.28)
        ax.axis("off")

    def leyenda(ax):
        leg = [Line2D([0], [0], marker="o", color="w", markerfacecolor=c, markersize=8, label=CLASE_LABEL[k])
               for k, c in CLASE_COLOR.items()]
        ax.legend(handles=leg, loc="lower left", fontsize=7.5, frameon=False)

    with PdfPages(PDF) as pdf:
        # ---- 1. Portada ----
        fig = page(pdf)
        fig.patches.append(Rectangle((0, 0.74), 1, 0.26, transform=fig.transFigure, facecolor=AZUL, zorder=0))
        fig.text(0.07, 0.90, "DATAGASTRO · DIAGNÓSTICO TERRITORIAL", color="#cdd9e5", fontsize=10, fontweight="bold")
        fig.text(0.07, 0.815, "Casas de pastas en la\nCiudad de Buenos Aires", color="white",
                 fontsize=27, fontweight="bold", va="center")
        fig.text(0.07, 0.66, "Registro oficial, fuentes abiertas y padrón candidato integrado",
                 fontsize=14, color=AZUL)
        fig.lines.append(Line2D([0.07, 0.55], [0.625, 0.625], color=ROJO, lw=2.5, transform=fig.transFigure))
        cards(fig, 0.45, [(n_tot, "candidatos únicos", AZUL), (n_ind, "independientes", "#1a9850"),
                          (n_cad, "en cadenas", "#c0762b"), (n_rev, "revisión manual", GRIS)], h=0.12)
        fig.text(0.07, 0.34,
                 "Padrón candidato integrado (v2) que combina el registro administrativo oficial (AGC / F02),\n"
                 "el relevamiento abierto auxiliar (OpenStreetMap) y una señal operativa no oficial\n"
                 "(Google Places API). No reemplaza al registro oficial ni constituye un censo definitivo:\n"
                 "es una base analítica, no oficial, pendiente de validación manual.",
                 fontsize=11, color="#333333", va="top")
        fig.text(0.07, 0.13, f"Fecha: {hoy}    ·    Versión: V2 (ejecutiva)", fontsize=10, color=GRIS)
        fig.text(0.07, 0.105, "Documento interno · agregados y mapas anonimizados · sin datos personales",
                 fontsize=9, color=GRIS)
        pdf.savefig(fig); plt.close(fig)

        # ---- 2. Resumen ejecutivo ----
        fig = page(pdf)
        head(fig, "CASAS DE PASTAS EN CABA", "Resumen ejecutivo",
             "El número oficial es angosto; el universo operativo probable es más amplio.", "2 / 18")
        cards(fig, 0.74, [(n_tot, "candidatos únicos", AZUL), (n_ind, "independientes", "#1a9850"),
                          (n_cad, "en cadenas", "#c0762b"), (n_multi, "multifuente", "#1a9850"),
                          (n_rev, "revisión manual", GRIS)], h=0.11)
        bullets(fig, 0.66, [
            f"Se construyó un padrón candidato integrado de {n_tot} posibles casas de pastas en CABA, "
            "combinando registro oficial, fuentes abiertas y señales operativas no oficiales.",
            "No reemplaza al registro oficial ni constituye un censo definitivo: es una base analítica "
            "para validación territorial.",
            f"La mayor parte del padrón son casas independientes o de escala barrial ({n_ind} de {n_tot}); "
            f"{n_cad} pertenecen a cadenas reconocidas, usadas para control de cobertura.",
            f"{n_multi} candidatos aparecen en más de una fuente: son el núcleo de mayor confianza.",
            "El registro administrativo oficial (AGC / F02) aporta 11 habilitaciones estrictas, que no "
            "implican local activo.",
            f"{n_rev} casos quedan pendientes de validación manual; forman parte del control de calidad, "
            "no son un error.",
        ])
        foot(fig, "Padrón candidato no oficial · pendiente de validación manual. Total 261 · independientes 180 · cadenas 81.")
        pdf.savefig(fig); plt.close(fig)

        # ---- 3. Hallazgo principal ----
        fig = page(pdf)
        head(fig, "HALLAZGO PRINCIPAL", "Registro oficial vs. universo operativo probable",
             "El registro oficial muestra el núcleo estricto; el padrón candidato amplía la lectura.", "3 / 18")
        ax = fig.add_axes([0.12, 0.42, 0.74, 0.34])
        vals = [11, n_multi if isinstance(n_multi, int) else int(n_multi), int(n_tot)]
        labels = ["AGC oficial\nestricto", "Núcleo\nmultifuente", "Padrón candidato\nintegrado"]
        colors = [AZUL2, "#1a9850", AZUL]
        b = ax.bar(labels, [11, int(n_multi), int(n_tot)], color=colors, width=0.6)
        for bi, v in zip(b, [11, int(n_multi), int(n_tot)]):
            ax.text(bi.get_x() + bi.get_width() / 2, v + 4, str(v), ha="center", fontweight="bold", color=AZUL)
        ax.set_ylim(0, int(n_tot) * 1.15)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.set_ylabel("candidatos / registros", fontsize=9)
        bullets(fig, 0.33, [
            "El registro administrativo oficial (AGC / F02) identifica un núcleo estricto de 11 "
            "habilitaciones de elaboración de pastas: es preciso pero angosto, y no implica local activo.",
            f"El padrón candidato integrado eleva la lectura a {n_tot} establecimientos posibles al sumar "
            "fuentes abiertas (OpenStreetMap) y operativas (Google Places).",
            "La diferencia no es un error: refleja distintas fuentes y definiciones. El número oficial es "
            "el piso; el universo operativo probable es mayor y queda pendiente de validación.",
        ])
        foot(fig, "AGC = registro administrativo oficial · OSM = fuente abierta auxiliar · Google = señal operativa no oficial.")
        pdf.savefig(fig); plt.close(fig)

        # ---- 4. Fuentes y capas ----
        fig = page(pdf)
        head(fig, "METODOLOGÍA", "Fuentes y capas del análisis",
             "Qué puede y qué no puede afirmar cada fuente.", "4 / 18")
        ax = fig.add_axes([0.07, 0.58, 0.86, 0.26]); ax.axis("off")
        data = [
            ["AGC / F02", "Registro oficial", "11", "Habilitaciones; NO implica local activo"],
            ["OpenStreetMap", "Abierta auxiliar", "152", "Cobertura territorial; no oficial"],
            ["Google Places", "Operativa no oficial", "151", "Visibilidad comercial; no gubernamental"],
            ["Integrado v2", "Padrón candidato", str(n_tot), "Unión deduplicada; a validar"],
        ]
        t = ax.table(cellText=data, colLabels=["Fuente", "Naturaleza", "Detectados", "Qué puede / no puede afirmar"],
                     colWidths=[0.18, 0.20, 0.15, 0.47], loc="upper center", cellLoc="center")
        t.auto_set_font_size(False); t.set_fontsize(9); t.scale(1, 1.6)
        for (r, _c), cell in t.get_celld().items():
            cell.set_edgecolor("#dddddd")
            if r == 0:
                cell.set_facecolor(AZUL); cell.set_text_props(color="white", fontweight="bold")
            elif r % 2 == 0:
                cell.set_facecolor(GRISCLARO)
        fig.text(0.07, 0.55, "Detectados por fuente dentro del padrón integrado post-deduplicación; "
                 "no equivale a resultados brutos.", fontsize=8.5, color=GRIS, style="italic")
        bullets(fig, 0.49, [
            "Ninguna fuente sola alcanza el universo real: AGC es preciso pero angosto; OSM y Google amplían "
            "cobertura pero no son oficiales.",
            "Aparecer en más de una fuente sube la confianza (clase multifuente). Aparecer en una sola se "
            "conserva como candidato, sin degradar a los independientes.",
            "El padrón es candidato: el número final requiere validación manual antes de presentarse como definitivo.",
        ])
        foot(fig, "AGC / F02 · OpenStreetMap · Google Places API. Padrón candidato no oficial.")
        pdf.savefig(fig); plt.close(fig)

        # ---- 5. Mapa general ----
        fig = page(pdf)
        head(fig, "CARTOGRAFÍA", "Mapa general de CABA",
             "Distribución del padrón candidato por clase integrada (anonimizado).", "5 / 18")
        ax = fig.add_axes([0.06, 0.12, 0.88, 0.74])
        mapa_base(ax, pts)
        leyenda(ax)
        foot(fig, "Puntos del padrón candidato integrado, sin nombres, direcciones ni identificadores. "
                  "Contornos: comunas GCBA.")
        pdf.savefig(fig); plt.close(fig)

        # ---- 6. Distribución por comuna ----
        fig = page(pdf)
        head(fig, "DISTRIBUCIÓN", "Comunas con mayor concentración",
             "Comunas 14 y 13 lideran en cantidad absoluta de candidatos.", "6 / 18")
        topc = com.most_common(12)[::-1]
        barh(fig, [0.16, 0.16, 0.74, 0.66], [f"Comuna {c}" for c, _ in topc], [n for _, n in topc],
             AZUL2, "Candidatos por comuna (v2)", "candidatos")
        foot(fig, "Incluye cadenas e independientes. Padrón candidato no oficial.")
        pdf.savefig(fig); plt.close(fig)

        # ---- 7. Distribución por barrio ----
        fig = page(pdf)
        head(fig, "DISTRIBUCIÓN", "Barrios con más casas de pastas candidatas",
             "Palermo, Caballito, Recoleta, Belgrano y Villa Urquiza encabezan el ranking.", "7 / 18")
        topb = bar.most_common(12)[::-1]
        barh(fig, [0.22, 0.16, 0.70, 0.66], [b for b, _ in topb], [n for _, n in topb],
             "#7b5ea7", "Candidatos por barrio (v2)", "candidatos")
        foot(fig, "Cantidad absoluta; la densidad por km² (pág. 8) mide algo distinto.")
        pdf.savefig(fig); plt.close(fig)

        # ---- 8. Densidad ----
        fig = page(pdf)
        head(fig, "INTENSIDAD TERRITORIAL", "Densidad por km²",
             "Cantidad absoluta y densidad no miden lo mismo: un barrio chico puede ser muy denso.", "8 / 18")
        dc = dens_com[:8][::-1]
        barh(fig, [0.16, 0.57, 0.74, 0.30], [f"Comuna {c}" for c, _, _ in dc], [d for _, _, d in dc],
             "#31a354", "Densidad por comuna (candidatos/km²)", "candidatos/km²", valfmt="{:.2f}")
        db = dens_bar[:8][::-1]
        barh(fig, [0.22, 0.14, 0.68, 0.30], [b for b, _, _ in db], [d for _, _, d in db],
             "#dd8452", "Densidad por barrio (candidatos/km²)", "candidatos/km²", valfmt="{:.2f}")
        foot(fig, "Densidad = candidatos / área oficial km² (geometrías GCBA). NO es densidad por habitante "
                  "(falta dataset de población).")
        pdf.savefig(fig); plt.close(fig)

        # ---- 9-11. Zoom barrios ----
        zooms = [("Palermo", "9 / 18", "Mayor concentración absoluta de la Ciudad; oferta repartida entre cadenas e independientes."),
                 ("Caballito", "10 / 18", "Fuerte presencia de casas de barrio; densidad alta en una superficie media."),
                 ("Recoleta", "11 / 18", "Empata con Belgrano (22 candidatos c/u); se muestra Recoleta. Densidad elevada por su superficie acotada.")]
        for barrio, num, coment in zooms:
            fig = page(pdf)
            cnt = bar.get(barrio, 0)
            head(fig, "ZOOM TERRITORIAL", f"Zoom: {barrio}",
                 f"{cnt} candidatos en {barrio} (padrón v2, anonimizado).", num)
            ax = fig.add_axes([0.08, 0.20, 0.84, 0.62])
            geom = bar_poly.get(barrio)
            xs_all, ys_all = [], []
            if geom:
                for xs, ys in poligonos(geom):
                    ax.plot(xs, ys, color="#bbbbbb", lw=1.0)
                    ax.fill(xs, ys, color="#f7f9fb", zorder=0)
                    xs_all += xs; ys_all += ys
            bp = [p for p in pts if p["barrio"] == barrio]
            for p in bp:
                ax.scatter(p["lon"], p["lat"], s=34, color=CLASE_COLOR.get(p["clase"], "#999"),
                           edgecolor="white", lw=0.4, zorder=3)
            if xs_all:
                mx = (max(xs_all) - min(xs_all)) * 0.08; my = (max(ys_all) - min(ys_all)) * 0.08
                ax.set_xlim(min(xs_all) - mx, max(xs_all) + mx)
                ax.set_ylim(min(ys_all) - my, max(ys_all) + my)
            ax.set_aspect(1.28); ax.axis("off")
            leyenda(ax)
            fig.text(0.07, 0.16, coment, fontsize=10.5, color="#222222", style="italic", va="top",
                     wrap=True)
            foot(fig, "Solo puntos anonimizados dentro del barrio. Sin nombres ni direcciones.")
            pdf.savefig(fig); plt.close(fig)

        # ---- 12. Cadenas e independientes ----
        fig = page(pdf)
        head(fig, "ESTRUCTURA DEL UNIVERSO", "Cadenas e independientes",
             "El foco no son las franquicias: la mayor parte son casas independientes.", "12 / 18")
        bullets(fig, 0.84, [
            "El informe no describe únicamente cadenas: la mayor parte del padrón candidato corresponde a "
            f"casas independientes o de escala barrial ({n_ind} de {n_tot}).",
            f"{n_cad} establecimientos pertenecen a cadenas reconocidas, que se reportan como control de "
            "cobertura, no como foco comercial.",
            "La auditoría no detectó inflación de cadenas: los conteos son unión legítima de fuentes.",
        ], gap=0.044)
        top_cad = [(CADENA_CAPS.get(r["cadena"], r["cadena"].upper()), int(r["sucursales"])) for r in cobertura][:8][::-1]
        barh(fig, [0.34, 0.14, 0.56, 0.42], [c for c, _ in top_cad], [n for _, n in top_cad],
             "#c0762b", "Cadenas con más sucursales (control de cobertura)", "sucursales")
        foot(fig, "Cadenas como referencia de cobertura. No se incluyen categorías genéricas (p. ej. 'pastas frescas').")
        pdf.savefig(fig); plt.close(fig)

        # ---- 13. Núcleo multifuente ----
        fig = page(pdf)
        head(fig, "CONFIANZA", "Núcleo multifuente",
             "Los candidatos detectados por más de una fuente son la base más sólida.", "13 / 18")
        orden = ["agc", "google", "osm", "google+osm"]
        etq = {"agc": "Solo AGC (oficial)", "google": "Solo Google", "osm": "Solo OSM",
               "google+osm": "Google + OSM (multifuente)"}
        vals = [(etq[k], combos.get(k, 0)) for k in orden]
        barh(fig, [0.30, 0.50, 0.60, 0.30], [e for e, _ in vals][::-1], [v for _, v in vals][::-1],
             "#1a9850", "Candidatos por combinación de fuentes", "candidatos")
        bullets(fig, 0.40, [
            f"{n_multi} candidatos aparecen en más de una fuente (Google + OSM): se clasifican como "
            "multifuente y constituyen el núcleo de mayor confianza.",
            "Los detectados por una sola fuente se conservan como candidatos (operativo no oficial si es "
            "Google, auxiliar si es OSM, oficial estricto si es AGC), sin degradarlos.",
            "Para la validación manual conviene empezar por el núcleo multifuente y por los independientes "
            "de barrios con mayor concentración.",
        ])
        foot(fig, "Multifuente = mayor confianza. AGC oficial estricto no implica local activo.")
        pdf.savefig(fig); plt.close(fig)

        # ---- 14. Revisión manual y control de calidad ----
        fig = page(pdf)
        head(fig, "CONTROL DE CALIDAD", "Revisión manual y control de calidad",
             "Los casos pendientes son parte del proceso, no un error.", "14 / 18")
        bullets(fig, 0.84, [
            f"{n_rev} casos quedan en revisión manual: dudosos o posibles faltantes que no se descartan ni "
            "se promueven automáticamente.",
            "Auditoría de cadenas: 11 cadenas revisadas, sin alertas de inflación. La Juvenil (28 sucursales) "
            "es unión legítima de fuentes (19 por Google, 19 por OSM, 10 en común), no duplicados.",
            "Posibles duplicados revisados: 2 pares; al inspeccionarlos resultaron locales distintos. "
            "Falsas fusiones: 0.",
            "4 casos marcados para revisar fusión se resolvieron: 2 duplicados fusionados, 1 descartado "
            "(bodegón), 1 mantenido en revisión.",
            "Los nombres genéricos (p. ej. 'pastas frescas', 'pastificio') se reclasificaron como "
            "independientes, no como cadenas.",
            "El número definitivo se establecerá recién tras la validación manual.",
        ], gap=0.042)
        foot(fig, "El padrón candidato quedó cerrado en v2 tras la auditoría de calidad.")
        pdf.savefig(fig); plt.close(fig)

        # ---- 15. Limitaciones ----
        fig = page(pdf)
        head(fig, "ALCANCE", "Limitaciones", "Qué no afirma este informe.", "15 / 18")
        bullets(fig, 0.84, [
            "No es un censo definitivo ni un padrón oficial de casas de pastas: es un padrón candidato.",
            "Google Places y OpenStreetMap no son fuentes oficiales; reflejan visibilidad comercial y "
            "relevamiento colaborativo, no un registro gubernamental.",
            "AGC es oficial pero angosto: mide habilitaciones de un rubro estricto y no implica local activo.",
            "Puede haber locales cerrados (que figuran) o faltantes (que no figuran en ninguna fuente).",
            "La deduplicación entre fuentes es heurística (nombre + distancia + similitud); puede dejar algún "
            "duplicado o separar sucursales.",
            "No se calcula densidad por habitante (no hay dataset de población en el proyecto).",
            "Falta validación manual / de campo antes de considerar el número definitivo.",
        ], gap=0.044)
        foot(fig, "Padrón candidato no oficial · pendiente de validación manual.")
        pdf.savefig(fig); plt.close(fig)

        # ---- 16. Próximos pasos ----
        fig = page(pdf)
        head(fig, "AGENDA", "Próximos pasos", "Del padrón candidato a una base validada.", "16 / 18")
        bullets(fig, 0.84, [
            f"Validar los {n_rev} casos en revisión manual (dudosos y posibles faltantes).",
            "Revisar los locales independientes prioritarios: son el núcleo del universo de casas de barrio.",
            "Confirmar los candidatos multifuente como base más sólida.",
            "Documentar casos emblemáticos con fuentes verificables (ver pág. 17).",
            "Incorporar al pipeline DataGastro solo después de la validación manual, con aprobación.",
            "Replicar la metodología (oficial + abierta + operativa, con auditoría de calidad) en otros "
            "rubros gastronómicos.",
        ], gap=0.046)
        foot(fig, "Padrón candidato no oficial · base para validación territorial.")
        pdf.savefig(fig); plt.close(fig)

        # ---- 17. Casos emblemáticos ----
        fig = page(pdf)
        head(fig, "PATRIMONIO GASTRONÓMICO", "Casos emblemáticos (a validar documentalmente)",
             "Solo se afirma lo que tiene fuente verificable.", "17 / 18")
        usar = [h for h in hist if h["usar_en_informe"] == "si"]
        if usar:
            fig.patches.append(Rectangle((0.07, 0.66), 0.86, 0.13, transform=fig.transFigure,
                                         facecolor=GRISCLARO, edgecolor=AZUL, lw=1.2))
            fig.text(0.09, 0.755, "LA JUVENIL — caso documentado", fontsize=12, fontweight="bold", color=AZUL)
            fig.text(0.09, 0.715, "Fundada el 1 de diciembre de 1959 (Colegiales); negocio familiar de tres\n"
                     "generaciones. Fuentes: La Nación y El Cronista.", fontsize=10, color="#222222", va="top")
        bullets(fig, 0.60, [
            "El resto de las marcas relevadas no tiene, por ahora, antigüedad documentada de forma confiable: "
            "Raviolón (referencias secundarias a 1971) y Master Pastas (marca actual desde 1995, según su "
            "sitio) requieren confirmación; Biasatti es un pastificio reciente (2020), no histórico.",
            "Multipasta, Pastas Mazzeo y Caprizzi no presentan año de fundación verificable en las fuentes "
            "consultadas.",
            "Criterio: no se afirma antigüedad sin fuente. El detalle de fuentes y nivel de confianza queda "
            "registrado en 'fuentes_historicas_casas_pastas.csv'.",
        ], gap=0.05)
        fig.patches.append(Rectangle((0.07, 0.20), 0.86, 0.07, transform=fig.transFigure,
                                     facecolor="#fff4e6", edgecolor="#c0762b", lw=1.0))
        fig.text(0.09, 0.245, "Casos emblemáticos a validar documentalmente en una próxima etapa.",
                 fontsize=10.5, color="#7a4a10", style="italic", va="top")
        foot(fig, "No se infiere antigüedad por fama. Fuentes registradas en CSV con nivel de confianza.")
        pdf.savefig(fig); plt.close(fig)

        # ---- 18. Cierre metodológico ----
        fig = page(pdf)
        head(fig, "REPLICABILIDAD", "Cierre metodológico",
             "Cómo replicar este enfoque en otros rubros gastronómicos.", "18 / 18")
        bullets(fig, 0.84, [
            "1) Partir del registro administrativo oficial (AGC / F02) como núcleo estricto.",
            "2) Ampliar cobertura con fuentes abiertas (OpenStreetMap) y operativas no oficiales (Google "
            "Places API), siempre rotuladas como tales.",
            "3) Deduplicar entre fuentes (nombre + dirección + distancia + similitud) conservando trazabilidad.",
            "4) Clasificar por confianza (multifuente > una fuente) y separar cadenas de independientes, sin "
            "descartar a las casas de barrio.",
            "5) Auditar calidad (inflación de cadenas, falsas fusiones, nombres genéricos) antes de cerrar.",
            "6) Marcar la revisión manual pendiente y no presentar el número como definitivo hasta validarlo.",
        ], gap=0.05)
        fig.text(0.07, 0.30, "Resultado: una base analítica reproducible, no oficial, lista para validación "
                 "territorial y eventual incorporación al pipeline DataGastro (con aprobación).",
                 fontsize=10.5, color=AZUL, va="top")
        foot(fig, "DataGastro · padrón candidato no oficial · método replicable en otros rubros.")
        pdf.savefig(fig); plt.close(fig)

        d = pdf.infodict()
        d["Title"] = "Casas de pastas en CABA — Padrón candidato integrado (V2 ejecutivo)"
        d["Author"] = "DataGastro"
        d["Subject"] = "Padrón candidato no oficial (AGC + OSM + Google Places). Pendiente de validación manual."

    escribir_md(hoy, rv2, rqc, com, bar, dens_com, dens_bar, combos, cobertura, hist)
    print(f"PDF V2 generado: {PDF}")
    print(f"Páginas: 18 | tamaño: {PDF.stat().st_size/1024:.0f} KB")
    print(f"MD V2 generado: {MD}")
    print(f"GeoJSON sanitizado v2: {len(feats)} puntos")


def escribir_md(hoy, rv2, rqc, com, bar, dens_com, dens_bar, combos, cobertura, hist):
    n_tot = rv2["candidatos_unicos"]
    L = ["# Casas de pastas en CABA — Padrón candidato integrado (V2 ejecutivo)\n"]
    L.append(f"_Fecha: {hoy} · Versión V2 · **Padrón candidato no oficial, pendiente de validación manual.**_\n")
    L.append("> El registro oficial muestra el núcleo administrativo estricto, pero el universo operativo "
             "probable de casas de pastas en la Ciudad es más amplio. El padrón candidato integrado combina "
             "AGC, OpenStreetMap y Google Places para construir una base analítica, no oficial, pendiente de "
             "validación manual.\n")
    L.append("## Indicadores\n")
    L.append(f"- **{n_tot}** candidatos únicos · **{rv2['independientes']}** independientes / de barrio · "
             f"**{rv2['cadenas']}** en cadenas · **{rv2['multifuente']}** multifuente · "
             f"**{rv2['revision_manual_prioritaria']}** en revisión manual.\n")
    L.append("## Fuentes y capas\n")
    L.append("| Fuente | Naturaleza | Detectados | Qué puede / no puede afirmar |")
    L.append("|---|---|---|---|")
    L.append("| AGC / F02 | Registro administrativo **oficial** | 11 | Habilitaciones; **no implica local activo** |")
    L.append("| OpenStreetMap | Relevamiento **abierto auxiliar** | 152 | Cobertura territorial; **no oficial** |")
    L.append("| Google Places | **Operativa no oficial** | 151 | Visibilidad comercial; **no gubernamental** |")
    L.append(f"| Integrado v2 | **Padrón candidato** | {n_tot} | Unión deduplicada; **a validar** |")
    L.append("\n_Detectados por fuente dentro del padrón integrado post-deduplicación; no equivale a "
             "resultados brutos._\n")
    L.append("## Distribución territorial\n")
    L.append("- **Comunas (cantidad):** " + ", ".join(f"{c} ({n})" for c, n in com.most_common(5)) + ".")
    L.append("- **Barrios (cantidad):** " + ", ".join(f"{b} ({n})" for b, n in bar.most_common(5)) + ".")
    L.append("- **Densidad comuna (cand./km²):** " + ", ".join(f"{c} ({d:.2f})" for c, _, d in dens_com[:5]) + ".")
    L.append("- **Densidad barrio (cand./km²):** " + ", ".join(f"{b} ({d:.2f})" for b, _, d in dens_bar[:5]) +
             ". No es densidad por habitante.\n")
    L.append("## Cadenas e independientes\n")
    L.append(f"> El informe no describe únicamente cadenas: la mayor parte del padrón candidato corresponde "
             f"a casas independientes o de escala barrial ({rv2['independientes']} de {n_tot}).\n")
    L.append("Cadenas (control de cobertura): " +
             ", ".join(f"{CADENA_CAPS.get(r['cadena'], r['cadena'].upper())} ({r['sucursales']})"
                       for r in cobertura[:7]) + ".\n")
    L.append("## Núcleo multifuente\n")
    L.append(f"- {rv2['multifuente']} candidatos en más de una fuente (Google + OSM): base de mayor confianza.")
    L.append(f"- Combinaciones: solo OSM {combos.get('osm',0)} · solo Google {combos.get('google',0)} · "
             f"Google+OSM {combos.get('google+osm',0)} · solo AGC {combos.get('agc',0)}.\n")
    L.append("## Control de calidad\n")
    L.append("- 11 cadenas auditadas, sin alertas de inflación. La Juvenil (28) = unión legítima de fuentes.")
    L.append(f"- Posibles duplicados: {rqc['posibles_duplicados_pares']} (resultaron distintos) · "
             f"falsas fusiones: {rqc['falsas_fusiones_grupos']}.")
    L.append("- Nombres genéricos ('pastas frescas', 'pastificio', 'fábrica de pasta') reclasificados como "
             "independientes, no cadenas.")
    L.append(f"- {rv2['revision_manual_prioritaria']} casos en revisión manual (parte del control de calidad).\n")
    L.append("## Casos emblemáticos (a validar documentalmente)\n")
    usar = [h for h in hist if h["usar_en_informe"] == "si"]
    if usar:
        L.append("- **LA JUVENIL** — fundada el 1 de diciembre de 1959 (Colegiales); negocio familiar de tres "
                 "generaciones. Fuentes: La Nación, El Cronista (caso documentado).")
    L.append("- Raviolón (1971, referencia secundaria) y Master Pastas (marca actual desde 1995) requieren "
             "confirmación; Biasatti es reciente (2020). Multipasta, Pastas Mazzeo y Caprizzi sin año "
             "verificable. Detalle en `fuentes_historicas_casas_pastas.csv`.")
    L.append("- _No se infiere antigüedad por fama; solo se afirma lo que tiene fuente verificable._\n")
    L.append("## Limitaciones\n")
    L.append("- No es censo definitivo ni padrón oficial. Google/OSM no son oficiales. AGC es oficial pero "
             "angosto y no implica local activo. Puede haber locales cerrados o faltantes. La deduplicación "
             "es heurística. Falta validación manual/campo.\n")
    L.append("## Próximos pasos\n")
    L.append(f"1. Validar los {rv2['revision_manual_prioritaria']} casos manuales.\n2. Revisar independientes "
             "prioritarios.\n3. Confirmar multifuente.\n4. Documentar emblemáticos con fuentes.\n"
             "5. Incorporar al pipeline solo tras validación.\n6. Replicar en otros rubros.\n")
    MD.write_text("\n".join(L), encoding="utf-8")


if __name__ == "__main__":
    main()
