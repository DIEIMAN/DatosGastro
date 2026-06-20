"""Arma el PDF ejecutivo del informe INTEGRADO de casas de pastas en CABA (padrón v2).

Usa SOLO agregados y un mapa anonimizado. No imprime nombres, direcciones, razón social,
place_id, teléfonos, emails, ratings, reviews, horarios ni API key.

Fuentes:
  outputs/casas_pastas_integrado/padron_candidato_integrado_v2.csv  (solo para AGREGAR; no se imprimen filas)
  outputs/casas_pastas_integrado/resumen_integrado_v2.csv
  outputs/casas_pastas_integrado/auditoria_calidad/resumen_auditoria_calidad.csv
  outputs/casas_pastas_reporte/integrado_sanitizado/cobertura_cadenas_e_independientes.csv
  outputs/casas_pastas_reporte/integrado_sanitizado/mapa_puntos_sanitizado.geojson
  data/raw/geo_comunas.geojson  (contornos + área)
  data/raw/geo_barrios.geojson  (área)

Salidas:
  outputs/casas_pastas_reporte/INFORME_CASAS_PASTAS_INTEGRADO.pdf
  outputs/casas_pastas_reporte/INFORME_CASAS_PASTAS_INTEGRADO.md
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

ROOT = Path(__file__).resolve().parents[2]
INT = ROOT / "outputs" / "casas_pastas_integrado"
REP = ROOT / "outputs" / "casas_pastas_reporte"
SAN = REP / "integrado_sanitizado"
GEO = ROOT / "data" / "raw"
PDF = REP / "INFORME_CASAS_PASTAS_INTEGRADO.pdf"
MD = REP / "INFORME_CASAS_PASTAS_INTEGRADO.md"

A4 = (8.27, 11.69)
AZUL = "#1f3b57"
ROJO = "#c0392b"
GRIS = "#555555"

# Colores por clase integrada (para mapa y leyenda).
CLASE_COLOR = {
    "A_integrado_multifuente": "#1a9850",
    "A_agc_oficial_estricto": "#2c7fb8",
    "A_google_probable": "#f08c00",
    "A_osm_auxiliar": "#7b5ea7",
    "B_revision_manual": "#999999",
}
CLASE_LABEL = {
    "A_integrado_multifuente": "Multifuente (≥2)",
    "A_agc_oficial_estricto": "AGC oficial estricto",
    "A_google_probable": "Google (operativo)",
    "A_osm_auxiliar": "OSM (auxiliar)",
    "B_revision_manual": "Revisión manual",
}


def read_csv(p):
    with p.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def kv(rows):
    return {r["indicador"]: r["valor"] for r in rows}


def new_page(pdf):
    fig = plt.figure(figsize=A4)
    fig.subplots_adjust(left=0.09, right=0.93, top=0.92, bottom=0.07)
    return fig


def header(fig, titulo, num=""):
    fig.text(0.09, 0.95, "Casas de pastas en CABA — Padrón candidato integrado", color=GRIS, fontsize=9)
    fig.text(0.09, 0.925, titulo, color=AZUL, fontsize=18, fontweight="bold")
    fig.text(0.93, 0.95, num, color=GRIS, fontsize=9, ha="right")
    fig.lines.append(Line2D([0.09, 0.93], [0.915, 0.915], color=AZUL, lw=1.2, transform=fig.transFigure))


def bullets(fig, y0, items, size=11, gap=0.04, wrap=82, color="#222222"):
    y = y0
    for it in items:
        marker = "•" if not it.startswith("  ") else "–"
        lines = textwrap.wrap(it.strip(), wrap) or [""]
        fig.text(0.11, y, marker, fontsize=size, color=ROJO, va="top")
        for j, ln in enumerate(lines):
            fig.text(0.135, y - j * 0.024, ln, fontsize=size, color=color, va="top")
        y -= gap + (len(lines) - 1) * 0.024
    return y


def table(fig, rect, data, headers, col_w, fontsize=10, title=None):
    ax = fig.add_axes(rect)
    ax.axis("off")
    if title:
        ax.set_title(title, color=AZUL, fontsize=12, loc="left", pad=8)
    t = ax.table(cellText=data, colLabels=headers, colWidths=col_w, loc="upper center", cellLoc="center")
    t.auto_set_font_size(False)
    t.set_fontsize(fontsize)
    t.scale(1, 1.5)
    for (r, _c), cell in t.get_celld().items():
        cell.set_edgecolor("#dddddd")
        if r == 0:
            cell.set_facecolor(AZUL)
            cell.set_text_props(color="white", fontweight="bold")
        elif r % 2 == 0:
            cell.set_facecolor("#f2f5f8")
    return ax


def barh(fig, rect, labels, values, color, title, xlabel):
    ax = fig.add_axes(rect)
    ax.barh(labels, values, color=color)
    ax.set_title(title, color=AZUL, fontsize=11, loc="left")
    ax.set_xlabel(xlabel, fontsize=9)
    ax.tick_params(labelsize=9)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    return ax


def poligonos(geom):
    """Devuelve lista de anillos exteriores [(xs,ys)] desde Polygon/MultiPolygon."""
    out = []
    if geom["type"] == "Polygon":
        rings = [geom["coordinates"][0]]
    elif geom["type"] == "MultiPolygon":
        rings = [poly[0] for poly in geom["coordinates"]]
    else:
        return out
    for ring in rings:
        xs = [c[0] for c in ring]
        ys = [c[1] for c in ring]
        out.append((xs, ys))
    return out


def main():
    hoy = dt.date.today().isoformat()
    rv2 = kv(read_csv(INT / "resumen_integrado_v2.csv"))
    rqc = kv(read_csv(INT / "auditoria_calidad" / "resumen_auditoria_calidad.csv"))
    cobertura = read_csv(SAN / "cobertura_cadenas_e_independientes.csv")

    # Agregados desde v2 (solo conteos; no se imprimen filas individuales).
    pad = read_csv(INT / "padron_candidato_integrado_v2.csv")
    gc = json.load((GEO / "geo_comunas.geojson").open(encoding="utf-8"))
    gb = json.load((GEO / "geo_barrios.geojson").open(encoding="utf-8"))
    acom = {str(f["properties"]["comuna"]): f["properties"]["area"] / 1e6 for f in gc["features"]}
    abar = {f["properties"]["nombre"].title(): f["properties"]["area_metro"] / 1e6 for f in gb["features"]}
    com = Counter(r["comuna"] for r in pad if r["comuna"])
    bar = Counter(r["barrio"] for r in pad if r["barrio"])
    dens_com = sorted(((c, n, n / acom[c]) for c, n in com.items() if c in acom), key=lambda x: -x[2])
    dens_bar = sorted(((b, n, n / abar[b]) for b, n in bar.items() if b in abar), key=lambda x: -x[2])

    geo_pts = json.load((SAN / "mapa_puntos_sanitizado.geojson").open(encoding="utf-8"))["features"]

    n_tot = rv2["candidatos_unicos"]
    n_ind = int(rv2["independientes"]); n_cad = int(rv2["cadenas"])
    n_rev = rv2["revision_manual_prioritaria"]
    n_multi = rv2["multifuente"]

    with PdfPages(PDF) as pdf:
        # 1. Portada
        fig = new_page(pdf)
        fig.text(0.09, 0.72, "Casas de pastas\nen la Ciudad de Buenos Aires",
                 fontsize=27, fontweight="bold", color=AZUL, va="top")
        fig.text(0.09, 0.58, "Registro oficial, fuentes abiertas y padrón candidato integrado",
                 fontsize=14, color=GRIS)
        fig.lines.append(Line2D([0.09, 0.62], [0.545, 0.545], color=ROJO, lw=2, transform=fig.transFigure))
        fig.text(0.09, 0.47,
                 "Padrón candidato integrado v2 que combina el registro administrativo oficial (AGC/F02),\n"
                 "el relevamiento abierto auxiliar (OpenStreetMap) y una señal operativa no oficial\n"
                 "(Google Places API). No reemplaza al registro oficial ni constituye un censo definitivo.",
                 fontsize=11, color="#333333", va="top")
        fig.text(0.09, 0.13, f"Fecha: {hoy}   ·   Versión: v2 (padrón cerrado, pendiente de validación manual)",
                 fontsize=10, color=GRIS)
        fig.text(0.09, 0.105, "Documento ejecutivo · agregados y mapa anonimizado · sin datos personales",
                 fontsize=9, color=GRIS)
        pdf.savefig(fig); plt.close(fig)

        # 2. Resumen ejecutivo
        fig = new_page(pdf)
        header(fig, "Resumen ejecutivo", "2 / 12")
        bullets(fig, 0.86, [
            f"Se construyó un padrón candidato integrado de {n_tot} posibles casas de pastas en CABA, "
            "combinando registro oficial, fuentes abiertas y señales operativas no oficiales.",
            "El resultado no reemplaza al registro oficial ni constituye un censo definitivo: sirve como "
            "base analítica para validación territorial.",
            f"Universo amplio, no solo cadenas: {n_ind} locales independientes / de barrio y {n_cad} "
            "establecimientos pertenecientes a cadenas reconocidas.",
            f"{n_multi} candidatos aparecen en más de una fuente (mayor confianza); el registro oficial "
            "estricto (AGC) aporta 11 habilitaciones, que no implican local activo.",
            f"{n_rev} casos quedan pendientes de validación manual; ninguno se descarta de antemano.",
            "Diferencia clave entre el dato oficial (angosto) y el universo operativo probable (más amplio): "
            "no es un error, son fuentes y definiciones distintas.",
        ])
        # mini tarjetas de números
        ax = fig.add_axes([0.09, 0.30, 0.84, 0.16]); ax.axis("off")
        tarjetas = [(n_tot, "candidatos\núnicos"), (n_ind, "independientes"),
                    (n_cad, "en cadenas"), (n_rev, "revisión\nmanual")]
        for i, (v, lab) in enumerate(tarjetas):
            x = 0.02 + i * 0.25
            ax.add_patch(plt.Rectangle((x, 0.1), 0.21, 0.8, transform=ax.transAxes,
                                       facecolor="#f2f5f8", edgecolor=AZUL, lw=1))
            ax.text(x + 0.105, 0.62, str(v), transform=ax.transAxes, ha="center",
                    fontsize=22, fontweight="bold", color=AZUL)
            ax.text(x + 0.105, 0.28, lab, transform=ax.transAxes, ha="center", fontsize=9, color=GRIS)
        fig.text(0.09, 0.10, "Padrón candidato no oficial · pendiente de validación manual.", fontsize=9, color=GRIS)
        pdf.savefig(fig); plt.close(fig)

        # 3. Lectura metodológica
        fig = new_page(pdf)
        header(fig, "Lectura metodológica", "3 / 12")
        bullets(fig, 0.86, [
            "AGC / F02 — registro administrativo oficial. Mide habilitaciones aprobadas bajo rubro de "
            "elaboración de pastas. Es estricto y administrativo: una habilitación no implica local activo hoy.",
            "OpenStreetMap — relevamiento abierto auxiliar. Colaborativo y no oficial; útil para ampliar la "
            "cobertura territorial, especialmente en zonas que otras fuentes no alcanzan.",
            "Google Places API — fuente operativa no oficial. Útil para detectar locales actualmente visibles "
            "comercialmente; no es un padrón gubernamental.",
            "Integrado v2 — padrón candidato consolidado. Cruza las tres fuentes, deduplica e incluye tanto "
            "cadenas como casas independientes/de barrio. Queda pendiente de validación manual.",
            "Se preservan explícitamente los locales de una sola sede: las cadenas sirven para control de "
            "cobertura, pero el análisis central también muestra la presencia territorial de independientes.",
        ], gap=0.052)
        pdf.savefig(fig); plt.close(fig)

        # 4. Fuentes y capas
        fig = new_page(pdf)
        header(fig, "Fuentes y capas del análisis", "4 / 12")
        data = [
            ["AGC / F02", "Oficial administrativo", "11", "Habilitaciones; NO local activo"],
            ["OpenStreetMap", "Abierta auxiliar", "152", "Cobertura territorial; no oficial"],
            ["Google Places", "Operativa no oficial", "151", "Visibilidad comercial; no gubernamental"],
            ["Integrado v2", "Padrón candidato", str(n_tot), "Unión deduplicada; a validar"],
        ]
        table(fig, [0.09, 0.55, 0.84, 0.28], data,
              ["Fuente", "Naturaleza", "Detectados", "Qué puede / no puede afirmar"],
              [0.18, 0.22, 0.16, 0.44], fontsize=9)
        fig.text(0.09, 0.55, "Detectados por fuente dentro del padrón integrado post-deduplicación; "
                 "no equivale a resultados brutos.", fontsize=8.5, color=GRIS, style="italic")
        bullets(fig, 0.49, [
            "Ninguna fuente sola alcanza el universo real. AGC es preciso pero angosto; OSM y Google amplían "
            "cobertura pero no son oficiales.",
            "Aparecer en más de una fuente sube la confianza (clase multifuente). Aparecer en una sola se "
            "conserva como candidato, sin degradar a los independientes.",
            "El padrón es candidato: el número final requiere validación manual antes de presentarse como definitivo.",
        ], gap=0.05)
        pdf.savefig(fig); plt.close(fig)

        # 5. Mapa general
        fig = new_page(pdf)
        header(fig, "Mapa general (anonimizado)", "5 / 12")
        ax = fig.add_axes([0.08, 0.14, 0.84, 0.72])
        for f in gc["features"]:
            for xs, ys in poligonos(f["geometry"]):
                ax.plot(xs, ys, color="#cccccc", lw=0.7)
        for feat in geo_pts:
            lo, la = feat["geometry"]["coordinates"]
            cl = feat["properties"]["clasificacion_integrada"]
            ax.scatter(lo, la, s=14, color=CLASE_COLOR.get(cl, "#999999"), edgecolor="white", lw=0.2, zorder=3)
        ax.set_aspect(1.28); ax.axis("off")
        leg = [Line2D([0], [0], marker="o", color="w", markerfacecolor=c, markersize=8, label=CLASE_LABEL[k])
               for k, c in CLASE_COLOR.items()]
        ax.legend(handles=leg, loc="lower left", fontsize=8, frameon=False)
        fig.text(0.09, 0.10, "Puntos del padrón candidato integrado, coloreados por clase.\n"
                 "Sin nombres, direcciones ni identificadores. Contornos: comunas GCBA.",
                 fontsize=9, color=GRIS, va="top")
        pdf.savefig(fig); plt.close(fig)

        # 6. Distribución por comuna
        fig = new_page(pdf)
        header(fig, "Distribución por comuna", "6 / 12")
        top_c = com.most_common(12)[::-1]
        barh(fig, [0.13, 0.40, 0.78, 0.44], [f"Comuna {c}" for c, _ in top_c],
             [n for _, n in top_c], "#2c7fb8", "Candidatos por comuna (v2)", "candidatos")
        fig.text(0.09, 0.30, "Top comunas: 14 y 13 (33 c/u), 6 (25), 12 (24), 2 (22). El conteo incluye "
                 "cadenas e independientes.", fontsize=10, color="#222222")
        fig.text(0.09, 0.085, "Padrón candidato no oficial · pendiente de validación.", fontsize=9, color=GRIS)
        pdf.savefig(fig); plt.close(fig)

        # 7. Distribución por barrio
        fig = new_page(pdf)
        header(fig, "Distribución por barrio", "7 / 12")
        top_b = bar.most_common(12)[::-1]
        barh(fig, [0.22, 0.40, 0.70, 0.44], [b for b, _ in top_b],
             [n for _, n in top_b], "#756bb1", "Candidatos por barrio (v2)", "candidatos")
        fig.text(0.09, 0.30, "Top barrios: Palermo (33), Caballito (25), Recoleta y Belgrano (22 c/u), "
                 "Villa Urquiza (19).", fontsize=10, color="#222222")
        fig.text(0.09, 0.085, "Incluye locales independientes y de cadenas.", fontsize=9, color=GRIS)
        pdf.savefig(fig); plt.close(fig)

        # 8. Densidad por km2
        fig = new_page(pdf)
        header(fig, "Densidad por km²", "8 / 12")
        dc = dens_com[:8][::-1]
        barh(fig, [0.13, 0.57, 0.78, 0.30], [f"Comuna {c}" for c, _, _ in dc],
             [d for _, _, d in dc], "#31a354", "Densidad por comuna (candidatos/km²)", "candidatos/km²")
        db = dens_bar[:8][::-1]
        barh(fig, [0.22, 0.15, 0.70, 0.30], [b for b, _, _ in db],
             [d for _, _, d in db], "#dd8452", "Densidad por barrio (candidatos/km²)", "candidatos/km²")
        fig.text(0.09, 0.095, "Densidad = candidatos / área oficial km² (geometrías GCBA). NO es densidad por "
                 "habitante (falta dataset de población).", fontsize=9, color=GRIS)
        pdf.savefig(fig); plt.close(fig)

        # 9. Cadenas e independientes
        fig = new_page(pdf)
        header(fig, "Cadenas e independientes", "9 / 12")
        bullets(fig, 0.86, [
            f"El análisis no es un informe de franquicias: {n_ind} de {n_tot} candidatos son locales "
            "independientes / de barrio o de una sola sede.",
            f"{n_cad} establecimientos pertenecen a cadenas reconocidas, usadas para control de cobertura.",
            "La auditoría no detectó inflación de cadenas: los conteos son unión legítima de fuentes, no "
            "duplicados mal fusionados.",
        ], gap=0.045)
        top_cad = [(r["cadena"], int(r["sucursales"])) for r in cobertura][:8][::-1]
        barh(fig, [0.30, 0.16, 0.60, 0.42], [c for c, _ in top_cad], [n for _, n in top_cad],
             "#c0762b", "Principales cadenas detectadas (sucursales)", "sucursales")
        fig.text(0.09, 0.095, "Las cadenas se reportan para control de cobertura; el foco del análisis "
                 "incluye a los independientes.", fontsize=9, color=GRIS)
        pdf.savefig(fig); plt.close(fig)

        # 10. Control de calidad
        fig = new_page(pdf)
        header(fig, "Control de calidad", "10 / 12")
        bullets(fig, 0.86, [
            "La Juvenil (cadena más grande): 28 sucursales = unión de fuentes (19 por Google, 19 por OSM, "
            "10 en común). Las solo-OSM están a más de 600 m de cualquier sucursal de Google: son locales "
            "distintos, no duplicados.",
            f"Cadenas auditadas: {rqc['cadenas_auditadas']} · ninguna con alerta de inflación.",
            f"Posibles duplicados revisados: {rqc['posibles_duplicados_pares']} pares; al inspeccionarlos "
            "resultaron locales distintos (nombres diferentes).",
            f"Falsas fusiones: {rqc['falsas_fusiones_grupos']}.",
            "4 casos marcados para revisar fusión se resolvieron: 2 duplicados fusionados con su candidato A, "
            "1 descartado por ser bodegón, 1 mantenido en revisión.",
            f"{n_rev} casos quedan pendientes de validación manual.",
        ], gap=0.046)
        fig.text(0.09, 0.085, "El padrón candidato quedó cerrado en v2 tras la auditoría de calidad.",
                 fontsize=9, color=GRIS)
        pdf.savefig(fig); plt.close(fig)

        # 11. Limitaciones
        fig = new_page(pdf)
        header(fig, "Limitaciones", "11 / 12")
        bullets(fig, 0.86, [
            "No es un censo definitivo ni un padrón oficial de casas de pastas: es un padrón candidato.",
            "Google Places y OpenStreetMap no son fuentes oficiales; reflejan visibilidad comercial y "
            "relevamiento colaborativo, no un registro gubernamental.",
            "AGC es oficial pero angosto: mide habilitaciones de un rubro estricto y no implica local activo.",
            "Puede haber locales cerrados (que figuran) o faltantes (que no figuran en ninguna fuente).",
            "La deduplicación entre fuentes es heurística (nombre + distancia + similitud); puede dejar "
            "algún duplicado o separar sucursales.",
            "Falta validación manual / de campo antes de considerar el número definitivo.",
            "No se calcula densidad por habitante (no hay dataset de población en el proyecto).",
        ], gap=0.05)
        pdf.savefig(fig); plt.close(fig)

        # 12. Próximos pasos
        fig = new_page(pdf)
        header(fig, "Próximos pasos", "12 / 12")
        bullets(fig, 0.86, [
            f"Validar los {n_rev} casos en revisión manual (dudosos y posibles faltantes).",
            "Revisar locales independientes prioritarios, núcleo del universo de casas de barrio.",
            "Confirmar los locales multifuente (mayor confianza) como base más sólida.",
            "Incorporar al pipeline DataGastro solo después de la validación manual, con aprobación.",
            "Replicar la metodología (oficial + abierta + operativa, con auditoría de calidad) en otros "
            "rubros gastronómicos.",
        ], gap=0.052)
        fig.text(0.09, 0.12, "Padrón candidato no oficial · base para validación territorial · "
                 "no reemplaza el registro oficial.", fontsize=9, color=GRIS)
        pdf.savefig(fig); plt.close(fig)

        d = pdf.infodict()
        d["Title"] = "Casas de pastas en CABA — Padrón candidato integrado v2"
        d["Author"] = "DataGastro"
        d["Subject"] = "Padrón candidato no oficial (AGC + OSM + Google Places). Pendiente de validación manual."

    escribir_md(hoy, rv2, rqc, com, bar, dens_com, dens_bar, cobertura)
    print(f"PDF generado: {PDF}")
    print(f"Páginas: 12 | tamaño: {PDF.stat().st_size/1024:.0f} KB")
    print(f"MD generado: {MD}")


def escribir_md(hoy, rv2, rqc, com, bar, dens_com, dens_bar, cobertura):
    n_tot = rv2["candidatos_unicos"]
    L = []
    L.append("# Casas de pastas en CABA — Padrón candidato integrado (v2)\n")
    L.append(f"_Fecha: {hoy} · Versión v2 · **Padrón candidato no oficial, pendiente de validación manual.**_\n")
    L.append("> Se construyó un padrón candidato integrado de **261** posibles casas de pastas en CABA, "
             "combinando registro oficial, fuentes abiertas y señales operativas no oficiales. El resultado "
             "no reemplaza al registro oficial ni constituye un censo definitivo: sirve como base analítica "
             "para validación territorial.\n")
    L.append("## Resumen ejecutivo\n")
    L.append(f"- **{n_tot}** candidatos únicos.")
    L.append(f"- **{rv2['independientes']}** independientes / de barrio · **{rv2['cadenas']}** en cadenas.")
    L.append(f"- **{rv2['multifuente']}** multifuente (≥2 fuentes).")
    L.append(f"- **{rv2['revision_manual_prioritaria']}** pendientes de validación manual.\n")
    L.append("## Fuentes y capas\n")
    L.append("| Fuente | Naturaleza | Detectados | Qué puede / no puede afirmar |")
    L.append("|---|---|---|---|")
    L.append("| AGC / F02 | Registro administrativo **oficial** | 11 | Habilitaciones; **no implica local activo** |")
    L.append("| OpenStreetMap | Relevamiento **abierto auxiliar** | 152 | Cobertura territorial; **no oficial** |")
    L.append("| Google Places | **Operativa no oficial** | 151 | Visibilidad comercial; **no gubernamental** |")
    L.append(f"| Integrado v2 | **Padrón candidato** | {n_tot} | Unión deduplicada; **a validar** |\n")
    L.append("_Detectados por fuente dentro del padrón integrado post-deduplicación; no equivale a "
             "resultados brutos._\n")
    L.append("## Clases integradas\n")
    L.append(f"- Multifuente: {rv2['clase_A_integrado_multifuente']} · Google: {rv2['clase_A_google_probable']} "
             f"· OSM: {rv2['clase_A_osm_auxiliar']} · AGC oficial estricto: {rv2['clase_A_agc_oficial_estricto']} "
             f"· Revisión manual: {rv2['clase_B_revision_manual']}\n")
    L.append("## Distribución territorial\n")
    L.append("- **Top comunas:** " + ", ".join(f"{c} ({n})" for c, n in com.most_common(5)) + ".")
    L.append("- **Top barrios:** " + ", ".join(f"{b} ({n})" for b, n in bar.most_common(5)) + ".")
    L.append("- **Densidad comuna (cand./km²):** " + ", ".join(f"{c} ({d:.2f})" for c, _, d in dens_com[:5]) + ".")
    L.append("- **Densidad barrio (cand./km²):** " + ", ".join(f"{b} ({d:.2f})" for b, _, d in dens_bar[:5]) +
             ". No es densidad por habitante.\n")
    L.append("## Cadenas e independientes\n")
    L.append(f"No es un informe de franquicias: **{rv2['independientes']}** independientes. Principales cadenas "
             "(control de cobertura): " + ", ".join(f"{r['cadena']} ({r['sucursales']})" for r in cobertura[:6]) + ".\n")
    L.append("## Control de calidad\n")
    L.append("- La Juvenil: 28 sucursales = unión de fuentes (19 Google + 19 OSM, 10 en común); las solo-OSM "
             "están a >600 m de cualquier Google → locales distintos, no duplicados.")
    L.append(f"- Cadenas auditadas: {rqc['cadenas_auditadas']} · sin alertas de inflación.")
    L.append(f"- Posibles duplicados: {rqc['posibles_duplicados_pares']} (resultaron distintos) · "
             f"falsas fusiones: {rqc['falsas_fusiones_grupos']}.")
    L.append("- 4 casos `revisar_fusion` resueltos: 2 fusionados con su A, 1 descartado (bodegón), 1 mantenido en B.\n")
    L.append("## Limitaciones\n")
    L.append("- No es censo definitivo ni padrón oficial. Google/OSM no son oficiales. AGC es oficial pero "
             "angosto y no implica local activo. Puede haber locales cerrados o faltantes. Falta validación "
             "manual/campo.\n")
    L.append("## Próximos pasos\n")
    L.append(f"1. Validar los {rv2['revision_manual_prioritaria']} casos manuales.\n2. Revisar independientes "
             "prioritarios.\n3. Confirmar multifuente.\n4. Incorporar al pipeline solo tras validación.\n"
             "5. Replicar la metodología en otros rubros.\n")
    MD.write_text("\n".join(L), encoding="utf-8")


if __name__ == "__main__":
    main()
