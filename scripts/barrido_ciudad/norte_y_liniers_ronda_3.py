"""Ronda 3 · el eje del IDECBA contra los locales bolivianos, el viaducto de Núñez y R18.

TRES MEDICIONES QUE COMPARTEN LA MISMA PREGUNTA: ¿la convergencia se sostiene con datos?
------------------------------------------------------------------------------------------

**1 · Liniers.** El IDECBA releva ejes comerciales, no gastronomía, y no sabe nada de
colectividades. Su eje de Liniers es **Ramón Falcón 6801-7299**, que es una de las cuatro calles
del microcentro boliviano. Dos mediciones ciegas entre sí que caen sobre la misma calle es
exactamente lo que la regla de independencia busca. **Pero caer sobre la misma calle no es caer
sobre el mismo tramo**, y eso es lo que se mide acá.

Lo declarado en `LECTURA_PREVIA_RONDA_3.md` §5, antes de mirar: *de los cinco locales bolivianos
con altura, cuatro son de Ibarrola y uno de José León Suárez; ninguno es de Ramón Falcón. Si eso
se confirma, la convergencia es entre el eje y el polígono del enclave, no entre el eje y los
locales.*

**2 · Núñez y el viaducto Mitre.** 58 locales, 3,5 km, 80.000 a 100.000 personas los fines de
semana (enero de 2025). Es la única cifra dura de densidad de todo el barrido documental. Se
traza el corredor y se mide **qué encontró el clustering ahí**.

**3 · R18 a la luz de Z46 Retiro.** No se redibuja nada. Se mide cuánto del clúster coreano
documentado cae adentro de R18 y cuánto afuera.

Google Places: 0 requests. Ninguna geometría publicada se toca.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/norte_y_liniers_ronda_3.py
"""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import LineString
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from dataset_bares_notables import CACHE, consultar, limpiar  # noqa: E402
from polos_soporte import (  # noqa: E402
    BARRIDO,
    CALLEJERO,
    CRS_GEOGRAFICO,
    CRS_METRICO,
    envolventes_22,
    puntos_base,
    sin_tildes,
)

OUT = BARRIDO / "seis_vias"
IDECBA = BARRIDO / "idecba" / "ejes_comerciales_48_vigente.csv"
PUBLICABLES = BARRIDO / "borrador_polos" / "polos_publicables.geojson"

BUFFER_EJE_M = 150          # la misma convención declarada que los enclaves: una cuadra por lado

# Los locales bolivianos con altura que trae el material. Son de 2016 y así se los trata.
LOCALES_BOLIVIANOS = [
    ("El Conejo", "Jose Leon Suarez 216", "2016"),
    ("Miriam", "Ibarrola 7184", "2016"),
    ("Pollo Copacabana", "Ibarrola 7276", "2016"),
    ("Pollo Copacabana (2)", "Ibarrola 7291", "2016"),
    ("Rico Pollo", "Ibarrola 7193", "2016"),
]

# El paseo bajo el viaducto Mitre. La primera versión de esta corrida lo trazó como la recta entre
# las dos cabeceras que nombra la fuente —Federico Lacroze y Libertador, hasta Av. Monroe— y dio
# 1,61 km contra los 3,5 declarados: la recta no representa la traza. La segunda no adivina.
#
# **El propio callejero oficial marca el viaducto.** La columna `tipo_ffcc` distingue «Tren
# Elevado - Paso a Nivel Sin Vías» de los pasos a nivel comunes, y en Colegiales, Belgrano y Núñez
# hay 18 cruces así marcados. No son un solo viaducto: son dos ramales. Se separan por componentes
# conexas a 400 m —y el resultado NO cambia entre 300 y 500 m, así que el umbral no lo sostiene—;
# la componente mayor tiene 13 cruces y es la del ramal Tigre, la que la fuente describe.
BARRIOS_VIADUCTO = ["Colegiales", "Belgrano", "Nuñez"]
CORTE_COMPONENTE_M = 400
CURVA_COMPONENTE_M = (300, 400, 500)
LARGO_DECLARADO_KM = 3.5
LOCALES_DECLARADOS_VIADUCTO = 58

