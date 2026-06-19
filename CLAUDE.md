# CLAUDE.md — DataGastro

Instrucciones operativas para Claude Code (y cualquier asistente) en este repositorio.
La documentación completa vive en `docs/skills_claude/`. Este archivo es el resumen que se
carga en cada sesión. **Ante conflicto, ganan los guardrails.**

## Guardrails (Prioridad 0 — permanentes)

1. **Drive es solo lectura.** No borrar/mover/modificar nada en Google Drive. No escribir en
   rutas `G:\My Drive` ni `G:\.shortcut-targets-by-id` (leer/hashear/copiar desde ahí, sí).
2. **No tocar el pipeline sin permiso explícito de Diego:** `src/build_model.py`,
   `src/build_analytics.py`, `data/processed/`, `data/analytics/`, `dashboard/`, `notebooks/`
   ni outputs finales del informe. El pipeline público **F01–F05 queda intacto** hasta aprobación.
3. **Separar universos de fuentes:** públicas (`F01–F05`), internas (`I01–I99`), externas/privadas
   (`E01–E99`). No mezclarlas como un mismo universo.
4. **No inventar datos**, URLs, IDs ni métricas. Respetar `--strict-real`. Los seeds no son datos
   reales.
5. **No convertir habilitaciones en "locales activos".** No decir "locales activos" si la fuente
   mide habilitaciones, oferta registrada, permisos, eventos o registros parciales.
6. **No scraping** de Google Maps, Rappi, PedidosYa, Mercado Libre, Mercado Pago, TripAdvisor,
   TheFork, Instagram, TikTok ni plataformas privadas. Solo APIs oficiales, datos agregados,
   convenios o documentación. No ejecutar llamadas pagas. No guardar credenciales.
7. **No exponer datos personales:** CUIT, DNI, emails, teléfonos, contactos, montos o
   transacciones individuales. Trabajar con agregados, perfiles de columnas, conteos y
   diagnósticos; **no exportar filas individuales sensibles**.
8. **No commitear datos internos/privados.** Todo dato interno/privado va al `.gitignore`. Todo
   output interno sensible va a `outputs/analisis_interno/` o carpeta ignorada por Git.
9. **Confirmar antes de cambios destructivos.** Antes de borrar/mover algo del proyecto local:
   plan de limpieza (seguro/revisar/no borrar) y **esperar confirmación**. No borrar outputs
   finales, scripts ni datos fuente públicos.

## Documentación operativa (leer según la tarea)

- `docs/skills_claude/01_datagastro_guardrails.md` — reglas permanentes (detalle).
- `docs/skills_claude/02_metodologia_fuentes.md` — clasificación y ficha de fuentes.
- `docs/skills_claude/03_privacidad_datos_sensibles.md` — datos sensibles y redacción.
- `docs/skills_claude/04_pipeline_reproducible.md` — trabajar sin romper el pipeline.
- `docs/skills_claude/05_geodatos_y_territorio.md` — geocodificación y sesgos territoriales.
- `docs/skills_claude/06_fuentes_externas_privadas.md` — reglas por plataforma externa.
- `docs/skills_claude/07_informes_ejecutivos.md` — redacción para jefatura.
- `docs/skills_claude/08_limpieza_archivos_locales.md` — borrado seguro local.

## Entorno

- Windows. Shell primaria PowerShell; Bash disponible para POSIX.
- Python en `.venv/`. `pandas` disponible; `openpyxl` **no** está instalado: para leer `.xlsx`
  sin dependencias, usar lectura por `zipfile` + XML (ver `outputs/analisis_interno/.../_*.py`).
- Pipeline (no regenerar salidas sin permiso):
  `python src/build_model.py --strict-real`, `python src/build_analytics.py --strict-real`,
  `python src/validate_model.py --strict-real`, `python -m unittest discover tests`.
