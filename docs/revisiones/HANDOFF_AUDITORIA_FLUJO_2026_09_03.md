# Handoff — auditoría de flujo de trabajo, 2026-09-03

Pedido de Diego: auditoría exhaustiva del repo (global → skills, hooks, MCPs) con qué secar,
mejorar y sumar. Informe completo: `AUDITORIA_FLUJO_DE_TRABAJO_2026_09_03.md` (mismo directorio).

## Qué se hizo

Cuatro auditorías de solo lectura en paralelo y consolidación. **Nada borrado, movido ni
commiteado.**

## Lo urgente (Bloque A del informe, no requiere decisión)

1. `scripts/shared/fuentes_locales/`, `scripts/panaderias/`, `tests/test_fuentes_locales.py`,
   `tests/test_casas_pastas_dedup.py`, `docs/estudios_de_rubro/`, `docs/panaderias/`, 20 handoffs
   y `DECISIONES_CERRADAS_Y_PENDIENTES.md` están **sin trackear**. Primer commit.
2. La **F3 de la reorganización (Polos historico/) está hecha en disco desde el 08-28 y sin
   commit**: 71 scripts de `scripts/polos_gastro` con rutas parcheadas en working tree. Un
   `git checkout .` los rompe. Commit `reorg(F3)` separado del de contenido.
3. 529 de los 646 modificados son solo fin de línea: `git add --renormalize .` y commit propio.
4. 50 commits sin push en `mercados-gastronomicos-v2` (rama principal de facto; `main` congelada
   desde 06-19 y puede hacer fast-forward).
5. Hooks de graphify rotos (`python3` no existe en Git Bash; grafo 13 commits atrás; sin
   `graph.json`). `"Bash(git reset *)"` en el allow local.

## Decisiones que esperan a Diego

Cuarentena F0 (228 MB), dump ATP (2,8 GB), `DataMercados.zip`, espejos de raíz, copias `.docx`
intermedias del Atlas 39 (574 MB), merge a `main`, `kpis_lock.json` adoptar o retirar, agente
nativo `auditor-qa`, archivo de `scripts/cafecito/`.

## Próximo paso sugerido

Ejecutar el Bloque A en ese orden, un commit por paso, corriendo `unittest` tras el paso 2.
