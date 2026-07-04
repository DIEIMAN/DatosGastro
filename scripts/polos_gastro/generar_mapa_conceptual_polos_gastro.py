from __future__ import annotations

import csv
import textwrap
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


ROOT = Path(__file__).resolve().parents[2]
OUTPUTS = ROOT / "outputs" / "polos_gastro"
DOCS = ROOT / "docs" / "polos_gastro"
GRAFICOS = OUTPUTS / "graficos"
FECHA_CORTE = "2026-06-29"

UNIVERSO_PATH = OUTPUTS / "universo_informe_polos_gastro.csv"
DELIMITACION_PATH = OUTPUTS / "base_delimitacion_preliminar_polos_gastro.csv"
FAMILIAS_PATH = OUTPUTS / "fuentes_por_familia_territorial.csv"
BASE_MAPA_PATH = OUTPUTS / "base_mapa_conceptual_polos_gastro.csv"

AUDITORIA_PATH = DOCS / "AUDITORIA_MAPA_CONCEPTUAL_FASE3B.md"
LECTURA_MAPA_PATH = DOCS / "LECTURA_MAPA_CONCEPTUAL_POLOS_GASTRO.md"
DELIMITACION_DOC_PATH = DOCS / "DELIMITACION_TEXTUAL_PRELIMINAR_POLOS_GASTRO.md"
ESQUELETO_DOC_PATH = DOCS / "ESQUELETO_INFORME_POLOS_GASTRO.md"


BASE_MAPA_COLUMNS = [
    "polo_id",
    "nombre_publico",
    "familia_territorial",
    "grupo_informe",
    "estado_validacion",
    "tipo_area",
    "nivel_precision_delimitacion",
    "representacion_sugerida",
    "barrios_asociados",
    "comunas_probables",
    "delimitacion_textual",
    "fuentes_principales",
    "urls_pendientes",
    "mostrar_en_mapa_conceptual",
    "motivo_visualizacion",
    "riesgo_metodologico",
    "observaciones",
]

GROUP_ORDER = [
    "nucleo_principal",
    "zona_relevante",
    "emergente_o_candidato",
    "anexo",
    "no_incluir_por_ahora",
]

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
PRECISION_LABELS = {
    "alta": "Alta",
    "media": "Media",
    "baja": "Baja",
    "sin_delimitacion": "Sin delimitación",
}
PRECISION_COLORS = {
    "alta": "#275DAD",
    "media": "#2A9D8F",
    "baja": "#E9B44C",
    "sin_delimitacion": "#C44536",
}

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

FAMILY_ORDER = [
    "palermo_y_subpolos",
    "zona_costera_y_turistica",
    "sur_historico_y_tradicional",
    "zona_central",
    "belgrano_y_norte",
    "oeste_y_barrios_con_oferta",
    "corredores_emergentes_norte_oeste",
    "cultura_avenidas_y_noches",
]

