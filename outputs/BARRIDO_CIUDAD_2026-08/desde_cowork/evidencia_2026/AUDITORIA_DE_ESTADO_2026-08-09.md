# Auditoría de estado · Atlas V3

**9 de agosto de 2026 · hecha desde Cowork con lectura directa del repositorio**

Qué es esto: un cruce de todo lo que el proyecto afirma sobre sí mismo contra lo que hay en
disco. No produce nada nuevo. Corrige el mapa, no el territorio.

**Cómo se verificó.** Lectura directa de `C:\proyectos\Gastronomia\DataGastro` por el puente de
archivos: `git log`, `git status` normalizado, mtimes, y lectura íntegra de las narrativas de las
rondas 3 y 5 a 12 más los CSV que las acompañan. Cada cifra de este documento se leyó de un
archivo; ninguna se arrastra del handoff.

**Qué NO se verificó.** El pipeline público (`src/`, `data/processed/`, `dashboard/`) —no se tocó
ni se leyó—. Los otros subproyectos (Cafecito, Mercados, CasasDePastas, V2). El gasto real de
Google Places, que sólo lo dice la consola de facturación. Y la geometría: no se recorrió ningún
polígono, se leyeron las mediciones que las rondas dejaron escritas.

---

## 1 · Antes que nada: un artefacto del instrumento

Visto desde el montaje de Linux, `git status` marca **cientos de archivos como modificados**,
incluidos archivos commiteados el 6 de agosto que nadie tocó.

**Es falso, y el mecanismo es este.** Git de Windows tiene `core.autocrlf=true` en la
configuración global del usuario: guarda LF en el objeto y escribe CRLF en el árbol de trabajo.
El Git de Linux que corre en el puente lee otra configuración global —la del contenedor, vacía—,
no aplica la conversión, y entonces ve CRLF donde el objeto tiene LF. Todo archivo de texto
aparece cambiado línea por línea.

Prueba sobre `borrador_polos/parametros.json`, commiteado el 06/08 y no tocado desde entonces:

| | bytes | CR (0x0d) | md5 sin CR |
|---|---:|---:|---|
| objeto en HEAD | 858 | 0 | `2181e54a814161255b869fb50968bdf6` |
| archivo en disco | 936 | 78 | `2181e54a814161255b869fb50968bdf6` |

**Mismo contenido.** El diff decía 78 líneas borradas y 78 agregadas; el contenido es idéntico.

Normalizando con `git -c core.autocrlf=true`, el estado real de `outputs/BARRIDO_CIUDAD_2026-08`
es **3 archivos modificados y 98 sin rastrear**, no cientos.

> Se registra acá porque es exactamente la pregunta cero: una propiedad del instrumento con forma
> de propiedad del territorio. Y era la lectura más alarmante de las dos.

---

## 2 · El hallazgo operativo: casi todo lo de Cowork está fuera de git

Con los finales de línea normalizados, esto es lo que hay:

**Modificados y sin commitear (3):**

- `desde_cowork/README.md`
- `desde_cowork/evidencia_2026/INDICE_DE_VERSIONES.md`
- `ronda_11/decisiones_tomadas_2026-08-08.csv`

**Sin rastrear (98 entradas).** El grueso es **`desde_cowork/evidencia_2026/`: 83 de sus 99
archivos**, incluidos el handoff, las láminas v2.1, `catalogo_90_estado_final.csv`, la capa de
memoria, las erratas y el corpus de fichas. Sólo 16 archivos de esa carpeta están rastreados, y
son los más viejos. Además:

- `ronda_12/` completa (13 archivos) — la ronda que rehízo las láminas 14 y 15 y aplicó la decisión 23
- `hitos/hitos_capa_2026_r11.csv` — la capa de hitos vigente
- `seis_vias/seis_vias_94_filas_r12.csv` y `seis_vias/seis_vias_22_zonas_r12.csv` — la matriz vigente
- `desde_cowork/docx/` (2) y `desde_cowork/mapas/` (3)
- nueve archivos sueltos en `desde_cowork/` — ocho `.md` y `POLOS_NOMBRADOS.csv`—, entre ellos
  `ATLAS_V3_SECCIONES_V_VI.md`, que es donde vive la nota metodológica

