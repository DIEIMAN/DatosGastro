# DataGastro

Datos del ecosistema gastronómico de la Ciudad Autónoma de Buenos Aires para la DGDGAS
(Dirección General de Desarrollo Gastronómico). Repositorio interno: los entregables públicos
llevan la marca DGDGAS; "DataGastro" es el nombre de trabajo.

El repo tiene dos capas: un **pipeline reproducible de fuentes públicas** (F01–F05, congelado
desde junio de 2026) y una serie de **subproyectos** que lo usan como base: Polos Gastronómicos
(Atlas), Barrido de la Ciudad, estudios de rubro (casas de pastas, panaderías), Mercados
gastronómicos y Cafecito.

## Cómo se trabaja acá

1. Leer `CLAUDE.md` (guardrails, entorno, alcance). Vale para cualquier asistente; `AGENTS.md`
   agrega lo específico de Codex.
2. Leer `docs/revisiones/HANDOFF_ACTUAL.md` y el `docs/<subproyecto>/ESTADO.md` del hilo que se
   va a tocar.
3. `docs/README.md` dice qué hay en cada carpeta y qué es vigente.
4. Python siempre desde el venv: `.venv/Scripts/python.exe`. Tareas estándar en el `Makefile`.

```bash
.venv/Scripts/python.exe -m pip install -r requirements.txt
make test          # 91 tests
make estado        # estado del repo: handoff, git, pesos
```

## Estructura

| Carpeta | Qué es |
|---|---|
| `src/` | Pipeline F01–F05 (`download_sources`, `profile_sources`, `build_model`, `build_analytics`, `validate_model`), más `src/v2/` y `src/mercados_caba/`. **Protegido**: no se regenera sin permiso. |
| `data/` | `raw/` descargas reales, `seeds/` desarrollo (no son datos reales), `processed/` y `analytics/` salidas del pipeline, `fuentes_externas/` descargas de fuentes abiertas (RUS, censo, OSM, Overture, ATP, Wikidata). |
| `scripts/` | Un subdirectorio por subproyecto (`polos_gastro/`, `barrido_ciudad/`, `casas_pastas/`, `panaderias/`, `cafecito/`, `mercados/`), más `shared/` (lector de fuentes locales, reporting DGDGAS), `qa/` (QA de PDF, KPIs, estado del repo) y `hooks/` (guardrails en código). |
| `outputs/` | Un subdirectorio por subproyecto; lo vigente con nombre, lo cerrado en `historico/`. `entregas/` para paquetes entregados. `analisis_interno/` no se versiona. |
| `docs/` | `general/` (diccionario, contratos, guías del pipeline), un subdirectorio por subproyecto con `ESTADO.md`, `revisiones/` (handoffs y auditorías), `skills_claude/` (reglas en detalle), `estudios_de_rubro/` (receta para abrir un rubro), `archive/`. |
| `tests/` | `python -m unittest discover tests`. |
| `.claude/skills/` | Skills de Claude Code (canónicas). `.agents/skills/` son punteros para otros agentes. |
| `config/`, `schemas/`, `sql/`, `dashboard/`, `notebooks/` | Configuración de encuestas y V2, esquemas V2, DDL histórico, dashboard Streamlit de demo y notebooks de junio (congelados). |

## Pipeline público F01–F05

- F01 Oferta y establecimientos gastronómicos (BA Data). F02 Habilitaciones aprobadas AGC
  2015–2025. F03 Ferias y mercados (CSV + GeoJSON FIAB). F04 Eventos y F05 Programas:
  relevamientos manuales trazables, no datasets oficiales completos.
- **F02 son habilitaciones, no locales activos.** No sumar F01 + F02 como establecimientos.
- El archivo F02 llamado «2025» republica trámites de 2015–2018 con otro identificador; el «2023»
  está subrepresentado en origen. Detalle en `docs/estudios_de_rubro/LECTOR_FUENTES_LOCALES.md`.

```bash
.venv/Scripts/python.exe src/build_model.py --strict-real
.venv/Scripts/python.exe src/build_analytics.py --strict-real
.venv/Scripts/python.exe src/validate_model.py --strict-real
```

En modo estricto no se permiten seeds. Las cifras del pipeline, sus contratos de columnas y sus
limitaciones están en `docs/general/` (`diccionario_de_datos.md`, `contratos_fuentes.md`,
`perfilado_fuentes.md`, `pendientes_y_limitaciones.md`) con su fecha de corte.

## Subproyectos

| Subproyecto | Estado y entregable vigente |
|---|---|
| Polos Gastronómicos / Atlas | `docs/polos_gastro/ESTADO.md`; estatus institucional en `outputs/polos_gastro/INFORMEFINAL/ESTADO_GENERAL_INFORMEFINAL.md`. |
| Barrido de la Ciudad / base gastronómica | `outputs/BARRIDO_CIUDAD_2026-08/README.md` y `README_BASE_GASTRONOMICA.md`. |
| Panaderías | `docs/panaderias/README_PANADERIAS.md`. |
| Casas de pastas | `docs/casas_pastas/ESTADO.md`. |
| Mercados gastronómicos | `docs/mercados_caba/ESTADO.md`. |
| Cafecito | `docs/cafecito/ESTADO.md`. |

Dashboard de demo interna: `streamlit run dashboard/app.py` (lee `data/analytics/` y
`data/processed/`; checklist en `docs/general/CHECKLIST_DEMO_DATAGASTRO.md`).
