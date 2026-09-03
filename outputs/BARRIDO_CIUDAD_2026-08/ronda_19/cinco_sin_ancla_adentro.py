# -*- coding: utf-8 -*-
"""Las cinco páginas cuyo borde no contiene ningún establecimiento con historia: qué costaría.

QUÉ MIDE
--------
El control anterior encontró cinco páginas donde el borde publicado no contiene **ninguno** de
los establecimientos con trayectoria sobre los que la zona se apoya. Acá se mide, para cada una,
**qué pasaría si el borde se extendiera lo mínimo necesario para contenerlos**: superficie y
locales de las dos versiones, y por dónde habría que extender.

**No se adopta ninguna.** La decisión es la misma que resolvió los dos casos anteriores: se
extiende cuando el establecimiento está pegado a lo que el perímetro escrito ya nombra, y no se
extiende cuando llegar hasta él cambia el objeto que la página describe. Para poder aplicarla
hace falta saber, establecimiento por establecimiento, si la calle de su puerta es una de las que
el perímetro escrito ya nombra. Esa columna es el resultado principal de esta corrida.

LA REGLA DE EXTENSIÓN, ESCRITA ANTES DE MEDIR
---------------------------------------------
Para cada establecimiento que hoy queda afuera se toma **la calle de su dirección** y el tramo de
esa calle que va **del borde vigente hasta su puerta** —ni una cuadra más—, y se suman las
manzanas frentistas de ese tramo con el mismo frente mínimo de 20 m con el que se trazó todo lo
demás. No se elige el recorrido más corto sobre el mapa: se extiende sobre la calle en la que el
establecimiento está, que es lo que una página puede escribir.

Se mide en EPSG:5347 y se guarda en EPSG:4326. Cero requests.
"""

import csv
import json
import sys
from datetime import date
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from shapely.ops import nearest_points, unary_union

SALIDA = Path(__file__).resolve().parent
BARRIDO = SALIDA.parent
sys.path.insert(0, str(SALIDA))
sys.path.insert(0, str(BARRIDO / "ronda_18"))
sys.path.insert(0, str(BARRIDO / "ronda_17"))
import geometria_vigente_19 as gv  # noqa: E402
from cierre_geometrico import Callejero  # noqa: E402
from geometria_vigente_19 import limpia  # noqa: E402

CRS_M, CRS_G = "EPSG:5347", "EPSG:4326"
HOY = date.today().isoformat()
HITOS = BARRIDO / "hitos" / "hitos_capa_2026_r11.csv"
ANCLAS = BARRIDO / "ronda_18" / "anclas_dentro_y_fuera.csv"
FICHAS = BARRIDO / "ronda_17_codex" / "fichas_corpus_polos.csv"