REP_LABELS = {
    "punto_conceptual": "Punto conceptual",
    "etiqueta_zona": "Etiqueta de zona",
    "linea_corredor_conceptual": "Línea / corredor conceptual",
    "familia_sin_geometria": "Familia sin geometría",
    "no_mapear": "No mapear",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: list[dict[str, str]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def pending_urls(value: str) -> bool:
    value = (value or "").strip()
    return bool(value and not value.startswith("sin_url"))


def short_join(names: list[str], limit: int = 7) -> str:
    if not names:
        return "sin casos"
    if len(names) <= limit:
        return ", ".join(names)
    return ", ".join(names[:limit]) + f" y {len(names) - limit} más"


def wrap_label(value: str, width: int = 22) -> str:
    return "\n".join(textwrap.wrap(value, width=width, break_long_words=False))


def representation_for(row: dict[str, str]) -> tuple[str, str, str, str]:
    group = row["grupo_informe"]
    precision = row["nivel_precision"]
    tipo = row["tipo_area"]
    urls = row.get("urls_pendientes", "")

    if group == "no_incluir_por_ahora":
        return (
            "no_mapear",
            "no",
            "El caso fue clasificado fuera del universo del informe por ahora.",
            "Riesgo alto de convertir una señal débil en zona validada.",
        )

    if precision == "sin_delimitacion":
        return (
            "no_mapear",
            "no",
            "No tiene delimitación textual suficiente.",
            "No debe representarse como área ni como corredor.",
        )

    if group == "anexo":
        if precision in {"alta", "media"}:
            return (
                "etiqueta_zona",
                "si",
                "Puede figurar como referencia secundaria, sin jerarquía central.",
                "Riesgo de sobredimensionar un caso de anexo.",
            )
        return (
            "familia_sin_geometria",
            "si",
            "Conviene mostrarlo dentro de su familia territorial, sin punto ni área propia.",
            "Riesgo de darle precisión visual a evidencia baja.",
        )

    if group == "nucleo_principal" and precision in {"alta", "media"}:
        return (
            "etiqueta_zona",
            "si",
            "Tiene respaldo documental suficiente para lectura conceptual.",
            "No debe leerse como polígono oficial ni padrón de locales.",
        )

    if group == "zona_relevante":
        if precision in {"alta", "media"}:
            return (
                "etiqueta_zona",
                "si",
                "Puede leerse como zona relevante, con advertencia metodológica.",
                "Riesgo de confundir relevancia documental con delimitación oficial.",
            )
        return (
            "punto_conceptual",
            "si",
            "Puede figurar como punto aproximado para discusión interna.",
            "La precisión baja impide dibujar área o corredor.",
        )

    if group == "emergente_o_candidato":
        if pending_urls(urls):
            return (
                "familia_sin_geometria",
                "si",
                "Tiene URLs pendientes o evidencia insuficiente para ubicarlo como eje.",
                "Riesgo de validar visualmente un candidato incompleto.",
            )
        if tipo in {"corredor", "avenida"} and precision in {"alta", "media"}:
            return (
                "linea_corredor_conceptual",
                "si",
                "La delimitación textual permite mostrar un eje conceptual.",
                "La línea no equivale a traza oficial ni polígono.",
            )
        if precision in {"alta", "media"}:
            return (
                "punto_conceptual",
                "si",
                "Puede aparecer como candidato con ubicación conceptual.",
                "No debe interpretarse como zona validada completa.",
            )
        return (
            "punto_conceptual",
            "si",
            "Puede aparecer como candidato débil solo a nivel orientativo.",
            "La precisión baja impide usar polígonos o límites cerrados.",
        )

    return (
        "familia_sin_geometria",
        "si",
        "Representación conservadora por familia territorial.",
        "Requiere validación antes de cualquier mapa final.",
    )


def build_base_mapa(
    universo: list[dict[str, str]], delimitacion: list[dict[str, str]]
) -> list[dict[str, str]]:
    universo_by_id = {row["polo_id"]: row for row in universo}
    rows: list[dict[str, str]] = []

    for delim in delimitacion:
        uni = universo_by_id[delim["polo_id"]]
        rep, show, reason, visual_risk = representation_for({**uni, **delim})
        riesgo = uni.get("riesgo_metodologico", "").strip()
        if visual_risk and visual_risk not in riesgo:
            riesgo = f"{riesgo} {visual_risk}".strip()
        rows.append(
            {
                "polo_id": delim["polo_id"],
                "nombre_publico": delim["nombre_publico"],
                "familia_territorial": delim["familia_territorial"],
                "grupo_informe": uni["grupo_informe"],
                "estado_validacion": uni["estado_validacion"],
                "tipo_area": delim["tipo_area"],
                "nivel_precision_delimitacion": delim["nivel_precision"],
                "representacion_sugerida": rep,
                "barrios_asociados": delim["barrios_asociados"],
                "comunas_probables": delim["comunas_probables"],
                "delimitacion_textual": delim["delimitacion_textual"],
                "fuentes_principales": uni["fuentes_principales"],
                "urls_pendientes": uni["urls_pendientes"],
                "mostrar_en_mapa_conceptual": show,
                "motivo_visualizacion": reason,
                "riesgo_metodologico": riesgo,
                "observaciones": delim["observaciones"],
            }
        )
    return rows


def add_footer(fig: plt.Figure, note: str) -> None:
    fig.text(
        0.02,
        0.02,
        f"Base: 32 polos. Fuente: insumos PolosGastro. Fecha de corte: {FECHA_CORTE}. {note}",
        ha="left",
        va="bottom",
        fontsize=8,
        color="#4A4A4A",
    )


def save_group_chart(rows: list[dict[str, str]]) -> Path:
    counts = Counter(row["grupo_informe"] for row in rows)
    labels = [GROUP_LABELS[group] for group in GROUP_ORDER]
    values = [counts[group] for group in GROUP_ORDER]
    colors = [GROUP_COLORS[group] for group in GROUP_ORDER]

    fig, ax = plt.subplots(figsize=(10, 6), dpi=180)
    bars = ax.barh(labels, values, color=colors)
    ax.invert_yaxis()
    ax.set_title("Universo PolosGastro por grupo de informe", fontsize=15, loc="left", pad=16)
    ax.set_xlabel("Cantidad de polos")
    ax.set_xlim(0, max(values) + 2)
    ax.grid(axis="x", color="#D9D9D9", linewidth=0.7)
    ax.set_axisbelow(True)
    for bar, value in zip(bars, values):
        ax.text(value + 0.12, bar.get_y() + bar.get_height() / 2, str(value), va="center", fontsize=10)
    ax.spines[["top", "right", "left"]].set_visible(False)
    add_footer(fig, "El gráfico muestra jerarquía metodológica, no intensidad gastronómica.")
    fig.tight_layout(rect=(0, 0.06, 1, 0.95))

    path = GRAFICOS / "universo_polos_por_grupo.png"
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def save_precision_chart(rows: list[dict[str, str]]) -> Path:
    counts = Counter(row["nivel_precision_delimitacion"] for row in rows)
    labels = [PRECISION_LABELS[item] for item in PRECISION_ORDER]
    values = [counts[item] for item in PRECISION_ORDER]
    colors = [PRECISION_COLORS[item] for item in PRECISION_ORDER]

    fig, ax = plt.subplots(figsize=(9, 6), dpi=180)
    bars = ax.bar(labels, values, color=colors)
    ax.set_title("Precisión de delimitación territorial", fontsize=15, loc="left", pad=16)
    ax.set_ylabel("Cantidad de polos")
    ax.set_ylim(0, max(values) + 3)
    ax.grid(axis="y", color="#D9D9D9", linewidth=0.7)
    ax.set_axisbelow(True)
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 0.2, str(value), ha="center", fontsize=10)
    ax.spines[["top", "right"]].set_visible(False)
    add_footer(fig, "La baja precisión y los casos sin delimitación impiden polígonos cerrados.")
    fig.tight_layout(rect=(0, 0.06, 1, 0.95))

    path = GRAFICOS / "precision_delimitacion_polos.png"
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def save_family_chart(rows: list[dict[str, str]]) -> Path:
    counts: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        counts[row["familia_territorial"]][row["grupo_informe"]] += 1

    families = [family for family in FAMILY_ORDER if family in counts]
    labels = [wrap_label(FAMILY_LABELS.get(family, family), 28) for family in families]
    y_positions = list(range(len(families)))

    fig, ax = plt.subplots(figsize=(13, 7.2), dpi=180)
    left = [0] * len(families)
    for group in GROUP_ORDER:
        values = [counts[family][group] for family in families]
        ax.barh(
            y_positions,
            values,
            left=left,
            label=GROUP_LABELS[group],
            color=GROUP_COLORS[group],
        )
        left = [base + value for base, value in zip(left, values)]

    ax.set_yticks(y_positions, labels)
    ax.invert_yaxis()
    ax.set_xlabel("Cantidad de polos")
    ax.set_title("Familias territoriales por grupo de informe", fontsize=15, loc="left", pad=16)
    ax.grid(axis="x", color="#D9D9D9", linewidth=0.7)
    ax.set_axisbelow(True)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.22), ncol=3, frameon=False, fontsize=9)

    for y, total in zip(y_positions, left):
        ax.text(total + 0.08, y, str(total), va="center", fontsize=9)

    add_footer(fig, "Las familias organizan lectura territorial; no equivalen a polígonos.")
    fig.tight_layout(rect=(0, 0.12, 1, 0.95))

    path = GRAFICOS / "familias_territoriales_polos.png"
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def marker_for_rep(rep: str) -> str:
    return {
        "punto_conceptual": "o",
        "etiqueta_zona": "s",
        "linea_corredor_conceptual": "D",
        "familia_sin_geometria": "^",
        "no_mapear": "x",
    }.get(rep, "o")


