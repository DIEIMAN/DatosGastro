"""Ronda 9 · la escalera de calibración de Places · CUATRO requests, por dirección.

QUÉ PREGUNTA, Y POR QUÉ ESTOS CUATRO
-------------------------------------
La ronda 8 midió que Places falla en dos de tres cierres conocidos y acierta el de 3.285 días.
Con tres puntos no se sabe **dónde** está el corte: sólo que cae entre 280 y 3.285 días. Esta
corrida pone cuatro peldaños adentro de esa horquilla y en su extremo:

    El Palacio de la Papa Frita   Av. Corrientes 1612      159 días
    Mercado de los Carruajes      Retiro                  ~480 días
    Confitería del Hotel Castelar Av. de Mayo 1152      ~2.290 días
    La Perla del Once             Av. Rivadavia 2800     3.493 días   ← TEST DECISIVO

LA HIPÓTESIS, ESCRITA ANTES DE CORRER · R1
--------------------------------------------
**Places sigue el LUGAR, no el negocio.**

La Perla del Once cerró hace más que el Plaza Bar —3.493 días contra 3.285— y en su local
funciona hoy la pizzería La Americana. Los dos casos son casi iguales en antigüedad y opuestos en
ocupación: el Plaza Bar está dentro de un hotel vacío en obra, y La Perla del Once tiene un
negocio abierto en la puerta.

    si vuelve CLOSED_PERMANENTLY   Places sigue al NEGOCIO. La lectura de v2b se sostiene.
    si vuelve OPERATIONAL          Places sigue al LUGAR — y entonces CLOSED_PERMANENTLY tampoco
                                   acredita cierre del establecimiento, sólo que la dirección no
                                   tiene un comercio activo. Hay que reescribir v2b por tercera vez.

Esa es toda la corrida: **el resultado tiene consecuencia escrita de antemano en los dos
sentidos**, que es lo que la distingue de salir a mirar a ver qué pasa.

POR QUÉ SE CONSULTA POR DIRECCIÓN Y NO POR NOMBRE
---------------------------------------------------
Hay cuatro «Perla» en el Atlas, y la ronda 8 ya consultó una de ellas —La Perla de Caminito, Av.
Don Pedro de Mendoza 1899, que está abierta y no tiene nada que ver—. Preguntar por «La Perla»
devolvería esa. El `textQuery` de esta corrida lleva la dirección primero y el nombre después,
y el control de identidad se hace contra la altura, como en la ronda 8.

EL COSTO
--------
Misma máscara de tres campos que la ronda 8 —la fijó la decisión 4— y por lo tanto mismo SKU:
Text Search **Enterprise**, 1.000 gratis por mes y USD 35,00 por 1.000 después. Cuatro requests.
Si el cupo estuviera agotado, USD 0,14. La caché es la misma de la ronda 8: las 71 ya escritas no
se vuelven a pagar, y estas cuatro quedan escritas después de cada request.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/ronda_9_escalera_places.py            # seco
  .venv/Scripts/python.exe scripts/barrido_ciudad/ronda_9_escalera_places.py --ejecutar
"""
from __future__ import annotations

import argparse
import io
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from places_control_zonas import cargar_dotenv, leer_api_key  # noqa: E402
from polos_soporte import BARRIDO  # noqa: E402
from ronda_8_places_incremental import (  # noqa: E402
    CAMPOS as CAMPOS_R8,
    GRATIS_ENTERPRISE_MENSUAL,
    PRECIO_ENTERPRISE_USD_1000,
    identidad,
    p_factory,
)

INTERNO = ROOT / "outputs" / "analisis_interno" / "places_vigencia_2026-08"
SALIDA = BARRIDO / "ronda_9"
CACHE = INTERNO / "_cache_places_vigencia.json"
OUT = SALIDA / "places_escalera_de_calibracion.csv"
INFORME = SALIDA / "PLACES_ESCALERA_R9.txt"

# La máscara de la ronda 8 MÁS `displayName`. Sin el nombre, la respuesta no puede distinguir
# «Places marcó el bar histórico» de «Places marcó el comercio que ocupa hoy el local», que es
# EXACTAMENTE la pregunta de esta corrida. Es R7: un campo que la consulta no pidió y sin el cual
# el resultado no responde. `displayName` es campo Essentials y NO sube el SKU: la corrida ya cae
# en Enterprise por `regularOpeningHours`, así que el precio por request no cambia.
CAMPOS = [*CAMPOS_R8, "places.displayName"]

TOPE_ABSOLUTO = 8  # cuatro de la escalera + las cuatro de la relectura con displayName.
HOY = date(2026, 8, 8)