Sí están rastreados, para que no se busquen dos veces: `EDICION_TECNICA_METODO.md`,
`ATLAS_V3_SECCIONES_I_IV_VII.md`, `QUE_ES_UN_POLO.md` y el resto de los `.md` de la primera
tanda de `desde_cowork/`.

**No están en `.gitignore`.** Lo revisé entero: ignora `outputs/analisis_interno/`,
`outputs/**/*.pdf`, `outputs/**/*.html`, los crudos de Places y de casas de pastas, y `exports/`.
No menciona `desde_cowork`, ni `evidencia_2026`, ni `ronda_*`, ni `hitos`. Git los ve, los
reporta como sin rastrear y `git add` los tomaría. **Nunca se agregaron.**

El último commit es **`f1d956f`, 8 de agosto 20:26**, que corresponde a la ronda 11. Todo lo
posterior —la ronda 12 entera, la carga del catálogo de 90, la corrección de las láminas 14 y 15,
el índice de versiones y el handoff— está en el árbol de trabajo y en ningún otro lado.

> **Esto no es un problema de disco: los archivos están.** Es un problema de que un `git clean -fd`,
> un cambio de rama o una máquina nueva se los lleva sin dejar rastro, y de que el rastro de
> correcciones que el proyecto se impuso conservar no tiene historia. Es la versión de git del modo
> de falla que ya está registrado: **diez archivos dados por entregados y no escritos.**

Antes de commitear hay que mirar dos cosas contra el guardrail 7: `catalogo_pendientes_para_diego.csv`
(19 KB) y `lista_places_prioridad.csv` (15 KB) son listados por establecimiento con dirección. Son
datos de terceros, no personales, y el resto de la carpeta ya es de ese tenor — pero la decisión
de commitearlos o ignorarlos es de Diego, no mía.

---

## 3 · La cronología real

28 commits entre el 6 y el 8 de agosto, todos con prefijo `feat(polos)` / `fix(polos)` /
`feat(hitos)`. El arco, con las narrativas que los acompañan:

| día | qué pasó |
|---|---|
| **06/08** | base gastronómica de la Ciudad sobre fuentes abiertas · borrador de 124 polos · capa poligonal publicable · matriz extendida a 94 filas · capa de hitos unificada (211 hitos, 181 con punto) · Soho aparece como P091 |
| **07/08** | las seis vías medidas · vía B por presencia y el norte medido · dos enclaves reparados · la Res. 1225/26 como catálogo vigente y el diff que encuentra un alta que nadie había visto |
| **08/08 mañana** | Café Olimpo no estaba en Villa Luro · la vía B pasa a medirse por zona y salta de 16 a 33 · la geometría se toca por primera vez |
| **08/08 tarde** | Places contesta 71 de 71 y lo que mide es que no ve un cierre de nueve meses · el bug de denominador · Places no decía de quién hablaba · el callejero canónico |
| **08/08 noche** | ronda 11 (último commit, 20:26) · **ronda 12 sin commitear (~21:30)** · láminas v2.1 · índice de versiones · handoff (22:03) |

Las rondas 5 a 12 corrieron **con 0 requests de Google Places cada una**. La única corrida pagada
es la de la ronda 8, y se resolvió con caché.

---

## 4 · Palermo: la cadena completa, y de dónde salió el 407

Esta es la corrección más importante del documento, porque el handoff dejó el número mal
etiquetado y con eso bloqueó diez fichas.

**Lo que midió la ronda 9** (`ronda_9/RONDA_9.txt`, tarea 6). La hipótesis escrita antes de correr
era «R01 ya es Soho ∪ Hollywood, y Las Cañitas nunca estuvo adentro». Las tres predicciones
fallaron:

```
R01 publicado          271,29 ha · 1358 locales
Soho      (P091)        92,36 ha ·  772
Hollywood (P078)       102,61 ha ·  595
Cañitas   (P065)        82,04 ha ·  361
Soho ∪ Hollywood       194,97 ha · 1367

R01 ∩ (Soho ∪ Hollywood)   119,14 ha (43,9 %) · 960 locales (70,7 %)   ← predecía «casi todo»
R01 ∩ Cañitas               43,65 ha (16,1 %) · 210 locales             ← predecía ≈ 0
residuo R01 − (Soho ∪ H)   152,15 ha · 398 locales · 7 piezas           ← predecía 9 sobre un borde
```

**Y acá está el 407, con su definición exacta:**

```
locales de Soho ∪ Hollywood que caen FUERA de R01:   407
locales de R01 que NO están en Soho ∪ Hollywood:     398
diferencia (el «delta 9»):                             9
```

> **407 son los locales de las subzonas que se salen de R01. No son locales de R01.** El handoff
> dice «407 locales de R01 no están en ninguna subzona» y eso invierte el objeto. Los de R01 que no
> están en las subzonas son 398 contra Soho ∪ Hollywood, y **188** contra las tres.

**Lo que midió la ronda 10** (`ronda_10/RONDA_10.txt`, tarea 2), esta vez contra las tres subzonas:

```
R01 pierde 0,000000 m² dentro de R01 ∪ Soho ∪ Hollywood ∪ Cañitas   (covers() por predicado da False y por eso NO se usa — R12)
Soho, Hollywood y Cañitas pierden 0,000000 m² cada uno
el padre mide 385,51 ha · 1916 locales

si el padre fuera SÓLO las tres subzonas, R01 perdería 108,50 ha y 188 locales publicados
el residuo son 8 piezas de más de 0,1 ha:

   #      ha  locales  barrio dominante
   1   40,17      134  Palermo (100 %)
   2   31,42       15  Palermo (100 %)
   3   11,07       25  Villa Crespo (88 %)
   4   10,74        1  Palermo (100 %)
   5    6,71        6  Colegiales (97 %)
   6    4,64        5  Palermo (100 %)
   7    3,21        2  Chacarita (96 %)
   8    0,54        0  Chacarita (100 %)
```

**La aritmética cierra sola, y eso vale como control.** El residuo contra dos subzonas es 398; al
sumar Cañitas se absorben los 210 de `R01 ∩ Cañitas`; 398 − 210 = **188**. Y por el otro lado:
1358 (R01) + 407 (los que se salen) = 1765, más 151 nuevos de Cañitas = **1916**, que es
exactamente el padre. Las dos rondas midieron cosas distintas y son consistentes entre sí.

**Qué queda decidido.** La opción A se sostiene por R12 con superficie perdida cero. La pieza 1
—40,17 ha y 134 locales, el 71 % de los locales del residuo— es un área coherente y no un
remiendo, y la figura que corresponde es un polo con subzonas donde esa pieza es **una subzona
más, la que no tiene nombre todavía**.

**Qué queda abierto de verdad, y es chico.** Ponerle nombre y perímetro declarado a la pieza 1, y
decidir qué se hace con las piezas 3, 5 y 7 —25 locales en Villa Crespo, 6 en Colegiales, 2 en
Chacarita—, que son filtraciones del polígono de R01 sobre barrios vecinos y tocan R08 y el nudo
de Chacagiales.

**El archivo se llama `palermo_los_407_por_zona.csv` y devuelve 188.** El nombre quedó del
planteo anterior. Conviene renombrarlo o, como mínimo, que la fila de errata lo diga.

---

## 5 · Monserrat: la respuesta ya estaba escrita dos rondas antes

El handoff da Monserrat por «sin reconciliar» y la lámina 7 está retirada por eso. La secuencia
real, leída en tres archivos:

- **Ronda 7** (`hitos/RONDA_7_HITOS.txt`, tarea 5c): «Bares Notables con punto en la capa: 91;
  dentro del polígono administrativo de Monserrat: **9**», con los nueve nombrados uno por uno
  (36 Billares, Bar Seddon, Bar Iberia, Cabildo, Café Tortoni, El Colonial, El Querandí,
  La Puerto Rico, London City). Medido por geometría.
- **Ronda 9** (`ronda_9/RONDA_9.txt`, tarea 3): «Notables en Monserrat **2** en la capa: H015 Bar
  Seddon, H094 Bar Iberia». Contado por el campo `barrio_declarado`.
