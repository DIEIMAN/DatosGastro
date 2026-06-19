# Skill 08 — Limpieza de archivos locales

Cómo limpiar el proyecto local sin perder nada importante y sin tocar Drive.

## 1. Reglas base

1. **Drive no se toca.** Nunca borrar/mover en `G:\My Drive` ni `G:\.shortcut-targets-by-id`
   (skill 01). La limpieza es **solo del proyecto local**.
2. **El proyecto local SÍ se puede limpiar**, especialmente outputs internos pesados, copias
   extraídas de Drive y diagnósticos temporales.
3. **Siempre con plan previo + confirmación.** Antes de borrar o mover, generar un plan y esperar
   el OK de Diego.
4. Preferir **mover a una zona de cuarentena** (p. ej. `data/archive/_a_revisar/`) antes que
   borrar definitivo, cuando hay duda.

## 2. Plan de limpieza: tres categorías obligatorias

Todo plan de limpieza clasifica cada ítem en:

| Categoría | Qué incluye | Acción |
| --- | --- | --- |
| **Seguro borrar** | Caches (`__pycache__`, `.pytest_cache`), temporales (`outputs/tmp/`), `.pyc`, HTML/PDF regenerables, copias duplicadas idénticas (mismo hash) que ya están versionadas o en Drive | Borrar tras confirmación |
| **Revisar** | Outputs internos pesados, copias extraídas de Drive, diagnósticos viejos, artefactos de los que no se está seguro si se regeneran | Listar, mostrar tamaño/origen, decidir con Diego |
| **No borrar** | Outputs finales del informe, scripts (`src/`, `scripts/`), datos fuente públicos (`data/raw`, `data/seeds`), `data/processed`, `data/analytics`, documentación, configuración | Intocable sin permiso explícito |

## 3. Qué NUNCA se borra sin permiso explícito

- Outputs finales del informe (`docs/informe_ejecutivo.*`, entregables aprobados).
- Scripts del pipeline y utilitarios (`src/`, `scripts/`, `tests/`, `dashboard/`).
- Datos fuente públicos (`data/raw/`, `data/seeds/`).
- Salidas productivas (`data/processed/`, `data/analytics/`).
- Configuración, `.gitignore`, documentación.

## 4. Qué se prioriza para limpiar (cuando se aprueba)

- **Outputs internos pesados** que se pueden regenerar.
- **Copias duplicadas** confirmadas por hash idéntico.
- **Diagnósticos temporales** y exploraciones viejas.
- Archivos extraídos de un ZIP que quedaron mal ubicados, **una vez** reubicado lo útil y
  confirmado que el original sigue disponible.

## 5. Procedimiento

1. **Inventariar**: listar candidatos con ruta, tamaño, fecha, y si tienen copia/hash en otro lado.
2. **Clasificar** en seguro / revisar / no borrar.
3. **Verificar reproducibilidad**: ¿se regenera con el pipeline? ¿hay copia en Drive o en Git?
4. **Presentar el plan** a Diego y esperar confirmación.
5. **Ejecutar** solo lo aprobado; preferir mover a cuarentena antes que borrado definitivo.
6. **Dejar constancia** de lo borrado/movido (en el commit o en una nota).

## 6. Antes de borrar un archivo concreto

- ¿Lo creé yo en esta sesión o ya estaba? Si ya estaba y no sé qué es, **no lo borro**.
- ¿Su contenido contradice lo que me dijeron que era? → frenar y avisar.
- ¿Es la única copia? → no borrar; mover a cuarentena y consultar.
- ¿Está en `.gitignore` y es pesado/regenerable? → candidato a "seguro", igual con confirmación.
