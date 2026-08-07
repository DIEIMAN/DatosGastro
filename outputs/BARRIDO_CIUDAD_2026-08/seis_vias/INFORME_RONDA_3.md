# Ronda 3 · la vía B por presencia, los cuatro estados de la vía D y el norte

*7 de agosto de 2026 · DGDGAS · continúa `INFORME_RONDA_2.md`*

Lectura previa escrita antes de correr: `LECTURA_PREVIA_RONDA_3.md`. La del cruce ENTUR × vía E la
escribió Diego y está fechada antes: `desde_cowork/evidencia_2026/LECTURA_PREVIA_ENTUR_x_VIA_E.md`.
**Google Places: 0 requests.** USIG sí. Geometría, agrupamientos, fichas y cartografía: intactos.

---

## Lo primero, porque es una reversión

**P008 Barracas no está cerrada.** La ronda 2 la bajó porque su único hito —Los Laureles— figuraba
`vigencia_verificada = no`, y ese `no` era una lectura de una sola fuente. La Nación y Canal 26
publican el mismo 5 de agosto que cerró y que no cerró; El Tokio cerró en 2023 y reabrió en 2025
sin que ningún listado registrara ninguna de las dos cosas. **Los Laureles pasa a `en_disputa` y
P008 vuelve a quedar pendiente**, que no es abrir ni cerrar.

Y la regla que sale de ahí cambia el número más grande de la matriz.

---

## 1 · La vía B se desploma, y ese es el resultado

Con `via_B_soporte` y la regla de presencia, sobre las 92 filas con soporte:

| `via_B_soporte` | filas | ¿abre? |
|---|---:|---|
| `activo` | **7** | sí |
| `mixto` | 0 | sí |
| `en_disputa` | **1** | pendiente |
| `sin_verificar` | **36** | pendiente |
| `extinguido` | **0** | no |
| `sin_hitos` | **48** | no |

**El delta: 43 de 94 → 7 de 94.** Y 37 filas quedan pendientes.

Diego esperaba que `sin_verificar` fuera la mayoría. **Lo es, pero hay que decir de qué.** De las
92 filas con soporte, 48 —el 52 %— no tienen ningún hito adentro: no son `sin_verificar`, son
`sin_hitos`, y ahí no hay nada que verificar. Entre las 44 filas **que sí tienen hitos**,
`sin_verificar` son 36: el **82 %**. Esa es la cifra que corresponde a la expectativa, y sí, está
bien que lo sea.

Las 43 de la ronda 2 no se perdieron: **nunca existieron**. La regla vieja contaba como «abre»
todo hito que no estuviera verificado cerrado, es decir 212 hitos que nadie miró.

**Las 7 que abren, con el hito que las abre:** Avenida Corrientes (Los Galgos), Federico Lacroze /
Libertador y Colegiales (Bar Conde), Retiro (Florería Atlántico), P012 Mataderos (El Cedrón),
P025-2 Monte Castro (El Fortín), P034 Monte Castro (El Tokio).

**`extinguido` sale en cero, y no porque no haya cierres.** El orden de precedencia declarado pone
`extinguido` último: sólo se aplica cuando **todos** los hitos de la fila están verificados
cerrados. The New Brighton está cerrado y verificado, pero la fila que lo contiene tiene además
hitos sin verificar, y uno de esos puede estar abierto. Con 8 hitos verificados abiertos y 1
cerrado sobre 220, ninguna fila llega a tener todo su bloque verificado. **La capa histórica que la
decisión pide existe —está en `via_B_cerrados_cuales`— pero todavía no hay ninguna fila que sea
sólo historia.**

**Lo que no se marcó, que también es una decisión.** Los cuatro Bares Notables de Retiro y Casa
Watson llegaron etiquetados «dudosos». El motivo que traen —«el catálogo no acredita apertura»—
vale para los 90 y es la definición misma de `sin_verificar`. `dudosa` se reservó para donde hay un
motivo positivo para dudar: Bar Oviedo (sin observación de campo desde 2013) y El Faro (única
fuente, 2011).

**Y una consecuencia sobre las 22 publicadas:** R03 San Telmo queda con **cero vías abiertas**. No
porque se haya descubierto algo sobre San Telmo, sino porque sus vías A, C y F ya daban `no` desde
la ronda 2 —el Mercado de San Telmo sigue 64 m afuera de R03— y sus vías B y D están pendientes.
Es el estado de nuestra verificación, no un resultado sobre el territorio, y hay que leerlo así.

