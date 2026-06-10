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

## 4 bis. Contratos de columnas

`build_model.py` detecta primero archivos reales y usa seeds solo como fallback.

Patrones reconocidos:

- F01: `f01_*.csv`, `*oferta*establecimientos*gastronom*.csv`, `*establecimientos*gastronom*.csv`
- F02: `f02_*.csv`, `*habilitaciones*aprobadas*.csv`, `*habilitaciones*.csv`
- F03: `f03_*.csv`, `*ferias*mercados*.csv`, `*ferias*.csv`, `*mercados*.csv`

Despues de correr el modelo se generan:

- `outputs/tablas_resumen/contratos_fuentes.csv`
- `docs/contratos_fuentes.md`

Si una fuente real trae columnas no reconocidas, ajustar los candidatos en `src/source_contracts.py`.

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
