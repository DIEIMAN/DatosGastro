# Informe de auditoría externa (red team) — Corrida territorial V3

**Rol:** `auditor_externo_red_team`  
**Fecha:** 2026-07-11  
**Ámbito:** Belgrano, Recoleta, Costanera Norte  
**Marca de trabajo:** DGDGAS / DataGastro (uso interno de línea)  
**Alcance de esta auditoría:** coherencia territorial, claridad pública, riesgos de sobreinterpretación, legibilidad de mapas, solidez argumental y objeciones externas.  
**No abarca:** reauditoría de hashes, regeneración cartográfica, edición de geometrías ni integración al PDF.

---

## 0. Método de revisión

### Insumos leídos (solo lectura)

| Bloque | Ruta |
|---|---|
| Corrida documental V3 | `docs/polos_gastro/corrida_territorial_v3/` |
| Outputs V3 + mapas | `outputs/polos_gastro/corrida_territorial_v3/` (incl. 15 PNG) |
| Pack de revisión | `REVISION_CORRIDA_TERRITORIAL_V3.zip` y extracción QA asociada |
| Evidencia documental | `docs/polos_gastro/evidencia_documental_integrada_v1_1/` |
| Preintegración editorial | `docs/polos_gastro/preintegracion_editorial_v3/` |
| Preflight cartográfico | `docs/polos_gastro/preflight_cartografico_v3_1/` |
| Superficies protegidas | `docs/polos_gastro/PROTECTED_SURFACES.yaml` |
| Decisiones humanas | `DECISIONES_Y_USOS_DOCUMENTALES.md` (V1.1) + `DECISIONES_CARTOGRAFICAS_VIGENTES_V3_1.md` |

### Decisiones cerradas (no reabiertas)

- **Belgrano:** un polo; BEL-A; tres centralidades; Belgrano R = sector secundario.
- **Recoleta:** un polo; REC-A; nueve núcleos solo analíticos; no nueve polos.
- **Costanera Norte:** un polo; cuatro componentes; CN_C02 pleno; cuerpo principal; DEC-10 prevalece.

### Criterio de veredicto

Se separan validez territorial, coherencia documental, claridad institucional, aptitud visual y riesgos pendientes. Un hallazgo visual o de lenguaje **no** reabre la decisión territorial si la geometría y la evidencia se sostienen.

---

## PARTE 1 — Coherencia territorial

### 1.1 Belgrano (modelo BEL-A)

#### Lectura del resultado

| Indicador | Valor V3 | Lectura red team |
|---|---|---|
| Universo de puntos | 697 | Contenedor de trabajo, no “todo el barrio de Belgrano” como polígono oficial |
| Puntos incluidos | 248 | Núcleos densos del polo |
| Cobertura | **35,58 %** | Proporción del universo de puntos dentro de la geometría multiparte; **no** es “el 35 % del barrio es polo” |
| Componentes / centralidades | 3 | Emergen a umbral 160 m (sensibilidad documentada) |
| Piezas topológicas | 7 | Fragmentación geométrica interna; no son 7 polos |
| Estabilidad | 0,765 | Relativamente alta entre los tres polos |
| Dependencia externa | **53,23 %** | Limitación de fuente, no de existencia del polo |
| Superficie | 0,3975 km² | Compacta; densidad ~624 pts/km² |

#### Coincidencia con evidencia documental V1.1

La evidencia periodística e institucional de trabajo (BEL-E03…E14) describe una **centralidad dominante** Barrio Chino–Belgrano C–Barrancas–Pasaje Echeverría, un **eje** Cabildo–Juramento con menor sedimentación de nombre, **Bajo Belgrano** con denominación periodística y límites difusos, y **Belgrano R** como oferta más dispersa. Turismo BA no lista a Belgrano entre polos clásicos: eso se declara en método y no impide la definición de trabajo.

BEL-A responde razonablemente a ese relato: no dibuja un hull gigante del barrio; no fuerza cuatro polígonos equivalentes; mantiene Belgrano R como sector secundario con geometría propia sin promoverlo a subpolo. El umbral de 160 m (3 componentes) frente a 120 m (6 fragmentos) y 250 m (fusión total) da un argumento técnico defendible para no adoptar BEL-B ni un polígono único artificial.

#### Saltos lógicos y riesgos

