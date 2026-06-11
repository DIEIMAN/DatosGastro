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

-- Habilitaciones gastronomicas por anio/periodo F02.
SELECT
  anio_fuente,
  periodo_fuente,
  categoria_gastronomica_inferida,
  COUNT(*) AS cantidad_habilitaciones
FROM fact_habilitacion_gastronomica
GROUP BY 1, 2, 3
ORDER BY cantidad_habilitaciones DESC;

-- Registros que requieren validacion.
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
WHERE requiere_validacion = 'si';

-- Eventos sin ubicacion determinada.
SELECT id_evento, nombre_evento, fecha_inicio, motivo_validacion
FROM fact_evento_gastronomico
WHERE id_ubicacion = 'U00000';

-- Eventos F04 aptos por tipo: solo metricas fuertes.
SELECT tipo_evento, COUNT(*) AS cantidad_eventos
FROM fact_evento_gastronomico
WHERE id_fuente = 'F04'
  AND apto_dashboard = 'si'
  AND requiere_validacion <> 'si'
  AND fecha_completa = 'si'
  AND tipo_vinculo_gcba !~* 'Difusion oficial|Requiere validacion'
GROUP BY tipo_evento
ORDER BY cantidad_eventos DESC;

-- Eventos F04 cualitativos: conservados, pero fuera de metricas fuertes.
SELECT id_evento, nombre_evento, fecha_inicio, tipo_vinculo_gcba, apto_dashboard, motivo_validacion
FROM fact_evento_gastronomico
WHERE id_fuente = 'F04'
  AND (
    apto_dashboard <> 'si'
    OR requiere_validacion = 'si'
    OR fecha_completa <> 'si'
    OR tipo_vinculo_gcba ~* 'Difusion oficial|Requiere validacion'
  );

-- Programas F05 aptos por tipo: catalogo, no serie temporal de impacto.
SELECT tipo_programa, COUNT(*) AS cantidad_programas
FROM fact_programa_politica
WHERE id_fuente = 'F05'
  AND apto_dashboard = 'si'
  AND vigencia_clara = 'si'
GROUP BY tipo_programa
ORDER BY cantidad_programas DESC;

-- Programas F05 cualitativos: antecedentes, instrumentos puntuales o validacion pendiente.
SELECT id_programa, nombre_programa, tipo_programa, estado, apto_dashboard, motivo_validacion
FROM fact_programa_politica
WHERE id_fuente = 'F05'
  AND (apto_dashboard <> 'si' OR vigencia_clara <> 'si');

-- Cobertura de fuentes por tabla de hechos.
SELECT id_fuente, COUNT(*) AS registros, 'establecimientos' AS tabla
FROM fact_establecimiento
GROUP BY id_fuente
UNION ALL
SELECT id_fuente, COUNT(*) AS registros, 'habilitaciones_gastronomicas' AS tabla
FROM fact_habilitacion_gastronomica
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