---

## 2 · La vía D pasa a cuatro estados, y el Abasto se puede medir

| estado | filas de 92 |
|---|---:|
| `abierta` | **12** |
| `no_medida` | **80** |

**El delta: 7 abiertas → 12.** Y lo más importante no es el 12: es que **las 87 filas que la ronda
2 escribía como `no` ahora dicen `no_medida`**, que es lo que eran. Diego tenía razón y la
corrección va más lejos de lo que él mismo pidió.

De los 15 enclaves, **8 recibieron geometría y 7 computan**. Los tres estados negativos no son la
misma cosa y ahora la capa los distingue:

- `medida_sin_enclave` — **E08 Charrúa**, E10 paraguaya, E14 china fuera de Belgrano. Se buscó, hay
  comunidad, no hay oferta comercial estable. **Es un hallazgo, no una laguna.**
- `no_medible_con_este_instrumento` — **E11 senegalesa** y **E13 japonesa**.
- `enclave_en_formacion` — **E15 venezolana y colombiana.** Es un quinto valor que trae el CSV y la
  consigna no nombra. No se plegó a ninguno de los cuatro: es un `medida_sin_enclave` **con fecha de
  vencimiento**, y queda para que Diego lo confirme o lo pliegue.

**E08 Charrúa tiene el mejor perímetro físico del Atlas y aun así no se poligonizó.** Le falta el
cuarto borde, y sobre todo: darle área sugeriría que hay algo adentro que medir.

### E01 · el Corredor Peruano del Abasto

**3 tramos, 506 m de eje, 28,8 ha.** Agüero entre Av. Corrientes y Valentín Gómez (117 m), Jean
Jaurès al 600 (108 m), Pasaje Zelaya entero (281 m). Los anexos por establecimiento —Guardia Vieja
3372 y Av. Corrientes 3564— **no entraron al eje**: la fuente los da como anexos, no como
continuidad, y meterlos habría convertido dos puntos sueltos en corredor.

**PG013 Abasto pasa de `cerrada` a `abierta` por E01 y E05.** Era lo que faltaba.

**`es_normativa = no`, y para E01 con nota propia.** «Corredor Peruano» es una **placa** del 2 de
junio de 2012 puesta por vecinos, comerciantes y el Consulado del Perú. No hay ley, ordenanza,
resolución ni declaración de interés. Y la cuadra 400 de Agüero está en recambio asiático desde
2024: la delimitación de 2012 y la de 2025 describen realidades distintas.

**Una corrección de lo que yo mismo había declarado.** La lectura previa dijo que Jean Jaurès y
Zelaya entraban **enteras** porque la fuente las nombra «sin cabecera». Para Zelaya es cierto. Para
Jean Jaurès no: la fuente dice «al 600», que es una cuadra. Entera daba 1.431 m de eje y llevaba
E01 a **66,3 ha**; con la cuadra que la fuente nombra da **28,8**. La regla «sin cabecera entra
entera» existe para no inventar cortes, no para ignorar los que la fuente da, y aplicada así
inflaba el enclave — que es el sesgo que hace abrir vía D de más.

---

## 3 · Un bicho en la geometría de Liniers, encontrado por accidente

**El callejero oficial tiene dos Ramón Falcón.**

| nombre en el callejero | segmentos en Liniers | largo | alturas |
|---|---:|---:|---|
| `FALCON, RAMON L.,CNEL.` | 21 | 1.728 m | 0–7300 |
| `FALCON, RAMON L.,CNEL. AV.` | 1 | 128 m | 5902–6000 |

**La receta del enclave boliviano de la ronda 1 usaba la segunda.** El Mercado Andino, los locales
de Ibarrola al 7100-7300 y el eje comercial del IDECBA (6801-7299) están todos sobre la primera.
E07 estaba puesto **900 números al oeste** de donde está el enclave. Queda corregido en
`enclaves_ronda_3.py`: el eje pasa de 3.381 m a **4.981 m** y el enclave de 113,5 ha a **131,7 ha**,
y —esto es lo que importa— **ahora incluye la calle donde está el Mercado Andino**, que antes no.

### ¿La convergencia del IDECBA se sostiene?

**No como se la venía contando.** Los cinco locales bolivianos con altura que trae el material:

| local | dirección | distancia al eje del IDECBA |
|---|---|---:|
| El Conejo | José León Suárez 216 | 176 m |
| Miriam | Ibarrola 7184 | 152 m |
| Pollo Copacabana | Ibarrola 7276 | 144 m |
| Pollo Copacabana | Ibarrola 7291 | 136 m |
| Rico Pollo | Ibarrola 7193 | 143 m |

**Cero de cinco están sobre Ramón Falcón.** Tres de cinco caen dentro del buffer de 150 m. Es lo
que la lectura previa dijo que iba a pasar, escrito antes de medirlo.

Entonces: **la convergencia es de área, no de puerta.** Dos instrumentos ciegos entre sí siguen
señalando el mismo lugar —eso vale— pero decirla como convergencia entre el eje comercial y los
locales bolivianos la sobrevende, porque ningún local boliviano documentado está sobre ese eje.

Lo que sí se sostiene, y con número: **el tramo del IDECBA tiene 189 locales por km de la base
contra 58 en el resto de Ramón Falcón dentro de Liniers.** El eje comercial oficial marca un tramo
que es tres veces más denso, y ese tramo es el del enclave.

Limitación que no se arregla midiendo: los cinco locales son de 2016 y ninguno tiene vigencia
verificada. Se comparó un eje relevado en 2026 contra puertas publicadas hace diez años.

---

## 4 · Núñez · la predicción de la lectura previa se cayó

**El callejero oficial marca el viaducto solo.** La columna `tipo_ffcc` distingue «Tren Elevado -
Paso a Nivel Sin Vías»: hay 18 cruces así en Colegiales, Belgrano y Núñez, que son **dos ramales**,
y se separan en componentes conexas — 13 y dos pares — **con el mismo resultado entre 300 y 500 m**,
así que el umbral no está sosteniendo la partición.

La traza reconstruida mide **1,43 km**, no 3,5. La fuente empieza el paseo en Federico Lacroze y
Libertador, que es Colegiales, y los cruces marcados como tren elevado no llegan tan al sur. **Lo
que se midió es el tramo Belgrano–Núñez del viaducto**, y todo lo que sigue se lee sobre ese tramo.

| | |
|---|---:|
| corredor, 150 m por lado | 49,0 ha |
| locales de la base adentro | **245** |
| densidad | 5,00 loc/ha · 171 por km |
| distancia media al vecino más cercano | 14 m |
| pares a ≤60 m | 1.702 |

**Qué encontró el clustering ahí: dos polos, con el 85 % y el 95 % de sus locales dentro del
corredor.** No son polos que rozan el corredor: son polos que **son** el corredor.

**La lectura previa había anticipado lo contrario** —que 16,6 locales por km no forman cadena a
60 m— y **esa predicción se cayó**. La razón de la diferencia importa: los 58 locales son los
**inaugurados** bajo el viaducto; la base cuenta toda la gastronomía del corredor, incluida la que
ya estaba en las calles que el viaducto atraviesa. Son dos universos distintos y el más grande no
valida al más chico. **La cifra de prensa sigue sin entrar a ninguna columna.**

### Las seis del norte, contra la densidad que mide la base

| id | zona | veredicto documental | locales | ha | loc/ha |
|---|---|---|---:|---:|---:|
| Z41 | Núñez | ENTRA | 494 | 450 | 1,10 |
| Z42 | Coghlan | ENTRA | 108 | 128 | **0,84** |
| Z43 | Colegiales | ENTRA | 441 | 229 | 1,93 |
| Z44 | Villa Ortúzar | ENTRA | 201 | 185 | 1,08 |
| Z45 | Belgrano R y Barrancas | NO ENTRA | — | — | sin barrio homónimo |
| Z46 | Retiro | ENTRA | 598 | 452 | 1,32 |

El número es sobre el barrio entero, que es grueso: **sirve para descartar, no para confirmar**.
**Coghlan es el más flaco de los cinco**, consistente con que su propia ficha lo marque como el
caso más expuesto —dos vías, la C dependiente de un solo local relevado por la misma fuente que
sostiene media vía E—.

---

## 5 · R18 · la hipótesis no se sostiene, y con este material tampoco se descarta del todo

De las 7 puertas del clúster coreano-asiático que las dos fuentes nombran con dirección, **5 caen
dentro de R18**. Kimchi Garden (San Martín 687) queda a 83 m y Carlos Pellegrini 1179 a 56 m, los
dos adentro de R12.