1. **Cobertura baja mal leída.** Un lector puede concluir que “Belgrano casi no es polo”.  
   **Respuesta correcta:** la cobertura mide puntos del universo de trabajo capturados por las centralidades densas; el resto del barrio concentra oferta dispersa o de contexto. El polo no es sinónimo del barrio administrativo.
2. **Tres centralidades vs. siete piezas.** El mapa de presentación muestra varios polígonos verdes. Sin texto, se confunden piezas topológicas con centralidades o subpolos.  
   **Respuesta:** las piezas son el detalle geométrico; las centralidades son la lectura editorial (hasta tres). No publicar “siete centralidades”.
3. **Etiqueta compuesta** “Barrio Chino–… / Bajo Belgrano”. Agrupa en un solo rótulo la centralidad principal y Bajo Belgrano, lo que debilita la jerarquía interna que el texto sí separa.  
   **Respuesta editorial:** acortar y separar rótulos (ver Parte 2 y 6).
4. **BEL-A como decisión post hoc de nombres.** Los nombres no supervisaron el clustering (correcto metodológicamente). DH-05 sigue diferida para firma de nombres públicos: el handoff ya propone topónimos; el informe no debe presentarlos como nomenclatura oficial GCBA.

#### ¿La geometría explica territorio o solo “cierra el gráfico”?

Explica territorio: evita hull común, respeta discontinuidad entre centralidades y no rellena vacíos. No es un contorno cosmético del barrio.

#### Cómo explicar la cobertura 35,58 % sin desautorizar el polo

Texto sugerido (institucional):

> El Polo Gastronómico Belgrano se identifica a partir de **centralidades densas** de oferta registrada/visible, no como la totalidad del barrio. La cobertura del modelo (35,6 % del universo de puntos de trabajo) muestra que una parte relevante de la señal queda fuera de esos núcleos y se lee como contexto o dispersión barrial. Esa lectura **refuerza** la idea de polo con estructura interna, en lugar de un relleno superficial del perímetro administrativo.

Cifras a preferir en cuerpo: existencia del polo único; tres centralidades; Belgrano R secundario.  
Cifras a reservar para método: 35,58 %; 7 piezas; 53,23 % dependencia; 449 sin asignar; códigos BEL-A.

---

### 1.2 Recoleta (modelo REC-A)

#### Lectura del resultado

| Indicador | Valor V3 | Lectura red team |
|---|---|---|
| Universo | 767 | Contenedor de trabajo |
| Incluidos | 602 | Alta captación de la señal densa |
| Cobertura | **78,49 %** | Coherente con polo de alta densidad |
| Componentes | **1** | Unidad continua (con huecos internos) |
| Núcleos absorbidos | 9 | Solo estructura analítica interna |
| Estabilidad | **0,626** | Media; no es “certeza absoluta” |
| Superficie | 1,218 km² | Envolvente irregular, no relleno rectangular |
| Dependencia externa | 46,51 % | Comparable a Belgrano; no descalifica |
| Riesgo fragmentación / unión artificial | BAJO / BAJO | Favorable a REC-A |

#### Coincidencia con evidencia documental V1.1

Recoleta es el polo con **mayor respaldo institucional directo** (Turismo BA: “primero y más viejo”, REC-R01). La documentación describe **corredor con nodos** (Junín–Vicente López; Alvear–Posadas), no nueve polos ni una centralidad única tipo Barrio Chino. REC-R02 (~150 restaurantes) está **rechazada** (cifra de San Telmo): no aparece en métricas V3 publicables como oferta de Recoleta.

REC-A reduce los nueve núcleos HDBSCAN a **una unidad pública**, con huecos que respetan predios (cementerio, plazas, equipamientos). REC-B (dos subzonas) es casi equivalente en cobertura (78,36 %) pero introduce una división no imprescindible y baja la claridad institucional (matriz de decisión: MEDIA vs. ALTA). REC-C fragmenta sin mejorar la lectura pública.

#### Saltos lógicos y riesgos

1. **Forma irregular leída como “envolvente arbitraria”.**  
   **Respuesta:** la forma sigue la nube densa; los huecos internos son predios no gastronómicos, no “errores de dibujo”.
2. **Nueve núcleos = nueve polos.** Riesgo residual si se filtran mapas analíticos o jerga técnica.  
   **Respuesta:** los núcleos no se comunican como polos; no rotular N01–N09 en informe político.
