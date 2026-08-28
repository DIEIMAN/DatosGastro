from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image
from shapely.ops import unary_union


ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "outputs/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1"
COMPLETA = BASE / "completa_v1"
PAQUETE = COMPLETA / "paquete_editorial_v1"
OUT = BASE / "cartografia_editorial_v2"

POLIGONOS_REV = PAQUETE / "poligonos_todos_con_revision_v1.geojson"
TABLA_DECISION = PAQUETE / "tabla_decision_editorial_microzonas_v1.csv"
MICROCLUSTERS = COMPLETA / "MICROCLUSTERS_COMPLETA_V1.geojson"
UNIVERSO = COMPLETA / "UNIVERSO_COMPLETO_SANITIZADO.csv"
POLIGONOS_BASE = COMPLETA / "POLIGONOS_MICROZONAS_COMPLETA_V1.geojson"

CALLEJERO = ROOT / "outputs/polos_gastro/fase15_mapas_callejeros_v3/assets/callejero_gcba_2026_06_02.geojson"
BARRIOS = ROOT / "PolosGastro/cartografia/barrios_caba.geojson"
COMUNAS = ROOT / "PolosGastro/cartografia/comunas_caba.geojson"

CRS_METERS = "EPSG:5347"


MAP_FILES = {
    "general": "mapa_general_simplificado_v0.png",
    "palermo": "mapa_palermo_simplificado_v0.png",
    "san_telmo": "mapa_san_telmo_simplificado_v0.png",
    "belgrano": "mapa_belgrano_simplificado_v0.png",
    "corrientes_microcentro": "mapa_corrientes_microcentro_simplificado_v0.png",
    "caballito": "mapa_caballito_simplificado_v0.png",
    "recoleta": "mapa_recoleta_simplificado_v0.png",
    "villa_crespo": "mapa_villa_crespo_simplificado_v0.png",
    "puerto_madero": "mapa_puerto_madero_simplificado_v0.png",
    "chacarita": "mapa_chacarita_simplificado_v0.png",
    "costanera_norte": "mapa_costanera_norte_simplificado_v0.png",
    "caseros_barracas": "mapa_caseros_barracas_simplificado_v0.png",
}


MACRO_LABELS = {
    "MZ_AVENIDA_CASEROS_BARRACAS": "Av. Caseros / Barracas",
    "MZ_AVENIDA_CORRIENTES": "Av. Corrientes",
    "MZ_BELGRANO": "Belgrano",
    "MZ_CABALLITO": "Caballito",
    "MZ_CHACARITA": "Chacarita",
    "MZ_COSTANERA_NORTE": "Costanera Norte",
    "MZ_MICROCENTRO_Y_CENTRO": "Microcentro y Centro",
    "MZ_PALERMO_HOLLYWOOD": "Palermo Hollywood",
    "MZ_PALERMO_SOHO": "Palermo Soho",
    "MZ_PUERTO_MADERO": "Puerto Madero",
    "MZ_RECOLETA": "Recoleta",
    "MZ_SAN_TELMO": "San Telmo",
    "MZ_VILLA_CRESPO": "Villa Crespo",
}

PROBLEM_MACROZONES = {
    "MZ_AVENIDA_CASEROS_BARRACAS",
    "MZ_AVENIDA_CORRIENTES",
    "MZ_BELGRANO",
    "MZ_CABALLITO",
    "MZ_COSTANERA_NORTE",
    "MZ_MICROCENTRO_Y_CENTRO",
}

PALETTE = {
    "CONSERVAR_COMO_MICROZONA": "#1b7f79",
    "FUSIONAR_EN_CORREDOR": "#2f5597",
    "FUSIONAR_EN_NUCLEO": "#397367",
    "REDIBUJAR_MANUAL": "#c77d00",
    "DEJAR_COMO_SENAL_EXPLORATORIA": "#8a8f98",
}


def slug(value: str) -> str:
    value = value.upper()
    value = re.sub(r"[^A-Z0-9]+", "_", value)
    return value.strip("_")


def priority_rank(value: str) -> int:
    return {"BAJA": 0, "MEDIA": 1, "ALTA": 2}.get(str(value), 0)


def max_priority(values: pd.Series) -> str:
    order = ["BAJA", "MEDIA", "ALTA"]
    return order[max(priority_rank(v) for v in values.dropna())] if len(values.dropna()) else "MEDIA"


