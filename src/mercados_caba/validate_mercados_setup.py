"""Validador OFFLINE de la CADENA VIGENTE del informe 'Mercados gastronomicos de CABA'.

Desde la reorganizacion 2026-06-29 este validador NO valida el historial completo de
versiones (V1/V2/V3/V4 y sus CSV/PDF/QA intermedios fueron eliminados o archivados en `_archive_historico/` durante la reorganización).
Valida UNICAMENTE la cadena vigente y reproducible que genera el PDF final:

  Generador final : src/mercados_caba/build_pdf_final_con_horarios.py
  Cadena builders : build_pdf_final_con_horarios -> build_pdf_final_entrega
                    -> build_pdf_final_v4_1_from_v3 -> build_pdf_from_markdown_master
  Graficos vigentes: src/mercados_caba/build_visuals_v5.py (-> *_v5.png)
  PDF fuente verdad: outputs/mercados_caba/sanitized/MercadosGastroCABA_con_horarios.pdf
  Copia final      : MercadosGastro/final/MercadosGastroCABA_FINAL.pdf

Verifica, sin requests ni datos sensibles:
  - existen el generador final y los builders/visuals encadenados;
  - existen los insumos (docs/CSV/PNG) que la cadena vigente consume;
  - existe la salida final en outputs/.../sanitized/ y la copia en MercadosGastro/final/;
  - el PDF final tiene 14 paginas, footer correcto y conserva frases ancla de p7/p11/p14;
  - el PDF final NO menciona 'V4_1';
  - los entregables sanitizados no contienen datos personales (email/tel/CUIT/place_id/Drive/apikey);
  - las carpetas internas/crudas y .env siguen gitignored y sin crudos versionables.

NO valida material historico V1/V2/V3/V4 (el material historico fue archivado o eliminado).

NO hace requests, NO usa API keys, NO lee datos sensibles. Solo libreria estandar
(+ PyPDF2/pypdf si esta disponible, para los chequeos del PDF final).

Uso:
    python src/mercados_caba/validate_mercados_setup.py
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = REPO_ROOT / "docs" / "mercados_caba"
SAN_DIR = REPO_ROOT / "outputs" / "mercados_caba" / "sanitized"
SRC_DIR = REPO_ROOT / "src" / "mercados_caba"
FINAL_DIR = REPO_ROOT / "MercadosGastro" / "final"

# ---------------------------------------------------------------------------
# CADENA VIGENTE (solo lo que se usa para regenerar el PDF final)
# ---------------------------------------------------------------------------

# Generador final + builders encadenados (importados dinamicamente entre si) + visuals v5.
EXPECTED_BUILDERS = [
    "build_pdf_final_con_horarios.py",   # generador final (entrypoint)
    "build_pdf_final_entrega.py",        # encadenado por el anterior
    "build_pdf_final_v4_1_from_v3.py",   # encadenado
    "build_pdf_from_markdown_master.py", # base markdown-first de la cadena
    "build_visuals_v5.py",               # genera los graficos/mapas v5 vigentes
]

# Documentos que la cadena vigente consume como fuente editorial.
EXPECTED_DOCS = [
    "INFORME_FINAL_MERCADOS_GASTRONOMICOS_CABA_MARKDOWN_MASTER.md",  # fuente de verdad editorial
    "ANEXO_HORARIOS_DOCUMENTADOS_MERCADOS.md",
    "ANEXO_FUENTES_Y_METODOLOGIA_MERCADOS_V4_1.md",
    "OPORTUNIDAD_GESTION_MERCADOS_CABA_V4_1.md",
    "README_REGENERAR_INFORME_FINAL_V4_1.md",
]

# CSV sanitizados que alimentan la cadena vigente (build_pdf_* y build_visuals_v5).
EXPECTED_CSV = [
    "horarios_documentados_mercados_vfinal.csv",
    "horarios_mercados_gastronomicos_v3.csv",
    "mercados_gastronomicos_activos_v4.csv",
    "indicadores_mercados_gastronomicos_v4.csv",
    "respaldo_fuentes_mercados_v4.csv",
    "tipologias_mercados_v4.csv",
    "mercados_sedes_fijas_v5.csv",
    "oportunidades_gestion_mercados_v4_1.csv",
    "pilotos_recomendados_mercados_v4_1.csv",
    "publicos_objetivo_mercados_v4_1.csv",
]

# Graficos/mapas v5 que la cadena del PDF reutiliza.
EXPECTED_VISUALS = [
    "grafico_kpi_cards_v5.png",
    "grafico_tipo_primario_v5.png",
    "grafico_gestion_v5.png",
    "grafico_horarios_v5.png",
    "grafico_publicos_objetivo_v5.png",
    "grafico_respaldo_fuentes_v5.png",
    "mapa_sedes_fijas_mercados_gastronomicos_v5.png",
    "visual_itinerantes_mercados_gastronomicos_v5.png",
]

# Salida final (fuente de verdad) y copia navegable.
FINAL_PDF_SRC = SAN_DIR / "MercadosGastroCABA_con_horarios.pdf"
FINAL_RESUMEN_SRC = SAN_DIR / "ResumenEjecutivo_MercadosGastroCABA_con_horarios.pdf"
FINAL_PDF_COPY = FINAL_DIR / "MercadosGastroCABA_FINAL.pdf"

# Anclas de contenido que el PDF final debe conservar.
PDF_EXPECTED_PAGES = 14
PDF_FOOTER = "DataGastro · Mercados gastronómicos de CABA · Informe final"
PDF_ANCHOR_P11 = "Activar patios públicos como dinamizadores barriales."
PDF_ANCHOR_P14 = "Alcances del relevamiento y próximos pasos para consolidar la base candidata."
# En p7 hay una tabla de franjas horarias documentadas; estas son lecturas concretas.
PDF_ANCHOR_P7_ANY = ["8-18", "11-24", "9-24", "10-19", "8:30-20"]
PDF_FORBIDDEN = ["V4_1", "v4_1", "V4.1"]

# Columnas que NUNCA deben aparecer en entregables sanitizados.
FORBIDDEN_COLUMNS = {
    "telefono", "teléfono", "celular", "mail", "email", "correo", "referente",
    "contacto", "cuit", "dni", "instagram", "place_id",
}

INTERNAL_DIRS = [
    "outputs/mercados_caba/internal/", "outputs/mercados_caba/raw/",
    "outputs/mercados_caba/internal/google_places_raw/", "fuentes_internas_mercados_caba/",
]

PRIVACY_PATTERNS = {
    "email": re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}"),
    "telefono_ar": re.compile(r"(?<!\d)(?:\+?54\s?)?(?:11|15)[\s\-]?\d{4}[\s\-]?\d{4}(?!\d)"),
    "cuit": re.compile(r"(?<!\d)\d{2}-\d{8}-\d(?!\d)"),
    "place_id": re.compile(r"\bChIJ[0-9A-Za-z_\-]{10,}\b"),
    "drive_link": re.compile(r"(?i)(?:drive|docs)\.google\.com/[^\s\"']+"),
    "api_key_google": re.compile(r"AIza[0-9A-Za-z_\-]{20,}"),
}


class Check:
    def __init__(self):
        self.ok_lines, self.warnings, self.errors = [], [], []

    def ok(self, m): self.ok_lines.append(m)
    def warn(self, m): self.warnings.append(m)
    def error(self, m): self.errors.append(m)


def read_gitignore() -> set[str]:
    gi = REPO_ROOT / ".gitignore"
    if not gi.exists():
        return set()
    return {ln.strip() for ln in gi.read_text(encoding="utf-8").splitlines()
            if ln.strip() and not ln.strip().startswith("#")}


# ---------------------------------------------------------------------------
# Chequeos de la cadena vigente
# ---------------------------------------------------------------------------

def check_builders(chk):
    for name in EXPECTED_BUILDERS:
        if (SRC_DIR / name).is_file():
            chk.ok(f"builder vigente presente: src/mercados_caba/{name}")
        else:
            chk.error(f"falta builder vigente: src/mercados_caba/{name}")


def check_docs(chk):
    for name in EXPECTED_DOCS:
        if (DOCS_DIR / name).is_file():
            chk.ok(f"doc vigente presente: docs/mercados_caba/{name}")
        else:
            chk.error(f"falta doc de la cadena vigente: docs/mercados_caba/{name}")


def check_csv(chk):
    for name in EXPECTED_CSV:
        p = SAN_DIR / name
        if not p.is_file():
            chk.error(f"falta CSV insumo vigente: outputs/mercados_caba/sanitized/{name}")
            continue
        with p.open(encoding="utf-8", newline="") as fh:
            header = next(csv.reader(fh), [])
        bad = [c for c in header if c.strip().lower() in FORBIDDEN_COLUMNS]
        if bad:
            chk.error(f"columna sensible en {name}: {bad}")
        else:
            chk.ok(f"CSV insumo vigente OK: {name} ({len(header)} columnas)")


def check_visuals(chk):
    for name in EXPECTED_VISUALS:
        if (SAN_DIR / name).is_file():
            chk.ok(f"visual vigente presente: {name}")
        else:
            chk.error(f"falta visual vigente: outputs/mercados_caba/sanitized/{name}")


def check_csv_consistency(chk):
    """Cada CSV insumo vigente debe tener filas con el mismo numero de columnas que el header."""
    for name in EXPECTED_CSV:
        p = SAN_DIR / name
        if not p.is_file():
            continue
        with p.open(encoding="utf-8", newline="") as fh:
            rows = list(csv.reader(fh))
        if not rows:
            chk.warn(f"CSV vacio: {name}")
            continue
        ncols = len(rows[0])
        malformadas = [(i + 1, len(r)) for i, r in enumerate(rows) if len(r) != ncols]
        if malformadas:
            detalle = "; ".join(f"linea {ln}: {nc} cols" for ln, nc in malformadas)
            chk.error(f"CSV mal formado {name} (header={ncols} cols) -> {detalle}")
        else:
            chk.ok(f"CSV consistente: {name} ({len(rows)} filas x {ncols} cols)")


def check_final_outputs(chk):
    """Existen la salida final (fuente de verdad) y la copia navegable."""
    for label, p, rel in [
        ("PDF final (fuente de verdad)", FINAL_PDF_SRC,
         "outputs/mercados_caba/sanitized/MercadosGastroCABA_con_horarios.pdf"),
        ("Resumen ejecutivo final", FINAL_RESUMEN_SRC,
         "outputs/mercados_caba/sanitized/ResumenEjecutivo_MercadosGastroCABA_con_horarios.pdf"),
        ("Copia final navegable", FINAL_PDF_COPY,
         "MercadosGastro/final/MercadosGastroCABA_FINAL.pdf"),
    ]:
        if p.is_file():
            chk.ok(f"{label} presente: {rel}")
        else:
            chk.error(f"falta {label}: {rel}")


def _load_pdf_reader(pdf_path):
    try:
        from pypdf import PdfReader  # type: ignore
        return PdfReader(str(pdf_path)), None
    except Exception:
        pass
    try:
        from PyPDF2 import PdfReader  # type: ignore
        return PdfReader(str(pdf_path)), None
    except Exception as e:  # pragma: no cover
        return None, e


def check_final_pdf_content(chk):
    """Valida paginas, footer y frases ancla del PDF final. Degrada a aviso si no hay lib PDF."""
    if not FINAL_PDF_SRC.is_file():
        chk.error("no se puede validar contenido: falta el PDF final fuente de verdad")
        return
    reader, err = _load_pdf_reader(FINAL_PDF_SRC)
    if reader is None:
        chk.warn(f"no hay libreria PDF (pypdf/PyPDF2) disponible; se omiten chequeos de contenido del PDF ({err})")
        return

    pages = reader.pages
    n = len(pages)
    if n == PDF_EXPECTED_PAGES:
        chk.ok(f"PDF final tiene {PDF_EXPECTED_PAGES} paginas")
    else:
        chk.error(f"PDF final tiene {n} paginas (se esperaban {PDF_EXPECTED_PAGES})")

    def page_text(i):
        if 0 <= i < n:
            try:
                return pages[i].extract_text() or ""
            except Exception:
                return ""
        return ""

    full = "\n".join(page_text(i) for i in range(n))

    # Footer (puede repetirse en cada pagina). Buscar en todo el documento.
    if PDF_FOOTER in full:
        chk.ok(f"PDF final conserva el footer: '{PDF_FOOTER}'")
    else:
        chk.error(f"PDF final NO contiene el footer esperado: '{PDF_FOOTER}'")

    # p7 (indice 6): franjas horarias documentadas concretas.
    p7 = page_text(6)
    if any(tok in p7 for tok in PDF_ANCHOR_P7_ANY):
        chk.ok("p7 conserva horarios documentales concretos (franjas horarias)")
    elif any(tok in full for tok in PDF_ANCHOR_P7_ANY):
        chk.warn("franjas horarias presentes en el PDF pero no detectadas exactamente en p7; revisar maquetacion")
    else:
        chk.error("p7 no conserva horarios documentales concretos")

    # p11: frase ancla de patios.
    if PDF_ANCHOR_P11 in full:
        chk.ok(f"PDF final conserva (p11): '{PDF_ANCHOR_P11}'")
    else:
        chk.error(f"PDF final NO conserva la frase de p11: '{PDF_ANCHOR_P11}'")

    # p14: frase ancla de alcances.
    if PDF_ANCHOR_P14 in full:
        chk.ok(f"PDF final conserva (p14): '{PDF_ANCHOR_P14}'")
    else:
        chk.error(f"PDF final NO conserva la frase de p14: '{PDF_ANCHOR_P14}'")

    # No debe aparecer 'V4_1' en el texto del informe final.
    found = [tok for tok in PDF_FORBIDDEN if tok in full]
    if found:
        chk.error(f"PDF final menciona etiqueta de version interna {found} (no debe aparecer)")
    else:
        chk.ok("PDF final no menciona 'V4_1' ni variantes")


# ---------------------------------------------------------------------------
# Guardrails agnosticos de version (privacidad / gitignore / crudos)
# ---------------------------------------------------------------------------

def check_privacy(chk):
    """Escanea docs y entregables sanitizados (vigentes) en busca de datos personales."""
    scanned, hits = 0, []
    for base in (DOCS_DIR, SAN_DIR):
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if not p.is_file() or p.suffix.lower() not in {".md", ".csv", ".txt"}:
                continue
            scanned += 1
            text = p.read_text(encoding="utf-8", errors="ignore")
            for label, pat in PRIVACY_PATTERNS.items():
                if pat.search(text):
                    hits.append(f"{p.relative_to(REPO_ROOT)} ~ {label}")
    if hits:
        chk.error(f"posible dato sensible en entregables: {hits}")
    else:
        chk.ok(f"escaneo de privacidad OK en {scanned} entregables (sin email/tel/CUIT/place_id/Drive/apikey)")


def check_internal_gitignored(chk):
    ignored = read_gitignore()
    for rel in INTERNAL_DIRS:
        if rel in ignored:
            chk.ok(f"gitignore cubre carpeta interna/cruda: {rel}")
        else:
            chk.error(f"carpeta interna/cruda NO esta en .gitignore: {rel}")


def check_env_not_tracked(chk):
    """.env y *.env deben estar gitignored y NO versionados."""
    ignored = read_gitignore()
    for pat in (".env", "*.env"):
        if pat in ignored:
            chk.ok(f"gitignore cubre credenciales: {pat}")
        else:
            chk.error(f"patron de credenciales NO esta en .gitignore: {pat}")
    if (REPO_ROOT / ".env").exists():
        try:
            import subprocess
            r = subprocess.run(["git", "ls-files", "--error-unmatch", ".env"],
                               cwd=REPO_ROOT, capture_output=True, text=True)
            if r.returncode == 0:
                chk.error(".env esta VERSIONADO en git (no debe estarlo)")
            else:
                chk.ok(".env presente pero NO versionado")
        except Exception:
            chk.warn("no se pudo verificar el tracking de .env con git")
    else:
        chk.ok(".env no presente (sin credenciales en repo)")


def check_no_crudos(chk):
    data_suffixes = {".csv", ".json", ".zip", ".pdf", ".xlsx", ".geojson"}
    for rel in ["outputs/mercados_caba/internal", "outputs/mercados_caba/raw"]:
        base = REPO_ROOT / rel
        if not base.exists():
            continue
        files = [p for p in base.rglob("*") if p.is_file() and p.suffix.lower() in data_suffixes]
        if files:
            chk.warn(f"hay datos en {rel} (gitignored, no se versiona): {len(files)} archivos")
        else:
            chk.ok(f"carpeta interna/cruda sin datos versionables: {rel}")


def main() -> int:
    chk = Check()
    print("=" * 78)
    print("Mercados CABA - validacion de la CADENA VIGENTE del informe final (OFFLINE).")
    print("No valida historial V1/V2/V3/V4 (el material histórico fue archivado o eliminado). No hace requests.")
    print(f"Repo: {REPO_ROOT}")
    print("=" * 78)

    check_builders(chk)
    check_docs(chk)
    check_csv(chk)
    check_visuals(chk)
    check_csv_consistency(chk)
    check_final_outputs(chk)
    check_final_pdf_content(chk)
    check_privacy(chk)
    check_internal_gitignored(chk)
    check_env_not_tracked(chk)
    check_no_crudos(chk)

    print(f"\n[OK]      {len(chk.ok_lines)} verificaciones")
    for l in chk.ok_lines:
        print(f"  + {l}")
    if chk.warnings:
        print(f"\n[AVISOS]  {len(chk.warnings)}")
        for l in chk.warnings:
            print(f"  ! {l}")
    if chk.errors:
        print(f"\n[ERRORES] {len(chk.errors)}")
        for l in chk.errors:
            print(f"  x {l}")

    print("\n" + "-" * 78)
    if chk.errors:
        print("RESULTADO: HAY ERRORES en la cadena vigente.")
        return 1
    print("RESULTADO: CADENA VIGENTE MERCADOS CABA OK. Sin requests.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
