# Reporte — Piloto Google Places

Fecha de ejecución: 2026-06-29.

Reporte del piloto controlado de Google Places API sobre locales destacados del núcleo
principal. **Experimento aislado, fuera del pipeline.** Autorizado por Diego con tope de 10.

---

## 1. Detección de API key

Se detectó **`GOOGLE_MAPS_API_KEY`** (presente) — leída de entorno/`.env`. **El valor de la key
no se mostró, ni se guardó, ni se logueó** en ningún momento. El script solo reporta el estado
("presente"/"ausente").

## 2. ¿Se ejecutó?

**Sí.** Se corrió primero `dry_run` (sin llamadas) y luego ejecución real:
```
python scripts/polos_gastro/google_places/places_piloto_locales.py --execute --max-locales 10
```

## 3. Requests intentados

**10** (tope respetado; hard cap absoluto = 10). Solo locales del núcleo principal (en el seed,
los 10 primeros corresponden a Palermo).

## 4. Matches

**10 / 10** devolvieron un lugar. Por confianza de coincidencia nombre seed ↔ Google:

| Confianza | Cantidad | Casos |
| --- | --- | --- |
| alta | 6 | Don Julio, Niño Gordo, Gran Dabbang, Mishiguene, La Mar, Cosi Mi Piace |
| media | 1 | La Cabrera (→ "La Cabrera Buenos Aires") |
| baja | 3 | Osaka (→ "Osaki Sushi Palermo"), Aldo's (→ "Artemisia"), Oporto (→ "Alto Palermo Shopping") |

> Los 3 de confianza **baja** son **probables falsos positivos** (la Text Search devolvió el
> lugar más cercano por texto, no necesariamente el local buscado). **Requieren revisión manual**
> antes de cualquier uso. Todos los registros llevan `requiere_revision_manual = si`.

Todos los lugares devueltos figuran como `business_status = OPERATIONAL`.

## 5. Errores

**0.**

## 6. Campos guardados

Por fila: `place_id`, `nombre_google` (displayName), `direccion_google` (formattedAddress),
`tipos_google` (types), `business_status`, `match_confidence` (heurística local),
`fecha_consulta`. FieldMask mínimo usado:
`places.id, places.displayName, places.formattedAddress, places.types, places.businessStatus`.

**No se guardaron**: responses crudas completas, **ni coordenadas (lat/lng)**, ni ningún dato no
necesario. La key nunca se escribió en disco.

Output: `outputs/polos_gastro/experimentos_google_places/locales_places_piloto_resultados.csv`
(+ `locales_places_piloto_queries.csv` con las queries auditables).

## 7. Limitaciones

- **Text Search con `maxResultCount=1`** devuelve el mejor match por texto: puede traer un lugar
  equivocado (ver los 3 de confianza baja).
- `match_confidence` es una heurística simple de comparación de nombres, **no** una validación.
- Solo cubre 10 locales de Palermo (núcleo); no es representativo del universo.
- Sin coordenadas: por diseño, no sirve (ni debe usarse) para mapas del informe.
- Google Maps tiene **sesgo comercial/popularidad**: presencia ≠ relevancia gastronómica
  institucional.

## 8. Advertencia sobre uso experimental

Estos datos son **experimentales**. No constituyen padrón oficial, no validan polos, no se
integran al pipeline y **no deben publicarse en el informe** todavía.

## 9. Recomendación: no usar todavía en informe público

- **No** usar en el informe hasta una revisión manual de los matches (en especial los de
  confianza baja) y una decisión metodológica sobre el rol de Google Places.
- **No** usar las coordenadas/datos Google sobre mapas no-Google sin revisar los Términos de
  Google Maps Platform.

## 10. Impacto sugerido sobre locales destacados

- Permite, tras revisión manual, marcar qué locales destacados del núcleo siguen **operativos** y
  asignarles un `place_id` estable como identificador.
- **No cambia el universo de polos** ni la clasificación. Es validación de *locales*, no de polos.
- Próximo paso sugerido (si se decide continuar): revisar manualmente los 3 casos de baja
  confianza y, si se amplía, mantener el tope bajo y el control de costo.
