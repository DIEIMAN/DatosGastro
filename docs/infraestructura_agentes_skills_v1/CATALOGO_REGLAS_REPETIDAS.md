# Catálogo de reglas repetidas en prompts y workflows

**Paquete:** `INFRAESTRUCTURA_AGENTES_SKILLS_V1`  
**Fecha:** 2026-07-11  
**Base:** auditoría de infraestructura + handoffs/QA/prompts de Polos, Cafecito, Mercados y capa `agent_skills`.  
**Estado:** extracción de evidencia local. No inventa reglas nuevas; las agrupa para skills futuras.

**Nota:** el pedido original de Parte 2 se cortó en el mensaje del usuario. Este documento cubre el núcleo observable en el repositorio; se puede ampliar con prompts pegados en chat que no estén versionados.

---

## 1. Cómo se extrajo

Fuentes prioritarias:

| Fuente | Qué aporta |
| --- | --- |
| `CLAUDE.md`, `AGENTS.md`, `docs/skills_claude/*` | Reglas “permanentes” |
| `agent_skills/shared/*` | Estándar de informes y QA privacidad |
| `docs/polos_gastro/experimentos/**/QA_FINAL_*.md` | Checklist de cierre experimental |
| Scripts con `PROTECTED` (híbrido v2, v2.1) | Superficies intocables + hashes |
| `PLAN_INTEGRACION_RESULTADOS_CODEX_FABLE.md` | Higiene multiagente |
| Handoffs Cafecito / evidencia documental | Formulario, privacidad, cross-tool |
| `docs/prompts_codex.md` y prompts de fases Polos | Frases repetidas en tareas puntuales |

Criterio de “repetida”: aparece en **≥2** líneas de trabajo o en un QA_FINAL que se copió entre paquetes.

---

## 2. Catálogo por familia

Cada ítem tiene:

- **ID** estable para referenciar desde skills/agentes  
- **Texto canónico corto** (para no re-pegar párrafos en cada prompt)  
- **Dónde ya vive** (si existe)  
- **Skill propuesta** (existente o a crear en V1)

### 2.1 Seguridad, Git y alcance

| ID | Regla | Dónde vive hoy | Skill propuesta |
| --- | --- | --- | --- |
| R-SEC-01 | No inventar datos, métricas, URLs, fuentes ni conclusiones | Guardrails, AGENTS, modelo informes | `datagastro-guardrails` (existente) |
| R-SEC-02 | No modificar datos fuente / XLSX-CSV originales | Guardrails, Cafecito, Polos | guardrails + proyectos cortos |
| R-SEC-03 | No tocar pipeline F01–F05 ni `src/build_*`, processed, analytics, dashboard, notebooks sin permiso | Guardrails, CLAUDE | `datagastro-pipeline` |
| R-SEC-04 | No commit / no push / no staging / no `git add .` sin pedido explícito | AGENTS, QA_FINAL Polos, handoffs | **Nueva:** `datagastro-git-higiene` (o sección de paquete) |
| R-SEC-05 | No instalar librerías; usar `.venv` existente | QA GPT-56, CLAUDE (venv) | **Nueva:** `datagastro-entorno-windows` |
| R-SEC-06 | No APIs, no Google Places, no descargas externas (salvo autorización explícita) | QA híbridos, guardrails fuentes externas | `datagastro-fuentes-externas` |
| R-SEC-07 | Drive solo lectura (`G:\My Drive`, shortcut-targets) | Guardrails | guardrails |
| R-SEC-08 | No borrar archivos; limpieza solo con plan + confirmación | Skill limpieza | `datagastro-limpieza` |
| R-SEC-09 | No sobrescribir `AGENTS.md` / `CLAUDE.md` / settings / skills sin auditoría | Pedido de esta infra + guardrail “confirmar destructivo” | **Nueva:** `datagastro-infra-agentes` (meta) |
| R-SEC-10 | Trabajar en carpetas nuevas; no pisar fases/paquetes cerrados | Handoffs Polos, scripts PROTECTED | **Nueva:** `datagastro-superficies-protegidas` |

### 2.2 Superficies protegidas (Polos y generalizables)

