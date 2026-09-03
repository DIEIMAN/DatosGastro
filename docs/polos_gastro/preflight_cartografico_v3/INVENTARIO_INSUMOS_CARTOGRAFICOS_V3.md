# Inventario de insumos cartográficos V3

**Estado:** EXPERIMENTAL / NO OFICIAL  
**Fecha de corte:** 2026-07-11  
**Rol:** `cartografo_territorial`  
**Alcance:** preflight técnico, offline y de solo lectura sobre insumos existentes.

## Resultado ejecutivo

El entorno local contiene los insumos necesarios para preparar una futura corrida territorial de Belgrano, Recoleta y Costanera Norte. `HANDOFF_DOCUMENTAL_CARTOGRAFO_V1.md` apareció durante la sesión, fue leído y evaluado como compatible con observaciones. La ejecución queda bloqueada hasta una instrucción posterior explícita.

No se generaron geometrías, clusters ni mapas. No se modificaron v2.1, Fase 25, Fase 26, fuentes, capas analíticas, capas de presentación ni paquetes previos.

La matriz machine-readable complementaria está en `outputs/polos_gastro/preflight_cartografico_v3/MATRIZ_INSUMOS_Y_DEPENDENCIAS.csv`.

## Infraestructura aplicada

- Política base: `docs/infraestructura_agentes_skills_v1_1/POLITICA_OPERATIVA_DATAGASTRO_V1_1.md`.
- Hotfix vigente: `docs/infraestructura_agentes_skills_v1_1_1_hotfix/`; corrige empaquetado y trazabilidad, sin cambiar roles, skills ni superficies.
- Definición del rol: `docs/infraestructura_agentes_skills_v1/agents/cartografo_territorial.md`.
- Adaptador Codex: `docs/infraestructura_agentes_skills_v1_1/adaptadores/codex/cartografo_territorial.md`.
- Skills autorizadas consultadas: `transformar_cartografia_a_presentacion`, `crear_manifest_hashes_metadata` y `auditar_git_y_archivos_protegidos`. `qa_pdf_pagina_por_pagina` no se activó porque los PDF están fuera de alcance.
- Guardrails transversales aplicados: geodatos, privacidad e informes DataGastro.

## Universo de puntos vigente

Fuente de trabajo local: `outputs/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/completa_v1/UNIVERSO_COMPLETO_SANITIZADO.csv`.

| Macrozona | Registros | F01/F02 | Señal externa ya almacenada | Lectura permitida |
| --- | ---: | ---: | ---: | --- |
| `MZ_BELGRANO` | 697 | 304 | 393 | Oferta registrada/visible; no equivale a locales activos. |
| `MZ_RECOLETA` | 767 | 404 | 363 | Oferta registrada/visible; no equivale a locales activos. |
| `MZ_COSTANERA_NORTE` | 72 | 5 | 67 | Señal exploratoria con dependencia externa alta. |

Campos de enlace y filtro: `id_punto`, `macrozona_id`, `lat`, `lon`, `fuente`. El cruce local existente agrega desde `universo_entidades_v1.csv` los campos `id_entidad`, `en_f01`, `en_f02`, `nombre_canonico`, `nombre_norm` y `direccion_normalizada`. Este preflight no exportó filas ni valores individuales.

## Sistemas de coordenadas

- Cálculo métrico previsto por los scripts existentes: `EPSG:5347`.
- Intercambio GeoJSON: `EPSG:4326`; los archivos inspeccionados declaran `OGC:CRS84`, equivalente en orden de coordenadas GeoJSON longitud/latitud.
- Regla para la futura corrida: transformar a `EPSG:5347` antes de medir distancias, áreas o buffers y volver a `EPSG:4326` solo al exportar. No medir en grados.

## Insumos principales con huella

