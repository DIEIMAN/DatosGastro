"""Hook Stop: recuerda el QA visual obligatorio de PDFs (skill datagastro-qa-pdf).

Busca PDFs bajo outputs/ modificados en las ultimas ocho horas que no tengan al lado una carpeta
`qa_png_<nombre>/` mas nueva que el PDF (la que produce scripts/qa/pdf_check.py). Si encuentra
alguno, devuelve un systemMessage con la lista. No bloquea: avisa. Sale siempre con 0.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
VENTANA_S = 8 * 3600
SALTAR = {"historico", "analisis_interno", "_tmp_candidato", "qa_png_", "raster_pages"}


def main() -> int:
    try:
        json.load(sys.stdin)
    except Exception:
        pass
    ahora = time.time()
    sin_qa: list[str] = []
    base = RAIZ / "outputs"
    if not base.exists():
        return 0
    for raiz, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if not any(d.startswith(s) for s in SALTAR)]
        for f in files:
            if not f.lower().endswith(".pdf"):
                continue
            p = Path(raiz) / f
            try:
                m = p.stat().st_mtime
            except OSError:
                continue
            if ahora - m > VENTANA_S:
                continue
            qa = p.parent / f"qa_png_{p.stem}"
            if qa.is_dir() and qa.stat().st_mtime >= m - 60:
                continue
            sin_qa.append(p.relative_to(RAIZ).as_posix())
    if sin_qa:
        msg = ("QA visual pendiente (datagastro-qa-pdf): PDFs generados en las ultimas 8 h sin "
               "renderizar: " + "; ".join(sin_qa[:6]) +
               (f" (+{len(sin_qa) - 6} mas)" if len(sin_qa) > 6 else "") +
               ". Correr .venv/Scripts/python.exe scripts/qa/pdf_check.py <pdf> y mirar las paginas.")
        sys.stdout.write(json.dumps({"systemMessage": msg}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