| ID | Regla | Evidencia | Skill propuesta |
| --- | --- | --- | --- |
| R-PROT-01 | No modificar Fase 25 oficial (docs/outputs/script generador) | `PROTECTED` v2/v2.1, QA_FINAL | `datagastro-superficies-protegidas` |
| R-PROT-02 | No modificar Fase 26 ni capas cartográficas asociadas | Idem | idem |
| R-PROT-03 | No modificar v1–v4.2 / resultados técnicos cerrados / v2.1 como base a pisar | Idem + QA v2.1 | idem |
| R-PROT-04 | Verificar integridad pre/post con SHA-256 de árbol protegido | Scripts híbridos, auditoría GPT-56 (48/48, 333, 386 archivos) | idem + script utilitario |
| R-PROT-05 | Marcar estado EXPERIMENTAL / NO OFICIAL cuando no es fase oficial | QA_FINAL repetidos | `datagastro-paquete-entregable` |

### 2.3 Privacidad y outputs publicables

| ID | Regla | Dónde vive | Skill propuesta |
| --- | --- | --- | --- |
| R-PRIV-01 | No exponer emails, teléfonos, nombres, CUIT, DNI, IDs técnicos, place_id, API keys, links privados Drive | guardrails, qa_privacidad, QA_FINAL | `datagastro-privacidad` + `datagastro_qa_privacidad` |
| R-PRIV-02 | Outputs públicos = agregados; crudos a carpetas ignoradas / internal | gitignore + skills | privacidad |
| R-PRIV-03 | Escaneo automático no reemplaza revisión humana | QA_FINAL | qa_privacidad |
| R-PRIV-04 | No commitear datos internos/privados | guardrails | privacidad + git-higiene |

### 2.4 Metodología de datos y lenguaje

| ID | Regla | Dónde vive | Skill propuesta |
| --- | --- | --- | --- |
| R-MET-01 | Separar universos F / I / E; no sumar como total único | guardrails, prompts_codex | metodologia-fuentes |
| R-MET-02 | No llamar “locales activos” a habilitaciones, oferta registrada, permisos | guardrails, informes | guardrails + informes |
| R-MET-03 | Separar: confirmado / inferido / pendiente / no encontrado | AGENTS (Cowork), modelo informes | informes + metodologia |
| R-MET-04 | Cada número con fuente, fecha de corte y universo | modelo informes, skill informes | informes |
| R-MET-05 | Lenguaje prudente: “identificados”, “orientativo”, “exploratorio” | modelo informes, guía lenguaje Polos | informes |
| R-MET-06 | Seeds no son datos reales; respetar `--strict-real` | CLAUDE | pipeline |
| R-MET-07 | Geometrías/buffers experimentales no son límites oficiales | QA híbridos, evidencia documental | geodatos + (Polos) skill territorial |

### 2.5 Informes y marca institucional

| ID | Regla | Dónde vive | Skill propuesta |
| --- | --- | --- | --- |
| R-INF-01 | Marca pública DGDGAS; DataGastro solo docs internos | CLAUDE, skill informes Claude ampliada, design system | **Unificar en skill informes** (hoy falta en copias Codex) |
| R-INF-02 | Portada: título + DGDGAS; sin fecha/versión/“borrador”/“documento interno” en piezas mostrables | skill informes Claude | informes (paridad) |
| R-INF-03 | Índice + secciones numeradas | skill informes Claude | informes |
| R-INF-04 | Metodología y fuentes al anexo; cuerpo expositivo | skill informes Claude | informes |
| R-INF-05 | Si hay `kpis_lock.json`, validar con `scripts/qa/validate_kpis.py` | CLAUDE, skill informes | informes + qa |
| R-INF-06 | Informar rutas absolutas de archivos producidos al cierre | skill informes Claude | paquete-entregable |
| R-INF-07 | Estructura base de informe (resumen → hallazgos → límites → pasos) | shared modelo informes | modelo informes |

### 2.6 QA de entregables

