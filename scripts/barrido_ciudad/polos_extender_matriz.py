"""Extiende `matriz_validacion_polos_gastro.csv` sin romperla: filas nuevas y UNA columna nueva.

LO QUE ESTE SCRIPT TIENE PROHIBIDO HACER
------------------------------------------
La matriz es la curaduría, y es lo que sostiene el Atlas V2. El pedido fue explícito y acá está
convertido en condición verificada, no en buena intención:

  · **no cambiar el esquema, no renombrar columnas, no reordenar.** Las 22 columnas quedan como
    están y en el mismo orden; la nueva va **al final**.
  · **no tocar las 32 filas existentes.** Se comparan antes y después, columna por columna, y si
    alguna cambió el script **aborta sin escribir**. Es la única forma de que «no las toqué» sea
    una afirmación verificada y no un recuerdo.
  · **dejar vacías las columnas de fuentes documentales.** `cantidad_fuentes_*`, `hay_fuente_*`,
    `hay_delimitacion_explicita`, `hay_locales_mencionados` y `url_pendiente` las llena Diego
    desde afuera. Una fila nueva llega sin ninguna de ellas.

LA COLUMNA NUEVA, Y EL ÚNICO LUGAR DONDE SE APARTA DEL PEDIDO
---------------------------------------------------------------
`evidencia_relevamiento_propio` con valores `si` / `no`, y el detalle en el dossier de la Tarea 1.

Se aparta en **tres filas**, y se declara en vez de disimularlo: Barrio Chino, Bajo Belgrano y
Belgrano R son subzonas dentro de Belgrano, y la sonda del control trabaja a resolución de barrio,
así que devolvería «todo Belgrano» para las tres. Ahí no hay un `no` —sería afirmar que no hay
concentración— ni un `si` —sería atribuirle a la subzona la concentración del barrio—. Llevan
**`sin_resolucion`**. Poner `no` habría sido el valor cómodo y el equivocado.

Palermo Soho, Hollywood y Las Cañitas tienen la misma forma pero **sí** están resueltos, por
`DONDE_ESTA_SOHO.txt`, que los midió directo: van con `si`.

QUÉ ENTRA COMO FILA NUEVA, Y QUÉ NO SE LE PONE
------------------------------------------------
Los **62 candidatos del dossier**: los polos del borrador sin ninguna zona publicada encima. De
cada uno entra sólo lo medido. **No se le pone nombre, ni tipo_area, ni nivel de consolidación**,
y no es un olvido: nombrar y clasificar son decisiones de curaduría —§5 de `CRITERIOS_LECTURA`
lista «cómo se llaman» entre lo que el algoritmo NO decide— y llenarlas desde el clustering sería
exactamente confundir el generador de candidatos con la curaduría. `nombre_polo` lleva un
localizador —`P021 · Liniers`—, que ubica sin nombrar.

Cuando un candidato nuevo cae dentro del territorio declarado de una fila que YA está en la
matriz, queda anotado en `observaciones`: son la misma zona vista por dos instrumentos, y sumar
las dos sin verlo sería contar el lugar dos veces.

Google Places: 0 requests.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/polos_extender_matriz.py
  .venv/Scripts/python.exe scripts/barrido_ciudad/polos_extender_matriz.py --escribir
"""
from __future__ import annotations

import argparse
import io
import sys
import warnings
from pathlib import Path

import pandas as pd

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from polos_atributos_clases import OUT  # noqa: E402

MATRIZ = ROOT / "outputs" / "polos_gastro" / "matriz_validacion_polos_gastro.csv"
DOSSIER = OUT / "DOSSIER_MEDICION_CANDIDATOS.csv"
CONTROL = OUT / "control_matriz_v2.csv"

COLUMNA_NUEVA = "evidencia_relevamiento_propio"

# Las columnas que llena Diego desde afuera. Una fila nueva llega sin ninguna.
DOCUMENTALES = [
    "cantidad_fuentes_total", "cantidad_fuentes_alta", "cantidad_fuentes_media",
    "cantidad_fuentes_baja", "cantidad_fuentes_requiere_revision",
    "hay_fuente_oficial", "hay_fuente_periodistica", "hay_fuente_datos_abiertos",
    "hay_fuente_turistica", "hay_fuente_academica", "hay_delimitacion_explicita",
    "hay_locales_mencionados", "url_pendiente",
]
# Las que son decisión de curaduría y tampoco se rellenan desde el clustering.
DE_CURADURIA = [
    "tipo_area_revisado", "nivel_consolidacion_revisado",
    "estado_validacion", "decision_para_informe",
]

