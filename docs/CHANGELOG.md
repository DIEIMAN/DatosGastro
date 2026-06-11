# Changelog

## 2026-06-10 - V3 control de datos reales y dashboard

- Se integraron F04 y F05 como fuentes reales semiestructuradas y trazables: eventos gastronomicos y programas/politicas.
- Se agrego `puente_evento_programa.csv` para vinculos explicitos F04-F05.
- Se agregaron analytics F04: eventos por barrio, tipo, anio y cualitativos.
- Se agregaron analytics F05: programas por tipo, estado, catalogo y cualitativos.
- Se ajusto `profile_sources.py` para perfilar archivos grandes por muestra y evitar timeouts con F02.
- Se separo conceptualmente F01/F02/F03: `fact_establecimiento.csv` queda solo para F01, `fact_habilitacion_gastronomica.csv` queda para F02 y `fact_mercado_feria.csv` queda para F03.
- Se agregaron analytics de habilitaciones por anio, barrio, categoria y recientes.
- Se actualizo `analytics_resumen_ejecutivo.csv` para informar indicadores separados: oferta F01, habilitaciones F02, ferias/mercados F03, eventos reales y programas reales.
- Se actualizo `analytics_mapa_oportunidades.csv` para distinguir densidad F01, habilitaciones F02 y ferias/mercados F03.
- Se reforzo `validate_model.py --strict-real` para validar la nueva tabla F02, trazabilidad, FKs y que F02 no vuelva a mezclarse en `fact_establecimiento.csv`.
- Se separaron seeds/manuales en `data/seeds/` y se reservo `data/raw/` para datos reales.
- Se incorporaron URLs reales verificadas para F01, F02 2015-2025 y F03.
- Se descargo y proceso F01/F02/F03 reales en modo estricto.
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
