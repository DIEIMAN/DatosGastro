# Cierre geométrico · los perímetros que faltaban

*10 de agosto de 2026 · cero consultas a servicios pagos · sin `git commit`*

---

## Las tres cifras que cambiaron

**Los polos sin borde propio pasan de dieciocho a cuatro.** Catorce de los dieciocho quedaron con
perímetro medido sobre el callejero oficial. Los cuatro que siguen sin borde son Villa Santa Rita,
Mataderos, Núñez y Retiro, y por dos motivos distintos que el documento tiene que separar: a las
dos primeras el texto no les da ninguna extensión, y las dos últimas cierran adoptando el polígono
de su barrio, que describe el barrio y no el polo.

**La masa gastronómica que el documento publica como «lo que hay adentro de los barrios sin
perímetro» pasa de 3.227 locales en 893,5 hectáreas a 527 locales en 112,9 hectáreas.** Es la
misma medición, sobre los cuatro barrios que quedan en vez de sobre quince.

**La superficie total de las concentraciones no es 3.128,5 hectáreas: es 3.143,53.** No la movió
esta pasada. La cifra publicada se midió el 7 de agosto, la capa se rehizo después, y seis
documentos siguen citando la vieja. Son **15,03 hectáreas de diferencia**, y aparecieron porque
ahora hay un archivo que las compara.

---

## Lo que no cambió, y hay que decirlo

**Los 12.688 locales siguen siendo 12.688 y las hectáreas del total no dependen de estos
perímetros.** La tarea suponía que esa cifra sale de sumar la superficie de los polos una sola
vez. **No sale de ahí.** Sale de la unión de las 124 concentraciones detectadas por densidad, que
es otro objeto: las concentraciones son lo que produce el instrumento, y los polos son lo que el
criterio admite después. Cerrar el borde de un polo no mueve una concentración.

La medición lo confirma sin ambigüedad: la unión de las 124 da las mismas 3.143,53 hectáreas antes
y después de esta pasada, y su suma cruda da lo mismo que su unión —siguen siendo disjuntas—.

**Lo que sí se movió es la unión de los polos, que hasta hoy nadie publicaba**, porque diez de
ellos tenían por geometría el polígono de un barrio entero y sumarlos habría sido publicar el
tamaño de los barrios:

| | superficie | locales |
|---|---:|---:|
| unión de los 41 polos, antes | 8.574,16 ha | 13.582 |
| unión de los 41 polos, después | **6.127,36 ha** | **11.138** |
| cambio | −2.446,80 ha | −2.444 |

La caída no es una pérdida de oferta: es que catorce polos dejaron de estar representados por el
barrio que los contiene. Es exactamente la corrección que el documento venía anunciando.

Y hay una segunda cifra del total, porque **una decisión de borde sigue abierta**: si el corredor
de Villa Ortúzar se lee de una sola acera, la unión da 6.119,44 hectáreas y 11.128 locales. La
decisión mueve 7,92 hectáreas y 10 locales.

---

## Una corrección de un número que el documento publica

**Los objetos territoriales disjuntos son cuarenta, no treinta y nueve.** El documento dice que
dos de las cuarenta y una fichas son subzonas dentro de otra —el enclave coreano de Carabobo
dentro de Parque Avellaneda, y el eje de Sáenz dentro de Nueva Pompeya— y de ahí resta dos.

Medido, **sólo una de las dos lo es**. El eje de Sáenz queda íntegramente dentro de Nueva Pompeya:
0 m² de superficie propia fuera. El enclave coreano de Carabobo queda **100 % fuera de los otros
cuarenta polos** —sus 348.613 m² enteros—, y **el Parque Avellaneda, que según el documento lo
contiene, está a 1.912 metros**. El polo más cercano al enclave es Caballito, a 598 metros. No hay
doble conteo que descontar ahí.

