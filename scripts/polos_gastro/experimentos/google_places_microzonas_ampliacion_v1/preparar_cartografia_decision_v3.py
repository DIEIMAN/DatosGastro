from __future__ import annotations

import json
import re
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image


ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "outputs/polos_gastro/historico/experimentos/google_places_microzonas_ampliacion_v1"
SOURCE = BASE / "cartografia_editorial_v2"
OUT = BASE / "cartografia_decision_v3"

POLYGONS = SOURCE / "poligonos_editoriales_simplificados_v0.geojson"
POINTS = SOURCE / "puntos_evidencia_microzonas_v0.geojson"
GROUPING = SOURCE / "tabla_agrupamiento_editorial_v0.csv"
SUMMARY_V2 = SOURCE / "RESUMEN_CARTOGRAFIA_EDITORIAL_V2.md"
HANDOFF_V2 = SOURCE / "HANDOFF_CARTOGRAFIA_EDITORIAL_V2.md"

CALLEJERO = ROOT / "outputs/polos_gastro/fase15_mapas_callejeros_v3/assets/callejero_gcba_2026_06_02.geojson"
BARRIOS = ROOT / "PolosGastro/cartografia/barrios_caba.geojson"
COMUNAS = ROOT / "PolosGastro/cartografia/comunas_caba.geojson"

CRS_METERS = "EPSG:5347"

FAMILY_COLORS = {
    "MAPA_EJECUTIVO_CANDIDATO": "#2f7f67",
    "REQUIERE_REDIBUJO": "#c46a21",
    "ANEXO_EXPLORATORIO": "#7b8491",
    "EXCLUIR": "#d9d9d9",
}

MAP_FILES = [
    "mapa_ejecutivo_candidato_v3.png",
    "mapa_decision_general_v3.png",
    "mapa_redibujo_corrientes_microcentro_v3.png",
    "mapa_redibujo_belgrano_v3.png",
    "mapa_redibujo_caballito_v3.png",
    "mapa_anexo_exploratorio_v3.png",
]


EXECUTIVE_GROUPS = {
    "PALERMO_HOLLYWOOD_FITZ_ROY",
    "PALERMO_HOLLYWOOD_ESTE",
    "PALERMO_HOLLYWOOD_NORTE",
    "PALERMO_HONDURAS_ARMENIA",
    "PALERMO_SOHO_ESTE",
    "PALERMO_PLAZA_SERRANO_ARMENIA",
    "SAN_TELMO_DEFENSA_DORREGO",
    "SAN_TELMO_MERCADO_NORTE",
    "SAN_TELMO_SUR",
    "RECOLETA_CENTRO",
    "RECOLETA_ESTE_CULTURAL",
    "RECOLETA_OESTE_ALTO_PALERMO",
    "CHACARITA_CENTRO",
    "CHACARITA_NORTE",
    "CHACARITA_SUR",
    "VILLA_CRESPO_ESTE_PALERMO_LIMITE",
    "VILLA_CRESPO_OESTE_CORRIENTES",
    "BELGRANO_BARRIO_CHINO_BARRANCAS",
    "PUERTO_MADERO_CENTRO_FRENTES",
}

REDRAW_GROUPS = {
    "CORRIENTES_TRIBUNALES_OBELISCO",
    "CORRIENTES_CENTRO_TEATRAL",
    "CORRIENTES_ESTE_CENTRO",
    "CORRIENTES_OESTE_ABASTO_ONCE",
    "CENTRO_TRIBUNALES_ADMINISTRATIVO",
    "FLORIDA_LAVALLE_MICROCENTRO",
    "MICROCENTRO_LABORAL_ADMINISTRATIVO",
    "BELGRANO_BAJO",
    "BELGRANO_NORTE_OESTE",
    "BELGRANO_CABILDO_JURAMENTO",
    "CABALLITO_ACOYTE_CENTRO",
    "CABALLITO_AVELLANEDA_COMERCIAL",
    "CABALLITO_PEDRO_GOYENA",
    "CABALLITO_PRIMERA_JUNTA_RIVADAVIA",
    "PUERTO_MADERO_NORTE_FRENTE_OESTE",
    "PUERTO_MADERO_SUR_DIQUES",
    "VILLA_CRESPO_CENTRO_SCALABRINI",
}