3. **Borde hacia Retiro.** La documentación histórica (2011) habla de corredor hacia Posadas/Retiro; la corrida trata el borde sin expansión automática. Correcto, pero el mapa no etiqueta ese límite: el texto debe decir que **corredor ≠ fusión de barrios**.
4. **Estabilidad 0,626.** No es baja al punto de invalidar; tampoco autoriza lenguaje de certeza total. Una vez en método alcanza.

#### ¿REC-A se entiende mejor que REC-B en informe institucional?

**Sí.** Para jefatura y lectura pública, una unidad con huecos es más simple que “dos subzonas” con diferencia métrica mínima. REC-B es buen **respaldo técnico** (anexo / QA), no el mensaje principal.

#### Unidad territorial vs. envolvente cartográfica

La geometría de presentación es una **definición de trabajo del estudio** sobre oferta densa, no el límite del barrio Recoleta ni un perímetro administrativo. Debe decirse una sola vez en la nota metodológica de cartografía.

---

### 1.3 Costanera Norte (modelo CN-DEC10)

#### Lectura del resultado

| Indicador | Valor V3 | Lectura red team |
|---|---|---|
| Universo | 72 | Pequeño; alta cobertura relativa |
| Incluidos | **71** | +1 señal de borde sin asignación |
| Cobertura | **98,61 %** | Casi todo el universo técnico |
| Componentes | **4** | Discontinuos; alineados a DEC-05/DEC-10 |
| Piezas topológicas | 5 | Un componente puede tener más de una pieza |
| Separación min / max | 163,5 m / 2.727,5 m | Vacíos reales, no “fallas de dibujo” |
| Dependencia externa | **92,96 %** | Limitación de fuente; no reabre existencia |
| CN_C02 | 11 pts; 0 F01/F02 | Componente pleno por decisión; lenguaje acotado |

#### Coincidencia con evidencia documental V1.1

Turismo BA (restaurantes clásicos y carritos), Ley 5.961/2018 (Distrito Joven, concesiones, integración con parques/Aeroparque), regularización de carritos (2013/2017), patio de containers y predios Costa Salguero–Punta Carrasco sostienen una **identidad multiparte discontinua**. La correspondencia post hoc V3 empareja CN_C01 y CN_C03 con confianza ALTA; CN_C02 y CN_C04 con PARCIAL — coherente con la regla “correspondencia imperfecta no elimina componente”.

DEC-10 prevalece correctamente sobre lecturas previas “exploratorias” o de anexo. No se proponen conectores artificiales.

#### Saltos lógicos y riesgos

1. **Dependencia 92,96 % = “el polo no es real”.**  
   **Respuesta institucional:** la existencia y la estructura multiparte se adoptan por evidencia documental + decisión institucional; la composición de fuentes se declara en método.  
   **Respuesta metodológica:** Places/señal externa no prueba habilitación; tampoco prueba ilegalidad.
2. **CN_C02 sin F01/F02 = informalidad o ilegalidad.**  
   **Prohibido** afirmarlo. Permitido solo como hipótesis metodológica de tipología (puestos, carritos, concesiones, subregistro, otro domicilio).
3. **Cuatro componentes no etiquetados en el mapa de presentación.** Un solo rótulo “Polo Gastronómico Costanera Norte” sobre un extremo puede leerse como un único blob o como “solo ese tramo es el polo”.  
   **Ajuste editorial de rótulos** (no de geometría): nombres descriptivos post hoc o “Componente 1–4” sin códigos técnicos si se desea sobriedad.
4. **Espacio vacío del lienzo.** La discontinuidad ribereña genera mucho blanco; a media página puede parecer “mapa incompleto”. El pie debe anticipar: *los vacíos son parte de la estructura territorial*.

#### Confusión subregistro / informalidad / ilegalidad

| Concepto | Uso permitido |
|---|---|
| Subregistro administrativo | Hipótesis metodológica (una vez) |
| Tipología puesto/carrito/concesión | Caracterización documental respaldada |
| Informalidad / ilegalidad / falta de habilitación de locales concretos | **No** sin evidencia oficial |
| “Señal externa almacenada” | Lenguaje técnico; preferir “fuente externa de localización” en público |

No se cuestiona la existencia del polo ni se propone eliminar componentes.

---

## PARTE 2 — Revisión visual de mapas

Clasificación usada:

- **LISTO_PARA_INFORME** — usable en cuerpo con pie y nota metodológica estándar (ajustes de texto del PDF, no del PNG, o ajustes cosméticos menores).
- **AJUSTE_MENOR** — usable si el integrador corrige leyenda/rótulos/subtítulo en composición o en regeneración liviana.
- **AJUSTE_IMPORTANTE** — no entra al cuerpo político hasta corregir legibilidad o riesgo de lectura.
- **NO_USAR_EN_INFORME** — solo anexo técnico / QA, o descartar del PDF político.

