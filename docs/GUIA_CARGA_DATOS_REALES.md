# Guia de carga de datos reales

No inventar URLs ni fuentes. `data/raw/` es solo para archivos reales descargados desde BA Data / GCBA u otra fuente oficial documentada.

## Datasets a descargar

1. F01 Oferta y Establecimientos Gastronomicos
   - Portal: `https://data.buenosaires.gob.ar/dataset/oferta-establecimientos-gastronomicos`
   - Guardar como: `data/raw/f01_oferta_establecimientos_gastronomicos.csv`

2. F02 Habilitaciones Aprobadas AGC
   - Portal: `https://data.buenosaires.gob.ar/dataset/habilitaciones-aprobadas`
   - Guardar como: `data/raw/f02_habilitaciones_aprobadas.csv`
   - Si viene por anio, usar nombres como `data/raw/f02_habilitaciones_aprobadas_2025.csv`

3. F03 Ferias y Mercados
   - Portal: `https://data.buenosaires.gob.ar/dataset/ferias-mercados`
   - Guardar como: `data/raw/f03_ferias_mercados.csv`

## Escenario A: URLs directas en config

Completar `SOURCE_CONFIG` en `src/config.py` solo con URLs directas a archivo. Luego ejecutar:

```bash
python src/download_sources.py
```

El script guarda los archivos en `data/raw/` y reporta si algun archivo pesa menos de 1 KB.

## Escenario B: descarga manual

1. Descargar los CSV oficiales desde el portal.
2. Guardarlos en `data/raw/`.
3. Usar nombres que empiecen con `f01_`, `f02_` o `f03_`.
4. Ejecutar:

```bash
python src/profile_sources.py
python src/build_model.py
python src/build_analytics.py
python src/validate_model.py
```

## Verificar que se tomaron como reales

Revisar:

- `outputs/tablas_resumen/contratos_fuentes.csv`
- `docs/contratos_fuentes.md`
- `docs/AUDITORIA_DATOS_REALES.md`

Para cada fuente, el campo `origin` debe ser `real`. Si dice `seed`, el pipeline uso fallback de desarrollo.

## Si las columnas no coinciden

1. Revisar `docs/contratos_fuentes.md`.
2. Identificar columnas requeridas faltantes.
3. Agregar alias de columnas en `src/source_contracts.py`.
4. Volver a correr `python src/build_model.py`.

## Validacion estricta

Para saber si el proyecto esta listo para analisis serio:

```bash
python src/build_model.py --strict-real
python src/build_analytics.py --strict-real
python src/validate_model.py --strict-real
```

Si faltan datos reales, estos comandos deben fallar. Ese fallo es correcto y evita publicar seeds como datos reales.
