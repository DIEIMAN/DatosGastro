# Inventario de puntos disponibles — Experimento de clustering espacial (PolosGastro)

**Fecha:** 2026-07-07
**Carácter:** documento interno de trabajo, experimental. No forma parte del informe vigente de
PolosGastro ni modifica ninguna fase cerrada.

## Objetivo del relevamiento

Identificar archivos locales del repo con puntos georreferenciados de locales gastronómicos
utilizables como input de un experimento de clustering espacial, cuyo fin es generar
**polígonos exploratorios** (áreas estimadas de concentración) como **capa auxiliar** para
contrastar con las delimitaciones editoriales. Los resultados **no constituyen límites
oficiales** y **requieren revisión territorial**.

## Criterios de relevamiento

- Solo archivos locales al repo (sin APIs externas, sin descargas nuevas).
- No se abrieron archivos con credenciales ni se exportaron filas con datos sensibles.
- Se revisaron: `outputs/polos_gastro/`, `docs/polos_gastro/`, `PolosGastro/`,
  `data/processed/`, `data/analytics/`, `scripts/polos_gastro/`.

## Archivos relevados

### 1. `outputs/polos_gastro/fase13_mapas/tablas/locales_para_mapa_revision.csv` ⭐ candidato principal

| Aspecto | Detalle |
|---|---|
| Filas | 106 |
| Campos relevantes | `polo`, `subzona`, `nombre_lugar`, `lat`, `lon`, `estado_consolidado`, `decision_borrador4`, `mostrar_mapa_revision`, `mostrar_mapa_publico`, `observacion` |
| Coordenadas | Sí — 106/106 con lat/lon numéricas (lat −34.637 a −34.480; lon −58.571 a −58.343) |
| Polo/zona | Sí — 13 polos, 12 subzonas |
| Score/rating/reviews | No |
| Usable para clustering | **Sí** — es la tabla de revisión de mapas de Fase 13 con el universo completo de 106 locales semilla geolocalizados |
| Riesgos/limitaciones | 1 punto fuera de CABA (Belgrano, lat −34.4796 / lon −58.5707 — probable sede errónea, `vigencia_no_confirmada`). 11 filas `duplicado_probable` que inflarían la densidad si se cuentan doble. Los estados incluyen casos aún no validados humanamente (`zona_sucursal_a_revisar`, `query_a_corregir`). Universo semilla curado editorialmente, no censo: la densidad refleja el muestreo, no la oferta total. |

Distribución de `estado_consolidado`: match_fuerte 32, match_razonable_revisar_sede 27,
zona_sucursal_a_revisar 25, duplicado_probable 11, vigencia_no_confirmada 8, query_a_corregir 3.

### 2. `outputs/polos_gastro/fase15_mapas_callejeros_v3/tablas/locales_para_mapas_v3.csv`

- 41 filas (39 con lat/lon), 6 polos, 10 subzonas; campos de curaduría visual.
- Usable pero es un **subconjunto curado** para los mapas V3: menos cobertura (solo 6 polos).
- Riesgo: sesgo de selección fuerte; clustering sobre 39 puntos fragmentaría demasiado.

### 3. `outputs/polos_gastro/fase13_mapas/tablas/polos_ejes_para_mapa_global.csv`

- 22 filas: **centroides aproximados por polo/eje**, no locales individuales.
- No usable como input de clustering (1 punto por polo); sí útil como referencia de etiquetas.

### 4. Resultados Google Places Fase 11 — versiones `_publicable` (3 archivos)

- `resultados_repiloto_tanda1_publicable.csv` (10), `resultados_tanda2_publicable.csv` (10),
  `resultados_corrida_ampliada_publicable.csv` (86).
- Tienen columnas `lat`/`lon` pero **vacías** (sanitizadas a propósito). No usables directamente.

### 5. Resultados Google Places Fase 11 — versiones `_interno` (3 archivos)

- Mismas tandas con `lat`, `lon`, `rating_interno`, `user_ratings_total_interno`,
  `google_place_id_interno`.
