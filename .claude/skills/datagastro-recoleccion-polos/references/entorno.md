# Entorno y dependencias

## Runtimes

- `.venv-tools`: Agent Reach, Crawl4AI, ScrapeGraph-AI, Browser-Use, Playwright, OSMnx,
  Folium, HDBSCAN, scikit-learn y DuckDB.
- `.agent-tools/chromadb/.venv`: ChromaDB, aislado porque su dependencia `kubernetes` requiere
  `aiohttp>=3.13.5` y Browser-Use fija `aiohttp==3.13.4`.
- Navegadores Playwright/Patchright: caché de usuario de Playwright; no usan perfiles ni cookies
  existentes.

## Credenciales

No guardar claves en el repo. `scrapegraph_schema.py` recibe el nombre de una variable de
entorno mediante `--api-key-env`; nunca muestra su valor. Sin clave solo puede validarse la
inicialización y el esquema.

## Vinculación de registros

Splink 4 está operativo sobre DuckDB y es el motor adoptado por `dedupe-registros`. La librería
homónima `dedupe==3.0.3` no se usa: en Windows/Python 3.12 exigiría compilar extensiones nativas
sin aportar una capacidad necesaria que Splink no cubra.

## Verificación

`scripts/verify_stack.py` no usa red ni datos del proyecto. Prueba imports y operaciones
sintéticas. Un estado `FAIL` no debe reinterpretarse como operativo.
