# Propuesta de ampliacion de componentes - Claude Design v1

Fecha de revision: 2026-07-01.

Alcance: propuesta documental para ampliar el catalogo local de componentes
DGDGAS Informes. No modifica `COMPONENTES_INFORMES_DGDGAS.md`, no modifica
scripts y no aplica el sistema visual a informes.

Reglas transversales:

- DGDGAS es marca publica.
- DataGastro es nombre interno del sistema/metodologia.
- No inventar datos, fuentes, rankings ni conclusiones.
- Los mapas son referencia territorial; no delimitan oficialmente.
- No usar Google Places como base publica.
- En recomendaciones publicas, usar `En espera de evidencia` para casos sin
  sustento suficiente.

## 1. QueHabilita

**Proposito.** Explicitar que decision, mejora operativa o proximo paso habilita
un relevamiento, y que no habilita.

**Campos esperados.**

- `titulo` opcional, por defecto `Que habilita`.
- `texto_habilita`.
- `texto_no_habilita`.
- `alcance`.
- `estado_doc` opcional.

**Tokens usados.**

- `surface.card` o `state.media.bg`.
- `border.subtle` o `state.media.border`.
- `status.medium` / `state.media.text`.
- `typography.scale.body` y `small`.

**Relacion local.** Se vincula con `lista_puntos()` y con las paginas de
sintesis/aspectos a considerar. No reemplaza conclusiones; agrega un bloque de
decision prudente.

**Recomendacion.** Adaptar en etapa 2 como componente documental y luego como
spec en `report_components_dgdgas.py`.

**Riesgos.**

- Convertir senales exploratorias en decisiones definitivas.
- Prometer padrones, rankings o representatividad no sostenida.
- Duplicar recomendaciones si no se coordina con la seccion de aspectos.

## 2. FuenteEvidencia

**Proposito.** Mostrar de forma breve las fuentes o insumos que sostienen un
bloque, sin exponer datos personales ni links privados.

**Campos esperados.**

- `fuentes[]`: nombre publico de fuente o insumo.
- `fecha_consulta` o `fecha_corte`, si corresponde.
- `tipo_fuente`: publica, interna agregada, externa cualitativa, documental.
- `nota_alcance` opcional.

**Tokens usados.**

- `brand.accent` para vinietas o borde discreto.
- `text.secondary` y `text.muted`.
- `typography.scale.caption` para fecha/fuente.

**Relacion local.** Complementa captions de graficos/tablas y anexo
metodologico. No reemplaza trazabilidad completa.

**Recomendacion.** Adoptar ahora en documentacion; adaptar a scripts despues de
validar formato de fuentes.

**Riesgos.**

- Publicar URLs privadas, IDs tecnicos o fuentes internas no publicables.
- Dar apariencia de fuente oficial a una senal cualitativa.
- Repetir fuente en exceso y ensuciar visualmente el informe.

## 3. AlcanceAdvertencia

**Proposito.** Presentar limites metodologicos o de lectura de forma neutral y
visible, sin usar lenguaje alarmista.

**Campos esperados.**

- `texto`.
- `tipo`: alcance, limitacion, privacidad, cartografia, advertencia_real.
- `severidad`: informativa, requiere_validacion, alerta_real.

**Tokens usados.**

- `surface.warm` para alcance metodologico.
- `surface.warn` y `status.validation` para validacion.
- `status.alert` solo para advertencias reales.
- `border.accent` como borde izquierdo.

**Relacion local.** Amplia `caja_advertencia()` y `caja_nota_metodologica()`.

**Recomendacion.** Adaptar. Primero documentar criterios de uso para evitar que
todo limite se vuelva alerta.

**Riesgos.**

- Usar rojo para evidencia debil.
- Ocultar limites en anexos cuando deben verse en cuerpo.
- Repetir advertencias y bajar legibilidad.

## 4. RequiereValidacion

**Proposito.** Marcar un dato o bloque que todavia requiere confirmacion antes
de presentarse como consolidado.

**Campos esperados.**

- `texto`.
- `que_falta_validar`.
- `responsable` opcional, solo si es institucional y publicable.
- `estado`: `validacion` o `pendiente`.

**Tokens usados.**

- `surface.warn`.
- `status.validation`.
- `border.strong`.
- `content_states.validacion` o `content_states.pendiente`.

**Relacion local.** Ya existe como `caja_validacion()` y `content_states.pendiente`.
Claude Design aporta una semantica mas precisa.

**Recomendacion.** Adoptar, pero conservar alias local `pendiente` hasta migrar
templates y scripts.

**Riesgos.**

- Presentar validacion pendiente como alarma.
- Mezclar `pendiente` con `requiere validacion`.
- Publicar campos internos de seguimiento.

## 5. EstadoDocumentacion / EstadoChip

**Proposito.** Calificar la madurez de evidencia de un dato, polo o bloque con
texto y apoyo visual.

**Campos esperados.**

- `estado`: fuerte, media, debil, pendiente, validacion, en_espera, contexto,
  no_delimita, anexo, interno, alerta.
- `label` visible.
- `nota` opcional.

**Tokens usados.**

