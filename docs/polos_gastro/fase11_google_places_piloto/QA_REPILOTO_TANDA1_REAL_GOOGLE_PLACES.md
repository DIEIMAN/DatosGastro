# QA de la corrida real — Re-piloto Tanda 1 (Google Places, Fase 11)

Fecha: 2026-07-02. Documento interno. Registra la **única** corrida real autorizada del re-piloto.

## Ejecución

- Comando ejecutado (una sola vez): `python scripts/polos_gastro/google_places/places_repiloto_fase11.py --execute --confirm-real-api`.
- API ejecutada: **sí** (Places API New, Text Search).
- Consultas reales: **10** (una por local). Hard cap 10 **respetado**.
- Matches: 10. Errores de API: 0. Errores de cuota/billing/permiso: 0. Errores de endpoint: 0.
- API key: reportada solo como "GOOGLE_MAPS_API_KEY (presente)"; **nunca** se imprimió ni guardó.
- Aceptados para mapa automáticamente: 0 (por diseño prudente; se habilitan a mano tras revisión).

## Resultado por local

| id | query usada | nombre Google | rubro | business_status | lat/lon | conf. | rev.man. | acept.mapa | decisión auto | acción |
|---|---|---|---|---|---|---|---|---|---|---|
| LG001 Don Julio | Don Julio Palermo Buenos Aires | Don Julio | restaurant | OPERATIONAL | sí | alta | si | no | aceptar_con_revision | validar y habilitar |
| LG002 La Cabrera | La Cabrera Palermo Buenos Aires | La Cabrera Buenos Aires | barbecue_restaurant | OPERATIONAL | sí | alta | si | no | aceptar_con_revision | validar y habilitar |
| LG003 Niño Gordo | Niño Gordo Palermo Buenos Aires | Niño Gordo | restaurant | OPERATIONAL | sí | media | si | no | aceptar_con_revision | revisar sede/zona |
| LG004 Gran Dabbang | Gran Dabbang Palermo Buenos Aires | Gran Dabbang | restaurant | OPERATIONAL | sí | alta | si | no | aceptar_con_revision | validar y habilitar |
| LG005 Mishiguene | Mishiguene restaurante Palermo Buenos Aires | Mishiguene | fine_dining_restaurant | OPERATIONAL | sí | media | si | no | aceptar_con_revision | revisar sede/zona |
| LG006 Osaka | Osaka restaurante nikkei Palermo Buenos Aires | Osaka | japanese_restaurant | **CLOSED_PERMANENTLY** | sí | media | si | no | aceptar_con_revision | revisar (cerrado) |
| LG007 La Mar | La Mar Palermo Buenos Aires | La Mar | peruvian_restaurant | OPERATIONAL | sí | media | si | no | aceptar_con_revision | revisar sede/zona |
| LG008 Aldo's | Aldo's restaurante Palermo Buenos Aires | Aldos Restaurante | restaurant | **CLOSED_PERMANENTLY** | sí | baja | si | no | revisar_manual | revisar (cerrado) |
| LG009 Cosi Mi Piace | Cosi Mi Piace Palermo Buenos Aires | Cosi Mi Piace | italian_restaurant | OPERATIONAL | sí | media | si | no | aceptar_con_revision | revisar sede/zona |
| LG010 Oporto | Oporto restaurante Palermo Buenos Aires | Oporto Almacén | restaurant | OPERATIONAL | sí | media | si | no | aceptar_con_revision | revisar zona (Colegiales) |

(lat/lon están en el interno y en la revisión visual; se omiten aquí para no repetir coordenadas.)

## Revisión de los casos críticos

- **Osaka**: Google devolvió **"Osaka" (japanese_restaurant)**, NO "Osaki". La query específica
  ("restaurante nikkei") funcionó. **Pero** el local aparece como **CLOSED_PERMANENTLY** → no
  publicar como activo; requiere revisión de vigencia.
- **Aldo's**: Google devolvió **"Aldos Restaurante" (restaurant)**, NO "Artemisia". La query
  específica funcionó. **Pero** aparece como **CLOSED_PERMANENTLY** → revisión de vigencia. La
  dirección (Arévalo 2032) es coherente con la zona.
- **Oporto**: Google devolvió **"Oporto Almacén" (restaurant)**, NO "Somos OP" ni rubro no
  gastronómico. **Pero** la dirección (11 de Septiembre 4152, lat -34.541) cae en **Colegiales**,
  no en Palermo Soho/Hollywood → posible sucursal/zona distinta a la esperada; requiere revisión de
  zona antes de aceptar.
- **Niño Gordo**: encoding **correcto** ("Niño Gordo" con ñ) en todos los outputs. Match sólido en
  Palermo (Thames 1810).
- **Fuera de CABA**: ninguno. Las 10 direcciones son de CABA.
- **No gastronómicos**: ninguno. (Nota: el veredicto inicial marcó por error "Cosi Mi Piace" como
  rubro no gastronómico por un bug de subcadena `store`⊂`food_store`; corregido — ver sección
  siguiente.)
- **Cerrados/no operacionales**: **2** (Osaka y Aldo's, CLOSED_PERMANENTLY) → ambos en revisión, no
  publicables como activos.

## Corrección de código post-corrida (sin nueva llamada API)

Tras la corrida se detectó un **bug de clasificación** (no de API ni de datos): el filtro de rubro
usaba coincidencia por subcadena, y `"store"` matcheaba `food_store`/`grocery_store` que Google
añade a restaurantes legítimos. Eso marcó "Cosi Mi Piace" (italian_restaurant, OPERATIONAL) como
"rubro no gastronomico".

Corrección mínima aplicada en `places_repiloto_fase11.py`:
- `_rubro_no_gastronomico` ahora hace match por **token exacto** (separado por `|`), no subcadena.
- Se quitó `"store"` del set no gastronómico y se agregó un set de tokens **gastronómicos**: si el
  resultado tiene evidencia gastronómica (`restaurant`, `cafe`, etc.), no se rechaza por rubro.

La clasificación se **reprocesó desde el interno ya guardado** (sin ninguna llamada nueva a la API);
el dato crudo de Google se preservó intacto. Resultado: Cosi Mi Piace pasó a `media /
aceptar_con_revision`. **No se ejecutó API por segunda vez.**

## Verificación de outputs

- **Interno** (`resultados_repiloto_tanda1_interno.csv`): contiene `google_place_id_interno`,
  `rating_interno`, `user_ratings_total_interno` y `direccion_google` (correcto; es el archivo
  técnico).
- **Revisión visual** (`resultados_repiloto_tanda1_revision_visual.csv`): trae **lat/lon en las 10
  filas** aunque `aceptado_para_mapa=no`. **No** contiene place_id, rating, user_ratings_total, raw
  JSON, API key, dirección exacta con altura ni nota_interna (verificado: 0 columnas prohibidas).
- **Publicable** (`resultados_repiloto_tanda1_publicable.csv`): **lat/lon vacíos** (todos
  `aceptado_para_mapa=no`), sin place_id, rating, user_ratings_total, raw JSON, API key ni
  nota_interna (verificado: 0 columnas prohibidas).

## Confirmaciones

- Solo se ejecutó el comando autorizado, **una vez**. No tanda 2. No 106 locales. No más de 10
  consultas.
- API key no expuesta; `.env` no copiado; no se guardaron keys en outputs; no raw JSON en outputs.
- No PDF/DOCX/mapas finales. No se tocaron datos fuente, Borrador 2/3, Cafecito, Mercados ni Casas
  de Pastas. No se borró nada. No commit/push/staging.
