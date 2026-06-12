from __future__ import annotations

import argparse
import warnings

import pandas as pd

from config import DATA_ANALYTICS, DATA_PROCESSED


def read_processed(filename: str) -> pd.DataFrame:
    path = DATA_PROCESSED / filename
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def write_analytics(df: pd.DataFrame, filename: str) -> None:
    DATA_ANALYTICS.mkdir(parents=True, exist_ok=True)
    df.to_csv(DATA_ANALYTICS / filename, index=False, encoding="utf-8")
    print(f"OK {filename}: {len(df)} filas")


def data_status(*frames: pd.DataFrame) -> str:
    values = []
    for frame in frames:
        if "estado_datos" in frame.columns:
            values.extend(frame["estado_datos"].dropna().astype(str).tolist())
        elif "origen_dato" in frame.columns:
            values.extend(frame["origen_dato"].dropna().astype(str).tolist())
    if not values:
        return "datos pendientes de validacion"
    if all(value == "datos seed" for value in values):
        return "datos seed"
    if any("datos reales" in value for value in values) and any(value == "datos seed" for value in values):
        return "datos reales parciales"
    if all("datos reales semiestructurados" in value for value in values):
        return "datos reales semiestructurados"
    if all("datos reales" in value for value in values):
        return "datos reales"
    return "datos pendientes de validacion"


def traceability_metadata(*frames: pd.DataFrame, method: str, limitations: str, source_catalog: pd.DataFrame | None = None) -> dict:
    status = data_status(*frames)
    source_values = []
    url_values = []
    for frame in frames:
        if frame.empty:
            continue
        if "id_fuente" in frame.columns:
            source_values.extend(frame["id_fuente"].astype(str).tolist())
        if "url_fuente" in frame.columns:
            url_values.extend(frame["url_fuente"].astype(str).tolist())
    sources = sorted({value for value in source_values if value})
    if source_catalog is not None and not source_catalog.empty and sources:
        catalog = source_catalog[source_catalog["id_fuente"].isin(sources)] if "id_fuente" in source_catalog.columns else pd.DataFrame()
        if not catalog.empty:
            if "url_base" in catalog.columns:
                url_values.extend(catalog["url_base"].astype(str).tolist())
            date_values = catalog["fecha_consulta"].astype(str).tolist() if "fecha_consulta" in catalog.columns else []
        else:
            date_values = []
    else:
        date_values = []
    urls = sorted({value for value in url_values if value and value != "No disponible"})
    has_urls = bool(urls)
    if status == "datos seed":
        apto = "no"
    elif status == "datos reales parciales":
        apto = "no"
    elif status in {"datos reales", "datos reales semiestructurados"} and has_urls:
        apto = "si"
    else:
        apto = "no"

    return {
        "estado_datos": status,
        "fuentes_utilizadas": " | ".join(sources) if sources else "No disponible",
        "urls_fuentes": " | ".join(urls) if urls else "No disponible",
        "fecha_consulta_min": min(date_values) if date_values else "No disponible",
        "fecha_consulta_max": max(date_values) if date_values else "No disponible",
        "nota_metodologica": method,
        "limitaciones": limitations,
        "apto_dashboard": apto,
    }


def attach_metadata(df: pd.DataFrame, metadata: dict) -> pd.DataFrame:
    result = df.copy()
    for key, value in metadata.items():
        result[key] = value
    return result


def strong_events(eventos: pd.DataFrame) -> pd.DataFrame:
    if eventos.empty:
        return eventos
    result = eventos[
        (eventos.get("apto_dashboard", "").astype(str) == "si")
        & (eventos.get("requiere_validacion", "").astype(str) != "si")
        & (eventos.get("fecha_completa", "").astype(str) == "si")
    ].copy()
    if "tipo_vinculo_gcba" in result.columns:
        result = result[~result["tipo_vinculo_gcba"].astype(str).str.contains("Difusion oficial|Requiere validacion", case=False, na=False)]
    return result


def qualitative_events(eventos: pd.DataFrame) -> pd.DataFrame:
    if eventos.empty:
        return eventos
    strong_ids = set(strong_events(eventos).get("id_evento", pd.Series(dtype=str)))
    return eventos[~eventos["id_evento"].isin(strong_ids)].copy()


def strong_programs(programas: pd.DataFrame) -> pd.DataFrame:
    if programas.empty:
        return programas
    return programas[
        (programas.get("apto_dashboard", "").astype(str) == "si")
        & (programas.get("vigencia_clara", "").astype(str) == "si")
    ].copy()


