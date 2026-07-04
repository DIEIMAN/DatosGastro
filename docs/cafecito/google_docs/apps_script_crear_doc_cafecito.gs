/**
 * Crea un Google Doc editable del informe Cafecito BA en tu barrio a partir
 * del payload JSON. Completar PAYLOAD_JSON_FILE_ID con el ID del archivo JSON
 * subido a Drive.
 */
const PAYLOAD_JSON_FILE_ID = 'PEGAR_ID_DEL_JSON_EN_DRIVE';

const COLORS = {
  ink: '#1f3b57',
  orange: '#c0762b',
  blue: '#2c7fb8',
  grey: '#555555',
  light: '#eef2f6',
  softBlue: '#eaf2f8',
  softOrange: '#fff4e6'
};

function crearInformeCafecitoDesdePayload() {
  const payload = leerPayload_();
  const doc = DocumentApp.create(payload.meta.title + ' - editable');
  const body = doc.getBody();
  body.clear();

  configurarDocumento_(body);
  agregarPortada_(body, payload);
  body.appendPageBreak();
  agregarIndice_(body, payload.index || []);
  body.appendPageBreak();
  (payload.sections || []).forEach((section, index) => {
    agregarSeccion_(body, section);
    if (index < payload.sections.length - 1) body.appendPageBreak();
  });

  const footer = doc.addFooter();
  footer.appendParagraph(payload.meta.footer || 'DGDGAS · Cafecito BA en tu barrio · Resultados de encuestas')
    .setForegroundColor(COLORS.grey)
    .setFontSize(8);

  doc.saveAndClose();
  Logger.log('Documento creado: ' + doc.getUrl());
}

function leerPayload_() {
  const file = DriveApp.getFileById(PAYLOAD_JSON_FILE_ID);
  return JSON.parse(file.getBlob().getDataAsString('UTF-8'));
}

function configurarDocumento_(body) {
  body.setMarginTop(54);
  body.setMarginBottom(54);
  body.setMarginLeft(54);
  body.setMarginRight(54);
  body.setAttributes({
    [DocumentApp.Attribute.FONT_FAMILY]: 'Arial',
    [DocumentApp.Attribute.FONT_SIZE]: 11,
    [DocumentApp.Attribute.FOREGROUND_COLOR]: '#222222'
  });
}

function agregarPortada_(body, payload) {
  agregarTexto_(body, payload.meta.presenta, 12, true, COLORS.orange);
  agregarTexto_(body, payload.meta.title, 28, true, COLORS.ink);
  agregarTexto_(body, payload.meta.subtitle, 14, false, COLORS.grey).setItalic(true);
  body.appendParagraph(payload.cover.intro || '').setSpacingAfter(12);
  agregarTablaSimple_(body, [['Etiqueta', 'Contenido']].concat(payload.cover.facts || []), true);
}

function agregarIndice_(body, entries) {
  agregarTexto_(body, 'Índice', 22, true, COLORS.ink);
  const rows = [['Seccion', 'Titulo', 'Pagina PDF']];
  entries.forEach(e => rows.push([e.num || '', e.texto || '', e.pagina || '']));
  agregarTablaSimple_(body, rows, true);
  body.appendParagraph('Los numeros de pagina corresponden al PDF aprobado; pueden cambiar al editar en Google Docs.')
    .setItalic(true)
    .setForegroundColor(COLORS.grey)
    .setFontSize(9);
}

function agregarSeccion_(body, section) {
  agregarTexto_(body, section.number + '. ' + section.title, 20, true, COLORS.ink);
  if (section.subtitle) agregarTexto_(body, section.subtitle, 12, false, COLORS.grey).setItalic(true);
  (section.blocks || []).forEach(block => agregarBloque_(body, block));
}

