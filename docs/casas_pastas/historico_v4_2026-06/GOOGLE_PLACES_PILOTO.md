# Piloto controlado — Google Places API (casas/fábricas de pastas)

Documento operativo del piloto para **validar** el universo de casas/fábricas de pastas en
CABA contra una fuente externa (Google Places API oficial). Es una prueba chica y acotada;
**no reemplaza el informe actual** ni toca el pipeline principal.

## Qué es y qué NO es

- **Es:** un contraste externo, exploratorio, de orden de magnitud, con datos de Google.
- **No es:** un padrón oficial. Google Places **no es** una fuente administrativa.
- Los resultados **no se mezclan** con AGC (registro administrativo oficial, F02) ni con OSM
  (relevamiento abierto auxiliar) **sin aclarar la fuente** de cada uno.

## Guardrails de seguridad (obligatorios)

- La API key se lee **solo** desde la variable de entorno `GOOGLE_MAPS_API_KEY`.
- **Nunca** se imprime, loguea, guarda ni commitea la API key.
- No se escribe en `.env`.
- `--dry-run` es el **modo por defecto**: sin `--run` no se hace ningún request real.
- Topes duros en el script: `--max-queries` ≤ 10 y `--max-results` ≤ 50 (aborta si se exceden).
- Pausa configurable entre requests (`--pause`, default 1.5 s).
- Solo **API oficial** de Places. Nada de scraping de Google Maps ni de plataformas privadas.
- Toda la salida va a `outputs/casas_pastas_google_places/`, que está **gitignored**.

## Cómo correrlo

```bash
# 1) Simulación (no gasta, no llama a la API). Modo por defecto:
python scripts/casas_pastas/google_places_piloto.py

# 2) Ejecución real (requiere la API key en el entorno de TU sesión):
#    PowerShell:  $env:GOOGLE_MAPS_API_KEY = "<tu_api_key>"
python scripts/casas_pastas/google_places_piloto.py --run --max-queries 5 --max-results 50
```

La API key se setea en la sesión del shell, **no** en el repo ni en archivos.

## Parámetros

| Flag | Default | Descripción |
|------|---------|-------------|
| `--run` | (off) | Ejecuta requests reales. Sin esto: dry-run. |
| `--max-queries` | 5 | Máximo de queries (tope duro: 10). |
| `--max-results` | 50 | Máximo de resultados totales (tope duro: 50). |
| `--page-size` | 20 | Resultados por request (1–20). |
| `--pause` | 1.5 | Segundos de pausa entre requests. |

## Endpoint y campos

- **Endpoint:** `https://places.googleapis.com/v1/places:searchText` (Places API New, Text Search).
- **Campos mínimos (primera pasada):** `id`, `displayName`, `formattedAddress`, `location`,
  `businessStatus`, `types`.
- **No** se piden todavía (segunda etapa, mayor costo/complejidad): `rating`, `userRatingCount`,
  `priceLevel`, `regularOpeningHours`, `websiteUri`, `nationalPhoneNumber`, `reviews`.

## Queries del piloto (city-level, sin grilla por comuna)

1. `casa de pastas CABA`
2. `pastas frescas CABA`
3. `fábrica de pastas CABA`
4. `pastificio Buenos Aires`
5. `ravioles CABA`

La grilla completa por comuna (planificada en `outputs/casas_pastas/google_places_plan_casas_pastas.csv`,
carpeta gitignored) **no** se ejecuta en este piloto.

## Clasificación de resultados

Cada candidato se clasifica de forma determinística y conservadora:

- `A_google_probable_casa_pastas` — nombre con término fuerte de pastas (pastificio, ravioles,
  pastas frescas, etc.) y sin señal de gastronómico general.
- `B_google_dudoso` — término ambiguo (posible restaurante italiano) o señales mixtas;
  `requiere_revision_manual = si`.
- `C_google_descartado` — sin término de pastas en el nombre.

## Salidas (todas gitignored)

| Archivo | Contenido |
|---------|-----------|
| `google_places_raw_minimo.json` | Respuesta cruda, solo los campos mínimos pedidos (sin API key). |
| `google_places_candidatos.csv` | Candidatos normalizados y clasificados. |
| `google_places_resumen.csv` | Conteos A/B/C, requests, errores. |
| `piloto_log.txt` | Log de ejecución (sin API key). |

Columnas de `google_places_candidatos.csv`: `place_id`, `nombre`, `direccion`, `lat`, `lon`,
`business_status`, `types`, `query_origen`, `match_casas_pastas`, `confianza`, `motivo`,
`requiere_revision_manual`.

## Costo / riesgo

- Estimación de **orden de magnitud**: con ≤ 5–10 requests de Text Search (tier *Pro* por los
  campos pedidos), el gasto esperado es de **centavos**. El precio por 1000 requests lo fija
  Google y debe **confirmarse contra el pricing vigente** y el crédito gratuito de la cuenta
  antes de cualquier ampliación. *(No es un precio oficial; verificar.)*
- El piloto está topeado por diseño para evitar gasto no controlado.

## Después de ejecutar — qué reportar

1. Cantidad de requests hechas.
2. Cantidad de resultados.
3. Conteo A / B / C.
4. Si hubo errores (y cuáles).
5. Archivos generados.
6. Recomendación: ¿vale la pena ampliar el piloto (más queries / grilla por comuna)?

## Estado

- Script y documentación: versionables (no contienen API key ni datos sensibles).
- Outputs y log: **no** se commitean (gitignored).
- Nada se pushea hasta autorización explícita.
