"""Valida que un informe (md/txt/html/pdf) contenga los KPIs canónicos de su lockfile.

El lockfile es un JSON simple: {"descripcion del KPI": "valor exacto que debe aparecer", ...}
Ejemplo (kpis_lock.json):
    {
      "candidatos depurados": "254",
      "independientes": "173",
      "en cadenas": "81"
    }

Uso:
    .venv/Scripts/python.exe scripts/qa/validate_kpis.py kpis_lock.json INFORME.md [OTRO.pdf ...]

Falla (exit 1) listando cada valor ausente. Evita el drift de números entre regeneraciones
sin tener que re-pegar los KPIs en cada prompt.
"""
import json
import sys
from pathlib import Path


def extract_text(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        import fitz  # PyMuPDF

        doc = fitz.open(path)
        return "\n".join(page.get_text() for page in doc)
    return path.read_text(encoding="utf-8", errors="replace")


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    lock_path = Path(sys.argv[1])
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    failed = False
    for target in sys.argv[2:]:
        path = Path(target)
        if not path.exists():
            print(f"[ERROR] no existe: {path}")
            failed = True
            continue
        text = extract_text(path)
        missing = {k: v for k, v in lock.items() if str(v) not in text}
        if missing:
            failed = True
            print(f"[FALLA] {path}:")
            for k, v in missing.items():
                print(f"   falta '{v}' ({k})")
        else:
            print(f"[OK] {path}: {len(lock)} KPIs presentes")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