def save_concept_map(rows: list[dict[str, str]], filename: str, complete: bool) -> Path:
    visible = [row for row in rows if row["mostrar_en_mapa_conceptual"] == "si"]
    not_mapped = [row for row in rows if row["mostrar_en_mapa_conceptual"] != "si"]

    if not complete:
        # Resumido: solo casos de mayor jerarquía o mejor legibilidad.
        visible = [
            row
            for row in visible
            if row["grupo_informe"] in {"nucleo_principal", "zona_relevante"}
            or row["representacion_sugerida"] == "linea_corredor_conceptual"
        ]

    family_to_y = {family: idx * 1.08 for idx, family in enumerate(reversed(FAMILY_ORDER))}
    group_to_x = {group: idx * 1.85 for idx, group in enumerate(GROUP_ORDER[:-1])}
    cell_offsets = [
        (0.0, 0.0),
        (0.0, 0.26),
        (0.0, -0.26),
        (0.34, 0.13),
        (0.34, -0.13),
        (-0.34, 0.13),
        (-0.34, -0.13),
    ]

    fig, ax = plt.subplots(figsize=(18, 11 if complete else 8.6), dpi=180)
    ax.set_facecolor("#FAFAFA")
    fig.suptitle(
        "Mapa conceptual preliminar PolosGastro" + (" - completo" if complete else " - resumido"),
        fontsize=16,
        x=0.06,
        y=0.985,
        ha="left",
    )
    fig.text(
        0.06,
        0.952,
        "Mapa conceptual preliminar. No representa delimitaciones oficiales ni polígonos definitivos.",
        fontsize=10,
        color="#C44536",
        weight="bold",
        ha="left",
    )

    for family, y in family_to_y.items():
        if family not in {row["familia_territorial"] for row in rows}:
            continue
        ax.axhline(y=y, color="#E6E6E6", linewidth=0.8, zorder=0)
        ax.text(
            -0.68,
            y,
            wrap_label(FAMILY_LABELS.get(family, family), 24),
            ha="right",
            va="center",
            fontsize=9,
            color="#333333",
        )

    offsets_by_cell: dict[tuple[str, str], int] = defaultdict(int)
    for row in visible:
        family = row["familia_territorial"]
        group = row["grupo_informe"]
        if family not in family_to_y or group not in group_to_x:
            continue
        key = (family, group)
        offset_i = offsets_by_cell[key]
        offsets_by_cell[key] += 1

        dx, dy = cell_offsets[offset_i % len(cell_offsets)]
        x = group_to_x[group] + dx
        y = family_to_y[family] + dy
        color = GROUP_COLORS[group]
        rep = row["representacion_sugerida"]

        if rep == "linea_corredor_conceptual":
            ax.plot([x - 0.13, x + 0.13], [y, y], color=color, linewidth=3.2, solid_capstyle="round", zorder=3)
            ax.scatter([x], [y], marker=marker_for_rep(rep), s=72, color=color, edgecolor="white", linewidth=1, zorder=4)
        else:
            ax.scatter(
                [x],
                [y],
                marker=marker_for_rep(rep),
                s=92 if rep != "familia_sin_geometria" else 72,
                color=color,
                edgecolor="white",
                linewidth=1,
                zorder=4,
            )

        label = row["nombre_publico"]
        ax.text(
            x + 0.08,
            y,
            wrap_label(label, 18 if complete else 20),
            fontsize=7.1 if complete else 8.2,
            va="center",
            ha="left",
            color="#222222",
            zorder=5,
        )

    ax.set_xticks([group_to_x[group] for group in GROUP_ORDER[:-1]], [GROUP_LABELS[group] for group in GROUP_ORDER[:-1]])
    ax.tick_params(axis="x", labelsize=9)
    ax.set_yticks([])
    ax.set_xlim(-1.05, 6.95)
    ax.set_ylim(-0.9, max(family_to_y.values()) + 0.85)
    ax.spines[:].set_visible(False)

    group_handles = [
        Line2D([0], [0], marker="o", color="w", label=GROUP_LABELS[group], markerfacecolor=GROUP_COLORS[group], markersize=9)
        for group in GROUP_ORDER[:-1]
    ]
    rep_handles = [
        Line2D([0], [0], marker=marker_for_rep(rep), color="w", label=REP_LABELS[rep], markerfacecolor="#555555", markersize=8)
        for rep in ["punto_conceptual", "etiqueta_zona", "linea_corredor_conceptual", "familia_sin_geometria"]
    ]
    first_legend = ax.legend(handles=group_handles, loc="upper left", bbox_to_anchor=(0.0, -0.08), ncol=4, frameon=False, fontsize=8)
    ax.add_artist(first_legend)
    ax.legend(handles=rep_handles, loc="upper right", bbox_to_anchor=(1.0, -0.08), ncol=2, frameon=False, fontsize=8)

    no_map_text = short_join([row["nombre_publico"] for row in not_mapped], limit=6)
    ax.text(
        0.99,
        0.02,
        "No mapeados en esta fase:\n" + wrap_label(no_map_text, 48),
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=8,
        color="#4A4A4A",
        bbox={"boxstyle": "round,pad=0.35", "facecolor": "white", "edgecolor": "#D0D0D0"},
    )

    add_footer(fig, "Diagrama territorial esquemático, sin geocodificación ni base cartográfica.")
    fig.tight_layout(rect=(0.02, 0.12, 1, 0.91))

    path = GRAFICOS / filename
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def replace_section(path: Path, start: str, end: str, section_text: str) -> None:
    original = path.read_text(encoding="utf-8")
    block = f"{start}\n{section_text.rstrip()}\n{end}"
    if start in original and end in original:
        before = original.split(start, 1)[0].rstrip()
        after = original.split(end, 1)[1].lstrip()
        updated = f"{before}\n\n{block}\n\n{after}".rstrip() + "\n"
    else:
        updated = original.rstrip() + "\n\n" + block + "\n"
    path.write_text(updated, encoding="utf-8")


