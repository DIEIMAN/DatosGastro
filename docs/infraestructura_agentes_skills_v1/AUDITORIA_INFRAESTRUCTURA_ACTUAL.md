# Auditoría de infraestructura actual — agentes y skills

**Proyecto:** DataGastro / DGDGAS  
**Paquete:** `INFRAESTRUCTURA_AGENTES_SKILLS_V1`  
**Fecha de auditoría:** 2026-07-11  
**Alcance:** inspección de convenciones existentes; sin modificación de datos fuente, PDFs finales, Fase 25/26, v2.1 técnico, paquetes cerrados, commits ni APIs.  
**Estado:** evidencia local del repositorio; no asume compatibilidad entre plataformas sin verificación.

---

## 1. Resumen ejecutivo

El repositorio ya tiene una **infraestructura parcial y funcional** de reglas y skills, nacida sobre todo para Claude Code y luego adaptada de forma imperfecta a Codex. No existe todavía un sistema unificado de **agentes especializados** (no hay `.claude/agents/`, ni definiciones de roles reutilizables con permisos acotados).

Hay **tres capas de skills** y **dos archivos raíz de instrucciones** que se solapan:

| Capa | Ruta | Rol observado |
| --- | --- | --- |
| Canónica (texto largo) | `docs/skills_claude/` | Fuente de verdad de procedimientos (8 docs) |
| Operativa Claude | `CLAUDE.md` + `.claude/skills/` | Resumen de sesión + wrappers skill |
| Operativa multiagente / Codex | `AGENTS.md` + `agent_skills/` | Estándar de informes + copias importadas |
| Espejo incompleto | `.agents/skills/` | Copia de skills; desfasada en 2 puntos |
| Vacío | `.codex/` | Carpeta reservada, sin contenido |
| Ausente | `.claude/agents/`, `agents/` | No hay agentes especializados versionados |

**Hallazgo central:** la lógica ya se piensa en “skills + guardrails + handoffs”, pero **no hay una sola fuente de verdad operativa** entre Claude y Codex, y hay **divergencias reales** entre copias de `SKILL.md`.

**Recomendación de arquitectura (síntesis):** no inventar un framework nuevo. Formalizar lo que ya funciona:

1. **Canónico largo** en `docs/skills_claude/` (y skills compartidas nuevas en `agent_skills/shared/` o docs del paquete v1).  
2. **Wrappers delgados** por plataforma (`.claude/skills/` para Claude; referencias en `AGENTS.md` / `agent_skills/` para Codex).  
3. **Agentes como adaptadores de rol** (definiciones en docs o `.claude/agents/` solo tras diseño), nunca como dueños de la lógica.  
4. **Paquete de prueba** solo en `docs|outputs|scripts/infraestructura_agentes_skills_v1/` hasta validar.

---

## 2. Estructura existente inspeccionada

### 2.1 Archivos raíz de instrucciones

| Archivo | Vigente | Quién lo carga | Observación |
| --- | --- | --- | --- |
| `CLAUDE.md` | Sí (tracked) | Claude Code (automático por sesión) | Guardrails Prioridad 0, entorno Windows/venv, QA PDF, handoffs, alcance por subproyecto, graphify |
| `AGENTS.md` | Sí (tracked) | Codex / agentes genéricos (convención del repo) | Reporting standard vía `agent_skills/`; reglas obligatorias; incluye bloque largo “Claude Cowork” (modelo de datos, fuentes prioritarias, oportunidades) |
| `.claude/settings.json` | Sí (tracked; hay cambios locales untracked en working tree) | Claude Code | Permissions: `ask` en git commit/push/add; hooks SessionStart (handoff reciente) y PreToolUse (graphify); plugins oficiales |
| `.claude/settings.local.json` | Local (gitignored globalmente) | Claude Code local | Allowlist de comandos; paths absolutos de usuario; **no reutilizar como skill** |

### 2.2 Skills Claude (wrappers)

Ubicación: `.claude/skills/<nombre>/SKILL.md`