| ID | Regla | Dónde vive | Skill propuesta |
| --- | --- | --- | --- |
| R-QA-01 | PDF no está terminado sin renderizar y **mirar** páginas | skill qa-pdf, CLAUDE | `datagastro-qa-pdf` (**exportar a Codex**) |
| R-QA-02 | Usar `scripts/qa/pdf_check.py` con Python del venv | CLAUDE, qa-pdf | qa-pdf |
| R-QA-03 | PNG no blancos / páginas con texto | QA híbridos | qa-pdf + paquete |
| R-QA-04 | GeoJSON válidos / sin duplicados de rutas en ZIP | QA v2.1 | paquete-entregable |
| R-QA-05 | MANIFEST_ARCHIVOS con hashes y tamaños | Paquetes Polos recientes | paquete-entregable |
| R-QA-06 | QA_FINAL con checklist de controles | Casi todo experimento 2026-07 | paquete-entregable |
| R-QA-07 | ZIP íntegro (`testzip`) + metadata JSON opcional | GPT-56, consolidación editorial | paquete-entregable |

### 2.7 Multiagente y handoffs

| ID | Regla | Evidencia | Skill propuesta |
| --- | --- | --- | --- |
| R-MA-01 | No escribir en la carpeta de trabajo del otro agente | PLAN integración Codex↔Fable §8 | **Nueva:** `datagastro-trabajo-multiagente` |
| R-MA-02 | Consumir solo entregables finales con QA propio del productor | Idem | multiagente |
| R-MA-03 | Contradicción técnica no revierte sola una decisión firmada → nota + Diego | Idem §§3–8 | multiagente |
| R-MA-04 | Handoff en `docs/revisiones/` o del paquete al cortar sesión | CLAUDE Continuidad | multiagente + handoff template |
| R-MA-05 | El creador no audita y aprueba de forma definitiva su propio entregable | Pedido explícito de esta infra | multiagente (regla dura) |
| R-MA-06 | Agentes con permisos acotados (rutas + acciones) | Pedido de esta infra | contrato de agente |

### 2.8 Entorno técnico

| ID | Regla | Dónde vive | Skill propuesta |
| --- | --- | --- | --- |
| R-ENV-01 | Windows; PowerShell primario; `.venv/Scripts/python.exe` siempre | CLAUDE | entorno-windows |
| R-ENV-02 | Commits multilínea: here-string PowerShell o `-F archivo` | CLAUDE | git-higiene |
| R-ENV-03 | graphify para código; no para docs/informes | CLAUDE + hooks | (solo Claude; no forzar en Codex) |

### 2.9 Alcance por subproyecto (no re-litigar)

| ID | Regla | Dónde vive | Skill propuesta |
| --- | --- | --- | --- |
| R-SUB-01 | Casas de Pastas = pastas/fábricas; no restaurantes italianos genéricos | CLAUDE | **Nueva o anexo:** `datagastro-alcance-subproyectos` |
| R-SUB-02 | Mercados = gastronómicos; no minoristas genéricos | CLAUDE | idem |
| R-SUB-03 | Polos: no solo franquicias; Abasto = subzona Corrientes | CLAUDE | idem |
| R-SUB-04 | No tocar otros subproyectos sin pedido explícito | CLAUDE, AGENTS | idem |

### 2.10 Proyectos cortos / formularios (Cafecito y similares)

| ID | Regla | Dónde vive | Skill propuesta |
| --- | --- | --- | --- |
| R-FORM-01 | XLSX solo lectura; no modificar fuente | shared proyectos cortos / formulario | `datagastro_reporte_formulario` |
| R-FORM-02 | Diccionario de preguntas antes de afirmar resultados | proyectos cortos | idem |
| R-FORM-03 | Multi-respuesta: no partir categorías; % pueden >100% | proyectos cortos | idem |
| R-FORM-04 | No publicar respuestas abiertas identificables | qa_privacidad + formulario | privacidad + formulario |
| R-FORM-05 | Muestra exploratoria; no representatividad sin diseño muestral | modelo informes, Cafecito README | informes |

---

## 3. Mapa: regla → skill existente vs gap

### Cubierto hoy (con matices)

- Guardrails generales, pipeline, fuentes, geodatos, limpieza, privacidad base.  
- Modelo de informes y proyectos cortos en `agent_skills/shared/`.  
- QA PDF **solo en Claude**.

### Gaps claros (aparecen todo el tiempo en prompts y no están como skill compartida)

