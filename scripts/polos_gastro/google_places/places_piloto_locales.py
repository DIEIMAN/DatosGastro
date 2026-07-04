# -*- coding: utf-8 -*-
"""
Piloto Google Places — locales destacados del núcleo principal (PolosGastro).

EXPERIMENTO AISLADO. No forma parte del pipeline DataGastro.

Modos:
- dry_run (por defecto): NO llama a la API. Escribe solo las QUERIES PROPUESTAS.
- --execute: ejecución real controlada. Requiere API key por variable de entorno
  (GOOGLE_MAPS_API_KEY, o en su defecto GOOGLE_PLACES_API_KEY). Si hay un .env en la raíz del
  repo, se carga con un parser simple seguro (python-dotenv es opcional).

Seguridad (ver docs/polos_gastro/google_places/):
- La API key SOLO se lee de entorno/.env. NUNCA se imprime, guarda ni loguea (ni enmascarada).
- Hard cap absoluto de 10 locales (MAX_LOCALES_HARD_CAP). --max-locales no puede superarlo.
- Solo núcleo principal (Palermo, Puerto Madero, San Telmo, Recoleta).
- FieldMask mínimo. NO se guardan responses crudas completas.
- NO se guardan lat/lng (para no usarlos en mapas del informe).
- Se guarda: place_id/id, nombre, dirección, tipos, business_status, fecha de consulta.
- Costos: Places API es PAGA. No ejecutar masivamente.
- Términos: revisar Google Maps Platform ToS antes de cachear/mezclar con otros mapas.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SEED = ROOT / "outputs" / "polos_gastro" / "locales_destacados_por_polo_seed.csv"
OUT_DIR = ROOT / "outputs" / "polos_gastro" / "experimentos_google_places"
OUT_QUERIES = OUT_DIR / "locales_places_piloto_queries.csv"
OUT_RESULTS = OUT_DIR / "locales_places_piloto_resultados.csv"
# CSV histórico de dry_run de la fase anterior (se mantiene por compatibilidad).
OUT_LEGACY = OUT_DIR / "locales_places_piloto.csv"

NUCLEO_NOMBRES = {
    "Palermo (Soho, Hollywood y Las Cañitas)",
    "Puerto Madero",
    "San Telmo",
    "Recoleta",
}

MAX_LOCALES_HARD_CAP = 10  # tope absoluto; no superar sin cambio de código en otra fase.

# Endpoint Places API (New) Text Search.
PLACES_URL = "https://places.googleapis.com/v1/places:searchText"
# FieldMask mínimo: NO incluye location (lat/lng) a propósito.
FIELD_MASK = "places.id,places.displayName,places.formattedAddress,places.types,places.businessStatus"

COLUMNS = [
    "local_id", "nombre_local", "nombre_polo", "query_busqueda",
    "place_id", "nombre_google", "direccion_google", "tipos_google",
    "business_status", "match_confidence", "requiere_revision_manual",
    "fecha_consulta", "fuente", "observaciones",
]


def load_env_file(path: Path) -> dict:
    """Parser simple y seguro de .env. No imprime valores."""
    vals = {}
    if not path.exists():
        return vals
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        vals[k.strip()] = v.strip().strip('"').strip("'")
    return vals


def detect_api_key() -> tuple[str | None, str]:
    """Devuelve (key, fuente_descriptiva). NUNCA imprime la key."""
    # Prioridad: entorno; luego .env (sin dotenv si no está).
    env_file = {}
    try:
        import dotenv  # type: ignore
        dotenv.load_dotenv(ROOT / ".env")  # carga a os.environ si está disponible
    except Exception:
        env_file = load_env_file(ROOT / ".env")

    for name in ("GOOGLE_MAPS_API_KEY", "GOOGLE_PLACES_API_KEY"):
        v = os.environ.get(name) or env_file.get(name)
        if v:
            return v, f"{name} (presente)"
    return None, "ausente"


def read_seed() -> list[dict]:
    with SEED.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def select_nucleo(rows: list[dict], limit: int) -> list[dict]:
    seleccion = [r for r in rows if r.get("nombre_polo", "").strip() in NUCLEO_NOMBRES]
    return seleccion[:limit]


def build_query(row: dict) -> str:
    return f"{row.get('nombre_local','').strip()}, {row.get('nombre_polo','').strip()}, CABA, Argentina"


def write_csv(path: Path, rows: list[dict]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)


def base_row(r: dict) -> dict:
    return {
        "local_id": r.get("local_id", ""),
        "nombre_local": r.get("nombre_local", ""),
        "nombre_polo": r.get("nombre_polo", ""),
        "query_busqueda": build_query(r),
        "place_id": "", "nombre_google": "", "direccion_google": "",
        "tipos_google": "", "business_status": "", "match_confidence": "",
        "requiere_revision_manual": "si", "fecha_consulta": "",
        "fuente": "Google Places API (experimental)", "observaciones": "",
    }


def simple_confidence(seed_name: str, google_name: str) -> str:
    if not google_name:
        return ""
    a = seed_name.lower().strip()
    b = google_name.lower().strip()
    if a == b:
        return "alta"
    if a in b or b in a:
        return "media"
    return "baja"


def call_places(query: str, api_key: str):
    """Llama Places API (New) Text Search. Devuelve (dict_min, error_str). NO imprime la key."""
    import requests  # import local para que dry_run no dependa de requests
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,          # la key viaja en header, no se loguea
        "X-Goog-FieldMask": FIELD_MASK,
    }
    payload = {"textQuery": query, "maxResultCount": 1, "languageCode": "es", "regionCode": "AR"}
    try:
        resp = requests.post(PLACES_URL, headers=headers, data=json.dumps(payload), timeout=20)
    except Exception as exc:  # error de red: no exponer secretos
        return None, f"network_error: {type(exc).__name__}"
    if resp.status_code != 200:
        # No incluir headers (que contienen la key) en el mensaje.
        return None, f"http_{resp.status_code}"
    try:
        data = resp.json()
    except Exception:
        return None, "invalid_json"
    places = data.get("places") or []
    if not places:
        return {}, "no_match"
    p = places[0]
    # Solo campos permitidos; NO se guarda la response cruda completa, ni lat/lng.
    return {
        "place_id": p.get("id", ""),
        "nombre_google": (p.get("displayName") or {}).get("text", ""),
        "direccion_google": p.get("formattedAddress", ""),
        "tipos_google": "|".join(p.get("types", []) or []),
        "business_status": p.get("businessStatus", ""),
    }, ""


def main() -> int:
    parser = argparse.ArgumentParser(description="Piloto Google Places (dry_run por defecto).")
    parser.add_argument("--execute", action="store_true",
                        help="Ejecución real (requiere API key por entorno/.env). Default: dry_run.")
    parser.add_argument("--max-locales", type=int, default=MAX_LOCALES_HARD_CAP,
                        help=f"Máximo de locales (cap absoluto {MAX_LOCALES_HARD_CAP}).")
    args = parser.parse_args()

    limit = max(0, min(args.max_locales, MAX_LOCALES_HARD_CAP))
    if args.max_locales > MAX_LOCALES_HARD_CAP:
        print(f"[aviso] --max-locales {args.max_locales} excede el cap; se usa {MAX_LOCALES_HARD_CAP}.",
              file=sys.stderr)

    seed = read_seed()
    seleccion = select_nucleo(seed, limit)
    if not seleccion:
        print("No se encontraron locales del núcleo principal en el seed.", file=sys.stderr)
        return 1

    # Queries siempre se escriben (auditables, sin datos de Google).
    q_rows = []
    for r in seleccion:
        row = base_row(r)
        row["observaciones"] = "query propuesta"
        q_rows.append(row)
    write_csv(OUT_QUERIES, q_rows)

    if not args.execute:
        # dry_run: también refresca el CSV legacy por compatibilidad.
        for row in q_rows:
            row["fuente"] = "Google Places API (experimental) - dry_run"
            row["observaciones"] = "dry_run: sin llamada real a la API; solo query propuesta."
        write_csv(OUT_LEGACY, q_rows)
        print(f"[dry_run] {len(q_rows)} queries propuestas escritas en:")
        print(f"  {OUT_QUERIES}")
        print("[dry_run] No se realizó ninguna llamada a Google Places API.")
        return 0

    # --- Ejecución real ---
    api_key, key_status = detect_api_key()
    print(f"[execute] API key: {key_status}")  # solo estado, nunca el valor
    if not api_key:
        print("ERROR: --execute requiere API key (GOOGLE_MAPS_API_KEY o GOOGLE_PLACES_API_KEY) "
              "por entorno o .env. No se realizó ninguna llamada.", file=sys.stderr)
        return 2

    try:
        import requests  # noqa: F401
    except Exception:
        print("ERROR: falta 'requests' para ejecución real. No se realizó ninguna llamada.",
              file=sys.stderr)
        return 4

    today = date.today().isoformat()
    results, n_req, n_match, n_err = [], 0, 0, 0
    for r in seleccion:
        row = base_row(r)
        query = row["query_busqueda"]
        n_req += 1
        data, err = call_places(query, api_key)
        row["fecha_consulta"] = today
        if err and data is None:
            n_err += 1
            row["observaciones"] = f"error: {err}"
        elif err == "no_match":
            row["observaciones"] = "sin coincidencia"
        else:
            row.update(data)
            row["match_confidence"] = simple_confidence(row["nombre_local"], row["nombre_google"])
            row["observaciones"] = "match experimental; requiere revision manual."
            if row["place_id"]:
                n_match += 1
        row["requiere_revision_manual"] = "si"
        results.append(row)

    write_csv(OUT_RESULTS, results)
    print(f"[execute] requests intentados: {n_req} | matches: {n_match} | errores: {n_err}")
    print(f"[execute] resultados en: {OUT_RESULTS}")
    print("[execute] No se guardaron responses crudas ni coordenadas. Uso experimental.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
