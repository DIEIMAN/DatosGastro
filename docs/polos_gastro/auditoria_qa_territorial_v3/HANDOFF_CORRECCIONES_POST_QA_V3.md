# Handoff de correcciones post-QA V3

**Origen:** `auditor_qa`  
**Destino:** `cartografo_territorial` → `integrador_tecnico_editorial` → nuevo `auditor_qa`  
**Regla:** corregir en línea derivada; no editar en silencio ni recalcular las geometrías adoptadas.

## Trabajo requerido del cartógrafo

1. Derivar tres láminas institucionales y un mapa general desde las capas de presentación existentes.
2. Quitar códigos BEL-A, REC-A, CN-DEC10, puntos técnicos, categorías F01/F02 y señal externa de la cara pública.
3. Usar marca DGDGAS y lenguaje de delimitación adoptada/definición territorial del estudio.
4. Belgrano: resolver solapamientos; expresar Belgrano R como sector secundario; comunicar tres centralidades sin confundirlas con siete piezas.
5. Recoleta: conservar huecos; mejorar ubicación de etiqueta y legibilidad en media página; no comunicar nueve polos.
6. Costanera Norte: comunicar inequívocamente cuatro componentes; explicar en nota técnica que uno es multiparte y produce cinco piezas; mejorar jerarquía de rótulos y uso del espacio vacío.
7. Entregar por lámina: dimensiones, dpi, bbox, fuente de fondo y tabla categoría→estilo.
8. Distinguir superficie del modelo pre-simplificación y superficie del GeoJSON exportado; no reemplazar el KPI lock.

## Trabajo requerido del integrador

1. Corregir la contradicción del handoff: el contrato existe, está incorporado y su hash coincide.
2. Separar `PUNTOS_ASOCIADOS_SANITIZADOS_V3.geojson` como `INTERNO_TECNICO_NO_PUBLICABLE`; excluirlo del pack institucional.
3. Completar el manifest o documentar la exclusión de los dos checksums.
4. Mantener KPI lock, decisiones BEL-A/REC-A/CN-DEC10 y geometrías analíticas sin cambios.

## No requiere

- Nueva corrida analítica.
- Cambios en datos fuente, evidencia documental, pipeline híbrido o decisiones humanas cerradas.
- APIs, Places, instalaciones, commit o push.

## Gate de reingreso

Entregar una línea nueva con PNG/SVG institucionales, mapa general, metadata editorial, manifest/hashes actualizados y QA del productor. Luego solicitar QA independiente visual, contractual y de privacidad.
