# Cómo se describe un polo

**Diseño de la capa de enriquecimiento · 6 de agosto de 2026**

118 polos no se pueden describir a mano. Este documento define qué atributos lleva cada uno, de
dónde salen, qué se puede decir automáticamente y qué necesita una persona.

---

## 0 · Una decisión de fondo, antes de los atributos

**El Atlas nunca nombró un solo local.** Es una decisión sostenida en las 22 fichas: describe
zonas, no establecimientos. Cuando nombra algo concreto lo hace como **hito** —«el Mercado de
San Telmo es el hito de referencia de la zona»— y nunca como lista.

Eso no es un descuido, es lo que separa un atlas de un directorio. Un directorio implica dos
cosas que la Dirección no puede sostener: **completitud** —si figuran diez, ¿por qué no el
once?— y **respaldo** —si el Gobierno lo lista, ¿lo recomienda?—.

Así que la regla para esta capa:

> **Los notables y los Michelin entran como atributos del polo y como hitos, no como listado.**
> «Este polo incluye tres cafés notables» sí. Una tabla con los tres nombres, no — salvo que la
> Dirección decida cambiar la naturaleza del documento, que es una decisión suya y no técnica.

Hay una excepción natural y ya usada: **cuando un establecimiento es el hito que le da identidad
a la zona**, nombrarlo es describir el territorio, no listar oferta. El Mercado de San Telmo, el
Mercado del Progreso, Caminito. Uno o dos por polo, no diez.

---

## 1 · Los atributos, y de dónde salen

### 1.1 · Forma y tamaño — de la geometría

| atributo | fuente | para qué |
|---|---|---|
| superficie (ha) | envolvente | dimensionar |
| locales | base | dimensionar |
| densidad (locales/ha) | derivado | **clase de densidad**, por cortes naturales |
| elongación | envolvente | sugiere eje o corredor frente a mancha |
| número de partes | clustering | sugiere polo con subzonas |
| **`foco_menor`** | clustering + **decisión humana** | un foco secundario que **no** llega a subzona |
| barrios que toca | crosswalk | ubicar, y declarar añada del Relevamiento |

Las tres últimas alimentan la **familia territorial** —eje o corredor, polo, polo con partes,
área segmentada, referencia dispersa—, que el algoritmo *sugiere* y una persona confirma.

#### El `foco_menor`, y por qué no tiene umbral

Un polo puede tener adentro una pieza estable que **no corresponde publicar como subzona**. Ese
caso se registra como atributo y como **una línea en la ficha**, nunca como división del polígono.

**El campo no lleva umbral numérico, y es deliberado.** Belgrano —el precedente publicado, con
tres partes— tiene una pieza chica de 23 contra 107: **21,5 %**. P103 San Telmo tiene 44 contra
290: **15,2 %**. Seis puntos separan al precedente que se publica del caso que se rechaza, así
que cualquier corte por proporción deja a Belgrano a punto de caerse también. **La proporción es
evidencia, no criterio.**

Lo que decide es la **condición 3** de la regla de partes —nombre de uso corriente o respaldo
documental—, que por el §5 de `CRITERIOS_LECTURA_POLIGONIZACION` no la evalúa un algoritmo. El
campo registra por lo tanto una decisión humana con su motivo escrito, más la evidencia medible
que la sostiene: locales, proporción, calles, barrios y zona publicada encima.

Y **el foco se describe por sus calles, no por un nombre**. Ponerle nombre sería hacer exactamente
lo que la condición 3 dice que no corresponde: si tuviera nombre de uso corriente, sería subzona.

> **Caso registrado · P103 San Telmo.** Foco de 44 locales (12,9 % del polo) sobre Chacabuco,
> Estados Unidos e Independencia. Resuelto como **mención**, no como subzona: el Atlas publica R03
> San Telmo como «Polo» sin partes, la asimetría 290/44 es un satélite y no una pieza comparable,
> y el foco no tiene nombre de uso corriente. Evidencia en `borrador_polos/polos_foco_menor.csv`.
>
> Con una salvedad que viaja con la línea: **las calles salen de 24 de los 44 locales** —los que
> tienen dirección—. Nombran dónde está el foco; no son un recuento de oferta por calle.

### 1.2 · Composición — qué clase de gastronomía es

De la categoría normalizada de la base, agregada por polo. Es lo que permite distinguir un polo
de otro en una frase:

- **Perfil dominante**: la o las dos categorías que superan su participación esperada en la
  Ciudad. No la más numerosa en términos absolutos — los cafés ganan en todos lados y no
  distinguen nada. Lo informativo es la **sobre-representación**.
- **Diversidad**: si el polo se apoya en una categoría o en muchas.
- Ejemplo del tipo de frase que habilita: *«predominan las parrillas y la comida al paso, con
  una participación de cafés menor a la del promedio de la Ciudad»*.

### 1.3 · Antigüedad — de las fechas de habilitación

