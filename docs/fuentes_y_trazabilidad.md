# Fuentes y trazabilidad

El proyecto separa pagina portal, URL directa de descarga y datos efectivamente disponibles.

## Fuentes principales

| id | fuente | tabla processed | lectura correcta |
| --- | --- | --- | --- |
| F01 | Oferta y Establecimientos Gastronomicos | `fact_establecimiento.csv` | Oferta/establecimientos gastronomicos registrados |
| F02 | Habilitaciones Aprobadas AGC | `fact_habilitacion_gastronomica.csv` | Habilitaciones aprobadas inferidas como gastronomicas |
| F03 | Ferias y Mercados | `fact_espacio_feria_mercado.csv` / `fact_puesto_feria.csv` | Espacios reales separados de puestos/personas |
| F04 | Eventos gastronomicos semiestructurados | `fact_evento_gastronomico.csv` | Relevamiento manual trazable de eventos/activaciones |
| F05 | Programas y politicas gastronomicas semiestructuradas | `fact_programa_politica.csv` | Catalogo manual trazable de politicas, normativa e instrumentos |

Actualizacion V3: las URLs directas reales quedaron registradas en `src/config.py`.

- F01: CKAN + CDN alternativo.
- F02: recursos 2015-2018 y anuales 2019-2025. F02 2026 no esta publicado y no se exige.
- F03: CSV combinado, CSV ferias, CSV mercados y GeoJSON FIAB. El CSV combinado es padron de puestos/personas; el GeoJSON es solo FIAB.
- F04: CSV manual trazable con fuente por fila. No es dataset oficial estructurado.
- F05: CSV manual trazable con fuente por fila. No es dataset oficial estructurado ni serie temporal de impacto.

Las URLs portal se conservan en `data/raw/raw_fuentes_relevadas.csv` y en `src/config.py`. No se usan como descarga automatica si no apuntan a un archivo directo.

## Separacion conceptual

F02 no es un padron vivo de establecimientos activos. Es un registro de habilitaciones aprobadas, por eso vive en `fact_habilitacion_gastronomica.csv` y no en `fact_establecimiento.csv`.

Regla de comunicacion:

- No mostrar "40.295 establecimientos gastronomicos" ni ningun total combinado F01+F02 como establecimientos.
- Mostrar "2.823 registros en Oferta Gastronomica F01".
- Mostrar "44.169 habilitaciones gastronomicas inferidas desde AGC F02".
- Mostrar "220 espacios reales F03: mercados, ferias especializadas y FIAB".
- No mostrar puestos/personas F03 como cantidad de ferias o mercados.
- No usar F02 2025 como flujo anual comparable: el recurso tiene esquema distinto y contiene disposiciones de varios anios. La serie comparable excluye 2025 y el periodo agregado 2015-2018.

F03 contiene recursos con distintos niveles de grano. Los puestos individuales no deben interpretarse como ferias o mercados. Los indicadores principales usan espacios reales; los registros de puestos, si se conservan, quedan solo como insumo tecnico y no se exponen en dashboard.

Cada metrica debe incluir fuente, URL, fecha de consulta, metodologia y limitaciones.

## F04/F05 semiestructurados

F04 y F05 no provienen de datasets oficiales estructurados. Son relevamientos manuales trazables. No representan el universo completo de eventos ni programas gastronomicos de CABA. Las metricas fuertes solo consideran filas con `apto_dashboard = si`.

Las filas con fechas incompletas, fuentes privadas sin vinculo confirmado, montos desactualizados o validaciones pendientes se conservan como insumo cualitativo y no deben usarse para indicadores fuertes.

- F04 apto fuerte: `apto_dashboard = si`, `requiere_validacion = no`, fecha completa y vinculo GCBA no ambiguo.
- F05 apto dashboard: fichas/catalogo con `apto_dashboard = si` y vigencia clara; no usar como serie temporal de impacto.

## Campos de trazabilidad

Las tablas de hechos deben conservar, cuando corresponde:

- `id_fuente`
- `url_fuente`
- `fecha_ultima_actualizacion` o fecha equivalente
- `calidad_dato`
- `requiere_validacion`
- `motivo_validacion`
- `origen_dato`

## Contratos de carga

La carga desde `data/raw/` usa contratos flexibles definidos en `src/source_contracts.py`. `data/raw/` debe contener solo datos reales. Los seeds/manuales viven en `data/seeds/` y son fallback de desarrollo.

Cada corrida de `python src/build_model.py` genera:

- `outputs/tablas_resumen/contratos_fuentes.csv`
- `docs/contratos_fuentes.md`

Estos archivos indican:

- archivo usado para F01/F02/F03,
- si fue seed o fuente real,
- columnas mapeadas al contrato canonico,
- columnas requeridas faltantes,
- columnas extra ignoradas por el modelo.

## Estado de datos

- `datos seed`: datos manuales o muestra inicial.
- `datos reales parciales`: hay al menos una fuente real cargada, pero no cubre todo el universo.
- `datos reales completos`: las fuentes reales esperadas estan cargadas y validadas.
- `datos pendientes de validacion`: no hay evidencia suficiente para clasificar.

## Reglas dashboard

- Si `estado_datos = datos seed`, entonces `apto_dashboard = no`.
- Si hay mezcla de datos reales y seed, entonces `apto_dashboard = no` hasta validar cobertura.
- Si faltan `fuentes_utilizadas` o `urls_fuentes`, entonces no se debe publicar como dashboard real.
- Si una analytics llama "establecimientos" a F02, no debe publicarse.
- El modo `--strict-real` debe fallar ante cualquiera de esos casos.

## Regla de prioridad

Ante conflicto entre fuentes, priorizar:

1. BA Data / GCBA con recurso directo.
2. Boletin Oficial o normativa oficial.
3. Web oficial GCBA.
4. Camaras sectoriales.
5. Prensa o fuentes privadas, siempre marcadas para validacion.
