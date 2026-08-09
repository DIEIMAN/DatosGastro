# El Relevamiento de Ejes Comerciales del IDECBA — la fuente que nos faltaba, y es del propio Gobierno

*8 de agosto de 2026 · encontrada rastreando de dónde salía el censo de Las Cañitas*
*Corregido en la ronda 12 contra la planilla, que ya está bajada.*

Datos en `idecba_ejes_comerciales.csv` y `idecba_ocupacion_por_eje.csv` — **las dos reescritas
sobre los 48 ejes vigentes**. La tabla completa con tramos está en
`ronda_12/idecba_48_autoridad.csv`.

> ## Corrección de entrada: son 48 ejes, no 53 — y la autoridad es el XLSX
>
> Todo lo que sigue se escribió leyendo el **informe en PDF**. La planilla
> `AC_EJ_2026_03.xlsx` se bajó después, y sus cuatro cuatrimestres —1.º de 2025 a 1.º de
> 2026— traen **48 ejes**, no 53. Mi conteo del PDF además ya era internamente
> inconsistente: los subtotales por zona que transcribí suman 57 y los nombres que listé
> son 53.
>
> **Seis ejes que cité no están en la serie vigente:** *Microcentro, Palermo Hollywood,
> Cañitas, Nazca, Murillo* y *Jujuy*. **Y uno que no cité sí está:** *Lavalle*
> (Corrientes 501-999 · Lavalle 501-999 · Esmeralda 401-599), que es el eje del microcentro
> peatonal en la serie vigente.
>
> **Eso no es un error de conteo: es la lámina 14.** El 63,2 % de ocupación del
> «Microcentro» y su caída de 7,2 puntos —el número que sostenía la lámina más fuerte del
> paquete— vienen de una edición anterior del relevamiento y **no existen en la serie
> vigente**. Lo mismo la corroboración del censo de Las Cañitas y la caída de Palermo
> Hollywood. Qué sostenía cada uno está en `ronda_12/idecba_los_6_que_salen.csv`.
>
> El volumen también cambia: **12.896 locales relevados y 11.605 ocupados**, no 15.636 y
> 14.083.

---

## Qué es

El **Instituto de Estadística y Censos de la Ciudad Autónoma de Buenos Aires (IDECBA)**, dependiente de la Jefatura de Gabinete de Ministros del GCBA, publica un **Relevamiento de Ejes Comerciales**.

| | |
|---|---|
| cobertura | **48 ejes comerciales** — el XLSX no trae la agrupación por zona; las cuatro zonas de abajo son las del PDF, sostenidas para poder comparar |
| volumen | **12.896 locales relevados** · 11.605 ocupados · 1.291 desocupados · ocupación 90,0 % |
| periodicidad | **cuatrimestral** |
| último dato visto | 3er cuatrimestre de 2025, provisorio, publicado en enero de 2026; y una serie de banco de datos con 1er cuatrimestre 2025 / 1er cuatrimestre 2026 |
| método | **relevamiento visual, a pie** |
| acceso | **público, descargable** — planilla `AC_EJ_2026_03.xlsx` en el banco de datos |

Lo que mide, por eje: **locales relevados, ocupados y desocupados, tasa de ocupación, densidad comercial, locales desocupados por cuadra, variación respecto del relevamiento previo y variación interanual, y rubro de actividad.**

Y define densidad con una fórmula que conviene copiar literal, porque es más honesta que la nuestra:

> **Densidad comercial: «cociente de la cantidad de locales sobre el total de cuadras relevadas (teniendo en cuenta ambas aceras)».**

**Es público y es del propio Gobierno de la Ciudad.** No es una fuente interna: está publicado en el sitio del Instituto, con archivo descargable.

---

## Por qué esto es lo más importante que encontré en todo el barrido

El Atlas tiene tres agujeros que esta fuente toca directamente.

### Uno · No teníamos ninguna medida de estado a escala de zona

Toda la capa de vigencia que construimos es **establecimiento por establecimiento**: cuarenta verificados, uno a uno, a mano. No hay forma de escalar eso a una ciudad.

Esto da **tasa de ocupación por eje, cada cuatro meses, relevada a pie.** Es exactamente la medida de estado de zona que no teníamos, y no la tenemos que producir nosotros.

### Dos · El Atlas no puede decir si un polo crece o se achica

Es un mapa de un momento. La única variable temporal que tiene es la `añada`, que es la última señal de actividad de un local y no una serie.