ANNEX_GROUPS = {
    "COSTANERA_NORTE_SENAL_EXPLORATORIA",
    "AV_CASEROS_BARRACAS_SENAL_EXPLORATORIA",
    "CASEROS_BARRACAS_NUCLEO_DEFENDIBLE",
    "PUERTO_MADERO_SENAL_EXPLORATORIA",
    "CABALLITO_SENAL_EXPLORATORIA",
}


def clean_name(value: str) -> str:
    return (
        str(value)
        .replace("senal", "señal")
        .replace("nucleo", "núcleo")
        .replace("limite", "límite")
        .replace("gastronomicos", "gastronómicos")
    )


def priority_for(row: pd.Series, family: str) -> str:
    if family == "REQUIERE_REDIBUJO":
        if row["grupo_editorial_v0"] in {
            "CORRIENTES_TRIBUNALES_OBELISCO",
            "CORRIENTES_CENTRO_TEATRAL",
            "CORRIENTES_ESTE_CENTRO",
            "CORRIENTES_OESTE_ABASTO_ONCE",
            "FLORIDA_LAVALLE_MICROCENTRO",
            "BELGRANO_NORTE_OESTE",
            "BELGRANO_CABILDO_JURAMENTO",
            "CABALLITO_ACOYTE_CENTRO",
            "CABALLITO_PRIMERA_JUNTA_RIVADAVIA",
        }:
            return "ALTA"
        return "MEDIA"
    if family == "ANEXO_EXPLORATORIO":
        return "BAJA"
    return "BAJA"


def classify(row: pd.Series) -> dict[str, str]:
    group = row["grupo_editorial_v0"]
    name = clean_name(row["nombre_orientativo"])
    pct_places = float(row.get("porcentaje_places", 0) or 0)
    action_v2 = row["accion_v2"]

    if group in ANNEX_GROUPS or action_v2 == "DEJAR_COMO_SENAL_EXPLORATORIA":
        family = "ANEXO_EXPLORATORIO"
        decision = "PASAR_A_ANEXO"
        reason = "Se conserva como señal exploratoria o zona débil; no debe entrar al mapa principal."
        show_points = "SI"
        show_general = "NO"
    elif group in REDRAW_GROUPS:
        family = "REQUIERE_REDIBUJO"
        if "CORRIENTES" in group or "MICROCENTRO" in group or "CENTRO_" in group:
            decision = "REDIBUJAR_SOBRE_CALLES"
            reason = "Tiene buena señal territorial, pero la geometría v2 todavía expresa cortes algorítmicos."
        elif group in {"PUERTO_MADERO_NORTE_FRENTE_OESTE", "PUERTO_MADERO_SUR_DIQUES"}:
            decision = "FUSIONAR_ANTES_DE_MOSTRAR"
            reason = "Puede sostenerse como frente, pero requiere simplificación editorial antes de mostrar."
        else:
            decision = "REDIBUJAR_SOBRE_CALLES"
            reason = "El grupo requiere redibujo para dejar de verse como mancha o corte artificial."
        show_points = "SI"
        show_general = "SI_COMO_REDIBUJO"
    elif group in EXECUTIVE_GROUPS:
        family = "MAPA_EJECUTIVO_CANDIDATO"
        if pct_places >= 65:
            decision = "USAR_SOLO_CON_NOTA"
            reason = "La pieza es legible, pero depende en forma alta de señal Places; conviene mostrarla con nota metodológica."
        else:
            decision = "USAR_COMO_REFERENCIA"
            reason = "La pieza es legible y puede alimentar un mapa limpio, con aclaración experimental."
        show_points = "NO"
        show_general = "SI"
    else:
        family = "EXCLUIR"
        decision = "EXCLUIR_DEL_MAPA"
        reason = "No fue priorizada para mapa principal, redibujo o anexo en esta tanda."
        show_points = "NO"
        show_general = "NO"

    return {
        "familia_v3": family,
        "decision_visual": decision,
        "nombre_mapa_v3": name,
        "prioridad_redibujo": priority_for(row, family),
        "motivo_decision": reason,
        "mostrar_puntos": show_points,
        "mostrar_en_mapa_general": show_general,
        "observaciones": "Experimental / no oficial. No usar como límite institucional final.",
    }


