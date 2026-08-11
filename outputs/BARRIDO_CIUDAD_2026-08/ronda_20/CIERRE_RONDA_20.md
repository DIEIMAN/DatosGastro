# Cierre · qué perímetro tiene escrito cada página, y la verificación contra el documento real

Fecha de la medición: 10/08/2026. Todo se midió en EPSG:5347 y se guardó en EPSG:4326. La
contención se verificó por superficie perdida y nunca con `covers()`. Cero consultas a servicios
pagos y ninguna fuente cerrada. Los archivos citados están en esta misma carpeta.

El archivo del atlas en disco es del 10/08 a las 18:21 y contiene lo que se le incorporó, así que
**esta verificación mide el documento real**. La anterior no lo hacía y quedó anotado que no.

---

## 1 · Lo que cambió de valor

| qué | antes | ahora |
|---|---|---|
| La Boca sobre Almirante Brown y Necochea | 6,14 ha · 3 locales | **16,17 ha · 21 locales** (adoptado) |
| Unión de los 41, superficie | 5.434,11 ha | **5.444,15 ha** |
| Unión de los 41, locales | 10.801 | **10.819** |
| Suma de los 41 por separado, locales | 12.087 | **12.105** |
| Locales en los barrios de los polos que se miden sobre su barrio | 527 | **347** |
| Hectáreas concentradas en esos barrios | 112,9 | **41,1** |
| Polos que publican el polígono de su barrio | 3 | **4** |
| Establecimientos con historia fuera de su propio borde | 42 | **39** |
| Páginas sin ningún establecimiento con historia adentro | 5 | **4** |
| Establecimientos con reconocimiento fuera de todo borde | 80 | **81** |
| De ésos, a 250 m o menos | 45 | **43** |
| De ésos, que se resolverían sin inventar una línea | 12 | **7** |
| Cifras del texto que coinciden con su fuente | 12 | **23** |
| Páginas cuyo perímetro escrito reconstruye el borde | no se medía | **11 de 41** |

Cuatro cifras cambiaron **porque cambió la geometría** —la unión, la suma y las dos de los
establecimientos que quedan afuera—; dos cambiaron **porque cambió la definición** —los polos que
se miden sobre su barrio pasaron de cuatro a tres, y los que publican el polígono de su barrio de
tres a cuatro, que no son la misma lista—; y la de los doce cambió **porque la prueba se corre
contra otro texto**, que es el asunto de esta tanda.

---

## 2 · La verificación, ahora contra el documento que existe

**Cinco cifras del texto no coinciden con su fuente, veintitrés sí y veinticinco todavía no se
usan en ningún documento.** La vez pasada eran cinco, doce y veintiocho, pero la comparación no es
directa: aquella corrida leyó un archivo que no tenía lo incorporado. **Doce cifras aparecieron en
el texto** y **catorce empezaron a coincidir**.

Antes de nada, lo que el pedido mandaba verificar y verifica bien:

> **347 locales en 41,1 hectáreas concentradas.** Medido fila por fila contra
> `magnitudes_sin_perimetro.csv` del 09/08/2026: 92 + 201 + 54 = 347 locales, y 12,43 + 18,21 +
> 10,46 = 41,10 hectáreas. **Coincide con lo que publica el documento.** Las canónicas viejas
> —527 y 112,9— eran las de cuatro polos; Mataderos sale de la lista porque tiene borde
> transitorio, y esa es toda la diferencia.

### Las cinco que no coinciden

| cifra | dice el texto | dice la fuente | dónde |
|---|---|---|---|
| unión de los 41, locales | 10.801 | **10.819** | documento, línea 4553 · y el anexo de las concentraciones |
| unión de los 41, hectáreas | 5.434 | **5.444,15** | ídem |
| suma de los 41 por separado | 12.087 | **12.105** | documento, línea 4552 · ídem |
| superficie de la unión de las concentraciones | 3.128,5 | **3.143,53** | dos documentos de trabajo |
| polos sin borde propio | dieciocho | **3** | el tablero de estado |

