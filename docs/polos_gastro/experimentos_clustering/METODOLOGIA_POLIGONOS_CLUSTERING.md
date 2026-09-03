# Metodología — Polígonos exploratorios por clustering espacial (PolosGastro)

**Fecha:** 2026-07-07 · **Carácter:** experimento interno auxiliar.
Los polígonos generados son **polígonos exploratorios** (áreas estimadas de concentración):
**no constituyen límites oficiales** y **requieren revisión territorial**. Este experimento no
modifica el informe vigente de PolosGastro, ni la Fase 25, ni los PDFs finales, ni los mapas
actuales.

## 1. Objetivo

Evaluar si un algoritmo de clustering espacial sobre los locales semilla georreferenciados
aporta una **capa auxiliar** útil para contrastar (no reemplazar) las delimitaciones
editoriales de polos y ejes gastronómicos.

## 2. Input usado

`outputs/polos_gastro/fase13_mapas/tablas/locales_para_mapa_revision.csv`
- 106 locales del universo semilla de PolosGastro, con lat/lon completas, polo, subzona y
  estado consolidado de la Fase 11 (Google Places ya descargado; **no se ejecutó ninguna
  consulta nueva**).
- Trazabilidad: generado por `scripts/polos_gastro/generar_mapas_fase13.py` a partir del
  consolidado de tandas de Fase 11 (`consolidado_tandas_google_places.csv`).
- Cartografía de apoyo (solo lectura): `PolosGastro/cartografia/comunas_caba.geojson`
  (filtro del límite de CABA) y `barrios_caba.geojson` (fondo de mapa).
- Capa editorial de referencia (solo lectura, sin modificar):
  `outputs/polos_gastro/fase16_mapas_editoriales_v4/tablas/subzonas_editoriales_geometrias.geojson`.

Ver alternativas evaluadas y descartadas en `INVENTARIO_PUNTOS_DISPONIBLES.md`.

## 3. Variables usadas

- **Coordenadas (lat/lon)** proyectadas a CRS métrico: única variable de entrada del
  clustering (distancia euclidiana en metros).
- **Peso por punto = 1 (uniforme).** El input elegido no trae rating ni reseñas. El script
  contempla un peso auxiliar `score_aux = max(rating − 3.5, 0) × log1p(reviews)` si el input
  los tuviera, solo como peso de densidad; **nunca** como afirmación de calidad comercial ni
  como ordenamiento público de locales.
- `polo` y `subzona` se usan **a posteriori** para caracterizar cada cluster
  (polo mayoritario, distribución), no como variable del algoritmo.

## 4. Qué se excluyó

| Exclusión | Cantidad | Motivo |
|---|---|---|
| Filas `estado_consolidado = duplicado_probable` | 11 | No doble-contar densidad con el mismo local repetido |
| Puntos fuera del polígono de comunas de CABA | 2 | Un local de Belgrano geolocalizado en provincia (−34.4796, −58.5707) y un punto de Puerto Madero sobre el borde costero (−34.6334, −58.3433), fuera del polígono de comunas |
| Rating/reseñas de los archivos `_interno` de Fase 11 | — | Decisión de alcance: no arrastrar datos internos de Google Places a outputs experimentales |
| Universo público F01–F05 (`data/processed/`) | — | Separación de universos (guardrail 3); sería un experimento futuro separado |

## 5. Algoritmo usado

**DBSCAN** (`scikit-learn` 1.9.0), elegido por ser simple, auditable, sin necesidad de fijar
la cantidad de clusters a priori y con noción explícita de ruido/outliers.
- CRS métrico: **EPSG:5347** (POSGAR 2007 / Argentina faja 5), adecuado para CABA.
- Distancia euclidiana en metros; `sample_weight` uniforme (= 1).

Nota: scikit-learn no estaba en `.venv`; se instaló el 2026-07-07 con autorización explícita
de Diego (`pip install scikit-learn`, agrega scipy/joblib/threadpoolctl, no modifica paquetes
existentes).

## 6. Parámetros probados

Grilla de 24 combinaciones (tabla completa en
`outputs/polos_gastro/experimentos_clustering/parametros_probados.csv`):
- `eps_m`: 150, 200, 250, 300, 400, 500
- `min_samples`: 3, 4, 5, 6

Resultado general de la grilla: con 93 puntos válidos repartidos en 13 polos (~7 por polo),
la densidad es baja y **ninguna configuración baja del 43 % de ruido**; con `min_samples ≥ 5`
casi no se forman clusters, y con `eps ≤ 300` el ruido supera el 64 %.

## 7. Cómo se eligió la configuración

Criterio documentado (implementado en `elegir_configuracion()` del script):

