# Plan de integración de resultados Codex ↔ Fable

Estado: PROPUESTA EDITORIAL EXPERIMENTAL. Fecha: 2026-07-11.
División de trabajo vigente: **Codex** ejecuta las pruebas técnicas de San Telmo,
Belgrano, Puerto Madero, Corrientes y Costanera en carpetas nuevas (línea
`pipeline_hibrido_repeticiones_v2/`, no tocada por este paquete). **Fable** produce la
capa editorial/institucional (este paquete). Este plan define qué pasa cuando Codex
termine. Nada de lo aquí descrito se ejecuta sin aprobación de Diego.

## 1. Qué resultados técnicos se incorporarán

De cada zona, al paquete editorial le interesan exactamente estos productos (no el
detalle de corrida):

- **San Telmo:** ¿el eje Defensa queda respaldado con la técnica de "eje respaldado"?
  (condición de DH-01 c). Métrica de respaldo + geometría del eje si existe.
- **Belgrano:** núcleos estables con estabilidad y cobertura **por núcleo**; resultado
  del contenedor de contraste (barrio oficial vs. corredores 250 m); correspondencia
  post hoc núcleo↔topónimo (protocolo BEL-R14).
- **Puerto Madero:** métricas del frente doble (hipótesis principal DH-06 b) vs. frente
  único; cobertura por opción; segmentación solo si emerge del perfil.
- **Corrientes:** confirmación (o no) de la continuidad del corredor bajo el protocolo
  repetido; perfil longitudinal actualizado (insumo de las etiquetas narrativas DEC-02).
- **Costanera:** componentes de concentración actualizadas (insumo de la representación
  multiparte DEC-05), con su dependencia de fuente.
- **Transversal:** hashes/metadata de insumos para trazabilidad ([MET] cap. 16).

## 2. Qué documentos de este paquete deberán actualizarse al llegar resultados

| Documento | Actualización esperada |
| --- | --- |
| `REGISTRO_DECISIONES_APROBADAS_DIEGO.md` | DEC-04 pasa de "sujeto a prueba" a resuelta; se registran las firmas nuevas (DH-01, DH-06; DH-05 si se activan nombres) como DEC-10+ |
| `ARQUITECTURA_INFORME_POLOS_HIBRIDOS.md` | Páginas 5, 7, 8 dejan de ser hipotéticas; jerarquía de madurez (§8) se puebla con estados reales |
| `INVENTARIO_RECURSOS_INFORMES_FINALES.md` | Filas "¿Codex? = sí" cambian a rutas concretas de la v2 |
| `MATRIZ_AJUSTES_FASE25.csv` | Filas con `depende_pipeline_hibrido = sí` (Puerto Madero, Costanera en mapa global, San Telmo) pasan a ejecutables |
| `ESPECIFICACION_FASE25_PULIDA_POLITICOS.md` | §5 "Deben regenerarse": se confirma o descarta la regeneración de San Telmo y Puerto Madero |
| `ARQUITECTURA_INFORME_EVOLUCION_METODOLOGICA.md` | Cap. 15 ("resultado final") y métricas post-repetición del §8 |

## 3. Qué decisiones se reabren si hay contradicción

Regla general: una contradicción técnica **no revierte automáticamente** una decisión;
dispara una nota de contradicción y vuelve a Diego. Casos previstos:

| Resultado de Codex | Decisión afectada | Efecto |
| --- | --- | --- |
| El corredor Corrientes muestra huecos reales de continuidad (no artefactos) | DEC-01 / DEC-02 | Se reabre la forma del corredor (condición explícita del registro) |
| El eje Defensa no queda respaldado | DH-01 (abierta) | Cae a opción a) núcleo único — no reabre nada firmado |
| Los núcleos de Belgrano no alcanzan estabilidad ni con contenedor de contraste | DEC-04 (resultado) / DH-05 | Belgrano queda "experimental" en el informe híbrido; nombres siguen diferidos; no se fuerza lámina de detalle |
| La correspondencia post hoc contradice los topónimos de Fase 25 | DEC-04 "qué no significa" | La lectura editorial de Fase 25 se mantiene como editorial; el híbrido publica códigos neutros; decisión de nombres a Diego |
| El frente doble de Puerto Madero no supera al único | DH-06 (abierta) | Se firma frente único; el mapa F25 de PM puede pulirse sin cambio de concepto |
| Costanera pierde estabilidad en la repetición | DEC-05/06 | No se reabre (ya es exploratoria); solo se ajusta el texto del anexo |
| Cualquier resultado que dependa de consultas Places nuevas | — | Fuera de protocolo: 0 consultas autorizadas; se detiene y se reporta |

## 4. Qué mapas deberán regenerarse (post-integración)

En orden de valor:

1. **Mapa global** con jerarquía + Costanera multiparte (DEC-05) — cierra [F25P] p. 3.
2. **Puerto Madero** según DH-06 firmada — [F25P] p. 5 y [HIB] p. 8.
3. **San Telmo** con eje Defensa (solo si DH-01 c se firma) — [F25P] p. 6 y [HIB] p. 5.
4. **Belgrano híbrido** (núcleos estables, códigos neutros) — solo [HIB] p. 7; la lámina
   editorial de F25 no cambia de geometría.
5. **Corrientes híbrido** (corredor + etiquetas narrativas + contexto) — [HIB] p. 6.

Todo mapa regenerado pasa por `scripts/qa/pdf_check.py` + inspección visual.

## 5. Qué partes de Fase 25 pueden pulirse inmediatamente (sin esperar)

- Todos los ajustes de la matriz con `depende_pipeline_hibrido = no`: reescritura del
  resumen, fusión pp. 3+4, eliminación/reconversión p. 6, retitulado de cajas, guía de
  lenguaje aplicada, tags unificados, leyendas sin "aproximado", página de próximos
  pasos, nota metodológica final.
- El mapa global con jerarquía editorial de tres niveles (la jerarquía es editorial;
  no necesita el híbrido — solo la representación de Costanera queda provisoria).
- La implementación se hace como fase nueva heredando del generador de F25 (F25 final
  intacta), **previa aprobación de Diego de la especificación**.

## 6. Qué debe esperar

- Geometrías nuevas de Puerto Madero, San Telmo y Belgrano (repeticiones + firmas).
- Costanera multiparte en cualquier mapa (componentes actualizadas de Codex + decisión
  de representación).
- Coberturas y mezclas de fuentes publicables (requieren además DH-11, que no es de
  Codex sino etiquetado humano interno).
- La redacción del informe híbrido y del metodológico (dependencias en §7).

## 7. Orden recomendado de producción de los informes

1. **Ahora (sin Codex):** Diego revisa este paquete → aprueba especificación [F25P] →
   se implementa la Fase 25 pulida con los cambios inmediatos (§5). Si hay urgencia
   política, esta pieza sale con el mapa global mejorado y Costanera como está (eje),
   documentando la provisoriedad solo internamente.
2. **Al llegar resultados de Codex:** integración según §§1–4; firmas de DH-01/DH-06;
   regeneración de mapas 1–3; [F25P] versión final.
3. **Después de firmas + DH-11 (cota rápida):** redacción del **informe híbrido**
   (variante A primero, B como extensión).
4. **Al final:** **informe metodológico** (necesita el estado final de todo; sus actos
   I–III pueden pre-redactarse en paralelo desde ya).

## 8. Protocolo de integración (higiene entre agentes)

- Fable no escribe en carpetas de Codex ni interpreta corridas a medio terminar; solo
  consume entregables finales con QA propio de Codex.
- Toda incorporación de resultados se documenta en un `HANDOFF_*` en `docs/revisiones/`
  y actualiza este plan.
- Si un entregable de Codex contradice un guardrail (consultas externas no autorizadas,
  datos sensibles), se detiene la integración y se reporta a Diego antes de usar nada.
