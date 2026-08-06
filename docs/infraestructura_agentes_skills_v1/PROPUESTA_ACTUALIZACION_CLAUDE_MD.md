# Propuesta de actualización — CLAUDE.md

**Estado:** PROPUESTA. **No aplicada.**

## Texto actual relevante

- Guardrails Prioridad 0 (9 puntos).  
- `docs/skills_claude/` index.  
- Entorno Windows + venv + `pdf_check` + `validate_kpis`.  
- Continuidad: handoffs en `docs/revisiones/`.  
- Alcance subproyectos.

## Problema

1. No referencia el paquete de agentes/skills V1.  
2. Skills productivas en `.claude/skills/` y skills V1 en docs pueden confundirse.  
3. No menciona roles (documental, cartógrafo, QA solo lectura).  
4. Hook SessionStart solo mira `docs/revisiones/HANDOFF_*`, no handoffs del paquete V1.

## Cambio propuesto (insertar tras “Documentación operativa”)

```markdown
## Infraestructura agentes y skills V1 (controlada)

Paquete documental (aún no productivo global):

- Política: `docs/infraestructura_agentes_skills_v1/POLITICA_OPERATIVA_DATAGASTRO.md`
- Agentes: `docs/infraestructura_agentes_skills_v1/agents/`
- Skills V1: `docs/infraestructura_agentes_skills_v1/skills/`
- Guía: `docs/infraestructura_agentes_skills_v1/GUIA_USO_AGENTES_SKILLS_DATAGASTRO.md`

Las skills productivas siguen en `.claude/skills/` y `docs/skills_claude/`.
Las V1 se leen por ruta hasta promoción aprobada.
Ante conflicto de procedimiento: guardrails 01 > política V1 > prompt puntual.
```

## Justificación

Claude ya carga CLAUDE.md siempre; un puntero corto activa multiagente sin reescribir guardrails.

## Impacto

Bajo en tokens si el párrafo es corto.

## Riesgo

Bajo. Evitar copiar las 10 skills dentro de CLAUDE.md.

## Compatibilidad

No depende de `.claude/agents/`. Compatible con hooks actuales.

## ¿Requiere reiniciar sesiones?

Sí para Claude Code (CLAUDE.md se carga al inicio de sesión).
