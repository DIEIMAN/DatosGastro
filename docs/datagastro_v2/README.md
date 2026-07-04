# DataGastro V2 — README (Etapa 0 + Etapa 1)

Índice operativo de DataGastro V2. La **fuente de verdad metodológica** son los documentos de
esta carpeta (`docs/datagastro_v2/`); este README es el mapa de entrada.

## Qué es DataGastro V2

Un **sistema de inteligencia gastronómica territorial para CABA** que releva el ecosistema
gastronómico completo (consumo, producción, venta especializada, ferias/mercados, cadenas,
independientes barriales e históricos/emblemáticos). Produce un **padrón candidato / universo
operativo probable**, con trazabilidad por fila y nivel de confianza explícito. **No** es un
censo ni un padrón oficial.

## Estado

- **Etapa 0 — Diseño:** aprobada. Documentos `00`–`10`.
- **Etapa 1 — Esqueleto técnico:** implementada. Estructura, configs, esquemas, validador y
  código mínimo. **Sin integraciones, sin requests, sin API keys, sin datos reales.**
- **Etapa 2 — Anclas oficiales y mapa de cobertura:** implementada. Matriz de fuentes
  oficiales/institucionales y cobertura por rubro hacia el **universo gastronómico completo**,
  construida solo con archivos locales y documentación existente. **Sin requests, sin descargas,
  sin integración de datos, sin padrón.**
- **Etapa 2.5 — Inventario de fuentes internas DGDGAS:** implementada. Inventario seguro y
  sanitizado de la carpeta interna copiada de Drive, fuentes internas candidatas (I10–I13) y su
  cruce con la taxonomía. **Sin requests, sin leer valores de celdas, sin exponer PII, sin tocar
  los archivos originales, sin padrón.**
- **Etapa 3 — Integración segura y minimizada de I10:** implementada. Staging interno
  minimizado (gitignored) + agregados sanitizados por hoja/rubro/barrio, excluyendo PII. **Sin
  requests, sin padrón final, sin deduplicar contra Google/OSM, sin exponer nombres/direcciones,
  sin tocar el Excel original.**
- **Etapa 3.5 — Normalización interna de I10:** implementada. Barrios mapeados al catálogo
  oficial CABA (48 barrios) y clasificación tentativa de rubro para hojas mixtas. **Sin requests,
  sin geocodificar, sin deduplicar contra externas, sin padrón final, sin exponer PII.**

## Documentos de diseño (Etapa 0)

| Archivo | Contenido |
|---|---|
| `00_vision_general.md` | Visión, principios, vocabulario, arquitectura por capas |
| `01_taxonomia_gastronomica_v2.md` | Taxonomía de rubros (2 niveles + incluye/excluye/riesgo) |
| `02_fuentes_y_roles.md` | Catálogo de fuentes y rol metodológico |
| `03_niveles_de_confianza.md` | Escala de confianza y reglas de promoción/degradación |
| `04_plan_integracion_google_places.md` | Plan (no ejecución) de Places API |
| `05_plan_integracion_osm.md` | Plan de OpenStreetMap |
| `06_plan_fuentes_oficiales.md` | AGC, BA Data, Ente de Turismo, ferias/eventos |
| `07_plan_fuentes_documentales_y_perplexity.md` | Web/Perplexity como localizador |
| `08_modelo_datos_propuesto.md` | Tablas, campos y propósito |
| `09_salidas_ejecutivas_y_dashboards.md` | Mapas, rankings, fichas, informes |
| `10_plan_de_implementacion_por_etapas.md` | Hoja de ruta por fases |
| `11_matriz_fuentes_oficiales_v2.md` | (Etapa 2) Anclas oficiales, qué cubren y brechas |
| `12_plan_barrido_total_gastronomico_v2.md` | (Etapa 2) Camino al universo total por etapas A–I |
| `13_mapa_cobertura_por_rubro_v2.md` | (Etapa 2) Cobertura oficial vs dependencia externa por rubro |
| `14_inventario_dgdgas_drive.md` | (Etapa 2.5) Inventario sanitizado de la carpeta interna DGDGAS |
| `15_fuentes_internas_dgdgas_v2.md` | (Etapa 2.5) Fuentes internas candidatas I10–I13 y cruce con taxonomía |
| `16_integracion_segura_i10_dgdgas.md` | (Etapa 3) Integración minimizada de I10: qué se leyó, qué se excluyó, agregados y límites |
| `17_normalizacion_i10_barrios_y_rubros.md` | (Etapa 3.5) Normalización de barrios al catálogo oficial CABA y desagregación tentativa de rubros |

