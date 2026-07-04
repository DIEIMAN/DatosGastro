# DGDGAS Informes — Design System v1 (documento maestro)

Documento de referencia del sistema visual y editorial para informes de la
**Dirección General de Gastronomía (DGDGAS)**. Define marca, tono, estructura,
tokens y reglas de contenido. Es la especificación que implementan los
componentes, plantillas y scripts de este directorio.

---

## 1. Marca

- **Marca pública principal:** `DGDGAS – Dirección General de Gastronomía`.
- **No** usar `DataGastro` como marca pública por defecto. `DataGastro` es el
  nombre interno del sistema/proyecto y solo se nombra en documentación técnica
  cuando corresponde.
- En portada y encabezados, la Dirección debe ser más visible que el nombre
  interno del proyecto.
- Marco institucional sugerido en portada:
  `Gobierno de la Ciudad de Buenos Aires · BA Capital Gastronómica`
  (ajustar según el marco vigente de cada informe).

## 2. Tono

- Institucional, claro, descriptivo, prudente.
- **No** marketinero, sin slogans ni superlativos.
- **No** excesivamente técnico ni con estética de dashboard automático.
- Recomendaciones **en potencial**: «podría», «sería conveniente»,
  «permitiría», «convendría evaluar».
- Separar siempre **hallazgos** de **límites**. No afirmar representatividad si
  el relevamiento no la tiene.

## 3. Estructura base de un informe

1. Portada.
2. Índice (con números de página).
3. Datos generales.
4. Fuente o relevamiento.
5. Preguntas o variables.
6. Resultados.
7. Lectura descriptiva.
8. Síntesis.
9. Aspectos a considerar.
10. Anexos.
11. Nota metodológica breve.

Secciones numeradas. Índice con números de página. Oraciones completas.

## 4. Reglas de contenido

- **Datos duros primero**, interpretación después.
- Preguntas visibles **antes** del análisis cuando hay encuestas.
- Diferenciar tipo de pregunta: **cerrada**, **abierta**, **multi-respuesta**,
  **consentimiento**.
- En multi-respuesta: mostrar **menciones** y aclarar que la suma **puede
  superar 100 %**.
- **No** publicar respuestas individuales ni datos de contacto.
- Notas metodológicas **breves** en el cuerpo; el material secundario va a
  **anexo**.
- Gráficos legibles; cada gráfico con título, base/universo, fuente y lectura
  breve.
- Mapas territoriales **útiles**, no decorativos.

## 5. Cartografía

- **No** representar límites oficiales si no existen.
- Usar **barrios/comunas** como referencia territorial.
- Aclarar cuando un mapa es **conceptual, preliminar o de trabajo**
  (nota de alcance obligatoria).
- Preferir mapas sobrios y legibles. Evitar mapas tipo red o decorativos.
- **No** usar coordenadas ni geometría de plataformas privadas como base
  pública. **No** usar Google Places como fuente pública principal.

## 6. Tokens de diseño

La fuente de verdad son `tokens/design_tokens_dgdgas.yaml` (y su equivalente
`.json`). Aquí se resumen para lectura rápida. **Usar siempre los nombres
semánticos**, no el HEX directo.

### 6.1 Color

| Token semántico    | HEX       | Uso |
|--------------------|-----------|-----|
| `brand.primary`    | `#1F3B57` | Azul institucional profundo. Portada, títulos, choropleth máx. |
| `brand.secondary`  | `#2C7FB8` | Azul de apoyo. Barras, acentos de dato, puntos de mapa. |
| `brand.accent`     | `#C0762B` | Acento cálido, uso moderado para destacar. |
| `text.primary`     | `#222222` | Cuerpo. |
| `text.secondary`   | `#555555` | Bajadas, epígrafes, notas. |
| `text.muted`       | `#777D86` | Metadatos, pies discretos. |
| `text.on_brand`    | `#FFFFFF` | Texto sobre `brand.primary`. |
| `surface.page`     | `#FFFFFF` | Fondo de página. |
| `surface.card`     | `#EEF2F6` | Cajas neutras. |
| `surface.note`     | `#EAF1F8` | Caja de nota / lectura. |
| `surface.warn`     | `#F7EBDC` | Caja de alcance / advertencia. |
| `surface.ok`       | `#EAF6EF` | Estado positivo. |
| `surface.zebra`    | `#F4F7FA` | Filas alternas de tabla. |
| `border.subtle`    | `#D9DEE5` | Separadores finos, bordes de tabla. |
| `border.strong`    | `#B8C2CE` | Bordes marcados, encabezado de tabla. |
| `status.strong`    | `#1A9850` | Dato consolidado / resultado principal. |
| `status.medium`    | `#C0762B` | Dato parcial / secundario. |
| `status.weak`      | `#B0403A` | Dato débil / poca evidencia. |
| `status.pending`   | `#8A6D3B` | Pendiente de validación. |
| `status.review`    | `#2C7FB8` | En revisión / preliminar. |

