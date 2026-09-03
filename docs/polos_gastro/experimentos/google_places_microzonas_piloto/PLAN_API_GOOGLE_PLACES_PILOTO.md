# Plan de consultas Google Places — piloto microzonas

**Fecha:** 2026-07-09 · **Estado: EJECUTADO el 2026-07-09 con autorización explícita de
Diego** — 379 consultas reales (dentro del plan y del cap), 0 errores, 3.511 puntos
gastronómicos únicos. El diseño de abajo queda como registro del plan autorizado y como
plantilla para extender a otras macrozonas (siempre con nueva autorización previa).

## Objetivo

Enriquecer el universo F01+F02 en las 4 zonas piloto (6 macrozonas contenedoras de
`macrozonas_editoriales_candidatas_v1`) con oferta gastronómica visible en Google Places,
para contrastar los núcleos detectados solo con fuentes públicas. Places es
**enriquecimiento, nunca fuente principal** (decisión de Diego 2026-07-08).

## Método de consulta

- **Endpoint:** Places API (New) `places:searchNearby` — API oficial, sin scraping.
- **Acotación territorial:** grilla cuadrada de paso 180 m sobre cada macrozona piloto
  (+40 m de borde); cada celda es un círculo de radio 135 m. Ninguna consulta sale de
  las macrozonas piloto.
- **Filtro de rubro en la consulta:** `includedTypes` gastronómicos (restaurant, cafe,
  coffee_shop, bar, bakery, ice_cream_shop, meal_takeaway).
- **FieldMask mínimo:** id, displayName, location, types, primaryType, businessStatus,
  rating, userRatingCount. **No se pide ni guarda nada más.** Sin raw JSON.
- **Máximo 20 resultados por celda** (límite de la API). En zonas densas la celda se
  satura: lo devuelto es lo más prominente, **no un censo**. Limitación documentada.

## Presupuesto y acotación explícita

| Zona piloto | Celdas (= consultas) |
|---|---|
| Corrientes / Microcentro | 158 |
| Palermo Soho / Hollywood | 89 |
| Belgrano | 87 |
| San Telmo | 45 |
| **Total** | **379** |

- **Hard cap absoluto en código: 450 consultas por corrida.** El plan (379) entra.
- **Costo máximo estimado: USD 13,27** (SKU Enterprise por incluir rating:
  USD 35 / 1.000). Desde marzo 2025 cada SKU tiene cuota gratuita mensual (Enterprise
  ~1.000 llamadas): el costo real puede ser USD 0, pero el presupuesto se calcula sin
  asumir esa cuota.
- **Una sola pasada:** el script deduplica por `place_id` entre celdas solapadas, guarda
  progreso cada 25 celdas y es **reanudable sin reconsultar** celdas ya hechas.

## Seguridad y ejecución

- Key solo por entorno/`.env` (ya presente; `.env` en `.gitignore`; verificado que no hay
  keys hardcodeadas en el repo). El script **nunca** imprime, loguea ni guarda la key.
- Dry-run por defecto. Ejecución real solo con `--execute --confirm-real-api`.
- Resultados con `place_id` y campos técnicos → `outputs/.../interno/` (**gitignoreado**).
  Dataset sanitizado sin `place_id` ni dirección → `places/places_sanitizado.csv`.

## Qué falta para ejecutar

1. Autorización explícita de Diego para las 379 consultas (≤ USD 13,27).
2. Correr:
   `.venv/Scripts/python.exe scripts/polos_gastro/experimentos/google_places_microzonas_piloto/preparar_consultas_places_piloto.py --execute --confirm-real-api`
3. Re-correr las etapas 2–4 (universo, clustering, mapas) para incorporar los puntos nuevos.

## Términos de uso (recordatorio)

Revisar ToS de Google Maps Platform antes de mezclar estos puntos con mapas de otros
proveedores en material publicado; cache limitado (place_id es lo único cacheable sin
restricción y acá queda solo en el CSV interno). Uso actual: análisis interno experimental.
