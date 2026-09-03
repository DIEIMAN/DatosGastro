# Tareas estandar de DataGastro. Se corre desde Git Bash (la shell de Claude Code):  make test
# Todas usan el Python del venv, nunca `python` a secas (el de Microsoft Store lo pisa).
#
#   make test                  91 tests en ~10 s
#   make perfil-f02            perfil de los ocho archivos F02 (sale 1 si alguno queda en cero)
#   make rubro RUBRO=panaderias OUT=outputs/_prueba/panaderias
#   make pdf-check FILE=outputs/x/informe.pdf
#   make kpis FILE=outputs/x/informe.pdf LOCK=outputs/x/kpis_lock.json
#   make estado                estado del repo (git, handoff, pesos)
#   make lint                  ruff sobre scripts/, src/, tests/ (sin corregir)
#   make graph                 regenera el grafo de graphify (AST, sin costo)
#   make clean-pycache         borra __pycache__ fuera de los venvs
#
# No hay tareas que regeneren data/processed, data/analytics ni outputs finales: eso requiere
# permiso explicito (guardrail 2) y se corre a mano.

PY      := .venv/Scripts/python.exe
PYTOOLS := .venv-tools/Scripts/python.exe

.PHONY: test perfil-f02 rubro pdf-check kpis estado lint graph clean-pycache

test:
	$(PY) -m unittest discover tests

perfil-f02:
	$(PY) -m scripts.shared.fuentes_locales.f02

rubro:
	@test -n "$(RUBRO)" || (echo "uso: make rubro RUBRO=panaderias OUT=outputs/_prueba/panaderias" && exit 1)
	$(PY) scripts/$(RUBRO)/build_$(RUBRO).py $(if $(OUT),--out $(OUT),)

pdf-check:
	@test -n "$(FILE)" || (echo "uso: make pdf-check FILE=ruta.pdf" && exit 1)
	$(PY) scripts/qa/pdf_check.py "$(FILE)"

kpis:
	@test -n "$(FILE)" -a -n "$(LOCK)" || (echo "uso: make kpis FILE=informe.pdf LOCK=kpis_lock.json" && exit 1)
	$(PY) scripts/qa/validate_kpis.py "$(FILE)" "$(LOCK)"

estado:
	$(PY) scripts/qa/estado_repo.py

lint:
	$(PY) -m ruff check scripts src tests

graph:
	graphify update .

clean-pycache:
	find . -name __pycache__ -type d -not -path "./.venv*" -not -path "./node_modules/*" -not -path "./.agent-tools/*" -prune -exec rm -rf {} +
