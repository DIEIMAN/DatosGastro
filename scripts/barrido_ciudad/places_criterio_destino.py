"""Criterio de destino para Places y dry-run. NO EJECUTA NINGUNA LLAMADA. 0 requests.

QUÉ CAMBIÓ Y POR QUÉ HACE FALTA UN CRITERIO NUEVO
--------------------------------------------------
El destino de Places iba a decidirse contra un denominador externo de completitud. Ese pedido no
va: no habrá INDEC, ni APRA, ni AGIP, ni Estadística y Censos. **Nunca vamos a tener denominador
externo**, y eso pasa de pendiente a limitación declarada.

Lo que queda es lo interno: los dos proxies de parejidad y el solapamiento con el padrón. Y hay
una lectura de eso que convierte la restricción en un uso concreto —la mejor disponible—:

  **Places pasa a ser el sustituto interno del denominador externo que no va a llegar.**

No como fuente del mapa —no está en la base, su licencia no es redistribuible y eso no cambia—,
sino como **sonda de descubrimiento**: se corre donde la base está más flaca y se mide cuánto
aparece que no teníamos. Si aun ahí aparece poco, la cobertura queda acotada por arriba con un
número propio. Si aparece mucho, sabemos dónde y cuánto falta. Las dos respuestas sirven; hoy no
tenemos ninguna.

Y lo que este barrido NO puede hacer, porque ya está medido y no se relitiga: **Places aporta
descubrimiento, no vigencia.** La mediana de lo que trae no está en el padrón (62,5 %) y sólo
confirma el 11 % del padrón. Ningún resultado de esta corrida se puede leer como validación de
que un local siga abierto.

EL CRITERIO, DECLARADO ANTES DE MIRAR QUÉ BARRIOS SALEN
--------------------------------------------------------
Dos indicadores internos, los dos ya calculados y ninguno dependiente de terceros:

  1. `aporte_otras_fuentes` — cuánto agregan las otras seis fuentes por encima del piso del
     Relevamiento. Bajo = ahí las demás fuentes vieron poco y la base descansa casi sola sobre el
     censo caminado.
  2. `pct_padron` — qué fracción de los locales del barrio tiene respaldo de F01/F02, el padrón de
     la AGC. Bajo = poco respaldo administrativo independiente.

**Selección: los barrios que están en el tercio más bajo de LOS DOS.** Intersección y no unión, y
el motivo es que un barrio flojo en un solo indicador puede ser una rareza de esa fuente; flojo en
los dos significa que la base ahí se apoya en menos patas independientes. La intersección también
mantiene el barrido chico, que es lo que corresponde a una sonda.

Se declara antes de correr, además, el tope: la corrida tiene que caber en la franja gratuita del
mes con margen, así que no se propone nada que pase de `TOPE_REQUESTS`.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/places_criterio_destino.py
"""
from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

import pandas as pd

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from borrador_polos_ciudad import BARRIDO, plegar  # noqa: E402

GEN = BARRIDO / "generado"
BASE = BARRIDO / "base" / "local.csv"
OUT = BARRIDO / "places_criterio_destino"

