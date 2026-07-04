# QA — Fase 18 Interpretación de diseño de mapas (Claude Design)

**DGDGAS — Dirección General de Desarrollo Gastronómico**
Fecha de control: 3 de julio de 2026.
Fase de interpretación de diseño. Solo documentos: no se ejecutó código, API, PDF ni mapas.

## Entregables creados

- [x] `DIAGNOSTICO_CLAUDE_DESIGN_VS_V4.md` — diagnóstico comparado.
- [x] `ESPECIFICACION_VISUAL_MAPAS_MOSTRABLE_ALE.md` — especificación visual final.
- [x] `ESTRATEGIA_VERSION_MOSTRABLE_ALE.md` — estrategia para la reunión con Ale.
- [x] `PROMPT_CODEX_IMPLEMENTAR_MAPAS_MOSTRABLE_ALE.md` — prompt listo para Codex.
- [x] `QA_FASE18_CLAUDE_DESIGN_MAPAS.md` — este control.
- [x] Carpeta `docs/polos_gastro/fase18_claude_design_mapas/` creada (con subcarpeta `inputs/`).

## Contenido verificado

- [x] Diagnóstico responde: qué sirve de Claude Design, qué no es implementable, qué se conserva de V4, qué
      se reemplaza, qué es rápido para versión mostrable y qué queda para después de Ale.
- [x] Especificación cubre: sistema visual común, mapa global (conservar), criterio de mapas de detalle,
      Palermo/Las Cañitas con delimitaciones aproximadas, Puerto Madero longitudinal, San Telmo,
      Corrientes/Abasto diferenciados, Belgrano con jerarquía por borde, cautelas visibles.
- [x] Estrategia responde: si conviene V5 antes de Ale, qué páginas mejorar sí o sí, qué mostrar aunque no
      esté final, advertencias, decisiones a pedir, qué no seguir tocando.
- [x] Prompt Codex pide: generar mapas V5, PDF V5 mostrable, rasterizar y QA, guardar en
      `fase19_pdf_mostrable_ale`, responder con problemas visuales y pendientes.

## Alcance de ejecución (confirmaciones)

- [x] No se ejecutó API.
- [x] No se hicieron llamadas Google Places.
- [x] No se generó PDF.
- [x] No se generaron mapas.
- [x] No se tocaron datos fuente ni `data/`.
- [x] No se tocó el pipeline F01–F05.
- [x] No se tocó Cafecito.
- [x] No se tocó Mercados.
- [x] No se tocó Casas de Pastas.
- [x] No se tocó Design System (tokens canónicos).
- [x] No se tocó Borrador 2 ni Borrador 3.
- [x] No se borró nada.
- [x] No commit / no push / no staging / no `git add`.

## Privacidad y marca (documentos de esta fase)

- [x] Marca visible usada: **DGDGAS — Dirección General de Desarrollo Gastronómico**.
- [x] Sin uso de "DataGastro" como marca pública en el contenido de los entregables.
- [x] Sin campos sensibles ni técnicos en los documentos: sin `place_id`, `rating`,
      `user_ratings_total`, API key, raw JSON, CUIT, DNI, emails, teléfonos.
- [x] Nombres de locales usados solo como menciones del universo semilla ya presentes en la base V4; no se
      agregaron datos nuevos.
- [x] Nota: los documentos de esta fase son **internos** (contienen referencias a fases, nombres de
      archivos y criterios de proceso). El barrido estricto de campos sensibles aplica a la **pieza pública
      V5**, que deberá pasar su propio QA en la fase 19. Estos criterios ya están incorporados al prompt de
      Codex.

## Observaciones

- La referencia de Claude Design (`inputs/DGDGAS_mapas_detalle_claude_design_v1.html`) se analizó como
  maqueta: su contenido visible está en un bundle JS y sus geometrías son esquemáticas, no
  georreferenciadas. Se extrajo el sistema visual, la paleta, las etiquetas y las reglas de
  implementación; no se ejecutó ni se exportó.
- La versión V5 mostrable queda **pendiente de ejecución por Codex** con el prompt provisto. Su QA técnico
  y de privacidad corresponde a la fase 19.
