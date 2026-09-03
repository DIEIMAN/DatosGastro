"""Hook PreToolUse (Bash | PowerShell): hace cumplir en codigo tres guardrails de CLAUDE.md.

Lee el JSON del hook por stdin y sale con codigo 2 (bloquear, el mensaje de stderr vuelve al
asistente) cuando el comando:

  1. escribe en Google Drive (guardrail 1: G:\\My Drive y G:\\.shortcut-targets-by-id son solo
     lectura); leer, listar o copiar DESDE ahi sigue permitido;
  2. borra, mueve o revierte superficies protegidas del pipeline (guardrail 2 y 9):
     data/processed, data/analytics, src/build_model.py, src/build_analytics.py,
     src/validate_model.py, dashboard/, notebooks/;
  3. invoca `python`, `python3`, `pip` o `py` a secas (el Python de Microsoft Store pisa al del
     proyecto): hay que usar .venv/Scripts/python.exe o .venv-tools/Scripts/python.exe.

Cualquier otro caso sale con 0 y no dice nada. Nunca lanza excepciones hacia afuera: ante un
JSON raro, deja pasar (exit 0) para no romper la sesion.
"""
from __future__ import annotations

import json
import re
import shlex
import sys

DRIVE = re.compile(r"(?:g:/|/g/)(?:my drive|\.shortcut-targets-by-id)", re.I)
WRITE_VERBS = re.compile(
    r"(?:^|[\s;&|(])(?:rm|rmdir|mv|del|erase|ren|rename|mkdir|touch|tee|"
    r"remove-item|move-item|new-item|out-file|set-content|add-content|clear-content|"
    r"rename-item|ri|rd|mi|ni)(?:\s|$)|>>?",
    re.I,
)
COPY_VERBS = re.compile(r"(?:^|[\s;&|(])(?:cp|copy|copy-item|cpi|robocopy|xcopy)(?:\s|$)", re.I)

PROTEGIDAS = re.compile(
    r"(?:^|[\s\"'=/(])(?:data/processed|data/analytics|src/build_model\.py|"
    r"src/build_analytics\.py|src/validate_model\.py|dashboard(?:/|\b)|notebooks(?:/|\b))",
    re.I,
)
DESTRUCTIVOS = re.compile(
    r"(?:^|[\s;&|(])(?:rm|rmdir|del|erase|remove-item|ri|rd|move-item|mi|mv|"
    r"git\s+rm|git\s+mv|git\s+clean|git\s+reset\s+--hard|git\s+checkout\s+--|git\s+restore)(?:\s|$)",
    re.I,
)

PYTHON_PELADO = re.compile(r"(?:^|[\s;&|(`]|\$\()(?:python3?|pip3?|py)(?:\.exe)?(?:\s|$)", re.I)
PROBE = re.compile(r"(?:command\s+-v|which|where(?:\.exe)?|get-command|type)\s+(?:python3?|pip3?|py)\b", re.I)
VENV_OK = re.compile(r"(?:\.venv|venv-tools|agent-tools|agent-reach)", re.I)


def drive_write(cmd: str) -> bool:
    if not DRIVE.search(cmd):
        return False
    if WRITE_VERBS.search(cmd):
        return True
    if COPY_VERBS.search(cmd):
        # cp ORIGEN DESTINO: si la ruta de Drive es el ultimo argumento, es destino -> escritura.
        try:
            toks = shlex.split(cmd, posix=True)
        except ValueError:
            toks = cmd.split()
        return bool(toks) and bool(DRIVE.search(toks[-1].replace("\\", "/")))
    return False


def toca_protegidas(cmd: str) -> bool:
    return bool(DESTRUCTIVOS.search(cmd) and PROTEGIDAS.search(cmd))


def python_pelado(cmd: str) -> bool:
    if VENV_OK.search(cmd) or PROBE.search(cmd):
        return False
    return bool(PYTHON_PELADO.search(cmd))


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    tool = str(data.get("tool_name", ""))
    if tool not in {"Bash", "PowerShell"}:
        return 0
    raw = data.get("tool_input", {}) or {}
    cmd = str(raw.get("command", "") or "")
    if not cmd.strip():
        return 0
    norm = cmd.replace("\\", "/")

    if drive_write(norm):
        sys.stderr.write(
            "BLOQUEADO (guardrail 1): Google Drive es solo lectura. No se escribe, borra ni mueve "
            "nada en G:\\My Drive ni G:\\.shortcut-targets-by-id. Leer o copiar desde ahi hacia el "
            "proyecto si esta permitido.\n"
        )
        return 2
    if toca_protegidas(norm):
        sys.stderr.write(
            "BLOQUEADO (guardrails 2 y 9): el comando borra, mueve o revierte una superficie "
            "protegida (data/processed, data/analytics, src/build_*.py, src/validate_model.py, "
            "dashboard/, notebooks/). Requiere permiso explicito de Diego; proponer el plan y "
            "esperar confirmacion.\n"
        )
        return 2
    if python_pelado(norm):
        sys.stderr.write(
            "BLOQUEADO (entorno): `python`/`pip` a secas resuelve al Python de Microsoft Store o a "
            "un venv ajeno. Usar .venv/Scripts/python.exe (pipeline) o "
            ".venv-tools/Scripts/python.exe (recoleccion).\n"
        )
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
