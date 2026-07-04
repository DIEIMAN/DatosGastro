# Plan de proximos pasos - PolosGastro y Design System DGDGAS

Fecha: 2026-07-01. Documento interno de planificacion. Ordena el camino recomendado despues de la
revision final del Borrador 3 y de la preview visual minima. Ninguna etapa se ejecuta sin decision
humana previa; ninguna toca datos fuente, pipeline F01-F05 ni proyectos ajenos (Cafecito,
MercadosGastro, CasasDePastas, DataGastro V2).

Referencias: `REVISION_FINAL_BORRADOR_3_POLOS_GASTRO_2026_07_01.md`,
`docs/datagastro_design_system/previews/EVALUACION_PREVIEW_POLOS_BORRADOR3.md`,
`docs/datagastro_design_system/PLAN_ACTUALIZACION_DESIGN_SYSTEM_POST_MAPEO.md`.

---

## Etapa A - Cerrar Borrador 3 metodologico

**Objetivo.** Dejar el Borrador 3 con todas las decisiones humanas resueltas, listo para servir de
base a una version presentable.

**Archivos involucrados.**
- `docs/polos_gastro/fase9_borrador_3/` (los 6 documentos).
- `outputs/polos_gastro/fase9_borrador_3/tablas/tabla_polos_para_informe_borrador_3.csv`.
- `docs/revisiones/REVISION_FINAL_BORRADOR_3_POLOS_GASTRO_2026_07_01.md` como checklist.

**Que hacer.**
- Revision humana de las decisiones de `NOTAS_REVISION_HUMANA_BORRADOR_3.md`: Paternal, Bajo
  Belgrano, Corrientes/Abasto, recortes de Caseros y DoHo, Costanera Norte.
- Resolver el caso Paternal en la tabla (tipo corredor vs senal barrial) y documentar la opcion.
- Completar o degradar las fuentes pendientes (Clarin de Parque Saavedra, Federico Lacroze).
- Decidir tratamiento editorial de las referencias del documento semilla.

**Que no hacer.**
- No aplicar cambios de clasificacion sin decision humana registrada.
- No modificar Borrador 2, Fase 7 ni Fase 8.
- No agregar fuentes nuevas ni busquedas web sin autorizacion.

**Riesgo.** Aplicar recomendaciones "no aplicar ahora" por inercia, o endurecer casos con fuentes
sin verificar.

**Output esperado.** Acta breve de decisiones (que se aprueba, que se rechaza, que se posterga) y,
si corresponde, un Borrador 3.1 o directamente insumos para Borrador 4.

---

## Etapa B - Validar preview visual

**Objetivo.** Que Diego (y jefatura si corresponde) revise la preview HTML y decida si la direccion
visual es correcta.

**Archivos involucrados.**
- `outputs/datagastro_design_system/previews/polos_borrador3_preview_minima/` (HTML + CSS).
- `docs/datagastro_design_system/previews/README_PREVIEW_POLOS_BORRADOR3.md` y
  `EVALUACION_PREVIEW_POLOS_BORRADOR3.md`.

**Que hacer.**
- Abrir la preview en navegador, revisar las 3 paginas contra la evaluacion.
- Decidir sobre los 8 ajustes listados en la evaluacion (estados faltantes, tabla larga,
  tipografia, contraste, cinta de estado, footer, invariante de orden).
- Registrar observaciones visuales propias (que convence, que no).

**Que no hacer.**
- No convertir la preview en entregable ni circularla como informe.
- No generar PDF de la preview.
- No retocar tokens canonicos a partir de impresiones sueltas; primero cerrar la lista de ajustes.

**Riesgo.** Que la preview se tome como diseno aprobado y se saltee la etapa de ajuste de tokens.

**Output esperado.** Lista corta de ajustes aprobados/rechazados sobre la evaluacion.

---

## Etapa C - Ajustar tokens y componentes (solo si B funciona)

**Objetivo.** Incorporar los ajustes aprobados al mapeo experimental y, recien con eso validado,
decidir la actualizacion canonica.

**Archivos involucrados.**
- `docs/datagastro_design_system/tokens/design_tokens_dgdgas_claude_design_mapped_v1.json`
  (o una v2 experimental).
- `docs/datagastro_design_system/tokens/MAPEO_TOKENS_CLAUDE_DESIGN_A_BASE_LOCAL.md`.
- `docs/datagastro_design_system/COMPONENTES_PROPUESTA_AMPLIACION_CLAUDE_DESIGN_V1.md`.
- Solo con aprobacion explicita: `design_tokens_dgdgas.json` / `.yaml` (canonicos).

**Que hacer.**
- Completar `state_details` para los estados faltantes (contexto, no_delimita, validacion,
  interno, alerta, anexo).
