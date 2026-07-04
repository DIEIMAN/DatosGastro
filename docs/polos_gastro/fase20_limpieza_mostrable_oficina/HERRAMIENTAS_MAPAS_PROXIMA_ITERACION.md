# Herramientas para mejorar los mapas — próxima iteración

**Proyecto:** PolosGastro — DGDGAS (Dirección General de Desarrollo Gastronómico)
**Fecha:** 3 de julio de 2026

Documento de análisis de opciones para una etapa posterior de trabajo cartográfico. **No es
un compromiso de implementación en fase20.** El PDF de oficina usa los mapas editoriales ya
existentes de fase19.

---

## 1. Criterio general antes de elegir herramienta

- **Para el PDF institucional, el entregable final de mapas debe ser estático: PNG o SVG.**
  Un mapa interactivo no se imprime ni se pega en un informe; lo que viaja al documento es una
  imagen exportada, sobria y controlada.
- **Cualquier herramienta interactiva (Leaflet, Felt, etc.) sirve para prototipar, visualizar
  y ajustar polígonos, no como entregable final.** Es un banco de trabajo, no la pieza.
- **Si se necesita precisión editorial, conviene dibujar los polígonos a mano una vez y luego
  hacer que Codex los use tal cual, sin recalcularlos.** Los polígonos de subzona son
  decisiones editoriales; no deben regenerarse automáticamente en cada corrida.
- **Las subzonas siguen siendo aproximaciones de lectura**, no límites oficiales, aunque el
  dibujo gane precisión. El lenguaje prudente se mantiene.

---

## 2. Opciones analizadas

### Leaflet / React Leaflet
- **Qué es:** librería JS de mapas interactivos sobre tiles.
- **Uso recomendado:** prototipar y visualizar polígonos, ajustar posiciones, revisar cómo se
  leen las subzonas sobre una base real.
- **Límite:** **no debería ser el entregable final** de una pieza institucional; produce mapa
  web, no imagen impresa. Exportar a PNG/SVG requiere pasos extra.
- **Veredicto:** útil como banco de prototipado; no como salida final.

### GeoJSON manual dibujado en geojson.io
- **Qué es:** editor web simple para dibujar geometrías y exportarlas como GeoJSON.
- **Uso recomendado:** dibujar a mano los polígonos de subzona y ejes, exportar el GeoJSON y
  versionarlo como insumo editorial fijo.
- **Ventaja:** rápido, sin instalación, produce un archivo que Codex puede consumir sin
  recalcular. Encaja con el criterio "dibujar una vez, reusar".
- **Veredicto:** **opción más práctica para la próxima fase** junto con Felt.

### Felt
- **Qué es:** herramienta colaborativa de mapas en la nube; dibujo cómodo y exportación.
- **Uso recomendado:** dibujar y exportar GeoJSON de forma más asistida que geojson.io, con
  edición colaborativa si participa más de una persona.
- **Veredicto:** **opción práctica para dibujar y exportar** en la próxima iteración; buena si
  se quiere edición compartida.

### QGIS
- **Qué es:** SIG de escritorio, completo y reproducible.
- **Uso recomendado:** cuando se necesite precisión seria, capas oficiales, control de
  proyección y exportación cartográfica de calidad (PNG/SVG con composición de impresión).
- **Límite:** curva de aprendizaje y más peso de proceso.
- **Veredicto:** **opción para algo más serio y reproducible**; el paso siguiente natural si el
  proyecto formaliza la cartografía.

### Mapbox o CARTO
- **Qué es:** plataformas de mapas en la nube con estilos y publicación.
- **Uso recomendado:** visualizaciones ricas o publicación web a escala.
- **Límite:** dependencia de servicio, posible costo y credenciales; excede lo necesario para
  una pieza institucional estática.
- **Veredicto:** no prioritario para este caso; solo si más adelante hay un producto web.

### Capas oficiales BA Data (GCBA)
- **Qué es:** datos abiertos del portal Buenos Aires Data.
- **Uso recomendado:** base de barrios, comunas y callejero como respaldo geográfico
  documentado (la base callejera CC-BY-2.5-AR ya se usó como referencia interna en fase19).
- **Veredicto:** insumo recomendado para dar respaldo a las geometrías, siempre como referencia,
  no como definición de límites de subzona editorial.

### GeoJSON de barrios / comunas / calles
- **Qué es:** geometrías oficiales reutilizables.
- **Uso recomendado:** dar contexto y encuadre a los polígonos editoriales dibujados a mano.
- **Veredicto:** útil como capa de contexto; las subzonas se dibujan encima, sin confundirse
  con los límites oficiales.

### Herramienta interna simple para dibujar/editar subzonas
- **Qué es:** un editor propio mínimo (por ejemplo, basado en Leaflet + draw) para dibujar y
  guardar polígonos de subzona como GeoJSON versionado.
- **Uso recomendado:** si el trabajo de subzonas se vuelve recurrente y se quiere control total
  del flujo sin depender de servicios externos.
- **Veredicto:** posible a futuro; solo si la frecuencia justifica construirlo. Para pocas
  iteraciones, geojson.io o Felt alcanzan.

---

## 3. Recomendación resumida

1. **Próxima fase, camino rápido:** dibujar los polígonos a mano en **geojson.io** o **Felt**,
   exportar GeoJSON y versionarlo como insumo editorial fijo.
2. **Prototipado/ajuste visual:** **Leaflet / React Leaflet** como banco de trabajo, nunca como
   entregable.
3. **Camino serio y reproducible:** **QGIS**, con capas oficiales de **BA Data (GCBA)** como
   contexto.
4. **Entregable final siempre estático:** exportar a **PNG/SVG** para el PDF institucional.
5. **Regla editorial permanente:** los polígonos de subzona se dibujan una vez, se versionan y
   Codex los usa sin recalcularlos; siguen siendo aproximaciones de lectura, no límites
   oficiales.