def group_common(row: pd.Series, group: str, name: str, kind: str, reason: str) -> dict[str, str]:
    cat = row["categoria_revision"]
    macro = row["macrozona_id"]
    if cat == "DESCARTAR":
        action = "EXCLUIR_DEL_MAPA_EDITORIAL"
        keep = "NO"
        priority = "ALTA"
    elif cat == "REVISAR UNIVERSO":
        action = "DEJAR_COMO_SENAL_EXPLORATORIA"
        keep = "SI_COMO_SENAL"
        priority = "ALTA"
    elif cat == "REVISAR CORTE":
        action = "REDIBUJAR_MANUAL"
        keep = "SI"
        priority = "ALTA" if macro in PROBLEM_MACROZONES else row["prioridad_revision"]
    elif cat == "REVISAR FUSION":
        action = "FUSIONAR_EN_CORREDOR" if kind == "corredor" else "FUSIONAR_EN_NUCLEO"
        keep = "SI"
        priority = "ALTA" if macro in PROBLEM_MACROZONES else row["prioridad_revision"]
    else:
        action = "FUSIONAR_EN_CORREDOR" if kind == "corredor" else "FUSIONAR_EN_NUCLEO"
        keep = "SI"
        priority = row["prioridad_revision"]
    return {
        "grupo_editorial_v0": group,
        "nombre_orientativo": name,
        "tipo_grupo": kind,
        "accion_v2": action,
        "motivo_agrupamiento": reason,
        "prioridad_revision": priority,
        "mantener_en_mapa": keep,
        "observaciones": "Nombre y envolvente orientativos. No usar como limite final institucional.",
    }


