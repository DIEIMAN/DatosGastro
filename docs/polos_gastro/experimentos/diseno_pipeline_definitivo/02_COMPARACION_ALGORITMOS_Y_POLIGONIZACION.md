# Comparación metodológica — Algoritmos de clustering y poligonización para microzonas

**Fecha:** 2026-07-08 · **Carácter:** análisis metodológico experimental; nada se implementa
ni se corre en esta entrega. Complementa `01_PIPELINE_MICROZONAS_PROPUESTO.md`.

El problema a resolver: dado un conjunto de puntos (locales del universo consolidado) **dentro
de una macrozona**, detectar los núcleos de concentración y dibujar un polígono ajustado por
núcleo. Escala esperada del insumo por macrozona con universo completo: entre ~50 y ~800
puntos (hoy, con 106 puntos en toda la Ciudad, ningún método rinde — límite ya demostrado en
Tandas 1 y 2, no se repite el experimento).

## 1. Qué aprendimos ya (no re-derivar)

- DBSCAN funciona como prueba de concepto pero con `eps` global sufre: ruido 29–57 %, zonas
  sin cluster, sensibilidad fuerte al parámetro (Tanda 2).
- El hull convexo sobreestima corredores y grupos dispersos (Chacarita 1.546 ha).
- La poligonización asistida por subzona fue la mejor referencia porque **hereda semántica
  editorial** — intuición que el nuevo pipeline institucionaliza al clusterizar por macrozona.
- El cuello de botella es el dato, no el algoritmo.

## 2. Algoritmos de detección de núcleos

### 2.1 Tabla comparativa

| Método | Cómo decide | Fortalezas para este problema | Debilidades | Rol recomendado |
|---|---|---|---|---|
| **DBSCAN** | densidad fija: `eps` + `min_samples` | simple, conocido, ya calibrado en Tandas 1–2 | un solo `eps` por corrida: falla cuando la densidad varía entre y dentro de macrozonas (el caso real); ruido alto | corrida de **continuidad** para comparar con lo hecho; no titular |
| **HDBSCAN** | jerarquía de densidades; extrae clusters estables a múltiples escalas | sin `eps` global — cada núcleo emerge a su densidad natural; outliers explícitos con score; parámetro principal (`min_cluster_size`) es interpretable ("mínimo de locales que forman un núcleo"); disponible en scikit-learn (ya instalado en `.venv` con autorización) | menos intuitivo de explicar; con muy pocos puntos (<30 por macrozona) fragmenta o no encuentra nada; `cluster_selection_method` (eom/leaf) cambia resultados y hay que fijarlo | **detector principal** intra-macrozona |
| **OPTICS** | ordenamiento por alcanzabilidad; DBSCAN a todos los `eps` a la vez | diagnóstico fino de estructura de densidad | para extraer clusters termina requiriendo un corte (ξ o eps) tan sensible como DBSCAN; HDBSCAN cubre el mismo caso mejor y más simple | **descartado** (superado por HDBSCAN); a lo sumo gráfico de alcanzabilidad como diagnóstico puntual |
| **KDE** (densidad kernel) | superficie continua de densidad; núcleos = zonas sobre umbral | salida visual excelente (mapa de calor); permite umbral **relativo a la macrozona** (p. ej. ≥ 40 % del máximo local), inmune al sesgo entre comunas; sus curvas de nivel ya son polígonos | no asigna puntos a clusters (hay que cruzarlo); depende del ancho de banda (bandwidth) tanto como DBSCAN de `eps`; suaviza de más en corredores angostos | **superficie de control**: validar núcleos HDBSCAN, detectar núcleos que HDBSCAN parte en dos, y comunicar visualmente |
| **Mean-shift** | ascenso al máximo local de densidad | encuentra modos sin fijar k | bandwidth global (mismo problema que eps); costoso; poco usado en geoanálisis institucional | descartado |
| **K-means / GMM** | particionan en k grupos compactos | — | exigen k a priori y asignan **todo** punto a un cluster (no existe "no-núcleo"); geometría esférica artificial | descartados |
| **Grilla + hot-spot (hex/H3, Getis-Ord Gi\*)** | agrega a celdas y testea significancia de concentración | estadísticamente defendible ("concentración significativa al 95 %"); estable; fácil de explicar | resolución atada al tamaño de celda; polígonos con borde de celda (estética de panal); pierde forma fina de corredores | **alternativa robusta** si HDBSCAN resulta difícil de defender; también sirve como tercera validación |
| **ST-DBSCAN / clustering espacio-temporal** | densidad en espacio + tiempo | permitiría "núcleos en crecimiento/decadencia" usando fechas de habilitación | exige historia limpia por entidad (hoy no la tenemos); complejidad prematura | roadmap, no v1 |

### 2.2 Combinación recomendada

**HDBSCAN (detector) + KDE (control y comunicación) + reglas de QA (doc 01 §6).**

Justificación en tres puntos:

1. **La densidad real varía** entre macrozonas (Palermo vs. Caballito) y dentro de ellas
   (núcleo vs. periferia). Es exactamente el escenario donde DBSCAN con `eps` único falla y
   HDBSCAN fue diseñado para funcionar. Además, al correr **por macrozona**, cada corrida
   opera sobre una densidad de fondo más homogénea, que es donde todos los métodos mejoran.
2. **Los outliers importan**: en Tanda 2, los puntos "apartados" resultaron ser errores de
   sede. HDBSCAN da score de outlier por punto → alimenta directamente la cola de revisión
   de calidad del universo (círculo virtuoso datos ↔ clustering).
3. **KDE desacopla detección de comunicación**: el detector puede ser técnico; el mapa de
   calor con curvas de nivel es lo que jefatura entiende. Si ambos señalan el mismo núcleo,
   la microzona es defendible; si no coinciden, bandera de revisión.

