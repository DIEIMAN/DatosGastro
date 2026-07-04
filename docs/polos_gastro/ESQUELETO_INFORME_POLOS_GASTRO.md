# Esqueleto futuro de informe PolosGastro

Este documento es una base de estructura para una fase posterior. No es un informe final PDF, no contiene conclusiones institucionales cerradas y no debe presentarse como producto terminado.

## 1. Portada

Título tentativo, fecha de corte, área responsable y advertencia de alcance.

## 2. Resumen ejecutivo

Síntesis de objetivo, fuente inicial, hallazgos validados y próximos pasos.

## 3. Qué es un polo gastronómico

Definición operativa: barrio, corredor, avenida, subpolo y zona turística/gastronómica.

## 4. Mapa conceptual de zonas/corredores

Visual futuro, sujeto a validación cartográfica. No generar mapa final hasta definir polígonos o tramos.

## 5. Polos consolidados

Casos con evidencia documental y validación complementaria.

## 6. Polos emergentes

Casos candidatos o incipientes con necesidad de relevamiento adicional.

## 7. Locales destacados como evidencia cualitativa

Uso prudente de menciones de locales. Aclarar que no son padrón oficial, no prueban vigencia y no delimitan por sí solos un polo.

## 8. Oportunidades de gestión

Posibles usos: agenda territorial, promoción, circuitos, diagnóstico de cobertura y articulación con turismo/cultura/desarrollo económico.

## 9. Limitaciones metodológicas

Fuente semilla, ausencia de delimitación formal, vigencia no validada, sesgos territoriales y necesidad de fuentes complementarias.

## 10. Próximos pasos

Validar fuente, construir ficha, definir criterios, contrastar con datos públicos y evaluar integración futura con DataGastro.

<!-- FASE2_PENDIENTES_INFORME_FINAL_START -->
## Pendientes antes del informe final

- Validacion de URLs pendientes.
- Busqueda de fuentes complementarias para casos debiles o ambiguos.
- Delimitacion territorial por polo, subpolo, avenida o corredor.
- Mapa conceptual por comunas, barrios y corredores.
- Clasificacion final de polos consolidados, relevantes, emergentes y candidatos.
- Cruce futuro con Buenos Aires Data.
- Posible cruce futuro con habilitaciones gastronomicas si se habilita metodologicamente.
- Posible geocodificacion futura de locales destacados.
- Cuidado metodologico para no convertir fuentes turisticas, datos abiertos o locales destacados en padron oficial.
<!-- FASE2_PENDIENTES_INFORME_FINAL_END -->

<!-- FASE3_UNIVERSO_DEFENDIBLE_START -->
## Estructura sugerida segun universo defendible

1. Portada.
2. Resumen ejecutivo.
3. Que es un polo gastronomico y como se construyo el universo.
4. Nucleo de polos consolidados.
5. Zonas relevantes.
6. Corredores emergentes y candidatos.
7. Lectura territorial preliminar.
8. Oportunidades de gestion.
9. Limitaciones metodologicas.
10. Anexo de casos pendientes y fuentes.

Nota: esta estructura no habilita todavia PDF final, mapas finales ni geocodificacion. Primero debe cerrarse delimitacion territorial y validacion de URLs pendientes.
<!-- FASE3_UNIVERSO_DEFENDIBLE_END -->

<!-- FASE3A_PENDIENTES_MAPA_CONCEPTUAL_START -->
## Pendientes para mapa conceptual

- URLs pendientes criticas o especificas: PX023A, PX023B, PX024B, PX025A.
- Delimitaciones sin fuente: Federico Lacroze / Libertador a Cabildo; Parque Saavedra / Garcia del Rio.
- Diferenciar barrios, subpolos, avenidas, corredores y zona central antes de diseñar simbolos.
- Evitar mapas con poligonos falsamente precisos.
- Evaluar un mapa por puntos, etiquetas o familias antes que poligonos cerrados.
- Separar visualmente polos consolidados, zonas relevantes, emergentes/candidatos, anexo y no incluir por ahora.
<!-- FASE3A_PENDIENTES_MAPA_CONCEPTUAL_END -->

<!-- FASE3B_VISUALES_DISPONIBLES_START -->
## Visuales disponibles para informe futuro

La Fase 3B deja disponibles visuales de apoyo para un informe posterior:

