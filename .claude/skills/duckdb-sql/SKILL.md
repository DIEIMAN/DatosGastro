---
name: duckdb-sql
description: >
  Consultas SQL analíticas locales con DuckDB sobre CSV/Parquet/GeoJSON del
  proyecto (cruces de tablas, métricas, agregaciones rápidas sin cargar todo en
  pandas). Usar cuando haya que cruzar o agregar tablas grandes de outputs/ o
  data/ con SQL. Solo lectura sobre datos del pipeline: no reemplaza ni modifica
  data/processed ni data/analytics (guardrail 2).
---

# DuckDB — SQL analítico local

Instalado en los dos venvs (`.venv` 1.5.5 y `.venv-tools`): usar `.venv\Scripts\python.exe`,
no hace falta cambiar de interprete. Tambien existe el MCP `duckdb` para consultas ad hoc.

## Uso básico

```python
import duckdb

con = duckdb.connect()  # en memoria; para persistir: duckdb.connect("archivo.duckdb")

# Consultar CSV directamente, sin cargarlo
r = con.sql("""
    SELECT barrio, count(*) AS n
    FROM 'outputs/BARRIDO_CIUDAD_2026-08/base_referencia_agregada.csv'
    GROUP BY barrio ORDER BY n DESC
""").df()
```

También lee Parquet y JSON con la misma sintaxis (`FROM 'ruta/*.parquet'`).

## Reglas propias de la herramienta

1. Los `.duckdb` persistentes van a `outputs/` o al scratchpad, nunca a `data/processed` ni
   `data/analytics`; heredan la sensibilidad de lo que contienen.
2. Toda tabla que junte fuentes lleva columna de origen (F/I/E).

Los guardrails generales ya estan cargados desde `CLAUDE.md`; no se repiten aca.