# --------------------------------------------------------------------------------------------
# LAS CALLES QUE EL PERÍMETRO ESCRITO DE CADA PÁGINA NOMBRA.
#
# Se declaran acá, copiadas del texto de la ficha, y la frase de la que salen se imprime en la
# salida para que se pueda cotejar. No se extraen con una expresión regular sobre la prosa:
# «Barrio Charrúa» no es una calle y «sus intersecciones con la avenida Suárez» sí lo es, y esa
# diferencia no la resuelve un patrón.
# --------------------------------------------------------------------------------------------
PERIMETRO_ESCRITO = {
    "Z32": ["SUAREZ, JOSE LEON", "FALCON, RAMON L.,CNEL.", "IBARROLA", "BOSCH, VENTURA"],
    "Z35": ["TUCUMAN", "PASO"],
    "Z40": ["CASEROS AV.", "SAENZ AV."],
    "Z52": ["NECOCHEA", "SUAREZ", "OLAVARRIA", "BROWN, ALTE. AV."],
    "Z54": ["SAENZ AV."],
}
# De dónde sale cada lista, para que la salida lo diga y no haya que creerle al script.
DE_DONDE = {
    "Z32": "«EJE: José León Suárez entre Ramón Falcón y Ventura Bosch… Transversales: Ramón "
           "Falcón, Ibarrola y Ventura Bosch»",
    "Z35": "la página no escribe perímetro —dice «en revisión»—; las calles son las de las cinco "
           "puertas del enclave que la propia página lista, que es de donde salió el borde",
    "Z40": "«Av. Caseros / Distrito Tecnológico + Av. Sáenz / Mercado de Pompeya + Barrio "
           "Charrúa»",
    "Z52": "«el tramo de la calle Necochea y sus intersecciones con la avenida Suárez y la calle "
           "Olavarría… desde la avenida Suárez y la calle Olavarría, extendiéndose hasta la "
           "avenida Almirante Brown»",
    "Z54": "«Eje Av. Sáenz, con núcleo en el Mercado de Pompeya (Av. Sáenz 790)»",
}
# La calle de la puerta de cada establecimiento, tal como la escribe la capa de reconocimiento,
# resuelta contra el callejero oficial. Se declara para que un nombre que no resuelva corte la
# corrida en vez de saltearse en silencio.
CALLE_DEL_HITO = {
    "El Ciervo": "CARHUE",
    "CAFE DE LOS ANGELITOS": "RIVADAVIA AV.",
    "El Tropezón": "CALLAO AV.",
    "Roma del Abasto": "ANCHORENA, TOMAS MANUEL DE, DR.",
    "El Buzón": "ESQUIU",
    "El Estano 1880": "VALLE, ARISTOBULO DEL",
    "Bar Boca a Boca": "PEREZ GALDOS, BENITO AV.",
    "LA PERLA": "DON PEDRO DE MENDOZA AV.",
    "Il Matterello": "RODRIGUEZ, MARTIN",
    "El Portuario": "PINZON",
    "Café Roma": "OLAVARRIA",
    "La Buena Medida": "SUAREZ",
    "Banchero": "SUAREZ",
}
# La Perla ya está adentro de otro polo: el de Caminito, que se extendió el mes pasado
# exactamente para contenerla. Extender esta página hasta ella sería traérsela de la otra.
YA_ESTA_EN_OTRO_POLO = {"LA PERLA": "Z53 · La Boca · Caminito y Vuelta de Rocha"}


def p(*a):
    print(*a)


def tramo_hasta(cj, nom_calle, borde, punto_puerta):
    """El tramo de `nom_calle` que va del borde hasta la puerta. Ni una cuadra más.

    La cuadra de la puerta va SIEMPRE, y va aparte. El selector de tramos entre dos puntos se
    queda con los segmentos cuyo **centro** cae entre los dos, y el centro de la cuadra donde
    está la puerta cae más allá de la puerta: sin esta línea el tramo termina una cuadra antes y
    la extensión no contiene el establecimiento que se está yendo a buscar. Pasó con tres de los
    trece —el Café de los Angelitos, el Café Roma y Roma del Abasto— y la primera corrida no
    falló: devolvió una extensión que no contenía nada, con una cifra de superficie creíble.
    """
    segs = cj.segmentos(nom_calle)
    eje = unary_union(list(segs.geometry))
    pa = nearest_points(eje, borde)[0]
    pb = nearest_points(eje, punto_puerta)[0]
    cuadra = segs.geometry.loc[segs.geometry.distance(punto_puerta).idxmin()]
    partes = [cuadra]
    if pa.distance(pb) >= 1.0:
        entre = cj._tramo_entre(segs, pa, pb, holgura_m=120.0)
        if entre is not None and not entre.is_empty:
            partes.append(entre)
    tramo = unary_union(partes)
    return tramo, tramo.length


def piezas(g):
    """Cuántas piezas sueltas tiene la figura. Tres de los cinco bordes ya llegan partidos, así
    que «quedó en dos piezas» no dice nada si no se publica con cuántas empezó."""
    return 1 if g.geom_type == "Polygon" else len(g.geoms)


