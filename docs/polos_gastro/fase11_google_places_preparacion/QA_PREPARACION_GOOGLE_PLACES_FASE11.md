# QA preparación Google Places — Fase 11

Fecha: 2026-07-02.

## Archivos creados
- outputs/polos_gastro/fase11_google_places_preparacion/tablas/locales_semilla_preparados_para_google_places.csv
- outputs/polos_gastro/fase11_google_places_preparacion/tablas/ambiguedades_locales_google_places.csv
- outputs/polos_gastro/fase11_google_places_preparacion/tablas/polos_para_busqueda_complementaria_fase11.csv
- outputs/polos_gastro/fase11_google_places_preparacion/tablas/schema_resultados_google_places_fase11.csv
- docs/polos_gastro/fase11_google_places_preparacion/CRITERIOS_MATCH_GOOGLE_PLACES_FASE11.md
- docs/polos_gastro/fase11_google_places_preparacion/PLAN_PILOTO_GOOGLE_PLACES_FASE11.md
- docs/polos_gastro/fase11_google_places_preparacion/QA_PREPARACION_GOOGLE_PLACES_FASE11.md

## Tablas creadas
- locales semilla preparados para Google Places
- ambigüedades de locales
- polos para búsqueda complementaria
- esquema de resultados de Google Places

## Conteos
- locales preparados: 106
- casos ambiguos en la tabla: 78
- polos para búsqueda complementaria: 10

## Confirmaciones
- Se ejecutó Google Places: no
- Se usaron API keys: no
- Se tocaron datos fuente: no
- Se tocó Borrador 3: no
- Se tocó Cafecito/Mercados/Casas de Pastas: no
- Se generó PDF/DOCX/mapas: no
- Se hizo commit/push/staging: no

## Riesgos pendientes
- Ambigüedades de sedes y marcas requieren revisión manual antes del piloto.
- Polos sin locales explícitos necesitan investigación complementaria documental.
- El piloto debe limitarse a una muestra pequeña para validar criterios.

## Próximo paso recomendado
- Revisar manualmente primero los casos ambiguos y las sucursales compartidas.
- Validar las consultas de Google Places con un piloto de 20-30 locales.
- Asegurar que ningún place_id ni campos internos se publiquen sin decisión explícita.
