# Esta carpeta está vacía a propósito

`REPORTE_PARIDAD_SKILLS.md` la declara como capa `v1_1_docs`, pero nunca se pobló. Eso hacía
pensar que faltaban archivos.

**No faltan. Las skills de procedimiento vigentes viven en otro lado:**

| qué | dónde |
|---|---|
| Skills productivas de Claude (canónicas) | `.claude/skills/<skill>/SKILL.md` |
| Espejos puntero | `.agents/skills/` y `agent_skills/claude_imported/` |
| Skills compartidas entre agentes | `agent_skills/shared/` |
| Skills de procedimiento V1, **vigentes** bajo la política V1.1 | `docs/infraestructura_agentes_skills_v1/skills/` |
| Documentación larga | `docs/skills_claude/` |

⚠ Las skills de `..._v1/skills/` citan la numeración de la política **V1**, que cambió. Traducí
con `CORRESPONDENCIA_SECCIONES_V1_V1_1.md` antes de buscar una sección.

**Si algún día se pueblan skills V1.1 acá**, hay que borrar este archivo y actualizar
`REPORTE_PARIDAD_SKILLS.md`. Mientras tanto, esta carpeta vacía no es un pendiente.
