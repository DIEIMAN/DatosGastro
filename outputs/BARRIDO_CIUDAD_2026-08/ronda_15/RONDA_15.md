# Ronda 15 · los dieciocho perímetros · 2026-08-10

Una sola tarea: poligonizar los perímetros que las dieciocho fichas ya tienen escritos.
**Google Places: 0 requests.** No se tocó el pipeline público, ni las láminas, ni la sección VII,
ni ninguna capa publicada. Todo lo de esta ronda es nuevo y vive en `ronda_15/`.

**Resultado en una línea: cierran 7 de los 18, otros 4 cierran una pieza de varias, y 7 no
cierran.** Los que no cierran no fallaron por falta de herramienta: **el texto de su ficha no
alcanza para cerrar una figura**, y en cada caso está dicho qué dato falta.

Salidas: `perimetros_18.csv` · `geometria/perimetros_18.geojson` (13 piezas, EPSG:4326, el mismo
CRS que `zonas_r8.geojson`) · `RONDA_15.txt` con la corrida completa ·
`errata_2026-08-10_ronda_15.csv`.

> **Nota de numeración, 2026-08-10.** Las cinco erratas de esta ronda **se publicaron primero como
> ERR-17 a ERR-21 y están renumeradas a ERR-22 a ERR-26.** ERR-17, ERR-18 y ERR-19 ya estaban
> tomadas por Cowork desde la noche anterior —las siete zonas del sur sin incorporar, el `n_vias`
> contra las columnas de vía, y la fila R03 de `via_E_22_referencias.csv`— y Codex las cerró en
> `ronda_15_codex`. El mapeo es `17→22 · 18→23 · 19→24 · 20→25 · 21→26`. **Si algún documento cita
> un ERR-17/18/19 de esta ronda, está citando el número equivocado.**

---

## 1 · Lo que destrabó el paso, y es una capa que el repositorio creía no tener

`polos_poligonizar.py` §5 declaró una carencia, y la declaró bien:

> *«Recortar a manzana necesita una capa de manzanas o parcelas, y **en el repositorio no hay
> ninguna** —sólo barrios y comunas—.»*

Por eso los 124 polígonos del borrador tienen bordes libres, y por eso hasta ayer un corredor sólo
se podía cerrar con un buffer. **Esa capa no había que conseguirla: había que construirla, y el
insumo ya estaba en disco.**

```
callejero oficial     31.961 segmentos
polygonize(union)     15.032 caras cerradas · mediana 1,05 ha · 19.414 ha en total
```

Son las manzanas. La Ciudad mide 20.300 ha y la red de calles encierra 19.414: el resto es río,
puerto y playas de maniobras, que no cierran cara. Con esto, **«Av. Álvarez Jonte entre el 4400 y
el 5299» deja de necesitar un ancho inventado**: el polígono son las manzanas con frente sobre ese
tramo, y su borde corre sobre calles por construcción.

Es la técnica que la ronda 14 usó para la cuña de Colegiales, aplicada a la Ciudad entera en vez
de a tres bordes elegidos a mano.

### El único parámetro del método, y no manda

Una manzana cuenta como frentista si comparte **20 m o más** con el tramo. Es lo único elegible que
tiene esta corrida, así que se midió a 10, 20 y 40 m:

```
zona          10 m         20 m         40 m
Z41         23,81 ha     23,81 ha     23,81 ha
Z46         30,87 ha     30,87 ha     30,87 ha
Z50         50,62 ha     50,62 ha     50,62 ha
Z28         28,73 ha     28,73 ha     27,58 ha     ← la mayor variación: 4 %
Z47         13,77 ha     13,77 ha     12,76 ha
Z44         34,39 ha     34,39 ha     33,25 ha
Z31 · Z32 · Z37 · Z51 · Z52          idénticas en los tres
```

**Seis de once no se mueven nada y la peor varía un 4 %.** Un frente de manzana mide entre 60 y
120 m: cualquier corte entre 10 y 40 deja pasar las mismas manzanas y descarta las mismas ochavas.
El parámetro no está eligiendo el resultado, que es exactamente lo que había que demostrar antes
de publicar una cifra que sale de él.

---

## 2 · La regla que decide si una ficha cierra, escrita antes de correr

