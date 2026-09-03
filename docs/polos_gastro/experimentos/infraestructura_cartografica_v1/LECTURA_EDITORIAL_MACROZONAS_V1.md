# Lectura editorial — macrozonas candidatas V1

**Fecha:** 2026-07-09 · **Hecho por:** Claude, revisión editorial/cartográfica (sin tocar
scripts, geometrías ni generar outputs nuevos). Base: `REVISION_DGDGAS_MACROZONAS_CANDIDATAS_V1.md`,
cruzado con `FICHAS_TECNICAS_MACROZONAS_V1.md` y `QA_CORRECCIONES_BLOQUEANTES.md`.

**Para qué sirve este documento:** no es una nueva revisión técnica ni reemplaza el
documento de revisión. Es una lectura de si ese documento, tal como está escrito hoy,
le sirve a alguien de DGDGAS que lo abre sin contexto previo — y qué decisiones humanas
quedan pendientes antes de aprobar nada.

---

## 1. ¿Las fichas son claras para DGDGAS?

En general, sí. El documento de revisión (`REVISION_DGDGAS_...md`) está escrito en
lenguaje llano, sin jerga cartográfica, con la estructura pedida (qué se propone / qué
contiene / qué cambió / atención / pendiente) y checkbox de una sola marca. Es
razonable para alguien que abre el documento por primera vez.

Dos matices que vale señalar, no bloqueantes:

- **Falta la fecha y el "quién decide" en el encabezado de cada ficha**, aunque la
  sección de trazabilidad al final promete guardarlos. Si el documento se imprime o se
  reenvía por separado de esa última sección, se pierde el rastro de cuándo se completó.
  No es un problema de contenido, es un problema de que el campo fecha/nombre no está
  *en* cada ficha sino solo prometido al final.
- El documento dice "12 zonas... más 2 subzonas de Palermo" en la intro, pero después
  numera 14 entradas donde Palermo (zona 3) es una entrada de puro contexto que "no se
  usa para calcular nada". Alguien que cuenta rápido puede confundirse entre "14
  macrozonas" y "12 + 2 subzonas + 1 contextual = 15 conceptos distintos en 14 fichas".
  Sugerencia de redacción (no aplicada): aclarar en la intro que la ficha 3 (Palermo
  completo) es solo de referencia visual y no entra en el conteo de decisiones.

## 2. Checklist por macrozona (nombre / estado / problema / decisión / casillas)

Confirmado contra las 14 fichas: **todas tienen los 5 elementos pedidos**, con dos
excepciones parciales:

| # | Macrozona | Nombre claro | Estado revisión | Problema principal | Decisión sugerida | Casillas |
|---|---|---|---|---|---|---|
| 1 | Palermo Soho | ✓ | ✓ (implícito: alta confianza) | Ninguno | Implícita: aprobable | ✓ |
| 2 | Palermo Hollywood | ✓ | ✓ | Ninguno | Implícita: aprobable | ✓ |
| 3 | Palermo (contexto) | ✓ | ⚠️ no aplica estado (es contextual) | Subzonas faltantes (Cañitas, Chico, Nuevo) | No explícita | ✓ (pero decidir qué significa "aprobar" algo contextual) |
| 4 | Av. Corrientes | ✓ | ✓ | Ninguno tras corrección | Implícita: aprobable | ✓ |
| 5 | Microcentro y Centro | ✓ | ✓ | Pendiente Retiro (no bloqueante) | No explícita para el pendiente de Retiro | ✓ |
| 6 | Belgrano | ✓ | ✓ | **53 locales huérfanos** | Explícita: revisar antes de aprobar | ✓ |
| 7 | Costanera Norte | ✓ | ✓ | Evidencia mínima (5 locales) | Explícita: modificar/pendiente | ✓ |
| 8 | Chacarita | ✓ | ✓ | Ninguno nuevo | Implícita: aprobable | ✓ |
| 9 | San Telmo | ✓ | ✓ | Posible sobre-inclusión (Constitución/Barracas) | No explícita (queda "para próxima revisión") | ✓ |
| 10 | Villa Crespo | ✓ | ✓ | Ninguno | Implícita: aprobable | ✓ |
| 11 | Puerto Madero | ✓ | ✓ | Área grande / pocos locales | No explícita (queda "a futuro") | ✓ |
| 12 | Recoleta | ✓ | ✓ | Ninguno | Implícita: aprobable | ✓ |
| 13 | Caballito | ✓ | ✓ | Ninguno | Implícita: aprobable | ✓ |
| 14 | Av. Caseros/Barracas | ✓ | ✓ | Evidencia escasa (18 locales, semilla con ruido) | Explícita: modificar/pendiente | ✓ |

