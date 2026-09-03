# Especificación de repetición — Belgrano (red multinuclear)

Estado: EXPERIMENTAL / NO OFICIAL. Fecha de corte: 2026-07-10.
Es un diseño: **no ejecuta nada**. La corrida es local (universo experimental ya
almacenado + capas locales); no requiere APIs, Google Places ni descargas.
Plan de pruebas tabulado: `outputs/.../decisiones_y_repeticiones_pipeline_hibrido_v1/tabla_plan_pruebas_belgrano.csv`.

## 1. Problema a resolver

El prototipo v1 produjo 6 núcleos visualmente convincentes con robustez por bloques
0,39. La repetición debe explicar **por qué** la robustez fue baja y entregar un
conjunto pequeño de núcleos con estabilidad cuantificada por núcleo — o concluir que no
hay núcleos firmes con las fuentes actuales.

Hipótesis rivales a discriminar (no excluyentes):

- **H1 — Contenedor:** el contenedor actual (unión de corredores de 250 m sobre
  Juramento/Libertador/Cabildo) corta estructura. Indicios: 32,7 % de puntos a ≤100 m
  del borde; encoger 100 m duplica el ruido (12,8→26,0 %); la propia ficha del
  contenedor registra 53 entidades conocidas fuera de toda macrozona; anillo externo de
  200 m con 131 F01/F02 + 157 Places ya almacenados.
- **H2 — Parámetros/método:** la partición depende del detector y sus parámetros
  (ARI grafo vs. HDBSCAN eom = 0,07; eom vs. leaf = 0,16), no de la estructura.
- **H3 — Fuentes:** la multinuclearidad la aporta la mezcla; F01/F02 solos dan 2
  clusters y F01 solo es 100 % ruido, con 56,4 % Places en el universo. Parte de los
  núcleos puede ser artefacto de dónde mira Places.
- **H4 — Estructura débil real:** Belgrano simplemente no tiene núcleos separables al
  nivel de ruido actual, y la lectura correcta es densidad continua (KDE) sin unidades.

## 2. Universo y reglas

- Universo: el mismo del experimento v1 (F01/F02 + Places sanitizado, deduplicado), sin
  agregar ni quitar puntos. Los anillos externos ya almacenados se usan **solo** para
  diagnóstico de borde; no se incorporan al universo sin rededuplicación (regla del
  experimento v1).
- Sin KMeans en ninguna etapa. Sin cantidad objetivo de núcleos. Sin nombres en ninguna
  salida intermedia (solo códigos BEL_Rxx_Nyy).
- Todas las corridas con semillas registradas y parámetros en el metadata.
- Corregir la discrepancia de conteo v1 (CSV 152 vs. GeoJSON 150): definir el conteo
  por **membresía de comunidad** y derivar el hull después; el conteo por contención en
  hull se reporta aparte si difiere.
- Entorno: `.venv` existente. Documentado: scikit-learn 1.9.0 lanza `TypeError` con
  `cluster_selection_epsilon > 0`; por lo tanto la grilla HDBSCAN corre con epsilon 0 y
  el efecto epsilon queda explícitamente fuera de alcance (no imputar). No instalar
  librerías sin permiso; Leiden (igraph/leidenalg) queda como opcional condicionado.

## 3. Diseño de pruebas

### 3.1 Comparación HDBSCAN (H2)

- Grilla: `cluster_selection_method` ∈ {eom, leaf} × `min_cluster_size` ∈ {8, 10, 12,
  15, 20} × `min_samples` ∈ {3, 5, 8, 10}; epsilon = 0 (limitación documentada).
- Registrar por configuración: nº clusters, % ruido, tamaño del mayor cluster.
- Matriz ARI entre todas las configuraciones; identificar la región de la grilla donde
  la partición es localmente estable (bloques de configuraciones vecinas con ARI ≥ 0,6
  entre sí).
- Sin KMeans; ninguna configuración se elige por producir "seis" núcleos.

### 3.2 Grafo de proximidad (H2)

- Grafo k-NN mutuo o por radio sobre distancias métricas (EPSG:5347).
- Umbrales **derivados de la distribución de distancias locales**: cuantiles
  {0,40; 0,50; 0,60; 0,75; 0,90} de la distancia al k-ésimo vecino, con k ∈ {3, 5, 8}
  (v1 usó solo q75 con k=5 → 80 m). Ningún umbral se elige por la cantidad de núcleos
  que produce.
- Registrar por umbral: nº comunidades, % puntos en comunidades ≥ tamaño mínimo,
  modularidad, nº aristas.
- **Persistencia entre umbrales:** para cada comunidad, Jaccard máximo contra las
  comunidades del umbral vecino; una comunidad es "persistente" si mantiene
  Jaccard ≥ 0,6 en al menos 3 umbrales consecutivos. AMI/ARI global entre particiones
  de umbrales consecutivos como curva de estabilidad.

### 3.3 Comunidades (H2)

- Métodos disponibles sin instalar nada (networkx 3.6.1): greedy modularity (v1),
  Louvain (`nx.community.louvain_communities`), label propagation.
- Louvain es estocástico: 20 corridas con semillas distintas; estabilidad de membresía
  por punto = frecuencia de co-asignación (matriz de consenso); membresía media por
  comunidad.
- Comparar los tres métodos entre sí (ARI) y contra la región estable de HDBSCAN
  (3.1). Leiden: solo si Diego autoriza instalar `python-igraph`+`leidenalg`; no es
  bloqueante.
