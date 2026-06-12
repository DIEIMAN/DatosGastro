from __future__ import annotations

import altair as alt
import pandas as pd
import pydeck as pdk
import streamlit as st

from dashboard.data_loader import numeric_series


def kpi_row(items: list[tuple[str, object, str | None]]) -> None:
    columns = st.columns(len(items))
    for column, (label, value, help_text) in zip(columns, items):
        column.metric(label, value, help=help_text)


def horizontal_bar(
    df: pd.DataFrame,
    label: str,
    value: str,
    title: str,
    *,
    limit: int = 15,
    color: str = "#2f6f9f",
    caption: str = "",
) -> None:
    st.subheader(title)
    if df.empty or label not in df.columns or value not in df.columns:
        st.info(f"No hay datos para {title}.")
        return
    chart_df = df[[label, value]].copy()
    chart_df[value] = numeric_series(chart_df[value])
    chart_df = chart_df.sort_values(value, ascending=False).head(limit)
    chart = (
        alt.Chart(chart_df)
        .mark_bar(color=color)
        .encode(
            y=alt.Y(f"{label}:N", sort="-x", title=None),
            x=alt.X(f"{value}:Q", title=None),
            tooltip=[alt.Tooltip(f"{label}:N", title=label), alt.Tooltip(f"{value}:Q", title=value)],
        )
        .properties(height=max(260, 24 * len(chart_df)))
    )
    st.altair_chart(chart, width="stretch")
    if caption:
        st.caption(caption)


def vertical_bar(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    *,
    order: list[str] | None = None,
    color: str = "#5c7c3f",
    caption: str = "",
) -> None:
    st.subheader(title)
    if df.empty or x not in df.columns or y not in df.columns:
        st.info(f"No hay datos para {title}.")
        return
    chart_df = df[[x, y]].copy()
    chart_df[y] = numeric_series(chart_df[y])
    sort = order if order else None
    chart = (
        alt.Chart(chart_df)
        .mark_bar(color=color)
        .encode(
            x=alt.X(f"{x}:N", sort=sort, title=None),
            y=alt.Y(f"{y}:Q", title=None),
            tooltip=[alt.Tooltip(f"{x}:N", title=x), alt.Tooltip(f"{y}:Q", title=y)],
        )
        .properties(height=320)
    )
    st.altair_chart(chart, width="stretch")
    if caption:
        st.caption(caption)


def searchable_table(df: pd.DataFrame, columns: list[str], key: str) -> pd.DataFrame:
    if df.empty:
        st.info("No hay filas para mostrar.")
        return df
    query = st.text_input("Filtro de texto", key=key)
    view = df.copy()
    if query:
        mask = view.astype(str).apply(lambda col: col.str.contains(query, case=False, na=False)).any(axis=1)
        view = view[mask]
    available = [column for column in columns if column in view.columns]
    st.dataframe(view[available] if available else view, width="stretch", hide_index=True)
    return view


def pydeck_map(f01_map: pd.DataFrame, f03_map: pd.DataFrame, *, show_f01: bool = True, show_f03: bool = True) -> None:
    layers = []
    visible_frames = []
    if show_f01 and not f01_map.empty:
        visible_frames.append(f01_map)
        layers.append(
            pdk.Layer(
                "ScatterplotLayer",
                data=f01_map,
                get_position="[longitud_num, latitud_num]",
                get_fill_color="color",
                get_radius=35,
                pickable=True,
                opacity=0.72,
            )
        )
    if show_f03 and not f03_map.empty:
        visible_frames.append(f03_map)
        layers.append(
            pdk.Layer(
                "ScatterplotLayer",
                data=f03_map,
                get_position="[longitud_num, latitud_num]",
                get_fill_color="color",
                get_radius=85,
                pickable=True,
                opacity=0.88,
            )
        )
    if not layers or not visible_frames:
        st.info("No hay capas seleccionadas con puntos oficiales mapeables.")
        return
    visible = pd.concat(visible_frames, ignore_index=True)
    view_state = pdk.ViewState(
        latitude=float(visible["latitud_num"].mean()),
        longitude=float(visible["longitud_num"].mean()),
        zoom=11,
        pitch=0,
    )
    st.pydeck_chart(
        pdk.Deck(
            map_style=None,
            initial_view_state=view_state,
            layers=layers,
            tooltip={
                "html": (
                    "<b>{nombre}</b><br/>"
                    "Capa: {capa}<br/>"
                    "Categoria: {tooltip_categoria}<br/>"
                    "Barrio: {barrio}<br/>"
                    "Comuna: {comuna}<br/>"
                    "{tooltip_detalle}"
                ),
                "style": {"backgroundColor": "#ffffff", "color": "#111111"},
            },
        ),
        width="stretch",
    )


def pydeck_comuna_choropleth(geojson: dict, coverage: float) -> None:
    if not geojson or not geojson.get("features"):
        st.info("No está disponible `data/raw/geo_comunas.geojson`. Ejecutá `python src/download_sources.py` y luego reconstruí el modelo para habilitar la coropleta.")
        return
    layer = pdk.Layer(
        "GeoJsonLayer",
        data=geojson,
        stroked=True,
        filled=True,
        get_fill_color="properties.fill_color",
        get_line_color=[80, 80, 80, 180],
        get_line_width=45,
        pickable=True,
        opacity=0.72,
    )
    st.pydeck_chart(
        pdk.Deck(
            map_style=None,
            initial_view_state=pdk.ViewState(latitude=-34.61, longitude=-58.44, zoom=10, pitch=0),
            layers=[layer],
            tooltip={
                "html": (
                    "<b>Comuna {comuna}</b><br/>"
                    "Habilitaciones F02 con comuna: {cantidad_habilitaciones}<br/>"
                    "% dentro de registros con comuna: {porcentaje_total_identificado}%<br/>"
                    "Cobertura territorial F02: {coverage}%"
                ),
                "style": {"backgroundColor": "#ffffff", "color": "#111111"},
            },
        ),
        width="stretch",
    )
    st.caption(f"Coropleta calculada solo sobre registros F02 con comuna identificada. Cobertura territorial actual: {coverage:.1f}% del total F02 clasificado.")
