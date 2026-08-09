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

**Y una regla de frontera que costó cinco errores:** nadie afirma el contenido de un archivo que no
leyó. Cowork tiene lectura directa del repositorio por el puente. **Se lee, no se recuerda.**

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
| **I** | Presentación | escrita · pendiente el ajuste de cifras |
| **II** | Qué es un polo gastronómico | escrita, reescrita |
| **III** | De dónde salen los datos | escrita |
| **IV** | Cómo se leyó el territorio | escrita |
| **V** | Los referentes de la Ciudad | escrita |
| **VI** | Las comunidades y el territorio | escrita |
| **VII** | La Ciudad, comuna por comuna | **22 de 41 fichas escritas** |
| **VIII** | Lo que se midió y no alcanzó | escrita completa |
| **IX** | Qué no dice este atlas | escrita |
| **Anexo A** | Nota metodológica | **escrita** — deja de estar huérfana |
| **Anexo B** | Las 124 concentraciones detectadas | falta armar; los nombres y polígonos están |
| **Anexo C** | Correspondencia, glosario, fuentes y licencias | falta armar |

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
| `SECCION_VII_REFERENCIAS_PUBLICADAS.md` | **las 22 fichas de referencias publicadas** · reemplaza a la tanda 1 |
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
| ¿Hay que cargar Plaza Asturias y El Globo como hitos? | **No, y es decisión de la ronda 7:** no tienen registro oficial. Lo que falta es su vigencia | ronda 7 |
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

### Espera la firma de Diego · nada avanza sin esto

| # | qué hay que firmar | qué destraba |
|---|---|---|
| **D1** | **El nombre y el perímetro de la cuarta subzona de Palermo.** Propuesta medida: «Palermo — eje Av. Santa Fe», que explica 75 de sus 134 locales en un tercio de su superficie. No explica 27,47 ha y 59 locales | cierra Palermo entero |
| **D2** | **Las 8,09 ha y 7 locales de doble conteo** entre Palermo y el corredor Chacarita–Colegiales | cierra el nudo de Chacagiales |
| **D3** | **ERR-08 y ERR-09.** La primera ya está aplicada en la lámina 4; la segunda es pasar la vía C de Monserrat a «no abre», que la decisión 1 ordenó el 07/08 y nunca llegó al archivo. Ninguna cambia un veredicto de admisión | limpieza |
| **D4** | **Los niveles de nombre de las 41.** Propuesta completa, con la evidencia por fila. Cuatro casos convienen mirarse primero: Federico Lacroze, Liniers, Nueva Pompeya y el nombre de la referencia del Centro | destraba el encabezado de las 41 fichas |
| **D5** | **¿Av. Montes de Oca entra como referencia número 42, o queda en el anexo?** Ver el hallazgo de abajo | define si son 41 o 42 |
| **D6** | La vigencia de **Plaza Asturias y El Globo** — es lo único que le falta a la lámina 5 | libera la lámina 5 |
| **D7** | Las **tres caminatas** — Montes de Oca 280–1702, Av. Rivadavia en Flores, Las Cañitas | verifica lo que sólo se ve en la calle |

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

### Le toca a Cowork

1. **Las 19 fichas de zonas nuevas** — el resto de la sección VII.
2. **El Anexo B**, cuando exista el mapeo.
3. **Consolidar la edición técnica con las rondas 8 a 13.**
4. **El ajuste de cifras de la sección I**, que su propia cabecera anuncia y nadie hizo.

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
| criterio de admisión | 100 % |
| cobertura geográfica | 100 % · 15 comunas |
| vigencia del catálogo de Notables | 100 % · 90 de 90 |
| estructura del documento | **100 % · resuelta hoy** |
| niveles de nombre | **propuesta completa, esperando firma** |
| vía E medida | 84 % · 79 de 94, con 10 que son un cruce espacial |
| vía B medida | 67 % · 63 de 94, y sube sola al recorrerla contra el catálogo |
| delimitación de polos | ~85 % · Palermo a una firma, Colegiales y el solape Villa Crespo–La Paternal abiertos |
| **el cuerpo del documento** | **22 de 41 fichas** |
| edición técnica | ~90 %, con las rondas 8 a 13 por incorporar |
| presentación | **v2.2**, con la lámina 5 pendiente de dos verificaciones |

**El cuello de botella ya no es el dato ni la estructura: son las 19 fichas que faltan y siete
firmas.** Y de las siete, tres —el nombre de la subzona de Palermo, los niveles de nombre y las dos
erratas— tienen la propuesta escrita y sólo esperan un sí.
