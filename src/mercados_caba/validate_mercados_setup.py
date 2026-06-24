"""Validador OFFLINE del setup del informe 'Mercados de la Ciudad de Buenos Aires'.

Verifica el andamiaje SIN ejecutar requests ni exponer datos sensibles:
  - existen los documentos esperados;
  - existen los CSV sanitizados esperados;
  - los entregables sanitizados no contienen emails/telefonos/CUIT/place_id/Drive/API keys;
  - los outputs internos/crudos estan gitignored;
  - no se generaron crudos versionables.

NO hace requests, NO usa API keys, NO lee datos sensibles. Solo libreria estandar.

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

EXPECTED_DOCS = [
    "00_vision_y_objetivo.md", "01_taxonomia_mercados.md", "02_fuentes_posibles.md",
    "03_metodologia_y_niveles_confianza.md", "04_plan_relevamiento.md", "05_campos_objetivo.md",
    "06_prompt_perplexity_mercados.md", "07_plan_google_places_mercados.md",
    "08_plan_osm_mercados.md", "09_estructura_informe_final.md",
    "10_relevamiento_candidatos_v0.md", "11_hallazgos_preliminares_v0.md",
    "12_brechas_y_pendientes_v0.md",
    "13_consolidacion_documental_v1.md", "14_hallazgos_v1.md",
    "15_decisiones_metodologicas_v1.md",
    "16_cierre_fino_v1_2.md", "17_resumen_ejecutivo_preinforme_v1_2.md",
    "INFORME_MERCADOS_GASTRONOMICOS_CABA_V1_2.md",
    "18_prompts_perplexity_enriquecimiento_v2.md",
    "19_enriquecimiento_google_internas_perplexity_v2.md",
    "20_integracion_documental_v2_1.md", "21_ajuste_conservador_estado_operativo_v2_2.md",
    "22_resumen_ejecutivo_v2_2.md", "INFORME_MERCADOS_GASTRONOMICOS_CABA_V2_2.md",
    "23_integracion_urls_perplexity_v2_3.md",
]
EXPECTED_CSV = [
    "fuentes_mercados_candidatas.csv", "taxonomia_mercados.csv",
    "campos_objetivo_mercados.csv", "mercados_candidatos_iniciales.csv",
    "mercados_gastronomicos_candidatos_v0.csv", "fuentes_mercados_urls_v0.csv",
    "mercados_fuera_alcance_v0.csv", "mercados_pendientes_revision_v0.csv",
    "resumen_relevamiento_mercados_v0.csv",
    "mercados_gastronomicos_candidatos_v1.csv", "mercados_gastronomicos_activos_v1.csv",
    "mercados_gastronomicos_cerrados_o_no_activos_v1.csv",
    "mercados_gastronomicos_pendientes_v1.csv", "fuentes_mercados_urls_v1.csv",
    "resumen_relevamiento_mercados_v1.csv",
    "mercados_gastronomicos_candidatos_v1_2.csv", "mercados_gastronomicos_activos_v1_2.csv",
    "mercados_gastronomicos_pendientes_v1_2.csv",
    "mercados_gastronomicos_no_contabilizados_v1_2.csv", "fuentes_mercados_urls_v1_2.csv",
    "resumen_relevamiento_mercados_v1_2.csv",
    # --- V2 enriquecimiento ---
    "fuentes_internas_mercados_resumen_v2.csv", "candidatos_mercados_fuentes_internas_v2.csv",
    "google_places_mercados_resumen_v2.csv", "google_places_matches_v1_2.csv",
    "google_places_posibles_omitidos_v2.csv", "fuentes_documentales_mercados_v2.csv",
    "mercados_gastronomicos_candidatos_v2.csv", "mercados_gastronomicos_activos_v2.csv",
    "mercados_gastronomicos_posibles_omitidos_v2.csv",
    "mercados_gastronomicos_no_contabilizados_v2.csv", "resumen_relevamiento_mercados_v2.csv",
    # --- V2.2 conservador ---
    "mercados_gastronomicos_candidatos_v2_2.csv", "mercados_gastronomicos_activos_v2_2.csv",
    "mercados_gastronomicos_en_revision_v2_2.csv",
    "mercados_gastronomicos_no_contabilizados_v2_2.csv",
    "mercados_gastronomicos_posibles_omitidos_v2_2.csv",
    "fuentes_documentales_mercados_v2_2.csv", "resumen_relevamiento_mercados_v2_2.csv",
    # --- V2.3 documental (URLs visibles) ---
    "fuentes_documentales_mercados_v2_3.csv", "afirmaciones_mercados_v2_3.csv",
    "contradicciones_y_brechas_v2_3.csv",
    "fuentes_url_truncadas_requieren_verificacion_v2_3.csv",
]
# CSV -> columnas obligatorias que deben existir en el header
REQUIRED_COLUMNS = {
    "mercados_gastronomicos_candidatos_v1.csv": [
        "id_candidato", "nombre", "tipo_mercado_gastronomico", "estado_operativo",
        "activo_para_conteo", "motivo_no_activo", "nivel_confianza",
    ],
    "mercados_gastronomicos_candidatos_v1_2.csv": [
        "id_candidato", "nombre", "tipo_mercado_gastronomico", "estado_operativo",
        "activo_para_conteo", "motivo_no_activo", "nivel_confianza",
    ],
    "mercados_gastronomicos_no_contabilizados_v1_2.csv": [
        "id", "nombre", "categoria_no_conteo", "motivo", "nivel_confianza",
    ],
    "mercados_gastronomicos_candidatos_v2_2.csv": [
        "id_candidato", "nombre", "activo_para_conteo", "categoria_v2_2",
    ],
}
# Casos retirados del conteo activo en V2.2 (no deben figurar en activos_v2_2).
EN_REVISION_V2_2 = {"MG-0005", "MG-0009", "MG-0014"}
FICHAS_DIRS = [DOCS_DIR / "fichas_v0", DOCS_DIR / "fichas_v1", DOCS_DIR / "fichas_v1_2"]
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
FORBIDDEN_COLUMNS = {
    "telefono", "teléfono", "celular", "mail", "email", "correo", "referente",
    "contacto", "cuit", "dni", "instagram", "place_id",
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


def check_docs(chk):
    for name in EXPECTED_DOCS:
        if (DOCS_DIR / name).is_file():
            chk.ok(f"doc presente: docs/mercados_caba/{name}")
        else:
            chk.error(f"falta doc: docs/mercados_caba/{name}")


def check_csv(chk):
    for name in EXPECTED_CSV:
        p = SAN_DIR / name
        if not p.is_file():
            chk.error(f"falta CSV sanitizado: outputs/mercados_caba/sanitized/{name}")
            continue
        with p.open(encoding="utf-8", newline="") as fh:
            header = next(csv.reader(fh), [])
        bad = [c for c in header if c.strip().lower() in FORBIDDEN_COLUMNS]
        if bad:
            chk.error(f"columna sensible en {name}: {bad}")
        else:
            chk.ok(f"CSV sanitizado OK: {name} ({len(header)} columnas)")
        req = REQUIRED_COLUMNS.get(name)
        if req:
            hdr = {c.strip() for c in header}
            missing = [c for c in req if c not in hdr]
            if missing:
                chk.error(f"faltan columnas obligatorias en {name}: {missing}")
            else:
                chk.ok(f"columnas obligatorias OK en {name}")


def check_csv_consistency(chk):
    """Verifica que cada fila tenga la misma cantidad de columnas que el header."""
    for p in sorted(SAN_DIR.glob("*.csv")):
        with p.open(encoding="utf-8", newline="") as fh:
            rows = list(csv.reader(fh))
        if not rows:
            chk.warn(f"CSV vacio: {p.name}")
            continue
        ncols = len(rows[0])
        malformadas = [(i + 1, len(r)) for i, r in enumerate(rows) if len(r) != ncols]
        if malformadas:
            detalle = "; ".join(f"linea {ln}: {nc} cols" for ln, nc in malformadas)
            chk.error(f"CSV mal formado {p.name} (header={ncols} cols) -> {detalle}")
        else:
            chk.ok(f"CSV consistente: {p.name} ({len(rows)} filas x {ncols} cols)")


def check_fichas(chk):
    for d in FICHAS_DIRS:
        if not d.is_dir():
            chk.error(f"falta carpeta de fichas: docs/mercados_caba/{d.name}/")
            continue
        fichas = sorted(d.glob("*.md"))
        if not fichas:
            chk.warn(f"carpeta {d.name} sin fichas .md")
        else:
            chk.ok(f"{d.name} con {len(fichas)} fichas .md")


def check_privacy(chk):
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


def check_v2_2_conservador(chk):
    """V2.2: los 3 en revision no estan en activos; resumen reporta 12 activos."""
    act = SAN_DIR / "mercados_gastronomicos_activos_v2_2.csv"
    rev = SAN_DIR / "mercados_gastronomicos_en_revision_v2_2.csv"
    res = SAN_DIR / "resumen_relevamiento_mercados_v2_2.csv"
    if act.is_file():
        with act.open(encoding="utf-8", newline="") as fh:
            rows = list(csv.DictReader(fh))
        ids = {r.get("id_candidato", "").strip() for r in rows}
        intrusos = sorted(EN_REVISION_V2_2 & ids)
        if intrusos:
            chk.error(f"casos en revision presentes en activos_v2_2: {intrusos}")
        else:
            chk.ok("activos_v2_2 no contiene los 3 casos en revision")
        if len(rows) == 12:
            chk.ok("activos_v2_2 tiene 12 filas (conteo conservador)")
        else:
            chk.error(f"activos_v2_2 tiene {len(rows)} filas (se esperaban 12)")
    if rev.is_file():
        with rev.open(encoding="utf-8", newline="") as fh:
            rows = list(csv.DictReader(fh))
        ids = {r.get("id_candidato", "").strip() for r in rows}
        if EN_REVISION_V2_2 <= ids:
            chk.ok("en_revision_v2_2 contiene los 3 casos esperados")
        else:
            chk.error(f"en_revision_v2_2 no contiene {sorted(EN_REVISION_V2_2 - ids)}")
        no_conteo = all(r.get("activo_para_conteo", "").strip().lower() == "no" for r in rows)
        chk.ok("en_revision_v2_2: activo_para_conteo=no en todos") if no_conteo else \
            chk.error("en_revision_v2_2: algun caso no tiene activo_para_conteo=no")
    if res.is_file():
        txt = res.read_text(encoding="utf-8")
        if "activos_confirmados_para_conteo,12" in txt.replace(" ", ""):
            chk.ok("resumen_v2_2 reporta 12 activos para conteo")
        else:
            chk.error("resumen_v2_2 no reporta 12 activos para conteo")


def check_v2_3_urls(chk):
    """Toda URL con '...' en fuentes_documentales_v2_3 debe marcarse url_truncada_requiere_verificacion."""
    p = SAN_DIR / "fuentes_documentales_mercados_v2_3.csv"
    if not p.is_file():
        return
    mal = []
    with p.open(encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            url = (r.get("url") or "")
            est = (r.get("estado_url") or "").strip()
            if "..." in url and est != "url_truncada_requiere_verificacion":
                mal.append(r.get("id_fuente", "?"))
    if mal:
        chk.error(f"URLs truncadas sin estado_url correcto en v2_3: {mal}")
    else:
        chk.ok("v2_3: URLs truncadas marcadas url_truncada_requiere_verificacion")


def check_env_not_tracked(chk):
    """.env y *.env deben estar gitignored y NO versionados."""
    ignored = read_gitignore()
    for pat in (".env", "*.env"):
        if pat in ignored:
            chk.ok(f"gitignore cubre credenciales: {pat}")
        else:
            chk.error(f"patron de credenciales NO esta en .gitignore: {pat}")
    # si existe .env, verificar que git no lo trackee
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
    print("Informe Mercados CABA - validacion de setup (OFFLINE). No hace requests.")
    print(f"Repo: {REPO_ROOT}")
    print("=" * 78)

    check_docs(chk)
    check_csv(chk)
    check_csv_consistency(chk)
    check_fichas(chk)
    check_privacy(chk)
    check_internal_gitignored(chk)
    check_v2_2_conservador(chk)
    check_v2_3_urls(chk)
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
        print("RESULTADO: HAY ERRORES.")
        return 1
    print("RESULTADO: SETUP MERCADOS CABA OK (diseño/preparación). Sin requests.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
