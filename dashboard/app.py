from __future__ import annotations

import pandas as pd
import streamlit as st

from dashboard.components import horizontal_bar, kpi_row, pydeck_map, searchable_table, vertical_bar
from dashboard.dashboard_config import DOCS, F02_SERIE_ORDER
from dashboard.data_loader import (
    DashboardData,
    filter_by_dashboard,
    first_value,
    get_indicator,
    linked_events_for_program,
    load_dashboard_data,
    number,
    numeric_series,
    prepare_f01_map,
    prepare_f03_map,
    top_f01_barrios,
    traceability_rows,
)
from dashboard.textos import CRITICAL_WARNINGS, TAB_INTROS, WHAT_IT_DOES_NOT_ANSWER, source_caption


st.set_page_config(page_title="DataGastro - Preguntas de gestion", layout="wide")


def caption_for(df: pd.DataFrame, source_key: str) -> str:
    return source_caption(source_key, first_value(df, "fecha_consulta_max"))


def metric_value(data: DashboardData, indicator: str) -> int:
    return get_indicator(data.resumen, indicator)


def render_global_header() -> None:
    st.title("DataGastro - Tablero de gestion")
    st.caption("Lectura integrada de oferta, habilitaciones, espacios, eventos y programas con reglas metodologicas explicitas.")
    for warning in CRITICAL_WARNINGS:
        st.warning(warning)


def render_panorama(data: DashboardData) -> None:
    st.header("Panorama")
    st.write(TAB_INTROS["panorama"])
    kpi_row(
        [
            ("F01 oferta registrada", f"{metric_value(data, 'establecimientos_oferta_gastronomica_f01'):,}".replace(",", "."), "Registros publicados por Buenos Aires Data; no confirma vigencia actual."),
            ("F02 habilitaciones", f"{metric_value(data, 'habilitaciones_gastronomicas_f02'):,}".replace(",", "."), "Serie comparable 2019-2024. 2015-2018 es agregado y 2025 se muestra aparte por esquema distinto."),
            ("F03 espacios", f"{metric_value(data, 'espacios_ferias_mercados_f03'):,}".replace(",", "."), "Espacios reales: mercados, ferias/padron agregado y FIAB. Excluye puestos/personas."),
            ("F04 eventos aptos", f"{metric_value(data, 'eventos_gastronomicos_reales_f04_aptos'):,}".replace(",", "."), "Solo eventos apto_dashboard=si para metricas fuertes."),
        ]
    )
    st.caption(caption_for(data.resumen, "resumen"))

    top_barrios = top_f01_barrios(data.est_cat_barrio)
    if not top_barrios.empty:
        text = "; ".join(
            f"{row.barrio}: {int(row.cantidad)} registros ({row.porcentaje}%)"
            for row in top_barrios.itertuples(index=False)
        )
        st.info(f"Lectura F01: los 3 barrios con mas oferta registrada son {text}.")

    st.subheader("Mapa integrado F01/F03")
    show_f01 = st.checkbox("Mostrar F01 oferta registrada", value=True, key="panorama_f01")
    show_f03 = st.checkbox("Mostrar F03 espacios", value=True, key="panorama_f03")
    pydeck_map(prepare_f01_map(data), prepare_f03_map(data), show_f01=show_f01, show_f03=show_f03)
    st.caption(source_caption("mapa"))


def render_territorio(data: DashboardData) -> None:
    st.header("Territorio")
    st.write(TAB_INTROS["territorio"])
    categories = sorted(
        value
        for value in data.dim_categoria.get("categoria_general", pd.Series(dtype=str)).dropna().astype(str).unique()
        if value and value not in {"No gastronomico", "Requiere validacion"}
    )
    selected = st.multiselect("Categorias F01", categories, default=categories, key="territorio_categorias")
    f01_map = prepare_f01_map(data, selected)
    st.subheader("Mapa territorial")
    pydeck_map(f01_map, prepare_f03_map(data), show_f01=True, show_f03=True)
    st.caption(source_caption("mapa"))

    top_barrios = top_f01_barrios(data.est_cat_barrio, limit=15)
    horizontal_bar(
        top_barrios,
        "barrio",
        "cantidad",
        "Ranking de barrios por oferta registrada F01",
        caption=caption_for(data.est_cat_barrio, "f01"),
    )

    with st.expander("Tabla por comuna - universos separados", expanded=False):
        searchable_table(
            data.mapa_oportunidades,
            [
                "comuna",
                "cantidad_establecimientos_f01",
                "cantidad_habilitaciones_f02_con_comuna",
                "cantidad_espacios_f03",
                "cantidad_eventos_f04_aptos",
                "observaciones",
            ],
            "territorio_mapa_oportunidades",
        )
        st.caption(caption_for(data.mapa_oportunidades, "mapa_oportunidades"))


