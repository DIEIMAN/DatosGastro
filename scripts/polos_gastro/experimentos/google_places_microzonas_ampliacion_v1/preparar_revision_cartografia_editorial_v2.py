from __future__ import annotations

import json
import re
import shutil
import zipfile
from pathlib import Path

import geopandas as gpd
import pandas as pd


ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "outputs/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1"
SOURCE = BASE / "cartografia_editorial_v2"
PACKAGE_NAME = "REVISION_CARTOGRAFIA_EDITORIAL_V2"
DEST = BASE / PACKAGE_NAME
ZIP_PATH = BASE / f"{PACKAGE_NAME}.zip"

MAPS = [
    "mapa_general_simplificado_v0.png",
    "mapa_palermo_simplificado_v0.png",
    "mapa_san_telmo_simplificado_v0.png",
    "mapa_belgrano_simplificado_v0.png",
    "mapa_corrientes_microcentro_simplificado_v0.png",
    "mapa_caballito_simplificado_v0.png",
    "mapa_recoleta_simplificado_v0.png",
    "mapa_villa_crespo_simplificado_v0.png",
    "mapa_puerto_madero_simplificado_v0.png",
    "mapa_chacarita_simplificado_v0.png",
    "mapa_costanera_norte_simplificado_v0.png",
    "mapa_caseros_barracas_simplificado_v0.png",
]

COPY_PLAN = {
    "00_LEER_PRIMERO": [
        "RESUMEN_CARTOGRAFIA_EDITORIAL_V2.md",
        "HANDOFF_CARTOGRAFIA_EDITORIAL_V2.md",
        "metadata_cartografia_editorial_v2.json",
    ],
    "01_MAPAS": MAPS,
    "02_TABLAS": [
        "tabla_agrupamiento_editorial_v0.csv",
        "qa_png_no_blanco_v0.csv",
        "capas_referencia_locales_detectadas_v0.csv",
    ],
    "03_GEOJSON": [
        "poligonos_editoriales_simplificados_v0.geojson",
        "puntos_evidencia_microzonas_v0.geojson",
    ],
}

REVIEW_ORDER = [
    ("mapa_general_simplificado_v0.png", "Mapa general"),
    ("mapa_san_telmo_simplificado_v0.png", "San Telmo"),
    ("mapa_palermo_simplificado_v0.png", "Palermo"),
    ("mapa_belgrano_simplificado_v0.png", "Belgrano"),
    ("mapa_corrientes_microcentro_simplificado_v0.png", "Corrientes / Microcentro"),
    ("mapa_caballito_simplificado_v0.png", "Caballito"),
    ("mapa_recoleta_simplificado_v0.png", "Recoleta"),
    ("mapa_villa_crespo_simplificado_v0.png", "Villa Crespo"),
    ("mapa_chacarita_simplificado_v0.png", "Chacarita"),
    ("mapa_puerto_madero_simplificado_v0.png", "Puerto Madero"),
    ("mapa_costanera_norte_simplificado_v0.png", "Costanera Norte"),
    ("mapa_caseros_barracas_simplificado_v0.png", "Caseros / Barracas"),
    ("tabla_agrupamiento_editorial_v0.csv", "Tabla de agrupamiento si algo no se entiende"),
]


def require_inputs() -> None:
    if not SOURCE.exists():
        raise FileNotFoundError(f"No existe carpeta fuente: {SOURCE}")
    missing = []
    for files in COPY_PLAN.values():
        for name in files:
            if not (SOURCE / name).exists():
                missing.append(name)
    if missing:
        raise FileNotFoundError("Faltan archivos fuente: " + ", ".join(missing))
    if DEST.exists():
        raise FileExistsError(f"La carpeta de paquete ya existe: {DEST}")
    if ZIP_PATH.exists():
        raise FileExistsError(f"El ZIP ya existe: {ZIP_PATH}")


