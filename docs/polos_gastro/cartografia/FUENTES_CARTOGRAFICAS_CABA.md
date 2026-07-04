# Fuentes cartográficas oficiales de CABA

Fecha de relevamiento: 2026-06-29.

Inventario de fuentes cartográficas oficiales de la Ciudad de Buenos Aires útiles para futuros
mapas de DataGastro / PolosGastro. **No se descargó ningún paquete de datos** en esta fase: solo
se documentaron URLs verificadas y su utilidad. Las URLs de Buenos Aires Data y USIG se
confirmaron por búsqueda; los IDs de recurso GeoJSON corresponden a los datasets oficiales.

Guardrail aplicable: las descargas de geodata, cuando se autoricen, deben citar fuente, fecha y
licencia, y **no** convertir delimitaciones turísticas en límites oficiales.

---

## Buenos Aires Data (portal de datos abiertos)

| Fuente | URL | Tipo | Para informes | Mapas estáticos | Mapas interactivos | Limitaciones | Recomendación |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **Barrios** (dataset) | https://data.buenosaires.gob.ar/dataset/barrios | dataset (varios formatos) | Alta — base de límites barriales oficiales (48 barrios) | Sí | Sí | Barrios administrativos ≠ polos gastronómicos | **Base recomendada** para todo mapa por barrio |
| **Barrios — GeoJSON** | https://data.buenosaires.gob.ar/dataset/barrios/resource/1c3d185b-fdc9-474b-b41b-9bd960a3806e | GeoJSON | Alta | Sí (GeoPandas) | Sí (Leaflet/MapLibre) | — | **Capa base preferida** |
| **Comunas** (dataset) | https://data.buenosaires.gob.ar/dataset/comunas | dataset | Alta — 15 comunas (Ley 1777) | Sí | Sí | Comuna agrupa varios barrios | Útil para lectura agregada |
| **Comunas — GeoJSON** | https://data.buenosaires.gob.ar/dataset/comunas/resource/b0b627ac-5b47-4574-89ac-6999b63598ee | GeoJSON | Alta | Sí | Sí | — | Buena para mapas de contexto |
| **Comunas — SHP** | https://data.buenosaires.gob.ar/dataset/comunas/resource/Juqdkmgo-612222-resource | Shapefile | Media | Sí | Indirecto | Requiere GeoPandas/QGIS | Alternativa si se prefiere SHP |
| **API Geocodificador CABA** | https://data.buenosaires.gob.ar/dataset/api-geocodificador-direcciones-caba | API | Solo si se geocodifica (no ahora) | — | — | **No usar en esta fase** (no geocodificar locales) | Roadmap futuro autorizado |
| **API Normalización AMBA** | https://data.buenosaires.gob.ar/dataset/api-normalizacion-direcciones-amba | API | Solo roadmap | — | — | Igual que arriba | Roadmap futuro |

> Nota: hay otros datasets geo en el portal (sedes comunales, puntos verdes, etc.) que no
> aplican a PolosGastro pero confirman que el portal sirve GeoJSON estándar.

## USIG / GCBA (servicios e infraestructura geo)

| Fuente | URL | Tipo | Para informes | Mapas estáticos | Mapas interactivos | Limitaciones | Recomendación |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **Portal USIG** | https://usig.buenosaires.gob.ar/ | documentación / APIs | Referencia | — | — | — | Punto de entrada a servicios geo del GCBA |
| **Normalizador de direcciones** | http://servicios.usig.buenosaires.gob.ar/normalizar | API / JS | Solo roadmap (no geocodificar ahora) | — | — | No usar en esta fase | Futuro, si se autoriza |
| **Geocoder USIG** | http://ws.usig.buenosaires.gob.ar/geocoder/2.2 | API | Solo roadmap | — | — | No usar en esta fase | Futuro |
| **Tiles base GCBA (GeoServer)** | https://geoserver.buenosaires.gob.ar/geoserver/gwc/service/tms/1.0.0/catalogo_mapa_base%3Amapa_base_v2@EPSG%3A900913@png/{z}/{x}/{y}.png | tiles XYZ/TMS | Media-alta (fondo de mapa) | Sí (vía contextily) | Sí (Leaflet/MapLibre) | Requiere internet; respetar atribución | **Fondo institucional** para mapas con identidad GCBA |
| **Tiles temáticos USIG (mapcache)** | http://tiles1.usig.buenosaires.gob.ar/mapcache/tms/... | tiles | Según capa | Sí | Sí | HTTP (no HTTPS) en algunos endpoints | Capas temáticas puntuales |
| **Mapa Interactivo BA (capas)** | http://epok.buenosaires.gob.ar/mapainteractivoba/layers | API catálogo | Referencia | — | Sí (vía `@usig-gcba/mapa-interactivo`) | — | Catálogo de capas públicas |
| **Visor Mapa Interactivo BA** | https://mapa.buenosaires.gob.ar/ | visor web | Referencia visual | — | — | No es dato descargable | Inspiración de estilo |

**Atribución obligatoria** al usar la base GCBA: *GOED (GCBA) © OpenStreetMap (ODbL)*.

## IDECBA / Banco de mapas

| Fuente | URL | Tipo | Utilidad | Recomendación |
| --- | --- | --- | --- | --- |
| IDECBA (Infraestructura de Datos Espaciales CABA) | https://www.idecba.buenosaires.gob.ar/ | visor / catálogo geo | Catálogo de capas oficiales adicionales (uso del suelo, equipamiento, etc.) | Revisar si se necesitan capas temáticas; verificar disponibilidad y formato antes de usar |

> Verificar el estado de IDECBA antes de depender de él: los portales del GCBA cambian de URL.
> No tratarlo como confirmado hasta abrirlo y comprobar la capa concreta que se busque.

---

## Síntesis de recomendación

- **Capa base para mapas de PolosGastro**: **Barrios GeoJSON** de Buenos Aires Data (límites
  oficiales), con **Comunas GeoJSON** para la vista agregada. Son lo más estable, abierto y
  fácil de usar con GeoPandas.
- **Fondo de mapa con identidad GCBA** (si se quiere "look" institucional): tiles
  `mapa_base_v2` de GeoServer GCBA, vía contextily (estático) o Leaflet/MapLibre (interactivo),
  citando la atribución GOED/GCBA/OSM.
- **Geocodificación (USIG geocoder / normalizador)**: **no en esta fase** — el objetivo actual
  excluye geocodificar locales. Queda en roadmap, solo si Diego lo autoriza.
- **Qué descargar cuando se autorice**: únicamente `barrios.geojson` y `comunas.geojson`
  (livianos), guardándolos con su fecha y fuente. Nada de paquetes grandes innecesarios.

**Sources:**
- [Buenos Aires Data — Barrios](https://data.buenosaires.gob.ar/dataset/barrios)
- [Buenos Aires Data — Barrios (GeoJSON)](https://data.buenosaires.gob.ar/dataset/barrios/resource/1c3d185b-fdc9-474b-b41b-9bd960a3806e)
- [Buenos Aires Data — Comunas](https://data.buenosaires.gob.ar/dataset/comunas)
- [Buenos Aires Data — Comunas (GeoJSON)](https://data.buenosaires.gob.ar/dataset/comunas/resource/b0b627ac-5b47-4574-89ac-6999b63598ee)
- [Portal USIG](https://usig.buenosaires.gob.ar/)
- [API Geocodificador CABA](https://data.buenosaires.gob.ar/dataset/api-geocodificador-direcciones-caba)