## Estructura técnica (Etapa 1)

```text
src/v2/                         módulos V2 (separados de V1)
  __init__.py
  load_config.py                lee y valida los CSV de config/v2/
  validate_v2_setup.py          valida el setup completo (sin requests)
  contracts/__init__.py         (vacío) validación contra esquemas, etapas futuras
  utils/__init__.py             (vacío) utilidades compartidas, etapas futuras

config/v2/                      configuración versionable (no sensible)
  taxonomia_gastronomica_v2.csv
  fuentes_v2.csv
  google_places_query_templates.csv   (solo templates, no ejecución)
  osm_tags_v2.csv
  niveles_confianza_v2.csv
  reglas_exclusion_v2.csv
  rubros_piloto_v2.csv
  fuentes_oficiales_candidatas_v2.csv  (Etapa 2)
  cobertura_fuente_rubro_v2.csv        (Etapa 2)
  rubros_universo_gastronomico_v2.csv  (Etapa 2)

schemas/v2/                     contratos de tablas (YAML), versionables
  dim_establecimiento_candidato.schema.yml
  dim_fuente.schema.yml
  dim_rubro_gastronomico.schema.yml
  dim_marca_cadena.schema.yml
  dim_territorio.schema.yml
  fact_deteccion_fuente.schema.yml
  fact_validacion_manual.schema.yml
  fact_trayectoria_documental.schema.yml
  fact_evento_gastronomico.schema.yml

data/v2/
  raw/         (gitignored)  datos crudos sensibles — vacío
  processed/   (gitignored)  filas individuales sensibles — vacío
  analytics/   (versionable) agregados sanitizados — vacío (.gitkeep)

outputs/v2/
  sanitized/   (versionable) entregables agregados — vacío (.gitkeep)
  internal/    (gitignored)  material interno sensible — vacío
```

## Cómo correr el validador

```bash
python src/v2/validate_v2_setup.py
```

Verifica: carpetas, configs y columnas mínimas, esquemas, ausencia de `.env`, ausencia de API
keys hardcodeadas, que las carpetas sensibles estén gitignored y que no haya datos crudos
versionables. **No hace requests.** Devuelve código 0 (ok) o 1 (hay errores).

Para inspeccionar sólo los configs:

```bash
python src/v2/load_config.py
```

## Qué todavía NO está implementado

- Ninguna integración de datos (Google Places, OSM/Overpass, fuentes oficiales, documental).
- Ningún request externo, ninguna API key, ningún uso de Perplexity.
- Ninguna tabla poblada con datos reales (`data/v2/` y `outputs/v2/` están vacíos).
- Ningún dashboard ni salida ejecutiva V2.
- Ninguna modificación del pipeline V1 ni de casas de pastas.

## Próximos pasos (según `10_plan_de_implementacion_por_etapas.md`)

1. **Etapa 2 — Anclas oficiales (sin costo):** poblar candidatos leyendo salidas públicas
   existentes (AGC/F02, BA Data, F03/F04) sin regenerarlas.
2. **Etapa 3 — OSM (sin costo monetario):** integrar OSM con aprobación para consultas Overpass.
3. **Etapa 4 — Google Places (PILOTO, BLOQUEADA):** requiere aprobación + presupuesto + topes.
4. Etapas 5–8: documental/emblemáticos, revisión manual, salidas y validación territorial.

