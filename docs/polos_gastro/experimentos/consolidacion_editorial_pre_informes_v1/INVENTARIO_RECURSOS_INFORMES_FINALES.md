# Inventario de recursos para los informes finales de Polos

Estado: DOCUMENTACIÓN EDITORIAL EXPERIMENTAL. Fecha: 2026-07-11.
Destinos: **[F25P]** Fase 25 pulida política · **[HIB]** informe híbrido · **[MET]**
informe metodológico. "Codex" = depende de los resultados técnicos que Codex está
produciendo en carpetas nuevas (no inspeccionadas ni tocadas por este trabajo).

## 1. Mapas existentes reutilizables

| Recurso | Ruta | Estado | Calidad | Utilidad / destino | ¿Actualizar? | ¿Codex? |
| --- | --- | --- | --- | --- | --- | --- |
| Mapa detalle Palermo/Las Cañitas | `outputs/polos_gastro/fase25_microajustes_finales_oficina/assets/mapa_fase25_palermo_las_canitas.png/.svg` | final F25 | alta | plantilla de lámina; [F25P] | leyenda/tags (regenerar con misma geometría) | no |
| Mapa detalle San Telmo | `…/assets/mapa_fase25_san_telmo.png/.svg` | final F25 | alta | [F25P] | leyenda/tags; geometría solo si DH-01 c) | parcial (soporte Defensa) |
| Mapa detalle Corrientes/Abasto | `…/assets/mapa_fase25_corrientes_abasto.png/.svg` | final F25 | alta | [F25P]; compatible con DEC-01 | título/rotulado Abasto | no |
| Mapa detalle Belgrano | `…/assets/mapa_fase25_belgrano.png/.svg` | final F25 | alta | [F25P] con rótulos unificados (DEC-04) | tags unificados | no (geometría F25 se mantiene) |
| Mapa detalle Puerto Madero | `…/assets/mapa_fase25_puerto_madero.png/.svg` | final F25 | media (tags mezclados) | [F25P] provisorio | esperar DH-06 | sí |
| Contact sheets QA F25 | `…/contact_sheet_pdf_pages_fase25.png`, `…/contact_sheet_mapas_fase25.png` | final | alta | control de regresión visual [F25P] | no | no |

## 2. Mapas que necesitan rediseño

| Recurso | Ruta base | Problema | Destino | ¿Codex? |
| --- | --- | --- | --- | --- |
| Mapa global | `…/assets/global_mapa_fase25.png`, `mapa_global_fase25_completo.png` | sin jerarquía visual; ocupa media página; leyenda con "aproximado"; Costanera como eje continuo (contradice DEC-05) | [F25P] (prioridad 1), base de [HIB] | no para jerarquía editorial; sí para Costanera multiparte |
| Estructuras híbridas por zona | `outputs/polos_gastro/experimentos/pipeline_hibrido_tipo_territorial_v1/mapas/` + geojson candidatos (`san_telmo_nucleo_candidato.geojson`, `corrientes_eje_candidato.geojson`, `corrientes_buffer_candidato.geojson`, `belgrano_nucleos_candidatos.geojson`, `puerto_madero_frentes_candidatos.geojson`, `costanera_concentraciones_exploratorias.geojson`) | son prototipos v1; Belgrano y Puerto Madero serán reemplazados por las repeticiones | [HIB] | sí (repeticiones v2) |
| Cartografía técnica v4.2 | `outputs/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/cartografia_design_v4_2/` | no publicable como delimitación; útil como insumo comparativo | [MET] (comparativas antes/después) | no |
| Macrozonas editoriales candidatas | `outputs/polos_gastro/experimentos/infraestructura_cartografica_v1/macrozonas_editoriales_candidatas_v1.geojson` + mapas PNG asociados | pendiente checklist ✓/△/✗ de Diego+DGDGAS | [HIB] (contenedores), [MET] | no (bloqueado por revisión humana, no por Codex) |

## 3. Tablas

