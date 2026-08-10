# Cierre · los solapes, la correspondencia y qué costaría cerrar las cinco

Fecha de la medición: 10/08/2026. Todo se midió en EPSG:5347 y se guardó en EPSG:4326. La
contención de un polígono dentro de otro se verificó por superficie perdida y nunca con
`covers()`. Cero consultas a servicios pagos y ninguna fuente cerrada. Los archivos citados están
en esta misma carpeta.

---

## 1 · Lo que cambió de valor

| qué | antes | ahora |
|---|---|---|
| Unión de los 41 perímetros, superficie | no se publicaba | **5.434,11 ha** |
| Unión de los 41 perímetros, locales | no se publicaba | **10.801 locales** |
| Polos sin borde propio | 4 | **3**, más 1 con borde transitorio |
| Establecimientos con reconocimiento fuera de todo borde | 60 | **80** |
| De ésos, a 250 m o menos del borde | 41 | **45** filas · **44** establecimientos |
| De ésos, que se resolverían sin inventar una línea | no se medía | **12** |
| Qué costaría cerrar las cinco páginas sin ancla adentro | no se medía | **medido, ninguna adoptada** |

Y dos cifras que **no** cambiaron aunque se hayan recalculado enteras: los pares de polos que
comparten superficie siguen siendo **25**, y las concentraciones que caen dentro de algún polo
siguen siendo **53 de 124**. Las dos tablas se rehicieron desde cero contra la geometría de ahora
y dan exactamente lo mismo que la vez pasada, par por par y fila por fila. La geometría vigente no
se movió entre una tanda y otra: lo que faltaba no era la medición, era la tabla publicada.

**Aviso sobre el punto 1c del pedido: no hay commit.** El índice de git sigue trabado por un
`.git/index.lock` y cualquier `git add` falla con «Another git process seems to be running». Por
regla no se toca ese archivo, así que la tanda queda escrita en disco y sin commitear, igual que
las seis anteriores. Hay 645 cambios en el árbol esperando. **Hay que destrabarlo a mano.**

---

## 2 · La tabla de solapes, que era lo que faltaba

**25 pares de polos comparten superficie.** La tabla va completa, con las hectáreas, los locales
compartidos y **la lista de qué locales son**, por identificador.

| par | ha compartidas | locales compartidos |
|---|---|---|
| Centro y Microcentro + Retiro | 52,16 | 301 |
| Chacarita + Federico Lacroze | 60,37 | 153 |
| Avenida Corrientes + Centro y Microcentro | 21,72 | 133 |
| Federico Lacroze + Colegiales | 67,02 | 115 |
| Abasto + Almagro | 25,33 | 101 |
| Palermo + Federico Lacroze | 22,86 | 98 |
| Villa Crespo + La Paternal | 49,68 | 91 |
| Palermo + Villa Crespo | 12,55 | 77 |

El caso que la decisión pedía verificar está verificado: **Villa Ortúzar comparte 15,93 ha y 25
locales con Chacarita, Colegiales y Federico Lacroze** —12,07 ha con Colegiales, 3,46 con Federico
Lacroze y 1,86 con Chacarita, y 15,93 los tres juntos sin contar dos veces lo que se pisan entre
ellos—. **Coincide exacto con la cifra adoptada.**

**Cuatro de los 25 pares** involucran un polo que publica el polígono de su barrio en vez del del
polo —Retiro y Núñez—, y va marcado en la tabla: ese solape es una propiedad de la capa
administrativa y no del polo. Ningún par involucra el borde transitorio.

La vez pasada esa cuenta decía cinco, y la diferencia es de definición y no de medición: entonces
se contaba también el par de Villa Santa Rita, que no publica el polígono de su barrio sino su
soporte provisorio. Son dos cosas distintas y ahora van separadas: la columna
`alguno_publica_su_barrio` marca a Retiro y Núñez, y Villa Santa Rita sigue contada entre los tres
polos sin borde propio.

**Archivos: `solapes_declarados.csv`** (25 filas, con `ha_compartidas`, `locales_compartidos` y la
lista de identificadores) y **`solapes_locales_detalle.csv`** (1.309 filas, un local por par, con
barrio y comuna). Nombre y dirección de cada local están en `base/local.csv` por ese
identificador y no se copian acá.

