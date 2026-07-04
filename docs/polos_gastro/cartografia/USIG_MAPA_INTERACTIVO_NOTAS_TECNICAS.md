# Notas técnicas — `@usig-gcba/mapa-interactivo`

Fecha de inspección: 2026-06-29.
Versión instalada: **1.2.8** (en `node_modules/@usig-gcba/mapa-interactivo/`).
Inspección hecha sobre el paquete ya instalado y su README, `package.json`, `src/`, `demo/`.
No se copió el paquete al repo, no se ejecutó, no se modificó nada.

---

## 1. Qué es la librería

Wrapper sobre **Leaflet** mantenido por USIG/GOED (GCBA) para crear mapas interactivos de la
Ciudad de Buenos Aires con la base cartográfica y las capas públicas oficiales del Gobierno de
la Ciudad. Expone una clase `MapaInteractivo` que monta un mapa Leaflet sobre un `div`, con
helpers para capas públicas, marcadores, recorridos, heatmaps y tiles vectoriales.

## 2. Cómo se instala

```
npm install @usig-gcba/mapa-interactivo
```

Ya está instalado en este proyecto (`package.json` raíz lo declara como dependencia
`^1.2.8`). El `package-lock.json` quedó generado en la raíz.

## 3. Dependencias que usa

Runtime (de su `package.json`): `leaflet ^1.4.0`, `leaflet.markercluster`, `leaflet.heat`,
`leaflet-heatmap`, `proj4`, `lodash`, `d3-queue`, `isomorphic-fetch`, `es6-promise`.

Build/dev (viejas): webpack 3, babel 6, mocha 3. El `.nvmrc` pide **Node v6.10** (muy
antiguo). El bundle ya viene compilado en `lib/MapaInteractivo.min.js`, así que para **usarlo**
no hace falta su toolchain de build; sí importa que asume un entorno con DOM.

## 4. Cómo se instancia un mapa

```javascript
import MapaInteractivo from '@usig-gcba/mapa-interactivo'

const mapa = new MapaInteractivo("mapa-id", { center: [-34.62, -58.44], zoom: 13 });
```

Requisito: el `div#mapa-id` debe **existir en el DOM y tener dimensiones** antes de instanciar.
Opciones útiles: `center`, `zoom`, `zoomControl`, `attributionControl`, callbacks
(`onClick`, `onFeatureClick`, `onMoveEnd`, etc.), iconos de marcadores.

## 5. Capas y tiles que usa

- **Base cartográfica oficial** (default): GeoServer GCBA
  `geoserver.buenosaires.gob.ar/geoserver/gwc/service/tms/.../mapa_base_v2/...png`
  con atribución **GOED (GCBA) © OpenStreetMap (ODbL)**.
- **Tiles temáticos USIG**: `tiles1.usig.buenosaires.gob.ar/mapcache/tms/...`.
- **API de capas públicas**: `epok.buenosaires.gob.ar/mapainteractivoba/layers` (catálogo de
  capas que se agregan por nombre con `addPublicLayer`).
- `setBaseLayer()` permite cambiar la base por cualquier `L.tileLayer` propio.

## 6. Puntos, recorridos y capas

- `addMarker(latlng, visible, draggable, goTo, activate, clickable, options)` → marcadores.
- `addLocationMarker(position, recenter, zoomIn)` → marcador de ubicación.
- `addPublicLayer(nombre, opciones)` → capa oficial por nombre (con clustering opcional).
- `addVectorTileLayer(id, {url, style, displayPopup})` → tiles vectoriales (.pbf) con estilo y
  popups por placeholders `{atributo}`.
- `mostrarRecorrido(recorrido)` / `ocultarRecorrido(recorrido)` → recorridos (formato
  `@usig-gcba/recorridos`).
- `setHeatMapData([[lat, lng, peso], ...], {radius})` → heatmap.
- `getMapa()` → devuelve la instancia `L.Map` de Leaflet (acceso completo a la API de Leaflet).

## 7. ¿Permite exportar imagen?

**Sí, pero solo en browser.** `getStaticImage()` devuelve `Promise<canvas>`. Internamente usa
`utils/leaflet-image` (basado en `leaflet-image`), que rasteriza el mapa a un `<canvas>`. En el
demo se hace `canvas.toDataURL()` para obtener un PNG. **Requiere DOM, `<canvas>` y que los
tiles sean accesibles** (y sin problemas de CORS para que el canvas no quede "tainted").

