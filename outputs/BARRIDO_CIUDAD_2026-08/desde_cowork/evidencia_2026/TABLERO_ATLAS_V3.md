# Tablero · Atlas V3

**9 de agosto de 2026, cierre del día · única fuente de estado**

**Reemplaza a `HANDOFF_ATLAS_V3_CONTEXTO.md` y a `TABLERO_DE_ESTADO.md`.** Los dos quedan en disco
—nada se borra— y ninguno de los dos manda. Si alguno dice algo distinto de esto, manda esto.

**Cada línea de este archivo se leyó de un archivo del repositorio hoy.** Lo que no se pudo
verificar está marcado como no verificado.

---

## 0 · La regla, que es una sola

**Antes de trabajar en algo, se busca en la sección 4. Si está ahí, está cerrado.**
**Antes de reportar algo, se escribe acá. Un hallazgo que no está en este archivo no existe para
la próxima sesión.**

Esto no es burocracia: es la respuesta a un patrón medido. **Cinco veces se rehizo trabajo que ya
estaba hecho**, y las cinco por la misma causa —nadie miró el archivo que ya tenía la respuesta—:

| se rehizo | ya estaba resuelto en |
|---|---|
| el conteo de Monserrat | ronda 7, medido por geometría. La ronda 9 lo contradijo con otro método y nadie lo notó hasta la 10 |
| «qué son los 407 de Palermo» | rondas 9 y 10. El handoff invirtió el objeto y con eso bloqueó diez fichas |
| los 76,1 m y los 1.100 m² de la lámina 5 | ronda 7, tarea 5e. Se pidieron como «que falta verificar» |
| la tabla de numeración de secciones | la cabecera del propio archivo que la auditoría estaba citando |
| el modelo de ficha | había dos moldes, no uno, y se produjo con el más nuevo sin mirar el otro |
| **«La Boca no fue evaluada»** | **ronda del sur, 07/08.** Se midió con las seis vías, entró con dos zonas, y el resultado quedó en un archivo que nadie volvió a abrir. **Sexta vez.** ERR-17 |

**Y una regla de frontera que costó cinco errores:** nadie afirma el contenido de un archivo que no
leyó. Cowork tiene lectura directa del repositorio por el puente. **Se lee, no se recuerda.**

---

## 0 bis · El criterio, que también es uno solo

**Escrito el 09/08 a pedido de Diego.** Documento completo en
`CRITERIO_DE_ADMISION_Y_PERMANENCIA.md`, tabla en `criterio_admision_55.csv`, reproducible con
`build_criterio.py`.

> **Haber sido publicado no da derecho de admisión. Da derecho de permanencia.**

**Admisión · tres condiciones, las tres necesarias.**
**C1** abre al menos **dos** de las seis vías · **C2** las vías que abren se apoyan en **al menos dos
orígenes independientes** · **C3** la evidencia cae dentro de **un objeto delimitable**.

**Cuatro reglas de aplicación.** Una vía abre o no abre —«parcial» es no abre—. Una puerta cerrada
ni bloquea ni otorga. La herencia no vale hacia arriba. **El perímetro no es condición de admisión:
es un atributo de producción.**

**Permanencia · nada se da de baja, cambia de categoría, con motivo y fecha.**
`polo admitido` · `referencia en observación` · `zona en estudio` · `zona evaluada sin admisión`.

**El umbral está calibrado, no elegido:** con ≥1 entran Villa Real y Parque Chas por un solo bar;
con ≥3 **se cae el Microcentro, se cae San Telmo y se caen las dos zonas de La Boca**. Con ≥2 el
conjunto queda en 41.

**Resultado sobre las 55 unidades evaluadas:** 41 polos admitidos · 1 referencia en observación
(R22 Villa Pueyrredón) · 4 zonas en estudio · 9 zonas evaluadas sin admisión. **Coincide con el
disco en 44 de 48 filas y difiere en cuatro** —R22, Z42 Coghlan salen; Z28 Monte Castro y Z35
Balvanera·Once entran—. **Catorce comunas con polo; la 8 sigue sin ninguno.**

---

## 1 · El reparto

| | **Diego** | **Cowork** | **El repositorio** |
|---|---|---|---|
| hace | decide, verifica en la calle y en redes, firma | investiga fuentes públicas, fija criterio, redacta, audita | mide, corre, cruza geometría, versiona |
| no hace | no escribe el documento | no mide geometría ni corre nada | no decide criterio ni redacta |
| sólo él puede | Instagram, Facebook, TikTok, la calle, la firma | leer prensa y fuentes públicas, y escribir | tocar el dato y git |

