"""Hotfix V1.1.1: empaquetado con orden de cierre correcto, UTF-8, dependencias, git, ZIP + reverify.

No modifica política, agentes, skills, adaptadores, E2E, superficies ni punteros.
No sobrescribe packs V1 / V1.1.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOC_HF = ROOT / "docs" / "archive" / "infraestructura_agentes_skills_v1_1_1_hotfix"
OUT_HF = ROOT / "outputs" / "infraestructura_agentes_skills_v1_1_1_hotfix"
SCR_HF = ROOT / "scripts" / "infraestructura_agentes_skills_v1_1_1_hotfix"

# Fuentes V1.1 (solo lectura)
DOC_V11 = ROOT / "docs" / "infraestructura_agentes_skills_v1_1"
OUT_V11 = ROOT / "outputs" / "infraestructura_agentes_skills_v1_1"
SCR_V11 = ROOT / "scripts" / "infraestructura_agentes_skills_v1_1"
DOC_V1 = ROOT / "docs" / "infraestructura_agentes_skills_v1"

REV = OUT_HF / "REVISION_INFRAESTRUCTURA_AGENTES_SKILLS_V1_1_1_HOTFIX"
ZIP_PATH = OUT_HF / "REVISION_INFRAESTRUCTURA_AGENTES_SKILLS_V1_1_1_HOTFIX.zip"

TEXT_SUFFIXES = {".md", ".txt", ".csv", ".json", ".yaml", ".yml", ".py", ".diff"}
SKIP_DIR = {"__pycache__", ".git"}
SKIP_SUF = {".pyc", ".png", ".pdf", ".zip"}  # binarios no auditados como UTF-8 texto


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run_git(args: list[str]) -> str:
    p = subprocess.run(
        ["git", *args],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return p.stdout if p.stdout is not None else ""


def ensure_dirs() -> None:
    for d in (DOC_HF, OUT_HF, SCR_HF, DOC_HF / "evidencia_git"):
        d.mkdir(parents=True, exist_ok=True)


def convert_diff_utf8() -> dict:
    """Convierte PUNTEROS_APLICADOS.diff de UTF-16 a UTF-8 sin BOM (archivo V1.1 solicitado)."""
    src = DOC_V11 / "diffs" / "PUNTEROS_APLICADOS.diff"
    report = {"path": str(src.relative_to(ROOT)).replace("\\", "/"), "action": "none"}
    if not src.is_file():
        report["action"] = "missing"
        return report
    raw = src.read_bytes()
    if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
        text = raw.decode("utf-16")
        # strip BOM if present in decoded text
        if text.startswith("\ufeff"):
            text = text.lstrip("\ufeff")
        src.write_bytes(text.encode("utf-8"))
        report["action"] = "converted_utf16_to_utf8"
        report["sha256_after"] = sha256(src)
    else:
        # already utf-8?
        try:
            src.read_text(encoding="utf-8")
            report["action"] = "already_utf8"
        except UnicodeDecodeError:
            text = raw.decode("utf-16", errors="replace")
            src.write_bytes(text.encode("utf-8"))
            report["action"] = "forced_to_utf8"
    return report


def audit_utf8(paths: list[Path]) -> list[dict]:
    results = []
    for p in paths:
        if not p.is_file():
            continue
        if p.suffix.lower() not in TEXT_SUFFIXES and p.suffix.lower() not in {".diff"}:
            continue
        if any(part in SKIP_DIR for part in p.parts):
            continue
        entry = {"ruta": str(p.relative_to(ROOT)).replace("\\", "/"), "ok_utf8": False, "detalle": ""}
        try:
            data = p.read_bytes()
            if data.startswith(b"\xff\xfe") or data.startswith(b"\xfe\xff"):
                entry["detalle"] = "UTF-16 BOM"
            elif data.startswith(b"\xef\xbb\xbf"):
                # UTF-8 with BOM — decodeable as utf-8-sig; report as warning but ok with utf-8-sig
                data.decode("utf-8-sig")
                entry["ok_utf8"] = True
                entry["detalle"] = "utf-8-sig (BOM presente)"
            else:
                data.decode("utf-8")
                entry["ok_utf8"] = True
                entry["detalle"] = "utf-8"
        except UnicodeDecodeError as e:
            entry["detalle"] = f"UnicodeDecodeError: {e}"
        results.append(entry)
    return results


def collect_text_files_for_audit() -> list[Path]:
    paths: list[Path] = []
    for base in (DOC_V11, DOC_HF, SCR_V11, SCR_HF, DOC_V1):
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if p.is_file() and p.suffix.lower() in TEXT_SUFFIXES:
                paths.append(p)
    # key repo pointers
    for rel in ("AGENTS.md", "CLAUDE.md", "agent_skills/codex/README.md"):
        p = ROOT / rel
        if p.is_file():
            paths.append(p)
    return paths


def write_git_evidence() -> None:
    ev = DOC_HF / "evidencia_git"
    (ev / "GIT_STATUS_SHORT.txt").write_text(run_git(["status", "--short"]) or "(vacío)\n", encoding="utf-8")
    # full infra-related diff (untracked not in diff; include tracked changes)
    patch_infra = run_git(
        [
            "diff",
            "--",
            "docs/infraestructura_agentes_skills_v1_1",
            "docs/archive/infraestructura_agentes_skills_v1_1_1_hotfix",
            "docs/polos_gastro/PROTECTED_SURFACES.yaml",
            "scripts/infraestructura_agentes_skills_v1_1",
            "scripts/infraestructura_agentes_skills_v1_1_1_hotfix",
            "outputs/infraestructura_agentes_skills_v1_1",
            "outputs/infraestructura_agentes_skills_v1_1_1_hotfix",
        ]
    )
    # untracked won't appear; note that
    note = (
        "# Nota: archivos untracked no aparecen en git diff.\n"
        "# Ver GIT_STATUS_SHORT.txt para ?? de carpetas infra.\n\n"
    )
    (ev / "GIT_DIFF_INFRAESTRUCTURA.patch").write_text(note + (patch_infra or "(sin cambios tracked en rutas listadas)\n"), encoding="utf-8")
    patch_ptr = run_git(["diff", "--", "AGENTS.md", "CLAUDE.md", "agent_skills/codex/README.md"])
    (ev / "GIT_DIFF_PUNTEROS.patch").write_text(patch_ptr or "(sin diff en punteros)\n", encoding="utf-8")
    cached = run_git(["diff", "--cached", "--name-only"])
    (ev / "GIT_DIFF_CACHED.txt").write_text(
        cached if cached.strip() else "(vacío — no hay staging)\n",
        encoding="utf-8",
    )


def build_dependencies_csv(dest: Path) -> Path:
    """Inventario de dependencias externas al ZIP (canónicas en el repo)."""
    # (ruta, tipo, version, proposito, requerida, usada_por, obs)
    specs = [
        ("docs/infraestructura_agentes_skills_v1/skills/auditar_evidencia_documental/SKILL.md", "skill_v1", "1", "Procedimiento evidencia", True, "investigador_documental", "Canónico procedimiento"),
        ("docs/infraestructura_agentes_skills_v1/skills/transformar_cartografia_a_presentacion/SKILL.md", "skill_v1", "1", "Presentación cartográfica", True, "cartografo_territorial", ""),
        ("docs/infraestructura_agentes_skills_v1/skills/integrar_handoffs/SKILL.md", "skill_v1", "1", "Handoffs", True, "integrador", ""),
        ("docs/infraestructura_agentes_skills_v1/skills/auditar_entregable_experimental/SKILL.md", "skill_v1", "1", "Cierre experimental", True, "auditor_qa", ""),
        ("docs/infraestructura_agentes_skills_v1/skills/auditar_git_y_archivos_protegidos/SKILL.md", "skill_v1", "1", "Git y protegidos", True, "auditor_qa", ""),
        ("docs/infraestructura_agentes_skills_v1/skills/crear_manifest_hashes_metadata/SKILL.md", "skill_v1", "1", "Manifest (concepto)", True, "empaquetado", "Esquema actualizado en V1.1 docs"),
        ("docs/infraestructura_agentes_skills_v1/skills/crear_paquete_revision_sanitizado/SKILL.md", "skill_v1", "1", "Pack sanitizado", True, "auditor_qa", ""),
        ("docs/infraestructura_agentes_skills_v1/skills/validar_metricas_y_kpis/SKILL.md", "skill_v1", "1", "KPIs", True, "auditor_qa", ""),
        ("docs/infraestructura_agentes_skills_v1/skills/qa_pdf_pagina_por_pagina/SKILL.md", "skill_v1", "1", "QA PDF", True, "auditor_qa", ""),
        ("docs/infraestructura_agentes_skills_v1/skills/gestionar_decisiones_humanas/SKILL.md", "skill_v1", "1", "Decisiones humanas", True, "integrador", ""),
        ("docs/infraestructura_agentes_skills_v1/agents/investigador_documental.md", "agente_v1", "1", "Definición rol", True, "piloto", ""),
        ("docs/infraestructura_agentes_skills_v1/agents/cartografo_territorial.md", "agente_v1", "1", "Definición rol", True, "piloto", ""),
        ("docs/infraestructura_agentes_skills_v1/agents/integrador_tecnico_editorial.md", "agente_v1", "1", "Definición rol", True, "piloto", ""),
        ("docs/infraestructura_agentes_skills_v1/agents/auditor_qa.md", "agente_v1", "1.1", "Definición rol", True, "piloto", ""),
        ("docs/skills_claude/01_datagastro_guardrails.md", "guardrail", "canónico", "Prioridad 0 seguridad", True, "política", ""),
        ("docs/skills_claude/03_privacidad_datos_sensibles.md", "guardrail", "canónico", "Privacidad", True, "política", ""),
        (".claude/skills/datagastro-guardrails/SKILL.md", "skill_productiva", "wrapper", "Claude runtime", False, "Claude Code", "No duplicar en ZIP"),
        (".claude/skills/datagastro-qa-pdf/SKILL.md", "skill_productiva", "wrapper", "QA PDF Claude", False, "Claude Code", "Ausente en espejos Codex"),
        (".claude/skills/datagastro-informes/SKILL.md", "skill_productiva", "wrapper", "Informes", False, "Claude Code", "Puede diverger de espejos"),
        ("AGENTS.md", "entrada_codex", "repo", "Instrucciones multiagente", True, "Codex/agentes", "Puntero V1.1 aplicado"),
        ("CLAUDE.md", "entrada_claude", "repo", "Instrucciones Claude", True, "Claude Code", "Puntero V1.1 aplicado"),
        ("agent_skills/codex/README.md", "entrada_codex", "repo", "Puntero adaptadores Codex", True, "Codex", ""),
        ("scripts/qa/validate_kpis.py", "script_externo", "repo", "Validación KPIs E2E", True, "caso5/caso4", ""),
        ("scripts/qa/pdf_check.py", "script_externo", "repo", "Render PDF", False, "qa_pdf skill", "No re-ejecutado en hotfix"),
        ("docs/polos_gastro/PROTECTED_SURFACES.yaml", "registro", "1", "Superficies Polos", True, "política V1.1", "Fuera del núcleo genérico"),
        ("docs/infraestructura_agentes_skills_v1_1/POLITICA_OPERATIVA_DATAGASTRO_V1_1.md", "politica", "1.1", "Política piloto", True, "todo V1.1", "Canónico V1.1"),
        ("docs/infraestructura_agentes_skills_v1_1/CATALOGO_AGENTES_SKILLS.json", "catalogo", "1.1", "Catálogo machine-readable", True, "adaptadores", ""),
        ("outputs/polos_gastro/historico/REVISION_EVIDENCIA_DOCUMENTAL_POLOS_V1/", "insumo_e2e", "pack", "Caso1 evidencia (directorio)", True, "caso1", "No en ZIP hotfix; en repo"),
        ("outputs/polos_gastro/historico/experimentos/pipeline_hibrido_integracion_v21/puerto_madero_capa_analitica_v21.geojson", "insumo_e2e", "v21", "Caso2 analítica", True, "caso2", "Baseline solo lectura"),
    ]
    rows = []
    for ruta, tipo, ver, prop, req, usada, obs in specs:
        p = ROOT / ruta
        existe = p.exists()
        size = p.stat().st_size if p.is_file() else (sum(f.stat().st_size for f in p.rglob("*") if f.is_file()) if p.is_dir() else 0)
        digest = sha256(p) if p.is_file() else ("DIR" if p.is_dir() else "")
        rows.append(
            {
                "ruta_relativa_repo": ruta.replace("\\", "/"),
                "tipo": tipo,
                "versión": ver,
                "propósito": prop,
                "requerida": "sí" if req else "no",
                "existe": "sí" if existe else "no",
                "tamaño_bytes": size if existe else "",
                "sha256": digest if p.is_file() else ("" if not existe else "N/A_directorio"),
                "usada_por": usada,
                "observaciones": obs,
            }
        )
    out = dest / "DEPENDENCIAS_REFERENCIADAS.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(
            fh,
            fieldnames=[
                "ruta_relativa_repo",
                "tipo",
                "versión",
                "propósito",
                "requerida",
                "existe",
                "tamaño_bytes",
                "sha256",
                "usada_por",
                "observaciones",
            ],
        )
        w.writeheader()
        w.writerows(rows)
    return out


def write_portability_md(dest: Path, n_deps: int) -> None:
    text = f"""# Dependencias y portabilidad — V1.1.1 hotfix

