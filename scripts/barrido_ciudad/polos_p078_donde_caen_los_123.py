"""¿Dónde caen los 123 locales de P078 que quedan afuera de sus tres partes?

QUÉ DECIDE ESTA CORRIDA
------------------------
P078 dio tres partes estables (333 / 88 / 41) con **79,0 % de cobertura contra un umbral de
80 %**. La decisión de aceptarlas como excepción registrada se apoya en un argumento documental:
las tres caen dentro de R01 Palermo, que el Atlas publica como polo con partes, y cuya ficha dice
que entre Soho, Hollywood y Las Cañitas *«hay tramos sin oferta, y esos espacios forman parte de
cómo funciona la zona»*.

Si eso es cierto, **el 21 % que queda afuera no es defecto de la partición: es la estructura
documentada de la zona.** Pero es una afirmación falsable y hay que medirla antes de firmar la
excepción. Si los 123 estuvieran amontonados de un solo lado —una cola que cuelga del extremo de
S1— la lectura sería otra: sobraría un pedazo de polo, no faltarían los intersticios.

LA LECTURA, ESCRITA ANTES DE CORRER (R1)
-----------------------------------------
La medida que decide es **cuántos de los 123 quedan ENTRE dos partes**. Un local está entre A y B
si, mirado desde él, A y B caen en direcciones opuestas (ángulo obtuso hacia el punto más cercano
de cada una). Un local que cuelga por afuera de A tiene a A y a B en la misma dirección.

    ≥ 2/3 entre dos partes   → CONFIRMA. Son los tramos sin oferta que la ficha de R01 describe.
                               La excepción se firma con este motivo escrito.
    ≤ 1/3 entre dos partes   → NO CONFIRMA. Están concentrados de un lado y hay que mirar qué son
                               antes de aceptar nada.
    entre 1/3 y 2/3          → MIXTO. Se reporta el reparto y decide una persona; el script no
                               elige por su cuenta cuál de las dos lecturas gana.

Dos medidas de apoyo, que no deciden solas pero tienen que ser coherentes con la principal:

  · **adentro/afuera del envolvente conjunto** de las tres partes. Un local intersticial cae
    adentro; una cola cae afuera.
  · **reparto por parte más cercana**, contra la cuota de locales de cada parte. S1 tiene el 72 %
    de los locales de las partes, así que un reparto parejo NO es un tercio cada una: la
    expectativa naive es la cuota, y se imprime al lado para no leer como concentración lo que es
    tamaño.

Google Places: 0 requests. No se toca ninguna cifra publicada ni el borrador de polos.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/polos_p078_donde_caen_los_123.py
"""
from __future__ import annotations

import io
import sys
import warnings
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely
from scipy.spatial import cKDTree

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from borrador_polos_ciudad import (  # noqa: E402
    CRS_METRICO, ENVOLVENTES_22, PARAMETROS, cargar_puntos, envolver,
)
from polos_atributos_clases import OUT  # noqa: E402
from polos_particion_anada_estructura import MINIMO, componentes  # noqa: E402

POLO = "P078"
UMBRAL = 55          # el más alto del tramo estable (40, 55): el que menos fragmenta
BANDA_CONFIRMA = 2 / 3
BANDA_RECHAZA = 1 / 3


def partes_y_sueltos(cuerpo: gpd.GeoDataFrame, umbral: int):
    """Las componentes que llegan a `MINIMO` son partes; el resto son los sueltos."""
    todas = componentes(cuerpo, umbral)
    partes = [c for c in todas if len(c) >= MINIMO]
    sueltos = [c for c in todas if len(c) < MINIMO]
    return partes, sueltos