| Gap | Por qué duele |
| --- | --- |
| Superficies protegidas + hashes | Se reescribe `PROTECTED = [...]` en cada script/prompt |
| Paquete entregable (MANIFEST + QA_FINAL + ZIP + metadata) | Casi idéntico entre experimentos |
| Trabajo multiagente / handoff / no auto-aprobar | Codex↔Fable ya opera sin skill formal |
| Paridad Claude–Codex de plantilla DGDGAS + QA PDF | Divergencia de copias |
| Git higiene unificada | Repetida en todo QA_FINAL |
| Entorno Windows/venv | Fuerte en CLAUDE, débil en AGENTS |
| Alcance subproyectos | Solo en CLAUDE |

---

## 4. Texto “mínimo reutilizable” (candidatos a skill)

Estos bloques son los que hoy se pegan enteros en prompts. En V1 deberían reducirse a: *“Aplicar skills R-SEC, R-PROT, R-QA del catálogo”*.

### Bloque A — Higiene dura (casi universal 2026-07)

```text
No modificar datos fuente. No modificar Fase 25, Fase 26 ni resultados técnicos cerrados.
No APIs, no Google Places, no descargas, no instalar librerías.
No commit, no push, no staging, no git add .
Usar solo .venv/Scripts/python.exe.
Trabajar en carpetas nuevas del paquete. Cerrar con MANIFEST + QA_FINAL.
```

### Bloque B — Informe mostrable DGDGAS

```text
Marca DGDGAS (no DataGastro en entregable).
Portada sin fecha/versión/borrador/documento interno.
Índice y secciones numeradas. Metodología al anexo.
Lenguaje prudente; no “locales activos” sin base.
QA visual PDF obligatorio (pdf_check + mirar PNG).
Si hay kpis_lock.json, validate_kpis.
```

### Bloque C — Multiagente

```text
No escribir en la carpeta del otro agente.
Consumir solo entregables finales con QA.
Contradicciones → documentar y escalar a Diego.
El productor no aprueba en definitivo su propio paquete.
Dejar HANDOFF al cortar.
```

---

## 5. Frecuencia observada (cualitativa)

| Familia | Frecuencia en prompts recientes Polos | En Cafecito/Mercados | En pipeline general |
| --- | --- | --- | --- |
| R-SEC / R-PROT | Muy alta | Media | Alta (pipeline) |
| R-PRIV | Alta | Muy alta | Alta |
| R-MET | Alta | Alta | Muy alta |
| R-INF / R-QA PDF | Alta (oficina/PDF) | Alta | Media |
| R-MA | Alta (2026-07) | Baja | Baja |
| R-FORM | Baja | Muy alta | Baja |

---

## 6. Implicancia para el diseño V1

1. **No crear 30 skills micro:** agrupar en 5–8 skills nuevas de procedimiento + reutilizar las 9 Claude.  
2. **Prioridad de paridad Claude↔Codex:** informes (plantilla DGDGAS) + qa-pdf + compartido en `agent_skills/shared/`.  
3. **Prioridad de des-repetir prompts Polos:** superficies-protegidas + paquete-entregable + multiagente.  
4. **Agentes** deben listar IDs de reglas (R-\*) o skills, no reescribir el bloque A/B/C.  
5. **Prohibición de auto-aprobación** es regla de agente, no solo de skill de QA.

---

## 7. Próximos documentos del paquete (sugeridos)

| Documento | Contenido |
| --- | --- |
| `CONTRATO_SKILL.md` | Campos mínimos de una skill DataGastro |
| `CONTRATO_AGENTE.md` | Rol, skills, rutas permitidas, outputs, prohibiciones, handoff |
| `ARQUITECTURA_V1.md` | Ubicaciones finales candidatas + plan de promoción |
| `SKILLS_PROPUESTAS/*.md` | Borradores de skills nuevas (solo en este paquete) |
| `scripts/.../check_skills_parity.py` | Detectar divergencia entre copias |

---

## 8. Trazabilidad

- No se modificaron datos fuente, Fase 25/26, v2.1, PDFs oficiales ni skills productivas.  
- Sin commit/push/staging.  
- Este catálogo es **documental**; no activa plugins ni agentes.

*Fin del catálogo de reglas repetidas (Parte 2 — núcleo).*
