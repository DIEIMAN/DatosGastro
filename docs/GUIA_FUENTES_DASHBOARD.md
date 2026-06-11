# Guia de fuentes para dashboard

Regla V3: si una vista usa seeds/manuales, debe mostrarse como no apta para dashboard real. F01, F02 y F03 deben comunicarse como conceptos separados. F04 y F05 son relevamientos manuales trazables, no datasets oficiales estructurados.

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
- Fuentes usadas: F01, F02, F03 y relevamientos manuales trazables F04/F05.
- Texto sugerido: Datos: Buenos Aires Data - Gobierno de la Ciudad de Buenos Aires para F01/F02/F03, y relevamiento manual trazable para F04/F05. Consulta: 10/06/2026. Procesamiento propio.
- Limitaciones: no sumar F01 + F02; F02 son habilitaciones aprobadas; F04/F05 no representan universos completos.
- Lista hoy: si, con advertencias por fuente.

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

- Tablas usadas: `analytics_eventos_por_barrio.csv`, `analytics_eventos_por_tipo.csv`, `analytics_eventos_por_anio.csv`, `analytics_eventos_cualitativos.csv`, `fact_evento_gastronomico.csv`
- Fuentes usadas: F04 relevamiento manual trazable.
- Texto sugerido: Fuente: Relevamiento propio de eventos, ciclos, concursos y activaciones vinculados a la politica gastronomica de la Ciudad de Buenos Aires (BA Capital Gastronomica / Direccion General de Desarrollo Gastronomico / Ministerio de Desarrollo Economico, y estructuras antecesoras como la Subsecretaria de Politicas Gastronomicas), sobre comunicaciones oficiales del GCBA (buenosaires.gob.ar y turismo.buenosaires.gob.ar) y el Boletin Oficial de la CABA. Los eventos de organizacion privada con vinculo o presencia institucional de la Ciudad se identifican como tales, indicando el tipo de vinculo. Datos consultados al 10/06/2026. Las cifras de asistencia y locales adheridos corresponden a declaraciones de los organizadores; los totales de eventos de alcance nacional no son atribuibles a CABA. No existe a la fecha un dataset oficial estructurado de eventos gastronomicos.
- Limitaciones: F04 no representa el universo completo de eventos. Las metricas fuertes solo consideran `apto_dashboard = si`, `requiere_validacion = no`, fecha completa y vinculo GCBA no ambiguo. Las filas dudosas van a `analytics_eventos_cualitativos.csv`.
- Lista hoy: si para metricas fuertes filtradas; cualitativos solo como fichas/alertas.

## Programas y politicas

- Tablas usadas: `analytics_programas_por_tipo.csv`, `analytics_programas_por_estado.csv`, `analytics_programas_catalogo.csv`, `analytics_programas_cualitativos.csv`, `fact_programa_politica.csv`
- Fuentes usadas: F05 relevamiento manual trazable.
- Texto sugerido: Fuente: Relevamiento manual trazable de programas, politicas, normativa e instrumentos vinculados a la gastronomia en la Ciudad de Buenos Aires, elaborado sobre paginas institucionales del GCBA (Ministerio de Desarrollo Economico, Ministerio de Cultura, Jefatura de Gabinete), normativa publicada (Ley 35/1998, Ley 5213/2014, Ley 6447/2021), disposiciones del Boletin Oficial de la CABA y anuncios oficiales del Banco Ciudad. No constituye un dataset oficial: es un catalogo curado con fecha de consulta 10/06/2026. No existen, en las fuentes relevadas, presupuestos, metricas ni resultados publicados de forma estructurada para estos programas; donde un dato economico aparece, corresponde al momento de su anuncio y puede estar desactualizado. El estado de vigencia se indica en cada ficha junto con su nivel de validacion.
- Limitaciones: F05 es catalogo/fichero, no serie temporal de impacto. No inventar resultados ni usar presupuestos o montos viejos como vigentes. Las filas no aptas o con validacion pendiente van a `analytics_programas_cualitativos.csv`.
- Lista hoy: si como catalogo filtrado; no como impacto ni evolucion temporal.

## Mapa de oportunidades

- Tabla usada: `analytics_mapa_oportunidades.csv`
- Variables: `densidad_establecimientos_f01`, `cantidad_habilitaciones_f02`, `cantidad_ferias_mercados_f03`.
- Fuentes usadas: F01, F02, F03 y eventos F04 aptos.
- Texto sugerido: Elaboracion propia sobre Buenos Aires Data / GCBA y relevamiento manual trazable F04. El mapa separa oferta registrada F01, habilitaciones aprobadas F02, ferias/mercados F03 y eventos F04 aptos. Fecha de consulta: 10/06/2026.
- Limitaciones: geocodificacion pendiente; algunas ubicaciones quedan a nivel texto/barrio/comuna; no sumar F02 como establecimientos activos; no mapear F04 cualitativo como actividad confirmada.
- Lista hoy: si con advertencia metodologica.
