# Criterios de matching Google Places — Fase 11

Fecha de preparación: 2026-07-02.

Este documento define cómo aceptar o rechazar coincidencias de Google Places para los locales semilla de PolosGastro, sin ejecutar la API aún.

## 1. Aceptar un match

Un match se acepta con confidence alta cuando:
- el nombre devuelto coincide estrechamente con el nombre del local semilla.
- el barrio/zona inferida coincide con barrio_hint, subzona o polo.
- la dirección está dentro de la Ciudad Autónoma de Buenos Aires.
- el business_status no indica cierre permanente.
- la entidad no es un mercado/patio/hito colectivo tratado como local individual.

## 2. Rechazar un match

Un match se rechaza si:
- la categoría de Google no concuerda con el tipo gastronómico estimado.
- el punto está fuera de CABA.
- la coincidencia corresponde a una sucursal equivocada.
- el local está cerrado permanentemente y no hay evidencia de reapertura.
- la respuesta es un edificio, hotel o espacio no gastronómico.

## 3. Tratar sucursales

- Para cadenas o nombres repetidos, usar siempre el polo y el barrio como contexto.
- Si hay varias sedes, asociar al polo indicado en la semilla.
- No usar el primer resultado sin verificar que pertenece al polo correcto.
- Si no se puede distinguir, marcar requiere_revision_manual = si.

## 4. Tratar cadenas

- Para nombres de cadena, usar query principal con nombre + polo + Buenos Aires.
- Si la cadena aparece en varias zonas, no asumir que todos los matches son equivalentes.
- Documentar en nota_interna cuando el nombre es genérico o de múltiples sedes.

## 5. Tratar mercados, patios y hitos colectivos

- Los resultados para Mercado de San Telmo, Patio de los Lecheros, El Mercado / Faena y similares deben tratarse como hito_colectivo.
- No interpretarlos como un local individual simple.
- El registro debe diferenciarse de un restaurante.
- Si la búsqueda devuelve un mercado, usar la coincidencia solo como referencia del punto.

## 6. Restaurantes cerrados

- Un business_status cerrado permanente no valida el local como activo.
- Mantener el registro semilla con nota pública y nota interna explicando la vigencia no confirmada.
- No publicar un punto como activo si el único respaldo es un match cerrado.

## 7. Locales con nombre parecido

- Si el nombre coincide aproximadamente pero no exactamente, bajar la confianza.
- confidence_match:
  - alta: nombre y barrio/polo coinciden.
  - media: nombre coincide pero barrio/zona requiere revisión.
  - baja: nombre parecido o zona dudosa.
- Los matches de confianza baja deben revisarse manualmente.

## 8. Documentar confidence_match

- confidence_match es un campo interno.
- Sirve para control de calidad.
- Documentar en nota_interna la razón de la confianza.

## 9. Campos internos

No deben aparecer en productos públicos por defecto:
- query_google_places_principal
- query_google_places_alternativa
- google_place_id_interno
- rating_interno
- user_ratings_total_interno
- confidence_match
- nota_interna
- status_busqueda
- business_status
- fecha_consulta

## 10. Campos no públicos en PDF o mapas

- google_place_id_interno
- rating_interno
- user_ratings_total_interno
- query_google_places_principal
- query_google_places_alternativa
- nota_interna
- confidence_match
- status_busqueda
- fecha_consulta

En un mapa público, se pueden mostrar solo los puntos y nombres seleccionados con una leyenda prudente.
