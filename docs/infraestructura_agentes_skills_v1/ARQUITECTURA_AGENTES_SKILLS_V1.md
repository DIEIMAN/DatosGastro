# Arquitectura agentes y skills V1

**Paquete:** `INFRAESTRUCTURA_AGENTES_SKILLS_V1`  
**Fecha:** 2026-07-11  
**Base:** `AUDITORIA_INFRAESTRUCTURA_ACTUAL.md`  
**Principio:** una fuente canónica de procedimientos; adaptadores pequeños por plataforma; **sin symlinks** (evitar problemas en Windows y clones).

---

## 1. Objetivos

1. Reducir prompts repetitivos (matriz + política + skills).  
2. Mejorar consistencia Claude Code ↔ Codex ↔ otros.  
3. Permitir trabajo paralelo con handoffs.  
4. Preservar seguridad, trazabilidad y calidad DataGastro.  
5. Servir a Polos (caso de prueba principal) sin acoplarse solo a Polos.

---

## 2. Separación skills vs agentes

| | Skills | Agentes |
| --- | --- | --- |
| Naturaleza | Procedimientos verificables | Roles con misión y límites |
| Lógica | Canónica, compartida | Adaptador: elige skills, no redefine reglas |
| Output | Artefactos + checklist | Handoff al siguiente rol |
| Prohibición clave | — | No auto-aprobar en definitivo su propio entregable |

---

## 3. Capas y ubicaciones

### 3.1 Canónico (fuente de verdad de procedimientos)

| Contenido | Ubicación V1 | Notas |
| --- | --- | --- |
| Política corta transversal | `docs/infraestructura_agentes_skills_v1/POLITICA_OPERATIVA_DATAGASTRO.md` | Referenciada por todo |
| Matriz de reglas | `.../MATRIZ_REGLAS_REUTILIZABLES.md` | IDs R-* |
| Skills V1 (borrador controlado) | `.../skills/<nombre>/SKILL.md` | Formato frontmatter compatible Claude |
| Agentes V1 (definiciones) | `.../agents/<rol>.md` | Independientes del runtime |
| Guardrails y metodología largos ya existentes | `docs/skills_claude/` | No se reescriben en V1 |
| Estándares de informe ya existentes | `agent_skills/shared/` | Se referencian |

**Promoción futura (solo con auditoría y aprobación):**

- Wrappers delgados hacia `.claude/skills/` (Claude).  
- Copia controlada a `agent_skills/claude_imported/` y/o `.agents/skills/`.  
- **No** symlinks; copia versionada + script de paridad.

### 3.2 Adaptador Claude Code

| Pieza | Rol |
| --- | --- |
| `CLAUDE.md` | Resumen Prioridad 0 + punteros; **no** duplicar skills enteras |
| `.claude/skills/*/SKILL.md` | Wrappers cortos → canónico (hoy: skills productivas existentes) |
| `.claude/agents/` | **Vacío hoy.** Candidato futuro: copiar definiciones desde `docs/.../agents/` en formato que soporte la versión de Claude |
| `.claude/settings.json` | Permissions (ask en git add/commit/push), hooks handoff/graphify; **no** meter lógica de negocio |
| `.claude/settings.local.json` | Solo local; gitignored; no es skill |

**Activación Claude:** skill por `name`/`description` en frontmatter; lectura explícita de política/skills del paquete V1 mientras no estén promovidas.

**Fallback Claude:** si no carga `.claude/skills/`, rige `CLAUDE.md` + `docs/skills_claude/` + lectura directa de este paquete.

### 3.3 Adaptador Codex / multiagente

| Pieza | Rol |
| --- | --- |
| `AGENTS.md` | Entrada Codex: reglas + puntero a `agent_skills/` y, en V1, a este paquete |
| `agent_skills/README.md` + `shared/` + `claude_imported/` | Capa actual multi-tool |
| `agent_skills/codex/` | Instrucciones específicas Codex (hoy mínimo) |
| `.codex/` | Reservado; vacío; **no asumir** carga automática sin prueba |
| `.agents/skills/` | Espejo parcial actual (con drift); no editar en divergencia |

**Activación Codex:** por convención de `AGENTS.md` (lectura ordenada). No hay runtime de agentes versionado en `.codex/` al 2026-07-11.

**Fallback Codex:** `AGENTS.md` + `agent_skills/shared/` + política V1 + skills en `docs/infraestructura_agentes_skills_v1/skills/` por ruta explícita.

