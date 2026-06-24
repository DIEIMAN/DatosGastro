# Mercados gastronómicos CABA — Plan OpenStreetMap (no ejecución)

> **Plan, no ejecución.** No se consulta Overpass, no hay requests. OSM es **fuente abierta
> auxiliar** (ODbL, con atribución). Acceso por Overpass API o extracto regional; **sin**
> scraping del sitio.

## 1. Rol
Cobertura auxiliar y geometría de los **mercados gastronómicos** y espacios tipo mercado con eje
gastronómico, para contrastar con F03 y con Google. No es oficial ni completa.

## 2. Tags candidatos → tipología

| Tag OSM | Mapea a (tentativo) | Confianza |
|---|---|---|
| `amenity=marketplace` | mercado (público/productores/alimentario) | media (verificar foco gastronómico) |
| `amenity=food_court` | food_hall | fuerte |
| `shop=*` con `name~Mercado` y señal gastronómica (`shop=deli/greengrocer/butcher/bakery/food`) | mercado_gastronomico_privado / barrial_alimentario | débil-media |
| `landuse=retail` (con `name~Mercado` + señal gastronómica) | espacio_tipo_mercado_gastronomico | débil |
| `tourism=attraction` (con `name~Mercado` + oferta gastronómica) | mercado_turistico_gastronomico | débil |
| `name~Mercado` (regex en nombre) | candidato a revisar foco gastronómico | débil |

`shop=*`, `landuse=retail` y `tourism=attraction` solo se consideran si el **nombre** contiene
"Mercado/Market" **y** hay señal de eje gastronómico/alimentario; si no, no entran (evita falsos
positivos). Los `amenity=marketplace` sin señal gastronómica quedan `dudoso_pendiente_revision`
hasta verificar; los de pulgas/antigüedades, `fuera_de_alcance_no_gastronomico`.

## 3. Consulta (planificada)
- Overpass con bounding box / límites de CABA, filtrando por los tags de arriba.
- Alternativa offline: extracto regional (Geofabrik) filtrado localmente.
- Consultas acotadas, sin barridos innecesarios.

## 4. Campos a extraer
`osm_id`, `osm_type`, `name`, tags (`amenity`/`shop`/`tourism`/`landuse`), `lat`, `lon`,
`addr:*` (si existe), `operator`/`brand` (para gestión/cadena).

## 5. Deduplicación e integración
Por (`osm_type`,`osm_id`) intra-OSM; contra F03/Google por nombre+dirección normalizados +
distancia. Coincidencia multifuente **sube** confianza.

## 6. Límites a declarar
Cobertura desigual (mejor en zonas céntricas), tags incompletos, posibles espacios cerrados sin
actualizar. OSM **complementa**, no sustituye a las fuentes oficiales ni a la validación
territorial.

## 7. Brutos y sanitización
Brutos a `outputs/mercados_caba/internal/` o `raw/` (gitignored). A entregables solo conteos y
geometría agregada; sin direcciones individuales innecesarias.