| Skill | Presente | Notas |
| --- | --- | --- |
| `datagastro-guardrails` | Sí | Apunta a `docs/skills_claude/01_...` y resume checklist |
| `datagastro-metodologia-fuentes` | Sí | Wrapper |
| `datagastro-privacidad` | Sí | Wrapper |
| `datagastro-pipeline` | Sí | Wrapper |
| `datagastro-geodatos` | Sí | Wrapper |
| `datagastro-fuentes-externas` | Sí | Wrapper |
| `datagastro-informes` | Sí | **Versión ampliada** (plantilla DGDGAS, KPIs, QA PDF) |
| `datagastro-limpieza` | Sí | Wrapper |
| `datagastro-qa-pdf` | Sí | **Solo en `.claude/skills/`** |

### 2.3 Documentación canónica Claude

`docs/skills_claude/` (tracked):

| Archivo | Tema |
| --- | --- |
| `01_datagastro_guardrails.md` | Reglas permanentes |
| `02_metodologia_fuentes.md` | F/I/E |
| `03_privacidad_datos_sensibles.md` | Datos personales |
| `04_pipeline_reproducible.md` | No romper F01–F05 |
| `05_geodatos_y_territorio.md` | Territorio / densidades |
| `06_fuentes_externas_privadas.md` | Places, delivery, etc. |
| `07_informes_ejecutivos.md` | Redacción jefatura |
| `08_limpieza_archivos_locales.md` | Borrado seguro |
| `README.md` | Explica carga: `CLAUDE.md` > skills > lectura directa |

El propio README de skills declara que **no se debe depender exclusivamente de `.claude/skills/`**.

### 2.4 Capa multiagente / Codex

| Ruta | Contenido | Estado |
| --- | --- | --- |
| `agent_skills/README.md` | Inventario y uso recomendado por Codex | Vigente; **desactualizado** en detalle (dice `.agents/` sin contenido útil; hoy hay skills ahí) |
| `agent_skills/shared/` | Modelo informes, proyectos cortos, formulario, QA privacidad, índice Claude | Vigente y valioso |
| `agent_skills/claude_imported/` | Copia de 8 skills Claude (sin `qa-pdf`) | Instantánea; no es canónica |
| `agent_skills/codex/README.md` | Placeholder: “usar shared, no duplicar” | Mínimo |
| `.agents/skills/` | 8 skills (tracked) | Espejo parcial de Claude |
| `.codex/` | Vacío | Reservado, sin convención operativa |

### 2.5 Agentes especializados

| Ubicación esperada | Existe |
| --- | --- |
| `.claude/agents/` | **No** |
| `.agents/agents/` | **No** |
| `agents/` en raíz | **No** |
| Plugin `atomic-agents@claude-plugins-official` | Habilitado en `settings.json`; **sin definiciones de proyecto versionadas** |

Hay **roles de facto** en handoffs (Codex técnico vs Fable editorial; Claude web de revisión externa; prompts Codex de mapas/PDF), pero **no están codificados como agentes reutilizables**.

### 2.6 Prompts y documentación de trabajo

| Ruta | Uso |
| --- | --- |
| `docs/prompts_codex.md` | Prompts puntuales dashboard/notebook/PDF (antiguos; aún útiles como estilo) |
| `docs/fuentes_externas/prompt_codex_fuentes_externas.md` | Fuentes externas |
| `docs/polos_gastro/fase*/PROMPT_*.md` | Prompts de fases Polos |
| `docs/mercados_caba/*prompt*` | Perplexity / enriquecimiento mercados |
| `docs/revisiones/HANDOFF_*.md` | Continuidad entre sesiones (hook SessionStart) |
| Handoffs por subproyecto | Cafecito, Polos evidencia documental, clustering, etc. |

### 2.7 QA, manifests, hashes, privacidad, PDF

