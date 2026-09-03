# Etapa 1 · el punto de control pasó

Las capas llegaron bien: **12.640 manzanas**, **31.961 tramos de calle** con nombre y alturas, y
**3.554 radios censales** con población, hogares y NBI. Corrí la asignación y las dos pruebas.

---

## Los locales ya están puestos sobre manzanas

**27.666 de 27.727 locales quedaron asignados a una manzana: el 99,8 %.** Sólo 61 quedaron sin
ninguna a menos de 25 metros, y están donde uno esperaría: 15 en Palermo, 7 en Retiro, 7 en Belgrano,
7 en Villa Soldati, 7 en Recoleta —parques, la Costanera, terrenos de ferrocarril, el Riachuelo—.

El 62,8 % cae adentro del polígono de manzana y el 37,2 % cae en la calzada, a **3,3 metros de
mediana**. Eso no es un error: es que muchas fuentes geocodifican a la línea de frente o al eje de la
calle, no al interior de la parcela.

---

## Prueba 1 · los códigos catastrales · **100,00 %**

**10.889 locales traen su código de manzana de origen** —sección y manzana, del Relevamiento de Usos
del Suelo—. Comparé ese código contra la manzana en la que cae el punto:

> ### 10.889 de 10.889 coinciden. Cero diferencias.

Ni una sección equivocada, ni una manzana corrida. **La asignación geométrica reproduce exactamente
el código catastral**, y eso prueba que se puede confiar en ella para los 16.800 locales que no traen
código.

Una honestidad: esos 10.889 caen adentro de la manzana 10.886 veces, así que **esta prueba valida el
punto-adentro-del-polígono, no la regla de recuperación a 25 metros** —que sólo tocó 3 casos, y
acertó en los 3—. Para eso hice la segunda prueba.

---

## Prueba 2 · la dirección · **94,9 %**

Si el punto está bien puesto, la manzana en la que cae tiene que **dar a la calle que dice su propia
dirección**. Crucé las 12.640 manzanas contra el callejero para saber qué calles rodean a cada una
—mediana de 4 calles por manzana, que es lo que uno esperaría— y después comparé.

| | |
|---|---:|
| locales con dirección legible y manzana asignada | 14.252 |
| **la calle no existe en el callejero con esa forma de escribirla** | **1.410** (9,9 %) |
| sobre los 12.842 restantes: **la manzana da a su propia calle** | **12.187 · 94,90 %** |
| no da → quedan listados para revisar | 655 · 5,10 % |

Y el detalle que importa: **los recuperados a 25 metros aciertan el 95,8 %**, un poco mejor que los
que caen adentro (92,7 %). La regla de recuperación no sólo no ensucia: los puntos geocodificados al
frente son, si acaso, los mejor ubicados.

### De paso apareció una diferencia de escritura que hace falta arreglar igual

El callejero oficial escribe al revés: **«RIVADAVIA AV.»** donde la base escribe **«Av. Rivadavia»**,
y **«ALVAREZ, JULIAN»** donde la base escribe **«Julián Álvarez»**. Comparando por conjunto de
palabras en vez de por texto, el problema baja del 29,7 % al 9,9 %.

Lo que queda son títulos que el callejero abrevia —*Teniente General*, *Coronel*, *Mariscal*,
*Fray*— y nombres de pila que acorta. **Quedan 880 formas distintas listadas en
`calles_que_no_cierran.csv`**, ordenadas por cuántos locales arrastran. Esa tabla hace falta igual
para la Etapa 3: sin ella no se pueden escribir los bordes.

---

## Barrio y comuna, por geometría

**Coinciden el 99,97 %** con lo que la base ya traía: 27.718 de 27.725. Las 7 diferencias son todas
casos únicos sobre una línea de borde —un local de Villa Urquiza que cae en Villa Pueyrredón, uno de
Palermo que cae en Villa Crespo—. Cada uno queda anotado, ninguno corregido en silencio.

---

## Cómo se reparte la gastronomía por manzana

Del universo publicado —23.981 locales—, **6.302 manzanas tienen al menos uno**. La mitad de la
Ciudad, en manzanas.

