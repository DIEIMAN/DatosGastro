# Matriz de reglas reutilizables

**Paquete:** `INFRAESTRUCTURA_AGENTES_SKILLS_V1`  
**Fecha:** 2026-07-11  
**Política común:** `POLITICA_OPERATIVA_DATAGASTRO.md`  
**Catálogo previo:** `CATALOGO_REGLAS_REPETIDAS.md`  
**Estado:** documental; no activa skills productivas en `.claude/` ni `.agents/`.

Leyenda:

- **obligatoria:** `sí` = no se omite en el alcance indicado; `condicional` = solo si aplica el tipo de entregable.
- **configurable:** `no` = fija; `parcial` = umbrales/rutas del paquete; `sí` = parámetros de tarea.
- **agente responsable:** rol principal; el coordinador siempre puede invocar la skill.

Todas las skills nuevas de esta matriz viven (borrador V1) en  
`docs/infraestructura_agentes_skills_v1/skills/<nombre>/SKILL.md`.

---

## Matriz

| regla_id | regla | alcance | proyectos donde aplica | skill candidata | agente responsable | obligatoria | configurable | riesgo si se omite | fuente dentro del repositorio |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R-FIN-01 | No tocar finales (PDFs oficiales, packs de oficina cerrados, fases oficiales publicables) | Entregables y fases cerradas | Polos, Cafecito, Mercados, Casas de Pastas, DataGastro general | `auditar_git_y_archivos_protegidos` | auditor_qa / coordinador | sí | parcial (lista PROTECTED del paquete) | Pisar material mostrable; pérdida de trazabilidad | `CLAUDE.md`; `docs/polos_gastro/experimentos/**/QA_FINAL_*.md`; scripts `PROTECTED` en híbrido v2/v2.1 |
| R-PAR-01 | Crear líneas paralelas (carpetas nuevas docs/outputs/scripts); no editar in-place lo cerrado | Cualquier experimento o tanda nueva | Todos | `auditar_entregable_experimental`; `crear_paquete_revision_sanitizado` | coordinador | sí | sí (nombre de paquete) | Contaminar baseline; imposible comparar versiones | Handoffs Polos; `PLAN_INTEGRACION_RESULTADOS_CODEX_FABLE.md` |
| R-SRC-01 | Proteger datos fuente (solo lectura; no modificar XLSX/CSV/PDF fuente) | Fuentes y crudos | Todos | `auditar_git_y_archivos_protegidos`; política común | todos | sí | no | Corrupción de evidencia; irreproducibilidad | `docs/skills_claude/01_datagastro_guardrails.md`; `agent_skills/shared/*` |
| R-CAP-01 | Separar capa analítica y de presentación (geometrías/métricas vs narrativa/PDF/mapas editoriales) | Cartografía e informes | Polos (prioridad), Mercados, futuros mapas | `transformar_cartografia_a_presentacion` | cartografo_territorial + editor_institucional | sí en cartografía | parcial | Presentar experimento como oficial; confusión de capas | Scripts/capas v4.x Polos; handoffs clustering; design system |
| R-KPI-01 | Validar cifras (conteos, KPIs lock, consistencia CSV/MD/PDF) | Informes y tablas | Todos con números canónicos | `validar_metricas_y_kpis` | auditor_metodologico / auditor_qa | sí si hay números | parcial (`kpis_lock.json`) | Drift de KPIs entre regeneraciones | `scripts/qa/validate_kpis.py`; skill `datagastro-informes` (Claude) |
| R-PDF-01 | Revisar PDF página por página (render + inspección visual) | Todo PDF generado | Todos con PDF | `qa_pdf_pagina_por_pagina` | editor_institucional / auditor_qa | sí si hay PDF | parcial (páginas, dpi) | Entregar PDF roto o no mostrable | `.claude/skills/datagastro-qa-pdf`; `scripts/qa/pdf_check.py`; `CLAUDE.md` |
| R-PRIV-01 | Preservar privacidad (sin PII, place_id, keys, links privados en publicables) | Outputs publicables y packs | Todos | `crear_paquete_revision_sanitizado` (+ `datagastro_qa_privacidad`) | auditor_qa | sí | no | Filtración de datos; incumplimiento guardrails | `docs/skills_claude/03_*`; `agent_skills/shared/datagastro_qa_privacidad.md` |
| R-HASH-01 | Verificar hashes (insumos y superficies protegidas pre/post) | Experimentos y packs | Polos (patrón maduro), extensible | `crear_manifest_hashes_metadata`; `auditar_git_y_archivos_protegidos` | auditor_qa | sí en packs experimentales | parcial (lista rutas) | No detectar alteraciones accidentales | `construir_integracion_v21.py` (`PROTECTED`+sha256); QA GPT-56 |
| R-MAN-01 | Generar manifest de archivos del paquete | Cierre de paquete | Todos experimentales | `crear_manifest_hashes_metadata` | auditor_qa / productor del paquete | sí en cierre | sí | Entrega incompleta o no auditable | `MANIFEST_ARCHIVOS.md` en experimentos Polos |
| R-ZIP-01 | Preparar ZIP sanitizado de revisión (sin crudos ni secretos) | Packs de revisión humana | Polos, auditorías, consolidaciones | `crear_paquete_revision_sanitizado` | auditor_qa | condicional | sí | Compartir material sensible o incompleto | `armar_paquete_revision.py` (GPT-56 y similares) |
| R-GIT-01 | No usar `git add .` | Git | Todos | `auditar_git_y_archivos_protegidos` | todos | sí | no | Staging masivo de secretos/outputs | `AGENTS.md`; `.claude/settings.json` (ask en git add) |
| R-GIT-02 | No commit ni push sin autorización explícita | Git | Todos | `auditar_git_y_archivos_protegidos` | todos | sí | no | Publicar trabajo no revisado | `AGENTS.md`; settings ask commit/push |
| R-DEC-01 | Separar decisiones técnicas y humanas | Análisis → informe | Polos (muy alta), otros | `gestionar_decisiones_humanas` | auditor_metodologico + editor; decide Diego | sí | no | “Promover” geometría a política sin firma | Matrices DEC/DH Polos; `REGISTRO_DECISIONES_*` |
| R-HO-01 | Producir handoffs al cortar o transferir | Continuidad multiagente | Todos | `integrar_handoffs` | coordinador / especialista saliente | sí en tareas largas o handoff | parcial | Pérdida de contexto entre sesiones/herramientas | `docs/revisiones/HANDOFF_*.md`; hook SessionStart Claude |
| R-LIM-01 | Documentar limitaciones y estado experimental | Informes y experimentos | Todos | `auditar_entregable_experimental`; política | editor_institucional / auditor_metodologico | sí | no | Sobreconfianza del lector | `agent_skills/shared/datagastro_modelo_informes.md`; QA_FINAL |
| R-EVI-01 | Distinguir evidencia, inferencia y decisión institucional | Texto y matrices | Polos, Mercados, evidencia documental | `auditar_evidencia_documental` | investigador_documental + editor | sí | no | Nota periodística leída como límite oficial | `docs/polos_gastro/evidencia_documental/*`; skill metodologia fuentes |
| R-MET-01 | No inventar resultados ni rellenar huecos como hechos | Todo análisis | Todos | política + `validar_metricas_y_kpis` | todos | sí | no | Datos falsos en gestión | Guardrails; `AGENTS.md` |
| R-MET-02 | Declarar incertidumbre real (cobertura, sesgo, n, no verificado) | Hallazgos | Todos | `auditar_entregable_experimental` | auditor_metodologico | sí | no | Decisiones sobre bases frágiles | Modelo informes; QA GPT-56 “no verificables” |
| R-MET-03 | Defender decisiones institucionales ya adoptadas sin reabrirlas por default | Texto y geometría de presentación | Polos prioritario | `gestionar_decisiones_humanas` | editor_institucional / cartografo | sí | no | Debilitar Belgrano/Recoleta/Costanera ya firmadas | `HANDOFF_EVIDENCIA_DOCUMENTAL_CODEX_CLAUDE.md` decisiones cerradas |
| R-UNI-01 | No mezclar universos F/I/E ni sumar como total único | Datos y KPIs | DataGastro general + todos | `validar_metricas_y_kpis` + metodologia existente | auditor_metodologico | sí | no | KPI engañoso | `docs/skills_claude/02_metodologia_fuentes.md` |
| R-LEN-01 | No llamar “locales activos” sin fuente que mida actividad | Redacción | Todos | editor usa política + informes | editor_institucional | sí | no | Error conceptual en jefatura | Guardrails #5; skill informes |
| R-MAR-01 | Marca pública DGDGAS; DataGastro solo docs internos | Entregables públicos | Informes PDF/DOCX | política + editor | editor_institucional | sí en publicables | no | Marca incorrecta | `CLAUDE.md`; skill informes Claude ampliada |
| R-MA-01 | No escribir en la carpeta de trabajo del otro agente | Paralelo multi-tool | Polos Codex↔Fable; extensible | `integrar_handoffs` | coordinador | sí en paralelo | sí (rutas) | Pisadas mutuas | `PLAN_INTEGRACION_RESULTADOS_CODEX_FABLE.md` §8 |
| R-MA-02 | El productor no aprueba en definitivo su propio entregable | Cierre | Todos con rol split | `auditar_entregable_experimental` | auditor_qa (distinto del productor) | sí | no | Sesgo de auto-aprobación | Pedido infra V1; política |
| R-API-01 | No APIs pagas / Places / scraping sin autorización | Fuentes externas | Polos Places, Casas, Mercados | política + skill fuentes externas existente | todos | sí | no | Costo, ToS, datos no autorizados | `docs/skills_claude/06_*`; QA_FINAL “Sin API” |
| R-ENV-01 | Python del venv del proyecto en Windows | Ejecución scripts | Todos con Python | política (ref) | todos | sí | no | Falla de paquetes / Python Store | `CLAUDE.md` Entorno |

