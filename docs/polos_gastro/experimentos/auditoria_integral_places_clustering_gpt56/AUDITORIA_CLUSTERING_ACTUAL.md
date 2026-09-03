# Auditoría del clustering actual

## Veredicto

HDBSCAN es una mejora real frente al DBSCAN global, pero la salida vigente no es “HDBSCAN puro”. Es un encadenamiento HDBSCAN -> KMeans -> concave hull -> agrupación editorial manual. La mayor parte de la fragmentación visible se introduce después de HDBSCAN.

## DBSCAN

**Hecho verificado.** Los antecedentes probaron grillas `eps=150-500 m` sobre la semilla y luego DBSCAN de continuidad `650 m / min_samples=4`, además de DBSCAN local `150 m / 4`.

**Diagnóstico.** Un `eps` global no puede representar simultáneamente Palermo, Corrientes, Costanera y Caseros. Con `eps` bajo fragmenta y eleva ruido; con `eps` alto crea puentes. Sirve como control de continuidad, no como detector principal.

## HDBSCAN

Parámetros vigentes en completa v1:

- `min_cluster_size = max(8, round(3 % de n))`;
- `min_samples = 5`;
- `cluster_selection_epsilon = 50 m`;
- selección `eom`;
- CRS métrico POSGAR 2007 / Faja 5.

**Mejora verificada.** Maneja densidades variables sin fijar un radio único y produce ruido explícito. La comparación local muestra estabilidad alta en Corrientes, Caballito, Puerto Madero, Costanera y Caseros bajo perturbaciones pequeñas; estabilidad media en Microcentro, Palermo Hollywood, Recoleta y San Telmo; baja en Belgrano, Chacarita, Palermo Soho y Villa Crespo.

**Problema.** La selección jerárquica importa mucho. `leaf` cambia drásticamente Caballito, Microcentro, Belgrano y Villa Crespo. Elevar epsilon a 100 m cambia con fuerza Corrientes, Belgrano, Palermo Hollywood, Palermo Soho, Recoleta, San Telmo y Villa Crespo.

**Compatibilidad.** El entorno auditado usa scikit-learn 1.8.0, no 1.9. `cluster_selection_epsilon=50` funciona. El código conserva un fallback a epsilon 0 ante `TypeError`; Palermo Soho quedó efectivamente registrado con epsilon 0. La causa original no quedó en el QA. Esto es deuda de trazabilidad, no prueba actual de un bug de 1.9.

## Segunda pasada jerárquica

El prototipo paralelo la aplicó a seis clusters sobredimensionados. Es útil en núcleos compactos porque permite que subdensidades emerjan sin imponer `k`. Es inadecuada como única respuesta para corredores: puede cortar un eje continuo o devolver ruido en los tramos menos densos.

La completa v1 no reutiliza esa segunda pasada. En su lugar aplica KMeans a los clusters grandes.

## KMeans

**Hecho verificado.** 91 de 163 polígonos (55,8 %) y 3.045 de 5.343 puntos asignados (57,0 %) dependen de KMeans. Toda la salida de Corrientes (23 polígonos) y Caballito (33) depende de KMeans; también 14 de 17 en Belgrano, 12 de 14 en Villa Crespo, 6 de 11 en Microcentro y 3 de 13 en Recoleta.

KMeans resuelve un gate técnico de superficie: parte un cluster cuando supera 18 ha o 1.000 m de diámetro no corredor, buscando piezas de 10 ha. No detecta territorios. Minimiza distancia a centroides y por eso crea celdas convexas similares a tiles, sin considerar calles, barreras o continuidad del eje.

**Recomendación.** Eliminar KMeans como generador de unidades territoriales. Puede conservarse como diagnóstico interno de carga o como inicialización auxiliar, nunca como justificación de límites.

## Poligonización

Todos los 163 polígonos usan `concave_hull(ratio=0.4) + buffer 35 m` y recorte por macrozona. El método es razonable para núcleos compactos. No lo es para corredores, frentes costeros ni redes multinucleares. El recorte por macrozona impide expansión fuera del contenedor y puede crear bordes artificiales.

## Simplificación editorial

La simplificación mejora legibilidad, pero es manual. v2 mapea 163 microzonas a 55 grupos y excluye 14; v3 retiene 41; v4 los fusiona en 31 unidades mediante una lista codificada; v4.1 recorta visualmente solapes; v4.2 cambia diseño. Esta cadena es reproducible, no independiente de juicio humano.

