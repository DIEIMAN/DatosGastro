# Prompt para Codex – DataGastro: fuentes externas F07/F08/F09

Quiero ampliar DataGastro sin romper la regla strict-real y sin mezclar universos. Trabajá sobre el repo actual.

Objetivo:
Agregar una arquitectura preparada para nuevas fuentes externas, pero implementando primero sólo lo que sea legal y reproducible.

Alcance inmediato:
1. Crear fuente F07_OSM usando OpenStreetMap/Overpass para CABA.
2. Crear contratos/stubs para F08_GOOGLE_PLACES y F09_CONVENIOS_PRIVADOS, pero sin ejecutar APIs pagas ni scraping.
3. Preparar tablas normalizadas para integrar futuras fuentes privadas de delivery/pagos/POS de forma agregada y con trazabilidad.

Reglas:
- No inventar datos.
- No scrapear Google Maps, Rappi, PedidosYa ni Mercado Pago.
- No simular métricas privadas.
- Todo campo privado debe quedar como contrato/schema, no como dato falso.
- Mantener `--strict-real`.
- Separar claramente:
  a) locales/oferta visible,
  b) habilitaciones oficiales,
  c) actividad económica,
  d) delivery/pedidos,
  e) flujo de personas,
  f) eventos.

Tareas técnicas:
1. Agregar `src/ingest_osm_overpass.py`:
   - Consulta Overpass para CABA con tags gastronómicos: amenity=restaurant/cafe/bar/fast_food/pub/food_court; shop=bakery/deli; cuisine si existe.
   - Guardar raw en `data/raw/F07_osm/`.
   - Exportar processed `data/processed/fact_osm_gastronomia.csv`.
   - Campos mínimos: osm_type, osm_id, name, amenity, shop, cuisine, opening_hours, website, phone, lat, lon, comuna_usig si se puede cruzar, barrio_usig si se puede cruzar, fuente_url, fecha_consulta.
2. Agregar a `source_contracts.py` contrato F07.
3. Agregar tests:
   - no coordenadas fuera de CABA si hay polígono,
   - ids no nulos,
   - fuente y fecha_consulta presentes,
   - categorías normalizadas no vacías.
4. Crear `docs/fuentes_externas_privadas.md`:
   - documentar Google Places, Rappi, PedidosYa, Mercado Pago, POS, reservas.
   - dejar explícito que esas fuentes requieren API oficial/convenio.
5. Crear schemas vacíos:
   - `schemas/f08_google_places_schema.yml`
   - `schemas/f09_delivery_private_aggregate_schema.yml`
   - `schemas/f10_payments_private_aggregate_schema.yml`
   - `schemas/f11_pos_private_aggregate_schema.yml`
6. Actualizar validación:
   - si no existen archivos privados, no debe fallar.
   - si existen, validar que sean agregados y que no contengan email, teléfono personal, DNI, tarjeta, usuario ni datos personales.
7. Ejecutar:
   - `python src/build_model.py --strict-real`
   - `python src/build_analytics.py --strict-real`
   - `python src/validate_model.py --strict-real`
   - `python -m unittest discover tests`

Entregable:
- Resumen de archivos modificados.
- Explicación corta de cómo se integra F07 y cómo quedan preparadas F08-F11.
- No tocar datos existentes salvo lo necesario para registrar nuevas fuentes.
