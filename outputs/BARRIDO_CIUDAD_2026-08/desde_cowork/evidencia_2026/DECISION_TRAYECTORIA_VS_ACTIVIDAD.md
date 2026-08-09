# Cuando el hito cierra, ¿se cierra la vía B?

*Decisión de criterio · 7 de agosto de 2026 · a propósito de P008 Barracas*

El repositorio cargó el campo de vigencia y **P008 Barracas dejó de abrir la vía B**: su único hito era Los Laureles, y Los Laureles cerró. La fila pasó de abrir a no abrir por un cambio de estado de un solo establecimiento.

Es la fila que justifica sola el campo. Y es también la que obliga a decidir algo que hasta ahora no estaba escrito.

---

## Primero, el hecho: Los Laureles no está confirmado

Antes del criterio, el dato. **El cierre de Los Laureles está en disputa entre dos medios nacionales del mismo día.**

- La Nación, 5 de agosto de 2026: *"El último adiós de Los Laureles: el bar notable de 133 años que marcó la vida de Barracas"*.
- Canal 26, 5 de agosto de 2026: *"Los Laureles no cierra: el histórico Bar Notable de Barracas seguirá vivo y ya anunció nueva milonga"*.
- El sitio de turismo del GCBA lo sigue publicando sin nota.

Tres fuentes, tres estados. **Ninguna de las tres alcanza para cerrar la fila.**

Y hay un precedente que muestra que el estado puede volver: **El Tokio**, Av. Álvarez Jonte 3550, Bar Notable de 1930, **cerró en 2023 y reabrió en 2025**. Los listados nunca registraron ni una cosa ni la otra.

**Decisión inmediata:** Los Laureles queda en `cerrado_en_disputa` y P008 no se cierra. Se marca `pendiente_de_verificacion`. Bajar la vía B de una fila sobre un cierre que un medio nacional desmiente el mismo día es exactamente el error que el campo de vigencia vino a evitar, cometido en la dirección contraria.

---

## Ahora el criterio, que es lo que falta

La pregunta de fondo: **¿una zona pierde su trayectoria cuando la institución que la sostenía cierra?**

Las dos respuestas obvias fallan.

**Si el cierre no cuenta**, publicamos un Atlas que certifica trayectoria con bares muertos. Es literalmente lo que hace hoy el circuito oficial del GCBA con Los Laureles, y es el problema que vinimos a arreglar.

**Si el cierre cierra la vía**, se cae media ciudad. El casco histórico de Flores tiene una capa entera extinguida —Londres en Rivadavia y Boyacá, La Perla en Rivadavia 6900, El Guipuzcoano en Yerbal 2502, La Perla de Flores frente a la plaza, Las Orquídeas, el Palacio de los Billares, La Cosechera—. La Blanqueada funcionó en Av. Sáenz y Rabanal **desde 1802** y cerró en 2017. The New Brighton, Sarmiento 645, quebró en marzo de 2026 tras más de un siglo. Si la trayectoria extinguida vale cero, el sur y el oeste de la Ciudad quedan sin historia gastronómica por decreto metodológico.

Las dos son falsas porque **confunden dos cosas que la definición mantiene separadas**. La definición dice que la identidad de un polo puede estar dada por *"su trayectoria histórica"* **y** por *"la presencia de mercados o instituciones emblemáticas"*. Son dos cláusulas, no una. La trayectoria es un hecho del pasado que no se revierte. La presencia es un hecho del presente que sí.

---

## La regla

**La vía B se abre por presencia, no por trayectoria. La trayectoria extinguida se registra y se publica, pero no abre la vía.**

Concretamente, se agrega un campo `via_B_soporte` con cinco valores:

| valor | qué significa | ¿abre la vía B? |
|---|---|---|
| `activo` | al menos un hito verificado abierto | **sí** |
| `mixto` | hay hitos activos y hitos extinguidos | **sí** |
| `extinguido` | hubo hitos, todos cerrados o demolidos | **no**, pero se publica la capa histórica |
| `en_disputa` | el estado del único hito está contradicho entre fuentes | **pendiente**, no se resuelve |
| `sin_verificar` | hay hitos cargados y nadie verificó su estado | **pendiente**, no se cuenta como abierta ni como cerrada |

