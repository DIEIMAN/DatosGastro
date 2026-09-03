# -*- coding: utf-8 -*-
"""Ampliacion Google Places v1 - Etapa 2: universo sanitizado para Tanda A.

EXPERIMENTO CONTROLADO. Lee insumos ya existentes y escribe solo en
`outputs/polos_gastro/historico/experimentos/google_places_microzonas_ampliacion_v1/`.
No toca F01-F05, Fase 25, informes oficiales ni datos fuente.

Calcula:
- contencion estricta contra las macrozonas de Tanda A;
- duplicados por place_id contra el piloto;
- duplicados espaciales/textuales contra el universo F01+F02;
- puntos Google Places nuevos incorporables en capa experimental sanitizada.
"""
from __future__ import annotations

import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]

UNIVERSO_V1 = (ROOT / "outputs" / "polos_gastro" / "historico" / "experimentos" / "pipeline_microzonas_v1"
               / "universo" / "universo_entidades_v1.csv")
MACROZONAS = (ROOT / "outputs" / "polos_gastro" / "historico" / "experimentos"
              / "infraestructura_cartografica_v1" / "macrozonas_editoriales_candidatas_v1.geojson")
SALIDA = ROOT / "outputs" / "polos_gastro" / "historico" / "experimentos" / "google_places_microzonas_ampliacion_v1"
PILOTO_INTERNO = (ROOT / "outputs" / "polos_gastro" / "historico" / "experimentos"
                  / "google_places_microzonas_piloto" / "interno"
                  / "places_resultados_interno.csv")
PLACES_INTERNO = SALIDA / "interno" / "places_resultados_interno_a_criticas.csv"

OUT_UNIVERSO = SALIDA / "UNIVERSO_AMPLIADO_TANDA_A_SANITIZADO.csv"
OUT_NUEVOS = SALIDA / "places_nuevos_tanda_a_sanitizado.csv"
OUT_QA = SALIDA / "qa_universo_ampliacion_tanda_a.json"

CRS_GEO = "EPSG:4326"
CRS_METRICO = "EPSG:5347"

ZONAS_TANDA_A = {
    "MZ_CHACARITA": "chacarita",
    "MZ_PUERTO_MADERO": "puerto_madero",
    "MZ_COSTANERA_NORTE": "costanera_norte",
    "MZ_AVENIDA_CASEROS_BARRACAS": "caseros_barracas",
}
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


def cargar_base_f01f02(mz: gpd.GeoDataFrame) -> pd.DataFrame:
    ent = pd.read_csv(UNIVERSO_V1, dtype={"id_ubicacion": str})
    apta = ent["apta_clustering"].astype(str).str.lower().isin(["true", "si", "1", "1.0"])
    ent = ent[apta & ent["lat"].notna() & ent["lon"].notna()].copy()
    g_ent = gpd.GeoDataFrame(ent, geometry=gpd.points_from_xy(ent["lon"], ent["lat"]),
                             crs=CRS_GEO)
    dentro = gpd.sjoin(g_ent, mz[["id", "zona_piloto", "geometry"]],
                       how="inner", predicate="within")
    dentro = dentro[~dentro.index.duplicated(keep="first")].copy()
    dentro = dentro.rename(columns={"id": "macrozona_id"})
    return pd.DataFrame({
        "id_punto": dentro["id_entidad"],
        "zona_piloto": dentro["zona_piloto"],
        "macrozona_id": dentro["macrozona_id"],
        "nombre_normalizado": dentro["nombre_norm"].fillna(""),
        "lat": dentro["lat"],
        "lon": dentro["lon"],
        "categoria": dentro["categoria_canonica"].fillna(""),
        "rating": "",
        "user_ratings_total": "",
        "business_status": "",
        "fuente": "F01+F02",
        "fecha_consulta": "",
    })