Parámetros iniciales propuestos (a calibrar en piloto, doc 01 §8 Fase C):

- HDBSCAN: `min_cluster_size = max(8, 3 % de los puntos de la macrozona)`, `min_samples = 5`,
  `cluster_selection_epsilon = 50 m` (evita fragmentar núcleos separados por una calle),
  `cluster_selection_method = "eom"`; coordenadas siempre en CRS métrico.
- KDE: kernel gaussiano, bandwidth 80–120 m (≈ una cuadra porteña de ~110 m), grilla de
  20 m; umbral de núcleo relativo por macrozona (p. ej. ≥ 40 % del máximo local), nunca un
  umbral absoluto citywide.
- DBSCAN de continuidad: candidata inclusiva 650/4 de Tanda 2, solo para tabla comparativa.

## 3. Métodos de poligonización

Dado el conjunto de puntos de un núcleo, construir su polígono:

| Método | Ventajas | Desventajas | Cuándo usarlo |
|---|---|---|---|
| **Convex hull** | trivial, sin parámetros, robusto | sobreestima siempre que la forma no es convexa; ya demostró inflar corredores (Tanda 2) | solo como referencia interna / control de QA (ratio área concave/convex mide cuán "cóncava" es la forma) |
| **Concave hull** (shapely ≥ 2.0, `concave_hull(ratio)`) | se ajusta a la forma real; un parámetro (`ratio`) interpretable; sin dependencias nuevas | con pocos puntos o ratio agresivo genera púas y auto-estrangulamientos; requiere suavizado posterior | **método por defecto** para núcleos compactos con n ≥ ~10 |
| **Alpha shape** (paquete `alphashape`) | control fino vía α; puede producir huecos y multipartes legítimos | α es poco intuitivo y sensible; dependencia nueva; multipartes complican la comunicación | equivalente funcional al concave hull; solo si el `concave_hull` de shapely queda corto |
| **Curvas de nivel de KDE** | polígono suave, estética institucional, coherente con el mapa de calor | depende del bandwidth; puede unir núcleos vecinos o recortar locales de borde reales | capa de **comunicación**; y validador: el polígono final debería quedar dentro del contorno KDE de baja exigencia |
| **Buffer-unión (cierre morfológico)**: buffer(+r) de cada punto → unión → buffer(−r′) | muy robusto con pocos puntos; nunca se estrangula; r interpretable ("radio de influencia de un local", ~60–80 m) | bordes redondeados "de burbuja"; con r grande une lo que no debe | núcleos chicos (5 ≤ n < 10) donde el hull es inestable |
| **Buffer sobre eje vial** (cápsula sobre la calle) | representa corredores como lo que son: una calle con frentes gastronómicos; superficie mínima y honesta | requiere base de ejes viales GCBA (pendiente ya identificado para mapas V3) y lógica de detección de corredor | **corredores** (Corrientes, Caseros; elongación PCA > 3 y largo > 600 m) |
| **Voronoi (celdas de los locales, recortadas)** | partición exhaustiva sin huecos ni solapes; útil para separar núcleos contiguos y asignar "área de influencia" | las celdas no representan la huella del núcleo (se extienden hasta el vecino, no hasta donde termina la concentración) | **no** para la huella; sí como herramienta auxiliar para (a) trazar la frontera entre dos microzonas pegadas y (b) recortar hulls que invaden zonas vacías |

### Recomendación híbrida (regla de decisión por núcleo)

```
n < 5            → sin polígono: marcador puntual ("núcleo insuficiente")
5 ≤ n < 10       → buffer-unión (cierre morfológico, r ≈ 70 m)
n ≥ 10 compacto  → concave_hull(ratio a calibrar ≈ 0.3–0.5) + buffer 30–40 m
                   + suavizado + recorte (macrozona, CABA, contorno KDE laxo)
corredor         → cápsula sobre eje (principal por PCA hasta tener ejes viales GCBA;
 (elong.>3,        luego eje vial real) con semiancho 50–70 m
  largo>600 m)
núcleos pegados  → frontera por Voronoi entre los dos conjuntos de puntos
```

El buffer final de 30–40 m no es cosmético: los puntos son puertas de local; el polígono debe
cubrir el frente edificado, no pasar por el medio de la calzada.

## 4. Criterios de evaluación para el piloto

Para elegir configuración ganadora en la Fase C (piloto en 3 macrozonas) sin discusiones
circulares, fijar de antemano las métricas de comparación:

1. **Cobertura útil:** % de puntos del universo de la macrozona dentro de alguna microzona
   (ni 100 % — sería sobreajuste — ni < 40 %).
2. **Compacidad:** superficie mediana por microzona y ratio área/convex-hull.
3. **Estabilidad:** Jaccard de área bajo perturbación de parámetros (±25 %) y bajo submuestreo
   de puntos (bootstrap 80 %).
4. **Concordancia entre métodos:** solapamiento HDBSCAN vs. núcleos KDE.
5. **Juicio experto:** en el piloto, la validación editorial es la métrica final — el caso de
   prueba canónico: en Palermo Hollywood debe emerger Fitz Roy–Honduras–Gorriti, no todo el
   barrio.

## 5. Dependencias técnicas

Ya disponibles en `.venv`: `scikit-learn` (incluye `HDBSCAN` y `KernelDensity` desde la
1.3), `shapely ≥ 2.0` vía geopandas (`concave_hull`, `voronoi_diagram`, buffers), `geopandas`,
`matplotlib`. Única dependencia nueva potencial: `alphashape` (solo si el concave hull nativo
resulta insuficiente — verificar en piloto antes de instalar). La base de ejes viales GCBA es
un insumo de datos, no de software, y ya está identificada como pendiente en el plan de mapas
V3.