## Qué contiene el ZIP de hotfix

El paquete `REVISION_INFRAESTRUCTURA_AGENTES_SKILLS_V1_1_1_HOTFIX.zip` incluye:

- Documentación de hotfix (este archivo, QA, metadata, esquema de cierre corregido).
- Evidencia Git (status, diffs de punteros e infra, cached vacío).
- Inventario `DEPENDENCIAS_REFERENCIADAS.csv` ({n_deps} filas de datos + cabecera).
- Copia de lectura de artefactos de revisión V1.1 **ya generados** (docs V1.1, scripts V1.1, salidas E2E/paridad) para trazabilidad del piloto.
- Scripts de este hotfix.
- `MANIFEST_CONTENIDO.csv` y `CHECKSUMS_INTERNO.txt` generados con orden de cierre correcto.

## Qué depende del repositorio (no está “cerrado” en el ZIP)

Las **skills y agentes canónicos de procedimiento** viven en:

- `docs/infraestructura_agentes_skills_v1/skills/`
- `docs/infraestructura_agentes_skills_v1/agents/`

La política y catálogo del piloto viven en:

- `docs/infraestructura_agentes_skills_v1_1/`

Los guardrails canónicos largos:

- `docs/skills_claude/`

Las skills productivas de Claude:

- `.claude/skills/`

