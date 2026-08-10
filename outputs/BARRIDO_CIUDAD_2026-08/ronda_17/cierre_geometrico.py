# -*- coding: utf-8 -*-
"""Cierre geométrico: los siete perímetros que faltaban y los cuatro que estaban a medias.

QUÉ CIERRA ESTA CORRIDA Y QUÉ NO
---------------------------------
La ronda anterior dejó los dieciocho polos sin borde repartidos en 7 cerrados, 4 parciales y 7
sin trazar, y dejó medido —sin adoptar— el candidato de casi cada hueco. Acá se adoptan los que
el texto de la ficha sostiene y se declaran, con su medición, los que no.

La regla es la misma de la ronda anterior y no se relaja: **una pieza cierra sólo si el texto de
la ficha le da extensión medible sobre el callejero.** Lo que cambia es de dónde se lee la
extensión: no sólo de la frase del perímetro, sino de **cualquier parte de la misma ficha** —el
párrafo de contexto comercial, la altura de puerta de un referente— siempre que la salida declare
de qué frase salió. Esa procedencia va en `fuente_del_perimetro` de cada fila, y es lo que separa
esto de inventar una traza.

DOS COSAS QUE ESTA CORRIDA MIDE Y CONTRADICEN LO ESCRITO
--------------------------------------------------------
  - **Av. Olivera no bordea el Parque Avellaneda.** Tiene 0 m de frente sobre la cara del parque;
    los 911 m son de Av. Lacarra y los 614 m de Av. Directorio, que la ficha no nombra. El anillo
    existe y se puede trazar; la avenida que lo nombra está mal.
  - **Baek-ku no está dentro de Parque Avellaneda.** El documento dice que dos de las 41 fichas
    son subzonas dentro de otra y por eso los objetos disjuntos serían 39. Medido, Baek-ku queda
    **100 % fuera de los otros cuarenta** —sus 348.613 m² enteros— y el Parque Avellaneda, que
    supuestamente lo contiene, está a 1.912 m. El eje Sáenz sí está adentro de Pompeya —0 m²
    fuera—. Los objetos disjuntos son **40**, no 39.

TRAMPAS QUE LAS RONDAS ANTERIORES DEJARON ANOTADAS Y QUE ACÁ SE RESPETAN
------------------------------------------------------------------------
  - Se mide en EPSG:5347 y se guarda en EPSG:4326. Nunca se mide en 4326.
  - **La contención se verifica por superficie perdida, no por predicado.** `covers()` devuelve
    False en casos que sí contienen. Cada polígono nuevo se mide contra su provisorio y contra
    cada vecino con `B.difference(A).area`, y ese número se publica.
  - `buffer(0)` antes de cada operación booleana.
  - El frente de una manzana sobre el tramo se mide por intersección exacta de borde contra eje.
  - Un nombre de calle que no resuelve **corta la corrida**. La ronda 15 escribió «Albariños»,
    el callejero lo tiene como ALBARINO y el control se salteó en silencio.

Cero requests. Se ejecuta con .venv/Scripts/python.exe.
"""

import csv
import json
import sys
from datetime import date
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.ops import polygonize, unary_union

sys.path.insert(0, str(Path(__file__).resolve().parent))
from nombres_de_barrio import clave as clave_barrio  # noqa: E402

BASE = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[3]
SALIDA = Path(__file__).resolve().parent
CRS_METRICO = "EPSG:5347"
CRS_SALIDA = "EPSG:4326"

ZONAS_R8 = BASE / "geometria_r7" / "zonas_r8.geojson"
SOPORTES_41 = BASE / "ronda_16_codex" / "geometria" / "soportes_41.geojson"
PUBLICABLES = BASE / "borrador_polos" / "polos_publicables.geojson"
BARRIOS_OFICIAL = BASE / "insumos" / "caba_barrios.geojson"
BARRIOS_VIEJA = ROOT / "data" / "raw" / "geo_barrios.geojson"
MAGNITUDES = BASE / "desde_cowork" / "evidencia_2026" / "magnitudes_sin_perimetro.csv"

FRENTE_MIN_M = 20.0
FRENTE_SENSIBILIDAD = (10.0, 20.0, 40.0)
HOY = date.today().isoformat()


def limpia(g):
    return g if g.is_valid else g.buffer(0)


# --------------------------------------------------------------------------------------------
# LAS RECETAS
#
# `piezas`      lo que se adopta, con la frase de la ficha de la que sale la extensión.
# `sin_cerrar`  lo que la ficha nombra y no alcanza a cerrar, con el motivo.
# `lecturas`    lo que se mide y NO se adopta, con el motivo de por qué no.
# `referentes`  las puertas que la propia ficha lista. Es la prueba que decide si el polígono
#               describe al polo o al instrumento, y es la lección de Almagro.
# --------------------------------------------------------------------------------------------

