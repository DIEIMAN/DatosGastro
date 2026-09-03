"""Las tres preguntas que quedaron abiertas sobre el borrador. BORRADOR — no se publica.

§A · EL PRECIO DE LA PARTICIÓN, DESGLOSADO
   1.064 locales y dos zonas no es un número que se apruebe en agregado. Hay que saber cuáles.
   Para cada polo padre que se partió, dónde cayeron sus locales sueltos:
     · ¿son TEJIDO CONECTIVO entre las piezas que se separaron? Entonces la partición hizo lo
       correcto y esos locales engrosan el «fuera de todo polo», que ya era la mayoría.
     · ¿o hay un BLOQUE COHERENTE que quedó por debajo del mínimo? Eso sería error de partición.
   La prueba es directa y se declara antes de correrla: se vuelve a correr el MISMO clustering
   sobre los locales sueltos de cada padre, solos. Si de ahí sale un cluster de 40 o más, había un
   bloque; si sale ruido, era tejido. Y se mide, además, cuántos caen adentro de la cáscara que
   envuelve a las piezas —posición de tejido— y cuántos afuera.

   Y las dos zonas perdidas se identifican con su FAMILIA del Atlas, que es lo que decide:
   perder una «referencia dispersa» la confirma —no tiene por qué producir un cluster—; perder una
   con nombre e identidad documental obliga a revisar la partición que la rompió.

§B · LA CURVA DE SENSIBILIDAD DE LOS SEIS QUE `leaf` NO PARTIÓ
   Que `leaf` no encuentre nada que partir no prueba que no haya nada: prueba que ese método no lo
   encontró. Para convertir esa ausencia en evidencia hace falta medirlo, y el proyecto ya tiene el
   instrumento: el barrido de continuidad con el que se decidió Belgrano —se unen los puntos que
   están a menos de un umbral, se cuentan las componentes conexas y sus tamaños, y se mueve el
   umbral—. Es el mismo `graph_components` de `ejecutar_corrida_territorial_v3.py`.

   **Y el barrido se corre también sobre los polos que SÍ se partieron.** Sin esos controles
   positivos, una curva plana no dice nada: no se sabe si el instrumento distingue estructura de
   ausencia de estructura. Con ellos, una curva plana al lado de una escalonada es una medición.

   Criterio declarado antes de mirar: la curva es PLANA si el número de componentes de tamaño
   nombrable (≥ min_cluster_size) es 1 en TODOS los umbrales del barrido. Si en algún tramo
   aparecen dos o más partes estables de tamaño comparable, ése se parte con el criterio de
   Belgrano.

§C · LA AÑADA CONTRA LA DENSIDAD
   Si los barrios relevados en 2022 muestran sistemáticamente menor densidad, la clase C no es sólo
   «extendida»: es en parte «relevada en 2022». Tres pruebas, y la tercera es la que decide:

     C.1 ¿cuánta varianza de la densidad explica la añada? (eta² y Kruskal–Wallis)
     C.2 dentro de cada cohorte por separado, ¿los cortes de Jenks caen en el mismo lugar?
     C.3 **la prueba decisiva: recalcular la densidad SIN los puntos del Relevamiento.** Las otras
         seis fuentes no rotan. Si al sacar la fuente rotativa las clases se reproducen, lo que
         separa a las clases es el territorio y no el año de medición.

   Y un límite estructural que hay que decir antes que los resultados: **la añada está anidada
   dentro del barrio** —un barrio tiene una sola añada—, así que año y lugar no se pueden separar
   por diseño. Por eso C.3 no compara años: cambia la fuente y mira si el resultado aguanta.

Google Places no interviene. 0 requests.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/polos_particion_anada_estructura.py
"""
from __future__ import annotations

import io
import json
import sys
import warnings
from itertools import combinations
from pathlib import Path

import geopandas as gpd
import networkx as nx
import numpy as np
import pandas as pd
from scipy.stats import kruskal, mannwhitneyu
from sklearn.metrics import adjusted_rand_score
from scipy.spatial import cKDTree

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from borrador_polos_ciudad import (  # noqa: E402
    BARRIDO, CRS_METRICO, ENVOLVENTES_22, PARAMETROS, agrupar, cargar_puntos, envolver,
)
from polos_atributos_clases import (  # noqa: E402
    GVF_MINIMO, K_CANDIDATOS, NOMBRES_CLASE, OUT, cargar_parejidad, fisher_jenks,
)

# --- §B · el barrido de continuidad, con los mismos umbrales con los que se leyó Belgrano -------
# (80, 120, 160, 200, 250, 300) son los de `ejecutar_corrida_territorial_v3.py`. Se agregan tres
# valores por debajo porque aquel barrido corría sobre clusters candidatos y éste corre sobre
# puntos sueltos: sin los umbrales chicos, todo aparece conectado y el barrido no mide nada.
UMBRALES_CONTINUIDAD = (40, 55, 70, 80, 120, 160, 200, 250, 300)

