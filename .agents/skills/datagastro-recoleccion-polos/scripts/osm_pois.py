from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from common import safe_output_path


TAGS = {"amenity": ["restaurant", "cafe", "bar", "fast_food", "food_court"]}


def main() -> None:
    parser = argparse.ArgumentParser(description="POIs gastronómicos OSM/Overpass, fuente E abierta")
    parser.add_argument("--place", required=True)
    parser.add_argument("--output-dir", default=".agent-tools/osm")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    plan = {
        "place": args.place,
        "tags": TAGS,
        "fuente": "OpenStreetMap/Overpass",
        "licencia": "ODbL",
        "universo": "oferta_visible_en_OSM",
        "advertencia": "No es padrón ni prueba de actividad actual",
    }
    if args.dry_run:
        print(json.dumps({"dry_run": True, **plan}, ensure_ascii=False))
        return
    output_dir = safe_output_path(args.output_dir, directory=True)
    import osmnx as ox

    gdf = ox.features_from_place(args.place, TAGS)
    if gdf.empty:
        raise RuntimeError("La consulta no encontró POIs con la cobertura disponible")
    keep = [column for column in ("name", "amenity", "cuisine", "geometry") if column in gdf.columns]
    gdf = gdf[keep].reset_index(drop=True)
    geojson = output_dir / "osm_pois.geojson"
    gdf.to_file(geojson, driver="GeoJSON")
    metadata = {
        **plan,
        "fecha_consulta_utc": datetime.now(timezone.utc).isoformat(),
        "registros": int(len(gdf)),
        "archivo": str(Path(geojson).name),
        "estado": "EXPERIMENTAL / NO OFICIAL",
    }
    (output_dir / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps({"ok": True, "registros": len(gdf), "output_dir": str(output_dir)}))


if __name__ == "__main__":
    main()