def require_inputs() -> None:
    missing = [p for p in [POLYGONS, POINTS, GROUPING, SUMMARY_V2, HANDOFF_V2] if not p.exists()]
    if missing:
        raise FileNotFoundError("Faltan insumos: " + ", ".join(str(p) for p in missing))
    if OUT.exists():
        raise FileExistsError(f"La carpeta de salida ya existe: {OUT}")
    OUT.mkdir(parents=True, exist_ok=False)


def load_layers() -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    groups = gpd.read_file(POLYGONS)
    points = gpd.read_file(POINTS)
    if len(groups) != 41:
        raise ValueError(f"Se esperaban 41 grupos v2, se leyeron {len(groups)}")
    return groups, points


def build_decision_table(groups: gpd.GeoDataFrame) -> pd.DataFrame:
    records = []
    for _, row in groups.iterrows():
        decision = classify(row)
        records.append(
            {
                "grupo_editorial_v0": row["grupo_editorial_v0"],
                "nombre_orientativo_v2": row["nombre_orientativo"],
                "macrozona": row["macrozona"],
                "entidades_total": row["entidades_total"],
                "cantidad_f01_f02": row["cantidad_f01_f02"],
                "cantidad_places": row["cantidad_places"],
                "porcentaje_places": row["porcentaje_places"],
                "accion_v2": row["accion_v2"],
                **decision,
            }
        )
    table = pd.DataFrame(records)
    known = set(table["grupo_editorial_v0"])
    missing = (EXECUTIVE_GROUPS | REDRAW_GROUPS | ANNEX_GROUPS) - known
    if missing:
        raise ValueError("Hay grupos clasificados que no existen en v2: " + ", ".join(sorted(missing)))
    return table


def write_layers(groups: gpd.GeoDataFrame, table: pd.DataFrame) -> gpd.GeoDataFrame:
    all_groups = groups.merge(table, on="grupo_editorial_v0", how="left", validate="one_to_one", suffixes=("", "_tabla"))
    all_groups.to_file(OUT / "zonas_todas_decision_v3.geojson", driver="GeoJSON")
    mapping = {
        "MAPA_EJECUTIVO_CANDIDATO": "zonas_ejecutivas_candidatas_v3.geojson",
        "REQUIERE_REDIBUJO": "zonas_requieren_redibujo_v3.geojson",
        "ANEXO_EXPLORATORIO": "zonas_anexo_exploratorio_v3.geojson",
        "EXCLUIR": "zonas_excluidas_v3.geojson",
    }
    for family, filename in mapping.items():
        subset = all_groups[all_groups["familia_v3"] == family].copy()
        subset.to_file(OUT / filename, driver="GeoJSON")
    return all_groups


def load_reference_layers():
    barrios = gpd.read_file(BARRIOS) if BARRIOS.exists() else None
    comunas = gpd.read_file(COMUNAS) if COMUNAS.exists() else None
    streets = None
    if CALLEJERO.exists():
        streets = gpd.read_file(CALLEJERO)
        streets["tipo_c_norm"] = streets["tipo_c"].astype(str).str.upper()
        streets["red_norm"] = streets["red_jerarq"].astype(str).str.upper()
        keep = streets["tipo_c_norm"].isin(["AVENIDA", "BOULEVARD", "AUTOPISTA", "CALLE PEATONAL"])
        keep = keep | streets["red_norm"].str.contains("TRONCAL|PRINCIPAL", na=False)
        streets = streets[keep].copy()
    return barrios, comunas, streets


