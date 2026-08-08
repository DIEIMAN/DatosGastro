"""Ronda 8 · la pasada de Places, incremental, por prioridades y tolerante a corte.

QUÉ HACE
--------
Consulta el `business_status` de Places para los 71 establecimientos de
`lista_places_prioridad.csv`, **en un orden que Diego fijó** y guardando el resultado en disco
**después de cada request**. Si el crédito se corta a mitad de camino, lo hecho queda hecho y la
próxima corrida sigue donde ésta terminó: la caché es la que decide qué falta.

EL ORDEN, Y POR QUÉ ESE ORDEN
------------------------------
    (a) LOS TRES TESTS DE CALIBRACIÓN, siempre primero, aunque sea lo único que entre
    (b) los dos tests de reapertura
    (c) prioridad 1 · los seis hitos únicos sin verificar
    (d) prioridad 4 · los del catálogo sin verificar
    (e) el resto

Los tres tests son cierres conocidos a **nueve años, nueve meses y cinco meses**. Places es lento
con el cierre reciente y bueno con la decadencia lenta; si hay un corte de detección, cae adentro
de esa horquilla. **Sin los tres tests, el resto de la corrida no sabemos cuánto vale**: 60
`OPERATIONAL` no significan lo mismo si el detector no marca un local cerrado hace cinco meses.
Por eso van primero y no al final.

LOS DOS TESTS DE REAPERTURA responden otra pregunta: si Places arrastra el cierre viejo de un
local que volvió a abrir. El Tokio cerró en 2023 y reabrió en 2025; Los Laureles cerró en julio de
2026 y ya reabrió.

EL PRECIO, ANTES DEL PRIMER REQUEST
------------------------------------
No se puede leer la consola de facturación de Diego desde acá. Lo que sí se pudo verificar, y
queda escrito, es la lista de precios pública de Google Maps Platform:

    Text Search Enterprise    1.000 llamadas gratis por mes, después USD 35,00 por 1.000
    Text Search Pro           5.000 llamadas gratis por mes, después USD 32,00 por 1.000

**Esta corrida cae en Enterprise**, y no por elección: `places.regularOpeningHours` es un campo
Enterprise, y se factura al SKU más alto que toque la máscara. Los tres campos mínimos los fijó la
decisión 4 y no se recortan.

Las corridas de Places de agosto de este repositorio —control de zonas, techo, sonda— usaron una
máscara **sin** `regularOpeningHours`, así que consumieron Pro y **no** el cupo Enterprise. Con 71
requests contra 1.000 gratis mensuales, lo esperable es **USD 0,00**. No es una garantía: el cupo
es de la cuenta, no del repositorio, y este proceso no puede verlo. Por eso hay tope duro.

TOPE DURO
---------
`--tope` limita los requests de la corrida (por defecto los 71). El guion cuenta uno por uno,
corta al llegar y reporta dónde quedó. Y ante cualquier error de la API —cuota, facturación,
permiso— **se detiene en el acto** en vez de seguir intentando.

PUBLICACIÓN
-----------
La regla vigente no se toca: la respuesta cruda de Places —con `formattedAddress` y los horarios—
va a `outputs/analisis_interno/`, que Git ignora. Lo versionable es el veredicto por `hito_id`,
que es un campo nuestro.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/ronda_8_places_incremental.py            # seco
  .venv/Scripts/python.exe scripts/barrido_ciudad/ronda_8_places_incremental.py --ejecutar
  .venv/Scripts/python.exe scripts/barrido_ciudad/ronda_8_places_incremental.py --ejecutar --tope 5
"""
from __future__ import annotations

import argparse
import io
import json
import re
import sys
import time
import unicodedata
from datetime import date, datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from places_control_zonas import cargar_dotenv, leer_api_key  # noqa: E402
from polos_soporte import BARRIDO  # noqa: E402

HITOS = BARRIDO / "hitos"
COWORK = BARRIDO / "desde_cowork" / "evidencia_2026"
INTERNO = ROOT / "outputs" / "analisis_interno" / "places_vigencia_2026-08"

