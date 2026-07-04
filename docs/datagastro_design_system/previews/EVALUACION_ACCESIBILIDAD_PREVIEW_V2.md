# Evaluacion de accesibilidad y contraste - Preview v2

Fecha: 2026-07-01. Documento interno. Evalua contraste WCAG 2.1 de la preview v2
(`outputs/datagastro_design_system/previews/polos_borrador3_preview_v2/`). No canoniza tokens.

## Metodo

Se calculo el ratio de contraste WCAG 2.1 (luminancia relativa) con una funcion propia en Python
(formula estandar sRGB -> luminancia lineal), sin instalar dependencias. Script temporal de
sesion, no incorporado al repo (formula documentada abajo). Umbrales usados:

- **AA texto normal / chico:** >= 4.5:1 (aplica a body 10.5pt, small 9pt y caption 8pt).
- **AA texto grande (>= 18pt o >= 14pt bold):** >= 3.0:1 (aplica a display y h1).
- **AAA (referencia):** >= 7.0:1.

Formula: `ratio = (L1 + 0.05) / (L2 + 0.05)`, con `L = 0.2126*R + 0.7152*G + 0.0722*B` sobre
canales linealizados (`c/12.92` si `c <= 0.04045`, si no `((c+0.055)/1.055)^2.4`).

Limite del metodo: es un calculo numerico de pares de color; no reemplaza una prueba con lectores
de pantalla ni una revision de impresion real en grises.

## Resultados - texto principal

| Par (uso) | Colores | Ratio | AA texto chico |
| --- | --- | --- | --- |
| Texto primario sobre pagina | #1B2733 / #FFFFFF | 15.17 | PASA (y AAA) |
| Texto secundario sobre pagina | #566573 / #FFFFFF | 5.99 | PASA |
| Texto de tabla sobre pagina | #3C4B59 / #FFFFFF | 8.96 | PASA (y AAA) |
| Texto de tabla sobre zebra | #3C4B59 / #FAFBFC | 8.65 | PASA (y AAA) |
| Texto secundario sobre card/warm/warn | #566573 / #F4F6F8-#F4EAE0 | 5.05-5.53 | PASA |
| Blanco sobre brand.primary (header tabla) | #FFFFFF / #1F3B57 | 11.53 | PASA (y AAA) |
| on_brand_soft sobre brand.primary | #EAF0F5 / #1F3B57 | 10.04 | PASA (y AAA) |
| on_brand_soft sobre primary_dark (portada) | #EAF0F5 / #16293D | 12.89 | PASA (y AAA) |
| Titulos brand.primary sobre pagina | #1F3B57 / #FFFFFF | 11.53 | PASA (y AAA) |
| **text.muted sobre pagina** | **#8A97A3 / #FFFFFF** | **2.98** | **FALLA (tambien falla 3:1)** |
| **brand.secondary como eyebrow 8pt** | **#2C7FB8 / #FFFFFF** | **4.34** | **FALLA (pasa solo como texto grande)** |
| **brand.accent como titulo 9pt sobre warm** | **#C0762B / #F6F4EF** | **3.26** | **FALLA** |
| **status.validation como titulo sobre warn** | **#A85B2A / #F4EAE0** | **4.22** | **FALLA** |

### Correcciones aplicadas en la preview v2

| Uso | v1 (falla) | v2 (corregido) | Ratio v2 |
| --- | --- | --- | --- |
| Footers, captions, cinta de estado | text.muted #8A97A3 | text.secondary #566573 | 5.05-5.99 |
| Eyebrow de seccion (8pt) | brand.secondary #2C7FB8 | status.medium #2C6E9E | 5.48 |
| Titulo de nota metodologica (9pt, sobre warm) | brand.accent #C0762B | #9A5C1F (accent oscurecido) | 4.87 |
| Titulo de advertencia (9pt, sobre warn) | status.validation #A85B2A | #8A4B22 (= state validacion.text) | 5.69 |

`brand.accent` y `status.validation` siguen usandose **solo como filetes y bordes** (elementos no
textuales), donde el requisito aplicable es 3:1 de componentes UI y el uso es decorativo-redundante.

## Resultados - chips

