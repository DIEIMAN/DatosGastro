# DataGastro V2 — Modelo de datos propuesto

> Propuesta de modelo. **No** se implementa todavía. Define tablas, propósito y campos
> principales. Sigue el estilo de V1: campos de calidad obligatorios, trazabilidad por fila,
> separación de universos y agregados sin filas sensibles.

## 1. Diagrama lógico (resumen)

```text
dim_fuente ───────────────┐
                          │
dim_rubro_gastronomico ───┤
dim_marca_cadena ─────────┤
dim_territorio ───────────┤
                          ▼
            dim_establecimiento_candidato  (1 fila = 1 entidad resuelta)
                          ▲
        ┌─────────────────┼─────────────────┬────────────────────┐
fact_deteccion_fuente  fact_validacion_   fact_trayectoria_   (puente_taxonomia_v1_v2)
(1 fila = 1 detección)  manual             documental
                          
fact_evento_gastronomico  (eventos/ediciones, hereda F04)
```

## 2. Campos de calidad obligatorios (en toda fact)

Heredados de V1: `calidad_dato`, `requiere_validacion`, `motivo_validacion`,
`fecha_consulta` / `fecha_extraccion`, `origen_dato`, `limitaciones`.

## 3. Dimensiones

### `dim_fuente`
- **Propósito:** catálogo de fuentes con su rol metodológico.
- **Campos:** `id_fuente`, `codigo` (F02, E01, E02, ...), `nombre`, `universo` (F/I/E),
  `naturaleza` (oficial / operativo / auxiliar / documental / interno), `url_fuente`,
  `licencia`, `fecha_consulta`, `apto_dashboard`, `limitaciones`.

### `dim_rubro_gastronomico`
- **Propósito:** taxonomía v2 (doc 01).
- **Campos:** `id_rubro`, `categoria_principal`, `subcategoria`, `incluye`, `excluye`,
  `fuentes_sugeridas`, `riesgo_metodologico`, `criterio_de_validacion`,
  `pendiente_revision_taxonomica` (si/no).

### `dim_marca_cadena`
- **Propósito:** marcas/cadenas conocidas y detectadas.
- **Campos:** `id_marca`, `nombre_marca`, `nombre_normalizado`, `es_marca_conocida` (si/no),
  `cantidad_sucursales_detectadas`, `fuentes_evidencia`, `observaciones`.

### `dim_territorio`
- **Propósito:** comuna / barrio / geometría GCBA (reutiliza `geo_comunas.geojson`,
  `geo_barrios.geojson`).
- **Campos:** `id_territorio`, `comuna`, `barrio`, `area_km2`, `geometria_ref`,
  `fuente_geo` (GCBA), `metodo_asignacion` (punto-en-polígono / declarado).

### `dim_establecimiento_candidato` (tabla central)
- **Propósito:** **1 fila = 1 entidad gastronómica candidata resuelta** (post-deduplicación).
- **Campos principales:**
```text
id_candidato
nombre_comercial            (SENSIBLE — no a entregables externos)
direccion_normalizada       (SENSIBLE — no a entregables externos)
lat, lon                    (SENSIBLE a nivel fila)
id_territorio               → dim_territorio (comuna/barrio)
id_rubro_principal          → dim_rubro_gastronomico
id_rubro_secundario         (opcional)
categoria_secundaria        (texto, doble función)
tipo_establecimiento        cadena | independiente | indeterminado
id_marca                    → dim_marca_cadena (si aplica)
es_historico_emblematico    si | no
nivel_confianza             C0..C5 / X  (doc 03)
etiqueta_confianza          multifuente_alto | oficial_estricto | ...
fuentes_detectan            lista de códigos
cantidad_fuentes
fuente_principal
requiere_revision_manual    si | no
confirmado_territorial      si | no | pendiente
business_status             (de Google, si existe) → flag posible_cierre
calidad_dato, requiere_validacion, motivo_validacion, origen_dato, limitaciones, observaciones
```