---

## 3 · La cifra que la tabla existe para permitir

Con la tabla de solapes se puede totalizar, que es lo que hasta ahora no se podía hacer sin
contar dos veces:

| | superficie | locales |
|---|---|---|
| la suma de los 41 por separado | 5.866,77 ha | 12.087 |
| **la unión de los 41** | **5.434,11 ha** | **10.801** |
| lo que se contaba de más | 432,65 ha | 1.286 |

Los 1.286 están repartidos en **1.263 locales distintos** que caen en dos o más polos: la
diferencia entre las dos cifras es que hay locales en tres polos a la vez, y cada uno aparece en
los tres pares.

---

## 4 · Las 124 concentraciones contra los bordes de ahora

| | concentraciones | locales | ha |
|---|---|---|---|
| contenidas o mayormente dentro de un polo | **53** | 6.800 | 1.355,42 |
| tocan un borde sin quedar mayormente dentro | 28 | 2.818 | 782,87 |
| fuera de todo polo | 43 | 2.902 | 1.005,26 |

**La cifra publicable: 53 de las 124 caen dentro de algún polo y 71 no; las 71 suman 5.720
locales.**

Las más grandes de las 43 que quedan enteramente fuera: Palermo Botánico (207 locales), Congreso
(175), Palermo · Bustamante y Mario Bravo (154), Alto Palermo (141), el centro comercial de Av.
Cuenca (135) y Av. Eva Perón entre Escalada y Castañares (132).

«Dentro» se resolvió por superficie perdida —`concentración.difference(polo).area`— y no con un
predicado: una concentración cuenta como dentro si le queda menos del 1 % de su superficie afuera,
o si más de la mitad cae dentro de un polo.

**Archivo: `correspondencia_124_x_41.csv`**, 124 filas.

---

## 5 · Las cinco páginas sin ningún establecimiento con historia adentro

Para cada una se midió **qué pasaría si el borde se extendiera lo mínimo necesario** para contener
a los que hoy quedan afuera. **No se adopta ninguna.**

**La regla de extensión, escrita antes de medir:** para cada establecimiento se toma la calle de su
dirección y el tramo de esa calle que va del borde hasta su puerta —ni una cuadra más—, con las
manzanas frentistas y el mismo frente mínimo de 20 m con el que se trazó todo lo demás.

| página | ahora | extendido hasta contenerlos a todos | × superficie | calles que el texto ya nombra |
|---|---|---|---|---|
| La Boca · Almirante Brown y Necochea | 6,14 ha · 3 locales | 58,81 ha · 100 locales | 9,6× | **3 de 8** |
| Balvanera · Once | 19,18 ha · 74 locales | 51,30 ha · 231 locales | 2,7× | 0 de 3 |
| Nueva Pompeya y Parque Patricios | 69,06 ha · 112 locales | 82,79 ha · 117 locales | 1,2× | 0 de 1 |
| Nueva Pompeya · eje Av. Sáenz | 39,39 ha · 52 locales | 53,12 ha · 57 locales | 1,3× | 0 de 1 |
| Liniers · Mercado Andino | 7,00 ha · 63 locales | 8,07 ha · 70 locales | 1,2× | 0 de 1 |

La columna que decide es la última, y es la que traduce el criterio con el que se resolvieron
Caminito y Balvanera: **de los catorce establecimientos que las cinco páginas dejan afuera, sólo
tres están sobre una calle que el perímetro escrito de su página ya nombra.** Los tres son de La
Boca · Almirante Brown y Necochea.

Hay una segunda prueba, geométrica y publicada aparte: **si la calle llega o no hasta el borde.**
Nueve de los catorce están sobre calles que ni siquiera tocan el polígono, así que la extensión
quedaría en dos piezas sueltas.

### Mis dos renglones por cada una

**La Boca · Almirante Brown y Necochea.** Extendería, pero sólo sobre Av. Suárez y Olavarría, que
la delimitación de obra pública que la página cita ya nombra: **16,17 ha y 21 locales**, tres de
los ocho adentro —Banchero a 54 m, La Buena Medida a 106 y el Café Roma a 111— y la figura sigue
siendo una sola pieza.
No iría por los otros cinco: llegar hasta ellos multiplica la superficie por 9,6, exige cinco
calles que el texto no nombra y que no tocan el borde, y uno de los ocho —La Perla— ya está dentro
de Caminito, que se extendió justamente para contenerla; traérsela sería contarla dos veces.

