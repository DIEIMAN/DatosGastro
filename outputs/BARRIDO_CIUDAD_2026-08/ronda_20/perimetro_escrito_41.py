# -*- coding: utf-8 -*-
"""Qué perímetro tiene escrito cada una de las 41 páginas, y si el borde se reconstruye desde ahí.

DE DÓNDE SALE ESTE CONTROL
--------------------------
La tanda anterior dejó 33 establecimientos con reconocimiento cerca de un borde que no se pudieron
decidir, y dijo por qué: la prueba que decide —«¿la calle de su puerta la nombra el perímetro
escrito de su página?»— se corre contra un texto **de calidad desigual**. Hay páginas que dan
calles y alturas y hay páginas que no escriben perímetro. Antes de decidir esos 33 hay que saber
contra qué texto se los mide, página por página. Eso es esto.

CÓMO SE HACE, Y QUÉ PARTE NO PUEDE HACER UN PATRÓN
---------------------------------------------------
Mecánico:
  - **El recorte del bloque.** Va desde `**Dónde está.**` hasta el próximo rótulo en negrita
    terminado en punto —`**Reconocimiento oficial.**`, `**Por qué es un polo.**`— o el próximo
    título. Los párrafos sin rótulo que siguen entran: en Av. Montes de Oca **son** el perímetro.
  - **La resolución de cada nombre contra el callejero oficial.** Un nombre que no resuelve corta
    la corrida. Es la regla de siempre y acá importa el doble: la lista de calles de cada página
    es el insumo de la decisión de los 33.
  - **Si la calle toca el borde dibujado**, medido.

Declarado a mano, con el texto literal al lado para que se pueda cotejar:
  - **Qué nombres del bloque son calles y cuáles no.** «Barrio Charrúa» no es una calle, «sus
    intersecciones con la avenida Suárez» sí lo es, y esa diferencia no la resuelve una expresión
    regular. Es la misma advertencia que dejó escrita la tanda anterior.
  - **La categoría y si el borde se reconstruye.**

LAS CATEGORÍAS, DEFINIDAS ANTES DE MIRAR
-----------------------------------------
Se asignan por lo más fuerte que el bloque ofrece, y son mecánicas una vez decidido qué nombre es
una calle:

    da calles y alturas                    nombra calles y da números de puerta
    da calles sin alturas                  nombra calles y no da números
    da un cruce de avenidas sin extensión   nombra un cruce y no dice hasta dónde llega
    da un barrio o una referencia sin calles   nombra un barrio, una plaza o un mercado, sin calles
    no escribe perímetro                   no nombra nada: remite al «perímetro vigente» o dice
                                           «en revisión»

Y `reconstruible_desde_el_texto` toma tres valores, porque dos no alcanzan:

    si        el texto da las piezas Y su extensión: aplicando la regla con la que se trazó todo
              lo demás —las manzanas frentistas del tramo— sale la figura publicada sin elegir
              nada más
    en parte  alguna pieza tiene extensión y otra no
    no        no hay extensión, o la página misma declara que el trazado está en revisión

Se mide en EPSG:5347. Cero requests.
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
from extraer_donde_esta import paginas  # noqa: E402

CRS_M, CRS_G = "EPSG:5347", "EPSG:4326"
HOY = date.today().isoformat()
BORDES = SALIDA / "geometria" / "bordes_vigentes_41.geojson"
BASE = BARRIDO / "base" / "local.csv"

CON_ALTURAS = "da calles y alturas"
SIN_ALTURAS = "da calles sin alturas"
CRUCE = "da un cruce de avenidas sin extensión"
REFERENCIA = "da un barrio o una referencia sin calles"
NADA = "no escribe perímetro"

SI, PARTE, NO = "si", "en parte", "no"

# --------------------------------------------------------------------------------------------
# LA DECLARACIÓN, PÁGINA POR PÁGINA
#
#   calles       el nombre con el que el callejero oficial la tiene. Si no resuelve, corta.
#   como_dice    cómo la escribe la página, que es lo que va en la salida legible
#   referencias  lo que el bloque nombra y NO es una calle: plazas, mercados, barrios, enclaves
#   alturas      los números de puerta que el bloque escribe
#   categoria / reconstruible / por_que
# --------------------------------------------------------------------------------------------
D = [
 dict(pid="R01", calles=[], como_dice="",
      referencias="Soho; Hollywood; Las Cañitas; «el perímetro publicado de Palermo»",
      alturas="", categoria=REFERENCIA, reconstruible=NO,
      por_que="el bloque no describe un perímetro: explica cómo se publica un sistema de "
              "subzonas y da las cifras de cada una. Ninguna calle"),
 dict(pid="R02", calles=["CORRIENTES AV.", "CALLAO AV.", "PUEYRREDON AV."],
      como_dice="Av. Corrientes; Callao; Pueyrredón", referencias="el Obelisco",
      alturas="", categoria=SIN_ALTURAS, reconstruible=NO,
      por_que="da el eje y los dos extremos, pero la página declara que «el tramo exacto está "
              "por precisar» y el extremo norte es «el entorno de Callao/Pueyrredón»"),
 dict(pid="R03", calles=["DEFENSA"], como_dice="Defensa", referencias="Plaza Dorrego",
      alturas="", categoria=SIN_ALTURAS, reconstruible=NO,
      por_que="la delimitación es «perímetro vigente»: la calle y la plaza describen el núcleo, "
              "no el borde"),
 dict(pid="R04", calles=[], como_dice="", referencias="los diques", alturas="",
      categoria=REFERENCIA, reconstruible=NO,
      por_que="«perímetro vigente, organizado sobre los diques». Ninguna calle, ninguna extensión"),
 dict(pid="R05", calles=[], como_dice="", referencias="el enclave del Barrio Chino", alturas="",
      categoria=REFERENCIA, reconstruible=NO,
      por_que="«perímetro vigente» más el enclave que contiene. Ninguna calle"),
 dict(pid="R06", calles=[], como_dice="", referencias="", alturas="", categoria=NADA,
      reconstruible=NO, por_que="el bloque entero dice «Perímetro vigente.»"),
 dict(pid="R07", calles=[], como_dice="", referencias="", alturas="", categoria=NADA,
      reconstruible=NO, por_que="el bloque entero dice «Perímetro vigente.»"),
 dict(pid="R08", calles=["LOYOLA", "THAMES", "AGUIRRE"], como_dice="Loyola; Thames; Aguirre",
      referencias="", alturas="", categoria=SIN_ALTURAS, reconstruible=NO,
      por_que="tres ejes sin extensión, sobre un «perímetro vigente» de 335 ha: los ejes no la "
              "producen"),
 dict(pid="R09", calles=["ELCANO AV.", "ALVAREZ THOMAS AV.", "FOREST AV.", "NEWBERY, JORGE AV."],
      como_dice="Elcano; Álvarez Thomas; Forest; Jorge Newbery",
      referencias="", alturas="", categoria=SIN_ALTURAS, reconstruible=NO,
      por_que="las cuatro calles describen el corredor que comparte con Colegiales, no el borde "
              "propio, y la página dice que «el trazado conjunto está en revisión»"),
 dict(pid="R10", calles=["GOYENA, PEDRO AV."], como_dice="Av. Pedro Goyena", referencias="",
      alturas="", categoria=SIN_ALTURAS, reconstruible=NO,
      por_que="«perímetro vigente» más una subzona sobre una avenida, sin extensión"),
 dict(pid="R11", calles=["CASEROS AV.", "DEFENSA", "BOLIVAR", "PERU",
                         "MONTES DE OCA MANUEL AV"],
      como_dice="Av. Caseros; Defensa; Bolívar; Perú; Av. Montes de Oca", referencias="",
      alturas="", categoria=SIN_ALTURAS, reconstruible=SI,
      por_que="eje, los dos extremos y el tope máximo escritos: «Av. Caseros entre Defensa y "
              "Bolívar, una cuadra, como máximo hasta Perú», y dice hasta dónde NO llega"),
 dict(pid="R12", calles=[], como_dice="", referencias="Monserrat", alturas="",
      categoria=REFERENCIA, reconstruible=NO,
      por_que="«perímetro vigente» y el aviso de que se pisa con Monserrat. Ninguna calle"),
 dict(pid="R13", calles=[], como_dice="", referencias="el enclave Corredor Peruano", alturas="",
      categoria=REFERENCIA, reconstruible=NO,
      por_que="«perímetro vigente» más el enclave que contiene. Ninguna calle"),
 dict(pid="R14", calles=["BOEDO AV."], como_dice="Av. Boedo", referencias="", alturas="",
      categoria=SIN_ALTURAS, reconstruible=NO,
      por_que="«el eje de Av. Boedo, con el contorno vigente»: el eje sin extensión y el contorno "
              "remitido"),
 dict(pid="R15", calles=[], como_dice="", referencias="Plaza Arenales", alturas="",
      categoria=REFERENCIA, reconstruible=NO,
      por_que="«perímetro vigente» más el núcleo en una plaza. Ninguna calle"),
 dict(pid="R16", calles=["DONADO", "HOLMBERG", "ECHEVERRIA", "LA PAMPA"],
      como_dice="Donado; Holmberg; Echeverría; La Pampa", referencias="", alturas="",
      categoria=SIN_ALTURAS, reconstruible=SI,
      por_que="dos ejes paralelos con los dos extremos escritos: «Donado y Holmberg entre "
              "Echeverría y La Pampa»"),
 dict(pid="R17", calles=["TRIUNVIRATO AV.", "MONROE AV."],
      como_dice="Av. Triunvirato; Av. Monroe", referencias="Plaza Echeverría", alturas="",
      categoria=SIN_ALTURAS, reconstruible=NO,
      por_que="dos avenidas y una plaza enumeradas, sin ninguna extensión, para un borde de "
              "446 ha"),
 dict(pid="R19", calles=["FRAGA", "DORREGO AV.", "CHARLONE", "NEWBERY, JORGE AV."],
      como_dice="Fraga; Dorrego; Charlone; Jorge Newbery", referencias="Plaza Los Andes",
      alturas="", categoria=SIN_ALTURAS, reconstruible=NO,
      por_que="«se amplía al entorno de» cuatro calles y una plaza: «entorno» no es una extensión"),
 dict(pid="R20", calles=["GARCIA DEL RIO AV.", "CABILDO AV.", "BALBIN RICARDO DR AV", "PINTO"],
      como_dice="Av. García del Río; Av. Cabildo; Av. Balbín; Pinto", referencias="",
      alturas="", categoria=SIN_ALTURAS, reconstruible=SI,
      por_que="eje, los dos extremos y el largo verificado: «de Av. Cabildo a Av. Balbín, 1.483 "
              "metros, unas quince cuadras»"),
 dict(pid="R21", calles=["BELAUSTEGUI LUIS DR", "ESCALADA DE SAN MARTIN R", "PAZ SOLDAN",
                         "ROJAS", "AVALOS", "ESPINOSA", "TERRERO"],
      como_dice="Belaustegui; Remedios de Escalada de San Martín; Paz Soldán; Rojas; Ávalos; "
                "Espinosa; Terrero",
      referencias="el límite con Villa Crespo", alturas="", categoria=SIN_ALTURAS,
      reconstruible=NO,
      por_que="«se amplía hacia» siete calles: es una dirección de crecimiento, no un contorno, y "
              "el único límite escrito es el del barrio vecino"),
 dict(pid="Z24", calles=["AVELLANEDA AV.", "NAZCA AV.", "CUENCA", "BAHIA BLANCA",
                         "GODOY RUPERTO", "VALLESE, FELIPE"],
      como_dice="Av. Avellaneda; Nazca; Cuenca; Bahía Blanca; Pasaje Ruperto Godoy; Felipe "
                "Vallese",
      referencias="", alturas="Pasaje Ruperto Godoy 700-800; Felipe Vallese 3100",
      categoria=CON_ALTURAS, reconstruible=SI,
      por_que="las tres piezas con su extensión: el corredor entre dos cortes, el pasaje por "
              "altura y el racimo por altura"),
 dict(pid="Z27", calles=["ALVAREZ JONTE AV."], como_dice="Av. Álvarez Jonte", referencias="",
      alturas="", categoria=SIN_ALTURAS, reconstruible=NO,
      por_que="«puntos dispersos con anclaje» en una avenida que la propia página dice que es el "
              "límite del barrio y no su columna interior. No hay trazado: publica el barrio"),
 dict(pid="Z28", calles=["ALVAREZ JONTE AV.", "LOPE DE VEGA AV."],
      como_dice="Av. Álvarez Jonte; Av. Lope de Vega", referencias="",
      alturas="Av. Álvarez Jonte 4400-5299", categoria=CON_ALTURAS, reconstruible=SI,
      por_que="eje con rango de alturas y el nodo del cruce. La página escribe «aproximadamente», "
              "y esa es toda la holgura"),
 dict(pid="Z31", calles=["FALCON, RAMON L.,CNEL.", "RIVADAVIA AV.", "ALBARINO", "ESCALADA AV"],
      como_dice="Bulevar Ramón L. Falcón; Av. Rivadavia; Albariños; Escalada",
      referencias="", alturas="Ramón L. Falcón 5400-5800; Av. Rivadavia 10100-10400",
      categoria=CON_ALTURAS, reconstruible=SI,
      por_que="las dos piezas por altura, y además la página documenta que el perímetro estaba "
              "escrito dos veces —por alturas y por calles de corte—, que las dos lecturas "
              "diferían en 256 m y cuál adoptó. Es el bloque mejor escrito de las 41"),
 dict(pid="Z32", calles=["SUAREZ, JOSE LEON", "FALCON, RAMON L.,CNEL.", "BOSCH, VENTURA",
                         "IBARROLA"],
      como_dice="José León Suárez; Ramón Falcón; Ventura Bosch; Ibarrola", referencias="",
      alturas="", categoria=SIN_ALTURAS, reconstruible=PARTE,
      por_que="el eje tiene los dos extremos y el largo medido —285 m—; las tres transversales "
              "están nombradas y no dice hasta dónde llegan"),
 dict(pid="Z33", calles=["DE LA TORRE, LISANDRO AV.", "DE LOS CORRALES AV",
                         "ALBERDI, JUAN BAUTISTA AV."],
      como_dice="Av. Lisandro de la Torre; Av. de los Corrales; Av. Alberdi",
      referencias="la Feria y el Mercado de Hacienda", alturas="Av. Alberdi 5501-6299",
      categoria=CRUCE, reconstruible=NO,
      por_que="para el polo da un cruce de dos avenidas y no dice hasta dónde llega —la propia "
              "página lo declara y por eso su borde es transitorio—. El único rango de alturas "
              "que escribe es el del eje comercial, que la página dice que es otro objeto"),
 dict(pid="Z35", calles=["TUCUMAN", "PASO", "RIVADAVIA AV.", "PASTEUR"],
      como_dice="Tucumán; Paso; Av. Rivadavia; Pasteur", referencias="",
      alturas="Tucumán 2379-2755; Paso 700; Av. Rivadavia 2001-2200", categoria=CON_ALTURAS,
      reconstruible=PARTE,
      por_que="el enclave y la transversal están por altura; el tramo de Av. Rivadavia también, y "
              "es el que el borde dibujado no tiene: el texto escribe más perímetro del que la "
              "geometría publica"),
 dict(pid="Z37", calles=["GUARDIA VIEJA", "BULNES", "CORRIENTES AV.", "RIVADAVIA AV.",
                         "MEDRANO AV."],
      como_dice="Guardia Vieja; Bulnes; Av. Corrientes; Rivadavia; Medrano", referencias="",
      alturas="Av. Corrientes 3500-4200; Guardia Vieja 3601 y 3602", categoria=CON_ALTURAS,
      reconstruible=PARTE,
      por_que="el corredor de Av. Corrientes tiene rango de alturas; «el núcleo de Guardia Vieja "
              "y Bulnes» y «el nodo de Rivadavia y Medrano» son dos cruces sin extensión"),
 dict(pid="Z39", calles=["OLIVERA AV.", "LACARRA AV."], como_dice="Av. Olivera; Av. Lacarra",
      referencias="el anillo del Parque Avellaneda", alturas="", categoria=SIN_ALTURAS,
      reconstruible=NO,
      por_que="el anillo de un parque se podría reconstruir por las caras del parque, pero está "
              "medido que Av. Olivera tiene 0 m de frente sobre la cara del parque: una de las "
              "dos avenidas que lo nombran no lo toca"),
 dict(pid="Z39b", calles=["CARABOBO AV.", "CASTANARES AV.", "PERON EVA AV"],
      como_dice="Av. Carabobo; Av. Castañares; Av. Eva Perón",
      referencias="Flores; el límite con Parque Chacabuco", alturas="", categoria=SIN_ALTURAS,
      reconstruible=SI,
      por_que="eje con los dos extremos y el largo en cuadras: «Av. Carabobo entre Av. "
              "Castañares y Av. Eva Perón: siete cuadras»"),
 dict(pid="Z40", calles=["CASEROS AV.", "SAENZ AV."], como_dice="Av. Caseros; Av. Sáenz",
      referencias="el Distrito Tecnológico; el Mercado de Pompeya; el Barrio Charrúa",
      alturas="", categoria=SIN_ALTURAS, reconstruible=NO,
      por_que="tres piezas y ninguna con extensión; la tercera no tiene ni siquiera una calle, y "
              "está medido que no cierra sobre el callejero"),
 dict(pid="Z41", calles=["LARRALDE, CRISOLOGO AV.", "DEL LIBERTADOR AV", "CABILDO AV.",
                         "CAMPOS SALLES", "O HIGGINS", "GRECIA", "CONGRESO AV."],
      como_dice="Crisólogo Larralde; Av. del Libertador; Av. Cabildo; Campos Salles; O'Higgins; "
                "Grecia; Av. Congreso",
      referencias="el viaducto Mitre", alturas="", categoria=SIN_ALTURAS, reconstruible=PARTE,
      por_que="la primera pieza tiene eje y los dos extremos; el corredor del viaducto y el "
              "núcleo disperso de tres calles no tienen extensión. La página publica el polígono "
              "del barrio, no esto"),
 dict(pid="Z43", calles=["ARENAL CONCEPCION", "ZAPIOLA"],
      como_dice="Concepción Arenal; Zapiola",
      referencias="el Polo Concepción; el Mercado de Pulgas", alturas="", categoria=SIN_ALTURAS,
      reconstruible=NO,
      por_que="la página abre diciendo «En revisión» y lo que escribe es una propuesta. Medido, "
              "su borde es el polígono del barrio"),
 dict(pid="Z44", calles=["ALVAREZ THOMAS AV.", "GIRIBONE", "14 DE JULIO", "CHARLONE", "BAUNESS"],
      como_dice="Av. Álvarez Thomas; Giribone; 14 de Julio; Charlone; Bauness",
      referencias="Plaza 25 de Agosto", alturas="Av. Álvarez Thomas 600-1700",
      categoria=CON_ALTURAS, reconstruible=SI,
      por_que="eje por altura y, además, la página declara la regla con la que se trazó: «las dos "
              "aceras de la avenida — veintitrés manzanas»"),
 dict(pid="Z46", calles=["FLORIDA", "JUNCAL", "ESMERALDA", "MAIPU", "PARAGUAY",
                         "ALVEAR MARCELO T DE", "CORDOBA AV."],
      como_dice="Florida; Juncal; Esmeralda; Maipú; Paraguay; M. T. de Alvear; Av. Córdoba",
      referencias="Plaza San Martín; el corredor Arroyo; Plaza Carlos Pellegrini",
      alturas="Maipú, Esmeralda, Paraguay y M. T. de Alvear 800-990", categoria=CON_ALTURAS,
      reconstruible=PARTE,
      por_que="la tercera pieza tiene calles, alturas y los dos extremos; el núcleo institucional "
              "y el corredor Arroyo van por plazas y no tienen extensión. La página publica el "
              "polígono del barrio, no esto"),
 dict(pid="Z47", calles=["DE MAYO AV.", "CALLAO AV.", "PERU", "BOLIVAR", "LIMA", "SALTA",
                         "YRIGOYEN, HIPOLITO", "ALSINA ADOLFO", "BELGRANO AV.", "DEFENSA",
                         "SOLIS", "ENTRE RIOS AV.", "INDEPENDENCIA AV."],
      como_dice="Av. de Mayo; Callao; Perú; Bolívar; Lima; Salta; H. Yrigoyen; Alsina; Av. "
                "Belgrano; Defensa; Solís; Entre Ríos; Independencia",
      referencias="",
      alturas="Av. de Mayo 500-1300; H. Yrigoyen 1199-1201; Alsina 420; Perú 86 y 302; Av. "
              "Belgrano 599 y 1144; Defensa 695; Solís 475; Av. Callao 248 y 368",
      categoria=CON_ALTURAS, reconstruible=SI,
      por_que="eje con los dos cortes, rango de alturas, «ambas aceras» y los remates uno por uno "
              "con su puerta. Es el perímetro escrito más preciso de las 41"),
 dict(pid="Z50", calles=["MONTES DE OCA MANUEL AV", "QUINQUELA MARTIN, BENITO",
                         "GARCIA, MARTIN AV."],
      como_dice="Av. Montes de Oca; Benito Quinquela Martín; Av. Martín García",
      referencias="el Centro Comercial a Cielo Abierto",
      alturas="Av. Montes de Oca 280-1702 (el corredor documentado); 301-999 (el contorno)",
      categoria=CON_ALTURAS, reconstruible=SI,
      por_que="separa el corredor documentado del contorno medido y da la altura de los dos. La "
              "cifra que le pone al contorno no es la del borde publicado, y eso va aparte"),
 dict(pid="Z51", calles=["IRIARTE GRAL AV", "VIEYTES", "CALIFORNIA"],
      como_dice="Av. Iriarte; Vieytes; California", referencias="",
      alturas="Av. Iriarte 2100-2300", categoria=CON_ALTURAS, reconstruible=PARTE,
      por_que="el tramo de Av. Iriarte va por altura; «con extensión a Vieytes y California» no "
              "dice hasta dónde. Y el bloque declara que no hay borde dibujado cuando sí lo hay"),
 dict(pid="Z52", calles=["NECOCHEA", "SUAREZ", "OLAVARRIA", "BROWN, ALTE. AV."],
      como_dice="Necochea; Av. Suárez; Olavarría; Av. Almirante Brown",
      referencias="", alturas="", categoria=SIN_ALTURAS, reconstruible=PARTE,
      por_que="la cita de la obra pública da el eje, los dos extremos y el largo —340 m—, y con "
              "eso se reconstruye el tramo. No el borde adoptado en esta edición, que se extiende "
              "sobre Av. Suárez y Olavarría: el bloque nombra las dos calles y no dice hasta "
              "dónde va sobre ellas"),
 dict(pid="Z53", calles=["DON PEDRO DE MENDOZA AV."], como_dice="Av. Don Pedro de Mendoza",
      referencias="Caminito; la Vuelta de Rocha", alturas="", categoria=SIN_ALTURAS,
      reconstruible=NO,
      por_que="«entorno de» dos referencias, sobre una avenida sin extensión"),
 dict(pid="Z54", calles=["SAENZ AV."], como_dice="Av. Sáenz",
      referencias="el Mercado de Pompeya", alturas="Av. Sáenz 790; 790-1399",
      categoria=CON_ALTURAS, reconstruible=SI,
      por_que="eje por altura, con el núcleo en una puerta concreta: «Av. Sáenz entre el 790 y el "
              "1399»"),
]


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.path.insert(0, str(BARRIDO / "ronda_17"))
    from cierre_geometrico import Callejero  # noqa: E402

    filas_doc = {pid: (nombre, titulo, texto) for pid, nombre, titulo, texto in paginas()}
    decl = {d["pid"]: d for d in D}
    if set(decl) != set(filas_doc):
        raise SystemExit(f"la declaración y el documento no cubren los mismos polos. "
                         f"Sólo en la declaración: {sorted(set(decl) - set(filas_doc))}. "
                         f"Sólo en el documento: {sorted(set(filas_doc) - set(decl))}.")

    cj = Callejero()
    bordes = gpd.read_file(BORDES).to_crs(CRS_M).set_index("polo_id")

    base = pd.read_csv(BASE)
    base = base[(base.anillo == "nucleo") & (base.apto_geometria.astype(str).str.lower()
                                             .isin(["true", "1", "si", "sí"]))]
    pts = gpd.GeoSeries([Point(x, y) for x, y in zip(base.lon, base.lat)],
                        crs=CRS_G).to_crs(CRS_M)

    print("=" * 98)
    print("EL PERÍMETRO ESCRITO DE LAS 41 PÁGINAS")
    print("=" * 98 + "\n")

    filas = []
    for pid in sorted(decl, key=lambda x: (x[0], int("".join(c for c in x[1:] if c.isdigit())),
                                           x)):
        d = decl[pid]
        nombre, titulo, texto = filas_doc[pid]
        borde = bordes.geometry.loc[pid]

        # cada nombre declarado, resuelto contra el callejero. Si uno no resuelve, corta.
        tocan = 0
        detalle_calles = []
        for calle in d["calles"]:
            eje = cj.eje_completo(calle)   # levanta SystemExit si el nombre no resuelve
            dist = eje.distance(borde)
            if dist <= 1.0:
                tocan += 1
            detalle_calles.append((calle, dist))

        n_loc = int(pts.within(borde).sum())
        fila = dict(
            polo=f"{pid} · {nombre}",
            polo_id=pid,
            texto_del_perimetro=" ".join(texto.split()),
            calles_nombradas=d["como_dice"],
            n_calles_nombradas=len(d["calles"]),
            calles_que_tocan_el_borde=tocan,
            tiene_alturas="si" if d["alturas"] else "no",
            alturas_que_escribe=d["alturas"],
            categoria=d["categoria"],
            reconstruible_desde_el_texto=d["reconstruible"],
            por_que=d["por_que"],
            referencias_que_no_son_calles=d["referencias"],
            ha_del_borde=round(borde.area / 10_000, 2),
            locales_del_borde=n_loc,
            calles_en_el_callejero="; ".join(c for c, _ in detalle_calles),
        )
        filas.append(fila)

        print("-" * 98)
        print(f"{pid} · {nombre}")
        print(f"    categoría   {d['categoria']}")
        print(f"    calles      {d['como_dice'] or '(ninguna)'}"
              + (f"   ·  {tocan} de {len(d['calles'])} tocan el borde dibujado"
                 if d["calles"] else ""))
        if d["alturas"]:
            print(f"    alturas     {d['alturas']}")
        if d["referencias"]:
            print(f"    referencias {d['referencias']}")
        print(f"    reconstruible: {d['reconstruible'].upper()} — {d['por_que']}")

    # ------------------------------------------------------------------ el cuadro
    df = pd.DataFrame(filas)
    print("\n" + "=" * 98)
    print("EL CUADRO")
    print("=" * 98)
    print("\n  por categoría:")
    for cat in (CON_ALTURAS, SIN_ALTURAS, CRUCE, REFERENCIA, NADA):
        sub = df[df.categoria == cat]
        print(f"    {cat:<42} {len(sub):>3} de 41   "
              f"{', '.join(sub.polo_id)}" if len(sub) else f"    {cat:<42}   0 de 41")
    print("\n  ¿se reconstruye el borde desde el texto?")
    for v in (SI, PARTE, NO):
        sub = df[df.reconstruible_desde_el_texto == v]
        print(f"    {v:<10} {len(sub):>3} de 41   {', '.join(sub.polo_id)}")
    con = df[df.tiene_alturas == "si"]
    print(f"\n  páginas con alturas: {len(con)} de 41")
    print(f"  páginas sin ninguna calle escrita: "
          f"{int((df.n_calles_nombradas == 0).sum())} de 41   "
          f"{', '.join(df[df.n_calles_nombradas == 0].polo_id)}")
    hay = df[df.n_calles_nombradas > 0]
    print(f"  calles nombradas en total: {int(df.n_calles_nombradas.sum())}, de las que "
          f"{int(df.calles_que_tocan_el_borde.sum())} tocan el borde de su página")
    sueltas = hay[hay.calles_que_tocan_el_borde < hay.n_calles_nombradas]
    print(f"  páginas con alguna calle nombrada que NO toca su borde: {len(sueltas)}")
    for r in sueltas.itertuples():
        print(f"      {r.polo_id:<6} {r.calles_que_tocan_el_borde} de "
              f"{r.n_calles_nombradas}")

    campos = ["polo", "texto_del_perimetro", "calles_nombradas", "tiene_alturas", "categoria",
              "reconstruible_desde_el_texto", "polo_id", "n_calles_nombradas",
              "calles_que_tocan_el_borde", "alturas_que_escribe", "por_que",
              "referencias_que_no_son_calles", "ha_del_borde", "locales_del_borde",
              "calles_en_el_callejero"]
    with (SALIDA / "perimetro_escrito_41.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=campos)
        w.writeheader()
        for f in filas:
            w.writerow({k: f[k] for k in campos})

    (SALIDA / "perimetro_escrito_resumen.json").write_text(json.dumps(dict(
        fecha=HOY, paginas=len(filas),
        por_categoria={cat: sorted(df[df.categoria == cat].polo_id)
                       for cat in (CON_ALTURAS, SIN_ALTURAS, CRUCE, REFERENCIA, NADA)},
        reconstruible={v: sorted(df[df.reconstruible_desde_el_texto == v].polo_id)
                       for v in (SI, PARTE, NO)},
        con_alturas=len(con),
        sin_ninguna_calle=int((df.n_calles_nombradas == 0).sum()),
        calles_nombradas=int(df.n_calles_nombradas.sum()),
        calles_que_tocan_su_borde=int(df.calles_que_tocan_el_borde.sum()),
    ), ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\nEscrito: perimetro_escrito_41.csv ({len(filas)} filas) · "
          f"perimetro_escrito_resumen.json")


if __name__ == "__main__":
    main()
