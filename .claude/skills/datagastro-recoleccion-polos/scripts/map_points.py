from __future__ import annotations

import argparse
import json

from common import safe_output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Mapa Folium interno sin popups identificables")
    parser.add_argument("--input-csv", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--lat", default="lat")
    parser.add_argument("--lon", default="lon")
    parser.add_argument("--heatmap", action="store_true")
    args = parser.parse_args()
    import folium
    import pandas as pd
    from folium.plugins import HeatMap

    frame = pd.read_csv(args.input_csv)
    coordinates = frame[[args.lat, args.lon]].apply(pd.to_numeric, errors="raise").dropna()
    if coordinates.empty:
        raise ValueError("No hay coordenadas válidas")
    if not coordinates[args.lat].between(-34.8, -34.4).all() or not coordinates[args.lon].between(-58.7, -58.2).all():
        raise ValueError("Hay coordenadas fuera del rango de control de CABA")
    center = [float(coordinates[args.lat].median()), float(coordinates[args.lon].median())]
    map_obj = folium.Map(location=center, zoom_start=12, tiles="OpenStreetMap")
    if args.heatmap:
        HeatMap(coordinates[[args.lat, args.lon]].values.tolist(), name="densidad experimental").add_to(map_obj)
    else:
        for lat, lon in coordinates.itertuples(index=False, name=None):
            folium.CircleMarker(location=[lat, lon], radius=3, tooltip=None, popup=None).add_to(map_obj)
    folium.LayerControl().add_to(map_obj)
    output = safe_output_path(args.output)
    map_obj.save(str(output))
    print(json.dumps({"ok": True, "points": len(coordinates), "output": str(output)}))


if __name__ == "__main__":
    main()
