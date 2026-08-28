# Reproduccion de la corrida territorial V3

Estado: `EXPERIMENTAL / NO OFICIAL`.

Ejecutar desde la raiz del repositorio, sin red:

```powershell
.\.venv\Scripts\python.exe scripts\polos_gastro\corrida_territorial_v3\ejecutar_corrida_territorial_v3.py
```

El script lee exclusivamente los baselines enumerados por el preflight V3/V3.1, verifica sus
hashes, calcula en `EPSG:5347`, exporta GeoJSON en `EPSG:4326`, genera la documentacion y arma el
paquete de revision. No llama APIs, no descarga datos y no modifica baselines.

La configuracion explicita esta en `config_territorial_v3.json`. Para reproducibilidad, no editar
GeoJSON de salida manualmente: cambiar la configuracion o el script y regenerar la linea completa.
