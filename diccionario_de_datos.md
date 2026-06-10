# Diccionario de datos — Ecosistema Gastronómico de CABA

Ubicación de las tablas: `data/raw/` (crudo), `data/processed/` (modelo normalizado), `data/analytics/` (tablas para dashboard).

**Campos de calidad obligatorios** en toda tabla del modelo: `calidad_dato`, `requiere_validacion`, `motivo_validacion`, más `fecha_consulta` (en `dim_fuente`) o `fecha_extraccion` (en tablas raw). La trazabilidad a la fuente se resuelve por `id_fuente` → `dim_fuente` (que aporta `url_base` y `fecha_consulta`).

**Convención de marcado de faltantes** (tres valores distintos, nunca intercambiables):
- `No disponible`: el campo aplica pero el dato no se obtuvo.
- `No encontrado en fuente pública`: se buscó en fuente oficial y no figura.
- `Dato inferido`: derivado por regla, no leído de la fuente.
- `Requiere validación`: presente pero sin confirmar contra fuente prioritaria.

---

## Dimensiones

### `dim_fuente`
Catálogo de fuentes relevadas. PK `id_fuente` (F01…F16).
Campos: `nombre_fuente`, `tipo_fuente`, `organismo_entidad`, `url_base`, `confiabilidad`, `frecuencia_actualizacion`, `fecha_consulta` (date), `notas`.

### `dim_ubicacion`
Direcciones normalizadas y geocodificación. PK `id_ubicacion` (U…).
Campos: `direccion_original`, `direccion_normalizada` (salida USIG), `barrio` (catálogo Ley 2650), `comuna` (derivada del barrio, nunca a mano), `latitud`, `longitud` (WGS84), `codigo_postal`, `zona`, `calidad_geo` (exacta/interpolada/manual/sin_geo), `requiere_validacion`, `motivo_validacion`.
**Fila centinela `U00000`** ("No determinado"): destino de FK para eventos sin sede física única (ciclos / multi-local). Evita FKs huérfanas sin inventar una dirección.

### `dim_categoria_gastronomica`
Taxonomía de rubros, 2 niveles. PK `id_categoria` (C…).
Campos: `categoria_general` (Restauración, Pizzería / empanadas, Cafetería, Bar, Helado y dulce, Espacios), `subcategoria`, `descripcion`, `ejemplos`.

### `dim_organizador`
Organizadores de eventos. PK `id_organizador` (O…).
Campos: `nombre_organizador`, `tipo_organizador` (público / privado/mixto), `sector`, `web`, `observaciones`.

---

## Hechos

### `fact_establecimiento`
Locales gastronómicos. PK `id_establecimiento` (EST…).
FK: `id_categoria` → dim_categoria, `id_ubicacion` → dim_ubicacion, `id_fuente` → dim_fuente.
Campos propios: `nombre` (limpio de mojibake), `estado` (activo/cerrado/dudoso/sin_verificar), `web`, `redes`, `telefono`, `fecha_alta_detectada`, `fecha_ultima_actualizacion`, + campos de calidad.

### `fact_evento_gastronomico`
Eventos y ediciones. PK `id_evento` (EVT…).
FK: `id_ubicacion` → dim_ubicacion (U00000 si no hay sede única), `id_organizador` → dim_organizador, `id_fuente` → dim_fuente.
Campos propios: `nombre_evento`, `descripcion`, `fecha_inicio`, `fecha_fin`, `periodicidad`, `tipo_evento`, `gratuito`, `requiere_inscripcion`, `cantidad_asistentes_estimada`, `cantidad_puestos_estimada`, `estado`, `link_evento`, + calidad.

### `fact_programa_politica`
Programas, políticas e iniciativas. PK `id_programa` (PRG…).
FK: `id_fuente` → dim_fuente.
Campos propios: `nombre_programa`, `organismo_responsable`, `fecha_inicio`, `fecha_fin`, `estado`, `tipo_programa`, `objetivo`, `beneficiarios`, `alcance_geografico`, `resultados`, `metricas_publicadas`, `link`, + calidad.

### `fact_mercado_feria`
Ferias, mercados y patios. PK `id_mercado_feria` (MF…).
FK: `id_ubicacion` → dim_ubicacion, `id_fuente` → dim_fuente.
Campos propios: `nombre`, `tipo_espacio`, `gestion`, `dias_funcionamiento`, `horarios`, `cantidad_puestos`, `rubros`, `estado`, `link`, + calidad.

---

## Puentes (N:N) — hoy vacíos, listos para poblar

- `puente_evento_establecimiento`: (`id_evento`, `id_establecimiento`) PK + `rol`, `observaciones`.
- `puente_programa_establecimiento`: (`id_programa`, `id_establecimiento`) PK + `tipo_beneficio`, `fecha_participacion`, `observaciones`.
- `puente_evento_categoria`: (`id_evento`, `id_categoria`) PK + `observaciones`.

---

## Tablas analíticas (`data/analytics/`)
Se recalculan **desde el modelo** vía `src/build_analytics.py` (no se editan a mano):
`analytics_resumen_ejecutivo`, `analytics_establecimientos_por_categoria_barrio`, `analytics_mapa_oportunidades`, `analytics_eventos_por_barrio`, `analytics_programas_por_anio`.
Todas llevan una columna/nota que aclara que están calculadas sobre la muestra seed (n=6), no sobre el padrón completo.
