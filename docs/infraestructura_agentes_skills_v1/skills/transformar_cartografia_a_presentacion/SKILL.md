---
name: transformar_cartografia_a_presentacion
description: Pasar capas analíticas (GeoJSON, métricas, clusters) a capas/mapas de presentación editorial sin alterar la geometría analítica fuente ni decisiones humanas firmadas.
version: 1
---

# transformar_cartografia_a_presentacion

**Política:** §§3, 9, 12.  
**Reglas:** R-CAP-01, R-MET-03, R-FIN-01.  
**Referencia:** capas editoriales Polos v4.x; design system `scripts/shared/style_tokens_dgdgas.py`.

## Propósito

Producir visualización y geometrías de **presentación** a partir de una capa **analítica**, manteniendo trazabilidad y sin promover automáticamente el resultado.

## Cuándo usarla

- Mapas para informe DGDGAS.  
- Simplificación, estilos, multiparte visual, etiquetas post hoc.  
- Comparativos experimentales vs lectura Fase 25 (en paralelo, no pisando F25).

## Cuándo no usarla

- Para redefinir límites institucionales.  
- Para renombrar polos en contra de decisiones firmadas.  
- Para llamar Places o bajar OSM sin autorización.

## Insumos requeridos

- Capa analítica versionada (ruta + hash preferible).  
- Guía de estilo / tokens si hay mapa institucional.  
- Decisiones humanas de nombres/jerarquía (si aplican).

## Rutas permitidas

- Lectura de GeoJSON/CSV analíticos del experimento.  
- Escritura en línea paralela:  
  `outputs/.../<paquete>/presentacion/` o `cartografia_editorial_*` **nuevo**.

## Rutas prohibidas

- Sobrescribir GeoJSON analítico fuente.  
- Fase 25/26 oficiales.  
- PDFs finales previos.

## Procedimiento

1. Declarar capa de entrada (analítica) y de salida (presentación).  
2. No modificar el archivo analítico; copiar/derivar.  
3. Aplicar solo transformaciones de presentación: estilo, simplificación cartográfica documentada, disoluciones visuales autorizadas, etiquetas.  
4. Registrar en metadata: qué cambió respecto de la analítica (no “silenciar” solapes reales).  
5. Si hay nombres: solo los de registro de decisiones; resto códigos neutros.  
6. Generar mapas; encadenar `qa_pdf_pagina_por_pagina` si salen en PDF.  
7. Etiquetar EXPERIMENTAL salvo instrucción humana de mostrable.

## Criterios de aceptación

- [ ] Analítica intacta (hash).  
- [ ] Presentación en ruta nueva.  
- [ ] Nota metodológica de simplificación.  
- [ ] Sin nombres no firmados presentados como oficiales.

## Outputs obligatorios

- Capas de presentación + README de diferencias.  
- Figuras/mapas.  
- Referencia a decisiones humanas usadas.

## Errores frecuentes

- Editar el GeoJSON de clustering “para que se vea bien” y perder métricas.  
- Fundir multiparte de Costanera sin documentarlo.  
- Usar KMeans u otros métodos ya descartados sin justificación (contexto Polos).

## Checklist de QA

- Hash analítica.  
- CRS/unidades.  
- Leyenda legible.  
- Disclaimer experimental.

## Formato del handoff

```markdown
## Handoff — cartografía presentación
- Analítica (ruta, hash):
- Presentación (ruta):
- Transformaciones:
- Nombres usados (DEC/DH):
- Mapas:
```

## Formato de respuesta final

Rutas + “analítica intacta: sí/no” + limitaciones visuales.

## Ejemplo breve

De `cartografia_design_v4_2` lectura → nueva carpeta de mapa global con jerarquía editorial, sin tocar F25.

## Reglas de seguridad

Política §2–3. Sin APIs.

## Autorización humana

- Cambiar geometría que implementa una decisión firmada.  
- Publicar mapa como “oficial GCBA”.