def qualitative_programs(programas: pd.DataFrame) -> pd.DataFrame:
    if programas.empty:
        return programas
    strong_ids = set(strong_programs(programas).get("id_programa", pd.Series(dtype=str)))
    return programas[~programas["id_programa"].isin(strong_ids)].copy()


def strict_real_errors(analytics: dict[str, pd.DataFrame]) -> list[str]:
    errors = []
    important = {
        "analytics_establecimientos_por_categoria_barrio.csv",
        "analytics_habilitaciones_por_anio.csv",
        "analytics_habilitaciones_por_barrio.csv",
        "analytics_habilitaciones_por_categoria.csv",
        "analytics_habilitaciones_recientes.csv",
        "analytics_espacios_ferias_mercados_por_tipo.csv",
        "analytics_espacios_ferias_mercados_por_comuna.csv",
        "analytics_fiab_por_comuna.csv",
        "analytics_eventos_por_barrio.csv",
        "analytics_eventos_por_tipo.csv",
        "analytics_eventos_por_anio.csv",
        "analytics_programas_por_tipo.csv",
        "analytics_programas_por_estado.csv",
        "analytics_programas_catalogo.csv",
        "analytics_mapa_oportunidades.csv",
        "analytics_resumen_ejecutivo.csv",
    }
    required = [
        "estado_datos",
        "fuentes_utilizadas",
        "urls_fuentes",
        "fecha_consulta_min",
        "fecha_consulta_max",
        "nota_metodologica",
        "limitaciones",
        "apto_dashboard",
    ]
    for filename, df in analytics.items():
        missing = [column for column in required if column not in df.columns]
        if missing:
            errors.append(f"{filename}: faltan columnas de trazabilidad analytics {missing}")
            continue
        if filename in important:
            if df["estado_datos"].astype(str).str.contains("seed", case=False, na=False).any():
                errors.append(f"{filename}: contiene analytics basadas en seed")
            if df["apto_dashboard"].astype(str).ne("si").any():
                errors.append(f"{filename}: no es apta para dashboard en modo estricto")
            if df["fuentes_utilizadas"].astype(str).isin(["", "No disponible"]).any():
                errors.append(f"{filename}: fuentes_utilizadas vacio/no disponible")
            if df["urls_fuentes"].astype(str).isin(["", "No disponible"]).any():
                errors.append(f"{filename}: urls_fuentes vacio/no disponible")
    return errors


def eventos_por_barrio(eventos: pd.DataFrame, ubicaciones: pd.DataFrame, fuentes: pd.DataFrame) -> pd.DataFrame:
    eventos_fuertes = strong_events(eventos)
    if eventos_fuertes.empty:
        df = pd.DataFrame(
            [
                {
                    "barrio": "Sin eventos aptos",
                    "comuna": "Sin eventos aptos",
                    "cantidad_eventos": 0,
                    "cantidad_eventos_gratuitos": 0,
                    "cantidad_eventos_con_validacion": 0,
                    "tipos_eventos_principales": "Sin eventos aptos para metricas fuertes",
                }
            ]
        )
        return attach_metadata(
            df,
            {
                "estado_datos": "datos pendientes de validacion",
                "fuentes_utilizadas": "No disponible",
                "urls_fuentes": "No disponible",
                "fecha_consulta_min": "No disponible",
                "fecha_consulta_max": "No disponible",
                "nota_metodologica": "Conteo fuerte de eventos F04; solo apto_dashboard=si, sin validacion pendiente y con fecha completa.",
                "limitaciones": "F04 es relevamiento manual trazable, no universo completo de eventos.",
                "apto_dashboard": "no",
            },
        )
    merged = eventos_fuertes.merge(ubicaciones[["id_ubicacion", "barrio", "comuna"]], on="id_ubicacion", how="left", suffixes=("", "_dim"))
    merged["barrio"] = merged.get("barrio", merged.get("barrio_dim", "")).replace("", pd.NA).fillna(merged.get("barrio_dim", "No determinado"))
    merged["comuna"] = merged.get("comuna", merged.get("comuna_dim", "")).replace("", pd.NA).fillna(merged.get("comuna_dim", "No determinada"))
    grouped = (
        merged.groupby(["barrio", "comuna"], dropna=False)
        .agg(
            cantidad_eventos=("id_evento", "count"),
            cantidad_eventos_gratuitos=("gratuito", lambda s: (s == "si").sum()),
            cantidad_eventos_con_validacion=("requiere_validacion", lambda s: (s == "si").sum()),
            tipos_eventos_principales=("tipo_evento", lambda s: ", ".join(sorted(set(s.astype(str))))),
        )
        .reset_index()
    )
    return attach_metadata(
        grouped,
        traceability_metadata(
            eventos_fuertes,
            method="Conteo fuerte de eventos F04 por ubicacion normalizada.",
            limitations="Solo filas F04 apto_dashboard=si, sin validacion pendiente y con fecha completa; no representa universo completo.",
            source_catalog=fuentes,
        ),
    )


