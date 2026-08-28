# Reproducción V2.2

Desde la raíz del repositorio:

```powershell
.venv\Scripts\python.exe scripts\polos_gastro\fase29_microajustes_cierre_informe_politico_v2_2\generar_informe_politico_integrado_v2_2.py
```

La ejecución lee fase28 en modo de solo lectura, aplica la capa de microajustes y genera una línea
nueva. El recorte de Costanera se deriva del SVG V3.2 sin alterar geometrías. No ejecuta análisis
territorial, solicitudes de red, servicios externos ni instalaciones. `--no-pack` permite iterar
los controles visuales antes del empaquetado.