**Una sola sesión de Cowork por vez.** Dos sesiones sobre la misma carpeta duplican exactamente lo
que este tablero viene a evitar: el tablero anterior y esta auditoría se escribieron en paralelo y
llegaron a conclusiones distintas sobre los mismos archivos.

**Y un detalle operativo que hay que saber:** `git status` desde el puente marca cientos de
archivos como modificados **y es falso** — Git de Windows guarda LF en el objeto y escribe CRLF en
el árbol, y el Git de Linux del puente no hace la conversión. Se usa siempre
`git -c core.autocrlf=true status`.

---

## 2 · La estructura del documento · RESUELTA

Era la decisión más grande del proyecto y está tomada. **El cuerpo son las 41 fichas en prosa. Las
124 concentraciones van como capa de datos y anexo.**

| | sección | estado |
|---|---|---|
| **I** | Presentación | **reescrita el 09/08** · `SECCION_I_PRESENTACION.md` |
| **II** | Qué es un polo gastronómico | escrita, reescrita |
| **III** | De dónde salen los datos | escrita |
| **IV** | Cómo se leyó el territorio | escrita |
| **V** | Los referentes de la Ciudad | escrita |
| **VI** | Las comunidades y el territorio | escrita |
| **VII** | La Ciudad, comuna por comuna | **COMPLETA · 42 fichas** |
| **VIII** | Lo que se midió y no alcanzó | escrita completa |
| **IX** | Qué no dice este atlas | escrita |
| **Anexo A** | Nota metodológica | **escrita** — deja de estar huérfana |
| **Anexo B** | Las 124 concentraciones detectadas | **escrito** · `ANEXO_B_LAS_124_CONCENTRACIONES.md` y `anexo_B_124_concentraciones.csv` |
| **Anexo C** | Correspondencia, glosario, fuentes y erratas | **escrito** · `ANEXO_C_CORRESPONDENCIA_GLOSARIO_FUENTES.md` |

**Tres resoluciones que van con eso, y por qué.**

**Las 41 se agrupan por comuna, no por origen.** El argumento editorial que ya estaba tomado
—ordenar por tamaño pone Palermo primero y el sur al final, y reproduce en el índice el sesgo que
el trabajo vino a corregir— **vale igual para ordenar por origen**, que pone «las 22 de siempre»
adelante. El origen queda en el encabezado de cada ficha, que es donde no ordena nada. **Con esto
la sección VII conserva su título y la tabla de numeración no se toca.**

**La Nota metodológica va como Anexo A.** Su propia definición es «resumen, con remisión a la
edición técnica como documento aparte». Un resumen que remite a otro documento es anexo, no
sección. Y las nueve secciones están ocupadas: VIII es «Lo que se midió y no alcanzó», que está
escrita completa. **Era la única fila de la correspondencia que no cerraba, y ahora cierra.**

**La apertura de «comuna por comuna» del proyecto de las 124 se recicla para el Anexo B.** Está
escrita —cómo leer las páginas, sobre los nombres, sobre los números— y sirve tal cual para
presentar la tabla de las 124.

---

## 3 · Lo que se produjo el 9 de agosto

| pieza | qué es |
|---|---|
| `AUDITORIA_DE_ESTADO_2026-08-09.md` | la auditoría que abrió el día |
| `DOS_PROYECTOS_DE_FICHA.md` | el hallazgo de los dos moldes de ficha |
| `ERRATA_DEL_MODELO_DE_FICHA.md` | dos cifras del IDECBA refutadas que el modelo arrastraba |
| `SECCION_VII_REFERENCIAS_PUBLICADAS.md` | **las 21 fichas de referencias publicadas** · reemplaza a la tanda 1 |
| `SECCION_VII_ZONAS_INCORPORADAS.md` | **las 21 fichas de zonas que se incorporan**, Montes de Oca incluida · cierra el cuerpo |
| `LO_QUE_DECIDISTE_Y_LO_QUE_FALTA.md` y `decisiones_2026-08-09.csv` | el consolidado de decisiones del día |
| `NIVELES_DE_NOMBRE_41.md` y `.csv` | la asignación de nivel de nombre para las 41, para firma |
| `LAMINAS_v2.2_2026-08-09.md` | la presentación con Almagro en cinco vías y Monserrat repuesta |
| `TABLERO_ATLAS_V3.md` | este archivo |
| ronda 13, del repositorio | git al día, Almagro medido, las tres subzonas de Palermo, la sanitización de contactos |

---

## 4 · CERRADO · no reabrir

Cada línea tiene su archivo. Si alguien vuelve a preguntar esto, la respuesta es «está cerrado,
mirá tal archivo».

