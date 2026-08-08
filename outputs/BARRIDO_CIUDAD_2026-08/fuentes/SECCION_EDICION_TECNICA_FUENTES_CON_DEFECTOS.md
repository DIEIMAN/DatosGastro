# Fuentes con defectos conocidos

*Sección para la edición técnica · redactada el 7 de agosto de 2026 · datos en
`outputs/BARRIDO_CIUDAD_2026-08/fuentes/fuentes_defectos_conocidos.csv` y
`fuentes_marcas_aplicadas.csv`*

Un dato mal cargado se corrige en su fila. Lo que esta sección registra es distinto: fuentes donde
el defecto **es una propiedad del artefacto** y afecta a todo lo que salga de él, hoy y en cada
consulta futura. Sin un registro explícito, cada corrección se paga de nuevo cada vez que alguien
vuelve a citar la misma fuente.

Van cinco. Cada una tiene tres campos que hacen falta juntos: **cómo se detecta** —una regla que un
script puede evaluar, no una impresión—, **qué prohíbe afirmar** y **qué sigue valiendo**. Una regla
sin consecuencia declarada se convierte en una etiqueta decorativa; una consecuencia sin regla no se
puede aplicar sola.

*Actualizada el 7 de agosto de 2026 (ronda 6): entra FD-12 y FD-02 suma su tercera instancia. La
numeración salta de FD-04 a FD-12 porque FD-05 a FD-15 se identificaron en el material producido
afuera (`desde_cowork/evidencia_2026/`); acá sólo están las que ya pasaron a la capa canónica con su
evidencia.*

---

## FD-01 · El Cronista con fecha de actualización 24/09/2025

**Se detecta:** dominio `cronista.com` **y** `fecha_actualizacion = 2025-09-24`.

**Qué pasó.** Al menos tres notas con años de origen distintos llevan exactamente la misma fecha de
actualización: la del Mercado de los Carruajes, «5 lugares para comer bien y barato en el barrio
chino» (original de agosto de 2021) y la de Ultramarinos (original de septiembre de 2024). Tres
notas, tres años de origen, una sola fecha. Eso no es una nota desactualizada: es un **re-sellado
masivo del archivo**.

**La prueba está en la de los Carruajes:** actualizada el 24/09/2025, seguía recomendando dos
restaurantes adentro de un mercado que había cerrado cinco meses antes. La fecha de actualización no
acompañó ninguna revisión del contenido.

**Prohíbe:** leer esa fecha de actualización como fecha de verificación del dato.
**Sigue valiendo:** el contenido, con la añada de su fecha de **origen**.

**Dos precisiones que evitan aplicarla de más.** La marca es **dominio más fecha**, no fecha sola:
una nota de otro medio publicada el mismo día no está afectada. Y no alcanza el medio: la nota de El
Cronista sobre Los Laureles del 05/08/2026 se publicó 12:33 y se actualizó 12:34 — un minuto es una
corrección de redacción, no un re-sellado, y esa nota cuenta.

**Y una asimetría que hay que respetar.** Seis hitos de la capa salen de cronista.com y no tienen
fecha de actualización registrada por nosotros. **No encontrar la fecha no es haberla verificado
distinta**: quedan `pendiente_de_comprobacion`, que es un tercer estado y no un descarte encubierto.

---

## FD-02 · El catálogo consolidado de Bares Notables, en su campo territorial

**Se detecta:** cualquier uso del campo `barrio` o `comuna` del catálogo.

**Qué pasó.** El catálogo ubica La Academia en la Comuna 5. El normalizador del GCBA la pone en
Balvanera, Comuna 3. El error es verificable contra una fuente oficial del mismo Estado que publica
el catálogo.

**Prohíbe:** usar el barrio o la comuna del catálogo como dato territorial sin cotejarlo con USIG.
**Sigue valiendo:** la declaratoria, el nombre y la dirección postal.

Esto importa porque la matriz asigna hitos a filas por **punto**, y el punto sale de la dirección,
no del barrio declarado. Una fila que se arme por nombre de barrio hereda el error entero.

**Tercera instancia, y la que muestra el mecanismo (ronda 6).** El anexo asienta el Café Olimpo,
Irigoyen 1491, en **Villa Luro**. La calle Irigoyen atraviesa cuatro barrios y el catastro reparte
por altura: del 1 al 1299 el lado impar es Villa Luro, del **1301 al 1799 es Monte Castro** —el lado
par de ese tramo es Versalles— y del 1901 en adelante, Villa Real. El 1491 cae dos cuadras después
de que Villa Luro se termina. USIG sobre el punto responde Monte Castro, Comuna 10, y la esquina que
cita la ficha —Irigoyen y Arregui, resuelta por intersección de ejes del callejero, a 16 m del
punto— queda sobre el límite Monte Castro/Versalles, a 262 m de Villa Luro.

