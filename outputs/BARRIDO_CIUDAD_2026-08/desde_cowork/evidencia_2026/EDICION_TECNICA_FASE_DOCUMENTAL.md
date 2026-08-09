# Edición técnica · Parte segunda · la fase documental

**Atlas de Referencias Gastronómicas de la Ciudad de Buenos Aires · Dirección General de
Desarrollo Gastronómico, GCBA**

*Versión de trabajo · 8 de agosto de 2026*

---

## Cómo se lee esto

Esto **continúa** `EDICION_TECNICA_METODO.md`, que tiene las secciones 0 a 26 y las Partes I a X.
Mismas convenciones, misma numeración: acá se empieza en la sección 27 y en la Parte XI. Las
referencias con `§` menores a 27 son a aquel documento.

El primero explica **cómo se construyeron los polígonos**: las fuentes, la deduplicación, HDBSCAN,
la grilla de sensibilidad, la ablación, las uniones y particiones. Este explica lo que vino después
y es de otra naturaleza: **cómo se decide si una zona es un polo, cómo se verifica que un
establecimiento sigue abierto, qué se hace con los que ya no están, y cómo se garantiza que nada se
cuente dos veces.**

Hay una razón para que sean dos documentos y no uno. El primero mide geometría y se corre. Este
mide **evidencia documental**, se lee, y por lo tanto falla distinto: sus errores no son de
parámetro sino de atribución, de fecha y de nombre. Las tres partes finales están dedicadas
justamente a eso.

Y hay una continuidad explícita que conviene señalar de entrada. La Parte X del primer documento
declaraba, entre sus límites:

> **No dice si un local está abierto.** Ninguna fuente confirma vigencia.

**La Parte XII de este documento es el intento de levantar ese límite**, y termina informando
cuánto se levantó y cuánto no.

Se mantiene la convención que gobierna todo: **«no encontramos» no es «no existe»**.

---

# Parte XI · El criterio de admisión

## 27 · Por qué un criterio de entrada y no un umbral

El barrido produjo 124 concentraciones. La pregunta que quedaba no era geométrica sino
**definicional**: cuáles de esas concentraciones —y cuáles de las zonas que el clustering no vio—
son un polo gastronómico.

Un umbral único no sirve, y se puede mostrar por qué con dos casos reales del Atlas:

- **Liniers** no tiene un solo Bar Notable. Cualquier criterio patrimonial lo deja afuera. Tiene un
  mercado con eje de 285 metros, una colectividad instalada desde mediados de los ochenta y prensa
  gastronómica extranjera.
- **Puerto Madero** tiene reconocimiento externo abundante y **perdió** dos de sus piezas, y los dos
  cierres los registra la misma nota que sostiene su reconocimiento.

Un umbral de densidad admite al segundo y rechaza al primero. Un umbral patrimonial hace lo
inverso. **Ninguno de los dos describe lo que la Dirección entiende por polo.**

La definición adoptada por el proyecto —una concentración espacial reconocible de establecimientos,
actividades o referentes gastronómicos que conforma una identidad territorial propia— **enumera
formas de conformarla, no una sola**. El criterio de admisión tenía que tener la misma estructura.

## 28 · Las seis vías

**Una zona entra por cualquiera de ellas.** No es una lista de requisitos: es una disyunción.

| vía | qué mide |
|---|---|
| **A** · densidad y continuidad | locales por hectárea y cuadras seguidas con oferta |
| **B** · trayectoria e instituciones | Bares Notables, Restaurantes Icónicos, pizzerías emblemáticas, protección patrimonial |
| **C** · mercados y centralidades | mercados en actividad, patios, galerías |
| **D** · comunidades y especialización | enclaves de colectividad con oferta propia, especialización de rubro |
| **E** · reconocimiento externo | prensa, guías y operadores que tratan a la zona como destino |
| **F** · corredor | la forma: eje y no núcleo |

La vía F merece una aclaración que se pidió más de una vez: **F no mide tamaño ni cantidad, mide
forma.** Un corredor de 800 metros con oferta continua y un núcleo compacto de la misma cantidad de
locales son dos objetos distintos y hay que poder decirlo. F es lo que permite que Av. Montes de Oca
y el entorno de Plaza Dorrego no se midan con la misma vara.

Y una zona que abre las seis existe: **Almagro**, con cinco Bares Notables sobre tres ejes, cuatro
locales en tres cuadras de Guardia Vieja y seis colectividades con oferta. Es el caso testigo del
documento entero y va a reaparecer en la sección siguiente por el motivo opuesto.

## 29 · Las dos familias, y el error que las separó

Ésta es la decisión de criterio más importante de la fase, y salió de un número que no cerraba.

**La vía B estaba abriendo en 7 filas de 94.** La lectura obvia era que los bares estaban cerrados o
sin verificar. Era falsa.

El repositorio lo detectó al cargar dos verificaciones —Café Olimpo y El Boliche de Roberto— y
observar que **ninguno de los dos hitos cae dentro de ninguna de las 94 filas ni de las 22
envolventes**. Café Olimpo queda a **1.532 metros** del polígono al que debía pertenecer.

El caso completo es Almagro:

| | |
|---|---|
| barrio de Almagro | **405 ha** |
| fragmento `PGR_P083 · Almagro` producido por el clustering | **5,7 ha** — el **1,4 %** del barrio |
| Bares Notables del barrio | **5** (El Banderín, El Boliche de Roberto, El Símbolo, La Orquídea, Las Violetas) |
| Bares Notables dentro del fragmento | **0** |

**Por supuesto que no contiene ninguno. No podría.** Están repartidos sobre Guardia Vieja,
Corrientes y Rivadavia, tres ejes distintos de un barrio de cuatro kilómetros cuadrados.

Y entonces lo que la medición estaba midiendo no era la trayectoria de la zona. Era **si el
clustering acertó a caer encima de un bar** — una pregunta cuya respuesta depende de dónde cortó un
algoritmo, no de la historia gastronómica del lugar.

**La regla que sale: las seis vías se dividen en dos familias y no se miden sobre el mismo objeto.**

### Vías geométricas · se miden sobre el polígono, fila por fila

| vía | por qué es del fragmento |
|---|---|
| **A** | es una propiedad de la nube de puntos que el polígono contiene |
| **C** | es contención espacial pura |
| **F** | es una propiedad de la forma del polígono |

**Ninguna medición geométrica cambia.** A, C y F siguen exactamente como estaban.

### Vías documentales · se miden sobre la zona y las filas las heredan

| vía | por qué es de la zona |
|---|---|
| **B** | un bar de 1893 pertenece a un barrio y a una identidad, no a un blob de 5,7 ha |
| **D** | un enclave tiene delimitación textual propia, que no coincide con la del clustering |
| **E** | nadie escribe sobre un fragmento sin nombre |

La vía E ya se venía midiendo así, y por un pelo: estuvo a punto de salir una búsqueda de prensa
para `PGR_P058 · Flores`, un polígono de 53 locales **sin nombre**. Nadie escribe sobre eso. Lo que
esta sección hace es extender a B y a D un criterio que E ya tenía, en vez de inventar uno nuevo.