Todos los pares texto/fondo de chips **pasan AA 4.5:1**, tanto los existentes en el mapeo v1 como
los tres propuestos en v2:

| Chip | Texto / fondo | Ratio |
| --- | --- | --- |
| Documentacion fuerte | #245A4A / #E9F1EC | 6.93 |
| Documentacion media | #245980 / #E9F0F6 | 6.48 |
| Documentacion debil | #7E571A / #F4EEE1 | 5.56 |
| En espera de evidencia | #4C5964 / #ECEFF1 | 6.23 |
| Requiere validacion | #8A4B22 / #F4EAE0 | 5.69 |
| Insumo interno | #3E4A57 / #EBEDF0 | 7.71 (AAA) |
| Advertencia real | #8A2E22 / #F6E9E7 | 7.11 (AAA) |
| Contexto (propuesto) | #33626C / #EAF1F2 | 5.92 |
| No delimita (propuesto) | #8A4B22 / #F3E7DC | 5.55 |
| Anexo (propuesto) | #454F5B / #EEF0F2 | 7.29 (AAA) |

**Dots (puntos de color).** El dot de "en espera" del mapeo v1 (#8A97A3 sobre #ECEFF1) da 2.58 y
no llega al 3:1 de componentes no textuales; en v2 se oscurecio a #6F7D8A. Los dots son siempre
redundantes con la etiqueta textual, por lo que el significado nunca depende solo del color.

## Riesgos detectados

1. **`text.muted` (#8A97A3) no sirve para texto informativo** sobre ninguna superficie clara del
   sistema (2.98 sobre blanco, menos sobre superficies tenues). El token `footer.text_color`
   canonico apunta a text.muted: si se canoniza asi, todos los footers fallarian AA.
2. **`brand.secondary` no sirve para texto chico sobre blanco** (4.34). Solo para texto >= 14pt
   bold o elementos graficos.
3. **`brand.accent` es el color mas debil del sistema como texto** (3.26 sobre warm; ~3.5 sobre
   blanco). Debe quedar restringido a filetes, bordes y titulos grandes.
4. **Zebra + chip:** los fondos de chip sobre filas zebra (#FAFBFC) mantienen sus ratios (la
   diferencia de fondo es minima), pero si la zebra se oscureciera, los bordes de chip de 0.6pt
   podrian perder definicion en impresion.
5. **Impresion en grises:** varios pares de chips (media vs contexto) convergen a grises similares;
   la etiqueta textual obligatoria es la mitigacion y debe mantenerse como regla dura.

## Combinaciones a evitar

- `text.muted` sobre cualquier superficie, para cualquier texto que deba leerse (solo decorativo).
- `brand.secondary` como color de texto en cuerpos <= 12pt sobre fondos claros.
- `brand.accent` como color de texto chico, sobre cualquier superficie.
- `status.validation` como texto chico sobre `surface.warn` (usar la variante texto #8A4B22).
- Dot `enEspera` original (#8A97A3) sobre su propio fondo de chip.
- Cualquier chip sin etiqueta textual (regla existente, confirmada por esta evaluacion).

## Recomendaciones para ajustar tokens antes de canonizar

1. Agregar un token `color.text.caption_aa` (o redefinir `text.muted` a un valor >= 4.5 sobre
   blanco, por ejemplo #566573 o #6A7682 ~ 4.6) y apuntar `footer.text_color` ahi.
2. Documentar en los tokens la regla de uso: `brand.secondary` y `brand.accent` no son colores de
   texto chico; agregar variantes `*_text_aa` (#2C6E9E ya existe como status.medium; #9A5C1F como
   accent oscurecido) si se necesitan como texto.
3. Incorporar los `state_details` propuestos de v2 (contexto, no_delimita, anexo) con los valores
   ya verificados >= 4.5.
4. Oscurecer `state_details.enEspera.dot` a #6F7D8A (o documentar que el dot es decorativo).
5. Mantener como regla dura: etiqueta textual obligatoria en chips (`chip.text_required = true` ya
   existe en el mapeo; conservarlo en cualquier canonizacion).
6. Antes de PDF/DOCX: repetir esta verificacion sobre el render real (los ratios pueden variar con
   antialiasing y perfiles de color de impresion).
