from __future__ import annotations

import argparse

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
        if "origen_dato" in frame.columns:
            values.extend(frame["origen_dato"].dropna().astype(str).tolist())
    if not values:
        return "datos pendientes de validacion"
    if all(value == "datos seed" for value in values):
        return "datos seed"
    if any("datos reales" in value for value in values) and any(value == "datos seed" for value in values):
        return "datos reales parciales"
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
    elif status == "datos reales" and has_urls:
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


def strict_real_errors(analytics: dict[str, pd.DataFrame]) -> list[str]:
    errors = []
    important = {
        "analytics_establecimientos_por_categoria_barrio.csv",
        "analytics_eventos_por_barrio.csv",
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
    if eventos.empty:
        return pd.DataFrame(columns=["barrio", "comuna", "cantidad_eventos"])
    merged = eventos.merge(ubicaciones[["id_ubicacion", "barrio", "comuna"]], on="id_ubicacion", how="left")
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
            eventos,
            method="Conteo de eventos por ubicacion normalizada.",
            limitations="Eventos seed no representan agenda completa; eventos sin sede fija usan U00000.",
            source_catalog=fuentes,
        ),
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


def programas_por_anio(programas: pd.DataFrame, fuentes: pd.DataFrame) -> pd.DataFrame:
    if programas.empty:
        return pd.DataFrame(columns=["anio", "cantidad_programas"])
    work = programas.copy()
    work["anio"] = work["fecha_inicio"].str.extract(r"(\d{4})", expand=False).fillna("No disponible")
    grouped = (
        work.groupby(["anio"], dropna=False)
        .agg(cantidad_programas=("id_programa", "count"), programas=("nombre_programa", lambda s: " | ".join(s)))
        .reset_index()
    )
    return attach_metadata(
        grouped,
        traceability_metadata(
            programas,
            method="Conteo de programas segun anio extraido de fecha_inicio.",
            limitations="Muchos programas seed no publican fecha de inicio estructurada.",
            source_catalog=fuentes,
        ),
    )


def mapa_oportunidades(est: pd.DataFrame, eventos: pd.DataFrame, mercados: pd.DataFrame, ubicaciones: pd.DataFrame, fuentes: pd.DataFrame) -> pd.DataFrame:
    barrios = ubicaciones[["barrio", "comuna"]].drop_duplicates()
    barrios = barrios[barrios["barrio"].ne("No determinado")]
    est_count = est.merge(ubicaciones[["id_ubicacion", "barrio"]], on="id_ubicacion", how="left").groupby("barrio").size()
    evt_count = eventos.merge(ubicaciones[["id_ubicacion", "barrio"]], on="id_ubicacion", how="left").groupby("barrio").size()
    mer_count = mercados.merge(ubicaciones[["id_ubicacion", "barrio"]], on="id_ubicacion", how="left").groupby("barrio").size()
    rows = []
    for _, row in barrios.iterrows():
        barrio = row["barrio"]
        rows.append(
            {
                "barrio": barrio,
                "comuna": row["comuna"],
                "densidad_gastronomica": int(est_count.get(barrio, 0)),
                "cantidad_eventos": int(evt_count.get(barrio, 0)),
                "cantidad_mercados_ferias": int(mer_count.get(barrio, 0)),
                "presencia_de_polos": "Requiere validacion",
                "nivel_actividad_gastronomica": "alto" if int(est_count.get(barrio, 0)) + int(mer_count.get(barrio, 0)) >= 2 else "bajo/muestra seed",
                "oportunidades_detectadas": "Geocodificar, validar vigencia y cruzar con habilitaciones AGC",
                "observaciones": "Calculado sobre processed; interpretar segun estado_datos",
            }
        )
    df = pd.DataFrame(rows).sort_values(["densidad_gastronomica", "cantidad_mercados_ferias"], ascending=False)
    return attach_metadata(
        df,
        traceability_metadata(
            est,
            eventos,
            mercados,
            method="Cruce territorial de establecimientos, eventos y mercados/ferias.",
            limitations="No usar para decisiones si alguna entrada es seed o no tiene geocodificacion validada.",
            source_catalog=fuentes,
        ),
    )


def resumen_ejecutivo(est: pd.DataFrame, eventos: pd.DataFrame, programas: pd.DataFrame, mercados: pd.DataFrame, fuentes: pd.DataFrame) -> pd.DataFrame:
    status = data_status(est, eventos, programas, mercados)
    rows = [
        ("fuentes_relevadas", len(fuentes), status),
        ("establecimientos_modelados", len(est), status),
        ("eventos_modelados", len(eventos), status),
        ("programas_modelados", len(programas), status),
        ("mercados_ferias_modelados", len(mercados), status),
        ("registros_que_requieren_validacion", sum((df.get("requiere_validacion", pd.Series(dtype=str)) == "si").sum() for df in (est, eventos, programas, mercados)), status),
    ]
    df = pd.DataFrame(rows, columns=["indicador", "valor", "estado_datos"])
    return attach_metadata(
        df.drop(columns=["estado_datos"]),
        traceability_metadata(
            est,
            eventos,
            programas,
            mercados,
            method="Resumen de conteos principales del modelo procesado.",
            limitations="No presentar como dashboard real si estado_datos no es datos reales.",
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
    eventos = read_processed("fact_evento_gastronomico.csv")
    programas = read_processed("fact_programa_politica.csv")
    mercados = read_processed("fact_mercado_feria.csv")

    analytics = {
        "analytics_eventos_por_barrio.csv": eventos_por_barrio(eventos, ubicaciones, fuentes),
        "analytics_establecimientos_por_categoria_barrio.csv": establecimientos_por_categoria_barrio(est, ubicaciones, categorias, fuentes),
        "analytics_programas_por_anio.csv": programas_por_anio(programas, fuentes),
        "analytics_mapa_oportunidades.csv": mapa_oportunidades(est, eventos, mercados, ubicaciones, fuentes),
        "analytics_resumen_ejecutivo.csv": resumen_ejecutivo(est, eventos, programas, mercados, fuentes),
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
