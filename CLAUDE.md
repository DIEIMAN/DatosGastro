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

## Infraestructura agentes y skills (V1.1, controlada)

Paquete documental (no sustituye `.claude/skills/` productivas hasta promoción explícita):

- Política: `docs/infraestructura_agentes_skills_v1_1/POLITICA_OPERATIVA_DATAGASTRO_V1_1.md`
- Ciclo y roles: `docs/infraestructura_agentes_skills_v1_1/CICLO_OPERATIVO_UNA_PASADA.md` —
  una producción → una auditoría independiente → una corrección puntual → decisión → cierre.
  El QA del productor no es auditoría independiente. Estado vigente de Polos INFORMEFINAL:
  leer SIEMPRE `outputs/polos_gastro/INFORMEFINAL/ESTADO_GENERAL_INFORMEFINAL.md` y
  `DECISIONES_CERRADAS_Y_PENDIENTES.md`; ningún mapa técnico es fuente de estatus institucional.
- Catálogo: `docs/infraestructura_agentes_skills_v1_1/CATALOGO_AGENTES_SKILLS.json`
- Guía / evaluación / adaptadores propuestos: `docs/infraestructura_agentes_skills_v1_1/`
- Skills de procedimiento (V1, reutilizadas): `docs/infraestructura_agentes_skills_v1/skills/`
- Superficies protegidas: `docs/<subproyecto>/PROTECTED_SURFACES.yaml` (ej. Polos)

Ante conflicto: guardrails (01) > autorización humana de excepciones permitidas > política V1.1 > agente > skill > tarea.
No crear `.claude/agents/` ni tocar `.claude/settings.json` sin pedido. Coordinador, editor y auditor metodológico no se activan como nativos en V1.1.

## Entorno

- Windows. Shell primaria PowerShell; Bash disponible para POSIX.
- **Python: invocar SIEMPRE `.venv/Scripts/python.exe`, nunca `python` a secas** (el Python de
  Microsoft Store lo pisa y no tiene los paquetes del proyecto).
- Paquetes disponibles en `.venv`: `pandas`, `openpyxl`, `pypdf`, `pymupdf` (importar como
  `fitz`), `reportlab`, `PIL`, `geopandas`, `matplotlib`, `requests`.
- **QA visual de PDFs:** usar `scripts/qa/pdf_check.py` (páginas → PNG vía PyMuPDF + texto).
  Después de generar cualquier PDF, renderizar y **mirar** las páginas antes de darlo por
  terminado; no alcanza con que el generador corra sin error.
- **Commits multilínea:** here-string de PowerShell `@'...'@` o `git commit -F archivo.txt`;
  nunca heredocs bash en PowerShell. Para transformar texto, preferir Python del venv antes que
  one-liners de `sed`/`awk`.
- **KPIs de informes:** si existe `kpis_lock.json` junto al generador de un informe, validar con
  `scripts/qa/validate_kpis.py` antes de entregar; los números canónicos no se cambian sin aviso.
- Pipeline (no regenerar salidas sin permiso):
  `python src/build_model.py --strict-real`, `python src/build_analytics.py --strict-real`,
  `python src/validate_model.py --strict-real`, `python -m unittest discover tests`.

## Continuidad entre sesiones

- Al iniciar trabajo que continúa algo previo, leer el `docs/revisiones/HANDOFF_*.md` más
  reciente (un hook de SessionStart lo señala automáticamente).
- En tareas largas, mantener/actualizar ese handoff sin que Diego lo pida, para que un corte por
  tokens no pierda contexto.

## Alcance por subproyecto (no re-litigar)

- **Casas de Pastas:** solo casas/fábricas de pastas; NO restaurantes ni restaurantes italianos.
- **Mercados:** mercados gastronómicos específicamente; NO mercados generales/minoristas.
- **PolosGastro:** el objetivo NO es franquicias ni solo cadenas grandes. Abasto = subzona del
  polo Corrientes, no zona propia.
- **Marca pública:** DGDGAS (Dirección General de Desarrollo Gastronómico); DataGastro solo en docs internos.
- No tocar los otros subproyectos (Cafecito / Mercados / CasasDePastas / PolosGastro / V2) salvo
  pedido explícito.

## graphify

This project has a knowledge graph at `.graphify/` (CLI: `@sentropic/graphify`, installed globally
via npm). The old `graphify-out/` directory is a stale copy from a previous version — do not use it.

Rules:

- For codebase questions, first run `graphify query "<question>"` when `.graphify/graph.json` exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- Read `.graphify/GRAPH_REPORT.md` only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
- graphify is for orienting in **code** (scripts/, src/); for docs e informes, ir directo a los archivos.
