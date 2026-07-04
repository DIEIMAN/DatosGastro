# -*- coding: utf-8 -*-
"""
Fase 4A — Rediseño visual PolosGastro + mapa territorial estático.

Genera, en outputs/polos_gastro/graficos/fase4a/ (NO sobrescribe los PNG anteriores):
- universo_polos_por_grupo_v2.png
- precision_delimitacion_polos_v2.png
- familias_territoriales_polos_v2.png  (rediseño: barras agrupadas)
- mapa_conceptual_polos_gastro_resumido_v2.png  (sin solapes, sin caja que tape)
- mapa_conceptual_polos_gastro_completo_v2.png
- mapa_estatico_caba_polos_gastro_v1.png         (GeoPandas + barrios/comunas oficiales)
- mapa_estatico_caba_polos_gastro_nucleo_v1.png  (núcleo + relevantes)

También escribe outputs/polos_gastro/base_cartografica_visual_polos_gastro.csv.

Reglas: barrios/comunas son REFERENCIA territorial, no delimitación oficial de polos.
No usa Google Places. No crea polígonos de polos. No geocodifica locales.
"""
from __future__ import annotations

import csv
import textwrap
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

import geopandas as gpd

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "outputs" / "polos_gastro"
GRAF = OUT / "graficos" / "fase4a"
CARTO = ROOT / "PolosGastro" / "cartografia"
FECHA_CORTE = "2026-06-29"

BASE_MAPA = OUT / "base_mapa_conceptual_polos_gastro.csv"
BASE_CARTO_VISUAL = OUT / "base_cartografica_visual_polos_gastro.csv"
BARRIOS_GEOJSON = CARTO / "barrios_caba.geojson"
COMUNAS_GEOJSON = CARTO / "comunas_caba.geojson"

GROUP_ORDER = ["nucleo_principal", "zona_relevante", "emergente_o_candidato", "anexo", "no_incluir_por_ahora"]
GROUP_LABELS = {
    "nucleo_principal": "Núcleo principal",
    "zona_relevante": "Zona relevante",
    "emergente_o_candidato": "Emergente / candidato",
    "anexo": "Anexo",
    "no_incluir_por_ahora": "No incluir por ahora",
}
GROUP_COLORS = {
    "nucleo_principal": "#275DAD",
    "zona_relevante": "#2A9D8F",
    "emergente_o_candidato": "#E9B44C",
    "anexo": "#7D8597",
    "no_incluir_por_ahora": "#C44536",
}
PRECISION_ORDER = ["alta", "media", "baja", "sin_delimitacion"]
PRECISION_LABELS = {"alta": "Alta", "media": "Media", "baja": "Baja", "sin_delimitacion": "Sin delimitación"}
# Escala ordinal monocroma (azul DataGastro de oscuro a claro) para reforzar que es una escala.
PRECISION_COLORS = {"alta": "#1F4E79", "media": "#2E74B5", "baja": "#9DC3E6", "sin_delimitacion": "#C44536"}

FAMILY_LABELS = {
    "palermo_y_subpolos": "Palermo y subpolos",
    "zona_costera_y_turistica": "Zona costera y turística",
    "sur_historico_y_tradicional": "Sur histórico y tradicional",
    "zona_central": "Zona central y Recoleta",
    "belgrano_y_norte": "Belgrano y norte",
    "oeste_y_barrios_con_oferta": "Oeste y barrios con oferta",
    "corredores_emergentes_norte_oeste": "Corredores emergentes norte-oeste",
    "cultura_avenidas_y_noches": "Cultura, avenidas y noches",
}
FAMILY_ORDER = list(FAMILY_LABELS.keys())

CARTO_COLUMNS = [
    "polo_id", "nombre_publico", "familia_territorial", "grupo_informe", "estado_validacion",
    "tipo_area", "nivel_precision_delimitacion", "representacion_sugerida", "barrios_asociados",
    "comunas_probables", "mostrar_en_mapa_estatico", "tipo_visualizacion_estatica",
    "etiqueta_mapa", "prioridad_visual", "riesgo_metodologico", "observaciones",
]

FOOTER = "Fuente: insumos PolosGastro. Fecha de corte: " + FECHA_CORTE + "."


def norm(s: str) -> str:
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    return s.lower().strip()


def read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def wrap(s: str, w: int = 22) -> str:
    return "\n".join(textwrap.wrap(s, width=w, break_long_words=False))


def footer(fig, extra: str = "") -> None:
    fig.text(0.01, 0.01, f"Base: 32 polos. {FOOTER} {extra}".strip(),
             ha="left", va="bottom", fontsize=7.5, color="#4A4A4A")


