# La capa de memoria — y la trampa de los homónimos

*7 de agosto de 2026*

Datos en `capa_de_memoria.csv` (31 entradas) y `homonimos_vivo_muerto.csv` (7 pares).

La decisión de trayectoria versus actividad dejó establecido que **la vía B se abre por presencia y la trayectoria extinguida se publica pero no abre**. Faltaba construir el objeto que se publica. Esto es ese objeto.

---

## No son dos estados, son cuatro

Al armarla apareció que "abierto" y "cerrado" no alcanzan:

| estado | qué es | ejemplos |
|---|---|---|
| **`extinguido`** | cerró y no volvió | La Blanqueada (215 años), The New Brighton, La Buena Medida, las cantinas de Necochea |
| **`extinguido con reapertura anunciada`** | cerró, se conserva y hay obra en curso | **Plaza Bar**, con el grill y el bar rescatados y reapertura para 2028 |
| **`mutado`** | el local sigue vivo, cambia lo que es | La Perla del Once → pizzería La Americana · Confitería del Molino → visita guiada · Café Palacio → Museo Fotográfico Simik |
| **`interrumpido y recuperado`** | cerró y volvió; **no va en esta capa** | El Tokio, Bar Iberia, Todos Contentos, Clásica y Moderna, Café Thibon, Casa Burgio, Los Laureles |

**La mutación es el estado que no habíamos nombrado y es el que más se malinterpreta.** Rivadavia 2800 sigue siendo gastronomía —hay una pizzería— pero ya no es La Perla. Y la Confitería del Molino está viva como edificio y en uso, con visitas guiadas, mientras su función gastronómica no existe. **Circula en material de difusión como si fuera oferta**, y esa es exactamente la clase de error que esta capa evita.

---

## La trampa: siete pares de nombres compartidos, y tres ya nos mordieron

Este es el hallazgo que no esperaba. **La capa de memoria y la capa viva comparten nombres**, y ese es el mecanismo por el que un bar muerto se publica como vivo — o al revés.

**Hay cuatro "Perla" en el Atlas.** La de Caminito está viva y es la única del catálogo. La del Once cerró en 2017 y hoy es una pizzería. En Flores hubo un almacén La Perla en Rivadavia 6900 y una Confitería La Perla de Flores frente a la plaza, las dos extinguidas.

**Y tres de estos pares ya produjeron un error concreto:**

**El Coleccionista.** Yo lo tenía en la capa extinguida de Flores, a partir de una fuente de 2012 sobre un bar de los años 30 llamado "El Cóndor". **Es un Bar Notable vivo de Caballito, Av. Rivadavia 4929, entrada 44 del consolidado.** Son dos locales homónimos y yo mezclé uno con otro.

**Café Roma y Roma del Abasto.** El repositorio encontró la fila "Café Roma" con una dirección **inventada** fusionada —"San Luis 3101"— y las coordenadas reasignadas. Son dos Bares Notables vivos en dos barrios distintos: Olavarría 409 en La Boca y Anchorena 806 en Balvanera. **La dirección falsa era mía.**

**"Bar Bar O".** Buscarlo por la grafía del catálogo no devolvía nada, y probablemente por eso estuvo tanto tiempo en dudoso. Es Bárbaro.

Y uno detectado a tiempo: **Paulín**. Hay un Bar Notable vivo en Sarmiento 635, San Nicolás, y un Café Paulín extinguido en Av. San Martín, Floresta, donde se iniciaron los hermanos Fresedo. La fuente de Floresta lo nombra **sin dirección**, que es justamente lo que facilita la confusión.

**La regla que sale de esto: en la capa de memoria, un establecimiento sin dirección no se carga.** Y todo nombre que aparezca en las dos capas lleva marca explícita de par.

---

## Lo que la capa explica, zona por zona

No es un anexo nostálgico. **Cada entrada explica la forma de un polo hoy.**

**Flores casco histórico.** Siete establecimientos extinguidos sobre Rivadavia y Yerbal —Londres, La Perla, El Guipuzcoano, La Perla de Flores, Las Orquídeas, el Palacio de los Billares, La Cosechera— y **un solo hito vivo, La Farmacia, que además cae ocho cuadras fuera del polígono**. Esa capa *es* la ficha de Flores casco histórico: explica por qué la zona tiene memoria y no tiene vía B.