**Lectura:** las 3 fichas con problema real y grave (Belgrano, Costanera Norte,
Caseros/Barracas) sí tienen decisión sugerida explícita y coinciden con la tabla-resumen
del final del documento. Las fichas "sin cambios en esta ronda" (San Telmo, Puerto
Madero) mencionan un pendiente pero no sugieren explícitamente qué casilla marcar —
razonable, porque el propio documento las clasifica aparte como "sin problemas
detectados en esta ronda", pero no está de más que quien revise sepa que ahí la omisión
de "decisión sugerida" es intencional, no un olvido.

## 3. Revisión especial de las 5 zonas pedidas

### Belgrano
El documento es transparente sobre el trade-off: gana 84 locales, pierde 53 que quedan
sin ninguna macrozona. La ficha técnica (`FICHAS_TECNICAS...md`) agrega un dato que el
documento de revisión **no** traslada explícitamente: las 3 identidades internas
(Barrio Chino, Bajo Belgrano, Belgrano R) siguen mezcladas en una sola zona, con calles
de referencia ya identificadas (Juramento/Arribeños, Libertador, Cabildo) pero **no
usadas todavía** para separarlas — es la misma lógica que ya se aplicó a Palermo
Soho/Hollywood. Vale que DGDGAS sepa que existe ese camino de subdivisión antes de
aprobar Belgrano como zona única.
**Lectura:** correctamente marcada como "revisar con atención". No aprobar sin que
alguien mire los 53 locales huérfanos.

### Costanera Norte
Coherente entre ficha, QA y resumen: 5 locales en toda la zona, corredor ya recortado al
tramo real. El documento sugiere explícitamente "modificar" o dejar pendiente, y explica
por qué (no es un problema del dibujo, es falta de oferta registrada). Es la ficha más
honesta de las 14 — no infla la lectura.
**Lectura:** lista para revisión, con una recomendación clara ya incluida. No debería
aprobarse como zona consolidada.

### Caseros/Barracas
Aparece en la tabla-resumen del documento de revisión bajo "revisar con atención", que
es coherente con la ficha técnica (semilla mayormente ruido, 3 de 5 puntos duplicados o
mal asignados). Ojo con un matiz: en el cuerpo del documento (ficha 14) dice "sin
cambios en esta ronda" y recomienda el mismo criterio que Costanera Norte, pero la
zona **no pasó por el mismo proceso de corrección** que Belgrano/Corrientes/Microcentro/
Chacarita — es la más chica de las 14 (18 locales, 55,9 ha) y quedó fuera de los 4
bloqueantes "según lo pedido explícitamente", no por estar en mejor estado.
**Lectura:** correctamente señalada como no lista para aprobar. Vale aclarar en el
documento que "sin cambios en esta ronda" acá no significa "sin problemas", sino "no
llegó a ser prioridad".

### Chacarita
El documento de revisión dice "los mismos 116 locales de antes" y no cambia el número,
lo cual puede leerse como "no pasó nada". La ficha técnica aclara que sí hubo una
corrección real: se descartó una lista de referencia con direcciones mal cargadas y se
recortó el polígono a partir de la concentración real de las 116 entidades — el ajuste
de superficie fue "modesto" no porque no se haya trabajado, sino porque los locales
están repartidos por casi toda el área. Es un matiz que el documento de revisión resume
bien ("recortado alrededor de los locales que realmente existen"), aunque no queda
explícito que Chacarita fue uno de los 4 bloqueantes resueltos en esta tanda — un lector
que solo mire este documento podría pensar que fue una zona "tranquila" al mismo nivel
que Villa Crespo o Recoleta.
**Lectura:** técnicamente lista para revisión (bloqueante ya resuelto), pero el
documento la ubica en el grupo "sin cambios, sin problemas" junto con zonas que nunca se
tocaron. Es una imprecisión de categorización, no de contenido.

