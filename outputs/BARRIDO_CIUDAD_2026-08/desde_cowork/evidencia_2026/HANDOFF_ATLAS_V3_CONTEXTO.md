# Atlas de Referencias Gastronómicas de la Ciudad de Buenos Aires · V3
# Contexto para retomar el trabajo

*Documento de traspaso · 8 de agosto de 2026*

> **Leé esto primero y entero.** Está escrito para que una sesión nueva pueda retomar sin volver a deducir nada. Todo lo que dice acá está verificado contra archivos, salvo lo que está marcado como pendiente o dudoso.

---

# 1 · Quién hace qué

**Diego Alemán**, analista de datos de la **Dirección General de Desarrollo Gastronómico (DGDGAS), GCBA**. Es el que decide, el que conoce a la audiencia y el que puede verificar en la calle y en redes sociales.

**Vos (Cowork, fuera del repositorio)**: investigación documental, criterio, redacción, auditoría y síntesis. **No tenés acceso de lectura al repositorio** salvo por el puente de archivos.

**El repositorio (Claude Code adentro de `C:\proyectos\Gastronomia\DataGastro`)**: código, geometría, corridas, datos y git. Diego pega tus bloques en esa sesión y te trae los informes de vuelta.

**Cómo se entregan los archivos.** Se escriben en el workspace, se mandan con `SendUserFile` y **se commitean con `device_commit_files`** a:

```
C:\proyectos\Gastronomia\DataGastro\outputs\BARRIDO_CIUDAD_2026-08\desde_cowork\evidencia_2026\
```

**Mandar por chat no los pone en el repositorio.** Ya pasó: diez archivos se dieron por entregados y no estaban.

---

# 2 · Restricciones que puso Diego · no se negocian

- **«Me tenés que dar eso al final siempre»** — el bloque pegable para el repositorio va **último** en cada mensaje.
- **«No podemos pedir fuentes internas ya te dije»** — nada que no sea públicamente accesible. Una fuente cerrada se declara como puerta cerrada y se sigue.
- **«No hace falta que me las devuelvas acá en el chat, mientras las guardes en el repo está todo bien»**.
- **Nunca mencionar la versión anterior como «Atlas V2»** en el documento. Se dice «la versión anterior de este atlas».
- **Las 22 referencias publicadas sólo se amplían, nunca se redefinen ni se dan de baja.**
- **«Nunca descartes nada sin antes detallarme bien qué sería.»**
- **Google Places publica sólo a nivel agregado**: no salen puntos, ni `place_id`, ni nombres.

---

# 3 · Qué es el objeto

**Definición adoptada, y gobierna todo:**

> Un polo gastronómico es una **concentración espacial reconocible de establecimientos, actividades o referentes gastronómicos que conforma una identidad territorial propia** — por densidad y continuidad, trayectoria histórica, mercados o instituciones emblemáticas, especialización culinaria, relaciones comunitarias, reconocimiento externo, o capacidad de funcionar como destino.
>
> **No es necesariamente homogéneo ni está acotado administrativamente.** Puede ser un núcleo compacto, un corredor, una sucesión de centralidades o un sistema de subpolos.
> **Su delimitación responde a evidencia territorial y gastronómica, no a límites de barrio.**

## Las seis vías de entrada — se entra por **cualquiera**

| vía | qué mide |
|---|---|
| **A** · densidad y continuidad | locales por hectárea, continuidad a 20/40/60/80/120 m |
| **B** · trayectoria e instituciones | Bares Notables, Restaurantes Icónicos, Pizzerías Emblemáticas, protección patrimonial |
| **C** · mercados y centralidades | ver el criterio de abajo — es la más discutida |
| **D** · comunidades y especialización | enclaves de colectividad con oferta propia |
| **E** · reconocimiento externo | prensa, guías y operadores que tratan a la zona como destino |
| **F** · corredor | **la forma, no el tamaño**: eje y no núcleo |

## Las dos familias — la decisión de criterio más importante del proyecto

**Vías geométricas (A, C, F)** — se miden **sobre el polígono**, fila por fila.