# Los tres que el control no puede resolver, con el motivo. Ver el docstring.
SIN_RESOLUCION_DECLARADA = {
    "PG006A_BARRIO_CHINO", "PG006B_BAJO_BELGRANO", "PG006C_BELGRANO_R",
}
# Los tres que tienen la misma forma pero sí están resueltos, por otra medición.
RESUELTOS_APARTE = {
    "PG001A_PALERMO_SOHO": "DONDE_ESTA_SOHO.txt: Soho es P091 (728 locales).",
    "PG001B_PALERMO_HOLLYWOOD": "DONDE_ESTA_SOHO.txt: Hollywood es P078 (585 locales).",
    "PG001C_LAS_CANITAS": "DONDE_ESTA_SOHO.txt: Cañitas está dentro de P065 (Báez 17/17).",
}


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser()
    parser.add_argument("--escribir", action="store_true",
                        help="escribe la matriz; sin esto sólo muestra qué haría")
    args = parser.parse_args()

    buffer = io.StringIO()

    def p(*args_):
        print(*args_, file=buffer)

    # `utf-8-sig` en las dos puntas: el archivo trae BOM y sacárselo sería cambiarlo.
    matriz = pd.read_csv(MATRIZ, encoding="utf-8-sig", dtype=str, keep_default_na=False)
    original = matriz.copy()
    dossier = pd.read_csv(DOSSIER)
    control = pd.read_csv(CONTROL).set_index("polo_id")

    p("EXTENSIÓN DE LA MATRIZ DE VALIDACIÓN · filas nuevas y una columna, sin tocar lo que había")
    p("=" * 100)
    p("")
    p(f"  matriz actual: {len(matriz)} filas × {len(matriz.columns)} columnas")
    p(f"  candidatos del dossier a agregar: {len(dossier)}")
    p("")

    if COLUMNA_NUEVA in matriz.columns:
        p(f"  La columna `{COLUMNA_NUEVA}` ya existe: se recalcula su contenido, no se duplica.")
        p("")

    # ------------------------------------------------------------------ 1 · la columna nueva
    valores = []
    for fila in matriz.itertuples():
        if fila.polo_id in RESUELTOS_APARTE:
            valores.append("si")
        elif fila.polo_id in SIN_RESOLUCION_DECLARADA:
            valores.append("sin_resolucion")
        else:
            valores.append(control.loc[fila.polo_id, "aparece_en_relevamiento"]
                           if fila.polo_id in control.index else "")
    matriz[COLUMNA_NUEVA] = valores

    p("-" * 100)
    p("  1 · LA COLUMNA NUEVA sobre las 32 filas que ya estaban")
    p("")
    for valor, n in pd.Series(valores).value_counts().items():
        p(f"      {valor:<16} {n:>3}")
    p("")
    p("      Los `sin_resolucion` son 3 y están declarados: Barrio Chino, Bajo Belgrano y")
    p("      Belgrano R son subzonas de Belgrano y la sonda trabaja a resolución de barrio.")
    p("")

    # ------------------------------------------------------------------ 2 · las filas nuevas
    # Territorio de cada candidato de la matriz, para avisar cuándo se superponen.
    territorios = {}
    for fila in control.itertuples():
        barrios = {b.strip() for b in str(fila.territorio_barrios).split(";") if b.strip()}
        if barrios and "—" not in barrios:
            territorios[fila.Index] = barrios

    nuevas = []
    for fila in dossier.itertuples():
        barrio = str(fila.barrio_principal).upper()
        solapa = sorted(k for k, v in territorios.items() if barrio in v)
        calles = fila.calles_dominantes if isinstance(fila.calles_dominantes, str) else ""
        observacion = (
            f"Candidato del relevamiento propio, sin zona publicada encima. "
            f"{fila.n_locales} locales · {fila.ha} ha · {fila.locales_x_ha} loc/ha "
            f"({fila.clase_densidad}) · barrios: {fila.barrios} · comuna(s) {fila.comunas} · "
            f"calles sobre el {fila.pct_locales_con_direccion} % con dirección: "
            f"{calles or 'sin calles dominantes'} · {fila.n_hitos_adentro} hito(s) adentro · "
            f"a {fila.d_a_zona_publicada_m:.0f} m de la zona publicada más cercana, entre puntos. "
            f"Detalle en DOSSIER_MEDICION_CANDIDATOS.csv."
        )
        if solapa:
            observacion += (f" SUPERPONE territorio declarado de: {', '.join(solapa)} — "
                            f"revisar antes de contarlos como candidatos distintos.")
        registro = {c: "" for c in matriz.columns}
        registro["polo_id"] = f"PGR_{fila.polo_id}"
        # Localizador, NO nombre: nombrar es decisión de curaduría (§5 de CRITERIOS_LECTURA).
        registro["nombre_polo"] = f"{fila.polo_id} · {fila.barrio_principal}"
        registro["tipo_area_fase1"] = "no_aplica_fase1"
        registro["nivel_consolidacion_fase1"] = "no_aplica_fase1"
        registro[COLUMNA_NUEVA] = "si"
        registro["observaciones"] = observacion
        nuevas.append(registro)

    nuevas_df = pd.DataFrame(nuevas, columns=matriz.columns)
    p("-" * 100)
    p("  2 · LAS FILAS NUEVAS")
    p("")
    p(f"      {len(nuevas_df)} filas. Todas con `{COLUMNA_NUEVA}` = si, por construcción: entran")
    p("      justamente porque hay concentración medida.")
    p("")
    p(f"      vacías por pedido — las llena Diego: {', '.join(DOCUMENTALES)}")
    p(f"      vacías por criterio — son curaduría: {', '.join(DE_CURADURIA)}")
    p("")
    con_solape = sum(1 for r in nuevas if "SUPERPONE" in r["observaciones"])
    p(f"      {con_solape} de {len(nuevas_df)} caen en el territorio declarado de una fila que ya")
    p("      estaba. Quedan anotadas, no fusionadas: fusionarlas es decisión de curaduría.")
    p("")

    # ------------------------------------------------------------------ 3 · la verificación
    final = pd.concat([matriz, nuevas_df], ignore_index=True)

    p("-" * 100)
    p("  3 · VERIFICACIÓN · que las 32 filas de antes estén intactas")
    p("")
    cambios = []
    for columna in original.columns:
        antes = original[columna].tolist()
        despues = final[columna].head(len(original)).tolist()
        if antes != despues:
            cambios.append(columna)
    orden_ok = list(final.columns[:len(original.columns)]) == list(original.columns)
    p(f"      columnas originales en el mismo orden: {'SÍ' if orden_ok else 'NO'}")
    p(f"      columna nueva al final: {'SÍ' if final.columns[-1] == COLUMNA_NUEVA else 'NO'}")
    p(f"      celdas cambiadas en las 32 filas originales: "
      f"{'ninguna' if not cambios else 'EN ' + ', '.join(cambios)}")
    p("")

    if cambios or not orden_ok:
        p("  ABORTA: algo de lo que estaba cambió. No se escribe nada.")
        print(buffer.getvalue())
        return 1

    if args.escribir:
        final.to_csv(MATRIZ, index=False, encoding="utf-8-sig")
        p(f"  ESCRITA: {MATRIZ.relative_to(ROOT)} — {len(final)} filas × {len(final.columns)} columnas")
    else:
        p("  ENSAYO: no se escribió nada. Correr con --escribir para aplicarlo.")
    p("")

    p("=" * 100)
    p(f"  {len(original)} filas intactas + {len(nuevas_df)} nuevas = {len(final)} · "
      f"{len(original.columns)} columnas + 1 = {len(final.columns)} · Google Places: 0 requests")
    p("=" * 100)
    p("")

    salida = buffer.getvalue()
    (OUT / "EXTENSION_MATRIZ.txt").write_text(salida, encoding="utf-8")
    print(salida)
    return 0


if __name__ == "__main__":
    sys.exit(main())
