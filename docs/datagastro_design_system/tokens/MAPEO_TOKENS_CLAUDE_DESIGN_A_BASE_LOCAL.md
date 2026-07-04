# Mapeo tokens Claude Design a base local - DGDGAS Informes v1

Fecha de revision: 2026-07-01.

Alcance:

- Entrada Claude Design: `docs/datagastro_design_system/claude_design_export_v1/tokens.json`.
- Base local canonica: `docs/datagastro_design_system/tokens/design_tokens_dgdgas.json`.
- Salida experimental: `docs/datagastro_design_system/tokens/design_tokens_dgdgas_claude_design_mapped_v1.json`.

Este documento no reemplaza tokens canonicos. Define una equivalencia de trabajo
para evaluar una posible adopcion futura. DGDGAS sigue siendo la marca publica;
DataGastro queda solo como nombre interno del sistema/metodologia.

## 1. Criterio de mapeo

El export de Claude Design tiene mas metadata por token: `value`, `use`,
fallbacks, unidades mixtas y estados con `dot/text/bg/border`. La base local
espera una estructura mas simple, consumida por `style_tokens_dgdgas.py`:

- Colores como strings HEX bajo `color.<grupo>.<nombre>`.
- Tipografia en `typography.family`, `typography.role`, `typography.scale`.
- Layout en `layout.page`, `layout.margin_mm`, `layout.margin_frac`.
- Cajas en `box.<tipo>`.
- Estados publicables en `content_states.<estado>`.

Por eso el archivo experimental conserva la forma local y guarda lo nuevo como
extension, sin modificar scripts.

## 2. Equivalencias token por token

### Metadatos

| Claude Design | Valor Claude Design | Local equivalente | Valor local | Accion | Observacion |
| --- | --- | --- | --- | --- | --- |
| `$system` | `DGDGAS Informes - Design System` | `meta.system` | `DGDGAS Informes` | adaptar | Mantener nombre local breve y declarar origen en metadata experimental. |
| `$version` | `1.0.0` | `meta.version` | `1.0.0` | adoptar | Coincide. |
| `$publicBrand` | `DGDGAS - Direccion General de Desarrollo Gastronomico` | `meta.marca_publica` | `DGDGAS - Direccion General de Desarrollo Gastronomico` | adoptar | Coincide conceptualmente; normalizar guion/acentos segun salida. |
| `$internalName` | `DataGastro` | `meta.nombre_interno` | `DataGastro` | adoptar | Solo uso interno. |
| `$notes` | Regla de marca, unidades y no delimitaciones | `meta.descripcion` / documentacion | Descripcion local | adaptar | Es una nota metodologica, no un token operativo. |

### Marca y color principal

| Claude Design | Valor Claude Design | Local equivalente | Valor local | Accion | Observacion |
| --- | --- | --- | --- | --- | --- |
| `color.brand.primary.value` | `#1F3B57` | `color.brand.primary` | `#1F3B57` | adoptar | Coincidencia directa. |
| `color.brand.primaryDark.value` | `#16293D` | `color.brand.primary_dark` | No existe | adaptar | Util para fondos oscuros; agregar solo como extension experimental. |
| `color.brand.secondary.value` | `#2C7FB8` | `color.brand.secondary` | `#2C7FB8` | adoptar | Coincidencia directa. |
| `color.brand.accent.value` | `#C0762B` | `color.brand.accent` | `#C0762B` | adoptar | Coincidencia directa; uso moderado. |

### Texto, superficies y lineas

