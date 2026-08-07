"""El normalizador de nombres de calle. Cuarto corte de la serie R8: **el orden de los tokens.**

POR QUÉ ESTE MÓDULO EXISTE, Y POR QUÉ NO VIVE MÁS ADENTRO DE `polos_foco_menor.py`
-----------------------------------------------------------------------------------
El normalizador se escribió adentro del script que medía el foco menor de P103, porque ahí fue
donde se necesitó por primera vez. Ese domicilio accidental es parte del problema: cada bicho de
la familia se arregló donde apareció, caso por caso, y el arreglo quedó enterrado en un script que
habla de otra cosa. Vive acá para que el próximo se arregle una sola vez.

EL CUARTO BICHO, LEÍDO DEL INVENTARIO
--------------------------------------
`INVENTARIO_NOMBRES_DE_CALLE.txt` bloque (B) dejó 46 grupos de sub-plegado. Sacando el residuo
declarado de las iniciales —que no se resuelve sin callejero canónico—, **el grupo grande que
queda es siempre la misma calle escrita en otro ORDEN**:

    ROOSEVELT FRANKLIN D      vs  FRANKLIN D ROOSEVELT      (26 direcciones)
    URIBURU JOSE E            vs  JOSE E URIBURU            (26)
    JUANA MANSO               vs  MANSO JUANA               (21)
    DEL BARCO CENTENERA       vs  BARCO DEL CENTENERA       (36 con la tercera forma)
    LINIERS VIRREY            vs  VIRREY LINIERS            (9)
    COSTANERA RAFAEL OBLIGADO vs  COSTANERA OBLIGADO RAFAEL (29)

Y la causa es exactamente la de Niceto Vega, con otra ropa: **la regla se apoya en una marca que
no siempre está.** La desinversión se dispara con la coma, y la coma falta o está en otro lugar:

    'ROOSEVELT FRANKLIN D.'         — invertido y SIN coma
    'MANSO JUANA'                   — invertido y SIN coma
    'URIBURU JOSE E., Pres.'        — hay coma, pero separa el tratamiento, no el apellido
    'OBLIGADO RAFAEL, Av.Costanera' — ídem
    'BARCO CENTENERA del'           — sin coma, y con el artículo corrido al final

EL ARREGLO ES DEJAR DE ADIVINAR EL ORDEN, NO ADIVINARLO MEJOR
---------------------------------------------------------------
No se puede saber, mirando `MANSO JUANA`, si el orden natural es ése o el otro: hace falta un
callejero, que es lo mismo que falta para las iniciales. Así que el arreglo **no decide el orden**:

  · para AGRUPAR   se usa `clave_calle()`, que es el **conjunto** de tokens. Dos formas de la
                   misma calle caen juntas sin que nadie declare cuál está bien escrita.
  · para PUBLICAR  se usa `ResolutorDeCalles`, que elige la etiqueta **con evidencia y no con una
                   regla de estilo**: el padrón (F01/F02/RUS/PERMISOS) escribe invertido; OSM,
                   Overture y ATP escriben en orden natural. Entre las formas del grupo se elige
                   la que usan las fuentes que NO invierten.

Sobre los 12 grupos que el corpus tiene hoy, la regla de la fuente acierta **12 de 12**, y en 5 de
ellos corrige a la mayoría simple —`ROOSEVELT FRANKLIN D` gana 19 a 7 y sin embargo está al
revés—. Por eso la etiqueta no se elige por frecuencia sola.

POR QUÉ LA CLAVE ES UN CONJUNTO Y NO UN MULTICONJUNTO
-------------------------------------------------------
Porque el conjunto **absorbe la regla del conector colgando** y así una regla se va en vez de
sumarse. `BARCO CENTENERA del` tiene el artículo corrido al final; el recorte de cola —que existe
porque «11 de Septiembre de 1888» pierde el año con la altura— se lo comía y lo dejaba en
`BARCO CENTENERA`, separado de `DEL BARCO CENTENERA`. Con el conjunto, `{11, DE, SEPTIEMBRE}` sale
igual con el «DE» colgando o sin él, y `{BARCO, CENTENERA, DEL}` sale igual con el artículo
adelante o atrás. Medido sobre el corpus: el conjunto pliega **3 grupos más** que el
multiconjunto —Barco Centenera, Del Valle Iberlucea, Manuel de Artigas— y **ninguno de más**.

LO QUE SIGUE SIN RESOLVERSE, Y ES LA MISMA RAZÓN DE SIEMPRE
-------------------------------------------------------------
Las **iniciales** (`RAMON L FALCON` / `RAMON FALCON`, `S MARTIN` / `SAN MARTIN`) siguen contándose
aparte. El conjunto no las pliega porque la inicial es un token más, y está bien que no las
pliegue: tirar las letras sueltas rompería `S. MARTIN`, que es *San* Martín. Y los **artículos de
cabeza** (`LA PAMPA` / `PAMPA`, `DE LOS CONSTITUYENTES` / `CONSTITUYENTES`) tampoco: ahí la forma
larga es el nombre real y la corta es un recorte de quien cargó el dato, y plegarlos sería
sobre-plegar. Las dos cosas esperan callejero, declaradas, y no se adivinan.

Google Places: 0 requests. Este módulo no lee ni escribe datos: transforma texto.
"""
from __future__ import annotations