def eventos_por_tipo(eventos: pd.DataFrame, fuentes: pd.DataFrame) -> pd.DataFrame:
    eventos_fuertes = strong_events(eventos)
    if eventos_fuertes.empty:
        df = pd.DataFrame([{"tipo_evento": "Sin eventos aptos", "cantidad_eventos": 0}])
    else:
        df = (
            eventos_fuertes.groupby("tipo_evento", dropna=False)
            .agg(cantidad_eventos=("id_evento", "count"))
            .reset_index()
            .sort_values("cantidad_eventos", ascending=False)
        )
    return attach_metadata(
        df,
        traceability_metadata(
            eventos_fuertes,
            method="Conteo fuerte de eventos F04 por tipo; solo apto_dashboard=si, sin validacion pendiente y con fecha completa.",
            limitations="F04 no es dataset oficial estructurado ni universo completo de eventos.",
            source_catalog=fuentes,
        ),
    )


def eventos_por_anio(eventos: pd.DataFrame, fuentes: pd.DataFrame) -> pd.DataFrame:
    eventos_fuertes = strong_events(eventos)
    if eventos_fuertes.empty:
        df = pd.DataFrame([{"anio": "Sin eventos aptos", "cantidad_eventos": 0}])
    else:
        df = (
            eventos_fuertes.groupby("anio", dropna=False)
            .agg(cantidad_eventos=("id_evento", "count"))
            .reset_index()
            .sort_values("anio")
        )
    return attach_metadata(
        df,
        traceability_metadata(
            eventos_fuertes,
            method="Conteo fuerte de eventos F04 por anio declarado; no usa fechas incompletas.",
            limitations="F04 no representa el universo completo; no atribuir totales nacionales a CABA.",
            source_catalog=fuentes,
        ),
    )


def eventos_cualitativos(eventos: pd.DataFrame, fuentes: pd.DataFrame) -> pd.DataFrame:
    df = qualitative_events(eventos)
    keep = [
        "id_evento",
        "nombre_evento",
        "fecha_inicio",
        "fecha_fin",
        "tipo_evento",
        "tipo_vinculo_gcba",
        "requiere_validacion",
        "apto_dashboard",
        "motivo_validacion",
        "limitaciones",
        "url_fuente",
    ]
    df = df[[column for column in keep if column in df.columns]] if not df.empty else pd.DataFrame(columns=keep)
    return attach_metadata(
        df,
        {
            **traceability_metadata(
                eventos,
                method="Catalogo cualitativo de eventos F04 excluidos de metricas fuertes.",
                limitations="Incluye fechas incompletas, vinculos no confirmados, difusion oficial o validaciones pendientes.",
                source_catalog=fuentes,
            ),
            "apto_dashboard": "no",
        },
    )


def establecimientos_por_categoria_barrio(est: pd.DataFrame, ubicaciones: pd.DataFrame, categorias: pd.DataFrame, fuentes: pd.DataFrame) -> pd.DataFrame:
    if est.empty:
        return pd.DataFrame(
            columns=["barrio", "comuna", "categoria_general", "subcategoria", "cantidad_establecimientos"]
        )
    merged = est.merge(ubicaciones[["id_ubicacion", "barrio", "comuna"]], on="id_ubicacion", how="left")
    merged = merged.merge(categorias[["id_categoria", "categoria_general", "subcategoria"]], on="id_categoria", how="left")
    grouped = (
        merged.groupby(["barrio", "comuna", "categoria_general", "subcategoria"], dropna=False)
        .agg(cantidad_establecimientos=("id_establecimiento", "count"))
        .reset_index()
    )
    totals = grouped.groupby("barrio")["cantidad_establecimientos"].transform("sum")
    grouped["porcentaje_sobre_total_barrio"] = (grouped["cantidad_establecimientos"] / totals * 100).round(2)
    grouped = grouped.sort_values(["barrio", "cantidad_establecimientos"], ascending=[True, False])
    return attach_metadata(
        grouped,
        traceability_metadata(
            est,
            method="Agrupacion de establecimientos por barrio, comuna y categoria inferida.",
            limitations="Si usa seed, la muestra no representa el universo de establecimientos.",
            source_catalog=fuentes,
        ),
    )