LISTA = COWORK / "lista_places_prioridad.csv"
CATALOGO_90 = COWORK / "catalogo_90_notables_cruzado.csv"
CAPA = HITOS / "hitos_capa_2026_r7.csv"

CACHE = INTERNO / "_cache_places_vigencia.json"        # respuesta cruda · Git la ignora
COLA_CSV = HITOS / "places_cola_r8.csv"                 # el plan, sin datos de Places
RESULTADO_CSV = HITOS / "places_resultado_r8.csv"       # veredictos, sin dirección de Places
TESTS_CSV = HITOS / "places_tests_calibracion_r8.csv"
INFORME = HITOS / "PLACES_R8.txt"

ENDPOINT = "https://places.googleapis.com/v1/places:searchText"
# Los tres que fijó la decisión 4, y ninguno más. `regularOpeningHours` es el que sube a
# Enterprise; se paga a propósito, porque es el campo que detecta retracción de horario.
CAMPOS = ["places.businessStatus", "places.formattedAddress", "places.regularOpeningHours"]

PRECIO_ENTERPRISE_USD_1000 = 35.00
GRATIS_ENTERPRISE_MENSUAL = 1000
FUENTE_PRECIO = ("developers.google.com/maps/billing-and-pricing/pricing, consultada el "
                 "2026-08-08: Text Search Enterprise, 1.000 gratis por mes y USD 35,00 por 1.000 "
                 "en el tramo 1.001-100.000. NO es la consola de facturación de Diego.")

TOPE_ABSOLUTO = 100  # ni con --tope se pasa de acá sin editar el archivo

# (a) y (b) · los cinco tests, con lo que sabemos de cada uno ANTES de preguntar.
TESTS = [
    ("calibracion", "Plaza Bar", "Florida 1005", "cerrado desde abril de 2017", 9 * 365,
     "CLOSED_PERMANENTLY"),
    ("calibracion", "La Buena Medida", "Suarez 101", "cerrada desde octubre de 2025", 280,
     "CLOSED_PERMANENTLY"),
    ("calibracion", "The New Brighton", "Sarmiento 645", "quiebra declarada el 18/03/2026", 143,
     "CLOSED_PERMANENTLY"),
    ("reapertura", "El Tokio", "Av. Alvarez Jonte 3550", "cerró en 2023, reabrió en 2025", 0,
     "OPERATIONAL"),
    ("reapertura", "Los Laureles", "Av. Iriarte 2290", "cerró en julio de 2026, ya reabrió", 0,
     "OPERATIONAL"),
]

LECTURA = {
    "CLOSED_PERMANENTLY": ("no", "v2b",
                           "acredita CERRADO con fuerza: es una afirmación positiva y difícil de "
                           "producir por error"),
    "CLOSED_TEMPORARILY": ("dudosa", "v2b",
                           "interrupción declarada; no es cierre definitivo"),
    "OPERATIONAL": ("", "",
                    "NO acredita abierto: dice que nadie reportó lo contrario. No mueve el "
                    "estado; se registra la consulta y su fecha"),
    "SIN_RESULTADO": ("", "", "Places no devolvió ningún lugar para la consulta"),
    "SIN_ESTADO": ("", "", "Places devolvió un lugar pero sin businessStatus"),
}


def sin_tildes(texto: str) -> str:
    limpio = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode().upper()
    return re.sub(r"\s+", " ", re.sub(r"[^A-Z0-9 ]", " ", limpio)).strip()


def nombre_limpio(texto: str) -> str:
    """Saca el paréntesis aclaratorio: «Los Galgos (Callao 501)» → «Los Galgos»."""
    return sin_tildes(re.sub(r"\([^)]*\)", " ", str(texto)))


def altura_de(direccion: str) -> str:
    numeros = re.findall(r"\b(\d{2,5})\b", str(direccion))
    return numeros[0] if numeros else ""


