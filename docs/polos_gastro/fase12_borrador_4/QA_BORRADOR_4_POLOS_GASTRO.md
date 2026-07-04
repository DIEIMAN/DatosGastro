# QA — Borrador 4 PolosGastro

DGDGAS — Dirección General de Gastronomía. Documento interno. Fecha: 2026-07-02.

## Entregables creados

- `docs/polos_gastro/fase12_borrador_4/INFORME_POLOS_GASTRO_BORRADOR_4.md` (10 secciones + anexos).
- `docs/polos_gastro/fase12_borrador_4/RESUMEN_EJECUTIVO_POLOS_GASTRO_BORRADOR_4.md` (~1 página).
- `docs/polos_gastro/fase12_borrador_4/NOTAS_REVISION_HUMANA_BORRADOR_4.md`.
- `outputs/polos_gastro/fase12_borrador_4/tablas/tabla_polos_borrador_4.csv` (22 polos).
- `outputs/polos_gastro/fase12_borrador_4/tablas/casos_criticos_borrador_4.csv` (51 casos).
- Este QA.

## Fuentes usadas

- **Fase 10**: `universo_polos_semilla_fase10.csv` (22 polos, lectura territorial).
- **Fase 11**: `consolidado_tandas_google_places.csv` (106 registros) y documentos consolidados
  (anexo de vigencia, decisiones acumuladas, decisión post corrida ampliada).

## Consistencia de datos (calculada, no inventada)

- 22 polos en la tabla; **13 con locales explícitos**, **9 sin locales** (marcados explícitamente).
- Suma de locales por polo = **106** (coincide con el consolidado).
- Casos críticos = **51**: 8 vigencia + 3 query + 11 duplicados + 25 zona/sucursal + 3 hitos
  colectivos + 1 eje vinculado (Abasto/Corrientes).
- Matches razonables/fuertes = **59** (coincide con Fase 11).

## Confirmaciones

- **Borrador 4 creado.** Resumen ejecutivo creado. Notas de revisión humana creadas. Dos tablas
  creadas.
- **Se usaron Fase 10 y Fase 11** como fuentes (universo semilla + consolidado).
- **No se ejecutó API** ni hubo llamadas a la capa de geolocalización.
- **No se generó PDF, DOCX ni mapas.**
- **No se tocaron datos fuente**, ni Borrador 2, Borrador 3, Cafecito, Mercados o Casas de Pastas.
- **No se borró nada.** La semilla se conserva completa (22 polos, 106 locales).
- **No se usó "DataGastro"** como marca pública; marca visible: **DGDGAS — Dirección General de
  Gastronomía**.
- Documentos públicos **sin** place_id, rating, user_ratings_total, raw JSON, API key ni rutas
  técnicas (verificado por búsqueda; 0 coincidencias). Tampoco se menciona la plataforma externa
  como validador oficial: se habla de "capa auxiliar de geolocalización".
- **No commit / push / staging.** No se usó `git add`.

## Tono y criterio

- Lenguaje prudente ("podría", "permite observar", "requiere validación", "sería conveniente").
- La capa se presenta como **auxiliar**, no como validación.
- No se presentan cerrados/dudosos como activos; no se propone su inclusión en mapa público.
- No se doble cuenta Abasto/Corrientes ni los duplicados por punto.

## Suficiencia para PDF

El material es suficiente para preparar una pieza institucional **después** de la revisión humana de
los casos críticos (sección 8 del informe y notas de revisión). No antes.
