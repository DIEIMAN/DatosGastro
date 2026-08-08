"""Ronda 7 · las decisiones de Diego sobre la capa de hitos, y Monserrat medido.

QUÉ HACE
--------
Aplica a `hitos_capa_2026_r6.csv` lo que las veinte decisiones del 07/08 cambian **sobre los
hitos** —no sobre la geometría, que va en `ronda_7_geometria_ampliaciones.py`, ni sobre la matriz,
que va en `ronda_7_familias_de_vias.py`— y mide las tres cosas que Monserrat y San Cristóbal
pedían medir.

    TAREA 2   decisiones 1 a 4 de criterio, en lo que tocan a un hito
    TAREA 5   Monserrat: qué de los diez «hitos nuevos» era nuevo de verdad, el núcleo de Salta
              medido, el conteo de San Cristóbal y la discrepancia de barrio de Bar Seddon
    TAREA 6   decisiones 18, 19 y 20 de publicación
    TAREA 7   el enum de vigencia, las dos contradicciones y el bloque de Almagro

LO QUE NO SE COPIA
------------------
El insumo `hitos_nuevos_monserrat.csv` afirma que cinco Bares Notables de Monserrat **no estaban
en nuestra base**. Se comprueba contra la capa antes de dar de alta nada: dar de alta un hito que
ya existe es fabricar un duplicado, y los duplicados inflan la vía B, que es justo la vía que esta
ronda está tratando de medir bien.

Igual con «nueve de los noventa Bares Notables están en Monserrat»: se cuenta contra el polígono
administrativo del barrio, no se transcribe.

EL CRITERIO DE CONTEO DE LA VÍA B NO SE TOCA EN ESTA RONDA
-----------------------------------------------------------
La decisión 18 agrega el campo `registro_oficial` y confirma que los Restaurantes Icónicos cuentan
para la vía B —ya contaban, por `tipo`—. El campo se agrega para publicar; **la regla de conteo
sigue siendo la misma que en las rondas 3 y 4**, a propósito: esta ronda cambia la *escala* a la
que se mide la vía B y ese es el único cambio que tiene que poder leerse en el número.

Google Places: 0 requests. USIG: normalizador sobre direcciones nuevas y `/datos_utiles` sobre los
puntos que hay que adjudicar a un barrio, ambos cacheados.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/ronda_7_hitos_y_decisiones.py
"""
from __future__ import annotations

import csv
import io
import json
import sys
import time
from pathlib import Path

import geopandas as gpd
import pandas as pd
import requests
from shapely.geometry import Point
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from polos_soporte import (  # noqa: E402
    BARRIDO,
    CALLEJERO,
    CRS_GEOGRAFICO,
    CRS_METRICO,
    barrios,
    puntos_base,
    sin_tildes,
)

HITOS = BARRIDO / "hitos"
SEIS_VIAS = BARRIDO / "seis_vias"
COWORK = BARRIDO / "desde_cowork" / "evidencia_2026"

CAPA_R6 = HITOS / "hitos_capa_2026_r6.csv"
OUT_CSV = HITOS / "hitos_capa_2026_r7.csv"
CAMBIOS_CSV = HITOS / "cambios_ronda_7.csv"
INFORME_TXT = HITOS / "RONDA_7_HITOS.txt"
MONSERRAT_CSV = HITOS / "monserrat_hitos_r7.csv"
NUCLEO_CSV = SEIS_VIAS / "nucleo_de_salta_r7.csv"
SANCRIS_CSV = SEIS_VIAS / "san_cristobal_densidad_r7.csv"
PENDIENTES_CSV = HITOS / "veredictos_no_aplicados_r7.csv"

CACHE_USIG = BARRIDO / "dataset_bares_notables" / "_cache_usig.json"
CACHE_DATOS_UTILES = SEIS_VIAS / "_cache_usig_datos_utiles.json"
USIG_NORMALIZAR = "https://servicios.usig.buenosaires.gob.ar/normalizar/"
USIG_DATOS_UTILES = "https://ws.usig.buenosaires.gob.ar/datos_utiles/"

FECHA = "2026-08-08"

# --------------------------------------------------------------------------- enums declarados
#
# TAREA 7 · el enum de vigencia no tenía `probablemente_abierto` y por eso once veredictos
# quedaron sin aplicar desde la ronda 6. Entra como valor propio y NO como un `dudosa` con nota:
# «nadie miró» y «miré, encontré, y no alcanza para v1-v3» son dos estados distintos y el segundo
# es información.
VIGENCIA_ESTADOS = {
    "si", "no", "probablemente_abierto", "dudosa", "sin_verificar", "en_disputa",
    "en_riesgo", "senalado_no_cerrado", "cerrado_con_reapertura_anunciada",
}
# v3b · decisión 3. Check-in de consumo con fecha y usuario, últimos 90 días. Es v3 en fuerza
# —rastro presencial fechado y atribuido— y lleva letra propia porque no es prosa: no se le puede
# aplicar la prueba de refrito que se le aplica a una reseña.
VIGENCIA_NIVELES = {"v1", "v2", "v2b", "v3", "v3b", "v4", "v5", "ninguno", ""}

# Decisión 18. `sitio_interes_cultural`, `APH` y `ley_especifica` ya viajaban en las columnas de
# patrimonio; el campo los unifica para la ficha. Un hito puede tener más de uno: Miramar tiene
# dos y Bar Seddon tiene dos.
REGISTRO_POR_TIPO = {
    "Bar Notable": "bar_notable",
    "Restaurante Icónico": "restaurante_iconico",
    "Pizzería emblemática": "pizzeria_emblematica",
}
REGISTROS_VALIDOS = {
    "bar_notable", "restaurante_iconico", "pizzeria_emblematica",
    "sitio_interes_cultural", "APH", "ley_especifica",
}

# Decisión 20 · se publica la del anexo y se registra la variante. Las cuatro que Diego listó.
DOBLE_NUMERACION = {
    "H009": ("Carlos Calvo 595", "599", "Bar El Federal · misma esquina de Perú y Carlos Calvo"),
    "H074": ("Av. de Mayo 1265", "1271", "Los 36 Billares · finca con doble numeración"),
    "H054": ("Av. Corrientes 3787", "3797", "El Símbolo · finca de esquina con doble numeración"),
    "H004": ("Av. Benito Perez Galdos 201", "207", "Bar Boca a Boca"),
}

# TAREA 5 · el núcleo de Salta. Cuatro establecimientos reconocidos sobre un cruce. Dos de los
# cuatro NO son hitos de la capa —El Globo no tiene ningún registro oficial y Plaza Asturias
# tampoco— y por eso el núcleo se mide aparte: es una medición de convergencia, no de vía B.
NUCLEO_SALTA = [
    ("Bar Iberia", "Avenida de Mayo 1196", "bar_notable"),
    ("Plaza Asturias", "Avenida de Mayo 1199", ""),
    ("El Globo", "Hipolito Yrigoyen 1199", ""),
    ("El Imparcial", "Hipolito Yrigoyen 1201", "restaurante_iconico"),
]

