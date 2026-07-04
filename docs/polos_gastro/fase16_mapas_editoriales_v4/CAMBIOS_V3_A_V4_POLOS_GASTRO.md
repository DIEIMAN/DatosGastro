# Cambios V3 a V4 - PolosGastro DGDGAS

## Qué cambió

- Se creó una Fase 16 paralela con mapas editoriales de subzonas.
- Se mantuvo el mapa global de 22 polos/ejes.
- Se reemplazaron los cinco mapas de detalle por piezas donde predominan áreas coloreadas y etiquetas grandes.
- Los puntos dejaron de ser el elemento principal: las menciones quedan en cajas laterales del PDF.
- Se creó una tabla de subzonas y un GeoJSON con geometrías aproximadas para trazabilidad.
- Se conserva el aporte del callejero V3: avenidas y calles principales siguen como soporte de orientación urbana.
- Se ajustaron posiciones manuales de etiquetas y se ocultaron rótulos contextuales cuando recargaban el mapa.

## Por qué se abandonó la centralidad de los puntos

El PDF anterior incorporó callejero, y ese avance se conserva porque ayuda a leer la trama urbana. Lo que se corrige es la prolijidad visual: evitar etiquetas amontonadas, priorizar nombres de subzona, reducir puntos y sacar nombres de locales del mapa. Para una pieza ejecutiva, el objetivo es entender zonas, ejes y relaciones territoriales. Por eso el mapa pasa a mostrar áreas de lectura, subzonas y ejes aproximados, mientras que los nombres de locales quedan como menciones destacadas fuera del mapa.

## Cómo se construyeron las subzonas aproximadas

Las geometrías se armaron con coordenadas de referencia, barrios/comunas como marco, callejero GCBA, puntos sanitizados como apoyo indirecto y criterio editorial documentado. Se usaron elipses, polígonos y ejes aproximados. No son límites oficiales ni deben tratarse como delimitaciones normativas.

## Mapas generados

- Palermo / Las Cañitas: 5 subzonas/ejes editoriales visibles.
- Puerto Madero: 4 subzonas/ejes editoriales visibles.
- San Telmo: 4 subzonas/ejes editoriales visibles.
- Corrientes / Abasto: 4 subzonas/ejes editoriales visibles.
- Belgrano: 4 subzonas/ejes editoriales visibles.

## Qué mapas quedaron más claros

- Palermo / Las Cañitas: ahora separa Palermo Soho, Palermo Hollywood y Las Cañitas con etiquetas grandes; las áreas contextuales quedan coloreadas sin forzar rótulos.
- Puerto Madero: se entiende mejor como banda de docks y eje costero.
- San Telmo: el Mercado aparece como hito colectivo y el casco histórico ordena la lectura.
- Corrientes / Abasto: muestra vínculo, pero diferencia el eje Corrientes del área Abasto.
- Belgrano: separa Barrio Chino, Bajo Belgrano y Belgrano R, con Belgrano R como subzona a reforzar.

## Limitaciones que siguen

- Las subzonas son aproximadas y no límites oficiales.
- No se valida actividad vigente de locales.
- Abasto y Belgrano R requieren decisión humana antes de una versión final.
- Las menciones destacadas siguen siendo universo semilla, no padrón operativo.

## Qué queda para decisión final con Ale

- Cerrar si Abasto queda como área vinculada o página propia.
- Decidir si Belgrano R sigue visible o pasa a nota.
- Validar si Palermo requiere todas las subzonas contextuales o solo las principales.
- Definir nivel final de color y densidad de etiquetas para circulación institucional.
