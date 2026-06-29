"""Valida la version comparativa con horarios documentados.

No hace requests ni usa APIs. Controla entregables, paginas, CSV/anexo de
horarios, conteos, itinerantes sin horario fijo unico, render visual y pack.
"""
from __future__ import annotations

import csv
import re
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs" / "mercados_caba"
SAN = ROOT / "outputs" / "mercados_caba" / "sanitized"

PDF = SAN / "MercadosGastroCABA_con_horarios.pdf"
SUMMARY = SAN / "ResumenEjecutivo_MercadosGastroCABA_con_horarios.pdf"
PACK = SAN / "PACK_MercadosGastroCABA_con_horarios.zip"
HORARIOS_CSV = SAN / "horarios_documentados_mercados_vfinal.csv"
ANEXO_HORARIOS = DOCS / "ANEXO_HORARIOS_DOCUMENTADOS_MERCADOS.md"
QA_DIR = SAN / "qa_final_con_horarios_png"

EXPECTED_PACK_FILES = [
    "outputs/mercados_caba/sanitized/MercadosGastroCABA_con_horarios.pdf",
    "outputs/mercados_caba/sanitized/ResumenEjecutivo_MercadosGastroCABA_con_horarios.pdf",
    "docs/mercados_caba/ANEXO_HORARIOS_DOCUMENTADOS_MERCADOS.md",
    "outputs/mercados_caba/sanitized/horarios_documentados_mercados_vfinal.csv",
    "docs/mercados_caba/README_REGENERAR_INFORME_FINAL_V4_1.md",
    "docs/mercados_caba/OPORTUNIDAD_GESTION_MERCADOS_CABA_V4_1.md",
    "docs/mercados_caba/ANEXO_FUENTES_Y_METODOLOGIA_MERCADOS_V4_1.md",
    "outputs/mercados_caba/sanitized/oportunidades_gestion_mercados_v4_1.csv",
    "outputs/mercados_caba/sanitized/pilotos_recomendados_mercados_v4_1.csv",
    "outputs/mercados_caba/sanitized/publicos_objetivo_mercados_v4_1.csv",
]


