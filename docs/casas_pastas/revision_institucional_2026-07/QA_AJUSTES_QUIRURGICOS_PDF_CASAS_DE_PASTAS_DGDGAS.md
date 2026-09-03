# QA - Ajustes quirurgicos PDF Casas de Pastas DGDGAS

Fecha: 2026-07-02.

## Archivos modificados o generados

- Modificado: `scripts/casas_pastas/build_pdf_dgdgas.py`.
- Generado nuevamente: `outputs/casas_de_pastas/INFORME_CASAS_DE_PASTAS_DGDGAS.pdf`.
- Creado: `docs/casas_de_pastas/revision_institucional/QA_AJUSTES_QUIRURGICOS_PDF_CASAS_DE_PASTAS_DGDGAS.md`.

No se modificaron archivos del V4 original, datos fuente, Cafecito, PolosGastro, Mercados, `data/`, `src/`, `dashboard/` ni `notebooks/`.

## Problemas corregidos

- Pagina 5: se separo la zona de nota metodologica breve de la firma institucional.
- Pie institucional: se fijo una posicion consistente para la regla y la firma en todas las paginas.
- Notas inferiores: se normalizo la mayuscula inicial en las notas breves de paginas 6, 7, 11 y 14.
- Se mantuvo la estructura general del informe, las cifras, las conclusiones y las secciones.

## PDF regenerado

- Ruta: `outputs/casas_de_pastas/INFORME_CASAS_DE_PASTAS_DGDGAS.pdf`.
- Paginas: 14.
- Tamano: 761.766 bytes.
- SHA-256: `5C033CA93F035E714973DFB9284CBC517FE449D9319703F39202167E7FBA4F2B`.

## Verificacion visual

Se rasterizaron las 14 paginas del PDF con `pdftoppm` a PNG y se reviso una hoja de contacto completa.

Paginas verificadas con foco especifico:

- Pagina 5: nota en dos lineas, sin solapamiento con el pie institucional.
- Pagina 6: nota inferior con mayuscula inicial, sin solapamiento.
- Pagina 7: nota inferior con mayuscula inicial, sin solapamiento.
- Pagina 11: nota inferior con mayuscula inicial, sin solapamiento.
- Paginas 3 y 14: notas metodologicas breves sin solapamiento evidente.

Resultado: no se observaron solapamientos entre notas inferiores y la firma institucional.

## Verificacion textual

- Marca publica visible: DGDGAS - Direccion General de Desarrollo Gastronomico.
- `DataGastro`: 0 coincidencias en el texto extraido del PDF.
- Etiquetas editoriales no permitidas solicitadas: 0 coincidencias exactas en el texto extraido del PDF.
- Nota pagina 6: `Cantidad absoluta; comparar con la densidad por km² (seccion 4).`
- Nota pagina 7: `Densidad por superficie oficial (GCBA); una etapa posterior puede incorporar poblacion.`
- Nota pagina 11: `Las cadenas se reportan como control de cobertura; no se cuentan categorias genericas como cadenas.`
- Nota pagina 14: `Padrón candidato no oficial · la verificación territorial final queda pendiente.`

## QA de privacidad

Busqueda sobre texto extraido del PDF:

- Emails: 0.
- Telefonos: 0.
- CUIT/DNI: 0.
- `place_id`: 0.
- API keys: 0.
- Links privados de Drive/Docs: 0.

No se tocaron datos fuente ni se incorporaron datos nuevos.

## V4 intacto

Hashes SHA-256 verificados antes y despues de regenerar el PDF DGDGAS:

- `outputs/casas_pastas_reporte/INFORME_CASAS_PASTAS_INTEGRADO_V4.md`: `07AFDDD5FD82C94B6F84A641426E2EFA9E891D11E29F2D20367BEC1C6185FE85`.
- `outputs/casas_pastas_reporte/INFORME_CASAS_PASTAS_INTEGRADO_V4.pdf`: `540C5B893CBBD0D09CC72A5E8F7D20A132AB998F4E64CB27778560687F3B7359`.
- `outputs/casas_pastas_reporte/PACK_REVISION_EXTERNA_254_V4/INFORME_CASAS_PASTAS_INTEGRADO_V4.md`: `07AFDDD5FD82C94B6F84A641426E2EFA9E891D11E29F2D20367BEC1C6185FE85`.
- `outputs/casas_pastas_reporte/PACK_REVISION_EXTERNA_254_V4/INFORME_CASAS_PASTAS_INTEGRADO_V4.pdf`: `50C68F664134C61D721CEE1E08559DF1C0F7973C9F3C43D687179D41A76A9560`.

Resultado: V4 intacto.

## Git y alcance

- No se hizo commit.
- No se hizo push.
- No se ejecuto `git add`.
- Indice git verificado vacio con `git diff --cached --name-only`.
- Se observaron archivos untracked preexistentes en el repo; no se stageo nada.

## Pendientes

Sin problemas pendientes detectados para este ajuste quirurgico.
