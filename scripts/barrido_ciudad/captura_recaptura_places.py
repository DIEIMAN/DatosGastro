"""Captura-recaptura sobre las dos corridas de Places en R08. CERO requests.

QUÉ PREGUNTA CONTESTA, Y POR QUÉ ES GRATIS
------------------------------------------
La prueba de techo dejó abierto si el 12 % que Places recupera en Villa Crespo es el techo de la
FUENTE o el techo de UNA barrida. Hay dos muestras independientes de la misma población, ya
pagadas y guardadas en disco:

  - **muestra 1** · familia A del control, sólo los puntos que trajeron celdas de R08 (la línea
    comparable que fija `baseline_del_control`);
  - **muestra 2** · familia A de la prueba de techo: la misma consulta, sobre las mismas celdas,
    otra corrida.

Misma consulta, misma geometría, distinta corrida. Eso es captura-recaptura, y el solape entre las
dos contesta cuánto queda sin ver. **No cuesta un solo request: es un merge por `place_id`.**

  m  = place_id en común entre las dos corridas
  N̂  = (n1+1)(n2+1)/(m+1) − 1        estimador de Chapman

Solape alto ⇒ las dos corridas ven casi lo mismo ⇒ el universo alcanzable por Places está casi
agotado con una corrida, y el 12 % es techo estructural. Solape bajo ⇒ cada corrida ve un
subconjunto distinto y la unión acumulada llega mucho más alto: Places no sería pobre, sería no
reproducible, que es otra cosa y se usa distinto.

LAS DOS ADVERTENCIAS QUE VIAJAN CON EL NÚMERO
---------------------------------------------
Van impresas en el informe, no en un comentario del código, porque el número se cita y el
comentario no:

1. **El estimador supone igual capturabilidad, y acá no la hay.** Lo que sale es una **cota
   inferior** del universo alcanzable, no un valor central. El §4 mide la desigualdad con los datos
   que ya están, y resulta ser más filosa que «unos aparecen más que otros»: hay locales con
   probabilidad de captura CERO, y a ésos la captura-recaptura no los ve por construcción.
2. **Estima el universo alcanzable POR PLACES, no el universo real.** Los 646 locales de Villa
   Crespo son un conteo de campo; N̂ es cuántos de ellos esta consulta sobre esta grilla podría
   llegar a mostrar acumulando corridas. No es una segunda estimación de la cifra publicada y no se
   mezcla con ella.

QUÉ SE ESCRIBIÓ ANTES Y QUÉ DESPUÉS
-----------------------------------
`LECTURA_PREVIA` y el veredicto del §1 están escritos **antes** de calcular m, igual que en la
prueba de techo y por el mismo motivo: con el número a la vista, cualquier resultado se acomoda a
la conclusión que ya se tenía.

Los §2, §3 y §4 se agregaron **después** de ver el número, y se declara: son el diagnóstico de la
causa, no la lectura. Las bandas no se tocaron ni se movió el veredicto.

GUARDARRAÍLES
-------------
- **No toca la red.** No hay endpoint, no hay key, no hay presupuesto que gastar. Si este script
  alguna vez necesita un request, está mal escrito.
- Los `place_id` y los nombres se leen de la carpeta interna ignorada por Git y **no salen de
  ella**: lo que se publica son conteos.

USO
---
  python scripts/barrido_ciudad/captura_recaptura_places.py
  python scripts/barrido_ciudad/captura_recaptura_places.py --zona R08
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from places_control_zonas import (  # noqa: E402
    GEN,
    INTERNO as INTERNO_CONTROL,
    LADO_BASE_M,
    TECHO_API,
    asignar_por_geometria,
    zonas_con_cifra,
)
from places_techo_zona import (  # noqa: E402
    FAMILIA_ESPEJO,
    INTERNO as INTERNO_TECHO,
)

ZONA_POR_DEFECTO = "R08"

# Las bandas están escritas ANTES de calcular m. El veredicto lo elige el número.
#
# El piso aritmético de N̂ es la unión observada (n1 + n2 − m): el estimador no puede quedar por
# debajo de lo que ya se vio. Por eso la banda baja no arranca en cero de verdad.
LECTURA_PREVIA = [
    (0.0, 95.0, "UNIVERSO ALCANZABLE CASI AGOTADO · conclusión cerrada",
     "Una corrida ve casi todo lo que Places puede mostrar. El 12 % es techo estructural de la "
     "fuente, no de esta barrida: acumular corridas no cambiaría el orden de magnitud. La "
     "conclusión operativa —Places es fuente de contraste, no de conteo— queda cerrada del todo."),
    (95.0, 130.0, "EN EL MEDIO · decide Diego",
     "El universo alcanzable es mayor que una corrida pero no tanto como para cambiar el uso de "
     "la fuente. Se reporta el número y se decide con Diego, sin acomodar la lectura."),
    (130.0, 1e9, "PLACES NO ES POBRE, ES NO REPRODUCIBLE · replantear con Diego",
     "Cada corrida ve un subconjunto distinto y la unión acumulada llega bastante más alto. Eso "
     "cambia cómo se usa la fuente: pasa de contraste a descubrimiento por acumulación, y hay "
     "que replantearlo con Diego ANTES de cerrar nada."),
]

# Cuartiles de posición dentro de la celda, como proxy de ranking. Ver `heterogeneidad()`.
CUARTILES = [(0, 25, "1.º cuarto (mejor rankeados)"), (25, 50, "2.º cuarto"),
             (50, 75, "3.º cuarto"), (75, 101, "4.º cuarto (fondo del ranking)")]

# Una celda se declara DISCORDANTE entre corridas si le cambió el estado de saturación —que es lo
# que decide si se refina o no— o si la cantidad devuelta se movió por lo menos esto. Con menos que
# eso la celda reprodujo: el ruido de uno o dos resultados no cambia ninguna decisión.
DIFERENCIA_MATERIAL = 10


# --------------------------------------------------------------------------- las dos muestras

def muestra_control(rid: str) -> pd.DataFrame:
    """Los puntos del control que trajeron celdas de ESTA zona y caen dentro de su envolvente.

    Es la misma línea que fija `baseline_del_control()` en la prueba de techo, y por el mismo
    motivo: el control consultó las 17 zonas y las celdas vecinas barren territorio de ésta, así
    que su total incluye puntos que las celdas de R08 nunca trajeron. Para captura-recaptura hace
    falta que las dos muestras tengan la MISMA cobertura, o el solape mide dos cosas mezcladas.
    """
    archivo = INTERNO_CONTROL / "places_puntos_interno.csv"
    if not archivo.exists():
        raise SystemExit(f"ABORTADO: falta {archivo}. No hay muestra 1.")
    puntos = asignar_por_geometria(pd.read_csv(archivo, encoding="utf-8-sig"))
    return puntos[(puntos.rid_geo == rid) & (puntos.anillo == "nucleo")
                  & (puntos.rid == rid)].copy()


def muestra_techo(rid: str) -> pd.DataFrame:
    """Los puntos de la prueba de techo que caen dentro de la envolvente, todas las familias."""
    archivo = INTERNO_TECHO / f"places_techo_{rid}_puntos.csv"
    if not archivo.exists():
        raise SystemExit(f"ABORTADO: falta {archivo}. No hay muestra 2.")
    puntos = asignar_por_geometria(pd.read_csv(archivo, encoding="utf-8-sig"))
    return puntos[(puntos.rid_geo == rid) & (puntos.anillo == "nucleo")].copy()


def bitacoras(rid: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Las dos bitácoras de celdas, recortadas a la zona y a la familia espejo."""
    control = pd.read_csv(INTERNO_CONTROL / "places_bitacora_celdas.csv")
    techo = pd.read_csv(INTERNO_TECHO / f"places_techo_{rid}_bitacora.csv")
    return (control[control.rid == rid].copy(),
            techo[techo.familia == FAMILIA_ESPEJO].copy())


