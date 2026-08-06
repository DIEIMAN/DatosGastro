# Caso B — PDF político experimental (prueba QA)

**Fecha:** 2026-07-11  
**Agente simulado:** `auditor_qa`  
**Insumo (solo lectura):**  
`outputs/polos_gastro/experimentos/fase25_politica_e_integracion_editorial_v1/`  
incl. `REVISION_FASE25_POLITICA_EXPERIMENTAL.zip` y PDF experimental  
**PNG de esta prueba (escritura solo en infra):**  
`outputs/infraestructura_agentes_skills_v1/casos_prueba/caso_b_qa_png/`  
**Informe QA:**  
`outputs/infraestructura_agentes_skills_v1/casos_prueba/caso_b_informe_qa.md`

## Manifest

Presente en el pack de revisión:

- `REVISION_FASE25_POLITICA_EXPERIMENTAL/MANIFEST_ARCHIVOS.md`
- `metadata_fase25_politica_e_integracion.json`
- README de orden de lectura

**Resultado:** manifest **OK** (estructura de pack de revisión reconocible).

## Inspección PDF

Comando (venv):

```text
.venv/Scripts/python.exe scripts/qa/pdf_check.py
  INFORME_POLOS_GASTRO_FASE25_POLITICA_EXPERIMENTAL_V1.pdf
  --outdir outputs/infraestructura_agentes_skills_v1/casos_prueba/caso_b_qa_png
  --dpi 80
```

| Página | Texto (chars) | Notas visuales (muestra) |
| --- | --- | --- |
| 1 | 234 | Portada DGDGAS; **muestra “Julio 2026” y “Versión de trabajo interna”** |
| 2–10 | 593–1592 | Texto presente; sin `[SIN TEXTO]` |
| 3 | 604 | Mapa general legible; pie DGDGAS; disclaimer de no límites oficiales |

**PDF origen no editado.**

## Pendientes de integración detectados

Del QA_FINAL y docs del pack:

1. Integración futura del handoff v2.1 **no forma parte** de esa tanda (explícito en QA_FINAL).  
2. `MATRIZ_ASSETS_PENDIENTES_CODEX.csv` y `PLAN_INTEGRACION_HANDOFF_CODEX_V21.md` señalan assets/placeholders dependientes de Codex.  
3. `kpis_lock_preliminar.json` con advertencias (KPIs técnicos no todos en superficie del PDF).  
4. Pieza **EXPERIMENTAL / NO OFICIAL / interna**.

## Hallazgos QA (sin corregir el PDF)

| id | severidad | hallazgo |
| --- | --- | --- |
| B1 | menor / estándar mostrable | Portada con fecha y “versión de trabajo interna” — coherente con experimental interno; **chocaría** con plantilla DGDGAS “mostrable sin fecha/versión” si se promociona |
| B2 | info | 10/10 páginas con texto; render OK |
| B3 | info | Pendiente integración v2.1 documentada |
| B4 | info | Marca DGDGAS correcta en muestras p.1 y p.3 |

## Controles

| control | resultado |
| --- | --- |
| PDF editado | **no** |
| Pack origen modificado | **no** |
| API/Places/install | **no** |
| commit | **no** |

## Resultado del caso

**PASS** (QA independiente sin editar PDF; manifest y pendientes de integración reportados).
