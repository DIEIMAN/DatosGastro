
SET search_path TO gastronomia_caba;
CREATE TABLE IF NOT EXISTS dim_fuente (
  id_fuente text PRIMARY KEY,
  nombre_fuente text,
  tipo_fuente text,
  organismo_entidad text,
  url_base text,
  confiabilidad text,
  frecuencia_actualizacion text,
  fecha_consulta date,
  notas text
);
CREATE TABLE IF NOT EXISTS dim_ubicacion (
  id_ubicacion text PRIMARY KEY,
  direccion_original text,
  direccion_normalizada text,
  barrio text,
  comuna text,
  latitud text,
  longitud text,
  codigo_postal text,
  zona text,
  calidad_geo text,
  requiere_validacion text,
  motivo_validacion text
);
CREATE TABLE IF NOT EXISTS dim_categoria_gastronomica (
  id_categoria text PRIMARY KEY,
  categoria_general text,
  subcategoria text,
  descripcion text,
  ejemplos text
);
CREATE TABLE IF NOT EXISTS fact_establecimiento (
  id_establecimiento text PRIMARY KEY,
  nombre text,
  id_categoria text REFERENCES dim_categoria_gastronomica(id_categoria),
  id_ubicacion text REFERENCES dim_ubicacion(id_ubicacion),
  id_fuente text REFERENCES dim_fuente(id_fuente),
  estado text,
  web text,
  redes text,
  telefono text,
  fecha_alta_detectada text,
  fecha_ultima_actualizacion text,
  calidad_dato text,
  requiere_validacion text,
  motivo_validacion text,
  observaciones text
);
