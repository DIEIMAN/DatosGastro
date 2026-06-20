"""Informe ejecutivo V3 — Casas de pastas en CABA, padrón candidato integrado.

Versión storytelling DataGastro: cada sección responde una pregunta (pregunta -> respuesta
ejecutiva -> dato -> visualización -> lectura territorial -> cuidado metodológico). Suma
mapas coropléticos por comuna y barrio (cantidad y densidad).

Usa SOLO agregados y mapas anonimizados (sin nombres, direcciones, razón social, place_id,
teléfonos, emails, ratings ni API key). No hace requests. No commitea.

Salidas:
  outputs/casas_pastas_reporte/INFORME_CASAS_PASTAS_INTEGRADO_V3.pdf
  outputs/casas_pastas_reporte/INFORME_CASAS_PASTAS_INTEGRADO_V3.md
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
import matplotlib.cm as cm  # noqa: E402
import matplotlib.patheffects as pe  # noqa: E402
from matplotlib.colors import Normalize  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402
from shapely.geometry import shape  # noqa: E402

# Precisión de coordenadas para el GeoJSON compartible (territorial, NO submétrica).
# 3 decimales ≈ ~110 m en latitud y ~90 m en longitud a la latitud de CABA.
GEO_DECIMALS = 3

ROOT = Path(__file__).resolve().parents[2]
INT = ROOT / "outputs" / "casas_pastas_integrado"
REP = ROOT / "outputs" / "casas_pastas_reporte"
SAN = REP / "integrado_sanitizado"
GEO = ROOT / "data" / "raw"
PDF = REP / "INFORME_CASAS_PASTAS_INTEGRADO_V3.pdf"
MD = REP / "INFORME_CASAS_PASTAS_INTEGRADO_V3.md"

A4 = (8.27, 11.69)
AZUL = "#1f3b57"
AZUL2 = "#2c7fb8"
ROJO = "#c0392b"
GRIS = "#555555"
GRISCLARO = "#eef2f6"
VERDE = "#1a9850"
NARANJA = "#c0762b"

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


# ---------- diseño ----------
def page():
    fig = plt.figure(figsize=A4)
    fig.patch.set_facecolor("white")
    return fig


def head(fig, kicker, titulo, subtitulo, num, tsize=18):
    fig.text(0.07, 0.955, kicker, color=ROJO, fontsize=8.5, fontweight="bold")
    fig.text(0.93, 0.955, num, color=GRIS, fontsize=8.5, ha="right")
    for j, ln in enumerate(textwrap.wrap(titulo, 46)):
        fig.text(0.07, 0.928 - j * 0.030, ln, color=AZUL, fontsize=tsize, fontweight="bold", va="top")
    base = 0.928 - len(textwrap.wrap(titulo, 46)) * 0.030
    fig.lines.append(Line2D([0.07, 0.34], [base + 0.004, base + 0.004], color=ROJO, lw=2.2, transform=fig.transFigure))
    if subtitulo:
        for j, ln in enumerate(textwrap.wrap(subtitulo, 92)):
            fig.text(0.07, base - 0.012 - j * 0.020, ln, color=GRIS, fontsize=10.5, style="italic", va="top")
    return base


def bullets(fig, y0, items, size=10.5, gap=0.039, wrap=86, x=0.085):
    y = y0
    for it in items:
        lines = textwrap.wrap(it.strip(), wrap) or [""]
        fig.text(x, y, "•", fontsize=size, color=ROJO, va="top")
        for j, ln in enumerate(lines):
            fig.text(x + 0.022, y - j * 0.0225, ln, fontsize=size, color="#222222", va="top")
        y -= gap + (len(lines) - 1) * 0.0225
    return y


def insight(fig, y, texto, color=AZUL, h=0.075, fc=GRISCLARO):
    fig.patches.append(Rectangle((0.07, y), 0.86, h, transform=fig.transFigure, facecolor=fc,
                                 edgecolor=color, lw=1.3))
    lines = textwrap.wrap(texto, 84)
    for j, ln in enumerate(lines):
        fig.text(0.09, y + h - 0.022 - j * 0.019, ln, fontsize=9.5, color="#222222", va="top", fontweight="bold")


def cards(fig, y, items, h=0.10):
    n = len(items)
    w = 0.86 / n
    for i, (val, lab, col) in enumerate(items):
        x = 0.07 + i * w
        fig.patches.append(Rectangle((x + 0.008, y), w - 0.016, h, transform=fig.transFigure,
                                     facecolor=GRISCLARO, edgecolor=col, lw=1.6))
        fig.text(x + w / 2, y + h * 0.58, str(val), ha="center", fontsize=21, fontweight="bold", color=col)
        fig.text(x + w / 2, y + h * 0.20, lab, ha="center", fontsize=8, color=GRIS)


def foot(fig, txt):
    fig.lines.append(Line2D([0.07, 0.93], [0.055, 0.055], color="#dddddd", lw=0.8, transform=fig.transFigure))
    for j, ln in enumerate(textwrap.wrap("Cuidado metodológico: " + txt, 120)):
        fig.text(0.07, 0.043 - j * 0.016, ln, color=GRIS, fontsize=7.8, va="top")


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
        ax.text(b.get_width() + mx * 0.01, b.get_y() + b.get_height() / 2, valfmt.format(v),
                va="center", fontsize=8, color=GRIS)
    ax.set_xlim(0, mx * 1.13)
    return ax


def poligonos(geom):
    if geom["type"] == "Polygon":
        rings = [geom["coordinates"][0]]
    elif geom["type"] == "MultiPolygon":
        rings = [poly[0] for poly in geom["coordinates"]]
    else:
        return []
    return [([c[0] for c in r], [c[1] for c in r]) for r in rings]


def label_xy(geom):
    """Punto de etiqueta garantizado DENTRO del polígono (representative_point)."""
    try:
        p = shape(geom).representative_point()
        return p.x, p.y
    except Exception:  # noqa: BLE001
        xs, ys = [], []
        for x, y in poligonos(geom):
            xs += x; ys += y
        return (sum(xs) / len(xs), sum(ys) / len(ys)) if xs else (0, 0)


def _texto_contraste(rgba):
    """Devuelve (color_texto, color_halo) legible según luminancia del fondo."""
    r, g, b = rgba[0], rgba[1], rgba[2]
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    if lum < 0.55:                      # fondo oscuro -> texto blanco, halo oscuro
        return "white", "#1a1a1a"
    return "#1a1a1a", "white"           # fondo claro -> texto oscuro, halo blanco


def choropleth(fig, rect, features, key_prop, val_by_key, cmap_name, title, label_keys=None,
               etiqueta_num=False):
    ax = fig.add_axes(rect)
    vals = [v for v in val_by_key.values() if v]
    vmax = max(vals) if vals else 1
    norm = Normalize(vmin=0, vmax=vmax)
    cmap = plt.get_cmap(cmap_name)
    for f in features:
        if key_prop == "comuna":
            key = str(f["properties"]["comuna"])
        else:
            key = f["properties"]["nombre"].title()
        v = val_by_key.get(key, 0)
        color = cmap(norm(v)) if v else (0.94, 0.94, 0.94, 1.0)
        for xs, ys in poligonos(f["geometry"]):
            ax.fill(xs, ys, facecolor=color, edgecolor="white", lw=0.5, zorder=1)
        etiqueta = etiqueta_num or (label_keys and key in label_keys)
        if etiqueta:
            cx, cy = label_xy(f["geometry"])
            txtcolor, halo = _texto_contraste(color)
            size = 7 if etiqueta_num else 6.5
            ax.text(cx, cy, key, ha="center", va="center", fontsize=size, color=txtcolor,
                    fontweight="bold", zorder=5,
                    path_effects=[pe.withStroke(linewidth=1.8, foreground=halo)])
    ax.set_aspect(1.28); ax.axis("off")
    ax.set_title(title, color=AZUL, fontsize=11, loc="left", pad=4)
    sm = cm.ScalarMappable(norm=norm, cmap=cmap); sm.set_array([])
    cb = fig.colorbar(sm, ax=ax, fraction=0.035, pad=0.01, shrink=0.6)
    cb.ax.tick_params(labelsize=7)
    return ax


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

    com = Counter(r["comuna"] for r in pad if r["comuna"])
    bar = Counter(r["barrio"] for r in pad if r["barrio"])
    dcom = {c: round(n / acom[c], 3) for c, n in com.items() if c in acom}
    dbar = {b: round(n / abar[b], 3) for b, n in bar.items() if b in abar}
    dens_com = sorted(dcom.items(), key=lambda x: -x[1])
    dens_bar = sorted(dbar.items(), key=lambda x: -x[1])
    combos = Counter(r["fuentes_detectan"] for r in pad)

    pts, feats = [], []
    for i, r in enumerate(pad, 1):
        la, lo = fnum(r["lat"]), fnum(r["lon"])
        if la is None or lo is None:
            continue
        pts.append({"lat": la, "lon": lo, "clase": r["clase_integrada"], "barrio": r["barrio"]})
        # Coordenadas REDUCIDAS para el pack compartible (territorial, no submétrica).
        feats.append({"type": "Feature",
                      "geometry": {"type": "Point",
                                   "coordinates": [round(lo, GEO_DECIMALS), round(la, GEO_DECIMALS)]},
                      "properties": {"id_anonimo": f"PT{i:04d}", "clasificacion_integrada": r["clase_integrada"],
                                     "es_cadena_detectada": r["es_cadena_detectada"], "comuna": r["comuna"],
                                     "barrio": r["barrio"]}})
    SAN.mkdir(parents=True, exist_ok=True)
    (SAN / "mapa_puntos_sanitizado.geojson").write_text(
        json.dumps({"type": "FeatureCollection", "features": feats}, ensure_ascii=False, indent=1),
        encoding="utf-8")

    # Regenerar integrado_por_fuente.csv ALINEADO a v2 (evita contradicción con el informe).
    etq_combo = {"osm": "solo OSM", "google": "solo Google", "google+osm": "Google + OSM", "agc": "solo AGC"}
    filas_fuente = [{"combinacion_fuentes": etq_combo.get(k, k), "cantidad": combos.get(k, 0)}
                    for k in ("osm", "google", "google+osm", "agc")]
    filas_fuente.append({"combinacion_fuentes": "total", "cantidad": sum(combos.values())})
    filas_fuente.append({"combinacion_fuentes": "multifuente", "cantidad": int(rv2["multifuente"])})
    with (SAN / "integrado_por_fuente.csv").open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["combinacion_fuentes", "cantidad"]); w.writeheader()
        w.writerows(filas_fuente)

    n_tot, n_ind, n_cad = rv2["candidatos_unicos"], int(rv2["independientes"]), int(rv2["cadenas"])
    n_rev, n_multi = rv2["revision_manual_prioritaria"], int(rv2["multifuente"])

    def leyenda(ax, loc="lower left"):
        leg = [Line2D([0], [0], marker="o", color="w", markerfacecolor=c, markersize=8, label=CLASE_LABEL[k])
               for k, c in CLASE_COLOR.items()]
        ax.legend(handles=leg, loc=loc, fontsize=7.3, frameon=False)

    top_barrios = set(b for b, _ in bar.most_common(6))

    with PdfPages(PDF) as pdf:
        # 1. Portada
        fig = page()
        fig.patches.append(Rectangle((0, 0.72), 1, 0.28, transform=fig.transFigure, facecolor=AZUL, zorder=0))
        fig.text(0.07, 0.90, "DIAGNÓSTICO TERRITORIAL GASTRONÓMICO", color="#cdd9e5", fontsize=10, fontweight="bold")
        fig.text(0.07, 0.815, "Casas de pastas en la\nCiudad de Buenos Aires", color="white",
                 fontsize=27, fontweight="bold", va="center")
        fig.text(0.07, 0.665, "Una lectura territorial del universo operativo probable", fontsize=13.5, color=AZUL)
        fig.lines.append(Line2D([0.07, 0.55], [0.635, 0.635], color=ROJO, lw=2.5, transform=fig.transFigure))
        cards(fig, 0.47, [(n_tot, "candidatos únicos", AZUL), (n_ind, "independientes", VERDE),
                          (n_cad, "en cadenas", NARANJA), (n_multi, "multifuente", VERDE),
                          (n_rev, "revisión manual", GRIS)], h=0.115)
        fig.text(0.07, 0.36,
                 "Padrón candidato integrado (v2): cruza el registro administrativo oficial (AGC / F02),\n"
                 "el relevamiento abierto auxiliar (OpenStreetMap) y una señal operativa no oficial\n"
                 "(Google Places API). No es un padrón oficial ni un censo definitivo: es una base\n"
                 "analítica, pendiente de validación manual.",
                 fontsize=11, color="#333333", va="top")
        fig.text(0.07, 0.12, f"Fecha: {hoy}    ·    Versión: V3 (ejecutiva)", fontsize=10, color=GRIS)
        fig.text(0.07, 0.095, "Documento interno · agregados y mapas anonimizados · sin datos personales",
                 fontsize=9, color=GRIS)
        pdf.savefig(fig); plt.close(fig)

        # 2. Resumen ejecutivo
        fig = page()
        head(fig, "RESUMEN EJECUTIVO", "Qué muestra el cruce de fuentes",
             "Un universo operativo probable más amplio que el registro oficial, con foco en las casas de barrio.", "2 / 22")
        cards(fig, 0.74, [(n_tot, "candidatos únicos", AZUL), (n_ind, "independientes", VERDE),
                          (n_cad, "en cadenas", NARANJA), (n_multi, "multifuente", VERDE),
                          (n_rev, "revisión manual", GRIS)], h=0.105)
        bullets(fig, 0.66, [
            f"Se construyó un padrón candidato integrado de {n_tot} posibles casas de pastas en CABA, "
            "combinando registro oficial, fuentes abiertas y señales operativas no oficiales.",
            "No reemplaza al registro oficial ni constituye un censo definitivo: es una base analítica para "
            "validación territorial.",
            f"Predominan las casas independientes / de barrio ({n_ind} de {n_tot}); {n_cad} pertenecen a "
            "cadenas, usadas como control de cobertura.",
            f"{n_multi} candidatos aparecen en más de una fuente: son el núcleo de mayor respaldo cruzado.",
            f"{n_rev} casos quedan en revisión manual; forman parte del control de calidad, no son un error.",
        ])
        insight(fig, 0.20, "El número oficial es el piso; el universo operativo probable es más amplio. "
                "La diferencia no es un error: son fuentes y definiciones distintas.", color=AZUL)
        foot(fig, "padrón candidato no oficial. Total 261 · independientes 180 · cadenas 81 · multifuente 53 · revisión 42.")
        pdf.savefig(fig); plt.close(fig)

        # 3. Hallazgo principal
        fig = page()
        head(fig, "HALLAZGO PRINCIPAL", "Registro oficial vs. universo operativo probable",
             "El registro oficial muestra el núcleo estricto; el padrón candidato amplía la lectura.", "3 / 22")
        ax = fig.add_axes([0.13, 0.40, 0.72, 0.34])
        n_tot_i = int(n_tot)
        valores = [11, n_multi, n_tot_i]
        labels = ["AGC oficial\nestricto", "Núcleo\nmultifuente", "Padrón candidato\nintegrado"]
        b = ax.bar(labels, valores, color=[AZUL2, VERDE, AZUL], width=0.6)
        for bi, v in zip(b, valores):
            ax.text(bi.get_x() + bi.get_width() / 2, v + 4, str(v), ha="center", fontweight="bold", color=AZUL)
        ax.set_ylim(0, n_tot_i * 1.15)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.set_ylabel("candidatos / registros", fontsize=9)
        bullets(fig, 0.32, [
            "El registro oficial (AGC / F02) identifica un núcleo estricto de 11 habilitaciones de "
            "elaboración de pastas: preciso pero angosto, y no implica local activo.",
            f"El padrón candidato integrado eleva la lectura a {n_tot} establecimientos posibles al sumar "
            "fuentes abiertas y operativas.",
        ])
        foot(fig, "AGC = registro administrativo oficial · OSM = fuente abierta auxiliar · Google = señal operativa no oficial.")
        pdf.savefig(fig); plt.close(fig)

        # 4. Fuentes y capas (P2)
        fig = page()
        head(fig, "PREGUNTA 2", "¿Por qué el registro oficial no alcanza por sí solo?",
             "Respuesta: porque mide habilitaciones de un rubro estricto; las fuentes abiertas y operativas amplían cobertura.", "4 / 22")
        ax = fig.add_axes([0.07, 0.55, 0.86, 0.24]); ax.axis("off")
        data = [["AGC / F02", "Registro oficial", "11", "Habilitaciones; NO implica local activo"],
                ["OpenStreetMap", "Abierta auxiliar", "152", "Cobertura territorial; no oficial"],
                ["Google Places", "Operativa no oficial", "151", "Visibilidad comercial; no gubernamental"],
                ["Integrado v2", "Padrón candidato", str(n_tot), "Unión deduplicada; a validar"]]
        t = ax.table(cellText=data, colLabels=["Fuente", "Naturaleza", "Detectados", "Qué puede / no puede afirmar"],
                     colWidths=[0.18, 0.20, 0.15, 0.47], loc="upper center", cellLoc="center")
        t.auto_set_font_size(False); t.set_fontsize(9); t.scale(1, 1.6)
        for (r, _c), cell in t.get_celld().items():
            cell.set_edgecolor("#dddddd")
            if r == 0:
                cell.set_facecolor(AZUL); cell.set_text_props(color="white", fontweight="bold")
            elif r % 2 == 0:
                cell.set_facecolor(GRISCLARO)
        fig.text(0.07, 0.52, "Detectados por fuente dentro del padrón integrado post-deduplicación; no equivale "
                 "a resultados brutos.", fontsize=8.3, color=GRIS, style="italic")
        bullets(fig, 0.46, [
            "Ninguna fuente sola alcanza el universo real: AGC es preciso pero angosto; OSM y Google amplían "
            "cobertura pero no son oficiales.",
            "Aparecer en más de una fuente sube la confianza; aparecer en una sola se conserva como candidato.",
        ])
        foot(fig, "el padrón es candidato; el número final requiere validación manual.")
        pdf.savefig(fig); plt.close(fig)

        # 5. Mapa general (P3)
        fig = page()
        head(fig, "PREGUNTA 3", "¿Dónde se concentran las casas de pastas candidatas?",
             "Respuesta: en el corredor norte–centro de la Ciudad, con polos en Palermo, Caballito y Recoleta/Belgrano.", "5 / 22")
        ax = fig.add_axes([0.06, 0.13, 0.88, 0.70])
        for f in gc["features"]:
            for xs, ys in poligonos(f["geometry"]):
                ax.plot(xs, ys, color="#cfcfcf", lw=0.6, zorder=1)
        for p in pts:
            ax.scatter(p["lon"], p["lat"], s=14, color=CLASE_COLOR.get(p["clase"], "#999"),
                       edgecolor="white", lw=0.25, zorder=3)
        ax.set_aspect(1.28); ax.axis("off")
        leyenda(ax)
        foot(fig, "El mapa representa 259 candidatos georreferenciados; los 2 restantes integran el conteo "
                  "general pero no cuentan con coordenadas suficientes para visualización puntual. Puntos "
                  "anonimizados (sin nombres ni direcciones); contornos: comunas GCBA.")
        pdf.savefig(fig); plt.close(fig)

        # 6. Coroplético comuna - cantidad
        fig = page()
        head(fig, "CONCENTRACIÓN TERRITORIAL", "Concentración territorial por comuna",
             "Cantidad de candidatos por comuna.", "6 / 22")
        choropleth(fig, [0.08, 0.20, 0.82, 0.62], gc["features"], "comuna", dict(com), "YlOrRd",
                   "Candidatos por comuna (cantidad)", etiqueta_num=True)
        insight(fig, 0.10, "Las comunas con más candidatos muestran zonas de alta oferta comercial y "
                "residencial, pero no necesariamente la mayor densidad relativa.", color=NARANJA, h=0.07)
        foot(fig, "cantidad absoluta por comuna; comparar con densidad (pág. 8).")
        pdf.savefig(fig); plt.close(fig)

        # 7. Coroplético comuna - densidad
        fig = page()
        head(fig, "DENSIDAD TERRITORIAL", "Densidad territorial por comuna",
             "Candidatos por km² de superficie oficial.", "7 / 22")
        choropleth(fig, [0.08, 0.20, 0.82, 0.62], gc["features"], "comuna", dcom, "PuBuGn",
                   "Densidad por comuna (candidatos/km²)", etiqueta_num=True)
        insight(fig, 0.10, "Densidad = candidatos / superficie oficial km². No es densidad por habitante. "
                "El ranking por densidad difiere del de cantidad absoluta.", color=AZUL2, h=0.07)
        foot(fig, "densidad por superficie, no por población (falta dataset de población).")
        pdf.savefig(fig); plt.close(fig)

        # 8. Ranking comuna
        fig = page()
        head(fig, "PREGUNTA 4", "¿Qué cambia cuando miramos densidad por km²?",
             "Respuesta: el orden cambia; comunas chicas y céntricas escalan posiciones.", "8 / 22")
        topc = com.most_common(8)[::-1]
        barh(fig, [0.16, 0.45, 0.74, 0.29], [f"Comuna {c}" for c, _ in topc], [n for _, n in topc],
             AZUL2, "Top comunas por cantidad", "candidatos")
        dc = dens_com[:8][::-1]
        barh(fig, [0.16, 0.085, 0.74, 0.29], [f"Comuna {c}" for c, _ in dc], [v for _, v in dc],
             "#31a354", "Top comunas por densidad (cand./km²)", "candidatos/km²", valfmt="{:.2f}")
        foot(fig, "cantidad y densidad miden cosas distintas; ambas son lecturas válidas y complementarias.")
        pdf.savefig(fig); plt.close(fig)

        # 9. Coroplético barrio - cantidad
        fig = page()
        head(fig, "CONCENTRACIÓN TERRITORIAL", "Concentración por barrio (cantidad)",
             "Barrios líderes: Palermo, Caballito, Recoleta, Belgrano y Villa Urquiza.", "9 / 22")
        choropleth(fig, [0.06, 0.16, 0.86, 0.66], gb["features"], "barrio", dict(bar), "YlOrRd",
                   "Candidatos por barrio (cantidad)", label_keys=top_barrios)
        foot(fig, "barrios con 0 candidatos en gris claro. Cantidad absoluta.")
        pdf.savefig(fig); plt.close(fig)

        # 10. Coroplético barrio - densidad
        fig = page()
        head(fig, "DENSIDAD TERRITORIAL", "Densidad por barrio (candidatos/km²)",
             "El ranking por densidad puede diferir del de cantidad absoluta.", "10 / 22")
        choropleth(fig, [0.06, 0.16, 0.86, 0.66], gb["features"], "barrio", dbar, "PuBuGn",
                   "Densidad por barrio (candidatos/km²)", label_keys=set(b for b, _ in dens_bar[:5]))
        insight(fig, 0.08, "Los barrios con más candidatos no siempre son los más densos en relación con su "
                "superficie.", color=AZUL2, h=0.06)
        foot(fig, "densidad por superficie oficial, no por habitante.")
        pdf.savefig(fig); plt.close(fig)

        # 11. Ranking barrio
        fig = page()
        head(fig, "PREGUNTA 5", "¿Qué barrios aparecen como polos del universo candidato?",
             "Palermo y Caballito lideran; Recoleta y Belgrano empatan tercero (22 c/u).", "11 / 22")
        topb = bar.most_common(10)[::-1]
        barh(fig, [0.22, 0.45, 0.70, 0.29], [b for b, _ in topb], [n for _, n in topb],
             "#7b5ea7", "Top barrios por cantidad", "candidatos")
        db = dens_bar[:10][::-1]
        barh(fig, [0.22, 0.085, 0.70, 0.29], [b for b, _ in db], [v for _, v in db],
             "#dd8452", "Top barrios por densidad (cand./km²)", "candidatos/km²", valfmt="{:.2f}")
        foot(fig, "Recoleta y Belgrano empatan (22 c/u); se elige Recoleta para el zoom cartográfico.")
        pdf.savefig(fig); plt.close(fig)

        # 12-14. Zooms
        zooms = [("Palermo", "12 / 22", "Palermo concentra el mayor volumen absoluto de candidatos, combinando "
                  "cadenas, locales independientes y puntos detectados por más de una fuente."),
                 ("Caballito", "13 / 22", "Caballito muestra fuerte presencia de casas de barrio y una densidad "
                  "alta sobre una superficie media."),
                 ("Recoleta", "14 / 22", "Recoleta empata con Belgrano (22 candidatos c/u); su superficie "
                  "acotada la ubica entre las de mayor densidad.")]
        for barrio, num, coment in zooms:
            fig = page()
            head(fig, "ZOOM TERRITORIAL", f"Zoom: {barrio}",
                 f"{bar.get(barrio, 0)} candidatos en {barrio} (padrón v2, anonimizado).", num)
            ax = fig.add_axes([0.08, 0.33, 0.84, 0.50])
            geom = bar_poly.get(barrio)
            xs_all, ys_all = [], []
            if geom:
                for xs, ys in poligonos(geom):
                    ax.fill(xs, ys, color="#f7f9fb", zorder=0)
                    ax.plot(xs, ys, color="#bbbbbb", lw=1.0)
                    xs_all += xs; ys_all += ys
            for p in [p for p in pts if p["barrio"] == barrio]:
                ax.scatter(p["lon"], p["lat"], s=36, color=CLASE_COLOR.get(p["clase"], "#999"),
                           edgecolor="white", lw=0.4, zorder=3)
            if xs_all:
                mx = (max(xs_all) - min(xs_all)) * 0.08; my = (max(ys_all) - min(ys_all)) * 0.08
                ax.set_xlim(min(xs_all) - mx, max(xs_all) + mx); ax.set_ylim(min(ys_all) - my, max(ys_all) + my)
            ax.set_aspect(1.28); ax.axis("off")
            # Leyenda FUERA del mapa (debajo), para no pisar los puntos.
            leg = [Line2D([0], [0], marker="o", color="w", markerfacecolor=c, markersize=8, label=CLASE_LABEL[k])
                   for k, c in CLASE_COLOR.items()]
            ax.legend(handles=leg, loc="upper center", bbox_to_anchor=(0.5, -0.03), ncol=3,
                      fontsize=7.5, frameon=False)
            for j, ln in enumerate(textwrap.wrap(coment, 96)):
                fig.text(0.07, 0.165 - j * 0.020, ln, fontsize=10.5, color="#222222", style="italic", va="top")
            foot(fig, "solo puntos anonimizados dentro del barrio; sin nombres ni direcciones.")
            pdf.savefig(fig); plt.close(fig)

        # 15. Cadenas e independientes (P6)
        fig = page()
        head(fig, "PREGUNTA 6", "¿Predominan las cadenas o las casas de barrio?",
             "En el universo candidato predominan las casas independientes y de escala barrial.", "15 / 22")
        cards(fig, 0.72, [(n_ind, "independientes / de barrio", VERDE), (n_cad, "en cadenas", NARANJA)], h=0.12)
        ax = fig.add_axes([0.10, 0.50, 0.80, 0.10])
        tot = n_ind + n_cad
        ax.barh([0], [n_ind], color=VERDE)
        ax.barh([0], [n_cad], left=[n_ind], color=NARANJA)
        ax.text(n_ind / 2, 0, f"Independientes {round(100*n_ind/tot)}%", ha="center", va="center",
                color="white", fontsize=10, fontweight="bold")
        ax.text(n_ind + n_cad / 2, 0, f"Cadenas {round(100*n_cad/tot)}%", ha="center", va="center",
                color="white", fontsize=9, fontweight="bold")
        ax.axis("off")
        insight(fig, 0.34, "El universo candidato no está compuesto solo por franquicias: predominan las casas "
                "independientes y de escala barrial.", color=VERDE)
        foot(fig, "las cadenas se reportan como control de cobertura, no como foco único. No se cuentan categorías genéricas como cadenas.")
        pdf.savefig(fig); plt.close(fig)

        # 16. Principales cadenas (P7)
        fig = page()
        head(fig, "PREGUNTA 7", "¿Cuáles son las principales cadenas detectadas?",
             "Respuesta: La Juvenil encabeza; el resto son cadenas medianas o chicas.", "16 / 22")
        top_cad = [(CADENA_CAPS.get(r["cadena"], r["cadena"].upper()), int(r["sucursales"])) for r in cobertura][:8][::-1]
        barh(fig, [0.34, 0.20, 0.56, 0.60], [c for c, _ in top_cad], [n for _, n in top_cad],
             NARANJA, "Cadenas con más sucursales (control de cobertura)", "sucursales")
        foot(fig, "ranking de control de cobertura. No incluye categorías genéricas (p. ej. 'pastas frescas'), que se tratan como independientes.")
        pdf.savefig(fig); plt.close(fig)

        # 17. Núcleo multifuente (P8)
        fig = page()
        head(fig, "PREGUNTA 8", "¿Cuál es el núcleo de mayor respaldo cruzado?",
             "Respuesta: los candidatos detectados por más de una fuente (multifuente).", "17 / 22")
        orden = [("agc", "Solo AGC (oficial estricto)"), ("google", "Solo Google (operativo)"),
                 ("osm", "Solo OSM (auxiliar)"), ("google+osm", "Google + OSM (multifuente)")]
        barh(fig, [0.32, 0.50, 0.58, 0.30], [e for _, e in orden][::-1],
             [combos.get(k, 0) for k, _ in orden][::-1], VERDE, "Candidatos por combinación de fuentes", "candidatos")
        bullets(fig, 0.40, [
            f"{n_multi} candidatos aparecen en más de una fuente (Google + OSM): núcleo de mayor respaldo cruzado.",
            "Aparecer en más de una fuente aumenta la probabilidad de existencia, pero no la confirma: no "
            "reemplaza la validación territorial.",
            "Los de una sola fuente se conservan como candidatos (oficial estricto si es AGC, operativo si es "
            "Google, auxiliar si es OSM), sin degradar a los independientes.",
        ])
        foot(fig, "AGC oficial estricto no implica local activo; el núcleo multifuente es la base para empezar la validación.")
        pdf.savefig(fig); plt.close(fig)

        # 18. Revisión manual (P9)
        fig = page()
        head(fig, "PREGUNTA 9", "¿Qué queda pendiente antes de hablar de padrón definitivo?",
             "El padrón candidato requiere una etapa de validación manual y territorial antes de "
             "convertirse en una base definitiva.", "18 / 22")
        bullets(fig, 0.78, [
            f"Validar los {n_rev} casos en revisión manual.",
            "Confirmar el núcleo de mayor respaldo cruzado.",
            "Revisar especialmente casas independientes y de barrio.",
            "Verificar cadenas y sucursales con fuentes propias o revisión manual.",
            "Documentar posibles bajas, cierres o casos mal clasificados.",
            f"Mantener el {n_tot} como cifra de trabajo, no como cifra pública definitiva.",
        ], gap=0.05)
        insight(fig, 0.26, "El número definitivo se establece recién tras la validación manual y territorial. "
                "El detalle de los chequeos de calidad queda en el anexo metodológico interno.", color=AZUL)
        foot(fig, "los casos pendientes son parte del control de calidad, no un error.")
        pdf.savefig(fig); plt.close(fig)

        # 19. Casos emblemáticos
        fig = page()
        head(fig, "PATRIMONIO GASTRONÓMICO", "Casos emblemáticos (a validar documentalmente)",
             "Solo se afirma lo que tiene fuente verificable.", "19 / 22", tsize=16)
        usar = [h for h in hist if h["usar_en_informe"] == "si"]
        if usar:
            fig.patches.append(Rectangle((0.07, 0.66), 0.86, 0.12, transform=fig.transFigure,
                                         facecolor=GRISCLARO, edgecolor=AZUL, lw=1.2))
            fig.text(0.09, 0.745, "LA JUVENIL — caso documentado", fontsize=12, fontweight="bold", color=AZUL)
            fig.text(0.09, 0.708, "Fundada el 1 de diciembre de 1959 (Colegiales); negocio familiar de tres\n"
                     "generaciones. Fuentes: La Nación y El Cronista.", fontsize=10, color="#222222", va="top")
        bullets(fig, 0.60, [
            "El resto no tiene antigüedad documentada de forma confiable: Raviolón (1971, según fuentes "
            "secundarias de prensa) y Master Pastas (marca actual desde 1995, según su sitio oficial) "
            "requieren confirmación; Biasatti es un pastificio reciente (2020), no histórico.",
            "Multipasta, Pastas Mazzeo y Caprizzi no presentan año de fundación verificable en las fuentes "
            "consultadas.",
            "Criterio: no se afirma antigüedad sin fuente. Información histórica documentada en anexo "
            "metodológico interno.",
        ], gap=0.05)
        fig.patches.append(Rectangle((0.07, 0.22), 0.86, 0.06, transform=fig.transFigure,
                                     facecolor="#fff4e6", edgecolor=NARANJA, lw=1.0))
        fig.text(0.09, 0.258, "Casos emblemáticos a validar documentalmente en una próxima etapa.",
                 fontsize=10.5, color="#7a4a10", style="italic", va="top")
        foot(fig, "no se infiere antigüedad por fama; fuentes registradas en anexo metodológico interno.")
        pdf.savefig(fig); plt.close(fig)

        # 20. ¿Qué decisión permite tomar este informe? (+ recomendación operativa)
        fig = page()
        head(fig, "USO EJECUTIVO", "¿Qué decisión permite tomar este informe?",
             "Una hoja de ruta para pasar del padrón candidato a una base validada.", "20 / 22")
        bullets(fig, 0.82, [
            "Priorizar la validación territorial en los barrios polo (Palermo, Caballito, Recoleta/Belgrano).",
            f"Empezar por el núcleo de mayor respaldo cruzado: los {n_multi} candidatos multifuente.",
            f"Revisar los {n_rev} casos en revisión manual antes de cerrar cifras.",
            "Priorizar las casas independientes / de barrio: son el núcleo del universo.",
            f"No usar el {n_tot} como cifra pública definitiva hasta completar la validación.",
            "Tomar la metodología como prueba de concepto replicable para el análisis territorial gastronómico.",
        ], gap=0.038)
        fig.patches.append(Rectangle((0.07, 0.21), 0.86, 0.20, transform=fig.transFigure,
                                     facecolor=GRISCLARO, edgecolor=AZUL, lw=1.2))
        fig.text(0.09, 0.385, "Recomendación operativa para las próximas 2–4 semanas",
                 fontsize=11.5, fontweight="bold", color=AZUL, va="top")
        for j, paso in enumerate([
                "1. Validar una muestra piloto en un barrio polo.",
                "2. Depurar cadenas y nombres genéricos.",
                "3. Confirmar los candidatos multifuente.",
                "4. Revisar los independientes prioritarios.",
                "5. Definir si el padrón candidato alimenta la línea de análisis territorial gastronómico."]):
            fig.text(0.10, 0.345 - j * 0.026, paso, fontsize=10, color="#222222", va="top")
        foot(fig, "documento de apoyo a la decisión; el número definitivo requiere validación manual.")
        pdf.savefig(fig); plt.close(fig)

        # 21. Limitaciones
        fig = page()
        head(fig, "ALCANCE", "Limitaciones", "Qué no afirma este informe.", "21 / 22")
        bullets(fig, 0.82, [
            "No es un censo definitivo ni un padrón oficial de casas de pastas: es un padrón candidato.",
            "Google Places y OpenStreetMap no son fuentes oficiales; reflejan visibilidad comercial y "
            "relevamiento colaborativo, no un registro gubernamental.",
            "AGC es oficial pero angosto: mide habilitaciones de un rubro estricto y no implica local activo.",
            "Puede haber locales cerrados (que figuran) o faltantes (que no figuran en ninguna fuente).",
            "La deduplicación entre fuentes es heurística (nombre + distancia + similitud).",
            "No se calcula densidad por habitante (no hay dataset de población en el proyecto).",
            "Falta validación manual / de campo antes de considerar el número definitivo.",
        ], gap=0.043)
        foot(fig, "padrón candidato no oficial · pendiente de validación manual.")
        pdf.savefig(fig); plt.close(fig)

        # 22. Próximos pasos + cierre metodológico (P10)
        fig = page()
        head(fig, "PREGUNTA 10", "¿Qué aporta esta metodología al análisis gastronómico?",
             "Respuesta: un método replicable (oficial + abierta + operativa + auditoría) para otros rubros.", "22 / 22")
        bullets(fig, 0.82, [
            f"Próximos pasos: validar los {n_rev} casos en revisión; confirmar el núcleo multifuente; revisar "
            "independientes prioritarios; documentar emblemáticos con fuentes.",
            "Incorporar a la línea de análisis territorial gastronómico solo después de la validación manual, "
            "con aprobación.",
            "El método combina registro oficial (núcleo), fuentes abiertas y operativas (cobertura) y una "
            "auditoría de calidad (deduplicación, cadenas, nombres genéricos).",
            "Es replicable en otros rubros gastronómicos: pizzerías, heladerías artesanales, cafeterías de "
            "especialidad, panaderías, parrillas y casas de empanadas.",
        ], gap=0.05)
        insight(fig, 0.28, "Resultado: una base analítica reproducible, no oficial, lista para validación "
                "territorial y eventual incorporación a la línea de análisis territorial gastronómico "
                "(con aprobación).", color=VERDE)
        foot(fig, "padrón candidato no oficial · método replicable en otros rubros gastronómicos.")
        pdf.savefig(fig); plt.close(fig)

        d = pdf.infodict()
        d["Title"] = "Casas de pastas en CABA — Padrón candidato integrado (V3 ejecutivo)"
        d["Author"] = "Análisis territorial gastronómico"
        d["Subject"] = "Padrón candidato no oficial (AGC + OSM + Google Places). Pendiente de validación manual."

    escribir_md(hoy, rv2, rqc, com, bar, dens_com, dens_bar, combos, cobertura, hist)
    print(f"PDF V3 generado: {PDF}")
    print(f"Páginas: 22 | tamaño: {PDF.stat().st_size/1024:.0f} KB")
    print(f"MD V3 generado: {MD}")
    print(f"GeoJSON sanitizado v2: {len(feats)} puntos")


def escribir_md(hoy, rv2, rqc, com, bar, dens_com, dens_bar, combos, cobertura, hist):
    n_tot = rv2["candidatos_unicos"]
    L = ["# Casas de pastas en CABA — Padrón candidato integrado (V3 ejecutivo)\n"]
    L.append(f"_Fecha: {hoy} · Versión V3 · **Padrón candidato no oficial, pendiente de validación manual.**_\n")
    L.append("> El registro oficial muestra el núcleo administrativo estricto, pero el universo operativo "
             "probable de casas de pastas en la Ciudad es más amplio. El padrón candidato integrado combina "
             "AGC, OpenStreetMap y Google Places para construir una base analítica, no oficial, pendiente de "
             "validación manual.\n")
    L.append("## Indicadores\n")
    L.append(f"- **{n_tot}** candidatos únicos · **{rv2['independientes']}** independientes / de barrio · "
             f"**{rv2['cadenas']}** en cadenas · **{rv2['multifuente']}** multifuente · "
             f"**{rv2['revision_manual_prioritaria']}** en revisión manual · "
             "**259** georreferenciados.\n")
    L.append("## 1. ¿Qué universo permite ver el cruce de fuentes?\n")
    L.append(f"{n_tot} candidatos únicos. No es un padrón oficial ni un censo definitivo: es una base "
             "analítica para validación territorial.\n")
    L.append("## 2. ¿Por qué el registro oficial no alcanza?\n")
    L.append("| Fuente | Naturaleza | Detectados | Qué puede / no puede afirmar |")
    L.append("|---|---|---|---|")
    L.append("| AGC / F02 | Registro administrativo **oficial** | 11 | Habilitaciones; **no implica local activo** |")
    L.append("| OpenStreetMap | **Abierta auxiliar** | 152 | Cobertura territorial; **no oficial** |")
    L.append("| Google Places | **Operativa no oficial** | 151 | Visibilidad comercial; **no gubernamental** |")
    L.append(f"| Integrado v2 | **Padrón candidato** | {n_tot} | Unión deduplicada; **a validar** |")
    L.append("\n_Detectados por fuente dentro del padrón post-deduplicación; no equivale a resultados brutos._\n")
    L.append("## 3. ¿Dónde se concentran?\n")
    L.append("- **Comunas (cantidad):** " + ", ".join(f"{c} ({n})" for c, n in com.most_common(5)) + ".")
    L.append("- **Barrios (cantidad):** " + ", ".join(f"{b} ({n})" for b, n in bar.most_common(5)) + ".\n")
    L.append("## 4. ¿Qué cambia con la densidad por km²?\n")
    L.append("- **Densidad comuna (cand./km²):** " + ", ".join(f"{c} ({v:.2f})" for c, v in dens_com[:5]) + ".")
    L.append("- **Densidad barrio (cand./km²):** " + ", ".join(f"{b} ({v:.2f})" for b, v in dens_bar[:5]) +
             ". No es densidad por habitante; el ranking difiere del de cantidad absoluta.\n")
    L.append("## 5. ¿Qué barrios son polos? \n")
    L.append("Palermo y Caballito lideran; Recoleta y Belgrano empatan en el tercer lugar (22 c/u). Mapas de "
             "zoom para Palermo, Caballito y Recoleta.\n")
    L.append("## 6. ¿Cadenas o casas de barrio?\n")
    L.append(f"> El universo candidato no está compuesto solo por franquicias: predominan las casas "
             f"independientes y de escala barrial ({rv2['independientes']} de {n_tot}; {rv2['cadenas']} en cadenas).\n")
    L.append("## 7. Principales cadenas (control de cobertura)\n")
    L.append(", ".join(f"{CADENA_CAPS.get(r['cadena'], r['cadena'].upper())} ({r['sucursales']})"
                       for r in cobertura[:7]) + ".\n")
    L.append("## 8. Núcleo de mayor respaldo cruzado\n")
    L.append(f"- {rv2['multifuente']} candidatos multifuente (Google + OSM): base más sólida. Combinaciones: "
             f"solo OSM {combos.get('osm',0)} · solo Google {combos.get('google',0)} · Google+OSM "
             f"{combos.get('google+osm',0)} · solo AGC {combos.get('agc',0)}. Aparecer en más de una fuente "
             "aumenta la probabilidad de existencia, pero no la confirma: no reemplaza la validación.\n")
    L.append("## 9. ¿Qué queda pendiente?\n")
    L.append("El padrón candidato requiere validación manual y territorial antes de convertirse en una base "
             "definitiva.\n")
    L.append(f"- Validar los {rv2['revision_manual_prioritaria']} casos en revisión manual.\n"
             "- Confirmar el núcleo de mayor respaldo cruzado.\n"
             "- Revisar especialmente casas independientes y de barrio.\n"
             "- Verificar cadenas y sucursales con fuentes propias o revisión manual.\n"
             "- Documentar posibles bajas, cierres o casos mal clasificados.\n"
             f"- Mantener el {n_tot} como cifra de trabajo, no como cifra pública definitiva.\n"
             "\n(El detalle de los chequeos de calidad queda en el anexo metodológico interno.)\n")
    L.append("## Casos emblemáticos (a validar documentalmente)\n")
    if [h for h in hist if h["usar_en_informe"] == "si"]:
        L.append("- **LA JUVENIL** — fundada el 1 de diciembre de 1959 (Colegiales); negocio familiar de tres "
                 "generaciones. Fuentes: La Nación, El Cronista (caso documentado).")
    L.append("- Raviolón (1971, según fuentes secundarias de prensa) y Master Pastas (1995, según su sitio "
             "oficial) a confirmar; Biasatti reciente (2020). Multipasta, Pastas Mazzeo y Caprizzi sin año "
             "verificable. Información histórica documentada en anexo metodológico interno. No se infiere "
             "antigüedad por fama.\n")
    L.append("## 10. ¿Qué aporta esta metodología?\n")
    L.append("Un método replicable (registro oficial + fuentes abiertas + señal operativa + auditoría de "
             "calidad) para otros rubros: pizzerías, heladerías artesanales, cafeterías de especialidad, "
             "panaderías, parrillas, casas de empanadas.\n")
    L.append("## ¿Qué decisión permite tomar este informe?\n")
    L.append(f"- Priorizar validación territorial en barrios polo; empezar por el núcleo de mayor respaldo "
             f"cruzado ({rv2['multifuente']} multifuente); revisar los {rv2['revision_manual_prioritaria']} "
             f"casos manuales; priorizar independientes/de barrio; no usar el {n_tot} como cifra pública "
             "definitiva hasta validar; usar la metodología como prueba de concepto del análisis "
             "territorial gastronómico.\n")
    L.append("**Recomendación operativa (2–4 semanas):** 1) validar muestra piloto en un barrio; 2) depurar "
             "cadenas y nombres genéricos; 3) confirmar multifuente; 4) revisar independientes prioritarios; "
             "5) definir si el padrón candidato alimenta la línea de análisis territorial gastronómico.\n")
    L.append("## Limitaciones\n")
    L.append("- No es censo definitivo ni padrón oficial. Google/OSM no son oficiales. AGC es oficial pero "
             "angosto y no implica local activo. Puede haber locales cerrados o faltantes. La deduplicación "
             "es heurística. Falta validación manual/campo.\n")
    MD.write_text("\n".join(L), encoding="utf-8")


if __name__ == "__main__":
    main()
