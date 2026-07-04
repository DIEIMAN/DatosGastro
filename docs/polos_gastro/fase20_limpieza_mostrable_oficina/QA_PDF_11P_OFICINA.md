# QA PDF 11P Oficina

**Proyecto:** PolosGastro — DGDGAS (Dirección General de Desarrollo Gastronómico)  
**Fecha de control:** 3 de julio de 2026  
**PDF revisado:** `outputs/polos_gastro/fase20_limpieza_mostrable_oficina/INFORME_POLOS_GASTRO_DGDGAS_11P_OFICINA.pdf`

## Resultado

- [x] PDF creado.
- [x] PDF tiene 11 páginas reales (`pdfinfo`: `Pages: 11`).
- [x] Tamaño de página A4.
- [x] Índice actualizado a 11 páginas.
- [x] Numeración visible actualizada a `N / 11`.
- [x] No aparecen páginas 12 a 18.

## Controles textuales sobre el PDF

Se extrajo texto con `pdftotext` a:

`outputs/polos_gastro/fase20_limpieza_mostrable_oficina/pdf_text_extract.txt`

No se detectaron apariciones de:

- [x] `Ale`.
- [x] `validar con Ale`.
- [x] `Para validar`.
- [x] `a validar`.
- [x] `requiere validación`.
- [x] `área a reforzar`.
- [x] `subzona a reforzar`.
- [x] `decisiones pendientes`.
- [x] `recomendaciones prudentes`.
- [x] `próximos pasos`.
- [x] `Anexos`.
- [x] `DataGastro`.
- [x] `V5`, `preliminar`, `borrador`, `prueba`, `revisión`, `documento interno`.
- [x] Rutas locales.
- [x] Nombres de scripts.
- [x] Nombres de CSV internos.
- [x] `place_id`.
- [x] `rating`.
- [x] `user_ratings_total`.
- [x] API key.
- [x] raw JSON.
- [x] Google Places visible.

## QA visual

Se rasterizaron las 11 páginas en:

`outputs/polos_gastro/fase20_limpieza_mostrable_oficina/raster_pages/`

Se creó hoja de contacto:

`outputs/polos_gastro/fase20_limpieza_mostrable_oficina/contact_sheet_pdf_pages.png`

Control visual:

- [x] Resumen ejecutivo textual, sin KPIs.
- [x] Cautela metodológica concentrada en página 4.
- [x] Mapas de páginas 7 a 11 revisados visualmente.
- [x] Sin textos fuera de caja.
- [x] Sin superposición grave.
- [x] Sin cajas repetidas de `Nota de cautela`.
- [x] Sin línea repetida de referencia territorial debajo de cada mapa.
- [x] Las subzonas se presentan como lectura orientativa, no como límites oficiales.

## Alcance operativo

- [x] No se ejecutó API.
- [x] No se hicieron llamadas a Google Places.
- [x] No se hizo scraping.
- [x] No se usaron capturas de Google Maps.
- [x] No se tocaron datos fuente.
- [x] No se tocó Cafecito.
- [x] No se tocó Mercados.
- [x] No se tocó Casas de Pastas.
- [x] No se tocó Borrador 2.
- [x] No se tocó Borrador 3.
- [x] Fase19 se usó solo como lectura/base visual.
- [x] No se hizo commit.
- [x] No se hizo push.
- [x] No se hizo staging.
- [x] No se usó `git add .`.

## Archivos principales de salida

- `docs/polos_gastro/fase20_limpieza_mostrable_oficina/INFORME_POLOS_GASTRO_DGDGAS_PDF_BASE_11P_OFICINA.md`
- `outputs/polos_gastro/fase20_limpieza_mostrable_oficina/INFORME_POLOS_GASTRO_DGDGAS_11P_OFICINA.pdf`
- `outputs/polos_gastro/fase20_limpieza_mostrable_oficina/raster_pages/`
- `outputs/polos_gastro/fase20_limpieza_mostrable_oficina/contact_sheet_pdf_pages.png`