**No se afloja ningún criterio.** Un Bar Notable sigue teniendo que existir, estar verificado y
pertenecer a la zona. Lo único que se corrige es **a qué objeto se le atribuye**.

### La salvedad, para que no se use de más

**La herencia no vale hacia arriba.** Que Almagro tenga cinco Notables no convierte a `PGR_P083` en
un polo notable: lo convierte en **un fragmento de una zona que tiene cinco Notables**. La ficha
tiene que decir eso y no otra cosa.

Para las zonas que se publiquen como polo único la distinción se disuelve sola: si el polígono final
cubre el barrio o el conjunto de sus ejes, los cinco quedan adentro y la contención vuelve a
funcionar. **La regla es una muleta mientras la geometría está congelada, y un criterio permanente
para las filas que sigan siendo fragmentos.**

## 30 · Cómo se implementa la herencia

Dos campos por vía documental:

```
zona_via_X          la zona sobre la que se midió
via_X_modo          ∈ { propia, heredada, requiere_cruce }
```

- **`propia`** — la fila *es* la zona sobre la que se midió.
- **`heredada`** — la fila es un fragmento de una zona medida, y toma su valor por referencia.
- **`requiere_cruce`** — todavía no se estableció a qué zona pertenece la fila. **No es un valor
  faltante: es un trabajo pendiente identificado.**

Y una restricción de implementación que no es cosmética: **se guarda la referencia, no el valor
copiado.** Si mañana se vuelve a correr el clustering y los fragmentos cambian, las filas rompen
visiblemente —apuntan a una zona que ya no las contiene— en vez de quedarse con un valor huérfano
que parece bueno. Es la misma familia de problema que **R8**: un dato heredado que sobrevive a la
desaparición de su origen falla en silencio.

## 31 · El resultado medido de la vía B

Misma capa de hitos, mismas 94 filas, único cambio: a qué objeto se le pregunta.

| vía B | por contención | por zona |
|---|---:|---:|
| **abre** | 16 | **33** |
| pendiente | 27 | 37 |
| no abre | 51 | 24 |

**La vía B se duplica cambiando solo el objeto de la pregunta.**

Y lo que más importa no es el número que sube sino el que se parte. De las **51** filas que la
medición por contención registraba como `sin_hitos` —es decir, como si la zona no tuviera
trayectoria— el reparto reportado es:

- **27** son *«la zona sí tiene, el fragmento no»*
- **23** son *«la zona tampoco tiene»*

**Veintisiete filas que parecían vacías no lo estaban.** Eso es exactamente lo que la medición
anterior no podía distinguir, y son dos cosas completamente distintas que se estaban contando igual.

> **Pendiente de reconciliación, declarado acá porque corresponde:** 27 + 23 = **50**, y las filas
> a repartir eran **51**. Falta clasificar una. No cambia ninguna conclusión, pero un conteo que no
> cierra se anota, no se redondea.

**Y hay un beneficio que no es de método sino de publicación.** Con la vía B medida por contención,
el Atlas no podía afirmar que Almagro tiene trayectoria, porque su propia matriz decía que no.
Medida por zona, puede afirmarlo y respaldarlo con cinco direcciones.

Lo mismo pasó del otro lado con la vía D, y sirve como control: al corregir el eje inflado del
enclave de Liniers —que tocaba fragmentos que no le correspondían— **la vía D de las 94 bajó de 12 a
10**. El criterio no sólo suma: también resta cuando la delimitación estaba mal.

## 32 · La escala de la vía E

El reconocimiento externo es la vía más fácil de inflar, porque casi toda zona tiene *alguna*
mención. La escala fija qué clase de mención es evidencia.

| nivel | qué es |
|---|---|
| **e1** | guía editorial internacional (Michelin, 50 Best, Gault&Millau) |
| **e2** | prensa nacional o extranjera de interés general que trata **a la zona** |
| **e3** | ranking con método declarado |
| **e4** | guía turística comercial |
| **e5** | food tour comercial |

**La vía E abre con dos grupos de independencia distintos entre e1 y e4, o con uno solo si es e1.
Un e5 solo no abre.**

Tres precisiones que se ganaron con casos:

**La comunicación del GCBA no cuenta.** Es parte interesada. Esto no es un juicio sobre su calidad:
una zona no puede acreditar reconocimiento externo con material producido por el organismo que la
está evaluando.

**Michelin distingue restaurantes, no barrios.** Una estrella en una dirección es un hito de
trayectoria — **vía B, no vía E**. Confundirlas convertiría cada restaurante distinguido en
reconocimiento territorial de su cuadra.

**Se cuentan grupos de independencia, no notas** (R6). Seis réplicas de prensa fueron descontadas en
la auditoría de duplicados; **sin ese filtro, Colegiales y Retiro habrían contado el doble de grupos
de los que tienen.**

Estado de cobertura: **94 de 94 filas asignadas** — 57 abren, 22 no abren, 10 en `requiere_cruce`, 4
pendientes y 1 marcada para revisión. Por modo: 25 `propia`, 58 `heredada`, 10 `requiere_cruce`.

## 33 · El estado de soporte de la vía B · seis valores

Que una zona *haya tenido* trayectoria y que la *tenga hoy* son dos afirmaciones distintas, y el
Atlas tiene que poder hacer las dos por separado. La decisión de fondo quedó así: **la vía B se abre
por presencia; la trayectoria extinguida se publica pero no abre.**

El campo que lo registra:

| `via_B_soporte` | qué significa |
|---|---|
| `activo` | los hitos que la sostienen están abiertos y verificados |
| `mixto` | conviven hitos activos y extinguidos |
| `extinguido` | la trayectoria está documentada y no la sostiene ningún hito vivo |
| `en_disputa` | fuentes que se contradicen y ninguna prevalece |
| `sin_verificar` | hay hitos y no se verificó su vigencia |
| `sin_hitos` | no se le conocen hitos a la zona *(agregado por el repositorio)* |

`sin_hitos` es el valor que hizo falta agregar cuando la medición pasó a hacerse por zona, y es el
que la sección 31 reparte en dos.

**Flores casco histórico es el caso que justifica todo el campo:** siete establecimientos extinguidos
documentados sobre Rivadavia y Yerbal, y **un solo hito vivo —La Farmacia— que además cae ocho
cuadras fuera del polígono**. Sin este campo el Atlas sólo puede decir una de las dos cosas
verdaderas sobre Flores. Con él puede decir las dos.

## 34 · Los cuatro estados de la vía D

La vía D fue la que más se prestó a confundir ausencia de dato con ausencia de fenómeno, así que
lleva estados explícitos en vez de un booleano:

| estado | qué afirma |
|---|---|
| `abierta` | hay enclave delimitado con oferta comercial propia |
| `medida_sin_enclave` | se midió y la comunidad existe **sin** oferta comercial concentrada |
| `no_medida` | no se buscó todavía |
| `no_medible_con_este_instrumento` | el fenómeno existe y este instrumento no lo alcanza |

