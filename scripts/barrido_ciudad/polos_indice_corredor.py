"""El índice de corredor: una medida de FORMA, calibrada contra las 22 zonas ya clasificadas.

QUÉ PREGUNTA CONTESTA
---------------------
La definición adoptada dice que un polo puede ser «un núcleo compacto, un corredor, una sucesión
de centralidades o un sistema de subpolos». Hace falta entonces una medida que distinga un núcleo
de un corredor **sin mirar el tamaño**: dos polos con los mismos 200 locales pueden ser una manzana
apretada o una avenida de doce cuadras.

EL ÍNDICE, Y ESTABA ESCRITO ANTES DE CORRER (`LECTURA_PREVIA.md` §3)
----------------------------------------------------------------------
Sobre la nube de puntos del soporte, en EPSG:5347:

    PCA de las coordenadas → σ1 = √λ1 , σ2 = √λ2
    elongacion = σ1 / σ2        ← el índice. Largo sobre ancho, adimensional.

Acompañan, declaradas de antemano y **como diagnóstico, no como sustitutos**: `frac_banda_100m`,
`ancho_p80_m`, `largo_p5_p95_m` y `elongacion_rect` (la del polígono, no la de los puntos).

    corte declarado     elongacion >= 2,0    convención geométrica, anclada afuera de los datos
    muestra mínima      20 puntos            con menos, un eje principal es ruido

LA CALIBRACIÓN, Y LO QUE PUEDE SALIR MAL CON ELLA
---------------------------------------------------
El Atlas ya clasificó sus 22 en familias y **seis** están declaradas «Eje o corredor» —el
enunciado decía cinco; la sexta es R20 García del Río, que `QUE_ES_UN_POLO.md` §5 también nombra
como corredor—. Se calibra contra las seis y se reporta también contra las cinco.

Pero las 22 envolventes son **dibujos editoriales**: a lo que alguien decidió llamar corredor se
le dibujó una franja, y los puntos adentro de una franja salen elongados por construcción. Si el
índice acierta sólo por eso, está leyendo la mano del cartógrafo. Por eso la corrida mide la
correlación entre la elongación de los puntos y la del polígono, con el umbral escrito antes
(rho >= 0,80 → calibración contaminada), y el veredicto sale con esa salvedad pegada.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/polos_indice_corredor.py
"""
from __future__ import annotations

import io
import sys
import warnings
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from polos_soporte import (  # noqa: E402
    BARRIDO,
    CRS_METRICO,
    envolventes_22,
    puntos_base,
    soportes_94,
)

OUT = BARRIDO / "seis_vias"

# --------------------------------------------------------------------------- lo declarado
CORTE_ELONGACION = 2.0          # convención: dos veces más largo que ancho
MUESTRA_MINIMA = 20             # con menos puntos, el eje principal es ruido
BANDA_M = 100                   # una cuadra de ancho
CURVA_BANDA_M = (50, 75, 100, 150, 200)
UMBRAL_AUC = 0.80
UMBRAL_RHO_CONTAMINACION = 0.80

FAMILIA_CORREDOR = "Eje o corredor"
FAMILIA_POLO = "Polo"
CINCO_DEL_ENUNCIADO = ["R02", "R11", "R14", "R16", "R19"]


def indice(coordenadas: np.ndarray) -> dict:
    """El índice y su diagnóstico sobre una nube de puntos ya en metros."""
    n = len(coordenadas)
    if n < MUESTRA_MINIMA:
        salida = {"n_puntos": n, "elongacion": np.nan, "ancho_p80_m": np.nan,
                  "largo_p5_p95_m": np.nan,
                  "motivo_na": f"muestra insuficiente ({n} < {MUESTRA_MINIMA})"}
        salida.update({f"frac_banda_{m}m": np.nan for m in CURVA_BANDA_M})
        return salida

    centro = coordenadas.mean(axis=0)
    centradas = coordenadas - centro
    covarianza = np.cov(centradas.T)
    valores, vectores = np.linalg.eigh(covarianza)
    orden = np.argsort(valores)[::-1]
    valores, vectores = valores[orden], vectores[:, orden]
    sigma1, sigma2 = np.sqrt(max(valores[0], 0)), np.sqrt(max(valores[1], 0))

    sobre_eje = centradas @ vectores[:, 0]
    al_costado = np.abs(centradas @ vectores[:, 1])

    salida = {
        "n_puntos": n,
        "elongacion": float(sigma1 / sigma2) if sigma2 > 0 else np.inf,
        "ancho_p80_m": float(np.percentile(al_costado, 80)),
        "largo_p5_p95_m": float(np.percentile(sobre_eje, 95) - np.percentile(sobre_eje, 5)),
        "motivo_na": "",
    }
    for metros in CURVA_BANDA_M:
        salida[f"frac_banda_{metros}m"] = float((al_costado <= metros).mean())
    return salida


