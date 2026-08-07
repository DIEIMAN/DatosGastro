# Places no se descartó: dejó de ser la herramienta del problema

*7 de agosto de 2026 · a propósito de la pregunta de Diego*

La pregunta era si dejamos de usar Google Places, y si fue por falta de rigor. **No, y no.** Vale la pena escribirlo porque la respuesta cambia lo que hay que hacer ahora.

---

## Por qué el contador viene en cero

El repositorio informa "Places: 0 requests" en cada corrida desde hace varias rondas. La razón no es una decisión de descartarlo: es que **las últimas rondas fueron trabajo documental que Places no puede contestar.**

- La **vía E** es reconocimiento editorial externo: si La Nación o Time Out trataron a una zona como destino. Places no tiene prensa.
- La **vía B** es trayectoria e instituciones: Bares Notables, leyes, catalogaciones de la CPPHC, pizzerías emblemáticas. Places no tiene normas.
- La **vía D** son enclaves de colectividad con delimitación textual. Places no tiene delimitaciones.
- La **grilla de seis vías** sobre 46 zonas es lectura de fuentes.

Places es fuerte donde nosotros no estábamos trabajando: **conteo, ubicación y estado de locales**. Las vías A, C y F, que son las cuantitativas, ya las corrió el repositorio con la base propia.

Así que el cero no es un juicio sobre la herramienta. Es que durante seis rondas el problema fue otro.

---

## Y ahora es exactamente la herramienta que falta

El cuello de botella se mudó a la vigencia, y ahí Places es lo que estábamos necesitando sin decirlo.

De los **quince establecimientos** verificados en las dos rondas, **ninguno llegó a `verificado_abierto`**. Cuatro quedaron `probablemente_abierto`, ocho `dudoso`, dos `cerrado`, uno `en_disputa`. No fue por falta de esfuerzo: se hicieron entre cinco y siete rutas de búsqueda por establecimiento.

**Fue porque Instagram, Facebook, TikTok y Yelp bloquean el acceso automatizado, y ahí estaba la prueba.** En Los Laureles, en Iberia, en La Farmacia, en Saint Moritz, en Florida Garden: la pieza que cerraba el veredicto era un posteo fechado que no se pudo leer.

Places tiene, en un solo campo, lo que estuvimos persiguiendo por cinco rutas:

- **`business_status`** — `OPERATIONAL`, `CLOSED_TEMPORARILY`, `CLOSED_PERMANENTLY`.
- **Horarios declarados**, que además permiten detectar retracción — el caso de El Buzón, que sigue abierto pero perdió la noche y el fin de semana.
- **Fecha de las reseñas más recientes**, que es exactamente el nivel v3 de nuestra escala.

---

## La parte honesta: dónde falla Places

No es infalible, y conviene saber cómo se equivoca antes de usarlo.

**Places es lento con los cambios recientes.** El estado lo mantienen el comerciante y los usuarios, así que un cierre de hace cinco días probablemente todavía no figure. **Los Laureles cerró en julio y Places casi seguro lo sigue dando operativo.**

**Places es bueno con la decadencia lenta.** Un local cerrado hace años acumula reseñas que lo dicen, deja de tener horarios y termina marcado. **El Plaza Bar —cerrado desde abril de 2017, con el hotel demolido en parte y en obra hasta 2028— es justo el caso que Places detecta y el catálogo oficial no detectó en siete años.**

Y ahí está el argumento, que es mejor que "usemos las dos cosas porque sí:

> **La prensa y Places fallan en direcciones opuestas.** La prensa ve el cierre reciente y es ciega a la decadencia lenta: por eso el Plaza Bar sobrevivió siete años en el catálogo sin que nadie lo notara. Places ve la decadencia lenta y es ciego al cierre reciente: por eso no habría visto lo de Los Laureles. **Cruzarlas no suma cobertura: cubre el punto ciego de cada una.**

Eso es independencia de fuentes en el sentido fuerte de la regla, no dos fuentes que dicen lo mismo.

---

## Cómo entra sin romper la decisión de publicación

La regla vigente es que los datos de Places se publican solo a nivel **agregado**: no salen puntos, ni `place_id`, ni nombres.

**Para vigencia la regla se cumple sin esfuerzo**, y conviene decir por qué:

- Los establecimientos que verificamos **no vienen de Places**. Vienen del catálogo oficial de Bares Notables, del listado de pizzerías emblemáticas de APyCE, de la CPPHC. Son públicos y normativos.
- Lo que Places aporta es **un estado sobre un local que ya teníamos**: abierto, cerrado, temporalmente cerrado, y la fecha de la reseña más nueva.
- **Lo que se publica es nuestro campo `vigencia_verificada`, no el registro de Places.** El Atlas no dice "según Google, este bar está abierto". Dice que el bar está abierto, y la trazabilidad de esa afirmación vive en el repositorio.

Propongo agregar un nivel a la escala de vigencia, con su lugar propio:

| nivel | qué es |
|---|---|
| v1 | Nota de prensa con reporteo propio, últimos 90 días |
| v2 | Publicación fechada en canal propio, últimos 60 días |
| **v2b** | **`business_status` de Places, con fecha de consulta registrada** |
| v3 | Reseña de usuario con fecha visible, últimos 90 días |
| v4 | Listado o guía fechada, últimos 180 días |
| v5 | Cobertura de un evento concreto con fecha |

**`v2b` acredita `cerrado` con más fuerza que `abierto`.** Un `CLOSED_PERMANENTLY` es una afirmación positiva y difícil de producir por error. Un `OPERATIONAL` solo dice que nadie reportó lo contrario, que es más débil. Esa asimetría hay que respetarla: **Places para descartar, la prensa y los canales propios para confirmar.**