**La envolvente convexa del clúster mide 11,1 ha contra las 48,4 ha de R18, y el 98 % de ella cae
adentro.** Es decir: R18 no se queda corta. **Es cuatro veces más grande que el clúster que la
justifica**, y la hipótesis de que fuera el borde sur de un polo de Retiro más grande **no se
sostiene con este material**.

**Pero el material es chico y hay que decirlo.** La Nación del 10 de mayo de 2026 habla de un
direccionario de **25** restaurantes coreanos y acá hay **7** puertas con dirección publicada. Si
las 25 se extienden al norte o al oeste, el número cambia. Con 7 de 25 la pregunta no se cierra:
se acota.

**Lo que sí cambia hoy:** con E09 cargado, **R18 pasa a abrir vía D**. Antes decía `no`.

---

## 6 · ENTUR × vía E · H1 cae dentro del rango predicho y aun así no hay señal

| | |
|---|---|
| **H1** · rho de Spearman | **+0,252** (predicho 0,20–0,55) → **CAE DENTRO** |
| **control (a)** · razón vs `n_locales` | +0,210 → **PASA** (correlaciona más con la vía E que con el tamaño) |
| **control (b)** · permutación, 1.000 iteraciones, semilla 20260807 | percentil 95 del nulo = **+0,361** · p empírico = **0,119** → **FALLA** |
| **H2** | **no se cumple** |

**El observado no supera el percentil 95 del nulo.** Con 22 zonas, un rho de 0,252 es
indistinguible del azar: uno de cada ocho barajados da un valor igual o mayor. Éste es exactamente
el control que faltó en la ablación anterior, y esta vez sirvió para desmentir, que es para lo que
está.

**H2, por cuadrante:**

| cuadrante | zonas | mediana del año e1–e4 |
|---|---:|---:|
| razón alta + vía E abierta | 9 | 2024 |
| razón alta + vía E cerrada (*declive*) | 2 | **2026** |
| razón baja + vía E abierta (*emergente*) | 7 | **2025** ✓ |
| razón baja + vía E cerrada | 4 | 2025 |

El cuadrante **emergente cumple** —2025, y la predicción pedía 2023 o posterior—. El de **declive
no**: pedía anterior a 2021 y da 2026. Y ahí la mediana esconde el detalle: son **dos zonas**, y
una de ellas, R18, no tiene ninguna fuente admisible —lo cual cumple la parte «o directamente
inexistente» de la predicción—, mientras la otra, **R12 Centro, que es el caso que hizo formular la
hipótesis, tiene su única fuente admisible fechada en abril de 2026**. El cuadrante se sostiene
sobre dos zonas, una sin fuente. No alcanza para nada, ni a favor ni en contra.

**Las zonas nombradas de antemano: 8 aciertos de 11.** Fallan R04, R09 y R19, y no fallan igual:

- **R09 y R19** caen del lado «alta» por **0,004 y 0,017** sobre una mediana. Con terciles, con
  media o con cualquier otro criterio razonable cambian de cuadrante. **El corte es arbitrario y
  tres de las once predicciones dependen de él.** Eso no se arregla eligiendo otro corte: se dice.
- **R04 Puerto Madero** falla de una manera que la propia lectura previa había previsto: la
  predicción decía «vía E que abre pero con toda su evidencia anterior a 2024», y su mediana da
  **2022**. Acierta en lo que predijo sobre las fechas y falla en la etiqueta binaria, porque la
  etiqueta no distingue «abierta» de «abierta con material viejo». El error está en el instrumento
  de clasificación, no en la predicción.
- **R14 Boedo** sale con razón **baja**. La hipótesis del tercer tipo —turístico sin ser
  gastronómico— no hizo falta: el ENTUR resulta más gastronómico de lo que su nombre sugiere.

**Qué se hace con esto: la razón ENTUR/base NO entra a la matriz**, ni como vía ni como columna de
contexto. Se registra como dato descriptivo del ENTUR, con su número, y queda escrito que se probó
y no funcionó — como se hizo con el índice de Rand ajustado que dio 0,391.

**Una decisión de fecha que esta ronda obligó a tomar.** Varias fuentes vienen como «El Cronista
09/11/2021 act. 12/09/2025». Se tomó **2021**, no 2025, por lo mismo que Diego señala del Mercado de
los Carruajes: la fecha de actualización de una nota no es la fecha de verificación de sus datos.
Usar la de actualización habría inflado la añada de exactamente las zonas que H2 quería separar.

---

## 7 · La procedencia del catálogo · circulan tres contenidos, no dos