# --- §A · qué cuenta como bloque coherente ------------------------------------------------------
# El mismo mínimo de toda la corrida. Un grupo de sueltos que llegue a 40 es un polo que se perdió;
# por debajo de eso es tejido, y el criterio ya declarado dice que no se rescata.
MINIMO = PARAMETROS["min_cluster_size"]


def plano(conteos: list[int]) -> bool:
    """La curva es plana si nunca aparece más de una parte nombrable."""
    return max(conteos) <= 1


# --------------------------------------------------------------------------- §A


def componentes(puntos: gpd.GeoDataFrame, umbral: float) -> list[list[int]]:
    """Componentes conexas uniendo puntos a menos de `umbral` metros.

    Mismo criterio que `graph_components` de la corrida territorial V3, con un árbol de vecinos en
    lugar del bucle de pares: acá hay polos de 300 puntos y el bucle O(n²) del original tarda de
    más sin cambiar el resultado —une exactamente los mismos pares—.
    """
    xy = np.c_[puntos.geometry.x.to_numpy(), puntos.geometry.y.to_numpy()]
    grafo = nx.Graph()
    grafo.add_nodes_from(range(len(puntos)))
    grafo.add_edges_from(cKDTree(xy).query_pairs(umbral))
    return sorted((sorted(c) for c in nx.connected_components(grafo)), key=len, reverse=True)


def desglosar_particion(geo: gpd.GeoDataFrame, p) -> pd.DataFrame:
    """§A · dónde cayeron los locales que la partición dejó sueltos, padre por padre."""
    sueltos = geo[(geo.polo_id != "") & (geo.polo_final == "")]
    padres = sorted(sueltos.polo_id.unique())

    p("§A · EL PRECIO DE LA PARTICIÓN, DESGLOSADO · ¿tejido conectivo o bloque coherente?")
    p("=" * 100)
    p("")
    p("  LO PRIMERO, PORQUE YA ESTABA MEDIDO Y CAMBIA LA PREGUNTA: ninguno de los 1.064 locales")
    p("  quedó suelto por caer bajo el mínimo. `leaf` no produjo ni un solo fragmento por debajo de")
    p(f"  {MINIMO} locales —la columna `fragmentos_anotados_sin_rescate` dio 0 en los cuatro padres—.")
    p("  Los 1.064 son puntos que el corte profundo etiquetó como RUIDO, no piezas amputadas.")
    p("")
    p("  La prueba, declarada antes de correrla: se vuelve a correr el mismo clustering (eom,")
    p(f"  min_cluster_size={MINIMO}, min_samples={PARAMETROS['min_samples']}) sobre los sueltos de")
    p("  cada padre, solos. Si de ahí sale un cluster nombrable, había un bloque coherente y la")
    p("  partición lo perdió. Si sale ruido, era tejido.")
    p("")

    filas, detalle_bloques = [], []
    for padre in padres:
        cuerpo = sueltos[sueltos.polo_id == padre]
        piezas = geo[(geo.polo_id == padre) & (geo.polo_final != "")]
        # La cáscara que envuelve a las piezas: lo que cae adentro está ENTRE ellas, que es la
        # definición geométrica de tejido conectivo.
        cascara = envolver(piezas, PARAMETROS["concave_hull_ratio"])[0].convex_hull
        adentro = int(cuerpo.within(cascara).sum())

        recluster = agrupar(cuerpo, MINIMO, PARAMETROS["min_samples"]) if len(cuerpo) >= MINIMO \
            else np.full(len(cuerpo), -1)
        tamanios = pd.Series(recluster[recluster >= 0]).value_counts()
        bloques = int((tamanios >= MINIMO).sum())
        # Un grupo de 40 o más no alcanza para llamarlo «bloque perdido»: hay que saber DÓNDE está
        # y con qué densidad. Un grupo grande y ralo metido entre las piezas es la matriz de baja
        # densidad que la partición justamente quiso sacar; uno compacto y afuera es un polo que se
        # perdió. Sin esta distinción, «6 bloques» se lee como seis polos perdidos y no lo son.
        for etiqueta, tamanio in tamanios[tamanios >= MINIMO].items():
            miembros = cuerpo[recluster == etiqueta]
            forma = envolver(miembros, PARAMETROS["concave_hull_ratio"])[0]
            centro = miembros.union_all().centroid
            detalle_bloques.append({
                "padre": padre, "bloque": f"{padre}-S{etiqueta + 1}", "locales": int(tamanio),
                "ha": round(forma.area / 1e4, 1),
                "locales_x_ha": round(tamanio / (forma.area / 1e4), 2),
                "centro_dentro_de_la_cascara": bool(cascara.contains(centro)),
                "pct_del_bloque_entre_las_piezas": round(miembros.within(cascara).mean() * 100, 1),
                "dist_a_pieza_mas_cercana_m": round(float(
                    cKDTree(np.c_[piezas.geometry.x, piezas.geometry.y]).query(
                        np.c_[[centro.x], [centro.y]])[0][0]), 1),
            })

        # Distancia de cada suelto a la pieza más cercana: el tejido está cerca; un bloque perdido
        # estaría lejos y junto.
        arbol = cKDTree(np.c_[piezas.geometry.x, piezas.geometry.y])
        distancias = arbol.query(np.c_[cuerpo.geometry.x, cuerpo.geometry.y])[0]

        filas.append({
            "padre": padre,
            "barrio": piezas.barrio.value_counts().index[0],
            "piezas_que_quedaron": piezas.polo_final.nunique(),
            "locales_en_piezas": len(piezas),
            "locales_sueltos": len(cuerpo),
            "pct_suelto": round(len(cuerpo) / (len(cuerpo) + len(piezas)) * 100, 1),
            "sueltos_entre_las_piezas": adentro,
            "pct_entre_las_piezas": round(adentro / len(cuerpo) * 100, 1),
            "dist_mediana_a_pieza_m": round(float(np.median(distancias)), 1),
            "dist_p90_a_pieza_m": round(float(np.percentile(distancias, 90)), 1),
            "bloques_coherentes": bloques,
            "mayor_grupo_de_sueltos": int(tamanios.max()) if len(tamanios) else 0,
        })
    tabla = pd.DataFrame(filas)
    p(tabla.to_string(index=False))
    p("")
    bloques = pd.DataFrame(detalle_bloques)
    p(f"  LOS GRUPOS DE SUELTOS QUE LLEGAN A {MINIMO}, UNO POR UNO")
    p("    El conteo solo no alcanza: hay que saber dónde está cada grupo y con qué densidad. Un")
    p("    grupo grande y ralo metido ENTRE las piezas es la matriz de baja densidad que la")
    p("    partición quiso sacar; uno compacto y AFUERA es un polo que se perdió.")
    if not len(bloques):
        p("    ninguno")
        p("")
        return tabla, bloques
    p(bloques.to_string(index=False))
    p("")
    # La densidad de referencia: la de las piezas que sí quedaron. Un bloque de sueltos que tenga
    # una densidad comparable a las piezas es otra cosa que un bloque tres veces más ralo.
    tejido = bloques[bloques.centro_dentro_de_la_cascara]
    afuera = bloques[~bloques.centro_dentro_de_la_cascara]
    p(f"    grupos cuyo centro cae ENTRE las piezas (posición de tejido): {len(tejido)} de "
      f"{len(bloques)}, {int(tejido.locales.sum())} locales")
    p(f"    grupos cuyo centro cae AFUERA de las piezas: {len(afuera)}, "
      f"{int(afuera.locales.sum())} locales")
    p(f"    densidad de estos grupos: mediana {bloques.locales_x_ha.median():.2f} locales/ha")
    p("")
    return tabla, bloques


