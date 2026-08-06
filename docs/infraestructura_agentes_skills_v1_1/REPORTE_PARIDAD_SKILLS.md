# Reporte de paridad de skills — V1.1

Fecha: 2026-07-14

Script: `scripts/infraestructura_agentes_skills_v1_1/check_skills_parity.py`

Clasificación: `identica` | `wrapper_valido` | `divergente` | `ausente` | `extra`

## Capas

- **claude_productivo**: `.claude\skills`
- **agents_espejo**: `.agents\skills`
- **agent_skills_imported**: `agent_skills\claude_imported`
- **v1_docs**: `docs\infraestructura_agentes_skills_v1\skills`
- **v1_1_docs**: `docs\infraestructura_agentes_skills_v1_1\skills`

## Matriz vs Claude productivo

| skill | agents_espejo | agent_skills_imported |
| --- | --- | --- |
| `datagastro-fuentes-externas` | wrapper_valido | wrapper_valido |
| `datagastro-geodatos` | wrapper_valido | wrapper_valido |
| `datagastro-guardrails` | wrapper_valido | wrapper_valido |
| `datagastro-informes` | wrapper_valido | wrapper_valido |
| `datagastro-limpieza` | wrapper_valido | wrapper_valido |
| `datagastro-metodologia-fuentes` | wrapper_valido | wrapper_valido |
| `datagastro-pipeline` | wrapper_valido | wrapper_valido |
| `datagastro-privacidad` | wrapper_valido | wrapper_valido |
| `datagastro-qa-pdf` | wrapper_valido | wrapper_valido |

## Hallazgos

- (sin hallazgos automáticos)

## Nota

Este script **no copia ni modifica** skills productivas.
Skills de infraestructura V1.1 (snake_case) no son espejos de datagastro-*; su ausencia en `.claude/skills` es esperada hasta promoción controlada.