**Las tres primeras son un solo hecho y conviene decirlo así:** el párrafo de los solapes se
escribió antes de adoptar el borde nuevo de La Boca. El documento publica ese borde en 16,17
hectáreas —y esa cifra sí coincide— pero el total del conjunto todavía es el de antes. Adoptar
La Boca suma 10,04 hectáreas y 18 locales a la unión, y no toca ninguna otra cifra del párrafo:
los pares de solape siguen siendo veinticinco, los locales en dos o más polos siguen siendo 1.263
y las concentraciones siguen siendo 53 adentro y 71 afuera. **Sólo hay que corregir tres números
en dos renglones.**

Las otras dos ya no están en el documento del atlas: la de las concentraciones quedó en dos
archivos de trabajo, y «dieciocho» sobrevive únicamente en el tablero de estado. **El atlas dice
tres, y está bien dicho.**

### Y una que da el número correcto con la palabra equivocada

El documento escribe: *«Sumar los 41 por separado da 12.087 locales; la unión real es de 10.801
locales… La diferencia son 1.263 locales que están adentro de dos polos o de tres»*. **1.263 es
correcto y no es la diferencia.** Son dos cosas distintas: 1.263 es la cantidad de locales
distintos que caen en más de un polo, y la resta entre la suma y la unión da 1.286, porque un
local que está en tres polos se cuenta de más dos veces. El verificador da esa cifra por buena
—y lo es— pero la frase que la presenta no cierra su propia aritmética.

**Archivos: `VERIFICACION_CIFRAS.txt`, `cifras_canonicas.json`** (53 cifras, 8 nuevas) y
**`verificacion_cifras.json`**.

---

## 3 · El entregable: qué perímetro tiene escrito cada una de las 41 páginas

Esto sale de lo que quedó anotado la vez pasada: los establecimientos que están cerca de un borde
no se podían decidir porque la prueba —«¿la calle de su puerta la nombra el perímetro escrito?»—
se corre contra un texto de calidad desigual. Medido, la desigualdad es mayor de lo que parecía.

### La respuesta corta

**Once de las cuarenta y una.** Once páginas tienen un perímetro escrito del que se puede
reconstruir el borde dibujado sin agregar nada: dan las piezas y su extensión, y aplicándoles la
regla con la que se trazó todo lo demás —las manzanas frentistas del tramo— sale la figura
publicada. Otras siete lo dan a medias. **Veintitrés no lo dan.**

| ¿se reconstruye el borde desde el texto? | páginas |
|---|---:|
| sí | **11** |
| en parte | 7 |
| no | 23 |

Y por lo que el bloque ofrece:

| categoría | páginas |
|---|---:|
| da calles y alturas | 11 |
| da calles sin alturas | 21 |
| da un cruce de avenidas sin extensión | 1 |
| da un barrio o una referencia sin calles | 6 |
| no escribe perímetro | 2 |

**Ocho páginas no nombran ninguna calle.** Dos de ellas no escriben perímetro de ninguna clase: el
bloque entero dice «Perímetro vigente.» y nada más. Las otras seis remiten a ese perímetro y
agregan un barrio, una plaza, un mercado o un enclave.

En total las 41 páginas nombran 121 calles. **Ciento siete tocan el borde de su propia página**, y
siete páginas nombran al menos una que no lo toca.

Una aclaración de lectura, porque el cuadro tiene dos números que parecen contradecirse: **doce
páginas escriben alturas y sólo once están en «da calles y alturas»**. La que falta es Mataderos.
Las únicas alturas que escribe son las del eje comercial de Av. Alberdi, y su propia página dice
que ese eje es otro objeto y no el polo; para el polo da un cruce de dos avenidas y no dice hasta
dónde llega. Por eso queda en «da un cruce sin extensión», que es la categoría que existe para
ella y es también la razón por la que su borde es transitorio.

### Tres cosas que aparecieron al leer las 41

**Una página publica dos superficies distintas para el mismo contorno.** En Av. Montes de Oca el
bloque dice que el contorno medido es de *«18,02 hectáreas y 62 locales»*, y catorce renglones más
abajo la misma página dice *«84 locales en 50,62 hectáreas»*. La capa tiene 50,62. La cifra del
bloque quedó de una medición anterior.