`medida_sin_enclave` es el estado que más se usa y el que más informa: **de los enclaves
identificados, once son casos donde la comunidad existe y la oferta comercial no.** Eso es un dato,
no un hueco — y es exactamente la distinción que R7 exige.

## 35 · La prueba que falló, y por qué está publicada

Se planteó una hipótesis: que la densidad de puntos del padrón **ENTUR** correlacionara con la vía E,
sirviendo como proxy barato de reconocimiento externo.

Cumpliendo **R1**, la lectura se escribió antes de correr, con un rango predicho de correlación.

| | |
|---|---|
| resultado | **ρ = +0,252** |
| ¿cayó en el rango predicho? | **sí** |
| control de permutación | **p = 0,119** |

**El control falló.** Con p = 0,119 no se puede descartar que una asignación al azar produzca la
misma correlación. **La hipótesis se descarta**, y se publica con su número — porque un resultado
que cae exactamente donde se lo predijo y aun así no supera su control es la mejor demostración
disponible de por qué R2 existe.

Y de paso quedó registrado un defecto de fuente que se detalla en la Parte XIII: el portal informa
ENTUR como *«actualizado el 22/07/2026»*, y esa fecha es el `metadata_modified` del registro. **Los
datos son de agosto de 2019**, y son 2.823 puntos contra los 23.981 de la base del Atlas.

---

# Parte XII · La vigencia

## 36 · Por qué hizo falta

El cuello de botella del Atlas se mudó. Dejó de ser dónde están los polos y pasó a ser **si los
hitos que los sostienen siguen abiertos**.

El disparador fue un hallazgo del catálogo oficial (§40) y una constatación aritmética: entre las
filas con hitos adentro, **el 82 % estaba sin verificar**. Un padrón que no distingue lo abierto de
lo cerrado no puede sostener una vía de admisión.

Y hay una regla previa, que ya se conocía y esta fase confirmó con cinco casos más: **el catálogo de
Bares Notables no acredita apertura ni cierre.** Los Laureles cerró y siguió publicado; El Tokio
cerró en 2023 y reabrió en 2025; Todos Contentos cerró en 2020 y volvió en 2024; The New Brighton
está en quiebra desde marzo y sigue en el catálogo. **El catálogo es un registro de
reconocimiento, no de operación.**

## 37 · La escala de vigencia y los cinco veredictos

| nivel | qué es |
|---|---|
| **v1** | prensa fechada en los últimos **90 días** que lo describe funcionando, **con reporteo propio** |
| **v2** | publicación **fechada** en canal propio del establecimiento, últimos **60 días** |
| **v2b** | `business_status` de Places **con fecha de consulta registrada** |
| **v3** | reseña de usuario **con fecha visible**, últimos **90 días** |
| **v3b** | check-in de consumo fechado |
| **v4** | listado, guía o agregador **fechado**, últimos **180 días** |
| **v5** | evento concreto y fechado, **nombrado por el organizador** |

**Veredictos:** `verificado_abierto` (v1–v3b) · `probablemente_abierto` (v4 o v5 solos) · `dudoso`
(nada posterior a 180 días) · `cerrado` (evidencia positiva de cierre) · `en_disputa` (fuentes que se
contradicen sin que ninguna prevalezca).

Dos cláusulas que se agregaron con caso:

**«Nombrado por el organizador» no es adorno en v5.** Se agregó después de una grilla de evento
fabricada sobre un padrón caduco (§43) que, sin esa cláusula, habría resuelto cinco fichas de un
golpe con evidencia falsa.

**La evidencia negativa se busca, no se espera.** Avisos de cierre, quiebra, remate, local en
alquiler o venta, cambio de rubro en la dirección, despidos, posteos de despedida. Un veredicto de
apertura al que no se le buscó evidencia en contra no está verificado: está sin refutar.

## 38 · La asimetría, que decide el orden de trabajo

**Un «abierto» y un «cerrado» no valen lo mismo, y no valen lo mismo en las dos direcciones.**

Para **resolver una fila de la matriz**: un abierto resuelve la fila entera —basta un hito vivo para
sostener la vía B— y un cerrado no cierra nada, porque el resto de los hitos de esa fila sigue sin
resolver.

Para **auditar el catálogo oficial**: es al revés. Un cerrado es el hallazgo; un abierto es lo
esperado.

**Son dos operaciones distintas con la misma herramienta**, y conviene no mezclarlas: la tanda de
centro se corrió buscando aperturas y la auditoría del catálogo buscando cierres. Cuando se mezclan,
el esfuerzo se gasta donde menos rinde.

## 39 · El desbloqueo, medido

Durante dos rondas todo terminaba en `probablemente_abierto`. El diagnóstico inicial fue falta de
evidencia; **era falso**. Se hacían seis o siete rutas de búsqueda por establecimiento. El freno real
eran los `robots.txt`: Instagram, Facebook, TikTok y Yelp bloquearon en los cinco casos, y en tres de
ellos **la pieza que habría cerrado el veredicto estaba justamente ahí**.

La ruta que faltaba: **TripAdvisor no bloquea, y expone reseñas con día exacto** — que es
exactamente lo que pide v3.

| | rondas 1–2 | tanda de centro |
|---|---:|---:|
| establecimientos | 15 | 8 |
| **v3 limpios** | **0** | **5** |

Las cinco fechas: 17, 34, 52, 73 y 74 días. **Y hay que leer las dos fichas**, `.com` y `.com.ar`,
porque devuelven una «más reciente» distinta: en Las Violetas la reseña del 07/07/2026 sólo aparece
en `.com`; en Varela Varelita, 25/06 contra 02/06. **El orden de listado tampoco es estrictamente
cronológico**, así que las fechas se leen una por una y no por posición.

Corolario operativo, que invirtió el plan de trabajo: **la ruta primaria pasó a ser TripAdvisor y la
búsqueda de prensa quedó como complemento.** Es al revés de como se venía trabajando y es la razón
por la que la tanda salió entera.

**Untappd** es el segundo recurso, para bares con carta de cerveza: check-ins con fecha y usuario.
Más débil —son consumos, no reseñas en prosa— pero fechado y presencial. Queda como decisión de
criterio si computa: **si el proyecto los rechaza, La Perla cae de `verificado_abierto` a `dudoso`
sin escalón intermedio.**

**Estado al cierre de la fase:** **40 establecimientos distintos verificados** — 21
`verificado_abierto`, 2 con reserva declarada, 9 `probablemente_abierto`, 5 `dudoso`, 2 `cerrado`.

## 40 · La auditoría del catálogo, y una hipótesis mía que era falsa

El catálogo consolidado de Cafés, Bares, Billares y Confiterías Notables —**Resolución MCGC 1225/26,
firmada el 3 de agosto de 2026**— tiene 90 entradas. Se auditaron once.

**Tres están cerrados y siguen en el padrón vigente:**

