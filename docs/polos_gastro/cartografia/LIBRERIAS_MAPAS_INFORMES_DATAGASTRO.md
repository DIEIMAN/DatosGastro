# Librerías de mapas para informes DataGastro

Fecha de evaluación: 2026-06-29.

Comparación de opciones para producir mapas en informes DataGastro (estáticos para PDF e
interactivos para exploración). Se prioriza lo **ya disponible** y lo **reproducible en Windows**
sin browser headless.

## Disponibilidad ya verificada en el `.venv` del proyecto

| Librería | Estado en `.venv` |
| --- | --- |
| matplotlib | ✅ instalada |
| pandas | ✅ |
| geopandas | ✅ |
| shapely | ✅ |
| pyproj | ✅ |
| folium | ✅ |
| pydeck | ✅ |
| contextily | ❌ (no instalada) |
| fiona | ❌ |
| plotly | ❌ |
| leafmap | ❌ |
| lonboard | ❌ |

GeoPandas + matplotlib ya están listos: el camino de mapas estáticos no requiere instalar nada
nuevo (salvo contextily si se quiere fondo de tiles). Confirmar guardrails antes de instalar.

---

## Python / estático

| Opción | Calidad visual | Facilidad aquí | PDF estático | HTML interactivo | Dep. internet | Complejidad | Riesgos | Recomendación |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **GeoPandas** | Alta | **Alta (ya instalada)** | Sí | No | No (con GeoJSON local) | Baja-media | Necesita GeoJSON de barrios/comunas | **Núcleo del enfoque estático** |
| **matplotlib + GeoPandas** | Alta, control total | **Alta** | **Sí (ideal)** | No | No | Media | Estilo manual | **Recomendado para PDF** |
| **contextily** | Alta (fondo de tiles real) | Media (hay que instalarla) | Sí | No | **Sí (tiles)** | Media | CRS EPSG:3857; internet | Opcional, para fondo institucional GCBA |
| **folium** | Buena | **Alta (ya instalada)** | No directo (es HTML) | **Sí** | Sí (tiles) | Baja | Screenshot requiere browser headless | Bueno para interactivo rápido |
| **plotly** | Alta | Media (instalar) | Parcial (necesita kaleido) | Sí | Según basemap | Media | Export estático extra | Alternativa, no prioritaria |
| **pydeck** | Alta (3D/WebGL) | Media (ya instalada) | No | Sí | Sí | Media-alta | Orientado a grandes volúmenes | Sobra para 32 polos |
| **lonboard** | Alta (WebGL) | Baja (instalar) | No | Sí | Sí | Media-alta | Pensado para millones de puntos | No necesario |
| **leafmap** | Alta | Baja (instalar, trae mucho) | Parcial | Sí | Sí | Alta | Dependencias pesadas | No necesario para este alcance |

## JavaScript / interactivo

| Opción | Calidad visual | Facilidad aquí | PDF | HTML interactivo | Dep. internet | Complejidad | Riesgos | Recomendación |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Leaflet** | Alta | Media | No (necesita captura) | **Sí** | Sí (tiles) | Media | — | Estándar interactivo |
| **@usig-gcba/mapa-interactivo** | Alta, **identidad GCBA de fábrica** | Media (ya instalada) | Solo vía headless | **Sí** | Sí (GCBA) | Media | Node viejo; requiere DOM | **Mejor opción institucional interactiva** |
| **MapLibre GL JS** | Muy alta (vector tiles) | Media-baja | No | Sí | Sí | Alta | Más setup | Futuro dashboard de alta calidad |
| **deck.gl** | Muy alta (WebGL) | Baja | No | Sí | Sí | Alta | Sobredimensionado | No necesario |
| **Observable / notebooks** | Alta | — | No | Sí | Sí | — | Solo referencia | Inspiración, no entrega |

## Enfoque institucional GCBA

- **USIG tiles** (`mapa_base_v2` GeoServer): fondo con identidad oficial; usable desde
  contextily (estático) o Leaflet/MapLibre/USIG (interactivo). Atribución GOED/GCBA/OSM.
- **Buenos Aires Data GeoJSON** (barrios, comunas): geometrías oficiales, livianas, estándar.
- **Paleta DataGastro**: ya usada en los gráficos actuales (`#275DAD` azul núcleo, `#2A9D8F`
  verde, `#E9B44C` amarillo, `#7D8597` gris, `#C44536` rojo). Reutilizable para choropleths y
  marcadores por nivel de evidencia.

---

## Recomendación concreta

- **Mejor opción para PDFs estáticos**: **GeoPandas + matplotlib**, con barrios/comunas GeoJSON
  de Buenos Aires Data como capa base. Ya está todo instalado salvo contextily (opcional para
  fondo de tiles GCBA). Reproducible en Windows, sin browser, encaja con el pipeline actual de
  PNG por script.
- **Mejor opción para exploración interactiva**: **folium** (ya instalada) para prototipos
  rápidos, o **`@usig-gcba/mapa-interactivo`** si se quiere la identidad GCBA y capas oficiales.
- **Mejor opción para futuro dashboard**: **`@usig-gcba/mapa-interactivo`** (institucional) o
  **MapLibre GL JS** (máxima calidad vector) si el dashboard crece.
- **Qué probar primero en PolosGastro**: un mapa estático **GeoPandas + matplotlib** que pinte
  los barrios asociados a cada polo del núcleo principal, coloreados por `grupo_informe`, con la
  advertencia metodológica visible. Sin geocodificar locales, sin polígonos inventados:
  solo límites barriales oficiales etiquetados como aproximación, no como delimitación del polo.

> Ver el detalle de cómo evitar mapas falsamente precisos en
> `PROPUESTA_VISUAL_INFORME_POLOS_GASTRO.md`.
