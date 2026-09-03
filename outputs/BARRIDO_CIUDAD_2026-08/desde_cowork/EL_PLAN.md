# El plan del trabajo que queda

**Agosto de 2026.** Escrito después de mirar todo lo que hay en el proyecto: las trece geometrías,
las capas administrativas, los 56 mapas del documento, el código que los genera, la base de 27.727
locales y las cuatro notas del equipo de Patricia.

---

## Lo primero, y es la buena noticia

**Los cuatro puntos que trajiste son el mismo punto, y vos ya lo habías encontrado.**

> *«hay un tema más importante creo yo, hacer que toda la base sobre la que se hace todo sea más
> clara así poder delimitar todos los polos con calles»*

Eso es la raíz. Los cuatro pedidos son ramas de esa raíz:

| lo que pidieron | qué necesita para poder contestarse |
|---|---|
| **1 · dividir por comunas y barrios** | que cada local esté atribuido sin ambigüedad a un barrio |
| **2 · delimitar de inicio a fin cada corredor** | que el borde del polo esté hecho de calles |
| **3 · consumidores de cercanía / densidad poblacional** | que el polo tenga una superficie que signifique algo |
| **4 · si adentro del polo hay algún mercado** | que «adentro» sea una pregunta con respuesta binaria |

**Las cuatro se resuelven de una sola vez si se cambia la unidad con la que está armado todo.** Ese
es el plan. Lo demás son consecuencias.

---
---

# 1 · El diagnóstico · por qué los mapas no se entienden

Miré los 56 mapas y el código que los dibuja. **Tienen un solo problema, y produce todos los
síntomas.**

> **Los polos están dibujados como manchas derivadas de los puntos, y abajo no hay calles.**

Las manchas salen de inflar los locales con un radio y unir lo que se toca. Es un método rápido y
razonable para *encontrar* una concentración. **Es un método imposible para *publicar* una.**

### Los seis síntomas, con la evidencia

**Primero: una mancha no tiene dirección.** El mapa de «Avenida Boedo» no tiene dibujada la Avenida
Boedo. Es una lonja naranja vertical sobre un fondo vacío. Nadie puede decir dónde empieza ni dónde
termina —que es, textual, lo que pidió el equipo de Patricia.

**Segundo: no hay una sola calle en ningún mapa.** Ni una. Lo verifiqué en el código que los genera:
las capas que se dibujan son comunas, barrios, concentraciones, polos e hitos. **Calles, ninguna.**
Las líneas grises finas que uno cree ver son límites de barrio. Un mapa de la Ciudad sin calles es un
mapa que el lector no puede cotejar contra nada de lo que conoce.

**Tercero: los locales son invisibles.** El atlas es sobre 11.119 locales adentro de los polos y en
los mapas **no se ve ni uno**. Los puntos negros que aparecen son los establecimientos con historia
—unos pocos por mapa—. La densidad que justifica cada polo no está representada.

**Cuarto: las superficies están infladas, y once polos ya no son polos.**

| polo | superficie | locales |
|---|---:|---:|
| Chacagiales | 495,8 ha | 891 |
| Devoto | 478,7 ha | 422 |
| Villa Urquiza | 446,6 ha | 528 |
| Núñez | 442,6 ha | 494 |
| Retiro | 415,0 ha | 414 |
| Palermo | 385,5 ha | 1.916 |
| La Paternal | 377,3 ha | 293 |
| Puerto Madero | 314,5 ha | 354 |
| Villa Crespo | 293,8 ha | 746 |
| Caballito | 225,4 ha | 508 |
| Villa Santa Rita | 215,5 ha | 182 |

**400 hectáreas son dos kilómetros por dos kilómetros.** Eso no es un polo gastronómico: es un
barrio. Y no es que el territorio sea así — es que la mancha, al unir concentraciones separadas por
diez cuadras vacías, se traga las diez cuadras vacías.

**Y se puede medir exactamente cuánto se las traga.** Medí qué porción del barrio ocupa la mancha de
cada polo:

| polo | ocupa, de su barrio |
|---|---:|
| Chacagiales | **216 %** de Colegiales — el doble del barrio |
| La Paternal | **169 %** de La Paternal |
| Núñez | 100 % |
| Villa Santa Rita | 100 % |
| Retiro | 92 % |
| Villa Urquiza | 82 % |
| Villa Crespo | 81 % |
| Devoto | 75 % |
| **Avenida Boedo** | **69 % del barrio Boedo** |
| Centro y Microcentro | 67 % de San Nicolás |
| Puerto Madero | 62 % |

**Once de los 41 polos ocupan más de la mitad de su barrio.** Y el caso que lo dice todo es el
noveno: *Avenida Boedo* es **un corredor** —una avenida, dos veredas— y su figura cubre **más de dos
tercios del barrio entero**. Un corredor no puede ser dos tercios de un barrio. La figura no está
describiendo la avenida: la está reemplazando.

**Quinto, y es el más caro: la densidad mide el dibujo, no el territorio.** Los 41 polos van de
**0,15 a 9,66 locales por hectárea: un factor de 66.** Ese rango no describe la Ciudad, describe
cuánto se infló cada mancha. **El documento cita densidad 54 veces y hectáreas 212 veces.** Todas esas
cifras están apoyadas sobre una superficie que es un artefacto del método de dibujo.

**Sexto: el fondo está lleno de formas pálidas.** Son las 124 «concentraciones detectadas» —el paso
intermedio del método: los grupos que se encontraron antes de decidir cuáles llegaban a polo—. La
leyenda las nombra, pero el nombre no le dice al lector qué hacer con ellas, y **en varios mapas
ocupan más superficie visual que los polos mismos**: en la Comuna 5, el fondo es casi todo
concentraciones. El lector no puede distinguir lo que el atlas afirma de lo que el atlas descartó.

### Lo bueno: la mitad del punto 1 ya está hecha

**El atlas ya está organizado por comuna.** La sección de polos va Comuna 1, Comuna 2, Comuna 3…, y
al final hay un cierre —*La Ciudad, comuna por comuna*— con **quince mapas, uno por comuna**, que
están generados y sí están en el documento.

Así que el pedido de dividir por comunas no arranca de cero. **Le faltan dos cosas:**

**Falta el barrio.** El límite de barrio está dibujado, pero en un gris tan claro que se pierde
contra el fondo y **sin el nombre escrito**: funcionalmente no está. El pedido era comunas *y* dentro
de las comunas los barrios, y hoy el lector ve un contorno de comuna con manchas adentro sin poder
decir en qué barrio cae cada una.

**Y falta contenido.** Cada comuna del cierre tiene el mapa y una línea con los nombres de sus polos.
Nada más: ni cuántos locales, ni qué rubros, ni qué barrios, ni qué mercados. **Son quince páginas
que hoy no dicen casi nada, y son el lugar natural donde poner todo lo que sale de este plan.**

Los quince mapas, además, **arrastran los mismos seis problemas**: no tienen calles, no muestran los
locales, el fondo está lleno de concentraciones pálidas, y en la Comuna 5 la leyenda se apoya encima
del polo de Avenida Boedo.

---
---

# 2 · La idea · cambiar la unidad, de punto a manzana

**La manzana es la pieza que falta.** Todo lo demás sale solo.

> Hoy un polo es **un conjunto de puntos inflados**.
> A partir de acá, un polo es **un conjunto de manzanas**.

### Por qué esto resuelve las cuatro cosas de una

**Una manzana está rodeada de calles por definición.** No hay manzana sin calles alrededor: es lo que
la hace manzana. Entonces:

**→ El borde de un polo pasa a ser un perímetro de calles, automáticamente.** No hay que dibujarlo a
mano ni decidir nada: se eligen las manzanas y el borde ya está hecho de calles. *(Punto 2, resuelto
por construcción.)*

**→ Las manzanas anidan dentro de barrios, y los barrios dentro de comunas.** Cada local queda
atribuido a un barrio sin ambigüedad y sin cruces por nombre —que es donde se pierden datos en
silencio: la capa vieja escribe «La Boca» y la oficial escribe «Boca»—. *(Punto 1.)*

**→ Una superficie de manzanas es una superficie real**, y entonces la población que vive adentro se
puede repartir con un método declarable. *(Punto 3.)*

