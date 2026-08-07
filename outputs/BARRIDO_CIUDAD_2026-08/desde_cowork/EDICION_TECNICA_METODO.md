# Edición técnica · cómo se construyó cada número

**Atlas de Referencias Gastronómicas de la Ciudad de Buenos Aires · Dirección General de
Desarrollo Gastronómico, GCBA**

*Versión de trabajo · 6 de agosto de 2026*

---

## 0 · Qué es este documento y qué no es

Esto no es un resumen del Atlas. Es el documento que explica **de dónde sale cada número**: qué
fuente lo produjo, con qué regla se contó, qué parámetro se eligió, qué se probó para saber si
ese parámetro decidía el resultado, y qué quedó sin poder decidirse.

Está escrito para tres lectores distintos y no pide que se lo lea entero:

- **Quien tiene que defender un número** en una reunión: el índice del final dice qué archivo lo
  produce.
- **Quien tenga que rehacer esto** dentro de dos años, cuando ninguno de nosotros esté: las
  reglas de método de la Parte IX son la parte que no se hereda leyendo el código.
- **Quien quiera discutirlo**: cada decisión está con la prueba que se le corrió y con el número
  que dio, incluidas las que salieron mal.

Hay una convención de redacción que se sostiene en todo el documento y conviene declararla
primero, porque cambia cómo se leen los resultados negativos:

> **«No encontramos» no es «no existe».** Cada vez que una búsqueda no dio resultado, lo que se
> reporta es qué se buscó, con qué cobertura y con qué umbral. La ausencia de un hallazgo es una
> afirmación sobre nuestro instrumento, no sobre el territorio.

Esa regla no es retórica. El Atlas publicado dice «No se identificaron zonas en el extremo sur de
la Ciudad», que es literalmente cierto y se lee como si no hubiera nada. El barrido posterior
encontró diez concentraciones con mil locales ahí. La frase no era falsa: era una afirmación
sobre dónde habíamos mirado, escrita como una afirmación sobre la Ciudad.

---

# Parte I · El objeto

## 1 · Qué es un polo gastronómico, y por qué no es una entidad natural

Un «polo gastronómico» no es un objeto que exista en el territorio con bordes propios, como un
río o una manzana. Es una **categoría de lectura**: una manera de agrupar locales que están
cerca unos de otros y que, tomados juntos, significan algo para quien camina la Ciudad.

Eso tiene una consecuencia metodológica que atraviesa todo el trabajo: **no hay una respuesta
correcta que el método deba encontrar**. Hay decisiones, y lo único que se le puede exigir a un
método es que sus decisiones sean **reproducibles, declaradas y defendibles**.

Por eso, en todo este documento, cada vez que hay un corte se responden tres preguntas:

1. ¿De dónde salió el valor del corte? (Nunca de mirar los datos que va a juzgar.)
2. ¿El resultado cambia si el corte se mueve? (La curva de sensibilidad, publicada.)
3. Si el corte es una convención, ¿está declarado como convención?

Un corte declarado como convención es defendible. Un corte óptimo presentado como frontera
natural se cae en la primera revisión.

## 2 · Las cuatro familias del Atlas publicado

El Atlas V2 publica 22 referencias, y no todas son la misma cosa. La clasificación por familias
—que estaba implícita y ahora está explícita— importa porque **una zona de cada familia se
verifica distinto**:

| familia | qué es | cómo se verifica |
|---|---|---|
| **Polo** | una concentración compacta con nombre propio | un cluster del tamaño de la zona |
| **Polo con subzonas / multiparte** | varias concentraciones bajo un mismo nombre | varios clusters, y el vacío entre ellos se preserva |
| **Eje o corredor** | actividad tendida sobre una avenida | un cluster alargado, o varios sobre el mismo eje |
| **Referencia dispersa** | un área con presencia, sin una concentración que la explique | **no debe producir un cluster del tamaño de la zona** |

La última fila es la que más se malinterpreta. Que una referencia dispersa no produzca un cluster
grande **no la refuta**: la confirma. Lo veremos en la Parte VII con R07 Costanera Norte y R16
Donado-Holmberg.

---

# Parte II · La base

## 3 · Las siete fuentes, y los cinco grupos de independencia

La base reúne siete fuentes. Pero **no son siete testimonios independientes**, y contar fuentes
en vez de grupos es el error más caro que se puede cometer acá: Overture redistribuye a
Foursquare y a All The Places, así que un local «corroborado por tres fuentes» puede estar
corroborado por un solo relevamiento contado tres veces.

Se definieron **cinco grupos de independencia** y todo conteo de corroboración se hace por grupo:

| grupo | qué contiene | licencia | qué aporta |
|---|---|---|---|
| `GCBA_URBANISMO` | Relevamiento de Usos del Suelo | CC-BY-2.5-AR | el piso territorial: cobertura pareja por diseño |
| `GCBA_AGC` | padrón de habilitaciones y trámites | CC-BY-2.5-AR | estado administrativo, con la corrección del §5 |
| `GCBA_ESPACIO_PUBLICO` | permisos de uso del espacio público | CC-BY-2.5-AR | terrazas y superficies exteriores |
| `OSM` | OpenStreetMap | ODbL (share-alike) | actualidad y detalle de nombre |
| `OVERTURE_FSQ_ATP` | Overture + Foursquare + All The Places | CDLA-P / Apache 2.0 / CC0 | volumen; **es un solo grupo, no tres** |

A esto se suma **Google Places** como fuente de descubrimiento, con un tratamiento aparte
descrito en el §10, porque su naturaleza es distinta: no es una base que se pueda enumerar.

**Regla de procedencia.** Ningún registro se colapsa a una versión «verdadera». Cada fuente
conserva lo que dijo, con su identificador de origen. La base tiene dos tablas —`local` y
`local_fuente`— y la segunda es la que permite responder, un año después, por qué un local está.

**Regla de licencia.** Cada registro lleva el nivel de publicación que su fuente más restrictiva
permite:

| nivel | qué se publica | cuándo |
|---|---|---|
| `abierto` | registro completo | la identidad viene de una fuente redistribuible |
| `punto` | punto y categoría, sin nombre ni dirección | la ubicación está corroborada, la identidad no |
| `agregado` | sólo el conteo en una celda o zona | el dato existe únicamente en una fuente no redistribuible |

Google Places cae siempre en `agregado`. De la sonda del §10 entraron al repositorio los totales
por barrio y nada más: ningún punto, ningún `place_id`, ningún nombre.

## 4 · El total, y qué significa

**23.981 puntos** en el universo de trabajo del barrido. Ese número no es «la cantidad de locales
gastronómicos de la Ciudad» y no debe leerse así. Es **la cantidad de locales que las siete
fuentes, unidas y deduplicadas, alcanzan a ver**.

La diferencia entre las dos cosas es el objeto del §9 y del §10, y no se resolvió: se **acotó**.

## 5 · La corrección del padrón · los asientos replicados

Es la corrección más grande que se le hizo a una fuente, y vale la pena contarla entera porque
es el ejemplo de manual de un artefacto que se lee como un hallazgo.

**El síntoma.** El padrón georreferenciado de habilitaciones mostraba concentraciones extremas en
puntos únicos: decenas o cientos de asientos sobre la misma parcela.