La confusión tiene una raíz identificable: hay dos objetos de este atlas con «Avellaneda» en el
nombre —el Parque Avellaneda, en la Comuna 9, y el corredor de Av. Avellaneda en Flores— y el
enclave está cerca del segundo, no adentro del primero.

---

## Qué se trazó, uno por uno

Los perímetros salen de las manzanas con frente sobre el tramo que cada ficha nombra. El borde
corre sobre calles por construcción, no por un ancho elegido. La regla de la pasada anterior no se
relajó: **una pieza cierra sólo si el texto de la ficha le da extensión medible.** Lo que sí
cambió es de dónde se puede leer esa extensión: no sólo de la frase del perímetro, sino de
cualquier parte de la misma ficha —el párrafo de contexto comercial, la altura de puerta de un
referente—, **siempre que la salida declare de qué frase salió**. Esa procedencia está en la
columna `fuente_del_perimetro` de cada fila.

| zona | superficie | locales | estado | de dónde sale la extensión |
|---|---:|---:|---|---|
| Nueva Pompeya y Parque Patricios | 69,06 ha | 112 | cierra, con una pieza excluida | eje relevado de Av. Caseros y de Av. Sáenz, más las puertas de El Globito y del Mercado de Pompeya |
| Nueva Pompeya · eje de Sáenz | 39,39 ha | 52 | cierra, **como subzona de la anterior** | la misma pieza; no se suma dos veces |
| Balvanera · Once | 19,18 ha | 74 | cierra | las cinco puertas del enclave que la ficha lista |
| Parque Avellaneda | 75,26 ha | 11 | cierra | la cara cerrada del parque en el callejero, con sus manzanas frentistas |
| Almagro | 60,90 ha | 207 | cierra | los tres ejes, con las tres cuadras de Guardia Vieja acotadas por el cruce con Bulnes |
| Retiro | 467,14 ha | 715 | cierra por capa administrativa | el barrio, más el cluster coreano que la ficha declara |
| Núñez | 442,64 ha | 494 | cierra por capa administrativa | el barrio |
| Villa Ortúzar | 34,39 ha | 69 | **dos opciones medidas, sin elegir** | el corredor de Av. Álvarez Thomas 600-1700 |
| La Boca · Caminito | 1,27 ha | 16 | parcial | Caminito entero, 140,6 m de calle del callejero |
| Mataderos | — | — | **no cierra** | el texto da un cruce de avenidas y ninguna extensión |
| Villa Santa Rita | — | — | **no cierra** | el texto dice «puntos dispersos» |

Los polígonos están en `ronda_17/geometria/perimetros_cierre.geojson`, en EPSG:4326, medidos en
EPSG:5347. La tabla completa está en `ronda_17/perimetros_cierre.csv`.

### El solape de cada uno contra todo polo vecino

Medido por **superficie perdida** —cuánta superficie propia queda fuera del otro— y nunca con un
predicado de contención, que devuelve falso en casos que sí contienen. Cada perímetro nuevo se
comparó contra los cuarenta y uno, con las geometrías nuevas ya puestas: el orden en que se
trazaron no decide contra qué se mide.

| zona | se pisa con | comparten | locales compartidos |
|---|---|---:|---:|
| Nueva Pompeya y Parque Patricios | eje de Sáenz *(su propia subzona)* | 39,39 ha | 52 |
| Balvanera · Once | Abasto | 3,91 ha | 15 |
| Almagro | Abasto | 25,33 ha | 101 |
| Villa Ortúzar | Colegiales | 12,07 ha | 23 |
| Villa Ortúzar | Federico Lacroze | 3,46 ha | 2 |
| Villa Ortúzar | Chacarita | 1,86 ha | 9 |
| Retiro | Centro y Microcentro | 52,16 ha | 301 |
| Retiro | Puerto Madero | 23,17 ha | 4 |
| Núñez | García del Río | 2,33 ha | 6 |
| Núñez | Belgrano | 0,06 ha | 0 |
| Parque Avellaneda | — | — | — |
| La Boca · Caminito | — | — | — |

