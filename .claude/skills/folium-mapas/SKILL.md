---
name: folium-mapas
description: >
  Mapas interactivos HTML con Folium (Leaflet): coropletas, capas de calor,
  marcadores y polígonos de polos sobre teselas de OpenStreetMap. Usar para
  exploración interactiva y entregables HTML; los mapas estáticos de informes
  PDF siguen saliendo de matplotlib/geopandas como hasta ahora.
---

# Folium — mapas interactivos HTML

Instalado en los dos venvs (`.venv` 0.20.0 y `.venv-tools`): usar `.venv\Scripts\python.exe`,
que es el mismo de geopandas y matplotlib del pipeline.

## Uso básico

```python
import folium
from folium.plugins import HeatMap

m = folium.Map(location=[-34.61, -58.42], zoom_start=12, tiles="OpenStreetMap")

# Polígonos desde GeoJSON (los GeoDataFrame van con .to_json())
folium.GeoJson("outputs/.../polos.geojson", name="Polos").add_to(m)

# Capa de calor desde puntos [[lat, lon], ...]
HeatMap(puntos, radius=12).add_to(m)

folium.LayerControl().add_to(m)
m.save("outputs/.../mapa_polos.html")
```

Ojo con el orden de coordenadas: Folium usa **[lat, lon]**; los GeoDataFrame
traen (lon, lat). Reproyectar a EPSG:4326 antes de mapear.

## Reglas propias de la herramienta

1. Atribución "© OpenStreetMap contributors" queda embebida en las teselas: no
   quitarla.
2. Mapas sobre datos internos/sensibles → guardarlos en carpeta ignorada por
   Git; un HTML interactivo expone TODOS los puntos con sus atributos en el
   fuente (guardrails 7 y 8) — revisar qué columnas van en tooltips/popups.
3. QA visual: abrir el HTML y mirarlo antes de darlo por terminado (análogo a
   la regla de QA de PDFs).
