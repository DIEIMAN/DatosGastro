"""Diccionario de columnas de los CSV del barrido, con el aviso de `habilitaciones` incluido.

Un CSV no admite nota al pie. La advertencia de que **la columna `habilitaciones` no es un
indicador de volumen** vive en el informe y en el tablero, pero cualquiera que reciba un CSV suelto
se la pierde. Este archivo es la pieza que viaja con los CSV.

El script recorre los CSV entregables del barrido, detecta cuáles traen la columna y arma el
diccionario. Si aparece un CSV nuevo con `habilitaciones`, entra solo: el aviso no se puede
desactualizar por olvido.

Uso:
  python scripts/barrido_ciudad/documentar_columnas.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
BARRIDO = ROOT / "outputs" / "BARRIDO_CIUDAD_2026-08"
DESTINO = BARRIDO / "DICCIONARIO_COLUMNAS.md"

COLUMNA_AVISADA = "habilitaciones"

GLOSARIO = {
    "dir_nucleo": "Direcciones distintas con al menos una habilitación gastronómica del anillo "
                  "núcleo entre 2015 y 2025. **Es la unidad de conteo del trabajo.**",
    "dir_ampliado": "Ídem, sumando el anillo ampliado (panadería, pastelería, confitería).",
    "dir_outlier": "Direcciones con más de 20 trámites, excluidas del conteo por la regla 3 del "
                   "método. Centros comerciales, complejos y cargas masivas del padrón.",
    "habilitaciones": "**Cantidad de trámites de habilitación, no de locales.** Ver el aviso de "
                      "arriba antes de usarla.",
    "f01_locales": "Establecimientos de la oferta registrada en F01. Universo distinto y mucho "
                   "más chico: no es un censo.",
    "rus_nucleo": "Parcelas con uso gastronómico del anillo núcleo según el Relevamiento de Usos "
                  "del Suelo, en la añada declarada para ese barrio.",
    "rus_ampliado": "Ídem, con el anillo ampliado.",
    "rus_inactivo": "Parcelas gastronómicas que el Relevamiento encontró inactivas.",
    "anio_relevamiento": "Año en que el Relevamiento pasó por ese barrio. El operativo es "
                         "rotativo: no todos los barrios tienen la misma añada.",
    "lotes_detectados": "Conjuntos de permisos replicados detectados en el barrio.",
    "direcciones_en_lotes": "Direcciones involucradas en esos conjuntos.",
    "habilitaciones_en_lotes": "Trámites involucrados. Contra `habilitaciones` da la proporción "
                               "del volumen de trámite del barrio que es repetición.",
    "partidas_matriz": "Partidas matriz distintas asociadas a la dirección en el crudo 2025.",
    "direcciones_con_esa_partida": "Cuántas direcciones del padrón cuelgan de la misma partida. "
                                   "Más de una = el mismo inmueble cargado en varias puertas.",
    "smp": "Clave catastral sección-manzana-parcela.",
}

AVISO = """> ## Aviso sobre la columna `habilitaciones`
>
> **No es un indicador de volumen de oferta.** Cuenta trámites de habilitación, no locales.
>
> En 45 conjuntos de direcciones —137 direcciones, 9.697 trámites, el **22,6 % del padrón
> georreferenciado**— un mismo permiso figura repetido contra cada puerta del frente de manzana
> de un inmueble. El mecanismo está en el propio padrón: el campo `calles` asienta el frente
> entero del inmueble en un solo registro (13,9 % de los registros crudos traen más de un número
> de puerta), y la exportación de 2025 lo aplana a un domicilio por fila. El catastro lo
> corrobora: las 37 partidas matriz involucradas resuelven **todas a una única parcela**.
>
> El caso más engañoso de la Ciudad es **Liniers**: el 77 % de sus trámites viene de tres
> conjuntos replicados. Un lector que ordene barrios por esta columna lo pondría entre los más
> densos de la Ciudad, y no lo es.
>
> **Las columnas de direcciones (`dir_nucleo`, `dir_ampliado`) no están afectadas:** la regla 3
> del método deja estas direcciones fuera del conteo desde el principio. Ninguna cifra publicada
> depende de `habilitaciones`.
>
> La columna se publica igual porque mide algo que sí importa —carga de trámite sobre el
> territorio— pero se lee como eso y no como oferta."""


def csvs_del_barrido() -> list[Path]:
    return sorted(BARRIDO.glob("*.csv")) + sorted((BARRIDO / "generado").glob("*.csv"))


def main() -> int:
    lineas = ["# Diccionario de columnas · Barrido de la Ciudad",
              "",
              "Acompaña a los CSV de esta carpeta. Si un CSV se entrega suelto, este archivo va con él.",
              "", AVISO, "", "---", "", "## Qué CSV traen la columna avisada", ""]

    con_aviso, sin_aviso = [], []
    columnas_vistas: set[str] = set()
    for ruta in csvs_del_barrido():
        try:
            encabezado = pd.read_csv(ruta, nrows=0, encoding="utf-8-sig")
        except Exception:  # noqa: BLE001
            continue
        columnas = set(encabezado.columns)
        columnas_vistas |= columnas
        destino = con_aviso if COLUMNA_AVISADA in columnas else sin_aviso
        destino.append(ruta.relative_to(BARRIDO).as_posix())

    for ruta in con_aviso:
        lineas.append(f"- `{ruta}` — **trae `{COLUMNA_AVISADA}`**")
    lineas += ["", f"Otros {len(sin_aviso)} CSV de la carpeta no la traen.", "",
               "---", "", "## Glosario", ""]
    for columna in sorted(columnas_vistas & set(GLOSARIO)):
        lineas.append(f"- **`{columna}`** — {GLOSARIO[columna]}")

    lineas += ["", "---", "",
               "**Fuentes:** habilitaciones aprobadas y oferta gastronómica de BA Data "
               "(F01, F02, cohortes 2015-2025); Relevamiento de Usos del Suelo, GCBA. "
               "La prueba catastral está en `generado/PRUEBA_SMP_LOTES.txt`."]

    DESTINO.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print(f"{len(con_aviso)} CSV traen `{COLUMNA_AVISADA}`:")
    for ruta in con_aviso:
        print(f"  {ruta}")
    print(f"\nescrito: {DESTINO}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
