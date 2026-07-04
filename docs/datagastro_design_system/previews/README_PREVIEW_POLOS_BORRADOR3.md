# README - Preview minima controlada: Polos Borrador 3 + Design System DGDGAS

Fecha: 2026-07-01. Documento interno. La preview NO es informe final, NO aplica diseno al Borrador
3 real y NO canoniza tokens.

## Ubicacion de la preview

- HTML: `outputs/datagastro_design_system/previews/polos_borrador3_preview_minima/preview_polos_borrador3_design_system.html`
- CSS: `outputs/datagastro_design_system/previews/polos_borrador3_preview_minima/preview_styles.css`

Es un prototipo HTML estatico de 3 paginas A4 simuladas (portada, tabla ejecutiva, capa objetiva
como contexto). Se abre en cualquier navegador, sin dependencias, sin webfonts descargadas, sin
JavaScript y sin conexion.

## Que se probo

1. **Portada institucional DGDGAS** con marca publica (DGDGAS - Direccion General de Desarrollo Gastronomico),
   panel oscuro `brand.primary_dark`, filete de acento y caja de alcance con la leyenda "no es
   informe final, no delimita oficialmente polos". DataGastro no aparece como marca publica.
2. **TablaPolos con chips de estado** sobre 8 casos reales del Borrador 3 (Palermo agrupado,
   Recoleta, San Telmo, Puerto Madero, Barrio Chino, Avenida Corrientes, Abasto, Bajo Belgrano),
   con columnas caso / grupo / tipo territorial / estado documental / lectura prudente, zebra
   striping, header azul institucional y caption de fuente con fecha de corte.
3. **Capa objetiva como contexto** con caja "Alcance / advertencia", cuatro ejemplos de lectura
   (Palermo, Recoleta, Abasto, corredores), placeholder de mapa sin geometria y la frase
   obligatoria de alcance.
