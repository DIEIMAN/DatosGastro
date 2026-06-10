# Estructura del proyecto

La raiz del repositorio debe quedar liviana:

- `README.md`
- `requirements.txt`
- `.gitignore`
- carpetas principales del proyecto

## Carpetas canonicas

- `src/`: codigo ejecutable del pipeline.
- `data/raw/`: fuentes seed o descargadas.
- `data/processed/`: modelo normalizado reconstruible.
- `data/analytics/`: salidas agregadas reconstruibles.
- `sql/`: scripts SQL vigentes.
- `docs/`: documentacion vigente.
- `outputs/`: reportes generados por ejecuciones locales.
- `notebooks/`: notebooks exploratorios.

## Archivo historico

- `docs/archive/v1/`: entregables y documentos heredados de V1.
- `docs/references/`: documentos fuente de referencia, como el PDF inicial.
- `data/archive/v1_root/`: CSV sueltos heredados de la raiz.
- `sql/archive/v1_root/`: SQL sueltos heredados de la raiz.

Los archivos de `archive/` se conservan para trazabilidad, pero no deben ser usados como fuente canonica del pipeline.

## Compatibilidad

`scripts/compat/` guarda wrappers antiguos para quien haya ejecutado scripts desde la raiz. Los comandos recomendados son:

```bash
python src/download_sources.py
python src/profile_sources.py
python src/build_model.py
python src/build_analytics.py
python src/validate_model.py
```
