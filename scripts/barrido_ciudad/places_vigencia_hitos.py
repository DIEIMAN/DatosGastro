"""Decisión 4 · la pasada de Places sobre los hitos, con la puerta de precio cerrada por defecto.

QUÉ ES ESTO
-----------
Diego autorizó el gasto de Places sobre los hitos de la capa (decisión 4 del 07/08/2026), con una
condición explícita: **confirmar el precio contra la consola ANTES de gastar.**

Este archivo deja la pasada lista para correr y **no la corre**. En seco imprime el plan exacto
—cuántas consultas, con qué campos, sobre qué hitos— y no toca la red. Para gastar hacen falta
las dos banderas juntas:

    --precio-confirmado <USD por 1.000 consultas>   el número que Diego lea en SU consola
    --ejecutar                                       la confirmación de que se quiere gastar

Sin las dos, el guion sale sin haber hecho una sola llamada. No es una precaución decorativa: la
estimación que circula (USD 3,74–7,04) sale de una tarifa que el propio repositorio dejó anotada
como **no confirmada**, y la consola de facturación es de Diego, no de este proceso.

LOS CAMPOS, Y POR QUÉ ESOS Y NO MÁS
------------------------------------
La decisión fija el mínimo: `business_status`, `formatted_address`, `opening_hours`. Se pide eso
y nada más. Cada campo extra sube de SKU y no aporta al veredicto de vigencia, que es lo único
que esta pasada viene a resolver.

LA FECHA DE CONSULTA SE REGISTRA SIEMPRE
-----------------------------------------
Places **no trae la fecha del dato**: devuelve un estado sin decir de cuándo es. Sin la fecha de
consulta, un `OPERATIONAL` de hoy y uno de hace ocho meses se leen igual, que es exactamente el
defecto FD-01 que ya está catalogado. Por eso `vigencia_fecha_consulta` se escribe en cada fila y
no es opcional.

LA ASIMETRÍA, QUE ES LO QUE HACE UTILIZABLE EL RESULTADO
---------------------------------------------------------
    CLOSED_PERMANENTLY   acredita CERRADO con fuerza. Un comercio no se marca cerrado solo.
    CLOSED_TEMPORARILY   señal fuerte de interrupción; no es cierre definitivo.
    OPERATIONAL          NO acredita abierto. Dice que nadie reportó lo contrario, que es otra
                         cosa. Places es lento con el cierre reciente: Los Laureles cerró en
                         julio y casi seguro sigue figurando operativo.

Por eso el nivel que otorga es **v2b** y sólo hacia el lado del cierre. Un `OPERATIONAL` no sube
a nadie a `verificado_abierto`; deja el estado donde estaba y se anota como consulta hecha.

USO
---
  # el plan, sin gastar nada (lo que hace por defecto)
  .venv/Scripts/python.exe scripts/barrido_ciudad/places_vigencia_hitos.py

  # gastar, una vez que el precio esté confirmado en la consola
  .venv/Scripts/python.exe scripts/barrido_ciudad/places_vigencia_hitos.py \
      --precio-confirmado 32.00 --ejecutar
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from datetime import date
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from polos_soporte import BARRIDO  # noqa: E402

HITOS = BARRIDO / "hitos"
CAPA = HITOS / "hitos_capa_2026_r7.csv"
PLAN_CSV = HITOS / "places_plan_consulta.csv"
RESULTADO_CSV = HITOS / "places_resultado_vigencia.csv"
CACHE = HITOS / "_cache_places_vigencia.json"
INFORME = HITOS / "PLACES_VIGENCIA.txt"

# Los tres que fija la decisión 4, y ninguno más.
CAMPOS = ["places.businessStatus", "places.formattedAddress", "places.regularOpeningHours"]
ENDPOINT = "https://places.googleapis.com/v1/places:searchText"

# Lo que Places puede decir, y lo que cada cosa acredita.
LECTURA = {
    "CLOSED_PERMANENTLY": ("no", "v2b", "acredita CERRADO con fuerza: un comercio no se marca "
                                        "cerrado permanentemente solo"),
    "CLOSED_TEMPORARILY": ("dudosa", "v2b", "interrupción declarada; no es cierre definitivo"),
    "OPERATIONAL": ("", "", "NO acredita abierto: dice que nadie reportó lo contrario. No mueve "
                            "el estado; se registra la consulta y la fecha"),
}


def hitos_a_consultar() -> pd.DataFrame:
    capa = pd.read_csv(CAPA)
    # Se consultan los que tienen dirección: sin dirección no hay qué buscar. No se filtra por
    # estado: el objetivo declarado es cubrir de una sola pasada los hitos de las 22 publicadas,
    # que son justamente los que no tienen ninguna verificación individual.
    con_direccion = capa[capa.direccion.notna() & (capa.direccion.astype(str).str.strip() != "")]
    return con_direccion[["hito_id", "nombre", "direccion", "barrio_declarado",
                          "registro_oficial", "vigencia_verificada", "vigencia_nivel"]].copy()


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--precio-confirmado", type=float, default=None,
                        help="USD por 1.000 consultas, leído en la consola de facturación")
    parser.add_argument("--ejecutar", action="store_true",
                        help="confirma que se quiere gastar. Sin esto, corrida en seco")
    args = parser.parse_args()

    if not CAPA.exists():
        raise SystemExit("falta hitos_capa_2026_r7.csv — correr ronda_7_hitos_y_decisiones.py")

    plan = hitos_a_consultar()
    plan["consulta"] = plan.nombre.astype(str) + ", " + plan.direccion.astype(str) + \
        ", Ciudad Autónoma de Buenos Aires, Argentina"
    plan.to_csv(PLAN_CSV, index=False, encoding="utf-8")

    lineas = []
    lineas.append("DECISIÓN 4 · LA PASADA DE PLACES SOBRE LOS HITOS")
    lineas.append("=" * 100)
    lineas.append("")
    lineas.append(f"  hitos en la capa con dirección utilizable: {len(plan)}")
    lineas.append(f"  campos pedidos: {', '.join(CAMPOS)}")
    lineas.append(f"  nivel que otorga: v2b, y sólo hacia el lado del cierre")
    lineas.append(f"  plan escrito en: {PLAN_CSV.name}")
    lineas.append("")
    lineas.append("  reparto por estado actual de vigencia:")
    for valor, n in plan.vigencia_verificada.value_counts().items():
        lineas.append(f"      {valor:<36} {n:>4}")
    lineas.append("")

    if not (args.ejecutar and args.precio_confirmado is not None):
        lineas.append("-" * 100)
        lineas.append("  CORRIDA EN SECO · 0 requests · 0 gasto")
        lineas.append("")
        lineas.append("  Falta la condición que puso la decisión 4: el precio confirmado contra")
        lineas.append("  la consola. Este proceso NO puede leer la consola de facturación de")
        lineas.append("  Diego, y la tarifa que circula en la estimación está anotada como no")
        lineas.append("  confirmada en el propio repositorio (`estimar_costo_places.py`, línea 17).")
        lineas.append("")
        lineas.append("  Para correrla, con el número que diga la consola:")
        lineas.append("")
        lineas.append("      .venv/Scripts/python.exe scripts/barrido_ciudad/"
                      "places_vigencia_hitos.py \\")
        lineas.append("          --precio-confirmado <USD_por_1000> --ejecutar")
        lineas.append("")
        lineas.append("  Y hace falta la clave en el entorno: GOOGLE_MAPS_API_KEY.")
        lineas.append("  No se guarda ninguna credencial en el repositorio.")
        texto = "\n".join(lineas)
        INFORME.write_text(texto, encoding="utf-8")
        print(texto)
        return 0

    clave = os.environ.get("GOOGLE_MAPS_API_KEY", "").strip()
    if not clave:
        raise SystemExit("falta GOOGLE_MAPS_API_KEY en el entorno. No se guardan credenciales "
                         "en el repositorio.")

    import requests  # se importa acá a propósito: la corrida en seco no necesita red

    costo = len(plan) * args.precio_confirmado / 1000
    lineas.append("-" * 100)
    lineas.append(f"  EJECUTANDO · {len(plan)} consultas · precio confirmado "
                  f"USD {args.precio_confirmado:.2f} por 1.000 · costo estimado USD {costo:.2f}")
    lineas.append("")

    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    hoy = date.today().isoformat()
    resultados, hechas = [], 0
    for fila in plan.itertuples():
        consulta = fila.consulta
        if consulta not in cache:
            respuesta = requests.post(
                ENDPOINT,
                headers={"Content-Type": "application/json", "X-Goog-Api-Key": clave,
                         "X-Goog-FieldMask": ",".join(CAMPOS)},
                json={"textQuery": consulta, "maxResultCount": 1,
                      "languageCode": "es", "regionCode": "AR"},
                timeout=30)
            respuesta.raise_for_status()
            cache[consulta] = {"respuesta": respuesta.json(), "fecha_consulta": hoy}
            hechas += 1
            time.sleep(0.2)
        guardado = cache[consulta]
        lugares = (guardado["respuesta"] or {}).get("places") or []
        estado = lugares[0].get("businessStatus", "") if lugares else "SIN_RESULTADO"
        nuevo_estado, nivel, lectura = LECTURA.get(estado, ("", "", "sin lectura definida"))
        resultados.append({
            "hito_id": fila.hito_id, "nombre": fila.nombre, "direccion": fila.direccion,
            "business_status": estado,
            "formatted_address": lugares[0].get("formattedAddress", "") if lugares else "",
            "opening_hours": json.dumps(
                lugares[0].get("regularOpeningHours", {}), ensure_ascii=False) if lugares else "",
            # Places NO trae la fecha del dato. Sin esta columna el resultado es infechable.
            "vigencia_fecha_consulta": guardado["fecha_consulta"],
            "estado_que_acredita": nuevo_estado, "nivel": nivel, "lectura": lectura,
            "estado_previo_en_la_capa": fila.vigencia_verificada,
        })

    CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    pd.DataFrame(resultados).to_csv(RESULTADO_CSV, index=False, encoding="utf-8")

    conteo = pd.Series([r["business_status"] for r in resultados]).value_counts()
    for valor, n in conteo.items():
        lineas.append(f"      {valor:<24} {n:>4}")
    lineas.append("")
    lineas.append(f"  consultas nuevas (no cacheadas): {hechas}")
    lineas.append(f"  resultado en: {RESULTADO_CSV.name}")
    lineas.append("")
    lineas.append("  EL RESULTADO NO SE APLICA SOLO A LA CAPA. Los CLOSED_PERMANENTLY se revisan")
    lineas.append("  uno por uno antes de escribirlos: un cierre es la afirmación más cara de")
    lineas.append("  equivocar, y FD-12 ya probó que una marca de cierre puede ser falsa.")
    texto = "\n".join(lineas)
    INFORME.write_text(texto, encoding="utf-8")
    print(texto)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
