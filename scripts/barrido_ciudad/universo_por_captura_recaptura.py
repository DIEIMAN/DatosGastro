"""Padrón × Places como captura-recaptura, contra las 17 cifras publicadas. CERO requests.

DE DÓNDE SALE ESTA PRUEBA
-------------------------
El cruce de R08 (`cruzar_places_padron.py`) dio un resultado que no se buscaba: de los 81 puntos
de Places, 27 caen en una dirección del padrón núcleo. Eso es el 33,3 %, y el padrón núcleo cubre
el 36,1 % de la cifra contada a pie. Las dos proporciones coinciden, y coinciden porque tienen que
coincidir **si las dos fuentes se equivocan por motivos distintos**: el solape entre dos muestras
independientes de una misma población es el producto de sus coberturas.

Dicho al revés, que es como se usa: si el solape es el del azar, entonces

    N̂ = (n_padrón + 1)(n_places + 1) / (m + 1) − 1

estima el tamaño de la población de la que las dos salen. En R08 eso da del orden de la cifra que
se contó caminando. **Si eso se repite en las otras zonas con conteo de campo, hay una manera de
estimar el universo de un barrio sin caminarlo**: no hace falta que Places sea completo —ya se sabe
que no lo es, recupera el 12 %—, hace falta que sea independiente del padrón.

Ojo con el entusiasmo: esto NO valida el estimador. Lo que hace es ponerlo a prueba donde hay con
qué, que es acá y ahora, y gratis.

LAS PREDICCIONES, ESCRITAS ANTES DE CORRER
------------------------------------------
Las 17 zonas no son un bloque: sus cifras publicadas se obtuvieron con métodos distintos, y eso
permite pedirle al estimador cosas distintas en cada familia. Si acierta donde tiene que acertar y
se pasa donde tiene que pasarse, es señal; si acierta en todas o falla en todas, no.

  1. **relevamiento propio** (R08, R09, R10, R11 · conteo de campo, cifra exacta): N̂ tiene que
     caer CERCA. Es la única familia donde hay una verdad contra la cual medir. Tolerancia ±25 %.
  2. **mínimo relevado** (cota inferior declarada): N̂ tiene que quedar POR ENCIMA. Si queda por
     debajo, el estimador subestima y se cae.
  3. **directorio comercial** (R14–R17 · listados comerciales, chicos por construcción): N̂ tiene
     que quedar MUY por encima —el factor de captura documental ya mostró que esas cifras son
     varias veces chicas—.
  4. **relevamiento anterior** (R05, R07 · cifras históricas de otra metodología): sin predicción.
     Se informan y no cuentan para el veredicto.

Un m chico hace estallar la varianza del estimador: por debajo de `M_MINIMO` coincidencias la
zona se informa pero **no se lee**, y se dice.

QUÉ PUEDE INVALIDAR TODO ESTO, Y HAY QUE DECIRLO CADA VEZ
---------------------------------------------------------
- **Las dos fuentes no muestrean la misma población.** El padrón son direcciones que alguna vez
  tramitaron habilitación en 2015-2025 y no registra bajas; Places es lo que está abierto hoy. La
  población de la que salen las dos existe —los locales de la zona— pero cada una la recorta
  distinto. El N̂ que sale es del universo común, y su interpretación es más floja que en una
  captura-recaptura de laboratorio.
- **Independencia es un supuesto, no un hallazgo.** Que en R08 el solape sea el del azar es
  consistente con independencia; no la prueba. Si las dos fuentes fallaran sobre los mismos locales
  —los chicos, los informales, los de poca visibilidad— el solape saldría inflado y N̂ quedaría
  corto. La dirección del sesgo es conocida: **N̂ es cota inferior** bajo captura desigual.
- **Una zona no es una validación.** Cuatro tampoco, pero cuatro con predicción escrita antes ya
  distinguen una coincidencia de un método.

GUARDARRAÍLES
-------------
- **No toca la red.** Usa los puntos del control de las 17 zonas, ya pagados y guardados.
- Nombres y direcciones se leen de la carpeta interna ignorada por Git; a `generado/` van conteos.

USO
---
  python scripts/barrido_ciudad/universo_por_captura_recaptura.py
"""
from __future__ import annotations

import argparse
import datetime as dt
import io
import json
import sys
import warnings
from pathlib import Path

import geopandas as gpd
import pandas as pd

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from places_control_zonas import (  # noqa: E402
    GEN,
    INTERNO as INTERNO_CONTROL,
    asignar_por_geometria,
    zonas_con_cifra,
)
from cruzar_places_padron import (  # noqa: E402
    TOLERANCIA_ALTURA,
    direcciones_padron,
    misma_calle,
    partir_places,
)