def bbox_filter(gdf: gpd.GeoDataFrame | None, bounds, pad: float):
    if gdf is None or gdf.empty:
        return None
    minx, miny, maxx, maxy = bounds
    return gdf.cx[minx - pad : maxx + pad, miny - pad : maxy + pad].copy()


def annotate(ax, gdf: gpd.GeoDataFrame, label_col: str, size: float = 8.5) -> None:
    label_g = gdf.to_crs(CRS_METERS)
    reps = label_g.representative_point().to_crs("EPSG:4326")
    for (_, row), pt in zip(gdf.iterrows(), reps):
        ax.text(
            pt.x,
            pt.y,
            clean_name(row[label_col]),
            ha="center",
            va="center",
            fontsize=size,
            weight="bold",
            color="#16202a",
            bbox={"facecolor": "#fffdf7", "edgecolor": "#9c9387", "linewidth": 0.35, "alpha": 0.9, "boxstyle": "round,pad=0.22"},
            zorder=9,
        )


def setup_base(ax, selected: gpd.GeoDataFrame, barrios, comunas, streets, street_alpha=0.45, street_width=0.35):
    bounds = selected.total_bounds
    barrios_sub = bbox_filter(barrios, bounds, 0.01)
    comunas_sub = bbox_filter(comunas, bounds, 0.01)
    streets_sub = bbox_filter(streets, bounds, 0.01)
    if barrios_sub is not None and not barrios_sub.empty:
        barrios_sub.boundary.plot(ax=ax, color="#ddd7ce", linewidth=0.45, alpha=0.7, zorder=1)
    if comunas_sub is not None and not comunas_sub.empty:
        comunas_sub.boundary.plot(ax=ax, color="#c4bbae", linewidth=0.75, alpha=0.6, zorder=2)
    if streets_sub is not None and not streets_sub.empty:
        streets_sub.plot(ax=ax, color="#b6afa5", linewidth=street_width, alpha=street_alpha, zorder=3)
    minx, miny, maxx, maxy = bounds
    dx = max((maxx - minx) * 0.12, 0.004)
    dy = max((maxy - miny) * 0.12, 0.004)
    ax.set_xlim(minx - dx, maxx + dx)
    ax.set_ylim(miny - dy, maxy + dy)
    ax.set_axis_off()


def save_fig(fig, path: Path) -> None:
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def plot_executive(all_groups, points, refs) -> Path:
    barrios, comunas, streets = refs
    selected = all_groups[all_groups["familia_v3"] == "MAPA_EJECUTIVO_CANDIDATO"].copy()
    fig, ax = plt.subplots(figsize=(13, 9), dpi=220)
    fig.patch.set_facecolor("#faf8f2")
    ax.set_facecolor("#faf8f2")
    setup_base(ax, selected, barrios, comunas, streets, street_alpha=0.28, street_width=0.25)
    selected.plot(ax=ax, facecolor="#66a88f", edgecolor="#1e4f42", linewidth=1.05, alpha=0.42, zorder=5)
    selected.boundary.plot(ax=ax, color="#1e4f42", linewidth=0.95, alpha=0.85, zorder=6)
    annotate(ax, selected, "nombre_mapa_v3", size=7.4)
    ax.set_title("Microzonas gastronómicas - selección candidata para revisión", loc="left", fontsize=15, weight="bold", color="#16202a")
    ax.text(0.01, 0.015, "Experimental / no oficial. Selección visual simplificada; no es delimitación final.", transform=ax.transAxes, fontsize=7.5, color="#57606a")
    out = OUT / "mapa_ejecutivo_candidato_v3.png"
    save_fig(fig, out)
    return out


