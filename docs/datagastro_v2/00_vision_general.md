# DataGastro V2 — Visión general

> Documento de diseño. **No** ejecuta integraciones, **no** llama a ninguna API, **no** usa
> API keys, **no** toca el padrón ni el pipeline actuales (F01–F05 intactos). Es una propuesta
> técnica y metodológica para discusión y aprobación de Diego antes de implementar nada.

## 1. Qué es DataGastro V2

DataGastro V2 es la evolución de DataGastro hacia un **sistema de inteligencia gastronómica
territorial para CABA**. La V1 produjo un pipeline reproducible sobre fuentes públicas
(F01–F05) más pilotos externos acotados (Google Places para casas de pastas). La V2 amplía el
**alcance conceptual**: deja de pensar el problema como "un listado de restaurantes" y lo
piensa como el **ecosistema gastronómico completo** de la Ciudad: consumo, producción, venta
especializada, tradición barrial, cadenas, ferias, mercados y rubros emblemáticos.

V2 **no** es un censo ni un padrón oficial. Es un **padrón candidato** y un **universo
operativo probable**, construido por capas, con trazabilidad por fila y nivel de confianza
explícito.

## 2. Qué cambia respecto de V1

| Dimensión | V1 | V2 |
|---|---|---|
| Alcance | Oferta gastronómica + habilitaciones + ferias + eventos + programas | Ecosistema completo: consumo, producción, venta especializada, ferias/mercados, histórico/emblemático |
| Unidad de análisis | Establecimiento / habilitación / espacio / evento | **Establecimiento candidato** unificado, con detecciones por fuente |
| Taxonomía | Categoría gastronómica simple | Taxonomía de 2 niveles (categoría principal + subcategoría) con incluye/excluye/riesgo |
| Fuentes | F01–F05 + pilotos | Mismas oficiales + Google Places + OSM + documentales + Perplexity (localizador) + revisión manual |
| Confianza | `calidad_dato`, `requiere_validacion` | Niveles de confianza formalizados (multifuente sube confianza) |
| Salida | Informes + dashboard V1 | Mapas por rubro, rankings por comuna/barrio, densidad, cadenas vs independientes, fichas por rubro, casos históricos |

V2 **reutiliza** el modelo conceptual de V1 (separación F01/F02/F03, "habilitación ≠ local
activo", agregados sin filas sensibles) y lo generaliza.

## 3. Principios rectores

1. **Padrón candidato, no censo.** Toda salida se nombra como universo operativo probable
   sujeto a validación territorial posterior.
2. **Separación de universos.** Públicas (F01–F05), internas (I01–I99), externas/privadas
   (E01–E99). Nunca se mezclan como un mismo universo sin declarar la fuente.
3. **Multifuente sube confianza.** Aparecer en más de una fuente independiente eleva el nivel
   de confianza; aparecer en una sola **no** descarta (las casas independientes barriales son
   centrales, no ruido).
4. **No inventar.** Nada de datos, URLs, IDs ni métricas inventadas. `--strict-real` se
   mantiene como norma. Los seeds no son datos.
5. **Habilitación ≠ local activo.** El registro administrativo mide permisos/registros, no
   actividad confirmada.
6. **Privacidad por diseño.** Los brutos sensibles (con place_id, dirección, razón social,
   contactos) viven en carpetas **gitignored**; sólo se publican **agregados** y entregables
   sanitizados.
7. **Documental ≠ fuente final.** Perplexity y la web sirven para **localizar** fuentes
   documentales (notas, sitios oficiales), no como fuente de verdad.

## 4. Vocabulario institucional (obligatorio)

**Usar:** padrón candidato · universo operativo probable · registro administrativo oficial ·
señal operativa no oficial · fuente abierta auxiliar · validación territorial posterior ·
detección por fuente · nivel de confianza.

**No usar:** censo definitivo · padrón oficial · locales activos confirmados · todos los
establecimientos · listado completo.

## 5. Arquitectura por capas (resumen)

```text
Capa 0  Fuentes              oficiales (F0x) | externas (E0x: Google, OSM) | documentales | manual
Capa 1  Detección            fact_deteccion_fuente  (1 fila = 1 aparición en 1 fuente)
Capa 2  Resolución de entidad deduplicación → dim_establecimiento_candidato (1 fila = 1 entidad)
Capa 3  Clasificación        rubro (taxonomía v2) + cadena/independiente + confianza integrada
Capa 4  Territorio           punto-en-polígono contra geometrías GCBA (comuna/barrio)
Capa 5  Validación           fact_validacion_manual + validación territorial posterior
Capa 6  Salidas              agregados, mapas, rankings, fichas, informes ejecutivos
```

## 6. Lo que V2 promete y lo que NO promete

**Promete:** un universo amplio y defendible, trazable por fila, con confianza explícita,
separando rubros y fuentes, útil para priorizar relevamiento territorial.

**No promete:** completitud, exactitud de "locales activos", ni reemplazar el registro
administrativo oficial. Toda cifra es de **orden de magnitud** hasta validación territorial.

## 7. Índice de la propuesta

- `01_taxonomia_gastronomica_v2.md` — taxonomía de rubros (2 niveles, incluye/excluye/riesgo).
- `02_fuentes_y_roles.md` — catálogo de fuentes y rol metodológico de cada una.
- `03_niveles_de_confianza.md` — escala de confianza y reglas de promoción.
- `04_plan_integracion_google_places.md` — plan (no ejecución) de Places API.
- `05_plan_integracion_osm.md` — plan de OpenStreetMap.
- `06_plan_fuentes_oficiales.md` — AGC, BA Data, Ente de Turismo, ferias/eventos.
- `07_plan_fuentes_documentales_y_perplexity.md` — uso de web/Perplexity como localizador.
- `08_modelo_datos_propuesto.md` — tablas, campos y propósito.
- `09_salidas_ejecutivas_y_dashboards.md` — mapas, rankings, fichas, informes.
- `10_plan_de_implementacion_por_etapas.md` — hoja de ruta por fases.