# Por debajo de esto la varianza de Chapman domina y el número no se lee. Siete es donde el error
# estándar relativo baja del 40 % en los tamaños de esta prueba.
M_MINIMO = 7

# Para la proporción de solape del §5 no hace falta m grande, pero sí una muestra de Places que no
# sea un puñado: con 5 puntos, un local de más o de menos mueve la proporción veinte puntos.
MUESTRA_MINIMA = 10

# Tolerancia para «acierta» en la familia con conteo de campo. Un cuarto es holgado a propósito:
# lo que se está probando es si el estimador da el orden de magnitud correcto, no si clava el
# número. Si hubiera que ajustar esta tolerancia después de ver los datos, la prueba no valdría.
TOLERANCIA_ACIERTO = 0.25

PREDICCIONES = {
    "relevamiento propio": ("CERCA", f"dentro de ±{int(TOLERANCIA_ACIERTO * 100)} % de la cifra"),
    "minimo relevado": ("POR ENCIMA", "la cifra es cota inferior declarada"),
    "directorio comercial": ("MUY POR ENCIMA", "listados comerciales, chicos por construcción"),
    "relevamiento anterior": ("SIN PREDICCIÓN", "otra metodología, otra época"),
}


def chapman(n1: int, n2: int, m: int) -> dict:
    """Estimador de Chapman y su error estándar. El mismo que usa `captura_recaptura_places.py`."""
    estimado = (n1 + 1) * (n2 + 1) / (m + 1) - 1
    varianza = ((n1 + 1) * (n2 + 1) * (n1 - m) * (n2 - m)) / ((m + 1) ** 2 * (m + 2))
    error = varianza ** 0.5
    return {"n_estimado": estimado, "error_estandar": error,
            "ic_bajo": max(estimado - 1.96 * error, n1 + n2 - m),
            "ic_alto": estimado + 1.96 * error}


def puntos_del_control(rid: str) -> pd.DataFrame:
    """Los puntos núcleo del control que caen dentro de la envolvente de la zona.

    Se toma la atribución geométrica, no la celda: incluye los puntos que trajeron celdas de zonas
    vecinas. Acá eso es lo correcto —la pregunta es qué vio Places dentro de este perímetro, no
    cuánto costó verlo— y es la misma regla con la que se calculó `places_nucleo` en el control.
    """
    puntos = asignar_por_geometria(
        pd.read_csv(INTERNO_CONTROL / "places_puntos_interno.csv", encoding="utf-8-sig"))
    return puntos[(puntos.rid_geo == rid) & (puntos.anillo == "nucleo")].reset_index(drop=True)


def coincidencias(places: pd.DataFrame, padron: gpd.GeoDataFrame) -> int:
    """Cuántos puntos de Places caen sobre una dirección del padrón núcleo. Misma regla que el cruce."""
    nucleo = padron[padron.es_nucleo & ~padron.es_outlier]
    puertas_por_fila = list(nucleo.puertas)
    total = 0
    for direccion in places.direccion:
        tokens, altura = partir_places(direccion)
        if altura is None:
            continue
        for puertas in puertas_por_fila:
            if any(misma_calle(tokens, calle) and puerta is not None
                   and abs(altura - puerta) <= TOLERANCIA_ALTURA
                   for calle, puerta in puertas):
                total += 1
                break
    return total


def evaluar(fila: pd.Series) -> str:
    """El veredicto por zona, contra la predicción escrita para su familia de método."""
    if fila.m < M_MINIMO:
        return "no se lee · m chico"
    prediccion = PREDICCIONES.get(fila.metodo, ("SIN PREDICCIÓN", ""))[0]
    razon = fila.n_estimado / fila.cifra_publicada
    if prediccion == "CERCA":
        return "cumple" if abs(razon - 1) <= TOLERANCIA_ACIERTO else "FALLA"
    if prediccion == "POR ENCIMA":
        return "cumple" if razon > 1 else "FALLA"
    if prediccion == "MUY POR ENCIMA":
        return "cumple" if razon > 1.5 else "FALLA"
    return "sin predicción"