def plot_decision_general(all_groups, points, refs) -> Path:
    barrios, comunas, streets = refs
    selected = all_groups[all_groups["familia_v3"] != "EXCLUIR"].copy()
    fig, ax = plt.subplots(figsize=(13, 9), dpi=220)
    fig.patch.set_facecolor("#f9f7f0")
    ax.set_facecolor("#f9f7f0")
    setup_base(ax, selected, barrios, comunas, streets, street_alpha=0.30, street_width=0.25)
    for family, label in [
        ("MAPA_EJECUTIVO_CANDIDATO", "Ejecutivo candidato"),
        ("REQUIERE_REDIBUJO", "Requiere redibujo"),
        ("ANEXO_EXPLORATORIO", "Anexo exploratorio"),
    ]:
        subset = selected[selected["familia_v3"] == family]
        if subset.empty:
            continue
        subset.plot(ax=ax, facecolor=FAMILY_COLORS[family], edgecolor="#20262d", linewidth=1.0, alpha=0.38, zorder=5, label=label)
        subset.boundary.plot(ax=ax, color="#20262d", linewidth=0.8, alpha=0.75, zorder=6)
    annotate(ax, selected, "nombre_mapa_v3", size=5.4)
    ax.legend(loc="upper right", frameon=True, facecolor="#fffdf7", edgecolor="#aaa", fontsize=8)
    ax.set_title("Cartografía de decisión v3 - familias de trabajo", loc="left", fontsize=15, weight="bold", color="#16202a")
    ax.text(0.01, 0.015, "Experimental / no oficial. Mapa para separar decisiones, no para presentación final.", transform=ax.transAxes, fontsize=7.5, color="#57606a")
    out = OUT / "mapa_decision_general_v3.png"
    save_fig(fig, out)
    return out


def plot_redraw(all_groups, points, refs, macrozones: list[str], title: str, filename: str) -> Path:
    barrios, comunas, streets = refs
    selected = all_groups[(all_groups["familia_v3"] == "REQUIERE_REDIBUJO") & (all_groups["macrozona"].isin(macrozones))].copy()
    pts = points[(points["macrozona_id"].isin(macrozones)) & (points["mantener_en_mapa"] != "NO")].copy()
    fig, ax = plt.subplots(figsize=(12, 7), dpi=220)
    fig.patch.set_facecolor("#fbfaf5")
    ax.set_facecolor("#fbfaf5")
    setup_base(ax, selected, barrios, comunas, streets, street_alpha=0.62, street_width=0.45)
    if not pts.empty:
        pts[pts["fuente"].astype(str).eq("F01+F02")].plot(ax=ax, color="#1f5d7a", markersize=7, alpha=0.38, zorder=4)
        pts[pts["fuente"].astype(str).eq("google_places")].plot(ax=ax, color="#c47a1d", markersize=6, alpha=0.32, zorder=4)
    selected.plot(ax=ax, facecolor="#e0a56e", edgecolor="#4f2f16", linewidth=1.15, alpha=0.22, zorder=5)
    selected.boundary.plot(ax=ax, color="#4f2f16", linewidth=0.9, alpha=0.85, zorder=6)
    annotate(ax, selected, "nombre_mapa_v3", size=8.4)
    ax.set_title(title, loc="left", fontsize=14, weight="bold", color="#16202a")
    ax.text(0.01, 0.015, "Insumo para redibujo editorial, no límite final.", transform=ax.transAxes, fontsize=7.5, color="#57606a")
    out = OUT / filename
    save_fig(fig, out)
    return out


