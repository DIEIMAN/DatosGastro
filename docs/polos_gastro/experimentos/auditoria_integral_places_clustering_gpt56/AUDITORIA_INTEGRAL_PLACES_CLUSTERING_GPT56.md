# Auditoría integral de Places, clustering y cartografía

Estado: experimental, no oficial. Fecha de corte: 10 de julio de 2026.

## 1. Veredicto ejecutivo

**PIPELINE_HIBRIDO_POR_TIPO_TERRITORIAL.**

El pipeline actual es valioso como sistema de detección y QA, pero no es adecuado como generador uniforme de polígonos institucionales. HDBSCAN debe conservarse como detector principal; KMeans debe dejar de definir unidades territoriales; la representación final debe depender de si la señal es núcleo, corredor, red multinuclear, frente o exploración.

## 2. Qué está sólidamente validado

- **Hecho:** el universo F01/F02 contiene 9.739 entidades, 9.738 aptas para clustering.
- **Hecho:** el universo vigente dentro de 13 macrozonas contiene 6.461 IDs únicos: 3.240 F01/F02 y 3.221 Places.
- **Hecho:** CSV y GeoJSON tienen los mismos 6.461 IDs.
- **Hecho:** 5.343 puntos se asignan una sola vez a un cluster final y 1.118 quedan como ruido.
- **Hecho:** las 163 microzonas están mapeadas completamente a v2; v2 produce 55 grupos, retiene 41 y excluye 14; los 41 pasan a 31 unidades v4 sin faltantes.
- **Hecho:** v4.2 no cambia datos, geometría analítica ni conteos.

## 3. Qué mejoró respecto de Fase 25

La mejora principal es de evidencia. Fase 25 era una lectura editorial prudente de una semilla de 106 referencias y 22 polos/ejes. La nueva línea cuantifica concentración, ruido, composición por fuente y subestructura dentro de 13 macrozonas. También mejora trazabilidad, QA y jerarquía visual.

## 4. Qué no está validado

- Que los 6.461 puntos representen establecimientos operando hoy.
- Que Places tenga cobertura homogénea o recall conocido.
- Que los umbrales de deduplicación maximicen precisión y recall.
- Que los clusters tengan nombres o límites institucionalmente aceptables.
- Que 10 ha sea una escala territorial válida.
- Que KMeans identifique unidades urbanas.
- Que los recortes visuales v4.1 sean equivalentes a reasignación analítica.

## 5. Riesgos actuales

Los riesgos principales son dependencia de Places, subcaptura en 58 celdas saturadas, contención por macrozonas previas, duplicación residual posible, sensibilidad jerárquica, tiles KMeans, solapes v4, nombres manuales y falsa precisión poligonal.

## 6. Diagnóstico de Places

Places aporta 49,9 % del universo. Cambia estructuralmente el número de clusters o el ruido en 10 de 13 macrozonas. Es decisivo en Costanera (93,1 %), Puerto Madero (71,1 %), Caseros (69,0 %), Chacarita (65,5 %), Villa Crespo (60,5 %) y Caballito (60,4 %).

El piloto verificó 379 consultas y 1.651 incorporaciones bajo sus propias reglas. La integración completa vuelve a procesar el origen y retiene 1.684, una diferencia de 33 por contención/reglas. La ampliación acumulada verifica 3.221 nuevos, no doble contados por ID.

## 7. Diagnóstico de deduplicación

La resolución reduce repetición administrativa y evita pares cruzados dentro de 15 m. Sin embargo, 844 filas participan en coordenadas exactas repetidas y la cola de proximidad/nombre identifica 2.217 pares potencialmente duplicados. Son candidatos, no confirmaciones. Falta una muestra manual etiquetada.

El uso de un único vecino más cercano puede omitir un segundo vecino compatible. El colapso F02 por ubicación puede fusionar negocios distintos. No se recomienda cambiar reglas sin estimar error.

## 8. Diagnóstico de clustering

HDBSCAN supera a DBSCAN global en el problema correcto: densidades distintas. La estabilidad es heterogénea. Es alta bajo perturbaciones locales en Corrientes, Caballito, Puerto, Costanera y Caseros; media en Microcentro, Hollywood, Recoleta y San Telmo; baja en Belgrano, Chacarita, Soho y Villa Crespo.

La selección `leaf` y epsilon 100 producen cambios grandes en varias zonas. El entorno actual es scikit-learn 1.8.0 y acepta epsilon 50; no se reprodujo una incompatibilidad de 1.9. Palermo Soho sí quedó registrado con epsilon 0 en la corrida vigente, sin conservar el error que activó el fallback.

## 9. Diagnóstico de polígonos

Los 163 polígonos usan concave hull 0,4 y buffer de 35 m. Es apropiado sólo para núcleos compactos. KMeans genera 91 polígonos y particiona 3.045 puntos. Corrientes y Caballito dependen completamente de esa subdivisión. El límite de 18 ha y objetivo de 10 ha son gates técnicos, no criterios urbanos.