**Balvanera · Once.** No lo reabriría: la decisión ya está tomada, se adoptó la lectura del enclave
y la extendida quedó publicada como alternativa medida.
Lo que esta corrida agrega es la cota de lo que se descartó: contener a los tres —el Café de los
Angelitos, El Tropezón y Roma del Abasto— cuesta 51,30 ha y 231 locales, casi el triple del
enclave, y ninguna de las tres calles toca el borde; la lectura publicada de 44,75 ha llega sólo
hasta el Café, que es el único de los tres con vigencia verificada este año.

**Nueva Pompeya y Parque Patricios** y **Nueva Pompeya · eje Av. Sáenz.** No extendería ninguna de
las dos. Esquiú sí toca el borde, así que la figura no se parte, pero el perímetro escrito no la
nombra y el precio es **13,73 hectáreas por cinco locales**: se agregaría superficie casi vacía
para alcanzar un establecimiento.
Y El Buzón sostiene las dos páginas a la vez porque las dos se recortan de la misma zona: es un
caso para escribir una vez, en las dos páginas, y no para mover dos bordes.

**Liniers · Mercado Andino.** No extendería. El costo es el más bajo de las cinco —+1,07 ha y +7
locales— pero la única forma de llegar a El Ciervo es por Carhué, que el perímetro escrito no
nombra —nombra José León Suárez, Ramón Falcón, Ibarrola y Ventura Bosch— y que además queda a 124
m del polígono: la extensión sale en dos piezas sueltas.
Es exactamente el caso de la regla al revés: llegar hasta él cambia el objeto que la página
describe, que es un eje con transversales y no un cuadrante.

**Archivos: `cinco_sin_ancla_adentro.csv`** (5 filas, una por página, con las tres versiones
medidas) y **`cinco_sin_ancla_detalle.csv`** (14 filas, una por establecimiento, con su calle, si
el texto la nombra, si toca el borde y cuánto costaría ir sólo por él). Las geometrías de las
versiones, en `geometria/cinco_sin_ancla_versiones.geojson`.

---

## 6 · Los que quedan cerca del borde, recalculados

Rehecho contra la geometría de ahora. **80 establecimientos con reconocimiento quedan fuera de
todos los bordes** y **45 de ellos a 250 m o menos**. Antes eran 60 y 41.

**Por qué subió, que no es lo que parece.** No aparecieron establecimientos nuevos: **los
perímetros trazados son más chicos que los soportes provisorios que reemplazaron.** Los 20 que
pasaron a estar afuera estaban dentro de un soporte que ya no es la geometría publicada: nueve en
el de Caminito, tres en el de Mataderos, tres en el de Almagro, dos en el de Balvanera, dos en el
de Nueva Pompeya y uno en el de Parque Avellaneda. Ninguno dejó de estar afuera.

**El corte de 250 m sigue siendo una prioridad de inspección y no una prueba de que el borde esté
incompleto.** La sensibilidad se publica: 27 a 100 m, 45 a 250 y 58 a 500, sobre 80.

**Lo que esta corrida agrega es la distinción que decide qué hacer con cada uno:**

| qué haría falta | cuántos |
|---|---|
| extender sobre una calle que el perímetro escrito ya nombra, y que toca el borde | **12** |
| una calle que el perímetro escrito no nombra | 33 |

Los doce son los únicos que se resolverían sin inventar una línea, y ésos sí son casos para
revisar:

