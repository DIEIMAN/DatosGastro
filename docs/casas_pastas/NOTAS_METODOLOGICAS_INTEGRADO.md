# Notas metodológicas — Padrón candidato integrado de casas de pastas (CABA)

Complementa `INFORME_CASAS_PASTAS_INTEGRADO.md`. Describe cómo se construyó el padrón
candidato integrado **sin hacer nuevos requests** a ninguna API.

## Script

`scripts/casas_pastas/google_places_integrar.py` (no toca el pipeline principal).
Clasificador de pastas compartido: `scripts/casas_pastas/google_places_clasificador.py`.

## Insumos

| Fuente | Archivo | Naturaleza |
|---|---|---|
| Google Places (consolidado plus) | `outputs/casas_pastas_google_places/google_places_consolidado_plus_deduplicado.csv` | operativo no oficial |
| Auditoría C con señal | `outputs/casas_pastas_google_places/revision_cobertura_google/revision_C_con_senal_pastas.csv` | marca posibles faltantes |
| OpenStreetMap | `outputs/casas_pastas/osm_casas_pastas_candidatos.csv` | auxiliar abierto |
| AGC / F02 | `outputs/casas_pastas/casas_pastas_maestro.csv` | oficial administrativo estricto |
| Geometrías | `data/raw/geo_comunas.geojson`, `data/raw/geo_barrios.geojson` | GCBA (comuna/barrio + área) |

## Tratamiento de Google en capas

- **Google A (probable)** → entra al padrón como candidato fuerte.
- **Google B** → **no se descarta**; va a revisión manual.
- **Google C con `posible_faltante_buscar`** (de la auditoría) → revisión manual, **no** se
  promueve automáticamente a A. Incluye `food_store/store/manufacturer/noodle_shop` con
  nombre compatible con casa de pastas barrial aunque no diga "pastas".
- **Google C descartado** (restaurantes, trattorias, pasta bars, pizzerías, bares,
  gastronómicos generales) → se mantienen descartados (preservados en `deduplicacion_fuentes.csv`).

## Asignación territorial

Punto-en-polígono con `shapely` contra las geometrías oficiales GCBA. Para AGC se respeta
la comuna/barrio ya asignada en el maestro; para Google/OSM se asigna por coordenadas.
Áreas en km² tomadas de las propiedades de las geometrías (m² ÷ 1.000.000).

## Deduplicación entre fuentes

Se agrupan registros que refieren al mismo establecimiento usando, en conjunto:

- `place_id` (cuando aplica, solo Google);
- **nombre normalizado** (minúsculas, sin acentos ni puntuación);
- **dirección normalizada** (sin "CABA/Buenos Aires/Argentina");
- **distancia geográfica** (haversine);
- **similitud de nombre** (ratio de secuencias).

Reglas de fusión (heurísticas, conservadoras para no unir independientes distintos):
`dist<40 m y similitud≥0.5`, ó `dist<150 m y similitud≥0.8`, ó `nombre idéntico y dist<250 m`.

Trazabilidad conservada por registro: `fuentes_detectan`, `cantidad_fuentes`,
`fuente_principal`, `confianza_integrada`, `requiere_revision_manual`, `motivo_clasificacion`.

## Clasificación integrada

| Clase | Regla |
|---|---|
| `A_integrado_multifuente` | evidencia A en ≥2 fuentes (mayor confianza). |
| `A_agc_oficial_estricto` | solo AGC. Oficial, pero **no implica local activo**. |
| `A_google_probable` | solo Google A. Candidato operativo no oficial. |
| `A_osm_auxiliar` | solo OSM A. Auxiliar. |
| `B_revision_manual` | Google B, OSM B o C *posible faltante*. **No desaparecen.** |
| `C_descartado` | restaurantes/bares/etc. Se conservan aparte. |

- Aparecer en más de una fuente **sube** la confianza.
- Las casas independientes **no** bajan de prioridad por ser de una sola fuente: son centrales.

## Cadenas vs independientes

`es_cadena_detectada`, `cadena_detectada`, `cantidad_sucursales_cadena`, `tipo_establecimiento`
(`cadena` / `independiente` / `indeterminado`). Se marca **cadena** si el nombre coincide con
una marca conocida o si el nombre normalizado aparece en ≥2 sedes; si aparece una sola vez y
no es marca conocida, **independiente**.

## Privacidad y datos sensibles

- El padrón por establecimiento incluye **nombre comercial / razón social (AGC)** y
  **dirección** → es **sensible** (datos de terceros) y vive en carpeta **gitignored**
  (`outputs/casas_pastas_integrado/`).
- No se exponen CUIT, DNI, emails, teléfonos ni transacciones (verificado: 0 coincidencias).
- Esta documentación y los **agregados** (por comuna/barrio, densidad, resúmenes) **no**
  contienen filas individuales sensibles.

## Reproducibilidad

```bash
python scripts/casas_pastas/google_places_integrar.py
```
No hace requests, no usa API key, no toca `src/`, `data/processed/` ni `data/analytics/`.