`hitos/PROCEDENCIA_CATALOGOS.csv` guarda SHA-256, tamaño y fecha de cada archivo de catálogo que ya
está en disco. **No se volvió a descargar nada**: bajar el PDF hoy daría un tercer contenido y
perdería la trazabilidad de las corridas que usaron el que está.

Y el hash trajo algo que el hash solo no muestra:

**El PDF que el repositorio tiene en disco desde el 3 de agosto de 2026 trae 90 entradas y contiene
las doce altas — las doce, incluidos El Greco y Plaza Café.** Su hoja de firmas está fechada el
**26 de febrero de 2026**, seis meses antes de la fecha de las altas, y su identificador propio es
**IF-2026-10314379-GCABA-DGPMYCH**.

| contenido | entradas | de las 12 altas |
|---|---:|---:|
| el que está en disco (firmado 26/02/2026) | **90** | **12** |
| el que la URL de la Res. 3758/24 sirve hoy | 88 | 7 |
| GCBA / Wikidata (ya cruzadas en ronda 2) | 84 / 95 | — |

**Y una consecuencia que no es de forma:** si un documento firmado en febrero de 2026 ya lista los
doce, entonces «alta del 3 de agosto» no describe el acto declaratorio. Puede ser la fecha de
difusión de un catálogo ya consolidado. **No se afirma cuál de las dos cosas es**: se afirma que la
prensa y el documento no dicen lo mismo, y que **la resolución que declararía las altas sigue sin
localizarse**. Las doce llevan `declaratoria_localizada = «no · sólo prensa»`.

Nota: el «1225/2026» del nombre del archivo es **nuestro**, no del documento — ese número no
aparece en su texto. La procedencia se cita por el GEDO.

**El síntoma de La Ópera, con el nombre corregido.** La prosa de la ronda 3 §6 nombra «La Ópera
(Av. Corrientes 4101, Almagro)». En el CSV que la acompaña, Av. Corrientes 4101 / Almagro es **La
Orquídea**, y La Ópera figura aparte en Av. Corrientes 1799 / San Nicolás. La capa tiene las dos.
El síntoma de la reedición es real; el nombre con el que se lo cita es el equivocado, y **no da lo
mismo porque cambia la referencia que toca**: 4101 toca Z37 Almagro y 1799 toca R02 / R12.

**Segunda discrepancia, menor:** la lista de altas da Boca a Boca en Av. Benito Pérez Galdós **207**
y la capa lo tiene en **201**.

---

## 8 · Los bordes · USIG contesta, y una pregunta estaba mal planteada

El control pasó primero: **La Academia, Av. Callao 368 → Balvanera, Comuna 3.** El catálogo la
consigna en Comuna 5. El procedimiento distingue.

| establecimiento | dirección | USIG | qué decide |
|---|---|---|---|
| **La Escuela** | Manuela Pedraza 2803 | **Núñez, Comuna 13** | la única vía B de Núñez **cuenta para Núñez**; el catálogo tenía razón y La Nación no |
| **La Mezzetta** | Av. Álvarez Thomas 1321 | **Villa Ortúzar, Comuna 15** | la Pizzería Emblemática cuenta para **Z44**, no para R09 |
| Vereda Adentro | 11 de Septiembre 3201 | **Núñez, Comuna 13** | Ohlalá tenía razón, El Cronista no |
| Corte Comedor | Av. Olazábal 1391 | **Belgrano, Comuna 13** | **Time Out se equivoca**: la altura mandaba |

**Y el quinto no era «Flores o Floresta».** Las tres direcciones que quedaban de la ronda anterior
caen en **tres barrios distintos y tres comunas distintas**:

- Av. Avellaneda 3069 → **Flores, Comuna 7**
- Cuenca 954 → **Villa Santa Rita, Comuna 11**
- Campana 685 → **Floresta, Comuna 10**

El enclave sefardí de Flores (E06) no está sobre un límite entre dos barrios: **está repartido en
tres**. La pregunta «¿Flores o Floresta?» presuponía una dicotomía que el callejero no sostiene, y
es una razón más para poligonizar E06 por altura de puerta y no por nombre de barrio — que es
exactamente lo que la propia ficha de E06 recomienda.

Ruperto Godoy **700 no resuelve en USIG** (el pasaje arranca en el 712); el 800 sí, y da Flores,
Comuna 7. Queda declarado, no supuesto.

---

## 9 · Lo que cambió de estado en la capa de hitos