### Delimitación y geometría

| pregunta | respuesta | dónde |
|---|---|---|
| ¿Qué son los 407 de Palermo? | Los locales de Soho ∪ Hollywood que caen **fuera** del perímetro publicado. No son de él. Los suyos que no están en las subzonas son 398 contra dos y **188** contra las tres, en 8 piezas | `ronda_10/palermo_residuo_por_zona.csv` · ERR-06, ERR-07 |
| ¿Palermo opción A o B? | **A.** La B perdería 188 locales publicados. Contención verificada por superficie perdida 0,0 m² — el predicado da False y por eso no se usa | ronda 10 |
| ¿La pieza 1 es Botánico, Pacífico o Villa Freud? | **No.** Las tres intersecan en 0,00 ha y 0 locales. La hipótesis se corrió y se cayó | `ronda_13/palermo_seis_subzonas.csv` |
| ¿La pieza 3 se solapa con Villa Crespo? | **No.** Está a 6 m y no se tocan. Es artefacto de borde, no filtración: hay un hueco que declarar, no algo que repartir | ronda 13 |
| Soho: ¿728 o 772 locales? | **Los dos, y miden cosas distintas.** 728 es el grupo detectado; 772 es el polígono publicado. La resta cierra: −8 del grupo que caen afuera, +52 adentro que no eran del grupo. **Para cartografía manda 772** | ronda 13 |
| ¿Con qué universo se contaron los locales de Palermo? | `anillo == 'nucleo'` **y** `apto_geometria == True`: 23.981 de 27.727. Contar los 27.727 da un 7 % más **con las mismas áreas**, que es lo que lo hace peligroso | ERR-10 |
| ¿Cuántos Notables tiene Monserrat? | **9**, medido por geometría. El «2» salía de filtrar por un campo de texto de la fuente | ronda 7, reconciliado en la 10 |
| ¿La vía C de Almagro abre? | **No abre.** Ningún hito de tipo mercado o patio cae en su polígono; el más cercano está a 1.237 m y es de Caballito. Lo único cerca es una feria itinerante, y una feria no abre la vía | `ronda_13/via_C_almagro.csv` · ERR-08 |
| ¿Cuántas filas abren vía C? | **2 de 94** (Palermo Hollywood, Caballito) y **3 de 22** (Bonpland, Belgrano, del Progreso). Cadena completa: r8 cuatro → r10 tres → r12 dos | ronda 13, control de arrastre |
| ¿La cola de García del Río? | 47 % de la superficie y 30 % de los locales — 28,63 ha y 31 locales. Se conserva y se declara | ronda 12 |
| ¿Villa Crespo toca Palermo? | No. 6 m. Su solape real es con La Paternal: 49,7 ha | ronda 9 |

### Vigencia y referentes

| pregunta | respuesta | dónde |
|---|---|---|
| ¿Estado del catálogo de Notables? | **90 de 90 verificados.** 86 abiertos · 1 en quiebra operando · 1 en riesgo · 2 cerrados. Operan 88 | `catalogo_90_estado_final.csv` |
| ¿Cuáles son los 2 cerrados? | Plaza Bar (Florida 1005, desde abril de 2017) y La Buena Medida (Suárez 101, desde octubre de 2025) | ídem |
| ¿The New Brighton está cerrado? | **No.** Quiebra decretada y sigue atendiendo. Un acto jurídico no es un hecho operativo | ídem |
| ¿El Palacio de la Papa Frita cerró? | **No: se mudó** de Av. Corrientes 1612 a Paraná 350 | errata del 08/08 |
| ¿Sirve la corrida de Places de la ronda 8? | **No.** Se da por perdida entera: sin `displayName`, ninguno de los 71 resultados tiene referente conocido | ronda 9 |
| ¿Hay que cargar Plaza Asturias y El Globo como hitos? | **No, y es decisión de la ronda 7:** no tienen registro oficial | ronda 7 |
| ¿Plaza Asturias y El Globo están abiertos? | **Sí, los dos, verificados el 09/08/2026** por publicación fechada en canal propio — v2. El Globo con historia del 09/08, Plaza Asturias con foto del ≈02/08 | `LO_QUE_DECIDISTE_Y_LO_QUE_FALTA.md` |
| ¿Por qué la cuarta subzona de Palermo no está adentro de las otras? | Porque las tres conocidas cubren el 60 % del perímetro publicado y están del lado de Juan B. Justo; la pieza está sobre Paraguay, Charcas y Soler, del lado de Santa Fe. **Y Botánico, Pacífico y Villa Freud intersecan en 0,00 ha: están enteramente afuera del perímetro publicado.** Son vecinas, no subzonas | `ronda_13/palermo_seis_subzonas.csv` |
| ¿Los 76 m y los 1.100 m² de la lámina 5? | **Medidos.** Máxima 76,1 m entre Plaza Asturias y El Imparcial; envolvente 0,110 ha | ronda 7, tarea 5e |