def assign_non_excluded_group(row: pd.Series) -> dict[str, str]:
    macro = row["macrozona_id"]
    lon = row["centroid_lon"]
    lat = row["centroid_lat"]
    cat = row["categoria_revision"]

    if cat == "DESCARTAR":
        group = f"EXCLUIR_{slug(row['microzona_id'])}"
        return group_common(
            row,
            group,
            f"Excluir por ahora / {MACRO_LABELS.get(macro, macro)}",
            "exclusion",
            "La revision editorial previa marco el poligono como DESCARTAR.",
        )

    if cat == "REVISAR UNIVERSO":
        group = f"{slug(MACRO_LABELS.get(macro, macro))}_SENAL_EXPLORATORIA"
        return group_common(
            row,
            group,
            f"{MACRO_LABELS.get(macro, macro)} / senal exploratoria",
            "senal_exploratoria",
            "Se conserva como senal auxiliar para revision, sin pasar a capa firme.",
        )

    if macro == "MZ_AVENIDA_CORRIENTES":
        if lon < -58.411:
            return group_common(row, "CORRIENTES_OESTE_ABASTO_ONCE", "Corrientes oeste / Abasto-Once", "corredor", "Fusion por continuidad longitudinal sobre el eje Corrientes.")
        if lon < -58.400:
            return group_common(row, "CORRIENTES_CENTRO_TEATRAL", "Corrientes centro / teatral", "corredor", "Reduce cortes KMeans artificiales en un mismo corredor teatral/comercial.")
        if lon < -58.386:
            return group_common(row, "CORRIENTES_TRIBUNALES_OBELISCO", "Corrientes / Tribunales-Obelisco", "corredor", "Agrupa piezas vecinas con alta continuidad urbana.")
        return group_common(row, "CORRIENTES_ESTE_CENTRO", "Corrientes este / Centro", "corredor", "Fusion por continuidad de eje y lectura cartografica.")

    if macro == "MZ_MICROCENTRO_Y_CENTRO":
        if lon > -58.382 and lat > -34.604:
            return group_common(row, "FLORIDA_LAVALLE_MICROCENTRO", "Florida-Lavalle / Microcentro", "nucleo", "Agrupa piezas cercanas del nucleo peatonal y comercial.")
        if lon > -58.382:
            return group_common(row, "MICROCENTRO_LABORAL_ADMINISTRATIVO", "Microcentro laboral / centro administrativo", "nucleo", "Agrupa piezas de centro administrativo que requieren decision humana.")
        return group_common(row, "CENTRO_TRIBUNALES_ADMINISTRATIVO", "Centro administrativo / Tribunales", "nucleo", "Fusion orientativa de piezas contiguas al borde oeste del centro.")

    if macro == "MZ_BELGRANO":
        if lon > -58.449 and lat <= -34.560:
            return group_common(row, "BELGRANO_BARRIO_CHINO_BARRANCAS", "Barrio Chino / Barrancas", "nucleo", "Agrupa piezas de Belgrano este con lectura urbana reconocible.")
        if lon > -58.449:
            return group_common(row, "BELGRANO_BAJO", "Bajo Belgrano", "nucleo", "Separa piezas del borde este para revision humana.")
        if lon <= -58.457 and lat <= -34.560:
            return group_common(row, "BELGRANO_CABILDO_JURAMENTO", "Cabildo / Juramento", "nucleo", "Reduce cortes KMeans en torno al eje Cabildo-Juramento.")
        return group_common(row, "BELGRANO_NORTE_OESTE", "Belgrano norte / oeste", "nucleo", "Agrupa subpiezas occidentales para evitar sobreparticion.")

    if macro == "MZ_CABALLITO":
        if lon <= -58.445 and lat <= -34.612:
            return group_common(row, "CABALLITO_PEDRO_GOYENA", "Pedro Goyena", "nucleo", "Agrupa piezas al sur con lectura de nucleo gastronomico.")
        if lon >= -58.446 and lat <= -34.616:
            return group_common(row, "CABALLITO_ACOYTE_CENTRO", "Acoyte / Caballito centro", "nucleo", "Reduce sobreparticion del nucleo central.")
        if lon >= -58.446:
            return group_common(row, "CABALLITO_PRIMERA_JUNTA_RIVADAVIA", "Primera Junta / Rivadavia", "corredor", "Agrupa piezas del corredor Rivadavia/Primera Junta.")
        if lat >= -34.616:
            return group_common(row, "CABALLITO_AVELLANEDA_COMERCIAL", "Avellaneda / zona comercial", "corredor", "Agrupa piezas norte para lectura comercial.")
        return group_common(row, "CABALLITO_CENTRO_RIVADAVIA", "Caballito centro / Rivadavia", "corredor", "Fusion intermedia para revision humana.")

    if macro == "MZ_PALERMO_SOHO":
        if lon <= -58.429:
            return group_common(row, "PALERMO_PLAZA_SERRANO_ARMENIA", "Plaza Serrano / Armenia", "nucleo", "Agrupa subnucleos Soho con continuidad peatonal.")
        if lat <= -34.586:
            return group_common(row, "PALERMO_HONDURAS_ARMENIA", "Honduras / Armenia", "corredor", "Fusion orientativa sobre eje Honduras y entorno Armenia.")
        return group_common(row, "PALERMO_SOHO_ESTE", "Palermo Soho este", "nucleo", "Separa borde oriental para revision.")

    if macro == "MZ_PALERMO_HOLLYWOOD":
        if lon <= -58.436:
            return group_common(row, "PALERMO_HOLLYWOOD_FITZ_ROY", "Palermo Hollywood / Fitz Roy", "nucleo", "Agrupa piezas con continuidad clara en Hollywood.")
        if lat <= -34.582:
            return group_common(row, "PALERMO_HOLLYWOOD_NORTE", "Palermo Hollywood norte", "nucleo", "Separa borde norte para lectura mas clara.")
        return group_common(row, "PALERMO_HOLLYWOOD_ESTE", "Palermo Hollywood este", "nucleo", "Agrupa piezas orientales cercanas.")

    if macro == "MZ_SAN_TELMO":
        if lat <= -34.621:
            return group_common(row, "SAN_TELMO_SUR", "San Telmo sur", "nucleo", "Agrupa piezas del eje sur sin convertirlas en limite final.")
        if lon <= -58.372:
            return group_common(row, "SAN_TELMO_DEFENSA_DORREGO", "Defensa / Plaza Dorrego", "nucleo", "Agrupa el nucleo historico mas defendible.")
        return group_common(row, "SAN_TELMO_MERCADO_NORTE", "Mercado de San Telmo / nucleo norte", "nucleo", "Agrupa piezas cercanas al mercado y al borde norte.")

    if macro == "MZ_PUERTO_MADERO":
        if lat <= -34.616:
            return group_common(row, "PUERTO_MADERO_SUR_DIQUES", "Puerto Madero sur / diques", "corredor", "Agrupa piezas del frente sur con revision de fusion.")
        if lat <= -34.609:
            return group_common(row, "PUERTO_MADERO_CENTRO_FRENTES", "Puerto Madero centro / frentes gastronomicos", "corredor", "Agrupa frentes gastronomicos consolidados.")
        return group_common(row, "PUERTO_MADERO_NORTE_FRENTE_OESTE", "Puerto Madero norte / frente oeste", "corredor", "Agrupa piezas norte para revision de continuidad.")

    if macro == "MZ_RECOLETA":
        if lon <= -58.398:
            return group_common(row, "RECOLETA_OESTE_ALTO_PALERMO", "Recoleta oeste / Alto Palermo", "nucleo", "Agrupa piezas occidentales con lectura territorial clara.")
        if lon <= -58.392:
            return group_common(row, "RECOLETA_CENTRO", "Recoleta centro", "nucleo", "Fusion intermedia de piezas vecinas.")
        return group_common(row, "RECOLETA_ESTE_CULTURAL", "Recoleta este / cultural", "nucleo", "Agrupa piezas orientales para mapa de revision.")

    if macro == "MZ_VILLA_CRESPO":
        if lon <= -58.444:
            return group_common(row, "VILLA_CRESPO_OESTE_CORRIENTES", "Villa Crespo oeste / Corrientes", "corredor", "Agrupa piezas occidentales del eje Corrientes.")
        if lon >= -58.436:
            return group_common(row, "VILLA_CRESPO_ESTE_PALERMO_LIMITE", "Villa Crespo este / limite Palermo", "nucleo", "Agrupa piezas al borde Palermo para revision.")
        return group_common(row, "VILLA_CRESPO_CENTRO_SCALABRINI", "Villa Crespo centro / Scalabrini", "nucleo", "Reduce cortes en el nucleo central.")

    if macro == "MZ_CHACARITA":
        if lat <= -34.589:
            return group_common(row, "CHACARITA_SUR", "Chacarita sur", "nucleo", "Agrupa piezas sur y evita lectura de microcortes.")
        if lat <= -34.584:
            return group_common(row, "CHACARITA_CENTRO", "Chacarita centro", "nucleo", "Agrupa piezas centrales derivadas del refuerzo Places.")
        return group_common(row, "CHACARITA_NORTE", "Chacarita norte", "nucleo", "Agrupa piezas norte para revision humana.")

    if macro == "MZ_COSTANERA_NORTE":
        if lon <= -58.420:
            return group_common(row, "COSTANERA_NORTE_NORTE_SENAL", "Costanera Norte norte / senal exploratoria", "senal_exploratoria", "Zona debil: conservar como senal, no como capa firme.")
        return group_common(row, "COSTANERA_NORTE_CENTRO_SENAL", "Costanera Norte centro / senal exploratoria", "senal_exploratoria", "Zona debil: conservar como senal, no como capa firme.")

    if macro == "MZ_AVENIDA_CASEROS_BARRACAS":
        if lon <= -58.382:
            return group_common(row, "CASEROS_BARRACAS_NUCLEO_DEFENDIBLE", "Caseros / Barracas oeste", "corredor", "Se conserva solo el nucleo mas defendible.")
        return group_common(row, "CASEROS_BARRACAS_SENAL_EXPLORATORIA", "Caseros / Barracas senal exploratoria", "senal_exploratoria", "Zona debil: mantener para decision humana, no como firme.")

    return group_common(
        row,
        f"{slug(MACRO_LABELS.get(macro, macro))}_GRUPO_UNICO",
        MACRO_LABELS.get(macro, macro),
        "nucleo",
        "Agrupamiento unico por macrozona.",
    )