Entradas de sesión:

- `AGENTS.md`, `CLAUDE.md`, `agent_skills/codex/README.md`

Scripts de QA del repo:

- `scripts/qa/validate_kpis.py`, `scripts/qa/pdf_check.py`

Insumos de casos E2E (solo lectura):

- packs Polos de evidencia e integración técnica en `outputs/polos_gastro/...`

## Qué es canónico (no se duplica)

| Capa | Canónico |
| --- | --- |
| Guardrails | `docs/skills_claude/` |
| Procedimientos skills piloto | `docs/infraestructura_agentes_skills_v1/skills/` |
| Política piloto | `docs/infraestructura_agentes_skills_v1_1/POLITICA_..._V1_1.md` |
| Catálogo | `docs/infraestructura_agentes_skills_v1_1/CATALOGO_AGENTES_SKILLS.json` |
| Superficies Polos | `docs/polos_gastro/PROTECTED_SURFACES.yaml` |
| Empaquetado correcto | `scripts/infraestructura_agentes_skills_v1_1_1_hotfix/` |

## Por qué no se duplican skills en el ZIP

Duplicar crearía una segunda fuente de verdad y reintroduciría el drift entre copias (problema ya auditado entre `.claude/skills`, `.agents/skills` y `agent_skills/claude_imported`).  
El ZIP de revisión es un **paquete de verificación y entrega del piloto**, no un monorepo portable offline.