En los pares de Retiro y de Núñez, **el que pone la superficie es el polígono del barrio**, no un
perímetro de polo: son consecuencia de que esas dos zonas publican su barrio, y se van a achicar
cuando se les escriba el tramo que les falta. Los de Villa Ortúzar caen a cero locales si se
adopta la opción de una sola acera. El detalle completo, con la superficie propia que queda fuera
en cada par, está en `ronda_17/solapes_cierre.csv`.

### Los dos que no cierran, y qué les falta exactamente

**Mataderos.** El perímetro escrito son dos piezas: la Feria y el Mercado de Hacienda «en Av.
Lisandro de la Torre y Av. de los Corrales» —un cruce de avenidas, sin extensión— y «un conjunto
de referentes dispersos», que la propia ficha declara separados por más de un kilómetro y de los
que dice que «una densidad promedio sobre el conjunto no describe ninguna de las dos».

Se midió el único candidato que hay en disco, el eje comercial que releva la Ciudad sobre Av.
Alberdi 5501-6299: **24,27 hectáreas y 55 locales**. **No se adopta.** Ese tramo es el objeto de
otra fuente, contiene uno solo de los cuatro referentes de la ficha y deja afuera la primera pieza
del perímetro, que es la Feria. El dato que falta existe fuera del atlas: la Feria ocupa calles
cortadas y tiene un perímetro de ocupación declarado administrativamente.

**Villa Santa Rita.** El hueco no es de redacción. La propia ficha declara que la vía de densidad
no abre —«seis locales dispersos en diez cuadras es un conjunto, no una densidad»—, y sus tres
referentes están en tres calles distintas sin extensión. **Todavía no hay una concentración que
delimitar**, y escribirle un borde sería inventarlo.

### Nueva Pompeya y el eje de Sáenz: un solo objeto, dos fichas

Las dos fichas describen la misma pieza a la misma dirección. Se trazó Nueva Pompeya entera —dos
piezas, 69,06 hectáreas y 112 locales— y el eje de Sáenz adentro, como subzona: 39,39 hectáreas y
52 locales, con **0 m² de superficie propia fuera** de la zona mayor. **No se suman.** La zona
grande ya incluye a la chica.

La tercera pieza del perímetro escrito, el enclave boliviano, **queda declarada afuera con motivo
medido**: sus tres bordes no cierran ninguna cara —las vías del ferrocarril no son una línea del
callejero y las dos avenidas que la ficha nombra se cruzan en un punto—, y la propia ficha dice
que ahí no hay oferta comercial documentada. Sumarla agregaría superficie con cero locales y
bajaría la densidad publicada de la zona sin que hubiera cambiado nada en el territorio.

### Parque Avellaneda: el anillo existe, la avenida que lo nombra está mal

La ficha dice «el anillo del Parque Avellaneda, sobre Av. Olivera y Av. Lacarra». El anillo se
puede trazar sin inventar nada: el parque es una cara cerrada del callejero y sus manzanas
frentistas son el anillo. Diecisiete manzanas, y con el parque adentro **75,26 hectáreas y 11
locales**.

Pero **Av. Olivera no bordea el parque**. Tiene **0 metros** de frente sobre él: lo toca en un
punto. Los 911 metros de frente son de Av. Lacarra y otros 614 de Av. Directorio, que la ficha no
nombra. La frase del perímetro nombra una avenida que no está ahí, y eso hay que corregirlo en el
texto aunque la geometría del anillo se sostenga.

Y una advertencia que la propia ficha ya trae y conviene repetir junto a la cifra: buena parte de
esa superficie es el parque, donde no hay locales. **La densidad por hectárea de esta zona no es
comparable con la de las demás.**

### Almagro: dónde están realmente las tres cuadras

