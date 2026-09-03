# Belgrano · resultados territoriales V3

## Resultado técnico

Se recomienda **BEL-A: unidad macro multiparte con tres centralidades internas**. El umbral de
continuidad de 160 m produce tres componentes con 107, 82 y 23 puntos-candidato. A 120 m aparecen
seis fragmentos; a 250 m todo se fusiona. Por eso no hay respaldo técnico para forzar cuatro
estructuras equivalentes ni para dibujar un hull gigante.

| modelo | universo | puntos_incluidos | cobertura_pct | componentes | superficie_km2 | compacidad | densidad_puntos_km2 | estabilidad | sensibilidad | dependencia_places_pct | puntos_sin_asignar | riesgo_fragmentacion | riesgo_union_artificial |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| BEL-A | 697 | 248 | 35.58 | 3 | 0.3975 | 0.093 | 623.9 | 0.765 | 0.206 | 53.23 | 449 | BAJO | BAJO |
| BEL-B | 697 | 206 | 29.56 | 4 | 0.3257 | 0.116 | 632.4 | 0.719 | 0.206 | 53.4 | 491 | ALTO | MEDIO |
| BEL-C | 697 | 234 | 33.57 | 12 | 0.3723 | 0.061 | 628.5 | 0.765 | 0.206 | 53.42 | 463 | MEDIO | BAJO |

## Interpretación documental post hoc

La centralidad dominante se interpreta como Barrio Chino–Belgrano C–Barrancas–Pasaje Echeverría,
con Bajo Belgrano como nodo interno; Cabildo–Juramento se conserva como eje/centralidad interna.
La tercera señal se asocia prudencialmente con Belgrano R y se clasifica **SECTOR_SECUNDARIO**.
No alcanza respaldo para promoverla a `SUBPOLO_INTERNO`; tampoco queda sin geometría propia.

## Alternativas

- Respaldo: **BEL-C**, red multiparte cruda bajo la misma identidad.
- Descartada: **BEL-B**; escoger cuatro de seis fragmentos a 120 m introduciría arbitrariedad.