def calle_de(direccion: str) -> set[str]:
    """Los tokens de nombre de calle, sin altura, sin abreviaturas ni código postal.

    Sirve para separar dos cosas que el control ingenuo confunde: «Alsina 420» contra «Adolfo
    Alsina 416» es la misma puerta con otra numeración de fachada, y «Gorriti 5143» contra
    «Fitz Roy 1819» es otro local. Tratarlas igual convierte diez coincidencias buenas en once
    alarmas.
    """
    ruido = {"AV", "AVENIDA", "CDAD", "AUTONOMA", "DE", "BUENOS", "AIRES", "PRES", "DR",
             "CALLE", "LA", "EL", "LOS", "SAN", "DEL", "Y"}
    tokens = {t for t in sin_tildes(direccion).split()
              if t and not t[0].isdigit() and t not in ruido and len(t) > 2}
    return tokens


def identidad(consultada: str, devuelta: str) -> tuple[str, str]:
    """(veredicto, detalle) sobre si Places devolvió el establecimiento que le pedimos."""
    if not devuelta:
        return "sin respuesta", ""
    esperada, obtenida = altura_de(consultada), altura_de(devuelta)
    calles_a, calles_b = calle_de(consultada), calle_de(devuelta)
    misma_calle = bool(calles_a & calles_b)
    if not misma_calle:
        return "OTRA CALLE", f"consultada «{consultada}» · devuelta «{devuelta}»"
    if not esperada or not obtenida:
        return "sin altura comparable", ""
    salto = abs(int(esperada) - int(obtenida))
    if salto == 0:
        return "exacta", ""
    if salto <= 30:
        return "misma cuadra", f"{esperada} contra {obtenida} ({salto} de diferencia)"
    return "MISMA CALLE, OTRA CUADRA", f"{esperada} contra {obtenida} ({salto} de diferencia)"


def p_factory(buffer: io.StringIO):
    def p(*args_):
        print(*args_, file=buffer)
    return p


# --------------------------------------------------------------------------- la cola
def construir_cola(p) -> pd.DataFrame:
    """El plan de consultas, en el orden que fijó Diego, con la mejor dirección disponible.

    La dirección se busca en tres fuentes, en este orden: el cruce del catálogo de 90 —que es el
    que tiene la dirección exacta y el barrio oficial—, la lista de prioridad, y la capa de hitos.
    Sin una altura, la consulta de texto es ambigua y el resultado no se puede auditar.
    """
    lista = pd.read_csv(LISTA)
    catalogo = pd.read_csv(CATALOGO_90)
    capa = pd.read_csv(CAPA)

    por_catalogo = {nombre_limpio(r.establecimiento): (r.direccion, r.barrio_catalogo)
                    for r in catalogo.itertuples()}
    por_capa = {nombre_limpio(r.nombre): (r.direccion, r.hito_id)
                for r in capa.itertuples() if isinstance(r.direccion, str)}

    filas = []
    for orden, (clase, nombre, direccion, sabemos, dias, esperado) in enumerate(TESTS):
        filas.append({"orden": orden, "tramo": f"({'a' if clase == 'calibracion' else 'b'}) "
                                               f"test de {clase}",
                      "establecimiento": nombre, "direccion": direccion,
                      "barrio": "", "prioridad": 0, "clase_test": clase,
                      "lo_que_sabemos": sabemos, "dias_desde_el_hecho": dias,
                      "esperado": esperado})

    nombres_test = {nombre_limpio(t[1]) for t in TESTS}
    orden_prioridad = [1, 4, 2, 3]
    orden = len(filas)
    for prioridad in orden_prioridad:
        bloque = lista[lista.prioridad == prioridad]
        for fila in bloque.itertuples():
            clave = nombre_limpio(fila.establecimiento)
            if clave in nombres_test:
                continue
            direccion, barrio = "", fila.barrio if isinstance(fila.barrio, str) else ""
            fuente = ""
            if clave in por_catalogo:
                direccion, barrio_cat = por_catalogo[clave]
                barrio = barrio or barrio_cat
                fuente = "catalogo_90_notables_cruzado.csv"
            elif isinstance(fila.direccion, str) and altura_de(fila.direccion):
                direccion, fuente = fila.direccion, "lista_places_prioridad.csv"
            elif clave in por_capa:
                direccion, _ = por_capa[clave]
                fuente = "hitos_capa_2026_r7.csv"
            etiqueta = {1: "(c) prioridad 1 · hitos únicos",
                        4: "(d) prioridad 4 · catálogo sin verificar",
                        2: "(e) el resto · prioridad 2",
                        3: "(e) el resto · prioridad 3"}[prioridad]
            filas.append({"orden": orden, "tramo": etiqueta,
                          "establecimiento": fila.establecimiento, "direccion": direccion,
                          "barrio": barrio, "prioridad": prioridad, "clase_test": "",
                          "lo_que_sabemos": "", "dias_desde_el_hecho": "", "esperado": "",
                          "fuente_direccion": fuente})
            orden += 1

    cola = pd.DataFrame(filas)
    cola["hito_id"] = cola.establecimiento.map(
        lambda n: por_capa.get(nombre_limpio(n), ("", ""))[1])
    cola["altura_esperada"] = cola.direccion.map(altura_de)
    cola["consulta"] = cola.apply(
        lambda r: (f"{r.establecimiento}, {r.direccion}, Ciudad Autónoma de Buenos Aires, Argentina"
                   if r.direccion else
                   f"{r.establecimiento}, Ciudad Autónoma de Buenos Aires, Argentina"), axis=1)
    return cola


