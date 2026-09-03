# Preflight expansión candidatos V4

**Fecha:** 2026-07-12  
**Rol:** cartografo_territorial  
**Estado:** preparación completa — **sin Places ni clustering**

## Qué incluye

- Config final + snapshot Claude
- Inventario de insumos
- Áreas de consulta GeoJSON (barrios, ejes, nodos, bandas, controles)
- Cobertura vs universo sanitizado 2026-07-09
- Plan incremental de consultas (no ejecutado)
- Subunidades Centro C-S01…C-S08
- Contratos, métodos, tandas, riesgos, QA

## Qué no incluye

- Adopción de polos
- Ejecución API
- Resultados de clustering
- Expedientes documentales completos (viven en evidencia Grok)

## Orden de lectura

1. `ESTADO_RECUPERACION_PREFLIGHT_CLAUDE_V4.md`
2. `HANDOFF_CODEX_EJECUCION_EXPANSION_V4.md`
3. `PLAN_TANDAS` + `MATRIZ_COBERTURA`
4. `AREAS_CONSULTA_CANDIDATOS_V4.geojson`
5. Contratos Places / universo

## Integración documental

Ver `docs/polos_gastro/preparacion_integrada_expansion_v4/` y evidencia Grok V4.

## Reproducción

```text
.venv/Scripts/python.exe scripts/polos_gastro/expansion_candidatos_v4_preflight/build_preflight_expansion_candidatos_v4.py
```
