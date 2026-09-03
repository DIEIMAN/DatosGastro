# -*- coding: utf-8 -*-
"""Ampliación Google Places — microzonas PolosGastro (v1). Etapa 1: consultas por zona.

EXPERIMENTO CONTROLADO. No forma parte del pipeline público F01-F05 ni de Fase 25.
NO toca los outputs del piloto exitoso (`google_places_microzonas_piloto/`): todo lo de
esta ampliación vive en `google_places_microzonas_ampliacion_v1/`.

Cubre las 7 macrozonas contenedoras que el piloto NO escaneó:
Chacarita, Villa Crespo, Puerto Madero, Recoleta, Caballito, Costanera Norte,
Avenida Caseros/Barracas. Las 6 del piloto NO se reescanean (cobertura completa del
2026-07-09; reescaneo solo se justificaría por refresco temporal o refinamiento de
celdas saturadas, no en esta tanda).

Ejecución por TANDAS (cada una bajo el hard cap y con autorización propia):
- a_criticas:       Chacarita, Puerto Madero, Costanera Norte, Caseros/Barracas
                    (F01+F02 débil o subregistro sospechado: máximo valor metodológico).
- b_consolidacion:  Recoleta, Villa Crespo, Caballito (F01+F02 razonable; Places
                    consolida y densifica).

Mismos parámetros validados en el piloto (379 consultas, 0 errores): grilla 180 m,
radio 135 m, searchNearby con includedTypes gastronómicos, FieldMask mínimo.
NOVEDAD vs. piloto: registra las celdas SATURADAS (20/20 resultados) en un QA propio,
para poder refinar con grilla fina SOLO donde haga falta en una tanda futura.

- **Dry-run (default):** plan de consultas + presupuesto por tanda. NO llama a la API.
- **Ejecución real:** `--tanda <t> --execute --confirm-real-api` + key en entorno/.env.
  Bloques con guardado incremental; reanudable sin reconsultar.

Seguridad (idéntica al piloto): key solo de entorno/.env, nunca impresa ni guardada;
sin raw JSON; place_id y campos técnicos solo en `interno/` (en .gitignore); el CSV
sanitizado no lleva place_id ni dirección.

Uso:
    .venv/Scripts/python.exe scripts/polos_gastro/historico/experimentos/google_places_microzonas_ampliacion_v1/preparar_consultas_places_ampliacion.py
    (dry-run de todas las tandas; agregar --tanda a_criticas --execute --confirm-real-api
     SOLO con autorización explícita de Diego)
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
SALIDA = ROOT / "outputs" / "polos_gastro" / "historico" / "experimentos" / "google_places_microzonas_ampliacion_v1"
DIR_PLACES = SALIDA / "places"
DIR_INTERNO = SALIDA / "interno"   # en .gitignore: place_id, campos técnicos

CRS_GEO = "EPSG:4326"
CRS_METRICO = "EPSG:5347"

# Macrozona -> (zona, tanda). Una macrozona = una zona (sin pares combinados acá).
ZONAS_AMPLIACION = {
    "MZ_CHACARITA": ("chacarita", "a_criticas"),
    "MZ_PUERTO_MADERO": ("puerto_madero", "a_criticas"),
    "MZ_COSTANERA_NORTE": ("costanera_norte", "a_criticas"),
    "MZ_AVENIDA_CASEROS_BARRACAS": ("caseros_barracas", "a_criticas"),
    "MZ_RECOLETA": ("recoleta", "b_consolidacion"),
    "MZ_VILLA_CRESPO": ("villa_crespo", "b_consolidacion"),
    "MZ_CABALLITO": ("caballito", "b_consolidacion"),
}
TANDAS = ("a_criticas", "b_consolidacion")

# Parámetros de grilla VALIDADOS en el piloto (mantener comparabilidad).
GRID_PASO_M = 180.0
RADIO_CELDA_M = 135.0
BORDE_MACROZONA_M = 40.0
SATURACION_N = 20  # searchNearby devuelve máx. 20: celda con 20 = saturada

MAX_CONSULTAS_HARD_CAP = 425   # autorización adicional 2026-07-09: <= USD 15
COSTO_USD_POR_1000 = 35.0      # SKU Enterprise (incluye rating), 2025
BLOQUE_GUARDADO = 25
TANDAS_AUTORIZADAS_EJECUCION_REAL = {"b_consolidacion"}
ZONAS_ESPERADAS_POR_TANDA = {
    "a_criticas": {"chacarita", "puerto_madero", "costanera_norte", "caseros_barracas"},
    "b_consolidacion": {"recoleta", "villa_crespo", "caballito"},
}
ERROR_ABORT_MIN_REQUESTS = 10
ERROR_ABORT_MIN_ERRORS = 5
ERROR_ABORT_RATE = 0.20

PLACES_URL = "https://places.googleapis.com/v1/places:searchNearby"
FIELD_MASK = (
    "places.id,places.displayName,places.location,places.types,"
    "places.primaryType,places.businessStatus,places.rating,places.userRatingCount"
)
INCLUDED_TYPES = ["restaurant", "cafe", "coffee_shop", "bar", "bakery",
                  "ice_cream_shop", "meal_takeaway"]
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


def rutas_tanda(tanda: str) -> dict:
    return {
        "plan": DIR_PLACES / f"plan_consultas_{tanda}.csv",
        "sanitizado": DIR_PLACES / f"places_sanitizado_{tanda}.csv",
        "saturacion": DIR_PLACES / f"qa_saturacion_{tanda}.json",
        "interno": DIR_INTERNO / f"places_resultados_interno_{tanda}.csv",
        "progreso": DIR_INTERNO / f"progreso_celdas_{tanda}.json",
    }


def normalizar_nombre(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode("ascii")
    return " ".join("".join(c if c.isalnum() or c.isspace() else " " for c in s.lower()).split())


def cargar_macrozonas():
    import geopandas as gpd
    mz = gpd.read_file(MACROZONAS).to_crs(CRS_METRICO)
    sel = mz[mz["id"].isin(ZONAS_AMPLIACION)].copy()
    faltan = set(ZONAS_AMPLIACION) - set(sel["id"])
    if faltan:
        raise SystemExit(f"Macrozonas faltantes en la capa: {faltan}")
    sel["zona_piloto"] = sel["id"].map(lambda i: ZONAS_AMPLIACION[i][0])
    sel["tanda"] = sel["id"].map(lambda i: ZONAS_AMPLIACION[i][1])
    return sel


def construir_grilla(mz):
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
                        "tanda": fila["tanda"],
                        "geometry": p,
                    })
    gdf = gpd.GeoDataFrame(celdas, geometry="geometry", crs=CRS_METRICO).to_crs(CRS_GEO)
    gdf["lat"] = gdf.geometry.y.round(6)
    gdf["lon"] = gdf.geometry.x.round(6)
    gdf["radio_m"] = RADIO_CELDA_M
    return gdf


def resumen(grilla) -> dict:
    out = {"por_tanda": {}, "total": int(len(grilla))}
    for tanda in TANDAS:
        sub = grilla[grilla["tanda"] == tanda]
        out["por_tanda"][tanda] = {
            "celdas_por_zona": sub.groupby("zona_piloto").size().to_dict(),
            "total_consultas": int(len(sub)),
            "costo_maximo_usd": round(len(sub) * COSTO_USD_POR_1000 / 1000, 2),
            "dentro_del_cap": int(len(sub)) <= MAX_CONSULTAS_HARD_CAP,
        }
    out["costo_maximo_total_usd"] = round(out["total"] * COSTO_USD_POR_1000 / 1000, 2)
    return out


def detect_api_key():
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


def call_places_nearby(lat, lon, radio, api_key):
    import requests
    headers = {"Content-Type": "application/json", "X-Goog-Api-Key": api_key,
               "X-Goog-FieldMask": FIELD_MASK}
    payload = {
        "includedTypes": INCLUDED_TYPES, "maxResultCount": 20,
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
            "lat": loc.get("latitude", ""), "lon": loc.get("longitude", ""),
            "categoria_google": p.get("primaryType", ""),
            "tipos_google": "|".join(p.get("types", []) or []),
            "business_status": p.get("businessStatus", ""),
            "rating_interno": p.get("rating", ""),
            "user_ratings_total_interno": p.get("userRatingCount", ""),
        })
    return out, ""


def es_gastronomico(categoria, tipos) -> bool:
    tokens = set()
    for campo in (categoria or "", tipos or ""):
        for t in campo.lower().split("|"):
            if t.strip():
                tokens.add(t.strip())
    return bool(tokens & CATEGORIAS_GASTRONOMICAS)


def _escribir_csv(path: Path, cols, rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def _escribir_sanitizado(path: Path, internos) -> None:
    filas = [{
        "id_punto_places": r["id_punto_places"], "zona_piloto": r["zona_piloto"],
        "macrozona_id": r["macrozona_id"], "nombre_normalizado": r["nombre_norm"],
        "lat": r["lat"], "lon": r["lon"], "categoria": r["categoria_google"],
        "rating": r.get("rating_interno", ""),
        "user_ratings_total": r.get("user_ratings_total_interno", ""),
        "business_status": r.get("business_status", ""), "fuente": "google_places",
        "fecha_consulta": r["fecha_consulta"],
    } for r in internos]
    _escribir_csv(path, COLUMNS_SANITIZADO, filas)


def do_execute(grilla, tanda: str) -> int:
    rutas = rutas_tanda(tanda)
    sub = grilla[grilla["tanda"] == tanda]
    if tanda not in TANDAS_AUTORIZADAS_EJECUCION_REAL:
        print(f"ERROR: la ejecución real de {tanda} no está autorizada en esta corrida. "
              "Sin llamadas.", file=sys.stderr)
        return 7
    zonas_reales = set(sub["zona_piloto"])
    zonas_esperadas = ZONAS_ESPERADAS_POR_TANDA.get(tanda, set())
    if zonas_reales != zonas_esperadas:
        print(f"ERROR: zonas inesperadas para {tanda}: reales={sorted(zonas_reales)} "
              f"esperadas={sorted(zonas_esperadas)}. Sin llamadas.", file=sys.stderr)
        return 8
    if len(sub) > MAX_CONSULTAS_HARD_CAP:
        print(f"ERROR: la tanda {tanda} ({len(sub)}) excede el cap "
              f"({MAX_CONSULTAS_HARD_CAP}). Sin llamadas.", file=sys.stderr)
        return 5
    api_key, estado = detect_api_key()
    print(f"[execute:{tanda}] API key: {estado}")
    if not api_key:
        print("ERROR: falta API key (GOOGLE_MAPS_API_KEY / GOOGLE_PLACES_API_KEY). "
              "No se realizó ninguna llamada.", file=sys.stderr)
        return 3

    DIR_INTERNO.mkdir(parents=True, exist_ok=True)
    hechas, internos, saturadas = set(), [], {}
    if rutas["progreso"].exists():
        hechas = set(json.loads(rutas["progreso"].read_text(encoding="utf-8")))
        if rutas["interno"].exists():
            with rutas["interno"].open("r", encoding="utf-8-sig", newline="") as fh:
                internos = list(csv.DictReader(fh))
        if rutas["saturacion"].exists():
            saturadas = json.loads(rutas["saturacion"].read_text(encoding="utf-8")).get(
                "celdas_saturadas", {})
        print(f"[execute:{tanda}] reanudando: {len(hechas)} celdas hechas.", file=sys.stderr)

    vistos = {r.get("google_place_id_interno") for r in internos}
    today = date.today().isoformat()
    pendientes = [r for _, r in sub.iterrows() if r["celda_id"] not in hechas]
    n_req = n_err = 0
    seq = len(internos)

    def guardar():
        _escribir_csv(rutas["interno"], COLUMNS_INTERNO, internos)
        _escribir_sanitizado(rutas["sanitizado"], internos)
        rutas["progreso"].write_text(json.dumps(sorted(hechas)), encoding="utf-8")
        rutas["saturacion"].parent.mkdir(parents=True, exist_ok=True)
        rutas["saturacion"].write_text(json.dumps({
            "nota": "celdas con 20/20 resultados: cobertura saturada, candidatas a "
                    "refinamiento con grilla fina en una tanda futura",
            "n_celdas_saturadas": len(saturadas),
            "celdas_saturadas": saturadas,
        }, ensure_ascii=False, indent=2), encoding="utf-8")

    for i, r in enumerate(pendientes, 1):
        lugares, err = call_places_nearby(float(r["lat"]), float(r["lon"]),
                                          float(r["radio_m"]), api_key)
        n_req += 1
        hechas.add(r["celda_id"])
        if err and lugares is None:
            n_err += 1
            if (n_req >= ERROR_ABORT_MIN_REQUESTS and n_err >= ERROR_ABORT_MIN_ERRORS
                    and (n_err / n_req) >= ERROR_ABORT_RATE):
                guardar()
                print(f"ERROR: tasa anormal de errores ({n_err}/{n_req}). "
                      "Ejecución abortada.", file=sys.stderr)
                return 6
        else:
            if len(lugares) >= SATURACION_N:
                saturadas[r["celda_id"]] = len(lugares)
            for p in lugares:
                pid = p["google_place_id_interno"]
                if not pid or pid in vistos:
                    continue
                if not es_gastronomico(p["categoria_google"], p["tipos_google"]):
                    continue
                if (p.get("business_status") or "OPERATIONAL").upper() != "OPERATIONAL":
                    continue
                vistos.add(pid)
                seq += 1
                internos.append({
                    "id_punto_places": f"PA{seq:04d}",
                    "zona_piloto": r["zona_piloto"], "macrozona_id": r["macrozona_id"],
                    "celda_id": r["celda_id"],
                    "nombre_norm": normalizar_nombre(p["nombre_google"]),
                    "fecha_consulta": today, **p,
                })
        if i % BLOQUE_GUARDADO == 0:
            guardar()
            print(f"[execute:{tanda}] {i}/{len(pendientes)} celdas | únicos: "
                  f"{len(internos)} | saturadas: {len(saturadas)} | err: {n_err}",
                  file=sys.stderr)
        time.sleep(0.12)

    guardar()
    print(f"[execute:{tanda}] TOTAL consultas: {n_req} | puntos únicos: {len(internos)} "
          f"| celdas saturadas: {len(saturadas)} | errores: {n_err}")
    print(f"[execute:{tanda}] interno (NO publicable): {rutas['interno']}")
    print(f"[execute:{tanda}] sanitizado (sin place_id): {rutas['sanitizado']}")
    print("[execute] No se guardó raw JSON ni la API key.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Ampliación Places por tandas (dry-run default, sin API).")
    ap.add_argument("--tanda", choices=TANDAS,
                    help="Tanda a ejecutar (obligatoria con --execute).")
    ap.add_argument("--execute", action="store_true",
                    help="Intención de ejecución real. Requiere --tanda y --confirm-real-api.")
    ap.add_argument("--confirm-real-api", action="store_true",
                    help="Segunda confirmación obligatoria para llamar a la API real.")
    args = ap.parse_args()

    mz = cargar_macrozonas()
    grilla = construir_grilla(mz)
    DIR_PLACES.mkdir(parents=True, exist_ok=True)
    for tanda in TANDAS:
        sub = grilla[grilla["tanda"] == tanda]
        cols = ["celda_id", "zona_piloto", "macrozona_id", "lat", "lon", "radio_m"]
        sub[cols].to_csv(rutas_tanda(tanda)["plan"], index=False, encoding="utf-8")

    res = resumen(grilla)
    print("[plan] === Ampliación Google Places v1 (7 macrozonas pendientes) ===")
    for tanda in TANDAS:
        r = res["por_tanda"][tanda]
        print(f"[plan] tanda {tanda}: {r['total_consultas']} consultas "
              f"(cap {MAX_CONSULTAS_HARD_CAP}: {'OK' if r['dentro_del_cap'] else 'EXCEDE'}) "
              f"| costo máx. USD {r['costo_maximo_usd']}")
        for z, n in sorted(r["celdas_por_zona"].items()):
            print(f"[plan]     {z:<18} {n:>4} celdas")
    print(f"[plan] TOTAL: {res['total']} consultas | costo máx. USD "
          f"{res['costo_maximo_total_usd']}")
    print(f"[plan] planes escritos en: {DIR_PLACES}")

    if args.execute and (not args.confirm_real_api or not args.tanda):
        print("ERROR: ejecución real requiere --tanda <t> --execute --confirm-real-api. "
              "No se realizó ninguna llamada.", file=sys.stderr)
        return 2
    if args.execute and args.confirm_real_api and args.tanda:
        return do_execute(grilla, args.tanda)
    print("[dry_run] No se realizó ninguna llamada a Google Places API.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
