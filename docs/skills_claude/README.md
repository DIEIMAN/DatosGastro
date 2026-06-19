# Skills internas de DataGastro para Claude Code

Esta carpeta contiene la **documentación operativa** del proyecto DataGastro: el conjunto de
reglas, criterios y procedimientos que cualquier asistente (Claude Code u otro) debe seguir
para trabajar este repositorio de forma **consistente y segura**.

No es documentación de producto ni de pipeline (eso vive en `docs/` y `README.md`). Es
documentación de *cómo se trabaja*, pensada para reducir errores destructivos, fugas de datos
sensibles y conclusiones metodológicamente incorrectas.

## Índice

| Archivo | Tema | Cuándo aplicarlo |
| --- | --- | --- |
| `01_datagastro_guardrails.md` | Reglas permanentes y límites duros | Siempre, antes de cualquier acción |
| `02_metodologia_fuentes.md` | Clasificación y ficha de fuentes (F/I/E) | Al sumar, describir o priorizar una fuente |
| `03_privacidad_datos_sensibles.md` | Manejo de datos personales y sensibles | Al perfilar o exportar cualquier dato interno |
| `04_pipeline_reproducible.md` | Cómo trabajar sin romper el pipeline | Al tocar `src/`, `data/processed`, `data/analytics`, tests |
| `05_geodatos_y_territorio.md` | Direcciones, comunas, lat/lon, sesgos | Al geocodificar o hacer análisis territorial |
| `06_fuentes_externas_privadas.md` | Google, delivery, pagos, redes | Al evaluar fuentes externas/privadas |
| `07_informes_ejecutivos.md` | Cómo redactar para jefatura | Al producir cualquier informe o resumen |
| `08_limpieza_archivos_locales.md` | Borrado seguro de archivos locales | Antes de borrar o mover archivos del proyecto |

## Cómo se "carga" esto en Claude Code

Hay tres niveles, de mayor a menor garantía de que Claude lo respete:

1. **`CLAUDE.md` en la raíz del repo (activo y garantizado).**
   Claude Code carga automáticamente `CLAUDE.md` en cada sesión. Ese archivo contiene un
   resumen ejecutable de los guardrails (Prioridad 0) y referencia a estos documentos. Es el
   mecanismo principal y siempre disponible en cualquier versión de Claude Code.

2. **`.claude/skills/` (skills de proyecto, según versión).**
   Las versiones recientes de Claude Code soportan skills de proyecto en
   `.claude/skills/<nombre>/SKILL.md` con frontmatter YAML (`name`, `description`). Se crearon
   wrappers ahí que apuntan a estos documentos. Si tu versión de Claude Code no los reconoce,
   no pasa nada: el contenido canónico vive en `docs/skills_claude/` y se carga vía `CLAUDE.md`.
   No dependas exclusivamente de `.claude/skills/`.

3. **Lectura directa.**
   Cualquier persona o agente puede abrir estos `.md` y seguirlos. Son la fuente de verdad.

> Regla de oro: si hay conflicto entre lo que parece conveniente y lo que dice
> `01_datagastro_guardrails.md`, **gana el guardrail**. Ante la duda, no se borra, no se mueve,
> no se publica: se pregunta.

## Versionado

Estos documentos se versionan junto con el repo. Si una regla cambia, se actualiza el archivo
correspondiente y se deja constancia en el commit. No se eliminan reglas sin aprobación explícita
del responsable del proyecto (Diego).
