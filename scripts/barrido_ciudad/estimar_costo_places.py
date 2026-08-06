"""Estimación del costo en requests del barrido de Places. No hace ninguna llamada.

Este script **no toca la red**: es aritmética sobre la grilla y sobre lo que ya sabemos del
universo. Existe porque la regla es contar los requests y decírselo a Diego antes de correr
cualquier cosa con `--run`.

Qué estima, en el orden en que conviene ejecutarlo:
  1. el control de las 22 zonas ya relevadas, que es el experimento que decide si hace falta
     salir a la calle en 48 barrios o en cinco;
  2. el barrido completo de los 48 barrios sobre la grilla de `grilla_places_48_barrios.csv`.

Sobre la paginación: Text Search devuelve hasta 20 resultados por página y hasta tres páginas, y
**cada página es un request**. Estimar todo ×3 sobreestima, porque la mayoría de las celdas no
llega a 20 resultados. Acá se estima página por página según el universo esperado de cada celda, y
se informa también la cota ×3 para tener el peor caso.

Franja gratuita vigente de Google Maps Platform: Text Search cae en el SKU Pro, 5.000 llamadas
gratuitas por mes. El precio por encima de la franja **no está confirmado** y hay que consultarlo
antes de planificar una corrida que se pase.

Uso:
  python scripts/barrido_ciudad/estimar_costo_places.py
"""
from __future__ import annotations

import io
import math
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

BARRIDO = ROOT / "outputs" / "BARRIDO_CIUDAD_2026-08"
OUT_DIR = BARRIDO / "generado"
GRILLA = BARRIDO / "grilla_places_48_barrios.csv"
CAPA_ZONAS = BARRIDO / "capa_homogenea_22_zonas.csv"
CIFRAS_ATLAS = BARRIDO / "insumos" / "cifras_publicadas_atlas_22.csv"
CAPA_RUS_ZONAS = OUT_DIR / "capa_rus_22_zonas.csv"

# Criterios de la grilla, tal como están en SPEC_PLACES_BARRIDO.md.
KM2_POR_CELDA = 0.25
LOCALES_POR_CELDA = 40
FACTOR_CAPTURA_CAMPO = 0.182  # mediana medida del relevamiento propio contra habilitaciones

RESULTADOS_POR_PAGINA = 20
PAGINAS_MAXIMAS = 3
FRANJA_GRATUITA_MENSUAL = 5_000


def miles(numero: int) -> str:
    """Separador de miles con punto, sin tocar el resto de la frase."""
    return f"{numero:,}".replace(",", ".")


def celdas(km2: float, universo_esperado: float) -> int:
    """Celdas de una zona: el mayor de los dos criterios, nunca menos de una."""
    return max(1,
               math.ceil(km2 / KM2_POR_CELDA),
               math.ceil(universo_esperado / LOCALES_POR_CELDA))


def paginas(universo_esperado: float, cantidad_celdas: int) -> int:
    """Requests de una zona, contando páginas y no consultas.

    Cada celda cuesta al menos un request. Si el universo esperado por celda supera los 20
    resultados de la primera página, se paga una segunda; si supera 40, una tercera. Es el tope de
    la API: más de 60 no se pueden traer y por eso la grilla se dimensiona para no llegar.
    """
    por_celda = universo_esperado / cantidad_celdas if cantidad_celdas else 0
    paginas_por_celda = min(PAGINAS_MAXIMAS,
                            max(1, math.ceil(por_celda / RESULTADOS_POR_PAGINA)))
    return cantidad_celdas * paginas_por_celda


def control_22_zonas(p) -> int:
    """El control sobre las zonas ya relevadas, que es lo primero que hay que correr."""
    zonas = pd.read_csv(CAPA_ZONAS, index_col=0, encoding="utf-8")
    zonas.index = [str(i).split(" · ")[0] for i in zonas.index]
    cifras = pd.read_csv(CIFRAS_ATLAS).set_index("rid")
    superficie = pd.read_csv(CAPA_RUS_ZONAS, index_col=0, encoding="utf-8")["hectareas"] / 100

    filas = []
    for rid in zonas.index:
        # El universo esperado de una zona ya relevada es su propia cifra publicada; donde no hay
        # cifra, se estima desde la base documental con el factor de captura medido.
        relevado = cifras.relevado.get(rid)
        esperado = float(relevado) if pd.notna(relevado) else \
            zonas.dir_nucleo[rid] / FACTOR_CAPTURA_CAMPO
        cantidad = celdas(float(superficie.get(rid, 0)), esperado)
        filas.append({
            "rid": rid,
            "zona": cifras.zona_publicada.get(rid, ""),
            "km2": round(float(superficie.get(rid, 0)), 2),
            "universo_esperado": int(round(esperado)),
            "celdas": cantidad,
            "requests": paginas(esperado, cantidad),
            "tiene_cifra_publicada": "si" if pd.notna(relevado) else "no",
        })
    tabla = pd.DataFrame(filas)

    con_cifra = tabla[tabla.tiene_cifra_publicada == "si"]
    p("PASO 1 · Control de las 22 zonas ya relevadas")
    p("")
    p("  Es el experimento que decide el plan: si Places captura cerca del 100 % en las zonas")
    p("  relevadas a pie, sustituye al campo y el barrido se hace sin caminar. Si captura como el")
    p("  directorio comercial, el campo sigue haciendo falta.")
    p("")
    p(f"  las 22 zonas completas: {int(tabla.celdas.sum())} celdas, "
      f"**{int(tabla.requests.sum())} requests**")
    p(f"  cota superior si toda celda paginara al máximo (×3): "
      f"{int(tabla.celdas.sum()) * PAGINAS_MAXIMAS} requests")
    p("")
    p(f"  sólo las {len(con_cifra)} zonas con cifra publicada, que son las únicas comparables: "
      f"{int(con_cifra.celdas.sum())} celdas, **{int(con_cifra.requests.sum())} requests**")
    propio = con_cifra[con_cifra.rid.isin(["R08", "R09", "R10", "R11"])]
    p(f"  y sólo las 4 relevadas a pie por la Dirección (R08-R11), que es el corazón del control: "
      f"{int(propio.celdas.sum())} celdas, **{int(propio.requests.sum())} requests**")
    p("")
    p(tabla.sort_values("requests", ascending=False).to_string(index=False))
    p("")
    tabla.to_csv(OUT_DIR / "estimacion_places_22_zonas.csv", index=False, encoding="utf-8")
    return int(con_cifra.requests.sum())