# Las altas cuya dirección de fuente es una esquina sin altura. Se resuelven por cruce de ejes.
OCHAVAS = {"DIR-026": ("ENTRE RIOS AV.", "INDEPENDENCIA AV.")}

# TAREA 5 · el conteo que Diego pidió antes de decidir San Cristóbal (decisión 11).
SAN_CRISTOBAL_TRAMOS = [
    ("SAN JUAN AV.", 1900, 2100),
    ("INDEPENDENCIA AV.", 2300, 2500),
]
# Media cuadra a cada lado del eje: el conteo es de continuidad sobre la calle, no de área.
BUFFER_CONTEO_M = 75


def p_factory(buffer: io.StringIO):
    def p(*args_):
        print(*args_, file=buffer)
    return p


# ----------------------------------------------------------------------------- capa
def cargar_capa() -> tuple[list[str], list[dict]]:
    with open(CAPA_R6, encoding="utf-8", newline="") as f:
        lector = csv.DictReader(f)
        return list(lector.fieldnames or []), list(lector)


def por_id(filas: list[dict], hito_id: str) -> dict:
    for fila in filas:
        if fila["hito_id"] == hito_id:
            return fila
    raise KeyError(f"{hito_id} no está en {CAPA_R6.name}")


def set_campo(cambios: list[dict], fila: dict, campo: str, valor: str, motivo: str,
              tarea: str) -> None:
    antes = fila.get(campo, "")
    if str(antes) == str(valor):
        return
    fila[campo] = valor
    cambios.append({"hito_id": fila["hito_id"], "nombre": fila["nombre"], "campo": campo,
                    "valor_antes": antes, "valor_despues": valor, "motivo": motivo,
                    "tarea": tarea, "fecha": FECHA})


