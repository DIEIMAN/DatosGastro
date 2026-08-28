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
V3 = BASE / "cartografia_decision_v3"
V2 = BASE / "cartografia_editorial_v2"
OUT = BASE / "cartografia_redibujo_editorial_v4"

INPUTS = [
    V3 / "tabla_decision_cartografia_v3.csv",
    V3 / "zonas_todas_decision_v3.geojson",
    V3 / "zonas_ejecutivas_candidatas_v3.geojson",
    V3 / "zonas_requieren_redibujo_v3.geojson",
    V3 / "zonas_anexo_exploratorio_v3.geojson",
    V2 / "puntos_evidencia_microzonas_v0.geojson",
]

CALLEJERO = ROOT / "outputs/polos_gastro/fase15_mapas_callejeros_v3/assets/callejero_gcba_2026_06_02.geojson"
BARRIOS = ROOT / "PolosGastro/cartografia/barrios_caba.geojson"
COMUNAS = ROOT / "PolosGastro/cartografia/comunas_caba.geojson"
CRS_METERS = "EPSG:5347"

STATUS_COLORS = {
    "CANDIDATA_FUERTE": "#3f8f75",
    "CANDIDATA_CON_OBSERVACIONES": "#88b78f",
    "REQUIERE_REVISION_HUMANA": "#d28a45",
    "EXPLORATORIA": "#8c96a3",
    "EXCLUIR": "#d9d9d9",
}

FAMILY_COLORS = {
    "MAPA_PRINCIPAL": "#4b9a7f",
    "REQUIERE_REVISION": "#d28a45",
    "ANEXO_EXPLORATORIO": "#8c96a3",
    "EXCLUIR": "#d9d9d9",
}