# --- lo declarado antes de mirar resultados -----------------------------------------------------
TERCIO = 1 / 3          # «tercio más bajo» de cada indicador
FRANJA_GRATUITA = 5_000  # Text Search, SKU Pro, por mes
YA_USADOS_AGOSTO = 306
TOPE_REQUESTS = 600      # tope propio, muy por debajo de la franja: es una sonda, no un barrido


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    OUT.mkdir(parents=True, exist_ok=True)
    lineas = []

    def p(*args_):
        lineas.append(" ".join(str(a) for a in args_))

    parejidad = pd.read_csv(GEN / "parejidad_a_parcelas_comerciales.csv", index_col=0)
    parejidad.index = [plegar(i) for i in parejidad.index]
    estimacion = pd.read_csv(GEN / "estimacion_places_48_barrios.csv")
    estimacion["barrio_k"] = estimacion.barrio.map(plegar)

    # El solapamiento con el padrón se calcula desde la base, no se toma de ninguna tabla vieja:
    # es la fracción de locales del barrio que tiene respaldo de F01 o F02.
    base = pd.read_csv(BASE, low_memory=False)
    base = base[base.anillo == "nucleo"]
    base["barrio_k"] = base.barrio.map(plegar)
    base["en_padron"] = base.fuentes.fillna("").str.contains("F01|F02", regex=True)
    padron = base.groupby("barrio_k").en_padron.agg(["mean", "size"])
    padron.columns = ["pct_padron", "locales_nucleo"]
    padron["pct_padron"] *= 100

    tabla = parejidad[["aporte_otras_fuentes", "cobertura", "rus_gastro",
                       "anio_relevamiento"]].join(padron, how="inner")
    tabla = tabla.join(estimacion.set_index("barrio_k")[["requests", "celdas", "univ_est"]])

    corte_aporte = tabla.aporte_otras_fuentes.quantile(TERCIO)
    corte_padron = tabla.pct_padron.quantile(TERCIO)
    tabla["flojo_aporte"] = tabla.aporte_otras_fuentes <= corte_aporte
    tabla["flojo_padron"] = tabla.pct_padron <= corte_padron
    tabla["seleccionado"] = tabla.flojo_aporte & tabla.flojo_padron

    p("CRITERIO DE DESTINO PARA GOOGLE PLACES · dry-run")
    p("=" * 100)
    p("")
    p("NINGUNA LLAMADA EJECUTADA. 0 requests. Esto es un pedido de autorización, no una corrida.")
    p("")
    p("EL CAMBIO DE MARCO, PORQUE CAMBIA PARA QUÉ SIRVE ESTA CORRIDA")
    p("  El destino iba a decidirse contra un denominador externo de completitud. Ese pedido no va,")
    p("  y no va a haber otro: **nunca vamos a tener denominador externo.** Eso deja de ser un")
    p("  pendiente y pasa a ser limitación declarada del §10.")
    p("")
    p("  La propuesta es usar Places para ocupar ese lugar, con lo que Places sí sabe hacer:")
    p("  **sonda de descubrimiento en los barrios donde la base está más flaca.** Si aun ahí")
    p("  aparece poco que no teníamos, la cobertura queda acotada por arriba con un número propio.")
    p("  Si aparece mucho, sabemos dónde y cuánto falta. Hoy no tenemos ninguna de las dos.")
    p("")
    p("  Y el límite que no se relitiga: **Places aporta descubrimiento, NO vigencia.** Nada de")
    p("  esta corrida se puede leer como que un local sigue abierto.")
    p("")
    p("EL CRITERIO, DECLARADO ANTES DE MIRAR QUÉ BARRIOS SALEN")
    p(f"  1 · `aporte_otras_fuentes` en el tercio más bajo (≤ {corte_aporte:.2f})")
    p(f"  2 · `pct_padron` en el tercio más bajo (≤ {corte_padron:.1f} %)")
    p("  Selección = intersección de los dos, no unión. Flojo en un solo indicador puede ser una")
    p("  rareza de esa fuente; flojo en los dos significa menos patas independientes.")
    p("")

    elegidos = tabla[tabla.seleccionado].sort_values("requests", ascending=False)
    p(f"  barrios en el tercio bajo de aporte: {int(tabla.flojo_aporte.sum())}")
    p(f"  barrios en el tercio bajo de padrón: {int(tabla.flojo_padron.sum())}")
    p(f"  **en los dos (seleccionados): {len(elegidos)}**")
    p("")
    p(elegidos[["aporte_otras_fuentes", "pct_padron", "cobertura", "locales_nucleo",
                "rus_gastro", "anio_relevamiento", "celdas", "requests"]].round(2).to_string())
    p("")

    total = int(elegidos.requests.sum())
    p("DRY-RUN · el número que hace falta para autorizar")
    p("=" * 100)
    p("")
    p(f"  barrios         : {len(elegidos)}")
    p(f"  celdas          : {int(elegidos.celdas.sum())}")
    p(f"  **requests      : {total}**  (estimados página por página, no ×3)")
    p(f"  cota superior ×3: {total * 3} si toda celda paginara al máximo")
    p("")
    p(f"  franja gratuita mensual   : {FRANJA_GRATUITA:,} (Text Search, SKU Pro)")
    p(f"  ya usados en agosto       : {YA_USADOS_AGOSTO}")
    p(f"  quedarían usados con esto : {YA_USADOS_AGOSTO + total} "
      f"({(YA_USADOS_AGOSTO + total) / FRANJA_GRATUITA * 100:.1f} % de la franja)")
    p(f"  en el peor caso ×3        : {YA_USADOS_AGOSTO + total * 3} "
      f"({(YA_USADOS_AGOSTO + total * 3) / FRANJA_GRATUITA * 100:.1f} %)")
    p(f"  tope propio declarado     : {TOPE_REQUESTS} requests")
    if total <= TOPE_REQUESTS:
        p(f"  CABE · {total} ≤ {TOPE_REQUESTS}, y el peor caso ×3 sigue adentro de la franja gratuita.")
    else:
        p(f"  NO CABE en el tope propio ({total} > {TOPE_REQUESTS}). Hay que recortar la selección")
        p("  antes de pedir autorización: primero los barrios de menor `requests`, para maximizar")
        p("  barrios cubiertos por request gastado.")
    p("")
    p("QUÉ SE MEDIRÍA, ESCRITO ANTES DE CORRER PARA QUE EL RESULTADO SEA FALSABLE")
    p("  Por barrio: cuántos puntos trae Places, cuántos ya están en la base, y cuántos son")
    p("  nuevos. El indicador que importa es **la fracción nueva**, y las dos lecturas están")
    p("  escritas de antemano:")
    p("    · fracción nueva BAJA en los barrios más flacos → la base está más completa de lo que")
    p("      podíamos afirmar, y la afirmación pasa a tener respaldo propio.")
    p("    · fracción nueva ALTA → hay faltante y queda localizado, con su tamaño.")
    p("  Ninguna de las dos se puede anticipar y las dos son publicables. Eso es lo que hace que")
    p("  valga la pena correrla.")
    p("")
    p("LO QUE NO SE HACE CON EL RESULTADO, sin una decisión aparte")
    p("  No entra a la base: la licencia de Places no es redistribuible y por eso la base se")
    p("  construyó sin él. El producto de esta corrida es un número de diagnóstico, no puntos.")
    p("")
    p("PEDIDO DE AUTORIZACIÓN")
    p(f"  Se solicita autorización para ejecutar {total} requests de Text Search sobre "
      f"{len(elegidos)} barrios.")
    p("  Sin autorización explícita no se ejecuta nada.")
    p("")

    salida = "\n".join(lineas)
    (OUT / "CRITERIO_DESTINO_PLACES.txt").write_text(salida, encoding="utf-8")
    tabla.round(3).to_csv(OUT / "indicadores_por_barrio.csv", encoding="utf-8")
    elegidos.round(3).to_csv(OUT / "barrios_seleccionados.csv", encoding="utf-8")
    (OUT / "dry_run.json").write_text(json.dumps({
        "barrios": len(elegidos), "celdas": int(elegidos.celdas.sum()), "requests": total,
        "cota_superior_x3": total * 3, "franja_gratuita": FRANJA_GRATUITA,
        "ya_usados_agosto": YA_USADOS_AGOSTO, "tope_propio": TOPE_REQUESTS,
        "cabe_en_el_tope": bool(total <= TOPE_REQUESTS),
        "estado": "PENDIENTE_DE_AUTORIZACION", "ejecutado": False, "requests_ejecutados": 0,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(salida)
    print(f"escrito en {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
