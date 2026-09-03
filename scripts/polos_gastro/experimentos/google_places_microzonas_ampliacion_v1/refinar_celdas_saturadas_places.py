# -*- coding: utf-8 -*-
"""Refinamiento puntual de celdas saturadas Google Places.

Dry-run por defecto. Impide consultar macrozonas completas: solo acepta una
lista explicita de `celda_id` ya presentes en los planes de consulta y marcadas
como saturadas en QA. La ejecucion real requiere `--execute --confirm-real-api`.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from preparar_consultas_places_ampliacion import (  # noqa: E402
    BLOQUE_GUARDADO,
    COSTO_USD_POR_1000,
    COLUMNS_INTERNO,
    COLUMNS_SANITIZADO,
    DIR_INTERNO,
    DIR_PLACES,
    ERROR_ABORT_MIN_ERRORS,
    ERROR_ABORT_MIN_REQUESTS,
    ERROR_ABORT_RATE,
    MAX_CONSULTAS_HARD_CAP,
    call_places_nearby,
    detect_api_key,
    es_gastronomico,
    normalizar_nombre,
    rutas_tanda,
)

RADIO_REFINO_M = 70.0
SALIDA = ROOT / "outputs" / "polos_gastro" / "historico" / "experimentos" / "google_places_microzonas_ampliacion_v1"
DIR_REFINO = SALIDA / "places" / "refinamientos"
DIR_REFINO_INTERNO = DIR_INTERNO / "refinamientos"


def cargar_plan() -> dict:
    out = {}
    for tanda in ("a_criticas", "b_consolidacion"):
        path = rutas_tanda(tanda)["plan"]
        with path.open("r", encoding="utf-8-sig", newline="") as fh:
            for row in csv.DictReader(fh):
                row["tanda"] = tanda
                out[row["celda_id"]] = row
    return out


def celdas_saturadas() -> set[str]:
    out = set()
    for tanda in ("a_criticas", "b_consolidacion"):
        path = DIR_PLACES / f"qa_saturacion_{tanda}.json"
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            out.update((data.get("celdas_saturadas") or {}).keys())
    return out


def subconsultas(celda: dict, grilla: str) -> list[dict]:
    # Offsets en grados aproximados solo para subdividir localmente el centro de consulta.
    # A 35 m el error longitudinal en CABA es despreciable frente al radio 70 m.
    lat = float(celda["lat"])
    lon = float(celda["lon"])
    step_lat = 35.0 / 111_320.0
    step_lon = 35.0 / (111_320.0 * 0.86)
    if grilla == "2x2":
        offs = [(-0.5, -0.5), (-0.5, 0.5), (0.5, -0.5), (0.5, 0.5)]
    else:
        offs = [(a, b) for a in (-1, 0, 1) for b in (-1, 0, 1)]
    rows = []
    for i, (oy, ox) in enumerate(offs, 1):
        rows.append({
            "celda_refino_id": f"{celda['celda_id']}_R{i:02d}_{grilla}",
            "celda_origen": celda["celda_id"],
            "zona_piloto": celda["zona_piloto"],
            "macrozona_id": celda["macrozona_id"],
            "tanda_origen": celda["tanda"],
            "lat": round(lat + oy * step_lat, 6),
            "lon": round(lon + ox * step_lon, 6),
            "radio_m": RADIO_REFINO_M,
        })
    return rows


def escribir_csv(path: Path, cols: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def escribir_sanitizado(path: Path, internos: list[dict]) -> None:
    filas = [{
        "id_punto_places": r["id_punto_places"],
        "zona_piloto": r["zona_piloto"],
        "macrozona_id": r["macrozona_id"],
        "nombre_normalizado": r["nombre_norm"],
        "lat": r["lat"],
        "lon": r["lon"],
        "categoria": r["categoria_google"],
        "rating": r.get("rating_interno", ""),
        "user_ratings_total": r.get("user_ratings_total_interno", ""),
        "business_status": r.get("business_status", ""),
        "fuente": "google_places",
        "fecha_consulta": r["fecha_consulta"],
    } for r in internos]
    escribir_csv(path, COLUMNS_SANITIZADO, filas)


def main() -> int:
    ap = argparse.ArgumentParser(description="Refinamiento puntual Places (dry-run default).")
    ap.add_argument("--cells", required=True,
                    help="Lista separada por coma de celda_id saturadas explicitas.")
    ap.add_argument("--grid", choices=["2x2", "3x3"], default="2x2")
    ap.add_argument("--max-new-requests", type=int, default=MAX_CONSULTAS_HARD_CAP)
    ap.add_argument("--run-id", default=None)
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--confirm-real-api", action="store_true")
    args = ap.parse_args()

    plan = cargar_plan()
    saturadas = celdas_saturadas()
    cells = [c.strip() for c in args.cells.split(",") if c.strip()]
    if not cells:
        raise SystemExit("ERROR: lista de celdas vacia.")
    faltan = [c for c in cells if c not in plan]
    no_sat = [c for c in cells if c in plan and c not in saturadas]
    if faltan or no_sat:
        raise SystemExit(f"ERROR: celdas invalidas. faltan={faltan} no_saturadas={no_sat}")
    rows = []
    for c in cells:
        rows.extend(subconsultas(plan[c], args.grid))
    if len(rows) > args.max_new_requests:
        raise SystemExit(f"ERROR: {len(rows)} consultas exceden cap {args.max_new_requests}.")
    run_id = args.run_id or f"{args.grid}_{len(cells)}celdas"
    plan_path = DIR_REFINO / f"plan_refino_{run_id}.csv"
    escribir_csv(plan_path, ["celda_refino_id", "celda_origen", "zona_piloto",
                             "macrozona_id", "tanda_origen", "lat", "lon", "radio_m"], rows)
    costo = round(len(rows) * COSTO_USD_POR_1000 / 1000, 2)
    print(f"[refino][plan] celdas_origen={len(cells)} grilla={args.grid} "
          f"consultas={len(rows)} costo_max_usd={costo} cap={args.max_new_requests}")
    print(f"[refino][plan] plan -> {plan_path}")
    if not args.execute:
        print("[refino][dry_run] No se llamo a Google Places API.")
        return 0
    if not args.confirm_real_api:
        raise SystemExit("ERROR: ejecucion real requiere --confirm-real-api.")

    api_key, estado = detect_api_key()
    print(f"[refino][execute] API key: {estado}")
    if not api_key:
        raise SystemExit("ERROR: falta API key.")
    DIR_REFINO_INTERNO.mkdir(parents=True, exist_ok=True)
    interno_path = DIR_REFINO_INTERNO / f"places_resultados_interno_refino_{run_id}.csv"
    sanitizado_path = DIR_REFINO / f"places_sanitizado_refino_{run_id}.csv"
    progreso_path = DIR_REFINO_INTERNO / f"progreso_refino_{run_id}.json"
    hechas = set()
    internos = []
    if progreso_path.exists():
        hechas = set(json.loads(progreso_path.read_text(encoding="utf-8")))
        if interno_path.exists():
            with interno_path.open("r", encoding="utf-8-sig", newline="") as fh:
                internos = list(csv.DictReader(fh))
    vistos = {r.get("google_place_id_interno") for r in internos}
    today = date.today().isoformat()
    n_req = n_err = 0
    seq = len(internos)

    def guardar():
        escribir_csv(interno_path, COLUMNS_INTERNO, internos)
        escribir_sanitizado(sanitizado_path, internos)
        progreso_path.write_text(json.dumps(sorted(hechas)), encoding="utf-8")

    for i, r in enumerate([x for x in rows if x["celda_refino_id"] not in hechas], 1):
        lugares, err = call_places_nearby(float(r["lat"]), float(r["lon"]),
                                          float(r["radio_m"]), api_key)
        n_req += 1
        hechas.add(r["celda_refino_id"])
        if err and lugares is None:
            n_err += 1
            if (n_req >= ERROR_ABORT_MIN_REQUESTS and n_err >= ERROR_ABORT_MIN_ERRORS
                    and (n_err / n_req) >= ERROR_ABORT_RATE):
                guardar()
                raise SystemExit(f"ERROR: tasa anormal de errores ({n_err}/{n_req}).")
        else:
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
                    "id_punto_places": f"PR{seq:04d}",
                    "zona_piloto": r["zona_piloto"],
                    "macrozona_id": r["macrozona_id"],
                    "celda_id": r["celda_refino_id"],
                    "nombre_norm": normalizar_nombre(p["nombre_google"]),
                    "fecha_consulta": today,
                    **p,
                })
        if i % BLOQUE_GUARDADO == 0:
            guardar()
            print(f"[refino][execute] {i}/{len(rows)} consultas | unicos={len(internos)} err={n_err}")
        time.sleep(0.12)
    guardar()
    print(f"[refino][execute] TOTAL consultas={n_req} puntos_unicos={len(internos)} errores={n_err}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