def names_by(rows: list[dict[str, str]], predicate) -> list[str]:
    return [row["nombre_publico"] for row in rows if predicate(row)]


def family_support_summary(rows: list[dict[str, str]]) -> tuple[list[str], list[str]]:
    support: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        family = row["familia_territorial"]
        if row["nivel_precision_delimitacion"] in {"alta", "media"}:
            support[family]["fuerte"] += 1
        if row["grupo_informe"] in {"nucleo_principal", "zona_relevante"}:
            support[family]["central"] += 1
        if row["representacion_sugerida"] in {"no_mapear", "familia_sin_geometria"}:
            support[family]["debil"] += 1

    better = []
    weaker = []
    for family in FAMILY_ORDER:
        score = support[family]["fuerte"] + support[family]["central"] - support[family]["debil"]
        label = FAMILY_LABELS.get(family, family)
        if score >= 2:
            better.append(label)
        else:
            weaker.append(label)
    return better, weaker


def write_audit(rows: list[dict[str, str]]) -> None:
    safe = names_by(
        rows,
        lambda row: row["mostrar_en_mapa_conceptual"] == "si"
        and row["nivel_precision_delimitacion"] in {"alta", "media"}
        and row["representacion_sugerida"] != "familia_sin_geometria",
    )
    approximate = names_by(
        rows,
        lambda row: row["mostrar_en_mapa_conceptual"] == "si"
        and (
            row["nivel_precision_delimitacion"] == "baja"
            or row["representacion_sugerida"] == "familia_sin_geometria"
        ),
    )
    not_mapped = names_by(rows, lambda row: row["mostrar_en_mapa_conceptual"] != "si")
    better, weaker = family_support_summary(rows)

    content = f"""# Auditoría para mapa conceptual - Fase 3B

Fecha de corte documental: {FECHA_CORTE}.

Esta auditoría revisa los insumos locales ya generados para PolosGastro y define un criterio visual prudente. No se usó geocodificación, no se descargó geodata y no se modificaron fuentes.

## Insumos revisados

- `outputs/polos_gastro/universo_informe_polos_gastro.csv`
- `outputs/polos_gastro/base_delimitacion_preliminar_polos_gastro.csv`
- `outputs/polos_gastro/fuentes_por_familia_territorial.csv`

## Polos que pueden mapearse con seguridad conceptual

Pueden aparecer como etiquetas, puntos conceptuales o líneas conceptuales, siempre con nota metodológica visible:

{bullet_list(safe)}

## Polos que solo pueden aparecer como etiqueta, punto aproximado o familia sin geometría

Estos casos pueden ayudar a pensar el informe, pero no deben leerse como zonas cerradas ni como delimitaciones institucionales:

{bullet_list(approximate)}

## Polos que no deberían mapearse todavía

Estos casos quedan fuera del mapa conceptual principal por estar en `no_incluir_por_ahora` o por no tener delimitación suficiente:

{bullet_list(not_mapped)}

## Familias mejor respaldadas

{bullet_list(better)}

## Familias débiles o mixtas

{bullet_list(weaker)}

## Riesgos visuales

- Confundir un diagrama conceptual con un mapa oficial.
- Convertir barrios amplios en polígonos cerrados sin fuente territorial.
- Dar la misma jerarquía visual a núcleos consolidados, candidatos y anexos.
- Representar casos de baja precisión como áreas completas.
- Leer familias territoriales como límites administrativos.
- Interpretar fuentes documentales como padrón de locales activos.

## Criterio de cierre de esta fase

La Fase 3B habilita gráficos de apoyo y un diagrama territorial esquemático. No habilita mapa institucional final, geocodificación de locales, shapefiles, geojson definitivos ni polígonos cerrados.
"""
    AUDITORIA_PATH.write_text(content, encoding="utf-8")


