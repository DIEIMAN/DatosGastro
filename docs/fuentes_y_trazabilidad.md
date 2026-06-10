# Fuentes y trazabilidad

El proyecto separa pagina portal, URL directa de descarga y datos efectivamente disponibles.

## Fuentes principales

| id | fuente | estado V2 |
| --- | --- | --- |
| F01 | Oferta y Establecimientos Gastronomicos | Falta URL directa oficial en `src/config.py` |
| F02 | Habilitaciones Aprobadas AGC | Falta URL directa oficial o lista anual en `src/config.py` |
| F03 | Ferias y Mercados | Falta URL directa oficial en `src/config.py` |

Las URLs portal se conservan en `data/raw/raw_fuentes_relevadas.csv` y en `src/config.py`. No se usan como descarga automatica si no apuntan a un archivo directo.

## Campos de trazabilidad

Las tablas de hechos deben conservar, cuando corresponde:

- `id_fuente`
- `url_fuente`
- `fecha_ultima_actualizacion` o fecha equivalente
- `calidad_dato`
- `requiere_validacion`
- `motivo_validacion`
- `origen_dato`

## Estado de datos

- `datos seed`: datos manuales o muestra inicial.
- `datos reales parciales`: hay al menos una fuente real cargada, pero no cubre todo el universo.
- `datos reales completos`: las fuentes reales esperadas estan cargadas y validadas.
- `datos pendientes de validacion`: no hay evidencia suficiente para clasificar.

## Regla de prioridad

Ante conflicto entre fuentes, priorizar:

1. BA Data / GCBA con recurso directo.
2. Boletin Oficial o normativa oficial.
3. Web oficial GCBA.
4. Camaras sectoriales.
5. Prensa o fuentes privadas, siempre marcadas para validacion.
