# Handoff para Claude Code — DGDGAS Informes Design System v1

Guía de implementación del sistema visual. **Este handoff define el sistema; no aplica el diseño a ningún informe todavía.**

- **Marca pública:** DGDGAS — Dirección General de Gastronomía.
- **Nombre interno:** DataGastro (nunca visible en portadas, encabezados ni pies).
- **Fuentes de verdad:** `handoff/tokens.json` + `handoff/COMPONENTES_DGDGAS_DESIGN_SYSTEM.md` + la guía visual `DGDGAS Informes - Design System v1.dc.html`.

---

## 1. Confirmaciones explícitas (leer antes de implementar)

- ✅ **DGDGAS es la marca pública.** Aparece en portada, encabezados y pies.
- ✅ **DataGastro es solo interno.** Se admite como nombre del sistema/metodología, nunca como marca pública por defecto.
- ✅ **Los mapas son referencia territorial, no delimitación oficial.** Barrios/comunas como soporte tenue; sin polígonos de polos; disclaimer visible en cada mapa.
- ✅ **No se usa Google Places** como fuente pública (sesgo comercial, sin delimitación, condiciones a revisar).
- ✅ **No se inventan datos.** Los valores llegan como `{token}` y los completa cada proyecto.
- ✅ **No se generan rankings.** PolosGastro se ordena por grupo, no por puntaje; no es padrón de locales activos.

---

## 2. Estructura de carpetas sugerida

```
dgdgas-informes/
├─ tokens.json                      # copia de handoff/tokens.json (fuente de verdad)
├─ components/
│  ├─ Portada · Indice · SeccionHeader
│  ├─ FichaRelevamiento
│  ├─ PreguntaAnalizada · LecturaResultados · NotaMetodologica
│  ├─ TablaInstitucional · TablaPolos
│  ├─ FichaPolo · MapaContexto
│  ├─ EstadoDocumentacion (EstadoChip) · RequiereValidacion
│  ├─ QueHabilita · AnexoMetodologico
│  └─ ResultadoBarras · FuenteEvidencia · AlcanceAdvertencia
├─ templates/
│  ├─ informe_encuesta        # base: Cafecito
│  ├─ informe_territorial     # base: PolosGastro
│  ├─ informe_ejecutivo_corto
│  ├─ anexo_metodologico
│  └─ resumen_ejecutivo
└─ export/
   ├─ pdf/                    # HTML/CSS @page A4 o Markdown→PDF
   ├─ docx/                   # estilos de párrafo mapeados a tokens
   └─ gdocs/
```

## 3. Archivos a actualizar

### `docs/datagastro_design_system/`
- `TOKENS.md` → generar desde `tokens.json` (tabla de nombre → valor → uso).
- `COMPONENTES.md` → copiar `COMPONENTES_DGDGAS_DESIGN_SYSTEM.md`.
- `GUIA_ESTILO.md` → actualizar con: paleta, tipografías, jerarquía, grilla A4, reglas de uso (hacer/no hacer) y QA público.
- `CARTOGRAFIA.md` → reglas de `map.*`: barrios tenues, halos por grupo, disclaimer y fuente obligatorios, sin Google Places.

### `scripts/shared/reporting_dgdgas/`
- `tokens.py` (o `tokens.js`) → cargar `tokens.json` y exponer constantes (`COLOR`, `STATE`, `TYPE`, `SPACE`, `PAGE`, `TABLE`, `CHIP`, `MAP`).
- `components/` → una función/plantilla por componente del inventario, parametrizada por sus campos.
- `render_pdf.*` → compone `templates/*` con datos reales; A4 vertical; sin sombras.
- `render_docx.*` → mapea estilos de párrafo a tokens (ver §5).
- `qa_publico.*` → checklist automatizable (rutas locales, emails, hashes, marca correcta, respuestas individuales).

> No reescribir el contenido de los informes existentes ni cambiar la clasificación de polos: los scripts consumen los datos ya curados.

## 4. Mapear tokens a PDF

- PDF es la **fuente de verdad** del formato.
- Página: `@page { size: A4 portrait; margin: 22mm 20mm; }`. Grilla de 12 columnas, medianil 5mm.
- Tipografía por `type.size` en **pt** (h1 26 · h2 17 · h3 12.5 · body 10.5 · small 9 · caption 8). Fuentes embebidas: Libre Franklin, Source Sans 3, IBM Plex Mono.
- Color directo de `tokens.json` (HEX). `shadow.print = none`.
- Tablas: header `table.header`, alternancia `table.rowAlt`, alineación numérica a la derecha, caption de base/fuente obligatorio.
- Mapas: exportar la capa cartográfica real (GeoJSON Barrios CABA — Buenos Aires Data) con relleno tenue + halos; incluir disclaimer y fuente al pie.

## 5. Mapear tokens a DOCX / Google Docs

- Definir **estilos de párrafo** equivalentes a la escala:
  - `Title` → `type.h1` · `Heading 1` → `type.h2` · `Heading 2` → `type.h3` · `Normal` → `type.body` · `Caption` → `type.small`/`caption`.
- **Fuentes con equivalentes seguros** (`typography.family.*.fallbackDocx`): Libre Franklin → Arial; Source Sans 3 → Calibri; IBM Plex Mono → Consolas.
- Color de fuente y sombreado de celda desde los mismos HEX.
- Chips de estado → celda/recuadro con `state[x].bg` + texto `state[x].text` (el color no debe ser el único portador del significado: mantener la etiqueta textual).
- Tablas nativas de Word/Docs con fila de encabezado sombreada `brand.primary` y texto claro.
- Márgenes de documento 2,0–2,2cm (≈ A4 del sistema).

## 6. Qué NO aplicar todavía

- ❌ No generar el informe final de Cafecito ni de PolosGastro.
- ❌ No aplicar el diseño a ningún informe real en esta etapa.
- ❌ No reescribir contenido ni recalcular datos.
- ❌ No cambiar la clasificación ni el orden de los polos.
- ❌ No dibujar límites oficiales de polos.
- ❌ No incorporar Google Places.
- ❌ No exponer material interno/no publicable en salidas públicas.

Alcance de esta entrega: **construir el sistema y sus componentes**, listos para que un paso posterior —con aprobación humana— los aplique a un informe concreto.