### Corrientes / Microcentro
La pareja más sólida de las 5 revisadas. El documento explica con claridad el
solapamiento anterior (406 locales duplicados) y que quedó resuelto a 0. El QA de
correcciones confirma que no introdujo solapamientos nuevos de magnitud comparable (el
único nuevo, Palermo × Costanera Norte al 75%, es de bajo impacto porque Palermo
contextual no es contenedor de clustering). El único pendiente que el documento de
revisión menciona y que no debería perderse es si Retiro entra o no en "Microcentro y
Centro" — es una decisión de alcance, no técnica.
**Lectura:** la pareja más lista para aprobar de las 5, con una sola pregunta abierta
(Retiro) que no bloquea la aprobación del resto.

## 4. Síntesis: listas / requieren ajuste / no aprobar todavía

**Listas para revisión y probablemente aprobables tal cual:**
Palermo Soho, Palermo Hollywood, Avenida Corrientes, Microcentro y Centro, Chacarita
(bloqueante ya resuelto, aunque el documento no lo destaca como tal), Villa Crespo,
Recoleta, Caballito.

**Requieren ajuste antes de aprobar (sí o sí):**
- **Belgrano** — resolver los 53 locales huérfanos antes de aprobar el corredor de 3
  avenidas. Sugerencia técnica ya identificada (ensanchar semiancho o método híbrido),
  pendiente de decisión de Diego/DGDGAS.
- **San Telmo** — no es bloqueante, pero el propio documento admite un posible
  sobre-alcance hacia Constitución/Barracas sin verificar todavía.
- **Puerto Madero** — no es un error, pero el área (503 ha) es desproporcionada respecto
  de los 85 locales; candidato a acotar a la franja este en una próxima ronda.

**No deberían aprobarse todavía como zonas consolidadas:**
- **Costanera Norte** — 5 locales en total, corredor igual duplica la distancia real con
  evidencia.
- **Avenida Caseros/Barracas** — 18 locales, semilla con ruido confirmado, no pasó por
  el mismo proceso de corrección que las otras 4 zonas revisadas esta ronda.

**Caso aparte — Palermo (ficha 3, contextual):**
No es una macrozona operativa (`es_contenedor_clustering=false`), así que "aprobar/
modificar/rehacer" no tiene el mismo significado que en las demás 13. Antes de que
alguien marque una casilla ahí, valdría aclarar qué significa aprobarla: ¿el barrio
completo como fondo visual está bien, o hace falta esperar a que existan las 3 subzonas
pendientes (Cañitas, Palermo Chico, Nuevo/Botánico)?

## 5. Dudas que DGDGAS debería resolver (no técnicas, editoriales)

1. **Belgrano:** ¿los 53 locales huérfanos son en su mayoría de Barrio Chino, Bajo
   Belgrano o Belgrano R? Sin ese dato, no se puede decidir entre ensanchar el semiancho
   de las 3 avenidas o volver a un método híbrido (corredor + buffer de respaldo sobre
   las elipses viejas).
2. **Microcentro y Centro:** ¿Retiro debería considerarse parte del "centro" a efectos
   editoriales, o queda deliberadamente afuera?
3. **Belgrano (alcance a futuro):** ¿tiene sentido, para una próxima ronda, separar
   Barrio Chino / Bajo Belgrano / Belgrano R en subzonas propias — mismo criterio que ya
   se aplicó a Palermo Soho/Hollywood? No es necesario resolverlo ahora, pero condiciona
   si vale la pena "arreglar" el semiancho actual o esperar a la subdivisión.
4. **Costanera Norte y Caseros/Barracas:** ¿se dejan directamente "pendiente" (sin
   marcar △ ni ✗, simplemente fuera de esta ronda de aprobación) hasta que haya más
   oferta registrada, o se fuerza una decisión ahora aunque la evidencia sea escasa?
5. **Palermo contextual:** ¿qué significa aprobar la ficha 3 si no es una unidad
   operativa? Ver punto 4 de la síntesis arriba.
6. **Cobertura total de CABA:** el QA de correcciones señala que la superficie cubierta
   por macrozonas bajó de ~19,7% a ~12,2% (contenedores de clustering) como consecuencia
   de priorizar precisión sobre cobertura. Esto no está mencionado en el documento de
   revisión dirigido a DGDGAS — vale que alguien decida si ese dato debe agregarse ahí o
   si es información de nivel técnico que no necesita bajar a ese documento.

---

**No se tocaron scripts, geometrías ni se generaron outputs nuevos.** Este documento es
puramente de lectura editorial sobre lo ya existente en
`docs/polos_gastro/experimentos/infraestructura_cartografica_v1/`.
