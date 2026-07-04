# QA de la corrida real — Tanda 2 (Google Places, Fase 11)

Fecha: 2026-07-02. Documento interno. Registra la **única** corrida real autorizada de Tanda 2.

## Ejecución

- Comando (una sola vez): `python scripts/polos_gastro/google_places/places_repiloto_fase11.py --tanda tanda2 --execute --confirm-real-api`.
- API ejecutada: **sí** (Places API New, Text Search).
- Consultas reales: **10**. Hard cap 10 **respetado**.
- Matches: 10. Errores de API: 0. Cuota/billing/permiso/endpoint: sin problemas.
- API key: reportada solo como "GOOGLE_MAPS_API_KEY (presente)"; nunca impresa ni guardada.
- Aceptados para mapa automáticamente: 0 (diseño prudente).
- Outputs en rutas propias de tanda2 (no pisaron Tanda 1).

## Resultado por local

| id | query usada | nombre Google | rubro | business_status | lat/lon | conf. | rev.man. | acept.mapa | decisión auto | acción |
|---|---|---|---|---|---|---|---|---|---|---|
| LG011 Las Pizarras Bistro | Las Pizarras Bistro Palermo Buenos Aires | Las Pizarras bistro | restaurant | **CLOSED_TEMPORARILY** | sí | alta | si | no | revisar_manual | revisar (cerrado temp.) |
| LG012 Pa' Pastar | Pa Pastar Palermo Buenos Aires | Pastasole Argentina – Buenos Aires | italian_restaurant | OPERATIONAL | sí | baja | si | no | revisar_manual | revisar/corregir_query (nombre no coincide) |
| LG013 Café Registrado | Café Registrado Palermo Buenos Aires | Café Registrado | coffee_shop | OPERATIONAL | sí | media | si | no | aceptar_con_revision | revisar sede/zona |
| LG014 Francisca del Fuego | Francisca del Fuego Distrito Arcos Palermo Buenos Aires | Francisca del Fuego | bar_and_grill | **CLOSED_TEMPORARILY** | sí | media | si | no | aceptar_con_revision | revisar (cerrado temp.) |
| LG015 Campo Bravo | Campo Bravo Las Cañitas Buenos Aires | CAMPOBRAVO Las Cañitas | restaurant | OPERATIONAL | sí | baja | si | no | revisar_manual | revisar (variante de nombre) |
| LG016 Novecento | Novecento Las Cañitas Buenos Aires | Novecento Cañitas | argentinian_restaurant | OPERATIONAL | sí | media | si | no | aceptar_con_revision | revisar sede/zona |
| LG017 Morelia | Morelia Las Cañitas Buenos Aires | Morelia | pizza_restaurant | **CLOSED_PERMANENTLY** | sí | media | si | no | aceptar_con_revision | revisar vigencia (cerrado perm.) |
| LG018 Kansas | Kansas Las Cañitas Buenos Aires | Kansas | american_restaurant | OPERATIONAL | sí | media | si | no | aceptar_con_revision | revisar sede/zona |
| LG019 SushiClub | SushiClub Las Cañitas Buenos Aires | SushiClub Las Cañitas | sushi_restaurant | OPERATIONAL | sí | media | si | no | aceptar_con_revision | revisar sede/zona |
| LG028 Niño Gordo (zona límite) | Niño Gordo Villa Crespo Buenos Aires | Niño Gordo | restaurant | OPERATIONAL | sí | media | si | no | aceptar_con_revision | revisar (ver nota) |

## Hallazgos por criterio

- **Resultados cerrados**: **3**. Las Pizarras Bistro (CLOSED_TEMPORARILY), Francisca del Fuego
  (CLOSED_TEMPORARILY), Morelia (CLOSED_PERMANENTLY). Ninguno mapeable como activo hasta validar.
- **Resultados fuera de CABA**: **ninguno**. Las 10 direcciones son de CABA.
- **Sucursales/zona dudosa**: las cadenas (Café Registrado, Novecento, Morelia, Kansas, SushiClub)
  quedaron en `aceptar_con_revision`; zona coherente con Las Cañitas (calle Báez) salvo Café
  Registrado (Medrano/Almagro-límite) y Kansas (Av. Libertador, borde Las Cañitas). Requieren
  confirmar sede.
- **Rubros no gastronómicos**: **ninguno**. Todos gastronómicos (restaurant, coffee_shop,
  italian/argentinian/american/sushi/pizza restaurant, bar_and_grill).
- **Nombre que no coincide (corregir_query)**: **Pa' Pastar** devolvió "Pastasole Argentina"
  (nombre distinto, confidence baja) → probable cierre/renombramiento; corregir_query o marcar sin
  match confiable.
- **Variante de nombre (revisar)**: Campo Bravo→"CAMPOBRAVO", clasificado baja por formato; muy
  probablemente el mismo local (Báez 292, rating alto). Revisión confirmará.

## Nota metodológica — Niño Gordo (LG028)

La query "Niño Gordo Villa Crespo" devolvió la **misma sede de Palermo (Thames 1810)** ya obtenida
en la Tanda 1 (LG003). Esto sugiere que la "zona límite" del documento semilla **no** es una sede
distinta, sino el mismo Niño Gordo de Palermo. La revisión visual marca `barrio_o_zona_inferida =
Villa Crespo` por herencia del polo semilla, pero la dirección real es Palermo. **Decisión humana**:
confirmar si Niño Gordo tiene o no una sede propia en Villa Crespo; si no, LG028 se trata como
duplicado de LG003.

## Verificación de outputs

- **Interno** (`resultados_tanda2_interno.csv`): contiene `google_place_id_interno`,
  `rating_interno`, `user_ratings_total_interno`, `direccion_google` (correcto; archivo técnico).
- **Revisión visual** (`resultados_tanda2_revision_visual.csv`): **lat/lon en las 10 filas** aunque
  `aceptado_para_mapa=no`. Sin place_id, rating, user_ratings_total, raw JSON, API key, dirección
  exacta ni nota_interna (verificado: 0 columnas prohibidas).
- **Publicable** (`resultados_tanda2_publicable.csv`): lat/lon vacíos (todos
  `aceptado_para_mapa=no`), sin campos sensibles (verificado: 0 columnas prohibidas).

## Confirmaciones

- Solo el comando autorizado, una vez. No 106 locales. No más de 10 consultas. Cap intacto.
- API key no expuesta; `.env` no copiado; sin keys ni raw JSON en outputs.
- No PDF/DOCX/mapas. No se tocaron datos fuente, Borrador 2/3, Cafecito, Mercados ni Casas de
  Pastas. No se borró nada. No commit/push/staging.