| Insumo | Formato | Bytes | SHA-256 | Función prevista |
| --- | --- | ---: | --- | --- |
| `outputs/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/completa_v1/UNIVERSO_COMPLETO_SANITIZADO.csv` | CSV | 831054 | `bd309bd45e029a412d3d80e46084de287f4c29be5c0bbf1ec6e177bd4a5aad44` | Universo local vigente. |
| `outputs/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/completa_v1/MICROCLUSTERS_COMPLETA_V1.geojson` | GeoJSON | 2236634 | `3185ef76909917c7a926acab78ee15ebabade36fee99cbd44f852b740a8a97ae` | Capa previa de puntos/clusters, solo contraste. |
| `outputs/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/completa_v1/POLIGONOS_MICROZONAS_COMPLETA_V1.geojson` | GeoJSON | 1003782 | `62e49aa3f73c15a96efc40a74928d406b2f2cec0261c364f4be0d67da86b8f4e` | Capa analítica previa, solo lectura. |
| `outputs/polos_gastro/experimentos/pipeline_microzonas_v1/universo/universo_entidades_v1.csv` | CSV | 2117481 | `8c962bfb9d27981f5c660c453ad2e7996c1c9e36932c70ef64a1557e71a97dee` | Flags F01/F02 y enlace de entidades. |
| `outputs/polos_gastro/experimentos/infraestructura_cartografica_v1/macrozonas_editoriales_candidatas_v1.geojson` | GeoJSON | 239236 | `5d72327e9a67cbb9c938545e2784dddd47ed2c85d0532eff9f677e9901eb9b95` | Contenedores de contraste. |
| `outputs/polos_gastro/fase15_mapas_callejeros_v3/assets/callejero_gcba_2026_06_02.geojson` | GeoJSON | 23855699 | `a30de3bcfaddfecbb154a59bf0ec83530d103e954de87b00369e47baab415902` | Referencia vial local. |
| `PolosGastro/cartografia/barrios_caba.geojson` | GeoJSON | 740597 | `21e052e070808dd476364c765b40542699ae40ebfb8cdb86436107066d76d562` | Barrio oficial para contraste, protegido. |
| `PolosGastro/cartografia/comunas_caba.geojson` | GeoJSON | 584528 | `c128dadf5b8a3c43c68cad4dacd8c0995d774b93060a785b156861bcb9de062e` | Comunas oficiales, protegidas. |

## Belgrano

| Insumo | Contenido verificado | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| `outputs/polos_gastro/experimentos/pipeline_hibrido_repeticiones_v2/belgrano_estabilidad_nucleos_v2.csv` | 17 candidatos; métricas por bloque, fuente, KDE, borde y contenedor. | 3242 | `0bf3c8aba7e1415f031a06158c561f4ca35acf774b08116835cc771a68340f96` |
| `outputs/polos_gastro/experimentos/pipeline_hibrido_repeticiones_v2/belgrano_nucleos_candidatos_v2.geojson` | 17 features analíticas. | 68502 | `de29bce2bb38e7be9fff0f6309a52671e83b4755558b6c759db31f3f044251ca` |
| `outputs/polos_gastro/experimentos/pipeline_hibrido_integracion_v21/belgrano_evaluacion_editorial_candidatos_v21.csv` | Regla explícita de elegibilidad y shortlist. | 3181 | `4db86ed3ca31a5fc7d1b89f824ab5df122663a5cffffeb60adfa5529b08a02c5` |
| `outputs/polos_gastro/experimentos/pipeline_hibrido_integracion_v21/belgrano_shortlist_tecnica_v21.geojson` | 4 features: `BEL_RV2_N02`, `N03`, `N05`, `N06`. | 16786 | `ab596e1425f9f8e6a6ffdd42e3bc0a1d393519869ba68f20671dbf29532ab618` |

Campos clave disponibles: `identificador_tecnico`, `categoria`, `cantidad_puntos`, `f01_f02`, `places`, `dependencia_places_pct`, supervivencias `b150/b200/b300/b400`, `respaldo_kde`, `jaccard_sin_places`, `posiblemente_cortado`, `dependencia_contenedor` y `correspondencia_metodos`.

La baseline v2 registra 6 candidatos de estabilidad ALTA, 8 MEDIA y 3 BAJA. La v2.1 no valida nombres: Barrio Chino, Cabildo/Juramento, Bajo Belgrano y Barrancas/Libertador se usaron solo como referencias post hoc. La lectura editorial de Barrio Chino, Bajo Belgrano y Belgrano R permanece separada de la jerarquía técnica.

## Recoleta

| Insumo | Contenido verificado | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| `outputs/polos_gastro/experimentos/pipeline_hibrido_integracion_v21/recoleta_metricas_v21.csv` | Universo, cobertura, robustez, composición y sensibilidades. | 693 | `a227a72fed93d3d21f6d998ffaa65048ef9b2483ee4ff89e9638e78d7ed004aa` |
| `outputs/polos_gastro/experimentos/pipeline_hibrido_integracion_v21/recoleta_nucleos_analiticos_v21.geojson` | 9 núcleos técnicos. | 54798 | `fbbff323bca8ccdfd514c505c7e7bf63d8f6bf4245cf6b76caa6323dd370e5e6` |
| `outputs/polos_gastro/experimentos/pipeline_hibrido_integracion_v21/recoleta_nucleos_presentacion_v21.geojson` | 5 candidatos de presentación previos. | 29545 | `be12dda98356b13f945cdf16b73a415b8db1b0f7508767b90d309b2fcdda6459` |

