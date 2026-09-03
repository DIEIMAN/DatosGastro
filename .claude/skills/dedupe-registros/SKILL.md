---
name: dedupe-registros
description: >
  Desduplicación y vinculación probabilística de registros entre fuentes
  dispares (Splink, modelo Fellegi-Sunter sobre DuckDB): emparejar el mismo
  local que aparece con variantes de nombre/dirección en padrón, Overture, OSM
  y relevamientos. Usar para cruces entre bases donde el join exacto falla.
---

# Splink — vinculación de entidades entre fuentes

Motor instalado: **Splink 4** en `.venv-tools` (la librería `dedupe` clásica no
compila en esta máquina: sus extensiones C no tienen wheel para Python 3.12 en
Windows y falta MSVC Build Tools; si se la quiere igual, instalar antes
"Visual Studio Build Tools"). Ejecutar con `.venv-tools\Scripts\python.exe`.

## Flujo típico (link entre dos DataFrames)

```python
import splink.comparison_library as cl
from splink import Linker, SettingsCreator, DuckDBAPI, block_on

settings = SettingsCreator(
    link_type="link_only",           # "dedupe_only" para duplicados internos
    comparisons=[
        cl.JaroWinklerAtThresholds("nombre", [0.9, 0.7]),
        cl.LevenshteinAtThresholds("direccion", 2),
        cl.ExactMatch("barrio"),
    ],
    blocking_rules_to_generate_predictions=[block_on("barrio")],
)
linker = Linker([df_a, df_b], settings, db_api=DuckDBAPI())
linker.training.estimate_u_using_random_sampling(max_pairs=1e6)
pares = linker.inference.predict(threshold_match_probability=0.9)
df_pares = pares.as_pandas_dataframe()
```

## Reglas DataGastro

1. Un match es probabilístico: reportar siempre el umbral usado y la banda de
   score; los cruces que alimentan cifras publicadas requieren revisión humana
   de los pares límite (método experimental del proyecto).
2. Emparejar por dirección además de nombre — lección registrada del catálogo
   de Notables: el nombre solo produce falsos negativos.
3. Los pares salen con columna de origen por lado (F/I/E) y van a `outputs/analisis_interno/`.