Detalle por archivo: `QA_VISUAL_EXTERNO_MAPAS_V3.csv`.

### Síntesis por polo

#### Belgrano

| Mapa | Clase | Motivo principal |
|---|---|---|
| 01 analítico | NO_USAR_EN_INFORME (cuerpo) | Capa técnica; útil en anexo metodológico |
| 02 presentación | **AJUSTE_IMPORTANTE** | Etiqueta principal demasiado larga; fusión visual centralidad principal + Bajo Belgrano; mucha franja vacía al este; subtítulo con código BEL-A |
| 03 comparativo | **NO_USAR_EN_INFORME** | No muestra geometrías de modelo de forma legible; solo nube de puntos; no sostiene la decisión BEL-A frente a B/C para un lector externo |
| 04 puntos/cobertura | NO_USAR_EN_INFORME (cuerpo) | Sin leyenda de símbolos; lenguaje de “asignación” |
| 05 vacíos | AJUSTE_IMPORTANTE / anexo | Segmentos y cotas se solapan; buen argumento técnico de no-conectores si se limpia |

#### Recoleta

| Mapa | Clase | Motivo principal |
|---|---|---|
| 01 analítico | Anexo / NO_USAR cuerpo | Muestra bien la unidad con huecos; jerga F01/F02 |
| 02 presentación | **AJUSTE_MENOR** → casi listo | Forma y huecos se entienden; un solo nombre de polo; falta pulir subtítulo (REC-A), leyenda técnica y pie “EXPERIMENTAL” |
| 03 comparativo | Anexo metodológico | Útil para defender REC-A vs B/C; no para página de ficha política |
| 04 cobertura | NO_USAR cuerpo | Sin leyenda de estados de punto |
| 05 vacíos | Anexo | Cotas solapadas; mensaje “no son conectores” correcto en subtítulo |

#### Costanera Norte

| Mapa | Clase | Motivo principal |
|---|---|---|
| 01 analítico | Anexo | Cuatro tramos visibles; sin nombres; F01/F02 |
| 02 presentación | **AJUSTE_IMPORTANTE** | Un solo rótulo en el componente SE; el cuarto tramo y la lógica multiparte no se leen en media página; exceso de vacío SW; código CN-DEC10 en subtítulo |
| 03 comparativo | **NO_USAR_EN_INFORME** | Un solo panel; pie colisionado (“administrativo” vs. “Fuente”); QA interno ya marcó REVISAR |
| 04 cobertura | Anexo / NO_USAR cuerpo | Sin leyenda; pocos puntos |
| 05 vacíos | **AJUSTE_MENOR** (anexo fuerte) | Mejor pieza para explicar discontinuidad y distancias; apto para caja metodológica si se acorta el lienzo |

### Riesgos de malinterpretación visual (transversales)

1. Puntos naranja/azul leídos como “ilegales vs. habilitados” → deben ser “fuente pública / fuente externa”.
2. Polígonos leídos como límite barrial oficial → pie único de no-oficialidad.
3. Costanera: un rótulo = un solo predio.
4. Belgrano: muchas piezas = muchos polos.
5. Comparativos Belgrano/Costanera no cumplen función de “demostrar elección de modelo” en estado actual.

---

## PARTE 3 — Lenguaje público

### Hallazgos

| Elemento actual | Problema | Reemplazo institucional sugerido |
|---|---|---|
| `EXPERIMENTAL / NO OFICIAL` (banner en cada mapa) | Debilita en exceso si se repite en todas las páginas; suena a borrador descartable | Una sola vez: *“Definición territorial de trabajo del estudio; no constituye límite administrativo oficial.”* |
| Códigos `BEL-A`, `REC-A`, `CN-DEC10` en subtítulos de mapa | Jerga de corrida; no aporta a jefatura | Reservar a metodología/anexo; en mapa: “Modelo de presentación adoptado” o sin código |
| “Geometría experimental” | Enfatiza provisoriedad más que adopción | “Delimitación de trabajo” / “geometría de presentación del estudio” |
| “No constituye límite administrativo oficial” | Correcto y necesario | Mantener **una vez** (nota cartográfica + método); no en cada párrafo del cuerpo |
| “Oferta registrada/visible” | Correcto frente a “locales activos” | Mantener; preferible a “actividad gastronómica” sin matiz |
| “Señal externa almacenada” | Técnico; puede confundirse con vigilancia | “Fuente externa de localización (previamente almacenada)” |
| `F01/F02` en leyenda de mapa político | Opaco para no técnicos | “Registro público de oferta / habilitación” vs. “Fuente externa” (formulación a pactar con editor; sin prometer “habilitados”) |
| “Modelo recomendado: …” | Tono de laboratorio | “Lectura adoptada para este informe” |