**Vías documentales (B, D, E)** — se miden **sobre la zona** y las filas las heredan, con dos campos: `zona_via_X` + `via_X_modo` ∈ {`propia`, `heredada`, `requiere_cruce`}, **guardadas como referencia y no como valor copiado**.

**El caso que la originó:** Almagro tiene cinco Bares Notables sobre tres ejes en un barrio de 405 ha. El fragmento que el clustering detectó ahí mide **5,7 ha — el 1,4 % del barrio — y no contiene ninguno de los cinco.** Medir «¿este polígono contiene un bar notable?» no mide la trayectoria de la zona: mide si el algoritmo acertó a caer encima de un bar.

**La herencia no vale hacia arriba**: que Almagro tenga cinco Notables no convierte al fragmento en un polo notable.

## La vía C, que es la que más problemas dio

**Criterio vigente, fijado el 08/08/2026 (decisión 23):**

> **La vía C se abre por centralidad, no por concentración de oferta bajo un techo.**
> **La prueba: ¿el objeto organiza su entorno, o fue puesto en él?**

Con eso: Mercado Bonpland, Mercado de Belgrano y **Mercado del Progreso mantienen** —el del Progreso es privado, pero es de 1889 y organiza Caballito—. **El Patio Costanera Norte no.** Público/privado dejó de ser la variable.

Estado: **abre en 2 de las 94 filas y 3 de las 22 zonas.** Es la vía que menos rinde por discusión que genera. R07 y PG009 perdieron la C y **se sostienen por A y F**, así que no hubo bajas.

## Las cuatro familias morfológicas

**Polo** (núcleo compacto) · **polo multiparte o con subzonas** (los vacíos son parte de la figura) · **eje o corredor** · **referencia dispersa**. Más una quinta que apareció midiendo: **sistema de subpolos**, que es la salida de Chacagiales y probablemente la de Palermo.

> **Que una referencia dispersa no produzca una concentración compacta no la refuta. La confirma.**

---

# 4 · Las escalas de evidencia

## Vigencia

| nivel | qué es |
|---|---|
| **v1** | prensa con reporteo propio, ≤ 90 días |
| **v2** | publicación fechada en canal propio del local, ≤ 60 días |
| **v2b** | `business_status` de Places **con fecha de consulta** — ver la advertencia de la sección 8 |
| **v3** | reseña de usuario con fecha visible, ≤ 90 días |
| **v3b** | check-in de consumo fechado (Untappd) — **decisión tomada: sí computa** |
| **v4** | listado o guía fechada, ≤ 180 días |
| **v5** | evento concreto fechado **y nombrado por el organizador** |

**Veredictos:** `verificado_abierto` (v1–v3b) · `probablemente_abierto` (v4 o v5 solos) · `dudoso` · `cerrado` · `en_disputa`. Más `en_riesgo` para contingencia sin cierre consumado.

**Reglas duras:**
- **La evidencia negativa se busca, no se espera.** Un veredicto de apertura sin buscar evidencia en contra no está verificado: está sin refutar.
- **Un acto jurídico no es un hecho operativo** (FD-20). Quiebra, concurso, condena laboral, contrato vencido, inmueble en venta: van al campo `alerta_juridica`, **no tocan el veredicto**.
- **El catálogo de Bares Notables no acredita apertura ni cierre.** Ningún padrón lo hace (FD-10).
- **Toda verificación vence.** Cada afirmación lleva su fecha.

## Vía E · reconocimiento externo

**e1** guía editorial internacional · **e2** prensa nacional o extranjera que trata **a la zona** · **e3** ranking con método declarado · **e4** guía turística comercial · **e5** food tour comercial.

**Abre con dos grupos de independencia entre e1 y e4, o con uno solo si es e1. Un e5 solo no abre.**

- **La comunicación del GCBA no cuenta** — parte interesada. Pero **una fuente oficial no acredita reconocimiento y sí acredita medición**: la estadística del IDECBA va a las vías A y F y a la capa de estado, nunca a la E.
- **Michelin distingue restaurantes, no barrios** → eso es vía B.
- Se cuentan **grupos de independencia, no notas** (R6).
- **Reporteo a nivel programa acredita v4, no v1** (decisión tomada).