| Utilidad | Ruta | Rol demostrado |
| --- | --- | --- |
| QA visual PDF | `scripts/qa/pdf_check.py` + skill `datagastro-qa-pdf` | Render PNG + texto; obligatorio antes de dar PDF por terminado |
| KPIs lock | `scripts/qa/validate_kpis.py` | Evita drift de números canónicos |
| Templates informe | `scripts/shared/template_pdf_informe_dgdgas.py`, `style_tokens_dgdgas.py`, etc. | Design system operativo en código |
| Superficies protegidas + SHA-256 | p.ej. `PROTECTED` en `pipeline_hibrido_integracion_v21/construir_integracion_v21.py` y repeticiones v2 | Comparación pre/post de cientos de archivos |
| MANIFEST + QA_FINAL | Varios paquetes en `docs/polos_gastro/experimentos/*` | Cierre de entregable experimental |
| ZIP + hash + privacidad | Auditoría GPT-56, consolidación editorial, paquetes híbridos | Empaquetado revisable sin datos sensibles |
| QA privacidad (comandos) | `agent_skills/shared/datagastro_qa_privacidad.md` | Escaneo de emails, CUIT, place_id, AIza…, Drive links |

### 2.8 Git y protección de datos

`.gitignore` (entre otros):

- `.env`, datos internos, `outputs/**/*.pdf`, ZIPs, crudos Places, `Cafesito/`, espejos de finales, QA PNG regenerables, carpetas `interno/` de experimentos Places.
- `settings.local.json` ignorado por config global del usuario (no por el `.gitignore` del repo).

Reglas de Git en prompts y handoffs recientes (repetidas):

- No commit / no push / no staging / no `git add .` sin pedido explícito.
- Trabajar en carpetas nuevas; no pisar fases cerradas.
- Reportar archivos creados/modificados y si se tocaron fuentes.

---

## 3. Qué lee Claude vs qué lee Codex

### 3.1 Claude Code (verificado en repo)

Carga / convención documentada:

1. **`CLAUDE.md`** (automático).  
2. **`.claude/settings.json`** (+ local).  
3. **`.claude/skills/*/SKILL.md`** (si la versión de Claude Code las reconoce).  
4. Hook SessionStart → handoff más reciente en `docs/revisiones/HANDOFF_*.md`.  
5. Contenido canónico largo en **`docs/skills_claude/`** (vía referencias).  
6. graphify para código (`scripts/`, `src/`), no para docs de informes.

Claude **no** está obligado por código a leer `AGENTS.md` ni `agent_skills/`, aunque un humano o prompt puede pedirlo.

### 3.2 Codex (convención del repo, no runtime verificado aquí)

Según `AGENTS.md` y `agent_skills/README.md`, debería leer:

1. `AGENTS.md`  
2. `agent_skills/README.md`  
3. `agent_skills/shared/*` según tipo de informe  
4. `agent_skills/claude_imported/*` cuando toque guardrails/pipeline/etc.  

**No verificado en este entorno:** carga automática de `.codex/` o de `.agents/skills/` por el runtime de Codex. La carpeta `.codex/` está vacía. Por lo tanto **no se debe asumir paridad automática Claude ↔ Codex**.

### 3.3 Grok / otros

No hay adaptador versionado específico. Operan con las instrucciones de sesión del entorno y, si se les indica, con `AGENTS.md` / `CLAUDE.md`. Esta auditoría no inventa compatibilidad.

---

## 4. Comparación de copias de skills (hashes)

Comparación SHA-256 (12 hex) al 2026-07-11:

| Skill | `.claude/skills` | `.agents/skills` | `agent_skills/claude_imported` |
| --- | --- | --- | --- |
| fuentes-externas | BC70EDBAE6A7 | idéntico | idéntico |
| geodatos | BBA09CAE15A5 | idéntico | idéntico |
| limpieza | ED8FFB1680E1 | idéntico | idéntico |
| metodologia-fuentes | 87BE4E28B5C3 | idéntico | idéntico |
| pipeline | 0780E76FA76C | idéntico | idéntico |
| privacidad | 54DCD2816C76 | idéntico | idéntico |
| **guardrails** | 287193CCB154 | **33B59F9FE52C** (difiere) | 287193CCB154 (= claude) |
| **informes** | **2E9519B1A0CF** (2212 B, ampliada) | F55F622CD03F (835 B) | F55F622CD03F (= agents) |
| **qa-pdf** | 72A694357623 | **MISSING** | **MISSING** |

### Divergencias concretas

