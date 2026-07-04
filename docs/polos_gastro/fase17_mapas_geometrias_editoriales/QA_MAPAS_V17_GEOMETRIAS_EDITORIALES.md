# QA mapas V17 - geometrias editoriales PolosGastro

Fecha de control: 3 de julio de 2026.

## Resultado general

- Estado: assets creados para revision visual, sin generar PDF.
- Marca visible usada en los mapas: **DGDGAS — Dirección General de Desarrollo Gastronómico**.
- Base cartografica: callejero GCBA local ya disponible en el repo.
- Criterio: subzona aproximada de lectura, eje aproximado o area a reforzar; no limites oficiales.

## Mapas creados

- `outputs\polos_gastro\fase17_mapas_geometrias_editoriales\assets\mapa_v17_palermo_las_canitas.png` y `outputs\polos_gastro\fase17_mapas_geometrias_editoriales\assets\mapa_v17_palermo_las_canitas.svg` (3 geometria(s)).
- `outputs\polos_gastro\fase17_mapas_geometrias_editoriales\assets\mapa_v17_puerto_madero.png` y `outputs\polos_gastro\fase17_mapas_geometrias_editoriales\assets\mapa_v17_puerto_madero.svg` (3 geometria(s)).
- `outputs\polos_gastro\fase17_mapas_geometrias_editoriales\assets\mapa_v17_san_telmo.png` y `outputs\polos_gastro\fase17_mapas_geometrias_editoriales\assets\mapa_v17_san_telmo.svg` (3 geometria(s)).
- `outputs\polos_gastro\fase17_mapas_geometrias_editoriales\assets\mapa_v17_corrientes_abasto.png` y `outputs\polos_gastro\fase17_mapas_geometrias_editoriales\assets\mapa_v17_corrientes_abasto.svg` (3 geometria(s)).
- `outputs\polos_gastro\fase17_mapas_geometrias_editoriales\assets\mapa_v17_belgrano.png` y `outputs\polos_gastro\fase17_mapas_geometrias_editoriales\assets\mapa_v17_belgrano.svg` (3 geometria(s)).

Hoja de contacto:

- `outputs\polos_gastro\fase17_mapas_geometrias_editoriales\contact_sheet_mapas_v17.png`

Tabla de geometrias:

- `outputs\polos_gastro\fase17_mapas_geometrias_editoriales\tablas\geometrias_editoriales_v17.csv`

## QA visual

- [x] Se redujeron elipses como forma principal: no se usa ninguna elipse en la capa V17.
- [x] Palermo / Las Canitas usa poligonos apoyados en avenidas para Palermo Soho, Palermo Hollywood y Las Canitas.
- [x] Corrientes se representa como eje lineal claro entre 9 de Julio y Callao.
- [x] Abasto queda como area a reforzar separada del eje Corrientes.
- [x] Belgrano usa poligonos/areas orientadas por cuadras; Belgrano R queda acotado y no sobredimensionado.
- [x] San Telmo combina hito Mercado, eje Defensa y area gastronomica cercana sin circulos genericos.
- [x] Puerto Madero prioriza formas longitudinales orientadas a docks/rio.
- [x] Las etiquetas principales son legibles y no se detectan superposiciones fuertes en la hoja de contacto.
- [x] Los puntos de locales no son protagonistas: no se graficaron puntos de locales en esta pasada.
- [x] La lectura visual se acerca mas al ejemplo de Diego porque las zonas pasan de manchas a formas por calles, cuadras y ejes.

## QA editorial y privacidad

- [x] No se presentan subzonas como limites oficiales.
- [x] No se usa DataGastro como marca publica visible.
- [x] No se incluyen `place_id`, `rating`, `user_ratings_total`, raw JSON, rutas locales, API keys ni links privados en los mapas.
- [x] No se incluyen nombres de archivos CSV internos dentro de los mapas.
- [x] No se generaron capturas de Google Maps.
- [x] No se generaron datos de locales ni filas individuales sensibles.

## Alcance de ejecucion

- [x] No API.
- [x] No llamadas Google Places.
- [x] No scraping.
- [x] No PDF.
- [x] No datos fuente tocados.
- [x] No `data/` modificado.
- [x] No Cafecito, Mercados ni Casas de Pastas tocados.
- [x] No Borrador 2 ni Borrador 3 tocados.
- [x] No commit, push ni staging.

## Que mejora respecto al V4

- Palermo deja de apoyarse en elipses y usa recortes aproximados por avenidas.
- Corrientes queda como linea/eje y Abasto como area separada.
- Puerto Madero se lee como banda longitudinal y no como areas circulares.
- San Telmo y Belgrano reemplazan manchas genericas por piezas mas orientadas por cuadras.
- Los locales quedan fuera del mapa: la pieza queda mas limpia para revision institucional.

## Que sigue flojo o requiere decision

- Las geometrias siguen siendo editoriales y aproximadas; necesitan validacion humana antes de circular como PDF.
- Palermo podria requerir ajuste fino si Diego quiere incluir o excluir contexto Botanico/Palermo Chico.
- Abasto y Belgrano R siguen marcados como areas a reforzar; no conviene tratarlos como polos consolidados.
- Falta prueba de insercion en pagina A4 antes de recomendar PDF final.

## Recomendacion

Recomiendo pasar a una prueba PDF V5 solo despues de revision humana de estos cinco PNG/SVG. La base visual esta mejor encaminada que V4, pero conviene aprobar recortes y etiquetas antes de maquetar.
