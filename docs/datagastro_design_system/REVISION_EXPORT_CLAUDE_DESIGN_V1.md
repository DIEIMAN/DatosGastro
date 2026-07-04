# Revision export Claude Design - DGDGAS Informes Design System v1

Fecha de revision: 2026-07-01.

Alcance revisado:

- `docs/datagastro_design_system/claude_design_export_v1/`
- `docs/datagastro_design_system/`
- `docs/datagastro_design_system/tokens/`
- `docs/datagastro_design_system/templates/`
- `scripts/shared/reporting_dgdgas/`

No se aplico el diseno a ningun informe. No se modificaron scripts productivos,
templates canonicos, informes finales, datos fuente ni carpetas de proyectos.

## 1. Archivos importados

Se creo la carpeta:

- `docs/datagastro_design_system/claude_design_export_v1/`

Archivos copiados desde el handoff local disponible en
`docs/datagastro_design_system/Sistema de diseño DGDGAS/handoff/`:

| Archivo | Estado | Observacion |
| --- | --- | --- |
| `tokens.json` | Importado | Tokens exportados por Claude Design. |
| `COMPONENTES_DGDGAS_DESIGN_SYSTEM.md` | Importado | Catalogo de componentes propuesto por Claude Design. |
| `HANDOFF_CLAUDE_CODE_DGDGAS_DESIGN_SYSTEM.md` | Importado | Guia de implementacion propuesta por Claude Design. |
| `DGDGAS Informes - Design System v1.pdf` | No disponible | No se encontro con ese nombre en el handoff local revisado; no se genero PDF. |

No se crearon copias comparativas adicionales en `tokens/` ni se reemplazaron
archivos canonicos. La carpeta importada queda como insumo versionable y
auditable.

## 2. Diferencias entre tokens locales y tokens de Claude Design

### Estructura general

| Tema | Base local | Export Claude Design | Impacto |
| --- | --- | --- | --- |
| Metadatos | `meta.system`, `meta.version`, `meta.marca_publica`, `meta.nombre_interno` | `$system`, `$version`, `$publicBrand`, `$internalName`, `$notes` | Requiere adaptador; los scripts actuales no leen claves con `$`. |
| Colores | `color.brand.primary = "#1F3B57"` | `color.brand.primary.value = "#1F3B57"` y `use` | El valor principal coincide en marca, pero cambia el esquema de acceso. |
| Texto y superficies | `color.text.*`, `color.surface.*`, `color.border.*` | `color.ink.*`, `color.surface.*`, `color.line.*` | Hay equivalencias, pero no son nombres compatibles uno a uno. |
| Tipografia | `typography.scale.*`, `family.sans/serif/mono` | `typography.size.*.pt/px`, `family.head/body/mono` con `fallbackDocx` | Mejor documentacion de fallback en el export; requiere mapeo para scripts. |
| Pagina | `layout.page`, `layout.margin_mm`, `layout.margin_frac` | `page.size`, `page.marginTop`, `page.grid` | Local esta mejor alineado a scripts; export agrega grilla de 12 columnas. |
| Espaciado | `spacing.xs = 4`, `md = 12`, `xxl = 32` | `space.xs = "4px"`, `md = "16px"`, `xxl = "48px"` | Cambian unidades y escala media/larga; no adoptar sin revisar layout real. |
| Radios | `sm = 3`, `md = 6`, `lg = 10`, `pill = 999` | `sm = "2px"`, `md = "4px"`, nota: no superar 4px | Conviene adoptar el criterio sobrio, no necesariamente la estructura cruda. |
| Tablas | Header por referencia semantica `border.strong`; filas `surface.zebra` | Header azul `#1F3B57`, captions y divisores mas definidos | Export mejora la tabla, pero debe traducirse a tokens semanticos locales. |
| Cajas | `box.question`, `box.reading`, `box.method`, `box.warning`, `box.validation` | No tiene bloque `box`; reparte estilo entre `border`, `surface`, `state` y componentes | Los scripts actuales dependen de `box.*`; no se puede reemplazar directo. |
| Estados | `content_states.*` simple, color + label | `state.*` completo, dot/text/bg/border/label | Export es mas rico y mas util para chips, pero rompe `content_state()`. |
| Mapas | Tierra, agua, bordes, puntos, choropleth, `scope_note_required` | Barrios tenues, halos, disclaimer, fuente cartografica y reglas explicitas | Conviene adoptar reglas y disclaimer; adaptar halos a backend futuro. |
| Sombras | No definido | `shadow.print = none`, sombra solo pantalla | Adoptable como regla de QA visual. |