### 3.4 Relación con AGENTS.md y CLAUDE.md

```text
POLITICA + MATRIZ + skills V1 + docs/skills_claude
                 │
     ┌───────────┴───────────┐
     ▼                       ▼
 CLAUDE.md (corto)      AGENTS.md (corto + reporting)
     │                       │
 .claude/skills           agent_skills/*
 (wrappers)               (shared + imported)
```

**V1 no sobrescribe** `AGENTS.md` ni `CLAUDE.md`. Solo propone, en un paso posterior opcional, un párrafo de puntero:

- Claude: “Infra agentes V1: `docs/infraestructura_agentes_skills_v1/`”.  
- Codex: idem en sección reporting standard.

### 3.5 Settings

| Setting | Qué puede hacer V1 | Qué no |
| --- | --- | --- |
| `.claude/settings.json` | Documentar plugins existentes; proponer ask-rules ya alineadas | No activar experimentales nuevos sin documentar |
| `settings.local.json` | Ignorar | No versionar paths de usuario |

Plugins ya habilitados (`atomic-agents`, `skill-creator`, etc.) se tratan como **capacidad del IDE**, no como fuente de verdad del proyecto.

---

## 4. Versionado

| Elemento | Esquema |
| --- | --- |
| Paquete | `INFRAESTRUCTURA_AGENTES_SKILLS_V1` (carpeta fija) |
| Política | `versión: 1.0` en el propio MD |
| Skill | frontmatter `name` + campo `version: 1` en cuerpo |
| Agente | campo `version: 1` en definición |
| Promoción a productiva | solo con checklist de paridad y aprobación Diego |

Cambios: preferir **añadir** skill/agente o subir versión menor; no reescribir silenciosamente.

---

## 5. Dependencias

### 5.1 Entre artefactos

```text
POLITICA_OPERATIVA_DATAGASTRO
        ↑
   todas las skills V1
        ↑
   todos los agentes V1
        ↑
   prompts de tarea / coordinador
```

### 5.2 Herramientas del repo (no instalar nuevas en V1)

| Uso | Herramienta |
| --- | --- |
| PDF QA | `.venv/Scripts/python.exe scripts/qa/pdf_check.py` |
| KPIs | `scripts/qa/validate_kpis.py` |
| Python | `.venv/Scripts/python.exe` |
| Hashes | `hashlib` en scripts del paquete o PowerShell `Get-FileHash` |

### 5.3 Skills productivas existentes

Las skills V1 **referencian** (no copian):

- `docs/skills_claude/01`…`08`  
- `.claude/skills/datagastro-*` cuando el runtime las tenga  
- `agent_skills/shared/*`

---

## 6. Activación por plataforma

| Paso | Claude Code | Codex | Otro |
| --- | --- | --- | --- |
| 1 | Carga `CLAUDE.md` | Carga `AGENTS.md` | Pedir política + matriz |
| 2 | Skills productivas si aplica | `agent_skills/*` | — |
| 3 | Leer política + skill/agente del paquete V1 por ruta | Igual | Igual |
| 4 | Ejecutar procedimiento | Igual | Igual |
| 5 | Handoff / QA | Igual | Igual |

**No symlinks.** Si hace falta “la misma skill” en dos lados: copiar archivo y correr verificación de hash (script futuro en `scripts/infraestructura_agentes_skills_v1/`).

---

## 7. Evitar divergencias entre copias

1. **Una canónica** en `docs/infraestructura_agentes_skills_v1/skills/` (V1) o `docs/skills_claude/` (legacy largo).  
2. Wrappers de ≤40 líneas que solo apuntan al canónico.  
3. Script de paridad (planificado): comparar SHA-256 de skills espejo.  
4. Prohibido editar solo `.agents/skills` o solo `claude_imported` “porque es más corto”.  
5. Índice de versión en `MATRIZ` / README del paquete cuando se promueva.

Estado actual (auditoría): drift real en `datagastro-informes` y ausencia de `datagastro-qa-pdf` fuera de Claude — V1 no lo “arregla” pisando productivos; lo documenta y ofrece skills de paquete.

---

## 8. Flujo de trabajo multiagente