# ----------------------------------------------------------------------------- USIG
def _cache(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def normalizar(direccion: str, cache: dict) -> tuple[float, float] | tuple[None, None]:
    """Punto de una dirección por el normalizador de USIG. Servicio público del GCBA, cacheado."""
    if direccion not in cache:
        respuesta = requests.get(USIG_NORMALIZAR,
                                 params={"direccion": direccion, "geocodificar": "true"},
                                 timeout=25)
        respuesta.raise_for_status()
        cache[direccion] = respuesta.json()
        time.sleep(0.35)
    normalizadas = cache[direccion].get("direccionesNormalizadas") or []
    if not normalizadas:
        return None, None
    coord = normalizadas[0].get("coordenadas") or {}
    if not coord:
        return None, None
    return float(coord["y"]), float(coord["x"])


def datos_utiles(x: float, y: float, cache: dict) -> dict:
    clave = f"{x},{y}"
    if clave not in cache:
        respuesta = requests.get(USIG_DATOS_UTILES,
                                 params={"x": x, "y": y, "formato": "json"}, timeout=25)
        respuesta.raise_for_status()
        cache[clave] = respuesta.json()
        time.sleep(0.35)
    return cache[clave]


def barrio_de(respuesta: dict) -> str:
    for clave in ("barrio", "Barrio", "nombre_barrio"):
        if isinstance(respuesta, dict) and respuesta.get(clave):
            return str(respuesta[clave])
    return ""


# ----------------------------------------------------------------------------- tramos
def punto_de_ochava(callejero: gpd.GeoDataFrame, calle_a: str, calle_b: str):
    """El cruce de dos calles, resuelto por geometría del callejero.

    Para las direcciones que la fuente da como esquina y sin altura —«ochava de Entre Ríos e
    Independencia»— el normalizador de USIG no devuelve nada, y dejar el hito sin punto lo saca
    de toda medición espacial sin que se note. El cruce de los dos ejes es un dato del callejero
    oficial, no una estimación.
    """
    a = callejero[callejero.clave == sin_tildes(calle_a)]
    b = callejero[callejero.clave == sin_tildes(calle_b)]
    if a.empty or b.empty:
        return None
    from shapely.ops import nearest_points
    eje_a, eje_b = unary_union(list(a.geometry)), unary_union(list(b.geometry))
    p1, p2 = nearest_points(eje_a, eje_b)
    if p1.distance(p2) > 40:  # no se tocan: no es un cruce
        return None
    return Point((p1.x + p2.x) / 2, (p1.y + p2.y) / 2)


def tramo_por_altura(callejero: gpd.GeoDataFrame, calle: str, desde: int, hasta: int):
    """Los segmentos de la calle cuyo rango de alturas se solapa con [desde, hasta].

    El callejero trae cuatro columnas de altura —par e impar, inicio y fin— porque la numeración
    corre por acera. Se toma el solape con cualquiera de las dos aceras: un tramo con la vereda
    impar dentro del rango y la par afuera sigue siendo el tramo pedido.
    """
    seg = callejero[callejero.clave == sin_tildes(calle)].copy()
    if seg.empty:
        return None, 0
    def solapa(fila) -> bool:
        for ini, fin in ((fila.alt_izqini, fila.alt_izqfin), (fila.alt_derini, fila.alt_derfin)):
            if ini and fin and max(ini, fin) >= desde and min(ini, fin) <= hasta:
                return True
        return False
    elegidos = seg[seg.apply(solapa, axis=1)]
    if elegidos.empty:
        return None, 0
    return unary_union(list(elegidos.geometry)), len(elegidos)


def main() -> int:  # noqa: C901 — es un guion de tareas, no un algoritmo
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    buffer = io.StringIO()
    p = p_factory(buffer)

    if not CAPA_R6.exists():
        raise SystemExit("falta hitos_capa_2026_r6.csv — correr la ronda 6")

    campos, filas = cargar_capa()
    for nuevo in ("registro_oficial", "direccion_variante", "vigencia_fecha_consulta",
                  "nota_ronda_7"):
        if nuevo not in campos:
            campos.append(nuevo)
    for fila in filas:
        for nuevo in ("registro_oficial", "direccion_variante", "vigencia_fecha_consulta",
                      "nota_ronda_7"):
            fila.setdefault(nuevo, "")
    cambios: list[dict] = []

    cache_norm = _cache(CACHE_USIG)
    cache_du = _cache(CACHE_DATOS_UTILES)

    p("RONDA 7 · LAS DECISIONES SOBRE LA CAPA DE HITOS, Y MONSERRAT MEDIDO")
    p("=" * 100)
    p("")
    p(f"  capa de entrada: {CAPA_R6.name} · {len(filas)} hitos")
    p("  Google Places: 0 requests. USIG: normalizador y /datos_utiles, cacheados.")
    p("")

    # ================================================================= TAREA 7a · el enum
    p("-" * 100)
    p("  TAREA 7a · EL ENUM DE VIGENCIA")
    p("")
    p("  `probablemente_abierto` entra como estado propio del enum, y `v3b` como nivel.")
    p("  Es lo que destraba los once veredictos que la ronda 6 dejó sin aplicar: el bloqueo no")
    p("  era de evidencia, era de vocabulario.")
    p("")
    p(f"  estados admitidos ({len(VIGENCIA_ESTADOS)}): "
      + ", ".join(sorted(VIGENCIA_ESTADOS)))
    p(f"  niveles admitidos ({len(VIGENCIA_NIVELES) - 1}): "
      + ", ".join(sorted(n for n in VIGENCIA_NIVELES if n)))
    p("")

    # ================================================= TAREA 2 · las cuatro de criterio
    p("-" * 100)
    p("  TAREA 2 · LAS DECISIONES DE CRITERIO QUE TOCAN UN HITO")
    p("")

    # --- decisión 2 · el reporteo a nivel programa no es v1
    imparcial = por_id(filas, "ICO-002")
    set_campo(cambios, imparcial, "vigencia_verificada", "probablemente_abierto",
              "DECISIÓN 2: el reporteo a nivel PROGRAMA no acredita v1. La nota de Info "
              "Gastronómica del 07/07/2026 entrevista al presidente de la AHRCC sobre los 16 "
              "Restaurantes Icónicos, no sobre El Imparcial. Baja a v4 (listado fechado dentro "
              "de 180 días) y el veredicto que corresponde a un v4 solo es probablemente_abierto.",
              "TAREA_2")
    set_campo(cambios, imparcial, "vigencia_nivel", "v4", "", "TAREA_2")
    set_campo(cambios, imparcial, "vigencia_fuente",
              "Info Gastronómica 07/07/2026 (reporteo sobre el programa, no sobre el local) · "
              "La Nación 07/07/2026", "", "TAREA_2")
    set_campo(cambios, imparcial, "vigencia_fecha", "2026-07-07", "", "TAREA_2")
    set_campo(cambios, imparcial, "nota_ronda_7",
              "Ancla contra refritos, registrada: una reseña de marzo de 2026 menciona que sirve "
              "con un robot mozo. Cualquier nota «reciente» que no lo mencione es sospechosa.",
              "", "TAREA_2")

    tancat = por_id(filas, "ICO-015")
    set_campo(cambios, tancat, "vigencia_verificada", "si",
              "DECISIÓN 2: Tancat NO baja. El reporteo de programa se le cae igual que a El "
              "Imparcial, pero tiene una pieza propia que el otro no tiene: Instagram "
              "@tancattasca, confirmado por Diego el 07/08/2026. v2 por vía propia.",
              "TAREA_2")
    set_campo(cambios, tancat, "vigencia_nivel", "v2", "", "TAREA_2")
    set_campo(cambios, tancat, "vigencia_fuente",
              "Instagram @tancattasca · verificación humana de Diego, 07/08/2026", "", "TAREA_2")
    set_campo(cambios, tancat, "vigencia_fecha", "2026-08-07", "", "TAREA_2")

    # --- decisión 3 · v3b
    perla = por_id(filas, "H069")
    set_campo(cambios, perla, "vigencia_verificada", "si",
              "DECISIÓN 3: los check-ins de consumo con fecha y usuario cuentan, con nivel propio "
              "v3b. La Perla de Caminito tiene dos check-ins independientes de Untappd dentro de "
              "ventana (20/05 y 17/05/2026) más uno del 12/03. Sin la decisión caía a dudoso sin "
              "escalón intermedio: lo siguiente que tiene es de diciembre de 2025.",
              "TAREA_2")
    set_campo(cambios, perla, "vigencia_nivel", "v3b", "", "TAREA_2")
    set_campo(cambios, perla, "vigencia_fuente",
              "Untappd, check-ins del 20/05/2026 (Patrick Reurink) y del 17/05/2026 "
              "(Francisco Montanaro)", "", "TAREA_2")
    set_campo(cambios, perla, "vigencia_fecha", "2026-05-20", "", "TAREA_2")
    set_campo(cambios, perla, "nota_ronda_7",
              "Es la de CAMINITO, no la del Once: el anexo tiene una sola entrada «La Perla» y es "
              "la n.68, La Boca. La Perla del Once cerró el 14/01/2017.", "", "TAREA_2")

    p("  decisión 2 · El Imparcial (ICO-002) → probablemente_abierto · v4")
    p("  decisión 2 · Tancat (ICO-015) NO baja → si · v2, por Instagram propio")
    p("  decisión 3 · La Perla de Caminito (H069) → si · v3b (nivel nuevo)")
    p("  decisión 4 · Places: autorizado y NO ejecutado en esta corrida. Ver el informe al pie.")
    p("")

    # ================================================= TAREA 7b · las dos contradicciones
    p("-" * 100)
    p("  TAREA 7b · LAS DOS CONTRADICCIONES ENTRE ARCHIVOS")
    p("")

    simbolo = por_id(filas, "H054")
    set_campo(cambios, simbolo, "vigencia_verificada", "si",
              "Dos niveles distintos entre archivos: v4 probablemente_abierto en la tanda B "
              "(Canal 26, 06/05/2026) y v2 verificado_abierto en el cierre del día (Diego, "
              "07/08/2026). PREVALECE EL MÁS NUEVO. No es un empate de fuentes: es una pieza "
              "posterior que hace irrelevante a la anterior.",
              "TAREA_7")
    set_campo(cambios, simbolo, "vigencia_nivel", "v2", "", "TAREA_7")
    set_campo(cambios, simbolo, "vigencia_fuente",
              "verificación humana · Diego, 07/08/2026", "", "TAREA_7")
    set_campo(cambios, simbolo, "vigencia_fecha", "2026-08-07", "", "TAREA_7")

    cedron = por_id(filas, "DIR-011")
    set_campo(cambios, cedron, "vigencia_verificada", "dudosa",
              "CONTRADICCIÓN, NO DATO FALTANTE: la capa lo tenía en `si` y el registro de la "
              "tanda lo da `dudoso`. Prevalece `dudoso`, y el motivo es asimétrico: la capa nunca "
              "tuvo verificación —el `si` venía heredado del catálogo— y la tanda sí buscó y no "
              "encontró. Un `si` sin verificación no empata contra una búsqueda con resultado.",
              "TAREA_7")
    set_campo(cambios, cedron, "vigencia_nivel", "ninguno", "", "TAREA_7")
    set_campo(cambios, cedron, "vigencia_sentido_duda",
              "la ficha de Tripadvisor está desactualizada y su propia reseña más reciente lo "
              "dice: «el teléfono NO CORRESPONDE A LA PIZZERÍA Y LOS DATOS TAMPOCO». Nada "
              "posterior a 2025-06-27.", "", "TAREA_7")
    set_campo(cambios, cedron, "vigencia_fecha", "2025-06-27", "", "TAREA_7")
    set_campo(cambios, cedron, "vigencia_fuente", "", "", "TAREA_7")

    p("  El Símbolo (H054) · v4 tanda B vs v2 cierre del día → prevalece v2, si")
    p("  El Cedrón (DIR-011) · `si` en la capa vs `dudoso` en la tanda → prevalece dudosa")
    p("")

    # ================================================= TAREA 7c · el bloque de Almagro
    p("-" * 100)
    p("  TAREA 7c · LOS CUATRO VEREDICTOS DE ALMAGRO, EN BLOQUE")
    p("")

    almagro_bloque = [
        ("H071", "si", "v3",
         "Tripadvisor .com, reseña del 07/07/2026 (JulieS, 5/5), con mención a los vitrales y a "
         "la vitrina de panadería; segunda del 27/06/2026 en .com.ar + confirmación de Diego",
         "2026-07-07",
         "Ancla contra refrito: la reseña del 27/06 describe interacción con el personal de sala "
         "en el momento de la visita. Testimonio de servicio en mesa, no reciclable de material "
         "promocional."),
        ("H044", "si", "v3",
         "Tripadvisor, reseña del 16/06/2026 (Claudio S., visitante de Madrid), verificada por "
         "doble vía en las fichas .com y .com.ar con la misma fecha y el mismo usuario",
         "2026-06-16",
         "Ancla contra refrito: la SUPERMILANESA es ítem de carta, no lugar común de guía."),
        # El Símbolo ya quedó resuelto arriba por la contradicción; se deja constancia acá para
        # que el bloque de Almagro se lea completo.
        ("H054", "si", "v2", None, None, None),
        ("H063", "probablemente_abierto", "v5",
         "Agencia NOVA, 07/08/2026: acto de entrega de diplomas a los doce nuevos Bares Notables "
         "el 04/08/2026, con La Orquídea entre los distinguidos. El organizador es el GCBA y es "
         "el GCBA el que nombra al establecimiento.",
         "2026-08-07",
         "No sube a verificado_abierto y el motivo es de escala, no de fuerza: el acto fue en la "
         "Casa de la Cultura, no en el local. La distinción es indicio fuerte, no constatación "
         "presencial. Queda en probablemente_abierto SIN pendiente de chequeo."),
    ]
    for hito_id, estado, nivel, fuente, fecha, nota in almagro_bloque:
        fila = por_id(filas, hito_id)
        if fuente is None:
            p(f"  {hito_id} · {fila['nombre']:<26} ya resuelto en TAREA 7b → {estado} · {nivel}")
            continue
        set_campo(cambios, fila, "vigencia_verificada", estado,
                  "Bloque de Almagro, aplicado a la capa. El veredicto existía desde el 07/08 en "
                  "`desde_cowork/evidencia_2026/` y no se había aplicado: mientras no se aplicara, "
                  "«Almagro recupera los cinco» era cierto en el registro de la tanda y falso en "
                  "la capa.", "TAREA_7")
        set_campo(cambios, fila, "vigencia_nivel", nivel, "", "TAREA_7")
        set_campo(cambios, fila, "vigencia_fuente", fuente, "", "TAREA_7")
        set_campo(cambios, fila, "vigencia_fecha", fecha, "", "TAREA_7")
        set_campo(cambios, fila, "nota_ronda_7", nota, "", "TAREA_7")
        p(f"  {hito_id} · {fila['nombre']:<26} → {estado} · {nivel}")
    p("")

    # ============================== TAREA 7d · el resto del bloque que la ronda 6 dejó frenado
    p("-" * 100)
    p("  TAREA 7d · EL RESTO DEL BLOQUE QUE EL ENUM TENÍA FRENADO")
    p("")
    p("  La ronda 6 dejó once veredictos sin aplicar por tres bloqueos, y la tarea 7 resuelve los")
    p("  tres. Se aplican los que venían de los DOS registros que la ronda 6 nombró como")
    p("  bloqueados —`vigencia_cierre_del_dia.csv` y `vigencia_tanda_B_almagro_norte.csv`—.")
    p("")

    resto_bloqueado = [
        ("H056", "si", "v2", "verificación humana · Diego, 07/08/2026", "2026-08-07",
         "Bar DISTINTO de El Buzón (H046). Es una de las diez sedes que el GCBA nombra para el "
         "Festival y Mundial de Tango 2026. Su dirección queda por confirmar contra el anexo "
         "1225/26: la capa la tiene en Neuquén 1100 y el registro de la tanda la da «por "
         "confirmar»."),
        ("H007", "probablemente_abierto", "v4",
         "Aquí Mataderos 06/04/2026, sobre el proyecto de beneplácito por los 85 años del club",
         "2026-04-06",
         "RESERVA REGISTRADA: sin reporteo propio, el párrafo tiene la cadencia de la ficha del "
         "catálogo. El aniversario (fundación 03/02/1941) sí es real y verificable."),
        ("H001", "dudosa", "ninguno", "", "2025-10-16",
         "Sin ficha en Tripadvisor, verificado por búsqueda restringida a los tres dominios. "
         "Figura como sede de La Noche de los Bares Notables del 16/10/2025, pero quien lo nombra "
         "es un medio barrial y no el organizador: no computa como v5, y 295 días lo dejan fuera "
         "de ventana igual. ANTECEDENTE: cerró el 06/08/2019 y reabrió en 2021."),
    ]
    for hito_id, estado, nivel, fuente, fecha, nota in resto_bloqueado:
        fila = por_id(filas, hito_id)
        set_campo(cambios, fila, "vigencia_verificada", estado,
                  "Veredicto de los registros del 07/08 que la ronda 6 dejó frenado por el enum. "
                  "Con `probablemente_abierto` y `v3b` en el vocabulario, deja de estar frenado.",
                  "TAREA_7")
        set_campo(cambios, fila, "vigencia_nivel", nivel, "", "TAREA_7")
        if fuente:
            set_campo(cambios, fila, "vigencia_fuente", fuente, "", "TAREA_7")
        set_campo(cambios, fila, "vigencia_fecha", fecha, "", "TAREA_7")
        set_campo(cambios, fila, "nota_ronda_7", nota, "", "TAREA_7")
        if estado == "dudosa":
            set_campo(cambios, fila, "vigencia_sentido_duda",
                      "nada dentro de ventana y un antecedente de cierre y reapertura", "",
                      "TAREA_7")
        p(f"  {hito_id} · {fila['nombre']:<26} → {estado} · {nivel}")
    p("")
    p("  LO QUE NO SE APLICÓ, Y POR QUÉ. `vigencia_tanda_A_centro.csv` trae cinco veredictos más")
    p("  —Bar El Federal, Los 36 Billares, Café Tortoni, Café de los Angelitos y Varela")
    p("  Varelita— que NUNCA estuvieron bloqueados por el enum y que ninguna de las veinte")
    p("  decisiones nombra. Quedan sin aplicar y listados en `veredictos_no_aplicados_r7.csv`.")
    p("  Su efecto sobre la vía B se mide igual, más abajo, como sensibilidad.")
    p("")

    no_aplicados = [
        {"hito_id": "H009", "nombre": "Bar El Federal", "veredicto": "verificado_abierto",
         "nivel": "v3", "fecha_dato": "2026-07-21", "registro": "vigencia_tanda_A_centro.csv",
         "zona": "R03 San Telmo",
         "motivo_no_aplicado": "no estaba bloqueado por el enum y ninguna decisión lo nombra"},
        {"hito_id": "H074", "nombre": "Los 36 Billares", "veredicto": "verificado_abierto",
         "nivel": "v3", "fecha_dato": "2026-07-04", "registro": "vigencia_tanda_A_centro.csv",
         "zona": "Z47 Monserrat",
         "motivo_no_aplicado": "no estaba bloqueado por el enum y ninguna decisión lo nombra"},
        {"hito_id": "H035", "nombre": "Café Tortoni", "veredicto": "verificado_abierto",
         "nivel": "v3", "fecha_dato": "2026-05-26", "registro": "vigencia_tanda_A_centro.csv",
         "zona": "Z47 Monserrat",
         "motivo_no_aplicado": "no estaba bloqueado por el enum y ninguna decisión lo nombra"},
        {"hito_id": "H024", "nombre": "Café de los Angelitos", "veredicto": "verificado_abierto",
         "nivel": "v3", "fecha_dato": "2026-05-25", "registro": "vigencia_tanda_A_centro.csv",
         "zona": "Z36 → Z47 por la decisión 13",
         "motivo_no_aplicado": "no estaba bloqueado por el enum y ninguna decisión lo nombra"},
        {"hito_id": "H085", "nombre": "Varela Varelita", "veredicto": "verificado_abierto",
         "nivel": "v3", "fecha_dato": "2026-06-25", "registro": "vigencia_tanda_A_centro.csv",
         "zona": "R01 Palermo",
         "motivo_no_aplicado": "no estaba bloqueado por el enum y ninguna decisión lo nombra"},
    ]

    # ================================================= TAREA 6 · las de publicación
    p("-" * 100)
    p("  TAREA 6 · LAS DECISIONES DE PUBLICACIÓN")
    p("")

    # --- decisión 18 · registro_oficial
    for fila in filas:
        registros: list[str] = []
        tipo = fila.get("tipo", "")
        if tipo in REGISTRO_POR_TIPO:
            registros.append(REGISTRO_POR_TIPO[tipo])
        reconocimiento = fila.get("reconocimiento", "")
        if "Sitio de Interes Cultural" in reconocimiento or "Sitio de Interés Cultural" in reconocimiento:
            registros.append("sitio_interes_cultural")
        norma = fila.get("patrimonio_norma", "") or ""
        if "APH" in reconocimiento or "APH" in norma:
            registros.append("APH")
        if "Ley" in norma or "Ley CABA" in reconocimiento:
            registros.append("ley_especifica")
        valor = "; ".join(dict.fromkeys(registros))
        if valor:
            set_campo(cambios, fila, "registro_oficial", valor,
                      "DECISIÓN 18: campo de registro oficial para la ficha. Derivado de `tipo`, "
                      "`reconocimiento` y `patrimonio_norma`, que ya viajaban en la capa.",
                      "TAREA_6")

    # Miramar · el caso que la decisión 11 señaló: doble reconocimiento y la capa lo tenía en dos
    # filas distintas, una por registro. No se fusionan las filas —eso movería el conteo de la vía
    # B sin decirlo— pero las dos quedan marcadas con los dos registros y apuntadas entre sí.
    miramar_bn = por_id(filas, "H078")
    miramar_ico = por_id(filas, "ICO-012")
    for fila, par in ((miramar_bn, "ICO-012"), (miramar_ico, "H078")):
        set_campo(cambios, fila, "registro_oficial", "bar_notable; restaurante_iconico",
                  "DECISIÓN 11 + 18: Miramar tiene DOBLE reconocimiento oficial —Bar Notable del "
                  "anexo 1225/26 y Restaurante Icónico (16, 07/07/2026)— y la capa lo tenía a "
                  "medias: dos filas, una por registro, sin saber que eran el mismo local.",
                  "TAREA_6")
        set_campo(fila=fila, cambios=cambios, campo="nota_ronda_7",
                  valor=f"MISMO ESTABLECIMIENTO que {par}: Sarandí 1190 / Av. San Juan 1999 es la "
                        "misma ochava. Las dos filas se conservan porque fusionarlas movería el "
                        "conteo de la vía B sin que se vea; quedan apuntadas entre sí.",
                  motivo="", tarea="TAREA_6")

    # Bar Seddon · dos registros
    seddon = por_id(filas, "H015")
    set_campo(cambios, seddon, "registro_oficial", "bar_notable; sitio_interes_cultural",
              "DECISIÓN 18: Bar Notable del anexo + Sitio de Interés Cultural, norma 287/00.",
              "TAREA_6")

    con_registro = sum(1 for f in filas if f.get("registro_oficial"))
    p(f"  decisión 18 · `registro_oficial` cargado en {con_registro} de {len(filas)} hitos")
    for valor, n in sorted(pd.Series(
            [f["registro_oficial"] for f in filas if f.get("registro_oficial")]
    ).value_counts().items(), key=lambda kv: -kv[1]):
        p(f"      {valor:<44} {n:>4}")
    p("")

    # --- decisión 19 · Plaza Bar
    plaza = por_id(filas, "H082")
    estado_previo = plaza.get("vigencia_verificada", "")
    set_campo(cambios, plaza, "vigencia_verificada", "cerrado_con_reapertura_anunciada",
              "DECISIÓN 19: no es cierre definitivo. El bar histórico se conserva y se "
              "reinstalará: se excavan cinco subsuelos y se rescatan el grill y el bar.",
              "TAREA_6")
    set_campo(cambios, plaza, "vigencia_revisar_hasta", "2028",
              "DECISIÓN 19: reapertura anunciada para 2028.", "TAREA_6")
    set_campo(cambios, plaza, "nota_ronda_7",
              "Reapertura anunciada para 2028. Con la decisión 5 pasa a contar dentro de Z46 "
              "Retiro, que queda con cuatro Bares Notables en seis cuadras y uno de ellos cerrado "
              "desde 2017.", "", "TAREA_6")
    p(f"  decisión 19 · Plaza Bar (H082) · estado previo `{estado_previo}` → "
      "cerrado_con_reapertura_anunciada, revisar_hasta 2028")
    if estado_previo == "cerrado_con_reapertura_anunciada":
        p("      el estado ya era ése desde una ronda anterior; la decisión lo confirma y agrega")
        p("      el año. No es un cambio de veredicto.")
    p("")

    # --- decisión 20 · doble numeración
    p("  decisión 20 · doble numeración: se publica la del anexo, se registra la variante")
    for hito_id, (publicada, variante, detalle) in DOBLE_NUMERACION.items():
        fila = por_id(filas, hito_id)
        actual = fila.get("direccion", "")
        set_campo(cambios, fila, "direccion_variante", variante,
                  f"DECISIÓN 20: {detalle}. Se publica la altura del anexo y la variante queda "
                  "registrada, no descartada: es la que usan Tripadvisor y parte de la prensa, y "
                  "sin ella un cruce por dirección falla.", "TAREA_6")
        coincide = "=" if actual.strip() == publicada else "≠"
        p(f"      {hito_id} · {fila['nombre']:<20} capa «{actual}» {coincide} anexo "
          f"«{publicada}» · variante {variante}")
        if coincide == "≠":
            set_campo(cambios, fila, "direccion", publicada,
                      "DECISIÓN 20: la dirección publicada es la del anexo.", "TAREA_6")
    p("")

    # ================================================= TAREA 5 · Monserrat
    p("-" * 100)
    p("  TAREA 5 · MONSERRAT")
    p("")

    capa_barrios = barrios()
    monserrat_poly = capa_barrios[capa_barrios.clave == "MONSERRAT"].geometry.iloc[0]
    callejero = gpd.read_file(CALLEJERO).to_crs(CRS_METRICO)
    callejero["clave"] = callejero.nomoficial.map(sin_tildes)

    # --- 5a · ¿los cinco «no estaban en la capa»?
    nuevos = pd.read_csv(COWORK / "hitos_nuevos_monserrat.csv")
    p("  5a · LO PRIMERO, PORQUE CONTRADICE AL INSUMO")
    p("")
    p("  `hitos_nuevos_monserrat.csv` marca diez establecimientos y dice de nueve de ellos que NO")
    p("  estaban en nuestra base. Se comprobó uno por uno contra la capa antes de dar de alta:")
    p("")
    por_nombre = {sin_tildes(f["nombre"]): f for f in filas}
    alias = {
        "BAR EL COLONIAL": "EL COLONIAL",
        "CABILDO DE BUENOS AIRES": "CABILDO DE BUENOS AIRES",
        "BAR SEDDON": "BAR SEDDON",
        "EL QUERANDI": "EL QUERANDI",
        "LONDON CITY": "LONDON CITY",
        "MIRAMAR": "MIRAMAR",
    }
    monserrat_filas = []
    for reg in nuevos.itertuples():
        clave = sin_tildes(reg.establecimiento)
        clave = sin_tildes(alias.get(clave, clave))
        encontrado = por_nombre.get(clave)
        estado = "YA ESTABA EN LA CAPA" if encontrado else "alta nueva"
        monserrat_filas.append({
            "establecimiento": reg.establecimiento, "direccion": reg.direccion,
            "dice_el_insumo": reg.estaba_en_nuestra_base, "lo_que_dice_la_capa": estado,
            "hito_id": encontrado["hito_id"] if encontrado else "",
            "registro": reg.registro,
        })
        marca = "✗" if (str(reg.estaba_en_nuestra_base).strip().upper() == "NO"
                        and encontrado) else " "
        p(f"   {marca} {reg.establecimiento:<34} insumo: {str(reg.estaba_en_nuestra_base):<8} "
          f"capa: {estado}"
          + (f" ({encontrado['hito_id']})" if encontrado else ""))
    ya_estaban = sum(1 for f in monserrat_filas
                     if f["lo_que_dice_la_capa"] == "YA ESTABA EN LA CAPA"
                     and str(f["dice_el_insumo"]).strip().upper() == "NO")
    p("")
    p(f"  {ya_estaban} de los diez que el insumo da por ausentes YA ESTABAN en la capa, con punto")
    p("  y con dirección. Entraron con el canon del Boletín y con la Res. 1225/26 de la ronda 5.")
    p("  No se dan de alta: duplicarlos habría inflado exactamente la vía B que esta ronda está")
    p("  tratando de medir bien.")
    p("")

    # --- 5b · las altas que sí lo son
    p("  5b · LAS ALTAS QUE SÍ SON ALTAS")
    p("")
    altas = [
        ("DIR-026", "Gran Café Gardel", "Café histórico sin registro oficial",
         "ochava Av. Entre Ríos e Independencia", "Monserrat", "",
         "si", "v1", "Infobae 05/01/2025, con reporteo",
         "1935, 91 años. NO figura en el anexo 1225/26 ni entre los 16 Restaurantes Icónicos: "
         "es trayectoria sin registro oficial, y por eso NO computa para la vía B con la regla "
         "vigente. Se carga igual porque es el tipo de hito que la ficha de la zona necesita "
         "nombrar. Barrio disputado con San Cristóbal."),
        ("DIR-027", "Centro Asturiano de Buenos Aires", "Casa regional con comedor",
         "Solis 475", "Monserrat", "",
         "dudosa", "ninguno", "sitio oficial: la sede social cuenta con restaurante",
         "ABRE LA VÍA D, no la B: es oferta de colectividad verificable, no registro oficial "
         "gastronómico. Sede lunes a viernes 10-18; el horario del restaurante no se pudo "
         "confirmar, y por eso dudosa."),
        ("DIR-028", "Centro Laurak Bat (Restaurante Haritz)", "Casa regional con comedor",
         "Av. Belgrano 1144", "Monserrat", "",
         "sin_verificar", "", "",
         "HALLAZGO NUEVO. Opera el Restaurante Haritz. ABRE LA VÍA D con oferta verificable, no "
         "con relato: es un restaurante con nombre propio dentro de la casa vasca, no una "
         "referencia a la colectividad."),
        ("DIR-029", "Casal de Catalunya", "Casa regional con comedor",
         "Chacabuco 863", "San Telmo", "",
         "sin_verificar", "", "",
         "Fuera del perímetro propuesto de Monserrat pero contiguo. Se registra para que la vía D "
         "de la zona pueda decidirse con el conjunto a la vista, no para computarlo adentro."),
    ]
    for hito_id, nombre, tipo, direccion, barrio_decl, registro, estado, nivel, fuente, nota in altas:
        if sin_tildes(nombre) in por_nombre:
            p(f"      {nombre}: ya estaba — no se da de alta")
            continue
        if hito_id in OCHAVAS:
            calle_a, calle_b = OCHAVAS[hito_id]
            punto = punto_de_ochava(callejero, calle_a, calle_b)
            if punto is None:
                lat, lon = None, None
            else:
                geografico = gpd.GeoSeries([punto], crs=CRS_METRICO).to_crs(CRS_GEOGRAFICO).iloc[0]
                lat, lon = geografico.y, geografico.x
        else:
            lat, lon = normalizar(direccion, cache_norm)
        nueva = {campo: "" for campo in campos}
        nueva.update({
            "hito_id": hito_id, "nombre": nombre, "tipo": tipo,
            "reconocimiento": "trayectoria documentada sin registro oficial"
                              if "Café" in tipo else "casa regional con comedor en funciones",
            "direccion": direccion, "barrio_declarado": barrio_decl,
            "latitud": f"{lat:.6f}" if lat else "", "longitud": f"{lon:.6f}" if lon else "",
            "origen": "evidencia_2026 · alta ronda 7",
            "fuente_primaria": "hitos_nuevos_monserrat.csv",
            "edicion_o_anio": "2026", "confianza": "media",
            "metodo_geocodificacion": (
                "cruce de ejes del callejero oficial (la fuente da ochava sin altura)"
                if hito_id in OCHAVAS and lat else
                "USIG normalizador sobre la dirección" if lat else
                "SIN PUNTO: la dirección no se resolvió"),
            "es_patrimonio_normativo": "False",
            "vigencia_verificada": estado, "vigencia_nivel": nivel, "vigencia_fuente": fuente,
            "vigencia_fecha": "2025-01-05" if hito_id == "DIR-026" else "",
            "es_alta_2026_08_03": "False",
            "registro_oficial": registro, "nota_ronda_7": nota,
        })
        filas.append(nueva)
        cambios.append({"hito_id": hito_id, "nombre": nombre, "campo": "(alta)",
                        "valor_antes": "", "valor_despues": "alta a la capa",
                        "motivo": nota, "tarea": "TAREA_5", "fecha": FECHA})
        punto = f"{lat:.6f}, {lon:.6f}" if lat else "SIN PUNTO"
        p(f"      {hito_id} · {nombre:<38} {punto}")
    p("")
    p("  El Globo (H. Yrigoyen 1199) y Plaza Asturias (Av. de Mayo 1199) NO se dan de alta como")
    p("  hitos: no tienen ningún registro oficial —El Globo está explícitamente fuera del anexo y")
    p("  de los 16 Icónicos—. Entran a la medición del núcleo de Salta, que es otra cosa.")
    p("")

    # --- 5c · los nueve notables del barrio, contados
    p("  5c · «NUEVE DE LOS NOVENTA BARES NOTABLES», CONTADO CONTRA EL POLÍGONO")
    p("")
    con_punto = [f for f in filas if f.get("latitud") and f.get("longitud")]
    geo = gpd.GeoDataFrame(
        pd.DataFrame(con_punto),
        geometry=[Point(float(f["longitud"]), float(f["latitud"])) for f in con_punto],
        crs=CRS_GEOGRAFICO).to_crs(CRS_METRICO)
    notables = geo[geo.tipo == "Bar Notable"]
    dentro = notables[notables.within(monserrat_poly)]
    p(f"  Bares Notables con punto en la capa: {len(notables)}")
    p(f"  dentro del polígono administrativo de Monserrat: {len(dentro)}")
    p("")
    for fila in dentro.sort_values("nombre").itertuples():
        p(f"      {fila.hito_id:<9} {fila.nombre:<30} {str(fila.direccion):<32} "
          f"{fila.vigencia_verificada}")
    p("")
    if len(dentro) != 9:
        p(f"  EL INSUMO DICE NUEVE Y EL POLÍGONO DA {len(dentro)}. Se reporta la diferencia sin")
        p("  ajustar ninguno de los dos: los que faltan o sobran están en el CSV de la tarea.")
    p("")

    # --- 5d · Bar Seddon
    p("  5d · LA DISCREPANCIA DE BARRIO DE BAR SEDDON, RESUELTA CON USIG")
    p("")
    seddon_lat, seddon_lon = float(seddon["latitud"]), float(seddon["longitud"])
    respuesta = datos_utiles(seddon_lon, seddon_lat, cache_du)
    barrio_usig = barrio_de(respuesta)
    p(f"      el catálogo lo asigna a Monserrat · la CPPHC a San Telmo")
    p(f"      USIG /datos_utiles sobre el punto ({seddon_lat:.6f}, {seddon_lon:.6f}): "
      f"{barrio_usig or 'sin respuesta'}")
    punto_seddon = gpd.GeoSeries([Point(seddon_lon, seddon_lat)], crs=CRS_GEOGRAFICO).to_crs(
        CRS_METRICO).iloc[0]
    for nombre_barrio in ("MONSERRAT", "SAN TELMO"):
        poly = capa_barrios[capa_barrios.clave == nombre_barrio].geometry.iloc[0]
        adentro = punto_seddon.within(poly)
        distancia = punto_seddon.distance(poly)
        p(f"      polígono GCBA de {nombre_barrio.title():<11} dentro={'sí' if adentro else 'no'} "
          f"· distancia={distancia:,.0f} m")
    if barrio_usig:
        set_campo(cambios, seddon, "barrio_declarado", barrio_usig,
                  f"DISCREPANCIA RESUELTA POR PUNTO: el catálogo lo asigna a Monserrat y la CPPHC "
                  f"a San Telmo. USIG /datos_utiles sobre el punto responde {barrio_usig}. Es el "
                  "mismo procedimiento con el que la ronda 6 resolvió Café Olimpo, y la cuarta "
                  "vez que el campo territorial de un catálogo no se sostiene contra el punto.",
                  "TAREA_5")
        set_campo(cambios, seddon, "conflicto_direccion",
                  "barrio en disputa entre el catálogo (Monserrat) y la CPPHC (San Telmo); "
                  f"resuelto por punto: {barrio_usig}", "", "TAREA_5")
    p("")

    # --- 5e · el núcleo de Salta
    p("  5e · EL NÚCLEO DE SALTA, MEDIDO")
    p("")
    puntos_nucleo = []
    for nombre, direccion, registro in NUCLEO_SALTA:
        lat, lon = normalizar(direccion, cache_norm)
        puntos_nucleo.append({"establecimiento": nombre, "direccion": direccion,
                              "registro_oficial": registro, "latitud": lat, "longitud": lon})
    nucleo = gpd.GeoDataFrame(
        pd.DataFrame(puntos_nucleo),
        geometry=[Point(r["longitud"], r["latitud"]) for r in puntos_nucleo],
        crs=CRS_GEOGRAFICO).to_crs(CRS_METRICO)
    p(f"  {'':<16} " + " ".join(f"{r.establecimiento[:13]:>14}" for r in nucleo.itertuples()))
    distancias = []
    for a in nucleo.itertuples():
        celdas = []
        for b in nucleo.itertuples():
            d = a.geometry.distance(b.geometry)
            celdas.append(f"{d:>14,.1f}")
            if a.Index < b.Index:
                distancias.append({"a": a.establecimiento, "b": b.establecimiento,
                                   "distancia_m": round(d, 1)})
        p(f"  {a.establecimiento[:15]:<16} " + " ".join(celdas))
    p("")
    maxima = max(distancias, key=lambda d: d["distancia_m"])
    minima = min(distancias, key=lambda d: d["distancia_m"])
    envolvente = unary_union(list(nucleo.geometry)).convex_hull
    p(f"  la distancia máxima entre dos de los cuatro: {maxima['distancia_m']:,.1f} m "
      f"({maxima['a']} ↔ {maxima['b']})")
    p(f"  la mínima: {minima['distancia_m']:,.1f} m ({minima['a']} ↔ {minima['b']})")
    p(f"  los cuatro caben en una envolvente convexa de {envolvente.area / 10_000:.3f} ha")
    p("")

    # --- 5f · San Cristóbal
    p("  5f · SAN CRISTÓBAL · EL CONTEO QUE PIDE LA DECISIÓN 11")
    p("")
    callejero = gpd.read_file(CALLEJERO).to_crs(CRS_METRICO)
    callejero["clave"] = callejero.nomoficial.map(sin_tildes)
    base = puntos_base()
    sancris_filas = []
    ejes_sancris = []
    for calle, desde, hasta in SAN_CRISTOBAL_TRAMOS:
        eje, n_seg = tramo_por_altura(callejero, calle, desde, hasta)
        if eje is None:
            p(f"      {calle} {desde}-{hasta}: el callejero no devuelve tramo — se declara")
            continue
        ejes_sancris.append(eje)
        area = eje.buffer(BUFFER_CONTEO_M)
        adentro = base[base.within(area)]
        largo = eje.length
        sancris_filas.append({
            "tramo": f"{calle} {desde}-{hasta}", "segmentos": n_seg,
            "largo_eje_m": round(largo, 1), "buffer_m": BUFFER_CONTEO_M,
            "ha": round(area.area / 10_000, 2), "locales": len(adentro),
            "locales_x_ha": round(len(adentro) / (area.area / 10_000), 3),
            "locales_x_100m_de_eje": round(len(adentro) / (largo / 100), 2),
        })
        p(f"      {calle} {desde}-{hasta:<6} {n_seg:>3} segmentos · {largo:>7,.0f} m de eje · "
          f"{len(adentro):>4} locales · {len(adentro) / (largo / 100):>5.1f} por 100 m")
    if ejes_sancris:
        conjunto = unary_union(ejes_sancris).buffer(BUFFER_CONTEO_M)
        total = base[base.within(conjunto)]
        sancris_filas.append({
            "tramo": "LOS DOS TRAMOS (unión, sin doble conteo)", "segmentos": "",
            "largo_eje_m": "", "buffer_m": BUFFER_CONTEO_M,
            "ha": round(conjunto.area / 10_000, 2), "locales": len(total),
            "locales_x_ha": round(len(total) / (conjunto.area / 10_000), 3),
            "locales_x_100m_de_eje": "",
        })
        p("")
        p(f"      los dos juntos: {len(total)} locales en {conjunto.area / 10_000:,.1f} ha "
          f"= {len(total) / (conjunto.area / 10_000):.2f} locales por hectárea")
        p("")
        p("  PARA COMPARAR, Y PARA QUE EL NÚMERO NO SE LEA SOLO: la vía A se abre a 2 locales por")
        p("  hectárea en la grilla vigente. Este conteo es sobre eje con media cuadra a cada lado,")
        p("  que es un recorte más ajustado que un polígono de polo, así que la densidad sale más")
        p("  alta por construcción. NO es un veredicto de vía A: es el insumo que la decisión 11")
        p("  pidió antes de decidir.")
    p("")

    # ================================================= validación de enums
    p("-" * 100)
    p("  VALIDACIÓN DE LA CAPA DE SALIDA")
    p("")
    malos_estado = sorted({f.get("vigencia_verificada", "") for f in filas} - VIGENCIA_ESTADOS
                          - {""})
    malos_nivel = sorted({(f.get("vigencia_nivel") or "") for f in filas} - VIGENCIA_NIVELES)
    malos_registro = set()
    for fila in filas:
        for valor in (fila.get("registro_oficial") or "").split(";"):
            if valor.strip() and valor.strip() not in REGISTROS_VALIDOS:
                malos_registro.add(valor.strip())
    if malos_estado or malos_nivel or malos_registro:
        p(f"  ✗ valores fuera de enum · estado={malos_estado} nivel={malos_nivel} "
          f"registro={sorted(malos_registro)}")
        raise SystemExit(f"enum roto: {malos_estado} {malos_nivel} {sorted(malos_registro)}")
    p("  ✓ los tres enums cierran: vigencia_verificada, vigencia_nivel y registro_oficial")
    p("")
    conteo = pd.Series([f["vigencia_verificada"] for f in filas]).value_counts()
    for valor, n in conteo.items():
        p(f"      {valor:<36} {n:>4}")
    p("")

    # ================================================= salidas
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(filas)
    pd.DataFrame(cambios).to_csv(CAMBIOS_CSV, index=False, encoding="utf-8")
    pd.DataFrame(monserrat_filas).to_csv(MONSERRAT_CSV, index=False, encoding="utf-8")
    pd.DataFrame(distancias).to_csv(NUCLEO_CSV, index=False, encoding="utf-8")
    pd.DataFrame(sancris_filas).to_csv(SANCRIS_CSV, index=False, encoding="utf-8")
    pd.DataFrame(no_aplicados).to_csv(PENDIENTES_CSV, index=False, encoding="utf-8")
    CACHE_USIG.write_text(json.dumps(cache_norm, ensure_ascii=False), encoding="utf-8")
    CACHE_DATOS_UTILES.write_text(json.dumps(cache_du, ensure_ascii=False), encoding="utf-8")

    p("-" * 100)
    p(f"  capa de salida: {OUT_CSV.name} · {len(filas)} hitos · {len(campos)} columnas")
    p(f"  cambios: {len(cambios)}")
    p("  Google Places: 0 requests.")

    texto = buffer.getvalue()
    INFORME_TXT.write_text(texto, encoding="utf-8")
    print(texto)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
