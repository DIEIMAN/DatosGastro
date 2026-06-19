"""Valida el catálogo y la documentación de fuentes externas. NO llama APIs ni hace scraping.

Chequea:
1. Existen los artefactos esperados (catálogo csv/json, splits por prioridad, roadmap, matriz).
2. El catálogo tiene las columnas requeridas y es consistente entre CSV y JSON.
3. Ninguna fuente queda con scraping permitido (`permite_scraping` != "no" -> ERROR).
4. No hay credenciales/secretos embebidos en los archivos de fuentes externas (ERROR).
5. No se filtran datos personales evidentes (emails reales, CUIT/DNI) -> AVISO.

Sale con código != 0 si hay ERRORES. Los AVISOS no hacen fallar.

Ver docs/skills_claude/06_fuentes_externas_privadas.md y 04_pipeline_reproducible.md.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = ROOT / "config" / "fuentes_externas"
DOCS_DIR = ROOT / "docs" / "fuentes_externas"
OUT_DIR = ROOT / "outputs" / "fuentes_externas"

REQUIRED_FILES = [
    CONFIG_DIR / "matriz_fuentes_externas.csv",
    CONFIG_DIR / "catalogo_fuentes_externas.csv",
    CONFIG_DIR / "catalogo_fuentes_externas.json",
    OUT_DIR / "fuentes_prioridad_alta.csv",
    OUT_DIR / "fuentes_prioridad_media.csv",
    OUT_DIR / "fuentes_prioridad_baja.csv",
    DOCS_DIR / "ROADMAP_FUENTES_EXTERNAS.md",
]
REQUIRED_COLUMNS = [
    "id_externa", "id_matriz_original", "fuente", "grupo", "universo_sugerido",
    "prioridad_normalizada", "permite_scraping",
]
PRIORIDADES_VALIDAS = {"alta", "media", "baja"}

# patrones de secretos/credenciales (ERROR si aparecen)
SECRET_PATTERNS = [
    (r"AIza[0-9A-Za-z_\-]{30,}", "posible Google API key"),
    (r"(?i)\b(api[_-]?key|secret|token|password|passwd)\b\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{12,}", "credencial asignada"),
    (r"(?i)bearer\s+[A-Za-z0-9._\-]{20,}", "token bearer"),
    (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "clave privada"),
]
# datos personales (AVISO)
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
CUIT_RE = re.compile(r"\b\d{2}-?\d{8}-?\d\b")


def scan_files() -> tuple[list[str], list[str]]:
    errors, warnings = [], []
    targets = []
    for d in (CONFIG_DIR, DOCS_DIR, OUT_DIR):
        if d.exists():
            targets += [p for p in d.rglob("*") if p.suffix.lower() in {".md", ".csv", ".json", ".txt"}]
    for p in targets:
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for pat, label in SECRET_PATTERNS:
            if re.search(pat, text):
                errors.append(f"[SECRETO] {label} en {p.relative_to(ROOT)}")
        for m in EMAIL_RE.findall(text):
            if "[" not in m and "ejemplo" not in m.lower():
                warnings.append(f"[PERSONAL] email '{m}' en {p.relative_to(ROOT)}")
        if CUIT_RE.search(text):
            warnings.append(f"[PERSONAL] patrón tipo CUIT en {p.relative_to(ROOT)}")
    return errors, warnings


def main() -> int:
    errors, warnings = [], []

    # 1. archivos requeridos
    for f in REQUIRED_FILES:
        if not f.exists():
            errors.append(f"[FALTA] {f.relative_to(ROOT)}")

    cat_csv = CONFIG_DIR / "catalogo_fuentes_externas.csv"
    cat_json = CONFIG_DIR / "catalogo_fuentes_externas.json"
    if cat_csv.exists():
        df = pd.read_csv(cat_csv, dtype=str).fillna("")
        # 2. columnas
        missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
        if missing:
            errors.append(f"[COLUMNAS] faltan en catálogo: {missing}")
        else:
            # 3. scraping prohibido
            bad = df[df["permite_scraping"].str.lower() != "no"]
            if len(bad):
                errors.append(f"[SCRAPING] {len(bad)} fuente(s) con permite_scraping != 'no'")
            # prioridades válidas
            inval = sorted(set(df["prioridad_normalizada"]) - PRIORIDADES_VALIDAS)
            if inval:
                errors.append(f"[PRIORIDAD] valores no válidos: {inval}")
        # 4. consistencia con JSON
        if cat_json.exists():
            try:
                data = json.loads(cat_json.read_text(encoding="utf-8"))
                if len(data) != len(df):
                    errors.append(f"[CONSISTENCIA] csv={len(df)} != json={len(data)}")
            except json.JSONDecodeError as exc:
                errors.append(f"[JSON] no parsea: {exc}")

    # 5. secretos / datos personales
    e2, w2 = scan_files()
    errors += e2
    warnings += w2

    print("== Validación fuentes externas ==")
    if cat_csv.exists():
        print(f"Catálogo: {len(pd.read_csv(cat_csv))} fuentes")
    for w in warnings:
        print("AVISO:", w)
    for e in errors:
        print("ERROR:", e)
    if errors:
        print(f"\nFALLÓ: {len(errors)} error(es).")
        return 1
    print(f"\nOK: sin errores. Avisos: {len(warnings)}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