import re
import unicodedata
from collections import Counter
from typing import Iterable

# Palabras que no son el nombre de la calle, como pares abreviatura → forma larga.
#
# El par es la estructura y no una lista suelta, porque **una abreviatura sin su forma larga parte
# la calle en dos**: la tabla tenía `DR` y no `DOCTOR`, así que «VALLE IBERLUCEA del, Dr.» y
# «Doctor del Valle Iberlucea» caían en claves distintas. Es el mismo bicho una vez más, y con el
# par explícito no puede volver por olvido —falta un lado y se ve—.
#
# Se comparan como TOKEN ENTERO y no como prefijo: así el bug de la familia «Esquiu» —«AV»
# matcheando adentro de «AVELLANEDA»— no puede volver, porque es igualdad y no subcadena.
MARCADORES_PAREADOS = {
    "AV": "AVENIDA", "AVDA": "AVENIDA", "AVE": "AVENIDA",
    "PJE": "PASAJE",
    "CNEL": "CORONEL", "GRAL": "GENERAL", "TTE": "TENIENTE", "MCAL": "MARISCAL",
    "ALTE": "ALMIRANTE", "BRIG": "BRIGADIER", "INT": "INTENDENTE",
    "DR": "DOCTOR", "DRA": "DOCTORA", "PROF": "PROFESOR", "ING": "INGENIERO",
    "PTE": "PRESIDENTE", "PRES": "PRESIDENTE",
}
MARCADORES = set(MARCADORES_PAREADOS) | set(MARCADORES_PAREADOS.values()) | {"CALLE"}

# Abreviaturas que NO se tiran sino que se ESTIRAN, porque la palabra es parte del nombre y no un
# tratamiento: «STA FE» es Santa Fe, y sacarle el «Santa» dejaría «FE». Distinto mecanismo que los
# marcadores y por eso va aparte.
#
# `S` NO está acá a propósito: `S. MARTIN` es *San* Martín pero `S` es también una inicial, y las
# dos son indistinguibles sin callejero. Es el residuo declarado, y estirarlo lo rompería.
ABREVIATURAS_DE_NOMBRE = {"STA": "SANTA", "STO": "SANTO"}
# Conectores que sólo aparecen sueltos en un extremo cuando el nombre quedó recortado:
# «11 de Septiembre de 1888» pierde el año con la altura y termina en «DE». Se recortan para la
# ETIQUETA legible; la clave no los necesita porque es un conjunto.
CONECTORES_COLA = {"DE", "DEL", "Y", "LA", "EL"}
# Código postal argentino pegado al nombre: «BARTOLOME MITRE C1201AAX».
CPA = re.compile(r"^[A-Z]\d{4}[A-Z]{3}$")

# Las fuentes que asientan la calle INVERTIDA («CALVO, CARLOS»): el padrón de habilitaciones y sus
# derivados. Las demás —OSM, Overture, ATP— la escriben en orden natural. Esto no es una
# observación de estilo: es la convención de carga de cada fuente, y es lo que permite elegir la
# etiqueta sin decidir a mano cuál orden está bien.
FUENTES_QUE_INVIERTEN = {"F01", "F02", "RUS", "PERMISOS"}