Lectura v2.1: 9 núcleos candidatos sobre 767 registros; cobertura 78,23 %, robustez media 0,626, p10 0,068; 404 F01/F02 y 363 señales externas. Campos clave: `nucleo_id`, `n_puntos`, `f01_f02`, `places`, `places_pct`, `respaldo_kde`, `estado`, más las métricas de sensibilidad y ablación del CSV.

## Costanera Norte

| Insumo | Contenido verificado | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| `outputs/polos_gastro/experimentos/pipeline_hibrido_repeticiones_v2/costanera_componentes_v2.csv` | `CN_C01–CN_C04`; 71 registros asignados. | 375 | `39ef7f8fc7cfaa85b2d5bb26c6e6224942946e81980ccd34068cbded8eda77c6` |
| `outputs/polos_gastro/experimentos/pipeline_hibrido_repeticiones_v2/costanera_unidad_multiparte_v2.geojson` | Una unidad de presentación multiparte, 3 componentes principales. | 21643 | `e0a77c9329140d45dd39237595ad04486aefb8b2d13eaf4c21a55feb66c5f890` |
| `outputs/polos_gastro/experimentos/pipeline_hibrido_repeticiones_v2/costanera_concentracion_contextual_v2.geojson` | `CN_C02` contextual. | 4035 | `4577bb13ddd439a83ca23e42d79b17336624941b36987b2ef53a96fc76aad856` |
| `outputs/polos_gastro/experimentos/pipeline_hibrido_integracion_v21/costanera_conteos_corregidos_v21.csv` | Conciliación 72 = 71 asignados + 1 ruido localizado. | 664 | `0c296c050c22f6ba2deb825f4f896c46326a3919d9f78aa84eec16b84fb9cb3e` |
| `outputs/polos_gastro/experimentos/pipeline_hibrido_integracion_v21/costanera_unidad_multiparte_presentacion_v21.geojson` | Presentación discontinua de `CN_C01`, `CN_C03`, `CN_C04`. | 21517 | `265e970aa6004ee780868aab8e3025ff89e672bdaecbff47c63afeb682875107` |
| `outputs/polos_gastro/experimentos/pipeline_hibrido_integracion_v21/costanera_contexto_secundario_v21.geojson` | `CN_C02`: 11 registros, 0 F01/F02, 100 % señal externa. | 4232 | `cd64a6d3ff8cee5f3b9f1313fa795c5c52def608497e8c5fb0b513360e27475e` |

Campos clave: `componente_editorial`, `concentracion_tecnica`, `n_puntos`, `f01_f02`, `places`, `places_pct`, `estado`, `vacio_entre_componentes_preservado`. La diferencia 72/71 está localizada: un registro fue clasificado como ruido por el proceso previo; v2.1 lo documenta sin modificar v2.

## Robustez, sensibilidad y cobertura

- `outputs/polos_gastro/experimentos/auditoria_integral_places_clustering_gpt56/metricas_robustez_por_zona.csv` — 3174 bytes — SHA-256 `dad0df6078db102515c448f0008b985802a29b58b8a675e1b3e2c6780f5626c6`.
- `outputs/polos_gastro/experimentos/auditoria_integral_places_clustering_gpt56/sensibilidad_hdbscan_detalle.csv` — 4539 bytes — SHA-256 `494f2ba8f0848724140d3321db60869eba8d4e98d042a4cc868eb36e8121e10e`.
- `outputs/polos_gastro/experimentos/auditoria_integral_places_clustering_gpt56/sensibilidad_umbral_deduplicacion.csv` — 131 bytes — SHA-256 `f1674bb7f10b475c72f0a26dd9404463ff67013da367c18c0cbe8b2b7a8a6ab2`.
- `docs/polos_gastro/experimentos/pipeline_hibrido_integracion_v21/AUDITORIA_CONSISTENCIA_REPETICIONES_V2.md` y diagnósticos por zona.
- `docs/polos_gastro/experimentos/pipeline_hibrido_repeticiones_v2/COMPARACION_REPETICIONES_HIBRIDAS_V2.md` y QA final.

## Scripts reutilizables, sin ejecutar en esta tanda

