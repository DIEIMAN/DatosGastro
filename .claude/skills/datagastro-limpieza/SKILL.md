---
name: datagastro-limpieza
description: Borrado seguro de archivos locales en DataGastro. Usar SIEMPRE antes de borrar o mover archivos del proyecto. Drive nunca se toca; el local solo con plan previo y confirmación.
---

# Limpieza de archivos locales

Contenido canónico: `docs/skills_claude/08_limpieza_archivos_locales.md`.

- Drive no se toca. El proyecto local sí se puede limpiar, con plan previo + confirmación de Diego.
- Clasificar cada ítem en: **seguro borrar** / **revisar** / **no borrar**.
- No borrar nunca sin permiso: outputs finales, scripts, datos fuente públicos, `data/processed`,
  `data/analytics`, documentación, configuración.
- Priorizar: outputs internos pesados regenerables, copias duplicadas (hash idéntico),
  diagnósticos temporales.
- Ante duda: mover a cuarentena (`data/archive/_a_revisar/`) antes que borrar definitivo.
