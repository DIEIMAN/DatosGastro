from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import pandas as pd

from clean_text import normalize_text

TODAY = date.today().isoformat()


@dataclass(frozen=True)
class SourceLoadResult:
    source_id: str
    path: str
    origin: str
    rows: int
    mapped_columns: str
    missing_columns: str
    extra_columns: str


SOURCE_COLUMN_CONTRACTS = {
    "F01": {
        "id_raw": ["id_raw", "id", "id_establecimiento", "registro", "nro_registro"],
        "id_fuente": ["id_fuente"],
        "nombre_original": ["nombre_original", "nombre", "establecimiento", "nombre_fantasia", "razon_social"],
        "categoria_original": ["categoria_original", "categoria", "rubro", "actividad", "tipo", "clase"],
        "direccion_original": ["direccion_original", "direccion", "domicilio", "domicilio_completo", "direccion_completa", "calle", "ubicacion"],
        "barrio_original": ["barrio_original", "barrio"],
        "comuna_original": ["comuna_original", "comuna"],
        "longitud": ["longitud", "lon", "lng", "long", "x"],
        "latitud": ["latitud", "lat", "y"],
        "fecha_extraccion": ["fecha_extraccion", "fecha_consulta", "fecha_actualizacion"],
        "calidad_dato": ["calidad_dato"],
        "requiere_validacion": ["requiere_validacion"],
        "motivo_validacion": ["motivo_validacion"],
        "observaciones_raw": ["observaciones_raw", "observaciones", "notas"],
    },
    "F02": {
        "id_raw": ["id_raw", "id", "nro_expediente", "expediente", "numero_expediente"],
        "id_fuente": ["id_fuente"],
        "anio": ["anio", "ano", "year"],
        "fecha_habilitacion": ["fecha_habilitacion", "fecha", "fecha_aprobacion", "fecha_inicio", "fecha_disposicion", "fecha_acto"],
        "rubro_original": ["rubro_original", "rubro", "actividad", "descripcion_rubro", "tipo_actividad", "descripcion", "actividad_comercial"],
        "direccion_original": ["direccion_original", "direccion", "domicilio", "domicilio_completo", "calles", "calle", "ubicacion"],
        "barrio_original": ["barrio_original", "barrio"],
        "comuna_original": ["comuna_original", "comuna"],
        "superficie": ["superficie", "superficie_m2", "metros_cuadrados"],
        "es_gastronomico": ["es_gastronomico"],
        "categoria_gastronomica_inferida": ["categoria_gastronomica_inferida", "categoria"],
        "fecha_extraccion": ["fecha_extraccion", "fecha_consulta", "fecha_actualizacion"],
        "calidad_dato": ["calidad_dato"],
        "requiere_validacion": ["requiere_validacion"],
        "motivo_validacion": ["motivo_validacion"],
        "observaciones_raw": ["observaciones_raw", "observaciones", "notas"],
    },
    "F03": {
        "id_raw": ["id_raw", "id", "id_feria", "id_mercado"],
        "id_fuente": ["id_fuente"],
        "nombre_original": ["nombre_original", "nombre", "feria", "mercado", "denominacion"],
        "tipo_original": ["tipo_original", "tipo", "clase", "categoria"],
        "direccion_original": ["direccion_original", "direccion", "domicilio", "domicilio_completo", "ubicacion"],
        "barrio_original": ["barrio_original", "barrio"],
        "comuna_original": ["comuna_original", "comuna"],
        "dias_horarios_original": ["dias_horarios_original", "dias_horarios", "horario", "horarios", "dias"],
        "gestion_original": ["gestion_original", "gestion", "administracion"],
        "fecha_extraccion": ["fecha_extraccion", "fecha_consulta", "fecha_actualizacion"],
        "calidad_dato": ["calidad_dato"],
        "requiere_validacion": ["requiere_validacion"],
        "motivo_validacion": ["motivo_validacion"],
        "observaciones_raw": ["observaciones_raw", "observaciones", "notas"],
    },
    "F04": {
        "id_raw": ["id_evento_raw", "id_raw", "id_evento"],
        "id_fuente": ["id_fuente"],
        "nombre_evento": ["nombre_evento", "nombre_original", "nombre"],
        "descripcion": ["descripcion"],
        "fecha_inicio": ["fecha_inicio"],
        "fecha_fin": ["fecha_fin"],
        "anio": ["anio", "ano"],
        "periodicidad": ["periodicidad"],
        "ubicacion_original": ["ubicacion_original", "ubicacion"],
        "direccion_original": ["direccion_original", "direccion"],
        "barrio_original": ["barrio", "barrio_original"],
        "comuna_original": ["comuna", "comuna_original"],
        "organizador_original": ["organizador", "organizador_original"],
        "tipo_organizador": ["tipo_organizador"],
        "apoyo_gcba": ["apoyo_gcba"],
        "organismo_gcba_relacionado": ["organismo_gcba_relacionado"],
        "area_gcba_relacionada": ["area_gcba_relacionada"],
        "tipo_vinculo_gcba": ["tipo_vinculo_gcba"],
        "tipo_evento": ["tipo_evento"],
        "categoria_gastronomica": ["categoria_gastronomica"],
        "gratuito": ["gratuito"],
        "requiere_inscripcion": ["requiere_inscripcion"],
        "cantidad_asistentes": ["cantidad_asistentes", "cantidad_asistentes_estimada"],
        "cantidad_puestos": ["cantidad_puestos", "cantidad_puestos_estimada"],
        "url_fuente": ["url_fuente", "url"],
        "fuente": ["fuente"],
        "tipo_fuente": ["tipo_fuente"],
        "fecha_consulta": ["fecha_consulta"],
        "calidad_dato": ["calidad_dato"],
        "requiere_validacion": ["requiere_validacion"],
        "motivo_validacion": ["motivo_validacion"],
        "apto_dashboard": ["apto_dashboard"],
        "limitaciones": ["limitaciones"],
        "observaciones_raw": ["observaciones_raw", "observaciones", "notas"],
    },
    "F05": {
        "id_raw": ["id_programa_raw", "id_raw", "id_programa"],
        "id_fuente": ["id_fuente"],
        "nombre_programa": ["nombre_programa", "nombre_original", "nombre"],
        "organismo_responsable": ["organismo_responsable"],
        "area_dependiente": ["area_dependiente"],
        "tipo_programa": ["tipo_programa"],
        "estado": ["estado"],
        "fecha_inicio": ["fecha_inicio"],
        "fecha_fin": ["fecha_fin"],
        "anio_inicio": ["anio_inicio", "anio"],
        "descripcion": ["descripcion"],
        "objetivo": ["objetivo"],
        "beneficiarios": ["beneficiarios"],
        "alcance_geografico": ["alcance_geografico"],
        "barrios_comunas": ["barrios_comunas"],
        "normativa_relacionada": ["normativa_relacionada"],
        "presupuesto": ["presupuesto"],
        "metricas_publicadas": ["metricas_publicadas"],
        "resultados_publicados": ["resultados_publicados", "resultados"],
        "url_fuente": ["url_fuente", "url"],
        "fuente": ["fuente"],
        "tipo_fuente": ["tipo_fuente"],
        "fecha_consulta": ["fecha_consulta"],
        "calidad_dato": ["calidad_dato"],
        "requiere_validacion": ["requiere_validacion"],
        "motivo_validacion": ["motivo_validacion"],
        "apto_dashboard": ["apto_dashboard"],
        "limitaciones": ["limitaciones"],
        "observaciones_raw": ["observaciones_raw", "observaciones", "notas"],
    },
}

