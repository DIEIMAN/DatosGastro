"""P065 rehecho, el precio final, las clases a dos y la unión a 100 m. BORRADOR — no se publica.

§1 · P065 SE REHACE, NO SE REVIERTE
   Una partición de Palermo que deja afuera dos concentraciones de 70 y 59 locales a 5,96 y 5,39
   locales/ha —por encima de la mediana global de 5,03— no es una partición a la que le falta un
   remiendo: es una mala partición. Se rehace con el instrumento que ya decidió Belgrano, el
   barrido de continuidad, en vez de con `leaf`.

   REGLA DECLARADA ANTES DE MIRAR EL RESULTADO: se toma el umbral MÁS ALTO en el que todavía
   existan dos o más componentes de tamaño nombrable (≥ min_cluster_size). El más alto y no el
   más bajo, y el motivo es que es el conservador: cuanto más alto el umbral, más une, así que el
   más alto que todavía separa es el que menos fragmenta. Bajar el umbral hasta que aparezcan las
   partes que uno quiere ver es exactamente cómo se fabrica una partición a medida.

   Y se verifica contra tres cosas que NO se usaron para elegir el umbral: si las piezas capturan
   los dos bloques que la partición vieja perdió, si R19 vuelve por encima del umbral de cotejo, y
   si alguna pieza queda por debajo del mínimo.

§2 · EL PRECIO FINAL, con P018/P025/P072 aceptados y P065 rehecho.

§3 · LAS CLASES PASAN DE TRES A DOS
   La frontera densa/media no existe: al cambiar el conjunto de puntos, la clase C conserva 51 de
   51 y la A conserva 2 de 26. Publicar tres clases cuando una frontera se sostiene siempre y la
   otra casi nunca es publicar ruido con nombre. Quedan «concentración extendida» (la C estable) y
   «concentración» (el resto). **El corte NO se recalcula**: se usa el mismo 4,58 ya declarado, que
   es justamente la frontera que aguantó. Refitear acá sería cambiar la frontera que se conserva
   porque se borró la otra.

§4 · UNIÓN A 100 M, Y NO ES TRANSITIVA
   El umbral de unión pasa de 50 a 100 m. Pero **la unión a 100 m no se aplica de forma transitiva
   y ciega**: A con B a 90 m y B con C a 90 m encadenaría A con C aunque estén a 500, que es
   exactamente el problema que se acaba de arreglar partiendo. Así que cada unión candidata se
   evalúa SOBRE EL RESULTADO UNIDO, y las uniones se aplican de a una: cuando dos polos se unen, la
   candidata siguiente que los toque se evalúa contra el objeto ya unido, no contra las partes.

   Dos pruebas sobre el objeto unido, las dos declaradas antes de correr:
     · CONTINUIDAD  · los puntos de los dos polos juntos tienen que formar UNA sola componente
                      conexa a 100 m. Si a 100 m siguen siendo dos cuerpos, el hueco entre ellos
                      no lo cierra la oferta y unirlos es dibujar un puente que no existe.
     · ESTABILIDAD  · el objeto unido tiene que sobrevivir al mismo instrumento que parte. Si
                      `leaf` sobre el unido lo vuelve a separar en dos piezas nombrables, entonces
                      **no se une lo que la partición volvería a separar**. Es la misma vara para
                      las dos operaciones, y sin eso unir y partir se contradirían.

Google Places no interviene. 0 requests.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/polos_p065_union_y_clases.py
"""
from __future__ import annotations

import io
import json
import sys
import warnings
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from sklearn.metrics import adjusted_rand_score

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from borrador_polos_ciudad import (  # noqa: E402
    CRS_GEO, CRS_METRICO, ENVOLVENTES_22, PARAMETROS, agrupar, cargar_base_completa,
    cargar_puntos, construir_polos, control_aptitud, plegar,
)
from polos_atributos_clases import (  # noqa: E402
    COBERTURA_MINIMA_ZONA, OUT, SUPERFICIE_CIUDAD_HA, cargar_parejidad, fisher_jenks,
)
from polos_particion_anada_estructura import (  # noqa: E402
    MINIMO, UMBRALES_CONTINUIDAD, componentes,
)

POLO_A_REHACER = "P065"
METODO_PARTICION = "leaf"

# §3 · el corte que se conserva es el que aguantó la prueba de robustez. No se recalcula.
CLASE_EXTENDIDA = "concentración extendida"
CLASE_CONCENTRACION = "concentración"

# §4 · el umbral de unión, y las dos pruebas sobre el objeto unido
UMBRAL_UNION_M = 100.0


# --------------------------------------------------------------------------- §1


