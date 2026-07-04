# QA PDF preliminar V2 - PolosGastro DGDGAS

Fecha de control: julio de 2026  
PDF revisado: `outputs/polos_gastro/fase14_pdf_institucional_revision_visual/INFORME_POLOS_GASTRO_DGDGAS_PRELIMINAR_V2.pdf`

## Resultado general

- Estado: **apto como versión preliminar V2 para revisión visual e institucional**.
- Cantidad de páginas: **18**.
- Formato: A4 vertical.
- Marca visible: **DGDGAS - Dirección General de Desarrollo Gastronómico**.
- No se ejecutaron API, llamadas Google Places ni scraping.
- No se tocaron datos fuente.
- No se hizo commit, push ni staging.

## Archivos revisados

- PDF V2 generado.
- Markdown base de revisión visual.
- Tabla de menciones destacadas por polo/subzona.
- Assets cartográficos V2.
- HTML de vista previa.
- Render PNG de las 18 páginas.
- Hoja de contacto: `tmp_pdf_preview/polos_fase14_pdf_v2/contact_sheet.png`.

## Cantidad de páginas

`pdfinfo` informa **18 páginas**. La estructura queda:

1. Portada.
2. Índice.
3. Resumen ejecutivo.
4. Alcance.
5. Mapa global.
6. Lectura territorial general.
7. Palermo / Las Cañitas.
8. Puerto Madero.
9. San Telmo.
10. Corrientes / Abasto.
11. Belgrano y subzonas.
12. Criterio de menciones.
13. Hallazgos de la capa auxiliar.
14. Decisiones pendientes.
15. Recomendaciones prudentes.
16. Próximos pasos.
17. Anexo de universo semilla.
18. Anexo cartográfico y limitaciones.

## QA visual página por página

| Página | Resultado | Observación |
| --- | --- | --- |
| Portada | OK | Marca DGDGAS, título y fecha sin etiquetas internas visibles. |
| Índice | OK | Estructura y numeración consistentes. |
| Resumen ejecutivo | OK | KPIs legibles y sin sobrecarga visual. |
| Alcance | OK | Cajas claras; tono prudente. |
| Mapa global | OK | Se conserva como mapa principal del universo de 22 polos/ejes. |
| Lectura general | OK | Diferencia polos, ejes y macroáreas. |
| Palermo / Las Cañitas | OK | Página fortalecida; mapa más limpio, puntos grandes y caja de menciones. |
| Puerto Madero | OK con cautela | Mapa integrado; sedes a validar separadas de menciones con mayor respaldo. |
| San Telmo | OK | Mercado tratado como hito colectivo; no como restaurante puntual. |
| Corrientes / Abasto | OK con cautela | Corrientes y Abasto diferenciados; Abasto queda como área a reforzar. |
| Belgrano | OK con cautela | Macroárea no sobredimensionada; subzonas separadas. |
| Criterio de menciones | OK | Explica incluidos, a validar y excluidos sin listar casos críticos en cuerpo. |
| Capa auxiliar | OK | Conteos prudentes; no se presenta como fuente oficial. |
| Decisiones | OK | Pendientes claros. |
| Recomendaciones | OK | Lenguaje institucional y accionable. |
| Próximos pasos | OK | Secuencia clara. |
| Anexos | OK | Tabla y criterio metodológico legibles. |

## Menciones destacadas

La tabla generada contiene:

- **22** menciones incluidas con prudencia.
- **19** menciones o hitos marcados con cautela / a validar.
- **10** candidatos excluidos del PDF visible.

Se agregan cajas por polo/subzona con menciones del universo semilla. No se presentan como ranking ni como padrón oficial.

## Casos excluidos por prudencia

No figuran como destacados visibles:

- Osaka.
- Aldo's.
- Las Pizarras Bistro.
- Francisca del Fuego.
- Morelia.
- Oporto.
- Chila.
- La Reina Kunti.
- Anafe.
- Casa China.

Motivos: vigencia no confirmada, búsqueda a corregir, duplicado probable, sede no resuelta o falta de correspondencia gastronómica suficiente.

## Controles editoriales

- [x] Cerrados no figuran como destacados visibles.
- [x] Vigencia no confirmada no figura como actividad activa.
- [x] Queries a corregir no figuran como destacados visibles.
- [x] Duplicados probables no figuran como activos.
- [x] Corrientes y Abasto están diferenciados.
- [x] Belgrano no se sobredimensiona.
- [x] Los hitos colectivos se diferencian de restaurantes puntuales.
- [x] La capa auxiliar no se presenta como fuente oficial ni validación definitiva.
- [x] El tono es institucional, no experimental.

## QA de privacidad y contenido sensible

Resultado del barrido textual sobre PDF extraído, Markdown base, HTML preview y CSV de menciones:

- Emails: 0.
- Teléfonos: 0.
- DNI: 0.
- CUIT/CUIL: 0.
- Links privados de Drive/Docs: 0.
- API keys: 0.
- `place_id`: 0.
- `rating` / `user_ratings_total`: 0.
- Raw JSON: 0.
- Rutas locales: 0.
- Marca interna DataGastro: 0.

## QA de términos prohibidos en PDF visible

La extracción textual del PDF no arroja hits para:

- `preliminar`.
- `borrador`.
- `prueba`.
- `documento interno`.
- `revision institucional` / `revisión institucional`.
- `DataGastro`.
- `place_id`.
- `rating`.
- `user_ratings_total`.
- `API key`.
- `raw JSON`.
- rutas locales.
- nombres de scripts o CSV internos.
- Google Places / Google.

La palabra **PRELIMINAR** solo queda en el nombre del archivo, no en el contenido visible del PDF.

## Comandos de QA ejecutados

- `python -m py_compile scripts\polos_gastro\build_pdf_institucional_fase14_revision_visual.py`
- `python scripts\polos_gastro\build_pdf_institucional_fase14_revision_visual.py`
- `pdfinfo outputs\polos_gastro\fase14_pdf_institucional_revision_visual\INFORME_POLOS_GASTRO_DGDGAS_PRELIMINAR_V2.pdf`
- `pdftotext ...`
- `pdftoppm -png -r 130 ...`
- Revisión visual de hoja de contacto y páginas clave renderizadas.

## Cautelas pendientes

- Corrientes / Abasto mejora visualmente, pero Abasto sigue requiriendo refuerzo documental.
- Belgrano mejora como macroárea, pero Barrio Chino, Bajo Belgrano y Belgrano R todavía requieren validación diferenciada.
- Puerto Madero conserva menciones a validar por sede/zona antes de una versión final.
- Para versión final conviene cerrar criterios humanos con Ale y, si se aprueba, regenerar cartografía final con una base cartográfica institucional.
