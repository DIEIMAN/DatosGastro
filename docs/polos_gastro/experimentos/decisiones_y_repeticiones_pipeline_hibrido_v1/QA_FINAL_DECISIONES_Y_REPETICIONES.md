# QA final — decisiones_y_repeticiones_pipeline_hibrido_v1

Estado: APTO PARA REVISIÓN INTERNA; EXPERIMENTAL / NO OFICIAL. Fecha: 2026-07-10.

## Naturaleza de la tanda

Tanda **de escritorio**: revisión crítica, matrices de decisión y especificaciones de
repetición. No se ejecutó ninguna detección nueva; las repeticiones de Belgrano y
Puerto Madero quedan **diseñadas, no corridas**. Única computación nueva: inventario de
ejes viales de Puerto Madero (lectura local del callejero GCBA ya almacenado) y el
empaquetado (hashes, copias, ZIP).

## Verificaciones

- **APIs / Google Places / descargas:** ninguna llamada, ninguna descarga. El plan de
  consultas Places es documental y no autoriza nada (0 consultas recomendadas como
  EJECUTAR).
- **Datos fuente:** sin modificaciones. Solo lecturas.
- **Fase 25 / Fase 26 / informes oficiales / v1–v4.2 / prototipos híbridos v1:** sin
  cambios. Todo resultado nuevo vive en las tres carpetas nuevas
  `*/decisiones_y_repeticiones_pipeline_hibrido_v1/`.
- **Hashes de insumos críticos v1:** 24 verificados contra el manifest v1; 23 OK; 0
  cambiados; 1 discrepancia **preexistente** documentada:
  `metadata_pipeline_hibrido_v1.json` — el manifest v1 registró una versión de 1.573
  bytes, pero las tres copias actuales (archivo suelto, carpeta del paquete y ZIP v1
  **intacto**) son byte-idénticas entre sí (1.583 bytes,
  `2a453994…33c8f3`). Es una errata del empaquetado v1 (manifest generado antes de la
  última escritura del metadata), no un cambio de esta tanda. Detalle:
  `verificacion_hashes_insumos_v1.csv`.
- **Privacidad:** barrido automático sobre todos los `.md/.csv/.json` del paquete
  (emails, CUIT/DNI, teléfonos, API keys): limpio. Los entregables trabajan solo con
  agregados y conteos; sin filas individuales sensibles.
- **ZIP sin datos internos:** el ZIP contiene únicamente documentos nuevos, tres CSV
  metodológicos y seis mapas PNG copiados sin modificar del v1. La carpeta interna de
  deduplicación (`interno_revision_deduplicacion/`) no se copió ni se referencia con
  contenido.
- **Git:** staging vacío (0 archivos), HEAD sin cambios (`e6d79a9`), sin commits, sin
  push, sin `git add`. Los únicos archivos trackeados modificados
  (`.claude/settings.json`, `.gitignore`) ya estaban modificados al inicio de la
  sesión y no fueron tocados por esta tanda. Todos los archivos nuevos quedan sin
  trackear.
- **Entorno:** `.venv` existente; ninguna librería instalada.

## Limitaciones de esta tanda

- Las recomendaciones técnicas de la matriz DH-01..DH-12 no son vinculantes; ninguna
  decisión queda tomada.
- Las coberturas por opción de Puerto Madero (PM-B..PM-F) y los núcleos estables de
  Belgrano no existen todavía: son el objetivo de las repeticiones diseñadas.
- La discrepancia menor de conteo del v1 (CSV 152 vs. GeoJSON 150 en Belgrano) queda
  señalada y se corrige en la repetición (BEL-R15); no se editó el v1.
- El inventario de ejes de Puerto Madero usa el campo `nomoficial` del callejero GCBA
  local; el recorte (contenedor + 50 m) incluye tramos de borde de ejes vecinos. No
  incluye hidrografía ni geometría de diques (limitación heredada de la capa).