Cada etapa termina con un **gate de aprobación de Diego**.

## Etapa 2 — Anclas oficiales y mapa de cobertura

**Qué se creó:**
- Docs `11_matriz_fuentes_oficiales_v2.md`, `12_plan_barrido_total_gastronomico_v2.md`,
  `13_mapa_cobertura_por_rubro_v2.md`.
- Configs `config/v2/fuentes_oficiales_candidatas_v2.csv`, `cobertura_fuente_rubro_v2.csv`,
  `rubros_universo_gastronomico_v2.csv`.
- Script offline de apoyo `src/v2/build_official_anchors_matrix.py`.
- Validador y `EXPECTED_COLUMNS` ampliados a los nuevos artefactos.

**Qué NO se ejecutó:** ningún request, ninguna descarga, ninguna API key, ningún uso de
Google/OSM/Perplexity, ninguna integración de datos, ningún padrón. Los inventarios locales se
miraron **solo como metadata de presencia** (no se leyeron filas sensibles) y no se modificaron.

**Cómo se usa:**
```bash
python src/v2/build_official_anchors_matrix.py   # reporte offline de anclas y cobertura
python src/v2/validate_v2_setup.py               # valida setup (incluye artefactos Etapa 2)
```

**Próximos pasos:** según `12_...md`, iniciar la **Etapa A (anclas oficiales)** leyendo salidas
públicas existentes (F01–F05) sin regenerarlas, previo gate de aprobación.

## Etapa 2.5 — Inventario de fuentes internas DGDGAS

**Qué se creó:**
- Docs `14_inventario_dgdgas_drive.md`, `15_fuentes_internas_dgdgas_v2.md`.
- Config `config/v2/fuentes_internas_v2.csv` (fuentes internas I10–I13).
- Salidas sanitizadas en `outputs/v2/sanitized/`: `inventario_dgdgas_archivos_sanitizado.csv`,
  `fuentes_internas_dgdgas_candidatas.csv`, `cobertura_dgdgas_por_rubro_v2.csv`.
- Script offline `src/v2/build_dgdgas_inventory.py`.
- Pack sanitizado `outputs/v2/sanitized/PACK_DATAGASTRO_V2_ETAPA_2_5_DGDGAS.zip`.

**Qué NO se ejecutó / expuso:** ningún request, ninguna descarga, ningún valor de celda leído,
ningún dato personal (PII), ningún link privado de Drive, ningún padrón. Los archivos originales
**no se modificaron, movieron ni borraron**. La carpeta DGDGAS original es interna/gitignored y
**no** es requerida por el validador (puede no existir en otra máquina).

**Cómo se usa:**
```bash
python src/v2/build_dgdgas_inventory.py    # regenera el inventario sanitizado (offline)
python src/v2/validate_v2_setup.py         # valida setup + escaneo de privacidad de entregables
```

**Hallazgo clave:** la base "DGDGAS EVENTOS" es en realidad un **directorio de locales por
rubro** (con PII de contacto). Útil como ancla interna para `bares`, `bodegones`, `restaurantes`,
`heladerias`, `parrillas` (y media para `cafeterias`/`pizzerias`), **solo agregada y sin PII**.

## Etapa 3 — Integración segura y minimizada de I10 (DGDGAS)

**Qué se creó:**
- Doc `16_integracion_segura_i10_dgdgas.md`.
- Script offline `src/v2/build_i10_dgdgas_staging.py` (lee el `.xlsx` por `zipfile`, excluye PII).
- **Staging interno (gitignored)** en `outputs/v2/internal/`: `i10_dgdgas_perfil_columnas.csv`,
  `i10_dgdgas_establecimientos_minimizados.csv` (con `nombre_local`/`direccion`, **sensible**).