Una pieza cierra **sólo si el texto le da extensión medible sobre el callejero**: un rango de
alturas, dos calles de corte, o calles que encierren una cara. **No cierra** cuando el texto nombra
un eje sin extremos, una esquina sin extensión, o puntos que el propio texto llama dispersos.

En ese caso **no se inventa el borde**: queda el provisorio del barrio y la salida declara qué
falta. Un ancho puesto por buffer es una propiedad del instrumento, no del territorio.

`cerrado_si_no` toma tres valores y no dos, porque la mitad de estas zonas son **sistemas de
subpolos** y el texto cierra unas piezas y otras no:

| valor | qué significa | qué puede hacer Cowork |
|---|---|---|
| **sí** | cerraron todas las piezas que el texto nombra | publicar `ha` y `n_locales`; dibujar relleno |
| **parcial** | cerró alguna y falta otra | **no publicar cifra de zona**; lo trazado es una pieza, no el polo |
| **no** | no cerró ninguna | queda el provisorio; sigue rayada |

---

## 3 · El resultado, en el orden de prioridad que pidió `MAGNITUD_DE_LOS_18.md`

`delta` es contra el polígono administrativo del barrio, que es lo que hoy tienen como geometría.

| # | zona | % del barrio | trazado | provisorio | delta | cerrado |
|---|---|---:|---|---|---|---|
| 1 | **Z41** Núñez | 2,8 % | 23,81 ha · 61 loc | 449,86 ha · 494 loc | −426,04 ha · −433 | parcial 1/3 |
| 2 | **Z46** Retiro | 3,9 % | 30,87 ha · 195 loc | 466,60 ha · 715 loc | −435,74 ha · −520 | parcial 2/3 |
| 3 | **Z27** Villa Santa Rita | 4,9 % | — | 215,46 ha · 182 loc | — | **no** |
| 4 | **Z50** Barracas · Montes de Oca | 5,2 % | 50,62 ha · 84 loc | 795,89 ha · 410 loc | −745,27 ha · −326 | **sí** |
| 4 | **Z51** Barracas · Iriarte | 5,2 % | 5,83 ha · 12 loc | 795,89 ha · 410 loc | −790,06 ha · −398 | **sí** |
| 5 | **Z39** Parque Avellaneda | 5,2 % | — | 473,47 ha · 173 loc | — | **no** |
| 6 | **Z28** Monte Castro | 5,7 % | 28,73 ha · 69 loc | 262,85 ha · 202 loc | −234,12 ha · −133 | **sí** |
| 7 | **Z52** La Boca · Necochea | 7,5 % | 6,14 ha · 3 loc | 504,00 ha · 295 loc | −497,86 ha · −292 | **sí** |
| 7 | **Z53** La Boca · Caminito | 7,5 % | — | 504,00 ha · 295 loc | — | **no** |
| 8 | **Z33** Mataderos | 9,7 % | — | 740,11 ha · 375 loc | — | **no** |
| 9 | **Z31** Villa Luro | 9,8 % | 13,70 ha · 41 loc | 256,80 ha · 206 loc | −243,10 ha · −165 | **sí** |
| 10 | **Z35** Balvanera · Once | 19,2 % | — | 434,43 ha · 1.253 loc | — | **no** |
| 10 | **Z40** Pompeya y P. Patricios | 19,8 % | — | 870,07 ha · 546 loc | — | **no** |
| 10 | **Z54** Pompeya · eje Sáenz | 19,8 % | — | 870,07 ha · 546 loc | — | **no** |
| 10 | **Z47** Monserrat y Congreso | 23,7 % | 13,77 ha · 133 loc | 219,97 ha · 913 loc | −206,19 ha · −780 | **sí** |
| 10 | **Z37** Almagro | 29,1 % | 25,79 ha · 89 loc | 405,26 ha · 868 loc | −379,47 ha · −779 | parcial 1/3 |
| 10 | **Z32** Liniers · Mercado Andino | 33,7 % | 7,00 ha · 63 loc | 437,61 ha · 447 loc | −430,61 ha · −384 | **sí** |
| 10 | **Z44** Villa Ortúzar | 34,2 % | 34,39 ha · 69 loc | 185,46 ha · 201 loc | −151,07 ha · −132 | parcial 1/2 |

