# Versiones instaladas el 2026-08-14

## `.venv-tools`

- Agent Reach 1.5.0, instalado desde `Panniantong/agent-reach` rama `main`.
- Crawl4AI 0.9.2.
- ScrapeGraph-AI 2.1.6.
- Browser-Use 0.13.7.
- Playwright 1.62.0.
- OSMnx 2.1.1.
- Folium 0.20.0.
- HDBSCAN 0.8.44.
- scikit-learn 1.9.0.
- DuckDB 1.5.5.
- Splink 4.0.16 (vinculación/desduplicación probabilística sobre DuckDB).

## `.agent-tools/chromadb/.venv`

- ChromaDB 1.5.9.

## Decisión de entorno

- La librería `dedupe` 3.0.3 no se instala: Splink 4 cubre la vinculación probabilística sin
  requerir Microsoft Visual C++ y ya es el motor declarado por la skill `dedupe-registros`.

Estas versiones describen el entorno probado, no una recomendación de actualización automática.