## 10. Diagnóstico editorial

La reducción a 31 unidades resuelve saturación visual. No resuelve fundamento territorial. v4 presenta 16 pares solapados y 144,0 ha de intersección acumulada. v4.1 recorta 13 polígonos en dibujo, 143,95 ha, sin reasignar datos. Es una solución gráfica válida para QA, no un cierre metodológico.

## 11. Alternativas evaluadas

- HDBSCAN sin KMeans: prioridad alta.
- HDBSCAN eom/leaf comparado: prioridad alta para redes.
- KDE: control de densidad y comunicación.
- Grafos/comunidades: prioridad alta para redes multinucleares y corredores.
- Ejes con buffer: prioridad alta para Corrientes, Puerto y Caseros.
- OPTICS: diagnóstico puntual; en la prueba produjo 48-93 % de ruido según zona/configuración y no mejora de forma general.
- Alpha shapes: no priorizar; concave hull nativo cubre la necesidad actual.
- Red vial: futuro, si hay capa enrutable limpia.
- Heatmap/puntos: salida preferida para señales exploratorias.

## 12. Recomendación metodológica

Conservar HDBSCAN como detector; comparar eom/leaf; medir estabilidad; validar con KDE o grafo; clasificar tipo territorial; aplicar representación específica; documentar decisión humana. KMeans no debe determinar límites.

## 13. Recomendación cartográfica

- Núcleo compacto: contorno KDE o concave hull con buffer, sujeto a gate.
- Corredor lineal: eje y buffer.
- Red multinuclear: multipunto/núcleos separados o multipolígono.
- Frente gastronómico: línea/frente con buffer.
- Zona difusa: heatmap.
- Señal exploratoria: puntos, sin polígono.

## 14. Decisiones humanas pendientes

Diego/DGDGAS debe decidir nombres, fusiones, jerarquía, inclusión en mapa principal, límites aproximados, solapes, tratamiento de unidades Places-dependientes y relación con Fase 25. La matriz específica se encuentra en `MATRIZ_DECISIONES_DIEGO_DGDGAS.md`.

## 15. Pruebas que sí valen la pena

1. Muestra etiquetada de deduplicación.
2. HDBSCAN sin KMeans + KDE en Soho y San Telmo.
3. Corredor sobre callejero local en Corrientes y Puerto Madero.
4. Grafo/comunidades en Belgrano y Villa Crespo.
5. Bootstrap espacial por bloques.
6. Sensibilidad a bordes de macrozona.
7. Piloto comparativo de cuatro tipos territoriales.

## 16. Pruebas que no valen la pena

- Optimizar KMeans para obtener una cantidad deseada de piezas.
- Ejecutar más llamadas Places antes de resolver método.
- Elegir por Silhouette.
- Implementar ST-DBSCAN sin historia temporal válida.
- Incorporar alpha shapes masivamente.
- Convertir Voronoi o tiles en límites.

## 17. Plan recomendado antes del nuevo informe

Primero resolver deduplicación, KMeans, solapes, nombres y gates de dependencia Places. Después ejecutar cuatro prototipos: núcleo, corredor, red y señal. Sólo entonces seleccionar unidades del mapa principal y producir el nuevo informe.

## 18. Qué se puede reutilizar sin cambios

- Universo sanitizado como insumo experimental versionado.
- Separación de fuentes y IDs.
- Controles de asignación única.
- HDBSCAN como detector inicial.
- Capas de puntos para QA.
- Trazabilidad 163/55/41/31.
- Diseño v4.2 como sistema visual, no como metodología.
- Prudencia narrativa de Fase 25.

## 19. Qué debe corregirse

- Retirar KMeans del rol territorial.
- Registrar excepciones/fallbacks con error y versión.
- Independizar reglas editoriales en una tabla aprobable.
- Resolver solapes analíticos y asignaciones.
- Documentar saturación y discrepancia piloto.
- Calibrar deduplicación con verdad manual.
- Cambiar geometría según tipo territorial.

## 20. Qué debe quedar documentado para futuras actualizaciones

Fecha y universo por fuente; reglas y versión de deduplicación; macrozonas y tratamiento de borde; versión de librerías; parámetros y semillas; estabilidad; tipo territorial; método de representación; decisiones humanas; exclusiones; trazabilidad; hashes; límites de publicación.

## Conclusión

El trabajo nuevo no debe descartarse: aporta una base cuantitativa muy superior a Fase 25. Tampoco debe cerrarse tal como está: más de la mitad de los polígonos depende de KMeans y varias zonas dependen mayoritariamente de Places. La salida institucional defendible es híbrida, con menos polígonos, más ejes/núcleos/señales y decisiones humanas explícitas.