def bullet_list(items: list[str]) -> str:
    if not items:
        return "- Sin casos."
    return "\n".join(f"- {item}" for item in items)


def write_visual_reading(rows: list[dict[str, str]]) -> None:
    main = names_by(rows, lambda row: row["grupo_informe"] == "nucleo_principal")
    relevant = names_by(rows, lambda row: row["grupo_informe"] == "zona_relevante")
    candidates = names_by(rows, lambda row: row["grupo_informe"] == "emergente_o_candidato")
    not_mapped = names_by(rows, lambda row: row["mostrar_en_mapa_conceptual"] != "si")
    corridors = names_by(rows, lambda row: row["representacion_sugerida"] == "linea_corredor_conceptual")

    content = f"""# Lectura del mapa conceptual PolosGastro

Fecha de corte documental: {FECHA_CORTE}.

## 1. Qué muestra el mapa conceptual

El mapa conceptual muestra cómo ordenar el universo PolosGastro por familias territoriales y niveles de evidencia. Sirve para pensar la estructura visual de un informe futuro y para diferenciar casos consolidados, zonas relevantes, candidatos y anexos.

## 2. Qué no muestra

No muestra polígonos oficiales, límites administrativos, locales activos, concentración real de oferta ni trazas cartográficas definitivas. Tampoco reemplaza una validación geográfica posterior.

## 3. Cómo leer los grupos

- Núcleo principal: casos con mayor respaldo documental y mejor utilidad para el cuerpo del informe.
- Zona relevante: casos que ayudan a explicar el territorio, pero requieren prudencia visual.
- Emergente/candidato: señales documentales o territoriales que todavía no alcanzan nivel de núcleo.
- Anexo: casos útiles para contexto, no para eje central.
- No incluir por ahora: casos que no deben formar parte del mapa principal.

## 4. Cómo leer las familias territoriales

Las familias agrupan zonas relacionadas para ordenar la conversación. No son polígonos ni unidades oficiales. Palermo, zona costera, zona central, norte, oeste, sur histórico y corredores emergentes se usan como familias de lectura.

## 5. Por qué no se usan polígonos cerrados

La base tiene 3 delimitaciones de precisión alta, 11 de precisión media, 16 de precisión baja y 2 sin delimitación. Esa combinación no permite dibujar áreas cerradas para todo el universo sin generar una precisión falsa.

## 6. Polos que aparecen como núcleo principal

{bullet_list(main)}

## 7. Zonas que quedan como relevantes

{bullet_list(relevant)}

## 8. Corredores o ejes que aparecen como candidatos

{bullet_list(corridors if corridors else candidates)}

## 9. Casos que no deberían mapearse todavía

{bullet_list(not_mapped)}

Paternal se mantiene como candidato, pero sin geometría individual fuerte: puede aparecer solo como referencia dentro de familia territorial hasta resolver la fuente específica pendiente.

## 10. Qué falta para un mapa institucional final

- Validar delimitaciones con criterio cartográfico explícito.
- Resolver URLs pendientes críticas.
- Definir si el producto final usará puntos, líneas, áreas o una combinación.
- Incorporar una base cartográfica validada de CABA solo cuando se autorice trabajar esa capa.
- Documentar fuente, fecha, método y limitaciones de cada geometría.
"""
    LECTURA_MAPA_PATH.write_text(content, encoding="utf-8")