def rehacer_p065(geo: gpd.GeoDataFrame, bloques: pd.DataFrame, zonas: gpd.GeoDataFrame,
                 p) -> dict:
    """§1 · P065 partido con el barrido de continuidad, no con `leaf`."""
    cuerpo = geo[geo.polo_id == POLO_A_REHACER]

    p(f"§1 · {POLO_A_REHACER} REHECHO CON EL BARRIDO DE CONTINUIDAD")
    p("=" * 100)
    p("")
    p(f"  {len(cuerpo)} locales. La partición vieja con `leaf` dejó dos concentraciones afuera de")
    p("  la cáscara, de 70 y 59 locales a 5,96 y 5,39 locales/ha. Eso no se remienda: se rehace.")
    p("")
    p("  REGLA DECLARADA ANTES DE MIRAR: se toma el umbral MÁS ALTO en el que todavía existan dos")
    p(f"  o más componentes de {MINIMO} locales o más. El más alto es el conservador —cuanto más")
    p("  alto, más une—, así que el más alto que todavía separa es el que menos fragmenta.")
    p("")

    filas = []
    for umbral in UMBRALES_CONTINUIDAD:
        partes = componentes(cuerpo, umbral)
        nombrables = [c for c in partes if len(c) >= MINIMO]
        filas.append({
            "umbral_m": umbral, "componentes": len(partes),
            f"componentes_de_{MINIMO}_o_mas": len(nombrables),
            "locales_en_esas_componentes": sum(len(c) for c in nombrables),
            # La columna que distingue una PARTICIÓN de un ESTALLIDO. Dos partes nombrables
            # acompañadas de sesenta esquirlas no son una estructura de dos lóbulos: son un tejido
            # continuo mirado con lupa. En Belgrano las tres componentes se llevaban todos los
            # puntos; acá hay que mirar si pasa lo mismo antes de creerle al conteo.
            "pct_locales_en_esas_componentes": round(
                sum(len(c) for c in nombrables) / len(cuerpo) * 100, 1),
            "tamanos": ";".join(str(len(c)) for c in partes[:6]),
        })
    curva = pd.DataFrame(filas)
    p(curva.to_string(index=False))
    p("")

    columna = f"componentes_de_{MINIMO}_o_mas"
    candidatos = curva[curva[columna] >= 2]
    if not len(candidatos):
        p("  NO HAY NINGÚN UMBRAL CON DOS PARTES NOMBRABLES. La curva es plana: no hay estructura")
        p("  estable que partir, y entonces sí corresponde revertir la partición y dejarlo entero.")
        p("")
        return {"se_parte": False, "umbral": None, "piezas": {}}

    umbral = int(candidatos.umbral_m.max())
    partes = [c for c in componentes(cuerpo, umbral) if len(c) >= MINIMO]
    p(f"  UMBRAL ELEGIDO: {umbral} m → {len(partes)} partes nombrables de "
      f"{', '.join(str(len(c)) for c in partes)} locales")
    p(f"    (a {int(curva[curva[columna] >= 2].umbral_m.min())} m la estructura ya aparece, y a "
      f"{int(curva[curva[columna] < 2].umbral_m.min())} m se funde en una sola: la partición vive")
    p("    en una franja del barrido, no en un solo valor. Eso es lo que la hace estable.)")
    p("")

    etiquetas = {}
    for orden, parte in enumerate(partes, start=1):
        for posicion in parte:
            etiquetas[cuerpo.index[posicion]] = f"{POLO_A_REHACER}-{orden}"
    sueltos = len(cuerpo) - sum(len(c) for c in partes)
    p(f"    locales en las partes: {sum(len(c) for c in partes)} | sueltos: {sueltos} "
      f"({sueltos / len(cuerpo) * 100:.1f} %)")
    p("")

    # --- la verificación, contra cosas que NO se usaron para elegir el umbral
    p("  VERIFICACIÓN · contra cosas que no intervinieron en la elección del umbral")
    p("    La condición era explícita: «si aparecen partes estables que incluyan esos dos bloques,")
    p("    ésa es la partición». Así que lo que hay que mirar no es si aparecen partes, sino si")
    p("    esas partes se llevan los bloques que la partición vieja perdió.")
    p("")
    asignado = pd.Series(etiquetas)
    sueltos_viejos = geo[(geo.polo_id == POLO_A_REHACER) & (geo.polo_final == "")]
    recluster = agrupar(sueltos_viejos, MINIMO, PARAMETROS["min_samples"])
    capturas = []
    for bloque in bloques[bloques.padre == POLO_A_REHACER].itertuples():
        numero = int(bloque.bloque.split("-S")[1]) - 1
        miembros = sueltos_viejos.index[recluster == numero]
        capturados = int(asignado.reindex(miembros).notna().sum())
        destino = asignado.reindex(miembros).dropna().value_counts()
        capturas.append(capturados / len(miembros) if len(miembros) else 0.0)
        p(f"    bloque {bloque.bloque} ({bloque.locales} locales, {bloque.locales_x_ha} loc/ha): "
          f"{capturados} de {len(miembros)} ahora caen en una pieza"
          + (f" → {destino.index[0]}" if len(destino) else " → NINGUNA"))
    cobertura_bloques = min(capturas) if capturas else 0.0
    en_partes = sum(len(c) for c in partes) / len(cuerpo)
    p("")
    p(f"    locales del polo que quedan en alguna parte: {en_partes * 100:.1f} %")
    p(f"    peor bloque recapturado: {cobertura_bloques * 100:.1f} %")
    p("")

    # El criterio de aceptación también estaba declarado: las partes tienen que INCLUIR los
    # bloques. Si no los incluyen, esta partición no resuelve lo que se pidió resolver, y la
    # instrucción para ese caso también estaba escrita: revertir.
    if cobertura_bloques >= 0.5 and en_partes >= 0.70:
        p("    VEREDICTO: la partición por continuidad recupera los bloques. Se adopta.")
        p("")
        return {"se_parte": True, "umbral": umbral, "piezas": etiquetas, "curva": curva,
                "n_partes": len(partes)}

    p("    VEREDICTO: NO. Esta partición tampoco sirve, y hay que decirlo en vez de acomodarla.")
    p("")
    p("    El diagnóstico está en la columna `pct_locales_en_esas_componentes`: en el umbral")
    p(f"    elegido las dos partes nombrables se llevan sólo el {en_partes * 100:.1f} % de los")
    p(f"    locales, y el resto queda repartido en "
      f"{int(curva.loc[curva.umbral_m == umbral, 'componentes'].iloc[0]) - len(partes)} esquirlas.")
    p("    **P065 no se parte en dos lóbulos: estalla en muchos pedazos.** Es un tejido continuo")
    p("    mirado con lupa, no una estructura de partes. La diferencia con Belgrano es visible en")
    p("    la tabla: allá las tres componentes se llevaban todos los puntos; acá, la mitad se cae.")
    p("")
    p("    Y por eso el bloque S1 no aparece en ninguna parte: no es que la partición lo puso en")
    p("    el lado equivocado, es que a 55 m S1 ya está roto en pedazos por debajo del mínimo.")
    p("")
    p("    CONSECUENCIA, y era la instrucción declarada para este caso: **P065 se revierte y queda")
    p("    entero.** No hay estructura estable que lo divida. Vuelven sus 188 locales sueltos y")
    p("    vuelve R19, que es lo que se quería, pero por el camino honesto: porque el polo no")
    p("    tenía que haberse partido, no porque se lo remiende hasta que dé.")
    p("")
    p("    NOTA SOBRE PALERMO · CORREGIDA el 2026-08-06 por `polos_donde_esta_soho.py`. Lo que")
    p("    decía era: «Soho, Hollywood y Las Cañitas son estructura real, pero NO están en P065».")
    p("    **Es cierto para Soho y para Hollywood, y es falso para Las Cañitas.** Al medirlo:")
    p("    Báez 17 de 17 locales y Arce 17 de 17 caen adentro de P065, y las dos son la segunda y")
    p("    tercera calle del polo. P065 ES Las Cañitas y su entorno —Soldado de la Independencia,")
    p("    Migueletes, Luis María Campos, Gorostiaga—, no una cadena sin identidad.")
    p("")
    p("    Esto NO cambia la decisión de revertir la partición: se tomó por la curva de")
    p("    estabilidad, no por esta nota. Lo que cambia es cómo se nombra P065.")
    p("")
    p("    Y el mapa completo de la hipótesis de las tres subzonas, que era la pregunta de fondo:")
    p("      Palermo Soho      → P091 (728 locales; la esquina Serrano y Honduras cae adentro)")
    p("      Palermo Hollywood → P078 (585; Fitz Roy, Bonpland, Humboldt)")
    p("      Las Cañitas       → P065 (361; Báez y Arce enteras)")
    p("    Las tres están en el borrador, pero como POLOS SEPARADOS y no como partes de uno. Por")
    p("    eso ninguna curva de estabilidad las encontraba: se las buscaba adentro de un polo.")
    p("")
    return {"se_parte": False, "umbral": umbral, "piezas": {}, "curva": curva, "n_partes": 0}


