"""Informe ejecutivo DGDGAS — Casas de Pastas de la Ciudad de Buenos Aires.

Versión EJECUTIVA condensada. Copia adaptada de build_pdf_integrado_v4.py. NO recalcula
datos ni cambia el padrón, clasificación, mapas, rankings, fuentes ni recall: lee
exactamente los mismos archivos depurados. Usa SOLO agregados y mapas anonimizados (sin
nombres, direcciones, razón social, place_id, teléfonos, emails, ratings ni API key).
No hace requests. No commitea.

Marca institucional DGDGAS — Dirección General de Gastronomía (Gobierno de la Ciudad de
Buenos Aires). NO usa "DataGastro" como marca pública. Título: "Casas de Pastas de la
Ciudad de Buenos Aires — Informe". No incluye etiquetas de "prueba", "borrador",
"revisión institucional" ni "documento interno".

Estructura ejecutiva (14 páginas):
  1  Portada
  2  Índice
  3  Resumen ejecutivo (KPIs: 254 candidatos, 173 independientes, 81 cadenas)
  4  Sección 1 — Fuentes utilizadas y alcance del padrón (bullets breves)
  5  Sección 2 — Distribución territorial de los candidatos (mapa de puntos)
  6  Sección 3 — Distribución territorial por cantidad (comuna + barrio, 2 mapas)
  7  Sección 4 — Distribución territorial por densidad (comuna + barrio, 2 mapas)
  8  Sección 5 — Zoom territorial: Palermo
  9  Sección 5 — Zoom territorial: Caballito
  10 Sección 5 — Zoom territorial: Belgrano
  11 Sección 6 — Cadenas y casas independientes (proporción + ranking, 1 página)
  12 Anexo A — Casos con respaldo documental
  13 Anexo B — Fuentes documentales
  14 Anexo C — Limitaciones (con nota metodológica breve)

Salida (nueva, NO sobrescribe la V4):
  outputs/casas_de_pastas/INFORME_CASAS_DE_PASTAS_DGDGAS.pdf
"""
from __future__ import annotations

import csv
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

ROOT = Path(__file__).resolve().parents[2]
INT = ROOT / "outputs" / "casas_pastas_integrado"
GEO = ROOT / "data" / "raw"
OUT = ROOT / "outputs" / "casas_de_pastas"
PDF = OUT / "INFORME_CASAS_DE_PASTAS_DGDGAS.pdf"

INSTITUCION = "DGDGAS — Dirección General de Gastronomía"
GOBIERNO = "Gobierno de la Ciudad de Buenos Aires"
TITULO = "Casas de Pastas de la Ciudad de Buenos Aires — Informe"

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
    "A_integrado_multifuente": "Detectado por 2 o más fuentes",
    "A_validado_manual": "Validado en revisión",
    "A_documental_validado_manual": "Documental (histórico)",
    "A_google_recall_validado_manual": "Cobertura complementaria",
    "A_agc_oficial_estricto": "Registro oficial (AGC)",
    "A_google_probable": "Fuente operativa",
    "A_osm_auxiliar": "Fuente abierta (OSM)",
    "B_revision_manual": "En revisión",
}
CADENA_CAPS = {
    "la juvenil": "LA JUVENIL", "multipasta": "MULTIPASTA", "caprizzi": "CAPRIZZI",
    "master pastas / pastas master": "MASTER PASTAS / PASTAS MASTER",
    "milena pastas artesanales": "MILENA PASTAS ARTESANALES",
    "pastas mazzeo": "PASTAS MAZZEO", "raviolon": "RAVIOLON", "biasatti": "BIASATTI",
    "pastas bayo": "PASTAS BAYO",
}

TOTAL_PAG = 14


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


def numpag(n):
    return f"{n} / {TOTAL_PAG}"


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


def foot(fig, nota=None):
    """Pie institucional DGDGAS. La versión ejecutiva no repite advertencias metodológicas;
    solo deja la firma institucional. `nota` opcional para una aclaración puntual y breve."""
    footer_y = 0.031
    rule_y = 0.050
    note_last_line_y = 0.064
    note_line_gap = 0.0145
    fig.lines.append(Line2D([0.07, 0.93], [rule_y, rule_y], color="#dddddd", lw=0.8, transform=fig.transFigure))
    if nota:
        note_lines = textwrap.wrap(nota, 118)
        note_y = note_last_line_y + (len(note_lines) - 1) * note_line_gap
        for j, ln in enumerate(note_lines):
            fig.text(0.07, note_y - j * note_line_gap, ln, color=GRIS, fontsize=7.4,
                     va="top", style="italic")
    fig.text(0.07, footer_y, f"{INSTITUCION} · {GOBIERNO}", color=AZUL, fontsize=7.6,
             va="top", fontweight="bold")


