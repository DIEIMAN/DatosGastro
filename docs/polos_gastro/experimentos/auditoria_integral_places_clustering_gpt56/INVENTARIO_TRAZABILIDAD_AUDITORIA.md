# Inventario y trazabilidad de la auditoría

Estado: experimental, no oficial. Fecha de corte: 10 de julio de 2026.

## Cadena verificada

`F01/F02 -> resolución de entidades -> universo de 9.739 entidades -> contención en macrozonas -> Places almacenado -> deduplicación -> universo sanitizado de 6.461 puntos -> HDBSCAN -> KMeans en clusters grandes -> 163 polígonos -> 55 grupos v2 (41 retenidos + 14 excluidos) -> 41 grupos v3 -> 31 unidades v4/v4.1 -> diseño v4.2`

La cadena es completa a nivel de IDs. La formulación abreviada `163 -> 41 -> 31` omite que v2 crea 55 grupos y excluye 14 antes de v3. La evidencia fila a fila está en `trazabilidad_163_41_31.csv` y `qa_trazabilidad_163_41_31.json`.

## Inventario principal

| Archivo | Ruta | Función / input -> output | Etapa | Tipo | Vigente | Estado e inconsistencia |
| --- | --- | --- | --- | --- | --- | --- |
| `fact_establecimiento.csv` | `data/processed/` | F01 procesada -> entidades | universo | fuente derivada pública | sí | Solo lectura; no mide actividad vigente. |
| `fact_habilitacion_gastronomica.csv` | `data/processed/` | F02 procesada -> entidades | universo | fuente derivada pública | sí | 44.169 filas históricas; fuerte repetición administrativa. |
| `dim_ubicacion.csv` | `data/processed/` | ubicación/lat-lon -> joins F01/F02 | universo | derivado | sí | Una ubicación F02 puede contener más de un establecimiento real. |
| `locales_para_mapa_revision.csv` | `outputs/polos_gastro/fase13_mapas/tablas/` | 106 referencias -> contenedores iniciales | antecedente | semilla editorial | indirecto | Semilla curada; no es universo estadístico. |
| `config.py` | `scripts/polos_gastro/experimentos/pipeline_microzonas_v1/` | parámetros documentados | prototipo | código | sí, como antecedente | Usa `ceil(3%)`; la ampliación usa `round(3%)`. |
| `s01_construir_universo.py` | misma carpeta | F01/F02 -> 9.739 entidades | universo | código | sí | Dedup F01/F02 reproducible, pero no validada con muestra etiquetada. |
| `universo_entidades_v1.csv` | `outputs/.../pipeline_microzonas_v1/universo/` | universo F01/F02 | universo | derivado | sí | 9.739 entidades; 9.738 aptas para clustering. |
| `correspondencia_filas_fuente.csv` | misma carpeta | 37.368 filas -> entidad | trazabilidad | QA | sí | Conserva separación F01/F02. |
| `s03_clustering_macrozonas.py` | `scripts/.../pipeline_microzonas_v1/` | universo -> HDBSCAN/DBSCAN/KDE | clustering inicial | código | antecedente | Comparación útil; no es el generador de completa v1. |
| `labels_clusters.csv` | `outputs/.../pipeline_microzonas_v1/clustering/` | tres etiquetas por entidad | clustering inicial | derivado | antecedente | 4.615 entidades contenidas; resto queda fuera, no eliminado del universo general. |
| `s07_segunda_pasada.py` | `scripts/.../pipeline_microzonas_v1/` | 6 clusters grandes -> subclusters | segunda pasada | experimento | no en completa v1 | Demuestra utilidad parcial; no alimenta la cadena vigente de Places. |
| `generar_poligonos_clustering.py` | `scripts/polos_gastro/experimentos/` | semilla -> DBSCAN + hull | antecedente DBSCAN | código obsoleto | no | Prueba temprana sobre semilla; no participa del resultado vigente. |
| `generar_poligonos_clustering_v2.py` | misma carpeta | alternativa DBSCAN | antecedente | código paralelo | no | No participa de completa v1. |
| `plan_consultas_places.csv` | `outputs/.../google_places_microzonas_piloto/places/` | 379 celdas | piloto Places | plan | sí como registro | No ejecutar de nuevo sin autorización. |
| `places_sanitizado.csv` | misma carpeta | 3.511 resultados únicos sanitizados | piloto Places | derivado externo | antecedente | No contiene identificadores privados; fuente separada. |
| `qa_universo_piloto.json` | `outputs/.../google_places_microzonas_piloto/` | QA contención/dedup | piloto | QA | sí | Verifica 1.651 incorporaciones bajo geometría piloto. |
| `plan_consultas_a_criticas.csv` | `outputs/.../google_places_microzonas_ampliacion_v1/places/` | 351 celdas de 135 m | ampliación A | plan | sí como registro | 2 celdas saturadas, luego refinadas en Chacarita. |
| `plan_consultas_b_consolidacion.csv` | misma carpeta | 260 celdas de 135 m | ampliación B | plan | sí como registro | 58 celdas saturadas no refinadas en Villa Crespo, Recoleta y Caballito. |
| `plan_refino_chacarita_saturadas_3x3.csv` | `outputs/.../places/refinamientos/` | 18 consultas de 70 m | refino | plan | sí como registro | Refina solo 2 celdas de A; no resuelve las 58 de B. |
| `construir_integracion_completa_v1.py` | `scripts/.../google_places_microzonas_ampliacion_v1/` | F01/F02 + cuatro resultados Places -> 6.461 | integración | código | sí | Contención, identificador interno, 15 m y 40 m. Usa el vecino más cercano únicamente. |
| `qa_integracion_completa_v1.json` | `outputs/.../completa_v1/` | QA de 6.208 resultados brutos | integración | QA | sí | 983 fuera, 146 repetidos entre tandas, 1.858 contra F01/F02, 3.221 nuevos. |
| `UNIVERSO_COMPLETO_SANITIZADO.csv` | misma carpeta | 3.240 F01/F02 + 3.221 Places | universo vigente | derivado sanitizado | sí | IDs únicos; 844 filas participan en coordenadas exactas repetidas. |
| `detectar_microzonas_completa_v1.py` | `scripts/.../google_places_microzonas_ampliacion_v1/` | universo -> HDBSCAN/KMeans/polígonos | clustering vigente | código | sí | Mezcla detección, partición y poligonización; fallback silencioso `epsilon=0` ante `TypeError`. |
| `MICROCLUSTERS_COMPLETA_V1.geojson` | `outputs/.../completa_v1/` | 6.461 puntos con cluster final | clustering | derivado | sí | 5.343 asignados una vez; 1.118 ruido. |
| `POLIGONOS_MICROZONAS_COMPLETA_V1.geojson` | misma carpeta | 163 polígonos | poligonización | derivado | sí como insumo | 91 polígonos y 3.045 puntos dependen de KMeans. |
| `tabla_agrupamiento_editorial_v0.csv` | `outputs/.../cartografia_editorial_v2/` | 163 -> 55 grupos | simplificación v2 | decisión editorial | sí | 41 retenidos y 14 exclusiones; mapeo manual codificado. |
| `preparar_cartografia_editorial_v2.py` | `scripts/.../google_places_microzonas_ampliacion_v1/` | diccionario manual -> geometrías agrupadas | v2 | código/decisión | sí | Decisiones humanas embebidas en código, sin archivo de reglas independiente. |
| `tabla_decision_cartografia_v3.csv` | `outputs/.../cartografia_decision_v3/` | 41 grupos -> familias | v3 | decisión editorial | sí | Ordena decisiones; no redibuja límites. |
| `preparar_cartografia_redibujo_editorial_v4.py` | `scripts/.../google_places_microzonas_ampliacion_v1/` | 41 -> 31 unidades | v4 | código/decisión | sí | Lista manual `UNITS`; completa, pero territorialmente no validada. |
| `poligonos_editoriales_redibujados_v4.geojson` | `outputs/.../cartografia_redibujo_editorial_v4/` | 31 unidades | v4 | derivado | sí | 16 pares solapados; 144,0 ha de solape acumulado. |
| `poligonos_v4_1_decision_dibujo.geojson` | `outputs/.../cartografia_redibujo_editorial_v4_1/` | recorte visual | v4.1 | presentación | sí | 13 geometrías recortadas solo para dibujo; puntos y conteos no se reasignan. |
| `metadata_cartografia_v4_2.json` | `outputs/.../cartografia_design_v4_2/` | v4.1 -> diseño | v4.2 | presentación/QA | sí | Declara explícitamente que no cambia método ni geometría analítica. |
| `build_fase25_microajustes_finales_oficina.py` | `scripts/polos_gastro/` | Fase 24 -> PDF Fase 25 | antecedente | código institucional | comparación | No usa Places; conserva lectura semilla de 22 polos/ejes. |
| `INFORME_POLOS_GASTRO_DGDGAS_11P_OFICINA_FASE25.pdf` | `outputs/.../fase25_microajustes_finales_oficina/` | mapa previo | antecedente | informe | comparación | Más prudente en límites; evidencia cuantitativa mucho menor. |
| `INFORME_FASE26_COMPARATIVA_CARTOGRAFIA.md` | `docs/.../fase26_comparativa_cartografia/` | comparación v1-v4.2 | Fase 26 | documentación | solo lectura | Resume versiones; no sustituye verificación de tablas. |

## Inconsistencias y deuda documental

- El piloto informa 1.651 incorporaciones; la integración completa vuelve a procesar el mismo origen y retiene 1.684. La diferencia de 33 proviene del cambio de contenedores/reglas de la corrida completa y debe explicitarse.
- El prototipo usa `ceil(3 %)` para `min_cluster_size`; completa v1 usa `round(3 %)`.
- Completa v1 registra Palermo Soho con `hdbscan_eps_0`, mientras las demás macrozonas usan 50 m. El código captura sólo `TypeError` y no registra el error original.
- La documentación abrevia v2 como “41 grupos”, pero el archivo de mapeo contiene 55: 41 retenidos y 14 exclusiones.
- La lógica editorial está codificada en diccionarios Python. Es reproducible, pero no independiente de la persona que definió nombres, fusiones y jerarquías.
- v4.1 soluciona solapes para visualización sin alterar asignación de puntos. El mapa y la tabla analítica dejan de representar exactamente la misma geometría.
