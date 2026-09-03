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

Instalado en `.venv-tools`. Ejecutar con `.venv-tools\Scripts\python.exe`.

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

## Reglas DataGastro

1. Solo lectura sobre `data/processed/` y `data/analytics/`: nunca escribir ahí
   (guardrail 2). Los `.duckdb` persistentes van a `outputs/` o al scratchpad.
2. No mezclar universos de fuentes (F/I/E) en una misma tabla sin columna de
   origen explícita (guardrail 3).
3. Archivos con datos internos/privados: los `.duckdb` derivados heredan la
   sensibilidad — van a carpeta ignorada por Git (guardrail 8).