## Cómo reconstruir / verificar en otra copia del repo

1. Clonar/actualizar el mismo repositorio DataGastro en el mismo commit (o working tree con los mismos archivos).  
2. Verificar filas de `DEPENDENCIAS_REFERENCIADAS.csv` (`existe=sí` y `sha256` si es archivo).  
3. Ejecutar:  
   `.venv/Scripts/python.exe scripts/infraestructura_agentes_skills_v1_1_1_hotfix/empaquetar_y_validar_hotfix.py`  
4. Comparar SHA-256 del ZIP y de `MANIFEST_CONTENIDO.csv` con `CHECKSUMS_INTERNO.txt` / `CHECKSUMS_SHA256.txt`.  
5. Opcional: re-ejecutar E2E V1.1 (`run_casos_e2e_v1_1.py`) si se necesitan regenerar salidas; el hotfix no las redefine.

## Causa del checksum V1.1 incorrecto

El empaquetador V1.1 escribía `CHECKSUMS_INTERNO.txt` con el hash del manifest y **después** regeneraba `MANIFEST_CONTENIDO.csv` (para incluir el propio checksums o un estado posterior), cambiando el hash del manifest sin actualizar la línea en `CHECKSUMS_INTERNO.txt`.  
El hotfix fija el orden: contenidos → metadata/QA → **manifest definitivo** → **checksums sobre archivos definitivos** → ZIP → reverify sobre extracción.
"""
    (dest / "DEPENDENCIAS_Y_PORTABILIDAD.md").write_text(text, encoding="utf-8")


def copy_tree(src: Path, dst: Path) -> None:
    if not src.exists():
        return
    for path in src.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIR for part in path.parts):
            continue
        if path.suffix in SKIP_SUF and path.suffix == ".pyc":
            continue
        # skip heavy optional qa png trees if any
        if "caso_b_qa_png" in path.parts:
            continue
        rel = path.relative_to(src)
        target = dst / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)


def write_manifest(pack_root: Path) -> Path:
    """Todas las filas excepto MANIFEST_CONTENIDO.csv y CHECKSUMS_INTERNO.txt (meta de cierre)."""
    exclude = {"MANIFEST_CONTENIDO.csv", "CHECKSUMS_INTERNO.txt", "CHECKSUMS_SHA256.txt"}
    rows = []
    for path in sorted(pack_root.rglob("*")):
        if not path.is_file():
            continue
        if path.name in exclude:
            continue
        rel = path.relative_to(pack_root).as_posix()
        rows.append({"ruta_relativa": rel, "bytes": path.stat().st_size, "sha256": sha256(path)})
    out = pack_root / "MANIFEST_CONTENIDO.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["ruta_relativa", "bytes", "sha256"])
        w.writeheader()
        w.writerows(rows)
    return out


def write_checksums_interno(pack_root: Path, manifest: Path, meta: Path, qa: Path) -> Path:
    """Hashes de archivos definitivos. CHECKSUMS_INTERNO no se lista a sí mismo."""
    lines = [
        f"{sha256(manifest)}  MANIFEST_CONTENIDO.csv",
        f"{sha256(meta)}  metadata_infraestructura_agentes_skills_v1_1_1_hotfix.json",
        f"{sha256(qa)}  QA_FINAL_INFRAESTRUCTURA_AGENTES_SKILLS_V1_1_1_HOTFIX.md",
        "# CHECKSUMS_INTERNO.txt se excluye de su propia lista",
    ]
    out = pack_root / "CHECKSUMS_INTERNO.txt"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def validate_manifest(pack_root: Path, manifest: Path) -> None:
    with manifest.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        if r["ruta_relativa"] in ("MANIFEST_CONTENIDO.csv", "CHECKSUMS_INTERNO.txt"):
            raise SystemExit(f"Manifest no debe listar meta de cierre: {r['ruta_relativa']}")
        p = pack_root / r["ruta_relativa"]
        if not p.is_file():
            raise SystemExit(f"Falta archivo del manifest: {r['ruta_relativa']}")
        if str(p.stat().st_size) != str(r["bytes"]) and int(r["bytes"]) != p.stat().st_size:
            raise SystemExit(f"Tamaño mismatch: {r['ruta_relativa']}")
        if sha256(p) != r["sha256"]:
            raise SystemExit(f"Hash mismatch en pack: {r['ruta_relativa']}")
    # every non-meta file must be listed
    listed = {r["ruta_relativa"] for r in rows}
    for path in pack_root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(pack_root).as_posix()
        if path.name in ("MANIFEST_CONTENIDO.csv", "CHECKSUMS_INTERNO.txt"):
            continue
        if rel not in listed:
            raise SystemExit(f"Archivo no listado en manifest: {rel}")


def validate_checksums_interno(pack_root: Path) -> dict:
    path = pack_root / "CHECKSUMS_INTERNO.txt"
    text = path.read_text(encoding="utf-8")
    results = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        digest, name = line.split(None, 1)
        name = name.strip()
        if name == "CHECKSUMS_INTERNO.txt":
            raise SystemExit("CHECKSUMS_INTERNO no debe hashearse a sí mismo")
        f = pack_root / name
        if not f.is_file():
            raise SystemExit(f"Checksum apunta a faltante: {name}")
        real = sha256(f)
        if real != digest:
            raise SystemExit(f"Checksum interno inválido para {name}: esperado {digest} real {real}")
        results[name] = real
    return results


def no_absolute_paths_in_zip_names(names: list[str]) -> None:
    for n in names:
        if n.startswith("/") or (len(n) > 2 and n[1] == ":"):
            raise SystemExit(f"Ruta absoluta en ZIP: {n}")
        if "\\" in n:
            raise SystemExit(f"Backslash en arcname ZIP: {n}")


def extract_and_reverify(zip_path: Path) -> dict:
    with tempfile.TemporaryDirectory(prefix="dg_hotfix_") as tmp:
        tmp_path = Path(tmp)
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(tmp_path)
            names = zf.namelist()
        # find pack root
        roots = [p for p in tmp_path.iterdir() if p.is_dir()]
        if len(roots) != 1:
            # flat?
            pack = tmp_path
        else:
            pack = roots[0]
        manifest = pack / "MANIFEST_CONTENIDO.csv"
        if not manifest.is_file():
            raise SystemExit("Extracción: falta MANIFEST_CONTENIDO.csv")
        validate_manifest(pack, manifest)
        ch = validate_checksums_interno(pack)
        return {
            "extract_ok": True,
            "members": len(names),
            "checksums_ok": ch,
            "manifest_hash_extracted": sha256(manifest),
        }


def main() -> int:
    ensure_dirs()
    os.chdir(ROOT)

    # 1) Convert diff encoding in V1.1 (explicit request)
    diff_report = convert_diff_utf8()
    (DOC_HF / "ENCODING_DIFF_PUNTEROS.json").write_text(
        json.dumps(diff_report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    # 2) UTF-8 audit
    audit = audit_utf8(collect_text_files_for_audit())
    bad = [a for a in audit if not a["ok_utf8"]]
    (DOC_HF / "AUDITORIA_ENCODING_UTF8.json").write_text(
        json.dumps({"total": len(audit), "fallas": bad, "items": audit}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    if bad:
        # still continue after convert; re-audit critical
        audit2 = audit_utf8(collect_text_files_for_audit())
        bad2 = [a for a in audit2 if not a["ok_utf8"]]
        if bad2:
            raise SystemExit(f"UTF-8 fallas: {bad2}")

    # 3) Git evidence (does not modify AGENTS/CLAUDE)
    write_git_evidence()

    # 4) Dependencies docs in DOC_HF first
    n_specs_placeholder = 0
    write_portability_md(DOC_HF, n_deps=0)  # rewritten after csv count
    dep_tmp = DOC_HF
    dep_csv = build_dependencies_csv(dep_tmp)
    with dep_csv.open(encoding="utf-8") as fh:
        n_deps = sum(1 for _ in csv.DictReader(fh))
    write_portability_md(DOC_HF, n_deps=n_deps)

    # 5) Build pack directory
    if REV.exists():
        shutil.rmtree(REV)
    REV.mkdir(parents=True)

    # Hotfix docs
    copy_tree(DOC_HF, REV / "docs_hotfix")
    # V1.1 review artifacts (read-only snapshot into pack)
    if DOC_V11.exists():
        copy_tree(DOC_V11, REV / "snapshot_v1_1" / "docs")
    if SCR_V11.exists():
        copy_tree(SCR_V11, REV / "snapshot_v1_1" / "scripts")
    for sub in ("casos_e2e", "paridad"):
        src = OUT_V11 / sub
        if src.exists():
            copy_tree(src, REV / "snapshot_v1_1" / "outputs" / sub)
    # hotfix scripts
    copy_tree(SCR_HF, REV / "scripts_hotfix")

    (REV / "README.md").write_text(
        """# REVISION_INFRAESTRUCTURA_AGENTES_SKILLS_V1_1_1_HOTFIX

