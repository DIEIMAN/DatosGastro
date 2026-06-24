"""Enriquecimiento con Google Places API (Text Search New) para mercados gastronomicos (CABA).

MODO SEGURO:
  - La API key se lee SOLO de variable de entorno (GOOGLE_PLACES_API_KEY o GOOGLE_MAPS_API_KEY)
    o de un .env local (gitignored). NUNCA se imprime, loguea ni se escribe en outputs.
  - Modo por defecto dry-run (no hace requests). Sin --mode run no hay llamada real.
  - Topes duros: --max-queries y --max-results-per-query.
  - Crudos JSON -> outputs/mercados_caba/internal/google_places_raw/ (GITIGNORED).
  - Staging interno con place_id/direccion -> internal (GITIGNORED).
  - Outputs sanitizados SIN place_id, telefono, email ni direccion individual.

Uso:
    python src/mercados_caba/google_places_mercados_enrichment.py --mode dry-run
    python src/mercados_caba/google_places_mercados_enrichment.py --mode run --max-queries 5 --max-results-per-query 5
    python src/mercados_caba/google_places_mercados_enrichment.py --mode run --max-queries 25 --max-results-per-query 10
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import time
import unicodedata
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SAN_OUT = REPO_ROOT / "outputs" / "mercados_caba" / "sanitized"
INTERNAL = REPO_ROOT / "outputs" / "mercados_caba" / "internal"
RAW_OUT = INTERNAL / "google_places_raw"

PLACES_URL = "https://places.googleapis.com/v1/places:searchText"
# Mascara de campos acotada (controla costo). Incluye campos para horarios/web/estado.
FIELD_MASK = ",".join([
    "places.id", "places.displayName", "places.formattedAddress", "places.location",
    "places.businessStatus", "places.types", "places.rating", "places.userRatingCount",
    "places.websiteUri", "places.googleMapsUri", "places.regularOpeningHours.weekdayDescriptions",
])
USD_POR_REQUEST_REF = 0.032  # orden de magnitud; CONFIRMAR contra pricing vigente

# Bounding box aproximado de CABA. Places API usa 'latitude'/'longitude'.
CABA = {"low": {"latitude": -34.706, "longitude": -58.532},
        "high": {"latitude": -34.526, "longitude": -58.335}}

KEY_NAMES = ("GOOGLE_PLACES_API_KEY", "GOOGLE_MAPS_API_KEY")

VALIDATION_TARGETS = [
    ("MG-0001", "Mercado de San Telmo CABA", "San Telmo"),
    ("MG-0002", "Mercado de Belgrano CABA", "Belgrano"),
    ("MG-0003", "Mercado del Progreso CABA", "Caballito"),
    ("MG-0004", "Mercat Villa Crespo CABA", "Villa Crespo"),
    ("MG-0005", "Mercado Soho CABA", "Palermo"),
    ("MG-0006", "Patio de los Lecheros CABA", "Caballito"),
    ("MG-0008", "Mercado Bonpland CABA", "Palermo"),
    ("MG-0009", "El Galpon Chacarita CABA", "Chacarita"),
    ("MG-0010", "Smart Plaza Parque Patricios CABA", "Parque Patricios"),
    ("MG-0011", "Patio Costanera Norte CABA", "Costanera Norte"),
    ("MG-0012", "Patio Rodrigo Bueno CABA", "Puerto Madero"),
    ("MG-0013", "Mercado San Nicolas CABA", "San Nicolas"),
    ("MG-0014", "Mercat Caballito CABA", "Caballito"),
    ("MG-0015", "Buenos Aires Market CABA", "itinerante"),
    ("MG-0016", "Sabe la Tierra CABA", "itinerante"),
]
DISCOVERY_QUERIES = [
    "mercado gastronomico CABA", "mercado de comidas CABA", "food hall Buenos Aires",
    "mercado de productores CABA", "mercado gourmet Buenos Aires",
    "mercado gastronomico Palermo CABA", "mercado gastronomico San Telmo CABA",
    "mercado gastronomico Belgrano CABA", "mercado gastronomico Caballito CABA",
    "feria gastronomica CABA", "mercado de alimentos CABA", "patio gastronomico CABA",
]
# Nombres de los 15 activos para deduplicar descubrimiento.
ACTIVE_NAMES = [t[1].replace(" CABA", "") for t in VALIDATION_TARGETS]


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode()
    return " ".join(s.lower().split())


def get_api_key() -> str | None:
    for name in KEY_NAMES:
        key = os.environ.get(name)
        if key:
            return key
    env = REPO_ROOT / ".env"
    if env.is_file():
        for ln in env.read_text(encoding="utf-8-sig", errors="ignore").splitlines():
            ln = ln.strip()
            if "=" not in ln or ln.startswith("#"):
                continue
            name, val = ln.split("=", 1)
            if name.strip() in KEY_NAMES:
                return val.strip().strip('"').strip("'") or None
    return None


def in_caba(loc: dict | None) -> bool:
    if not loc:
        return True  # sin dato: no descartar
    lat, lng = loc.get("latitude"), loc.get("longitude")
    if lat is None or lng is None:
        return True
    return (CABA["low"]["latitude"] <= lat <= CABA["high"]["latitude"]
            and CABA["low"]["longitude"] <= lng <= CABA["high"]["longitude"])


def matches_active(name: str) -> bool:
    n = norm(name)
    for a in ACTIVE_NAMES:
        na = norm(a)
        if na in n or n in na:
            return True
        ta, tn = set(na.split()), set(n.split())
        if ta and len(ta & tn) / len(ta) >= 0.6:
            return True
    return False


def classify_omitido(name: str, types: list[str], loc: dict | None) -> str:
    t = set(types or [])
    n = norm(name)
    if not in_caba(loc):
        return "fuera_de_caba"
    if "supermarket" in t:
        return "supermercado_no_mercado"
    if t & {"shopping_mall", "department_store"}:
        return "shopping_o_galeria"
    if "market" in t or "mercado" in n or "market" in n or "food hall" in n or "mercat" in n:
        return "posible_mercado_gastronomico"
    if "feria" in n:
        return "posible_feria_gastronomica"
    if "food_court" in t:
        return "posible_food_hall"
    if t & {"restaurant", "cafe", "bar", "meal_takeaway"}:
        return "restaurante_individual_no_mercado"
    return "dudoso_pendiente_revision"


def tipos_resumidos(types: list[str]) -> str:
    keep = [x for x in (types or []) if x not in {"point_of_interest", "establishment"}]
    return "|".join(keep[:4]) if keep else "sin_tipos"


def search_text(query: str, key: str, max_results: int):
    body = json.dumps({
        "textQuery": query,
        "languageCode": "es",
        "regionCode": "AR",
        "maxResultCount": max(1, min(int(max_results), 20)),
        "locationBias": {"rectangle": CABA},
    }).encode("utf-8")
    req = urllib.request.Request(PLACES_URL, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("X-Goog-Api-Key", key)        # nunca se imprime
    req.add_header("X-Goog-FieldMask", FIELD_MASK)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def run_queries(key: str, max_queries: int, max_results: int):
    RAW_OUT.mkdir(parents=True, exist_ok=True)
    queries = ([("validacion", cid, q, zona) for cid, q, zona in VALIDATION_TARGETS]
               + [("descubrimiento", "", q, "") for q in DISCOVERY_QUERIES])
    queries = queries[:max_queries]

    matches, staging, omitidos_seen, omitidos = [], [], set(), []
    n_exec, n_err, n_results = 0, 0, 0

    for kind, cid, q, zona in queries:
        try:
            data = search_text(q, key, max_results)
            n_exec += 1
        except urllib.error.HTTPError as e:
            n_err += 1
            try:
                msg = json.loads(e.read().decode("utf-8")).get("error", {}).get("message", "")
            except Exception:
                msg = ""
            print(f"  [error] HTTP {e.code} en query '{q}': {msg[:160]}")
            continue
        except Exception as e:  # noqa
            n_err += 1
            print(f"  [error] {type(e).__name__} en query '{q}'")
            continue

        # crudo gitignored
        safe = norm(q).replace(" ", "_")[:50]
        (RAW_OUT / f"{kind}_{safe}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2),
                                                     encoding="utf-8")
        places = data.get("places", []) or []
        n_results += len(places)

        if kind == "validacion":
            top = places[0] if places else None
            if top:
                name = top.get("displayName", {}).get("text", "")
                types = top.get("types", [])
                bs = top.get("businessStatus", "")
                web = bool(top.get("websiteUri"))
                hrs = bool(top.get("regularOpeningHours", {}).get("weekdayDescriptions"))
                sim = matches_active(name)
                staging.append([top.get("id", ""), name, top.get("formattedAddress", ""),
                                (top.get("location") or {}).get("latitude", ""),
                                (top.get("location") or {}).get("longitude", ""),
                                bs, "|".join(types), top.get("rating", ""),
                                top.get("userRatingCount", ""), top.get("websiteUri", ""),
                                top.get("googleMapsUri", ""), q, "si" if sim else "revisar", cid])
                matches.append([cid, q.replace(" CABA", ""), zona, bs or "sin_estado",
                                tipos_resumidos(types), "si" if web else "no",
                                "si" if hrs else "no", "si" if sim else "revisar",
                                "alto" if sim and bs == "OPERATIONAL" else "medio",
                                "confirmar_ficha" if sim else "revisar_match",
                                "validado por Google" if sim else "match dudoso por nombre"])
            else:
                matches.append([cid, q.replace(" CABA", ""), zona, "sin_resultado",
                                "sin_tipos", "no", "no", "no", "bajo",
                                "revisar_manual", "Google no devolvio resultado"])
        else:
            for p in places:
                name = p.get("displayName", {}).get("text", "")
                if not name or matches_active(name):
                    continue  # es uno de los 15 activos: no es omitido
                key_n = norm(name)
                if key_n in omitidos_seen:
                    continue
                omitidos_seen.add(key_n)
                types = p.get("types", [])
                loc = p.get("location")
                clasif = classify_omitido(name, types, loc)
                bs = p.get("businessStatus", "")
                web = bool(p.get("websiteUri"))
                staging.append([p.get("id", ""), name, p.get("formattedAddress", ""),
                                (loc or {}).get("latitude", ""), (loc or {}).get("longitude", ""),
                                bs, "|".join(types), p.get("rating", ""),
                                p.get("userRatingCount", ""), p.get("websiteUri", ""),
                                p.get("googleMapsUri", ""), q, "omitido", ""])
                conf = "medio" if clasif in {"posible_mercado_gastronomico",
                                             "posible_food_hall",
                                             "posible_feria_gastronomica"} else "bajo"
                accion = ("posible_omitido_pendiente_revision"
                          if conf == "medio" else "descartar_o_revisar")
                omitidos.append([name, "CABA", bs or "sin_estado", tipos_resumidos(types),
                                 "si" if web else "no", clasif, conf, accion,
                                 "detectado por descubrimiento Google; NO se suma al conteo"])
        time.sleep(0.2)  # cortesia

    # staging interno (gitignored) con place_id/direccion
    INTERNAL.mkdir(parents=True, exist_ok=True)
    with (INTERNAL / "google_places_staging_v2.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["place_id", "nombre_google", "direccion_google", "lat", "lon",
                    "business_status", "tipos_google", "rating", "user_rating_count",
                    "website", "google_maps_uri", "query_origen", "match_con_v1_2",
                    "id_candidato_v1_2_si_match"])
        w.writerows(staging)

    return matches, omitidos, n_exec, n_err, n_results


def write_sanitized(mode, key_present, matches, omitidos, n_exec, n_err, n_results):
    SAN_OUT.mkdir(parents=True, exist_ok=True)
    estado = "ejecutado" if (mode == "run" and key_present and n_exec) else "pendiente_dry_run"

    with (SAN_OUT / "google_places_matches_v1_2.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["id_candidato_v1_2", "nombre", "barrio_o_zona", "estado_google",
                    "tipos_google_resumidos", "tiene_web", "tiene_horarios_google",
                    "match_con_v1_2", "nivel_confianza_google", "accion_recomendada",
                    "observacion"])
        if matches:
            w.writerows(matches)
        else:
            for cid, q, zona in VALIDATION_TARGETS:
                w.writerow([cid, q.replace(" CABA", ""), zona, "pendiente_dry_run", "pendiente",
                            "pendiente", "pendiente", "por_validar", "pendiente",
                            "ejecutar_con_key", "sin ejecucion"])

    with (SAN_OUT / "google_places_posibles_omitidos_v2.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["nombre", "barrio_o_zona", "estado_google", "tipos_google_resumidos",
                    "tiene_web", "clasificacion_omitido", "nivel_confianza_google",
                    "accion_recomendada", "observacion"])
        w.writerows(omitidos)

    plan = len(VALIDATION_TARGETS) + len(DISCOVERY_QUERIES)
    costo_exec = round(n_exec * USD_POR_REQUEST_REF, 3)
    posibles = sum(1 for o in omitidos if o[6] == "medio")
    with (SAN_OUT / "google_places_mercados_resumen_v2.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["metrica", "valor", "detalle"])
        w.writerow(["modo", mode, "dry-run no hace requests"])
        w.writerow(["key_presente", "si" if key_present else "no", "leida de entorno/.env (no se imprime)"])
        w.writerow(["queries_validacion", len(VALIDATION_TARGETS), "uno por mercado activo V1.2"])
        w.writerow(["queries_descubrimiento", len(DISCOVERY_QUERIES), "busqueda de posibles omitidos"])
        w.writerow(["queries_totales_planeadas", plan, "validacion + descubrimiento"])
        w.writerow(["queries_ejecutadas", n_exec, "reales contra Google Places"])
        w.writerow(["errores_api", n_err, "queries con error HTTP/red"])
        w.writerow(["resultados_obtenidos", n_results, "lugares devueltos (todas las queries)"])
        w.writerow(["matches_con_15_activos", sum(1 for m in matches if m[7] == "si"),
                    "validaciones con coincidencia de nombre"])
        w.writerow(["posibles_omitidos_pendiente_revision", posibles,
                    "candidatos gastronomicos nuevos (NO se suman al conteo)"])
        w.writerow(["costo_estimado_ejecutado_usd", costo_exec,
                    f"~{USD_POR_REQUEST_REF}/req; orden de magnitud, CONFIRMAR pricing"])
        w.writerow(["estado", estado, "pendiente_por_key" if not key_present else estado])


def main() -> int:
    ap = argparse.ArgumentParser(description="Google Places enrichment (modo seguro) — mercados CABA")
    ap.add_argument("--mode", choices=["dry-run", "run"], default="dry-run")
    ap.add_argument("--max-queries", type=int, default=25)
    ap.add_argument("--max-results-per-query", type=int, default=10)
    args = ap.parse_args()

    key = get_api_key()
    key_present = key is not None
    plan = len(VALIDATION_TARGETS) + len(DISCOVERY_QUERIES)
    a_ejecutar = min(plan, args.max_queries)

    print("=" * 72)
    print("Google Places — enriquecimiento mercados gastronomicos CABA (MODO SEGURO)")
    print(f"  modo: {args.mode}  |  key presente: {'SI' if key_present else 'NO'}")
    print(f"  queries planeadas: {plan} (15 validacion + 12 descubrimiento)")
    print(f"  tope --max-queries: {args.max_queries} -> se ejecutarian {a_ejecutar}")
    print(f"  tope --max-results-per-query: {args.max_results_per_query}")
    print(f"  costo estimado si run: ~USD {round(a_ejecutar * USD_POR_REQUEST_REF, 3)}"
          f" (orden de magnitud, a confirmar contra pricing vigente)")

    matches, omitidos, n_exec, n_err, n_results = [], [], 0, 0, 0
    if args.mode == "run" and key_present:
        print("  [run] ejecutando requests reales (con topes)...")
        matches, omitidos, n_exec, n_err, n_results = run_queries(
            key, args.max_queries, args.max_results_per_query)
        print(f"  ejecutadas={n_exec} errores={n_err} resultados={n_results}"
              f" matches={sum(1 for m in matches if m[7]=='si')} omitidos_posibles={sum(1 for o in omitidos if o[6]=='medio')}")
    elif args.mode == "run" and not key_present:
        print("  [run] sin API key -> NO se ejecuta. Etapa queda PENDIENTE.")
    else:
        print("  [dry-run] no se realizan requests.")

    key = None  # descartar referencia
    write_sanitized(args.mode, key_present, matches, omitidos, n_exec, n_err, n_results)
    print("  outputs sanitizados actualizados (sin place_id ni datos sensibles).")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