**Las siete cerradas suman 125,79 ha y 405 locales.** Las once con algo trazado suman 240,65 ha y
819 locales. **Los tres barrios que contienen dos polos —Barracas, La Boca y el par
Pompeya–Parque Patricios— repiten el provisorio en dos filas, y esa columna no se suma.**

**Y el orden de prioridad se confirmó al medirlo.** De los seis de proporción más baja, **cuatro
trazaron y dan entre el 0,7 % y el 6,6 % de la superficie de su barrio**: ahí el provisorio estaba
multiplicando la superficie del polo por entre quince y ciento cuarenta veces. Los otros dos —Villa
Santa Rita y Parque Avellaneda— no trazaron, y son los dos casos en que el texto de la ficha no
alcanza. **La proporción baja predijo bien dónde el provisorio miente; no predice si la ficha
alcanza para arreglarlo.**

---

## 4 · La prueba que decide si un trazado describe al polo o al algoritmo

No la inventa esta ronda: **es la lección de Almagro, escrita en su propia ficha.** El fragmento
que el agrupamiento automático detectó ahí mide 5,7 ha y **no contiene ninguno de los cinco Bares
Notables** de la zona. Un polígono que no contiene los hitos sobre los que su ficha se apoya no es
el polígono de esa ficha, por prolijo que sea su borde.

Aplicada a los once trazados, contra la capa de hitos con punto, y con la distancia al borde para
los que quedan afuera —**sin la distancia, «0 de 9» se lee como una refutación y puede ser lo
contrario**—:

| zona | hitos dentro / del barrio | lectura |
|---|---|---|
| **Z47** Monserrat | **6 de 13** | dentro: Tortoni, London City, Iberia, El Imparcial, 36 Billares, Cabildo. Afuera: **seis de los siete son direcciones que la ficha lista como «remates»** (La Puerto Rico a 160 m, El Querandí 273, El Colonial 375, Laurak Bat 393, Centro Asturiano 732, Bar Seddon 774) |
| **Z37** Almagro | **3 de 8** | dentro: El Símbolo y La Orquídea, los dos Notables **de Corrientes**. Afuera: El Banderín a 107 m y Las Violetas a 697 m, que son de las dos piezas que no cerraron |
| **Z46** Retiro | **3 de 11** | dentro: Saint Moritz, Florería Atlántico, Tancat. Afuera: **Florida Garden a 5 m y Plaza Bar a 59 m**, que son de la pieza de Florida, que no cerró |
| **Z50** Montes de Oca | 2 de 6 | dentro: Los Campeones y El Progreso. Los otros cuatro, entre 359 y 813 m |
| **Z41** Núñez | 1 de 5 | dentro: Ness. Garabato Bistro queda **a 6 m** |
| **Z51** Iriarte | 1 de 6 | dentro: Los Laureles, que es su Bar Notable |
| **Z28** Monte Castro | 1 de 2 | dentro: El Fortín. Café Olimpo a 638 m, que es lo que su propia ficha dice |
| **Z44** Villa Ortúzar | **1 de 1** | La Mezzetta |
| **Z31** Villa Luro | 0 de 0 | **la ficha dice «Los referentes. Ninguno.»** No hay nada que contener |
| **Z32** Liniers | 0 de 1 | **la ficha dice «Cero Bares Notables en Liniers»** y entra igual, a propósito |
| **Z52** La Boca · Necochea | **0 de 9** | y acá la prueba encuentra algo. Ver abajo |

**Nueve de once son coherentes con lo que su ficha dice**, y en tres casos la prueba señala con
precisión la pieza que falta: los hitos que quedan afuera de Retiro, Almagro y Monserrat son
exactamente los de las piezas que no cerraron. **Eso no es una casualidad favorable: es la
prueba funcionando.**

---

## 5 · Los cuatro hallazgos que cambian una decisión

### 5.1 · La Boca: el perímetro más preciso del sur no contiene ninguna de sus cinco anclas

Es el único perímetro de las dieciocho fichas que **no lo dibujó este atlas**: sale, literal, del
texto de una obra pública de enero de 2026, que dice *«aproximadamente 340 metros lineales»*.

