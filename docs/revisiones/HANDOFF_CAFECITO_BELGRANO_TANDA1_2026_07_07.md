# Handoff — Cafecito BA en tu barrio · Edición Belgrano · Revisión tanda 1

Fecha: 2026-07-07. Complementa (no reemplaza) el handoff general del 2026-07-02.
Cubre solo la línea Cafecito; PolosGastro, Mercados y Casas de Pastas no se tocaron.

## Qué se hizo

Primera tanda de correcciones editoriales sobre el informe de Cafecito, con la
**Revisión 4** como base (versión vigente; la versión ejecutiva Markdown de
`docs/cafecito/revision_ejecutiva/` sigue pendiente de decisión y no se usó).
El objetivo declarado por Diego: que Cafecito funcione como **plantilla reusable**
para futuros informes de encuestas/eventos (familia visual distinta de la de
informes territoriales como Polos/Mercados).

Archivos nuevos (nada de lo anterior fue modificado ni pisado):

- `scripts/cafecito/generar_informe_cafecito_belgrano_tanda1.py` — generador tanda 1.
- `docs/cafecito/contenido_editable_informe_cafecito_belgrano_tanda1.yaml` — textos.
- `outputs/cafecito/revision_formulario_belgrano_tanda1/` — PDF de revisión
  (`INFORME_CAFECITO_BELGRANO_DGDGAS_REVISION_TANDA1.pdf`, 14 págs.), texto por página,
  PNGs de QA y `QA_REVISION_TANDA1_CAFECITO_BELGRANO.md` (detalle completo de cambios,
  controles y pendientes).

Cambios principales: encabezado institucional arriba en todas las páginas (DGDGAS ·
evento · tipo · fecha 29/6/2026), folio abajo a la derecha, portada con "Edición
Belgrano" + "Datos generales del evento" (79 respuestas, fechas 27–28/6/2026 en
minúscula, sin "Presenta"), pág. 3 metodología en párrafo + distribución solo en %,
pág. 4 "Resumen ejecutivo" (reemplaza "Preguntas del formulario"), subtítulos de
resultados = solo la pregunta entre comillas (sin "Pregunta analizada"/"Qué permite
observar"/"Fuente"), residencia con GBA+PBA unificado y top de barrios solo en %.

QA textual y visual: OK (14/14 páginas revisadas; términos prohibidos ausentes).

## Estado git

Sin commits, sin staging, sin push (decisión de Diego). Todo untracked/modified en la
rama `mercados-gastronomicos-v2`.

## Pendientes para la tanda 2 (decisión humana)

1. Redundancia entre Resumen ejecutivo (pág. 4) y Síntesis (pág. 12): ¿se elimina o
   reconvierte la sección 10?
2. ¿Folio "Pág. 1" también en portada? (hoy la carátula va sin número).
3. Compactar el espacio en blanco de las páginas de un solo gráfico (5, 9, 10).
4. Destino de la versión ejecutiva Markdown de Cafecito (sigue abierta del handoff
   anterior).
5. Extraer el "motor" de la plantilla (hoy importa helpers de los scripts históricos
   `generar_informe_datagastro_final*.py`) a un módulo compartido para nuevas encuestas.
