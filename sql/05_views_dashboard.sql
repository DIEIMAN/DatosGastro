SET search_path TO gastronomia_caba;

CREATE OR REPLACE VIEW vw_establecimientos_mapa AS
SELECT
  e.id_establecimiento,
  e.nombre,
  c.categoria_general,
  c.subcategoria,
  e.es_gastronomico,
  e.confianza_categoria,
  u.id_ubicacion,
  u.direccion_normalizada,
  u.barrio,
  u.comuna,
  u.latitud,
  u.longitud,
  e.calidad_dato,
  e.requiere_validacion,
  e.origen_dato
FROM fact_establecimiento e
JOIN dim_categoria_gastronomica c ON c.id_categoria = e.id_categoria
JOIN dim_ubicacion u ON u.id_ubicacion = e.id_ubicacion;

CREATE OR REPLACE VIEW vw_eventos_dashboard AS
SELECT
  ev.id_evento,
  ev.nombre_evento,
  ev.fecha_inicio,
  ev.fecha_fin,
  ev.tipo_evento,
  ev.tipo_vinculo_gcba,
  org.nombre_organizador,
  u.barrio,
  u.comuna,
  ev.apto_dashboard,
  ev.calidad_dato,
  ev.requiere_validacion,
  ev.origen_dato
FROM fact_evento_gastronomico ev
JOIN dim_organizador org ON org.id_organizador = ev.id_organizador
JOIN dim_ubicacion u ON u.id_ubicacion = ev.id_ubicacion
WHERE ev.id_fuente = 'F04'
  AND ev.apto_dashboard = 'si'
  AND ev.requiere_validacion <> 'si'
  AND ev.fecha_completa = 'si'
  AND ev.tipo_vinculo_gcba !~* 'Difusion oficial|Requiere validacion';

CREATE OR REPLACE VIEW vw_eventos_cualitativos AS
SELECT
  ev.id_evento,
  ev.nombre_evento,
  ev.fecha_inicio,
  ev.fecha_fin,
  ev.tipo_evento,
  ev.tipo_vinculo_gcba,
  ev.apto_dashboard,
  ev.requiere_validacion,
  ev.motivo_validacion,
  ev.limitaciones,
  ev.url_fuente
FROM fact_evento_gastronomico ev
WHERE ev.id_fuente = 'F04'
  AND (
    ev.apto_dashboard <> 'si'
    OR ev.requiere_validacion = 'si'
    OR ev.fecha_completa <> 'si'
    OR ev.tipo_vinculo_gcba ~* 'Difusion oficial|Requiere validacion'
  );

CREATE OR REPLACE VIEW vw_programas_catalogo AS
SELECT
  p.id_programa,
  p.nombre_programa,
  p.tipo_programa,
  p.estado,
  p.organismo_responsable,
  p.objetivo,
  p.beneficiarios,
  p.normativa_relacionada,
  p.apto_dashboard,
  p.limitaciones,
  p.url_fuente
FROM fact_programa_politica p
WHERE p.id_fuente = 'F05'
  AND p.apto_dashboard = 'si'
  AND p.vigencia_clara = 'si';

CREATE OR REPLACE VIEW vw_habilitaciones_dashboard AS
SELECT
  h.id_habilitacion,
  h.fecha_habilitacion,
  h.anio_fuente,
  h.periodo_fuente,
  h.descripcion_rubro_original,
  h.categoria_gastronomica_inferida,
  h.confianza_categoria,
  h.id_ubicacion,
  h.direccion_original,
  h.barrio,
  h.comuna,
  h.superficie,
  h.calidad_dato,
  h.requiere_validacion,
  h.origen_dato,
  h.estado_datos
FROM fact_habilitacion_gastronomica h;

CREATE OR REPLACE VIEW vw_validaciones_pendientes AS
SELECT 'establecimiento' AS tipo, id_establecimiento AS id, nombre, motivo_validacion
FROM fact_establecimiento
WHERE requiere_validacion = 'si'
UNION ALL
SELECT 'habilitacion_gastronomica' AS tipo, id_habilitacion AS id, descripcion_rubro_original AS nombre, motivo_validacion
FROM fact_habilitacion_gastronomica
WHERE requiere_validacion = 'si'
UNION ALL
SELECT 'evento' AS tipo, id_evento AS id, nombre_evento AS nombre, motivo_validacion
FROM fact_evento_gastronomico
WHERE requiere_validacion = 'si'
UNION ALL
SELECT 'mercado_feria' AS tipo, id_mercado_feria AS id, nombre, motivo_validacion
FROM fact_mercado_feria
WHERE requiere_validacion = 'si'
UNION ALL
SELECT 'programa' AS tipo, id_programa AS id, nombre_programa AS nombre, motivo_validacion
FROM fact_programa_politica
WHERE requiere_validacion = 'si';

CREATE OR REPLACE VIEW vw_resumen_barrio AS
SELECT
  u.barrio,
  u.comuna,
  COUNT(DISTINCT e.id_establecimiento) AS establecimientos_oferta_f01,
  COUNT(DISTINCT h.id_habilitacion) AS habilitaciones_f02,
  COUNT(DISTINCT ev.id_evento) AS eventos,
  COUNT(DISTINCT mf.id_mercado_feria) AS ferias_mercados_f03
FROM dim_ubicacion u
LEFT JOIN fact_establecimiento e ON e.id_ubicacion = u.id_ubicacion
LEFT JOIN fact_habilitacion_gastronomica h ON h.id_ubicacion = u.id_ubicacion
LEFT JOIN fact_evento_gastronomico ev ON ev.id_ubicacion = u.id_ubicacion
  AND ev.id_fuente = 'F04'
  AND ev.apto_dashboard = 'si'
  AND ev.requiere_validacion <> 'si'
  AND ev.fecha_completa = 'si'
  AND ev.tipo_vinculo_gcba !~* 'Difusion oficial|Requiere validacion'
LEFT JOIN fact_mercado_feria mf ON mf.id_ubicacion = u.id_ubicacion
GROUP BY u.barrio, u.comuna;