```
largo declarado por la obra pública       340 m
largo medido sobre el callejero           319 m       −21 m  (6,0 %)
polígono                                 6,14 ha ·  3 locales
hitos de La Boca adentro                 0 de 9
```

**El largo verifica.** Lo que no verifica es la afirmación de la ficha. La ficha dice, sobre Café
Roma y Boca a Boca: *«los dos caen en el entorno mismo de Necochea y Olavarría — es decir, adentro
del tramo que la obra pública delimita»*. Medido: **Café Roma queda a 111 m y Boca a Boca a 529 m.**
Banchero, su ancla normativa, a 54 m.

**Ninguno de los cinco está adentro**, y el más cercano está a media cuadra. O el polo es más
grande que el tramo de la obra pública, o sus anclas no son suyas. **La ficha no puede sostener las
dos cosas a la vez, y hoy las sostiene.** → **ERR-22.**

### 5.2 · Villa Ortúzar: dos tercios del corredor están en otros dos barrios

Av. Álvarez Thomas 600-1700, «ambas aceras». Trazado y repartido contra la capa de barrios:

```
Colegiales      35 %
Chacarita       34 %
Villa Ortúzar   31 %      ← el barrio de la zona
fuera del provisorio: 23,70 ha de 34,39 (68,9 %)
y 15,93 ha con 25 locales caen DENTRO de R09R19_CHACAGIALES, que ya está publicada
```

**Es la lección de la cuña de Colegiales repitiéndose exacta**, y una ronda después: Av. Álvarez
Thomas **es** el límite del barrio, así que leer «ambas aceras» pone la mitad de las manzanas del
otro lado. La ficha ya avisaba que el extremo sur toca Chacagiales; **lo que no estaba medido es
que son 15,93 ha y 25 locales, ni que el reparto es de tercios.** → **ERR-23.**

### 5.3 · Almagro: el corredor que su ficha nombra está 70 % adentro del Abasto

```
corredor Av. Corrientes 3500-4200        25,79 ha ·  89 locales
compartido con R13 Abasto                18,09 ha ·  65 locales   ← 70,2 % del trazado
```

La ficha de Almagro dice **«excluido el sector del Abasto»** y su nota de delimitación declara el
solape sin depurar con cuatro establecimientos nombrados. Medido, el solape no es de cuatro
establecimientos: **es de 65 locales y de siete de cada diez hectáreas del corredor.** Publicar esa
cifra como de Almagro contaría dos veces la mayor parte. → **ERR-24.**

### 5.4 · Villa Luro: la ficha escribe la misma pieza dos veces y las dos no coinciden

*«Bulevar Ramón L. Falcón 5400-5800, entre Albariños y Escalada»* — un rango de alturas y dos
calles de corte para el mismo tramo. Es la zona de la que la ficha dice que tiene **«la
delimitación más nítida del oeste, fijada con numeración por prensa nacional»**.

```
por alturas, 5400-5800                   1.028 m
por calles de corte, Albariño a Escalada 1.284 m
diferencia                                 +256 m   ← unas dos cuadras y media, un 25 %
```

**Se adopta el rango de alturas**, porque es lo que la ficha declara como fijado por la fuente; las
calles de corte llegan más lejos. La diferencia queda declarada. → **ERR-25.**

> **Y este hallazgo se produjo por una falla silenciosa que casi lo tapa.** La primera corrida
> escribió `ALBARIÑOS` y el callejero lo tiene como `ALBARINO`, en singular: la búsqueda devolvió
> vacío, el control devolvió `None` y **no imprimió nada ni tiró error**. Es la sexta vez que este
> proyecto encuentra esta familia de falla. Ahora un nombre de calle que no resuelve **corta la
> corrida** en vez de producir un número de menos.

---

## 6 · Los siete que no cierran, y qué dato le falta a cada uno

Ninguno falló por herramienta. **A los siete les falta un dato que sólo puede poner quien escribe
la ficha**, y en cinco casos son cuatro palabras: un rango de alturas.

