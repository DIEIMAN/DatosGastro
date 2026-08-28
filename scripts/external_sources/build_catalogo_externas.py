"""Normaliza la matriz de fuentes externas en un catálogo limpio + splits por prioridad.

Lee:  config/fuentes_externas/matriz_fuentes_externas.csv
Escribe:
  config/fuentes_externas/catalogo_fuentes_externas.csv
  config/fuentes_externas/catalogo_fuentes_externas.json
  data/fuentes_externas/fuentes_prioridad_alta.csv
  data/fuentes_externas/fuentes_prioridad_media.csv
  data/fuentes_externas/fuentes_prioridad_baja.csv

No llama APIs ni hace scraping. Solo transforma documentación local.
Ver docs/skills_claude/06_fuentes_externas_privadas.md y 02_metodologia_fuentes.md.
"""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "config" / "fuentes_externas" / "matriz_fuentes_externas.csv"
CONFIG_DIR = ROOT / "config" / "fuentes_externas"
OUT_DIR = ROOT / "data" / "fuentes_externas"


def norm(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(ch for ch in text if not unicodedata.combining(ch)).lower()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", text)).strip()


def prioridad_normalizada(prioridad: str) -> str:
    n = norm(prioridad)
    if "no hacer" in n:
        return "baja"
    if "muy alta" in n or "alta estrategica" in n:
        return "alta"
    if "media alta" in n:
        return "alta"
    if n == "alta":
        return "alta"
    if "media baja" in n or "baja media" in n or n == "baja":
        return "baja"
    if n == "media":
        return "media"
    return "media"


def universo_sugerido(id_matriz: str, grupo: str, acceso: str, prioridad: str) -> str:
    nid, ng, na = norm(id_matriz), norm(grupo), norm(acceso)
    if "no hacer" in norm(prioridad) or nid.startswith("scr"):
        return "no_recomendada"
    if nid.startswith("int") or "gobierno" in ng:
        return "interna_o_publica_gcba"
    if "convenio" in na or "comercial" in na:
        return "externa_privada_convenio"
    return "externa_publica_o_api"


def main() -> None:
    if not SRC.exists():
        raise SystemExit(f"No existe la matriz: {SRC}")
    df = pd.read_csv(SRC, dtype=str).fillna("")

    rows = []
    for i, r in enumerate(df.to_dict("records"), 1):
        prioridad_orig = r.get("Prioridad", "")
        rows.append({
            "id_externa": f"E{i:02d}",
            "id_matriz_original": r.get("ID", ""),
            "fuente": r.get("Fuente", ""),
            "grupo": r.get("Grupo", ""),
            "universo_sugerido": universo_sugerido(r.get("ID", ""), r.get("Grupo", ""), r.get("Acceso real", ""), prioridad_orig),
            "que_aporta": r.get("Qué aporta", ""),
            "acceso_real": r.get("Acceso real", ""),
            "api_open_data": r.get("API/open data", ""),
            "legalidad_riesgo": r.get("Legalidad/riesgo", ""),
            "granularidad": r.get("Granularidad", ""),
            "cobertura_caba": r.get("Cobertura CABA", ""),
            "prioridad_original": prioridad_orig,
            "prioridad_normalizada": prioridad_normalizada(prioridad_orig),
            "puntaje": r.get("Puntaje", ""),
            "camino_recomendado": r.get("Camino recomendado", ""),
            "accion_concreta": r.get("Acción concreta Diego", ""),
            "url": r.get("URL", ""),
            "permite_scraping": "no",  # regla dura del proyecto
        })

    cat = pd.DataFrame(rows)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    cat.to_csv(CONFIG_DIR / "catalogo_fuentes_externas.csv", index=False, encoding="utf-8-sig")
    (CONFIG_DIR / "catalogo_fuentes_externas.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

    orden = {"alta": 0, "media": 1, "baja": 2}
    for nivel in ("alta", "media", "baja"):
        sub = cat[cat["prioridad_normalizada"] == nivel].copy()
        sub = sub.sort_values(by="puntaje", key=lambda s: pd.to_numeric(s, errors="coerce"), ascending=False)
        sub.to_csv(OUT_DIR / f"fuentes_prioridad_{nivel}.csv", index=False, encoding="utf-8-sig")

    print(f"catalogo: {len(cat)} fuentes")
    print(cat["prioridad_normalizada"].value_counts().to_dict())
    print(cat["universo_sugerido"].value_counts().to_dict())


if __name__ == "__main__":
    main()
