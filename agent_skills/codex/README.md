# Codex skills DataGastro

Carpeta reservada para instrucciones específicas de Codex.

Por ahora, Codex debe usar como base:

- `AGENTS.md`
- `agent_skills/README.md`
- `agent_skills/shared/datagastro_modelo_informes.md`
- `agent_skills/shared/datagastro_proyectos_cortos.md`
- `.agents/skills/` como referencia importada desde Claude.

## Infraestructura multiagente (V1.1)

- Política: `docs/infraestructura_agentes_skills_v1_1/POLITICA_OPERATIVA_DATAGASTRO_V1_1.md`
- Ciclo y roles: `docs/infraestructura_agentes_skills_v1_1/CICLO_OPERATIVO_UNA_PASADA.md`
- Adaptadores delgados: `docs/infraestructura_agentes_skills_v1_1/adaptadores/codex/`
- Catálogo: `docs/infraestructura_agentes_skills_v1_1/CATALOGO_AGENTES_SKILLS.json`

No se asume carga automática de `.codex/`. No duplicar reglas si pueden vivir en
`agent_skills/shared/` o en la política V1.1.
