# Fuentes insuficientes para capa objetiva barrial

Fecha de consulta: 2026-07-01.

La Fase 8 fuerte pudo construir oferta gastronomica por barrio a partir de F01, pero no una tabla
confiable de habilitaciones gastronomicas por barrio.

## Caso principal

- Fuente evaluada: `data/processed/fact_habilitacion_gastronomica.csv` junto con
  `data/processed/dim_ubicacion.csv`.
- Registros de habilitaciones leidos: 44169.
- Registros con barrio no determinado o no util para lectura barrial: 44099.

## Decision

No se crea `habilitaciones_gastronomicas_por_barrio_fase8_fuerte.csv` porque podria sugerir una
precision territorial que la fuente procesada no sostiene. La lectura de F02 queda limitada a
comuna.

## Impacto

- El indice por barrio usa solo F01.
- El indice por comuna combina F01 y F02.
- Los cruces de polos de tipo corredor, subpolo o area de revision siguen requiriendo delimitacion
  humana antes de cualquier comparacion cuantitativa fina.
