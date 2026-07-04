# Diagnóstico comparado — Claude Design vs. mapas V4/V17

**DGDGAS — Dirección General de Desarrollo Gastronómico**
Fase 18 — Interpretación de diseño de mapas. Documento de análisis, no de ejecución.
No ejecuta API, no genera PDF, no genera mapas, no toca datos fuente. No commit / no push / no staging.

Referencia analizada:
`docs/polos_gastro/fase18_claude_design_mapas/inputs/DGDGAS_mapas_detalle_claude_design_v1.html`
(propuesta visual standalone generada en Claude Design; se lee como **referencia visual**, no como pieza a publicar).

---

## 1. Qué se comparó

| Insumo | Qué es | Rol en este diagnóstico |
|---|---|---|
| Mapas V3 (fase 15) | Mapas de detalle con callejero GCBA suavizado; puntos como apoyo. | Base callejera que funciona. |
| Mapas V4 (fase 16) | Subzonas coloreadas + etiquetas grandes sobre el callejero V3; puntos ya no protagonizan. | Punto de partida real a mejorar. |
| V17 (geometrías más editoriales) | Iteración con geometrías más trabajadas. | Antecedente de la misma búsqueda editorial. |
| Claude Design v1 (HTML) | Propuesta visual standalone: sistema de color, mockups de los cinco mapas, reglas de implementación. | Referencia visual y fuente de la especificación. |
| Necesidad de Diego | Que los mapas dejen de parecer generados por script. | Criterio de aceptación. |
| Necesidad de reunión con Ale | Versión **mostrable**, no perfecta. | Criterio de urgencia. |

El problema que ya estaba diagnosticado (fase 14–16): el callejero mejoró la lectura urbana, pero las
subzonas todavía se leen como elipses/manchas, algunas etiquetas no jerarquizan y la pieza no termina de
verse mostrable para conducción. Claude Design ataca exactamente ese punto.

---

## 2. Qué del diseño de Claude Design sirve (y hay que adoptar)

1. **Sistema visual único para los cinco mapas.** Una sola gramática: fondo `#FAFBFC`, grilla de calles
   tenue rotada al ángulo del barrio, agua/avenidas como soporte, subzonas coloreadas como protagonistas,
   estado indicado por el borde, menciones fuera del mapa. Esto es lo que hoy falta: coherencia entre las
   cinco páginas.

2. **Estado codificado por el borde, no por el texto.**
   - Borde **sólido** → subzona consolidada.
   - Borde **discontinuo** (dash) → a reforzar / a validar.
   - **Punteado tenue** sin relleno → contexto (no protagonista).
   Resuelve de un modo limpio la exigencia de mostrar "Belgrano R a reforzar", "Abasto a reforzar",
   "sedes a validar" sin llenar el mapa de aclaraciones.

3. **Polígonos angulares que siguen avenidas, en lugar de elipses.** La propuesta reemplaza la elipse
   genérica por áreas angulares apoyadas en ejes viales reales. Es la corrección central del "parece
   script".

4. **Bandas longitudinales para fenómenos lineales.** Corrientes como eje lineal y Puerto Madero como
   banda costera de diques se dibujan como bandas, no como manchas redondas. Coincide con la regla
   editorial ya acordada (Corrientes eje 9 de Julio–Callao; Puerto Madero longitudinal).

5. **Etiqueta grande dentro del área + tag "aproximada" en mono chico.** Jerarquía tipográfica clara:
   nombre de subzona grande, y una etiqueta chica "subzona/área/eje aproximado" que mantiene la cautela
   visible sin romper la estética.

6. **Menciones siempre en caja lateral, nunca puntos de locales sobre el mapa.** Sólo hitos urbanos
   (mercado, arco del Barrio Chino, Obelisco, Faena) como rombo. Esto ya era criterio del proyecto y la
   propuesta lo formaliza bien: sub-bloque separado "a validar" con nota de confirmación.

7. **Paleta institucional sobria y coherente con DGDGAS.** Navy `#1F3B57` como color de marca, verde
   `#2F6E5B`, azul `#2C7FB8`, cobre `#C0762B` para ejes, slate para "a reforzar". Rellenos a baja opacidad
   (15–20% consolidada, 8–10% a reforzar). Se ve institucional, no técnico.

8. **Reglas de implementación numéricas.** Trae valores concretos (tamaños de etiqueta, opacidades,
   grosores de borde, separación mínima entre etiquetas, criterio de línea guía) sobre un lienzo de
   referencia 720×560. Convierte "que se vea mejor" en parámetros reproducibles — clave para pasárselo a
   Codex.

---

## 3. Qué NO sirve o no es implementable tal cual

1. **El HTML no es la pieza; es una maqueta.** Está armado con SVG/HTML dibujados a mano sobre un lienzo
   de referencia. Las geometrías son **esquemáticas**, no georreferenciadas: no salen del callejero GCBA
   ni de coordenadas reales. No se puede "exportar el HTML a PDF" y darlo por hecho.

2. **Fuentes Google (Libre Franklin, Source Sans, IBM Plex Mono) vía `fonts.googleapis.com`.** La maqueta
   las llama por red. En la pieza real hay que usar fuentes locales o los fallbacks ya validados
   (Arial/Calibri), como en el resto de DGDGAS. No depender de fuentes no instaladas.

3. **Encabezados de proceso visibles.** La maqueta muestra chips como "Borrador de diseño", "REGLAS PARA
   CODEX", "DIAGNÓSTICO", "SISTEMA VISUAL", "Fecha de corte". **Nada de eso puede viajar al PDF público.**
   Son andamiaje de la referencia, no contenido institucional.