- **Agregados sanitizados** en `outputs/v2/sanitized/`: `i10_dgdgas_agregado_por_hoja.csv`,
  `i10_dgdgas_agregado_por_rubro_v2.csv`, `i10_dgdgas_agregado_por_barrio.csv`,
  `i10_dgdgas_resumen_integracion.csv`.
- Pack `outputs/v2/sanitized/PACK_DATAGASTRO_V2_ETAPA_3_I10_DGDGAS.zip`.

**Resultado:** 2.480 establecimientos minimizados (solo interno); 8.350 valores PII excluidos.
Cubre fuerte `restaurantes`, `bares`, `bodegones`, `parrillas`, `heladerias`. Pendientes de
desagregación: `Café y dulce` y `Pizza/empanadas/pasta`; pendientes taxonómicos: `Hamburguesería`,
`Foodtrucks`, `Emprendimientos`.

**Qué NO se hizo:** ningún request, ningún padrón final, ninguna deduplicación contra Google/OSM,
ninguna geocodificación, ningún nombre/dirección en sanitizados, ninguna modificación del Excel
original. I10 es **fuente interna de validación / catálogo candidato**, no padrón ni local activo.

**Cómo se usa:**
```bash
python src/v2/build_i10_dgdgas_staging.py   # regenera staging + agregados (offline)
python src/v2/validate_v2_setup.py          # valida setup, columnas y privacidad
```

## Etapa 3.5 — Normalización interna de I10 (barrios y rubros)

**Qué se creó:**
- Doc `17_normalizacion_i10_barrios_y_rubros.md`.
- Configs `config/v2/barrios_caba_aliases_v2.csv` (48 oficiales + aliases + genéricos + fuera de
  CABA, desde la fuente local `data/raw/geo_barrios.geojson`) y
  `config/v2/reglas_desagregacion_i10_v2.csv`.
- Script offline `src/v2/normalize_i10_dgdgas.py`.
- **Interno (gitignored):** `outputs/v2/internal/i10_dgdgas_establecimientos_normalizados.csv`.
- **Sanitizados:** `i10_dgdgas_calidad_barrios.csv`, `i10_dgdgas_agregado_barrio_normalizado.csv`,
  `i10_dgdgas_agregado_rubro_normalizado.csv`, `i10_dgdgas_desagregacion_hojas_mixtas.csv`,
  `i10_dgdgas_pendientes_revision.csv`.
- Pack `outputs/v2/sanitized/PACK_DATAGASTRO_V2_ETAPA_3_5_NORMALIZACION_I10.zip`.

**Resultado:** 1.380/2.480 (55,6%) con barrio normalizado a los 48 barrios oficiales; 955 sin
barrio, 42 ambiguos, 29 fuera de CABA, 12 múltiples, 62 pendientes. Rubro: 391 de hojas mixtas
desagregados tentativamente, 587 mixtos + 278 taxonómicos quedan pendientes.

**Qué NO se hizo:** sin requests, sin geocodificar, sin deduplicar contra externas, sin padrón
final, sin exponer nombres/direcciones. I10 sigue siendo fuente interna de validación.

```bash
python src/v2/normalize_i10_dgdgas.py   # normaliza (offline)
python src/v2/validate_v2_setup.py      # valida setup, columnas y privacidad
```

## Guardrails (resumen, ganan ante conflicto)

- **Drive es solo lectura.** No tocar el pipeline V1 ni F01–F05 ni casas de pastas sin permiso.
- **Separar universos:** públicas (F0x), internas (I0x), externas/privadas (E0x). No mezclar.
- **No inventar** datos, URLs, IDs ni métricas. Respetar `--strict-real`.
- **Habilitación ≠ local activo.** Padrón candidato, no censo.
- **No scraping** de plataformas privadas. Solo APIs oficiales, datos abiertos o convenios.
- **No exponer datos personales.** Brutos sensibles en carpetas gitignored; sólo se publican
  agregados sanitizados. Sin `place_id`, API keys, teléfonos, emails ni direcciones en
  entregables externos.
- **Sin commit/push** sin autorización explícita.
