# Evidencia documental — Expansión candidatos V4

**Fecha:** 2026-07-12  
**Roles:** `investigador_documental_externo` (principal), `red_team_documental` (secundario)  
**Infraestructura:** agentes y skills V1.1 / hotfix V1.1.1 (skill `auditar_evidencia_documental`)  
**Marca pública:** DGDGAS · **Línea interna:** DataGastro / Polos Gastro

## Qué es

Base documental trazable para **15 zonas candidatas** aún no desarrolladas en detalle en la corrida V3, orientada a la futura expansión territorial V4.

## Qué no es

- No es delimitación geométrica ni corrida Places.
- No adopta polos ni impone nombres institucionales.
- No modifica el informe político V2.1, fase27/28, preflight de Claude, V3/V3.1 ni evidencia V1.1.
- No supervisa clustering.

## Regla metodológica

| Usar la evidencia para | No usar la evidencia para |
|---|---|
| Interpretar, caracterizar, nombrar, contrastar, comunicar | Supervisar clustering, asignar puntos, forzar polígonos, decidir límites |

Separar siempre: **evidencia** | **inferencia** | **hipótesis territorial** | **decisión institucional futura**.

## Archivos en docs/

- 15 expedientes `*_EXPEDIENTE_DOCUMENTAL_V4.md`
- `SINTESIS_DOCUMENTAL_EXPANSION_CANDIDATOS_V4.md`
- `AGENDA_BUSQUEDA_OFICIAL_PENDIENTE_V4.md`
- `RED_TEAM_DOCUMENTAL_EXPANSION_V4.md`
- `HANDOFF_DOCUMENTAL_PREFLIGHT_CLAUDE_EXPANSION_V4.md`
- `HANDOFF_DOCUMENTAL_CODEX_CORRIDA_EXPANSION_V4.md`
- este README

## Archivos en outputs/

`outputs/polos_gastro/evidencia_documental_expansion_v4/`

- matrices CSV (normalización, fuentes, evidencia, diagnóstico, relaciones, subunidades centro, auditoría semilla, priorización, objeciones, QA)
- metadata, manifest, checksums

## Orden de lectura

1. Este README + `SINTESIS_...`
2. `DIAGNOSTICO_...csv` + `NORMALIZACION_...csv`
3. Expedientes de la tanda prioritaria
4. Handoffs Claude / Codex
5. `RED_TEAM_...` antes de cualquier elevación de estatus

## Universos de fuentes

| Nivel | Uso |
|---|---|
| OFICIAL_PRIMARIA | Respaldo principal o complementario de denominación/nodos |
| ACADEMICA | Marco |
| PERIODISTICA_CONFIABLE | Caracterización y tramos; no límite oficial |
| AUXILIAR | Solo contexto |

## Estado

Paquete experimental para contrastar con preflight espacial y futura corrida. **Ninguna zona queda adoptada.**
