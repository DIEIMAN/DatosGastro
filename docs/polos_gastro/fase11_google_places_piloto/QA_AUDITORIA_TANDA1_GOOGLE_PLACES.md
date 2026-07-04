# QA de la auditoría — Tanda 1 Google Places (PolosGastro, Fase 11)

Fecha: 2026-07-02. Cierre de control de la auditoría de la Tanda 1. Documento interno.

## Confirmaciones de seguridad y alcance

- **No se ejecutaron nuevas llamadas a Google Places.** La auditoría fue 100 % por lectura de
  artefactos ya existentes.
- **No se imprimió ninguna API key.** No se leyó su valor.
- **No se copió `.env`** ni se accedió a su contenido.
- **No se modificó `MAX_LOCALES_HARD_CAP`** (sigue en 10).
- **No se guardó ninguna API key en outputs.**
- **No se publicaron** `place_id`, `rating` ni `user_ratings_total` en los CSV creados por esta
  auditoría.
- **No se generó PDF, DOCX ni mapas.**
- **No se tocó Borrador 2, Borrador 3, datos fuente, Cafecito, Mercados ni Casas de Pastas.**
- **No se borró ningún archivo.**
- **No se hizo commit, push ni staging.** No se usó `git add`.
- No se usó "DataGastro" como marca pública en los entregables.

## Archivos revisados

- `scripts/polos_gastro/google_places/places_piloto_locales.py`, `README.md`
- `outputs/polos_gastro/locales_destacados_por_polo_seed.csv` (seed usado por el script)
- `outputs/polos_gastro/fase10_reencuadre_y_locales/tablas/locales_semilla_polos_fase10.csv`
- `outputs/polos_gastro/fase11_google_places_preparacion/tablas/locales_semilla_preparados_para_google_places.csv`
- `outputs/polos_gastro/fase11_google_places_piloto/tablas/locales_semilla_piloto_google_places.csv`
- `outputs/polos_gastro/experimentos_google_places/locales_places_piloto_resultados.csv`,
  `..._queries.csv`, `locales_places_piloto.csv`
- `outputs/polos_gastro/fase11_google_places_piloto/tablas/locales_places_piloto_resultados_interno.csv`
- `.../locales_places_piloto_resultados_sanitizado.csv`
- `docs/polos_gastro/fase11_google_places_piloto/QA_TANDA_1_GOOGLE_PLACES.md`

## Locales auditados

10 (LG001–LG010, todos de Palermo).

## Locales fuera de semilla

**Ninguno.** Los 10 consultados existen en el documento semilla y en la tabla preparada de Fase 11.
"Artemisia" y "Somos OP" **no** son locales incorporados: son nombres devueltos por Google como
matches erróneos para Aldo's y Oporto.

## Nombres corregidos

- "Ni�o Gordo" → "Niño Gordo": corrección de **documentación** (mojibake); el dato ya estaba bien.
- "Artemisia" y "Somos OP": no se renombra la semilla; se descartan como matches erróneos.
- Detalle en `correcciones_nombres_tanda1.csv`.

## Matches aceptados / en revisión / a corregir

- Aceptados para mapa: **0** (todo `aceptado_para_mapa = no`).
- Plausibles en revisión (`aceptar_con_revision`): **7** (Don Julio, La Cabrera, Niño Gordo, Gran
  Dabbang, Mishiguene, La Mar, Cosi Mi Piace).
- A corregir/rechazar: **3** (Osaka→Osaki `corregir_query`; Aldo's→Artemisia `corregir_query`;
  Oporto→Somos OP `rechazar`).

## Queries a corregir

Todas las de la tanda (query cruda con nombre de polo embebido). Se recomienda usar
`query_google_places_principal` de la tabla preparada de Fase 11.

## ¿Se recomienda Tanda 2?

**No** con el esquema actual. Rehacer el piloto con queries corregidas antes de cualquier Tanda 2.
Ver `DECISION_TANDA2_GOOGLE_PLACES.md`.

## Outputs publicables sanitizados

El sanitizado no contiene place_id/rating/user_ratings_total/JSON/key (cumple reglas duras). No es
publicable todavía por los matches erróneos. Ver `QA_OUTPUT_PUBLICABLE_TANDA1.md`.

## Entregables creados por esta auditoría

- `docs/polos_gastro/fase11_google_places_piloto/RECONSTRUCCION_TANDA1_GOOGLE_PLACES.md`
- `outputs/polos_gastro/fase11_google_places_piloto/tablas/auditoria_origen_tanda1.csv`
- `outputs/polos_gastro/fase11_google_places_piloto/tablas/correcciones_nombres_tanda1.csv`
- `outputs/polos_gastro/fase11_google_places_piloto/tablas/auditoria_matches_tanda1.csv`
- `docs/polos_gastro/fase11_google_places_piloto/QA_OUTPUT_PUBLICABLE_TANDA1.md`
- `docs/polos_gastro/fase11_google_places_piloto/DECISION_TANDA2_GOOGLE_PLACES.md`
- `docs/polos_gastro/fase11_google_places_piloto/QA_AUDITORIA_TANDA1_GOOGLE_PLACES.md` (este)
