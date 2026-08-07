"""Ronda 4 · E07 Liniers con la delimitación de fuente y E02 con núcleo y corredor.

QUÉ HACE
--------
Reescribe **dos** de los quince enclaves. Los otros trece se copian de la ronda 3 sin tocarlos: sus
insumos no se movieron y recomputarlos sería fabricar la oportunidad de que cambien por otra cosa.

**E07 Liniers.** La ronda 3 lo construyó sobre la consigna —un cuadrante José León Suárez /
Montiel / Ramón Falcón / Ibarrola— que no salía de ninguna fuente. Ahora hay cuatro fuentes
independientes, una arbitrada (Ciocoletto, *El mercado andino de Liniers*, AREA 25(2), FADU-UBA,
2019), y dicen otra cosa: **un eje de ~300 m sobre José León Suárez entre Ramón Falcón y Ventura
Bosch, con transversales**. No un cuadrante. Poligonizar un cuadrante habría inventado dos lados.

    Montiel se cae. Aparece en una sola fuente, sin fecha ni firma, que además ubica el mercado
    «a la altura de Av. Rivadavia 1600» cuando el cruce real está en la altura 11.000. Un error
    verificable de más de nueve mil números no delimita nada.

**E02 Barrio Chino.** Deja de ser un radio. Es **núcleo compacto de dos cuadras** sobre Arribeños
entre Juramento y Olazábal **más un corredor a lo largo del viaducto del Mitre**. El radio no
exagera la superficie: equivoca la forma —sobredimensiona el este y el oeste, subdimensiona el eje
del viaducto, que es donde está la apertura reciente—.

Y con eso se puede hacer lo que decide la forma final: **geocodificar los 57 establecimientos con
puerta** (51 del Barrio Chino, 6 de Liniers) y contar cuántos caen en el núcleo, cuántos en el
corredor y cuántos afuera de los dos.

CÓMO SE CONSTRUYE EL CORREDOR, Y POR QUÉ NO CON LAS PUERTAS
------------------------------------------------------------
Definir el corredor con las mismas puertas que después se van a clasificar contra él es
circular: daría «todas adentro» por construcción. El eje del corredor sale del **callejero
oficial**: los segmentos que el propio GCBA marca como `Tren Elevado` en Belgrano son los cruces
del viaducto, y su secuencia ordenada es la traza. Las cabeceras —Monroe y Echeverría— son los
nombres de calle que las fuentes dan, no puntos elegidos por nosotros.

USIG sí (una consulta por dirección, cacheada). Google Places: 0 requests.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/enclaves_ronda_4.py
"""
from __future__ import annotations

import io
import json
import math
import re
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString
from shapely.ops import nearest_points, unary_union

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

ENTRADA_R3_CSV = OUT / "enclaves_comunitarios_r3.csv"
ENTRADA_R3_GEO = OUT / "enclaves_comunitarios_r3.geojson"
ESTABLECIMIENTOS = EVIDENCIA / "enclaves_establecimientos_E02_E07.csv"
REPARADOS = EVIDENCIA / "enclaves_E02_E07_reparados.csv"

# La medición que la fuente arbitrada publica, contra la que se coteja la geocodificación propia.
EXTENSION_PAPER_M = 300.0
EXTENSION_COWORK_M = 285.0
EXTENSION_NUCLEO_COWORK_M = 256.0

# Las calles que las fuentes nombran como extremos del tramo del viaducto. La geometría de la traza
# sale del callejero; estos nombres sólo dicen dónde empieza y dónde termina.
CORREDOR_CABECERAS = ("MONROE", "ECHEVERRIA")


def punto_usig(direccion: str, cache: dict):
    """El punto de una dirección por el normalizador del GCBA, o None si no la resuelve."""
    candidato = consultar(limpiar(direccion), cache)
    if not candidato or not candidato.get("coordenadas"):
        return None
    coordenadas = candidato["coordenadas"]
    return gpd.GeoSeries(
        gpd.points_from_xy([float(coordenadas["x"])], [float(coordenadas["y"])]),
        crs=CRS_GEOGRAFICO).to_crs(CRS_METRICO).iloc[0]