def reparar_mojibake(texto: str, vueltas: int = 3) -> str:
    """Deshace una conversión de codificación equivocada, tantas veces como se haya aplicado.

    `ARRIBEÃ\\x83â\\x80\\x98OS` es «Arribeños» que pasó DOS veces por el mismo error: se leyó como
    cp1252 un texto que estaba en UTF-8, se volvió a guardar en UTF-8, y volvió a leerse mal. Se
    deshace igual que se hizo —volver a bytes y releer como UTF-8— hasta que deje de cambiar.

    El caso negativo es lo que lo vuelve seguro: «Cañitas» pasada a bytes da `F1`, que **no es
    UTF-8 válido**, así que el intento falla y el texto sano vuelve intacto. Sólo se transforma lo
    que efectivamente era mojibake, porque sólo el mojibake decodifica limpio.
    """
    for _ in range(vueltas):
        crudo = bytearray()
        for caracter in texto:
            try:
                crudo += caracter.encode("cp1252")
            except UnicodeEncodeError:
                try:
                    crudo += caracter.encode("latin-1")
                except UnicodeEncodeError:
                    return texto
        try:
            candidato = bytes(crudo).decode("utf-8")
        except UnicodeDecodeError:
            return texto
        if candidato == texto:
            return texto
        texto = candidato
    return texto


def tokens_calle(direccion: str) -> list[str]:
    """Los tokens del nombre de la calle, sin altura, sin marcadores y sin código postal.

    Seis convenciones mezcladas en el mismo campo, y cada una parte una calle en dos si no se
    pliega. Las seis están vistas en la base, con su volumen medido en
    `INVENTARIO_NOMBRES_DE_CALLE.txt`:

        «Carlos Calvo»  vs  «CALVO, CARLOS»              → se desinvierte la coma
        «INDEPENDENCIA AV.»  vs  «Avenida Independencia» → se saca el marcador, esté donde esté
        «Chacabuco»  vs  «CHACABUCO»                     → se pliega la caja
        «Arévalo»  vs  «Arevalo»                         → se pliegan las tildes
        «ARRIBEÃ\\x83â\\x80\\x98OS»  vs  «Arribeños»      → se repara el mojibake
        «BARTOLOME MITRE C1201AAX»                       → se tira el código postal pegado

    POR QUÉ EL MARCADOR SE SACA DE CUALQUIER POSICIÓN Y NO SÓLO DE LOS EXTREMOS
    ---------------------------------------------------------------------------
    Porque **la desinversión lo pone en el medio**, y ésa es la continuación exacta del bug de
    Niceto Vega. `CALVO, CARLOS AV.` tiene el marcador al final del último segmento; al dar vuelta
    los segmentos queda `CARLOS AV. CALVO`, con el «AV.» en el medio, donde ninguna regla de
    extremos lo alcanza. El inventario lo encontró 23 veces.

    El precio de sacar por posición libre sería el bug de «Esquiu», y no se paga: la comparación
    es de **token entero contra un conjunto**, no de prefijo, así que «AVELLANEDA» no puede
    matchear «AV» ni por accidente.
    """
    texto = reparar_mojibake(str(direccion))
    # El padrón asienta frentes de esquina en un solo campo: «CHILE 700;CHACABUCO 706».
    texto = texto.split(";")[0]
    texto = re.sub(r"\s+\d.*$", "", texto).strip()
    # Tildes: «Arévalo» y «Arevalo» son la misma calle y el campo trae las dos.
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    # La inversión puede tener MÁS DE UNA coma: «VEGA, NICETO, Cnel. AV.» es
    # «Avenida Coronel Niceto Vega». Se dan vuelta todos los segmentos, no sólo el primero.
    if "," in texto:
        texto = " ".join(s.strip() for s in reversed(texto.split(",")) if s.strip())
    # El punto separa tanto como el espacio: «AV.SAN MARTIN» viene sin espacio detrás del punto y
    # sin esto el marcador queda pegado al nombre y no se reconoce.
    tokens = [t for t in re.split(r"[\s.]+", texto.upper()) if t]
    tokens = [ABREVIATURAS_DE_NOMBRE.get(t, t) for t in tokens]
    return [t for t in tokens if t not in MARCADORES and not CPA.match(t)]


def calle(direccion: str) -> str:
    """La calle de una dirección, legible y en el orden en que vino. **Es una etiqueta candidata.**

    Sirve para mostrar, no para agrupar: dos formas de la misma calle en distinto orden devuelven
    dos cadenas distintas, que es justamente el cuarto bicho. Para agrupar va `clave_calle()`; para
    publicar, la etiqueta que elige `ResolutorDeCalles`.
    """
    tokens = tokens_calle(direccion)
    # Sólo en la cola: «11 DE SEPTIEMBRE DE» perdió el año, pero «DE LOS CONSTITUYENTES» empieza
    # así de verdad y recortarle el «DE» inventaría otra calle.
    while tokens and tokens[-1] in CONECTORES_COLA:
        tokens.pop()
    return " ".join(tokens)