| establecimiento | dirección | cerrado desde | orden |
|---|---|---|---:|
| **Plaza Bar** | Florida 1005 | **abril de 2017** — nueve años | 84 |
| **La Buena Medida** | Suárez 101, La Boca | octubre de 2025 | 61 |
| **The New Brighton** | Sarmiento 645 | marzo de 2026 (quiebra) | 88 |

Más un cuarto con evidencia parcial —**La Esquina de Aníbal Troilo**, cierre indeterminado entre 2024
y 2026— y uno **en riesgo sin cierre consumado**: la Esquina Homero Manzi, orden 55.

Y tres casos que la auditoría **resolvió al revés**, que son igual de importantes porque corrigen
datos nuestros: **La Academia** no cerró, se mudó de Callao 368 a Montevideo 341 el 19/06/2025;
**Clásica y Moderna** reabrió en diciembre de 2023; **Café Thibon** opera con nueva gestión desde
2024.

### La hipótesis del contenedor

Al ver que Plaza Bar y la Confitería del Hotel Castelar habían cerrado por cierre del edificio que
los alojaba, propuse que **el catálogo fallara sistemáticamente con los establecimientos alojados
dentro de otro inmueble** —hoteles, galerías, clubes—, porque su cierre no se comunica como cierre
gastronómico.

**Se verificaron doce establecimientos alojados. Los doce contenedores están operativos.**

**La hipótesis era mía y era falsa.** Los cierres no son de contenedor: son a nivel de calle, y todos
por alquiler. Queda registrada acá porque una hipótesis descartada con doce verificaciones vale más
que una no formulada — y porque el mecanismo real que apareció al descartarla es el de §48.

## 41 · Places como sonda de vigencia

Places entra **sólo como sonda de vigencia**, con tres restricciones duras:

1. **Publica únicamente a nivel agregado.** No salen puntos, ni `place_id`, ni nombres del
   repositorio.
2. **`vigencia_fecha_consulta` es obligatoria.** Un `business_status` sin fecha de consulta no es un
   dato: es una foto sin fecha.
3. **La asimetría está codificada** (§38): un `OPERATIONAL` resuelve; un `CLOSED_PERMANENTLY` se
   registra pero no cierra por sí solo.

**Y antes de gastar, los tres tests de calibración** — que son la aplicación directa de R5, y están
elegidos para que el resultado sea informativo pase lo que pase:

| test | cerrado hace | qué mide |
|---|---|---|
| **Plaza Bar** | 9 años | ¿detecta un cierre viejo? |
| **La Buena Medida** | 9 meses | ¿detecta un cierre de mediano plazo? |
| **The New Brighton** | 5 meses | ¿detecta un cierre reciente? |

**Donde esté el corte de detección de Places, va a estar ahí.** Si los tres salen
`CLOSED_PERMANENTLY`, la herramienta sirve para auditar el catálogo entero. Si el de cinco meses
sale `OPERATIONAL`, sabemos que la herramienta tiene latencia y de cuánto — y eso también es un
resultado que se publica.

La lista priorizada son **71 establecimientos en cuatro prioridades**, y su núcleo son los **58 hitos
del catálogo que nunca fueron mirados**.

---

# Parte XIII · Las fuentes con defecto

## 42 · El catálogo FD, y sus seis mecanismos

Quince defectos documentados —**FD-01 a FD-15**— más cuatro propuestos. No son quince fuentes malas:
son **seis mecanismos** que reaparecen en fuentes distintas, y lo que se cataloga es el mecanismo.

### Mecanismo 1 · Re-sellado de archivo

Una nota vieja recibe fecha de actualización nueva sin cambiar el cuerpo. **FD-01**: El Cronista, con
una ventana de re-datado en **septiembre de 2025** —cuatro notas confirmadas, tres al 24/09 y una al
12/09—. El caso que lo probó: una nota «actualizada» al 24 de septiembre de 2025 **seguía
recomendando dos restaurantes adentro de un mercado cerrado cinco meses antes**.

**Con un matiz que importa: no se aplica a ciegas.** Una nota del mismo medio del 5 de agosto de 2026
se actualizó **un minuto** después de publicarse, y esa sí es nueva. **El marcador es la ventana de
septiembre de 2025, no cualquier discrepancia entre publicación y actualización.**

### Mecanismo 2 · Lavado de recencia

Peor que el anterior, porque la fecha de **publicación** también es nueva: es contenido viejo
reempaquetado como nota nueva. **FD-02**: una nota del 10/07/2026 cuya frase de horarios aparece
**textual en un TikTok de enero de 2024**, y que contradice los horarios de la ficha del propio
establecimiento. **FD-14** es la variante barata: fecha fresca, cuerpo sin reporteo, ilustrado con
capturas de mapas.

Consecuencia sobre la regla anterior: ya sabíamos que una fecha de *actualización* no acredita.
**Ahora tampoco acredita una fecha de publicación reciente**, si el cuerpo es refrito. El chequeo
práctico: buscar si las frases distintivas de toda nota «reciente» aparecen antes en redes.

Y de acá sale un truco de detección que conviene generalizar: **el ancla contra refritos**. El
Imparcial sirve con un robot mozo desde marzo de 2026; cualquier nota «reciente» sobre El Imparcial
que no lo mencione es sospechosa. **Un detalle operativo fechado y verificable funciona como marca de
agua temporal.**

### Mecanismo 3 · Recencia sintética

La fecha está fabricada. **FD-13** es el caso más elaborado que apareció: un agregador estampa
*«última actualización: <fecha reciente> desde: <nombre de usuario>»* donde **la reseña real de ese
usuario es de años antes** — 12/07/2026 firmado por un usuario cuya reseña es del 13/01/2024.
**Simula trazabilidad**, que es lo que la hace peor que un re-sellado común.

Variantes menores del mismo mecanismo: **FD-09**, el año en el título («Top 10 (2026)» sobre una nota
de octubre de 2025, 223 días); **FD-15**, padrón sin fecha con un «© 2026» al pie que no es fecha de
actualización; **FD-06**, encabezado que renderiza la fecha del día, de modo que una nota de junio de
2025 se lee como de esta semana.

### Mecanismo 4 · El padrón que se re-data solo

**FD-10**: un padrón de premios marca `modified_time` fresco, pero ese cambio corresponde al alta de
la cohorte nueva y **no dice nada de los distinguidos en cohortes anteriores**.

**Ningún padrón acredita vigencia, ni siquiera uno con fecha fresca de modificación.** Es la regla del
catálogo de Notables extendida a todos los registros oficiales.

### Mecanismo 5 · El mismo dominio produciendo evidencia y ruido

**FD-07**: el sitio de turismo del GCBA convive con dos objetos distintos — **la ficha inerte**, que
arrastra contenido sin tocar desde 2018 o 2021, y **la ficha editada**, que describe un cambio con
horarios propios. De cuatro fichas abiertas en una tanda, **tres inertes y una editada de verdad**.

**Hay que mirar la fecha de modificación una por una.** Una ficha con edición reciente y horarios
específicos **sí** es evidencia —así se resolvió Los Laureles— y una inerte no lo es aunque el texto
sea entusiasta. Todas siguen sirviendo como dato factual de dirección y teléfono.