### Valores coincidentes o cercanos

- Marca principal: `#1F3B57`.
- Marca secundaria: `#2C7FB8`.
- Acento: `#C0762B`.
- Pagina A4 vertical.
- Margenes laterales de 20 mm.
- Criterio de marca publica DGDGAS y nombre interno DataGastro.

### Diferencias criticas para implementacion

- `style_tokens_dgdgas.py` espera colores como strings directos bajo
  `color.<grupo>.<nombre>`. El export usa objetos con `value` y `use`.
- `Tokens.font_size()` espera `typography.scale.<rol>`. El export usa
  `typography.size.<rol>.pt`.
- `Tokens.box_style()` espera `box.<kind>`. El export no define `box.*`.
- `Components.estado_documentacion()` espera `content_states.<estado>`. El
  export usa `state.<estado>` con otra taxonomia.
- El export mezcla unidades `px`, `pt` y `mm`; la base local usa numeros para
  render documental y referencias semanticas.

Conclusion: los tokens de Claude Design no conviene reemplazarlos de forma
directa. Si se adoptan, primero hay que crear una capa de mapeo o transformar
el export al esquema local.

## 3. Diferencias de nombres de estados metodologicos

### Base local

Estados actuales en `content_states`:

- `principal` - Resultado principal.
- `secundario` - Resultado secundario.
- `preliminar` - Preliminar.
- `pendiente` - Requiere validacion.
- `anexo` - Anexo.
- `advertencia` - Advertencia metodologica.
- `interno` - Uso interno.
- `historico` - Referencia historica.

### Export Claude Design

Estados propuestos en `state`:

- `fuerte` - Documentacion fuerte.
- `media` - Documentacion media.
- `debil` - Documentacion debil.
- `pendiente` - Pendiente.
- `validacion` - Requiere validacion.
- `enEspera` - En espera de evidencia.
- `contexto` - Capa objetiva de contexto.
- `noDelimita` - No delimita oficialmente.
- `anexo` - Anexo / caso secundario.
- `interno` - Insumo interno / no publicable.
- `alerta` - Advertencia real, solo para advertencias reales.

### Lectura comparativa

- La base local mezcla jerarquia de resultado (`principal`, `secundario`) con
  estado de documento (`preliminar`, `pendiente`).
- El export separa mejor madurez de evidencia, uso interno, contexto territorial
  y advertencia real.
- El export incorpora explicitamente `enEspera`, que resuelve el punto sensible:
  no usar "Dejar afuera" como lenguaje publico.
- `alerta` queda reservado para advertencias reales y no para documentacion
  debil; esta distincion conviene adoptarla.
- `noDelimita` es util para mapas y fichas territoriales, pero debe usarse con
  cuidado para no saturar documentos ejecutivos.

Recomendacion: mantener temporalmente `content_states` por compatibilidad, pero
agregar una tabla de equivalencias hacia `state` antes de tocar scripts:

| Local | Claude Design sugerido | Comentario |
| --- | --- | --- |
| `principal` | `fuerte` | Solo cuando la evidencia sea efectivamente fuerte. |
| `secundario` | `media` o `contexto` | Segun sea apoyo documental o capa objetiva. |
| `preliminar` | `pendiente` | Si falta cierre metodologico. |
| `pendiente` | `validacion` | Cuando requiere confirmacion activa. |
| Sin equivalente | `enEspera` | Incorporar para casos sin evidencia suficiente. |
| `advertencia` | `alerta` o `validacion` | Usar `alerta` solo ante riesgo real. |
| `interno` | `interno` | Mantener como no publicable. |
| `anexo` | `anexo` | Compatible en concepto. |
| `historico` | `contexto` o `anexo` | Definir segun uso editorial. |

## 4. Diferencias de componentes

### Componentes en comun

- Portada.
- Indice.
- Ficha de relevamiento / datos generales.
- Pregunta analizada.
- Lectura de resultados.
- Nota metodologica.
- Tabla institucional.
- Tabla de polos.
- Ficha de polo.
- Mapa territorial / mapa de contexto.
- Requiere validacion.
- Estado de documentacion.
- Anexo metodologico / anexo.

### Componentes locales que no aparecen igual en el export

- Pagina con grafico.
- Grafico de barras como componente principal.
- Pagina de sintesis.
- Pagina de aspectos a considerar.
- Bloque de alcance / advertencia.
- Plantillas de pagina P0-P10.
- Contrato Python de `Canvas` y specs estructuradas en `Components`.

### Componentes del export que enriquecen la base local