La ficha nombra «el núcleo de Guardia Vieja y Bulnes» y dice que hay cuatro locales en tres
cuadras, dos de ellos en la misma esquina, el 3601 y el 3602. La pasada anterior supuso que las
tres cuadras iban del 3500 al 3800 y declaró que era una suposición.

**Medido, Bulnes cruza Guardia Vieja a la altura del 3800, no del 3601.** El tramo 3500-3800 es
justamente el único de tres cuadras que contiene el 3601 y **no llega** al cruce que da nombre a
la pieza. El que satisface las dos condiciones que la ficha escribe es **3600-3900**: contiene las
dos alturas nombradas y tiene el cruce con Bulnes adentro. Da 8,70 hectáreas y 43 locales, contra
7,60 y 35 de la lectura anterior.

Las tres piezas juntas dan **60,90 hectáreas y 207 locales**, y contienen cuatro de los cinco
Bares Notables que la ficha nombra. El quinto, El Boliche de Roberto, queda a 238 metros.

**El solape con el Abasto sigue abierto y sigue siendo grande**: 25,33 hectáreas y 101 locales
compartidos. La cifra de esta zona no se suma con la del Abasto hasta que el reparto se decida.

### La Boca: Caminito cierra, la Vuelta de Rocha no

De las dos cosas que el perímetro nombra, Caminito sí está en el callejero —140,6 metros— y sus
manzanas frentistas cierran: **1,27 hectáreas y 16 locales**. La Vuelta de Rocha no está, porque
es un recodo del Riachuelo y no una calle, y el texto no da tramo sobre Av. Don Pedro de Mendoza.

**La medición decide el veredicto, y decide en contra de publicar la cifra.** El polígono de
Caminito solo **no contiene ninguno de los tres referentes de la ficha**, y La Perla de Caminito
—Av. Don Pedro de Mendoza 1899, que es el ancla de la zona— queda a **26 metros afuera**. Un
polígono que deja afuera al establecimiento sobre el que su ficha se apoya no es el polígono de
esa ficha.

Lo que falta es una línea. Están medidos los dos candidatos:

- **Caminito más las dos cuadras de la avenida que toca, 1871-1939: 4,15 hectáreas y 37 locales.**
  Sí contiene La Perla. No se adopta porque esas dos cuadras las elige la medición y no la ficha.
- La cara de la Vuelta de Rocha, cerrada por la avenida y por el límite oficial del barrio sobre
  el Riachuelo: **3,30 hectáreas y 0 locales.** Cierra con objetos auditables, pero agregaría
  superficie sin oferta, que es el mismo motivo por el que el enclave boliviano queda afuera de
  Pompeya.

### Núñez y Retiro: se cierran con lo que ya estaba medido

**Núñez.** La zona que el atlas publica es **idéntica** a la capa de barrios que venía usando:
diferencia simétrica 0 m². El atlas no le sumó superficie a nadie. Toda la diferencia contra la
capa oficial son **74.837 m² sobre la línea de ribera del Río de la Plata, con cero locales**.
Adoptar la capa oficial le saca 7,22 hectáreas y no le mueve un solo local. Queda en **442,64
hectáreas y 494 locales**.

**Retiro.** Esta sí sumó, y suma lo que su propia ficha declara: **149.485 m² con 117 locales,
100 % en San Nicolás** —el cluster coreano y asiático—. Confirmado contra la capa que el atlas
venía usando. Contra la capa oficial el mismo cálculo da 156.196 m² y 118 locales, y **los 6.711
m² y el local de diferencia no son del polo**: son la diferencia entre las dos capas de barrios, y
mezclarlos le atribuiría al polo un local que puso el cambio de capa.

En los dos casos la cifra que se publica es **la del barrio, no la del polo**, y el documento
tiene que seguir diciéndolo: las piezas del perímetro escrito que no cerraban siguen sin cerrar
—el corredor bajo el viaducto en Núñez, el tramo de Florida en Retiro—.

### Villa Ortúzar: las dos opciones, medidas, sin elegir