def render_dinamismo(data: DashboardData) -> None:
    st.header("Dinamismo (F02)")
    st.write(TAB_INTROS["dinamismo"])
    comparable = data.hab_anio[data.hab_anio.get("comparable_como_flujo_anual", pd.Series(dtype=str)).astype(str) == "si"].copy()
    no_comparable = data.hab_anio[data.hab_anio.get("comparable_como_flujo_anual", pd.Series(dtype=str)).astype(str) == "no"].copy()

    vertical_bar(
        comparable,
        "anio_fuente",
        "cantidad_habilitaciones",
        "Habilitaciones F02 por anio comparable",
        order=F02_SERIE_ORDER,
        caption=caption_for(data.hab_anio, "f02"),
    )

    if not no_comparable.empty:
        metric_items = []
        for row in no_comparable.itertuples(index=False):
            metric_items.append(
                (
                    f"Periodo {row.anio_fuente}",
                    f"{number(row.cantidad_habilitaciones):,}".replace(",", "."),
                    getattr(row, "nota_serie", "No comparable como flujo anual"),
                )
            )
        kpi_row(metric_items)
        st.warning("Estos periodos se separan de la serie: 2015-2018 es agregado y 2025 tiene esquema distinto.")

    left, right = st.columns(2)
    with left:
        horizontal_bar(
            data.hab_categoria,
            "categoria_gastronomica_inferida",
            "cantidad_habilitaciones",
            "Ranking por categoria corregida",
            caption=caption_for(data.hab_categoria, "f02"),
        )
    with right:
        if not data.hab_barrio.empty:
            comuna_df = data.hab_barrio[data.hab_barrio["comuna"].astype(str).isin([str(value) for value in range(1, 16)])].copy()
            total = numeric_series(data.hab_barrio["cantidad_habilitaciones"]).sum() if "cantidad_habilitaciones" in data.hab_barrio.columns else 0
            identified = numeric_series(comuna_df["cantidad_habilitaciones"]).sum() if not comuna_df.empty else 0
            coverage = (identified / total * 100) if total else 0
            st.warning(f"Cobertura territorial F02 identificada por comuna: {coverage:.1f}% del total clasificado.")
            horizontal_bar(
                comuna_df,
                "comuna",
                "cantidad_habilitaciones",
                "Habilitaciones F02 por comuna identificada",
                caption=caption_for(data.hab_barrio, "f02"),
            )

    with st.expander("Tabla de habilitaciones recientes", expanded=False):
        searchable_table(
            data.hab_recientes,
            [
                "id_habilitacion",
                "fecha_habilitacion",
                "anio_fuente",
                "descripcion_rubro_original",
                "categoria_gastronomica_inferida",
                "direccion_original",
                "barrio",
                "comuna",
                "requiere_validacion",
                "motivo_validacion",
            ],
            "dinamismo_recientes",
        )
        st.caption(caption_for(data.hab_recientes, "f02"))


