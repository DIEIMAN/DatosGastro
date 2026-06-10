# Guia de fuentes para dashboard

Regla V3: si una vista usa seeds/manuales, debe mostrarse como no apta para dashboard real.

## Resumen general

- Tablas usadas: `analytics_resumen_ejecutivo.csv`
- Fuentes usadas: F01, F02, F03 y fuentes seed complementarias segun `fuentes_utilizadas`
- Texto sugerido: Fuente: BA Data / GCBA y fuentes relevadas. Fecha de consulta: ver campo `fecha_consulta_max`. Procesamiento propio.
- Limitaciones: no presentar como real si `estado_datos = datos seed` o `apto_dashboard != si`.
- Lista hoy: no.

## Establecimientos por barrio/comuna

- Tablas usadas: `analytics_establecimientos_por_categoria_barrio.csv`, `fact_establecimiento.csv`, `dim_ubicacion.csv`
- Fuentes usadas: F01 Oferta y Establecimientos Gastronomicos, y F02 si aporta habilitaciones.
- Texto sugerido: Fuente: BA Data / GCBA - Oferta y Establecimientos Gastronomicos. Fecha de consulta: AAAA-MM-DD. Procesamiento propio. Limitaciones: clasificacion gastronomica inferida por rubro; requiere validacion en casos ambiguos.
- Limitaciones: con seed de 6 filas no representa el universo de establecimientos.
- Lista hoy: no.

## Habilitaciones gastronomicas recientes

- Tablas usadas: `fact_establecimiento.csv` filtrando `id_fuente = F02`
- Fuentes usadas: F02 Habilitaciones Aprobadas AGC.
- Texto sugerido: Fuente: BA Data / GCBA - Habilitaciones Aprobadas AGC. Fecha de consulta: AAAA-MM-DD. Procesamiento propio. Limitaciones: clasificacion gastronomica inferida por rubro; requiere validacion en casos ambiguos.
- Limitaciones: hoy F02 seed esta vacio.
- Lista hoy: no.

## Ferias y mercados

- Tablas usadas: `fact_mercado_feria.csv`, `dim_ubicacion.csv`
- Fuentes usadas: F03 Ferias y Mercados.
- Texto sugerido: Fuente: BA Data / GCBA - Ferias y Mercados. Fecha de consulta: AAAA-MM-DD. Procesamiento propio. Limitaciones: validar cobertura, vigencia y geocodificacion.
- Limitaciones: hoy usa seed/manual.
- Lista hoy: no.

## Eventos gastronomicos

- Tablas usadas: `analytics_eventos_por_barrio.csv`, `fact_evento_gastronomico.csv`
- Fuentes usadas: fuentes privadas/oficiales relevadas en seed, segun `id_fuente`.
- Texto sugerido: Fuente: fuentes relevadas indicadas en el modelo. Fecha de consulta: AAAA-MM-DD. Procesamiento propio. Limitaciones: eventos sin sede fija usan ubicacion centinela; agenda no exhaustiva.
- Limitaciones: hoy no hay fuente real estructurada de agenda completa.
- Lista hoy: no.

## Programas y politicas

- Tablas usadas: `analytics_programas_por_anio.csv`, `fact_programa_politica.csv`
- Fuentes usadas: fuentes relevadas en seed.
- Texto sugerido: Fuente: GCBA y fuentes relevadas. Fecha de consulta: AAAA-MM-DD. Procesamiento propio. Limitaciones: metricas de impacto no estructuradas o no publicadas.
- Limitaciones: datos manuales de relevamiento inicial.
- Lista hoy: no para metricas; si como inventario cualitativo con advertencia.

## Mapa de oportunidades

- Tablas usadas: `analytics_mapa_oportunidades.csv`, `fact_establecimiento.csv`, `fact_evento_gastronomico.csv`, `fact_mercado_feria.csv`, `dim_ubicacion.csv`
- Fuentes usadas: F01, F02, F03 y fuentes de eventos.
- Texto sugerido: Fuente: BA Data / GCBA y fuentes relevadas. Fecha de consulta: AAAA-MM-DD. Procesamiento propio. Limitaciones: requiere datos reales completos, geocodificacion y validacion territorial.
- Limitaciones: con seeds no debe usarse para priorizar politicas o inversion.
- Lista hoy: no.
