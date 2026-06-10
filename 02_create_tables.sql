-- =====================================================================
-- 02_create_tables.sql  (V2 — DDL completo)
-- Modelo estrella del Ecosistema Gastronomico de CABA.
-- Cambios respecto de V1:
--   * Se agregan las 7 tablas que faltaban (dim_organizador, fact_evento,
--     fact_programa, fact_mercado_feria y los 3 puentes).
--   * Se agregan FKs de fact_evento a dim_ubicacion / dim_organizador.
-- Todas las columnas siguen exactamente los headers de los CSV en data/processed.
-- =====================================================================
SET search_path TO gastronomia_caba;

-- ------------------------- DIMENSIONES -------------------------------
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
  comuna text,   -- text: admite "No determinada" del centinela; validar a smallint al cargar padron real
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

CREATE TABLE IF NOT EXISTS dim_organizador (
  id_organizador text PRIMARY KEY,
  nombre_organizador text,
  tipo_organizador text,
  sector text,
  web text,
  observaciones text
);

-- --------------------------- HECHOS ----------------------------------
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

CREATE TABLE IF NOT EXISTS fact_evento_gastronomico (
  id_evento text PRIMARY KEY,
  nombre_evento text,
  descripcion text,
  fecha_inicio text,
  fecha_fin text,
  periodicidad text,
  id_ubicacion text REFERENCES dim_ubicacion(id_ubicacion),
  id_organizador text REFERENCES dim_organizador(id_organizador),
  id_fuente text REFERENCES dim_fuente(id_fuente),
  tipo_evento text,
  gratuito text,
  requiere_inscripcion text,
  cantidad_asistentes_estimada text,
  cantidad_puestos_estimada text,
  estado text,
  link_evento text,
  calidad_dato text,
  requiere_validacion text,
  motivo_validacion text,
  observaciones text
);

CREATE TABLE IF NOT EXISTS fact_programa_politica (
  id_programa text PRIMARY KEY,
  nombre_programa text,
  organismo_responsable text,
  fecha_inicio text,
  fecha_fin text,
  estado text,
  tipo_programa text,
  objetivo text,
  beneficiarios text,
  alcance_geografico text,
  resultados text,
  metricas_publicadas text,
  id_fuente text REFERENCES dim_fuente(id_fuente),
  link text,
  calidad_dato text,
  requiere_validacion text,
  motivo_validacion text,
  observaciones text
);

CREATE TABLE IF NOT EXISTS fact_mercado_feria (
  id_mercado_feria text PRIMARY KEY,
  nombre text,
  tipo_espacio text,
  id_ubicacion text REFERENCES dim_ubicacion(id_ubicacion),
  gestion text,
  dias_funcionamiento text,
  horarios text,
  cantidad_puestos text,
  rubros text,
  estado text,
  id_fuente text REFERENCES dim_fuente(id_fuente),
  link text,
  calidad_dato text,
  requiere_validacion text,
  motivo_validacion text,
  observaciones text
);

-- --------------------------- PUENTES ---------------------------------
CREATE TABLE IF NOT EXISTS puente_evento_establecimiento (
  id_evento text REFERENCES fact_evento_gastronomico(id_evento),
  id_establecimiento text REFERENCES fact_establecimiento(id_establecimiento),
  rol text,
  observaciones text,
  PRIMARY KEY (id_evento, id_establecimiento)
);

CREATE TABLE IF NOT EXISTS puente_programa_establecimiento (
  id_programa text REFERENCES fact_programa_politica(id_programa),
  id_establecimiento text REFERENCES fact_establecimiento(id_establecimiento),
  tipo_beneficio text,
  fecha_participacion text,
  observaciones text,
  PRIMARY KEY (id_programa, id_establecimiento)
);

CREATE TABLE IF NOT EXISTS puente_evento_categoria (
  id_evento text REFERENCES fact_evento_gastronomico(id_evento),
  id_categoria text REFERENCES dim_categoria_gastronomica(id_categoria),
  observaciones text,
  PRIMARY KEY (id_evento, id_categoria)
);
