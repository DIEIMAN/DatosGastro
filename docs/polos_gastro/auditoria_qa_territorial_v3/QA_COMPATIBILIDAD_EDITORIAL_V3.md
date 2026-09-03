# QA de compatibilidad editorial V3

## Estado real del contrato

El contrato `CONTRATO_OUTPUTS_CARTOGRAFICOS_PARA_INTEGRACION_V3.md` existe, fue incorporado a la configuración y su SHA-256 coincide con el valor declarado. Estado real: **INCORPORADO Y VIGENTE PARA LA RECEPCIÓN**.

La frase del handoff “al no existir contrato específico” contradice la existencia, ruta y hash citados en el párrafo anterior. Debe reemplazarse por: “El contrato específico fue incorporado; permanecen pendientes los ajustes y entregables indicados por QA”.

## Matriz de cumplimiento

| Requisito | Estado | Evidencia / brecha |
| --- | --- | --- |
| GeoJSON analítico | CUMPLE | Tres capas separadas, válidas, CRS84/EPSG:4326 |
| GeoJSON presentación | CUMPLE_GEOMETRÍA | Tres capas separadas; derivación verificable |
| PNG y SVG | CUMPLE_PARCIAL | 15 pares; faltan versiones institucionales limpias |
| Resolución | CUMPLE | PNG ≈220 dpi; dimensiones registradas |
| Fondo | NO_CUMPLE_DOCUMENTACIÓN | Callejero local visible, pero fuente/condición de uso no declarada por lámina |
| Etiquetas sin códigos | NO_CUMPLE | BEL-A, REC-A y CN-DEC10 visibles; puntos y categorías técnicas visibles |
| Leyenda / tabla de estilos | CUMPLE_PARCIAL | Hay leyendas técnicas; no hay tabla editorial categoría→estilo |
| CRS | CUMPLE | EPSG:4326 / CRS84 declarado |
| Bounding box de render | NO_CUMPLE | Derivable de capas, no entregado como metadata por lámina |
| Métricas | CUMPLE | Lock y métricas consistentes |
| Área del modelo vs. exportada | CUMPLE_PARCIAL | Belgrano 0,3975 km² pre-simplificación vs. 0,385365 km² en GeoJSON; falta rotular la diferencia |
| Cobertura/dependencia | CUMPLE | Valores coincidentes y trazables |
| Nombres post hoc | CUMPLE_PARCIAL | Presentes; Belgrano R no expresa sector secundario |
| Decisiones humanas | CUMPLE | No se reabren; DEC-10 prevalece |
| QA cartográfico | CUMPLE_PARCIAL | Autocontrol existe; QA visual independiente detecta ajustes importantes |
| Hashes/manifest | CUMPLE_PARCIAL | Hashes válidos; dos checksums fuera del manifest |
| Handoff | CUMPLE_PARCIAL | Inventario útil; contradicción sobre el contrato |
| Mapa general | NO_CUMPLE | No fue entregado |

## Lenguaje por superficie

Válido para revisión técnica interna: `EXPERIMENTAL / NO OFICIAL`, “geometría experimental”, “no constituye límite administrativo oficial”, BEL-A, REC-A y CN-DEC10.

Para mapas institucionales: usar “delimitación adoptada”, “definición territorial del estudio”, “Polo Gastronómico …” y “unidad multiparte de cuatro componentes discontinuos” cuando corresponda. Eliminar de la cara visible códigos de modelo, categorías de fuente, puntos individuales, marca DataGastro y advertencias repetidas que debiliten decisiones adoptadas. La limitación metodológica debe permanecer en el texto o pie editorial acordado, no dominar cada lámina.

## Dictamen

La preintegración puede usar las capas como base geométrica, pero no debe insertar los PNG actuales. Requiere una tanda cartográfica/editorial sin recálculo territorial y un nuevo QA independiente.
