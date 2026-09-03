# HANDOFF — Consolidación editorial pre-informes Polos (2026-07-11)

Sesión: Fable (capa editorial), en paralelo con Codex (pruebas técnicas en
`pipeline_hibrido_repeticiones_v2/`, no tocadas).

## Qué se hizo (completo)

Paquete editorial completo en:

- Docs: `docs/polos_gastro/experimentos/consolidacion_editorial_pre_informes_v1/`
  (9 entregables + QA_FINAL + MANIFEST).
- Outputs: `outputs/polos_gastro/experimentos/consolidacion_editorial_pre_informes_v1/`
  (`REVISION_CONSOLIDACION_EDITORIAL/` + `.zip` de 42.363 bytes + metadata JSON).

Contenido: registro formal de las 9 decisiones aprobadas por Diego (DEC-01…DEC-09,
trazadas a DH-01…DH-12 del paquete 2026-07-10); auditoría editorial página por página
de Fase 25 para audiencia política + matriz CSV de 32 ajustes; especificación de la
Fase 25 pulida (9–10 pp.); arquitecturas del informe híbrido (2 variantes) y del
informe metodológico (16 hitos); guía de lenguaje; inventario de recursos; plan de
integración con Codex.

## Estado

- Sin commits/push/staging (todo untracked). Fase 25/26, prototipos y datos intactos.
- Pendiente: revisión de Diego del paquete (empezar por
  `REVISION_CONSOLIDACION_EDITORIAL/README.md`, orden de lectura ahí).

## Próximos pasos al retomar

1. Si Diego aprueba la especificación → implementar Fase 25 política como **fase nueva**
   heredando del generador de F25 (ajustes con `depende_pipeline_hibrido = no` de la
   matriz; el mapa global con jerarquía es la regeneración de mayor valor).
2. Cuando Codex entregue → seguir `PLAN_INTEGRACION_RESULTADOS_CODEX_FABLE.md` §§1–4
   (qué documento se actualiza con cada resultado; qué decisiones se reabren solo si
   hay contradicción).
3. DH abiertas que no dependen de Codex: DH-11 (etiquetado deduplicación, cota rápida
   de 50), checklist de macrozonas editoriales, nombres de subtramos Corrientes.