### Fuentes, láminas y documento

| pregunta | respuesta | dónde |
|---|---|---|
| ¿Cuántos ejes tiene el IDECBA? | **48 vigentes.** La serie manda, el PDF no. «Microcentro» no está entre los 48 | `ronda_12/idecba_48_autoridad.csv` |
| ¿«Los polos consagrados son los que más pierden»? | **Refutado.** −1,69 contra −1,30, con 21 casos por lado | ronda 12 |
| ¿«La brecha no es norte-sur»? | **Refutado, y al revés:** Norte 0 de 9 suben, Sur 7 de 13 | ronda 12 |
| ¿La lámina 7 está en suspenso? | **No.** Repuesta en la v2.2, con los nueve de Monserrat y su estado | `LAMINAS_v2.2_2026-08-09.md` |
| ¿Almagro abre las seis vías? | **No: cinco.** Y tampoco era la única que marcaba seis — eran tres | ERR-08 |
| ¿Falta escribir la Nota metodológica? | **No.** Está escrita y completa. Va como **Anexo A** | sección 2 de este tablero |
| ¿Hay dos numeraciones del documento? | **Eran dos proyectos de documento, no dos numeraciones.** Resuelto: el cuerpo son las 41 | `DOS_PROYECTOS_DE_FICHA.md` |
| ¿Cuál es el cuerpo del documento? | **Las 41 fichas en prosa, agrupadas por comuna.** Las 124 van al Anexo B | decidido por Diego el 09/08 |
| ¿Está todo bajo git? | **Sí, desde la ronda 13**, salvo los cuatro CSV con teléfono que van al `.gitignore` con su derivada `*_sin_contacto` versionada | ronda 13 |

---

## 5 · ABIERTO

### Espera algo de Diego

**Cinco de las siete decisiones que estaban abiertas se cerraron el 09/08.** Quedan dos, y ninguna
bloquea la producción. Detalle y explicación en `LO_QUE_DECIDISTE_Y_LO_QUE_FALTA.md`.

| # | qué | por qué sólo él |
|---|---|---|
| ~~**D1**~~ | ~~¿La Boca se evalúa y entra como la 43?~~ **CERRADA, y no por decisión: La Boca fue evaluada el 07/08 con las seis vías y sus dos zonas entraron.** El resultado quedó en un solo archivo y nunca se trasladó al corpus. No hay nada que decidir: hay que trazarle el perímetro. Ver ERR-17 | ya no espera nada |
| **D2** | **Happening** y **Celta Bar**, en Instagram o Facebook. Son los dos únicos establecimientos del atlas que no resolvió nadie, y las redes están bloqueadas para todo agente automático | sólo él puede |
| **D3** | Las **tres caminatas**, cuando pueda. **Ya no bloquean:** las tres tienen reemplazo de escritorio, la de Las Cañitas está resuelta y la de Montes de Oca se midió | mirar la calle |

**Y nada más.** Las otras dos que estaban abiertas se cerraron por delegación explícita de Diego
—*«hacé lo que creas mejor con esas 2 no bloqueantes»*—:

**Av. Montes de Oca entra como la referencia 42, con ficha escrita.** Sostenía una lámina, una
verificación de campo y una fila del cruce con el relevamiento oficial de ejes, y existía sólo en la
capa de las 124. Su ficha se apoya en trayectoria, anclaje normativo y reconocimiento externo, que
están documentados; **queda pendiente medirla con las seis vías**, y eso está declarado adentro.

**Las Cañitas ya no es una caminata: está resuelta en disco.** La diferencia entre nuestros 361
locales y los 97 de La Nación **no es un error de nadie: son taxonomías distintas.** Ellos contaron
dos rubros —46 cafés y 51 restaurantes— dentro de su propio censo de **856 locales comerciales
activos en 53 manzanas**; nosotros contamos toda la gastronomía en 82 hectáreas. Lo que falta no es
caminar: es cruzar rubro por rubro sobre el mismo perímetro, y ya está anotado como tal.

**Y una que le vuelve cuando el repositorio termine:** la firma del **nombre de la cuarta subzona
de Palermo**. La propuesta —«Palermo — eje Av. Santa Fe»— está escrita y medida, pero **no se le
puede pedir la firma sin el perímetro en calles**, y ese perímetro hay que medirlo sobre la caja
`-58,43404 · -34,59232` a `-58,42101 · -34,58240`. Proponer un perímetro sin medirlo ya falló dos
veces en este proyecto.

