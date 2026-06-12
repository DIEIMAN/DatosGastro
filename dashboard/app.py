from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
ANALYTICS = ROOT / "data" / "analytics"
PROCESSED = ROOT / "data" / "processed"
DOCS = ROOT / "docs"

TRACE_COLUMNS = [
    "estado_datos",
    "fuentes_utilizadas",
    "urls_fuentes",
    "fecha_consulta_min",
    "fecha_consulta_max",
    "nota_metodologica",
    "limitaciones",
    "apto_dashboard",
]


st.set_page_config(page_title="DataGastro - Dashboard V1", layout="wide")


@st.cache_data(show_spinner=False)
def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def number(value: object) -> int:
    try:
        return int(float(str(value).replace(".", "").replace(",", ".")))
    except Exception:
        return 0


def numeric_series(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").fillna(0).astype(int)


def get_indicator(resumen: pd.DataFrame, indicator: str) -> int:
    if resumen.empty or "indicador" not in resumen.columns:
        return 0
    row = resumen[resumen["indicador"] == indicator]
    if row.empty:
        return 0
    return number(row.iloc[0].get("valor", 0))


def first_value(df: pd.DataFrame, column: str, default: str = "No disponible") -> str:
    if df.empty or column not in df.columns:
        return default
    values = [str(value) for value in df[column].dropna().unique() if str(value).strip()]
    return values[0] if values else default


def trace_box(df: pd.DataFrame, title: str = "Fuente y metodologia") -> None:
    with st.expander(title, expanded=False):
        if df.empty:
            st.warning("No hay datos cargados para esta seccion.")
            return
        for column in TRACE_COLUMNS:
            if column in df.columns:
                st.markdown(f"**{column}:** {first_value(df, column)}")


def section_warning(text: str) -> None:
    st.warning(text)


def filter_table(df: pd.DataFrame, columns: list[str], key: str) -> pd.DataFrame:
    if df.empty:
        st.info("No hay filas para mostrar.")
        return df
    query = st.text_input("Filtro de texto", key=key)
    view = df.copy()
    if query:
        mask = view.astype(str).apply(lambda col: col.str.contains(query, case=False, na=False)).any(axis=1)
        view = view[mask]
    available = [column for column in columns if column in view.columns]
    st.dataframe(view[available] if available else view, use_container_width=True, hide_index=True)
    return view


def bar_chart(df: pd.DataFrame, label: str, value: str, title: str, limit: int = 15) -> None:
    if df.empty or label not in df.columns or value not in df.columns:
        st.info(f"No hay datos para {title}.")
        return
    chart = df[[label, value]].copy()
    chart[value] = numeric_series(chart[value])
    chart = chart.sort_values(value, ascending=False).head(limit).set_index(label)
    st.subheader(title)
    st.bar_chart(chart)


def split_fact_by_dashboard(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if df.empty or "apto_dashboard" not in df.columns:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    apt = df[df["apto_dashboard"].astype(str) == "si"]
    validation = df[df["apto_dashboard"].astype(str) == "requiere_validacion"]
    not_apt = df[df["apto_dashboard"].astype(str) == "no"]
    return apt, validation, not_apt


resumen = read_csv(ANALYTICS / "analytics_resumen_ejecutivo.csv")
est_cat_barrio = read_csv(ANALYTICS / "analytics_establecimientos_por_categoria_barrio.csv")
hab_anio = read_csv(ANALYTICS / "analytics_habilitaciones_por_anio.csv")
hab_barrio = read_csv(ANALYTICS / "analytics_habilitaciones_por_barrio.csv")
hab_categoria = read_csv(ANALYTICS / "analytics_habilitaciones_por_categoria.csv")
hab_recientes = read_csv(ANALYTICS / "analytics_habilitaciones_recientes.csv")
eventos_anio = read_csv(ANALYTICS / "analytics_eventos_por_anio.csv")
eventos_tipo = read_csv(ANALYTICS / "analytics_eventos_por_tipo.csv")
eventos_barrio = read_csv(ANALYTICS / "analytics_eventos_por_barrio.csv")
eventos_cualitativos = read_csv(ANALYTICS / "analytics_eventos_cualitativos.csv")
programas_catalogo = read_csv(ANALYTICS / "analytics_programas_catalogo.csv")
programas_cualitativos = read_csv(ANALYTICS / "analytics_programas_cualitativos.csv")
mapa_oportunidades = read_csv(ANALYTICS / "analytics_mapa_oportunidades.csv")

fact_mercados = read_csv(PROCESSED / "fact_mercado_feria.csv")
fact_eventos = read_csv(PROCESSED / "fact_evento_gastronomico.csv")
fact_programas = read_csv(PROCESSED / "fact_programa_politica.csv")
dim_fuente = read_csv(PROCESSED / "dim_fuente.csv")

eventos_aptos, eventos_validacion, eventos_no_aptos = split_fact_by_dashboard(fact_eventos)
programas_aptos, programas_validacion, programas_no_aptos = split_fact_by_dashboard(fact_programas)

st.title("DataGastro - Dashboard V1 de validacion")
st.caption("App local para revisar metricas, fuentes, advertencias y consistencia metodologica. No es dashboard final de presentacion.")

section_warning(
    "Nunca sumar F01 + F02 como establecimientos gastronomicos. F02 son habilitaciones aprobadas, no establecimientos activos unicos."
)

tabs = st.tabs(
    [
        "Resumen",
        "F01 Oferta",
        "F02 Habilitaciones",
        "F03 Ferias/Mercados",
        "F04 Eventos",
        "F05 Programas",
        "Mapa",
        "Fuentes",
        "Chequeos",
    ]
)

with tabs[0]:
    st.header("1. Resumen ejecutivo")
    cols = st.columns(4)
    cols[0].metric("Oferta gastronomica registrada F01", get_indicator(resumen, "establecimientos_oferta_gastronomica_f01"))
    cols[1].metric("Habilitaciones gastronomicas F02", get_indicator(resumen, "habilitaciones_gastronomicas_f02"))
    cols[2].metric("Ferias y mercados F03", get_indicator(resumen, "ferias_mercados_f03"))
    cols[3].metric("Eventos F04 aptos", get_indicator(resumen, "eventos_gastronomicos_reales_f04_aptos"))

    cols = st.columns(3)
    cols[0].metric("Eventos F04 en validacion", len(eventos_validacion))
    cols[1].metric("Eventos F04 no aptos", len(eventos_no_aptos))
    cols[2].metric("Programas F05 aptos", get_indicator(resumen, "programas_politicas_reales_f05_aptos"))

    cols = st.columns(2)
    cols[0].metric("Programas F05 en validacion", len(programas_validacion))
    cols[1].metric("Programas F05 no aptos / historicos", len(programas_no_aptos))
    trace_box(resumen)
    st.dataframe(resumen, use_container_width=True, hide_index=True)

with tabs[1]:
    st.header("2. Oferta gastronomica F01")
    section_warning(
        "F01 representa registros de oferta gastronomica publicados por Buenos Aires Data. No confirma vigencia actual por registro."
    )
    if not est_cat_barrio.empty:
        top_cat = (
            est_cat_barrio.groupby("categoria_general", dropna=False)["cantidad_establecimientos"]
            .apply(lambda s: numeric_series(s).sum())
            .reset_index()
        )
        top_barrios = (
            est_cat_barrio.groupby("barrio", dropna=False)["cantidad_establecimientos"]
            .apply(lambda s: numeric_series(s).sum())
            .reset_index()
        )
        left, right = st.columns(2)
        with left:
            bar_chart(top_cat, "categoria_general", "cantidad_establecimientos", "Top categorias")
        with right:
            bar_chart(top_barrios, "barrio", "cantidad_establecimientos", "Top barrios")
    filter_table(
        est_cat_barrio,
        ["barrio", "comuna", "categoria_general", "subcategoria", "cantidad_establecimientos", "porcentaje_sobre_total_barrio"],
        "f01_filter",
    )
    trace_box(est_cat_barrio)

with tabs[2]:
    st.header("3. Habilitaciones F02")
    section_warning(
        "F02 son habilitaciones aprobadas por AGC, no establecimientos activos unicos. La clasificacion gastronomica se infiere desde la descripcion del rubro."
    )
    left, right = st.columns(2)
    with left:
        bar_chart(hab_anio, "anio_fuente", "cantidad_habilitaciones", "Habilitaciones por anio/periodo")
        bar_chart(hab_categoria, "categoria_gastronomica_inferida", "cantidad_habilitaciones", "Habilitaciones por categoria inferida")
    with right:
        bar_chart(hab_barrio, "comuna", "cantidad_habilitaciones", "Habilitaciones por comuna/barrio no normalizado")
    st.subheader("Habilitaciones recientes")
    filter_table(
        hab_recientes,
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
        ],
        "f02_recientes_filter",
    )
    trace_box(hab_anio)

with tabs[3]:
    st.header("4. Ferias y mercados F03")
    section_warning(
        "F03 integra ferias y mercados. La geometria disponible no representa necesariamente todos los espacios."
    )
    st.metric("Registros F03", len(fact_mercados))
    if not fact_mercados.empty:
        left, right = st.columns(2)
        with left:
            tipo = fact_mercados.groupby("tipo_espacio", dropna=False).size().reset_index(name="cantidad")
            bar_chart(tipo, "tipo_espacio", "cantidad", "Tipo de espacio")
        with right:
            merged = fact_mercados.copy()
            barrio_count = merged.groupby("id_ubicacion", dropna=False).size().reset_index(name="cantidad")
            st.subheader("Registros por ubicacion")
            st.dataframe(barrio_count.sort_values("cantidad", ascending=False), use_container_width=True, hide_index=True)
    filter_table(
        fact_mercados,
        ["id_mercado_feria", "nombre", "tipo_espacio", "gestion", "dias_funcionamiento", "id_fuente", "url_fuente"],
        "f03_filter",
    )

with tabs[4]:
    st.header("5. Eventos F04")
    section_warning(
        "F04 no es un dataset oficial estructurado. Es un relevamiento manual trazable de eventos vinculados a la politica gastronomica de la Ciudad. Las metricas fuertes solo usan apto_dashboard = si."
    )
    cols = st.columns(3)
    cols[0].metric("Aptos para dashboard", get_indicator(resumen, "eventos_gastronomicos_reales_f04_aptos"))
    cols[1].metric("En validacion", len(eventos_validacion))
    cols[2].metric("No aptos", len(eventos_no_aptos))
    left, right = st.columns(2)
    with left:
        bar_chart(eventos_anio, "anio", "cantidad_eventos", "Eventos aptos por anio")
        bar_chart(eventos_tipo, "tipo_evento", "cantidad_eventos", "Eventos aptos por tipo")
    with right:
        bar_chart(eventos_barrio, "barrio", "cantidad_eventos", "Eventos aptos por barrio")
    st.subheader("Eventos cualitativos / en validacion / no aptos")
    st.dataframe(eventos_cualitativos, use_container_width=True, hide_index=True)
    st.subheader("Tabla completa F04")
    filter_table(
        fact_eventos,
        [
            "id_evento",
            "nombre_evento",
            "fecha_inicio",
            "fecha_fin",
            "tipo_evento",
            "apto_dashboard",
            "requiere_validacion",
            "tipo_vinculo_gcba",
            "url_fuente",
        ],
        "f04_filter",
    )
    trace_box(eventos_tipo)

with tabs[5]:
    st.header("6. Programas F05")
    section_warning(
        "F05 es un catalogo curado de programas, politicas, normativa e instrumentos. No es una serie temporal de impacto y no tiene metricas de presupuesto/resultados estructuradas."
    )
    cols = st.columns(3)
    cols[0].metric("Aptos como catalogo", get_indicator(resumen, "programas_politicas_reales_f05_aptos"))
    cols[1].metric("En validacion", len(programas_validacion))
    cols[2].metric("No aptos / historicos", len(programas_no_aptos))
    st.subheader("Catalogo apto")
    st.dataframe(programas_catalogo, use_container_width=True, hide_index=True)
    st.subheader("Programas cualitativos / en validacion / no aptos")
    st.dataframe(programas_cualitativos, use_container_width=True, hide_index=True)
    st.subheader("Tabla completa F05")
    filter_table(
        fact_programas,
        [
            "id_programa",
            "nombre_programa",
            "tipo_programa",
            "estado",
            "apto_dashboard",
            "requiere_validacion",
            "vigencia_clara",
            "url_fuente",
        ],
        "f05_filter",
    )
    trace_box(programas_catalogo)

with tabs[6]:
    st.header("7. Mapa de oportunidades")
    section_warning(
        "La tabla distingue F01, F02 y F03. No mezclar todo en un unico score sin explicar la metodologia."
    )
    cols = [
        "barrio",
        "comuna",
        "densidad_establecimientos_f01",
        "cantidad_habilitaciones_f02",
        "cantidad_eventos",
        "cantidad_ferias_mercados_f03",
        "nivel_actividad_gastronomica",
        "oportunidades_detectadas",
    ]
    filter_table(mapa_oportunidades, cols, "mapa_filter")
    trace_box(mapa_oportunidades)

with tabs[7]:
    st.header("8. Fuentes y trazabilidad")
    st.subheader("Dimensiones de fuente")
    st.dataframe(dim_fuente, use_container_width=True, hide_index=True)
    guide = DOCS / "GUIA_FUENTES_DASHBOARD.md"
    if guide.exists():
        with st.expander("Guia de fuentes dashboard", expanded=False):
            st.markdown(guide.read_text(encoding="utf-8"))
    st.subheader("Trazabilidad por analytics")
    trace_rows = []
    for path in sorted(ANALYTICS.glob("analytics_*.csv")):
        df = read_csv(path)
        trace_rows.append(
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
    st.dataframe(pd.DataFrame(trace_rows), use_container_width=True, hide_index=True)

with tabs[8]:
    st.header("9. Chequeos de calidad")
    st.success("Resultado esperado actual: validate_model.py --strict-real => OK=39 WARNING=0 ERROR=0")
    st.subheader("Conteos por fuente")
    conteos = pd.DataFrame(
        [
            {"fuente": "F01 oferta registrada", "filas": get_indicator(resumen, "establecimientos_oferta_gastronomica_f01")},
            {"fuente": "F02 habilitaciones aprobadas", "filas": get_indicator(resumen, "habilitaciones_gastronomicas_f02")},
            {"fuente": "F03 ferias/mercados", "filas": get_indicator(resumen, "ferias_mercados_f03")},
            {"fuente": "F04 eventos aptos", "filas": get_indicator(resumen, "eventos_gastronomicos_reales_f04_aptos")},
            {"fuente": "F05 programas aptos", "filas": get_indicator(resumen, "programas_politicas_reales_f05_aptos")},
        ]
    )
    st.dataframe(conteos, use_container_width=True, hide_index=True)
    st.subheader("Aptitud F04/F05")
    st.dataframe(
        pd.DataFrame(
            [
                {"fuente": "F04", "apto": len(eventos_aptos), "requiere_validacion": len(eventos_validacion), "no_apto": len(eventos_no_aptos)},
                {"fuente": "F05", "apto": len(programas_aptos), "requiere_validacion": len(programas_validacion), "no_apto": len(programas_no_aptos)},
            ]
        ),
        use_container_width=True,
        hide_index=True,
    )
    st.markdown(
        """
        **Advertencias metodologicas principales**

        - F01 no confirma vigencia actual por registro.
        - F02 no son establecimientos activos unicos.
        - F03 tiene cobertura geografica desigual.
        - F04/F05 son relevamientos manuales trazables, no datasets oficiales estructurados.
        - Filas cualitativas o en validacion quedan fuera de metricas fuertes.
        """
    )
