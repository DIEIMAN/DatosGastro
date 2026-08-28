# Reproducción de la línea V2.1

Desde la raíz del repositorio:

```powershell
.venv\Scripts\python.exe scripts\polos_gastro\fase28_ajustes_finales_informe_politico_v2_1\generar_informe_politico_integrado_v2_1.py
```

La ejecución es local y deriva una línea nueva. Lee la fase27 y los assets cartográficos V3.1,
pero no los modifica. No realiza solicitudes de red, llamadas a servicios externos, cálculos de
modelos ni cambios de geometría. La opción `--no-pack` omite el armado del paquete durante las
iteraciones de control visual.

Requisitos: entorno virtual existente del repositorio y dependencias ya instaladas. No se deben
instalar paquetes adicionales.
