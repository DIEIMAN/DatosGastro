from __future__ import annotations

import csv
import json
import shutil
import zipfile
import argparse
from collections import Counter
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "outputs" / "polos_gastro" / "experimentos" / "google_places_microzonas_ampliacion_v1"
COMPLETA = EXP / "completa_v1"
REVISION = COMPLETA / "revision_editorial_v1"
PAQUETE = COMPLETA / "paquete_editorial_v1"
DOCS = ROOT / "docs" / "polos_gastro" / "experimentos" / "google_places_microzonas_ampliacion_v1"

DEST = EXP / "REVISION_HUMANA_COMPLETA_V1"
ZIP_PATH = EXP / "REVISION_HUMANA_COMPLETA_V1.zip"


def ensure_source(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Falta insumo requerido: {path}")


def copy_file(src: Path, dst: Path, manifest: list[dict[str, str]], desc: str, use: str, priority: str) -> None:
    ensure_source(src)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    manifest.append(
        {
            "ruta_relativa": dst.relative_to(DEST).as_posix(),
            "tipo": dst.suffix.lower().lstrip(".") or "archivo",
            "descripcion": desc,
            "para_que_sirve": use,
            "prioridad": priority,
        }
    )


def write_text(path: Path, content: str, manifest: list[dict[str, str]], desc: str, use: str, priority: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")
    manifest.append(
        {
            "ruta_relativa": path.relative_to(DEST).as_posix(),
            "tipo": "md",
            "descripcion": desc,
            "para_que_sirve": use,
            "prioridad": priority,
        }
    )


def summarize_universe(manifest: list[dict[str, str]]) -> None:
    src = COMPLETA / "UNIVERSO_COMPLETO_SANITIZADO.csv"
    ensure_source(src)
    df = pd.read_csv(src)
    group_cols = ["macrozona_id", "fuente"]
    resumen = (
        df.groupby(group_cols, dropna=False)
        .size()
        .reset_index(name="cantidad_puntos")
        .sort_values(["macrozona_id", "fuente"])
    )
    pivot = (
        df.pivot_table(index="macrozona_id", columns="fuente", values="id_punto", aggfunc="count", fill_value=0)
        .reset_index()
    )
    pivot["total_puntos"] = pivot.drop(columns=["macrozona_id"]).sum(axis=1)
    out = DEST / "03_TABLAS_REVISION" / "tabla_resumen_universo_por_macrozona_fuente.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    resumen.to_csv(out, index=False, encoding="utf-8")
    manifest.append(
        {
            "ruta_relativa": out.relative_to(DEST).as_posix(),
            "tipo": "csv",
            "descripcion": "Conteo agregado del universo sanitizado por macrozona y fuente.",
            "para_que_sirve": "Permite revisar peso relativo de F01+F02 y Google Places sin mirar filas individuales.",
            "prioridad": "prioritario",
        }
    )
    out_pivot = DEST / "03_TABLAS_REVISION" / "tabla_resumen_universo_pivot_macrozona_fuente.csv"
    pivot.to_csv(out_pivot, index=False, encoding="utf-8")
    manifest.append(
        {
            "ruta_relativa": out_pivot.relative_to(DEST).as_posix(),
            "tipo": "csv",
            "descripcion": "Tabla ancha agregada por macrozona con totales por fuente.",
            "para_que_sirve": "Lectura rapida de composicion del universo por macrozona.",
            "prioridad": "complementario",
        }
    )


def redact_contact_terms_in_universe_copy(path: Path) -> None:
    df = pd.read_csv(path)
    if "nombre_normalizado" in df.columns:
        df["nombre_normalizado"] = (
            df["nombre_normalizado"]
            .astype(str)
            .str.replace(
                r"\b(whatsapp|telefono|teléfono|celular|phone)\b",
                "contacto_redactado",
                regex=True,
                case=False,
            )
        )
    df.to_csv(path, index=False, encoding="utf-8")


def readme_revision_humana() -> str:
    return """
# README revision humana completa v1

Estado: EXPERIMENTAL / no oficial. Este paquete no define limites institucionales ni acredita locales activos.

## Objetivo

Ordenar en una carpeta limpia los mapas, tablas y capas necesarios para que Diego revise visualmente los 163 poligonos experimentales de microzonas gastronomicas antes de cualquier redibujo o version institucional.

## Orden recomendado de lectura

1. `00_LEER_PRIMERO/README_REVISION_HUMANA.md`
2. `01_MAPAS_GENERALES/contact_sheet_mapas_completa_v1.png`
3. `01_MAPAS_GENERALES/mapa_general_categorias_editoriales_v1.png`
4. `03_TABLAS_REVISION/tabla_decision_editorial_microzonas_v1.csv`
5. Mapas por zona en este orden: San Telmo, Palermo, Belgrano, Corrientes/Microcentro, Caballito, Recoleta, Villa Crespo, Puerto Madero, Chacarita, Costanera Norte y Caseros/Barracas.
6. GeoJSON solo si se quiere revisar o simbolizar en QGIS.

## Que mirar primero

- En el contact sheet: continuidad territorial, cortes artificiales, piezas aisladas y zonas con exceso de fragmentacion.
- En el mapa general por categorias: donde predominan `REVISAR CORTE`, `REVISAR UNIVERSO` o `DESCARTAR`.
- En la tabla de decision: `accion_editorial`, `prioridad_revision`, `problema_detectado` y `proxima_accion`.

## Como interpretar las categorias

- `APROBAR`: candidato directo a borrador editorial.
- `APROBAR CON OBSERVACIONES`: candidato a borrador, pero requiere nota o ajuste menor.
- `REVISAR CORTE`: requiere redibujo de limite con criterio urbano.
- `REVISAR FUSION`: evaluar union con poligonos vecinos o continuidad de corredor.
- `REVISAR UNIVERSO`: no consolidar sin validacion humana o fuente complementaria.
- `DESCARTAR`: dejar fuera de la capa editorial por ahora.

## Decisiones humanas pendientes

- Confirmar que las piezas aprobables tienen lectura urbana defendible.
- Redibujar cortes artificiales en Corrientes/Microcentro, Belgrano y Caballito.
- Decidir si Puerto Madero se organiza por diques/frentes o por piezas mas chicas.
- Tratar Costanera Norte y Caseros/Barracas como senal exploratoria hasta validacion adicional.
- Resolver si las piezas con alto peso de Places y bajo respaldo F01+F02 entran, salen o quedan con nota metodologica.

## Que NO debe considerarse version final

Ningun GeoJSON de este paquete debe usarse como limite institucional final. Las capas son insumos de decision y revision. La version institucional requiere redibujo manual, nomenclatura editorial, validacion metodologica y nuevo paquete versionado.

## Nota metodologica

Google Places se usa como senal auxiliar no oficial de oferta visible. F01+F02 y Google Places no deben leerse como padron de locales activos.
"""


def contexto_chatgpt() -> str:
    return """
# Contexto para ChatGPT

Este ZIP contiene un paquete de revision humana para la linea Polos Gastronomicos de DataGastro / DGDGAS.

Estado: EXPERIMENTAL / no oficial. No define limites oficiales, no acredita locales activos y no requiere nuevas llamadas a Google Places por ahora.

## Que se hizo

Se partio de la capa `completa_v1`, que integra fuentes publicas F01+F02 con Google Places como senal auxiliar no oficial. Sobre esa base se generaron 163 poligonos experimentales y una revision editorial preliminar.

Conteo editorial:

- APROBAR: 46
- APROBAR CON OBSERVACIONES: 51
- REVISAR CORTE: 42
- REVISAR FUSION: 4
- REVISAR UNIVERSO: 6
- DESCARTAR: 14

El objetivo ahora no es calcular mas datos ni llamar API. El objetivo es pasar de poligonos algoritmicos a microzonas institucionalmente defendibles mediante revision humana.

## Archivos para mirar primero

1. `00_LEER_PRIMERO/README_REVISION_HUMANA.md`
2. `01_MAPAS_GENERALES/contact_sheet_mapas_completa_v1.png`
3. `01_MAPAS_GENERALES/mapa_general_categorias_editoriales_v1.png`
4. `03_TABLAS_REVISION/tabla_decision_editorial_microzonas_v1.csv`
5. `04_GEOJSON_QGIS/poligonos_todos_con_revision_v1.geojson`, si se va a revisar en QGIS.

## Que se espera revisar

- Si los poligonos aprobables tienen continuidad territorial y lectura urbana defendible.
- Si los cortes marcados como `REVISAR CORTE` responden a limites reales o a particiones algoritmicas.
- Si las piezas pequenas, aisladas o de baja densidad conviene descartarlas o dejarlas como observacion.
- Si hay zonas que deben fusionarse antes de pasar a borrador.
- Si las zonas con alto peso de Places y bajo respaldo F01+F02 requieren nota metodologica o exclusion.

## Zonas problematicas

- Corrientes/Microcentro: continuidad urbana y cortes artificiales.
- Belgrano: cortes KMeans, especialmente entorno Cabildo/Juramento/Barrio Chino.
- Caballito: posible sobreparticion de corredores.
- Recoleta y Villa Crespo: saturacion previa, resolver por criterio editorial antes que por mas API.
- Puerto Madero: definir lectura por diques/frentes y descartar piezas debiles.
- Costanera Norte y Caseros/Barracas: macrozonas debiles o emergentes, no consolidar sin decision humana.
- Chacarita: revisar celdas saturadas y continuidad con lectura territorial.

## Criterio de trabajo

No usar mas API por ahora. Priorizar revision visual, continuidad urbana, comparabilidad con el piloto y trazabilidad metodologica. Mantener la leyenda de que Google Places es senal auxiliar no oficial.
"""


def manifest_md(rows: list[dict[str, str]]) -> str:
    lines = [
        "# Manifest archivos",
        "",
        "Estado: EXPERIMENTAL / no oficial.",
        "",
        "| ruta relativa | tipo | descripcion | para que sirve | prioridad |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in sorted(rows, key=lambda r: r["ruta_relativa"]):
        lines.append(
            f"| `{row['ruta_relativa']}` | {row['tipo']} | {row['descripcion']} | {row['para_que_sirve']} | {row['prioridad']} |"
        )
    return "\n".join(lines)


def add_manifest_entry(path: Path, manifest: list[dict[str, str]], desc: str, use: str, priority: str) -> None:
    manifest.append(
        {
            "ruta_relativa": path.relative_to(DEST).as_posix(),
            "tipo": path.suffix.lower().lstrip(".") or "archivo",
            "descripcion": desc,
            "para_que_sirve": use,
            "prioridad": priority,
        }
    )


def build_package(refresh_existing: bool = False) -> dict[str, object]:
    if DEST.exists() and not refresh_existing:
        raise FileExistsError(f"La carpeta destino ya existe: {DEST}")
    if ZIP_PATH.exists() and not refresh_existing:
        raise FileExistsError(f"El ZIP destino ya existe: {ZIP_PATH}")

    manifest: list[dict[str, str]] = []
    for sub in [
        "00_LEER_PRIMERO",
        "01_MAPAS_GENERALES",
        "02_MAPAS_POR_ZONA",
        "03_TABLAS_REVISION",
        "04_GEOJSON_QGIS",
        "05_NOTAS_PARA_CHATGPT",
    ]:
        (DEST / sub).mkdir(parents=True, exist_ok=True)

    write_text(
        DEST / "00_LEER_PRIMERO" / "README_REVISION_HUMANA.md",
        readme_revision_humana(),
        manifest,
        "Guia practica para Diego.",
        "Indica orden de lectura, categorias y decisiones humanas pendientes.",
        "prioritario",
    )

    copy_file(
        DOCS / "RESUMEN_EJECUTIVO_REVISION_COMPLETA_V1.md",
        DEST / "00_LEER_PRIMERO" / "RESUMEN_EJECUTIVO_REVISION_COMPLETA_V1.md",
        manifest,
        "Resumen ejecutivo de la revision editorial preliminar.",
        "Da el conteo y los principales limites de lectura.",
        "prioritario",
    )
    copy_file(
        PAQUETE / "RESUMEN_PAQUETE_EDITORIAL_V1.md",
        DEST / "00_LEER_PRIMERO" / "RESUMEN_PAQUETE_EDITORIAL_V1.md",
        manifest,
        "Resumen del paquete editorial v1.",
        "Sintetiza capas, prioridades y macrozonas debiles.",
        "prioritario",
    )
    copy_file(
        DOCS / "HANDOFF_REVISION_POLIGONOS_COMPLETA_V1.md",
        DEST / "00_LEER_PRIMERO" / "HANDOFF_REVISION_POLIGONOS_COMPLETA_V1.md",
        manifest,
        "Handoff de revision de poligonos completa v1.",
        "Enumera candidatos y reglas para la siguiente tanda.",
        "prioritario",
    )
    copy_file(
        PAQUETE / "HANDOFF_PAQUETE_EDITORIAL_V1.md",
        DEST / "00_LEER_PRIMERO" / "HANDOFF_PAQUETE_EDITORIAL_V1.md",
        manifest,
        "Handoff del paquete editorial v1.",
        "Indica capas a abrir y pasos faltantes para version institucional.",
        "prioritario",
    )

    copy_file(
        REVISION / "contact_sheet_mapas_completa_v1.png",
        DEST / "01_MAPAS_GENERALES" / "contact_sheet_mapas_completa_v1.png",
        manifest,
        "Contact sheet de mapas completa v1.",
        "Permite una primera lectura visual de todas las zonas.",
        "prioritario",
    )
    copy_file(
        PAQUETE / "mapas_revision" / "mapa_general_categorias_editoriales_v1.png",
        DEST / "01_MAPAS_GENERALES" / "mapa_general_categorias_editoriales_v1.png",
        manifest,
        "Mapa general por categoria editorial.",
        "Muestra aprobables, cortes, universo, fusion y descartes.",
        "prioritario",
    )
    for src in sorted((COMPLETA / "mapas").glob("*general*.png")):
        copy_file(
            src,
            DEST / "01_MAPAS_GENERALES" / src.name,
            manifest,
            "Mapa general adicional de completa v1.",
            "Referencia visual complementaria.",
            "complementario",
        )

    for src in sorted((COMPLETA / "mapas").glob("*.png")):
        copy_file(
            src,
            DEST / "02_MAPAS_POR_ZONA" / f"completa__{src.name}",
            manifest,
            "Mapa por zona de completa v1.",
            "Sirve para revisar poligonos, puntos y lectura territorial por zona.",
            "prioritario",
        )
    for src in sorted((PAQUETE / "mapas_revision").glob("*.png")):
        if "general" in src.name:
            continue
        copy_file(
            src,
            DEST / "02_MAPAS_POR_ZONA" / f"revision__{src.name}",
            manifest,
            "Mapa de revision editorial por zona.",
            "Sirve para revisar categorias y problemas editoriales focalizados.",
            "prioritario",
        )

    copy_file(
        REVISION / "tabla_revision_editorial_poligonos_completa_v1.csv",
        DEST / "03_TABLAS_REVISION" / "tabla_revision_editorial_poligonos_completa_v1.csv",
        manifest,
        "Tabla de revision editorial preliminar.",
        "Base analitica de clasificacion por poligono.",
        "prioritario",
    )
    copy_file(
        PAQUETE / "tabla_decision_editorial_microzonas_v1.csv",
        DEST / "03_TABLAS_REVISION" / "tabla_decision_editorial_microzonas_v1.csv",
        manifest,
        "Tabla de decision editorial.",
        "Tablero principal para decidir accion y prioridad por microzona.",
        "prioritario",
    )
    copy_file(
        REVISION / "resumen_revision_editorial_poligonos_completa_v1.json",
        DEST / "03_TABLAS_REVISION" / "resumen_revision_editorial_poligonos_completa_v1.json",
        manifest,
        "Resumen JSON de revision editorial.",
        "Control tecnico de conteos de la revision.",
        "complementario",
    )
    copy_file(
        PAQUETE / "metadata_paquete_editorial_v1.json",
        DEST / "03_TABLAS_REVISION" / "metadata_paquete_editorial_v1.json",
        manifest,
        "Metadata del paquete editorial.",
        "Control tecnico de capas y conteos.",
        "complementario",
    )
    universo = COMPLETA / "UNIVERSO_COMPLETO_SANITIZADO.csv"
    if universo.stat().st_size <= 5 * 1024 * 1024:
        copy_file(
            universo,
            DEST / "03_TABLAS_REVISION" / "UNIVERSO_COMPLETO_SANITIZADO.csv",
            manifest,
            "Universo completo sanitizado.",
            "Permite auditoria de composicion de puntos sin raw JSON ni identificadores tecnicos de API.",
            "complementario",
        )
        redact_contact_terms_in_universe_copy(DEST / "03_TABLAS_REVISION" / "UNIVERSO_COMPLETO_SANITIZADO.csv")
    summarize_universe(manifest)

    geojsons = [
        PAQUETE / "poligonos_todos_con_revision_v1.geojson",
        PAQUETE / "poligonos_aprobables_v1.geojson",
        PAQUETE / "poligonos_revisar_corte_v1.geojson",
        PAQUETE / "poligonos_revisar_fusion_v1.geojson",
        PAQUETE / "poligonos_revisar_universo_v1.geojson",
        PAQUETE / "poligonos_descartar_v1.geojson",
        COMPLETA / "POLIGONOS_MICROZONAS_COMPLETA_V1.geojson",
        COMPLETA / "MICROCLUSTERS_COMPLETA_V1.geojson",
    ]
    for src in geojsons:
        copy_file(
            src,
            DEST / "04_GEOJSON_QGIS" / src.name,
            manifest,
            "Capa GeoJSON para QGIS.",
            "Insumo geoespacial de revision; no usar como version final.",
            "prioritario" if "todos_con_revision" in src.name or src.name.isupper() else "complementario",
        )

    write_text(
        DEST / "05_NOTAS_PARA_CHATGPT" / "CONTEXTO_PARA_CHATGPT.md",
        contexto_chatgpt(),
        manifest,
        "Contexto breve para compartir con ChatGPT.",
        "Explica objetivo, archivos clave y zonas problematicas.",
        "prioritario",
    )

    manifest_path = DEST / "00_LEER_PRIMERO" / "MANIFEST_ARCHIVOS.md"
    write_text(
        manifest_path,
        manifest_md(manifest),
        manifest,
        "Manifest de archivos incluidos.",
        "Indice de ruta, tipo, descripcion, uso y prioridad.",
        "prioritario",
    )

    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for path in sorted(DEST.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(DEST.parent))

    counts = Counter(p.relative_to(DEST).parts[0] for p in DEST.rglob("*") if p.is_file())
    return {
        "dest": str(DEST),
        "zip": str(ZIP_PATH),
        "zip_size_bytes": ZIP_PATH.stat().st_size,
        "file_count": sum(counts.values()),
        "counts_by_folder": dict(sorted(counts.items())),
        "manifest_rows": len(manifest),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh-existing", action="store_true")
    args = parser.parse_args()
    result = build_package(refresh_existing=args.refresh_existing)
    print(json.dumps(result, ensure_ascii=False, indent=2))
