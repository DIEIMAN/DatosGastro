# Propuesta de configuración — agentes Claude (`.claude/agents/`)

**Estado:** PROPUESTA. **No crear** `.claude/agents/` ni modificar `.claude/settings.json` en esta tanda.

## Situación actual

| Elemento | Estado |
| --- | --- |
| `.claude/agents/` | No existe |
| `.claude/settings.json` | Permissions ask en git; hooks handoff/graphify; plugins incl. `atomic-agents` |
| Definiciones V1 | `docs/infraestructura_agentes_skills_v1/agents/*.md` |

## Problema

1. Los roles V1 no están en el formato nativo de Claude agents (si la versión lo soporta).  
2. Activar agents reales sin prueba puede dar permisos demasiado amplios.  
3. `settings.json` ya tiene cambios locales no auditados en el working tree; **no tocar** sin autorización.

## Cambio propuesto (fase futura, post-aprobación Diego)

1. Verificar en la versión de Claude Code del equipo el esquema de `.claude/agents/*.md` o YAML.  
2. Crear **un agente por archivo**, con:
   - `name`, `description`
   - tools limitados (Read, Grep; Write solo en rutas de paquete; Bash acotado)
   - system prompt = resumen del agente V1 + “aplicar POLITICA + skills listadas”
3. **No** dar a ningún agente `git commit`/`push` ni write global.  
4. `auditor_qa`: preferir deny write sobre el entregable; allow write solo en `**/QA_*` y `**/INFORME_QA*`.  
5. Mantener definiciones canónicas en `docs/.../agents/`; `.claude/agents/` = adaptador delgado.

### Ejemplo de adaptador (ilustrativo, no creado)

```markdown
---
name: auditor-qa-datagastro
description: QA independiente de entregables experimentales DataGastro. Solo lectura del producto; escribe INFORME_QA.
---
Leer docs/infraestructura_agentes_skills_v1/agents/auditor_qa.md
y POLITICA_OPERATIVA_DATAGASTRO.md. No corregir en silencio.
```

## Settings

| Acción | Recomendación V1 |
| --- | --- |
| Modificar `settings.json` | **No**, salvo necesidad demostrada |
| `settings.local.json` | No versionar |
| Plugins atomic-agents | Documentar uso; no base de verdad del proyecto |

## Justificación

Separar canónico (docs) de runtime (`.claude/agents`) evita drift y permisos excesivos.

## Impacto

Medio cuando se active: Claude podrá invocar agentes por nombre.  
Hasta entonces: invocar por prompt + ruta al MD del agente.

## Riesgo

Alto si se copian agentes con write ilimitado. Mitigar con deny paths y QA de permisos.

## Compatibilidad

Depende de versión Claude Code. Fallback: leer `docs/.../agents/*.md` manualmente (funciona hoy).

## ¿Requiere reiniciar sesiones?

Sí, al crear/cambiar `.claude/agents/` o settings.