## 4. Tablas de hechos

### `fact_deteccion_fuente`
- **Propósito:** **1 fila = 1 aparición de una entidad en una fuente** (antes de resolver
  entidad). Es la materia prima de la deduplicación y la trazabilidad.
- **Campos:** `id_deteccion`, `id_candidato` (asignado al resolver), `id_fuente`,
  `id_externo_fuente` (place_id / osm_id / id_agc — **SENSIBLE**), `nombre_fuente`,
  `direccion_fuente`, `lat_fuente`, `lon_fuente`, `tipos_fuente` (types/tags/rubro_agc),
  `clasificacion_local` (A/B/C u homólogo), `confianza_local`, `query_origen`,
  `fecha_extraccion`, `motivo_clasificacion`.

### `fact_validacion_manual`
- **Propósito:** decisiones humanas trazables (I01) sobre casos dudosos.
- **Campos:** `id_validacion`, `id_candidato`, `revisor`, `fecha`, `decision`
  (confirma_rubro / cambia_rubro / descarta / marca_pendiente), `nivel_confianza_resultante`,
  `motivo`, `evidencia_consultada`.

### `fact_trayectoria_documental`
- **Propósito:** referencias documentales asociadas a entidades/casos (doc 07).
- **Campos:** `id_referencia`, `id_candidato` (o `id_caso`), `titulo`, `medio`, `url`,
  `fecha_publicacion`, `fecha_consulta`, `autor`, `afirmacion_sostenida`, `tipo_fuente`,
  `confiabilidad`, `cita_textual`.

### `fact_evento_gastronomico`
- **Propósito:** eventos/ediciones gastronómicas (hereda F04, relevamiento manual trazable).
- **Campos:** `id_evento`, `nombre`, `tipo_evento`, `id_territorio`, `fecha_completa`,
  `id_organizador`, `id_fuente`, `url_fuente`, `apto_dashboard`, `limitaciones`.
- **Nota:** **no** representa el universo completo de eventos de CABA (regla V1).

## 5. Tablas puente

### `puente_taxonomia_v1_v2`
- Mapea `dim_categoria_gastronomica` (V1) ↔ `dim_rubro_gastronomico` (V2). Preserva
  compatibilidad con el pipeline público.

### `puente_candidato_evento` (opcional)
- Vincula entidades con eventos donde participan (ej.: feria con puestos identificados).

## 6. Granularidad y reglas (heredadas de V1)

```text
- fact_deteccion_fuente:        1 fila = 1 detección en 1 fuente.
- dim_establecimiento_candidato:1 fila = 1 entidad resuelta (deduplicada).
- No sumar detecciones como si fueran entidades.
- No sumar universos distintos (oficial/operativo) en un total único sin nota.
- Lo descartado (X) se conserva en una vista aparte, no se borra.
```

## 7. Sensibilidad y almacenamiento

| Tabla | Sensibilidad | Dónde vive |
|---|---|---|
| `dim_establecimiento_candidato` (con nombre+dirección) | Alta (datos de terceros) | **gitignored** |
| `fact_deteccion_fuente` (con place_id/osm_id/dirección) | Alta | **gitignored** |
| `fact_trayectoria_documental` | Media (público, sin datos personales) | versionable con cuidado |
| `dim_rubro`, `dim_fuente`, `dim_territorio`, puentes | Baja (catálogos) | versionable |
| Agregados (por comuna/barrio, densidad, conteos) | Baja | versionable / entregables |

Regla: **agregados y diccionarios se versionan; filas individuales sensibles, no.**

## 8. Campos derivados para analytics

```text
- densidad_por_km2          (conteo / area_km2 del territorio)
- ratio_cadena_independiente
- cobertura_por_subcategoria_x_comuna
- distribucion_por_nivel_confianza
- brecha_oficial_vs_operativo  (AGC vs Google/OSM, como diagnóstico de cobertura)
```
