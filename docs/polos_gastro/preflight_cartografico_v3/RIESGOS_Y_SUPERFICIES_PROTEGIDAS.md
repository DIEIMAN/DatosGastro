# Riesgos y superficies protegidas

**Estado:** control previo completado; corrida no iniciada.

## Superficies verificadas

El registro canónico es `docs/polos_gastro/PROTECTED_SURFACES.yaml`. Se verificaron como solo lectura:

| ID | Patrón protegido | Regla operativa |
| --- | --- | --- |
| `POLOS-SRC-SEMILLA` | `PolosGastro/**` | No modificar fuentes semilla. |
| `POLOS-BASE-OFICINA-CERRADA` | `docs/polos_gastro/fase25_microajustes_finales_oficina/**` | Baseline cerrada. |
| `POLOS-OUT-OFICINA-CERRADA` | `outputs/polos_gastro/fase25_microajustes_finales_oficina/**` | Entregable cerrado. |
| `POLOS-SCRIPT-OFICINA` | `scripts/polos_gastro/build_fase25_microajustes_finales_oficina.py` | Generador cerrado. |
| `POLOS-EXP-CARTO-CERRADA` | `outputs/.../fase26_comparativa_cartografia/**` | Fase 26 de solo lectura. |
| `POLOS-EXP-COMPLETA-V1` | `outputs/.../completa_v1/**` | Universo y resultados experimentales cerrados. |
| `POLOS-EXP-CARTO-V4X` | `outputs/.../cartografia_*/**` | Cartografías editoriales v2–v4.x cerradas. |
| `POLOS-HIBRIDO-V1*` | docs y outputs del pipeline híbrido v1 | Baseline experimental cerrada. |
| `POLOS-HIBRIDO-REP-V2*` | docs y outputs de repeticiones v2 | Baseline experimental cerrada. |
| `POLOS-HIBRIDO-INT-V21-*` | docs y outputs de integración v2.1 | Baseline experimental cerrada. |
| `POLOS-EVIDENCIA-PACK` | `outputs/polos_gastro/REVISION_EVIDENCIA_DOCUMENTAL_POLOS_V1/**` | Pack de revisión cerrado. |
| `POLOS-PIPE-GENERAL` | `src/build_*.py` | Pipeline general protegido. |

Control previo y posterior: 479 archivos, 120896589 bytes, SHA-256 compuesto `063b3f8956273f2754bbc839628b99b51cfe3ffb457d20c536cf31df4f044278` en ambos momentos; diferencias: 0. Este valor es un control de sesión construido sobre rutas, tamaños y hashes de contenido; no reemplaza los manifests canónicos.

## Decisiones humanas vigentes

- **DEC-12:** Belgrano continúa experimental, sin número de polos ni nombres definitivos. La correspondencia urbana es post hoc y requiere firma humana.
- **DEC-13:** Costanera Norte mantiene una identidad única multiparte; `CN_C01`, `CN_C03` y `CN_C04` son principales y `CN_C02` contexto secundario. La ubicación editorial de `CN_C02` sigue abierta.
- **DEC-07:** el pipeline híbrido complementa Fase 25; no la reemplaza.
- **DEC-08:** los puntos no asignados se clasifican con taxonomía explícita; no todo es ruido.
- **DEC-09:** los buffers son convenciones cartográficas orientativas, no mediciones.
- Recoleta permanece pendiente de decisión sobre su incorporación y representación; la técnica no puede imponer una unidad o nombres.

## Riesgos detectados y mitigaciones

| Riesgo | Severidad | Evidencia actual | Mitigación obligatoria |
| --- | --- | --- | --- |
| Sobrescribir v2.1 o una capa cerrada | Crítica | v2.1 figura en el registro protegido. | Línea paralela nueva, hashes pre/post y rutas de salida exclusivas. |
| Ejecutar sin instrucción posterior al handoff | Crítica | El handoff apareció y fue evaluado, pero esta tanda sigue siendo solo preparatoria. | Detención tras evaluación de compatibilidad; no iniciar corrida. |
| Reabrir Fase 25 o Fase 26 | Crítica | Ambas superficies están cerradas. | Solo lectura; excluirlas de cualquier escritura futura. |
| Convertir una geometría técnica en límite institucional | Alta | Las capas se rotulan experimentales. | Separar analítica/presentación y exigir decisión humana. |
| Fragmentación excesiva de Belgrano | Alta | 17 candidatos v2; 6/8/3 por estabilidad. | Comparar unidad macro y centralidades; penalizar cantidad de piezas. |
| Hull gigante en Belgrano | Alta | El barrio completo se usa como contraste, no como forma automática. | Medir área sin soporte, huecos y continuidad; prohibir envolvente no restringida. |
| Nombres anticipados en Belgrano | Alta | DEC-12 mantiene nombres diferidos. | Topónimos solo post hoc y sujetos al handoff y firma humana. |
| Disolver los nueve núcleos de Recoleta ocultando vacíos | Alta | v2.1 tiene 9 analíticos y 5 de presentación. | Comparar unidad única vs máximo dos subzonas; control de vacíos y área sin soporte. |
| Absorber Retiro o fijar Callao–9 de Julio sin evidencia | Alta | Son relaciones solicitadas para evaluación, no decisiones. | Tratarlas como transición/hipótesis y exigir compatibilidad documental. |
| Resolver mal la doble regla de `CN_C02` | Alta | El handoff exige cuatro componentes incluidos; DEC-13 lo conserva como contexto secundario. | Representar/evaluar los cuatro, mantener `CN_C02` contextual y no forzar el clustering ni promover jerarquía. |
| Rellenar discontinuidades de Costanera | Alta | DEC-13 exige multiparte discontinua. | Prohibir conectores, hull común y buffers de continuidad. |
| Inferir informalidad o falta de habilitación | Crítica | Las fuentes no prueban estatus regulatorio. | Usar “oferta registrada/visible” y abstenerse de inferencias regulatorias. |
| Confundir oferta con actividad actual | Alta | Universo mezcla registros y señal externa. | No usar “locales activos”; mostrar fuente, universo y fecha. |
| Dependencia de señal externa | Alta | Belgrano 56,38 %, Recoleta 47,33 %, Costanera 93,06 %. | Ablación por fuente, composición visible y lenguaje prudente. |
| Inconsistencia 72/71 en Costanera | Media | v2.1 localiza un ruido no resumido por v2. | Mantener conciliación 71+1; no modificar v2 ni asignar el punto por conveniencia. |
| Medir en CRS geográfico | Alta | GeoJSON se exporta en CRS84. | Transformar a EPSG:5347 antes de medir. |
| Drift de dependencias | Media | Entorno actual es funcional; Fiona/rtree ausentes. | Revalidar imports sin instalar; usar stack existente o detenerse. |
| Exposición de registros individuales | Alta | El universo contiene identificadores y atributos de punto. | Trabajar con métricas/capas agregadas; no exportar filas ni valores individuales. |
| Contaminar Git con cambios ajenos | Alta | Working tree ya estaba ampliamente sucio. | No limpiar, stagear ni modificar archivos ajenos; reportar solo rutas creadas en esta tanda. |

## Git y privacidad

- Prohibidos y no ejecutados: `git add`, staging, commit, push, reset destructivo y limpieza.
- El estado previo ya incluía modificaciones y archivos no rastreados ajenos a esta tarea; se preservaron.
- Este preflight no incluye emails, teléfonos, CUIT/DNI, nombres de personas, claves, enlaces privados ni valores individuales del universo.
- Los nombres de campos técnicos se documentan para reproducibilidad; no se copiaron registros.
