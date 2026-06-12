# Auditoria de datos reales vs seed

Generado: 2026-06-12

Regla V3: ninguna salida de dashboard debe presentarse como dato real si deriva de seeds/manuales.
Regla conceptual: F01 oferta registrada, F02 habilitaciones aprobadas y F03 ferias/mercados se comunican por separado.
Advertencia F03: contiene recursos con distintos niveles de grano. Los puestos individuales no deben interpretarse como ferias o mercados; los indicadores principales usan espacios reales.

## Decision de estructura

Se eligio la opcion A: `data/raw/` queda reservado para datos reales descargados y `data/seeds/` contiene fallback de desarrollo.

## raw

### f01_oferta_establecimientos_gastronomicos.csv

- Filas x columnas: 2823 x 18
- Origen detectado: dataset real probable
- Apto dashboard: requiere_validacion
- Motivo: requiere revisar contrato, fuente y cobertura antes de dashboard
- Fuentes: No disponible
- Riesgo de decision: alto
- Recomendacion: cargar fuente real o validar cobertura antes de usar

### f02_habilitaciones_aprobadas_2015_2018.csv

- Filas x columnas: 137463 x 18
- Origen detectado: dataset real probable
- Apto dashboard: requiere_validacion
- Motivo: requiere revisar contrato, fuente y cobertura antes de dashboard
- Fuentes: No disponible
- Riesgo de decision: alto
- Recomendacion: cargar fuente real o validar cobertura antes de usar

### f02_habilitaciones_aprobadas_2019.csv

- Filas x columnas: 23203 x 19
- Origen detectado: dataset real probable
- Apto dashboard: requiere_validacion
- Motivo: requiere revisar contrato, fuente y cobertura antes de dashboard
- Fuentes: No disponible
- Riesgo de decision: alto
- Recomendacion: cargar fuente real o validar cobertura antes de usar

### f02_habilitaciones_aprobadas_2020.csv

- Filas x columnas: 12938 x 21
- Origen detectado: dataset real probable
- Apto dashboard: requiere_validacion
- Motivo: requiere revisar contrato, fuente y cobertura antes de dashboard
- Fuentes: No disponible
- Riesgo de decision: alto
- Recomendacion: cargar fuente real o validar cobertura antes de usar

### f02_habilitaciones_aprobadas_2021.csv

- Filas x columnas: 31829 x 609
- Origen detectado: dataset real probable
- Apto dashboard: requiere_validacion
- Motivo: requiere revisar contrato, fuente y cobertura antes de dashboard
- Fuentes: No disponible
- Riesgo de decision: alto
- Recomendacion: cargar fuente real o validar cobertura antes de usar

### f02_habilitaciones_aprobadas_2022.csv

- Filas x columnas: 26430 x 21
- Origen detectado: dataset real probable
- Apto dashboard: requiere_validacion
- Motivo: requiere revisar contrato, fuente y cobertura antes de dashboard
- Fuentes: No disponible
- Riesgo de decision: alto
- Recomendacion: cargar fuente real o validar cobertura antes de usar

### f02_habilitaciones_aprobadas_2023.csv

- Filas x columnas: 5063 x 21
- Origen detectado: dataset real probable
- Apto dashboard: requiere_validacion
- Motivo: requiere revisar contrato, fuente y cobertura antes de dashboard
- Fuentes: No disponible
- Riesgo de decision: alto
- Recomendacion: cargar fuente real o validar cobertura antes de usar

### f02_habilitaciones_aprobadas_2024.csv

- Filas x columnas: 8637 x 21
- Origen detectado: dataset real probable
- Apto dashboard: requiere_validacion
- Motivo: requiere revisar contrato, fuente y cobertura antes de dashboard
- Fuentes: No disponible
- Riesgo de decision: alto
- Recomendacion: cargar fuente real o validar cobertura antes de usar

### f02_habilitaciones_aprobadas_2025.csv

- Filas x columnas: 145483 x 9
- Origen detectado: dataset real probable
- Apto dashboard: requiere_validacion
- Motivo: requiere revisar contrato, fuente y cobertura antes de dashboard
- Fuentes: No disponible
- Riesgo de decision: alto
- Recomendacion: cargar fuente real o validar cobertura antes de usar

### f03_ferias.csv

