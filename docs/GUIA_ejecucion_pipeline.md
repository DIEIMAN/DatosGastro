# Guia de ejecucion del pipeline

## 1. Instalar dependencias

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Configurar fuentes

Revisar `src/config.py`.

Completar `SOURCE_CONFIG["F01"]["url"]`, `SOURCE_CONFIG["F02"]["url"]` y `SOURCE_CONFIG["F03"]["url"]` solo con URLs directas a archivos descargables oficiales. Si no estan disponibles, dejarlas como `None`.

## 3. Descargar

```bash
python src/download_sources.py
```

Resultado esperado con V2 inicial: `PENDING` para fuentes sin URL directa. El log queda en `outputs/download_sources.log`.

## 4. Perfilar fuentes

```bash
python src/profile_sources.py
```

Salidas:

- `outputs/tablas_resumen/perfilado_fuentes_resumen.csv`
- `docs/perfilado_fuentes.md`

## 5. Construir modelo

```bash
python src/build_model.py
```

Reconstruye `data/processed/` desde `data/raw/`. Si solo hay seed, conserva `origen_dato = datos seed`.

## 6. Construir analytics

```bash
python src/build_analytics.py
```

Reconstruye `data/analytics/` desde `data/processed/`.

## 7. Validar

```bash
python src/validate_model.py
```

La validacion termina con codigo distinto de cero si hay errores graves de estructura, PK, FK o analytics vacias.
