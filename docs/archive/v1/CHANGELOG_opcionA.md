# Changelog — Opción A: arreglos estructurales (sin datos nuevos)

Fecha: 2026-06-10. No se descargó ni se inventó ningún dato. Solo se corrigió la estructura existente.

## 1. Integridad referencial de `fact_evento_gastronomico`
- Antes: `id_ubicacion = "No disponible"` y `id_organizador = "No normalizado"` (strings libres → FK rotas).
- Ahora: FKs válidas. Organizadores resueltos contra `dim_organizador` (O001…O008); ubicaciones apuntan al centinela `U00000` ("No determinado") porque son eventos multi-local o ciclos sin sede única. La sede textual declarada (ej. "La Rural", "Planetario") se preserva en `observaciones`, sin inventar una dirección normalizada.
- Validado: 0 FKs huérfanas en todo el modelo.

## 2. Normalización de barrios (catálogo Ley 2650) en `dim_ubicacion`
- "San Cristobal" → "San Cristóbal" (tilde).
- "Retiro/San Nicolás" (dos barrios en un campo) → "Retiro" (coincide con la dirección Alem 852). Documentado en `motivo_validacion`.
- `comuna` derivada del barrio vía tabla oficial (regla: comuna nunca a mano).
- Se agregó la fila centinela `U00000`.

## 3. Unificación de taxonomía analytics ↔ `dim_categoria`
- Antes: analytics usaba "Restaurante"/"Bar Notable"/"Bar Temático" (inconsistente con el modelo).
- Ahora: usa `categoria_general` real del join → "Restauración" / "Bar". Las analytics se derivan del modelo, no se tipean aparte.

## 4. Recálculo de tablas analytics DESDE el modelo
- `analytics_establecimientos_por_categoria_barrio`, `analytics_mapa_oportunidades`, `analytics_resumen_ejecutivo`, `analytics_eventos_por_barrio`, `analytics_programas_por_anio` recalculadas por join real.
- Todas conservan la advertencia explícita de "muestra seed (n=6), no padrón completo".
- `analytics_resumen_ejecutivo` ahora incluye el indicador clave `ubicaciones_geocodificadas = 0`.

## 5. SQL
- `02_create_tables.sql`: pasó de 4 a **11 tablas** (faltaban dim_organizador, fact_evento, fact_programa, fact_mercado_feria y los 3 puentes), con todas las FKs declaradas.
- `03_load_data.sql`: pasó de comentario-ejemplo a **carga real con `\copy`** en orden de dependencias (dimensiones → hechos → puentes).
- Modelo validado end-to-end (DDL + carga + joins) con motor SQL real: carga sin violar FKs.

## 6. Diccionario de datos
- Reescrito con el detalle de campos por tabla (antes remitía a "ver tablas"). Documenta el centinela U00000 y la convención de marcado de faltantes.
