# -*- coding: utf-8 -*-
"""El normalizador de nombres de barrio, y el motivo por el que existe.

LA TRAMPA QUE VIENE A LEVANTAR
-------------------------------
La capa de barrios que el atlas venía usando escribe **«La Boca»**. La capa oficial escribe
**«Boca»**. Un cruce por nombre entre las dos **pierde el barrio entero y no falla**: devuelve
cero filas, el conteo de La Boca queda en cero y nada avisa. Es la misma familia de falla
silenciosa que este proyecto ya tiene contada varias veces —«Albariños» contra ALBARINO, «Boyacá»
y «Carabobo» siendo la misma avenida— y siempre cuesta lo mismo: un número de menos que nadie ve.

El segundo caso es la eñe. La capa oficial escribe **«NUÑEZ»** en mayúsculas y con eñe; la vieja,
**«Nuñez»**; el documento, **«Núñez»**. Un `==` entre cualquiera de los tres da False.

QUÉ HACE
--------
`clave(nombre)` devuelve una clave comparable: mayúsculas, sin tildes ni eñes, sin puntuación,
sin espacios repetidos, **y sin el artículo inicial** («LA BOCA» y «BOCA» dan la misma clave).

`igual(a, b)` compara dos nombres por su clave.

`emparejar(izquierda, derecha)` cruza dos listas de nombres y devuelve
`(pares, solo_izquierda, solo_derecha)`. **Lo que no empareja se devuelve, no se descarta**: un
cruce que pierde un barrio tiene que poder decir cuál.

QUÉ NO HACE
-----------
No adivina. Si dos barrios distintos colapsaran a la misma clave, `emparejar` lo levanta como
error en vez de elegir uno. Y las excepciones que no salen de la normalización —si alguna vez
aparece una— van en `EXCEPCIONES`, escritas, no metidas en la función.

Verificado el 10/08/2026 contra las dos capas: **48 y 48 barrios, 48 pares, cero sueltos.** El
único par que la normalización sola no habría emparejado es «La Boca» / «Boca», y lo resuelve la
regla del artículo inicial.
"""

import re
import unicodedata

# Artículos iniciales que las capas ponen o sacan sin criterio: «La Boca» / «Boca».
# No se sacan artículos en el interior del nombre —«Villa del Parque» los tiene y son parte
# del nombre—: sólo el primero.
ARTICULOS_INICIALES = ("LA ", "EL ", "LOS ", "LAS ")

# Equivalencias que la normalización no puede deducir. Está vacío a propósito: hoy no hace falta
# ninguna, y si mañana hace falta una tiene que estar escrita acá y no escondida en el código.
EXCEPCIONES: dict[str, str] = {}


def clave(nombre) -> str:
    """La clave comparable de un nombre de barrio."""
    if nombre is None:
        return ""
    texto = unicodedata.normalize("NFKD", str(nombre)).encode("ascii", "ignore").decode().upper()
    texto = re.sub(r"[^A-Z0-9 ]", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    for art in ARTICULOS_INICIALES:
        if texto.startswith(art):
            texto = texto[len(art):]
            break
    return EXCEPCIONES.get(texto, texto)


def igual(a, b) -> bool:
    return clave(a) == clave(b) and clave(a) != ""


def emparejar(izquierda, derecha):
    """Cruza dos colecciones de nombres por clave.

    Devuelve `(pares, solo_izquierda, solo_derecha)`, donde `pares` es una lista de
    `(nombre_izq, nombre_der)`. Levanta ValueError si dos nombres distintos de un mismo lado
    colapsan a la misma clave: ahí el cruce sería ambiguo y elegir uno sería inventar.
    """
    def indexar(nombres, lado):
        ix = {}
        for n in nombres:
            k = clave(n)
            if not k:
                continue
            if k in ix and ix[k] != n:
                raise ValueError(
                    f"dos nombres de {lado} colapsan a la clave «{k}»: «{ix[k]}» y «{n}». "
                    f"El cruce sería ambiguo; hay que resolverlo en EXCEPCIONES, no acá.")
            ix[k] = n
        return ix

    ii, di = indexar(izquierda, "la izquierda"), indexar(derecha, "la derecha")
    comunes = sorted(set(ii) & set(di))
    return ([(ii[k], di[k]) for k in comunes],
            sorted(ii[k] for k in set(ii) - set(di)),
            sorted(di[k] for k in set(di) - set(ii)))


def serie_normalizada(serie):
    """La versión pandas: aplica `clave` a una columna de nombres de barrio."""
    return serie.map(clave)