def barh(fig, rect, labels, values, color, title, xlabel, valfmt="{:.0f}", titlesize=11):
    ax = fig.add_axes(rect)
    bars = ax.barh(labels, values, color=color)
    ax.set_title(title, color=AZUL, fontsize=titlesize, loc="left", pad=6)
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
    try:
        p = shape(geom).representative_point()
        return p.x, p.y
    except Exception:  # noqa: BLE001
        xs, ys = [], []
        for x, y in poligonos(geom):
            xs += x; ys += y
        return (sum(xs) / len(xs), sum(ys) / len(ys)) if xs else (0, 0)


def _texto_contraste(rgba):
    r, g, b = rgba[0], rgba[1], rgba[2]
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    if lum < 0.55:
        return "white", "#1a1a1a"
    return "#1a1a1a", "white"


def choropleth(fig, rect, features, key_prop, val_by_key, cmap_name, title, label_keys=None,
               etiqueta_num=False, titlesize=11, labelsize=None):
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
            size = labelsize if labelsize else (7 if etiqueta_num else 6.5)
            ax.text(cx, cy, key, ha="center", va="center", fontsize=size, color=txtcolor,
                    fontweight="bold", zorder=5,
                    path_effects=[pe.withStroke(linewidth=1.8, foreground=halo)])
    ax.set_aspect(1.28); ax.axis("off")
    ax.set_title(title, color=AZUL, fontsize=titlesize, loc="left", pad=4)
    sm = cm.ScalarMappable(norm=norm, cmap=cmap); sm.set_array([])
    cb = fig.colorbar(sm, ax=ax, fraction=0.035, pad=0.01, shrink=0.55)
    cb.ax.tick_params(labelsize=6.5)
    return ax


