# Auditoría comparativa — Informe político experimental V1 → Informe político integrado V2

Fecha: 2026-07-12. Base V1: `INFORME_POLOS_GASTRO_FASE25_POLITICA_EXPERIMENTAL_V1.pdf`
(SHA-256 `f9ba2eff…71c7d7`, intacto). V2: `INFORME_POLOS_GASTRO_POLITICO_INTEGRADO_V2.pdf`
(fase27; hash en `CHECKSUMS_SHA256.txt`).

## Cantidad de páginas e identidad

- V1: 10 páginas A4 · V2: 10 páginas A4 (sin página 11).
- Identidad visual DGDGAS conservada: misma paleta, tipografía Arial, encabezado con franja
  azul/roja, pie institucional, cajas redondeadas, chips de estado.
- Portada: mismo diseño; V2 retira la línea "Versión de trabajo interna".

## Páginas conservadas (diseño y texto sustancialmente iguales)

| Página | Cambio residual |
|---|---|
| 1 Portada | Sin línea de versión; metadatos PDF reescritos institucionales |
| 4 Palermo | Solo cambia el mapa (placeholder saneado → render institucional); texto idéntico |
| 5 Corrientes | Solo cambia el mapa (placeholder → corredor v2.1); textos idénticos |
| 6 San Telmo y Puerto Madero | Mapas nuevos; único cambio de texto: se retira la frase de cartografía "en elaboración" |

## Páginas modificadas

| Página | V1 | V2 |
|---|---|---|
| 2 Síntesis | Belgrano y Costanera como "señales en seguimiento"; "cinco zonas seleccionadas" | Belgrano/Recoleta/Costanera como polos consolidados; "siete zonas seleccionadas"; estados de lectura actualizados |
| 3 Mapa general | Asset fase25 con leyenda de 4 categorías; "frente ribereño en observación" | Asset institucional V3.1 (7 zonas; leyenda con unidad general y unidad multiparte); lectura reescrita; nota metodológica pública única |
| 7 Belgrano | "Belgrano y zonas en observación"; 3 áreas equivalentes; Recoleta en observación | "Polo Gastronómico Belgrano"; jerarquía de 3 centralidades + sector secundario; Recoleta retirada de la caja |
| 8 (V1) → 9 (V2) Costanera | Solo texto; "tres sectores"; "lectura exploratoria"; "no constituye un polo delimitado"; mitad inferior vacía | "Polo multiparte" de 4 componentes; "delimitación adoptada"; mapa media página V3.1 en la mitad antes vacía |
| 9+10 (V1) → 10 (V2) | Próximos pasos (4 bullets + caja relación) y Nota metodológica separadas | Página fusionada: 3 bullets actualizados + nota metodológica con párrafo de dependencia de fuentes |

## Página agregada

- 8 (V2): **Polo Gastronómico Recoleta** — página nueva (en V1 Recoleta solo aparecía como
  "zona en observación"). Financiada con la fusión 9+10; el total sigue en 10.

## Textos eliminados (los más relevantes)

- "muestran señales de actividad que la Dirección mantiene en seguimiento" (p.2, respecto de Belgrano/Costanera).
- "un frente ribereño en observación sobre la Costanera" (p.3).
- "Belgrano y zonas en observación" / "cuya lectura de conjunto se encuentra en consolidación" (p.7).
- "…el área central, **Recoleta** y el eje Caseros–Barracas" (p.7, caja de observación).
- "con tres sectores principales de actividad" (p.8).
- Panel completo "Qué significa lectura exploratoria", incl. "no constituye un polo delimitado"
  y "sin proponer todavía una delimitación" (p.8).
- Chip "lectura exploratoria" (p.8).
- "La Dirección mantiene la zona en seguimiento…" (p.8).
- "Consolidar la lectura de Belgrano y extender el análisis en detalle a … Recoleta…" (p.9).
- "Mantener el seguimiento del frente ribereño de la Costanera Norte…" (p.9).
- "La representación cartográfica de detalle de este frente se encuentra en elaboración." (p.6).

## Textos agregados (los más relevantes)

- Párrafo de síntesis sobre los tres polos consolidados (p.2).
- Lectura de Belgrano como polo único con tres centralidades y Belgrano R sector secundario (p.7).
- Página completa de Recoleta: lectura de unidad + caja de diversidad interna (p.8).
- Lectura de Costanera como polo multiparte + paneles "Una delimitación adoptada" y
  "Las condiciones del territorio" (p.9).
- Nota metodológica pública única (p.3, pie del bloque cartográfico).
- Párrafo de dependencia de fuente externa de Costanera, 92,96 %, una sola vez en metodología (p.10).

## Mapas reemplazados (8/8; cero placeholders)

| Página | V1 | V2 |
|---|---|---|
| 3 | `global_mapa_fase25.png` (placeholder saneado) | `mapa_general_institucional_v3_1` (copia recortada) |
| 4 | `mapa_fase25_palermo_las_canitas.png` | render institucional Palermo (delimitación vigente) |
| 5 | `mapa_fase25_corrientes_abasto.png` | render corredor v2.1 |
| 6 | `mapa_fase25_san_telmo.png` / `mapa_fase25_puerto_madero.png` | renders núcleo+Defensa v2.1 / PM_PRES_C |
| 7 | `mapa_fase25_belgrano.png` | `belgrano_institucional_v3_1` (copia recortada) |
| 8 (V2) | (sin mapa en V1) | `recoleta_institucional_v3_1` (copia recortada) |
| 9 (V2) | (sin mapa en V1) | `costanera_norte_media_pagina_v3_1` (copia recortada) |

## KPIs actualizados

Ver `KPI_LOCK_EDITORIAL_V2.csv`: zonas seleccionadas 5→7; Belgrano 3 centralidades;
Recoleta 1 unidad pública; Costanera 4 componentes (universo conciliado 72 registrado, no
publicado); dependencia de fuente externa de Costanera publicada una única vez en metodología
(92,96 %). Coberturas y estabilidades permanecen reservadas.