### Mecanismo 6 · Discrepancias de fecha dentro de la misma pieza

**FD-11**: URL con ruta de fecha desfasada un día respecto de los metadatos. **Regla: tomar siempre la
más vieja de las dos.** Trivial salvo en el borde de una ventana — y hubo un caso exactamente en el
borde.

### Y dos que no son defectos de fecha sino de lectura

**FD-12** — marcas de cierre visibles e inauditables: un buscador muestra *«CLOSED – Updated July
2026»* en el título del resultado, y el dominio bloquea por `robots.txt`, así que no se puede saber
de cuándo es ni de dónde salió. **Se registra, nunca se convierte en veredicto.**

**FD-03** — el mismo medio publicando las dos direcciones en diez días, sin retractar nada. No es mala
fe: es cómo se cubre un hecho en desarrollo. Pero **la unidad de análisis no puede ser el medio, tiene
que ser la nota.** «Tal medio dice que está abierto» no es una afirmación con sentido si el mismo
medio dijo lo contrario nueve días antes.

### Y uno que es un desbloqueo, no un defecto

**FD-04** — **el bloqueo suele ser de la ruta, no del dominio.** Un portal bloqueaba la URL con ruta
de fecha; la misma nota, servida desde el dominio raíz con el mismo slug, se lee entera. Así se leyó
una nota que llevaba semanas anotada como inaccesible.

**Vale reintentar así cualquier lectura fallida registrada**, y sale barato. El mismo patrón se
confirmó del lado del GCBA: dos rutas devuelven 500 mientras otras dos del mismo dominio funcionan.
**El dominio está sano; la ruta no.**

## 43 · La trampa más peligrosa

Un sitio de turismo publicó un listado de sedes «Bares Notables» de un festival de 2026 **con fechas
correctas** e incluyendo cinco de los ocho establecimientos de una tanda en curso.

Habría sido un **v5 perfecto: evento concreto, fechas concretas, cinco fichas resueltas de un solo
golpe.**

**Es falso.** Contrastado con el anuncio oficial del organizador, las sedes reales son otras diez y
**ninguno de los ocho está entre ellas**. Lo que hizo el sitio fue **pegar un padrón viejo y genérico
de Bares Notables y presentarlo como grilla del festival**.

Y se delata solo, con tres indicios acumulativos: dice «35 sedes» y enumera **39**; duplica locales
bajo dos nombres —Café Margot y Bar Margot en la misma dirección, Bar Montecarlo y Café Montecarlo—;
y el indicio decisivo, **lista «La Perla, Av. Rivadavia 2800» y «La Perla de Once, Jujuy y Rivadavia»
como si fueran dos locales distintos, cuando son la misma esquina y cerró hace nueve años.**

**La forma es nueva y no tiene precedente en el catálogo: es una grilla de evento fabricada sobre un
padrón caduco.** Y es más peligrosa que el re-sellado y que el lavado de recencia por una razón
precisa: **el evento sí existe y las fechas sí son correctas**, así que el conjunto pasa el olfato.
No hay ninguna señal interna de falsedad salvo el contraste con el organizador.

> **Regla: una sede sólo cuenta como v5 si la nombra el organizador, en una edición fechada. Nunca
> una guía intermediaria, y nunca un padrón permanente** —esto último por **FD-15**, donde ni siquiera
> el sitio del organizador acredita si publica un listado sin fecha ni vínculo a una edición concreta.

## 44 · Los cuatro propuestos que faltan cerrar

**FD-16 · Dato normativo que sólo existe en el slug de la URL.** El tramo de una figura administrativa
se pudo leer únicamente del slug de la URL canónica del portal de obras, indexada y reaparecida en
dos búsquedas independientes. **No se pudo leer el cuerpo**: la página redirige a mantenimiento. Hay
coherencia geográfica verificada, y **no hay corroboración en prosa**. Se publica con esa salvedad
escrita, no sin ella.

**FD-17 · El mismo medio contradiciéndose sobre la edad de un local.** Un mismo diario publica dos
notas sobre el mismo establecimiento diciendo «hace 150 años» y «hace 200 años». **La regla que sale
no es elegir: es atribuir.** En el caso de El Puentecito, consignar **1750 como sitio** —pulpería y
posta de carretas, según ficha del GCBA— y **~1876 como establecimiento gastronómico**, según prensa,
diciendo de dónde sale cada cifra. **El Atlas no tiene que elegir entre las dos: tiene que decir de
dónde viene cada una.**

**FD-18 · Reetiquetado editorial de una distinción real.** Un programa oficial distinto —Restaurantes
Icónicos, del GCBA con la AHRCC— aparece en cobertura como si fuera el catálogo de Bares Notables.
**Son dos registros separados** y la matriz tiene que distinguirlos: hay establecimientos con
distinción formal reciente que el catálogo de Notables no refleja, y viceversa.

**FD-19 · Fichas oficiales vivas e inertes con el mismo tono.** Es FD-07 elevado a regla general: el
problema no es que existan fichas viejas, sino que **son tipográficamente indistinguibles de las
recientes**. La única señal es la fecha de modificación, y no está a la vista.

Y un escalón de criterio que quedó explícito y hay que decidir una vez para todos los casos:
**reporteo a nivel programa versus reporteo a nivel establecimiento.** Una nota con tres entrevistados
con nombre y cargo, pero cuyo reporteo es sobre el programa y no sobre el local, es **v1 si se acepta
el nivel programa y v4 si se exige el nivel establecimiento**. En las dos lecturas el veredicto no
baja de `probablemente_abierto` y la fecha es la misma, así que no urge — pero conviene fijarlo antes
de que dos personas lo resuelvan distinto.

---

# Parte XIV · Las capas de referentes

## 45 · Tres capas, no una

| capa | qué contiene | qué hace |
|---|---|---|
| **hitos vivos** | establecimientos con reconocimiento formal o trayectoria, verificados | **abre** la vía B |
| **memoria** | establecimientos extinguidos o mutados, con nombre, dirección y causa | **no abre**; alimenta `via_B_soporte` |
| **enclaves** | 15 delimitaciones comunitarias con calles, alturas y año | alimenta la vía D |

La separación no es organizativa: **es la que permite decir dos cosas verdaderas al mismo tiempo** —
que una zona tiene trayectoria y que hoy no la sostiene— que con una sola capa no se pueden decir
juntas.

De los enclaves, dos están relevados a nivel establecimiento: **51 locales con dirección en el Barrio
Chino de Belgrano y 6 en Liniers**. El resto está delimitado pero no enumerado.

## 46 · La capa de memoria · cuatro estados

Al armarla apareció que «abierto» y «cerrado» no alcanzan:

| estado | qué es |
|---|---|
| **`extinguido`** | cerró y no volvió |
| **`extinguido con reapertura anunciada`** | cerró, se conserva y hay obra en curso |
| **`mutado`** | el local sigue vivo y cambia lo que es |
| **`interrumpido y recuperado`** | cerró y volvió — **no va en esta capa** |

