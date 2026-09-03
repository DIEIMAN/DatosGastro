# Metodología — Tanda 1 Expansión V4

**Estado:** EXPERIMENTAL / NO OFICIAL. **Modo:** REUSE_ONLY.

Se reutilizó el universo sanitizado de 6.461 puntos con corte Places 8–9 de julio de 2026. No se ejecutaron consultas nuevas. Los puntos se asignaron mediante intersección geométrica en EPSG:5347; el campo barrio del CSV no intervino.

Se construyeron universos administrativo (F01/F02), Places y combinado. Los controles incluyeron HDBSCAN, variante conservadora, grafo de proximidad de 250 m, continuidad, envolvente cóncava restringida, ablación por fuente y bootstrap por bloques de 250 m. La evidencia documental se incorporó únicamente post hoc y solo cuando su fuente tenía estado `ABIERTA_Y_LEIDA` en el QA documental.

Limitación central: 330 filas categoría×celda —66 celdas físicas— permanecen sin consultar. Por eso las clasificaciones son recomendaciones técnicas provisionales y no adopciones institucionales.
