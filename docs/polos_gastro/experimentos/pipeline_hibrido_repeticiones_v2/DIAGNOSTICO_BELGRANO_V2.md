# Diagnóstico Belgrano v2

Estado: **EXPERIMENTAL / NO OFICIAL**. Se ejecutaron BEL-R01…BEL-R15 sobre el contenedor actual y el barrio oficial completo como contraste, sin imponer nombres.

## Resultado

Se identificaron 17 estructuras candidatas: 6 ALTA, 8 MEDIA y 3 BAJA. Los identificadores son exclusivamente técnicos.

La grilla HDBSCAN incluyó `eom` y `leaf`, la red usó umbrales derivados de distancias locales, Louvain se repitió con 20 semillas, KDE se usó como contraste y el bootstrap espacial se ejecutó con bloques de 150/200/300/400 m y 50 repeticiones por tamaño.

## Interpretación

La categoría de cada núcleo combina supervivencia, variación del centro y extensión, respaldo KDE, mezcla de fuentes y dependencia del contenedor. Ninguna categoría se asignó por cantidad deseada de núcleos. BEL-R14 queda como contraste post hoc; los nombres urbanos no entraron al algoritmo ni a las salidas.

## Límite

Places representa 56.4% del universo del contenedor actual. Las estructuras `places_dependiente` no son aptas para promoción firme.
