"""Ronda 8 · el nudo Chacagiales se fusiona, y las dos correcciones de perímetro.

QUÉ HACE
--------
    TAREA 3   R09 Chacarita + R19 Federico Lacroze pasan a UN SOLO POLO con subzonas, con
              Z43 Colegiales adentro. Morfología: sistema de subpolos
    TAREA 4a  Z23 Flores casco histórico recibe el perímetro corregido: Av. Rivadavia entre
              Carabobo/Boyacá y Av. Nazca, con ensanche en Plaza Flores
    TAREA 4c  se declara la cola de R20 — las 24,7 ha de lo publicado que la evidencia
              documental actual no alcanza

POR QUÉ LA FUSIÓN Y NO UN REPARTO
----------------------------------
La ronda 7 midió que la ampliación de R19 dejaba **R09 ∩ R19 = 60,4 ha, el 64 % de Chacarita**.
Eso no es un accidente de buffer: la decisión 6 amplió R19 hacia **Fraga, Dorrego y Charlone, que
están en Chacarita**. La ampliación hizo exactamente lo que se le pidió, y lo que quedó al
descubierto es que la decisión era internamente inconsistente con la existencia de R09 como
objeto separado.

Repartir el solape por precedencia habría escondido eso: dos polos que se pisan en dos tercios no
son dos polos. La fusión lo dice.

**Y hay una figura que la definición ya provee y que ninguna de las dos tenía.** El clustering le
puso «dispersa» a R09 y «eje» a R19 — dos morfologías que describen fragmentos, no el objeto. El
sistema de subpolos es la que corresponde, y es la misma que se usó en Z39, Z40 y Z46.

NO VIOLA LA REGLA DE QUE LAS 22 SÓLO SE AMPLÍAN
------------------------------------------------
El polo fusionado **contiene** a los dos publicados. Se verifica por superficie perdida, igual que
las cuatro ampliaciones de la ronda 7, y por el mismo motivo: `covers()` de GEOS devuelve `False`
sobre geometrías cuya diferencia mide exactamente 0,0 m².

Z44 VILLA ORTÚZAR QUEDA AFUERA, Y CONVIENE DECIR POR QUÉ
----------------------------------------------------------
Su núcleo es Plaza 25 de Agosto y sólo su extremo sur toca el corredor. La Mezzetta —su único
hito con distinción— ya está adjudicada ahí. Meterla adentro sería absorber una zona por
contigüidad de borde, que es justo lo que le pasó a R09 sin que nadie lo decidiera.

Google Places: 0 requests. Ninguna consulta de red.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/ronda_8_geometria.py
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
    puntos_base,
    sin_tildes,
)
from ronda_7_geometria_ampliaciones import (  # noqa: E402
    BUFFER_EJE_M,
    contencion,
    piezas_en_marco,
)

GEOMETRIA = BARRIDO / "geometria_r7"
GEOMETRIA_R8 = BARRIDO / "geometria_r8"
REFERENCIAS_R7 = GEOMETRIA / "referencias_r7.geojson"
OUT_GEOJSON = GEOMETRIA_R8 / "referencias_r8.geojson"
OUT_FUSION = GEOMETRIA_R8 / "fusion_chacagiales_r8.csv"
OUT_SOLAPES = GEOMETRIA_R8 / "solapes_r8.csv"
OUT_FICHA_R20 = GEOMETRIA_R8 / "cola_de_R20_declarada.csv"
INFORME = GEOMETRIA_R8 / "GEOMETRIA_R8.txt"

ESPACIOS_VERDES = (ROOT / "outputs" / "polos_gastro" / "INVESTIGACION_DESBLOQUEOS_V21" /
                   "paquete" / "r15_plaza_arenales" / "fuentes" /
                   "espacios_verdes_publicos_gcba.geojson")

FUSION_ID = "R09R19_CHACAGIALES"
FUSION_NOMBRE = "Chacagiales · Chacarita, Federico Lacroze y Colegiales"


def p_factory(buffer: io.StringIO):
    def p(*args_):
        print(*args_, file=buffer)
    return p


def tramo_entre(callejero, calle, corte_a, corte_b, marco):
    partes, _ = piezas_en_marco(callejero, calle, marco)
    if not partes:
        return None
    eje = unary_union(partes)
    puntos = []
    for corte in (corte_a, corte_b):
        otra = callejero[callejero.clave == sin_tildes(corte)]
        if otra.empty:
            return None
        union_otra = unary_union(list(otra.geometry))
        interseccion = eje.intersection(union_otra)
        puntos.append(interseccion.centroid if not interseccion.is_empty
                      else nearest_points(eje, union_otra)[0])
    a, b = puntos
    dx, dy = b.x - a.x, b.y - a.y
    largo2 = dx * dx + dy * dy
    if largo2 == 0:
        return None
    elegidos = []
    for pieza in partes:
        centro = pieza.interpolate(0.5, normalized=True)
        t = ((centro.x - a.x) * dx + (centro.y - a.y) * dy) / largo2
        perp = abs((centro.x - a.x) * dy - (centro.y - a.y) * dx) / largo2 ** 0.5
        if -0.02 <= t <= 1.02 and perp <= 200:
            elegidos.append(pieza)
    return unary_union(elegidos) if elegidos else None


def main() -> int:  # noqa: C901
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    buffer = io.StringIO()
    p = p_factory(buffer)

    GEOMETRIA_R8.mkdir(parents=True, exist_ok=True)
    referencias = gpd.read_file(REFERENCIAS_R7).to_crs(CRS_METRICO).set_index("referencia_id")
    capa_barrios = barrios()
    callejero = gpd.read_file(CALLEJERO).to_crs(CRS_METRICO)
    callejero["clave"] = callejero.nomoficial.map(sin_tildes)
    verdes = gpd.read_file(ESPACIOS_VERDES).to_crs(CRS_METRICO)
    base = puntos_base()

    def medir(g):
        return round(g.area / 10_000, 2), int(base.within(g).sum())

    p("RONDA 8 · EL NUDO CHACAGIALES Y LAS DOS CORRECCIONES")
    p("=" * 100)
    p("")
    p("  Google Places: 0 requests. Ninguna consulta de red.")
    p("")

    # ==================================================================== TAREA 3 · la fusión
    p("-" * 100)
    p("  TAREA 3 · R09 + R19 SE FUSIONAN, CON Z43 COLEGIALES ADENTRO")
    p("")
    r09 = referencias.geometry.loc["R09"]
    r19 = referencias.geometry.loc["R19"]
    colegiales = capa_barrios[capa_barrios.clave == "COLEGIALES"].geometry.iloc[0]

    ha_r09, loc_r09 = medir(r09)
    ha_r19, loc_r19 = medir(r19)
    ha_z43, loc_z43 = medir(colegiales)
    solape_previo = r09.intersection(r19).area / 10_000

    p(f"      R09 Chacarita (publicada)        {ha_r09:>8,.1f} ha · {loc_r09:>5} locales · "
      "morfología del clustering: «dispersa»")
    p(f"      R19 Lacroze (ampliada en r7)     {ha_r19:>8,.1f} ha · {loc_r19:>5} locales · "
      "morfología del clustering: «eje»")
    p(f"      Z43 Colegiales (barrio)          {ha_z43:>8,.1f} ha · {loc_z43:>5} locales")
    p("")
    p(f"      R09 ∩ R19 antes de fusionar: {solape_previo:,.1f} ha "
      f"= el {solape_previo * 10_000 / r09.area * 100:.0f} % de R09")
    p("")

    nucleo = unary_union([r09, r19])
    ha_nucleo, loc_nucleo = medir(nucleo)
    fusion = unary_union([r09, r19, colegiales])
    ha_fusion, loc_fusion = medir(fusion)

    p(f"      R09 ∪ R19, sin Colegiales:       {ha_nucleo:>8,.1f} ha · {loc_nucleo:>5} locales")
    p(f"      + Z43 Colegiales (el polo)       {ha_fusion:>8,.1f} ha · {loc_fusion:>5} locales")
    p("")
    p("      COLEGIALES ENTRA A ESCALA DE BARRIO, y eso es un techo y no una medición: Z43 no")
    p("      tiene perímetro delimitado —su delimitación textual es «Polo Concepción + corredor")
    p("      Elcano/Jorge Newbery + entorno del Mercado de Pulgas»— y hasta que se construya, el")
    p("      barrio es lo más chico que se puede usar sin inventar. La diferencia entre las dos")
    p(f"      líneas de arriba, {ha_fusion - ha_nucleo:,.1f} ha y "
      f"{loc_fusion - loc_nucleo} locales, es lo que está en juego.")
    p("")

    filas_fusion = []
    for rid, geom, nombre in (("R09", r09, "Chacarita"),
                              ("R19", r19, "Federico Lacroze (ampliada en la ronda 7)")):
        conserva, perdida, predicado = contencion(fusion, geom)
        ha, loc = medir(geom)
        p(f"      CONTENCIÓN de {rid}: superficie que queda afuera del polo fusionado "
          f"{perdida:,.6f} m² → {'CONSERVA TODO' if conserva else 'PIERDE SUPERFICIE'}")
        if not predicado:
            p("          (covers() de GEOS dice NO sobre una diferencia de 0,0 m²: manda la "
              "superposición)")
        filas_fusion.append({
            "subzona_id": rid, "nombre": nombre, "clase": "referencia publicada",
            "ha": ha, "locales": loc,
            "conserva_todo_lo_publicado": bool(conserva),
            "superficie_perdida_m2": round(perdida, 6),
            "predicado_covers_geos": bool(predicado)})
    filas_fusion.append({
        "subzona_id": "Z43", "nombre": "Colegiales", "clase": "zona nueva, a escala de barrio",
        "ha": ha_z43, "locales": loc_z43, "conserva_todo_lo_publicado": True,
        "superficie_perdida_m2": 0.0, "predicado_covers_geos": True})
    p("")
    p(f"      EL POLO FUSIONADO · {FUSION_ID}")
    p(f"      {FUSION_NOMBRE}")
    p(f"      morfología: SISTEMA DE SUBPOLOS · {ha_fusion:,.1f} ha · {loc_fusion} locales · "
      f"{loc_fusion / ha_fusion:.2f} locales/ha")
    p(f"      subzonas: R09 Chacarita · R19 Federico Lacroze · Z43 Colegiales")
    p("")
    p("      Z44 VILLA ORTÚZAR QUEDA AFUERA. Medido, para que la exclusión no sea una opinión:")
    ortuzar = capa_barrios[capa_barrios.clave == "VILLA ORTUZAR"].geometry.iloc[0]
    solape_ortuzar = ortuzar.intersection(fusion).area / ortuzar.area * 100
    p(f"      el {solape_ortuzar:.1f} % de Villa Ortúzar cae dentro del polo fusionado. Es")
    p("      contigüidad de borde, no pertenencia: su núcleo es Plaza 25 de Agosto y La Mezzetta")
    p("      ya está adjudicada ahí.")
    p("")

    # ==================================================================== TAREA 4a · Z23
    p("-" * 100)
    p("  TAREA 4a · Z23 FLORES CASCO HISTÓRICO · EL PERÍMETRO CORREGIDO")
    p("")
    p("  La ronda 7 midió que «Av. Rivadavia entre Boyacá y Carabobo» mide cero cuadras: son la")
    p("  misma avenida, que cambia de nombre al cruzar Rivadavia. La corrección de Diego cambia")
    p("  el corte de destino: de Carabobo/Boyacá a Av. NAZCA.")
    p("")
    marco_flores = capa_barrios[capa_barrios.clave == "FLORES"].geometry.iloc[0]
    eje_z23 = tramo_entre(callejero, "RIVADAVIA AV.", "CARABOBO AV.", "NAZCA AV.", marco_flores)
    if eje_z23 is None:
        raise SystemExit("Z23: no se pudo resolver Av. Rivadavia entre Carabobo/Boyacá y Nazca")
    # «Plaza Flores» es el nombre de uso; en la capa oficial de espacios verdes se llama PLAZA
    # PUEYRREDÓN. Buscarla por «Flores» no devuelve nada y el ensanche se perdía en silencio.
    # La equivalencia no se da por sabida: se verifica contra el eje antes de usarla.
    plaza = verdes[(verdes.barrio == "Flores")
                   & (verdes.nombre.map(sin_tildes) == "PLAZA PUEYRREDON")]
    ensanche = None
    if not plaza.empty:
        candidata = unary_union(list(plaza.geometry))
        distancia = candidata.distance(eje_z23)
        p(f"      «Plaza Flores» en la capa oficial = PLAZA PUEYRREDÓN (Flores), "
          f"{candidata.area / 10_000:.2f} ha, a {distancia:,.0f} m del eje de Av. Rivadavia.")
        if distancia <= 200:
            ensanche = candidata
            p("      La equivalencia se verifica por posición: da sobre el eje, así que es la")
            p("      plaza que la delimitación llama Plaza Flores. Entra como ensanche.")
        else:
            p("      Queda demasiado lejos del eje: NO se usa, para no adjudicar por nombre.")
    if ensanche is None:
        p("      ensanche en Plaza Flores: no se pudo resolver contra la capa oficial. Se declara")
        p("      y el perímetro queda sin ensanche, sin inventar el polígono.")
    piezas_z23 = [eje_z23.buffer(BUFFER_EJE_M)] + ([ensanche] if ensanche is not None else [])
    z23 = unary_union(piezas_z23)
    ha_z23, loc_z23 = medir(z23)
    p(f"      eje Av. Rivadavia entre Carabobo/Boyacá y Av. Nazca: {eje_z23.length:,.0f} m")
    p(f"      perímetro corregido: {ha_z23:,.1f} ha · {loc_z23} locales")
    p("")
    p("      EL VEREDICTO NO CAMBIA: Z23 sigue PENDIENTE. Ahora tiene perímetro construible, que")
    p("      es lo que le faltaba para poligonizar, pero los dos motivos de fondo siguen en pie —")
    p("      su único hito vivo cae ocho cuadras afuera y la densidad del eje es textil.")
    la_farmacia_dist = None
    try:
        capa_hitos = pd.read_csv(BARRIDO / "hitos" / "hitos_capa_2026_r8.csv")
        farmacia = capa_hitos[capa_hitos.nombre.astype(str).str.contains("FARMACIA", case=False,
                                                                        na=False)]
        if len(farmacia) and pd.notna(farmacia.iloc[0].latitud):
            punto = gpd.GeoSeries(gpd.points_from_xy([farmacia.iloc[0].longitud],
                                                     [farmacia.iloc[0].latitud]),
                                  crs="EPSG:4326").to_crs(CRS_METRICO).iloc[0]
            la_farmacia_dist = punto.distance(z23)
            adentro = punto.within(z23)
            p(f"      medido: La Farmacia queda a {la_farmacia_dist:,.0f} m del perímetro "
              f"corregido (dentro: {'sí' if adentro else 'no'}).")
    except Exception as exc:  # noqa: BLE001
        p(f"      (no se pudo medir La Farmacia: {exc})")
    p("")

    # ==================================================================== TAREA 4c · cola de R20
    p("-" * 100)
    p("  TAREA 4c · LA COLA DE R20, DECLARADA")
    p("")
    r20 = referencias.geometry.loc["R20"]
    marco_saavedra = capa_barrios[capa_barrios.clave == "SAAVEDRA"].geometry.iloc[0]
    tramo = tramo_entre(callejero, "GARCIA DEL RIO", "CABILDO AV.", "BALBIN, RICARDO, DR. AV.",
                        marco_saavedra)
    cola = r20.difference(tramo.buffer(BUFFER_EJE_M))
    ha_cola, loc_cola = medir(cola)
    ha_r20, loc_r20 = medir(r20)
    p(f"      R20 completa (lo que se publica):        {ha_r20:>7,.1f} ha · {loc_r20:>4} locales")
    p(f"      la cola, fuera del tramo Cabildo-Balbín: {ha_cola:>7,.1f} ha · {loc_cola:>4} locales")
    p(f"      = el {ha_cola / ha_r20 * 100:.0f} % de la superficie y el "
      f"{loc_cola / loc_r20 * 100:.0f} % de los locales")
    p("")
    p("      SE CONSERVA por la regla de contención, y se DECLARA EN LA FICHA como superficie de")
    p("      la versión anterior que la evidencia documental actual no alcanza. No es lo mismo")
    p("      que territorio respaldado: son dos cosas dentro del mismo polígono y la ficha tiene")
    p("      que poder distinguirlas.")
    p("")
    pd.DataFrame([{
        "referencia_id": "R20", "nombre": "Garcia del Rio",
        "ha_publicada": ha_r20, "locales_publicados": loc_r20,
        "ha_con_respaldo_documental": round(ha_r20 - ha_cola, 2),
        "locales_con_respaldo_documental": loc_r20 - loc_cola,
        "ha_de_la_cola": ha_cola, "locales_de_la_cola": loc_cola,
        "pct_superficie_sin_respaldo": round(ha_cola / ha_r20 * 100, 1),
        "texto_para_la_ficha":
            f"De las {ha_r20:,.1f} ha del polígono, {ha_cola:,.1f} ha "
            f"({ha_cola / ha_r20 * 100:.0f} %) provienen de la delimitación anterior y quedan "
            "fuera del tramo Av. Cabildo–Av. Balbín, que es el que la evidencia documental "
            "vigente describe. Se conservan porque las referencias publicadas sólo se amplían, "
            "y se consignan como tales.",
    }]).to_csv(OUT_FICHA_R20, index=False, encoding="utf-8")

    # ==================================================================== la capa y los solapes
    p("-" * 100)
    p("  LA CAPA DE REFERENCIAS DE LA RONDA 8")
    p("")
    salida = []
    for rid, fila in referencias.iterrows():
        if rid in ("R09", "R19"):
            continue
        salida.append({"referencia_id": rid, "nombre": fila.nombre, "familia": fila.familia,
                       "estado_r8": "sin cambios",
                       "ha": round(fila.geometry.area / 10_000, 2),
                       "locales": int(base.within(fila.geometry).sum()),
                       "geometry": fila.geometry})
    salida.append({"referencia_id": FUSION_ID, "nombre": FUSION_NOMBRE,
                   "familia": "sistema de subpolos",
                   "estado_r8": "FUSIÓN de R09 + R19 + Z43",
                   "ha": ha_fusion, "locales": loc_fusion, "geometry": fusion})
    salida.append({"referencia_id": "Z23_PERIMETRO", "nombre": "Flores · casco histórico",
                   "familia": "corredor", "estado_r8": "perímetro corregido (decisión de la r8)",
                   "ha": ha_z23, "locales": loc_z23, "geometry": z23})
    capa = gpd.GeoDataFrame(salida, geometry="geometry", crs=CRS_METRICO)

    p(f"  referencias r7: {len(referencias)} · r8: {len(capa)} "
      f"(R09 y R19 salen; entra el polo fusionado y el perímetro de Z23)")
    p("")
    for fila in capa.itertuples():
        marca = "←" if fila.estado_r8 != "sin cambios" else " "
        p(f"   {marca} {fila.referencia_id:<28} {fila.nombre[:38]:<40} {fila.ha:>8,.1f} ha · "
          f"{fila.locales:>5} locales")
    p("")

    p("  QUÉ PASA CON LOS SEIS SOLAPES QUE LA RONDA 7 DEJÓ ABIERTOS")
    p("")
    solapes_r7 = pd.read_csv(GEOMETRIA / "solapes_r7.csv")
    filas_solape = []
    vistos: set[tuple[str, str]] = set()
    geoms = capa.set_index("referencia_id").geometry
    for _, viejo in solapes_r7.iterrows():
        a, b = viejo["a"], viejo["b"]
        a_new = FUSION_ID if a in ("R09", "R19") else a
        b_new = FUSION_ID if b in ("R09", "R19") else b
        if a_new == b_new:
            p(f"      {a} ∩ {b}: {viejo['ha_despues']:>7,.2f} ha → DESAPARECE. Los dos son ahora "
              "el mismo objeto.")
            filas_solape.append({"a": a, "b": b, "ha_r7": viejo["ha_despues"], "ha_r8": 0.0,
                                 "resolucion": "fusionados en un solo polo"})
            continue
        # R09∩R21 y R19∩R21 colapsan en la MISMA pareja después de fusionar. Contarlas dos veces
        # inflaría el número de solapes abiertos con una duplicación de la propia fusión.
        pareja = tuple(sorted((a_new, b_new)))
        nuevo = geoms.loc[a_new].intersection(geoms.loc[b_new]).area / 10_000
        if pareja in vistos:
            p(f"      {a} ∩ {b}: {viejo['ha_despues']:>7,.2f} ha → colapsa en "
              f"{pareja[0]} ∩ {pareja[1]}, ya contada")
            continue
        vistos.add(pareja)
        p(f"      {a} ∩ {b}: {viejo['ha_despues']:>7,.2f} ha → {a_new} ∩ {b_new} = "
          f"{nuevo:>7,.2f} ha")
        filas_solape.append({"a": a_new, "b": b_new, "ha_r7": viejo["ha_despues"],
                             "ha_r8": round(nuevo, 2),
                             "resolucion": "sigue abierto" if nuevo > 0.01 else "sin solape"})
    p("")
    abiertos = [f for f in filas_solape if f["resolucion"] == "sigue abierto"]
    p(f"  quedan {len(abiertos)} solapes abiertos, el mayor de "
      f"{max((f['ha_r8'] for f in abiertos), default=0):,.1f} ha. La fusión resuelve el más")
    p("  grande —el que valía dos tercios de Chacarita— y no toca los demás: la precedencia")
    p("  sigue siendo editorial.")
    p("")

    GEOMETRIA_R8.mkdir(parents=True, exist_ok=True)
    capa.to_crs("EPSG:4326").to_file(OUT_GEOJSON, driver="GeoJSON")
    pd.DataFrame(filas_fusion).to_csv(OUT_FUSION, index=False, encoding="utf-8")
    pd.DataFrame(filas_solape).to_csv(OUT_SOLAPES, index=False, encoding="utf-8")

    p("-" * 100)
    p(f"  {OUT_GEOJSON.name} · {len(capa)} geometrías")
    p(f"  {OUT_FUSION.name} · las tres subzonas con su verificación de contención")
    p(f"  {OUT_SOLAPES.name} · {len(filas_solape)} parejas")
    p(f"  {OUT_FICHA_R20.name} · la cola de R20, con el texto para la ficha")

    texto = buffer.getvalue()
    INFORME.write_text(texto, encoding="utf-8")
    print(texto)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