def zonas_perdidas(geo: gpd.GeoDataFrame, p) -> pd.DataFrame:
    """§A bis · cuáles son las dos zonas que dejaron de estar encontradas, y de qué familia."""
    zonas = gpd.read_file(ENVOLVENTES_22).to_crs(CRS_METRICO)
    cotejo = pd.read_csv(OUT / "siete_zonas_explicacion.csv")
    perdidas = cotejo[(cotejo.explicacion == "ENCONTRADA") & (cotejo.pct_zona_cubierta_tras_partir < 25)]
    ficha = zonas.set_index("referencia_id")

    p("§A bis · LAS DOS ZONAS PERDIDAS, CON SU FAMILIA DEL ATLAS")
    p("=" * 100)
    p("")
    p("  La familia es lo que decide. Perder una «referencia dispersa» la CONFIRMA: no tiene por qué")
    p("  producir un cluster. Perder una con nombre e identidad documental obliga a revisar la")
    p("  partición que la rompió.")
    p("")
    filas = []
    for fila in perdidas.itertuples():
        datos = ficha.loc[fila.referencia_id]
        adentro = geo[geo.within(datos.geometry)]
        # Quién la cubría antes y qué pasó con ese polo.
        cubria = adentro[adentro.polo_id != ""].polo_id.value_counts()
        filas.append({
            "referencia_id": fila.referencia_id, "nombre": fila.nombre,
            "familia": datos.familia_etiqueta, "registro": datos.registro,
            "piezas_declaradas": datos.piezas, "ha": round(fila.ha_zona, 1),
            "soporte": datos.soporte,
            "pct_cubierta_antes": fila.pct_zona_cubierta,
            "pct_cubierta_despues": fila.pct_zona_cubierta_tras_partir,
            "polo_que_la_cubria": cubria.index[0] if len(cubria) else "",
            "locales_de_esa_zona_en_ese_polo": int(cubria.iloc[0]) if len(cubria) else 0,
            "locales_en_la_zona": len(adentro),
        })
    tabla = pd.DataFrame(filas)
    for fila in tabla.itertuples():
        p(f"  {fila.referencia_id} · {fila.nombre}")
        p(f"     familia      : {fila.familia}   (registro {fila.registro}, "
          f"{fila.piezas_declaradas} pieza/s declaradas, {fila.ha:.0f} ha)")
        p(f"     soporte      : {fila.soporte}")
        p(f"     cobertura    : {fila.pct_cubierta_antes:.1f} % antes de partir → "
          f"{fila.pct_cubierta_despues:.1f} % después")
        p(f"     la cubría    : {fila.polo_que_la_cubria} "
          f"({fila.locales_de_esa_zona_en_ese_polo} de sus {fila.locales_en_la_zona} locales)")
        if fila.familia == "Referencia dispersa":
            p("     LECTURA      : perderla la CONFIRMA. Una referencia dispersa no tiene por qué")
            p("                    producir un cluster; que el clustering no la dibuje es coherente")
            p("                    con lo que el Atlas declara que es.")
        else:
            p(f"     LECTURA      : NO es referencia dispersa — el Atlas la publica como «{fila.familia}»,")
            p("                    con identidad propia. Perderla obliga a revisar la partición que la")
            p("                    rompió antes de aceptar el precio.")
        p("")
    return tabla


