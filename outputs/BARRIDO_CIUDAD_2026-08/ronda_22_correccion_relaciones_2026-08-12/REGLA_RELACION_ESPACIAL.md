# Regla de relación espacial referente–polo

**Estado:** regla editorial reproducible; no modifica geometrías ni asignaciones documentales.

| valor | definición | relaciones |
|---|---|---:|
| `DENTRO` | punto cubierto por la geometría del polo | 138 |
| `BORDE_HASTA_50M` | fuera de geometría, a 50 m o menos | 6 |
| `ENTORNO_51_250M` | fuera, a más de 50 m y hasta 250 m | 22 |
| `CONTEXTUAL_MAS_250M` | fuera y a más de 250 m | 24 |

## Uso editorial

- `DENTRO`: puede presentarse como referente del polo.
- `BORDE_HASTA_50M`: debe nombrarse como referente de borde y acompañarse con la distancia.
- `ENTORNO_51_250M`: debe nombrarse como referente del entorno inmediato, con distancia.
- `CONTEXTUAL_MAS_250M`: no se presenta como referente interno; sólo puede citarse como contexto documental si la ficha explica la relación.

Los umbrales 50/250 m fueron declarados antes de regenerar la maqueta. `SENSIBILIDAD_UMBRAL_RELACIONES.csv` muestra cómo cambia la clasificación entre 50 y 1.000 m; no se ajustaron umbrales para obtener un resultado deseado.