### Cerrado en la ronda 13 · segunda vuelta

| pregunta | respuesta |
|---|---|
| ¿La cuarta pieza de Palermo se llama «eje Av. Santa Fe»? | **No, y la medición lo refutó.** Av. Santa Fe tiene **0 metros dentro del paño y está a 251 metros**. Los 191 m de Santa Fe del polo que lo sugería están en la parte que queda **afuera** |
| ¿Se le puede poner perímetro en calles? | **No.** De sus 4.645 m de borde, sólo **709 —el 15 %—** corren sobre alguna calle; las largas lo atraviesan. **Una figura cuyo borde no corre sobre calles no es una zona: es un residuo**, y se publica como resto sin nombre |
| ¿Sirve TripAdvisor para verificar vigencia? | **No: responde 403 a pedidos automáticos.** La ruta que sí cierra es prensa fechada con reporteo a nivel establecimiento |
| San Bernardo, Británico, La Biela | **Los tres verificados abiertos** — 08/06/2026, 18/04/2026 y 15/10/2025 |
| ¿Costanera Norte cierra? | **No.** El Patio resuelve por página oficial **sin fecha** —resuelve la fila y no se cita— y Happening **no resuelve**: un copyright 2026 no es evidencia de actividad |
| ¿Recoleta es «la calle fantasma»? | **No en presente.** La nota es de 2017 y **el mismo diario publicó en 2021 que la cuadra se recuperó.** Seis cierres cargados entre 2013 y 2017, y la cuadra reocupada con otros rubros |

### Lo que se cerró el 09/08 y no vuelve a abrirse

| decisión | resolución |
|---|---|
| **Los niveles de nombre de las 41** | **ACEPTADOS por Diego.** 0 normativos · 3 oficiales de facto · 27 de uso corriente · 11 de trabajo. Con dos cambios de nombre: «Centro y Microcentro» y «Monserrat y Congreso» |
| **Plaza Asturias y El Globo** | **VERIFICADOS ABIERTOS.** El Globo, historia en canal propio del 09/08/2026, v2. Plaza Asturias, foto en canal propio del ≈02/08/2026, v2. Verificación humana directa de Diego. **La lámina 5 queda liberada** |
| **ERR-09 · la vía C de Monserrat** | **Aplicada por Cowork por delegación de Diego.** Pasa a «no abre»: la decisión 1 del 07/08 ya había resuelto que una feria itinerante no abre esa vía, y nunca había llegado al archivo. Monserrat entra igual, con cuatro vías |
| **ERR-08 · las seis vías de Almagro** | Aplicada en la lámina 4 de la v2.2 |
| **Las 8,09 ha de doble conteo** entre Palermo y Chacarita–Colegiales | **No es una decisión de criterio: los perímetros publicados no se tocan.** Se declara en las dos fichas y no se suman. Ya está escrito así en las dos |

### Un hallazgo de hoy que abre D5, y hay que entenderlo antes de firmarlo

**El corredor de Av. Montes de Oca sostiene la lámina 12 y una de las tres caminatas, y no está
entre las 41.** Buscado en el corpus, Barracas aparece sólo como parte de Boulevard Caseros
(Barracas / San Telmo). En las 124 concentraciones **sí existe: es P066 «Av. Montes de Oca», nivel
3, uso corriente como corredor comercial.**

**Y hay una colisión de identificadores que hay que arreglar antes de que muerda.** El id **P008**
designa dos cosas distintas según qué archivo se abra:

- en `POLOS_NOMBRADOS.csv`, de las 124: **P008 = «Distrito de Diseño (Barracas)»**, nivel 1, Ley 4761/2013
- en el modelo de ficha y en el cruce del IDECBA: **P008 = «Barracas · Av. Montes de Oca»**

Los dos son de Barracas, los dos son plausibles, y **quien lea «P008» sin saber de qué numeración
viene va a describir el polo equivocado.** Es errata nueva: **ERR-11.**

### Le toca al repositorio

1. **El mapeo P ↔ R/Z, por contención geométrica.** No existe: `POLOS_NOMBRADOS.csv` tiene sólo
   P-ids y ni una mención de los R. **Sin él no se puede armar el Anexo B ni cerrar ERR-11.** Es lo
   que más destraba.
2. **ERR-11 · la colisión de P008**, que sale del punto anterior.
2b. **ERR-12 · Defensa 695 está asignada a dos establecimientos.** El catálogo la da a Bar Seddon,
   en Monserrat, y la verificación del Bar Británico llegó con la misma altura. **Dos
   establecimientos no comparten una puerta.**