- Filas x columnas: 30 x 15
- Origen detectado: dataset real probable
- Apto dashboard: requiere_validacion
- Motivo: requiere revisar contrato, fuente y cobertura antes de dashboard
- Fuentes: No disponible
- Riesgo de decision: alto
- Recomendacion: cargar fuente real o validar cobertura antes de usar

### f03_ferias_mercados.csv

- Filas x columnas: 4352 x 7
- Origen detectado: dataset real probable
- Apto dashboard: requiere_validacion
- Motivo: requiere revisar contrato, fuente y cobertura antes de dashboard
- Fuentes: No disponible
- Riesgo de decision: alto
- Recomendacion: cargar fuente real o validar cobertura antes de usar

### f03_fiab.geojson

- Filas x columnas: 0 x 0
- Origen detectado: dataset real probable
- Apto dashboard: no
- Motivo: archivo vacio o sin filas
- Fuentes: No disponible
- Riesgo de decision: alto
- Recomendacion: cargar fuente real o validar cobertura antes de usar

### f03_mercados.csv

- Filas x columnas: 6 x 5
- Origen detectado: pendiente/insuficiente
- Apto dashboard: no
- Motivo: archivo menor a 1 KB; no tratar como dataset real
- Fuentes: No disponible
- Riesgo de decision: alto
- Recomendacion: cargar fuente real o validar cobertura antes de usar

### f04_eventos_gastronomicos.csv

- Filas x columnas: 29 x 33
- Origen detectado: dataset real probable
- Apto dashboard: requiere_validacion
- Motivo: requiere revisar contrato, fuente y cobertura antes de dashboard
- Fuentes: No disponible
- Riesgo de decision: alto
- Recomendacion: cargar fuente real o validar cobertura antes de usar

### f05_programas_politicas_gastronomicas.csv

- Filas x columnas: 9 x 28
- Origen detectado: dataset real probable
- Apto dashboard: requiere_validacion
- Motivo: requiere revisar contrato, fuente y cobertura antes de dashboard
- Fuentes: No disponible
- Riesgo de decision: alto
- Recomendacion: cargar fuente real o validar cobertura antes de usar

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

- Filas x columnas: 18 x 5
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

- Filas x columnas: 15 x 6
- Origen detectado: modelo/dimension
- Apto dashboard: requiere_validacion
- Motivo: requiere revisar contrato, fuente y cobertura antes de dashboard
- Fuentes: No disponible
- Riesgo de decision: alto
- Recomendacion: cargar fuente real o validar cobertura antes de usar

### dim_ubicacion.csv

- Filas x columnas: 10545 x 12
- Origen detectado: modelo/dimension
- Apto dashboard: requiere_validacion
- Motivo: requiere revisar contrato, fuente y cobertura antes de dashboard
- Fuentes: No disponible
- Riesgo de decision: alto
- Recomendacion: cargar fuente real o validar cobertura antes de usar

### fact_espacio_feria_mercado.csv

- Filas x columnas: 220 x 24
- Origen detectado: datos reales
- Apto dashboard: requiere_validacion
- Motivo: requiere revisar contrato, fuente y cobertura antes de dashboard
- Fuentes: F03
- Riesgo de decision: alto
- Recomendacion: cargar fuente real o validar cobertura antes de usar

### fact_establecimiento.csv

- Filas x columnas: 2823 x 25
- Origen detectado: datos reales parciales
- Apto dashboard: requiere_validacion
- Motivo: requiere revisar contrato, fuente y cobertura antes de dashboard
- Fuentes: F01
- Riesgo de decision: alto
- Recomendacion: cargar fuente real o validar cobertura antes de usar

### fact_evento_gastronomico.csv

- Filas x columnas: 29 x 42
- Origen detectado: relevamiento_manual_trazable
- Apto dashboard: requiere_validacion
- Motivo: requiere revisar contrato, fuente y cobertura antes de dashboard
- Fuentes: F04
- Riesgo de decision: alto
- Recomendacion: cargar fuente real o validar cobertura antes de usar

### fact_habilitacion_gastronomica.csv

- Filas x columnas: 44169 x 24
- Origen detectado: datos reales parciales
- Apto dashboard: requiere_validacion
- Motivo: requiere revisar contrato, fuente y cobertura antes de dashboard
- Fuentes: F02
- Riesgo de decision: alto
- Recomendacion: cargar fuente real o validar cobertura antes de usar

### fact_mercado_feria.csv