# --------------------------------------------------------------------------- §4


def unir_a_100(polos: gpd.GeoDataFrame, geo: gpd.GeoDataFrame, p) -> tuple[gpd.GeoDataFrame, pd.DataFrame]:
    """§4 · unión a 100 m evaluada sobre el objeto unido, de a una y sin transitividad."""
    p(f"§4 · UNIÓN A {UMBRAL_UNION_M:.0f} M · evaluada sobre el objeto unido, no transitiva")
    p("=" * 100)
    p("")
    p("  Cada candidata se evalúa sobre el RESULTADO UNIDO y las uniones se aplican de a una: si")
    p("  dos polos se unen, la candidata siguiente que los toque se evalúa contra el objeto ya")
    p("  unido. Así A–B a 90 m y B–C a 90 m no encadenan A con C por transitividad: la segunda")
    p("  unión tiene que pasar las pruebas contra el cuerpo A+B entero.")
    p("")
    p("  CONTINUIDAD · los puntos de los dos juntos tienen que formar UNA componente conexa a")
    p(f"                {UMBRAL_UNION_M:.0f} m. Si siguen siendo dos cuerpos, el hueco no lo cierra la oferta.")
    p("  ESTABILIDAD · `leaf` sobre el unido no lo tiene que volver a separar en dos piezas")
    p("                nombrables. **No se une lo que la partición volvería a separar.**")
    p("")

    pertenencia = {polo: {polo} for polo in polos.polo_id}
    geometrias = dict(zip(polos.polo_id, polos.geometry))
    puntos = {polo: geo[geo.polo_final == polo] for polo in polos.polo_id}

    # Candidatas ordenadas por distancia: se prueba primero la más cercana, que es la más
    # defendible, y las que quedan se reevalúan contra el objeto que haya resultado.
    def padre(polo_id: str) -> str:
        """El polo del que salió una pieza, si salió de una partición."""
        return polo_id.split("-")[0]

    candidatas, hermanas = [], []
    for i, a in enumerate(polos.polo_id):
        for b in list(polos.polo_id)[i + 1:]:
            distancia = geometrias[a].distance(geometrias[b])
            if distancia > UMBRAL_UNION_M:
                continue
            # NO se reúnen dos piezas del mismo padre. Es la regla que impide que la unión deshaga
            # en silencio la partición que se acaba de decidir. Y no es una excepción cómoda: la
            # prueba de estabilidad de la unión corre `leaf` sobre los puntos de las dos piezas
            # solas, mientras que la partición corrió `leaf` sobre el padre entero —con sus 694
            # puntos de tejido incluidos—. Son dos preguntas distintas sobre dos conjuntos
            # distintos, y la del padre entero es la que tenía la información completa. La unión
            # sirve para juntar polos independientes que quedaron cerca, no para re-litigar una
            # partición ya resuelta con mejores datos.
            if padre(a) == padre(b) and "-" in a and "-" in b:
                hermanas.append({"par": f"{a}+{b}", "distancia_m": round(distancia, 1),
                                 "evaluado_como": "", "continuidad": "", "estabilidad": "",
                                 "decision": "EXCLUIDA · piezas del mismo padre"})
                continue
            candidatas.append((distancia, a, b))
    candidatas.sort()

    p(f"  pares a menos de {UMBRAL_UNION_M:.0f} m: {len(candidatas) + len(hermanas)}")
    p(f"    excluidos por ser piezas del mismo padre: {len(hermanas)}"
      + (f" — {', '.join(h['par'] for h in hermanas)}" if hermanas else ""))
    p("    (la unión no deshace una partición ya decidida: la prueba de la unión mira las dos")
    p("     piezas solas, y la partición miró el padre entero con su tejido. La segunda tenía la")
    p("     información completa.)")
    p(f"    candidatas que se evalúan: {len(candidatas)}")
    p("")

    vive = {polo: polo for polo in polos.polo_id}   # a qué objeto pertenece hoy cada polo
    registro = []
    for distancia, a, b in candidatas:
        objeto_a, objeto_b = vive[a], vive[b]
        if objeto_a == objeto_b:
            registro.append({"par": f"{a}+{b}", "distancia_m": round(distancia, 1),
                             "evaluado_como": f"{objeto_a}+{objeto_b}",
                             "continuidad": "", "estabilidad": "", "decision": "YA UNIDOS"})
            continue
        cuerpo = pd.concat([puntos[objeto_a], puntos[objeto_b]])
        conexas = componentes(cuerpo, UMBRAL_UNION_M)
        continuidad = len(conexas) == 1
        etiquetas = agrupar(cuerpo, MINIMO, PARAMETROS["min_samples"], METODO_PARTICION)
        piezas = pd.Series(etiquetas[etiquetas >= 0]).value_counts()
        estabilidad = int((piezas >= MINIMO).sum()) < 2
        une = continuidad and estabilidad

        if une:
            nuevo = f"{objeto_a}+{objeto_b}"
            puntos[nuevo] = cuerpo
            geometrias[nuevo] = geometrias[objeto_a].union(geometrias[objeto_b])
            pertenencia[nuevo] = pertenencia.pop(objeto_a) | pertenencia.pop(objeto_b)
            for polo, objeto in list(vive.items()):
                if objeto in (objeto_a, objeto_b):
                    vive[polo] = nuevo
        registro.append({
            "par": f"{a}+{b}", "distancia_m": round(distancia, 1),
            "evaluado_como": f"{objeto_a}+{objeto_b}",
            "continuidad": "1 cuerpo" if continuidad else f"{len(conexas)} cuerpos",
            "estabilidad": "no se vuelve a partir" if estabilidad
                           else f"leaf la parte en {int((piezas >= MINIMO).sum())}",
            "decision": "UNE" if une else "NO UNE",
        })

    tabla = pd.DataFrame(registro + hermanas)
    p(tabla.to_string(index=False))
    p("")
    unidas = tabla[tabla.decision == "UNE"]
    rechazadas = tabla[tabla.decision == "NO UNE"]
    p(f"    uniones aplicadas: {len(unidas)} · rechazadas: {len(rechazadas)} · "
      f"pares ya unidos por una unión previa: {int((tabla.decision == 'YA UNIDOS').sum())}")
    if len(rechazadas):
        por_continuidad = int((rechazadas.continuidad != "1 cuerpo").sum())
        p(f"    rechazadas por continuidad (siguen siendo dos cuerpos a {UMBRAL_UNION_M:.0f} m): "
          f"{por_continuidad}")
        p(f"    rechazadas por estabilidad (la partición las volvería a separar): "
          f"{len(rechazadas) - por_continuidad}")
    p("")
    p("    La columna `evaluado_como` es la que demuestra que no hubo transitividad: cuando un par")
    p("    toca un objeto ya unido, lo que se evaluó fue el objeto entero y no el polo suelto.")
    p("")

    objetos = {objeto: sorted(partes) for objeto, partes in pertenencia.items()}
    geo = geo.copy()
    geo["polo_unido"] = geo.polo_final.map(vive).fillna("")
    return geo, tabla, objetos