RECETAS = [
    # ---------------------------------------------------------------- TAREA 1 · los siete
    dict(
        zona="Z40", nombre="Nueva Pompeya y Parque Patricios", tarea=1, provisorio="Z40",
        fuente=("Tres piezas: Av. Caseros y el Distrito Tecnológico, Av. Sáenz y el Mercado de "
                "Pompeya, y el Barrio Charrúa. Las dos extensiones salen de la misma ficha: el "
                "párrafo de contexto comercial da «Av. Caseros 2601-2999» y «Av. Sáenz del 801 "
                "al 1399», y los referentes dan El Globito en Av. Caseros 3159 y el Mercado de "
                "Pompeya en Av. Sáenz 790."),
        piezas=[
            dict(nombre="Av. Caseros y el Distrito Tecnológico", tipo="eje_por_altura",
                 calle="CASEROS AV.", desde=2601, hasta=3199,
                 de_donde="eje relevado 2601-2999 de la ficha, extendido a El Globito (3159)"),
            dict(nombre="Av. Sáenz y el Mercado de Pompeya", tipo="eje_por_altura",
                 calle="SAENZ AV.", desde=790, hasta=1399,
                 de_donde="Mercado de Pompeya (790) y eje relevado 801-1399 de la ficha"),
        ],
        sin_cerrar=[("Barrio Charrúa",
                     "medido y no cierra: las vías del Belgrano Sur no son una línea del "
                     "callejero y Av. Bonorino y Av. Fernández de la Cruz se cruzan; con el "
                     "borde del barrio como tercer lado la cara que sale es Nueva Pompeya "
                     "entera. Y la propia ficha declara que ahí no hay oferta comercial "
                     "documentada -«comunidad medida, sin enclave comercial»-, así que sumarlo "
                     "agregaría superficie sin locales")],
        lecturas=[dict(nombre="La Rioja 1901-2199, la otra mitad del eje relevado de Parque "
                              "Patricios", tipo="eje_por_altura", calle="LA RIOJA",
                       desde=1901, hasta=2199,
                       porque="el perímetro escrito nombra Av. Caseros, no La Rioja")],
        referentes=[("El Buzón", "ESQUIU", 1393), ("El Globito", "CASEROS AV.", 3159),
                    ("Mercado de Pompeya", "SAENZ AV.", 790)],
        veredicto="si_con_exclusion_declarada",
        veredicto_porque=("cierran las dos piezas que tienen oferta. La tercera está medida y "
                          "no cierra, y la propia ficha declara que no tiene establecimientos: "
                          "sumarla agregaría superficie con cero locales. No es una pieza que "
                          "falta, es una pieza que se excluye con motivo escrito"),
    ),
    dict(
        zona="Z54", nombre="Nueva Pompeya · eje Av. Sáenz", tarea=1, provisorio="Z40",
        subzona_de="Z40",
        fuente=("Eje Av. Sáenz, con núcleo en el Mercado de Pompeya, Av. Sáenz 790. Es la misma "
                "pieza que el perímetro de Nueva Pompeya y Parque Patricios ya lista como su "
                "segunda: mismo eje, mismo objeto, misma dirección."),
        piezas=[dict(nombre="eje Av. Sáenz", tipo="eje_por_altura", calle="SAENZ AV.",
                     desde=790, hasta=1399,
                     de_donde="Mercado de Pompeya (790) y eje relevado 801-1399 de la ficha")],
        sin_cerrar=[],
        referentes=[("Mercado de Pompeya", "SAENZ AV.", 790),
                    ("Peña Los Amigos / El Chino", "BEAZLEY", 3566)],
    ),
    dict(
        zona="Z35", nombre="Balvanera · Once", tarea=1, provisorio="Z35",
        fuente=("Eje Tucumán entre el 2379 y el 2755, ambas aceras, con transversal sobre Paso "
                "al 700. La frase del perímetro dice «en revisión» y no escribe ninguna calle; "
                "la extensión sale de las cinco puertas del enclave que la propia ficha lista, "
                "todas del padrón oficial de 2015: Sucat David (Tucumán 2379), El Jaial (2620), "
                "Al Galope (2633), Lalo Helueni (2755) y Yaffo Kosher (Paso 747)."),
        piezas=[
            dict(nombre="eje Tucumán 2379-2755", tipo="eje_por_altura", calle="TUCUMAN",
                 desde=2379, hasta=2755, de_donde="las cuatro puertas de Tucumán de la ficha"),
            dict(nombre="transversal Paso al 700", tipo="eje_por_altura", calle="PASO",
                 desde=700, hasta=799, de_donde="Yaffo Kosher, Paso 747"),
        ],
        sin_cerrar=[],
        referentes=[("Sucat David", "TUCUMAN", 2379), ("El Jaial", "TUCUMAN", 2620),
                    ("Al Galope", "TUCUMAN", 2633), ("Lalo Helueni", "TUCUMAN", 2755),
                    ("Yaffo Kosher", "PASO", 747),
                    ("Café de los Angelitos", "RIVADAVIA AV.", 2100)],
        aviso=("el padrón del que salen las cinco puertas es de 2015 y la ficha lo declara "
               "dudoso en bloque; el eje delimita el enclave de colectividad, no la zona entera"),
    ),
    dict(
        zona="Z33", nombre="Mataderos", tarea=1, provisorio="Z33",
        fuente=("Dos piezas separadas por más de un kilómetro: la Feria y el Mercado de "
                "Hacienda, en Av. Lisandro de la Torre y Av. de los Corrales, y un conjunto de "
                "referentes dispersos."),
        piezas=[],
        sin_cerrar=[
            ("la Feria y el Mercado de Hacienda",
             "el texto da el cruce de dos avenidas y ninguna extensión. El perímetro de "
             "ocupación de la Feria es un dato administrativo que existe fuera del atlas y el "
             "repositorio no lo tiene"),
            ("el conjunto de referentes dispersos",
             "el texto los llama dispersos y la propia ficha dice que «una densidad promedio "
             "sobre el conjunto no describe ninguna de las dos» piezas"),
        ],
        lecturas=[dict(nombre="el eje comercial que releva la Ciudad, Av. Alberdi 5501-6299",
                       tipo="eje_por_altura", calle="ALBERDI, JUAN BAUTISTA AV.",
                       desde=5501, hasta=6299,
                       porque="es el eje del IDECBA, no el perímetro del polo, y adoptarlo "
                              "sería atribuirle al polo el objeto de otra fuente. Contiene un "
                              "solo referente de los cuatro -El Cedrón, Alberdi 6101- y deja "
                              "afuera la pieza de la Feria, que es la primera del perímetro")],
        referentes=[("Bar Oviedo", "DE LA TORRE, LISANDRO AV.", 2407),
                    ("Bar del Glorias", "ANDALGALA", 1982),
                    ("9 de Julio", "LARRAZABAL", 1276),
                    ("El Cedrón", "ALBERDI, JUAN BAUTISTA AV.", 6101)],
    ),
    dict(
        zona="Z39", nombre="Parque Avellaneda", tarea=1, provisorio="Z39",
        fuente=("El anillo del Parque Avellaneda. El anillo son las manzanas con frente sobre "
                "el perímetro del parque, que es una cara cerrada del callejero y no necesita "
                "rango de alturas. La ficha nombra Av. Olivera y Av. Lacarra; medido, Olivera "
                "tiene 0 m de frente sobre el parque."),
        piezas=[dict(nombre="el anillo del parque, con el parque adentro", tipo="anillo_de_cara",
                     calles_del_anillo=["LACARRA AV.", "DIRECTORIO AV."],
                     de_donde="la cara cerrada del Parque Avellaneda en el callejero")],
        sin_cerrar=[],
        lecturas=[dict(nombre="corredor en L por las alturas de los tres referentes",
                       tipo="eje_por_altura", calle="LACARRA AV.", desde=836, hasta=1500,
                       porque="delimitar por dónde están los referentes no es delimitar por el "
                              "perímetro, y los tres referentes están dudosos")],
        referentes=[("La Barra del Parque", "LACARRA AV.", 836),
                    ("De Flores Café", "LACARRA AV.", 1500),
                    ("Viejo Mercado", "OLIVERA AV.", 1557)],
        aviso=("buena parte de la superficie encerrada es el parque, donde no hay locales: la "
               "densidad por hectárea de esta zona no es comparable con la de las demás"),
    ),
    dict(
        zona="Z27", nombre="Villa Santa Rita", tarea=1, provisorio="Z27",
        fuente=("Puntos dispersos con anclaje en Av. Álvarez Jonte, que es el límite sur y "
                "oeste del barrio y no su columna interior."),
        piezas=[],
        sin_cerrar=[("el conjunto",
                     "no hay rango de alturas ni calles de corte, y el hueco no es de "
                     "redacción: la propia ficha declara que la vía de densidad no abre "
                     "-«seis locales dispersos en diez cuadras es un conjunto, no una "
                     "densidad»-, así que todavía no hay una concentración que delimitar. Los "
                     "tres referentes están en tres calles distintas -Av. Álvarez Jonte 3550, "
                     "Camarones 2702 y Luis Viale 2867- y ninguna trae extensión")],
        referentes=[("El Tokio", "ALVAREZ JONTE AV.", 3550), ("Bar Don Juan", "CAMARONES", 2702),
                    ("El Sol de Galicia", "VIALE, LUIS", 2867)],
    ),
    dict(
        zona="Z53", nombre="La Boca · Caminito y Vuelta de Rocha", tarea=1, provisorio="S_LABOCA",
        fuente=("Entorno de Caminito y la Vuelta de Rocha, sobre Av. Don Pedro de Mendoza. "
                "De las dos cosas que el texto nombra, Caminito sí está en el callejero -140,6 "
                "m- y toca la avenida a 0 m: sus manzanas frentistas cierran. La Vuelta de Rocha "
                "no está, y el texto no da tramo sobre la avenida."),
        piezas=[dict(nombre="entorno de Caminito", tipo="eje_completo", calle="CAMINITO",
                     de_donde="Caminito entero, 140,6 m, es una calle del callejero")],
        sin_cerrar=[("la Vuelta de Rocha",
                     "no está en el callejero porque es un recodo del Riachuelo, no una calle, "
                     "y el texto no da tramo sobre Av. Don Pedro de Mendoza")],
        lecturas=[dict(nombre="la cara de ribera contigua, cerrada por la avenida y el límite "
                              "oficial del barrio", tipo="cara_de_ribera",
                       porque="cierra con objetos auditables -la avenida y el límite oficial del "
                              "barrio, con procedencia y sha256-, pero mide 3,30 ha con 0 "
                              "locales: agregaría superficie sin oferta, que es el mismo motivo "
                              "por el que el Barrio Charrúa queda afuera de Pompeya"),
                  dict(nombre="Caminito más las dos cuadras de Av. Don Pedro de Mendoza que "
                              "toca, 1871-1939", tipo="union_de_dos",
                       calle_a="CAMINITO", calle_b="DON PEDRO DE MENDOZA AV.",
                       desde=1871, hasta=1939,
                       porque="es el candidato más barato de todo el conjunto y mide 4,15 ha con "
                              "37 locales, y sí contiene La Perla de Caminito. NO se adopta "
                              "porque las dos cuadras las elige esta corrida y no la ficha: es "
                              "una línea de redacción, y quien escribe la ficha la firma o la "
                              "cambia")],
        referentes=[("La Perla de Caminito", "DON PEDRO DE MENDOZA AV.", 1899),
                    ("El Obrero", "CAFFARENA, AGUSTIN R.", 64), ("Genovés", "BRANDSEN", 923)],
        veredicto_porque=("cierra Caminito y no cierra la avenida, así que queda PARCIAL, y la "
                          "medición es la que lo decide: el polígono de Caminito solo **no "
                          "contiene ninguno de los tres referentes de su ficha**, y La Perla de "
                          "Caminito -Av. Don Pedro de Mendoza 1899, el ancla de la zona- queda a "
                          "26 m afuera. Un polígono que deja afuera al establecimiento sobre el "
                          "que su ficha se apoya no es el polígono de esa ficha. Lo que falta es "
                          "una línea: el tramo de la avenida"),
    ),

    # ---------------------------------------------------------------- TAREA 2 · los cuatro
    dict(
        zona="Z41", nombre="Núñez", tarea=2, provisorio="Z41",
        cierra_por_capa_administrativa="Nunez",
        fuente=("El polígono administrativo del barrio de Núñez, de la capa oficial de 48 "
                "barrios. La zona que el atlas publica es idéntica a la capa de barrios que "
                "venía usando -diferencia simétrica 0 m²-: el atlas no sumó superficie. Toda la "
                "diferencia contra la capa oficial está sobre la línea de ribera del Río de la "
                "Plata y no lleva locales."),
        piezas=[dict(nombre="corredor de Crisólogo Larralde, entre Av. del Libertador y Av. "
                            "Cabildo", tipo="eje_entre", calle="LARRALDE, CRISOLOGO AV.",
                     corte_a="DEL LIBERTADOR AV.", corte_b="CABILDO AV.",
                     de_donde="la primera pieza del perímetro escrito")],
        sin_cerrar=[("corredor bajo el viaducto Mitre",
                     "sigue sin extensión y sin reparto con las otras dos zonas que lo "
                     "comparten; el único dibujo que existe es un buffer de 150 m sobre una "
                     "recta entre cabeceras, y ese borde es una propiedad del instrumento"),
                    ("núcleo de bistrós en Campos Salles, O'Higgins y Grecia",
                     "tres calles sin extensión, y el texto las llama dispersas")],
        referentes=[("La Escuela", "PEDRAZA, MANUELA", 2803), ("Ness", "GRECIA", 3691),
                    ("Evelia", "CAMPOS SALLES", 1712)],
        veredicto="si_por_capa_administrativa",
        veredicto_porque=("la geometría que la zona publica es el polígono del barrio y la "
                          "medición dice que está bien: el atlas no le sumó nada. Las dos "
                          "piezas del perímetro escrito que no cierran siguen sin cerrar, y "
                          "eso se declara: la cifra publicada es la del barrio, no la del polo"),
    ),
    dict(
        zona="Z46", nombre="Retiro", tarea=2, provisorio="Z46",
        cierra_por_capa_administrativa="Retiro",
        suma_declarada=("Z46_SUBZONA_CLUSTER_COREANO",
                        "el cluster coreano y asiático, que la propia ficha declara: cae 100 % "
                        "en San Nicolás, fuera del barrio de Retiro"),
        fuente=("El polígono administrativo del barrio de Retiro, de la capa oficial de 48 "
                "barrios, más la subzona del cluster coreano y asiático, que la ficha ya "
                "declara y que cae íntegramente en San Nicolás."),
        piezas=[
            dict(nombre="cluster coreano y asiático", tipo="ejes_por_altura",
                 calles=["MAIPU", "ESMERALDA", "PARAGUAY", "ALVEAR, MARCELO T. DE"],
                 desde=800, hasta=990, de_donde="la tercera pieza del perímetro escrito"),
            dict(nombre="corredor Arroyo", tipo="eje_entre", calle="ARROYO",
                 corte_a="JUNCAL", corte_b="PELLEGRINI, CARLOS",
                 de_donde="la segunda pieza del perímetro escrito"),
        ],
        sin_cerrar=[("núcleo institucional de Plaza San Martín y Florida",
                     "el texto no da el tramo de Florida, que entera mide más de un kilómetro")],
        lecturas=[dict(nombre="Florida 800-1005, acotada por sus dos Notables",
                       tipo="eje_por_altura", calle="FLORIDA", desde=800, hasta=1005,
                       porque="las alturas salen de Florida Garden (899) y Plaza Bar (1005), "
                              "que son referentes y no bordes")],
        referentes=[("Florida Garden", "FLORIDA", 899), ("Plaza Bar", "FLORIDA", 1005),
                    ("Bárbaro", "TRES SARGENTOS", 415),
                    ("Confitería Saint Moritz", "ESMERALDA", 894), ("Tancat", "PARAGUAY", 645),
                    ("Florería Atlántico", "ARROYO", 872),
                    ("Centro Cultural Coreano", "MAIPU", 972)],
        veredicto="si_por_capa_administrativa",
        veredicto_porque=("la zona sí suma superficie sobre el barrio, y lo que suma es "
                          "exactamente el cluster coreano que su ficha ya declara. La pieza "
                          "del núcleo institucional sigue sin tramo escrito"),
    ),
    dict(
        zona="Z37", nombre="Almagro", tarea=2, provisorio="Z37",
        fuente=("Tres ejes: Guardia Vieja 3600-3900, Av. Corrientes 3500-4200 y Av. Rivadavia "
                "3401-4099. Las tres cuadras de Guardia Vieja son las que contienen las dos "
                "alturas que la ficha nombra -el 3601 y el 3602- y llegan al cruce con Bulnes, "
                "que es lo que da nombre a la pieza; medido, Bulnes cruza Guardia Vieja al "
                "3800, no al 3601. La extensión sobre Rivadavia es el eje que la ficha releva "
                "-Av. Rivadavia 3401-4099-, que contiene Las Violetas en el 3899."),
        piezas=[
            dict(nombre="núcleo de Guardia Vieja y Bulnes", tipo="eje_por_altura",
                 calle="GUARDIA VIEJA", desde=3600, hasta=3900,
                 de_donde="las alturas 3601 y 3602 de la ficha y el cruce con Bulnes"),
            dict(nombre="corredor de Av. Corrientes 3500-4200", tipo="eje_por_altura",
                 calle="CORRIENTES AV.", desde=3500, hasta=4200,
                 de_donde="la segunda pieza del perímetro escrito"),
            dict(nombre="nodo de Rivadavia y Medrano", tipo="eje_por_altura",
                 calle="RIVADAVIA AV.", desde=3401, hasta=4099,
                 de_donde="el eje Almagro que releva la Ciudad, con Las Violetas en el 3899"),
        ],
        sin_cerrar=[],
        lecturas=[dict(nombre="Guardia Vieja 3500-3800, la lectura de la ronda anterior",
                       tipo="eje_por_altura", calle="GUARDIA VIEJA", desde=3500, hasta=3800,
                       porque="es el único tramo de tres cuadras que contiene el 3601 y NO "
                              "llega al cruce con Bulnes que da nombre a la pieza")],
        referentes=[("El Banderín", "GUARDIA VIEJA", 3601), ("El Boliche de Roberto", "BULNES", 331),
                    ("El Símbolo", "CORRIENTES AV.", 3787), ("La Orquídea", "CORRIENTES AV.", 4101),
                    ("Las Violetas", "RIVADAVIA AV.", 3899)],
        contra=["R13"],
        aviso=("el corredor de Av. Corrientes se pisa con el Abasto y el reparto sigue siendo "
               "una decisión abierta: la cifra de esta zona no se suma con la del Abasto"),
    ),
    dict(
        zona="Z44", nombre="Villa Ortúzar", tarea=2, provisorio="Z44",
        dos_opciones=True,
        fuente=("Av. Álvarez Thomas, tramo 600-1700. La avenida es el límite del barrio en la "
                "mayor parte del tramo, así que hay dos lecturas posibles y las dos están "
                "medidas: una sola acera -las manzanas cuyo barrio dominante es Villa Ortúzar- "
                "o las dos aceras con el reparto declarado."),
        piezas=[dict(nombre="corredor Av. Álvarez Thomas 600-1700", tipo="eje_por_altura",
                     calle="ALVAREZ THOMAS AV.", desde=600, hasta=1700,
                     de_donde="la primera pieza del perímetro escrito")],
        sin_cerrar=[("núcleo secundario de Plaza 25 de Agosto",
                     "medido y no cierra: las cuatro calles no encierran ninguna cara; el par "
                     "más separado, Charlone y Bauness, queda a 784 m")],
        referentes=[("La Mezzetta", "ALVAREZ THOMAS AV.", 1321), ("Simona", "ALVAREZ THOMAS AV.", 661),
                    ("Cullen Henderson", "ALVAREZ THOMAS AV.", 1106),
                    ("Kopem", "ALVAREZ THOMAS AV.", 1700),
                    ("Cervecería Charlone", "FREIRE, RAMON, CAP. GRAL.", 745), ("Gallo Negro", "DONADO", 1851),
                    ("F4 Esquina", "ROSETI", 1596), ("Tía Meche", "BAUNESS", 1302),
                    ("Cantina y Teatro Tai", "CHARLONE", 1752), ("Suculentas", "HEREDIA", 499),
                    ("Curva", "CALDAS", 1596)],
        veredicto="dos_opciones_medidas",
        veredicto_porque=("la decisión de borde es editorial y no se toma acá: las dos "
                          "lecturas están medidas y la ficha elige"),
        recomendacion=("una sola acera. El corredor de dos aceras deja el 69 % de su "
                       "superficie fuera de Villa Ortúzar y se pisa con tres polos ya "
                       "publicados; el de una acera no se pisa con ninguno."),
    ),
]


