# Plan de actualizacion post-mapeo - DGDGAS Informes Design System

Fecha de revision: 2026-07-01.

Objetivo: ordenar una posible adopcion de los tokens y componentes de Claude
Design sin romper la base local ni aplicar cambios a informes finales antes de
validar.

## Principios

- La base canonica sigue siendo local hasta aprobacion explicita.
- DGDGAS es la marca publica; DataGastro queda como nombre interno.
- No se aplican cambios a Cafecito, PolosGastro, MercadosGastro,
  CasasDePastas, DataGastro V2 ni informes finales en estas etapas.
- No se generan PDF/DOCX hasta que exista autorizacion especifica.
- No se usa Google Places como base publica.
- Los informes territoriales no se convierten en rankings.
- Mapas siempre como referencia territorial, no delimitacion oficial.

## Etapa 1 - Validar mapeo experimental

Alcance:

- Revisar `tokens/MAPEO_TOKENS_CLAUDE_DESIGN_A_BASE_LOCAL.md`.
- Revisar `tokens/design_tokens_dgdgas_claude_design_mapped_v1.json`.
- Revisar `tokens/preview_tokens_diff_claude_design_vs_local.csv`.
- Comparar contra `REVISION_EXPORT_CLAUDE_DESIGN_V1.md`.

No hacer:

- No tocar scripts.
- No tocar tokens canonicos.
- No tocar templates productivos.
- No generar informes.

Criterios de salida:

- Tabla de equivalencias aprobada o corregida.
- Estados metodologicos acordados.
- Decision sobre tipografias y fallbacks.
- Decision sobre mapas: disclaimer, fuente cartografica y halos.

## Etapa 2 - Actualizar documentacion y tokens canonicos si se aprueba

Alcance:

- Actualizar `design_tokens_dgdgas.yaml` y `design_tokens_dgdgas.json` solo si
  se aprueba el mapeo.
- Agregar componentes nuevos al catalogo local:
  `QueHabilita`, `FuenteEvidencia`, `AlcanceAdvertencia`, chips de estado y
  `MapaContexto`.
- Crear pruebas de render conceptual o previews estaticas, todavia sin informes
  finales.

No hacer:

- No aplicar a Cafecito ni PolosGastro.
- No modificar datos ni fuentes.
- No cambiar clasificaciones territoriales.

Criterios de salida:

- Tokens canonicos actualizados con version nueva.
- Catalogo de componentes actualizado.
- Checklist de QA ampliado con estados y mapas.
- Pruebas o previews revisadas visualmente.

## Etapa 3 - Adaptar scripts compartidos

Alcance:

- Adaptar `scripts/shared/reporting_dgdgas/` para leer nuevos tokens si fueron
  aprobados.
- Agregar soporte de estados enriquecidos sin romper `content_states` existente.
- Agregar specs para nuevos componentes.
- Probar con un documento minimo de laboratorio, no con informes finales.

No hacer:

- No aplicar a informes finales.
- No generar PDF/DOCX publicable.
- No instalar dependencias sin autorizacion.

Criterios de salida:

- `style_tokens_dgdgas.py` carga tokens nuevos y mantiene compatibilidad.
- `report_components_dgdgas.py` emite specs para nuevos componentes.
- Tests o smoke checks pasan.
- Documento minimo revisado sin datos reales sensibles.

## Etapa 4 - Aplicacion controlada

Alcance:

- Aplicar primero a un ejemplo controlado y no publicable.
- Revisar visualmente estructura, lectura, estados, tablas y mapas.
- Evaluar despues si corresponde probar con Cafecito o PolosGastro.

No hacer:

- No tocar Borrador 2 de PolosGastro sin pedido explicito.
- No reemplazar informes finales existentes.
- No publicar salidas sin QA.

Criterios de salida:

- Ejemplo controlado validado.
- QA publico sin datos personales, rutas, links privados ni claves.
- Decision humana sobre siguiente proyecto piloto.

## Decision actual

No estamos listos para actualizar tokens canonicos. Falta validar el mapeo,
resolver conflictos de tipografia/espaciado/estados y ver una preview
controlada antes de tocar scripts o informes.
