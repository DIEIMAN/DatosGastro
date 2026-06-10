# Changelog

## 2026-06-10 - V3 control de datos reales y dashboard

- Se separaron seeds/manuales en `data/seeds/` y se reservo `data/raw/` para datos reales.
- Se agrego modo `--strict-real` a `build_model.py`, `build_analytics.py` y `validate_model.py`.
- Se reforzo trazabilidad obligatoria en analytics: fuentes, URLs, fechas, metodologia, limitaciones y `apto_dashboard`.
- Se agrego auditoria real-vs-seed en `src/audit_real_data.py`.
- Se agregaron `docs/AUDITORIA_DATOS_REALES.md`, `docs/GUIA_FUENTES_DASHBOARD.md` y `docs/GUIA_CARGA_DATOS_REALES.md`.
- Se evita presentar seeds como datos reales: analytics seed quedan `apto_dashboard = no`.

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
