# QA del plan de mapas callejeros V3 — PolosGastro DGDGAS

Control del documento `PLAN_MAPAS_CALLEJEROS_V3_POLOS_GASTRO.md`. Este QA valida el **plan**, no
una ejecución: en esta sesión no se generaron mapas ni PDF ni se ejecutó API.

## Alcance de esta sesión

- [x] No se ejecutó ninguna API ni llamada Google Places.
- [x] No se generó PDF.
- [x] No se generaron mapas.
- [x] No se tocaron datos fuente (`data/`, pipeline F01–F05, scripts productivos).
- [x] No se borró ningún archivo.
- [x] No se tocaron otros proyectos (Cafecito, Mercados, Casas de Pastas, Design System).
- [x] No hubo commit, push ni staging (`git add` no ejecutado).

## Cobertura del plan (verificación de contenido)

- [x] Diagnóstico visual del V2: mapa global se conserva, detalle esquemático, falta base callejera, menciones se mantienen.
- [x] Objetivo V3: calles/avenidas/referencias, no técnico, institucional, complementa las cajas.
- [x] Mapas a rehacer: Palermo/Las Cañitas, Puerto Madero, San Telmo, Corrientes/Abasto, Belgrano.
- [x] Requisitos cartográficos transversales, incluida la nota "lectura territorial preliminar, no delimitación oficial".
- [x] Requisitos por zona (con las diferenciaciones y menciones pedidas por zona).
- [x] Fuentes posibles con obligación de documentar origen, fecha y licencia; sin scraping.
- [x] Criterios para PDF V3: 18 páginas, mapa global intacto, reemplazo de páginas 7–11, cajas mantenidas, pie DGDGAS, sin lenguaje técnico.
- [x] Checklist de ejecución para Codex.

## Guardrails reflejados en el plan

- [x] Marca pública **DGDGAS — Dirección General de Gastronomía**; nunca DataGastro como marca pública.
- [x] Instrucción de excluir `place_id`, `rating`, `user_ratings_total`, API key, raw JSON y rutas locales del PDF público.
- [x] Cerrados no como activos; duplicados y queries a corregir fuera de los destacados.
- [x] Corrientes y Abasto diferenciados, con advertencia de no doble conteo.
- [x] Belgrano R como subzona a reforzar, no polo consolidado.
- [x] Mercado de San Telmo y hitos colectivos tratados como tales, no como restaurante puntual.

## Notas para la ejecución (pendientes para Codex)

- Confirmar si existe capa de **calles GCBA** ya descargada en el proyecto. Las capas locales
  halladas (`data/raw/geo_barrios.geojson`, `data/raw/geo_comunas.geojson`) son **polígonos de
  barrio/comuna, sin calles**: sirven como marco, no como base callejera.
- Si se recurre a OSM, dejar atribución y licencia ODbL registradas en el anexo cartográfico.
- Los checks de campos sensibles y términos prohibidos del plan deben re-ejecutarse **sobre el PDF
  V3 real** una vez generado; este QA no los reemplaza.
