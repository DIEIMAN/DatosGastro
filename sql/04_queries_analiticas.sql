SET search_path TO gastronomia_caba;

-- Establecimientos por barrio y categoria.
SELECT
  u.barrio,
  u.comuna,
  c.categoria_general,
  c.subcategoria,
  COUNT(*) AS cantidad_establecimientos,
  MAX(e.origen_dato) AS estado_datos
FROM fact_establecimiento e
JOIN dim_ubicacion u ON u.id_ubicacion = e.id_ubicacion
JOIN dim_categoria_gastronomica c ON c.id_categoria = e.id_categoria
GROUP BY 1, 2, 3, 4
ORDER BY cantidad_establecimientos DESC;

-- Registros que requieren validacion.
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
WHERE requiere_validacion = 'si';

-- Eventos sin ubicacion determinada.
SELECT id_evento, nombre_evento, fecha_inicio, motivo_validacion
FROM fact_evento_gastronomico
WHERE id_ubicacion = 'U00000';

-- Cobertura de fuentes por tabla de hechos.
SELECT id_fuente, COUNT(*) AS registros, 'establecimientos' AS tabla
FROM fact_establecimiento
GROUP BY id_fuente
UNION ALL
SELECT id_fuente, COUNT(*) AS registros, 'eventos' AS tabla
FROM fact_evento_gastronomico
GROUP BY id_fuente
UNION ALL
SELECT id_fuente, COUNT(*) AS registros, 'programas' AS tabla
FROM fact_programa_politica
GROUP BY id_fuente
UNION ALL
SELECT id_fuente, COUNT(*) AS registros, 'mercados_ferias' AS tabla
FROM fact_mercado_feria
GROUP BY id_fuente;
