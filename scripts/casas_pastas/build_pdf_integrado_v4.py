"""Informe ejecutivo V4 — Casas de pastas en CABA, padrón candidato integrado.

Versión ejecutiva para revisión de jefatura alta / ministro. Misma metodología, KPIs y
contenido central que la V3, con un cambio principal:
  1. Portada más institucional / estilo DataGastro (con bajada no técnica y autoría sobria,
     sin tarjetas de KPIs en portada para no repetirlos con la página de Indicadores).
  Se conserva el cierre metodológico (PREGUNTA 10) como última página, para no terminar en
  Limitaciones. 23 páginas, igual que la V3.

NO recalcula datos: lee los mismos archivos depurados que la V3. No cambia padrón, clasificación,
mapas, rankings, fuentes ni recall. Usa SOLO agregados y mapas anonimizados (sin nombres,
direcciones, razón social, place_id, teléfonos, emails, ratings ni API key). No hace requests.
No commitea.

Salidas (nuevas, no sobrescriben la V3):
  outputs/casas_pastas_reporte/INFORME_CASAS_PASTAS_INTEGRADO_V4.pdf
  outputs/casas_pastas_reporte/INFORME_CASAS_PASTAS_INTEGRADO_V4.md
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
PDF = REP / "INFORME_CASAS_PASTAS_INTEGRADO_V4.pdf"
MD = REP / "INFORME_CASAS_PASTAS_INTEGRADO_V4.md"

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
    "A_validado_manual": "#d62728",
    "A_documental_validado_manual": "#8c564b",
    "A_google_recall_validado_manual": "#e377c2",
    "A_agc_oficial_estricto": "#2c7fb8",
    "A_google_probable": "#f08c00",
    "A_osm_auxiliar": "#7b5ea7",
    "B_revision_manual": "#999999",
}
CLASE_LABEL = {
    "A_integrado_multifuente": "Multifuente (2 o más fuentes)",
    "A_validado_manual": "Validado en revisión manual",
    "A_documental_validado_manual": "Documental (fuente histórica)",
    "A_google_recall_validado_manual": "Recall complementario (validado)",
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
    # Padrón DEPURADO (tras revisión manual). Los agregados sanitizados los genera
    # aplicar_revision_diego.py; aquí solo se lee para producir el informe.
    rv2 = kv(read_csv(INT / "resumen_integrado_v3_depurado.csv"))
    pad = read_csv(INT / "padron_candidato_integrado_v3_depurado.csv")

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

    # Cobertura de cadenas recomputada desde el padrón depurado.
    cad_cnt = Counter(r["cadena_detectada"] for r in pad
                      if r["es_cadena_detectada"] == "si" and r["cadena_detectada"])
    cobertura = [{"cadena": k, "sucursales": v} for k, v in sorted(cad_cnt.items(), key=lambda x: -x[1])]

    pts = []
    for r in pad:
        la, lo = fnum(r["lat"]), fnum(r["lon"])
        if la is None or lo is None:
            continue
        pts.append({"lat": la, "lon": lo, "clase": r["clase_integrada"], "barrio": r["barrio"]})

    n_tot, n_ind, n_cad = rv2["candidatos_unicos"], int(rv2["independientes"]), int(rv2["cadenas"])
    n_multi = int(rv2["multifuente"])
    n_conf = rv2["confirmados_revision_manual"]
    n_desc = rv2["descartados_revision_manual"]
    georref = rv2["georreferenciados"]
    con_g = sum(1 for r in pad if "google" in r["fuentes_detectan"])
    con_o = sum(1 for r in pad if "osm" in r["fuentes_detectan"])
    con_a = sum(1 for r in pad if "agc" in r["fuentes_detectan"])

    clases_presentes = {p["clase"] for p in pts}

    def leyenda(ax, loc="lower left"):
        leg = [Line2D([0], [0], marker="o", color="w", markerfacecolor=c, markersize=8, label=CLASE_LABEL[k])
               for k, c in CLASE_COLOR.items() if k in clases_presentes]
        ax.legend(handles=leg, loc=loc, fontsize=7.3, frameon=False)

    top_barrios = set(b for b, _ in bar.most_common(6))

    with PdfPages(PDF) as pdf:
        # 1. Portada institucional DataGastro (V4) — sin KPIs (no repetir con Indicadores).
        fig = page()
        # Banda institucional superior.
        fig.patches.append(Rectangle((0, 0.70), 1, 0.30, transform=fig.transFigure, facecolor=AZUL, zorder=0))
        # Filete rojo de acento sobre el borde inferior de la banda.
        fig.patches.append(Rectangle((0, 0.694), 1, 0.006, transform=fig.transFigure, facecolor=ROJO, zorder=1))
        # Masthead de marca.
        fig.text(0.07, 0.945, "DataGastro", color="white", fontsize=21, fontweight="bold")
        fig.lines.append(Line2D([0.07, 0.215], [0.927, 0.927], color=ROJO, lw=2.2, transform=fig.transFigure))
        fig.text(0.07, 0.895, "DIAGNÓSTICO TERRITORIAL GASTRONÓMICO", color="#cdd9e5",
                 fontsize=10.5, fontweight="bold")
        # Título principal.
        fig.text(0.07, 0.805, "Casas de pastas en la\nCiudad de Buenos Aires", color="white",
                 fontsize=26, fontweight="bold", va="center")
        # Subtítulo institucional bajo la banda.
        fig.text(0.07, 0.628, "Padrón candidato depurado y lectura territorial del rubro",
                 fontsize=14, color=AZUL, fontweight="bold")
        fig.lines.append(Line2D([0.07, 0.60], [0.598, 0.598], color=ROJO, lw=2.5, transform=fig.transFigure))
        # Bajada breve, no técnica.
        bajada = ("Este informe integra registro oficial, fuentes abiertas, señales operativas y revisión "
                  "manual para aproximar un universo operativo probable de casas de pastas en CABA. El "
                  "resultado no constituye un censo definitivo ni reemplaza al registro oficial: funciona "
                  "como base analítica para orientar validaciones y decisiones territoriales.")
        yb = 0.545
        for ln in textwrap.wrap(bajada, 90):
            fig.text(0.07, yb, ln, fontsize=11.5, color="#333333", va="top")
            yb -= 0.028
        # Línea sobria de capas metodológicas (cualitativa, no numérica).
        capas = "Registro oficial   ·   Fuentes abiertas   ·   Señales operativas   ·   Revisión manual"
        fig.patches.append(Rectangle((0.07, 0.30), 0.86, 0.052, transform=fig.transFigure,
                                     facecolor=GRISCLARO, edgecolor=AZUL, lw=1.0))
        fig.text(0.5, 0.326, capas, ha="center", va="center", fontsize=10, color=AZUL, fontweight="bold")
        # Autoría sobria.
        fig.lines.append(Line2D([0.07, 0.93], [0.135, 0.135], color="#dddddd", lw=0.8, transform=fig.transFigure))
        fig.text(0.07, 0.115, "Análisis y desarrollo: Diego Aleman", fontsize=10.5, color=AZUL,
                 fontweight="bold", va="top")
        fig.text(0.07, 0.088, "Padrón candidato no oficial · sujeto a verificación territorial.",
                 fontsize=8.5, color=GRIS, style="italic", va="top")
        pdf.savefig(fig); plt.close(fig)

        # 2. Resumen ejecutivo
        fig = page()
        head(fig, "RESUMEN EJECUTIVO", "Qué muestra el cruce de fuentes",
             "Un universo operativo probable más amplio que el registro oficial, con foco en las casas de barrio.", "2 / 23")
        cards(fig, 0.74, [(n_tot, "candidatos únicos", AZUL), (n_ind, "independientes", VERDE),
                          (n_cad, "en cadenas", NARANJA), (n_multi, "multifuente", VERDE)], h=0.105)
        bullets(fig, 0.66, [
            "El registro oficial muestra un núcleo administrativo estricto. El cruce de fuentes permite "
            "aproximar un universo operativo probable más amplio.",
            f"La revisión manual de casos dudosos permitió depurar el padrón candidato, que queda en {n_tot} "
            "establecimientos posibles.",
            f"El resultado muestra fuerte presencia de casas independientes y de escala barrial "
            f"({n_ind} de {n_tot}); {n_cad} pertenecen a cadenas (control de cobertura) y {n_multi} aparecen "
            "en más de una fuente (mayor respaldo cruzado).",
        ], gap=0.05)
        insight(fig, 0.24, "\"Candidato\": establecimiento detectado por una o más fuentes como posible casa "
                "de pastas, pastificio o comercio de pastas frescas. No implica validación definitiva ni "
                "actividad actual confirmada por una fuente oficial.", color=AZUL, h=0.10)
        foot(fig, f"padrón candidato no oficial · {n_tot} candidatos · {n_ind} independientes · {n_cad} en "
                  f"cadenas · {n_multi} multifuente.")
        pdf.savefig(fig); plt.close(fig)

        # 3. Hallazgo principal
        fig = page()
        head(fig, "HALLAZGO PRINCIPAL", "Registro oficial vs. universo operativo probable",
             "El registro oficial muestra el núcleo estricto; el padrón candidato amplía la lectura.", "3 / 23")
        ax = fig.add_axes([0.13, 0.40, 0.72, 0.34])
        n_tot_i = int(n_tot)
        valores = [11, n_multi, n_tot_i]
        labels = ["AGC oficial\nestricto", "Núcleo\nmultifuente", "Padrón candidato\ndepurado"]
        b = ax.bar(labels, valores, color=[AZUL2, VERDE, AZUL], width=0.6)
        for bi, v in zip(b, valores):
            ax.text(bi.get_x() + bi.get_width() / 2, v + 4, str(v), ha="center", fontweight="bold", color=AZUL)
        ax.set_ylim(0, n_tot_i * 1.15)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.set_ylabel("candidatos / registros", fontsize=9)
        bullets(fig, 0.32, [
            "El gráfico muestra tres niveles de lectura, no padrones equivalentes.",
            "AGC representa el núcleo administrativo oficial y estricto; el núcleo multifuente reúne "
            "candidatos detectados por más de una fuente; el padrón integrado amplía la mirada al universo "
            "operativo probable, sujeto a validación.",
        ], gap=0.05)
        foot(fig, "AGC = registro administrativo oficial · OSM = fuente abierta auxiliar · Google = señal operativa no oficial.")
        pdf.savefig(fig); plt.close(fig)

        # 4. Fuentes y capas (P2)
        fig = page()
        head(fig, "PREGUNTA 2", "¿Por qué el registro oficial no alcanza por sí solo?",
             "Respuesta: porque mide habilitaciones de un rubro estricto; las fuentes abiertas y operativas amplían cobertura.", "4 / 23")
        ax = fig.add_axes([0.07, 0.55, 0.86, 0.24]); ax.axis("off")
        data = [["AGC / F02", "Registro oficial", str(con_a), "Habilitaciones; NO implica local activo"],
                ["OpenStreetMap", "Abierta auxiliar", str(con_o), "Cobertura territorial; no oficial"],
                ["Google Places", "Operativa no oficial", str(con_g), "Visibilidad comercial; no gubernamental"],
                ["Padrón depurado", "Padrón candidato", str(n_tot), "Unión deduplicada + revisión manual"]]
        t = ax.table(cellText=data, colLabels=["Fuente", "Naturaleza", "Candidatos", "Qué puede / no puede afirmar"],
                     colWidths=[0.19, 0.21, 0.13, 0.47], loc="upper center", cellLoc="center")
        t.auto_set_font_size(False); t.set_fontsize(9); t.scale(1, 1.6)
        for (r, _c), cell in t.get_celld().items():
            cell.set_edgecolor("#dddddd")
            if r == 0:
                cell.set_facecolor(AZUL); cell.set_text_props(color="white", fontweight="bold")
            elif r % 2 == 0:
                cell.set_facecolor(GRISCLARO)
        fig.text(0.07, 0.52, "Los conteos corresponden al padrón integrado ya consolidado; no representan "
                 "resultados brutos de búsqueda.", fontsize=8.3, color=GRIS, style="italic")
        bullets(fig, 0.46, [
            "Ninguna fuente sola alcanza el universo real: AGC es preciso pero angosto; OSM y Google amplían "
            "cobertura pero no son oficiales.",
            "Aparecer en más de una fuente sube la confianza; aparecer en una sola se conserva como candidato.",
        ])
        foot(fig, "el padrón es candidato; el número definitivo requiere verificación territorial posterior.")
        pdf.savefig(fig); plt.close(fig)

        # 5. Mapa general (P3)
        fig = page()
        head(fig, "PREGUNTA 3", "¿Dónde se concentran las casas de pastas candidatas?",
             "Respuesta: en el corredor norte–centro de la Ciudad, con polos en Palermo, Caballito y Recoleta/Belgrano.", "5 / 23")
        ax = fig.add_axes([0.06, 0.13, 0.88, 0.70])
        for f in gc["features"]:
            for xs, ys in poligonos(f["geometry"]):
                ax.plot(xs, ys, color="#cfcfcf", lw=0.6, zorder=1)
        for p in pts:
            ax.scatter(p["lon"], p["lat"], s=14, color=CLASE_COLOR.get(p["clase"], "#999"),
                       edgecolor="white", lw=0.25, zorder=3)
        ax.set_aspect(1.28); ax.axis("off")
        leyenda(ax)
        n_sin = int(n_tot) - int(georref)
        foot(fig, f"{georref} de los {n_tot} candidatos cuentan con coordenadas suficientes para su ubicación "
                  f"puntual; los {n_sin} restantes integran el conteo general pero no se grafican. «Recall "
                  "complementario» refiere a una búsqueda adicional de cobertura. Puntos anonimizados (sin "
                  "nombres ni direcciones); contornos: comunas GCBA.")
        pdf.savefig(fig); plt.close(fig)

        # 6. Coroplético comuna - cantidad
        fig = page()
        head(fig, "CONCENTRACIÓN TERRITORIAL", "Concentración territorial por comuna",
             "Cantidad de candidatos por comuna.", "6 / 23")
        choropleth(fig, [0.08, 0.20, 0.82, 0.62], gc["features"], "comuna", dict(com), "YlOrRd",
                   "Candidatos por comuna (cantidad)", etiqueta_num=True)
        insight(fig, 0.10, "Las comunas con más candidatos muestran zonas de alta oferta comercial y "
                "residencial, pero no necesariamente la mayor densidad relativa.", color=NARANJA, h=0.07)
        foot(fig, "cantidad absoluta por comuna; comparar con densidad (pág. 8).")
        pdf.savefig(fig); plt.close(fig)

        # 7. Coroplético comuna - densidad
        fig = page()
        head(fig, "DENSIDAD TERRITORIAL", "Densidad territorial por comuna",
             "Candidatos por km² de superficie oficial.", "7 / 23")
        choropleth(fig, [0.08, 0.20, 0.82, 0.62], gc["features"], "comuna", dcom, "PuBuGn",
                   "Densidad por comuna (candidatos/km²)", etiqueta_num=True)
        insight(fig, 0.10, "La densidad se calcula por superficie; una etapa posterior puede incorporar "
                "población para estimar cobertura relativa por habitante.", color=AZUL2, h=0.07)
        foot(fig, "el ranking por densidad difiere del de cantidad absoluta.")
        pdf.savefig(fig); plt.close(fig)

        # 8. Ranking comuna
        fig = page()
        head(fig, "PREGUNTA 4", "¿Qué cambia cuando miramos densidad por km²?",
             "Respuesta: el orden cambia; comunas chicas y céntricas escalan posiciones.", "8 / 23")
        topc = com.most_common(8)[::-1]
        barh(fig, [0.16, 0.45, 0.74, 0.29], [f"Comuna {c}" for c, _ in topc], [n for _, n in topc],
             AZUL2, "Top comunas por cantidad", "candidatos")
        dc = dens_com[:8][::-1]
        barh(fig, [0.16, 0.085, 0.74, 0.29], [f"Comuna {c}" for c, _ in dc], [v for _, v in dc],
             "#31a354", "Top comunas por densidad (cand./km²)", "", valfmt="{:.2f}")
        foot(fig, "cantidad y densidad miden cosas distintas; ambas son lecturas válidas y complementarias.")
        pdf.savefig(fig); plt.close(fig)

        # 9. Coroplético barrio - cantidad
        fig = page()
        head(fig, "CONCENTRACIÓN TERRITORIAL", "Concentración por barrio (cantidad)",
             "Barrios líderes: Palermo, Caballito, Recoleta, Belgrano y Villa Urquiza.", "9 / 23")
        choropleth(fig, [0.06, 0.16, 0.86, 0.66], gb["features"], "barrio", dict(bar), "YlOrRd",
                   "Candidatos por barrio (cantidad)", label_keys=top_barrios)
        foot(fig, "barrios con 0 candidatos en gris claro. Cantidad absoluta.")
        pdf.savefig(fig); plt.close(fig)

        # 10. Coroplético barrio - densidad
        fig = page()
        head(fig, "DENSIDAD TERRITORIAL", "Densidad por barrio (candidatos/km²)",
             "El ranking por densidad puede diferir del de cantidad absoluta.", "10 / 23")
        choropleth(fig, [0.06, 0.16, 0.86, 0.66], gb["features"], "barrio", dbar, "PuBuGn",
                   "Densidad por barrio (candidatos/km²)", label_keys=set(b for b, _ in dens_bar[:5]))
        insight(fig, 0.08, "Los barrios con más candidatos no siempre son los más densos en relación con su "
                "superficie.", color=AZUL2, h=0.06)
        foot(fig, "la densidad se calcula por superficie; una etapa posterior puede incorporar población.")
        pdf.savefig(fig); plt.close(fig)

        # 11. Ranking barrio
        fig = page()
        topb_full = bar.most_common(10)
        lider = topb_full[0]
        seg = topb_full[1:3]  # los dos que siguen
        sub_11 = (f"{lider[0]} lidera ({lider[1]}); " +
                  " y ".join(b for b, _ in seg) + f" le siguen ({seg[0][1]} c/u)."
                  if seg and seg[0][1] == seg[-1][1] else
                  f"{lider[0]} lidera; " + ", ".join(f"{b} ({n})" for b, n in seg) + ".")
        head(fig, "PREGUNTA 5", "¿Qué barrios aparecen como polos del universo candidato?", sub_11, "11 / 23")
        topb = topb_full[::-1]
        barh(fig, [0.22, 0.45, 0.70, 0.29], [b for b, _ in topb], [n for _, n in topb],
             "#7b5ea7", "Top barrios por cantidad", "candidatos")
        db = dens_bar[:10][::-1]
        barh(fig, [0.22, 0.085, 0.70, 0.29], [b for b, _ in db], [v for _, v in db],
             "#dd8452", "Top barrios por densidad (cand./km²)", "", valfmt="{:.2f}")
        foot(fig, "los mapas de zoom muestran los tres barrios con más candidatos del padrón depurado.")
        pdf.savefig(fig); plt.close(fig)

        # 12-14. Zooms de los tres barrios con más candidatos (depurado).
        coment_barrio = {
            "Palermo": "Palermo concentra el mayor volumen absoluto de candidatos, combinando cadenas, "
                       "locales independientes y puntos detectados por más de una fuente.",
            "Caballito": "Caballito combina fuerte presencia de casas de barrio con una densidad alta sobre "
                         "una superficie media.",
            "Belgrano": "Belgrano se ubica entre los barrios con más candidatos del corredor norte de la Ciudad.",
            "Recoleta": "Recoleta, de superficie acotada, se cuenta entre los barrios de mayor densidad.",
        }
        top3 = [b for b, _ in bar.most_common(3)]
        for k, barrio in enumerate(top3):
            num = f"{12 + k} / 23"
            coment = coment_barrio.get(barrio, f"{barrio} es uno de los barrios con más candidatos del "
                                               "padrón depurado.")
            fig = page()
            head(fig, "ZOOM TERRITORIAL", f"Zoom: {barrio}",
                 f"{bar.get(barrio, 0)} candidatos en {barrio} (padrón depurado, anonimizado).", num)
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
            bpts = {p["clase"] for p in pts if p["barrio"] == barrio}
            leg = [Line2D([0], [0], marker="o", color="w", markerfacecolor=c, markersize=8, label=CLASE_LABEL[k])
                   for k, c in CLASE_COLOR.items() if k in bpts]
            ax.legend(handles=leg, loc="upper center", bbox_to_anchor=(0.5, -0.03), ncol=3,
                      fontsize=7.5, frameon=False)
            for j, ln in enumerate(textwrap.wrap(coment, 96)):
                fig.text(0.07, 0.165 - j * 0.020, ln, fontsize=10.5, color="#222222", style="italic", va="top")
            foot(fig, "solo puntos anonimizados dentro del barrio; sin nombres ni direcciones.")
            pdf.savefig(fig); plt.close(fig)

        # 15. Cadenas e independientes (P6)
        fig = page()
        head(fig, "PREGUNTA 6", "¿Predominan las cadenas o las casas de barrio?",
             "En el universo candidato predominan las casas independientes y de escala barrial.", "15 / 23")
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
             "Respuesta: La Juvenil encabeza; el resto son cadenas medianas o chicas.", "16 / 23")
        top_cad = [(CADENA_CAPS.get(r["cadena"], r["cadena"].upper()), int(r["sucursales"])) for r in cobertura][:8][::-1]
        barh(fig, [0.34, 0.20, 0.56, 0.60], [c for c, _ in top_cad], [n for _, n in top_cad],
             NARANJA, "Cadenas con más sucursales (control de cobertura)", "sucursales")
        foot(fig, "ranking de control de cobertura. No incluye categorías genéricas (p. ej. 'pastas frescas'), que se tratan como independientes.")
        pdf.savefig(fig); plt.close(fig)

        # 17. Núcleo multifuente (P8)
        fig = page()
        head(fig, "PREGUNTA 8", "¿Cuál es el núcleo de mayor respaldo cruzado?",
             "Respuesta: los candidatos detectados por más de una fuente (multifuente).", "17 / 23")
        orden = [("documental", "Documental (revisión)"), ("google_recall", "Recall complementario"),
                 ("agc", "Solo AGC (oficial estricto)"), ("google", "Solo Google (operativo)"),
                 ("osm", "Solo OSM (auxiliar)"), ("google+osm", "Google + OSM (multifuente)")]
        barh(fig, [0.32, 0.50, 0.58, 0.30], [e for _, e in orden][::-1],
             [combos.get(k, 0) for k, _ in orden][::-1], VERDE, "Candidatos por origen principal", "candidatos")
        bullets(fig, 0.40, [
            f"{n_multi} candidatos aparecen en más de una fuente (Google + OSM): núcleo de mayor respaldo cruzado.",
            "Aparecer en más de una fuente aumenta la probabilidad de existencia, pero no la confirma: no "
            "reemplaza la validación territorial.",
            "Los de una sola fuente se conservan como candidatos (oficial estricto si es AGC, operativo si es "
            "Google, auxiliar si es OSM), sin degradar a los independientes.",
        ])
        foot(fig, "AGC oficial estricto no implica local activo; el núcleo multifuente es la base para empezar la validación.")
        pdf.savefig(fig); plt.close(fig)

        # 18. ¿Qué aportó la revisión manual?
        fig = page()
        head(fig, "DEPURACIÓN", "¿Qué aportó la revisión manual?",
             "La revisión manual permitió depurar los casos dudosos detectados por el cruce de fuentes.", "18 / 23")
        bullets(fig, 0.80, [
            f"Se confirmaron {n_conf} candidatos y se excluyeron {n_desc} casos del padrón principal.",
            "Los casos excluidos correspondían a restaurantes, locales cerrados, registros genéricos o "
            "rubros no incluidos.",
            "Una búsqueda complementaria de cobertura permitió detectar candidatos adicionales, "
            f"incorporados solo tras revisión y trazabilidad ({rv2.get('incorporados_recall_google', '0')}).",
            f"El padrón depurado queda conformado por {n_tot} establecimientos posibles.",
        ], gap=0.05)
        insight(fig, 0.30, "La revisión manual y documental mejora la depuración, pero no reemplaza la "
                "verificación territorial final. El detalle por caso queda en el anexo metodológico interno.",
                color=AZUL)
        foot(fig, "la depuración consolida el padrón; no se listan casos individuales en este documento.")
        pdf.savefig(fig); plt.close(fig)

        # 19. ¿Para qué sirve este diagnóstico?
        fig = page()
        head(fig, "USO EJECUTIVO", "¿Para qué sirve este diagnóstico?",
             "Una base territorial para orientar decisiones y priorizar validaciones.", "19 / 23")
        bullets(fig, 0.80, [
            "Identificar zonas de mayor concentración territorial del rubro.",
            "Distinguir entre núcleo oficial, núcleo multifuente y universo operativo probable.",
            "Priorizar barrios y candidatos para una validación posterior.",
            "Reconocer el peso de las casas independientes y de escala barrial.",
            "Probar una metodología replicable para otros rubros gastronómicos.",
        ], gap=0.05)
        insight(fig, 0.28, "Es una base analítica candidata, no oficial: orienta el trabajo territorial y no "
                "reemplaza al registro oficial.", color=VERDE)
        foot(fig, "padrón candidato no oficial · base para validación territorial.")
        pdf.savefig(fig); plt.close(fig)

        # 20. Casos con respaldo documental
        fig = page()
        head(fig, "TRAYECTORIA", "Casos con respaldo documental",
             "Además del análisis territorial, se identificaron establecimientos con fuentes sobre "
             "trayectoria, origen familiar o antigüedad.", "20 / 23")
        fig.text(0.07, 0.835, "No se trata de un ranking histórico exhaustivo, sino de ejemplos verificables "
                 "dentro del rubro.", fontsize=10.5, color="#333333", va="top")
        docs_casos = [
            ("Pastas Amelia — Boedo · 1948",
             "Caso documentado por prensa nacional, vinculado a la familia Palazzo y a una tradición "
             "artesanal de pastas frescas, especialmente fusilis al fierrito. Se incorpora como ejemplo de "
             "trayectoria barrial con respaldo documental."),
            ("La Hispano Americana — San Telmo · más de medio siglo",
             "Casa de pastas asociada a inmigrantes gallegos y continuidad familiar en un barrio histórico "
             "de la Ciudad. Se incluye como ejemplo de persistencia comercial y tradición familiar "
             "documentada."),
            ("La Juvenil — Colegiales · 1959",
             "Marca familiar con varias generaciones vinculadas a la elaboración de pastas frescas y "
             "posterior expansión territorial. Se incluye como caso de trayectoria, escala y continuidad "
             "empresarial dentro del rubro."),
            ("Pastas Bayo — Belgrano · 1978",
             "Casa de pastas familiar con permanencia en la misma dirección desde su apertura. Se incluye "
             "como ejemplo de continuidad barrial y especialización en pastas frescas."),
        ]
        yb = 0.80
        for titulo_c, desc_c in docs_casos:
            fig.text(0.07, yb, titulo_c, fontsize=11, fontweight="bold", color=AZUL, va="top")
            lines = textwrap.wrap(desc_c, 98)
            for j, ln in enumerate(lines):
                fig.text(0.07, yb - 0.026 - j * 0.0185, ln, fontsize=9, color="#333333", va="top")
            yb -= 0.034 + len(lines) * 0.0185 + 0.018
        cierre_doc = ("Estos casos se incluyen por contar con fuentes documentales identificables; no agotan "
                      "la historia del rubro ni prueban por sí solos cuál es la casa de pastas más antigua "
                      "de la Ciudad.")
        for j, ln in enumerate(textwrap.wrap(cierre_doc, 100)):
            fig.text(0.07, 0.20 - j * 0.020, ln, fontsize=9, color=GRIS, style="italic", va="top")
        fig.text(0.07, 0.15, "Fuentes documentales: prensa nacional y sitios oficiales de los "
                 "establecimientos (ver detalle en la página siguiente).", fontsize=8.5, color=GRIS, va="top")
        foot(fig, "no se citan reseñas como fuente principal; las fuentes se detallan en la página siguiente.")
        pdf.savefig(fig); plt.close(fig)

        # 21. Fuentes documentales de la sección Trayectoria
        fig = page()
        head(fig, "REFERENCIAS", "Fuentes documentales de la sección Trayectoria",
             "Prensa nacional y sitios oficiales de los establecimientos. No se citan reseñas.", "21 / 23")
        fuentes_doc = [
            ("Pastas Amelia",
             "La Nación — nota sobre la fábrica de pastas de Boedo en funcionamiento desde 1948 "
             "(adaptación durante la pandemia).",
             "lanacion.com.ar"),
            ("La Hispano Americana",
             "Sitio oficial de La Hispano Americana — información institucional sobre su trayectoria "
             "en San Telmo e historia familiar.",
             "lahispanoamericana.com.ar"),
            ("La Juvenil",
             "Sitio oficial de La Juvenil, sección \"La empresa\"; y La Nación, nota sobre el "
             "crecimiento familiar y las nuevas generaciones.",
             "lajuvenilpastas.com.ar · lanacion.com.ar"),
            ("Pastas Bayo",
             "Sitio oficial de Pastas Bayo, sección institucional — historia de la marca desde 1978.",
             "pastasbayo.com.ar"),
        ]
        yb = 0.82
        for nombre_f, ref, url in fuentes_doc:
            fig.text(0.07, yb, nombre_f, fontsize=11, fontweight="bold", color=AZUL, va="top")
            lines = textwrap.wrap(ref, 98)
            for j, ln in enumerate(lines):
                fig.text(0.07, yb - 0.026 - j * 0.0185, ln, fontsize=9, color="#333333", va="top")
            fig.text(0.07, yb - 0.026 - len(lines) * 0.0185, url, fontsize=8, color=AZUL2, va="top")
            yb -= 0.05 + len(lines) * 0.0185 + 0.026
        nota_f = ("Las fuentes corresponden a los medios y sitios oficiales originales. Las búsquedas web "
                  "asistidas se usaron solo como herramienta de localización, no como fuente. El detalle "
                  "completo (títulos y enlaces) se conserva en el anexo metodológico interno.")
        for j, ln in enumerate(textwrap.wrap(nota_f, 100)):
            fig.text(0.07, 0.24 - j * 0.020, ln, fontsize=8.5, color=GRIS, style="italic", va="top")
        foot(fig, "referencias de la sección Trayectoria; no constituyen un ranking histórico ni prueban antigüedades relativas.")
        pdf.savefig(fig); plt.close(fig)

        # 22. Limitaciones
        fig = page()
        head(fig, "ALCANCE", "Limitaciones", "Qué no afirma este informe.", "22 / 23")
        bullets(fig, 0.82, [
            "Sigue siendo un padrón candidato; no reemplaza al registro oficial.",
            "No implica local activo confirmado por una fuente oficial.",
            "Google Places y OpenStreetMap no son fuentes oficiales; reflejan visibilidad comercial y "
            "relevamiento colaborativo.",
            "Puede haber locales cerrados (que figuran) o faltantes (que no figuran en ninguna fuente).",
            "La densidad se expresa por superficie; una etapa posterior puede incorporar población para "
            "estimar cobertura relativa por habitante.",
            "La revisión manual de escritorio mejora la depuración, pero no reemplaza la verificación "
            "territorial final si el informe se usa públicamente.",
        ], gap=0.05)
        foot(fig, "padrón candidato no oficial · la verificación territorial final queda pendiente.")
        pdf.savefig(fig); plt.close(fig)

        # 23. Cierre metodológico (P10) — se conserva para no terminar en Limitaciones.
        fig = page()
        head(fig, "PREGUNTA 10", "¿Qué aporta esta metodología al análisis gastronómico?",
             "Respuesta: un método replicable (oficial + abierta + operativa + auditoría) para otros rubros.", "23 / 23")
        bullets(fig, 0.82, [
            "El método combina registro oficial (núcleo), fuentes abiertas y operativas (cobertura) y una "
            "revisión manual de los casos dudosos.",
            "Es replicable en otros rubros gastronómicos: pizzerías, heladerías artesanales, cafeterías de "
            "especialidad, panaderías, parrillas y casas de empanadas.",
            "Una línea futura puede ampliar la documentación de casas emblemáticas e históricas del rubro "
            "con fuentes verificables.",
            "La metodología puede consolidarse como insumo para futuras líneas de análisis territorial "
            "gastronómico.",
        ], gap=0.05)
        insight(fig, 0.28, "Resultado: una base analítica reproducible, no oficial, lista para validación "
                "territorial y eventual incorporación a la línea de análisis territorial gastronómico "
                "(con aprobación).", color=VERDE)
        foot(fig, "padrón candidato no oficial · método replicable en otros rubros gastronómicos.")
        pdf.savefig(fig); plt.close(fig)

        d = pdf.infodict()
        d["Title"] = "Casas de pastas en CABA — Padrón candidato depurado"
        d["Author"] = "Análisis territorial gastronómico"
        d["Subject"] = "Padrón candidato no oficial (AGC + OSM + Google Places). Sujeto a verificación territorial."

    escribir_md(rv2, com, bar, dens_com, dens_bar, combos, cobertura,
                con_a, con_o, con_g, n_conf, n_desc, georref)
    print(f"PDF generado: {PDF}")
    print(f"Páginas: 23 | tamaño: {PDF.stat().st_size/1024:.0f} KB")
    print(f"MD generado: {MD}")


def escribir_md(rv2, com, bar, dens_com, dens_bar, combos, cobertura,
                con_a, con_o, con_g, n_conf, n_desc, georref):
    n_tot = rv2["candidatos_unicos"]
    n_ind, n_cad, n_multi = rv2["independientes"], rv2["cadenas"], rv2["multifuente"]
    L = ["# DataGastro — Diagnóstico territorial gastronómico\n"]
    L.append("## Casas de pastas en la Ciudad de Buenos Aires\n")
    L.append("**Padrón candidato depurado y lectura territorial del rubro**\n")
    L.append("_Análisis y desarrollo: Diego Aleman_\n")
    L.append("Este informe integra registro oficial, fuentes abiertas, señales operativas y revisión manual "
             "para aproximar un universo operativo probable de casas de pastas en CABA. El resultado no "
             "constituye un censo definitivo ni reemplaza al registro oficial: funciona como base analítica "
             "para orientar validaciones y decisiones territoriales.\n")
    L.append("> Tras una revisión manual de los casos dudosos, el padrón candidato depurado queda conformado "
             f"por **{n_tot}** establecimientos posibles, combinando el registro administrativo oficial "
             "(AGC / F02), el relevamiento abierto auxiliar (OpenStreetMap) y una señal operativa no oficial "
             "(Google Places). No es un padrón oficial ni un censo definitivo: es una base analítica para "
             "validación territorial.\n")
    L.append("## Indicadores\n")
    L.append(f"- **{n_tot}** candidatos únicos · **{n_ind}** independientes / de barrio · "
             f"**{n_cad}** en cadenas · **{n_multi}** multifuente · **{georref}** georreferenciados.\n")
    L.append(f"_{georref} de los {n_tot} candidatos cuentan con coordenadas suficientes para su ubicación "
             f"puntual; los {int(n_tot) - int(georref)} restantes integran el conteo general pero no se "
             "grafican._\n")
    L.append("## 1. ¿Qué universo permite ver el cruce de fuentes?\n")
    L.append(f"{n_tot} candidatos únicos. No es un padrón oficial ni un censo definitivo: es una base "
             "analítica para validación territorial.\n")
    L.append("## 2. ¿Por qué el registro oficial no alcanza?\n")
    L.append("| Fuente | Naturaleza | Candidatos | Qué puede / no puede afirmar |")
    L.append("|---|---|---|---|")
    L.append(f"| AGC / F02 | Registro administrativo **oficial** | {con_a} | Habilitaciones; **no implica local activo** |")
    L.append(f"| OpenStreetMap | **Abierta auxiliar** | {con_o} | Cobertura territorial; **no oficial** |")
    L.append(f"| Google Places | **Operativa no oficial** | {con_g} | Visibilidad comercial; **no gubernamental** |")
    L.append(f"| Padrón depurado | **Padrón candidato** | {n_tot} | Unión deduplicada + revisión manual |")
    L.append("\n_Los conteos corresponden al padrón integrado ya consolidado; no representan resultados "
             "brutos de búsqueda._\n")
    L.append("## 3. ¿Dónde se concentran?\n")
    L.append("- **Comunas (cantidad):** " + ", ".join(f"{c} ({n})" for c, n in com.most_common(5)) + ".")
    L.append("- **Barrios (cantidad):** " + ", ".join(f"{b} ({n})" for b, n in bar.most_common(5)) + ".\n")
    L.append("## 4. ¿Qué cambia con la densidad por km²?\n")
    L.append("- **Densidad comuna (cand./km²):** " + ", ".join(f"{c} ({v:.2f})" for c, v in dens_com[:5]) + ".")
    L.append("- **Densidad barrio (cand./km²):** " + ", ".join(f"{b} ({v:.2f})" for b, v in dens_bar[:5]) +
             ". No es densidad por habitante; el ranking difiere del de cantidad absoluta.\n")
    L.append("## 5. ¿Qué barrios son polos?\n")
    top3b = [b for b, _ in bar.most_common(3)]
    L.append(", ".join(f"{b} ({n})" for b, n in bar.most_common(3)) +
             " encabezan el ranking. Mapas de zoom para " + ", ".join(top3b) + ".\n")
    L.append("## 6. ¿Cadenas o casas de barrio?\n")
    L.append(f"> En el universo candidato predominan las casas independientes y de escala barrial "
             f"({n_ind} de {n_tot}; {n_cad} en cadenas).\n")
    L.append("## 7. Principales cadenas (control de cobertura)\n")
    L.append(", ".join(f"{CADENA_CAPS.get(r['cadena'], r['cadena'].upper())} ({r['sucursales']})"
                       for r in cobertura[:7]) + ".\n")
    L.append("## 8. Núcleo de mayor respaldo cruzado\n")
    L.append(f"- {n_multi} candidatos multifuente (Google + OSM): base más sólida. Combinaciones: "
             f"solo OSM {combos.get('osm',0)} · solo Google {combos.get('google',0)} · Google+OSM "
             f"{combos.get('google+osm',0)} · solo AGC {combos.get('agc',0)} · recall complementario "
             f"(búsqueda adicional de cobertura) {combos.get('google_recall',0)} · documental "
             f"{combos.get('documental',0)}. Aparecer en más de una fuente "
             "aumenta la probabilidad de existencia, pero no la confirma: no reemplaza la validación.\n")
    L.append("## 9. ¿Qué aportó la revisión manual?\n")
    L.append("La revisión manual permitió depurar los casos dudosos detectados por el cruce de fuentes.\n")
    L.append(f"- Se confirmaron {n_conf} candidatos y se excluyeron {n_desc} casos (restaurantes, locales "
             "cerrados, registros genéricos o rubros no incluidos).\n"
             "- Los confirmados se incorporan como candidatos validados en revisión manual.\n"
             f"- Una búsqueda complementaria de cobertura permitió detectar "
             f"{rv2.get('incorporados_recall_google','0')} candidatos adicionales, incorporados solo tras "
             "revisión y trazabilidad.\n"
             "- El detalle por caso queda en el anexo metodológico interno.\n")
    L.append("## 10. ¿Qué aporta esta metodología?\n")
    L.append("Un método replicable (registro oficial + fuentes abiertas + señal operativa + revisión manual) "
             "para otros rubros: pizzerías, heladerías artesanales, cafeterías de especialidad, panaderías, "
             "parrillas, casas de empanadas.\n")
    L.append("## Casos con respaldo documental\n")
    L.append("Además del análisis territorial, se identificaron establecimientos con fuentes sobre "
             "trayectoria, origen familiar o antigüedad. No es un ranking histórico exhaustivo, sino "
             "ejemplos verificables dentro del rubro.\n")
    L.append("- **Pastas Amelia** — Boedo · 1948 — fábrica artesanal vinculada a la familia Palazzo "
             "(fusilis al fierrito).")
    L.append("- **La Hispano Americana** — San Telmo · más de medio siglo — casa de pastas asociada a "
             "inmigrantes gallegos y continuidad familiar.")
    L.append("- **La Juvenil** — Colegiales · 1959 — marca familiar con varias generaciones y expansión "
             "territorial.")
    L.append("- **Pastas Bayo** — Belgrano · 1978 — casa de pastas familiar con permanencia en la misma "
             "dirección.\n")
    L.append("_Se incluyen por contar con fuentes documentales identificables (prensa nacional y sitios "
             "oficiales); no agotan la historia del rubro ni prueban por sí solos cuál es la casa de pastas "
             "más antigua de la Ciudad. Detalle de fuentes en anexo metodológico interno._\n")
    L.append("## ¿Para qué sirve este diagnóstico?\n")
    L.append("Dimensionar el universo operativo probable por comuna y barrio; identificar polos territoriales; "
             "distinguir cadenas de casas independientes; señalar el núcleo de mayor respaldo cruzado como "
             "base más sólida. Es una base analítica candidata, no oficial: orienta el trabajo territorial y "
             "no reemplaza al registro oficial.\n")
    L.append("## Limitaciones\n")
    L.append("- Sigue siendo padrón candidato; no reemplaza al registro oficial; no implica local activo "
             "confirmado por fuente oficial. Google/OSM no son fuentes oficiales. Puede haber locales "
             "cerrados o faltantes. La densidad se expresa por superficie; una etapa posterior puede "
             "incorporar población para estimar cobertura relativa por habitante. La revisión manual de "
             "escritorio mejora la depuración, pero no reemplaza la verificación territorial final si el "
             "informe se usa públicamente.\n")
    MD.write_text("\n".join(L), encoding="utf-8")


if __name__ == "__main__":
    main()
