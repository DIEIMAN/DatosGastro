"""La compuerta de identidad de Places. Ningún request sale de acá sin pasar por esto.

QUÉ PASÓ, Y POR QUÉ ESTO EXISTE
--------------------------------
La ronda 9 preguntó por «La Perla del Once» en Av. Rivadavia 2800 y Places devolvió
`OPERATIONAL` para **«La Americana, La Reina de las Empanadas»** — el comercio que ocupa hoy el
local. La respuesta era correcta sobre La Americana y la íbamos a leer como si hablara del bar.

**La ronda 8 se da por perdida entera.** Sus 71 resultados no tienen referente conocido: la
máscara no traía `displayName`, así que no se sabe de qué establecimiento habla ninguno —incluido
el único `CLOSED_PERMANENTLY`—.

LAS CUATRO CONDICIONES, Y NINGUNA ES OPCIONAL
-----------------------------------------------
    (a) `displayName` y `formattedAddress` **obligatorios** en la máscara. `CAMPOS_MINIMOS` los
        incluye y `validar_mascara()` corta si faltan.
    (b) La compuerta **RECHAZA** la respuesta si nombre y dirección no coinciden con lo
        preguntado. No la marca: la rechaza. Un resultado rechazado no produce veredicto.
    (c) **Nada de `maxResultCount: 1`.** La misma consulta, a dos minutos, devolvió otro lugar;
        con uno solo se toma el primero de una lista rankeada inestable y la respuesta no es
        reproducible. Se piden varios y se desambigua **entre los candidatos**.
    (d) **Dos campos de la misma respuesta que se contradicen anulan la respuesta entera.**
        «EX Hotel Castelar.» con `OPERATIONAL` no se resuelve eligiendo el campo que uno fue a
        buscar: se descarta.

EL CONTROL DE DIRECCIÓN ES EL DE LA RONDA 8, QUE FUNCIONÓ
-----------------------------------------------------------
De 71 respuestas dejó **una sola falla real** —Crizia, consultada en Gorriti y devuelta en Fitz
Roy— y convirtió otras diez alarmas en coincidencias buenas al distinguir «otra cuadra» de «otra
calle». Se reusa tal cual y se le agrega la regla de esquina: dos direcciones sobre calles que se
cruzan, a menos de `ESQUINA_M`, son la misma puerta. Es el caso de La Perla del Once, que el
catálogo del Festival ya había contado dos veces por no tenerla.

USO
---
  from places_compuerta_identidad import CAMPOS_MINIMOS, compuerta, validar_mascara
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ronda_8_places_incremental import altura_de, calle_de, identidad, sin_tildes  # noqa: E402

# (a) Los dos que la compuerta necesita para existir, más el que fijó la decisión 4.
CAMPOS_MINIMOS = [
    "places.displayName",       # sin esto no se sabe de quién habla la respuesta
    "places.formattedAddress",  # sin esto no se puede auditar contra la dirección preguntada
    "places.businessStatus",
]
CAMPOS_OBLIGATORIOS = {"places.displayName", "places.formattedAddress"}

# (c) Cuántos candidatos se piden. Uno solo no es reproducible.
CANDIDATOS = 5

# Dos puertas sobre calles distintas a menos de esto son la misma esquina.
ESQUINA_M = 120.0

# (d) Pares de valores que no pueden convivir en una misma respuesta.
CONTRADICCIONES = [
    (r"\bEX[\s.\-]", "OPERATIONAL",
     "el nombre declara que el establecimiento es el ex y el estado dice que opera"),
    (r"\b(CERRADO|CLAUSURAD)", "OPERATIONAL",
     "el nombre declara cierre y el estado dice que opera"),
]

# Cuánto tiene que parecerse el nombre devuelto al preguntado. Es laxo a propósito: «Los Galgos
# (Callao 501)» contra «Los Galgos» tiene que pasar, y «La Perla del Once» contra «La Americana»
# tiene que fallar.
UMBRAL_NOMBRE = 0.34


def _tokens(texto: str) -> set[str]:
    ruido = {"BAR", "CAFE", "EL", "LA", "LOS", "LAS", "DE", "DEL", "Y", "RESTAURANTE",
             "CONFITERIA", "PIZZERIA", "SA", "SRL"}
    return {t for t in sin_tildes(re.sub(r"\([^)]*\)", " ", str(texto))).split()
            if len(t) > 2 and t not in ruido}


def parecido_de_nombre(preguntado: str, devuelto: str) -> float:
    """Jaccard sobre tokens significativos. 0 = nada en común, 1 = los mismos."""
    a, b = _tokens(preguntado), _tokens(devuelto)
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def contradiccion(nombre: str, estado: str) -> str | None:
    """(d) Si dos campos de la misma respuesta se contradicen, no hay dato."""
    for patron, estado_malo, motivo in CONTRADICCIONES:
        if estado == estado_malo and re.search(patron, sin_tildes(nombre)):
            return motivo
    return None


def validar_mascara(campos: list[str]) -> None:
    """(a) Corta antes del primer request si la máscara no puede sostener la compuerta."""
    faltan = CAMPOS_OBLIGATORIOS - set(campos)
    if faltan:
        raise ValueError(
            f"máscara sin {sorted(faltan)}: la compuerta de identidad no puede funcionar y el "
            f"resultado no tendría referente conocido. Es lo que invalidó la ronda 8.")


def es_la_misma_esquina(dir_a: str, dir_b: str, callejero=None, mapa=None) -> bool:
    """Dos direcciones sobre calles que se cruzan y a menos de ESQUINA_M son la misma puerta."""
    if callejero is None:
        return False
    from callejero_canonico import eje_canonico  # noqa: PLC0415

    def punto(direccion):
        calles = calle_de(direccion)
        altura = altura_de(direccion)
        if not calles or not altura:
            return None
        for nombre in calles:
            candidatos = callejero[callejero.raiz.str.contains(nombre, na=False, regex=False)]
            for _, fila in candidatos.iterrows():
                for ini, fin in ((fila.alt_izqini, fila.alt_izqfin),
                                 (fila.alt_derini, fila.alt_derfin)):
                    try:
                        if ini is not None and fin is not None and \
                                min(ini, fin) <= int(altura) <= max(ini, fin):
                            return fila.geometry.interpolate(0.5, normalized=True)
                    except (TypeError, ValueError):
                        continue
        return None

    pa, pb = punto(dir_a), punto(dir_b)
    if pa is None or pb is None:
        return False
    return pa.distance(pb) <= ESQUINA_M


def compuerta(preguntado_nombre: str, preguntado_dir: str, candidatos: list[dict],
              callejero=None) -> dict:
    """Elige entre los candidatos el que ES el establecimiento preguntado, o RECHAZA.

    Devuelve un dict con `veredicto` ∈ {`aceptado`, `RECHAZADO`} y el motivo. Un `RECHAZADO`
    **no produce dato de vigencia**: no es un `OPERATIONAL` débil, es la ausencia de respuesta.
    """
    if not candidatos:
        return {"veredicto": "RECHAZADO", "motivo": "sin resultados",
                "business_status": "", "nombre_devuelto": "", "n_candidatos": 0}

    evaluados = []
    for cand in candidatos:
        nombre = (cand.get("displayName") or {}).get("text", "")
        direccion = cand.get("formattedAddress", "")
        estado = cand.get("businessStatus", "SIN_ESTADO")
        choque = contradiccion(nombre, estado)
        ver_dir, detalle_dir = identidad(preguntado_dir, direccion)
        parecido = parecido_de_nombre(preguntado_nombre, nombre)
        dir_ok = ver_dir in ("exacta", "misma cuadra") or (
            ver_dir == "OTRA CALLE" and es_la_misma_esquina(preguntado_dir, direccion, callejero))
        evaluados.append({
            "nombre_devuelto": nombre, "business_status": estado,
            "parecido_de_nombre": round(parecido, 3), "control_direccion": ver_dir,
            "control_detalle": detalle_dir, "direccion_ok": dir_ok,
            "contradiccion": choque or "",
        })

    # (d) primero: una contradicción anula ese candidato entero, gane o pierda el resto.
    limpios = [e for e in evaluados if not e["contradiccion"]]
    if not limpios:
        peor = evaluados[0]
        return {**peor, "veredicto": "RECHAZADO", "n_candidatos": len(candidatos),
                "motivo": f"contradicción interna · {peor['contradiccion']}",
                "business_status": ""}

    # (b) el candidato tiene que coincidir en NOMBRE y en DIRECCIÓN. Las dos.
    validos = [e for e in limpios
               if e["direccion_ok"] and e["parecido_de_nombre"] >= UMBRAL_NOMBRE]
    if not validos:
        mejor = max(limpios, key=lambda e: e["parecido_de_nombre"])
        motivo = ("ningún candidato coincide en nombre Y dirección · el mejor fue "
                  f"«{mejor['nombre_devuelto']}» (parecido {mejor['parecido_de_nombre']}, "
                  f"dirección {mejor['control_direccion']})")
        return {**mejor, "veredicto": "RECHAZADO", "motivo": motivo,
                "n_candidatos": len(candidatos), "business_status": ""}

    elegido = max(validos, key=lambda e: e["parecido_de_nombre"])
    otros = [e for e in validos if e is not elegido]
    ambiguo = [e for e in otros
               if abs(e["parecido_de_nombre"] - elegido["parecido_de_nombre"]) < 0.05
               and e["business_status"] != elegido["business_status"]]
    if ambiguo:
        return {**elegido, "veredicto": "RECHAZADO", "n_candidatos": len(candidatos),
                "motivo": "dos candidatos igual de buenos con estados distintos: la respuesta no "
                          "es reproducible",
                "business_status": ""}
    return {**elegido, "veredicto": "aceptado", "n_candidatos": len(candidatos),
            "motivo": f"coincide en nombre ({elegido['parecido_de_nombre']}) y dirección "
                      f"({elegido['control_direccion']})"}
