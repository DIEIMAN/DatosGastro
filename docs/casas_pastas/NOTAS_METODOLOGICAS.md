# Notas metodológicas — casas/fábricas de pastas

Complemento técnico de `INFORME_CASAS_PASTAS.md`. Bloque independiente; no toca el pipeline
principal (`src/build_model.py`, `src/build_analytics.py`, `data/processed/`, `data/analytics/`,
`dashboard/`, notebooks ni outputs finales del informe DataGastro).

## 1. Pipeline del análisis

Scripts en `scripts/casas_pastas/`:

- `pastas_patterns.py` — clasificador estricto A/B/C (sin dependencias externas).
- `build_casas_pastas.py` — partes 1–7 y 10: inventario, candidatos F01/F02, dedup, maestro,
  geocodificación local, asignación comuna/barrio (geopandas `sjoin`), densidad, evolución,
  figuras.
- `explore_osm_casas_pastas.py` — parte 8: OSM/Overpass, **solo con `--run`**.
- `prepare_google_places_casas_pastas_plan.py` — parte 9: plan Google, **sin llamar API**.

Reproducir:

```bash
python scripts/casas_pastas/build_casas_pastas.py
python scripts/casas_pastas/prepare_google_places_casas_pastas_plan.py
python scripts/casas_pastas/explore_osm_casas_pastas.py --run   # opcional, requiere internet
```

## 2. Criterio de clasificación (A / B / C)

### Patrones estrictos → A
`elaboración de pastas alimenticias frescas/secas`, `elaboración de pastas`, `fábrica de pastas
(alimenticias/frescas)`, `pastas alimenticias`, `casa(s) de pastas`, `pastificio`,
`venta de pastas frescas`, `pastas frescas`, y términos-producto: `ravioles`, `sorrentinos`,
`ñoquis`, `fideos frescos`, `tallarines frescos`.

### Probable → B
Mención de pastas con contexto de producción/venta (fábrica, elaboración, artesanal, casera,
venta) **sin** rubro concluyente; o nombre con "pastas" y rubro genérico, **sin** señal de
restaurante.

### Dudoso/descartado → C
Mención de pasta junto a señales de restaurante/italiano/pizzería/bar/trattoria, o sin señal real
de pasta. Ejemplos reales descartados (OSM): "Il Bruno Pasta & Pizza", "Quotidiano - Bar de
Pasta", "Monti Bar de Pastas".

### Exclusiones (empujan a C salvo match estricto)
`restaurant, trattoria, ristorante, pizza, parrilla, bar, cervecería, café, heladería, panadería,
confitería, cocina italiana, pasta bar, comida italiana, resto`.

## 3. Fuentes y campos de matcheo

- **F02 (raw, por año)**: se evalúan `rubro` + `razon_social` + `comentarios`. El universo real de
  pastas estrictas son los rubros `Elaboración de pastas alimenticias frescas` (108 filas) y
  `secas` (44 filas); más `Farfalla Pastas` (rubro genérico → B). Todas las filas estrictas están
  en el archivo `f02_habilitaciones_aprobadas_2025.csv` (padrón acumulado).
- **F01 (raw, latin-1, `;`)**: se evalúan `nombre` + `categoria` + `cocina`. Solo 1 registro con
  término de pasta ("La Pasta", RESTAURANTE) → C. F01 tiene `lat/long/barrio/comuna` propios.

## 4. Deduplicación (Parte 4)

- Clave de establecimiento = `nombre_normalizado` + `calle_sin_altura`. Esto une variantes de
  altura/esquina (p. ej. "Larrazábal 3543" y "3541" = mismo establecimiento) sin fusionar
  sucursales en calles distintas.
- Campos de trazabilidad de duplicados: `fuentes_que_lo_detectan`, `cantidad_fuentes`,
  `es_duplicado_probable`, `grupo_duplicado`, `confianza_match`, `requiere_revision_manual`,
  `registros_agrupados`.
- 152 filas A (F02) → **10 establecimientos** A.

## 5. Geocodificación (Parte 5)

- F01: usa `lat/long` de la propia fuente (`calidad_geo = f01_fuente`).
- F02: se busca el `domicilio` en la caché local `geo_cache.csv` y `dim_ubicacion.csv`
  (`calidad_geo = cache_*`). **No** se geocodifica con servicios externos pagos.
- Sin match → `sin_geo`; el registro igual cuenta por comuna usando el campo `comuna` del registro
  AGC. Solo entran al `.geojson` los puntos con lat/lon confiable (9 de 10 en A).

## 6. Territorio y densidad (Parte 6)

- Asignación comuna/barrio por punto-en-polígono (`geopandas.sjoin`, `within`) contra
  `geo_comunas.geojson` y `geo_barrios.geojson` (oficiales GCBA).
- `comuna_efectiva` = comuna por geometría; si el punto no está geolocalizado, se usa la `comuna`
  del registro AGC.
- Área km² tomada de las propiedades oficiales (`area` m² en comunas, `area_metro` en barrios).
- Densidad = cantidad / área km². Per cápita (por 10.000 hab) **no** calculado: falta población
  local (columna dejada vacía a propósito).

## 7. OSM (Parte 8) y Google (Parte 9)

- OSM: consulta Overpass por `shop=pasta`, `craft=pasta` y nombres con términos de pastas dentro
  del límite administrativo de CABA. `shop=pasta`/`craft=pasta` se consideran A (tag explícito de
  casa de pastas). Resultado auxiliar, **no** verificado.
- Google: solo se genera un CSV de plan de consultas (text search + grilla por comuna) y la lista
  de campos deseados de Places API (New). **No** se ejecuta API, no se usa API key, no hay
  scraping.

## 8. Reglas respetadas

- No se usó Google Drive ni fuentes internas.
- No se hizo scraping de plataformas privadas.
- No se llamó a APIs pagas; OSM (abierto) solo bajo `--run`.
- No se llamó "locales activos" a las habilitaciones AGC.
- No se tocó el pipeline principal ni sus salidas.
- Universos A y B siempre separados.