- Universo por grupo: muestra que el universo no entra todo con la misma jerarquía.
- Precisión de delimitación: explica por qué no corresponde hacer polígonos cerrados para todo.
- Familias territoriales: ordena los polos por familias y grupo de informe.
- Mapa conceptual preliminar: diagrama territorial esquemático, no cartográfico.
- Mapa conceptual completo: versión de trabajo con más casos visibles para revisión interna.

Estos visuales no son mapas finales. No geocodifican locales, no usan polígonos definitivos, no generan shapefiles/geojson y no deben publicarse como delimitación oficial.
<!-- FASE3B_VISUALES_DISPONIBLES_END -->

<!-- FASE_AUDITORIA_CARTOGRAFIA_PENDIENTES_START -->
## Pendientes de auditoría y cartografía (antes del borrador)

Fase de auditoría técnica y exploración cartográfica/visual (2026-06-29). **No iniciar el
informe final** hasta cerrar estas decisiones:

- **Auditoría integral**: ver `AUDITORIA_INTEGRAL_PRE_INFORME_POLOS_GASTRO.md` y
  `QA_CONSISTENCIA_UNIVERSO_POLOS_GASTRO.md` (universo consistente; pendientes documentados).
- **Cartografía pendiente**: decidir si el informe usa mapa territorial real (GeoPandas +
  matplotlib sobre barrios GeoJSON de Buenos Aires Data) o se mantiene en diagrama conceptual.
  Ver `cartografia/FUENTES_CARTOGRAFICAS_CABA.md` y
  `cartografia/LIBRERIAS_MAPAS_INFORMES_DATAGASTRO.md`.
- **Estilo visual pendiente**: definir simbología institucional (paleta DataGastro, marcadores
  por nivel de evidencia/precisión); rediseñar familias y mapa conceptual completo; reubicar la
  caja "No mapeados". Ver `PROPUESTA_VISUAL_INFORME_POLOS_GASTRO.md` y
  `AUDITORIA_VISUAL_GRAFICOS_POLOS_GASTRO.md`.
- **Fuentes adicionales pendientes**: cerrar (o asumir como pendientes) las 4 URLs
  (PX023A/B, PX024B, PX025A) y reforzar polos débiles. Ver
  `PEDIDOS_EXTERNOS_PARA_MEJORAR_POLOS_GASTRO.md`.
- **Cartografía interactiva (futuro)**: `@usig-gcba/mapa-interactivo` documentado en
  `cartografia/USIG_MAPA_INTERACTIVO_NOTAS_TECNICAS.md`; prototipo aislado en
  `scripts/polos_gastro/cartografia_experimentos/usig_mapa_interactivo_minimo/`.

No iniciar PDF final, mapa final, geocodificación ni shapefiles/geojson definitivos hasta que
estas decisiones estén cerradas y autorizadas.
<!-- FASE_AUDITORIA_CARTOGRAFIA_PENDIENTES_END -->

<!-- FASE4A_VISUAL_COMPLETADA_START -->
## Fase 4A — Rediseño visual completada

Visuales aptos para informe (en `outputs/polos_gastro/graficos/fase4a/`):
- `universo_polos_por_grupo_v2.png`, `precision_delimitacion_polos_v2.png`,
  `familias_territoriales_polos_v2.png` (barras agrupadas).
- `mapa_conceptual_polos_gastro_resumido_v2.png` (sin solapes).
- `mapa_estatico_caba_polos_gastro_nucleo_v1.png` y `..._v1.png` — **mapa territorial real** con
  barrios oficiales de Buenos Aires Data.

**Cartografía usada**: Barrios/Comunas CABA GeoJSON (Buenos Aires Data), en
`PolosGastro/cartografia/`. Ver `cartografia/fase4a/CARTOGRAFIA_USADA_FASE4A.md`.

**Decisión metodológica**: el informe lleva mapa territorial real, pero **barrios/comunas son
referencia territorial, no delimitación oficial de polos**. Sin polígonos de polos, sin
coordenadas Google, sin geocodificar locales. Nota metodológica visible en cada mapa.

QA y reporte: `cartografia/fase4a/QA_VISUALES_REGENERADOS_FASE4A.md` y
`cartografia/fase4a/REPORTE_VISUALES_FASE4A.md`. Plan de armado:
`PLAN_ENSAMBLADO_INFORME_POLOS_GASTRO.md`.

Próximo paso: Fase 5 (primer borrador Markdown). **No iniciar PDF final todavía.**
<!-- FASE4A_VISUAL_COMPLETADA_END -->