- `QueHabilita`: explicita que decision o mejora habilita el relevamiento y que
  no habilita.
- `FuenteEvidencia`: lista breve de fuentes por bloque.
- `AlcanceAdvertencia`: disclaimer neutral de alcance.
- `EstadoDocumentacion (EstadoChip)`: chip con dot/text/bg/border y etiqueta
  textual.
- `MapaContexto`: reglas mas estrictas para evitar apariencia de delimitacion
  oficial.

Conclusion: conviene actualizar componentes, pero como ampliacion del catalogo
local y no como reemplazo. La base local ya tiene piezas necesarias para
informes; el export agrega mejores guardrails territoriales y metodologicos.

## 5. Diferencias de estructura sugerida

### Base local actual

- Documentacion en `docs/datagastro_design_system/`.
- Tokens canonicos en `docs/datagastro_design_system/tokens/`.
- Templates de contenido y payload en `docs/datagastro_design_system/templates/`.
- Scripts compartidos en `scripts/shared/reporting_dgdgas/`.
- Estado actual: base reusable y esqueletos, sin render final de PDF/DOCX.

### Export Claude Design

Propone una estructura generica:

- `dgdgas-informes/tokens.json`
- `components/`
- `templates/`
- `export/pdf/`
- `export/docx/`
- `export/gdocs/`

Y sugiere crear o actualizar:

- `TOKENS.md`
- `COMPONENTES.md`
- `GUIA_ESTILO.md`
- `CARTOGRAFIA.md`
- `tokens.py` o `tokens.js`
- `components/`
- `render_pdf.*`
- `render_docx.*`
- `qa_publico.*`

### Lectura

La estructura del export es valida como arquitectura conceptual, pero no debe
implantarse tal cual porque el repo ya tiene una ubicacion mas integrada:
`docs/datagastro_design_system/` y `scripts/shared/reporting_dgdgas/`.

Conviene adoptar la idea de separar guia de estilo, cartografia y QA publico en
documentos especificos, pero preservando la estructura local existente.

## 6. Que conviene adoptar

- Mantener explicitamente que DGDGAS es la marca publica y DataGastro solo el
  nombre interno del sistema/metodologia.
- Adoptar `En espera de evidencia` como lenguaje publico para casos sin
  sustento suficiente, evitando "Dejar afuera".
- Adoptar estados mas expresivos: `fuerte`, `media`, `debil`, `validacion`,
  `enEspera`, `contexto`, `noDelimita`, `interno`, `alerta`.
- Adoptar chips de estado con etiqueta textual obligatoria; el color no debe
  ser el unico portador del significado.
- Adoptar reglas cartograficas del export: barrios/comunas tenues, halos o
  puntos, disclaimer visible, fuente cartografica al pie, sin Google Places.
- Adoptar `QueHabilita`, `FuenteEvidencia` y `AlcanceAdvertencia` como bloques
  utiles para informes ejecutivos prudentes.
- Adoptar fallback tipografico seguro para DOCX/Google Docs, especialmente:
  Libre Franklin a Arial, Source Sans 3 a Calibri/Segoe UI, IBM Plex Mono a
  Consolas/Courier New. Si no se embeben fuentes, los fallbacks deben ser la
  regla operativa.
- Adoptar `shadow.print = none` como criterio para exportacion documental.
- Adoptar la grilla A4 de 12 columnas solo como guia de layout, no como
  dependencia inmediata de scripts.

## 7. Que conviene mantener de la base local

- La estructura actual del repo.
- `tokens/design_tokens_dgdgas.yaml` como fuente de verdad editable y
  `design_tokens_dgdgas.json` como derivado util para scripts.
- El esquema semantico simple de tokens mientras los scripts lo consuman.
- `style_tokens_dgdgas.py`, porque ya resuelve tokens semanticos sin
  dependencias externas.
- `report_components_dgdgas.py`, porque define una API comun y backend-agnostica
  para PDF, DOCX y Google Docs.
- Las plantillas P0-P10, porque el export no reemplaza la logica de pagina.
- La plantilla de contenido YAML, porque separa datos reales de estilo y evita
  hardcodear texto en generadores.
- El checklist QA local, que ya cubre marca, privacidad, mapas, fuentes y no
  exposicion tecnica.

## 8. Que requiere adaptacion antes de implementar

- Crear un mapeo controlado entre `tokens.json` del export y
  `design_tokens_dgdgas.json` local. No reemplazar directo.
- Definir si la fuente canonica seguira siendo YAML local o si el export JSON se
  transformara a YAML local en cada sincronizacion.
