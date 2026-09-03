# docs/ — índice

Qué hay en cada carpeta, qué está vigente y qué leer según la tarea. Actualizado 2026-09-03.

## Según la tarea

| Voy a… | Leer primero |
|---|---|
| Empezar una sesión | `revisiones/HANDOFF_ACTUAL.md` y el `ESTADO.md` del subproyecto |
| Tocar el pipeline F01–F05 | `skills_claude/04_pipeline_reproducible.md`, `general/GUIA_ejecucion_pipeline.md` |
| Sumar o describir una fuente | `skills_claude/02_metodologia_fuentes.md`, `general/contratos_fuentes.md`, `fuentes_externas/` |
| Abrir o tocar un rubro | `estudios_de_rubro/COMO_ABRIR_UN_RUBRO_NUEVO.md`, `estudios_de_rubro/LECTOR_FUENTES_LOCALES.md` |
| Geocodificar o hacer análisis territorial | `skills_claude/05_geodatos_y_territorio.md` |
| Recolectar de plataformas externas | `skills_claude/06_fuentes_externas_privadas.md` |
| Escribir un informe para jefatura | `skills_claude/07_informes_ejecutivos.md`, `datagastro_design_system/` |
| Borrar o mover archivos | `skills_claude/08_limpieza_archivos_locales.md` |
| Correr algo que produce un número | `../agent_skills/shared/datagastro_metodo_experimental.md` |

## Carpetas

| Carpeta | Contenido | Vigencia |
|---|---|---|
| `general/` | Diccionario de datos, contratos y perfilado de fuentes, guías del pipeline y del dashboard, CHANGELOG, criterios de limpieza, pendientes y limitaciones (todo de la V3, junio 2026). | Vigente como referencia del pipeline congelado. |
| `skills_claude/` | Las ocho reglas en detalle (01 guardrails … 08 limpieza). Las skills de `.claude/skills/` son sus checklists. | Vigente. |
| `estudios_de_rubro/` | Receta para abrir un rubro, lector de fuentes locales, comparación panaderías / pastas, acciones para Diego. | Vigente. |
| `revisiones/` | `HANDOFF_ACTUAL.md`, handoffs por hilo (`HANDOFF_<TEMA>_<fecha>.md`), auditorías del repo, planes de limpieza, settings propuestos. | Vigente; los handoffs viejos son historia útil. |
| `polos_gastro/` | `ESTADO.md`, README, `PROTECTED_SURFACES.yaml`, pedidos externos, fichas, y muchas subcarpetas de fases cerradas (junio–julio). | Solo `ESTADO.md`, README, PROTECTED_SURFACES y pedidos externos son vigentes; el resto es histórico y 189 archivos duplican `outputs/polos_gastro/historico/` (pendiente de decisión). |
| `panaderias/` | README con estado y cifras, alcance y definición, notas metodológicas, plan de trabajo. | Vigente (2026-08-28). |
| `casas_pastas/` | `ESTADO.md`; `historico_v4_2026-06/` (línea V4) y `revision_institucional_2026-07/`. | Solo `ESTADO.md` vigente. |
| `mercados_caba/` | Informe final markdown master, fichas (`fichas_v1_2/` vigente; `v0`, `v1` superadas), anexos, `revision_dgdgas_2026-07/`, `ESTADO.md`. Lo leen tres scripts de `src/mercados_caba/`. | Vigente. |
| `cafecito/` | `ESTADO.md`, cómo editar el informe, auditorías visuales, contenidos editables por tanda, handoffs de tandas 2–5. | Informe cerrado en julio; pet friendly abierto (2026-09). |
| `fuentes_externas/` | README, roadmap, checklist legal y metodológico, plan de limpieza del data pack, acciones para Diego. | Vigente. |
| `datagastro_design_system/` | Sistema de diseño DGDGAS que leen `scripts/shared/reporting_dgdgas/`. | Vigente. |
| `datagastro_v2/`, `datagastro_estandares/`, `encuestas/` | Documentación de `src/v2/`, estándares, plantilla de encuestas. | Vigente pero sin actividad reciente. |
| `infraestructura_agentes_skills_v1/`, `_v1_1/` | Política, ciclo de una pasada, catálogo de agentes y skills, adaptadores, evaluaciones. | Documentación congelada de un piloto (julio); el ciclo y las superficies protegidas siguen en uso. |
| `references/` | Un PDF de referencia. | — |
| `archive/` | `v3_2026-06/` (informe ejecutivo, presentación, prompts y propuesta de junio), `reorganizacion_2026-06/`, `v1/`, hotfix V1.1.1. | Histórico. |
| `legacy/` | Instrucciones Cowork supersedidas. | Histórico. |

## Convenciones

- Cada subproyecto tiene `docs/<sub>/ESTADO.md` con: fecha de corte, cifras canónicas con su
  unidad de conteo, qué está cerrado y qué abierto, ruta del entregable vigente, handoff más
  reciente, decisiones que esperan a Diego.
- Handoffs: `docs/revisiones/HANDOFF_<TEMA>_<AAAA_MM_DD>.md`; `HANDOFF_ACTUAL.md` lista los hilos
  abiertos. El hook de SessionStart elige por la fecha del nombre, no por mtime.
- Nada vigente se referencia por su ruta histórica: al mover una carpeta, grepear y parchear en el
  mismo commit (`scripts/qa/estado_repo.py` ayuda a ver qué quedó sin commit).
