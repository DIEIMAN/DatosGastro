# QA PDF V4 - PolosGastro DGDGAS

Fecha de control: 3 de julio de 2026.  
PDF revisado: `outputs/polos_gastro/fase16_mapas_editoriales_v4/INFORME_POLOS_GASTRO_DGDGAS_PRELIMINAR_V4.pdf`

## Resultado general

- Estado: apto como V4 editorial para revision visual e institucional.
- Cantidad de paginas: **18**.
- Formato: A4 vertical.
- Marca visible: **DGDGAS - Direccion General de Desarrollo Gastronomico**.
- El PDF visible no contiene "V4" ni "preliminar".
- No se ejecutaron APIs ni llamadas Google Places.
- No se tocaron datos fuente.
- No se hizo commit, push ni staging.

## Mapas y estructura

- [x] Mapa global conservado en pagina 5.
- [x] Paginas 7 a 11 reemplazadas por mapas editoriales de subzonas.
- [x] Palermo / Las Canitas: subzonas coloreadas para Palermo Soho, Palermo Hollywood, Las Canitas y areas contextuales.
- [x] Puerto Madero: docks, eje costero, area Faena / El Mercado, sector costero y area a validar.
- [x] San Telmo: entorno Mercado, casco historico / Defensa, area gastronomica cercana e hito colectivo.
- [x] Corrientes / Abasto: eje Corrientes y area Abasto diferenciados.
- [x] Belgrano: Barrio Chino, Bajo Belgrano, Belgrano R y Cabildo/Juramento diferenciados.

## QA visual

Se rasterizaron las 18 paginas del PDF en `tmp_pdf_preview/polos_fase16_pdf_v4/` y se genero hoja de contacto en `tmp_pdf_preview/polos_fase16_pdf_v4/contact_sheet.png`.

- [x] Subzonas editoriales visibles.
- [x] Etiquetas grandes y legibles en los cinco mapas de detalle.
- [x] Fondo callejero suave, sin saturacion de calles.
- [x] No hay exceso de puntos: los puntos individuales de locales no son el elemento visual principal.
- [x] Se conserva el enfoque de callejero V3: avenidas y calles principales siguen como referencia urbana.
- [x] Etiquetas de subzonas priorizadas manualmente para evitar solapamientos.
- [x] Las subzonas contextuales pueden quedar coloreadas sin etiqueta visible cuando la etiqueta no aporta.
- [x] Los nombres de locales se mantienen en cajas laterales, fuera del mapa.
- [x] Menciones destacadas conservadas en cajas laterales.
- [x] Corrientes y Abasto diferenciados como ejes vinculados, no como mismo polo.
- [x] Abasto marcado como area a reforzar.
- [x] Belgrano R marcado como subzona a reforzar.
- [x] No se presentan poligonos como limites oficiales.
- [x] Notas de cautela visibles en paginas de detalle.
- [x] Pie institucional consistente.

Observacion visual: luego de la aclaracion de criterio, se ajustaron etiquetas con prioridad manual, se redujeron nombres dentro del mapa y se conservaron solo referencias viales principales. Palermo queda con Las Canitas, Palermo Hollywood y Palermo Soho como etiquetas principales; las areas contextuales se leen por color sin forzar rotulos.

## QA editorial y privacidad

Barrido textual sobre el texto extraido del PDF:

- [x] Sin `preliminar`.
- [x] Sin `V4`.
- [x] Sin `prueba`, `borrador`, `revision institucional` ni `documento interno`.
- [x] Sin marca DataGastro como marca publica.
- [x] Sin `place_id`.
- [x] Sin `rating` ni `user_ratings_total`.
- [x] Sin API key.
- [x] Sin raw JSON.
- [x] Sin Google como fuente visible.
- [x] Sin rutas locales visibles.
- [x] Sin nombres de scripts ni CSV internos visibles.

Barrido de privacidad sobre PDF extraido, Markdown base, comparativo, tabla de subzonas y GeoJSON:

- [x] Sin emails.
- [x] Sin telefonos.
- [x] Sin CUIT/CUIL.
- [x] Sin DNI literal.
- [x] Sin `place_id`.
- [x] Sin API keys.
- [x] Sin links privados de Drive/Docs.

Nota: una regex amplia de DNI marco falsos positivos en coordenadas decimales del GeoJSON. Se reejecuto con patron estricto literal de DNI y el resultado fue 0 hits.

## Criterios de inclusion y cautela

- [x] Cerrados o vigencia no confirmada no aparecen como activos.
- [x] Duplicados probables y busquedas a corregir no se presentan como oferta activa.
- [x] Las menciones destacadas se mantienen como referencias del universo semilla, no como ranking.
- [x] Las areas coloreadas son subzonas de trabajo, zonas de lectura o ejes aproximados.
- [x] El PDF no presenta las geometrias como delimitaciones oficiales.

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

- Las subzonas son aproximadas y deben validarse con Ale antes de una version final.
- Abasto queda como area a reforzar; falta decidir si requiere mapa propio.
- Belgrano R queda visible como subzona a reforzar; falta decidir si permanece en la pieza final.
- La paleta y el grado de saturacion de etiquetas pueden ajustarse si se define un destino de circulacion mas formal.
