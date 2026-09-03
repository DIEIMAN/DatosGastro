"""Los dos polos cortos · completar cuatro domicilios en Barracas y buscar dos nombres en La Boca.

QUÉ ES Y QUÉ NO ES
------------------
Es un trabajo chico y cerrado: **16 requests como tope duro**, autorizado por Diego el 21/08 con
la condición de quedar dentro del tramo gratuito. No es un barrido. Reabre el uso de Places sólo
para esta tarea: las decisiones `C-GB-NO-API-REOPEN` (no reabrir universos ni llamar sin
autorización) y `C-GB-ENV-EXC` (la lectura de `.env` fue una excepción acotada a
`GOOGLE_MAPS_API_KEY`) siguen vigentes y esta corrida es otra excepción acotada, asentada en
`BITACORA_PLACES.md`.

TRABAJO 1 · BARRACAS, CUATRO DOMICILIOS
---------------------------------------
Los cuatro establecimientos ya están identificados y tienen nombre y calle; **falta la altura**.
No se busca un nombre: se completa un número. Por eso el control es más fuerte que de costumbre —
se puede exigir coincidencia de nombre Y de calle, y sólo la altura queda libre—:

    (1) el punto devuelto cae a <= 50 m del nuestro;
    (2) el nombre devuelto se parece al nuestro por encima de `UMBRAL_NOMBRE`;
    (3) la calle devuelta es la misma calle que ya teníamos en `direccion_norm`;
    (4) la dirección devuelta trae altura.

Si (2) falla, **no se adopta y no se rebautiza nada**: se registra la discrepancia y el domicilio
queda incompleto. Es la regla de la compuerta de identidad, con el control de dirección recortado
a la calle porque la altura es justamente lo que se fue a buscar.

TRABAJO 2 · LA BOCA, DOS NOMBRES
--------------------------------
Nearby Search por coordenada, radio 30 m. Se adopta si:

    (1) el punto de Places cae a <= 30 m;
    (2) el rubro cae en el anillo gastronómico (núcleo o ampliado; los excluidos pierden);
    (3) si tenemos domicilio, coincide en calle Y en altura exacta;
    (4) si NO tenemos domicilio, tiene que haber **un solo** candidato gastronómico en el radio.
        Con dos no hay forma de saber de cuál de los dos puntos habla Places, y una atribución
        que no se puede sostener es el defecto que invalidó la ronda 8 entera.

`includedTypes` va vacío a propósito: en 30 m no hay riesgo real de desbordar los 20 resultados,
y un type mal escrito aborta una corrida paga. El rubro se filtra acá con el mismo anillo que usa
el resto del repositorio.

QUÉ SE GUARDA Y QUÉ NO
-----------------------
Todo lo que devuelve Places entra como **EVIDENCIA_EXTERNA_NO_CANONICA**, con `place_id`, fecha de
consulta, tipo de fuente y límite declarado. Places **no es una de las siete fuentes del
inventario** y no se suma a `fuentes_disponibles`: un nombre adoptado sigue siendo un registro de
una sola fuente propia más una evidencia externa.

El `place_id` se puede cachear sin vencimiento. **Las coordenadas no**: sólo se pueden retener
treinta días. Por eso la caché se escribe con `location` YA BORRADO y lo que queda en disco es la
distancia en metros, calculada en el momento del request. La caché sirve para no re-gastar; no
sirve para recomputar distancias, y así tiene que ser.

SKU Y PRECIO
------------
Máscara **sin** `regularOpeningHours` ni ningún campo Enterprise: las dos consultas caen en **Pro**
(Text Search Pro y Nearby Search Pro), 5.000 gratis por mes cada una. 16 requests contra ese cupo
son USD 0,00 salvo que el cupo de la cuenta ya esté gastado, cosa que este proceso no puede ver.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/places_completar_dos_polos.py            # seco
  .venv/Scripts/python.exe scripts/barrido_ciudad/places_completar_dos_polos.py --ejecutar
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
import time
import unicodedata
from datetime import date, datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from places_compuerta_identidad import UMBRAL_NOMBRE as UMBRAL_COMPUERTA  # noqa: E402
from places_compuerta_identidad import parecido_de_nombre  # noqa: E402
from places_control_zonas import (  # noqa: E402
    AMPLIADO,
    EXCLUIDOS,
    NUCLEO,
    cargar_dotenv,
    leer_api_key,
)
from ronda_8_places_incremental import altura_de, calle_de  # noqa: E402

BASE = (ROOT / "outputs/BARRIDO_CIUDAD_2026-08/desde_cowork"
        / "BASE_GASTRONOMICA_estado_2026-08-12.csv")
# Las 130 referencias interiores publicables, con su `estado_vigencia`. Se leen por dos
# motivos: son nombres que la ficha YA imprime —adoptarlos sería duplicarlos— y traen las
# que están CERRADAS, que es lo único que puede desmentir a un `OPERATIONAL` de Places.
REFERENCIAS = (ROOT / "outputs/polos_gastro/ATLAS_INFORMATIVO_39_2026-08-13/codex/atlas_informativo_v1"
               / "preparacion/REFERENCIAS_INTERIORES_PUBLICABLES.csv")
POLO_LA_BOCA = "POLO-Z52"
INTERNO = ROOT / "outputs/analisis_interno/places_dos_polos_2026-08-21"
CACHE = INTERNO / "_cache_places_dos_polos.json"

TEXT_SEARCH = "https://places.googleapis.com/v1/places:searchText"
NEARBY = "https://places.googleapis.com/v1/places:searchNearby"

# Ni un campo Enterprise. `location` se pide para medir la distancia y se descarta enseguida.
CAMPOS = ["places.id", "places.displayName", "places.formattedAddress",
          "places.location", "places.businessStatus", "places.types"]

TOPE_ABSOLUTO = 16          # lo que autorizó Diego. No se pasa sin editar este archivo.
UMBRAL_NOMBRE = 0.34        # el mismo de la compuerta
RADIO_BARRACAS_M = 50.0
RADIO_LA_BOCA_M = 30.0
PAUSA_S = 0.2

PRECIO_PRO_USD_1000 = 32.00
GRATIS_PRO_MENSUAL = 5000
FUENTE_PRECIO = ("developers.google.com/maps/billing-and-pricing/pricing: Text Search Pro y "
                 "Nearby Search Pro, 5.000 llamadas gratis por mes cada uno y USD 32,00 por 1.000 "
                 "después. NO es la consola de facturación de Diego.")

BARRACAS = ["LOC007567", "LOC007568", "LOC007571", "LOC008388"]
# El orden es el de prioridad y se gasta en ese orden. Primero los cuatro con domicilio
# completo, que son los únicos que se pueden verificar contra calle y altura. Después los
# siete del racimo central. `LOC021898` sube antes que los tres últimos porque está sobre
# otra cuadra: los otros tres caen a metros de puntos ya consultados y sabemos qué devuelven.
LA_BOCA = ["LOC000379", "LOC004607", "LOC005413", "LOC001411",
           "LOC007519", "LOC021867", "LOC021879", "LOC021883", "LOC021884",
           "LOC021886", "LOC021887",
           "LOC021898", "LOC021889", "LOC021890", "LOC021892"]


def metros(lat_a: float, lon_a: float, lat_b: float, lon_b: float) -> float:
    """Distancia en metros. Equirectangular: a 30 m de separación el error es despreciable."""
    r = 6371000.0
    x = math.radians(lon_b - lon_a) * math.cos(math.radians((lat_a + lat_b) / 2))
    y = math.radians(lat_b - lat_a)
    return math.hypot(x, y) * r


def clave_nombre(texto: str) -> str:
    """Nombre comparable: sin tildes, sin puntuación, en minúsculas.

    Sin esto, «Café Roma» no coincide con el «CAFE ROMA» del inventario y un nombre que ya está
    publicado entra como si fuera un hallazgo. Pasó: los tres nombres que Places devolvió en La
    Boca eran las tres referencias que la ficha ya imprime, y el control de duplicados los dejó
    pasar por la tilde.
    """
    plano = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", plano)).strip()


def alturas_de(domicilio: str) -> set[str]:
    """Todas las alturas del domicilio, no la primera.

    `direccion_norm` del padrón trae los accesos separados por `;` —«SUAREZ, JOSE LEON 276;
    SUAREZ, JOSE LEON 274» es una puerta con dos numeraciones—. Quedarse con la primera hace
    fallar la comparación contra la otra, que es la buena: así se rechazó Los 3 Amigos en el
    274 cuando el 274 era nuestro.
    """
    return {a for a in (altura_de(parte) for parte in str(domicilio).split(";")) if a}


def rectangulo(centro: tuple[float, float], radio_m: float) -> dict:
    """El `locationRestriction.rectangle` que envuelve al círculo de `radio_m` alrededor de centro.

    Las esquinas quedan más lejos que el radio, y está bien: el rectángulo sólo acota el pedido y
    el corte exacto lo hace el filtro de distancia, acá.
    """
    dlat = radio_m / 111_320.0
    dlon = radio_m / (111_320.0 * math.cos(math.radians(centro[0])))
    return {"low": {"latitude": centro[0] - dlat, "longitude": centro[1] - dlon},
            "high": {"latitude": centro[0] + dlat, "longitude": centro[1] + dlon}}


def anillo(tipos: list[str]) -> str:
    """Núcleo, ampliado o fuera del universo. Los excluidos ganan sobre todo lo demás."""
    conjunto = set(tipos or [])
    if conjunto & EXCLUIDOS:
        return "excluido"
    if conjunto & NUCLEO:
        return "nucleo"
    if conjunto & AMPLIADO:
        return "ampliado"
    return "fuera"


def cargar_base() -> pd.DataFrame:
    base = pd.read_csv(BASE, encoding="utf-8-sig", low_memory=False)
    return base.set_index("local_id")


class Corrida:
    """Cuenta requests, escribe caché después de cada uno y corta al primer error."""

    def __init__(self, clave: str | None, tope: int):
        self.clave, self.tope, self.hechos = clave, tope, 0
        self.error: str | None = None
        self.cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}

    def pedir(self, endpoint: str, cuerpo: dict, etiqueta: str, centro: tuple[float, float]):
        """Un request, o la caché. Devuelve (lugares, fuente) o (None, 'corte')."""
        llave = json.dumps([endpoint, cuerpo], ensure_ascii=False, sort_keys=True)
        if llave in self.cache:
            return self.cache[llave]["lugares"], "cache"
        if self.error:
            return None, "corte"
        if self.hechos >= self.tope:
            self.error = f"tope de {self.tope} requests alcanzado"
            return None, "corte"
        if not self.clave:
            # Cinturón además del tirante. Sin credencial no se sale a la red ni por accidente:
            # el reproceso desde caché corre sin clave y tiene que cortar acá, no fallar con un
            # 401 que sí cuenta como llamada.
            self.error = "sin credencial: reproceso desde caché, no se hacen llamadas"
            return None, "corte"

        import requests  # noqa: PLC0415
        try:
            resp = requests.post(
                endpoint,
                headers={"Content-Type": "application/json", "X-Goog-Api-Key": self.clave,
                         "X-Goog-FieldMask": ",".join(CAMPOS)},
                json=cuerpo, timeout=30)
        except Exception as exc:  # noqa: BLE001
            self.hechos += 1
            self.error = f"fallo de red en «{etiqueta}»: {type(exc).__name__}"
            return None, "corte"
        self.hechos += 1
        if resp.status_code != 200:
            # No se vuelca el cuerpo crudo: puede traer el eco de la request, y ahí va la key.
            try:
                mensaje = resp.json().get("error", {}).get("message", "")
            except Exception:  # noqa: BLE001
                mensaje = ""
            self.error = f"HTTP {resp.status_code} en «{etiqueta}»: {mensaje[:200]}"
            return None, "corte"

        lugares = []
        for lugar in (resp.json().get("places") or []):
            loc = lugar.get("location") or {}
            # La distancia se calcula ACÁ y la coordenada se descarta: retención de 30 días.
            distancia = (round(metros(centro[0], centro[1],
                                      loc.get("latitude"), loc.get("longitude")), 1)
                         if loc.get("latitude") is not None else None)
            lugares.append({
                "place_id": lugar.get("id", ""),
                "nombre_places": (lugar.get("displayName") or {}).get("text", ""),
                "direccion_places": lugar.get("formattedAddress", ""),
                "business_status": lugar.get("businessStatus", "SIN_ESTADO"),
                "types": lugar.get("types", []),
                "distancia_m": distancia,
            })
        self.cache[llave] = {
            "lugares": lugares, "etiqueta": etiqueta,
            "fecha_consulta": date.today().isoformat(),
            "momento_utc": datetime.now(timezone.utc).isoformat(timespec="seconds")}
        CACHE.write_text(json.dumps(self.cache, ensure_ascii=False, indent=1), encoding="utf-8")
        time.sleep(PAUSA_S)
        return lugares, "api"


# ------------------------------------------------------------------ trabajo 1 · Barracas
def trabajo_1(corrida: Corrida, base: pd.DataFrame, seco: bool) -> pd.DataFrame:
    filas = []
    for local_id in BARRACAS:
        fila = base.loc[local_id]
        centro = (float(fila.lat), float(fila.lon))
        consulta = (f"{fila.nombre}, {fila.direccion_norm}, Barracas, "
                    f"Ciudad Autónoma de Buenos Aires")
        # Text Search sólo admite `rectangle` en `locationRestriction` —el `circle` es de
        # `searchNearby` y de `locationBias`, y pedirlo acá devuelve HTTP 400—. Se acota con un
        # rectángulo de ±50 m y el corte redondo de 50 m lo hace después el filtro de distancia,
        # que es de este lado y no depende de la API.
        cuerpo = {"textQuery": consulta, "languageCode": "es", "regionCode": "AR",
                  "maxResultCount": 5,
                  "locationRestriction": {"rectangle": rectangulo(centro, RADIO_BARRACAS_M)}}
        salida = {"local_id": local_id, "nombre_inventario": fila.nombre,
                  "calle_inventario": fila.direccion_norm, "consulta": consulta,
                  "radio_m": RADIO_BARRACAS_M}
        if seco:
            filas.append({**salida, "resultado": "(corrida en seco)"})
            continue

        lugares, fuente = corrida.pedir(TEXT_SEARCH, cuerpo, f"barracas·{fila.nombre}", centro)
        if lugares is None:
            filas.append({**salida, "resultado": "NO_CONSULTADO",
                          "motivo": f"corte de la corrida · {corrida.error}"})
            continue

        evaluados = []
        for lugar in lugares:
            parecido = parecido_de_nombre(str(fila.nombre), lugar["nombre_places"])
            misma_calle = bool(calle_de(str(fila.direccion_norm))
                               & calle_de(lugar["direccion_places"]))
            evaluados.append({**lugar, "parecido_de_nombre": round(parecido, 3),
                              "misma_calle": misma_calle,
                              "altura": altura_de(lugar["direccion_places"])})
        salida["n_candidatos"] = len(evaluados)
        salida["origen_respuesta"] = fuente
        salida["fecha_consulta"] = date.today().isoformat()

        validos = [e for e in evaluados
                   if e["parecido_de_nombre"] >= UMBRAL_NOMBRE and e["misma_calle"]
                   and e["altura"] and (e["distancia_m"] or 0) <= RADIO_BARRACAS_M]
        if not validos:
            mejor = max(evaluados, key=lambda e: e["parecido_de_nombre"], default=None)
            if mejor is None:
                salida["resultado"] = "SIN_RESULTADO"
                salida["motivo"] = "Places no devolvió ningún lugar en el radio de 50 m"
            else:
                falta = []
                if mejor["parecido_de_nombre"] < UMBRAL_NOMBRE:
                    falta.append(f"el nombre no coincide (devolvió «{mejor['nombre_places']}», "
                                 f"parecido {mejor['parecido_de_nombre']})")
                if not mejor["misma_calle"]:
                    falta.append("la calle devuelta no es la que ya teníamos")
                if not mejor["altura"]:
                    falta.append("la dirección devuelta no trae altura")
                salida["resultado"] = "NO_ADOPTADO"
                salida["motivo"] = ("DISCREPANCIA · " + "; ".join(falta) + " · NO se adopta: el "
                                    "domicilio queda incompleto y el nombre no se cambia")
                salida["nombre_places"] = mejor["nombre_places"]
                # La dirección devuelta se registra aunque se rechace: sin ella la discrepancia
                # no se puede auditar y queda como un «no coincidió» sin contenido.
                salida["domicilio_places_rechazado"] = mejor["direccion_places"]
                salida["types_places"] = ";".join(mejor["types"][:4])
                salida["parecido_de_nombre"] = mejor["parecido_de_nombre"]
                salida["distancia_m"] = mejor["distancia_m"]
                salida["business_status"] = mejor["business_status"]
            filas.append(salida)
            continue

        elegido = max(validos, key=lambda e: e["parecido_de_nombre"])
        # El rubro no decide acá —el establecimiento ya está identificado y lo único que se busca
        # es la altura—, pero si Places lo clasifica fuera del anillo gastronómico hay que decirlo:
        # «Rotisería Panadería Candela» vuelve como `bakery` y `food_store`, y `food_store` es de
        # los excluidos del universo. No bloquea la altura; sí tiene que quedar a la vista.
        anillo_places = anillo(elegido["types"])
        filas.append({**salida, "resultado": "DOMICILIO_COMPLETADO",
                      "nombre_places": elegido["nombre_places"],
                      "domicilio_places": elegido["direccion_places"],
                      "altura": elegido["altura"],
                      "types_places": ";".join(elegido["types"][:4]),
                      "anillo_places": anillo_places,
                      "alerta_rubro": ("" if anillo_places in ("nucleo", "ampliado")
                                       else f"Places lo clasifica «{anillo_places}» del universo "
                                            "gastronómico; el rubro del inventario manda, pero "
                                            "conviene mirarlo"),
                      "parecido_de_nombre": elegido["parecido_de_nombre"],
                      "distancia_m": elegido["distancia_m"],
                      "business_status": elegido["business_status"],
                      "place_id": elegido["place_id"],
                      "estatus_dato": "EVIDENCIA_EXTERNA_NO_CANONICA",
                      "fuente_externa": "Google Places API (New) · Text Search Pro",
                      "limite_declarado": ("completa la altura, no acredita vigencia ni "
                                           "reemplaza al nombre del inventario; no se suma a "
                                           "fuentes_disponibles"),
                      "motivo": (f"coincide en nombre ({elegido['parecido_de_nombre']}), en calle "
                                 f"y a {elegido['distancia_m']} m")})
    return pd.DataFrame(filas)


def limite_de_fuentes(fila) -> str:
    """El límite declarado, con la cuenta de fuentes propias que la fila realmente tiene.

    CORRECCIÓN 01 (auditoría del 21/08). Este texto decía «UNA sola fuente propia» para todas las
    filas, incluida `LOC001411`, cuyo registro trae `F02;PERMISOS`: **dos**. La bitácora defendía
    esa fila justamente por tener dos y la columna afirmaba lo contrario. El conteo sale de
    `n_fuentes` de la base, que es el que ya colapsa las familias que se redistribuyen —`ATP;
    OVERTURE` cuenta 1, no 2— y no de contar los `;` del texto.
    """
    n = int(fila.n_fuentes)
    cuantas = "UNA sola fuente propia" if n == 1 else f"{n} fuentes propias"
    return (f"el registro sigue teniendo {cuantas} ({fila.fuentes}) más esta evidencia externa; "
            "Places NO se suma a fuentes_disponibles")


# ------------------------------------------------------------------ trabajo 2 · La Boca
def trabajo_2(corrida: Corrida, base: pd.DataFrame, seco: bool) -> pd.DataFrame:
    polo = base[base.polo.astype(str).str.contains("Almirante Brown", na=False)]
    refs = pd.read_csv(REFERENCIAS, encoding="utf-8-sig")
    refs = refs[refs.polo_uid == POLO_LA_BOCA]

    # Lo que la ficha ya imprime, por nombre y por puerta. Places devolvió las tres referencias
    # del polo y hay que reconocerlas aunque vengan con otro rótulo: «Bar La Buena Medida» es
    # «LA BUENA MEDIDA» de Suárez 101, y una comparación de cadena exacta no lo ve.
    ya_publicados = [(str(n), str(d)) for n, d in
                     zip(polo.nombre.fillna(""), polo.direccion_norm.fillna(""), strict=False)
                     if str(n).strip()]
    ya_publicados += [(str(n), str(d)) for n, d in
                      zip(refs.nombre.fillna(""), refs.direccion.fillna(""), strict=False)]

    # Las referencias que el repositorio da por CERRADAS. Un `OPERATIONAL` de Places no las
    # reabre: la ronda 8 midió que Places le dio OPERATIONAL a una quiebra judicial de 143 días,
    # y La Buena Medida es uno de sus tres tests de calibración —cerrada desde octubre de 2025 y
    # todavía OPERATIONAL—. Publicar un local cerrado es el error de Los Laureles otra vez.
    cerradas = {clave_nombre(n) for n in
                refs.loc[refs.estado_vigencia.eq("CERRADO"), "nombre"].dropna()}

    def duplica_lo_publicado(nombre: str, direccion: str):
        """(a quién duplica, por qué) o (None, None). Nombre parecido O misma puerta."""
        alturas = alturas_de(direccion)
        calles = calle_de(direccion)
        for publicado, puerta in ya_publicados:
            if parecido_de_nombre(publicado, nombre) >= UMBRAL_COMPUERTA:
                return publicado, "el nombre es el mismo"
            if puerta and alturas & alturas_de(puerta) and calles & calle_de(puerta):
                return publicado, "es la misma puerta (calle y altura)"
        return None, None

    nombres_del_polo = {clave_nombre(n) for n, _ in ya_publicados}

    # Un mismo `place_id` no se adopta dos veces: son dos puntos nuestros sobre un solo
    # establecimiento, y contarlo dos veces infla la lista con un local que no existe.
    adoptados: dict[str, str] = {}
    filas = []
    for local_id in LA_BOCA:
        fila = base.loc[local_id]
        centro = (float(fila.lat), float(fila.lon))
        domicilio = "" if pd.isna(fila.direccion_norm) else str(fila.direccion_norm)
        salida = {"local_id": local_id, "rubro_inventario": fila.rubro,
                  "domicilio_inventario": domicilio,
                  "fuentes_propias": fila.fuentes, "radio_m": RADIO_LA_BOCA_M}
        if seco:
            filas.append({**salida, "resultado": "(corrida en seco)"})
            continue
        cuerpo = {"languageCode": "es", "regionCode": "AR", "maxResultCount": 20,
                  "locationRestriction": {"circle": {
                      "center": {"latitude": centro[0], "longitude": centro[1]},
                      "radius": RADIO_LA_BOCA_M}}}
        lugares, fuente = corrida.pedir(NEARBY, cuerpo, f"laboca·{local_id}", centro)
        if lugares is None:
            filas.append({**salida, "resultado": "NO_CONSULTADO",
                          "motivo": f"corte de la corrida · {corrida.error}"})
            continue
        salida["origen_respuesta"] = fuente
        salida["fecha_consulta"] = date.today().isoformat()
        salida["n_devueltos"] = len(lugares)

        gastro = [x for x in lugares
                  if anillo(x["types"]) in ("nucleo", "ampliado")
                  and (x["distancia_m"] if x["distancia_m"] is not None else 999)
                  <= RADIO_LA_BOCA_M]
        salida["n_gastronomicos_en_radio"] = len(gastro)
        salida["devueltos_no_gastronomicos"] = "; ".join(
            f"{x['nombre_places']} [{anillo(x['types'])}]" for x in lugares if x not in gastro)

        if not gastro:
            filas.append({**salida, "resultado": "SIN_CANDIDATO",
                          "motivo": "ningún resultado gastronómico dentro de los 30 m"})
            continue

        if domicilio:
            calle_nuestra, nuestras = calle_de(domicilio), alturas_de(domicilio)
            validos = [x for x in gastro
                       if (calle_nuestra & calle_de(x["direccion_places"]))
                       and altura_de(x["direccion_places"]) in nuestras]
            criterio = "distancia <= 30 m + rubro + calle y altura exactas"
        else:
            validos = gastro if len(gastro) == 1 else []
            criterio = ("distancia <= 30 m + rubro + candidato único (no hay domicilio que "
                        "verifique)")
        salida["criterio"] = criterio

        if not validos:
            mejor = min(gastro, key=lambda x: x["distancia_m"] or 999)
            if domicilio:
                motivo = (f"el candidato más cercano —«{mejor['nombre_places']}», "
                          f"{mejor['direccion_places']}, a {mejor['distancia_m']} m— no coincide "
                          f"en calle y altura con «{domicilio}»")
            else:
                motivo = (f"{len(gastro)} candidatos gastronómicos en el radio y ningún domicilio "
                          f"para desambiguar: no se puede saber de cuál habla Places "
                          f"({'; '.join(x['nombre_places'] for x in gastro)})")
            filas.append({**salida, "resultado": "NO_ADOPTADO", "motivo": motivo,
                          "nombre_places": mejor["nombre_places"],
                          "domicilio_places_rechazado": mejor["direccion_places"],
                          "distancia_m": mejor["distancia_m"],
                          "business_status": mejor["business_status"]})
            continue

        elegido = min(validos, key=lambda x: x["distancia_m"] or 999)
        duplica, por_que_duplica = duplica_lo_publicado(elegido["nombre_places"],
                                                        elegido["direccion_places"])
        cerrado = next((c for c in cerradas
                        if parecido_de_nombre(c, elegido["nombre_places"]) >= UMBRAL_COMPUERTA),
                       None)
        ya_adoptado = adoptados.get(elegido["place_id"])
        if cerrado:
            veredicto, porque = "NO_ADOPTADO", (
                f"el repositorio da «{duplica or cerrado}» por CERRADO y Places dice "
                f"{elegido['business_status']}; un OPERATIONAL no acredita abierto y publicar un "
                "local cerrado es el error de Los Laureles")
        elif duplica:
            veredicto, porque = "NO_ADOPTADO", (
                f"duplica a «{duplica}», que la ficha ya publica: {por_que_duplica}. No es un "
                "nombre nuevo")
        elif ya_adoptado:
            veredicto, porque = "NO_ADOPTADO", (
                f"mismo place_id que {ya_adoptado}, que quedó más cerca: son dos puntos nuestros "
                "sobre un solo establecimiento y adoptarlo dos veces lo contaría doble")
        else:
            veredicto, porque = "NOMBRE_ADOPTADO", f"cumple {criterio}"
            adoptados[elegido["place_id"]] = local_id
        filas.append({**salida,
                      "resultado": veredicto,
                      "nombre_places": elegido["nombre_places"],
                      "domicilio_places": elegido["direccion_places"],
                      "distancia_m": elegido["distancia_m"],
                      "business_status": elegido["business_status"],
                      "types": ";".join(elegido["types"][:4]),
                      "place_id": elegido["place_id"],
                      "estatus_dato": "EVIDENCIA_EXTERNA_NO_CANONICA",
                      "fuente_externa": "Google Places API (New) · Nearby Search Pro",
                      "limite_declarado": limite_de_fuentes(fila),
                      "motivo": porque})
    return pd.DataFrame(filas)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ejecutar", action="store_true", help="gasta. Sin esto, corrida en seco")
    parser.add_argument("--tope", type=int, default=TOPE_ABSOLUTO, help="tope duro de requests")
    args = parser.parse_args()
    tope = min(args.tope, TOPE_ABSOLUTO)
    seco = not args.ejecutar

    INTERNO.mkdir(parents=True, exist_ok=True)
    base = cargar_base()

    print("LOS DOS POLOS CORTOS · PLACES, 16 REQUESTS COMO TOPE DURO")
    print("=" * 96)
    print(f"  precio declarado: {FUENTE_PRECIO}")
    print(f"  máscara sin campos Enterprise → SKU Pro ({GRATIS_PRO_MENSUAL:,} gratis/mes)")
    print(f"  tope de esta corrida: {tope}")
    print(f"  costo si el cupo Pro ya estuviera agotado: "
          f"USD {tope * PRECIO_PRO_USD_1000 / 1000:.2f}")
    print(f"  trabajo 1 · Barracas: {len(BARRACAS)} consultas (Text Search, radio 50 m)")
    print(f"  trabajo 2 · La Boca : hasta {tope - len(BARRACAS)} de {len(LA_BOCA)} puntos "
          f"(Nearby, radio 30 m)")
    if len(LA_BOCA) > tope - len(BARRACAS):
        print(f"  ATENCIÓN · quedan {len(LA_BOCA) - (tope - len(BARRACAS))} puntos SIN CONSULTAR "
              f"por el tope. Van listados como NO_CONSULTADO, no se descartan en silencio.")
    print("")

    clave = None
    # CORRECCIÓN 01 (auditoría del 21/08). El reproceso desde caché —`--ejecutar --tope 0`— no
    # puede salir a la red: `Corrida.pedir` corta en el tope antes de construir el request. Exigir
    # la credencial ahí dejaba el entregable irreproducible para quien no la tiene. La clave se
    # pide sólo cuando el tope permite gastar.
    if not seco and tope > 0:
        cargar_dotenv()
        clave = leer_api_key()
        if not clave:
            raise SystemExit("falta GOOGLE_MAPS_API_KEY (ni en el entorno ni en .env)")
    elif not seco:
        print("  REPROCESO DESDE CACHÉ · tope 0 · no se pide credencial y no se puede salir a "
              "la red\n")

    corrida = Corrida(clave, tope)
    t1 = trabajo_1(corrida, base, seco)
    t2 = trabajo_2(corrida, base, seco)

    t1.to_csv(INTERNO / "PLACES_BARRACAS_IRIARTE.csv", index=False, encoding="utf-8-sig")
    t2.to_csv(INTERNO / "PLACES_LA_BOCA_ALMIRANTE_BROWN.csv", index=False, encoding="utf-8-sig")

    if seco:
        print("CORRIDA EN SECO · 0 requests · 0 gasto. Plan escrito en los dos CSV.")
        return 0

    print("-" * 96)
    print("  TRABAJO 1 · BARRACAS")
    for f in t1.itertuples():
        detalle = getattr(f, "domicilio_places", "") or getattr(f, "motivo", "")
        print(f"   {f.local_id}  {str(f.nombre_inventario)[:26]:<28} {f.resultado:<22} "
              f"{str(detalle)[:60]}")
    print("")
    print("  TRABAJO 2 · LA BOCA")
    for f in t2.itertuples():
        print(f"   {f.local_id}  {str(f.rubro_inventario)[:14]:<16} {f.resultado:<16} "
              f"{str(getattr(f, 'nombre_places', '') or '')[:24]:<26} "
              f"{str(getattr(f, 'motivo', ''))[:52]}")
    adoptados = int((t2.resultado == "NOMBRE_ADOPTADO").sum()) if "resultado" in t2 else 0
    print("")
    print("-" * 96)
    print(f"  requests gastados: {corrida.hechos}   nombres adoptados en La Boca: {adoptados}")
    print(f"  costo si el cupo Pro estaba libre: USD 0,00 ({corrida.hechos} <= "
          f"{GRATIS_PRO_MENSUAL:,} gratis mensuales)")
    print(f"  costo si el cupo ya estaba agotado: USD "
          f"{corrida.hechos * PRECIO_PRO_USD_1000 / 1000:.2f}")
    if corrida.error:
        print(f"  SE CORTÓ · {corrida.error} · la caché guarda todo lo pagado")
    print(f"  salida en {INTERNO.relative_to(ROOT)} (Git la ignora)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