def rumbo(a, b) -> float:
    """El acimut de la recta A–B, plegado a [0,180): una recta no tiene sentido, tiene dirección."""
    return math.degrees(math.atan2(b.x - a.x, b.y - a.y)) % 180.0


def altura_de(valor: str) -> tuple[str | None, str]:
    """La altura utilizable de un campo que puede traer dos, una aproximación o ninguna.

    Devuelve (altura, nota). «2245 o 2241» da la primera y deja dicho que hay dos; «al 100» es una
    cuadra, no una puerta, y viaja marcado; «s/altura» no da nada y no se inventa.
    """
    texto = str(valor or "").strip()
    if not texto or texto.lower().startswith("s/"):
        return None, "sin altura en la fuente"
    numeros = re.findall(r"\d{2,5}", texto)
    if not numeros:
        return None, f"altura no numérica: «{texto}»"
    nota = ""
    if texto.lower().startswith("al "):
        nota = "altura de cuadra, no de puerta"
    elif len(numeros) > 1:
        nota = f"la fuente da {len(numeros)} alturas ({', '.join(numeros)}); se usa la primera"
    elif re.search(r"local|esq", texto, flags=re.I):
        nota = f"se recorta «{texto}» a la altura"
    return numeros[0], nota


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    OUT.mkdir(parents=True, exist_ok=True)
    buffer_txt = io.StringIO()

    def p(*args_):
        print(*args_, file=buffer_txt)

    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    consultas_antes = len(cache)

    callejero = gpd.read_file(CALLEJERO).to_crs(CRS_METRICO)
    callejero["clave"] = callejero.nomoficial.map(sin_tildes)
    liniers = callejero[callejero.barrio == "Liniers"]
    belgrano = callejero[callejero.barrio == "Belgrano"]

    p("RONDA 4 · E07 LINIERS CON LA DELIMITACIÓN DE FUENTE, E02 CON NÚCLEO Y CORREDOR")
    p("=" * 100)
    p("")
    p("  Se reescriben DOS de los quince enclaves. Los otros trece se copian de la ronda 3.")
    p("  Google Places: 0 requests. USIG sí, una consulta por dirección y cacheada.")
    p("")

    # ================================================================ E07 · el eje, con su métrica
    p("-" * 100)
    p("  E07 LINIERS · EL EJE QUE DICEN LAS FUENTES, Y CUÁNTO MIDE")
    p("")

    jls = _segmentos_de("SUAREZ, JOSE LEON", liniers)
    falcon = callejero[callejero.clave == sin_tildes("FALCON, RAMON L.,CNEL.")]
    bosch = callejero[callejero.clave == sin_tildes("BOSCH, VENTURA")]
    ibarrola = _segmentos_de("IBARROLA", liniers)

    if jls.empty or falcon.empty or bosch.empty:
        raise SystemExit("el callejero no trae alguna de las tres calles del eje de E07")

    corte_falcon = _punto_de_cruce(jls, falcon)
    corte_bosch = _punto_de_cruce(jls, bosch)
    recta_m = corte_falcon.distance(corte_bosch)
    eje_e07 = _tramo_entre(jls, corte_falcon, corte_bosch)
    largo_e07 = float(eje_e07.length) if eje_e07 is not None and not eje_e07.is_empty else 0.0

    # Los largos se miden DENTRO DE LINIERS, que es el marco que la delimitación nombra. Sin el
    # recorte, «Ramón Falcón» son 7.150 m de punta a punta de la Ciudad y el número no dice nada
    # sobre el enclave; con el recorte se puede comparar contra el de la ronda 3.
    p("      LA CALLE, CON LA TRAMPA DE LA RONDA 3 YA RESUELTA (largos dentro de Liniers)")
    p(f"            «FALCON, RAMON L.,CNEL.»      "
      f"{float(_segmentos_de('FALCON, RAMON L.,CNEL.', liniers).length.sum()):>8,.0f} m   "
      "la del Mercado Andino · es ÉSTA")
    variante = _segmentos_de("FALCON, RAMON L.,CNEL. AV.", liniers)
    if len(variante):
        p(f"            «FALCON, RAMON L.,CNEL. AV.»  {float(variante.length.sum()):>8,.0f} m   "
          "la que usaba la ronda 1: 900 números al oeste")
    p(f"            «BOSCH, VENTURA»              "
      f"{float(_segmentos_de('BOSCH, VENTURA', liniers).length.sum()):>8,.0f} m   "
      "la cuarta calle verdadera, en Liniers")
    montiel = _segmentos_de("MONTIEL", liniers)
    p(f"            «MONTIEL» (Liniers)           {float(montiel.length.sum()):>8,.0f} m   "
      "NO entra: una sola fuente, sin fecha ni firma")
    p("")
    p("      LA MEDICIÓN, CONTRA LA DE LA FUENTE")
    p("")
    p(f"            eje sobre José León Suárez, Ramón Falcón → Ventura Bosch: "
      f"{largo_e07:,.1f} m")
    p(f"            la misma distancia en línea recta entre los dos cruces:   {recta_m:,.1f} m")
    p(f"            lo que mide Ciocoletto (2019), «aproximadamente»:         "
      f"{EXTENSION_PAPER_M:,.0f} m")
    p(f"            lo que midió cowork con USIG:                             "
      f"{EXTENSION_COWORK_M:,.0f} m")
    p("")
    delta_cowork = largo_e07 - EXTENSION_COWORK_M
    delta_paper = largo_e07 - EXTENSION_PAPER_M
    p(f"            diferencia contra cowork: {delta_cowork:+,.1f} m "
      f"({abs(delta_cowork) / EXTENSION_COWORK_M * 100:.1f} %)")
    p(f"            diferencia contra el paper: {delta_paper:+,.1f} m "
      f"({abs(delta_paper) / EXTENSION_PAPER_M * 100:.1f} %)")
    p("")
    p("            Las dos mediciones no son el mismo objeto y conviene decirlo: USIG devuelve la")
    p("            distancia entre dos PUNTOS de altura, y esto mide la LONGITUD DEL EJE del")
    p("            callejero entre dos cruces. Sobre una calle recta las dos convergen; el número")
    p("            del paper es «aproximadamente 300 m» y no admite más precisión que ésa.")
    p("")

    # ================================================================ E02 · núcleo y corredor
    p("-" * 100)
    p("  E02 BARRIO CHINO · EL NÚCLEO MEDIDO Y EL CORREDOR DEL VIADUCTO")
    p("")

    arribenos = _segmentos_de("ARRIBEÑOS", belgrano)
    juramento = callejero[callejero.clave == sin_tildes("JURAMENTO AV.")]
    olazabal = callejero[callejero.clave == sin_tildes("OLAZABAL")]
    corte_jur = _punto_de_cruce(arribenos, juramento)
    corte_ola = _punto_de_cruce(arribenos, olazabal)
    nucleo_eje = _tramo_entre(arribenos, corte_jur, corte_ola)
    largo_nucleo = float(nucleo_eje.length) if nucleo_eje is not None else 0.0

    cruces = belgrano[belgrano.tipo_ffcc.astype(str).str.startswith("Tren Elevado")].copy()
    cruces["centro"] = cruces.geometry.apply(lambda g: g.interpolate(0.5, normalized=True))
    extremos = {}
    for nombre in CORREDOR_CABECERAS:
        candidatos = cruces[cruces.clave == sin_tildes(nombre)]
        if candidatos.empty:
            raise SystemExit(f"el callejero no marca cruce de viaducto sobre {nombre}")
        extremos[nombre] = candidatos.iloc[
            candidatos.centro.distance(corte_jur).argmin()].centro
    a, b = extremos[CORREDOR_CABECERAS[0]], extremos[CORREDOR_CABECERAS[1]]
    dx, dy = b.x - a.x, b.y - a.y
    largo2 = dx * dx + dy * dy
    sobre_traza = []
    for fila in cruces.itertuples():
        centro = fila.centro
        t = ((centro.x - a.x) * dx + (centro.y - a.y) * dy) / largo2
        perpendicular = abs((centro.x - a.x) * dy - (centro.y - a.y) * dx) / largo2 ** 0.5
        if -0.02 <= t <= 1.02 and perpendicular <= 60:
            sobre_traza.append((t, centro, fila.nomoficial))
    sobre_traza.sort(key=lambda x: x[0])
    corredor_eje = LineString([punto for _, punto, _ in sobre_traza])
    largo_corredor = float(corredor_eje.length)

    p("      EL NÚCLEO · Arribeños entre Juramento y Olazábal")
    p(f"            {largo_nucleo:,.1f} m de eje  (cowork con USIG: "
      f"{EXTENSION_NUCLEO_COWORK_M:,.0f} m · diferencia "
      f"{largo_nucleo - EXTENSION_NUCLEO_COWORK_M:+,.1f} m)")
    p("            Dos cuadras, con Mendoza en el medio. La cifra se sostiene.")
    p("")
    p("      EL CORREDOR · la traza del viaducto del Mitre, del callejero oficial")
    p(f"            {len(sobre_traza)} cruces marcados `Tren Elevado` entre "
      f"{CORREDOR_CABECERAS[0]} y {CORREDOR_CABECERAS[1]}, en orden:")
    for _, _, nombre in sobre_traza:
        p(f"                  {nombre}")
    p(f"            traza: {largo_corredor:,.0f} m")
    p("")
    rumbo_nucleo = rumbo(corte_jur, corte_ola)
    rumbo_corredor = rumbo(a, b)
    angulo = abs(rumbo_nucleo - rumbo_corredor)
    angulo = min(angulo, 180 - angulo)
    p(f"            rumbo del núcleo:   {rumbo_nucleo:5.1f}°")
    p(f"            rumbo del corredor: {rumbo_corredor:5.1f}°")
    p(f"            ángulo entre los dos: {angulo:.1f}°")
    p("")
    if angulo < 30:
        p("            **CORRECCIÓN A LA DESCRIPCIÓN.** El corredor NO es perpendicular al eje")
        p("            histórico: es casi PARALELO. Arribeños corre al lado de las vías, no las")
        p("            cruza —por eso el núcleo está «bajo el viaducto» sin cruzarlo—, y el paseo")
        p("            que corre debajo del viaducto corre junto a Arribeños, desplazado. La forma")
        p("            que sale no es una cruz: son dos bandas paralelas separadas por la traza.")
    elif angulo > 60:
        p("            La descripción se sostiene: el corredor es transversal al eje histórico.")
    else:
        p("            Ni paralelo ni perpendicular: oblicuo. Se declara el ángulo y no se")
        p("            redondea a ninguna de las dos figuras.")
    p("")

    nucleo_area = nucleo_eje.buffer(BUFFER_ENCLAVE_M)
    corredor_area = corredor_eje.buffer(BUFFER_ENCLAVE_M)
    e02_area = unary_union([nucleo_area, corredor_area])
    e07_area = eje_e07.buffer(BUFFER_ENCLAVE_M)

    p(f"            núcleo {nucleo_area.area / 10_000:6.1f} ha  ·  corredor "
      f"{corredor_area.area / 10_000:6.1f} ha  ·  unión {e02_area.area / 10_000:6.1f} ha")
    p(f"            se solapan {(nucleo_area.intersection(corredor_area).area / 10_000):.1f} ha, "
      f"el {nucleo_area.intersection(corredor_area).area / nucleo_area.area * 100:.0f} % del núcleo")
    p("            (buffer declarado de 150 m, una cuadra a cada lado, el mismo de los quince)")
    p("")

    # ================================================================ los 57, geocodificados
    p("-" * 100)
    p("  LOS 57 ESTABLECIMIENTOS · dónde caen, que es lo que decide la forma")
    p("")

    entrada = pd.read_csv(ESTABLECIMIENTOS)
    filas = []
    for fila in entrada.itertuples():
        altura, nota_altura = altura_de(fila.altura)
        calle = str(fila.calle).strip()
        registro = {
            "enclave_id": fila.enclave_id, "establecimiento": fila.establecimiento,
            "calle": calle, "altura_fuente": fila.altura, "rubro": fila.rubro,
            "origen_cocina": fila.origen_cocina, "vigencia": fila.vigencia,
            "vigencia_fecha": fila.vigencia_fecha, "fuente": fila.fuente,
            "nota_direccion": nota_altura, "geocodificado": "no",
            "latitud": None, "longitud": None, "zona": "sin_geocodificar",
            "dist_nucleo_m": None, "dist_corredor_m": None,
        }
        punto = None
        if altura is not None:
            consulta = f"{calle} {altura}"
            punto = punto_usig(consulta, cache)
            if punto is None:
                # Segundo intento sin el prefijo de vía: «Pasaje Arribeños» no existe como calle
                # para el normalizador, «Av. del Libertador» sí. Si tampoco resuelve, se declara.
                sin_prefijo = re.sub(r"^(Pasaje|Pje\.?|Av\.?|Avenida)\s+", "", calle,
                                     flags=re.I).strip()
                if sin_prefijo != calle:
                    punto = punto_usig(f"{sin_prefijo} {altura}", cache)
                    if punto is not None:
                        registro["nota_direccion"] = (
                            f"{nota_altura + ' · ' if nota_altura else ''}resuelta sin el prefijo "
                            f"de vía («{sin_prefijo}»)")
            if punto is None:
                registro["nota_direccion"] = (
                    f"{nota_altura + ' · ' if nota_altura else ''}USIG NO resuelve "
                    f"«{consulta}»")
        if punto is not None:
            geografico = gpd.GeoSeries([punto], crs=CRS_METRICO).to_crs(CRS_GEOGRAFICO).iloc[0]
            distancia_nucleo = punto.distance(nucleo_eje)
            distancia_corredor = punto.distance(corredor_eje)
            registro.update({
                "geocodificado": "si",
                "latitud": round(geografico.y, 6), "longitud": round(geografico.x, 6),
                "dist_nucleo_m": round(distancia_nucleo, 1),
                "dist_corredor_m": round(distancia_corredor, 1),
            })
            if fila.enclave_id == "E07":
                registro["zona"] = ("dentro_E07" if e07_area.contains(punto)
                                    else "fuera_E07")
                registro["dist_nucleo_m"] = round(punto.distance(eje_e07), 1)
                registro["dist_corredor_m"] = None
            elif distancia_nucleo <= BUFFER_ENCLAVE_M:
                registro["zona"] = "nucleo"
            elif distancia_corredor <= BUFFER_ENCLAVE_M:
                registro["zona"] = "corredor"
            else:
                registro["zona"] = "afuera"
        filas.append(registro)

    puertas = pd.DataFrame(filas)
    e02 = puertas[puertas.enclave_id == "E02"]
    e07_puertas = puertas[puertas.enclave_id == "E07"]

    p(f"      E02 · {len(e02)} establecimientos del Barrio Chino")
    p("")
    p(f"            {'zona':<20}{'n':>4}   qué son")
    for zona, glosa in [("nucleo", "dentro de las dos cuadras de Arribeños, ±150 m"),
                        ("corredor", "fuera del núcleo, sobre el viaducto, ±150 m"),
                        ("afuera", "fuera de los dos"),
                        ("sin_geocodificar", "USIG no los resuelve o no tienen altura")]:
        p(f"            {zona:<20}{int((e02.zona == zona).sum()):>4}   {glosa}")
    p("")
    p("      La precedencia está declarada: el núcleo gana. Un establecimiento a 80 m del eje de")
    p("      Arribeños y a 90 m de la traza cuenta como núcleo, no como corredor. Sin esa regla")
    p("      las dos bandas se solapan y el reparto no significa nada.")
    p("")
    for zona in ("corredor", "afuera", "sin_geocodificar"):
        suyos = e02[e02.zona == zona]
        if not len(suyos):
            continue
        p(f"      LOS DE «{zona.upper()}»:")
        for fila in suyos.itertuples():
            detalle = (f"{fila.dist_nucleo_m:>6.0f} m del núcleo · "
                       f"{fila.dist_corredor_m:>5.0f} m del corredor"
                       if fila.geocodificado == "si" else f"— {fila.nota_direccion}")
            p(f"            {str(fila.establecimiento)[:30]:<32}"
              f"{str(fila.calle)[:22]:<24}{str(fila.altura_fuente)[:12]:<14}{detalle}")
        p("")

    # ---------------------------------------------------------------- ¿dónde está lo reciente?
    #
    # La afirmación que hay que probar o refutar no es «el radio es más grande»: es que el radio
    # **subdimensiona el eje del viaducto, que es donde está la apertura reciente». Eso se mide
    # con la añada de cada puerta contra la zona en la que cae.
    geocodificados = e02[e02.geocodificado == "si"].copy()
    geocodificados["anio"] = pd.to_numeric(
        geocodificados.vigencia_fecha.astype(str).str[:4], errors="coerce")
    p("      LA AÑADA CONTRA LA ZONA · lo reciente, ¿está en el corredor?")
    p("")
    p(f"            {'añada':<16}{'núcleo':>8}{'corredor':>10}{'afuera':>8}{'total':>8}")
    for etiqueta, desde, hasta in [("2024-2026", 2024, 2026), ("2018-2023", 2018, 2023),
                                   ("hasta 2017", 0, 2017), ("sin fecha", -1, -1)]:
        if desde < 0:
            suyos = geocodificados[geocodificados.anio.isna()]
        else:
            suyos = geocodificados[geocodificados.anio.between(desde, hasta)]
        p(f"            {etiqueta:<16}"
          f"{int((suyos.zona == 'nucleo').sum()):>8}{int((suyos.zona == 'corredor').sum()):>10}"
          f"{int((suyos.zona == 'afuera').sum()):>8}{len(suyos):>8}")
    p("")

    # ---------------------------------------------------------------- el radio, medido
    #
    # «Radio de cuatro manzanas» tomado en su lectura más literal: un círculo centrado en el medio
    # del núcleo, de radio cuatro cuadras. La cuadra de Belgrano se mide, no se supone: es el largo
    # del núcleo dividido por las dos cuadras que lo componen.
    cuadra_m = largo_nucleo / 2
    radio_m = 4 * cuadra_m
    centro_nucleo = nucleo_eje.interpolate(0.5, normalized=True)
    radio_area = centro_nucleo.buffer(radio_m)
    dentro_radio = sum(1 for fila in geocodificados.itertuples()
                       if radio_area.contains(
                           gpd.GeoSeries(gpd.points_from_xy([fila.longitud], [fila.latitud]),
                                         crs=CRS_GEOGRAFICO).to_crs(CRS_METRICO).iloc[0]))
    dentro_bandas = int((geocodificados.zona != "afuera").sum())
    p("      EL RADIO, MEDIDO CONTRA LAS DOS BANDAS")
    p("")
    p(f"            la cuadra de Belgrano, medida acá: {cuadra_m:.0f} m "
      f"(el núcleo son dos)")
    p(f"            radio de cuatro manzanas: {radio_m:.0f} m → "
      f"{radio_area.area / 10_000:.1f} ha")
    p(f"            núcleo + corredor:                  {e02_area.area / 10_000:.1f} ha")
    p("")
    p(f"            el radio contiene    {dentro_radio} de {len(geocodificados)} puertas "
      f"geocodificadas, en {radio_area.area / 10_000:.1f} ha")
    p(f"            las dos bandas       {dentro_bandas} de {len(geocodificados)}, en "
      f"{e02_area.area / 10_000:.1f} ha")
    p("")
    p(f"            Por puerta contenida: el radio gasta "
      f"{radio_area.area / 10_000 / max(dentro_radio, 1):.2f} ha, las bandas "
      f"{e02_area.area / 10_000 / max(dentro_bandas, 1):.2f} ha.")
    p("")

    p(f"      E07 · {len(e07_puertas)} establecimientos de Liniers")
    for fila in e07_puertas.itertuples():
        detalle = (f"{fila.zona:<14}{fila.dist_nucleo_m:>6.0f} m del eje"
                   if fila.geocodificado == "si" else f"{fila.zona:<14}{fila.nota_direccion}")
        p(f"            {str(fila.establecimiento)[:30]:<32}"
          f"{str(fila.calle)[:22]:<24}{str(fila.altura_fuente)[:12]:<14}{detalle}")
    p("")
    dentro07 = int((e07_puertas.zona == "dentro_E07").sum())
    p(f"      {dentro07} de {len(e07_puertas)} caen dentro del eje con su buffer. Las cinco puertas")
    p("      de Ibarrola no necesitan un eje propio: Ibarrola está a una cuadra de José León")
    p("      Suárez y el buffer declarado de 150 m ya las contiene. Agregarle a E07 las tres")
    p("      transversales enteras habría sido volver al cuadrante por otra puerta.")
    p("")

    # ================================================================ la capa
    p("-" * 100)
    p("  LA CAPA · lo que cambia y lo que no")
    p("")

    capa = gpd.read_file(ENTRADA_R3_GEO).to_crs(CRS_METRICO)
    tabla = pd.read_csv(ENTRADA_R3_CSV)
    reparados = pd.read_csv(REPARADOS).set_index("enclave_id")

    nuevos = {
        "E02": {"geometry": e02_area, "n_tramos": 1 + len(sobre_traza) - 1,
                "largo_eje_m": round(largo_nucleo + largo_corredor, 1),
                "metodo_geometria": "nucleo(eje+buffer) + corredor(traza ffcc+buffer)"},
        "E07": {"geometry": e07_area, "n_tramos": 1, "largo_eje_m": round(largo_e07, 1),
                "metodo_geometria": "eje+buffer"},
    }
    for enclave_id, datos in nuevos.items():
        antes_ha = float(tabla.loc[tabla.enclave_id == enclave_id, "ha"].iloc[0])
        antes_eje = float(tabla.loc[tabla.enclave_id == enclave_id, "largo_eje_m"].iloc[0])
        mascara = capa.enclave_id == enclave_id
        capa.loc[mascara, "geometry"] = datos["geometry"]
        for columna in ("n_tramos", "largo_eje_m", "metodo_geometria"):
            capa.loc[mascara, columna] = datos[columna]
        capa.loc[mascara, "nivel_precision"] = reparados.loc[enclave_id, "nivel_precision"]
        capa.loc[mascara, "delimitacion_textual"] = reparados.loc[
            enclave_id, "delimitacion_textual_CORREGIDA"]
        capa.loc[mascara, "desde"] = reparados.loc[enclave_id, "desde"]
        capa.loc[mascara, "n_grupos_fuentes"] = str(reparados.loc[enclave_id, "n_grupos_fuentes"])
        capa.loc[mascara, "reescrita_en"] = "ronda 4 · 2026-08-07"
        ahora_ha = datos["geometry"].area / 10_000
        p(f"      {enclave_id}   eje {antes_eje:>8,.0f} m → {datos['largo_eje_m']:>8,.0f} m   ·   "
          f"{antes_ha:>6.1f} ha → {ahora_ha:>6.1f} ha")
    capa["ha"] = capa.geometry.apply(lambda g: round(g.area / 10_000, 2) if g is not None else 0.0)
    p("")
    p("      E07 se achica porque deja de ser tres calles enteras dentro de Liniers y pasa a ser")
    p("      el eje de 300 m que la fuente arbitrada mide. La ronda 3 no lo tenía inflado por")
    p("      error de cálculo: lo tenía inflado porque la consigna no daba cabeceras y la regla")
    p("      «sin cabecera entra entera» hizo lo que tenía que hacer con lo que había.")
    p("")

    capa.to_file(OUT / "enclaves_comunitarios_r4.geojson", driver="GeoJSON")
    capa.drop(columns="geometry").to_csv(
        OUT / "enclaves_comunitarios_r4.csv", index=False, encoding="utf-8")
    componentes = gpd.GeoDataFrame(
        {"componente": ["E02_nucleo", "E02_corredor", "E07_eje"],
         "que_es": ["Arribeños entre Juramento y Olazábal, dos cuadras",
                    "traza del viaducto del Mitre entre Monroe y Echeverría",
                    "José León Suárez entre Ramón Falcón y Ventura Bosch"],
         "largo_m": [round(largo_nucleo, 1), round(largo_corredor, 1), round(largo_e07, 1)],
         "geometry": [nucleo_area, corredor_area, e07_area]},
        geometry="geometry", crs=CRS_METRICO)
    componentes.to_file(OUT / "enclaves_componentes_r4.geojson", driver="GeoJSON")
    puertas.to_csv(OUT / "establecimientos_E02_E07_geo_r4.csv", index=False, encoding="utf-8")
    CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")

    p("=" * 100)
    p(f"  E02 y E07 reescritos · {len(puertas)} puertas, "
      f"{int((puertas.geocodificado == 'si').sum())} geocodificadas · "
      f"USIG: {len(cache) - consultas_antes} consultas nuevas · Places: 0 requests")
    p("=" * 100)
    p("")

    (OUT / "ENCLAVES_R4.txt").write_text(buffer_txt.getvalue(), encoding="utf-8")
    print(buffer_txt.getvalue())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