def clave_calle(direccion: str) -> str:
    """La clave con la que dos escrituras de la misma calle caen juntas. **No se publica nunca.**

    Es el CONJUNTO de tokens, ordenado alfabéticamente para que sea comparable. Sale ilegible a
    propósito —`CENTENERA BARCO DEL`—: es una clave, y si alguna vez aparece en una salida es
    porque alguien la usó donde iba la etiqueta.

    El conjunto —y no el multiconjunto— es lo que hace que el conector colgando deje de importar:
    `{11, DE, SEPTIEMBRE}` sale igual con el «DE» de más o sin él.
    """
    return " ".join(sorted(set(tokens_calle(direccion))))


class ResolutorDeCalles:
    """Elige, para cada calle, la etiqueta que se publica — con la evidencia del corpus entero.

    Se construye UNA vez sobre toda la base y se aplica a cualquier subconjunto. Ese orden importa:
    si cada polo eligiera su etiqueta con sus propios locales, la misma calle podría salir
    «Juana Manso» en un polo y «Manso Juana» en el de al lado.
    """

    def __init__(self, direcciones: Iterable[str], fuentes: Iterable[str]) -> None:
        candidatas: dict[str, Counter] = {}
        candidatas_abiertas: dict[str, Counter] = {}
        for direccion, fuente in zip(direcciones, fuentes):
            if direccion is None or (isinstance(direccion, float)):
                continue
            clave = clave_calle(direccion)
            if not clave:
                continue
            etiqueta = calle(direccion)
            candidatas.setdefault(clave, Counter())[etiqueta] += 1
            if not (set(str(fuente).split(";")) & FUENTES_QUE_INVIERTEN):
                candidatas_abiertas.setdefault(clave, Counter())[etiqueta] += 1

        self.formas: dict[str, Counter] = candidatas
        self.etiquetas: dict[str, str] = {}
        self.base_de_la_etiqueta: dict[str, tuple[str, int]] = {}
        for clave, conteo in candidatas.items():
            abiertas = candidatas_abiertas.get(clave)
            if abiertas:
                # `most_common` desempata por orden de inserción; se ordena para que la etiqueta no
                # dependa del orden en que se leyó la base.
                elegida = max(sorted(abiertas), key=lambda e: abiertas[e])
                self.etiquetas[clave] = elegida
                self.base_de_la_etiqueta[clave] = ("fuente_no_invierte", sum(abiertas.values()))
            else:
                elegida = max(sorted(conteo), key=lambda e: conteo[e])
                self.etiquetas[clave] = elegida
                self.base_de_la_etiqueta[clave] = ("solo_padron_moda", sum(conteo.values()))

    def etiqueta(self, direccion: str) -> str:
        """La etiqueta publicable de una dirección. Cadena vacía si no hay calle legible."""
        clave = clave_calle(direccion)
        return self.etiquetas.get(clave, calle(direccion))

    def grupos_plegados(self) -> list[tuple[str, str, list[tuple[str, int]]]]:
        """Las claves que recibieron más de una escritura: lo que arregló el cuarto bicho.

        Devuelve `(clave, etiqueta_elegida, [(forma, n), …])` ordenado por volumen, para poder
        auditar de un vistazo qué se plegó y con qué etiqueta salió.
        """
        grupos = [(clave, self.etiquetas[clave],
                   sorted(conteo.items(), key=lambda kv: -kv[1]))
                  for clave, conteo in self.formas.items() if len(conteo) > 1]
        return sorted(grupos, key=lambda g: -sum(n for _, n in g[2]))


def resolutor_desde(tabla, columna_direccion: str = "direccion_norm",
                    columna_fuentes: str = "fuentes") -> ResolutorDeCalles:
    """Construye el resolutor desde un DataFrame con las dos columnas que hacen falta."""
    sub = tabla.dropna(subset=[columna_direccion])
    return ResolutorDeCalles(sub[columna_direccion].tolist(),
                             sub.get(columna_fuentes, "").tolist()
                             if columna_fuentes in sub.columns else [""] * len(sub))
