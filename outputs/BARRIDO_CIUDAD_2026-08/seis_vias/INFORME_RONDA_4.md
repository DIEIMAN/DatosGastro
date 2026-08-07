# Ronda 4 · los dos enclaves con delimitación de fuente, la prioridad de verificación y las fuentes con defecto

*7 de agosto de 2026 · DGDGAS · continúa `INFORME_RONDA_3.md`*

**Google Places: 0 requests.** USIG: 37 consultas nuevas, todas cacheadas. Geometría publicada,
agrupamientos, fichas y cartografía: intactos. Los archivos de la ronda 3 quedan como estaban; esto
escribe con sufijo `_r4`.

---

## Lo primero, porque es la consecuencia que no estaba pedida

Reescribir E07 sobre la delimitación de fuente **le saca la vía D a dos filas**, y una de ellas ni
siquiera está en Liniers.

| fila | vía D ronda 3 | vía D ronda 4 |
|---|---|---|
| PGR_P017 · Liniers | abierta por E07 | `no_medida` |
| PGR_P020 · **Villa Luro** | abierta por E07 | `no_medida` |
| PGR_P021 · Liniers | abierta por E07 | **abierta por E07** |

El E07 de la ronda 3 medía 131,7 ha porque la consigna no daba cabeceras y tres calles enteras de
Liniers entraban completas. Con 4.981 m de eje, el enclave llegaba hasta Villa Luro y abría una vía
allá. Con el eje de 284 m que mide la fuente, **queda la fila que contiene al mercado y se caen las
dos que lo tocaban por estiramiento.** Vía D de las 94: 12 → 10. Las 22 zonas no se mueven.

Esto no es un ajuste cosmético del polígono: es una celda de la matriz que decía «sí» sin
sostenerlo.

---

## 1 · E07 Liniers, con las cuatro fuentes y la métrica cruzada

**El eje mide 284,0 m** sobre José León Suárez entre Ramón Falcón y Ventura Bosch.

| medición | valor | contra el eje |
|---|---:|---:|
| eje del callejero entre los dos cruces | **284,0 m** | — |
| la misma distancia en línea recta | 284,0 m | 0,0 m |
| tu medición con USIG | 285 m | **−1,0 m · 0,4 %** |
| Ciocoletto (2019), «aproximadamente» | 300 m | −16,0 m · 5,3 % |

**Coincide.** Y conviene decir por qué no es la misma medición hecha dos veces: USIG devuelve la
distancia entre dos **puntos de altura** y esto mide la **longitud del eje** del callejero entre dos
**cruces**. Sobre una calle recta convergen, y acá convergen hasta el metro. El número del paper es
«aproximadamente 300 m» y no admite más precisión que ésa: 284 está adentro de esa aproximación.

**Las tres correcciones tuyas, aplicadas.** Montiel afuera —la fuente que la nombra ubica el mercado
en Rivadavia 1600 cuando el cruce está en la 11.000, un error verificable de más de nueve mil
números—. Salteñería, no Salchichería. Y eje con transversales, no cuadrante.

**Y no hizo falta trazar las transversales.** Las cinco puertas de Ibarrola (7184, 7193, 7239, 7276,
7291) y la de José León Suárez 216 caen **6 de 6** adentro del eje con su buffer declarado de 150 m,
porque Ibarrola está a una cuadra. Agregarle a E07 las tres transversales enteras habría sido volver
al cuadrante por otra puerta.

Largos dentro de Liniers, para cerrar la trampa de la ronda 3: `FALCON, RAMON L.,CNEL.` 1.728 m
—ésta— contra `FALCON, RAMON L.,CNEL. AV.` 128 m —la que usaba la ronda 1—.

**E07: 131,7 ha → 15,6 ha.** El *desde* queda cargado: mediados de los 80, por el cierre del Mercado
de Frutas y Verduras (1984) y de la Feria (1986).

---

## 2 · El Barrio Chino: 51 puertas geocodificadas, y la forma que sale

**49 de 51 geocodificadas.** Las dos que no: Ultramarinos y el Templo Chong Kuan (sin altura).

| zona | n |
|---|---:|
| núcleo — dos cuadras de Arribeños, ±150 m | **39** |
| corredor — viaducto, fuera del núcleo, ±150 m | **6** |
| afuera de los dos | 4 |
| sin geocodificar | 2 |