def main() -> int:
    if not PLACES_INTERNO.exists():
        raise SystemExit(f"Falta insumo interno: {PLACES_INTERNO}")

    mz = gpd.read_file(MACROZONAS)
    mz = mz[mz["id"].isin(ZONAS_TANDA_A)].copy()
    mz["zona_piloto"] = mz["id"].map(ZONAS_TANDA_A)

    base = cargar_base_f01f02(mz)
    qa = {
        "tanda": "a_criticas",
        "zonas": sorted(set(ZONAS_TANDA_A.values())),
        "f01f02_en_zonas_tanda_a": int(len(base)),
        "f01f02_por_zona": base.groupby("zona_piloto").size().to_dict(),
    }

    pl = pd.read_csv(PLACES_INTERNO)
    qa["places_puntos_unicos_internos"] = int(len(pl))

    g_pl_geo = gpd.GeoDataFrame(
        pl,
        geometry=gpd.points_from_xy(pl["lon"], pl["lat"]),
        crs=CRS_GEO,
    )
    dentro_pl = gpd.sjoin(g_pl_geo, mz[["id", "zona_piloto", "geometry"]],
                          how="inner", predicate="within")
    dentro_pl = dentro_pl[~dentro_pl.index.duplicated(keep="first")].copy()
    qa["places_fuera_de_macrozona_descartados"] = int(len(pl) - len(dentro_pl))
    dentro_pl = pd.DataFrame(dentro_pl.drop(columns=["geometry", "index_right"]))
    dentro_pl = dentro_pl.rename(columns={"id": "macrozona_id_real"})
    dentro_pl["zona_piloto"] = dentro_pl["zona_piloto_right"]
    dentro_pl["macrozona_id"] = dentro_pl["macrozona_id_real"]

    pilot_ids: set[str] = set()
    if PILOTO_INTERNO.exists():
        pilot = pd.read_csv(PILOTO_INTERNO, usecols=["google_place_id_interno"])
        pilot_ids = set(pilot["google_place_id_interno"].dropna().astype(str))
    dup_piloto = dentro_pl["google_place_id_interno"].astype(str).isin(pilot_ids)
    qa["places_duplicados_vs_piloto"] = int(dup_piloto.sum())

    candidatos = dentro_pl.loc[~dup_piloto].copy()
    if len(candidatos):
        g_pl = gpd.GeoDataFrame(
            candidatos,
            geometry=gpd.points_from_xy(candidatos["lon"], candidatos["lat"]),
            crs=CRS_GEO,
        ).to_crs(CRS_METRICO)
        g_base = gpd.GeoDataFrame(
            base.copy(),
            geometry=gpd.points_from_xy(base["lon"], base["lat"]),
            crs=CRS_GEO,
        ).to_crs(CRS_METRICO)
        cerca = gpd.sjoin_nearest(
            g_pl,
            g_base[["nombre_normalizado", "geometry"]],
            how="left",
            max_distance=DEDUP_NOMBRE_COMPATIBLE_M,
            distance_col="dist_m",
        )
        cerca = cerca[~cerca.index.duplicated(keep="first")]
        nombre_ok = np.array([
            nombres_compatibles(a, b)
            for a, b in zip(cerca["nombre_norm"].fillna(""),
                            cerca["nombre_normalizado"].fillna(""))
        ])
        dup_f01f02 = (cerca["dist_m"] <= DEDUP_MISMA_PARCELA_M) | (
            (cerca["dist_m"] <= DEDUP_NOMBRE_COMPATIBLE_M) & nombre_ok
        )
        nuevos = candidatos.loc[~dup_f01f02.values].copy()
        qa["places_duplicados_vs_f01f02"] = int(dup_f01f02.sum())
    else:
        nuevos = candidatos
        qa["places_duplicados_vs_f01f02"] = 0

    qa["places_nuevos_incorporados"] = int(len(nuevos))
    qa["places_nuevos_por_zona"] = nuevos.groupby("zona_piloto").size().to_dict()
    qa["places_descartes_totales"] = {
        "fuera_de_macrozona": qa["places_fuera_de_macrozona_descartados"],
        "duplicados_vs_piloto": qa["places_duplicados_vs_piloto"],
        "duplicados_vs_f01f02": qa["places_duplicados_vs_f01f02"],
    }

    nuevos_sanitizados = pd.DataFrame({
        "id_punto": nuevos["id_punto_places"],
        "zona_piloto": nuevos["zona_piloto"],
        "macrozona_id": nuevos["macrozona_id"],
        "nombre_normalizado": nuevos["nombre_norm"].fillna(""),
        "lat": nuevos["lat"],
        "lon": nuevos["lon"],
        "categoria": nuevos["categoria_google"].fillna(""),
        "rating": nuevos["rating_interno"],
        "user_ratings_total": nuevos["user_ratings_total_interno"],
        "business_status": nuevos["business_status"],
        "fuente": "google_places",
        "fecha_consulta": nuevos["fecha_consulta"],
    })
    universo = pd.concat([base, nuevos_sanitizados], ignore_index=True)
    qa["universo_ampliado_tanda_a_total"] = int(len(universo))
    qa["universo_por_zona_y_fuente"] = {
        f"{z}|{f}": int(n)
        for (z, f), n in universo.groupby(["zona_piloto", "fuente"]).size().items()
    }

    nuevos_sanitizados.to_csv(OUT_NUEVOS, index=False, encoding="utf-8")
    universo.to_csv(OUT_UNIVERSO, index=False, encoding="utf-8")
    OUT_QA.write_text(json.dumps(qa, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[universo-a] {len(universo)} puntos ({qa['f01f02_en_zonas_tanda_a']} F01+F02 + "
          f"{qa['places_nuevos_incorporados']} Places nuevos) -> {OUT_UNIVERSO}")
    print(f"[universo-a] nuevos sanitizados -> {OUT_NUEVOS}")
    print(f"[universo-a] QA -> {OUT_QA}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
