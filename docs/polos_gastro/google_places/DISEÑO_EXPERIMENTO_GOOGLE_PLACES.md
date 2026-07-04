# Diseño de experimento — Google Places (piloto)

Fecha: 2026-06-29.

Diseño técnico del **piloto** de validación de locales con Google Places API. **No se ejecuta.**
Sin API key, sin llamadas reales. Complementa
`GOOGLE_PLACES_API_ROADMAP_POLOS_GASTRO.md`.

---

## Input

`outputs/polos_gastro/locales_destacados_por_polo_seed.csv`

> Nota: este CSV usa el `polo_id` de Fase 1 (p. ej.
> `PG001_PALERMO_SOHO_HOLLYWOOD_Y_LAS_CANITAS`), no los subpolos A/B/C del universo. El piloto
> filtra por nombre de polo del núcleo principal (Palermo, Puerto Madero, San Telmo, Recoleta).

## Output experimental (posible)

`outputs/polos_gastro/experimentos_google_places/locales_places_piloto.csv`

> Carpeta separada de los outputs públicos. En **dry_run** el script genera solo las *queries
> propuestas* (sin datos de Google). En ejecución real (autorizada) agregaría las columnas de
> respuesta.

## Columnas sugeridas

| Columna | Origen | Nota |
| --- | --- | --- |
| `local_id` | seed | Identificador interno del local. |
| `nombre_local` | seed | Nombre transcripto del PDF semilla. |
| `nombre_polo` | seed | Polo asociado. |
| `query_busqueda` | derivada | Texto de búsqueda (p. ej. `"<nombre_local>, <polo>, CABA"`). |
| `place_id` | Google (real) | Vacío en dry_run. Identificador estable. |
| `nombre_google` | Google (real) | `displayName`. Vacío en dry_run. |
| `direccion_google` | Google (real) | `formattedAddress`. Vacío en dry_run. |
| `tipos_google` | Google (real) | `types`. Vacío en dry_run. |
| `business_status` | Google (real) | Operativo/cerrado. Vacío en dry_run. |
| `match_confidence` | derivada | Heurística de coincidencia nombre seed ↔ Google. |
| `requiere_revision_manual` | derivada | `si` por defecto hasta validación humana. |
| `fecha_consulta` | runtime | Fecha de la consulta real (vacía en dry_run). |
| `fuente` | fija | `Google Places API (experimental)`. |
| `observaciones` | libre | Notas (p. ej. "dry_run: sin llamada real"). |

## Reglas

- **Máximo 10 locales** en el piloto (tope duro en el script).
- **Solo núcleo principal** (Palermo, Puerto Madero, San Telmo, Recoleta).
- **Dry run por defecto**: sin `--execute`, no hay llamadas; solo se escriben `query_busqueda`.
- **No guardar API responses completas**: solo los campos del FieldMask mínimo.
- **No guardar datos innecesarios** (evitar coordenadas si no son imprescindibles).
- **No usar en informe público todavía**.
- **No hacer mapas con estos datos todavía**.
- **No geocodificar** el universo a partir de esto.

## Flujo (real, cuando se autorice)

1. Filtrar ≤ 10 locales del núcleo principal.
2. Construir `query_busqueda` por local.
3. (solo con `--execute` + `GOOGLE_MAPS_API_KEY`) llamar Places **Text Search / Place Details**
   con FieldMask mínimo (`id`, `displayName`, `formattedAddress`, `types`, `businessStatus`).
4. Calcular `match_confidence` (comparación de nombres).
5. Escribir el CSV experimental con `fecha_consulta` y `requiere_revision_manual = si`.
6. Revisión manual antes de cualquier uso.

## Qué NO hace el experimento

- No decide si un local sigue siendo "destacado".
- No valida polos.
- No reemplaza Buenos Aires Data.
- No produce padrón oficial.
- No alimenta el pipeline.
