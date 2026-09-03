# Índice compartido de skills Claude importadas

Desde 2026-07-14, `.agents/skills/` contienen **réplicas
puntero** (wrappers): conservan nombre y descripción, y remiten a la copia canónica en
`.claude/skills/<skill>/SKILL.md`. Leer siempre la canónica; las réplicas no duplican el
procedimiento (así se eliminan divergencias entre agentes). La documentación larga sigue en
`docs/skills_claude/`.

| Skill | Ruta importada | Cuándo usarla |
| --- | --- | --- |
| `datagastro-guardrails` | `.agents/skills/datagastro-guardrails/SKILL.md` | Siempre antes de borrar, mover, tocar pipeline, exponer datos o evaluar fuentes sensibles |
| `datagastro-metodologia-fuentes` | `.agents/skills/datagastro-metodologia-fuentes/SKILL.md` | Al describir, clasificar o sumar fuentes F/I/E |
| `datagastro-privacidad` | `.agents/skills/datagastro-privacidad/SKILL.md` | Al perfilar, analizar o exportar datos con riesgo personal o sensible |
| `datagastro-pipeline` | `.agents/skills/datagastro-pipeline/SKILL.md` | Antes de tocar `src/`, `data/processed`, `data/analytics`, validaciones o tests |
| `datagastro-geodatos` | `.agents/skills/datagastro-geodatos/SKILL.md` | Para direcciones, comunas, barrios, lat/lon, USIG, OSM, densidad o sesgos territoriales |
| `datagastro-fuentes-externas` | `.agents/skills/datagastro-fuentes-externas/SKILL.md` | Al evaluar Google Places, delivery, pagos, redes, POS u otras plataformas externas |
| `datagastro-informes` | `.agents/skills/datagastro-informes/SKILL.md` | Al redactar informes ejecutivos, resúmenes o entregables institucionales |
| `datagastro-qa-pdf` | `.agents/skills/datagastro-qa-pdf/SKILL.md` | SIEMPRE después de generar o regenerar un PDF y antes de reportarlo terminado (render + inspección visual) |

## Regla de uso

Si un pedido toca varias dimensiones, consultar primero guardrails y luego la skill específica.
Si el pedido implica **correr algo y reportar un resultado**, agregar siempre
`datagastro_metodo_experimental.md`: `datagastro-guardrails` dice qué no hacer, ésta dice cómo hacer.
Por ejemplo, un informe con datos de formulario debe combinar: guardrails, privacidad, informes y
`datagastro_proyectos_cortos.md`.

## Skills compartidas operativas

Además de las skills importadas desde Claude, los agentes deben usar estas guías compartidas:

| Skill compartida | Ruta | Cuándo usarla |
| --- | --- | --- |
| Reporte con formulario | `agent_skills/shared/datagastro_reporte_formulario.md` | Para Google Forms, XLSX/CSV de respuestas, PDF/DOCX de preguntas y contexto de eventos |
| QA privacidad entregables | `agent_skills/shared/datagastro_qa_privacidad.md` | Antes de cerrar informes, packs, DOCX, PDF, CSV o Markdown publicables |
| **Método experimental** | `agent_skills/shared/datagastro_metodo_experimental.md` | **SIEMPRE que una corrida vaya a producir un número que después se lea como conclusión**: bandas escritas antes de correr, control aleatorio en ablaciones, umbrales que no se mueven, curvas de sensibilidad, presupuesto de API, procedencia y licencia, y «no encontramos» ≠ «no existe» |

Para proyectos tipo Cafecito, combinar `datagastro_reporte_formulario.md`,
`datagastro_qa_privacidad.md`, `datagastro_modelo_informes.md` y la skill importada
`datagastro-privacidad`.

## Fuente canónica

Los documentos largos siguen en `docs/skills_claude/`. Si hay conflicto entre una copia importada
y `docs/skills_claude/`, revisar el contexto y priorizar el guardrail vigente definido por el
responsable del proyecto.