1. **`datagastro-guardrails`:** Claude e importadas dicen “resumen en `CLAUDE.md`”; `.agents` dice “resumen en `AGENTS.md`”. Misma checklist; referencia distinta.  
2. **`datagastro-informes`:** solo `.claude` incluye “Plantilla institucional DGDGAS” (marca, portada sin fecha/versión/borrador, índice, KPIs lock, QA PDF, rutas absolutas al cierre). Las copias agents/importadas **no** tienen esos defaults.  
3. **`datagastro-qa-pdf`:** skill operativa reciente **solo** en Claude; Codex no la tiene en su árbol importado.

**Consecuencia:** un agente Claude y un agente Codex pueden producir informes con **criterios de portada y QA distintos** si solo leen su copia local de skills.

---

## 5. Convenciones que ya demostraron funcionar

Extraídas de Polos (Fase 25, híbrido, v2, v2.1, auditoría GPT-56, consolidación editorial), Cafecito y Mercados:

### 5.1 Separación de roles (de facto)

- **Técnico (Codex u otro):** scripts en carpetas nuevas, geometrías, métricas, QA de integridad.  
- **Editorial (Fable/Claude):** lenguaje, arquitectura de informe, matrices de ajuste, integración con decisiones de Diego.  
- **Higiene entre agentes** (`PLAN_INTEGRACION_RESULTADOS_CODEX_FABLE.md` §8): no escribir en la carpeta del otro; consumir solo entregables finales con QA; contradicciones → Diego, no auto-revertir.

### 5.2 Superficies protegidas con hash

Patrón reutilizado en scripts híbridos:

- Lista `PROTECTED` de rutas (Fase 25, Fase 26, v1–v4.2, paquetes previos).  
- `sha256` pre y post.  
- QA_FINAL declara “N archivos protegidos; 0 cambios”.

### 5.3 Paquete de entrega experimental

Casi siempre:

- `docs/<proyecto>/...` documentación + `MANIFEST_ARCHIVOS.md` + `QA_FINAL_*.md`  
- `outputs/<proyecto>/...` artefactos + a veces ZIP + metadata JSON  
- `scripts/<proyecto>/...` generadores  
- Estado **EXPERIMENTAL / NO OFICIAL** cuando no es fase oficial  
- Sin commit/push/staging

### 5.4 Lenguaje institucional

- Marca pública **DGDGAS**, no DataGastro en entregables.  
- “Oferta registrada / activos identificados”, no “locales activos” sin base.  
- Separar hallazgo / límite / pendiente de validación.  
- Universos F/I/E no sumables.

### 5.5 Continuidad

- `docs/revisiones/HANDOFF_*.md` + handoffs locales por paquete.  
- Hook SessionStart en Claude apunta al handoff más reciente.

### 5.6 Python del proyecto

- Siempre `.venv/Scripts/python.exe` (documentado en `CLAUDE.md`; Microsoft Store pisa `python`).

### 5.7 Privacidad por defecto

- No filas individuales sensibles en outputs publicables.  
- Escaneo de patrones + revisión humana.  
- Crudos Places / formularios fuera de Git.

---

## 6. Duplicaciones e inconsistencias

| Tema | Dónde se repite | Riesgo |
| --- | --- | --- |
| Guardrails | `CLAUDE.md`, `docs/skills_claude/01`, wrappers skill ×3, `AGENTS.md` (parcial), prompts de cada fase | Drift si se actualiza un solo lugar |
| No inventar datos / no sumar F01+F02 | skills, prompts Codex, modelo informes, prompts Polos | Bajo si se mantiene tono; alto si se acorta mal |
| Marca DGDGAS y portada | `CLAUDE.md` alcance, skill informes Claude ampliada, design system, prompts PDF | **Alto:** Codex no tiene la plantilla ampliada en su skill |
| QA PDF | `CLAUDE.md`, skill qa-pdf, skill informes Claude, consolidación editorial | Codex puede omitir si no lee Claude |
| Python venv | `CLAUDE.md` fuerte; `AGENTS.md` no lo enfatiza igual | Errores de entorno en Codex |
| Pipeline F01–F05 intocable | guardrails + AGENTS + casi todo handoff Polos | Bajo (muy repetido) |
| `agent_skills/README` vs realidad | README dice `.agents` sin contenido útil | Confusión de onboarding |
| `AGENTS.md` bloque Cowork largo | Modelo de datos y estructura `gastronomia_caba/` del ZIP inicial | Puede desalinearse con estructura actual del monorepo |
| Plugins Claude (`atomic-agents`, skill-creator) | settings | Habilitan capacidades experimentales globales del IDE; **no documentados en docs de proyecto** |