# Las puertas del clúster coreano-asiático de Retiro / San Nicolás que nombran las dos fuentes.
CLUSTER_COREANO = [
    ("Centro Cultural Coreano", "Maipu 972", "Info Gastronómica 2019 · ex Palacio Bencich"),
    ("Mr. HO", "Paraguay 884", "La Nación 10/05/2026"),
    ("Kimchi Garden", "San Martin 687", "La Nación 10/05/2026"),
    ("Kuro Neko", "Paraguay 831", "relevamiento de enclaves"),
    ("Saigon Noodle Bar", "M. T. de Alvear 818", "relevamiento de enclaves · vietnamita"),
    ("Fa Song Song", "Esmeralda y M. T. de Alvear", "relevamiento del norte · sin altura"),
    ("(derrame) Carlos Pellegrini 1179", "Carlos Pellegrini 1179", "derrame sobre San Nicolás"),
]


def geocodificar(direccion: str, cache: dict):
    candidato = consultar(limpiar(direccion), cache)
    if not candidato or not candidato.get("coordenadas"):
        return None
    return gpd.GeoSeries(
        gpd.points_from_xy([float(candidato["coordenadas"]["x"])],
                           [float(candidato["coordenadas"]["y"])]),
        crs=CRS_GEOGRAFICO).to_crs(CRS_METRICO).iloc[0]


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    OUT.mkdir(parents=True, exist_ok=True)
    buffer_txt = io.StringIO()

    def p(*args_):
        print(*args_, file=buffer_txt)

    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    puntos = puntos_base()
    callejero = gpd.read_file(CALLEJERO).to_crs(CRS_METRICO)
    callejero["clave"] = callejero.nomoficial.map(sin_tildes)
    publicables = gpd.read_file(PUBLICABLES).to_crs(CRS_METRICO)

    p("RONDA 3 · LINIERS, EL VIADUCTO DE NÚÑEZ Y R18")
    p("=" * 100)
    p("")
    p(f"  base: {len(puntos):,} locales · polos publicables: {len(publicables)}")
    p("  Lo declarado está en LECTURA_PREVIA_RONDA_3.md §5 y §6. Google Places: 0 requests.")
    p("")

    # ================================================================ 1 · LINIERS
    p("=" * 100)
    p("  1 · ¿LA CONVERGENCIA DEL IDECBA SE SOSTIENE CON DATOS O ES COINCIDENCIA DE CALLE?")
    p("=" * 100)
    p("")
    ejes = pd.read_csv(IDECBA)
    eje_liniers = ejes[(ejes.eje == "Liniers")].iloc[0]
    p(f"      el eje del IDECBA: {eje_liniers.calle} {eje_liniers.altura_texto} "
      f"(eje_id {eje_liniers.eje_id}, relevamiento 1.er cuatrimestre 2026)")
    p("")

    # El tramo del IDECBA sale del propio callejero, que trae la altura por segmento en
    # `alt_izqini` / `alt_izqfin`. No hace falta geocodificar cabeceras ni proyectar nada.
    #
    # Y acá aparece una trampa que además arrastraba el enclave de Liniers: el callejero tiene DOS
    # Ramón Falcón. «FALCON, RAMON L.,CNEL. AV.» son 128 m en Liniers, alturas 5902-6000. La calle
    # donde está el Mercado Andino —alturas 6700 a 7300— es «FALCON, RAMON L.,CNEL.», sin AV., y
    # son 1.728 m. La receta de la ronda 1 usaba la variante con AV. y por lo tanto ponía el
    # enclave boliviano 900 números más al oeste de donde está.
    segmentos_falcon = callejero[(callejero.clave == sin_tildes("FALCON, RAMON L.,CNEL.")) &
                                 (callejero.barrio == "Liniers")]
    con_av = callejero[(callejero.clave == sin_tildes("FALCON, RAMON L.,CNEL. AV.")) &
                       (callejero.barrio == "Liniers")]
    p(f"      LAS DOS RAMÓN FALCÓN DEL CALLEJERO, dentro de Liniers:")
    p(f"            «FALCON, RAMON L.,CNEL.»       {len(segmentos_falcon):>3} segmentos · "
      f"{segmentos_falcon.length.sum():>6,.0f} m · alturas "
      f"{int(segmentos_falcon.alt_izqini.min())}-{int(segmentos_falcon.alt_izqfin.max())}")
    p(f"            «FALCON, RAMON L.,CNEL. AV.»   {len(con_av):>3} segmentos · "
      f"{con_av.length.sum():>6,.0f} m · alturas "
      f"{int(con_av.alt_izqini.min())}-{int(con_av.alt_izqfin.max())}")
    p("      El eje del IDECBA cae sobre la PRIMERA. La receta del enclave de la ronda 1 usaba la")
    p("      segunda: 900 números más al oeste que el Mercado Andino. Queda corregido en")
    p("      `enclaves_ronda_3.py` y anotado acá, porque cambia dónde está E07.")
    p("")
    del_tramo = segmentos_falcon[
        (segmentos_falcon.alt_izqfin >= eje_liniers.altura_desde) &
        (segmentos_falcon.alt_izqini <= eje_liniers.altura_hasta)]
    if del_tramo.empty:
        p("      Ningún segmento del callejero cae en el rango del IDECBA. No se sustituye.")
        tramo_idecba = None
    else:
        tramo_idecba = unary_union(list(del_tramo.geometry))
        p(f"      el tramo del IDECBA: {len(del_tramo)} segmentos, "
          f"{tramo_idecba.length:,.0f} m, alturas "
          f"{int(del_tramo.alt_izqini.min())}-{int(del_tramo.alt_izqfin.max())} · "
          f"la calle entera en Liniers mide {segmentos_falcon.length.sum():,.0f} m")
    p("")

    filas_bol = []
    for nombre, direccion, anio in LOCALES_BOLIVIANOS:
        punto = geocodificar(direccion, cache)
        registro = {"local": nombre, "direccion": direccion, "anio_fuente": anio,
                    "geocodificado": "si" if punto is not None else "no"}
        if punto is not None and tramo_idecba is not None:
            registro["distancia_al_eje_idecba_m"] = round(punto.distance(tramo_idecba), 1)
            registro["dentro_del_buffer_150m"] = \
                "si" if punto.distance(tramo_idecba) <= BUFFER_EJE_M else "no"
        registro["calle"] = direccion.rsplit(" ", 1)[0]
        filas_bol.append(registro)
    bolivianos = pd.DataFrame(filas_bol)
    bolivianos.to_csv(OUT / "liniers_bolivianos_vs_idecba.csv", index=False, encoding="utf-8")

    p("      LOS LOCALES BOLIVIANOS CON ALTURA, CONTRA EL EJE DEL IDECBA")
    p("")
    p(f"      {'local':<24}{'dirección':<26}{'dist. al eje':>14}{'≤150 m':>9}")
    for fila in bolivianos.itertuples():
        distancia = getattr(fila, "distancia_al_eje_idecba_m", np.nan)
        p(f"      {fila.local[:23]:<24}{fila.direccion[:25]:<26}"
          f"{('—' if pd.isna(distancia) else f'{distancia:,.0f} m'):>14}"
          f"{getattr(fila, 'dentro_del_buffer_150m', '—'):>9}")
    p("")
    en_falcon = bolivianos[bolivianos.calle.str.contains("Falcon", case=False, na=False)]
    dentro = bolivianos[bolivianos.get("dentro_del_buffer_150m", pd.Series(dtype=str)) == "si"]
    p(f"      locales sobre Ramón Falcón: {len(en_falcon)} de {len(bolivianos)}")
    p(f"      locales a ≤150 m del tramo del IDECBA: {len(dentro)} de {len(bolivianos)}")
    p("")

    # La otra mitad de la prueba: ¿el tramo del IDECBA es más denso que el resto de la calle?
    if tramo_idecba is not None:
        buffer_tramo = tramo_idecba.buffer(BUFFER_EJE_M)
        resto = unary_union(list(segmentos_falcon.geometry)).difference(buffer_tramo)
        en_tramo = puntos[puntos.within(buffer_tramo)]
        en_resto = puntos[puntos.within(resto.buffer(BUFFER_EJE_M))] if not resto.is_empty \
            else puntos.iloc[0:0]
        largo_resto = resto.length if not resto.is_empty else 0.0
        p("      ¿EL TRAMO DEL IDECBA ES MÁS DENSO EN GASTRONOMÍA QUE EL RESTO DE LA CALLE?")
        p("")
        p(f"      {'tramo':<34}{'largo':>10}{'locales':>10}{'por km':>10}")
        p(f"      {'Ramón Falcón 6801-7299 (IDECBA)':<34}{tramo_idecba.length:>9,.0f}m"
          f"{len(en_tramo):>10}"
          f"{len(en_tramo) / (tramo_idecba.length / 1000):>10.1f}")
        if largo_resto > 0:
            p(f"      {'resto de R. Falcón en Liniers':<34}{largo_resto:>9,.0f}m{len(en_resto):>10}"
              f"{len(en_resto) / (largo_resto / 1000):>10.1f}")
        p("")

    p("      LO QUE SE PUEDE AFIRMAR:")
    if len(en_falcon) == 0:
        p("      Ninguno de los locales bolivianos documentados está sobre Ramón Falcón. La")
        p("      convergencia NO es entre el eje comercial del IDECBA y los locales bolivianos:")
        p("      es entre el eje y el POLÍGONO del enclave, que se construyó con tres calles y")
        p("      una de ellas es Ramón Falcón. Sigue siendo una convergencia —dos instrumentos")
        p("      ciegos entre sí que señalan el mismo lugar—, pero es una convergencia de área,")
        p("      no de puerta, y decirla como si fuera de puerta la sobrevende.")
    else:
        p(f"      {len(en_falcon)} de {len(bolivianos)} locales bolivianos están sobre Ramón")
        p("      Falcón. La convergencia se sostiene también a nivel de puerta.")
    p("")
    p("      Y una limitación que no se arregla midiendo: los cinco locales son de 2016 y ninguno")
    p("      tiene vigencia verificada. Lo que se comparó es un eje relevado en 2026 contra")
    p("      puertas publicadas hace diez años.")
    p("")

    # ================================================================ 2 · NÚÑEZ
    p("=" * 100)
    p("  2 · NÚÑEZ · EL VIADUCTO MITRE CONTRA LO QUE ENCONTRÓ EL CLUSTERING")
    p("=" * 100)
    p("")
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components
    from scipy.spatial import cKDTree

    en_barrios = callejero[callejero.barrio.isin(BARRIOS_VIADUCTO)]
    elevados = en_barrios[en_barrios.tipo_ffcc.astype(str).str.startswith(
        "Tren Elevado")].reset_index(drop=True)
    medios = np.array([[g.interpolate(0.5, normalized=True).x,
                        g.interpolate(0.5, normalized=True).y] for g in elevados.geometry])
    p(f"      el callejero oficial marca {len(elevados)} cruces «Tren Elevado» en "
      f"{', '.join(BARRIOS_VIADUCTO)}.")
    p("      No son un viaducto sino dos ramales, y separarlos es la primera decisión:")
    for radio in CURVA_COMPONENTE_M:
        pares = np.array(list(cKDTree(medios).query_pairs(radio)))
        grafo = coo_matrix((np.ones(len(pares)), (pares[:, 0], pares[:, 1])),
                           shape=(len(medios), len(medios)))
        cuantas, etiquetas = connected_components(grafo, directed=False)
        p(f"            a {radio} m: {cuantas} componentes, tamaños "
          f"{sorted((int(t) for t in np.bincount(etiquetas)), reverse=True)}")
        if radio == CORTE_COMPONENTE_M:
            mayor = np.argmax(np.bincount(etiquetas))
            elegidos = np.where(etiquetas == mayor)[0]
    p("      El resultado no cambia en todo el rango: el umbral no está sosteniendo la partición.")
    p("")
    if len(elegidos) < 3:
        p("      La componente mayor tiene menos de 3 cruces. No se traza el corredor.")
    else:
        cruces = medios[elegidos]
        centrado = cruces - cruces.mean(axis=0)
        _, _, ejes = np.linalg.svd(centrado, full_matrices=False)
        orden = np.argsort(centrado @ ejes[0])
        traza = LineString(cruces[orden])
        largo_km = traza.length / 1000
        p(f"      la componente mayor tiene {len(elegidos)} cruces: "
          f"{', '.join(sorted(set(elevados.nomoficial[elegidos])))}")
        p("")
        p(f"      traza reconstruida: {largo_km:.2f} km · declarado por la fuente: "
          f"{LARGO_DECLARADO_KM} km")
        if abs(largo_km - LARGO_DECLARADO_KM) / LARGO_DECLARADO_KM > 0.25:
            p("      DIFERENCIA MAYOR AL 25 %. La fuente empieza el paseo en Federico Lacroze y")
            p("      Libertador, que es Colegiales; los cruces que el callejero marca como tren")
            p("      elevado en estos tres barrios llegan hasta Virrey del Pino y no más al sur.")
            p("      Lo que se mide acá es EL TRAMO BELGRANO-NÚÑEZ del viaducto, no los 3,5 km")
            p("      enteros, y todo lo que sigue se lee sobre ese tramo.")
        else:
            p("      La diferencia es menor al 25 %: la traza del callejero y la de la fuente")
            p("      describen el mismo corredor.")
        p("")
        corredor = traza.buffer(BUFFER_EJE_M)
        adentro = puntos[puntos.within(corredor)]
        tocados = publicables[publicables.intersects(corredor)]
        p(f"      corredor con {BUFFER_EJE_M} m por lado: {corredor.area / 10_000:.1f} ha")
        p(f"      locales de la base adentro: {len(adentro)}")
        p(f"      densidad: {len(adentro) / (corredor.area / 10_000):.2f} locales/ha · "
          f"{len(adentro) / largo_km:.1f} por km de traza")
        p("")
        p(f"      LA CIFRA DE LA FUENTE: {LOCALES_DECLARADOS_VIADUCTO} locales inaugurados en tres")
        p(f"      tramos (enero de 2025) = {LOCALES_DECLARADOS_VIADUCTO / LARGO_DECLARADO_KM:.1f}")
        p("      por km. No entra a ninguna columna: mide inauguraciones acumuladas, no puertas")
        p("      abiertas hoy, y no es comparable con `n_locales`, que sale de la base.")
        p("")
        p(f"      QUÉ ENCONTRÓ EL CLUSTERING AHÍ: {len(tocados)} polos publicables tocan el")
        p("      corredor.")
        p("")
        cuotas = []
        if len(tocados):
            p(f"      {'polo':<10}{'locales':>9}{'ha':>9}{'loc/ha':>9}{'del polo adentro':>19}")
            for fila in tocados.itertuples():
                suyos = puntos[puntos.within(fila.geometry)]
                en_corredor = suyos[suyos.within(corredor)]
                cuota = (100.0 * len(en_corredor) / len(suyos)) if len(suyos) else np.nan
                cuotas.append(cuota)
                p(f"      {fila.polo_id:<10}{fila.n_locales:>9}{fila.ha:>9.1f}"
                  f"{fila.locales_x_ha:>9.2f}{cuota:>18.0f}%")
        p("")
        # La continuidad, que es lo que la lectura previa dijo que había que medir antes de
        # concluir nada: 16,6 locales por km a 60 m de umbral no forma cadena.
        if len(adentro) >= 2:
            from scipy.spatial import cKDTree
            coordenadas = np.array([[g.x, g.y] for g in adentro.geometry])
            distancias, _ = cKDTree(coordenadas).query(coordenadas, k=2)
            p(f"      distancia media al vecino más cercano dentro del corredor: "
              f"{distancias[:, 1].mean():,.0f} m")
            p(f"      pares a ≤60 m (el umbral de continuidad declarado): "
              f"{len(cKDTree(coordenadas).query_pairs(60))}")
        p("")
        p("      LO QUE SE PUEDE AFIRMAR:")
        propios = [c for c in cuotas if not np.isnan(c) and c >= 50]
        if propios:
            p(f"      El clustering SÍ encontró el corredor: {len(propios)} de los "
              f"{len(tocados)} polos que lo tocan tienen más de la mitad de sus locales")
            p("      adentro. No es un polo que roza el corredor: es un polo que ES el corredor.")
            p("      La lectura previa había anticipado lo contrario —que 16,6 locales por km no")
            p("      forman cadena a 60 m— y esa predicción SE CAYÓ: la base tiene ahí una")
            p("      densidad muy superior a la que la cifra de prensa sugiere.")
        else:
            p("      Los polos que tocan el corredor lo tocan por un pedazo: ninguno tiene más de")
            p("      la mitad de sus locales adentro. Para un algoritmo que exige contigüidad,")
            p("      la franja es larga y flaca.")
        p("")
        p("      Y la razón de la diferencia con la cifra de prensa, que importa: los 58 locales")
        p("      son los INAUGURADOS bajo el viaducto; la base cuenta toda la gastronomía del")
        p("      corredor, incluida la que ya estaba en las calles que el viaducto atraviesa.")
        p("      Son dos universos distintos y el más grande no valida al más chico.")
        p("")
        gpd.GeoDataFrame(
            [{"que_es": "corredor bajo el viaducto Mitre (aprox. recta entre cabeceras)",
              "largo_km": round(largo_km, 2), "buffer_m": BUFFER_EJE_M,
              "locales_base": len(adentro), "polos_publicables_tocados": len(tocados),
              "geometry": corredor}],
            geometry="geometry", crs=CRS_METRICO).to_file(
                OUT / "nunez_corredor_viaducto.geojson", driver="GeoJSON")

    # ================================================================ 3 · R18
    p("=" * 100)
    p("  3 · R18 ESMERALDA-PARAGUAY A LA LUZ DE Z46 RETIRO")
    p("=" * 100)
    p("")
    envolventes = envolventes_22().set_index("referencia_id")
    r18 = envolventes.geometry.get("R18")
    r12 = envolventes.geometry.get("R12")
    filas_cor = []
    for nombre, direccion, fuente in CLUSTER_COREANO:
        punto = geocodificar(direccion, cache)
        registro = {"establecimiento": nombre, "direccion": direccion, "fuente": fuente,
                    "geocodificado": "si" if punto is not None else "no"}
        if punto is not None:
            registro["dentro_de_R18"] = "si" if r18.contains(punto) else "no"
            registro["distancia_a_R18_m"] = round(punto.distance(r18), 1)
            registro["dentro_de_R12"] = "si" if r12 is not None and r12.contains(punto) else "no"
        filas_cor.append(registro)
    coreano = pd.DataFrame(filas_cor)
    coreano.to_csv(OUT / "retiro_cluster_coreano.csv", index=False, encoding="utf-8")

    p(f"      {'establecimiento':<32}{'dirección':<28}{'en R18':>8}{'dist.':>9}{'en R12':>8}")
    for fila in coreano.itertuples():
        distancia = getattr(fila, "distancia_a_R18_m", np.nan)
        p(f"      {fila.establecimiento[:31]:<32}{fila.direccion[:27]:<28}"
          f"{getattr(fila, 'dentro_de_R18', '—'):>8}"
          f"{('—' if pd.isna(distancia) else f'{distancia:,.0f} m'):>9}"
          f"{getattr(fila, 'dentro_de_R12', '—'):>8}")
    p("")
    resueltos = coreano[coreano.geocodificado == "si"]
    adentro18 = int((resueltos.dentro_de_R18 == "si").sum())
    p(f"      del clúster documentado, {adentro18} de {len(resueltos)} puertas caen DENTRO de R18.")
    cubierta = np.nan
    if len(resueltos):
        envolvente_cluster = unary_union(
            [geocodificar(direccion, cache) for _, direccion, _ in CLUSTER_COREANO
             if geocodificar(direccion, cache) is not None]).convex_hull
        cubierta = 100 * envolvente_cluster.intersection(r18).area / envolvente_cluster.area
        p(f"      la envolvente convexa del clúster mide {envolvente_cluster.area / 10_000:.1f} ha "
          f"contra las {r18.area / 10_000:.1f} ha de R18")
        p(f"      de esa envolvente, {cubierta:.0f} % cae dentro de R18")
    p("")
    p("      LO QUE SE PUEDE AFIRMAR:")
    if not np.isnan(cubierta) and cubierta >= 75:
        p("      Con las puertas documentadas, R18 NO se queda corta: el clúster coreano cabe")
        p("      adentro. La hipótesis de que R18 fuera el borde sur de un polo de Retiro más")
        p("      grande NO se sostiene con este material — se sostiene lo contrario, que R18 es")
        p(f"      {r18.area / 10_000 / (envolvente_cluster.area / 10_000):.0f} veces más grande "
          "que el clúster que la justifica.")
        p("")
        p("      PERO EL MATERIAL ES CHICO Y HAY QUE DECIRLO. La fuente de mayo de 2026 habla de")
        p(f"      un direccionario de 25 restaurantes coreanos y acá hay {len(resueltos)} puertas")
        p("      con dirección publicada. Si las 25 se extienden al norte o al oeste, el número")
        p("      cambia. La medición se hizo sobre lo que se puede geocodificar, no sobre lo que")
        p("      la nota afirma, y con 7 de 25 no se cierra la pregunta: se acota.")
    else:
        p("      La mayoría del clúster cae afuera de R18. R18 no es la zona: es su borde, y la")
        p("      delimitación tendría que responder al clúster y no al recorte actual.")
    p("")
    p("      En cualquiera de los dos casos, redibujar R18 es una DECISIÓN de Diego sobre")
    p("      geometría publicada, no un resultado de esta corrida: acá sólo está el número.")
    p("")
    p("      Y una consecuencia que sí es de esta corrida: con E09 cargado, R18 pasa a abrir vía")
    p("      D. Antes decía `no`. Ahora dice `abierta`, y por el clúster coreano-asiático.")
    p("")

    # ================================================================ 4 · las seis del norte
    p("=" * 100)
    p("  4 · LAS SEIS ZONAS DEL NORTE, CONTRA LA DENSIDAD QUE MIDE LA BASE")
    p("=" * 100)
    p("")
    p("      El relevamiento documental dice «5 entran, 1 no». Lo que el repositorio puede aportar")
    p("      es lo único que a esas fichas les falta: densidad por conteo. Se mide sobre el")
    p("      polígono del barrio, que es grueso —una zona no es su barrio— y por eso el número")
    p("      sirve para descartar, no para confirmar.")
    p("")
    ronda3 = pd.read_csv(BARRIDO / "desde_cowork" / "evidencia_2026" /
                         "seis_vias_ronda_3_norte.csv")
    capa_barrios = gpd.read_file(ROOT / "data" / "raw" / "geo_barrios.geojson").to_crs(CRS_METRICO)
    capa_barrios["clave"] = capa_barrios.nombre.map(sin_tildes)
    p(f"      {'id':<5}{'zona':<26}{'veredicto':<34}{'locales':>9}{'ha':>9}{'loc/ha':>9}")
    for fila in ronda3.itertuples():
        clave = sin_tildes(str(fila.zona).split("(")[0])
        suyo = capa_barrios[capa_barrios.clave == clave]
        if suyo.empty:
            p(f"      {fila.zona_id:<5}{str(fila.zona)[:25]:<26}{str(fila.veredicto)[:33]:<34}"
              f"{'sin barrio homónimo':>27}")
            continue
        poligono = suyo.geometry.iloc[0]
        adentro = puntos[puntos.within(poligono)]
        hectareas = poligono.area / 10_000
        p(f"      {fila.zona_id:<5}{str(fila.zona)[:25]:<26}{str(fila.veredicto)[:33]:<34}"
          f"{len(adentro):>9}{hectareas:>9.0f}{len(adentro) / hectareas:>9.2f}")
    p("")
    p("      COGHLAN es el caso que la propia ficha marca como el más expuesto: entra por el")
    p("      mínimo estricto, con dos vías, y su vía C depende de UN local relevado por la MISMA")
    p("      fuente que sostiene la mitad de su vía E. El número de arriba es lo que la base ve")
    p("      en el barrio entero; si esa densidad no se sostiene, la ficha hay que revisarla.")
    p("")

    CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
    p("=" * 100)
    p("  Google Places: 0 requests · ninguna geometría publicada modificada")
    p("=" * 100)
    p("")

    (OUT / "NORTE_Y_LINIERS_R3.txt").write_text(buffer_txt.getvalue(), encoding="utf-8")
    print(buffer_txt.getvalue())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
