# -*- coding: utf-8 -*-
"""Los bordes de la ronda 18: dos decisiones firmadas, un borde tentativo y una lectura doble.

QUÉ HACE ESTA CORRIDA
---------------------
  1. **Balvanera · Once, las dos lecturas.** El borde que se adoptó deja al Café de los Angelitos
     —Av. Rivadavia 2100, Bar Notable, el establecimiento con el que la vía B admitió la zona—
     768 m afuera. Se miden las dos y se entregan las dos; la decisión la firma quien escribe.
  2. **La Boca · Caminito se extiende** hasta contener La Perla de Caminito. Decisión firmada.
  3. **Mataderos** recibe un borde **tentativo**, declarado tentativo, sobre el cruce de las dos
     avenidas que la ficha nombra.
  4. **Villa Ortúzar** se lleva la opción B ya adoptada, sin rehacer geometría.

REGLAS QUE NO SE RELAJAN
------------------------
  - Se mide en EPSG:5347 y se guarda en EPSG:4326. Nunca se mide en 4326.
  - La contención entre polígonos se verifica por **superficie perdida** —`B.difference(A).area`—
    y nunca con `covers()`. Para un PUNTO contra un polígono sí se usa `covers`, y el motivo está
    escrito en la ronda 17: el punto de una altura cae sobre el eje de la calle, que es el mismo
    borde por el que están cortadas las manzanas; con `contains`, un establecimiento a 0 m del
    borde se cuenta como afuera.
  - `buffer(0)` antes de cada operación booleana.
  - Un nombre de calle que no resuelve corta la corrida.

Cero requests. Se ejecuta con .venv/Scripts/python.exe.
"""

import csv
import json
import sys
from datetime import date
from pathlib import Path

import geopandas as gpd
from shapely.ops import unary_union

SALIDA = Path(__file__).resolve().parent
sys.path.insert(0, str(SALIDA.parent / "ronda_17"))
from cierre_geometrico import Callejero, limpia, resolver  # noqa: E402

CRS_METRICO = "EPSG:5347"
CRS_G = "EPSG:4326"
HOY = date.today().isoformat()

LDT = "DE LA TORRE, LISANDRO AV."
CORR = "DE LOS CORRALES AV."
ALB = "ALBERDI, JUAN BAUTISTA AV."
DPM = "DON PEDRO DE MENDOZA AV."


