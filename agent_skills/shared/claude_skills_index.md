# Índice compartido de skills Claude importadas

Las skills de `.claude/skills/` fueron copiadas a `agent_skills/claude_imported/` para que Codex
también pueda consultarlas como referencia. Esta copia es una instantánea segura: no reemplaza los
originales ni la documentación canónica en `docs/skills_claude/`.

| Skill | Ruta importada | Cuándo usarla |
| --- | --- | --- |
| `datagastro-guardrails` | `agent_skills/claude_imported/datagastro-guardrails/SKILL.md` | Siempre antes de borrar, mover, tocar pipeline, exponer datos o evaluar fuentes sensibles |
| `datagastro-metodologia-fuentes` | `agent_skills/claude_imported/datagastro-metodologia-fuentes/SKILL.md` | Al describir, clasificar o sumar fuentes F/I/E |
| `datagastro-privacidad` | `agent_skills/claude_imported/datagastro-privacidad/SKILL.md` | Al perfilar, analizar o exportar datos con riesgo personal o sensible |
| `datagastro-pipeline` | `agent_skills/claude_imported/datagastro-pipeline/SKILL.md` | Antes de tocar `src/`, `data/processed`, `data/analytics`, validaciones o tests |
| `datagastro-geodatos` | `agent_skills/claude_imported/datagastro-geodatos/SKILL.md` | Para direcciones, comunas, barrios, lat/lon, USIG, OSM, densidad o sesgos territoriales |
| `datagastro-fuentes-externas` | `agent_skills/claude_imported/datagastro-fuentes-externas/SKILL.md` | Al evaluar Google Places, delivery, pagos, redes, POS u otras plataformas externas |
| `datagastro-informes` | `agent_skills/claude_imported/datagastro-informes/SKILL.md` | Al redactar informes ejecutivos, resúmenes o entregables institucionales |
| `datagastro-limpieza` | `agent_skills/claude_imported/datagastro-limpieza/SKILL.md` | Antes de proponer borrado, movimiento o limpieza local |

## Regla de uso

Si un pedido toca varias dimensiones, consultar primero guardrails y luego la skill específica.
Por ejemplo, un informe con datos de formulario debe combinar: guardrails, privacidad, informes y
`datagastro_proyectos_cortos.md`.

## Skills compartidas operativas

Además de las skills importadas desde Claude, los agentes deben usar estas guías compartidas:

| Skill compartida | Ruta | Cuándo usarla |
| --- | --- | --- |
| Reporte con formulario | `agent_skills/shared/datagastro_reporte_formulario.md` | Para Google Forms, XLSX/CSV de respuestas, PDF/DOCX de preguntas y contexto de eventos |
| QA privacidad entregables | `agent_skills/shared/datagastro_qa_privacidad.md` | Antes de cerrar informes, packs, DOCX, PDF, CSV o Markdown publicables |

Para proyectos tipo Cafecito, combinar `datagastro_reporte_formulario.md`,
`datagastro_qa_privacidad.md`, `datagastro_modelo_informes.md` y la skill importada
`datagastro-privacidad`.

## Fuente canónica

Los documentos largos siguen en `docs/skills_claude/`. Si hay conflicto entre una copia importada
y `docs/skills_claude/`, revisar el contexto y priorizar el guardrail vigente definido por el
responsable del proyecto.