Y una precaución que ya nos costó cara con otras fuentes: **registrar la fecha de consulta**. Places no la trae; si no la anotamos nosotros, en seis meses tendremos un campo sin saber de cuándo es, que es exactamente el problema de El Cronista y su re-sellado de septiembre de 2025.

---

## Dos cosas que Places también resuelve, de paso

**Las discrepancias de dirección.** Tenemos cinco sin resolver: Marte en Crisólogo Larralde 277 o 2772, El Símbolo en Corrientes 3787 o 3797, La Media Costilla en Bahía Blanca 2300 o Arregui 4000, Palitos en Arribeños 2245 o 2241, El Sol de Galicia en Luis Viale 2867 o 2881. Places devuelve la dirección formateada del local, y en varias de esas la discrepancia se cae sola.

**Los nombres que no coinciden con el catálogo.** Esta ronda lo mostró: **"Bar Bar O" es la grafía estilizada de Bárbaro**, y buscarlo por el nombre del catálogo no devolvía nada. Probablemente por eso llevaba tanto tiempo en `dudoso`. Places busca por nombre y ubicación a la vez, así que ese tipo de bloqueo por nomenclatura desaparece.

---

## Lo que hace falta decidir

Nada de esto se puede hacer desde acá: Places lo corre el repositorio. Lo que hace falta es la autorización explícita para gastar requests en vigencia, y una estimación de costo antes de gastarlos.

Son **220 hitos**. Un `Place Details` por hito, con los campos mínimos —`business_status`, `formatted_address`, `opening_hours`— es una consulta por establecimiento y una sola pasada. Es la clase de gasto que la regla de estimar antes de gastar pide justificar, y acá se justifica solo: es la única vía que mueve ocho fichas de `dudoso` a un estado con evidencia, sin depender de que un medio barrial se acuerde de escribir sobre un bar.

---

## El número, para autorizar antes de gastar (ronda 5, 2026-08-07)

**0 requests ejecutados. Esto es una estimación de costo, no una corrida.** Guardrail 6: no se
ejecutan llamadas pagas sin autorización explícita de Diego.

### Por qué el costo depende de qué campo se pide

La API de Places (New) de Google cobra por **SKU de campos**, no por request plano: cuanto más
"caro" el campo pedido, más cara la consulta completa que lo incluye. De los tres campos mínimos
que pide la tarea:

| campo | SKU aproximado | por qué |
|---|---|---|
| `business_status` | Basic Data (SKU más barato) | dato de bajo costo, similar a `formatted_address` |
| `formatted_address` | Basic Data | igual |
| `opening_hours` | Preferred Data (SKU más caro, uno o dos escalones arriba de Basic) | Google lo tarifica junto a horarios/reseñas/rating, no junto al domicilio |

Como la consulta pide los tres juntos, **paga el SKU más caro de los tres que se piden**: el
costo de la corrida completa es el de "Place Details con datos Preferred", no el de Basic.

### La cifra, con la salvedad que corresponde

**No tengo una cotización en vivo del panel de Google Cloud para este proyecto: el número que
sigue es de la lista de precios pública tal como la conozco, no verificada hoy.** Antes de
autorizar gasto real, hay que confirmarla contra `console.cloud.google.com` → Maps Platform →
Billing, porque Google cambia estas tarifas sin previo aviso y porque el proyecto puede tener un
descuento, un crédito mensual o un tier distinto. Con esa salvedad, el orden de magnitud público
para Place Details con campos de nivel Preferred (que es el que fija el costo por incluir
`opening_hours`) ronda **entre USD 0,017 y USD 0,032 por solicitud** (USD 17–32 cada 1.000),
según el tramo de volumen mensual acumulado del proyecto.

| conjunto | hitos | costo estimado (USD 0,017/req) | costo estimado (USD 0,032/req) |
|---|---|---|---|
| **Subconjunto tandas A + B** (prioridad de verificación, ronda 4) | 29 | **USD 0,49** | **USD 0,93** |
| **Capa completa de hitos** | 220 | **USD 3,74** | **USD 7,04** |

En ambos casos el gasto es trivial en términos absolutos — el problema no es el dinero, es que
sigue siendo un llamado a una plataforma privada que requiere autorización explícita (guardrail
6) y que Google Cloud puede tener un crédito mensual gratuito que cubra la corrida completa sin
gasto neto: eso también hay que chequearlo en el panel de facturación antes de correr, no
suponerlo.

### La recomendación de secuencia

**No correr las 220 de una.** Correr primero el subconjunto de 29 (tandas A+B, ya priorizadas en
`prioridad_verificacion_filas.csv` de la ronda 4): es el 13 % del universo y toca el 50 % de las
filas con hitos. Si el subconjunto confirma que Places mueve fichas de `dudoso`/`sin_verificar` a
un estado con evidencia — que es la apuesta de este documento —, se autoriza el resto con el
patrón ya probado. Si no las mueve, se frena ahí y se ahorra el 87 % del gasto y del volumen de
llamadas a una plataforma externa.

### Registrar siempre la fecha de consulta

Places no devuelve cuándo se generó el estado de `business_status`: lo único fechable es el
momento en que **nosotros** lo consultamos. Sin ese campo, en seis meses `v2b` es un dato sin
saber de cuándo es — exactamente el problema que ya costó caro con El Cronista y su re-sellado
(FD-01, ronda 4). Cada consulta debe guardar `fecha_consulta_places` junto al valor devuelto, no
en una nota aparte.