La avenida es el límite del barrio en la mayor parte del tramo, así que leer «ambas aceras» pone
la mitad de las manzanas del otro lado.

| opción | manzanas | superficie | locales | reparto por barrio |
|---|---:|---:|---:|---|
| **A · una sola acera**, la de Villa Ortúzar | 8 | **10,71 ha** | **34** | Villa Ortúzar 100,0 % |
| **B · las dos aceras**, con reparto declarado | 23 | **34,39 ha** | **69** | Colegiales 34,9 % · Chacarita 34,0 % · Villa Ortúzar 31,1 % |

La opción B se pisa con tres polos ya publicados: 12,07 hectáreas y 23 locales con Colegiales,
3,46 y 2 con Federico Lacroze, 1,86 y 9 con Chacarita. **La opción A comparte 0,15 hectáreas con
Federico Lacroze y 0,01 con Colegiales, y ni un solo local**: son ochavas, no reparto.

**Recomendación, en una línea: una sola acera** — la de dos deja el 69 % de su superficie fuera
del barrio que da nombre a la zona y comparte 34 locales con tres polos publicados; la de una cae
entera en Villa Ortúzar y no comparte ninguno. La decisión es editorial y no se toma acá.

---

## La capa de barrios: adoptada, con el costo publicado

Se adopta la capa oficial de 48 barrios y 15 comunas como capa canónica del proyecto. La razón es
una sola: **tiene procedencia, commit y sha256 verificables, y la que se venía usando no tiene
ninguno de los tres.**

El costo está medido y es chico. **Siete locales de 23.981 cambian de barrio. Doce barrios cambian
su conteo, con un neto de +1** sobre el conjunto de los 48. El neto no es cero porque un local que
hoy cae fuera de toda la capa vieja entra en la oficial. La tabla completa, barrio por barrio y
con el detalle de a dónde va cada local, está en `ronda_17/impacto_capa_barrios.csv`, y los siete
locales están nombrados en `ronda_17/locales_que_cambian_de_barrio.csv`.

Sobre geometría, las dos capas difieren en 366.931 m² que la vieja tiene de más —con cero
locales— y 35.519 m² que tiene de más la oficial, con uno. La diferencia es la línea de ribera.

### La trampa de los nombres, levantada antes de que muerda

La capa vieja escribe **«La Boca»** y la oficial **«Boca»**. La oficial escribe **«NUÑEZ»** y el
resto del proyecto **«Núñez»**. Un cruce por nombre que no encuentra nada **no falla**: devuelve
cero filas, y cero filas se lee como «ese barrio no tiene locales».

Medido sobre los mismos 48 barrios:

| forma de cruzar | barrios que pierde |
|---|---:|
| comparando los nombres tal cual | **48** |
| pasando a mayúsculas y sacando tildes | **1** |
| con el normalizador | **0** |

El normalizador es `ronda_17/nombres_de_barrio.py` y lo usan todos los cruces de esta pasada. El
test es `ronda_17/test_capa_de_barrios.py` y **falla si algún barrio que tiene locales devuelve
cero al cruzar por nombre**, contra las dos capas. Doce pruebas, todas en verde.

No es una precaución teórica: **el script de perímetros de esta misma pasada se tropezó con la eñe
en su primera corrida.** Buscó «Nunez» con una comparación exacta, no encontró nada, midió 0,00
hectáreas y siguió adelante sin avisar. Por eso ahora un nombre de barrio que no resuelve corta la
corrida en vez de producir un número de menos.

### Cómo quedó aplicada

La función que sirve los barrios a todas las mediciones del proyecto ahora **devuelve la geometría
oficial con los nombres de siempre**. La grafía no cambia a propósito: los llamadores buscan por
una clave que sale del nombre, y con «BOCA» en lugar de «La Boca» una decena de scripts habría
empezado a medir sobre un polígono vacío —sin fallar, devolviendo cero—. El nombre tal como lo
escribe la fuente queda disponible en una columna aparte, y la capa anterior sigue alcanzable con
un parámetro, para reproducir cualquier número que ya haya circulado.

