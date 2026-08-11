# -*- coding: utf-8 -*-
"""El Café Roma cargado dos veces: cuál de las dos direcciones es, y de dónde salió la otra.

LA PREGUNTA
-----------
La capa que alimenta el bloque «Para conocer» de cada página trae **dos filas llamadas Café
Roma**, con dos direcciones —«Olavarría 409» y «San Luis 3101»— y **un solo punto**. Las dos caen
adentro del borde nuevo de La Boca, así que esa página cuenta un Bar Notable de más.

LA RESPUESTA, Y NO HACE FALTA SALIR DEL REPOSITORIO A BUSCARLA
---------------------------------------------------------------
No es «cuál de las dos direcciones del Café Roma es la buena». **Son dos establecimientos
distintos**, y el catálogo oficial los tiene a los dos por separado:

    Res. 1225/26, orden 29/90 · CAFE ROMA        · Olavarría 409 · La Boca
    Res. 1225/26, orden 86/90 · ROMA DEL ABASTO  · Anchorena 806 · Balvanera

«San Luis 3101» no es una segunda dirección del Café Roma: es **la esquina de Roma del Abasto**.
Wikidata lo carga con ese nombre y esa dirección —Q56826620, barrio Balvanera— y el punto que le
geocodifica queda a metros del que USIG le da a Anchorena 806. Esa distancia se mide acá y se
publica, porque es la prueba de que son el mismo local y no dos.

El emparejamiento por nombre fusionó las dos entradas de Wikidata bajo «Café Roma» y le puso a la
segunda **el punto de la primera**, a seis kilómetros de donde va. La corrección ya está hecha
—desde la ronda 5— en la capa canónica `hitos_capa_2026_r11.csv`. Lo que quedó sin corregir es
`hitos_capa_2026.geojson`, que es una foto anterior de la misma capa **y es la que leen las
páginas**.

LO QUE ESTE CONTROL AGREGA
--------------------------
Resolver un duplicado no sirve de nada si la fuente del duplicado sigue conectada. Así que además
de responder la pregunta se mide **cuánto más trae de atraso esa foto**: qué filas difieren, qué
establecimientos le faltan, y a qué páginas les cambia el bloque «Para conocer».

Se mide en EPSG:5347. Cero requests, ninguna fuente cerrada.
"""

import csv
import json
import sys
from datetime import date
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

SALIDA = Path(__file__).resolve().parent
BARRIDO = SALIDA.parent
sys.path.insert(0, str(SALIDA))
import geometria_vigente_20 as gv  # noqa: E402

CRS_M, CRS_G = "EPSG:5347", "EPSG:4326"
HOY = date.today().isoformat()

CAPA_QUE_LEEN_LAS_PAGINAS = BARRIDO / "hitos" / "hitos_capa_2026.geojson"
CAPA_CANONICA = BARRIDO / "hitos" / "hitos_capa_2026_r11.csv"
CATALOGO_90 = BARRIDO / "desde_cowork" / "evidencia_2026" / "catalogo_90_estado_final.csv"
WIKIDATA = BARRIDO / "dataset_bares_notables" / "bares_notables_caba.csv"
CAMBIOS_R5 = BARRIDO / "hitos" / "cambios_ronda_5.csv"


def punto(lon, lat):
    return gpd.GeoSeries([Point(lon, lat)], crs=CRS_G).to_crs(CRS_M).iloc[0]