# --------------------------------------------------------------------------------------- capa


class Callejero:
    def __init__(self):
        sys.path.insert(0, str(ROOT / "scripts" / "barrido_ciudad"))
        from callejero_canonico import cargar, familias, eje_canonico  # noqa: E402
        from polos_soporte import puntos_base, sin_tildes, _punto_de_cruce, _tramo_entre  # noqa

        self._eje_canonico, self._sin_tildes = eje_canonico, sin_tildes
        self._punto_de_cruce, self._tramo_entre = _punto_de_cruce, _tramo_entre
        self.calles = cargar()
        self.familias = familias(self.calles)
        self.puntos = puntos_base()

        oficial = gpd.read_file(BARRIOS_OFICIAL).to_crs(CRS_METRICO)
        self.barrios_oficial = oficial.rename(columns={"BARRIO": "nombre"})[["nombre", "geometry"]]
        vieja = gpd.read_file(BARRIOS_VIEJA).to_crs(CRS_METRICO)
        col = "nombre" if "nombre" in vieja.columns else vieja.columns[0]
        self.barrios_vieja = vieja.rename(columns={col: "nombre"})[["nombre", "geometry"]]

        caras = [limpia(p) for p in polygonize(unary_union(list(self.calles.geometry)))]
        self.manzanas = gpd.GeoSeries(caras, crs=CRS_METRICO)
        self._sidx = self.manzanas.sindex
        print(f"callejero: {len(self.calles):,} segmentos -> {len(self.manzanas):,} caras "
              f"cerradas (manzanas)")
        print(f"base: {len(self.puntos):,} locales del universo anillo=nucleo & apto_geometria")
        print(f"barrios: capa oficial {len(self.barrios_oficial)} · capa vieja "
              f"{len(self.barrios_vieja)}\n")

    def barrio(self, nombre, oficial=True):
        """El polígono de un barrio, buscado por clave normalizada y no por `==`.

        Con `==` este mismo script perdió Núñez en su primera corrida: la capa oficial lo escribe
        NUÑEZ y la receta decía Nunez. Devolvió un polígono vacío, midió 0,00 ha y siguió. Es
        exactamente la falla que el normalizador viene a levantar, así que acá **falla fuerte**.
        """
        capa = self.barrios_oficial if oficial else self.barrios_vieja
        sub = capa[capa.nombre.map(clave_barrio) == clave_barrio(nombre)]
        if sub.empty:
            cual = "oficial" if oficial else "vieja"
            raise SystemExit(f"«{nombre}» (clave {clave_barrio(nombre)}) no está en la capa "
                             f"{cual} de barrios. No se sigue con un polígono vacío.")
        return limpia(unary_union(list(sub.geometry)))

    # --- resolución de nombres --------------------------------------------------------------
    def segmentos(self, nombre):
        clave = self._sin_tildes(nombre)
        sub = self.calles[self.calles.clave.isin(self.familias.get(clave, {clave}))]
        if sub.empty:
            raise SystemExit(f"«{nombre}» ({clave}) no está en el callejero: la receta lo nombra "
                             f"y no se puede resolver. No se sigue con un tramo de menos.")
        return sub

    def eje(self, nombre):
        return self._eje_canonico(self.calles, nombre, self.familias)

    # --- tramos -----------------------------------------------------------------------------
    def tramo_por_altura(self, nombre, desde, hasta):
        elegidos = []
        for r in self.segmentos(nombre).itertuples():
            alturas = [v for v in (r.alt_izqini, r.alt_izqfin, r.alt_derini, r.alt_derfin)
                       if v and v > 0]
            if alturas and max(alturas) > desde and min(alturas) < hasta:
                elegidos.append(r.geometry)
        return unary_union(elegidos) if elegidos else None

    def tramo_entre(self, nombre, corte_a, corte_b):
        segmentos = self.segmentos(nombre)
        pa = self._punto_de_cruce(segmentos, self.segmentos(corte_a))
        pb = self._punto_de_cruce(segmentos, self.segmentos(corte_b))
        return self._tramo_entre(segmentos, pa, pb)

    def eje_completo(self, nombre):
        return unary_union(list(self.segmentos(nombre).geometry))

    # --- manzanas ---------------------------------------------------------------------------
    def frentistas(self, tramo, frente_min=FRENTE_MIN_M):
        salida = []
        for i in self._sidx.query(tramo.buffer(2)):
            cara = self.manzanas.iloc[i]
            largo = cara.boundary.intersection(tramo).length
            if largo >= frente_min:
                salida.append((i, largo, cara))
        return salida

    def cara_del_parque(self, calles_del_anillo):
        """La cara cerrada más grande con frente sobre las dos avenidas que la delimitan."""
        ejes = [self.eje_completo(c) for c in calles_del_anillo]
        candidatas = [m for m in self.manzanas if m.area > 20e4]
        for m in sorted(candidatas, key=lambda x: -x.area):
            frentes = [m.boundary.intersection(e).length for e in ejes]
            if all(f > 300 for f in frentes):
                return m
        return None

    def anillo_de(self, cara):
        vecinas = [self.manzanas.iloc[i] for i in self._sidx.query(cara.buffer(2))
                   if self.manzanas.iloc[i].boundary.intersection(cara.boundary).length >= 20
                   and not self.manzanas.iloc[i].equals(cara)]
        return vecinas

    def cara_de_ribera(self, barrio, avenida, cerca_de, tope_m=80):
        borde = self.barrio(barrio).boundary
        red = unary_union([borde] + [g for g in self.calles.geometry if g.intersects(borde.envelope)])
        caras = [limpia(p) for p in polygonize(red)]
        caras = [c for c in caras
                 if c.boundary.intersection(avenida).length > 50
                 and c.boundary.intersection(borde).length > 50
                 and c.distance(cerca_de) < tope_m]
        return limpia(unary_union(caras)) if caras else None

    # --- medición ---------------------------------------------------------------------------
    def punto_de_altura(self, calle, altura):
        for r in self.segmentos(calle).itertuples():
            for ini, fin in ((r.alt_izqini, r.alt_izqfin), (r.alt_derini, r.alt_derfin)):
                if ini and fin and min(ini, fin) <= altura <= max(ini, fin):
                    return r.geometry.interpolate(0.5, normalized=True)
        return None

    def locales(self, geom):
        return int(self.puntos.within(geom).sum())

    def ha(self, geom):
        return geom.area / 10_000

    def reparto_por_barrio(self, geom, capa=None, minimo=0.01):
        capa = self.barrios_oficial if capa is None else capa
        salida = []
        for r in capa.itertuples():
            inter = limpia(geom.intersection(limpia(r.geometry)))
            if inter.is_empty:
                continue
            fraccion = inter.area / geom.area
            if fraccion >= minimo:
                salida.append((r.nombre, fraccion * 100, inter.area / 10_000))
        return sorted(salida, key=lambda x: -x[1])

    def barrio_dominante(self, geom):
        mejor, area = None, 0.0
        for r in self.barrios_oficial.itertuples():
            a = limpia(geom).intersection(limpia(r.geometry)).area
            if a > area:
                mejor, area = r.nombre, a
        return mejor


