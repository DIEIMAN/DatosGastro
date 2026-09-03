# Fe de erratas de la auditoría GPT56

Estado: EXPERIMENTAL / no oficial. No modifica la auditoría original.

## Correcciones

1. `clusters_sin_places` y `clusters_con_places` mezclaban la composición de polígonos posteriores a KMeans con clusters HDBSCAN. Se reemplazan por `diagnostico_places_por_zona_corregido.csv`, que separa HDBSCAN completo, HDBSCAN F01/F02 y polígonos post-KMeans.
2. `estabilidad_sintetica` resumía estabilidad local, bootstrap y sensibilidad global. Se reemplaza por `metricas_estabilidad_desagregadas_v1.csv`. Caballito queda explícitamente como estabilidad local alta y sensibilidad global alta.
3. `muestra_casos_deduplicacion_revision.csv` contiene candidatos clasificados automáticamente; no es verdad manual etiquetada y no permite calcular precisión ni recall.
4. El entorno `.venv` usa scikit-learn 1.9.0. Se reprodujo un `TypeError` con HDBSCAN y epsilon positivo. Cada fallback a epsilon 0 queda registrado en las tablas nuevas.

## Efecto sobre el veredicto

Las correcciones no invalidan `PIPELINE_HIBRIDO_POR_TIPO_TERRITORIAL`. Lo refuerzan: muestran que no debe confundirse estabilidad del detector con validez de polígonos y que KMeans no debe definir unidades.
