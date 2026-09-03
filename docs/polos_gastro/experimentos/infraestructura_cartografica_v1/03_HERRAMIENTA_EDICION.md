# Herramienta de edición de contornos (Etapa Infra-3)

**Fecha:** 2026-07-08 · **Carácter:** propuesta de flujo de trabajo, no de aplicación
nueva. Conclusión del inventario (Infra-1): ninguna librería ya instalada en el proyecto
sirve para **editar** vértices de polígono (USIG mapa-interactivo y Leaflet solo
visualizan). No hace falta desarrollarla: existen herramientas maduras y gratuitas que
resuelven exactamente esto.

## Recomendación: QGIS como herramienta principal

**QGIS** (gratuito, open source, probablemente ya conocido en el equipo) resuelve las 5
capacidades pedidas sin desarrollo nuevo:

| Capacidad pedida | Cómo la cubre QGIS |
|---|---|
| Visualizar callejero | Cargar `callejero_referencia.geojson` del kit (Etapa Infra-3 abajo) como capa de líneas |
| Visualizar locales gastronómicos | Cargar `entidades_universo_v1.geojson`, simbolizar por categoría o por cluster |
| Visualizar microclusters | Cargar `microclusters_hdbscan.geojson` (o `poligonos_prototipo_v1.geojson`), simbolizar por `cluster_id` |
| Editar vértices | Capa vectorial nueva (`Capa > Crear capa > Capa vectorial nueva`, tipo polígono) + herramienta nativa "Editar vértices" (edición de nodos con snapping a la capa de calles) |
| Exportar GeoJSON | `Clic derecho en la capa > Exportar > Guardar objetos como... > GeoJSON` |

**Ventaja clave para este proyecto:** el snapping de QGIS a la capa de calles permite
trazar el polígono **literalmente sobre las esquinas reales** del callejero GCBA, en vez
de aproximar a ojo — resuelve de raíz el problema identificado en Infra-1 (todo lo
existente son elipses o hulls, nada sigue calles reales).

## Alternativa liviana: geojson.io

Para ediciones puntuales sin instalar nada, [geojson.io](https://geojson.io) permite
arrastrar un GeoJSON de referencia, dibujar un polígono a mano sobre el mapa base (OSM) y
descargar el resultado. Sirve para iterar rápido un contorno, pero **no tiene snapping a
calles** (el trazo queda libre) y no soporta cargar varias capas de referencia con
simbología distinta a la vez tan cómodo como QGIS. Recomendado para ajustes chicos, no
para el trazado inicial de los 12 contornos.

## Kit de edición por macrozona (ya generado, ver `preparar_kit_edicion.py`)

En vez de que quien edite tenga que ir a buscar cada capa por el repo, el script
`scripts/polos_gastro/experimentos/infraestructura_cartografica_v1/preparar_kit_edicion.py`
arma una carpeta lista para arrastrar a QGIS o geojson.io:

```
.venv/Scripts/python.exe scripts/polos_gastro/experimentos/infraestructura_cartografica_v1/preparar_kit_edicion.py "Palermo"
.venv/Scripts/python.exe scripts/polos_gastro/experimentos/infraestructura_cartografica_v1/preparar_kit_edicion.py --todas
```

Salida en `outputs/polos_gastro/experimentos/infraestructura_cartografica_v1/kits_edicion/
<macrozona>/`: callejero recortado, entidades del universo V1, microclusters HDBSCAN,
polígonos del prototipo (para ver qué detecta hoy el algoritmo), la elipse editorial de
fase16 si existe, y los puntos semilla de Fase 13 (control de calidad mínimo: el contorno
nuevo debe contenerlos). Cada carpeta trae un `LEEME.md` con el orden sugerido de carga.
Corrido de prueba para Palermo: 1.043 entidades, 2.233 tramos de calle exportados.

## De QGIS/geojson.io al esquema formal

Ni QGIS ni geojson.io conocen los 16 atributos del esquema de Infra-2
(`id`, `nivel_confianza`, `metodo_construccion`, etc.) — solo exportan la geometría más los
campos que el editor haya cargado a mano en la tabla de atributos, lo cual es tedioso para
15 campos por polígono. La pieza que falta es un **normalizador**: un script que toma el
GeoJSON crudo recién exportado (geometría + a lo sumo `nombre`) y lo completa contra el
esquema formal, tomando el resto de los metadatos (fuente, calles límite, autor, fecha) de
una tabla simple que el editor completa en una hoja de cálculo o CSV — no en la interfaz
de QGIS. Este normalizador se construye y se prueba en la Etapa Infra-4, con el caso real
de Palermo Soho.

## Por qué no una aplicación propia todavía

Construir un editor web propio (Leaflet + `leaflet-draw` o `geoman`, ninguno instalado
hoy) es factible pero agrega una dependencia nueva, mantenimiento propio, y resuelve un
problema que QGIS ya resuelve mejor (snapping, simbología, capas múltiples, sin curva de
aprendizaje de código). Vale la pena reconsiderarlo únicamente si en el futuro se quiere
que la edición la haga alguien sin QGIS instalado y sin conocimientos de SIG — no es el
caso hoy. Si esa necesidad aparece, la base ya identificada en Infra-1
(`@usig-gcba/mapa-interactivo` + Leaflet, ya instalados) sería el punto de partida, sumando
`leaflet-draw` (requiere `npm install`, a autorizar explícitamente antes de sumarlo).
