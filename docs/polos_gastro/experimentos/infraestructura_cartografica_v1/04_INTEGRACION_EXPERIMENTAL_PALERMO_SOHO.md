# Integración experimental — Palermo Soho con contorno editorial real (Etapa Infra-4)

**Fecha:** 2026-07-08 · **Carácter:** prueba experimental paralela. No reemplaza el
contenedor del prototipo V1 ni cambia ningún parámetro de HDBSCAN. Compara, sobre el
mismo universo V1, el pipeline con el contenedor viejo (hull de la semilla completa de
"Palermo") contra el mismo pipeline con el polígono editorial real de Palermo Soho
(Etapa Infra-4, trazado sobre el callejero GCBA a partir de las 4 calles límite de la
ficha PG001A).

## Qué se construyó

1. **Polígono real de Palermo Soho** (`construir_poligono_real_palermo_soho.py`):
   se tomaron los tramos reales de Scalabrini Ortiz, Córdoba, Juan B. Justo y Santa Fe del
   callejero GCBA, se ajustó una recta a cada uno (cuadrados mínimos) y se particionó el
   plano con las 4 rectas extendidas; se seleccionó la pieza que contiene el centro
   editorial de la elipse de fase16 (localizador, no geometría final). Se corrió el mismo
   método para Palermo Hollywood (con Dorrego en vez de Scalabrini Ortiz) como control
   cruzado: **154,9 ha para Soho, 88,5 ha para Hollywood**, adyacentes y compartiendo el
   borde de Juan B. Justo — geometría verificada visualmente contra el callejero
   (`tmp/qa_palermo_soho_hollywood.png`).
2. **Normalizador de esquema** (`normalizar_capa_editorial.py`): junta los polígonos
   crudos y completa los 16 atributos del esquema de Infra-2 →
   `macrozonas_editorial_v1_borrador.geojson`.
3. **Simulación del pipeline completo** (`simular_pipeline_editorial_palermo_soho.py`):
   editorial.geojson → filtrado espacial → HDBSCAN (mismos parámetros del prototipo V1)
   → segunda pasada donde corresponde → microzonas, comparado contra lo que el prototipo
   V1 ya tenía para esos mismos puntos.

## Resultado: Mundo A (contenedor viejo) vs. Mundo B (contorno real)

| | Mundo A (hull de semilla, "Palermo" completo) | Mundo B (polígono real Palermo Soho) |
|---|---|---|
| Universo de entrada | 1.043 entidades (Soho+Hollywood+Las Cañitas+Chico+Botánico mezclados) | **373 entidades** (solo Soho) |
| Clusters HDBSCAN | 8 (incluye Hollywood, Las Cañitas, etc. como clusters aparte) | 4 |
| Clusters sobredimensionados (>35 ha) | 2 (C2 Hollywood 87 ha, C5 "Soho-ish" 73 ha) | 1 (58,5 ha) |
| Ruido | 20 % | 18,5 % antes de segunda pasada; **46 % después** |

## Hallazgo 1 (positivo): el contorno real separa Soho de Hollywood de raíz

De las 373 entidades dentro del polígono real de Soho, **ninguna pertenecía al viejo
cluster C2** (el que la validación había identificado como "cae casi entero sobre la
elipse Palermo Hollywood"). Las que sí venían del prototipo V1 se repartían entre los
clusters C4, C5, C6 y C7 y 62 que eran ruido — es decir, el contorno real logra
exactamente lo que el diagnóstico editorial (Etapa V2-3) señaló como problema estructural:
**HDBSCAN tenía que resolver con densidad la separación Soho/Hollywood que debería venir
dada por el contorno**, y ahora ya no tiene que hacerlo. Esto confirma la causa raíz
identificada en la validación (el contenedor, no el algoritmo).

## Hallazgo 2 (neutral): el contorno real NO resuelve el cluster sobredimensionado

Incluso con el universo ya restringido a solo Palermo Soho, aparece un cluster de 251
entidades / 58,5 ha (el 67 % de las entidades de la zona) — el mismo patrón "núcleo
dominante" que Belgrano o Microcentro. Esto es consistente con la hipótesis de la
validación (Etapa V2-3): **Palermo Soho probablemente tiene 2-3 corazones propios**, y
ese problema es independiente de la calidad del contorno — lo resuelve (parcialmente) la
segunda pasada, no un mejor polígono editorial.

## Hallazgo 3 (costo real, a documentar sin disimular): la segunda pasada sube el ruido a 46 %

Al aplicar la segunda pasada (leaf, epsilon 25 m) sobre el cluster de 251 puntos, aparecen
11 subclusters — más granularidad, igual que en la validación (Etapa V2-4) — pero el ruido
total pasa de 18,5 % a 46 %. Es el mismo trade-off ya documentado en Belgrano: cuando el
cluster grande no es perfectamente homogéneo, la segunda pasada gana precisión y pierde
cobertura. **El mapa comparativo (`comparativo_mundo_a_vs_b_palermo_soho.png`) muestra
esto sin maquillarlo**: el panel B tiene visiblemente más "x" grises que el panel A.

## Respuesta a la pregunta de la etapa

> ¿El cambio realmente elimina los problemas detectados en la validación?

**Parcialmente, y de forma distinta según el problema:**

- El problema de **"cluster fuera de zona editorial" / "identidades mezcladas"**
  (el hallazgo más grave de la validación, presente en San Telmo y en la propia Palermo
  Hollywood/Soho): **sí, se elimina** — es exactamente lo que el contorno real está
  diseñado para resolver, y el Hallazgo 1 lo confirma con datos.
- El problema de **"núcleo dominante sobredimensionado"**: **no se elimina con el
  contorno**; sigue necesitando la segunda pasada (ya diseñada en la validación), con el
  mismo costo de ruido ya documentado ahí. Contorno real y segunda pasada son mejoras
  **complementarias**, no sustitutas una de la otra — confirma la recomendación de la
  Etapa V2-7 (atacar ambas, no una sola).

## Limitación de este caso de prueba

Palermo Soho fue el único caso con las 4 calles límite documentadas explícitamente
(Infra-1): es el mejor caso posible, no uno representativo. Para el resto de las 12
macrozonas (donde la ficha solo dice "Barrio X" o "no definida"), trazar el contorno real
va a requerir criterio editorial humano además del callejero — el método de este script
(4 calles → partición del plano) no se generaliza automáticamente a esos casos.