| Claude Design | Valor Claude Design | Local equivalente | Valor local | Accion | Observacion |
| --- | --- | --- | --- | --- | --- |
| `color.ink.base.value` | `#1B2733` | `color.text.primary` | `#222222` | adaptar | Mejora la pertenencia visual; probar legibilidad en DOCX/PDF. |
| `color.ink.muted.value` | `#566573` | `color.text.secondary` | `#555555` | adaptar | Muy cercano; adoptable si pasa contraste. |
| `color.ink.faint.value` | `#8A97A3` | `color.text.muted` | `#777D86` | adaptar | Mas tenue; usar para captions/metadatos. |
| `table.header.text` | `#EAF0F5` | `color.text.on_brand_soft` | No existe | adaptar | Puede convivir con `text.on_brand = #FFFFFF`. |
| `color.surface.paper.value` | `#FFFFFF` | `color.surface.page` | `#FFFFFF` | adoptar | Coincide. |
| `color.surface.base.value` | `#F4F6F8` | `color.surface.card` / `surface.note` | `#EEF2F6` / `#EAF1F8` | adaptar | Unifica cajas frias; requiere preview. |
| `color.surface.warm.value` | `#F6F4EF` | `color.surface.warn` o nuevo `surface.warm` | `#F7EBDC` | adaptar | Mejor para nota metodologica, no para alerta. |
| `color.surface.subtle.value` | `#FAFBFC` | `color.surface.zebra` | `#F4F7FA` | adaptar | Alternancia mas tenue. |
| `color.surface.desk.value` | `#E7EAED` | `color.surface.desk` | No existe | descartar por ahora | Solo pantalla/previews, no necesario para informes. |
| `color.line.base.value` | `#DDE3E9` | `color.border.subtle` | `#D9DEE5` | adaptar | Diferencia menor. |
| `color.line.strong.value` | `#C4CDD6` | `color.border.strong` | `#B8C2CE` | adaptar | Algo mas suave que local. |
| `color.line.soft.value` | `#EDF1F4` | `color.border.soft` | No existe | adaptar | Util para divisores internos de tabla. |

### Estados y evidencia

| Claude Design | Valor Claude Design | Local equivalente | Valor local | Accion | Observacion |
| --- | --- | --- | --- | --- | --- |
| `state.fuerte.dot` | `#2F6E5B` | `color.status.strong` | `#1A9850` | adaptar | Menos saturado; recomendable para evidencia fuerte. |
| `state.media.dot` | `#2C6E9E` | `color.status.medium` / `review` | `#C0762B` / `#2C7FB8` | adaptar | Separar evidencia media de acento calido. |
| `state.debil.dot` | `#9A6B1E` | `color.status.weak` | `#B0403A` | adoptar criterio | Evita rojo para documentacion debil. |
| `state.pendiente.dot` | `#5E6B78` | `color.status.pending` | `#8A6D3B` | adaptar | Pendiente neutro, no alarmista. |
| `state.validacion.dot` | `#A85B2A` | `color.status.validation` | No existe | adoptar | Diferenciar "pendiente" de "requiere validacion". |
| `state.enEspera.dot` | `#8A97A3` | `content_states.en_espera` | No existe | adoptar | Usar como lenguaje publico para casos sin evidencia suficiente. |
| `state.contexto.dot` | `#3F7A86` | `content_states.contexto` | No existe | adoptar | Util para capas objetivas de contexto. |
| `state.noDelimita.dot` | `#A85B2A` | `content_states.no_delimita` | No existe | adaptar | Util en mapas; no saturar fichas ejecutivas. |
| `state.anexo.dot` | `#6B7280` | `content_states.anexo` | `text.muted` | adaptar | Compatible. |
| `state.interno.dot` | `#4A5568` | `content_states.interno` | `text.muted` | adaptar | Mantener como no publicable. |
| `state.alerta.dot` | `#A23A2C` | `content_states.advertencia` | `status.medium` | adaptar | Reservar solo para advertencias reales. |

### Tipografia

