# Auditoria de datos reales vs seed

Generado: 2026-06-10

Regla V3: ninguna salida de dashboard debe presentarse como dato real si deriva de seeds/manuales.

## Decision de estructura

Se eligio la opcion A: `data/raw/` queda reservado para datos reales descargados y `data/seeds/` contiene fallback de desarrollo.

## raw

No hay archivos.

## seeds

### raw_establecimientos_gastronomicos.csv

- Filas x columnas: 6 x 12
- Origen detectado: seed/manual
- Apto dashboard: no
- Motivo: seed/manual; solo desarrollo
- Fuentes: F01
- Riesgo de decision: alto
- Recomendacion: cargar fuente real o validar cobertura antes de usar

### raw_eventos_gastronomicos.csv

- Filas x columnas: 6 x 12
- Origen detectado: seed/manual
- Apto dashboard: no
- Motivo: seed/manual; solo desarrollo
- Fuentes: F07 | F08 | F13 | F14
- Riesgo de decision: alto
- Recomendacion: cargar fuente real o validar cobertura antes de usar

### raw_ferias_mercados.csv

- Filas x columnas: 6 x 14
- Origen detectado: seed/manual
- Apto dashboard: no
- Motivo: seed/manual; solo desarrollo
- Fuentes: F03 | F08 | F15
- Riesgo de decision: alto
- Recomendacion: cargar fuente real o validar cobertura antes de usar

### raw_fuentes_relevadas.csv

- Filas x columnas: 16 x 9
- Origen detectado: seed/manual
- Apto dashboard: no
- Motivo: seed/manual; solo desarrollo
- Fuentes: No disponible
- Riesgo de decision: alto
- Recomendacion: cargar fuente real o validar cobertura antes de usar

### raw_habilitaciones_aprobadas.csv

- Filas x columnas: 0 x 14
- Origen detectado: seed/manual
- Apto dashboard: no
- Motivo: archivo vacio o sin filas
- Fuentes: No disponible
- Riesgo de decision: alto
- Recomendacion: cargar fuente real o validar cobertura antes de usar

### raw_normativa_gastronomica.csv

- Filas x columnas: 1 x 12
- Origen detectado: seed/manual
- Apto dashboard: no
- Motivo: seed/manual; solo desarrollo
- Fuentes: F10
- Riesgo de decision: alto
- Recomendacion: cargar fuente real o validar cobertura antes de usar

### raw_programas_politicas.csv

- Filas x columnas: 6 x 11
- Origen detectado: seed/manual
- Apto dashboard: no
- Motivo: seed/manual; solo desarrollo
- Fuentes: F06 | F07 | F09 | F10 | F12
- Riesgo de decision: alto
- Recomendacion: cargar fuente real o validar cobertura antes de usar

## processed

### dim_categoria_gastronomica.csv

- Filas x columnas: 17 x 5
- Origen detectado: modelo/dimension
- Apto dashboard: requiere_validacion
- Motivo: requiere revisar contrato, fuente y cobertura antes de dashboard
- Fuentes: No disponible
- Riesgo de decision: alto
- Recomendacion: cargar fuente real o validar cobertura antes de usar

### dim_fuente.csv

- Filas x columnas: 16 x 9
- Origen detectado: modelo/dimension
- Apto dashboard: requiere_validacion
- Motivo: requiere revisar contrato, fuente y cobertura antes de dashboard
- Fuentes: F01 | F02 | F03 | F04 | F05 | F06 | F07 | F08 | F09 | F10 | F11 | F12 | F13 | F14 | F15 | F16
- Riesgo de decision: alto
- Recomendacion: cargar fuente real o validar cobertura antes de usar

### dim_organizador.csv

- Filas x columnas: 6 x 6
- Origen detectado: modelo/dimension
- Apto dashboard: requiere_validacion
- Motivo: requiere revisar contrato, fuente y cobertura antes de dashboard
- Fuentes: No disponible
- Riesgo de decision: alto
- Recomendacion: cargar fuente real o validar cobertura antes de usar

### dim_ubicacion.csv

- Filas x columnas: 16 x 12
- Origen detectado: modelo/dimension
- Apto dashboard: requiere_validacion
- Motivo: requiere revisar contrato, fuente y cobertura antes de dashboard
- Fuentes: No disponible
- Riesgo de decision: alto
- Recomendacion: cargar fuente real o validar cobertura antes de usar

### fact_establecimiento.csv