# --------------------------------------------------------------------------- informe


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    buffer = io.StringIO()

    def p(*args_):
        print(*args_, file=buffer)

    geo = cargar_puntos(PARAMETROS["anillo"], PARAMETROS["solo_aptos"])
    base_completa = cargar_base_completa()
    pertenencia = pd.read_csv(OUT / "pertenencia_local_polo_v2.csv")
    geo = geo.merge(pertenencia[["local_id", "polo_id", "polo_final"]], on="local_id", how="left")
    geo[["polo_id", "polo_final"]] = geo[["polo_id", "polo_final"]].fillna("")
    bloques = pd.read_csv(OUT / "particion_bloques_de_sueltos.csv")
    zonas = gpd.read_file(ENVOLVENTES_22).to_crs(CRS_METRICO)
    cortes = json.loads((OUT / "parametros_v2.json").read_text(
        encoding="utf-8"))["clases_densidad"]["cortes_locales_x_ha"]
    parejidad = cargar_parejidad()

    p("BORRADOR · P065 rehecho, el precio final, las clases a dos y la unión a 100 m")
    p("=" * 100)
    p("")
    p("NO ES UN PRODUCTO. No se publica, no se sella y no toca el Atlas.")
    p("Google Places: 0 requests. Places no está en la base.")
    p("")
    p("ACEPTADO SIN CAMBIOS: la partición de P018, P025 y P072. El desglose mostró que sus sueltos")
    p("son tejido —los cuatro grupos de P072 tienen el centro adentro de la cáscara de sus piezas—.")
    p("")

    resultado = rehacer_p065(geo, bloques, zonas, p)

    # --- el conjunto con P065 rehecho
    geo["polo_final_v3"] = geo.polo_final
    if resultado["se_parte"]:
        geo.loc[geo.polo_id == POLO_A_REHACER, "polo_final_v3"] = ""
        for indice, etiqueta in resultado["piezas"].items():
            geo.at[indice, "polo_final_v3"] = etiqueta
    else:
        geo.loc[geo.polo_id == POLO_A_REHACER, "polo_final_v3"] = POLO_A_REHACER
    geo["polo_final"] = geo.polo_final_v3

    polos = reconstruir(geo, base_completa, "polo_final")
    geo, tabla_union, objetos = unir_a_100(polos, geo, p)
    polos = reconstruir(geo, base_completa, "polo_unido")
    polos["partes_unidas"] = polos.polo_id.map(lambda o: len(objetos.get(o, [o])))

    # --- §2 precio final
    ruido = int((geo.polo_unido == "").sum())
    p("§2 · EL PRECIO FINAL")
    p("=" * 100)
    p("")
    cotejo = cotejar(polos, zonas)
    tabla_precio = pd.DataFrame([
        {"etapa": "etapa 1 · sin partir", "polos": 118, "locales_en_polos": 13564,
         "pct_fuera": 43.4, "ha": 3745, "zonas_encontradas": 15},
        {"etapa": "etapa 2 · leaf en los 10", "polos": 127, "locales_en_polos": 12500,
         "pct_fuera": 47.9, "ha": 3058, "zonas_encontradas": 13},
        {"etapa": "etapa 3 · P065 rehecho + unión 100 m", "polos": len(polos),
         "locales_en_polos": int(polos.locales.sum()),
         "pct_fuera": round(ruido / len(geo) * 100, 1), "ha": round(polos.ha.sum()),
         "zonas_encontradas": int(cotejo.encontrada.sum())},
    ])
    p(tabla_precio.to_string(index=False))
    p("")
    p(f"    locales fuera de todo polo: {ruido:,} de {len(geo):,}")
    p(f"    control §5 · envolventes que pasan: {int(polos.control_aptitud.sum())} de {len(polos)}")
    p("")
    vuelven = cotejo[(cotejo.referencia_id.isin(["R19", "R15"]))]
    p("    LAS DOS ZONAS QUE SE HABÍAN PERDIDO")
    p(vuelven[["referencia_id", "nombre", "pct_zona_cubierta", "encontrada"]].to_string(index=False))
    p("")

    # --- §3 clases a dos
    polos = clases_a_dos(polos, geo, cortes, p)

    # La añada vuelve a la capa: se rearmaron los polos desde cero y hay que recalcularla. Va en la
    # ficha AL LADO de la clase, no en otra tabla, que es la forma de que nadie compare dos polos
    # de años distintos sin verlo.
    puntos = geo[geo.polo_unido != ""].copy()
    puntos["anada"] = puntos.barrio.map(plegar).map(parejidad.anio_relevamiento)
    puntos["es_rus"] = puntos.grupos_independencia.fillna("").str.contains("GCBA_URBANISMO")
    anadas = puntos.groupby("polo_unido").apply(lambda g: pd.Series({
        "anada_relevamiento": int(g.anada.value_counts().index[0]) if g.anada.notna().any() else None,
        "anada_mixta": g.anada.nunique() > 1,
        "anadas": ";".join(f"{int(a)}:{c}" for a, c in g.anada.value_counts().items()),
        "pct_puntos_del_relevamiento": round(g.es_rus.mean() * 100, 1),
    }))
    polos = polos.merge(anadas, left_on="polo_id", right_index=True, how="left")
    p("  LA AÑADA, RECALCULADA SOBRE EL CONJUNTO FINAL")
    p(polos.groupby("anada_relevamiento").agg(
        polos=("polo_id", "size"), locales=("locales", "sum")).to_string())
    p(f"    con añada mixta: {int(polos.anada_mixta.sum())} de {len(polos)}")
    p("")

    # --- salidas
    salida = buffer.getvalue()
    (OUT / "P065_UNION_Y_CLASES.txt").write_text(salida, encoding="utf-8")
    polos.drop(columns=["geometry"]).round(3).to_csv(
        OUT / "borrador_polos_v3.csv", index=False, encoding="utf-8")
    polos.to_crs(CRS_GEO).to_file(OUT / "borrador_polos_v3.geojson", driver="GeoJSON")
    geo[["local_id", "polo_id", "polo_final", "polo_unido", "barrio", "comuna"]].to_csv(
        OUT / "pertenencia_local_polo_v3.csv", index=False, encoding="utf-8")
    tabla_union.to_csv(OUT / "union_100m_candidatas.csv", index=False, encoding="utf-8")
    if resultado.get("curva") is not None:
        resultado["curva"].to_csv(OUT / "curva_continuidad_p065.csv", index=False, encoding="utf-8")
    cotejo.to_csv(OUT / "cotejo_22_zonas_v3.csv", index=False, encoding="utf-8")

    print(salida)
    print(f"escrito en {OUT.relative_to(ROOT)}")
    return 0