El núcleo mide **255,2 m** contra los 256 que mediste: coincide. La precedencia está declarada —el
núcleo gana— porque las dos bandas se solapan y sin regla el reparto no significaría nada.

**Confirmado lo de Ultramarinos.** USIG no resuelve la altura 1980 sobre Arribeños en ninguna de las
tres variantes probadas: `Pasaje Arribeños 1980`, `Arribeños 1980` y `Arribeños Pje. 1980`. Queda sin
geocodificar y declarado, no aproximado. Y es lo más caro de la lista, porque es **la única vía B
candidata nueva del Barrio Chino**: ficha propia en el sitio de la Guía Michelin.

### La corrección que sale de medir la forma

**El corredor no es perpendicular al eje histórico: es casi paralelo.**

| | rumbo |
|---|---:|
| núcleo (Arribeños, Juramento–Olazábal) | 145,3° |
| corredor (traza del viaducto, Monroe–Echeverría) | 126,2° |
| **ángulo entre los dos** | **19,1°** |

Arribeños corre **al lado** de las vías y no las cruza: por eso el núcleo está bajo el viaducto sin
cruzarlo, y el paseo que corre debajo corre junto a Arribeños, desplazado unos 50 m. La figura que
sale no es una cruz. **Son dos bandas casi paralelas separadas por la traza**, y el desborde no es
transversal: es longitudinal, sobre la misma dirección, más largo que el núcleo.

Eso no debilita tu conclusión —el radio equivoca la forma— la cambia de motivo: no es que falte el
brazo sur, es que **la banda es más larga que las dos cuadras**, y la parte nueva está en su
extremo.

El corredor lo construí desde el callejero oficial, no desde las 51 puertas: los siete cruces que el
GCBA marca como `Tren Elevado` entre Monroe y Echeverría. Definirlo con las mismas puertas que
después se clasifican contra él habría dado «todas adentro» por construcción.

### El radio, medido

| forma | contiene | superficie | ha por puerta |
|---|---:|---:|---:|
| radio de cuatro manzanas (510 m) | 45 de 49 | 81,7 ha | 1,82 |
| núcleo + corredor | 45 de 49 | **30,7 ha** | **0,68** |

La cuadra de Belgrano medida acá es de 128 m, así que cuatro manzanas son 510 m. **Las dos formas
capturan lo mismo y el radio gasta 2,7 veces más superficie.** Ése es el argumento contra el radio,
y es más fuerte que el de la forma: no pierde nada, sobra en todas direcciones.

### La añada contra la zona

| añada | núcleo | corredor | afuera |
|---|---:|---:|---:|
| 2024-2026 | 17 | 4 | 4 |
| 2018-2023 | 6 | 2 | 0 |
| hasta 2017 | 9 | 0 | 0 |

**Tu hipótesis se sostiene, con el tamaño que tiene.** Todo lo anterior a 2017 está en el núcleo, sin
excepción; de lo reciente, 8 de 25 cayó afuera del núcleo. El desborde es real y es nuevo. Lo que no
dice el cuadro es que el corredor haya desplazado al núcleo: 17 de 25 aperturas recientes siguen
adentro de las dos cuadras.

**El conteo queda como lo dejaste:** los ~120 comercios de la Asociación, julio de 2020, en el peor
momento posible, y no hay conteo posterior de nadie. «Más de 40 locales en 4 cuadras» no entra:
cuenta el paseo Vía Viva y es una proyección.

---

## 3 · La prioridad de verificación, que es lo que más importa

De las 44 filas con hitos, **18 dependen de un solo hito** y **15 de ésas lo tienen sin resolver**.
Ésas son las frágiles: si el hito cerró, la fila no baja de grado, se cae entera. Es exactamente
P008 / Los Laureles.

