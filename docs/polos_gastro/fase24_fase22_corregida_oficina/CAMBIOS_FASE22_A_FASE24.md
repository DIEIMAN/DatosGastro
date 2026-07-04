# Cambios fase22 a fase24

**Proyecto:** PolosGastro - DGDGAS
**Fecha:** 2026-07-03

## Principio de trabajo

Fase24 **parte de fase22** (`fase22_microajustes_texto_oficina`), no de fase23. Fase23 quedó documentada como
no entregable por regresiones visuales (`FASE23_NO_ENTREGABLE_REGRESIONES.md`) y solo se consultó como
referencia de lo que no debía repetirse: mapas agrandados de forma agresiva, elementos contra los bordes,
pérdida de aire visual y recuadros reducidos.

Como fase22 no dejó script de generación propio, fase24 reconstruye el PDF con el generador de la cadena
fase20 (el mismo layout que heredó fase22) y con los textos finales exactos de fase22
(`INFORME_POLOS_GASTRO_DGDGAS_PDF_BASE_11P_TEXTO.md`). Los mapas de detalle se regeneraron con la
configuración visual de los assets de fase20 usados por fase22 (misma caja, misma escala, mismas geometrías,
relación de aspecto verificada píxel a píxel contra los PNG originales), aplicando solo los microajustes
listados abajo. Script nuevo: `scripts/polos_gastro/build_fase24_fase22_corregida_oficina.py`.

## Cambios aplicados

| Página | Elemento | Cambio | Motivo | Riesgo controlado |
| --- | --- | --- | --- | --- |
| Todas | Texto del PDF | Reconstrucción con encoding correcto: los acentos que en fase22 se veían como "?" ("gastron?micos", "Direcci?n") ahora se ven correctos | Defecto real de fase22, señalado como observación en su propio cierre (`CIERRE_FASE22_BASE_OFICINA.md`) | Layout replicado del generador fase20 (origen de fase22) y verificado página a página contra los rasters de fase22 |
| 5 | Etiqueta "Abasto" (mapa global) | Reubicada debajo-izquierda de su elipse, con línea guía | En fase22 pisaba la etiqueta "Corrientes" | Solo cambia el offset de una etiqueta; el mapa (base, áreas, ejes, encuadre, recorte) es el mismo |
| 5 | Etiqueta "DoHo" (mapa global) | Reubicada arriba-derecha de su eje | En fase22 quedaba encimada con "Villa Urquiza" | Ídem: solo offset de etiqueta |
| 5 | Leyenda del mapa global | "Área / barrio de lectura", "Macroárea con subzonas", "Área aproximada" con tildes; etiqueta "Villa Pueyrredón / San Martín" con tildes | Consistencia de tildes en piezas visibles | Cambio tipográfico puro |
| 7 | Rótulo "Av. Córdoba" | Tilde agregada y reubicado hacia el sureste, sobre la misma avenida | En fase22 quedaba parcialmente tapado por la leyenda y sin tilde | El rótulo sigue sobre la traza de la avenida, lejos de bordes |
| 7 | Rótulo "Scalabrini Ortiz" | Reubicado a la derecha del polígono de Palermo Soho | En fase22 quedaba oculto detrás del rótulo "Palermo Soho" | Solo posición del rótulo de calle |
| 7 | Rótulo "Juan B. Justo" | Reubicado por encima del rótulo "Palermo Hollywood" | En fase22 quedaba oculto detrás de ese rótulo | Solo posición del rótulo de calle |
| 8 | Rótulo "Dársena Sur" | Desplazado hacia el este, dentro de su área | En fase22 pisaba la leyenda del mapa | Se mantiene el mismo encuadre; no se repite el error de fase23 (área contra el borde inferior) |
| 8 | Rótulo vertical "frente costero" | Corrido levemente hacia la franja de agua | En fase22 quedaba parcialmente cubierto por la banda de Docks | Sigue con margen respecto del borde derecho |
| 9 | Rótulos internos del mapa | "Área gastronómica", "Casco histórico / Defensa" con tildes; rótulo de calle "Paseo Colón" con tilde | Tildes internas del mapa pendientes desde fase22 | Mismas posiciones y tamaños |
| 9 | Rótulo "Chile" | Reubicado fuera del recuadro "Área gastronómica" | En fase22 quedaba oculto detrás del recuadro | Solo posición del rótulo de calle |
| 7-11 | Leyenda de mapas de detalle | "área de lectura" con tilde | Consistencia de tildes | Cambio tipográfico puro |
| 7-11 | Tags de zonas | "ÁREA DE LECTURA" con tilde (antes "AREA DE LECTURA") | Consistencia de tildes | Cambio tipográfico puro |
| 10 | Etiqueta chica "Abasto" | Eliminada la etiqueta de calle duplicada dentro del área Abasto | Redundante con el rótulo grande "Abasto" y rozaba el borde punteado del área | El área, su rótulo principal y la separación con Corrientes no cambian |
| 11 | Rótulos "Juramento" y "Del Libertador" | Reubicados en tramos libres de sus avenidas | En fase22 quedaban ocultos detrás de "Barrio Chino" y "Bajo Belgrano" | Solo posición de rótulos de calle; los tres sectores no se tocaron |

## Cambios NO aplicados

| Página | Observación | Motivo por el cual no se aplicó |
| --- | --- | --- |
| 8 | "Sector costero" queda cerca del borde derecho | Está igual que en fase22 y se lee bien; moverlo hacia adentro taparía "Juana Manso" o el eje costero. Criterio: si la corrección genera regresión, no se aplica |
| 8 | "A. Moreau de Justo" y "Juana Manso" parcialmente cubiertas | Igual que en fase22; reubicarlas agrega ruido en la franja más densa del mapa sin ganancia real de lectura |
| 5 | Densidad de etiquetas de la zona centro del mapa global | Es la composición heredada de fase22; redistribuir más etiquetas excede el criterio de intervención mínima |
| 7-11 | Agrandar los mapas o llevar elementos hacia los bordes | Fue exactamente la regresión de fase23; fase24 conserva escala, márgenes y aire de fase22 |
| 3 | Rediseño del recuadro institucional | Fase22 ya estaba bien; fase23 lo empeoró al achicarlo. Se conservó el de fase22 |

## Confirmación

- No se tocaron datos fuente (`data/`, geojson fuente, CSV de fases previas: solo lectura).
- No se usaron fuentes externas, APIs, Google Places ni scraping.
- No se modificó ninguna fase anterior (fase22 y fase23 quedan intactas).
- No se tocaron Cafecito, Mercados, Casas de Pastas, Borrador 2 ni Borrador 3.
- No hubo commit, push ni staging; no se usó `git add .`.
