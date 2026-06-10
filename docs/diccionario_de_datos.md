# Diccionario de datos

Ver tablas en `data/raw`, `data/processed` y `data/analytics`. Campos de calidad obligatorios: `calidad_dato`, `requiere_validacion`, `motivo_validacion`, `fecha_consulta` o `fecha_extraccion`.

## Tablas núcleo

- `dim_fuente`: catálogo de fuentes.
- `dim_ubicacion`: direcciones normalizadas y geocodificación.
- `dim_categoria_gastronomica`: taxonomía de rubros.
- `fact_establecimiento`: locales gastronómicos.
- `fact_evento_gastronomico`: eventos y ediciones.
- `fact_programa_politica`: programas, políticas e iniciativas.
- `fact_mercado_feria`: ferias, mercados y patios.
