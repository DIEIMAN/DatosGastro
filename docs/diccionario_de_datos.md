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
- `fact_espacio_feria_mercado`: espacios reales F03, con grano 1 fila = 1 mercado, feria especializada o punto FIAB.
- `fact_puesto_feria`: padron tecnico F03, con grano 1 fila = 1 puesto/persona anonimizada. No apto para dashboard.
- `fact_mercado_feria`: alias de compatibilidad de espacios F03; no debe usarse para contar puestos.
- `puente_evento_programa`: vinculos explicitos entre eventos F04 y programas/instrumentos F05.

## Regla conceptual F01/F02/F03

- F01 alimenta `fact_establecimiento.csv` y debe nombrarse como oferta gastronomica registrada.
- F02 alimenta `fact_habilitacion_gastronomica.csv` y debe nombrarse como habilitaciones gastronomicas aprobadas o inferidas desde AGC.
- F03 alimenta `fact_espacio_feria_mercado.csv` para indicadores principales de espacios. `fact_puesto_feria.csv` queda solo como insumo tecnico.
- F04 alimenta `fact_evento_gastronomico.csv` y debe nombrarse como eventos/activaciones relevados manualmente con trazabilidad.
- F05 alimenta `fact_programa_politica.csv` y debe nombrarse como catalogo de programas, politicas, normativa e instrumentos.
- No sumar F01 y F02 como "establecimientos gastronomicos".
- F03 contiene recursos con distintos niveles de grano. Los puestos individuales no deben interpretarse como ferias o mercados. Los indicadores principales usan espacios reales; los registros de puestos, si se conservan, quedan solo como insumo tecnico y no se exponen en dashboard.

## `fact_espacio_feria_mercado.csv`

Campos minimos: `id_espacio`, `id_fuente`, `tipo_espacio`, `nombre`, `descripcion`, `direccion`, `barrio`, `comuna`, `latitud`, `longitud`, `calidad_geo`, `dias_funcionamiento`, `horarios`, `productos`, `url_fuente`, `fecha_consulta`, `origen_dato`, `estado_datos`, `calidad_dato`, `requiere_validacion`, `motivo_validacion`, `limitaciones`, `observaciones`.

Grano: 1 fila = 1 espacio real. Incluye mercados, ferias especializadas y FIAB cuando existe GeoJSON.

## `fact_puesto_feria.csv`

Grano: 1 fila = 1 puesto/persona del padron F03. No conserva nombres ni apellidos en processed; usa `persona_hash`, `apto_dashboard = no` y `uso = auditoria_interna`.

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

`analytics_habilitaciones_por_anio.csv` incluye `nota_serie` y `comparable_como_flujo_anual`. El valor `no` aplica al periodo agregado 2015-2018 y al recurso 2025, porque 2025 tiene esquema distinto y contiene disposiciones de varios anios.

Cada analytics conserva fuente, URL, fecha de consulta, metodologia, limitaciones y `apto_dashboard`.
