SET search_path TO gastronomia_caba;

CREATE TABLE IF NOT EXISTS dim_fuente (
  id_fuente text PRIMARY KEY,
  nombre_fuente text,
  tipo_fuente text,
  organismo_entidad text,
  url_base text,
  confiabilidad text,
  frecuencia_actualizacion text,
  fecha_consulta text,
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

CREATE TABLE IF NOT EXISTS dim_organizador (
  id_organizador text PRIMARY KEY,
  nombre_organizador text,
  tipo_organizador text,
  sector text,
  web text,
  observaciones text
);

CREATE TABLE IF NOT EXISTS fact_establecimiento (
  id_establecimiento text PRIMARY KEY,
  nombre text,
  id_categoria text REFERENCES dim_categoria_gastronomica(id_categoria),
  id_ubicacion text REFERENCES dim_ubicacion(id_ubicacion),
  id_fuente text REFERENCES dim_fuente(id_fuente),
  url_fuente text,
  fecha_consulta text,
  estado text,
  web text,
  redes text,
  telefono text,
  fecha_alta_detectada text,
  fecha_ultima_actualizacion text,
  calidad_dato text,
  requiere_validacion text,
  motivo_validacion text,
  observaciones text,
  es_gastronomico text,
  categoria_gastronomica_inferida text,
  confianza_categoria text,
  motivo_categoria text,
  origen_dato text,
  estado_datos text,
  anio_fuente text,
  periodo_fuente text
);

CREATE TABLE IF NOT EXISTS fact_habilitacion_gastronomica (
  id_habilitacion text PRIMARY KEY,
  id_fuente text REFERENCES dim_fuente(id_fuente),
  url_fuente text,
  fecha_consulta text,
  periodo_fuente text,
  anio_fuente text,
  fecha_habilitacion text,
  descripcion_rubro_original text,
  descripcion_rubro_normalizada text,
  es_gastronomico text,
  categoria_gastronomica_inferida text,
  confianza_categoria text,
  motivo_categoria text,
  id_ubicacion text REFERENCES dim_ubicacion(id_ubicacion),
  direccion_original text,
  barrio text,
  comuna text,
  superficie text,
  origen_dato text,
  estado_datos text,
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
  anio text,
  periodicidad text,
  id_ubicacion text REFERENCES dim_ubicacion(id_ubicacion),
  ubicacion_original text,
  direccion_original text,
  barrio text,
  comuna text,
  id_organizador text REFERENCES dim_organizador(id_organizador),
  tipo_organizador text,
  id_fuente text REFERENCES dim_fuente(id_fuente),
  url_fuente text,
  fecha_consulta text,
  tipo_evento text,
  categoria_gastronomica text,
  gratuito text,
  requiere_inscripcion text,
  cantidad_asistentes_estimada text,
  cantidad_puestos_estimada text,
  apoyo_gcba text,
  organismo_gcba_relacionado text,
  area_gcba_relacionada text,
  tipo_vinculo_gcba text,
  estado text,
  link_evento text,
  fuente text,
  tipo_fuente text,
  calidad_dato_original text,
  calidad_dato_normalizada text,
  calidad_dato text,
  requiere_validacion text,
  motivo_validacion text,
  apto_dashboard text,
  fecha_completa text,
  limitaciones text,
  observaciones text,
  origen_dato text,
  estado_datos text
);

CREATE TABLE IF NOT EXISTS fact_programa_politica (
  id_programa text PRIMARY KEY,
  nombre_programa text,
  organismo_responsable text,
  area_dependiente text,
  fecha_inicio text,
  fecha_fin text,
  anio_inicio text,
  estado text,
  tipo_programa text,
  descripcion text,
  objetivo text,
  beneficiarios text,
  alcance_geografico text,
  barrios_comunas text,
  normativa_relacionada text,
  presupuesto text,
  resultados text,
  metricas_publicadas text,
  id_fuente text REFERENCES dim_fuente(id_fuente),
  url_fuente text,
  fecha_consulta text,
  link text,
  fuente text,
  tipo_fuente text,
  calidad_dato_original text,
  calidad_dato_normalizada text,
  calidad_dato text,
  requiere_validacion text,
  motivo_validacion text,
  apto_dashboard text,
  vigencia_clara text,
  limitaciones text,
  observaciones text,
  origen_dato text,
  estado_datos text
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
  url_fuente text,
  fecha_consulta text,
  link text,
  calidad_dato text,
  requiere_validacion text,
  motivo_validacion text,
  observaciones text,
  origen_dato text,
  estado_datos text
);

CREATE TABLE IF NOT EXISTS puente_evento_categoria (
  id_evento text REFERENCES fact_evento_gastronomico(id_evento),
  id_categoria text REFERENCES dim_categoria_gastronomica(id_categoria),
  observaciones text
);

CREATE TABLE IF NOT EXISTS puente_evento_establecimiento (
  id_evento text REFERENCES fact_evento_gastronomico(id_evento),
  id_establecimiento text REFERENCES fact_establecimiento(id_establecimiento),
  observaciones text
);

CREATE TABLE IF NOT EXISTS puente_programa_establecimiento (
  id_programa text REFERENCES fact_programa_politica(id_programa),
  id_establecimiento text REFERENCES fact_establecimiento(id_establecimiento),
  observaciones text
);

CREATE TABLE IF NOT EXISTS puente_evento_programa (
  id_evento text REFERENCES fact_evento_gastronomico(id_evento),
  id_programa text REFERENCES fact_programa_politica(id_programa),
  tipo_vinculo text,
  observaciones text
);
