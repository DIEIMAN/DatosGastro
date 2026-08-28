from __future__ import annotations

import json
import os
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "outputs/polos_gastro/expansion_candidatos_v4_tanda1"
PLAN = ROOT / "outputs/polos_gastro/expansion_candidatos_v4_preflight/PLAN_CONSULTAS_PLACES_EXPANSION_V4.csv"


def main() -> int:
    state = json.loads((OUT / "ESTADO_PRECHECK_TANDA1_V4.json").read_text(encoding="utf-8"))
    plan = pd.read_csv(PLAN, encoding="utf-8-sig")
    gaps = plan[(plan["tanda"].astype(str) == "1") &
                (plan["estado"] == "CONSULTAR_SOLO_BRECHA")].copy()
    # This script is deliberately fail-closed. Network execution requires a separate,
    # reviewed adapter and API_READY from the precheck. It never reads .env.
    api_key_present = bool(os.environ.get("GOOGLE_MAPS_API_KEY") or
                           os.environ.get("GOOGLE_PLACES_API_KEY"))
    can_execute = state.get("api_ready") is True and api_key_present
    progress = gaps[["consulta_id", "zona_id", "subunidad_id", "celda_id", "categoría"]].copy()
    progress["estado_ejecucion"] = "NO_EJECUTADA_CREDENCIAL_AUSENTE" if not can_execute else "PENDIENTE_ADAPTADOR_REVISADO"
    progress["llamada_api_realizada"] = "NO"
    progress.to_csv(OUT / "PROGRESO_CONSULTAS_TANDA1_V4.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame([{
        "tipo": "API_NO_EJECUTADA" if not can_execute else "ADAPTADOR_NO_HABILITADO",
        "filas_categoria_celda": len(gaps),
        "celdas_fisicas": gaps["celda_id"].nunique(),
        "detalle": "Credencial no disponible en entorno autorizado; no se leyó .env."
                   if not can_execute else "Requiere revisión humana del adaptador acotado.",
    }]).to_csv(OUT / "FALLOS_CONSULTA_TANDA1_V4.csv", index=False, encoding="utf-8-sig")
    (OUT / "QA_SATURACION_TANDA1_V4.json").write_text(json.dumps({
        "estado": "NO_EVALUABLE_SIN_CONSULTAS_NUEVAS",
        "celdas_saturadas_nuevas": 0,
        "nota": "No se ejecutaron llamadas; no se infiere saturación nueva.",
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    pd.DataFrame(columns=["celda_id", "zona_id", "motivo", "estado_refino"]).to_csv(
        OUT / "PLAN_REFINO_PENDIENTE_TANDA1_V4.csv", index=False, encoding="utf-8-sig")
    print("NO_API_CALLS_REUSE_ONLY")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