def p(*a):
    print(*a)


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    p("=" * 98)
    p("BORDES · dos decisiones firmadas, un borde tentativo y una lectura que queda abierta")
    p("=" * 98 + "\n")

    cj = Callejero()
    filas, capa, resumen = [], [], {}

    def medir(pieza):
        tramo, poligono, detalle = resolver(cj, pieza)
        if poligono is None:
            raise SystemExit(f"no resuelve: {detalle}. No se sigue con un tramo de menos.")
        return tramo, limpia(poligono), detalle

    # ======================================================================= 1 · BALVANERA
    p("=" * 98)
    p("Z35 · Balvanera · Once   ·   LAS DOS LECTURAS, LAS DOS MEDIDAS")
    p("=" * 98)
    p("  El Café de los Angelitos, Av. Rivadavia 2100, Bar Notable verificado abierto a junio de")
    p("  2026, es la evidencia con la que la vía B admitió esta zona. El borde adoptado en la")
    p("  ronda anterior lo deja afuera. Se miden las dos lecturas y se entregan las dos.\n")

    ang = cj.punto_de_altura("RIVADAVIA AV.", 2100)
    if ang is None:
        raise SystemExit("Av. Rivadavia 2100 no está en el callejero. No se sigue.")

    pz_tucuman = dict(tipo="eje_por_altura", calle="TUCUMAN", desde=2379, hasta=2755)
    pz_paso = dict(tipo="eje_por_altura", calle="PASO", desde=700, hasta=799)
    pz_pasteur = dict(tipo="eje_entre", calle="PASTEUR", corte_a="TUCUMAN",
                      corte_b="RIVADAVIA AV.")
    pz_riv = dict(tipo="eje_por_altura", calle="RIVADAVIA AV.", desde=2001, hasta=2200)

    t1, g1, d1 = medir(pz_tucuman)
    t2, g2, d2 = medir(pz_paso)
    t3, g3, d3 = medir(pz_pasteur)
    t4, g4, d4 = medir(pz_riv)

    lect_a = limpia(unary_union([g1, g2]))
    lect_b = limpia(unary_union([g1, g2, g3, g4]))

    p("  LECTURA 1 · el enclave, como está")
    for det, tr, g in ((d1, t1, g1), (d2, t2, g2)):
        p(f"      {det:<46} eje {tr.length:6,.0f} m -> {cj.ha(g):6,.2f} ha, "
          f"{cj.locales(g):3d} locales")
    p(f"    total: {cj.ha(lect_a):,.2f} ha · {cj.locales(lect_a)} locales · "
      f"{lect_a.geom_type}")
    p(f"    Café de los Angelitos: AFUERA, a {lect_a.distance(ang):,.0f} m\n")

    p("  LECTURA 2 · extendida hasta contener el Café de los Angelitos")
    p("    por dónde se extiende: por Pasteur, que es la transversal que corta el eje de Tucumán")
    p("    en el extremo sur del enclave -Tucumán 2301-2400, el bloque que contiene el 2379- y la")
    p("    única de las cinco que llegan a Av. Rivadavia que lo hace más cerca del Café: su cruce")
    p("    con Rivadavia cae a 325 m del Café, contra 451 m por Azcuénaga, 572 por Larrea, 713")
    p("    por Paso y 956 por Av. Pueyrredón. Al sur de Rivadavia, Pasteur se llama Pichincha.")
    for det, tr, g in ((d1, t1, g1), (d2, t2, g2), (d3, t3, g3), (d4, t4, g4)):
        p(f"      {det:<46} eje {tr.length:6,.0f} m -> {cj.ha(g):6,.2f} ha, "
          f"{cj.locales(g):3d} locales")
    p(f"    total: {cj.ha(lect_b):,.2f} ha · {cj.locales(lect_b)} locales · "
      f"{lect_b.geom_type}")
    p(f"    Café de los Angelitos: ADENTRO, a {lect_b.distance(ang):,.0f} m")
    p(f"    cuánto se extendió: {t3.length + t4.length:,.0f} m de eje nuevo "
      f"({t3.length:,.0f} m sobre Pasteur y {t4.length:,.0f} m sobre Av. Rivadavia), "
      f"+{cj.ha(lect_b) - cj.ha(lect_a):,.2f} ha y +{cj.locales(lect_b) - cj.locales(lect_a)} "
      f"locales")
    p("    es el mínimo: con Av. Rivadavia 2001-2100 -una sola cuadra- el Café queda adentro")
    p("    pero la figura se parte en dos piezas sueltas; con 2001-2200 vuelve a ser una sola.\n")

    # los establecimientos con reconocimiento de cada lectura
    for etiqueta, geom in (("lectura 1 · enclave", lect_a), ("lectura 2 · extendida", lect_b)):
        p(f"  qué establecimientos con reconocimiento contiene la {etiqueta}:")
        dentro = anclas_dentro(cj, geom)
        if not dentro:
            p("      ninguno de la capa de reconocimiento")
        for nom, tipo, dist in dentro:
            p(f"      {nom:<34} {tipo}")
        p("")

    for etiqueta, geom, cual in (("lectura_1_enclave", lect_a, "1"),
                                 ("lectura_2_extendida", lect_b, "2")):
        capa.append(dict(
            zona_id="Z35", nombre="Balvanera · Once", pieza=f"la zona entera · {etiqueta}",
            caracter="lectura medida, decisión abierta",
            fuente_del_perimetro=(
                "Eje Tucumán 2379-2755 y transversal Paso 700-799, del enclave que la ficha "
                "lista" if cual == "1" else
                "Eje Tucumán 2379-2755, transversal Paso 700-799, transversal Pasteur entre "
                "Tucumán y Av. Rivadavia, y Av. Rivadavia 2001-2200 para contener el Café de "
                "los Angelitos"),
            de_donde_sale_la_extension=(
                "las cinco puertas del enclave, del padrón oficial de 2015" if cual == "1" else
                "las cinco puertas del enclave más el Café de los Angelitos, Av. Rivadavia "
                "2100, Bar Notable"),
            metodo="manzanas frentistas del callejero (frente mínimo 20 m)",
            ha=round(cj.ha(geom), 2), n_locales=cj.locales(geom), geometry=geom))

    resumen["Z35"] = dict(
        lectura_1_ha=round(cj.ha(lect_a), 2), lectura_1_locales=cj.locales(lect_a),
        lectura_2_ha=round(cj.ha(lect_b), 2), lectura_2_locales=cj.locales(lect_b),
        angelitos_afuera_de_1_m=round(lect_a.distance(ang), 1),
        eje_nuevo_m=round(t3.length + t4.length))

    filas.append(dict(
        zona_id="Z35", nombre="Balvanera · Once", caracter="dos lecturas medidas",
        ha=round(cj.ha(lect_a), 2), n_locales=cj.locales(lect_a),
        ha_alternativa=round(cj.ha(lect_b), 2), n_locales_alternativa=cj.locales(lect_b),
        que_cambia=("la lectura 2 contiene el Café de los Angelitos, que es la evidencia con la "
                    "que la zona entró; la lectura 1 lo deja a 768 m"),
        fuente_del_perimetro="las cinco puertas del enclave (lectura 1) · más el Café de los "
                             "Angelitos (lectura 2)",
        metodo="manzanas frentistas del callejero",
        decision="abierta: la firma quien escribe"))

    # ======================================================================= 2 · LA BOCA
    p("=" * 98)
    p("Z53 · La Boca · Caminito y Vuelta de Rocha   ·   DECISIÓN FIRMADA: SE EXTIENDE")
    p("=" * 98)
    p("  Criterio que va escrito en la página: el polo se extiende sobre Av. Don Pedro de")
    p("  Mendoza lo mínimo necesario para contener La Perla de Caminito, que es el")
    p("  establecimiento sobre el que la zona se apoya.\n")

    t_cam, g_cam, d_cam = medir(dict(tipo="eje_completo", calle="CAMINITO"))
    t_av, g_av, d_av = medir(dict(tipo="eje_por_altura", calle=DPM, desde=1871, hasta=1939))
    laboca = limpia(unary_union([g_cam, g_av]))
    p(f"    {d_cam:<46} eje {t_cam.length:6,.0f} m -> {cj.ha(g_cam):6,.2f} ha, "
      f"{cj.locales(g_cam):3d} locales")
    p(f"    {d_av:<46} eje {t_av.length:6,.0f} m -> {cj.ha(g_av):6,.2f} ha, "
      f"{cj.locales(g_av):3d} locales")
    p(f"    el polígono adoptado: {cj.ha(laboca):,.2f} ha · {cj.locales(laboca)} locales · "
      f"{laboca.geom_type}")
    antes = limpia(g_cam)
    p(f"    contra el borde anterior (sólo Caminito, {cj.ha(antes):,.2f} ha): "
      f"{cj.ha(laboca) - cj.ha(antes):+,.2f} ha · "
      f"{cj.locales(laboca) - cj.locales(antes):+d} locales\n")

    p("  los tres establecimientos que la página nombra:")
    for nom, calle, altura in (("La Perla de Caminito", DPM, 1899),
                               ("Genovés", "BRANDSEN", 923),
                               ("El Obrero", "CAFFARENA, AGUSTIN R.", 64)):
        pt = cj.punto_de_altura(calle, altura)
        if pt is None:
            p(f"      {nom:<24} {calle} {altura}: la altura no está en el callejero")
            continue
        estado = "ADENTRO" if laboca.covers(pt) else "afuera"
        p(f"      {nom:<24} {estado:<8} a {laboca.distance(pt):5,.0f} m del borde nuevo "
          f"(era {antes.distance(pt):5,.0f} m del anterior)")
    p("")

    capa.append(dict(
        zona_id="Z53", nombre="La Boca · Caminito y Vuelta de Rocha",
        pieza="la zona entera, como se adopta", caracter="borde cerrado",
        fuente_del_perimetro=(
            "Caminito entero más las dos cuadras de Av. Don Pedro de Mendoza que toca, 1871-1939. "
            "El polo se extiende sobre la avenida lo mínimo necesario para contener La Perla de "
            "Caminito, que es el establecimiento sobre el que la zona se apoya."),
        de_donde_sale_la_extension="La Perla de Caminito, Av. Don Pedro de Mendoza 1899",
        metodo="manzanas frentistas del callejero (frente mínimo 20 m)",
        ha=round(cj.ha(laboca), 2), n_locales=cj.locales(laboca), geometry=laboca))
    filas.append(dict(
        zona_id="Z53", nombre="La Boca · Caminito y Vuelta de Rocha", caracter="borde cerrado",
        ha=round(cj.ha(laboca), 2), n_locales=cj.locales(laboca),
        ha_alternativa="", n_locales_alternativa="",
        que_cambia=f"el borde pasa de {cj.ha(antes):,.2f} ha a {cj.ha(laboca):,.2f} ha y de "
                   f"{cj.locales(antes)} a {cj.locales(laboca)} locales; La Perla de Caminito "
                   f"pasa de estar 26 m afuera a estar adentro",
        fuente_del_perimetro="Caminito más Av. Don Pedro de Mendoza 1871-1939",
        metodo="manzanas frentistas del callejero", decision="firmada"))
    resumen["Z53"] = dict(ha=round(cj.ha(laboca), 2), n_locales=cj.locales(laboca))

    # ======================================================================= 3 · MATADEROS
    p("=" * 98)
    p("Z33 · Mataderos   ·   BORDE TENTATIVO, DECLARADO TENTATIVO")
    p("=" * 98)
    cruce = cj._punto_de_cruce(cj.segmentos(LDT), cj.segmentos(CORR))
    tramo_cruce = unary_union([cj.eje_completo(LDT), cj.eje_completo(CORR)]).intersection(
        cruce.buffer(150))
    frent = cj.frentistas(tramo_cruce)
    mat = limpia(unary_union([c for _, _, c in frent]))
    p(f"  regla 1 · las manzanas frentistas del cruce de Av. Lisandro de la Torre y Av. de los")
    p(f"  Corrales, con el entorno mínimo que cierra una figura sobre el callejero:")
    p(f"      {len(frent)} manzanas · eje {tramo_cruce.length:,.0f} m -> "
      f"{cj.ha(mat):,.2f} ha, {cj.locales(mat)} locales · {mat.geom_type}")
    areas = sorted((c.area / 10_000 for _, _, c in frent), reverse=True)
    p(f"      la figura la domina una sola manzana de {areas[0]:,.2f} ha -el predio cerrado del")
    p(f"      cruce-; las otras {len(areas) - 1} suman {sum(areas[1:]):,.2f} ha. Es la razón por")
    p(f"      la que esta zona mide mucha superficie con pocos locales, y hay que decirlo antes")
    p(f"      de que alguien divida una cosa por la otra.\n")

    refs_mat = (("Bar Oviedo", LDT, 2407), ("9 de Julio", "LARRAZABAL", 1276),
                ("Bar del Glorias", "ANDALGALA", 1982), ("El Cedrón", ALB, 6101))
    p("  regla 2 · ¿deja afuera a alguno de los cuatro que la página nombra?")
    afuera_mat = []
    for nom, calle, altura in refs_mat:
        pt = cj.punto_de_altura(calle, altura)
        if pt is None:
            p(f"      {nom:<18} {calle} {altura}: la altura no está en el callejero")
            continue
        if mat.covers(pt):
            p(f"      {nom:<18} ADENTRO")
        else:
            p(f"      {nom:<18} afuera, a {mat.distance(pt):,.0f} m  ({calle} {altura})")
            afuera_mat.append((nom, calle, altura, pt))
    p("")
    p("  la regla 2 dice «extendé sobre la avenida que corresponda». Medido: ninguno de los tres")
    p("  que quedan afuera está sobre las dos avenidas del perímetro escrito. Larrazábal y")
    p("  Andalgalá no son las avenidas que la ficha nombra, y Andalgalá no es una avenida. La")
    p("  avenida que los tres tienen cerca es otra —Av. Juan B. Alberdi, a 72 m del 9 de Julio,")
    p("  83 m del Bar del Glorias y 0 m de El Cedrón—, y llegar hasta ella exige un brazo de un")
    p("  kilómetro por Av. Lisandro de la Torre. Esa es la regla que no se puede aplicar, así")
    p("  que se mide lo que costaría y se declara, en vez de adoptarla en silencio.\n")

    t_brazo, g_brazo, d_brazo = medir(dict(tipo="eje_entre", calle=LDT, corte_a=CORR,
                                           corte_b=ALB))
    t_alb, g_alb, d_alb = medir(dict(tipo="eje_por_altura", calle=ALB, desde=5501, hasta=6499))
    mat_ext = limpia(unary_union([mat, g_brazo, g_alb]))
    p("  lectura medida y NO adoptada · el borde extendido hasta Av. Alberdi:")
    p(f"      brazo {d_brazo}")
    p(f"          eje {t_brazo.length:,.0f} m -> {cj.ha(g_brazo):,.2f} ha, "
      f"{cj.locales(g_brazo)} locales")
    p(f"      {d_alb}: eje {t_alb.length:,.0f} m -> {cj.ha(g_alb):,.2f} ha, "
      f"{cj.locales(g_alb)} locales")
    p(f"      total: {cj.ha(mat_ext):,.2f} ha, {cj.locales(mat_ext)} locales "
      f"(+{cj.ha(mat_ext) - cj.ha(mat):,.2f} ha, "
      f"+{cj.locales(mat_ext) - cj.locales(mat)} locales sobre el tentativo)")
    faltan = [n for n, c, a, _ in [(x[0], x[1], x[2], x[3]) for x in afuera_mat]
              if not mat_ext.covers(cj.punto_de_altura(c, a))]
    p(f"      y aun así deja afuera a {', '.join(faltan) if faltan else 'ninguno'}"
      + (f" (a {mat_ext.distance(cj.punto_de_altura('ANDALGALA', 1982)):,.0f} m)"
         if faltan else ""))
    p("      por qué no se adopta: duplica la superficie del borde tentativo para alcanzar dos")
    p("      referentes de cuatro, el brazo aporta 30 locales en 65 hectáreas, y el tramo de")
    p("      Alberdi que agrega es el eje del IDECBA, que se publica aparte y por separado.\n")

    p("  lectura medida y publicada aparte · el eje comercial que releva la Ciudad, "
      "Av. Alberdi 5501-6299:")
    _, g_alb0, d_alb0 = medir(dict(tipo="eje_por_altura", calle=ALB, desde=5501, hasta=6299))
    p(f"      {cj.ha(g_alb0):,.2f} ha, {cj.locales(g_alb0)} locales")
    p(f"      relación con el borde tentativo: son dos objetos separados. Lo más cerca que pasan")
    p(f"      es {mat.distance(g_alb0):,.0f} m y no comparten ni una hectárea "
      f"(intersección {limpia(mat.intersection(g_alb0)).area / 10_000:,.2f} ha).")
    dentro_alb = [n for n, c, a in refs_mat if g_alb0.covers(cj.punto_de_altura(c, a))]
    dentro_mat = [n for n, c, a in refs_mat if mat.covers(cj.punto_de_altura(c, a))]
    p(f"      el borde tentativo contiene {len(dentro_mat)} de los cuatro que la página nombra "
      f"({', '.join(dentro_mat)}); el eje comercial contiene {len(dentro_alb)} "
      f"({', '.join(dentro_alb)}). Entre los dos, tres de cuatro. El cuarto, el Bar del Glorias,")
    p(f"      no está en ninguno.")
    p(f"      el eje comercial es de otra fuente y mide otro objeto: adoptarlo como perímetro le")
    p(f"      atribuiría al polo el recorte del IDECBA.\n")

    capa.append(dict(
        zona_id="Z33", nombre="Mataderos", pieza="la zona entera, como se adopta",
        caracter="BORDE TENTATIVO · no es un borde cerrado",
        fuente_del_perimetro=(
            "Manzanas frentistas del cruce de Av. Lisandro de la Torre y Av. de los Corrales, "
            "el entorno mínimo que cierra una figura sobre el callejero. TENTATIVO: el texto de "
            "la ficha da el cruce y ninguna extensión, y el perímetro de ocupación de la Feria "
            "es un dato administrativo que el repositorio no tiene."),
        de_donde_sale_la_extension="el cruce de las dos avenidas que nombra el perímetro escrito",
        metodo="manzanas frentistas del callejero (frente mínimo 20 m), radio de 150 m sobre "
               "las dos avenidas desde el cruce",
        ha=round(cj.ha(mat), 2), n_locales=cj.locales(mat), geometry=mat))
    capa.append(dict(
        zona_id="Z33", nombre="Mataderos", pieza="eje comercial Av. Alberdi 5501-6299",
        caracter="lectura medida, NO adoptada como perímetro",
        fuente_del_perimetro="el eje comercial que releva la Ciudad (IDECBA). No es el perímetro "
                             "del polo: mide otro objeto y se publica aparte.",
        de_donde_sale_la_extension="IDECBA · eje comercial de Mataderos",
        metodo="manzanas frentistas del callejero (frente mínimo 20 m)",
        ha=round(cj.ha(g_alb0), 2), n_locales=cj.locales(g_alb0), geometry=g_alb0))
    filas.append(dict(
        zona_id="Z33", nombre="Mataderos", caracter="BORDE TENTATIVO",
        ha=round(cj.ha(mat), 2), n_locales=cj.locales(mat),
        ha_alternativa=round(cj.ha(mat_ext), 2), n_locales_alternativa=cj.locales(mat_ext),
        que_cambia=("pasa de no tener ninguna geometría a tener un borde tentativo sobre el "
                    "cruce de las dos avenidas; contiene 1 de los 4 establecimientos que la "
                    "página nombra"),
        fuente_del_perimetro="cruce de Av. Lisandro de la Torre y Av. de los Corrales",
        metodo="manzanas frentistas del callejero, radio 150 m desde el cruce",
        decision="tentativa: no se toma por definitiva"))
    resumen["Z33"] = dict(ha=round(cj.ha(mat), 2), n_locales=cj.locales(mat), tentativo=True,
                          extendido_ha=round(cj.ha(mat_ext), 2),
                          eje_alberdi_ha=round(cj.ha(g_alb0), 2),
                          eje_alberdi_locales=cj.locales(g_alb0))

    # ======================================================================= 4 · V. ORTÚZAR
    p("=" * 98)
    p("Z44 · Villa Ortúzar   ·   OPCIÓN B ADOPTADA · la geometría ya estaba, no se rehace")
    p("=" * 98)
    r17 = gpd.read_file(SALIDA.parent / "ronda_17" / "geometria" /
                        "perimetros_cierre.geojson").to_crs(CRS_METRICO)
    z44 = limpia(unary_union(list(
        r17[(r17.zona_id == "Z44") & (r17.pieza == "la zona entera, como se adopta")].geometry)))
    p(f"  las dos aceras de Av. Álvarez Thomas entre el 600 y el 1700: "
      f"{cj.ha(z44):,.2f} ha · {cj.locales(z44)} locales")
    rep = cj.reparto_por_barrio(z44)
    p("  reparto por barrio: " + " · ".join(f"{n} {x:.1f} %" for n, x, _ in rep))
    p("  que el corredor cruce tres barrios no es un problema: es una de las cosas que este")
    p("  atlas quiere mostrar. El control que sí hace falta es el del solape, y va aparte.\n")
    capa.append(dict(
        zona_id="Z44", nombre="Villa Ortúzar", pieza="la zona entera, como se adopta",
        caracter="borde cerrado",
        fuente_del_perimetro=("Av. Álvarez Thomas, tramo 600-1700, las dos aceras. El corredor "
                              "cruce tres barrios y el reparto se declara."),
        de_donde_sale_la_extension="la primera pieza del perímetro escrito",
        metodo="manzanas frentistas del callejero (frente mínimo 20 m)",
        ha=round(cj.ha(z44), 2), n_locales=cj.locales(z44), geometry=z44))
    filas.append(dict(
        zona_id="Z44", nombre="Villa Ortúzar", caracter="borde cerrado",
        ha=round(cj.ha(z44), 2), n_locales=cj.locales(z44),
        ha_alternativa="", n_locales_alternativa="",
        que_cambia="la opción B queda adoptada; la geometría es la misma que ya estaba medida",
        fuente_del_perimetro="Av. Álvarez Thomas 600-1700, las dos aceras",
        metodo="manzanas frentistas del callejero", decision="firmada"))
    resumen["Z44"] = dict(ha=round(cj.ha(z44), 2), n_locales=cj.locales(z44))

    # ======================================================================= salidas
    campos = ["zona_id", "nombre", "caracter", "ha", "n_locales", "ha_alternativa",
              "n_locales_alternativa", "que_cambia", "fuente_del_perimetro", "metodo", "decision"]
    with (SALIDA / "perimetros_ronda_18.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=campos)
        w.writeheader()
        w.writerows(filas)

    (SALIDA / "geometria").mkdir(exist_ok=True)
    gpd.GeoDataFrame(capa, geometry="geometry", crs=CRS_METRICO).to_crs(CRS_G).to_file(
        SALIDA / "geometria" / "perimetros_ronda_18.geojson", driver="GeoJSON")
    (SALIDA / "bordes_ronda_18.json").write_text(
        json.dumps(dict(fecha=HOY, **resumen), ensure_ascii=False, indent=2), encoding="utf-8")

    p("=" * 98)
    p(f"Escrito: perimetros_ronda_18.csv ({len(filas)} filas) · "
      f"geometria/perimetros_ronda_18.geojson ({len(capa)} piezas, {CRS_G}) · "
      f"bordes_ronda_18.json")
    p("=" * 98)


def anclas_dentro(cj, geom):
    """Los establecimientos de la capa de reconocimiento que caen dentro del polígono."""
    import pandas as pd
    from shapely.geometry import Point
    ruta = SALIDA.parent / "hitos" / "hitos_capa_2026_r11.csv"
    d = pd.read_csv(ruta)
    d = d[d.latitud.notna()]
    pts = gpd.GeoSeries([Point(x, y) for x, y in zip(d.longitud, d.latitud)],
                        crs=CRS_G).to_crs(CRS_METRICO)
    salida = []
    for (_, fila), pt in zip(d.iterrows(), pts):
        if geom.covers(pt):
            salida.append((str(fila.nombre), str(fila.tipo), 0.0))
    return sorted(salida)


if __name__ == "__main__":
    main()