10 hitos movieron de estado respecto de la ronda 2: 8 a `si` (El Tokio, El Fortín, El Buzón, El
Cedrón, Bar Conde, Los Galgos, Florería Atlántico, más Casa Burgio que ya estaba), 1 a `no` (The New
Brighton), 1 a `en_disputa` (Los Laureles) y El Faro a `dudosa`.

Tres no se pudieron marcar porque **no están en la capa**: Casa Bogotá, Casa Madrilia y el **Mercado
de los Carruajes**. Los tres quedan declarados, no inventados. El de los Carruajes importa: cerró a
fines de abril de 2025, era el único mercado gastronómico de Retiro, y El Cronista —en su versión
«actualizada al 24/09/2025»— sigue recomendando dos restaurantes adentro.

Dos hitos llevan `continuidad_ininterrumpida = no` con su motivo: **El Tokio** (cerró 2023, reabrió
2025) y **Casa Bogotá** (la trayectoria es del edificio de 1914; el restaurante abrió en 2025). Es
el caso que la decisión describe: `vigencia = sí` y `continuidad = no`, los dos campos juntos.

---

## Archivos

| qué | dónde |
|---|---|
| lectura previa (antes de correr) | `seis_vias/LECTURA_PREVIA_RONDA_3.md` |
| capa de hitos con cinco valores | `hitos/hitos_capa_2026_r3.csv` / `.geojson` |
| procedencia con SHA-256 | `hitos/PROCEDENCIA_CATALOGOS.csv` |
| los 15 enclaves | `seis_vias/enclaves_comunitarios_r3.csv` / `.geojson` |
| matriz recomputada | `seis_vias/seis_vias_94_filas_r3.csv`, `seis_vias_22_zonas_r3.csv` |
| bordes resueltos | `seis_vias/bordes_usig_ronda_3.csv` |
| Liniers, Núñez, R18 | `seis_vias/liniers_bolivianos_vs_idecba.csv`, `nunez_corredor_viaducto.geojson`, `retiro_cluster_coreano.csv` |
| ENTUR × vía E | `seis_vias/entur_x_via_E.csv`, `entur_x_via_E_estadisticos.csv` |
| corridas completas | `hitos/VIGENCIA_RONDA_3.txt`, `seis_vias/ENCLAVES_R3.txt`, `SEIS_VIAS_R3.txt`, `NORTE_Y_LINIERS_R3.txt`, `ENTUR_x_VIA_E.txt`, `BORDES_USIG.txt` |

Scripts: `hitos_ronda_3_vigencia.py`, `enclaves_ronda_3.py`, `polos_seis_vias_r3.py`,
`norte_y_liniers_ronda_3.py`, `entur_x_via_e.py`, `usig_bordes_ronda_3.py`. Los archivos de la
ronda 2 quedan intactos, con sufijo distinto, para que el delta se pueda medir contra un estado
que sigue en disco.

---

## Lo que espera decisión

1. **El quinto valor de la vía D** (`enclave_en_formacion`, E15): confirmarlo o plegarlo.
2. **El sexto valor de la vía B** (`sin_hitos`): confirmarlo. Son 48 de 92 filas y los cinco valores
   de la decisión no lo cubren.
3. **E07 Liniers reconstruido** sobre la Ramón Falcón correcta: revisar el polígono nuevo, y decidir
   si se recuperan las cinco fuentes accesibles que cerrarían el cuadrante.
4. **R18**: redibujar o no. El número dice que R18 contiene al clúster documentado y es cuatro veces
   más grande; las 25 direcciones del direccionario de La Nación cambiarían la cuenta.
5. **R03 San Telmo con cero vías abiertas**, y el Mercado de San Telmo que sigue 64 m afuera.
6. **La resolución de las 12 altas**, que sigue sin localizarse, contra un anexo firmado en febrero
   de 2026 que ya las lista.
7. **Verificar vigencia sobre los 207 `sin_verificar`**, priorizando los hitos únicos de su fila.
8. **E06 por altura de puerta**, ahora que se sabe que cruza tres barrios y tres comunas.
9. Sigue de antes: los 48 ejes comerciales a geometría, las 39 filas que superponen territorio,
   `Ultramarinos` sin geocodificar, `Mercado San Nicolás` y `Smart Plaza Parque Patricios` sin
   dirección, el saliente N–NE, R01 en la V3 con el 47,7 %, la cláusula ODbL, el visto de Patricia,
   Foursquare y el documento extenso del método.