def habilitaciones_por_anio(hab: pd.DataFrame, fuentes: pd.DataFrame) -> pd.DataFrame:
    if hab.empty:
        df = pd.DataFrame(
            [
                {
                    "anio_fuente": "Sin datos",
                    "cantidad_habilitaciones": 0,
                    "nota_serie": "Sin datos para construir serie anual",
                    "comparable_como_flujo_anual": "no",
                }
            ]
        )
    else:
        df = (
            hab.groupby(["anio_fuente"], dropna=False)
            .agg(
                cantidad_habilitaciones=("id_habilitacion", "count"),
                cantidad_con_validacion=("requiere_validacion", lambda s: (s == "si").sum()),
            )
            .reset_index()
        )
        df["anio_fuente"] = df["anio_fuente"].astype(str)
        non_comparable = df["anio_fuente"].isin(["2015-2018", "2025"])
        df["comparable_como_flujo_anual"] = "si"
        df.loc[non_comparable, "comparable_como_flujo_anual"] = "no"
        df["nota_serie"] = "Comparable como flujo anual del recurso"
        df.loc[df["anio_fuente"] == "2015-2018", "nota_serie"] = "Periodo agregado 2015-2018; no comparable como flujo anual"
        df.loc[df["anio_fuente"] == "2025", "nota_serie"] = "Recurso 2025 con esquema distinto: contiene disposiciones de varios anios; no usar como flujo anual"
    return attach_metadata(
        df,
        traceability_metadata(
            hab,
            method="Conteo de habilitaciones gastronomicas F02 por anio/periodo de recurso.",
            limitations="No representa establecimientos activos unicos; 2015-2018 es periodo agregado y 2025 no es comparable como flujo anual.",
            source_catalog=fuentes,
        ),
    )


def habilitaciones_por_barrio(hab: pd.DataFrame, fuentes: pd.DataFrame) -> pd.DataFrame:
    if hab.empty:
        df = pd.DataFrame([{"barrio": "Sin datos", "comuna": "Sin datos", "cantidad_habilitaciones": 0}])
    else:
        df = (
            hab.groupby(["barrio", "comuna"], dropna=False)
            .agg(cantidad_habilitaciones=("id_habilitacion", "count"))
            .reset_index()
            .sort_values("cantidad_habilitaciones", ascending=False)
        )
    return attach_metadata(
        df,
        traceability_metadata(
            hab,
            method="Conteo de habilitaciones gastronomicas F02 por barrio/comuna cuando la ubicacion pudo normalizarse.",
            limitations="Muchas habilitaciones pueden no tener barrio normalizado; no equivale a locales activos.",
            source_catalog=fuentes,
        ),
    )


def habilitaciones_por_categoria(hab: pd.DataFrame, fuentes: pd.DataFrame) -> pd.DataFrame:
    if hab.empty:
        df = pd.DataFrame([{"categoria_gastronomica_inferida": "Sin datos", "cantidad_habilitaciones": 0}])
    else:
        df = (
            hab.groupby(["categoria_gastronomica_inferida"], dropna=False)
            .agg(
                cantidad_habilitaciones=("id_habilitacion", "count"),
                confianza_promedio=("confianza_categoria", lambda s: round(pd.to_numeric(s, errors="coerce").mean(), 3)),
            )
            .reset_index()
            .sort_values("cantidad_habilitaciones", ascending=False)
        )
    return attach_metadata(
        df,
        traceability_metadata(
            hab,
            method="Conteo de habilitaciones F02 por categoria gastronomica inferida.",
            limitations="Categorias inferidas por keywords sobre descripcion de rubro.",
            source_catalog=fuentes,
        ),
    )


