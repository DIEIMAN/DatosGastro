# Handoff — de Claude Design a implementación (código)

Guía para pasar del sistema visual DGDGAS (tokens + componentes) a un informe
concreto en PDF, DOCX o Google Docs. Explica el flujo, qué tocar y qué **no**
tocar.

---

## 0. Estado de Claude Design en esta base

- El sistema visual se creó **localmente** a partir del pack de referencia
  (`outputs/datagastro_design_system/claude_design_pack/`).
- Al momento de crear la v1, **no existía un proyecto en claude.ai/design** del
  cual sincronizar (la lista de proyectos de design system estaba vacía).
- Si en el futuro se quiere publicar este sistema como proyecto de Claude
  Design (para verlo/editarlo en claude.ai/design), se puede usar el flujo
  `/design-sync` / `DesignSync`. Esa es una acción **hacia afuera** y requiere
  autorización explícita de Diego antes de crear el proyecto remoto y subir
  archivos. No se ejecutó en la v1.

---

## 1. Fuente de verdad

1. **Tokens:** `tokens/design_tokens_dgdgas.yaml` (el `.json` se deriva de él).
2. **Componentes:** `COMPONENTES_INFORMES_DGDGAS.md`.
3. **Plantillas de página:** `PLANTILLAS_PAGINA_DGDGAS.md`.
4. **Contenido:** un YAML por informe basado en
   `templates/template_informe_dgdgas.yaml`.

Regla de oro: **el contenido va en YAML/JSON; el estilo va en tokens; el código
solo compone.** Nunca poner texto de informe hardcodeado en el generador.

---

## 2. Flujo para generar un informe nuevo

### Paso 1 — Preparar el contenido
Copiar `templates/template_informe_dgdgas.yaml` a la carpeta del proyecto
(por ejemplo `docs/polos_gastro/`) y completarlo con el contenido real del
informe. No inventar datos ni métricas.

### Paso 2 — Elegir formato
- **PDF:** partir de `scripts/shared/reporting_dgdgas/template_pdf_informe_dgdgas.py`.
- **DOCX:** partir de `scripts/shared/reporting_dgdgas/template_docx_informe_dgdgas.py`.
- **Google Docs:** partir de
  `templates/template_payload_google_docs_dgdgas.json` (payload de bloques).

### Paso 3 — Componer con los componentes
Usar las primitivas de `report_components_dgdgas.py` (portada, índice, cajas,
tabla, mapa, etc.). No reescribir el estilo: los componentes ya leen los tokens
vía `style_tokens_dgdgas.py`.

### Paso 4 — Generar la salida
Guardar en la carpeta de outputs del proyecto correspondiente
(`outputs/<proyecto>/`), **nunca** sobrescribiendo un informe final existente.
Usar un nombre de versión nuevo.

### Paso 5 — QA
Pasar el checklist de `QA_VISUAL_INFORMES_DGDGAS.md` antes de considerar el
informe listo.

---

## 3. Pedidos típicos de la siguiente fase

Cuando quieras avanzar, podés pedir literalmente:

- **«Aplicá el sistema visual DGDGAS a PolosGastro».**
  → Se crea el YAML de contenido de PolosGastro a partir del material de
  `outputs/datagastro_design_system/claude_design_pack/referencias/polos_gastro/`
  y se compone con los componentes. No se toca la Fase 5/6 existente.

- **«Generá un informe PDF de PolosGastro con los componentes DGDGAS».**
  → Se instancia `template_pdf_informe_dgdgas.py` para PolosGastro.

- **«Generá un DOCX editable con el mismo sistema».**
  → Se instancia `template_docx_informe_dgdgas.py`.

- **«Revisá el QA visual del informe».**
  → Se corre el checklist de QA.

---

## 4. Qué NO tocar (guardrails del handoff)

- **No** modificar los informes finales existentes (Cafecito final, PolosGastro
  Fase 5/6, MercadosGastro, CasasDePastas).
- **No** tocar `data/`, `src/` general, dashboards ni notebooks.
- **No** modificar PDFs finales ni fuentes XLSX/PDF.
- **No** integrar todavía estos scripts con Cafecito ni PolosGastro (la v1 solo
  provee la base).
- Salidas nuevas siempre con **nombre de versión nuevo**, en la carpeta del
  proyecto.

---

## 5. Publicar el sistema en Claude Design (opcional, fase futura)

Si Diego lo autoriza, el sistema puede publicarse como proyecto de design
system en claude.ai/design con `DesignSync` / `/design-sync`:

1. `DesignSync list_projects` → confirmar que no existe ya.
2. `DesignSync create_project` con nombre `DGDGAS Informes` (requiere permiso).
3. Preparar un bundle de previews HTML de los componentes.
4. `finalize_plan` con las rutas exactas → `write_files`.

Esto es un paso hacia afuera (publica contenido en un servicio externo) y **no**
se hace sin confirmación explícita.
