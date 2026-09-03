# Handoff - Cafecito BA en tu barrio - Edicion Belgrano - Tanda 2

Fecha: 2026-07-07

Este handoff cierra la revision de Cafecito Belgrano Tanda 2. Cubre solo `docs/cafecito/`, `scripts/cafecito/` y `outputs/cafecito/revision_formulario_belgrano_tanda2/`.

## 1. Estado de la tanda 2

Estado: apta para revision humana.

La tanda 2 queda cerrada formalmente con QA textual y visual finalizados. No se reescribio el informe desde cero y no se corrigieron PDFs en esta retomada porque el QA no encontro defectos reales. El problema previo informado sobre `amigos/as` ya no aparece en el PDF publico actual.

## 2. Archivos creados o disponibles

Script:

- `scripts/cafecito/generar_informe_cafecito_belgrano_tanda2.py`

YAML:

- `docs/cafecito/contenido_editable_informe_cafecito_belgrano_tanda2.yaml`

PDFs:

- `outputs/cafecito/revision_formulario_belgrano_tanda2/INFORME_CAFECITO_BELGRANO_DGDGAS_PUBLICO_TANDA2.pdf`
- `outputs/cafecito/revision_formulario_belgrano_tanda2/INFORME_CAFECITO_BELGRANO_DGDGAS_INTERNO_TANDA2.pdf`

Textos extraidos:

- `outputs/cafecito/revision_formulario_belgrano_tanda2/texto_por_pagina_publico.txt`
- `outputs/cafecito/revision_formulario_belgrano_tanda2/texto_por_pagina_interno.txt`

PNGs y grillas de revision:

- `outputs/cafecito/revision_formulario_belgrano_tanda2/qa_png_publico/`
- `outputs/cafecito/revision_formulario_belgrano_tanda2/qa_png_interno/`
- `outputs/cafecito/revision_formulario_belgrano_tanda2/contact_sheet_publico_tanda2.png`
- `outputs/cafecito/revision_formulario_belgrano_tanda2/contact_sheet_interno_tanda2.png`

QA markdown:

- `outputs/cafecito/revision_formulario_belgrano_tanda2/QA_REVISION_TANDA2_CAFECITO_BELGRANO.md`

## 3. Que cambio respecto de tanda 1

- El PDF publico paso de 14 paginas a 11 paginas.
- Las ex paginas 13 y 14 de la tanda 1 se movieron a un PDF interno separado.
- Se creo un PDF interno de 4 paginas con aspectos a considerar, anexo de red de cafeterias vinculadas y notas metodologicas/variables no usadas.
- La pagina 3 publica incorpora grafico de franjas horarias sabado/domingo.
- La variable de aceptacion/recibir informacion quedo fuera del publico y registrada solo como variable excluida en el interno.
- La seccion `Canales de llegada` fue reemplazada por `Canales de informacion`.
- Las preguntas se muestran como pregunta entre comillas mas tipo, sin subtitulos metodologicos visibles.
- Las preguntas de seleccion multiple se muestran como porcentaje sobre total de menciones registradas.
- Los graficos publicos no muestran cantidades absolutas.
- El resumen ejecutivo fue fortalecido y absorbio la ex sintesis de resultados.
- La etiqueta publica de acompanamiento usa `Con amigos`, no `amigos/as`.

## 4. Pendientes sugeridos para tanda 3

- Revisar visualmente el PDF publico con Diego.
- Decidir si el nivel de negritas queda bien o hay que moderarlo.
- Decidir si el informe interno esta bien separado o necesita mas/menos contenido.
- Decidir si la portada publica debe llevar folio o no.
- Decidir si se commitea esta tanda.
- Mas adelante, evaluar si el YAML debe convertirse en configuracion reusable de encuestas o si quedo demasiado parecido a un Word disfrazado.

## 5. Dudas o decisiones humanas pendientes

- Nivel final de negritas en resumen y lecturas.
- Separacion final entre version publica e interna.
- Folio en portada publica.
- Criterio de versionado/commit para cerrar la tanda en Git.
- Posible extraccion futura del motor de plantilla para nuevos informes de encuestas.

## 6. Confirmaciones de cierre

- No se tocaron datos fuente.
- No se toco Rev. 4.
- No se toco tanda 1.
- No se tocaron PolosGastro, Mercados ni Casas de Pastas.
- No hubo push.
- No hubo commits.
- No hubo staging.
- No se uso `git add .`.
- No se uso `git add -A`.

