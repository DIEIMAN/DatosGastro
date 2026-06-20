"""Piloto controlado de Google Places API (New) para validar casas/fábricas de pastas en CABA.

OBJETIVO
--------
Prueba MUY chica (5-10 queries, <=50 resultados) para contrastar el universo de
casas/fábricas de pastas contra una fuente externa (Google Places API oficial).
NO reemplaza el informe actual. NO toca el pipeline principal ni data/processed.
Los resultados de Google NO son "oficiales" y NO se mezclan con AGC ni OSM sin aclarar fuente.

SEGURIDAD (guardrails)
----------------------
- La API key se lee SOLO desde la variable de entorno GOOGLE_MAPS_API_KEY.
- Nunca se imprime, loguea, guarda ni commitea la API key.
- --dry-run es el modo por defecto: NO hace requests reales sin --run.
- Límites: --max-queries, --max-results, --pause entre requests.
- Salida a carpeta separada y gitignored: outputs/casas_pastas_google_places/
- Solo Places API oficial. Nada de scraping.

USO
---
  # Simulación (no gasta, no llama a la API):
  python scripts/casas_pastas/google_places_piloto.py

  # Ejecución real (requiere GOOGLE_MAPS_API_KEY en el entorno):
  python scripts/casas_pastas/google_places_piloto.py --run --max-queries 5 --max-results 50
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs" / "casas_pastas_google_places"
RAW = OUT / "google_places_raw_minimo.json"
CAND = OUT / "google_places_candidatos.csv"
RESUMEN = OUT / "google_places_resumen.csv"
LOG = OUT / "piloto_log.txt"

ENDPOINT = "https://places.googleapis.com/v1/places:searchText"

# Campos MÍNIMOS de primera pasada (no pedir rating, reviews, teléfono, web, horarios todavía).
FIELDS = [
    "places.id",
    "places.displayName",
    "places.formattedAddress",
    "places.location",
    "places.businessStatus",
    "places.types",
]

# Queries semilla del piloto (city-level, sin grilla por comuna todavía).
SEED_QUERIES = [
    "casa de pastas CABA",
    "pastas frescas CABA",
    "fábrica de pastas CABA",
    "pastificio Buenos Aires",
    "ravioles CABA",
]

# --- Clasificación ligera (determinística, conservadora) ---
# Términos fuertes: indican casa/fábrica de pastas con alta probabilidad.
TERMINOS_FUERTES = [
    "pastas", "pasta fresca", "pastas frescas", "pastificio", "fabrica de pasta",
    "fábrica de pasta", "casa de pasta", "ravioles", "ravioli", "sorrentinos",
    "ñoquis", "noquis", "gnocchi", "canelones", "tallarines", "fideos caseros",
]
# Términos débiles/ambiguos: pueden ser restaurante italiano, no casa de pastas.
TERMINOS_DEBILES = ["pasta", "italian", "italiana", "trattoria", "cocina italiana"]
# Señales de NO casa de pastas (gastronómico general).
TERMINOS_DESCARTE = ["pizzeria", "pizzería", "pizza", "bar ", "café", "cafe ", "heladería", "heladeria"]


def log(msg: str, *, to_file: bool = True) -> None:
    """Imprime y opcionalmente persiste en log. NUNCA recibe la API key."""
    line = f"[{dt.datetime.now().isoformat(timespec='seconds')}] {msg}"
    print(line)
    if to_file:
        OUT.mkdir(parents=True, exist_ok=True)
        with LOG.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")


def clasificar(nombre: str, types: list[str]) -> tuple[str, str, str, bool]:
    """Devuelve (match, confianza, motivo, requiere_revision_manual)."""
    n = (nombre or "").lower()
    t = " ".join(types or []).lower()

    tiene_fuerte = any(k in n for k in TERMINOS_FUERTES)
    tiene_debil = any(k in n for k in TERMINOS_DEBILES)
    tiene_descarte = any(k in n for k in TERMINOS_DESCARTE)

    if tiene_fuerte and not tiene_descarte:
        return ("A_google_probable_casa_pastas", "alta",
                "nombre con término fuerte de pastas", False)
    if tiene_fuerte and tiene_descarte:
        return ("B_google_dudoso", "media",
                "término de pastas + señal de gastronómico general", True)
    if tiene_debil:
        return ("B_google_dudoso", "media",
                "término ambiguo (posible restaurante italiano)", True)
    return ("C_google_descartado", "baja",
            "sin término de pastas en el nombre", False)


def cargar_queries(max_queries: int) -> list[str]:
    qs = list(SEED_QUERIES)[:max_queries]
    return qs


def estimar_costo(n_queries: int) -> str:
    """Estimación de orden de magnitud. NO es precio oficial; confirmar con Google."""
    return (
        f"~{n_queries} requests de Text Search (New), tier 'Pro' por los campos pedidos "
        f"(formattedAddress/location/types). El costo por 1000 requests lo fija Google y "
        f"suele estar en el rango de decenas de USD/1000; con {n_queries} requests el gasto "
        f"esperado es de centavos. CONFIRMAR contra el pricing vigente y el crédito gratuito "
        f"de tu cuenta antes de ampliar."
    )


def mostrar_plan(queries: list[str], max_results: int, pause: float, modo: str) -> None:
    print("=" * 72)
    print(f"  PILOTO GOOGLE PLACES — MODO: {modo}")
    print("=" * 72)
    print(f"  Endpoint            : {ENDPOINT}")
    print(f"  Cantidad de queries : {len(queries)}")
    for i, q in enumerate(queries, 1):
        print(f"      {i}. {q}")
    print(f"  Máx. resultados     : {max_results}")
    print(f"  Campos solicitados  : {', '.join(f.replace('places.', '') for f in FIELDS)}")
    print(f"  Pausa entre requests: {pause:.1f} s")
    print(f"  Carpeta de salida   : {OUT.relative_to(ROOT)}  (gitignored)")
    print(f"  Advertencia costo   : {estimar_costo(len(queries))}")
    print(f"  API key             : se lee de $GOOGLE_MAPS_API_KEY · NO se imprime ni se guarda")
    print("=" * 72)


def validar_api_key() -> str | None:
    key = os.environ.get("GOOGLE_MAPS_API_KEY", "").strip()
    if not key:
        return None
    return key


def hacer_request(key: str, query: str, page_size: int):
    """Una llamada a Text Search (New). Devuelve (places, error)."""
    import requests  # import diferido: el dry-run no necesita la librería

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": key,  # solo en el header, jamás en logs/archivos
        "X-Goog-FieldMask": ",".join(FIELDS),
    }
    body = {
        "textQuery": query,
        "languageCode": "es",
        "regionCode": "AR",
        "pageSize": page_size,
    }
    try:
        resp = requests.post(ENDPOINT, headers=headers, json=body, timeout=30)
    except Exception as exc:  # noqa: BLE001
        return [], f"excepción de red: {type(exc).__name__}"
    if resp.status_code != 200:
        # No volcamos el body crudo por si trae el echo de la request; solo el status y message.
        try:
            msg = resp.json().get("error", {}).get("message", "")
        except Exception:  # noqa: BLE001
            msg = ""
        return [], f"HTTP {resp.status_code}: {msg[:200]}"
    return resp.json().get("places", []), None


def normalizar(place: dict, query: str) -> dict:
    nombre = (place.get("displayName") or {}).get("text", "")
    loc = place.get("location") or {}
    types = place.get("types") or []
    match, conf, motivo, rev = clasificar(nombre, types)
    return {
        "place_id": place.get("id", ""),
        "nombre": nombre,
        "direccion": place.get("formattedAddress", ""),
        "lat": loc.get("latitude", ""),
        "lon": loc.get("longitude", ""),
        "business_status": place.get("businessStatus", ""),
        "types": ";".join(types),
        "query_origen": query,
        "match_casas_pastas": match,
        "confianza": conf,
        "motivo": motivo,
        "requiere_revision_manual": "si" if rev else "no",
    }


def escribir_salidas(filas: list[dict], raw: list[dict], queries: list[str],
                     requests_hechas: int, errores: list[str]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    # raw mínimo (sin API key; solo los campos pedidos que ya vienen en la respuesta)
    RAW.write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8")

    cols = ["place_id", "nombre", "direccion", "lat", "lon", "business_status", "types",
            "query_origen", "match_casas_pastas", "confianza", "motivo",
            "requiere_revision_manual"]
    with CAND.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(filas)

    a = sum(1 for f in filas if f["match_casas_pastas"].startswith("A_"))
    b = sum(1 for f in filas if f["match_casas_pastas"].startswith("B_"))
    c = sum(1 for f in filas if f["match_casas_pastas"].startswith("C_"))
    with RESUMEN.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["indicador", "valor"])
        w.writerow(["fecha", dt.date.today().isoformat()])
        w.writerow(["fuente", "Google Places API (New) - Text Search - PILOTO no oficial"])
        w.writerow(["queries_ejecutadas", requests_hechas])
        w.writerow(["queries_planificadas", len(queries)])
        w.writerow(["resultados_totales", len(filas)])
        w.writerow(["A_google_probable_casa_pastas", a])
        w.writerow(["B_google_dudoso", b])
        w.writerow(["C_google_descartado", c])
        w.writerow(["errores", len(errores)])


def main() -> int:
    ap = argparse.ArgumentParser(description="Piloto controlado Google Places (casas/fábricas de pastas).")
    ap.add_argument("--run", action="store_true", help="Ejecuta requests reales. Sin esto: dry-run.")
    ap.add_argument("--max-queries", type=int, default=5, help="Máx. de queries (default 5).")
    ap.add_argument("--max-results", type=int, default=50, help="Máx. de resultados totales (default 50).")
    ap.add_argument("--page-size", type=int, default=20, help="Resultados por request (1-20, default 20).")
    ap.add_argument("--pause", type=float, default=1.5, help="Pausa en seg entre requests (default 1.5).")
    args = ap.parse_args()

    # Tope duro de seguridad: este piloto no consulta la grilla completa.
    if args.max_queries > 10:
        log(f"ABORTADO: --max-queries={args.max_queries} supera el tope del piloto (10).")
        return 2
    if args.max_results > 50:
        log(f"ABORTADO: --max-results={args.max_results} supera el tope del piloto (50).")
        return 2
    page_size = max(1, min(20, args.page_size))

    queries = cargar_queries(args.max_queries)
    modo = "EJECUCIÓN REAL (--run)" if args.run else "DRY-RUN (simulación, sin requests)"
    mostrar_plan(queries, args.max_results, args.pause, modo)

    if not args.run:
        print("\nDRY-RUN: no se hicieron requests ni se gastó cuota.")
        print("Para ejecutar de verdad: agregá --run (requiere GOOGLE_MAPS_API_KEY).")
        return 0

    # --- A partir de acá, ejecución real ---
    key = validar_api_key()
    if key is None:
        log("ABORTADO: falta GOOGLE_MAPS_API_KEY en el entorno. No se ejecuta nada.")
        print("\nSeteá la variable y reintentá. Ejemplo (PowerShell, solo en tu sesión):")
        print('  $env:GOOGLE_MAPS_API_KEY = "<tu_api_key>"')
        return 2
    log(f"GOOGLE_MAPS_API_KEY detectada (no se imprime; longitud={len(key)}).")

    OUT.mkdir(parents=True, exist_ok=True)
    log(f"Inicio piloto · queries={len(queries)} · max_results={args.max_results} · page_size={page_size}")

    raw_all: list[dict] = []
    filas: list[dict] = []
    vistos: set[str] = set()
    errores: list[str] = []
    requests_hechas = 0

    for i, q in enumerate(queries, 1):
        if len(filas) >= args.max_results:
            log(f"Tope de resultados alcanzado ({args.max_results}). Se detienen más queries.")
            break
        log(f"Request {i}/{len(queries)}: query='{q}'")
        places, err = hacer_request(key, q, page_size)
        requests_hechas += 1
        if err:
            errores.append(f"{q} -> {err}")
            log(f"  error: {err}")
        else:
            log(f"  resultados: {len(places)}")
            for p in places:
                if len(filas) >= args.max_results:
                    break
                pid = p.get("id", "")
                if pid and pid in vistos:
                    continue
                vistos.add(pid)
                raw_all.append(p)
                filas.append(normalizar(p, q))
        if i < len(queries):
            time.sleep(args.pause)

    escribir_salidas(filas, raw_all, queries, requests_hechas, errores)

    a = sum(1 for f in filas if f["match_casas_pastas"].startswith("A_"))
    b = sum(1 for f in filas if f["match_casas_pastas"].startswith("B_"))
    c = sum(1 for f in filas if f["match_casas_pastas"].startswith("C_"))
    log("=" * 60)
    log(f"FIN · requests={requests_hechas} · resultados={len(filas)} · "
        f"A={a} B={b} C={c} · errores={len(errores)}")
    log(f"Archivos: {RAW.name}, {CAND.name}, {RESUMEN.name}, {LOG.name}")
    if errores:
        log("Detalle de errores:")
        for e in errores:
            log(f"  - {e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