---

## 7. Qué está desactualizado o incompleto

1. **`agent_skills/claude_imported/`** no refleja `datagastro-qa-pdf` ni la plantilla DGDGAS de informes.  
2. **`.agents/skills/datagastro-informes`** desfasado respecto de `.claude`.  
3. **`agent_skills/README.md`** inventario de `.agents/` desactualizado.  
4. **`.codex/`** vacío: no hay adapter Codex real.  
5. **Sin agentes especializados** pese a división Codex/Fable ya operativa en Polos.  
6. **`docs/prompts_codex.md`** orientado a dashboard/notebook del pipeline general; no al patrón experimental de Polos 2026-07.  
7. **Handoff general 2026-07-02** superado en parte por trabajo Polos/Cafecito posterior; el más reciente en `docs/revisiones/` al auditar es consolidación editorial Polos 2026-07-11.

---

## 8. Qué no debe tocarse (líneas rojas de esta infraestructura)

Sin pedido explícito de Diego y fuera del alcance de este paquete v1:

| Superficie | Motivo |
| --- | --- |
| Datos fuente (`data/raw`, XLSX/CSV originales, Drive) | Guardrails + regla de no modificar fuentes |
| Pipeline F01–F05: `src/build_*`, `data/processed`, `data/analytics`, `dashboard/`, `notebooks/` | Guardrail pipeline |
| Fase 25 oficial y generador asociado | Paquetes cerrados / protegidos en scripts |
| Fase 26 y comparativas cartográficas asociadas | Idem |
| Resultados técnicos v2.1 y repeticiones v2 (como insumos cerrados a pisar) | Idem; se leen, no se reescriben |
| PDFs finales / packs de oficina ya cerrados | Entregables oficiales |
| `.env`, credenciales, crudos Places | Privacidad / secretos |
| Sobrescritura ciega de `AGENTS.md`, `CLAUDE.md`, `.claude/settings.json`, skills existentes | Pedido explícito de esta auditoría: solo con auditoría previa y cambios chicos |
| Google Drive en escritura | Solo lectura |
| Commit / push / staging / `git add .` | Convención del proyecto |

**Este paquete solo escribe en:**

- `docs/infraestructura_agentes_skills_v1/`  
- `outputs/infraestructura_agentes_skills_v1/`  
- `scripts/infraestructura_agentes_skills_v1/`  

hasta que se apruebe una ubicación operativa definitiva de skills/agentes.

---

## 9. Riesgos

| ID | Riesgo | Severidad | Mitigación propuesta |
| --- | --- | --- | --- |
| R1 | Tres copias de skills divergen | Alta | Una canónica + wrappers; script de verificación de paridad |
| R2 | Codex sin skill QA PDF / plantilla DGDGAS | Alta | Compartir procedimiento en `agent_skills/shared/` y reimportar con control |
| R3 | Agente “todo poderoso” sin límites | Alta | Roles con alcance de rutas y prohibiciones; no auto-aprobar su propio entregable |
| R4 | Plugins Claude experimentales no documentados | Media | Documentar `enabledPlugins` y cuándo se usan |
| R5 | Handoffs y prompts repiten 40 reglas cada vez | Media | Skills de procedimiento + prompts cortos que las invocan |
| R6 | Asumir que `.agents` o `.codex` se cargan solos | Media | Probar en runtime real antes de declarar soporte |
| R7 | Tocar fases/protegidos por error en trabajo paralelo | Alta | Mantener patrón `PROTECTED` + carpetas nuevas por paquete |
| R8 | `settings.local.json` con paths personales / pip install | Media | No versionar; no copiar a skills |
| R9 | Confundir marca DataGastro vs DGDGAS en outputs | Media | Skill informes unificada |
| R10 | Duplicar lógica en agentes Claude y prompts Codex | Alta | Agentes = adaptadores; skills = lógica |