**→ Un mercado está parado sobre una manzana.** «¿Está adentro del polo?» pasa a ser sí o no, sin
criterio. *(Punto 4.)*

### Lo que gana el lector, que es lo que a vos te importa

Hoy la ficha de un corredor dice *«Avenida Boedo · 179,5 ha · 245 locales»* y muestra una lonja.

Con manzanas, la misma ficha pasa a tener **esta forma** —los números y las calles del ejemplo son
inventados, sirven para mostrar la forma; los reales salen de la Etapa 3—:

> **Av. Boedo, de [calle] a [calle]** — las manzanas de las dos veredas. **[n] manzanas · [n] ha ·
> 245 locales · [n] por hectárea.**

**Esa frase se puede caminar**, y cualquiera puede pararse en la esquina y verificarla. Y el mapa que
la acompaña tiene la avenida dibujada, con su nombre, y las dos transversales que la cierran escritas
en los extremos.

Los 245 locales son el único número que no se mueve: **los locales están donde están.** Lo que cambia
es la figura que los contiene, y con ella la superficie y la densidad.

### Cómo se elige el conjunto de manzanas · la regla de armado

**Ojo, que esto no toca el criterio de admisión.** Las seis condiciones que deciden *si un lugar es
un polo* quedan como están: esto decide, una vez admitido, *qué manzanas lo forman*. Son dos
preguntas distintas y conviene no mezclarlas.

La regla tiene que estar escrita y ser la misma para los 41. La propuesta, y cada paso es discutible:

1. **Manzana admitida** — la que contiene locales del polo por encima de un umbral. Para corredores
   el umbral se aplica sobre la vereda, no sobre la manzana entera.
2. **Las dos veredas siempre juntas** — una avenida gastronómica no es una vereda: si entra un lado,
   entra el de enfrente. Es la corrección de un defecto real del dibujo actual.
3. **Se tapan los huecos interiores** — una manzana rodeada de manzanas admitidas entra, aunque no
   tenga locales. Una plaza, una escuela o un terreno adentro del polo no lo parte en dos.
4. **Continuidad obligatoria** — el conjunto tiene que ser una sola pieza. Lo que queda suelto o es
   un polo aparte con nombre propio, o no entra. **Ahí es donde se van las 400 hectáreas**: los
   pedazos separados por diez cuadras dejan de estar unidos por una mancha que los abraza.
5. **Los bordes se estiran al eje de la calle**, no al filo de la parcela, para que dos polos vecinos
   no dejen una franja de nadie entre ellos.

### La verificación que sale gratis, y es fuerte

**10.890 locales de la base traen su código de manzana** —vienen del Relevamiento de Usos del Suelo,
que registra sección, manzana y parcela—. Cuando asigne cada local a una manzana por geometría, esos
10.890 son un **testigo independiente**: el código que ya traen tiene que coincidir con la manzana en
la que cae el punto.

Si coinciden por encima del 99 %, la asignación geométrica queda probada, y entonces se puede confiar
en ella para **los 17.000 locales que no traen código**. Si no coinciden, aparece exactamente dónde
está el problema. **Es una prueba que no cuesta nada y decide si todo lo demás se apoya en algo
firme.** Se hace primero.

---
---

# 3 · Lo que falta, y de dónde sale

**En todo el proyecto no hay una capa de manzanas ni una capa de calles.** Lo verifiqué archivo por
archivo: hay trece geometrías de polos, la capa de barrios y la de comunas, y nada más. Es el insumo
que falta y es el que sostiene el plan entero.

Las cuatro capas están publicadas y son abiertas. **Ninguna se puede bajar desde acá**: el portal de
datos de la Ciudad no es alcanzable desde este entorno —lo probé, no responde—, así que **las bajás
vos**. Está el bloque para pegar al final.