def main():
    OUT.mkdir(parents=True, exist_ok=True)

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
        # 1. Portada institucional DGDGAS.
        fig = page()
        fig.patches.append(Rectangle((0, 0.70), 1, 0.30, transform=fig.transFigure, facecolor=AZUL, zorder=0))
        fig.patches.append(Rectangle((0, 0.694), 1, 0.006, transform=fig.transFigure, facecolor=ROJO, zorder=1))
        fig.text(0.07, 0.945, "DGDGAS", color="white", fontsize=22, fontweight="bold")
        fig.lines.append(Line2D([0.07, 0.205], [0.927, 0.927], color=ROJO, lw=2.2, transform=fig.transFigure))
        fig.text(0.07, 0.905, "Dirección General de Gastronomía", color="white",
                 fontsize=12.5, fontweight="bold")
        fig.text(0.07, 0.878, GOBIERNO.upper(), color="#cdd9e5", fontsize=9.5, fontweight="bold")
        fig.text(0.07, 0.788, "Casas de Pastas de la\nCiudad de Buenos Aires", color="white",
                 fontsize=25, fontweight="bold", va="center")
        fig.text(0.07, 0.723, "Informe", color="#cdd9e5", fontsize=15, fontweight="bold", va="center")
        fig.text(0.07, 0.628, "Padrón candidato depurado y lectura territorial del rubro",
                 fontsize=14, color=AZUL, fontweight="bold")
        fig.lines.append(Line2D([0.07, 0.60], [0.598, 0.598], color=ROJO, lw=2.5, transform=fig.transFigure))
        bajada = ("Este informe dimensiona el universo probable de casas de pastas en la Ciudad de Buenos "
                  "Aires y describe su distribución territorial. Es una base analítica para orientar "
                  "validaciones y decisiones; no constituye un censo ni reemplaza al registro oficial.")
        yb = 0.545
        for ln in textwrap.wrap(bajada, 90):
            fig.text(0.07, yb, ln, fontsize=11.5, color="#333333", va="top")
            yb -= 0.028
        fig.lines.append(Line2D([0.07, 0.93], [0.135, 0.135], color="#dddddd", lw=0.8, transform=fig.transFigure))
        fig.text(0.07, 0.115, INSTITUCION, fontsize=10.5, color=AZUL, fontweight="bold", va="top")
        fig.text(0.07, 0.088, GOBIERNO, fontsize=9.5, color=GRIS, va="top")
        fig.text(0.07, 0.062, "Padrón candidato no oficial · sujeto a verificación territorial.",
                 fontsize=8.5, color=GRIS, style="italic", va="top")
        pdf.savefig(fig); plt.close(fig)

        # 2. Índice.
        fig = page()
        head(fig, "CONTENIDO", "Índice", "", numpag(2))
        indice = [
            ("Resumen ejecutivo", "3"),
            ("1.  Fuentes utilizadas y alcance del padrón", "4"),
            ("2.  Distribución territorial de los candidatos", "5"),
            ("3.  Distribución territorial por cantidad", "6"),
            ("4.  Distribución territorial por densidad", "7"),
            ("5.  Zoom territorial por barrio", "8–10"),
            ("6.  Cadenas y casas independientes", "11"),
            ("Anexos", ""),
            ("A.  Casos con respaldo documental", "12"),
            ("B.  Fuentes documentales", "13"),
            ("C.  Limitaciones", "14"),
        ]
        y = 0.85
        for txt, pg in indice:
            es_titulo = pg == "" or txt.startswith("Resumen") or txt.startswith("Anexos")
            color = AZUL if es_titulo else "#222222"
            fw = "bold" if es_titulo else "normal"
            fig.text(0.09, y, txt, fontsize=11.5 if es_titulo else 11, color=color, va="top", fontweight=fw)
            if pg:
                fig.text(0.91, y, pg, fontsize=11, color=GRIS, va="top", ha="right")
                fig.lines.append(Line2D([0.09, 0.90], [y - 0.006, y - 0.006], color="#e8e8e8",
                                        lw=0.6, transform=fig.transFigure, zorder=0))
            y -= 0.042
        foot(fig)
        pdf.savefig(fig); plt.close(fig)

        # 3. Resumen ejecutivo.
        fig = page()
        head(fig, "RESUMEN EJECUTIVO", "Qué muestra el informe",
             "Un universo candidato depurado, con fuerte presencia de casas de barrio y polos territoriales claros.",
             numpag(3))
        cards(fig, 0.72, [(n_tot, "candidatos únicos", AZUL), (n_ind, "independientes / de barrio", VERDE),
                          (n_cad, "en cadenas", NARANJA)], h=0.11)
        top_com = ", ".join(f"Comuna {c} ({n})" for c, n in com.most_common(3))
        top_bar = ", ".join(f"{b} ({n})" for b, n in bar.most_common(3))
        bullets(fig, 0.63, [
            f"El padrón candidato depurado reúne {n_tot} establecimientos posibles de casas de pastas en la "
            "Ciudad de Buenos Aires.",
            f"Predominan las casas independientes y de escala barrial ({n_ind} de {n_tot}); {n_cad} pertenecen "
            "a cadenas.",
            f"La oferta se concentra en {top_com} por cantidad; y en barrios como {top_bar}.",
            "La lectura por densidad reordena el mapa: barrios más compactos muestran alta concentración "
            "por superficie aunque no lideren en cantidad.",
            "El informe sirve para orientar validaciones territoriales y priorizar dónde verificar.",
        ], gap=0.048)
        insight(fig, 0.235, "Es una base analítica candidata, no oficial: orienta el trabajo territorial y no "
                "reemplaza al registro oficial. \"Candidato\" es un establecimiento detectado como posible "
                "casa de pastas, sin validación definitiva de actividad.", color=AZUL, h=0.095)
        foot(fig, f"Nota: {n_multi} candidatos aparecen en más de una fuente (mayor respaldo cruzado).")
        pdf.savefig(fig); plt.close(fig)

        # 4. Sección 1 — Fuentes utilizadas y alcance (breve, sin gráficos ni tabla larga).
        fig = page()
        head(fig, "SECCIÓN 1", "Fuentes utilizadas y alcance del padrón",
             "Cómo se construyó el universo candidato, en pocas líneas.", numpag(4))
        bullets(fig, 0.82, [
            "Se parte del registro administrativo oficial (AGC / F02), que aporta el núcleo estricto pero "
            "acotado del rubro.",
            "Se complementa con fuentes abiertas (OpenStreetMap) y una señal operativa (Google Places) para "
            "ampliar la cobertura territorial.",
            "Se deduplican los registros que refieren al mismo establecimiento y se revisan manualmente los "
            "casos dudosos.",
            f"El resultado es un padrón candidato depurado de {n_tot} establecimientos posibles.",
            "No reemplaza al registro oficial ni confirma que cada candidato sea un local activo: es una base "
            "para validación territorial.",
        ], gap=0.055)
        insight(fig, 0.36, "El registro oficial mide habilitaciones, no locales activos. Las fuentes abiertas "
                "y operativas amplían cobertura, pero no son oficiales. Aparecer en más de una fuente aumenta "
                "la confianza; aparecer en una sola conserva al establecimiento como candidato.", color=AZUL2,
                h=0.12)
        foot(fig)
        pdf.savefig(fig); plt.close(fig)

        # 5. Sección 2 — Mapa general de puntos.
        fig = page()
        head(fig, "SECCIÓN 2", "Distribución territorial de los candidatos",
             "Se concentran en el corredor norte–centro de la Ciudad, con polos en Palermo, Caballito y Recoleta/Belgrano.",
             numpag(5))
        ax = fig.add_axes([0.06, 0.14, 0.88, 0.70])
        for f in gc["features"]:
            for xs, ys in poligonos(f["geometry"]):
                ax.plot(xs, ys, color="#cfcfcf", lw=0.6, zorder=1)
        for p in pts:
            ax.scatter(p["lon"], p["lat"], s=14, color=CLASE_COLOR.get(p["clase"], "#999"),
                       edgecolor="white", lw=0.25, zorder=3)
        ax.set_aspect(1.28); ax.axis("off")
        leyenda(ax)
        n_sin = int(n_tot) - int(georref)
        foot(fig, f"{georref} de los {n_tot} candidatos tienen coordenadas suficientes para ubicarse; los "
                  f"{n_sin} restantes integran el conteo pero no se grafican. Puntos anonimizados (sin nombres "
                  "ni direcciones); contornos: comunas GCBA.")
        pdf.savefig(fig); plt.close(fig)

        # 6. Sección 3 — Distribución por cantidad (comuna + barrio en una hoja).
        fig = page()
        head(fig, "SECCIÓN 3", "Distribución territorial por cantidad",
             "Cantidad de candidatos por comuna y por barrio.", numpag(6))
        choropleth(fig, [0.05, 0.44, 0.44, 0.36], gc["features"], "comuna", dict(com), "YlOrRd",
                   "Por comuna (cantidad)", etiqueta_num=True, titlesize=10, labelsize=6)
        choropleth(fig, [0.52, 0.44, 0.44, 0.36], gb["features"], "barrio", dict(bar), "YlOrRd",
                   "Por barrio (cantidad)", label_keys=top_barrios, titlesize=10, labelsize=5.5)
        top_com = ", ".join(f"{c} ({n})" for c, n in com.most_common(5))
        top_bar = ", ".join(f"{b} ({n})" for b, n in bar.most_common(5))
        bullets(fig, 0.33, [
            f"Comunas con más candidatos: {top_com}.",
            f"Barrios con más candidatos: {top_bar}.",
            "La concentración por cantidad marca dónde hay más establecimientos para validar por volumen.",
        ], gap=0.05)
        foot(fig, "Cantidad absoluta; comparar con la densidad por km² (sección 4).")
        pdf.savefig(fig); plt.close(fig)

        # 7. Sección 4 — Distribución por densidad (comuna + barrio en una hoja).
        fig = page()
        head(fig, "SECCIÓN 4", "Distribución territorial por densidad",
             "Candidatos por km² de superficie oficial, por comuna y por barrio.", numpag(7))
        choropleth(fig, [0.05, 0.44, 0.44, 0.36], gc["features"], "comuna", dcom, "PuBuGn",
                   "Por comuna (cand./km²)", etiqueta_num=True, titlesize=10, labelsize=6)
        choropleth(fig, [0.52, 0.44, 0.44, 0.36], gb["features"], "barrio", dbar, "PuBuGn",
                   "Por barrio (cand./km²)", label_keys=set(b for b, _ in dens_bar[:5]),
                   titlesize=10, labelsize=5.5)
        dcom_txt = ", ".join(f"{c} ({v:.2f})" for c, v in dens_com[:5])
        dbar_txt = ", ".join(f"{b} ({v:.2f})" for b, v in dens_bar[:5])
        bullets(fig, 0.33, [
            f"Comunas más densas (cand./km²): {dcom_txt}.",
            f"Barrios más densos (cand./km²): {dbar_txt}.",
            "El ranking por densidad difiere del de cantidad: barrios chicos y compactos escalan posiciones. "
            "La densidad se mide por superficie, no por habitante.",
        ], gap=0.05)
        foot(fig, "Densidad por superficie oficial (GCBA); una etapa posterior puede incorporar población.")
        pdf.savefig(fig); plt.close(fig)

        # 8-10. Sección 5 — Zooms de los tres barrios con más candidatos.
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
            num = numpag(8 + k)
            coment = coment_barrio.get(barrio, f"{barrio} es uno de los barrios con más candidatos del padrón.")
            fig = page()
            head(fig, "SECCIÓN 5 · ZOOM TERRITORIAL", f"Zoom: {barrio}",
                 f"{bar.get(barrio, 0)} candidatos en {barrio} (anonimizados).", num)
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
            bpts = {p["clase"] for p in pts if p["barrio"] == barrio}
            leg = [Line2D([0], [0], marker="o", color="w", markerfacecolor=c, markersize=8, label=CLASE_LABEL[k])
                   for k, c in CLASE_COLOR.items() if k in bpts]
            ax.legend(handles=leg, loc="upper center", bbox_to_anchor=(0.5, -0.03), ncol=3,
                      fontsize=7.5, frameon=False)
            for j, ln in enumerate(textwrap.wrap(coment, 96)):
                fig.text(0.07, 0.175 - j * 0.020, ln, fontsize=10.5, color="#222222", style="italic", va="top")
            foot(fig)
            pdf.savefig(fig); plt.close(fig)

        # 11. Sección 6 — Cadenas y casas independientes (proporción + ranking en una hoja).
        fig = page()
        head(fig, "SECCIÓN 6", "Cadenas y casas independientes",
             "Predominan las casas independientes y de escala barrial.", numpag(11))
        cards(fig, 0.75, [(n_ind, "independientes / de barrio", VERDE), (n_cad, "en cadenas", NARANJA)], h=0.10)
        # Barra de proporción.
        ax = fig.add_axes([0.10, 0.66, 0.80, 0.045])
        tot = n_ind + n_cad
        ax.barh([0], [n_ind], color=VERDE)
        ax.barh([0], [n_cad], left=[n_ind], color=NARANJA)
        ax.text(n_ind / 2, 0, f"Independientes {round(100*n_ind/tot)}%", ha="center", va="center",
                color="white", fontsize=9.5, fontweight="bold")
        ax.text(n_ind + n_cad / 2, 0, f"Cadenas {round(100*n_cad/tot)}%", ha="center", va="center",
                color="white", fontsize=8.5, fontweight="bold")
        ax.axis("off")
        # Ranking compacto de cadenas.
        top_cad = [(CADENA_CAPS.get(r["cadena"], r["cadena"].upper()), int(r["sucursales"])) for r in cobertura][:7][::-1]
        barh(fig, [0.34, 0.20, 0.56, 0.38], [c for c, _ in top_cad], [n for _, n in top_cad],
             NARANJA, "Principales cadenas (sucursales detectadas)", "sucursales", titlesize=10.5)
        foot(fig, "Las cadenas se reportan como control de cobertura; no se cuentan categorías genéricas como cadenas.")
        pdf.savefig(fig); plt.close(fig)

        # 12. Anexo A — Casos con respaldo documental.
        fig = page()
        head(fig, "ANEXO A", "Casos con respaldo documental",
             "Establecimientos con fuentes sobre trayectoria, origen familiar o antigüedad.", numpag(12))
        fig.text(0.07, 0.835, "No es un ranking histórico exhaustivo, sino ejemplos verificables dentro del "
                 "rubro.", fontsize=10.5, color="#333333", va="top")
        docs_casos = [
            ("Pastas Amelia — Boedo · 1948",
             "Caso documentado por prensa nacional, vinculado a la familia Palazzo y a una tradición "
             "artesanal de pastas frescas, especialmente fusilis al fierrito."),
            ("La Hispano Americana — San Telmo · más de medio siglo",
             "Casa de pastas asociada a inmigrantes gallegos y continuidad familiar en un barrio histórico "
             "de la Ciudad."),
            ("La Juvenil — Colegiales · 1959",
             "Marca familiar con varias generaciones vinculadas a la elaboración de pastas frescas y "
             "posterior expansión territorial."),
            ("Pastas Bayo — Belgrano · 1978",
             "Casa de pastas familiar con permanencia en la misma dirección desde su apertura."),
        ]
        yb = 0.79
        for titulo_c, desc_c in docs_casos:
            fig.text(0.07, yb, titulo_c, fontsize=11, fontweight="bold", color=AZUL, va="top")
            lines = textwrap.wrap(desc_c, 98)
            for j, ln in enumerate(lines):
                fig.text(0.07, yb - 0.026 - j * 0.0185, ln, fontsize=9.5, color="#333333", va="top")
            yb -= 0.040 + len(lines) * 0.0185 + 0.020
        cierre_doc = ("Se incluyen por contar con fuentes documentales identificables; no agotan la historia "
                      "del rubro ni prueban por sí solos cuál es la casa de pastas más antigua de la Ciudad.")
        for j, ln in enumerate(textwrap.wrap(cierre_doc, 100)):
            fig.text(0.07, 0.24 - j * 0.020, ln, fontsize=9, color=GRIS, style="italic", va="top")
        foot(fig)
        pdf.savefig(fig); plt.close(fig)

        # 13. Anexo B — Fuentes documentales.
        fig = page()
        head(fig, "ANEXO B", "Fuentes documentales",
             "Prensa nacional y sitios oficiales de los establecimientos. No se citan reseñas.", numpag(13))
        fuentes_doc = [
            ("Pastas Amelia",
             "La Nación — nota sobre la fábrica de pastas de Boedo en funcionamiento desde 1948.",
             "lanacion.com.ar"),
            ("La Hispano Americana",
             "Sitio oficial — información institucional sobre su trayectoria en San Telmo e historia familiar.",
             "lahispanoamericana.com.ar"),
            ("La Juvenil",
             "Sitio oficial, sección \"La empresa\"; y La Nación, nota sobre el crecimiento familiar.",
             "lajuvenilpastas.com.ar · lanacion.com.ar"),
            ("Pastas Bayo",
             "Sitio oficial, sección institucional — historia de la marca desde 1978.",
             "pastasbayo.com.ar"),
        ]
        yb = 0.82
        for nombre_f, ref, url in fuentes_doc:
            fig.text(0.07, yb, nombre_f, fontsize=11, fontweight="bold", color=AZUL, va="top")
            lines = textwrap.wrap(ref, 98)
            for j, ln in enumerate(lines):
                fig.text(0.07, yb - 0.026 - j * 0.0185, ln, fontsize=9.5, color="#333333", va="top")
            fig.text(0.07, yb - 0.026 - len(lines) * 0.0185, url, fontsize=8, color=AZUL2, va="top")
            yb -= 0.058 + len(lines) * 0.0185 + 0.026
        nota_f = ("Las fuentes corresponden a los medios y sitios oficiales originales. Las búsquedas web "
                  "asistidas se usaron solo como herramienta de localización, no como fuente.")
        for j, ln in enumerate(textwrap.wrap(nota_f, 100)):
            fig.text(0.07, 0.26 - j * 0.020, ln, fontsize=8.5, color=GRIS, style="italic", va="top")
        foot(fig)
        pdf.savefig(fig); plt.close(fig)

        # 14. Anexo C — Limitaciones (con nota metodológica breve).
        fig = page()
        head(fig, "ANEXO C", "Limitaciones", "Qué no afirma este informe.", numpag(14))
        bullets(fig, 0.82, [
            "Es un padrón candidato; no reemplaza al registro oficial ni implica local activo confirmado.",
            "Google Places y OpenStreetMap no son fuentes oficiales; reflejan visibilidad comercial y "
            "relevamiento colaborativo.",
            "Puede haber locales cerrados (que figuran) o faltantes (que no figuran en ninguna fuente).",
            "La densidad se expresa por superficie; una etapa posterior puede incorporar población para "
            "estimar cobertura por habitante.",
            "La revisión de escritorio mejora la depuración, pero no reemplaza la verificación territorial "
            "final si el informe se usa públicamente.",
        ], gap=0.05)
        insight(fig, 0.34, "Nota metodológica: el universo combina registro oficial (núcleo), fuentes abiertas "
                "y operativas (cobertura) y revisión manual de casos dudosos. El método es replicable en otros "
                "rubros gastronómicos.", color=AZUL, h=0.10)
        foot(fig, "Padrón candidato no oficial · la verificación territorial final queda pendiente.")
        pdf.savefig(fig); plt.close(fig)

        d = pdf.infodict()
        d["Title"] = "Casas de Pastas de la Ciudad de Buenos Aires — Informe"
        d["Author"] = "DGDGAS — Dirección General de Gastronomía"
        d["Subject"] = "Padrón candidato no oficial (AGC + OSM + Google Places). Sujeto a verificación territorial."

    print(f"PDF generado: {PDF}")
    print(f"Páginas: {TOTAL_PAG} | tamaño: {PDF.stat().st_size/1024:.0f} KB")


if __name__ == "__main__":
    main()
