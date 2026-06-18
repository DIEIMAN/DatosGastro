from __future__ import annotations

import argparse
import json
import re
import time
from dataclasses import dataclass, replace
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd
import requests
from shapely.geometry import Point, shape

from clean_text import normalize_text
from config import DATA_PROCESSED, DATA_RAW

USIG_URL = "https://servicios.usig.buenosaires.gob.ar/normalizar/"
CACHE_PATH = DATA_PROCESSED / "geo_cache.csv"
CACHE_COLUMNS = [
    "direccion_original",
    "direccion_consulta",
    "direccion_candidatas",
    "direccion_normalizada",
    "latitud",
    "longitud",
    "barrio_usig",
    "comuna_usig",
    "comuna_fuente",
    "coincide_comuna",
    "precision",
    "estado",
    "calidad_geo",
    "criterio_seleccion",
    "fecha_consulta",
]

CABA_LAT_MIN = -34.75
CABA_LAT_MAX = -34.50
CABA_LON_MIN = -58.55
CABA_LON_MAX = -58.30
REQUEST_INTERVAL_SECONDS = 0.25
REQUEST_TIMEOUT_SECONDS = 10
_COMUNA_GEOMETRIES: list[tuple[str, object]] | None = None


@dataclass(frozen=True)
class GeocodeResult:
    direccion_original: str
    direccion_consulta: str
    direccion_normalizada: str
    latitud: str
    longitud: str
    barrio_usig: str
    comuna_usig: str
    precision: str
    estado: str
    fecha_consulta: str
    direccion_candidatas: str = ""
    comuna_fuente: str = ""
    coincide_comuna: str = ""
    calidad_geo: str = ""
    criterio_seleccion: str = ""

    def as_row(self) -> dict[str, str]:
        return {
            "direccion_original": self.direccion_original,
            "direccion_consulta": self.direccion_consulta,
            "direccion_candidatas": self.direccion_candidatas,
            "direccion_normalizada": self.direccion_normalizada,
            "latitud": self.latitud,
            "longitud": self.longitud,
            "barrio_usig": self.barrio_usig,
            "comuna_usig": self.comuna_usig,
            "comuna_fuente": self.comuna_fuente,
            "coincide_comuna": self.coincide_comuna,
            "precision": self.precision,
            "estado": self.estado,
            "calidad_geo": self.calidad_geo,
            "criterio_seleccion": self.criterio_seleccion,
            "fecha_consulta": self.fecha_consulta,
        }


def cache_key(value: object) -> str:
    return normalize_text(value, case="upper", remove_accents=True)