def elongacion_rect(geometria) -> float:
    """Largo sobre ancho del rectángulo rotado mínimo del polígono. Es la forma DIBUJADA."""
    if geometria is None or geometria.is_empty:
        return np.nan
    rectangulo = geometria.minimum_rotated_rectangle
    puntos = np.array(rectangulo.exterior.coords[:-1])
    lados = np.linalg.norm(np.diff(np.vstack([puntos, puntos[:1]]), axis=0), axis=1)
    largo, ancho = max(lados[0], lados[1]), min(lados[0], lados[1])
    return float(largo / ancho) if ancho > 0 else np.inf


def medir(capa: gpd.GeoDataFrame, puntos: gpd.GeoDataFrame, clave: str) -> pd.DataFrame:
    """El índice para cada geometría de una capa, con los puntos de la base que caen adentro."""
    dentro = gpd.sjoin(puntos[["local_id", "geometry"]], capa[[clave, "geometry"]],
                       predicate="within", how="inner")
    filas = []
    for fila in capa.itertuples():
        identificador = getattr(fila, clave)
        if fila.geometry is None or fila.geometry.is_empty:
            registro = {clave: identificador, "n_puntos": 0, "elongacion": np.nan,
                        "motivo_na": "sin soporte geométrico", "elongacion_rect": np.nan,
                        "ha": np.nan}
            registro.update({f"frac_banda_{m}m": np.nan for m in CURVA_BANDA_M})
            registro.update({"ancho_p80_m": np.nan, "largo_p5_p95_m": np.nan})
            filas.append(registro)
            continue
        miembros = dentro[dentro[clave] == identificador]
        coordenadas = np.array([[p.x, p.y] for p in
                                puntos.loc[miembros.index.unique(), "geometry"]]) \
            if len(miembros) else np.empty((0, 2))
        registro = {clave: identificador}
        registro.update(indice(coordenadas))
        registro["elongacion_rect"] = elongacion_rect(fila.geometry)
        registro["ha"] = round(fila.geometry.area / 10_000, 2)
        filas.append(registro)
    return pd.DataFrame(filas)


