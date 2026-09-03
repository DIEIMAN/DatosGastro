# Tipología automática de polos (Etapa V2-5)

**Fecha:** 2026-07-08 · **Carácter:** experimental. Clasificación por umbrales explícitos
(`scripts/.../s08_tipologia_polos.py`), no ajustada a mano por macrozona. Fuente:
`outputs/.../validacion/tipologia_polos.csv`.

**Respuesta a la pregunta de fondo: sí, existen categorías distintas de polos**, y la
clasificación automática las separa sin forzarlas — las 12 macrozonas cayeron en 5
categorías distintas, no en una sola bolsa.

## Reglas de clasificación (en orden de prioridad)

1. **EVIDENCIA_INSUFICIENTE** — < 30 entidades asignadas o 0 clusters.
2. **CONTENEDOR_BAJA_CONFIANZA** — contenedor degradado o < 80 entidades.
3. **CORREDOR_DOMINANTE** — clusters marcados `es_corredor` concentran ≥ 30 % de los
   locales clusterizados.
4. **NUCLEO_DOMINANTE_SATELITES** — el cluster más grande concentra ≥ 45 % de los locales.
5. **MULTI_NUCLEO** — ≥ 3 clusters con ≥ 15 locales cada uno, ninguno domina.
6. **POLO_DISPERSO** — resto (clusters chicos y fragmentados, sin núcleo ni corredor).

## Resultado

| Macrozona | Entidades | Clusters | % en dominante | % en corredores | Tipología |
|---|---|---|---|---|---|
| Avenida Corrientes | 860 | 9 | 22 % | 21 % | MULTI_NÚCLEO |
| Caballito | 352 | 9 | 23 % | 0 % | MULTI_NÚCLEO |
| Chacarita | 226 | 7 | 22 % | 22 % | MULTI_NÚCLEO |
| Palermo | 1.043 | 8 | 29 % | 9 % | MULTI_NÚCLEO |
| Recoleta | 249 | 11 | 17 % | 0 % | MULTI_NÚCLEO |
| San Telmo | 218 | 10 | 20 % | 0 % | MULTI_NÚCLEO |
| Villa Crespo | 234 | 9 | 26 % | 0 % | MULTI_NÚCLEO |
| Belgrano | 158 | 4 | 69 % | 0 % | NÚCLEO_DOMINANTE + satélites |
| Microcentro y Centro | 1.073 | 5 | 52 % | 0 % | NÚCLEO_DOMINANTE + satélites |
| Puerto Madero | 137 | 8 | 20 % | 13 % | POLO_DISPERSO |
| Avenida Caseros / Barracas | 63 | 3 | 59 % | 0 % | CONTENEDOR_BAJA_CONFIANZA |
| Costanera Norte | 2 | 0 | — | — | EVIDENCIA_INSUFICIENTE |

## Lectura

- **7 de 12 son multi-núcleo** (varios corazones comparables, ninguno domina): el
  comportamiento más frecuente y, según el diagnóstico editorial, el mejor resuelto por
  HDBSCAN.
- **2 son núcleo dominante + satélites** (Belgrano 69 %, Microcentro 52 %): ambas fueron
  justamente las que produjeron clusters sobredimensionados (Etapa V2-4). Tiene sentido:
  un cluster que concentra la mitad o más de los locales de su macrozona casi
  necesariamente supera el gate de superficie.
- **Ningún caso quedó como "corredor dominante" puro** (umbral 30 % no alcanzado en
  ninguna macrozona): Avenida Corrientes (21 %) y Chacarita (22 %) tienen corredores
  reales y visibles (confirmado en el diagnóstico editorial), pero conviven con núcleos no
  lineales dentro de la misma macrozona — el corredor nunca es toda la historia. Esto
  sugiere que "corredor" es mejor pensado como **una propiedad de un cluster**, no como una
  categoría de macrozona completa (coherente con cómo ya está implementado: `es_corredor`
  es un flag por cluster, no por macrozona).
- **Puerto Madero es el único "disperso" con evidencia suficiente**: 8 clusters chicos,
  ninguno domina, y un 13 % en corredores (el eje costero) que tampoco alcanza a
  organizar la zona. Con docks + costanera + área a validar (ver capa editorial), es
  plausible que Puerto Madero sea estructuralmente más disperso que los demás polos.
- **Caseros/Barracas y Costanera Norte confirman la categoría "sin datos suficientes"**:
  no son un fallo de método, son macrozonas donde el universo F01+F02 actual no alcanza.

## Implicancia para el diseño

La tipología sugiere que un pipeline V2 podría **tratar distinto cada categoría en vez de
aplicar el mismo HDBSCAN a todas**: a las núcleo-dominante aplicarles la segunda pasada
por defecto (Etapa V2-4); a las multi-núcleo dejarlas como están (funcionan bien); a las
dispersas o de baja confianza, marcarlas explícitamente como "no aptas para microzonas
todavía" en vez de forzar un resultado. Ver recomendación completa en Etapa V2-7.