3. **El bug del normalizador de calles**, vivo en **9 de los 124** polos de `POLOS_NOMBRADOS.csv`
   —la misma calle repetida en su propio top de ejes—. `callejero_canonico.py` arregla esa familia
   y el arreglo nunca se propagó a ese archivo. **El campo se publica.**
4. **La vía C de Nueva Pompeya** — mismo defecto que Almagro, con objeto nombrado. Señalado en la
   ronda 13 y fuera de su alcance.
5. **El perímetro de Colegiales sobre la cuña real** — Zabala 254 m y Virrey Avilés 344 m son los
   únicos cruces con tramo verificable. Tres cuadras, no diez.
6. **Las dos ampliaciones medidas antes y después** — Federico Lacroze y La Paternal—, verificando
   que el polígono nuevo contenga al viejo sin perder superficie.
7. **Los 10 `requiere_cruce` de la vía E** — es un cruce espacial, no investigación. Llevaría esa
   vía del 84 % a cerca del 95 %.
8. **La vía B recorrida contra el catálogo cargado** — cero requests.
9. **Atribuir el eje Triunvirato a Villa Urquiza** en el cruce del IDECBA: el eje que releva la
   Ciudad es casi exactamente el perímetro declarado de esa referencia, y el cruce la marca como
   que no está en el atlas.
10. **Las 5 zonas pendientes de límites.**
11. **ERR-17 · las cuatro zonas del sur que cumplen el criterio y están afuera** — Z51 Iriarte, Z52
   La Boca Necochea, Z53 La Boca Caminito, Z54 Pompeya Sáenz. **Y medir el reparto de dos de
   ellas**: Z51 contra Z50 y R11, Z54 contra Z40. Se mide, no se decide.
12. **ERR-18 · recalcular `n_vias` desde las columnas de vía** en `fichas_corpus_polos.csv`. Cinco
   filas se contradicen a sí mismas —R02, R04, R05, R19, Z37—. Ninguna cambia de categoría.
13. **ERR-19 · la fila R03 de `via_E_22_referencias.csv`** tiene un campo con comas sin entrecomillar
   que desborda `via_E_rutas_n` y `fecha_relevamiento`.
14. **Z55 · ¿la feria de 840 m sobre Av. Mariano Acosta es una FIAB?** Dos rondas propias en
   contradicción, nunca cerrada. **De esto depende que la Comuna 8 tenga o no tenga un polo.**

### Le toca a Cowork

**Hecho el 09/08 a la noche, después del criterio:**

- ~~Reescribir la Sección I con el criterio y las cuatro categorías~~ · hecho
- ~~Escribir la Sección VIII con las 14 zonas no admitidas, vía por vía~~ · hecho, y las cinco que
  salieron de la VII se mudaron enteras
- ~~Cuatro fichas nuevas del sur~~ · hechas, dos de ellas de La Boca
- ~~Cartografía~~ · **hecha**: mapa general y catorce comunales, en `cartografia/`, reproducibles
- ~~Ensamblar el documento~~ · **hecho**: `documento/ATLAS_V3_DOCUMENTO.md`
- ~~Maquetar~~ · **hecho**: `documento/Atlas_V3_agosto_2026.pdf`, 103 páginas
- ~~Verificación interna~~ · **hecha**: ninguna cifra contradice a otra

**Pendiente de este lado:**

1. **Consolidar la edición técnica con las rondas 8 a 14** — **en stand-by por decisión de Diego.**
   No entra en esta entrega.
2. **Segunda pasada de cartografía**, si aparecen los polígonos oficiales de barrios y comunas: hoy
   el mapa se orienta con los 27 polígonos administrativos que ya estaban en `zonas_r8`.
3. **Rehacer los mapas** de las zonas cuyo perímetro se trace, y con ellos el PDF. Es una corrida de
   dos scripts.

**EL DOCUMENTO ESTÁ COMPLETO** en el sentido de que ninguna sección quedó sin escribir. Lo que abrió
el criterio del 09/08 es reescritura, no investigación.

### Lo que trajo la ronda 14 de Codex, y verificado contra sus archivos

**El mapeo entre los 124 y los 42 existe:** 171 pares, 105 concentraciones adentro de algún polo,
**19 afuera con 1.451 locales — el 11,4 % de todo lo que el atlas contabiliza.** Y las 124 suman
exactamente 12.688 locales, que es la cifra publicada: **el control cierra solo.**

