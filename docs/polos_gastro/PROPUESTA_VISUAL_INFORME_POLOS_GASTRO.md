# Propuesta visual para el futuro informe PolosGastro

Fecha: 2026-06-29.

Propuesta de arquitectura visual para el informe futuro. **No habilita** todavía PDF final,
mapa final, geocodificación ni shapefiles. Es la base de decisión de estilo antes del borrador.

Insumos: `AUDITORIA_VISUAL_GRAFICOS_POLOS_GASTRO.md`, `cartografia/*`, universo de 32 polos.

> **Actualización 2026-06-29 (Fase 4A completada):** los rediseños propuestos en este documento
> ya se ejecutaron en `outputs/polos_gastro/graficos/fase4a/` (gráficos v2, mapas conceptuales v2
> sin solapes, y **mapa territorial real** con barrios oficiales de Buenos Aires Data). Ver
> `cartografia/fase4a/REPORTE_VISUALES_FASE4A.md` y `QA_VISUALES_REGENERADOS_FASE4A.md`. Lo que
> sigue es la propuesta original que guió ese rediseño.

---

## 1. Qué gráficos actuales conviene usar

- `universo_polos_por_grupo.png` — **usar** (claro, presentable).
- `precision_delimitacion_polos.png` — **usar** (justifica por qué no hay polígonos cerrados).
- `mapa_conceptual_polos_gastro.png` (resumido) — **usar**, tras reubicar la caja "No mapeados".

## 2. Qué gráficos conviene rediseñar

- `familias_territoriales_polos.png` — rediseño leve: pasar de barras apiladas a **barras
  agrupadas** o **heatmap familia × grupo** para comparar mejor.
- `mapa_conceptual_polos_gastro_completo.png` — rediseño mayor: resolver el solapamiento de
  etiquetas (DoHo/Villa Crespo/Villa Urquiza/Paternal/Colegiales) con más separación, jitter o
  paginado por familia. Hoy es solo insumo interno.
- Ambos mapas conceptuales: mover la caja "No mapeados" para que no tape "Avenida Corrientes"
  ni "Abasto".

## 3. Qué mapas faltan

- Un **mapa territorial real (estático)** del núcleo principal sobre límites de barrios
  oficiales (Buenos Aires Data), como complemento del diagrama conceptual. Sin geocodificar
  locales: solo barrios asociados coloreados por grupo, con advertencia.
- Opcional: un **visor interactivo** institucional (fase posterior, no informe).

## 4. Qué estilo cartográfico conviene

- **Capa base**: barrios/comunas GeoJSON de Buenos Aires Data. Fondo opcional con tiles GCBA
  (`mapa_base_v2`) si se quiere identidad institucional (atribución GOED/GCBA/OSM).
- **Render estático**: GeoPandas + matplotlib (ya en el `.venv`).
- **Paleta DataGastro** ya en uso: núcleo `#275DAD`, relevante `#2A9D8F`, emergente `#E9B44C`,
  anexo `#7D8597`, no incluir `#C44536`.

## 5. Cómo evitar mapas falsamente precisos

- **No** dibujar polígonos cerrados para polos de precisión baja (16) ni sin delimitación (2).
- Usar la **simbología por nivel de precisión**:
  - alta (3) → área o eje con borde, etiquetado como aproximación.
  - media (11) → etiqueta de zona / barrio asociado, sin borde duro.
  - baja (16) → punto o centroide de barrio, nunca área.
  - sin delimitación (2) → no mapear.
- Pintar el **barrio administrativo** como contexto, aclarando que **el barrio ≠ el polo**.
- Mantener visible la advertencia: "diagrama/aproximación, no delimitación oficial ni padrón".

## 6. Cómo mostrar niveles de evidencia

- Codificar el **grupo de informe** por color (paleta de arriba) y la **precisión** por forma
  o intensidad (relleno sólido = alta, semitransparente = media, contorno punteado = baja).
- Leyenda doble: una para grupo, otra para tipo de representación (como ya hace el script).

## 7. Cómo mostrar familias territoriales

- Agrupar visualmente por las **8 familias** (facetas o secciones del mapa/diagrama).
- En el informe, una familia por bloque narrativo, con su mini-tabla de polos.
- Heatmap familia × grupo como vista de resumen.

## 8. Cómo mostrar núcleo principal vs candidatos

- **Jerarquía visual clara**: núcleo principal con mayor peso (color saturado, etiqueta grande);
  zona relevante medio; emergente/candidato atenuado; anexo gris; "no incluir" fuera del mapa.
- En el PDF: secciones separadas (consolidados → relevantes → emergentes → anexo), no todo junto.

## 9. Qué fuentes visuales/cartográficas conviene usar

- Buenos Aires Data: Barrios GeoJSON, Comunas GeoJSON.
- Tiles base GCBA (GeoServer `mapa_base_v2`) — opcional, para fondo institucional.
- `@usig-gcba/mapa-interactivo` — solo para el visor interactivo futuro.
- Detalle en `cartografia/FUENTES_CARTOGRAFICAS_CABA.md` y
  `cartografia/LIBRERIAS_MAPAS_INFORMES_DATAGASTRO.md`.

## 10. Qué pedirle a Perplexity o buscar manualmente

- Fuentes específicas para los 4 casos de URL pendiente (Federico Lacroze, García del Río,
  Paternal) y para los polos débiles. Ver `PEDIDOS_EXTERNOS_PARA_MEJORAR_POLOS_GASTRO.md`.
- Confirmar el ID/recurso GeoJSON vigente de barrios y comunas antes de descargar.

## 11. Qué pedir en la próxima fase técnica

- Implementar el mapa estático GeoPandas + matplotlib del núcleo principal.
- Rediseñar familias y mapa conceptual completo.
- Decidir si se incorpora fondo de tiles GCBA.
- Definir plantilla DataGastro (tipografía, márgenes, pie de fuente/fecha) consistente con
  el informe de Mercados.

## 12. Qué debería tener el informe estilo Mercados

- Portada con fecha de corte y advertencia de alcance.
- Resumen ejecutivo sobrio (hallazgos separados de límites).
- Definición operativa de "polo".
- Mapa conceptual + (opcional) mapa territorial del núcleo.
- Secciones por jerarquía (consolidados, relevantes, emergentes) y por familia.
- Anexo de locales destacados (cualitativo, con advertencia de no-padrón).
- Limitaciones metodológicas y próximos pasos.
- Trazabilidad de fuentes.

> Recordatorio: ningún elemento visual debe convertir habilitaciones/oferta registrada/menciones
> turísticas en "locales activos", ni delimitaciones textuales en límites oficiales.
