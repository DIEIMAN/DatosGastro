# DGDGAS Informes — Design System v1

Base reutilizable para informes institucionales de la **Dirección General de
Gastronomía (DGDGAS)** en formato PDF, DOCX y Google Docs.

Este directorio contiene el sistema visual y editorial: tokens, componentes,
plantillas de página, guías de handoff y QA. Su objetivo es que futuros
informes (por ejemplo PolosGastro, MercadosGastro, CasasDePastas o nuevos
relevamientos) se produzcan con una identidad institucional coherente, sobria y
prudente, sin rehacer el diseño desde cero cada vez.

> **Marca pública por defecto:** `DGDGAS – Dirección General de Desarrollo Gastronómico`.
> `DataGastro` es el nombre **interno** del sistema/proyecto y solo aparece en
> documentación técnica cuando corresponde. No se usa como marca pública.

## Alcance de esta versión (v1)

Esta v1 es **la base del sistema**. No aplica el diseño a ningún informe
existente todavía. En particular:

- **No** modifica Cafecito (informe final), PolosGastro (Fase 5/6),
  MercadosGastro ni CasasDePastas.
- **No** toca `data/`, `src/` general, dashboards ni notebooks.
- Los scripts de `scripts/shared/reporting_dgdgas/` son **esqueletos
  reutilizables**: definen la API y el estilo, pero no generan aún un informe
  completo ni se integran con ningún proyecto.

## Estructura del directorio

```
docs/datagastro_design_system/
├─ README_DGDGAS_DESIGN_SYSTEM.md      ← este archivo (punto de entrada)
├─ DGDGAS_INFORMES_DESIGN_SYSTEM_V1.md ← documento maestro (marca, tono, tokens)
├─ COMPONENTES_INFORMES_DGDGAS.md      ← catálogo de componentes reutilizables
├─ PLANTILLAS_PAGINA_DGDGAS.md         ← plantillas de página tipo
├─ HANDOFF_CLAUDE_DESIGN_A_CODE.md     ← cómo pasar de diseño a implementación
├─ QA_VISUAL_INFORMES_DGDGAS.md        ← checklist de QA visual y público
├─ tokens/
│  ├─ design_tokens_dgdgas.yaml        ← tokens (fuente de verdad)
│  └─ design_tokens_dgdgas.json        ← tokens (para herramientas)
└─ templates/
   ├─ template_informe_dgdgas.yaml     ← esqueleto de contenido de informe
   └─ template_payload_google_docs_dgdgas.json ← payload base Google Docs

scripts/shared/reporting_dgdgas/
├─ README.md                           ← uso de los esqueletos
├─ style_tokens_dgdgas.py              ← carga y resuelve tokens
├─ report_components_dgdgas.py         ← primitivas de componentes
├─ template_pdf_informe_dgdgas.py      ← esqueleto de informe PDF
└─ template_docx_informe_dgdgas.py     ← esqueleto de informe DOCX
```

## Cómo se relaciona con el pack de Claude Design

El pack de referencia está en
`outputs/datagastro_design_system/claude_design_pack/`. Contiene la guía de
estilo, las pautas de Cafecito, los componentes requeridos y material histórico
(Cafecito REVISION_4, PolosGastro, MercadosGastro, CasasDePastas). Este sistema
**implementa** ese pack como base de código y documentación dentro de `docs/`.

- La referencia editorial **principal** es Cafecito DGDGAS REVISION_4.
- MercadosGastro y CasasDePastas son **antecedentes históricos**: no se copian
  tal cual, se actualizan al criterio DGDGAS.

## Cómo usarlo después

Cuando quieras avanzar a la siguiente fase, se puede pedir por ejemplo:

- «Aplicá el sistema visual DGDGAS a PolosGastro».
- «Generá un informe PDF de PolosGastro usando los componentes DGDGAS».
- «Generá un DOCX editable con el mismo sistema».
- «Revisá el QA visual del informe según las reglas DGDGAS».

Cada uno de esos pedidos usa lo definido en este directorio. La guía de
handoff (`HANDOFF_CLAUDE_DESIGN_A_CODE.md`) explica el flujo paso a paso.

## Orden de lectura recomendado

1. Este README.
2. `DGDGAS_INFORMES_DESIGN_SYSTEM_V1.md` — marca, tono, estructura, tokens.
3. `COMPONENTES_INFORMES_DGDGAS.md` — qué componentes existen y cómo se ven.
4. `PLANTILLAS_PAGINA_DGDGAS.md` — cómo se arma cada página.
5. `HANDOFF_CLAUDE_DESIGN_A_CODE.md` — cómo implementar un informe concreto.
6. `QA_VISUAL_INFORMES_DGDGAS.md` — cómo revisar antes de publicar.
