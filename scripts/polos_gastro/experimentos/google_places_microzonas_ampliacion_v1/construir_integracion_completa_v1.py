# -*- coding: utf-8 -*-
"""Integracion completa Places microzonas: piloto + Tanda A + Tanda B.

EXPERIMENTAL / no oficial. No toca Fase 25, informes oficiales, datos fuente ni
pipeline F01-F05. Lee outputs ya generados y escribe derivados versionados:

- outputs/.../google_places_microzonas_ampliacion_v1/completa_v1/
- outputs/.../google_places_microzonas_ampliacion_v1/interno/completa_v1/

La tabla interna conserva place_id solo bajo `interno/`; las salidas publicables
son sanitizadas y mantienen separadas las fuentes F01+F02, piloto, Tanda A y Tanda B.
"""
from __future__ import annotations

import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]

UNIVERSO_V1 = (ROOT / "outputs" / "polos_gastro" / "experimentos" / "pipeline_microzonas_v1"
               / "universo" / "universo_entidades_v1.csv")
MACROZONAS = (ROOT / "outputs" / "polos_gastro" / "experimentos"
              / "infraestructura_cartografica_v1" / "macrozonas_editoriales_candidatas_v1.geojson")
BASE_AMPLIACION = (ROOT / "outputs" / "polos_gastro" / "experimentos"
                   / "google_places_microzonas_ampliacion_v1")
PILOTO = ROOT / "outputs" / "polos_gastro" / "experimentos" / "google_places_microzonas_piloto"
OUT = BASE_AMPLIACION / "completa_v1"
OUT_INTERNO = BASE_AMPLIACION / "interno" / "completa_v1"

OUT_UNIVERSO = OUT / "UNIVERSO_COMPLETO_SANITIZADO.csv"
OUT_PLACES_NUEVOS = OUT / "places_nuevos_completo_sanitizado.csv"
OUT_QA = OUT / "qa_integracion_completa_v1.json"
OUT_DUP_PUBLIC = OUT / "tabla_deduplicacion_resumen.csv"
OUT_PLACES_INTERNO = OUT_INTERNO / "places_consolidados_interno.csv"
OUT_DUP_INTERNO = OUT_INTERNO / "tabla_deduplicacion_interna.csv"

CRS_GEO = "EPSG:4326"
CRS_METRICO = "EPSG:5347"
DEDUP_MISMA_PARCELA_M = 15
DEDUP_NOMBRE_COMPATIBLE_M = 40

MACROZONAS_ESCANEADAS = {
    "MZ_PALERMO_SOHO": "palermo_soho_hollywood",
    "MZ_PALERMO_HOLLYWOOD": "palermo_soho_hollywood",
    "MZ_AVENIDA_CORRIENTES": "corrientes_microcentro",
    "MZ_MICROCENTRO_Y_CENTRO": "corrientes_microcentro",
    "MZ_BELGRANO": "belgrano",
    "MZ_SAN_TELMO": "san_telmo",
    "MZ_CHACARITA": "chacarita",
    "MZ_PUERTO_MADERO": "puerto_madero",
    "MZ_COSTANERA_NORTE": "costanera_norte",
    "MZ_AVENIDA_CASEROS_BARRACAS": "caseros_barracas",
    "MZ_RECOLETA": "recoleta",
    "MZ_VILLA_CRESPO": "villa_crespo",
    "MZ_CABALLITO": "caballito",
}

PLACES_SOURCES = [
    {
        "path": PILOTO / "interno" / "places_resultados_interno.csv",
        "origen_places": "piloto",
        "orden": 1,
    },
    {
        "path": BASE_AMPLIACION / "interno" / "places_resultados_interno_a_criticas.csv",
        "origen_places": "tanda_a_criticas",
        "orden": 2,
    },
    {
        "path": BASE_AMPLIACION / "interno" / "places_resultados_interno_b_consolidacion.csv",
        "origen_places": "tanda_b_consolidacion",
        "orden": 3,
    },
    {
        "path": BASE_AMPLIACION / "interno" / "refinamientos"
                / "places_resultados_interno_refino_chacarita_saturadas_3x3.csv",
        "origen_places": "refino_chacarita_saturadas_3x3",
        "orden": 4,
        "optional": True,
    },
]