Hotfix de empaquetado y trazabilidad. No cambia política, agentes, skills, adaptadores ni E2E.

## Contenido

- `docs_hotfix/` — dependencias, encoding, evidencia Git, QA
- `snapshot_v1_1/` — copia de lectura de artefactos V1.1 del repo
- `scripts_hotfix/` — empaquetador validador
- `MANIFEST_CONTENIDO.csv` — sin autorreferencia; no lista CHECKSUMS_INTERNO
- `CHECKSUMS_INTERNO.txt` — hashes de manifest + metadata + QA (no de sí mismo)

## Orden de cierre

contenidos → metadata/QA → manifest definitivo → checksums → ZIP → extracción y reverify
""",
        encoding="utf-8",
    )

    # Also place deps at pack root for easy access
    shutil.copy2(DOC_HF / "DEPENDENCIAS_REFERENCIADAS.csv", REV / "DEPENDENCIAS_REFERENCIADAS.csv")
    shutil.copy2(DOC_HF / "DEPENDENCIAS_Y_PORTABILIDAD.md", REV / "DEPENDENCIAS_Y_PORTABILIDAD.md")
    for name in ("GIT_STATUS_SHORT.txt", "GIT_DIFF_INFRAESTRUCTURA.patch", "GIT_DIFF_PUNTEROS.patch", "GIT_DIFF_CACHED.txt"):
        src = DOC_HF / "evidencia_git" / name
        if src.is_file():
            (REV / "evidencia_git").mkdir(exist_ok=True)
            shutil.copy2(src, REV / "evidencia_git" / name)

    # --- Orden de cierre correcto ---
    # a) metadata + QA definitivos
    meta = {
        "nombre": "REVISION_INFRAESTRUCTURA_AGENTES_SKILLS_V1_1_1_HOTFIX",
        "fecha": date.today().isoformat(),
        "version_infra": "1.1.1-hotfix",
        "corrige": [
            "CHECKSUMS_INTERNO desfasado respecto de MANIFEST",
            "PUNTEROS_APLICADOS.diff UTF-16 → UTF-8",
            "Dependencias externas inventariadas sin duplicar skills",
            "Evidencia Git UTF-8 y reverify post-ZIP",
        ],
        "no_modifica": [
            "politica_v1_1",
            "agentes",
            "skills",
            "adaptadores",
            "casos_e2e",
            "protected_surfaces",
            "punteros_agentes_claude",
            "settings_json",
        ],
        "manifest_hash_v1_1_incorrecto_en_checksums": "aba38d7c25cae33c1413fa7ddbb4de6bcac3a274281c85d36f60c1cb928f6c80",
        "manifest_hash_v1_1_real_empaquetado": "d480685d63d376aac4368607575dce2b4b300cee0ce4f98ffc7137206d83ba5c",
    }
    meta_path = REV / "metadata_infraestructura_agentes_skills_v1_1_1_hotfix.json"
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    qa_text = f"""# QA final — INFRAESTRUCTURA_AGENTES_SKILLS_V1_1_1_HOTFIX

