# Tanda A · centro: ocho de ocho, un desbloqueo de método y la trampa más peligrosa hasta ahora

*7 de agosto de 2026*

Datos en `vigencia_tanda_A_centro.csv` y `fuentes_con_defecto_FD05_FD07.csv`.

Esta tanda se corrió con la asimetría que marcó el repositorio: **un "abierto" resuelve una fila entera, un "cerrado" no cierra nada**, porque ninguna de estas filas tiene el resto de sus hitos resuelto. Así que se buscaron aperturas, al revés de la auditoría del catálogo.

**Resultado: ocho de ocho abiertos.** Cinco con v3 limpio, tres con reserva declarada. Ninguno cerrado.

---

## 1 · El desbloqueo: TripAdvisor se lee, y expone el día exacto

Después de dos rondas terminando todo en `probablemente_abierto` porque Instagram, Facebook, TikTok y Yelp bloquean, apareció la ruta que faltaba.

**TripAdvisor no bloquea. Y expone reseñas con día exacto, no solo mes** — que es precisamente lo que pide el nivel v3.

Eso cambia el rendimiento de la verificación por completo. En las dos rondas anteriores, quince establecimientos y **ningún v3**. En esta tanda, ocho establecimientos y **cinco v3 limpios**, con fechas de 17, 34, 52, 73 y 74 días.

**Untappd** es el segundo recurso, para bares con carta de cerveza: expone check-ins con fecha y usuario. Es más débil —son consumos, no reseñas en prosa— pero fecha y es presencial.

Esto reordena la ronda 3 y la tanda B: **la ruta primaria pasa a ser TripAdvisor, y la búsqueda de prensa queda como complemento.** Es al revés de como veníamos trabajando, y es la razón por la que esta tanda salió entera.

---

## 2 · Lo que se resolvió

**Cinco con v3 limpio:**

| establecimiento | fecha | días | qué dice |
|---|---|---|---|
| **Bar El Federal** | 21/07/2026 | 17 | *"esperábamos que fuera muy turístico y nos sorprendió gratamente que el bar estuviera tranquilo"*. Dos reseñas de julio, de usuarios distintos |
| **Los 36 Billares** | 04/07/2026 | 34 | Dos reseñas con día visible; una describe las arañas originales y las mesas de pool en uso |
| **El Globo** | 16/06/2026 | 52 | **Nombra a un empleado, Maxi** — eso la hace casi imposible de confundir con un refrito |
| **Café Tortoni** | 26/05/2026 | 73 | Reseña crítica —3 de 5, churros mediocres— pero inequívocamente presencial |
| **Café de los Angelitos** | 25/05/2026 | 74 | Más sitio propio con función vigente y motor de reservas activo |

Y **El Federal era el urgente**: la vía E de R03 San Telmo acababa de quedar en dos grupos por el re-sellado de El Cronista. Con el hito principal verificado a 17 días, la fila deja de estar expuesta por los dos lados a la vez.

**Con Café Tortoni queda desplazada** la nota de Canal 26 del 17 de julio que lo daba operativo citando Wikipedia al pie. Ya no hace falta apoyarse en ella.

---

## 3 · Tres con reserva, y las reservas son honestas

**Tancat y El Imparcial** se apoyan en la cobertura del 7 de julio sobre los 16 Restaurantes Icónicos. La pieza de Info Gastronómica tiene reporteo propio verificable —tres entrevistados con nombre y cargo, entre ellos el presidente de la AHRCC— pero **ese reporteo es sobre el programa, no sobre el local**. La descripción del establecimiento puede venir de gacetilla.

Queda explícito el escalón: **v1 si se acepta reporteo a nivel programa, v4 si se exige a nivel establecimiento.** En cualquiera de las dos lecturas el veredicto no baja de `probablemente_abierto` y la fecha es la misma. Es una decisión de criterio, y conviene tomarla una vez para todos los casos.

Y una nota de registro: **ni Tancat ni El Imparcial son Bares Notables.** Son "Restaurantes Icónicos", un programa distinto del GCBA con la AHRCC. Son dos registros separados y conviene que la matriz los distinga. De paso apareció que **habrá una nueva tanda de Icónicos en Hotelga 2026, del 2 al 4 de septiembre en La Rural** — vale anotarlo para volver.

**La Perla** depende de check-ins de Untappd. Son dato de usuario fechado y presencial, pero no reseña en prosa. **Si el criterio del proyecto los rechaza, cae a `dudoso` sin escalón intermedio**, porque lo siguiente que tiene es de diciembre de 2025.

---

## 4 · La Perla estaba mal identificada, y ahora se sabe cuál es

**Es la de Caminito: Av. Don Pedro de Mendoza 1899, La Boca**, entrada 68 del anexo de la Res. 1225/26.

