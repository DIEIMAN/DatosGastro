# Handoff cartográfico al integrador V3.1

| Campo | Valor |
| --- | --- |
| Origen | `cartografo_territorial` |
| Destino | `integrador_tecnico_editorial` y QA independiente |
| Fecha | 2026-07-11 |
| Estado | LISTO PARA INTEGRACIÓN EDITORIAL, sujeto a QA independiente |

## Modelos territoriales cerrados

- Belgrano: `BEL-A`; un polo, tres centralidades, siete piezas; Belgrano R es sector secundario.
- Recoleta: `REC-A`; una unidad pública; nueve núcleos solo analíticos; `REC-B` respaldo interno.
- Costanera Norte: `CN-DEC10`; un polo, cuatro componentes discontinuos y cinco piezas; vacíos preservados.

No volver a correr modelos. KPI lock V3 permanece sin cambios.

## Assets públicos recomendados

- Página 3: `mapa_general_institucional_v3_1.png` (SVG disponible).
- Página 7: `belgrano_institucional_v3_1.png`.
- Página de Recoleta: `recoleta_institucional_v3_1.png`.
- Página 8: `costanera_norte_media_pagina_v3_1.png`; usar la versión completa si el layout dispone de mayor caja.

## Capas de presentación

`BELGRANO_PRESENTACION_V3_1.geojson`, `RECOLETA_PRESENTACION_V3_1.geojson` y `COSTANERA_NORTE_PRESENTACION_V3_1.geojson`, todas en EPSG:4326. BBox y estilos: `metadatos/`.

## Nombres públicos

Belgrano: Barrio Chino–Belgrano C; Barrancas · Pasaje Echeverría; Cabildo–Juramento; Bajo Belgrano; Belgrano R (sector secundario). Recoleta: Polo Gastronómico Recoleta. Costanera Norte: numeración 1–4 con denominaciones descriptivas documentadas.

## Nota metodológica

Usar una sola vez en la página o bloque cartográfico: “Delimitación territorial adoptada por el estudio. No representa un límite administrativo oficial.” No repetirla en cada asset si la página ya la contiene.

## Interno técnico no publicable

`PUNTOS_ASOCIADOS_SANITIZADOS_V3.geojson`, tablas punto→unidad, códigos de modelo, métricas completas, estabilidad, dependencia de fuente y alternativas. Clasificación: `INTERNO_TECNICO_NO_PUBLICABLE`. Ninguno integra el pack editorial.

## Contrato

El contrato específico `docs/polos_gastro/preintegracion_editorial_v3/CONTRATO_OUTPUTS_CARTOGRAFICOS_PARA_INTEGRACION_V3.md` **sí existía** y fue aplicado en esta tanda V3.1. Se elimina la contradicción previa entre “contrato incorporado” y “al no existir contrato específico”. Matriz: `MATRIZ_CUMPLIMIENTO_CONTRATO_EDITORIAL_V3_1.csv`.

## Integración

No alterar geometrías ni KPI. Insertar el mapa general en página 3, Belgrano en página 7, Costanera media página en página 8 y Recoleta en la página que defina el integrador. No mostrar puntos, códigos técnicos ni porcentajes de fuente en el cuerpo político.
