# Caso D — Cartografía analítica vs presentación

**Fecha:** 2026-07-11  
**Agente simulado:** `cartografo_territorial`  
**Insumo (solo lectura), Puerto Madero v2.1:**

| capa | ruta |
| --- | --- |
| Analítica | `outputs/polos_gastro/experimentos/pipeline_hibrido_integracion_v21/puerto_madero_capa_analitica_v21.geojson` |
| Presentación (opciones) | `.../puerto_madero_opciones_presentacion_v21.geojson` |
| Tabla simplificación | `.../tabla_simplificacion_puerto_madero_v21.csv` |
| Mapa comparativo | `.../mapa_puerto_madero_analitica_vs_presentacion_v21.png` |

También disponibles (no regenerados): Corrientes y San Telmo `*_presentacion_v21.geojson`.

**Salida:**  
`outputs/infraestructura_agentes_skills_v1/casos_prueba/caso_d_checklist_transformacion.md`  
**No se regeneraron mapas.**

## Diferencia analítica vs presentación

| Dimensión | Analítica | Presentación |
| --- | --- | --- |
| Propósito | métricas, cobertura, opciones de frente, reproducibilidad | lectura visual / informe |
| Geometría | capa de análisis (p. ej. banda/frente con parámetros) | simplificación / tolerancia documentada |
| PM tabla | puntos_universo 294; cobertura ~80.27% en opciones A/B/C | PM_PRES_C recomendada **no vinculante** (tol. 65 m, bin 200 m) |
| Riesgo | sobreajustar parámetros | vender simplificación como límite oficial |
| Archivo | `puerto_madero_capa_analitica_v21.geojson` (~11.5 KB) | `puerto_madero_opciones_presentacion_v21.geojson` (~2.8 KB) |

## Checklist de transformación (sin ejecutar)

Ver `caso_d_checklist_transformacion.md`.

## Controles

- Sin regenerar mapas.  
- Sin editar GeoJSON.  
- Sin commit.

## Resultado del caso

**PASS**.
