# Agent skills DataGastro

Base compartida para que Claude, Codex y futuros agentes trabajen informes DataGastro con los
mismos criterios de seguridad, privacidad y estilo.

## Inventario detectado

| Ruta | Tipo | Uso aparente | Alcance | Utilidad para informes |
| --- | --- | --- | --- | --- |
| `CLAUDE.md` | Archivo raíz de instrucciones | Resumen operativo que Claude carga por sesión; contiene guardrails prioritarios | Claude, reusable por cualquier agente | Alta: reglas de privacidad, fuentes, pipeline, redacción prudente |
| `.claude/skills/` | Carpeta de skills | Wrappers `SKILL.md` de proyecto para Claude Code | Claude | Alta: guardrails, informes, privacidad, pipeline, fuentes, geodatos |
| `.claude/settings.local.json` | Configuración local | Permisos/configuración local de Claude | Claude local | No se copia ni se reutiliza como skill; puede contener preferencias locales |
| `.agents/skills/` | Carpeta de skills | Espejo puntero de las nueve skills canónicas de `.claude/skills/` (paridad verificada 2026-07-14) | General | Alta: es el punto de entrada para agentes que no son Claude Code |
| `.codex/` | Carpeta | Carpeta reservada para Codex; sin contenido útil detectado | Codex | Baja por ahora |
| `docs/skills_claude/` | Documentación operativa | Fuente canónica de reglas DataGastro para Claude y otros asistentes | General, nacida para Claude | Muy alta: guardrails, metodología, privacidad, informes ejecutivos |
| `docs/prompts_codex.md` | Prompts | Prompts de trabajo para Codex sobre dashboard, notebook e informe | Codex | Media/alta: útil como referencia, pero son tareas puntuales |
| `docs/fuentes_externas/prompt_codex_fuentes_externas.md` | Prompt | Trabajo sobre fuentes externas | Codex/general | Media: útil para fuentes privadas/externas |
| `docs/mercados_caba/*prompt*.md` | Prompts/procedimiento | Prompts específicos del proyecto Mercados CABA | Proyecto específico | Media: útil como antecedente, no estándar general |
| `data/archive/_a_revisar/.../prompt_codex_fuentes_externas.md` | Prompt archivado | Copia histórica de prompt de fuentes externas | Archivo histórico | Baja: no usar como fuente vigente sin validar |

## Skills importadas desde Claude

Desde 2026-07-14, `agent_skills/claude_imported/` (y su espejo `.agents/skills/`) contiene
**réplicas puntero**: cada `SKILL.md` conserva nombre y descripción y remite a la copia canónica
en `.claude/skills/<skill>/SKILL.md`, que es la única fuente del procedimiento:

- `datagastro-guardrails`
- `datagastro-metodologia-fuentes`
- `datagastro-privacidad`
- `datagastro-pipeline`
- `datagastro-geodatos`
- `datagastro-fuentes-externas`
- `datagastro-informes`
- `datagastro-limpieza`
- `datagastro-qa-pdf`

Los originales siguen en `.claude/skills/`. Ante diferencia, gana la canónica
(validador: `scripts/infraestructura_agentes_skills_v1_1/check_skills_parity.py`).

## Skills compartidas

La carpeta `agent_skills/shared/` contiene documentos de referencia que deberían consultar todos
los agentes antes de producir informes o entregables:

- `datagastro_modelo_informes.md`: modelo común para informes DataGastro.
- `datagastro_proyectos_cortos.md`: guía para relevamientos chicos tipo Cafecito.
- `datagastro_reporte_formulario.md`: skill operativa para informes basados en formularios,
  encuestas y planillas de respuestas.
- `datagastro_qa_privacidad.md`: skill operativa para revisar entregables públicos y evitar
  exposición de datos sensibles.
- `claude_skills_index.md`: índice de las skills Claude importadas y sus usos.

## Uso recomendado por Codex

Antes de trabajar en un informe DataGastro, Codex debería leer:

1. `AGENTS.md`
2. `agent_skills/README.md`
3. `agent_skills/shared/datagastro_modelo_informes.md`
4. `agent_skills/shared/datagastro_proyectos_cortos.md` si el proyecto es una encuesta,
   formulario, relevamiento exploratorio o informe corto.
5. `agent_skills/shared/datagastro_reporte_formulario.md` si hay Google Forms, XLSX/CSV de
   respuestas, PDF/DOCX de preguntas o gráficos exportados del formulario.
6. `agent_skills/shared/datagastro_qa_privacidad.md` antes de cerrar outputs públicos,
   informes, packs, DOCX o PDF.
7. La skill importada que corresponda en `agent_skills/claude_imported/` cuando el trabajo toque
   privacidad, fuentes, pipeline, geodatos o limpieza.

## Archivos que no se deben tocar sin pedido explícito

- Datos fuente originales: XLSX, CSV crudos, PDFs fuente, formularios y archivos internos.
- `.env`, credenciales, API keys y cualquier configuración sensible.
- `data/processed/`, `data/analytics/`, `src/build_model.py`, `src/build_analytics.py`,
  `src/validate_model.py`, `dashboard/`, `notebooks/` e informes finales del pipeline general.
- Carpetas de proyectos ya cerrados como `MercadosGastro/`, `CasasDePastas/` y `Cafesito/`,
  salvo documentación explícita de estándares.
- Google Drive y rutas internas/crudas: solo lectura, nunca escritura o limpieza automática.

## Privacidad

No exponer correos, teléfonos, nombres de personas, CUIT, DNI, direcciones individuales,
identificadores técnicos, links privados, montos/transacciones individuales ni API keys.
Los outputs publicables deben usar agregados, umbrales, redacción prudente y advertencias de
limitación. Separar siempre fuentes internas/crudas de entregables públicos.

## Git

No hacer commit, push ni `git add .` sin pedido explícito. Antes de cerrar, reportar archivos
creados/modificados y confirmar si se tocaron datos fuente.
