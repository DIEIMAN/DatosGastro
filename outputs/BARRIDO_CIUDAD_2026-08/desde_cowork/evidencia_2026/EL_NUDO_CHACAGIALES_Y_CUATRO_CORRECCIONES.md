# El nudo Chacagiales, y cuatro correcciones — dos de ellas mías

*7 de agosto de 2026 · sobre la ronda 7 del repositorio*

---

## Primero: el número salió como estaba previsto, y la mitad de la diferencia tiene nombre

| vía B | por contención | por zona |
|---|---|---|
| abre | 16 | **33** |
| pendiente | 27 | 37 |
| no abre | 51 | 24 |

**La vía B se duplica cambiando solo a qué objeto se le pregunta.** Misma capa de hitos, mismas 94 filas.

Y lo que más importa es el reparto de las 51 `sin_hitos`: **27 son "la zona sí tiene, el fragmento no" y 23 son "la zona tampoco".** Eso es exactamente lo que la medición anterior no podía distinguir, y ahora está separado: **27 filas que parecían vacías no lo estaban.**

`PGR_P083 · Almagro` sigue siendo el caso testigo: 5,67 hectáreas, zona con ocho hitos, soporte activo.

---

## Cuatro correcciones. Dos son mías y una es fea

### 1 · Le pasé cinco hitos duplicados al repositorio

Los cinco Bares Notables de Monserrat que reporté como "que no estaban en la capa" **ya estaban, con punto y dirección**. El repositorio no los dio de alta, y explicó por qué: duplicarlos habría inflado justo la vía B que la ronda venía a medir.

**Escribí la auditoría de duplicados esta misma tarde y después alimenté un duplicado.** Es el error más incómodo del día, porque no es de dato sino de método: verifiqué el catálogo contra mi propia lista y no contra la capa cargada. Las altas reales eran cuatro, y tres de ellas abren la vía D, no la B.

**La regla que sale: antes de reportar un hito como nuevo, se cruza contra la capa, no contra mis archivos.**

### 2 · El perímetro de Flores casco histórico mide cero cuadras

**Av. Boyacá y Av. Carabobo son la misma avenida**, renombrada al cruzar Rivadavia. Yo definí Z23 como *"Av. Rivadavia entre Boyacá y Av. Carabobo"* — que es un punto, no un tramo.

La fuente que tenía decía otra cosa y la leí mal. La Nación describe el corredor comercial **"entre Carabobo y Nazca"**, que sí es un tramo real.

**Perímetro corregido: Av. Rivadavia entre Av. Carabobo/Boyacá y Av. Nazca**, con ensanche en Plaza Flores.

Y esto no cambia el veredicto de Z23, que sigue en PENDIENTE por otro motivo: su único hito vivo, La Farmacia, cae ocho cuadras al sur del corredor, y la densidad del eje es textil —la indumentaria es el 50 % de los locales.

### 3 · El Puentecito no cerró, y la alarma también fue mía

Leí *"acaba de perder su pieza más visible"* junto a la descripción de El Puentecito y asumí que hablaba de él. **Hablaba de Los Laureles**, el Bar Notable de Av. Iriarte 2290. Están a **1,5 kilómetros** uno del otro.

**El Puentecito, Vieytes 1895, está probablemente abierto**, listado el 7 de julio de 2026 entre los 16 Restaurantes Icónicos, y con una reseña de servicio real del 4 de mayo que se quedó **a cinco días** de la ventana de verificación.

Y trae una tensión documental que hay que registrar en la ficha: **el "1750" es del GCBA y no tiene respaldo en prensa.** Todas las notas hablan de unos 150 años, o sea origen alrededor de 1876 como restaurante. Y `cronista.com` publica dos notas mutuamente contradictorias sobre el mismo local: "hace 150 años" y "hace 200 años".

**Recomiendo consignar 1750 como *sitio* —pulpería y posta de carretas— y ~1876 como *establecimiento gastronómico*, atribuyendo cada cifra a su fuente.** El Atlas no tiene que elegir entre las dos: tiene que decir de dónde sale cada una.

### 4 · Yiyo el Zeneize está tipado como mercado y no lo es

El repositorio lo detectó y no lo tocó, con razón: **es la única vía C de las 94 que no se apoya en un mercado oficial.**

Yiyo el Zeneize es un **bodegón**, y su reconocimiento es la **Ley CABA 6.533**, que declara patrimonio su *carta gastronómica* — no el local como mercado. Tiparlo como Mercado/patio le da a su zona una vía C que no existe.

**Recomiendo retiparlo como restaurante/bodegón con `registro_oficial = ley_especifica`**, y que la zona pierda esa vía C.

---

## Y ahora el problema grande: la ampliación de R19 se comió dos tercios de Chacarita

**R09 ∩ R19 = 60,4 hectáreas, el 64 % de Chacarita.** Es el mayor de los seis solapes nuevos que produjo la ampliación.

### Por qué pasó, y es honesto decirlo

**La decisión 6 era internamente inconsistente con la existencia de R09, y nadie lo vio hasta que corrió la geometría.**

