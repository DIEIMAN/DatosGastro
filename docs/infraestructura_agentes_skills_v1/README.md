# INFRAESTRUCTURA_AGENTES_SKILLS_V1

Primera versión **controlada y documental** de skills y agentes reutilizables para Claude Code, Codex y otros asistentes en DataGastro / DGDGAS.

**No sustituye** todavía a `.claude/skills/` productivas ni reescribe `AGENTS.md` / `CLAUDE.md`.  
**No usa symlinks.** Promoción a runtimes solo con auditoría y aprobación.

## Documentos

| Archivo | Contenido |
| --- | --- |
| `AUDITORIA_INFRAESTRUCTURA_ACTUAL.md` | Estado del repo antes de diseñar |
| `CATALOGO_REGLAS_REPETIDAS.md` | Extracción de reglas repetidas |
| `MATRIZ_REGLAS_REUTILIZABLES.md` | Matriz regla → skill → agente |
| `ARQUITECTURA_AGENTES_SKILLS_V1.md` | Arquitectura y flujo multiagente |
| `POLITICA_OPERATIVA_DATAGASTRO.md` | Política corta transversal |
| `EVALUACION_AGENTES_SKILLS_V1.md` | Evaluación post casos A–D |
| `GUIA_USO_AGENTES_SKILLS_DATAGASTRO.md` | Guía de uso y prompts cortos |
| `PROPUESTA_ACTUALIZACION_AGENTS_MD.md` | Propuesta (no aplicada) |
| `PROPUESTA_ACTUALIZACION_CLAUDE_MD.md` | Propuesta (no aplicada) |
| `PROPUESTA_CONFIGURACION_CLAUDE_AGENTS.md` | Propuesta agents runtime (no creada) |
| `skills/*/SKILL.md` | 10 skills V1 |
| `agents/*.md` | 7 agentes V1 |
| `plantillas/*` | Handoffs + INFORME_QA |
| `casos_prueba/*` | Casos A–D documentados |

## Skills V1 (10)

1. `auditar_entregable_experimental`  
2. `qa_pdf_pagina_por_pagina`  
3. `crear_paquete_revision_sanitizado`  
4. `auditar_git_y_archivos_protegidos`  
5. `crear_manifest_hashes_metadata`  
6. `integrar_handoffs`  
7. `validar_metricas_y_kpis`  
8. `transformar_cartografia_a_presentacion`  
9. `gestionar_decisiones_humanas`  
10. `auditar_evidencia_documental`  

## Agentes V1 (7)

| Agente | Rol |
| --- | --- |
| `coordinador` | Orquestación liviana (si ≥2 roles) |
| `investigador_documental` | Evidencia y bibliografía |
| `auditor_metodologico` | Método y robustez |
| `cartografo_territorial` | Capas y mapas |
| `editor_institucional` | Narrativa DGDGAS |
| `integrador_tecnico_editorial` | Handoffs → versión nueva |
| `auditor_qa` | Cierre solo lectura del producto |

## Flujo

```text
usuario → coordinador? → especialista(s) → handoff → auditor_qa → entrega
```

## Pack de revisión

- Carpeta: `outputs/infraestructura_agentes_skills_v1/REVISION_INFRAESTRUCTURA_AGENTES_SKILLS_V1/`
- ZIP: `outputs/infraestructura_agentes_skills_v1/REVISION_INFRAESTRUCTURA_AGENTES_SKILLS_V1.zip`
- Script: `scripts/infraestructura_agentes_skills_v1/empaquetar_revision_v1.py`

## Líneas rojas

Ver política. En particular: no tocar finales F25/26/v2.1, no Places sin autorización, no commit sin pedido, no symlinks.
