# Revisión Fase 25 política experimental

Estado: **EXPERIMENTAL / NO OFICIAL**. No es Fase 25 oficial ni Fase 26.

Este paquete cierra la tanda editorial iniciada por Fable. Contiene el PDF político experimental de 10 páginas, sus 10 PNG de QA, el contenido editable, el generador reproducible y la documentación editorial y metodológica asociada.

## Lectura recomendada

1. `AUDITORIA_CONTINUIDAD_FABLE_INCOMPLETO.md`.
2. `QA_VISUAL_PAGINA_A_PAGINA_FASE25_POLITICA.md`.
3. PDF experimental.
4. `REGISTRO_DECISIONES_EDITORIALES_V2.md`.
5. `PLAN_INTEGRACION_HANDOFF_CODEX_V21.md`.

## Regeneración

Desde la raíz del repositorio:

```powershell
.venv\Scripts\python.exe scripts\polos_gastro\experimentos\fase25_politica_e_integracion_editorial_v1\generar_fase25_politica_experimental_v1.py
```

El generador usa un parser YAML de respaldo y no requiere instalar PyYAML. Lee los assets oficiales de Fase 25 en modo solo lectura y crea copias sanitizadas dentro de la carpeta experimental.

## Límites

- Los mapas incluidos continúan siendo placeholders editoriales.
- No se integró `pipeline_hibrido_integracion_v21`.
- No se ejecutaron APIs, descargas, Google Places, clustering ni instalaciones.
- El paquete no contiene fuentes, coordenadas individuales, nombres comerciales, identificadores técnicos, credenciales ni cachés.

