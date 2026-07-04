# Piloto Google Places — locales destacados

Experimento **aislado**. NO forma parte del pipeline principal de DataGastro.
Sirve para diseñar (y, si se autoriza, ejecutar) una validación mínima de locales destacados del
núcleo principal con Google Places API.

Documentación de diseño:
- `docs/polos_gastro/google_places/GOOGLE_PLACES_API_ROADMAP_POLOS_GASTRO.md`
- `docs/polos_gastro/google_places/DISEÑO_EXPERIMENTO_GOOGLE_PLACES.md`

## Cómo funciona

- **Por defecto corre en `dry_run`**: lee hasta 10 locales del núcleo principal
  (Palermo, Puerto Madero, San Telmo, Recoleta) del seed
  `outputs/polos_gastro/locales_destacados_por_polo_seed.csv` y escribe solo las **queries
  propuestas** en `…/experimentos_google_places/locales_places_piloto_queries.csv`
  (y el legacy `locales_places_piloto.csv`). **No hace ninguna llamada a la API.**
- **`--execute`**: ejecución real controlada. Requiere API key por entorno o `.env`
  (`GOOGLE_MAPS_API_KEY` o `GOOGLE_PLACES_API_KEY`). Escribe
  `…/experimentos_google_places/locales_places_piloto_resultados.csv`.
- **Hard cap absoluto de 10 locales** (`MAX_LOCALES_HARD_CAP`); `--max-locales` no puede
  superarlo. FieldMask mínimo. **No** se guardan responses crudas, coordenadas, ni la key.

## Cómo correr dry run

```
python scripts/polos_gastro/google_places/places_piloto_locales.py
```

Genera el CSV de queries propuestas. No requiere API key. No tiene costo.

## Cómo correr ejecución real (si se autoriza)

1. Conseguir una **API key** de Google Maps Platform con **billing y tope de gasto** definidos.
2. Copiar `.env.example` a un `.env` **local** (no commitear) o exportar la variable:
   ```
   export GOOGLE_MAPS_API_KEY="...tu key..."
   ```
3. Revisar los **Términos de Google Maps Platform** (cache, mezcla con otros mapas).
4. Implementar la llamada real (hoy deshabilitada) con **FieldMask mínimo**
   (`places.id, places.displayName, places.formattedAddress, places.types,
   places.businessStatus`) y respetar el tope de 10 locales.
5. Recién entonces ejecutar con `--execute`.

> Tal como está, `--execute` **no** llama a la API: imprime un error explicando los pasos
> previos. Esto es intencional.

## Advertencias de costo

- Places API es **paga**: cada request cuesta. No ejecutar masivamente.
- Un loop mal hecho puede disparar el gasto: respetar `MAX_LOCALES = 10`.

## Advertencias de términos

- No mezclar datos de Places con bases de otros proveedores sin revisar el ToS.
- Cachear solo lo permitido (`place_id` es estable; otros campos tienen límites).
- No guardar responses crudas completas.

## Seguridad de la key

- La key se lee **solo** de `GOOGLE_MAPS_API_KEY` (variable de entorno).
- El script **nunca** imprime ni guarda la key.
- `.env` real → `.gitignore`. Solo se versiona `.env.example` (sin valor).

## Qué NO hace

- No forma parte del pipeline.
- No geocodifica el universo.
- No produce padrón oficial ni mapas.
- No valida polos.
