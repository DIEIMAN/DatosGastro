# Plan recomendado post auditoría

## Imprescindibles antes del informe

| Acción | Esfuerzo | Resultado esperado |
| --- | --- | --- |
| Decidir tipo territorial y representación de las 13 zonas | medio | Polígono, corredor, núcleos o señal definidos explícitamente. |
| Eliminar KMeans como justificación territorial en Corrientes, Caballito, Belgrano, Villa Crespo, Microcentro y Recoleta | medio | Evitar 91 tiles artificiales. |
| Resolver los 16 solapes y documentar si existe jerarquía o reasignación | medio | Coherencia entre geometría, puntos y conteos. |
| Etiquetar muestra de deduplicación y estimar precisión/recall | medio | Umbrales defendibles o decisión de no cambiarlos. |
| Confirmar las 14 exclusiones v2 y los 31 nombres/unidades v4 | medio | Decisiones humanas auditables. |
| Marcar como no aptas para mapa principal las zonas con >60 % Places sin corroboración | bajo | Evitar sobrerrepresentación de fuente privada. |
| Explicar la diferencia 1.651 vs. 1.684 del origen piloto | bajo | Trazabilidad cuantitativa sin aparente contradicción. |

## Recomendables

| Acción | Esfuerzo | Resultado esperado |
| --- | --- | --- |
| Probar HDBSCAN sin KMeans + KDE en Palermo Soho y San Telmo | medio | Núcleos compactos más defendibles. |
| Probar grafo de proximidad/comunidades en Belgrano, Villa Crespo, Chacarita y Microcentro | medio | Redes multinucleares sin forzar `k`. |
| Construir ejes/buffers con callejero local para Corrientes, Puerto Madero y Caseros | medio | Corredores reproducibles y legibles. |
| Ejecutar bootstrap espacial por bloques, no sólo de puntos | medio | Estabilidad menos optimista. |
| Auditar bordes con buffers internos/externos de macrozonas | medio | Medir dependencia del contenedor. |
| Revisar las 58 celdas saturadas de Tanda B con datos ya almacenados y documentar subcaptura | bajo | Límite visible; sin nuevas llamadas. |

## Opcionales

| Acción | Esfuerzo | Resultado esperado |
| --- | --- | --- |
| OPTICS/reachability en dos casos ambiguos | bajo | Diagnóstico de escalas, no reemplazo. |
| Alpha shapes en un núcleo donde concave hull falle | bajo | Comparación puntual. |
| Hotspots en grilla/hexágonos como tercera validación | medio | Evidencia agregada estable. |

## Futuras

| Acción | Esfuerzo | Condición |
| --- | --- | --- |
| Distancia de red y barreras urbanas | alto | Red vial local limpia y enrutable. |
| Clustering espacio-temporal | alto | Historia comparable de aperturas/cierres o evidencia temporal. |
| Descubrimiento fuera de macrozonas | alto | Diseño de cobertura CABA completa y nueva autorización de datos. |

## No recomendadas

- Afinar KMeans para que los tiles “se vean mejor”.
- Elegir parámetros por cantidad deseada de polígonos.
- Usar Silhouette como criterio rector.
- Mostrar Costanera, Puerto Madero, Caballito, Chacarita, Villa Crespo o Caseros como unidades firmes sólo por su estabilidad geométrica.
- Volver a llamar Places antes de resolver método, saturación y decisiones editoriales.
- Convertir v4.1/v4.2 en delimitación institucional sin reasignación coherente de puntos.