- Tokenizar la cinta de estado del documento y el patron de footer.
- Cerrar decision tipografica (fallback definitivo o instalacion autorizada de fuentes).
- Actualizar la preview con los tokens ajustados y re-validar (iteracion corta B-C).
- Recien despues, con aprobacion de Diego: versionar tokens canonicos (etapa 2 del plan post-mapeo).

**Que no hacer.**
- No tocar `style_tokens_dgdgas.py` ni `scripts/shared/` en esta etapa.
- No actualizar canonicos sin aprobacion explicita.
- No agregar halos de mapa ni chips complejos sin backend probado.

**Riesgo.** Romper compatibilidad de scripts si se canoniza una estructura que
`style_tokens_dgdgas.py` no interpreta; mantener la forma local del JSON.

**Output esperado.** Mapeo v2 (o canonicos versionados, si se aprueba) + preview actualizada.

---

## Etapa D - Preparar Borrador 4 / version presentable

**Objetivo.** Redactar la version presentable del informe de polos incorporando las decisiones de
la Etapa A, todavia sin diseno aplicado.

**Archivos involucrados.**
- Nueva carpeta `docs/polos_gastro/fase10_borrador_4/` (o el nombre de fase que se decida).
- Base: Borrador 3 + acta de decisiones de Etapa A.

**Que hacer.**
- Aplicar los cambios de clasificacion aprobados (y solo esos), con trazabilidad de la decision.
- Ajustar redaccion segun la revision final (por ejemplo "validan" -> "respaldan").
- Mantener estructura: resumen ejecutivo, hallazgos, limites, proximos pasos, anexos.
- Definir que tablas de capa objetiva entran al anexo y con que advertencias.
- QA de lenguaje: sin "locales activos", sin ranking, sin descarte, marca DGDGAS publica.

**Que no hacer.**
- No modificar los archivos del Borrador 3 (se copia, no se edita en el lugar).
- No sumar la senal objetiva al cuerpo como dato duro.
- No generar todavia PDF/DOCX ni mapas.

**Riesgo.** Perder advertencias al condensar; el checklist de la revision final funciona como
control.

**Output esperado.** Borrador 4 en Markdown, cerrado metodologicamente y listo para diseno.

---

## Etapa E - Aplicar diseno solo sobre copia controlada

**Objetivo.** Producir la primera version disenada del informe sobre una copia del Borrador 4,
nunca sobre los originales.

**Archivos involucrados.**
- Copia controlada en una carpeta de trabajo dedicada (por ejemplo
  `outputs/polos_gastro/version_presentable_wip/`, fuera de `docs/polos_gastro/fase*`).
- Tokens ajustados de Etapa C; catalogo de componentes; checklist
  `QA_VISUAL_INFORMES_DGDGAS.md`.

**Que hacer.**
- Aplicar template y componentes (TablaPolos, EstadoChip, AlcanceAdvertencia, cajas) a la copia.
- Probar tabla completa de 32 filas con cortes de pagina.
- QA visual + QA de privacidad (sin rutas internas, sin fuentes no publicables, sin DataGastro
  como marca).
- Revision humana de la pieza disenada completa.

**Que no hacer.**
- No editar los Markdown originales de Borrador 3/4.
- No publicar ni circular la copia en trabajo.
- No incluir mapas todavia, salvo placeholder con disclaimer.

**Riesgo.** Que la version disenada se perciba como final antes del QA; la cinta de estado del
documento (Etapa C) es la mitigacion.

**Output esperado.** Version disenada en HTML (u otro formato intermedio aprobado) con QA visual
cerrado.

---

## Etapa F - Recien despues, evaluar PDF/DOCX

**Objetivo.** Decidir formato de salida final y produccion, con autorizacion explicita.

**Archivos involucrados.**
- La version disenada validada de Etapa E.
- Si se aprueba tocar scripts: `scripts/shared/reporting_dgdgas/` (etapa 3 del plan post-mapeo),
  con permiso previo por tratarse de scripts productivos.

**Que hacer.**
- Definir con jefatura el formato (PDF, DOCX, ambos) y el circuito de firma/aprobacion.
- Verificar paginado real, tipografias embebidas y fidelidad de tokens en el formato elegido.
- QA final de privacidad y marca sobre el archivo de salida.
- Decidir si se autoriza la fase de mapas de contexto (separada, con sus propias reglas).

**Que no hacer.**
- No generar PDF/DOCX antes de este punto.
- No modificar scripts productivos sin permiso explicito de Diego.
- No usar Google Places ni fuentes privadas para ninguna pieza cartografica.

**Riesgo.** Divergencia entre la preview HTML y el render PDF/DOCX real; presupuestar una
iteracion de ajuste.

**Output esperado.** Informe final de polos en formato aprobado, con trazabilidad de decisiones
desde el Borrador 3.

---

## Resumen del camino

A (decisiones humanas) y B (validar preview) pueden avanzar en paralelo; C depende de B; D depende
de A; E depende de C y D; F depende de E. El unico punto que requiere permiso adicional sobre
scripts productivos es F (y la parte canonica de C).
