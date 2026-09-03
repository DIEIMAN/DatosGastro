# Settings propuestos (2026-09-03)

Claude Code no puede escribir `.claude/settings.json` ni `settings.local.json` (el clasificador
de permisos lo bloquea). Estos dos archivos son las versiones que propone la auditoria de flujo.
Para aplicarlos: copiarlos sobre `.claude/settings.json` y `.claude/settings.local.json`.

Que cambia respecto de los actuales:

- **Salen** los dos hooks PreToolUse de graphify (usaban `python3`, que no existe en Git Bash, y
  el grafo tiene semanas de atraso).
- **Entra** un PreToolUse `Bash|PowerShell` -> `scripts/hooks/guardrails_pretooluse.py`: bloquea
  escrituras en Google Drive, borrados o reversiones sobre `data/processed`, `data/analytics`,
  `src/build_*`, `dashboard/`, `notebooks/`, y el uso de `python`/`pip` a secas.
- El SessionStart pasa a `scripts/qa/estado_repo.py --sesion`: handoff vigente (por fecha del
  nombre y `HANDOFF_ACTUAL.md`), modificados reales vs solo fin de linea, sin trackear, commits
  sin push, edad del grafo.
- **Entra** un hook Stop -> `scripts/hooks/stop_pdf_qa.py`: avisa si hay PDFs generados en las
  ultimas 8 h sin `qa_png_*` al lado. No bloquea.
- Plugins `frontend-design` y `atomic-agents` quedan en `false` (cero uso en el repo).
- `settings.local.json`: sale `Bash(git reset *)` (choca con el guardrail 9) y las entradas de un
  solo uso con rutas absolutas del scratchpad; entra `.venv-tools/Scripts/python.exe *`.
