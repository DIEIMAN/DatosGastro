# Como usar la version editable en Google Drive

Esta version editable acompana al PDF aprobado de Cafecito BA en tu barrio. Sirve para abrir el informe como Google Docs y recibir comentarios. No reemplaza al YAML ni al generador como fuente de verdad.

## DOCX editable

1. Subir `INFORME_CAFECITO_DGDGAS_REVISION_4_EDITABLE.docx` a Google Drive.
2. Abrir el archivo con Google Docs.
3. Revisar visualmente portada, indice, tablas, imagenes y saltos de pagina.
4. Usar el documento para comentarios y sugerencias de texto.
5. Si hay cambios de redaccion aprobados, trasladarlos luego al YAML de revision 4.
6. Si hay cambios de datos, calculos o graficos, corregir el generador correspondiente y volver a producir los outputs.
7. No editar el PDF aprobado a mano.

## Apps Script opcional

1. Subir `cafecito_google_docs_payload_revision_4.json` a Google Drive.
2. Copiar el ID del archivo JSON desde la URL de Drive.
3. Abrir Apps Script y pegar el contenido de `apps_script_crear_doc_cafecito.gs`.
4. Reemplazar `PEGAR_ID_DEL_JSON_EN_DRIVE` por el ID del JSON.
5. Ejecutar `crearInformeCafecitoDesdePayload`.
6. Si se quieren insertar imagenes desde Apps Script, subir los PNG de `assets/` a Drive.
7. Completar en el JSON los campos `driveFileId` o reemplazar los placeholders de cada imagen.
8. Volver a ejecutar el script para crear un Google Doc nuevo.

## Criterio de uso

- El DOCX prioriza edicion y claridad sobre replica pixel-perfect del PDF.
- Las tablas son editables para facilitar comentarios.
- Los mapas del anexo se incluyen como imagenes.
- La version editable no debe usarse para cambiar datos sin volver al flujo reproducible.