def extender(cj, borde, tramos):
    """El borde más las manzanas frentistas de los tramos. `limpia` antes de cada booleana."""
    partes = [limpia(borde)]
    for tramo in tramos:
        frent = cj.frentistas(tramo)
        if frent:
            partes.append(limpia(unary_union([c for _, _, c in frent])))
    return limpia(unary_union(partes))


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    p("=" * 98)
    p("LAS CINCO PÁGINAS SIN NINGÚN ESTABLECIMIENTO CON HISTORIA ADENTRO")
    p("qué costaría extender el borde lo mínimo necesario para contenerlos")
    p("=" * 98 + "\n")

    cj = Callejero()
    bordes, procedencia, soportes = gv.cargar()
    fichas = pd.read_csv(FICHAS).set_index("polo_id")

    # los establecimientos, con su punto real de la capa de reconocimiento
    hitos = pd.read_csv(HITOS)
    hitos = hitos[hitos.latitud.notna()]
    punto_de = {}
    for r in hitos.itertuples():
        pt = gpd.GeoSeries([Point(r.longitud, r.latitud)], crs=CRS_G).to_crs(CRS_M).iloc[0]
        punto_de.setdefault(str(r.nombre), pt)

    # las filas del control anterior: quién queda afuera de cuál página
    anclas = pd.read_csv(ANCLAS)
    con_historia = anclas[(anclas.sostiene_condicion_historia == "si")
                          & (anclas.dentro_del_borde == "no")]

    resumen = json.loads(
        (BARRIDO / "ronda_18" / "anclas_resumen.json").read_text(encoding="utf-8"))
    paginas = resumen["paginas_sin_ninguno_adentro"]
    p(f"las cinco páginas: {len(paginas)}")
    for x in paginas:
        p(f"    {x}")
    p("")

    filas_pagina, filas_detalle = [], []
    capa = []

    for etiqueta in paginas:
        pid = etiqueta.split(" · ")[0].strip()
        borde = bordes[pid]
        nombre = str(soportes.polo_nombre.loc[pid])
        ha0, loc0 = cj.ha(borde), cj.locales(borde)
        nombradas = PERIMETRO_ESCRITO[pid]
        objetivos = con_historia[con_historia.polo == etiqueta]

        p("=" * 98)
        p(f"{pid} · {nombre}")
        p("=" * 98)
        p(f"  el borde de ahora: {ha0:,.2f} ha · {loc0} locales · {piezas(borde)} "
          f"pieza(s) ({procedencia[pid]})")
        p(f"  el perímetro escrito nombra: {', '.join(nombradas)}")
        p(f"      de donde sale: {DE_DONDE[pid]}")
        p(f"  establecimientos con historia que hoy quedan afuera: {len(objetivos)}\n")

        tramos_todos, tramos_nombradas, tramos_propios, detalle_pid = [], [], [], []
        for r in objetivos.itertuples():
            est = str(r.establecimiento)
            calle = CALLE_DEL_HITO.get(est)
            if calle is None:
                raise SystemExit(f"«{est}» no tiene calle declarada en CALLE_DEL_HITO. No se "
                                 f"sigue con un objetivo de menos.")
            pt = punto_de.get(est)
            if pt is None:
                raise SystemExit(f"«{est}» no tiene punto en la capa de reconocimiento.")
            ya_nombrada = calle in nombradas
            de_otro = YA_ESTA_EN_OTRO_POLO.get(est, "")
            eje_calle = unary_union(list(cj.segmentos(calle).geometry))
            toca = eje_calle.distance(borde)
            tramo, largo = tramo_hasta(cj, calle, borde, pt)
            solo = extender(cj, borde, [tramo])
            queda = solo.covers(pt)
            tramos_todos.append(tramo)
            if ya_nombrada:
                tramos_nombradas.append(tramo)
            if not de_otro:
                tramos_propios.append(tramo)
            p(f"    {est[:30]:<32} {calle[:30]:<32} "
              f"{'YA LA NOMBRA' if ya_nombrada else 'calle nueva  '}  "
              f"a {r.distancia_m:>6,.0f} m · tramo {largo:>5,.0f} m -> "
              f"{cj.ha(solo):>7,.2f} ha ({cj.ha(solo) - ha0:+6,.2f}) · "
              f"{cj.locales(solo):>4} locales ({cj.locales(solo) - loc0:+4d})"
              + ("" if queda else "   NO LO CONTIENE")
              + (f"   [la calle no toca el borde: {toca:,.0f} m]" if toca > 1 else "")
              + (f"   [ya está en {de_otro.split(' · ')[0]}]" if de_otro else ""))
            fila = dict(
                polo_id=pid, polo=nombre, establecimiento=est, tipo=str(r.tipo),
                direccion=str(r.direccion), distancia_al_borde_m=round(float(r.distancia_m), 1),
                calle_de_la_puerta=calle,
                la_nombra_el_perimetro_escrito="si" if ya_nombrada else "no",
                la_calle_toca_el_borde="si" if toca <= 1 else f"no, a {toca:,.0f} m",
                tramo_a_agregar_m=round(largo),
                ha_si_se_extiende_solo_por_este=round(cj.ha(solo), 2),
                locales_si_se_extiende_solo_por_este=cj.locales(solo),
                delta_ha=round(cj.ha(solo) - ha0, 2),
                delta_locales=cj.locales(solo) - loc0,
                queda_adentro="si" if queda else "no",
                piezas_del_borde_actual=piezas(borde),
                piezas_si_se_extiende=piezas(solo),
                ya_esta_dentro_de_otro_polo=de_otro)
            filas_detalle.append(fila)
            detalle_pid.append(fila)

        # --- la versión que los contiene a todos
        ext = extender(cj, borde, tramos_todos) if tramos_todos else borde
        ha1, loc1 = cj.ha(ext), cj.locales(ext)
        contenidos = sum(1 for r in objetivos.itertuples()
                         if punto_de.get(str(r.establecimiento)) is not None
                         and ext.covers(punto_de[str(r.establecimiento)]))
        # --- la versión que sólo usa calles que el perímetro escrito ya nombra
        ext_n = extender(cj, borde, tramos_nombradas) if tramos_nombradas else borde
        ha2, loc2 = cj.ha(ext_n), cj.locales(ext_n)
        contenidos_n = sum(1 for r in objetivos.itertuples()
                           if punto_de.get(str(r.establecimiento)) is not None
                           and ext_n.covers(punto_de[str(r.establecimiento)]))
        # --- la versión que deja fuera a los que ya están dentro de otro polo
        hay_de_otro = len(tramos_propios) != len(tramos_todos)
        ext_p = extender(cj, borde, tramos_propios) if hay_de_otro else ext
        ha3, loc3 = cj.ha(ext_p), cj.locales(ext_p)

        p("")
        p(f"  A · el borde de ahora                                  "
          f"{ha0:>8,.2f} ha · {loc0:>4} locales · contiene 0 de {len(objetivos)}")
        p(f"  B · extendido hasta contenerlos a todos                "
          f"{ha1:>8,.2f} ha · {loc1:>4} locales · contiene {contenidos} de {len(objetivos)}"
          f"   ({ha1 / ha0 if ha0 else 0:,.1f}× la superficie)")
        if tramos_nombradas:
            p(f"  C · extendido sólo por las calles que el texto nombra   "
              f"{ha2:>8,.2f} ha · {loc2:>4} locales · contiene {contenidos_n} de "
              f"{len(objetivos)}")
        else:
            p(f"  C · extendido sólo por las calles que el texto nombra   "
              f"no existe: ninguno de los que quedan afuera está sobre una calle que el "
              f"perímetro escrito nombre")
        if hay_de_otro:
            p(f"  D · como B, sin ir a buscar los que ya están en otro polo "
              f"{ha3:>8,.2f} ha · {loc3:>4} locales")
        p("")

        capa.append(dict(zona_id=pid, nombre=nombre, version="A · el borde de ahora",
                         ha=round(ha0, 2), n_locales=loc0, geometry=borde))
        capa.append(dict(zona_id=pid, nombre=nombre,
                         version="B · extendido hasta contenerlos a todos",
                         ha=round(ha1, 2), n_locales=loc1, geometry=ext))
        if tramos_nombradas:
            capa.append(dict(zona_id=pid, nombre=nombre,
                             version="C · sólo sobre calles que el perímetro escrito nombra",
                             ha=round(ha2, 2), n_locales=loc2, geometry=ext_n))
        if hay_de_otro:
            capa.append(dict(zona_id=pid, nombre=nombre,
                             version="D · como B, sin los que ya están en otro polo",
                             ha=round(ha3, 2), n_locales=loc3, geometry=ext_p))

        filas_pagina.append(dict(
            polo_id=pid, polo=nombre,
            ha_borde_actual=round(ha0, 2), locales_borde_actual=loc0,
            con_historia_afuera=len(objetivos),
            establecimientos_afuera="; ".join(sorted(objetivos.establecimiento.astype(str))),
            distancia_minima_m=round(float(objetivos.distancia_m.min()), 1) if len(objetivos) else "",
            distancia_maxima_m=round(float(objetivos.distancia_m.max()), 1) if len(objetivos) else "",
            calles_del_perimetro_escrito=", ".join(nombradas),
            calles_a_las_que_habria_que_extender=", ".join(
                sorted({f["calle_de_la_puerta"] for f in detalle_pid})),
            cuantas_ya_las_nombra_el_texto=sum(
                1 for f in detalle_pid if f["la_nombra_el_perimetro_escrito"] == "si"),
            ha_extendido_todos=round(ha1, 2), locales_extendido_todos=loc1,
            delta_ha_todos=round(ha1 - ha0, 2), delta_locales_todos=loc1 - loc0,
            veces_la_superficie=round(ha1 / ha0, 2) if ha0 else "",
            contiene_todos="si" if contenidos == len(objetivos) else f"{contenidos}/{len(objetivos)}",
            ha_extendido_solo_calles_nombradas=round(ha2, 2) if tramos_nombradas else "",
            locales_extendido_solo_calles_nombradas=loc2 if tramos_nombradas else "",
            alcanza_solo_calles_nombradas=(f"{contenidos_n}/{len(objetivos)}"
                                           if tramos_nombradas else "0 (no hay ninguna)"),
            ha_sin_los_que_ya_estan_en_otro_polo=round(ha3, 2) if hay_de_otro else "",
            locales_sin_los_que_ya_estan_en_otro_polo=loc3 if hay_de_otro else "",
            piezas_del_borde_actual=piezas(borde),
            piezas_del_borde_extendido=piezas(ext),
            borde_transitorio="si" if pid in gv.TRANSITORIOS else "no"))

    # ------------------------------------------------------------------ salidas
    campos_p = list(filas_pagina[0].keys())
    with (SALIDA / "cinco_sin_ancla_adentro.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=campos_p)
        w.writeheader()
        w.writerows(filas_pagina)
    campos_d = list(filas_detalle[0].keys())
    with (SALIDA / "cinco_sin_ancla_detalle.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=campos_d)
        w.writeheader()
        w.writerows(filas_detalle)
    (SALIDA / "geometria").mkdir(exist_ok=True)
    gpd.GeoDataFrame(capa, geometry="geometry", crs=CRS_M).to_crs(CRS_G).to_file(
        SALIDA / "geometria" / "cinco_sin_ancla_versiones.geojson", driver="GeoJSON")
    (SALIDA / "cinco_sin_ancla_resumen.json").write_text(
        json.dumps(dict(fecha=HOY, paginas=filas_pagina), ensure_ascii=False, indent=2),
        encoding="utf-8")

    p("=" * 98)
    p("EL CUADRO, LAS CINCO JUNTAS")
    p("=" * 98)
    p(f"  {'página':<42} {'ahora ha':>9} {'loc':>5}   {'extendido ha':>12} {'loc':>5}  "
      f"{'×sup':>5}  {'calles ya nombradas':>20}")
    for f in filas_pagina:
        p(f"  {(f['polo_id'] + ' · ' + f['polo'])[:40]:<42} {f['ha_borde_actual']:>9,.2f} "
          f"{f['locales_borde_actual']:>5} {f['ha_extendido_todos']:>12,.2f} "
          f"{f['locales_extendido_todos']:>5}  {f['veces_la_superficie']:>5}  "
          f"{f['cuantas_ya_las_nombra_el_texto']:>4} de {f['con_historia_afuera']}")
    p(f"\nEscrito: cinco_sin_ancla_adentro.csv ({len(filas_pagina)} filas) · "
      f"cinco_sin_ancla_detalle.csv ({len(filas_detalle)} filas) · "
      f"geometria/cinco_sin_ancla_versiones.geojson · cinco_sin_ancla_resumen.json")


if __name__ == "__main__":
    main()