def render_ecosistema(data: DashboardData) -> None:
    st.header("Ecosistema publico (F03-F05)")
    st.write(TAB_INTROS["ecosistema"])
    f03_tipo = (
        data.fact_espacios_f03.groupby("tipo_espacio", dropna=False)
        .size()
        .reset_index(name="cantidad_espacios")
        if not data.fact_espacios_f03.empty
        else pd.DataFrame()
    )
    horizontal_bar(
        f03_tipo,
        "tipo_espacio",
        "cantidad_espacios",
        "F03 por tipo de espacio",
        caption=source_caption("f03", first_value(data.fact_espacios_f03, "fecha_consulta")),
    )
    with st.expander("Listado F03 de espacios", expanded=False):
        searchable_table(
            data.fact_espacios_f03,
            [
                "id_espacio",
                "nombre",
                "tipo_espacio",
                "es_gastronomico",
                "cantidad_puestos",
                "cantidad_puestos_gastronomicos",
                "rubros_principales",
                "direccion",
                "barrio",
                "comuna",
                "calidad_geo",
            ],
            "ecosistema_f03",
        )

    eventos_aptos = filter_by_dashboard(data.fact_eventos, "si")
    eventos_validacion = filter_by_dashboard(data.fact_eventos, "requiere_validacion")
    eventos_no = filter_by_dashboard(data.fact_eventos, "no")
    kpi_row(
        [
            ("F04 aptos", len(eventos_aptos), "Eventos aptos para metricas fuertes."),
            ("F04 en validacion", len(eventos_validacion), "Eventos con validaciones pendientes."),
            ("F04 no aptos", len(eventos_no), "Eventos fuera de metricas fuertes."),
        ]
    )
    st.warning("F04 tiene N chico y cobertura parcial: usar como evidencia cualitativa, no como universo completo.")
    left, right = st.columns(2)
    with left:
        vertical_bar(data.eventos_anio, "anio", "cantidad_eventos", "F04 aptos por anio", caption=caption_for(data.eventos_anio, "f04"))
    with right:
        horizontal_bar(data.eventos_tipo, "tipo_evento", "cantidad_eventos", "F04 aptos por tipo", caption=caption_for(data.eventos_tipo, "f04"))

    with st.expander("Tabla F04 de eventos aptos", expanded=False):
        searchable_table(
            eventos_aptos,
            ["id_evento", "nombre_evento", "fecha_inicio", "fecha_fin", "tipo_evento", "barrio", "comuna", "url_fuente"],
            "ecosistema_eventos_aptos",
        )

    st.subheader("F05 fichas de programas e instrumentos")
    if data.programas_catalogo.empty:
        st.info("No hay programas aptos para mostrar.")
    for row in data.programas_catalogo.itertuples(index=False):
        program_id = getattr(row, "id_programa", "")
        with st.expander(f"{program_id} - {getattr(row, 'nombre_programa', 'Programa')}", expanded=False):
            st.markdown(f"**Objetivo:** {getattr(row, 'objetivo', 'No disponible')}")
            st.markdown(f"**Beneficiarios:** {getattr(row, 'beneficiarios', 'No disponible')}")
            st.markdown(f"**Normativa:** {getattr(row, 'normativa_relacionada', 'No disponible')}")
            url = getattr(row, "url_fuente", "No disponible")
            st.markdown(f"**URL:** {url}")
            linked = linked_events_for_program(program_id, data)
            if linked.empty:
                st.caption("Sin eventos F04 vinculados en puente_evento_programa.csv.")
            else:
                names = linked.get("nombre_evento", pd.Series(dtype=str)).astype(str).tolist()
                st.markdown("**Eventos vinculados F04:** " + " | ".join(names))
    st.caption(caption_for(data.programas_catalogo, "f05"))


def render_metodologia(data: DashboardData) -> None:
    st.header("Metodologia y calidad")
    st.write(TAB_INTROS["metodologia"])
    st.subheader("Advertencias metodologicas")
    for warning in CRITICAL_WARNINGS:
        st.warning(warning)
    st.subheader("Que NO responde este tablero")
    for item in WHAT_IT_DOES_NOT_ANSWER:
        st.markdown(f"- {item}")

    eventos_aptos = filter_by_dashboard(data.fact_eventos, "si")
    eventos_validacion = filter_by_dashboard(data.fact_eventos, "requiere_validacion")
    eventos_no = filter_by_dashboard(data.fact_eventos, "no")
    programas_aptos = filter_by_dashboard(data.fact_programas, "si")
    programas_validacion = filter_by_dashboard(data.fact_programas, "requiere_validacion")
    programas_no = filter_by_dashboard(data.fact_programas, "no")
    kpi_row(
        [
            ("F04 aptos", len(eventos_aptos), "Aptos para metrica fuerte."),
            ("F04 validacion/no", len(eventos_validacion) + len(eventos_no), "Fuera de metrica fuerte."),
            ("F05 aptos", len(programas_aptos), "Aptos como catalogo."),
            ("F05 validacion/no", len(programas_validacion) + len(programas_no), "Historicos, incompletos o en validacion."),
        ]
    )

    st.subheader("Trazabilidad por archivo analytics")
    st.dataframe(traceability_rows(), width="stretch", hide_index=True)

    with st.expander("dim_fuente", expanded=False):
        searchable_table(
            data.dim_fuente,
            ["id_fuente", "nombre_fuente", "tipo_fuente", "organismo_entidad", "url_base", "fecha_consulta", "notas"],
            "metodologia_dim_fuente",
        )

    guide = DOCS / "GUIA_FUENTES_DASHBOARD.md"
    if guide.exists():
        with st.expander("Guia de fuentes dashboard", expanded=False):
            st.markdown(guide.read_text(encoding="utf-8"))


def main() -> None:
    data = load_dashboard_data()
    render_global_header()
    tabs = st.tabs(["Panorama", "Territorio", "Dinamismo (F02)", "Ecosistema publico (F03-F05)", "Metodologia y calidad"])
    with tabs[0]:
        render_panorama(data)
    with tabs[1]:
        render_territorio(data)
    with tabs[2]:
        render_dinamismo(data)
    with tabs[3]:
        render_ecosistema(data)
    with tabs[4]:
        render_metodologia(data)


main()