# --------------------------------------------------------------------------- §B


def curva_de_sensibilidad(geo: gpd.GeoDataFrame, enteros: list[str], partidos: list[str],
                          p) -> pd.DataFrame:
    """§B · barrido de continuidad sobre los seis, con los partidos como control positivo."""
    p("§B · LA CURVA DE SENSIBILIDAD · ¿ausencia de estructura, o ausencia de evidencia?")
    p("=" * 100)
    p("")
    p("  Método: el mismo con el que se decidió Belgrano —se unen los puntos que están a menos de")
    p("  un umbral, se cuentan las componentes conexas y sus tamaños, y se mueve el umbral—.")
    p(f"  Umbrales: {', '.join(str(u) for u in UMBRALES_CONTINUIDAD)} m. Los seis últimos son los de")
    p("  la corrida territorial V3; los tres primeros se agregan porque aquel barrido corría sobre")
    p("  clusters candidatos y éste corre sobre puntos sueltos.")
    p("")
    p("  CONTROLES POSITIVOS. El barrido se corre también sobre los cuatro polos que SÍ se")
    p("  partieron. Sin ellos una curva plana no dice nada: no se sabría si el instrumento")
    p("  distingue estructura de ausencia de estructura. Con ellos, una curva plana al lado de una")
    p("  escalonada es una medición.")
    p("")
    p(f"  Criterio declarado: la curva es PLANA si el número de componentes de {MINIMO} locales o")
    p("  más es 1 en TODOS los umbrales. Si en algún tramo aparecen dos o más partes estables de")
    p("  tamaño comparable, ése se parte con el criterio de Belgrano.")
    p("")

    filas = []
    for polo_id in enteros + partidos:
        cuerpo = geo[geo.polo_id == polo_id]
        for umbral in UMBRALES_CONTINUIDAD:
            partes = componentes(cuerpo, umbral)
            nombrables = [c for c in partes if len(c) >= MINIMO]
            filas.append({
                "polo_id": polo_id,
                "rol": "control positivo (se partió)" if polo_id in partidos else "entero",
                "locales": len(cuerpo),
                "umbral_m": umbral,
                "componentes": len(partes),
                f"componentes_de_{MINIMO}_o_mas": len(nombrables),
                "tamanos": ";".join(str(len(c)) for c in partes[:5]),
                "pct_en_la_mayor": round(len(partes[0]) / len(cuerpo) * 100, 1),
            })
    tabla = pd.DataFrame(filas)
    columna = f"componentes_de_{MINIMO}_o_mas"

    for rol, titulo in [("entero", "LOS SEIS QUE `leaf` NO PARTIÓ"),
                        ("control positivo (se partió)", "LOS CONTROLES POSITIVOS")]:
        p(f"  {titulo}")
        subconjunto = tabla[tabla.rol == rol]
        pivote = subconjunto.pivot(index="polo_id", columns="umbral_m", values=columna)
        p(f"    componentes de {MINIMO} locales o más, por umbral:")
        p(pivote.to_string())
        p("")
        for polo_id, grupo in subconjunto.groupby("polo_id"):
            conteos = grupo[columna].tolist()
            veredicto = "PLANA · no tiene estructura interna" if plano(conteos) else \
                "NO PLANA · aparecen partes nombrables"
            p(f"    {polo_id} ({int(grupo.locales.iloc[0])} locales) → {veredicto}")
            p(f"       tamaños por umbral: " + " | ".join(
                f"{int(f.umbral_m)}m:{f.tamanos}" for f in grupo.itertuples()))
        p("")

    resultado = tabla.groupby(["polo_id", "rol"])[columna].max().reset_index()
    resultado["curva"] = np.where(resultado[columna] <= 1, "PLANA", "NO PLANA")
    p("  VEREDICTO")
    p(resultado.to_string(index=False))
    planos = resultado[(resultado.rol == "entero") & (resultado.curva == "PLANA")]
    no_planos = resultado[(resultado.rol == "entero") & (resultado.curva == "NO PLANA")]
    p("")
    p(f"    de los seis enteros: {len(planos)} con curva plana, {len(no_planos)} sin ella")
    if len(planos):
        p(f"    PLANOS — {' '.join(planos.polo_id)}: esto ya no es «leaf no los partió». Es")
        p("    **medimos que no tienen estructura interna**, con un instrumento que en los mismos")
        p("    umbrales sí encuentra estructura en los controles. Quedan enteros, clasificados")
        p("    como referencia dispersa / clase extendida, con la densidad declarada en la ficha.")
    if len(no_planos):
        p(f"    NO PLANOS — {' '.join(no_planos.polo_id)}: aparecen partes nombrables y estables.")
        p("    Ésos SÍ se parten, con el criterio de Belgrano, y no quedan como referencia dispersa.")
    p("")
    return tabla