def habilitaciones_recientes(hab: pd.DataFrame, fuentes: pd.DataFrame) -> pd.DataFrame:
    if hab.empty:
        df = pd.DataFrame([{"id_habilitacion": "Sin datos", "fecha_habilitacion": "Sin datos"}])
    else:
        df = hab.copy()
        iso_dates = df["fecha_habilitacion"].astype(str).str.match(r"^\d{4}-\d{2}-\d{2}$", na=False)
        df["_fecha_sort"] = pd.NaT
        df.loc[iso_dates, "_fecha_sort"] = pd.to_datetime(df.loc[iso_dates, "fecha_habilitacion"], errors="coerce")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            df.loc[~iso_dates, "_fecha_sort"] = pd.to_datetime(df.loc[~iso_dates, "fecha_habilitacion"], errors="coerce", dayfirst=True)
        df = (
            df.sort_values(["_fecha_sort", "anio_fuente"], ascending=False)
            .drop(columns=["_fecha_sort"])
            .head(500)
        )
        keep = [
            "id_habilitacion",
            "fecha_habilitacion",
            "anio_fuente",
            "periodo_fuente",
            "descripcion_rubro_original",
            "categoria_gastronomica_inferida",
            "confianza_categoria",
            "direccion_original",
            "barrio",
            "comuna",
            "superficie",
            "requiere_validacion",
            "motivo_validacion",
        ]
        df = df[[column for column in keep if column in df.columns]]
    return attach_metadata(
        df,
        traceability_metadata(
            hab,
            method="Ultimas habilitaciones gastronomicas F02 segun fecha_habilitacion disponible.",
            limitations="No equivale a establecimientos activos; fecha puede faltar en algunos recursos.",
            source_catalog=fuentes,
        ),
    )


def espacios_ferias_mercados_por_tipo(espacios: pd.DataFrame, fuentes: pd.DataFrame) -> pd.DataFrame:
    if espacios.empty:
        df = pd.DataFrame([{"tipo_espacio": "Sin espacios", "cantidad_espacios": 0}])
    else:
        df = (
            espacios.groupby("tipo_espacio", dropna=False)
            .agg(cantidad_espacios=("id_espacio", "count"))
            .reset_index()
            .sort_values("cantidad_espacios", ascending=False)
        )
    return attach_metadata(
        df,
        traceability_metadata(
            espacios,
            method="Conteo de espacios reales F03 por tipo. Excluye padron de puestos/personas.",
            limitations="F03 tiene recursos con distinto grano; puestos individuales no cuentan como espacios.",
            source_catalog=fuentes,
        ),
    )


def espacios_ferias_mercados_por_comuna(espacios: pd.DataFrame, fuentes: pd.DataFrame) -> pd.DataFrame:
    if espacios.empty:
        df = pd.DataFrame([{"comuna": "Sin espacios", "cantidad_espacios": 0}])
    else:
        df = (
            espacios.groupby("comuna", dropna=False)
            .agg(cantidad_espacios=("id_espacio", "count"))
            .reset_index()
            .sort_values("cantidad_espacios", ascending=False)
        )
    return attach_metadata(
        df,
        traceability_metadata(
            espacios,
            method="Conteo de espacios reales F03 por comuna declarada o normalizada.",
            limitations="Mercados sin coordenadas de fuente pueden requerir validacion territorial; puestos no incluidos.",
            source_catalog=fuentes,
        ),
    )


def fiab_por_comuna(espacios: pd.DataFrame, fuentes: pd.DataFrame) -> pd.DataFrame:
    fiab = espacios[espacios.get("tipo_espacio", pd.Series(dtype=str)).astype(str) == "FIAB"].copy() if not espacios.empty else pd.DataFrame()
    if fiab.empty:
        df = pd.DataFrame([{"comuna": "Sin FIAB", "cantidad_fiab": 0}])
    else:
        df = (
            fiab.groupby("comuna", dropna=False)
            .agg(cantidad_fiab=("id_espacio", "count"))
            .reset_index()
            .sort_values("cantidad_fiab", ascending=False)
        )
    return attach_metadata(
        df,
        traceability_metadata(
            fiab,
            method="Conteo de puntos FIAB desde GeoJSON oficial por comuna.",
            limitations="FIAB es capa de abastecimiento barrial; no mezclar con ferias especializadas sin aclaracion.",
            source_catalog=fuentes,
        ),
    )


