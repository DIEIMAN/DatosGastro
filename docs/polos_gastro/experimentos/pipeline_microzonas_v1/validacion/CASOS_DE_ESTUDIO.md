# Casos de estudio para la validación (Etapa V2-1)

**Fecha:** 2026-07-08 · **Carácter:** experimental, sin decisión editorial tomada.

## Selección: 8 macrozonas

| Macrozona | n entidades | Clusters HDBSCAN | Ruido | Por qué se eligió |
|---|---|---|---|---|
| **Palermo** | 1.043 | 8 | 20 % | Multi-núcleo grande; tiene capa editorial de subzonas (Soho, Hollywood, Las Cañitas, Chico, Botánico) para contrastar; 2 clusters sobredimensionados (candidatos a segunda pasada). |
| **Avenida Corrientes** | 860 | 9 | 29 % | Corredor lineal claro (un cluster de 128 puntos con elongación 3,4 detectado como corredor); tiene capa editorial (Corrientes/Abasto); 1 cluster sobredimensionado. |
| **San Telmo** | 218 | 10 | 27 % | Compacto, con hito colectivo (Mercado de San Telmo) y capa editorial propia; buena relación señal/ruido. |
| **Belgrano** | 158 | 4 | 20 % | Un cluster dominante grande (88 pts/42 ha) + satélites chicos; capa editorial (Barrio Chino, Bajo Belgrano, Cabildo/Juramento). Patrón "núcleo + satélites", distinto del multi-núcleo de Palermo. |
| **Chacarita** | 226 | 7 | 31 % | Caso problema conocido de la Tanda 2 (hull convexo de 1.546 ha); sin capa editorial; permite ver si HDBSCAN resuelve lo que DBSCAN no pudo. Corredor propio detectado. |
| **Villa Crespo** | 234 | 9 | 24 % | Tamaño medio, sin capa editorial de referencia: caso "neutro" sin andamiaje adicional que ayude a interpretar. |
| **Avenida Caseros / Barracas** | 63 | 3 | 38 % | Evidencia escasa; contenedor degradado (quedó con 1 punto semilla tras depurar apartados). Caso de baja confianza. |
| **Costanera Norte** | 2 | 0 | 100 % | Evidencia insuficiente extrema: el fallback DBSCAN no encuentra nada. Caso de **fallo honesto** — el pipeline debe decir "no sé", no inventar un núcleo. |

## Nota sobre Palermo Soho / Palermo Hollywood

Diego propuso Palermo Soho y Palermo Hollywood como casos separados. En el prototipo V1 el
**contenedor de macrozona sigue al polo editorial** (doc 01 §4.4: las macrozonas no se
redefinen), y "Palermo" es un solo polo que contiene varias subzonas editoriales. Por eso
Soho y Hollywood no son macrozonas propias en este pipeline: son **subzonas dentro de
Palermo**, y el tablero de Palermo (Etapa V2-2) las superpone como capa de referencia para
poder juzgar, cluster por cluster, si corresponden a Soho, Hollywood, Las Cañitas u otra
subzona. Esto resuelve la intención de Diego sin tocar la definición de macrozona.

## Excluidas de esta tanda de validación (no se pierden, quedan para después)

Caballito, Microcentro y Centro, Puerto Madero y Recoleta ya tienen resultados en el
prototipo V1 (Etapas 3–5) pero no se les dedica tablero ni diagnóstico narrativo en esta
tanda, para mantener el foco en 8 casos diversos. Microcentro y Centro concentra 2 de los 6
clusters sobredimensionados detectados (432 y 190 puntos): entra igual a la segunda pasada
jerárquica (Etapa V2-4), que corre sobre **todos** los clusters sobredimensionados del
universo, no solo sobre los 8 casos seleccionados.
