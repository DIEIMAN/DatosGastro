"""Los quince enclaves comunitarios, con geometría donde la fuente la permite y no donde no.

QUÉ HACE
--------
La ronda 1 construyó **cuatro** enclaves a partir de lo que Diego había escrito en prosa. La ronda
3 trae un CSV de **quince**, con delimitación textual, nivel de precisión, número de grupos
independientes y advertencias. Este script los convierte en capa.

Y estrena el vocabulario de la vía D, que deja de tener dos valores:

    abierta                          hay enclave delimitable y cruzable
    medida_sin_enclave               se buscó, hay comunidad, no hay oferta comercial estable
    no_medida                        falta la delimitación para poder cruzar
    no_medible_con_este_instrumento  economía migrante que no toma forma de fachada contigua
    enclave_en_formacion             el quinto valor que trae el CSV y no estaba en la consigna

DOS MÉTODOS DE CONSTRUCCIÓN, DECLARADOS EN `LECTURA_PREVIA_RONDA_3.md` §4
--------------------------------------------------------------------------
    eje+buffer      tramo(s) de calle + 150 m. Cabeceras por calle de corte o por rango de altura.
    puntos+buffer   la unión de 150 m alrededor de las puertas documentadas, sin eje. Sólo E09.

Los que no toman ninguno no reciben geometría. **E08 Charrúa tiene el mejor perímetro físico del
Atlas —dos avenidas y una traza ferroviaria— y aun así no se poligoniza**, porque le falta el
cuarto borde y porque su estado ya es `medida_sin_enclave`: darle área sugeriría que hay algo
adentro que medir.

LO QUE MÁS FÁCIL SE HACE MAL ACÁ
---------------------------------
**«Corredor Peruano» no es una designación normativa.** Es una placa del 2 de junio de 2012 puesta
por vecinos, comerciantes y el Consulado del Perú. No hay ley, ordenanza, resolución ni
declaración de interés. `es_normativa = no` para los quince, y para E01 con una nota propia: si
entra como norma, el Atlas afirma algo falso sobre el Estado.

Google Places: 0 requests. USIG sí, para las cabeceras por altura.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/enclaves_ronda_3.py
"""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from dataset_bares_notables import CACHE, consultar, limpiar  # noqa: E402
from polos_soporte import (  # noqa: E402
    BUFFER_ENCLAVE_M,
    CALLEJERO,
    CRS_GEOGRAFICO,
    CRS_METRICO,
    _punto_de_cruce,
    _segmentos_de,
    _tramo_entre,
    sin_tildes,
)

BARRIDO = ROOT / "outputs" / "BARRIDO_CIUDAD_2026-08"
OUT = BARRIDO / "seis_vias"
EVIDENCIA = BARRIDO / "desde_cowork" / "evidencia_2026"
ENTRADA = EVIDENCIA / "enclaves_comunitarios_delimitados.csv"

