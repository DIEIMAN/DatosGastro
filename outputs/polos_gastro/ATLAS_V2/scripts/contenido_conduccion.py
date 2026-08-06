#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Capa editorial de la edición de conducción.

Se deriva de la V2.1 RESTANDO: no hay una sola afirmación que no esté en el corpus
cerrado, ni un solo número que la V2.1 no publique. Lo que cambia es el registro.

Cada ficha se reordena en los cuatro bloques del lector (B3):

    1. Qué es esta zona          - el carácter gastronómico del lugar, en positivo.
    2. Cuánta oferta hay         - la frase de cifra (B2) más una línea de contexto.
    3. De qué se compone         - las partes internas, con nombre de barrio o de calle.
    4. Qué hay que tener en cuenta - como máximo tres líneas, las que sirven para decidir.

Las salvedades que no entran en esas tres líneas no se pierden: viajan enteras a la
edición técnica, y `qa/TRAZABILIDAD_LENGUAJE.csv` deja registrado cuáles fueron.

Ninguna cifra cambia. El control `diff_cifras_v21_conduccion` lo verifica ficha por
ficha: todo número publicado acá tiene que existir en la ficha equivalente de la V2.1.
"""

from __future__ import annotations

import re

# ---------------------------------------------------------------------------------------
# B2 · El badge de cifra pasa a ser una frase
#
# La V2.1 decía un número con tres elementos: un símbolo (= o ≥), una etiqueta en
# mayúsculas (CIFRA EXACTA / COTA INFERIOR / ANTECEDENTE PREVIO) y el número. Acá lo
# dice una sola línea en castellano. La distinción entre los cuatro casos se mantiene:
# la lleva la frase, no una etiqueta.
# ---------------------------------------------------------------------------------------

SIN_CIFRA = "SIN_CIFRA_CANONICA_COMPARABLE"


def numero_principal(cifra: str) -> str | None:
    """Primer número de la cifra publicada por la V2.1, sin tocarlo."""
    m = re.search(r"\d[\d.]*", str(cifra))
    return m.group(0) if m else None


def frase_cifra(ficha: dict) -> str:
    cruda = str(ficha["cifra"])
    if cruda.startswith(SIN_CIFRA):
        return "Zona caracterizada, sin conteo propio"
    n = numero_principal(cruda)
    naturaleza = ficha["naturaleza"]
    if naturaleza == "cota_inferior":
        return f"Al menos {n} locales"
    if naturaleza == "historica_metodologica":
        return f"{n} locales según un relevamiento anterior"
    return f"{n} locales relevados"


# ---------------------------------------------------------------------------------------
# B3 · Las 22 fichas
#
# `es`       -> párrafo de dos o tres frases. En positivo.
# `contexto` -> la línea que acompaña a la frase de cifra.
# `compone`  -> partes internas con su nombre real de barrio o de calle.
# `cuenta`   -> máximo tres líneas.
# ---------------------------------------------------------------------------------------

MINIMO = "Es un mínimo: puede haber más, no menos."
NO_ABIERTOS = "El número cuenta locales relevados, no locales abiertos hoy."
UNA_VEZ = "Se contó una sola vez a los locales que aparecían repetidos."

FICHAS: dict[str, dict] = {
    "R01": dict(
        es="Palermo concentra oferta gastronómica de manera amplia y variada, distribuida en "
           "tres áreas con personalidad propia: Palermo Soho, Palermo Hollywood y Las Cañitas. "
           "Entre una y otra hay tramos sin oferta, y esos espacios forman parte de cómo "
           "funciona la zona.",
        contexto="El Atlas describe y ubica Palermo, pero no publica un número de locales "
                 "para el conjunto.",
        compone=[
            "Palermo Soho, Palermo Hollywood y Las Cañitas.",
            "Son partes del barrio de Palermo: nombres de uso corriente, sin límite "
            "administrativo propio. No son zonas nuevas ni polos separados.",
            "Cada una tiene su mapa ampliado; ninguna de las tres representa por sí sola "
            "a todo Palermo.",
        ],
        cuenta=[
            "No hay un contorno oficial de Palermo: el área dibujada es una lectura, no un límite.",
            "Los espacios sin oferta entre las tres partes se muestran a propósito y no se rellenan.",
            "Villa Crespo y Chacarita son zonas aparte y no quedan incluidas en Palermo.",
        ],
    ),
    "R02": dict(
        es="La avenida Corrientes es una calle de teatros, librerías y pizzerías donde la "
           "gastronomía se ordena a lo largo de la avenida y no alrededor de un centro. "
           "El tramo más reconocible va, aproximadamente, entre 9 de Julio y Callao.",
        contexto="No se hizo un conteo propio de esta zona.",
        compone=[
            "Se lee como un corredor a lo largo de la avenida, sin partes internas propias.",
            "El tramo de referencia va aproximadamente entre 9 de Julio y Callao.",
        ],
        cuenta=[
            "Ese tramo es una referencia descriptiva, no una delimitación oficial.",
            "Abasto se relaciona con Corrientes, pero es una zona distinta: no se cuentan ni "
            "se dibujan como una sola.",
        ],
    ),
    "R03": dict(
        es="San Telmo es un polo gastronómico apoyado en el casco histórico. El Mercado de "
           "San Telmo funciona como punto de encuentro y la calle Defensa ordena el recorrido.",
        contexto="No se hizo un conteo propio de esta zona.",
        compone=[
            "El núcleo del casco histórico, el tejido de calles antiguas y el eje de la calle Defensa.",
            "El Mercado de San Telmo es el hito de referencia de la zona.",
        ],
        cuenta=[
            "La lectura no se extiende a todo el sur de la Ciudad.",
            "Boulevard Caseros y el entorno de Parque Lezama están asociados a San Telmo, "
            "pero son zonas distintas.",
        ],
    ),
    "R04": dict(
        es="Puerto Madero ordena su oferta gastronómica a lo largo de los diques, sobre dos "
           "frentes enfrentados y con hitos repartidos en el borde. Es una banda larga antes "
           "que una mancha alrededor de un centro.",
        contexto="No se hizo un conteo propio de esta zona.",
        compone=[
            "La sucesión de diques a lo largo del agua y el frente costero, con dos partes "
            "que el mapa rotula: los Docks y la Dársena Sur.",
            "No tiene un centro único: la oferta se distribuye sobre los dos frentes.",
        ],
        cuenta=[
            "El área dibujada excluye el espejo de agua de los cuatro diques.",
            "La lectura no se extiende más allá del frente relevado ni se une con el Centro.",
        ],
    ),
    "R05": dict(
        es="Belgrano es un polo de escala grande, con tres centros gastronómicos distintos: "
           "el Barrio Chino, el Bajo Belgrano y Belgrano R. Los tres funcionan dentro de una "
           "misma zona y con pesos distintos.",
        contexto="Es el dato de un relevamiento anterior: sirve para describir la zona, no es "
                 "su número de hoy.",
        compone=[
            "Barrio Chino, Bajo Belgrano y Belgrano R.",
            "Son tres centros dentro de Belgrano, no tres zonas separadas.",
            "Belgrano R ocupa un lugar secundario, sin dejar de pertenecer a la zona.",
        ],
        cuenta=[
            "Los 697 no equivalen a locales abiertos hoy.",
            "Los tres centros no se cuentan por separado ni se suman entre sí.",
            "Villa Urquiza y Donado–Holmberg quedan fuera de Belgrano.",
        ],
    ),
    "R06": dict(
        es="Recoleta se presenta como una sola zona continua, con oferta diversa en su "
           "interior. El Atlas la trata como una unidad y no la parte en pedazos.",
        contexto="Un relevamiento anterior dejó datos de trabajo sobre Recoleta, pero no un "
                 "número publicable para la zona.",
        compone=[
            "Se lee como una sola unidad continua.",
            "El detalle interno del relevamiento anterior no se publica como una lista de partes.",
        ],
        cuenta=[
            "El área dibujada es una lectura de la zona, no un límite oficial.",
            "Esmeralda–Paraguay es una zona distinta, aunque esté cerca.",
        ],
    ),
    "R07": dict(
        es="La Costanera Norte tiene su oferta gastronómica repartida en cuatro tramos "
           "separados a lo largo del frente al río. Entre un tramo y otro hay espacios sin "
           "oferta que forman parte de cómo es la zona.",
        contexto="Es el dato de un relevamiento anterior: describe la zona, no mide su "
                 "situación de hoy.",
        compone=[
            "Cuatro tramos separados sobre el frente costero.",
            "Los cuatro se leen juntos como una sola zona, sin unirlos con una línea que no existe.",
        ],
        cuenta=[
            "Los espacios vacíos entre tramos son reales y se muestran.",
            "Los cuatro tramos no son cuatro zonas nuevas.",
            "Los 72 no equivalen a locales abiertos hoy.",
        ],
    ),
    "R08": dict(
        es="Villa Crespo tiene identidad gastronómica propia, apoyada sobre Thames, "
           "Gurruchaga y Velazco. Es una zona reconocible, aunque su borde exacto todavía "
           "no esté fijado.",
        contexto=UNA_VEZ,
        compone=[
            "Se organiza sobre los ejes de Thames, Gurruchaga y Velazco.",
            "No tiene un contorno cerrado: la definición fina de los bordes quedó para más adelante.",
        ],
        cuenta=[
            NO_ABIERTOS,
            "En tres puntos el relevamiento llegó a su tope y no pudo seguir contando: "
            "ahí puede haber más locales.",
            "Villa Crespo es una zona distinta de Palermo y de Chacarita.",
        ],
    ),
    "R09": dict(
        es="En Chacarita la gastronomía se agrupa en dos focos separados: Jorge Newbery y "
           "Dorrego. No forman una sola mancha continua, y el Atlas los muestra separados.",
        contexto=UNA_VEZ + " El mapa dibuja los dos focos, que no cubren la totalidad de lo relevado.",
        compone=[
            "El foco de Jorge Newbery y el foco de Dorrego, independientes entre sí.",
            "Federico Lacroze aparece solo para ubicar la zona: no es el eje de Chacarita.",
        ],
        cuenta=[
            NO_ABIERTOS,
            "Los dos focos no se juntan en un polo único.",
            "Chacarita no se mezcla con Palermo, Villa Crespo ni Federico Lacroze.",
        ],
    ),
    "R10": dict(
        es="Caballito tiene dos núcleos gastronómicos separados: Pedro Goyena y Primera "
           "Junta–Mercado del Progreso. Cada uno funciona por su cuenta y el Atlas no los une.",
        contexto=UNA_VEZ + " El mapa dibuja los dos núcleos, que no cubren la totalidad de lo relevado.",
        compone=[
            "El núcleo de Pedro Goyena y el de Primera Junta–Mercado del Progreso.",
            "El Patio de los Lecheros se miró como punto de control y quedó fuera de la zona.",
            "Parque Rivadavia salió de la lectura vigente y no se vuelve a usar.",
        ],
        cuenta=[
            NO_ABIERTOS,
            "Los dos núcleos no forman una sola área continua.",
        ],
    ),
    "R11": dict(
        es="Boulevard Caseros es una concentración chica y localizada, vinculada al entorno "
           "de Parque Lezama y San Telmo. Es un tramo corto, no una avenida gastronómica de "
           "punta a punta.",
        contexto=UNA_VEZ,
        compone=[
            "Un tramo corto del boulevard, sin partes internas propias.",
            "47 de los locales quedaron a menos de 250 metros del eje: es una descripción, "
            "no la prueba de una avenida continua.",
        ],
        cuenta=[
            "La evidencia no alcanza para hablar de una avenida gastronómica continua.",
            "La lectura no se extiende a Parque Patricios ni al resto de Barracas.",
            "Está asociada a San Telmo y a Lezama, pero es una zona distinta.",
        ],
    ),
    "R12": dict(
        es="El Centro y el Microcentro no funcionan como un polo único, sino como varias "
           "áreas gastronómicas vecinas que conviene leer por separado. Cada una tiene su "
           "propio entorno y su propia escala.",
        contexto=MINIMO,
        compone=[
            "Microcentro financiero, Plaza de Mayo–Monserrat, Avenida de Mayo, Retiro central "
            "y Tribunales.",
            "143 locales están dentro de dos de esas áreas a la vez: por eso los números de "
            "las áreas no se suman.",
            "Tribunales se lee aparte y con menos respaldo que las demás.",
        ],
        cuenta=[
            "No es un polo único del Centro.",
            NO_ABIERTOS,
        ],
    ),
    "R13": dict(
        es="Abasto es un polo gastronómico reconocible sobre el tramo de la avenida "
           "Corrientes con el que se lo asocia. Su delimitación todavía es provisoria.",
        contexto=MINIMO,
        compone=[
            "Se lee como una sola pieza sobre el tramo de Corrientes.",
            "Para relevarlo se lo dividió en tres tramos —al menos 91, 115 y 108 locales—, "
            "sin que ninguno se destaque sobre los otros.",
        ],
        cuenta=[
            "Abasto es una zona distinta de la avenida Corrientes, aunque estén asociadas.",
            "La delimitación es provisoria y la lectura no abarca todo Balvanera ni todo Almagro.",
        ],
    ),
    "R14": dict(
        es="Boedo tiene una identidad cultural fuerte y una oferta gastronómica que aparece "
           "a lo largo de la avenida, en tramos, con interrupciones entre ellos.",
        contexto=UNA_VEZ,
        compone=[
            "Tramos sueltos a lo largo de la avenida Boedo, sin partes internas propias.",
        ],
        cuenta=[
            "La identidad cultural de la avenida no equivale a una oferta gastronómica continua.",
            NO_ABIERTOS,
            "La franja de 150 metros usada para relevar es una herramienta de trabajo, no un límite.",
        ],
    ),
    "R15": dict(
        es="Devoto tiene un núcleo gastronómico estable alrededor de Plaza Arenales, con una "
           "periferia más difusa a su alrededor.",
        contexto=UNA_VEZ,
        compone=[
            "El núcleo alrededor de Plaza Arenales, en Villa Devoto.",
            "La periferia que lo rodea no está definida con precisión.",
        ],
        cuenta=[
            "El núcleo no autoriza a extender la zona a todo el barrio.",
            "Villa Pueyrredón y Villa del Parque quedan fuera.",
            NO_ABIERTOS,
        ],
    ),
    "R16": dict(
        es="Donado y Holmberg forman un doble eje gastronómico: la oferta se ubica sobre las "
           "dos calles, en tramos, y no en una mancha continua.",
        contexto=UNA_VEZ,
        compone=[
            "Las calles Donado y Holmberg, con tramos separados entre sí.",
        ],
        cuenta=[
            "Es una zona distinta de Villa Urquiza y no queda incluida en ella.",
            "El nombre institucional es Donado–Holmberg; «DoHo» es un apodo y no se usa como nombre.",
            NO_ABIERTOS,
        ],
    ),
    "R17": dict(
        es="Villa Urquiza es un polo gastronómico organizado sobre tres calles: Triunvirato, "
           "Monroe y Congreso.",
        contexto=UNA_VEZ,
        compone=[
            "Los ejes de Triunvirato, Monroe y Congreso.",
            "El mapa ubica el de Triunvirato, el único con recorrido cerrado en el material "
            "disponible; Monroe y Congreso aparecen como calles de referencia.",
        ],
        cuenta=[
            "Donado–Holmberg es una zona aparte y no queda incluida en Villa Urquiza.",
            "La zona no abarca todo el barrio administrativo.",
            NO_ABIERTOS,
        ],
    ),
    "R18": dict(
        es="En el cruce de Esmeralda y Paraguay hay oferta gastronómica documentada, sin un "
           "centro claro alrededor del cual se ordene.",
        contexto=MINIMO,
        compone=[
            "Se lee como una sola pieza, sin partes internas propias.",
            "La mayor cantidad de locales no está en el centro del círculo sino en las bandas "
            "intermedias, entre 100 y 300 metros.",
        ],
        cuenta=[
            "El círculo de 400 metros es el radio con que se consultó la zona, no un centro demostrado.",
            "«Nuevo Bajo» no es el nombre de esta zona y no se usa para ampliarla.",
        ],
    ),
    "R19": dict(
        es="Sobre Federico Lacroze hay oferta gastronómica documentada en dos tramos "
           "separados: entre Libertador y Cabildo, y entre Cabildo y Álvarez Thomas.",
        contexto="Al momento del relevamiento, 204 estaban abiertos y 7 cerrados de forma temporaria.",
        compone=[
            "El tramo entre Libertador y Cabildo, con al menos 112 locales, y el tramo entre "
            "Cabildo y Álvarez Thomas, con al menos 138.",
            "Los dos se relevaron por separado y sus números no se suman.",
            "Cerca de Cabildo los dos tramos se tocan y comparten 39 locales.",
        ],
        cuenta=[
            MINIMO,
            "Que los tramos se toquen no prueba que la oferta sea continua a lo largo de toda "
            "la avenida.",
            "La zona no llega hasta Dorrego ni se mezcla con Chacarita.",
        ],
    ),
    "R20": dict(
        es="Sobre García del Río, entre Cabildo y Parque Saavedra, hay una oferta "
           "gastronómica continua y de escala modesta, algo más concentrada del lado de "
           "Cabildo y más rala hacia el parque.",
        contexto="Al momento del relevamiento, 39 estaban abiertos y 1 cerrado de forma temporaria.",
        compone=[
            "Un solo tramo, entre Cabildo y Parque Saavedra.",
            "Parque Saavedra se usó para verificar que la oferta no siguiera dentro del parque: "
            "no aporta locales.",
        ],
        cuenta=[
            MINIMO,
            "No alcanza para hablar de un corredor, un eje ni un polo.",
            "Villa Pueyrredón es una zona separada de esta.",
        ],
    ),
    "R21": dict(
        es="En La Paternal la oferta gastronómica está repartida en un área extensa, sin un "
           "centro que la organice. Es una zona documentada, no una concentración.",
        contexto="Al momento del relevamiento, 242 estaban abiertos y 12 cerrados de forma temporaria.",
        compone=[
            "El sector oeste de La Paternal, con al menos 237 locales.",
            "El borde de Rojas y Honorio Pueyrredón, con 19 locales, mirado aparte como límite "
            "con Villa Crespo.",
            "Los dos se relevaron con criterios distintos y sus números no se suman.",
        ],
        cuenta=[
            MINIMO,
            "No hay un centro, un corredor ni una red de puntos demostrados.",
            "El borde con Villa Crespo sigue siendo parte de La Paternal.",
        ],
    ),
    "R22": dict(
        es="En Villa Pueyrredón la oferta gastronómica está repartida por todo el barrio, con "
           "algo más de densidad en el centro y el centro este. No hay un núcleo dominante ni "
           "una avenida que la ordene.",
        contexto="Al momento del relevamiento, 152 estaban abiertos y 6 cerrados de forma temporaria.",
        compone=[
            "El centro y el centro este concentran algo más de oferta: es una descripción, no "
            "una zona nueva.",
            "La avenida San Martín no se toma como eje de la zona.",
        ],
        cuenta=[
            MINIMO,
            "El contorno del mapa es el marco con que se relevó el barrio, no un área gastronómica.",
            "García del Río es una zona separada: entre las dos no hay locales en común.",
        ],
    ),
}

# Corrección editorial 2026-08-04. Acá vivían dos fórmulas que se repetían a lo largo de
# todo el documento y que se retiraron:
#   · ADVERTENCIA_UNICA, al pie de las 22 páginas de ficha (22 apariciones).
#   · APROX, el arranque genérico del bloque «Qué no es» de cada mapa (31 apariciones).
# De cada bloque «Qué no es» quedó sólo la frase propia de esa zona, que es la que informa.
# La salvedad de fondo no se perdió: está completa en «Cómo leer el Atlas» y en el cierre.

# ---------------------------------------------------------------------------------------
# Bloque inferior de las 29 páginas de mapa, en el registro de la conducción.
# ---------------------------------------------------------------------------------------

TRIOS: dict[str, dict] = {
    "R01": dict(
        muestra="El área aproximada de Palermo, con sus tres partes: Palermo Soho, Palermo "
                "Hollywood y Las Cañitas.",
        mide="No se hizo un conteo propio de esta zona: el Atlas la describe y la ubica.",
        no_es="Los espacios sin oferta entre las tres partes se muestran a "
              "propósito y no se cierran en un contorno único."),
    "R02": dict(
        muestra="El tramo de la avenida Corrientes donde se concentran los teatros y la "
                "oferta gastronómica, aproximadamente entre 9 de Julio y Callao.",
        mide="No se hizo un conteo propio de esta zona.",
        no_es="Abasto se relaciona con Corrientes, pero es una zona distinta: no se "
              "dibujan como una sola."),
    "R03": dict(
        muestra="El área aproximada de San Telmo, sobre el casco histórico, con el Mercado de "
                "San Telmo como hito y la calle Defensa como recorrido.",
        mide="No se hizo un conteo propio de esta zona.",
        no_es="Boulevard Caseros está asociado a San Telmo, pero es una zona distinta."),
    "R04": dict(
        muestra="El área aproximada de Puerto Madero, sobre la banda de diques y el frente "
                "al río, con sus dos partes: los Docks y la Dársena Sur.",
        mide="No se hizo un conteo propio de esta zona.",
        no_es="El área excluye el espejo de agua de los cuatro diques, descontado con "
              "cartografía pública de acceso abierto verificada contra la capa oficial de "
              "cuerpos de agua de la Ciudad."),
    "R05": dict(
        muestra="El área aproximada de Belgrano, con sus tres centros: Barrio Chino–Belgrano C, "
                "Cabildo–Juramento y Belgrano R.",
        mide="697 locales según un relevamiento anterior. Describe la zona; no es su número de hoy.",
        no_es="Los 697 no equivalen a locales abiertos hoy ni se ponen al lado de las "
              "cifras de otras zonas."),
    "R06": dict(
        muestra="El área aproximada de Recoleta, presentada como una sola unidad continua.",
        mide="No se hizo un conteo propio de esta zona.",
        no_es="El detalle interno de la zona no se publica como una lista de partes."),
    "R07": dict(
        muestra="El área aproximada de la Costanera Norte, con sus cuatro tramos separados a lo "
                "largo del frente al río.",
        mide="72 locales según un relevamiento anterior.",
        no_es="Los espacios vacíos entre tramos son reales: no se unen con una línea "
              "que no existe."),
    "R08": dict(
        muestra="El área aproximada de Villa Crespo, sobre los ejes de Thames y Gurruchaga.",
        mide="646 locales relevados, contando una sola vez los que aparecían repetidos. No "
             "equivale a locales abiertos hoy.",
        no_es="Villa Crespo tiene identidad propia frente a Palermo y Chacarita, y no "
              "queda incluida en ellas."),
    "R09": dict(
        muestra="Los dos focos gastronómicos de Chacarita: Jorge Newbery y Dorrego.",
        mide="327 locales relevados en Chacarita, contando una sola vez los repetidos. El mapa "
             "dibuja los dos focos, que no cubren todo lo relevado. No equivale a locales "
             "abiertos hoy.",
        no_es="Los focos no forman un contorno común ni un polo único, y no se mezclan "
              "con Palermo, Villa Crespo ni Federico Lacroze."),
    "R10": dict(
        muestra="Los dos núcleos gastronómicos de Caballito: Pedro Goyena y Primera Junta–"
                "Mercado del Progreso.",
        mide="907 locales relevados en Caballito, contando una sola vez los repetidos. El mapa "
             "dibuja los dos núcleos, que no cubren todo lo relevado. No equivale a locales "
             "abiertos hoy.",
        no_es="Los núcleos son independientes y no forman una sola área; Parque "
              "Rivadavia quedó fuera de la lectura vigente."),
    "R11": dict(
        muestra="El área aproximada de Boulevard Caseros, un tramo corto vinculado al entorno de "
                "Parque Lezama y San Telmo.",
        mide="66 locales relevados, contando una sola vez los repetidos. No equivale a locales "
             "abiertos hoy.",
        no_es="La evidencia no alcanza para una avenida gastronómica continua, y la "
              "lectura no se extiende a Parque Patricios ni a Barracas."),
    "R12": dict(
        muestra="Las áreas gastronómicas del Centro y el Microcentro, cada una con su propio entorno.",
        mide="Al menos 797 locales distintos. Es un mínimo: puede haber más, no menos. No "
             "equivale a locales abiertos hoy.",
        no_es="No es un polo único del Centro: los números de las áreas no se suman "
              "porque comparten locales."),
    "R13": dict(
        muestra="El área aproximada de Abasto, sobre el tramo de la avenida Corrientes con el "
                "que se lo asocia.",
        mide="Al menos 314 locales. Es un mínimo: puede haber más, no menos. No equivale a "
             "locales abiertos hoy.",
        no_es="Abasto es una zona distinta de la avenida Corrientes y su delimitación "
              "todavía es provisoria."),
    "R14": dict(
        muestra="El área aproximada del eje de la avenida Boedo, con oferta que aparece en tramos.",
        mide="79 locales relevados, contando una sola vez los repetidos. No equivale a locales "
             "abiertos hoy.",
        no_es="La identidad cultural de la avenida no equivale a una oferta "
              "gastronómica continua."),
    "R15": dict(
        muestra="El área aproximada de Devoto, con su núcleo alrededor de Plaza Arenales.",
        mide="119 locales relevados, contando una sola vez los repetidos. No equivale a locales "
             "abiertos hoy.",
        no_es="La periferia del polo no está definida con precisión y la lectura no se "
              "extiende a Villa Pueyrredón ni a Villa del Parque."),
    "R16": dict(
        muestra="El área aproximada del doble eje de Donado y Holmberg, con la oferta repartida "
                "en tramos.",
        mide="40 locales relevados, contando una sola vez los repetidos. No equivale a locales "
             "abiertos hoy.",
        no_es="No forma un área única ni queda incluida en Villa Urquiza."),
    "R17": dict(
        muestra="El área aproximada de Villa Urquiza. De sus tres calles —Triunvirato, Monroe y "
                "Congreso— el mapa ubica la de Triunvirato, la única con recorrido cerrado en el "
                "material disponible.",
        mide="189 locales relevados, contando una sola vez los repetidos. No equivale a locales "
             "abiertos hoy.",
        no_es="Villa Urquiza no incluye a Donado–Holmberg, que es una zona aparte."),
    "R18": dict(
        muestra="El círculo de 400 metros con que se consultó el cruce de Esmeralda y Paraguay.",
        mide="Al menos 216 locales. Es un mínimo: puede haber más, no menos. No equivale a "
             "locales abiertos hoy.",
        no_es="El círculo es el radio con que se consultó la zona, no un centro demostrado."),
    "R19": dict(
        muestra="Los dos tramos de Federico Lacroze: entre Libertador y Cabildo, y entre Cabildo "
                "y Álvarez Thomas.",
        mide="Al menos 211 locales. Al momento del relevamiento, 204 estaban abiertos y 7 "
             "cerrados de forma temporaria.",
        no_es="Los dos tramos se relevaron por separado y sus números no se suman; la "
              "zona no se mezcla con Chacarita."),
    "R20": dict(
        muestra="El tramo de García del Río, entre Cabildo y Parque Saavedra, con oferta continua "
                "y de escala modesta.",
        mide="Al menos 40 locales. Es un mínimo: puede haber más, no menos. No equivale a locales "
             "abiertos hoy.",
        no_es="El tramo no sigue antes de Cabildo ni dentro del parque, y no alcanza "
              "para hablar de un corredor."),
    "R21": dict(
        muestra="El área aproximada de La Paternal, extensa y con la oferta repartida.",
        mide="Al menos 254 locales. Al momento del relevamiento, 242 estaban abiertos y 12 "
             "cerrados de forma temporaria.",
        no_es="No tiene un centro demostrado ni un contorno definido, y el borde con "
              "Villa Crespo sigue siendo parte de La Paternal."),
    "R22": dict(
        muestra="El marco con que se relevó Villa Pueyrredón, con la oferta repartida por todo "
                "el barrio.",
        mide="Al menos 158 locales. Es un mínimo: puede haber más, no menos. No equivale a "
             "locales abiertos hoy.",
        no_es="El contorno es el marco con que se relevó el barrio, no un área "
              "gastronómica: la mayor densidad del centro y centro este es una descripción, no "
              "un núcleo adoptado."),
}

TRIOS_DETALLE: dict[str, dict] = {
    # S-02/S-03 · las tres partes de Palermo, cada una con su propia ampliación y con las
    # otras dos atrás en gris. El pie dice de qué parte se trata y qué queda alrededor.
    "R01_DETALLE_PALERMO_SOHO.png": dict(
        muestra="Palermo Soho ampliado, una de las tres partes de Palermo. Alrededor, las "
                "avenidas del entorno; en gris, las otras partes de Palermo que alcanzan "
                "a verse.",
        mide="No se hizo un conteo propio de esta zona.",
        no_es="Palermo Soho no representa por sí solo a todo Palermo."),
    "R01_DETALLE_PALERMO_HOLLYWOOD.png": dict(
        muestra="Palermo Hollywood ampliado, una de las tres partes de Palermo. Alrededor, "
                "las avenidas del entorno; en gris, las otras partes de Palermo que "
                "alcanzan a verse.",
        mide="No se hizo un conteo propio de esta zona.",
        no_es="Palermo Hollywood no representa por sí solo a todo Palermo."),
    "R01_DETALLE_LAS_CANITAS.png": dict(
        muestra="Las Cañitas ampliada, una de las tres partes de Palermo. Alrededor, las "
                "avenidas del entorno; en gris, las otras partes de Palermo que alcanzan "
                "a verse.",
        mide="No se hizo un conteo propio de esta zona.",
        no_es="Las Cañitas no representa por sí sola a todo Palermo."),
    "R02_R13_CONTEXTO_CORRIENTES_ABASTO.png": dict(
        muestra="La avenida Corrientes y el polo de Abasto en un mismo mapa, para ver cómo se "
                "ubican uno respecto del otro.",
        mide="Ninguna de las dos zonas tiene un conteo propio.",
        no_es="Estar cerca no las convierte en una sola zona."),
    "R08_DETALLE_SATURACIONES_RESIDUALES.png": dict(
        muestra="Los tres puntos de Villa Crespo donde el relevamiento llegó a su tope y no pudo "
                "seguir contando.",
        mide="646 locales relevados en Villa Crespo; en esos tres puntos el conteo quedó incompleto.",
        no_es="Los tres círculos marcan un límite del relevamiento, no una "
              "concentración de oferta."),
    "R12_DETALLE_SUBUNIDADES_SATURACION.png": dict(
        muestra="Las áreas del Centro y el Microcentro ampliadas, cada una con su nombre.",
        mide="Al menos 797 locales distintos en el conjunto; 143 de ellos están dentro de dos "
             "áreas a la vez.",
        no_es="Los números de las áreas no se suman ni se ordenan de mayor a menor, "
              "porque comparten locales."),
    "R15_DETALLE_NUCLEO_PERIFERIA.png": dict(
        muestra="Devoto ampliado. Su núcleo se organiza alrededor de Plaza Arenales.",
        mide="119 locales relevados, contando una sola vez los repetidos.",
        no_es="No hay un trazado propio del núcleo, así que el mapa muestra el polo completo."),
    "R19_DETALLE_LACROZE_CABILDO.png": dict(
        muestra="Los dos tramos de Federico Lacroze de cerca, con la zona donde se tocan, junto "
                "a Cabildo.",
        mide="Al menos 211 locales en el conjunto; cada tramo se relevó por separado y sus "
             "números no se suman.",
        no_es="Que los tramos se toquen no prueba que la oferta sea continua entre ellos."),
    "R20_DETALLE_CABILDO_PARQUE_SAAVEDRA.png": dict(
        muestra="El extremo de García del Río junto a Parque Saavedra, con el parque señalado.",
        mide="Al menos 40 locales en el tramo. El parque no aporta locales: se usó para "
             "verificar que el tramo no siguiera dentro de él.",
        no_es="El parque no integra la zona."),
}

TITULOS_DETALLE = {
    "R01_DETALLE_PALERMO_SOHO.png": "Palermo Soho",
    "R01_DETALLE_PALERMO_HOLLYWOOD.png": "Palermo Hollywood",
    "R01_DETALLE_LAS_CANITAS.png": "Las Cañitas",
    "R02_R13_CONTEXTO_CORRIENTES_ABASTO.png": "Corrientes y Abasto",
    "R08_DETALLE_SATURACIONES_RESIDUALES.png": "Dónde se cortó el relevamiento",
    "R12_DETALLE_SUBUNIDADES_SATURACION.png": "Las áreas del Centro",
    "R15_DETALLE_NUCLEO_PERIFERIA.png": "El núcleo de Devoto",
    "R19_DETALLE_LACROZE_CABILDO.png": "Los dos tramos de Lacroze",
    "R20_DETALLE_CABILDO_PARQUE_SAAVEDRA.png": "García del Río y Parque Saavedra",
}

# Rótulos de mapa que nombraban un objeto interno del proyecto en vez del territorio.
# El de La Paternal venía del encargo anterior. Los cuatro de la Costanera aparecieron en
# la revisión visual de esta corrida: el mapa los rotulaba «Componente 1» a «Componente 4»,
# que no es un nombre. Se usa la palabra que la propia ficha emplea —«tramo»—; no se les
# inventa un nombre de lugar, que sería una decisión territorial. La edición técnica
# conserva el rótulo original.
ROTULOS_MAPA = {
    "Red occidental de calles documentadas": "Sector oeste de La Paternal",
    "Componente 1": "Tramo 1",
    "Componente 2": "Tramo 2",
    "Componente 3": "Tramo 3",
    "Componente 4": "Tramo 4",
}

# ---------------------------------------------------------------------------------------
# Apertura
# ---------------------------------------------------------------------------------------

# Corrección editorial 2026-08-04, observación «agregar qué es el atlas y/o el objetivo».
# Primer párrafo del resumen ejecutivo, antes de todo lo demás: el lector que abre el
# documento sin conocer el proyecto no sabía qué tenía delante ni para qué existe.
QUE_ES_UN_ATLAS = (
    "Un atlas es un conjunto ordenado de mapas y fichas sobre un mismo tema. El objetivo de "
    "este es dar a la Dirección y a sus áreas una referencia común sobre la gastronomía de la "
    "Ciudad: dónde se concentra la oferta, cómo es cada lugar y con qué información se cuenta "
    "sobre cada uno."
)

# Segundo párrafo de apertura, también escrito en el Doc la noche del 2026-08-04. Va detrás
# de `QUE_ES_UN_ATLAS` y antes de la caja «Lo que muestra este Atlas»: primero qué es un
# atlas, después qué reúne éste en concreto.
ATLAS_REUNE = (
    "Este Atlas reúne las 22 zonas gastronómicas que la Dirección identificó en la Ciudad: "
    "dónde está cada una, cuánta oferta se relevó en ella y cómo es ese lugar."
)

# ---------------------------------------------------------------------------------------
# Nombrar la fuente · decisión de Diego del 2026-08-05
#
# Se dice que la fuente es Google Places, aclarando que es información de Google. Se termina
# el eufemismo «directorio comercial en línea», que además no le decía nada al lector: un
# nombre de método no explica por qué un grupo da números tres veces más grandes que otro.
#
# Los cuatro grupos pasan a nombrarse por CUÁNTAS FUENTES SE CRUZARON, y con eso la salvedad
# «estos números no se comparan» deja de ser una afirmación que hay que creer: 907 salió de dos
# fuentes y 189 de una, y eso se lee solo.
#
# NINGUNA CIFRA SE MUEVE. Cambian nombres de grupo y frases explicativas.
#
# Contesta además dos comentarios abiertos de Patricia sobre esta misma página: el `[c]`
# —«cuáles son las formas de relevo y conteo?»— y el `[d]` —«a qué se llama directorio?»—.
#
# El detalle pasaje por pasaje está en
# `outputs/BARRIDO_CIUDAD_2026-08/REESCRITURA_NOMBRAR_LA_FUENTE.md`.
# ---------------------------------------------------------------------------------------

GRUPOS_RESUMEN = [
    ("Zonas contadas cruzando dos fuentes",
     "Caballito 907 · Villa Crespo 646 · Chacarita 327 · Boulevard Caseros 66",
     "Se cruzaron los datos abiertos del Gobierno de la Ciudad —el listado de oferta "
     "gastronómica y el padrón de habilitaciones— con la información de comercios de Google, y "
     "se contó una sola vez a los locales que aparecían en las dos. No son locales abiertos hoy."),
    ("Zonas contadas sólo con la información de Google",
     "Villa Urquiza 189 · Devoto 119 · Avenida Boedo 79 · Donado–Holmberg 40",
     "Google Places es el servicio que reúne los comercios que aparecen en Google Maps, con "
     "nombre, rubro y dirección. Es una fuente privada, no oficial: incluye a los locales que "
     "tienen presencia en Google y deja afuera a los que no la tienen. Acá se usó sola, sin "
     "cruzarla con los datos abiertos, y por eso estos números no se comparan con los del grupo "
     "anterior: no indican menos oferta, están construidos con menos fuentes."),
    ("Zonas con un mínimo, porque la búsqueda llegó a su tope",
     "Centro y Microcentro 797 · Abasto 314 · La Paternal 254 · Esmeralda–Paraguay 216 · "
     "Federico Lacroze 211 · Villa Pueyrredón 158 · García del Río 40",
     "El servicio consultado devuelve una cantidad máxima de resultados por consulta. Donde se "
     "alcanzó ese tope, el conteo quedó incompleto y el número se escribe con «al menos»: puede "
     "haber más locales, nunca menos. Nunca se estimó lo que faltaba."),
    ("Zonas sin conteo propio",
     "Palermo · Avenida Corrientes · San Telmo · Puerto Madero · Recoleta",
     "Están descriptas y ubicadas. Belgrano y Costanera Norte solo tienen datos de un "
     "relevamiento anterior: 697 y 72."),
]

NOTA_GRUPOS = (
    "Las zonas no se contaron todas igual, y por eso sus números no se comparan entre sí. En "
    "unas se cruzaron dos fuentes; en otras se usó una sola; en otras la búsqueda llegó a su "
    "tope y el número quedó como un mínimo; y en otras alcanzó para describir el lugar pero no "
    "para contarlo. Los cuatro grupos que siguen ordenan las zonas según cuál de esas formas se "
    "usó. Un número más alto no significa más oferta que en otra zona: significa que se contó "
    "con más fuentes o de otra manera. Los números tampoco se suman entre sí."
)

FUENTE_UNICA = (
    "Fuente: relevamiento propio de la Dirección General de Desarrollo Gastronómico. "
    "Los datos corresponden a julio de 2026."
)

CAJA_USO = (
    "El mapa general, unas páginas más adelante, ubica las 22 zonas en la Ciudad. Cada zona "
    "tiene después una ficha y un mapa propios. Las áreas dibujadas envuelven los locales que "
    "se relevaron en cada zona: muestran dónde se encontró la oferta y cómo está repartida. "
    "Son una lectura de trabajo, no un límite oficial, un padrón de locales ni una "
    "recomendación comercial."
)

# ---------------------------------------------------------------------------------------
# M-04 · Una sola capa de mayúsculas
#
# La V2.1 apilaba cuatro: el encabezado de sección, los títulos de caja, los sufijos de
# página y los enlaces. Queda en versalitas el encabezado de sección —el rótulo de
# navegación que se repite arriba de cada página— y todo lo demás pasa a capitalización
# normal, distinguido por peso y por color. Un título en negrita se lee igual y no grita.
# ---------------------------------------------------------------------------------------

CAJA_QUE_MUESTRA_TITULO = "Lo que muestra este Atlas"
CAJA_USO_TITULO = "Cómo usar este Atlas"
CAJA_FAMILIAS_TITULO = "Sobre esta clasificación"
CAJA_CIERRE_TITULO = "En una línea"
TITULO_GRUPOS = "Dónde se concentra la oferta relevada"

# B6 · la página de lectura pasa de ocho cajas de método a tres ideas.
COMO_LEER = [
    ("Qué es una zona de este Atlas",
     "Cada una de las 22 zonas es un lugar de la Ciudad donde la Dirección identificó oferta "
     "gastronómica con carácter propio. Algunas son barrios, otras una avenida o un tramo de "
     "calle, y otras un conjunto de partes separadas. No forman un ranking ni son 22 polos "
     "equivalentes."),
    ("Por qué los números de distintas zonas no se comparan entre sí",
     "Cada zona se contó con las fuentes que había disponibles para ella, y con su propia fecha. "
     "Un número más alto no significa más oferta que en otra zona: puede significar simplemente "
     "que se contó con más fuentes. Tampoco se suman entre sí. Cuando el número viene con «al "
     "menos», es un mínimo: puede haber más locales, nunca menos."),
    ("Qué son las áreas de los mapas",
     "El área de cada mapa envuelve los locales que se relevaron en esa zona: muestra hasta "
     "dónde llegó la oferta encontrada y cómo está repartida. Su forma sigue a los locales y "
     "no al límite del barrio, y su tamaño depende de cuán separados estén entre sí: un área "
     "grande puede corresponder a pocos locales muy dispersos. Es una lectura de trabajo, no "
     "un límite oficial."),
]

CAJA_FAMILIAS = (
    "La familia describe la forma de estar en el territorio, no la importancia ni el tamaño. "
    "Ninguna familia agrupa cifras: los números de cada zona siguen sin sumarse entre sí."
)

# B5 · la página que reemplaza a los seis anexos que se fueron a la edición técnica.
COMO_SE_HIZO_TITULO = "Cómo se hizo este Atlas y qué no dice"

COMO_SE_HIZO = [
    "El Atlas reúne 22 zonas de la Ciudad donde la Dirección identificó oferta gastronómica "
    "con carácter propio. Cada zona se estudió por separado y con la información disponible "
    "para ella. Las dos fuentes del conteo son los datos abiertos del Gobierno de la Ciudad —el "
    "listado de oferta gastronómica del Ente de Turismo y el padrón de habilitaciones de la "
    "Agencia Gubernamental de Control— y la información de comercios de Google Places. En "
    "algunas zonas se cruzaron las dos, en otras se usó sólo una, y en otras alcanzó para "
    "describir el lugar pero no para dar un número.",
    "Los números cuentan locales relevados en julio de 2026. No son un padrón, no dicen "
    "cuántos locales están abiertos hoy y no se pueden sumar entre zonas.",
    "Cuando un número viene con «al menos», el relevamiento llegó a su tope y quedó "
    "incompleto: hay por lo menos esa cantidad y puede haber más. Nunca se estimó lo que faltaba.",
    "Los contornos de los mapas envuelven los locales relevados en cada zona. Ninguno es un "
    "límite oficial ni fue adoptado como tal, y el tamaño del área no mide cantidad de oferta.",
    "El Atlas no ordena las zonas de mejor a peor, no indica dónde conviene invertir y no "
    "reemplaza a ningún registro oficial.",
    # Párrafo nuevo (2026-08-05). El cierre decía qué NO dice el Atlas sobre las zonas y no
    # decía nada sobre el límite de las fuentes mismas. Nombrada la fuente, corresponde decir
    # también qué se queda afuera de las dos, y decirlo como límite del trabajo y no como
    # afirmación sobre ningún local.
    "Ninguna de las dos fuentes es un censo de la gastronomía de la Ciudad. Los datos abiertos "
    "registran trámites, no locales abiertos. Google conoce a los comercios que tienen presencia "
    "en Google, y no a los que no la tienen. Un local sin trámite reciente y sin ficha en Google "
    "no aparece en este Atlas, y eso es un límite del trabajo, no una afirmación sobre ese local.",
    "El detalle completo del método, con todas las salvedades del trabajo, está en la edición "
    "técnica de este mismo Atlas.",
]

# B5 · Anexo A, única tabla que sobrevive. Encabezados en castellano.
# M-06 · Cuatro columnas: la de "Qué mide la cifra" repetía lo que ya dice la frase de
# cifra, y en cinco de las once filas lo decía con las mismas palabras.
ANEXO_A_ENCABEZADOS = ["Ref.", "Zona", "Qué tipo de zona es", "Cuánta oferta hay"]

ANEXO_A_PIE = (
    "Los números de distintas zonas no se comparan entre sí ni se suman: cada uno se obtuvo "
    "de otra manera. La ficha de cada zona explica qué cuenta su número y qué hay que tener "
    "en cuenta."
)