### Textos del handoff cartográfico

Los pies sugeridos en `HANDOFF_CARTOGRAFICO_INTEGRADOR_V3.md` son metodológicamente correctos pero **demasiado densos** si se apilan los tres en cada mapa. Recomendación: un pie corto + remisión a la nota metodológica única.

### Coherencia con preintegración (TO-01…TO-14)

La matriz de textos obsoletos de preintegración V3 está alineada con esta auditoría: hay que retirar “observación/exploratoria” de Costanera y “zonas en observación” para Recoleta/Belgrano. La corrida V3 **no** reintroduce esas formulaciones en los resultados por polo; el riesgo está en el PDF político heredado, no en los markdown V3 de resultados.

---

## PARTE 4 — Coherencia documental

### Contrastados

| Tema | Estado |
|---|---|
| Nombres de polos (Belgrano / Recoleta / Costanera Norte) | Alineados V1.1 + V3 |
| Tres centralidades Belgrano + R secundario | Alineado; DH-05 de firma de nombres sigue abierta |
| Nueve núcleos Recoleta no públicos | Alineado (REC-A) |
| REC-R02 no usada como cifra de Recoleta | Cumple |
| DEC-10 + CN_C02 pleno + 4 componentes | Cumple |
| Evidencia Grok + correcciones Perplexity (p.ej. vacío previo Costanera) | Linaje documentado; no se reabre |
| Correspondencia Costanera post hoc | EMPAREJADA / PARCIAL; no se elimina por parcial |
| Documentación no supervisó clustering | Declarado y coherente con método |

### Clasificación de afirmaciones (guía para el integrador)

| Afirmación | Tipo |
|---|---|
| Existe un Polo Gastronómico Recoleta (Turismo BA) | **Respaldada** (institucional) |
| Costanera tiene identidad pública de restaurantes y carritos | **Respaldada** |
| Belgrano es polo del listado clásico de Turismo BA | **No respaldada** → solo definición de trabajo (método) |
| Tres centralidades internas en Belgrano | **Parcialmente respaldada** (espacial + prensa; nombres post hoc) |
| Belgrano R no es subpolo en esta versión | **Decisión institucional** + coherencia espacial |
| Cuatro componentes Costanera | **Decisión institucional (DEC-05/10)** + reproducción espacial |
| CN_C02 es “informal” | **No afirmable** |
| Cobertura Belgrano 35,58 % | **Métrica de corrida** → cuerpo con cuidado / método |
| Estabilidad Recoleta 0,626 | **Solo metodología** |
| Dependencia Costanera 92,96 % | **Solo metodología** (una vez) |
| Nueve núcleos = estructura del polo público | **Incorrecta** si se publica así |

---

## PARTE 5 — Objeciones externas (resumen)

Detalle tabular: `MATRIZ_OBJECIONES_Y_RESPUESTAS_V3.csv`.

### Belgrano

1. **Técnica:** La cobertura es baja; el modelo deja afuera la mayoría de puntos.  
2. **Política/comunicacional:** “¿Por qué un polo si Turismo BA no lo nombra y el mapa no cubre el barrio?”  
3. **Respuesta institucional breve:** El polo se define por centralidades densas reconocibles, no por el perímetro del barrio ni por un listado único de fuentes.  
4. **Respuesta metodológica breve:** 35,6 % es cobertura del universo de puntos de trabajo sobre geometría multiparte a 160 m; la densidad interna es alta y la sensibilidad descarta hulls artificiales.

### Recoleta

1. **Técnica:** La envolvente es irregular, con huecos, y la estabilidad es solo media.  
2. **Política:** “Parece dibujado a ojo / demasiado amplio hacia el este.”  
3. **Institucional:** Un solo polo histórico consolidado; la geometría sigue la oferta densa y respeta predios no gastronómicos.  
4. **Metodológica:** REC-A maximiza parsimonia frente a REC-B/C con coberturas casi idénticas; los nueve núcleos no se publican como polos.