El padrón F02 tiene fecha de habilitación por registro, 2015–2025. Agregada por polo da un
perfil de antigüedad que distingue **oferta consolidada** de **oferta reciente**, que es una de
las cosas que la Dirección más va a querer saber y que hoy el Atlas no dice.

⚠ Con dos salvedades que van escritas: el padrón **no registra bajas**, así que mide altas y no
permanencia; y hay que **excluir los lotes replicados** —el 22,6 % del padrón— porque distorsionan
cualquier distribución temporal.

### 1.4 · Hitos y distinciones — la capa nueva

| capa | fuente | licencia | cómo se usa |
|---|---|---|---|
| **Bares Notables** | Wikidata (95 ítems) + declaratoria | CC0 | conteo por polo; y como hito cuando le da identidad |
| **Guía Michelin** | guía publicada (56 en Buenos Aires) | editorial, no redistribuible como dato | **sólo conteo**, nunca listado. Citar la guía como fuente |
| **Mercados y ferias** | BA Data | CC-BY | hito, casi siempre. Un mercado organiza un polo |
| **Espacios culturales · bares** | BA Data | CC-BY | conteo, y contexto cultural del polo |
| **Locales bailables** | AGC, BA Data | CC-BY | conteo. Distingue polos nocturnos |
| **Permisos de mesas y sillas** | BA Data | CC-BY | **indicador de vida en la vereda**, que ninguna otra capa da |

Sobre Michelin: el dato de que un polo contiene N establecimientos de la guía es un **hecho
citable**, no una reproducción de su contenido. Reproducir la lista sí sería otra cosa. Se cita
la guía y el año, como se cita cualquier fuente.

**El de mesas y sillas es el más subestimado.** Es el único que mide algo que no es cantidad de
locales sino **uso del espacio público** — y un polo con muchos permisos es cualitativamente
distinto de uno con los mismos locales y ninguno. Para una Dirección que trabaja sobre
desarrollo gastronómico, eso es más accionable que el recuento.

### 1.5 · Solidez — la columna que evita el falso brillo

Va en toda ficha, no en un anexo:

- número de fuentes independientes que sostienen el polo
- porcentaje de locales corroborados por más de una
- **parejidad de cobertura del barrio**
- **añada del Relevamiento de Usos del Suelo**
- resultado de las tres pruebas de artefacto

---

## 2 · Qué se genera solo y qué necesita una persona

| | automático | persona |
|---|---|---|
| Superficie, locales, densidad, clase | ✓ | |
| Composición y perfil dominante | ✓ | |
| Antigüedad | ✓ | |
| Conteos de notables, Michelin, mercados, permisos | ✓ | |
| Columna de solidez | ✓ | |
| **Familia territorial** | sugerida | **confirma** |
| **Nombre del polo** | | **decide** |
| **Cuál es el hito** | candidatos | **elige** |
| **Si el polo entra al Atlas** | | **decide** |
| **La frase de carácter** | borrador | **reescribe** |

La última fila importa. Un texto generado que diga «predomina la categoría X» es correcto y
suena a máquina. La ficha publicable necesita una pasada humana — es exactamente el trabajo que
se hizo sobre las 22 y que costó sacar 84 fórmulas repetidas. **No repitamos ese error a escala
118.**

Recomendación práctica: que el generador produzca **datos y viñetas**, no prosa. La prosa se
escribe encima. Un atlas de 118 fichas con párrafos autogenerados va a leerse exactamente como
lo que es.

---

## 3 · El orden que propongo

1. **Los atributos calculables**, sobre los 118 del borrador. No requiere ninguna decisión y
   deja ver de qué se está hablando.
2. **Cargar las capas de hitos** —notables, mercados, ferias, permisos, bailables, culturales— y
   contarlas por polo. Todas CC-BY o CC0, ninguna cuesta llamadas.
3. **Michelin a mano.** Son 56 y se cargan en una tarde con dirección; se geocodifica con USIG.
4. **Una tabla de 118 filas** con todo lo anterior. Ése es el entregable de esta etapa: no
   fichas, una tabla que permita decidir cuáles merecen ficha.
5. Recién ahí, elegir los que van al Atlas y escribirles el texto a mano.

**El paso 4 es el que hay que defender de la tentación de saltear.** Con 118 polos, la decisión
importante no es cómo se describe cada uno: es cuáles se describen. Una tabla ordenable resuelve
esa conversación en una reunión; 118 fichas la vuelven imposible.

---

## 4 · Dos advertencias para cuando esto se vea lindo

**Los hitos sesgan hacia el centro y el norte.** Los bares notables, los Michelin y los mercados
históricos están donde está el patrimonio reconocido. Un polo del sur puede ser perfectamente
real y no tener un solo hito. **La ausencia de hitos no es una debilidad del polo, es una
propiedad del reconocimiento** — y si la ficha no lo dice, el mapa va a reproducir el mismo
sesgo que acabamos de descubrir.

**Y el conteo de notables no mide calidad.** Mide declaratorias, que son actos administrativos
con su propia historia. Un polo con cuatro notables tiene cuatro edificios declarados; no tiene
mejor gastronomía que uno con cero.
