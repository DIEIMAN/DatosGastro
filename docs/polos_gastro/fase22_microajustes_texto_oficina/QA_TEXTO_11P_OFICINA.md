# QA texto 11P oficina - Fase22

**Proyecto:** PolosGastro - DGDGAS  
**Fecha de control:** 3 de julio de 2026  
**PDF controlado:** `outputs/polos_gastro/fase22_microajustes_texto_oficina/INFORME_POLOS_GASTRO_DGDGAS_11P_TEXTO.pdf`

## Resultado

- [x] PDF creado.
- [x] PDF tiene 11 páginas reales (`pdfinfo`: `Pages: 11`).
- [x] Tamaño de página A4.
- [x] Se mantiene la estructura de 11 páginas.
- [x] Se mantiene la sigla `DGDGAS`.
- [x] Aparece `Dirección General de Desarrollo Gastronómico` en la denominación institucional visible.
- [x] No aparece `Dirección General de Gastronomía` en el texto extraído del PDF.

## Controles textuales

Se extrajo texto con Poppler a:

`outputs/polos_gastro/fase22_microajustes_texto_oficina/pdf_text_extract.txt`

Resultados:

- [x] `DGDGAS`: 11 apariciones en el texto extraído.
- [x] `Dirección General de Desarrollo Gastronómico`: 11 apariciones en el texto extraído.
- [x] `Dirección General de Gastronomía`: 0 apariciones en el texto extraído.
- [x] `Otras referencias del universo semilla`: 0 apariciones en el texto extraído.
- [x] `Otras referencias de la zona`: 5 apariciones en el texto extraído.
- [x] `Abasto` no aparece mezclado como local; queda en línea separada como área de lectura.
- [x] `Belgrano R` no aparece mezclado como local; queda en línea separada como subzona de referencia.
- [x] `La Mar` fue controlada y se documentó criterio en `CAMBIOS_FASE21_A_FASE22_TEXTO.md`.
- [x] `La Mar` queda visible solo en Palermo / Las Canitas.
- [x] `el shopping`: 0 apariciones; se uso `Shopping Abasto`.
- [x] `Napoles` sin tilde: 0 apariciones en texto extraído; se usó `Nápoles` en la caja textual.

## Control de terminos no publicables en PDF

- [x] No aparece `Ale`.
- [x] No aparece `validar con Ale`.
- [x] No aparece `a validar`.
- [x] No aparece `DataGastro`.
- [x] No aparece `preliminar`.
- [x] No aparece `borrador`.
- [x] No aparece `prueba`.
- [x] No aparece `revision`.
- [x] No aparece `documento interno`.

## Control basico de privacidad

Sobre la base Markdown y el texto extraído del PDF:

- [x] Sin emails.
- [x] Sin teléfonos.
- [x] Sin CUIT.
- [x] Sin DNI.
- [x] Sin links privados de Drive/Docs.
- [x] Sin API keys.
- [x] Sin `place_id`.

## QA visual

- [x] Se rasterizaron las 11 páginas del PDF nuevo en `outputs/polos_gastro/fase22_microajustes_texto_oficina/raster_pages/`.
- [x] Se generó hoja de contacto en `outputs/polos_gastro/fase22_microajustes_texto_oficina/contact_sheet_pdf_pages.png`.
- [x] La estructura visual general se mantiene.
- [x] No se observaron saltos de pagina, textos fuera de caja ni superposiciones graves en la hoja de contacto.

## Alcance operativo

- [x] No se tocaron mapas.
- [x] No se modificaron assets cartográficos.
- [x] No se ejecutó API.
- [x] No se usó Google Places.
- [x] No se hizo scraping.
- [x] No se tocaron datos fuente.
- [x] No se tocaron otros proyectos.
- [x] No hubo commit.
- [x] No hubo push.
- [x] No hubo staging.
- [x] No se usó `git add .`.

## Archivos de salida

- `docs/polos_gastro/fase22_microajustes_texto_oficina/INFORME_POLOS_GASTRO_DGDGAS_PDF_BASE_11P_TEXTO.md`
- `docs/polos_gastro/fase22_microajustes_texto_oficina/CAMBIOS_FASE21_A_FASE22_TEXTO.md`
- `docs/polos_gastro/fase22_microajustes_texto_oficina/QA_TEXTO_11P_OFICINA.md`
- `outputs/polos_gastro/fase22_microajustes_texto_oficina/INFORME_POLOS_GASTRO_DGDGAS_11P_TEXTO.pdf`
- `outputs/polos_gastro/fase22_microajustes_texto_oficina/pdf_text_extract.txt`
- `outputs/polos_gastro/fase22_microajustes_texto_oficina/raster_pages/`
- `outputs/polos_gastro/fase22_microajustes_texto_oficina/contact_sheet_pdf_pages.png`