| capa | para qué | estado |
|---|---|---|
| **Manzanas catastrales** (GeoJSON) | la unidad atómica de todo | publicada · [ficha](https://data.buenosaires.gob.ar/dataset/manzanas/resource/78a97854-6930-4d1c-b345-deb43168d88d) |
| **Callejero** (GeoJSON) | nombrar los bordes y dibujar la base de los mapas | publicada · **actualizada el 07/08/2026**, cuatro días atrás · [ficha](https://data.buenosaires.gob.ar/dataset/calles/resource/2941f731-0a2e-4391-b8c9-a2912a80c081) |
| **Información censal por radio** (GeoJSON) | los consumidores de cercanía | publicada, **con una salvedad, abajo** · [ficha](https://data.buenosaires.gob.ar/dataset/informacion-censal-por-radio) |
| **Ferias y Mercados** | el punto 4 | publicada · [ficha](https://data.buenosaires.gob.ar/dataset/ferias-mercados) |

### La salvedad del censo, y hay que decidirla

**La Ciudad publica por radio censal el Censo 2010 y el 2001. No publica el 2022 a esa escala.** Y
2010 es hace dieciséis años, en una ciudad donde Puerto Madero, Núñez, Villa Urquiza y Barracas
cambiaron de población de manera fuerte. Usar 2010 sin decirlo sería un error.

Hay tres caminos y ninguno es obvio:

- **Usar 2010, declarado como 2010.** Es la capa oficial de la Ciudad, es geográfica, se cruza
  directo. Sirve para comparar polos entre sí —la forma— aunque el nivel esté viejo.
- **Buscar el 2022 por radio**, que existe fuera del portal de la Ciudad —hay una cartografía de
  radios censales de todo el país con población y densidad, publicada en un repositorio académico
  abierto—. Es más actual y es citable, pero es de terceros y hay que verificar que los radios
  cierren con los de la Ciudad.
- **Las dos, y que la diferencia sea el hallazgo.** Donde 2010 y 2022 se separan mucho, eso *es* la
  noticia sobre ese polo.

**Mi recomendación es la tercera**, y si hay que elegir una sola, la primera con la fecha escrita en
cada tabla. Pero la decisión es tuya.

### Y una cosa que encontré mirando los mercados

**La capa de hitos del proyecto tiene 8 registros de tipo «Mercado/patio». Uno de ellos no es un
mercado**: *Yiyo el Zeneize*, en Parque Avellaneda, está cargado como mercado y es una pizzería.
Quedan siete: San Telmo, Belgrano, Progreso, Bonpland, Patio de los Lecheros, Patio Costanera Norte
y Patio Gastronómico Rodrigo Bueno.

**Siete es muy poco para contestar el punto 4.** Faltan, por lo menos, el Mercado de Liniers /
Andino —que da nombre a un polo del atlas—, el de Flores, el Mercado de San Nicolás, el de Las Luces,
el de Los Carruajes, y toda la red de ferias itinerantes. **Contestar «si dentro de los polos está
alguno de los mercados» con una lista de siete es contestar mal.** Por eso la capa oficial de Ferias
y Mercados está en la lista de arriba.

---
---

# 4 · Las etapas

Ocho. Cada una dice qué produce y cómo se comprueba. **Las que dependen de vos están marcadas.**

### Etapa 0 · Las capas · **te toca a vos** · diez minutos

Bajar las cuatro capas y dejarlas en el repositorio. Bloque para pegar, al final.

### Etapa 1 · La base pasa a estar hecha de manzanas · medio día

Cada uno de los 27.727 locales queda asignado a una manzana, a un barrio y a una comuna, por
geometría y no por nombre.

- **Se comprueba** contra los 10.890 códigos de manzana que ya trae la base.
- **Se comprueba** que el barrio geométrico coincida con el campo `barrio` que ya está cargado, y se
  listan las diferencias una por una, sin corregir nada en silencio.
- **Produce** `manzana.csv` —una fila por manzana con locales, rubros, superficie, barrio y comuna— y
  eso pasa a ser **la espina dorsal del proyecto**. Todo lo demás se cuelga de ahí.
- **Riesgo conocido:** los locales geocodificados a la calle en vez de al frente caen en el asfalto y
  no dan manzana. Se resuelven por vecino más cercano a menos de 25 metros y **quedan marcados**, no
  escondidos.

### Etapa 2 · Los 41 polos redibujados sobre manzanas · dos días

Aplicar la regla de armado —los cinco pasos de arriba— a cada polo, medir todo de nuevo y **publicar
la tabla de lo que cambió**: superficie vieja contra nueva, locales viejos contra nuevos, cuántas
manzanas.

- **Produce** también, y esto es lo importante, **una respuesta a los cuatro polos que hoy no tienen
  borde propio** —Núñez, Villa Santa Rita y Retiro se están dibujando con el barrio entero, y
  Mataderos con un borde tentativo—. Con manzanas se dibujan como todos los demás.
- **Riesgo real:** algunos polos se van a partir en dos o tres piezas al aplicar continuidad. Eso no
  es un error del método: es lo que el método está para encontrar. **Cada partición se decide con
  vos**, no automáticamente.

### Etapa 3 · El borde escrito · un día

Para cada polo, generar la frase de delimitación cruzando su perímetro contra el callejero: qué calle
lo cierra por cada lado, y en los corredores, de qué transversal a qué transversal.

- **Produce** una tabla de 41 filas —*«de X a Y por Z, entre W y V»*— que **es la respuesta literal
  al punto 2** y que además cualquiera puede verificar caminando.
- **La máquina escribe el borrador; vos revisás 41 frases.** No es automático del todo y no conviene
  que lo sea: las diagonales, las plazas, las vías del tren y los pasajes sin salida necesitan ojo.
- **Riesgo:** el eje de la calle y el filo de la manzana están separados por media calzada. Se
  resuelve con tolerancia y control de paralelismo, y se revisa a mano donde el nombre no cierre.

### Etapa 4 · La cartografía nueva · tres o cuatro días

Es la etapa larga y es la que más se ve. Tiene su sección propia, más abajo.

### Etapa 5 · Los consumidores de cercanía · un día

- Población que vive **adentro** del polo, repartida desde los radios censales con peso por
  superficie de manzana, con el método escrito.
- Población en **el anillo caminable**: 400 metros —cinco minutos— y 800 metros —diez—. Esta medida
  es la robusta, porque casi no depende de dónde caiga exactamente el borde.
- **Locales cada mil residentes**, que es la cifra que convierte esto en un hallazgo y no en un dato:
  separa **el polo de barrio** —que le cocina a quien vive al lado— del **polo de destino** —que le
  cocina a quien viene—. Puerto Madero, Caminito y el Microcentro van a caer de un lado; Devoto,
  Villa Pueyrredón y Boedo del otro. **Esa distinción no está en el atlas y vale una sección.**

### Etapa 6 · Los mercados · medio día

Cruzar la capa oficial contra los 41 polos y contestar el punto 4 con una tabla: qué mercado, en qué
polo, a cuántos metros del borde el que quede afuera y cerca. Corregir de paso los siete registros de
la capa de hitos y sacar la pizzería de la categoría equivocada.

### Etapa 7 · Reconciliar el documento · dos o tres días

**Esta es la etapa que hay que mirar antes de empezar, no después.** Está en la sección 6.

### Etapa 8 · Verificación · un día

Recontar todo contra la base: superficies, locales, densidades, población, mercados. Cotejar las 41
frases de delimitación contra el callejero. Revisar los mapas uno por uno buscando etiquetas pisadas,
leyendas encima del dibujo y escalas mal puestas.

---
---

# 5 · La cartografía nueva, en concreto

Dijiste que es lo que más se ve y con lo que se van a quedar. **Entonces las reglas se escriben antes
de dibujar.**

## Tres escalas, y cada una contesta una pregunta distinta

| escala | la pregunta que contesta | cuántos |
|---|---|---:|
| **La Ciudad** | ¿dónde está la gastronomía de Buenos Aires? | 1 |
| **La comuna** | ¿qué hay en mi comuna, y en qué barrio? | 15 |
| **El polo** | ¿por dónde camino y qué voy a encontrar? | 41 |

## Lo que entra en cada mapa

**Las calles, siempre.** Es el cambio de fondo. Las avenidas con trazo grueso y **con su nombre
escrito**; las calles comunes finas; en la escala de polo, todas nombradas.

**Los locales, siempre.** Son el tema del atlas. Puntos chicos, un color por rubro en la escala de
polo, gris parejo en las otras. **Que se vea la concentración que justifica el polo.**

**El borde, apoyado en la calle.** Trazo firme, relleno translúcido para que las calles se sigan
leyendo por debajo. Y en los corredores, **las dos transversales que lo cierran escritas sobre el
mapa, en los extremos** — eso es el punto 2 dibujado.

**Los barrios adentro de la comuna**, con línea punteada y nombre. Es el punto 1 dibujado.

**Los mercados**, con un símbolo propio. Punto 4.

**Escala gráfica, norte y un recuadro de ubicación** en los 41 mapas de polo, siempre en el mismo
lugar de la hoja.

## Lo que sale

- **Las 124 «concentraciones detectadas».** Son un paso intermedio del método, no un hecho del
  territorio, y en varios mapas tapan a los polos. *(Si querés conservarlas, van a un anexo
  metodológico y no al mapa. No se tiran: se mudan.)*
- **Las manchas redondeadas.** Reemplazadas por bordes rectos sobre líneas de calle.
- **Las leyendas encima del dibujo.** Fuera del área de mapa, siempre.

## Las reglas de oficio

- **Escala fija por familia de polos**, para que dos polos se puedan comparar mirándolos. Hoy cada
  mapa tiene su propio zoom y eso engaña: Caminito y Devoto ocupan lo mismo en la hoja siendo uno
  cien veces más chico que el otro.
- **Etiquetas que no se pisan.** En el mapa general hoy «Chacarita · Colegiales» se monta sobre
  «Villa Ortúzar», y el sudeste —Barracas, La Boca, Montes de Oca— es una pila de nombres. Se resuelve
  con corrimiento automático más anclas puestas a mano donde el automático no alcance.
- **Que sobreviva a la fotocopia en blanco y negro** y a un daltónico. Los tres colores de tipo de
  polo se distinguen hoy por tono; van a distinguirse también por trama.
- **Tipografía mínima 7 puntos** a tamaño de impresión real. Varias etiquetas de hoy no llegan.
- **300 dpi y, además, el vector.** Que el mapa se pueda ampliar sin que se rompa, y que la Dirección
  pueda reusarlo.

## Y una hoja por polo, con todo junto

La ficha de cada polo pasa a tener el mapa **y** la frase del borde **y** la tabla de cifras en la
misma hoja. Hoy están separados y el lector tiene que armar el rompecabezas.

## Las quince páginas de comuna, con algo adentro

Hoy cada comuna del cierre es un mapa y una línea de nombres. Pasan a tener: el mapa **con sus
barrios dibujados y nombrados**, cuántos locales tiene la comuna y cuántos están adentro de un polo,
el reparto por rubro, los mercados, la población, y la lista de polos con su frase de delimitación.

**Es la respuesta completa al punto 1**, y de paso convierte quince páginas casi vacías en la parte
del atlas que un funcionario de comuna va a leer primero.

---
---

# 6 · Lo que esto cuesta · los números del atlas se van a mover

**Hay que decirlo antes de empezar y no después.**

Redibujar los polos sobre manzanas **cambia la superficie de los 41**, y con la superficie cambia la
densidad. En el documento eso toca:

| qué | cuántas veces aparece |
|---|---:|
| menciones de hectáreas | **212** |
| de ésas, menciones de densidad por hectárea | **54** |
| fichas de polo con su cifra de superficie | **41** |
| mapas distintos en el documento, a regenerar | **56** — 39 de polo, 15 de comuna, 2 generales |

**Las superficies van a bajar, casi todas.** Los once polos de más de 200 hectáreas van a caer fuerte
—esa es la corrección—, y con la superficie más chica **la densidad de todos ellos va a subir**. El
número de locales, en cambio, casi no se mueve: los locales están donde están; lo que cambia es la
figura que los contiene.

**Tres consecuencias que conviene mirar de frente:**

1. **Un polo puede dejar de calificar.** Si al aplicar continuidad se parte en pedazos chicos, alguno
   puede quedar por debajo de lo que el criterio pide. **Eso se decide con vos, uno por uno.**
2. **La vara de cantidad quedaría resuelta de paso.** Está derivada y probada, sin aplicar, porque
   moverla daba vuelta doce páginas. Con superficies reales, la vara se puede volver a discutir sobre
   cifras que significan algo.
3. **Es una versión nueva del documento, no un parche.** Conviene asumirlo así desde el principio.

**Y por eso hay una decisión que es tuya y va abajo:** redibujar los 41, o congelar los diecinueve
que ya estaban publicados y redibujar sólo los veinte que se suman.

---
---

# 7 · Las decisiones que son tuyas

Ninguna la puedo tomar yo. Están en orden de cuánto bloquean lo demás.

**A · ¿Se redibujan los 41 o se congelan los diecinueve publicados?**
Redibujar todo es coherente y es más trabajo; congelar es más rápido y deja el atlas con dos métodos
adentro, lo cual hay que declarar. **Mi recomendación: redibujar los 41.** Un atlas con dos métodos de
delimitación es exactamente la crítica que recibió la versión anterior.

**B · ¿Qué censo?** 2010 oficial de la Ciudad, 2022 de repositorio académico, o los dos.

**C · ¿La vara de cantidad se aplica en esta versión o no?** Sigue pendiente desde antes.

**D · La nota en la versión anterior.** Las tres opciones que te pasé siguen esperando: sólo la nota
de actualización fechada; la nota más la corrección marcada de tres afirmaciones; o la edición
numérica completa.

**E · ¿Los rubros del Excel se revisan antes o después?** El diccionario de 140 etiquetas y los 110
posibles bodegones están esperando tu media hora. **Si el trabajo que viene es por rubro, esto va
primero**, porque cambia lo que muestran los mapas nuevos.

---
---

# 8 · Lo que ya está resuelto y no hay que volver a tocar

Para que se vea el piso que ya está puesto:

- **La base**, 27.727 locales, siete fuentes con nombre, fecha de corte y licencia, seis grupos de
  independencia, y cada local guarda de cuál vino.
- **El criterio de admisión** —las seis condiciones, al menos dos, de orígenes independientes—.
- **Las categorías**, de 140 etiquetas en cuatro idiomas a 21 rubros, más cocina y atributos.
- **Los repetidos**, medidos: entre 100 y 230 sobre 27.727.
- **La capa de barrios y comunas**, cotejada contra la oficial, con su procedencia documentada.
- **El texto del atlas**, 5.246 líneas, **ya organizado por comuna** —la sección de polos y el cierre
  de quince páginas—, que es la mitad del punto 1 hecha.
- **La corrección de las seis familias de fuentes**, hecha en las tres piezas donde aparecía.

### Y lo chico que sigue suelto, para que no se pierda

Nada de esto bloquea el plan, pero ninguno está cerrado:

- **El commit.** Hay diecinueve y pico de archivos sin commitear en el repositorio. Va en el bloque
  del final, y lo corrés vos desde PowerShell.
- **Trece establecimientos con la vigencia en duda** — figuran abiertos y hay señales de que no.
- **2.524 puntos del Relevamiento de Usos del Suelo a menos de 10 metros de un local con nombre.** No
  se pueden adjudicar desde el escritorio; con manzanas se puede al menos decir si comparten parcela.
- **148 locales que capaz no son gastronómicos** —kioscos, fiambrerías, una farmacia— esperando que
  definas el borde entre gastronomía y comercio de alimentos.
- **110 posibles bodegones** por señal en el nombre, sin tocar.
- **60 pares con el nombre casi igual a menos de 30 metros** — la lista más corta y más segura de
  repetidos, lista para aprobar en bloque.

---

# 9 · El orden

```
0 · bajás las capas                          ← te toca · 10 minutos
1 · la base sobre manzanas + la prueba       ← medio día · acá se decide si el plan camina
2 · los 41 redibujados + tabla de cambios    ← dos días
3 · las 41 frases de borde                   ← un día · revisás 41 frases
4 · la cartografía                           ← tres o cuatro días
5 · población · 6 · mercados                 ← día y medio
7 · reconciliar el documento                 ← dos o tres días
8 · verificación                             ← un día
```

**El punto de control está al final de la Etapa 1.** Si los 10.890 códigos de manzana coinciden con
la geometría, el plan entero se apoya en algo firme y sigue. Si no coinciden, paramos ahí y se ve por
qué antes de dibujar nada.

**Y hay una etapa que puede correr en paralelo desde hoy**, porque no depende de las capas: la
revisión del diccionario de rubros. Es tuya y es media hora.