Lo que hace instructivo el caso es **por qué no se veía**: las tres son Comuna 10, así que la comuna
del anexo era correcta y el cotejo por comuna lo habría dado por bueno. El defecto es de barrio y
sólo se ve a escala de barrio. Las tres instancias —La Academia, Roma del Abasto, Café Olimpo—
comparten la forma: el campo territorial se llenó por nombre de calle o por zona aproximada, no por
altura.

---

## FD-03 · El PDF del catálogo servido bajo la URL de la Res. MCGC 3758/24

**Se detecta:** cualquier cita del catálogo que no venga con SHA-256 y fecha de descarga.

**Qué pasó.** Bajo la misma URL y el mismo número de resolución circulan contenidos distintos: el
que está en disco desde el 03/08/2026 trae **90 entradas** y una hoja de firmas del **26/02/2026**
(GEDO IF-2026-10314379-GCABA-DGPMYCH); la URL sirve hoy uno de **88**. A eso se suman las listas
independientes del GCBA (84) y de Wikidata (95).

**Prohíbe:** citar «el catálogo» sin decir cuál de los contenidos.
**Sigue valiendo:** cada contenido, citado por su hash y su identificador interno.

La consecuencia excede la cita. Si un documento firmado en febrero ya lista las doce altas, «alta del
3 de agosto» no describe el acto declaratorio. La resolución de las altas sigue sin localizarse, y
por eso las doce viajan con `declaratoria_localizada = "no · sólo prensa"`.

---

## FD-04 · Time Out Buenos Aires, en su campo de barrio

**Se detecta:** el barrio que declara una nota de Time Out.

**Qué pasó.** Tres direcciones mal asignadas, verificadas contra USIG en el control de bordes: Corte
Comedor —Time Out dice Núñez, USIG dice Belgrano—, Vereda Adentro y el tercer caso del mismo control.

**Prohíbe:** usar el barrio que declara Time Out como dato territorial.
**Sigue valiendo:** la distinción editorial y la dirección de puerta.

---

## FD-12 · Las marcas de cierre de Yelp, visibles e inauditables

**Se detecta:** el título del resultado de búsqueda expone `CLOSED - Updated <mes> <año>` y el
dominio bloquea por `robots.txt`, así que la ficha no se puede abrir.

**Qué pasó.** Yelp mostraba «EL BOLICHE DE ROBERTO - CLOSED - Updated July 2026» sobre Bulnes 331.
No hay manera de abrir la ficha para saber de cuándo es la marca ni de dónde salió. La tanda la
registró como señal a resolver y **no** la convirtió en veredicto, porque contradecía actividad de
usuario de fines de marzo de 2026.

**Y acá se probó.** Diego verificó el establecimiento **abierto el 07/08/2026**. La marca era falsa.

**Prohíbe:** leer la marca como evidencia de cierre, y también dejarla como duda que baje el
veredicto de una ficha.
**Sigue valiendo:** nada de la ficha — no se puede abrir.

**Por qué es la más incómoda de las cinco.** Las otras cuatro son errores del documento sobre sí
mismo: una fecha de actualización, un campo de barrio, un número de resolución. Ésta es una
**afirmación sobre el establecimiento**, del tipo que normalmente sí acreditaría, y encima en el
sentido que más cuesta ignorar: nadie duda de un «cerrado». La regla se sostiene por la asimetría
que ordena toda la verificación de vigencia —un abierto resuelve una ficha, un cerrado no cierra
nada— y ahora tiene detrás un caso medido, no una precaución.

---

## Cómo se usa esta sección

1. Antes de incorporar un dato, buscar su fuente acá. Si tiene marca, aplicar lo que la marca
   prohíbe **y** conservar lo que sigue valiendo: la marca no borra la fuente.
2. Cuando una marca se aplique a un registro concreto, dejarlo en `fuentes_marcas_aplicadas.csv` con
   el campo afectado y la consecuencia. Sin ese rastro, la marca vuelve a discutirse cada ronda.
3. Cuando una detección resulte falso positivo, **registrarla igual, marcada como tal**. La lista de
   lo que se decidió no marcar vale tanto como la de lo marcado: es lo que impide que la próxima
   ronda la vuelva a levantar.
4. Un defecto nuevo entra con los tres campos completos —regla, prohibición, evidencia—. Si no se
   puede escribir la regla, todavía no es un defecto de fuente: es un dato mal cargado.

**Y el criterio general, que es el que ordena casi todo lo anterior:** una fecha de actualización, un
campo de barrio o un número de resolución son **metadatos del artefacto**, no observaciones del
territorio. Ninguno de los cuatro primeros defectos es un error sobre un restaurante: los cuatro son
errores sobre cómo el documento se describe a sí mismo. Que sean todos del mismo tipo fue el
hallazgo de la ronda 4.

