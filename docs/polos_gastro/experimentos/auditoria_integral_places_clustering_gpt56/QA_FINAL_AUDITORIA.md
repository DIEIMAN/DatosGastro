# QA final de auditoría

Fecha: 10 de julio de 2026. Estado: APTO PARA REVISIÓN INTERNA, no oficial.

## Rutas inspeccionadas

- `data/processed/`: F01, F02 y dimensión de ubicación, sólo lectura.
- `scripts/polos_gastro/experimentos/pipeline_microzonas_v1/`.
- `outputs/polos_gastro/experimentos/pipeline_microzonas_v1/`.
- `docs/polos_gastro/experimentos/pipeline_microzonas_v1/`.
- `scripts|outputs|docs/polos_gastro/experimentos/google_places_microzonas_piloto/`.
- `scripts|outputs|docs/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/`, incluidas completa v1, v2, v3, v4, v4.1, v4.2 y comparación Fase 26.
- `scripts/polos_gastro/build_fase25_microajustes_finales_oficina.py`.
- `outputs|docs/polos_gastro/fase25_microajustes_finales_oficina/`.

## Scripts y pruebas ejecutadas

- Compilación Python de `ejecutar_auditoria_integral.py` y `armar_paquete_revision.py`: OK.
- Auditoría integral y corrida final con comparación de hashes: OK.
- Pruebas HDBSCAN de sensibilidad, remuestreo, fuente y selección: OK.
- Prueba controlada OPTICS en cinco macrozonas: ejecutada; no mejora general.
- Consistencia CSV/GeoJSON, asignación única y trazabilidad 163/55/41/31: OK.
- Inspección visual de completa v1, QA v4.2 y mapas Fase 25: realizada.
- Integridad ZIP con `ZipFile.testzip()`: OK.
- Escaneo de privacidad de 26 archivos: 0 hallazgos.
- Revisión de columnas CSV prohibidas: 0 hallazgos.

## Números verificados

- Semilla geolocalizada: 106 referencias.
- Universo F01/F02: 9.739 entidades; 9.738 aptas.
- Consultas piloto: 379.
- Nuevos piloto bajo QA piloto: 1.651.
- Places nuevos acumulados: 3.221.
- Universo completo: 6.461 IDs únicos.
- Puntos asignados: 5.343; ruido: 1.118; asignaciones múltiples: 0.
- Polígonos técnicos: 163.
- v2: 55 grupos totales, 41 retenidos y 14 excluidos.
- v3: 41 grupos.
- v4/v4.1/v4.2: 31 unidades; principal 13, fuertes 6, con observaciones 7, revisión 14, anexo 4.
- KMeans: 91/163 polígonos y 3.045/5.343 puntos asignados.
- Topología v4: 16 pares solapados, 144,0009 ha acumuladas.

## Discrepancias encontradas

- El origen piloto aporta 1.651 nuevos en el QA piloto y 1.684 al reprocesarse en la integración completa: diferencia 33 por contención/reglas de corrida.
- La abreviatura `163 -> 41 -> 31` omite 55 grupos v2: 41 pasan y 14 se excluyen.
- `min_cluster_size` usa `ceil` en el prototipo y `round` en completa v1.
- Palermo Soho quedó con epsilon 0 en el QA vigente; el código no conserva el error que activó el fallback.
- v4.1 corrige solapes en la capa de dibujo, no en asignaciones ni conteos.

## Números no verificables con los insumos disponibles

- Recall absoluto de Places.
- Cantidad real de establecimientos operando hoy.
- Precisión/recall de deduplicación sin muestra etiquetada.
- Validez institucional de nombres y límites.
- Efecto de barreras urbanas sin prueba sobre red vial enrutable.

## Librerías

No se instaló ninguna librería. Entorno observado: pandas 2.3.3, numpy 1.26.4, scikit-learn 1.8.0, geopandas 1.1.3, shapely 2.1.2 y scipy 1.16.3.

## Privacidad y paquete

- Carpeta: `outputs/polos_gastro/experimentos/auditoria_integral_places_clustering_gpt56/REVISION_AUDITORIA_GPT56/`.
- ZIP: `outputs/polos_gastro/experimentos/auditoria_integral_places_clustering_gpt56/REVISION_AUDITORIA_GPT56.zip`.
- Archivos: 26.
- Tamaño sin comprimir: 258.811 bytes.
- ZIP: 168.904 bytes.
- SHA-256 ZIP: `56290281b0b5e134938bca2a526388dd602ed58d72c38bd9c0d0fd8cbe95dfbb`.
- Sin datos fuente, carpetas internas, credenciales, identificadores privados, JSON crudo ni datos personales.

## Seguridad y Git

- 48/48 insumos críticos conservaron exactamente tamaño y SHA-256.
- Sin API y sin llamadas a Google Places.
- Sin descarga de fuentes.
- Sin modificación de datos fuente, Fase 25, Fase 26, v1, v2, v3, v4, v4.1 o v4.2.
- Sin staging, `git add`, commit, push ni modificación de HEAD (`e6d79a970caae550e4942aeda096f18651f9dcae`).
- El worktree ya contenía cambios y archivos ajenos; se preservaron sin intervención.

