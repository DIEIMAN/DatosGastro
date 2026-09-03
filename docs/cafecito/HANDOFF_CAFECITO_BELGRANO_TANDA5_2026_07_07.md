# Handoff Cafecito Belgrano - Tanda 5

Fecha de creacion: 2026-07-07
Ultima actualizacion: 2026-07-08 (tercera iteracion: tarjetas de pregunta nuevas,
justificados de portada/resumen y paginas 5-6 verticales, pedidos por Diego)

## Veredicto

APTO PARA REVISION HUMANA.

## Entregables

- Script: `scripts/cafecito/generar_informe_cafecito_belgrano_tanda5.py`
- YAML: `docs/cafecito/contenido_editable_informe_cafecito_belgrano_tanda5.yaml`
- PDF publico (9 paginas): `outputs/cafecito/revision_formulario_belgrano_tanda5/INFORME_CAFECITO_BELGRANO_DGDGAS_PUBLICO_TANDA5.pdf`
- PDF interno (4 paginas): `outputs/cafecito/revision_formulario_belgrano_tanda5/INFORME_CAFECITO_BELGRANO_DGDGAS_INTERNO_TANDA5.pdf`
- Texto extraido: `texto_por_pagina_publico.txt` y `texto_por_pagina_interno.txt`
- PNGs QA: `qa_png_publico/` (9) y `qa_png_interno/` (4)
- Contact sheets: `contact_sheet_publico_tanda5.png` y `contact_sheet_interno_tanda5.png`
- QA: `outputs/cafecito/revision_formulario_belgrano_tanda5/QA_REVISION_TANDA5_CAFECITO_BELGRANO.md`

## Iteracion 2026-07-08 tarde (pedidos de Diego)

- Tarjetas de pregunta (pregunta entre comillas + `Tipo:`) con nuevo estilo:
  fondo `SOFT_BLUE`, borde azul claro y barra de acento naranja a la izquierda.
- Portada: `Datos generales` y parrafo final justificados; columnas de
  `Cafeterias adheridas` distribuidas mas anchas.
- Resumen ejecutivo: intro y bullets justificados (respetando negritas).
- Pagina 5 (Perfil) y pagina 6 (Residencia) pasaron de columnas
  izquierda/derecha a disposicion vertical (pregunta+grafico arriba y abajo),
  para reducir el aire en blanco.
- Fix: el justificado palabra por palabra con `va="top"` bajaba las palabras
  con tilde; se corrigio con `va="baseline"` + ascendente medido.
- QA completo re-ejecutado (visual 13 paginas + contact sheets + textual +
  privacidad): OK. El PDF interno no cambio.
- Nota operativa: `pdf_check.py` sin `--outdir` escribe a
  `qa_png_<nombre_del_pdf>/`; usar `--outdir qa_png_publico|qa_png_interno`.

## Iteracion 2026-07-08 manana (cambios respecto de la Tanda 5 del 2026-07-07)

- Margenes laterales mas amplios: de x=0.065/0.935 (Tanda 4 y Tanda 5 inicial) a
  LEFT=0.075/RIGHT=0.925 (~1,37 cm -> ~1,57 cm por lado en A4).
- Portada publica con mas aire en `Datos generales del evento` y en
  `Cafeterias adheridas presentes en el evento`.
- Parrafo metodologico (pagina 3) con justificado real.
- Se elimino la leyenda `Base: n=79` de los graficos (barras apiladas sin leyenda
  de base).
- Se agrego el PDF interno de 4 paginas: portada, A. Aspectos a considerar,
  B. Anexo red de cafeterias vinculadas (mapas), C. Notas metodologicas y
  variables no usadas.
- QA cerrado el 2026-07-08: revision visual de las 13 paginas y de ambos contact
  sheets (regenerados desde los PNGs actuales), QA textual sobre el texto completo
  extraido de ambos PDFs, QA de privacidad. Sin defectos; no hubo que regenerar.

## Cambios de la Tanda 5 respecto de Tanda 4 (iteracion 2026-07-07)

- Se creo una Tanda 5 sin pisar Tanda 4.
- Se eliminaron las cajas tituladas `Sintesis` del PDF publico.
- Se unieron `5.1 Vinculo previo con eventos de la Ciudad` y `5.2 Canales de difusion del evento` en una sola pagina.
- El informe paso de 10 a 9 paginas.
- Se mantuvo el listado de cafeterias adheridas presentes en el evento.
- Se mantuvo el resumen ejecutivo recuperado con opiniones en negrita.
- Se mantuvieron portada, encabezado interior, franjas horarias, residencia, acompanamiento/motivos e intereses.
- Se mantuvo `Locales o cafeterias adheridas` en el grafico de canales con 0%.
- Se ajusto la nota de aclaraciones para evitar un falso hit textual de la cadena prohibida `presenta`.

## Decision visual sobre 5.1 y 5.2

Se mantiene la version compacta en una sola hoja (5.1 arriba, 5.2 abajo): grafico de
canales legible, sin textos pisados, sin notas pegadas a titulos, sin cortes, con
`Locales o cafeterias adheridas` en 0%.

## QA realizado (cierre 2026-07-08)

- `py_compile` del script: OK.
- Generacion de ambos PDFs con `.venv/Scripts/python.exe`: OK.
- Render a PNG con `scripts/qa/pdf_check.py`: OK (9 publico + 4 interno).
- Revision visual pagina por pagina de las 13 paginas: OK.
- Contact sheets de ambos PDFs regenerados y revisados: OK.
- QA textual sobre texto completo (PyMuPDF) de ambos PDFs: sin `Base: n=79`,
  sin `Lectura de resultados`, sin `Sintesis`, sin `DataGastro`, sin encabezados
  duplicados, folios secuenciales correctos, numeracion 1-7 + 4.1/4.2/5.1/5.2/6.1/6.2
  consistente con el indice.
- QA privacidad sobre ambos PDFs: OK.
- No existe `kpis_lock.json` para esta tanda; `validate_kpis.py` no aplica.

## Observaciones para revision humana

- Validar portada y margenes nuevos como definitivos.
- Segmentos angostos sin etiqueta (~1%) en los graficos de genero (p5) y vinculo
  previo (p7): comportamiento heredado de tandas anteriores, categorias bajo el
  umbral de rotulado.
- El interno p4 refiere a `decisiones metodologicas de la revision tanda 4`
  (referencia historica correcta); decidir si se actualiza la redaccion.
- Validar si la formulacion de `Aclaraciones del informe` queda definitiva.

## Alcance

- No se tocaron datos fuente crudos.
- No se tocaron Rev. 4 ni las Tandas 1, 2, 3 o 4.
- No se tocaron PolosGastro, Mercados ni Casas de Pastas.
- No se tocaron `data/`, `src/`, `dashboard/` ni `notebooks/`.
- No hubo push.
- No hubo commits.
- No hubo staging.
- No se uso `git add .`.
- No se uso `git add -A`.
