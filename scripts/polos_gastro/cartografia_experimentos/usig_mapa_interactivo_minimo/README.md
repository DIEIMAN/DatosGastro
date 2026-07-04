# Prototipo mínimo — USIG Mapa Interactivo

Fecha: 2026-06-29.

Experimento **aislado** para evaluar si `@usig-gcba/mapa-interactivo` puede renderizar un mapa
simple de CABA y exportar imagen. No forma parte del pipeline. No toca scripts existentes. No
depende de datos privados. No geocodifica locales. No produce outputs públicos finales.

## Qué es

Un único `index.html` que:
1. instancia un mapa de CABA con la base cartográfica oficial del GCBA;
2. permite agregar un punto conceptual de ejemplo (no es ubicación de un local);
3. intenta exportar la imagen del mapa con `getStaticImage()` → `canvas.toDataURL()`.

Carga el bundle ya compilado desde
`node_modules/@usig-gcba/mapa-interactivo/lib/MapaInteractivo.js` (el paquete **no** se copió al
repo; solo se referencia por ruta relativa).

## Cómo correrlo

Necesita un navegador y un servidor estático local (por `file://` algunos tiles/CORS fallan).
Desde la raíz del repo, por ejemplo:

```
# Opción 1: Python
python -m http.server 8000
# luego abrir:
# http://localhost:8000/scripts/polos_gastro/cartografia_experimentos/usig_mapa_interactivo_minimo/index.html

# Opción 2: cualquier servidor estático (live-server, etc.)
```

Requiere **conexión a internet** (los tiles vienen de servidores del GCBA).

## Qué prueba

- Que la librería instala y monta un mapa Leaflet de CABA con base oficial GCBA.
- Que se puede agregar un marcador.
- Que `getStaticImage()` existe y, en browser, devuelve un canvas exportable a PNG.

## Qué NO prueba

- **No** prueba generación de PNG desde Node/CLI (la librería necesita DOM/browser).
- **No** prueba un mapa final ni delimitaciones de polos.
- **No** prueba geocodificación de locales (excluida por diseño).
- **No** valida que `toDataURL()` funcione siempre: si algún tile no envía cabeceras CORS, el
  canvas queda "tainted" y la exportación falla.

## Estado / diagnóstico

- El paquete (`1.2.8`) es un wrapper de Leaflet con base e identidad GCBA. Funciona **en
  browser**. Ver `docs/polos_gastro/cartografia/USIG_MAPA_INTERACTIVO_NOTAS_TECNICAS.md`.
- **No se ejecutó render automático** en esta fase: requeriría un navegador o un headless
  (Playwright/Puppeteer), lo que agrega fricción y va más allá del objetivo ("no forzar si
  complica"). Se deja el HTML listo para abrir manualmente cuando se quiera validar.

## ¿Sirve para el futuro?

- **Para mapas estáticos de PDF**: no es el camino recomendado (necesita headless). Para
  estáticos conviene **GeoPandas + matplotlib** — ver
  `docs/polos_gastro/cartografia/LIBRERIAS_MAPAS_INFORMES_DATAGASTRO.md`.
- **Para un visor interactivo institucional**: sí, es una buena base (identidad GCBA y capas
  oficiales de fábrica). Candidato para un futuro dashboard.
