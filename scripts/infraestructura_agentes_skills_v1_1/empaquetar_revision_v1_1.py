"""Empaqueta REVISION_INFRAESTRUCTURA_AGENTES_SKILLS_V1_1 con manifest sin autorreferencia."""
from __future__ import annotations

import csv
import hashlib
import json
import shutil
import zipfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs" / "infraestructura_agentes_skills_v1_1"
SCRIPTS = ROOT / "scripts" / "infraestructura_agentes_skills_v1_1"
OUT_BASE = ROOT / "outputs" / "infraestructura_agentes_skills_v1_1"
REV = OUT_BASE / "REVISION_INFRAESTRUCTURA_AGENTES_SKILLS_V1_1"
ZIP_PATH = OUT_BASE / "REVISION_INFRAESTRUCTURA_AGENTES_SKILLS_V1_1.zip"
POLOS_PROTECTED = ROOT / "docs" / "polos_gastro" / "PROTECTED_SURFACES.yaml"

SKIP_DIR_NAMES = {"__pycache__", "caso_b_qa_png", ".git"}
SKIP_SUFFIXES = {".pyc"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def should_skip(path: Path) -> bool:
    if path.suffix in SKIP_SUFFIXES:
        return True
    return any(part in SKIP_DIR_NAMES for part in path.parts)


def copy_tree(src: Path, dst: Path) -> None:
    if not src.exists():
        return
    for path in src.rglob("*"):
        if not path.is_file() or should_skip(path):
            continue
        rel = path.relative_to(src)
        target = dst / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)


def write_manifest_contenido(pack_root: Path) -> Path:
    """Lista todos los archivos excepto MANIFEST_CONTENIDO.csv y CHECKSUMS externos."""
    rows = []
    exclude_names = {"MANIFEST_CONTENIDO.csv", "CHECKSUMS_SHA256.txt"}
    for path in sorted(pack_root.rglob("*")):
        if not path.is_file():
            continue
        if path.name in exclude_names and path.parent == pack_root:
            continue
        # also exclude if nested same names for clarity
        if path.name == "MANIFEST_CONTENIDO.csv":
            continue
        rel = path.relative_to(pack_root).as_posix()
        rows.append({"ruta_relativa": rel, "bytes": path.stat().st_size, "sha256": sha256(path)})
    out = pack_root / "MANIFEST_CONTENIDO.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["ruta_relativa", "bytes", "sha256"])
        w.writeheader()
        w.writerows(rows)
    return out