def plot_annex(all_groups, points, refs) -> Path:
    barrios, comunas, streets = refs
    selected = all_groups[all_groups["familia_v3"] == "ANEXO_EXPLORATORIO"].copy()
    pts = points[(points["grupo_editorial_v0"].isin(selected["grupo_editorial_v0"])) & (points["mantener_en_mapa"] != "NO")].copy()
    fig, ax = plt.subplots(figsize=(12, 8), dpi=220)
    fig.patch.set_facecolor("#faf8f2")
    ax.set_facecolor("#faf8f2")
    setup_base(ax, selected, barrios, comunas, streets, street_alpha=0.42, street_width=0.32)
    if not pts.empty:
        pts.plot(ax=ax, color="#6b7280", markersize=5, alpha=0.25, zorder=4)
    selected.plot(ax=ax, facecolor="#9aa3ad", edgecolor="#303740", linewidth=1.05, alpha=0.36, zorder=5)
    selected.boundary.plot(ax=ax, color="#303740", linewidth=0.95, alpha=0.85, zorder=6)
    annotate(ax, selected, "nombre_mapa_v3", size=8.0)
    ax.set_title("Señales exploratorias - no incorporar al mapa principal", loc="left", fontsize=14, weight="bold", color="#16202a")
    ax.text(0.01, 0.015, "Experimental / no oficial. Señales auxiliares para anexo técnico o exclusión.", transform=ax.transAxes, fontsize=7.5, color="#57606a")
    out = OUT / "mapa_anexo_exploratorio_v3.png"
    save_fig(fig, out)
    return out


def png_nonblank(path: Path) -> dict[str, object]:
    img = Image.open(path).convert("RGB")
    colors = img.getcolors(maxcolors=10_000_000)
    unique = len(colors) if colors is not None else 10_000_000
    bbox = img.getbbox()
    return {"archivo": path.name, "ancho": img.width, "alto": img.height, "colores_unicos": unique, "no_blanco": bool(bbox and unique > 10)}


def write_docs(table: pd.DataFrame, map_paths: list[Path]) -> None:
    counts = table["familia_v3"].value_counts().to_dict()
    executive = table[table["familia_v3"] == "MAPA_EJECUTIVO_CANDIDATO"]["nombre_mapa_v3"].tolist()
    redraw = table[table["familia_v3"] == "REQUIERE_REDIBUJO"]["nombre_mapa_v3"].tolist()
    annex = table[table["familia_v3"] == "ANEXO_EXPLORATORIO"]["nombre_mapa_v3"].tolist()
    resumen = f"""# Resumen cartografía de decisión v3

Estado: EXPERIMENTAL / NO OFICIAL.

## Síntesis

La cartografía editorial v2 mejoró la lectura al reducir 163 polígonos a 41 grupos. Aun así, no alcanza como mapa final: conserva manchas derivadas de polígonos algorítmicos, etiquetas superpuestas y cortes que deben redibujarse con criterio urbano.

La v3 no redibuja límites finales. Ordena esos 41 grupos en tres familias de decisión: mapa ejecutivo candidato, redibujo editorial y anexo exploratorio.

## Conteo por familia

{json.dumps(counts, ensure_ascii=False, indent=2)}

## Pasan a mapa ejecutivo candidato

{chr(10).join(f'- {x}' for x in executive)}

## Requieren redibujo editorial

{chr(10).join(f'- {x}' for x in redraw)}

## Quedan en anexo exploratorio

{chr(10).join(f'- {x}' for x in annex)}

## Decisiones humanas pendientes

- Confirmar si la selección ejecutiva es suficientemente defendible.
- Redibujar Corrientes/Microcentro, Belgrano y Caballito sobre calles reales.
- Decidir si Puerto Madero se muestra por frentes o queda parcialmente como anexo.
- Definir si Costanera Norte y Av. Caseros/Barracas quedan fuera del mapa principal.
- Revisar nombres orientativos antes de cualquier versión institucional.

## Mapas creados

{chr(10).join(f'- `{p.name}`' for p in map_paths)}
"""
    (OUT / "RESUMEN_CARTOGRAFIA_DECISION_V3.md").write_text(resumen, encoding="utf-8")

    handoff = """# Handoff cartografía de decisión v3

Estado: EXPERIMENTAL / NO OFICIAL.

## Mirar primero

1. `mapa_ejecutivo_candidato_v3.png`
2. `mapa_decision_general_v3.png`
3. `tabla_decision_cartografia_v3.csv`

## Mapas que NO son para mostrar como pieza ejecutiva

- `mapa_redibujo_corrientes_microcentro_v3.png`
- `mapa_redibujo_belgrano_v3.png`
- `mapa_redibujo_caballito_v3.png`
- `mapa_anexo_exploratorio_v3.png`

Esos mapas son insumos de trabajo: sirven para decidir o redibujar, no para presentación final.

## Insumos de redibujo

- `zonas_requieren_redibujo_v3.geojson`
- `mapa_redibujo_corrientes_microcentro_v3.png`
- `mapa_redibujo_belgrano_v3.png`
- `mapa_redibujo_caballito_v3.png`

## Decisiones para Diego

- Validar o corregir la familia asignada a cada grupo.
- Confirmar qué zonas del mapa ejecutivo candidato pasan a una versión limpia.
- Decidir si las zonas de anexo se excluyen o quedan como soporte técnico.
- Definir criterios de nombres finales.

## Siguiente paso para Codex

Cuando haya decisiones humanas, Codex debería preparar una versión v4 con límites redibujados o guías de redibujo sobre calles, sin presentar la geometría algorítmica como final institucional.
"""
    (OUT / "HANDOFF_CARTOGRAFIA_DECISION_V3.md").write_text(handoff, encoding="utf-8")


