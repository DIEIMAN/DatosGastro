# Auditoría de consistencia de repeticiones v2

Estado: **EXPERIMENTAL / NO OFICIAL**. Auditoría directa de GeoJSON, CSV, diagnósticos, metadata, mapas, manifests y matrices v2.

## Veredicto

La v2 es internamente consistente salvo una omisión explícita en el resumen de Costanera Norte: el universo contiene 72 registros, pero los cuatro componentes HDBSCAN suman 71. El registro restante fue localizado y clasificado; no se corrigió ningún insumo v2.

| control | valor | esperado | estado |
|---|---|---|---|
| Costanera universo | 72 | 72 | OK |
| Costanera suma componentes | 71 | 71 | INCONSISTENCIA_LOCALIZADA |
| Costanera no asignados | 1 | 1 | LOCALIZADO |
| Belgrano candidatos | 17 | 17 | OK |
| Belgrano ALTA/MEDIA/BAJA | 6/8/3 | 6/8/3 | OK |
| Belgrano shortlist preliminar | BEL_RV2_N02;BEL_RV2_N03;BEL_RV2_N05;BEL_RV2_N06 | N02/N03/N05/N06 | OK_REQUIERE_REGLA_EXPLICITA |
| San Telmo núcleo | 177/320 (55.31%) | 177/320 (55.31%) | OK |
| San Telmo núcleo+Defensa | 208/320 (65.00%) | 208/320 (65.00%) | OK |
| Corrientes | 503/1255; 2901.6 m | 503/1255; 2901.6 m | OK |
| Puerto Madero PM-C | 235/294; 80 componentes | 235/294; 80 | OK |
| Reproducibilidad reportada | 71/71 | 71/71 | REPORTADA_NO_REEJECUTADA_COMO_TEST_SEPARADO |

## Costanera: causa exacta

El registro faltante quedó etiquetado como ruido (`-1`) por HDBSCAN. Es una señal Places, está a **146.0 m** de `CN_C01` y a **9.5 m** del borde. Se clasifica como **dependencia del contenedor**. No hubo pérdida en unión, filtro ni exportación: la tabla v2 solo resumió clusters asignados y no explicitó el ruido.

## Otros controles

- Belgrano conserva 17 candidatos y la distribución 6 ALTA, 8 MEDIA y 3 BAJA. La shortlist preliminar N02/N03/N05/N06 coincide con la evidencia tabular, pero se vuelve a derivar con regla explícita en v2.1.
- San Telmo reproduce 177/320 para el núcleo y 208/320 para núcleo + Defensa.
- Corrientes reproduce 503/1.255 y 2.901,6 m; los cuatro subtramos son exclusivamente narrativos.
- Puerto Madero PM-C reproduce 235/294, 79,93%, 180 m, 21,46% del contenedor y 80 componentes analíticos.
- Las tablas de puntos externos usan la taxonomía aprobada. No se promueve ningún punto automáticamente.
- La metadata v2 reporta reproducibilidad 71/71 para sus pruebas. Esta auditoría verifica outputs persistidos y relaciones críticas; no sobrescribe ni recompone v2.