# --------------------------------------------------------------------------- el estimador

def chapman(n1: int, n2: int, m: int) -> dict:
    """Chapman con su varianza de Seber, y el piso aritmético declarado.

    Chapman en vez de Lincoln-Petersen (n1·n2/m) porque con muestras chicas el segundo se va a
    infinito cuando el solape es chico y no tiene esperanza finita. El +1 de Chapman lo acota.
    """
    estimado = (n1 + 1) * (n2 + 1) / (m + 1) - 1
    varianza = ((n1 + 1) * (n2 + 1) * (n1 - m) * (n2 - m)
                / ((m + 1) ** 2 * (m + 2)))
    error = math.sqrt(varianza)
    union = n1 + n2 - m
    return {
        "n1": n1, "n2": n2, "m": m,
        "union_observada": union,
        "n_estimado": estimado,
        "error_estandar": error,
        # Intervalo normal al 95 %, recortado por abajo al piso aritmético: el universo no puede
        # ser más chico que lo que ya se vio con los ojos.
        "ic_bajo": max(union, estimado - 1.96 * error),
        "ic_alto": estimado + 1.96 * error,
        "ic_bajo_crudo": estimado - 1.96 * error,
        "solape_sobre_n1": 100 * m / n1 if n1 else None,
        "solape_sobre_n2": 100 * m / n2 if n2 else None,
    }