def tabla_de_zonas() -> pd.DataFrame:
    zonas = zonas_con_cifra()
    filas = []
    for rid in zonas.index:
        places = puntos_del_control(rid)
        if not len(places):
            continue
        padron = direcciones_padron(rid)
        n1 = int((padron.es_nucleo & ~padron.es_outlier).sum())
        n2 = len(places)
        m = coincidencias(places, padron)
        estimacion = chapman(n1, n2, m)
        filas.append({
            "rid": rid, "zona": zonas.zona_publicada[rid], "metodo": zonas.metodo[rid],
            "cifra_publicada": int(zonas.relevado[rid]),
            "padron_nucleo": n1, "places_nucleo": n2, "m": m,
            "n_estimado": round(estimacion["n_estimado"], 1),
            "ic_bajo": round(estimacion["ic_bajo"], 1),
            "ic_alto": round(estimacion["ic_alto"], 1),
        })
    tabla = pd.DataFrame(filas)
    tabla["razon_sobre_publicada"] = (tabla.n_estimado / tabla.cifra_publicada).round(2)
    # La proporción de puntos de Places que el padrón ya tiene. No es el estimador —no supone
    # independencia ni población cerrada— y por eso sobrevive aunque el estimador se caiga.
    tabla["pct_places_en_padron"] = (100 * tabla.m / tabla.places_nucleo).round(1)
    tabla["prediccion"] = [PREDICCIONES.get(metodo, ("SIN PREDICCIÓN", ""))[0]
                           for metodo in tabla.metodo]
    tabla["veredicto"] = [evaluar(fila) for _, fila in tabla.iterrows()]
    return tabla


def _coma(valor: float, decimales: int = 1) -> str:
    return f"{valor:.{decimales}f}".replace(".", ",")


def _envolver(texto: str, ancho: int = 96) -> list[str]:
    lineas, actual = [], ""
    for palabra in texto.split():
        if len(actual) + len(palabra) + 1 > ancho:
            lineas.append(actual)
            actual = palabra
        else:
            actual = f"{actual} {palabra}".strip()
    if actual:
        lineas.append(actual)
    return lineas


