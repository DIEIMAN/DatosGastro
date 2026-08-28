# -*- coding: utf-8 -*-
"""Regenera solamente mapas V3 desde capas y configuración reproducibles."""
from __future__ import annotations

import importlib.util
from pathlib import Path


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("run_v3", HERE / "ejecutar_corrida_territorial_v3.py")
run = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(run)


def main() -> None:
    cfg=run.read_config(); data=run.load_data()
    results={"belgrano":run.make_belgrano(data,cfg),"recoleta":run.make_recoleta(data,cfg),"costanera":run.make_costanera(data,cfg)}
    run.generate_maps(data,results["belgrano"],"belgrano","Polo Gastronómico Belgrano","BEL-A",cfg)
    run.generate_maps(data,results["recoleta"],"recoleta","Polo Gastronómico Recoleta","REC-A",cfg)
    run.generate_maps(data,results["costanera"],"costanera_norte","Polo Gastronómico Costanera Norte","CN-DEC10",cfg)


if __name__ == "__main__":
    main()
