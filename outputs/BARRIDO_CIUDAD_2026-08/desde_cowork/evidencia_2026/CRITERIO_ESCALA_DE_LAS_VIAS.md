# Tres vías se miden sobre la zona y tres sobre la geometría

*Decisión de criterio · 7 de agosto de 2026 · a propósito del hallazgo de Café Olimpo y Almagro*

El repositorio cargó las dos verificaciones y agregó una advertencia de escala que parece menor y no lo es:

> Ninguno de los dos hitos cae dentro de ninguna de las 94 filas ni de las 22 envolventes, así que la vía B medida no se mueve. `PGR_P020` y `PGR_P083` siguen en `sin_hitos`. Almagro barrio son 405 ha; `PGR_P083` son 5,7 ha, y ninguno de sus cinco Notables está adentro.

**Eso explica el número que nos vino molestando todo el día.** La vía B está en 7 filas confirmadas de 94, y no es porque los bares estén cerrados: es porque **los polígonos son demasiado chicos para contenerlos**.

---

## El tamaño del problema, en un solo caso

Almagro es la única zona del Atlas que abre las seis vías. Tiene **cinco Bares Notables**, cuatro de ellos verificados abiertos esta semana:

| establecimiento | dirección |
|---|---|
| El Banderín | Guardia Vieja 3601 |
| El Boliche de Roberto | Bulnes 331 |
| El Símbolo | Av. Corrientes 3787 |
| La Orquídea | Av. Corrientes 4101 |
| Las Violetas | Av. Rivadavia 3899 |

Están repartidos sobre tres ejes distintos —Guardia Vieja, Corrientes y Rivadavia— a lo largo de un barrio de **405 hectáreas**.

`PGR_P083 · Almagro`, el fragmento que el clustering produjo ahí, mide **5,7 hectáreas**. El **1,4 % del barrio**.

**Por supuesto que no contiene ninguno de los cinco.** No podría. Y el resultado es que la fila queda registrada como `sin_hitos` — es decir, como si Almagro no tuviera trayectoria.

Lo mismo con Café Olimpo: aun corrigiendo el barrio, queda a **1.532 metros** del polígono `PGR_P020`.

---

## Lo que la medición está midiendo

Cuando se pregunta *"¿este polígono de 5,7 hectáreas contiene un Bar Notable?"*, no se está midiendo la trayectoria de la zona. Se está midiendo **si el clustering acertó a caer encima de un bar**.

Y esa es una pregunta distinta, cuya respuesta depende de dónde cortó un algoritmo, no de la historia gastronómica del lugar.

Es exactamente el mismo error que estuve a punto de cometer con la vía E, y por suerte se detectó antes: iba a salir a buscarle prensa a `PGR_P058 · Flores`, un polígono de 53 locales sin nombre. Nadie escribe sobre eso. **La vía E se mide por zona y las filas la heredan.**

**La vía B tiene el mismo problema y necesita la misma solución.** Y la vía D también — de hecho ya lo mostró: cuando se corrigió el eje de Liniers, la vía D de las 94 bajó de 12 a 10, porque el enclave inflado tocaba fragmentos que no le correspondían.

---

## La regla

**Las seis vías se dividen en dos familias, y no se miden igual.**

### Vías geométricas · se miden sobre el polígono

| vía | qué mide | por qué es del fragmento |
|---|---|---|
| **A** · densidad y continuidad | locales por hectárea, continuidad a 20/40/60/80/120 m | es una propiedad de la nube de puntos que el polígono contiene |
| **C** · mercados y centralidades | contiene un mercado, un patio, una galería | es contención espacial pura |
| **F** · corredor | elongación, ancho, largo, fracción en banda | es una propiedad de la forma del polígono |

Estas tres **se miden fila por fila** y están bien como están.

### Vías documentales · se miden sobre la zona y se heredan

| vía | qué mide | por qué es de la zona |
|---|---|---|
| **B** · trayectoria e instituciones | Bares Notables, Restaurantes Icónicos, pizzerías emblemáticas, protección patrimonial | un bar de 1893 pertenece a un barrio y a una identidad, no a un blob de 5,7 ha |
| **D** · comunidades y especialización | enclaves de colectividad, especialización de rubro | un enclave tiene delimitación textual propia, que no coincide con la del clustering |
| **E** · reconocimiento externo | prensa, guías, food tours que tratan a la zona como destino | nadie escribe sobre un fragmento sin nombre |

Estas tres **se miden a nivel de zona** y las filas las heredan, con el mismo esquema que ya está implementado para la vía E:

`zona_via_X` + `via_X_modo` ∈ {`propia`, `heredada`, `requiere_cruce`}

Y guardadas **como referencia, no como valor copiado** — si mañana se vuelve a correr el clustering, las filas rompen visiblemente en vez de quedar con un valor huérfano.

---

## Lo que cambia, y lo que no

**No cambia ninguna medición geométrica.** A, C y F siguen exactamente igual.

**No se afloja ningún criterio.** Un Bar Notable sigue teniendo que existir, estar verificado y pertenecer a la zona. Lo único que se corrige es **a qué objeto se le atribuye**.

**Sí cambia el número de la vía B**, y bastante. Hoy está en 7 de 94 porque se pregunta por contención espacial. Medida por zona, Almagro pasa a tener sus cinco, Monserrat sus nueve, Retiro sus cuatro, Mataderos sus tres. **Y las 48 filas que hoy están en `sin_hitos` van a repartirse entre "la zona no tiene hitos" y "la zona sí tiene, el fragmento no" — que son dos cosas completamente distintas y hoy se cuentan igual.**

**Y hay un beneficio que no es menor: se puede publicar.** Con la vía B medida por contención, el Atlas no puede decir que Almagro tiene trayectoria, porque su propia matriz dice que no. Medida por zona, puede decirlo y respaldarlo con cinco direcciones.

---

## Una salvedad, para que no se use de más

**La herencia no vale hacia arriba.** Que Almagro tenga cinco Notables no convierte a `PGR_P083` en un polo notable: lo convierte en **un fragmento de una zona que tiene cinco Notables**. La ficha tiene que decir eso, no otra cosa.

Y para las zonas que se publiquen como polo único, la distinción se disuelve sola: si el polígono final de Almagro cubre el barrio o el conjunto de sus ejes, los cinco quedan adentro y la contención vuelve a funcionar. **La regla es una muleta para el período en que la geometría está congelada, y un criterio permanente para las filas que sigan siendo fragmentos.**

---

## Por qué esto además prueba las decisiones de ampliación

El caso de Almagro es el argumento más fuerte que apareció hasta ahora para las decisiones 5 a 8 —R18, R19, R20 y R21—, que Diego acaba de aprobar.

Si un fragmento del 1,4 % de un barrio no contiene ninguno de sus cinco Bares Notables, entonces **el desajuste entre lo que la prensa describe y lo que el polígono encierra no es una anomalía de tres o cuatro referencias: es la forma normal del problema.** R19 mide Lacroze cuando la prensa habla de Fraga y Dorrego; R21 mide San Martín y Warnes cuando el circuito está en Beláustegui y Rojas. Son el mismo fenómeno que Almagro, visto desde el otro lado.

Y le da contenido concreto a la advertencia que Diego hizo hace varias rondas: los polos de la V2 están curados, tienen mediana de 130 hectáreas, y los del borrador tienen 13. **Un objeto de 13 hectáreas no puede contener la historia de un barrio.**