- Agregar soporte de tokens con objetos `{ value, use }` solo si se decide
  adoptar el esquema Claude Design.
- Adaptar `Tokens.color()`, `font_size()`, `box_style()` y `content_state()` si
  se incorporan `state.*`, `typography.size.*` y `color.*.value`.
- Traducir `state.*` a `content_states.*` o reemplazar gradualmente el sistema
  de estados, con pruebas.
- Definir unidades por backend: `pt` para documento, `mm` para pagina, `px` solo
  para previews de pantalla.
- Revisar el cambio de escala tipografica: el export propone `h2 = 17 pt` y
  `body = 10.5 pt`; la base local usa `h2 = 12` y `body = 9.5`.
- Revisar radios y espaciado en una preview visual antes de adoptar valores de
  `space` y `radius`.
- Agregar `QueHabilita`, `FuenteEvidencia` y `AlcanceAdvertencia` a
  `report_components_dgdgas.py` solo en una fase posterior autorizada.
- Crear pruebas de carga de tokens y compatibilidad antes de tocar generadores.

## 9. Riesgos detectados

- Reemplazo directo de tokens: alto riesgo de romper `style_tokens_dgdgas.py`,
  porque el formato del export no coincide con el formato local.
- Cambio de estados sin mapeo: riesgo de que informes o templates esperen
  `principal`, `secundario`, `preliminar` y reciban `fuerte`, `media`, `debil`.
- Tipografias del export: Libre Franklin, Source Sans 3 e IBM Plex Mono son
  buenas para identidad, pero pueden no estar disponibles en Word/Google Docs o
  en entornos de render sin instalacion. Los fallbacks deben ser obligatorios.
- Mapas con halos: pueden leerse como areas de influencia si no se aplica el
  disclaimer y un estilo tenue. Requieren QA visual antes de publicar.
- `Google Places`: el export no lo propone como fuente; al contrario, lo
  prohibe como base publica. El riesgo esta en implementaciones futuras que
  ignoren esta regla.
- Rankings: el export aclara que no se generan rankings; debe preservarse para
  PolosGastro y cualquier informe territorial.
- Lenguaje publico: "Dejar afuera" aparece solo como frase a evitar. No debe
  pasar a plantillas ni informes; usar "En espera de evidencia".
- Estructura generica del export: si se copia literalmente, duplicaria la base
  local y crearia dos fuentes de verdad.
- Dependencias: implementar DOCX real requeriria `python-docx`; esta revision no
  instalo dependencias ni genero DOCX.

## 10. Proximos pasos recomendados

1. Mantener `claude_design_export_v1/` como evidencia del handoff recibido.
2. Crear, en una fase posterior, un archivo de mapeo documentado:
   `docs/datagastro_design_system/MAPEO_TOKENS_CLAUDE_DESIGN_V1.md`.
3. Decidir si se adopta el sistema de estados del export y, si se adopta,
   preparar una migracion por compatibilidad:
   `content_states` local -> `state` Claude Design.
4. Agregar primero documentacion canonica nueva, no codigo:
   `CARTOGRAFIA_INFORMES_DGDGAS.md` y una seccion de estados metodologicos.
5. Solo despues, actualizar `style_tokens_dgdgas.py` con pruebas, sin tocar
   informes finales.
6. Incorporar componentes nuevos (`QueHabilita`, `FuenteEvidencia`,
   `AlcanceAdvertencia`) como specs nuevas y no como reemplazo de componentes
   existentes.
7. Preparar una preview visual estatica de componentes antes de aplicar el
   sistema a Cafecito, PolosGastro u otro informe.
8. Repetir QA publico antes de cualquier salida publicable.

## Decision recomendada

No conviene adoptar los tokens de Claude Design por reemplazo directo. Conviene
adoptar su criterio visual y metodologico mediante un mapeo controlado hacia la
base local.

Si se avanza, la ruta prudente es:

1. Preservar la base local como canonica por ahora.
2. Incorporar reglas y estados del export en documentacion.
3. Crear transformador o adaptador de tokens.
4. Actualizar componentes y scripts con pruebas.
5. Recien despues aplicar a un informe concreto, con autorizacion explicita.

## Confirmacion de alcance

- No se aplico el Design System a informes.
- No se tocaron informes finales.
- No se genero PDF.
- No se genero DOCX.
- No se instalaron dependencias.
- No se modificaron datos fuente.
- No se tocaron `data/`, `src/` general, `Cafesito/`, `PolosGastro/`,
  `MercadosGastro/`, `CasasDePastas/` ni DataGastro V2.
- No se hizo commit, push ni staging.