def reconstruir(geo: gpd.GeoDataFrame, base_completa: gpd.GeoDataFrame,
                columna: str) -> gpd.GeoDataFrame:
    """Rearma la capa de polos desde una columna de pertenencia."""
    con_polo = geo[geo[columna] != ""].copy()
    codigos = {etiqueta: i for i, etiqueta in enumerate(sorted(con_polo[columna].unique()))}
    polos = construir_polos(con_polo, con_polo[columna].map(codigos).to_numpy(),
                            PARAMETROS["concave_hull_ratio"])
    inverso = {f"P{v + 1:03d}": k for k, v in codigos.items()}
    polos["polo_id"] = polos.polo_id.map(inverso)
    return control_aptitud(polos, base_completa)


def cotejar(polos: gpd.GeoDataFrame, zonas: gpd.GeoDataFrame) -> pd.DataFrame:
    """El cotejo contra las 22, con el mismo umbral de siempre."""
    union = polos.union_all()
    filas = []
    for zona in zonas.itertuples():
        cubierta = zona.geometry.intersection(union).area / zona.geometry.area
        filas.append({"referencia_id": zona.referencia_id, "nombre": zona.nombre,
                      "familia": zona.familia_etiqueta,
                      "pct_zona_cubierta": round(cubierta * 100, 1),
                      "encontrada": cubierta >= COBERTURA_MINIMA_ZONA})
    return pd.DataFrame(filas)