Se controló que **las 48 claves que los scripts existentes buscan siguen resolviendo**, una por
una, antes de dar el cambio por hecho.

---

## Un solo lugar donde viven las cifras

`ronda_17/cifras_canonicas.json` declara **dieciocho cifras del atlas**, cada una con su valor, su
fecha de cálculo, el archivo del que sale y cómo se calcula. **Las dieciocho se calculan en la
corrida; ninguna se tipea.**

`ronda_17/verificar_cifras.py` recorre los 86 documentos del atlas, busca cada cifra en su
contexto y compara. Entiende el formato de acá —`3.128,5` es tres mil ciento veintiocho con
cinco— y entiende los números escritos con letra, porque el atlas los usa: «Dieciocho de los
cuarenta y un polos» es exactamente una de las frases que hay que atrapar.

**No corrige nada, y es a propósito.** Un reemplazo automático sobre prosa toca frases que dicen
cosas distintas con el mismo número: «la cifra correcta es X» y «el documento decía X» son la
misma cadena y sólo una hay que cambiar. El script señala; la corrección la firma quien escribe.

Corrido hoy: **doce cifras coinciden con la fuente, cinco no, y una todavía no aparece en ningún
documento.** Las cinco que no coinciden:

| cifra | el texto dice | la fuente dice | dónde |
|---|---|---|---|
| polos sin borde | dieciocho | **4** | 5 documentos, 6 menciones |
| locales en los barrios sin borde | 3.227 | **527** | 2 documentos |
| hectáreas en los barrios sin borde | 893,5 | **112,9** | 2 documentos |
| superficie de las concentraciones | 3.128,5 ha | **3.143,53 ha** | 6 documentos, 12 menciones |
| objetos territoriales disjuntos | 39 | **40** | 2 documentos |

Las tres primeras las movió esta pasada. Las dos últimas ya estaban desincronizadas y nadie lo
había visto, que es exactamente para lo que sirve el archivo.

La cifra que todavía no aparece en ningún documento es **12.520 locales**, y conviene incorporarla
porque resuelve una ambigüedad: los 12.688 son los locales que el agrupamiento asignó a alguna
concentración, y 12.520 son los que caen dentro del polígono publicado. **Son dos universos y la
diferencia son 168 locales**, un 1,3 %. Un local puede pertenecer al agrupamiento y quedar fuera
de la envolvente simplificada. Cualquier tabla que use una de las dos tiene que decir cuál.

---

## Lo que esta pasada no hizo

- **No tocó ninguna capa publicada.** `zonas_r8.geojson`, las fichas y los soportes quedan como
  estaban. Los perímetros nuevos viven en `ronda_17/geometria/` y esperan que alguien los adopte.
- **No volvió a correr las mediciones anteriores** con la capa de barrios nueva. El cambio queda
  hecho en el código y sus salidas viejas quedan intactas: rehacerlas movería números que ya
  circularon, y eso se decide con la lista de qué se rehace delante.
- **No corrigió ningún documento.** Las cinco discrepancias están señaladas con archivo y línea.
- **No eligió el borde de Villa Ortúzar**, ni el reparto de Almagro con el Abasto, ni el tramo de
  la avenida en La Boca.
- **Cero consultas a servicios pagos. No se corrió `git commit`.**

## Lo que rinde más de lo que queda

**Una línea de texto cierra La Boca.** El tramo de Av. Don Pedro de Mendoza: está medido, da 4,15
hectáreas y 37 locales, y contiene el ancla de la zona.

**El perímetro de ocupación de la Feria de Mataderos existe fuera del atlas** y es un dato
administrativo, no una medición: con él cierra la primera de sus dos piezas.

**Y Villa Santa Rita no necesita una línea de texto, necesita relevamiento.** Es la única de las
cuatro donde el hueco no es de redacción.