**La hipótesis alternativa.** Podía ser real —una galería, un centro comercial, un patio de
comidas— o podía ser una replicación del registro.

**La prueba.** Se usó la clave catastral SMP (sección-manzana-parcela) y el número de partida
matriz. Si los asientos replicados fueran locales distintos en la misma dirección, resolverían a
parcelas distintas o a partidas distintas. Resolvieron **48 de 48 a una sola parcela**.

**El mecanismo, identificado.** El campo `calles` del padrón es **multivalor en el 13,9 % de los
245.563 registros crudos**: una esquina o un local con dos accesos genera un asiento por cada
puerta. Y la geometría de la Ciudad lo amplifica: **15.237 de 42.246 parcelas (36,1 %) tienen más
de una puerta**, y hay una parcela con **237 puertas**.

**La discriminancia, que es la parte que casi se lee mal.** El SMP resuelve a una sola parcela en
el 99,26 % de los casos de toda la Ciudad. Aplicado ingenuamente, eso vuelve la prueba inútil:
0,9926⁴⁸ ≈ 0,70, o sea que **un 70 % de las veces 48 direcciones al azar resolverían a una sola
parcela por casualidad**. La prueba parece no probar nada.

La corrección fue estratificar. La base de acierto por azar **depende de cuántas direcciones
tenga el caso**:

| direcciones del caso | partidas puestas a prueba | resuelven a una | base limpia | probabilidad por azar |
|---|---:|---:|---:|---:|
| 2 | 20 | 20 | 99,60 % | 92,3 % |
| 3–5 | 11 | 11 | 98,35 % | 83,3 % |
| 6–10 | 1 | 1 | 91,27 % | 91,3 % |
| **11 o más** | **5** | **5** | **42,47 %** | **1,4 %** |

**Donde la prueba discrimina es en la última fila.** Ahí la base cae a 42,47 % y la probabilidad
de acertar por azar es 1,4 %. Los casos de 2 y de 3–5 direcciones no prueban nada y se reportan
como no probatorios, no como confirmatorios.

**El impacto.** 45 lotes, 137 direcciones, **9.697 habilitaciones = 22,6 % del padrón
georreferenciado**. Sin la corrección, ese 22,6 % entra al clustering como densidad real y
fabrica polos donde hay un trámite.

**Consecuencia editorial.** El Atlas hablaba de «habilitaciones». Después de esto, el término
correcto es **«trámites»**, con la advertencia del 22,6 % al lado. Un asiento de habilitación no
es un local.

---

# Parte III · La comparabilidad

## 6 · El problema, medido

Las 22 zonas del Atlas V2 **no se contaron todas igual**. Zonas relevadas con criterios distintos
producen números que no se pueden poner en la misma tabla, y estaban en la misma tabla.

La magnitud: la cobertura de la base sobre lo publicado va de **92,6 % a 18,2 %** según la zona.
**Un factor de 5,1×.** Cualquier ranking, cualquier «zona más densa», cualquier comparación entre
dos referencias del Atlas V2 estaba midiendo, en buena parte, con qué criterio se había relevado
cada una.

## 7 · Las cinco reglas de conteo

Para volver comparable lo que no lo era, se fijaron cinco reglas y se recontó todo con ellas:

1. **Una unidad es un local con puerta a la calle o acceso propio identificable.** Un patio de
   comidas es un local por puesto sólo si cada puesto tiene identidad comercial propia.
2. **El estado administrativo no define la unidad.** Un local sin habilitación vigente que opera
   cuenta; un trámite sin local no cuenta.
3. **La unidad es el punto, no el asiento.** (Es la regla que hace falta después del §5.)
4. **El perímetro manda sobre el nombre.** Un local se asigna a la zona cuyo polígono lo contiene,
   no a la zona que le queda cerca.
5. **Un local pertenece a una sola zona.** Donde dos zonas publicadas se superponen, se declara
   la superposición y no se cuenta dos veces.

Con estas cinco reglas se produjo la **capa homogénea**, en dos versiones —48 barrios y 22
zonas—, que quedó **congelada como referencia**. Toda corrida posterior se verifica contra ella
con `--check`: si un número de la capa cambia, la corrida se detiene y avisa. Una referencia que
se puede mover en silencio no es una referencia.

## 8 · El factor de captura

Para cada zona se calcula el **factor de captura**: cuántos locales ve la base por cada local que
el Atlas publicó. No es una medida de error del Atlas — es una medida de **cuánto se parece cada
zona a la otra cuando se las mira con el mismo instrumento**.

Un detalle que cambia el número y que conviene tener presente: el factor se calcula **contra las
dos bases** (la base de trabajo y la publicada), no contra una sola. Se conservan los dos cálculos
—`factor_captura_dos_bases.csv` y `factor_captura_una_base.csv`— justamente para que se vea la
diferencia, porque en algún momento se comparó una razón con la otra y se leyó al revés.

## 9 · Parejidad de cobertura · dos indicadores, y sus límites explícitos

La pregunta de fondo: **¿la base ve peor el sur de la Ciudad que el norte?** Si la respuesta
fuera que sí, todo el barrido estaría sesgado y el mapa reproduciría el sesgo como si fuera
territorio.

Se construyeron dos indicadores internos, con sus fórmulas escritas y —esto es lo importante—
con sus límites escritos al lado:

**Indicador A · cobertura.** `base_núcleo ÷ parcelas gastronómicas del RUS`.

> **Límite declarado:** el RUS está *adentro* de la base, así que este cociente **no puede bajar
> de 1** y lo que mide es cuánto agregan las otras seis fuentes sobre ese piso. Por eso se reporta
> también `aporte_otras_fuentes = cobertura − 1`, cuya mediana es **1,46**.

La razón cruda `base_total ÷ parcelas comerciales` **no se puede leer sola**: mezcla cobertura con
composición. Por eso se reporta partida en A.1 (cobertura), A.2 (composición) y A.3 (aporte).

> **Sobre A.2:** que Palermo tenga más gastronomía por comercio que Villa Riachuelo **no es un
> defecto de la base. Es el territorio.** Confundir composición con cobertura es cómo se fabrica
> un sesgo que no existe.

**Indicador B · locales cada mil habitantes.** `base_núcleo ÷ población en viviendas particulares
× 1000`, con población del Censo 2022 verificada contra dos archivos del INDEC.

> **Límite declarado:** **no es un diagnóstico de cobertura.** La gastronomía se ubica donde hay
> oficinas y turismo, no donde hay camas. Un microcentro con pocos habitantes y muchos bares no
> tiene «exceso de cobertura».
>
> **Unidad de referencia: la comuna, no el barrio.** El 20,5 % de la población vive en radios
> censales que tocan más de un barrio, y bajar a barrio exige repartir gente que el censo no
> reparte.

**El resultado.** Sur **2,50** contra resto **2,45**. **El sur no está peor cubierto.** Y ese
resultado se obtuvo mirando el disco, sin gastar una sola llamada a una API paga.

## 10 · La sonda de Google Places

Places se incorporó porque da una imagen actual que las fuentes documentales no dan. Pero tiene
una propiedad que hay que decir antes de usar cualquier número que salga de ahí:

> **Places no es una base que se pueda enumerar.** Es un buscador que devuelve una **lista
> ordenada servida a profundidad variable**. Pedir «todos los restaurantes de X» no devuelve
> todos: devuelve los primeros N según un ranking que no controlamos y que puede cambiar entre
> dos consultas hechas con media hora de diferencia. El tope de 60 resultados por página **no es
> lo mismo** que el corte de profundidad del ranking.

Por eso Places no se usa para medir cuántos locales hay. Se usa para **descubrir** locales que
las otras fuentes no tienen, y el número que produce es una **cota**, no un promedio.

**La sonda.** Cinco barrios, elegidos con criterio declarado *antes* de correr: los cinco peores
según los dos indicadores internos del §9.

| barrio | Places (núcleo) | ya estaba | nuevos | base | nuevos sobre base |
|---|---:|---:|---:|---:|---:|
| Paternal | 42 | 23 | 19 | 126 | 15,1 % |
| San Cristóbal | 50 | 23 | 27 | 250 | 10,8 % |
| Villa del Parque | 64 | 41 | 23 | 337 | 6,8 % |
| Villa Gral. Mitre | 43 | 16 | 27 | 208 | 13,0 % |
| Villa Luro | 47 | 22 | 25 | 207 | 12,1 % |
| **total** | **246** | **125** | **121** | **1.128** | **10,7 %** |

**Tres calificaciones que van pegadas al 10,7 % y no en una nota al pie:**

1. **Es una cota superior, no un promedio.** Los cinco barrios se eligieron *por ser los peores*.
   El barrio mediano tiene que estar por debajo.
2. **No dice nada sobre vigencia.** Places **descubre**, no confirma. Un local que aparece en
   Places puede estar cerrado.
3. **No se traslada al sur.** Los cinco son del oeste y el centro —comunas 3, 10, 11 y 15—.
   Ninguno es del sur. El techo del 11 % es el techo *de esos barrios*.

**Y una cota independiente.** Para saber cuánto del universo alcanza Places se usó
**captura-recaptura (Chapman)** entre dos corridas: el estimador da **N̂ ≈ 77** para un caso donde
la ficha publicada declara 646 registros. No es que falten 569 locales: es que **las dos corridas
de Places ven casi lo mismo**, lo cual acota fuerte lo que Places alcanza a ver y confirma que no
es una fuente para enumerar.

---

# Parte IV · El barrido

## 11 · HDBSCAN, y por qué

Se necesita un método que **no exija decir de antemano cuántos polos hay** ni suponer que todos
tienen el mismo tamaño o la misma forma. Eso descarta k-means. HDBSCAN además tiene ruido
explícito —un local puede no pertenecer a ningún polo—, que es exactamente lo que queremos: el
**47,1 %** de la gastronomía de la Ciudad no está en ninguna concentración, y un método que
obligue a asignar todo lo escondería.

Se usa `cluster_selection_method = 'leaf'`, es decir las hojas del árbol condensado en vez de las
ramas más persistentes. La razón es que las ramas tienden a producir **encadenamientos**: una
cadena de locales a través de un corredor ralo une dos concentraciones que nadie llamaría lo
mismo. `leaf` los evita, a costa de partir de más — y esa partición de más se corrige después con
las pruebas de continuidad de la Parte V.

## 12 · La grilla de sensibilidad · 15 combinaciones

El resultado depende de dos parámetros elegidos a mano. Publicar el resultado sin la grilla sería
publicar la mitad del método:

| `min_cluster_size` | `min_samples` | polos | ruido | mayor | mayor % | colapsa |
|---:|---:|---:|---:|---:|---:|:--|
| 20 | 5 | 323 | 32,7 % | 400 | 1,7 % | no |
| 20 | 10 | 244 | 45,6 % | 507 | 2,1 % | no |
| 20 | 20 | 146 | 52,8 % | 588 | 2,5 % | no |
| 30 | 5 | 212 | 35,5 % | 400 | 1,7 % | no |
| 30 | 10 | 154 | 41,3 % | 1.314 | 5,5 % | no |
| 30 | 20 | 99 | 53,3 % | 701 | 2,9 % | no |
| 40 | 5 | 148 | 34,6 % | 892 | 3,7 % | no |
| **40** | **10** | **118** | **43,4 %** | **1.314** | **5,5 %** | **no · adoptado** |
| 40 | 20 | 80 | 53,3 % | 964 | 4,0 % | no |
| 60 | 5 | 89 | 36,4 % | 1.253 | 5,2 % | no |
| 60 | 10 | 65 | 46,9 % | 1.548 | 6,5 % | no |
| 60 | 20 | **5** | 3,8 % | **22.698** | **94,6 %** | **SÍ** |
| 80 | 5 | 66 | 36,7 % | 1.253 | 5,2 % | no |
| 80 | 10 | 51 | 45,3 % | 1.548 | 6,5 % | no |
| 80 | 20 | **4** | 4,1 % | **22.698** | **94,6 %** | **SÍ** |

**Cómo se lee.** El número de polos varía mucho (de 4 a 323), pero **la estructura no colapsa en
trece de las quince combinaciones**. El colapso aparece sólo con `min_samples = 20` combinado con
`min_cluster_size ≥ 60`: ahí el 94,6 % de los locales cae en un solo cuerpo, que es la señal
inequívoca de que el parámetro se comió el resultado.

**Criterio de adopción, declarado antes:** la combinación más chica que no colapsa, que mantiene
el mayor cluster por debajo del 6 % del total, y cuyo ruido queda cerca de la mediana de la
grilla. Da `40 / 10`.

**Y qué NO es este número.** «118 polos» no es un hallazgo sobre la Ciudad: es el resultado de
`40 / 10`. Lo que sí es un hallazgo es que **la estructura sobrevive en trece de quince
combinaciones**.

## 13 · La ablación, con control aleatorio

La pregunta: ¿de qué fuentes depende el mapa? La trampa: sacar una fuente saca puntos, y sacar
puntos ya cambia el resultado. Sin un control, no se sabe si el efecto es **de lo que se sacó** o
**de cuánto se sacó**.

Por eso toda ablación va con **control aleatorio**: se quita la misma cantidad de puntos al azar,
cinco veces, con semilla fija.

| grupo quitado | puntos perdidos | polos tras quitarlo | **polos al azar (mediana)** | **colapsos al azar** | mayor % | ¿colapsa? |
|---|---:|---:|---:|:--:|---:|:--|
| GCBA_ESPACIO_PUBLICO | 0,0 % | 118 | 118 | 0/5 | 5,5 % | no |
| GCBA_AGC | 21,5 % | 82 | 68 | 2/5 | 3,3 % | no |
| OVERTURE_FSQ_ATP | 36,6 % | 64 | 65 | 0/5 | 6,9 % | no |
| **OSM** | 23,5 % | **5** | 77 | 1/5 | **94,3 %** | **SÍ** |
| **GCBA_URBANISMO** | 37,5 % | **5** | 67 | **0/5** | **94,4 %** | **SÍ** |

