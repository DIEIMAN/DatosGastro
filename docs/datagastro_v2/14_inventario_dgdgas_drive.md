# DataGastro V2 — Inventario de la carpeta interna DGDGAS (copia de Drive)

> Etapa 2.5. Inventario **seguro y sanitizado** de la carpeta interna copiada de Drive. **No**
> se ejecutaron requests, **no** se descargó nada, **no** se modificó ni movió ningún archivo
> original, **no** se leyeron valores de celdas ni datos personales. Pipeline V1 y casas de
> pastas intactos.

## 1. Carpeta localizada

- **Ruta relativa:** `Algunas Cosas de Drive/` (carpeta ya **gitignored** en el repo).
- Rutas candidatas revisadas: `Algunas Cosas de Drive`, `DGDGAS`, `DG DGAS`, `DGAS`,
  `Direccion Gastronomia`. La elegida es la única con contenido DGDGAS real.
- Existe además `DGDGAS.lnk` (acceso directo a Drive `G:\`) que **no se abre** (Drive es solo
  lectura y no se navega).
- Análisis previo seguro de V1 reutilizado: `outputs/analisis_interno/eventos_dgdgas/`
  (perfilado de hojas/columnas sin valores).

## 2. Método (cómo se inventarió sin exponer datos)

- Script offline `src/v2/build_dgdgas_inventory.py`.
- De los `.xlsx` se leyó **solo** `xl/workbook.xml` (nombres de hoja) — metadata estructural;
  **nunca** `sharedStrings` (que contiene los valores/PII).
- Los `.gdoc`/`.gsheet`/`.lnk` son **punteros de Drive de 0 bytes**: se registran como punteros,
  **no se abren** y **no se expone su URL privada**.
- Solo **rutas relativas**. Sin rutas absolutas, sin links de Drive, sin valores de celdas.

## 3. Resumen del inventario

- Carpetas recorridas: 1 · Archivos inventariados: **16**.
- Principales tipos: planillas `.xlsx` (3 con contenido real), punteros `.gdoc`/`.gsheet`
  (Documentos/Sheets de Drive, 0 bytes locales), 1 `.zip` (readme), 1 `.lnk` (acceso directo).
- Utilidad para V2: **alta = 5** (incluye punteros de los archivos clave), media = 6, baja = 4,
  descartar_por_ahora = 1.
- Archivos con **PII probable = sí: 2** (las dos versiones de la base directorio).

Detalle completo y sanitizado en `outputs/v2/sanitized/inventario_dgdgas_archivos_sanitizado.csv`.

## 4. Archivos con contenido real (planillas)

### 4.1 `Copia de Base de datos DGDGAS EVENTOS.xlsx` — **clave**
- A pesar del nombre "EVENTOS", es un **directorio de locales gastronómicos por rubro**, no una
  base de eventos (confirmado por perfilado V1: no hay columnas de fecha ni evento claras).
- **15 hojas**, ~2.509 filas. Hojas por rubro: BASE, Bares (269), Bodegones (97),
  Café y dulce (702), Cocina internacional (178), Hamburguesería (131), Heladería (65),
  Parrillas (95), Pizza/empanadas/pasta (276), Restaurantes (470), Restaurantes de autor (50),
  Foodtrucks (82), Organizadores (1), Emprendimientos (65), Comunas (15).
- Columnas típicas por hoja: `LOCAL`, `BARRIO`, `DIRECCIÓN`, `REFERENTE`, `CARGO`, `CELULAR`,
  `MAIL`, `INSTAGRAM`, `N`. → **PII alto** (celular/mail/referente/teléfono).
- **Sensibilidad: alta.** Uso solo agregado y **tras minimizar PII**. No publicable con contacto.

### 4.2 `Copia de Recap eventos.xlsx`
- Recaps de **eventos propios** por edición. 9 hojas: TOTAL, CONSOLIDADO, DASHBOARD RECAP,
  Sabor a Bs As, Experiencia BA, Mate BA, Corrientes 24hs, Barrios a la carta, Cafecito.
- Sensibilidad media (gestión interna). Útil para **enriquecer F04 (eventos)**.

### 4.3 `Copia de ADE I SEGUIMIENTO.xlsx`
- Seguimiento/ranking de **foodtrucks** y eventos. 6 hojas: 2026, RANKING FOODTRUCKS, ALIAS FT,
  DASHBOARD FT, 2025, MAUTINO Food truck Argentina.
- Sensibilidad media. Contexto de gestión, **no padrón territorial**.

## 5. Punteros de Drive (0 bytes locales)

`.gdoc`/`.gsheet` sin contenido local: `Documento_Maestro_Ecosistema`,
`Informe_Base_de_Datos`, `Informe_Eventos_Acompanados`, `Informe_Recap_Eventos`,
`Eventos Acompañados`, `RYSDE DGGAS`, `AC_README`, `BD_README`, `SYS_README` y las versiones
`.gsheet` de las planillas. Útiles como **documental/contexto**, pero requieren un export
oficial sin datos privados antes de cualquier uso. **No se navegó a Drive.**

## 6. Clasificación por utilidad (síntesis)

| Utilidad | Archivos |
|---|---|
| **alta** | Base directorio por rubro (I10), Recap eventos (I11) |
| **media** | Seguimiento ADE/foodtrucks (I12), documentos/informes maestros (I13) |
| **baja** | READMEs, documentación interna |
| **descartar_por_ahora** | `DGDGAS.lnk` (acceso directo) |

## 7. Riesgos detectados

- **PII** en el directorio por rubro (celular, mail, referente): no exportar a entregables.
- **Confundir contactos con establecimientos vigentes** o con eventos (el nombre "EVENTOS"
  induce a error).
- **Sin fecha de actualización** declarada → no asumir vigencia.
- **Grano mixto** en recaps (total/consolidado/edición) y en seguimiento (gestión).
- Punteros de Drive: contenido no auditable localmente.

## 8. Qué NO se hizo (límites de esta etapa)

- No se integró ningún dato ni se construyó padrón.
- No se generaron outputs con nombres/direcciones/personas.
- No se modificó, movió ni borró ningún archivo original.
- No se abrieron los punteros de Drive ni se expusieron sus URLs.

Continúa en `15_fuentes_internas_dgdgas_v2.md` (fuentes internas candidatas y cobertura por rubro).
