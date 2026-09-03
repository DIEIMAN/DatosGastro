# Handoff — auditoría de flujo de trabajo, 2026-09-03

Pedido de Diego: auditoría exhaustiva del repo (global → skills, hooks, MCPs) con qué secar,
mejorar y sumar; después, «corregí todo». Informe: `AUDITORIA_FLUJO_DE_TRABAJO_2026_09_03.md`.

## Ejecutado el 2026-09-03 (Bloques A y B)

- **Git:** trackeado lo canónico que faltaba (lector F02, panaderías, tests, docs de rubro,
  handoffs, DECISIONES de Polos); commits separados para el guardrail 6 y las skills, el contenido
  del barrido (Atlas V3, rondas 21–22), la F3 de Polos (71 scripts + rename + .gitignore) y la
  renormalización de fin de línea (329 archivos, cero cambios reales). `core.autocrlf=false` local.
- **Estructura:** `docs/general/` (12 docs del pipeline), `docs/archive/v3_2026-06/` (8 de junio),
  `docs/casas_pastas/{historico_v4_2026-06,revision_institucional_2026-07}`,
  `docs/mercados_caba/revision_dgdgas_2026-07`, hotfix V1.1.1 a `docs/archive/`,
  `outputs/mercados` → `outputs/mercados_caba/revision_dgdgas_2026-07`, `exports/` y
  `deliverables/` → `outputs/entregas/`. Referencias parcheadas (skills_claude 01/02/04/08,
  agent_skills/README, build_pdf_dgdgas_mercados, parity, hotfix).
- **Navegación:** CLAUDE.md reescrito (~95 líneas, guardrails intactos), AGENTS.md remite a
  CLAUDE.md, README.md actualizado, `docs/README.md`, `HANDOFF_ACTUAL.md`, `ESTADO.md` para polos,
  casas_pastas, mercados_caba y cafecito, nota F3 en `ESTADO_GENERAL_INFORMEFINAL.md`.
- **Skills:** `datagastro-limpieza` fusionada en `datagastro-guardrails`; capa
  `agent_skills/claude_imported/` eliminada (queda `.agents/skills/` como puntero);
  `datagastro-recoleccion-polos` pasa a `.claude/skills/` con sus scripts; nuevas
  `datagastro-abrir-rubro` y `datagastro-mcps`; chromadb-rag, duckdb-sql, folium-mapas y
  clustering-polos con el intérprete correcto y sin pies que repetían guardrails.
- **Tooling:** `pyproject.toml` (ruff + pytest), `requirements.txt` completo y pinneado,
  `requirements-tools.txt`, `Makefile`, ruff instalado en `.venv` (754 avisos, 1 nombre indefinido
  en un experimento de Polos; nada corregido automáticamente), `.gitignore` reescrito (sin
  redundancias, con `tmp/`, `cache/`, `.playwright-mcp/`, `PolosGastro/`, `outputs/**/*.docx`),
  `scripts/qa/estado_repo.py`, `scripts/qa/check_docs_links.py`,
  `scripts/hooks/guardrails_pretooluse.py`, `scripts/hooks/stop_pdf_qa.py`, grafo de graphify
  regenerado.
- **Memoria persistente:** ~60 crónicas de Polos/Atlas/Barrido consolidadas en 4 archivos.

## Lo que NO pude hacer (bloqueado por el clasificador de permisos)

`.claude/settings.json` y `settings.local.json`: las versiones propuestas están en
`docs/revisiones/settings_propuestos/` con su README. **Hasta que se copien, los hooks nuevos no
corren y los de graphify siguen activos.**

## Decisiones que esperan a Diego (Bloque C, sin ejecutar)

Cuarentena F0 (228 MB), dump ATP (2,8 GB), `DataMercados.zip`, espejos de raíz (`Cafesito/` etc.),
copias `.docx` intermedias del Atlas 39 (574 MB), 189 duplicados de `docs/polos_gastro/`,
consolidar `outputs/casas_pastas_*` (la canónica está ignorada por Git), `fuentes_internas_mercados_caba/`
(toca `src/`), merge a `main` y cierre de `casas-pastas-integrado`, `kpis_lock.json` adoptar o
retirar, agente nativo `auditor-qa`, `scripts/cafecito/` a archivo, `scripts/compat/`, `sql/`,
`node_modules/`, cerrar la migración al lector F02 en pastas y polos.
