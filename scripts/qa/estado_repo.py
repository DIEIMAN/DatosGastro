"""Estado del repositorio en veinte lineas, solo lectura.

    .venv/Scripts/python.exe scripts/qa/estado_repo.py            # informe completo (con pesos)
    .venv/Scripts/python.exe scripts/qa/estado_repo.py --sesion   # version corta para SessionStart

Que muestra: handoff vigente (HANDOFF_ACTUAL.md y el HANDOFF_* mas reciente por la fecha del
nombre, no por mtime), archivos modificados partidos en "solo fin de linea" y "cambio real",
sin trackear por directorio, commits sin push, dias desde el ultimo commit, edad del grafo de
graphify frente al ultimo commit en scripts/ o src/, y en modo completo el peso de la raiz y de
outputs/. No modifica nada.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from collections import Counter
from datetime import date, datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
EXCLUIR = {".git", ".venv", ".venv-tools", "node_modules", ".agent-tools"}
FECHA_EN_NOMBRE = re.compile(r"(\d{4})_(\d{2})_(\d{2})\.md$")


def git(*args: str) -> str:
    try:
        return subprocess.run(
            ["git", "-c", "core.quotepath=false", *args],
            cwd=RAIZ, capture_output=True, text=True, encoding="utf-8", errors="replace",
        ).stdout
    except Exception:
        return ""


def handoffs() -> list[str]:
    out: list[str] = []
    actual = RAIZ / "docs" / "revisiones" / "HANDOFF_ACTUAL.md"
    if actual.exists():
        out.append(f"Handoff actual: {actual.relative_to(RAIZ).as_posix()}")
        for linea in actual.read_text(encoding="utf-8", errors="replace").splitlines():
            if linea.startswith("|") and not linea.startswith("|--") and "Hilo" not in linea:
                out.append("   " + linea.strip())
    candidatos = []
    for p in (RAIZ / "docs" / "revisiones").glob("HANDOFF_*.md"):
        m = FECHA_EN_NOMBRE.search(p.name)
        if m and p.name != "HANDOFF_ACTUAL.md":
            candidatos.append((date(int(m[1]), int(m[2]), int(m[3])), p.name))
    if candidatos:
        f, n = max(candidatos)
        out.append(f"Handoff mas reciente por fecha del nombre: docs/revisiones/{n} ({f.isoformat()})")
    return out


def estado_git() -> list[str]:
    out: list[str] = []
    status = git("status", "--short").splitlines()
    mod = [l[3:] for l in status if l[:2].strip() in {"M", "MM", "AM"}]
    unt = [l[3:] for l in status if l.startswith("??")]
    reales = {l.split("\t")[2] for l in git("diff", "-w", "--numstat").splitlines()
              if l and (l.split("\t")[0] not in {"0"} or l.split("\t")[1] not in {"0"})}
    solo_eol = len([m for m in mod if m not in reales])
    out.append(f"Modificados: {len(mod)} ({len(reales)} con cambio real, {solo_eol} solo fin de linea)")
    if unt:
        por_dir = Counter(p.split("/")[0] + ("/" + p.split("/")[1] if p.count("/") > 1 else "") for p in unt)
        top = ", ".join(f"{d} ({n})" for d, n in por_dir.most_common(6))
        out.append(f"Sin trackear: {len(unt)} entradas -> {top}")
    rama = git("rev-parse", "--abbrev-ref", "HEAD").strip()
    upstream = git("rev-parse", "--abbrev-ref", "@{u}").strip()
    if upstream:
        ahead = git("rev-list", "--count", f"{upstream}..HEAD").strip() or "0"
        out.append(f"Rama {rama}: {ahead} commits sin push a {upstream}")
    else:
        out.append(f"Rama {rama}: sin upstream configurado")
    ultimo = git("log", "-1", "--format=%cs %s").strip()
    if ultimo:
        f = datetime.strptime(ultimo[:10], "%Y-%m-%d").date()
        out.append(f"Ultimo commit: hace {(date.today() - f).days} dias -> {ultimo[:90]}")
    return out


def estado_graphify() -> list[str]:
    g = RAIZ / ".graphify"
    if not g.exists():
        return []
    reporte = g / "GRAPH_REPORT.md"
    if not reporte.exists():
        return [".graphify/ existe pero sin GRAPH_REPORT.md: correr `graphify update .` o ignorarlo"]
    grafo = datetime.fromtimestamp(reporte.stat().st_mtime).date()
    ult = git("log", "-1", "--format=%cs", "--", "scripts", "src").strip()
    if ult:
        commits = git("log", "--oneline", f"--since={grafo.isoformat()}", "--", "scripts", "src").count("\n")
        if commits:
            return [f"graphify: grafo del {grafo.isoformat()}, {commits} commits de scripts/src despues -> `graphify update .`"]
        return [f"graphify: grafo del {grafo.isoformat()}, al dia"]
    return []


def peso(p: Path) -> tuple[int, int]:
    total = n = 0
    for raiz, dirs, files in os.walk(p):
        dirs[:] = [d for d in dirs if d not in EXCLUIR]
        for f in files:
            try:
                total += (Path(raiz) / f).stat().st_size
                n += 1
            except OSError:
                pass
    return total, n


def mb(x: int) -> str:
    return f"{x / 1_048_576:,.0f} MB" if x < 1_073_741_824 else f"{x / 1_073_741_824:,.1f} GB"


def pesos() -> list[str]:
    out = ["", "Peso por directorio de la raiz (sin .git, .venv, .venv-tools, node_modules, .agent-tools):"]
    filas = []
    for d in sorted(RAIZ.iterdir()):
        if d.is_dir() and d.name not in EXCLUIR:
            t, n = peso(d)
            filas.append((t, n, d.name))
    for t, n, nombre in sorted(filas, reverse=True)[:14]:
        out.append(f"   {mb(t):>9}  {n:>6} archivos  {nombre}/")
    out.append("outputs/ por subcarpeta:")
    filas = []
    for d in sorted((RAIZ / "outputs").iterdir()):
        if d.is_dir():
            t, n = peso(d)
            filas.append((t, n, d.name))
    for t, n, nombre in sorted(filas, reverse=True)[:10]:
        out.append(f"   {mb(t):>9}  {n:>6} archivos  outputs/{nombre}/")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sesion", action="store_true", help="version corta para el hook de SessionStart")
    args = ap.parse_args()
    lineas = ["== Estado del repo DataGastro =="]
    lineas += handoffs()
    lineas += estado_git()
    lineas += estado_graphify()
    if not args.sesion:
        lineas += pesos()
    sys.stdout.write("\n".join(lineas) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