4. **Geometría "linda" ≠ geometría correcta.** Los polígonos del mockup están dibujados para verse bien,
   no para respetar las delimitaciones de trabajo acordadas. Al implementar hay que anclar las formas a
   las avenidas reales (ver especificación), no copiar el trazo del mockup.

5. **Riesgo de sobre-precisión.** Áreas angulares y prolijas pueden leerse como "límite oficial". Hay que
   sostener explícitamente el lenguaje "subzona aproximada / área de lectura / eje aproximado" y la nota
   "no delimita oficialmente polos" en cada mapa, que la propia maqueta ya incluye.

6. **Detalle de contexto que puede ensuciar.** Palermo Chico / Botánico y similares aparecen como
   contexto tenue; bien usados suman, mal usados recargan. Deben ir sólo como contorno punteado tenue sin
   relleno, o directamente omitirse si compiten con las tres subzonas principales.

---

## 4. Qué se conserva de V4 (no rehacer)

- **El mapa global de los 22 polos/ejes** (página 5). Es la lectura principal del universo y está
  correcto. No se rediseña; a lo sumo ajustes menores.
- **La estructura de 18 páginas** y el tono institucional sobrio.
- **Las cajas laterales de menciones destacadas** por polo/subzona. Ya funcionan y la propuesta de Claude
  Design las confirma como el lugar correcto para los nombres.
- **La base callejera GCBA (CC-BY-2.5-AR)** incorporada en V3/V4. Es la base urbana correcta y de origen
  institucional; se conserva como soporte tenue.
- **El pie institucional** "DGDGAS — Dirección General de Desarrollo Gastronómico" y el barrido de campos sensibles ya
  pasado en V3/V4 (0 `place_id`, rating, API key, rutas, etc.).
- **Los criterios de inclusión** (cerrados/dudosos fuera del mapa público; duplicados una sola sede;
  Corrientes y Abasto vinculados pero no fusionados).

---

## 5. Qué se reemplaza (de V4 a la versión mostrable)

| Elemento V4 | Reemplazo según Claude Design |
|---|---|
| Subzonas como elipses/manchas | Polígonos angulares apoyados en avenidas; bandas longitudinales para Corrientes y Puerto Madero. |
| Estado indicado con texto o color plano | Estado codificado por el borde (sólido / dash / punteado). |
| Rellenos opacos que "pintan el barrio" | Rellenos a baja opacidad (15–20% / 8–10%) sobre fondo claro. |
| Etiquetas en cajitas flotantes que se pisan | Etiqueta grande dentro del área + tag "aproximada" mono chica; separación mínima y línea guía si no cabe. |
| Contexto (Palermo Chico, etc.) compitiendo | Contexto sólo como contorno punteado tenue, sin relleno, o se omite. |
| Grilla de calles pareja | Grilla tenue **rotada al ángulo del barrio**, que da sensación de trama real. |

---

## 6. Qué se puede hacer rápido para una versión mostrable

Prioridad para tener algo presentable a Ale sin rehacer todo:

1. **Aplicar el sistema visual único** (fondo, grilla rotada, paleta, borde por estado) a los cinco mapas
   de detalle existentes. Es un cambio de estilo de render, no de datos.
2. **Convertir las elipses en polígonos angulares / bandas** anclados a las avenidas ya definidas en la
   especificación. Reutiliza el callejero GCBA que ya está descargado.
3. **Rehacer la tipografía de etiquetas** (grande dentro del área + tag aproximada) con fuentes locales.
4. **Mantener las cajas laterales tal como están** (sólo revisar que el sub-bloque "a validar" quede
   separado con su nota).
5. **Conservar mapa global y estructura de 18 páginas.**

Esto produce un **PDF V5 mostrable** que se ve institucional y editorial, sin tocar el universo semilla ni
generar datos nuevos.

---

## 7. Qué queda para después de hablar con Ale (no forzar ahora)

- **Recorte exacto de Abasto** (radio ~5 cuadras del shopping) y de Corrientes (9 de Julio–Callao): la
  forma se dibuja aproximada; el recorte fino lo valida Ale.
- **Destino de Belgrano R y Bajo Belgrano**: quedan visibles con borde discontinuo ("a reforzar / a
  revisar"); Ale decide si permanecen en la pieza final o pasan a nota.
- **Si Abasto merece página propia** o sigue como área vinculada en la página de Corrientes.
- **Cuántas subzonas de contexto** conservar en Palermo (¿sólo las tres principales?).
- **Nivel final de color y densidad de etiquetas** según el destino de circulación (interno vs.
  Vicejefatura).
- **Decisión tipográfica final** (Libre Franklin / Source Sans si se instalan; hasta entonces, fallback).

---

## 8. Conclusión del diagnóstico

Claude Design **no reemplaza** el trabajo de V4: lo **corrige en lo visual**. La base territorial
(callejero GCBA, subzonas de trabajo, cajas laterales, criterios de cautela) sigue siendo la de V4. Lo que
aporta la referencia es un **sistema visual coherente y parametrizado** que resuelve el "parece generado
por script": bordes que comunican estado, polígonos angulares en vez de elipses, bandas para lo lineal, y
tipografía jerárquica.

La ruta mostrable es clara: **aplicar el sistema visual de Claude Design sobre las geometrías y datos de
V4**, sin inventar nada nuevo y sin cerrar todavía las decisiones que corresponden a Ale.
