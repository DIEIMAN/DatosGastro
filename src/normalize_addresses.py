from __future__ import annotations

import hashlib
from dataclasses import dataclass

from clean_text import normalize_text, strip_accents
from config import BARRIO_COMUNA

USIG_URL = "https://servicios.usig.buenosaires.gob.ar/normalizar/"
UNKNOWN_LOCATION_ID = "U00000"


def _key(value: str) -> str:
    return strip_accents(value).lower().replace(".", "").strip()


BARRIO_ALIASES = {
    _key("Agronomía"): "Agronomia",
    _key("Nuñez"): "Nunez",
    _key("Núñez"): "Nunez",
    _key("Constitución"): "Constitucion",
    _key("Monserrat"): "Monserrat",
    _key("Montserrat"): "Monserrat",
    _key("San Cristóbal"): "San Cristobal",
    _key("San Cristobal"): "San Cristobal",
    _key("San Nicolás"): "San Nicolas",
    _key("San Nicolas"): "San Nicolas",
    _key("Vélez Sarsfield"): "Velez Sarsfield",
    _key("Villa Ortúzar"): "Villa Ortuzar",
    _key("Villa Pueyrredón"): "Villa Pueyrredon",
}
for _barrio in BARRIO_COMUNA:
    BARRIO_ALIASES.setdefault(_key(_barrio), _barrio)

AMBIGUOUS_BARRIOS = {
    _key("Retiro/San Nicolas"): "Barrio compuesto Retiro/San Nicolas; requiere elegir uno con direccion o geocodificacion.",
    _key("Retiro / San Nicolas"): "Barrio compuesto Retiro/San Nicolas; requiere elegir uno con direccion o geocodificacion.",
    _key("Retiro-San Nicolas"): "Barrio compuesto Retiro/San Nicolas; requiere elegir uno con direccion o geocodificacion.",
}


@dataclass(frozen=True)
class BarrioNormalizado:
    barrio: str
    comuna: str
    requiere_validacion: str
    motivo_validacion: str


def normalize_barrio(value) -> str | None:
    text = normalize_text(value)
    if not text:
        return None
    key = _key(text)
    if key in AMBIGUOUS_BARRIOS:
        return None
    return BARRIO_ALIASES.get(key)


def infer_comuna_from_barrio(value) -> str | None:
    barrio = normalize_barrio(value)
    if not barrio:
        return None
    return BARRIO_COMUNA.get(barrio)


def barrio_requires_validation(value) -> tuple[str, str]:
    text = normalize_text(value)
    key = _key(text)
    if not text:
        return "si", "Barrio no informado"
    if key in AMBIGUOUS_BARRIOS:
        return "si", AMBIGUOUS_BARRIOS[key]
    if normalize_barrio(text) is None:
        return "si", "Barrio no matchea catalogo CABA Ley 2650"
    return "no", ""


def normalize_barrio_record(value) -> BarrioNormalizado:
    barrio = normalize_barrio(value)
    requiere, motivo = barrio_requires_validation(value)
    if barrio is None:
        return BarrioNormalizado("No determinado", "No determinada", requiere, motivo)
    return BarrioNormalizado(barrio, BARRIO_COMUNA[barrio], requiere, motivo)


def make_location_id(address, barrio=None) -> str:
    address_text = normalize_text(address, case="upper")
    barrio_text = normalize_text(barrio or "")
    if not address_text or address_text in {"A RELEVAR", "NO DISPONIBLE", "NO DETERMINADO"}:
        return UNKNOWN_LOCATION_ID
    digest = hashlib.sha1(f"{address_text}|{barrio_text}".encode("utf-8")).hexdigest()[:5].upper()
    return f"U{digest}"


def normalize_address_offline(address, barrio=None) -> dict:
    barrio_info = normalize_barrio_record(barrio)
    address_text = normalize_text(address, case="upper")
    if not address_text or address_text in {"A RELEVAR", "NO DISPONIBLE", "NO DETERMINADO"}:
        return {
            "id_ubicacion": UNKNOWN_LOCATION_ID,
            "direccion_original": normalize_text(address),
            "direccion_normalizada": "No determinada",
            "barrio": "No determinado",
            "comuna": "No determinada",
            "latitud": "No disponible",
            "longitud": "No disponible",
            "codigo_postal": "No disponible",
            "zona": "No clasificada",
            "calidad_geo": "sin_geo",
            "requiere_validacion": "si",
            "motivo_validacion": "Ubicacion no determinada; preparada para geocodificacion futura con USIG",
        }
    requiere = barrio_info.requiere_validacion
    motivo = barrio_info.motivo_validacion
    if requiere == "no":
        requiere = "si"
        motivo = "Geocodificacion pendiente con USIG"
    return {
        "id_ubicacion": make_location_id(address_text, barrio_info.barrio),
        "direccion_original": normalize_text(address),
        "direccion_normalizada": "Pendiente USIG",
        "barrio": barrio_info.barrio,
        "comuna": barrio_info.comuna,
        "latitud": "No disponible",
        "longitud": "No disponible",
        "codigo_postal": "No disponible",
        "zona": "No clasificada",
        "calidad_geo": "sin_geo",
        "requiere_validacion": requiere,
        "motivo_validacion": motivo,
    }


def normalize_address(address: str, barrio: str | None = None):
    """Normalizacion offline. USIG queda documentado para una etapa futura con internet."""
    return normalize_address_offline(address, barrio)