def auc(positivos: list[float], negativos: list[float]) -> float:
    """Probabilidad de que un positivo tomado al azar supere a un negativo. Empates cuentan 0,5."""
    positivos = [v for v in positivos if not np.isnan(v)]
    negativos = [v for v in negativos if not np.isnan(v)]
    if not positivos or not negativos:
        return np.nan
    ganadas = sum((1.0 if p > n else 0.5 if p == n else 0.0)
                  for p in positivos for n in negativos)
    return ganadas / (len(positivos) * len(negativos))


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    OUT.mkdir(parents=True, exist_ok=True)
    buffer = io.StringIO()

    def p(*args_):
        print(*args_, file=buffer)

    puntos = puntos_base()
    envolventes = envolventes_22()

    p("ÍNDICE DE CORREDOR · calibrado contra las 22 del Atlas, que ya están clasificadas")
    p("=" * 100)
    p("")
    p(f"  universo de puntos: {len(puntos):,} locales del anillo núcleo con apto_geometria = True")
    p(f"  índice: elongacion = σ1/σ2 sobre PCA en {CRS_METRICO}")
    p(f"  corte declarado: {CORTE_ELONGACION} · muestra mínima: {MUESTRA_MINIMA} puntos")
    p("  Todo esto estaba escrito en LECTURA_PREVIA.md antes de correr. Google Places: 0 requests.")
    p("")

    medidas = medir(envolventes, puntos, "referencia_id")
    tabla = envolventes[["referencia_id", "nombre", "familia"]].merge(
        medidas, on="referencia_id", how="left")
    tabla = tabla.sort_values("elongacion", ascending=False).reset_index(drop=True)

    # ------------------------------------------------------------------ R8: campos no vacíos
    if tabla.elongacion.notna().sum() == 0:
        p("  CORTE R8: `elongacion` llegó vacía en el 100 % de las 22. No se reporta nada sobre")
        p("  ella. Revisar el recorte de puntos antes de seguir.")
        (OUT / "INDICE_CORREDOR.txt").write_text(buffer.getvalue(), encoding="utf-8")
        print(buffer.getvalue())
        return 1

    p("-" * 100)
    p("  EL RANKING DE LAS 22, con la familia al lado. Ordenado por el índice.")
    p("")
    p(f"  {'id':<5}{'zona':<34}{'familia':<32}{'n':>6}{'elong':>8}{'banda100':>10}"
      f"{'ancho80':>9}{'largo':>8}{'rect':>7}")
    for fila in tabla.itertuples():
        marca = " ←" if fila.familia == FAMILIA_CORREDOR else ""
        elongacion = f"{fila.elongacion:.2f}" if pd.notna(fila.elongacion) else "  NA"
        banda = f"{getattr(fila, f'frac_banda_{BANDA_M}m'):.2f}" \
            if pd.notna(fila.elongacion) else "  NA"
        ancho = f"{fila.ancho_p80_m:,.0f}" if pd.notna(fila.ancho_p80_m) else "NA"
        largo = f"{fila.largo_p5_p95_m:,.0f}" if pd.notna(fila.largo_p5_p95_m) else "NA"
        p(f"  {fila.referencia_id:<5}{fila.nombre[:33]:<34}{fila.familia:<32}"
          f"{fila.n_puntos:>6}{elongacion:>8}{banda:>10}{ancho:>9}{largo:>8}"
          f"{fila.elongacion_rect:>7.2f}{marca}")
    for fila in tabla[tabla.motivo_na != ""].itertuples():
        p(f"        {fila.referencia_id} sin índice: {fila.motivo_na}")
    p("")

    corredores = tabla[tabla.familia == FAMILIA_CORREDOR]
    polos = tabla[tabla.familia == FAMILIA_POLO]

    # El control que esta corrida se ganó a pulso: en su primera pasada leyó la columna `familia`
    # del geojson, que trae la etiqueta corta («eje», «polo»), y las dos comparaciones devolvieron
    # cero filas. Sin error, sin excepción, y con la rama A declarada sobre conjuntos vacíos: 0 de
    # 0 corredores arriba del corte y 0 de 0 polos abajo cumplen la condición de la rama A. Es la
    # familia de R8 —el filtro que no matchea nada y parece dato— y ahora corta.
    if corredores.empty or polos.empty:
        p(f"  CORTE · una de las dos familias quedó vacía: «{FAMILIA_CORREDOR}» "
          f"{len(corredores)} filas, «{FAMILIA_POLO}» {len(polos)} filas.")
        p(f"  Valores presentes en la columna: {sorted(tabla.familia.unique())}")
        p("  Un veredicto sobre un conjunto vacío no es un veredicto. La corrida aborta.")
        (OUT / "INDICE_CORREDOR.txt").write_text(buffer.getvalue(), encoding="utf-8")
        print(buffer.getvalue())
        return 1

    p("-" * 100)
    p("  EL VEREDICTO, contra la lectura escrita antes")
    p("")
    p(f"      «Eje o corredor»: {len(corredores)} zonas   —el enunciado decía 5; R20 García del")
    p("      Río también está declarada corredor en la columna `familia`, y se calibra con las 6")
    p(f"      «Polo»:           {len(polos)} zonas")
    p("")

    arriba = corredores[corredores.elongacion >= CORTE_ELONGACION]
    abajo = polos[polos.elongacion < CORTE_ELONGACION]
    corredores_medibles = corredores[corredores.elongacion.notna()]
    polos_medibles = polos[polos.elongacion.notna()]
    p(f"      corredores con elongacion >= {CORTE_ELONGACION}:  "
      f"{len(arriba)} de {len(corredores_medibles)} medibles")
    for fila in corredores.itertuples():
        estado = "OK " if fila.elongacion >= CORTE_ELONGACION else "NO "
        valor = f"{fila.elongacion:.2f}" if pd.notna(fila.elongacion) else "NA"
        p(f"            {estado} {fila.referencia_id} {fila.nombre[:30]:<32} {valor}")
    p("")
    p(f"      «Polo» con elongacion < {CORTE_ELONGACION}:       "
      f"{len(abajo)} de {len(polos_medibles)} medibles")
    for fila in polos.itertuples():
        estado = "OK " if fila.elongacion < CORTE_ELONGACION else "NO "
        valor = f"{fila.elongacion:.2f}" if pd.notna(fila.elongacion) else "NA"
        p(f"            {estado} {fila.referencia_id} {fila.nombre[:30]:<32} {valor}")
    p("")

    area = auc(list(corredores.elongacion), list(polos.elongacion))
    cinco = tabla[tabla.referencia_id.isin(CINCO_DEL_ENUNCIADO)]
    area_cinco = auc(list(cinco.elongacion), list(polos.elongacion))
    p(f"      AUC(corredor vs Polo) con las 6:  {area:.3f}")
    p(f"      AUC con las 5 del enunciado:      {area_cinco:.3f}")
    p("")

    limpio = (len(arriba) == len(corredores_medibles) and len(abajo) == len(polos_medibles)
              and len(corredores_medibles) == len(corredores)
              and len(polos_medibles) == len(polos))
    if limpio:
        rama, veredicto = "A", "EL ÍNDICE SIRVE · se adopta y se aplica a las 94"
    elif not np.isnan(area) and area >= UMBRAL_AUC:
        rama, veredicto = "B", ("SEPARACIÓN PARCIAL · el índice se publica con su curva y NO "
                                "decide solo: acompaña al criterio")
    else:
        rama, veredicto = "C", ("EL ÍNDICE NO SIRVE · se dice y se busca otro. El corte NO se "
                                "mueve para que separen")
    p(f"      RAMA {rama} · {veredicto}")
    p("")

    # ------------------------------------------------------------------ la circularidad
    comparables = tabla[tabla.elongacion.notna() & tabla.elongacion_rect.notna()]
    rho = comparables.elongacion.corr(comparables.elongacion_rect, method="spearman")
    p("-" * 100)
    p("  LA CIRCULARIDAD, medida y no supuesta")
    p("")
    p("      Las 22 envolventes son dibujos editoriales. Si los puntos sólo repiten la forma del")
    p("      polígono, el índice está leyendo la mano del cartógrafo y no el territorio.")
    p("")
    p(f"      rho de Spearman entre elongacion (puntos) y elongacion_rect (polígono): {rho:.3f}")
    if rho >= UMBRAL_RHO_CONTAMINACION:
        p(f"      >= {UMBRAL_RHO_CONTAMINACION}  →  CALIBRACIÓN CONTAMINADA. El veredicto de arriba")
        p("      vale con esta salvedad pegada: sobre las 94, cuyos polígonos salen de un")
        p("      procedimiento uniforme, la calibración transfiere sólo en parte.")
        contaminada = True
    else:
        p(f"      <  {UMBRAL_RHO_CONTAMINACION}  →  calibración limpia: los puntos dicen algo que")
        p("      el dibujo no fuerza.")
        contaminada = False
    p("")

    p("-" * 100)
    p("  LA CURVA DE LA BANDA (R4) · el resultado depende de los 100 m elegidos a mano")
    p("")
    encabezado = "  familia                          " + "".join(
        f"{m:>8}m" for m in CURVA_BANDA_M)
    p(encabezado)
    for familia in (FAMILIA_CORREDOR, FAMILIA_POLO):
        grupo = tabla[tabla.familia == familia]
        valores = "".join(f"{grupo[f'frac_banda_{m}m'].mean():>9.2f}" for m in CURVA_BANDA_M)
        p(f"  {familia:<33}{valores}")
    p("")
    p("      Es la fracción media de puntos dentro de la banda. Si la brecha entre las dos filas")
    p("      se sostiene a lo largo del rango, la elección de los 100 m no es la mitad del")
    p("      resultado; si se cierra, sí lo es.")
    p("")

    tabla.to_csv(OUT / "indice_corredor_22_zonas.csv", index=False, encoding="utf-8")

    # ------------------------------------------------------------------ aplicar a las 94
    soportes = soportes_94()
    medidas94 = medir(soportes, puntos, "polo_id")
    tabla94 = soportes.drop(columns="geometry").merge(medidas94, on="polo_id", how="left")
    tabla94["forma_declarada"] = np.where(
        tabla94.elongacion.isna(), "",
        np.where(tabla94.elongacion >= CORTE_ELONGACION, "corredor", "nucleo compacto"))
    if rama == "C":
        tabla94["forma_declarada"] = ""
    tabla94["rama_calibracion"] = rama
    tabla94["calibracion_contaminada"] = "si" if contaminada else "no"
    tabla94.to_csv(OUT / "indice_corredor_94_filas.csv", index=False, encoding="utf-8")

    p("-" * 100)
    p("  APLICADO A LAS 94 FILAS DE LA MATRIZ")
    p("")
    p(f"      con índice:        {int(tabla94.elongacion.notna().sum())}")
    p(f"      sin índice:        {int(tabla94.elongacion.isna().sum())}   "
      "(soporte ausente o menos de 20 puntos)")
    for motivo, cuantas in tabla94[tabla94.motivo_na != ""].motivo_na.value_counts().items():
        p(f"            {cuantas} por: {motivo}")
    if rama != "C":
        arriba94 = tabla94[tabla94.elongacion >= CORTE_ELONGACION]
        p(f"      elongacion >= {CORTE_ELONGACION}:  {len(arriba94)} de "
          f"{int(tabla94.elongacion.notna().sum())}")
        p("")
        p("      Las diez de forma más alargada:")
        for fila in tabla94.sort_values("elongacion", ascending=False).head(10).itertuples():
            p(f"            {str(fila.polo_id)[:26]:<28}{str(fila.nombre_polo)[:24]:<26}"
              f"{fila.elongacion:>6.2f}   {fila.soporte_clase}")
        p("")
        p("-" * 100)
        p("  LA TRANSFERENCIA DE ESCALA, que es la salvedad grande y no la chica")
        p("")
        p("      El corte se calibró sobre envolventes editoriales y se aplica sobre polos de un")
        p("      algoritmo, que son un orden de magnitud más chicos. Si la mayoría de los polos")
        p("      queda arriba del corte, el corte no discrimina a esa escala: describe lo normal.")
        p("")
        p(f"      {'soporte':<26}{'n':>5}{'mediana ha':>12}{'mediana elong':>15}"
          f"{'>= corte':>10}")
        for clase, grupo in tabla94[tabla94.elongacion.notna()].groupby("soporte_clase"):
            p(f"      {clase:<26}{len(grupo):>5}{grupo.ha.median():>12.1f}"
              f"{grupo.elongacion.median():>15.2f}"
              f"{(grupo.elongacion >= CORTE_ELONGACION).mean():>9.0%}")
        p("")
        p("      La lectura honesta de esa tabla va en el informe, no acá: el número la fija.")
    else:
        p("      La columna `forma_declarada` sale vacía a propósito: la rama C dice que el")
        p("      índice no sirve para decidir, y publicarla llena sería contradecir el veredicto.")
    p("")

    p("=" * 100)
    p(f"  RAMA {rama} · rho de circularidad {rho:.3f} · "
      f"{int(tabla94.elongacion.notna().sum())} de 94 con índice · Places: 0 requests")
    p("=" * 100)
    p("")

    (OUT / "INDICE_CORREDOR.txt").write_text(buffer.getvalue(), encoding="utf-8")
    print(buffer.getvalue())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
