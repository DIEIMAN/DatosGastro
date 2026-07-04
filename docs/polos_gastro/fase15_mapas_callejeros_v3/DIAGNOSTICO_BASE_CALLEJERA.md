# Diagnóstico de base callejera V3 - PolosGastro DGDGAS

Fecha de trabajo: 3 de julio de 2026.

## Capas geo existentes en el repo

| Capa | Ruta | Estado | Uso |
| --- | --- | --- | --- |
| Barrios CABA | `data/raw/geo_barrios.geojson` | sí | Marco territorial oficial por barrio. |
| Comunas CABA | `data/raw/geo_comunas.geojson` | sí | Marco territorial oficial por comuna. |
| Callejero GCBA | `outputs/polos_gastro/fase15_mapas_callejeros_v3/assets/callejero_gcba_2026_06_02.geojson` | sí | Base callejera de detalle para mapas V3. |

## ¿Hay una capa de calles ya disponible?

Al iniciar la fase no había una capa de calles descargada en `data/` ni en las fases previas de PolosGastro. Se detectaban capas de barrios y comunas, pero no un callejero completo.

Para cumplir el objetivo V3 se descargó una copia del recurso público **Callejero (GeoJson)** del dataset **Calles** de Buenos Aires Data, dentro de la carpeta de outputs de esta fase. No se modificó `data/` ni ninguna fuente original del proyecto.

## ¿Alcanza con barrios/comunas para marco?

Barrios y comunas alcanzan para marco territorial general y para el mapa global, pero no alcanzan para los zooms de detalle. Para las páginas 7 a 11 se requiere trama urbana: calles, avenidas, docks, ejes y referencias de cuadras.

## Fuente usada para calles

- Fuente: Buenos Aires Data / GCBA, dataset **Calles**, recurso **Callejero (GeoJson)**.
- URL dataset: https://data.buenosaires.gob.ar/dataset/calles
- URL de descarga usada: https://cdn.buenosaires.gob.ar/datosabiertos/datasets/jefatura-de-gabinete-de-ministros/calles/callejero.geojson
- Responsable informado por el portal: Jefatura de Gabinete de Ministros; Secretaría de Innovación y Transformación Digital; DG Gobernanza de Datos Abiertos; Gerencia Operativa de Explotación de Datos Geoespaciales.
- Licencia informada por el portal: **CC-BY-2.5-AR**.
- Fecha de publicación del dataset informada por el portal: 10 de mayo de 2021.
- Fecha de actualización informada por el portal: 2 de junio de 2026.
- Fecha de descarga local para esta fase: 3 de julio de 2026.

## Limitaciones

- El callejero se usa como contexto visual, no como fuente para validar locales ni actividad vigente.
- Los mapas de detalle simplifican la red vial para lectura en PDF: se muestran calles suaves, avenidas más visibles y pocas etiquetas.
- Las subzonas de Palermo, Belgrano, Corrientes/Abasto y Puerto Madero son lecturas preliminares, no delimitaciones oficiales.
- Los puntos provienen de la capa auxiliar ya sanitizada y no constituyen padrón oficial.
- No se ejecutaron APIs ni llamadas Google Places en esta fase.