def run() -> None:
    require_inputs()
    groups, points = load_layers()
    table = build_decision_table(groups)
    table.to_csv(OUT / "tabla_decision_cartografia_v3.csv", index=False, encoding="utf-8")
    all_groups = write_layers(groups, table)

    refs = load_reference_layers()
    map_paths = [
        plot_executive(all_groups, points, refs),
        plot_decision_general(all_groups, points, refs),
        plot_redraw(
            all_groups,
            points,
            refs,
            ["MZ_AVENIDA_CORRIENTES", "MZ_MICROCENTRO_Y_CENTRO"],
            "Redibujo técnico - Corrientes / Microcentro",
            "mapa_redibujo_corrientes_microcentro_v3.png",
        ),
        plot_redraw(all_groups, points, refs, ["MZ_BELGRANO"], "Redibujo técnico - Belgrano", "mapa_redibujo_belgrano_v3.png"),
        plot_redraw(all_groups, points, refs, ["MZ_CABALLITO"], "Redibujo técnico - Caballito", "mapa_redibujo_caballito_v3.png"),
        plot_annex(all_groups, points, refs),
    ]
    qa = pd.DataFrame([png_nonblank(p) for p in map_paths])
    qa.to_csv(OUT / "qa_png_no_blanco_v3.csv", index=False, encoding="utf-8")
    if not qa["no_blanco"].all():
        bad = qa.loc[~qa["no_blanco"], "archivo"].tolist()
        raise RuntimeError("PNG posiblemente en blanco: " + ", ".join(bad))
    write_docs(table, map_paths)
    metadata = {
        "estado": "EXPERIMENTAL_NO_OFICIAL",
        "api": "NO_API_NO_GOOGLE_PLACES",
        "grupos_v2_procesados": int(len(groups)),
        "conteo_familia_v3": table["familia_v3"].value_counts().to_dict(),
        "mapas_creados": [p.name for p in map_paths],
        "archivos_principales": [
            "tabla_decision_cartografia_v3.csv",
            "zonas_todas_decision_v3.geojson",
            "zonas_ejecutivas_candidatas_v3.geojson",
            "zonas_requieren_redibujo_v3.geojson",
            "zonas_anexo_exploratorio_v3.geojson",
            "zonas_excluidas_v3.geojson",
            "RESUMEN_CARTOGRAFIA_DECISION_V3.md",
            "HANDOFF_CARTOGRAFIA_DECISION_V3.md",
        ],
    }
    (OUT / "metadata_cartografia_decision_v3.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(metadata, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    run()