---

## 10. Oportunidades

1. **Formalizar el patrón de paquete** (docs + outputs + scripts + MANIFEST + QA_FINAL + handoff) como skill `datagastro-paquete-entregable`.  
2. **Skill de superficies protegidas / hashes** reutilizable fuera de scripts sueltos de Polos.  
3. **Skill de trabajo multiagente** (quién escribe dónde; handoff; no auto-aprobar).  
4. **Roles acotados** alineados a trabajo real:  
   - auditor de infraestructura / integridad  
   - analista técnico espacial  
   - redactor institucional / PDF  
   - QA privacidad + visual  
   - integrador de handoffs  
5. **Paridad Claude–Codex** vía índice único y check de hashes.  
6. **Reducir prompts Polos** a: objetivo + rutas + “aplicar skills X/Y/Z”.  
7. **Usar Polos como caso de prueba** sin acoplar la infraestructura solo a Polos (skills genéricas DataGastro).  
8. **No reescribir** `AGENTS.md`/`CLAUDE.md` en el primer paso: solo documentar y proponer diffs mínimos después de aprobación.

---

## 11. Recomendación de arquitectura V1

### 11.1 Principio

```text
                    ┌─────────────────────────────┐
                    │  Canónico (una sola lógica) │
                    │  docs/skills_claude/*       │
                    │  agent_skills/shared/*      │
                    │  (+ skills nuevas en docs   │
                    │   del paquete hasta promover)│
                    └─────────────┬───────────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              ▼                                       ▼
   Wrappers Claude                          Adapter Codex
   .claude/skills/*/SKILL.md                AGENTS.md +
   CLAUDE.md (resumen)                      agent_skills/*
              │                                       │
              └───────────── Agentes-rol ─────────────┘
                     (definiciones de alcance;
                      no dueños de la lógica)
```

### 11.2 Dónde poner cosas (propuesta; no implementada aún)

| Artefacto | Ubicación V1 (propuesta) | Cuándo promover a producción |
| --- | --- | --- |
| Diseño, catálogo, contratos de agentes | `docs/infraestructura_agentes_skills_v1/` | Tras prueba en Polos + 1 informe corto |
| Skills nuevas en borrador | mismo docs o `agent_skills/shared/` solo si se aprueba copiar | Tras paridad verificada |
| Scripts de verificación (hashes skills, checklist) | `scripts/infraestructura_agentes_skills_v1/` | Cuando el check sea estable |
| Outputs de prueba | `outputs/infraestructura_agentes_skills_v1/` | Nunca mezclar con packs oficiales |
| Skills Claude productivas | `.claude/skills/` | Solo sync controlada post-auditoría |
| Skills agents/Codex | `.agents/skills/`, `agent_skills/claude_imported/` | Sync desde canónico, no edición divergente |
| Agentes Claude | `.claude/agents/` **solo si** se confirma soporte real de la versión en uso | Tras piloto |
| Codex runtime | `.codex/` o instrucciones en `agent_skills/codex/` | Tras confirmar qué lee Codex en este entorno |

### 11.3 Skills vs agentes

| | Skills | Agentes |
| --- | --- | --- |
| Qué son | Procedimientos verificables reutilizables | Roles con misión, inputs, outputs, prohibiciones |
| Dónde vive la lógica | Skills / docs canónicos | Adaptadores que **invocan** skills |
| Ejemplo | QA PDF, privacidad, paquete, protegidos | “Redactor informe”, “Auditor de integridad” |
| Prohibición | — | No auditar y aprobar de forma definitiva su propio entregable |

### 11.4 Orden de implementación sugerido (post-auditoría)

1. Extraer **reglas repetidas** de prompts recientes → catálogo (Parte 2).  
2. Diseñar **contrato de skill** y **contrato de agente** (campos mínimos).  
3. Redactar skills nuevas solo como docs en este paquete (sin tocar `.claude` aún).  
4. Script de **auditoría de paridad** entre las tres copias de skills.  
5. Piloto en Polos (tarea chica, carpeta nueva) con 2 roles (técnico + QA).  
6. Solo entonces proponer diffs mínimos a `CLAUDE.md` / `AGENTS.md` / wrappers.

