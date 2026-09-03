# Cafecito — estado

**Fecha de corte:** 2026-09-03.

## Entregables

| Entregable | Dónde | Estado |
|---|---|---|
| Informe Cafecito Belgrano (encuesta, tandas 1–8) | `outputs/cafecito/INFORME_CAFECITO_DGDGAS_REVISION_4.pdf` (última revisión); generadores en `scripts/cafecito/generar_*` (uno por versión, 1.100–1.260 líneas cada uno); contenidos editables por tanda en `docs/cafecito/contenido_editable_*.yaml` | Cerrado (julio 2026). Cómo editar: `docs/cafecito/COMO_EDITAR_INFORME_CAFECITO.md`. |
| Sedes de cafeterías geocodificadas | `outputs/cafecito/cafeterias_sedes_caba_geocodificadas.csv` | Insumo. |
| Pet friendly CABA (encargo V2) | `outputs/analisis_interno/PET_FRIENDLY_CABA_2026-08-25/` (ignorado por Git) | Abierto. Al 2026-09-02: Places dio el atributo `allowsDogs` en 541 de 895; padrón 2017 ~55 % abierto; 110 nombres a corregir; V1 con 5.018 datos. Enriquecimiento frenado en fase 4. |

## Decisiones que esperan a Diego

- Congelar los ~20 generadores superados de `scripts/cafecito/` en `scripts/cafecito/archive/`
  con un README de qué PDF salió de cuál (propuesta de la auditoría del 2026-09-03).
- Continuar la fase 4 del enriquecimiento pet friendly.

## Dónde seguir

- Handoffs de tandas: `docs/cafecito/HANDOFF_CAFECITO_BELGRANO_TANDA*_2026_07_07.md` y
  `docs/revisiones/HANDOFF_CAFECITO_BELGRANO_TANDA1_2026_07_07.md`.
- Plantilla de encuestas reutilizable: `config/encuestas/`, `scripts/encuestas/`.
