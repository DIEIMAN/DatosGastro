"""Crea la capa preliminar de sedes conocidas de cafeterias Cafecito.

La salida es una base trazable de sedes publicas conocidas en CABA de marcas
participantes o vinculadas al evento. No afirma que cada sede haya participado
fisicamente en la edicion relevada. No lee ni modifica datos personales del
formulario; solo se usa el XLSX para verificar que la base de respuestas sigue
en 79 registros.

Geocodifica con el servicio publico USIG de Buenos Aires, sin API key y sin
guardar identificadores de servicios externos.

Uso:
    python scripts/cafecito/geolocalizar_sedes_cafeterias.py
"""
from __future__ import annotations

import csv
import json
import re
import sys
import time
import warnings
from collections import Counter
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import matplotlib

warnings.filterwarnings("ignore", message=".*urllib3.*")
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
import requests  # noqa: E402
from shapely.geometry import Point, shape  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.cafecito import analizar_cafecito as base  # noqa: E402

DOCS_DIR = REPO_ROOT / "docs" / "cafecito" / "geolocalizacion_cafeterias"
OUT_DIR = REPO_ROOT / "outputs" / "cafecito"
GRAF_DIR = OUT_DIR / "graficos_datagastro"
RAW_DIR = REPO_ROOT / "data" / "raw"

PERPLEXITY_DOC = DOCS_DIR / "perplexity_sedes_cafeterias.md"
METHOD_DOC = DOCS_DIR / "FUENTES_Y_METODO_GEOLOCALIZACION_CAFETERIAS.md"

PRELIM_CSV = OUT_DIR / "cafeterias_sedes_caba_preliminar.csv"
GEOCODED_CSV = OUT_DIR / "cafeterias_sedes_caba_geocodificadas.csv"
PENDING_CSV = OUT_DIR / "cafeterias_marcas_pendientes.csv"
RESUMEN_COMUNA_CSV = OUT_DIR / "resumen_sedes_cafeterias_por_comuna.csv"
RESUMEN_BARRIO_CSV = OUT_DIR / "resumen_sedes_cafeterias_por_barrio.csv"
LECTURA_RED_MD = OUT_DIR / "lectura_red_cafeterias_vs_publico.md"

MAPA_PNG = GRAF_DIR / "mapa_sedes_cafeterias_participantes.png"
RANKING_COMUNA_PNG = GRAF_DIR / "ranking_comunal_sedes_cafeterias.png"
RANKING_BARRIO_PNG = GRAF_DIR / "ranking_barrial_sedes_cafeterias.png"

USIG_URL = "https://servicios.usig.buenosaires.gob.ar/normalizar/"
REQUEST_TIMEOUT_SECONDS = 18
REQUEST_INTERVAL_SECONDS = 0.28

INK = "#1F3B57"
BLUE = "#2C7FB8"
ORANGE = "#C0762B"
GREEN = "#1A9850"
GREY = "#68717C"
LIGHT = "#EEF2F6"
LINE = "#D7DEE8"

METODO_PHRASE = (
    "El mapa muestra sedes públicas conocidas en CABA de marcas/cafeterías participantes "
    "o vinculadas al evento. No implica que todas esas sedes hayan participado físicamente "
    "en la edición relevada; se utiliza como aproximación a la red territorial potencial "
    "de difusión."
)


@dataclass(frozen=True)
class SedeSeed:
    instagram: str
    nombre_comercial: str
    sede_nombre_o_referencia: str
    direccion_preliminar: str
    barrio_preliminar: str
    comuna_preliminar: str
    fuente_preliminar: str
    fuente_secundaria_preliminar: str
    nivel_confianza_preliminar: str
    observaciones_preliminares: str
    estado_validacion: str
    tipo_punto: str
    usar_si_geocodifica: str
    sucursal_participante_exacta_confirmada: str = "no"


SOURCE = {
    "perplexity": "Insumo preliminar Perplexity provisto por usuario",
    "manteca_ig": "Instagram oficial Manteca: https://www.instagram.com/manteca_arg/",
    "lobo_ig": "Instagram oficial Lobo Cafe: https://www.instagram.com/lobocafe.ba/",
    "leble_web": "Sitio oficial Le Ble - cafe/resto: https://www.leble.com.ar/cafe-resto.html",
    "gout_ig": "Instagram oficial GOUT Gluten Free: https://www.instagram.com/goutglutenfree/",
    "registrado_web": "Sitio oficial Cafe Registrado - nuestros locales: https://www.caferegistrado.com/nuestros-locales/",
    "piccolina_ig": "Instagram oficial Piccolina: https://www.instagram.com/piccolinacafe/",
    "mojo_ig": "Instagram oficial Mojo Cafeteria: https://www.instagram.com/mojocafeteria/",
    "jimena_web": "Sitio oficial Jimena Fuster: https://jimenafuster.com.ar/",
    "mrgreen_ig": "Instagram oficial Mr. Green Coffee: https://www.instagram.com/mr.greencoffee/",
    "mrgreen_rappi": "Directorio Rappi Mr. Green Coffee Paraguay 364: https://www.rappi.com.ar/",
    "malvon_web": "Sitio oficial Malvon: https://www.malvon.ar/",
    "malvon_ig": "Instagram oficial Malvon: https://www.instagram.com/malvonba/",
    "juanvaldez_ig": "Instagram oficial Juan Valdez Cafe Argentina: https://www.instagram.com/juanvaldezcafear/",
    "aldiablo_ig": "Instagram oficial Al Diablo Coffee Roasters: https://www.instagram.com/aldiablo.coffeeroasters/",
    "aldiablo_store": "Tienda oficial Al Diablo Coffee Roasters: https://al-diablocoffeeroasters.mitiendanube.com/",
    "caoba_ig": "Instagram Caoba Cafe BA: https://www.instagram.com/caoba.cafeba/",
    "curatealma_ig": "Instagram Cura Te Alma: https://www.instagram.com/curatealma/",
    "curatealma_ref": "Referencias publicas no CABA de Cura Te Alma (Rio Cuarto/Cordoba)",
}


