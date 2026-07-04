# QA PDF V3 - PolosGastro DGDGAS

Fecha de control: 3 de julio de 2026.  
PDF revisado: `outputs/polos_gastro/fase15_mapas_callejeros_v3/INFORME_POLOS_GASTRO_DGDGAS_PRELIMINAR_V3.pdf`

## Resultado general

- Estado: apto como V3 mejorado para revision visual e institucional.
- Cantidad de paginas: **18**.
- Formato: A4 vertical.
- Marca visible: **DGDGAS — Direccion General de Gastronomia**.
- No se ejecutaron APIs ni llamadas Google Places.
- No se tocaron datos fuente.
- No se hizo commit, push ni staging.

## Base callejera

- Fuente usada: **Calles / Callejero (GeoJson)** de Buenos Aires Data - GCBA.
- URL dataset: https://data.buenosaires.gob.ar/dataset/calles
- URL de descarga usada: https://cdn.buenosaires.gob.ar/datosabiertos/datasets/jefatura-de-gabinete-de-ministros/calles/callejero.geojson
- Licencia informada por el portal: **CC-BY-2.5-AR**.
- Fecha de actualizacion informada por el portal: **2 de junio de 2026**.
- Fecha de descarga local: **3 de julio de 2026**.
- Archivo local generado: `outputs/polos_gastro/fase15_mapas_callejeros_v3/assets/callejero_gcba_2026_06_02.geojson`.

## Mapas V3 insertados

- [x] Palermo / Las Canitas: `mapa_v3_palermo_las_canitas.png` y `.svg`.
- [x] Puerto Madero: `mapa_v3_puerto_madero.png` y `.svg`.
- [x] San Telmo: `mapa_v3_san_telmo.png` y `.svg`.
- [x] Corrientes / Abasto: `mapa_v3_corrientes_abasto.png` y `.svg`.
- [x] Belgrano y subzonas: `mapa_v3_belgrano_subzonas.png` y `.svg`.

## QA visual

Se rasterizaron las 18 paginas del PDF en `tmp_pdf_preview/polos_fase15_pdf_v3/` y se genero hoja de contacto en `tmp_pdf_preview/polos_fase15_pdf_v3/contact_sheet.png`.

- [x] Mapa global conservado.
- [x] Paginas de detalle 7 a 11 reemplazadas por mapas con callejero GCBA.
- [x] Calles en gris suave y avenidas/ejes principales mas visibles.
- [x] Menciones destacadas visibles en cajas laterales.
- [x] Notas de cautela visibles.
- [x] Corrientes y Abasto diferenciados como ejes vinculados, no mismo polo.
- [x] Belgrano R presentado como subzona a reforzar, no polo consolidado.
- [x] Sin textos fuera de cajas.
- [x] Sin solapamientos criticos en paginas renderizadas.
- [x] Pie institucional consistente con DGDGAS — Direccion General de Gastronomia.

## QA editorial y privacidad

Barrido textual sobre el texto extraido del PDF, la base Markdown V3 y la tabla publica de mapas:

- [x] Sin emails.
- [x] Sin telefonos.
- [x] Sin DNI.
- [x] Sin CUIT/CUIL.
- [x] Sin links privados de Drive/Docs.
- [x] Sin API keys.
- [x] Sin `place_id`.
- [x] Sin `rating` ni `user_ratings_total`.
- [x] Sin raw JSON.
- [x] Sin rutas locales visibles en el PDF.
- [x] Sin nombres de scripts ni CSV internos visibles en el PDF.
- [x] Sin marca DataGastro como marca publica.
- [x] Sin "preliminar", "V3", "prueba", "borrador", "revision institucional" ni "documento interno" dentro del PDF visible.

Nota: una primera regex amplia marco un falso positivo de CUIT por la palabra "Circuito" en el anexo. Se reejecuto con patron literal estricto y el resultado fue 0 hits.

## Criterios de inclusion

- [x] Cerrados o vigencia no confirmada no aparecen como activos.
- [x] Queries a corregir no aparecen como activos.
- [x] Duplicados probables sin resolver no aparecen como activos.
- [x] Google Places no aparece como fuente oficial ni como validacion definitiva.
- [x] La tabla `locales_para_mapas_v3.csv` contiene solo columnas necesarias para mapas y no incluye direcciones exactas, `place_id`, rating, `user_ratings_total` ni raw JSON.

## Alcance de ejecucion

- [x] No API.
- [x] No llamadas Google Places.
- [x] No scraping de plataformas privadas.
- [x] No datos fuente tocados.
- [x] No `data/` modificado.
- [x] No Cafecito tocado.
- [x] No Mercados tocado.
- [x] No Casas de Pastas tocado.
- [x] No Borrador 2 tocado.
- [x] No Borrador 3 tocado.
- [x] No commit / push / staging.

## Limitaciones pendientes

- Los mapas mejoran la lectura territorial, pero no definen limites oficiales.
- Las menciones siguen siendo referencias del universo semilla, no padron operativo.
- Abasto, Belgrano R y sedes a validar requieren revision humana antes de una version final.
- Algunas etiquetas de calle se mantienen reducidas para no saturar la pieza impresa.
