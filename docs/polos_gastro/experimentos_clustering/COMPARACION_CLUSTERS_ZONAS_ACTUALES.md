# Comparación — Clusters exploratorios vs. zonas actuales (PolosGastro)

**Fecha:** 2026-07-07 · **Carácter:** lectura interna auxiliar. Los clusters son polígonos
exploratorios; **no constituyen límites oficiales** y **requieren revisión territorial**.
La capa editorial vigente (subzonas V4 y asignación `polo` de Fase 13) **no se modificó**.

Bases de la comparación: campo `polo` del input (13 polos) y contorno de
`subzonas_editoriales_geometrias.geojson` (Fase 16), dibujado como referencia punteada en
`mapa_poligonos_experimental.png`. Corrida: DBSCAN eps=400 m, min_samples=3, 93 puntos.

## 1. Clusters que coinciden con una zona clara

| Cluster | Composición | Lectura |
|---|---|---|
| C7 (8 pts) | San Telmo 7 + Caseros/Barracas 1 (limítrofe) | La coincidencia más nítida; cae dentro de los círculos editoriales de San Telmo |
| C1 (7 pts) | Villa Crespo 5 (+2 ajenos) | Núcleo claro de Villa Crespo |
| C4 (4 pts) | Palermo 4 | Subnúcleo interno de Palermo |
| C5 (3 pts) | Puerto Madero 3 | Dentro del rectángulo editorial de Puerto Madero |
| C8 (3 pts) | Belgrano 3 | Coincide con subzona editorial de Belgrano |
| C10 (3 pts) | Costanera Norte 3 | Núcleo costero consistente |

## 2. Clusters que mezclan zonas

- **C0**: Palermo 3 + "San Telmo" 1 + "Chacarita" 1 — los dos ajenos están físicamente en
  Palermo: **sedes/sucursales geocodificadas fuera de su polo**, no un hallazgo territorial.
- **C1**: incluye 1 "Palermo" y 1 "Costanera Norte" en Villa Crespo — mismo fenómeno.
- **C6**: Recoleta 3 + "Puerto Madero" 1.
- **C3**: Palermo 2 + Belgrano 1 (zona de borde Palermo/Colegiales).
- **C9** y **C11**: Av. Corrientes 2 + Caballito 1, y Av. Corrientes 2 + **Abasto 1** — esta
  última mezcla es *coherente* con la definición editorial (Abasto = subzona del polo
  Corrientes, no zona propia).

La mezcla es mayormente **diagnóstica de calidad de geolocalización**: señala con precisión
los casos `zona_sucursal_a_revisar` / `match_razonable_revisar_sede` pendientes de Fase 11.

## 3. Zonas que quedan fragmentadas

- **Palermo** (19 pts): se parte en 5 clusters (C0, C2, C3, C4 y aporte a C1) + 7 en ruido.
  A eps=400 la macrozona editorial no emerge como unidad; emergen subnúcleos.
- **Belgrano** (11 pts): C8 (3) + 1 punto en C3 + 5 en ruido; sus subzonas editoriales
  (Barrio Chino, Belgrano R, etc.) no se reconstruyen enteras con esta densidad.
- **Avenida Corrientes** (6 pts): repartida entre C9 y C11 + 2 en ruido — DBSCAN isotrópico
  corta el corredor lineal.

## 4. Zonas que no aparecen

- **Microcentro y Centro**: 7/7 puntos en ruido; ningún cluster. Corredor disperso a esta
  densidad de muestreo.
- **Caballito**: sin cluster propio (1 punto absorbido por C9, 4 en ruido).
- **Chacarita**: sin cluster propio (2 puntos en clusters ajenos, 4 en ruido).
- **Abasto**: sin cluster propio; su punto se integra a C11 (Corrientes) — consistente con su
  estatus editorial de subzona.

## 5. Puntos ruido / outliers

44 de 93 puntos (47.3 %), distribuidos en los 13 polos (máximos: Palermo 7, Microcentro 7,
Belgrano 5). En un universo semilla ralo, ruido = punto sin acompañamiento local a 400 m, no
dato inválido. Listado georreferenciado en `puntos_clustering_experimental.geojson`
(`cluster_id = -1`) y en gris en ambos mapas.

## 6. Limitaciones de la comparación

1. La capa editorial V4 usa radios y criterios gráficos aproximados, no límites medidos: la
   superposición es visual, no métrica.
2. El campo `polo` del input es asignación editorial previa, con 25+27 casos de sede aún en
   revisión — parte de la "mezcla" es error de geocodificación, no de delimitación.
3. Con ~7 puntos por polo, la ausencia de un cluster **no** implica ausencia de actividad
   gastronómica: implica muestreo insuficiente en esa zona.
4. Una sola configuración de parámetros; la alternativa 500/3 daría clusters más grandes y
   menos ruido.

## Lectura general

El experimento aporta dos usos auxiliares concretos: (a) **control de calidad de
geolocalización** (los clusters mixtos localizan exactamente las sedes dudosas) y
(b) **contraste de subnúcleos** dentro de macrozonas editoriales (Palermo, San Telmo,
Villa Crespo). No sustituye la delimitación editorial ni alcanza, con este universo, para
proponer áreas nuevas.
