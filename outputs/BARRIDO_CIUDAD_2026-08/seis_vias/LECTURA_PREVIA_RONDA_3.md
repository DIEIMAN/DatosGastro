# Lectura previa · ronda 3 · el soporte de la vía B, los cuatro estados de la vía D y el norte

*Escrita el 7 de agosto de 2026, ANTES de correr. Regla R1. Continúa `LECTURA_PREVIA_RONDA_2.md`.*

El cruce ENTUR × vía E tiene su propia lectura previa, escrita por Diego y fechada antes de esta
corrida: `desde_cowork/evidencia_2026/LECTURA_PREVIA_ENTUR_x_VIA_E.md`. Acá **no se repiten sus
predicciones ni se agregan otras**; lo único que se declara sobre esa tarea son los dos controles
y el estadístico, que ya vienen fijados desde allá.

Google Places: 0 requests. USIG sí. Ninguna geometría publicada se toca.

---

## 1 · Lo que se revierte, antes que nada

La ronda 2 bajó la vía B de **P008 Barracas** porque su único hito, Los Laureles, figuraba
`vigencia_verificada = no`. Ese `no` era una lectura de una sola fuente. La Nación y Canal 26
publican el **mismo día** —5 de agosto de 2026— que cerró y que no cerró, y El Tokio (Álvarez
Jonte 3550) cerró en 2023 y **reabrió en 2025** sin que ningún listado registrara ni una cosa ni la
otra.

**Se revierte:** Los Laureles pasa de `no` a `en_disputa`, y P008 vuelve a no estar cerrada. La
regla que la ronda 2 declaró en su §2 —«un hito cerrado no abre vía B»— sigue en pie; lo que
estaba mal era el estado del hito, no la regla.

---

## 2 · `via_B_soporte`: los cinco valores y su orden de precedencia

Se agrega a cada fila de la matriz un campo `via_B_soporte` que resume el estado de sus hitos:

| valor | condición sobre los hitos de la fila | `via_B_abierta` |
|---|---|---|
| `activo` | hay ≥1 hito verificado abierto y ninguno verificado cerrado | `si` |
| `mixto` | hay ≥1 verificado abierto **y** ≥1 verificado cerrado | `si` |
| `extinguido` | hay hitos y **todos** están verificados cerrados | `no` (se publica como capa histórica) |
| `en_disputa` | ninguno verificado abierto y ≥1 en disputa entre fuentes | `pendiente` |
| `sin_verificar` | ninguno verificado abierto, ninguno en disputa, y ≥1 sin verificar | `pendiente` |

**El orden de precedencia se declara acá y no se mueve después:**

    activo / mixto  >  en_disputa  >  sin_verificar  >  extinguido

Es decir: `extinguido` sólo se aplica cuando **todos** los hitos de la fila están verificados
cerrados. Una fila con un cerrado y un sin verificar no es `extinguido`: el sin verificar puede
estar abierto y nadie miró. Esa es exactamente la asimetría que Los Laureles obliga a respetar, y
es el motivo de que `extinguido` quede último y no primero.

**Un sexto valor de contabilidad, que Diego no pidió y hay que declarar igual:** las filas que
**no tienen ningún hito adentro** no pueden tomar ninguno de los cinco, porque los cinco suponen
que hay hitos. Toman `sin_hitos` y `via_B_abierta = no`. Un `sin_verificar` ahí sería falso: no
hay nada que verificar.

**`dudosa` se pliega a `sin_verificar`.** El repositorio ya tiene dos hitos en `dudosa` —Bar Oviedo
y Peña Los Amigos— que significan «el catálogo lo lista y no hay evidencia posterior de que abra».
Eso no es una disputa entre fuentes: es que nadie miró y además hay motivo para dudar. Se cuenta
como `sin_verificar` y el conteo de dudosos sigue viajando en su propia columna, como hasta ahora.