**Las 15, en orden:** San Telmo (Bar El Federal) · Avenida Caseros / Barracas (Británico) · Villa
Urquiza (Café de la U) · Flores (La Farmacia) · P004 Villa Lugano (Yiyo el Zeneize) · P013 Mataderos
(Bar del Glorias) · P021 Liniers (El Ciervo) · P032 La Boca (La Perla) · P044 San Cristóbal (Saverio
Helados) · P066 Barracas (Los Campeones) · P084 Balvanera (Las Violetas) · P088 Palermo (La Alacena
Trattoria) · P092 Palermo (Varela Varelita) · P101+P099 Balvanera (Café de los Angelitos) · **P008
Barracas (Los Laureles, `en_disputa`)**.

Las otras tres frágiles ya están resueltas y abiertas: Bar Conde, El Fortín, El Tokio.

**Los que más rinden**, porque están adentro de varias filas a la vez:

| hito | filas | zonas | barrio |
|---|---:|---:|---|
| Tancat | 3 | 2 | Retiro |
| Confitería Saint Moritz | 3 | 2 | Retiro |
| Florida Garden | 3 | 2 | Retiro |
| Plaza Bar | 3 | 2 | Retiro |
| El Imparcial | 2 | 1 | Monserrat |
| 36 Billares · Café Tortoni · El Querandí · La Puerto Rico | 2 | 1 | Monserrat / San Nicolás |
| Zum Edelweiss · La Giralda · Petit Colón · Guerrín | 2 | 2 | San Nicolás |
| ANAFE | 2 | 0 | Colegiales |

**El orden de ataque que sale de cruzar las dos listas:**

- **Tanda A · 15 verificaciones.** Los que son el único hito de su fila. Cada una decide una fila
  completa, para los dos lados.
- **Tanda B · 14 verificaciones.** Los que están en dos o más filas. Una consulta, varias celdas.
- **Tanda C · 105.** Comparten fila con otros: mueven la matriz sólo si el resultado es «abierto».
- **Fuera · 72 hitos pendientes que no caen en ninguna fila.** Verificarlos no mueve nada.

**A + B son 29 verificaciones y tocan 22 filas distintas: el 13 % del trabajo para el 50 % de las
filas con hitos.** Ésa es la ronda de verificación documental.

Dos cosas del método que conviene tener a mano cuando se corra:

- Un `abierto` y un `cerrado` no valen lo mismo. Un `abierto` pasa la fila a `activo` sola. Un
  `cerrado` sólo la extingue si no queda ningún otro pendiente adentro — y hoy **ninguna fila con
  más de un hito está en esa situación**. Por eso la tanda A es la única donde un cierre cierra algo.
- Los cuatro de Retiro son cuatro consultas que tocan las mismas 3 filas. Rinden por fila, no por
  fila nueva: conviene verificarlos juntos y en una sola pasada.

---

## 4 · Cuatro fuentes con defecto estructural, cargadas como capa

`outputs/BARRIDO_CIUDAD_2026-08/fuentes/fuentes_defectos_conocidos.csv`, con dos campos separados a
propósito: **la regla que un script puede evaluar** y **lo que la marca prohíbe afirmar**.

| id | fuente | clase | prohíbe |
|---|---|---|---|
| **FD-01** | cronista.com con `fecha_actualizacion = 2025-09-24` | re-sellado masivo de archivo | leer esa fecha como fecha de verificación |
| FD-02 | catálogo consolidado de Bares Notables | atribución territorial errónea | usar su barrio/comuna sin cotejar USIG |
| FD-03 | PDF del catálogo bajo la URL de la Res. 3758/24 | contenido mutable bajo cita estable | citar «el catálogo» sin decir cuál |
| FD-04 | Time Out Buenos Aires | atribución territorial errónea | usar el barrio que declara |

**La marca no borra el dato.** Una nota re-sellada sigue valiendo por su año de origen: si es de
2021, describe 2021. Lo que se descarta es la fecha, que era lo único que hacía trabajo indebido.

### Dónde pega FD-01 en lo nuestro · 20 marcas

- **5 establecimientos del Barrio Chino** citados de El Cronista 26/08/2021 — los que ya marcaste:
  Fujisan, China Rose, Dogg, Las Carnitas, Garbis.
- **8 citas de la evidencia documental** que invocan la actualización de 2025 como si fuera añada. La
  que más pesa es **R03 San Telmo**: su vía E cuenta a El Cronista «2021, act. 2025» como uno de sus
  grupos independientes, y con FD-01 ese grupo tiene añada 2021. R03 ya venía con cero vías abiertas.