# ---------------------------------------------------------------------------
# Base cartográfica visual
# ---------------------------------------------------------------------------
def primer_barrio(barrios_asociados: str) -> str:
    raw = barrios_asociados.split(";")[0].split(",")[0].strip()
    raw = raw.replace("La Paternal", "Paternal").replace("Nunez/Belgrano entorno Ciudad Universitaria", "Nunez")
    return raw


def tipo_visual_estatica(grupo: str, precision: str, rep: str) -> str:
    if grupo == "no_incluir_por_ahora":
        return "no_mapear"
    if grupo == "anexo":
        return "etiqueta_sin_geometria"
    if rep == "linea_corredor_conceptual":
        return "linea_conceptual"
    if precision in {"alta", "media"} and grupo in {"nucleo_principal", "zona_relevante"}:
        return "resaltar_barrio"
    if precision == "baja":
        return "punto_aproximado_por_barrio"
    return "punto_aproximado_por_barrio"


def build_base_carto(base_mapa: list[dict], barrios_norm: set[str]) -> list[dict]:
    rows = []
    for r in base_mapa:
        grupo = r["grupo_informe"]
        precision = r["nivel_precision_delimitacion"]
        rep = r["representacion_sugerida"]
        tve = tipo_visual_estatica(grupo, precision, rep)
        pb = primer_barrio(r["barrios_asociados"])
        match = norm(pb) in barrios_norm
        # Mostrar en mapa estático: núcleo, relevante y candidatos con barrio reconocible; no anexos/no_incluir.
        mostrar = "no"
        if grupo in {"nucleo_principal", "zona_relevante"} and match:
            mostrar = "si"
        elif grupo == "emergente_o_candidato" and match and tve != "no_mapear":
            mostrar = "si"
        prioridad = {"nucleo_principal": "1", "zona_relevante": "2", "emergente_o_candidato": "3",
                     "anexo": "4", "no_incluir_por_ahora": "5"}[grupo]
        rows.append({
            "polo_id": r["polo_id"],
            "nombre_publico": r["nombre_publico"],
            "familia_territorial": r["familia_territorial"],
            "grupo_informe": grupo,
            "estado_validacion": r["estado_validacion"],
            "tipo_area": r["tipo_area"],
            "nivel_precision_delimitacion": precision,
            "representacion_sugerida": rep,
            "barrios_asociados": r["barrios_asociados"],
            "comunas_probables": r["comunas_probables"],
            "mostrar_en_mapa_estatico": mostrar,
            "tipo_visualizacion_estatica": tve,
            "etiqueta_mapa": r["nombre_publico"],
            "prioridad_visual": prioridad,
            "riesgo_metodologico": "Barrio asociado es referencia territorial, no delimitacion del polo.",
            "observaciones": f"barrio_referencia={pb}; match_oficial={'si' if match else 'no'}",
        })
    return rows


def write_base_carto(rows: list[dict]) -> None:
    with BASE_CARTO_VISUAL.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=CARTO_COLUMNS)
        w.writeheader()
        w.writerows(rows)


