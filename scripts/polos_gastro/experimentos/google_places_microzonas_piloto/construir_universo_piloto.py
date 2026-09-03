# -*- coding: utf-8 -*-
"""Piloto Google Places + microzonas — Etapa 2: universo piloto por zona.

EXPERIMENTO CONTROLADO. Solo lectura de insumos ya construidos; no toca datos fuente.

- Base: universo F01+F02 del pipeline_microzonas_v1 (universo_entidades_v1.csv,
  decisión de Diego 2026-07-08: Google Places nunca como fuente principal).
- Recorta a las macrozonas piloto (contenedores de macrozonas_editoriales_candidatas_v1).
- Si existe places_sanitizado.csv (Etapa 1 ejecutada), lo integra como ENRIQUECIMIENTO:
  deduplica contra F01+F02 con los umbrales ya justificados en pipeline_microzonas_v1/config.py
  (15 m misma parcela; 40 m + nombre compatible = mismo local).
- Output: UNIVERSO_PILOTO_SANITIZADO.csv (sin place_id, sin dirección exacta).

Uso:
    .venv/Scripts/python.exe scripts/polos_gastro/historico/experimentos/google_places_microzonas_piloto/construir_universo_piloto.py
"""
from __future__ import annotations

import json
from pathlib import Path

import geopandas as gpd
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]

UNIVERSO_V1 = (ROOT / "outputs" / "polos_gastro" / "historico" / "experimentos" / "pipeline_microzonas_v1"
               / "universo" / "universo_entidades_v1.csv")
MACROZONAS = (ROOT / "outputs" / "polos_gastro" / "historico" / "experimentos"
              / "infraestructura_cartografica_v1" / "macrozonas_editoriales_candidatas_v1.geojson")
SALIDA = ROOT / "outputs" / "polos_gastro" / "historico" / "experimentos" / "google_places_microzonas_piloto"
PLACES_SANITIZADO = SALIDA / "places" / "places_sanitizado.csv"
OUT_CSV = SALIDA / "UNIVERSO_PILOTO_SANITIZADO.csv"
OUT_QA = SALIDA / "qa_universo_piloto.json"

CRS_GEO = "EPSG:4326"
CRS_METRICO = "EPSG:5347"

ZONAS_PILOTO = {
    "palermo_soho_hollywood": ["MZ_PALERMO_SOHO", "MZ_PALERMO_HOLLYWOOD"],
    "corrientes_microcentro": ["MZ_AVENIDA_CORRIENTES", "MZ_MICROCENTRO_Y_CENTRO"],
    "belgrano": ["MZ_BELGRANO"],
    "san_telmo": ["MZ_SAN_TELMO"],
}
# Umbrales de dedup (config.py del pipeline_microzonas_v1, con justificación allá):
DEDUP_MISMA_PARCELA_M = 15
DEDUP_NOMBRE_COMPATIBLE_M = 40


def nombres_compatibles(a: str, b: str) -> bool:
    a, b = (a or "").strip(), (b or "").strip()
    if not a or not b:
        return False
    if a in b or b in a:
        return True
    ta, tb = set(a.split()), set(b.split())
    inter = ta & tb
    return len(inter) / max(1, min(len(ta), len(tb))) >= 0.5