| zona | lo que dice | lo que falta |
|---|---|---|
| **Z27** Villa Santa Rita | «puntos dispersos con anclaje en Av. Álvarez Jonte» | el tramo de Álvarez Jonte, en alturas o entre cortes. La ficha ya declara que la vía de densidad no abre |
| **Z39** Parque Avellaneda | «el anillo del parque, sobre Av. Olivera y Av. Lacarra» | **las dos avenidas se cruzan a 0 m**: son dos lados de una esquina, no cuatro de un anillo. Faltan las otras dos calles |
| **Z53** La Boca · Caminito | «entorno de Caminito y la Vuelta de Rocha» | «entorno» no es extensión, y **la Vuelta de Rocha no está en el callejero: es un recodo del Riachuelo** |
| **Z33** Mataderos | la Feria «en Av. Lisandro de la Torre y Av. de los Corrales» | una esquina sin extensión, y la segunda pieza está a más de un kilómetro |
| **Z35** Balvanera · Once | «en revisión» | **la ficha no escribe ninguna calle.** No hay nada que poligonizar |
| **Z40** Pompeya y P. Patricios | tres piezas nombradas | ejes sin extremos. Y el Barrio Charrúa tiene tres bordes, pero **las vías del Belgrano Sur no son una línea del callejero** |
| **Z54** Pompeya · eje Sáenz | «eje Av. Sáenz, núcleo en el Mercado, Sáenz 790» | una sola altura no es extensión; y el reparto con Z40 sigue pendiente |

### Dos lecturas alternativas se midieron y **no se adoptan**, para que se vea por qué

**Parque Avellaneda, delimitado por sus tres referentes** (Lacarra 836-1500, Olivera 1557):
**59,97 ha y 6 locales.** De esas 59,97, **44,21 ha son una sola cara con cero locales: el parque.**
Es la advertencia de la propia ficha —*«buena parte de la superficie encerrada es el parque, donde
no hay locales»*— convertida en número. Y delimitaría por dónde están los referentes, que la ficha
declara **dudosos los tres**, y no por el perímetro escrito.

**Mataderos, por el eje comercial Alberdi 5501-6299**: 24,27 ha y 55 locales. **Ese tramo es el eje
del IDECBA, no el perímetro del polo**, y tomarlo sería atribuirle al polo el objeto de otra fuente.

---

## 7 · Lo que Cowork puede hacer con esto, y lo que no

**Puede publicar cifra y dibujar relleno en siete:** Z50, Z51, Z28, Z52, Z31, Z47 y Z32. Las
columnas `ha` y `n_locales` de `perimetros_18.csv` son las de esos polígonos.

**No puede publicar cifra de zona en cuatro** —Z41, Z46, Z37, Z44—, aunque tengan geometría en el
geojson: **lo trazado ahí es una pieza de un sistema de subpolos, no el polo.** Se pueden dibujar
las piezas, con su nombre de pieza; la ficha sigue sin cifra de escala.

**Siete siguen rayadas**, y ahora con una línea que dice exactamente qué falta.

**Tres cifras no se pueden citar sin su salvedad**, y son las de §5: Almagro pisa el Abasto en el
70 % de su corredor, Villa Ortúzar reparte su corredor en tercios entre tres barrios, y el tramo de
Necochea no contiene ninguna de sus cinco anclas. **Ninguna de las tres se resuelve desde el
repositorio: las tres son decisiones de delimitación.**

---

## 8 · Lo que esta ronda NO hizo, y conviene que quede escrito

- **No tocó ninguna capa publicada.** `zonas_r8.geojson`, `referencias_r8.geojson` y las fichas
  quedan como estaban. El geojson nuevo es una capa nueva.
- **No adoptó ningún perímetro.** Trazar no es decidir: los siete que cierran cierran *según su
  propio texto*, y adoptarlos es de Diego.
- **No resolvió los arrastres** —ERR-11, ERR-12, el normalizador de calles, los 584 de Palermo, la
  cuña de Colegiales, los 10 `requiere_cruce` de la vía E, la vía B contra el catálogo cargado, ni
  la atribución del eje Triunvirato—. Siguen abiertos.
- **No tocó Z43 Colegiales ni Z24 ni Z39b**, que ya tenían perímetro propio o lectura de la r14.
- **No corrigió la capa de hitos**, sólo la deduplicó para contar. Ver ERR-26.