- Filas x columnas: 220 x 20
- Origen detectado: datos reales
- Apto dashboard: requiere_validacion
- Motivo: requiere revisar contrato, fuente y cobertura antes de dashboard
- Fuentes: F03
- Riesgo de decision: alto
- Recomendacion: cargar fuente real o validar cobertura antes de usar

### fact_programa_politica.csv

- Filas x columnas: 9 x 35
- Origen detectado: relevamiento_manual_trazable
- Apto dashboard: requiere_validacion
- Motivo: requiere revisar contrato, fuente y cobertura antes de dashboard
- Fuentes: F05
- Riesgo de decision: alto
- Recomendacion: cargar fuente real o validar cobertura antes de usar

### fact_puesto_feria.csv

- Filas x columnas: 4352 x 18
- Origen detectado: datos reales
- Apto dashboard: no
- Motivo: insumo tecnico/auditoria interna; no exponer en dashboard
- Fuentes: F03
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

### puente_evento_programa.csv

- Filas x columnas: 10 x 4
- Origen detectado: modelo/dimension
- Apto dashboard: requiere_validacion
- Motivo: requiere revisar contrato, fuente y cobertura antes de dashboard
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

### analytics_espacios_ferias_mercados_por_comuna.csv

- Filas x columnas: 18 x 10
- Origen detectado: datos reales
- Apto dashboard: si
- Motivo: apto_dashboard provisto por analytics
- Fuentes: F03
- Riesgo de decision: bajo/normal
- Recomendacion: puede usarse citando fuentes y fecha

### analytics_espacios_ferias_mercados_por_tipo.csv

- Filas x columnas: 3 x 10
- Origen detectado: datos reales
- Apto dashboard: si
- Motivo: apto_dashboard provisto por analytics
- Fuentes: F03
- Riesgo de decision: bajo/normal
- Recomendacion: puede usarse citando fuentes y fecha

### analytics_establecimientos_por_categoria_barrio.csv

- Filas x columnas: 203 x 14
- Origen detectado: datos reales
- Apto dashboard: si
- Motivo: apto_dashboard provisto por analytics
- Fuentes: F01
- Riesgo de decision: bajo/normal
- Recomendacion: puede usarse citando fuentes y fecha

### analytics_eventos_cualitativos.csv

- Filas x columnas: 16 x 17
- Origen detectado: datos reales semiestructurados
- Apto dashboard: no
- Motivo: analytics no apta o basada en seed/parcial
- Fuentes: F04
- Riesgo de decision: alto
- Recomendacion: cargar fuente real o validar cobertura antes de usar

### analytics_eventos_por_anio.csv

- Filas x columnas: 6 x 10
- Origen detectado: datos reales semiestructurados
- Apto dashboard: si
- Motivo: apto_dashboard provisto por analytics
- Fuentes: F04
- Riesgo de decision: bajo/normal
- Recomendacion: puede usarse citando fuentes y fecha

### analytics_eventos_por_barrio.csv

- Filas x columnas: 10 x 14
- Origen detectado: datos reales semiestructurados
- Apto dashboard: si
- Motivo: apto_dashboard provisto por analytics
- Fuentes: F04
- Riesgo de decision: bajo/normal
- Recomendacion: puede usarse citando fuentes y fecha

### analytics_eventos_por_tipo.csv

- Filas x columnas: 5 x 10
- Origen detectado: datos reales semiestructurados
- Apto dashboard: si
- Motivo: apto_dashboard provisto por analytics
- Fuentes: F04
- Riesgo de decision: bajo/normal
- Recomendacion: puede usarse citando fuentes y fecha

### analytics_fiab_por_comuna.csv

- Filas x columnas: 18 x 10
- Origen detectado: datos reales
- Apto dashboard: si
- Motivo: apto_dashboard provisto por analytics
- Fuentes: F03
- Riesgo de decision: bajo/normal
- Recomendacion: puede usarse citando fuentes y fecha

### analytics_habilitaciones_por_anio.csv

- Filas x columnas: 8 x 13
- Origen detectado: datos reales
- Apto dashboard: si
- Motivo: apto_dashboard provisto por analytics
- Fuentes: F02
- Riesgo de decision: bajo/normal
- Recomendacion: puede usarse citando fuentes y fecha

### analytics_habilitaciones_por_barrio.csv

