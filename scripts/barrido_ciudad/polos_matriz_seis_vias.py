"""Las columnas medibles de las seis vías, incorporadas a la matriz, sin tocar nada de lo viejo.

QUÉ ESCRIBE Y QUÉ NO
--------------------
Agrega al final de `matriz_validacion_polos_gastro.csv` las columnas que `polos_seis_vias.py`
midió. **Las 23 columnas que ya estaban quedan en el mismo orden y con el mismo contenido**: el
script las compara celda por celda antes de escribir y **aborta** si alguna cambió. Es la misma
verificación con la que se extendió la matriz de 32 a 94 filas.

`via_E_reconocimiento` entra **vacía**, y esa es la forma correcta de que entre: la llena Diego
desde afuera, y una columna que no está no se puede llenar.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/polos_matriz_seis_vias.py
"""
from __future__ import annotations

import io
import sys
import warnings
from pathlib import Path

import pandas as pd

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from polos_soporte import BARRIDO, MATRIZ  # noqa: E402

OUT = BARRIDO / "seis_vias"

COLUMNAS_NUEVAS = [
    ("soporte_clase", "soporte_clase"),
    ("soporte_detalle", "soporte_detalle"),
    ("via_A_n_locales", "n_locales"),
    ("via_A_ha", "ha"),
    ("via_A_locales_x_ha", "locales_x_ha"),
    ("via_A_continuidad_60m", "cont_pct_comp_mayor_60m"),
    ("via_A_vecino_medio_m", "vecino_medio_m"),
    ("via_A_vecino_sobre_poisson", "vecino_obs_sobre_poisson"),
    ("via_A_abierta", "via_A_abierta"),
    ("via_B_bar_notable", "via_B_bar_notable"),
    ("via_B_restaurante_iconico", "via_B_restaurante_iconico"),
    ("via_B_pizzeria_emblematica", "via_B_pizzeria_emblematica"),
    ("via_B_heladeria_historica", "via_B_heladeria_historica"),
    ("via_B_michelin", "via_B_michelin"),
    ("via_B_50best", "via_B_50best"),
    ("via_B_patrimonio_normativo", "via_B_patrimonio_normativo"),
    ("via_B_total", "via_B_total"),
    ("via_B_cerrados", "via_B_cerrados"),
    ("via_B_dudosos", "via_B_dudosos"),
    ("via_B_abierta", "via_B_abierta"),
    ("via_C_mercado_patio", "via_C_mercado_patio"),
    ("via_C_cual", "via_C_cual"),
    ("via_D_enclave", "via_D_enclave"),
    ("via_E_reconocimiento", "via_E_reconocimiento"),
    ("via_F_elongacion", "via_F_elongacion"),
    ("via_F_frac_banda_100m", "via_F_frac_banda_100m"),
    ("via_F_ancho_p80_m", "via_F_ancho_p80_m"),
    ("via_F_largo_m", "via_F_largo_m"),
    ("via_F_forma", "via_F_forma"),
    ("n_vias_medibles", "n_vias_medibles"),
]


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    buffer = io.StringIO()

    def p(*args_):
        print(*args_, file=buffer)

    matriz = pd.read_csv(MATRIZ)
    medido = pd.read_csv(OUT / "seis_vias_94_filas.csv")

    columnas_previas = list(matriz.columns)
    ya_estaban = [nueva for nueva, _ in COLUMNAS_NUEVAS if nueva in columnas_previas]
    if ya_estaban:
        p(f"  Las columnas {ya_estaban} ya estaban: la corrida las reescribe en su lugar y no")
        p("  mueve el orden. Es lo que pasa al volver a correr esto, y está bien.")

    if set(matriz.polo_id) != set(medido.polo_id):
        p("  CORTE · la matriz y la medición no tienen las mismas filas. No se escribe nada.")
        print(buffer.getvalue())
        return 1

    # SE BORRAN LAS COLUMNAS NUEVAS DE LA MATRIZ ANTES DE UNIR, y no es cosmético. Sin esto, en
    # la segunda corrida `n_vias_medibles` existía en los dos lados, el merge la dejaba como
    # `n_vias_medibles` (la vieja) y `n_vias_medibles_medido` (la nueva), y la asignación se
    # quedaba con la vieja: la matriz conservaba la medición anterior y el reporte decía que
    # había escrito la nueva. Falla en silencio y parece dato — la familia de R8.
    nombres_nuevos = {nueva for nueva, _ in COLUMNAS_NUEVAS}
    base = matriz.drop(columns=[c for c in matriz.columns if c in nombres_nuevos])
    unido = base.merge(medido, on="polo_id", how="left", suffixes=("", "_medido"))
    faltantes = [origen for _, origen in COLUMNAS_NUEVAS if origen not in unido.columns]
    if faltantes:
        p(f"  CORTE · la medición no trae estas columnas: {faltantes}. No se escribe nada.")
        print(buffer.getvalue())
        return 1
    for nueva, origen in COLUMNAS_NUEVAS:
        unido[nueva] = unido[origen]
    unido["via_E_reconocimiento"] = ""

    conservadas = [c for c in columnas_previas if c not in nombres_nuevos]
    salida = unido[conservadas + [n for n, _ in COLUMNAS_NUEVAS]]

    # ------------------------------------------------------------------ la verificación
    antes = matriz[conservadas].set_index(matriz.polo_id).sort_index()
    despues = salida[conservadas].set_index(salida.polo_id).sort_index()
    diferencias = []
    for columna in conservadas:
        a, b = antes[columna], despues[columna]
        distinto = ~((a == b) | (a.isna() & b.isna()))
        for clave in a.index[distinto]:
            diferencias.append(f"{clave} · {columna}: «{a[clave]}» → «{b[clave]}»")
    if diferencias:
        p(f"  CORTE · {len(diferencias)} celdas de las columnas viejas cambiaron. NO se escribe.")
        for texto in diferencias[:20]:
            p(f"        {texto}")
        print(buffer.getvalue())
        return 1

    salida.to_csv(MATRIZ, index=False, encoding="utf-8")

    p("MATRIZ · las columnas medibles de las seis vías, incorporadas")
    p("=" * 100)
    p("")
    p(f"  filas:    {len(salida)}   (sin cambios)")
    p(f"  columnas: {len(columnas_previas)} → {len(salida.columns)}")
    p(f"  las {len(conservadas)} columnas previas: verificadas celda por celda, 0 diferencias")
    p("")
    p("  Columnas nuevas, en este orden y todas al final:")
    for nueva, _ in COLUMNAS_NUEVAS:
        valores = salida[nueva]
        llenas = int((valores.notna() & (valores.astype(str).str.strip() != "")).sum())
        nota = "  ← vacía a propósito: la llena Diego" if nueva == "via_E_reconocimiento" else ""
        p(f"        {nueva:<32}{llenas:>4} de {len(salida)} con valor{nota}")
    p("")
    p("=" * 100)
    p(f"  {MATRIZ.relative_to(ROOT)} · Google Places: 0 requests")
    p("=" * 100)
    p("")

    (OUT / "MATRIZ_SEIS_VIAS.txt").write_text(buffer.getvalue(), encoding="utf-8")
    print(buffer.getvalue())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
