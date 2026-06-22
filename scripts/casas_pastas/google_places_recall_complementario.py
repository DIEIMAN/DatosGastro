"""Búsqueda COMPLEMENTARIA de recall en Google Places para detectar posibles casas de pastas
no capturadas, SIN incorporarlas automáticamente al padrón.

Por defecto NO ejecuta requests: imprime el plan y sale. Solo con --run consulta la API
(requiere GOOGLE_MAPS_API_KEY en el entorno). Reutiliza el clasificador compartido.

Resultados (carpeta gitignored):
  outputs/casas_pastas_recall/google_api_complementaria/bruto/<tag>.json
  outputs/casas_pastas_recall/google_api_complementaria/candidatos_extra_a_validar.csv
  outputs/casas_pastas_recall/google_api_complementaria/resumen_recall_google.csv

Los resultados se MATCHEAN contra el padrón depurado actual y se separan en presentes vs
posibles nuevos; restaurantes/trattorias/bodegones/bares de pasta/fast food/confiterías y
cierres se marcan como excluidos. NO se modifica el padrón principal.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import sys
import time
import unicodedata
import re
from difflib import SequenceMatcher
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from google_places_clasificador import clasificar, norm_nombre  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
INT = ROOT / "outputs" / "casas_pastas_integrado"
OUT = ROOT / "outputs" / "casas_pastas_recall" / "google_api_complementaria"
BRUTO = OUT / "bruto"
PADRON = INT / "padron_candidato_integrado_v3_depurado.csv"
ENDPOINT = "https://places.googleapis.com/v1/places:searchText"
FIELDS = ["places.id", "places.displayName", "places.formattedAddress", "places.location",
          "places.businessStatus", "places.types"]

# Barrios prioritarios para ampliar recall (subconjunto; ajustable).
BARRIOS = ["Boedo", "Almagro", "Caballito", "Flores", "Villa Urquiza", "Villa Devoto",
           "Belgrano", "Palermo", "Mataderos", "Liniers", "Villa Crespo", "Parque Patricios"]
PLANTILLAS_BARRIO = [
    "casa de pastas {b} CABA", "pastas frescas {b} CABA", "fábrica de pastas {b} CABA",
    "fabrica de pastas {b} CABA", "pastificio {b} CABA", "ravioles {b} CABA",
    "sorrentinos {b} CABA", "ñoquis {b} CABA", "tallarines frescos {b} CABA",
    "pastas artesanales {b} CABA",
]
QUERIES_GENERALES = [
    "casa de pastas CABA", "pastas frescas CABA", "fábrica de pastas CABA",
    "pastificio Buenos Aires", "pastas artesanales Buenos Aires",
]
EXCL_TIPOS = {"restaurant", "italian_restaurant", "pizza_restaurant", "bar", "meal_delivery",
              "cafe", "coffee_shop", "fast_food_restaurant", "bakery", "fine_dining_restaurant"}


def na(s):
    s = unicodedata.normalize("NFKD", (s or "").lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", s)).strip()


def construir_queries():
    qs = list(QUERIES_GENERALES)
    for b in BARRIOS:
        for t in PLANTILLAS_BARRIO:
            qs.append(t.format(b=b))
    # dedup preservando orden
    seen, out = set(), []
    for q in qs:
        if q.lower() not in seen:
            seen.add(q.lower()); out.append(q)
    return out


def cargar_padron_nombres():
    if not PADRON.exists():
        return set()
    return {na(r["nombre"]) for r in csv.DictReader(PADRON.open(encoding="utf-8-sig"))}


def clasificar_estado(nombre, types, padron):
    """Devuelve (estado, accion) comparando contra el padrón depurado.
    Estados: presente_en_padron | duplicado_probable | excluido_por_rubro | posible_nuevo_a_validar.
    """
    n = na(nombre)
    match, _, _, _ = clasificar(nombre, ";".join(types))
    if n and n in padron:
        return "presente_en_padron", "ya en padrón"
    # near-duplicate: nombre muy similar a uno del padrón pero no idéntico
    mejor = max((SequenceMatcher(None, n, pn).ratio() for pn in padron), default=0.0) if n else 0.0
    if mejor >= 0.85:
        return "duplicado_probable", "revisar posible duplicado del padrón"
    if match.startswith("C_") or (set(types) & EXCL_TIPOS):
        return "excluido_por_rubro", "descartar (restaurante/bar/confitería/cierre)"
    return "posible_nuevo_a_validar", "validar manualmente"


def plan(queries):
    disponibles = len(QUERIES_GENERALES) + len(BARRIOS) * len(PLANTILLAS_BARRIO)
    print("=" * 72)
    print("  RECALL COMPLEMENTARIO GOOGLE PLACES — MODO DRY-RUN (sin requests)")
    print("=" * 72)
    print(f"  Endpoint       : {ENDPOINT}")
    print(f"  Queries a ejecutar: {len(queries)} (tope --max-queries) de {disponibles} "
          f"disponibles ({len(QUERIES_GENERALES)} generales + {len(BARRIOS)}x{len(PLANTILLAS_BARRIO)} por barrio)")
    print(f"  Campos pedidos : {', '.join(f.replace('places.','') for f in FIELDS)}")
    print(f"  Padrón base    : {PADRON.name} (matcheo por nombre normalizado)")
    print(f"  Brutos (gitignored): {BRUTO.relative_to(ROOT)}")
    print(f"  Variable de entorno requerida (solo en --run): GOOGLE_MAPS_API_KEY")
    print("  Ejemplos de query:")
    for q in queries[:6]:
        print(f"      - {q}")
    print("  Cada resultado se clasifica contra el padrón en: presente_en_padron · "
          "duplicado_probable · posible_nuevo_a_validar · excluido_por_rubro.")
    print("  Para EJECUTAR de verdad: --run (requiere GOOGLE_MAPS_API_KEY). NO incorpora nada al padrón.")
    print("=" * 72)


def main() -> int:
    ap = argparse.ArgumentParser(description="Recall complementario Google Places (dry-run por defecto).")
    ap.add_argument("--run", action="store_true", help="Ejecuta requests reales (requiere GOOGLE_MAPS_API_KEY).")
    ap.add_argument("--dry-run", action="store_true", help="Solo muestra el plan; no llama a la API (default).")
    ap.add_argument("--max-queries", type=int, default=40)
    ap.add_argument("--max-results", type=int, default=400)
    ap.add_argument("--pause", type=float, default=1.5)
    args = ap.parse_args()

    queries = construir_queries()[:args.max_queries]
    # Modo seguro: solo --run dispara requests. Cualquier otro caso (incluido --dry-run o sin
    # flags) imprime el plan y termina sin tocar la API.
    if not args.run:
        plan(queries)
        return 0

    key = os.environ.get("GOOGLE_MAPS_API_KEY", "").strip()
    if not key:
        print("ABORTADO: falta GOOGLE_MAPS_API_KEY. No se ejecuta.")
        return 2
    import requests  # diferido
    BRUTO.mkdir(parents=True, exist_ok=True)
    padron = cargar_padron_nombres()
    vistos, filas = set(), []
    for i, q in enumerate(queries, 1):
        if len(filas) >= args.max_results:
            break
        headers = {"Content-Type": "application/json", "X-Goog-Api-Key": key,
                   "X-Goog-FieldMask": ",".join(FIELDS)}
        body = {"textQuery": q, "languageCode": "es", "regionCode": "AR", "pageSize": 20}
        try:
            resp = requests.post(ENDPOINT, headers=headers, json=body, timeout=30)
            places = resp.json().get("places", []) if resp.status_code == 200 else []
        except Exception as exc:  # noqa: BLE001
            print(f"  error en '{q}': {type(exc).__name__}"); places = []
        (BRUTO / f"q{i:03d}.json").write_text(json.dumps(places, ensure_ascii=False), encoding="utf-8")
        for p in places:
            pid = p.get("id", "")
            if pid in vistos:
                continue
            vistos.add(pid)
            nombre = (p.get("displayName") or {}).get("text", "")
            types = p.get("types") or []
            match, _, _, _ = clasificar(nombre, ";".join(types))
            estado, accion = clasificar_estado(nombre, types, padron)
            filas.append({
                "nombre": nombre, "direccion": p.get("formattedAddress", ""),
                "business_status": p.get("businessStatus", ""), "types": ";".join(types),
                "clasificacion": match, "query_origen": q,
                "estado_en_padron": estado, "accion_sugerida": accion,
            })
        if i < len(queries):
            time.sleep(args.pause)

    OUT.mkdir(parents=True, exist_ok=True)
    cols = ["nombre", "direccion", "business_status", "types", "clasificacion", "query_origen",
            "estado_en_padron", "accion_sugerida"]
    with (OUT / "candidatos_extra_a_validar.csv").open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(filas)
    from collections import Counter
    est = Counter(f["estado_en_padron"] for f in filas)
    with (OUT / "resumen_recall_google.csv").open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh); w.writerow(["indicador", "valor"])
        w.writerow(["fecha", dt.date.today().isoformat()])
        w.writerow(["queries", len(queries)]); w.writerow(["resultados_unicos", len(filas)])
        for k, v in est.items():
            w.writerow([k, v])
    print(f"Recall Google: {len(filas)} resultados · {dict(est)}")
    print("NO se modificó el padrón. Revisar candidatos_extra_a_validar.csv.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
