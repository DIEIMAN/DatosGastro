# Guia de fuentes para dashboard

Regla V3: si una vista usa seeds/manuales, debe mostrarse como no apta para dashboard real. F01, F02 y F03 deben comunicarse como conceptos separados.

## Regla de comunicacion obligatoria

Nunca mostrar:

> "90.764 establecimientos gastronomicos"

Tampoco mostrar ningun total combinado F01+F02 como establecimientos activos.

Mostrar metricas separadas:

> "2.823 registros en Oferta Gastronomica F01"
> "87.934 habilitaciones gastronomicas inferidas desde AGC F02"
> "4.388 registros de ferias/mercados F03"

Cada metrica debe mostrar fuente, URL o dataset, fecha de consulta, procesamiento propio y limitaciones.

## Resumen general

- Tabla usada: `analytics_resumen_ejecutivo.csv`
- Fuentes usadas: F01, F02 y F03 para los indicadores reales; eventos y programas quedan en 0 hasta cargar fuentes reales estructuradas.
- Texto sugerido: Datos: Buenos Aires Data - Gobierno de la Ciudad de Buenos Aires. Datasets: Oferta y Establecimientos Gastronomicos F01, Habilitaciones Aprobadas AGC F02 y Ferias y Mercados F03. Consulta: 10/06/2026. Procesamiento propio. Licencia de origen: CC-BY-2.5-AR.
- Limitaciones: no sumar F01 + F02; F02 son habilitaciones aprobadas, no establecimientos activos unicos.
- Lista hoy: si para F01/F02/F03; no para eventos/programas reales.

## Oferta gastronomica F01

- Tablas usadas: `analytics_establecimientos_por_categoria_barrio.csv`, `fact_establecimiento.csv`, `dim_ubicacion.csv`
- Fuentes usadas: F01 Oferta y Establecimientos Gastronomicos.
- Texto sugerido: Fuente: Buenos Aires Data / GCBA - Oferta y Establecimientos Gastronomicos. Fecha de consulta: 10/06/2026. Procesamiento propio.
- Limitaciones: F01 no trae fecha de vigencia por registro y puede estar desactualizado; problemas de codificacion del archivo original pueden requerir revision.
- Lista hoy: si.

## Habilitaciones gastronomicas F02

- Tablas usadas: `fact_habilitacion_gastronomica.csv`, `analytics_habilitaciones_por_anio.csv`, `analytics_habilitaciones_por_barrio.csv`, `analytics_habilitaciones_por_categoria.csv`, `analytics_habilitaciones_recientes.csv`
- Fuentes usadas: F02 Habilitaciones Aprobadas AGC, recursos 2015-2025.
- Texto sugerido: Fuente: Buenos Aires Data / GCBA - Habilitaciones Aprobadas AGC, recursos 2015-2025. Fecha de consulta: 10/06/2026. Procesamiento propio.
- Limitaciones: clasificacion gastronomica inferida a partir de descripcion de rubro; F02 no equivale a establecimientos activos ni a locales unicos; sin datos 2026 publicados al momento de consulta.
- Lista hoy: si, con advertencia metodologica obligatoria.

## Ferias y mercados F03

- Tablas usadas: `fact_mercado_feria.csv`, `dim_ubicacion.csv`
- Fuentes usadas: F03 Ferias y Mercados.
- Texto sugerido: Fuente: Buenos Aires Data / GCBA - Ferias y Mercados. Fecha de consulta: 10/06/2026. Procesamiento propio.
- Limitaciones: `f03_mercados.csv` descargo menos de 1 KB y queda como sospechoso; la geometria completa no esta disponible para todos los recursos.
- Lista hoy: si con advertencia.

## Eventos gastronomicos

- Tablas usadas: `analytics_eventos_por_barrio.csv`, `fact_evento_gastronomico.csv`
- Fuentes usadas: no hay fuente real estructurada cargada en modo estricto.
- Texto sugerido: No publicar como metrica real hasta incorporar una fuente estructurada de agenda/eventos.
- Limitaciones: hoy no hay dataset real de eventos gastronomicos cargado.
- Lista hoy: no.

## Programas y politicas

- Tablas usadas: `analytics_programas_por_anio.csv`, `fact_programa_politica.csv`
- Fuentes usadas: no hay fuente real estructurada cargada en modo estricto.
- Texto sugerido: No publicar como metrica real hasta incorporar una fuente estructurada de programas/politicas.
- Limitaciones: no hay fuente real estructurada de programas/politicas cargada en modo estricto.
- Lista hoy: no.

## Mapa de oportunidades

- Tabla usada: `analytics_mapa_oportunidades.csv`
- Variables: `densidad_establecimientos_f01`, `cantidad_habilitaciones_f02`, `cantidad_ferias_mercados_f03`.
- Fuentes usadas: F01, F02 y F03.
- Texto sugerido: Elaboracion propia sobre Buenos Aires Data / GCBA. El mapa separa oferta registrada F01, habilitaciones aprobadas F02 y ferias/mercados F03. Fecha de consulta: 10/06/2026.
- Limitaciones: geocodificacion pendiente; algunas ubicaciones quedan a nivel texto/barrio/comuna; no sumar F02 como establecimientos activos.
- Lista hoy: si con advertencia metodologica.
