---
name: datagastro-recoleccion-polos
description: Integrar y ejecutar herramientas de recolección web autorizada, extracción estructurada, OSM, SQL local, memoria vectorial, desduplicación, clustering y mapas para Polos Gastronómicos. Usar cuando una tarea de DataGastro mencione Crawl4AI, ScrapeGraph-AI, Browser-Use, OSMnx, ChromaDB, Dedupe, DuckDB, Folium, HDBSCAN, scikit-learn o preparación de evidencia territorial externa.
---

# Recolección y análisis de Polos

Aplicar primero `datagastro-guardrails`, `datagastro-fuentes-externas`,
`datagastro-geodatos` y, si habrá resultados reportables, el método experimental del proyecto.

## Límites duros

- Se permite relevar plataformas externas y privadas como evidencia auxiliar cuando la tarea
  esté autorizada, el alcance sea acotado y la salida quede fuera del Atlas y del pipeline hasta
  revisión humana. No eludir login, CAPTCHA, paywall ni controles de acceso.
- Usar Browser-Use y Crawl4AI únicamente sobre hosts declarados expresamente con `--allow-host`.
  No reutilizar cookies, perfiles o credenciales personales; una sesión iniciada por el usuario
  requiere autorización puntual y debe mantenerse en modo lectura.
- Tratar OSM como fuente externa abierta de contraste, con atribución ODbL, fecha de consulta y
  límites de cobertura. No llamarlo padrón ni prueba de actividad.
- No conectar resultados a F01–F05, `src/`, `data/processed`, `data/analytics`, `dashboard` o
  `notebooks` sin aprobación explícita.
- Mantener RAG, SQL, desduplicación, puntos y mapas en `.agent-tools/` u
  `outputs/analisis_interno/`. Rechazar emails, teléfonos, CUIT/DNI y valores reidentificables.
- Marcar clustering y delimitaciones como `EXPERIMENTAL / NO OFICIAL`; fijar umbrales antes de
  correr y producir sensibilidad antes de concluir.

## Entornos

- Stack principal: `.venv-tools/Scripts/python.exe`.
- ChromaDB aislado: `.agent-tools/chromadb/.venv/Scripts/python.exe`.
- Vinculación/desduplicación: Splink 4 sobre DuckDB; consultar `references/entorno.md`.

## Flujo

1. Leer `references/politica_fuentes.md` y clasificar la fuente como pública/abierta o privada.
2. Para páginas públicamente visibles usar `crawl_public.py`; para páginas dinámicas autorizadas usar
   `browser_public.py`. Para extracción con LLM usar `scrapegraph_schema.py` solo con una clave en
   variable de entorno y un JSON Schema.
3. Para OSM usar `osm_pois.py` primero con `--dry-run`; ejecutar solo una consulta acotada.
4. Para persistencia y análisis usar los wrappers de DuckDB, ChromaDB y Dedupe.
5. Para clustering y mapas usar `cluster_points.py` y `map_points.py`; conservar el carácter
   experimental y no publicar puntos individuales sin revisión de privacidad.
6. Ejecutar `verify_stack.py` antes de declarar el entorno listo.

## Comandos

```powershell
.venv-tools\Scripts\python.exe .agents\skills\datagastro-recoleccion-polos\scripts\verify_stack.py

.venv-tools\Scripts\python.exe .agents\skills\datagastro-recoleccion-polos\scripts\crawl_public.py `
  --url https://example.com --allow-host example.com --output-dir .agent-tools\recoleccion\example

.venv-tools\Scripts\python.exe .agents\skills\datagastro-recoleccion-polos\scripts\browser_public.py `
  --url https://example.com --allow-host example.com

.venv-tools\Scripts\python.exe .agents\skills\datagastro-recoleccion-polos\scripts\osm_pois.py `
  --place "Comuna 1, Buenos Aires, Argentina" --dry-run

.venv-tools\Scripts\python.exe .agents\skills\datagastro-recoleccion-polos\scripts\duckdb_query.py `
  --sql "SELECT 1 AS ok"

.agent-tools\chromadb\.venv\Scripts\python.exe `
  .agents\skills\datagastro-recoleccion-polos\scripts\chroma_store.py smoke
```

Leer `references/entorno.md` para dependencias, credenciales no persistidas y estados de
instalación; consultar `references/versiones_instaladas.md` para reproducir el entorno probado.
