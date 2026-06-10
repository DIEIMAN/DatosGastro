# Guia de fuentes para dashboard

Regla V3: si una vista usa seeds/manuales, debe mostrarse como no apta para dashboard real.

## Resumen general

- Tablas usadas: `analytics_resumen_ejecutivo.csv`
- Fuentes usadas: F01, F02, F03 y fuentes seed complementarias segun `fuentes_utilizadas`
- Texto sugerido: Datos: Buenos Aires Data - Gobierno de la Ciudad de Buenos Aires (datasets Oferta y Establecimientos Gastronomicos, Habilitaciones Aprobadas AGC y Ferias y Mercados). Consulta: 10/06/2026. Procesamiento propio. Licencia de origen: CC-BY-2.5-AR.
- Limitaciones: no presentar como real si `estado_datos = datos seed` o `apto_dashboard != si`.
- Lista hoy: si para F01/F02/F03; no incluye eventos/programas reales.

## Establecimientos por barrio/comuna

- Tablas usadas: `analytics_establecimientos_por_categoria_barrio.csv`, `fact_establecimiento.csv`, `dim_ubicacion.csv`
- Fuentes usadas: F01 Oferta y Establecimientos Gastronomicos, y F02 si aporta habilitaciones.
- Texto sugerido: Fuente: Buenos Aires Data / GCBA - Oferta y Establecimientos Gastronomicos (Ente de Turismo). Fecha de consulta: 10/06/2026. Procesamiento propio. Limitaciones: relevamiento sin actualizacion por registro; problemas de codificacion en el archivo original.
- Limitaciones: F01 no trae fecha por registro y puede estar desactualizado; F02 aporta altas/habilitaciones inferidas por rubro.
- Lista hoy: si.

## Habilitaciones gastronomicas recientes

- Tablas usadas: `fact_establecimiento.csv` filtrando `id_fuente = F02`
- Fuentes usadas: F02 Habilitaciones Aprobadas AGC.
- Texto sugerido: Fuente: Buenos Aires Data / GCBA - Habilitaciones Aprobadas AGC (Agencia Gubernamental de Control), recursos 2015-2025. Fecha de consulta: 10/06/2026. Procesamiento propio. Limitaciones: clasificacion gastronomica inferida a partir de la descripcion del rubro; sin datos 2026 publicados al momento de consulta.
- Limitaciones: clasificacion por keywords; casos ambiguos se excluyen del fact de establecimientos gastronomicos en modo estricto.
- Lista hoy: si.

## Ferias y mercados

- Tablas usadas: `fact_mercado_feria.csv`, `dim_ubicacion.csv`
- Fuentes usadas: F03 Ferias y Mercados.
- Texto sugerido: Fuente: Buenos Aires Data / GCBA - Ferias y Mercados (DG de Ferias, Min. de Ambiente y Espacio Publico). Fecha de consulta: 10/06/2026. Procesamiento propio. Limitaciones: geometria disponible solo para FIAB.
- Limitaciones: `f03_mercados.csv` descargo menos de 1 KB y queda como sospechoso; la geometria completa no esta disponible.
- Lista hoy: si con advertencia.

## Eventos gastronomicos

- Tablas usadas: `analytics_eventos_por_barrio.csv`, `fact_evento_gastronomico.csv`
- Fuentes usadas: fuentes privadas/oficiales relevadas en seed, segun `id_fuente`.
- Texto sugerido: Fuente: fuentes relevadas indicadas en el modelo. Fecha de consulta: AAAA-MM-DD. Procesamiento propio. Limitaciones: eventos sin sede fija usan ubicacion centinela; agenda no exhaustiva.
- Limitaciones: hoy no hay fuente real estructurada de agenda completa.
- Lista hoy: no.

## Programas y politicas

- Tablas usadas: `analytics_programas_por_anio.csv`, `fact_programa_politica.csv`
- Fuentes usadas: fuentes relevadas en seed.
- Texto sugerido: Fuente: no disponible como dataset real estructurado en esta version. No publicar como metrica de dashboard.
- Limitaciones: no hay fuente real estructurada de programas/politicas cargada en modo estricto.
- Lista hoy: no.

## Mapa de oportunidades

- Tablas usadas: `analytics_mapa_oportunidades.csv`, `fact_establecimiento.csv`, `fact_evento_gastronomico.csv`, `fact_mercado_feria.csv`, `dim_ubicacion.csv`
- Fuentes usadas: F01, F02, F03 y fuentes de eventos.
- Texto sugerido: Elaboracion propia sobre Buenos Aires Data / GCBA (Oferta y Establecimientos Gastronomicos, Habilitaciones Aprobadas AGC 2015-2025 y Ferias y Mercados). Fecha de consulta: 10/06/2026. Cruces y normalizacion de elaboracion propia; algunas ubicaciones pueden quedar inferidas a nivel barrio/comuna.
- Limitaciones: geocodificacion pendiente; algunas ubicaciones quedan a nivel texto/barrio/comuna.
- Lista hoy: si con advertencia metodologica.