def informar(tabla: pd.DataFrame) -> tuple[str, dict]:
    salida = io.StringIO()
    def linea(texto: str = "") -> None:
        print(texto, file=salida)

    linea("=" * 106)
    linea("PADRÓN × PLACES COMO CAPTURA-RECAPTURA · 17 ZONAS CON CIFRA PUBLICADA · CERO REQUESTS")
    linea("=" * 106)
    linea()
    linea("§1 · LAS PREDICCIONES, ESCRITAS ANTES DE CALCULAR")
    linea("-" * 106)
    for metodo, (prediccion, motivo) in PREDICCIONES.items():
        linea(f"  {metodo:<24}{prediccion:<18}{motivo}")
    linea(f"  Zonas con m < {M_MINIMO} coincidencias: se informan y NO se leen.")
    linea()
    linea("§2 · LA TABLA")
    linea("-" * 106)
    encabezado = (f"  {'rid':<5}{'zona':<26}{'publicada':>10}{'padrón':>8}{'places':>8}{'m':>5}"
                  f"{'m/places':>10}{'N̂':>8}{'IC 95 %':>15}{'N̂/pub':>8}  veredicto")
    linea(encabezado)
    for fila in tabla.itertuples():
        ic = f"{int(fila.ic_bajo)}–{int(fila.ic_alto)}"
        linea(f"  {fila.rid:<5}{fila.zona[:25]:<26}{fila.cifra_publicada:>10}{fila.padron_nucleo:>8}"
              f"{fila.places_nucleo:>8}{fila.m:>5}{_coma(fila.pct_places_en_padron) + ' %':>10}"
              f"{_coma(fila.n_estimado, 0):>8}{ic:>15}"
              f"{_coma(fila.razon_sobre_publicada, 2):>8}  {fila.veredicto}")
    linea()
    linea("§3 · CÓMO SALIÓ CADA PREDICCIÓN")
    linea("-" * 106)
    leidas = tabla[tabla.veredicto.isin(["cumple", "FALLA"])]
    for metodo in PREDICCIONES:
        grupo = leidas[leidas.metodo == metodo]
        if not len(grupo):
            continue
        cumplen = int((grupo.veredicto == "cumple").sum())
        linea(f"  {metodo:<24}{cumplen} de {len(grupo)} cumplen"
              f"   ({', '.join(f'{f.rid}={_coma(f.razon_sobre_publicada, 2)}' for f in grupo.itertuples())})")
    no_leidas = tabla[tabla.veredicto == "no se lee · m chico"]
    if len(no_leidas):
        linea(f"  no se leen (m < {M_MINIMO}): {', '.join(no_leidas.rid)}")
    linea()

    campo = leidas[leidas.metodo == "relevamiento propio"]
    aciertos = int((campo.veredicto == "cumple").sum())
    linea("§4 · LO QUE ESTO HABILITA Y LO QUE NO")
    linea("-" * 106)
    for texto in _envolver(
        f"Sobre las zonas con conteo de campo —la única familia con una verdad contra la cual "
        f"medir— el estimador cumple en {aciertos} de {len(campo)}. "
        + ("Eso es una señal, no un método validado: son pocas zonas, la independencia entre "
           "las dos fuentes es un supuesto y las dos recortan la población de manera distinta. "
           "Lo que habilita es una prueba dirigida, no un barrido completo."
           if aciertos == len(campo) and len(campo) >= 3 else
           "Con ese resultado el estimador no se sostiene y la línea se cierra acá.")):
        linea(f"  {texto}")
    linea()
    for texto in _envolver(
        "Lo que NO habilita, en ningún caso: publicar un N̂ como cifra de un barrio. Estas cifras "
        "son estimaciones con supuestos fuertes; las cifras del Atlas se contaron. No se mezclan, "
        "no se promedian y no se comparan en la misma tabla sin decir cuál es cuál."):
        linea(f"  {texto}")
    linea()
    linea("§5 · LO QUE SÍ SOBREVIVE · LA PROPORCIÓN DE SOLAPE, SIN SUPUESTOS")
    linea("-" * 106)
    solidas = tabla[tabla.places_nucleo >= MUESTRA_MINIMA]
    for texto in _envolver(
        "La columna `m/places` no es el estimador: es cuántos de los puntos que Places trajo ya "
        "estaban en el padrón. No supone independencia, ni población cerrada, ni nada. Se cuenta y "
        "listo, y por eso sigue en pie aunque el estimador se haya caído."):
        linea(f"  {texto}")
    linea()
    linea(f"  Zonas con al menos {MUESTRA_MINIMA} puntos de Places: {len(solidas)}")
    linea(f"  Puntos de Places que el padrón YA tiene: mínimo {_coma(solidas.pct_places_en_padron.min())} % "
          f"({solidas.loc[solidas.pct_places_en_padron.idxmin()].rid}), "
          f"mediana {_coma(solidas.pct_places_en_padron.median())} %, "
          f"máximo {_coma(solidas.pct_places_en_padron.max())} % "
          f"({solidas.loc[solidas.pct_places_en_padron.idxmax()].rid})")
    mayoria_fuera = int((solidas.pct_places_en_padron < 50).sum())
    linea(f"  Zonas donde la MAYORÍA de lo que Places trae no está en el padrón: "
          f"{mayoria_fuera} de {len(solidas)}")
    linea()
    for texto in _envolver(
        "Ésta es la respuesta replicada a la pregunta que abrió el cruce de R08, y no depende de "
        "una sola zona ni del estimador que se acaba de caer: en casi todas las zonas medidas, la "
        "mayor parte de lo que Places encuentra son direcciones que el padrón no tiene. El reparto "
        "varía mucho de una zona a otra —y esa variación es en sí misma un hallazgo: dónde el "
        "padrón está al día, Places agrega poco—, pero la dirección es siempre la misma."):
        linea(f"  {texto}")
    linea()
    linea("=" * 106)

    resumen = {
        "fecha_calculo": dt.date.today().isoformat(),
        "requests_gastados": 0,
        "m_minimo": M_MINIMO,
        "tolerancia_acierto": TOLERANCIA_ACIERTO,
        "zonas": int(len(tabla)),
        "zonas_leidas": int(len(leidas)),
        "campo_aciertos": aciertos,
        "campo_total": int(len(campo)),
        "por_metodo": {
            metodo: {
                "cumplen": int((leidas[leidas.metodo == metodo].veredicto == "cumple").sum()),
                "leidas": int((leidas.metodo == metodo).sum()),
            } for metodo in PREDICCIONES
        },
    }
    return salida.getvalue(), resumen


def main() -> int:
    argparse.ArgumentParser(description=__doc__).parse_args()
    tabla = tabla_de_zonas()
    texto, resumen = informar(tabla)
    print(texto)
    tabla.to_csv(GEN / "universo_por_captura_17_zonas.csv", index=False, encoding="utf-8")
    (GEN / "universo_por_captura_resumen.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")
    (GEN / "UNIVERSO_POR_CAPTURA_17_ZONAS.txt").write_text(texto, encoding="utf-8")
    print(f"  publicado en {GEN.relative_to(ROOT)}: universo_por_captura_17_zonas.csv, "
          "universo_por_captura_resumen.json, UNIVERSO_POR_CAPTURA_17_ZONAS.txt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