def resolver(cj, pieza):
    """Devuelve (tramo, poligono, detalle) o (tramo|None, None, motivo)."""
    tipo = pieza["tipo"]
    if tipo == "eje_por_altura":
        tramo = cj.tramo_por_altura(pieza["calle"], pieza["desde"], pieza["hasta"])
        detalle = f"{pieza['calle']} {pieza['desde']}-{pieza['hasta']}"
    elif tipo == "ejes_por_altura":
        piezas = [cj.tramo_por_altura(n, pieza["desde"], pieza["hasta"]) for n in pieza["calles"]]
        faltan = [n for n, t in zip(pieza["calles"], piezas) if t is None]
        if faltan:
            return None, None, f"sin tramo en el callejero: {faltan}"
        tramo = unary_union(piezas)
        detalle = ", ".join(pieza["calles"]) + f" {pieza['desde']}-{pieza['hasta']}"
    elif tipo == "eje_entre":
        tramo = cj.tramo_entre(pieza["calle"], pieza["corte_a"], pieza["corte_b"])
        detalle = f"{pieza['calle']} entre {pieza['corte_a']} y {pieza['corte_b']}"
    elif tipo == "eje_completo":
        tramo = cj.eje_completo(pieza["calle"])
        detalle = f"{pieza['calle']} entera"
    elif tipo == "union_de_dos":
        otro = cj.tramo_por_altura(pieza["calle_b"], pieza["desde"], pieza["hasta"])
        if otro is None:
            return None, None, f"sin tramo: {pieza['calle_b']} {pieza['desde']}-{pieza['hasta']}"
        tramo = unary_union([cj.eje_completo(pieza["calle_a"]), otro])
        detalle = (f"{pieza['calle_a']} entera más {pieza['calle_b']} "
                   f"{pieza['desde']}-{pieza['hasta']}")
    elif tipo == "anillo_de_cara":
        cara = cj.cara_del_parque(pieza["calles_del_anillo"])
        if cara is None:
            return None, None, "no se encontró la cara cerrada del parque"
        anillo = cj.anillo_de(cara)
        poligono = limpia(unary_union(anillo + [cara]))
        return cara.boundary, poligono, f"anillo de {len(anillo)} manzanas frentistas del parque"
    else:
        raise SystemExit(f"tipo de pieza desconocido: {tipo}")
    if tramo is None or tramo.is_empty:
        return None, None, f"el tramo salió vacío: {detalle}"
    frentistas = cj.frentistas(tramo)
    if not frentistas:
        return tramo, None, f"ninguna manzana con frente >= {FRENTE_MIN_M:.0f} m sobre {detalle}"
    return tramo, limpia(unary_union([c for _, _, c in frentistas])), detalle