def load_inputs() -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame, pd.DataFrame]:
    missing = [p for p in [POLIGONOS_REV, TABLA_DECISION, MICROCLUSTERS, UNIVERSO, POLIGONOS_BASE] if not p.exists()]
    if missing:
        raise FileNotFoundError("Faltan insumos: " + ", ".join(str(p) for p in missing))

    pol = gpd.read_file(POLIGONOS_REV)
    points = gpd.read_file(MICROCLUSTERS)
    decision = pd.read_csv(TABLA_DECISION)

    pol_m = pol.to_crs(CRS_METERS)
    cent = pol_m.geometry.centroid.to_crs(pol.crs)
    pol["centroid_lon"] = cent.x
    pol["centroid_lat"] = cent.y
    return pol, points, decision


def build_grouping_table(pol: gpd.GeoDataFrame) -> pd.DataFrame:
    records = []
    for _, row in pol.iterrows():
        group = assign_non_excluded_group(row)
        records.append(
            {
                "macrozona": row["macrozona_id"],
                "microzona_id_original": row["microzona_id"],
                "categoria_revision_original": row["categoria_revision"],
                "accion_editorial_original": row["accion_editorial"],
                **group,
            }
        )
    table = pd.DataFrame(records)

    group_sizes = table.groupby("grupo_editorial_v0").size().to_dict()
    for idx, row in table.iterrows():
        if row["accion_v2"] in {"FUSIONAR_EN_CORREDOR", "FUSIONAR_EN_NUCLEO"} and group_sizes[row["grupo_editorial_v0"]] == 1:
            table.loc[idx, "accion_v2"] = "CONSERVAR_COMO_MICROZONA"
        if row["tipo_grupo"] == "senal_exploratoria":
            table.loc[idx, "accion_v2"] = "DEJAR_COMO_SENAL_EXPLORATORIA"
            table.loc[idx, "mantener_en_mapa"] = "SI_COMO_SENAL"
            table.loc[idx, "prioridad_revision"] = "ALTA"
    return table


def simplify_group_geometry(geoms, action: str):
    union = unary_union(list(geoms))
    if union.is_empty:
        return union
    geom = union
    if action in {"FUSIONAR_EN_CORREDOR", "FUSIONAR_EN_NUCLEO", "REDIBUJAR_MANUAL"}:
        geom = union.convex_hull
    geom = geom.buffer(25).buffer(-25).simplify(25, preserve_topology=True)
    if not geom.is_valid:
        geom = geom.buffer(0)
    return geom


