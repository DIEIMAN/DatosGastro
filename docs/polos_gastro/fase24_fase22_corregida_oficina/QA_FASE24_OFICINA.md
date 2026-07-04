# QA fase24 - Polos gastronómicos

## Resultado general

- Estado: **APTO**
- PDF auditado: `outputs/polos_gastro/fase24_fase22_corregida_oficina/INFORME_POLOS_GASTRO_DGDGAS_11P_OFICINA_FASE24.pdf`
- Base utilizada: fase22 (`outputs/polos_gastro/fase22_microajustes_texto_oficina/INFORME_POLOS_GASTRO_DGDGAS_11P_TEXTO.pdf`). **No se usó fase23 como base**; fase23 se consultó solo como referencia de regresiones a evitar (`docs/polos_gastro/fase23_microajustes_mapas_oficina/FASE23_NO_ENTREGABLE_REGRESIONES.md`).
- Fecha: 2026-07-03

## Verificaciones estructurales

| Check | Resultado |
| --- | --- |
| PDF creado | OK |
| 11 páginas reales (`pdfinfo`: Pages: 11) | OK |
| Tamaño A4 (595.276 x 841.89 pts) | OK |
| Índice consistente con las 11 páginas | OK |
| Estructura de páginas idéntica a fase22 (portada, índice, resumen, alcance, mapa general, lectura territorial, 5 detalles) | OK |
| Mapas de detalle con el mismo encuadre, escala y composición de fase22 | OK |
| Rasterizado completo en `raster_pages/` (11 PNG) | OK |
| Grillas de control generadas (`contact_sheet_pdf_pages_fase24.png`, `contact_sheet_mapas_fase24.png`) | OK |

## Verificaciones editoriales

Controles sobre `pdf_text_extract.txt` (pdftotext, UTF-8) y revisión visual de rasters:

| Check | Resultado |
| --- | --- |
| `DGDGAS`: 11 apariciones | OK |
| `Dirección General de Desarrollo Gastronómico`: 11 apariciones, con acentos correctos | OK |
| `Dirección General de Gastronomía`: 0 apariciones (texto y revisión visual de mapas) | OK |
| Página 5: "Mapa general de polos y ejes gastronómicos" | OK |
| `Otras referencias de la zona`: 5 apariciones | OK |
| `Otras referencias del universo semilla`: 0 apariciones | OK |
| `Shopping Abasto` presente; "el shopping" a secas: 0 | OK |
| Abasto en línea separada como área de lectura (no mezclado como local) | OK |
| Belgrano R en línea separada como subzona de referencia | OK |
| La Mar solo en Palermo / Las Cañitas | OK |
| Tildes visibles correctas: Cañitas, gastronómicos, gastronómico, Nápoles, Güerrín, Pulpería | OK |
| Sin caracteres `?` sustituyendo acentos (defecto de fase22 corregido) | OK |
| Sin `DataGastro`, `Ale` aislada, `preliminar`, `borrador`, `prueba`, `revisión`, `documento interno`, `a validar`, `validar con Ale` | OK |

## Verificaciones metodológicas

| Check | Resultado |
| --- | --- |
| Áreas presentadas como aproximaciones de lectura territorial | OK (páginas 3, 4 y subtítulos de mapas) |
| Se aclara que no son límites oficiales | OK (páginas 3 y 4) |
| Se aclara que no son padrón de locales | OK (página 3) |
| Se aclara que no son ranking gastronómico | OK (páginas 3 y 4) |
| Menciones destacadas: no recomendación comercial | OK (página 4) |
| Menciones: no acreditan actividad vigente por sí mismas | OK (página 4) |
| Subzonas como aproximaciones editoriales, no polígonos normativos | OK (página 4) |

## Auditoría visual por página

| Página | Contenido | Resultado |
| --- | --- | --- |
| 1 | Portada azul con marca DGDGAS | OK — acentos correctos ("gastronómicos", "Dirección"), layout idéntico a fase22 |
| 2 | Índice | OK — 11 entradas, título de página 5 correcto |
| 3 | Resumen ejecutivo | OK — 3 párrafos de fase22 con acentos correctos, recuadro ancho conservado (no se repite la reducción de fase23) |
| 4 | Alcance y criterio de lectura | OK — 3 cajas metodológicas de fase22 |
| 5 | Mapa general | OK — "Abasto" separado de "Corrientes", "DoHo" separado de "Villa Urquiza", leyenda con tildes; composición y tamaño del mapa iguales a fase22 |
| 6 | Lectura territorial general | OK — idéntica a fase22 con acentos correctos |
| 7 | Palermo / Las Cañitas | OK — leyenda ya no pisa "Av. Córdoba" (con tilde); "Scalabrini Ortiz" y "Juan B. Justo" legibles; encuadre igual a fase22 |
| 8 | Puerto Madero | OK — "Dársena Sur" ya no pisa la leyenda; rótulo vertical "frente costero" completo; aire visual conservado (no se repite el encuadre forzado de fase23) |
| 9 | San Telmo | OK — "Área gastronómica", "Casco histórico / Defensa" y "Paseo Colón" con tildes dentro del mapa; "Chile" legible |
| 10 | Corrientes / Abasto | OK — separación Corrientes/Abasto conservada; se quitó la etiqueta chica duplicada "Abasto" que tocaba el borde del área |
| 11 | Belgrano | OK — Barrio Chino, Bajo Belgrano y Belgrano R diferenciados; "Juramento" y "Del Libertador" ahora legibles; Bajo Belgrano con el mismo margen de fase22 (no pegado al borde como en fase23) |

## Observaciones aceptadas

Observaciones menores que no bloquean y se decidió no tocar para no introducir regresiones:

1. Página 8: "A. Moreau de Justo" queda parcialmente bajo la banda de Docks y "Juana Manso" parcialmente detrás del rótulo "Sector costero", igual que en fase22. Moverlas agregaría ruido o taparía otros elementos.
2. Página 8: el rótulo "Sector costero" queda cerca del borde derecho, igual que en fase22; corre con leve recorte del padding del recuadro, sin pérdida de lectura.
3. Página 8: el recuadro "Dársena Sur" pisa levemente el halo del extremo sur del eje costero; se prefirió esto a que pise la leyenda (defecto de fase22).
4. Página 5: la densidad de etiquetas de la zona centro (Corrientes / Microcentro / Nuevo Bajo Retiro) es la propia del mapa global heredado; legible a tamaño de página.

## Conclusión

Fase24 conserva la composición, el aire visual y el contenido editorial de fase22, corrige el defecto de encoding
(acentos mostrados como "?" en todo el texto del PDF de fase22) y aplica únicamente los microajustes de mapas
pendientes sin repetir las regresiones de fase23. **Fase24 puede reemplazar a fase22 como versión de oficina.**