| Claude Design | Valor Claude Design | Local equivalente | Valor local | Accion | Observacion |
| --- | --- | --- | --- | --- | --- |
| `typography.family.head.value` | `Libre Franklin` | `typography.family.head` | No existe | adaptar | Usar con fallback a Arial/Franklin Gothic. |
| `typography.family.body.value` | `Source Sans 3` | `typography.family.body` / `sans` | `DejaVu Sans, Arial...` | adaptar | No depender de fuente instalada. |
| `typography.family.mono.value` | `IBM Plex Mono` | `typography.family.mono` | `DejaVu Sans Mono, Consolas...` | adaptar | Mantener fallback Consolas/Courier New. |
| `typography.size.h1.pt` | `26` | `typography.scale.display` | `26` | adoptar | Equivale a portada/display local. |
| `typography.size.h2.pt` | `17` | `typography.scale.h1` | `15` | adaptar | Titulo de seccion, probar densidad en A4. |
| `typography.size.h3.pt` | `12.5` | `typography.scale.h2` | `12` | adaptar | Diferencia menor. |
| `typography.size.body.pt` | `10.5` | `typography.scale.body` | `9.5` | adaptar | Mejora lectura, pero puede aumentar paginas. |
| `typography.size.small.pt` | `9` | `typography.scale.small` | `8.6` | adaptar | Diferencia menor. |
| `typography.size.caption.pt` | `8` | `typography.scale.caption` | `7.9` | adoptar | Casi igual. |
| `typography.weight.*` | `400/500/600/700` | `typography.weight.*` | `normal/bold` | mantener local | Scripts actuales no usan pesos numericos. |

### Pagina, espaciado y radios

| Claude Design | Valor Claude Design | Local equivalente | Valor local | Accion | Observacion |
| --- | --- | --- | --- | --- | --- |
| `page.size` | `A4` | `layout.page.size` | `A4` | adoptar | Coincide. |
| `page.orientation` | `portrait` | `layout.page.orientation` | `portrait` | adoptar | Coincide. |
| `page.marginTop` | `22mm` | `layout.margin_mm.top` | `22` | adoptar | Coincide. |
| `page.marginBottom` | `22mm` | `layout.margin_mm.bottom` | `20` | adaptar | Aumenta margen inferior. |
| `page.marginLeft` | `20mm` | `layout.margin_mm.left` | `20` | adoptar | Coincide. |
| `page.marginRight` | `20mm` | `layout.margin_mm.right` | `20` | adoptar | Coincide. |
| `page.grid.columns` | `12` | `layout.grid.columns` | No existe | adaptar | Solo como guia de layout futura. |
| `space.xs` | `4px` | `spacing.xs` | `4` | adoptar | Coincide. |
| `space.sm` | `8px` | `spacing.sm` | `8` | adoptar | Coincide. |
| `space.md` | `16px` | `spacing.md` | `12` | adaptar | Aumenta aire entre bloques. |
| `space.lg` | `24px` | `spacing.lg` | `16` | adaptar | Puede mejorar lectura, pero cambia paginado. |
| `space.xl` | `32px` | `spacing.xl` | `24` | adaptar | Revisar en preview. |
| `space.xxl` | `48px` | `spacing.xxl` | `32` | adaptar | Revisar en portada/separadores. |
| `radius.sm` | `2px` | `radius.sm` | `3` | adaptar | Compatible con criterio sobrio. |
| `radius.md` | `4px` | `radius.md` | `6` | adaptar | No superar 4px si se adopta Claude Design. |
| Sin equivalente | No superar 4px | `radius.lg` / `radius.pill` | `10` / `999` | mantener local por ahora | No usar en documentos sin preview. |

### Tablas y chips

| Claude Design | Valor Claude Design | Local equivalente | Valor local | Accion | Observacion |
| --- | --- | --- | --- | --- | --- |
| `table.header.bg` | `#1F3B57` | `table.header_fill` | `border.strong` | adaptar | Conviene pasar header a `brand.primary`. |
| `table.header.text` | `#EAF0F5` | `table.header_text` | `text.on_brand` | adaptar | Usar `text.on_brand` o nuevo `text.on_brand_soft`. |
| `table.cell.text` | `#3C4B59` | `color.text.table` | No existe | adaptar | Puede quedar como extension futura. |
| `table.rowDivider.color` | `#EDF1F4` | `table.border` | `border.subtle` | adaptar | Usar `border.soft` experimental. |
| `table.rowAlt.bg` | `#FAFBFC` | `table.row_fill_alt` | `surface.zebra` | adaptar | Equivalencia directa si `surface.zebra` cambia. |
| `table.caption.*` | mono, 11px, `#8A97A3` | caption local | Parcial | adaptar | Requiere soporte en componentes/render. |
| `chip.shape.*` | radio, padding, gap | Sin equivalente local | No existe | adaptar | Guardar como extension experimental, sin usar en scripts actuales. |
| `chip.dot.*` | tamanio y radio | Sin equivalente local | No existe | adoptar mas adelante | Necesita componente `EstadoChip`. |