- **Ronda 10** (`ronda_10/RONDA_10.txt`, tarea 3): los 9 están en la capa; el 2 salía de filtrar
  por un campo de texto que viene de la fuente y no de la geometría. **Es R13.** Y midió el límite
  norte: Av. Rivadavia y Av. de Mayo corren sobre el borde de Monserrat a 0 m, y los cuatro
  establecimientos de Av. de Mayo caen adentro.

> La ronda 9 no descubrió una contradicción con el catálogo: **contradijo a la ronda 7 usando otro
> método, y nadie lo notó hasta la ronda 10.** La lámina 7 se retiró sobre la lectura equivocada.

**Y el estado de los nueve está cerrado.** En `catalogo_90_estado_final.csv`, los 9 de Monserrat
figuran **ABIERTO** — seis verificados por Diego el 08/08/2026, Tortoni v3 del 26/05, Los 36
Billares v3 del 04/07, Bar Iberia v4. La lámina 7 no sólo se destraba: se destraba con un dato
más fuerte que el que tenía.

Control cruzado que también cierra: los 4 barrios de Comuna 1 con notables (San Nicolás 20,
Monserrat 9, San Telmo 7, Retiro 4) suman **40 de 90 = 44,4 %**, que es exactamente la lámina 6.

---

## 6 · La lámina 5 está bastante menos bloqueada de lo que dice el índice

El `INDICE_DE_VERSIONES.md` dice: «Pendiente que bloquea la lámina 5: Plaza Asturias y El Globo no
están cargados como hitos y no tienen verificación». Las dos mitades no valen lo mismo.

- **«No están cargados como hitos» no es un pendiente: es una decisión de la ronda 7.** El
  archivo dice que no se dan de alta porque «no tienen ningún registro oficial —El Globo está
  explícitamente fuera del anexo y de los 16 Icónicos—». Cargarlos sería lo incorrecto.
- **«No tienen verificación» sí es real.** No hay vigencia con fecha para ninguno de los dos.

Y hay un tercer dato que el índice no registra: **los 76 m y los 1.100 m² ya están medidos.** Ronda
7, tarea 5e, distancias en metros entre los cuatro: Iberia–Plaza Asturias 17,2 · Iberia–El Globo
51,6 · Iberia–El Imparcial 61,6 · Plaza Asturias–El Globo 68,7 · **Plaza Asturias–El Imparcial
76,1 (máxima)** · El Globo–El Imparcial 30,4. Envolvente convexa: **0,110 ha = 1.100 m²**. El
`lamina_5_reescrita.csv` los pide como «que falta verificar» y ya estaban.

Con eso, la lámina 5 reescrita —cuatro establecimientos, dos con reconocimiento formal y dos sin
ninguno— se sostiene entera salvo por una cosa: **afirma en presente que los cuatro están ahí.**
Falta vigencia de dos. Es una búsqueda acotada, no un bloqueo.

---

## 7 · Deriva del handoff contra el disco

