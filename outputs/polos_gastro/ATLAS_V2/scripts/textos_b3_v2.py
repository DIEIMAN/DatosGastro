#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bloque B3 — el bloque inferior de las 29 paginas de mapa, en castellano llano.

Reemplaza "Lectura y limites", "Convenciones comunes", "Caveat geometrico" y
"Fuente/version" por tres lineas rotuladas, identicas en estructura en todas las paginas:

    Que muestra este mapa · Que mide la cifra · Que no es

Cada linea se deriva del contenido ya existente en el JSON canonico. El campo `fuente`
de cada trio registra de que campo salio, y alimenta qa/TRAZABILIDAD_TEXTOS_B3.csv.

Reglas de redaccion respetadas en las 22:
- nunca "locales activos";
- se mantiene la distincion entre cifra exacta, cota inferior, antecedente historico y
  ausencia de cifra comparable;
- cuando no hay cifra comparable, la linea del medio lo dice EN POSITIVO;
- el area es aproximacion de lectura territorial, dicho UNA sola vez por pagina.
"""

APROX = "El área es una aproximación de lectura territorial, no un límite oficial"

TRIOS = {
    "R01": dict(
        muestra="Área aproximada del polo de Palermo, con sus tres subzonas de identidad propia: Palermo Soho, Palermo Hollywood y Las Cañitas.",
        mide="Referencia caracterizada; sin conteo comparable entre métodos. Las subzonas se leen juntas, pero no existe un universo único cerrado para el polo completo.",
        no_es=f"{APROX}. Las discontinuidades entre subzonas son parte de la lectura y no se cierran en un polígono único.",
        fuente="caracterizacion[0]; cifra; denominador_metodo; limitaciones_especificas[0]"),
    "R02": dict(
        muestra="Corredor aproximado sobre la avenida Corrientes, en su tramo cultural y gastronómico entre 9 de Julio y Callao.",
        mide="Referencia caracterizada; sin conteo comparable entre métodos.",
        no_es=f"{APROX}. El vínculo con Abasto es contextual: no son la misma referencia ni se fusionan.",
        fuente="caracterizacion[0]; cifra; limitaciones_especificas[0]"),
    "R03": dict(
        muestra="Área aproximada del polo de San Telmo, sobre el casco histórico, con el Mercado de San Telmo como hito y el eje Defensa como organizador.",
        mide="Referencia caracterizada; sin conteo comparable entre métodos.",
        no_es=f"{APROX}. La asociación con Boulevard Caseros no implica que sean una sola referencia.",
        fuente="caracterizacion[0]; cifra; limitaciones_especificas[0]"),
    "R04": dict(
        muestra="Área aproximada del polo de Puerto Madero, sobre la banda de docks y el frente costero.",
        mide="Referencia caracterizada; sin conteo comparable entre métodos.",
        no_es=f"{APROX}. El área excluye el espejo de agua de los cuatro diques, descontado con cartografía pública de acceso abierto validada contra la capa oficial de cuerpos de agua de la Ciudad.",
        fuente="caracterizacion[0]; cifra; denominador_metodo; DECISIONES_AUTONOMAS_V2 D-A-10"),
    "R05": dict(
        muestra="Área aproximada del polo de Belgrano, con sus tres centralidades: Barrio Chino–Belgrano C, Cabildo–Juramento y Belgrano R.",
        mide="697 registros de un relevamiento cartográfico previo. Es un antecedente histórico y metodológico, no la cifra vigente del polo.",
        no_es=f"{APROX}. El antecedente de 697 no equivale a locales en actividad hoy ni se compara con las cifras de otras referencias.",
        fuente="caracterizacion[0]; cifra; detalle_cuantitativo[0]; limitaciones_especificas[0]"),
    "R06": dict(
        muestra="Área aproximada del polo de Recoleta, presentada como una unidad territorial continua.",
        mide="Referencia caracterizada; sin conteo comparable entre métodos.",
        no_es=f"{APROX}. La diversidad interna del polo no se publica como una lista de núcleos.",
        fuente="caracterizacion[0]; cifra; limitaciones_especificas[0]"),
    "R07": dict(
        muestra="Área aproximada del polo multiparte de Costanera Norte, formado por cuatro componentes separados a lo largo del frente costero.",
        mide="72 registros de un relevamiento cartográfico previo conciliado. Es un antecedente histórico y metodológico.",
        no_es=f"{APROX}. Los vacíos entre componentes son reales: no se unen artificialmente.",
        fuente="caracterizacion[0]; cifra; detalle_cuantitativo[0]; limitaciones_especificas[0]"),
    "R08": dict(
        muestra="Área aproximada de concentración gastronómica en Villa Crespo, sobre los ejes Thames y Gurruchaga.",
        mide="646 registros relevados con deduplicación conservadora. No equivale a locales en actividad hoy.",
        no_es=f"{APROX}. Villa Crespo tiene identidad propia respecto de Palermo y Chacarita, y no se absorbe con ellas.",
        fuente="caracterizacion[0]; cifra; detalle_cuantitativo[0]; limitaciones_especificas[0]"),
    "R09": dict(
        muestra="Los dos focos gastronómicos independientes de Chacarita: Jorge Newbery y Dorrego.",
        mide="327 registros relevados en Chacarita con deduplicación conservadora; el mapa muestra los dos focos identificados, no la totalidad de los registros. No equivale a locales en actividad hoy.",
        no_es=f"{APROX}. Los focos no forman una envolvente común ni un polo único, y no se funden con Palermo, Villa Crespo ni Federico Lacroze.",
        fuente="caracterizacion[0]; cifra; detalle_cuantitativo[0]; limitaciones_especificas[0]; DECISIONES_AUTONOMAS_V2 D-A-03"),
    "R10": dict(
        muestra="Los dos núcleos gastronómicos de Caballito: Pedro Goyena y Primera Junta–Mercado del Progreso.",
        mide="907 registros relevados en Caballito con deduplicación conservadora; el mapa muestra los dos núcleos identificados, no la totalidad de los registros. No equivale a locales en actividad hoy.",
        no_es=f"{APROX}. Los núcleos son independientes y no forman una envolvente única; Parque Rivadavia fue retirado de la lectura vigente.",
        fuente="caracterizacion[0]; cifra; detalle_cuantitativo[0]; limitaciones_especificas[0]; DECISIONES_AUTONOMAS_V2 D-A-03"),
    "R11": dict(
        muestra="Área aproximada de la microcentralidad de Boulevard Caseros, un tramo corto vinculado al entorno de Lezama y San Telmo.",
        mide="66 registros relevados con deduplicación conservadora. No equivale a locales en actividad hoy.",
        no_es=f"{APROX}. La evidencia no sostiene un corredor continuo, y la lectura no se extiende a Parque Patricios ni Barracas.",
        fuente="caracterizacion[0]; cifra; detalle_cuantitativo[0]; limitaciones_especificas[0]"),
    "R12": dict(
        muestra="Las subunidades independientes del área gastronómica del Centro y el Microcentro, cada una con su propio entorno de referencia.",
        mide="Al menos 797 establecimientos únicos. Es un piso de lo censado, no un conteo completo ni locales en actividad hoy.",
        no_es=f"{APROX}. No es un polo único del Centro: las subunidades no se suman entre sí porque comparten establecimientos.",
        fuente="caracterizacion[0]; cifra; detalle_cuantitativo[0]; denominador_metodo"),
    "R13": dict(
        muestra="Área aproximada del polo de Abasto, sobre el tramo de avenida Corrientes al que se asocia.",
        mide="Al menos 314 establecimientos. Es un piso de lo censado, no un conteo completo ni locales en actividad hoy.",
        no_es=f"{APROX}. Abasto es independiente de la referencia de avenida Corrientes y su delimitación es provisional.",
        fuente="caracterizacion[0]; cifra; detalle_cuantitativo[0]; limitaciones_especificas[0]"),
    "R14": dict(
        muestra="Área aproximada del eje gastronómico de avenida Boedo, fragmentado a lo largo de la avenida.",
        mide="79 registros de un directorio comercial en línea, con deduplicación conservadora. No equivale a locales en actividad hoy.",
        no_es=f"{APROX}. La continuidad cultural de la avenida no equivale a un corredor gastronómico continuo.",
        fuente="caracterizacion[0]; cifra; detalle_cuantitativo[0]; limitaciones_especificas[0]"),
    "R15": dict(
        muestra="Área aproximada del polo de Devoto, con su núcleo estable en torno de Plaza Arenales.",
        mide="119 registros de un directorio comercial en línea, con deduplicación conservadora. No equivale a locales en actividad hoy.",
        no_es=f"{APROX}. La periferia del polo no está estabilizada y la lectura no se extiende a Villa Pueyrredón ni Villa del Parque.",
        fuente="caracterizacion[0]; cifra; detalle_cuantitativo[0]; limitaciones_especificas[0]"),
    "R16": dict(
        muestra="Área aproximada del doble eje de Donado y Holmberg, fragmentado por tramos.",
        mide="40 registros de un directorio comercial en línea, con deduplicación conservadora. No equivale a locales en actividad hoy.",
        no_es=f"{APROX}. No forma una envolvente única ni se fusiona con Villa Urquiza.",
        fuente="caracterizacion[0]; cifra; detalle_cuantitativo[0]; limitaciones_especificas[0]"),
    "R17": dict(
        muestra="Área aproximada del polo de Villa Urquiza. De sus tres ejes internos —Triunvirato, Monroe y Congreso— el mapa ubica el de Triunvirato, único con trazado cerrado en el corpus.",
        mide="189 registros de un directorio comercial en línea, con deduplicación conservadora. No equivale a locales en actividad hoy.",
        no_es=f"{APROX}. Villa Urquiza no absorbe la referencia de Donado y Holmberg.",
        fuente="caracterizacion[0]; cifra; detalle_cuantitativo[0]; limitaciones_especificas[0]; DECISIONES_AUTONOMAS_V2 BLOQUEADO-02"),
    "R18": dict(
        muestra="Área de consulta de 400 metros en torno del cruce de Esmeralda y Paraguay.",
        mide="Al menos 216 establecimientos. Es un piso de lo censado, no un conteo completo ni locales en actividad hoy.",
        no_es=f"{APROX}. El círculo es el radio con que se consultó la zona, no un núcleo demostrado: la referencia no tiene centro radial probado.",
        fuente="caracterizacion[0]; cifra; detalle_cuantitativo[0]; regla_construccion GA-R18-CS07; DECISIONES_AUTONOMAS_V2 D-5a"),
    "R19": dict(
        muestra="Los dos tramos independientes de la referencia de Federico Lacroze, entre Libertador y Cabildo y entre Cabildo y Álvarez Thomas.",
        mide="Al menos 211 establecimientos, de los cuales 204 figuran en actividad y 7 cerrados temporalmente. Es un piso de lo censado.",
        no_es=f"{APROX}. Los dos tramos no son comparables entre sí y sus cifras no se suman; la referencia no se funde con Chacarita.",
        fuente="caracterizacion[0]; cifra; detalle_cuantitativo[0]; denominador_metodo"),
    "R20": dict(
        muestra="Tramo aproximado de oferta continua y modesta sobre García del Río, entre Cabildo y Parque Saavedra.",
        mide="Al menos 40 establecimientos. Es un piso de lo censado, no un conteo completo ni locales en actividad hoy.",
        no_es=f"{APROX}. El tramo no se prolonga antes de Cabildo ni dentro del parque, y no constituye un corredor.",
        fuente="caracterizacion[0]; cifra; detalle_cuantitativo[0]; observaciones GC-R20-BASE"),
    "R21": dict(
        muestra="Área aproximada de la referencia de La Paternal, extensa y dispersa sobre una red de calles documentadas.",
        mide="Al menos 254 establecimientos, de los cuales 242 figuran en actividad y 12 cerrados temporalmente. Es un piso de lo censado.",
        no_es=f"{APROX}. No tiene un núcleo único demostrado ni geometría estabilizada, y no absorbe el borde de Villa Crespo.",
        fuente="caracterizacion[0]; cifra; detalle_cuantitativo[0]; denominador_metodo"),
    "R22": dict(
        muestra="Marco de relevamiento de Villa Pueyrredón, con la oferta distribuida de manera extensa y heterogénea.",
        mide="Al menos 158 establecimientos. Es un piso de lo censado, no un conteo completo ni locales en actividad hoy.",
        no_es=f"{APROX}. El contorno es el marco con que se relevó el barrio, no un área gastronómica: la mayor densidad del centro y centro-este es una descripción, no un núcleo adoptado.",
        fuente="caracterizacion[0]; cifra; detalle_cuantitativo[0]; rol GC-R22-FRAME; DECISIONES_AUTONOMAS_V2 D-5b"),
}

# Vistas de detalle: mismo bloque de tres lineas, referido a lo que amplia cada vista.
TRIOS_DETALLE = {
    "R01_DETALLE_LAS_CANITAS.png": dict(
        muestra="Ampliación de Las Cañitas, una de las tres subzonas del polo de Palermo.",
        mide="Referencia caracterizada; sin conteo comparable entre métodos.",
        no_es=f"{APROX}. Las Cañitas no representa por sí sola al conjunto de Palermo.",
        fuente="complementarias[R01]; caracterizacion[0] de R01"),
    "R02_R13_CONTEXTO_CORRIENTES_ABASTO.png": dict(
        muestra="Vista conjunta del corredor de avenida Corrientes y del polo de Abasto, para mostrar su relación espacial.",
        mide="Ninguna de las dos referencias tiene conteo comparable con la otra.",
        no_es=f"{APROX}. La vecindad no las convierte en una sola referencia: son vínculo y asociación, no equivalencia ni fusión.",
        fuente="complementarias[R02]; limitaciones_especificas de R02 y R13"),
    "R08_DETALLE_SATURACIONES_RESIDUALES.png": dict(
        muestra="Los tres puntos de Villa Crespo donde el relevamiento alcanzó su tope de resultados y no pudo seguir contando.",
        mide="646 registros relevados en Villa Crespo; en esos tres puntos el conteo quedó incompleto por tope de la consulta.",
        no_es=f"{APROX}. Los tres círculos marcan un límite del relevamiento, no una concentración de oferta.",
        fuente="complementarias[R08]; SATURACIONES_RESIDUALES_CATEGORY_SPLIT_V4_4.csv"),
    "R12_DETALLE_SUBUNIDADES_SATURACION.png": dict(
        muestra="Las subunidades del Centro y el Microcentro ampliadas, cada una con su nombre.",
        mide="Al menos 797 establecimientos únicos en el conjunto. Cada subunidad tiene su propio piso, y 143 establecimientos pertenecen a dos subunidades a la vez.",
        no_es=f"{APROX}. Las subunidades no se suman entre sí ni se ordenan en un ranking, porque comparten establecimientos.",
        fuente="complementarias[R12]; detalle_cuantitativo[0] de R12"),
    "R15_DETALLE_NUCLEO_PERIFERIA.png": dict(
        muestra="El polo de Devoto ampliado. Su núcleo estable se organiza en torno de Plaza Arenales; el mapa no lo delimita como pieza propia.",
        mide="119 registros de un directorio comercial en línea, con deduplicación conservadora.",
        no_es=f"{APROX}. El corpus no cerró un trazado propio para el núcleo, así que el mapa muestra el polo completo y no delimita el núcleo.",
        fuente="complementarias[R15]; caracterizacion[0] de R15; DECISIONES_AUTONOMAS_V2 BLOQUEADO-03"),
    "R19_DETALLE_LACROZE_CABILDO.png": dict(
        muestra="Los dos tramos de Federico Lacroze en detalle, con su zona de contacto en torno de Cabildo.",
        mide="Al menos 211 establecimientos en el conjunto; cada tramo tiene su propio piso y no se suman.",
        no_es=f"{APROX}. Que los tramos se toquen no demuestra que la oferta sea continua entre ellos.",
        fuente="complementarias[R19]; denominador_metodo de R19"),
    "R20_DETALLE_CABILDO_PARQUE_SAAVEDRA.png": dict(
        muestra="El extremo de García del Río junto a Parque Saavedra, con el parque señalado como área de control.",
        mide="Al menos 40 establecimientos en el tramo. El parque no aporta registros: se usó para verificar que el tramo no se extendiera dentro de él.",
        no_es=f"{APROX}. El parque no integra la referencia.",
        fuente="complementarias[R20]; observaciones GC-R20-BASE"),
}