# ---------------------------------------------------------------------------------------- run


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("=" * 98)
    print("CIERRE GEOMÉTRICO · los siete que faltaban y los cuatro que estaban a medias")
    print("=" * 98 + "\n")

    cj = Callejero()
    zonas = gpd.read_file(ZONAS_R8).to_crs(CRS_METRICO).set_index("zona_id")
    soportes = gpd.read_file(SOPORTES_41).to_crs(CRS_METRICO).set_index("polo_id")
    magnitudes = pd.read_csv(MAGNITUDES).set_index("polo_id")

    filas, capa, trazados, opciones_z44 = [], [], {}, {}

    for receta in RECETAS:
        zona, nombre = receta["zona"], receta["nombre"]
        contenedor = receta.get("provisorio") or magnitudes.contenedor.get(zona)
        provisorio = limpia(zonas.geometry.loc[contenedor])
        ha_prov, loc_prov = cj.ha(provisorio), cj.locales(provisorio)

        print("=" * 98)
        print(f"{zona} · {nombre}   [tarea {receta['tarea']}]   "
              f"provisorio {contenedor}: {ha_prov:,.2f} ha, {loc_prov} locales")
        print("=" * 98)
        print(f"  perímetro adoptado: {receta['fuente']}\n")

        cerradas, notas = [], []
        for pieza in receta["piezas"]:
            tramo, poligono, detalle = resolver(cj, pieza)
            if poligono is None:
                print(f"  [NO CIERRA] {pieza['nombre']}: {detalle}")
                notas.append(f"{pieza['nombre']}: {detalle}")
                continue
            largo = tramo.length if tramo is not None else 0.0
            print(f"  [CIERRA]  {pieza['nombre']}")
            print(f"            {detalle}  ·  eje {largo:,.0f} m  ->  "
                  f"{cj.ha(poligono):,.2f} ha, {cj.locales(poligono)} locales")
            print(f"            de dónde sale la extensión: {pieza['de_donde']}")
            cerradas.append((pieza["nombre"], detalle, tramo, poligono, pieza["de_donde"]))

        for nom, motivo in receta.get("sin_cerrar", []):
            print(f"  [NO CIERRA] {nom}: {motivo}")

        union = limpia(unary_union([p for _, _, _, p, _ in cerradas])) if cerradas else None

        # ---- cierre por capa administrativa (Núñez y Retiro) -------------------------------
        if receta.get("cierra_por_capa_administrativa"):
            bnom = receta["cierra_por_capa_administrativa"]
            of = cj.barrio(bnom, oficial=True)
            vi = cj.barrio(bnom, oficial=False)
            print(f"\n  cierre por capa administrativa · barrio {bnom}")
            print(f"    la zona publicada menos la capa VIEJA:    "
                  f"{provisorio.difference(vi).area:12,.0f} m²  ·  "
                  f"{cj.locales(limpia(provisorio.difference(vi)))} locales")
            print(f"    la zona publicada menos la capa OFICIAL:  "
                  f"{provisorio.difference(of).area:12,.0f} m²  ·  "
                  f"{cj.locales(limpia(provisorio.difference(of)))} locales")
            print(f"    la capa OFICIAL menos la zona publicada:  "
                  f"{of.difference(provisorio).area:12,.0f} m²  ·  "
                  f"{cj.locales(limpia(of.difference(provisorio)))} locales")
            notas.append(
                f"zona menos capa vieja {provisorio.difference(vi).area:,.0f} m²; zona menos "
                f"capa oficial {provisorio.difference(of).area:,.0f} m² con "
                f"{cj.locales(limpia(provisorio.difference(of)))} locales")
            if receta.get("suma_declarada"):
                sid, porque = receta["suma_declarada"]
                # Lo que la ZONA suma se mide contra la capa que el atlas venía usando. Contra
                # la oficial da 6.711 m² y un local más, y ese local no es del cluster: es la
                # diferencia entre las dos capas de barrios. Mezclarlos atribuiría al polo un
                # local que puso el cambio de capa.
                extra = limpia(provisorio.difference(vi))
                rep = cj.reparto_por_barrio(extra, capa=cj.barrios_vieja)
                print(f"    lo que la ZONA suma sobre el barrio (contra la capa vieja): "
                      f"{extra.area:,.0f} m², {cj.locales(extra)} locales · {porque}")
                print(f"      reparto por barrio: " + " · ".join(
                    f"{n} {p:.0f} %" for n, p, _ in rep))
                entre_capas = limpia(provisorio.difference(of)).area - extra.area
                print(f"    lo que suma la diferencia ENTRE LAS DOS CAPAS de barrios: "
                      f"{entre_capas:,.0f} m² · no es del polo")
                notas.append(f"suma declarada: {extra.area:,.0f} m² y {cj.locales(extra)} "
                             f"locales, {porque}; la diferencia entre las dos capas de barrios "
                             f"agrega otros {entre_capas:,.0f} m² que no son del polo")
            union = limpia(of.union(provisorio)) if receta.get("suma_declarada") else of
            print(f"    geometría que se adopta: {cj.ha(union):,.2f} ha, "
                  f"{cj.locales(union)} locales")

        # ---- Villa Ortúzar: las dos opciones, medidas -------------------------------------
        opciones = {}
        if receta.get("dos_opciones") and cerradas:
            _, _, tramo, dos_aceras, _ = cerradas[0]
            frent = cj.frentistas(tramo)
            una = [c for _, _, c in frent
                   if clave_barrio(cj.barrio_dominante(c)) == clave_barrio(nombre)]
            u_una = limpia(unary_union(una)) if una else None
            print(f"\n  las dos opciones de borde, medidas · NINGUNA se elige acá")
            print(f"    A · una sola acera, la de {nombre}: {len(una)} manzanas -> "
                  f"{cj.ha(u_una):,.2f} ha, {cj.locales(u_una)} locales")
            print(f"    B · las dos aceras, con reparto declarado: {len(frent)} manzanas -> "
                  f"{cj.ha(dos_aceras):,.2f} ha, {cj.locales(dos_aceras)} locales")
            rep = cj.reparto_por_barrio(dos_aceras)
            print(f"        reparto de B: " + " · ".join(f"{n} {p:.1f} %" for n, p, _ in rep))
            opciones_z44["geometria_A"] = u_una
            opciones = {
                "A_una_acera": dict(ha=round(cj.ha(u_una), 2), n_locales=cj.locales(u_una),
                                    manzanas=len(una)),
                "B_dos_aceras": dict(ha=round(cj.ha(dos_aceras), 2),
                                     n_locales=cj.locales(dos_aceras), manzanas=len(frent),
                                     reparto={n: round(p, 1) for n, p, _ in rep}),
            }
            notas.append(f"opción A una acera {cj.ha(u_una):,.2f} ha y {cj.locales(u_una)} "
                         f"locales; opción B dos aceras {cj.ha(dos_aceras):,.2f} ha y "
                         f"{cj.locales(dos_aceras)} locales")
            union = dos_aceras  # la geometría que viaja es la medida; la decisión no se toma acá

        # ---- la prueba que decide: ¿contiene los referentes de su propia ficha? ------------
        #
        # Se usa `covers` y no `contains`: el punto de una altura es el centro de la cuadra, o
        # sea un punto del EJE de la calle, y las manzanas están cortadas por esos mismos ejes.
        # Con `contains`, un referente sobre el borde exterior del polígono da False estando a
        # 0 m. La primera corrida lo mostró: «De Flores Café a 0 m» contado como afuera.
        if receta.get("referentes"):
            adentro, afuera, sin_puerta = [], [], []
            for nom_ref, calle, altura in receta["referentes"]:
                punto = cj.punto_de_altura(calle, altura)
                if punto is None:
                    sin_puerta.append(f"{nom_ref} ({calle} {altura})")
                elif union is not None and union.covers(punto):
                    adentro.append(nom_ref)
                else:
                    afuera.append((f"{nom_ref} ({calle} {altura})",
                                   union.distance(punto) if union is not None else None))
            resueltos = len(adentro) + len(afuera)
            if union is None:
                print(f"\n  los referentes que nombra la ficha: {resueltos} de "
                      f"{resueltos + len(sin_puerta)} resuelven en el callejero, y no hay "
                      f"polígono contra el cual probarlos")
            else:
                print(f"\n  los referentes que nombra la ficha: {len(adentro)} adentro, "
                      f"{len(afuera)} afuera, de {resueltos} que resuelven")
                if adentro:
                    print(f"      adentro: {', '.join(adentro)}")
                for etiqueta, d in sorted(afuera, key=lambda x: -(x[1] or 0))[:6]:
                    print(f"      afuera:  {etiqueta:<46} a {d:,.0f} m")
                notas.append(f"referentes de la ficha: {len(adentro)} de {resueltos} caen "
                             f"dentro del trazado")
            for etiqueta in sin_puerta:
                print(f"      la altura no está en el callejero: {etiqueta}")

        # ---- R12: contención por superficie perdida ----------------------------------------
        ha_nuevo = loc_nuevo = fuera_ha = 0.0
        solapes = []
        if union is not None and union.is_empty:
            raise SystemExit(f"{zona}: la unión salió vacía. Una geometría vacía mide 0,00 ha y "
                             f"se lee como un dato. No se sigue.")
        if union is not None:
            ha_nuevo, loc_nuevo = cj.ha(union), cj.locales(union)
            fuera_ha = max(0.0, ha_nuevo - cj.ha(limpia(union.intersection(provisorio))))
            print(f"\n  el polígono adoptado: {ha_nuevo:,.2f} ha · {loc_nuevo} locales")
            print(f"  contra el provisorio ({contenedor}): {ha_nuevo - ha_prov:+,.2f} ha · "
                  f"{loc_nuevo - loc_prov:+d} locales "
                  f"({ha_nuevo / ha_prov * 100:.1f} % de su superficie)")
            print(f"  R12 · superficie del trazado que queda FUERA del provisorio: "
                  f"{fuera_ha:,.2f} ha ({fuera_ha / ha_nuevo * 100:.1f} %)")
            if fuera_ha >= 0.01:
                rep = cj.reparto_por_barrio(union)
                print("       reparto por barrio: "
                      + " · ".join(f"{n} {p:.0f} %" for n, p, _ in rep))

            trazados[zona] = union
            # La geometría que se adopta para la zona, entera y en una sola fila. Va siempre,
            # también cuando hay piezas: sin esto, Núñez y Retiro -que cierran adoptando el
            # polígono de su barrio- quedaban en la capa sólo con sus piezas sueltas y el
            # perímetro que la zona publica no estaba en ningún archivo.
            capa.append(dict(
                zona_id=zona, nombre=nombre, pieza="la zona entera, como se adopta",
                tarea=receta["tarea"], fuente_del_perimetro=receta["fuente"],
                de_donde_sale_la_extension=(
                    "capa oficial de 48 barrios"
                    if receta.get("cierra_por_capa_administrativa")
                    else "unión de las piezas cerradas"),
                metodo=("polígono administrativo de la capa oficial"
                        if receta.get("cierra_por_capa_administrativa")
                        else "manzanas frentistas del callejero"),
                ha=round(ha_nuevo, 2), n_locales=loc_nuevo,
                subzona_de=receta.get("subzona_de", ""), geometry=union))
            for nom_p, detalle, tramo, poligono, de_donde in cerradas:
                capa.append(dict(
                    zona_id=zona, nombre=nombre, pieza=nom_p, tarea=receta["tarea"],
                    fuente_del_perimetro=receta["fuente"],
                    de_donde_sale_la_extension=de_donde,
                    metodo=f"manzanas frentistas del callejero sobre {detalle} "
                           f"(frente mínimo {FRENTE_MIN_M:.0f} m)",
                    ha=round(cj.ha(poligono), 2), n_locales=cj.locales(poligono),
                    subzona_de=receta.get("subzona_de", ""), geometry=poligono))

        # ---- lecturas medidas y NO adoptadas ----------------------------------------------
        for lectura in receta.get("lecturas", []):
            if lectura["tipo"] == "cara_de_ribera":
                cam = cj.eje_completo("CAMINITO")
                av = cj.eje_completo("DON PEDRO DE MENDOZA AV.")
                g = cj.cara_de_ribera("BOCA", av, cam)
                if g is None:
                    print(f"\n  lectura NO adoptada · {lectura['nombre']}: no resuelve")
                    continue
                print(f"\n  lectura medida y NO adoptada · {lectura['nombre']}: "
                      f"{cj.ha(g):,.2f} ha, {cj.locales(g)} locales")
            else:
                _, g, detalle = resolver(cj, lectura)
                if g is None:
                    print(f"\n  lectura NO adoptada · {lectura['nombre']}: no resuelve ({detalle})")
                    continue
                print(f"\n  lectura medida y NO adoptada · {lectura['nombre']}: "
                      f"{cj.ha(g):,.2f} ha, {cj.locales(g)} locales")
            print(f"      por qué no se adopta: {lectura['porque']}")

        # ---- veredicto ---------------------------------------------------------------------
        #
        # Cinco valores y no tres. Los dos nuevos existen porque la regla de la ronda anterior
        # -«si falta una pieza, la ficha no publica cifra»- deja sin cifra a dos zonas cuya
        # pieza faltante está MEDIDA y no tiene oferta: sumarla agregaría superficie y cero
        # locales. Esa no es una pieza que falta, es una pieza que se excluye con motivo, y la
        # diferencia se escribe en vez de esconderse en un «parcial».
        n_piezas = len(receta["piezas"]) + len(receta.get("sin_cerrar", []))
        if union is None:
            cerrado = "no"
        elif receta.get("veredicto"):
            cerrado = receta["veredicto"]
        elif receta.get("sin_cerrar"):
            cerrado = "parcial"
        else:
            cerrado = "si"
        if receta.get("veredicto_porque"):
            print(f"\n  por qué este veredicto: {receta['veredicto_porque']}")
        que_falta = "; ".join(f"{n}: {m}" for n, m in receta.get("sin_cerrar", []))
        if receta.get("aviso"):
            que_falta = "; ".join(x for x in (que_falta, receta["aviso"]) if x)
        if not que_falta:
            que_falta = "nada: el texto cerró todas las piezas que nombra"

        print(f"\n  VEREDICTO: {cerrado.upper()}  ({len(cerradas)} de {n_piezas} piezas)\n")

        filas.append(dict(
            zona_id=zona, nombre=nombre, tarea=receta["tarea"],
            ha=round(ha_nuevo, 2) if union is not None else "",
            n_locales=loc_nuevo if union is not None else "",
            ha_del_provisorio=round(ha_prov, 2), n_locales_del_provisorio=loc_prov,
            delta_ha=round(ha_nuevo - ha_prov, 2) if union is not None else "",
            delta_locales=(loc_nuevo - loc_prov) if union is not None else "",
            ha_fuera_del_provisorio=round(fuera_ha, 2) if union is not None else "",
            cerrado_si_no=cerrado, piezas_cerradas=len(cerradas), piezas_del_texto=n_piezas,
            subzona_de=receta.get("subzona_de", ""),
            solape_con="", ha_de_solape="", locales_de_solape="",
            recomendacion=receta.get("recomendacion", ""),
            que_falta=que_falta, provisorio=contenedor,
            fuente_del_perimetro=receta["fuente"],
            metodo=("manzanas frentistas del callejero; borde sobre calles por construcción"
                    if cerradas else
                    ("polígono administrativo de la capa oficial de 48 barrios"
                     if receta.get("cierra_por_capa_administrativa")
                     else "sin trazado: se mantiene el polígono administrativo")),
            opciones=json.dumps(opciones, ensure_ascii=False) if opciones else "",
            notas="; ".join(notas),
        ))

    # ---- SOLAPES · contra todo polo vecino, por superficie perdida -------------------------
    #
    # Va después del bucle y no adentro, y el motivo se vio en la primera corrida: adentro del
    # bucle, Pompeya se comparaba contra el soporte VIEJO del eje Sáenz -una concentración- en
    # vez de contra el trazado nuevo, porque el eje todavía no se había trazado. El orden de las
    # recetas no puede decidir contra qué se mide.
    print("=" * 98)
    print("SOLAPE DE CADA PERÍMETRO NUEVO CONTRA TODO POLO VECINO")
    print("superficie perdida -B.difference(A).area-, nunca covers()")
    print("=" * 98)
    vecinos = {pid: limpia(g) for pid, g in soportes.geometry.items()}
    vecinos.update(trazados)
    filas_solape = []
    for fila in filas:
        zona = fila["zona_id"]
        if zona not in trazados:
            continue
        union = trazados[zona]
        print(f"\n{zona} · {fila['nombre']}  ({cj.ha(union):,.2f} ha)")
        encontrados = []
        for otro_id, g in sorted(vecinos.items()):
            if otro_id == zona or not union.intersects(g):
                continue
            inter = limpia(union.intersection(g))
            if inter.area < 1.0:
                continue
            es_prov = (otro_id in soportes.index and otro_id not in trazados
                       and not bool(soportes.soporte_es_real.loc[otro_id]))
            marca = "  (el otro es provisorio: mide el barrio, no el polo)" if es_prov else ""
            print(f"    {otro_id:<22} lo propio que queda FUERA del otro: "
                  f"{union.difference(g).area / 10_000:8,.2f} ha  ->  "
                  f"comparten {cj.ha(inter):6,.2f} ha y {cj.locales(inter):4d} locales{marca}")
            encontrados.append(dict(zona_id=zona, nombre=fila["nombre"], solape_con=otro_id,
                                    ha_de_solape=round(cj.ha(inter), 2),
                                    locales_de_solape=cj.locales(inter),
                                    ha_propia_fuera_del_otro=round(
                                        union.difference(g).area / 10_000, 2),
                                    el_otro_es_provisorio=bool(es_prov)))
        if not encontrados:
            print("    ninguno: el polígono no toca ningún otro polo")
        filas_solape.extend(encontrados)
        fila["solape_con"] = " · ".join(e["solape_con"] for e in encontrados)
        fila["ha_de_solape"] = " · ".join(f"{e['ha_de_solape']:.2f}" for e in encontrados)
        fila["locales_de_solape"] = " · ".join(str(e["locales_de_solape"]) for e in encontrados)

    with (SALIDA / "solapes_cierre.csv").open("w", encoding="utf-8", newline="") as fh:
        campos_s = ["zona_id", "nombre", "solape_con", "ha_de_solape", "locales_de_solape",
                    "ha_propia_fuera_del_otro", "el_otro_es_provisorio"]
        w = csv.DictWriter(fh, fieldnames=campos_s)
        w.writeheader()
        w.writerows(filas_solape)

    # ---- sensibilidad al único parámetro del método ----------------------------------------
    print("\n" + "=" * 98)
    print("SENSIBILIDAD AL FRENTE MÍNIMO · el único parámetro que este método tiene")
    print("=" * 98)
    print(f"{'zona':<8}" + "".join(f"{f'{f:.0f} m':>16}" for f in FRENTE_SENSIBILIDAD))
    for receta in RECETAS:
        piezas_eje = [p for p in receta["piezas"] if p["tipo"] != "anillo_de_cara"]
        if not piezas_eje:
            continue
        linea = f"{receta['zona']:<8}"
        for frente in FRENTE_SENSIBILIDAD:
            trozos = []
            for pieza in piezas_eje:
                tramo, _, _ = resolver(cj, pieza)
                if tramo is None:
                    continue
                fr = cj.frentistas(tramo, frente_min=frente)
                if fr:
                    trozos.append(unary_union([c for _, _, c in fr]))
            ha = cj.ha(limpia(unary_union(trozos))) if trozos else 0.0
            linea += f"{ha:>13,.2f} ha"
        print(linea)

    # ---- TAREA 5 · el total, recalculado ---------------------------------------------------
    print("\n" + "=" * 98)
    print("TAREA 5 · el total, recalculado sobre la unión")
    print("=" * 98)

    publicables = gpd.read_file(PUBLICABLES).to_crs(CRS_METRICO)
    u124 = limpia(unary_union([limpia(g) for g in publicables.geometry]))
    suma124 = sum(limpia(g).area for g in publicables.geometry) / 10_000
    print(f"\nLas 124 concentraciones, que son el objeto del que sale la cifra publicada:")
    print(f"  suma de áreas individuales : {suma124:>12,.2f} ha")
    print(f"  área de la unión           : {cj.ha(u124):>12,.2f} ha   "
          f"-> solape {suma124 - cj.ha(u124):,.2f} ha, siguen disjuntas")
    print(f"  locales medidos dentro     : {cj.locales(u124):>12,}")
    print(f"  suma de la columna n_locales de la capa: {publicables.n_locales.sum():,}   "
          f"(pertenencia al agrupamiento, no punto dentro del polígono)")
    print(f"  la cifra publicada es 12.688 locales en 3.128,5 ha")

    antes = {pid: limpia(g) for pid, g in soportes.geometry.items()}
    despues = dict(antes)
    for zona, g in trazados.items():
        despues[zona] = g
    u_antes = limpia(unary_union(list(antes.values())))
    u_despues = limpia(unary_union(list(despues.values())))
    print(f"\nLa unión de los 41 polos -que NO es de dónde sale la cifra publicada-:")
    print(f"  antes de esta corrida : {cj.ha(u_antes):>12,.2f} ha · {cj.locales(u_antes):,} locales")
    print(f"  después               : {cj.ha(u_despues):>12,.2f} ha · "
          f"{cj.locales(u_despues):,} locales")
    print(f"  cambio                : {cj.ha(u_despues) - cj.ha(u_antes):>+12,.2f} ha · "
          f"{cj.locales(u_despues) - cj.locales(u_antes):+,} locales")

    # La decisión de borde de Villa Ortúzar mueve el total, así que el total va con las dos.
    u_a = None
    if opciones_z44:
        con_a = dict(despues)
        con_a["Z44"] = opciones_z44["geometria_A"]
        u_a = limpia(unary_union(list(con_a.values())))
        print(f"\n  el total depende de la decisión de borde de Villa Ortúzar, y por eso va "
              f"con las dos:")
        print(f"    con las dos aceras (opción B, la de arriba): {cj.ha(u_despues):>10,.2f} ha "
              f"· {cj.locales(u_despues):,} locales")
        print(f"    con una sola acera (opción A)              : {cj.ha(u_a):>10,.2f} ha "
              f"· {cj.locales(u_a):,} locales")
        print(f"    la decisión mueve                          : "
              f"{cj.ha(u_a) - cj.ha(u_despues):>+10,.2f} ha · "
              f"{cj.locales(u_a) - cj.locales(u_despues):+,} locales")

    # objetos disjuntos: ¿cuántos polos quedan 100 % fuera de todos los demás?
    contenidos = []
    for pid, g in despues.items():
        resto = limpia(unary_union([x for k, x in despues.items() if k != pid]))
        fuera = g.difference(resto).area
        if fuera < g.area * 0.01:
            contenidos.append((pid, fuera, g.area))
    print(f"\nObjetos territoriales: {len(despues)} fichas, "
          f"{len(despues) - len(contenidos)} disjuntos")
    for pid, fuera, area in contenidos:
        print(f"  {pid} queda dentro de otro: le sobran {fuera:,.0f} m² de {area:,.0f} "
              f"({fuera / area * 100:.2f} %)")

    total = dict(
        fecha=HOY,
        las_124_suma_de_areas_ha=round(suma124, 2),
        las_124_union_ha=round(cj.ha(u124), 2),
        las_124_locales_medidos=cj.locales(u124),
        las_124_locales_por_pertenencia=int(publicables.n_locales.sum()),
        union_41_polos_antes_ha=round(cj.ha(u_antes), 2),
        union_41_polos_antes_locales=cj.locales(u_antes),
        union_41_polos_despues_ha=round(cj.ha(u_despues), 2),
        union_41_polos_despues_locales=cj.locales(u_despues),
        union_41_con_villa_ortuzar_una_acera_ha=round(cj.ha(u_a), 2) if u_a else None,
        union_41_con_villa_ortuzar_una_acera_locales=cj.locales(u_a) if u_a else None,
        objetos_disjuntos=len(despues) - len(contenidos),
        fichas=len(despues),
        contenidos=[c[0] for c in contenidos],
    )

    # ---- salidas ---------------------------------------------------------------------------
    campos = ["zona_id", "nombre", "tarea", "ha", "n_locales", "ha_del_provisorio",
              "n_locales_del_provisorio", "delta_ha", "delta_locales", "ha_fuera_del_provisorio",
              "cerrado_si_no", "piezas_cerradas", "piezas_del_texto", "subzona_de", "solape_con",
              "ha_de_solape", "locales_de_solape", "recomendacion", "que_falta", "provisorio",
              "fuente_del_perimetro", "metodo", "opciones", "notas"]
    with (SALIDA / "perimetros_cierre.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=campos)
        w.writeheader()
        w.writerows(filas)

    (SALIDA / "geometria").mkdir(exist_ok=True)
    gpd.GeoDataFrame(capa, geometry="geometry", crs=CRS_METRICO).to_crs(CRS_SALIDA).to_file(
        SALIDA / "geometria" / "perimetros_cierre.geojson", driver="GeoJSON")

    (SALIDA / "total_recalculado.json").write_text(
        json.dumps(total, ensure_ascii=False, indent=2), encoding="utf-8")


    print(f"\nEscrito: perimetros_cierre.csv ({len(filas)} filas) · "
          f"geometria/perimetros_cierre.geojson ({len(capa)} piezas, {CRS_SALIDA}) · "
          f"solapes_cierre.csv ({len(filas_solape)} filas) · total_recalculado.json")
    conteo = {}
    for f in filas:
        conteo[f["cerrado_si_no"]] = conteo.get(f["cerrado_si_no"], 0) + 1
    for k in sorted(conteo):
        print(f"  {k:<32} {conteo[k]}")
    print(f"  {'con perímetro medido':<32} "
          f"{sum(v for k, v in conteo.items() if k != 'no')} de {len(filas)}")


if __name__ == "__main__":
    main()