`sin_verificar` no es un tecnicismo: hoy alguien miró **4 de 220 hitos**. Rellenar los otros 216 con `sí` sería afirmar 216 cosas que nadie comprobó. El repositorio ya tomó esa decisión y es la correcta; esto la formaliza.

**P008 Barracas queda hoy en `en_disputa`.** No en `extinguido`.

---

## Por qué esto no es un tecnicismo

Tres consecuencias que ya se ven en el material relevado.

**Una zona puede tener trayectoria extinguida y ser un polo igual, por otra vía.** Nueva Pompeya perdió La Blanqueada en 2017 y sigue abriendo la vía B por El Buzón (Esquiú 1393, de 1930) y El Globito (Av. Caseros 3159, de 1934). Lo que La Blanqueada explica es *por qué el eje de Av. Sáenz hoy no se sostiene solo*. Ese es el valor de registrar lo extinguido: no abre la vía, pero explica la forma del polo.

**Una zona puede perder la vía B y no perder nada más.** El casco histórico de Flores tiene la capa extinguida más grande de la Ciudad y su vía B real hoy es un solo establecimiento, La Farmacia (Av. Directorio 2400), que además cae fuera del polígono propuesto. Con la regla nueva, la ficha dice exactamente eso, que es la verdad, en vez de decir que Flores "tiene trayectoria" apoyándose en siete bares que no existen.

**Y hay un caso donde la regla se aplica al revés.** Casa Bogotá, Bogotá 3900, es una casona de 1914 declarada patrimonio histórico, reabierta como restaurante en 2025. La trayectoria es del **edificio**, no del negocio. `via_B_soporte = activo`, pero con la nota de que la continuidad gastronómica no existe: el restaurante tiene un año. El repositorio ya inventó la distinción correcta para Casa Burgio —`vigencia = sí` y `continuidad_ininterrumpida = no`— y este es el mismo caso. **Conviene usar los dos campos siempre juntos.**

---

## Lo mismo, para la vía D

El relevamiento de enclaves comunitarios trajo un problema idéntico, y la solución es la misma forma.

Hoy la vía D de una fila dice `abierta` o `cerrada`. Eso mezcla tres estados que no son lo mismo:

| valor | qué significa | ejemplo real |
|---|---|---|
| `abierta` | hay colectividad o especialización con oferta delimitable | Liniers, Mercado Andino |
| `medida_sin_enclave` | se buscó, hay comunidad, **no hay oferta comercial estable** | Barrio Charrúa: tres fuentes independientes, ninguna nombra un solo local. Tiene la Fiesta de la Virgen de Copacabana desde 1972, no tiene comercio |
| `no_medida` | falta la delimitación textual para poder cruzar | el Abasto, hasta hoy |

El repositorio ya señaló esto con precisión: el Abasto figuraba `cerrada` cuando lo honesto era `no lo medimos`. Tenía razón, y la corrección va más lejos de lo que él mismo pidió: **`medida_sin_enclave` no es lo mismo que `no_medida`, y ninguna de las dos es `cerrada`**. Charrúa está medido y el resultado es negativo, que es un hallazgo. El Abasto no estaba medido, que es una laguna. Registrarlos con la misma etiqueta borra la diferencia entre saber y no saber.

---

## Y una limitación del instrumento que hay que escribir en algún lado

El relevamiento de enclaves dejó tres resultados que no son ausencias sino **cegueras del método**:

- La presencia **senegalesa** en Once y Constitución es de venta ambulante. No produce establecimiento habilitado, así que no produce fachada, así que este instrumento no la ve.
- La colectividad **japonesa** se instaló por dispersión de rubro —tintorerías, floricultura— y nunca por concentración de cuadra.
- La **china fuera del Barrio Chino** está dispersa **por diseño**: el supermercado de barrio compite consigo mismo si se agrupa. La forma del negocio produce dispersión.

En los tres casos el Atlas va a decir "no hay enclave". Y en los tres casos lo correcto es: **este instrumento mide fachadas contiguas, y hay economías migrantes que no toman esa forma.**

Si no queda escrito, con el tiempo un "no medido" se lee como "no existe". Propongo que vaya en la edición técnica, en la parte de límites del método, con esas tres palabras: *el Atlas ve fachadas*.