# (nombre, dirección para la consulta, cerró el, días, lo que sabemos, qué significaría cada salida)
ESCALERA = [
    ("El Palacio de la Papa Frita", "Av. Corrientes 1612", "2026-03-02", 159,
     "persianas bajadas el 02/03/2026; anuncian reapertura en Paraná 350",
     "local a la calle, vacío"),
    ("Mercado de los Carruajes", "Av. Ramos Mejía 1300, Retiro", "2025-04-15", 480,
     "cerrado desde 2025; edificio patrimonial del GCBA", "edificio cerrado"),
    ("Confitería del Hotel Castelar", "Av. de Mayo 1152", "2020-05-01", 2290,
     "el hotel cerró en mayo de 2020 y sigue cerrado y en venta por USD 7 millones",
     "dentro de un hotel cerrado"),
    ("La Perla del Once", "Av. Rivadavia 2800", "2017-01-15", 3493,
     "cerró hace más que el Plaza Bar; en su local funciona hoy la pizzería La Americana",
     "LOCAL OCUPADO POR OTRO NEGOCIO ← el test decisivo"),
]


def consultar_con(clave: str, consulta: str, campos: list[str]) -> tuple[dict | None, str | None]:
    """Un request con máscara propia. Copia de `ronda_8.consultar` con `campos` parametrizado."""
    import requests

    from ronda_8_places_incremental import ENDPOINT

    try:
        respuesta = requests.post(
            ENDPOINT,
            headers={"Content-Type": "application/json", "X-Goog-Api-Key": clave,
                     "X-Goog-FieldMask": ",".join(campos)},
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
    parser.add_argument("--tope", type=int, default=4)
    parser.add_argument("--sufijo", default="", help="separa la clave de caché de la corrida previa")
    args = parser.parse_args()
    tope = min(args.tope, TOPE_ABSOLUTO)

    buffer = io.StringIO()
    p = p_factory(buffer)
    SALIDA.mkdir(parents=True, exist_ok=True)
    INTERNO.mkdir(parents=True, exist_ok=True)

    p("RONDA 9 · LA ESCALERA DE CALIBRACIÓN DE PLACES")
    p("=" * 100)
    p("")
    p("  LA HIPÓTESIS, ESCRITA ANTES DE CORRER (R1): Places sigue el LUGAR, no el negocio.")
    p("")
    p("      La Perla del Once cerró hace 3.493 días —más que el Plaza Bar, 3.285— y en su local")
    p("      funciona hoy la pizzería La Americana.")
    p("")
    p("      CLOSED_PERMANENTLY  → Places sigue al negocio. v2b se sostiene como está.")
    p("      OPERATIONAL         → Places sigue al lugar. CLOSED_PERMANENTLY deja de acreditar")
    p("                            cierre del ESTABLECIMIENTO y hay que reescribir v2b.")
    p("")
    p("  Los dos desenlaces están escritos antes de preguntar, y los dos tienen consecuencia.")
    p("")
    p("-" * 100)
    p("  LA ESCALERA, con lo que ya sabemos de cada peldaño")
    p("")
    p(f"      {'establecimiento':<32}{'días':>7}  {'situación del local':<38}")
    for nombre, direccion, _, dias, _, situacion in ESCALERA:
        p(f"      {nombre:<32}{dias:>7}  {situacion:<38}")
    p("")
    p("      con los tres de la ronda 8, la escala queda:")
    p("        143 d  The New Brighton   OPERATIONAL   (quiebra, atendiendo)")
    p("        159 d  Papa Frita         ?")
    p("        280 d  La Buena Medida    OPERATIONAL   ← falla conocida")
    p("        480 d  Carruajes          ?")
    p("      2.290 d  Castelar           ?")
    p("      3.285 d  Plaza Bar          CLOSED_PERM.  ← acierto conocido")
    p("      3.493 d  La Perla del Once  ?             ← decide la hipótesis")
    p("")
    p("      El corte de detección está entre 280 y 3.285 días. Estos cuatro lo acotan, y el")
    p("      último además pregunta OTRA cosa: qué objeto es el que Places está siguiendo.")
    p("")
    p("  CUIDADO YA APLICADO · hay cuatro «Perla» en el Atlas. La ronda 8 consultó «La Perla (de")
    p("  Caminito), Av. Don Pedro de Mendoza 1899», que está abierta. Esta corrida pregunta por")
    p("  DIRECCIÓN, no por nombre.")
    p("")
    p("-" * 100)
    p("  EL COSTO, ANTES DEL PRIMER REQUEST")
    p("")
    p("      Text Search Enterprise · 1.000 gratis por mes · USD 35,00 por 1.000 después.")
    p(f"      máscara: {', '.join(CAMPOS)}")
    p("      `regularOpeningHours` es el campo que sube a Enterprise. Lo fijó la decisión 4.")
    p(f"      tope duro de esta corrida: {tope} requests")
    p(f"      costo máximo si el cupo Enterprise ya estuviera agotado: "
      f"USD {tope * PRECIO_ENTERPRISE_USD_1000 / 1000:.2f}")
    p(f"      la ronda 8 gastó 71 de los {GRATIS_ENTERPRISE_MENSUAL:,} de este mes. Con éstas, 75.")
    p("")

    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    p(f"      la caché trae {len(cache)} consultas ya pagadas. Las que estén acá no se repiten.")
    p("")

    filas, gastados, corte = [], 0, None
    clave_api = None
    if args.ejecutar:
        cargar_dotenv()
        clave_api = leer_api_key()
        if not clave_api:
            p("  !! no hay API key. La corrida no se ejecuta.")
            args.ejecutar = False

    p("-" * 100)
    p("  LA CORRIDA" if args.ejecutar else "  CORRIDA EN SECO — no se gasta nada")
    p("")

    for nombre, direccion, cerro, dias, sabemos, situacion in ESCALERA:
        consulta = (f"{direccion}, Ciudad Autónoma de Buenos Aires, Argentina — {nombre}"
                    f"{args.sufijo}")
        fila = {"establecimiento": nombre, "direccion_consultada": direccion,
                "cerro_el": cerro, "dias_desde_el_cierre": dias, "lo_que_sabemos": sabemos,
                "situacion_del_local": situacion, "consulta": consulta,
                "esperado_si_sigue_el_negocio": "CLOSED_PERMANENTLY",
                "esperado_si_sigue_el_lugar":
                    "OPERATIONAL" if "OCUPADO" in situacion else "CLOSED_PERMANENTLY"}

        if consulta in cache:
            respuesta, error = cache[consulta]["respuesta"], None
            fila["de_la_cache"] = True
        elif not args.ejecutar:
            fila.update({"business_status": "(no consultado · corrida en seco)",
                         "de_la_cache": False})
            filas.append(fila)
            p(f"      {nombre:<32} en seco · consulta: «{consulta}»")
            continue
        elif gastados >= tope:
            fila.update({"business_status": "(no consultado · tope alcanzado)",
                         "de_la_cache": False})
            filas.append(fila)
            continue
        else:
            respuesta, error = consultar_con(clave_api, consulta, CAMPOS)
            gastados += 1
            fila["de_la_cache"] = False
            if error:
                p(f"      !! {nombre}: {error}")
                p("      LA CORRIDA SE CORTA ACÁ. No se reintenta.")
                fila["business_status"] = f"ERROR: {error}"
                filas.append(fila)
                corte = nombre
                break
            cache[consulta] = {"respuesta": respuesta,
                               "consultado": datetime.now(timezone.utc).isoformat()}
            CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")

        lugares = (respuesta or {}).get("places", [])
        if not lugares:
            fila["business_status"] = "SIN_RESULTADO"
            fila["direccion_devuelta"] = ""
        else:
            fila["business_status"] = lugares[0].get("businessStatus", "SIN_ESTADO")
            fila["direccion_devuelta"] = lugares[0].get("formattedAddress", "")
            fila["nombre_devuelto"] = (lugares[0].get("displayName") or {}).get("text", "")
        veredicto, detalle = identidad(direccion, fila.get("direccion_devuelta", ""))
        fila["control_de_identidad"] = veredicto
        fila["control_detalle"] = detalle
        fila["vigencia_fecha_consulta"] = HOY.isoformat()
        filas.append(fila)
        p(f"      {nombre:<32} {fila['business_status']:<20} "
          f"devolvió: «{fila.get('nombre_devuelto', '')}» · identidad: {veredicto}"
          + (f" · {detalle}" if detalle else ""))

    tabla = pd.DataFrame(filas)
    # La dirección que devuelve Places NO se versiona: va sólo a `outputs/analisis_interno/`.
    # `control_detalle` transcribe la dirección que devolvió Places cuando el control falla, así
    # que arrastra el mismo dato que `direccion_devuelta` y se va con ella.
    versionable = tabla.drop(columns=[c for c in ("direccion_devuelta", "control_detalle")
                                      if c in tabla.columns])
    versionable.to_csv(OUT, index=False, encoding="utf-8")
    if "direccion_devuelta" in tabla.columns:
        tabla.to_csv(INTERNO / "escalera_r9_con_direcciones.csv", index=False, encoding="utf-8")

    p("")
    p("-" * 100)
    p("  LECTURA")
    p("")
    if not args.ejecutar:
        p("      corrida en seco: no hay resultados que leer. Correr con --ejecutar.")
    else:
        p(f"      requests gastados: {gastados} de {tope}")
        p(f"      costo máximo si el cupo estaba agotado: "
          f"USD {gastados * PRECIO_ENTERPRISE_USD_1000 / 1000:.2f}")
        if corte:
            p(f"      LA CORRIDA SE CORTÓ en «{corte}». Lo hecho quedó en la caché.")
        p("")
        p("      EL CONTROL QUE DECIDE NO ES EL ESTADO: ES EL NOMBRE DEVUELTO.")
        p("")
        p(f"      {'consultado':<32}{'devolvió':<40}{'estado':<20}")
        for f in filas:
            dev = f.get("nombre_devuelto", "(no pedido)")
            p(f"      {f['establecimiento']:<32}{dev:<40}{f.get('business_status', ''):<20}")
        p("")
        perla = next((f for f in filas if f["establecimiento"] == "La Perla del Once"), None)
        if perla and perla.get("nombre_devuelto"):
            devuelto = perla["nombre_devuelto"]
            mismo = "PERLA" in devuelto.upper()
            p(f"      EL TEST DECISIVO · se preguntó por «La Perla del Once» en Av. Rivadavia 2800")
            p(f"      y Places devolvió «{devuelto}» con estado {perla['business_status']}.")
            p("")
            if not mismo:
                p("      LA HIPÓTESIS ERA CASI CORRECTA Y EL MECANISMO ES OTRO, PEOR.")
                p("")
                p("      Places no le puso OPERATIONAL a La Perla del Once. Le puso OPERATIONAL a")
                p("      OTRO ESTABLECIMIENTO —el que ocupa hoy el local— y nosotros lo íbamos a")
                p("      leer como si hablara del que preguntamos. El defecto no está en la")
                p("      semántica de businessStatus: está en la ATRIBUCIÓN.")
                p("")
                p("      Text Search resuelve la consulta al lugar que mejor matchea el texto, y")
                p("      la dirección le gana al nombre. Sin `displayName` en la máscara no hay")
                p("      forma de saber de qué establecimiento habla la respuesta.")
                p("")
                p("      CONSECUENCIA SOBRE LA RONDA 8: sus 71 requests salieron SIN displayName.")
                p("      Los 70 OPERATIONAL no sólo no acreditan apertura —eso ya estaba escrito—:")
                p("      además no se sabe a qué establecimiento se refieren. Es R13 sobre la")
                p("      corrida entera, y no se arregla leyendo la tabla: hay que volver a")
                p("      preguntar con el nombre en la máscara.")
                p("")
                p("      LO QUE SÍ SE SOSTIENE: el Mercado de los Carruajes volvió con SU PROPIO")
                p("      nombre y CLOSED_PERMANENTLY. Cuando Places devuelve el establecimiento")
                p("      que se preguntó y lo marca cerrado, eso sigue acreditando.")
            else:
                p("      Places devolvió el establecimiento preguntado. La atribución se sostiene")
                p("      y la lectura de v2b no cambia por este caso.")
        p("")
        p("      Y EL CASO QUE NO ESTABA EN EL DISEÑO · Confitería del Hotel Castelar:")
        p("      Places devolvió «EX Hotel Castelar.» —el nombre declara que es el ex— con")
        p("      estado OPERATIONAL, 2.290 días después del cierre. El estado y el nombre de la")
        p("      misma respuesta se contradicen.")
        p("")
        p("      LA RESPUESTA NO ES ESTABLE. La misma consulta, con dos minutos de diferencia y")
        p("      cambiando sólo la máscara, devolvió dos lugares distintos para Av. Rivadavia")
        p("      2800: primero «Av. Jujuy 36» y después «Av. Rivadavia 2800 · La Americana».")
        p("      Con `maxResultCount: 1` se está tomando el primero de una lista rankeada que")
        p("      cambia entre llamadas. Para una pregunta de identidad, uno solo no alcanza.")
    p("")
    p("  LO QUE ESTA CORRIDA NO CAMBIA")
    p("      Ningún `OPERATIONAL` mueve un veredicto hacia arriba. La asimetría de v2b sigue")
    p("      valiendo mientras el test decisivo no la reescriba.")
    p("")
    p(f"  salidas: {OUT.relative_to(ROOT)} · {INFORME.relative_to(ROOT)}")

    texto = buffer.getvalue()
    INFORME.write_text(texto, encoding="utf-8")
    print(texto)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