### 11.5 Lo que esta V1 **no** hace

- No reemplaza el pipeline F01–F05.  
- No redefine Fase 25 política.  
- No instala plugins ni librerías.  
- No habilita Google Places.  
- No unifica a la fuerza runtimes sin prueba.

---

## 12. Inventario de archivos vigentes (skills e instrucciones)

### Tracked (git ls-files, muestra relevante)

- `AGENTS.md`, `CLAUDE.md`
- `.claude/settings.json`
- `.claude/skills/**` (9 skills, incluye `datagastro-qa-pdf`)
- `.agents/skills/**` (8 skills)
- `agent_skills/**` (README, codex placeholder, shared ×5, claude_imported ×8)
- `docs/skills_claude/**` (9 archivos)

### Local / no versionar como skill

- `.claude/settings.local.json`
- `.env`
- Outputs PDF/ZIP/QA PNG (gitignore)

### Carpetas vacías o solo reservadas

- `.codex/` (vacía al auditar)

---

## 13. Handoffs y workflows recientes relevantes

| Artefacto | Fecha / línea | Aporte a la infraestructura |
| --- | --- | --- |
| `docs/revisiones/HANDOFF_CONSOLIDACION_EDITORIAL_POLOS_2026_07_11.md` | Editorial + Codex en paralelo | División de trabajo, no tocar F25/26 |
| `PLAN_INTEGRACION_RESULTADOS_CODEX_FABLE.md` | Integración multiagente | Protocolo de higiene entre agentes |
| `QA_FINAL_*` híbrido v2 / v2.1 / GPT-56 | Técnico | Checklist de QA reutilizable |
| `HANDOFF_EVIDENCIA_DOCUMENTAL_CODEX_CLAUDE.md` | Documental | Handoff cross-tool |
| Handoffs Cafecito tandas | Formulario + PDF | Skill de proyectos cortos + privacidad |
| `docs/mercados_caba/*` | Informe numerado | Estructura de docs por pasos |

---

## 14. Veredicto

| Pregunta | Respuesta |
| --- | --- |
| ¿Hay base para `INFRAESTRUCTURA_AGENTES_SKILLS_V1`? | **Sí.** Guardrails, skills, shared, QA y patrones de paquete ya existen. |
| ¿Se puede copiar un sistema genérico de afuera? | **No recomendable.** Contradiría convenciones Polos/DataGastro ya probadas. |
| ¿Claude y Codex son el mismo sistema hoy? | **No.** Comparten intención y parte del texto; divergen en skills críticas (informes, QA PDF) y en mecanismo de carga. |
| ¿Hay agentes especializados listos? | **No.** Solo roles de facto en handoffs. |
| ¿Se puede tocar `.claude` / `AGENTS.md` ya? | **Solo con diffs mínimos post-diseño y aprobación.** Esta fase se limita a docs/outputs/scripts del paquete v1. |

---

## 15. Próximo paso inmediato

1. Completar **Parte 2**: catálogo de instrucciones repetidas en prompts/workflows (Polos F25, híbrido, v2/v2.1, GPT-56, Cafecito, Mercados, evidencia Grok si aplica).  
2. Mapear cada repetición a skill existente o skill nueva propuesta.  
3. No promover skills a `.claude/` ni `.agents/` hasta tener contrato y script de paridad.

---

## 16. Trazabilidad de esta auditoría

| Acción | Detalle |
| --- | --- |
| Lectura | `AGENTS.md`, `CLAUDE.md`, `.claude/settings*.json`, árboles `.claude/skills`, `.agents/skills`, `agent_skills`, `docs/skills_claude`, `.gitignore`, scripts QA, handoffs y QA_FINAL Polos/Cafecito |
| Escritura | Solo `docs/infraestructura_agentes_skills_v1/`, `outputs/...`, `scripts/...` |
| Datos fuente | No modificados |
| Fase 25/26 / v2.1 / PDFs oficiales | No modificados |
| Commit / push / staging | No ejecutados |
| APIs / Places / descargas / installs | No ejecutados |

*Fin de la auditoría de infraestructura actual.*