- **6 hitos de la capa que salen de cronista.com** —Pin Pun, La Mezzetta, San Carlos, Gran Pizzería
  José, San Antonio y la heladería Nápoli— **sin fecha de actualización registrada por nosotros**.
  Quedan `pendiente_de_comprobacion`: no se descartan y no se dan por buenos. No encontrar la fecha
  no es haberla verificado distinta, y son seis notas: mirarlas es barato.

**Y un falso positivo, marcado como tal en la tabla:** R15 Villa Devoto cita «Time Out BA
24/09/2025». Misma fecha, otro medio. FD-01 es dominio **más** fecha, no fecha sola.

**Y el contraejemplo que sostiene que la marca sea por fecha y no por medio:** la nota de El Cronista
sobre Los Laureles del 05/08/2026 está publicada 12:33 y actualizada 12:34. Un minuto. Eso es una
corrección de redacción y esa nota cuenta. FD-01 no dice «El Cronista no sirve».

La sección para la edición técnica está escrita y lista para pegar:
`fuentes/SECCION_EDICION_TECNICA_FUENTES_CON_DEFECTOS.md`.

---

## 5 · Los tres datos de vigencia, y Boca a Boca

**Cargados:** Todos Contentos (Arribeños 2177) como `dudoso_probablemente_abierto` —segundo caso El
Tokio—; Hong Kong Style (Montañeses 2149) y Dragón Porteño (Arribeños 2137) como `cerrado`. Los tres
caen en el núcleo.

Sobre el vocabulario, que no es un detalle: `dudoso_probablemente_abierto` no existe en la capa de
hitos, cuyo vocabulario es `si · no · en_disputa · dudosa · sin_verificar`, y `dudosa` no dice hacia
qué lado se duda. El estado viaja partido en dos campos —`vigencia` y `sentido_de_la_duda`— para que
si mañana entra a la capa de hitos se pliegue a `dudosa` **sin perder la dirección de la duda**.

Y una asimetría que conviene no perder: los tres cierres salen de la **misma** nota de iProfesional
del 04/07/2020. Que dos de ellos no tengan nada después no es evidencia de que sigan cerrados: es
que esa nota no vuelve a mirar. El Tokio y Todos Contentos reabrieron sin que ningún listado lo
registrara.

**Boca a Boca: confirmado.** La lista de las doce altas dice Av. Benito Pérez Galdós 207; la capa de
hitos tiene 201, que es la altura del Boletín. La capa ya traía la discrepancia anotada, y la base
gastronómica tiene las dos alturas como dos registros de fuentes distintas.

**Lo que sí se puede decir con un número: los dos puntos están a 2,6 m.** Es la misma puerta con dos
alturas publicadas, no dos locales. El conflicto es documental y no mueve ninguna medición —mismo
polo, mismo barrio, misma celda—. No se resuelve acá porque las dos fuentes son del mismo rango y la
resolución de las altas, que zanjaría, sigue sin localizarse. Queda como `conflicto_direccion` y se
verifica en campo.

---

## Lo que espera decisión

1. **La forma final de E02**: dos bandas casi paralelas (19,1°), no cruz y no radio. Está construida
   y medida; falta que la firmes.
2. **Los 4 «afuera» del Barrio Chino** —Ma La Tang, Shanghai Express, Gokana Omakase, Sachi— quedan
   fuera de las dos bandas. O el polígono los toma y crece, o se aceptan como derrame declarado.
3. **Ultramarinos**: sin geocodificar, y es la única vía B candidata nueva del enclave. Necesita
   resolución de dirección, no otra fuente.
4. **La ronda de verificación**: tandas A y B, 29 hitos. Es la que destraba la vía B.
5. **Las seis notas de cronista.com de la capa**: registrar su fecha de actualización y aplicar o
   levantar FD-01 sobre cada una.
6. **R03 San Telmo** sigue con cero vías abiertas y ahora además con una de sus fuentes de vía E
   reañadada a 2021.
7. Sigue de antes: el sexto valor `sin_hitos`, el quinto de la vía D, R18, la resolución de las 12
   altas, E06 por altura de puerta, la serie Z sin tabla, y todo el arrastre de la ronda 3.