def programas_por_anio(programas: pd.DataFrame, fuentes: pd.DataFrame) -> pd.DataFrame:
    programas_fuertes = strong_programs(programas)
    if programas_fuertes.empty:
        return attach_metadata(
            pd.DataFrame([{"anio": "No usar como serie temporal", "cantidad_programas": 0, "programas": "F05 es catalogo, no serie temporal de impacto"}]),
            {
                "estado_datos": "datos reales semiestructurados",
                "fuentes_utilizadas": "F05",
                "urls_fuentes": "relevamiento_manual_trazable",
                "fecha_consulta_min": "2026-06-10",
                "fecha_consulta_max": "2026-06-10",
                "nota_metodologica": "F05 es catalogo/fichero; esta salida se conserva por compatibilidad y no debe usarse como serie temporal de impacto.",
                "limitaciones": "No inventar impacto ni vigencia desde anio_inicio.",
                "apto_dashboard": "no",
            },
        )
    work = programas_fuertes.copy()
    work["anio"] = work["anio_inicio"].where(work["anio_inicio"].astype(str).str.match(r"^\d{4}$"), "No disponible")
    grouped = (
        work.groupby(["anio"], dropna=False)
        .agg(cantidad_programas=("id_programa", "count"), programas=("nombre_programa", lambda s: " | ".join(s)))
        .reset_index()
    )
    return attach_metadata(
        grouped,
        traceability_metadata(
            programas_fuertes,
            method="Conteo descriptivo de fichas F05 aptas por anio_inicio. No es serie temporal de impacto.",
            limitations="No usar como metrica de impacto; F05 es catalogo curado.",
            source_catalog=fuentes,
        ),
    )


def programas_por_tipo(programas: pd.DataFrame, fuentes: pd.DataFrame) -> pd.DataFrame:
    programas_fuertes = strong_programs(programas)
    if programas_fuertes.empty:
        df = pd.DataFrame([{"tipo_programa": "Sin programas aptos", "cantidad_programas": 0}])
    else:
        df = (
            programas_fuertes.groupby("tipo_programa", dropna=False)
            .agg(cantidad_programas=("id_programa", "count"))
            .reset_index()
            .sort_values("cantidad_programas", ascending=False)
        )
    return attach_metadata(
        df,
        traceability_metadata(
            programas_fuertes,
            method="Catalogo F05 apto por tipo de programa/politica/instrumento.",
            limitations="No es serie temporal de impacto; no usar montos viejos como vigentes.",
            source_catalog=fuentes,
        ),
    )


def programas_por_estado(programas: pd.DataFrame, fuentes: pd.DataFrame) -> pd.DataFrame:
    programas_fuertes = strong_programs(programas)
    if programas_fuertes.empty:
        df = pd.DataFrame([{"estado": "Sin programas aptos", "cantidad_programas": 0}])
    else:
        df = (
            programas_fuertes.groupby("estado", dropna=False)
            .agg(cantidad_programas=("id_programa", "count"))
            .reset_index()
            .sort_values("cantidad_programas", ascending=False)
        )
    return attach_metadata(
        df,
        traceability_metadata(
            programas_fuertes,
            method="Catalogo F05 apto por estado declarado.",
            limitations="Vigencia tomada de ficha curada; validar antes de afirmar beneficios vigentes.",
            source_catalog=fuentes,
        ),
    )


def programas_catalogo(programas: pd.DataFrame, fuentes: pd.DataFrame) -> pd.DataFrame:
    df = strong_programs(programas)
    keep = [
        "id_programa",
        "nombre_programa",
        "tipo_programa",
        "estado",
        "organismo_responsable",
        "objetivo",
        "beneficiarios",
        "normativa_relacionada",
        "url_fuente",
        "limitaciones",
    ]
    df = df[[column for column in keep if column in df.columns]] if not df.empty else pd.DataFrame(columns=keep)
    return attach_metadata(
        df,
        traceability_metadata(
            strong_programs(programas),
            method="Catalogo de fichas F05 aptas para dashboard informativo.",
            limitations="No usar como serie temporal ni como medicion de impacto; montos y presupuestos deben validarse aparte.",
            source_catalog=fuentes,
        ),
    )


def programas_cualitativos(programas: pd.DataFrame, fuentes: pd.DataFrame) -> pd.DataFrame:
    df = qualitative_programs(programas)
    keep = [
        "id_programa",
        "nombre_programa",
        "tipo_programa",
        "estado",
        "requiere_validacion",
        "apto_dashboard",
        "motivo_validacion",
        "presupuesto",
        "limitaciones",
        "url_fuente",
    ]
    df = df[[column for column in keep if column in df.columns]] if not df.empty else pd.DataFrame(columns=keep)
    return attach_metadata(
        df,
        {
            **traceability_metadata(
                programas,
                method="Catalogo cualitativo de programas/instrumentos F05 excluidos de indicadores fuertes.",
                limitations="Incluye antecedentes historicos, instrumentos puntuales, montos desactualizables o vigencia pendiente.",
                source_catalog=fuentes,
            ),
            "apto_dashboard": "no",
        },
    )


