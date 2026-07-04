# QA fase25 - Polos gastronómicos

## Resultado general

- Estado: **APTO**
- PDF auditado: `outputs/polos_gastro/fase25_microajustes_finales_oficina/INFORME_POLOS_GASTRO_DGDGAS_11P_OFICINA_FASE25.pdf`
- Base utilizada: `outputs/polos_gastro/fase24_fase22_corregida_oficina/INFORME_POLOS_GASTRO_DGDGAS_11P_OFICINA_FASE24.pdf`
- Fecha: 2026-07-03

## Verificaciones estructurales

| Check | Resultado | Evidencia |
| --- | --- | --- |
| PDF creado | OK | Archivo presente en carpeta fase25 |
| 11 páginas reales | OK | `pdfinfo`: `Pages: 11` |
| Formato A4 | OK | `pdfinfo`: `595.276 x 841.89 pts (A4)` |
| Índice consistente | OK | Páginas 1 a 11, sin entrada pisada |
| Numeración visible correcta | OK | `1 / 11` a `11 / 11` |
| Pie institucional consistente | OK | Pie visible en páginas 2 a 11 |
| Marca visible correcta | OK | `DGDGAS — Dirección General de Desarrollo Gastronómico` |
| Grilla de páginas generada | OK | `contact_sheet_pdf_pages_fase25.png` |
| Grilla de mapas generada | OK | `contact_sheet_mapas_fase25.png` |

## Verificaciones editoriales

| Check | Resultado | Evidencia |
| --- | --- | --- |
| Página 5: `Mapa general de polos y ejes gastronómicos` | OK | 2 apariciones en texto extraído |
| Página 3: `referencias del universo semilla` | OK | Frase aplicada |
| Página 4: enfoque de referencias sin endorsement | OK | Se reemplazó la frase remanente con `referencias del universo semilla` |
| Páginas 7 a 11: `Referencias del universo semilla` | OK | Títulos aplicados; 8 apariciones totales en PDF |
| `Menciones destacadas` | OK | 0 apariciones en texto extraído |
| `Shopping Abasto` con mayúscula | OK | 1 aparición |
| Abasto separado de Corrientes | OK | Página 10 conserva líneas y áreas diferenciadas |
| Belgrano R separado de Barrio Chino | OK | Página 11 conserva sectores diferenciados |
| La Mar solo en Palermo / Las Cañitas | OK | 1 aparición, página 7 |
| Tildes visibles | OK | Cañitas, gastronómicos, gastronómico, Nápoles, Güerrín, Pulpería y Dirección presentes |

## Verificaciones metodológicas

| Check | Resultado | Evidencia |
| --- | --- | --- |
| Áreas como aproximaciones de lectura territorial | OK | Páginas 3 y 4 |
| No son límites oficiales | OK | Páginas 3 y 4 |
| No son padrón de locales | OK | Páginas 3 y 5 |
| No son ranking gastronómico | OK | Páginas 3 y 4 |
| No son recomendación comercial | OK | Página 4 |
| No acreditan actividad vigente por sí mismas | OK | Página 4 |
| No se cambió el enfoque metodológico | OK | Solo microajustes editoriales y visuales |

## Verificación de ajustes fase25

| Página | Ajuste pedido | Estado | Evidencia | Observación |
| --- | --- | --- | --- | --- |
| 2 | Corregir línea guía del índice en la entrada del mapa general | Aplicado | Raster `page-02.png` | La línea empieza después del texto y no lo atraviesa |
| 8 | Mejorar legibilidad de Puerto Madero | Aplicado | Raster `page-08.png` y SVG de mapa | `A. Moreau de Justo`, `Juana Manso`, `Docks`, `Sector costero`, `Dársena Sur` y `Faena / El Mercado` quedan legibles |
| 8 | Evitar conflicto del texto vertical del frente costero | Aplicado | Raster `page-08.png` | Se eliminó el rótulo vertical redundante; el concepto queda en subtítulo, lectura y eje costero |
| 11 | Reemplazar `IDENTIDAD CLARA` en Barrio Chino | Aplicado | SVG de Belgrano | Quedó `SUBZONA APROX.` |
| 7-11 | Reemplazar título `Menciones destacadas` | Aplicado | Texto extraído | Quedó `Referencias del universo semilla` |
| 3 | Reemplazar frase `menciones destacadas del universo semilla` | Aplicado | Texto extraído | Quedó `referencias del universo semilla` |
| 10 | Mejorar rótulo Corrientes | Aplicado | SVG de Corrientes / Abasto | Quedó `Corrientes (9 de Julio – Callao)` |

## Auditoría visual por página

| Página | Resultado | Observación |
| --- | --- | --- |
| 1 | OK | Portada conserva marca DGDGAS y 11 páginas |
| 2 | OK | Índice limpio; la entrada larga no queda tachada |
| 3 | OK | Texto actualizado sin romper caja institucional |
| 4 | OK | Caja `Universo semilla` blindada con referencias, ranking y actividad vigente |
| 5 | OK | Mapa general conserva tamaño y lectura de fase24 |
| 6 | OK | Sin cambios visuales relevantes |
| 7 | OK | Caja renombrada sin desborde |
| 8 | OK | Puerto Madero mejora legibilidad sin agrandar agresivamente el mapa |
| 9 | OK | Caja renombrada sin desborde |
| 10 | OK | Corrientes / Abasto conserva separación; rótulo ajustado |
| 11 | OK | Barrio Chino sin `IDENTIDAD CLARA`; caja renombrada sin desborde |

## Control de privacidad y rastros técnicos

| Término o patrón buscado | Resultado | Observación |
| --- | --- | --- |
| `DataGastro` | 0 | OK |
| `Dirección General de Gastronomía` | 0 | OK |
| `Ale` como palabra aislada | 0 | OK |
| `a validar` / `validar con Ale` | 0 | OK |
| `preliminar`, `borrador`, `prueba`, `revisión`, `documento interno` | 0 | OK |
| `Google Places`, `place_id`, `API key`, `rating`, `raw JSON` | 0 | OK |
| `script`, `scripts`, `CSV` | 0 | OK |
| Emails / `@` | 0 | OK |
| Teléfonos | 0 | OK |
| CUIT / DNI | 0 | OK |
| Links privados Drive / Docs | 0 | OK |
| Patrón de API key Google | 0 | OK |

## Observaciones aceptadas

1. En página 8 se eliminó el texto vertical del frente costero porque era redundante y generaba conflicto visual. El concepto se mantiene por la banda de docks, el eje costero, el subtítulo y la lectura territorial.
2. El rótulo `Corrientes (9 de Julio – Callao)` queda partido en dos líneas dentro del mapa para conservar tamaño, encuadre y aire visual.
3. No se tocaron opcionales que implicaban riesgo de regresión visual o cambio de alcance.

## Conclusión

Fase25 mejora la versión fase24 en los ajustes menores señalados, conserva la estructura de 11 páginas y no introduce regresiones medias ni críticas. **Fase25 puede reemplazar a fase24 como versión de oficina.**
