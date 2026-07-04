# -*- coding: utf-8 -*-
"""
Re-piloto Google Places — Fase 11 (PolosGastro).

EXPERIMENTO CONTROLADO. No forma parte del pipeline público F01-F05.

Reescribe el piloto anterior corrigiendo los problemas detectados en la auditoría de Tanda 1
(ver docs/polos_gastro/fase11_google_places_piloto/QA_AUDITORIA_TANDA1_GOOGLE_PLACES.md):

- Lee EXCLUSIVAMENTE la tabla preparada de Fase 11
  (outputs/.../fase11_google_places_preparacion/tablas/locales_semilla_preparados_para_google_places.csv).
  NO usa `locales_destacados_por_polo_seed.csv` ni ningún seed de experimento aislado.
- Usa la query preparada (`query_google_places_principal`), no una query cruda con el nombre
  largo del polo embebido.
- FieldMask con `location` para poder obtener lat/lon (imprescindible para mapa).
- Tres outputs en la ejecución real (ver PLAN_REPILOTO_TANDA1_FASE11.md):
    1. interno: todos los campos técnicos (place_id, rating, dirección exacta, nota_interna...).
    2. revisión visual: sanitizado pero con lat/lon SIEMPRE (aunque aceptado_para_mapa='no'),
       para inspección manual. NO es publicable final.
    3. publicable: solo puntos aceptados; lat/lon vacíos si aceptado_para_mapa='no'.
- Dry-run por defecto. La ejecución real requiere DOBLE CONFIRMACIÓN: --execute --confirm-real-api.
- Hard cap absoluto de 10 locales.

Doble confirmación:
- Sin banderas o con --confirm-real-api sola: dry-run (no llama API).
- Con --execute sola: frena con error controlado (no llama API) y pide --confirm-real-api.
- Con --execute --confirm-real-api: rama real (llama API) SOLO si además hay API key válida.

Seguridad:
- La API key SOLO se lee de entorno/.env. NUNCA se imprime, guarda ni loguea (ni enmascarada).
- El contenido del .env NUNCA se imprime. Solo se reporta "presente/ausente".
- FieldMask mínimo con location. NO se guarda raw JSON. place_id/rating/userRatingCount son
  internos y NUNCA viajan al output publicable.
- Costos: Places API (New) es PAGA. No ejecutar masivamente.
- Términos: revisar Google Maps Platform ToS antes de cachear/mezclar con otros mapas.

Estado al preparar este archivo: la rama real está IMPLEMENTADA pero NO se ejecutó. Correr el
re-piloto real solo tras aprobación humana (ver PLAN_REPILOTO_TANDA1_FASE11.md).
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

# --- Fuente válida ÚNICA: tabla preparada de Fase 11 ---
PREP = (ROOT / "outputs" / "polos_gastro" / "fase11_google_places_preparacion" / "tablas"
        / "locales_semilla_preparados_para_google_places.csv")

OUT_DIR = ROOT / "outputs" / "polos_gastro" / "fase11_google_places_piloto" / "tablas"

# Configuración de rutas por TANDA. El default 'repiloto_tanda1' preserva EXACTAMENTE el
# comportamiento previo (no rompe la Tanda 1 ya ejecutada). Cada tanda usa su propia muestra,
# queries y outputs; nunca se mezclan ni se pisan.
TANDAS = {
    "repiloto_tanda1": {
        "muestra": OUT_DIR / "muestra_repiloto_tanda1_fase11.csv",
        "queries": OUT_DIR / "queries_repiloto_tanda1_fase11.csv",
        "dryrun": OUT_DIR / "dryrun_repiloto_tanda1_fase11.csv",
        "interno": OUT_DIR / "resultados_repiloto_tanda1_interno.csv",
        "revision": OUT_DIR / "resultados_repiloto_tanda1_revision_visual.csv",
        "publicable": OUT_DIR / "resultados_repiloto_tanda1_publicable.csv",
    },
    "tanda2": {
        "muestra": OUT_DIR / "muestra_tanda2_fase11.csv",
        "queries": OUT_DIR / "queries_tanda2_fase11.csv",
        "dryrun": OUT_DIR / "dryrun_tanda2_fase11.csv",
        "interno": OUT_DIR / "resultados_tanda2_interno.csv",
        "revision": OUT_DIR / "resultados_tanda2_revision_visual.csv",
        "publicable": OUT_DIR / "resultados_tanda2_publicable.csv",
    },
    "corrida_ampliada": {
        "muestra": OUT_DIR / "muestra_corrida_ampliada_fase11.csv",
        "queries": OUT_DIR / "queries_corrida_ampliada_fase11.csv",
        "dryrun": OUT_DIR / "dryrun_corrida_ampliada_fase11.csv",
        "interno": OUT_DIR / "resultados_corrida_ampliada_interno.csv",
        "revision": OUT_DIR / "resultados_corrida_ampliada_revision_visual.csv",
        "publicable": OUT_DIR / "resultados_corrida_ampliada_publicable.csv",
    },
}

# Rutas activas (se fijan en main() según --tanda). Default: repiloto_tanda1.
MUESTRA = TANDAS["repiloto_tanda1"]["muestra"]
QUERIES = TANDAS["repiloto_tanda1"]["queries"]
OUT_DRYRUN = TANDAS["repiloto_tanda1"]["dryrun"]
OUT_INTERNO = TANDAS["repiloto_tanda1"]["interno"]
OUT_REVISION = TANDAS["repiloto_tanda1"]["revision"]
OUT_PUBLICABLE = TANDAS["repiloto_tanda1"]["publicable"]


def set_tanda(nombre: str) -> None:
    """Redirige las rutas globales a la tanda indicada. No mezcla outputs entre tandas."""
    global MUESTRA, QUERIES, OUT_DRYRUN, OUT_INTERNO, OUT_REVISION, OUT_PUBLICABLE
    cfg = TANDAS[nombre]
    MUESTRA, QUERIES = cfg["muestra"], cfg["queries"]
    OUT_DRYRUN, OUT_INTERNO = cfg["dryrun"], cfg["interno"]
    OUT_REVISION, OUT_PUBLICABLE = cfg["revision"], cfg["publicable"]

MAX_LOCALES_HARD_CAP = 10  # tope absoluto; no superar sin cambio de código en otra fase.

# Endpoint Places API (New) Text Search.
PLACES_URL = "https://places.googleapis.com/v1/places:searchText"
# FieldMask con location (para lat/lon). place_id/rating/userRatingCount son SOLO internos.
FIELD_MASK = (
    "places.id,places.displayName,places.formattedAddress,places.location,"
    "places.types,places.primaryType,places.businessStatus,"
    "places.rating,places.userRatingCount"
)

# Esquema interno (todo lo que se guarda para QA; NO todo es publicable).
COLUMNS_INTERNO = [
    "id_local_semilla", "polo", "subzona", "nombre_lugar_original", "query_google_places",
    "status_busqueda", "nombre_google", "direccion_google", "barrio_o_zona_inferida",
    "lat", "lon", "categoria_google", "business_status",
    "rating_interno", "user_ratings_total_interno", "google_place_id_interno",
    "confidence_match", "requiere_revision_manual", "aceptado_para_mapa",
    "mostrar_nombre_en_mapa", "mostrar_en_ficha", "nota_publica", "nota_interna", "fecha_consulta",
]

# Esquema de REVISIÓN VISUAL (interno, sanitizado): trae lat/lon aunque aceptado_para_mapa='no',
# para inspeccionar los puntos antes de aceptar/rechazar. NO es publicable final.
# SIN place_id, rating, user_ratings_total, raw JSON, API key, dirección exacta ni nota_interna.
COLUMNS_REVISION = [
    "id_local_semilla", "polo", "subzona", "nombre_lugar_original", "query_google_places",
    "nombre_google", "barrio_o_zona_inferida", "lat", "lon", "categoria_google",
    "business_status", "confidence_match", "requiere_revision_manual", "aceptado_para_mapa",
    "decision_automatica", "motivo_decision", "accion_recomendada", "nota_publica",
]

# Esquema publicable (SIN dirección exacta, place_id, rating, user_ratings_total, nota_interna).
COLUMNS_PUBLICABLE = [
    "polo", "subzona", "nombre_lugar", "tipo_gastronomico_estimado",
    "lat", "lon", "barrio_o_zona", "fuente_geolocalizacion", "origen",
    "mostrar_en_mapa", "mostrar_en_ficha", "nota_publica",
]

# Rechazos explícitos: sustitutos incorrectos conocidos (auditoría Tanda 1).
SUSTITUTOS_PROHIBIDOS = {
    "osaki": "Osaka",       # Osaki Sushi != Osaka
    "artemisia": "Aldo's",  # Artemisia != Aldo's
    "somos op": "Oporto",   # Somos OP (aseguradora) != Oporto
}
# Rubros no gastronómicos que descalifican un match (match por TOKEN exacto, no subcadena;
# 'store' se excluye a propósito porque 'food_store'/'grocery_store' acompañan a restaurantes).
CATEGORIAS_NO_GASTRONOMICAS = {
    "insurance_agency", "real_estate_agency", "lawyer", "doctor", "bank", "atm",
    "car_dealer", "lodging", "school", "hospital", "gas_station",
}
# Tokens que confirman rubro gastronómico (si primaryType/types incluye uno, no se rechaza por rubro).
CATEGORIAS_GASTRONOMICAS = {
    "restaurant", "cafe", "coffee_shop", "bar", "bakery", "meal_takeaway",
    "meal_delivery", "food", "fine_dining_restaurant", "pub",
}


def load_env_file(path: Path) -> dict:
    """Parser simple y seguro de .env. NUNCA imprime valores."""
    vals = {}
    if not path.exists():
        return vals
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        vals[k.strip()] = v.strip().strip('"').strip("'")
    return vals


def detect_api_key() -> tuple[str | None, str]:
    """Devuelve (key, fuente_descriptiva). NUNCA imprime la key ni el .env."""
    env_file = {}
    try:
        import dotenv  # type: ignore
        dotenv.load_dotenv(ROOT / ".env")
    except Exception:
        env_file = load_env_file(ROOT / ".env")
    for name in ("GOOGLE_MAPS_API_KEY", "GOOGLE_PLACES_API_KEY"):
        v = os.environ.get(name) or env_file.get(name)
        if v:
            return v, f"{name} (presente)"
    return None, "ausente"


def read_source() -> list[dict]:
    """Lee la muestra corregida si existe; si no, la tabla preparada de Fase 11 (primeros 10)."""
    src = MUESTRA if MUESTRA.exists() else PREP
    with src.open("r", encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    return rows, src


def build_query(row: dict) -> str:
    q = (row.get("query_google_places_principal") or "").strip()
    if q:
        return q
    # Fallback prudente: nombre + polo + Buenos Aires (nunca query cruda con polo largo).
    nombre = (row.get("nombre_lugar_original") or "").strip()
    polo = (row.get("polo") or "").strip()
    return f"{nombre} {polo} Buenos Aires".strip()


def write_csv(path: Path, columns: list[str], rows: list[dict]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=columns, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def load_queries_index() -> dict:
    """Indexa las queries limpias por id_local_semilla (riesgo y criterios). Opcional."""
    idx = {}
    if not QUERIES.exists():
        return idx
    with QUERIES.open("r", encoding="utf-8-sig", newline="") as fh:
        for q in csv.DictReader(fh):
            idx[q.get("id_local_semilla", "")] = q
    return idx


def dryrun_row(row: dict, qidx: dict) -> dict:
    q = qidx.get(row.get("id_local_semilla", ""), {})
    return {
        "id_local_semilla": row.get("id_local_semilla", ""),
        "nombre_lugar_original": row.get("nombre_lugar_original", ""),
        "polo": row.get("polo", ""),
        "subzona": row.get("subzona", ""),
        "query_final": (q.get("query_final") or build_query(row)).strip(),
        "query_alternativa": (q.get("query_alternativa")
                              or row.get("query_google_places_alternativa") or "").strip(),
        "existe_en_fase11": "si",
        "requiere_revision_manual": row.get("requiere_revision_manual", "si"),
        "riesgo_esperado": q.get("riesgo_match", row.get("motivo_ambiguedad", "")),
        "criterio_aceptacion": q.get(
            "criterio_aceptacion",
            "nombre coincide + zona/polo coincide + dentro de CABA + rubro gastronomico",
        ),
        "criterio_rechazo": q.get(
            "criterio_rechazo",
            "sustituto incorrecto, rubro no gastronomico, fuera de CABA o sucursal de otro polo",
        ),
    }


DRYRUN_COLUMNS = [
    "id_local_semilla", "nombre_lugar_original", "polo", "subzona",
    "query_final", "query_alternativa", "existe_en_fase11", "requiere_revision_manual",
    "riesgo_esperado", "criterio_aceptacion", "criterio_rechazo",
]


def do_dry_run(rows: list[dict], src: Path, listar_todas: bool = False) -> int:
    # El dry-run no llama API: puede listar TODAS las filas (modo ampliado/batch) o solo el
    # primer bloque de 10 (tandas). El gasto real lo acotan do_execute / do_execute_batch.
    seleccion = rows if listar_todas else rows[:MAX_LOCALES_HARD_CAP]
    qidx = load_queries_index()
    dr = [dryrun_row(r, qidx) for r in seleccion]
    write_csv(OUT_DRYRUN, DRYRUN_COLUMNS, dr)
    n_bloques = (len(dr) + MAX_LOCALES_HARD_CAP - 1) // MAX_LOCALES_HARD_CAP
    print(f"[dry_run] fuente: {src.name}")
    print(f"[dry_run] {len(dr)} queries preparadas ({n_bloques} bloque/s de {MAX_LOCALES_HARD_CAP}) escritas en:")
    print(f"  {OUT_DRYRUN}")
    print("[dry_run] No se realizó ninguna llamada a Google Places API.")
    return 0


def call_places(query: str, api_key: str):
    """Llama Places API (New) Text Search. Devuelve (dict_min, error_str).

    NO imprime la key ni la respuesta cruda. Solo devuelve los campos del FieldMask.
    """
    import requests  # import local: el dry-run no depende de requests
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,          # la key viaja en header; nunca se loguea
        "X-Goog-FieldMask": FIELD_MASK,
    }
    payload = {"textQuery": query, "maxResultCount": 1, "languageCode": "es", "regionCode": "AR"}
    try:
        resp = requests.post(PLACES_URL, headers=headers, data=json.dumps(payload), timeout=20)
    except Exception as exc:  # error de red: no exponer secretos
        return None, f"network_error: {type(exc).__name__}"
    if resp.status_code != 200:
        # No incluir headers (que contienen la key) en el mensaje.
        return None, f"http_{resp.status_code}"
    try:
        data = resp.json()
    except Exception:
        return None, "invalid_json"
    places = data.get("places") or []
    if not places:
        return {}, "no_match"
    p = places[0]
    loc = p.get("location") or {}
    # Solo campos del FieldMask; NO se guarda la response cruda completa.
    return {
        "google_place_id_interno": p.get("id", ""),
        "nombre_google": (p.get("displayName") or {}).get("text", ""),
        "direccion_google": p.get("formattedAddress", ""),
        "lat": loc.get("latitude", ""),
        "lon": loc.get("longitude", ""),
        "categoria_google": p.get("primaryType", "") or "|".join(p.get("types", []) or []),
        "tipos_google": "|".join(p.get("types", []) or []),
        "business_status": p.get("businessStatus", ""),
        "rating_interno": p.get("rating", ""),
        "user_ratings_total_interno": p.get("userRatingCount", ""),
    }, ""


def _es_sustituto_prohibido(nombre_semilla: str, nombre_google: str) -> bool:
    """True si el nombre de Google es un sustituto incorrecto conocido para esta semilla."""
    g = (nombre_google or "").lower().strip()
    s = (nombre_semilla or "").lower()
    for bad, semilla_marca in SUSTITUTOS_PROHIBIDOS.items():
        if bad in g and semilla_marca.lower().strip("'") in s.replace("'", ""):
            return True
    return False


def _dentro_de_caba(direccion: str) -> bool:
    d = (direccion or "").lower()
    return ("buenos aires" in d) or ("caba" in d) or ("c.a.b.a" in d) or ("cdad. autónoma" in d)


def _rubro_no_gastronomico(categoria: str, tipos: str) -> bool:
    """Rechaza por rubro solo si hay token no gastronómico y NINGÚN token gastronómico.
    Match por token exacto (separado por '|'), no por subcadena."""
    tokens = set()
    for campo in (categoria or "", tipos or ""):
        for t in campo.lower().split("|"):
            t = t.strip()
            if t:
                tokens.add(t)
    if tokens & CATEGORIAS_GASTRONOMICAS:
        return False  # hay evidencia gastronómica; no rechazar por rubro
    return bool(tokens & CATEGORIAS_NO_GASTRONOMICAS)


def clasificar(row_semilla: dict, data: dict) -> dict:
    """Aplica criterios prudentes. Devuelve dict con confidence_match, requiere_revision_manual,
    aceptado_para_mapa, mostrar_nombre_en_mapa, mostrar_en_ficha, nota_interna.

    Nunca marca aceptado_para_mapa='si' salvo confianza alta + zona compatible + rubro gastronómico.
    """
    nombre_semilla = row_semilla.get("nombre_lugar_original", "")
    nombre_google = data.get("nombre_google", "")
    categoria = data.get("categoria_google", "")
    tipos = data.get("tipos_google", "")
    direccion = data.get("direccion_google", "")
    business = (data.get("business_status", "") or "").upper()

    out = {
        "confidence_match": "baja",
        "requiere_revision_manual": "si",
        "aceptado_para_mapa": "no",
        "mostrar_nombre_en_mapa": "no",
        "mostrar_en_ficha": "no",
        "nota_interna": "",
        "decision_automatica": "revisar_manual",
        "motivo_decision": "",
        "accion_recomendada": "revisar manualmente",
    }

    # Rechazos duros primero.
    if _es_sustituto_prohibido(nombre_semilla, nombre_google):
        out["decision_automatica"] = "rechazar"
        out["motivo_decision"] = "sustituto incorrecto conocido (Osaki/Artemisia/Somos OP)"
        out["accion_recomendada"] = "rechazar o corregir_query"
        out["nota_interna"] = "rechazar/corregir_query: sustituto incorrecto conocido"
        return out
    if _rubro_no_gastronomico(categoria, tipos):
        out["decision_automatica"] = "rechazar"
        out["motivo_decision"] = "rubro no gastronomico"
        out["accion_recomendada"] = "rechazar"
        out["nota_interna"] = "rechazar: rubro no gastronomico"
        return out
    if direccion and not _dentro_de_caba(direccion):
        out["decision_automatica"] = "rechazar"
        out["motivo_decision"] = "fuera de CABA"
        out["accion_recomendada"] = "rechazar"
        out["nota_interna"] = "rechazar: fuera de CABA"
        return out

    # Similitud de nombre.
    a = (nombre_semilla or "").lower().strip()
    b = (nombre_google or "").lower().strip()
    ambigua = str(row_semilla.get("ambiguedad_si_no", "")).lower() == "si"

    if b and (a == b or a in b or b in a) and not ambigua:
        out["confidence_match"] = "alta"
    elif b and (a in b or b in a):
        out["confidence_match"] = "media"
    else:
        out["confidence_match"] = "baja"

    # business_status no operativo => siempre revisión.
    if business and business != "OPERATIONAL":
        out["requiere_revision_manual"] = "si"
        out["nota_interna"] = f"business_status={business}; requiere revision"

    # Decisión automática por confianza (prudente: nunca aceptar_para_mapa sin revisión humana).
    if out["confidence_match"] == "alta" and (not business or business == "OPERATIONAL"):
        out["decision_automatica"] = "aceptar_con_revision"
        out["motivo_decision"] = "nombre y zona coinciden; operativo"
        out["accion_recomendada"] = "validar y luego habilitar para mapa/ficha"
        out["requiere_revision_manual"] = "si"  # el diseño mantiene revisión antes de publicar
        out["aceptado_para_mapa"] = "no"         # se habilita a mano tras revisar
        out["mostrar_en_ficha"] = "no"
    elif out["confidence_match"] == "media":
        out["decision_automatica"] = "aceptar_con_revision"
        out["motivo_decision"] = "nombre coincide; zona/sucursal dudosa"
        out["accion_recomendada"] = "revisar sede/zona antes de aceptar"
    else:
        out["decision_automatica"] = "revisar_manual"
        out["motivo_decision"] = out["motivo_decision"] or "nombre parecido o zona dudosa"
        out["accion_recomendada"] = "revisar manualmente; posible corregir_query"
    return out


def build_interno_row(row_semilla: dict, query: str, data: dict, err: str, today: str,
                      qmeta: dict) -> dict:
    base = {c: "" for c in COLUMNS_INTERNO}
    base.update({
        "id_local_semilla": row_semilla.get("id_local_semilla", ""),
        "polo": row_semilla.get("polo", ""),
        "subzona": row_semilla.get("subzona", ""),
        "nombre_lugar_original": row_semilla.get("nombre_lugar_original", ""),
        "query_google_places": query,
        "requiere_revision_manual": "si",
        "aceptado_para_mapa": "no",
        "mostrar_nombre_en_mapa": "no",
        "mostrar_en_ficha": "no",
        "nota_publica": "Piloto experimental; requiere validación manual.",
        "fecha_consulta": today,
    })
    # Claves auxiliares para derivar la revisión visual (no están en COLUMNS_INTERNO,
    # así que write_csv con extrasaction="ignore" NO las escribe en el CSV interno).
    base["_decision_automatica"] = "revisar_manual"
    base["_motivo_decision"] = ""
    base["_accion_recomendada"] = "revisar manualmente"

    if err and not data:
        base["status_busqueda"] = f"error: {err}"
        base["nota_interna"] = f"sin datos ({err})"
        base["_motivo_decision"] = f"sin datos ({err})"
        base["_accion_recomendada"] = "reintentar o corregir_query"
        return base
    if err == "no_match":
        base["status_busqueda"] = "sin_coincidencia"
        base["nota_interna"] = "Google no devolvió coincidencia"
        base["_motivo_decision"] = "sin coincidencia"
        base["_accion_recomendada"] = "corregir_query"
        return base

    base["status_busqueda"] = "match"
    base["nombre_google"] = data.get("nombre_google", "")
    base["direccion_google"] = data.get("direccion_google", "")
    base["barrio_o_zona_inferida"] = row_semilla.get("polo", "")
    base["lat"] = data.get("lat", "")
    base["lon"] = data.get("lon", "")
    base["categoria_google"] = data.get("categoria_google", "")
    base["business_status"] = data.get("business_status", "")
    base["rating_interno"] = data.get("rating_interno", "")
    base["user_ratings_total_interno"] = data.get("user_ratings_total_interno", "")
    base["google_place_id_interno"] = data.get("google_place_id_interno", "")

    clas = clasificar(row_semilla, data)
    base["confidence_match"] = clas["confidence_match"]
    base["requiere_revision_manual"] = clas["requiere_revision_manual"]
    base["aceptado_para_mapa"] = clas["aceptado_para_mapa"]
    base["mostrar_nombre_en_mapa"] = clas["mostrar_nombre_en_mapa"]
    base["mostrar_en_ficha"] = clas["mostrar_en_ficha"]
    base["_decision_automatica"] = clas["decision_automatica"]
    base["_motivo_decision"] = clas["motivo_decision"]
    base["_accion_recomendada"] = clas["accion_recomendada"]
    # nota_interna combinada (riesgo esperado + veredicto de clasificación).
    riesgo = (qmeta.get("riesgo_match") or "").strip()
    base["nota_interna"] = "; ".join(x for x in [f"riesgo:{riesgo}" if riesgo else "",
                                                 clas["nota_interna"]] if x)
    return base


def build_revision_row(interno: dict) -> dict:
    """Deriva la fila de REVISIÓN VISUAL desde la interna. Trae lat/lon SIEMPRE (aunque
    aceptado_para_mapa='no'), para inspección manual. SIN place_id, rating, user_ratings_total,
    dirección exacta, nota_interna ni campos técnicos sensibles."""
    return {
        "id_local_semilla": interno.get("id_local_semilla", ""),
        "polo": interno.get("polo", ""),
        "subzona": interno.get("subzona", ""),
        "nombre_lugar_original": interno.get("nombre_lugar_original", ""),
        "query_google_places": interno.get("query_google_places", ""),
        "nombre_google": interno.get("nombre_google", ""),
        "barrio_o_zona_inferida": interno.get("barrio_o_zona_inferida", ""),
        "lat": interno.get("lat", ""),   # se conserva para revisión visual
        "lon": interno.get("lon", ""),   # se conserva para revisión visual
        "categoria_google": interno.get("categoria_google", ""),
        "business_status": interno.get("business_status", ""),
        "confidence_match": interno.get("confidence_match", ""),
        "requiere_revision_manual": interno.get("requiere_revision_manual", "si"),
        "aceptado_para_mapa": interno.get("aceptado_para_mapa", "no"),
        "decision_automatica": interno.get("_decision_automatica", "revisar_manual"),
        "motivo_decision": interno.get("_motivo_decision", ""),
        "accion_recomendada": interno.get("_accion_recomendada", "revisar manualmente"),
        "nota_publica": interno.get("nota_publica", ""),
    }


def build_publicable_row(interno: dict) -> dict:
    """Deriva la fila publicable desde la interna. SIN dirección exacta, place_id, rating,
    user_ratings_total, nota_interna ni campos técnicos."""
    return {
        "polo": interno.get("polo", ""),
        "subzona": interno.get("subzona", ""),
        "nombre_lugar": interno.get("nombre_lugar_original", ""),
        "tipo_gastronomico_estimado": "",  # a completar en revisión manual
        "lat": interno.get("lat", "") if interno.get("aceptado_para_mapa") == "si" else "",
        "lon": interno.get("lon", "") if interno.get("aceptado_para_mapa") == "si" else "",
        "barrio_o_zona": interno.get("barrio_o_zona_inferida", ""),
        "fuente_geolocalizacion": "Google Places (experimental, requiere validación)",
        "origen": "documento_semilla",
        "mostrar_en_mapa": interno.get("aceptado_para_mapa", "no"),
        "mostrar_en_ficha": interno.get("mostrar_en_ficha", "no"),
        "nota_publica": interno.get("nota_publica", ""),
    }


def do_execute(rows: list[dict], src: Path) -> int:
    """Rama real. Solo se llega aquí con --execute --confirm-real-api y key válida."""
    api_key, key_status = detect_api_key()
    print(f"[execute] API key: {key_status}")  # solo estado, nunca el valor
    if not api_key:
        print("ERROR: falta API key válida (GOOGLE_MAPS_API_KEY o GOOGLE_PLACES_API_KEY) por "
              "entorno o .env. No se realizó ninguna llamada.", file=sys.stderr)
        return 3
    try:
        import requests  # noqa: F401
    except Exception:
        print("ERROR: falta 'requests' para la ejecución real. No se realizó ninguna llamada.",
              file=sys.stderr)
        return 4

    seleccion = rows[:MAX_LOCALES_HARD_CAP]
    if len(rows) > MAX_LOCALES_HARD_CAP:
        print(f"[execute] la muestra tiene {len(rows)} filas; se cortan a {MAX_LOCALES_HARD_CAP} "
              f"por el hard cap.", file=sys.stderr)
    qidx = load_queries_index()
    today = date.today().isoformat()

    internos, n_req, n_match, n_err = [], 0, 0, 0
    for r in seleccion:
        qmeta = qidx.get(r.get("id_local_semilla", ""), {})
        query = (qmeta.get("query_final") or build_query(r)).strip()
        n_req += 1
        data, err = call_places(query, api_key)
        if err and not data:
            n_err += 1
        elif err != "no_match" and data:
            n_match += 1
        internos.append(build_interno_row(r, query, data or {}, err, today, qmeta))

    revisiones = [build_revision_row(i) for i in internos]
    publicables = [build_publicable_row(i) for i in internos]
    write_csv(OUT_INTERNO, COLUMNS_INTERNO, internos)
    write_csv(OUT_REVISION, COLUMNS_REVISION, revisiones)
    write_csv(OUT_PUBLICABLE, COLUMNS_PUBLICABLE, publicables)

    n_acept = sum(1 for i in internos if i.get("aceptado_para_mapa") == "si")
    print(f"[execute] requests: {n_req} | matches: {n_match} | errores: {n_err} | "
          f"aceptados_para_mapa: {n_acept}")
    print(f"[execute] interno:         {OUT_INTERNO}")
    print(f"[execute] revision_visual: {OUT_REVISION}")
    print(f"[execute] publicable:      {OUT_PUBLICABLE}")
    print("[execute] No se guardaron responses crudas ni la API key. Uso experimental; "
          "revisar manualmente antes de publicar.")
    return 0


def _leer_ids_ya_procesados(path: Path) -> set:
    """Ids ya presentes en el interno (para reanudar sin duplicar consultas)."""
    if not path.exists():
        return set()
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return {row.get("id_local_semilla", "") for row in csv.DictReader(fh)}


def _regenerar_derivados(internos: list[dict]) -> None:
    """Reescribe interno/revisión/publicable desde la lista completa de internos."""
    write_csv(OUT_INTERNO, COLUMNS_INTERNO, internos)
    write_csv(OUT_REVISION, COLUMNS_REVISION, [build_revision_row(i) for i in internos])
    write_csv(OUT_PUBLICABLE, COLUMNS_PUBLICABLE, [build_publicable_row(i) for i in internos])


def do_execute_batch(rows: list[dict], src: Path) -> int:
    """Ejecución REAL en bloques internos de MAX_LOCALES_HARD_CAP (10).

    - Procesa todos los locales de la muestra, pero de a 10 por bloque (nunca más de 10 por request
      loop; el cap NO se modifica).
    - Guarda progreso tras CADA bloque (no se pierde nada si falla un bloque posterior).
    - Reanudable: omite ids ya presentes en el interno; no reconsulta.
    - Registra error por fila en status_busqueda.
    - Nunca marca aceptado_para_mapa='si' automáticamente.
    """
    api_key, key_status = detect_api_key()
    print(f"[batch] API key: {key_status}")  # solo estado, nunca el valor
    if not api_key:
        print("ERROR: falta API key válida (GOOGLE_MAPS_API_KEY o GOOGLE_PLACES_API_KEY) por "
              "entorno o .env. No se realizó ninguna llamada.", file=sys.stderr)
        return 3
    try:
        import requests  # noqa: F401
    except Exception:
        print("ERROR: falta 'requests' para la ejecución real. No se realizó ninguna llamada.",
              file=sys.stderr)
        return 4

    qidx = load_queries_index()
    today = date.today().isoformat()

    # Reanudación: cargar internos previos y omitir ids ya procesados.
    ya = _leer_ids_ya_procesados(OUT_INTERNO)
    internos = []
    if ya:
        with OUT_INTERNO.open("r", encoding="utf-8-sig", newline="") as fh:
            internos = list(csv.DictReader(fh))
        print(f"[batch] reanudando: {len(ya)} ids ya en interno; se omiten.", file=sys.stderr)

    pendientes = [r for r in rows if r.get("id_local_semilla", "") not in ya]
    total = len(pendientes)
    if total == 0:
        print("[batch] no hay pendientes; nada que consultar.")
        return 0
    print(f"[batch] pendientes: {total} | bloques de {MAX_LOCALES_HARD_CAP}")

    n_req = n_match = n_err = 0
    bloque_i = 0
    for start in range(0, total, MAX_LOCALES_HARD_CAP):
        bloque = pendientes[start:start + MAX_LOCALES_HARD_CAP]
        bloque_i += 1
        for r in bloque:
            qmeta = qidx.get(r.get("id_local_semilla", ""), {})
            query = (qmeta.get("query_final") or build_query(r)).strip()
            n_req += 1
            data, err = call_places(query, api_key)
            if err and not data:
                n_err += 1
            elif err != "no_match" and data:
                n_match += 1
            internos.append(build_interno_row(r, query, data or {}, err, today, qmeta))
        # Guardado incremental tras cada bloque (no se pierde progreso).
        _regenerar_derivados(internos)
        print(f"[batch] bloque {bloque_i} ok ({len(bloque)} consultas) | acumulado req={n_req} "
              f"match={n_match} err={n_err}", file=sys.stderr)

    n_acept = sum(1 for i in internos if i.get("aceptado_para_mapa") == "si")
    print(f"[batch] TOTAL requests: {n_req} | matches: {n_match} | errores: {n_err} | "
          f"aceptados_para_mapa: {n_acept}")
    print(f"[batch] interno:         {OUT_INTERNO}")
    print(f"[batch] revision_visual: {OUT_REVISION}")
    print(f"[batch] publicable:      {OUT_PUBLICABLE}")
    print("[batch] No se guardaron responses crudas ni la API key. Revisar manualmente antes de publicar.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Re-piloto Google Places Fase 11 (dry_run por defecto).")
    parser.add_argument("--execute", action="store_true",
                        help="Intención de ejecución real. Requiere ADEMÁS --confirm-real-api.")
    parser.add_argument("--confirm-real-api", action="store_true",
                        help="Segunda confirmación obligatoria para llamar a la API real.")
    parser.add_argument("--max-locales", type=int, default=MAX_LOCALES_HARD_CAP,
                        help=f"Máximo de locales (cap absoluto {MAX_LOCALES_HARD_CAP}).")
    parser.add_argument("--tanda", choices=sorted(TANDAS.keys()), default="repiloto_tanda1",
                        help="Tanda a procesar (muestra/queries/outputs propios). Default: repiloto_tanda1.")
    parser.add_argument("--batch", action="store_true",
                        help="Ejecución en bloques internos de 10 (procesa toda la muestra; "
                             "reanudable). Requiere --execute --confirm-real-api.")
    args = parser.parse_args()

    set_tanda(args.tanda)
    print(f"[info] tanda: {args.tanda}", file=sys.stderr)

    if args.max_locales > MAX_LOCALES_HARD_CAP:
        print(f"[aviso] --max-locales {args.max_locales} excede el cap; se usa {MAX_LOCALES_HARD_CAP}.",
              file=sys.stderr)

    rows, src = read_source()
    if not rows:
        print(f"No se encontraron filas en {src}", file=sys.stderr)
        return 1

    # --confirm-real-api sin --execute: no ejecuta API, cae a dry-run.
    if args.confirm_real_api and not args.execute:
        print("[aviso] --confirm-real-api sin --execute no ejecuta API; se corre dry-run.",
              file=sys.stderr)
        return do_dry_run(rows, src, listar_todas=args.batch)

    # --execute sin la segunda confirmación: frena sin llamar API.
    if args.execute and not args.confirm_real_api:
        print("ERROR: doble confirmación requerida.", file=sys.stderr)
        print("Para ejecutar llamadas reales a Google Places usar también --confirm-real-api:",
              file=sys.stderr)
        print("  python scripts/polos_gastro/google_places/places_repiloto_fase11.py "
              "--execute --confirm-real-api", file=sys.stderr)
        print("No se realizó ninguna llamada a la API.", file=sys.stderr)
        return 2

    # Doble confirmación presente: rama real.
    if args.execute and args.confirm_real_api:
        if args.batch:
            return do_execute_batch(rows, src)
        return do_execute(rows, src)

    # Default: dry-run.
    return do_dry_run(rows, src, listar_todas=args.batch)


if __name__ == "__main__":
    raise SystemExit(main())