def _dedupe_preserve_order(values: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        cleaned = re.sub(r"\s+", " ", value).strip()
        if not cleaned:
            continue
        key = cache_key(cleaned)
        if key and key not in seen:
            seen.add(key)
            result.append(cleaned)
    return result


def _clean_address_fragment(value: object) -> str:
    text = normalize_text(value, case="upper", remove_accents=True)
    text = text.replace(".", " ")
    text = re.sub(r"\bSIN\s+NUMERO\s+OFICIAL\b", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _strip_street_noise(value: str, *, expand_titles: bool) -> tuple[str, bool]:
    text = _clean_address_fragment(value)
    had_avenue = bool(re.search(r"\b(AV|AVDA|AVENIDA)\b", text))
    if expand_titles:
        text = re.sub(r"\bCNEL\b", "CORONEL", text)
        text = re.sub(r"\bGRAL\b", "GENERAL", text)
        text = re.sub(r"\bTTE\b", "TENIENTE", text)
        text = re.sub(r"\bPTE\b", "PRESIDENTE", text)
    else:
        text = re.sub(r"\b(GRAL|GENERAL|TTE|TENIENTE|CNEL|CORONEL|PTE|PRESIDENTE)\b", " ", text)
    text = re.sub(r"\b(DR|DRA|AV|AVDA|AVENIDA)\b", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text, had_avenue


def _address_part_candidates(address_part: str) -> list[str]:
    text = _clean_address_fragment(address_part)
    if not text:
        return []
    height_match = re.search(r"(\d{1,6})\s*$", text)
    if not height_match:
        return []
    height = height_match.group(1)
    street_text = re.sub(r"\s+\d{1,6}\s*$", "", text).strip(" ,")
    if not re.search(r"[A-Z]", street_text):
        return []

    candidates: list[str] = []
    if "," in street_text:
        parts = [part.strip() for part in street_text.split(",") if part.strip()]
        left, left_has_avenue = _strip_street_noise(parts[0], expand_titles=False)
        right_raw = " ".join(parts[1:])
        right, right_has_avenue = _strip_street_noise(right_raw, expand_titles=True)
        has_avenue = left_has_avenue or right_has_avenue
        if left:
            candidates.append(f"{left} {height}")
        if left and right:
            full = f"{right} {left}".strip()
            candidates.append(f"{full} {height}")
            if has_avenue:
                candidates.append(f"AV {full} {height}")
    else:
        street, has_avenue = _strip_street_noise(street_text, expand_titles=False)
        if street:
            candidates.append(f"{street} {height}")
            if has_avenue:
                candidates.append(f"AV {street} {height}")
                candidates.append(f"AVENIDA {street} {height}")
    return _dedupe_preserve_order(candidates)


def generate_f02_address_candidates(direccion_original: str) -> list[str]:
    """Genera candidatas USIG ordenadas para direcciones F02 sin perder trazabilidad."""
    parts = [part.strip() for part in str(direccion_original or "").split(";") if part.strip()]
    candidates: list[str] = []
    for part in parts:
        candidates.extend(_address_part_candidates(part))
    return _dedupe_preserve_order(candidates)


def normalize_f02_address(direccion: object) -> str:
    """Normaliza direcciones AGC invertidas antes de consultar USIG."""
    candidates = generate_f02_address_candidates(str(direccion or "").split(";")[0])
    return candidates[0] if candidates else ""


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


def _feature_comuna(properties: dict[str, Any]) -> str:
    for key in ("comuna", "COMUNA", "id", "ID", "nombre", "NOMBRE"):
        value = normalize_comuna(properties.get(key, ""))
        if value:
            return value
    return ""


def load_comuna_geometries(path: Path = DATA_RAW / "geo_comunas.geojson") -> list[tuple[str, object]]:
    global _COMUNA_GEOMETRIES
    if _COMUNA_GEOMETRIES is not None:
        return _COMUNA_GEOMETRIES
    if not path.exists():
        _COMUNA_GEOMETRIES = []
        return _COMUNA_GEOMETRIES
    data = json.loads(path.read_text(encoding="utf-8"))
    geometries: list[tuple[str, object]] = []
    for feature in data.get("features", []):
        comuna = _feature_comuna(feature.get("properties") or {})
        geometry = feature.get("geometry")
        if not comuna or not geometry:
            continue
        try:
            geometries.append((comuna, shape(geometry)))
        except Exception:
            continue
    _COMUNA_GEOMETRIES = geometries
    return geometries


def comuna_from_point(lat: float | None, lon: float | None) -> str:
    if lat is None or lon is None:
        return ""
    point = Point(lon, lat)
    for comuna, geometry in load_comuna_geometries():
        if geometry.covers(point):
            return comuna
    return ""


def read_cache(path: Path = CACHE_PATH) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=CACHE_COLUMNS)
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    for column in CACHE_COLUMNS:
        if column not in df.columns:
            df[column] = ""
    if "direccion_consulta" in df.columns:
        df["direccion_consulta"] = df["direccion_consulta"].where(
            df["direccion_consulta"].astype(str).str.strip().ne(""),
            df["direccion_original"],
        )
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


def parse_usig_payload(
    address: str,
    payload: Any,
    fecha_consulta: str | None = None,
    direccion_consulta: str | None = None,
) -> GeocodeResult:
    fecha = fecha_consulta or date.today().isoformat()
    query = direccion_consulta or address
    item = _first_item(payload)
    if not item:
        return GeocodeResult(address, query, "", "", "", "", "", "sin_resultado", "sin_match", fecha)

    normalized = normalize_text(
        _nested_value(item, ("direccion",), ("direccionNormalizada",), ("nombre",), ("texto",)),
    )
    precision = normalize_text(_nested_value(item, ("precision",), ("tipo",), ("clase",)), case="lower", remove_accents=True)
    lat = parse_float(_nested_value(item, ("coordenadas", "y"), ("coordenadas", "lat"), ("latitud",), ("y",)))
    lon = parse_float(_nested_value(item, ("coordenadas", "x"), ("coordenadas", "lon"), ("longitud",), ("x",)))
    barrio = normalize_text(_nested_value(item, ("barrio",), ("nombre_barrio",), ("barrioNombre",)))
    comuna = normalize_text(_nested_value(item, ("comuna",), ("comuna_usig",), ("nombre_comuna",)))

    if lat is None or lon is None:
        return GeocodeResult(address, query, normalized, "", "", barrio, comuna, precision or "sin_coordenadas", "sin_match", fecha)
    if not in_caba_bounds(lat, lon):
        return GeocodeResult(address, query, normalized, format_coordinate(lat), format_coordinate(lon), barrio, comuna, precision or "fuera_bbox", "sospechosa", fecha)
    if not normalize_comuna(comuna):
        comuna = comuna_from_point(lat, lon)

    exact_markers = {"calle_altura", "puerta", "exacta", "direccion"}
    estado = "exacta" if precision in exact_markers or any(marker in precision for marker in exact_markers) else "aproximada"
    return GeocodeResult(address, query, normalized, format_coordinate(lat), format_coordinate(lon), barrio, comuna, precision or estado, estado, fecha)


def _quality_for_estado(estado: str, criterio: str) -> str:
    if estado == "exacta" and criterio == "exacta_sin_control_comuna":
        return "usig_exacta_sin_control_comuna"
    if estado == "exacta":
        return "usig_exacta"
    if estado == "aproximada":
        return "usig_aproximada"
    if estado == "usig_comuna_inconsistente":
        return "usig_comuna_inconsistente"
    return estado or "sin_geo"


def _with_traceability(
    result: GeocodeResult,
    candidates: list[str],
    comuna_fuente: str = "",
    criterio: str = "",
) -> GeocodeResult:
    comuna_usig = normalize_comuna(result.comuna_usig)
    coincide = ""
    if comuna_fuente and comuna_usig:
        coincide = "si" if comuna_fuente == comuna_usig else "no"
    return replace(
        result,
        direccion_candidatas=" | ".join(candidates),
        comuna_fuente=comuna_fuente,
        coincide_comuna=coincide,
        criterio_seleccion=criterio,
        calidad_geo=_quality_for_estado(result.estado, criterio),
    )


def _commune_inconsistent_result(
    exact_result: GeocodeResult,
    candidates: list[str],
    comuna_fuente: str,
) -> GeocodeResult:
    return replace(
        exact_result,
        latitud="",
        longitud="",
        estado="usig_comuna_inconsistente",
        calidad_geo="usig_comuna_inconsistente",
        comuna_fuente=comuna_fuente,
        coincide_comuna="no",
        direccion_candidatas=" | ".join(candidates),
        criterio_seleccion="exacta_descartada_por_comuna_fuente",
    )


def select_geocode_result(
    address: str,
    candidates: list[str],
    results: list[GeocodeResult],
    comuna_fuente: str = "",
) -> GeocodeResult:
    if not candidates:
        return GeocodeResult(
            address,
            "",
            "",
            "",
            "",
            "",
            "",
            "sin_altura_o_codigo_no_consultado",
            "sin_match",
            date.today().isoformat(),
            comuna_fuente=comuna_fuente,
            calidad_geo="sin_geo",
            criterio_seleccion="sin_candidatas_validas",
        )
    exact_results = [result for result in results if result.estado == "exacta"]
    if comuna_fuente:
        for result in exact_results:
            if normalize_comuna(result.comuna_usig) == comuna_fuente:
                return _with_traceability(result, candidates, comuna_fuente, "exacta_comuna_coincidente")
        if exact_results:
            return _commune_inconsistent_result(exact_results[0], candidates, comuna_fuente)
    elif exact_results:
        return _with_traceability(exact_results[0], candidates, "", "exacta_sin_control_comuna")

    for result in results:
        if result.estado not in {"sin_match", "error"}:
            return _with_traceability(result, candidates, comuna_fuente, f"{result.estado}_sin_exacta_coincidente")
    if results:
        return _with_traceability(results[0], candidates, comuna_fuente, "sin_match_o_error")
    return GeocodeResult(
        address,
        candidates[0],
        "",
        "",
        "",
        "",
        "",
        "sin_respuesta_usig",
        "sin_match",
        date.today().isoformat(),
        direccion_candidatas=" | ".join(candidates),
        comuna_fuente=comuna_fuente,
        calidad_geo="sin_geo",
        criterio_seleccion="sin_resultados",
    )


def _geocode_candidate(address: str, query: str, client: requests.Session) -> GeocodeResult:
    try:
        response = client.get(
            USIG_URL,
            params={"direccion": query, "geocodificar": "true"},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        return parse_usig_payload(address, response.json(), direccion_consulta=query)
    except Exception as exc:
        return GeocodeResult(address, query, "", "", "", "", "", str(exc)[:180], "error", date.today().isoformat())


def geocode_address(
    address: str,
    session: requests.Session | None = None,
    comuna_fuente: str = "",
) -> GeocodeResult:
    client = session or requests.Session()
    candidates = generate_f02_address_candidates(address)
    results: list[GeocodeResult] = []
    for index, query in enumerate(candidates):
        if index:
            time.sleep(REQUEST_INTERVAL_SECONDS)
        results.append(_geocode_candidate(address, query, client))
    return select_geocode_result(address, candidates, results, normalize_comuna(comuna_fuente))


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


def normalize_comuna(value: object) -> str:
    text = normalize_text(value, case="lower", remove_accents=True)
    if not text or text in {"no determinada", "no determinado", "no disponible"}:
        return ""
    match = re.search(r"\b(1[0-5]|[1-9])\b", text)
    return str(int(match.group(1))) if match else ""


def consistency_report(
    habilitaciones: pd.DataFrame,
    cache: pd.DataFrame,
    max_discrepancies: int = 20,
) -> tuple[dict[str, float | int], pd.DataFrame]:
    if habilitaciones.empty or cache.empty:
        return {"total": 0, "coincidencias": 0, "discrepancias": 0, "porcentaje_coincidencia": 0.0}, pd.DataFrame()
    required_hab = {"direccion_original", "comuna"}
    required_cache = {"direccion_original", "comuna_usig", "estado"}
    if not required_hab.issubset(habilitaciones.columns) or not required_cache.issubset(cache.columns):
        return {"total": 0, "coincidencias": 0, "discrepancias": 0, "porcentaje_coincidencia": 0.0}, pd.DataFrame()

    hab = habilitaciones[["direccion_original", "comuna"]].copy()
    hab["comuna_fuente"] = hab["comuna"].map(normalize_comuna)
    hab["direccion_key"] = hab["direccion_original"].map(cache_key)
    hab = hab[hab["comuna_fuente"].ne("") & hab["direccion_key"].ne("")].copy()

    exact_cache = cache[cache["estado"].astype(str) == "exacta"].copy()
    exact_cache["comuna_usig_norm"] = exact_cache["comuna_usig"].map(normalize_comuna)
    if {"latitud", "longitud"}.issubset(exact_cache.columns):
        missing_comuna = exact_cache["comuna_usig_norm"].eq("")
        exact_cache.loc[missing_comuna, "comuna_usig_norm"] = exact_cache.loc[missing_comuna].apply(
            lambda row: comuna_from_point(parse_float(row.get("latitud")), parse_float(row.get("longitud"))),
            axis=1,
        )
    exact_cache["direccion_key"] = exact_cache["direccion_original"].map(cache_key)
    exact_cache = exact_cache[exact_cache["comuna_usig_norm"].ne("") & exact_cache["direccion_key"].ne("")]
    exact_cache = exact_cache.drop_duplicates("direccion_key", keep="last")

    merged = hab.merge(
        exact_cache[["direccion_key", "comuna_usig_norm"]],
        on="direccion_key",
        how="inner",
    )
    if merged.empty:
        return {"total": 0, "coincidencias": 0, "discrepancias": 0, "porcentaje_coincidencia": 0.0}, pd.DataFrame()

    merged["coincide"] = merged["comuna_fuente"] == merged["comuna_usig_norm"]
    total = len(merged)
    matches = int(merged["coincide"].sum())
    mismatches = total - matches
    match_rate = (matches / total * 100) if total else 0.0
    discrepancies = (
        merged[~merged["coincide"]]
        .rename(columns={"comuna_usig_norm": "comuna_usig"})
        [["direccion_original", "comuna_fuente", "comuna_usig"]]
        .drop_duplicates()
        .head(max_discrepancies)
        .reset_index(drop=True)
    )
    return {
        "total": total,
        "coincidencias": matches,
        "discrepancias": mismatches,
        "porcentaje_coincidencia": match_rate,
    }, discrepancies


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
        remaining = cache[cache.get("estado", pd.Series(dtype=str)).astype(str).isin(["sin_match", "error"])]
        if not remaining.empty:
            print("Direcciones aun sin match/error (hasta 15):")
            for row in remaining.head(15).itertuples(index=False):
                print(f"- {getattr(row, 'direccion_original')}")
    elif report["total"]:
        print("CAPA F02 USIG: habilitable como capa opcional desactivada por default.")


def read_habilitaciones(path: Path = DATA_PROCESSED / "fact_habilitacion_gastronomica.csv") -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def print_consistency_report(
    habilitaciones_path: Path = DATA_PROCESSED / "fact_habilitacion_gastronomica.csv",
    cache_path: Path = CACHE_PATH,
) -> None:
    habilitaciones = read_habilitaciones(habilitaciones_path)
    cache = read_cache(cache_path)
    report, discrepancies = consistency_report(habilitaciones, cache)
    print(
        "Consistencia comuna F02 vs USIG exacta: "
        f"comparables={report['total']} coincidencias={report['coincidencias']} "
        f"discrepancias={report['discrepancias']} "
        f"porcentaje_coincidencia={report['porcentaje_coincidencia']:.1f}%"
    )
    if report["total"] and report["porcentaje_coincidencia"] < 95:
        print("RECOMENDACION: no promover la capa F02 USIG al dashboard; coincidencia menor a 95%.")
    elif report["total"]:
        print("RECOMENDACION: consistencia de comuna suficiente para revisar promocion de la capa.")
    else:
        print("RECOMENDACION: no promover la capa F02 USIG; no hay casos comparables exactos.")
    if not discrepancies.empty:
        print("Discrepancias (hasta 20):")
        for row in discrepancies.itertuples(index=False):
            print(f"- direccion={row.direccion_original} | comuna_fuente={row.comuna_fuente} | comuna_usig={row.comuna_usig}")


def retry_sin_match(cache: pd.DataFrame, limit: int) -> pd.DataFrame:
    retry_mask = cache["estado"].astype(str).isin(["sin_match", "error"])
    retry_indexes = cache[retry_mask].index.tolist()[: max(limit, 0)]
    print(f"Reintentando direcciones sin_match/error={len(retry_indexes)}")
    last_call = 0.0
    for index_number, row_index in enumerate(retry_indexes, start=1):
        address = str(cache.at[row_index, "direccion_original"])
        elapsed = time.monotonic() - last_call
        if last_call and elapsed < REQUEST_INTERVAL_SECONDS:
            time.sleep(REQUEST_INTERVAL_SECONDS - elapsed)
        result = geocode_address(address)
        last_call = time.monotonic()
        for column, value in result.as_row().items():
            cache.at[row_index, column] = value
        print(f"{index_number:04d}/{len(retry_indexes):04d} {result.estado:11s} {address} -> {result.direccion_consulta}")
    return cache


def run(limit: int, solo_pendientes: bool, reintentar_sin_match: bool) -> int:
    cache = read_cache()
    if reintentar_sin_match:
        updated = retry_sin_match(cache.copy(), limit)
        write_cache(updated)
        print(f"Cache actualizado: {CACHE_PATH}")
        refreshed = read_cache()
        print_report(refreshed)
        print_consistency_report()
        return 0

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
        if index % 25 == 0:
            write_cache(pd.DataFrame(rows, columns=CACHE_COLUMNS))
            print(f"Checkpoint cache: {index}/{len(selected)}")

    updated = pd.DataFrame(rows, columns=CACHE_COLUMNS)
    write_cache(updated)
    print(f"Cache escrito: {CACHE_PATH}")
    print_report(read_cache())
    print_consistency_report()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Geocodifica direcciones F02 con USIG y cache persistente.")
    parser.add_argument("--limit", type=int, default=500, help="Cantidad maxima de direcciones nuevas a consultar.")
    parser.add_argument("--solo-pendientes", action="store_true", help="Procesa solo direcciones ausentes del cache.")
    parser.add_argument("--reintentar-sin-match", action="store_true", help="Reconsulta filas cacheadas con estado sin_match/error usando normalizacion F02 y actualiza esas filas.")
    parser.add_argument("--reporte-consistencia", action="store_true", help="Solo reporta consistencia comuna fuente vs comuna USIG exacta; no modifica datos.")
    args = parser.parse_args()
    if args.reporte_consistencia:
        print_consistency_report()
        return 0
    return run(limit=args.limit, solo_pendientes=args.solo_pendientes, reintentar_sin_match=args.reintentar_sin_match)


if __name__ == "__main__":
    raise SystemExit(main())