# ---------------------------------------------------------------- las recetas, una por enclave
#
# `tramos` es (calle, corte_a, corte_b) con los nombres como los escribe el callejero. Un corte
# puede ser una calle o una altura: `#2379` significa «el punto de esa calle en la altura 2379»,
# que se resuelve con USIG. `None` en los dos cortes significa que la fuente nombra la calle sin
# decir entre qué y qué, y entonces entra entera dentro del marco de barrios, declarado.
#
# El filtro por barrio NO agrupa por barrio: recorta la calle al lugar que la propia delimitación
# nombra. Agüero cruza Balvanera y Recoleta; sin el marco, el «tramo» se estira hasta donde el
# nombre exista.
RECETAS = {
    # El Corredor Peruano del Abasto: lo que la ronda 2 dejó pendiente y sin lo cual el Abasto no
    # podía abrir vía D medida. Los anexos por establecimiento —Guardia Vieja 3372 y Av.
    # Corrientes 3564— NO entran al eje: la fuente los da como anexos, no como continuidad, y
    # meterlos convertiría dos puntos sueltos en corredor.
    "E01": {"metodo": "eje+buffer", "barrios": ["Balvanera"], "tramos": [
        ("AGÜERO", "CORRIENTES AV.", "GOMEZ, VALENTIN"),
        # El callejero invierte el apellido: «Jean Jaurès» es «JAURES, JEAN», igual que «Ruperto
        # Godoy» es «GODOY, RUPERTO». Escribirlo como se lee lo pierde en silencio.
        #
        # Y una corrección de lo declarado, con su consecuencia medida. La lectura previa dijo que
        # Jean Jaurès y Zelaya entraban ENTERAS porque la fuente las nombra «sin cabecera». Para
        # Zelaya es cierto —es un pasaje y la fuente lo nombra sin más—. Para Jean Jaurès NO: la
        # fuente dice «al 600», que es una cuadra. Entera daba 1.431 m de eje y llevaba E01 a 66,3
        # ha; con la cuadra que la fuente nombra da 26,9 ha. La regla «sin cabecera entra entera»
        # existe para no inventar cortes, no para ignorar los que la fuente da: aplicada acá
        # inflaba el enclave, que es el sesgo que hace abrir vía D de más.
        ("JAURES, JEAN", "#600", "#699"),
        ("ZELAYA", None, None)]},
    "E02": {"metodo": "eje+buffer", "barrios": ["Belgrano"], "tramos": [
        ("ARRIBEÑOS", "JURAMENTO", "OLAZABAL"),
        ("MENDOZA", "MONTAÑESES", "__VIAS__")]},
    "E03": {"metodo": "eje+buffer", "barrios": ["Flores"], "tramos": [
        ("CARABOBO AV.", "CASTAÑARES AV.", "PERON, EVA AV.")]},
    "E04": {"metodo": "eje+buffer", "barrios": [], "tramos": [
        ("GODOY, RUPERTO", "HELGUERA", "CUENCA")]},
    # Once: la fuente oficial (GCBA 2015) da la nube de puertas habilitadas por rango de altura,
    # y esa nube es MUCHO más apretada que el polígono declarado por DAIA. Se usa la nube. El
    # polígono de DAIA —Corrientes, Pueyrredón, Rivadavia, Pasteur— queda en el texto: la propia
    # fuente avisa que sus límites son objeto de discusión.
    "E05": {"metodo": "eje+buffer", "barrios": ["Balvanera"], "tramos": [
        ("TUCUMAN", "#2379", "#2802"),
        ("PASO", "#706", "#757"),
        ("ECUADOR", "#594", "#742"),
        ("SAN LUIS", "#2427", "#2742"),
        ("PUEYRREDON AV.", "#336", "#880")]},
    # Flores sefardí: se construye y NO computa. n_grupos = 1 y de 2015. Tener la lista de
    # direcciones más larga después del Once no lo vuelve delimitado: lo vuelve bien inventariado
    # por una sola fuente vieja.
    "E06": {"metodo": "eje+buffer", "barrios": [], "computa": False, "tramos": [
        ("AVELLANEDA AV.", "#2395", "#2701"),
        ("ARANGUREN, JUAN F., DR.", "#2941", "#3192"),
        ("ARGERICH", "#809", "#843"),
        ("CUENCA", "#180", "#515")]},
    # Liniers SIN el cuadrante. El cuadrante José León Suárez / Montiel / Ramón Falcón / Ibarrola
    # vino en la consigna, no en una fuente, y no se carga como verificado. Se conservan los tres
    # tramos de la ronda 1, con la procedencia que tienen.
    #
    # CORRECCIÓN DE LA RONDA 1: el callejero tiene DOS Ramón Falcón. «FALCON, RAMON L.,CNEL. AV.»
    # son 128 m en Liniers, alturas 5902-6000. La calle donde está el Mercado Andino —y donde el
    # IDECBA pone el eje comercial, 6801-7299— es «FALCON, RAMON L.,CNEL.», sin AV., 1.728 m. La
    # receta de la ronda 1 usaba la variante con AV. y ponía el enclave 900 números al oeste.
    "E07": {"metodo": "eje+buffer", "barrios": ["Liniers"], "tramos": [
        ("SUAREZ, JOSE LEON", "RIVADAVIA AV.", None),
        ("FALCON, RAMON L.,CNEL.", None, None),
        ("IBARROLA", None, None)]},
    # Retiro coreano: seis puertas y ninguna cabecera. Trazarle un eje sería dibujar la línea que
    # la fuente no dibujó.
    "E09": {"metodo": "puntos+buffer", "puertas": [
        "Maipu 972", "Paraguay 884", "San Martin 687", "Paraguay 831",
        "M. T. de Alvear 818", "Carlos Pellegrini 1179"]},
}

# Los que reciben geometría pero no computan vía D, cada uno por el motivo que trae su fuente.
NO_COMPUTAN = {
    "E06": "n_grupos = 1 y de 2015: una sola fuente no delimita al mismo nivel que las demás",
}

NOTA_E01 = (
    "«Corredor Peruano» NO es normativo: es una placa del 02/06/2012 puesta por vecinos, "
    "comerciantes y el Consulado del Perú. No hay ley, ordenanza, resolución ni declaración de "
    "interés. Y la cuadra 400 de Agüero está en recambio asiático desde 2024, así que la "
    "delimitación de 2012 y la de 2025 describen realidades distintas.")


