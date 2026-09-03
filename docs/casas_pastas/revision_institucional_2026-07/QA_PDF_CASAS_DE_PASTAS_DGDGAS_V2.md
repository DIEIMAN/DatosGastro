# QA — PDF ejecutivo DGDGAS · Casas de Pastas (V2)

Segunda iteración: versión más corta y ejecutiva del PDF DGDGAS, con menos explicación metodológica.

## PDF regenerado

- **Sí.** Regenerado sobre la misma ruta (no se creó archivo nuevo ni se pisó el V4).
- **Ruta:** `outputs/casas_de_pastas/INFORME_CASAS_DE_PASTAS_DGDGAS.pdf`
- **Cantidad de páginas — anterior:** 25 → **nueva:** 14.
- **Tamaño:** ~769 KB.

## Script

- Modificado: `scripts/casas_pastas/build_pdf_dgdgas.py` (el mismo script DGDGAS de la iteración anterior; **no** es el script productivo del V4).
- **No** se tocó `scripts/casas_pastas/build_pdf_integrado_v4.py`.
- Sigue leyendo los mismos insumos depurados; no recalcula datos, no hace requests, no usa API key, no toca el pipeline.

## Cambios aplicados

1. **Menos metodología.** Se quitaron como páginas centrales las explicaciones extensas de multifuente, cuidado metodológico, revisión manual, replicabilidad y diferencias entre fuentes. Esa información quedó condensada en pocos bullets (sección 1 y nota del anexo C).
2. **Resumen ejecutivo.** KPIs = 254 candidatos únicos, 173 independientes, 81 en cadenas. **Se quitó el KPI "53 multifuente"**; multifuente aparece solo como nota breve al pie ("53 candidatos en más de una fuente"). El foco pasó a universo depurado, casas independientes, distribución territorial, zonas de mayor concentración y utilidad para validar.
3. **Fuentes.** Las dos páginas metodológicas ("Registro oficial y universo operativo probable" + "Por qué el registro oficial no alcanza") se reemplazaron por **una sola página breve** (sección 1) con bullets, sin el gráfico AGC/multifuente/padrón ni la tabla extensa de fuentes.
4. **Cantidad y densidad.** Las 6 páginas separadas (cantidad comuna, densidad comuna, comparación comuna, cantidad barrio, densidad barrio, barrios polo) se fusionaron en **2 páginas**: una de cantidad (mapas de comuna + barrio) y una de densidad (mapas de comuna + barrio), cada una con lectura breve.
5. **Zoom territorial.** Se mantienen Palermo, Caballito y Belgrano; comentarios acortados para no repetir cantidad/densidad.
6. **Cadenas.** "Cadenas y casas de barrio" + "Principales cadenas" se unieron en **una sola página** (proporción 68/32 + ranking compacto de cadenas + lectura breve).
7. **Páginas metodológicas pesadas eliminadas** como páginas independientes: "Núcleo de mayor respaldo cruzado", "Aporte de la revisión manual" y "Metodología: aporte y replicabilidad". Su contenido esencial quedó en bullets breves (sección 1 y nota del anexo C).
8. **Pie de página.** Ya no repite la advertencia larga de "cuidado metodológico". El pie es institucional (DGDGAS — Dirección General de Desarrollo Gastronómico · Gobierno de la Ciudad de Buenos Aires). Solo algunas páginas puntuales llevan una nota breve; las advertencias se concentran en resumen, sección 1 y anexo C.
9. **Anexos.** Se conservan: casos con respaldo documental (A), fuentes documentales (B) y limitaciones breves (C). Se eliminó el anexo de metodología larga / replicabilidad (condensado en la nota del anexo C).

## Páginas / secciones eliminadas o fusionadas

| En la versión de 25 páginas | En la versión de 14 |
|---|---|
| Sección 1 (registro oficial vs universo) + Sección 2 (fuentes, tabla) | Fusionadas → Sección 1 (bullets breves) |
| Concentración comuna + Densidad comuna + Comparación comuna | Fusionadas → Sección 3 (cantidad) y Sección 4 (densidad) |
| Concentración barrio + Densidad barrio + Barrios polo | Fusionadas en Sección 3 y 4 (mapa de barrio en cada hoja) |
| Cadenas y casas de barrio + Principales cadenas | Fusionadas → Sección 6 |
| Núcleo multifuente (página entera) | Eliminada (nota breve) |
| Aporte de la revisión manual (página entera) | Eliminada (bullet en sección 1) |
| Utilidad del diagnóstico (página entera) | Integrada en el resumen ejecutivo |
| Anexo D metodología/replicabilidad (página entera) | Eliminada (nota del anexo C) |

## Estructura final (14 páginas)

1. Portada · 2. Índice · 3. Resumen ejecutivo · 4. Sección 1 Fuentes y alcance · 5. Sección 2 Distribución territorial · 6. Sección 3 Cantidad · 7. Sección 4 Densidad · 8–10. Sección 5 Zoom (Palermo, Caballito, Belgrano) · 11. Sección 6 Cadenas · 12. Anexo A Casos documentales · 13. Anexo B Fuentes documentales · 14. Anexo C Limitaciones.

## Verificaciones

| Chequeo | Resultado |
|---|---|
| Cantidad de páginas | 14 (bajó de 25) |
| Portada DGDGAS (marca + Gobierno CABA + título) | Correcta |
| Índice actualizado (14 págs, secciones fusionadas) | Correcto |
| "DataGastro" como marca pública | **No aparece** en ninguna página |
| "prueba" / "borrador" / "revisión institucional" / "documento interno" | **No aparecen** (ver nota) |
| KPI "53 multifuente" en el resumen | **No** como KPI; solo nota breve al pie |
| Cantidad y densidad condensadas | Sí (1 hoja cada una, 2 mapas por hoja) |
| Cadenas en una sola página | Sí |
| Multifuente / revisión manual / metodología larga como páginas | **Ya no existen** como páginas independientes |
| Tablas y mapas legibles | Sí (verificado por rasterizado) |
| V4 original intacto | Sí (fecha y tamaño originales conservados) |

### Nota sobre falsos positivos

- "prueba" aparece solo como parte del verbo **"prueban"** ("no prueban por sí solos…"). No es la etiqueta.
- "institucional" aparece como "información **institucional**" (descripción de un sitio oficial en el Anexo B). No aparece "revisión institucional" ni "documento interno".

## Problema visual detectado y corregido

- En la primera generación de esta V2, en el resumen ejecutivo (1) las tarjetas KPI tapaban la segunda línea del subtítulo y (2) la nota al pie era larga y se solapaba con la firma institucional. **Corregido:** se bajaron las tarjetas y se acortó la nota al pie a una línea. Reverificado: sin solapamientos.

## Otras confirmaciones

- **V4 intacto:** `INFORME_CASAS_PASTAS_INTEGRADO_V4.md` y `.pdf` sin cambios (fecha 29-jun 11:18).
- **Datos fuente:** no se tocaron; solo lectura de agregados sanitizados y geometrías oficiales.
- **Otros proyectos:** Cafecito, PolosGastro y Mercados **no tocados**.
- **Git:** sin commit, sin push, sin `git add`, sin staging. Verificado: índice de git vacío; archivos nuevos untracked.

## Pendientes

- Sin problemas visuales pendientes en las páginas inspeccionadas (portada, índice, resumen, fuentes, cantidad, densidad, zoom, cadenas).
- Verificación por rasterizado con matplotlib (mismo backend que el PDF), al no haber rasterizador de PDF instalado en el entorno.
- Decisión humana: si este PDF ejecutivo reemplaza al V4 como pieza principal o convive con él.
