"""Ampliación CONTROLADA del piloto de Google Places (casas/fábricas de pastas en CABA).

Extiende el piloto inicial con más queries (tandas/batches) y deduplicación.
NO integra con AGC ni OSM. NO genera PDF. NO toca el pipeline principal.
Los resultados de Google NO son "oficiales" y se mantienen en universo aparte.

SEGURIDAD (guardrails)
----------------------
- La API key se lee SOLO de la variable de entorno GOOGLE_MAPS_API_KEY.
- Nunca se imprime, loguea, guarda ni commitea la API key.
- --dry-run por defecto: sin --run no hay requests reales.
- Topes: --max-queries, --max-results, --batch-size, --pause.
- No sobrescribe salidas previas sin backup (las mueve a backups/ con timestamp).
- Salidas del ampliado separadas de las del piloto inicial.
- Solo Places API oficial (Text Search New). Nada de scraping.
- Campos MÍNIMOS: id, displayName, formattedAddress, location, businessStatus, types.
  (NO se piden rating, teléfono, horarios, web ni reviews.)

USO
---
  # Simulación (no gasta, no llama a la API):
  python scripts/casas_pastas/google_places_ampliado.py

  # Ejecución real (requiere GOOGLE_MAPS_API_KEY en el entorno):
  python scripts/casas_pastas/google_places_ampliado.py --run
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import math
import os
import re
import shutil
import sys
import time
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from google_places_clasificador import clasificar as _clasificar, conf_integrada  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs" / "casas_pastas_google_places"
BACKUPS = OUT / "backups"
QUERY_FILE_DEFAULT = OUT / "queries_google_places_caba_ampliado.csv"

def paths_for_tag(tag: str):
    """Devuelve (RAW, CAND, RESUMEN, DEDUP, CALIDAD, LOG) para un tag de salida.

    tag 'ampliado' (default) conserva los nombres de la corrida ampliada original.
    Cualquier otro tag (ej. 'barrios_01') usa archivos separados, sin pisar lo anterior.
    """
    if tag == "ampliado":
        return (OUT / "google_places_raw_ampliado.json",
                OUT / "google_places_candidatos_ampliado.csv",
                OUT / "google_places_resumen_ampliado.csv",
                OUT / "google_places_deduplicado.csv",
                OUT / "google_places_calidad_queries.csv",
                OUT / "ampliado_log.txt")
    return (OUT / f"google_places_raw_{tag}.json",
            OUT / f"google_places_candidatos_{tag}.csv",
            OUT / f"google_places_resumen_{tag}.csv",
            OUT / f"google_places_deduplicado_{tag}.csv",
            OUT / f"google_places_calidad_queries_{tag}.csv",
            OUT / f"{tag}_log.txt")


# Defaults (se reasignan en main() según --tag).
RAW, CAND, RESUMEN, DEDUP, CALIDAD, LOG = paths_for_tag("ampliado")

ENDPOINT = "https://places.googleapis.com/v1/places:searchText"
FIELDS = [
    "places.id",
    "places.displayName",
    "places.formattedAddress",
    "places.location",
    "places.businessStatus",
    "places.types",
]

# Topes duros de esta etapa (primera ampliación, no la grilla completa).
HARD_MAX_QUERIES = 25
HARD_MAX_RESULTS = 200

def log(msg: str, *, to_file: bool = True) -> None:
    """Imprime y persiste en log. NUNCA recibe la API key."""
    line = f"[{dt.datetime.now().isoformat(timespec='seconds')}] {msg}"
    print(line)
    if to_file:
        OUT.mkdir(parents=True, exist_ok=True)
        with LOG.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")


def strip_acc(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c))


def norm_nombre(s: str) -> str:
    s = strip_acc((s or "").lower())
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def norm_dir(s: str) -> str:
    s = strip_acc((s or "").lower())
    for ruido in ("caba", "capital federal", "ciudad autonoma de buenos aires",
                  "buenos aires", "argentina", "c.a.b.a"):
        s = s.replace(ruido, " ")
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def haversine_m(lat1, lon1, lat2, lon2) -> float:
    try:
        lat1, lon1, lat2, lon2 = map(float, (lat1, lon1, lat2, lon2))
    except (TypeError, ValueError):
        return 1e9
    r = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def leer_queries(path: Path, max_queries: int) -> list[str]:
    if not path.exists():
        return []
    qs: list[str] = []
    with path.open(encoding="utf-8-sig", newline="") as fh:
        sample = fh.read(2048)
        fh.seek(0)
        if "," in sample.splitlines()[0]:
            r = csv.DictReader(fh)
            col = "query" if (r.fieldnames and "query" in r.fieldnames) else (r.fieldnames or [""])[0]
            for row in r:
                q = (row.get(col) or "").strip()
                if q:
                    qs.append(q)
        else:
            qs = [ln.strip() for ln in fh if ln.strip()]
    # dedup preservando orden
    seen, out = set(), []
    for q in qs:
        if q.lower() not in seen:
            seen.add(q.lower())
            out.append(q)
    return out[:max_queries]


def estimar_costo(n_queries: int) -> str:
    return (
        f"~{n_queries} requests de Text Search (New), tier 'Pro' por los campos pedidos. "
        f"1 request por query (sin paginación). Gasto esperado: del orden de centavos. "
        f"El precio por 1000 lo fija Google: CONFIRMAR contra el pricing vigente y el crédito "
        f"gratuito antes de ampliar a la grilla completa."
    )


def mostrar_plan(queries, max_results, batch_size, pause, modo, qfile) -> None:
    print("=" * 74)
    print(f"  GOOGLE PLACES AMPLIADO — MODO: {modo}")
    print("=" * 74)
    print(f"  Endpoint            : {ENDPOINT}")
    print(f"  Archivo de queries  : {qfile}")
    print(f"  Cantidad de queries : {len(queries)}")
    for i, q in enumerate(queries, 1):
        print(f"      {i:>2}. {q}")
    print(f"  Máx. requests       : {len(queries)} (1 por query, sin paginación)")
    print(f"  Máx. resultados     : {max_results}")
    print(f"  Tamaño de tanda     : {batch_size}")
    print(f"  Pausa entre requests: {pause:.1f} s")
    print(f"  Campos solicitados  : {', '.join(f.replace('places.', '') for f in FIELDS)}")
    print(f"  Carpeta de salida   : {OUT.relative_to(ROOT)}  (gitignored)")
    print(f"  Advertencia costo   : {estimar_costo(len(queries))}")
    print(f"  API key             : se lee de $GOOGLE_MAPS_API_KEY · NO se imprime ni se guarda")
    print("=" * 74)


def backup_si_existe(path: Path) -> None:
    if path.exists():
        BACKUPS.mkdir(parents=True, exist_ok=True)
        ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = BACKUPS / f"{path.stem}.{ts}{path.suffix}"
        shutil.copy2(path, dest)
        log(f"Backup: {path.name} -> backups/{dest.name}")


def hacer_request(key: str, query: str, page_size: int):
    import requests  # import diferido: dry-run no lo necesita
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": key,            # solo en el header
        "X-Goog-FieldMask": ",".join(FIELDS),
    }
    body = {"textQuery": query, "languageCode": "es", "regionCode": "AR", "pageSize": page_size}
    try:
        resp = requests.post(ENDPOINT, headers=headers, json=body, timeout=30)
    except Exception as exc:  # noqa: BLE001
        return [], f"excepción de red: {type(exc).__name__}"
    if resp.status_code != 200:
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
    match, conf, motivo, rev = _clasificar(nombre, ";".join(types))
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


RANK = {"A_google_probable_casa_pastas": 3, "B_google_dudoso": 2, "C_google_descartado": 1}


def deduplicar(filas: list[dict]) -> list[dict]:
    """Une por place_id y luego por (nombre normalizado + cercanía <75m o dirección igual)."""
    grupos: list[dict] = []  # cada grupo: dict con datos + set de queries + lista miembros

    def fusionar(grupo, fila):
        grupo["queries"].add(fila["query_origen"])
        # conserva la clasificación más fuerte (A>B>C)
        if RANK[fila["match_casas_pastas"]] > RANK[grupo["match_casas_pastas"]]:
            for k in ("match_casas_pastas", "motivo"):
                grupo[k] = fila[k]

    by_pid: dict[str, dict] = {}
    sin_pid: list[dict] = []
    for f in filas:
        pid = f["place_id"]
        if pid:
            if pid in by_pid:
                fusionar(by_pid[pid], f)
            else:
                g = dict(f)
                g["queries"] = {f["query_origen"]}
                by_pid[pid] = g
        else:
            sin_pid.append(f)

    grupos = list(by_pid.values())

    # segunda pasada: near-duplicates entre grupos con distinto place_id
    fusionado_flags = [False] * len(grupos)
    for i in range(len(grupos)):
        if fusionado_flags[i]:
            continue
        for j in range(i + 1, len(grupos)):
            if fusionado_flags[j]:
                continue
            a, b = grupos[i], grupos[j]
            mismo_nombre = norm_nombre(a["nombre"]) == norm_nombre(b["nombre"]) and a["nombre"]
            cerca = haversine_m(a["lat"], a["lon"], b["lat"], b["lon"]) < 75
            misma_dir = norm_dir(a["direccion"]) == norm_dir(b["direccion"]) and a["direccion"]
            if mismo_nombre and (cerca or misma_dir):
                a["queries"] |= b["queries"]
                if RANK[b["match_casas_pastas"]] > RANK[a["match_casas_pastas"]]:
                    a["match_casas_pastas"] = b["match_casas_pastas"]
                    a["motivo"] = b["motivo"]
                fusionado_flags[j] = True
    grupos = [g for k, g in enumerate(grupos) if not fusionado_flags[k]]

    # filas sin place_id: se agregan como propias (no fusionables con confianza)
    for f in sin_pid:
        g = dict(f)
        g["queries"] = {f["query_origen"]}
        grupos.append(g)

    out = []
    for g in grupos:
        nq = len(g["queries"])
        match = g["match_casas_pastas"]
        rev = "si" if (match.startswith("B_") or (match.startswith("A_") and "media" in g.get("confianza", ""))) else "no"
        out.append({
            "place_id": g["place_id"],
            "nombre": g["nombre"],
            "direccion": g["direccion"],
            "lat": g["lat"],
            "lon": g["lon"],
            "business_status": g["business_status"],
            "types": g["types"],
            "match_casas_pastas": match,
            "cantidad_queries_detectado": nq,
            "queries_detectado": ";".join(sorted(g["queries"])),
            "confianza_integrada_google": conf_integrada(match, nq),
            "requiere_revision_manual": rev,
            "motivo_clasificacion": g["motivo"],
        })
    out.sort(key=lambda r: (-RANK[r["match_casas_pastas"]], -r["cantidad_queries_detectado"]))
    return out


def escribir_salidas(filas, dedup, raw, queries, requests_hechas, errores, por_query):
    OUT.mkdir(parents=True, exist_ok=True)
    for p in (RAW, CAND, RESUMEN, DEDUP, CALIDAD):
        backup_si_existe(p)

    RAW.write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8")

    cand_cols = ["place_id", "nombre", "direccion", "lat", "lon", "business_status", "types",
                 "query_origen", "match_casas_pastas", "confianza", "motivo", "requiere_revision_manual"]
    with CAND.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cand_cols)
        w.writeheader()
        w.writerows(filas)

    dedup_cols = ["place_id", "nombre", "direccion", "lat", "lon", "business_status", "types",
                  "match_casas_pastas", "cantidad_queries_detectado", "queries_detectado",
                  "confianza_integrada_google", "requiere_revision_manual", "motivo_clasificacion"]
    with DEDUP.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=dedup_cols)
        w.writeheader()
        w.writerows(dedup)

    with CALIDAD.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["query", "resultados", "A", "B", "C", "unicos_nuevos", "aporte_relativo"])
        for q in queries:
            d = por_query.get(q, {})
            tot = d.get("total", 0)
            nuevos = d.get("nuevos", 0)
            aporte = round(nuevos / tot, 2) if tot else 0.0
            w.writerow([q, tot, d.get("A", 0), d.get("B", 0), d.get("C", 0), nuevos, aporte])

    a = sum(1 for f in dedup if f["match_casas_pastas"].startswith("A_"))
    b = sum(1 for f in dedup if f["match_casas_pastas"].startswith("B_"))
    c = sum(1 for f in dedup if f["match_casas_pastas"].startswith("C_"))
    with RESUMEN.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["indicador", "valor"])
        w.writerow(["fecha", dt.date.today().isoformat()])
        w.writerow(["fuente", "Google Places API (New) Text Search - AMPLIADO no oficial"])
        w.writerow(["queries_ejecutadas", requests_hechas])
        w.writerow(["queries_planificadas", len(queries)])
        w.writerow(["resultados_brutos", len(filas)])
        w.writerow(["establecimientos_unicos", len(dedup)])
        w.writerow(["A_google_probable_casa_pastas", a])
        w.writerow(["B_google_dudoso", b])
        w.writerow(["C_google_descartado", c])
        w.writerow(["errores", len(errores)])
    return a, b, c


def main() -> int:
    ap = argparse.ArgumentParser(description="Ampliación controlada Google Places (casas/fábricas de pastas).")
    ap.add_argument("--query-file", type=str, default=str(QUERY_FILE_DEFAULT))
    ap.add_argument("--tag", type=str, default="ampliado",
                    help="Etiqueta de salida (ej. 'barrios_01'). Genera archivos separados sin pisar lo anterior.")
    ap.add_argument("--run", action="store_true", help="Ejecuta requests reales. Sin esto: dry-run.")
    ap.add_argument("--max-queries", type=int, default=15)
    ap.add_argument("--max-results", type=int, default=120)
    ap.add_argument("--batch-size", type=int, default=5)
    ap.add_argument("--page-size", type=int, default=20)
    ap.add_argument("--pause", type=float, default=1.5)
    args = ap.parse_args()

    if args.max_queries > HARD_MAX_QUERIES:
        log(f"ABORTADO: --max-queries={args.max_queries} supera el tope ({HARD_MAX_QUERIES}).")
        return 2
    if args.max_results > HARD_MAX_RESULTS:
        log(f"ABORTADO: --max-results={args.max_results} supera el tope ({HARD_MAX_RESULTS}).")
        return 2
    page_size = max(1, min(20, args.page_size))
    batch_size = max(1, args.batch_size)

    # Reasigna las rutas de salida según --tag (no pisa la corrida anterior).
    global RAW, CAND, RESUMEN, DEDUP, CALIDAD, LOG
    RAW, CAND, RESUMEN, DEDUP, CALIDAD, LOG = paths_for_tag(args.tag)

    qfile = Path(args.query_file)
    queries = leer_queries(qfile, args.max_queries)
    if not queries:
        log(f"ABORTADO: no se leyeron queries de {qfile}")
        return 2

    modo = "EJECUCIÓN REAL (--run)" if args.run else "DRY-RUN (simulación, sin requests)"
    mostrar_plan(queries, args.max_results, batch_size, args.pause, modo, qfile)

    if not args.run:
        print("\nDRY-RUN: no se hicieron requests ni se gastó cuota.")
        print("Para ejecutar de verdad: agregá --run (requiere GOOGLE_MAPS_API_KEY).")
        return 0

    key = os.environ.get("GOOGLE_MAPS_API_KEY", "").strip()
    if not key:
        log("ABORTADO: falta GOOGLE_MAPS_API_KEY en el entorno. No se ejecuta nada.")
        print('\nPowerShell: $env:GOOGLE_MAPS_API_KEY = "<tu_api_key>"')
        return 2
    log(f"GOOGLE_MAPS_API_KEY detectada (no se imprime; longitud={len(key)}).")
    log(f"Inicio ampliado · queries={len(queries)} · batch={batch_size} · max_results={args.max_results}")

    raw_all, filas, errores = [], [], []
    vistos_pid: set[str] = set()
    por_query: dict[str, dict] = {}
    requests_hechas = 0

    for i, q in enumerate(queries, 1):
        if len(filas) >= args.max_results:
            log(f"Tope de resultados alcanzado ({args.max_results}). Se detiene.")
            break
        if i > 1 and (i - 1) % batch_size == 0:
            log(f"-- fin de tanda · pausa extra {args.pause * 2:.1f}s --")
            time.sleep(args.pause * 2)
        log(f"Request {i}/{len(queries)} (tanda {((i - 1) // batch_size) + 1}): query='{q}'")
        places, err = hacer_request(key, q, page_size)
        requests_hechas += 1
        stat = por_query.setdefault(q, {"total": 0, "A": 0, "B": 0, "C": 0, "nuevos": 0})
        if err:
            errores.append(f"{q} -> {err}")
            log(f"  error: {err}")
        else:
            log(f"  resultados: {len(places)}")
            for p in places:
                if len(filas) >= args.max_results:
                    break
                fila = normalizar(p, q)
                raw_all.append(p)
                filas.append(fila)
                stat["total"] += 1
                stat[fila["match_casas_pastas"][0]] += 1  # A/B/C por inicial
                pid = fila["place_id"]
                if pid and pid not in vistos_pid:
                    vistos_pid.add(pid)
                    stat["nuevos"] += 1
        if i < len(queries):
            time.sleep(args.pause)

    dedup = deduplicar(filas)
    a, b, c = escribir_salidas(filas, dedup, raw_all, queries, requests_hechas, errores, por_query)

    log("=" * 60)
    log(f"FIN · requests={requests_hechas} · brutos={len(filas)} · unicos={len(dedup)} · "
        f"A={a} B={b} C={c} · errores={len(errores)}")
    log(f"Archivos: {CAND.name}, {DEDUP.name}, {RESUMEN.name}, {CALIDAD.name}, {RAW.name}, {LOG.name}")
    if errores:
        for e in errores:
            log(f"  - {e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
