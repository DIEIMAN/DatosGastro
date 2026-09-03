# Evidencia documental integrada V1.1 — Belgrano, Recoleta, Costanera Norte

**Línea:** `docs/polos_gastro/evidencia_documental_integrada_v1_1/`
**Fecha:** 2026-07-11
**Rol ejecutor:** `investigador_documental` (infraestructura agentes y skills V1.1 / hotfix V1.1.1)
**Skill canónica aplicada:** `auditar_evidencia_documental` (`docs/infraestructura_agentes_skills_v1/skills/auditar_evidencia_documental/SKILL.md`)
**Estado:** EXPERIMENTAL / pendiente de revisión humana (Diego) — no es informe oficial.

## Qué es esta línea

**V1.1 = corrección de decisión y trazabilidad sobre V1** (que permanece intacta en
`docs/polos_gastro/evidencia_documental_integrada_v1/`). Único cambio de fondo: se
registra **DEC-10 — Adopción institucional de Costanera Norte**, que sustituye a DEC-06
en estatus editorial y comunicación pública (DEC-06 queda solo como antecedente
histórico SUPERADO POR DEC-10). Belgrano, Recoleta, las 42 evidencias, las URLs y la
bibliografía no cambian.

Consolidación depurada y estructurada de la evidencia documental generada por Grok
(`docs/polos_gastro/evidencia_documental/` y pack cerrado
`outputs/polos_gastro/REVISION_EVIDENCIA_DOCUMENTAL_POLOS_V1/`), integrada con:

- las decisiones humanas vigentes de Polos Gastro (DEC-01…DEC-10 y las decisiones
  comunicadas por Diego el 2026-07-11 para este piloto);
- los resultados técnicos del pipeline híbrido v2.1
  (`docs/polos_gastro/experimentos/pipeline_hibrido_integracion_v21/`);
- las investigaciones previas de Perplexity
  (`docs/polos_gastro/fuentes_externas/perplexity_*.md`).

Produce un handoff documental operativo para el agente `cartografo_territorial` y Codex.

## Qué NO es

- No crea geometrías, mapas ni modifica informes o PDFs.
- No reabre decisiones humanas cerradas.
- No sustituye al futuro `auditor_qa`.
- No modifica el paquete original de Grok ni el pack cerrado (superficie protegida
  `POLOS-EVIDENCIA-PACK`).
- No re-verifica URLs en línea: los estados de URL provienen de la auditoría de Grok del
  2026-07-11 (sin descargas nuevas en esta pasada, por diseño del piloto).

## Archivos

| Archivo | Función |
|---|---|
| `README_EVIDENCIA_DOCUMENTAL_INTEGRADA.md` | Este índice |
| `BELGRANO_EVIDENCIA_DOCUMENTAL_INTEGRADA.md` | Ficha integrada Belgrano (documental + técnico v2.1) |
| `RECOLETA_EVIDENCIA_DOCUMENTAL_INTEGRADA.md` | Ficha integrada Recoleta |
| `COSTANERA_NORTE_EVIDENCIA_DOCUMENTAL_INTEGRADA.md` | Ficha integrada Costanera Norte |
| `MATRIZ_EVIDENCIA_DOCUMENTAL_INTEGRADA.csv` | Matriz única (54 filas): evidencia + inferencias + decisiones, con fuente_id y uso permitido |
| `BIBLIOGRAFIA_DOCUMENTAL_VERIFICADA.csv` | Fuentes deduplicadas con estado de acceso y carácter (sin cambios vs. V1) |
| `DECISIONES_Y_USOS_DOCUMENTALES.md` | Decisiones humanas vigentes (incluye DEC-10) y reglas de uso editorial |
| `CONTRADICCIONES_Y_VACIOS_DOCUMENTALES.md` | Contradicciones, correcciones y vacíos reales |
| `HANDOFF_DOCUMENTAL_CARTOGRAFO_V1_1.md` | Handoff operativo para cartógrafo territorial / Codex |

## Linaje (no sobrescribe nada)

```text
Perplexity (2026-06-29)  →  primer barrido general; Costanera Norte sin evidencia suficiente
Grok (2026-07-11)        →  paquete evidencia_documental/ (42 filas, 31 fuentes, 25 descartes)
Pipeline híbrido v2.1    →  geometrías técnicas: BEL_RV2_N01–N06; 9 núcleos Recoleta; CN_C01–CN_C04
Decisiones Diego         →  DEC-01…DEC-09 (2026-07-11) + decisiones del piloto documental
Integrada V1             →  integración; corrige y traza REC-R02; handoff al cartógrafo
DEC-10 (Diego)           →  adopción institucional de Costanera Norte (sustituye DEC-06 en estatus editorial)
ESTA LÍNEA (V1.1)        →  corrección de decisión y trazabilidad; matriz 54 filas; handoff V1_1
```

Las líneas anteriores permanecen intactas y siguen siendo la fuente primaria de sus
propios contenidos.

## Corrección documental obligatoria conservada

`REC-R02`: la cifra de ~150 restaurantes de la ficha de polos de Turismo BA corresponde a
**San Telmo**, no a Recoleta. Queda registrada como afirmación **descartada** en la matriz
(clasificación EVIDENCIA, uso `solo_uso_interno`) y en
`CONTRADICCIONES_Y_VACIOS_DOCUMENTALES.md`. No usar esa cifra para Recoleta en ningún
texto.

## Orden de lectura recomendado

1. `DECISIONES_Y_USOS_DOCUMENTALES.md` (marco cerrado).
2. Fichas por polo.
3. `MATRIZ_EVIDENCIA_DOCUMENTAL_INTEGRADA.csv` + `BIBLIOGRAFIA_DOCUMENTAL_VERIFICADA.csv`.
4. `CONTRADICCIONES_Y_VACIOS_DOCUMENTALES.md`.
5. `HANDOFF_DOCUMENTAL_CARTOGRAFO_V1_1.md` (lo único que necesita el cartógrafo para arrancar).

## Marca

Marca pública: **DGDGAS** (Dirección General de Desarrollo Gastronómico). DataGastro solo
en documentación interna como esta.
