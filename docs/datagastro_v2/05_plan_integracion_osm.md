# DataGastro V2 — Plan de integración OpenStreetMap (OSM)

> **Plan, no ejecución.** OSM es **fuente abierta auxiliar** (E02). Aporta cobertura
> colaborativa, geometría y tags de rubro. No es oficial ni completa.

## 1. Encuadre

- Rol: **auxiliar y de contraste**, no fuente primaria.
- Licencia: ODbL. Uso compatible con un proyecto de inteligencia territorial; **se cita la
  fuente** y se respeta atribución. Verificar atribución antes de cualquier publicación.
- Acceso planificado por **Overpass API** (lectura de datos abiertos) y/o extractos `.pbf` de
  CABA. **No** scraping del sitio web.

## 2. Cómo se consulta (planificado)

- **Overpass API** con bounding box / límites de CABA, filtrando por tags gastronómicos.
- Alternativa offline: descargar el extracto regional (Geofabrik) y filtrar localmente —
  evita carga sobre el servidor público de Overpass.
- Topes y pausas análogos a Places (consultas acotadas, sin barridos masivos innecesarios).

## 3. Tags OSM → taxonomía v2

| Tag OSM | Subcategoría v2 (tentativa) | Confianza local |
|---|---|---|
| `amenity=restaurant` | restaurantes | tag fuerte |
| `amenity=cafe` | cafeterías | tag fuerte |
| `amenity=bar` / `amenity=pub` | bares | tag fuerte |
| `amenity=fast_food` | takeaway_delivery (rotiserías/empanadas) | tag medio |
| `amenity=ice_cream` | heladerías | tag fuerte |
| `shop=bakery` | panaderías | tag fuerte |
| `shop=pastry` / `shop=confectionery` | pastelerías / confiterías | tag fuerte |
| `shop=pasta` | casas_de_pastas | tag fuerte |
| `shop=chocolate` | chocolaterías | tag fuerte |
| `shop=wine` | vinotecas | tag fuerte |
| `shop=cheese` | queserías | tag fuerte |
| `shop=deli` | charcuterías / almacenes_gastronómicos | tag medio |
| `craft=caterer` / `craft=bakery` | obradores / producción | tag medio |
| `shop=coffee` / `craft=coffee_roaster` | cafeterías_de_especialidad / tostadores | tag medio |

El mapeo completo se versiona como archivo de configuración (no sensible). Tags ausentes o
genéricos ⇒ `pendiente_revision_taxonomica`.

## 4. Campos a extraer

```text
osm_id, osm_type (node/way/relation), name, tags relevantes (amenity/shop/craft/cuisine),
lat, lon, addr:* (cuando exista), source/operator (para detectar cadenas).
```

`osm_id` + `osm_type` es la clave estable para deduplicación intra-OSM.

## 5. Deduplicación e integración con otras fuentes

- Intra-OSM: por (`osm_type`,`osm_id`).
- Inter-fuente: misma heurística conservadora de §5 del plan de Places (nombre+dirección
  normalizados + distancia + similitud). Un mismo local detectado por OSM **y** Google **y**
  AGC ⇒ confianza C5 multifuente.
- OSM solo, con tag fuerte ⇒ C3 `auxiliar_abierto`. No se descarta por ser única fuente.

## 6. Detección de cadenas con OSM

- `operator` / `brand` (cuando existen) son señal directa de marca.
- Repetición de `name` normalizado en ≥2 elementos ⇒ candidato a cadena (se cruza con la
  detección de Places).

## 7. Brutos y sanitización

```text
outputs/v2_osm/                      (GITIGNORED)
  raw/<consulta>.json|.csv           respuesta cruda
  candidatos.csv                     normalizados + mapeados a taxonomía v2
  resumen.csv                        conteos por tag/subcategoría
```

OSM es dato abierto, pero los **agregados con dirección** se tratan con el mismo cuidado: a
entregables externos sólo van **conteos y densidades**, no filas individuales con dirección.

## 8. Límites de OSM (a declarar siempre)

- **Cobertura desigual:** zonas céntricas mejor mapeadas que periféricas → sesgo territorial.
- **Calidad variable:** tags incompletos, nombres desactualizados, locales cerrados sin
  actualizar.
- **No mide actividad:** la presencia de un nodo no prueba que el local esté abierto hoy.
- Por eso OSM **complementa**, nunca sustituye, a AGC ni a la validación territorial.