def main() -> int:
    if REV.exists():
        shutil.rmtree(REV)
    REV.mkdir(parents=True)

    copy_tree(DOC, REV / "docs_infra")
    copy_tree(SCRIPTS, REV / "scripts_infra")
    if POLOS_PROTECTED.is_file():
        dest = REV / "registros_subproyecto" / "polos_gastro"
        dest.mkdir(parents=True)
        shutil.copy2(POLOS_PROTECTED, dest / "PROTECTED_SURFACES.yaml")

    # copiar outputs de casos e2e y paridad (sin PNG pesados opcionales)
    for sub in ("casos_e2e", "paridad"):
        src = OUT_BASE / sub
        if src.exists():
            copy_tree(src, REV / sub)

    (REV / "README.md").write_text(
        """# REVISION_INFRAESTRUCTURA_AGENTES_SKILLS_V1_1

Paquete de revisión V1.1 (correcciones + E2E + paridad).

- `docs_infra/` — política, catálogo, evaluación, adaptadores, casos
- `scripts_infra/` — parity, empaquetado, E2E helpers
- `casos_e2e/` — salidas de pruebas end-to-end
- `paridad/` — reportes de paridad
- `MANIFEST_CONTENIDO.csv` — sin autorreferencia
- `CHECKSUMS_SHA256.txt` — junto al pack; el del ZIP está fuera del ZIP

Ver `docs_infra/ESQUEMA_MANIFEST_V1_1.md`.
""",
        encoding="utf-8",
    )

    meta = {
        "nombre": "REVISION_INFRAESTRUCTURA_AGENTES_SKILLS_V1_1",
        "fecha": date.today().isoformat(),
        "estado": "EXPERIMENTAL_NO_OFICIAL",
        "version_infra": "1.1",
        "schema_manifest": "MANIFEST_CONTENIDO + CHECKSUMS sin autorreferencia",
        "restricciones": [
            "no_modifica_v1",
            "no_modifica_finales",
            "no_api_places",
            "no_commit",
            "no_settings_json",
        ],
    }
    meta_path = REV / "metadata_infraestructura_agentes_skills_v1_1.json"
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    qa_path = REV / "QA_FINAL_INFRAESTRUCTURA_AGENTES_SKILLS_V1_1.md"
    # placeholder; will be overwritten if source exists in docs
    qa_src = DOC / "QA_FINAL_INFRAESTRUCTURA_AGENTES_SKILLS_V1_1.md"
    if qa_src.is_file():
        shutil.copy2(qa_src, qa_path)
    else:
        qa_path.write_text("# QA final V1.1\n\nPendiente generar antes del empaquetado final.\n", encoding="utf-8")

    # Manifest AFTER all pack files (except itself)
    manifest_path = write_manifest_contenido(REV)

    # Internal checksums: manifest + metadata + qa (NOT self-referential content list)
    lines = [
        f"{sha256(manifest_path)}  MANIFEST_CONTENIDO.csv",
        f"{sha256(meta_path)}  metadata_infraestructura_agentes_skills_v1_1.json",
        f"{sha256(qa_path)}  QA_FINAL_INFRAESTRUCTURA_AGENTES_SKILLS_V1_1.md",
    ]
    checksums_inside = REV / "CHECKSUMS_INTERNO.txt"
    checksums_inside.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Re-write manifest to include CHECKSUMS_INTERNO.txt but still not MANIFEST itself
    manifest_path = write_manifest_contenido(REV)
    # Update checksums interno after re-manifest? Manifest hash changes when we add CHECKSUMS_INTERNO
    # Order: write checksums of metadata+qa first without manifest, then final:
    # Final protocol: MANIFEST includes CHECKSUMS_INTERNO that only hashes metadata+qa (not manifest)
    lines2 = [
        f"{sha256(meta_path)}  metadata_infraestructura_agentes_skills_v1_1.json",
        f"{sha256(qa_path)}  QA_FINAL_INFRAESTRUCTURA_AGENTES_SKILLS_V1_1.md",
        f"{sha256(manifest_path)}  MANIFEST_CONTENIDO.csv",
    ]
    checksums_inside.write_text("\n".join(lines2) + "\n", encoding="utf-8")
    # Manifest no longer includes updated checksums interno content hash chain:
    # regenerate manifest once more so CHECKSUMS_INTERNO is listed with final hash
    manifest_path = write_manifest_contenido(REV)
    # Final CHECKSUMS_INTERNO references final manifest hash
    lines3 = [
        f"{sha256(meta_path)}  metadata_infraestructura_agentes_skills_v1_1.json",
        f"{sha256(qa_path)}  QA_FINAL_INFRAESTRUCTURA_AGENTES_SKILLS_V1_1.md",
        f"{sha256(manifest_path)}  MANIFEST_CONTENIDO.csv",
        f"# CHECKSUMS_INTERNO.txt se excluye de su propia lista de hashes",
    ]
    checksums_inside.write_text("\n".join(lines3) + "\n", encoding="utf-8")
    # last manifest includes checksums_interno final bytes
    manifest_path = write_manifest_contenido(REV)
    # Note: after last write_manifest, CHECKSUMS_INTERNO is listed; its content does not include its own hash.
    # Manifest hash is NOT inside MANIFEST rows — good.

    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(REV.rglob("*")):
            if path.is_file():
                arc = "REVISION_INFRAESTRUCTURA_AGENTES_SKILLS_V1_1/" + path.relative_to(REV).as_posix()
                zf.write(path, arcname=arc)

    with zipfile.ZipFile(ZIP_PATH, "r") as zf:
        bad = zf.testzip()
        if bad is not None:
            raise SystemExit(f"ZIP corrupt: {bad}")
        n = len(zf.namelist())

    # External checksums next to ZIP (includes ZIP hash)
    external = OUT_BASE / "CHECKSUMS_SHA256.txt"
    external_lines = [
        f"{sha256(manifest_path)}  REVISION_INFRAESTRUCTURA_AGENTES_SKILLS_V1_1/MANIFEST_CONTENIDO.csv",
        f"{sha256(meta_path)}  REVISION_INFRAESTRUCTURA_AGENTES_SKILLS_V1_1/metadata_infraestructura_agentes_skills_v1_1.json",
        f"{sha256(qa_path)}  REVISION_INFRAESTRUCTURA_AGENTES_SKILLS_V1_1/QA_FINAL_INFRAESTRUCTURA_AGENTES_SKILLS_V1_1.md",
        f"{sha256(ZIP_PATH)}  REVISION_INFRAESTRUCTURA_AGENTES_SKILLS_V1_1.zip",
    ]
    external.write_text("\n".join(external_lines) + "\n", encoding="utf-8")

    # verify no self-row in manifest
    with manifest_path.open(encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("MANIFEST_CONTENIDO.csv"):
                raise SystemExit("ERROR: autorreferencia en MANIFEST_CONTENIDO.csv")

    print(f"REV files: {len([p for p in REV.rglob('*') if p.is_file()])}")
    print(f"ZIP: {ZIP_PATH} ({ZIP_PATH.stat().st_size} bytes) members={n}")
    print(f"ZIP sha256: {sha256(ZIP_PATH)}")
    print(f"External checksums: {external}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