def copy_allowlist() -> None:
    for folder in ["00_LEER_PRIMERO", "01_MAPAS", "02_TABLAS", "03_GEOJSON", "04_NOTAS_PARA_CHATGPT"]:
        (DEST / folder).mkdir(parents=True, exist_ok=False)
    for folder, files in COPY_PLAN.items():
        for name in files:
            shutil.copy2(SOURCE / name, DEST / folder / name)


def build_group_summary() -> None:
    groups = gpd.read_file(SOURCE / "poligonos_editoriales_simplificados_v0.geojson")
    summary = (
        groups.groupby(["macrozona", "accion_v2"], dropna=False)
        .agg(
            grupos=("grupo_editorial_v0", "count"),
            poligonos_originales=("n_poligonos_originales", "sum"),
            entidades_total=("entidades_total", "sum"),
            cantidad_f01_f02=("cantidad_f01_f02", "sum"),
            cantidad_places=("cantidad_places", "sum"),
        )
        .reset_index()
        .sort_values(["macrozona", "accion_v2"])
    )
    summary["porcentaje_places"] = summary.apply(
        lambda row: round((row["cantidad_places"] / row["entidades_total"]) * 100, 1)
        if row["entidades_total"]
        else 0.0,
        axis=1,
    )
    summary.to_csv(DEST / "02_TABLAS" / "tabla_resumen_grupos_editoriales_por_zona_v0.csv", index=False, encoding="utf-8")


def write_readme_and_context() -> None:
    metadata = json.loads((SOURCE / "metadata_cartografia_editorial_v2.json").read_text(encoding="utf-8"))
    order_lines = "\n".join(
        f"{idx}. `{name}` - {label}" for idx, (name, label) in enumerate(REVIEW_ORDER, start=1)
    )
    readme = f"""# Revision cartografia editorial v2

Estado: EXPERIMENTAL / NO OFICIAL.

Este paquete sirve para revisar visualmente si los grupos editoriales simplificados son legibles, defendibles y utiles como base de una futura decision humana.

La version previa tenia 163 poligonos algoritimicos. Esta version los reduce a {metadata['grupos_editoriales_visibles_v0']} grupos editoriales visibles. No es una delimitacion institucional final.

## Orden sugerido de revision

{order_lines}

## Que revisar

- Si el mapa se entiende sin explicar la metodologia.
- Si el nombre orientativo ayuda o confunde.
- Si el grupo parece defendible como nucleo, corredor o senal exploratoria.
- Si algun grupo deberia fusionarse, dividirse, excluirse o quedar solo como anexo tecnico.

## Limites

- No se hicieron nuevas consultas externas.
- No se redibujaron limites finos sobre calles.
- Los puntos son evidencia auxiliar; no prueban actividad actual ni habilitacion vigente.
- La capa simplificada es un tablero de decision, no un producto final.
"""
    (DEST / "00_LEER_PRIMERO" / "README_REVISION_CARTOGRAFIA_EDITORIAL_V2.md").write_text(readme, encoding="utf-8")

    context = """# Contexto para ChatGPT - cartografia editorial v2

Estado: EXPERIMENTAL / NO OFICIAL.

La revision previa de 163 poligonos era util como insumo tecnico, pero no era legible como capa editorial: demasiadas piezas, formas irregulares, cortes KMeans artificiales y poca referencia urbana.

Esta cartografia editorial v2 reduce esos 163 poligonos a 41 grupos editoriales simplificados. El objetivo ahora no es validar una frontera final, sino revisar legibilidad, nombres orientativos y defendibilidad institucional de cada grupo.

No hace falta mas API por ahora. El problema principal ya no es conseguir mas puntos, sino decidir que piezas tienen sentido territorial y como deberian redibujarse despues sobre calles reales.

Zonas criticas para mirar con mas atencion:

- Corrientes / Microcentro.
- Belgrano.
- Caballito.
- Costanera Norte.
- Caseros / Barracas.
- Piezas exploratorias de Puerto Madero.

Preguntas recomendadas:

- El grupo se entiende visualmente?
- El nombre orientativo describe bien el territorio?
- La pieza parece nucleo, corredor, senal exploratoria o deberia excluirse?
- Hay grupos que conviene fusionar o partir antes de una version institucional?
- Que zonas deberian quedar fuera del mapa principal y pasar a anexo tecnico?

La capa no debe usarse como final institucional. Sirve para revision humana antes de redibujar limites finos.
"""
    (DEST / "04_NOTAS_PARA_CHATGPT" / "CONTEXTO_PARA_CHATGPT_CARTOGRAFIA_EDITORIAL_V2.md").write_text(
        context, encoding="utf-8"
    )