def update_existing_docs(rows: list[dict[str, str]], chart_paths: dict[str, Path]) -> None:
    no_map = names_by(rows, lambda row: row["mostrar_en_mapa_conceptual"] != "si")
    visual_section = f"""## Lectura visual preliminar

En Fase 3B se generaron visualizaciones conceptuales para ordenar el universo PolosGastro antes de un informe final:

- `outputs/polos_gastro/graficos/universo_polos_por_grupo.png`
- `outputs/polos_gastro/graficos/precision_delimitacion_polos.png`
- `outputs/polos_gastro/graficos/familias_territoriales_polos.png`
- `outputs/polos_gastro/graficos/mapa_conceptual_polos_gastro.png`
- `outputs/polos_gastro/graficos/mapa_conceptual_polos_gastro_completo.png`

Son visualizaciones conceptuales porque no usan geocodificación, no incorporan una base cartográfica definitiva y no convierten delimitaciones textuales en polígonos. Sirven para lectura interna, priorización y diseño del informe futuro.

Riesgos de interpretación:

- Leer el diagrama como mapa oficial.
- Convertir candidatos en zonas validadas.
- Interpretar familias como límites administrativos.
- Usar casos de baja precisión como áreas cerradas.
- Confundir fuentes documentales con padrón de locales activos.

Casos no mapeados en el mapa conceptual principal: {", ".join(no_map)}.

Próximos pasos para un mapa final: cerrar fuentes pendientes, validar geometrías con un criterio cartográfico documentado, decidir simbología institucional y separar puntos, líneas y áreas según nivel de evidencia."""

    replace_section(
        DELIMITACION_DOC_PATH,
        "<!-- FASE3B_LECTURA_VISUAL_START -->",
        "<!-- FASE3B_LECTURA_VISUAL_END -->",
        visual_section,
    )

    report_section = f"""## Visuales disponibles para informe futuro

La Fase 3B deja disponibles visuales de apoyo para un informe posterior:

- Universo por grupo: muestra que el universo no entra todo con la misma jerarquía.
- Precisión de delimitación: explica por qué no corresponde hacer polígonos cerrados para todo.
- Familias territoriales: ordena los polos por familias y grupo de informe.
- Mapa conceptual preliminar: diagrama territorial esquemático, no cartográfico.
- Mapa conceptual completo: versión de trabajo con más casos visibles para revisión interna.

Estos visuales no son mapas finales. No geocodifican locales, no usan polígonos definitivos, no generan shapefiles/geojson y no deben publicarse como delimitación oficial."""

    replace_section(
        ESQUELETO_DOC_PATH,
        "<!-- FASE3B_VISUALES_DISPONIBLES_START -->",
        "<!-- FASE3B_VISUALES_DISPONIBLES_END -->",
        report_section,
    )


def main() -> None:
    GRAFICOS.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    universo = read_csv(UNIVERSO_PATH)
    delimitacion = read_csv(DELIMITACION_PATH)
    read_csv(FAMILIAS_PATH)  # Explicit input audit; family ids are also present in delimitacion.

    base_rows = build_base_mapa(universo, delimitacion)
    write_csv(BASE_MAPA_PATH, base_rows, BASE_MAPA_COLUMNS)

    chart_paths = {
        "universo": save_group_chart(base_rows),
        "precision": save_precision_chart(base_rows),
        "familias": save_family_chart(base_rows),
        "mapa_resumido_alias": save_concept_map(base_rows, "mapa_conceptual_polos_gastro.png", complete=False),
        "mapa_resumido": save_concept_map(base_rows, "mapa_conceptual_polos_gastro_resumido.png", complete=False),
        "mapa_completo": save_concept_map(base_rows, "mapa_conceptual_polos_gastro_completo.png", complete=True),
    }

    write_audit(base_rows)
    write_visual_reading(base_rows)
    update_existing_docs(base_rows, chart_paths)


if __name__ == "__main__":
    main()