**Costanera Norte.** Cinco cerrados y uno **demolido** contra dos hitos vivos. **La zona perdió más de lo que conserva**, y eso explica por qué su vía E quedó a un solo grupo del umbral y no abrió.

**Av. Sáenz.** La Blanqueada funcionó **desde 1802** —215 años— y cerró en 2017. Es el establecimiento gastronómico más antiguo documentado de la Ciudad y **nunca llegó a ser declarado Bar Notable**. Explica por qué el eje no se sostiene solo hoy.

**La Boca · Necochea.** *"Hoy, ninguna sobrevive"* es la frase de la fuente sobre las cantinas. Cierra la vía A con evidencia en contra y explica la zona entera: Necochea entra por trayectoria y por proyecto, no por oferta.

**Puerto Madero.** Los dos cierres los registra **la propia nota que sostiene su vía E**, y esa nota es de 2023. La zona no tiene una sola pieza de nivel zona posterior.

**Retiro.** El Mercado de los Carruajes cierra la vía C **por cierre efectivo, no por falta de búsqueda**. Y es el caso que probó el re-sellado de El Cronista: su nota, "actualizada" al 24 de septiembre de 2025, seguía recomendando dos restaurantes adentro de un mercado cerrado cinco meses antes.

---

## Y una lectura que solo se ve con la capa completa

**De las cinco entradas de más de noventa años, cuatro cerraron por el alquiler o por el cierre de su contenedor, y ninguna por falta de clientes.**

La Buena Medida: *"falta de renovación del alquiler e imposibilidad de afrontar los costos"*. El Palacio de la Papa Frita: *"alquiler dolarizado que se duplicó a la renovación"*, con las persianas colocadas un lunes a la una de la madrugada y el personal enterándose el martes. La Confitería del Hotel Castelar y el Plaza Bar: cerró el edificio que los alojaba, no ellos.

**El mecanismo del cierre en esta ciudad es inmobiliario, no gastronómico.** Y eso tiene una consecuencia para el Atlas que conviene escribir: **un polo puede estar sano y perder su ancla igual.** Es exactamente lo que le pasó a P008 Barracas, y lo que le puede pasar mañana a la Esquina Homero Manzi, que está en riesgo no por vacío de público sino por una condena laboral de 220 millones.

---

## Cómo se publica

**No como lista de bares perdidos.** Como **el campo `via_B_soporte = extinguido` de cada zona**, con la capa detrás.

En la ficha, una línea: *"la zona conserva N hitos activos y registra M extinguidos"*, y el detalle en el anexo de datos. Así el Atlas puede decir que Flores tiene trayectoria **y** que hoy no la sostiene, que son dos cosas verdaderas al mismo tiempo y que hoy el instrumento no puede decir juntas.

Y hay un uso que a Patricia le sirve directo: **"qué se perdió" es una historia con nombres, direcciones y años.** Un bar de 1802 en Av. Sáenz, un restaurante de 1952 en Corrientes que cerró de madrugada, las cantinas de Necochea de las que ninguna sobrevive. Eso entra en una lámina y no necesita explicación metodológica.

---

## Lo que falta

**Diecisiete de las treinta y una entradas tienen confianza media o baja**, casi todas de la capa de Flores: vienen de una sola fuente de 2012 que ya entonces daba por sobreviviente a uno solo. No tienen año de cierre, ni causa, ni qué hay hoy en esa dirección.

Eso está bien para publicar la capa como memoria —lo que se afirma es que existieron, y eso la fuente lo sostiene— pero **no alcanza para afirmar cuándo cerraron**. La ficha tiene que decir "documentados hacia 2012 como ya inactivos", no inventar fechas.

Y queda una verificación puntual que vale por sí sola: **El Puentecito, Vieytes 1895**, el restaurante más antiguo de Buenos Aires en funcionamiento en su emplazamiento original, con origen en **1750**. La ronda del sur registró que su zona "acaba de perder su pieza más visible" justo al describirlo. **Si cerró, es la entrada más importante de esta capa y todavía no está.**
