# Auditoría comparativa fase22 vs fase24

**Fecha:** 2026-07-03
**PDF fase22:** `outputs/polos_gastro/fase22_microajustes_texto_oficina/INFORME_POLOS_GASTRO_DGDGAS_11P_TEXTO.pdf`
**PDF fase24:** `outputs/polos_gastro/fase24_fase22_corregida_oficina/INFORME_POLOS_GASTRO_DGDGAS_11P_OFICINA_FASE24.pdf`

## Resultado

**Fase24 mejora a fase22 sin regresiones.** Conserva la composición, la escala de mapas y el aire visual de
fase22 en las 11 páginas, corrige el defecto transversal de encoding (todos los acentos del texto del PDF de
fase22 se veían como "?") y resuelve las superposiciones y tildes internas de mapas que habían quedado
pendientes. No reproduce ninguna de las regresiones documentadas de fase23.

## Comparación visual

Comparación página por página entre los rasters de fase22 (`fase22_microajustes_texto_oficina/raster_pages/`)
y los de fase24 (`fase24_fase22_corregida_oficina/raster_pages/`):

| Página | Fase22 | Fase24 | Diagnóstico | Estado |
| --- | --- | --- | --- | --- |
| 1 | Portada correcta pero con "gastron?micos" y "Direcci?n" (acentos rotos) | Misma portada con acentos correctos | Mismo layout; texto ahora publicable | mejora |
| 2 | Índice correcto con acentos rotos ("?ndice", "Ca?itas") | Mismo índice con acentos correctos | Mismo layout | mejora |
| 3 | Resumen ejecutivo con recuadro ancho; acentos rotos | Idéntico con acentos correctos | Conserva la jerarquía visual que fase23 había perdido | mejora |
| 4 | Tres cajas metodológicas; acentos rotos | Idénticas con acentos correctos | Mismo layout | mejora |
| 5 | Mapa general correcto, pero "Abasto" pisaba "Corrientes" y "DoHo" chocaba con "Villa Urquiza" | Mismo mapa, mismo tamaño y encuadre, etiquetas separadas y leyenda con tildes | Composición conservada; legibilidad mejorada | mejora |
| 6 | Página de lectura territorial; acentos rotos | Idéntica con acentos correctos | Mismo layout | mejora |
| 7 | Encuadre correcto; leyenda pisaba "Av. Cordoba" (sin tilde); "Scalabrini Ortiz" y "Juan B. Justo" ocultos tras rótulos de subzonas | Mismo encuadre; los tres rótulos legibles y con tildes | Sin cambio de escala ni de composición | mejora |
| 8 | Encuadre correcto con aire; "Dársena Sur" pisaba la leyenda; rótulo vertical parcialmente cubierto | Mismo encuadre y aire; leyenda limpia; rótulo vertical completo | No repite el encuadre forzado de fase23 | mejora |
| 9 | Encuadre correcto; "Area gastronomica", "Casco historico" y "Paseo Colon" sin tildes; "Chile" oculto | Mismo encuadre; tildes internas correctas; "Chile" legible | Sin cambio de composición | mejora |
| 10 | Separación Corrientes/Abasto correcta; etiqueta chica "Abasto" duplicada rozando el borde del área | Misma composición panorámica; etiqueta duplicada eliminada | Balance horizontal de fase22 conservado | mejora |
| 11 | Tres sectores diferenciados con margen; "Juramento" y "Del Libertador" ocultos tras rótulos | Misma composición; rótulos de avenidas legibles; Bajo Belgrano con el mismo margen | No repite el borde forzado de fase23 | mejora |

Nota: en todas las páginas el "estado: mejora" corresponde a corrección de texto/etiquetas sobre una
composición **conservada**; ninguna página cambió de estructura, escala de mapa o distribución de cajas.

## Regresiones

**No se detectaron regresiones críticas ni medias.**

Diferencias menores aceptadas (documentadas también en el QA):

- Página 8: el recuadro "Dársena Sur" ahora pisa levemente el halo del extremo sur del eje costero; se
  consideró preferible a que pise la leyenda (situación de fase22). Severidad: baja, no bloquea.
- Los mapas de detalle son un re-render con la misma configuración; pueden existir microdiferencias de
  anti-aliasing respecto de los PNG de fase20/22, sin efecto en la lectura.

Controles de fase23 verificados en fase24 (no repetidos): recuadro de página 3 conservado ancho; mapa
general con el mismo tamaño; mapas 7-11 sin ampliaciones agresivas; "Dársena Sur" lejos del borde inferior;
Bajo Belgrano lejos del borde derecho; leyendas sin competir con rótulos de subzonas.

## Conclusión

**Fase24 está apta para reemplazar a fase22 como versión de oficina.** Mantiene todo lo que fase22 resolvía
(estructura de 11 páginas, denominación DGDGAS — Dirección General de Desarrollo Gastronómico, textos
editoriales, separaciones Corrientes/Abasto y Belgrano R/Barrio Chino, La Mar solo en Palermo / Las Cañitas),
elimina el defecto de acentos que la propia fase22 tenía observado y aplica solo las correcciones de mapas
pendientes, sin regresiones visuales.