### Costanera Norte

1. **Técnica:** Más del 90 % de la señal es externa; un componente carece de F01/F02.  
2. **Política:** “Están institucionalizando informalidad / un mapa a medias.”  
3. **Institucional:** Polo adoptado con estructura multiparte y vacíos propios del frente ribereño; tipologías diversas (concesiones, puestos, predios) sin juicio regulatorio de locales.  
4. **Metodológica:** DEC-10 + DEC-05; dependencia de fuente se declara una vez; ausencia de registro público en un tramo no prueba ilegalidad.

---

## PARTE 6 — Recomendaciones para el informe

Ver también `RECOMENDACIONES_EDITORIALES_EXTERNAS_V3.md`.

### Mapas

| Polo | Usar en cuerpo (tras ajuste) | No usar en cuerpo |
|---|---|---|
| Belgrano | 02 presentación (tras acortar rótulos y limpiar subtítulo) | 03 comparativo; 04 cobertura; 01/05 solo anexo |
| Recoleta | 02 presentación (ajuste menor de leyenda/pie) | 03 solo si hay caja metodológica; 04/05 no |
| Costanera | 02 presentación **con rótulos de componentes** o composición que identifique 4 tramos; 05 como apoyo de vacíos | 03; 04; 01 solo anexo |

### Cifras

- **Mostrar con cuidado en cuerpo:** existencia de tres polos; estructura (3 centralidades / 1 unidad / 4 componentes); Belgrano R secundario; vacíos estructurales en Costanera.  
- **Reservar a método:** coberturas %; dependencias Places; estabilidades; piezas topológicas; 71/72; códigos de modelo; 9 núcleos; composición F01/F02 por componente.

### Nombres públicos

- Polo Gastronómico Belgrano / Recoleta / Costanera Norte.  
- Centralidades Belgrano en forma corta (evitar rótulo de una línea con 6 topónimos).  
- Costanera: denominaciones descriptivas del handoff documental, no marcas comerciales.  
- No: BEL-A, REC-A, CN-DEC10, CN_C0x, BEL_RV2_*, “nueve polos”, “150 restaurantes en Recoleta”.

### Aclaración metodológica única (comienzo del bloque cartográfico o nota final)

> Las delimitaciones de este informe son **definiciones territoriales de trabajo** elaboradas por DGDGAS a partir de oferta registrada o visible y de contraste documental. **No constituyen límites administrativos oficiales.** Los mapas distinguen, cuando corresponde, registros de fuentes públicas y señales de fuentes externas de localización; estas últimas no equivalen a habilitación ni a juicio sobre la situación regulatoria de establecimientos. En Costanera Norte, la mayor dependencia de fuente externa se declara como limitación de información y no modifica la adopción del polo ni de sus cuatro componentes discontinuos.

---

## PARTE 7 — Veredicto (síntesis)

| Dimensión | Juicio |
|---|---|
| 1. Validez territorial | **Aceptable y coherente** con decisiones cerradas y con la lectura documental V1.1 |
| 2. Coherencia documental | **Alta** (REC-R02, DEC-10, post hoc, sin reabrir polos) |
| 3. Claridad institucional | **Media** — requiere reescritura de subtítulos, pies y algunos rótulos |
| 4. Aptitud visual | **Desigual** — Recoleta casi lista; Belgrano y Costanera presentación con ajustes importantes; comparativos Belgrano/Costanera no aptos |
| 5. Riesgos pendientes | Sobrelectura de cobertura Belgrano; confusión piezas/centralidades; multiparte Costanera sin etiquetas; dependencia Places leída como ilegitimidad; jerga experimental repetida |

### Veredicto global

**`APTO_CON_AJUSTES_EDITORIALES`**

No se requiere revisión territorial de modelos (BEL-A / REC-A / CN-DEC10).  
No se modificó ningún archivo de la corrida original.

---

## Anexos de esta auditoría

- `MATRIZ_OBJECIONES_Y_RESPUESTAS_V3.csv`
- `QA_VISUAL_EXTERNO_MAPAS_V3.csv`
- `RECOMENDACIONES_EDITORIALES_EXTERNAS_V3.md`
- `VEREDICTO_AUDITORIA_EXTERNA_V3.md`
- `HANDOFF_RED_TEAM_INTEGRADOR_V3.md`

Copia espejo en `outputs/polos_gastro/auditoria_externa_red_team_v3/`.
