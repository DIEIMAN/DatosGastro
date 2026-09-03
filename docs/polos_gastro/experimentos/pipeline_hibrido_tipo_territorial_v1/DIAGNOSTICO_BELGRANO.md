# Diagnóstico Belgrano

**Resultado:** mejora metodológica, aún no lista para escalar sin revisión. El umbral de grafo se deriva del percentil 75 de la distancia al quinto vecino (80 m), no de nombres deseados. Produce 6 núcleos separados; HDBSCAN eom produce 5 y leaf 10. Places representa 56.4 %.

Los núcleos se entregan sin nombres. No se afirma automáticamente que correspondan a Barrio Chino, Cabildo/Juramento, Bajo Belgrano o Libertador/Barrancas. Estabilidad media por bloques: 0.39.

**Recomendación:** usar grafo + KDE como insumo y validar nombres/jerarquía humanamente.
