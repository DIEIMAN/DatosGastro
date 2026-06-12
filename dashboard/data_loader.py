from __future__ import annotations

from dataclasses import dataclass
import json
import re
from pathlib import Path

import pandas as pd
import streamlit as st

from dashboard.dashboard_config import ANALYTICS, CATEGORY_COLORS, DEFAULT_POINT_COLOR, F02_USIG_POINT_COLOR, FIAB_POINT_COLOR, PROCESSED, RAW


@dataclass(frozen=True)
class DashboardData:
    resumen: pd.DataFrame
    est_cat_barrio: pd.DataFrame
    hab_anio: pd.DataFrame
    hab_barrio: pd.DataFrame
    hab_categoria: pd.DataFrame
    hab_recientes: pd.DataFrame
    eventos_anio: pd.DataFrame
    eventos_tipo: pd.DataFrame
    eventos_barrio: pd.DataFrame
    eventos_cualitativos: pd.DataFrame
    programas_catalogo: pd.DataFrame
    programas_cualitativos: pd.DataFrame
    mapa_oportunidades: pd.DataFrame
    fact_establecimientos: pd.DataFrame
    fact_habilitaciones: pd.DataFrame
    fact_espacios_f03: pd.DataFrame
    fact_puestos_f03: pd.DataFrame
    fact_eventos: pd.DataFrame
    fact_programas: pd.DataFrame
    puente_evento_programa: pd.DataFrame
    dim_fuente: pd.DataFrame
    dim_categoria: pd.DataFrame
    dim_ubicacion: pd.DataFrame
    geo_cache: pd.DataFrame


@st.cache_data(show_spinner=False)
def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, dtype=str, keep_default_na=False)