| lo que dice el handoff | lo que hay en disco |
|---|---|
| «falta saber qué son esos 407 locales» | Objeto mal etiquetado. 407 son los de las subzonas fuera de R01. El residuo de R01 está medido: 398 contra dos subzonas, **188** contra las tres, en 8 piezas |
| «Monserrat: 9 contra 2, sin reconciliar» | Reconciliado en la ronda 10. Los 9 están, y los 9 figuran ABIERTO |
| «la vía C de Almagro» sigue abierta | **Correcto.** El barrido de la ronda 11 sólo recorrió las filas que ya abrían la C; Almagro no aparece en `barrido_via_C_titularidad.csv` |
| vía C: 2 filas y 3 zonas | **Correcto.** Ronda 11 daba 3 y 4; la decisión 23 sacó al Patio Costanera Norte de ambas |
| cola de R20: 47 % y 30 % | **Correcto.** Antes 24,75 ha / 54 locales (41 %/53 %); ahora 28,63 ha / 31 locales |
| Polo Concepción, «47 % de su área dentro de R01» | Es el área a 150 m del **tramo** Zapiola–Conesa (143 m). Del **eje** entero (3.253 m) sólo el 8 % cae en R01. Y el eje corre 100 % dentro de Colegiales |
| Chacagiales: 495,8 ha y 891 locales | La ronda 9 dice explícitamente que **esa cifra no se publica como cifra del polo**: usa Colegiales a escala de barrio, que es un techo declarado |
| capa de hitos «225 × 21» | 225 filas × **46** columnas. El 21 es del volcado de la ronda 9 (`capa_de_hitos_volcado.csv`), otro archivo |
| Places: «79 requests, tope USD 2,76» | Tres cifras distintas conviven. Ronda 8: tope 71, **gastados 0**, resueltas 71 de 71 «incluye caché», tope de exposición USD 2,48. Ronda 9: 4 pedidos, **gastados 0 de 4**, tope USD 0,14, y dice «la ronda 8 gastó 71 de los 1.000 de este mes. Con éstas, 75» y «la caché trae 79 consultas ya pagadas». **Exposición máxima acumulada USD 2,62**, y el gasto real sólo lo dice la consola de facturación |
| «faltan las secciones VII y VIII» | Ver el punto 8: hay dos numeraciones conviviendo |
| todo está en `desde_cowork/evidencia_2026/` | `EDICION_TECNICA_METODO.md` y `ATLAS_V3_SECCIONES_I_IV_VII.md` están en `desde_cowork/`; `hitos/` y `ronda_9..12/` cuelgan de `BARRIDO_CIUDAD_2026-08/` |
| «con INDICE.csv y correspondencia_fase_documental.csv» | **Ninguno de los dos existe.** Hay `INDICE_DE_VERSIONES.md`, que es otra cosa |

Todo lo demás del handoff verifica: 124 polígonos publicables, 94 filas, 22 zonas, 90 del
catálogo (86 abiertos · 1 en quiebra · 1 en riesgo · 2 cerrados), 32 citables con fecha propia y
58 no, 48 fichas × 25 campos, 31 entradas en la capa de memoria, 15 enclaves, 3 caminatas.

---

## 8 · Las dos numeraciones del documento, que nadie reconcilió

El handoff dice que faltan la VII y la VIII. Lo que hay en disco son **dos esquemas distintos de
numeración** y ninguna tabla que los relacione:

**Numeración vieja** — `desde_cowork/ATLAS_V3_SECCIONES_I_IV_VII.md` y `ATLAS_V3_SECCIONES_V_VI.md`:

I Presentación · II Qué es un polo · III De dónde salen los datos · IV Cómo se leyó el territorio ·
V La Ciudad comuna por comuna · VI Lo que se midió y no alcanzó · **VII Qué no dice este atlas** ·
**VIII Nota metodológica**

**Numeración nueva** — `evidencia_2026/ATLAS_V3_SECCIONES_II_V_VI_IX.md`:

II Qué es un polo *(reescrita)* · **V Los referentes de la Ciudad** · **VI Las comunidades y el
territorio** · **IX Qué no dice este atlas**

> «Qué no dice este atlas» era VII y ahora es IX. «La Ciudad comuna por comuna» y «Lo que se midió
> y no alcanzó» eran V y VI y ahora esos números están ocupados por otra cosa. La **Nota
> metodológica está escrita** —en la numeración vieja— y el handoff la da por faltante.

Faltan de verdad: **VII, las 41 fichas**, que es el cuerpo. Y hay que decidir dónde va cada bloque
huérfano de la numeración vieja. **El archivo que resolvería esto es el que no existe:
`correspondencia_fase_documental.csv`.** El handoff lo nombra como si estuviera.

---

## 9 · Lo que está realmente abierto

Ordenado por lo que destraba:

1. **Commitear.** La ronda 12 y los 83 archivos sin rastrear de `evidencia_2026` no tienen historia.
2. **La correspondencia de secciones.** Sin eso no se sabe qué falta escribir.
3. **La vía C de Almagro** — mercado o feria itinerante. De eso depende que la lámina 4 diga
   «seis vías» o «cinco». Es una corrida, cero requests.
