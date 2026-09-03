# Comparación empírica — DBSCAN (tandas anteriores) vs. HDBSCAN vs. método híbrido

**Fecha:** 2026-07-08 · **Carácter:** experimental (Etapa 6 del prototipo V1).
Datos: `outputs/polos_gastro/experimentos/pipeline_microzonas_v1/metricas/`
(`comparacion_detectores.csv`, `resumen_por_metodo.csv`, `metricas_microzonas.csv`).
A diferencia de los documentos de diseño (que compararon en teoría), esta comparación corre
los tres enfoques **sobre el mismo universo V1** (4.615 entidades dentro de macrozonas).

## 1. Qué se comparó

| Enfoque | Configuración | Origen |
|---|---|---|
| DBSCAN continuidad | eps = 650 m, min_samples = 4, intra-macrozona | candidata "inclusiva" de la Tanda 2 (la mejor de 45 configuraciones probadas sobre la semilla) |
| DBSCAN local | eps = 150 m, min_samples = 4, intra-macrozona | escala de 1–2 cuadras, exigencia mínima |
| HDBSCAN | min_cluster_size = max(8, 3 % de la macrozona), min_samples = 5, epsilon de selección = 50 m, método eom | detector principal propuesto (doc 02 §2.2) |
| Híbrido | HDBSCAN + KDE de control (bw 100 m, umbral 40 % del máx local) + poligonización por reglas (corredor→cápsula; n<10→buffer-unión; resto→concave hull 0.5) + gates de QA | pipeline propuesto completo |

## 2. Resultado agregado (11 macrozonas con clusters; Costanera Norte quedó sin evidencia suficiente)

| Detector | Clusters totales | Ruido medio | Diámetro máx. de cluster | % medio de puntos en el cluster dominante |
|---|---|---|---|---|
| DBSCAN continuidad (650/4) | 11 | 8,3 % | **3.782 m** | **91,7 %** |
| DBSCAN local (150/4) | 48 | 11,7 % | 3.432 m | 74,4 % |
| HDBSCAN | **83** | 33,9 % | **1.314 m** | 29,9 % |

Lectura:

- **DBSCAN 650/4 no sobrevive al cambio de universo.** Con 106 puntos semilla era la
  candidata razonable; con cientos de puntos por macrozona produce UN cluster gigante por
  macrozona (91,7 % de los puntos clusterizados en el dominante, diámetros de hasta 3,8 km
  = el contenedor entero). No detecta microzonas: redibuja la macrozona. Confirma
  empíricamente que el `eps` óptimo depende del universo, el defecto estructural señalado
  en el diseño.
- **DBSCAN 150/4 mejora pero encadena.** 48 clusters, poco ruido, pero en zonas densas
  encadena núcleos distintos a través de calles con oferta continua (diámetros > 3 km en
  Corrientes y Caballito; 74 % en el dominante). El encadenamiento es el mecanismo del
  algoritmo, no un parámetro mal elegido.
- **HDBSCAN separa núcleos a su densidad natural.** 83 clusters, ninguno mayor a 1,3 km de
  diámetro, cluster dominante con solo el 30 % de los puntos: dentro de una misma macrozona
  emergen núcleos separados (el caso buscado: en Palermo separa Soho de Hollywood, Las
  Cañitas y dos núcleos menores; ver mapas de la Etapa 3). El costo es un ruido medio de
  34 %: un tercio de las entidades no pertenece a ningún núcleo denso. Ese ruido es
  **información honesta** (oferta dispersa existe), no pérdida: queda disponible con
  etiqueta -1.

## 3. Poligonización (mismos clusters HDBSCAN, siete construcciones)

De `resumen_por_metodo.csv` (83 clusters):

| Método | Superficie mediana (ha) | Contención mediana | Compacidad mediana | % pasa gates QA |
|---|---|---|---|---|
| buffer_union_r70 | 4,6 | 100 % | 0,30 | 95,2 % |
| hibrido_reglas | 6,8 | 100 % | 0,58 | 92,8 % |
| concave_hull_r03 | 6,4 | 100 % | 0,52 | 91,6 % |
| concave_hull_r05 | 6,6 | 100 % | 0,60 | 91,6 % |
| convex_hull | 7,8 | 100 % | 0,80 | 90,4 % |
| kde_contorno_40pct | 10,4 | 95,3 % | 0,93 | 89,2 % |
| capsula_pca (solo 4 corredores) | 10,5 | 79,9 % | 0,35 | 100 % |

- El **buffer-unión** es el más conservador en superficie pero produce formas "esponjosas"
  multiparte en clusters grandes (ver `poligonos/mapas/comparativa_palermo.png`): sirve
  para n chico, no como método general — exactamente el rol que le asignaba el diseño.
- Los **concave hull** dan el mejor equilibrio forma/contención; la diferencia entre ratio
  0.3 y 0.5 es menor a escala de microzona.
- El **contorno KDE** recorta al corazón denso (contención 95 %) con la mejor compacidad;
  como capa de comunicación y control cruzado cumple; como huella única excluye locales
  de borde reales.
- La **cápsula PCA** aplicó sola en los 4 clusters con forma de corredor (Corrientes C5 de
  128 locales, Palermo C6, Chacarita C0, Puerto Madero C1) y pasa todos los gates; su
  contención del 80 % delata que el eje PCA es un sustituto imperfecto del eje vial real
  (pendiente ya identificado: base de callejero GCBA).

## 4. Ventajas y desventajas (síntesis)

**DBSCAN (como en Tandas 1–2)**
- ✔ Simple de explicar; un solo parámetro de escala; ya calibrado y documentado.
- ✔ Con universo chico (semilla) es lo único que corre.
- ✘ `eps` global no transfiere entre universos ni entre macrozonas de densidad distinta
  (demostrado: la candidata de Tanda 2 colapsa a 1 cluster por macrozona).
- ✘ Encadena núcleos distintos en zonas densas; no da confianza por punto.

**HDBSCAN**
- ✔ Detecta núcleos a densidad variable sin `eps`; diámetros acotados; outliers explícitos
  que alimentan la revisión de calidad de sedes (círculo datos↔clustering).
- ✔ Parámetro principal interpretable ("mínimo de locales que forman un núcleo").
- ✘ Ruido alto (34 %) que hay que comunicar bien; menos intuitivo; en macrozonas con
  < 30 puntos no aplica (Costanera Norte quedó declarada sin evidencia suficiente).
- ✘ En macrozonas muy homogéneas produce clusters grandes que igual exceden el gate de
  35 ha (6 casos, p. ej. Microcentro C0 con 432 locales / 92 ha): detecta bien que "todo
  el centro es denso", pero la microzona útil exige una segunda pasada (ver informe final).

**Híbrido (HDBSCAN + KDE + reglas + QA)**
- ✔ Mejor paquete completo: detección adaptativa + control visual/estadístico independiente
  (KDE) + polígono adecuado a la forma (compacto/corredor/chico) + gates que rechazan lo
  absurdo. 92,8 % de los polígonos pasa QA sin intervención.
- ✔ Es el único de los tres que produce salidas listas para revisión humana con semántica
  editorial (microzona subordinada a macrozona).
- ✘ Más piezas = más parámetros que justificar (todos registrados en
  `parametros_pipeline_v1.json`); la cápsula de corredor necesita el eje vial real para ser
  publicable.

**Conclusión operativa:** mantener DBSCAN solo como corrida de continuidad histórica.
El detector para el pipeline definitivo es HDBSCAN dentro del esquema híbrido, con la
segunda pasada para núcleos > 35 ha como principal ajuste pendiente.
