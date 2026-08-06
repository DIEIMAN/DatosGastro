# Caso C — Integración técnica v2.1 (plan de prueba)

**Fecha:** 2026-07-11  
**Agente simulado:** `integrador_tecnico_editorial`  
**Insumo (solo lectura):**  
`outputs/polos_gastro/experimentos/pipeline_hibrido_integracion_v21/`  
incl. `REVISION_PIPELINE_HIBRIDO_INTEGRACION_V21.zip`, `HANDOFF_FABLE/`,  
`docs/polos_gastro/experimentos/pipeline_hibrido_integracion_v21/MATRIZ_DECISIONES_POST_INTEGRACION_V21.md`  
**Salida:**  
`outputs/infraestructura_agentes_skills_v1/casos_prueba/caso_c_plan_integracion.md`  
**Ningún entregable v2.1 modificado.**

## Lectura de handoff

`HANDOFF_FABLE/` contiene capas de **presentación**, mapas PNG, CSV de evaluación Belgrano, glosario, `DECISIONES_Y_ADVERTENCIAS.md`, `MANIFEST_HANDOFF.csv`, README.

Propósito aparente: entregar a Fable/editorial insumos listos sin reabrir corridas.

## Decisiones pendientes (matriz post-integración)

| estado | zona | decisión |
| --- | --- | --- |
| CERRADA | Corrientes | corredor único continuo, separado de Abasto |
| CERRADA | San Telmo | núcleo + Defensa contextual, jerarquía desigual |
| CERRADA | Puerto Madero | separar capa analítica y presentación |
| **PENDIENTE** | Puerto Madero | validar visualmente PM_PRES_C |
| **PENDIENTE** | Belgrano | revisión humana shortlist + post hoc |
| **PENDIENTE** | Costanera Norte | uso editorial de contexto CN_C02 |
| **PENDIENTE** | Escalado | validar lectura territorial antes de promover |
| NO_REABIERTA | General | Fase 25 sigue vigente |

## Inconsistencias / riesgos de integración

1. Editorial F25 política experimental **aún no incorpora** assets v2.1 (documentado en Caso B).  
2. PM_PRES_C es RECOMENDADA_NO_VINCULANTE en tabla de simplificación — no promover sin validación visual.  
3. Belgrano: shortlist técnica ≠ nombres institucionales automáticos.

## Plan de integración de prueba (no ejecutado)

Ver `caso_c_plan_integracion.md`: solo plan en carpeta de infra.

## Controles

- Sin modificar líneas v2.1 / F25 / F26.  
- Sin resolver contradicciones en silencio.  
- Sin commit.

## Resultado del caso

**PASS**.
