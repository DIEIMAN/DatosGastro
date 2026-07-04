# Cartografía usada — Fase 4A

Fecha de consulta/descarga: 2026-06-29.

Cartografía oficial de CABA usada como **base territorial de referencia** para el mapa estático
de PolosGastro. Descargada y guardada **solo** dentro de `PolosGastro/cartografia/` (no en `data/`).

## Fuentes descargadas

| Capa | URL | Formato | Features | Guardado en |
| --- | --- | --- | --- | --- |
| Barrios CABA | https://cdn.buenosaires.gob.ar/datosabiertos/datasets/ministerio-de-educacion/barrios/barrios.geojson | GeoJSON (EPSG:4326) | 48 barrios | `PolosGastro/cartografia/barrios_caba.geojson` |
| Comunas CABA | https://cdn.buenosaires.gob.ar/datosabiertos/datasets/ministerio-de-educacion/comunas/comunas.geojson | GeoJSON (EPSG:4326) | 15 comunas | `PolosGastro/cartografia/comunas_caba.geojson` |

Datasets de referencia en el portal: Buenos Aires Data — Barrios
(https://data.buenosaires.gob.ar/dataset/barrios) y Comunas
(https://data.buenosaires.gob.ar/dataset/comunas).

## Uso

- **Barrios** como base territorial del mapa estático: se pintan en gris los 48 barrios y se
  resaltan por color los barrios **asociados** a polos del núcleo, zonas relevantes y candidatos.
- **Comunas**: descargadas como respaldo; en esta fase el mapa usa barrios (más granular).
- Reproyección a EPSG:3857 para el render.

## Limitaciones

- Los barrios son unidades administrativas: **el barrio asociado no es el polo**. Varios polos
  comparten un mismo barrio (p. ej. Palermo Soho/Hollywood/Las Cañitas → barrio Palermo).
- No hay polígonos de polos: no existe geometría oficial de polo gastronómico.
- Subzonas (Barrio Chino, Microcentro, Costanera Norte) se aproximan al barrio que las contiene.

## Atribución

**Buenos Aires Data — Gobierno de la Ciudad de Buenos Aires.** Datos abiertos (barrios y comunas
de CABA). Citar la fuente y la fecha de descarga en cualquier uso.

## Advertencia metodológica

> **Base territorial de referencia, no delimitación oficial de polos.** Los barrios/comunas se
> usan para ubicar y contextualizar; no representan los límites de los polos gastronómicos, que
> **no** tienen delimitación oficial. No deben leerse como polígonos de polos ni como padrón.