def punto_en_altura(calle: str, altura: str, marco: gpd.GeoDataFrame, cache: dict):
    """El punto de una calle en una altura, por USIG. La cabecera que la fuente da por número."""
    candidato = consultar(limpiar(f"{calle} {altura}"), cache)
    if not candidato or not candidato.get("coordenadas"):
        return None
    punto = gpd.GeoSeries(
        gpd.points_from_xy([float(candidato["coordenadas"]["x"])],
                           [float(candidato["coordenadas"]["y"])]),
        crs=CRS_GEOGRAFICO).to_crs(CRS_METRICO).iloc[0]
    return punto


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    OUT.mkdir(parents=True, exist_ok=True)
    buffer_txt = io.StringIO()

    def p(*args_):
        print(*args_, file=buffer_txt)

    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    entrada = pd.read_csv(ENTRADA)
    callejero = gpd.read_file(CALLEJERO).to_crs(CRS_METRICO)
    callejero["clave"] = callejero.nomoficial.map(sin_tildes)
    cruces_ffcc = callejero[callejero.tipo_ffcc.astype(str).str.strip() != "Sin Iteracción"]

    p("LOS QUINCE ENCLAVES · geometría donde la fuente la permite, y no donde no")
    p("=" * 100)
    p("")
    p(f"  entrada: {len(entrada)} enclaves · lo declarado está en LECTURA_PREVIA_RONDA_3.md §3-§4")
    p("  Google Places: 0 requests.")
    p("")
    p("  El reparto de estados de vía D que trae la fuente:")
    for estado, cuantos in entrada.estado_via_D.value_counts().items():
        ids = ", ".join(entrada[entrada.estado_via_D == estado].enclave_id)
        p(f"      {estado:<34}{cuantos:>3}   {ids}")
    p("")
    p("      `enclave_en_formacion` (E15) es un QUINTO valor que el CSV trae y la consigna no")
    p("      nombra. No se pliega a ninguno de los cuatro: es un `medida_sin_enclave` con fecha")
    p("      de vencimiento, y queda para que Diego lo confirme o lo pliegue.")
    p("")

    filas, bitacora = [], []
    for fila in entrada.itertuples():
        receta = RECETAS.get(fila.enclave_id)
        registro = {
            "enclave_id": fila.enclave_id, "colectividad": fila.colectividad,
            "barrios_declarados": fila.barrios, "estado_via_D": fila.estado_via_D,
            "nivel_precision": fila.nivel_precision, "n_grupos_fuentes": fila.n_grupos_fuentes,
            "es_normativa": "no", "designacion_oficial": fila.designacion_oficial,
            "advertencia": fila.advertencia,
            "metodo_geometria": receta["metodo"] if receta else "sin geometría",
            "computa_via_D": "no", "geometry": None, "n_tramos": 0, "largo_eje_m": 0.0,
        }
        if fila.enclave_id == "E01":
            registro["advertencia"] = f"{NOTA_E01} || {fila.advertencia}"

        if receta is None:
            bitacora.append(f"{fila.enclave_id}: sin receta — no recibe geometría "
                            f"({fila.estado_via_D})")
            filas.append(registro)
            continue

        piezas = []
        if receta["metodo"] == "puntos+buffer":
            for puerta in receta["puertas"]:
                candidato = consultar(limpiar(puerta), cache)
                if not candidato or not candidato.get("coordenadas"):
                    bitacora.append(f"{fila.enclave_id} · {puerta}: USIG no resuelve — se omite")
                    continue
                punto = gpd.GeoSeries(
                    gpd.points_from_xy([float(candidato["coordenadas"]["x"])],
                                       [float(candidato["coordenadas"]["y"])]),
                    crs=CRS_GEOGRAFICO).to_crs(CRS_METRICO).iloc[0]
                piezas.append(punto)
            if piezas:
                bitacora.append(f"{fila.enclave_id}: {len(piezas)} de "
                                f"{len(receta['puertas'])} puertas geocodificadas; sin eje, "
                                "porque la fuente no da cabeceras")
                registro["n_tramos"] = len(piezas)
                registro["geometry"] = unary_union(piezas).buffer(BUFFER_ENCLAVE_M)
        else:
            marco = (callejero[callejero.barrio.isin(receta["barrios"])]
                     if receta["barrios"] else callejero)
            for calle, corte_a, corte_b in receta["tramos"]:
                segmentos = _segmentos_de(calle, marco)
                if segmentos.empty:
                    bitacora.append(f"{fila.enclave_id} · {calle}: NO está en el callejero "
                                    "— tramo omitido")
                    continue
                largo_total = float(segmentos.length.sum())
                if corte_a is None and corte_b is None:
                    piezas.append(unary_union(list(segmentos.geometry)))
                    bitacora.append(
                        f"{fila.enclave_id} · {calle}: la fuente la nombra sin cabecera; entra "
                        f"entera dentro del marco ({largo_total:,.0f} m)")
                    continue
                cruces, falla = [], False
                for corte in (corte_a, corte_b):
                    if corte is None:
                        cruces.append(None)
                        continue
                    if str(corte).startswith("#"):
                        punto = punto_en_altura(calle, str(corte)[1:], marco, cache)
                        if punto is None:
                            bitacora.append(f"{fila.enclave_id} · {calle} {corte}: USIG no "
                                            "resuelve la altura — se declara")
                            falla = True
                        cruces.append(punto)
                        continue
                    if corte == "__VIAS__":
                        otra = cruces_ffcc[(cruces_ffcc.clave == sin_tildes(calle)) &
                                           (cruces_ffcc.index.isin(marco.index))]
                    else:
                        otra = callejero[callejero.clave == sin_tildes(corte)]
                    if otra.empty:
                        bitacora.append(f"{fila.enclave_id} · corte «{corte}»: no aparece "
                                        "— se declara")
                        falla = True
                        cruces.append(None)
                        continue
                    cruces.append(_punto_de_cruce(segmentos, otra))
                if falla or any(c is None for c in cruces):
                    bitacora.append(f"{fila.enclave_id} · {calle}: falta un corte; se toma la "
                                    "calle entera dentro del marco, sin inventar el punto")
                    pieza = unary_union(list(segmentos.geometry))
                else:
                    pieza = _tramo_entre(segmentos, cruces[0], cruces[1])
                    if pieza is None or pieza.is_empty:
                        # Un rango de alturas puede ser MÁS CORTO que la cuadra que lo contiene:
                        # Argerich 809-843 son 34 números, un tercio de cuadra, y ningún centroide
                        # de segmento cae adentro de una base de 30 m. En ese caso el tramo no está
                        # vacío: es el segmento que contiene a las dos cabeceras. Se toma ése y
                        # queda dicho, en vez de perder el tramo por una tolerancia geométrica.
                        cercanos = {segmentos.distance(punto).idxmin() for punto in cruces}
                        pieza = unary_union(list(segmentos.loc[sorted(cercanos)].geometry))
                        bitacora.append(
                            f"{fila.enclave_id} · {calle} {corte_a}-{corte_b}: el rango es más "
                            f"corto que la cuadra; se toma {len(cercanos)} segmento(s) del "
                            "callejero que contienen a las cabeceras")
                if pieza is None or pieza.is_empty:
                    bitacora.append(f"{fila.enclave_id} · {calle}: el tramo salió vacío — se omite")
                    continue
                piezas.append(pieza)
                bitacora.append(
                    f"{fila.enclave_id} · {calle} entre {corte_a} y {corte_b}: "
                    f"{pieza.length:,.0f} m de eje (la calle dentro del marco: {largo_total:,.0f} m)")
            if piezas:
                registro["n_tramos"] = len(piezas)
                registro["largo_eje_m"] = round(sum(pieza.length for pieza in piezas), 1)
                registro["geometry"] = unary_union(piezas).buffer(BUFFER_ENCLAVE_M)

        if registro["geometry"] is not None:
            computa = (fila.estado_via_D == "abierta" and fila.enclave_id not in NO_COMPUTAN
                       and receta.get("computa", True))
            registro["computa_via_D"] = "si" if computa else "no"
            registro["motivo_no_computa"] = (
                "" if computa else NO_COMPUTAN.get(
                    fila.enclave_id, f"estado de vía D = {fila.estado_via_D}"))
        filas.append(registro)

    capa = gpd.GeoDataFrame(filas, geometry="geometry", crs=CRS_METRICO)
    capa["buffer_m"] = BUFFER_ENCLAVE_M
    capa["ha"] = capa.geometry.apply(lambda g: round(g.area / 10_000, 2) if g else 0.0)

    p("-" * 100)
    p("  CÓMO SE RESOLVIÓ CADA TRAMO")
    p("")
    for linea in bitacora:
        p(f"      {linea}")
    p("")

    p("-" * 100)
    p("  LA CAPA")
    p("")
    p(f"      {'id':<5}{'colectividad':<28}{'método':<16}{'tramos':>7}{'eje m':>10}{'ha':>9}"
      f"   {'computa':<9}estado")
    for fila in capa.itertuples():
        p(f"      {fila.enclave_id:<5}{str(fila.colectividad)[:27]:<28}"
          f"{fila.metodo_geometria:<16}{fila.n_tramos:>7}{fila.largo_eje_m:>10,.0f}{fila.ha:>9.1f}"
          f"   {fila.computa_via_D:<9}{fila.estado_via_D}")
    p("")
    con_geometria = capa[capa.geometry.notna()]
    computan = capa[capa.computa_via_D == "si"]
    p(f"      con geometría: {len(con_geometria)} de {len(capa)} · "
      f"computan vía D: {len(computan)}")
    p(f"      la ronda 1 tenía 4 enclaves cruzables; ahora son {len(computan)}.")
    p("")
    for fila in capa[(capa.geometry.notna()) & (capa.computa_via_D == "no")].itertuples():
        p(f"      GEOMETRÍA SIN CÓMPUTO · {fila.enclave_id}: {fila.motivo_no_computa}")
    p("")

    p("-" * 100)
    p("  E01 · EL CORREDOR PERUANO DEL ABASTO, QUE ES LO QUE FALTABA")
    p("")
    e01 = capa[capa.enclave_id == "E01"]
    if len(e01) and e01.geometry.iloc[0] is not None:
        p(f"      {e01.n_tramos.iloc[0]} tramos · {e01.largo_eje_m.iloc[0]:,.0f} m de eje · "
          f"{e01.ha.iloc[0]:.1f} ha con el buffer declarado de {BUFFER_ENCLAVE_M} m")
        p("")
        p("      Eje primario: Agüero entre Av. Corrientes y Valentín Gómez, altura 400-450.")
        p("      Ejes secundarios: Jean Jaurès y Zelaya, que la fuente nombra SIN cabecera y por")
        p("      eso entran enteros dentro de Balvanera, igual que Ramón Falcón e Ibarrola en")
        p("      Liniers. No se les inventa el corte.")
        p("")
        p("      Y lo que NO entró: Guardia Vieja 3372 y Av. Corrientes 3564. La fuente los da")
        p("      como anexos por establecimiento, no por continuidad. Meterlos en el eje habría")
        p("      convertido dos puntos sueltos en corredor.")
    else:
        p("      NO SE PUDO CONSTRUIR. Se declara y no se sustituye por otra cosa.")
    p("")
    p("      es_normativa = no. Y la nota que viaja con la fila:")
    for linea in [NOTA_E01[i:i + 88] for i in range(0, len(NOTA_E01), 88)]:
        p(f"            {linea}")
    p("")

    p("-" * 100)
    p("  LOS QUE NO RECIBEN GEOMETRÍA, Y POR QUÉ")
    p("")
    for fila in capa[capa.geometry.isna()].itertuples():
        p(f"      {fila.enclave_id} · {str(fila.colectividad)[:40]}")
        p(f"            estado: {fila.estado_via_D}")
        p(f"            {str(fila.advertencia)[:180]}")
    p("")
    p("      E08 Charrúa merece la aclaración: tiene el MEJOR perímetro físico del Atlas —Av.")
    p("      Bonorino, Av. Fernández de la Cruz y las vías del Belgrano Sur, dos avenidas y una")
    p("      traza ferroviaria— y aun así no se poligoniza. Le falta el cuarto borde, y sobre")
    p("      todo: su estado es `medida_sin_enclave`. Darle área sugeriría que hay algo adentro")
    p("      que medir, y tres fuentes independientes —incluida una nota extensa de prensa")
    p("      boliviana dedicada al barrio— no nombran un solo local de comida.")
    p("")

    salida = capa.copy()
    salida.loc[salida.geometry.isna(), "geometry"] = None
    salida[salida.geometry.notna()].to_file(
        OUT / "enclaves_comunitarios_r3.geojson", driver="GeoJSON")
    capa.drop(columns="geometry").to_csv(
        OUT / "enclaves_comunitarios_r3.csv", index=False, encoding="utf-8")
    CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")

    p("=" * 100)
    p(f"  {len(capa)} enclaves · {len(con_geometria)} con geometría · "
      f"{len(computan)} computan vía D · Places: 0 requests")
    p("=" * 100)
    p("")

    (OUT / "ENCLAVES_R3.txt").write_text(buffer_txt.getvalue(), encoding="utf-8")
    print(buffer_txt.getvalue())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