def nombres_compatibles(a: str, b: str) -> bool:
    a, b = (a or "").strip(), (b or "").strip()
    if not a or not b:
        return False
    if a in b or b in a:
        return True
    ta, tb = set(a.split()), set(b.split())
    inter = ta & tb
    return len(inter) / max(1, min(len(ta), len(tb))) >= 0.5


def cargar_macrozonas() -> gpd.GeoDataFrame:
    mz = gpd.read_file(MACROZONAS)
    mz = mz[mz["id"].isin(MACROZONAS_ESCANEADAS)].copy()
    mz["zona_piloto"] = mz["id"].map(MACROZONAS_ESCANEADAS)
    faltan = set(MACROZONAS_ESCANEADAS) - set(mz["id"])
    if faltan:
        raise SystemExit(f"Faltan macrozonas: {sorted(faltan)}")
    return mz


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
        "origen_places": "",
        "fecha_consulta": "",
    })


def cargar_places() -> pd.DataFrame:
    partes = []
    for src in PLACES_SOURCES:
        if not src["path"].exists():
            if src.get("optional"):
                continue
            raise SystemExit(f"Falta insumo Places: {src['path']}")
        df = pd.read_csv(src["path"])
        df["origen_places"] = src["origen_places"]
        df["orden_origen"] = src["orden"]
        partes.append(df)
    pl = pd.concat(partes, ignore_index=True)
    pl["google_place_id_interno"] = pl["google_place_id_interno"].astype(str)
    return pl


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    OUT_INTERNO.mkdir(parents=True, exist_ok=True)
    mz = cargar_macrozonas()
    base = cargar_base_f01f02(mz)
    pl = cargar_places()

    qa = {
        "nota": "EXPERIMENTAL / no oficial. Google Places es senal auxiliar no oficial.",
        "macrozonas_escaneadas": sorted(MACROZONAS_ESCANEADAS),
        "f01f02_en_macrozonas": int(len(base)),
        "f01f02_por_zona": base.groupby("zona_piloto").size().to_dict(),
        "places_brutos_por_origen": pl.groupby("origen_places").size().to_dict(),
    }

    # Contencion estricta: todo punto de Places se reasigna por geometria real.
    g_pl = gpd.GeoDataFrame(pl, geometry=gpd.points_from_xy(pl["lon"], pl["lat"]),
                            crs=CRS_GEO)
    dentro = gpd.sjoin(g_pl, mz[["id", "zona_piloto", "geometry"]],
                       how="inner", predicate="within")
    dentro = dentro[~dentro.index.duplicated(keep="first")].copy()
    fuera = len(pl) - len(dentro)
    qa["places_fuera_de_macrozona_descartados"] = int(fuera)
    qa["places_fuera_de_macrozona_por_origen"] = (
        pl.loc[~pl.index.isin(dentro.index)].groupby("origen_places").size().to_dict()
    )
    dentro = pd.DataFrame(dentro.drop(columns=["geometry", "index_right"]))
    dentro = dentro.rename(columns={"id": "macrozona_id_real",
                                    "zona_piloto_right": "zona_piloto_real"})
    dentro["zona_piloto"] = dentro["zona_piloto_real"]
    dentro["macrozona_id"] = dentro["macrozona_id_real"]

    # Dedup Places por place_id, conservando la primera fuente cronologica.
    dentro = dentro.sort_values(["google_place_id_interno", "orden_origen"])
    dup_place = dentro.duplicated("google_place_id_interno", keep="first")
    dup_place_rows = dentro.loc[dup_place].copy()
    unique_places = dentro.loc[~dup_place].copy()
    qa["places_duplicados_place_id_entre_tandas"] = int(dup_place.sum())
    qa["places_unicos_post_place_id"] = int(len(unique_places))

    # Dedup contra F01+F02 con reglas 15 m / 40 m + nombre compatible.
    g_places = gpd.GeoDataFrame(
        unique_places,
        geometry=gpd.points_from_xy(unique_places["lon"], unique_places["lat"]),
        crs=CRS_GEO,
    ).to_crs(CRS_METRICO)
    g_base = gpd.GeoDataFrame(
        base.copy(),
        geometry=gpd.points_from_xy(base["lon"], base["lat"]),
        crs=CRS_GEO,
    ).to_crs(CRS_METRICO)
    cerca = gpd.sjoin_nearest(
        g_places,
        g_base[["id_punto", "nombre_normalizado", "geometry"]],
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
    nuevos = unique_places.loc[~dup_f01f02.values].copy()
    dup_base = unique_places.loc[dup_f01f02.values].copy()
    qa["places_duplicados_vs_f01f02"] = int(dup_f01f02.sum())
    qa["places_nuevos_incorporados"] = int(len(nuevos))
    qa["places_nuevos_por_zona"] = nuevos.groupby("zona_piloto").size().to_dict()
    qa["places_nuevos_por_origen"] = nuevos.groupby("origen_places").size().to_dict()
    qa["places_descartes_totales"] = {
        "fuera_de_macrozona": qa["places_fuera_de_macrozona_descartados"],
        "duplicados_place_id_entre_tandas": qa["places_duplicados_place_id_entre_tandas"],
        "duplicados_vs_f01f02": qa["places_duplicados_vs_f01f02"],
    }

    nuevos_sanitizados = pd.DataFrame({
        "id_punto": [f"GPV1_{i:05d}" for i in range(1, len(nuevos) + 1)],
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
        "origen_places": nuevos["origen_places"],
        "fecha_consulta": nuevos["fecha_consulta"],
    })
    universo = pd.concat([base, nuevos_sanitizados], ignore_index=True)
    qa["universo_completo_total"] = int(len(universo))
    qa["universo_por_zona_y_fuente"] = {
        f"{z}|{f}": int(n)
        for (z, f), n in universo.groupby(["zona_piloto", "fuente"]).size().items()
    }

    dedup_public = pd.concat([
        pd.DataFrame({
            "tipo_descarte": "fuera_de_macrozona",
            "origen_places": pl.loc[~pl.index.isin(dentro.index), "origen_places"],
            "zona_original": pl.loc[~pl.index.isin(dentro.index), "zona_piloto"],
            "zona_final": "",
            "n": 1,
        }),
        pd.DataFrame({
            "tipo_descarte": "duplicado_place_id_entre_tandas",
            "origen_places": dup_place_rows["origen_places"],
            "zona_original": dup_place_rows["zona_piloto"],
            "zona_final": dup_place_rows["zona_piloto"],
            "n": 1,
        }),
        pd.DataFrame({
            "tipo_descarte": "duplicado_vs_f01f02",
            "origen_places": dup_base["origen_places"],
            "zona_original": dup_base["zona_piloto"],
            "zona_final": dup_base["zona_piloto"],
            "n": 1,
        }),
    ], ignore_index=True)
    if len(dedup_public):
        resumen_dup = (dedup_public.groupby(["tipo_descarte", "origen_places",
                                             "zona_original", "zona_final"], dropna=False)
                       ["n"].sum().reset_index())
    else:
        resumen_dup = dedup_public

    places_interno = unique_places.copy()
    places_interno["incorporado_como_nuevo"] = places_interno.index.isin(nuevos.index)
    places_interno.to_csv(OUT_PLACES_INTERNO, index=False, encoding="utf-8")
    dedup_interno = pd.DataFrame({
        "google_place_id_interno": unique_places["google_place_id_interno"],
        "origen_places": unique_places["origen_places"],
        "zona_piloto": unique_places["zona_piloto"],
        "duplicado_vs_f01f02": dup_f01f02,
        "incorporado": ~dup_f01f02,
    })
    dedup_interno.to_csv(OUT_DUP_INTERNO, index=False, encoding="utf-8")
    nuevos_sanitizados.to_csv(OUT_PLACES_NUEVOS, index=False, encoding="utf-8")
    universo.to_csv(OUT_UNIVERSO, index=False, encoding="utf-8")
    resumen_dup.to_csv(OUT_DUP_PUBLIC, index=False, encoding="utf-8")
    OUT_QA.write_text(json.dumps(qa, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[integracion] universo: {len(universo)} -> {OUT_UNIVERSO}")
    print(f"[integracion] nuevos Places: {len(nuevos_sanitizados)} -> {OUT_PLACES_NUEVOS}")
    print(f"[integracion] QA -> {OUT_QA}")
    print(f"[integracion] internos -> {OUT_INTERNO}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
