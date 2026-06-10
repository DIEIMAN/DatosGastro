-- =====================================================================
-- 03_load_data.sql  (V2 — carga real con \copy)
-- Ejecutar desde psql, parado en la raiz del repo:
--   psql "$DATABASE_URL" -f sql/01_create_schema.sql
--   psql "$DATABASE_URL" -f sql/02_create_tables.sql
--   psql "$DATABASE_URL" -f sql/03_load_data.sql
-- El orden respeta las foreign keys: primero dimensiones, luego hechos, luego puentes.
-- ENCODING UTF8 porque los CSV de data/processed ya estan limpios (ftfy aplicado).
-- =====================================================================
SET search_path TO gastronomia_caba;

-- 1) Dimensiones (sin dependencias)
\copy dim_fuente FROM 'data/processed/dim_fuente.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
\copy dim_ubicacion FROM 'data/processed/dim_ubicacion.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
\copy dim_categoria_gastronomica FROM 'data/processed/dim_categoria_gastronomica.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
\copy dim_organizador FROM 'data/processed/dim_organizador.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');

-- 2) Hechos (dependen de dimensiones)
\copy fact_establecimiento FROM 'data/processed/fact_establecimiento.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
\copy fact_evento_gastronomico FROM 'data/processed/fact_evento_gastronomico.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
\copy fact_programa_politica FROM 'data/processed/fact_programa_politica.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
\copy fact_mercado_feria FROM 'data/processed/fact_mercado_feria.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');

-- 3) Puentes (dependen de hechos) — hoy vacios, quedan listos para poblar
\copy puente_evento_establecimiento FROM 'data/processed/puente_evento_establecimiento.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
\copy puente_programa_establecimiento FROM 'data/processed/puente_programa_establecimiento.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
\copy puente_evento_categoria FROM 'data/processed/puente_evento_categoria.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