```text
┌──────────┐
│ Usuario  │  (pedido + autorizaciones)
└────┬─────┘
     ▼
┌─────────────────┐
│ Coordinador     │  interpreta pedido, aplica POLITICA,
│                 │  elige especialista(s), fija rutas de paquete,
│                 │  lista reglas R-* y skills
└────┬────────────┘
     ▼
┌─────────────────┐
│ Especialista(s) │  investigador_documental |
│ en paralelo o   │  auditor_metodologico |
│ secuencia       │  cartografo_territorial |
│                 │  editor_institucional
│                 │  → cada uno usa skills + produce handoff
└────┬────────────┘
     ▼
┌─────────────────┐
│ Handoff         │  HANDOFF_*.md + rutas + pendientes +
│                 │  “qué no se tocó”
└────┬────────────┘
     ▼
┌─────────────────┐
│ Auditor QA      │  distinto del productor principal
│                 │  skills: git/protegidos, manifest, privacidad,
│                 │  PDF, KPIs, entregable experimental
└────┬────────────┘
     ▼
┌─────────────────┐
│ Entrega         │  pack sanitizado + QA_FINAL + manifest
│                 │  → revisión humana (Diego)
└─────────────────┘
```

### Reglas del flujo

1. El coordinador no ejecuta todo el trabajo técnico si hay especialista definido.  
2. Especialistas no se aprueban a sí mismos en definitivo.  
3. Auditor QA puede ser el mismo humano (Diego) o un agente distinto en otra sesión.  
4. Trabajo paralelo: carpetas exclusivas (R-MA-01).

---

## 9. Agentes V1 (inventario)

Definiciones en `docs/infraestructura_agentes_skills_v1/agents/`:

| Archivo | Rol |
| --- | --- |
| `coordinador.md` | Orquestación y despacho |
| `investigador_documental.md` | Evidencia y bibliografía |
| `auditor_metodologico.md` | Método, robustez, sobreinterpretación |
| `cartografo_territorial.md` | Capas y mapas |
| `editor_institucional.md` | Narrativa DGDGAS / informe |
| `auditor_qa.md` | Cierre, hashes, privacidad, PDF, git |

El mensaje de diseño del Editor institucional llegó truncado; la definición V1 se completó con el patrón del repo (informes, marca, QA PDF, no inventar cifras).

---

## 10. Skills V1 (inventario)

| Carpeta | Propósito breve |
| --- | --- |
| `skills/auditar_entregable_experimental/` | Cierre de experimento |
| `skills/qa_pdf_pagina_por_pagina/` | QA visual PDF |
| `skills/crear_paquete_revision_sanitizado/` | ZIP/pack limpio |
| `skills/auditar_git_y_archivos_protegidos/` | Git + PROTECTED |
| `skills/crear_manifest_hashes_metadata/` | Manifest + hashes |
| `skills/integrar_handoffs/` | Handoffs e integración |
| `skills/validar_metricas_y_kpis/` | Cifras y locks |
| `skills/transformar_cartografia_a_presentacion/` | Analítica → presentación |
| `skills/gestionar_decisiones_humanas/` | DEC/DH |
| `skills/auditar_evidencia_documental/` | Matrices evidencia |

---

## 11. Outputs y scripts del paquete

| Ruta | Uso |
| --- | --- |
| `docs/infraestructura_agentes_skills_v1/` | Diseño y definiciones |
| `outputs/infraestructura_agentes_skills_v1/` | Pruebas de packs (vacío de producto) |
| `scripts/infraestructura_agentes_skills_v1/` | Utilidades de paridad/verificación (cuando se agreguen) |

No se usan para datos de Polos/Cafecito reales salvo pruebas explícitas de la infra.

---

## 12. Criterios de éxito de la arquitectura V1

1. Un prompt de tarea puede limitarse a objetivo + rutas + lista de skills/agentes.  
2. Claude y Codex, leyendo la misma política y skills de docs, no divergen en reglas duras.  
3. Ningún agente escribe fuera de rutas permitidas.  
4. Todo cierre experimental deja manifest + handoff + limitaciones.  
5. No se requieren symlinks ni installs.

---

## 13. Qué queda fuera de V1

- Promoción automática a `.claude/skills` productivas.  
- Implementación nativa `.claude/agents` sin verificar versión de Claude.  
- Reescritura de `AGENTS.md` / `CLAUDE.md`.  
- Ejecución de Places o pipeline F01–F05.  
- Agentes con permisos amplios de escritura en todo el monorepo.

---

*Fin de la arquitectura V1.*