def clases_a_dos(polos: gpd.GeoDataFrame, geo: gpd.GeoDataFrame, cortes: list[float],
                 p) -> gpd.GeoDataFrame:
    """§3 · dos clases, con el corte que ya aguantó la prueba de robustez."""
    corte = cortes[0]
    polos = polos.copy()
    polos["clase_densidad"] = np.where(polos.locales_x_ha < corte,
                                       CLASE_EXTENDIDA, CLASE_CONCENTRACION)

    p("§3 · LAS CLASES PASAN DE TRES A DOS")
    p("=" * 100)
    p("")
    p("  El motivo está medido en el informe anterior y conviene dejarlo acá también, porque es lo")
    p("  que justifica que no haya tres: al cambiar el conjunto de puntos —sacando entera la fuente")
    p("  rotativa— la clase C conservó 51 de 51 y la clase A conservó 2 de 26. Y las dos")
    p("  explicaciones intuitivas de esa inestabilidad resultaron falsas al medirlas: no es")
    p("  dependencia del Relevamiento (40,9 % contra 40,8 %, p = 0,51) ni cercanía al corte (0,179")
    p("  contra 0,228, p = 0,45). Es que Fisher–Jenks minimiza varianza, la varianza la domina la")
    p("  cola alta, y al adelgazarse la cola el corte superior se va de 1,59× la mediana a 3,29×.")
    p("  **La frontera densa/media la pone la forma de la cola, no el territorio.** Por eso no")
    p("  existe y no se publica.")
    p("")
    p(f"  EL CORTE ES UNA CONVENCIÓN DECLARADA, NO UNA FRONTERA DESCUBIERTA. {corte:.2f} locales/ha,")
    p(f"  a un pelo de la mediana de {polos.locales_x_ha.median():.2f}. Ésa es la redacción correcta")
    p("  y es la que hay que usar en todos lados, porque es la que el propio §1 ya obligaba: **no")
    p("  hay hueco en la distribución de densidad**, así que no hay ninguna estructura del")
    p("  territorio que este número esté encontrando. Lo elegimos, y lo decimos.")
    p("")
    p("  Con esa redacción el esquema deja de estar amenazado por el refit. Si dijéramos «acá está")
    p("  la frontera entre concentración y concentración extendida», un método de corte distinto")
    p("  que la mueve nos estaría contradiciendo. Diciendo «elegimos cortar en 4,58», un método")
    p("  distinto que corta en otro lado no contradice nada: elige otra convención.")
    p("")
    p("  El corte NO se recalcula al pasar de tres clases a dos: refitear ahora cambiaría la")
    p("  frontera que se conserva sólo porque se borró la otra.")
    p("")
    resumen = polos.groupby("clase_densidad").agg(
        polos=("polo_id", "size"), locales=("locales", "sum"), ha=("ha", "sum"),
        densidad_min=("locales_x_ha", "min"), densidad_max=("locales_x_ha", "max")).round(2)
    p(resumen.to_string())
    p("")

    # La misma prueba de robustez que tumbó a las tres clases, ahora sobre dos.
    sin_rus = geo[(geo.polo_unido != "")
                  & ~geo.grupos_independencia.fillna("").str.contains("GCBA_URBANISMO")]
    polos["densidad_sin_rus"] = polos.polo_id.map(
        sin_rus.groupby("polo_unido").local_id.count()).fillna(0) / polos.ha

    p("  LA MISMA PRUEBA DE ROBUSTEZ QUE TUMBÓ A LAS TRES CLASES, AHORA SOBRE DOS")
    p("    Se recalcula la densidad sin el Relevamiento —el 41 % de los puntos— y se vuelve a")
    p("    clasificar. Hay dos maneras de trasladar el corte a la escala nueva y dan resultados")
    p("    distintos, así que van las dos:")
    p("")

    # (a) La que corresponde a un clasificador de umbral fijo: el corte se reescala junto con la
    # distribución, porque sacar el 41 % de los puntos baja todas las densidades. La pregunta es
    # si los MISMOS polos caen del mismo lado, no si Jenks vuelve a cortar en el mismo número.
    factor = polos.densidad_sin_rus.median() / polos.locales_x_ha.median()
    corte_reescalado = corte * factor
    clase_reescalada = np.where(polos.densidad_sin_rus < corte_reescalado,
                                CLASE_EXTENDIDA, CLASE_CONCENTRACION)
    iguales_a = int((polos.clase_densidad == clase_reescalada).sum())
    rand_a = adjusted_rand_score(polos.clase_densidad, clase_reescalada)
    p(f"    (a) CORTE REESCALADO con la mediana ({corte:.2f} → {corte_reescalado:.2f} loc/ha).")
    p("        Es la traslación que corresponde a un clasificador de umbral fijo: la escala baja,")
    p("        el corte baja con ella, y se pregunta si los mismos polos caen del mismo lado.")
    p(f"        conservan clase: {iguales_a} de {len(polos)} "
      f"({iguales_a / len(polos) * 100:.1f} %) · Rand ajustado {rand_a:.3f}")
    p("")

    # (b) La que se usó con tres clases, para que las dos cifras sean comparables entre informes.
    corte_sin, _ = fisher_jenks(polos.densidad_sin_rus.to_numpy(), 2)
    clase_jenks = np.where(polos.densidad_sin_rus < corte_sin[0],
                           CLASE_EXTENDIDA, CLASE_CONCENTRACION)
    iguales_b = int((polos.clase_densidad == clase_jenks).sum())
    rand_b = adjusted_rand_score(polos.clase_densidad, clase_jenks)
    reparto = pd.Series(clase_jenks).value_counts()
    p(f"    (b) JENKS REFITEADO a k = 2 sobre la escala nueva (corte {corte_sin[0]:.2f}).")
    p(f"        conservan clase: {iguales_b} de {len(polos)} "
      f"({iguales_b / len(polos) * 100:.1f} %) · Rand ajustado {rand_b:.3f}")
    p(f"        reparto que produce: {' / '.join(f'{v} {k}' for k, v in reparto.items())}")
    p("        Este número es BAJO y no hay que taparlo — pero mide otra cosa: con k = 2 sobre una")
    p("        distribución de cola larga, Jenks pone el corte donde más varianza saca, o sea muy")
    p("        arriba, y produce clases muy desbalanceadas. Es el MISMO defecto que tumbó a las")
    p("        tres clases —el corte lo gobierna la cola—, ahora sobre el único corte que queda.")
    p("")
    rand = rand_a
    p("    QUÉ SE CONCLUYE. La lectura que decide es (a), porque el esquema adoptado es un umbral")
    p("    fijo y no un refit: la pregunta operativa es si un polo cambia de clase cuando cambian")
    p("    los datos, no si Jenks reelige el mismo número.")
    if rand >= 0.60:
        p(f"    Con el corte reescalado, {iguales_a / len(polos) * 100:.0f} % de los polos conserva")
        p("    su clase y el Rand pasa el umbral de 0,60 que las tres clases no pasaban. El esquema")
        p("    de dos clases SÍ es reproducible al cambiar el conjunto de puntos.")
    else:
        p("    Ni con el corte reescalado se llega a 0,60. Hay que decirlo entero: la clase sirve")
        p("    como descriptor y NUNCA como criterio, ni siquiera con dos categorías.")
    p("")
    p("    Y en los dos casos vale lo mismo, que es la parte que no depende de ningún umbral: la")
    p("    frontera se mueve con la forma de la distribución porque la distribución no tiene")
    p("    huecos. Por eso la ficha lleva la densidad exacta primero.")
    p("")
    p("  Y en la ficha, el orden es: **densidad exacta primero, clase después.**")
    p("")
    return polos


if __name__ == "__main__":
    sys.exit(main())