**La mutación es el estado que no habíamos nombrado y el que más se malinterpreta.** Una dirección
puede seguir siendo gastronomía sin seguir siendo el establecimiento que la hizo relevante. Y un
edificio puede estar vivo y en uso —con visitas guiadas— mientras su función gastronómica no existe.
Ese último caso **circula en material de difusión como si fuera oferta**, y es exactamente la clase
de error que esta capa evita.

`interrumpido y recuperado` no va en la capa por una razón que vale explicitar: **son siete casos
verificados de establecimientos que cerraron y volvieron.** Si un cierre bastara para pasar a la capa
de memoria, siete hitos vivos estarían hoy publicados como perdidos.

**Estado: 31 entradas.** Con una limitación declarada — **17 de las 31 tienen confianza media o baja**,
casi todas provenientes de una única fuente de 2012 que ya entonces daba por sobreviviente a uno
solo. No tienen año de cierre, ni causa, ni qué hay hoy en esa dirección. **Alcanza para afirmar que
existieron; no alcanza para afirmar cuándo cerraron.** La ficha dice «documentados hacia 2012 como
ya inactivos» y no inventa fechas.

## 47 · Los homónimos · el mecanismo por el que un bar muerto se publica como vivo

Éste es el hallazgo que no esperaba de esta capa. **La capa de memoria y la capa viva comparten
nombres**, y ese es el mecanismo concreto por el que un establecimiento cerrado se publica como
abierto — o al revés.

**Hay cuatro «Perla» en el Atlas.** Una viva y en el catálogo; una que cerró en enero de 2017 y hoy
es una pizzería; y dos extinguidas en Flores. **Siete pares de nombres compartidos** están
documentados, y **tres ya produjeron un error concreto:**

- **El Coleccionista** — lo tenía en la capa extinguida de Flores a partir de una fuente de 2012. **Es
  un Bar Notable vivo de Caballito, Av. Rivadavia 4929**, entrada 44 del consolidado. Dos locales
  homónimos, mezclados.
- **Café Roma y Roma del Abasto** — dos Bares Notables vivos en dos barrios distintos, que llegaron al
  repositorio fusionados en una sola fila, con **una dirección inventada** y las coordenadas
  reasignadas. **La dirección falsa era mía.**
- **«Bar Bar O»** — buscarlo por la grafía del catálogo no devolvía nada, y probablemente por eso
  estuvo tanto tiempo en `dudoso`. Es Bárbaro.

Y uno detectado a tiempo: hay un Bar Notable vivo en San Nicolás y un homónimo extinguido en
Floresta, y **la fuente del extinguido lo nombra sin dirección** — que es justamente lo que facilita
la confusión.

> **Dos reglas, y las dos son operativas:**
> **En la capa de memoria, un establecimiento sin dirección no se carga.**
> **Todo nombre que aparezca en las dos capas lleva marca explícita de par.**

El problema tiene además una versión de grafía: un mismo local circula como «La Perla» en el
catálogo, «La Perla de Caminito» en la fachada y «La Perla, Café Notable 1882» en un agregador.
**Cinco locales con dos o tres nombres** quedaron unificados en la auditoría.

## 48 · La lectura que sólo aparece con la capa completa

**De las entradas de más de noventa años, la causa documentada del cierre fue el alquiler o el cierre
del edificio que las alojaba. Ninguna cerró por falta de público.**

Un alquiler dolarizado que se duplicó a la renovación —con las persianas colocadas un lunes a la una
de la madrugada y el personal enterándose el martes—. Un contrato no renovado. Dos casos donde cerró
el edificio y no el establecimiento.

**El mecanismo del cierre en esta ciudad es inmobiliario, no gastronómico.** Y eso tiene una
consecuencia directa para el Atlas, que conviene escribir porque es contraintuitiva:

> **Un polo puede estar sano y perder su ancla igual.**

Es lo que le pasó a la zona de Barracas, y lo que puede pasarle mañana a un hito que hoy está en
riesgo **no por vacío de público sino por una contingencia judicial**.

Y hay un caso que resume la relación entre trayectoria y reconocimiento: **La Blanqueada, en Av.
Sáenz, funcionó desde 1802 —215 años— y nunca llegó a ser declarada Bar Notable.** Es el
establecimiento gastronómico más antiguo documentado de la Ciudad, y explica por qué ese eje no se
sostiene solo hoy.

---

# Parte XV · La no duplicación

## 49 · Tres universos, y qué se puede sumar de cada uno

Ésta es la sección que hay que leer antes de publicar cualquier cifra agregada.

| universo | qué es | ¿se suma? |
|---|---|---|
| **los 124 polígonos publicables** | salida del clustering | **Sí.** Son disjuntos |
| **la matriz de 94 filas** | instrumento de comparación | **Nunca.** Se pisa por diseño |
| **la capa de hitos** | referentes con reconocimiento | Sí, deduplicando por dirección |

### Los 124 son disjuntos, y está medido

| | |
|---|---:|
| suma de las áreas individuales | **3.128,5 ha** |
| área de la **unión** | **3.128,5 ha** |
| solapamiento | **0,0 ha · 0,0 %** |

HDBSCAN produce clusters que no se superponen, y eso significa que **sobre ese conjunto los agregados
se pueden sumar sin corrección**. De ahí sale la cifra publicable:

> **12.688 locales en 3.128,5 hectáreas** — sobre una base de 23.981 locales relevados y las ~20.300
> hectáreas de la Ciudad: **el 53 % de la gastronomía relevada concentrada en el 15 % de la
> superficie.**

Calculada **sobre la unión**, no sobre una suma.

### La matriz de 94 no es una partición, y no debería serlo

Es un **instrumento de comparación**, que pone deliberadamente lado a lado objetos que se pisan —un
barrio administrativo, sus fragmentos del clustering, la envolvente publicada de la misma área— para
poder medirlos con la misma vara. Que se pise es su función.

El problema aparece sólo si alguien la suma. Y si se suma:

| | resultado de sumar | qué implicaría |
|---|---:|---|
| locales | **16.499** sobre 23.981 | que el **69 %** de la gastronomía está dentro de polos |
| superficie | **7.731 ha** sobre ~20.300 | que los polos cubren el **38 %** del territorio |

**Las dos cifras están infladas por solapamiento.**

> **La regla, y va en la primera página de cualquier entrega: la matriz de 94 no se suma nunca.
> Todo agregado se calcula sobre la unión de los polígonos publicables.**

El caso extremo está medido: **Flores está contado siete veces.** El barrio entero son 773 locales en
859 ha; adentro hay seis fragmentos del clustering que suman 270 locales en 85,7 ha. Sumando las
siete filas, **Flores da 1.043 locales cuando el barrio tiene 773: 35 % de inflación en un solo
barrio.**

## 50 · La auditoría · ocho familias de riesgo

Se auditaron ocho familias: geometría, nombres, homónimos, hitos reclamados por dos zonas, dobles
registros oficiales, doble numeración, réplicas de prensa y enclaves. **Veintinueve riesgos
identificados; veintiséis resueltos o inofensivos; tres altos.**