4. **Cinta de preview** en las tres paginas ("preview de diseno - documento simulado - no es
   informe final") y footer con patron `DGDGAS - {proyecto} - {tipo}` y folio.

## Que tokens se usaron

Todos provienen de `docs/datagastro_design_system/tokens/design_tokens_dgdgas_claude_design_mapped_v1.json`
(mapeo experimental v1), declarados como CSS custom properties en `preview_styles.css`:

- **Marca:** `brand.primary` #1F3B57, `brand.primary_dark` #16293D, `brand.secondary` #2C7FB8,
  `brand.accent` #C0762B (solo filetes y titulos de nota metodologica).
- **Texto:** `text.primary/secondary/muted/on_brand/on_brand_soft/table`.
- **Superficies:** `surface.page/card/warm/warn/zebra/desk` (desk solo como fondo de pantalla).
- **Bordes:** `border.subtle/strong/soft`.
- **Estados (chips):** `experimental_claude_design.state_details` para fuerte, media, debil y
  enEspera (dot + text + bg + border); `status.context` para el chip de capa objetiva (sin
  state_details en el mapeo, se derivo un fondo claro coherente - a revisar).
- **Tipografia:** familias `head/body/mono` con fallback seguro (Libre Franklin -> Arial;
  Source Sans 3 -> Calibri/Segoe UI; IBM Plex Mono -> Consolas). No se descargan fuentes.
- **Escala:** display 26pt, h1 17pt, h2 12.5pt, body 10.5pt, small 9pt, caption 8pt.
- **Layout:** A4 vertical 210x297 mm, margenes 20 mm laterales / 22 mm verticales.
- **Radios:** sm 2px, md 4px, chips 3px (`chip.shape_radius`).
- **Sombra:** `shadow.screen` solo en pantalla; `@media print` la elimina (`shadow.print = none`).
- **Mapa:** `map.land_fill` #EAEDF0 solo como fondo del placeholder.

## Que componentes propuestos se probaron

De `COMPONENTES_PROPUESTA_AMPLIACION_CLAUDE_DESIGN_V1.md`:

- **TablaPolos** (parcial): columnas semanticas, sin ranking, con lectura prudente por fila.
- **EstadoChip / chips de estado metodologico**: punto + etiqueta textual obligatoria, tamano
  tabla; estados fuerte, media, debil, en espera y contexto.
- **AlcanceAdvertencia**: caja con severidad "requiere validacion" (surface.warn +
  status.validation), sin rojo de alerta.
- **Caja de lectura** (box.reading) para "como leer esta tabla".
- **Nota de alcance de portada** (variante de AlcanceAdvertencia sobre surface.warm).
- **MapaContexto**: solo como placeholder textual con disclaimer; sin geometria, sin halos, sin
  puntos, sin fuente cartografica inventada.

## Que NO se aplico

- No se modifico el Borrador 3 ni ningun documento de PolosGastro.
- No se tocaron tokens canonicos (`design_tokens_dgdgas.json` / `.yaml`) ni
  `style_tokens_dgdgas.py` ni scripts productivos.
- No se genero PDF, DOCX, mapa real, grafico ni dashboard.
- No se usaron halos de mapa, poligonos ni delimitaciones.
- No se uso el indice numerico de senal objetiva (solo niveles cualitativos en texto).
- No se ordeno ningun contenido por senal objetiva.
- No se uso Google Places ni ninguna fuente externa; no hay credenciales, place_id ni datos crudos.
- No se instalaron dependencias ni se descargaron fuentes.

## Limitaciones

- Es una simulacion de pantalla: el paginado real de PDF/DOCX (via scripts productivos) puede
  diferir en corte de pagina, interlineado y densidad de tabla.
- Las tipografias objetivo (Libre Franklin, Source Sans 3, IBM Plex Mono) probablemente no esten
  instaladas; lo que se ve es el fallback (Arial/Calibri/Segoe UI/Consolas). La decision tipografica
  final requiere ver ambas variantes.
- El chip "contexto" y el chip "no calculable" no tienen `state_details` propios en el mapeo v1;
  se resolvieron con derivaciones ad hoc que habria que tokenizar si se canoniza.
- Solo se probaron 5 de los estados; faltan validacion, interno, alerta, anexo y no_delimita.
- La tabla usa 8 filas; el comportamiento con 32 filas (quiebre de pagina, zebra larga, chips
  repetidos) no esta probado.
- No se probo accesibilidad formal (contraste AA medido, lectores de pantalla) mas alla de
  etiquetas textuales obligatorias y aria-labels basicos.

## La preview demuestra que el Design System sirve?

**Si, para el proposito evaluado.** Los tokens mapeados alcanzan para componer una pieza
institucional sobria, con jerarquia clara y lenguaje prudente integrado al diseno (cinta de
preview, cajas de alcance, chips con texto). No aparecieron huecos estructurales graves: colores,
escala, superficies y estados cubren las tres paginas sin inventar valores fuera del mapeo, con
las dos excepciones menores anotadas (chip contexto y chip no calculable).

## Ajustes visuales recomendados antes de canonizar

1. Agregar `state_details` para `contexto`, `no_delimita`, `validacion`, `interno`, `alerta` y
   `anexo` (hoy solo los estados de documentacion tienen dot/text/bg/border completos).
2. Definir un token para la cinta/preview o marca de estado del documento (borrador, preview,
   final), que hoy es un patron ad hoc.
3. Decidir tipografias: confirmar fallback como definitivo o autorizar instalacion de fuentes
   (queda fuera del alcance de esta preview).
4. Probar la tabla completa de 32 filas y el corte de pagina antes de definir `table.font_size`
   y paddings canonicos.
5. Verificar contraste AA de `text.on_brand_soft` sobre `brand.primary` en cuerpos chicos y de los
   textos de chip sobre sus fondos.
6. Mantener la regla "sin halos ni poligonos" como token/regla explicita de mapa (hoy es solo
   documental).