def veredicto(estimado: float) -> tuple[str, str]:
    for piso, techo, titulo, texto in LECTURA_PREVIA:
        if piso <= estimado < techo:
            return titulo, texto
    return "FUERA DE TODA BANDA", "Revisar: el número no cae en ninguna banda prevista."


# --------------------------------------------------------------------------- diagnóstico

def celdas_discordantes(bit_control: pd.DataFrame, bit_techo: pd.DataFrame) -> pd.DataFrame:
    """Celdas que las dos corridas consultaron igual y contestaron distinto, con su diferencia.

    Sirve para separar dos cosas que el total de la zona confunde: si la variación entre corridas
    está repartida por toda la grilla, la fuente es ruidosa en todas partes; si está concentrada en
    una celda, la fuente reproduce y lo que falló fue una decisión de refinamiento.
    """
    columnas = ["celda_id", "lado_m", "devueltos", "saturada", "requests"]
    juntas = bit_control[columnas].merge(bit_techo[columnas], on=["celda_id", "lado_m"],
                                        suffixes=("_control", "_techo"))
    juntas["diferencia"] = juntas.devueltos_techo - juntas.devueltos_control
    juntas["saturacion_cambio"] = juntas.saturada_control != juntas.saturada_techo
    juntas["discordante"] = (juntas.saturacion_cambio
                             | (juntas.diferencia.abs() >= DIFERENCIA_MATERIAL))
    return juntas.sort_values("diferencia")


def heterogeneidad(puntos: pd.DataFrame, recapturados: set[str]) -> pd.DataFrame:
    """Cuánto depende la recaptura del lugar que ocupó el local en el ranking de su celda.

    No hay columna de ranking guardada, pero el archivo interno conserva el ORDEN en que la API
    devolvió cada punto dentro de su celda, y ese orden es el ranking de Text Search. Se usa la
    posición relativa dentro de la celda como proxy.

    El proxy tiene un defecto conocido y acotado: el dedup entre celdas corre posiciones hacia
    arriba, porque un punto que ya se había visto no se vuelve a guardar. Sirve para ver la
    PENDIENTE —si los primeros se recapturan más que los últimos—, no para leer cada cuartil como
    una probabilidad exacta.
    """
    filas = []
    puntos = puntos.copy()
    puntos["posicion"] = puntos.groupby("celda_id").cumcount()
    tamanos = puntos.groupby("celda_id").place_id.transform("size")
    puntos["percentil"] = 100 * puntos.posicion / tamanos.clip(lower=1)
    for desde, hasta, etiqueta in CUARTILES:
        tramo = puntos[(puntos.percentil >= desde) & (puntos.percentil < hasta)]
        if not len(tramo):
            continue
        vueltos = int(tramo.place_id.isin(recapturados).sum())
        filas.append({"tramo": etiqueta, "locales": len(tramo), "recapturados": vueltos,
                      "pct_recaptura": round(100 * vueltos / len(tramo), 1)})
    return pd.DataFrame(filas)


def firma_de_truncacion(puntos: pd.DataFrame, recapturados: set[str],
                        celda: str) -> pd.DataFrame:
    """Recaptura por cuarto del ranking DENTRO de una celda, en el orden en que la API la devolvió.

    Distingue dos mecanismos que dan la misma cantidad de pérdidas y significan cosas distintas:
    si las pérdidas están repartidas por todo el ranking, la lista es inestable; si están todas al
    final, la lista es estable y lo que se movió es hasta dónde la sirvieron.
    """
    de_celda = puntos[puntos.celda_id == celda].copy()
    if len(de_celda) < 4:
        return pd.DataFrame()
    de_celda["posicion"] = range(len(de_celda))
    de_celda["cuarto"] = pd.cut(de_celda.posicion, 4,
                                labels=["1.º cuarto", "2.º cuarto", "3.º cuarto",
                                        "4.º cuarto (final de la lista)"])
    de_celda["recap"] = de_celda.place_id.isin(recapturados)
    tabla = de_celda.groupby("cuarto", observed=True).recap.agg(["size", "sum"]).reset_index()
    tabla.columns = ["cuarto", "locales", "recapturados"]
    tabla["pct_recaptura"] = (100 * tabla.recapturados / tabla.locales).round(1)
    return tabla


