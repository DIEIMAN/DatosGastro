from __future__ import annotations

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
        "id_fuente": ["id_fuente", "fuente"],
        "nombre_original": ["nombre_original", "nombre", "establecimiento", "nombre_fantasia", "razon_social"],
        "categoria_original": ["categoria_original", "categoria", "rubro", "actividad", "tipo", "clase"],
        "direccion_original": ["direccion_original", "direccion", "domicilio", "domicilio_completo", "calle", "ubicacion"],
        "barrio_original": ["barrio_original", "barrio"],
        "comuna_original": ["comuna_original", "comuna"],
        "fecha_extraccion": ["fecha_extraccion", "fecha_consulta", "fecha_actualizacion"],
        "calidad_dato": ["calidad_dato"],
        "requiere_validacion": ["requiere_validacion"],
        "motivo_validacion": ["motivo_validacion"],
        "observaciones_raw": ["observaciones_raw", "observaciones", "notas"],
    },
    "F02": {
        "id_raw": ["id_raw", "id", "nro_expediente", "expediente", "numero_expediente"],
        "id_fuente": ["id_fuente", "fuente"],
        "anio": ["anio", "ano", "year"],
        "fecha_habilitacion": ["fecha_habilitacion", "fecha", "fecha_aprobacion", "fecha_inicio", "fecha_disposicion", "fecha_acto"],
        "rubro_original": ["rubro_original", "rubro", "actividad", "descripcion_rubro", "tipo_actividad", "descripcion", "actividad_comercial"],
        "direccion_original": ["direccion_original", "direccion", "domicilio", "domicilio_completo", "calle", "ubicacion"],
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
        "id_fuente": ["id_fuente", "fuente"],
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
}

REQUIRED_COLUMNS = {
    "F01": ["nombre_original", "categoria_original", "direccion_original", "barrio_original"],
    "F02": ["rubro_original", "direccion_original", "fecha_habilitacion"],
    "F03": ["nombre_original", "tipo_original", "direccion_original", "barrio_original"],
}


def _column_key(value: str) -> str:
    return normalize_text(value, case="lower", remove_accents=True).replace(" ", "_")


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
