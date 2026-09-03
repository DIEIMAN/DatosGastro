# Resumen de estabilidad del clustering

## Alcance

Se recalculó HDBSCAN por macrozona sobre los 6.461 puntos, variando `min_cluster_size` ±20 %, `min_samples` 3/5/8, epsilon 0/50/100 y selección `eom/leaf`. También se realizaron cinco remuestreos del 90 % por zona y corridas sin Places, sólo F01 y sólo F02 cuando el enlace lo permitió.

Las métricas completas están en `metricas_robustez_por_zona.csv` y `sensibilidad_hdbscan_detalle.csv`.

## Resultados

| Estabilidad | Zonas | Lectura |
| --- | --- | --- |
| Alta bajo perturbaciones locales | Corrientes, Caballito, Puerto Madero, Costanera Norte, Caseros/Barracas | El patrón HDBSCAN local se repite; no valida la representación poligonal ni la fuente. |
| Media | Microcentro, Palermo Hollywood, Recoleta, San Telmo | Existe señal, pero selección/epsilon o remuestreo cambian piezas. |
| Baja | Belgrano, Chacarita, Palermo Soho, Villa Crespo | La partición depende demasiado de parámetros o de la muestra. |

## Places y fuentes

- Quitar Places cambia estructuralmente 10 de 13 macrozonas; Recoleta agrega principalmente volumen, mientras Palermo Soho cambia de manera moderada.
- Costanera no produce clusters con F01/F02 solamente; 93,1 % del universo es Places.
- En Caballito, el HDBSCAN base es estable pero pasa de 2 clusters crudos a 33 polígonos por KMeans. La estabilidad del detector no justifica la teselación final.
- En Corrientes, 5 clusters crudos se convierten en 23 polígonos. Su forma institucional adecuada es corredor/eje, no 23 áreas.

## Métricas y límites

- Ruido HDBSCAN completo: de 0 % en Caballito a 34,1 % en San Telmo.
- La probabilidad media HDBSCAN es menor en San Telmo (0,55), Chacarita (0,60) y Palermo Soho (0,65).
- Silhouette se calculó sólo sin ruido y no se usa para decidir: favorece formas convexas y puede penalizar corredores o clusters de densidad.
- DBCV no está expuesto por la implementación de HDBSCAN de scikit-learn usada. No se instaló otra librería sólo para obtenerlo; la estabilidad por perturbación y remuestreo aporta evidencia más directa para este caso.
- El bootstrap es de puntos, no un bootstrap espacial por bloques. Puede sobreestimar estabilidad cuando hay autocorrelación espacial.

## Recomendación

Usar estabilidad como gate de evidencia, no como criterio único. Una zona sólo debería pasar a mapa principal si combina: estabilidad al menos media, dependencia Places controlada o corroborada, representación compatible con su tipo territorial y decisión humana documentada.