**Predicción declarada, para que la corrida pueda desmentirla:** con esta regla la vía B **se
desploma**. De las 220 fichas de hitos, en la ronda 2 sólo 4 tenían estado verificado. Aun cargando
toda la evidencia de vigencia de ronda 2 y ronda 3, espero **menos de 15 filas de 94 en `activo` o
`mixto`**, más de 60 en `sin_verificar`, y el 43 de la ronda 2 reemplazado por un número de una
cifra o de dos bajas. **Eso no es una pérdida de evidencia: es la evidencia que nunca hubo,
mostrada.** Si el número saliera parecido a 43, habría que sospechar del código, no celebrar.

---

## 3 · `via_D_estado`: cuatro valores, y el cuarto es el que importa

La vía D deja de ser `si`/`no` y pasa a:

| valor | qué significa | abre |
|---|---|---|
| `abierta` | hay enclave con delimitación cruzable y la fila lo toca | `si` |
| `medida_sin_enclave` | se buscó, hay comunidad, no hay oferta comercial estable | `no` — es hallazgo |
| `no_medida` | falta delimitación textual para poder cruzar | `pendiente` |
| `no_medible_con_este_instrumento` | economía migrante sin fachada contigua | `no` — es límite del método |

`no_medida` es el único de los cuatro que no es un resultado: es una laguna, y por eso queda
`pendiente` y no `no`.

**El quinto valor que trae el CSV y no estaba en la consigna:** `enclave_en_formacion` (E15,
venezolana y colombiana). No se pliega a ninguno de los cuatro porque no es ninguno de los cuatro:
es un `medida_sin_enclave` **con fecha de vencimiento**. Se carga como quinto valor, se declara
acá, y queda para que Diego lo confirme o lo pliegue.

**Cómo se le asigna un estado a una fila de la matriz.** Los estados viven en el enclave, no en la
fila. Se asigna así, y también con precedencia declarada:

    toca un enclave `abierta`                    → abierta
    toca sólo enclaves `medida_sin_enclave`      → medida_sin_enclave
    no toca ninguno, pero hay enclave sin poligonizar cuyo barrio declarado la incluye → no_medida
    ninguna de las anteriores                    → no_medida

Es decir: **por defecto una fila queda `no_medida`, no `cerrada`**. Lo que la ronda 2 escribía como
un `no` para 87 de 94 filas era, en casi todas, «no lo medimos». Los tres enclaves
`no_medible_con_este_instrumento` (E11 senegalesa, E13 japonesa, E14 china fuera de Belgrano) no
tienen geometría y por lo tanto **no pueden tocar ninguna fila**: viajan en la capa y en el texto
de límites del método, no en el cruce.

---

## 4 · Cómo se poligoniza E01, el Corredor Peruano del Abasto

Con el mismo procedimiento que los cuatro enclaves de la ronda 1 —callejero oficial del GCBA,
tramo entre dos cortes, buffer de 150 m declarado— y **sin ninguna excepción nueva**:

- **Eje primario:** `AGÜERO` entre `CORRIENTES AV.` y `GOMEZ, VALENTIN`, dentro de Balvanera.
- **Ejes secundarios:** `JEAN JAURES` y `ZELAYA` enteros dentro de Balvanera, porque la fuente los
  nombra **sin cabecera** («Jean Jaurès al 600», «Pasaje Zelaya»). Entran enteros y queda dicho,
  igual que Ramón Falcón e Ibarrola en Liniers. No se les inventa el corte.
- **Los anexos por establecimiento** —Guardia Vieja 3372 y Av. Corrientes 3564— **no entran al
  eje**. La propia fuente los da como anexos «por establecimiento, no por continuidad», y meterlos
  en el eje convertiría dos puntos sueltos en corredor.

`es_normativa = no` para las quince filas. **E01 no es normativo:** es una placa del 2 de junio de
2012 puesta por vecinos, comerciantes y el Consulado del Perú. No hay ley, ordenanza, resolución
ni declaración de interés. Si entra como norma, el Atlas afirma algo falso sobre el Estado.

**Dos métodos de construcción, y la columna dice cuál se usó.** Los quince enclaves no traen todos
la misma clase de delimitación, y forzarlos a una sola sería inventarles precisión:

- `eje+buffer` — uno o más tramos de calle más 150 m, como la ronda 1. Vale cuando la fuente da
  **calle con cabeceras** (E01, E02, E03, E04, E07) o **calle con rango de alturas** (E05 Once,
  E06 Flores), en cuyo caso las cabeceras son los dos extremos del rango geocodificados con USIG.
- `puntos+buffer` — la unión de 150 m alrededor de las **puertas documentadas**, sin eje. Vale
  para **E09 Retiro** y sólo para él: la fuente da seis direcciones y ninguna cabecera, y trazarle
  un eje sería dibujar la línea que la fuente no dibujó.

Los que no toman ninguno de los dos no reciben geometría: **E08 Charrúa** (tres bordes reales, sin
cuarto borde explícito, y además `medida_sin_enclave`), **E12 Palermo armenia** (el cuadrilátero es
una inferencia: hay institución armenia densa y hay gastronomía armenia, y nadie verificó que
coincidan) y los seis dispersos.

**Tres enclaves reciben geometría y NO computan vía D**, cada uno por su motivo escrito en la
propia fuente: **E06** porque tiene `n_grupos = 1` y de 2015 —una sola fuente no delimita al mismo
nivel que las demás—, **E08** por `medida_sin_enclave`, y **E12** por inferencia. La columna
`computa_via_D` los separa, y el conteo de vía D se hace sobre los que sí.

**E07 Liniers se carga sin el cuadrante.** El cuadrante José León Suárez / Montiel / Ramón Falcón
/ Ibarrola vino en la consigna, no en una fuente. La geometría de Liniers que ya está en la capa
se conserva **con la procedencia que tiene** —los tres tramos de la ronda 1— y el cuadrante queda
como `sin_verificar` en el campo de delimitación, sin cargarse.

---

## 5 · El cruce del IDECBA contra los locales bolivianos: qué haría falta para que se sostenga

El eje comercial oficial de Liniers es **Ramón Falcón 6801-7299**, y es una de las cuatro calles
del microcentro boliviano. La convergencia es llamativa. **Antes de mirar, se declara qué la
sostendría y qué la volvería coincidencia de calle:**

1. **Se sostiene** si los locales bolivianos documentados con altura caen **dentro del rango
   6801-7299** o a menos de una cuadra de él, y si la densidad de la base gastronómica en ese
   tramo es visiblemente mayor que en el resto de Ramón Falcón dentro de Liniers.
2. **Es coincidencia de calle** si los locales bolivianos con altura caen mayoritariamente
   **fuera** del tramo del IDECBA —por ejemplo en Ibarrola al 7100-7300, que es otra calle— y lo
   único que comparten es el nombre «Ramón Falcón» sin compartir el tramo.

El material disponible ya avisa cuál es el riesgo: de los cinco locales bolivianos con altura que
trae el CSV de enclaves, **cuatro son de Ibarrola y uno de José León Suárez. Ninguno es de Ramón
Falcón.** Si eso se confirma, la convergencia es **entre el eje del IDECBA y el polígono del
enclave**, no entre el eje y los locales, y hay que decirlo con esas palabras.

Se mide, además, la distancia de cada local boliviano al tramo del IDECBA, para que el resultado
sea un número y no una impresión.

---

## 6 · Núñez, el viaducto y las 12 altas

**El viaducto Mitre.** La cifra dura es: 58 locales inaugurados en tres tramos, 3,5 km de traza
desde Federico Lacroze y Libertador hasta Av. Monroe, 80.000 a 100.000 personas los fines de
semana (enero de 2025, sin actualización posterior). Se traza el corredor con el callejero y se
mide **qué encontró el clustering ahí**: cuántos polos de `polos_publicables.geojson` lo tocan,
cuántos locales de la base caen adentro y con qué densidad.