REQUIRED_COLUMNS = {
    "F01": ["nombre_original", "categoria_original", "direccion_original", "barrio_original"],
    "F02": ["rubro_original", "direccion_original"],
    "F03": ["nombre_original", "tipo_original"],
    "F04": ["nombre_evento", "url_fuente", "apto_dashboard", "tipo_vinculo_gcba"],
    "F05": ["nombre_programa", "url_fuente", "apto_dashboard", "tipo_programa", "estado"],
}


def _column_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", normalize_text(value, case="lower", remove_accents=True))


def map_source_columns(df: pd.DataFrame, source_id: str, origin: str, path: Path) -> tuple[pd.DataFrame, SourceLoadResult]:
    contract = SOURCE_COLUMN_CONTRACTS[source_id]
    column_lookup = {_column_key(column): column for column in df.columns}
    mapped = pd.DataFrame(index=df.index)
    matched = {}

    for canonical, candidates in contract.items():
        source_column = None
        for candidate in candidates:
            source_column = column_lookup.get(_column_key(candidate))
            if source_column:
                break
        if source_column:
            mapped[canonical] = df[source_column].astype(str)
            matched[canonical] = source_column
        else:
            mapped[canonical] = ""

    mapped["id_fuente"] = mapped["id_fuente"].replace("", source_id)
    if "fecha_extraccion" in mapped.columns:
        mapped["fecha_extraccion"] = mapped["fecha_extraccion"].replace("", TODAY)
    mapped["calidad_dato"] = mapped["calidad_dato"].replace("", "media" if origin == "seed" else "alta")
    mapped["requiere_validacion"] = mapped["requiere_validacion"].replace("", "si")
    mapped["motivo_validacion"] = mapped["motivo_validacion"].replace(
        "",
        "Mapeo automatico desde seed" if origin == "seed" else "Mapeo automatico desde fuente real; revisar contrato",
    )
    mapped["origen_dato"] = "datos seed" if origin == "seed" else "datos reales parciales"
    if "id_raw" in mapped.columns:
        generated = [f"{source_id}_{idx + 1:07d}" for idx in range(len(mapped))]
        mapped["id_raw"] = mapped["id_raw"].where(mapped["id_raw"].astype(str).str.strip().ne(""), generated)

    missing = [column for column in REQUIRED_COLUMNS[source_id] if column not in matched]
    extra = [column for column in df.columns if column not in matched.values()]
    result = SourceLoadResult(
        source_id=source_id,
        path=str(path),
        origin=origin,
        rows=len(mapped),
        mapped_columns="; ".join(f"{key} <- {value}" for key, value in matched.items()),
        missing_columns="; ".join(missing),
        extra_columns="; ".join(extra[:25]),
    )
    return mapped, result
