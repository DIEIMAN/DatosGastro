"""Ronda 7 · las cuatro decisiones de geometría sobre las 22 publicadas.

QUÉ HACE
--------
Es la primera corrida del proyecto que mueve un polígono. Aplica las decisiones 5 a 8:

    R18 · se ABSORBE en Z46 Retiro y deja de existir como referencia independiente
    R19 · se AMPLÍA al entorno de Fraga, Dorrego, Charlone, Jorge Newbery y Plaza Los Andes
    R20 · se REVISA EL CORTE: el boulevard va de Av. Cabildo a Av. Balbín
    R21 · se AMPLÍA hacia Beláustegui, Remedios de Escalada, Paz Soldán, Rojas, Ávalos,
          Espinosa y Terrero

LA REGLA QUE ORDENA TODO ESTO
------------------------------
Las 22 **sólo se pueden ampliar**: el polígono nuevo tiene que CONTENER al viejo. No es una
formalidad. Las 22 son lo publicado, y un polígono que le saca superficie a lo publicado
convierte un ajuste de delimitación en una corrección de lo que la Dirección ya dijo. Por eso el
nuevo se construye como **unión** del viejo con la ampliación, y la contención se verifica igual,
explícitamente, en vez de darse por buena porque la construcción la garantiza.

R20 es el caso donde eso importa: la decisión dice «se revisa el corte», que puede recortar. Se
mide el tramo que la decisión describe **y** la unión que se adopta, y se reporta la diferencia
entre los dos en vez de esconderla adentro del resultado.

CÓMO SE CONVIERTE UNA CALLE EN ÁREA
------------------------------------
Con la misma convención que la ronda 3 declaró para los enclaves y no se movió desde entonces:
**150 m de buffer, una cuadra a cada lado del eje**. Se reporta la sensibilidad a 100 y 200 m
para que la elección quede a la vista y no haya que creerle a este archivo.

Los ejes se recortan al barrio de la zona antes de bufferearlos. Sin eso, «Terrero» son 3.989 m
que cruzan cuatro barrios y la ampliación de La Paternal se estiraría hasta Flores.

Google Places: 0 requests. Ninguna consulta de red: todo sale del callejero oficial, de la capa
de barrios, de la de espacios verdes públicos y de la base gastronómica.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/ronda_7_geometria_ampliaciones.py
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.ops import nearest_points, unary_union

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from polos_soporte import (  # noqa: E402
    BARRIDO,
    CALLEJERO,
    CRS_METRICO,
    barrios,
    envolventes_22,
    puntos_base,
    sin_tildes,
)

SEIS_VIAS = BARRIDO / "seis_vias"
GEOMETRIA = BARRIDO / "geometria_r7"
OUT_GEOJSON = GEOMETRIA / "referencias_r7.geojson"
OUT_CSV = GEOMETRIA / "ampliaciones_r7.csv"
OUT_SENSIBILIDAD = GEOMETRIA / "ampliaciones_sensibilidad_buffer_r7.csv"
INFORME_TXT = GEOMETRIA / "AMPLIACIONES_R7.txt"

ESPACIOS_VERDES = (ROOT / "outputs" / "polos_gastro" / "INVESTIGACION_DESBLOQUEOS_V21" /
                   "paquete" / "r15_plaza_arenales" / "fuentes" /
                   "espacios_verdes_publicos_gcba.geojson")

# La convención de la ronda 3, sin mover: una cuadra a cada lado del eje.
BUFFER_EJE_M = 150
CURVA_BUFFER_M = (100, 150, 200)

# Los ejes de cada decisión, con el nombre EXACTO del callejero oficial. Los cuatro que no
# coincidían con el nombre de la decisión se resolvieron buscando el token en el callejero y
# quedan anotados acá para que la traducción sea auditable, no un detalle de implementación:
#     «Beláustegui»                  → BELAUSTEGUI LUIS DR
#     «Remedios de Escalada»         → ESCALADA DE SAN MARTIN R
#     «M. T. de Alvear»              → ALVEAR MARCELO T DE
#     «Av. Balbín»                   → BALBIN RICARDO DR AV
AMPLIACIONES = {
    "R19": {
        "nombre": "Federico Lacroze por tramos",
        "decision": 6,
        "marco": ["Chacarita", "Colegiales"],
        "ejes": ["FRAGA", "DORREGO AV.", "CHARLONE", "NEWBERY, JORGE"],
        "plazas": ["Parque Los Andes"],
        "motivo": "El reconocimiento externo recae sobre Fraga, Dorrego, Charlone y Jorge "
                  "Newbery y sobre el entorno de Plaza Los Andes, NO sobre la Av. Federico "
                  "Lacroze. Cinco grupos de vía E hablan de Fraga y Dorrego y el polígono mide "
                  "Lacroze.",
    },
    "R21": {
        "nombre": "La Paternal",
        "decision": 8,
        # Villa Crespo entra al marco porque la decisión lo dice: «hacia el límite con Villa
        # Crespo». Con Paternal sola, TRES de los siete ejes —Beláustegui, Remedios de Escalada
        # y Rojas— dan cero metros: no pasan por el barrio. La ampliación sin Villa Crespo sería
        # de 9 locales, y no es lo que la decisión describe. Villa Gral. Mitre NO entra: la
        # decisión no lo nombra, y agregarlo sumaría otros 93 locales sin respaldo en el texto.
        "marco": ["Paternal", "Villa Crespo"],
        "ejes": ["BELAUSTEGUI LUIS DR", "ESCALADA DE SAN MARTIN R", "PAZ SOLDAN", "ROJAS",
                 "AVALOS", "ESPINOSA", "TERRERO"],
        "plazas": [],
        "motivo": "La prensa sitúa el circuito sobre esos siete ejes, hacia el límite con Villa "
                  "Crespo. La matriz la define por Av. San Martín y Av. Warnes, que ni La Nación "
                  "ni Time Out mencionan.",
    },
}

# R20 no es una ampliación por ejes sueltos: es un tramo entre dos avenidas.
R20_TRAMO = {
    "nombre": "Garcia del Rio",
    "decision": 7,
    "marco": ["Saavedra"],
    "eje": "GARCIA DEL RIO",
    "corte_a": "CABILDO AV.",
    "corte_b": "BALBIN, RICARDO, DR. AV.",
    "motivo": "Abre sólo vía F en la grilla pero tiene la cobertura documental más insistente de "
              "las 22 —La Nación 2021, 2025 y 2026, con reporteo de campo distinto cada vez—. Si "
              "la medición no ve lo que cuatro relevamientos describen, el problema está en dónde "
              "se cortó el corredor: el boulevard va de Av. Cabildo a Av. Balbín.",
}

# Decisión 5 · el clúster que R18 pasa a representar dentro de Retiro.
CLUSTER_COREANO = {
    "ejes": ["MAIPU", "ESMERALDA", "PARAGUAY", "ALVEAR MARCELO T DE"],
    "altura_desde": 800,
    "altura_hasta": 990,
    "marco": ["Retiro", "San Nicolas"],
}


def p_factory(buffer: io.StringIO):
    def p(*args_):
        print(*args_, file=buffer)
    return p


def marco_de(capa_barrios: gpd.GeoDataFrame, nombres: list[str]):
    trozos = [capa_barrios[capa_barrios.clave == sin_tildes(n)].geometry for n in nombres]
    trozos = [t.iloc[0] for t in trozos if len(t)]
    if not trozos:
        raise SystemExit(f"ninguno de estos barrios está en la capa: {nombres}")
    return unary_union(trozos)


def piezas_en_marco(callejero: gpd.GeoDataFrame, calle: str, marco) -> tuple[list, float]:
    """Los pedazos de la calle dentro del marco, SIN unir, y el largo total de la calle.

    Se cruza contra el polígono y NO contra la columna `barrio` del callejero: en una calle que
    es límite entre dos barrios esa columna trae uno solo, y con ella la mitad del eje se pierde
    sin error. Beláustegui y Rojas son exactamente ese caso en el borde con Villa Crespo.

    Y se devuelven sueltos, sin `unary_union`: la unión fusiona los segmentos contiguos en una
    sola LineString y el cortador de tramos —que decide segmento por segmento— pasa a ver un
    único objeto cuyo punto medio es el medio de toda la calle. Eso devuelve tramos vacíos sin
    tirar ningún error.
    """
    seg = callejero[callejero.clave == sin_tildes(calle)]
    if seg.empty:
        return [], 0.0
    largo_total = float(seg.length.sum())
    piezas = []
    for geometria in seg.geometry:
        if not geometria.intersects(marco):
            continue
        recorte = geometria.intersection(marco)
        if recorte.is_empty:
            continue
        piezas.extend(recorte.geoms if hasattr(recorte, "geoms") else [recorte])
    return [g for g in piezas if getattr(g, "length", 0) > 0], largo_total


def eje_en_marco(callejero: gpd.GeoDataFrame, calle: str, marco):
    piezas, largo_total = piezas_en_marco(callejero, calle, marco)
    if not piezas:
        return None, 0, largo_total
    return unary_union(piezas), len(piezas), largo_total


def tramo_entre(callejero: gpd.GeoDataFrame, calle: str, corte_a: str, corte_b: str, marco):
    """El pedazo de `calle` entre sus cruces con `corte_a` y `corte_b`, dentro del marco."""
    partes, _ = piezas_en_marco(callejero, calle, marco)
    if not partes:
        return None, None, None
    eje = unary_union(partes)
    puntos = []
    for corte in (corte_a, corte_b):
        otra = callejero[callejero.clave == sin_tildes(corte)]
        if otra.empty:
            return None, None, None
        # Si el eje y la calle que corta se tocan, el cruce es la intersección. `nearest_points`
        # con distancia 0 devuelve un punto arbitrario del contacto y puede dar el MISMO punto
        # para dos cortes distintos, lo que produce un tramo de largo cero sin ningún error.
        union_otra = unary_union(list(otra.geometry))
        interseccion = eje.intersection(union_otra)
        puntos.append(interseccion.centroid if not interseccion.is_empty
                      else nearest_points(eje, union_otra)[0])
    a, b = puntos
    dx, dy = b.x - a.x, b.y - a.y
    largo2 = dx * dx + dy * dy
    if largo2 == 0:
        return None, None, None
    elegidos = []
    for pieza in partes:
        centro = pieza.interpolate(0.5, normalized=True)
        t = ((centro.x - a.x) * dx + (centro.y - a.y) * dy) / largo2
        perp = abs((centro.x - a.x) * dy - (centro.y - a.y) * dx) / largo2 ** 0.5
        if -0.02 <= t <= 1.02 and perp <= 200:
            elegidos.append(pieza)
    if not elegidos:
        return None, a, b
    return unary_union(elegidos), a, b


def tramo_por_altura(callejero: gpd.GeoDataFrame, calle: str, desde: int, hasta: int, marco):
    seg = callejero[callejero.clave == sin_tildes(calle)]
    if seg.empty:
        return None, 0
    seg = seg[seg.intersects(marco)]
    if seg.empty:
        return None, 0

    def solapa(fila) -> bool:
        for ini, fin in ((fila.alt_izqini, fila.alt_izqfin), (fila.alt_derini, fila.alt_derfin)):
            if ini and fin and max(ini, fin) >= desde and min(ini, fin) <= hasta:
                return True
        return False

    elegidos = seg[seg.apply(solapa, axis=1)]
    if elegidos.empty:
        return None, 0
    return unary_union(list(elegidos.geometry)), len(elegidos)


def medir(geometria, base: gpd.GeoDataFrame) -> tuple[float, int]:
    return round(geometria.area / 10_000, 2), int(base.within(geometria).sum())


def contencion(nueva, vieja) -> tuple[bool, float, bool]:
    """¿El polígono nuevo conserva íntegro al viejo?

    Se responde por **superficie perdida**, no por el predicado topológico. `covers()` devuelve
    False en R19 sobre una de las tres partes de la envolvente cuya diferencia contra el nuevo
    mide exactamente 0.0 m²: es una falla de robustez de GEOS en `relate` con vértices casi
    colineales, no un polígono que se achicó. La pregunta que importa —«¿queda afuera algún metro
    cuadrado de lo publicado?»— la contesta la superposición, que es exacta acá.

    Devuelve (conserva_todo, superficie_perdida_m2, coincide_el_predicado).
    """
    perdida = vieja.difference(nueva).area
    return perdida <= 1e-6, perdida, bool(nueva.covers(vieja))


def main() -> int:  # noqa: C901
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    buffer = io.StringIO()
    p = p_factory(buffer)

    envolventes = envolventes_22().set_index("referencia_id")
    capa_barrios = barrios()
    callejero = gpd.read_file(CALLEJERO).to_crs(CRS_METRICO)
    callejero["clave"] = callejero.nomoficial.map(sin_tildes)
    base = puntos_base()
    verdes = gpd.read_file(ESPACIOS_VERDES).to_crs(CRS_METRICO)

    p("RONDA 7 · LAS CUATRO DECISIONES DE GEOMETRÍA")
    p("=" * 100)
    p("")
    p(f"  referencias de entrada: {len(envolventes)} · base gastronómica: {len(base):,} puntos")
    p(f"  convención de buffer: {BUFFER_EJE_M} m — la de la ronda 3, una cuadra a cada lado")
    p("  Google Places: 0 requests. Ninguna consulta de red.")
    p("")

    filas: list[dict] = []
    sensibilidad: list[dict] = []
    nuevas_geometrias: dict[str, object] = {}

    # ============================================================ R19 y R21 · ampliación por ejes
    for rid, receta in AMPLIACIONES.items():
        p("-" * 100)
        p(f"  {rid} · {receta['nombre'].upper()} · DECISIÓN {receta['decision']} · SE AMPLÍA")
        p("")
        vieja = envolventes.geometry.loc[rid]
        marco = marco_de(capa_barrios, receta["marco"])
        ha_antes, locales_antes = medir(vieja, base)

        piezas, bitacora = [], []
        for calle in receta["ejes"]:
            eje, n_seg, largo_total = eje_en_marco(callejero, calle, marco)
            if eje is None:
                bitacora.append(f"{calle}: NO cae dentro del marco — se declara y se omite")
                p(f"      {calle:<28} NO cae dentro de {'/'.join(receta['marco'])} — se omite")
                continue
            piezas.append(eje)
            bitacora.append(f"{calle}: {eje.length:,.0f} m dentro del marco "
                            f"(la calle entera mide {largo_total:,.0f} m)")
            p(f"      {calle:<28} {n_seg:>3} segmentos · {eje.length:>7,.0f} m dentro del marco "
              f"(la calle entera: {largo_total:,.0f} m)")

        area_plazas = []
        for plaza in receta["plazas"]:
            encontrada = verdes[verdes.nombre.map(sin_tildes) == sin_tildes(plaza)]
            if encontrada.empty:
                bitacora.append(f"{plaza}: NO está en la capa de espacios verdes — se declara")
                p(f"      {plaza:<28} NO está en la capa oficial de espacios verdes — se omite")
                continue
            poligono = unary_union(list(encontrada.geometry))
            area_plazas.append(poligono)
            bitacora.append(f"{plaza}: polígono oficial de {poligono.area / 10_000:.2f} ha")
            p(f"      {plaza:<28} polígono oficial · {poligono.area / 10_000:>6.2f} ha")

        if not piezas and not area_plazas:
            raise SystemExit(f"{rid}: la ampliación quedó vacía")

        for buffer_m in CURVA_BUFFER_M:
            ampliacion = unary_union(
                [e.buffer(buffer_m) for e in piezas] +
                [g.buffer(buffer_m) for g in area_plazas])
            union = unary_union([vieja, ampliacion])
            ha, locales = medir(union, base)
            sensibilidad.append({
                "referencia_id": rid, "buffer_m": buffer_m, "ha": ha, "locales": locales,
                "delta_ha": round(ha - ha_antes, 2), "delta_locales": locales - locales_antes})

        ampliacion = unary_union(
            [e.buffer(BUFFER_EJE_M) for e in piezas] +
            [g.buffer(BUFFER_EJE_M) for g in area_plazas])
        nueva = unary_union([vieja, ampliacion])
        ha_despues, locales_despues = medir(nueva, base)
        nuevas_geometrias[rid] = nueva

        conserva, perdida, predicado = contencion(nueva, vieja)
        contiguo = ampliacion.intersects(vieja)
        p("")
        p(f"      antes:   {ha_antes:>8,.1f} ha · {locales_antes:>5} locales · "
          f"{locales_antes / ha_antes:>5.2f} locales/ha")
        p(f"      después: {ha_despues:>8,.1f} ha · {locales_despues:>5} locales · "
          f"{locales_despues / ha_despues:>5.2f} locales/ha")
        p(f"      delta:   {ha_despues - ha_antes:>+8,.1f} ha · "
          f"{locales_despues - locales_antes:>+5} locales "
          f"({(locales_despues / locales_antes - 1) * 100:+.1f} %)")
        p("")
        p(f"      CONTENCIÓN · superficie del polígono publicado que queda afuera: "
          f"{perdida:,.6f} m² → {'CONSERVA TODO' if conserva else 'PIERDE SUPERFICIE'}")
        if not predicado:
            p("               (el predicado covers() de GEOS dice NO sobre una geometría cuya "
              "diferencia mide 0.0 m²:")
            p("                es una falla de robustez de relate, no una pérdida. Manda la "
              "superposición.)")
        p(f"      CONTIGÜIDAD · la ampliación toca el polígono publicado: "
          f"{'SÍ' if contiguo else 'NO — el resultado sería un objeto partido'}")
        p("")
        p("      sensibilidad al buffer:")
        for fila_s in [s for s in sensibilidad if s["referencia_id"] == rid]:
            p(f"        {fila_s['buffer_m']:>4} m → {fila_s['ha']:>8,.1f} ha · "
              f"{fila_s['locales']:>5} locales ({fila_s['delta_locales']:+})")
        p("")

        filas.append({
            "referencia_id": rid, "nombre": receta["nombre"], "decision": receta["decision"],
            "accion": "ampliacion", "marco": "; ".join(receta["marco"]),
            "ejes": "; ".join(receta["ejes"]),
            "plazas": "; ".join(receta["plazas"]), "buffer_m": BUFFER_EJE_M,
            "ha_antes": ha_antes, "ha_despues": ha_despues,
            "delta_ha": round(ha_despues - ha_antes, 2),
            "locales_antes": locales_antes, "locales_despues": locales_despues,
            "delta_locales": locales_despues - locales_antes,
            "delta_locales_pct": round((locales_despues / locales_antes - 1) * 100, 1),
            "conserva_todo_lo_publicado": bool(conserva),
            "superficie_del_viejo_perdida_m2": round(perdida, 6),
            "predicado_covers_geos": bool(predicado),
            "ampliacion_contigua": bool(contiguo),
            "bitacora": " | ".join(bitacora), "motivo": receta["motivo"],
        })

    # ==================================================================== R20 · revisión del corte
    p("-" * 100)
    p("  R20 · GARCIA DEL RIO · DECISIÓN 7 · SE REVISA EL CORTE")
    p("")
    vieja = envolventes.geometry.loc["R20"]
    marco = marco_de(capa_barrios, R20_TRAMO["marco"])
    ha_antes, locales_antes = medir(vieja, base)
    tramo, punto_a, punto_b = tramo_entre(callejero, R20_TRAMO["eje"], R20_TRAMO["corte_a"],
                                          R20_TRAMO["corte_b"], marco)
    if tramo is None:
        raise SystemExit("R20: no se pudo resolver el tramo entre Cabildo y Balbín")
    eje_entero, _, largo_entero = eje_en_marco(callejero, R20_TRAMO["eje"], marco)
    p(f"      García del Río dentro de Saavedra: {eje_entero.length:,.0f} m")
    p(f"      el tramo Cabildo → Balbín:         {tramo.length:,.0f} m "
      f"({tramo.length / eje_entero.length * 100:.0f} % del eje)")
    p(f"      distancia entre los dos cortes:    {punto_a.distance(punto_b):,.0f} m")
    p("")

    for buffer_m in CURVA_BUFFER_M:
        union = unary_union([vieja, tramo.buffer(buffer_m)])
        ha, locales = medir(union, base)
        sensibilidad.append({"referencia_id": "R20", "buffer_m": buffer_m, "ha": ha,
                             "locales": locales, "delta_ha": round(ha - ha_antes, 2),
                             "delta_locales": locales - locales_antes})

    solo_tramo = tramo.buffer(BUFFER_EJE_M)
    ha_tramo, locales_tramo = medir(solo_tramo, base)
    nueva = unary_union([vieja, solo_tramo])
    ha_despues, locales_despues = medir(nueva, base)
    nuevas_geometrias["R20"] = nueva
    conserva, perdida, predicado = contencion(nueva, vieja)
    contiguo = solo_tramo.intersects(vieja)
    fuera = vieja.difference(solo_tramo).area / 10_000

    p(f"      antes (la envolvente publicada):  {ha_antes:>8,.1f} ha · {locales_antes:>5} locales")
    p(f"      el tramo de la decisión, solo:    {ha_tramo:>8,.1f} ha · {locales_tramo:>5} locales")
    p(f"      la unión que se adopta:           {ha_despues:>8,.1f} ha · "
      f"{locales_despues:>5} locales")
    p(f"      delta contra lo publicado:        {ha_despues - ha_antes:>+8,.1f} ha · "
      f"{locales_despues - locales_antes:>+5} locales")
    p("")
    p(f"      CONTENCIÓN · superficie del polígono publicado que queda afuera: "
      f"{perdida:,.6f} m² → {'CONSERVA TODO' if conserva else 'PIERDE SUPERFICIE'}")
    p(f"      CONTIGÜIDAD · el tramo toca el polígono publicado: {'SÍ' if contiguo else 'NO'}")
    p("")
    p(f"      LO QUE LA REVISIÓN DEL CORTE DEJA A LA VISTA: {fuera:,.1f} ha de la envolvente")
    p("      publicada quedan FUERA del tramo que la decisión describe. La regla de contención")
    p("      las conserva, así que el polígono adoptado es la unión y no el tramo. Si en algún")
    p("      momento se decide que la envolvente publicada estaba mal cortada, ése es el número")
    p("      que hay que discutir — y es una decisión sobre lo publicado, no sobre la grilla.")
    p("")
    p("      sensibilidad al buffer:")
    for fila_s in [s for s in sensibilidad if s["referencia_id"] == "R20"]:
        p(f"        {fila_s['buffer_m']:>4} m → {fila_s['ha']:>8,.1f} ha · "
          f"{fila_s['locales']:>5} locales ({fila_s['delta_locales']:+})")
    p("")

    filas.append({
        "referencia_id": "R20", "nombre": R20_TRAMO["nombre"], "decision": 7,
        "accion": "revision_del_corte", "marco": "; ".join(R20_TRAMO["marco"]),
        "ejes": f"{R20_TRAMO['eje']} entre {R20_TRAMO['corte_a']} y {R20_TRAMO['corte_b']}",
        "plazas": "", "buffer_m": BUFFER_EJE_M,
        "ha_antes": ha_antes, "ha_despues": ha_despues,
        "delta_ha": round(ha_despues - ha_antes, 2),
        "locales_antes": locales_antes, "locales_despues": locales_despues,
        "delta_locales": locales_despues - locales_antes,
        "delta_locales_pct": round((locales_despues / locales_antes - 1) * 100, 1),
        "conserva_todo_lo_publicado": bool(conserva),
        "superficie_del_viejo_perdida_m2": round(perdida, 6),
        "predicado_covers_geos": bool(predicado),
        "ampliacion_contigua": bool(contiguo),
        "bitacora": f"tramo de {tramo.length:,.0f} m sobre un eje de {eje_entero.length:,.0f} m "
                    f"dentro de Saavedra | el tramo solo mide {ha_tramo} ha y {locales_tramo} "
                    f"locales | {fuera:.1f} ha de lo publicado quedan fuera del tramo y se "
                    f"conservan por la regla de contención",
        "motivo": R20_TRAMO["motivo"],
    })

    # ================================================================= R18 · absorción en Z46
    p("-" * 100)
    p("  R18 · ESMERALDA-PARAGUAY · DECISIÓN 5 · SE ABSORBE EN Z46 RETIRO")
    p("")
    r18 = envolventes.geometry.loc["R18"]
    ha_r18, locales_r18 = medir(r18, base)
    marco_retiro = marco_de(capa_barrios, CLUSTER_COREANO["marco"])
    solo_retiro = marco_de(capa_barrios, ["Retiro"])

    piezas_cluster, bitacora_cluster = [], []
    for calle in CLUSTER_COREANO["ejes"]:
        eje, n_seg = tramo_por_altura(callejero, calle, CLUSTER_COREANO["altura_desde"],
                                      CLUSTER_COREANO["altura_hasta"], marco_retiro)
        if eje is None:
            bitacora_cluster.append(f"{calle} {CLUSTER_COREANO['altura_desde']}-"
                                    f"{CLUSTER_COREANO['altura_hasta']}: sin tramo — se declara")
            p(f"      {calle:<24} sin tramo en el rango de alturas — se declara")
            continue
        piezas_cluster.append(eje)
        bitacora_cluster.append(f"{calle}: {n_seg} segmentos, {eje.length:,.0f} m")
        p(f"      {calle:<24} {n_seg:>2} segmentos · {eje.length:>6,.0f} m "
          f"(alturas {CLUSTER_COREANO['altura_desde']}-{CLUSTER_COREANO['altura_hasta']})")

    cluster = unary_union([e.buffer(BUFFER_EJE_M) for e in piezas_cluster])
    ha_cluster, locales_cluster = medir(cluster, base)
    p("")
    p(f"      el clúster coreano-asiático: {ha_cluster:>7,.1f} ha · {locales_cluster:>4} locales")
    p(f"      R18 tal como está publicada:  {ha_r18:>7,.1f} ha · {locales_r18:>4} locales")
    p(f"      R18 es {ha_r18 / ha_cluster:.1f} veces el clúster que dice representar")
    p("")

    cubre = cluster.intersection(r18).area / cluster.area * 100
    p(f"      del clúster, R18 cubre el {cubre:.1f} % de la superficie")
    fuera_retiro = r18.difference(solo_retiro).area / r18.area * 100
    p(f"      de R18, el {fuera_retiro:.1f} % cae FUERA del barrio de Retiro "
      "(el derrame a San Nicolás que la decisión anticipa)")
    p("")
    subzona = unary_union([r18, cluster])
    ha_sub, locales_sub = medir(subzona, base)
    nuevas_geometrias["Z46_SUBZONA_CLUSTER_COREANO"] = subzona
    p(f"      la subzona que queda dentro de Z46 (R18 ∪ clúster): {ha_sub:,.1f} ha · "
      f"{locales_sub} locales")
    p("")
    p("      QUÉ SE HIZO Y QUÉ NO. R18 deja de ser referencia independiente: pasa a subzona de")
    p("      Z46 Retiro. NO se dibuja acá el polígono de Z46 —Z46 es una zona nueva y su")
    p("      delimitación no es una de las cuatro decisiones de geometría—: la zona se mide por")
    p("      barrio, como todas las nuevas, en `ronda_7_familias_de_vias.py`.")
    p("")

    filas.append({
        "referencia_id": "R18", "nombre": "Esmeralda-Paraguay", "decision": 5,
        "accion": "absorcion_en_Z46", "marco": "; ".join(CLUSTER_COREANO["marco"]),
        "ejes": "; ".join(CLUSTER_COREANO["ejes"]), "plazas": "", "buffer_m": BUFFER_EJE_M,
        "ha_antes": ha_r18, "ha_despues": ha_sub, "delta_ha": round(ha_sub - ha_r18, 2),
        "locales_antes": locales_r18, "locales_despues": locales_sub,
        "delta_locales": locales_sub - locales_r18,
        "delta_locales_pct": round((locales_sub / locales_r18 - 1) * 100, 1),
        "conserva_todo_lo_publicado": bool(contencion(subzona, r18)[0]),
        "superficie_del_viejo_perdida_m2": round(r18.difference(subzona).area, 6),
        "predicado_covers_geos": bool(contencion(subzona, r18)[2]),
        "ampliacion_contigua": bool(cluster.intersects(r18)),
        "bitacora": " | ".join(bitacora_cluster) +
                    f" | el clúster mide {ha_cluster} ha y R18 mide {ha_r18} ha "
                    f"({ha_r18 / ha_cluster:.1f}×) | R18 cubre el {cubre:.1f} % del clúster | "
                    f"el {fuera_retiro:.1f} % de R18 cae fuera del barrio de Retiro",
        "motivo": "R18 deja de existir como referencia independiente. El clúster coreano-asiático "
                  "cubre el punto exacto de Esmeralda y Paraguay y R18 es varias veces más grande "
                  "que el clúster que dice representar.",
    })

    # ============================================================ la capa de salida
    p("-" * 100)
    p("  LA CAPA DE REFERENCIAS DESPUÉS DE LAS CUATRO DECISIONES")
    p("")
    salida = []
    for rid, fila in envolventes.iterrows():
        if rid == "R18":
            continue
        geometria = nuevas_geometrias.get(rid, fila.geometry)
        salida.append({"referencia_id": rid, "nombre": fila.nombre, "familia": fila.familia,
                       "estado_r7": "ampliada" if rid in nuevas_geometrias else "sin cambios",
                       "ha": round(geometria.area / 10_000, 2),
                       "locales": int(base.within(geometria).sum()),
                       "geometry": geometria})
    salida.append({
        "referencia_id": "Z46_SUBZONA_CLUSTER_COREANO",
        "nombre": "Retiro · subzona del clúster coreano-asiático (ex R18)",
        "familia": "subzona", "estado_r7": "absorbida en Z46",
        "ha": round(subzona.area / 10_000, 2), "locales": int(base.within(subzona).sum()),
        "geometry": subzona})
    capa = gpd.GeoDataFrame(salida, geometry="geometry", crs=CRS_METRICO)

    p(f"  referencias antes: {len(envolventes)} · después: "
      f"{len([s for s in salida if not s['referencia_id'].startswith('Z46')])} "
      "+ 1 subzona de Z46")
    p("")
    for fila in capa.itertuples():
        marca = "←" if fila.estado_r7 != "sin cambios" else " "
        p(f"   {marca} {fila.referencia_id:<28} {fila.nombre[:38]:<40} {fila.ha:>8,.1f} ha · "
          f"{fila.locales:>5} locales · {fila.estado_r7}")
    p("")

    # ---------------------------------------------------------------- solapes nuevos
    #
    # Una ampliación no sólo agranda: puede pisar a la referencia de al lado. Las 22 tienen regla
    # de precedencia por solape para contar sin duplicar, y si una ampliación crea un solape que
    # antes no existía, ese conteo cambia sin que nadie lo pida. Se mide antes y después.
    p("  SOLAPES ENTRE REFERENCIAS · ANTES Y DESPUÉS DE LAS AMPLIACIONES")
    p("")
    solapes = []
    ids = [r for r in envolventes.index if r != "R18"]
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            vieja_a, vieja_b = envolventes.geometry.loc[a], envolventes.geometry.loc[b]
            nueva_a = nuevas_geometrias.get(a, vieja_a)
            nueva_b = nuevas_geometrias.get(b, vieja_b)
            antes = vieja_a.intersection(vieja_b).area / 10_000
            despues = nueva_a.intersection(nueva_b).area / 10_000
            if despues > 0.01 or antes > 0.01:
                solapes.append({"a": a, "b": b, "ha_antes": round(antes, 2),
                                "ha_despues": round(despues, 2),
                                "delta_ha": round(despues - antes, 2),
                                "nuevo": antes <= 0.01 < despues})
    if not solapes:
        p("   ninguna pareja de referencias se pisa, ni antes ni después.")
    for fila_s in sorted(solapes, key=lambda s: -s["delta_ha"]):
        marca = "NUEVO" if fila_s["nuevo"] else "     "
        p(f"   {marca} {fila_s['a']} ∩ {fila_s['b']}: {fila_s['ha_antes']:>7,.2f} ha → "
          f"{fila_s['ha_despues']:>7,.2f} ha ({fila_s['delta_ha']:+,.2f})")
    nuevos_solapes = [s for s in solapes if s["nuevo"]]
    p("")
    if nuevos_solapes:
        p(f"   {len(nuevos_solapes)} solape(s) que ANTES NO EXISTÍAN. No se resuelven acá: la")
        p("   precedencia por solape es una decisión editorial de las 22, no un ajuste de")
        p("   geometría. Queda medido y a la vista.")
    else:
        p("   ninguna ampliación crea un solape que antes no existiera.")
    p("")
    pd.DataFrame(solapes).to_csv(GEOMETRIA / "solapes_r7.csv", index=False, encoding="utf-8") \
        if solapes else None

    # verificación global de contención: ninguna de las 21 perdió superficie
    p("  VERIFICACIÓN GLOBAL DE CONTENCIÓN")
    p("")
    rotas = []
    for rid in envolventes.index:
        if rid == "R18":
            continue
        vieja_g = envolventes.geometry.loc[rid]
        nueva_g = nuevas_geometrias.get(rid, vieja_g)
        perdida_g = vieja_g.difference(nueva_g).area
        if perdida_g > 1e-6:
            rotas.append((rid, perdida_g))
    if rotas:
        for rid, perdida_g in rotas:
            p(f"   ✗ {rid}: {perdida_g:,.4f} m² del polígono publicado quedan afuera")
        raise SystemExit(f"contención rota en {len(rotas)} referencias")
    p("   ✓ las 21 referencias que siguen vigentes conservan íntegro su polígono publicado:")
    p("     ni un metro cuadrado de lo publicado queda fuera de lo que sale de esta corrida")
    conserva_r18, perdida_r18, _ = contencion(subzona, r18)
    p(f"   {'✓' if conserva_r18 else '✗'} R18 queda dentro de la subzona de Z46 · "
      f"superficie perdida: {perdida_r18:,.6f} m²")
    p("")

    GEOMETRIA.mkdir(parents=True, exist_ok=True)
    capa.to_crs("EPSG:4326").to_file(OUT_GEOJSON, driver="GeoJSON")
    pd.DataFrame(filas).to_csv(OUT_CSV, index=False, encoding="utf-8")
    pd.DataFrame(sensibilidad).to_csv(OUT_SENSIBILIDAD, index=False, encoding="utf-8")

    p("-" * 100)
    p(f"  {OUT_GEOJSON.relative_to(BARRIDO)} · {len(capa)} geometrías")
    p(f"  {OUT_CSV.relative_to(BARRIDO)} · {len(filas)} decisiones aplicadas")
    p("  Google Places: 0 requests.")

    texto = buffer.getvalue()
    INFORME_TXT.write_text(texto, encoding="utf-8")
    print(texto)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