# ---------------------------------------------------------------------------
# Gráficos metodológicos v2
# ---------------------------------------------------------------------------
def chart_universo(rows: list[dict]) -> None:
    counts = Counter(r["grupo_informe"] for r in rows)
    labels = [GROUP_LABELS[g] for g in GROUP_ORDER]
    values = [counts[g] for g in GROUP_ORDER]
    colors = [GROUP_COLORS[g] for g in GROUP_ORDER]
    fig, ax = plt.subplots(figsize=(10, 5.6), dpi=180)
    bars = ax.barh(labels, values, color=colors)
    ax.invert_yaxis()
    ax.set_title("Universo PolosGastro por grupo de informe", fontsize=15, loc="left", pad=14)
    ax.set_xlabel("Cantidad de polos")
    ax.set_xlim(0, max(values) + 2)
    ax.grid(axis="x", color="#E2E2E2", linewidth=0.7); ax.set_axisbelow(True)
    for b, v in zip(bars, values):
        ax.text(v + 0.12, b.get_y() + b.get_height() / 2, str(v), va="center", fontsize=10)
    ax.spines[["top", "right", "left"]].set_visible(False)
    fig.text(0.01, 0.06, "Jerarquía metodológica del universo; no mide intensidad gastronómica.",
             fontsize=8.5, color="#555")
    footer(fig)
    fig.tight_layout(rect=(0, 0.08, 1, 0.97))
    fig.savefig(GRAF / "universo_polos_por_grupo_v2.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def chart_precision(rows: list[dict]) -> None:
    counts = Counter(r["nivel_precision_delimitacion"] for r in rows)
    labels = [PRECISION_LABELS[p] for p in PRECISION_ORDER]
    values = [counts[p] for p in PRECISION_ORDER]
    colors = [PRECISION_COLORS[p] for p in PRECISION_ORDER]
    fig, ax = plt.subplots(figsize=(9, 5.6), dpi=180)
    bars = ax.bar(labels, values, color=colors)
    ax.set_title("Precisión de delimitación territorial", fontsize=15, loc="left", pad=14)
    ax.set_ylabel("Cantidad de polos")
    ax.set_ylim(0, max(values) + 3)
    ax.grid(axis="y", color="#E2E2E2", linewidth=0.7); ax.set_axisbelow(True)
    for b, v in zip(bars, values):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.2, str(v), ha="center", fontsize=10)
    ax.spines[["top", "right"]].set_visible(False)
    fig.text(0.01, 0.06, "Escala ordinal: la baja precisión y los casos sin delimitación impiden polígonos cerrados.",
             fontsize=8.5, color="#555")
    footer(fig)
    fig.tight_layout(rect=(0, 0.08, 1, 0.97))
    fig.savefig(GRAF / "precision_delimitacion_polos_v2.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def chart_familias(rows: list[dict]) -> None:
    # Rediseño: barras agrupadas (no apiladas) por familia x grupo.
    data: dict[str, Counter] = defaultdict(Counter)
    for r in rows:
        data[r["familia_territorial"]][r["grupo_informe"]] += 1
    families = [f for f in FAMILY_ORDER if f in data]
    labels = [wrap(FAMILY_LABELS[f], 18) for f in families]
    import numpy as np
    x = np.arange(len(families))
    n = len(GROUP_ORDER)
    width = 0.16
    fig, ax = plt.subplots(figsize=(13.5, 6.6), dpi=180)
    for i, g in enumerate(GROUP_ORDER):
        vals = [data[f][g] for f in families]
        offset = (i - (n - 1) / 2) * width
        bars = ax.bar(x + offset, vals, width, label=GROUP_LABELS[g], color=GROUP_COLORS[g])
        for b, v in zip(bars, vals):
            if v:
                ax.text(b.get_x() + b.get_width() / 2, v + 0.05, str(v), ha="center", fontsize=7.5, color="#333")
    ax.set_xticks(x, labels, fontsize=9)
    ax.set_ylabel("Cantidad de polos")
    ax.set_ylim(0, 7.5)
    ax.set_title("Familias territoriales por grupo de informe", fontsize=15, loc="left", pad=14)
    ax.grid(axis="y", color="#E2E2E2", linewidth=0.7); ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=5, frameon=False, fontsize=8.5)
    fig.text(0.01, 0.045, "Las familias organizan la lectura territorial; no equivalen a polígonos ni a límites administrativos.",
             fontsize=8, color="#555")
    footer(fig)
    fig.tight_layout(rect=(0, 0.13, 1, 0.96))
    fig.savefig(GRAF / "familias_territoriales_polos_v2.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Mapas conceptuales v2
# ---------------------------------------------------------------------------
def marker_for_rep(rep: str) -> str:
    return {"punto_conceptual": "o", "etiqueta_zona": "s", "linea_corredor_conceptual": "D",
            "familia_sin_geometria": "^", "no_mapear": "x"}.get(rep, "o")


def concept_map(rows: list[dict], filename: str, completo: bool) -> None:
    # Grupos en X (sin no_incluir); familias en Y.
    groups_x = [g for g in GROUP_ORDER if g != "no_incluir_por_ahora"]
    if not completo:
        # Resumido: núcleo, relevante y candidatos; sin anexos ni no_incluir.
        groups_x = ["nucleo_principal", "zona_relevante", "emergente_o_candidato"]
        visibles = [r for r in rows if r["grupo_informe"] in groups_x]
    else:
        visibles = [r for r in rows if r["grupo_informe"] in groups_x]

    fams_present = [f for f in FAMILY_ORDER if any(r["familia_territorial"] == f for r in visibles)]
    fam_y = {f: i * 1.0 for i, f in enumerate(reversed(fams_present))}
    grp_x = {g: i * 2.0 for i, g in enumerate(groups_x)}

    # Distribuir varios polos en la misma celda verticalmente para evitar solape.
    fig, ax = plt.subplots(figsize=(15, 8.2 if not completo else 9.6), dpi=180)
    ax.set_facecolor("#FBFBFB")
    fig.suptitle("Mapa conceptual PolosGastro" + (" — resumido" if not completo else " — completo"),
                 fontsize=16, x=0.07, y=0.97, ha="left")
    fig.text(0.07, 0.925, "Esquema conceptual preliminar. No representa delimitaciones oficiales.",
             fontsize=10.5, color="#C44536", weight="bold", ha="left")

    for f, y in fam_y.items():
        ax.axhline(y=y, color="#ECECEC", linewidth=0.8, zorder=0)
        ax.text(-0.55, y, wrap(FAMILY_LABELS[f], 22), ha="right", va="center", fontsize=8.5, color="#333")

    cell = defaultdict(list)
    for r in visibles:
        cell[(r["familia_territorial"], r["grupo_informe"])].append(r)

    for (fam, grp), items in cell.items():
        if fam not in fam_y or grp not in grp_x:
            continue
        x0 = grp_x[grp]; y0 = fam_y[fam]
        k = len(items)
        # spread vertical dentro de la franja de la familia
        spread = 0.34
        ys = [y0] if k == 1 else [y0 + spread * (j - (k - 1) / 2) for j in range(k)]
        for r, yy in zip(items, ys):
            color = GROUP_COLORS[grp]
            rep = r["representacion_sugerida"]
            if rep == "linea_corredor_conceptual":
                ax.plot([x0 - 0.12, x0 + 0.12], [yy, yy], color=color, linewidth=3, solid_capstyle="round", zorder=3)
            ax.scatter([x0], [yy], marker=marker_for_rep(rep), s=70, color=color,
                       edgecolor="white", linewidth=1, zorder=4)
            ax.text(x0 + 0.12, yy, wrap(r["nombre_publico"], 20), fontsize=7.6, va="center", ha="left",
                    color="#222", zorder=5)

    ax.set_xticks([grp_x[g] for g in groups_x], [GROUP_LABELS[g] for g in groups_x], fontsize=10)
    ax.set_yticks([])
    ax.set_xlim(-1.4, max(grp_x.values()) + 1.5)
    ax.set_ylim(-0.8, max(fam_y.values()) + 0.8)
    ax.spines[:].set_visible(False)

    grp_handles = [Line2D([0], [0], marker="o", color="w", label=GROUP_LABELS[g],
                          markerfacecolor=GROUP_COLORS[g], markersize=9) for g in groups_x]
    rep_handles = [Line2D([0], [0], marker=marker_for_rep(rep), color="w", label=lbl,
                          markerfacecolor="#555", markersize=8)
                   for rep, lbl in [("punto_conceptual", "Punto"), ("etiqueta_zona", "Etiqueta de zona"),
                                    ("linea_corredor_conceptual", "Eje/corredor"),
                                    ("familia_sin_geometria", "Familia sin geometría")]]
    leg1 = ax.legend(handles=grp_handles, loc="upper left", bbox_to_anchor=(0.0, -0.06),
                     ncol=len(groups_x), frameon=False, fontsize=8.5)
    ax.add_artist(leg1)
    ax.legend(handles=rep_handles, loc="upper right", bbox_to_anchor=(1.0, -0.06), ncol=4, frameon=False, fontsize=8.5)
    footer(fig, "Diagrama esquemático, sin geocodificación ni base cartográfica.")
    fig.tight_layout(rect=(0.02, 0.10, 1, 0.90))
    fig.savefig(GRAF / filename, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Mapa territorial estático (GeoPandas)
# ---------------------------------------------------------------------------
def static_map(carto_rows: list[dict], barrios: gpd.GeoDataFrame, filename: str, solo_nucleo: bool) -> None:
    barrios = barrios.to_crs(3857)
    barrios["_norm"] = barrios["nombre"].map(norm)

    if solo_nucleo:
        sel = [r for r in carto_rows if r["mostrar_en_mapa_estatico"] == "si"
               and r["grupo_informe"] in {"nucleo_principal", "zona_relevante"}]
        subtitulo = "Núcleo principal y zonas relevantes"
    else:
        sel = [r for r in carto_rows if r["mostrar_en_mapa_estatico"] == "si"]
        subtitulo = "Núcleo, zonas relevantes y candidatos"

    # Barrios a resaltar -> color por grupo (prioridad: el grupo más alto si se repite el barrio).
    barrio_to_group = {}
    for r in sorted(sel, key=lambda r: r["prioridad_visual"], reverse=True):
        bn = norm(primer_barrio(r["barrios_asociados"]))
        barrio_to_group[bn] = r["grupo_informe"]

    fig, ax = plt.subplots(figsize=(11, 12), dpi=170)
    barrios.plot(ax=ax, color="#F2F2F2", edgecolor="#CFCFCF", linewidth=0.6, zorder=1)

    # Resaltar barrios asociados
    for grp in GROUP_ORDER:
        names = [bn for bn, g in barrio_to_group.items() if g == grp]
        if not names:
            continue
        sub = barrios[barrios["_norm"].isin(names)]
        if len(sub):
            sub.plot(ax=ax, color=GROUP_COLORS[grp], edgecolor="white", linewidth=0.7, alpha=0.78, zorder=2)

    # Etiquetas: una por barrio (varios polos pueden compartir barrio -> etiqueta combinada).
    by_barrio: dict[str, list[dict]] = defaultdict(list)
    for r in sorted(sel, key=lambda r: r["prioridad_visual"]):
        by_barrio[norm(primer_barrio(r["barrios_asociados"]))].append(r)

    # Etiqueta legible por barrio compartido (evita superposición de nombres).
    BARRIO_LABEL = {
        norm("Palermo"): "Palermo\n(Soho/Hollywood/Cañitas)",
        norm("Villa Urquiza"): "Villa Urquiza / DoHo",
    }
    for bn, items in by_barrio.items():
        sub = barrios[barrios["_norm"] == bn]
        if not len(sub):
            continue
        c = sub.geometry.representative_point().iloc[0]
        if bn in BARRIO_LABEL:
            label = BARRIO_LABEL[bn]
        elif len(items) == 1:
            label = items[0]["nombre_publico"]
        else:
            label = " / ".join(dict.fromkeys(i["nombre_publico"] for i in items))
        ax.annotate(label, (c.x, c.y), fontsize=7.2, ha="center", va="center",
                    color="#1A1A1A", zorder=5,
                    bbox={"boxstyle": "round,pad=0.18", "facecolor": "white", "alpha": 0.82, "edgecolor": "none"})

    ax.set_axis_off()
    fig.suptitle("Mapa territorial preliminar — PolosGastro", fontsize=16, x=0.5, y=0.965)
    ax.set_title(subtitulo, fontsize=11, color="#444", pad=6)
    fig.text(0.5, 0.085,
             "Mapa territorial preliminar. Barrios/comunas como referencia; no delimita oficialmente polos gastronómicos.",
             ha="center", fontsize=9.5, color="#C44536", weight="bold")
    legend = [Patch(facecolor=GROUP_COLORS[g], edgecolor="white", label=GROUP_LABELS[g])
              for g in GROUP_ORDER if g in barrio_to_group.values()]
    ax.legend(handles=legend, loc="lower left", frameon=False, fontsize=9, title="Grupo (barrio asociado)")
    fig.text(0.01, 0.01,
             f"Base cartográfica: Buenos Aires Data — Barrios CABA (GeoJSON). {FOOTER} "
             "Barrios asociados = referencia territorial, no delimitación del polo.",
             ha="left", va="bottom", fontsize=7, color="#4A4A4A")
    fig.savefig(GRAF / filename, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main() -> None:
    GRAF.mkdir(parents=True, exist_ok=True)
    base_mapa = read_csv(BASE_MAPA)
    barrios = gpd.read_file(BARRIOS_GEOJSON)
    barrios_norm = {norm(x) for x in barrios["nombre"]}

    carto_rows = build_base_carto(base_mapa, barrios_norm)
    write_base_carto(carto_rows)

    chart_universo(base_mapa)
    chart_precision(base_mapa)
    chart_familias(base_mapa)
    concept_map(base_mapa, "mapa_conceptual_polos_gastro_resumido_v2.png", completo=False)
    concept_map(base_mapa, "mapa_conceptual_polos_gastro_completo_v2.png", completo=True)
    static_map(carto_rows, barrios, "mapa_estatico_caba_polos_gastro_v1.png", solo_nucleo=False)
    static_map(carto_rows, barrios, "mapa_estatico_caba_polos_gastro_nucleo_v1.png", solo_nucleo=True)

    n_mostrar = sum(1 for r in carto_rows if r["mostrar_en_mapa_estatico"] == "si")
    print(f"[fase4a] base cartografica visual: {len(carto_rows)} filas ({n_mostrar} en mapa estatico)")
    print(f"[fase4a] PNG generados en: {GRAF}")


if __name__ == "__main__":
    main()