Esto trae **variación interanual y variación respecto del relevamiento previo, por eje.** Con eso el Atlas puede decir, con fuente oficial, cuáles de sus polos están creciendo y cuáles perdiendo locales.

### Tres · Nuestra densidad no tenía con qué compararse

La vía A se mide sobre nuestros polígonos y con nuestra base. Nunca tuvo un contraste externo.

Esto la mide **sobre cuadras contadas, con las dos aceras, por un tercero, sobre un perímetro declarado.** Es el control que la edición técnica pedía y no tenía.

---

## Los 48 ejes, y cuántos son nuestros

**Norte (9):** Cabildo · **Chacarita** · **Colegiales** · Córdoba y Scalabrini Ortiz · **Palermo Soho** · Recoleta · Santa Fe y Coronel Díaz · Santa Fe y Scalabrini Ortiz · Triunvirato

**Centro (13):** Av. Belgrano · Córdoba Facultad · Córdoba Tribunales · Corrientes y Callao · Corrientes y Pueyrredón · Entre Ríos · **Florida** · **Lavalle** · Libertad · **Monserrat** · **Once** · **Puerto Madero** · Santa Fe y Callao

**Oeste (13):** **Almagro** · Av. San Martín · Avellaneda · Caballito · Corrientes y Medrano · Corrientes y Scalabrini Ortiz · Cuenca · Devoto · **Flores** · **Liniers** · Monte Castro · **Villa Crespo** · **Warnes**

**Sur (13):** Alberdi · Av. Patricios · **Boedo** · Chilavert · Constitución · **Defensa** · **Flores Sur** · **Mataderos** · **Montes de Oca** · Parque Avellaneda · Parque Patricios · Riestra · **Sáenz**

**Veintiuno coinciden con zonas que ya tenemos, veintiuno no, y seis coinciden en parte.** Y una de las coincidencias es una decisión abierta de esta semana:

> **El Instituto de Estadística de la Ciudad releva «Chacarita» y «Colegiales» como dos ejes distintos.**

Eso no decide nuestra fusión —un eje comercial no es un polo gastronómico, y las escalas no tienen por qué coincidir— pero es **una segunda fuente oficial e independiente que trata a esos dos objetos por separado**, y estaba ausente de la discusión.

> **Y acá se cae lo que había dicho sobre Palermo.** La serie vigente releva **un solo eje de
> Palermo: Palermo Soho.** Hollywood y Cañitas no están. El argumento de que «la Ciudad ya
> delimita Soho, Hollywood y Cañitas como tres cosas» **se apoyaba en las dos que salieron** y
> no se sostiene. La hipótesis de la resta de Palermo pierde esta pata y queda como estaba
> antes de esta fuente.

Cada eje viene con sus tramos —calle y rango de alturas—, ochenta en total: eso es lo que
permite atribuir un establecimiento a un eje sin adivinar. La tabla está en
`ronda_12/idecba_48_autoridad.csv`.

---

## Las cuatro salvedades, que hay que escribir antes de usarla

**Es un relevamiento comercial, no gastronómico.** El rubro «Alojamiento y comida» es el **11,3 %** del total. La gastronomía hay que aislarla por rubro, y la clasificación es de ellos, no nuestra.

**Su método excluye justo lo que compone varios de nuestros polos.** Releva locales *«con acceso directo desde la calle»* y *«atención al público»*, y **excluye galerías, shoppings, puestos informales y actividades sin fines de lucro**.

Eso deja afuera, por diseño: el interior de los mercados, los patios gastronómicos, las galerías del Barrio Chino, las ferias, y toda la oferta sin frente a la calle. **Es el sesgo espejo del nuestro**: nosotros contamos habilitaciones y registros que incluyen lo que no tiene vidriera; ellos cuentan lo que se ve caminando. **Las dos coberturas son parciales y lo son en direcciones opuestas**, y por eso el cruce vale más que cualquiera de las dos.

**Es una muestra de ejes, no la Ciudad.** 48 corredores. Que un barrio no esté en la lista no dice nada sobre su comercio — **R7 se aplica a esta fuente igual que a las nuestras.** Y ahora se sabe que **la muestra cambia entre ediciones**: seis ejes que el informe anterior relevaba ya no están. Un eje que sale no es un eje que empeoró.

**Y no computa como vía E.** Es del GCBA, y la regla dice que la comunicación del Gobierno no acredita reconocimiento externo por parte interesada. Pero conviene precisar la regla, porque esto no es comunicación:

> **Una fuente oficial no acredita reconocimiento, pero sí acredita medición.**
>
> Va a las vías **A** y **F** y a la capa de estado. **No va a la vía E.**

Sin esa precisión, alguien la va a usar para abrir la vía E de veinte zonas de un plumazo, o alguien la va a descartar entera por ser del Gobierno. Las dos serían errores.

---

## Lo que haría con esto, en orden

**Uno · Cruzar los 48 ejes contra nuestros 41 polos.** *(Hecho en la ronda 12: 21 coinciden, 21 no, 6 en parte.)* Tres resultados, y los tres sirven:

- **Los que coinciden** heredan tasa de ocupación, densidad comercial y serie de variación, gratis y con fuente oficial.
- **Los ejes que no tenemos como polo** son candidatos a evaluar con las seis vías. Algunos van a ser corredores comerciales sin identidad gastronómica —y eso también es un resultado— pero *Cuenca*, *Chilavert*, *Riestra* o *Alberdi* no están hoy en nuestra matriz y merecen una mirada. *(Murillo y Nazca salen de la lista: no están en la serie vigente.)*
- **Los polos nuestros sin eje oficial** son los que la Ciudad no está mirando comercialmente. **Ésa es una lámina sola**: dónde hay concentración gastronómica que la estadística comercial de la propia Ciudad no releva.

**Dos · Calibrar nuestra densidad contra la suya. No validarla.**

> **Habilita calibración, no equivalencia.** Ellos miden **locales por cuadra sobre un eje
> lineal**; nosotros medimos **locales por hectárea sobre un polígono**. Son dos magnitudes
> distintas, no la misma medida en dos manos. Lo escribí como si fueran lo mismo y no lo son.

Lo que sí se puede hacer: mirar **si la razón entre las dos es estable entre ejes**. Si lo es,
hay un factor de conversión y un control externo. Si no lo es, la variación misma señala dónde
nuestra base ve distinto — y probablemente sea donde hay galerías y mercados, que es justo lo
que ellos excluyen. **Ninguno de los dos resultados valida una medida con la otra.**

**Tres · Usar la tasa de ocupación como señal de prioridad para la capa de vigencia.** Los ejes con desocupación alta o en aumento son donde más probable es que un hito esté cerrado. Es una forma barata de ordenar los 58 del catálogo que nunca fueron mirados, y no cuesta un solo request de API.

**Cuatro · Chequear si hay serie histórica.** El informe de enero de 2026 lleva número de orden 2005 en su nomenclatura, y el banco de datos ofrece comparaciones interanuales. **Si la serie tiene varios años, el Atlas puede decir cómo evolucionó cada corredor** — y eso es otra cosa completamente distinta de lo que tiene hoy.

---

## Una nota sobre cómo apareció, porque tiene moraleja

No la busqué. Salí a averiguar **de dónde salía el censo comercial de Las Cañitas** que había encontrado en La Nación, con la idea de que si alguien releva un corredor a pie, quizás releve más de uno.

La pregunta *«¿quién produce este dato?»* resultó valer mucho más que el dato.

Vale como método: **cuando una fuente periodística trae una cifra demasiado específica para haberla producido ella misma —950 locales, 7 % de vacancia, 192 comercios desde 2009—, la cifra tiene un dueño, y el dueño suele publicar más.**

Y vale como observación incómoda: **es una fuente del propio Gobierno de la Ciudad, pública y descargable, que el Atlas no estaba usando.** No hay que pedir nada ni negociar acceso a nada. Está en el sitio del Instituto.

---

## Lo que no pude hacer — y lo que pasó cuando se hizo

**No pude bajar la planilla `AC_EJ_2026_03.xlsx`** — el dominio no responde a mi entorno. Los números por eje que están en ese archivo —locales relevados, cuadras, densidad comercial— son la parte que faltaba, y son la que hace posible el cruce.

**Se bajó en la ronda 10** (`idecba/crudos/`), junto con el glosario de los 48 ejes con sus 80 tramos. Y la moraleja de esta ficha se le da vuelta encima:

> **La pregunta «¿quién produce este dato?» valía más que el dato. Y la pregunta que faltaba
> era «¿de qué edición es el dato que estoy leyendo?».** El informe en PDF y la planilla del
> banco de datos no cubren los mismos ejes. Escribí una lámina entera sobre un eje que la
> serie vigente no releva.