- `content_states.*` para compatibilidad local.
- Extension futura `state_details.*` para `dot`, `text`, `bg`, `border`.
- `chip.shape` y `chip.dot` cuando exista soporte de render.

**Relacion local.** Amplia `estado_documentacion()`, que hoy devuelve label y
color simple.

**Recomendacion.** Adoptar por etapas. Primero agregar vocabulario y mapeo;
despues incorporar chip visual.

**Riesgos.**

- Que el color sea el unico significado. La etiqueta textual debe ser obligatoria.
- Cambiar estados en informes existentes sin revisar metodologia.
- Usar `alerta` para casos que solo son evidencia debil.

## 6. Chips de estado metodologico

**Proposito.** Dar una representacion compacta de estados en tablas, fichas y
mapas, siempre con texto visible.

**Campos esperados.**

- `estado`.
- `label`.
- `tamano`: normal o tabla.
- `nota_accesible` opcional.

**Tokens usados.**

- `chip.shape.radius`.
- `chip.dot.size`.
- `chip.dotSmall.size`.
- `state_details.<estado>.dot/text/bg/border`.

**Relacion local.** Nuevo patron visual. Se conecta con `TablaPolos`,
`FichaPolo` y `EstadoDocumentacion`.

**Recomendacion.** Dejar para despues hasta que exista backend real de render y
pruebas visuales.

**Riesgos.**

- Incompatibilidad con DOCX/Google Docs si se intenta reproducir chips complejos.
- Perdida de significado si se renderiza solo el punto de color.
- Saturacion visual en tablas largas.

## 7. MapaContexto

**Proposito.** Ubicar referencias territoriales sin sugerir limites oficiales de
polos o corredores.

**Campos esperados.**

- `barrios` o `comunas` como soporte tenue.
- `marcadores[]`: grupo, coordenada o referencia, tipo visual.
- `leyenda`.
- `disclaimer`.
- `fuente_cartografica`.
- `nota_alcance`.

**Tokens usados.**

- `map.land_fill`.
- `map.boundary_line`.
- `map.point_fill`.
- `map.disclaimer_text`.
- Extension futura de halos: `map_halos`.

**Relacion local.** Reemplaza conceptualmente a `mapa_territorial()` cuando el
informe es territorial. Mantiene la regla local de nota de alcance obligatoria.

**Recomendacion.** Adaptar en documentacion; dejar halos para despues.

**Riesgos.**

- Que halos o manchas parezcan delimitacion oficial.
- Usar geometria de fuentes privadas.
- Publicar mapa sin fuente cartografica ni disclaimer.

## 8. TablaPolos

**Proposito.** Presentar casos territoriales con estado de evidencia,
referencia territorial y recomendacion prudente.

**Campos esperados.**

- `polo`.
- `grupo`.
- `estado_doc`.
- `tipo_territorial`.
- `barrios_comunas`.
- `recomendacion_prudente`.
- `observaciones`.

**Tokens usados.**

- `table.*`.
- `content_states.*`.
- Futuro `chip.dotSmall`.

**Relacion local.** Ya existe como componente documentado y puede usar
`tabla()`. Claude Design mejora la semantica de estados.

**Recomendacion.** Adoptar parcialmente: vocabulario y columnas, sin cambiar
ordenamiento ni convertir en ranking.

**Riesgos.**

- Ordenar por puntaje o color y generar lectura de ranking.
- Usar lenguaje de descarte en vez de `En espera de evidencia`.
- Mezclar evidencia fuerte con senales pendientes.

## 9. FichaPolo

**Proposito.** Desarrollar un caso territorial con evidencia, limites y que falta
validar.

**Campos esperados.**

- `nombre`.
- `grupo`.
- `tipo_territorial`.
- `estado_doc`.
- `evidencia`.
- `referencias_preliminares`.
- `limites_metodologicos`.
- `que_falta_validar`.
- `recomendacion_prudente`.

**Tokens usados.**

- `surface.card` o `surface.page`.
- `brand.primary`.
- `brand.accent`.
- `content_states.*`.
- `box.method` / `AlcanceAdvertencia`.

**Relacion local.** Ya existe `ficha_polo()`, pero con campos mas simples. La
propuesta amplia el contrato sin tocar implementacion actual.

**Recomendacion.** Adaptar despues de validar `TablaPolos` y estados.

**Riesgos.**

- Hacer fichas demasiado extensas para informe ejecutivo.
- Presentar referencias preliminares como evidencia confirmada.
- Publicar fuentes internas no publicables.

## Orden recomendado de adopcion

1. `RequiereValidacion` y vocabulario de `EstadoDocumentacion`.
2. `FuenteEvidencia` y `AlcanceAdvertencia`.
3. `QueHabilita`.
4. `TablaPolos` con estados mapeados.
5. `FichaPolo`.
6. `MapaContexto` sin halos.
7. Chips visuales completos y halos, solo con backend probado.

## Componentes para dejar para despues

- Chips visuales complejos.
- Halos de mapas.
- Sombras de pantalla.
- Cualquier componente que requiera render PDF/DOCX real.

## Estado final de esta propuesta

La propuesta queda lista para revision metodologica y visual. No implica cambio
en scripts, templates productivos ni informes finales.