---

## Mapa regla → skill V1 (resumen)

| skill V1 | reglas principales |
| --- | --- |
| `auditar_entregable_experimental` | R-PAR-01, R-LIM-01, R-MET-02, R-MA-02 |
| `qa_pdf_pagina_por_pagina` | R-PDF-01 |
| `crear_paquete_revision_sanitizado` | R-ZIP-01, R-PRIV-01, R-PAR-01 |
| `auditar_git_y_archivos_protegidos` | R-FIN-01, R-SRC-01, R-GIT-01, R-GIT-02, R-HASH-01 |
| `crear_manifest_hashes_metadata` | R-MAN-01, R-HASH-01 |
| `integrar_handoffs` | R-HO-01, R-MA-01 |
| `validar_metricas_y_kpis` | R-KPI-01, R-UNI-01, R-MET-01 |
| `transformar_cartografia_a_presentacion` | R-CAP-01 |
| `gestionar_decisiones_humanas` | R-DEC-01, R-MET-03 |
| `auditar_evidencia_documental` | R-EVI-01 |

Skills productivas ya existentes (no reescritas aquí): `datagastro-guardrails`, `datagastro-privacidad`, `datagastro-pipeline`, `datagastro-qa-pdf` (Claude), etc. Las skills V1 **referencian** la política y, cuando existan, las productivas; no las duplican.

---

## Agentes y reglas (cobertura)

| agente | reglas que “posee” en ejecución |
| --- | --- |
| `coordinador` | R-PAR-01, R-HO-01, R-MA-01, despacho |
| `investigador_documental` | R-EVI-01, R-MET-01 |
| `auditor_metodologico` | R-KPI-01, R-MET-02, R-UNI-01, R-DEC-01 (marco) |
| `cartografo_territorial` | R-CAP-01, R-HASH-01 (capas), R-MET-03 (no reabrir geometría firmada) |
| `editor_institucional` | R-INF/R-LEN/R-MAR, R-LIM-01, R-PDF-01 (con QA) |
| `auditor_qa` | R-FIN-01, R-PRIV-01, R-MAN-01, R-ZIP-01, R-GIT-*, R-MA-02 |

---

## Uso

1. En un prompt de tarea: listar `regla_id` aplicables o “aplicar matriz §X”.  
2. El agente carga `POLITICA_OPERATIVA_DATAGASTRO.md` + skills citadas.  
3. El auditor QA verifica la columna **obligatoria** antes de marcar entrega.

*Fin de la matriz.*