## Estados de soporte

`via_B_soporte` ∈ {`activo`, `mixto`, `extinguido`, `en_disputa`, `sin_verificar`, `sin_hitos`}
Vía D ∈ {`abierta`, `medida_sin_enclave`, `no_medida`, `no_medible_con_este_instrumento`}
Capa de memoria ∈ {`extinguido`, `extinguido con reapertura anunciada`, `mutado`, `interrumpido y recuperado` — **este último NO va en la capa**}

---

# 5 · Los números que se pueden usar, y los que no

## Los tres universos

| universo | ¿se suma? |
|---|---|
| **los 124 polígonos publicables** | **Sí** — son disjuntos, solapamiento medido **0,0 %** |
| **la matriz de 94 filas** | **NUNCA** — se pisa por diseño, es un instrumento de comparación |
| **la capa de hitos** | Sí, deduplicando **por dirección** |

> **La cifra publicable: 12.688 locales en 3.128,5 hectáreas — el 53 % de la gastronomía relevada en el 15 % de la superficie.** Sobre una base de 23.981 locales y ~20.300 ha de la Ciudad. **Calculada sobre la unión.**
>
> **Sumar la matriz de 94 da 16.499 locales y 7.731 ha. Las dos cifras están infladas.** Flores solo se cuenta siete veces.

## El catálogo de Bares Notables · **cerrado al 100 %**

Resolución MCGC 1225/26, consolidado firmado el **3 de agosto de 2026**, 90 entradas.

| | |
|---|---:|
| **abiertos** | **86** |
| abierto en quiebra — The New Brighton, Sarmiento 645 | 1 |
| en riesgo — Esquina Homero Manzi, orden 55 | 1 |
| **cerrados** | **2** |
| **operando** | **88 de 90 · 97,8 %** |

Los dos cerrados: **Plaza Bar**, Florida 1005, desde abril de 2017 — **nueve años**, en un padrón firmado este mes. Y **La Buena Medida**, Suárez 101, desde octubre de 2025.

**La lectura correcta es «dos sobre noventa», no «el catálogo arrastra cerrados».** Esa generalización salió de once casos elegidos por sospechosos y leídos como muestra al azar.

## La capa de hitos

`hitos/hitos_capa_2026_r11.csv` — **225 × 21**, con los 90 del catálogo cargados. Emparejados **por dirección**: 87 exactas y 3 variantes triviales; **por nombre habrían fallado 22.**

**Campo `citable_en_documento`: 32 citables con fecha propia, 58 no.** La regla de redacción:

> Una ficha **puede** afirmar el estado de la zona sin fecha por establecimiento: *«los cinco referentes de la zona están verificados abiertos al 8 de agosto de 2026»*.
> **Sólo cuando el documento hace una afirmación sobre un establecimiento en particular hace falta su fecha propia.**

## El IDECBA · Relevamiento de Ejes Comerciales

Instituto de Estadística y Censos de la Ciudad. **48 ejes vigentes**, relevamiento visual a pie, cuatrimestral, público y descargable. Bajado por el repositorio en la ronda 10: `ronda_10/idecba_densidad_48_ejes.csv`.

> **⚠️ El informe en PDF enumera 53 ejes y la serie vigente trae 48. No es diferencia de fecha: es otro universo (FD-23). LA AUTORIDAD ES LA SERIE, NUNCA EL PDF.**
> **«Microcentro» no existe entre los 48.** Salieron también Palermo Hollywood, Cañitas, Nazca, Murillo y Jujuy; entró Lavalle.

**Lo que sí se sostiene, medido sobre los 48:** **18 de los 90 Notables caen adentro de un eje relevado — 17 abiertos, 1 en riesgo, 0 cerrados — mientras los 48 ejes pierden 1,6 puntos de ocupación.** Con la salvedad de que **ninguno de los tres casos graves cae adentro de un eje** (Plaza Bar está en Florida 1005 y el eje Florida termina en el 999).

