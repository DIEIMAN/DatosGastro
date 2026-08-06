"""Empaqueta REVISION_INFRAESTRUCTURA_AGENTES_SKILLS_V1 (solo lectura de docs; escribe en outputs/infra...)."""
from __future__ import annotations

import csv
import hashlib
import json
import shutil
import zipfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs" / "infraestructura_agentes_skills_v1"
OUT_BASE = ROOT / "outputs" / "infraestructura_agentes_skills_v1"
REV = OUT_BASE / "REVISION_INFRAESTRUCTURA_AGENTES_SKILLS_V1"
ZIP_PATH = OUT_BASE / "REVISION_INFRAESTRUCTURA_AGENTES_SKILLS_V1.zip"
CASOS = OUT_BASE / "casos_prueba"

# No copiar PNG de QA voluminosos al ZIP de docs (opcional: copiar lista sin caso_b png)
SKIP_SUFFIXES = {".pyc"}
SKIP_DIR_NAMES = {"__pycache__", "caso_b_qa_png"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def should_skip(path: Path) -> bool:
    if path.suffix in SKIP_SUFFIXES:
        return True
    if any(p in SKIP_DIR_NAMES for p in path.parts):
        return True
    return False


def copy_tree(src: Path, dst: Path) -> None:
    if not src.exists():
        return
    for path in src.rglob("*"):
        if path.is_dir():
            continue
        if should_skip(path):
            continue
        rel = path.relative_to(src)
        target = dst / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)


def main() -> int:
    if REV.exists():
        shutil.rmtree(REV)
    REV.mkdir(parents=True)

    # Estructura del pack
    copy_tree(DOC, REV / "docs_infra")
    # Casos de prueba outputs (sin PNG pesados de QA)
    if CASOS.exists():
        copy_tree(CASOS, REV / "casos_prueba_outputs")

    # README del pack
    (REV / "README.md").write_text(
        """# REVISION_INFRAESTRUCTURA_AGENTES_SKILLS_V1

Paquete de revisión de la infraestructura controlada de agentes y skills DataGastro/DGDGAS.

## Contenido

- `docs_infra/` — auditoría, arquitectura, política, skills, agentes, plantillas, propuestas, evaluación, guía, casos documentados
- `casos_prueba_outputs/` — handoffs/planes/informes QA de los casos A–D (sin PNG de render)
- `MANIFEST_ARCHIVOS.csv`
- `metadata_infraestructura_agentes_skills_v1.json`
- `QA_FINAL_INFRAESTRUCTURA_AGENTES_SKILLS_V1.md`

## Estado

EXPERIMENTAL / NO OFICIAL. No modifica skills productivas ni AGENTS.md/CLAUDE.md.

## Cómo usar

Ver `docs_infra/GUIA_USO_AGENTES_SKILLS_DATAGASTRO.md` y `docs_infra/POLITICA_OPERATIVA_DATAGASTRO.md`.
""",
        encoding="utf-8",
    )

    # Manifest
    rows = []
    for path in sorted(REV.rglob("*")):
        if not path.is_file():
            continue
        if path.name in {"MANIFEST_ARCHIVOS.csv"}:
            continue
        rel = path.relative_to(REV).as_posix()
        rows.append(
            {
                "ruta": rel,
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )

    manifest_path = REV / "MANIFEST_ARCHIVOS.csv"
    with manifest_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["ruta", "bytes", "sha256"])
        w.writeheader()
        w.writerows(rows)

    # QA final
    qa_text = f"""# QA final — INFRAESTRUCTURA_AGENTES_SKILLS_V1

Fecha: {date.today().isoformat()}
Estado: **APTO PARA REVISIÓN HUMANA / EXPERIMENTAL / NO OFICIAL**

## Controles

| control | resultado |
| --- | --- |
| datos fuente modificados | **NO** |
| finales / F25 oficial / F26 / v2.1 baseline modificados | **NO** (solo lectura en casos) |
| paquetes previos Polos modificados | **NO** |
| API / Places / descargas / instalaciones | **NO** |
| commit / push / staging / git add . | **NO** (por esta tarea) |
| `.claude/settings.json` modificado por este empaquetado | **NO** |
| privacidad pack | OK (docs de procedimiento; menciones de patrones PII son documentales) |
| rutas | relativas al repo / pack |
| UTF-8 | sí (MD/CSV/JSON) |
| ZIP | ver postcondición |

## Casos de prueba

| caso | resultado |
| --- | --- |
| A evidencia documental | PASS |
| B PDF político experimental | PASS (PDF no editado) |
| C integración v2.1 | PASS (solo plan) |
| D cartografía PM | PASS (sin regenerar mapas) |

## Veredicto infraestructura

**APTO_CON_AJUSTES** para uso controlado. No producción global sin punteros AGENTS/CLAUDE y paridad de skills.

## Archivos en este pack

Ver MANIFEST_ARCHIVOS.csv ({len(rows)} entradas antes de incluir este QA y metadata si se regenera).
"""
    qa_path = REV / "QA_FINAL_INFRAESTRUCTURA_AGENTES_SKILLS_V1.md"
    qa_path.write_text(qa_text, encoding="utf-8")

    meta = {
        "nombre": "REVISION_INFRAESTRUCTURA_AGENTES_SKILLS_V1",
        "fecha": date.today().isoformat(),
        "estado": "EXPERIMENTAL_NO_OFICIAL",
        "veredicto": "APTO_CON_AJUSTES",
        "restricciones": [
            "no_modifica_finales",
            "no_api",
            "no_commit",
            "sin_symlinks",
            "no_sobrescribe_AGENTS_ni_CLAUDE",
        ],
        "skills_v1": 10,
        "agentes_v1": 7,
        "casos_prueba": ["A", "B", "C", "D"],
        "ruta_docs": "docs/infraestructura_agentes_skills_v1/",
        "ruta_outputs": "outputs/infraestructura_agentes_skills_v1/",
    }
    meta_path = REV / "metadata_infraestructura_agentes_skills_v1.json"
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # Rehacer manifest incluyendo QA y metadata
    rows = []
    for path in sorted(REV.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(REV).as_posix()
        if rel == "MANIFEST_ARCHIVOS.csv":
            continue
        rows.append({"ruta": rel, "bytes": path.stat().st_size, "sha256": sha256(path)})
    with manifest_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["ruta", "bytes", "sha256"])
        w.writeheader()
        w.writerows(rows)
    # append manifest self-hash after write of content without self — store separately
    manifest_row = {
        "ruta": "MANIFEST_ARCHIVOS.csv",
        "bytes": manifest_path.stat().st_size,
        "sha256": sha256(manifest_path),
    }
    # rewrite full including self with second pass note in metadata
    with manifest_path.open("a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["ruta", "bytes", "sha256"])
        w.writerow(manifest_row)

    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(REV.rglob("*")):
            if path.is_file():
                arc = "REVISION_INFRAESTRUCTURA_AGENTES_SKILLS_V1/" + path.relative_to(REV).as_posix()
                zf.write(path, arcname=arc)

    with zipfile.ZipFile(ZIP_PATH, "r") as zf:
        bad = zf.testzip()
        if bad is not None:
            raise SystemExit(f"ZIP corrupt: {bad}")
        n_members = len(zf.namelist())

    print(f"REV: {REV}")
    print(f"files: {len([p for p in REV.rglob('*') if p.is_file()])}")
    print(f"ZIP: {ZIP_PATH} ({ZIP_PATH.stat().st_size} bytes)")
    print(f"ZIP members: {n_members}")
    print(f"ZIP sha256: {sha256(ZIP_PATH)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