**FD-12 rompe el patrón, y conviene no disimularlo.** Es una afirmación sobre el establecimiento, no
sobre el documento, y resultó falsa. La lección no reemplaza a la anterior: la amplía. Los metadatos
no acreditan, y una afirmación de cierre que no se puede auditar tampoco — por más que suene a
observación del territorio.

---

## Ronda 8 · cuatro trampas nuevas, y una que no es de fuente

Las cuatro de la ronda 8 se separan del patrón anterior de una forma que conviene nombrar: **FD-01
a FD-04 eran errores del documento sobre sí mismo, FD-12 una afirmación falsa sobre un
establecimiento, y estas cuatro son sobre el CANAL** —dónde vive el dato, qué queda cuando el canal
se cae, y qué le pasa al dato cuando pasa por una redacción.

### FD-16 · el dato que sólo sobrevive en el slug de una URL

El portal `obras.buenosaires.gob.ar` fue retirado y hace 302 a mantenimiento. El tramo del CCCA de
Av. Montes de Oca —entre Benito Quinquela Martín y Av. Martín García— existe hoy **únicamente en el
slug de la URL canónica**, indexada y reaparecida en dos búsquedas independientes. El cuerpo no se
pudo abrir y no hay corroboración en prosa.

**La lectura de slugs entra como ruta de rescate, y se señala siempre como tal.** No es lo mismo que
haber leído la página: es haber leído cómo alguien la tituló. Sirve para no perder un dato que ya no
está en ningún lado, y no sirve como cita.

### FD-17 · cronista.com fabrica antigüedades

Dos notas del mismo dominio sobre El Puentecito dicen «hace 150 años» y «hace 200 años». El dominio
ya tenía FD-01 por re-sellado masivo de archivo: **además de re-sellar fechas, fabrica
antigüedades**. Ninguna de las dos cifras entra.

Es el defecto que obliga a la ficha de El Puentecito a hacer algo que conviene generalizar:
consignar **1750 como el SITIO** —pulpería y posta de carretas, dato del GCBA— y **~1876 como el
ESTABLECIMIENTO GASTRONÓMICO**, atribuyendo cada cifra a su fuente. Un local y el lugar donde está
no tienen por qué tener la misma edad, y sumarlas en un solo número es lo que produce el «200 años».

### FD-18 · reetiquetado editorial de una distinción real

Canal 26 llamó **«salón de la fama porteño»** a lo que es la lista de **Pizzerías Emblemáticas de
APyCE**. El reconocimiento existe y está verificado contra el sitio del organizador; el «salón de la
fama» no existe en ningún lado.

**Si se copia la etiqueta de prensa, el Atlas registra una institución inexistente**, y peor: una
que suena a padrón. Las distinciones entran con el nombre que les da su organizador, siempre.

### FD-19 · fichas vivas y momias con el mismo tono

La ficha del GCBA de El Puentecito fue editada el **20/02/2026**. La de Los Campeones lleva inerte
desde el **08/09/2021**, casi cinco años. **Las dos dicen frases institucionales del mismo estilo**,
y el tono no distingue una de otra: «todo un emblema de la identidad de Barracas» se lee igual de
firme venga de la ficha viva o de la momia.

Consecuencia operativa: **fechar ficha por ficha**, una por una, antes de usarla. El portal es el
mismo y el registro es el mismo; lo único que separa un dato de hoy de uno de hace cinco años es la
fecha de última modificación, que hay que ir a buscar.

---

## Una nota que no es de fuente, y va acá porque falla igual de callada

**`covers()` de GEOS devuelve `False` sobre geometrías cuya diferencia mide exactamente 0,0 m².**

Apareció verificando la regla de que las referencias publicadas sólo se amplían. El polígono nuevo
se construye como unión del viejo con la ampliación, así que contiene al viejo por construcción; el
predicado topológico igual dice que no. Medido en R19 y en R21: `vieja.difference(nueva).area` da
exactamente `0.0`, `difference` devuelve una geometría vacía, y `covers()` y `within()` devuelven
`False`. En R19 falla sobre **una de las tres partes** de la envolvente y acierta sobre las otras
dos. Es una falla de robustez de `relate` con vértices casi colineales, no un polígono que se
achicó.

**La regla que queda:** la contención se verifica por **superficie perdida**, nunca por el
predicado. Y se reporta el desacuerdo entre los dos en vez de elegir el que conviene.

Pertenece a esta sección por el mismo motivo que las trampas de fuente: **falla sin tirar ningún
error**. Un `if not nueva.covers(vieja): raise` habría abortado una corrida correcta, y —peor— un
`assert` invertido habría dado por buena una que perdía superficie. Las dos formas de equivocarse
están disponibles y ninguna avisa.
