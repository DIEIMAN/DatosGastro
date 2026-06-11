# Diccionario de datos

Ver tablas en `data/raw`, `data/processed` y `data/analytics`. Campos de calidad obligatorios: `calidad_dato`, `requiere_validacion`, `motivo_validacion`, `fecha_consulta` o `fecha_extraccion`.

## Tablas nucleo

- `dim_fuente`: catalogo de fuentes.
- `dim_ubicacion`: direcciones normalizadas y geocodificacion.
- `dim_categoria_gastronomica`: taxonomia de rubros.
- `dim_organizador`: organizadores de eventos/programas.
- `fact_establecimiento`: oferta/establecimientos gastronomicos registrados desde F01. No incluye F02.
- `fact_habilitacion_gastronomica`: habilitaciones aprobadas AGC F02 inferidas como gastronomicas por rubro. No representa establecimientos activos unicos.
- `fact_evento_gastronomico`: eventos y ediciones.
- `fact_programa_politica`: programas, politicas e iniciativas.
- `fact_mercado_feria`: ferias, mercados y patios desde F03.

## Regla conceptual F01/F02/F03

- F01 alimenta `fact_establecimiento.csv` y debe nombrarse como oferta gastronomica registrada.
- F02 alimenta `fact_habilitacion_gastronomica.csv` y debe nombrarse como habilitaciones gastronomicas aprobadas o inferidas desde AGC.
- F03 alimenta `fact_mercado_feria.csv` y debe nombrarse como ferias/mercados.
- No sumar F01 y F02 como "establecimientos gastronomicos".

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
