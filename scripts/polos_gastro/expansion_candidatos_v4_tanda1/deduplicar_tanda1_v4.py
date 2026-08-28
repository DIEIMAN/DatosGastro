from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "outputs/polos_gastro/expansion_candidatos_v4_tanda1"
UNIVERSE = ROOT / "outputs/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/completa_v1/UNIVERSO_COMPLETO_SANITIZADO.csv"


def main() -> int:
    df = pd.read_csv(UNIVERSE, encoding="utf-8-sig")
    report = {
        "estado": "REUTILIZADA_DEDUPLICACION_COMPLETA_V1",
        "filas_entrada": int(len(df)),
        "ids_unicos": int(df["id_punto"].nunique()),
        "ids_duplicados": int(df["id_punto"].duplicated().sum()),
        "filas_nuevas_api": 0,
        "deduplicacion_entre_ventanas_nueva": "NO_APLICA",
        "deduplicacion_entre_zonas": "asignacion analitica multizona; punto base conservado una sola vez por id_punto",
        "nota": "Se reutiliza el universo sanitizado ya deduplicado; no se reabre la tabla interna protegida.",
    }
    (OUT / "QA_DEDUPLICACION_TANDA1_V4.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    return 0 if report["ids_duplicados"] == 0 and report["filas_entrada"] == 6461 else 2


if __name__ == "__main__":
    raise SystemExit(main())
