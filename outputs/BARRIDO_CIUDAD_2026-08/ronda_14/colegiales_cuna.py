# -*- coding: utf-8 -*-
"""El perimetro de Colegiales trazado sobre la cuña real, no sobre la lista de calles.

DE DONDE SALE
-------------
`COLEGIALES_NO_ES_UNA_COSA.md` propone que Chacagiales incorpore la franja Z43-A —"Zabala ·
Delgado · Virrey Aviles · Conde, entre Av. Alvarez Thomas y Av. Forest / Av. Elcano"— en vez del
barrio entero, que hoy aporta 229,08 ha y 441 locales a escala administrativa.

La ronda 9 ya hizo las tres verificaciones que ese documento pedia ANTES de trazar, y devolvio algo
que cambia el objeto:

    Av. Alvarez Thomas y Av. Forest SE ENCUENTRAN: distancia 0 m.

No son dos avenidas paralelas con una banda entre medio: **confluyen**, y lo que encierran es una
CUÑA que se cierra. De las cuatro calles de la lista, **solo dos tienen tramo verificable entre las
dos avenidas** —Zabala 254 m y Virrey Aviles 344 m—; Delgado y Conde ni siquiera llegan a Av.
Alvarez Thomas (a 55 m y a 178 m). **Son tres cuadras, no diez.**

Esta corrida traza sobre eso. Y al trazarlo aparecen dos cosas que la lista de calles escondia:

  1. **No hay una cuña: hay dos.** Las dos avenidas no se juntan y terminan, se CRUZAN, y dejan
     cuatro sectores. Zabala cierra el sector del sudeste y Virrey Aviles el del noroeste: las dos
     caras se tocan en el apice y en ningun otro punto. La "franja" no es una banda continua.
  2. **Ninguna de las dos esta en Colegiales.** Una da 100 % Chacarita y la otra 100 % Villa
     Ortuzar. No es un error de la medicion: Av. Alvarez Thomas y Av. Forest **son** el limite del
     barrio, asi que lo que queda entre las dos esta por definicion del otro lado.

Por eso se miden las dos lecturas posibles y se reportan las dos:

  lectura A · "entre Av. Alvarez Thomas y Av. Forest", al pie de la letra -> las dos caras
  lectura B · "las calles del lado de Colegiales", que es lo que dice la fuente -> la banda de
              Zabala, Delgado, Virrey Aviles y Conde dentro del barrio, al buffer declarado

La lectura B tiene el problema opuesto y hay que decirlo: **la fuente no nombra el borde de
adentro**, asi que la profundidad de la banda la pone el buffer y no la evidencia.

COMO SE TRAZA · Y POR QUE NO CON UN BUFFER
-------------------------------------------
Un buffer de 150 m sobre los dos tramos daria una banda que se derrama sobre las dos avenidas y
hacia Chacarita: describiria cualquier cosa menos una cuña. Aca el poligono se arma **por
poligonizacion del callejero**: se toman los tres bordes —las dos avenidas y la calle que hace de
corte— y se deja que la red de calles cierre la cara. El perimetro resultante corre sobre calles
por construccion, que es justamente lo que el residuo de Palermo no podia hacer.

EL EMPALME EN T, DECLARADO
---------------------------
Virrey Aviles no cruza Av. Alvarez Thomas: **empalma en T y queda a 16 m**, dentro de la tolerancia
de 40 m que uso la ronda 9. Una cara no cierra con un hueco de 16 m, asi que el eje se extiende en
linea recta hasta el empalme y **el metro que se agrega queda escrito en la salida**. Si el hueco
fuera mayor que la tolerancia no se cerraria nada: se declararia sin tramo, como Delgado y Conde.

Cero requests. Se ejecuta con .venv/Scripts/python.exe.
"""

import csv
import sys
from pathlib import Path

import geopandas as gpd
from shapely.geometry import LineString, Point
from shapely.ops import nearest_points, polygonize, unary_union

BASE = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[3]
SALIDA = Path(__file__).resolve().parent
CRS_METRICO = "EPSG:5347"

REFERENCIAS_R7 = BASE / "geometria_r7" / "referencias_r7.geojson"
REFERENCIAS_R8 = BASE / "geometria_r8" / "referencias_r8.geojson"

