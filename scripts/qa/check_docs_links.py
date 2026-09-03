"""Verifica que las rutas del repo citadas en los documentos de navegacion existan.

    .venv/Scripts/python.exe scripts/qa/check_docs_links.py            # sale con 1 si hay rotas
    .venv/Scripts/python.exe scripts/qa/check_docs_links.py --todo     # tambien docs/**/*.md

Mira CLAUDE.md, AGENTS.md, README.md, docs/README.md, docs/revisiones/HANDOFF_ACTUAL.md,
docs/skills_claude/*.md, docs/*/ESTADO.md y las skills de .claude/skills. Extrae rutas con forma
`carpeta/...` de las carpetas conocidas del repo y las prueba con exists(). Los globs (`*`, `<`)
y las rutas de ejemplo (`<rubro>`, `...`) se saltean. Solo lectura.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
CARPETAS = "docs|scripts|src|outputs|data|tests|config|schemas|sql|dashboard|notebooks|agent_skills|\\.claude|\\.agents"
RUTA = re.compile(rf"(?<![\w/.-])((?:{CARPETAS})/[\w\-./()]+)")
NAVEGACION = [
    "CLAUDE.md", "AGENTS.md", "README.md", "docs/README.md", "docs/revisiones/HANDOFF_ACTUAL.md",
    *[p.relative_to(RAIZ).as_posix() for p in (RAIZ / "docs" / "skills_claude").glob("*.md")],
    *[p.relative_to(RAIZ).as_posix() for p in (RAIZ / "docs").glob("*/ESTADO.md")],
    *[p.relative_to(RAIZ).as_posix() for p in (RAIZ / ".claude" / "skills").glob("*/SKILL.md")],
]


# Rutas que los documentos nombran como propuesta, ejemplo o historia ("antes vivia en"), no como
# referencia vigente. Se agregan aca cuando aparecen; si una deja de ser propuesta, se saca.
PROPUESTAS_O_HISTORICAS = {
    ".claude/agents", "outputs/_prueba", "scripts/cafecito/archive", "data/fuentes_internas/mercados",
    "docs/mercados", "outputs/mercados", "outputs/analisis_interno/chroma", "outputs/casas_pastas_",
}
PREFIJO_INCOMPLETO = re.compile(r"(?:_|/\d\d|\.\*)$")


def rutas_en(texto: str) -> set[str]:
    out = set()
    for m in RUTA.finditer(texto):
        r = m.group(1).rstrip(".,;:)").rstrip("/")
        if any(c in r for c in "*<>…") or "..." in r or PREFIJO_INCOMPLETO.search(r):
            continue
        if r in PROPUESTAS_O_HISTORICAS:
            continue
        out.add(r)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--todo", action="store_true", help="revisar tambien todos los docs/**/*.md")
    args = ap.parse_args()
    archivos = list(NAVEGACION)
    if args.todo:
        archivos += [p.relative_to(RAIZ).as_posix() for p in (RAIZ / "docs").rglob("*.md")
                     if "archive" not in p.parts and "polos_gastro" not in p.parts]
    rotas: list[tuple[str, str]] = []
    for a in dict.fromkeys(archivos):
        p = RAIZ / a
        if not p.exists():
            rotas.append((a, "(el propio documento no existe)"))
            continue
        for r in sorted(rutas_en(p.read_text(encoding="utf-8", errors="replace"))):
            if not (RAIZ / r).exists() and not any(RAIZ.glob(r + "*")):
                rotas.append((a, r))
    if rotas:
        print(f"{len(rotas)} rutas rotas:")
        for a, r in rotas:
            print(f"  {a}: {r}")
        return 1
    print(f"OK: {len(archivos)} documentos, ninguna ruta rota.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