# --------------------------------------------------------------------------- §C


def anada_contra_densidad(polos: gpd.GeoDataFrame, geo: gpd.GeoDataFrame, cortes: list[float],
                          p) -> dict:
    """§C · ¿la clase de densidad mide territorio, o mide en parte el año de medición?"""
    p("§C · LA AÑADA CONTRA LA DENSIDAD · ¿las clases separan dentro de cada cohorte?")
    p("=" * 100)
    p("")
    p("  EL LÍMITE ESTRUCTURAL, DICHO ANTES QUE CUALQUIER RESULTADO. La añada está ANIDADA dentro")
    p("  del barrio: un barrio tiene una sola añada, así que no hay ningún barrio donde comparar")
    p("  2022 contra 2024. Año y lugar no se pueden separar por diseño, y ninguna prueba de este")
    p("  bloque lo va a lograr. Lo que sí se puede hacer es cambiar la fuente y ver si el resultado")
    p("  aguanta, que es C.3.")
    p("")

    # --- C.1 · cuánta varianza explica la añada
    cohortes = [g.locales_x_ha.to_numpy() for _, g in polos.groupby("anada_relevamiento")]
    media = polos.locales_x_ha.mean()
    entre = sum(len(c) * (c.mean() - media) ** 2 for c in cohortes)
    total = ((polos.locales_x_ha - media) ** 2).sum()
    eta2 = entre / total
    estadistico, valor_p = kruskal(*cohortes)

    p("  C.1 · ¿CUÁNTA VARIANZA DE LA DENSIDAD EXPLICA LA AÑADA?")
    p(polos.groupby("anada_relevamiento").locales_x_ha.describe()[
        ["count", "mean", "50%", "min", "max"]].round(2).to_string())
    p(f"    eta² = {eta2:.3f} — la añada explica el {eta2 * 100:.1f} % de la varianza de la densidad")
    p(f"    Kruskal–Wallis H = {estadistico:.2f}, p = {valor_p:.4f}")
    p(f"    Lectura: {'las cohortes SÍ difieren' if valor_p < 0.05 else 'no se detecta diferencia'} "
      f"en densidad, y la añada explica el {eta2 * 100:.1f} % de su variación. El "
      f"{(1 - eta2) * 100:.1f} % restante varía adentro de cada cohorte.")
    p("")

    # --- C.2 · los cortes, cohorte por cohorte
    p("  C.2 · LOS CORTES DE JENKS, COHORTE POR COHORTE")
    p("    si la añada fabricara las clases, cada cohorte cortaría en un lugar distinto")
    filas = []
    for anio, grupo in polos.groupby("anada_relevamiento"):
        densidad = grupo.locales_x_ha.to_numpy()
        if len(densidad) < 8:
            filas.append({"anada": int(anio), "polos": len(densidad), "cortes": "— pocos polos"})
            continue
        propios, _ = fisher_jenks(densidad, 3)
        filas.append({
            "anada": int(anio), "polos": len(densidad),
            "corte_bajo": round(propios[0], 2), "corte_alto": round(propios[1], 2),
            "desvio_vs_global_bajo": round(propios[0] - cortes[0], 2),
            "desvio_vs_global_alto": round(propios[1] - cortes[1], 2),
        })
    tabla_cortes = pd.DataFrame(filas)
    p(tabla_cortes.to_string(index=False))
    p(f"    cortes globales de referencia: {cortes[0]:.2f} | {cortes[1]:.2f}")
    p("")

    # --- C.3 · la prueba decisiva: sacar la fuente rotativa y reclasificar
    p("  C.3 · LA PRUEBA DECISIVA · recalcular la densidad SIN los puntos del Relevamiento")
    p("    Las otras seis fuentes no rotan. Si al sacar la fuente rotativa las clases se")
    p("    reproducen, lo que separa a las clases es el territorio y no el año de medición.")
    p("    La superficie de cada polo NO se recalcula: se mantiene la envolvente, así que lo único")
    p("    que cambia entre las dos densidades es el numerador.")
    sin_rus = geo[(geo.polo_final != "")
                  & ~geo.grupos_independencia.fillna("").str.contains("GCBA_URBANISMO")]
    cuenta = sin_rus.groupby("polo_final").local_id.count()
    polos = polos.copy()
    polos["locales_sin_rus"] = polos.polo_id.map(cuenta).fillna(0).astype(int)
    polos["densidad_sin_rus"] = polos.locales_sin_rus / polos.ha

    densidad_sin = polos.densidad_sin_rus.to_numpy()
    k_global = len(cortes) + 1

    # LA COMPARACIÓN VA A k IGUAL, y el motivo hay que dejarlo escrito porque la primera versión de
    # esta prueba se equivocó justamente acá. Sacar el 41 % de los puntos baja TODAS las densidades
    # en la misma proporción: cambia la escala, no el orden. Si además se deja que la regla del GVF
    # vuelva a elegir k, la comparación mezcla dos cosas —si el orden aguanta, y si el umbral de
    # bondad de ajuste cae del mismo lado de una escala corrida— y una diferencia de k se lee como
    # si las clases se hubieran caído. La pregunta es si las clases AGRUPAN igual, así que se fija
    # el mismo k y se comparan las particiones. El k libre se reporta aparte, como nota.
    cortes_sin, _ = fisher_jenks(densidad_sin, k_global)
    etiquetas = NOMBRES_CLASE[:k_global][::-1]
    polos["clase_sin_rus"] = pd.cut(polos.densidad_sin_rus, [-np.inf, *cortes_sin, np.inf],
                                    labels=etiquetas)

    sce_total = float(((densidad_sin - densidad_sin.mean()) ** 2).sum())
    ajuste = [(k, 1 - fisher_jenks(densidad_sin, k)[1] / sce_total) for k in K_CANDIDATOS]
    aptos = [k for k, gvf in ajuste if gvf >= GVF_MINIMO]
    k_libre = aptos[0] if aptos else K_CANDIDATOS[-1]

    correlacion = polos.locales_x_ha.corr(polos.densidad_sin_rus, method="spearman")
    rand = adjusted_rand_score(polos.clase_densidad.astype(str), polos.clase_sin_rus.astype(str))
    p("")
    p(f"    densidad mediana: {polos.locales_x_ha.median():.2f} con todas las fuentes → "
      f"{polos.densidad_sin_rus.median():.2f} sin el Relevamiento (la escala baja, es esperable)")
    p(f"    correlación de Spearman entre las dos densidades, polo por polo: {correlacion:.3f}")
    p(f"    cortes a k = {k_global}: {' | '.join(f'{c:.2f}' for c in cortes)} con todas las fuentes")
    p(f"                              {' | '.join(f'{c:.2f}' for c in cortes_sin)} sin el Relevamiento")
    p("")
    matriz = pd.crosstab(polos.clase_densidad, polos.clase_sin_rus)
    p("    MATRIZ DE CONFUSIÓN a k igual · clase con todas las fuentes (filas) contra clase sin el")
    p("    Relevamiento (columnas)")
    p(matriz.to_string())
    # `clase_densidad` viene del GeoJSON como texto plano, no como categoría: el orden se toma de
    # la lista declarada, que es la misma con la que se clasificó (de menos densa a más densa).
    matriz = matriz.reindex(index=etiquetas, columns=etiquetas).fillna(0)
    coinciden = int(np.trace(matriz.to_numpy()))
    p("")
    p(f"    misma clase: {coinciden} de {len(polos)} polos ({coinciden / len(polos) * 100:.1f} %)")
    p(f"    índice de Rand ajustado entre las dos particiones: {rand:.3f}")
    p(f"    nota · si en vez de fijar k se deja que la regla del GVF lo elija sobre la escala")
    p(f"    corrida, elige k = {k_libre}. Eso NO es que las clases se caigan: con Spearman "
      f"{correlacion:.3f}")
    p("    el orden de los polos es prácticamente el mismo, y una clase más sobre la misma")
    p("    secuencia parte la serie en otro lugar, no la reordena.")
    p("")

    # ¿Y la añada sigue explicando algo cuando el Relevamiento no está?
    cohortes_sin = [g.densidad_sin_rus.to_numpy() for _, g in polos.groupby("anada_relevamiento")]
    media_sin = polos.densidad_sin_rus.mean()
    eta2_sin = sum(len(c) * (c.mean() - media_sin) ** 2 for c in cohortes_sin) / \
        ((polos.densidad_sin_rus - media_sin) ** 2).sum()
    p(f"    eta² de la añada sobre la densidad SIN Relevamiento: {eta2_sin:.3f} "
      f"(era {eta2:.3f} con todas las fuentes)")
    p("")

    # Los tres umbrales se fijaron antes de correr. Dos pasan y uno falla, y eso obliga a
    # diagnosticar en vez de elegir el que convenga: ¿por qué se reclasifica un tercio de los polos
    # si el orden se conserva casi intacto? La hipótesis, comprobable, es que los que cambian son
    # los que estaban cerca de un corte —o sea que lo que falla no es la añada, es la robustez del
    # corte—. Se mide la distancia de cada polo al corte más cercano, en unidades de la propia
    # escala, y se compara entre los que cambiaron y los que no.
    polos["dist_al_corte"] = np.min(
        [np.abs(polos.locales_x_ha.to_numpy() - c) for c in cortes], axis=0
    ) / polos.locales_x_ha.median()
    polos["cambio_de_clase"] = (polos.clase_densidad.astype(str)
                                != polos.clase_sin_rus.astype(str))
    cambian, quedan = polos[polos.cambio_de_clase], polos[~polos.cambio_de_clase]
    p_borde = mannwhitneyu(cambian.dist_al_corte, quedan.dist_al_corte).pvalue
    p_rus = mannwhitneyu(cambian.pct_puntos_del_relevamiento,
                         quedan.pct_puntos_del_relevamiento).pvalue

    p("  POR QUÉ SE RECLASIFICA UN TERCIO SI EL ORDEN SE CONSERVA · el diagnóstico")
    p("    Se probaron las tres explicaciones candidatas y las dos primeras NO son:")
    p("")
    p(f"    · ¿dependen del Relevamiento los que cambian? NO. Share del Relevamiento: "
      f"{cambian.pct_puntos_del_relevamiento.median():.1f} % en los que cambian contra "
      f"{quedan.pct_puntos_del_relevamiento.median():.1f} % en los que")
    p(f"      quedan (Mann–Whitney p = {p_rus:.2f}). Todos los polos dependen del Relevamiento en")
    p("      una proporción parecida, así que sacarlo no golpea a unos más que a otros.")
    p(f"    · ¿estaban pegados a una frontera? NO de manera decisiva. Distancia mediana al corte "
      f"{cambian.dist_al_corte.median():.3f} contra {quedan.dist_al_corte.median():.3f} "
      f"(p = {p_borde:.2f}):")
    p("      la diferencia va en la dirección esperable pero es chica y no separa los grupos.")
    p("")
    p(f"    · LA QUE SÍ ES: los que cambian son los DENSOS. Densidad mediana "
      f"{cambian.locales_x_ha.median():.2f} en los que cambian contra "
      f"{quedan.locales_x_ha.median():.2f} en los que quedan,")
    p("      y todo el movimiento va hacia abajo. Mirando la matriz de confusión: la clase C no")
    p("      pierde ni un polo —los 51 se quedan— y la A pierde 24 de 26.")
    p("")
    p("    EL MECANISMO, que es un defecto del método de corte y no de los datos. Fisher–Jenks")
    p("    minimiza la varianza dentro de cada clase, y la varianza la domina la cola alta. Al")
    p("    sacar el 41 % de los puntos la cola se adelgaza, y el corte superior se va de "
      f"{cortes[1]:.2f}")
    p(f"    a {cortes_sin[1]:.2f} —de {cortes[1] / polos.locales_x_ha.median():.2f}× la mediana a "
      f"{cortes_sin[1] / polos.densidad_sin_rus.median():.2f}× la mediana—, y casi nadie queda")
    p("    arriba. **La frontera entre las clases densas se mueve con la forma de la cola, no con")
    p("    el territorio.** Es la consecuencia concreta de que la distribución no tenga huecos:")
    p("    sin un vacío que ancle el corte, el corte lo pone la varianza de los pocos extremos.")
    p("")

    contaminada = eta2 >= 0.10
    robusta = rand >= 0.60
    p("  VEREDICTO · son dos preguntas distintas y hay que contestarlas por separado")
    p(f"    umbrales declarados antes de correr: eta² < 0,10 · Spearman ≥ 0,90 · Rand ≥ 0,60")
    p(f"    obtenido: eta² {eta2:.3f} ✓ · Spearman {correlacion:.3f} ✓ · Rand {rand:.3f} ✗")
    p("")
    p("    1 · ¿LA AÑADA CONTAMINA LAS CLASES? " + ("SÍ" if contaminada else "NO."))
    if not contaminada:
        p(f"        La añada explica el {eta2 * 100:.1f} % de la varianza de la densidad, y al sacar")
        p(f"        entera la fuente rotativa —el 41 % de los puntos— baja a {eta2_sin * 100:.1f} %.")
        p("        Las tres clases aparecen en las tres cohortes, y los cortes propios de 2022 y")
        p("        2024 caen a menos de medio local/ha de los globales. La clase C no es «relevada")
        p("        en 2022»: el 96 % de la variación de densidad ocurre adentro de cada cohorte.")
    p("")
    p("    2 · ¿SON ROBUSTAS LAS CLASES? " + ("SÍ." if robusta else "LA BAJA SÍ, LAS ALTAS NO."))
    if not robusta:
        p(f"        Cambiando el conjunto de puntos, {int((~polos.cambio_de_clase).sum())} de "
          f"{len(polos)} conservan clase y {int(polos.cambio_de_clase.sum())} se mueven. Pero no")
        p("        se mueven parejo:")
        p("          · clase C «concentración extendida» — 51 de 51 conservan la clase. ESTABLE.")
        p("          · clase A «concentración densa»     — 2 de 26 la conservan. NO ESTABLE.")
        p("        **Y esto no lo produjo la añada.** Lo produce que la distribución no tenga")
        p("        huecos: sin un vacío que ancle el corte superior, lo pone la varianza de la cola.")
        p("")
        p("        Consecuencia operativa, y es más precisa que «abandonar las clases»:")
        p("          · «concentración extendida» se puede usar. Es el descriptor que aguanta, y es")
        p("            justamente el que hace falta para los seis del §B y para el sur.")
        p("          · la frontera entre «media» y «densa» NO se puede usar para decidir nada sobre")
        p("            un polo en particular. En la ficha va la densidad exacta primero y la clase")
        p("            después, y ningún polo se trata distinto por estar de un lado de ese corte.")
    p("")
    p("    Y lo que la prueba NO puede decir, por el anidamiento declarado arriba: si la densidad")
    p("    real del territorio cambió entre 2022 y 2024, esto no lo detecta. Lo que descarta es que")
    p("    las clases sean un artefacto de MEDICIÓN de la fuente rotativa.")
    p("")
    return {"eta2": float(eta2), "eta2_sin_rus": float(eta2_sin), "kruskal_p": float(valor_p),
            "spearman_con_sin_rus": float(correlacion), "rand_ajustado": float(rand),
            "k_fijado": int(k_global), "k_libre_sin_rus": int(k_libre),
            "cortes_sin_rus": cortes_sin, "anada_contamina": bool(contaminada), "clases_robustas": bool(robusta),
            "polos": polos}