| establecimiento | dirección | polo más cercano | m | el borde pasaría a |
|---|---|---|---|---|
| Bar Plaza Dorrego | Defensa 1098 | San Telmo | 27,2 | 29,40 ha · 90 locales |
| El Tropezón | Av. Callao 248 | Avenida Corrientes | 36,4 | 52,32 ha · 369 locales |
| Caseros | Av. Caseros 486 | Boulevard Caseros | 54,1 | 53,70 ha · 82 locales |
| Banchero | Suárez 396 | La Boca · Almirante Brown y Necochea | 54,1 | 8,34 ha · 9 locales |
| Duhau Restaurante & Vinoteca | Av. Alvear 1661 | Retiro | 61,8 | 470,67 ha · 723 locales |
| Mercado de San Telmo | Defensa 961 | San Telmo | 64,2 | 32,81 ha · 140 locales |
| Chuí | Loyola 1250 | Villa Crespo | 92,4 | 344,07 ha · 837 locales |
| La Buena Medida | Suárez 101 | La Boca · Almirante Brown y Necochea | 106,5 | 10,17 ha · 10 locales |
| Café Roma | Olavarría 409 | La Boca · Almirante Brown y Necochea | 110,9 | 10,73 ha · 13 locales |
| Bar Imperio | Av. Callao 181 | Avenida Corrientes | 124,8 | 55,72 ha · 389 locales |
| Pirilo | Defensa 821 | San Telmo | 223,4 | 36,89 ha · 171 locales |
| Corte Comedor | Av. Olazábal 1391 | Belgrano | 233,8 | 48,72 ha · 369 locales |

Tres de los doce son de La Boca · Almirante Brown y Necochea, tres de San Telmo y dos de Avenida
Corrientes. **Que la misma página aparezca tres veces acá y tres veces en el control de anclas no
es una coincidencia: es el mismo borde, contado por dos caminos distintos.**

**Un dato de la capa, no de la geometría:** las 45 filas son **44 establecimientos**. El Café Roma
está cargado dos veces —dos identificadores, dos direcciones distintas, «Olavarría 409» y «San
Luis 3101», y un solo punto—. La capa tiene **nueve grupos de filas que comparten coordenada, 20
filas en total**; los otros ocho son el mismo restaurante cargado por dos catálogos, con la misma
dirección, y no cambian ningún conteo de esta tanda. El del Café Roma sí, porque las dos
direcciones no son la misma. Va en la columna `mismo_punto_que`.

**Dos casos de contacto de borde** —a 0,2 y 2,3 m— se publican aparte y no se cuentan entre los
80, igual que en la medición anterior.

**Archivos: `hitos_cerca_del_borde.csv`** (80 filas) y **`hitos_contacto_de_borde.csv`** (2 filas).

---

## 7 · La verificación de cifras, y algo que hay que decir antes

**Resultado: 5 cifras del texto no coinciden con su fuente, 12 sí y 28 todavía no se usan en
ningún documento.** Ninguna dejó de coincidir y ninguna empezó a coincidir: son las mismas cinco
de la vez pasada.

| cifra | dice el texto | dice la fuente |
|---|---|---|
| polos sin borde propio | dieciocho | **3** |
| locales en los polos sin borde | 3.227 | **527** |
| hectáreas en los polos sin borde | 893,5 | **112,9** |
| objetos territoriales separados | 39 | **40** |
| superficie de la unión de las concentraciones | 3.128,5 ha | **3.143,53 ha** |

Las cuatro que el pedido marcaba están anotadas en la fuente para que nadie las «corrija» al
revés: **polos sin borde propio = 3** —Villa Santa Rita, que no tiene ningún trazado, y Núñez y
Retiro, que publican el polígono de su barrio—, **más uno con borde transitorio**, que es
Mataderos y por eso sale de la lista de los tres; **lugares separados = 40**; **Caminito 4,15 ha y
37 locales**; **Mataderos 43,99 ha y 17 locales, transitorio**.

### Lo que hay que decir: el documento en disco no tiene lo de la tanda anterior

La verificación se corrió sobre los 87 documentos del atlas, y el resultado obliga a una
aclaración. **Ninguna de estas cifras está escrita en ningún documento:**

| cifra | ¿aparece? |
|---|---|
| 42 establecimientos con historia fuera de su borde | **no aparece en ninguno** |
| Mataderos 43,99 ha | **no aparece en ninguno** |
| Balvanera, lectura extendida 44,75 ha | **no aparece en ninguno** |
| unión de los 41: 5.434,11 ha y 10.801 locales | no aparece (es de hoy) |
| 1.263 locales en dos o más polos | no aparece (es de hoy) |

Caminito 4,15 ha y 37 locales aparecen, pero **sólo en el documento de cierre geométrico anterior,
donde figuran como lectura medida y no adoptada**, no en el atlas. Villa Ortúzar 34,39 ha y el
solape de 15,93 ha sí están en el atlas.