- **Tienen rating y cantidad de reseñas** (ya descargados; no requiere API nueva).
- Decisión: **se excluyen de este experimento.** Son archivos marcados internos; usarlos como
  peso arrastraría datos internos de Google Places a outputs experimentales y complicaría la
  trazabilidad. El experimento MVP usa peso 1 por punto. Queda anotado como extensión posible
  (peso auxiliar `score_aux`), solo con decisión explícita y sin publicar valores por local.

### 6. `outputs/polos_gastro/fase11_google_places_piloto/tablas/consolidado_tandas_google_places.csv`

- 106 filas, tabla decisional (estados, decisiones Borrador 4). **Sin coordenadas.**
- Útil como diccionario de estados por `id_local_semilla`, no como input de puntos.

### 7. `outputs/polos_gastro/fase10_reencuadre_y_locales/tablas/locales_semilla_polos_fase10.csv`

- 106 filas, universo semilla original. **Sin coordenadas.** No usable directo.

### 8. `outputs/polos_gastro/base_cartografica_visual_polos_gastro.csv` y `base_delimitacion_preliminar_polos_gastro.csv`

- 32 polos con delimitación **textual**, barrios asociados, precisión. Sin coordenadas.
- Útiles como contexto editorial para la comparación, no como puntos.

### 9. `outputs/polos_gastro/fase16_mapas_editoriales_v4/tablas/subzonas_editoriales_geometrias.geojson`

- 21 features (19 polígonos + 2 líneas) de **subzonas editoriales** con etiquetas.
- No es input de puntos: es la **capa editorial de comparación** para contrastar los polígonos
  exploratorios (Tarea 7). No se modifica.

### 10. `PolosGastro/cartografia/barrios_caba.geojson` y `comunas_caba.geojson`

- 48 barrios / 15 comunas de CABA. Cartografía base local.
- Uso: **filtro espacial** (límite de CABA) y fondo de referencia de los mapas. Solo lectura.

### 11. `data/processed/dim_ubicacion.csv` + `fact_establecimiento.csv` + `geo_cache.csv` (pipeline F01–F05)

- `dim_ubicacion`: 10.847 filas, 10.744 con lat/lon; `fact_establecimiento`: 2.823
  establecimientos; `geo_cache`: 7.639 direcciones geocodificadas.
- **No se usan en esta corrida.** Son el universo público del pipeline (F01–F05): mezclarlo con
  el universo semilla editorial de PolosGastro violaría la separación de universos (guardrail 3).
  Además la densidad de habilitaciones/registros no equivale a "locales activos" (guardrail 5).
- Anotado como **experimento futuro separado**: clustering sobre el universo público completo,
  en corrida propia y con su propia lectura metodológica. Solo lectura; el pipeline no se toca.

### 12. `outputs/polos_gastro/fase8_fuerte/tablas/insumo_mapa_contexto_objetivo_fase8_fuerte.csv`

- 47 barrios con conteos agregados (oferta registrada, habilitaciones). Nivel barrio, sin
  puntos. No usable para clustering de puntos; sí como contexto interpretativo.

## Conclusión del inventario

Existe un input claro y trazable: **`locales_para_mapa_revision.csv` (Fase 13)** — 106 locales
del universo semilla con coordenadas completas, polo y subzona, generado por
`scripts/polos_gastro/generar_mapas_fase13.py` a partir del consolidado de Fase 11.
La capa editorial de Fase 16 permite la comparación clusters vs. zonas actuales, y la
cartografía de `PolosGastro/cartografia/` provee el filtro CABA y el fondo de mapa.

**Limitación estructural a dejar explícita en todo output:** con ~100 puntos curados
editorialmente, los clusters describen la **estructura del universo semilla**, no la
concentración gastronómica real de la Ciudad. Los polígonos resultantes son exploratorios,
auxiliares y estimados; **no constituyen límites oficiales** y **requieren revisión
territorial**.
