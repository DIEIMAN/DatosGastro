"""Consolida (SIN nuevos requests) las corridas de Google Places ya descargadas:
la ampliada inicial + la tanda de barrios (barrios_01), deduplicando entre ambas
y reclasificando todo con el criterio ajustado compartido.

Lee los RAW ya guardados (no llama a Google, no usa API key):
  google_places_raw_ampliado.json
  google_places_raw_barrios_01.json   (y/o otros raw_<tag>.json indicados)

Genera:
  google_places_consolidado_deduplicado.csv
  google_places_consolidado_resumen.csv
  google_places_consolidado_calidad_queries.csv

NO integra AGC/OSM. NO genera PDF. NO commitea.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import math
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from google_places_clasificador import (  # noqa: E402
    A, B, C, MARCAS_ESPERADAS, RANK, clasificar, conf_integrada, norm_nombre,
)

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs" / "casas_pastas_google_places"

DEFAULT_RAWS = ["google_places_raw_ampliado.json", "google_places_raw_barrios_01.json"]

# raw_<tag>.json no guarda la query de origen por resultado; los candidatos sí.
# Para la query_origen consolidada usamos los candidatos_*.csv si están disponibles.
DEFAULT_CANDS = ["google_places_candidatos_ampliado.csv", "google_places_candidatos_barrios_01.csv"]


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


def cargar_query_por_pid(cand_files: list[Path]) -> dict[str, set[str]]:
    """place_id -> set de query_origen, leído de los candidatos_*.csv disponibles."""
    qmap: dict[str, set[str]] = {}
    for cf in cand_files:
        if not cf.exists():
            continue
        for r in csv.DictReader(cf.open(encoding="utf-8-sig")):
            pid = r.get("place_id", "")
            q = r.get("query_origen", "")
            if pid:
                qmap.setdefault(pid, set()).add(q)
    return qmap


def main() -> int:
    ap = argparse.ArgumentParser(description="Consolida corridas Google Places ya descargadas (sin requests).")
    ap.add_argument("--raws", nargs="*", default=DEFAULT_RAWS,
                    help="Archivos raw_*.json a consolidar (relativos a la carpeta de salida).")
    ap.add_argument("--cands", nargs="*", default=DEFAULT_CANDS,
                    help="Archivos candidatos_*.csv para mapear query_origen.")
    ap.add_argument("--out-prefix", default="google_places_consolidado",
                    help="Prefijo de salida (ej. 'google_places_consolidado_plus' para Parte 4).")
    ap.add_argument("--faltantes", action="store_true",
                    help="Además, escribe google_places_faltantes_resueltos.csv con el estado de marcas esperadas.")
    args = ap.parse_args()

    dedup_out = OUT / f"{args.out_prefix}_deduplicado.csv"
    resumen_out = OUT / f"{args.out_prefix}_resumen.csv"
    calidad_out = OUT / f"{args.out_prefix}_calidad_queries.csv"

    raw_paths = [OUT / r for r in args.raws]
    presentes = [p for p in raw_paths if p.exists()]
    faltan = [p.name for p in raw_paths if not p.exists()]
    if not presentes:
        print("ABORTADO: no hay ningún raw_*.json para consolidar.")
        print(f"  Buscados: {', '.join(p.name for p in raw_paths)}")
        print("  Corré primero la ampliación y la tanda barrios_01.")
        return 2
    if faltan:
        print(f"AVISO: faltan (se consolida solo lo presente): {', '.join(faltan)}")

    qmap = cargar_query_por_pid([OUT / c for c in args.cands])

    # Junta todos los places de todos los raws.
    places: list[dict] = []
    for p in presentes:
        data = json.load(p.open(encoding="utf-8"))
        places.extend(data)
        print(f"  {p.name}: {len(data)} places")

    # Normaliza + clasifica con el criterio compartido.
    registros = []
    for pl in places:
        nombre = (pl.get("displayName") or {}).get("text", "")
        loc = pl.get("location") or {}
        types = pl.get("types") or []
        match, conf, motivo, rev = clasificar(nombre, ";".join(types))
        pid = pl.get("id", "")
        registros.append({
            "place_id": pid,
            "nombre": nombre,
            "direccion": pl.get("formattedAddress", ""),
            "lat": loc.get("latitude", ""),
            "lon": loc.get("longitude", ""),
            "business_status": pl.get("businessStatus", ""),
            "types": ";".join(types),
            "match_casas_pastas": match,
            "motivo_clasificacion": motivo,
            "queries": set(qmap.get(pid, set())),
        })

    # Dedup por place_id y luego por (nombre normalizado + cercanía <75m o dirección igual).
    by_pid: dict[str, dict] = {}
    sin_pid: list[dict] = []
    for r in registros:
        pid = r["place_id"]
        if not pid:
            sin_pid.append(r)
            continue
        if pid in by_pid:
            g = by_pid[pid]
            g["queries"] |= r["queries"]
            if RANK[r["match_casas_pastas"]] > RANK[g["match_casas_pastas"]]:
                g["match_casas_pastas"] = r["match_casas_pastas"]
                g["motivo_clasificacion"] = r["motivo_clasificacion"]
        else:
            by_pid[pid] = dict(r)

    grupos = list(by_pid.values())
    fus = [False] * len(grupos)
    for i in range(len(grupos)):
        if fus[i]:
            continue
        for j in range(i + 1, len(grupos)):
            if fus[j]:
                continue
            a, b = grupos[i], grupos[j]
            mismo_nombre = norm_nombre(a["nombre"]) == norm_nombre(b["nombre"]) and a["nombre"]
            cerca = haversine_m(a["lat"], a["lon"], b["lat"], b["lon"]) < 75
            misma_dir = norm_dir(a["direccion"]) == norm_dir(b["direccion"]) and a["direccion"]
            if mismo_nombre and (cerca or misma_dir):
                a["queries"] |= b["queries"]
                if RANK[b["match_casas_pastas"]] > RANK[a["match_casas_pastas"]]:
                    a["match_casas_pastas"] = b["match_casas_pastas"]
                    a["motivo_clasificacion"] = b["motivo_clasificacion"]
                fus[j] = True
    grupos = [g for k, g in enumerate(grupos) if not fus[k]] + sin_pid

    # Fila final consolidada.
    filas = []
    for g in grupos:
        nq = len([q for q in g["queries"] if q])
        match = g["match_casas_pastas"]
        rev = "si" if (match == B or (match == A and "media" in conf_integrada(match, nq))) else "no"
        filas.append({
            "place_id": g["place_id"],
            "nombre": g["nombre"],
            "direccion": g["direccion"],
            "lat": g["lat"],
            "lon": g["lon"],
            "business_status": g["business_status"],
            "types": g["types"],
            "match_casas_pastas": match,
            "cantidad_queries_detectado": nq,
            "queries_detectado": ";".join(sorted(q for q in g["queries"] if q)),
            "confianza_integrada_google": conf_integrada(match, nq),
            "requiere_revision_manual": rev,
            "motivo_clasificacion": g["motivo_clasificacion"],
        })
    filas.sort(key=lambda r: (-RANK[r["match_casas_pastas"]], -r["cantidad_queries_detectado"]))

    cols = ["place_id", "nombre", "direccion", "lat", "lon", "business_status", "types",
            "match_casas_pastas", "cantidad_queries_detectado", "queries_detectado",
            "confianza_integrada_google", "requiere_revision_manual", "motivo_clasificacion"]
    with dedup_out.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(filas)

    # Calidad por query: cuántos únicos aporta cada query.
    por_query: dict[str, dict] = {}
    primer_query: dict[str, str] = {}
    for f in filas:
        qs = [q for q in f["queries_detectado"].split(";") if q]
        for q in qs:
            d = por_query.setdefault(q, {"unicos": 0, "A": 0, "B": 0, "C": 0})
        # asigna "único nuevo" a la primera query (orden alfabético estable)
        if qs:
            q0 = qs[0]
            primer_query[f["place_id"] or f["nombre"]] = q0
            por_query[q0]["unicos"] += 1
            por_query[q0][f["match_casas_pastas"][0]] += 1
    with calidad_out.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["query", "unicos_atribuidos", "A", "B", "C"])
        for q in sorted(por_query):
            d = por_query[q]
            w.writerow([q, d["unicos"], d["A"], d["B"], d["C"]])

    a = sum(1 for f in filas if f["match_casas_pastas"] == A)
    b = sum(1 for f in filas if f["match_casas_pastas"] == B)
    c = sum(1 for f in filas if f["match_casas_pastas"] == C)
    with resumen_out.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["indicador", "valor"])
        w.writerow(["fecha", dt.date.today().isoformat()])
        w.writerow(["fuente", "Google Places API (New) - CONSOLIDADO (sin nuevos requests, no oficial)"])
        w.writerow(["raws_consolidados", ";".join(p.name for p in presentes)])
        w.writerow(["resultados_brutos", len(places)])
        w.writerow(["establecimientos_unicos", len(filas)])
        w.writerow(["A_google_probable_casa_pastas", a])
        w.writerow(["B_google_dudoso", b])
        w.writerow(["C_google_descartado", c])

    # Parte 4 opcional: estado de marcas esperadas tras consolidar.
    if args.faltantes:
        falt_out = OUT / "google_places_faltantes_resueltos.csv"
        with falt_out.open("w", encoding="utf-8-sig", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["marca", "sucursales", "sucursales_A", "status"])
            for marca, claves in MARCAS_ESPERADAS.items():
                hits = [f for f in filas if any(k in norm_nombre(f["nombre"]) for k in claves)]
                n_a = sum(1 for h in hits if h["match_casas_pastas"] == A)
                status = "ausente" if not hits else ("subrepresentada" if n_a <= 1 else "presente")
                w.writerow([marca, len(hits), n_a, status])
        print(f"  + {falt_out.name}")

    print(f"Consolidado: brutos={len(places)} -> unicos={len(filas)} | A={a} B={b} C={c}")
    print(f"Archivos: {dedup_out.name}, {resumen_out.name}, {calidad_out.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