@st.cache_data(show_spinner=False)
def read_geojson(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

@st.cache_data(show_spinner=False)
def load_dashboard_data() -> DashboardData:
    return DashboardData(
        resumen=read_csv(ANALYTICS / "analytics_resumen_ejecutivo.csv"),
        est_cat_barrio=read_csv(ANALYTICS / "analytics_establecimientos_por_categoria_barrio.csv"),
        hab_anio=read_csv(ANALYTICS / "analytics_habilitaciones_por_anio.csv"),
        hab_barrio=read_csv(ANALYTICS / "analytics_habilitaciones_por_barrio.csv"),
        hab_categoria=read_csv(ANALYTICS / "analytics_habilitaciones_por_categoria.csv"),
        hab_recientes=read_csv(ANALYTICS / "analytics_habilitaciones_recientes.csv"),
        eventos_anio=read_csv(ANALYTICS / "analytics_eventos_por_anio.csv"),
        eventos_tipo=read_csv(ANALYTICS / "analytics_eventos_por_tipo.csv"),
        eventos_barrio=read_csv(ANALYTICS / "analytics_eventos_por_barrio.csv"),
        eventos_cualitativos=read_csv(ANALYTICS / "analytics_eventos_cualitativos.csv"),
        programas_catalogo=read_csv(ANALYTICS / "analytics_programas_catalogo.csv"),
        programas_cualitativos=read_csv(ANALYTICS / "analytics_programas_cualitativos.csv"),
        mapa_oportunidades=read_csv(ANALYTICS / "analytics_mapa_oportunidades.csv"),
        fact_establecimientos=read_csv(PROCESSED / "fact_establecimiento.csv"),
        fact_habilitaciones=read_csv(PROCESSED / "fact_habilitacion_gastronomica.csv"),
        fact_espacios_f03=read_csv(PROCESSED / "fact_espacio_feria_mercado.csv"),
        fact_puestos_f03=read_csv(PROCESSED / "fact_puesto_feria.csv"),
        fact_eventos=read_csv(PROCESSED / "fact_evento_gastronomico.csv"),
        fact_programas=read_csv(PROCESSED / "fact_programa_politica.csv"),
        puente_evento_programa=read_csv(PROCESSED / "puente_evento_programa.csv"),
        dim_fuente=read_csv(PROCESSED / "dim_fuente.csv"),
        dim_categoria=read_csv(PROCESSED / "dim_categoria_gastronomica.csv"),
        dim_ubicacion=read_csv(PROCESSED / "dim_ubicacion.csv"),
        geo_cache=read_csv(PROCESSED / "geo_cache.csv"),
    )


def number(value: object) -> int:
    try:
        return int(float(str(value).replace(".", "").replace(",", ".")))
    except Exception:
        return 0


def numeric_series(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").fillna(0).astype(int)


def first_value(df: pd.DataFrame, column: str, default: str = "No disponible") -> str:
    if df.empty or column not in df.columns:
        return default
    values = [str(value) for value in df[column].dropna().unique() if str(value).strip()]
    return values[0] if values else default


def get_indicator(resumen: pd.DataFrame, indicator: str) -> int:
    if resumen.empty or "indicador" not in resumen.columns:
        return 0
    row = resumen[resumen["indicador"] == indicator]
    if row.empty:
        return 0
    return number(row.iloc[0].get("valor", 0))


def filter_by_dashboard(df: pd.DataFrame, value: str) -> pd.DataFrame:
    if df.empty or "apto_dashboard" not in df.columns:
        return pd.DataFrame()
    return df[df["apto_dashboard"].astype(str) == value].copy()


def coordinate_series(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series.astype(str).str.replace(",", ".", regex=False), errors="coerce")


def map_ready(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or not {"latitud", "longitud", "calidad_geo"}.issubset(df.columns):
        return pd.DataFrame()
    result = df[df["calidad_geo"].astype(str) == "fuente_oficial"].copy()
    result["latitud_num"] = coordinate_series(result["latitud"])
    result["longitud_num"] = coordinate_series(result["longitud"])
    return result.dropna(subset=["latitud_num", "longitud_num"])


def map_ready_usig(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or not {"latitud", "longitud", "calidad_geo"}.issubset(df.columns):
        return pd.DataFrame()
    result = df[df["calidad_geo"].astype(str).isin(["usig_exacta", "usig_aproximada"])].copy()
    result["latitud_num"] = coordinate_series(result["latitud"])
    result["longitud_num"] = coordinate_series(result["longitud"])
    return result.dropna(subset=["latitud_num", "longitud_num"])


def category_color(value: object) -> list[int]:
    return CATEGORY_COLORS.get(str(value), DEFAULT_POINT_COLOR)


def ensure_columns(df: pd.DataFrame, columns: list[str], default: str = "") -> pd.DataFrame:
    result = df.copy()
    for column in columns:
        if column not in result.columns:
            result[column] = default
    return result


def prepare_f01_map(data: DashboardData, categories: list[str] | None = None) -> pd.DataFrame:
    if data.fact_establecimientos.empty or data.dim_ubicacion.empty:
        return pd.DataFrame()
    result = data.fact_establecimientos.merge(data.dim_ubicacion, on="id_ubicacion", how="left", suffixes=("", "_ubicacion"))
    if not data.dim_categoria.empty:
        result = result.merge(data.dim_categoria[["id_categoria", "categoria_general"]], on="id_categoria", how="left")
    result = map_ready(result)
    result = ensure_columns(result, ["categoria_general", "nombre", "direccion_original", "barrio", "comuna"])
    if categories:
        result = result[result["categoria_general"].astype(str).isin(categories)]
    if not result.empty:
        result["color"] = result["categoria_general"].map(category_color)
        result["capa"] = "F01"
        result["tooltip_categoria"] = result["categoria_general"]
        result["tooltip_detalle"] = result.get("direccion_original", "")
    return result


def prepare_f03_map(data: DashboardData) -> pd.DataFrame:
    if data.fact_espacios_f03.empty:
        return pd.DataFrame()
    result = map_ready(data.fact_espacios_f03)
    result = ensure_columns(result, ["nombre", "tipo_espacio", "direccion", "barrio", "comuna", "productos"])
    if not result.empty:
        result["color"] = [FIAB_POINT_COLOR if value == "FIAB" else [35, 116, 171, 210] for value in result["tipo_espacio"].astype(str)]
        result["capa"] = "F03"
        result["tooltip_categoria"] = result["tipo_espacio"]
        result["tooltip_detalle"] = result["productos"]
    return result


def geo_cache_report(geo_cache: pd.DataFrame) -> dict[str, float | int | bool]:
    if geo_cache.empty or "estado" not in geo_cache.columns:
        return {"total": 0, "exacta": 0, "aproximada": 0, "exact_rate": 0.0, "promovible": False}
    counts = geo_cache["estado"].astype(str).value_counts().to_dict()
    total = len(geo_cache)
    exact = int(counts.get("exacta", 0))
    exact_rate = (exact / total * 100) if total else 0.0
    return {
        "total": total,
        "exacta": exact,
        "aproximada": int(counts.get("aproximada", 0)),
        "exact_rate": exact_rate,
        "promovible": bool(total and exact_rate >= 90),
    }


def prepare_f02_usig_map(data: DashboardData) -> tuple[pd.DataFrame, dict[str, float | int | bool]]:
    report = geo_cache_report(data.geo_cache)
    if not report["promovible"] or data.fact_habilitaciones.empty or data.dim_ubicacion.empty:
        return pd.DataFrame(), report
    result = data.fact_habilitaciones.merge(data.dim_ubicacion, on="id_ubicacion", how="left", suffixes=("", "_ubicacion"))
    result = map_ready_usig(result)
    result = ensure_columns(result, ["descripcion_rubro_original", "categoria_gastronomica_inferida", "direccion_original", "barrio", "comuna"])
    if not result.empty:
        result["color"] = [F02_USIG_POINT_COLOR for _ in range(len(result))]
        result["capa"] = "F02 USIG"
        result["tooltip_categoria"] = result["categoria_gastronomica_inferida"]
        result["tooltip_detalle"] = result["descripcion_rubro_original"]
        result["nombre"] = "Habilitacion " + result.get("id_habilitacion", pd.Series(dtype=str)).astype(str)
    return result, report


def top_f01_barrios(est_cat_barrio: pd.DataFrame, limit: int = 3) -> pd.DataFrame:
    if est_cat_barrio.empty or "barrio" not in est_cat_barrio.columns:
        return pd.DataFrame(columns=["barrio", "cantidad", "porcentaje"])
    grouped = (
        est_cat_barrio.groupby("barrio", dropna=False)["cantidad_establecimientos"]
        .apply(lambda s: numeric_series(s).sum())
        .reset_index(name="cantidad")
    )
    total = grouped["cantidad"].sum()
    grouped["porcentaje"] = (grouped["cantidad"] / total * 100).round(1) if total else 0
    return grouped.sort_values("cantidad", ascending=False).head(limit)


def traceability_rows(analytics_dir: Path = ANALYTICS) -> pd.DataFrame:
    rows = []
    for path in sorted(analytics_dir.glob("analytics_*.csv")):
        df = read_csv(path)
        rows.append(
            {
                "archivo": path.name,
                "estado_datos": first_value(df, "estado_datos"),
                "fuentes_utilizadas": first_value(df, "fuentes_utilizadas"),
                "fecha_consulta_min": first_value(df, "fecha_consulta_min"),
                "fecha_consulta_max": first_value(df, "fecha_consulta_max"),
                "apto_dashboard": first_value(df, "apto_dashboard"),
                "limitaciones": first_value(df, "limitaciones"),
            }
        )
    return pd.DataFrame(rows)



def prepare_f02_choropleth(data: DashboardData) -> tuple[dict, float]:
    geo = read_geojson(RAW / "geo_comunas.geojson")
    if not geo or data.hab_barrio.empty:
        return {}, 0.0
    df = data.hab_barrio.copy()
    df["comuna_norm"] = df.get("comuna", pd.Series(dtype=str)).astype(str).str.extract(r"(1[0-5]|[1-9])", expand=False).fillna("")
    total = numeric_series(df.get("cantidad_habilitaciones", pd.Series(dtype=str))).sum()
    df = df[df["comuna_norm"].ne("")].copy()
    by_comuna = df.groupby("comuna_norm")["cantidad_habilitaciones"].apply(lambda s: numeric_series(s).sum()).to_dict()
    identified = sum(by_comuna.values())
    coverage = (identified / total * 100) if total else 0.0
    max_value = max(by_comuna.values()) if by_comuna else 0
    features = []
    for feature in geo.get("features", []):
        props = dict(feature.get("properties") or {})
        comuna_raw = str(props.get("comuna") or props.get("COMUNA") or props.get("id") or props.get("ID") or "")
        comuna = ""
        match = re.search(r"(1[0-5]|[1-9])", comuna_raw)
        if match:
            comuna = str(int(match.group(1)))
        value = int(by_comuna.get(comuna, 0))
        intensity = value / max_value if max_value else 0
        color = [int(241 - 61 * intensity), int(245 - 200 * intensity), int(249 - 209 * intensity), 80 + int(120 * intensity)]
        props.update(
            {
                "comuna": comuna or comuna_raw,
                "cantidad_habilitaciones": value,
                "porcentaje_total_identificado": round((value / identified * 100), 1) if identified else 0,
                "coverage": round(coverage, 1),
                "fill_color": color,
            }
        )
        enriched = dict(feature)
        enriched["properties"] = props
        features.append(enriched)
    return {"type": "FeatureCollection", "features": features}, coverage

def lectura_serie_f02(hab_anio: pd.DataFrame) -> str:
    """Resume la serie anual comparable: anio pico, valle y ultimo anio."""
    if hab_anio.empty or "comparable_como_flujo_anual" not in hab_anio.columns:
        return ""
    serie = hab_anio[hab_anio["comparable_como_flujo_anual"].astype(str) == "si"].copy()
    if serie.empty:
        return ""
    serie["n"] = numeric_series(serie["cantidad_habilitaciones"])
    serie = serie.sort_values("anio_fuente")
    pico = serie.loc[serie["n"].idxmax()]
    valle = serie.loc[serie["n"].idxmin()]
    ultimo = serie.iloc[-1]
    return (
        f"En la serie comparable, el anio con mas habilitaciones gastronomicas fue {pico['anio_fuente']} "
        f"({int(pico['n'])}) y el de menos fue {valle['anio_fuente']} ({int(valle['n'])}). "
        f"El ultimo anio comparable ({ultimo['anio_fuente']}) registro {int(ultimo['n'])}."
    )


def lectura_comuna_f02(hab_barrio: pd.DataFrame) -> str:
    """Comuna lider en habilitaciones, sobre los registros con comuna informada."""
    if hab_barrio.empty or "comuna" not in hab_barrio.columns:
        return ""
    df = hab_barrio[hab_barrio["comuna"].astype(str).isin([str(v) for v in range(1, 16)])].copy()
    if df.empty:
        return ""
    df["n"] = numeric_series(df["cantidad_habilitaciones"])
    df = df.groupby("comuna")["n"].sum().sort_values(ascending=False)
    total = df.sum()
    top = df.index[0]
    share = df.iloc[0] / total * 100 if total else 0
    return (
        f"Entre los registros con comuna informada, la comuna {top} concentra el {share:.0f}% "
        f"de las habilitaciones gastronomicas ({int(df.iloc[0])} sobre {int(total)})."
    )


def lectura_f03(fact_espacios: pd.DataFrame) -> str:
    """Composicion de los espacios F03 en una frase."""
    if fact_espacios.empty or "tipo_espacio" not in fact_espacios.columns:
        return ""
    tipos = fact_espacios["tipo_espacio"].value_counts()
    alimentarios = (fact_espacios.get("es_gastronomico", pd.Series(dtype=str)).astype(str) == "si").sum()
    partes = ", ".join(f"{count} {tipo}" for tipo, count in tipos.items())
    return f"Hay {len(fact_espacios)} espacios relevados ({partes}); {alimentarios} tienen perfil alimentario."


def linked_events_for_program(program_id: str, data: DashboardData) -> pd.DataFrame:
    if data.puente_evento_programa.empty or data.fact_eventos.empty:
        return pd.DataFrame()
    links = data.puente_evento_programa[data.puente_evento_programa["id_programa"].astype(str) == str(program_id)]
    if links.empty:
        return pd.DataFrame()
    return links.merge(data.fact_eventos, on="id_evento", how="left", suffixes=("_puente", ""))