Cómo se decidió: el consolidado 2025 tiene **una sola** entrada "La Perla", y es esa. Se verificó expresamente que no hay ninguna en Av. Rivadavia 2800 ni en Balvanera. Y hay razón de fondo: **La Perla del Once cerró el 14 de enero de 2017** y en su local funciona la pizzería La Americana. No podría estar en un catálogo de 2025.

**Nuestro dato está mal:** la teníamos sobre Del Valle Iberlucea. El anexo la asienta sobre Av. Don Pedro de Mendoza 1899, la esquina de la Vuelta de Rocha. Hay que corregirlo.

Y es otro caso de la trampa del nombre: circula como **"La Perla"** en el catálogo, **"La Perla de Caminito"** en la fachada y **"La Perla, Café Notable 1882"** en TripAdvisor. Tres grafías del mismo local, igual que "Bar Bar O" y Bárbaro.

---

## 5 · La trampa más peligrosa que apareció hasta ahora

Un sitio de turismo publica un listado de **sedes "Bares Notables" del Festival y Mundial de Tango 2026**, con fechas correctas —del 19 de agosto al 1 de septiembre— e incluye a Tortoni, Los 36 Billares, El Federal, Angelitos y "La Perla".

Sería un **v5 perfecto: evento concreto, fechas concretas, cinco de las ocho fichas de un solo golpe.**

**Es falso.** Contrastado con el anuncio oficial del GCBA, las sedes reales son otras diez —El Viejo Buzón, La Puerto Rico, Saint Moritz, La Ideal, La Poesía, Brighton, Las Violetas, Esquina Homero Manzi, Claridge's y el Cabildo— y **ninguno de los ocho está entre ellas**. La Nación del 3 de agosto tampoco los nombra.

Lo que hizo el sitio fue **pegar un padrón viejo y genérico de Bares Notables y presentarlo como grilla del festival**. Y se delata solo: dice "35 sedes" y enumera 39, duplica locales bajo dos nombres —Café Margot y Bar Margot en la misma dirección, Bar Montecarlo y Café Montecarlo— y, el indicio decisivo, **incluye "La Perla, Av. Rivadavia 2800" y "La Perla de Once, Jujuy y Rivadavia" como si fueran dos locales distintos, cuando son la misma esquina y cerró hace nueve años.**

**La forma es nueva.** No es re-sellado ni lavado de recencia: es **una grilla de evento fabricada sobre un padrón caduco**. Y es más peligrosa que las anteriores porque **el evento sí existe y las fechas sí son correctas**, así que el conjunto pasa el olfato.

**Regla que propongo, y que va a la capa de fuentes:**

> **Una sede solo cuenta como v5 si la nombra el organizador.** Nunca una guía turística intermediaria.

Se suman dos defectos menores pero repetibles, en `fuentes_con_defecto_FD05_FD07.csv`:

**C5N renderiza la fecha del día en el encabezado.** Una nota de junio de 2025 se lee como de esta semana; la fecha real solo aparece en el bloque de autoría, más abajo.

**El sitio de turismo del GCBA produce los dos objetos a la vez.** De cuatro fichas abiertas en esta tanda, **tres son inertes** —El Federal modificada en 2018, La Perla en 2024— y **una está editada de verdad**: Tancat, modificada el 11 de marzo de 2026, con horarios propios. Confirma lo que vimos con Los Laureles, y agrega la instrucción operativa: **hay que mirar la fecha de modificación una por una**, porque el mismo dominio produce evidencia y ruido.

---

## 6 · Tres correcciones de dato

**El Federal:** el anexo consigna **Carlos Calvo 595**; nosotros y TripAdvisor decimos 599. Es la misma esquina de Perú y Carlos Calvo. Hay que unificar criterio, no elegir al azar.

**Los 36 Billares:** el anexo dice **Av. de Mayo 1265/71**. No es discrepancia: es un local con doble numeración.

**La Perla:** Av. Don Pedro de Mendoza 1899, no Del Valle Iberlucea.

Y una asimetría que vale registrar aunque no cambie nada: **El Globo no figura en ningún registro oficial** —ni Bar Notable ni Restaurante Icónico— mientras **El Imparcial, que está enfrente, entró a los 16 Icónicos**. Dos bodegones históricos en la misma esquina de H. Yrigoyen, uno distinguido y el otro no.

---

## 7 · Lo que queda, y es barato

**Tancat es el que más rinde y el que peor quedó.** Toca tres filas, y su reseña de TripAdvisor del 3 de mayo quedó **seis días fuera** de la ventana. Un vistazo a `@tancattasca` resuelve tres filas en dos minutos.

Y un ancla útil para detectar refritos: **El Imparcial sirve con un robot mozo**, según una reseña de marzo de 2026. Cualquier nota "reciente" sobre El Imparcial que no lo mencione es sospechosa de ser vieja.