| Recurso | Ruta | Estado | Destino |
| --- | --- | --- | --- |
| Universo del informe (22 polos/ejes) | `outputs/polos_gastro/universo_informe_polos_gastro.csv` | estable | [F25P] [MET] |
| Nombres públicos de polos | `outputs/polos_gastro/nombres_publicos_polos_gastro.csv` | estable | [F25P] [HIB] |
| Comparación prototipos híbridos | `outputs/polos_gastro/experimentos/pipeline_hibrido_tipo_territorial_v1/tabla_comparacion_prototipos_hibridos_v1.csv` | v1 | [HIB] anexo, [MET] |
| Métricas de estabilidad desagregadas | `…/metricas_estabilidad_desagregadas_v1.csv` | v1 (Belgrano/PM se reharán) | [MET] | 
| Mezcla de fuentes por representación | `…/mezcla_fuentes_representaciones_v1.csv` | v1; heredan error de apareo (DH-11) | [HIB] anexo B, [MET] |
| Diagnóstico Places por zona | `…/diagnostico_places_por_zona_corregido.csv` | corregido | [MET] |
| Comparación por zona Fase25 vs nuevo | `outputs/polos_gastro/experimentos/auditoria_integral_places_clustering_gpt56/` (`comparacion_por_zona_fase25_nuevo.csv`) | final auditoría | [MET] |
| Inventario ejes viales Puerto Madero | `outputs/polos_gastro/experimentos/decisiones_y_repeticiones_pipeline_hibrido_v1/inventario_ejes_viales_puerto_madero.csv` | final | [HIB] (soporte frente), [MET] |
| Planes de prueba Belgrano / Puerto Madero | `…/tabla_plan_pruebas_belgrano.csv`, `…/tabla_plan_pruebas_puerto_madero.csv` | especificación | [MET]; insumo directo de Codex |
| Matriz de ajustes Fase 25 | `docs/polos_gastro/experimentos/consolidacion_editorial_pre_informes_v1/MATRIZ_AJUSTES_FASE25.csv` | nuevo (este paquete) | [F25P] |

## 4. Gráficos

| Recurso | Ruta | Estado | Destino |
| --- | --- | --- | --- |
| Gráficos históricos del subproyecto | `outputs/polos_gastro/graficos/` | heredados (pre-F25) | revisar caso a caso; mayoría [MET] |
| Comparativos mundo A vs B | `outputs/polos_gastro/experimentos/infraestructura_cartografica_v1/comparativo_mundo_a_vs_b_*.png` | experimental | [MET] |
| Perfiles longitudinales (Corrientes, PM) | `…/pipeline_hibrido_tipo_territorial_v1/corrientes_perfil_longitudinal.csv`, `puerto_madero_perfil_frente.csv` | v1, datos para graficar | [HIB] anexo (subtramos narrativos DEC-02), [MET] |
| Gráficos nuevos del [MET] (línea de tiempo, embudos, barras de dependencia) | por crear | — | [MET]; especificados en su arquitectura | 

## 5. Textos

| Recurso | Ruta | Estado | Destino |
| --- | --- | --- | --- |
| Textos vigentes de Fase 25 (títulos, cajas, notas) | dentro de `scripts/polos_gastro/build_fase22…25*.py` (cadena de herencia) | final F25 | base de [F25P] con reemplazos de la guía |
| Registro de decisiones | `docs/…/consolidacion_editorial_pre_informes_v1/REGISTRO_DECISIONES_APROBADAS_DIEGO.md` | nuevo | los tres informes |
| Guía de lenguaje | `…/GUIA_LENGUAJE_INFORMES_POLOS.md` | nuevo | los tres informes |
| Narrativa metodológica fuente | `docs/polos_gastro/experimentos/auditoria_integral_places_clustering_gpt56/*.md`, `…/pipeline_hibrido_tipo_territorial_v1/*.md`, `docs/polos_gastro/experimentos_clustering*/` | final por experimento | [MET] (actos I–III pre-redactables) |
| Fichas y universo defendible (fases 5–12) | `docs/polos_gastro/FASE_5_*.md`, `UNIVERSO_DEFENDIBLE_INFORME_POLOS_GASTRO.md` | históricos | [MET] acto I |

## 6. Logos y tokens visuales

