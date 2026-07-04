---
name: datagastro-informes
description: Redactar informes ejecutivos de DataGastro para jefatura. Usar al producir cualquier informe, resumen o entregable institucional. Tono sobrio, sin lenguaje de IA, separar hallazgos de límites.
---

# Informes ejecutivos

Contenido canónico: `docs/skills_claude/07_informes_ejecutivos.md`.

- Tono institucional, claro, sin exagerar, sin lenguaje de IA ni superlativos vacíos.
- Estructura: resumen ejecutivo → hallazgos (tablas/bullets) → límites y riesgos metodológicos →
  próximos pasos → anexo.
- Separar hallazgos de límites. Cada número con fuente, fecha de corte y universo.
- Sustantivo correcto (no "activos" si no aplica). Sin datos personales/individuales.
- Declarar qué se puede publicar y qué no. Versión interna a `outputs/analisis_interno/`.

## Plantilla institucional DGDGAS (defaults obligatorios del primer borrador)

Estos requisitos NO se esperan del pedido: se aplican siempre, sin que Diego los repita.

- **Marca pública: DGDGAS — Dirección General de Desarrollo Gastronómico.** "DataGastro" nunca aparece en
  entregables públicos (solo en documentación interna de `docs/`).
- **Portada:** título + DGDGAS. NO mostrar fecha, número de versión, "documento interno",
  "borrador", "prueba", "revisión institucional" ni equivalentes en ninguna página.
- **Índice** y **secciones numeradas** siempre.
- **Cuerpo documental y expositivo**, no centrado en gestión ni en metodología: la metodología,
  fuentes y respaldo documental van al anexo, no al cuerpo.
- **Lenguaje prudente:** "activos identificados", no "confirmados"; "oferta registrada", no
  "locales activos" si la fuente no lo mide.
- **KPIs:** si existe `kpis_lock.json` del informe, correr
  `.venv/Scripts/python.exe scripts/qa/validate_kpis.py <lock> <entregables>` antes de entregar.
  Los números canónicos no cambian sin avisar explícitamente.
- **QA visual antes de entregar:** para PDFs, usar el skill `datagastro-qa-pdf` (renderizar y
  mirar todas las páginas). Un PDF no revisado visualmente no está terminado.
- **Cierre de tarea:** informar siempre las rutas absolutas de los archivos producidos.