def entre_dos_partes(punto, arboles: list[cKDTree], xys: list[np.ndarray]) -> dict:
    """¿El local está ENTRE dos partes, o cuelga por afuera de una?

    Se toma el punto más cercano de la parte más cercana y el de la segunda, y se mide el ángulo
    entre las dos direcciones. Obtuso = las partes quedan a lados opuestos = el local está en el
    tramo que las separa. Agudo = las dos quedan para el mismo lado = el local cuelga del extremo.

    Es una prueba sin umbral de distancia elegido a mano, que es justamente lo que se quiere: la
    respuesta no puede depender de cuántos metros llamemos «cerca».
    """
    distancias, vecinos = [], []
    for arbol, xy in zip(arboles, xys):
        d, i = arbol.query(punto)
        distancias.append(float(d))
        vecinos.append(xy[i])
    orden = np.argsort(distancias)
    a, b = orden[0], orden[1]
    v1 = vecinos[a] - punto
    v2 = vecinos[b] - punto
    coseno = float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-12))
    angulo = float(np.degrees(np.arccos(np.clip(coseno, -1, 1))))
    return {
        "parte_cercana": f"S{a + 1}",
        "d_cercana_m": round(distancias[a], 1),
        "parte_segunda": f"S{b + 1}",
        "d_segunda_m": round(distancias[b], 1),
        "angulo_grados": round(angulo, 1),
        "entre_dos_partes": angulo > 90,
        "par": f"S{min(a, b) + 1}–S{max(a, b) + 1}",
    }


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    buffer = io.StringIO()

    def p(*args_):
        print(*args_, file=buffer)

    geo = cargar_puntos(PARAMETROS["anillo"], PARAMETROS["solo_aptos"])
    pertenencia = pd.read_csv(OUT / "pertenencia_local_polo_v3.csv")
    geo = geo.merge(pertenencia[["local_id", "polo_unido"]], on="local_id", how="left")
    geo["polo_unido"] = geo.polo_unido.fillna("")
    cuerpo = geo[geo.polo_unido == POLO].reset_index(drop=True)
    zonas = gpd.read_file(ENVOLVENTES_22).to_crs(CRS_METRICO)

    partes, sueltos = partes_y_sueltos(cuerpo, UMBRAL)
    indices_sueltos = [i for c in sueltos for i in c]
    en_partes = sum(len(c) for c in partes)

    p(f"¿DÓNDE CAEN LOS {len(indices_sueltos)} LOCALES DE {POLO} QUE QUEDAN AFUERA DE SUS TRES PARTES?")
    p("=" * 100)
    p("")
    p("  La excepción de P078 se apoya en un argumento documental: la ficha de R01 Palermo dice que")
    p("  entre Soho, Hollywood y Las Cañitas «hay tramos sin oferta, y esos espacios forman parte de")
    p("  cómo funciona la zona». Si es así, el 21 % de afuera es la estructura de la zona y no un")
    p("  defecto de la partición. Es falsable, y esto lo mide.")
    p("")
    p(f"  polo {POLO} · {len(cuerpo)} locales · umbral {UMBRAL} m (el más alto del tramo estable)")
    p(f"  partes (≥ {MINIMO} locales): {len(partes)} → {en_partes} locales "
      f"({en_partes / len(cuerpo) * 100:.1f} %)")
    p(f"  sueltos: {len(indices_sueltos)} locales en {len(sueltos)} componentes")
    p("")
    p("  LECTURA DECLARADA ANTES DE CORRER:")
    p(f"    ≥ {BANDA_CONFIRMA:.0%} entre dos partes → CONFIRMA (tramos sin oferta, excepción firmada)")
    p(f"    ≤ {BANDA_RECHAZA:.0%} entre dos partes → NO CONFIRMA (concentrados de un lado)")
    p("    en el medio                → MIXTO, decide una persona")
    p("")

    # --- las tres partes, para tener la referencia de tamaño al lado del reparto
    xys, arboles, resumen_partes = [], [], []
    for orden, indices in enumerate(partes, start=1):
        miembros = cuerpo.iloc[indices]
        xy = np.c_[miembros.geometry.x.to_numpy(), miembros.geometry.y.to_numpy()]
        xys.append(xy)
        arboles.append(cKDTree(xy))
        geometria, _ = envolver(miembros, PARAMETROS["concave_hull_ratio"])
        resumen_partes.append({
            "parte": f"S{orden}",
            "locales": len(miembros),
            "cuota_de_las_partes": f"{len(miembros) / en_partes * 100:.1f} %",
            "ha": round(geometria.area / 1e4, 1),
        })
    p("-" * 100)
    p("  LAS TRES PARTES")
    p(pd.DataFrame(resumen_partes).to_string(index=False))
    p("")

    # --- envolvente conjunto: el perímetro de las tres partes juntas
    todos_los_puntos = np.vstack(xys)
    conjunto = shapely.MultiPoint([shapely.Point(x, y) for x, y in todos_los_puntos]).convex_hull

    filas = []
    for i in indices_sueltos:
        fila = cuerpo.iloc[i]
        punto = np.array([fila.geometry.x, fila.geometry.y])
        medida = entre_dos_partes(punto, arboles, xys)
        medida.update({
            "local_id": fila.local_id,
            "barrio": fila.barrio,
            "adentro_del_envolvente": conjunto.contains(fila.geometry),
        })
        filas.append(medida)
    sueltos_df = pd.DataFrame(filas)

    # el tamaño de la componente de cada suelto, para separar «esquirlas» de «bloques»
    tamano = {i: len(c) for c in sueltos for i in c}
    sueltos_df["tam_componente"] = [tamano[i] for i in indices_sueltos]

    entre = int(sueltos_df.entre_dos_partes.sum())
    fraccion = entre / len(sueltos_df)
    adentro = int(sueltos_df.adentro_del_envolvente.sum())

    p("-" * 100)
    p("  MEDIDA PRINCIPAL · ¿ENTRE DOS PARTES, O COLGANDO DE UNA?")
    p("")
    p(f"    entre dos partes:   {entre:>4} de {len(sueltos_df)}  ({fraccion:.1%})")
    p(f"    colgando de una:    {len(sueltos_df) - entre:>4} de {len(sueltos_df)}  "
      f"({1 - fraccion:.1%})")
    p("")
    if fraccion >= BANDA_CONFIRMA:
        veredicto = "CONFIRMA"
        p("    **CONFIRMA.** Los sueltos están repartidos en los tramos que separan a las tres")
        p("    partes, que es exactamente lo que la ficha de R01 describe. El 21 % de afuera es la")
        p("    estructura de la zona, no fragmentación.")
    elif fraccion <= BANDA_RECHAZA:
        veredicto = "NO CONFIRMA"
        p("    **NO CONFIRMA.** La mayoría cuelga por afuera de una sola parte. Eso no es un tramo")
        p("    sin oferta entre partes: hay que mirar qué es antes de firmar la excepción.")
    else:
        veredicto = "MIXTO"
        p("    **MIXTO.** Ni una lectura ni la otra. Se reporta el reparto y decide una persona.")
    p("")
    p(f"    apoyo · adentro del envolvente de las tres partes: {adentro} de {len(sueltos_df)} "
      f"({adentro / len(sueltos_df):.1%})")
    p("")

    p("-" * 100)
    p("  REPARTO POR PARTE MÁS CERCANA · contra la cuota de locales de cada parte")
    p("")
    reparto = sueltos_df.groupby("parte_cercana").agg(
        sueltos=("local_id", "size"),
        entre_dos=("entre_dos_partes", "sum"),
        d_mediana_m=("d_cercana_m", "median"),
    ).reset_index()
    cuotas = {f"S{o}": len(c) / en_partes for o, c in enumerate(partes, start=1)}
    reparto["pct_de_los_sueltos"] = (reparto.sueltos / len(sueltos_df) * 100).round(1)
    reparto["cuota_de_locales"] = [round(cuotas[s] * 100, 1) for s in reparto.parte_cercana]
    p(reparto.to_string(index=False))
    p("")
    p("    La columna `cuota_de_locales` es la expectativa naive: una parte con el 72 % de los")
    p("    locales queda cerca de más sueltos por tamaño, no por concentración. Se lee la")
    p("    diferencia entre las dos columnas, no la primera sola.")
    p("")

    p("-" * 100)
    p("  EN QUÉ TRAMO CAEN · el par de partes que cada suelto separa")
    p("")
    pares = sueltos_df[sueltos_df.entre_dos_partes].groupby("par").agg(
        locales=("local_id", "size"),
        d_cercana_mediana=("d_cercana_m", "median"),
        d_segunda_mediana=("d_segunda_m", "median"),
    ).reset_index()
    p(pares.to_string(index=False) if len(pares) else "    ninguno")
    p("")

    p("-" * 100)
    p("  A QUÉ DISTANCIA ESTÁN DE SU PARTE MÁS CERCANA")
    p("")
    d = sueltos_df.d_cercana_m
    p(f"    mínimo {d.min():.0f} m · p25 {d.quantile(.25):.0f} m · mediana {d.median():.0f} m · "
      f"p75 {d.quantile(.75):.0f} m · máximo {d.max():.0f} m")
    p(f"    a menos de 120 m de una parte: {int((d < 120).sum())} de {len(d)} "
      f"({(d < 120).mean():.0%})")
    p("")
    p("    Un suelto a 60–120 m de una parte está en el tramo de enfrente, no en otro barrio. El")
    p("    umbral que lo dejó afuera es de 55 m: la distancia se lee contra ese número.")
    p("")

    p("-" * 100)
    p("  CÓMO SON LAS COMPONENTES SUELTAS")
    p("")
    tamanos = pd.Series([len(c) for c in sueltos]).value_counts().sort_index()
    p("    tamaño · cuántas componentes")
    for t, n in tamanos.items():
        p(f"      {t:>3}  ·  {n}")
    p(f"    la más grande tiene {max(len(c) for c in sueltos)} locales, contra un mínimo de "
      f"{MINIMO} para ser parte.")
    p("")
    p("    Esto NO decide: en P065 los sueltos también eran esquirlas y ahí sí eran el problema,")
    p("    porque se llevaban el 46,5 % del polo. Acá se llevan el 21 % y el que decide es dónde")
    p("    caen, no cuán chicas son.")
    p("")

    p("-" * 100)
    p("  LOS TRES BLOQUES GRANDES · 70 de los 123 están en sólo tres componentes")
    p("")
    grandes = sorted(sueltos, key=len, reverse=True)[:3]
    filas_bloques = []
    for orden, indices in enumerate(grandes, start=1):
        miembros = cuerpo.iloc[indices]
        sub = sueltos_df[sueltos_df.local_id.isin(miembros.local_id)]
        filas_bloques.append({
            "bloque": f"B{orden}",
            "locales": len(indices),
            "le_faltan_para_ser_parte": MINIMO - len(indices),
            "parte_cercana": sub.parte_cercana.mode().iloc[0],
            "d_mediana_m": round(sub.d_cercana_m.median(), 1),
            "entre_dos_partes": int(sub.entre_dos_partes.sum()),
            "barrio": miembros.barrio.value_counts().index[0],
        })
    p(pd.DataFrame(filas_bloques).to_string(index=False))
    p("")
    p("    Tres bloques de 35, 23 y 12 contra un mínimo de 40 no son esquirlas: son casi-partes.")
    p("    Y NO se baja el mínimo para recuperarlos (R3): el umbral se fijó antes de mirar quién")
    p("    sobrevivía. Queda anotado que el que más cerca estuvo se quedó a 5 locales.")
    p("")

    p("-" * 100)
    p("  BARRIO Y ZONA PUBLICADA DE LOS SUELTOS")
    p("")
    p(sueltos_df.barrio.value_counts().to_string())
    p("")
    dentro_r01 = 0
    r01 = zonas[zonas.referencia_id == "R01"]
    if len(r01):
        geometria_r01 = r01.geometry.iloc[0]
        puntos_sueltos = cuerpo.iloc[indices_sueltos]
        dentro_r01 = int(puntos_sueltos.geometry.within(geometria_r01).sum())
        # CONTROL, y sin él el 10 % no se puede leer: si las partes tampoco están adentro de R01,
        # el número no dice nada de los sueltos, dice que R01 es más chico que P078. La comparación
        # es punto contra punto — el 67 % de la tabla de partes es área de hull, no locales.
        p(f"    adentro del polígono publicado R01 Palermo: {dentro_r01} de {len(indices_sueltos)} "
          f"({dentro_r01 / len(indices_sueltos):.0%})")
        p("")
        p("    CONTROL · la misma medida sobre las partes, que es la única forma de leer el número")
        p("    de arriba. Un 10 % en los sueltos no significa nada si las partes dan parecido.")
        p("")
        control = []
        for orden, indices in enumerate(partes, start=1):
            miembros = cuerpo.iloc[indices]
            adentro_p = int(miembros.geometry.within(geometria_r01).sum())
            control.append({
                "grupo": f"S{orden}",
                "locales": len(miembros),
                "adentro_de_R01": adentro_p,
                "pct": f"{adentro_p / len(miembros) * 100:.0f} %",
            })
        control.append({
            "grupo": "sueltos",
            "locales": len(indices_sueltos),
            "adentro_de_R01": dentro_r01,
            "pct": f"{dentro_r01 / len(indices_sueltos) * 100:.0f} %",
        })
        p(pd.DataFrame(control).to_string(index=False))
        p("")
        # ¿Y si el saliente está adentro de OTRA zona publicada? Sería una lectura distinta:
        # no un sobrante de P078 sino un pedazo que el Atlas ya publica con otro nombre.
        conteo = {}
        for z in zonas.itertuples():
            n = int(puntos_sueltos.geometry.within(z.geometry).sum())
            if n:
                conteo[z.referencia_id] = n
        p("    ¿caen adentro de alguna otra zona publicada?")
        if conteo:
            for k, v in sorted(conteo.items(), key=lambda x: -x[1]):
                p(f"      {k}: {v} locales")
        else:
            p("      ninguna.")
        fuera_de_todo = int(len(indices_sueltos) - sum(conteo.values()))
        p(f"      fuera de toda zona publicada: {fuera_de_todo} de {len(indices_sueltos)} "
          f"({fuera_de_todo / len(indices_sueltos):.0%})")
        p("")

    p("-" * 100)
    p("  ¿ANILLO O SALIENTE? · la pregunta que queda cuando cuelgan todos de la misma parte")
    p("")
    # Si los sueltos rodean a S1 en todas las direcciones son un borde difuso; si se van todos
    # para el mismo lado son un saliente del polo. La longitud resultante R del promedio circular
    # lo separa sin elegir sectores a mano: R≈0 es anillo, R≈1 es una sola dirección.
    centro_s1 = xys[0].mean(axis=0)
    colgando = sueltos_df[~sueltos_df.entre_dos_partes]
    puntos_colgando = cuerpo[cuerpo.local_id.isin(colgando.local_id)]
    vectores = np.c_[puntos_colgando.geometry.x.to_numpy() - centro_s1[0],
                     puntos_colgando.geometry.y.to_numpy() - centro_s1[1]]
    angulos = np.arctan2(vectores[:, 1], vectores[:, 0])
    resultante = float(np.hypot(np.cos(angulos).mean(), np.sin(angulos).mean()))
    rumbo = (90 - np.degrees(np.arctan2(np.sin(angulos).mean(), np.cos(angulos).mean()))) % 360
    sectores = pd.Series(
        pd.cut((90 - np.degrees(angulos)) % 360, bins=np.arange(0, 361, 45), right=False,
               labels=["N", "NE", "E", "SE", "S", "SO", "O", "NO"])
    ).value_counts().sort_index()
    p(f"    concentración direccional (R): {resultante:.2f}   ·   rumbo medio: {rumbo:.0f}°")
    p("      R ≈ 0 → anillo alrededor de S1 (borde difuso)")
    p("      R ≈ 1 → todos para el mismo lado (saliente del polo)")
    p("")
    p("    reparto por sector, desde el centro de S1:")
    for sector, n in sectores.items():
        p(f"      {sector:>2}  {'█' * int(n / 2):<25} {n}")
    p("")

    p("=" * 100)
    p(f"VEREDICTO: {veredicto}")
    p("=" * 100)
    p("")
    p(f"  entre dos partes {fraccion:.1%} · adentro del envolvente {adentro / len(sueltos_df):.1%} · "
      f"adentro de R01 {dentro_r01 / len(indices_sueltos):.0%} · concentración direccional "
      f"R = {resultante:.2f}")
    p("")

    salida = buffer.getvalue()
    (OUT / "P078_DONDE_CAEN_LOS_SUELTOS.txt").write_text(salida, encoding="utf-8")
    sueltos_df.to_csv(OUT / "p078_sueltos_ubicacion.csv", index=False, encoding="utf-8")
    reparto.to_csv(OUT / "p078_sueltos_reparto.csv", index=False, encoding="utf-8")

    print(salida)
    print(f"escrito en {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
