"""DataGastro - tablero de gestion.

Principios de la interfaz:
- Cada pestana responde una pregunta de gestion, no describe una fuente.
- Concepto primero; el codigo de fuente (F01-F05) acompana entre parentesis.
- Una sola regla de lectura global; el detalle metodologico vive en Metodologia.
- Cada bloque cierra con una "Lectura" calculada desde los datos visibles.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

from dashboard.components import (
    horizontal_bar,
    kpi_row,
    lectura,
    map_legend,
    pydeck_comuna_choropleth,
    pydeck_map,
    searchable_table,
    vertical_bar,
)
from dashboard.dashboard_config import CATEGORY_COLORS, DOCS, F02_SERIE_ORDER, F02_USIG_POINT_COLOR, FIAB_POINT_COLOR
from dashboard.data_loader import (
    DashboardData,
    filter_by_dashboard,
    first_value,
    get_indicator,
    lectura_comuna_f02,
    lectura_f03,
    lectura_serie_f02,
    linked_events_for_program,
    load_dashboard_data,
    number,
    numeric_series,
    prepare_f01_map,
    prepare_f02_choropleth,
    prepare_f02_usig_map,
    prepare_f03_map,
    top_f01_barrios,
    traceability_rows,
)
from dashboard.textos import (
    ADVERTENCIAS_COMPLETAS,
    BAJADA,
    CAPTIONS,
    INTROS,
    KPI_HELP,
    KPI_LABELS,
    NO_RESPONDE,
    REGLA_DE_ORO,
    TABS,
    TITULO,
    caption_con_fecha,
)

st.set_page_config(page_title="DataGastro", layout="wide")


def fmt(value: int) -> str:
    return f"{value:,}".replace(",", ".")


def f01_legend_items(f01_map: pd.DataFrame) -> list[tuple[str, list[int]]]:
    presentes = f01_map["categoria_general"].value_counts().index.tolist() if not f01_map.empty else []
    return [(cat, CATEGORY_COLORS[cat]) for cat in presentes if cat in CATEGORY_COLORS][:8]


def render_header() -> None:
    st.title(TITULO)
    st.markdown(BAJADA)
    st.info(REGLA_DE_ORO)


def render_panorama(data: DashboardData) -> None:
    st.markdown(INTROS["panorama"])
    kpi_row(
        [
            (KPI_LABELS["f01"], fmt(get_indicator(data.resumen, "establecimientos_oferta_gastronomica_f01")), KPI_HELP["f01"]),
            (KPI_LABELS["f02"], fmt(get_indicator(data.resumen, "habilitaciones_gastronomicas_f02")), KPI_HELP["f02"]),
            (KPI_LABELS["f03"], fmt(get_indicator(data.resumen, "espacios_ferias_mercados_f03")), KPI_HELP["f03"]),
            (KPI_LABELS["f04"], fmt(get_indicator(data.resumen, "eventos_gastronomicos_reales_f04_aptos")), KPI_HELP["f04"]),
        ]
    )
    st.caption(caption_con_fecha("resumen", first_value(data.resumen, "fecha_consulta_max")))

    st.subheader("El mapa del ecosistema")
    f01_map = prepare_f01_map(data)
    f03_map = prepare_f03_map(data)
    f02_usig_map, f02_usig_report = prepare_f02_usig_map(data)
    col_a, col_b, col_c = st.columns(3)
    show_f01 = col_a.checkbox(f"Locales de la guia oficial ({len(f01_map)} puntos)", value=True, key="pan_f01")
    show_f03 = col_b.checkbox(f"Ferias, mercados y FIAB ({len(f03_map)} puntos)", value=True, key="pan_f03")
    show_f02_usig = col_c.checkbox(
        f"Habilitaciones geocodificadas USIG ({len(f02_usig_map)} puntos)",
        value=False,
        key="pan_f02_usig",
        disabled=not f02_usig_report["promovible"],
    )
    legend_items = f01_legend_items(f01_map) if show_f01 else []
    if show_f03:
        legend_items = legend_items + [("Ferias/mercados/FIAB", FIAB_POINT_COLOR)]
    if show_f02_usig:
        legend_items = legend_items + [("Habilitaciones F02 USIG", F02_USIG_POINT_COLOR)]
    if legend_items:
        map_legend(legend_items)
    pydeck_map(f01_map, f03_map, f02_usig_map, show_f01=show_f01, show_f03=show_f03, show_f02_usig=show_f02_usig)
    st.caption(CAPTIONS["mapa"])
    if f02_usig_report["total"]:
        st.caption(
            f"{CAPTIONS['f02_usig']} Cache: {int(f02_usig_report['exacta'])} exactas, "
            f"{int(f02_usig_report['aproximada'])} aproximadas, tasa exacta {float(f02_usig_report['exact_rate']):.1f}%."
        )
    else:
        st.caption("F02 USIG pendiente: ejecutar `python src/geocode_usig.py --solo-pendientes` para construir `data/processed/geo_cache.csv`.")

    lecturas = []
    top_barrios = top_f01_barrios(data.est_cat_barrio)
    if not top_barrios.empty:
        share = top_barrios["porcentaje"].sum()
        nombres = ", ".join(top_barrios["barrio"].tolist())
        lecturas.append(f"{nombres} concentran el {share:.0f}% de la oferta registrada en la guia oficial.")
    serie = lectura_serie_f02(data.hab_anio)
    if serie:
        lecturas.append(serie)
    f03_txt = lectura_f03(data.fact_espacios_f03)
    if f03_txt:
        lecturas.append(f03_txt)
    for texto in lecturas:
        lectura(texto)


def render_territorio(data: DashboardData) -> None:
    st.markdown(INTROS["territorio"])

    vista = st.radio(
        "Que queres ver en el mapa",
        ["Locales y espacios (puntos exactos)", "Intensidad de habilitaciones por comuna"],
        horizontal=True,
        key="terr_vista",
    )
    if vista == "Locales y espacios (puntos exactos)":
        categorias = sorted(
            value
            for value in data.dim_categoria.get("categoria_general", pd.Series(dtype=str)).dropna().astype(str).unique()
            if value and value not in {"No gastronomico", "Requiere validacion", "Comercio alimenticio minorista"}
        )
        seleccion = st.multiselect("Filtrar por tipo de local", categorias, default=categorias, key="terr_cat")
        f01_map = prepare_f01_map(data, seleccion)
        f03_map = prepare_f03_map(data)
        f02_usig_map, f02_usig_report = prepare_f02_usig_map(data)
        show_f02_usig = st.checkbox(
            f"Sumar habilitaciones geocodificadas (USIG) ({len(f02_usig_map)} puntos)",
            value=False,
            key="terr_f02_usig",
            disabled=not f02_usig_report["promovible"],
        )
        legend_items = f01_legend_items(f01_map) + [("Ferias/mercados/FIAB", FIAB_POINT_COLOR)]
        if show_f02_usig:
            legend_items.append(("Habilitaciones F02 USIG", F02_USIG_POINT_COLOR))
        map_legend(legend_items)
        pydeck_map(f01_map, f03_map, f02_usig_map, show_f01=True, show_f03=True, show_f02_usig=show_f02_usig)
        st.caption(CAPTIONS["mapa"])
        if f02_usig_report["total"]:
            st.caption(
                f"{CAPTIONS['f02_usig']} Cache: {int(f02_usig_report['exacta'])} exactas, "
                f"{int(f02_usig_report['aproximada'])} aproximadas, tasa exacta {float(f02_usig_report['exact_rate']):.1f}%."
            )
    else:
        geo_comunas, coverage = prepare_f02_choropleth(data)
        pydeck_comuna_choropleth(geo_comunas, coverage)
        st.caption(CAPTIONS["coropleta"])
        comuna_txt = lectura_comuna_f02(data.hab_barrio)
        if comuna_txt:
            lectura(comuna_txt + f" La comuna se conoce en el {coverage:.0f}% de los registros: el resto no entra en esta vista.")

    st.divider()
    left, right = st.columns(2)
    with left:
        top_barrios = top_f01_barrios(data.est_cat_barrio, limit=15)
        horizontal_bar(
            top_barrios,
            "barrio",
            "cantidad",
            "Barrios con mas oferta registrada",
            caption=caption_con_fecha("f01", first_value(data.est_cat_barrio, "fecha_consulta_max")),
        )
    with right:
        if not data.hab_barrio.empty:
            comuna_df = data.hab_barrio[data.hab_barrio["comuna"].astype(str).isin([str(v) for v in range(1, 16)])].copy()
            horizontal_bar(
                comuna_df,
                "comuna",
                "cantidad_habilitaciones",
                "Comunas con mas habilitaciones aprobadas",
                caption=caption_con_fecha("f02_comuna", first_value(data.hab_barrio, "fecha_consulta_max")),
            )

    with st.expander("Tabla por comuna: los cuatro universos lado a lado", expanded=False):
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
            "terr_tabla",
        )
        st.caption(CAPTIONS["territorio_tabla"])


def render_dinamismo(data: DashboardData) -> None:
    st.markdown(INTROS["dinamismo"])

    comparable = data.hab_anio[data.hab_anio.get("comparable_como_flujo_anual", pd.Series(dtype=str)).astype(str) == "si"].copy()
    no_comparable = data.hab_anio[data.hab_anio.get("comparable_como_flujo_anual", pd.Series(dtype=str)).astype(str) == "no"].copy()

    vertical_bar(
        comparable,
        "anio_fuente",
        "cantidad_habilitaciones",
        "Habilitaciones gastronomicas aprobadas por anio",
        order=F02_SERIE_ORDER,
        caption=caption_con_fecha("f02_serie", first_value(data.hab_anio, "fecha_consulta_max")),
    )
    serie_txt = lectura_serie_f02(data.hab_anio)
    if serie_txt:
        lectura(serie_txt)

    if not no_comparable.empty:
        with st.expander("Por que faltan 2015-2018 y 2025 en el grafico", expanded=False):
            for row in no_comparable.itertuples(index=False):
                st.markdown(
                    f"- **{row.anio_fuente}** ({fmt(number(row.cantidad_habilitaciones))} registros): "
                    f"{getattr(row, 'nota_serie', 'no comparable como flujo anual')}"
                )

    st.divider()
    left, right = st.columns(2)
    with left:
        horizontal_bar(
            data.hab_categoria,
            "categoria_gastronomica_inferida",
            "cantidad_habilitaciones",
            "Que tipo de gastronomia se habilita",
            caption=caption_con_fecha("f02", first_value(data.hab_categoria, "fecha_consulta_max")),
        )
    with right:
        if not data.hab_barrio.empty:
            comuna_df = data.hab_barrio[data.hab_barrio["comuna"].astype(str).isin([str(v) for v in range(1, 16)])].copy()
            total = numeric_series(data.hab_barrio["cantidad_habilitaciones"]).sum() if "cantidad_habilitaciones" in data.hab_barrio.columns else 0
            identificado = numeric_series(comuna_df["cantidad_habilitaciones"]).sum() if not comuna_df.empty else 0
            cobertura = (identificado / total * 100) if total else 0
            horizontal_bar(
                comuna_df,
                "comuna",
                "cantidad_habilitaciones",
                f"Donde se habilita (comuna conocida en {cobertura:.0f}% de los casos)",
                caption=caption_con_fecha("f02_comuna", first_value(data.hab_barrio, "fecha_consulta_max")),
            )

    with st.expander("Ultimas habilitaciones con fecha (500)", expanded=False):
        searchable_table(
            data.hab_recientes,
            [
                "fecha_habilitacion",
                "anio_fuente",
                "descripcion_rubro_original",
                "categoria_gastronomica_inferida",
                "direccion_original",
                "comuna",
                "requiere_validacion",
            ],
            "din_recientes",
        )
        st.caption(caption_con_fecha("f02", first_value(data.hab_recientes, "fecha_consulta_max")))


def render_ecosistema(data: DashboardData) -> None:
    st.markdown(INTROS["ecosistema"])

    st.subheader("La red de mercados, ferias y abastecimiento barrial")
    f03_tipo = (
        data.fact_espacios_f03.groupby("tipo_espacio", dropna=False).size().reset_index(name="cantidad_espacios")
        if not data.fact_espacios_f03.empty
        else pd.DataFrame()
    )
    horizontal_bar(
        f03_tipo,
        "tipo_espacio",
        "cantidad_espacios",
        "Espacios por tipo",
        caption=caption_con_fecha("f03", first_value(data.fact_espacios_f03, "fecha_consulta")),
    )
    f03_txt = lectura_f03(data.fact_espacios_f03)
    if f03_txt:
        lectura(f03_txt)
    with st.expander("Listado de espacios", expanded=False):
        searchable_table(
            data.fact_espacios_f03,
            ["nombre", "tipo_espacio", "es_gastronomico", "cantidad_puestos", "rubros_principales", "direccion", "barrio", "comuna"],
            "eco_f03",
        )

    st.divider()
    st.subheader("El calendario de eventos gastronomicos")
    eventos_aptos = filter_by_dashboard(data.fact_eventos, "si")
    eventos_resto = len(data.fact_eventos) - len(eventos_aptos) if not data.fact_eventos.empty else 0
    st.markdown(
        f"Se relevaron **{len(data.fact_eventos)}** eventos vinculados a la politica gastronomica; "
        f"**{len(eventos_aptos)}** estan verificados con fecha completa y vinculo confirmado, y entran en los graficos. "
        f"Los otros {eventos_resto} quedan como registro cualitativo."
    )
    left, right = st.columns(2)
    with left:
        vertical_bar(
            data.eventos_anio,
            "anio",
            "cantidad_eventos",
            "Eventos verificados por anio",
            caption=caption_con_fecha("f04", first_value(data.eventos_anio, "fecha_consulta_max")),
        )
    with right:
        horizontal_bar(
            data.eventos_tipo,
            "tipo_evento",
            "cantidad_eventos",
            "Eventos verificados por tipo",
            caption=caption_con_fecha("f04", first_value(data.eventos_tipo, "fecha_consulta_max")),
        )
    st.caption("Inventario chico y parcial: leer como evidencia de que existe un calendario sostenido, no como tendencia estadistica.")
    with st.expander("Eventos verificados", expanded=False):
        searchable_table(
            eventos_aptos,
            ["nombre_evento", "fecha_inicio", "fecha_fin", "tipo_evento", "barrio", "url_fuente"],
            "eco_f04",
        )

    st.divider()
    st.subheader("Los programas e instrumentos de la Ciudad")
    if data.programas_catalogo.empty:
        st.info("No hay programas verificados para mostrar.")
    for row in data.programas_catalogo.itertuples(index=False):
        program_id = getattr(row, "id_programa", "")
        nombre = getattr(row, "nombre_programa", "Programa")
        estado = getattr(row, "estado", "")
        with st.expander(f"{nombre} ({estado})" if estado else str(nombre), expanded=False):
            st.markdown(f"**Objetivo:** {getattr(row, 'objetivo', 'No disponible')}")
            st.markdown(f"**Beneficiarios:** {getattr(row, 'beneficiarios', 'No disponible')}")
            st.markdown(f"**Normativa:** {getattr(row, 'normativa_relacionada', 'No disponible')}")
            st.markdown(f"**Fuente:** {getattr(row, 'url_fuente', 'No disponible')}")
            linked = linked_events_for_program(program_id, data)
            if not linked.empty:
                names = linked.get("nombre_evento", pd.Series(dtype=str)).astype(str).tolist()
                st.markdown("**Eventos del programa:** " + " | ".join(sorted(set(names))))
    st.caption(caption_con_fecha("f05", first_value(data.programas_catalogo, "fecha_consulta_max")))


def render_metodologia(data: DashboardData) -> None:
    st.markdown(INTROS["metodologia"])

    st.subheader("Reglas de lectura y advertencias")
    for advertencia in ADVERTENCIAS_COMPLETAS:
        st.markdown(f"- {advertencia}")

    st.subheader("Preguntas que este tablero NO responde todavia")
    for item in NO_RESPONDE:
        st.markdown(f"- {item}")

    st.subheader("Aptitud de los relevamientos manuales")
    eventos_aptos = filter_by_dashboard(data.fact_eventos, "si")
    programas_aptos = filter_by_dashboard(data.fact_programas, "si")
    kpi_row(
        [
            ("Eventos verificados (F04)", len(eventos_aptos), "apto_dashboard = si, fecha completa y vinculo confirmado."),
            ("Eventos cualitativos (F04)", len(data.fact_eventos) - len(eventos_aptos), "En validacion o sin vinculo confirmado; fuera de graficos."),
            ("Programas verificados (F05)", len(programas_aptos), "Fichas con vigencia clara."),
            ("Programas cualitativos (F05)", len(data.fact_programas) - len(programas_aptos), "Historicos, incompletos o en validacion."),
        ]
    )

    st.subheader("Trazabilidad por archivo")
    st.dataframe(traceability_rows(), width="stretch", hide_index=True)

    with st.expander("Catalogo de fuentes (dim_fuente)", expanded=False):
        searchable_table(
            data.dim_fuente,
            ["id_fuente", "nombre_fuente", "tipo_fuente", "organismo_entidad", "url_base", "fecha_consulta", "notas"],
            "met_fuentes",
        )

    guide = DOCS / "GUIA_FUENTES_DASHBOARD.md"
    if guide.exists():
        with st.expander("Guia de fuentes para dashboard", expanded=False):
            st.markdown(guide.read_text(encoding="utf-8"))
    st.caption("Validacion del modelo: `python src/validate_model.py --strict-real` debe terminar sin errores.")


def main() -> None:
    data = load_dashboard_data()
    render_header()
    tabs = st.tabs(TABS)
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
