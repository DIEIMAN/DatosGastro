"""Compara skills canónicas V1.1 / productivas / espejos. No modifica nada."""
from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "outputs" / "infraestructura_agentes_skills_v1_1" / "paridad"
DOC_DIR = ROOT / "docs" / "infraestructura_agentes_skills_v1_1"

# Capas a comparar (nombre skill -> path SKILL.md parent)
LAYERS = {
    "claude_productivo": ROOT / ".claude" / "skills",
    "agents_espejo": ROOT / ".agents" / "skills",
    "v1_docs": ROOT / "docs" / "infraestructura_agentes_skills_v1" / "skills",
    "v1_1_docs": ROOT / "docs" / "infraestructura_agentes_skills_v1_1" / "skills",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def list_skills(base: Path) -> dict[str, Path]:
    if not base.is_dir():
        return {}
    out = {}
    for p in base.iterdir():
        if p.is_dir() and (p / "SKILL.md").is_file():
            out[p.name] = p / "SKILL.md"
    return out


def classify(canon_hash: str | None, other_hash: str | None, other_text: str | None, canon_text: str | None) -> str:
    if other_hash is None:
        return "ausente"
    if canon_hash is None:
        return "extra"
    if other_hash == canon_hash:
        return "identica"
    # wrapper: short file that references docs/skills_claude or canonical path
    if other_text and len(other_text) < 2500 and (
        "docs/skills_claude" in other_text
        or "Contenido canónico" in other_text
        or "POLITICA_OPERATIVA" in other_text
        or "infraestructura_agentes_skills" in other_text
    ):
        return "wrapper_valido"
    return "divergente"


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    layers_skills = {name: list_skills(path) for name, path in LAYERS.items()}

    # Canónico para paridad productiva: docs/skills_claude no son SKILL.md;
    # usamos .claude/skills como referencia de skills productivas Claude,
    # y V1.1 skills como referencia de skills de infra.
    all_names = sorted({n for skills in layers_skills.values() for n in skills})

    rows = []
    for skill in all_names:
        entry = {"skill": skill, "capas": {}}
        texts = {}
        hashes = {}
        for layer, skills in layers_skills.items():
            p = skills.get(skill)
            if p is None:
                entry["capas"][layer] = {"estado": "ausente", "ruta": None, "sha256": None, "bytes": None}
                continue
            text = p.read_text(encoding="utf-8", errors="replace")
            h = sha256(p)
            texts[layer] = text
            hashes[layer] = h
            entry["capas"][layer] = {
                "estado": "presente",
                "ruta": p.relative_to(ROOT).as_posix(),
                "sha256": h,
                "bytes": p.stat().st_size,
            }

        # Comparaciones clave
        claude = hashes.get("claude_productivo")
        agents = hashes.get("agents_espejo")
        imported = hashes.get("agent_skills_imported")
        v11 = hashes.get("v1_1_docs")

        entry["vs_claude"] = {
            "agents_espejo": classify(claude, agents, texts.get("agents_espejo"), texts.get("claude_productivo")),
            "agent_skills_imported": classify(
                claude, imported, texts.get("agent_skills_imported"), texts.get("claude_productivo")
            ),
        }
        entry["vs_v1_1_infra"] = {
            "claude_productivo": classify(v11, claude, texts.get("claude_productivo"), texts.get("v1_1_docs")),
            "agents_espejo": classify(v11, agents, texts.get("agents_espejo"), texts.get("v1_1_docs")),
            "agent_skills_imported": classify(
                v11, imported, texts.get("agent_skills_imported"), texts.get("v1_1_docs")
            ),
        }
        rows.append(entry)

    # Resumen
    summary = {
        "fecha": date.today().isoformat(),
        "capas": {k: str(v.relative_to(ROOT)) if v.exists() else None for k, v in LAYERS.items()},
        "n_skills_union": len(all_names),
        "skills": rows,
        "hallazgos": [],
    }

    # Hallazgos conocidos
    for r in rows:
        s = r["skill"]
        for layer, st in r["vs_claude"].items():
            if st == "divergente":
                summary["hallazgos"].append(f"{s}: {layer} divergente vs claude_productivo")
            if st == "ausente" and r["capas"]["claude_productivo"]["estado"] == "presente":
                summary["hallazgos"].append(f"{s}: ausente en {layer}")
        if r["capas"]["claude_productivo"]["estado"] == "presente" and r["capas"]["agents_espejo"]["estado"] == "ausente":
            if s == "datagastro-qa-pdf":
                summary["hallazgos"].append("datagastro-qa-pdf solo en .claude/skills (esperado pre-promoción)")

    json_path = OUT_DIR / "REPORTE_PARIDAD_SKILLS.json"
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # MD
    lines = [
        "# Reporte de paridad de skills — V1.1",
        "",
        f"Fecha: {summary['fecha']}",
        "",
        "Script: `scripts/infraestructura_agentes_skills_v1_1/check_skills_parity.py`",
        "",
        "Clasificación: `identica` | `wrapper_valido` | `divergente` | `ausente` | `extra`",
        "",
        "## Capas",
        "",
    ]
    for k, v in summary["capas"].items():
        lines.append(f"- **{k}**: `{v}`")
    lines += ["", "## Matriz vs Claude productivo", "", "| skill | agents_espejo |", "| --- | --- |"]
    for r in rows:
        if r["capas"]["claude_productivo"]["estado"] != "presente" and r["capas"]["v1_1_docs"]["estado"] != "presente":
            continue
        lines.append(
            f"| `{r['skill']}` | {r['vs_claude']['agents_espejo']} |"
        )
    lines += ["", "## Hallazgos", ""]
    if summary["hallazgos"]:
        for h in summary["hallazgos"]:
            lines.append(f"- {h}")
    else:
        lines.append("- (sin hallazgos automáticos)")
    lines += [
        "",
        "## Nota",
        "",
        "Este script **no copia ni modifica** skills productivas.",
        "Skills de infraestructura V1.1 (snake_case) no son espejos de datagastro-*; su ausencia en `.claude/skills` es esperada hasta promoción controlada.",
        "",
    ]
    md_path = OUT_DIR / "REPORTE_PARIDAD_SKILLS.md"
    md_path.write_text("\n".join(lines), encoding="utf-8")
    # also copy md to docs
    (DOC_DIR / "REPORTE_PARIDAD_SKILLS.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    print(f"hallazgos: {len(summary['hallazgos'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