**Sin el control, tres de las cinco filas se leían al revés.** El caso de `OVERTURE_FSQ_ATP` es
el más claro: quitarlo baja de 118 a 64 polos, lo que parece un efecto enorme — pero quitar la
misma cantidad de puntos al azar deja 65. **El efecto es del volumen, no de la fuente.**

**La fila que importa es la última.** Quitar el Relevamiento de Usos del Suelo colapsa el mapa, y
quitar la misma cantidad al azar **no lo colapsa ninguna de las cinco veces**. Ese es un efecto
real y atribuible: el RUS es el piso de cobertura pareja sobre el que se apoya todo lo demás.

**Un matiz honesto sobre OSM.** OSM también colapsa, pero su control aleatorio colapsó **1 de 5
veces**. La atribución es más débil que la del RUS y se reporta así, no como equivalente.

## 14 · Los umbrales · el mínimo de 40 y el piso de densidad

**El mínimo de 40 locales.** Anclado **afuera de los datos que va a juzgar**: 40 es el tamaño de
la zona publicada más chica del Atlas. Si hubiera salido de mirar el histograma de los clusters,
el mapa habría confirmado lo que ya creíamos.

Es la regla que más presión recibe, porque siempre aparece un caso que queda a pocos locales.
**No se mueve.** Un mínimo que se baja una vez deja de ser un mínimo para los otros 123 polos.

**El piso de densidad.** Se evaluó imponer un piso absoluto de locales por hectárea, y se
descartó. La curva dice por qué:

| piso (loc/ha) | polos que sobreviven | locales que caen | barrios que pierden todo | **zonas publicadas que caerían** |
|---:|---:|---:|---:|---:|
| 2,0 | 106 | 10,5 % | 3 | **11 de 22** |
| 4,0 | 74 | 46,0 % | 18 | **16 de 22** |
| 6,0 | 44 | 68,4 % | 28 | **20 de 22** |

Cualquier piso razonable **elimina la mitad del Atlas publicado**. Eso no significa que el Atlas
esté mal: significa que **la densidad no es el criterio con el que el Atlas fue construido**, y
que imponerlo ahora sería juzgar el trabajo anterior con una regla que no se le aplicó.

---

# Parte V · La forma

## 15 · Cuándo dos concentraciones cercanas son una · los tres precedentes

Esta pregunta ya se había resuelto tres veces en el proyecto, con criterios explícitos y números
guardados. No hizo falta inventar una regla: hizo falta **leer la que se usó**.

**Recoleta · nueve núcleos, una zona.** El modelo elegido dice: «Los nueve núcleos forman una red
continua; unidad general más parsimoniosa». Y el dato que lo vuelve obvio: **tres pares están a
0,0 metros** —se tocan—, otros tres a 3, 6 y 10 m, la mediana de los catorce pares ronda los 25 m
y el máximo es 208. No eran nueve polos separados por algo: eran nueve pedazos de un tejido
continuo que el algoritmo había subdividido.

**Belgrano · tres partes, y el motivo del rechazo es lo importante.**

| umbral | componentes | tamaños |
|---:|---:|---|
| 80 m | 6 | 5; 5; 2; 2; 2; 1 |
| 120 m | 6 | 5; 5; 2; 2; 2; 1 |
| **160 m** | **3** | **8; 7; 2** |
| 200 m | 2 | 8; 9 |
| 250 m | 1 | 17 |

Se eligió 160 m y tres partes. El motivo textual del rechazo de la alternativa es la frase que
gobierna todo este asunto: **«A 120 m aparecen seis fragmentos; elegir cuatro sería arbitrario».**
No se rechazó por distancia: se rechazó porque **la cantidad de partes no era estable**. Y la
pieza de tamaño 2 —Belgrano R— sobrevive **por respaldo documental propio**, no por su tamaño.

**Costanera Norte · cuatro, y los vacíos se preservan a propósito.** Separaciones de 163, 462,
692, 1.418, 1.995 y 2.727 m. Unir habría sido inventar una línea que no existe.

## 16 · Las tres pruebas, en orden

**Prueba 1 · continuidad de la red.** Si los núcleos forman una red continua —vacíos cercanos a
cero— es **una** zona. Referencia empírica: **por debajo de ~50 m, unir** (precedente Recoleta).

**Prueba 2 · estabilidad de la partición.** Barrer el umbral y contar componentes. **Si el número
de partes cambia con un cambio chico del umbral, la partición es arbitraria y se sube un nivel.**
Es la prueba más importante de las tres, porque es la que evita publicar una división que sólo
existe por el parámetro que elegimos.

**Prueba 3 · ¿la división mejora la lectura?** Se responde con dos cosas concretas: **¿cada parte
tiene nombre de uso corriente?** y **¿tiene respaldo documental propio?** Un fragmento sin nombre
y sin respaldo no es una parte: es ruido.

**Una precisión técnica que apareció midiendo y no estaba prevista.** Hay **dos** distancias
posibles entre dos piezas y no son intercambiables:

| par (P078) | entre envolventes | entre puntos |
|---|---:|---:|
| S1–S2 | **8,2 m** | **60,5 m** |
| S1–S3 | 52,9 m | 70,6 m |
| S2–S3 | 195,8 m | 195,8 m |

La distancia entre envolventes puede medir **una arista tendida sobre un vacío**: el polígono
convexo de una pieza puede acercarse a la otra por una zona donde no hay ningún local. La
distancia **entre puntos** es la que mide continuidad de tejido. Se reportan las dos, y la que
decide es la segunda.

## 17 · Por qué la grilla de continuidad baja de 40 m a 20 m

La grilla original barría de 40 a 300 m. Se extendió hacia abajo, y la justificación es
geométrica, no de conveniencia.

**La ley.** Para un proceso de puntos de intensidad λ, la distancia media al vecino más cercano
es `1/(2·√λ)`. Duplicar la densidad no acerca los puntos a la mitad: los acerca en un factor √2.
A 2 loc/ha —la densidad para la que se diseñó la grilla vieja— el vecino típico está a 35,4 m, y
un piso de 40 m arranca justo donde la estructura empieza a aparecer.

**El problema.** En los polos densos ese piso ya no arranca en el lugar correcto:

| polo | loc/ha | vecino predicho | vecino observado | obs/pred | **piso viejo ÷ vecino** | piso nuevo ÷ vecino |
|---|---:|---:|---:|---:|---:|---:|
| P091 Palermo | 7,88 | 17,8 m | 14,5 m | 0,82 | **2,8** | 1,4 |
| P103 San Telmo | 7,21 | 18,6 m | 15,2 m | 0,82 | **2,6** | 1,3 |
| P065 Palermo | 4,40 | 23,8 m | 16,5 m | 0,69 | **2,4** | 1,2 |
| P078 Palermo | 5,70 | 20,9 m | 17,6 m | 0,84 | **2,3** | 1,1 |

`piso viejo ÷ vecino` es la lectura operativa: **cuando pasa de 2, el umbral más bajo de la grilla
ya conecta todo** y el barrido devuelve «un solo cuerpo» — que es un resultado de la grilla, no
del territorio. Un piso fijo de 40 m es **un umbral distinto según la densidad del polo**.