R19 se amplió porque el reconocimiento externo recae sobre Fraga, Dorrego, Charlone y Jorge Newbery en vez de sobre Av. Federico Lacroze. Pero **esas calles están en Chacarita**. Ampliar R19 hacia ellas necesariamente absorbe R09. La ampliación hizo exactamente lo que se le pidió, y el resultado es aritméticamente incompatible con que R09 exista aparte.

Y el crecimiento no fue menor: **+347 locales, +187,6 %.** R19 casi triplicó.

### Lo que dice la prensa, que es la clave

Canal 26, marzo de 2026: *"en el borde indefinido entre Colegiales y Chacarita nació **Chacagiales**, un corredor urbano donde la historia ferroviaria, los viejos talleres y las calles arboladas conviven con uno de los booms gastronómicos más vibrantes de Buenos Aires"*.

Time Out, junio de 2026, nombra **"el eje Chacarita–Colegiales"**. The New York Times, en 2024, escribe sobre Chacarita.

**La prensa trata esto como un solo objeto, y dice explícitamente que el borde es indefinido.** Nosotros tenemos cuatro zonas encima: R09, R19, Z43 Colegiales y el extremo sur de Z44 Villa Ortúzar.

### Las tres salidas

**A · Fusionar R09 y R19 en un polo con subzonas.**
Es lo que hace la prensa. Y no es tan redefinición como parece: la familia que el propio clustering le puso a R09 fue **"dispersa"** —o sea, no le encontró forma— y a R19 **"eje"**. La definición del proyecto ya provee la figura que falta: **sistema de subpolos**. El polo fusionado *contiene* a los dos, así que **no viola la regla de que las 22 solo se amplían**: no se pierde nada. Z43 Colegiales pasaría a ser una subzona, porque su evidencia —Chacagiales— es literalmente la misma.

**B · Revertir parte de la ampliación** y dejar Fraga y Dorrego en R09, ampliando R09 en su lugar. R19 se queda con el eje Lacroze, que es lo que su nombre dice. Contradice el fundamento de la decisión 6, pero conserva las dos referencias separadas.

**C · Aceptar el solape y publicarlo como tal.** Dos polos reclamando los mismos locales. Rompe la regla de no contar repetido para cualquier agregado, y es la peor de las tres.

**Recomiendo A.** Es la que responde a la evidencia, la que la definición contempla, y la única que no obliga a elegir entre lo que dice la prensa y lo que dice el instrumento.

Los hitos del corredor quedarían todos bajo un mismo polo, que es donde la prensa los pone: Bar Conde (Lacroze 3193), Museo Fotográfico Simik (Lacroze 3901), Ocho Esquinas (Av. Forest 1186), el Mercado de Pulgas (Gral. E. Martínez 50) y el Polo Concepción.

**Y Z44 Villa Ortúzar queda afuera**, porque su núcleo es Plaza 25 de Agosto y solo su extremo sur toca el corredor. La Mezzetta ya está adjudicada ahí por USIG.

---

## El otro pendiente que dejó la geometría: la cola de R20

**Revisar el corte de R20 deja 24,7 hectáreas de lo publicado fuera del tramo que la decisión describe**, y la regla de contención las conserva.

O sea que R20 queda siendo el boulevard de García del Río entre Cabildo y Balbín **más una cola de 24,7 ha que la evidencia documental no cubre**.

**Recomiendo conservarla —la regla de que las 22 solo se amplían es más importante que la prolijidad— y declararla explícitamente en la ficha** como superficie publicada en la versión anterior que la evidencia documental actual no alcanza. Es incómodo y es verdad.

---

## Una nota técnica que vale guardar

El repositorio verificó la contención de los polígonos ampliados **por superficie perdida, 0,0 m² en las cuatro**, y no por predicado, porque **`covers()` de GEOS devuelve NO sobre geometrías cuya diferencia es exactamente cero.**

Es una trampa de biblioteca, no de datos, y si no la hubiera visto habríamos concluido que las ampliaciones no contenían a los polígonos originales cuando sí los contienen. Vale que quede escrito en la edición técnica junto a las trampas de fuente.

---

## Sí, aplicá los cinco veredictos

El Federal, Los 36 Billares, Café Tortoni, Café de los Angelitos y Varela Varelita.

**Dos son de Monserrat, así que su vía B se está midiendo con ellos en `sin_verificar` cuando están verificados a 17, 34 y 73 días.** Ninguna decisión los excluía; simplemente no estaban nombrados. Van.

---

## Y sobre Places: falta un dato que solo tenés vos

El runner está listo, con `vigencia_fecha_consulta` obligatoria y la asimetría codificada, pero exige `--precio-confirmado`. **El repositorio no puede leer tu consola de facturación, y la tarifa que circula está anotada como no confirmada en el propio repo.**

Es un número y una corrida. Con eso se cierran los 58 hitos del catálogo que nunca fueron mirados, incluidos los tres tests de calibración —Plaza Bar a nueve años, La Buena Medida a nueve meses, The New Brighton a cinco— que nos van a decir dónde está el corte de detección de la herramienta.
