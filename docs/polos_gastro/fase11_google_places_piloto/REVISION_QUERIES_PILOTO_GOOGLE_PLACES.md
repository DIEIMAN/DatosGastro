# Revisión de queries piloto Google Places — Fase 11

Fecha de generación: 2026-07-02.

## Objetivo

Documentar la selección de 30 locales para el piloto controlado de Google Places y dejar las consultas propuestas verificadas antes de la ejecución.

## Directorio de trabajo

- `outputs/polos_gastro/fase11_google_places_piloto/tablas/locales_semilla_piloto_google_places.csv`

## Criterios de selección

1. Incluir al menos un caso representativo de cada uno de los polos clave:
   - Palermo
   - Puerto Madero
   - San Telmo
   - Recoleta

2. Añadir casos con ambigüedad razonable para validar los criterios de match.
3. Mantener un balance de locales únicos probables y sucursales/hitos colectivos.
4. Incluir casos de otros polos de interés para probar variación territorial.
5. No exceder 30 locales en el piloto.

## Locales seleccionados

Se seleccionaron 30 locales con los siguientes criterios:

- 12 locales del núcleo principal `Palermo`, `Puerto Madero`, `San Telmo`, `Recoleta`.
- 8 locales de otros polos de interés: `Belgrano`, `Villa Crespo`, `Caballito`, `Microcentro y Centro`, `Costanera Norte`, `Avenida Corrientes`.
- 10 locales con ambigüedad marcada (`ambiguedad_si_no = si`) para evaluar la robustez de la consulta y el match.
- 18 locales con ambigüedad mínima (`ambiguedad_si_no = no`) para medir la tasa de éxito en casos claros.

## Queries propuestas

Las `query_google_places_principal` ya están disponibles en la tabla interna de la semilla.

### Ejemplos de queries de la selección

- `Don Julio Palermo Soho; Palermo Hollywood; Las Canitas Palermo Buenos Aires`
- `La Cabrera Palermo Soho; Palermo Hollywood; Las Canitas Palermo Buenos Aires`
- `Nino Gordo Palermo Soho; Palermo Hollywood; Las Canitas Palermo Buenos Aires`
- `La Mar Palermo Soho; Palermo Hollywood; Las Canitas Palermo Buenos Aires`
- `Cabana Las Lilas Puerto Madero Buenos Aires`
- `Chila Puerto Madero Buenos Aires`
- `Sottovoce Puerto Madero Buenos Aires`
- `El Preferido de San Telmo Barrio; Mercado de San Telmo como hito San Telmo Buenos Aires`
- `La Pecora Nera Recoleta Buenos Aires`
- `Hong Kong Style Belgrano Buenos Aires`

## Observaciones de revisión

- Varias queries usan la misma marca con diferenciador de polo/barrio: esto es útil para probar cómo se comporta Google Places en sedes similares.
- Hay hitos colectivos incluidos (`El Mercado / Faena`, `Mercado de San Telmo`, `Patio de los Lecheros`) para validar el tratamiento de lugares con múltiples negocios.
- Las consultas deben revisarse manualmente antes de la ejecución real, especialmente en casos de `sucursal_ambigua`.

## Recomendaciones previas a la ejecución

1. Confirmar que el entorno local tenga la API key sólo si se decide proceder con `--execute`.
2. Ejecutar primero un `dry_run` con `python scripts/polos_gastro/google_places/places_piloto_locales.py` para asegurarse de que las rutas de salida son correctas.
3. Revisar manualmente las 10 consultas ambiguas antes de permitir la ejecución real.
4. Mantener la ejecución real limitada a la selección de 30 locales y no usar `--max-locales` por encima del límite.
5. Si se decide ejecutar, usar `python scripts/polos_gastro/google_places/places_piloto_locales.py --execute`.

## Conclusión

Este documento deja definido el conjunto piloto y las consultas a usar, sin necesidad de ejecutar la API todavía. El siguiente paso es validar la existencia de la API key segura y, si procede, correr la ejecución controlada.
