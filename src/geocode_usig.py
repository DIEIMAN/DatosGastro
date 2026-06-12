from __future__ import annotations

import argparse
import time
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd
import requests

from clean_text import normalize_text
from config import DATA_PROCESSED

USIG_URL = "https://servicios.usig.buenosaires.gob.ar/normalizar/"
CACHE_PATH = DATA_PROCESSED / "geo_cache.csv"
CACHE_COLUMNS = [
    "direccion_original",
    "direccion_normalizada",
    "latitud",
    "longitud",
    "barrio_usig",
    "comuna_usig",
    "precision",
    "estado",
    "fecha_consulta",
]

CABA_LAT_MIN = -34.75
CABA_LAT_MAX = -34.50
CABA_LON_MIN = -58.55
CABA_LON_MAX = -58.30
REQUEST_INTERVAL_SECONDS = 0.25
REQUEST_TIMEOUT_SECONDS = 10


@dataclass(frozen=True)
class GeocodeResult:
    direccion_original: str
    direccion_normalizada: str
    latitud: str
    longitud: str
    barrio_usig: str
    comuna_usig: str
    precision: str
    estado: str
    fecha_consulta: str

    def as_row(self) -> dict[str, str]:
        return {
            "direccion_original": self.direccion_original,
            "direccion_normalizada": self.direccion_normalizada,
            "latitud": self.latitud,
            "longitud": self.longitud,
            "barrio_usig": self.barrio_usig,
            "comuna_usig": self.comuna_usig,
            "precision": self.precision,
            "estado": self.estado,
            "fecha_consulta": self.fecha_consulta,
        }


def cache_key(value: object) -> str:
    return normalize_text(value, case="upper", remove_accents=True)


def in_caba_bounds(lat: float | None, lon: float | None) -> bool:
    return (
        lat is not None
        and lon is not None
        and CABA_LAT_MIN <= lat <= CABA_LAT_MAX
        and CABA_LON_MIN <= lon <= CABA_LON_MAX
    )


def parse_float(value: object) -> float | None:
    text = normalize_text(value)
    if not text or text in {"No disponible", "No determinada", "No determinado"}:
        return None
    try:
        return float(text.replace(",", "."))
    except ValueError:
        return None


def format_coordinate(value: float | None) -> str:
    if value is None:
        return ""
    return f"{value:.8f}".rstrip("0").rstrip(".")


def read_cache(path: Path = CACHE_PATH) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=CACHE_COLUMNS)
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    for column in CACHE_COLUMNS:
        if column not in df.columns:
            df[column] = ""
    return df[CACHE_COLUMNS].drop_duplicates("direccion_original", keep="last")