- Filas x columnas: 6 x 21
- Origen detectado: datos seed
- Apto dashboard: no
- Motivo: seed/manual; solo desarrollo
- Fuentes: F01
- Riesgo de decision: alto
- Recomendacion: cargar fuente real o validar cobertura antes de usar

### fact_evento_gastronomico.csv

- Filas x columnas: 6 x 22
- Origen detectado: datos seed
- Apto dashboard: no
- Motivo: seed/manual; solo desarrollo
- Fuentes: F07 | F08 | F13 | F14
- Riesgo de decision: alto
- Recomendacion: cargar fuente real o validar cobertura antes de usar

### fact_mercado_feria.csv

- Filas x columnas: 6 x 18
- Origen detectado: datos seed
- Apto dashboard: no
- Motivo: seed/manual; solo desarrollo
- Fuentes: F03 | F08 | F15
- Riesgo de decision: alto
- Recomendacion: cargar fuente real o validar cobertura antes de usar

### fact_programa_politica.csv

- Filas x columnas: 6 x 20
- Origen detectado: datos seed
- Apto dashboard: no
- Motivo: seed/manual; solo desarrollo
- Fuentes: F06 | F07 | F09 | F10 | F12
- Riesgo de decision: alto
- Recomendacion: cargar fuente real o validar cobertura antes de usar

### puente_evento_categoria.csv

- Filas x columnas: 0 x 3
- Origen detectado: modelo/dimension
- Apto dashboard: no
- Motivo: archivo vacio o sin filas
- Fuentes: No disponible
- Riesgo de decision: alto
- Recomendacion: cargar fuente real o validar cobertura antes de usar

### puente_evento_establecimiento.csv

- Filas x columnas: 0 x 4
- Origen detectado: modelo/dimension
- Apto dashboard: no
- Motivo: archivo vacio o sin filas
- Fuentes: No disponible
- Riesgo de decision: alto
- Recomendacion: cargar fuente real o validar cobertura antes de usar

### puente_programa_establecimiento.csv

- Filas x columnas: 0 x 5
- Origen detectado: modelo/dimension
- Apto dashboard: no
- Motivo: archivo vacio o sin filas
- Fuentes: No disponible
- Riesgo de decision: alto
- Recomendacion: cargar fuente real o validar cobertura antes de usar

## analytics

### analytics_establecimientos_por_categoria_barrio.csv

- Filas x columnas: 6 x 14
- Origen detectado: datos seed
- Apto dashboard: no
- Motivo: analytics no apta o basada en seed/parcial
- Fuentes: F01
- Riesgo de decision: alto
- Recomendacion: cargar fuente real o validar cobertura antes de usar

### analytics_eventos_por_barrio.csv

- Filas x columnas: 2 x 14
- Origen detectado: datos seed
- Apto dashboard: no
- Motivo: analytics no apta o basada en seed/parcial
- Fuentes: F07 | F08 | F13 | F14
- Riesgo de decision: alto
- Recomendacion: cargar fuente real o validar cobertura antes de usar

### analytics_mapa_oportunidades.csv

- Filas x columnas: 8 x 17
- Origen detectado: datos seed
- Apto dashboard: no
- Motivo: analytics no apta o basada en seed/parcial
- Fuentes: F01 | F03 | F07 | F08 | F13 | F14 | F15
- Riesgo de decision: alto
- Recomendacion: cargar fuente real o validar cobertura antes de usar

### analytics_programas_por_anio.csv

- Filas x columnas: 1 x 11
- Origen detectado: datos seed
- Apto dashboard: no
- Motivo: analytics no apta o basada en seed/parcial
- Fuentes: F06 | F07 | F09 | F10 | F12
- Riesgo de decision: alto
- Recomendacion: cargar fuente real o validar cobertura antes de usar

### analytics_resumen_ejecutivo.csv

- Filas x columnas: 6 x 10
- Origen detectado: datos seed
- Apto dashboard: no
- Motivo: analytics no apta o basada en seed/parcial
- Fuentes: F01 | F03 | F06 | F07 | F08 | F09 | F10 | F12 | F13 | F14 | F15
- Riesgo de decision: alto
- Recomendacion: cargar fuente real o validar cobertura antes de usar

## Resumen dashboard

- Apto hoy: ninguna tabla analytics importante es apta para dashboard real mientras F01/F02/F03 usen seeds o falten.
- No apto hoy: resumen general, establecimientos por barrio/comuna, eventos, ferias/mercados y mapa de oportunidades.