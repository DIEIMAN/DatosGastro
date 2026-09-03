# Dependencias y portabilidad — V1.1.1 hotfix

## Qué contiene el ZIP de hotfix

El paquete `REVISION_INFRAESTRUCTURA_AGENTES_SKILLS_V1_1_1_HOTFIX.zip` incluye:

- Documentación de hotfix (este archivo, QA, metadata, esquema de cierre corregido).
- Evidencia Git (status, diffs de punteros e infra, cached vacío).
- Inventario `DEPENDENCIAS_REFERENCIADAS.csv` (29 filas de datos + cabecera).
- Copia de lectura de artefactos de revisión V1.1 **ya generados** (docs V1.1, scripts V1.1, salidas E2E/paridad) para trazabilidad del piloto.
- Scripts de este hotfix.
- `MANIFEST_CONTENIDO.csv` y `CHECKSUMS_INTERNO.txt` generados con orden de cierre correcto.

## Qué depende del repositorio (no está “cerrado” en el ZIP)

Las **skills y agentes canónicos de procedimiento** viven en:

- `docs/infraestructura_agentes_skills_v1/skills/`
- `docs/infraestructura_agentes_skills_v1/agents/`

La política y catálogo del piloto viven en:

- `docs/infraestructura_agentes_skills_v1_1/`

Los guardrails canónicos largos:

- `docs/skills_claude/`

Las skills productivas de Claude:

- `.claude/skills/`

Entradas de sesión:

- `AGENTS.md`, `CLAUDE.md`, `agent_skills/codex/README.md`

Scripts de QA del repo:

- `scripts/qa/validate_kpis.py`, `scripts/qa/pdf_check.py`

Insumos de casos E2E (solo lectura):

- packs Polos de evidencia e integración técnica en `outputs/polos_gastro/...`

## Qué es canónico (no se duplica)

| Capa | Canónico |
| --- | --- |
| Guardrails | `docs/skills_claude/` |
| Procedimientos skills piloto | `docs/infraestructura_agentes_skills_v1/skills/` |
| Política piloto | `docs/infraestructura_agentes_skills_v1_1/POLITICA_..._V1_1.md` |
| Catálogo | `docs/infraestructura_agentes_skills_v1_1/CATALOGO_AGENTES_SKILLS.json` |
| Superficies Polos | `docs/polos_gastro/PROTECTED_SURFACES.yaml` |
| Empaquetado correcto | `scripts/infraestructura_agentes_skills_v1_1_1_hotfix/` |

## Por qué no se duplican skills en el ZIP

Duplicar crearía una segunda fuente de verdad y reintroduciría el drift entre copias (problema ya auditado entre `.claude/skills`, `.agents/skills` y `agent_skills/claude_imported`).  
El ZIP de revisión es un **paquete de verificación y entrega del piloto**, no un monorepo portable offline.

## Cómo reconstruir / verificar en otra copia del repo

1. Clonar/actualizar el mismo repositorio DataGastro en el mismo commit (o working tree con los mismos archivos).  
2. Verificar filas de `DEPENDENCIAS_REFERENCIADAS.csv` (`existe=sí` y `sha256` si es archivo).  
3. Ejecutar:  
   `.venv/Scripts/python.exe scripts/infraestructura_agentes_skills_v1_1_1_hotfix/empaquetar_y_validar_hotfix.py`  
4. Comparar SHA-256 del ZIP y de `MANIFEST_CONTENIDO.csv` con `CHECKSUMS_INTERNO.txt` / `CHECKSUMS_SHA256.txt`.  
5. Opcional: re-ejecutar E2E V1.1 (`run_casos_e2e_v1_1.py`) si se necesitan regenerar salidas; el hotfix no las redefine.

## Causa del checksum V1.1 incorrecto

El empaquetador V1.1 escribía `CHECKSUMS_INTERNO.txt` con el hash del manifest y **después** regeneraba `MANIFEST_CONTENIDO.csv` (para incluir el propio checksums o un estado posterior), cambiando el hash del manifest sin actualizar la línea en `CHECKSUMS_INTERNO.txt`.  
El hotfix fija el orden: contenidos → metadata/QA → **manifest definitivo** → **checksums sobre archivos definitivos** → ZIP → reverify sobre extracción.