## 8. ¿Sirve para generar PNGs para informes?

Sí, pero **no desde Node puro**. Para producir PNG automáticamente haría falta un entorno
**headless con DOM** (Playwright/Puppeteer cargando una página que monte el mapa y luego
`getStaticImage()` + `toDataURL()`, o screenshot del navegador). Eso agrega dependencias
pesadas (Chromium headless) y conexión a los tiles del GCBA.

## 9. Limitaciones

- **Necesita browser/DOM**: no se instancia en Node sin emular DOM.
- **Toolchain antiguo** (Node 6, webpack 3, babel 6) — solo afecta si se quisiera recompilar.
- **Dependencia de red**: la base y las capas vienen de servidores del GCBA; sin internet no
  hay tiles.
- **CORS / canvas tainted**: `toDataURL()` puede fallar si algún tile no permite CORS.
- **Pensado para interactividad**, no para batch de mapas estáticos en pipeline.
- **No produce GeoJSON/shapefiles** — es visualización, no procesamiento geográfico.

## 10. Riesgos

- Acoplar el pipeline de informes a un entorno headless es frágil y difícil de reproducir en
  Windows/CI.
- Capturar mapas con tiles del GCBA y publicarlos exige respetar la **atribución oficial**
  (GOED/GCBA © OpenStreetMap ODbL).
- Versión 1.2.8 con dependencias viejas: posible deuda técnica si se integra hondo.
- No mezclar la interactividad con los guardrails: nada de geocodificar locales ni publicar
  delimitaciones como oficiales.

## 11. Ejemplo mínimo de uso (solo browser, aislado)

```html
<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><title>Mapa CABA mínimo</title>
  <style>#mapa{height:520px;width:900px}</style>
</head>
<body>
  <div id="mapa"></div>
  <button id="png">Exportar PNG</button>
  <script src="../../../node_modules/@usig-gcba/mapa-interactivo/lib/MapaInteractivo.js"></script>
  <script>
    const mapa = new MapaInteractivo("mapa", {
      center: [-34.5895, -58.4255], // Palermo aprox.
      zoom: 13, zoomControl: true, attributionControl: true
    });
    // Punto conceptual de ejemplo (no es geocodificación de locales):
    mapa.addMarker({lat:-34.5895, lng:-58.4255}, true, false, false, false, false, {});
    document.getElementById("png").onclick = () =>
      mapa.getStaticImage().then(c => { const a=document.createElement('a');
        a.href=c.toDataURL(); a.download='mapa_caba.png'; a.click(); });
  </script>
</body>
</html>
```

> Este ejemplo **no debe** usarse para geocodificar locales ni para producir un mapa final.
> Es solo prueba técnica de que la librería renderiza CABA y puede exportar imagen en browser.

## 12. Recomendación para DataGastro

- **Para mapas estáticos de informes (PDF): NO usar esta librería como camino principal.**
  Renderizar PNG con USIG implica un browser headless: demasiada fricción para un pipeline
  reproducible en Windows. Para estáticos conviene **GeoPandas + matplotlib + contextily**
  (ver `cartografia/LIBRERIAS_MAPAS_INFORMES_DATAGASTRO.md`), usando GeoJSON de barrios/comunas
  de Buenos Aires Data y, si se desea, tiles base del GCBA vía contextily.
- **Para exploración interactiva (HTML) y futuro dashboard institucional: SÍ es candidata.**
  Da la base cartográfica oficial del GCBA, capas públicas y estética institucional "de fábrica".
  Es el camino correcto si en el futuro se quiere un visor web con identidad GCBA.
- **Lo que sí aporta ya**: confirma las **fuentes de tiles/base oficiales** (GeoServer GCBA,
  USIG mapcache, epok capas) que podemos reutilizar desde otras herramientas, y la atribución
  correcta a citar.

> Próximo paso técnico (solo si se autoriza): un prototipo HTML aislado en
> `scripts/polos_gastro/cartografia_experimentos/` para validar render + export, sin tocar el
> pipeline ni geocodificar locales.
