# INFRAESTRUCTURA_AGENTES_SKILLS_V1_1

Corrección y promoción controlada sobre V1 (sin sobrescribir V1).

## Qué hay aquí

| Artefacto | Descripción |
| --- | --- |
| `POLITICA_OPERATIVA_DATAGASTRO_V1_1.md` | Política genérica + precedencia + Drive + rutas |
| `CATALOGO_AGENTES_SKILLS.json` | Catálogo machine-readable |
| `ESQUEMA_MANIFEST_V1_1.md` | Manifest sin autorreferencia |
| `RUN_PLAN_MULTIAGENT.yaml` | Plan paralelo E2E |
| `EVALUACION_AGENTES_SKILLS_V1_1.md` | Evaluación real |
| `QA_FINAL_*.md` | Cierre |
| `adaptadores/` | Claude propuestos (no activados) + Codex delgados |
| `registros/PROTECTED_SURFACES_TEMPLATE.yaml` | Plantilla |
| `REPORTE_PARIDAD_SKILLS.md` | Paridad (generado) |

Registro Polos: `docs/polos_gastro/PROTECTED_SURFACES.yaml`  
Skills de procedimiento: reutilizan definiciones V1 en `docs/infraestructura_agentes_skills_v1/skills/`  
Scripts: `scripts/infraestructura_agentes_skills_v1_1/`

## Agentes en piloto (no nativos Claude)

1. investigador_documental  
2. cartografo_territorial  
3. integrador_tecnico_editorial  
4. auditor_qa  

## Empaquetado

```text
.venv/Scripts/python.exe scripts/infraestructura_agentes_skills_v1_1/empaquetar_revision_v1_1.py
```

Salida: `outputs/infraestructura_agentes_skills_v1_1/REVISION_INFRAESTRUCTURA_AGENTES_SKILLS_V1_1.zip`
