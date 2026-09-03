from __future__ import annotations

import argparse
import json
from pathlib import Path

from common import safe_output_path


EARTH_RADIUS_M = 6_371_008.8


def main() -> None:
    parser = argparse.ArgumentParser(description="Clustering geográfico experimental con sensibilidad")
    parser.add_argument("--input-csv", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--decision-plan", required=True, help="Lecturas y umbrales escritos antes de correr")
    parser.add_argument("--lat", default="lat")
    parser.add_argument("--lon", default="lon")
    parser.add_argument("--id", default="id")
    parser.add_argument("--method", choices=("hdbscan", "dbscan"), default="hdbscan")
    parser.add_argument("--min-cluster-size", action="append", type=int, default=[])
    parser.add_argument("--min-samples", type=int, default=3)
    parser.add_argument("--eps-m", action="append", type=float, default=[])
    args = parser.parse_args()
    decision_plan = Path(args.decision_plan)
    if not decision_plan.is_file() or not decision_plan.read_text(encoding="utf-8").strip():
        raise ValueError("El plan de decisión previo debe existir y no estar vacío")
    import numpy as np
    import pandas as pd

    frame = pd.read_csv(args.input_csv)
    for column in (args.lat, args.lon):
        if column not in frame.columns:
            raise ValueError(f"Falta la columna {column}")
    if args.id not in frame.columns:
        frame[args.id] = frame.index.astype(str)
    coordinates = frame[[args.lat, args.lon]].apply(pd.to_numeric, errors="raise")
    if not coordinates[args.lat].between(-34.8, -34.4).all() or not coordinates[args.lon].between(-58.7, -58.2).all():
        raise ValueError("Hay coordenadas fuera del rango de control de CABA")
    radians = np.radians(coordinates.to_numpy())
    curves = []
    last_labels = None
    if args.method == "hdbscan":
        import hdbscan

        values = args.min_cluster_size or [5, 10, 20]
        for value in values:
            labels = hdbscan.HDBSCAN(
                min_cluster_size=value,
                min_samples=args.min_samples,
                metric="haversine",
            ).fit_predict(radians)
            curves.append({
                "min_cluster_size": value,
                "n_clusters": int(len(set(labels)) - (1 if -1 in labels else 0)),
                "n_noise": int((labels == -1).sum()),
            })
            last_labels = labels
    else:
        from sklearn.cluster import DBSCAN

        values = args.eps_m or [80.0, 120.0, 160.0, 200.0]
        for value in values:
            labels = DBSCAN(
                eps=value / EARTH_RADIUS_M,
                min_samples=args.min_samples,
                metric="haversine",
                algorithm="ball_tree",
            ).fit_predict(radians)
            curves.append({
                "eps_m": value,
                "n_clusters": int(len(set(labels)) - (1 if -1 in labels else 0)),
                "n_noise": int((labels == -1).sum()),
            })
            last_labels = labels
    output_dir = safe_output_path(args.output_dir, directory=True)
    result = frame[[args.id, args.lat, args.lon]].copy()
    result["cluster_experimental"] = last_labels
    result.to_csv(output_dir / "clusters_experimentales.csv", index=False)
    metadata = {
        "estado": "EXPERIMENTAL / NO OFICIAL",
        "method": args.method,
        "decision_plan": str(decision_plan.resolve()),
        "sensitivity": curves,
        "warning": "Resultado del instrumento; no equivale a límites institucionales",
    }
    (output_dir / "sensibilidad.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps({"ok": True, "output_dir": str(output_dir), "sensitivity": curves}))


if __name__ == "__main__":
    main()
