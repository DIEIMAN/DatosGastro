"""Validador del esqueleto tecnico de DataGastro V2 (Etapa 1).

Verifica que el andamiaje este bien armado SIN ejecutar integraciones:
  - existen las carpetas V2 esperadas;
  - existen los configs y tienen las columnas minimas;
  - existen los schemas;
  - no hay archivos .env en el repo;
  - no hay API keys hardcodeadas en src/v2, config/v2 ni schemas/v2;
  - no hay outputs crudos versionables (carpetas sensibles deben estar gitignored);
  - imprime un resumen y devuelve codigo de salida 0 (ok) o 1 (hay fallas).

NO hace requests. NO usa API keys. NO lee datos reales. Solo libreria estandar.

Uso:
    python src/v2/validate_v2_setup.py
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# Permitir importar load_config tanto si se corre como script como si se importa el paquete.
sys.path.insert(0, str(REPO_ROOT))
try:
    from src.v2.load_config import EXPECTED_COLUMNS, validate_config_file  # type: ignore
except Exception:  # pragma: no cover - fallback cuando se ejecuta dentro de src/v2
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from load_config import EXPECTED_COLUMNS, validate_config_file  # type: ignore

# --- Carpetas esperadas ---------------------------------------------------------------
EXPECTED_DIRS = [
    "src/v2",
    "src/v2/contracts",
    "src/v2/utils",
    "config/v2",
    "schemas/v2",
    "data/v2",
    "data/v2/raw",
    "data/v2/processed",
    "data/v2/analytics",
    "outputs/v2",
    "outputs/v2/sanitized",
    "outputs/v2/internal",
    "docs/datagastro_v2",
]

# --- Documentos esperados (Etapa 0, 1 y 2) --------------------------------------------
EXPECTED_DOCS = [
    "docs/datagastro_v2/README.md",
    "docs/datagastro_v2/00_vision_general.md",
    "docs/datagastro_v2/01_taxonomia_gastronomica_v2.md",
    # Etapa 2:
    "docs/datagastro_v2/11_matriz_fuentes_oficiales_v2.md",
    "docs/datagastro_v2/12_plan_barrido_total_gastronomico_v2.md",
    "docs/datagastro_v2/13_mapa_cobertura_por_rubro_v2.md",
    # Etapa 2.5:
    "docs/datagastro_v2/14_inventario_dgdgas_drive.md",
    "docs/datagastro_v2/15_fuentes_internas_dgdgas_v2.md",
    # Etapa 3:
    "docs/datagastro_v2/16_integracion_segura_i10_dgdgas.md",
    # Etapa 3.5:
    "docs/datagastro_v2/17_normalizacion_i10_barrios_y_rubros.md",
]

# --- Salidas sanitizadas esperadas (Etapa 2.5) ----------------------------------------
# Son versionables (agregados sin datos sensibles). NO se exige la carpeta DGDGAS original.
EXPECTED_SANITIZED = [
    "outputs/v2/sanitized/inventario_dgdgas_archivos_sanitizado.csv",
    "outputs/v2/sanitized/fuentes_internas_dgdgas_candidatas.csv",
    "outputs/v2/sanitized/cobertura_dgdgas_por_rubro_v2.csv",
    # Etapa 3 (I10):
    "outputs/v2/sanitized/i10_dgdgas_agregado_por_hoja.csv",
    "outputs/v2/sanitized/i10_dgdgas_agregado_por_rubro_v2.csv",
    "outputs/v2/sanitized/i10_dgdgas_agregado_por_barrio.csv",
    "outputs/v2/sanitized/i10_dgdgas_resumen_integracion.csv",
    # Etapa 3.5 (normalizacion I10):
    "outputs/v2/sanitized/i10_dgdgas_calidad_barrios.csv",
    "outputs/v2/sanitized/i10_dgdgas_agregado_barrio_normalizado.csv",
    "outputs/v2/sanitized/i10_dgdgas_agregado_rubro_normalizado.csv",
    "outputs/v2/sanitized/i10_dgdgas_desagregacion_hojas_mixtas.csv",
    "outputs/v2/sanitized/i10_dgdgas_pendientes_revision.csv",
]

# Columnas/encabezados que NUNCA deben aparecer en outputs sanitizados.
FORBIDDEN_SANITIZED_COLUMNS = {
    "nombre_local", "direccion", "direccion_si_existe", "telefono", "teléfono",
    "celular", "mail", "email", "correo", "referente", "instagram", "contacto",
    "cuit", "dni", "cargo",
}

# Staging interno que debe estar GITIGNORED (no versionable).
INTERNAL_MUST_BE_IGNORED = [
    "outputs/v2/internal/i10_dgdgas_perfil_columnas.csv",
    "outputs/v2/internal/i10_dgdgas_establecimientos_minimizados.csv",
    "outputs/v2/internal/i10_dgdgas_establecimientos_normalizados.csv",
]

# Archivos versionables/entregables sobre los que se corre el escaneo de privacidad.
PRIVACY_SCAN_PATHS = [
    "outputs/v2/sanitized",
    "config/v2/fuentes_internas_v2.csv",
    "docs/datagastro_v2/14_inventario_dgdgas_drive.md",
    "docs/datagastro_v2/15_fuentes_internas_dgdgas_v2.md",
]

# Patrones de datos sensibles que NO deben aparecer en entregables sanitizados.
PRIVACY_PATTERNS = {
    "email": re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}"),
    "telefono_ar": re.compile(r"(?<!\d)(?:\+?54\s?)?(?:11|15)[\s\-]?\d{4}[\s\-]?\d{4}(?!\d)"),
    "cuit": re.compile(r"(?<!\d)\d{2}-\d{8}-\d(?!\d)"),
    "place_id": re.compile(r"\bChIJ[0-9A-Za-z_\-]{10,}\b"),
    "drive_link": re.compile(r"(?i)(?:drive|docs)\.google\.com/[^\s\"']+"),
}

# --- Schemas esperados ----------------------------------------------------------------
EXPECTED_SCHEMAS = [
    "dim_establecimiento_candidato.schema.yml",
    "dim_fuente.schema.yml",
    "dim_rubro_gastronomico.schema.yml",
    "dim_marca_cadena.schema.yml",
    "dim_territorio.schema.yml",
    "fact_deteccion_fuente.schema.yml",
    "fact_validacion_manual.schema.yml",
    "fact_trayectoria_documental.schema.yml",
    "fact_evento_gastronomico.schema.yml",
]

# --- Carpetas que DEBEN quedar fuera del repo (datos sensibles / crudos) --------------
SENSITIVE_DIRS = [
    "data/v2/raw/",
    "data/v2/processed/",
    "outputs/v2/internal/",
    "outputs/v2/google_places_raw/",
    "outputs/v2/osm_raw/",
    "outputs/v2/documental_raw/",
]

# --- Patrones de posibles API keys hardcodeadas ---------------------------------------
# Heuristicas conservadoras. La idea es que NO aparezcan secretos en codigo/config versionado.
API_KEY_PATTERNS = [
    re.compile(r"AIza[0-9A-Za-z_\-]{20,}"),                     # Google API key
    re.compile(r"(?i)\bapi[_\-]?key\b\s*[=:]\s*['\"][^'\"]{12,}['\"]"),
    re.compile(r"(?i)GOOGLE_MAPS_API_KEY\s*[=:]\s*['\"][^'\"]+['\"]"),
    re.compile(r"sk-[0-9A-Za-z]{20,}"),                          # estilo OpenAI/Perplexity
    re.compile(r"(?i)\bbearer\b\s+[0-9A-Za-z_\-\.]{20,}"),
]
SCAN_DIRS = ["src/v2", "config/v2", "schemas/v2"]
SCAN_SUFFIXES = {".py", ".csv", ".yml", ".yaml", ".json", ".md", ".txt"}


class Check:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.ok_lines: list[str] = []

    def ok(self, msg: str) -> None:
        self.ok_lines.append(msg)

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)


def check_dirs(chk: Check) -> None:
    for rel in EXPECTED_DIRS:
        if (REPO_ROOT / rel).is_dir():
            chk.ok(f"carpeta presente: {rel}")
        else:
            chk.error(f"falta carpeta: {rel}")


def check_configs(chk: Check) -> None:
    for filename, expected in EXPECTED_COLUMNS.items():
        res = validate_config_file(filename, expected)
        if not res["existe"]:
            chk.error(f"falta config: config/v2/{filename}")
        elif not res["columnas_ok"]:
            chk.error(f"columnas invalidas en {filename}: faltan {res['faltan_columnas']}")
        elif res["filas"] == 0:
            chk.warn(f"config sin filas: {filename}")
        else:
            chk.ok(f"config OK: {filename} ({res['filas']} filas)")


def check_docs(chk: Check) -> None:
    for rel in EXPECTED_DOCS:
        if (REPO_ROOT / rel).is_file():
            chk.ok(f"doc presente: {rel}")
        else:
            chk.error(f"falta doc: {rel}")


def check_sanitized_outputs(chk: Check) -> None:
    for rel in EXPECTED_SANITIZED:
        if (REPO_ROOT / rel).is_file():
            chk.ok(f"salida sanitizada presente: {rel}")
        else:
            # No es error duro: pueden regenerarse con build_dgdgas_inventory.py.
            chk.warn(f"falta salida sanitizada (regenerable): {rel}")


def check_privacy_sanitized(chk: Check) -> None:
    """Escanea entregables sanitizados en busca de PII / links privados / place_id."""
    scanned = 0
    hits: list[str] = []
    for rel in PRIVACY_SCAN_PATHS:
        base = REPO_ROOT / rel
        if not base.exists():
            continue
        files = base.rglob("*") if base.is_dir() else [base]
        for path in files:
            if not path.is_file() or path.suffix.lower() not in {".csv", ".md", ".txt"}:
                continue
            scanned += 1
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for label, pat in PRIVACY_PATTERNS.items():
                m = pat.search(text)
                if m:
                    hits.append(f"{path.relative_to(REPO_ROOT)} ~ {label}")
    if hits:
        chk.error(f"posible dato sensible en entregables sanitizados: {hits}")
    else:
        chk.ok(f"escaneo de privacidad OK en {scanned} entregables (sin email/tel/CUIT/place_id/Drive)")


def check_sanitized_columns(chk: Check) -> None:
    """Ningun CSV sanitizado debe tener columnas sensibles (match exacto de encabezado)."""
    sdir = REPO_ROOT / "outputs" / "v2" / "sanitized"
    if not sdir.is_dir():
        return
    bad = []
    for path in sorted(sdir.glob("*.csv")):
        try:
            with path.open(encoding="utf-8", newline="") as fh:
                header = next(csv.reader(fh), [])
        except OSError:
            continue
        for col in header:
            if col.strip().lower() in FORBIDDEN_SANITIZED_COLUMNS:
                bad.append(f"{path.name}:{col}")
    if bad:
        chk.error(f"columna sensible en output sanitizado: {bad}")
    else:
        chk.ok("ningun output sanitizado tiene columnas sensibles (nombre/direccion/PII)")


def check_internal_not_versionable(chk: Check) -> None:
    """El staging interno I10, si existe, debe estar cubierto por .gitignore."""
    ignored = set(read_gitignore())
    dir_ignored = "outputs/v2/internal/" in ignored
    existentes = [rel for rel in INTERNAL_MUST_BE_IGNORED if (REPO_ROOT / rel).is_file()]
    if not existentes:
        chk.warn("staging interno I10 ausente (regenerable con build_i10_dgdgas_staging.py)")
        return
    if dir_ignored:
        chk.ok(f"staging interno I10 presente y gitignored ({len(existentes)} archivos)")
    else:
        chk.error("staging interno I10 existe pero outputs/v2/internal/ NO esta gitignored")


def check_schemas(chk: Check) -> None:
    schema_dir = REPO_ROOT / "schemas" / "v2"
    for name in EXPECTED_SCHEMAS:
        if (schema_dir / name).is_file():
            chk.ok(f"schema presente: {name}")
        else:
            chk.error(f"falta schema: schemas/v2/{name}")


def check_no_env_files(chk: Check) -> None:
    hits = []
    for path in REPO_ROOT.rglob("*"):
        # Ignorar el entorno virtual y carpetas pesadas irrelevantes.
        parts = set(path.parts)
        if ".venv" in parts or "__pycache__" in parts or ".git" in parts:
            continue
        if path.is_file() and (path.name == ".env" or path.suffix == ".env"):
            hits.append(str(path.relative_to(REPO_ROOT)))
    if hits:
        chk.error(f"se encontraron archivos .env (no deben existir/commitearse): {hits}")
    else:
        chk.ok("no hay archivos .env en el repo")


def check_no_hardcoded_keys(chk: Check) -> None:
    hits = []
    for rel in SCAN_DIRS:
        base = REPO_ROOT / rel
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in SCAN_SUFFIXES:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for pat in API_KEY_PATTERNS:
                if pat.search(text):
                    hits.append(f"{path.relative_to(REPO_ROOT)} ~ /{pat.pattern}/")
                    break
    if hits:
        chk.error(f"posibles API keys hardcodeadas: {hits}")
    else:
        chk.ok("no se detectaron API keys hardcodeadas en src/v2, config/v2 ni schemas/v2")


def read_gitignore() -> list[str]:
    gi = REPO_ROOT / ".gitignore"
    if not gi.exists():
        return []
    return [ln.strip() for ln in gi.read_text(encoding="utf-8").splitlines()
            if ln.strip() and not ln.strip().startswith("#")]


def check_sensitive_gitignored(chk: Check) -> None:
    ignored = set(read_gitignore())
    for rel in SENSITIVE_DIRS:
        if rel in ignored:
            chk.ok(f"gitignore cubre carpeta sensible: {rel}")
        else:
            chk.error(f"carpeta sensible NO esta en .gitignore: {rel}")


def check_no_versionable_raw(chk: Check) -> None:
    """Las carpetas crudas/internas no deben contener datos que se versionarian por error."""
    data_suffixes = {".csv", ".json", ".zip", ".pdf", ".xlsx", ".parquet", ".geojson"}
    for rel in ["data/v2/raw", "data/v2/processed", "outputs/v2/internal"]:
        base = REPO_ROOT / rel
        if not base.exists():
            continue
        data_files = [p for p in base.rglob("*")
                      if p.is_file() and p.suffix.lower() in data_suffixes]
        if data_files:
            sample = [str(p.relative_to(REPO_ROOT)) for p in data_files[:5]]
            chk.warn(f"hay datos en carpeta cruda/interna {rel} (debe estar gitignored): {sample}")
        else:
            chk.ok(f"carpeta cruda/interna vacia de datos: {rel}")


def main() -> int:
    chk = Check()
    print("=" * 78)
    print("DataGastro V2 - validacion de setup (Etapa 1). No hace requests.")
    print(f"Repo: {REPO_ROOT}")
    print("=" * 78)

    check_dirs(chk)
    check_configs(chk)
    check_docs(chk)
    check_sanitized_outputs(chk)
    check_sanitized_columns(chk)
    check_privacy_sanitized(chk)
    check_internal_not_versionable(chk)
    check_schemas(chk)
    check_no_env_files(chk)
    check_no_hardcoded_keys(chk)
    check_sensitive_gitignored(chk)
    check_no_versionable_raw(chk)

    print(f"\n[OK]      {len(chk.ok_lines)} verificaciones correctas")
    for line in chk.ok_lines:
        print(f"  + {line}")
    if chk.warnings:
        print(f"\n[AVISOS]  {len(chk.warnings)}")
        for line in chk.warnings:
            print(f"  ! {line}")
    if chk.errors:
        print(f"\n[ERRORES] {len(chk.errors)}")
        for line in chk.errors:
            print(f"  x {line}")

    print("\n" + "-" * 78)
    if chk.errors:
        print("RESULTADO: HAY ERRORES. Revisar arriba.")
        return 1
    print("RESULTADO: SETUP V2 OK (Etapa 1). Sin integraciones ejecutadas.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