def mapa_oportunidades(est: pd.DataFrame, hab: pd.DataFrame, eventos: pd.DataFrame, espacios: pd.DataFrame, ubicaciones: pd.DataFrame, fuentes: pd.DataFrame) -> pd.DataFrame:
    eventos_fuertes = strong_events(eventos)
    comunas = [str(value) for value in range(1, 16)]
    if not est.empty and not ubicaciones.empty and "id_ubicacion" in est.columns:
        est_by_comuna = est.merge(ubicaciones[["id_ubicacion", "comuna"]], on="id_ubicacion", how="left")
        est_count = est_by_comuna[est_by_comuna["comuna"].astype(str).isin(comunas)].groupby("comuna").size()
    else:
        est_count = pd.Series(dtype=int)
    if {"comuna"}.issubset(hab.columns):
        hab_con_comuna = hab[hab["comuna"].astype(str).isin(comunas)]
        hab_count = hab_con_comuna.groupby("comuna").size()
    else:
        hab_count = pd.Series(dtype=int)
    if {"comuna"}.issubset(espacios.columns):
        espacios_count = espacios[espacios["comuna"].astype(str).isin(comunas)].groupby("comuna").size()
    else:
        espacios_count = pd.Series(dtype=int)
    if "comuna" in eventos_fuertes.columns:
        eventos_count = eventos_fuertes[eventos_fuertes["comuna"].astype(str).isin(comunas)].groupby("comuna").size()
    else:
        eventos_count = pd.Series(dtype=int)
    rows = []
    for comuna in comunas:
        rows.append(
            {
                "comuna": comuna,
                "cantidad_establecimientos_f01": int(est_count.get(comuna, 0)),
                "cantidad_habilitaciones_f02_con_comuna": int(hab_count.get(comuna, 0)),
                "cantidad_espacios_f03": int(espacios_count.get(comuna, 0)),
                "cantidad_eventos_f04_aptos": int(eventos_count.get(comuna, 0)),
                "observaciones": "Universos separados; no sumar como establecimientos activos ni como score compuesto.",
            }
        )
    df = pd.DataFrame(rows).sort_values("comuna", key=lambda s: pd.to_numeric(s, errors="coerce"))
    return attach_metadata(
        df,
        traceability_metadata(
            est,
            hab,
            eventos_fuertes,
            espacios,
            method="Cruce territorial a nivel comuna con universos separados: F01, F02 con comuna valida, F03 espacios y F04 aptos.",
            limitations="No sumar F02 como establecimientos activos; F03 excluye puestos/personas; no contiene score ni placeholders de oportunidad.",
            source_catalog=fuentes,
        ),
    )


