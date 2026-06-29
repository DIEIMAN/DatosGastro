"""Genera los archivos finales de entrega de mercados CABA.

Usa V4_1 como base tecnica sin sobrescribirla. Aplica solo dos ajustes de
entrega: texto breve de la card de pagina 8 y frase final de pagina 14.
No hace requests ni usa APIs.
"""
from __future__ import annotations

import importlib.util
import shutil
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs" / "mercados_caba"
SAN = ROOT / "outputs" / "mercados_caba" / "sanitized"

BASE_BUILDER = ROOT / "src" / "mercados_caba" / "build_pdf_final_v4_1_from_v3.py"

FINAL_PDF = SAN / "MercadosGastroCABA.pdf"
FINAL_SUMMARY = SAN / "ResumenEjecutivo_MercadosGastroCABA.pdf"
FINAL_PACK = SAN / "PACK_MercadosGastroCABA.zip"

README_V4_1 = DOCS / "README_REGENERAR_INFORME_FINAL_V4_1.md"
OPORTUNIDAD_V4_1 = DOCS / "OPORTUNIDAD_GESTION_MERCADOS_CABA_V4_1.md"
ANEXO_METODOLOGIA_V4_1 = DOCS / "ANEXO_FUENTES_Y_METODOLOGIA_MERCADOS_V4_1.md"
OPORTUNIDADES_CSV_V4_1 = SAN / "oportunidades_gestion_mercados_v4_1.csv"
PILOTOS_CSV_V4_1 = SAN / "pilotos_recomendados_mercados_v4_1.csv"
PUBLICOS_CSV_V4_1 = SAN / "publicos_objetivo_mercados_v4_1.csv"

PAGE_8_TEXT = (
    "San Nicolás, Smart Plaza y Mercat Villa Crespo: almuerzo laboral "
    "y salida post-laboral."
)
PAGE_14_TEXT = (
    "Un método replicable que integra registro oficial, sitios propios, señal operativa, "
    "fuente interna y revisión documental para construir una base candidata trazable, "
    "distinguir tipologías y separar con claridad activos identificados, casos en revisión, "
    "cerrados y fuera de alcance. Es una base candidata, no oficial."
)


def load_base_builder():
    spec = importlib.util.spec_from_file_location("mercados_v4_1_builder", BASE_BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"No se pudo importar {BASE_BUILDER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def apply_delivery_overrides(v3_module) -> None:
    fixed_publicos = []
    for title, text, color in v3_module.PUBLICOS_INSIGHTS:
        if title == "Trabajadores / franja post-laboral":
            fixed_publicos.append((title, PAGE_8_TEXT, color))
        else:
            fixed_publicos.append((title, text, color))
    v3_module.PUBLICOS_INSIGHTS = fixed_publicos

    patched_box = v3_module.box

    def box_delivery(fig, x, y, w, h, title, text, kind="resp"):
        if title == "Qué aporta DataGastro":
            text = PAGE_14_TEXT
        return patched_box(fig, x, y, w, h, title, text, kind)

    v3_module.box = box_delivery


def build_pack_final() -> None:
    files = [
        FINAL_PDF,
        FINAL_SUMMARY,
        README_V4_1,
        OPORTUNIDAD_V4_1,
        ANEXO_METODOLOGIA_V4_1,
        OPORTUNIDADES_CSV_V4_1,
        PILOTOS_CSV_V4_1,
        PUBLICOS_CSV_V4_1,
    ]
    missing = [path for path in files if not path.exists()]
    if missing:
        raise FileNotFoundError("Faltan archivos para el pack final:\n" + "\n".join(map(str, missing)))

    with zipfile.ZipFile(FINAL_PACK, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in files:
            zf.write(path, path.relative_to(ROOT).as_posix())


def main() -> int:
    builder = load_base_builder()

    with tempfile.TemporaryDirectory(prefix="mercados_entrega_") as tmp_name:
        tmp = Path(tmp_name)
        v3_module = builder.load_v3_module()
        builder.patch_v3_module(v3_module, tmp)
        apply_delivery_overrides(v3_module)

        meta = v3_module.load_master_meta()
        v3_module.build_pdf_v2(meta)
        v3_module.build_summary_pdf_v2(meta)
        v3_module.build_pdf_v3(meta)

        new_pages = tmp / "new_pages_entrega.pdf"
        builder.build_new_pages(new_pages)

        builder.PDF_V4_1 = FINAL_PDF
        builder.build_final_pdf_with_overlays(v3_module.PDF_V3, new_pages, tmp)
        shutil.copyfile(v3_module.PDF_RESUMEN_V2, FINAL_SUMMARY)

    build_pack_final()

    print(f"ok: {FINAL_PDF}")
    print(f"ok: {FINAL_SUMMARY}")
    print(f"ok: {FINAL_PACK}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
