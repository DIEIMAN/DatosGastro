
CREATE OR REPLACE VIEW gastronomia_caba.vw_establecimientos_mapa AS
SELECT e.id_establecimiento, e.nombre, c.categoria_general, c.subcategoria, u.*
FROM gastronomia_caba.fact_establecimiento e
JOIN gastronomia_caba.dim_categoria_gastronomica c USING (id_categoria)
JOIN gastronomia_caba.dim_ubicacion u USING (id_ubicacion);
