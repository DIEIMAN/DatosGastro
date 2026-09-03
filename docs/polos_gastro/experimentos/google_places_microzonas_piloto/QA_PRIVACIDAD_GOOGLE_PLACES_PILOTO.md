# QA de privacidad y guardrails — piloto Google Places + microzonas

**Fecha:** 2026-07-09 · Verificado antes y después de la ejecución real (379 consultas
autorizadas por Diego; `interno/` poblado y confirmado gitignoreado con `git check-ignore`).

## Credenciales

| Control | Estado |
|---|---|
| API key hardcodeada en el repo (patrón `AIza…`) | ✅ 0 ocurrencias (grep repo completo) |
| Key solo por entorno/`.env` | ✅ el script solo lee `GOOGLE_MAPS_API_KEY`/`GOOGLE_PLACES_API_KEY` |
| `.env` en `.gitignore` | ✅ verificado con `git check-ignore` |
| Key impresa/logueada/guardada | ✅ nunca; solo se reporta "presente/ausente" |

## Datos de terceros (Google Places)

| Control | Estado |
|---|---|
| Raw JSON guardado | ✅ no se guarda; solo campos del FieldMask mínimo |
| `place_id` en outputs publicables | ✅ no: vive solo en `interno/` (gitignoreado desde 2026-07-09) |
| Dirección exacta en outputs sanitizados | ✅ no se incluye |
| Dataset sanitizado | nombre normalizado, lat/lon, categoría, rating, user_ratings_total, fuente, fecha |
| Scraping | ✅ no: exclusivamente Places API (New) oficial, y todavía sin ejecutar |

Nota: rating y user_ratings_total se incluyen en el dataset sanitizado por pedido
explícito del piloto (2026-07-09); el dataset es **de uso interno DGDGAS y no se
versiona como padrón oficial**. Si algo de esto se publicara, revisar antes el
tratamiento de esos campos (en Fase 11 quedaron como internos).

## Datos personales

- El universo es de **locales comerciales** (F01+F02 públicos + establecimientos de
  Places): no contiene CUIT, DNI, emails, teléfonos, contactos ni transacciones.
- No se exportan filas de personas; los nombres son nombres comerciales.

## Separación de universos y no-oficialidad

- F01+F02 (públicas) y Google Places (externa E) **no se mezclan como un mismo universo**:
  cada punto lleva su columna `fuente` y el QA reporta conteos por fuente.
- Todos los outputs llevan nota EXPERIMENTAL: no son límites oficiales, no miden
  "locales activos" (miden oferta registrada/habilitaciones + prominencia en Places).
- Nada de este piloto toca Fase 25, informes oficiales ni el pipeline F01–F05.

## Git

- Sin commits, sin `git add`, sin push. Único archivo versionable modificado fuera de
  las carpetas nuevas del piloto: `.gitignore` (se agregó la carpeta `interno/`).
