# Caso A — Evidencia documental (prueba de infraestructura)

**Fecha:** 2026-07-11  
**Agente simulado:** `investigador_documental` + skill `auditar_evidencia_documental`  
**Insumo (solo lectura):**  
`outputs/polos_gastro/REVISION_EVIDENCIA_DOCUMENTAL_POLOS_V1/`  
(y ZIP homónimo; no se modificó)  
**Salida de prueba:** este informe + handoff en  
`outputs/infraestructura_agentes_skills_v1/casos_prueba/caso_a_handoff_documental.md`

## Inventario de URLs (resumen)

Fuente: `05_AUDITORIA/AUDITORIA_FUENTES_Y_URLS.md` del pack.

| Métrica | Valor |
| --- | --- |
| Filas matriz evidencia | 42 |
| Fuentes bibliografía | 31 |
| URLs únicas principales | 31 |
| ACTIVA / usable | 24 |
| PAYWALL | 4 |
| CONTENIDO_NO_COINCIDE | **1 (REC-R02)** |

URLs institucionales clave inventariadas (ejemplos):

- Turismo BA polos: `turismo.buenosaires.gob.ar/.../polos-gastronomicos`
- Turismo BA Costanera / patio; BO Ley 5.961; La Nación Belgrano/Recoleta; etc.  
(Detalle completo en el pack origen; no se re-fetch en esta prueba de infra — sin descargas nuevas.)

## Corrección de los “150 restaurantes”

| Hallazgo | Detalle |
| --- | --- |
| ID | REC-R02 |
| Afirmación errónea | “~150 restaurantes en Recoleta” atribuida a Turismo BA |
| Corrección | La frase en la misma página de Turismo BA corresponde al párrafo de **San Telmo** |
| Estado pack | **NO_RESPALDA / NO_USAR / CONTENIDO_NO_COINCIDE** |
| Evidencia en pack | `01_INFORMES/recoleta_investigacion_documental.md`, README, `FUENTES_DESCARTADAS_*.csv` D01, handoff original |

**Resultado de la skill:** la corrección está **detectada y documentada** en el pack; el agente documental de infra **no debe reintroducir** la cifra en textos de Recoleta.

## Separación evidencia / decisión institucional

| Polo | Evidencia (E) | Inferencia (I) | Decisión institucional (D) |
| --- | --- | --- | --- |
| Recoleta | Turismo BA: polo histórico; nodos Junín–Vicente López | máximo dos subzonas de lectura | Usar “Polo Recoleta”; no nueve polos |
| Belgrano | Prensa + marco Turismo BA sin nombre en listado clásico | centralidad Barrio Chino–C–Barrancas | Polo Belgrano de trabajo (no listado oficial aislado) |
| Costanera Norte | Turismo BA, patio, Ley 5.961, regularización carritos | cuatro componentes + vacíos | Un polo multiparte de lectura |

## Handoff de prueba

Generado en: `outputs/infraestructura_agentes_skills_v1/casos_prueba/caso_a_handoff_documental.md`  
Plantilla base: `plantillas/HANDOFF_DOCUMENTAL.md`.

## Controles de seguridad de la prueba

- Pack origen: **no modificado**.  
- Sin API / sin nuevas descargas en esta tanda de prueba.  
- Sin commit.

## Resultado del caso

**PASS** para objetivos del caso A (inventario, REC-R02, separación E/I/D, handoff de prueba).