**Una página declara que no tiene borde dibujado y publica sus dos cifras.** En Barracas sobre
Iriarte, California y Vieytes el bloque dice *«Sin borde dibujado todavía: la superficie y la
cantidad de locales se publican cuando se cierre»*, y la misma página publica *«12 locales en 5,83
hectáreas»*. El borde existe en la capa. Lo que falta corregir es la frase.

**Una página escribe más perímetro del que su geometría contiene.** El bloque de Balvanera nombra
el enclave de Tucumán entre el 2379 y el 2755 —que está entero adentro del borde, 573 de 573
metros medidos— y además *«el tramo de Av. Rivadavia entre el 2001 y el 2200 que lo conecta por
Pasteur»*. Ese tramo mide 251 metros y está **a 715 metros del borde dibujado, con cero metros
adentro**. No es el caso de un texto vago: es un texto preciso que describe dos piezas cuando la
figura publicada tiene una.

A las tres hay que sumarles La Boca sobre Almirante Brown y Necochea, que es de otra clase: su
bloque sigue citando sólo el tramo de 340 metros de la obra pública, que es lo que decía antes de
que se adoptara el borde nuevo. El encabezado de la página ya dice 16,17 hectáreas. **El bloque
todavía no.**

**Archivo: `perimetro_escrito_41.csv`**, 41 filas, con el texto literal de cada bloque, las calles
que nombra —resueltas contra el callejero oficial, y si una no resuelve la corrida se corta—, si
da alturas, la categoría, si el borde se reconstruye y por qué. La salida completa, con los 41
bloques transcriptos, en **`PERIMETRO_ESCRITO_41.txt`**.

### Lo que esto resuelve de los que quedan cerca del borde

Con el cuadro se puede volver a correr la prueba, y el resultado cambia. **De los 43 que quedan a
250 metros o menos, siete se resolverían extendiendo sobre una calle que el perímetro escrito de
su página ya nombra y que además llega hasta el borde.** Antes eran doce de cuarenta y cinco.

| establecimiento | dirección | página | m | el borde pasaría a |
|---|---|---|---|---|
| Bar Plaza Dorrego | Defensa 1098 | San Telmo | 27,2 | 29,40 ha · 90 locales |
| El Tropezón | Av. Callao 248 | Avenida Corrientes | 36,4 | 52,32 ha · 369 locales |
| Caseros | Av. Caseros 486 | Boulevard Caseros | 54,1 | 53,70 ha · 82 locales |
| Mercado de San Telmo | Defensa 961 | San Telmo | 64,2 | 32,81 ha · 140 locales |
| Chuí | Loyola 1250 | Villa Crespo | 92,4 | 344,07 ha · 837 locales |
| Bar Imperio | Av. Callao 181 | Avenida Corrientes | 124,8 | 55,72 ha · 389 locales |
| Pirilo | Defensa 821 | San Telmo | 223,4 | 36,89 ha · 171 locales |

**Bajan de doce a siete y ninguno se movió del lugar.** Tres salieron porque el borde nuevo de La
Boca ya los contiene. Los otros dos salieron porque la prueba, corrida contra la página, da otra
cosa:

- **El restaurante del Alvear Palace** figuraba como resoluble porque su calle es Av. Alvear y el
  texto de trabajo contenía la palabra «Alvear». Lo que la página de Retiro nombra es **M. T. de
  Alvear**, que en el callejero oficial es otra calle. Era un falso positivo del método anterior,
  que buscaba palabras.
- **Corte Comedor**, en Av. Olazábal, quedaba resoluble por Belgrano. La página de Belgrano **no
  nombra ninguna calle**: su bloque entero es «Perímetro vigente» más el enclave que contiene.

Y el cruce de las dos tablas dice algo que ninguna de las dos dice sola: **los siete que se
resolverían caen todos en páginas de la categoría «da calles sin alturas»**. De los 16 que están
cerca de una página que sólo da un barrio o una referencia, y de los 5 que están cerca de una que
no escribe perímetro, **no se resuelve ninguno** — y no porque estén lejos, sino porque no hay
texto contra el cual medirlos. Para esos 21 la pregunta no es de geometría: es que primero hay que
escribir el perímetro.

**Archivo: `cerca_del_borde_20.csv`**, 81 filas.

---

## 4 · El recorte de adentro de los cuatro

