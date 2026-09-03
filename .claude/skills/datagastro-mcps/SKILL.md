---
name: datagastro-mcps
description: Qué MCP usar para cada pregunta de datos en DataGastro (ckan/BA Data, openstreetmap, duckdb, tavily, playwright, apify) y en qué orden frente a las fuentes propias (USIG, F01–F05, fuentes_externas). Usar al investigar, verificar o cruzar datos de CABA con herramientas externas, antes de elegir el MCP.
---

# MCPs en DataGastro: cuál, cuándo, en qué orden

Los MCPs son de nivel usuario (`~/.claude.json`): `ckan`, `openstreetmap`, `duckdb`, `tavily`,
`playwright`, más el plugin `apify`. `claude-design` falla la conexión y no se usa. Google Maps
Grounding y Brave Search **no están configurados**: no asumirlos.

## Orden frente a lo que ya tiene el repo

1. **Primero lo propio.** Padrón y oferta: `scripts/shared/fuentes_locales` (F01/F02). Direcciones:
   `src/geocode_usig.py` (USIG es el normalizador canónico de CABA, con cache y 11 tests).
   Fuentes abiertas ya descargadas: `data/fuentes_externas/` (RUS, censo, OSM, Overture, ATP,
   Wikidata) con sus bajadores.
2. **`ckan`** para descubrir o refrescar un dataset del GCBA (`data.buenosaires.gob.ar`): buscar,
   leer metadatos y recursos antes de bajar nada. Toda fuente nueva se clasifica F/I/E y se ficha
   (`datagastro-metodologia-fuentes`).
3. **`openstreetmap`** para contraste territorial abierto: POIs (`amenity=restaurant|cafe|bar|
   fast_food…`), polígonos, reverse geocoding. Un POI de OSM es "registro en OSM", no local
   activo; cobertura despareja por zona; Nominatim 1 req/s; atribución ODbL. Para consultas masivas
   usar `osmnx` o los bajadores de `data/fuentes_externas/osm/`, no el MCP en bucle.
4. **`duckdb`** para cruzar, agregar o perfilar CSV/Parquet/GeoJSON grandes en SQL en vez de
   cargar filas al contexto. Solo lectura sobre `data/processed` y `data/analytics`.
5. **`tavily`** para prensa, webs de locales y descubrimiento documental (vigencia de hitos,
   fuentes con nombre). Guardar URL y fecha de consulta; distinguir evidencia de inferencia.
6. **`playwright`** solo como fallback para páginas dinámicas que `tavily`/`crawl4ai` no leen, y
   **`apify`** solo con razón concreta y sin consumir créditos pagos sin presupuesto explícito.
   Ambos bajo el guardrail 6: autorización por tarea, alcance acotado, salida interna, sin eludir
   login, CAPTCHA ni paywall.

## Reglas

- La herramienta mínima que responde; no cinco fuentes si una autoritativa alcanza.
- Cada dato externo queda con fuente, consulta o URL y fecha. Lo no encontrado se declara no
  encontrado.
- Places, OSM, delivery y prensa son universos distintos del padrón; no se mezclan como
  equivalentes ni convierten habilitaciones en locales activos (guardrails 3 y 5).
- Salidas con nombres o direcciones individuales de terceros van a `outputs/analisis_interno/`
  (guardrail 8). Nada entra al Atlas ni al pipeline sin revisión humana.
- Si un MCP falla la conexión, decirlo; no simular su resultado.