| manzanas con… | cuántas |
|---|---:|
| 1 local | 1.836 |
| 2 a 4 | 2.671 |
| 5 a 9 | 1.328 |
| 10 o más | 467 |

**La manzana más gastronómica de Buenos Aires tiene 42 locales.** Es la 023-148B.

---
---

# La prueba de que esto funciona: dos polos redibujados

Redibujé dos, con la regla de armado del plan y sin tocarla a mano. **La línea punteada azul es el
borde de hoy**; el naranja es el nuevo.

| polo | superficie | locales | densidad | manzanas |
|---|---|---|---|---:|
| **Avenida Boedo** | 179,5 → **138,9 ha** | 245 → **257** | 1,37 → **1,85** | 84 |
| **Devoto** | 478,7 → **99,3 ha** *(el 21 %)* | 422 → **232** | 0,88 → **2,34** | 82 |

**Devoto es el caso que muestra el problema entero.** El borde de hoy son cuatro círculos enormes que
abarcan casi todo el barrio, con manzanas enteras adentro sin un solo local. El nuevo sigue la
Avenida Beiró, Lastra y Segurola, que es donde efectivamente está la gastronomía de Devoto. **La
superficie cae a la quinta parte y la densidad se multiplica por 2,7.**

Y sale un dato que el borde viejo escondía: al armarlo por manzanas, **Devoto se separa en 17 piezas**
—la mayor con 223 locales, y otras 196 locales repartidos en 16 pedazos sueltos—. Eso hay que mirarlo
con vos: puede ser que Devoto sean dos polos, o uno con satélites.

**Boedo, en cambio, da una sola pieza con los 245 locales adentro**: es un corredor de verdad. Su
superficie baja menos porque el borde viejo, aunque feo, no estaba tan lejos.

### Lo que todavía no funciona, y lo digo antes de que lo veas

**La regla específica para corredores no está bien.** Probé una variante que toma sólo las manzanas
que dan a la avenida y devuelve además de qué transversal a qué transversal va. Devolvió *«de
República Bolivariana de Venezuela a Carlos Calvo»*, que es una parte chica de la Avenida Boedo. **El
error es que la avenida viene partida en decenas de tramos en el callejero, y mi rutina tomó los
extremos del primer tramo en vez de los extremos geográficos.** Es un error mío, no de los datos, y
es exactamente el trabajo de la Etapa 3.

Por eso el mapa que te mando de Boedo usa la regla general: la forma es más escalonada de lo que
debería ser un corredor —admite cualquier manzana con un local—, pero **la avenida se ve, las
transversales se leen, y el borde está sobre las calles**. Con la regla de corredor afinada, esa
forma se convierte en una cinta limpia de dos manzanas de ancho.

---
---

# Una advertencia sobre los mercados

**El archivo `mercados.csv` que bajamos no sirve para el punto 4.** Trae 6 filas y son *Centros de
Abastecimiento Municipal*: mercados de barrio de canasta básica, no gastronómicos. Uno solo se
superpone con lo que buscamos —el CAM Nº 128 es el Mercado de Belgrano—.

Y busqué en la base: **hay 5 nombres que hablan de mercado o patio gastronómico, y ninguno es de los
que interesan.** Ni San Telmo, ni el Progreso, ni Bonpland, ni el Andino aparecen como local.

> **Conclusión: la Ciudad no publica en datos abiertos la lista de mercados y patios gastronómicos.**
> Existe como página del sitio de turismo, pero no como archivo. Para contestar el punto 4 hay que
> **construir la capa**, igual que hubo que construir el bodegón: los siete que ya tenemos, más los
> que falten, cada uno con dirección verificada y su fuente escrita al lado. Es media jornada y es
> una decisión tuya, no un dato que se baja.

---

# Y el censo es 2010

Confirmado al abrirlo: **3.554 radios, con población total, varones, mujeres, viviendas, hogares y
hogares con NBI**. Es una buena capa y la granularidad es la que necesitamos —3.554 piezas para 41
polos—, pero es el Censo 2010. La decisión B del plan sigue abierta.