def build_simplified_layer(pol: gpd.GeoDataFrame, table: pd.DataFrame) -> gpd.GeoDataFrame:
    enriched = pol.merge(
        table,
        left_on="microzona_id",
        right_on="microzona_id_original",
        how="left",
        validate="one_to_one",
        suffixes=("", "_v0"),
    )
    kept = enriched[enriched["mantener_en_mapa"] != "NO"].copy()
    kept_m = kept.to_crs(CRS_METERS)

    records = []
    for group, sub in kept_m.groupby("grupo_editorial_v0", sort=True):
        action_counts = Counter(sub["accion_v2"])
        action = action_counts.most_common(1)[0][0]
        geom = simplify_group_geometry(sub.geometry, action)
        sub_wgs = sub.to_crs("EPSG:4326")
        f01 = int(sub_wgs["cantidad_f01_f02"].fillna(0).sum()) if "cantidad_f01_f02" in sub_wgs else 0
        places = int(sub_wgs["cantidad_places"].fillna(0).sum()) if "cantidad_places" in sub_wgs else 0
        total = int(sub_wgs["cantidad_entidades"].fillna(0).sum()) if "cantidad_entidades" in sub_wgs else int(sub_wgs["n_puntos"].fillna(0).sum())
        pct_places = round((places / total) * 100, 1) if total else 0.0
        records.append(
            {
                "grupo_editorial_v0": group,
                "nombre_orientativo": sub_wgs["nombre_orientativo"].iloc[0],
                "tipo_grupo": sub_wgs["tipo_grupo"].iloc[0],
                "accion_v2": action,
                "prioridad_revision": max_priority(sub_wgs["prioridad_revision_v0"]),
                "macrozona": "; ".join(sorted(sub_wgs["macrozona_id"].astype(str).unique())),
                "n_poligonos_originales": int(len(sub_wgs)),
                "microzonas_originales": "; ".join(sorted(sub_wgs["microzona_id"].astype(str))),
                "categorias_originales": "; ".join(f"{k}:{v}" for k, v in sorted(Counter(sub_wgs["categoria_revision"]).items())),
                "entidades_total": total,
                "cantidad_f01_f02": f01,
                "cantidad_places": places,
                "porcentaje_places": pct_places,
                "metodo_geometria": "envolvente_simplificada_derivada_de_poligonos_originales_v0",
                "estado": "EXPERIMENTAL_NO_OFICIAL",
                "nota_uso": "Insumo para revision humana. No usar como limite institucional final.",
                "geometry": geom,
            }
        )
    out = gpd.GeoDataFrame(records, geometry="geometry", crs=CRS_METERS).to_crs("EPSG:4326")
    return out


def build_points_layer(points: gpd.GeoDataFrame, table: pd.DataFrame) -> gpd.GeoDataFrame:
    join = table[
        [
            "microzona_id_original",
            "grupo_editorial_v0",
            "nombre_orientativo",
            "tipo_grupo",
            "accion_v2",
            "mantener_en_mapa",
        ]
    ].copy()
    pts = points.merge(join, left_on="cluster_final", right_on="microzona_id_original", how="left")
    missing_group = pts["grupo_editorial_v0"].isna()
    pts.loc[missing_group, "grupo_editorial_v0"] = "SIN_GRUPO_EDITORIAL_V0"
    pts.loc[missing_group, "nombre_orientativo"] = "Sin grupo editorial v0 / ruido"
    pts.loc[missing_group, "tipo_grupo"] = "ruido_o_fuera_poligono"
    pts.loc[missing_group, "accion_v2"] = "EXCLUIR_DEL_MAPA_EDITORIAL"
    pts.loc[missing_group, "mantener_en_mapa"] = "NO"
    cols = [
        "fuente",
        "macrozona_id",
        "cluster_final",
        "grupo_editorial_v0",
        "nombre_orientativo",
        "tipo_grupo",
        "accion_v2",
        "mantener_en_mapa",
        "origen_places",
        "categoria",
        "geometry",
    ]
    pts = pts[cols].rename(columns={"cluster_final": "cluster_original"}).copy()
    pts["estado"] = "EXPERIMENTAL_NO_OFICIAL"
    return gpd.GeoDataFrame(pts, geometry="geometry", crs=points.crs)


def detect_reference_layers() -> pd.DataFrame:
    candidates = [
        ("barrios", BARRIOS),
        ("comunas", COMUNAS),
        ("callejero", CALLEJERO),
        ("barrios_raw", ROOT / "data/raw/geo_barrios.geojson"),
        ("comunas_raw", ROOT / "data/raw/geo_comunas.geojson"),
    ]
    rows = []
    for kind, path in candidates:
        if not path.exists():
            continue
        try:
            gdf = gpd.read_file(path)
            rows.append(
                {
                    "tipo": kind,
                    "ruta": str(path.relative_to(ROOT)),
                    "registros": len(gdf),
                    "crs": str(gdf.crs),
                    "geometria": ", ".join(sorted(gdf.geometry.geom_type.unique())),
                    "uso_v2": "usada" if path in {BARRIOS, COMUNAS, CALLEJERO} else "detectada_no_usada",
                }
            )
        except Exception as exc:  # pragma: no cover - diagnostic only
            rows.append({"tipo": kind, "ruta": str(path.relative_to(ROOT)), "error": str(exc), "uso_v2": "no_usable"})
    return pd.DataFrame(rows)


def load_reference_layers():
    barrios = gpd.read_file(BARRIOS) if BARRIOS.exists() else None
    comunas = gpd.read_file(COMUNAS) if COMUNAS.exists() else None
    streets = None
    if CALLEJERO.exists():
        streets = gpd.read_file(CALLEJERO)
        if "tipo_c" in streets.columns:
            streets = streets[streets["tipo_c"].astype(str).str.upper().isin(["AVENIDA", "BOULEVARD", "AUTOPISTA", "CALLE PEATONAL"])].copy()
        if "red_jerarq" in streets.columns:
            main = streets["red_jerarq"].astype(str).str.contains("TRONCAL|PRINCIPAL|COMPLEMENTARIA", case=False, na=False)
            streets = streets[main | streets["tipo_c"].astype(str).str.upper().isin(["AVENIDA", "AUTOPISTA"])].copy()
    return barrios, comunas, streets