Fecha: {date.today().isoformat()}
Estado: **HOTFIX DE EMPAQUETADO APROBABLE / PILOTO**

## Controles

| control | resultado |
| --- | --- |
| Manifest filas válidas | ver validación automática del script |
| Checksums internos válidos | ver validación automática |
| Encoding UTF-8 textos auditados | ver AUDITORIA_ENCODING_UTF8.json |
| Diff punteros UTF-8 | convertido si era UTF-16 |
| ZIP íntegro + extracción reverify | ver salida del script |
| Rutas absolutas en ZIP | prohibidas / validadas |
| `.claude/settings.json` | no tocado por este hotfix |
| Política / agentes / skills / E2E | no modificados |
| staging | debe estar vacío |
| commit / push | no |

## Causa del bug V1.1

`CHECKSUMS_INTERNO.txt` se firmó con el hash del manifest y luego el empaquetador **regeneró** `MANIFEST_CONTENIDO.csv`, invalidando la firma sin actualizar el checksums.

## Hash de referencia V1.1

- Incorrecto en CHECKSUMS_INTERNO: `aba38d7c25cae33c1413fa7ddbb4de6bcac3a274281c85d36f60c1cb928f6c80`
- Real del manifest empaquetado: `d480685d63d376aac4368607575dce2b4b300cee0ce4f98ffc7137206d83ba5c`
"""
    qa_path = REV / "QA_FINAL_INFRAESTRUCTURA_AGENTES_SKILLS_V1_1_1_HOTFIX.md"
    qa_path.write_text(qa_text, encoding="utf-8")
    # mirror QA into docs_hotfix for repo docs
    (DOC_HF / "QA_FINAL_INFRAESTRUCTURA_AGENTES_SKILLS_V1_1_1_HOTFIX.md").write_text(qa_text, encoding="utf-8")

    # b) manifest definitivo (no incluye MANIFEST ni CHECKSUMS_INTERNO)
    manifest_path = write_manifest(REV)

    # c) checksums sobre archivos definitivos (manifest ya final; no se regenera después)
    checksums_path = write_checksums_interno(REV, manifest_path, meta_path, qa_path)

    # d) validaciones pre-ZIP
    validate_manifest(REV, manifest_path)
    ch = validate_checksums_interno(REV)
    if ch["MANIFEST_CONTENIDO.csv"] != sha256(manifest_path):
        raise SystemExit("invariante roto: checksum manifest")

    # e) staging check
    cached = run_git(["diff", "--cached", "--name-only"]).strip()
    if cached:
        raise SystemExit(f"Hay staging: {cached}")

    # f) ZIP
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(REV.rglob("*")):
            if path.is_file():
                arc = "REVISION_INFRAESTRUCTURA_AGENTES_SKILLS_V1_1_1_HOTFIX/" + path.relative_to(REV).as_posix()
                zf.write(path, arcname=arc)
        names = zf.namelist()
    no_absolute_paths_in_zip_names(names)
    with zipfile.ZipFile(ZIP_PATH, "r") as zf:
        bad = zf.testzip()
        if bad is not None:
            raise SystemExit(f"ZIP corrupt: {bad}")

    # g) extract + reverify
    reverify = extract_and_reverify(ZIP_PATH)

    # h) external checksums next to ZIP
    external = OUT_HF / "CHECKSUMS_SHA256.txt"
    external.write_text(
        "\n".join(
            [
                f"{sha256(manifest_path)}  REVISION_INFRAESTRUCTURA_AGENTES_SKILLS_V1_1_1_HOTFIX/MANIFEST_CONTENIDO.csv",
                f"{sha256(meta_path)}  REVISION_INFRAESTRUCTURA_AGENTES_SKILLS_V1_1_1_HOTFIX/metadata_infraestructura_agentes_skills_v1_1_1_hotfix.json",
                f"{sha256(qa_path)}  REVISION_INFRAESTRUCTURA_AGENTES_SKILLS_V1_1_1_HOTFIX/QA_FINAL_INFRAESTRUCTURA_AGENTES_SKILLS_V1_1_1_HOTFIX.md",
                f"{sha256(ZIP_PATH)}  REVISION_INFRAESTRUCTURA_AGENTES_SKILLS_V1_1_1_HOTFIX.zip",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    report = {
        "diff_encoding": diff_report,
        "utf8_fallas": bad,
        "manifest_hash": sha256(manifest_path),
        "manifest_rows": sum(1 for _ in manifest_path.open(encoding="utf-8")) - 1,
        "checksums_interno": ch,
        "zip_size": ZIP_PATH.stat().st_size,
        "zip_sha256": sha256(ZIP_PATH),
        "zip_members": len(names),
        "reverify": reverify,
        "n_dependencias": n_deps,
        "staging_empty": True,
    }
    (OUT_HF / "HOTFIX_VALIDATION_REPORT.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    # also store report in pack was already zipped — write next to zip only is fine
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
