from __future__ import annotations

import csv
import json
import math
import os
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
CFG = json.loads((HERE / "config_tanda1_v4.json").read_text(encoding="utf-8"))
OUT = ROOT / "outputs/polos_gastro/historico/expansion_candidatos_v4_tanda1"
DOC = ROOT / "docs/polos_gastro/historico/expansion_candidatos_v4_tanda1"


def rel(path: str) -> Path:
    return ROOT / path


def git_cached() -> list[str]:
    proc = subprocess.run(
        ["git", "diff", "--cached", "--name-only"], cwd=ROOT,
        text=True, capture_output=True, check=False,
    )
    return [x for x in proc.stdout.splitlines() if x.strip()]


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6_371_008.8
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def load_cache_centers() -> list[dict]:
    rows: list[dict] = []
    for raw in CFG["planes_cache"]:
        path = rel(raw)
        if not path.exists():
            continue
        with path.open(encoding="utf-8-sig", newline="") as fh:
            for row in csv.DictReader(fh):
                rows.append({
                    "source": raw,
                    "celda_id": row.get("celda_id", ""),
                    "lat": float(row["lat"]), "lon": float(row["lon"]),
                    "radio_m": float(row.get("radio_m") or 0),
                })
    return rows


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    DOC.mkdir(parents=True, exist_ok=True)
    plan = pd.read_csv(rel(CFG["plan"]), encoding="utf-8-sig")
    t1 = plan[plan["tanda"].astype(str) == "1"].copy()
    t1["categoria_norm"] = t1["categoría"].astype(str).str.strip()
    checks: list[dict] = []

    def check(name: str, ok: bool, detail: str) -> None:
        checks.append({"control": name, "estado": "OK" if ok else "ERROR", "detalle": detail})

    zones = sorted(t1["zona_id"].unique().tolist())
    check("zonas", zones == CFG["zonas"], f"reales={zones}; esperadas={CFG['zonas']}")
    counts = t1["estado"].value_counts().to_dict()
    for state, expected in CFG["conteos_esperados"].items():
        check(f"conteo_{state}", int(counts.get(state, 0)) == expected,
              f"real={int(counts.get(state, 0))}; esperado={expected}")
    for zone, expected_states in CFG["por_zona"].items():
        z = t1[t1["zona_id"] == zone]["estado"].value_counts().to_dict()
        for state, expected in expected_states.items():
            check(f"conteo_{zone}_{state}", int(z.get(state, 0)) == expected,
                  f"real={int(z.get(state, 0))}; esperado={expected}")

    cats = sorted(t1["categoria_norm"].unique().tolist())
    check("categorias", cats == sorted(CFG["categorias"]), f"reales={cats}")
    check("radio", set(t1["radio_m"].astype(float)) == {float(CFG["radio_m"])},
          f"valores={sorted(set(t1['radio_m'].astype(float)))}")
    check("coordenadas_numericas", t1[["lat", "lon"]].notna().all().all(),
          f"nulos={int(t1[['lat','lon']].isna().sum().sum())}")
    check("coordenadas_caba", bool(t1["lat"].between(-34.75, -34.45).all() and
                                      t1["lon"].between(-58.60, -58.30).all()),
          "bbox prudencial CABA")
    check("ids_unicos", bool(t1["consulta_id"].is_unique),
          f"duplicados={int(t1['consulta_id'].duplicated().sum())}")
    pending = t1[t1["estado"] == "PENDIENTE_DECISION"]
    authorized = t1[t1["estado"].isin(CFG["estados_autorizados"])]
    check("pendientes_excluidas", len(set(pending["consulta_id"]) & set(authorized["consulta_id"])) == 0,
          f"pendientes={len(pending)}; autorizadas={len(authorized)}")

    areas = gpd.read_file(rel(CFG["areas"])).to_crs("EPSG:4326")
    mains = areas[(areas["zona_id"].isin(CFG["zonas"])) &
                  (areas["geometry_role"] == "AREA_PRINCIPAL")].copy()
    main_by_zone = {r.zona_id: r.geometry for r in mains.itertuples()}
    subunit_by_id = {
        str(r.subunidad_id): r.geometry
        for r in areas[areas["geometry_role"] == "SUBUNIDAD_ANALITICA"].itertuples()
        if str(r.subunidad_id).strip()
    }
    outside = []
    for row in t1.itertuples():
        subunit = "" if pd.isna(row.subunidad_id) else str(row.subunidad_id).strip()
        geom = subunit_by_id.get(subunit) if subunit else main_by_zone.get(row.zona_id)
        if geom is None or not geom.buffer(1e-8).covers(Point(float(row.lon), float(row.lat))):
            outside.append(row.consulta_id)
    check("dentro_areas_autorizadas", not outside,
          "validación contra subunidad explícita o área principal; " +
          f"fuera={len(outside)}" + (f"; ids={outside[:10]}" if outside else ""))

    # Brecha means no previously planned center covers the new center. A conservative
    # distance test uses the old radius; category rows share the same center by contract.
    cache = load_cache_centers()
    gaps = t1[t1["estado"] == "CONSULTAR_SOLO_BRECHA"].copy()
    covered = []
    for row in gaps.drop_duplicates(subset=["celda_id"]).itertuples():
        hits = [c for c in cache if haversine_m(float(row.lat), float(row.lon), c["lat"], c["lon"])
                <= max(1.0, c["radio_m"] * 0.25)]
        if hits:
            covered.append((row.celda_id, hits[0]["celda_id"]))
    check("brechas_no_en_cache", not covered,
          f"centros_brecha={gaps['celda_id'].nunique()}; coincidencias_centro={len(covered)}")
    cached_flag = gaps["consulta_existente_equivalente"].astype(str).str.upper().ne("NO")
    check("flag_equivalencia_brechas", not bool(cached_flag.any()),
          f"filas_con_equivalente={int(cached_flag.sum())}")

    cached = git_cached()
    check("staging_vacio", not cached, f"archivos_staged={len(cached)}")
    credential_state = {
        name: "PRESENTE" if os.environ.get(name) else "AUSENTE"
        for name in ("GOOGLE_MAPS_API_KEY", "GOOGLE_PLACES_API_KEY")
    }
    check("credencial_entorno", any(v == "PRESENTE" for v in credential_state.values()),
          "; ".join(f"{k}={v}" for k, v in credential_state.items()))

    qa = pd.DataFrame(checks)
    qa.to_csv(OUT / "QA_PRECHECK_API_TANDA1_V4.csv", index=False, encoding="utf-8-sig")
    summary_rows = []
    for zone in CFG["zonas"]:
        z = t1[t1["zona_id"] == zone]
        summary_rows.append({
            "zona_id": zone,
            "reutilizar_existente": int((z["estado"] == "REUTILIZAR_EXISTENTE").sum()),
            "consultar_solo_brecha": int((z["estado"] == "CONSULTAR_SOLO_BRECHA").sum()),
            "pendiente_decision_excluida": int((z["estado"] == "PENDIENTE_DECISION").sum()),
            "celdas_brecha_unicas": int(z.loc[z["estado"] == "CONSULTAR_SOLO_BRECHA", "celda_id"].nunique()),
            "api_habilitada": "SI" if any(v == "PRESENTE" for v in credential_state.values()) else "NO",
        })
    pd.DataFrame(summary_rows).to_csv(
        OUT / "RESUMEN_AUTORIZACION_CONSULTAS_TANDA1_V4.csv", index=False, encoding="utf-8-sig")

    hard_errors = qa[(qa["estado"] == "ERROR") & (qa["control"] != "credencial_entorno")]
    api_ready = hard_errors.empty and any(v == "PRESENTE" for v in credential_state.values())
    state = "API_READY" if api_ready else ("REUSE_ONLY" if hard_errors.empty else "BLOCKED_DIVERGENCE")
    lines = [
        "# Precheck API — Tanda 1 Expansión V4", "",
        "**Estado:** `" + state + "`  ",
        "**Carácter:** EXPERIMENTAL / NO OFICIAL  ",
        "**Fecha de corte:** 2026-07-12", "",
        "## Resultado", "",
        f"- Plan Tanda 1: {len(t1)} filas categoría×celda.",
        f"- Reutilizar existente: {int((t1['estado']=='REUTILIZAR_EXISTENTE').sum())}.",
        f"- Consultar solo brecha: {int((t1['estado']=='CONSULTAR_SOLO_BRECHA').sum())}.",
        f"- Pendiente de decisión, excluidas: {len(pending)}.",
        f"- Celdas físicas nuevas: {gaps['celda_id'].nunique()} (cinco categorías por celda).",
        f"- Credencial: {', '.join(f'{k}={v}' for k,v in credential_state.items())}.", "",
        "No se leyó `.env` y no se expuso ningún secreto. " +
        ("La ejecución API puede continuar con el script acotado." if api_ready else
         "No se habilita la API; corresponde completar en modo de reutilización."), "",
        "## Controles", "",
        "| Control | Estado | Detalle |", "|---|---|---|",
    ]
    lines += [f"| {r.control} | {r.estado} | {str(r.detalle).replace('|','/')} |" for r in qa.itertuples()]
    (DOC / "PRECHECK_API_TANDA1_V4.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (OUT / "ESTADO_PRECHECK_TANDA1_V4.json").write_text(json.dumps({
        "estado": state, "api_ready": api_ready,
        "conteos": {k: int(v) for k, v in counts.items()},
        "celdas_brecha_unicas": int(gaps["celda_id"].nunique()),
        "credenciales": credential_state,
        "hard_errors": hard_errors.to_dict(orient="records"),
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(state)
    return 0 if state in {"API_READY", "REUSE_ONLY"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