**Lo declarado antes de mirar:** el corredor del viaducto es una **traza ferroviaria elevada**, no
una calle comercial de fachada continua, y la base gastronómica se arma de fuentes que
georreferencian por puerta. Si el clustering no encontró nada ahí, la primera hipótesis no es que
no haya locales: es que **58 locales bajo un viaducto en 3,5 km dan 16,6 locales por km**, que a
60 m de umbral de continuidad no forma cadena. Se mide la continuidad antes de concluir.

**La cifra del viaducto no entra a ninguna columna de la matriz.** Es de una nota de prensa de
enero de 2025, mide inauguraciones acumuladas y no puertas abiertas hoy, y no es comparable con
`n_locales`, que sale de la base. Se reporta al lado, con su fecha.

**R18 a la luz de Z46.** No se redibuja nada: la geometría está congelada. Se mide **cuánto del
clúster coreano documentado cae dentro de R18 y cuánto afuera**, geocodificando por USIG las
direcciones que las dos fuentes nombran (Maipú 972, Paraguay 884, San Martín 687, Paraguay 831,
M.T. de Alvear 818, Carlos Pellegrini 1179). Si la mayoría cae afuera, R18 no es la zona: es su
borde, y eso es un insumo para una decisión de Diego, no una decisión de la corrida.

---

## 7 · La procedencia del catálogo de Notables

El PDF servido hoy bajo la URL de la Res. MCGC 3758/24 tiene **88 entradas** e incluye siete de
las doce altas del 3 de agosto de 2026, pero no El Greco ni Plaza Café. Fue reeditado sin cambiar
de número de resolución.

Se guarda **SHA-256 y fecha/hora de descarga** junto a cada archivo de catálogo que el repositorio
tenga en disco, en un `PROCEDENCIA_*.csv` con una fila por archivo. **No se vuelve a descargar el
PDF**: lo que se hashea es lo que ya está en disco, que es lo que las corridas usaron. Descargarlo
de nuevo hoy produciría un tercer contenido y perdería la trazabilidad de las corridas anteriores.

**No se localizó el número de resolución de las 12 altas ni su publicación en el Boletín Oficial.**
La fuente es sólo prensa —La Nación del 6 de agosto y Canal 26 del 3—. Queda asentado así en la
capa: las doce llevan `declaratoria_localizada = no`.

---

## 8 · Los cinco bordes, y qué se acepta como respuesta

Se resuelven con **dos consultas independientes a USIG**: `normalizar` para el punto y
`datos_utiles` para barrio y comuna del punto. Se acepta la respuesta de USIG por sobre el campo
`barrio`/`comuna` del catálogo y por sobre la atribución de la prensa, porque USIG es el callejero
oficial y el precedente de La Academia —consignada en Comuna 5 con domicilio en Av. Callao 368—
demuestra que el catálogo tiene errores propios en ese campo.

**Lo que USIG no resuelve y hay que decir igual:** «Núñez» y «Saavedra» son barrios oficiales y
USIG los distingue; **«Floresta» y «Flores» también**. Pero el uso periodístico de esos nombres no
coincide con el límite oficial, y una respuesta de USIG resuelve **la adscripción administrativa**,
no la disputa editorial. Si USIG dice Núñez y La Nación dice Saavedra, la ficha dice las dos cosas
con su fuente; lo que se corrige es el campo, no la cita.

---

## 9 · Cortes y convenciones que NO se mueven

Todo lo declarado en `LECTURA_PREVIA.md` y `LECTURA_PREVIA_RONDA_2.md` sigue vigente sin cambios:
60 m de continuidad, 50 % de pertenencia al soporte, 150 m de buffer de enclave, 150 m de distancia
para «el mismo local». La ronda 3 **no toca ninguno**. Las 23 columnas originales de la matriz se
vuelven a verificar contra el commit anterior y la corrida se corta si alguna cambió.

Los archivos de la ronda 2 —`seis_vias_94_filas.csv`, `hitos_capa_2026.csv`— **quedan intactos**.
La ronda 3 escribe al lado, con sufijo `_r3`, para que el delta se pueda medir contra un estado que
sigue en disco. Pisarlos borraría el punto de comparación, que es el mismo motivo por el que
`hitos_capa_unificada.csv` sigue ahí.