function agregarBloque_(body, block) {
  if (block.type === 'paragraph') {
    body.appendParagraph(block.text || '');
  } else if (block.type === 'note') {
    agregarCaja_(body, 'Nota', block.text || '', COLORS.softOrange);
  } else if (block.type === 'reading') {
    agregarCaja_(body, 'Lectura de resultados', block.text || '', COLORS.softBlue);
  } else if (block.type === 'facts') {
    agregarCaja_(body, 'Ficha del relevamiento', '', COLORS.softBlue);
    agregarTablaSimple_(body, [['Etiqueta', 'Contenido']].concat(block.rows || []), true);
  } else if (block.type === 'questions') {
    const rows = [['N', 'Pregunta', 'Tipo', 'Objetivo']];
    (block.items || []).forEach((q, i) => rows.push([String(i + 1), q.pregunta, q.tipo, q.objetivo]));
    agregarTablaSimple_(body, rows, true);
  } else if (block.type === 'question') {
    agregarCaja_(body, block.text || 'Pregunta analizada', [block.kind, block.observes].filter(Boolean).join('\n'), COLORS.softBlue);
  } else if (block.type === 'resultTable') {
    agregarTexto_(body, block.title || 'Resultados', 13, true, COLORS.ink);
    const rows = [[block.multiResponse ? 'Opción' : 'Categoría', block.multiResponse ? 'Menciones' : 'Respuestas', '%']];
    (block.rows || []).forEach(r => rows.push([r.label, String(r.count), r.percent]));
    agregarTablaSimple_(body, rows, true);
    const base = block.multiResponse
      ? 'Base: ' + block.base + ' respuestas. Pregunta multi-respuesta: se muestran menciones por opcion.'
      : 'Base: ' + block.base + ' respuestas.';
    body.appendParagraph(base).setItalic(true).setForegroundColor(COLORS.grey).setFontSize(9);
  } else if (block.type === 'table') {
    if (block.title) agregarTexto_(body, block.title, 13, true, COLORS.ink);
    if (block.intro) body.appendParagraph(block.intro);
    agregarTablaSimple_(body, [block.headers || []].concat(block.rows || []), true);
  } else if (block.type === 'bullets') {
    if (block.title) agregarTexto_(body, block.title, 13, true, COLORS.ink);
    (block.items || []).forEach(item => body.appendListItem(item).setGlyphType(DocumentApp.GlyphType.BULLET));
  } else if (block.type === 'image') {
    agregarImagenOpcional_(body, block);
  }
}

function agregarImagenOpcional_(body, block) {
  agregarTexto_(body, block.title || 'Imagen', 13, true, COLORS.ink);
  const id = block.driveFileId || block.driveFileIdPlaceholder || '';
  if (id && !/^PEGAR_/.test(id)) {
    const blob = DriveApp.getFileById(id).getBlob();
    const image = body.appendImage(blob);
    image.setWidth(520);
  } else {
    body.appendParagraph('Imagen pendiente: subir ' + (block.imageName || block.imagePath || 'archivo') + ' a Drive y completar driveFileId.')
      .setItalic(true)
      .setForegroundColor(COLORS.grey)
      .setFontSize(9);
  }
}

function agregarCaja_(body, title, text, color) {
  const table = body.appendTable([[title], [text || '']]);
  table.setBorderColor(COLORS.blue);
  table.getRow(0).getCell(0).setBackgroundColor(color);
  table.getRow(0).getCell(0).editAsText().setBold(true).setForegroundColor(COLORS.ink);
  table.getRow(1).getCell(0).setBackgroundColor(color);
}

function agregarTablaSimple_(body, rows, header) {
  const table = body.appendTable(rows);
  table.setBorderColor('#d5dce3');
  if (header && table.getNumRows() > 0) {
    const row = table.getRow(0);
    for (let i = 0; i < row.getNumCells(); i++) {
      row.getCell(i).setBackgroundColor(COLORS.ink);
      row.getCell(i).editAsText().setBold(true).setForegroundColor('#ffffff');
    }
  }
  return table;
}

function agregarTexto_(body, text, size, bold, color) {
  const p = body.appendParagraph(text || '');
  p.setFontSize(size);
  p.setBold(!!bold);
  p.setForegroundColor(color || '#222222');
  return p;
}