def write_manifest() -> None:
    rows = []
    for p in sorted(DEST.rglob("*")):
        if p.is_file():
            rows.append((str(p.relative_to(DEST)).replace("\\", "/"), p.stat().st_size))
    lines = [
        "# Manifest archivos",
        "",
        "Estado: EXPERIMENTAL / NO OFICIAL.",
        "",
        "El paquete contiene solo archivos necesarios para revision visual de la cartografia editorial v2.",
        "",
        "| Archivo | Bytes |",
        "| --- | ---: |",
    ]
    lines.extend(f"| `{name}` | {size} |" for name, size in rows)
    (DEST / "00_LEER_PRIMERO" / "MANIFEST_ARCHIVOS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def make_zip() -> None:
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(DEST.rglob("*")):
            if p.is_file():
                arcname = Path(PACKAGE_NAME) / p.relative_to(DEST)
                zf.write(p, arcname.as_posix())


def qa_package() -> dict[str, object]:
    patterns = {
        "api_key_google": re.compile(r"AIza[0-9A-Za-z_\-]{20,}"),
        "email": re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}"),
        "api_technical_id": re.compile(r"place_id", re.I),
        "private_drive_docs_link": re.compile(r"drive\.google\.com|docs\.google\.com", re.I),
        "cuit_dni_label_or_format": re.compile(r"\b(CUIT|C\.U\.I\.T\.|DNI|D\.N\.I\.)\b|\b\d{2}-\d{8}-\d\b"),
        "phone_label_or_arg_phone": re.compile(r"whatsapp|telefono|tel[eé]fono|celular|phone|\b(?:\+?54\s*)?(?:11\s*)?\d{4}[-\s]?\d{4}\b", re.I),
    }
    text_ext = {".csv", ".json", ".geojson", ".md", ".txt"}
    hits = {key: [] for key in patterns}
    for p in DEST.rglob("*"):
        rel = str(p.relative_to(DEST)).replace("\\", "/")
        if "interno/" in rel.lower() or p.name.lower() == ".env" or "raw" in p.name.lower():
            hits.setdefault("forbidden_path_or_raw_name", []).append(rel)
        if not p.is_file() or p.suffix.lower() not in text_ext:
            continue
        text = p.read_text(encoding="utf-8", errors="ignore")
        for label, pattern in patterns.items():
            if pattern.search(text):
                hits[label].append(rel)

    with zipfile.ZipFile(ZIP_PATH) as zf:
        names = zf.namelist()
    bad_root = [name for name in names if not name.startswith(f"{PACKAGE_NAME}/")]
    folder_counts = {}
    for p in DEST.rglob("*"):
        if p.is_file():
            top = p.relative_to(DEST).parts[0]
            folder_counts[top] = folder_counts.get(top, 0) + 1

    return {
        "folder_exists": DEST.exists(),
        "zip_exists": ZIP_PATH.exists(),
        "zip_size_bytes": ZIP_PATH.stat().st_size,
        "file_count": sum(1 for p in DEST.rglob("*") if p.is_file()),
        "folder_counts": dict(sorted(folder_counts.items())),
        "privacy_hits": hits,
        "bad_zip_root_entries": bad_root,
        "zip_entries": len(names),
    }


def run() -> None:
    require_inputs()
    copy_allowlist()
    build_group_summary()
    write_readme_and_context()
    write_manifest()
    make_zip()
    qa = qa_package()
    print(json.dumps(qa, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    run()
