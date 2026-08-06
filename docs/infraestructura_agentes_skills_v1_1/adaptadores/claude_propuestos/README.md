# Adaptadores Claude propuestos (NO activados)

## Verificación de schema

- Carpeta `.claude/agents/`: **no existe** en este repo al 2026-07-11.
- No hay documentación versionada del schema de agentes nativos en el proyecto.
- `.claude/settings.json` **no se modifica** en V1.1.

## Decisión

Los archivos en este directorio son **propuestas de adaptador delgado**.  
**No se copian** a `.claude/agents/` en esta tanda.

Para usar hoy: el prompt de sesión debe apuntar a:

1. `POLITICA_OPERATIVA_DATAGASTRO_V1_1.md`
2. Definición del agente en catálogo / V1 `agents/*.md`
3. Este adaptador como checklist de límites

## Formato propuesto (hipotético)

Frontmatter mínimo si Claude Code lo soporta en el futuro:

```yaml
---
name: datagastro-auditor-qa
description: QA independiente DataGastro; solo lectura del producto.
---
```

Cuerpo: puntero a política + catálogo + skills; deny write sobre producto auditado.