### Mapas

| Claude Design | Valor Claude Design | Local equivalente | Valor local | Accion | Observacion |
| --- | --- | --- | --- | --- | --- |
| `map.barrioFill.value` | `#EAEDF0` | `map.land_fill` | `#F3F5F8` | adaptar | Barrios/comunas mas visibles pero tenues. |
| `map.canvasBg.value` | `#FAFBFC` | `map.legend_fill` / fondo | `surface.page` | adaptar | Usar como fondo de mapa, no de pagina. |
| `map.haloNucleo.*` | Gradiente / dot `#1F3B57` | Sin equivalente | No existe | dejar para despues | Requiere backend visual y QA. |
| `map.haloRelevante.*` | Gradiente / dot `#2C7FB8` | Sin equivalente | No existe | dejar para despues | Riesgo de parecer area oficial. |
| `map.haloEmergente.*` | Gradiente / dot `#C0762B` | Sin equivalente | No existe | dejar para despues | Usar solo con disclaimer. |
| `map.enEsperaDot.*` | punto transparente con borde punteado | Sin equivalente | No existe | adoptar mas adelante | Util para casos sin evidencia suficiente. |
| `map.disclaimer.text` | Referencia territorial, no delimita oficialmente | `map.scope_note_required` | `true` | adoptar | Convertir en texto obligatorio de mapa. |
| `map.sourceCaption.text` | Base cartografica BA Data, no delimitacion oficial | Nota de fuente | Parcial | adoptar | No inventar fuentes; usar solo si la base real es esa. |
| `map.$rules` | Reglas de cartografia | QA/documentacion | Parcial | adoptar | Especialmente no usar Google Places como base publica. |

## 3. Tokens de Claude Design con equivalente local

- `color.brand.primary.value` -> `color.brand.primary`.
- `color.brand.secondary.value` -> `color.brand.secondary`.
- `color.brand.accent.value` -> `color.brand.accent`.
- `color.surface.paper.value` -> `color.surface.page`.
- `color.surface.subtle.value` -> `color.surface.zebra`.
- `page.size` -> `layout.page.size`.
- `page.orientation` -> `layout.page.orientation`.
- `page.marginTop`, `page.marginLeft`, `page.marginRight` -> `layout.margin_mm.*`.
- `space.xs`, `space.sm` -> `spacing.xs`, `spacing.sm`.
- `typography.size.h1.pt` -> `typography.scale.display`.
- `typography.size.caption.pt` -> `typography.scale.caption`.
- `state.anexo` -> `content_states.anexo`.
- `state.interno` -> `content_states.interno`.

## 4. Tokens nuevos recomendados

- `color.brand.primary_dark`.
- `color.border.soft`.
- `color.text.on_brand_soft`.
- `color.status.validation`.
- `color.status.waiting`.
- `color.status.context`.
- `color.status.no_delimita`.
- `color.status.internal`.
- `color.status.alert`.
- `content_states.en_espera`.
- `content_states.contexto`.
- `content_states.no_delimita`.
- `content_states.validacion`.
- `experimental_claude_design.state_details`.
- `experimental_claude_design.chip`.
- `experimental_claude_design.shadow`.
- `experimental_claude_design.map_halos`.
- `layout.grid`.

## 5. Tokens locales que no aparecen en Claude Design

- `color.surface.ok`: el export usa estados positivos por `state.fuerte.bg`,
  pero no define una superficie generica `ok`.
