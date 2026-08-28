# -*- coding: utf-8 -*-
"""Reanuda solo QA de privacidad, manifest, ZIP y reverificacion de una corrida V3 calculada."""
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
    if run.git_cached():
        raise RuntimeError("El staging no está vacío")
    privacy = run.privacy_scan([
        *run.DOC.rglob("*"), *run.OUT.glob("*.csv"), *run.OUT.glob("*.json"),
        *run.OUT.glob("*.geojson"), *run.OUT.glob("*.md")
    ])
    run.write_json(privacy, run.OUT / "QA_PRIVACIDAD_V3.json")
    if privacy["resultado"] != "OK":
        raise RuntimeError(f"QA privacidad pendiente: {privacy['hits']}")
    metadata_path = run.OUT / "METADATA_CORRIDA_TERRITORIAL_V3.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["privacidad"] = "OK"
    run.write_json(metadata, metadata_path)

    manifest=[]
    for base,label in [(run.DOC,"docs"),(run.OUT,"outputs"),(run.SCRIPT_DIR,"scripts")]:
        for path in sorted(p for p in base.rglob("*") if p.is_file() and run.REVIEW not in p.parents and run.EXTRACT_QA not in p.parents and p != run.ZIP_PATH):
            if "__pycache__" in path.parts or path.suffix.lower() in {".pyc", ".pyo"}:
                continue
            if path.name in {"MANIFEST_CORRIDA_TERRITORIAL_V3.csv","CHECKSUMS_SHA256.txt","QA_ZIP_EXTRACCION_V3.json","ESTADO_FINAL_TERRITORIAL_RUN_V3.json"}:
                continue
            manifest.append({"grupo":label,"ruta":path.relative_to(run.ROOT).as_posix(),"bytes":path.stat().st_size,"sha256":run.sha256(path)})
    run.write_csv(pd.DataFrame(manifest),run.OUT/"MANIFEST_CORRIDA_TERRITORIAL_V3.csv")
    checks=[f"{run.sha256(run.ROOT/r.ruta)}  {r.ruta}" for r in pd.read_csv(run.OUT/"MANIFEST_CORRIDA_TERRITORIAL_V3.csv").itertuples(index=False)]
    (run.OUT/"CHECKSUMS_SHA256.txt").write_text("\n".join(checks)+"\n",encoding="utf-8")
    size,zip_hash,zip_qa=run.build_package()
    run.write_json(zip_qa,run.OUT/"QA_ZIP_EXTRACCION_V3.json")
    if zip_qa["resultado"] != "OK":
        raise RuntimeError(f"Reverificación ZIP falló: {zip_qa['fallas']}")
    final={"estado":"TERRITORIAL_RUN_V3_COMPLETED_READY_FOR_QA","zip":run.ZIP_PATH.relative_to(run.ROOT).as_posix(),
           "zip_bytes":size,"zip_sha256":zip_hash,"staging_vacio":not run.git_cached(),
           "superficies_protegidas_ok":json.loads((run.OUT/"QA_SUPERFICIES_PROTEGIDAS_V3.json").read_text(encoding="utf-8"))["resultado"]=="OK",
           "geojson_ok":all(pd.read_csv(run.OUT/"QA_GEOJSON_CRS_V3.csv").resultado.eq("OK")),
           "imagenes_png":len(list(run.MAPS.glob("*.png"))),"zip_qa":zip_qa}
    run.write_json(final,run.OUT/"ESTADO_FINAL_TERRITORIAL_RUN_V3.json")
    print(json.dumps(final,ensure_ascii=False,indent=2))


if __name__ == "__main__":
    main()
