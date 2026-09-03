# HANDOFF — Infraestructura cartográfica v1 de PolosGastro (2026-07-08, noche)

## Qué se pidió

Tercera tanda del día. Cerrada la validación del algoritmo (sí funciona, salvo casos
puntuales causados por el contenedor de macrozona), Diego pidió dejar de investigar el
algoritmo y construir la **infraestructura permanente** para la capa editorial de
macrozonas: inventario de referencias existentes, diseño de esquema, herramienta de
edición, integración experimental en un caso real, versionado y QA, cerrando con un
roadmap definitivo del proyecto completo. Restricciones: todo en `experimentos/`, sin
tocar Fase 25 ni mapas oficiales, sin commits.

## Qué se hizo (las 7 etapas, completas)

Todo en `docs/polos_gastro/experimentos/infraestructura_cartografica_v1/` (docs 01-07 +
README) y `scripts/polos_gastro/experimentos/infraestructura_cartografica_v1/` (6 scripts).

1. **Inventario:** confirmado que NO existe ningún polígono real de macrozona en el
   proyecto — ni siquiera Fase 25 (oficial) usa algo mejor que elipses dibujadas a mano
   (fase16). El insumo más valioso: fichas de polo (`docs/polos_gastro/fichas_polos/`,
   34 fichas) tienen una sección "delimitación territorial preliminar", pero **solo 2 de
   34** (Palermo Soho, Palermo Hollywood) traen las 4 calles límite completas; el resto
   solo nombra el barrio o dice "no definida". El callejero GCBA (31.961 tramos, ya
   usado en la validación) es la base real para construir contornos sobre calles.
2. **Esquema:** `macrozonas_editorial_vN.geojson`, jerarquía polo→subzona (resuelve que
   "Palermo" no es una unidad, es un polo con Soho/Hollywood/Las Cañitas adentro), 16
   atributos incluyendo `nivel_confianza`, `estado_revision`, `calles_limite`, `fuente`.
3. **Herramienta:** QGIS recomendado (snapping a calles reales), geojson.io para ajustes
   chicos. `preparar_kit_edicion.py` arma, por macrozona, callejero recortado + entidades
   del universo V1 + microclusters + polígonos del prototipo + elipse editorial vieja +
   semilla Fase 13 — probado con Palermo (1.043 entidades, 2.233 tramos de calle).
4. **Integración real (Palermo Soho):** se trazó el ÚNICO contorno real posible con datos
   existentes (las 4 calles de la ficha PG001A, vía regresión de línea + partición del
   plano sobre el callejero) y se simuló el pipeline completo. Hallazgo clave: el
   contorno real **elimina la mezcla de identidades Soho/Hollywood** (0 de 373 entidades
   del polígono real pertenecían al viejo cluster "Hollywood"), pero **no elimina** el
   problema de núcleo sobredimensionado (sigue apareciendo un cluster de 251
   entidades/58 ha) — confirma que contorno real y segunda pasada son mejoras
   complementarias, no sustitutas.
5. **Versionado:** `macrozonas_editorial_vN_YYYYMMDD.geojson`, snapshots inmutables,
   `CHANGELOG.md` + diff automático (`comparar_versiones_editorial.py`, probado).
6. **QA:** gates duros (geometría inválida, atributos faltantes, id duplicado,
   vocabulario controlado, jerarquía polo/subzona rota) + banderas (huecos, solapamiento,
   cobertura de CABA, estado de revisión). **Corrida real contra el borrador de Palermo:
   detectó un problema genuino** (las subzonas referencian un polo "MZ_PALERMO" que nunca
   se construyó) — validó que el QA funciona antes de necesitarlo en serio.
7. **Roadmap definitivo:** separa infraestructura permanente (universo, capa editorial,
   pipeline, QA, versionado) de proceso operativo (actualización → recálculo → revisión
   humana → publicación) y desarrollo futuro (polos emergentes, Places, indicadores,
   dashboards, análisis temporal). Próximos 3 pasos concretos al final del doc 07.

## Estado real de la capa editorial (para no perder la cuenta)

- **2 de 12 polos con contorno real:** Palermo Soho, Palermo Hollywood (`borrador`, sin
  aprobar).
- **10 de 12 sin contorno propio.** 5 tienen elipse aproximada heredada de fase16
  (Puerto Madero, San Telmo, Belgrano, Corrientes/Abasto, y Palermo a nivel de polo — no
  de subzona). 5 no tienen nada (Villa Crespo, Chacarita, Recoleta, Caballito, Costanera
  Norte, Caseros/Barracas — son 6, revisar antes de continuar).
- El polo "Palermo" en sí (contenedor de las 5 subzonas) tampoco tiene geometría propia
  todavía — el QA ya lo señaló como gate duro (jerarquía incompleta).

## Pendiente (orden en doc 07 §5)

(1) Diego revisa/aprueba Palermo Soho y Hollywood · (2) definir método para los 10 polos
restantes (probablemente barrio administrativo + ajuste editorial en QGIS) ·
(3) publicar `macrozonas_editorial_v1` completo y re-correr el pipeline, decidiendo antes
la segunda pasada condicionada a forma (pendiente de la validación anterior, no de esta
etapa). Sin commits: todo el árbol de `experimentos/` sigue untracked.
