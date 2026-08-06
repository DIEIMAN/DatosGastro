# Propuesta de actualización — AGENTS.md

**Estado:** PROPUESTA. **No aplicada.** No sobrescribe el archivo vigente.

## Texto actual relevante

Sección “DataGastro reporting standard” (líneas ~7–18): apunta a `agent_skills/README.md` y `shared/*`, y a `claude_imported/` para guardrails.

Sección “Reglas obligatorias”: no inventar datos, privacidad, no commit/push, no `git add .`.

## Problema

1. No menciona la infraestructura V1 de agentes/skills ni la política operativa corta.  
2. No apunta a `datagastro-qa-pdf` / QA visual (sí está en Claude).  
3. `agent_skills/README` desactualizado respecto de `.agents/skills` y drift de copias.  
4. El bloque Cowork largo puede competir en tokens con la política corta.

## Cambio propuesto (párrafo a insertar tras reporting standard)

```markdown
## Infraestructura agentes y skills (V1, opcional)

Para trabajo multiagente, experimentos Polos/Cafecito/Mercados o packs de revisión:

1. Leer `docs/infraestructura_agentes_skills_v1/POLITICA_OPERATIVA_DATAGASTRO.md`.
2. Elegir agente en `docs/infraestructura_agentes_skills_v1/agents/`.
3. Ejecutar skills en `docs/infraestructura_agentes_skills_v1/skills/<nombre>/SKILL.md`.
4. Usar plantillas de handoff en `docs/infraestructura_agentes_skills_v1/plantillas/`.
5. Cerrar con auditor QA distinto del productor.

No promover skills a `.claude/` ni `.agents/` sin aprobación.
Guía: `docs/infraestructura_agentes_skills_v1/GUIA_USO_AGENTES_SKILLS_DATAGASTRO.md`.
```

Opcional (segunda fase): acortar o archivar el bloque Cowork muy largo hacia `docs/`.

## Justificación

Reduce prompts repetidos; alinea Codex con Claude sin symlinks ni settings.

## Impacto

- Bajo: solo lectura adicional cuando se use multiagente.  
- No cambia pipeline F01–F05.

## Riesgo

- Medio-bajo: más texto en AGENTS.md aumenta tokens de sesión Codex. Mitigar con párrafo corto.

## Compatibilidad

- Compatible con `agent_skills/*` existente.  
- No requiere `.codex/` poblado.

## ¿Requiere reiniciar sesiones?

Sí, para que Codex/cargadores que cachean AGENTS.md vean el cambio. Sesiones ya abiertas: re-leer archivo.