def resumen_ejecutivo(est: pd.DataFrame, hab: pd.DataFrame, eventos: pd.DataFrame, programas: pd.DataFrame, espacios: pd.DataFrame, puestos: pd.DataFrame, fuentes: pd.DataFrame) -> pd.DataFrame:
    status = data_status(est, hab, espacios)
    eventos_fuertes = strong_events(eventos)
    programas_fuertes = strong_programs(programas)
    mercados = espacios[espacios.get("tipo_espacio", pd.Series(dtype=str)).astype(str) == "Mercado"] if not espacios.empty else pd.DataFrame()
    ferias = espacios[espacios.get("tipo_espacio", pd.Series(dtype=str)).astype(str).str.contains("Feria", case=False, na=False)] if not espacios.empty else pd.DataFrame()
    fiab = espacios[espacios.get("tipo_espacio", pd.Series(dtype=str)).astype(str) == "FIAB"] if not espacios.empty else pd.DataFrame()
    rows = [
        ("fuentes_relevadas", len(fuentes), status, "dashboard", ""),
        ("establecimientos_oferta_gastronomica_f01", len(est), data_status(est), "dashboard", ""),
        ("habilitaciones_gastronomicas_f02", len(hab), data_status(hab), "dashboard", "Habilitaciones, no establecimientos activos"),
        ("espacios_ferias_mercados_f03", len(espacios), data_status(espacios), "dashboard", "Espacios reales; excluye puestos/personas"),
        ("mercados_f03", len(mercados), data_status(mercados), "dashboard", "Subconjunto de espacios reales F03"),
        ("ferias_f03", len(ferias), data_status(ferias), "dashboard", "Ferias especializadas/no alimentarias; no mezclar con FIAB sin aclaracion"),
        ("fiab_f03", len(fiab), data_status(fiab), "dashboard", "Puntos FIAB de abastecimiento barrial desde GeoJSON"),
        ("puestos_feria_f03", len(puestos), data_status(puestos), "auditoria_interna", "Grano puesto/persona; no usar como KPI principal ni exponer personas"),
        ("eventos_gastronomicos_reales_f04_aptos", len(eventos_fuertes), data_status(eventos_fuertes), "dashboard", ""),
        ("programas_politicas_reales_f05_aptos", len(programas_fuertes), data_status(programas_fuertes), "dashboard", ""),
        ("registros_que_requieren_validacion", sum((df.get("requiere_validacion", pd.Series(dtype=str)) == "si").sum() for df in (est, hab, eventos, programas, espacios)), status, "tecnico", ""),
    ]
    df = pd.DataFrame(rows, columns=["indicador", "valor", "estado_datos", "uso", "advertencia_grano"])
    return attach_metadata(
        df.drop(columns=["estado_datos"]),
        traceability_metadata(
            est,
            hab,
            eventos,
            programas,
            espacios,
            method="Resumen de conteos principales separados por concepto: F01 oferta, F02 habilitaciones y F03 espacios reales.",
            limitations="F03 contiene recursos con distintos niveles de grano; puestos/personas quedan como insumo tecnico y no como KPI principal.",
            source_catalog=fuentes,
        ),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Construye data/analytics desde data/processed.")
    parser.add_argument("--strict-real", action="store_true", help="Falla si analytics usa seeds o no es apta para dashboard.")
    args = parser.parse_args()

    fuentes = read_processed("dim_fuente.csv")
    ubicaciones = read_processed("dim_ubicacion.csv")
    categorias = read_processed("dim_categoria_gastronomica.csv")
    est = read_processed("fact_establecimiento.csv")
    hab = read_processed("fact_habilitacion_gastronomica.csv")
    eventos = read_processed("fact_evento_gastronomico.csv")
    programas = read_processed("fact_programa_politica.csv")
    espacios = read_processed("fact_espacio_feria_mercado.csv")
    puestos = read_processed("fact_puesto_feria.csv")

    analytics = {
        "analytics_eventos_por_barrio.csv": eventos_por_barrio(eventos, ubicaciones, fuentes),
        "analytics_eventos_por_tipo.csv": eventos_por_tipo(eventos, fuentes),
        "analytics_eventos_por_anio.csv": eventos_por_anio(eventos, fuentes),
        "analytics_eventos_cualitativos.csv": eventos_cualitativos(eventos, fuentes),
        "analytics_establecimientos_por_categoria_barrio.csv": establecimientos_por_categoria_barrio(est, ubicaciones, categorias, fuentes),
        "analytics_habilitaciones_por_anio.csv": habilitaciones_por_anio(hab, fuentes),
        "analytics_habilitaciones_por_barrio.csv": habilitaciones_por_barrio(hab, fuentes),
        "analytics_habilitaciones_por_categoria.csv": habilitaciones_por_categoria(hab, fuentes),
        "analytics_habilitaciones_recientes.csv": habilitaciones_recientes(hab, fuentes),
        "analytics_espacios_ferias_mercados_por_tipo.csv": espacios_ferias_mercados_por_tipo(espacios, fuentes),
        "analytics_espacios_ferias_mercados_por_comuna.csv": espacios_ferias_mercados_por_comuna(espacios, fuentes),
        "analytics_fiab_por_comuna.csv": fiab_por_comuna(espacios, fuentes),
        "analytics_programas_por_anio.csv": programas_por_anio(programas, fuentes),
        "analytics_programas_por_tipo.csv": programas_por_tipo(programas, fuentes),
        "analytics_programas_por_estado.csv": programas_por_estado(programas, fuentes),
        "analytics_programas_catalogo.csv": programas_catalogo(programas, fuentes),
        "analytics_programas_cualitativos.csv": programas_cualitativos(programas, fuentes),
        "analytics_mapa_oportunidades.csv": mapa_oportunidades(est, hab, eventos, espacios, ubicaciones, fuentes),
        "analytics_resumen_ejecutivo.csv": resumen_ejecutivo(est, hab, eventos, programas, espacios, puestos, fuentes),
    }
    if args.strict_real:
        errors = strict_real_errors(analytics)
        if errors:
            print("ERROR --strict-real no puede construir analytics aptas para dashboard:")
            for error in errors:
                print(f"ERROR {error}")
            return 1
    for filename, df in analytics.items():
        write_analytics(df, filename)
    print("OK analytics reconstruidas desde data/processed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
