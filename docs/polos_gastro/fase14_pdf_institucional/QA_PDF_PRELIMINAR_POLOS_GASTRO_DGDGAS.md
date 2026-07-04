# QA PDF preliminar - PolosGastro DGDGAS

Fecha de control: 2026-07-02  
PDF revisado: `outputs/polos_gastro/fase14_pdf_institucional/INFORME_POLOS_GASTRO_DGDGAS_PRELIMINAR.pdf`

## Resultado general

- Estado: **apto como primera version PDF institucional para revision**.
- Cantidad de paginas: **18**.
- Formato: A4 vertical.
- Marca visible: **DGDGAS - Direccion General de Gastronomia**.
- El PDF no usa **DataGastro** como marca publica.
- No se ejecutaron API, llamadas Google Places ni scraping.
- No se tocaron datos fuente.

## Archivos revisados

- PDF institucional generado.
- HTML de vista previa.
- Base editorial Markdown.
- Copias sanitizadas de mapas usadas para el PDF.
- Render PNG de las 18 paginas para QA visual.

## Mapas incluidos en el PDF

1. Mapa global de 22 polos/ejes.
2. Detalle Palermo / Las Canitas.
3. Detalle Puerto Madero.
4. Detalle San Telmo.
5. Detalle Corrientes / Abasto.
6. Detalle Belgrano.

No se incluyo el mapa interno general de puntos de revision como pagina propia. Su contenido queda
representado mediante conteos y lectura de la capa auxiliar, para preservar el caracter publicable
de la pieza.

## QA visual

| Item | Resultado | Observacion |
| --- | --- | --- |
| Portada | OK | Marca DGDGAS, titulo y subtitulo limpios. |
| Indice | OK | Paginas coherentes con estructura final. |
| Mapas | OK con cautela | Insertados como mapas sanitizados, sin rotulos de proceso visibles. |
| Textos fuera de cajas | OK | No se detectaron textos cortados o fuera de contenedor. |
| Solapamientos | OK | No se detectaron solapamientos visuales relevantes. |
| Pies institucionales | OK | Pie consistente en paginas internas. |
| Mapa global | OK | Incluye 22 polos/ejes; se ve como pagina visual principal. |
| Corrientes / Abasto | OK con cautela | Diferenciados; se indica riesgo de doble conteo y necesidad de refuerzo. |
| Belgrano | OK con cautela | Presentado como zona a revisar y fortalecer. |

## QA de marca y contenido visible

- [x] No aparece **DataGastro** como marca publica.
- [x] Marca visible: **DGDGAS - Direccion General de Gastronomia**.
- [x] No aparecen `place_id`, `rating`, `user_ratings_total`.
- [x] No aparecen API keys.
- [x] No aparece raw JSON.
- [x] No aparecen rutas locales.
- [x] No aparecen nombres de scripts.
- [x] No aparecen nombres de CSV internos.
- [x] No aparece QA tecnico dentro del PDF.
- [x] No aparece "prueba", "borrador", "documento interno" ni "revision institucional".
- [x] No aparece "preliminar" en el contenido visible del PDF. Solo figura en el nombre del archivo.

## QA de privacidad

Busqueda textual sobre el PDF extraido:

- Emails: 0.
- Telefonos: 0.
- DNI: 0.
- CUIT/CUIL reales: 0.
- Links privados de Drive/Docs: 0.
- API keys: 0.

Nota: la busqueda literal de `CUIT` puede dar falso positivo si no se usa limite de palabra, porque
la palabra "Circuito" contiene esa secuencia de letras. No hay CUIT real en el PDF.

## Criterios editoriales verificados

- [x] Cerrados no se muestran como activos.
- [x] Queries a corregir no se muestran como activos.
- [x] Duplicados no se muestran como activos.
- [x] Google Places no aparece como fuente oficial ni como validacion definitiva.
- [x] La capa se presenta como **capa auxiliar de geolocalizacion y revision**.
- [x] Abasto y Corrientes estan diferenciados.
- [x] Corrientes se presenta como eje 9 de Julio-Callao.
- [x] Abasto se presenta como area alrededor del shopping, radio aproximado de cinco cuadras.
- [x] Los polos sin locales explicitos siguen integrando el mapa global.
- [x] El tono es institucional, prudente y no tecnico.

## Problemas o cautelas detectadas

- Los mapas de detalle de Corrientes / Abasto y Belgrano son utiles para revision, pero no deberian
  sobredimensionarse en la version final sin validacion adicional.
- La version final convendria regenerar mapas ya sin rotulos de proceso desde origen, para evitar
  depender de recortes sanitizados.
- El mapa interno general de puntos no se incorporo como pagina propia por criterio de publicabilidad.

## Comandos de QA ejecutados

- `pdfinfo` para cantidad de paginas y metadatos basicos.
- `pdftotext` para busqueda textual de terminos prohibidos y privacidad.
- `pdftoppm` para rasterizar todas las paginas.
- Revision visual de hoja de contacto y paginas clave renderizadas.

