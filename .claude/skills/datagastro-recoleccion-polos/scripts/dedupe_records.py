from __future__ import annotations

import argparse
import json


def main() -> None:
    parser = argparse.ArgumentParser(description="Verificar el motor Splink de vinculación probabilística")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--input-json")
    parser.add_argument("--settings")
    parser.add_argument("--output")
    parser.add_argument("--threshold", type=float, default=0.5)
    args = parser.parse_args()
    try:
        import splink  # noqa: F401
    except ImportError as exc:
        raise RuntimeError("Splink no está operativo en .venv-tools") from exc
    if args.status:
        from importlib.metadata import version

        print(json.dumps({"ok": True, "engine": "splink", "version": version("splink")}))
        return
    parser.error(
        "Este wrapper valida el entorno con --status. Para vincular registros, definir primero "
        "comparaciones, bloqueos, umbral y revisión humana según .claude/skills/dedupe-registros/SKILL.md"
    )


if __name__ == "__main__":
    main()