# --------------------------------------------------------------------------- la consulta
def consultar(clave: str, consulta: str) -> tuple[dict | None, str | None]:
    """Un request. Devuelve (respuesta, error). Nunca reintenta: si falla, se corta."""
    import requests

    try:
        respuesta = requests.post(
            ENDPOINT,
            headers={"Content-Type": "application/json", "X-Goog-Api-Key": clave,
                     "X-Goog-FieldMask": ",".join(CAMPOS)},
            json={"textQuery": consulta, "maxResultCount": 1,
                  "languageCode": "es", "regionCode": "AR"},
            timeout=30)
    except Exception as exc:  # noqa: BLE001
        return None, f"fallo de red: {exc}"
    if respuesta.status_code != 200:
        return None, f"HTTP {respuesta.status_code}: {respuesta.text[:220]}"
    return respuesta.json(), None


def main() -> int:  # noqa: C901
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ejecutar", action="store_true", help="gasta. Sin esto, corrida en seco")
    parser.add_argument("--tope", type=int, default=71, help="tope duro de requests")
    args = parser.parse_args()

    buffer = io.StringIO()
    p = p_factory(buffer)
    tope = min(args.tope, TOPE_ABSOLUTO)

    cola = construir_cola(p)
    INTERNO.mkdir(parents=True, exist_ok=True)
    cola.drop(columns=["consulta"]).to_csv(COLA_CSV, index=False, encoding="utf-8")

    p("RONDA 8 · PLACES, CORRIDA INCREMENTAL POR PRIORIDADES")
    p("=" * 100)
    p("")
    p("  EL PRECIO, ANTES DEL PRIMER REQUEST")
    p("")
    p("  No se puede leer la consola de facturación de Diego desde este proceso. Lo que sí se")
    p("  verificó y queda escrito es la lista de precios pública:")
    p("")
    p(f"      {FUENTE_PRECIO}")
    p("")
    p("  ESTA CORRIDA CAE EN ENTERPRISE, y no por elección: `places.regularOpeningHours` es campo")
    p("  Enterprise y se factura al SKU más alto que toque la máscara. Los tres campos los fijó la")
    p("  decisión 4.")
    p("")
    p("  Las corridas de Places de agosto de este repositorio —control de zonas, techo de zona,")
    p("  sonda de barrios— usan una máscara SIN `regularOpeningHours`: consumieron Pro, no el cupo")
    p(f"  Enterprise. Con {len(cola)} requests contra {GRATIS_ENTERPRISE_MENSUAL:,} gratis")
    p("  mensuales, lo esperable es USD 0,00. NO es una garantía: el cupo es de la cuenta y este")
    p("  proceso no puede verlo. Por eso hay tope duro y por eso se corta al primer error.")
    p("")
    p(f"  tope de esta corrida: {tope} requests")
    p(f"  costo máximo si el cupo Enterprise ya estuviera agotado: "
      f"USD {tope * PRECIO_ENTERPRISE_USD_1000 / 1000:.2f}")
    p("")
    p("-" * 100)
    p("  LA COLA")
    p("")
    for tramo, bloque in cola.groupby("tramo", sort=False):
        sin_direccion = int((bloque.direccion == "").sum())
        p(f"      {tramo:<44} {len(bloque):>3} consultas"
          + (f"  ({sin_direccion} sin altura)" if sin_direccion else ""))
    p(f"      {'TOTAL':<44} {len(cola):>3}")
    p("")
    sin_altura = cola[cola.altura_esperada == ""]
    if len(sin_altura):
        p(f"  {len(sin_altura)} sin altura resuelta — se consultan igual pero su resultado NO se")
        p("  puede auditar contra la dirección devuelta y queda marcado como no verificable:")
        for fila in sin_altura.itertuples():
            p(f"      {fila.establecimiento}")
        p("")

    # La lista dice 71 y el reparto por prioridad da otra cosa: se reporta, no se ajusta.
    lista_cruda = pd.read_csv(LISTA)
    p(f"  NOTA DE CONTEO · `lista_places_prioridad.csv` trae {len(lista_cruda)} filas, repartidas "
      f"{dict(lista_cruda.prioridad.value_counts().sort_index())}.")
    p("  La tarea habla de «los 58 del catálogo» para la prioridad 4 y en el archivo hay "
      f"{int((lista_cruda.prioridad == 4).sum())}.")
    p("  Se corre lo que trae el archivo.")
    p("")

    if not args.ejecutar:
        p("-" * 100)
        p("  CORRIDA EN SECO · 0 requests · 0 gasto")
        p("")
        p("  Para ejecutar:")
        p("      .venv/Scripts/python.exe scripts/barrido_ciudad/ronda_8_places_incremental.py "
          "--ejecutar")
        texto = buffer.getvalue()
        INFORME.write_text(texto, encoding="utf-8")
        print(texto)
        return 0

    cargar_dotenv()
    clave = leer_api_key()
    if not clave:
        raise SystemExit("falta GOOGLE_MAPS_API_KEY (ni en el entorno ni en .env)")

    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    hechos, corte, error_corte = 0, None, None
    resultados = []

    p("-" * 100)
    p("  EJECUCIÓN")
    p("")

    for fila in cola.itertuples():
        consulta = fila.consulta
        if consulta in cache:
            guardado = cache[consulta]
        else:
            if hechos >= tope:
                corte, error_corte = fila.orden, f"tope de {tope} requests alcanzado"
                break
            respuesta, error = consultar(clave, consulta)
            hechos += 1
            if error:
                corte, error_corte = fila.orden, error
                p(f"   ✗ CORTE en el request {hechos} · {fila.establecimiento}")
                p(f"     {error}")
                break
            guardado = {"respuesta": respuesta,
                        "fecha_consulta": date.today().isoformat(),
                        "momento_utc": datetime.now(timezone.utc).isoformat(timespec="seconds")}
            cache[consulta] = guardado
            # Se escribe DESPUÉS DE CADA REQUEST: si el crédito se corta, lo pagado queda guardado.
            CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
            time.sleep(0.2)

        lugares = (guardado["respuesta"] or {}).get("places") or []
        if not lugares:
            estado = "SIN_RESULTADO"
            direccion_devuelta, horarios = "", {}
        else:
            estado = lugares[0].get("businessStatus") or "SIN_ESTADO"
            direccion_devuelta = lugares[0].get("formattedAddress", "")
            horarios = lugares[0].get("regularOpeningHours", {}) or {}
        nuevo_estado, nivel, lectura = LECTURA.get(estado, ("", "", "estado no previsto"))
        veredicto_id, detalle_id = identidad(str(fila.direccion), direccion_devuelta)
        altura_ok = veredicto_id in ("exacta", "misma cuadra")
        resultados.append({
            "orden": fila.orden, "tramo": fila.tramo, "prioridad": fila.prioridad,
            "establecimiento": fila.establecimiento, "hito_id": fila.hito_id,
            "direccion_consultada": fila.direccion,
            "business_status": estado,
            # La dirección que devuelve Places NO se versiona: la regla de publicación manda que
            # el dato crudo de Places quede en carpeta interna. Se versiona si coincidió.
            "identidad": veredicto_id, "identidad_detalle": detalle_id,
            "publica_horarios": "si" if horarios.get("periods") else "no",
            "abierto_24h": "si" if horarios.get("openNow") is True and not horarios.get("periods")
                           else "",
            "vigencia_fecha_consulta": guardado["fecha_consulta"],
            "estado_que_acredita": nuevo_estado, "nivel": nivel, "lectura": lectura,
            "clase_test": fila.clase_test, "esperado": fila.esperado,
            "lo_que_sabemos": fila.lo_que_sabemos,
            "dias_desde_el_hecho": fila.dias_desde_el_hecho,
        })
        marca = {"CLOSED_PERMANENTLY": "✗", "CLOSED_TEMPORARILY": "~",
                 "OPERATIONAL": "·"}.get(estado, "?")
        if fila.clase_test:
            acierta = "ACIERTA" if estado == fila.esperado else "FALLA"
            p(f"   {marca} [{fila.clase_test.upper():<11}] {fila.establecimiento:<20} "
              f"{estado:<20} esperado {fila.esperado:<20} {acierta}")
        else:
            p(f"   {marca} {fila.establecimiento[:34]:<36} {estado:<20} "
              f"altura={'ok' if altura_ok else '—'}")

    tabla = pd.DataFrame(resultados)
    if len(tabla):
        # Los datos crudos, con dirección devuelta y horarios, a la carpeta interna.
        crudo = []
        for fila in cola.itertuples():
            if fila.consulta not in cache:
                continue
            lugares = (cache[fila.consulta]["respuesta"] or {}).get("places") or []
            crudo.append({"establecimiento": fila.establecimiento,
                          "consulta": fila.consulta,
                          "formatted_address": lugares[0].get("formattedAddress", "")
                                               if lugares else "",
                          "business_status": lugares[0].get("businessStatus", "")
                                             if lugares else "",
                          "opening_hours": json.dumps(
                              lugares[0].get("regularOpeningHours", {}), ensure_ascii=False)
                                             if lugares else "",
                          "fecha_consulta": cache[fila.consulta]["fecha_consulta"]})
        pd.DataFrame(crudo).to_csv(INTERNO / "places_crudo_r8.csv", index=False, encoding="utf-8")
        tabla.to_csv(RESULTADO_CSV, index=False, encoding="utf-8")
        tests = tabla[tabla.clase_test != ""]
        tests.to_csv(TESTS_CSV, index=False, encoding="utf-8")

    p("")
    p("-" * 100)
    p("  LO QUE DIJERON LOS CINCO TESTS · ES LO MÁS IMPORTANTE DE LA CORRIDA")
    p("")
    tests = tabla[tabla.clase_test != ""] if len(tabla) else pd.DataFrame()
    if not len(tests):
        p("   no llegó a correrse ninguno.")
    else:
        p(f"   {'establecimiento':<20} {'lo que sabemos':<38} {'días':>6}  "
          f"{'Places dice':<22} {'':<8}")
        for fila in tests.itertuples():
            acierta = "ACIERTA" if fila.business_status == fila.esperado else "FALLA"
            dias = fila.dias_desde_el_hecho
            p(f"   {fila.establecimiento:<20} {str(fila.lo_que_sabemos)[:36]:<38} "
              f"{dias if dias != '' else '—':>6}  {fila.business_status:<22} {acierta:<8}")
        p("")
        calib = tests[tests.clase_test == "calibracion"]
        aciertos = calib[calib.business_status == calib.esperado]
        p(f"   De los tres cierres conocidos, Places marca {len(aciertos)} de {len(calib)}.")
        if len(calib) and len(aciertos) < len(calib):
            fallados = calib[calib.business_status != calib.esperado]
            mas_viejo = fallados.dias_desde_el_hecho.max() if len(fallados) else 0
            p(f"   EL CORTE DE DETECCIÓN ESTÁ POR ENCIMA DE LOS {mas_viejo} DÍAS: hay un cierre de")
            p("   esa antigüedad que Places no marca. Todo `OPERATIONAL` de esta corrida se lee")
            p("   con ese límite encima.")
        elif len(calib):
            p("   Los tres, incluido el de cinco meses. El detector llega hasta ahí; qué pasa con")
            p("   un cierre más nuevo que cinco meses sigue sin medirse, porque no hay caso.")
    p("")

    p("-" * 100)
    p("  CONSUMO Y CORTE")
    p("")
    p(f"   requests efectivamente gastados en esta corrida: {hechos}")
    p(f"   consultas resueltas (incluye caché de corridas previas): {len(tabla)} de {len(cola)}")
    p(f"   costo si el cupo Enterprise estaba libre: USD 0,00 "
      f"({hechos} ≤ {GRATIS_ENTERPRISE_MENSUAL:,} gratis mensuales)")
    p(f"   costo si el cupo ya estaba agotado: USD "
      f"{hechos * PRECIO_ENTERPRISE_USD_1000 / 1000:.2f}")
    p("   cuál de los dos fue, sólo lo dice la consola de facturación.")
    p("")
    if corte is not None:
        pendiente = cola[cola.orden >= corte]
        p(f"   SE CORTÓ en el orden {corte} · {error_corte}")
        p(f"   quedan {len(pendiente)} consultas sin hacer, desde «"
          f"{pendiente.iloc[0].establecimiento}».")
        p("   La caché guarda todo lo pagado: volver a correr sigue desde ahí sin re-gastar.")
    else:
        p("   NO se cortó: la cola entró completa.")
    p("")

    if len(tabla):
        p("-" * 100)
        p("  EL REPARTO")
        p("")
        for valor, n in tabla.business_status.value_counts().items():
            p(f"      {valor:<24} {n:>4}   {LECTURA.get(valor, ('', '', ''))[2][:56]}")
        p("")
        p("-" * 100)
        p("  CONTROL DE IDENTIDAD · ¿Places devolvió el local que le pedimos?")
        p("")
        for valor, n in tabla.identidad.value_counts().items():
            p(f"      {valor:<28} {n:>4}")
        p("")
        dudosas = tabla[tabla.identidad.isin(["OTRA CALLE", "MISMA CALLE, OTRA CUADRA",
                                              "sin respuesta"])]
        cerca = tabla[tabla.identidad == "misma cuadra"]
        p(f"  {len(cerca)} devolvieron la misma calle con una altura a menos de 30 números —"
          " numeración de")
        p("  fachada, ochava o portal contiguo—. Se dan por buenas y quedan registradas:")
        for fila in cerca.itertuples():
            p(f"      {fila.establecimiento[:30]:<32} {fila.identidad_detalle}")
        p("")
        if len(dudosas):
            p(f"  {len(dudosas)} NO se pueden atribuir al establecimiento sin revisarlas a mano:")
            for fila in dudosas.itertuples():
                p(f"      {fila.establecimiento[:30]:<32} [{fila.identidad}] "
                  f"{fila.identidad_detalle}")
        else:
            p("  Ninguna quedó en otra calle ni en otra cuadra.")
        p("")
        p("  NADA DE ESTO SE APLICA SOLO A LA CAPA. Un CLOSED_PERMANENTLY es la afirmación más")
        p("  cara de equivocar y FD-12 ya probó que una marca de cierre puede ser falsa.")

    p("")
    p(f"  crudo (con dirección y horarios) en: {INTERNO.relative_to(ROOT)} · Git lo ignora")
    p(f"  veredictos versionables en: {RESULTADO_CSV.name}")

    texto = buffer.getvalue()
    INFORME.write_text(texto, encoding="utf-8")
    print(texto)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