def write_cache(cache: pd.DataFrame, path: Path = CACHE_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    for column in CACHE_COLUMNS:
        if column not in cache.columns:
            cache[column] = ""
    cache[CACHE_COLUMNS].drop_duplicates("direccion_original", keep="last").to_csv(path, index=False, encoding="utf-8")


def _first_item(payload: Any) -> dict[str, Any] | None:
    if isinstance(payload, dict):
        for key in ("direccionesNormalizadas", "direcciones", "resultados", "data"):
            value = payload.get(key)
            if isinstance(value, list) and value:
                return value[0] if isinstance(value[0], dict) else None
        return payload
    if isinstance(payload, list) and payload and isinstance(payload[0], dict):
        return payload[0]
    return None


def _nested_value(item: dict[str, Any], *paths: tuple[str, ...]) -> Any:
    for path in paths:
        current: Any = item
        for key in path:
            if not isinstance(current, dict) or key not in current:
                current = None
                break
            current = current[key]
        if current not in (None, ""):
            return current
    return ""


def parse_usig_payload(address: str, payload: Any, fecha_consulta: str | None = None) -> GeocodeResult:
    fecha = fecha_consulta or date.today().isoformat()
    item = _first_item(payload)
    if not item:
        return GeocodeResult(address, "", "", "", "", "", "sin_resultado", "sin_match", fecha)

    normalized = normalize_text(
        _nested_value(item, ("direccion",), ("direccionNormalizada",), ("nombre",), ("texto",)),
    )
    precision = normalize_text(_nested_value(item, ("precision",), ("tipo",), ("clase",)), case="lower", remove_accents=True)
    lat = parse_float(_nested_value(item, ("coordenadas", "y"), ("coordenadas", "lat"), ("latitud",), ("y",)))
    lon = parse_float(_nested_value(item, ("coordenadas", "x"), ("coordenadas", "lon"), ("longitud",), ("x",)))
    barrio = normalize_text(_nested_value(item, ("barrio",), ("nombre_barrio",), ("barrioNombre",)))
    comuna = normalize_text(_nested_value(item, ("comuna",), ("comuna_usig",), ("nombre_comuna",)))

    if lat is None or lon is None:
        return GeocodeResult(address, normalized, "", "", barrio, comuna, precision or "sin_coordenadas", "sin_match", fecha)
    if not in_caba_bounds(lat, lon):
        return GeocodeResult(address, normalized, format_coordinate(lat), format_coordinate(lon), barrio, comuna, precision or "fuera_bbox", "sospechosa", fecha)

    exact_markers = {"calle_altura", "puerta", "exacta", "direccion"}
    estado = "exacta" if precision in exact_markers or any(marker in precision for marker in exact_markers) else "aproximada"
    return GeocodeResult(address, normalized, format_coordinate(lat), format_coordinate(lon), barrio, comuna, precision or estado, estado, fecha)


def geocode_address(address: str, session: requests.Session | None = None) -> GeocodeResult:
    client = session or requests.Session()
    try:
        response = client.get(
            USIG_URL,
            params={"direccion": address, "geocodificar": "true"},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        return parse_usig_payload(address, response.json())
    except Exception as exc:
        return GeocodeResult(address, "", "", "", "", "", str(exc)[:180], "error", date.today().isoformat())


def cache_index(cache: pd.DataFrame) -> set[str]:
    if cache.empty:
        return set()
    return {cache_key(value) for value in cache["direccion_original"].astype(str) if cache_key(value)}


def unique_habilitacion_addresses(path: Path = DATA_PROCESSED / "fact_habilitacion_gastronomica.csv") -> list[str]:
    if not path.exists():
        return []
    df = pd.read_csv(path, dtype=str, keep_default_na=False, usecols=lambda col: col == "direccion_original")
    if "direccion_original" not in df.columns:
        return []
    values = []
    seen: set[str] = set()
    for value in df["direccion_original"].astype(str):
        key = cache_key(value)
        if not key or key in {"NO DISPONIBLE", "NO DETERMINADO", "A RELEVAR"} or key in seen:
            continue
        seen.add(key)
        values.append(normalize_text(value))
    return values


def pending_addresses(addresses: list[str], cache: pd.DataFrame) -> list[str]:
    cached = cache_index(cache)
    return [address for address in addresses if cache_key(address) not in cached]


def status_report(cache: pd.DataFrame) -> dict[str, float | int]:
    total = len(cache)
    counts = cache["estado"].value_counts().to_dict() if not cache.empty and "estado" in cache.columns else {}
    exact = int(counts.get("exacta", 0))
    exact_rate = (exact / total * 100) if total else 0.0
    return {
        "total": total,
        "exacta": exact,
        "aproximada": int(counts.get("aproximada", 0)),
        "sin_match": int(counts.get("sin_match", 0)),
        "sospechosa": int(counts.get("sospechosa", 0)),
        "error": int(counts.get("error", 0)),
        "exact_rate": exact_rate,
    }


def print_report(cache: pd.DataFrame) -> None:
    report = status_report(cache)
    print(
        "Reporte geo_cache: "
        f"total={report['total']} exacta={report['exacta']} aproximada={report['aproximada']} "
        f"sin_match={report['sin_match']} sospechosa={report['sospechosa']} error={report['error']} "
        f"tasa_exacta={report['exact_rate']:.1f}%"
    )
    if report["total"] and report["exact_rate"] < 90:
        print("CAPA F02 USIG: fuera del mapa por tasa exacta menor a 90%.")
    elif report["total"]:
        print("CAPA F02 USIG: habilitable como capa opcional desactivada por default.")


def run(limit: int, solo_pendientes: bool) -> int:
    cache = read_cache()
    addresses = unique_habilitacion_addresses()
    to_process = pending_addresses(addresses, cache)
    if solo_pendientes:
        print(f"Direcciones unicas F02={len(addresses)}; pendientes={len(to_process)}")
    else:
        print(f"Direcciones unicas F02={len(addresses)}; ya cacheadas={len(addresses) - len(to_process)}; nuevas={len(to_process)}")
    selected = to_process[: max(limit, 0)]

    rows = cache.to_dict("records")
    last_call = 0.0
    for index, address in enumerate(selected, start=1):
        elapsed = time.monotonic() - last_call
        if last_call and elapsed < REQUEST_INTERVAL_SECONDS:
            time.sleep(REQUEST_INTERVAL_SECONDS - elapsed)
        result = geocode_address(address)
        last_call = time.monotonic()
        rows.append(result.as_row())
        print(f"{index:04d}/{len(selected):04d} {result.estado:11s} {address}")

    updated = pd.DataFrame(rows, columns=CACHE_COLUMNS)
    write_cache(updated)
    print(f"Cache escrito: {CACHE_PATH}")
    print_report(read_cache())
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Geocodifica direcciones F02 con USIG y cache persistente.")
    parser.add_argument("--limit", type=int, default=500, help="Cantidad maxima de direcciones nuevas a consultar.")
    parser.add_argument("--solo-pendientes", action="store_true", help="Procesa solo direcciones ausentes del cache.")
    args = parser.parse_args()
    return run(limit=args.limit, solo_pendientes=args.solo_pendientes)


if __name__ == "__main__":
    raise SystemExit(main())
