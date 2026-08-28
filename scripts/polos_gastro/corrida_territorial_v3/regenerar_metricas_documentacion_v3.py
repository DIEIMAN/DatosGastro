# -*- coding: utf-8 -*-
"""Regenera métricas, decisiones y documentos V3 sin alterar GeoJSON ni mapas."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pandas as pd


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("run_v3", HERE / "ejecutar_corrida_territorial_v3.py")
run = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(run)


def main() -> None:
    cfg=run.read_config(); data=run.load_data()
    results={"belgrano":run.make_belgrano(data,cfg),"recoleta":run.make_recoleta(data,cfg),"costanera":run.make_costanera(data,cfg)}
    metrics=pd.DataFrame(sum([r["models"] for r in results.values()],[]))
    run.write_csv(metrics,run.OUT/"METRICAS_MODELOS_TERRITORIALES_V3.csv")
    decisions=run.decision_matrix(metrics)
    run.write_csv(decisions,run.OUT/"MATRIZ_DECISION_TERRITORIAL_V3.csv")
    kpi=metrics.loc[metrics.modelo.isin(["BEL-A","REC-A","CN-DEC10"]),
        ["polo","modelo","universo","puntos_incluidos","cobertura_pct","componentes","piezas_topologicas",
         "superficie_km2","densidad_puntos_km2","estabilidad","dependencia_places_pct","puntos_sin_asignar"]]
    run.write_csv(kpi,run.OUT/"KPI_LOCK_CARTOGRAFICO_V3.csv")
    snapshot=pd.read_csv(run.OUT/"SNAPSHOT_INSUMOS_TERRITORIALES_V3.csv")
    meta=json.loads((run.OUT/"METADATA_CORRIDA_TERRITORIAL_V3.json").read_text(encoding="utf-8"))
    run.documentation(results,metrics,decisions,snapshot,cfg,meta["contrato_editorial"],True)


if __name__ == "__main__":
    main()
