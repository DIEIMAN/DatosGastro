from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import streamlit as st

from dashboard.dashboard_config import ANALYTICS, CATEGORY_COLORS, DEFAULT_POINT_COLOR, FIAB_POINT_COLOR, PROCESSED


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
    fact_espacios_f03: pd.DataFrame
    fact_puestos_f03: pd.DataFrame
    fact_eventos: pd.DataFrame
    fact_programas: pd.DataFrame
    puente_evento_programa: pd.DataFrame
    dim_fuente: pd.DataFrame
    dim_categoria: pd.DataFrame
    dim_ubicacion: pd.DataFrame


@st.cache_data(show_spinner=False)
def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, dtype=str, keep_default_na=False)


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
        fact_espacios_f03=read_csv(PROCESSED / "fact_espacio_feria_mercado.csv"),
        fact_puestos_f03=read_csv(PROCESSED / "fact_puesto_feria.csv"),
        fact_eventos=read_csv(PROCESSED / "fact_evento_gastronomico.csv"),
        fact_programas=read_csv(PROCESSED / "fact_programa_politica.csv"),
        puente_evento_programa=read_csv(PROCESSED / "puente_evento_programa.csv"),
        dim_fuente=read_csv(PROCESSED / "dim_fuente.csv"),
        dim_categoria=read_csv(PROCESSED / "dim_categoria_gastronomica.csv"),
        dim_ubicacion=read_csv(PROCESSED / "dim_ubicacion.csv"),
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


def linked_events_for_program(program_id: str, data: DashboardData) -> pd.DataFrame:
    if data.puente_evento_programa.empty or data.fact_eventos.empty:
        return pd.DataFrame()
    links = data.puente_evento_programa[data.puente_evento_programa["id_programa"].astype(str) == str(program_id)]
    if links.empty:
        return pd.DataFrame()
    return links.merge(data.fact_eventos, on="id_evento", how="left", suffixes=("_puente", ""))

