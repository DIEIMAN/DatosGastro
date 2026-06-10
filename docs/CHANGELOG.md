# Changelog

## 2026-06-10 - V2 operativa reproducible

- Se agrego configuracion explicita de fuentes en `src/config.py` sin URLs inventadas.
- Se mejoro `src/download_sources.py` para reportar pendientes, validar tamanos y generar log.
- Se agrego `src/profile_sources.py` con resumen CSV y documento de perfilado.
- Se robustecio `src/clean_text.py`.
- Se agrego normalizacion offline de barrios, comunas y ubicaciones en `src/normalize_addresses.py`.
- Se agrego taxonomia gastronomica trazable en `src/normalize_categories.py`.
- Se reconstruye `data/processed/` desde `data/raw/` con seeds como fallback.
- Se reconstruye `data/analytics/` desde `data/processed/`.
- Se agrego `src/validate_model.py` para PK, FK, trazabilidad y analytics.
- Se actualizaron README, criterios, trazabilidad, limitaciones y guia de ejecucion.

## V1

- Estructura inicial de carpetas, seeds, SQL, docs, notebooks y primera auditoria.