- Prohibido asignar nombres durante toda la prueba.

### 3.4 KDE como contraste (H2/H4)

- KDE con bandwidth ∈ {60, 80, 100, 140} m sobre grilla de 25 m.
- Máximos locales por bandwidth; un máximo es **persistente** si aparece (±100 m) en
  ≥ 3 de los 4 bandwidths.
- Cruce con comunidades: distancia centroide-comunidad ↔ máximo persistente más
  cercano; comunidad "respaldada por KDE" si ≤ 150 m y solape de área ≥ 0,5 (v1 ya
  reporta `solape_kde` por núcleo: 0,39–1,0).
- Si H4 fuera cierta, se verá aquí: máximos persistentes pocos y mesetas anchas sin
  separación.

### 3.5 Bootstrap espacial por bloques (todas las H)

- Tamaños de bloque: {150, 200, 300, 400} m (v1 usó 200/300); 50 repeticiones por
  tamaño (v1 usó 20); submuestreo de 80 % de bloques sin reemplazo (mismo esquema v1,
  documentado como limitación: no es bootstrap con reemplazo).
- Métricas por repetición y núcleo candidato:
  - **Supervivencia:** fracción de repeticiones donde existe una comunidad con
    Jaccard ≥ 0,5 contra el núcleo base.
  - **Variación del centro:** desplazamiento del centroide (m), p50 y p90.
  - **Variación de extensión:** área del hull (ha), coeficiente de variación.
  - **Composición por fuente:** % Places dentro del núcleo, rango entre repeticiones.
- Reportar ARI global (media, p10, mínimo) por tamaño de bloque — no solo la media
  (lección de v1: la media 0,57 de San Telmo escondía p10 negativo).

### 3.6 Sensibilidad a bordes (H1) — sin ejecutar Places

- Repetir la detección con: (i) contenedor v1; (ii) contenedor v1 encogido 100 m;
  (iii) **contenedor de contraste: barrio oficial Belgrano completo**
  (`PolosGastro/cartografia/barrios_caba.geojson`, capa local existente); (iv) barrio
  oficial + anillo diagnóstico de 200 m usando **solo los puntos ya almacenados**
  (marcados como diagnóstico, no incorporados al universo).
- Por núcleo candidato: distancia mínima al borde del contenedor; marcar
  "posiblemente cortado" si < 100 m.
- Comparar particiones entre contenedores (ARI sobre los puntos comunes). Si los
  núcleos cambian sustancialmente entre (i) y (iii), H1 queda confirmada y el
  contenedor pasa a decisión editorial (DH-04).
- Places no se consulta en ningún caso; si (iv) sugiere estructura fuera del barrio,
  eso alimenta el plan de consultas futuras, no esta corrida.

### 3.7 Ablación de fuentes (H3)

- Detección sobre: universo completo; F01/F02 solo; Places solo (diagnóstico).
- Por núcleo candidato final: ¿sobrevive (Jaccard ≥ 0,5) sin Places? Etiquetar cada
  núcleo como `respaldo_publico` (sobrevive con F01/F02), `mixto` (solo con universo
  completo) o `places_dependiente` (solo aparece con Places). Los `places_dependientes`
  no pueden promoverse a estructura firme (guardrail del proyecto).

## 4. Resultado esperado y criterios de éxito

El entregable **no** es una macroárea ni tiles: es un conjunto pequeño de núcleos
estables, cada uno con categoría de estabilidad:

- **ALTA:** supervivencia ≥ 0,8 en ≥ 2 tamaños de bloque, persistente en el grafo,
  respaldado por KDE, y no `places_dependiente`.
- **MEDIA:** supervivencia 0,6–0,8 o falla exactamente uno de los otros criterios.
- **BAJA:** el resto (se reportan pero no se dibujan como polígono).

Criterios de éxito de la repetición (definidos antes de correr):

1. Diagnóstico de H1–H4 con evidencia explícita (qué hipótesis explica el 0,39).
2. Al menos un conjunto de núcleos con ≥ 3 miembros de categoría ALTA **o** la
   conclusión fundada de que Belgrano se comunica como densidad continua sin núcleos
   firmes (H4). Ambos resultados son éxito; lo que sería fracaso es otro conjunto de
   polígonos sin estabilidad por núcleo.
3. ARI global por bloques del método elegido ≥ 0,55 en al menos un tamaño de bloque, con
   p10 > 0,25 — o declaración explícita de que no se alcanza.
4. Concordancia entre familias (mejor grafo vs. mejor HDBSCAN) ARI ≥ 0,4; si no se
   alcanza, ningún método se declara ganador y se reporta la discrepancia.
5. Cero nombres en todas las salidas; la correspondencia con Barrio Chino,
   Cabildo/Juramento, Bajo Belgrano y Libertador/Barrancas se evalúa **solo post hoc**
   (BEL-R14) como test de emergencia: se dibujan las 4 áreas hipotéticas *después* de
   congelados los núcleos, se mide Jaccard/centroide, y el resultado va a DH-05. Las
   hipótesis nunca entran al algoritmo.

## 5. Qué NO hace esta repetición

- No consulta Google Places ni ninguna API; no descarga fuentes.
- No modifica el universo experimental ni los prototipos v1.
- No asigna nombres ni jerarquías (DH-05).
- No decide el contenedor definitivo (aporta evidencia a DH-04).
- No corre hasta que Diego apruebe el protocolo (DH-04).
