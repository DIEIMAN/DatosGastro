"""Exploración de oferta gastronómica en OpenStreetMap (Overpass) para CABA.

Fuente E05 (OSM/Overpass): abierta, ODbL, sin scraping de plataformas privadas.

Por defecto NO hace red: imprime la consulta Overpass y dónde se guardaría. Con `--run`
ejecuta la consulta contra un endpoint Overpass público (respetando límites de uso) y guarda
el GeoJSON/JSON crudo en data/fuentes_externas/osm_explore/ (fuera del pipeline).

Reglas: no es padrón oficial; OSM es contraste/validación externa. No reemplaza F01/F02.
Ver docs/skills_claude/05_geodatos_y_territorio.md y 06_fuentes_externas_privadas.md.

Uso:
  python scripts/external_sources/explore_osm_gastro.py            # dry-run: imprime query
  python scripts/external_sources/explore_osm_gastro.py --run      # ejecuta y guarda crudo
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "data" / "fuentes_externas" / "osm_explore"
ENDPOINT = "https://overpass-api.de/api/interpreter"
USER_AGENT = "DataGastro/exploratorio (uso institucional CABA; contacto via repo)"

# Tags gastronómicos (amenity/shop) para CABA.
AMENITIES = ["restaurant", "cafe", "bar", "fast_food", "pub", "food_court", "biergarten", "ice_cream"]
SHOPS = ["bakery", "deli", "pastry", "confectionery"]


def build_query() -> str:
    """Overpass QL: POIs gastronómicos dentro del límite administrativo de CABA."""
    amenity_re = "|".join(AMENITIES)
    shop_re = "|".join(SHOPS)
    return f"""[out:json][timeout:120];
// Área administrativa de la Ciudad Autónoma de Buenos Aires
area["boundary"="administrative"]["name"="Ciudad Autónoma de Buenos Aires"]->.caba;
(
  nwr["amenity"~"^({amenity_re})$"](area.caba);
  nwr["shop"~"^({shop_re})$"](area.caba);
);
out tags center;
"""


def run_query(query: str) -> dict:
    import urllib.request
    import urllib.parse

    data = urllib.parse.urlencode({"data": query}).encode("utf-8")
    req = urllib.request.Request(ENDPOINT, data=data, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=180) as resp:  # noqa: S310 (endpoint fijo y público)
        return json.loads(resp.read().decode("utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Exploración OSM/Overpass de gastronomía en CABA")
    parser.add_argument("--run", action="store_true", help="Ejecuta la consulta (red) y guarda el crudo")
    args = parser.parse_args()

    query = build_query()
    print("# Consulta Overpass (E05 OSM) para gastronomía en CABA\n")
    print(query)
    print(f"# Endpoint: {ENDPOINT}")
    print(f"# Salida cruda iría a: {OUT_DIR}")

    if not args.run:
        print("\n[dry-run] No se hizo ninguna llamada de red. Usá --run para ejecutar.")
        print("Recordá: OSM es contraste externo, NO padrón oficial ni confirmación de actividad.")
        return

    print("\n[run] Ejecutando consulta Overpass (puede tardar)...")
    result = run_query(query)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    raw_path = OUT_DIR / f"osm_gastro_caba_{stamp}.json"
    raw_path.write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
    elements = result.get("elements", [])
    print(f"Elementos recibidos: {len(elements)}")
    print(f"Crudo guardado en: {raw_path}")
    print("Pendiente (futuro, con aprobación): normalizar tags, cruzar comuna/barrio USIG, "
          "comparar con F01/F02. No integrar al pipeline sin contrato y permiso.")


if __name__ == "__main__":
    main()
