# Scripts — Tanda 1 Expansión V4

Línea experimental y paralela para Z01–Z04. No modifica preflight, evidencia documental, polos cerrados ni pipeline general.

Orden reproducible:

1. `preparar_incremental_tanda1_v4.py`
2. `consulta_brechas_tanda1_v4.py` (fail-closed; en esta corrida no hizo red)
3. `deduplicar_tanda1_v4.py`
4. `construir_universos_tanda1_v4.py`
5. `corrida_territorial_tanda1_v4.py`
6. `generar_mapas_tanda1_v4.py`
7. `qa_tanda1_v4.py`

Ejecutar con `.venv/Scripts/python.exe`. No instalar dependencias. El estado esperado de esta corrida es `REUSE_ONLY`.