- `color.chart.sequence`, `color.chart.grid`, `color.chart.empty`: el export no
  define una paleta de graficos general.
- `typography.family.serif`: el export no usa serif.
- `typography.scale.footer`: no tiene token explicito de footer.
- `layout.page.dpi`: el export no fija DPI.
- `layout.margin_frac`: el export trabaja con mm.
- `layout.content_width_frac`: el export usa grilla de 12 columnas.
- `radius.none`, `radius.lg`, `radius.pill`: el export restringe radios.
- `box.question`, `box.reading`, `box.method`, `box.warning`, `box.validation`:
  el export describe componentes, pero no define `box.*`.
- `footer.*`: el export no trae patron de footer local.
- `content_states.principal`, `secundario`, `preliminar`, `historico`: el
  export propone otro vocabulario.

## 6. Conflictos de nombres

- `typography.size.h1` en Claude Design equivale a portada/display local, no
  necesariamente a `typography.scale.h1`.
- `state.pendiente` no es lo mismo que `content_states.pendiente` local, que hoy
  se rotula como "Requiere validacion".
- `state.alerta` no debe reemplazar automaticamente `advertencia metodologica`;
  en Claude Design queda reservado para advertencias reales.
- `color.surface.base` puede mapear a `surface.card` o `surface.note` segun
  componente. No es una equivalencia unica.
- `color.line.*` equivale a `color.border.*`, pero cambia nombres y jerarquia.
- `table.header` en Claude Design es un objeto; en local es referencia
  semantica simple.

## 7. Conflictos de estructura

- Claude Design guarda colores como objetos con `value` y `use`; local espera
  strings HEX.
- Claude Design guarda unidades con sufijo (`px`, `mm`); local espera numeros
  en varios campos.
- Claude Design separa `page`, `space`, `state`, `chip`, `shadow`; local usa
  `layout`, `spacing`, `content_states`, sin chip ni shadow.
- Los scripts actuales no resuelven `state.<estado>.bg` ni `chip.*`.
- El backend actual no interpreta gradientes de mapa ni sombras de pantalla.

## 8. Recomendacion de adopcion

| Grupo | Recomendacion | Motivo |
| --- | --- | --- |
| Marca publica / nombre interno | Adoptar | Coincide con guardrails: DGDGAS publico, DataGastro interno. |
| Paleta brand | Adoptar | Coincide casi completo. |
| Texto, superficies y lineas | Adaptar | Mejora finura visual, pero requiere preview de contraste. |
| Tipografia | Adaptar | Usar fallbacks; no depender de fuentes no instaladas. |
| Espaciado/radios | Adaptar | Puede cambiar paginado y densidad. |
| Estados metodologicos | Adoptar con mapeo | Aporta lenguaje publico prudente y evita descarte tajante. |
| Chips | Dejar para despues | Necesitan componente y render. |
| Mapas con halos | Dejar para despues | Riesgo de interpretacion como delimitacion oficial. |
| Shadow | Mantener como regla | `shadow.print = none`; no incorporar sombras a PDF/DOCX. |
| Tokens locales de chart/footer/box | Mantener local | Son necesarios para scripts actuales. |

## 9. Riesgos

- Romper compatibilidad si se reemplaza `design_tokens_dgdgas.json`.
- Cambiar semantica de estados sin migrar templates y componentes.
- Aumentar tipografia/espaciado y alterar paginado de informes.
- Usar halos de mapa sin disclaimer y generar lectura de delimitacion oficial.
- Usar `alerta` como color de evidencia debil; debe quedar para advertencias
  reales.
- Exponer DataGastro como marca publica si se copian textos internos sin QA.
- Transformar informes territoriales en rankings si se ordenan polos por puntaje
  o color en vez de grupo/evidencia.
- Incorporar fuentes privadas o Google Places en mapas; no corresponde como
  base publica.

## 10. Estado recomendado

Todavia no estamos listos para actualizar tokens canonicos. El proximo paso
seguro es revisar el JSON experimental, validar equivalencias con una preview
controlada y recien despues decidir una actualizacion canonica.