def main() -> int:
    ent = pd.read_csv(UNIVERSO_V1, dtype={"id_ubicacion": str})
    apta = ent["apta_clustering"].astype(str).str.lower().isin(["true", "si", "1", "1.0"])
    ent = ent[apta & ent["lat"].notna() & ent["lon"].notna()].copy()

    mz = gpd.read_file(MACROZONAS)
    zona_de = {i: z for z, lst in ZONAS_PILOTO.items() for i in lst}
    mz = mz[mz["id"].isin(zona_de)].copy()
    mz["zona_piloto"] = mz["id"].map(zona_de)

    g_ent = gpd.GeoDataFrame(ent, geometry=gpd.points_from_xy(ent["lon"], ent["lat"]),
                             crs=CRS_GEO)
    dentro = gpd.sjoin(g_ent, mz[["id", "zona_piloto", "geometry"]],
                       how="inner", predicate="within")
    # Si un punto cayera en 2 macrozonas (QA dijo 0 entre contenedores), se queda con la 1ra.
    n_multi = int(dentro.index.duplicated().sum())
    dentro = dentro[~dentro.index.duplicated(keep="first")].copy()
    dentro = dentro.rename(columns={"id": "macrozona_id"})

    base = pd.DataFrame({
        "id_punto": dentro["id_entidad"],
        "zona_piloto": dentro["zona_piloto"],
        "macrozona_id": dentro["macrozona_id"],
        "nombre_normalizado": dentro["nombre_norm"].fillna(""),
        "lat": dentro["lat"], "lon": dentro["lon"],
        "categoria": dentro["categoria_canonica"].fillna(""),
        "rating": "", "user_ratings_total": "",
        "fuente": "F01+F02",
    })

    qa = {
        "f01f02_en_zonas_piloto": int(len(base)),
        "f01f02_por_zona": base.groupby("zona_piloto").size().to_dict(),
        "puntos_en_mas_de_una_macrozona": n_multi,
        "places_disponible": PLACES_SANITIZADO.exists(),
        "places_puntos_brutos": 0,
        "places_duplicados_vs_f01f02": 0,
        "places_nuevos_incorporados": 0,
        "places_nuevos_por_zona": {},
    }

    if PLACES_SANITIZADO.exists():
        pl = pd.read_csv(PLACES_SANITIZADO)
        qa["places_puntos_brutos"] = int(len(pl))
        # Contención estricta: la grilla de consulta se extiende ~175 m más allá del
        # borde (40 m de borde + radio 135 m), así que Places puede devolver locales
        # FUERA de la macrozona. Se re-verifica por geometría y se descartan.
        g_pl_geo = gpd.GeoDataFrame(
            pl.drop(columns=["zona_piloto", "macrozona_id"]),
            geometry=gpd.points_from_xy(pl["lon"], pl["lat"]), crs=CRS_GEO)
        dentro_pl = gpd.sjoin(g_pl_geo, mz[["id", "zona_piloto", "geometry"]],
                              how="inner", predicate="within")
        dentro_pl = dentro_pl[~dentro_pl.index.duplicated(keep="first")]
        qa["places_fuera_de_macrozona_descartados"] = int(len(pl) - len(dentro_pl))
        pl = pd.DataFrame(dentro_pl.drop(columns=["geometry", "index_right"]))
        pl = pl.rename(columns={"id": "macrozona_id"})
        g_pl = gpd.GeoDataFrame(pl, geometry=gpd.points_from_xy(pl["lon"], pl["lat"]),
                                crs=CRS_GEO).to_crs(CRS_METRICO)
        g_base = gpd.GeoDataFrame(base.copy(),
                                  geometry=gpd.points_from_xy(base["lon"], base["lat"]),
                                  crs=CRS_GEO).to_crs(CRS_METRICO)
        cerca = gpd.sjoin_nearest(g_pl, g_base[["nombre_normalizado", "geometry"]],
                                  how="left", max_distance=DEDUP_NOMBRE_COMPATIBLE_M,
                                  distance_col="dist_m")
        cerca = cerca[~cerca.index.duplicated(keep="first")]
        import numpy as np
        nombre_ok = np.array([nombres_compatibles(a, b) for a, b in
                              zip(cerca["nombre_normalizado_left"].fillna(""),
                                  cerca["nombre_normalizado_right"].fillna(""))])
        dup = (cerca["dist_m"] <= DEDUP_MISMA_PARCELA_M) | (
            (cerca["dist_m"] <= DEDUP_NOMBRE_COMPATIBLE_M) & nombre_ok
        )
        nuevos = pl.loc[~dup.values].copy()
        qa["places_duplicados_vs_f01f02"] = int(dup.sum())
        qa["places_nuevos_incorporados"] = int(len(nuevos))
        qa["places_nuevos_por_zona"] = nuevos.groupby("zona_piloto").size().to_dict()
        base = pd.concat([base, pd.DataFrame({
            "id_punto": nuevos["id_punto_places"],
            "zona_piloto": nuevos["zona_piloto"],
            "macrozona_id": nuevos["macrozona_id"],
            "nombre_normalizado": nuevos["nombre_normalizado"].fillna(""),
            "lat": nuevos["lat"], "lon": nuevos["lon"],
            "categoria": nuevos["categoria"].fillna(""),
            "rating": nuevos["rating"], "user_ratings_total": nuevos["user_ratings_total"],
            "fuente": "google_places",
        })], ignore_index=True)

    qa["universo_piloto_total"] = int(len(base))
    qa["universo_por_zona_y_fuente"] = {
        f"{z}|{f}": int(n) for (z, f), n in base.groupby(["zona_piloto", "fuente"]).size().items()
    }

    SALIDA.mkdir(parents=True, exist_ok=True)
    base.to_csv(OUT_CSV, index=False, encoding="utf-8")
    OUT_QA.write_text(json.dumps(qa, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[universo] {len(base)} puntos ({qa['f01f02_en_zonas_piloto']} F01+F02 + "
          f"{qa['places_nuevos_incorporados']} Places nuevos) -> {OUT_CSV}")
    print(f"[universo] QA -> {OUT_QA}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
