# QA técnico v2 — Polígonos exploratorios PolosGastro

**Fecha:** 2026-07-07 · Corrida:
`.venv/Scripts/python.exe scripts/polos_gastro/experimentos/generar_poligonos_clustering_v2.py`

## 1–3. Input y puntos

| Ítem | Valor |
|---|---|
| Input | `outputs/polos_gastro/fase13_mapas/tablas/locales_para_mapa_revision.csv` (mismo que tanda 1) |
| Puntos cargados / válidos | 106 / **93** (descartados: 11 `duplicado_probable`, 2 fuera del polígono de comunas de CABA) |
| Campos usados | `lat`, `lon` (clustering); `polo`, `subzona` (agrupamiento asistido y caracterización); `estado_consolidado` (filtro de duplicados); `nombre_lugar` (trazabilidad de apartados) |
| CRS métrico | EPSG:5347 (POSGAR 2007 / Argentina faja 5) |

Nota de datos: el CSV fuente trae un carácter corrupto literal (U+FFFD) en "Las Ca�itas"
(defecto de origen en Fase 13, **no se modificó el archivo fuente**); se sanea solo para las
etiquetas de los mapas ("Las Cañitas").

## 4–6. DBSCAN v2

- **Grilla probada:** eps ∈ {150, 200, 250, 300, 400, 500, 650, 800, 1000} ×
  min_samples ∈ {2, 3, 4, 5, 6} = 45 combinaciones, con métricas de fragmentación
  (`clusters_muy_chicos`) y fusión (`diametro_max_m`) → `parametros_probados_dbscan_v2.csv`.
- **Candidatas elegidas** (criterio: no solo menor ruido; ms=2 descartado por pares,
  eps ≥ 800 descartado por fusión de zonas distantes):

| Candidata | eps / ms | Clusters | Ruido |
|---|---|---|---|
| Estricta | 500 / 4 | 6 | 53 (57.0 %) |
| Equilibrada (= tanda 1) | 400 / 3 | 12 | 44 (47.3 %) |
| Inclusiva | 650 / 4 | 10 | **27 (29.0 %)** |

## 7–10. Polígonos asistidos por subzona

- **14 grupos** (clave polo + subzona; Palermo se divide en Las Cañitas y Palermo Soho).
- Depuración intra-grupo: **10 puntos apartados excluidos** (umbral máx(1500 m, 3× distancia
  mediana al centro del grupo)): Ichisou, BAO Kitchen y Tori Tori (Belgrano), La Casona del
  Nonno (Caballito), Puerto Cristal (Costanera Norte), Oporto (Palermo), La Parolaccia Casa
  Tua y Le Grill (Puerto Madero), La Pecora Nera (Recoleta), El Preferido de San Telmo
  (San Telmo).
- Confianza: **11 alta** (≥5 pts), **2 media** (Caseros/Barracas 3, Caballito 4),
  **1 baja** (Abasto, 1 pt → buffer puntual 80 m).
- Grupos con pocos puntos: Abasto (1), Caseros/Barracas (3), Caballito (4).
- **3 grupos `extension_a_revisar`** (hull > 400 ha, disperso): Chacarita (1.546 ha),
  Caseros/Barracas (931 ha), Costanera Norte (636 ha). En grupos con diámetro > 2.5 km se usó
  convex hull (el cóncavo generaba púas engañosas). Resto de áreas: 2–282 ha.

## 11. Outputs generados

En `outputs/polos_gastro/experimentos_clustering_v2/`:
`parametros_probados_dbscan_v2.csv`, `mapa_clusters_dbscan_estricto.png`,
`mapa_clusters_dbscan_equilibrado.png`, `mapa_clusters_dbscan_inclusivo.png`,
`poligonos_dbscan_equilibrado.geojson`, `poligonos_asistidos_subzona_experimental.geojson`,
`resumen_poligonos_asistidos_subzona.csv`,
`mapa_poligonos_asistidos_subzona_experimental.png`, `comparativo_dbscan_vs_asistido.png`.

En `docs/polos_gastro/experimentos_clustering_v2/`: diagnóstico de ruido, comparación
DBSCAN vs asistido, recomendación metodológica, este QA y el handoff.
Los outputs de la tanda 1 (`experimentos_clustering/`) **no se tocaron ni pisaron**.

## 12. Revisión visual realizada

Los 5 PNG se renderizaron y se inspeccionaron (tres iteraciones de corrección): se
eliminaron púas de hulls cóncavos en grupos dispersos, se corrigieron etiquetas truncadas y
solapadas (offsets alternados), y en el comparativo los polígonos dispersos pasaron a trazo
tenue para no tapar la lectura. Limitación visual conocida: quedan choques menores de
etiquetas en el centro del mapa asistido/comparativo (zona Corrientes–Recoleta–Abasto);
leer junto con `resumen_poligonos_asistidos_subzona.csv`.

## 13. Limitaciones

Las de la tanda 1 (universo semilla ralo y curado, no censo; comparación editorial solo
visual) más: la depuración de apartados usa un umbral heurístico (puede excluir de más o de
menos); los hulls convexos de corredores sobreestiman área; la confianza mide solo cantidad
de puntos, no calidad de match.

## 14. Lenguaje prudente

Títulos de mapas con "EXPERIMENTAL"; nota visible "Capa auxiliar exploratoria. No constituye
límite oficial. Requiere revisión territorial." en los 5 PNG; atributo `nota` en cada feature
GeoJSON y fila CSV. Grep de términos vedados ("ranking", "mejores locales",
"recomendaciones" como oferta al público, "zonas definitivas", "límite oficial" afirmativo)
sobre docs y outputs v2: sin ocurrencias afirmativas.

## 15–18. Confirmaciones

| # | Confirmación |
|---|---|
| 15 | **Sin API externa:** ninguna consulta a Google Places ni request externo de datos en toda la tanda. |
| 16 | **PDFs y outputs finales intactos:** Fase 25, PDFs, mapas vigentes y capa editorial V4 sin modificar (V4 ni siquiera se dibujó en esta tanda). |
| 17 | **Datos fuente intactos:** todos los inputs en solo lectura, incluido el CSV de Fase 13 con su defecto de encoding original. |
| 18 | **Sin push, sin commit, sin staging:** no se ejecutó `git add`/`commit`/`push`; verificado con `git status --short` (solo carpetas nuevas untracked). |