**El ajuste de la ley.** Observado/predicho entre 0,69 y 0,84: los puntos reales están *siempre*
más juntos que la predicción de Poisson, y tiene que ser así, porque la gastronomía se agrupa y
Poisson supone independencia. La ley se usa para la escala y el orden de magnitud, no para
predecir un valor.

**Un resultado que no se estaba buscando.** El orden de los polos por densidad nominal
(P065 < P078 < P103 < P091) **no coincide** con el orden por vecino observado
(P078 > P065 > P103 > P091). El caso que los separa es **P065**: tiene la densidad nominal más
baja de los cuatro y sus puntos están más juntos que los de P078, que es 30 % más denso en el
papel.

Eso es exactamente lo que se espera de un polo **encadenado**: la densidad se mide sobre una
envolvente que incluye los vacíos de la unión, así que subestima cuán juntos están los puntos
adentro de cada pedazo. **La densidad nominal describe la cáscara; el vecino observado describe el
tejido.** Es un control independiente del encadenamiento de P065, y coincide con lo que la curva
de continuidad ya había dicho por otro camino.

## 18 · Uniones · los 39 pares a menos de 100 m

Se midió la distancia mínima entre envolventes para todos los pares del borrador y se evaluaron
los 39 que quedaron por debajo de 100 m. **Unieron dos.**

| par | distancia | continuidad | estabilidad | decisión |
|---|---:|---|---|---|
| P090+P089 | 15,1 m | 1 cuerpo | **no se vuelve a partir** | **UNE** |
| P101+P099 | 85,1 m | 1 cuerpo | **no se vuelve a partir** | **UNE** |
| P081+P080 | 9,1 m | 1 cuerpo | `leaf` la parte en 2 | no une |
| P091+P088 | 16,2 m | 2 cuerpos | `leaf` la parte en 5 | no une |
| … (35 más) | | | | no une |

**Cómo se lee.** Estar pegados no alcanza. P081+P080 están a **9,1 m** —más cerca que el par que
sí unió— y no unen, porque al volver a correr el clustering sobre el conjunto unido, `leaf` lo
vuelve a partir en dos. La prueba de estabilidad manda sobre la distancia.

**Y la no-transitividad, que hay que declarar.** La columna `evaluado_como` muestra que algunos
pares se evaluaron dentro de un trío: P091+P090 se evaluó como `P091+P090+P089`, y P087+P089 como
`P087+P090+P089`. Que A una con B y B una con C **no implica** que A una con C. Por eso el
resultado depende del orden en que se evalúan los pares, y ese orden está fijado y registrado.

## 19 · Particiones · los diez encadenados

Diez polos eran candidatos a partirse por encadenamiento. **Se partieron cuatro**, y el mapa pasó
de **118 a 124 polos**.

| polo | barrio | locales | ha | loc/ha | contiene | piezas | **sueltos** | ¿se parte? |
|---|---|---:|---:|---:|---|---:|---:|:--|
| P072 | Belgrano | 1.314 | 440,7 | 2,98 | R05 entera | 7 | 694 (52,8 %) | **sí** |
| P065 | Palermo | 361 | 82,0 | 4,40 | — | 2 | 188 (52,1 %) | **sí** |
| P018 | Villa Devoto | 244 | 205,1 | 1,19 | — | 2 | 109 (44,7 %) | **sí** |
| P025 | Monte Castro | 162 | 89,5 | 1,81 | — | 2 | 73 (45,1 %) | **sí** |
| P046 | Villa Urquiza | 291 | 114,7 | 2,54 | — | 0 | 0 | no |
| P021 | Liniers | 262 | 77,9 | 3,36 | — | 0 | 0 | no |
| P027 | Parque Patricios | 189 | 100,8 | 1,87 | — | 0 | 0 | no |
| P043 | Villa Gral. Mitre | 161 | 91,6 | 1,76 | — | 0 | 0 | no |
| P004 | Villa Lugano | 141 | 144,0 | 0,98 | — | 0 | 0 | no |
| P005 | Villa Lugano | 100 | 100,9 | 0,99 | — | 0 | 0 | no |

**El costo de partir, declarado.** Partir deja locales afuera de las piezas: **1.064 locales
sueltos** en total. No se los esconde. Se mide dónde caen:

| padre | sueltos | **entre las piezas** | dist. mediana a pieza | dist. p90 | mayor grupo |
|---|---:|---:|---:|---:|---:|
| P072 Belgrano | 694 | **63,5 %** | 139,9 m | 326,0 m | 239 |
| P065 Palermo | 188 | 15,4 % | 186,9 m | 399,2 m | 70 |
| P025 Monte Castro | 73 | 12,3 % | 274,6 m | 633,2 m | 0 |
| P018 Villa Devoto | 109 | **0,9 %** | 569,5 m | 1.034,3 m | 0 |

**Las dos filas extremas dicen cosas opuestas y las dos son informativas.** En P072, el 63,5 % de
los sueltos está *entre* las piezas: es tejido de conexión, y la partición está cortando algo que
tiene continuidad — se sostiene igual porque «Belgrano–Núñez–Colegiales» no es un nombre que
alguien use. En P018, el 0,9 % está entre las piezas y la mediana de distancia es 569 m: ahí los
sueltos son **dispersión real**, no tejido cortado. La partición de P018 es limpia; la de P072 es
una decisión.

**Los bloques de sueltos que llegarían a 40.** Seis:

| padre | bloque | locales | loc/ha | ¿centro dentro de la cáscara? | % entre las piezas |
|---|---|---:|---:|:--:|---:|
| P072 | S3 | 239 | 3,92 | sí | 34,3 % |
| P072 | S4 | 80 | 5,36 | sí | 100 % |
| P072 | S2 | 79 | 5,80 | sí | 68,4 % |
| P065 | S1 | 70 | 5,96 | **no** | 0 % |
| P072 | S1 | 68 | 4,14 | sí | 92,6 % |
| P065 | S2 | 59 | 5,39 | **no** | 30,5 % |

Los cuatro de P072 tienen el centro **dentro** de la cáscara del padre: son tejido interno. Los
dos de P065 están **afuera**: son otra cosa, y son la evidencia más directa de que P065 estaba
encadenado.

---

# Parte VI · Los atributos

## 20 · Clases de densidad · Fisher–Jenks, y el control que falló

Se clasifican los polos en clases de densidad con Fisher–Jenks (cortes naturales). La bondad de
ajuste por número de clases:

| k | GVF | cortes (loc/ha) |
|---:|---:|---|
| 2 | 0,6992 | 6,39 |
| **3** | **0,8506** | **4,58 · 8,48** |
| 4 | 0,9124 | 3,54 · 6,14 · 9,34 |
| 5 | 0,9395 | 2,86 · 4,79 · 7,28 · 10,38 |
| 6 | 0,9633 | 2,78 · 4,58 · 6,39 · 8,48 · 10,85 |

Se adoptó **k = 3**. El GVF crece siempre con k, así que **no puede usarse para elegir k**: se
eligió 3 como convención declarada —tres clases se leen en un mapa, seis no—, no como óptimo
descubierto. Las clases son A (concentración densa), B (media) y C (extendida).

**Y acá el control falló.** Se declaró antes de correr que las clases serían robustas si el índice
de Rand ajustado entre la clasificación con y sin el RUS superaba **0,60**. Dio **0,391**.