UNITS = [
    {
        "id_v4": "V4_PALERMO_SOHO_PLAZA_SERRANO",
        "nombre": "Palermo Soho / Plaza Serrano",
        "groups": ["PALERMO_PLAZA_SERRANO_ARMENIA", "PALERMO_SOHO_ESTE"],
        "decision": "FUSIONAR_Y_SIMPLIFICAR",
        "tipo_zona": "nucleo",
        "tipo_geometria": "envolvente_suavizada",
        "estado": "CANDIDATA_FUERTE",
        "confianza": "ALTA",
        "motivo": "Fusiona piezas Soho contiguas en una unidad legible para oficina.",
    },
    {
        "id_v4": "V4_PALERMO_HONDURAS_ARMENIA",
        "nombre": "Honduras / Armenia",
        "groups": ["PALERMO_HONDURAS_ARMENIA"],
        "decision": "MANTENER_SIMPLIFICADO",
        "tipo_zona": "corredor",
        "tipo_geometria": "simplificada",
        "estado": "CANDIDATA_FUERTE",
        "confianza": "ALTA",
        "motivo": "Unidad reconocible y separable de Plaza Serrano.",
    },
    {
        "id_v4": "V4_PALERMO_HOLLYWOOD_FITZ_ROY",
        "nombre": "Palermo Hollywood / Fitz Roy",
        "groups": ["PALERMO_HOLLYWOOD_FITZ_ROY", "PALERMO_HOLLYWOOD_ESTE", "PALERMO_HOLLYWOOD_NORTE"],
        "decision": "FUSIONAR_Y_SIMPLIFICAR",
        "tipo_zona": "nucleo",
        "tipo_geometria": "envolvente_suavizada",
        "estado": "CANDIDATA_FUERTE",
        "confianza": "ALTA",
        "motivo": "Reduce subcortes internos de Hollywood y mantiene lectura urbana clara.",
    },
    {
        "id_v4": "V4_SAN_TELMO_DEFENSA_DORREGO",
        "nombre": "Defensa / Plaza Dorrego",
        "groups": ["SAN_TELMO_DEFENSA_DORREGO"],
        "decision": "MANTENER_SIMPLIFICADO",
        "tipo_zona": "nucleo",
        "tipo_geometria": "simplificada",
        "estado": "CANDIDATA_FUERTE",
        "confianza": "ALTA",
        "motivo": "Nucleo historico legible y defendible como pieza de revision.",
    },
    {
        "id_v4": "V4_SAN_TELMO_MERCADO",
        "nombre": "Mercado de San Telmo",
        "groups": ["SAN_TELMO_MERCADO_NORTE"],
        "decision": "MANTENER_SIMPLIFICADO",
        "tipo_zona": "nucleo",
        "tipo_geometria": "simplificada",
        "estado": "CANDIDATA_FUERTE",
        "confianza": "ALTA",
        "motivo": "Pieza urbana reconocible para revision ejecutiva.",
    },
    {
        "id_v4": "V4_SAN_TELMO_SUR",
        "nombre": "San Telmo sur",
        "groups": ["SAN_TELMO_SUR"],
        "decision": "MANTENER_SIMPLIFICADO",
        "tipo_zona": "nucleo",
        "tipo_geometria": "simplificada",
        "estado": "CANDIDATA_CON_OBSERVACIONES",
        "confianza": "MEDIA",
        "motivo": "Se mantiene separado para no forzar una fusion con el casco historico.",
    },
    {
        "id_v4": "V4_RECOLETA_CENTRO_CULTURAL",
        "nombre": "Recoleta central / cultural",
        "groups": ["RECOLETA_CENTRO", "RECOLETA_ESTE_CULTURAL"],
        "decision": "FUSIONAR_Y_SIMPLIFICAR",
        "tipo_zona": "nucleo",
        "tipo_geometria": "envolvente_suavizada",
        "estado": "CANDIDATA_CON_OBSERVACIONES",
        "confianza": "MEDIA",
        "motivo": "Reduce manchas contiguas y mejora lectura de Recoleta central.",
    },
    {
        "id_v4": "V4_RECOLETA_SANTA_FE_ALTO_PALERMO",
        "nombre": "Recoleta oeste / Santa Fe-Alto Palermo",
        "groups": ["RECOLETA_OESTE_ALTO_PALERMO"],
        "decision": "MANTENER_SIMPLIFICADO",
        "tipo_zona": "corredor",
        "tipo_geometria": "simplificada",
        "estado": "CANDIDATA_CON_OBSERVACIONES",
        "confianza": "MEDIA",
        "motivo": "Pieza legible pero requiere revision de nombre y borde urbano.",
    },
    {
        "id_v4": "V4_CHACARITA_CENTRAL_LACROZE",
        "nombre": "Chacarita central / Federico Lacroze",
        "groups": ["CHACARITA_CENTRO", "CHACARITA_NORTE"],
        "decision": "FUSIONAR_Y_SIMPLIFICAR",
        "tipo_zona": "nucleo",
        "tipo_geometria": "envolvente_suavizada",
        "estado": "CANDIDATA_CON_OBSERVACIONES",
        "confianza": "MEDIA",
        "motivo": "Fusiona piezas cercanas y mantiene la lectura central de Chacarita.",
    },
    {
        "id_v4": "V4_CHACARITA_DORREGO_CORRIENTES",
        "nombre": "Chacarita / Dorrego-Corrientes",
        "groups": ["CHACARITA_SUR"],
        "decision": "MANTENER_SIMPLIFICADO",
        "tipo_zona": "corredor",
        "tipo_geometria": "simplificada",
        "estado": "CANDIDATA_CON_OBSERVACIONES",
        "confianza": "MEDIA",
        "motivo": "Mantiene una pieza sur con nota para revision humana.",
    },
    {
        "id_v4": "V4_VILLA_CRESPO_SCALABRINI",
        "nombre": "Villa Crespo / Scalabrini",
        "groups": ["VILLA_CRESPO_CENTRO_SCALABRINI"],
        "decision": "REDIBUJAR_COMO_NUCLEO",
        "tipo_zona": "nucleo",
        "tipo_geometria": "envolvente_suavizada",
        "estado": "REQUIERE_REVISION_HUMANA",
        "confianza": "MEDIA",
        "motivo": "Buena señal, pero la pieza v3 seguia siendo demasiado irregular.",
    },
    {
        "id_v4": "V4_VILLA_CRESPO_CORRIENTES_LIMITE_PALERMO",
        "nombre": "Villa Crespo / Corrientes-limite Palermo",
        "groups": ["VILLA_CRESPO_OESTE_CORRIENTES", "VILLA_CRESPO_ESTE_PALERMO_LIMITE"],
        "decision": "FUSIONAR_Y_SIMPLIFICAR",
        "tipo_zona": "corredor",
        "tipo_geometria": "envolvente_suavizada",
        "estado": "CANDIDATA_CON_OBSERVACIONES",
        "confianza": "MEDIA",
        "motivo": "Une piezas de borde y exige nota para no mezclarla con Palermo.",
    },
    {
        "id_v4": "V4_BELGRANO_BARRIO_CHINO_BARRANCAS",
        "nombre": "Barrio Chino / Barrancas",
        "groups": ["BELGRANO_BARRIO_CHINO_BARRANCAS"],
        "decision": "MANTENER_SIMPLIFICADO",
        "tipo_zona": "nucleo",
        "tipo_geometria": "simplificada",
        "estado": "CANDIDATA_FUERTE",
        "confianza": "MEDIA",
        "motivo": "Pieza puntual clara dentro de Belgrano.",
    },
    {
        "id_v4": "V4_BELGRANO_CABILDO_JURAMENTO",
        "nombre": "Cabildo / Juramento",
        "groups": ["BELGRANO_CABILDO_JURAMENTO"],
        "decision": "REDIBUJAR_COMO_CORREDOR",
        "tipo_zona": "corredor",
        "tipo_geometria": "envolvente_suavizada",
        "estado": "REQUIERE_REVISION_HUMANA",
        "confianza": "MEDIA",
        "motivo": "Debe redibujarse sobre ejes urbanos para evitar cortes KMeans.",
    },
    {
        "id_v4": "V4_BELGRANO_BAJO",
        "nombre": "Bajo Belgrano",
        "groups": ["BELGRANO_BAJO"],
        "decision": "REDIBUJAR_COMO_NUCLEO",
        "tipo_zona": "nucleo",
        "tipo_geometria": "envolvente_suavizada",
        "estado": "REQUIERE_REVISION_HUMANA",
        "confianza": "MEDIA",
        "motivo": "Tiene señal, pero requiere borde editorial mas claro.",
    },
    {
        "id_v4": "V4_BELGRANO_LIBERTADOR_NORTE",
        "nombre": "Libertador / Barrancas-Belgrano norte",
        "groups": ["BELGRANO_NORTE_OESTE"],
        "decision": "REDIBUJAR_COMO_CORREDOR",
        "tipo_zona": "corredor",
        "tipo_geometria": "envolvente_suavizada",
        "estado": "REQUIERE_REVISION_HUMANA",
        "confianza": "MEDIA",
        "motivo": "Agrupa el norte/oeste de Belgrano sin validar limite final.",
    },
    {
        "id_v4": "V4_CABALLITO_ACOYTE_CENTRO",
        "nombre": "Acoyte / Caballito centro",
        "groups": ["CABALLITO_ACOYTE_CENTRO"],
        "decision": "REDIBUJAR_COMO_NUCLEO",
        "tipo_zona": "nucleo",
        "tipo_geometria": "envolvente_suavizada",
        "estado": "REQUIERE_REVISION_HUMANA",
        "confianza": "MEDIA",
        "motivo": "Unidad fuerte, pero necesita borde urbano mas limpio.",
    },
    {
        "id_v4": "V4_CABALLITO_PRIMERA_JUNTA_RIVADAVIA",
        "nombre": "Primera Junta / Rivadavia",
        "groups": ["CABALLITO_PRIMERA_JUNTA_RIVADAVIA"],
        "decision": "REDIBUJAR_COMO_CORREDOR",
        "tipo_zona": "corredor",
        "tipo_geometria": "envolvente_suavizada",
        "estado": "REQUIERE_REVISION_HUMANA",
        "confianza": "MEDIA",
        "motivo": "Debe redibujarse como corredor y no como mancha extensa.",
    },
    {
        "id_v4": "V4_CABALLITO_PEDRO_GOYENA",
        "nombre": "Pedro Goyena",
        "groups": ["CABALLITO_PEDRO_GOYENA"],
        "decision": "REDIBUJAR_COMO_CORREDOR",
        "tipo_zona": "corredor",
        "tipo_geometria": "envolvente_suavizada",
        "estado": "REQUIERE_REVISION_HUMANA",
        "confianza": "MEDIA",
        "motivo": "Pieza reconocible, pendiente de redibujo sobre eje.",
    },
    {
        "id_v4": "V4_CABALLITO_AVELLANEDA",
        "nombre": "Avellaneda / zona comercial",
        "groups": ["CABALLITO_AVELLANEDA_COMERCIAL"],
        "decision": "REDIBUJAR_COMO_CORREDOR",
        "tipo_zona": "corredor",
        "tipo_geometria": "simplificada",
        "estado": "REQUIERE_REVISION_HUMANA",
        "confianza": "BAJA",
        "motivo": "Solo se sostiene como pieza en revision, no como mapa firme.",
    },
    {
        "id_v4": "V4_CORRIENTES_OESTE_ABASTO_ONCE",
        "nombre": "Corrientes oeste / Abasto-Once",
        "groups": ["CORRIENTES_OESTE_ABASTO_ONCE"],
        "decision": "REDIBUJAR_COMO_CORREDOR",
        "tipo_zona": "corredor",
        "tipo_geometria": "envolvente_suavizada",
        "estado": "REQUIERE_REVISION_HUMANA",
        "confianza": "MEDIA",
        "motivo": "Corredor defendible como insumo, pendiente de redibujo fino.",
    },
    {
        "id_v4": "V4_CORRIENTES_CENTRO_TEATRAL",
        "nombre": "Corrientes centro / eje teatral-gastronomico",
        "groups": ["CORRIENTES_CENTRO_TEATRAL"],
        "decision": "REDIBUJAR_COMO_CORREDOR",
        "tipo_zona": "corredor",
        "tipo_geometria": "envolvente_suavizada",
        "estado": "REQUIERE_REVISION_HUMANA",
        "confianza": "MEDIA",
        "motivo": "Debe convertirse en corredor urbano, no tile algoritimico.",
    },
    {
        "id_v4": "V4_CORRIENTES_ESTE_CENTRO",
        "nombre": "Corrientes este / Centro",
        "groups": ["CORRIENTES_ESTE_CENTRO", "CORRIENTES_TRIBUNALES_OBELISCO"],
        "decision": "FUSIONAR_Y_SIMPLIFICAR",
        "tipo_zona": "corredor",
        "tipo_geometria": "envolvente_suavizada",
        "estado": "REQUIERE_REVISION_HUMANA",
        "confianza": "MEDIA",
        "motivo": "Fusiona piezas contiguas y reduce cortes del eje Corrientes.",
    },
    {
        "id_v4": "V4_FLORIDA_LAVALLE_MICROCENTRO",
        "nombre": "Florida-Lavalle / Microcentro",
        "groups": ["FLORIDA_LAVALLE_MICROCENTRO"],
        "decision": "REDIBUJAR_COMO_NUCLEO",
        "tipo_zona": "nucleo",
        "tipo_geometria": "envolvente_suavizada",
        "estado": "REQUIERE_REVISION_HUMANA",
        "confianza": "MEDIA",
        "motivo": "Nucleo claro, pendiente de redibujo sobre peatonales/ejes.",
    },
    {
        "id_v4": "V4_MICROCENTRO_LABORAL_ADMINISTRATIVO",
        "nombre": "Microcentro laboral / administrativo",
        "groups": ["MICROCENTRO_LABORAL_ADMINISTRATIVO", "CENTRO_TRIBUNALES_ADMINISTRATIVO"],
        "decision": "FUSIONAR_Y_SIMPLIFICAR",
        "tipo_zona": "nucleo",
        "tipo_geometria": "envolvente_suavizada",
        "estado": "REQUIERE_REVISION_HUMANA",
        "confianza": "MEDIA",
        "motivo": "Agrupa señales administrativas, requiere decision humana.",
    },
    {
        "id_v4": "V4_PUERTO_MADERO_CENTRO_DIQUES",
        "nombre": "Puerto Madero centro / diques",
        "groups": ["PUERTO_MADERO_CENTRO_FRENTES", "PUERTO_MADERO_NORTE_FRENTE_OESTE"],
        "decision": "FUSIONAR_Y_SIMPLIFICAR",
        "tipo_zona": "corredor",
        "tipo_geometria": "envolvente_suavizada",
        "estado": "CANDIDATA_CON_OBSERVACIONES",
        "confianza": "MEDIA",
        "motivo": "Fusiona frentes utiles y evita piezas aisladas.",
    },
    {
        "id_v4": "V4_PUERTO_MADERO_SUR_DIQUES",
        "nombre": "Puerto Madero sur / diques",
        "groups": ["PUERTO_MADERO_SUR_DIQUES"],
        "decision": "REDIBUJAR_COMO_CORREDOR",
        "tipo_zona": "corredor",
        "tipo_geometria": "envolvente_suavizada",
        "estado": "REQUIERE_REVISION_HUMANA",
        "confianza": "BAJA",
        "motivo": "Se conserva para revision, no como pieza firme.",
    },
    {
        "id_v4": "V4_ANEXO_COSTANERA_NORTE",
        "nombre": "Costanera Norte / señal exploratoria",
        "groups": ["COSTANERA_NORTE_SENAL_EXPLORATORIA"],
        "decision": "PASAR_A_ANEXO",
        "tipo_zona": "senal_exploratoria",
        "tipo_geometria": "simplificada",
        "estado": "EXPLORATORIA",
        "confianza": "BAJA",
        "motivo": "Alta dependencia Places y baja defendibilidad para mapa principal.",
    },
    {
        "id_v4": "V4_ANEXO_CASEROS_BARRACAS",
        "nombre": "Av. Caseros / Barracas exploratoria",
        "groups": ["AV_CASEROS_BARRACAS_SENAL_EXPLORATORIA", "CASEROS_BARRACAS_NUCLEO_DEFENDIBLE"],
        "decision": "PASAR_A_ANEXO",
        "tipo_zona": "senal_exploratoria",
        "tipo_geometria": "envolvente_suavizada",
        "estado": "EXPLORATORIA",
        "confianza": "BAJA",
        "motivo": "No se fuerza aprobacion; queda como anexo para decision humana.",
    },
    {
        "id_v4": "V4_ANEXO_PUERTO_MADERO_SENAL",
        "nombre": "Puerto Madero / piezas exploratorias",
        "groups": ["PUERTO_MADERO_SENAL_EXPLORATORIA"],
        "decision": "PASAR_A_ANEXO",
        "tipo_zona": "senal_exploratoria",
        "tipo_geometria": "simplificada",
        "estado": "EXPLORATORIA",
        "confianza": "BAJA",
        "motivo": "Piezas con respaldo insuficiente para mapa principal.",
    },
    {
        "id_v4": "V4_ANEXO_CABALLITO_SENAL",
        "nombre": "Caballito / señal exploratoria",
        "groups": ["CABALLITO_SENAL_EXPLORATORIA"],
        "decision": "PASAR_A_ANEXO",
        "tipo_zona": "senal_exploratoria",
        "tipo_geometria": "simplificada",
        "estado": "EXPLORATORIA",
        "confianza": "BAJA",
        "motivo": "Dependencia Places alta; no entra al mapa principal.",
    },
]


