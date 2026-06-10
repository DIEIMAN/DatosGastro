from __future__ import annotations

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
        return "datos reales completos"
    return "datos pendientes de validacion"


def eventos_por_barrio(eventos: pd.DataFrame, ubicaciones: pd.DataFrame) -> pd.DataFrame:
    if eventos.empty:
        return pd.DataFrame(columns=["barrio", "comuna", "cantidad_eventos", "estado_datos", "nota_estado_datos"])
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
    grouped["estado_datos"] = data_status(eventos)
    grouped["nota_estado_datos"] = "Reconstruido desde data/processed/fact_evento_gastronomico.csv"
    return grouped


def establecimientos_por_categoria_barrio(est: pd.DataFrame, ubicaciones: pd.DataFrame, categorias: pd.DataFrame) -> pd.DataFrame:
    if est.empty:
        return pd.DataFrame(
            columns=["barrio", "comuna", "categoria_general", "subcategoria", "cantidad_establecimientos", "estado_datos"]
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
    grouped["estado_datos"] = data_status(est)
    grouped["nota_estado_datos"] = "Reconstruido desde fact_establecimiento + dimensiones"
    return grouped.sort_values(["barrio", "cantidad_establecimientos"], ascending=[True, False])


def programas_por_anio(programas: pd.DataFrame) -> pd.DataFrame:
    if programas.empty:
        return pd.DataFrame(columns=["anio", "cantidad_programas", "estado_datos", "nota_estado_datos"])
    work = programas.copy()
    work["anio"] = work["fecha_inicio"].str.extract(r"(\d{4})", expand=False).fillna("No disponible")
    grouped = (
        work.groupby(["anio"], dropna=False)
        .agg(cantidad_programas=("id_programa", "count"), programas=("nombre_programa", lambda s: " | ".join(s)))
        .reset_index()
    )
    grouped["estado_datos"] = data_status(programas)
    grouped["nota_estado_datos"] = "Muchos programas seed no publican fecha de inicio estructurada"
    return grouped


def mapa_oportunidades(est: pd.DataFrame, eventos: pd.DataFrame, mercados: pd.DataFrame, ubicaciones: pd.DataFrame) -> pd.DataFrame:
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
                "estado_datos": data_status(est, eventos, mercados),
            }
        )
    return pd.DataFrame(rows).sort_values(["densidad_gastronomica", "cantidad_mercados_ferias"], ascending=False)


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
    return pd.DataFrame(rows, columns=["indicador", "valor", "estado_datos"]).assign(
        nota="Reconstruido automaticamente desde data/processed"
    )


def main() -> int:
    fuentes = read_processed("dim_fuente.csv")
    ubicaciones = read_processed("dim_ubicacion.csv")
    categorias = read_processed("dim_categoria_gastronomica.csv")
    est = read_processed("fact_establecimiento.csv")
    eventos = read_processed("fact_evento_gastronomico.csv")
    programas = read_processed("fact_programa_politica.csv")
    mercados = read_processed("fact_mercado_feria.csv")

    write_analytics(eventos_por_barrio(eventos, ubicaciones), "analytics_eventos_por_barrio.csv")
    write_analytics(
        establecimientos_por_categoria_barrio(est, ubicaciones, categorias),
        "analytics_establecimientos_por_categoria_barrio.csv",
    )
    write_analytics(programas_por_anio(programas), "analytics_programas_por_anio.csv")
    write_analytics(mapa_oportunidades(est, eventos, mercados, ubicaciones), "analytics_mapa_oportunidades.csv")
    write_analytics(resumen_ejecutivo(est, eventos, programas, mercados, fuentes), "analytics_resumen_ejecutivo.csv")
    print("OK analytics reconstruidas desde data/processed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
