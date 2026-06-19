"""Exploración OSM/Overpass de casas/fábricas de pastas en CABA (fuente auxiliar).

OSM es colaborativo, incompleto y heterogéneo: se usa como fuente AUXILIAR de contraste, NO como
padrón oficial. Por defecto NO hace red (imprime la consulta). Con `--run` consulta Overpass y
guarda resultados clasificados con el mismo criterio estricto A/B/C.

Uso:
  python scripts/casas_pastas/explore_osm_casas_pastas.py          # dry-run
  python scripts/casas_pastas/explore_osm_casas_pastas.py --run    # consulta y guarda
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from pastas_patterns import classify  # noqa: E402

OUT = ROOT / "outputs" / "casas_pastas"
ENDPOINT = "https://overpass-api.de/api/interpreter"
USER_AGENT = "DataGastro/casas_pastas exploratorio (uso institucional CABA)"


def build_query() -> str:
    """POIs de pastas en CABA: tag shop=pasta y nombres con términos de pastas."""
    name_re = "(pastas?|raviol|sorrentino|noqui|ñoqui|fideos? frescos|tallarines? frescos|pastificio|canelon|agnolot|capelet)"
    return f"""[out:json][timeout:120];
area["boundary"="administrative"]["name"="Ciudad Autónoma de Buenos Aires"]->.caba;
(
  nwr["shop"="pasta"](area.caba);
  nwr["shop"]["name"~"{name_re}",i](area.caba);
  nwr["craft"="pasta"](area.caba);
  nwr["amenity"]["name"~"{name_re}",i](area.caba);
);
out tags center;
"""


def run_query(query: str) -> dict:
    import urllib.parse
    import urllib.request

    data = urllib.parse.urlencode({"data": query}).encode("utf-8")
    req = urllib.request.Request(ENDPOINT, data=data, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=180) as resp:  # noqa: S310 (endpoint fijo público)
        return json.loads(resp.read().decode("utf-8"))


def to_geojson_and_csv(result: dict):
    feats, rows = [], []
    for el in result.get("elements", []):
        tags = el.get("tags", {})
        name = tags.get("name", "")
        shop = tags.get("shop", "")
        cuisine = tags.get("cuisine", "")
        craft = tags.get("craft", "")
        c = classify(name, shop, craft, cuisine)
        # shop=pasta / craft=pasta es el tag explicito de OSM para casa/fabrica de pastas -> A
        if shop == "pasta" or craft == "pasta":
            cat = c["categoria_pastas"] if c["nivel"] == "A" else "casa_pastas_osm"
            c = {"nivel": "A", "categoria_pastas": cat, "patron_detectado": "osm_shop_pasta",
                 "confianza_categoria": 0.8, "motivo_categoria": "OSM tag shop=pasta/craft=pasta"}
        lat = el.get("lat") or (el.get("center") or {}).get("lat")
        lon = el.get("lon") or (el.get("center") or {}).get("lon")
        rows.append({
            "fuente": "OSM", "osm_type": el.get("type", ""), "osm_id": el.get("id", ""),
            "nombre_original": name, "shop": shop, "craft": tags.get("craft", ""), "cuisine": cuisine,
            "nivel_universo": c["nivel"], "categoria_pastas": c["categoria_pastas"],
            "patron_detectado": c["patron_detectado"], "confianza_categoria": c["confianza_categoria"],
            "addr": tags.get("addr:street", "") + " " + tags.get("addr:housenumber", ""),
            "lat": lat, "lon": lon,
        })
        if lat and lon:
            feats.append({"type": "Feature",
                          "geometry": {"type": "Point", "coordinates": [lon, lat]},
                          "properties": {k: rows[-1][k] for k in ("nombre_original", "shop", "nivel_universo", "categoria_pastas")}})
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "osm_casas_pastas_raw.geojson").write_text(
        json.dumps({"type": "FeatureCollection", "features": feats}, ensure_ascii=False), encoding="utf-8")
    with (OUT / "osm_casas_pastas_candidatos.csv").open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()) if rows else
                           ["fuente", "osm_type", "osm_id", "nombre_original", "shop", "craft",
                            "cuisine", "nivel_universo", "categoria_pastas", "patron_detectado",
                            "confianza_categoria", "addr", "lat", "lon"], extrasaction="ignore")
        w.writeheader(); w.writerows(rows)
    return len(rows), len(feats)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true", help="Ejecuta la consulta Overpass (red)")
    args = parser.parse_args()

    query = build_query()
    print("# Consulta Overpass — casas/fábricas de pastas en CABA\n")
    print(query)
    if not args.run:
        print("[dry-run] sin red. Usá --run para consultar.")
        print("Recordatorio: OSM es auxiliar, colaborativo e incompleto; no es padrón oficial.")
        return
    print("[run] consultando Overpass...")
    result = run_query(query)
    n, g = to_geojson_and_csv(result)
    print(f"POIs OSM: {n} | geolocalizados: {g}")
    print("Guardado: osm_casas_pastas_raw.geojson, osm_casas_pastas_candidatos.csv")
    print("Clasificados con criterio estricto A/B/C. Revisar antes de unir al maestro.")


if __name__ == "__main__":
    main()