Núñez, Retiro y Villa Santa Rita ya estaban declarados. **Colegiales se declara acá**, y la
medición confirma el motivo: su contorno y el polígono del barrio coinciden en el 99,93 % —1.529 m²
del contorno caen fuera del barrio y 1.678 m² del barrio fuera del contorno—. Su propia página ya
lo dice: *«el contorno que esta página usa coincide con el polígono del barrio, y todavía no está
dibujado el recorte más chico de adentro»*.

Conviene precisar la coincidencia de cada uno, porque no son iguales:

| polo | contorno | barrio | del contorno fuera del barrio | del barrio fuera del contorno |
|---|---:|---:|---:|---:|
| Núñez | 442,64 ha | 442,64 ha | 0 m² | 0 m² |
| Retiro | 467,14 ha | 451,52 ha | 156.196 m² | 0 m² |
| Villa Santa Rita | 215,46 ha | 215,47 ha | 1.158 m² | 1.298 m² |
| Colegiales | 229,08 ha | 229,09 ha | 1.529 m² | 1.678 m² |

Núñez **es** el barrio, exacto por los dos lados. Retiro es el barrio **más** las 15,62 hectáreas
del núcleo coreano, que caen en San Nicolás y que su propia página ya declara. Los otros dos son
el barrio salvo por unos mil metros cuadrados de borde.

Y el recorte, medido y **no adoptado**:

| polo | contorno publicado | recorte de adentro | más chico | conserva | piezas |
|---|---|---|---:|---:|---:|
| Núñez | 442,64 ha · 494 locales | **35,66 ha · 107 locales** | 12,4× | 21,7 % | 2 |
| Retiro | 467,14 ha · 715 locales | **37,16 ha · 297 locales** | 12,6× | 41,5 % | 1 |
| Villa Santa Rita | 215,46 ha · 182 locales | **16,56 ha · 40 locales** | 13,0× | 22,0 % | 1 |
| Colegiales | 229,08 ha · 441 locales | **98,03 ha · 298 locales** | 2,3× | 67,6 % | 3 |

Los cuatro recortes contienen **el 100 %** de los locales de las concentraciones que fueron a
buscar, y eso se midió y no se supuso: un recorte que no contiene lo que fue a buscar no sirve
aunque su superficie sea creíble.

### Mis dos renglones por cada uno

**Núñez.** El recorte es doce veces más chico que lo que la página publica y se queda con uno de
cada cinco locales del barrio: publicar el barrio como si fuera el polo multiplica por doce la
superficie del objeto que la página describe.
Sale en dos piezas, y eso es fiel a lo que la propia página escribe —tres piezas separadas— así
que acá la fragmentación no es un defecto del método: es la forma del lugar.

**Retiro.** Es el que mejor sobrevive al recorte: pierde el 92 % de la superficie y conserva el
41 % de los locales, y sale en una sola pieza. Es la señal más clara de las cuatro de que hay un
polo adentro esperando que lo dibujen.
Con una advertencia de lectura: su contorno no es sólo el barrio, es el barrio más el núcleo
coreano, y ese añadido cae entero en San Nicolás; cualquier recorte que se adopte tiene que decir
si se lo queda o no.

**Villa Santa Rita.** Es el más chico y el más contundente en proporción —trece veces— pero
también el que menos sostiene: cuarenta locales. Antes de dibujarle un borde conviene decidir si
cuarenta locales son un polo.
Y hay que leerlo junto a lo que dice su propia página: el anclaje que declara es Av. Álvarez
Jonte, que es el **límite** del barrio y no su columna interior, así que el recorte de adentro y
el anclaje escrito no están hablando del mismo lugar.

**Colegiales.** Es el caso distinto de los cuatro: el recorte es sólo 2,3 veces más chico y
conserva dos de cada tres locales del barrio. Colegiales no tiene un polo adentro de un barrio
mayormente vacío; tiene gastronomía repartida por casi todo el barrio.
Sale en tres piezas y ésa es la información útil: lo que su página propone —el eje Concepción
Arenal–Zapiola, el Polo Concepción y el Mercado de Pulgas— son también tres, y decidir si se
publica como una zona o como tres es la decisión que su página tiene pendiente desde que dice «en
revisión».