| Recurso | Ruta | Estado | Destino |
| --- | --- | --- | --- |
| Guía de estilo DGDGAS para informes | `outputs/datagastro_design_system/claude_design_pack/GUIA_ESTILO_DGDGAS_INFORMES.md` | v1 | los tres informes |
| Pack de diseño (componentes, referencias, prompt) | `outputs/datagastro_design_system/claude_design_pack/` (+ `claude_design_pack_dgdgas_informes_v1.zip`, `previews/`) | v1 | [F25P] [HIB] |
| Paleta/estilo implícito de F25 (azul institucional #1f3a5f aprox., acento ladrillo, cajas redondeadas) | codificado en la cadena de generadores fase22→25 | final | mantener como base; unificar con el pack |
| Inputs de diseño de mapas (fase 18) | `docs/polos_gastro/fase18_claude_design_mapas/inputs/` | insumo | [HIB] (mapas por tipo) |

## 7. Generadores

| Recurso | Ruta | Estado | Destino | ¿Codex? |
| --- | --- | --- | --- | --- |
| Generador Fase 25 (hereda 24→22) | `scripts/polos_gastro/build_fase25_microajustes_finales_oficina.py` | final; NO tocar | [F25P] se implementa como fase nueva heredando de este | no |
| Generadores de mapas híbridos v1 | `scripts/polos_gastro/experimentos/` (pipeline híbrido) | experimental | [HIB]; se actualizan con lo de Codex | sí |
| QA visual de PDFs | `scripts/qa/pdf_check.py` | estable | QA obligatorio de los tres informes | no |
| Validador de KPIs | `scripts/qa/validate_kpis.py` | estable | [MET] (kpis_lock propio) y los tres informes | no |

## 8. Capas cartográficas

| Recurso | Ruta | Estado | Destino |
| --- | --- | --- | --- |
| Inventario de capas urbanas locales | `outputs/polos_gastro/experimentos/pipeline_hibrido_tipo_territorial_v1/inventario_capas_urbanas_locales.csv` | v1 | [HIB] (soporte vial de corredores/frentes) |
| Base callejera GCBA para mapas de detalle | pendiente (plan mapas V3: "próximo paso = fuente GCBA") | faltante | [F25P] mejora opcional; [HIB] necesario para corredores | 
| GeoJSON de estructuras candidatas (por zona) | ver §2 | v1 | [HIB] |
| Polígonos reales Palermo Soho/Hollywood | `outputs/polos_gastro/experimentos/infraestructura_cartografica_v1/poligono_real_palermo_*.geojson` | experimental | [HIB] escalado Palermo |

## 9. Documentación metodológica

| Recurso | Ruta | Estado | Destino |
| --- | --- | --- | --- |
| Auditoría integral GPT-5.6 (9 documentos) | `docs/polos_gastro/experimentos/auditoria_integral_places_clustering_gpt56/` | final | [MET] cap. 12 |
| Pipeline híbrido v1 (12 documentos: diagnósticos por zona, QA, plan de escalado) | `docs/polos_gastro/experimentos/pipeline_hibrido_tipo_territorial_v1/` | final v1 | [MET] cap. 13, [HIB] |
| Decisiones y repeticiones (matriz DH, especificaciones, revisión crítica) | `docs/polos_gastro/experimentos/decisiones_y_repeticiones_pipeline_hibrido_v1/` | final | [MET] cap. 14; insumo de Codex |
| Clustering v1/v2 (diagnóstico DBSCAN, recomendación metodológica) | `docs/polos_gastro/experimentos_clustering/`, `…_clustering_v2/` | final | [MET] caps. 7–8 |
| Piloto y ampliación Google Places microzonas | `docs/polos_gastro/experimentos/google_places_microzonas_piloto/`, `…_ampliacion_v1/`, `docs/polos_gastro/fase11_google_places_piloto/` | final | [MET] cap. 5 |
| QA y cambios de Fase 25 | `docs/polos_gastro/fase25_microajustes_finales_oficina/` (3 documentos) | final | [F25P] (línea base), [MET] cap. 2 |
| Este paquete editorial | `docs/polos_gastro/experimentos/consolidacion_editorial_pre_informes_v1/` | nuevo | los tres informes |

## 10. Lectura del inventario

- **Listo para usar sin esperar a Codex:** todos los assets de Fase 25 (con ajustes de
  leyenda), el pack de diseño, la documentación metodológica de los actos I–III, las
  tablas de la auditoría, los textos base y los dos QA scripts.
- **Bloqueado por Codex:** geometrías finales de Belgrano y Puerto Madero, soporte del
  eje Defensa (San Telmo), representación multiparte de Costanera, y toda métrica que
  las repeticiones actualicen.
- **Bloqueado por decisión humana (no por Codex):** checklist de macrozonas
  editoriales, DH-01/05/06/10 finales, etiquetado de deduplicación (DH-11), nombres de
  subtramos de Corrientes (DEC-02).
- **Faltante real:** base callejera GCBA para mapas de detalle de calidad callejera.
