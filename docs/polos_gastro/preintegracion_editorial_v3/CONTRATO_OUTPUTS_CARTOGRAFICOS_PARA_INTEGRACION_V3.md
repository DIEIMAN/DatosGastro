# Contrato de outputs cartográficos para la integración editorial V3

Estado: **CONTRATO DE ENTRADA / VIGENTE HASTA RECEPCIÓN DEL HANDOFF**. Fecha: 2026-07-11.
Emisor: `integrador_tecnico_editorial` (V1.1.1). Destinatario: corrida territorial V3
(Codex / `cartografo_territorial`).

Alcance: **Belgrano, Recoleta, Costanera Norte** + mapa general. Codex **no** diseña el informe
político ni compone páginas: entrega capas, imágenes según plantilla, métricas y QA. Todo lo no
listado aquí no es exigible.

## 1. Entregables por polo (Belgrano, Recoleta, Costanera Norte)

| # | Entregable | Requisito |
|---|---|---|
| 1 | **GeoJSON analítico** | Geometrías completas de la corrida (núcleos/componentes/ejes) con propiedades técnicas (ids, métricas por unidad). Uso interno; nunca se incrusta en el PDF político. Sin puntos individuales de establecimientos, sin nombres comerciales. |
| 2 | **GeoJSON de presentación** | Geometrías simplificadas para lectura editorial (equivalente a la separación analítica/presentación de v2.1, p.ej. PM_PRES_C). Sin segmentos analíticos crudos. |
| 3 | **PNG (y SVG si el flujo lo permite)** | Render por polo según `ESPECIFICACION_PLANTILLAS_MAPAS_POLITICOS.md` (línea Fase 25 política). PNG a resolución de imprenta (≥200 dpi al tamaño de lienzo de la plantilla); proporción del lienzo de la página destino, sin deformación. |
| 4 | **Fondo** | Base callejera sobria coherente con las láminas vigentes (calles de referencia, sin POIs comerciales, sin teselas con marca de terceros incompatible con uso institucional). Declarar la fuente del fondo. |
| 5 | **Etiquetas** | Solo rótulos editoriales pactados; sin códigos técnicos visibles (`BEL_RV2_*`, `CN_C0*` no aparecen en la imagen), sin vocabulario vetado (`APROX.`, `SUBZONA APROX.`, etc.), sin nombres comerciales. |
| 6 | **Leyenda** | Por lámina, con las categorías nuevas necesarias (polo, centralidad interna, eje interno, componente discontinuo, área en observación). Si la leyenda la compone el generador propio, entregar en su lugar la tabla categoría→estilo. |
| 7 | **CRS** | Declarado por archivo (EPSG). GeoJSON en EPSG:4326; si la corrida trabaja en un CRS proyectado (p.ej. EPSG:9498/POSGAR), entregar ambos o declarar la transformación. |
| 8 | **Bounding box** | BBox de cada lámina (coordenadas del encuadre usado en el render) para reproducir el encuadre en regeneraciones. |
| 9 | **Métricas** | Por polo y por componente/subzona: cantidad de registros, composición por universo de fuente (F01/F02 vs. externa), cobertura, robustez — con nombres de campo estables para volcar en el KPI lock V3. Sin métricas inventadas ni interpoladas. |
| 10 | **Cobertura** | Cobertura geométrica y dependencia de fuente externa por polo (imprescindible para Costanera: valor único citable en metodología, DEC-10). |
| 11 | **Hashes** | SHA-256 de cada archivo entregado, en un manifest (`MANIFEST` con ruta, bytes, hash, fecha). |
| 12 | **Nombres de componentes** | Ids técnicos estables + tabla id→denominación post hoc propuesta, marcada como NO institucional. Los nombres públicos los firma Diego (DH-05 para Belgrano). |
| 13 | **Decisiones humanas** | Declaración explícita de cumplimiento: ver §2. Cualquier desvío se reporta como hallazgo, no se resuelve en la capa. |
| 14 | **QA cartográfico** | Documento de QA por lámina: encuadre, legibilidad, solapamientos, verificación de que la geometría de presentación deriva de la analítica, y verificación de privacidad (sin datos individuales). |
| 15 | **Handoff** | Un `HANDOFF_*.md` que inventaríe todo lo anterior, con fecha de corrida, versión de insumos, parámetros relevantes y limitaciones conocidas. |

## 2. Restricciones por decisiones humanas vigentes (gates de aceptación)

- **Belgrano** (decisión 1.1 V1.1 + DEC-04): un único polo. La corrida contrasta la estructura
  decidida (centralidad principal Barrio Chino–Belgrano C–Barrancas–Pasaje Echeverría; eje
  interno Cabildo–Juramento; Bajo Belgrano diferenciado; Belgrano R secundario). No entregar
  jerarquías con nombres como validadas: DH-05 sigue diferida. Belgrano R solo se propone como
  subpolo si la evidencia espacial lo justifica, y aun así la promoción la firma Diego.
- **Recoleta** (decisión 1.2 V1.1): un único polo; comparar las dos arquitecturas (unidad
  general vs. unidad + máximo dos subzonas). **Nunca** entregar 9 núcleos como 9 polos.
  Callao–9 de Julio y Bellas Artes como referencias/transiciones, no subpolos. Sin cifras de
  oferta publicables (REC-R02 descartada).
- **Costanera Norte** (DEC-05 + DEC-10): un único polo, **cuatro componentes discontinuos con
  `CN_C02` incluido**; vacíos preservados, sin conectores artificiales ni envolvente común;
  apto para cartografía principal (no rotular como exploratorio/anexo); dependencia de Places
  como métrica única para metodología; sin afirmaciones de informalidad o irregularidad.
  Cualquier propuesta de eliminar/fusionar/alterar componentes vuelve a Diego (§4 de
  `DECISIONES_Y_USOS_DOCUMENTALES.md`).
- **Mapa general**: los tres polos integrados a la lectura de conjunto con la misma gramática
  visual que el resto (sin degradarlos a "observación").

## 3. Criterio de aceptación del integrador

El handoff se acepta si: manifest completo y hashes verificables; CRS y bbox declarados;
métricas con campos estables; QA cartográfico presente; gates de §2 declarados como cumplidos
o con desvíos reportados. Si falta cualquiera de estos elementos, la integración editorial no
comienza y se devuelve el paquete con observaciones.