def require_inputs() -> None:
    missing = [p for p in INPUTS if not p.exists()]
    if missing:
        raise FileNotFoundError("Faltan insumos: " + ", ".join(str(p) for p in missing))
    if OUT.exists():
        raise FileExistsError(f"La carpeta de salida ya existe: {OUT}")
    OUT.mkdir(parents=True, exist_ok=False)


def simplify_geometry(geoms, kind: str):
    union = unary_union(list(geoms))
    if union.is_empty:
        return union
    geom = union.buffer(35).buffer(-28).simplify(35, preserve_topology=True)
    if kind == "envolvente_suavizada" and geom.geom_type == "GeometryCollection":
        geom = union.convex_hull.simplify(35, preserve_topology=True)
    if not geom.is_valid:
        geom = geom.buffer(0)
    return geom


def build_v4_units(v3: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    v3m = v3.to_crs(CRS_METERS)
    rows = []
    used = []
    for unit in UNITS:
        sub = v3m[v3m["grupo_editorial_v0"].isin(unit["groups"])].copy()
        if len(sub) != len(unit["groups"]):
            missing = sorted(set(unit["groups"]) - set(sub["grupo_editorial_v0"]))
            raise ValueError(f"Faltan grupos para {unit['id_v4']}: {missing}")
        used.extend(unit["groups"])
        geom = simplify_geometry(sub.geometry, unit["tipo_geometria"])
        total = int(sub["entidades_total"].fillna(0).sum())
        f01 = int(sub["cantidad_f01_f02"].fillna(0).sum())
        places = int(sub["cantidad_places"].fillna(0).sum())
        pct = round((places / total) * 100, 1) if total else 0.0
        area_ha = round(gpd.GeoSeries([geom], crs=CRS_METERS).area.iloc[0] / 10_000, 2)
        density = round(total / area_ha, 2) if area_ha else 0.0
        if unit["estado"] in {"CANDIDATA_FUERTE", "CANDIDATA_CON_OBSERVACIONES"}:
            family = "MAPA_PRINCIPAL"
        elif unit["estado"] == "REQUIERE_REVISION_HUMANA":
            family = "REQUIERE_REVISION"
        elif unit["estado"] == "EXPLORATORIA":
            family = "ANEXO_EXPLORATORIO"
        else:
            family = "EXCLUIR"
        rows.append(
            {
                "id_v4": unit["id_v4"],
                "nombre_editorial_orientativo": unit["nombre"],
                "macrozona": "; ".join(sorted(sub["macrozona"].dropna().astype(str).unique())),
                "familia_v3": "; ".join(sorted(sub["familia_v3"].dropna().astype(str).unique())),
                "familia_v4": family,
                "decision_v4": unit["decision"],
                "ids_grupos_v3_origen": "; ".join(unit["groups"]),
                "entidades_total": total,
                "cantidad_f01_f02": f01,
                "cantidad_places": places,
                "porcentaje_places": pct,
                "superficie_ha": area_ha,
                "densidad_entidades_ha": density,
                "tipo_geometria": unit["tipo_geometria"],
                "tipo_zona": unit["tipo_zona"],
                "nivel_confianza": unit["confianza"],
                "estado_institucional_sugerido": unit["estado"],
                "motivo_redibujo": unit["motivo"],
                "observaciones": "Experimental / no oficial. Nombre y limite orientativos; no usar como delimitacion institucional final.",
                "geometry": geom,
            }
        )
    missing = sorted(set(v3["grupo_editorial_v0"]) - set(used))
    extra = sorted(set(used) - set(v3["grupo_editorial_v0"]))
    if missing or extra:
        raise ValueError(f"Mapeo v4 incompleto. missing={missing}, extra={extra}")
    return gpd.GeoDataFrame(rows, geometry="geometry", crs=CRS_METERS).to_crs("EPSG:4326")


def write_layers(units: gpd.GeoDataFrame, points: gpd.GeoDataFrame) -> None:
    units.to_file(OUT / "poligonos_editoriales_redibujados_v4.geojson", driver="GeoJSON")
    units[units["familia_v4"] == "MAPA_PRINCIPAL"].to_file(OUT / "poligonos_v4_mapa_principal.geojson", driver="GeoJSON")
    units[units["familia_v4"] == "REQUIERE_REVISION"].to_file(OUT / "poligonos_v4_requieren_revision.geojson", driver="GeoJSON")
    units[units["familia_v4"] == "ANEXO_EXPLORATORIO"].to_file(OUT / "poligonos_v4_anexo_exploratorio.geojson", driver="GeoJSON")

    rows = []
    for _, row in units.iterrows():
        for group in str(row["ids_grupos_v3_origen"]).split("; "):
            rows.append({"grupo_editorial_v0": group, "id_v4": row["id_v4"], "nombre_editorial_orientativo": row["nombre_editorial_orientativo"], "familia_v4": row["familia_v4"]})
    map_df = pd.DataFrame(rows)
    pts = points.merge(map_df, on="grupo_editorial_v0", how="left")
    pts["id_v4"] = pts["id_v4"].fillna("SIN_UNIDAD_V4")
    pts["nombre_editorial_orientativo"] = pts["nombre_editorial_orientativo"].fillna("Sin unidad v4 / ruido")
    pts["familia_v4"] = pts["familia_v4"].fillna("EXCLUIR")
    keep_cols = [
        "fuente",
        "macrozona_id",
        "cluster_original",
        "grupo_editorial_v0",
        "id_v4",
        "nombre_editorial_orientativo",
        "familia_v4",
        "accion_v2",
        "mantener_en_mapa",
        "geometry",
    ]
    pts[keep_cols].to_file(OUT / "puntos_evidencia_v4.geojson", driver="GeoJSON")


def load_refs():
    barrios = gpd.read_file(BARRIOS) if BARRIOS.exists() else None
    comunas = gpd.read_file(COMUNAS) if COMUNAS.exists() else None
    streets = None
    if CALLEJERO.exists():
        streets = gpd.read_file(CALLEJERO)
        streets["tipo_c_norm"] = streets["tipo_c"].astype(str).str.upper()
        streets["red_norm"] = streets["red_jerarq"].astype(str).str.upper()
        keep = streets["tipo_c_norm"].isin(["AVENIDA", "BOULEVARD", "AUTOPISTA", "CALLE PEATONAL"])
        keep = keep | streets["red_norm"].str.contains("TRONCAL|PRINCIPAL|COMPLEMENTARIA", na=False)
        streets = streets[keep].copy()
    return barrios, comunas, streets


def bbox_filter(gdf, bounds, pad=0.008):
    if gdf is None or gdf.empty:
        return None
    minx, miny, maxx, maxy = bounds
    return gdf.cx[minx - pad : maxx + pad, miny - pad : maxy + pad].copy()


def setup_ax(ax, selected, refs, street_alpha=0.35, street_width=0.30):
    barrios, comunas, streets = refs
    bounds = selected.total_bounds
    barrios_sub = bbox_filter(barrios, bounds, 0.01)
    comunas_sub = bbox_filter(comunas, bounds, 0.01)
    streets_sub = bbox_filter(streets, bounds, 0.01)
    if barrios_sub is not None and not barrios_sub.empty:
        barrios_sub.boundary.plot(ax=ax, color="#ddd7ce", linewidth=0.42, alpha=0.75, zorder=1)
    if comunas_sub is not None and not comunas_sub.empty:
        comunas_sub.boundary.plot(ax=ax, color="#c4bbae", linewidth=0.70, alpha=0.55, zorder=2)
    if streets_sub is not None and not streets_sub.empty:
        streets_sub.plot(ax=ax, color="#b6afa5", linewidth=street_width, alpha=street_alpha, zorder=3)
    minx, miny, maxx, maxy = bounds
    dx = max((maxx - minx) * 0.12, 0.004)
    dy = max((maxy - miny) * 0.12, 0.004)
    ax.set_xlim(minx - dx, maxx + dx)
    ax.set_ylim(miny - dy, maxy + dy)
    ax.set_axis_off()


LABEL_OFFSETS = {
    "V4_SAN_TELMO_MERCADO": (0.002, 0.0015),
    "V4_SAN_TELMO_DEFENSA_DORREGO": (-0.0025, 0.0005),
    "V4_SAN_TELMO_SUR": (0.0015, -0.001),
    "V4_PALERMO_SOHO_PLAZA_SERRANO": (-0.002, 0.0005),
    "V4_PALERMO_HONDURAS_ARMENIA": (0.002, -0.0005),
    "V4_CHACARITA_CENTRAL_LACROZE": (-0.001, 0.001),
    "V4_CHACARITA_DORREGO_CORRIENTES": (0.001, -0.001),
}


def annotate(ax, selected, fontsize=7.5):
    reps = selected.to_crs(CRS_METERS).representative_point().to_crs("EPSG:4326")
    for (_, row), pt in zip(selected.iterrows(), reps):
        dx, dy = LABEL_OFFSETS.get(row["id_v4"], (0, 0))
        ax.text(
            pt.x + dx,
            pt.y + dy,
            row["nombre_editorial_orientativo"],
            ha="center",
            va="center",
            fontsize=fontsize,
            weight="bold",
            color="#16202a",
            bbox={"facecolor": "#fffdf7", "edgecolor": "#9c9387", "linewidth": 0.35, "alpha": 0.92, "boxstyle": "round,pad=0.22"},
            zorder=9,
        )


def save_map(fig, path: Path):
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def plot_map(units, points, refs, filename, title, selector, mode="main", macros=None):
    selected = units[selector(units)].copy()
    if macros:
        selected = selected[selected["macrozona"].apply(lambda x: any(m in str(x) for m in macros))].copy()
    if selected.empty:
        raise ValueError(f"Mapa sin geometria: {filename}")
    fig, ax = plt.subplots(figsize=(12.5, 8.5), dpi=220)
    fig.patch.set_facecolor("#faf8f2")
    ax.set_facecolor("#faf8f2")
    setup_ax(ax, selected, refs, street_alpha=0.62 if mode == "qa" else 0.32, street_width=0.44 if mode == "qa" else 0.28)
    if mode == "qa":
        pts = points[points["id_v4"].isin(selected["id_v4"]) & (points["mantener_en_mapa"] != "NO")].copy()
        if not pts.empty:
            pts[pts["fuente"].astype(str).eq("F01+F02")].plot(ax=ax, color="#1f5d7a", markersize=5, alpha=0.35, zorder=4)
            pts[pts["fuente"].astype(str).eq("google_places")].plot(ax=ax, color="#c47a1d", markersize=4, alpha=0.30, zorder=4)
    if mode == "general":
        for fam, sub in selected.groupby("familia_v4"):
            color = FAMILY_COLORS.get(fam, "#999999")
            label = {"MAPA_PRINCIPAL": "principal", "REQUIERE_REVISION": "revision", "ANEXO_EXPLORATORIO": "anexo"}.get(fam, fam)
            sub.plot(ax=ax, facecolor=color, edgecolor="#25323a", linewidth=1.0, alpha=0.38, zorder=5, label=label)
            sub.boundary.plot(ax=ax, color="#25323a", linewidth=0.85, alpha=0.82, zorder=6)
        ax.legend(loc="upper right", frameon=True, facecolor="#fffdf7", edgecolor="#aaa", fontsize=8)
    else:
        for status, sub in selected.groupby("estado_institucional_sugerido"):
            color = STATUS_COLORS.get(status, "#999999")
            sub.plot(ax=ax, facecolor=color, edgecolor="#25323a", linewidth=1.0, alpha=0.40, zorder=5)
            sub.boundary.plot(ax=ax, color="#25323a", linewidth=0.90, alpha=0.85, zorder=6)
    annotate(ax, selected, fontsize=6.0 if len(selected) > 12 else 8.0)
    ax.set_title(title, loc="left", fontsize=14.5, weight="bold", color="#16202a")
    note = "Experimental / no oficial. Propuesta editorial orientativa; no es delimitacion final."
    if mode == "qa":
        note = "QA tecnico: puntos + poligonos. No usar como mapa final."
    ax.text(0.01, 0.015, note, transform=ax.transAxes, fontsize=7.5, color="#57606a")
    out = OUT / filename
    save_map(fig, out)
    return out


def make_maps(units, points, refs):
    maps = []
    maps.append(plot_map(units, points, refs, "mapa_principal_editorial_v4.png", "Microzonas gastronomicas - propuesta editorial v4", lambda g: g["familia_v4"] == "MAPA_PRINCIPAL"))
    maps.append(plot_map(units, points, refs, "mapa_general_decision_v4.png", "Cartografia editorial v4 - principal, revision y anexo", lambda g: g["familia_v4"] != "EXCLUIR", mode="general"))
    maps.append(plot_map(units, points, refs, "mapa_qa_puntos_y_poligonos_v4.png", "QA puntos y poligonos v4", lambda g: g["familia_v4"] != "EXCLUIR", mode="qa"))
    zone_specs = [
        ("mapa_palermo_v4.png", "Palermo - propuesta v4", ["MZ_PALERMO_SOHO", "MZ_PALERMO_HOLLYWOOD"]),
        ("mapa_san_telmo_v4.png", "San Telmo - propuesta v4", ["MZ_SAN_TELMO"]),
        ("mapa_belgrano_v4.png", "Belgrano - propuesta v4", ["MZ_BELGRANO"]),
        ("mapa_corrientes_microcentro_v4.png", "Corrientes / Microcentro - propuesta v4", ["MZ_AVENIDA_CORRIENTES", "MZ_MICROCENTRO_Y_CENTRO"]),
        ("mapa_caballito_v4.png", "Caballito - propuesta v4", ["MZ_CABALLITO"]),
        ("mapa_recoleta_v4.png", "Recoleta - propuesta v4", ["MZ_RECOLETA"]),
        ("mapa_villa_crespo_v4.png", "Villa Crespo - propuesta v4", ["MZ_VILLA_CRESPO"]),
        ("mapa_chacarita_v4.png", "Chacarita - propuesta v4", ["MZ_CHACARITA"]),
        ("mapa_puerto_madero_v4.png", "Puerto Madero - propuesta v4", ["MZ_PUERTO_MADERO"]),
        ("mapa_anexo_exploratorio_v4.png", "Anexo exploratorio v4 - no incorporar al mapa principal", None),
    ]
    for filename, title, macros in zone_specs:
        if filename == "mapa_anexo_exploratorio_v4.png":
            maps.append(plot_map(units, points, refs, filename, title, lambda g: g["familia_v4"] == "ANEXO_EXPLORATORIO", mode="general"))
        else:
            maps.append(plot_map(units, points, refs, filename, title, lambda g: g["familia_v4"].isin(["MAPA_PRINCIPAL", "REQUIERE_REVISION"]), macros=macros))
    return maps


def png_nonblank(path: Path):
    img = Image.open(path).convert("RGB")
    colors = img.getcolors(maxcolors=10_000_000)
    unique = len(colors) if colors is not None else 10_000_000
    bbox = img.getbbox()
    return {"archivo": path.name, "ancho": img.width, "alto": img.height, "colores_unicos": unique, "no_blanco": bool(bbox and unique > 10)}


def write_docs(units, maps):
    counts = units["familia_v4"].value_counts().to_dict()
    principal = units[units["familia_v4"] == "MAPA_PRINCIPAL"]["nombre_editorial_orientativo"].tolist()
    revision = units[units["familia_v4"] == "REQUIERE_REVISION"]["nombre_editorial_orientativo"].tolist()
    anexo = units[units["familia_v4"] == "ANEXO_EXPLORATORIO"]["nombre_editorial_orientativo"].tolist()
    resumen = f"""# Resumen cartografia redibujo editorial v4

Estado: EXPERIMENTAL / NO OFICIAL.

## Sintesis

La v4 busca resolver el problema principal que seguia abierto en v3: la lectura de oficina. La v3 separaba decisiones, pero todavia mostraba 41 grupos heredados de geometria algoritimica. Esta version reduce esos 41 grupos a {len(units)} unidades editoriales orientativas, con geometria derivada y simplificada.

No es una delimitacion institucional final. Es una propuesta para revisar nombres, piezas y jerarquia antes de cualquier comparacion final o institucionalizacion.

## Conteo v4

{json.dumps(counts, ensure_ascii=False, indent=2)}

## Zonas que quedaron mas fuertes

- Palermo: reducido a tres piezas principales.
- San Telmo: mantiene tres nucleos legibles.
- Recoleta: se simplifica a dos piezas.
- Chacarita: queda en dos unidades orientativas.
- Puerto Madero: se ordena en frentes principales y anexo.

## Zonas pendientes

- Corrientes / Microcentro: sigue requiriendo redibujo sobre calles reales.
- Belgrano: mejora la lectura, pero Cabildo/Juramento, Bajo Belgrano y norte requieren revision humana.
- Caballito: requiere redibujo para evitar manchas extensas.
- Villa Crespo / Scalabrini: conserva buena señal, pero debe revisarse como nucleo.

## Anexo exploratorio

{chr(10).join(f'- {x}' for x in anexo)}

## No usar como final

- No usar los poligonos v4 como limites institucionales.
- No presentar el mapa QA como pieza ejecutiva.
- No convertir señales de Google Places en padron ni actividad vigente.

## Decisiones humanas pendientes

- Validar nombres orientativos.
- Redibujar bordes finos en QGIS sobre calles reales.
- Confirmar que zonas exploratorias quedan fuera del mapa principal.
- Definir si algunas unidades de revision pasan a candidatas fuertes.

## Mapas creados

{chr(10).join(f'- `{p.name}`' for p in maps)}
"""
    (OUT / "RESUMEN_CARTOGRAFIA_REDIBUJO_EDITORIAL_V4.md").write_text(resumen, encoding="utf-8")

    handoff = """# Handoff cartografia redibujo editorial v4

Estado: EXPERIMENTAL / NO OFICIAL.

## Mirar primero

1. `mapa_principal_editorial_v4.png`
2. `mapa_general_decision_v4.png`
3. `tabla_redibujo_editorial_v4.csv`

## Capas para abrir en QGIS

- `poligonos_editoriales_redibujados_v4.geojson`
- `poligonos_v4_mapa_principal.geojson`
- `poligonos_v4_requieren_revision.geojson`
- `poligonos_v4_anexo_exploratorio.geojson`
- `puntos_evidencia_v4.geojson`

## Zonas a revisar manualmente

- Corrientes / Microcentro.
- Belgrano.
- Caballito.
- Puerto Madero norte/sur.
- Villa Crespo / Scalabrini.

## Aclaracion de nombres

Todos los nombres son orientativos. Sirven para revision editorial y no deben tomarse como denominaciones oficiales.

## Pasos faltantes para institucionalizar

1. Validar nombres y familias con decision humana.
2. Redibujar limites finos sobre calles reales.
3. Revisar cada unidad contra fuentes oficiales y criterio territorial.
4. Generar una version posterior solo cuando los limites esten revisados.
"""
    (OUT / "HANDOFF_CARTOGRAFIA_REDIBUJO_EDITORIAL_V4.md").write_text(handoff, encoding="utf-8")


def run():
    require_inputs()
    v3 = gpd.read_file(V3 / "zonas_todas_decision_v3.geojson")
    points = gpd.read_file(V2 / "puntos_evidencia_microzonas_v0.geojson")
    if len(v3) != 41:
        raise ValueError(f"Se esperaban 41 grupos v3, se leyeron {len(v3)}")
    units = build_v4_units(v3)
    table = pd.DataFrame(units.drop(columns="geometry"))
    table.to_csv(OUT / "tabla_redibujo_editorial_v4.csv", index=False, encoding="utf-8")
    write_layers(units, points)
    points_v4 = gpd.read_file(OUT / "puntos_evidencia_v4.geojson")
    maps = make_maps(units, points_v4, load_refs())
    qa = pd.DataFrame([png_nonblank(p) for p in maps])
    qa.to_csv(OUT / "qa_png_no_blanco_v4.csv", index=False, encoding="utf-8")
    if not qa["no_blanco"].all():
        bad = qa.loc[~qa["no_blanco"], "archivo"].tolist()
        raise RuntimeError("PNG posiblemente en blanco: " + ", ".join(bad))
    write_docs(units, maps)
    metadata = {
        "estado": "EXPERIMENTAL_NO_OFICIAL",
        "api": "NO_API_NO_GOOGLE_PLACES",
        "grupos_v3_procesados": int(len(v3)),
        "unidades_v4_generadas": int(len(units)),
        "reduccion": f"41->{len(units)}",
        "conteo_familia_v4": units["familia_v4"].value_counts().to_dict(),
        "conteo_estado_institucional_sugerido": units["estado_institucional_sugerido"].value_counts().to_dict(),
        "mapas_creados": [p.name for p in maps],
    }
    (OUT / "metadata_cartografia_redibujo_editorial_v4.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(metadata, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    run()
