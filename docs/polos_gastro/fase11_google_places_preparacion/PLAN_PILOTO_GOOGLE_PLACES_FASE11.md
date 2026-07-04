# Plan piloto Google Places — Fase 11

Fecha de preparación: 2026-07-02.

Este plan propone una primera ejecución pequeña y controlada de Google Places para PolosGastro.

## Objetivo del piloto

- Probar la tasa de match con la tabla semilla.
- Evaluar los campos devueltos y el comportamiento de la búsqueda.
- Identificar errores de coincidencia y ambigüedades.
- Validar criterios de revisión manual.

## Alcance recomendado

- 20 a 30 locales seleccionados de la tabla semilla.
- Incluir casos representativos de Palermo, Puerto Madero, San Telmo, Recoleta y algunos ambiguos.
- No ejecutar masivamente sobre los 106 locales.

## Selección inicial de queries

Priorizar:
- locales con nombre único claro y barrio definido.
- locales con nombres ambiguos o sucursales en varios polos.
- hitos colectivos de mercado/patio.

Ejemplos de consultas iniciales:
- Don Julio Palermo Buenos Aires
- La Fuerza Villa Crespo Buenos Aires
- La Fuerza Chacarita Buenos Aires
- La Mar Palermo Buenos Aires
- La Mar Belgrano Buenos Aires
- Sottovoce Puerto Madero Buenos Aires
- Sottovoce Recoleta Buenos Aires
- Napoles San Telmo Buenos Aires
- Napoles Avenida Caseros Buenos Aires
- Café Registrado Palermo Buenos Aires
- Café Registrado Avenida Caseros Buenos Aires

## Cómo guardar resultados

- Guardar cada respuesta en un CSV con el `id_local_semilla` original.
- Registrar la `query_google_places` exacta usada.
- Mantener `fecha_consulta` en cada fila.
- Mantener los campos internos separados de los parámetros públicos.
- Definir un directorio de resultados aislado bajo outputs/polos_gastro/fase11_google_places_preparacion/tablas/.

## Cómo cachear respuestas

- Cachear solo los resultados permitidos según la política de Google Places.
- Limitar la cache a metadatos mínimos y el `place_id`.
- Evitar guardar raw extensos si no son necesarios.
- No almacenar la API key en ningún CSV o archivo de salida.

## Cómo evitar duplicados

- No ejecutar la misma query más de una vez sin cambiar el polo/barrio.
- Registrar `query_google_places` y `status_busqueda` para cada intento.
- Si la misma ubicación aparece en varias filas, evaluar si corresponde a un registro compartido o a duplicado.
- En caso de duda, marcar `requiere_revision_manual`.

## Cómo no exponer API keys

- Usar variable de entorno `GOOGLE_MAPS_API_KEY`.
- No incluir la key en el código ni en archivos de salida.
- Usar `dry_run` por defecto; la primera ejecución real debe requerir un flag explícito.

## Cómo evitar publicar place_id

- Guardar `google_place_id_interno` sólo en la tabla interna.
- Nunca incluir `place_id` en PDF público, mapas o fichas externas.
- Usar el `place_id` sólo como identificador interno de control.

## Validación visual de puntos

- Verificar manualmente los resultados antes de publicar.
- Confirmar que el nombre y la dirección coincidan con la zona del polo.
- Para casos ambiguos, comparar con mapas y fuentes documentales propias.
- No publicar puntos sin revisión humana previa.