def p(*a):
    print(*a)


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    p("=" * 98)
    p("EL CAFÉ ROMA CARGADO DOS VECES · cuál es el establecimiento y qué es la otra fila")
    p("=" * 98 + "\n")

    vieja = gpd.read_file(CAPA_QUE_LEEN_LAS_PAGINAS).to_crs(CRS_M)
    canon = pd.read_csv(CAPA_CANONICA)
    cat = pd.read_csv(CATALOGO_90)
    wiki = pd.read_csv(WIKIDATA)

    # ---------------------------------------------------------------- 1 · las dos filas
    p("-" * 98)
    p("1 · LAS DOS FILAS, COMO ESTÁN EN LA CAPA QUE LEEN LAS PÁGINAS")
    p("-" * 98)
    dos = vieja[vieja.nombre.astype(str).str.strip().str.lower() == "café roma"]
    if len(dos) != 2:
        raise SystemExit(f"se esperaban 2 filas «Café Roma» en {CAPA_QUE_LEEN_LAS_PAGINAS.name} y "
                         f"hay {len(dos)}. La capa cambió: no se sigue con un diagnóstico viejo.")
    for r in dos.itertuples():
        p(f"    {r.hito_id}  {r.nombre:<12} {str(r.direccion):<16} "
          f"barrio declarado: {str(r.barrio_declarado):<12} "
          f"punto ({r.geometry.x:,.0f}, {r.geometry.y:,.0f})")
    a, b = dos.geometry.iloc[0], dos.geometry.iloc[1]
    p(f"\n    las dos filas comparten el punto: distancia entre ellas {a.distance(b):,.1f} m")

    # ---------------------------------------------------------------- 2 · el catálogo oficial
    p("\n" + "-" * 98)
    p("2 · QUÉ DICE EL CATÁLOGO OFICIAL · Res. MCGC 1225/26, los 90 Bares Notables")
    p("-" * 98)
    ficha = cat[cat.establecimiento.astype(str).str.contains("ROMA", case=False, na=False)]
    if len(ficha) != 2:
        raise SystemExit(f"el catálogo devuelve {len(ficha)} filas con «ROMA» y se esperaban 2.")
    for r in ficha.itertuples():
        p(f"    orden {r.orden:>3}/90   {r.establecimiento:<18} {r.direccion:<16} "
          f"{r.barrio:<12} {r.estado}")
    p("\n    El catálogo los tiene por separado, con dos órdenes distintos: no son dos")
    p("    direcciones de un establecimiento, son dos establecimientos.")

    # ---------------------------------------------------------------- 3 · de dónde sale San Luis
    p("\n" + "-" * 98)
    p("3 · DE DÓNDE SALE «SAN LUIS 3101», QUE NO ES UNA DIRECCIÓN INVENTADA")
    p("-" * 98)
    wr = wiki[wiki.nombre.astype(str).str.strip().str.lower() == "café roma"]
    for r in wr.itertuples():
        p(f"    {r.wikidata_id:<12} {r.nombre:<12} {str(r.direccion_declarada):<16} "
          f"barrio {str(r.barrio):<12} ({r.lat:.6f}, {r.lon:.6f})")
    p("\n    Wikidata tiene DOS entradas llamadas «Café Roma», con dos identificadores, dos")
    p("    barrios y dos puntos. El emparejamiento por nombre las fusionó en una sola fila.")

    sl = wr[wr.direccion_declarada.astype(str).str.contains("San Luis", case=False)].iloc[0]
    ol = wr[wr.direccion_declarada.astype(str).str.contains("Olavarr", case=False)].iloc[0]
    rda = canon[canon.hito_id == "H032"].iloc[0]
    p_sl, p_ol = punto(sl.lon, sl.lat), punto(ol.lon, ol.lat)
    p_rda = punto(rda.longitud, rda.latitud)
    d_sl_rda, d_sl_ol = p_sl.distance(p_rda), p_sl.distance(p_ol)

    p(f"\n    «San Luis 3101» (punto de Wikidata) contra «{rda.direccion}» (punto USIG de")
    p(f"    {rda.nombre}, que es el orden 86/90):   {d_sl_rda:,.1f} m")
    p(f"    «San Luis 3101» contra «Olavarría 409», que es el orden 29/90:   {d_sl_ol:,.0f} m")
    p(f"\n    San Luis y Anchorena se cruzan: el 3101 de una y el 806 de la otra son la misma")
    p(f"    esquina, y por eso los dos puntos caen a {d_sl_rda:,.0f} metros. La fila de «San Luis")
    p(f"    3101» es Roma del Abasto, en Balvanera, a {d_sl_ol / 1000:,.1f} km de La Boca.")

    # ---------------------------------------------------------------- 4 · la corrección ya hecha
    p("\n" + "-" * 98)
    p("4 · LA CORRECCIÓN YA ESTÁ HECHA EN LA CAPA CANÓNICA, Y NO LLEGÓ A LA QUE LEEN LAS PÁGINAS")
    p("-" * 98)
    cam = pd.read_csv(CAMBIOS_R5)
    cam = cam[(cam.hito_id == "H032") & (cam.campo.isin(["nombre", "direccion",
                                                          "barrio_declarado"]))]
    for r in cam.itertuples():
        p(f"    {r.fecha}  H032.{r.campo:<18} «{str(r.valor_antes)[:22]:<24}» -> "
          f"«{str(r.valor_despues)[:22]}»")
    p(f"\n    canónica  ({CAPA_CANONICA.name}):  H032 = {rda.nombre}, {rda.direccion}, "
      f"{rda.barrio_declarado}")
    vieja_h032 = vieja[vieja.hito_id == "H032"].iloc[0]
    p(f"    la que leen las páginas ({CAPA_QUE_LEEN_LAS_PAGINAS.name}):  H032 = "
      f"{vieja_h032.nombre}, {vieja_h032.direccion}")

    # ---------------------------------------------------------------- 5 · qué cuenta de más
    p("\n" + "-" * 98)
    p("5 · QUÉ CUENTA DE MÁS LA PÁGINA DE LA BOCA, MEDIDO CONTRA EL BORDE NUEVO")
    p("-" * 98)
    bordes, _, soportes = gv.cargar()
    z52 = bordes["Z52"]
    con_vieja = vieja[vieja.geometry.within(z52)]
    canon_pts = canon[canon.latitud.notna()].copy()
    canon_geo = gpd.GeoDataFrame(
        canon_pts, geometry=gpd.GeoSeries(
            [Point(x, y) for x, y in zip(canon_pts.longitud, canon_pts.latitud)],
            crs=CRS_G).to_crs(CRS_M).values, crs=CRS_M)
    con_canon = canon_geo[canon_geo.geometry.within(z52)]
    p(f"    con la capa que leen las páginas : {len(con_vieja)} · "
      f"{', '.join(f'{r.nombre} ({r.direccion})' for r in con_vieja.itertuples())}")
    p(f"    con la capa canónica             : {len(con_canon)} · "
      f"{', '.join(f'{r.nombre} ({r.direccion})' for r in con_canon.itertuples())}")
    p(f"\n    La página publica «4 lugares con reconocimiento: 3 Bares Notables y 1 pizzería».")
    notables = con_canon[con_canon.tipo == "Bar Notable"]
    p(f"    Medido contra la capa canónica son {len(con_canon)}: {len(notables)} Bares Notables y "
      f"{len(con_canon) - len(notables)} pizzería emblemática.")

    # ---------------------------------------------------------------- 6 · el atraso completo
    p("\n" + "=" * 98)
    p("6 · CUÁNTO MÁS TRAE DE ATRASO ESA FOTO DE LA CAPA")
    p("=" * 98)
    p(f"    la que leen las páginas: {len(vieja)} filas · la canónica: {len(canon)} filas")
    faltan = sorted(set(canon.hito_id) - set(vieja.hito_id))
    p(f"    establecimientos que la canónica tiene y la foto no: {len(faltan)}")

    filas_atraso = []
    union41 = gv.union(bordes)
    for hid in faltan:
        r = canon[canon.hito_id == hid].iloc[0]
        dentro, cual = "sin punto", ""
        if pd.notna(r.latitud):
            pt = punto(r.longitud, r.latitud)
            dentro = "si" if union41.covers(pt) else "no"
            if dentro == "si":
                cual = next((pid for pid, g in bordes.items() if g.covers(pt)), "")
        p(f"      {hid:<9} {str(r.nombre)[:34]:<36} {str(r.tipo)[:22]:<24} "
          f"dentro de un borde: {dentro} {cual}")
        filas_atraso.append(dict(
            hito_id=hid, nombre=r.nombre, tipo=r.tipo, direccion=r.direccion,
            que_pasa="falta entero en la capa que leen las páginas",
            dentro_de_algun_borde=dentro, polo=cual))

    # filas presentes en las dos pero con nombre o dirección distinta, ignorando mayúsculas y
    # el formato del callejero: lo que interesa es un dato distinto, no otra tipografía
    def clave(x):
        return "".join(ch for ch in str(x).lower() if ch.isalnum())

    m = vieja[["hito_id", "nombre", "direccion"]].merge(
        canon[["hito_id", "nombre", "direccion", "latitud", "longitud"]],
        on="hito_id", suffixes=("_foto", "_canon"))
    distintas = m[m.apply(lambda r: clave(r.nombre_foto) != clave(r.nombre_canon)
                          or clave(r.direccion_foto) != clave(r.direccion_canon), axis=1)]
    # el formato de la dirección no es un dato distinto: se separa
    sustantivas = []
    for r in distintas.itertuples():
        num_f = "".join(ch for ch in str(r.direccion_foto) if ch.isdigit())
        num_c = "".join(ch for ch in str(r.direccion_canon) if ch.isdigit())
        if clave(r.nombre_foto) == clave(r.nombre_canon) and num_f == num_c:
            continue  # misma puerta escrita de otra manera
        sustantivas.append(r)
    p(f"\n    filas que difieren de verdad —otro nombre u otra puerta—: {len(sustantivas)} "
      f"(de {len(distintas)} que difieren en algo, el resto es formato)")
    for r in sustantivas:
        vfila = vieja[vieja.hito_id == r.hito_id].iloc[0]
        dentro, cual = "sin punto", ""
        if pd.notna(r.latitud):
            pt = punto(r.longitud, r.latitud)
            dentro = "si" if union41.covers(pt) else "no"
            if dentro == "si":
                cual = next((pid for pid, g in bordes.items() if g.covers(pt)), "")
        antes_dentro = next((pid for pid, g in bordes.items()
                             if g.covers(vfila.geometry)), "")
        p(f"      {r.hito_id:<9} foto: «{r.nombre_foto}, {r.direccion_foto}»"
          f"{'  en ' + antes_dentro if antes_dentro else '  en ningún borde'}")
        p(f"      {'':<9} canónica: «{r.nombre_canon}, {r.direccion_canon}»"
          f"{'  en ' + cual if cual else '  en ningún borde'}")
        filas_atraso.append(dict(
            hito_id=r.hito_id, nombre=r.nombre_canon, tipo="",
            direccion=r.direccion_canon,
            que_pasa=f"la foto dice «{r.nombre_foto}, {r.direccion_foto}»",
            dentro_de_algun_borde=dentro, polo=cual))

    campos = ["hito_id", "nombre", "tipo", "direccion", "que_pasa", "dentro_de_algun_borde",
              "polo"]
    with (SALIDA / "capa_reconocimiento_atrasada.csv").open("w", encoding="utf-8",
                                                            newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=campos)
        w.writeheader()
        w.writerows(filas_atraso)

    # ---------------------------------------------------------------- la resolución
    resolucion = [
        dict(fila="H031", nombre_en_la_capa="Café Roma", direccion_en_la_capa="Olavarria 409",
             veredicto="es el establecimiento",
             es="Café Roma, Bar Notable, orden 29/90 de la Res. MCGC 1225/26, La Boca",
             direccion_buena="Olavarría 409",
             evidencia=f"{CATALOGO_90.name} orden 29; Wikidata Q56826608; verificado abierto por "
                       f"la Dirección el 08/08/2026",
             que_hacer="queda como está: es la única fila de Café Roma"),
        dict(fila="H032", nombre_en_la_capa="Café Roma", direccion_en_la_capa="San Luis 3101",
             veredicto="error de carga",
             es="Roma del Abasto, Bar Notable, orden 86/90 de la Res. MCGC 1225/26, Balvanera",
             direccion_buena="Anchorena 806",
             evidencia=f"{CATALOGO_90.name} orden 86; Wikidata Q56826620 la carga como «Café "
                       f"Roma, San Luis 3101, Balvanera», que es la esquina de Anchorena 806 "
                       f"—los dos puntos distan {d_sl_rda:,.0f} m—; corregido en "
                       f"{CAPA_CANONICA.name} el 07/08/2026",
             que_hacer=f"no es una dirección del Café Roma ni hay que elegir entre las dos: es "
                       f"otro establecimiento, ya corregido en la capa canónica. Lo que falta es "
                       f"regenerar {CAPA_QUE_LEEN_LAS_PAGINAS.name} desde "
                       f"{CAPA_CANONICA.name}, que es de donde salen los bloques de las páginas"),
    ]
    with (SALIDA / "cafe_roma_resolucion.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(resolucion[0].keys()))
        w.writeheader()
        w.writerows(resolucion)

    (SALIDA / "cafe_roma_resumen.json").write_text(json.dumps(dict(
        fecha=HOY,
        direccion_del_establecimiento="Olavarría 409",
        la_otra_fila_es="Roma del Abasto, Anchorena 806, Balvanera",
        metros_entre_san_luis_3101_y_anchorena_806=round(float(d_sl_rda), 1),
        metros_entre_san_luis_3101_y_olavarria_409=round(float(d_sl_ol)),
        reconocimiento_dentro_de_la_boca_con_la_foto=len(con_vieja),
        reconocimiento_dentro_de_la_boca_con_la_canonica=len(con_canon),
        bares_notables_dentro_de_la_boca=int(len(notables)),
        filas_de_la_foto=len(vieja), filas_de_la_canonica=len(canon),
        establecimientos_que_le_faltan_a_la_foto=len(faltan),
        filas_con_otro_nombre_u_otra_puerta=len(sustantivas),
    ), ensure_ascii=False, indent=2), encoding="utf-8")

    p(f"\nEscrito: cafe_roma_resolucion.csv (2 filas) · "
      f"capa_reconocimiento_atrasada.csv ({len(filas_atraso)} filas) · cafe_roma_resumen.json")


if __name__ == "__main__":
    main()