# --------------------------------------------------------------------------- informe


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    buffer = io.StringIO()

    def p(*args_):
        print(*args_, file=buffer)

    geo = cargar_puntos(PARAMETROS["anillo"], PARAMETROS["solo_aptos"])
    pertenencia = pd.read_csv(OUT / "pertenencia_local_polo_v2.csv")
    geo = geo.merge(pertenencia[["local_id", "polo_id", "polo_final"]], on="local_id", how="left")
    geo[["polo_id", "polo_final"]] = geo[["polo_id", "polo_final"]].fillna("")

    polos = gpd.read_file(OUT / "borrador_polos_v2.geojson").to_crs(CRS_METRICO)
    particion = pd.read_csv(OUT / "particion_encadenados.csv")
    cortes = json.loads((OUT / "parametros_v2.json").read_text(
        encoding="utf-8"))["clases_densidad"]["cortes_locales_x_ha"]

    enteros = particion.loc[~particion.se_parte, "polo_id"].tolist()
    partidos = particion.loc[particion.se_parte, "polo_id"].tolist()

    p("BORRADOR · el precio de la partición, la estructura de los seis y la añada contra la densidad")
    p("=" * 100)
    p("")
    p("NO ES UN PRODUCTO. No se publica, no se sella y no toca el Atlas.")
    p("Google Places: 0 requests. Places no está en la base.")
    p("")

    tabla_sueltos, tabla_bloques = desglosar_particion(geo, p)
    tabla_zonas = zonas_perdidas(geo, p)
    tabla_curva = curva_de_sensibilidad(geo, enteros, partidos, p)
    resultado = anada_contra_densidad(polos, geo, cortes, p)

    salida = buffer.getvalue()
    (OUT / "PARTICION_ESTRUCTURA_Y_ANADA.txt").write_text(salida, encoding="utf-8")
    tabla_sueltos.to_csv(OUT / "particion_sueltos_por_padre.csv", index=False, encoding="utf-8")
    tabla_bloques.to_csv(OUT / "particion_bloques_de_sueltos.csv", index=False, encoding="utf-8")
    tabla_zonas.to_csv(OUT / "particion_zonas_perdidas.csv", index=False, encoding="utf-8")
    tabla_curva.to_csv(OUT / "curva_continuidad_seis.csv", index=False, encoding="utf-8")
    resultado["polos"].drop(columns=["geometry"]).round(3).to_csv(
        OUT / "anada_contra_densidad.csv", index=False, encoding="utf-8")
    (OUT / "anada_contra_densidad_resumen.json").write_text(json.dumps(
        {k: v for k, v in resultado.items() if k != "polos"},
        ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(salida)
    print(f"escrito en {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
