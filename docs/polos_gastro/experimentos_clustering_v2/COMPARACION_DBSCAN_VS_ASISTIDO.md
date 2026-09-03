# Comparación — DBSCAN global vs. polígonos asistidos por subzona (v2)

**Fecha:** 2026-07-07 · Ambas salidas son **capas auxiliares exploratorias**: no constituyen
límites oficiales y requieren revisión territorial. Mapa conjunto:
`outputs/polos_gastro/experimentos_clustering_v2/comparativo_dbscan_vs_asistido.png`.

## 1. Ruido

| Salida | Puntos sin asignar |
|---|---|
| DBSCAN estricto (500/4) | 53 (57.0 %) |
| DBSCAN equilibrado (400/3, = tanda 1) | 44 (47.3 %) |
| DBSCAN inclusivo (650/4) | **27 (29.0 %)** |
| Asistido por subzona | 0 sin asignar por construcción; 10 (10.8 %) excluidos como "apartados de su zona" |

El asistido no "resuelve" el ruido: lo reemplaza por pertenencia editorial previa. Los 10
excluidos son la parte honesta del equivalente al ruido: puntos cuya ubicación contradice su
etiqueta.

## 2. Cantidad de polígonos

DBSCAN: 6 / 12 / 10 según candidata. Asistido: **14** (13 polos, con Palermo dividido en
Las Cañitas y Palermo Soho, y Abasto como grupo propio de 1 punto).

## 3. Coherencia territorial

- **Asistido:** cada polígono corresponde a una zona editorial conocida y lleva confianza
  (11 alta, 2 media, 1 baja). Pero 3 grupos dispersos producen hulls gigantes no
  interpretables (Chacarita 1.546 ha, Caseros/Barracas 931 ha, Costanera Norte 636 ha),
  marcados `extension_a_revisar` y dibujados en trazo tenue/rojo.
- **DBSCAN:** los clusters que emergen son compactos y localmente coherentes (mediana
  3–6 ha en equilibrado), pero no cubren todas las zonas y sus etiquetas de polo se mezclan
  donde hay sedes mal geocodificadas.

## 4. Separación de zonas conocidas

| Zona | DBSCAN (equilibrado / inclusivo) | Asistido |
|---|---|---|
| Palermo | 5 subnúcleos / Soho+Hollywood unidos | 2 subzonas editoriales (Cañitas, Soho) |
| Corrientes | cortada en 2 clusters | 1 polígono (convexo, corredor) |
| Abasto | absorbido con Corrientes (coherente con su estatus de subzona) | grupo propio, confianza baja (1 pt) |
| Belgrano | 1 cluster chico + ruido | 1 polígono (6 pts, 3 apartados excluidos) |
| San Telmo | cluster nítido (mejor caso) | polígono compacto (11.4 ha) |
| Puerto Madero | 1–2 clusters | 1 polígono (2 apartados excluidos) |
| Microcentro | sin cluster en equilibrado | 1 polígono (7 pts) |

## 5. Mezcla de zonas que deberían estar separadas

- DBSCAN mezcla **etiquetas** (no territorios): C0/C1/C6 incluyen locales de polos lejanos
  porque la sede geocodificada está en otra zona. A eps ≥ 800 mezcla territorios de verdad.
- El asistido no mezcla zonas por construcción, pero **hereda** los errores de
  geolocalización: sin la depuración de apartados, Belgrano llegaría hasta Recoleta y San
  Telmo hasta Palermo. La depuración excluyó 10 puntos con umbral documentado
  (máx(1500 m, 3× distancia mediana al centro del grupo)).

## 6. Zonas sin representación

- DBSCAN equilibrado: Microcentro, Caballito y Chacarita sin cluster propio; estricto deja
  además fuera a Corrientes, Caseros/Barracas y Abasto.
- Asistido: **ninguna zona queda sin polígono** (todas las 14 tienen salida, con confianza
  y banderas de calidad).

## 7. Qué salida es más útil para revisión humana

**La asistida por subzona**, por tres razones: cubre todas las zonas del informe, expone la
calidad de cada grupo (confianza, apartados excluidos, extensión a revisar) y su lista de 10
puntos apartados es un insumo directo para la revisión pendiente de sedes de Fase 11.
El DBSCAN inclusivo (650/4) queda como mejor diagnóstico de concentraciones emergentes.

## 8. Qué salida NO conviene usar

- **DBSCAN estricto (500/4):** 57 % de ruido y solo 6 clusters; útil apenas como control de
  robustez ("qué sobrevive con exigencia alta").
- **Los 3 polígonos asistidos con `extension_a_revisar`** (Chacarita, Caseros/Barracas,
  Costanera Norte) tal como están: el hull no representa una concentración sino la dispersión
  del muestreo; requieren depuración manual de sus puntos antes de cualquier uso.
- Cualquier configuración con eps ≥ 800 o min_samples = 2 (fusión / pares).

## Criterio general (confirmado por esta tanda)

DBSCAN sirve para **detectar concentraciones emergentes** y auditar calidad de
geolocalización; la poligonización asistida sirve para **revisar y mejorar áreas ya
definidas editorialmente**. Ninguna de las dos produce límites oficiales.