**Archivo: `recorte_de_los_cuatro.csv`** y la geometría en
`geometria/recorte_de_los_cuatro.geojson`.

---

## 5 · El Café Roma

**No hay que elegir entre las dos direcciones: son dos establecimientos distintos, y el catálogo
oficial los tiene a los dos por separado.**

| orden | establecimiento | dirección | barrio |
|---|---|---|---|
| 29 de 90 | Café Roma | **Olavarría 409** | La Boca |
| 86 de 90 | Roma del Abasto | **Anchorena 806** | Balvanera |

- **La dirección del establecimiento es Olavarría 409.** Es el Bar Notable de La Boca, orden 29 de
  la Res. MCGC 1225/26, con verificación de apertura del 08/08/2026.
- **La otra fila queda declarada como error de carga**, y es más preciso decir de qué error se
  trata. «San Luis 3101» no es una dirección inventada: Wikidata tiene **dos** entradas llamadas
  «Café Roma», con dos identificadores y dos barrios, y la segunda —Q56826620, Balvanera— es
  Roma del Abasto. San Luis y Anchorena se cruzan: el 3101 de una y el 806 de la otra son la misma
  esquina, y los dos puntos distan **12,8 metros** medidos. Lo que el emparejamiento por nombre
  hizo fue fusionar las dos entradas bajo un solo nombre y darle a la segunda **el punto de la
  primera**, a 6,1 kilómetros de donde va.

**La corrección ya estaba hecha desde el 07/08/2026** en la capa canónica de reconocimiento, con
su fila de cambios y su nota. Lo que no se corrigió es la copia que **leen las páginas**, que es
una foto anterior de esa misma capa. Por eso el bloque «Para conocer» de La Boca publica *«4
lugares con reconocimiento: 3 Bares Notables y 1 pizzería emblemática»* y lista dos veces el mismo
café. **Medido contra la capa canónica y el borde nuevo, adentro hay 3: dos Bares Notables —Café
Roma y La Buena Medida— y la pizzería Banchero.**

Y como resolver un duplicado no sirve si la fuente del duplicado sigue conectada, se midió cuánto
más trae de atraso esa copia:

- Tiene **215 filas contra 225** de la capa canónica: le faltan **diez establecimientos**.
- De esos diez, **uno cae dentro de un borde**: Bar Iberia, Bar Notable, adentro del Centro y
  Microcentro. **Esa página cuenta uno de menos**, por el mismo motivo por el que La Boca cuenta
  uno de más.
- Cuatro más —el Gran Café Gardel, el Centro Asturiano, el Centro Laurak Bat y el Casal de
  Catalunya— quedan fuera de todo borde, y son los cuatro que aparecen como nuevos en la lista de
  los que están afuera. No aparecieron: estaban y no se los estaba leyendo.
- Los cinco restantes todavía no tienen punto y por eso no entran en ninguna cuenta geométrica.
- Además de la del café, **una sola fila más difiere de verdad**: La Academia figura en Av. Callao
  368 y la capa canónica la tiene en Montevideo 341 —se mudó—, aunque las dos direcciones caen en
  la misma página y el conteo no cambia.

**Archivos: `cafe_roma_resolucion.csv`** (2 filas) y **`capa_reconocimiento_atrasada.csv`** (13
filas).

---

## 6 · Dos cosas del método que conviene dejar escritas

**Comparar nombres de calle como texto produce falsos negativos.** La puerta del Café de los
Angelitos resuelve contra el callejero como «RIVADAVIA» y la página escribe «Av. Rivadavia», que
resuelve como «RIVADAVIA AV.». Son la misma avenida —el callejero las tiene en la misma familia—
y la primera versión de este control decía que la página no la nombraba. Se compara por familia.
No afloja la prueba: «Callao» y «Callao Av.» son familias distintas y siguen contando como calles
distintas.

**Una sensibilidad que da tres veces el mismo número no es una comprobación.** El recorte de los
cuatro daba idéntica superficie con frente mínimo de 10, 20 y 40 metros, y la explicación no es
robustez: las cuadras son segmentos enteros del callejero, así que la manzana que da frente a una
cuadra le da la cuadra entera. El frente más chico que aparece en los cuatro casos es de 43
metros, el doble del umbral. Se publica ese número en vez de la sensibilidad, que era vacía.