Lo que se hizo con eso es el precedente más importante de todo el documento:

> **No se cambió el umbral.** Se diagnosticó por qué falló, se midió el diagnóstico, y se
> reportaron las dos lecturas.

Las dos explicaciones intuitivas se midieron y **las dos resultaron falsas**:

| explicación candidata | prueba | resultado |
|---|---|---|
| «la añada contamina la densidad» | η² = 0,0368 con RUS, 0,0320 sin | **falsa** — el efecto es mínimo en ambas |
| «el ranking cambia» | Spearman con/sin RUS = **0,975** | **falsa** — el orden es casi idéntico |

La explicación real apareció **sólo porque no se movió el umbral**: el orden de los polos casi no
cambia (Spearman 0,975), pero **los cortes sí**, porque Fisher–Jenks minimiza varianza dentro de
clase y **está dominado por la cola de la distribución**. Sin el RUS, k libre da 4 clases con
cortes en 3,70 y 10,82 en vez de 4,58 y 8,48. Unos pocos polos muy densos mueven los cortes, y
los polos que están cerca de un corte cambian de clase aunque su densidad casi no se mueva.

**Consecuencia adoptada:** las clases **se publican como lectura, no como propiedad**. Cada polo
lleva su distancia al corte más cercano, para que se vea cuáles están al filo.

> Un control que falla y se reemplaza por otro más benévolo no es un control: es un trámite.

## 21 · La añada

`añada` es el año de la última señal de actividad de cada local. Se verificó que **no contamina**
la densidad (η² ≈ 0,037; Kruskal–Wallis p = 0,012 indica que hay diferencia entre clases, pero
η² dice que explica menos del 4 % de la varianza). Se reporta como atributo, no como filtro: un
local con última señal de 2023 **no** se declara cerrado. Se declara que su última señal es de
2023.

---

# Parte VII · El cotejo contra lo publicado

## 22 · Las 22 zonas, medidas con la misma base

Se encontraron **14 de las 22**. Ese número, solo, se lee mal. Lo que importa es la explicación de
las otras ocho, y para eso se usó una taxonomía declarada **antes** de mirar los resultados:

- **E1 · no era una concentración: el perímetro es más ancho.** La mayoría de sus locales *sí*
  está en algún polo, pero esos polos ocupan una fracción chica del área publicada.
- **E2 · la cobertura de la base ahí es floja.** Por debajo del percentil 10 de la Ciudad. **No se
  concluye nada sobre la zona.**
- **E3 · queda como pregunta, no como conclusión.** No aplica E1 ni E2, y una hipótesis sobre una
  zona publicada **no se declara desde un borrador**.

| zona | ha | locales | % de la zona cubierta | % de sus locales en algún polo | explicación |
|---|---:|---:|---:|---:|---|
| R04 Puerto Madero | 314,5 | 354 | 9,3 % | 33,6 % | **E3 · pregunta** |
| R07 Costanera Norte | 38,5 | 67 | 16,1 % | 53,7 % | **E1 · perímetro más ancho** |
| R11 Boulevard Caseros | 50,0 | 60 | 5,5 % | 31,7 % | **E3 · pregunta** |
| R15 Devoto | 478,7 | 422 | 10,7 % | 75,6 % | **E1** (tras partir) |
| R16 Donado-Holmberg | 119,0 | 121 | 14,9 % | 52,9 % | **E1 · perímetro más ancho** |
| R20 García del Río | 28,4 | 61 | 1,0 % | 29,5 % | **E3 · pregunta** |
| R21 La Paternal | 321,0 | 208 | 13,2 % | 45,7 % | **E2 · cobertura floja (2,30 = p10)** |
| R22 Villa Pueyrredón | 305,6 | 198 | 9,3 % | 58,1 % | **E1 · perímetro más ancho** |

**La lectura correcta de las E1.** En R07 Costanera Norte, el 54 % de sus locales *está* adentro
de algún polo — pero esos polos ocupan sólo el 16,1 % de sus 39 ha publicadas. **La concentración
está; lo que es más ancho es el perímetro.** Y como R07 está clasificada en la familia «polo con
subzonas / multiparte», que no produzca un cluster del tamaño de la zona **la confirma, no la
refuta**.

**La lectura correcta de la E2.** R21 La Paternal tiene cobertura 2,30, que es exactamente el
percentil 10 de la Ciudad. Sobre R21 **no se dice nada**. Ni que está, ni que no está.

## 23 · Un hallazgo colateral sobre R01

Midiendo P078 apareció un dato sobre la zona publicada: **279 de los 585 locales de P078 (47,7 %)
caen fuera del perímetro de R01**. Y al revés, R01 contiene 1.358 locales de la base, de los
cuales sólo 306 son de P078.

Eso es información sobre **el perímetro de R01**, y va a la conversación de la V3 con su número.
No se usó —y no se debe usar— como justificación de ninguna decisión sobre P078.

---

# Parte VIII · Las decisiones de esta tanda

## 24 · La matriz, con la excepción que cayó

Seis decisiones, con la prueba que se les corrió y el número que dio:

| id | qué se decidía | prueba | resultado | decisión |
|---|---|---|---|---|
| **P078-EXC** | aceptar las 3 partes como excepción | motivo documental: los sueltos serían los «tramos sin oferta» de R01 | **REFUTADO** | **no se firma; queda registrada como refutada** |
| **P078-PART** | si la partición en 3 es estable | prueba 2 | **ARBITRARIA** | P078 va entero |
| **P078-NOM** | si cada parte tiene nombre propio | prueba 3 | **NO** | sin nombres propios |
| **P078-SAL** | si el saliente pertenece a otro polo | prueba 1 | **DE NADIE** | hallazgo acotado; el mínimo no se mueve |
| **P103-FOCO** | si el foco de 44 va como subzona | condición 3 | **FALLA** | mención de una línea |
| **R01-DESB** | (colateral sobre la zona publicada) | punto en polígono | **ANOTADO** | va a la V3 |

## 25 · P078 en detalle · el caso completo

Vale la pena seguirlo entero porque es donde el método se probó a sí mismo.

**El primer motivo, y su refutación.** Se propuso aceptar las tres partes con este argumento: los
123 locales que quedan afuera de las partes son los «tramos sin oferta» que R01 documenta. **La
lectura estaba escrita antes de correr.** El número cayó del otro lado:

| | las partes | los 123 sueltos |
|---|---:|---:|
| entre dos partes | 69 % | **9 · 7,3 %** |
| colgando de una sola parte | 48 % | **114 · 92,7 %** |
| adentro de R01 | 51 % | **12 · 10 %** |
| fuera de toda zona publicada | — | **108 · 88 %** |

Y el argumento se contradecía solo: **si un tramo no tiene oferta, no tiene locales que expliquen
el faltante.** Medido por el otro extremo, el hueco entre S1 y S2 mide ~300 m y tiene 6 locales.
No es un tramo sin oferta.

**La excepción no se firmó, y el motivo no se cambió.** Existía una lectura alternativa que los
datos sí sostenían —«P078 desborda R01»— y era tentador usarla para sostener la misma conclusión.
No se hizo, porque cambiar el motivo para conservar la conclusión es exactamente lo que la regla
de umbrales prohíbe. La excepción quedó **registrada como refutada, no borrada**.