**Su método excluye galerías, shoppings, ferias y puestos informales**, y sólo cuenta locales con frente a la calle: es el sesgo espejo del nuestro. Y **su densidad es locales por cuadra sobre un eje lineal**, mientras la vía A es locales por hectárea sobre un polígono: **habilita calibración, no equivalencia.**

## Otras cifras vivas

- **41 polos en 15 comunas** — 21 referencias publicadas (3 ampliadas) + 20 zonas incorporadas. 7 descartadas con argumento, 5 pendientes de límites.
- **124 concentraciones detectadas** por el clustering; mínimo de 40 locales, que **no se movió** aunque hubo un caso a cinco.
- **15 enclaves comunitarios delimitados**; once de ellos con comunidad y sin oferta comercial concentrada — **eso es un resultado, no un hueco**.
- **31 entradas en la capa de memoria**, 17 de confianza media o baja.
- **48 fichas en el corpus** (`fichas_corpus_polos.csv`, 25 campos).
- **El 46,6 % de la base no tiene `direccion_norm`.** Afecta toda asignación de locales a zonas que no sea puramente geométrica. **Va declarado en los límites.**

---

# 6 · Las reglas de método · R1 a R16 + la pregunta cero

Viven en `agent_skills/shared/datagastro_metodo_experimental.md`.

**Antes de todas, la pregunta cero:**

> **¿Esto que estoy por afirmar es una propiedad del territorio, o una propiedad de mi instrumento?**
> Si es del instrumento, se escribe como propiedad del instrumento. **Aunque sea menos interesante. Sobre todo si es menos interesante.**

| bloque | qué preguntan |
|---|---|
| **R1–R8** · fase de medición | **¿el número es correcto?** |
| **R9–R13** · fase documental | **¿a qué objeto pertenece este dato?** |
| **R14–R16 + pregunta cero** | **¿de qué estoy hablando?** |

**R1** lectura escrita antes de correr · **R2** ablación con control aleatorio · **R3** un umbral no se mueve para rescatar un caso · **R4** si depende de un parámetro, se publica la curva · **R5** antes de gastar en una API, el número estimado · **R6** procedencia y licencia; las fuentes se cuentan por **grupo** · **R7** «no encontramos» ≠ «no existe» · **R8** un campo que vuelve vacío sin fallar es un error

**R9** antes de reportar un dato como nuevo, se cruza contra la capa cargada, **nunca contra archivos propios** · **R10** un referente sin dirección no se carga; todo nombre en dos capas lleva marca de par · **R11** la fecha de un metadato no es la fecha del dato · **R12** toda delimitación se verifica **midiéndola**; la contención por superficie perdida, no por predicado · **R13** una atribución se verifica contra la **entidad nombrada**, no contra la más cercana

**R14** una clase que aparece y no estaba en el diseño se trata como sospecha de instrumento hasta que se la pueda producir a propósito · **R15** **una predicción que se cumple se audita igual que una que falla** · **R16** cuando se pidió la fuente autoritativa, **no se publica sobre la provisoria**

**Corolario de R6:** en una tabla de trazabilidad no se abrevia, y se verifica contra disco.

**Procedimiento de redacción, que no es regla pero falla igual:** toda afirmación de estado que venga de una frase de fuente **lleva la fecha pegada al texto**. «Hoy ninguna sobrevive» no se escribe; se escribe «ninguna sobrevivía, según una fuente de 2019».

---

# 7 · Cómo fallo · leer esto antes de producir nada

**El error que se repite, y ya van seis o siete veces:** afirmar una propiedad del instrumento como si fuera del territorio. El sur que «no tenía zonas»; la vía B en 7 de 94 que era el tamaño de los polígonos; una tercera clase que era un denominador roto; la «hipótesis del contenedor» falsa; setenta `OPERATIONAL` que eran ausencia de señal; «el catálogo arrastra cerrados» que eran once elegidos por sospechosos.

**En todos, la lectura territorial era la más noticiosa.** Ese es el sesgo: no es descuido, es atractivo.

**Los otros modos, con su caso:**