> Paleta heredada del informe **Cafecito DGDGAS REVISION_4**, tomada como
> referencia visual principal.

### 6.2 Tipografía

- Familia por defecto: **sans** (`DejaVu Sans` / `Arial` / `Liberation Sans`).
- Escala (pt, para A4): display 26 · h1 15 · h2 12 · h3 10.5 · body 9.5 ·
  small 8.6 · caption 7.9 · footer 7.5.
- Interlineado: tight 1.15 · normal 1.35 · loose 1.5.

### 6.3 Layout

- Página **A4 vertical** (210 × 297 mm), render a **200 dpi**.
- Márgenes (fracción): left/right 0.065 · top 0.075 · bottom 0.065.
  En mm (DOCX/Docs): left/right 20 · top 22 · bottom 20.
- Ancho útil de contenido ≈ 0.87 del ancho de página.

### 6.4 Espaciado y radios

- Espaciado (base 4): xs 4 · sm 8 · md 12 · lg 16 · xl 24 · xxl 32.
- Radios: sm 3 · md 6 · lg 10.

### 6.5 Tabla

- Encabezado con relleno `border.strong` y texto `text.on_brand`.
- Filas alternas `surface.zebra`. Bordes `border.subtle` (0.6 pt).
- Números alineados a la derecha; texto a la izquierda.

### 6.6 Cajas

| Caja                    | Relleno         | Acento           |
|-------------------------|-----------------|------------------|
| Pregunta analizada      | `surface.card`  | `brand.secondary`|
| Lectura de resultados   | `surface.note`  | `brand.primary`  |
| Nota metodológica       | `surface.card`  | `text.muted`     |
| Alcance / advertencia   | `surface.warn`  | `status.medium`  |
| Requiere validación     | `surface.warn`  | `status.pending` |

### 6.7 Mapas

- Tierra `#F3F5F8`, agua `#E4ECF3`, límites de barrio/comuna `#C3CCD7` (tenues).
- Puntos `brand.secondary` con borde blanco. Choropleth de
  `surface.note` a `brand.primary`.
- Nota de alcance **obligatoria** en mapas conceptuales/preliminares.

### 6.8 Footer

- Texto `text.muted`, regla `border.subtle`, tamaño footer.
- Patrón: `DGDGAS - {proyecto} - {tipo}`. Número de página visible.

## 7. Estados y variantes de contenido

Etiquetas semánticas para marcar el estado de un bloque de resultado:

| Estado        | Color            | Etiqueta                 |
|---------------|------------------|--------------------------|
| principal     | `status.strong`  | Resultado principal      |
| secundario    | `status.medium`  | Resultado secundario     |
| preliminar    | `status.review`  | Preliminar               |
| pendiente     | `status.pending` | Requiere validación      |
| anexo         | `text.muted`     | Anexo                    |
| advertencia   | `status.medium`  | Advertencia metodológica |
| interno       | `text.muted`     | Uso interno              |
| historico     | `text.muted`     | Referencia histórica     |

## 8. Reglas de QA público (resumen)

Antes de cerrar un informe o plantilla pública, verificar que **no** haya:
rutas locales, scripts, hashes, QA técnico, emails, teléfonos, datos personales,
CUIT/DNI, API keys, links privados, respuestas individuales identificables, ni
uso de `DataGastro` donde corresponde `DGDGAS`. Detalle completo en
`QA_VISUAL_INFORMES_DGDGAS.md`.

---

*Versión 1.0.0 — base del sistema. No aplicada aún a informes existentes.*
