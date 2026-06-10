
-- Establecimientos por barrio y categoría
SELECT u.barrio, u.comuna, c.categoria_general, c.subcategoria, COUNT(*) AS cantidad
FROM gastronomia_caba.fact_establecimiento e
JOIN gastronomia_caba.dim_ubicacion u USING (id_ubicacion)
JOIN gastronomia_caba.dim_categoria_gastronomica c USING (id_categoria)
GROUP BY 1,2,3,4
ORDER BY cantidad DESC;

-- Registros que requieren validación
SELECT id_establecimiento, nombre, motivo_validacion
FROM gastronomia_caba.fact_establecimiento
WHERE requiere_validacion = 'sí';
