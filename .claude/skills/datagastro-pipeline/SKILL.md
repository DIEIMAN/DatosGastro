---
name: datagastro-pipeline
description: Trabajar el pipeline de DataGastro sin romperlo. Usar antes de tocar src/, data/processed, data/analytics, validaciones, tests o de integrar una fuente nueva. Recordar que F01-F05 está intacto sin permiso.
---

# Pipeline reproducible

Contenido canónico: `docs/skills_claude/04_pipeline_reproducible.md`.

- No modificar sin permiso: `src/build_model.py`, `src/build_analytics.py`, `data/processed/`,
  `data/analytics/`, `dashboard/`, `notebooks/`, informe final.
- Documentar antes de codear; `--strict-real` manda; seeds ≠ reales; idempotencia; trazabilidad
  por fila.
- Flujo para fuente nueva: ficha + contrato → schema/stub → validación tolerante → tests →
  correr validaciones → aprobación de Diego.
- Comandos: `python src/build_model.py --strict-real`, `python src/build_analytics.py
  --strict-real`, `python src/validate_model.py --strict-real`, `python -m unittest discover
  tests`. No regenerar salidas productivas sin permiso.