**La prueba 2, corrida después y como corresponde.** Curva de estabilidad cada 5 m, formato
Belgrano:

| umbral | componentes | **partes** | tamaños de las partes | % de locales |
|---:|---:|---:|---|---:|
| 30 m | 166 | 1 | 82 | 14,0 % |
| 35 m | 126 | 1 | 107 | 18,3 % |
| **40 m** | 80 | **3** | 183; 46; 41 | 46,2 % |
| 50 m | 40 | **3** | 325; 46; 40 | 70,3 % |
| **60 m** | 21 | **3** | 379; 92; 43 | 87,9 % |
| 65 m | 14 | 2 | 491; 47 | 92,0 % |
| 75 m | 7 | 1 | 555 | 94,9 % |
| 90 m + | 1 | 1 | 585 | 100 % |

**Las tres partes existen sólo entre 40 y 60 m: una ventana de 20 m**, contra los 60 exigidos. Y
en la ventana de ±40 m alrededor del umbral elegido, el conteo de partes toma los valores 0, 1, 2
y 3. **Veredicto: partición arbitraria.** P078 va entero, por la misma lógica con la que se
rechazó la alternativa de Belgrano.

**La prueba 3, que lo confirma por otro camino:**

| parte | locales | calles dominantes | zona publicada |
|---|---:|---|---|
| S1 | 333 | Bonpland · Fitz Roy · Costa Rica · Honduras · Humboldt · Gorriti | Palermo (R01) 67 % |
| S2 | 88 | Dorrego · Arévalo · Gorriti · Niceto Vega · J. A. Cabrera · Álvarez Thomas | R01 46 %, R09 17 % |
| S3 | 41 | Niceto Vega · Humboldt · Fitz Roy · Bonpland · Córdoba | R01 66 %, R08 22 % |

**S1 y S3 comparten Humboldt, Fitz Roy y Bonpland.** Es el mismo lugar partido por la Av. Niceto
Vega. Y **no aparece ninguna calle de Soho**: la hipótesis de que P078 fuera «Soho + Hollywood +
Cañitas» era falsa. P078 es **Palermo Hollywood y su borde norte**.

## 26 · El saliente N–NE, y el registro de candidatos bajo el mínimo

Quedaba una concentración de 108 locales con dirección firme al N–NE (R = 0,70, rumbo 36°), en
tres bloques de 35, 23 y 12. El más grande queda **5 locales por debajo del mínimo de 40**.

**La pregunta legítima no era «bajamos el mínimo», era «¿de quién es esta cola?».** Si el bloque
tocara otro polo por debajo de 50 m, entraría al mapa por **contigüidad** —precedente Recoleta—
sin mover ningún umbral. Unir no es bajar. Se midió contra **todos** los polos del borrador:

| bloque | polo externo más cercano | entre envolventes | entre puntos |
|---|---|---:|---:|
| bloque_35 | P090+P089 (Palermo, 104 loc) | 315,7 m | 316,0 m |
| bloque_23 | P065 (Palermo, 361 loc) | 175,1 m | 175,1 m |
| bloque_12 | P065 | 287,8 m | 296,5 m |

**Ninguno por debajo de 50 m.** El precedente Recoleta no aplica. El saliente **no es de nadie**,
y se reporta con la redacción del §0: *concentración lineal de 108 locales, 88 % afuera de toda
zona publicada, que no alcanza el mínimo declarado de 40 por 5 locales*. **No** «no se identificó
actividad».

**El registro de candidatos bajo el mínimo.** Para que esa frase sea honesta hace falta que el
lector pueda ver qué había. Se produjo `candidatos_bajo_minimo.csv`: todos los conglomerados de
25 a 39 locales, con barrio, comuna, polo más cercano y zona publicada encima. Catorce afuera de
todo polo, más tres internos.

Los primeros:

| id | locales | loc/ha | barrios | comuna | polo más cercano | ¿en zona publicada? |
|---|---:|---:|---|---|---|---|
| C001 | 38 | 32,06 | Recoleta | 2 | P106 (76 m) | Recoleta (R06): 37 |
| C002 | 36 | 9,52 | San Cristóbal (27); Constitución (9) | 1; 3 | P085 (172 m) | **no** |
| B002 | 35 | 17,97 | Palermo | 14 | P078 (0 m) | **no** |
| C003 | 34 | 11,83 | San Nicolás | 1 | P117 (31 m) | R12: 27 |
| C004 | 32 | 15,98 | Recoleta | 2 | P110 (45 m) | Recoleta (R06): 32 |

**Y la sensibilidad va pegada, no aparte**, porque el registro es lo que se ve a 55 m, no una
propiedad del territorio:

| umbral | conglomerados en la banda | locales | el más grande |
|---:|---:|---:|---:|
| 40 m | **1** | 25 | 25 |
| **55 m** | **14** | **405** | 38 |
| 70 m | **18** | 550 | 39 |

De 1 a 18 candidatos según dónde se ponga el umbral. Publicar los 14 sin esta tabla sería publicar
una propiedad del parámetro como si fuera una propiedad de la Ciudad.

---

# Parte IX · Las reglas de método

Estas ocho reglas no salieron de un manual. Salieron de errores concretos de este proyecto, y
cada una tiene el caso que la originó en el cuerpo de este documento. Si una corrida no las
cumple, su resultado no se reporta como conclusión.

| # | regla | dónde se ve en este documento |
|---:|---|---|
| **R1** | La lectura se escribe **antes** de correr | §25 · la excepción de P078 |
| **R2** | Toda ablación lleva **control aleatorio** | §13 · tres de cinco filas se leían al revés |
| **R3** | Un umbral **no se mueve** para rescatar un caso | §14 y §26 · el mínimo de 40 |
| **R4** | Si el resultado depende de un parámetro, se publica **la curva** | §12, §17, §25, §26 |
| **R5** | Antes de gastar en una API, **el número estimado** | §10 · el dry-run de la sonda |
| **R6** | Cada dato lleva **procedencia y licencia**, y las fuentes se cuentan **por grupo** | §3 |
| **R7** | **«No encontramos» no es «no existe»** | §0, §22, §26 |
| **R8** | Un campo que vuelve vacío **sin fallar** es un error, no un dato | ver abajo |

**Sobre R8.** Una máscara de campos mal escrita devolvía `None` en cada fila sin producir ningún
error, y costó 37 requests antes de que alguien lo notara. Es la misma familia que dos bugs del
normalizador de direcciones: `esq` matcheando adentro de «Esquiú», y «INDEPENDENCIA AV.» contado
como una calle distinta de «Avenida Independencia». **Los tres fallaron en silencio.** El test de
regresión que los cubre incluye **casos negativos** —«Ciudad de la Paz» es una calle de Belgrano y
cortar por «Ciudad» la decapitaría; «Avellaneda» empieza con «Av» y no es una avenida abreviada—
porque un test de regresión sin casos negativos sólo demuestra que la corrección corrige.

**Y qué hacer cuando un control falla.** No se elige otro control. Se diagnostica por qué falló,
se mide el diagnóstico, y se reportan las dos lecturas. El caso está en el §20.