---

## 7 · Lo que no se pudo resolver, y por qué

1. **Las tres cifras del párrafo de los solapes siguen sin corregir en el documento** —10.801,
   5.434 y 12.087—. El verificador señala y no toca el texto: la corrección la firma quien
   escribe. Están medidas y guardadas.
2. **Un detalle de la corrección anterior que hay que tener a mano:** la unión medida da 5.444,15
   hectáreas y el documento escribe hectáreas enteras. El comparador de este control tiene una
   tolerancia fija de 0,1, así que escribir «5.444» lo va a seguir marcando. O se escribe con
   decimales, o se acepta que esa fila quede marcada por redondeo.
3. **Las tres contradicciones internas de páginas no se corrigieron**: las dos superficies de Av.
   Montes de Oca, el «sin borde dibujado» de Barracas sobre Iriarte y las dos piezas del perímetro
   escrito de Balvanera contra una sola dibujada. Son de redacción, no de medición.
4. **El bloque «Dónde está» de La Boca sobre Almirante Brown y Necochea no describe el borde que
   la página ya publica.** Sigue citando el tramo de 340 metros. Hay que escribir hasta dónde llega
   sobre Av. Suárez y Olavarría.
5. **La copia de la capa de reconocimiento que leen las páginas está atrasada y no se regeneró
   acá.** Regenerarla es tocar el insumo de los bloques de las 41 páginas y eso no es una decisión
   de un control. Mientras no se haga, La Boca cuenta un Bar Notable de más y el Centro y
   Microcentro uno de menos.
6. **Los 21 que quedan cerca de una página que no escribe perímetro no se pueden decidir, y ahora
   se sabe por qué.** No es un problema geométrico y no lo resuelve medir mejor: no hay texto
   contra el cual medir. La decisión previa es escribir el perímetro de esas páginas.
7. **Ninguno de los cuatro recortes de adentro se adopta.** Están las dos superficies, los dos
   conteos y mi lectura en dos renglones; la firma no.
8. **Mataderos sigue sin borde cerrado**, por lo mismo de siempre: lo que lo cerraría es el
   perímetro de ocupación de la Feria, que es un dato administrativo que este repositorio no
   tiene.

---

## Archivos de esta carpeta

| archivo | qué es |
|---|---|
| `perimetro_escrito_41.csv` | **el entregable**: el perímetro escrito de las 41 páginas, con su categoría |
| `recorte_de_los_cuatro.csv` | los cuatro que publican el polígono de su barrio, con su recorte medido |
| `cafe_roma_resolucion.csv` | cuál de las dos direcciones es el establecimiento y qué es la otra |
| `capa_reconocimiento_atrasada.csv` | lo que la copia que leen las páginas tiene de atraso |
| `cerca_del_borde_20.csv` | los 81 que quedan fuera de todo borde, con la prueba corrida contra la página |
| `solapes_declarados.csv` · `solapes_locales_detalle.csv` | los 25 pares, recalculados con La Boca adoptada |
| `correspondencia_124_x_41.csv` | las 124 concentraciones contra los bordes de ahora |
| `geometria/bordes_vigentes_41.geojson` | la capa vigente, con La Boca en 16,17 ha |
| `geometria/recorte_de_los_cuatro.geojson` | los cuatro recortes, medidos y no adoptados |
| `cifras_canonicas.json` · `verificacion_cifras.json` | las 53 cifras y el texto contra ellas |
| `PERIMETRO_ESCRITO_41.txt` · `RECORTE_DE_LOS_CUATRO.txt` · `CAFE_ROMA.txt` · `CERCA_DEL_BORDE.txt` · `SOLAPES_Y_UNION.txt` · `VERIFICACION_CIFRAS.txt` | la salida completa de cada corrida |
| `geometria_vigente_20.py` · `solapes_y_union_20.py` · `cafe_roma_y_la_capa.py` · `extraer_donde_esta.py` · `perimetro_escrito_41.py` · `recorte_de_los_cuatro.py` · `cerca_del_borde_20.py` · `cifras_y_verificacion_20.py` | los scripts, en ese orden |