| Script | Bytes | SHA-256 | Uso posterior controlado |
| --- | ---: | --- | --- |
| `scripts/polos_gastro/experimentos/pipeline_hibrido_tipo_territorial_v1/construir_pipeline_hibrido_v1.py` | 66815 | `23e8362e09ecd87b266459924ed722b1ee16ab71830d03055bb73d911d310e5b` | Carga canónica de universo, entidades, macrozonas y callejero. |
| `scripts/polos_gastro/experimentos/pipeline_hibrido_repeticiones_v2/ejecutar_repeticiones_hibridas_v2.py` | 65077 | `64702722ebbdda3ae5fbafd979de1c4ba4a4f5135e623d4978c292aa7dfeacaa` | Parámetros y pruebas previas de Belgrano y Costanera. Debe derivarse, no sobrescribirse. |
| `scripts/polos_gastro/experimentos/pipeline_hibrido_integracion_v21/construir_integracion_v21.py` | 61262 | `4e3b2fd5131e252717c5fa458af3d9b4afd5e50257f1323e670c55f728029d21` | Carga v2.1, separación analítica/presentación, QA y métricas. Solo lectura hasta instrucción. |

Parámetros existentes relevantes: semilla `260711`; HDBSCAN Costanera `min_cluster_size=8`, `min_samples=5`, método `eom`; Belgrano con grillas `eom/leaf`, Louvain con 20 semillas, KDE y bootstrap de 50 repeticiones para bloques de 150/200/300/400 m. Los buffers existentes son convenciones orientativas, no límites reales.

## Dependencias locales verificadas

Entorno: `.venv/Scripts/python.exe`, Python 3.12.10. Instaladas: NumPy 2.4.6, pandas 3.0.3, GeoPandas 1.1.3, Shapely 2.1.2, scikit-learn 1.9.0, SciPy 1.18.0, Matplotlib 3.11.0, Pillow 12.2.0, pyproj 3.7.2, pyogrio 0.12.1 y NetworkX 3.6.1.

Fiona y rtree no están instaladas. No se instalaron porque el stack actual usa pyogrio y Shapely; su ausencia debe revalidarse contra cualquier script nuevo antes de la corrida.

## Paquetes de revisión disponibles

| Paquete | Bytes | SHA-256 |
| --- | ---: | --- |
| `outputs/polos_gastro/REVISION_EVIDENCIA_DOCUMENTAL_POLOS_V1.zip` | 48990 | `6662999bc6a57a130f8099686d5fea5438afe0dc3fdabf9ef418089f3d528037` |
| `outputs/polos_gastro/experimentos/decisiones_y_repeticiones_pipeline_hibrido_v1/PAQUETE_DECISIONES_DIEGO.zip` | 3067756 | `28b07cf5e887d5910bf99066996e7bc4723d0bb9707cb93841f2a2e822ffa0c3` |
| `outputs/polos_gastro/experimentos/pipeline_hibrido_tipo_territorial_v1/REVISION_PROTOTIPOS_HIBRIDOS_V1.zip` | 4382699 | `b24208528d030abb09d2b6740efbb71c84b7a9d44dff231515209537db980420` |
| `outputs/polos_gastro/experimentos/pipeline_hibrido_repeticiones_v2/REVISION_REPETICIONES_HIBRIDAS_V2.zip` | 3140886 | `b5838e664471c206f6fe886bc18fe32bd13a282169cd37323d7e9391eac2b910` |
| `outputs/polos_gastro/experimentos/pipeline_hibrido_integracion_v21/REVISION_PIPELINE_HIBRIDO_INTEGRACION_V21.zip` | 7164598 | `9ca7b86c1b0a773021f2944843f9d27685dc6e7e7c4b4b238b91f51e52f466ba` |

Los paquetes son referencias de solo lectura. El handoff nuevo quedó disponible en dos copias idénticas:

- `docs/polos_gastro/evidencia_documental_integrada_v1/HANDOFF_DOCUMENTAL_CARTOGRAFO_V1.md` — 9551 bytes — SHA-256 `3735a6d803774e1c4c2d099a83d6109f33d14bfb5a7052815b7fd494c918ae7a`.
- `outputs/polos_gastro/evidencia_documental_integrada_v1/REVISION_EVIDENCIA_DOCUMENTAL_INTEGRADA_V1/04_HANDOFF/HANDOFF_DOCUMENTAL_CARTOGRAFO_V1.md` — 9551 bytes — mismo SHA-256.

La evaluación se registra en `ESTADO_ESPERA_HANDOFF_DOCUMENTAL.md`.