# La tolerancia de empalme de la ronda 9. No se toca: si se agrandara, Delgado (55 m) y Conde
# (178 m) entrarian de contrabando y la cuña volveria a tener diez cuadras.
TOLERANCIA_EMPALME_M = 40.0
SOBREPASO_M = 1.0
# El buffer declarado del proyecto, una cuadra a cada lado. Solo lo usa la lectura B: la cuña no
# lleva buffer porque su perimetro son calles.
BUFFER_BANDA_M = 150.0

BORDES = ["ALVAREZ THOMAS AV.", "FOREST AV."]
CORTES = ["ZABALA", "AVILES, VIRREY"]
# Las dos que la fuente nombra y la ronda 9 dejo sin tramo. Se vuelven a medir para que el negativo
# viaje con el poligono y no haya que ir a buscarlo a otra ronda.
SIN_TRAMO = ["DELGADO", "CONDE"]


def limpia(g):
    return g if g.is_valid else g.buffer(0)


def cerrar_hasta(linea, otra, tolerancia=TOLERANCIA_EMPALME_M):
    """Estira la linea hasta `otra` si el hueco entra en la tolerancia. Devuelve (linea, metros).

    **El sobrepaso de 1 m no es un detalle de implementacion.** `nearest_points` devuelve un punto
    calculado en punto flotante, y el conector que termina "sobre" la avenida queda a 1,8e-10 m de
    ella. El noding de `unary_union` es exacto: con ese hueco no crea nodo, `polygonize` no cierra
    ninguna cara y la corrida devuelve cero caras sin tirar ningun error — que es exactamente la
    familia de fallas silenciosas que este proyecto ya tiene contada cuatro veces. Se sobrepasa
    1 m para que el conector CRUCE en vez de tocar.
    """
    hueco = linea.distance(otra)
    if hueco == 0:
        return linea, 0.0
    if hueco > tolerancia:
        return None, hueco
    a, b = nearest_points(linea, otra)
    dx, dy = b.x - a.x, b.y - a.y
    largo = (dx * dx + dy * dy) ** 0.5
    mas_alla = Point(b.x + dx / largo * SOBREPASO_M, b.y + dy / largo * SOBREPASO_M)
    return unary_union([linea, LineString([a, mas_alla])]), hueco


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.path.insert(0, str(ROOT / "scripts" / "barrido_ciudad"))
    from polos_soporte import puntos_base, barrios, sin_tildes  # noqa: E402
    from callejero_canonico import cargar, eje_canonico, familias  # noqa: E402

    puntos = puntos_base()
    calles = cargar()
    mapa = familias(calles)
    capa_barrios = barrios().set_index("clave")
    colegiales = limpia(capa_barrios.geometry.loc[sin_tildes("Colegiales")])

    print("=" * 88)
    print("COLEGIALES · el perimetro sobre la cuña real")
    print("=" * 88)

    ejes = {n: eje_canonico(calles, n, mapa) for n in BORDES + CORTES + SIN_TRAMO}
    faltan = [n for n, g in ejes.items() if g is None]
    if faltan:
        raise SystemExit(f"no estan en el callejero: {faltan}")

    a_thomas, forest = ejes[BORDES[0]], ejes[BORDES[1]]
    d = a_thomas.distance(forest)
    apice = nearest_points(a_thomas, forest)[0]
    print(f"\nAv. Alvarez Thomas y Av. Forest: distancia {d:,.1f} m  ->  "
          f"{'SE ENCUENTRAN' if d < 1 else 'no se tocan'}")
    print(f"  el apice de la cuña esta en {apice.x:,.0f} / {apice.y:,.0f} (EPSG:5347)")

    print("\nCada calle de la lista contra las dos avenidas:\n")
    print(f"{'calle':<20}{'a Alvarez Thomas':>18}{'a Forest':>11}{'tramo entre las dos':>22}")
    filas, cortes_utiles = [], {}
    for nombre in CORTES + SIN_TRAMO:
        eje = ejes[nombre]
        d_t, d_f = eje.distance(a_thomas), eje.distance(forest)
        cerrado_t, hueco_t = cerrar_hasta(eje, a_thomas)
        cerrado_f, hueco_f = (cerrar_hasta(cerrado_t, forest) if cerrado_t is not None
                              else (None, d_f))
        if cerrado_f is None:
            tramo_m, veredicto = 0.0, "SIN TRAMO"
        else:
            # el tramo es lo que del eje corre entre las dos avenidas: se mide sobre la cara
            tramo_m, veredicto = None, "tramo"
            cortes_utiles[nombre] = (cerrado_f, hueco_t, hueco_f)
        print(f"{nombre:<20}{d_t:>16,.0f} m{d_f:>9,.0f} m"
              f"{(veredicto if veredicto == 'SIN TRAMO' else 'cierra la cara'):>22}")
        filas.append(dict(objeto=nombre, tipo="calle de la lista",
                          distancia_a_alvarez_thomas_m=round(d_t),
                          distancia_a_forest_m=round(d_f), ha="", locales="",
                          nota=("no llega a una de las dos avenidas dentro de la tolerancia de "
                                f"{TOLERANCIA_EMPALME_M:.0f} m: no puede ser lado de la cuña"
                                if veredicto == "SIN TRAMO"
                                else f"cierra la cara; empalmes agregados: "
                                     f"{hueco_t:.0f} m a Alvarez Thomas y {hueco_f:.0f} m a Forest")))

    # ---- la cara, por poligonizacion --------------------------------------------------------
    print("\nLa cuña, poligonizada sobre el callejero:\n")
    print(f"{'corte':<22}{'ha':>9}{'locales':>9}{'perimetro':>12}{'ancho':>10}")
    caras = {}
    for nombre, (cortada, hueco_t, hueco_f) in cortes_utiles.items():
        red = unary_union([a_thomas, forest, cortada])
        candidatas = [limpia(p) for p in polygonize(red)]
        # La cuña es la cara que toca el apice: las otras caras que la red pueda cerrar quedan
        # del otro lado de alguna de las dos avenidas.
        pegadas = [p for p in candidatas if p.distance(apice) < 1.0]
        if not pegadas:
            print(f"{nombre:<22}{'la red no cierra ninguna cara pegada al apice':>48}")
            continue
        cara = min(pegadas, key=lambda p: p.area)
        ancho = cortada.intersection(cara.buffer(1)).length
        loc = int(puntos.within(cara).sum())
        caras[nombre] = cara
        reparto = ", ".join(
            f"{b} {g.intersection(cara).area / cara.area * 100:.0f} %"
            for b, g in zip(capa_barrios.nombre, capa_barrios.geometry)
            if g.intersects(cara) and g.intersection(cara).area / cara.area > 0.01)
        print(f"{nombre:<22}{cara.area / 10_000:>9,.2f}{loc:>9}"
              f"{cara.length:>10,.0f} m{ancho:>8,.0f} m   {reparto}")
        filas.append(dict(objeto=f"cuña cerrada por {nombre}", tipo="poligono",
                          distancia_a_alvarez_thomas_m="", distancia_a_forest_m="",
                          ha=round(cara.area / 10_000, 2), locales=loc,
                          nota=f"perimetro {cara.length:,.0f} m, todo sobre calles por "
                               f"construccion; el corte mide {ancho:,.0f} m; "
                               f"{cara.intersection(colegiales).area / cara.area * 100:.0f} % "
                               f"del poligono cae en el barrio de Colegiales"))

    if len(caras) != 2:
        raise SystemExit("faltan caras: no hay que trazar sobre una cuña a medio medir")
    # Las dos caras estan en SECTORES OPUESTOS del cruce: se tocan en el apice y nada mas. La
    # "franja" no es una banda: es un moño.
    a, b = caras["ZABALA"], caras["AVILES, VIRREY"]
    comun = limpia(a.intersection(b))
    print(f"\nLas dos caras entre si: superficie comun {comun.area:,.2f} m2 · "
          f"distancia {a.distance(b):,.2f} m -> "
          f"{'se tocan solo en el apice' if comun.area < 1 and a.distance(b) < 1 else 'se solapan'}")
    cuna = limpia(unary_union([a, b]))
    print(f"La franja completa (las dos caras): {cuna.area / 10_000:,.2f} ha · "
          f"{int(puntos.within(cuna).sum())} locales")
    filas.append(dict(objeto="la franja completa (las dos caras)", tipo="poligono",
                      distancia_a_alvarez_thomas_m="", distancia_a_forest_m="",
                      ha=round(cuna.area / 10_000, 2), locales=int(puntos.within(cuna).sum()),
                      nota="las dos caras estan en sectores opuestos del cruce de las dos "
                           "avenidas: se tocan en el apice y no forman una banda continua"))

    # ---- la otra lectura: la banda DEL LADO de Colegiales --------------------------------
    #
    # Las dos caras dan 100 % Chacarita y 100 % Villa Ortuzar: ni un metro cuadrado en Colegiales.
    # No es un error de la medicion, es lo que significa la frase. Av. Alvarez Thomas y Av. Forest
    # SON el limite del barrio, asi que lo que queda "entre" las dos esta, por definicion, del otro
    # lado. La fuente no dice "entre las dos avenidas": dice que el limite lo trazan esas avenidas
    # y nombra a Zabala, Delgado, Virrey Aviles y Conde **del lado de Colegiales**. Esa es la otra
    # lectura y hay que medirla tambien, porque es la que la evidencia sostiene.
    print("\nLa otra lectura: la banda del lado de Colegiales (buffer declarado de 150 m):\n")
    print(f"{'calle':<20}{'m en Colegiales':>17}{'ha':>9}{'locales':>9}")
    tramos_colegiales = []
    for nombre in CORTES + SIN_TRAMO:
        dentro = limpia(ejes[nombre]).intersection(colegiales)
        if dentro.is_empty or dentro.length < 1:
            print(f"{nombre:<20}{0:>17}")
            continue
        area = dentro.buffer(BUFFER_BANDA_M).intersection(colegiales)
        tramos_colegiales.append(dentro)
        print(f"{nombre:<20}{dentro.length:>17,.0f}{area.area / 10_000:>9,.2f}"
              f"{int(puntos.within(area).sum()):>9}")
        filas.append(dict(objeto=f"{nombre} dentro de Colegiales", tipo="lectura B",
                          distancia_a_alvarez_thomas_m=round(dentro.distance(a_thomas)),
                          distancia_a_forest_m=round(dentro.distance(forest)),
                          ha=round(area.area / 10_000, 2), locales=int(puntos.within(area).sum()),
                          nota=f"{dentro.length:,.0f} m de eje dentro del barrio, "
                               f"buffer {BUFFER_BANDA_M:.0f} m recortado al barrio"))
    banda = limpia(unary_union([t.buffer(BUFFER_BANDA_M) for t in tramos_colegiales])
                   .intersection(colegiales)) if tramos_colegiales else None
    if banda is not None:
        print(f"\n  la banda de las cuatro calles: {banda.area / 10_000:,.2f} ha · "
              f"{int(puntos.within(banda).sum())} locales · "
              f"{banda.area / colegiales.area * 100:.0f} % del barrio "
              f"(el barrio entero aporta 229,08 ha y 441 locales a Chacagiales)")
        filas.append(dict(objeto="lectura B · la banda de las cuatro calles en Colegiales",
                          tipo="poligono", distancia_a_alvarez_thomas_m="",
                          distancia_a_forest_m="", ha=round(banda.area / 10_000, 2),
                          locales=int(puntos.within(banda).sum()),
                          nota=f"{banda.area / colegiales.area * 100:.0f} % del barrio; "
                               f"la fuente no nombra el borde de adentro, asi que la profundidad "
                               f"de la banda la pone el buffer y no la evidencia"))

    # ---- que le hace a Chacagiales -----------------------------------------------------------
    r7 = gpd.read_file(REFERENCIAS_R7).to_crs(CRS_METRICO).set_index("referencia_id")
    r8 = gpd.read_file(REFERENCIAS_R8).to_crs(CRS_METRICO).set_index("referencia_id")
    chacagiales = limpia(r8.geometry.loc["R09R19_CHACAGIALES"])
    r09 = limpia(r7.geometry.loc["R09"])
    r19 = limpia(r7.geometry.loc["R19"])

    print("\nQue le hace a Chacagiales:\n")
    corregido = limpia(unary_union([r09, r19, cuna]))
    for etiqueta, g in [("Chacagiales publicado (R09 + R19 + Z43 a escala de barrio)", chacagiales),
                        ("R09 Chacarita", r09),
                        ("R19 Federico Lacroze (ampliada, ronda 7)", r19),
                        ("la cuña de Colegiales", cuna),
                        ("Chacagiales con la cuña en lugar del barrio", corregido)]:
        print(f"  {etiqueta:<58}{g.area / 10_000:>9,.2f} ha{int(puntos.within(g).sum()):>7} loc")
        filas.append(dict(objeto=etiqueta, tipo="comparacion", distancia_a_alvarez_thomas_m="",
                          distancia_a_forest_m="", ha=round(g.area / 10_000, 2),
                          locales=int(puntos.within(g).sum()), nota=""))
    print(f"\n  delta: {corregido.area / 10_000 - chacagiales.area / 10_000:+,.2f} ha · "
          f"{int(puntos.within(corregido).sum()) - int(puntos.within(chacagiales).sum()):+d} locales")
    print(f"  la cuña esta dentro de Chacagiales publicado: "
          f"{cuna.intersection(chacagiales).area / cuna.area * 100:.0f} % de su superficie")

    # ---- el Mercado de Pulgas, que la propuesta suma aparte -----------------------------------
    # ---- el Mercado de Pulgas, que la propuesta suma aparte ------------------------------
    #
    # La propuesta lo ubica de dos maneras distintas en el mismo renglon: "Gral. E. Martinez 50" y
    # "el entorno del Mercado de Pulgas en Dorrego y Alvarez Thomas". Se resuelven las dos por
    # separado —la altura contra el rango del callejero, la esquina por interseccion— porque si no
    # coinciden hay que decirlo antes de sumarle el entorno a ningun poligono.
    print("\nEl Mercado de Pulgas, que la propuesta suma aparte del eje:\n")
    dorrego = eje_canonico(calles, "DORREGO AV.", mapa)
    cuadras = calles[calles.raiz == "MARTINEZ ENRIQUE GRAL"]
    anclajes = {}
    if len(cuadras):
        con_altura = cuadras[((cuadras.alt_derini <= 50) & (cuadras.alt_derfin >= 50)) |
                             ((cuadras.alt_izqini <= 50) & (cuadras.alt_izqfin >= 50))]
        if len(con_altura):
            anclajes["Gral. E. Martinez 50 (cuadra del callejero)"] = limpia(
                unary_union(list(con_altura.geometry))).centroid
    if dorrego is not None:
        cruce = dorrego.intersection(a_thomas)
        if not cruce.is_empty:
            anclajes["Dorrego x Alvarez Thomas (esquina)"] = (
                cruce if cruce.geom_type == "Point" else cruce.centroid)
        else:
            print(f"  Av. Dorrego no cruza Av. Alvarez Thomas: quedan a "
                  f"{dorrego.distance(a_thomas):,.0f} m")
    for etiqueta, punto in anclajes.items():
        print(f"  {etiqueta:<46} a {cuna.distance(punto):>6,.0f} m de la franja · "
              f"{'dentro' if chacagiales.contains(punto) else 'fuera'} de Chacagiales publicado")
        filas.append(dict(objeto=etiqueta, tipo="anclaje del Mercado de Pulgas",
                          distancia_a_alvarez_thomas_m=round(punto.distance(a_thomas)),
                          distancia_a_forest_m=round(punto.distance(forest)), ha="", locales="",
                          nota=f"a {cuna.distance(punto):,.0f} m de la franja medida; "
                               f"{'dentro' if chacagiales.contains(punto) else 'fuera'} de "
                               f"Chacagiales publicado"))
    if len(anclajes) == 2:
        p1, p2 = list(anclajes.values())
        print(f"  los dos anclajes de la propuesta estan a {p1.distance(p2):,.0f} m entre si")
        filas.append(dict(objeto="distancia entre los dos anclajes de la propuesta",
                          tipo="control", distancia_a_alvarez_thomas_m="",
                          distancia_a_forest_m="", ha="", locales="",
                          nota=f"{p1.distance(p2):,.0f} m: la propuesta ubica el mismo hito en dos "
                               f"lugares distintos del mismo renglon"))

    destino = SALIDA / "colegiales_cuna.csv"
    with destino.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["objeto", "tipo", "distancia_a_alvarez_thomas_m",
                                           "distancia_a_forest_m", "ha", "locales", "nota"])
        w.writeheader()
        w.writerows(filas)
    piezas_salida = [(f"cuña cerrada por {n}", "A", g) for n, g in caras.items()]
    if banda is not None:
        piezas_salida.append(("banda de las cuatro calles dentro de Colegiales", "B", banda))
    capa = gpd.GeoDataFrame(
        {"pieza": [n for n, _, _ in piezas_salida],
         "lectura": [le for _, le, _ in piezas_salida],
         "ha": [round(g.area / 10_000, 2) for _, _, g in piezas_salida]},
        geometry=[g for _, _, g in piezas_salida], crs=CRS_METRICO)
    capa.to_file(SALIDA / "colegiales_cuna.geojson", driver="GeoJSON")
    print(f"\nEscrito: {destino.name} ({len(filas)} filas) y colegiales_cuna.geojson "
          f"({len(capa)} piezas)")


if __name__ == "__main__":
    main()
