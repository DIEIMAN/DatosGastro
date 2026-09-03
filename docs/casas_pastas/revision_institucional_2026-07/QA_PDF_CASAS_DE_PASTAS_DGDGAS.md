# QA — PDF institucional DGDGAS · Casas de Pastas

## PDF creado

- **Sí.** PDF generado correctamente.
- **Ruta:** `outputs/casas_de_pastas/INFORME_CASAS_DE_PASTAS_DGDGAS.pdf`
- **Páginas:** 25 (portada + índice + 15 secciones + 4 anexos, con 3 páginas de zoom territorial).
- **Tamaño:** ~829 KB.

### Nota sobre las rutas base del pedido

El pedido listaba como archivos base `docs/casas_pastas/INFORME_CASAS_PASTAS_INTEGRADO_V4.md` y `.pdf`. Esos archivos **no** están en `docs/casas_pastas/` (que solo contiene notas metodológicas y planes). El informe V4 vigente (md + pdf) vive en `outputs/casas_pastas_reporte/`. Se usó esa ubicación real. La carpeta de salida `outputs/casas_pastas_reporte/` usa guion bajo; para la nueva pieza institucional se creó `outputs/casas_de_pastas/` (con "de"), siguiendo la ruta sugerida en el pedido y en línea con la carpeta de la revisión institucional en docs.

## Script creado o usado

- **Creado (copia nueva):** `scripts/casas_pastas/build_pdf_dgdgas.py`
- Es una copia adaptada de `scripts/casas_pastas/build_pdf_integrado_v4.py` (el generador del V4).
- **No se modificó el script productivo original** `build_pdf_integrado_v4.py`.
- El script nuevo lee exactamente los mismos insumos depurados que el V4:
  - `outputs/casas_pastas_integrado/resumen_integrado_v3_depurado.csv`
  - `outputs/casas_pastas_integrado/padron_candidato_integrado_v3_depurado.csv`
  - `data/raw/geo_comunas.geojson`, `data/raw/geo_barrios.geojson`
- No recalcula datos, no hace requests, no usa API key, no toca el pipeline principal.

### Mejoras aplicadas respecto del V4

- Marca institucional **DGDGAS — Dirección General de Desarrollo Gastronómico** + **Gobierno de la Ciudad de Buenos Aires** (se quitó "DataGastro" de la portada y del masthead).
- Título: **Casas de Pastas de la Ciudad de Buenos Aires — Informe**.
- Página de **índice** nueva.
- **Secciones numeradas** de forma correlativa (1–15) y **anexos** (A–D) al final.
- **Pie de página institucional DGDGAS** en todas las páginas (en línea propia, sin solapamiento).
- Metadatos del PDF (Title/Author) actualizados a DGDGAS.
- No genera Markdown (para no tocar nada del V4): solo produce el PDF pedido.

## Archivos modificados

- Ninguno de los existentes fue modificado.
- **Creados:**
  - `scripts/casas_pastas/build_pdf_dgdgas.py`
  - `outputs/casas_de_pastas/INFORME_CASAS_DE_PASTAS_DGDGAS.pdf`
  - `docs/casas_de_pastas/revision_institucional/QA_PDF_CASAS_DE_PASTAS_DGDGAS.md` (este archivo)

## V4 original intacto

- **Sí.** `outputs/casas_pastas_reporte/INFORME_CASAS_PASTAS_INTEGRADO_V4.pdf` y `.md` conservan su fecha (29-jun 11:18) y tamaño originales. No se tocaron.
- El script generador del V4 (`build_pdf_integrado_v4.py`) tampoco se modificó.

## Datos fuente intactos

- **Sí.** Solo se leyeron agregados sanitizados y geometrías oficiales. No se escribió en `data/`, `data/processed/`, `data/analytics/`, ni en las salidas del pipeline. No se hicieron requests ni se usó API key.

## Otros proyectos intactos

- Cafecito: **no tocado.**
- PolosGastro: **no tocado.**
- Mercados: **no tocado.** (Solo se verificó que este informe no depende de esa estructura.)

## Commit / push / staging

- **No** commit. **No** push. **No** `git add`. **No** staging.
- Verificado: no hay nada en el índice de git; los nuevos archivos quedan como `??` (untracked).

## Verificación visual realizada

Como el entorno no tiene rasterizador de PDF (poppler/pymupdf/pypdfium2 no instalados), la verificación se hizo por dos vías:

1. **Extracción de texto del PDF** (PyPDF2) sobre las 24 hojas de contenido.
2. **Rasterizado a PNG** de todas las páginas regenerando las figuras con matplotlib, para inspección visual (portada, índice, resumen, tabla de fuentes, mapas coropléticos, zoom territorial y anexos).

### Resultados

| Chequeo | Resultado |
|---|---|
| Portada institucional (DGDGAS + Dirección General + Gobierno CABA) | Correcta |
| Título "Casas de Pastas de la Ciudad de Buenos Aires — Informe" | Presente |
| Índice con secciones numeradas y anexos | Correcto |
| Numeración de secciones (1–15) y anexos (A–D) | Correcta |
| Anexos al final | Sí |
| Tablas legibles (no rotas) | Sí (tabla de fuentes verificada) |
| Mapas coropléticos y de puntos | Renderizan bien, con leyenda |
| Pie de página institucional en cada hoja | Presente |
| "DataGastro" como texto | **No aparece** en ninguna página |
| "prueba" / "borrador" / "revisión institucional" como etiqueta | **No aparecen** (ver nota abajo) |
| Rutas locales / nombres de scripts / hashes | **No aparecen** |

### Nota sobre falsos positivos de búsqueda

- "prueba" aparece solo como parte del verbo **"prueban"** (en frases del tipo "no prueban por sí solos…"). No es la etiqueta "prueba".
- "institucional" aparece como "documento **institucional**", "información **institucional**" y "sección **institucional**" (descripciones de sitios oficiales). No aparece "revisión institucional".

## Problema visual detectado y corregido

- En la primera generación, el pie de página superponía el texto de "Cuidado metodológico" (izquierda) con la firma institucional (derecha) en páginas con pie largo. **Corregido:** la firma DGDGAS se movió a una línea propia debajo del cuidado metodológico. Reverificado en índice, tabla y secciones: sin solapamiento.

## Pendientes / problemas visuales

- Sin problemas visuales pendientes detectados en las páginas inspeccionadas.
- Verificación por rasterizado con matplotlib (equivalente al render del PDF, ya que ambos usan el mismo backend). Si se requiere una revisión pixel a pixel del PDF final, instalar un rasterizador (poppler / pymupdf) — no se instaló por no agregar dependencias sin pedido.
- Decisión humana pendiente: si este PDF reemplaza al V4 como pieza principal o convive como versión institucional.