El archivo del atlas en disco es del 10/08 a la 01:00 y la tanda anterior corrió a las 15:39 del
mismo día: **el documento que hay en el repositorio es anterior a lo que se le incorporó.** No es
un desacuerdo sobre las cifras —las cifras están medidas y guardadas— sino sobre qué versión del
documento está en disco. La verificación de esta tanda se corrió contra la que hay.

**Archivos: `cifras_canonicas.json`** (45 cifras, 15 nuevas o actualizadas), **`verificacion_cifras.json`**
y **`presencia_en_documentos.json`**, que es la búsqueda de la cadena exacta y no del patrón.

---

## 8 · Lo que no se pudo resolver, y por qué

1. **El commit.** El índice de git está trabado por un `.git/index.lock` que sigue ahí. Por regla
   no se toca ese archivo, así que la tanda queda sin commitear y hay que destrabarlo a mano.
   Van siete tandas.
2. **La verificación se corrió contra un documento anterior a la incorporación.** Lo del §7: el
   archivo del atlas en disco es de la 01:00 y no contiene el control de anclas ni los bordes
   nuevos. Si la versión incorporada existe en otro lado, hay que traerla al repositorio y volver
   a correr la verificación; los números canónicos ya están al día y esperando.
3. **Las cinco cifras viejas de la prosa** siguen sin corregir. La corrección la firma quien
   escribe: el verificador señala y no toca el texto.
4. **La decisión sobre las cinco páginas no es mía.** Están las dos cifras de cada una y mi
   lectura en dos renglones; la firma no.
5. **El Café Roma está cargado dos veces en la capa de reconocimiento**, con dos direcciones
   distintas y un solo punto. No se corrigió acá porque la capa no es de esta tanda: se marca en
   la columna `mismo_punto_que` y hay que decidir cuál de las dos direcciones es la buena.
6. **Mataderos sigue sin borde cerrado.** El transitorio es un lugar donde apoyar el mapa. Lo que
   lo cerraría es el perímetro de ocupación de la Feria, que es un dato administrativo que este
   repositorio no tiene.
7. **De los 33 que quedan cerca del borde y exigirían una calle que el texto no nombra, no se
   propone nada.** Medirlos uno por uno no alcanza para decidirlos, y el motivo no es geométrico:
   la prueba de «¿lo nombra el texto?» se corre contra el perímetro escrito de cada página, y ese
   texto es de calidad desigual —hay páginas que dan calles y alturas y hay páginas que no
   escriben perímetro—. Antes de decidir esos 33 hay que saber contra qué texto se los está
   midiendo, página por página. Eso no se hizo acá.

---

## Archivos de esta carpeta

| archivo | qué es |
|---|---|
| `solapes_declarados.csv` | los 25 pares que comparten superficie, con los locales compartidos |
| `solapes_locales_detalle.csv` | qué locales son, por identificador, barrio y comuna |
| `correspondencia_124_x_41.csv` | las 124 concentraciones contra los bordes de ahora |
| `cinco_sin_ancla_adentro.csv` | las cinco páginas, con las versiones medidas |
| `cinco_sin_ancla_detalle.csv` | los 14 establecimientos, uno por uno |
| `hitos_cerca_del_borde.csv` | los 80 que quedan fuera, ordenados por distancia |
| `hitos_contacto_de_borde.csv` | los 2 que están a menos de 3 m |
| `geometria/bordes_vigentes_41.geojson` | la capa vigente completa, EPSG:4326 |
| `geometria/cinco_sin_ancla_versiones.geojson` | las versiones A, B, C y D de las cinco |
| `cifras_canonicas.json` · `verificacion_cifras.json` · `presencia_en_documentos.json` | las cifras, el texto contra ellas y qué está escrito |
| `SOLAPES_Y_CORRESPONDENCIA.txt` · `CINCO_SIN_ANCLA_ADENTRO.txt` · `HITOS_CERCA_DEL_BORDE.txt` · `VERIFICACION_CIFRAS.txt` | la salida completa de cada corrida |
| `geometria_vigente_19.py` · `solapes_y_correspondencia.py` · `cinco_sin_ancla_adentro.py` · `hitos_cerca_del_borde.py` · `cifras_y_verificacion.py` | los scripts, en ese orden |
