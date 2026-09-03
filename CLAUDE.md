# CLAUDE.md — DataGastro

Instrucciones operativas para Claude Code (y cualquier asistente) en este repositorio. Este
archivo se carga en cada sesión: contiene las reglas permanentes y los punteros; el detalle vive
en `docs/`. **Ante conflicto, ganan los guardrails.**

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
6. **Recolección externa controlada.** Se permite relevar información comercial visible en
   Google Maps, Rappi, PedidosYa, TripAdvisor, TheFork, Instagram y otras plataformas como
   evidencia externa no canónica. Exigir autorización explícita por tarea, alcance acotado,
   trazabilidad, ritmo prudente y salida interna. No eludir login, CAPTCHA, paywall ni controles
   de acceso; no guardar credenciales/cookies; no ejecutar llamadas pagas sin presupuesto. Nada
   entra automáticamente al Atlas o al pipeline: requiere corroboración y revisión humana.
7. **No exponer datos personales:** CUIT, DNI, emails, teléfonos, contactos, montos o
   transacciones individuales. Trabajar con agregados, perfiles de columnas, conteos y
   diagnósticos; **no exportar filas individuales sensibles**.
8. **No commitear datos internos/privados.** Todo dato interno/privado va al `.gitignore`. Todo
   output interno sensible va a `outputs/analisis_interno/` o carpeta ignorada por Git.
9. **Confirmar antes de cambios destructivos.** Antes de borrar/mover algo del proyecto local:
   plan de limpieza (seguro/revisar/no borrar) y **esperar confirmación**. No borrar outputs
   finales, scripts ni datos fuente públicos. Toda reorganización termina en commit.

Los guardrails 1, 2 y 9 (y el Python del venv) los hace cumplir en código el hook
`scripts/hooks/guardrails_pretooluse.py`; el resto depende de leerlos.

## Mapa del repo y dónde leer

- `docs/README.md` — qué hay en cada carpeta, qué es vigente y qué histórico.
- `docs/revisiones/HANDOFF_ACTUAL.md` — hilos abiertos con su handoff más reciente. Leerlo al
  empezar; el hook de SessionStart lo señala. En tareas largas, actualizar el handoff del hilo
  sin que Diego lo pida.
- `docs/<subproyecto>/ESTADO.md` — estado vigente por subproyecto (cifras canónicas, entregable
  vigente, decisiones abiertas). Para Polos manda además
  `outputs/polos_gastro/INFORMEFINAL/ESTADO_GENERAL_INFORMEFINAL.md` y
  `DECISIONES_CERRADAS_Y_PENDIENTES.md`; ningún mapa técnico es fuente de estatus institucional.
- `docs/skills_claude/01…08` — detalle de guardrails, fuentes, privacidad, pipeline, geodatos,
  fuentes externas, informes, limpieza. Las skills de `.claude/skills/` son sus checklists.
- `agent_skills/shared/datagastro_metodo_experimental.md` — **leer antes de correr cualquier cosa
  que produzca un número que se vaya a leer como conclusión.**
- Infraestructura de agentes V1.1 (ciclo una pasada, catálogo, superficies protegidas):
  `docs/infraestructura_agentes_skills_v1_1/README.md`. Precedencia: guardrails > autorización
  humana > política V1.1 > agente > skill > tarea. No crear `.claude/agents/` ni tocar
  `.claude/settings.json` sin pedido.

## Entorno

- Windows. Shell primaria PowerShell; Bash disponible para POSIX.
- **Python: SIEMPRE `.venv/Scripts/python.exe`** (pipeline, rubros, informes) o
  `.venv-tools/Scripts/python.exe` (recolección). Nunca `python` a secas: el de Microsoft Store
  lo pisa y el hook lo bloquea.
- Tareas estándar en el `Makefile`: `make test`, `make perfil-f02`, `make rubro RUBRO=… OUT=…`,
  `make pdf-check FILE=…`, `make estado`, `make lint`, `make graph`. Si `make` no está instalado,
  cada receta es una línea del propio Makefile y se copia tal cual.
- **QA visual de PDFs:** `scripts/qa/pdf_check.py` renderiza páginas a PNG; mirarlas antes de dar
  un PDF por terminado. El hook de Stop avisa si quedó un PDF sin renderizar.
- **KPIs:** si existe `kpis_lock.json` junto al generador, validar con `scripts/qa/validate_kpis.py`.
- **Commits multilínea:** `git commit -F archivo.txt` o here-string PowerShell `@'...'@`; nunca
  heredocs bash en PowerShell. Transformar texto con Python del venv, no con `sed`/`awk`.
- Fin de línea gobernado por `.gitattributes` (LF en el repo, `core.autocrlf=false` local).
- Pipeline (no regenerar salidas sin permiso): `src/build_model.py --strict-real`,
  `src/build_analytics.py --strict-real`, `src/validate_model.py --strict-real`, `make test`.

## Alcance por subproyecto (no re-litigar)

- **Casas de Pastas:** solo casas/fábricas de pastas; NO restaurantes ni restaurantes italianos.
- **Panaderías:** núcleo (elaboración o despacho de pan) + punto de cocción; NO confitería,
  NO despacho de masas sin elaboración, NO pizzerías (`docs/panaderias/ALCANCE_Y_DEFINICION.md`).
- **Mercados:** mercados gastronómicos específicamente; NO mercados generales/minoristas.
- **PolosGastro:** el objetivo NO es franquicias ni solo cadenas grandes. Abasto = subzona del
  polo Corrientes, no zona propia.
- **Marca pública:** DGDGAS (Dirección General de Desarrollo Gastronómico); DataGastro solo en
  docs internos.
- No tocar otros subproyectos salvo pedido explícito.

## Estudios de rubro (panaderías, casas de pastas y los que sigan)

Antes de abrir o tocar un rubro, invocar la skill `datagastro-abrir-rubro` o leer
`docs/estudios_de_rubro/COMO_ABRIR_UN_RUBRO_NUEVO.md`. Tres reglas que no se negocian: las fuentes
locales se leen **solo** por `scripts/shared/fuentes_locales` (`iter_f01`, `iter_f02`); se agrupa
por `reg.clave_habilitacion`, nunca por partida ni por `id_registro`; y el padrón «2025» republica
trámites viejos y no trae habilitaciones de 2025. El detalle (59 republicados, ochavas,
`--out DIR`, año 2023 subrepresentado) está en `docs/estudios_de_rubro/LECTOR_FUENTES_LOCALES.md`.

## graphify

Grafo de código en `.graphify/` (CLI `graphify`, npm global). Para orientarse en `scripts/` y
`src/`: `graphify query "<pregunta>"`, `graphify explain "<concepto>"`, `graphify path A B`.
Tras modificar código, `make graph`. Es para código; docs e informes se leen directo.