| hallazgo | qué es |
|---|---|
| ~~La Boca no fue evaluada~~ **REFUTADO EL 09/08 · ERR-17** | **Sí fue evaluada, el 07/08, con las seis vías, y sus dos zonas entraron.** Lo que nunca pasó fue que el resultado se trasladara al corpus: los ids Z50–Z56 existen en un solo archivo del repositorio y ninguna ronda posterior los tomó. Dos concentraciones con 157 locales, seis Bares Notables con cinco abiertos, y la delimitación más precisa de todo el sur —340 metros lineales, de obra pública de enero de 2026— |
| **Palermo tiene 584 locales afuera de su sistema** | Seis concentraciones —Botánico, Pacífico, Villa Freud, Gascón y Honduras, Plaza Italia, Alto Palermo— que el sistema de 1.916 no toca. **La pregunta abierta no es cómo se llama la pieza que sobra adentro: es hasta dónde llega Palermo** |
| **Los polos cubren catorce comunas** | La **Comuna 8** tiene tres concentraciones con 259 locales y **ningún polo admitido**. Es un resultado, no un hueco: se barrió con el mismo umbral y ninguna alcanzó el criterio. **Y desde el 09/08 la respuesta es simétrica:** Villa Lugano falla exactamente lo mismo que falla Villa Pueyrredón, que sí está publicada; la diferencia no es de evidencia sino de antigüedad, y ahora está declarada. **Queda un cabo suelto que decide el asunto: Z55, la feria de 840 m sobre Av. Mariano Acosta, con dos rondas propias en contradicción** |
| **Montes de Oca no es continuo puerta a puerta** | 8,9 % a 40 metros · **71,3 % a 120**, la proporción más alta de todas las zonas medidas. La lámina 12 cambió la frase: **«continuo a escala de cuadra»** |
| **El Barrio Coreano es el único de los 42 sin ninguna concentración adentro** | Coherente con cómo entró —comunidad, corredor, reconocimiento— pero es el único polo que ningún instrumento detecta y ninguna dirección confirma |

### Lo que Cowork verificó el 09/08 · trece establecimientos

**Diez verificados abiertos, uno probablemente abierto, dos que no cierran.** Detalle en
`RONDA_DE_VIGENCIA_COWORK.md` y `verificaciones_cowork_2026-08-09.csv`.

**Puerto Madero pasó de cero verificaciones a cuatro; Recoleta a cinco; Av. Corrientes a tres.** De
las 42 fichas **queda una sola donde los referentes no cerraron después de buscarlos: Costanera
Norte.**

**Y tres hallazgos que valen más que el conteo:**

**«Bar del Alvear» no existe.** El atlas lo tenía cargado como referente de Recoleta y **el hotel
nombra seis locales, ninguno con ese nombre.** El hotel está operando y verificado; lo que no se
puede verificar es un local que no se puede identificar. Falta decidir cuál de los seis era.

**Celta Bar no tiene rastro desde octubre de 2025, y tampoco tiene evidencia de cierre.** Es
ausencia de rastro, no prueba de cierre, y **es el caso donde más rinde una mirada a redes.**

**Un patrón de defecto nuevo, que sale de La Giralda:** su reseña más nueva está **escrita dentro de
ventana y relata una visita de julio de 2025.** Las plataformas muestran dos fechas y **sólo la de
la visita dice algo sobre la actividad del local.** Regla que sale de ahí: en una reseña vale la
fecha de la visita, no la de publicación.

**Y dos límites del método, confirmados:** Instagram y Facebook están bloqueados para cualquier
agente automático —ese frente es de Diego—, y **la lectura de reseñas no es determinista**: pasadas
sucesivas sobre la misma dirección dieron resultados distintos, y una omitió una reseña que habría
cambiado un veredicto. **Se lee dos veces por rutas distintas o no está verificado.**

---

## 6 · Lo que no se toca

El criterio de admisión, las escalas de evidencia, las 16 reglas y los 23 defectos de fuente están
cerrados y documentados en `EDICION_TECNICA_METODO.md`,
`EDICION_TECNICA_FASE_DOCUMENTAL.md` y `agent_skills/shared/datagastro_metodo_experimental.md`.

Lo mínimo que hay que tener presente al producir:

**Las seis vías** — se entra por cualquiera. A, C y F se miden sobre el polígono; B, D y E sobre la
zona, y las filas las heredan por referencia. **La herencia no vale hacia arriba.**

**Vía C** — se abre por centralidad, no por concentración de oferta bajo un techo. La prueba: ¿el
objeto organiza su entorno, o fue puesto en él? **Y exige un objeto en actividad, nombrado.**

**Vigencia** — v1 a v5 con veredictos. Un acto jurídico no es un hecho operativo. La evidencia
negativa se busca, no se espera. **Toda verificación vence y lleva su fecha pegada al texto.**

