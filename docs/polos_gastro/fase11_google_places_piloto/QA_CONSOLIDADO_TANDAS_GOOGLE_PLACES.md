# QA del consolidado — Tandas Google Places (PolosGastro, Fase 11)

DGDGAS — Dirección General de Gastronomía. Documento interno. Fecha: 2026-07-02.

## Entregables creados

- Anexo consolidado: `ANEXO_CONSOLIDADO_VIGENCIA_Y_GEOLOCALIZACION.md`.
- Tabla consolidada: `outputs/polos_gastro/fase11_google_places_piloto/tablas/consolidado_tandas_google_places.csv`.
- Decisiones humanas acumuladas: `DECISIONES_HUMANAS_ACUMULADAS_GOOGLE_PLACES.md`.
- Este QA.

## Actualización — corrida ampliada incorporada

Tras esta consolidación se ejecutó la **corrida ampliada** (86 restantes) y se integró al
consolidado. Estado actualizado:

- Corridas incluidas: **Tanda 1**, **Tanda 2** y **corrida ampliada**.
- Consultas reales consolidadas: **106** (10 + 10 + 86). Cobertura completa de Fase 11.
- Registros en la tabla consolidada: **106**.
- Distribución: match_fuerte 32 · match_razonable_revisar_sede 27 · zona_sucursal_a_revisar 25 ·
  duplicado_probable 11 · vigencia_no_confirmada 8 · query_a_corregir 3.
- Detalle en `QA_CORRIDA_AMPLIADA_GOOGLE_PLACES.md` y `DECISION_POST_CORRIDA_AMPLIADA.md`.

Las secciones siguientes reflejan el estado previo (20 registros) y se conservan como respaldo del
avance por tandas.

## Alcance consolidado (histórico: primeras 2 tandas)

- Tandas incluidas: **Tanda 1** (re-piloto) y **Tanda 2**.
- Consultas reales consolidadas: **20** (10 + 10).
- Registros en la tabla consolidada: **20**.

## Conteos verificados (desde la tabla consolidada)

| Métrica | Valor |
|---|---|
| match_fuerte | 3 |
| match_razonable_revisar_sede | 9 |
| vigencia_no_confirmada | 5 |
| query_a_corregir | 2 |
| duplicado_probable | 1 |
| **matches razonables/fuertes (fuerte + razonable)** | **12** |
| casos con vigencia no confirmada (cerrados) | 5 (3 permanentes + 2 temporales) |
| query_a_corregir | 2 (Pa' Pastar; Oporto por zona) |
| duplicados probables | 1 (Niño Gordo LG028) |

(Conteos calculados sobre `consolidado_tandas_google_places.csv`; coinciden con los QA por tanda.)

## Confirmaciones

- **No se ejecutó API** en esta consolidación (trabajo 100 % sobre outputs ya existentes).
- No hubo llamadas a Google Places; no se tocó la API key ni el `.env`.
- **No se generó PDF, DOCX ni mapas.**
- **No se tocaron** datos fuente, Borrador 2, Borrador 3, Cafecito, Mercados ni Casas de Pastas.
- **No se borró nada.** La semilla se conserva completa.
- **No commit / push / staging.** No se usó `git add`.
- Marca usada: **DGDGAS — Dirección General de Gastronomía** (no "DataGastro" como marca pública).
- Documentos por tanda conservados como respaldo técnico.

## Casos críticos acumulados (para decisión humana)

- Cerrados (5): Osaka, Aldo's, Morelia (permanentes); Las Pizarras Bistro, Francisca del Fuego
  (temporales).
- Zona/sucursal a revisar: Oporto (Colegiales), cadenas (Café Registrado, Novecento, Kansas,
  SushiClub), La Mar (sede).
- Duplicado probable: Niño Gordo LG028 vs LG003 (misma dirección Thames 1810).
- Query a corregir: Pa' Pastar → "Pastasole".

## Recomendación

Avanzar a **Tanda 3 (Puerto Madero)** con el mismo flujo y doble confirmación; consolidar 30–40
puntos razonables antes de armar mapa; preparar Borrador 4 con esta capa auxiliar y las decisiones
humanas pendientes.