def seeds() -> list[SedeSeed]:
    rows: list[SedeSeed] = []

    def add(
        instagram: str,
        nombre: str,
        ref: str,
        direccion: str,
        barrio: str,
        comuna: str,
        fuente: str,
        secundaria: str,
        confianza: str,
        obs: str,
        estado: str,
        tipo: str,
        usar: str,
    ) -> None:
        rows.append(SedeSeed(instagram, nombre, ref, direccion, barrio, comuna, fuente, secundaria, confianza, obs, estado, tipo, usar))

    # Sedes explicitadas en el insumo preliminar y validadas con fuente publica.
    add("@manteca_arg", "Manteca LB", "Villa Ortuzar", "Heredia 1407", "Villa Ortuzar", "15", SOURCE["perplexity"], SOURCE["manteca_ig"], "alta", "Sede publicada por la marca; se geocodifica con USIG.", "confirmada_pendiente_geocodificacion", "sede_confirmada_marca_participante", "si")
    add("@manteca_arg", "Manteca LB", "Belgrano", "Soldado de la Independencia 1486", "Belgrano", "13", SOURCE["perplexity"], SOURCE["manteca_ig"], "alta", "Corregida a Comuna 13 por validacion territorial.", "confirmada_pendiente_geocodificacion", "sede_confirmada_marca_participante", "si")
    add("@lobocafe.ba", "Lobo Cafe", "Puerto Madero actual", "Pierina Dealessi 1330", "Puerto Madero", "1", SOURCE["perplexity"], SOURCE["lobo_ig"], "alta", "La fuente oficial actual muestra 1330; se conserva nota por contradiccion con 1130.", "confirmada_pendiente_geocodificacion", "sede_confirmada_marca_participante", "si")
    add("@lobocafe.ba", "Lobo Cafe", "Puerto Madero direccion contradictoria", "Pierina Dealessi 1130", "Puerto Madero", "1", SOURCE["perplexity"], SOURCE["lobo_ig"], "baja", "Direccion contradictoria o historica frente a fuente oficial actual 1330; no se usa en mapa.", "requiere_validacion_fuente", "sede_exploratoria_requiere_validacion", "no")

    leble = [
        ("Valle", "Valle 1101", "Caballito", "6"),
        ("Dorrego", "Dorrego 999", "Chacarita", "15"),
        ("Almagro", "Mansilla 3401", "Almagro", ""),
        ("Arredondo", "Arredondo 2402", "Belgrano", "13"),
        ("Barracas", "Vieytes 1655", "Barracas", "4"),
        ("Ciudad", "Av. Cordoba 4302", "Palermo/Villa Crespo", ""),
        ("Boedo", "Castro Barros 501", "Boedo/Almagro", ""),
        ("Urquiza", "Plaza 2501", "Villa Urquiza", "12"),
    ]
    for ref, direccion, barrio, comuna in leble:
        add("@lebleoficial", "Le Ble", ref, direccion, barrio, comuna, SOURCE["leble_web"], SOURCE["perplexity"], "alta", "Sede publicada en sitio oficial; no estaba cerrada en el insumo preliminar.", "confirmada_pendiente_geocodificacion", "sede_multisucursal_no_confirmada_para_evento", "si")

    gout = [
        ("Recoleta", "Montevideo 1480", "Recoleta", "2"),
        ("Barrio Norte", "Juncal 2124", "Recoleta", "2"),
        ("Palermo", "Fray Justo Santa Maria de Oro 2480", "Palermo", "14"),
        ("Belgrano/Colegiales", "Av. Lacroze 2117", "Belgrano/Colegiales", ""),
        ("Caballito", "Av. Pedro Goyena 123", "Caballito", "6"),
        ("Barracas", "Av. Suarez 1673", "Barracas", "4"),
    ]
    for ref, direccion, barrio, comuna in gout:
        add("@goutglutenfree", "GOUT Gluten Free", ref, direccion, barrio, comuna, SOURCE["gout_ig"], SOURCE["perplexity"], "alta", "Sede publicada por la marca; se incluye como red potencial.", "confirmada_pendiente_geocodificacion", "sede_multisucursal_no_confirmada_para_evento", "si")
    add("@goutglutenfree", "GOUT Gluten Free", "Av. La Plata 24 dudosa", "Av. La Plata 24", "Caballito/Almagro", "", SOURCE["perplexity"], "Validacion web no concluyente; hay senales de posible confusion con otra marca/sede.", "baja", "No se confirma como sede GOUT con evidencia suficiente; queda fuera del mapa.", "requiere_validacion_fuente", "sede_exploratoria_requiere_validacion", "no")

    registrado = [
        ("Palermo Hollywood", "Costa Rica 5901", "Palermo", "14"),
        ("Almagro", "General Juan Domingo Peron 4211", "Almagro", "5"),
        ("Palermo", "Av. Medrano 1881", "Palermo", "14"),
        ("Belgrano", "Arcos 1853", "Belgrano", "13"),
        ("Arcos", "Av. Del Libertador 4101", "Palermo", "14"),
        ("Tribunales", "Viamonte 1574", "San Nicolas", "1"),
        ("Microcentro", "Viamonte 361", "San Nicolas", "1"),
        ("Puerto Madero", "Camila O'Gorman 373", "Puerto Madero", "1"),
        ("Belgrano R", "Vuelta de Obligado 2502", "Belgrano", "13"),
    ]
    for ref, direccion, barrio, comuna in registrado:
        add("@caferegistrado", "Cafe Registrado", ref, direccion, barrio, comuna, SOURCE["registrado_web"], SOURCE["perplexity"], "alta", "Validado contra listado oficial de locales; supera la validacion fuerte pedida.", "confirmada_pendiente_geocodificacion", "sede_multisucursal_no_confirmada_para_evento", "si")

    add("@piccolinacafe", "Piccolina Cafe", "Palermo", "Thames 1601", "Palermo", "14", SOURCE["piccolina_ig"], SOURCE["perplexity"], "alta", "Direccion validada contra fuente oficial de la marca.", "confirmada_pendiente_geocodificacion", "sede_confirmada_marca_participante", "si")
    add("@mojocafeteria", "Mojo Cafeteria", "Belgrano", "Jose Hernandez 2696", "Belgrano", "13", SOURCE["mojo_ig"], SOURCE["perplexity"], "alta", "Direccion validada contra fuente oficial de la marca.", "confirmada_pendiente_geocodificacion", "sede_multisucursal_no_confirmada_para_evento", "si")
    add("@mojocafeteria", "Mojo Cafeteria", "Palermo", "Av. Santa Fe 3902", "Palermo", "14", SOURCE["mojo_ig"], SOURCE["perplexity"], "alta", "Direccion validada contra fuente oficial de la marca.", "confirmada_pendiente_geocodificacion", "sede_multisucursal_no_confirmada_para_evento", "si")
    add("@jimenafuster_", "Jimena Fuster", "Belgrano", "Olazabal 2115", "Belgrano", "13", SOURCE["perplexity"], SOURCE["jimena_web"], "alta", "Se valida como local/sede comercial; se marca como red potencial, no como participacion exacta.", "confirmada_pendiente_geocodificacion", "sede_confirmada_marca_participante", "si")
    add("@mr.greencoffee", "Mr. Green Coffee", "Retiro", "Paraguay 364", "Retiro", "1", SOURCE["perplexity"], SOURCE["mrgreen_rappi"], "media", "Direccion publicada en directorio y consistente con presencia de la marca; usar como nodo medio.", "confirmada_pendiente_geocodificacion", "sede_confirmada_marca_participante", "si")
    add("@mr.greencoffee", "Mr. Green Coffee", "Centro", "Lavalle 1133", "San Nicolas", "1", SOURCE["mrgreen_ig"], SOURCE["perplexity"], "media", "Segunda sede publicada por la marca; sin segunda fuente fuerte.", "confirmada_pendiente_geocodificacion", "sede_multisucursal_no_confirmada_para_evento", "si")

    malvon = [
        ("Palermo/Villa Crespo", "Serrano 789", "Villa Crespo/Palermo", ""),
        ("Caballito", "Fragata Presidente Sarmiento 891", "Caballito", "6"),
        ("Villa Devoto", "Fernandez de Enciso 3939", "Villa Devoto", "11"),
        ("Monserrat", "Moreno 550", "Monserrat", "1"),
    ]
    for ref, direccion, barrio, comuna in malvon:
        add("@malvonba", "Malvon", ref, direccion, barrio, comuna, SOURCE["malvon_web"], SOURCE["malvon_ig"], "alta", "Sede publicada por la marca; se incluye como red potencial.", "confirmada_pendiente_geocodificacion", "sede_multisucursal_no_confirmada_para_evento", "si")

    add("@juanvaldezcafear", "Juan Valdez Cafe", "Cabildo", "Av. Cabildo 3787", "Nunez", "13", SOURCE["perplexity"], SOURCE["juanvaldez_ig"], "alta", "Handle corregido: se usa @juanvaldezcafear, no el typo preliminar.", "confirmada_pendiente_geocodificacion", "sede_multisucursal_no_confirmada_para_evento", "si")
    add("@juanvaldezcafear", "Juan Valdez Cafe", "Las Heras", "Av. Las Heras 2601", "Recoleta", "2", SOURCE["perplexity"], SOURCE["juanvaldez_ig"], "alta", "Handle corregido: se usa @juanvaldezcafear, no el typo preliminar.", "confirmada_pendiente_geocodificacion", "sede_multisucursal_no_confirmada_para_evento", "si")
    add("@aldiablo.coffeeroasters", "Al Diablo Coffee Roasters", "Palermo", "Costa Rica 4752", "Palermo", "14", SOURCE["perplexity"], f"{SOURCE['aldiablo_ig']} | {SOURCE['aldiablo_store']}", "alta", "Direccion validada con fuente oficial y tienda de la marca.", "confirmada_pendiente_geocodificacion", "sede_confirmada_marca_participante", "si")

    # Marcas sin sede CABA suficientemente validada.
    add("@caoba.cafeba", "Caoba Cafe BA", "Pendiente", "", "", "", SOURCE["perplexity"], SOURCE["caoba_ig"], "pendiente", "No se identifico direccion CABA publica confiable en esta validacion.", "pendiente_direccion", "pendiente_validacion", "pendiente")
    add("@curatealma", "Cura Te Alma", "Sin sede CABA validada", "", "", "", SOURCE["perplexity"], f"{SOURCE['curatealma_ig']} | {SOURCE['curatealma_ref']}", "pendiente", "Marca vinculada sin sede CABA publica validada; referencias disponibles apuntan fuera de CABA o venta/marca sin local mapeable.", "pendiente_direccion", "pendiente_validacion", "pendiente")
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def load_geometries() -> tuple[list[tuple[str, Any]], list[tuple[str, str, Any]]]:
    comunas_data = json.loads((RAW_DIR / "geo_comunas.geojson").read_text(encoding="utf-8"))
    barrios_data = json.loads((RAW_DIR / "geo_barrios.geojson").read_text(encoding="utf-8"))
    comunas = [(str(f["properties"]["comuna"]), shape(f["geometry"])) for f in comunas_data["features"]]
    barrios = [(f["properties"]["nombre"], str(f["properties"]["comuna"]), shape(f["geometry"])) for f in barrios_data["features"]]
    return comunas, barrios