def bbox_filter(gdf: gpd.GeoDataFrame | None, bounds: tuple[float, float, float, float], pad: float = 0.005):
    if gdf is None or gdf.empty:
        return None
    minx, miny, maxx, maxy = bounds
    return gdf.cx[minx - pad : maxx + pad, miny - pad : maxy + pad].copy()


def plot_map(
    groups: gpd.GeoDataFrame,
    points: gpd.GeoDataFrame,
    pol: gpd.GeoDataFrame,
    map_key: str,
    macrozones: list[str] | None,
    title: str,
    barrios: gpd.GeoDataFrame | None,
    comunas: gpd.GeoDataFrame | None,
    streets: gpd.GeoDataFrame | None,
) -> Path:
    if macrozones is None:
        g = groups.copy()
        p = points[points["mantener_en_mapa"] != "NO"].copy()
        macro_outline = pol.copy()
    else:
        g = groups[groups["macrozona"].apply(lambda x: any(mz in str(x) for mz in macrozones))].copy()
        p = points[(points["mantener_en_mapa"] != "NO") & (points["macrozona_id"].isin(macrozones))].copy()
        macro_outline = pol[pol["macrozona_id"].isin(macrozones)].copy()

    if g.empty:
        raise ValueError(f"Mapa sin grupos para {map_key}")

    bounds = g.total_bounds
    width = 13 if map_key == "general" else 10
    height = 10 if map_key == "general" else 8
    fig, ax = plt.subplots(figsize=(width, height), dpi=220)
    fig.patch.set_facecolor("#f8f7f2")
    ax.set_facecolor("#f8f7f2")

    barrios_sub = bbox_filter(barrios, bounds, pad=0.01)
    comunas_sub = bbox_filter(comunas, bounds, pad=0.01)
    streets_sub = bbox_filter(streets, bounds, pad=0.01)

    if barrios_sub is not None and not barrios_sub.empty:
        barrios_sub.boundary.plot(ax=ax, color="#d4d0c7", linewidth=0.45, alpha=0.75, zorder=1)
    if comunas_sub is not None and not comunas_sub.empty:
        comunas_sub.boundary.plot(ax=ax, color="#b8b2a7", linewidth=0.8, alpha=0.6, zorder=2)
    if streets_sub is not None and not streets_sub.empty:
        streets_sub.plot(ax=ax, color="#b7b0a5", linewidth=0.35, alpha=0.65, zorder=3)

    if not macro_outline.empty:
        macro_outline.dissolve(by="macrozona_id").boundary.plot(ax=ax, color="#4f555c", linewidth=0.7, alpha=0.55, zorder=4)

    if not p.empty:
        p[p["fuente"].astype(str).eq("F01+F02")].plot(ax=ax, color="#2d5f7f", markersize=5, alpha=0.22, zorder=5)
        p[p["fuente"].astype(str).eq("google_places")].plot(ax=ax, color="#c77d00", markersize=4, alpha=0.16, zorder=5)

    for action, sub in g.groupby("accion_v2"):
        color = PALETTE.get(action, "#555555")
        sub.plot(ax=ax, facecolor=color, edgecolor="#1f2933", linewidth=1.3, alpha=0.30, zorder=6)
        sub.boundary.plot(ax=ax, color="#1f2933", linewidth=1.1, alpha=0.82, zorder=7)

    label_g = g.to_crs(CRS_METERS)
    reps = label_g.representative_point().to_crs("EPSG:4326")
    for (_, row), pt in zip(g.iterrows(), reps):
        label = str(row["nombre_orientativo"])
        ax.text(
            pt.x,
            pt.y,
            label,
            ha="center",
            va="center",
            fontsize=8.5 if map_key != "general" else 6.3,
            weight="bold",
            color="#17202a",
            bbox={"facecolor": "#fffaf0", "edgecolor": "#8c877d", "linewidth": 0.35, "alpha": 0.88, "boxstyle": "round,pad=0.25"},
            zorder=8,
        )

    minx, miny, maxx, maxy = bounds
    dx = max((maxx - minx) * 0.12, 0.004)
    dy = max((maxy - miny) * 0.12, 0.004)
    ax.set_xlim(minx - dx, maxx + dx)
    ax.set_ylim(miny - dy, maxy + dy)
    ax.set_title(title, loc="left", fontsize=14, weight="bold", color="#17202a", pad=10)
    ax.text(
        0.01,
        0.01,
        "Experimental / no oficial. Puntos con baja opacidad. Limites orientativos derivados de poligonos previos.",
        transform=ax.transAxes,
        fontsize=7,
        color="#4f555c",
        ha="left",
        va="bottom",
    )
    ax.set_axis_off()
    fig.tight_layout()
    out = OUT / MAP_FILES[map_key]
    fig.savefig(out, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    return out


def png_nonblank(path: Path) -> dict[str, object]:
    img = Image.open(path).convert("RGB")
    colors = img.getcolors(maxcolors=10_000_000)
    unique = len(colors) if colors is not None else 10_000_000
    bbox = img.getbbox()
    return {"archivo": path.name, "ancho": img.width, "alto": img.height, "colores_unicos": unique, "no_blanco": bool(bbox and unique > 10)}


def write_markdown(
    original_count: int,
    group_count: int,
    excluded_count: int,
    map_paths: list[Path],
    table: pd.DataFrame,
    groups: gpd.GeoDataFrame,
    reference_layers: pd.DataFrame,
) -> None:
    action_counts = groups["accion_v2"].value_counts().to_dict()
    strong = [
        "Palermo Soho/Hollywood",
        "San Telmo",
        "Recoleta",
        "Villa Crespo",
        "Chacarita",
    ]
    weak = [
        "Costanera Norte",
        "Av. Caseros/Barracas",
        "partes de Puerto Madero",
        "cortes de Corrientes/Microcentro, Belgrano y Caballito",
    ]
    resumen = f"""# Resumen cartografia editorial v2

Estado: EXPERIMENTAL / NO OFICIAL.

## Sintesis

Los 163 poligonos algoritimicos de `completa_v1` se tratan como insumo interno de QA. No son una capa final porque presentan demasiadas piezas, cortes KMeans artificiales, geometrias irregulares y baja legibilidad para revision de oficina.

Esta tanda crea una capa editorial simplificada v0 para ordenar la decision humana. La capa reduce `163` poligonos originales a `{group_count}` grupos editoriales visibles. Se excluyen `{excluded_count}` poligonos marcados como `DESCARTAR`.

## Que se fusiono

- Corredores con continuidad urbana, especialmente Corrientes, Caballito/Rivadavia y frentes de Puerto Madero.
- Nucleos con varios cortes internos, especialmente Belgrano, Palermo, Recoleta, San Telmo, Villa Crespo y Chacarita.
- Piezas aprobables con observaciones cuando la lectura territorial era una sola unidad revisable.

## Que se excluyo

- Poligonos con categoria original `DESCARTAR`.
- No se borran del insumo base: solo quedan fuera del mapa editorial simplificado.

## Que queda como senal exploratoria

- `REVISAR UNIVERSO`, especialmente Costanera Norte, Av. Caseros/Barracas y piezas aisladas de Puerto Madero/Caballito.
- Estas piezas no deben presentarse como microzonas firmes.

## Zonas mas solidas

{chr(10).join(f'- {z}' for z in strong)}

## Zonas debiles o con decision pendiente

{chr(10).join(f'- {z}' for z in weak)}

## Decisiones humanas necesarias

- Validar si los nombres orientativos son adecuados.
- Redibujar limites finos sobre calles reales antes de cualquier uso institucional.
- Confirmar fusiones en Corrientes/Microcentro, Belgrano y Caballito.
- Decidir si las senales exploratorias se excluyen o se mantienen como anexo tecnico.
- No volver a consultar APIs para resolver problemas de cartografia editorial: el problema principal es de lectura urbana y decision institucional, no de falta de puntos.

## Conteos

- Poligonos originales procesados: {original_count}
- Grupos editoriales visibles v0: {group_count}
- Poligonos excluidos del mapa editorial: {excluded_count}
- Mapas creados: {len(map_paths)}
- Acciones v2 en capa visible: {json.dumps(action_counts, ensure_ascii=False)}
"""
    (OUT / "RESUMEN_CARTOGRAFIA_EDITORIAL_V2.md").write_text(resumen, encoding="utf-8")

    refs = "\n".join(f"- `{row.ruta}` ({row.tipo}, {row.registros} registros, {row.uso_v2})" for row in reference_layers.itertuples())
    handoff = f"""# Handoff cartografia editorial v2

Estado: EXPERIMENTAL / NO OFICIAL.

## Mirar primero

1. `mapa_general_simplificado_v0.png`
2. `mapa_corrientes_microcentro_simplificado_v0.png`
3. `mapa_belgrano_simplificado_v0.png`
4. `mapa_caballito_simplificado_v0.png`
5. `mapa_costanera_norte_simplificado_v0.png`
6. `mapa_caseros_barracas_simplificado_v0.png`

## Capas para abrir en QGIS

- `poligonos_editoriales_simplificados_v0.geojson`: capa principal de trabajo editorial v0.
- `puntos_evidencia_microzonas_v0.geojson`: puntos de evidencia sin nombres comerciales ni IDs privados de API.
- `tabla_agrupamiento_editorial_v0.csv`: trazabilidad entre cada poligono original y su grupo editorial candidato.

## Que NO usar como final

- No usar `poligonos_editoriales_simplificados_v0.geojson` como delimitacion institucional final.
- No usar los 163 poligonos originales como mapa editorial.
- No presentar las senales exploratorias como microzonas aprobadas.

## Decisiones para Diego

- Confirmar fusiones propuestas por macrozona.
- Decidir nombres orientativos a mantener o reemplazar.
- Separar lo que pasa a borrador institucional de lo que queda como anexo tecnico.
- Definir si Costanera Norte y Caseros/Barracas quedan fuera del mapa principal o como senal exploratoria.

## Siguiente paso hacia version institucional

1. Abrir la capa simplificada en QGIS con calles y barrios.
2. Redibujar limites finos sobre ejes urbanos reconocibles.
3. Congelar una tabla de decisiones humanas por grupo.
4. Crear una version `v1` institucional solo despues de esa revision.

## Capas locales de referencia detectadas

{refs}

## Reproducibilidad

Generado con:

`python scripts/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/preparar_cartografia_editorial_v2.py`
"""
    (OUT / "HANDOFF_CARTOGRAFIA_EDITORIAL_V2.md").write_text(handoff, encoding="utf-8")


def run() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    pol, points, _decision = load_inputs()
    if len(pol) != 163:
        raise ValueError(f"Se esperaban 163 poligonos, se leyeron {len(pol)}")

    reference_layers = detect_reference_layers()
    reference_layers.to_csv(OUT / "capas_referencia_locales_detectadas_v0.csv", index=False, encoding="utf-8")

    table = build_grouping_table(pol)
    table.to_csv(OUT / "tabla_agrupamiento_editorial_v0.csv", index=False, encoding="utf-8")

    groups = build_simplified_layer(pol, table)
    groups.to_file(OUT / "poligonos_editoriales_simplificados_v0.geojson", driver="GeoJSON")

    evidence = build_points_layer(points, table)
    evidence.to_file(OUT / "puntos_evidencia_microzonas_v0.geojson", driver="GeoJSON")

    barrios, comunas, streets = load_reference_layers()
    map_specs = [
        ("general", None, "Microzonas gastronomicas - capa editorial simplificada v0"),
        ("palermo", ["MZ_PALERMO_SOHO", "MZ_PALERMO_HOLLYWOOD"], "Palermo - simplificado v0"),
        ("san_telmo", ["MZ_SAN_TELMO"], "San Telmo - simplificado v0"),
        ("belgrano", ["MZ_BELGRANO"], "Belgrano - simplificado v0"),
        ("corrientes_microcentro", ["MZ_AVENIDA_CORRIENTES", "MZ_MICROCENTRO_Y_CENTRO"], "Corrientes / Microcentro - simplificado v0"),
        ("caballito", ["MZ_CABALLITO"], "Caballito - simplificado v0"),
        ("recoleta", ["MZ_RECOLETA"], "Recoleta - simplificado v0"),
        ("villa_crespo", ["MZ_VILLA_CRESPO"], "Villa Crespo - simplificado v0"),
        ("puerto_madero", ["MZ_PUERTO_MADERO"], "Puerto Madero - simplificado v0"),
        ("chacarita", ["MZ_CHACARITA"], "Chacarita - simplificado v0"),
        ("costanera_norte", ["MZ_COSTANERA_NORTE"], "Costanera Norte - simplificado v0"),
        ("caseros_barracas", ["MZ_AVENIDA_CASEROS_BARRACAS"], "Av. Caseros / Barracas - simplificado v0"),
    ]
    map_paths = [
        plot_map(groups, evidence, pol, key, macrozones, title, barrios, comunas, streets)
        for key, macrozones, title in map_specs
    ]

    png_qa = pd.DataFrame([png_nonblank(p) for p in map_paths])
    png_qa.to_csv(OUT / "qa_png_no_blanco_v0.csv", index=False, encoding="utf-8")
    if not png_qa["no_blanco"].all():
        bad = png_qa.loc[~png_qa["no_blanco"], "archivo"].tolist()
        raise RuntimeError("PNG posiblemente en blanco: " + ", ".join(bad))

    excluded_count = int((table["mantener_en_mapa"] == "NO").sum())
    summary = {
        "estado": "EXPERIMENTAL_NO_OFICIAL",
        "api": "NO_API_NO_GOOGLE_PLACES",
        "poligonos_originales_procesados": int(len(pol)),
        "grupos_editoriales_visibles_v0": int(len(groups)),
        "poligonos_excluidos_del_mapa_editorial": excluded_count,
        "mapas_creados": [p.name for p in map_paths],
        "acciones_v2": groups["accion_v2"].value_counts().to_dict(),
        "archivos_principales": [
            "tabla_agrupamiento_editorial_v0.csv",
            "poligonos_editoriales_simplificados_v0.geojson",
            "puntos_evidencia_microzonas_v0.geojson",
            "RESUMEN_CARTOGRAFIA_EDITORIAL_V2.md",
            "HANDOFF_CARTOGRAFIA_EDITORIAL_V2.md",
        ],
    }
    (OUT / "metadata_cartografia_editorial_v2.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    write_markdown(len(pol), len(groups), excluded_count, map_paths, table, groups, reference_layers)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    run()