def run(cmd: list[str], *, stdin: bytes | None = None) -> str:
    result = subprocess.run(
        cmd,
        input=stdin,
        cwd=ROOT,
        text=stdin is None,
        encoding="utf-8" if stdin is None else None,
        errors="replace" if stdin is None else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        stderr = result.stderr if isinstance(result.stderr, str) else result.stderr.decode("utf-8", errors="replace")
        stdout = result.stdout if isinstance(result.stdout, str) else result.stdout.decode("utf-8", errors="replace")
        raise RuntimeError(stderr.strip() or stdout.strip())
    if isinstance(result.stdout, bytes):
        return result.stdout.decode("utf-8", errors="replace")
    return result.stdout


def page_count(path: Path) -> int:
    out = run(["pdfinfo", str(path)])
    match = re.search(r"^Pages:\s+(\d+)", out, flags=re.MULTILINE)
    if not match:
        raise RuntimeError(f"No se pudo leer paginas de {path}")
    return int(match.group(1))


def pdf_text(path: Path) -> str:
    return run(["pdftotext", "-layout", str(path), "-"])


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def validate_pdf_text(report_text: str) -> None:
    forbidden = ["PÂ´ag.", "PÃ‚Â´ag.", "P´ag.", "P\\'ag", "->"]
    hits = [term for term in forbidden if term in report_text]
    if hits:
        raise RuntimeError("Terminos prohibidos en PDF con horarios:\n" + "\n".join(hits))

    required = [
        "Frecuencia, horarios documentados y públicos objetivo",
        "11 de 13 casos tienen horario documentado o frecuencia de apertura identificada",
        "los horarios permiten orientar programación",
        "en itinerantes, la franja depende de sede y edición",
        "Los horarios son autodeclarados o documentales",
        "pueden cambiar por temporada",
        "Validar y mantener actualizados los horarios antes de publicarlos como información operativa",
        "13 mercados gastronómicos activos identificados",
        "11 con sede fija",
        "2 itinerantes",
        "no es censo ni padrón oficial",
        "Google Places es señal auxiliar no oficial",
    ]
    text_norm = norm(report_text)
    missing = [item for item in required if norm(item) not in text_norm]
    if missing:
        raise RuntimeError("Falta texto esperado en PDF con horarios:\n" + "\n".join(missing))


def validate_horarios_files() -> None:
    anexo = ANEXO_HORARIOS.read_text(encoding="utf-8")
    if "Pueden variar por temporada, operador, sede o actualización de canales públicos" not in anexo:
        raise RuntimeError("El anexo no incluye advertencia de variabilidad de horarios")
    if "No se hicieron requests, no se usaron API keys y no se inventaron horarios" not in anexo:
        raise RuntimeError("El anexo no documenta la restriccion de no requests/API keys/no inventar")

    with HORARIOS_CSV.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    if len(rows) != 13:
        raise RuntimeError(f"CSV horarios: se esperaban 13 filas y hay {len(rows)}")

    mercados = {row["mercado"] for row in rows}
    required_markets = {"Buenos Aires Market", "Sabe la Tierra", "Mercado San Nicolás"}
    missing = sorted(required_markets - mercados)
    if missing:
        raise RuntimeError("Faltan mercados esperados en CSV horarios:\n" + "\n".join(missing))

    for row in rows:
        if row["sede"].lower() == "itinerante":
            horario = row["horario_documentado"].lower()
            if "depende" not in horario or "sin horario fijo" not in horario:
                raise RuntimeError(f"Itinerante con horario fijo no prudente: {row['mercado']} -> {row['horario_documentado']}")


def render_png() -> list[Path]:
    QA_DIR.mkdir(parents=True, exist_ok=True)
    for old in QA_DIR.glob("con_horarios_page-*.png"):
        old.unlink()
    prefix = QA_DIR / "con_horarios_page"
    run(["pdftoppm", "-png", "-r", "140", str(PDF), str(prefix)])
    return sorted(QA_DIR.glob("con_horarios_page-*.png"))


def zip_member_text(zf: zipfile.ZipFile, name: str) -> str:
    data = zf.read(name)
    if name.lower().endswith(".pdf"):
        return run(["pdftotext", "-layout", "-", "-"], stdin=data)
    return data.decode("utf-8", errors="replace")


def validate_pack() -> list[str]:
    with zipfile.ZipFile(PACK) as zf:
        names = zf.namelist()
        missing = [name for name in EXPECTED_PACK_FILES if name not in names]
        extra = [name for name in names if name not in EXPECTED_PACK_FILES]
        if missing:
            raise RuntimeError("Faltan archivos en pack con horarios:\n" + "\n".join(missing))
        if extra:
            raise RuntimeError("El pack con horarios incluye archivos no esperados:\n" + "\n".join(extra))

        forbidden_path_patterns = [
            r"(^|/)\.env($|/)",
            r"(^|/)internal/",
            r"(^|/)raw/",
            r"fuentes_internas_mercados_caba/",
            r"(^|/)config/v2/",
            r"(^|/)data/v2/",
            r"(^|/)docs/datagastro_v2/",
            r"qa_.*\.png$",
            r"\.xlsx$",
            r"\.json$",
        ]
        bad_paths = [
            name
            for name in names
            if any(re.search(pattern, name, flags=re.IGNORECASE) for pattern in forbidden_path_patterns)
        ]
        if bad_paths:
            raise RuntimeError("El pack incluye rutas prohibidas:\n" + "\n".join(bad_paths))

        checks = [
            ("api_key_literal", re.compile(r"\bapi[_-]?key\b|AIza[0-9A-Za-z_-]{20,}|sk-[0-9A-Za-z]{20,}", re.IGNORECASE)),
            ("place_id", re.compile(r"\bplace_id\b|ChIJ[0-9A-Za-z_-]+", re.IGNORECASE)),
            ("email", re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE)),
            ("telefono", re.compile(r"\b(?:\+?54\s*)?(?:11|15)\s?\d{4}[-\s]?\d{4}\b")),
            ("CUIT", re.compile(r"\b\d{2}-\d{8}-\d\b")),
            ("DNI", re.compile(r"\bDNI\b", re.IGNORECASE)),
            ("drive_privado", re.compile(r"https?://(?:drive|docs)\.google\.com/[^\s)]+", re.IGNORECASE)),
        ]
        sensitive: list[str] = []
        for name in names:
            content = zip_member_text(zf, name)
            for label, pattern in checks:
                if pattern.search(content):
                    sensitive.append(f"{name}: {label}")
        if sensitive:
            raise RuntimeError("Posibles datos sensibles en pack:\n" + "\n".join(sensitive))
    return names


def main() -> int:
    for path in [PDF, SUMMARY, PACK, HORARIOS_CSV, ANEXO_HORARIOS]:
        if not path.exists():
            raise FileNotFoundError(path)

    pages = page_count(PDF)
    summary_pages = page_count(SUMMARY)
    if pages not in {14, 15}:
        raise RuntimeError(f"Informe con horarios: se esperaban 14 o 15 paginas y hay {pages}")
    if summary_pages != 2:
        raise RuntimeError(f"Resumen con horarios: se esperaban 2 paginas y hay {summary_pages}")

    validate_pdf_text(pdf_text(PDF))
    validate_horarios_files()

    pngs = render_png()
    if len(pngs) != pages:
        raise RuntimeError(f"Render QA: se esperaban {pages} PNG y hay {len(pngs)}")

    pack_names = validate_pack()
    print("RESULTADO: OK")
    print(f"Informe con horarios paginas: {pages}")
    print(f"Resumen con horarios paginas: {summary_pages}")
    print(f"Render QA PNG: {QA_DIR} ({len(pngs)} paginas)")
    print(f"Pack con horarios archivos: {len(pack_names)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