Lo resuelto, que no hay que volver a mirar:

- **Cinco locales con dos o tres nombres**, unificados.
- **Cuatro locales con dos registros oficiales** —Bar Notable *y* Restaurante Icónico, Sitio de
  Interés Cultural *y* Pizzería Emblemática—. **Son un hito con dos registros, no dos hitos:**
  `registro_oficial` se usa como lista y no se duplica la fila.
- **Ocho casos de doble numeración**, resueltos — con dos excepciones que **no** son doble numeración
  sino error o mudanza, y no se cargan sin verificar.
- **Seis réplicas de prensa** descontadas de la vía E (§32).
- **Tres enclaves coreanos que no son duplicados sino tres momentos de un mismo movimiento**: el
  núcleo del Bajo Flores, la extensión comercial de Ruperto Godoy y el desplazamiento a Retiro. **La
  ficha cuenta la secuencia, no repite el enclave.**

## 51 · Los dos que la geometría no resuelve sola

**Palermo.** Soho (772 locales) + Hollywood (595) + Las Cañitas (361) = **1.728 locales en 277 ha**.
La referencia publicada R01 mide **1.358 locales en 271,29 ha**.

**Las subzonas tienen más locales que la referencia que supuestamente las contiene.** No están
anidadas: son objetos distintos que se pisan parcialmente. **No lo arregla ninguna decisión de las
tomadas.** O R01 se amplía para contener a las tres, o las subzonas son las fichas y R01 deja de ser
una fila. **Las dos cosas no pueden convivir en un agregado.**

**Chacagiales.** La ampliación de R19 hacia Fraga, Dorrego y Charlone —decidida porque el
reconocimiento externo recae sobre esas calles y no sobre el eje que R19 medía— produjo un solape de
**60,4 ha, el 64 % de Chacarita**, y un crecimiento de **+347 locales, +187,6 %**.

**La decisión era internamente inconsistente con la existencia de R09, y nadie lo vio hasta que corrió
la geometría.** Esas calles están en Chacarita: ampliar R19 hacia ellas absorbe R09 necesariamente. La
ampliación hizo exactamente lo que se le pidió y el resultado es aritméticamente incompatible con que
R09 exista aparte.

Y la evidencia documental dice lo mismo desde el otro lado: **la prensa trata al conjunto como un solo
objeto y dice explícitamente que el borde es indefinido.** Hay cuatro filas nuestras encima del mismo
territorio.

La salida recomendada —fusionar en un **sistema de subpolos**— es la figura que la propia definición
del proyecto provee, y **no viola la regla de que las 22 sólo se amplían**, porque el polo fusionado
contiene a los dos: no se pierde nada.

**Y hay un residuo honesto que se conserva:** revisar el corte de otra referencia deja **24,7 ha** de
superficie publicada fuera del tramo que la evidencia documental cubre. **Se conservan** —la regla de
que las 22 sólo se amplían pesa más que la prolijidad— **y se declaran explícitamente en la ficha**
como superficie publicada en la versión anterior que la evidencia actual no alcanza. Es incómodo y es
verdad.

## 52 · El error inverso, que es más peligroso

**Contar de más se nota. Fusionar dos locales distintos en uno no se nota nunca.**

Cuatro casos donde estuvo a punto de pasar: dos locales con nombres casi idénticos donde uno es sede
real de un evento y el otro no; dos homónimos en barrios distintos, uno vivo y uno cerrado hace nueve
años; dos bodegones de nombre parecido en barrios distintos; y **dos Bares Notables vivos que llegaron
fusionados en una sola fila, con dirección inventada y coordenadas reasignadas.**

**Una fusión indebida no infla ningún total** —al contrario, lo desinfla— **y por eso ninguna
verificación de suma la detecta.** La única defensa es el cruce por dirección normalizada, no por
nombre.

---

# Parte XVI · Trampas técnicas y errores de esta fase

## 53 · La trampa de biblioteca · `covers()` sobre diferencia exactamente cero

Al verificar que los polígonos ampliados **contienen** a los originales, el predicado de contención
devolvió **NO** en los cuatro casos. La lectura inmediata habría sido que las ampliaciones no
contenían a lo publicado, y que las decisiones estaban mal ejecutadas.

**Era falso.** La verificación se rehízo **por superficie perdida: 0,0 m² en las cuatro.** Las cuatro
contienen.

> **`covers()` de GEOS devuelve NO sobre geometrías cuya diferencia es exactamente cero.**

Es una trampa de biblioteca, no de datos, y tiene el mismo perfil que los tres bugs de R8: **falla en
silencio y en la dirección conservadora**, que es la que menos sospecha despierta. **La contención se
verifica por superficie perdida, no por predicado.**

## 54 · Los errores de esta fase, con su mecanismo

Se listan porque el documento anterior estableció la convención de publicar lo que salió mal, y
porque **cada uno produjo una regla**.

| error | qué era | mecanismo | regla que produjo |
|---|---|---|---|
| **ENTUR «actualizado 22/07/2026»** | son datos de **agosto de 2019**; la fecha es el `metadata_modified` del registro | fecha de metadato leída como fecha del dato | **R11** |
| **Cinco hitos duplicados alimentados al repositorio** | ya estaban en la capa, con punto y dirección | verifiqué contra mis propios archivos y no contra la capa cargada | **R9** |
| **Dirección inventada en una fila fusionada** | dos Bares Notables distintos, una dirección que no existe | fusión por nombre, sin cruce por dirección | §52 |
| **Perímetro de cero cuadras** | dos avenidas que son **la misma**, renombrada al cruzar | no se verificó que el tramo tuviera longitud | **R12** |
| **Enclave con eje inflado** | abrió la vía D en dos fragmentos que no correspondían | delimitación textual extendida sin verificar contra qué toca | §29 |
| **Alarma de cierre por atribución equivocada** | la frase se refería a **otro** establecimiento, a 1,5 km | atribución de un pronombre a la entidad más cercana en el texto | **R13** |
| **Hito vivo puesto en la capa extinguida** | homónimo: dos locales con el mismo nombre en barrios distintos | §47 |  |
| **Hipótesis del contenedor** | falsa; los doce contenedores verificados están operativos | hipótesis formulada sobre dos casos que compartían otra cosa | R2, aplicada |

**El patrón que atraviesa la mitad de la tabla: producir un dato que ya existía, o afirmar una
relación entre dos objetos sin verificar que la relación exista.** No son errores de fuente. Son
errores de cruce.

Y la lección más incómoda del conjunto: **la auditoría de duplicados y el episodio de los cinco hitos
duplicados ocurrieron el mismo día.** Escribir la regla no es aplicarla.

## 55 · Las reglas nuevas · R9 a R13

Las ocho reglas de la Parte IX siguen vigentes sin cambios. Se agregan cinco, y cada una tiene su
caso en §54.