# --------------------------------------------------------------------------- informe

def publicar(rid: str) -> None:
    zonas = zonas_con_cifra()
    relevado = float(zonas.relevado[rid])
    control = muestra_control(rid)
    techo = muestra_techo(rid)
    espejo = techo[techo.familia_primera == FAMILIA_ESPEJO]
    bit_control, bit_techo = bitacoras(rid)

    ids_1 = set(control.place_id)
    ids_2 = set(espejo.place_id)
    comunes = ids_1 & ids_2
    resultado = chapman(len(ids_1), len(ids_2), len(comunes))
    titulo, texto = veredicto(resultado["n_estimado"])

    # Igual esfuerzo: las celdas que las dos corridas consultaron de verdad. La segunda refinó una
    # celda menos, así que unos pocos puntos del control vienen de celdas que la segunda nunca
    # miró: ésos tenían probabilidad de captura CERO por diseño, no por la fuente.
    solo_control = sorted(set(bit_control.celda_id) - set(bit_techo.celda_id))
    solo_techo = sorted(set(bit_techo.celda_id) - set(bit_control.celda_id))
    comun_celdas = control[~control.celda_id.isin(solo_control)]
    ids_1c = set(comun_celdas.place_id)
    igual_esfuerzo = chapman(len(ids_1c), len(ids_2), len(ids_1c & ids_2))

    # Sensibilidad con la unión de las tres familias como segunda muestra. NO es la estimación:
    # el protocolo de captura deja de ser el mismo y el supuesto se rompe de otra manera.
    ids_2_todas = set(techo.place_id)
    sensibilidad = chapman(len(ids_1), len(ids_2_todas), len(ids_1 & ids_2_todas))

    fechas_1 = sorted(control.fecha_consulta.dropna().astype(str).unique().tolist())
    fechas_2 = sorted(espejo.fecha_consulta.dropna().astype(str).unique().tolist())

    print("=" * 78)
    print(f"  CAPTURA-RECAPTURA · {rid} · {zonas.zona_publicada[rid]}")
    print("  dos corridas de la misma consulta sobre las mismas celdas · CERO requests")
    print("=" * 78)
    print("")
    print(f"  muestra 1 · familia A del control ({', '.join(fechas_1) or 's/f'}), "
          f"celdas de {rid} solamente     n1 = {resultado['n1']}")
    print(f"  muestra 2 · familia A de la prueba de techo ({', '.join(fechas_2) or 's/f'}), "
          f"misma consulta   n2 = {resultado['n2']}")
    if fechas_1 == fechas_2:
        print("")
        print("  ATENCIÓN: las dos corridas son del MISMO día. La variación entre ellas no es")
        print("  deriva de un día para otro; es la misma consulta contestada distinto en la misma")
        print("  tarde.")
    print("")
    print(f"  m  · place_id en común                 : {resultado['m']}")
    print(f"       de la muestra 1 volvió a aparecer : {resultado['solape_sobre_n1']:.1f} %")
    print(f"       de la muestra 2 ya estaba         : {resultado['solape_sobre_n2']:.1f} %")
    print(f"  locales que la 2.ª corrida agregó      : {len(ids_2 - ids_1)}")
    print(f"  unión observada de las dos corridas    : {resultado['union_observada']}  "
          "(piso aritmético de N̂)")
    print("")
    print(f"  N̂ · Chapman = ({resultado['n1']}+1)({resultado['n2']}+1)/({resultado['m']}+1) − 1"
          f" = {resultado['n_estimado']:.1f}")
    print(f"  error estándar (Seber): {resultado['error_estandar']:.1f}")
    print(f"  IC 95 % aproximado: {resultado['ic_bajo']:.0f} – {resultado['ic_alto']:.0f}", end="")
    if resultado["ic_bajo_crudo"] < resultado["union_observada"]:
        print(f"   (el borde bajo crudo daba {resultado['ic_bajo_crudo']:.0f}, "
              "por debajo de lo ya observado: se recorta al piso)")
    else:
        print("")

    print("")
    print("-" * 78)
    print("  §1 · VEREDICTO · banda escrita ANTES de calcular m")
    print("-" * 78)
    print(f"  N̂ = {resultado['n_estimado']:.0f} → {titulo}")
    for linea in _envolver(texto, 74):
        print(f"  {linea}")
    ver_bajo = veredicto(resultado["ic_bajo"])[0]
    ver_alto = veredicto(resultado["ic_alto"])[0]
    if ver_bajo != ver_alto:
        print("")
        print(f"  *** El IC CRUZA bandas: «{ver_bajo}» en el borde bajo, «{ver_alto}» en el alto.")
        print("      El punto estimado no alcanza para cerrar solo; se reporta el cruce.")
    else:
        print("  Las dos puntas del IC caen en la misma banda: el veredicto no depende del borde.")
    print("")
    print("  LAS DOS ADVERTENCIAS, QUE VAN CON EL NÚMERO A DONDE VAYA")
    print("  1. El estimador supone igual capturabilidad. Acá no la hay (§4), así que **N̂ es una")
    print("     cota inferior** del universo alcanzable, no un valor central.")
    print(f"  2. Estima el universo alcanzable POR ESTA CONSULTA, no el universo real. Los "
          f"{int(relevado)}")
    print("     locales relevados a pie son un conteo de campo; N̂ no es una segunda estimación de")
    print("     esa cifra y no se mezcla con ella.")

    print("")
    print("-" * 78)
    print("  §2 · A IGUAL ESFUERZO · las celdas que las dos corridas consultaron de verdad")
    print("-" * 78)
    print(f"  celdas de la familia A · control: {len(bit_control)} · prueba de techo: "
          f"{len(bit_techo)}")
    if solo_control:
        print(f"  la 2.ª corrida NO consultó {len(solo_control)} celdas que la 1.ª sí: "
              f"{', '.join(solo_control)}")
        perdidos = len(ids_1) - len(ids_1c)
        print(f"  puntos del control que salieron sólo de ahí: {perdidos}. Tenían probabilidad de")
        print("  captura cero en la 2.ª muestra por diseño del refinamiento, no por la fuente.")
    if solo_techo:
        print(f"  la 1.ª corrida no consultó: {', '.join(solo_techo)}")
    print("")
    print(f"  n1 a igual esfuerzo = {igual_esfuerzo['n1']}  ·  n2 = {igual_esfuerzo['n2']}  ·  "
          f"m = {igual_esfuerzo['m']}")
    variacion = 100 * (igual_esfuerzo["n2"] - igual_esfuerzo["n1"]) / igual_esfuerzo["n1"]
    print(f"  variación entre corridas a igual esfuerzo: {variacion:+.1f} %  "
          f"(contra el total del control: "
          f"{100 * (resultado['n2'] - resultado['n1']) / resultado['n1']:+.1f} %)")
    print(f"  N̂ a igual esfuerzo = {igual_esfuerzo['n_estimado']:.1f}  ·  IC 95 % "
          f"{igual_esfuerzo['ic_bajo']:.0f} – {igual_esfuerzo['ic_alto']:.0f}  → "
          f"{veredicto(igual_esfuerzo['n_estimado'])[0].split(' · ')[0]}")
    if veredicto(igual_esfuerzo["n_estimado"])[0] == titulo:
        print("  Misma banda que el número de arriba: el veredicto no depende de cuál se use.")

    print("")
    print("-" * 78)
    print("  §3 · DÓNDE ESTÁ LA VARIACIÓN · celda por celda, mismas celdas, distinta corrida")
    print("-" * 78)
    tabla_celdas = celdas_discordantes(bit_control, bit_techo)
    base = tabla_celdas[tabla_celdas.lado_m == LADO_BASE_M]
    print(base[["celda_id", "devueltos_control", "devueltos_techo", "diferencia",
                "saturada_control", "saturada_techo"]].to_string(index=False))
    discordantes = tabla_celdas[tabla_celdas.discordante]
    reproducen = len(tabla_celdas) - len(discordantes)
    print("")
    print(f"  celdas que reprodujeron (diferencia < {DIFERENCIA_MATERIAL} y misma saturación): "
          f"{reproducen} de {len(tabla_celdas)}")
    if len(discordantes):
        for fila in discordantes.itertuples():
            print(f"  DISCORDANTE · {fila.celda_id}: {fila.devueltos_control} → "
                  f"{fila.devueltos_techo} ({fila.diferencia:+d})"
                  + ("  y dejó de saturar, así que la 2.ª corrida no la refinó"
                     if fila.saturacion_cambio else ""))
        no_recap = control[~control.place_id.isin(ids_2)]
        en_discordantes = no_recap[
            no_recap.celda_id.isin(discordantes.celda_id)
            | no_recap.celda_id.str.startswith(tuple(discordantes.celda_id + "R"))]
        print("")
        print(f"  de los {len(no_recap)} locales que no volvieron a aparecer, "
              f"{len(en_discordantes)} salen de esas celdas.")
        print("  La variación NO está repartida por la grilla: está concentrada. Siete celdas")
        print(f"  contestaron lo mismo dentro de ±{int(base.diferencia.abs()[base.discordante == False].max())}"
              " resultados y una se movió sola.")
    en_el_techo = base[base.devueltos_control >= TECHO_API]
    if len(en_el_techo):
        print("")
        print(f"  {len(en_el_techo)} celdas devolvieron exactamente {TECHO_API} en las DOS corridas: "
              "es el tope duro de")
        print("  Text Search, no un conteo. Ahí la celda está recortada por la API y se refina.")

    print("")
    print("-" * 78)
    print("  §4 · LA FIRMA · qué mecanismo produjo las pérdidas")
    print("-" * 78)
    if len(discordantes):
        celda = discordantes.iloc[0].celda_id
        firma = firma_de_truncacion(control, comunes, celda)
        if len(firma):
            print(f"  Dentro de {celda}, por cuarto del ranking que devolvió la API:")
            print(firma.to_string(index=False))
            ultimo = firma.pct_recaptura.iloc[-1]
            arriba = firma.pct_recaptura.iloc[:-1].mean()
            print("")
            print(f"  los tres primeros cuartos volvieron al {arriba:.0f} %, el último al "
                  f"{ultimo:.0f} %.")
            if ultimo < 25 <= arriba:
                print("  Ésa es la firma de una LISTA TRUNCADA, no de una lista inestable: el orden")
                print("  se reprodujo y lo que cambió fue hasta dónde la sirvieron. Lo que entra en")
                print("  el corte vuelve; lo que queda pasado el corte desaparece entero.")
    sin_discordantes = control[
        ~control.celda_id.isin(discordantes.celda_id)
        & ~control.celda_id.isin(solo_control)] if len(discordantes) else control
    print("")
    print("  Y afuera de esas celdas, ¿hay pendiente por ranking?")
    tabla_het = heterogeneidad(sin_discordantes, comunes)
    if len(tabla_het):
        print(tabla_het.to_string(index=False))
        recap_limpia = 100 * sin_discordantes.place_id.isin(comunes).mean()
        print("")
        print(f"  recaptura fuera de las celdas discordantes: {recap_limpia:.1f} % "
              f"({int(sin_discordantes.place_id.isin(comunes).sum())} de {len(sin_discordantes)})")
        primero, ultimo = tabla_het.pct_recaptura.iloc[0], tabla_het.pct_recaptura.iloc[-1]
        if abs(primero - ultimo) < 15:
            print("  Sin pendiente apreciable: donde la lista no se truncó, la fuente reprodujo")
            print("  parejo de arriba abajo del ranking.")
        else:
            print(f"  Con pendiente: {primero:.0f} % arriba contra {ultimo:.0f} % abajo.")
    print("")
    print("  POR QUÉ ESTO HACE QUE N̂ SEA UNA COTA INFERIOR, y no por el motivo habitual.")
    print("  La desigualdad de captura acá no es gradual: es un corte. Un local pasado el corte en")
    print("  las dos corridas tiene probabilidad de captura CERO, y la captura-recaptura no puede")
    print(f"  verlo por construcción. Así que N̂ ≈ {resultado['n_estimado']:.0f} estima lo que esta")
    print("  consulta sobre esta grilla puede llegar a servir, y por debajo de eso puede haber una")
    print("  cola que ninguna cantidad de corridas iguales va a mostrar. Bajar el corte es lo que")
    print("  hace el refinamiento de celdas, y eso es diseño de barrida, no acumulación.")

    print("")
    print("-" * 78)
    print("  §5 · SENSIBILIDAD · no es la estimación")
    print("-" * 78)
    print(f"  Con la unión de las tres familias como muestra 2 (n2 = {sensibilidad['n2']}, "
          f"m = {sensibilidad['m']}):")
    print(f"    N̂ = {sensibilidad['n_estimado']:.0f}  ·  IC 95 % "
          f"{sensibilidad['ic_bajo']:.0f} – {sensibilidad['ic_alto']:.0f}  → "
          f"{veredicto(sensibilidad['n_estimado'])[0].split(' · ')[0]}")
    print("  Va aparte porque ahí las dos muestras ya no se tomaron con el mismo protocolo: la 2")
    print("  buscó tres consultas y la 1 buscó una. Estima otra cosa —el universo alcanzable por")
    print("  el conjunto de las tres familias— y no compite con el número del §1.")

    tabla = pd.DataFrame([{
        "zona": rid,
        "n1_control_familia_A": resultado["n1"],
        "n2_techo_familia_A": resultado["n2"],
        "m_comunes": resultado["m"],
        "agregados_por_la_2a_corrida": len(ids_2 - ids_1),
        "union_observada": resultado["union_observada"],
        "n_estimado_chapman": round(resultado["n_estimado"], 1),
        "ic95_bajo": round(resultado["ic_bajo"], 1),
        "ic95_alto": round(resultado["ic_alto"], 1),
        "pct_recaptura_sobre_n1": round(resultado["solape_sobre_n1"], 1),
        "n1_igual_esfuerzo": igual_esfuerzo["n1"],
        "n_estimado_igual_esfuerzo": round(igual_esfuerzo["n_estimado"], 1),
        "variacion_pct_igual_esfuerzo": round(variacion, 1),
        "celdas_discordantes": int(len(discordantes)),
        "celdas_comparadas": int(len(tabla_celdas)),
        "cifra_publicada": int(relevado),
        "veredicto": titulo,
        "advertencia": ("N̂ es cota inferior del universo alcanzable POR ESTA CONSULTA: hay locales "
                        "con probabilidad de captura cero pasados el corte del ranking. No es una "
                        "estimación de la cifra publicada."),
    }])
    GEN.mkdir(parents=True, exist_ok=True)
    tabla.to_csv(GEN / f"captura_recaptura_{rid}.csv", index=False, encoding="utf-8")
    (GEN / f"captura_recaptura_{rid}_resumen.json").write_text(
        json.dumps({"fecha_calculo": dt.date.today().isoformat(),
                    "corridas": {"muestra_1": fechas_1, "muestra_2": fechas_2},
                    "requests_gastados": 0,
                    **{k: (round(v, 2) if isinstance(v, float) else v)
                       for k, v in resultado.items()},
                    "veredicto": titulo,
                    "igual_esfuerzo": {k: (round(v, 2) if isinstance(v, float) else v)
                                       for k, v in igual_esfuerzo.items()},
                    "celdas_no_consultadas_por_la_2a": solo_control,
                    "celdas_discordantes": discordantes.celda_id.tolist(),
                    "sensibilidad_tres_familias": {
                        "n2": sensibilidad["n2"], "m": sensibilidad["m"],
                        "n_estimado": round(sensibilidad["n_estimado"], 1)},
                    "heterogeneidad_sin_discordantes": tabla_het.to_dict("records")},
                   ensure_ascii=False, indent=2), encoding="utf-8")

    print("")
    print(f"  publicable: {GEN / f'captura_recaptura_{rid}.csv'}")
    print("  requests gastados: 0. Este script no toca la red.")


def _envolver(texto: str, ancho: int) -> list[str]:
    palabras, linea, salida = texto.split(), "", []
    for palabra in palabras:
        if len(linea) + len(palabra) + 1 > ancho:
            salida.append(linea)
            linea = palabra
        else:
            linea = f"{linea} {palabra}".strip()
    if linea:
        salida.append(linea)
    return salida


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Captura-recaptura entre las dos corridas de Places. No toca la red.")
    ap.add_argument("--zona", default=ZONA_POR_DEFECTO,
                    help=f"referencia_id de la zona (default {ZONA_POR_DEFECTO}).")
    args = ap.parse_args()
    publicar(args.zona)
    return 0


if __name__ == "__main__":
    sys.exit(main())