def point_to_area(lat: float, lon: float, comunas: list[tuple[str, Any]], barrios: list[tuple[str, str, Any]]) -> tuple[str, str]:
    point = Point(lon, lat)
    barrio_name = ""
    barrio_comuna = ""
    for name, comuna, geom in barrios:
        if geom.contains(point) or geom.touches(point):
            barrio_name = name
            barrio_comuna = comuna
            break
    comuna_name = barrio_comuna
    if not comuna_name:
        for comuna, geom in comunas:
            if geom.contains(point) or geom.touches(point):
                comuna_name = comuna
                break
    return barrio_name, comuna_name


def parse_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(str(value).replace(",", "."))
    except ValueError:
        return None


def geocode_usig(address: str, session: requests.Session) -> dict[str, str]:
    if not address:
        return {"estado_geocodificacion": "sin_direccion"}
    try:
        response = session.get(
            USIG_URL,
            params={"direccion": address, "geocodificar": "true"},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        payload = response.json()
    except Exception as exc:  # noqa: BLE001
        return {"estado_geocodificacion": f"error: {str(exc)[:90]}"}
    candidates = payload.get("direccionesNormalizadas") or []
    for item in candidates:
        if str(item.get("cod_partido", "")).lower() != "caba":
            continue
        coords = item.get("coordenadas") or {}
        lat = parse_float(coords.get("y"))
        lon = parse_float(coords.get("x"))
        if lat is None or lon is None:
            continue
        return {
            "direccion_normalizada_usig": item.get("direccion", ""),
            "latitud": f"{lat:.6f}",
            "longitud": f"{lon:.6f}",
            "estado_geocodificacion": "exacta_usig",
        }
    return {"estado_geocodificacion": "sin_match_caba"}


def prelim_rows(seed_rows: list[SedeSeed]) -> list[dict[str, str]]:
    fieldnames = [
        "instagram",
        "nombre_comercial",
        "sede_nombre_o_referencia",
        "direccion_preliminar",
        "barrio_preliminar",
        "comuna_preliminar",
        "fuente_preliminar",
        "fuente_secundaria_preliminar",
        "nivel_confianza_preliminar",
        "observaciones_preliminares",
        "estado_validacion",
    ]
    return [{key: getattr(seed, key) for key in fieldnames} for seed in seed_rows]


def geocoded_rows(seed_rows: list[SedeSeed]) -> list[dict[str, str]]:
    comunas, barrios = load_geometries()
    session = requests.Session()
    rows = []
    last_request = 0.0
    for seed in seed_rows:
        row = {
            "instagram": seed.instagram,
            "nombre_comercial": seed.nombre_comercial,
            "sede_nombre_o_referencia": seed.sede_nombre_o_referencia,
            "direccion": seed.direccion_preliminar,
            "barrio": "",
            "comuna": "",
            "latitud": "",
            "longitud": "",
            "fuente_principal": seed.fuente_secundaria_preliminar or seed.fuente_preliminar,
            "fuente_secundaria": seed.fuente_preliminar,
            "nivel_confianza": seed.nivel_confianza_preliminar,
            "tipo_punto": seed.tipo_punto,
            "usar_en_mapa": "no",
            "sucursal_participante_exacta_confirmada": seed.sucursal_participante_exacta_confirmada,
            "observaciones": seed.observaciones_preliminares,
        }
        if seed.estado_validacion in {"pendiente_direccion", "excluir_no_caba", "no_mapeable"}:
            row["usar_en_mapa"] = "pendiente" if seed.estado_validacion == "pendiente_direccion" else "no"
            rows.append(row)
            continue
        if not seed.direccion_preliminar:
            row["usar_en_mapa"] = "pendiente"
            rows.append(row)
            continue

        elapsed = time.time() - last_request
        if elapsed < REQUEST_INTERVAL_SECONDS:
            time.sleep(REQUEST_INTERVAL_SECONDS - elapsed)
        geo = geocode_usig(seed.direccion_preliminar, session)
        last_request = time.time()

        row["latitud"] = geo.get("latitud", "")
        row["longitud"] = geo.get("longitud", "")
        lat = parse_float(row["latitud"])
        lon = parse_float(row["longitud"])
        if lat is not None and lon is not None:
            barrio_geo, comuna_geo = point_to_area(lat, lon, comunas, barrios)
            row["barrio"] = barrio_geo
            row["comuna"] = comuna_geo
            row["observaciones"] = normalize_space(
                f"{row['observaciones']} Geocodificacion USIG: {geo.get('direccion_normalizada_usig', '')}."
            )
            if seed.usar_si_geocodifica == "si" and seed.nivel_confianza_preliminar in {"alta", "media"} and comuna_geo:
                row["usar_en_mapa"] = "si"
            elif seed.usar_si_geocodifica == "pendiente":
                row["usar_en_mapa"] = "pendiente"
            else:
                row["usar_en_mapa"] = "no"
        else:
            row["usar_en_mapa"] = "pendiente" if seed.usar_si_geocodifica == "si" else seed.usar_si_geocodifica
            row["observaciones"] = normalize_space(
                f"{row['observaciones']} Geocodificacion USIG sin coordenadas confiables: {geo.get('estado_geocodificacion', '')}."
            )
        if seed.nivel_confianza_preliminar == "baja":
            row["usar_en_mapa"] = "no"
        rows.append(row)
    return rows


def pending_rows(seed_rows: list[SedeSeed], geo_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    pending: list[dict[str, str]] = []
    by_handle = {row["instagram"]: row for row in geo_rows}
    for seed in seed_rows:
        if seed.estado_validacion in {"pendiente_direccion", "requiere_validacion_fuente", "excluir_no_caba", "no_mapeable"} or seed.usar_si_geocodifica in {"no", "pendiente"}:
            motivo = {
                "pendiente_direccion": "No se encontro direccion CABA publica confiable.",
                "requiere_validacion_fuente": "Hay direccion dudosa o contradictoria; no se usa en mapa.",
                "excluir_no_caba": "Referencia fuera de CABA; queda fuera del mapa principal.",
                "no_mapeable": "No corresponde mapear como sede publica.",
            }.get(seed.estado_validacion, "Pendiente de validacion.")
            pending.append({
                "instagram": seed.instagram,
                "nombre_comercial": seed.nombre_comercial,
                "motivo_pendiente": motivo,
                "fuente_disponible": f"{seed.fuente_preliminar} | {seed.fuente_secundaria_preliminar}",
                "proximo_paso_sugerido": "Confirmar con fuente oficial de la marca o documento/listado oficial de comercios adheridos.",
                "observaciones": seed.observaciones_preliminares,
            })
    # Si una marca queda sin ningun punto usable, dejarla explicitamente marcada.
    usable_by_brand = Counter(row["instagram"] for row in geo_rows if row.get("usar_en_mapa") == "si")
    for handle, row in by_handle.items():
        if not usable_by_brand.get(handle) and not any(p["instagram"] == handle for p in pending):
            pending.append({
                "instagram": handle,
                "nombre_comercial": row["nombre_comercial"],
                "motivo_pendiente": "No quedo ninguna sede usable en mapa.",
                "fuente_disponible": row.get("fuente_principal", ""),
                "proximo_paso_sugerido": "Revalidar direccion y coordenadas.",
                "observaciones": row.get("observaciones", ""),
            })
    return pending


def summary_rows(geo_rows: list[dict[str, str]], field: str, output_field: str) -> list[dict[str, Any]]:
    usable = [row for row in geo_rows if row.get("usar_en_mapa") == "si" and row.get(field)]
    total = len(usable)
    counter = Counter(row[field] for row in usable)
    brand_counter: dict[str, set[str]] = {}
    for row in usable:
        brand_counter.setdefault(row[field], set()).add(row["instagram"])
    rows = []
    for key, count in counter.most_common():
        rows.append({
            output_field: key,
            "cantidad_sedes": count,
            "cantidad_marcas": len(brand_counter.get(key, set())),
            "porcentaje_sedes_mapa": f"{(count / total * 100):.1f}" if total else "0.0",
            "nota": "Cuenta sedes publicas conocidas usadas en mapa; no implica participacion fisica de cada sede.",
        })
    return rows


def rings(geom: dict[str, Any]) -> list[list[list[float]]]:
    if geom["type"] == "Polygon":
        return [geom["coordinates"][0]]
    if geom["type"] == "MultiPolygon":
        return [poly[0] for poly in geom["coordinates"]]
    return []


def draw_map(geo_rows: list[dict[str, str]]) -> None:
    data = json.loads((RAW_DIR / "geo_comunas.geojson").read_text(encoding="utf-8"))
    usable = [row for row in geo_rows if row.get("usar_en_mapa") == "si"]
    color_by_conf = {"alta": BLUE, "media": ORANGE, "baja": GREY, "pendiente": GREY}
    fig, ax = plt.subplots(figsize=(8.5, 8.7))
    for feature in data["features"]:
        for ring in rings(feature["geometry"]):
            xs = [p[0] for p in ring]
            ys = [p[1] for p in ring]
            ax.fill(xs, ys, facecolor=LIGHT, edgecolor="white", lw=1.0)
    for idx, row in enumerate(usable, 1):
        lat = parse_float(row["latitud"])
        lon = parse_float(row["longitud"])
        if lat is None or lon is None:
            continue
        color = color_by_conf.get(row["nivel_confianza"], GREY)
        ax.scatter(lon, lat, s=42, color=color, edgecolor="white", linewidth=0.8, zorder=5)
        ax.text(lon, lat, str(idx), ha="center", va="center", color="white", fontsize=5.8, fontweight="bold", zorder=6)
    ax.set_title(
        "Sedes conocidas de cafeterias participantes o vinculadas",
        loc="left",
        color=INK,
        fontsize=14,
        fontweight="bold",
        pad=12,
    )
    ax.axis("off")
    ax.set_aspect("equal")
    legend = [
        Line2D([0], [0], marker="o", color="w", label="Confianza alta", markerfacecolor=BLUE, markersize=8),
        Line2D([0], [0], marker="o", color="w", label="Confianza media", markerfacecolor=ORANGE, markersize=8),
    ]
    ax.legend(handles=legend, loc="lower left", frameon=False, fontsize=8)
    fig.text(
        0.02,
        0.03,
        "Puntos CABA con direccion validada y coordenadas USIG. " + METODO_PHRASE,
        color=GREY,
        fontsize=7.6,
        wrap=True,
    )
    fig.tight_layout(rect=[0, 0.06, 1, 0.96])
    GRAF_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(MAPA_PNG, dpi=190, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def draw_ranking(rows: list[dict[str, Any]], label_field: str, value_field: str, title: str, path: Path, top_n: int = 12) -> None:
    chosen = rows[:top_n]
    labels = [str(row[label_field]) for row in reversed(chosen)]
    values = [int(row[value_field]) for row in reversed(chosen)]
    fig, ax = plt.subplots(figsize=(8.4, max(3.2, 0.42 * len(labels) + 1.4)))
    colors = [ORANGE if i >= len(labels) - 3 else BLUE for i in range(len(labels))]
    ax.barh(labels, values, color=colors, height=0.62)
    ax.set_title(title, loc="left", color=INK, fontsize=14, fontweight="bold", pad=12)
    ax.spines[["top", "right", "bottom"]].set_visible(False)
    ax.spines["left"].set_color(LINE)
    ax.tick_params(axis="x", length=0, labelbottom=False)
    max_value = max(values) if values else 1
    for idx, value in enumerate(values):
        ax.text(value + max_value * 0.03, idx, str(value), color=INK, va="center", fontweight="bold", fontsize=8.5)
    ax.set_xlim(0, max_value * 1.22)
    fig.text(
        0.03,
        0.025,
        "Sedes usadas en mapa. No implica participacion fisica de cada sede en la edicion relevada.",
        color=GREY,
        fontsize=7.8,
    )
    fig.tight_layout(rect=[0, 0.06, 1, 0.94])
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=190, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def write_perplexity_doc() -> None:
    text = """# Insumo preliminar Perplexity - sedes de cafeterias Cafecito

Este documento conserva el insumo preliminar informado por el usuario. No se toma como verdad final: cada direccion debe validarse contra fuentes publicas oficiales, semioficiales o directorios confiables antes de entrar al mapa.

## Resumen del insumo

- `@manteca_arg`: Manteca LB, sedes sugeridas Heredia 1407, Villa Ortuzar, y Soldado de la Independencia 1486, Belgrano.
- `@lobocafe.ba`: Lobo Cafe, Puerto Madero, Pierina Dealessi 1130 segun busqueda preliminar. Validar porque tambien aparecio 1330.
- `@lebleoficial`: pendiente de sede CABA cerrada.
- `@goutglutenfree`: Montevideo 1480, Juncal 2124, Fray Justo Santa Maria de Oro 2480, Av. Lacroze 2117, Av. Pedro Goyena 123, La Plata 24.
- `@caferegistrado`: Costa Rica 5901, General Juan Domingo Peron 4211, Av. Medrano 1881. Requiere validacion fuerte.
- `@piccolinacafe`: pendiente de direccion confiable.
- `@mojocafeteria`: pendiente.
- `@jimenafuster_`: posible referencia Olazabal 2115, falta validar si funciona como local/sede comercial.
- `@mr.greencoffee`: Paraguay 364, Retiro.
- `@caoba.cafeba`: pendiente.
- `@malvonba`: Serrano 789 y Fragata Pres. Sarmiento 891.
- `@juanvaldezcafear`: Av. Cabildo 3787 y Av. Las Heras 2601. Corregir typo detectado: no usar `juandvaldezcafear`.
- `@aldiablo.coffeeroasters`: Costa Rica 4752, Palermo, pendiente de segunda fuente.
- `@curatealma`: pendiente.

## Regla de uso

El insumo solo inicia la investigacion. Las sedes usadas en el mapa requieren direccion validada, geocodificacion dentro de CABA y marca metodologica visible.
"""
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    PERPLEXITY_DOC.write_text(text, encoding="utf-8")


def write_method_doc(seed_rows: list[SedeSeed], geo_rows: list[dict[str, str]], pending: list[dict[str, str]]) -> None:
    usable = [row for row in geo_rows if row.get("usar_en_mapa") == "si"]
    excluded = [row for row in geo_rows if row.get("usar_en_mapa") != "si"]
    source_lines = "\n".join(f"- {value}" for value in sorted(set(SOURCE.values())))
    pending_lines = "\n".join(f"- `{row['instagram']}` - {row['motivo_pendiente']}" for row in pending)
    excluded_lines = "\n".join(
        f"- `{row['instagram']}` / {row['nombre_comercial']} / {row['sede_nombre_o_referencia']}: {row['observaciones']}"
        for row in excluded
        if row.get("tipo_punto") in {"sede_exploratoria_requiere_validacion", "pendiente_validacion"}
    )
    text = f"""# Fuentes y metodo - geolocalizacion de cafeterias Cafecito

## Objetivo de la capa

Construir una base trazable de sedes publicas conocidas en CABA de marcas/cafeterias participantes o vinculadas a Cafecito, para leer la red territorial potencial de difusion fisica y digital.

{METODO_PHRASE}

## Diferencia conceptual

- **Marca participante o vinculada:** marca/cafeteria mencionada como parte del universo Cafecito.
- **Sede conocida:** local publico de esa marca con direccion validada por fuente oficial, semioficial o directorio confiable.
- **Sede participante exacta:** local cuya participacion fisica en la edicion relevada esta confirmada. En esta capa no se afirma esa condicion salvo evidencia especifica; por defecto se marca `sucursal_participante_exacta_confirmada = no`.

## Fuentes usadas

{source_lines}

## Criterios de inclusion en mapa

- Direccion publica validada o suficientemente trazable.
- Coordenadas USIG dentro de CABA.
- Barrio y comuna validados con geometria local de DataGastro.
- Nivel de confianza `alta` o `media`.
- Sin datos personales, telefonos ni identificadores de servicios externos.

## Casos excluidos o no usados en mapa

{excluded_lines or "- No hubo casos excluidos con observacion especifica."}

## Casos pendientes

{pending_lines or "- No quedan marcas pendientes."}

## Limitaciones

- La base no prueba que cada sede haya participado fisicamente en la edicion relevada.
- La presencia de sedes por comuna no explica causalmente la procedencia del publico encuestado.
- Algunas marcas tienen multiples sucursales y pueden haber cambiado su red comercial.
- Las direcciones derivadas de directorios o fuentes no oficiales quedan en confianza media o pendiente.
- La geocodificacion USIG puede requerir revision manual si una direccion cambia de altura, calle o nombre comercial.

## Como leer correctamente el mapa

El mapa debe leerse como aproximacion a una red territorial potencial: lugares desde los cuales se podria reforzar difusion con QR, folleteria, historias, reposts o piezas por comuna. No debe leerse como mapa de asistencia, ventas, impacto ni participacion exacta de cada sucursal.

## Resumen operativo

- Marcas analizadas: {len(set(seed.instagram for seed in seed_rows))}.
- Sedes CABA geocodificadas con uso en mapa: {len(usable)}.
- Sedes o marcas pendientes/no usadas en mapa: {len(excluded)}.
- Fecha de generacion: {date.today().isoformat()}.
"""
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    METHOD_DOC.write_text(text, encoding="utf-8")


def read_public_comuna_ranking() -> list[dict[str, str]]:
    path = OUT_DIR / "ranking_comunal_cafecito.csv"
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def write_network_reading(comuna_rows: list[dict[str, Any]], barrio_rows: list[dict[str, Any]]) -> None:
    respuesta_rows = [row for row in read_public_comuna_ranking() if str(row.get("comuna", "")).isdigit()]
    top_sedes = ", ".join(f"Comuna {row['comuna']} ({row['cantidad_sedes']})" for row in comuna_rows[:5])
    top_respuestas = ", ".join(f"Comuna {row['comuna']} ({row['cantidad_respuestas']})" for row in respuesta_rows[:5])
    top_barrios = ", ".join(f"{row['barrio']} ({row['cantidad_sedes']})" for row in barrio_rows[:6])
    sedes_comunas = {str(row["comuna"]) for row in comuna_rows}
    respuestas_comunas = {str(row["comuna"]) for row in respuesta_rows}
    overlap = sorted(sedes_comunas & respuestas_comunas, key=lambda x: int(x))
    overlap_text = ", ".join(f"Comuna {c}" for c in overlap) if overlap else "sin coincidencias fuertes"
    text = f"""# Lectura red de cafeterias vs publico encuestado

Lectura exploratoria. No afirma causalidad entre ubicacion de sedes y respuestas del formulario.

## Comunas con mas sedes de cafeterias

{top_sedes or "Sin sedes geocodificadas."}

## Barrios con mas sedes de cafeterias

{top_barrios or "Sin barrios geocodificados."}

## Comunas con mas respuestas del formulario

{top_respuestas or "Sin ranking comunal de respuestas disponible."}

## Coincidencias y diferencias

Coincidencias entre comunas con sedes mapeadas y comunas con respuestas normalizadas: {overlap_text}.

Si Comuna 13 aparece fuerte en sedes y en respuestas, la lectura debe ser cautelosa: puede combinar cercania territorial, presencia de marcas, punto/horario de captacion y mayor visibilidad barrial. No prueba causalidad ni indica que las sedes hayan originado esas respuestas.

## Oportunidad de gestion

La red de locales puede funcionar como nodo fisico y digital de difusion: QR visibles, folleteria, historias, reposts y piezas por comuna. Para proximos relevamientos conviene preparar materiales por zona, coordinar publicaciones con marcas y medir captacion por punto/horario.

## Recomendacion

- Usar las comunas con mas sedes como base para pilotos de difusion fisica.
- Cruzar la red con respuestas solo como senal exploratoria.
- No publicar listados granulares si la fuente no esta validada.
- Mantener separada la base de sedes conocidas de la confirmacion de sede participante exacta.
"""
    LECTURA_RED_MD.write_text(text, encoding="utf-8")


def main() -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    GRAF_DIR.mkdir(parents=True, exist_ok=True)

    seed_rows = seeds()
    write_perplexity_doc()
    prelim = prelim_rows(seed_rows)
    write_csv(PRELIM_CSV, prelim, [
        "instagram",
        "nombre_comercial",
        "sede_nombre_o_referencia",
        "direccion_preliminar",
        "barrio_preliminar",
        "comuna_preliminar",
        "fuente_preliminar",
        "fuente_secundaria_preliminar",
        "nivel_confianza_preliminar",
        "observaciones_preliminares",
        "estado_validacion",
    ])

    geo = geocoded_rows(seed_rows)
    write_csv(GEOCODED_CSV, geo, [
        "instagram",
        "nombre_comercial",
        "sede_nombre_o_referencia",
        "direccion",
        "barrio",
        "comuna",
        "latitud",
        "longitud",
        "fuente_principal",
        "fuente_secundaria",
        "nivel_confianza",
        "tipo_punto",
        "usar_en_mapa",
        "sucursal_participante_exacta_confirmada",
        "observaciones",
    ])

    pending = pending_rows(seed_rows, geo)
    write_csv(PENDING_CSV, pending, [
        "instagram",
        "nombre_comercial",
        "motivo_pendiente",
        "fuente_disponible",
        "proximo_paso_sugerido",
        "observaciones",
    ])

    comuna = summary_rows(geo, "comuna", "comuna")
    barrio = summary_rows(geo, "barrio", "barrio")
    write_csv(RESUMEN_COMUNA_CSV, comuna, ["comuna", "cantidad_sedes", "cantidad_marcas", "porcentaje_sedes_mapa", "nota"])
    write_csv(RESUMEN_BARRIO_CSV, barrio, ["barrio", "cantidad_sedes", "cantidad_marcas", "porcentaje_sedes_mapa", "nota"])

    draw_map(geo)
    draw_ranking(comuna, "comuna", "cantidad_sedes", "Ranking comunal de sedes conocidas", RANKING_COMUNA_PNG)
    draw_ranking(barrio, "barrio", "cantidad_sedes", "Ranking barrial de sedes conocidas", RANKING_BARRIO_PNG)
    write_method_doc(seed_rows, geo, pending)
    write_network_reading(comuna, barrio)

    records = base.read_xlsx(base.XLSX)
    used = [row for row in geo if row.get("usar_en_mapa") == "si"]
    brands = len(set(seed.instagram for seed in seed_rows))
    print("=" * 72)
    print("Capa Cafecito - sedes de cafeterias")
    print(f"  Marcas analizadas: {brands}")
    print(f"  Respuestas formulario: {len(records)}")
    print(f"  Sedes CABA geocodificadas usadas en mapa: {len(used)}")
    print(f"  Marcas/sedes pendientes: {len(pending)}")
    print(f"  Mapa: {MAPA_PNG}")
    print("=" * 72)


if __name__ == "__main__":
    main()