| # | regla | caso |
|---:|---|---|
| **R9** | **Antes de reportar un dato como nuevo, se cruza contra la capa cargada — nunca contra archivos propios** | cinco hitos duplicados |
| **R10** | **Un referente sin dirección no se carga en ninguna capa**, y todo nombre presente en dos capas lleva marca de par | §47, siete pares |
| **R11** | **La fecha de un metadato no es la fecha del dato.** Ni `metadata_modified`, ni fecha de actualización, ni fecha de publicación si el cuerpo es refrito | ENTUR, y toda la Parte XIII |
| **R12** | **Toda delimitación se verifica midiéndola**: un tramo tiene que tener longitud, una contención se verifica por superficie perdida | perímetro de cero cuadras; §53 |
| **R13** | **Una atribución se verifica contra la entidad nombrada, no contra la más cercana en el texto ni en el mapa** | alarma de cierre; homónimos |

**Las seis preguntas de la Parte IX se amplían a nueve:**

1. ¿Estaba escrita la lectura antes de correr?
2. Si hubo ablación, ¿tuvo control aleatorio?
3. ¿Algún umbral se movió después de ver el resultado?
4. Si el resultado depende de un parámetro, ¿está la curva?
5. Si se gastó presupuesto, ¿se reportó gastado contra estimado?
6. ¿Hay alguna frase que diga «no existe» donde corresponde «no encontramos»?
7. **¿Esto ya existe en la capa cargada?**
8. **¿La fecha que estoy usando es del dato o de su metadato?**
9. **¿La relación que afirmo entre dos objetos está verificada, o inferida por proximidad?**

Si alguna respuesta incomoda, el resultado todavía no es una conclusión.

---

# Parte XVII · Los límites de esta fase

Lo que esta parte del método **no** puede decir, dicho antes de que alguien lo pregunte.

**Sobre vigencia no dice «está abierto»: dice «hay evidencia fechada de actividad al día tal».** Es
una mejora sobre el límite que declaraba la Parte X, no su cancelación. **`probablemente_abierto` es
un veredicto honesto y no un veredicto débil**, y hay establecimientos que no van a poder pasar de
ahí mientras las redes sociales sigan bloqueadas.

**Una verificación tiene fecha de vencimiento.** Un `verificado_abierto` a 17 días es un hecho sobre
julio de 2026. La verificación no es un atributo permanente del establecimiento: es un dato con
fecha, y por eso `vigencia_fecha_consulta` es obligatoria en todos lados. **Cualquier publicación
tiene que declarar su fecha de corte.**

**La cobertura de la verificación es parcial y sesgada hacia lo verificable.** 40 establecimientos de
un universo mucho mayor, y los que se verificaron primero fueron los que tenían presencia en
agregadores. **Un establecimiento sin reseñas en línea no es un establecimiento cerrado** — es uno que
este instrumento no alcanza, y hay una clase entera de gastronomía barrial exactamente ahí.

**La capa de memoria no es un censo de lo perdido.** Es lo que apareció buscando, con 17 de 31
entradas de confianza media o baja. Lo que no está en ella no es lo que no se perdió: es lo que
ninguna fuente registró.

**El criterio de admisión no produce «el» conjunto de polos.** Produce **un conjunto reproducible,
con la vía de entrada explícita en cada caso**. Alguien que discuta un umbral de la vía E puede
recalcular exactamente qué zonas cambian, y eso es lo defendible — no la lista.

**Y la herencia documental es una muleta con fecha de vencimiento propia** (§29). Cuando la geometría
se descongele y los polígonos cubran las zonas, `heredada` tiene que volver a ser `propia`. **Si el
campo `via_X_modo` sigue lleno de `heredada` dentro de dos años, es una deuda, no un diseño.**

---

# Anexo B · qué archivo produce qué número · fase documental

Todos en `outputs/BARRIDO_CIUDAD_2026-08/desde_cowork/evidencia_2026/`.

| tema | archivo |
|---|---|
| criterio de las dos familias de vías | `CRITERIO_ESCALA_DE_LAS_VIAS.md` |
| criterio de escala de la vía E | `CRITERIO_ESCALA_DE_LA_VIA_E.md` |
| vía E, las 94 filas asignadas | `via_E_94_filas.csv` |
| vía E, las 22 referencias publicadas | `via_E_22_referencias.csv` |
| decisión trayectoria versus actividad | `DECISION_TRAYECTORIA_VS_ACTIVIDAD.md` |
| las 20 decisiones con su consecuencia operativa | `DECISIONES_TOMADAS_2026-08-07.csv` |
| escala de vigencia y primeros patrones de falla | `ESCALA_DE_VIGENCIA_Y_PATRONES_DE_FALLA.md` |
| vigencia · rondas y tandas | `vigencia_verificada_ronda_1.csv`, `_ronda_2.csv`, `vigencia_ronda_2_cerrada.csv`, `vigencia_tanda_A_centro.csv`, `vigencia_tanda_B_almagro_norte.csv`, `vigencia_cierre_del_dia.csv` |
| auditoría del catálogo oficial · los tres cerrados | `catalogo_notables_auditoria_cierres.csv`, `AUDITORIA_DEL_CATALOGO_OFICIAL.md` |
| el catálogo de 90 cruzado contra las zonas | `catalogo_90_notables_cruzado.csv`, `CRUCE_DE_LOS_90_NOTABLES.md` |
| fuentes con defecto FD-01 a FD-15 | `fuentes_con_defecto_FD05_FD07.csv`, `_FD08_FD12.csv`, `_FD13_FD15.csv`, `EL_DESBLOQUEO_Y_LA_TRAMPA_PEOR.md` |
| Places · especificación y lista priorizada | `PLACES_PARA_VIGENCIA.md`, `lista_places_prioridad.csv` |
| capa de memoria y homónimos | `capa_de_memoria.csv`, `homonimos_vivo_muerto.csv`, `LA_CAPA_DE_MEMORIA.md` |
| enclaves comunitarios delimitados | `enclaves_comunitarios_delimitados.csv`, `enclaves_E02_E07_reparados.csv`, `enclaves_establecimientos_E02_E07.csv` |
| auditoría de duplicados · los 29 riesgos | `auditoria_duplicados.csv`, `AUDITORIA_DE_DUPLICADOS.md` |
| nudo Chacagiales, cola de R20, trampa GEOS | `EL_NUDO_CHACAGIALES_Y_CUATRO_CORRECCIONES.md` |
| corpus de fichas de polo | `fichas_corpus_polos.csv`, `FICHAS_CORPUS_LEEME.md` |
| lectura previa y resultado de ENTUR × vía E | `LECTURA_PREVIA_ENTUR_x_VIA_E.md` |
| correcciones propias, con su mecanismo | `CORRECCIONES_MIAS_2026-08.md`, `REPARACION_ENCLAVES_Y_TRES_CORRECCIONES.md` |
| barrido por zonas · rondas 2, 3 y sur | `seis_vias_ronda_2.csv`, `seis_vias_ronda_3_norte.csv`, `seis_vias_Z47_Z48_Z49.csv`, `seis_vias_sur_consolidado.csv` |
| material para la presentación | `LAMINAS_PLAN_2026_POLOS_Y_CLUSTERS.md` |
