-- Ejecutar desde psql ajustando las rutas locales segun corresponda.
-- Orden de carga compatible con claves foraneas.

SET search_path TO gastronomia_caba;

\copy dim_fuente FROM 'data/processed/dim_fuente.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
\copy dim_ubicacion FROM 'data/processed/dim_ubicacion.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
\copy dim_categoria_gastronomica FROM 'data/processed/dim_categoria_gastronomica.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
\copy dim_organizador FROM 'data/processed/dim_organizador.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');

\copy fact_establecimiento FROM 'data/processed/fact_establecimiento.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
\copy fact_habilitacion_gastronomica FROM 'data/processed/fact_habilitacion_gastronomica.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
\copy fact_evento_gastronomico FROM 'data/processed/fact_evento_gastronomico.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
\copy fact_programa_politica FROM 'data/processed/fact_programa_politica.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
\copy fact_mercado_feria FROM 'data/processed/fact_mercado_feria.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
\copy puente_evento_programa FROM 'data/processed/puente_evento_programa.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');

\copy puente_evento_categoria FROM 'data/processed/puente_evento_categoria.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
\copy puente_evento_establecimiento FROM 'data/processed/puente_evento_establecimiento.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
\copy puente_programa_establecimiento FROM 'data/processed/puente_programa_establecimiento.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