**Las seis preguntas antes de reportar cualquier resultado:**

1. ¿Estaba escrita la lectura antes de correr?
2. Si hubo ablación, ¿tuvo control aleatorio?
3. ¿Algún umbral se movió después de ver el resultado?
4. Si el resultado depende de un parámetro, ¿está la curva?
5. Si se gastó presupuesto, ¿se reportó gastado contra estimado?
6. ¿Hay alguna frase que diga «no existe» donde corresponde «no encontramos»?

Si alguna respuesta incomoda, el resultado todavía no es una conclusión.

---

# Parte X · Los límites

Lo que este método **no** puede decir, dicho antes de que alguien lo pregunte:

**No dice cuántos locales gastronómicos hay en la Ciudad.** Dice cuántos ven siete fuentes unidas
y deduplicadas. La diferencia se acotó (§9, §10), no se resolvió.

**No dice si un local está abierto.** Ninguna fuente confirma vigencia. `añada` es la última señal
de actividad, y una señal vieja no es un cierre.

**No alcanza a lo que no tiene registro.** Un carrito de choripán en la Costanera puede ser
patrimonio gastronómico de esa zona y no estar en ninguna base, no tener habilitación y no tener
perfil en Places. Queda afuera, inevitablemente, y eso es un límite del instrumento — no una
afirmación sobre su existencia.

**El Atlas ve fachadas.** Este instrumento mide **fachadas contiguas**, y hay economías migrantes
que no toman esa forma. El relevamiento de enclaves comunitarios de agosto de 2026 dejó tres
resultados negativos que no son ausencias sino cegueras del método, y por eso la vía D tiene un
valor propio para ellos, `no_medible_con_este_instrumento`:

- La presencia **senegalesa** en Once y Constitución es de **venta ambulante**. No produce
  establecimiento habilitado, así que no produce fachada, así que este instrumento no la ve. La
  gastronomía africana con puerta que sí existe está en Villa Crespo, fuera de esos barrios: son
  dos fenómenos distintos y el Atlas no debe fusionarlos.
- La colectividad **japonesa** se instaló por **dispersión de rubro** —tintorerías,
  floricultura— y nunca por concentración de cuadra.
- La presencia **china fuera del Barrio Chino** está dispersa **por diseño**: el formato dominante
  es el supermercado de barrio, cuyo modelo de negocio exige una boca por zona sin competencia
  interna. La forma del negocio produce dispersión.

En los tres casos el Atlas va a decir «no hay enclave». Lo correcto es decir que **este
instrumento mide fachadas contiguas y estas economías no toman esa forma**. Si no queda escrito,
con el tiempo un «no medido» se lee como «no existe», que es la afirmación que no tenemos.

Y la contracara, que es la misma distinción: `medida_sin_enclave` **no es** `no_medida`. El Barrio
Charrúa —Barrio General San Martín, ocupado en 1957— está medido y el resultado es negativo: tres
fuentes independientes, incluida una nota extensa de prensa boliviana dedicada íntegramente al
barrio, y ninguna nombra un solo local de comida. Tiene la Fiesta de la Virgen de Copacabana desde
1972 y no tiene comercio permanente. **Eso es un hallazgo.** El Abasto, hasta agosto de 2026,
figuraba `cerrada` cuando lo que pasaba era que no lo habíamos medido: **eso era una laguna.**
Registrar las dos con la misma etiqueta borra la diferencia entre saber y no saber.

**No dice cuál es «el» mapa de polos.** «Polo gastronómico» es una categoría de lectura
territorial, no una entidad natural (§1). Lo que este trabajo produce no es la verdad: es **una
decisión reproducible, con precedente y con sus sensibilidades publicadas**. Que es lo defendible.

**El número de polos depende de los parámetros.** 118 es el resultado de `40 / 10`; 124 después de
partir los encadenados. Lo que sobrevive a la grilla no es el número: es la estructura.

**Y las clases de densidad son una lectura, no una propiedad** (§20). El Rand ajustado de 0,391
está publicado justamente para que nadie las use como si fueran duras.

---

# Anexo · qué archivo produce qué número

| tema | archivo | script |
|---|---|---|
| grilla de parámetros HDBSCAN | `sensibilidad_grilla_hdbscan.csv` | `borrador_polos_ciudad.py` |
| ablación con control aleatorio | `ablacion_por_grupo.csv` | `borrador_polos_ciudad.py` |
| piso de densidad | `sensibilidad_piso_absoluto.csv` | `polos_atributos_clases.py` |
| clases Fisher–Jenks y GVF | `clases_jenks_gvf.csv` | `polos_atributos_clases.py` |
| control de la añada (Rand 0,391) | `anada_contra_densidad_resumen.json` | `polos_particion_anada_estructura.py` |
| precedente Recoleta | `recoleta_vacios_continuidad.csv` | `ejecutar_corrida_territorial_v3.py` |
| precedente Belgrano | `belgrano_continuidad_precedente.csv` | `ejecutar_corrida_territorial_v3.py` |
| justificación de la grilla 20–300 m | `justificacion_grilla_20_300m.txt` | `justificar_grilla_continuidad.py` |
| uniones evaluadas | `union_100m_candidatas.csv` | `polos_p065_union_y_clases.py` |
| particiones de encadenados | `particion_encadenados.csv` | `polos_atributos_clases.py` |
| dónde caen los sueltos | `particion_sueltos_por_padre.csv` | `polos_particion_anada_estructura.py` |
| P078 · refutación del motivo | `p078_sueltos_ubicacion.csv` | `polos_p078_donde_caen_los_123.py` |
| P078 · curva de estabilidad | `p078_curva_estabilidad.csv` | `polos_p078_prueba_estabilidad.py` |
| P078 · prueba 3 | `p078_prueba3_nombres.csv` | `polos_p078_prueba_estabilidad.py` |
| saliente N–NE | `saliente_p078_distancias.csv` | `polos_saliente_p078_de_quien_es.py` |
| candidatos bajo el mínimo | `candidatos_bajo_minimo.csv` + `_sensibilidad.csv` | `polos_candidatos_bajo_minimo.py` |
| asientos replicados | `prueba_catastral_smp.csv`, `_mecanismo.json`, `_discriminancia.csv` | `probar_smp_lotes.py` |
| factores de captura | `factor_captura_dos_bases.csv` | `estimar_costo_places.py` |
| parejidad de cobertura | `parejidad_a_por_barrio.csv`, `parejidad_b_por_comuna.csv`, `formulas_parejidad.csv` | `parejidad_cobertura.py` |
| sonda de Places | `places_sonda_resultado_nucleo.csv`, `places_dry_run.json` | `places_sonda_barrios_flacos.py` |
| cotejo contra las 22 | `cotejo_22_zonas_final.csv`, `zonas_no_encontradas_explicacion.csv` | `polos_p065_union_y_clases.py` |
| matriz de decisiones | `matriz_decision_borrador.csv` | registro a mano |
| tests del normalizador | `test_normalizador_direcciones.py` | `tests/` |

Todos en `outputs/BARRIDO_CIUDAD_2026-08/material_metodo/`, con `INDICE.csv` que da la ruta
original de cada uno.