- Filas x columnas: 16 x 11
- Origen detectado: datos reales
- Apto dashboard: si
- Motivo: apto_dashboard provisto por analytics
- Fuentes: F02
- Riesgo de decision: bajo/normal
- Recomendacion: puede usarse citando fuentes y fecha

### analytics_habilitaciones_por_categoria.csv

- Filas x columnas: 12 x 11
- Origen detectado: datos reales
- Apto dashboard: si
- Motivo: apto_dashboard provisto por analytics
- Fuentes: F02
- Riesgo de decision: bajo/normal
- Recomendacion: puede usarse citando fuentes y fecha

### analytics_habilitaciones_recientes.csv

- Filas x columnas: 500 x 21
- Origen detectado: datos reales
- Apto dashboard: si
- Motivo: apto_dashboard provisto por analytics
- Fuentes: F02
- Riesgo de decision: bajo/normal
- Recomendacion: puede usarse citando fuentes y fecha

### analytics_mapa_oportunidades.csv

- Filas x columnas: 61 x 18
- Origen detectado: datos reales
- Apto dashboard: si
- Motivo: apto_dashboard provisto por analytics
- Fuentes: F01 | F02 | F03 | F04
- Riesgo de decision: bajo/normal
- Recomendacion: puede usarse citando fuentes y fecha

### analytics_programas_catalogo.csv

- Filas x columnas: 4 x 17
- Origen detectado: datos reales semiestructurados
- Apto dashboard: si
- Motivo: apto_dashboard provisto por analytics
- Fuentes: F05
- Riesgo de decision: bajo/normal
- Recomendacion: puede usarse citando fuentes y fecha

### analytics_programas_cualitativos.csv

- Filas x columnas: 5 x 16
- Origen detectado: datos reales semiestructurados
- Apto dashboard: no
- Motivo: analytics no apta o basada en seed/parcial
- Fuentes: F05
- Riesgo de decision: alto
- Recomendacion: cargar fuente real o validar cobertura antes de usar

### analytics_programas_por_anio.csv

- Filas x columnas: 3 x 11
- Origen detectado: datos reales semiestructurados
- Apto dashboard: si
- Motivo: apto_dashboard provisto por analytics
- Fuentes: F05
- Riesgo de decision: bajo/normal
- Recomendacion: puede usarse citando fuentes y fecha

### analytics_programas_por_estado.csv

- Filas x columnas: 3 x 10
- Origen detectado: datos reales semiestructurados
- Apto dashboard: si
- Motivo: apto_dashboard provisto por analytics
- Fuentes: F05
- Riesgo de decision: bajo/normal
- Recomendacion: puede usarse citando fuentes y fecha

### analytics_programas_por_tipo.csv

- Filas x columnas: 4 x 10
- Origen detectado: datos reales semiestructurados
- Apto dashboard: si
- Motivo: apto_dashboard provisto por analytics
- Fuentes: F05
- Riesgo de decision: bajo/normal
- Recomendacion: puede usarse citando fuentes y fecha

### analytics_resumen_ejecutivo.csv

- Filas x columnas: 11 x 12
- Origen detectado: datos reales
- Apto dashboard: si
- Motivo: apto_dashboard provisto por analytics
- Fuentes: F01 | F02 | F03 | F04 | F05
- Riesgo de decision: bajo/normal
- Recomendacion: puede usarse citando fuentes y fecha

## Resumen dashboard

- Apto hoy: analytics_espacios_ferias_mercados_por_comuna.csv, analytics_espacios_ferias_mercados_por_tipo.csv, analytics_establecimientos_por_categoria_barrio.csv, analytics_eventos_por_anio.csv, analytics_eventos_por_barrio.csv, analytics_eventos_por_tipo.csv, analytics_fiab_por_comuna.csv, analytics_habilitaciones_por_anio.csv, analytics_habilitaciones_por_barrio.csv, analytics_habilitaciones_por_categoria.csv, analytics_habilitaciones_recientes.csv, analytics_mapa_oportunidades.csv, analytics_programas_catalogo.csv, analytics_programas_por_anio.csv, analytics_programas_por_estado.csv, analytics_programas_por_tipo.csv, analytics_resumen_ejecutivo.csv.
- No apto hoy: analytics_eventos_cualitativos.csv, analytics_programas_cualitativos.csv.
- Advertencia obligatoria: no sumar F01 y F02 como establecimientos gastronomicos.
- Advertencia F03: no contar puestos/personas como espacios de ferias o mercados.