- **Afirmar el contenido de archivos que no puedo leer.** Cinco veces: cinco hitos de Monserrat, dos de Barracas, la cantidad de preguntas de control, dos decisiones que ya estaban tomadas, y diez archivos que di por commiteados sin haberlos escrito. **Antídoto: pedir el volcado y cruzarlo.**
- **Proponer un perímetro sin medirlo.** Dos veces, las dos con avenidas que resultaron ser la misma o encontrarse: Flores (Boyacá/Carabobo) y Colegiales (Álvarez Thomas/Forest se tocan a 0 m). **Escribí R12 y no la apliqué a mi propia propuesta.**
- **Leer un titular como un hecho.** The New Brighton dado por cerrado, El Palacio de la Papa Frita dado por cerrado cuando se mudó.
- **Convertir una frase de fuente en estado presente.** Dos veces el mismo día: Las Cañitas y las cantinas de La Boca.
- **Amplificar un número ajeno sin poder verificarlo.** La cola de R20: dije 41 %/53 % y era 47 %/30 %.
- **Publicar sobre la fuente provisoria después de pedir la definitiva.** Las láminas 14 y 15 sobre el PDF del IDECBA. **El error más caro.**

**Lo que funcionó cada vez fue el reparto:** lo que se cayó lo tiró la geometría, una máscara de campos o una planilla — nunca una discusión. **Escribir el criterio de refutación antes de correr salvó Palermo de publicarse mal.**

---

# 8 · Google Places · leer antes de gastar un request

**La ronda 8 corrió 71 consultas y hay que darla por perdida entera.** La máscara no traía `displayName`, así que **ninguno de los 71 resultados tiene referente conocido — incluido el único `CLOSED_PERMANENTLY`**.

**El problema no es la semántica de `businessStatus`, es la atribución (R13).** Consultado por «La Perla del Once», Places devolvió **«La Americana, La Reina de las Empanadas»**: contestó sobre otro establecimiento.

**Antes de cualquier corrida futura:**

1. `displayName` y `formattedAddress` **obligatorios**.
2. **Compuerta de identidad** que rechace la respuesta si nombre y dirección no coinciden.
3. **No usar `maxResultCount: 1`** — la misma consulta a dos minutos devolvió otro lugar. Sin restricción de identidad no hay resultado reproducible.
4. **Cuando dos campos de la misma respuesta se contradicen, no hay dato.** El Castelar volvió como «EX Hotel Castelar.» con estado `OPERATIONAL`.

**Y la regla de la escala:** `v2b` **acredita cierre cuando Places lo afirma y no acredita nada cuando calla** (FD-21). `OPERATIONAL` es la ausencia de una señal de cierre, no una afirmación de apertura.

**Costo hasta hoy: 79 requests, tope USD 2,76.** El piso de detección quedó sin establecer.

---

# 9 · Las fuentes con defecto · FD-01 a FD-23

Están cargadas en la capa. **Los mecanismos, que es lo que importa:**

**Re-sellado de archivo** (FD-01, El Cronista, ventana de septiembre de 2025) · **lavado de recencia** — fecha de publicación nueva sobre cuerpo viejo (FD-02, FD-14) · **recencia sintética** — fecha fabricada con firma de usuario (FD-13), año en el título (FD-09), copyright como fecha (FD-15), fecha del día renderizada en el encabezado (FD-06) · **el padrón que se re-data solo** al sumar cohortes (FD-10) · **el mismo dominio produciendo ficha inerte y ficha editada** (FD-07, FD-19) · **discrepancia de fecha dentro de la misma pieza** — tomar siempre la más vieja (FD-11) · **marcas de cierre visibles e inauditables** — se registran, nunca deciden (FD-12) · **el mismo medio publicando las dos direcciones en diez días** — la unidad de análisis es la nota, no el medio (FD-03) · **el bloqueo suele ser de la ruta, no del dominio** — vale reintentar por el dominio raíz (FD-04) · **dato normativo que sólo existe en el slug de la URL** (FD-16) · **contradicción del mismo medio sobre la edad de un local** — no elegir, atribuir (FD-17) · **reetiquetado editorial de una distinción real** (FD-18) · **un acto jurídico leído como cierre** (FD-20) · **campo de estado cuyo valor por defecto tiene forma de afirmación** (FD-21) · **titular que afirma el desenlace opuesto en dominio inaccesible** (FD-22) · **informe y banco de datos del mismo organismo con universos distintos** (FD-23).