def barrido_48_barrios(p) -> int:
    """El barrido completo, sobre la grilla ya calculada."""
    grilla = pd.read_csv(GRILLA, encoding="utf-8-sig")
    grilla["requests"] = [paginas(fila.univ_est, int(fila.celdas)) for fila in grilla.itertuples()]

    # Reproducción de la grilla, para verificar que los dos criterios dan lo mismo que el CSV.
    recalculadas = [celdas(fila.km2, fila.univ_est) for fila in grilla.itertuples()]
    coinciden = int((pd.Series(recalculadas) == grilla.celdas).sum())

    p("PASO 2 · Barrido completo de los 48 barrios")
    p("")
    p(f"  grilla reproducida desde km² y universo esperado: {coinciden} de {len(grilla)} barrios "
      "coinciden con el CSV")
    p(f"  celdas: {miles(int(grilla.celdas.sum()))}")
    p(f"  **requests estimados contando páginas: {miles(int(grilla.requests.sum()))}**")
    p(f"  cota superior ×3: {miles(int(grilla.celdas.sum()) * PAGINAS_MAXIMAS)}")
    p("")
    p(f"  franja gratuita mensual (Text Search, SKU Pro): {miles(FRANJA_GRATUITA_MENSUAL)}")
    estimado = int(grilla.requests.sum())
    if estimado <= FRANJA_GRATUITA_MENSUAL:
        margen = miles(FRANJA_GRATUITA_MENSUAL - estimado)
        p(f"  → **entra en un mes gratuito**, con {margen} requests de margen")
    else:
        meses = math.ceil(estimado / FRANJA_GRATUITA_MENSUAL)
        p(f"  → **no entra**: haría falta partirlo en {meses} meses o pedir presupuesto")
    p("")
    p("  los diez barrios más caros:")
    caros = grilla.nlargest(10, "requests")[["barrio", "km2", "dir_nucleo", "univ_est",
                                             "celdas", "requests"]]
    p(caros.to_string(index=False))
    p("")

    # Dónde manda la superficie y no la densidad: ahí la grilla gasta requests en vacío.
    grilla["manda"] = ["superficie" if math.ceil(f.km2 / KM2_POR_CELDA) >
                       math.ceil(f.univ_est / LOCALES_POR_CELDA) else "densidad"
                       for f in grilla.itertuples()]
    por_superficie = grilla[grilla.manda == "superficie"]
    p(f"  en {len(por_superficie)} barrios la grilla la manda la superficie y no la densidad: "
      f"{miles(int(por_superficie.requests.sum()))} requests")
    p("    son barrios grandes y poco densos; ahí conviene bajar la grilla a celdas de 1 km antes")
    p("    de correr, porque se pagan celdas que van a volver casi vacías:")
    p("    " + ", ".join(f"{f.barrio} ({int(f.celdas)} celdas, {int(f.univ_est)} esperados)"
                        for f in por_superficie.nlargest(6, "celdas").itertuples()))
    p("")
    grilla.to_csv(OUT_DIR / "estimacion_places_48_barrios.csv", index=False, encoding="utf-8")
    return estimado


def main() -> int:
    buffer = io.StringIO()

    def p(*args):
        print(*args, file=buffer)

    p("Estimación de requests del barrido de Places · NINGUNA LLAMADA EJECUTADA")
    p("=" * 78)
    p("")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    control = control_22_zonas(p)
    barrido = barrido_48_barrios(p)

    p("RESUMEN PARA LA DECISIÓN")
    p("")
    p(f"  paso 1, control de las zonas con cifra publicada: {control} requests")
    p(f"  paso 2, barrido de los 48 barrios: {miles(barrido)} requests")
    p(f"  los dos juntos: {miles(control + barrido)} requests contra una franja de "
      f"{miles(FRANJA_GRATUITA_MENSUAL)}")
    p("")
    p("  El paso 1 hay que correrlo primero y solo: es barato y puede cambiar el paso 2 entero.")
    p("  El precio por encima de la franja no está confirmado y hay que consultarlo antes de")
    p("  planificar cualquier corrida que se pase.")

    (OUT_DIR / "ESTIMACION_PLACES.txt").write_text(buffer.getvalue(), encoding="utf-8")
    print(buffer.getvalue())
    print(f"escrito en {OUT_DIR.relative_to(ROOT)}: ESTIMACION_PLACES.txt, "
          "estimacion_places_22_zonas.csv, estimacion_places_48_barrios.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
