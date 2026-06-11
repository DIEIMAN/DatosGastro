# Diccionario de datos

Ver tablas en `data/raw`, `data/processed` y `data/analytics`. Campos de calidad obligatorios: `calidad_dato`, `requiere_validacion`, `motivo_validacion`, `fecha_consulta` o `fecha_extraccion`.

## Tablas nucleo

- `dim_fuente`: catalogo de fuentes.
- `dim_ubicacion`: direcciones normalizadas y geocodificacion.
- `dim_categoria_gastronomica`: taxonomia de rubros.
- `dim_organizador`: organizadores de eventos/programas.
- `fact_establecimiento`: oferta/establecimientos gastronomicos registrados desde F01. No incluye F02.
- `fact_habilitacion_gastronomica`: habilitaciones aprobadas AGC F02 inferidas como gastronomicas por rubro. No representa establecimientos activos unicos.
- `fact_evento_gastronomico`: eventos y ediciones desde F04, relevamiento manual trazable.
- `fact_programa_politica`: programas, politicas, normativa e instrumentos desde F05, catalogo manual trazable.
- `fact_mercado_feria`: ferias, mercados y patios desde F03.
- `puente_evento_programa`: vinculos explicitos entre eventos F04 y programas/instrumentos F05.

## Regla conceptual F01/F02/F03

- F01 alimenta `fact_establecimiento.csv` y debe nombrarse como oferta gastronomica registrada.
- F02 alimenta `fact_habilitacion_gastronomica.csv` y debe nombrarse como habilitaciones gastronomicas aprobadas o inferidas desde AGC.
- F03 alimenta `fact_mercado_feria.csv` y debe nombrarse como ferias/mercados.
- F04 alimenta `fact_evento_gastronomico.csv` y debe nombrarse como eventos/activaciones relevados manualmente con trazabilidad.
- F05 alimenta `fact_programa_politica.csv` y debe nombrarse como catalogo de programas, politicas, normativa e instrumentos.
- No sumar F01 y F02 como "establecimientos gastronomicos".

## F04/F05

F04 y F05 no son datasets oficiales estructurados. Son relevamientos manuales trazables, con fuente por fila, y no representan el universo completo de eventos ni programas gastronomicos de CABA.

Campos clave de F04:

- `tipo_vinculo_gcba`
- `apto_dashboard`
- `fecha_completa`
- `calidad_dato_original`
- `calidad_dato_normalizada`
- `limitaciones`

Campos clave de F05:

- `tipo_programa`
- `estado`
- `apto_dashboard`
- `vigencia_clara`
- `presupuesto`
- `metricas_publicadas`
- `limitaciones`

## `fact_habilitacion_gastronomica.csv`

Campos minimos:

- `id_habilitacion`
- `id_fuente`
- `url_fuente`
- `fecha_consulta`
- `periodo_fuente`
- `anio_fuente`
- `fecha_habilitacion`
- `descripcion_rubro_original`
- `descripcion_rubro_normalizada`
- `es_gastronomico`
- `categoria_gastronomica_inferida`
- `confianza_categoria`
- `motivo_categoria`
- `id_ubicacion`
- `direccion_original`
- `barrio`
- `comuna`
- `superficie`
- `origen_dato`
- `estado_datos`
- `calidad_dato`
- `requiere_validacion`
- `motivo_validacion`
- `observaciones`

## Analytics de habilitaciones

- `analytics_habilitaciones_por_anio.csv`
- `analytics_habilitaciones_por_barrio.csv`
- `analytics_habilitaciones_por_categoria.csv`
- `analytics_habilitaciones_recientes.csv`

Cada analytics conserva fuente, URL, fecha de consulta, metodologia, limitaciones y `apto_dashboard`.