4. **La pieza 1 de Palermo** — nombre y perímetro declarado para 40,17 ha y 134 locales. Y qué se
   hace con las tres piezas que se filtran a Villa Crespo, Colegiales y Chacarita.
5. **Vigencia de Plaza Asturias y El Globo** — lo único que le falta a la lámina 5.
6. **El perímetro de Colegiales sobre la cuña real** — Zabala 254 m y Virrey Avilés 344 m son los
   dos únicos cruces con tramo verificable. Tres cuadras, no diez.
7. **R08 ∩ R21** — 49,7 ha de solape entre Villa Crespo y La Paternal, sobre el contacto entre
   ellas y no sobre R01. Medido que R08 está a 6 m de R01 y no se tocan.
8. **Las 5 zonas pendientes de límites** y **los 10 `requiere_cruce` de la vía E**.
9. **Las tres caminatas de Diego** — Montes de Oca 280–1702, Rivadavia en Flores, Las Cañitas.

**Y una cosa que hay que dejar de repetir**, porque ya está resuelta y sigue circulando: la lámina
7 no está en suspenso. La cabecera de la v2.1 y las notas finales todavía dicen que sí.

---

## 10 · Lo que la auditoría no encontró

Vale escribirlo, porque un informe que sólo trae hallazgos se lee como si todo estuviera mal.

- **No hay ninguna cifra publicada que no tenga respaldo en un archivo.** Las de las láminas
  vigentes se cruzaron contra `ronda_12/`, `catalogo_90_estado_final.csv` y las series del IDECBA,
  y todas cierran.
- **No hay contradicciones vivas entre rondas.** Las tres que hubo —el retipado de Yiyo el
  Zeneize, el conteo de Monserrat y el anclaje de García del Río— las encontró y corrigió el
  propio proceso, cada una con su errata escrita.
- **La cadena de medición de Palermo es aritméticamente consistente** entre las rondas 9 y 10, y
  lo comprobé por dos caminos independientes.
- **Las correcciones de la ronda 12 son correctas y están bien documentadas.** Las dos tesis que
  se cayeron —«los polos consagrados son los que más comercio pierden» y «la brecha no es entre el
  norte y el sur»— están refutadas con el número al lado y con el universo declarado.

El problema del proyecto hoy no es la calidad de la medición. Es que **el registro de lo hecho
va más lento que lo hecho**: el handoff quedó atrás de la ronda 10, el índice de versiones quedó
atrás de la 10 también, y git quedó atrás de la 12.

---

## Anexo · Cifras verificadas contra disco el 09/08/2026

| cifra | valor | archivo |
|---|---:|---|
| polígonos publicables | 124 | `borrador_polos/polos_publicables.csv` |
| filas de la matriz | 94 | `seis_vias/seis_vias_94_filas_r12.csv` |
| zonas | 22 | `seis_vias/seis_vias_22_zonas_r12.csv` |
| catálogo de notables | 90 (86 abiertos · 1 quiebra · 1 riesgo · 2 cerrados) | `catalogo_90_estado_final.csv` |
| notables en Comuna 1 | 40 = 44,4 %, en 4 barrios | ídem |
| capa de hitos | 225 × 46 · 92 con vigencia «si» | `hitos/hitos_capa_2026_r11.csv` |
| citables con fecha propia | 32 sí · 58 no | ídem |
| fichas del corpus | 48 × 25 | `fichas_corpus_polos.csv` |
| capa de memoria | 31 × 15 | `capa_de_memoria.csv` |
| enclaves comunitarios | 15 × 16 | `enclaves_comunitarios_delimitados.csv` |
| caminatas | 3 | `caminatas_de_verificacion.csv` |
| padre de Palermo | 385,51 ha · 1916 locales | `ronda_10/palermo_contencion_y_residuo.csv` |
| residuo de Palermo | 108,5 ha · 188 locales · 8 piezas | `ronda_10/palermo_los_407_por_zona.csv` |
| último commit | `f1d956f` · 08/08 20:26 | `git log` |
| sin commitear en el barrido | 3 modificados · 98 sin rastrear | `git status` normalizado |
