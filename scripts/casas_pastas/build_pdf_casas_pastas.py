"""Arma el PDF del informe de casas/fábricas de pastas (10 páginas).

Usa SOLO la versión sanitizada (outputs/casas_pastas_reporte/): agregados, sin datos personales.
No depende de librerías extra (solo matplotlib). Salida:
  outputs/casas_pastas_reporte/INFORME_CASAS_PASTAS.pdf
"""
from __future__ import annotations

import csv
import datetime as dt
import textwrap
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.image as mpimg  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
REP = ROOT / "outputs" / "casas_pastas_reporte"
PDF = REP / "INFORME_CASAS_PASTAS.pdf"

A4 = (8.27, 11.69)
AZUL = "#1f3b57"
ROJO = "#c0392b"
GRIS = "#555555"


def read(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def new_page(pdf: PdfPages):
    fig = plt.figure(figsize=A4)
    fig.subplots_adjust(left=0.09, right=0.93, top=0.92, bottom=0.07)
    return fig


def header(fig, titulo: str, num: str = ""):
    fig.text(0.09, 0.95, "Casas y fábricas de pastas en CABA", color=GRIS, fontsize=9)
    fig.text(0.09, 0.925, titulo, color=AZUL, fontsize=18, fontweight="bold")
    fig.text(0.93, 0.95, num, color=GRIS, fontsize=9, ha="right")
    fig.lines.append(plt.Line2D([0.09, 0.93], [0.915, 0.915], color=AZUL, lw=1.2, transform=fig.transFigure))


def bullets(fig, y0: float, items: list[str], size=11, gap=0.038, wrap=80, color="#222222"):
    y = y0
    for it in items:
        marker = "•" if not it.startswith("  ") else "–"
        lines = textwrap.wrap(it.strip(), wrap) or [""]
        fig.text(0.11, y, marker, fontsize=size, color=ROJO, va="top")
        for j, ln in enumerate(lines):
            fig.text(0.135, y - j * 0.024, ln, fontsize=size, color=color, va="top")
        y -= gap + (len(lines) - 1) * 0.024
    return y


def table_page(fig, top, cols, headers, col_w, title=None, y_top=0.86, fontsize=10):
    ax = fig.add_axes([0.09, 0.12, 0.84, y_top - 0.12])
    ax.axis("off")
    data = [[r.get(c, "") for c in cols] for r in top]
    if title:
        ax.set_title(title, color=AZUL, fontsize=12, loc="left", pad=10)
    t = ax.table(cellText=data, colLabels=headers, colWidths=col_w, loc="upper center", cellLoc="center")
    t.auto_set_font_size(False)
    t.set_fontsize(fontsize)
    t.scale(1, 1.6)
    for (r, _c), cell in t.get_celld().items():
        cell.set_edgecolor("#dddddd")
        if r == 0:
            cell.set_facecolor(AZUL)
            cell.set_text_props(color="white", fontweight="bold")
        elif r % 2 == 0:
            cell.set_facecolor("#f2f5f8")
    return ax


def barh_axes(fig, rect, labels, values, color, title, xlabel):
    ax = fig.add_axes(rect)
    ax.barh(labels, values, color=color)
    ax.set_title(title, color=AZUL, fontsize=11, loc="left")
    ax.set_xlabel(xlabel, fontsize=9)
    ax.tick_params(labelsize=9)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    return ax


def main():
    resumen = read(REP / "tabla_resumen_general.csv")
    tc = read(REP / "top_comunas_cantidad.csv")
    tb = read(REP / "top_barrios_cantidad.csv")
    dc = read(REP / "top_comunas_densidad.csv")
    db = read(REP / "top_barrios_densidad.csv")
    comp = read(REP / "comparacion_agc_osm.csv")
    lims = read(REP / "limitaciones_metodologicas.csv")
    hoy = dt.date.today().isoformat()

    with PdfPages(PDF) as pdf:
        # ---- 1. Portada ----
        fig = new_page(pdf)
        fig.text(0.09, 0.70, "Casas y fábricas de pastas\nen la Ciudad de Buenos Aires",
                 fontsize=28, fontweight="bold", color=AZUL, va="top")
        fig.text(0.09, 0.56, "Diagnóstico territorial — distribución, densidad y fuentes",
                 fontsize=14, color=GRIS)
        fig.lines.append(plt.Line2D([0.09, 0.6], [0.52, 0.52], color=ROJO, lw=2, transform=fig.transFigure))
        fig.text(0.09, 0.46,
                 "Datos públicos: Habilitaciones AGC (F02) como registro administrativo oficial,\n"
                 "y OpenStreetMap como relevamiento abierto auxiliar. No incluye datos personales.",
                 fontsize=11, color="#333333", va="top")
        fig.text(0.09, 0.12, f"Fecha: {hoy}", fontsize=10, color=GRIS)
        fig.text(0.09, 0.095, "Versión sanitizada para informe (sin razón social, direcciones ni datos individuales)",
                 fontsize=9, color=GRIS)
        pdf.savefig(fig); plt.close(fig)

        # ---- 2. Resumen ejecutivo ----
        fig = new_page(fig=None) if False else new_page(pdf)
        header(fig, "Resumen ejecutivo", "2 / 10")
        bullets(fig, 0.86, [
            "El registro administrativo oficial (AGC / F02) identifica 10 casas/fábricas de pastas "
            "estrictas (rubro de elaboración de pastas), deduplicadas; 9 con geolocalización.",
            "Son habilitaciones aprobadas, no locales activos: un registro puede estar cerrado hoy.",
            "OpenStreetMap, como relevamiento abierto auxiliar, sugiere un universo operativo mucho "
            "mayor: 138 puntos con tag shop=pasta o equivalente (no oficial, no verificado).",
            "La diferencia 10 vs 138 no es un error: refleja distintas fuentes y definiciones. El "
            "número oficial es 10; el universo real probable es mayor y queda pendiente de validación.",
            "Distribución dispersa: Comuna 13 concentra 2; el resto, 1 por comuna entre 8 comunas.",
            "Mayor densidad por km² (oficial): Comuna 2, Comuna 5 y Comuna 13; barrios Colegiales y Floresta.",
            "No se calculó densidad por habitante (falta dataset de población en el proyecto).",
        ])
        pdf.savefig(fig); plt.close(fig)

        # ---- 3. Metodología y fuentes ----
        fig = new_page(pdf)
        header(fig, "Metodología y fuentes", "3 / 10")
        bullets(fig, 0.86, [
            "Universo estricto: comercios cuyo rubro principal es elaboración o venta de pastas "
            "(frescas/secas), pastificios y casas de pastas. Se excluyen restaurantes italianos, "
            "trattorias, pizzerías, bares y gastronómicos generales.",
            "Clasificación en tres niveles: A estricto confirmado, B probable, C dudoso/descartado. "
            "El análisis principal usa A; A y B nunca se mezclan.",
            "Fuente principal: F02 — Habilitaciones aprobadas AGC (datos públicos). Registro "
            "administrativo, no padrón de locales activos.",
            "Fuente auxiliar: OpenStreetMap / Overpass (abierta, colaborativa, no oficial).",
            "Geometrías oficiales GCBA (comunas y barrios) para asignación territorial y densidad.",
            "Geocodificación con caché local del proyecto; sin servicios externos pagos.",
        ], gap=0.05)
        table_page(fig, comp, ["fuente", "universo_A", "universo_B"],
                   ["Fuente", "Universo A", "Universo B"], [0.5, 0.22, 0.22],
                   y_top=0.36)
        fig.text(0.09, 0.10, "AGC = registro administrativo oficial · OSM = relevamiento abierto auxiliar.",
                 fontsize=9, color=GRIS)
        pdf.savefig(fig); plt.close(fig)

        # ---- 4. Mapa de nodos ----
        fig = new_page(pdf)
        header(fig, "Mapa de nodos", "4 / 10")
        mapa = REP / "mapa_nodos_agregado.png"
        if mapa.exists():
            ax = fig.add_axes([0.12, 0.12, 0.76, 0.74])
            ax.imshow(mpimg.imread(mapa)); ax.axis("off")
        fig.text(0.09, 0.085, "Puntos del registro AGC oficial (universo A). Sin etiquetas individuales. "
                 "OSM (auxiliar) no se incluye en el mapa.", fontsize=9, color=GRIS)
        pdf.savefig(fig); plt.close(fig)

        # ---- 5. Distribución por comuna ----
        fig = new_page(pdf)
        header(fig, "Distribución por comuna", "5 / 10")
        barh_axes(fig, [0.12, 0.40, 0.80, 0.42],
                  [f"Comuna {r['comuna']}" for r in sorted(tc, key=lambda r: int(r["cantidad"]))],
                  [int(r["cantidad"]) for r in sorted(tc, key=lambda r: int(r["cantidad"]))],
                  "#2c7fb8", "Cantidad por comuna (universo A)", "establecimientos")
        table_page(fig, tc, ["comuna", "cantidad", "area_km2", "densidad_por_km2"],
                   ["Comuna", "Cantidad", "Área km²", "Dens./km²"], [0.22, 0.22, 0.24, 0.24],
                   y_top=0.34, fontsize=9)
        fig.text(0.09, 0.085, "Habilitaciones AGC vinculadas a casas/fábricas de pastas. No son locales activos.",
                 fontsize=9, color=GRIS)
        pdf.savefig(fig); plt.close(fig)

        # ---- 6. Distribución por barrio ----
        fig = new_page(pdf)
        header(fig, "Distribución por barrio", "6 / 10")
        barh_axes(fig, [0.28, 0.40, 0.64, 0.42],
                  [r["barrio"] for r in sorted(tb, key=lambda r: int(r["cantidad"]))],
                  [int(r["cantidad"]) for r in sorted(tb, key=lambda r: int(r["cantidad"]))],
                  "#756bb1", "Cantidad por barrio (universo A, geolocalizados)", "establecimientos")
        table_page(fig, tb, ["barrio", "comuna", "cantidad", "densidad_por_km2"],
                   ["Barrio", "Comuna", "Cantidad", "Dens./km²"], [0.40, 0.18, 0.20, 0.20],
                   y_top=0.34, fontsize=9)
        fig.text(0.09, 0.085, "Solo establecimientos geolocalizados (9 de 10).", fontsize=9, color=GRIS)
        pdf.savefig(fig); plt.close(fig)

        # ---- 7. Densidad por km² ----
        fig = new_page(pdf)
        header(fig, "Densidad por km²", "7 / 10")
        barh_axes(fig, [0.12, 0.56, 0.80, 0.30],
                  [f"Comuna {r['comuna']}" for r in sorted(dc, key=lambda r: float(r["densidad_por_km2"]))],
                  [float(r["densidad_por_km2"]) for r in sorted(dc, key=lambda r: float(r["densidad_por_km2"]))],
                  "#31a354", "Densidad por comuna (casas/km²)", "casas/km²")
        barh_axes(fig, [0.28, 0.14, 0.64, 0.30],
                  [r["barrio"] for r in sorted(db, key=lambda r: float(r["densidad_por_km2"]))],
                  [float(r["densidad_por_km2"]) for r in sorted(db, key=lambda r: float(r["densidad_por_km2"]))],
                  "#dd8452", "Densidad por barrio (casas/km², geolocalizados)", "casas/km²")
        fig.text(0.09, 0.095, "Densidad = establecimientos / área oficial km². Con N pequeño, leer como indicativo.",
                 fontsize=9, color=GRIS)
        pdf.savefig(fig); plt.close(fig)

        # ---- 8. Comparación AGC vs OSM ----
        fig = new_page(pdf)
        header(fig, "Comparación AGC vs OSM", "8 / 10")
        bullets(fig, 0.86, [
            "Registro administrativo oficial (AGC / F02): 10 establecimientos A. Es lo formalmente "
            "habilitado bajo el rubro de elaboración de pastas.",
            "Relevamiento abierto auxiliar (OpenStreetMap): 138 puntos A (shop=pasta y equivalentes). "
            "Refleja un universo operativo más amplio, pero no es oficial ni está verificado.",
            "Pendiente de validación: 1 caso B en AGC y los puntos de OSM, hasta confirmarlos por "
            "validación manual o API oficial.",
            "Lectura: la brecha es de fuente y definición, no un error. Para política pública, el "
            "número oficial es 10; el universo real probable es bastante mayor.",
        ], gap=0.052)
        # gráfico comparativo
        ax = fig.add_axes([0.14, 0.16, 0.72, 0.30])
        fuentes = ["AGC / F02\n(oficial)", "OpenStreetMap\n(auxiliar)"]
        ax.bar(fuentes, [int(comp[0]["universo_A"]), int(comp[1]["universo_A"])],
               color=[AZUL, "#7fb069"], width=0.5)
        for i, v in enumerate([int(comp[0]["universo_A"]), int(comp[1]["universo_A"])]):
            ax.text(i, v + 2, str(v), ha="center", fontweight="bold")
        ax.set_title("Universo A por fuente", color=AZUL, fontsize=11, loc="left")
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        pdf.savefig(fig); plt.close(fig)

        # ---- 9. Limitaciones ----
        fig = new_page(pdf)
        header(fig, "Limitaciones metodológicas", "9 / 10")
        lims_wrap = [
            {"id": r["id"],
             "limitacion": "\n".join(textwrap.wrap(r["limitacion"], 34)),
             "implicancia": "\n".join(textwrap.wrap(r["implicancia"], 40))}
            for r in lims
        ]
        ax_lim = table_page(fig, lims_wrap, ["id", "limitacion", "implicancia"],
                            ["", "Limitación", "Implicancia"], [0.07, 0.42, 0.45],
                            y_top=0.86, fontsize=9)
        for cell in ax_lim.tables[0].get_celld().values():
            cell.set_height(cell.get_height() * 1.4)
            cell.set_text_props(va="center")
        pdf.savefig(fig); plt.close(fig)

        # ---- 10. Próximos pasos ----
        fig = new_page(pdf)
        header(fig, "Próximos pasos", "10 / 10")
        bullets(fig, 0.86, [
            "Ampliar cobertura con Google Places API oficial (plan ya preparado): consultas por "
            "casa de pastas / pastas frescas / pastificio y grilla por comuna. Requiere autorización "
            "y presupuesto; sin scraping.",
            "Validación manual del universo B (AGC) y de los puntos de OSM para promover a confirmados.",
            "Sumar dataset de población por comuna/barrio para calcular densidad por habitante.",
            "Revisar rubros AGC genéricos (comercio minorista de alimentos) con nombre de pastas, "
            "para recuperar casas de pastas registradas bajo rubros amplios.",
            "Recién con el universo A validado y ampliado, evaluar (con aprobación) un cruce hacia "
            "el pipeline principal.",
        ], gap=0.055)
        fig.text(0.09, 0.10, "Documento de diagnóstico. Fuente: datos públicos AGC + OSM auxiliar. "
                 "Sin datos personales.", fontsize=9, color=GRIS)
        pdf.savefig(fig); plt.close(fig)

        d = pdf.infodict()
        d["Title"] = "Casas y fábricas de pastas en CABA"
        d["Author"] = "DataGastro"
        d["Subject"] = "Diagnóstico territorial (datos públicos AGC + OSM auxiliar)"

    print(f"PDF generado: {PDF}")
    print(f"Páginas: 10 | tamaño: {PDF.stat().st_size/1024:.0f} KB")


if __name__ == "__main__":
    main()
