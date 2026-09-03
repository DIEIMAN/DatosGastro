# -*- coding: utf-8 -*-
"""Piloto Google Places + microzonas — Etapa 1: consultas Places acotadas por zona.

EXPERIMENTO CONTROLADO. No forma parte del pipeline público F01-F05 ni de Fase 25.

Construye una grilla de consulta (searchNearby) acotada a las macrozonas piloto de
`macrozonas_editoriales_candidatas_v1.geojson` y:

- **Dry-run (default):** escribe SOLO el plan de consultas (celdas, centro, radio) y la
  estimación de costo. NO llama a la API. No requiere key.
- **Ejecución real:** requiere DOBLE CONFIRMACIÓN (--execute --confirm-real-api) + API key
  por entorno/.env. Corre en bloques con guardado incremental y es reanudable.

Seguridad (mismo estándar que places_repiloto_fase11.py):
- La key SOLO se lee de entorno/.env; NUNCA se imprime, guarda ni loguea.
- NO se guarda raw JSON. El CSV interno (con place_id/dirección) va a la carpeta
  `interno/` que está en .gitignore. El CSV sanitizado NO contiene place_id ni dirección.
- Hard cap absoluto de consultas por corrida (MAX_CONSULTAS_HARD_CAP).

Uso:
    .venv/Scripts/python.exe scripts/polos_gastro/historico/experimentos/google_places_microzonas_piloto/preparar_consultas_places_piloto.py
    (agregar --execute --confirm-real-api SOLO con autorización explícita de Diego)
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
import unicodedata
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]

MACROZONAS = (ROOT / "outputs" / "polos_gastro" / "historico" / "experimentos"
              / "infraestructura_cartografica_v1" / "macrozonas_editoriales_candidatas_v1.geojson")
SALIDA = ROOT / "outputs" / "polos_gastro" / "historico" / "experimentos" / "google_places_microzonas_piloto"
DIR_PLACES = SALIDA / "places"
DIR_INTERNO = SALIDA / "interno"   # en .gitignore: place_id, dirección exacta, campos técnicos

PLAN_CSV = DIR_PLACES / "plan_consultas_places.csv"
SANITIZADO_CSV = DIR_PLACES / "places_sanitizado.csv"
INTERNO_CSV = DIR_INTERNO / "places_resultados_interno.csv"
PROGRESO_JSON = DIR_INTERNO / "places_progreso_celdas.json"

CRS_GEO = "EPSG:4326"
CRS_METRICO = "EPSG:5347"  # POSGAR 2007 faja 5 (mismo del pipeline_microzonas_v1)

# Zonas piloto (pedido de Diego 2026-07-09). Ids de macrozonas_editoriales_candidatas_v1.
ZONAS_PILOTO = {
    "palermo_soho_hollywood": ["MZ_PALERMO_SOHO", "MZ_PALERMO_HOLLYWOOD"],
    "corrientes_microcentro": ["MZ_AVENIDA_CORRIENTES", "MZ_MICROCENTRO_Y_CENTRO"],
    "belgrano": ["MZ_BELGRANO"],
    "san_telmo": ["MZ_SAN_TELMO"],
}

# Grilla: paso 180 m y radio 135 m (r ~ paso/sqrt(2) + margen) cubre el cuadrado completo.
# searchNearby devuelve como máximo 20 lugares por celda: en zonas densas la celda se
# SATURA (limitación documentada: es enriquecimiento por prominencia, no censo).
GRID_PASO_M = 180.0
RADIO_CELDA_M = 135.0
BORDE_MACROZONA_M = 40.0  # celdas cuyo centro cae hasta 40 m fuera igual se incluyen

# Tope duro de consultas por corrida. Costo unitario Nearby Search con rating
# (SKU Enterprise, 2025): USD 35 / 1000 => tope de gasto <= USD 15,75 por corrida.
MAX_CONSULTAS_HARD_CAP = 450
COSTO_USD_POR_1000 = 35.0
BLOQUE_GUARDADO = 25  # guardado incremental cada N celdas

PLACES_URL = "https://places.googleapis.com/v1/places:searchNearby"
FIELD_MASK = (
    "places.id,places.displayName,places.location,places.types,"
    "places.primaryType,places.businessStatus,places.rating,places.userRatingCount"
)
# Tipos gastronómicos de Table A para includedTypes (match por CUALQUIERA).
INCLUDED_TYPES = ["restaurant", "cafe", "coffee_shop", "bar", "bakery",
                  "ice_cream_shop", "meal_takeaway"]
# Aceptación por rubro (mismo criterio que Fase 11).
CATEGORIAS_GASTRONOMICAS = {
    "restaurant", "cafe", "coffee_shop", "bar", "bakery", "meal_takeaway",
    "meal_delivery", "food", "fine_dining_restaurant", "pub", "ice_cream_shop",
    "sandwich_shop", "fast_food_restaurant", "pizza_restaurant",
}

COLUMNS_INTERNO = [
    "id_punto_places", "zona_piloto", "macrozona_id", "celda_id",
    "google_place_id_interno", "nombre_google", "nombre_norm",
    "lat", "lon", "categoria_google", "tipos_google", "business_status",
    "rating_interno", "user_ratings_total_interno", "fecha_consulta",
]
COLUMNS_SANITIZADO = [
    "id_punto_places", "zona_piloto", "macrozona_id", "nombre_normalizado",
    "lat", "lon", "categoria", "rating", "user_ratings_total",
    "business_status", "fuente", "fecha_consulta",
]


def normalizar_nombre(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode("ascii")
    return " ".join("".join(c if c.isalnum() or c.isspace() else " " for c in s.lower()).split())


def cargar_macrozonas_piloto():
    import geopandas as gpd
    mz = gpd.read_file(MACROZONAS).to_crs(CRS_METRICO)
    ids = [i for v in ZONAS_PILOTO.values() for i in v]
    sel = mz[mz["id"].isin(ids)].copy()
    faltan = set(ids) - set(sel["id"])
    if faltan:
        raise SystemExit(f"Macrozonas piloto faltantes en la capa: {faltan}")
    zona_de = {i: z for z, lst in ZONAS_PILOTO.items() for i in lst}
    sel["zona_piloto"] = sel["id"].map(zona_de)
    return sel


def construir_grilla(mz):
    """Celdas (centros) por macrozona en grilla cuadrada de GRID_PASO_M."""
    import geopandas as gpd
    import numpy as np
    from shapely.geometry import Point

    celdas = []
    for _, fila in mz.iterrows():
        geom = fila.geometry.buffer(BORDE_MACROZONA_M)
        minx, miny, maxx, maxy = geom.bounds
        xs = np.arange(minx + GRID_PASO_M / 2, maxx, GRID_PASO_M)
        ys = np.arange(miny + GRID_PASO_M / 2, maxy, GRID_PASO_M)
        n = 0
        for x in xs:
            for y in ys:
                p = Point(x, y)
                if geom.contains(p):
                    n += 1
                    celdas.append({
                        "celda_id": f"{fila['id']}_C{n:03d}",
                        "zona_piloto": fila["zona_piloto"],
                        "macrozona_id": fila["id"],
                        "geometry": p,
                    })
    gdf = gpd.GeoDataFrame(celdas, geometry="geometry", crs=CRS_METRICO).to_crs(CRS_GEO)
    gdf["lat"] = gdf.geometry.y.round(6)
    gdf["lon"] = gdf.geometry.x.round(6)
    gdf["radio_m"] = RADIO_CELDA_M
    return gdf


def escribir_plan(grilla) -> None:
    DIR_PLACES.mkdir(parents=True, exist_ok=True)
    cols = ["celda_id", "zona_piloto", "macrozona_id", "lat", "lon", "radio_m"]
    grilla[cols].to_csv(PLAN_CSV, index=False, encoding="utf-8")


def resumen_plan(grilla) -> dict:
    por_zona = grilla.groupby("zona_piloto").size().to_dict()
    total = int(len(grilla))
    return {
        "celdas_por_zona": por_zona,
        "total_consultas": total,
        "hard_cap": MAX_CONSULTAS_HARD_CAP,
        "costo_maximo_estimado_usd": round(total * COSTO_USD_POR_1000 / 1000, 2),
        "dentro_del_cap": total <= MAX_CONSULTAS_HARD_CAP,
    }


def detect_api_key():
    """(key, estado). NUNCA imprime la key ni el contenido del .env."""
    vals = {}
    envp = ROOT / ".env"
    if envp.exists():
        for line in envp.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                vals[k.strip()] = v.strip().strip('"').strip("'")
    for name in ("GOOGLE_MAPS_API_KEY", "GOOGLE_PLACES_API_KEY"):
        v = os.environ.get(name) or vals.get(name)
        if v:
            return v, f"{name} (presente)"
    return None, "ausente"


def call_places_nearby(lat: float, lon: float, radio: float, api_key: str):
    """searchNearby. Devuelve (lista_places_min, error). No expone key ni raw JSON."""
    import requests
    headers = {"Content-Type": "application/json", "X-Goog-Api-Key": api_key,
               "X-Goog-FieldMask": FIELD_MASK}
    payload = {
        "includedTypes": INCLUDED_TYPES,
        "maxResultCount": 20,
        "locationRestriction": {"circle": {
            "center": {"latitude": lat, "longitude": lon}, "radius": radio}},
        "languageCode": "es", "regionCode": "AR",
    }
    try:
        resp = requests.post(PLACES_URL, headers=headers, data=json.dumps(payload), timeout=20)
    except Exception as exc:
        return None, f"network_error: {type(exc).__name__}"
    if resp.status_code != 200:
        return None, f"http_{resp.status_code}"
    try:
        data = resp.json()
    except Exception:
        return None, "invalid_json"
    out = []
    for p in data.get("places") or []:
        loc = p.get("location") or {}
        out.append({
            "google_place_id_interno": p.get("id", ""),
            "nombre_google": (p.get("displayName") or {}).get("text", ""),
            "lat": loc.get("latitude", ""),
            "lon": loc.get("longitude", ""),
            "categoria_google": p.get("primaryType", ""),
            "tipos_google": "|".join(p.get("types", []) or []),
            "business_status": p.get("businessStatus", ""),
            "rating_interno": p.get("rating", ""),
            "user_ratings_total_interno": p.get("userRatingCount", ""),
        })
    return out, ""


def es_gastronomico(categoria: str, tipos: str) -> bool:
    tokens = set()
    for campo in (categoria or "", tipos or ""):
        for t in campo.lower().split("|"):
            if t.strip():
                tokens.add(t.strip())
    return bool(tokens & CATEGORIAS_GASTRONOMICAS)


def do_execute(grilla, resumen: dict) -> int:
    api_key, estado = detect_api_key()
    print(f"[execute] API key: {estado}")
    if not api_key:
        print("ERROR: falta API key (GOOGLE_MAPS_API_KEY / GOOGLE_PLACES_API_KEY). "
              "No se realizó ninguna llamada.", file=sys.stderr)
        return 3
    if not resumen["dentro_del_cap"]:
        print(f"ERROR: el plan ({resumen['total_consultas']}) excede el hard cap "
              f"({MAX_CONSULTAS_HARD_CAP}). Reducir grilla. Sin llamadas.", file=sys.stderr)
        return 5

    DIR_INTERNO.mkdir(parents=True, exist_ok=True)
    hechas = set()
    internos = []
    if PROGRESO_JSON.exists():
        hechas = set(json.loads(PROGRESO_JSON.read_text(encoding="utf-8")))
        if INTERNO_CSV.exists():
            with INTERNO_CSV.open("r", encoding="utf-8-sig", newline="") as fh:
                internos = list(csv.DictReader(fh))
        print(f"[execute] reanudando: {len(hechas)} celdas ya consultadas.", file=sys.stderr)

    vistos = {r.get("google_place_id_interno") for r in internos}
    today = date.today().isoformat()
    pendientes = [r for _, r in grilla.iterrows() if r["celda_id"] not in hechas]
    n_req = n_err = 0
    seq = len(internos)

    def guardar():
        _escribir_csv(INTERNO_CSV, COLUMNS_INTERNO, internos)
        _escribir_sanitizado(internos)
        PROGRESO_JSON.write_text(json.dumps(sorted(hechas)), encoding="utf-8")

    for i, r in enumerate(pendientes, 1):
        lugares, err = call_places_nearby(float(r["lat"]), float(r["lon"]),
                                          float(r["radio_m"]), api_key)
        n_req += 1
        hechas.add(r["celda_id"])
        if err and lugares is None:
            n_err += 1
        else:
            for p in lugares:
                pid = p["google_place_id_interno"]
                if not pid or pid in vistos:
                    continue  # dedup entre celdas solapadas
                if not es_gastronomico(p["categoria_google"], p["tipos_google"]):
                    continue
                if (p.get("business_status") or "OPERATIONAL").upper() != "OPERATIONAL":
                    continue
                vistos.add(pid)
                seq += 1
                internos.append({
                    "id_punto_places": f"PL{seq:04d}",
                    "zona_piloto": r["zona_piloto"], "macrozona_id": r["macrozona_id"],
                    "celda_id": r["celda_id"], "nombre_norm": normalizar_nombre(p["nombre_google"]),
                    "fecha_consulta": today, **p,
                })
        if i % BLOQUE_GUARDADO == 0:
            guardar()
            print(f"[execute] {i}/{len(pendientes)} celdas | puntos únicos: {len(internos)} "
                  f"| errores: {n_err}", file=sys.stderr)
        time.sleep(0.12)  # pacing suave para no golpear rate limits

    guardar()
    print(f"[execute] TOTAL consultas: {n_req} | puntos gastronómicos únicos: {len(internos)} "
          f"| errores: {n_err}")
    print(f"[execute] interno (NO publicable, gitignore): {INTERNO_CSV}")
    print(f"[execute] sanitizado (sin place_id):          {SANITIZADO_CSV}")
    print("[execute] No se guardó raw JSON ni la API key.")
    return 0


def _escribir_csv(path: Path, cols, rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def _escribir_sanitizado(internos) -> None:
    filas = [{
        "id_punto_places": r["id_punto_places"], "zona_piloto": r["zona_piloto"],
        "macrozona_id": r["macrozona_id"], "nombre_normalizado": r["nombre_norm"],
        "lat": r["lat"], "lon": r["lon"], "categoria": r["categoria_google"],
        "rating": r.get("rating_interno", ""),
        "user_ratings_total": r.get("user_ratings_total_interno", ""),
        "business_status": r.get("business_status", ""), "fuente": "google_places",
        "fecha_consulta": r["fecha_consulta"],
    } for r in internos]
    _escribir_csv(SANITIZADO_CSV, COLUMNS_SANITIZADO, filas)


def main() -> int:
    ap = argparse.ArgumentParser(description="Consultas Places por zona piloto (dry-run default).")
    ap.add_argument("--execute", action="store_true",
                    help="Intención de ejecución real. Requiere ADEMÁS --confirm-real-api.")
    ap.add_argument("--confirm-real-api", action="store_true",
                    help="Segunda confirmación obligatoria para llamar a la API real.")
    args = ap.parse_args()

    mz = cargar_macrozonas_piloto()
    grilla = construir_grilla(mz)
    escribir_plan(grilla)
    res = resumen_plan(grilla)
    print("[plan] celdas por zona:", json.dumps(res["celdas_por_zona"], ensure_ascii=False))
    print(f"[plan] total consultas: {res['total_consultas']} (cap {MAX_CONSULTAS_HARD_CAP}) | "
          f"costo máx. estimado: USD {res['costo_maximo_estimado_usd']}")
    print(f"[plan] plan escrito en: {PLAN_CSV}")

    if args.execute and not args.confirm_real_api:
        print("ERROR: doble confirmación requerida (--execute --confirm-real-api). "
              "No se realizó ninguna llamada.", file=sys.stderr)
        return 2
    if args.execute and args.confirm_real_api:
        return do_execute(grilla, res)
    print("[dry_run] No se realizó ninguna llamada a Google Places API.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