**Y la peor:** **FD-05, la grilla de evento fabricada sobre un padrón caduco.** Un sitio publicó sedes de un festival con fechas correctas y un padrón viejo. **Pasa el olfato porque el evento sí existe.** De ahí sale que **una sede sólo cuenta como v5 si la nombra el organizador, en una edición fechada.**

**La ruta que funciona:** **TripAdvisor no bloquea y expone día exacto.** Hay que leer **las dos fichas, `.com` y `.com.ar`** — devuelven una «más reciente» distinta (FD-08) — y **leer las fechas una por una**, porque el orden de listado no es cronológico. Instagram, Facebook, TikTok y Yelp bloquean: **eso es lo que Diego resuelve en dos minutos y vos no podés resolver nunca.**

---

# 10 · Lo decidido y lo abierto

**23 decisiones tomadas**, en `DECISIONES_TOMADAS_*.csv`. Las que más gobiernan: las dos familias de vías · la trayectoria extinguida se publica pero no abre · Untappd computa como v3b · reporteo a nivel programa acredita v4 · la vía C se abre por centralidad · R22 Villa Pueyrredón se publica con su debilidad declarada.

## Lo que sigue abierto

**Palermo — la más grande.** Soho (772) + Hollywood (595) + Cañitas (361) = 1.728 locales; R01 publicada = 1.358. **No están anidadas.** Hubo una hipótesis mía —que R01 ya era Soho ∪ Hollywood— y **la refutó su propio criterio: `R01 ∩ Cañitas` = 43,65 ha y 210 locales**, donde había predicho cero. El «delta 9» eran **407 locales que salen menos 398 que entran**. Y **la corroboración externa también se cayó**: la serie del IDECBA releva un solo eje de Palermo.

**Lo único firme:** la unión de las tres **no contiene** a R01 — y eso descarta que las subzonas sean las fichas y R01 deje de ser fila, porque perdería locales publicados. Diego propuso adoptar la hipótesis igual; **hay que sostener que no**, porque publicar que Cañitas está afuera hace que quien sume cuente 210 locales dos veces.

> **Corregido el 09/08/2026 · ERR-07.** Esta línea decía «407 locales de R01 no están en ninguna
> subzona» y «perdería 407 locales publicados». **El objeto estaba invertido.** Los 407 son los
> locales de Soho ∪ Hollywood que caen **fuera** de R01: son de las subzonas, no de R01. Los de
> R01 que no están en las subzonas son **398** contra dos y **188** contra las tres. La opción B
> perdería **188**, no 407. **El veredicto no cambia; la magnitud sí.**
>
> Y «falta saber qué son esos 407» **ya no falta**: el residuo está medido en 8 piezas
> (`ronda_10/palermo_residuo_por_zona.csv`), la mayor de **40,17 ha y 134 locales**. La ronda 13
> midió además las tres subzonas que la ficha nombra y nadie había cruzado —Botánico, Pacífico y
> Villa Freud— y **las tres dan intersección cero con R01**: no explican ni un local del residuo.
> Ver `ronda_13/palermo_seis_subzonas.csv`.

**Colegiales.** Chacagiales quedó fusionado (495,8 ha, 891 locales, 0,0 m² perdidos), pero **158,1 ha y 310 locales entraron a escala de barrio** porque Z43 no tiene perímetro. Mi propuesta de perímetro era imposible: **Av. Álvarez Thomas y Av. Forest se tocan a 0 m.** Sólo **Zabala (254 m) y Virrey Avilés (344 m)** cruzan con tramo verificable: **tres cuadras, no diez.** Y el **Polo Concepción tiene el 47 % de su área dentro de R01**, así que se resuelve **con Palermo, no aparte**.

