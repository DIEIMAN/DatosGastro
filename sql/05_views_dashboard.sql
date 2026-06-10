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
  ev.tipo_evento,
  org.nombre_organizador,
  u.barrio,
  u.comuna,
  ev.calidad_dato,
  ev.requiere_validacion,
  ev.origen_dato
FROM fact_evento_gastronomico ev
JOIN dim_organizador org ON org.id_organizador = ev.id_organizador
JOIN dim_ubicacion u ON u.id_ubicacion = ev.id_ubicacion;

CREATE OR REPLACE VIEW vw_validaciones_pendientes AS
SELECT 'establecimiento' AS tipo, id_establecimiento AS id, nombre, motivo_validacion
FROM fact_establecimiento
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
  COUNT(DISTINCT e.id_establecimiento) AS establecimientos,
  COUNT(DISTINCT ev.id_evento) AS eventos,
  COUNT(DISTINCT mf.id_mercado_feria) AS mercados_ferias
FROM dim_ubicacion u
LEFT JOIN fact_establecimiento e ON e.id_ubicacion = u.id_ubicacion
LEFT JOIN fact_evento_gastronomico ev ON ev.id_ubicacion = u.id_ubicacion
LEFT JOIN fact_mercado_feria mf ON mf.id_ubicacion = u.id_ubicacion
GROUP BY u.barrio, u.comuna;