1. **Candidatas:** 6 ≤ clusters ≤ 20; ruido ≤ 55 %; ningún cluster con más del 50 % de los
   puntos (que no fusione media Ciudad ni fragmente todo).
   El techo de ruido es alto a propósito: en un universo semilla ralo, "ruido" significa
   *punto sin acompañamiento local suficiente*, no dato inválido.
2. **Entre candidatas** se minimiza `|n_clusters − n_polos(13)| + pct_ruido/10`; empate →
   menor `eps` (polígonos más compactos y auditables).

Solo dos configuraciones resultaron candidatas: `eps=400/min_samples=3` (12 clusters, 47.3 %
ruido, cluster máximo 8 puntos) y `eps=500/min_samples=3` (10 clusters, 43.0 % ruido, cluster
máximo 15). Se eligió **eps = 400 m, min_samples = 3**: cantidad de clusters más cercana a la
escala editorial conocida (13 polos) y hulls más compactos, a costa de ~4 puntos porcentuales
más de ruido. La elección puede forzarse por CLI (`--eps`, `--min-samples`) para probar la
alternativa.

## 8. Cómo se generaron los polígonos

Por cada cluster (nunca sobre el ruido):
1. `concave_hull(ratio=0.5, allow_holes=False)` de shapely 2.1 si el cluster tiene ≥ 4 puntos
   y el resultado es válido y con área > 0; si no, **convex hull** (baseline).
2. **Buffer suave de 40 m** en todos los casos, para que clusters chicos o colineales no
   queden como línea/punto degenerado.
3. No se unieron clusters entre sí ni se aplicó ninguna regla de fusión.

Atributos por polígono: `cluster_id`, `n_puntos`, `algoritmo`, `eps_m`, `min_samples`,
`area_m2`, `area_ha`, `fuente_input`, `polo_mayoritario`, `porcentaje_polo_mayoritario`,
`distribucion_polos` y `nota` ("Polígono exploratorio auxiliar. No constituye límite oficial.").

## 9. Limitaciones

1. **El input es un universo semilla curado, no un censo**: la densidad refleja el muestreo
   editorial (~7 locales por polo), no la oferta gastronómica real. Los clusters describen la
   estructura espacial del universo semilla.
2. **Ruido alto (47.3 %)** intrínseco a esa baja densidad; polos con puntos dispersos
   (Microcentro y Centro: 7/7 en ruido) no forman cluster.
3. **Sedes/sucursales mal geolocalizadas mezclan polos**: 25 filas del input están en estado
   `zona_sucursal_a_revisar` y 27 `match_razonable_revisar_sede`; varios clusters mezclan
   polos lejanos porque un local quedó geocodificado en otra zona (ver comparación).
4. **DBSCAN isotrópico no captura corredores lineales** (Avenida Corrientes, Microcentro):
   tiende a cortarlos o a dejarlos en ruido.
5. **Polígonos chicos** (0.66–21.2 ha) frente a las zonas editoriales: delimitan la mancha de
   los puntos disponibles, no el área percibida del polo.
6. La comparación con subzonas editoriales es **visual y aproximada** (la capa editorial usa
   radios/criterios gráficos, no límites medidos).

## 10. Por qué no son límites oficiales

Son áreas estimadas por un algoritmo sobre una muestra curada y parcialmente sin validar
(estados de revisión pendientes de Fase 11), con parámetros elegidos por un criterio interno
de trabajo. No hubo validación territorial, ni participación de las áreas competentes, ni
contraste con normativa o delimitaciones administrativas. Su único uso legítimo es como
**capa auxiliar de contraste interno**.

## 11. Revisión humana faltante

- Validar las sedes observadas: los clusters que mezclan polos lejanos señalan exactamente
  los casos `zona_sucursal_a_revisar` / `revisar_sede` de Fase 11.
- Revisar los 2 puntos excluidos por caer fuera del polígono de comunas.
- Mirar los dos mapas PNG y decidir si la escala de los polígonos aporta al contraste
  editorial o si conviene otra representación (densidad kernel, corredores).
- Decidir si se repite la corrida con `eps=500/min_samples=3` (alternativa candidata).

## 12. Próximos pasos (propuestos, no ejecutados)

1. Revisión visual humana de los dos mapas y del `resumen_clusters.csv`.
2. Si el enfoque sirve: corrida separada sobre el universo público F01–F05 (sin mezclar
   universos), con su propia lectura metodológica.
3. Evaluar variantes para corredores lineales (buffers sobre ejes, densidad kernel).
4. Recién con revisión territorial, discutir si alguna área estimada merece pasar a insumo
   editorial — siempre como contraste, nunca como límite oficial.