**Otros:** `R08 Villa Crespo ∩ R21 La Paternal = 49,7 ha`, sin tocar · **Monserrat: 9 en el catálogo contra 2 en la capa**, sin reconciliar — la lámina 6 aguanta porque los cuatro barrios son Comuna 1, la 7 no · **la vía C de Almagro**: mercado o feria itinerante, y de eso depende que la lámina 4 diga «seis vías» o «cinco» · **5 zonas pendientes de límites** · **la cola de R20**: 47 % de la superficie y 30 % de los locales fuera del tramo documentado, que **se conserva** porque las 22 sólo se amplían, y se declara.

---

# 11 · Dónde está cada cosa

Todo en `desde_cowork/evidencia_2026/`, con `INDICE.csv` y `correspondencia_fase_documental.csv`.

**Método:** `EDICION_TECNICA_METODO.md` (secciones 0–26) y `EDICION_TECNICA_FASE_DOCUMENTAL.md` (27–55, Partes XI–XVII) · `CRITERIO_ESCALA_DE_LAS_VIAS.md` · `EL_ERROR_QUE_SE_REPITE.md`

**Documento:** `ATLAS_V3_SECCIONES_I_IV_VII.md` (I, III, IV) y `ATLAS_V3_SECCIONES_II_V_VI_IX.md` (II reescrita, V, VI, IX) · `MODELO_DE_FICHA_Y_TRES_EJEMPLOS.md`

**Presentación:** `LAMINAS_v2_2026-08-08.md`, que el repositorio dejó en **v2.1** en el working tree · `lamina_5_reescrita.csv`

**Datos:** `catalogo_90_estado_final.csv` · `hitos/hitos_capa_2026_r11.csv` · `fichas_corpus_polos.csv` · `capa_de_memoria.csv` · `homonimos_vivo_muerto.csv` · `enclaves_comunitarios_delimitados.csv` · `auditoria_duplicados.csv` · `ronda_10/idecba_densidad_48_ejes.csv`

**Correcciones:** `errata_2026-08-08.csv`, `errata_2026-08-08_ronda_10.csv`, `NO_ERA_UN_CONTEO_MAL_ERA_OTRO_UNIVERSO.md`

**Para Diego:** `caminatas_de_verificacion.csv` — tres corredores para verificar en la calle: **Montes de Oca 280–1702** (es la lámina 12 y nadie midió la continuidad), **Av. Rivadavia en Flores** (y qué proporción del eje es gastronomía), **Las Cañitas** (361 locales nuestros contra 97 de La Nación, sin explicar).

---

# 12 · Qué sigue

**Diego eligió: los dos entregables, la presentación primero.**

**La presentación está casi lista** — v2.1 en el working tree, con la lámina 10 como la única si hiciera falta una sola.

**El documento: faltan las secciones VII y VIII.** La VII son las 41 fichas y es el cuerpo. **31 se pueden escribir ya**; 10 están bloqueadas por Palermo, Colegiales y las cinco zonas pendientes.

> **La recomendación que quedó sobre la mesa y no está tomada: cortar la dependencia.** Publicar las 10 bloqueadas con el perímetro declarado en revisión y sin cifra agregada. **No se resigna nada** —hoy tampoco se puede afirmar cuántos locales tiene Palermo— y se destraban 31 fichas.

**Estimado: entre seis y nueve jornadas de trabajo**, sesgado hacia arriba porque cada ronda encontró algo que agregó trabajo. **Con las tres palancas de alcance —cortar la dependencia, ficha compacta por defecto, publicar por comuna— baja a tres o cuatro.**

**Lo próximo para el repositorio, en orden:** recorrer la **vía B contra el catálogo cargado** (es lo que más rinde y es una corrida, cero requests) · los **10 `requiere_cruce`** de la vía E · la **vía C de Almagro** · **qué son los 407 locales** de Palermo · el **perímetro de Colegiales** sobre la cuña real · **R08 ∩ R21** · **Monserrat** capa contra catálogo.

**Lo próximo para vos:** las **31 fichas** con el modelo ya validado, la **sección VIII**, y consolidar la edición técnica con las rondas 8 a 12.

**Lo próximo para Diego:** las **tres caminatas**, y decidir el corte de la dependencia de Palermo.
