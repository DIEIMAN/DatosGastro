---
name: osmnx
description: >
  Mapeo geoespacial con OpenStreetMap vía OSMnx: polígonos de barrios/zonas,
  red de calles y POIs gastronómicos (amenity=restaurant/cafe/bar/fast_food).
  Usar para análisis territorial de polos gastronómicos con datos abiertos de OSM.
  Fuente abierta y publicable; clasificarla como fuente externa abierta según la
  metodología de fuentes de DataGastro.
---

# OSMnx — polígonos urbanos y POIs de OpenStreetMap

Instalado en `.venv-tools` (el venv del pipeline no se toca). Ejecutar con
`.venv-tools\Scripts\python.exe`.

## Uso básico

```python
import osmnx as ox

# POIs gastronómicos de un barrio
tags = {"amenity": ["restaurant", "cafe", "bar", "fast_food"]}
gdf = ox.features_from_place("Palermo, Buenos Aires, Argentina", tags)

# Polígono de un barrio
barrio = ox.geocode_to_gdf("San Telmo, Buenos Aires, Argentina")

# Red de calles
G = ox.graph_from_place("Boedo, Buenos Aires, Argentina", network_type="walk")
```

## Reglas DataGastro

1. OSM es dato abierto (ODbL): citable y publicable, con atribución
   "© OpenStreetMap contributors" en mapas e informes.
2. Un POI de OSM es "registro en OSM", no "local activo" (guardrail 5); la
   completitud de OSM en CABA es despareja por zona — declararlo como límite.
3. Nominatim (geocoder de OSM) tiene rate limit: máx. 1 request/segundo.
4. Para cruces con la base del proyecto, usar los criterios de
   `docs/skills_claude/05_geodatos_y_territorio.md` (CRS, sesgos territoriales).