**Lo que se puede sumar** — los 124 polígonos son disjuntos, con solape medido 0,0 %, y dan
**12.688 locales en 3.128,5 ha: el 53 % de la gastronomía en el 15 % de la superficie.** La matriz
de 94 filas **no se suma nunca.**

**La pregunta cero, antes de afirmar cualquier cosa:** ¿esto es una propiedad del territorio o de
mi instrumento? Ya falló seis veces y siempre en la misma dirección: **la lectura territorial es la
más noticiosa.**

**Y las restricciones de Diego:** el bloque para el repositorio va último · no se piden fuentes
internas · nunca «Atlas V2» en el documento · las 22 referencias sólo se amplían · nada se descarta
sin detallar qué sería.

---

## 7 · Dónde está cada cosa · verificado en disco el 09/08

```
outputs\BARRIDO_CIUDAD_2026-08\
├── desde_cowork\                  EDICION_TECNICA_METODO.md
│   │                              ATLAS_V3_SECCIONES_I_IV_VII.md     (I, III, IV)
│   │                              ATLAS_V3_SECCIONES_V_VI.md         (VIII y el Anexo A)
│   │                              POLOS_NOMBRADOS.csv                (los 124, con nivel de nombre)
│   └── evidencia_2026\            ATLAS_V3_SECCIONES_II_V_VI_IX.md   (II, V, VI, IX)
│                                  SECCION_VII_REFERENCIAS_PUBLICADAS.md  (22 de 41)
│                                  TABLERO_ATLAS_V3.md                (este archivo)
│                                  LAMINAS_v2.2_2026-08-09.md
│                                  NIVELES_DE_NOMBRE_41.md y .csv
│                                  catalogo_90_estado_final.csv
│                                  fichas_corpus_polos.csv            (las 48 evaluadas)
│                                  INDICE.csv · correspondencia_fase_documental.csv
├── hitos\hitos_capa_2026_r11.csv  225 × 46 · la capa vigente
├── seis_vias\seis_vias_94_filas_r12.csv y _22_zonas_r12.csv
├── ronda_9..13\                   las narrativas y sus CSV
└── ronda_12\idecba_48_autoridad.csv   la serie de 48 · manda sobre el PDF
```

**`hitos/`, `seis_vias/`, `ronda_*/` e `idecba/` cuelgan de `BARRIDO_CIUDAD_2026-08`, no de
`evidencia_2026`.** El handoff los ubicaba mal y por eso se los daba por inexistentes.

---

## 8 · Los porcentajes, al cierre del 9 de agosto

| frente | estado |
|---|---|
| criterio de admisión | **100 % · uno solo, escrito, calibrado y aplicado a las 55** |
| cobertura geográfica | 100 % · 15 comunas barridas, 14 con polo |
| vigencia del catálogo de Notables | 100 % · 90 de 90 |
| estructura del documento | 100 % |
| **texto del documento** | **100 %** · secciones I a IX y los tres anexos |
| el cuerpo | **41 fichas, agrupadas por comuna** |
| referentes con fecha propia | **40 de las 41 fichas** · la única sin cerrar es Costanera Norte |
| **cartografía** | **100 % de una primera pasada** · mapa general y catorce comunales, reproducibles |
| **maquetación** | **100 % de una primera pasada** · PDF A4 de 103 páginas, con tapa, índice y folios |
| **verificación interna** | **100 %** · ninguna cifra del documento contradice a otra |
| delimitación de polígonos | **56 %** · 23 polos con perímetro propio, **18 se representan con su barrio** |
| vía E medida | 84 % · 79 de 94, con 10 que son un cruce espacial |
| vía B medida | 67 % · 63 de 94, y sube sola al recorrerla contra el catálogo |
| edición técnica | **en stand-by por decisión de Diego** · no entra en esta entrega |
| presentación | **v2.3**, ninguna lámina retenida |

**El cuello de botella cambió de lugar dos veces en un día.** Dejó de ser el dato, después dejó de
ser la forma —hay documento armado, con mapas y maqueta—, **y hoy es uno solo: los dieciocho
perímetros que faltan trazar.** Mientras no estén, dieciocho de los cuarenta y un polos se dibujan
con el polígono de su barrio y **no pueden publicar superficie ni cantidad de locales**. Eso está
declarado en el mapa, en cada ficha y en la sección VIII — pero es lo único que separa a este atlas
de estar terminado.

**Y es trabajo de repositorio, no de análisis.** El material textual de los dieciocho perímetros ya
está escrito en las fichas: calles y alturas. Lo que falta es poligonizarlo.
