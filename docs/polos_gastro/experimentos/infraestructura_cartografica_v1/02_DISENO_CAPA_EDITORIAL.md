# Diseño de la capa editorial de macrozonas (Etapa Infra-2)

**Fecha:** 2026-07-08 · **Carácter:** propuesta de diseño experimental. No reemplaza nada
del pipeline oficial; es la especificación de un archivo nuevo que hoy no existe.

## Principio rector

**Esta capa es la fuente, no una salida.** El pipeline de microzonas (V1) la LEE; nunca la
escribe. Ningún script de clustering, de poligonización ni de QA de microzonas debe volver
a tocar este archivo. Es exactamente el rol que hoy cumplen `barrios_caba.geojson` o
`comunas_caba.geojson`: una capa de referencia estable, versionada por decisión humana.

## 1. Jerarquía: macrozona vs. subzona

El inventario (Infra-1) confirmó algo que la validación ya insinuaba: "Palermo" no es una
sola cosa, es un **polo** que agrupa **subzonas** (Soho, Hollywood, Las Cañitas, y en los
mapas editoriales también Palermo Chico y Palermo Nuevo/Botánico como contexto). Lo mismo
pasa con Belgrano (Barrio Chino + Bajo Belgrano + Belgrano R) y con Corrientes/Abasto. La
capa debe modelar esto explícitamente con dos niveles, no aplanarlos en una sola lista:

- **`nivel = "polo"`**: la unidad editorial de más alto nivel (Palermo, Belgrano,
  Corrientes/Abasto, …) — equivalente a lo que el prototipo V1 llamó "macrozona" y usó
  como contenedor de clustering.
- **`nivel = "subzona"`**: unidades internas con identidad propia (Palermo Soho, Palermo
  Hollywood, Las Cañitas, Barrio Chino, …) — lo que HDBSCAN venía re-descubriendo como
  clusters separados dentro de un mismo contenedor.

Cada subzona referencia a su polo por `polo_id`. Un polo sin subzonas propias (San Telmo,
Villa Crespo, Chacarita, hoy) puede tener una única fila con `nivel = "polo"` y
`es_contenedor_clustering = true`.

## 2. Esquema de atributos — `macrozonas_editorial_vN.geojson`

FeatureCollection en EPSG:4326 (estándar del resto del proyecto). Un feature = un polígono
(o, mientras no esté digitalizado, `null` con estado `pendiente`).

| Campo | Tipo | Ejemplo | Notas |
|---|---|---|---|
| `id` | string, estable entre versiones | `MZ_PALERMO_SOHO` | Prefijo `MZ_` + nombre en mayúsculas sin acentos; nunca se reutiliza para otra zona aunque se borre |
| `nombre` | string | "Palermo Soho" | Nombre editorial visible |
| `nivel` | `"polo"` \| `"subzona"` | `"subzona"` | Ver §1 |
| `polo_id` | string o null | `MZ_PALERMO` | Solo si `nivel = "subzona"` |
| `es_contenedor_clustering` | bool | `true` | Si HDBSCAN corre directamente sobre esta geometría (polos sin subzonas, o cuando se decide clusterizar por subzona en vez de por polo) |
| `tipo_geometria` | enum | `"poligono_real"` | `poligono_real` (trazado sobre callejero) / `poligono_aproximado` (mejor esfuerzo sin calles completas) / `elipse_editorial` (heredado de fase16, a migrar) / `pendiente` (sin geometría aún) |
| `metodo_construccion` | string | "Trazado sobre callejero GCBA a partir de calles límite de ficha PG001A" | Trazabilidad de cómo se hizo, no solo qué es |
| `calles_limite` | array de string o null | `["Scalabrini Ortiz", "Córdoba", "Juan B. Justo", "Santa Fe"]` | Cuando el método es por calles; vacío si no aplica |
| `fuente` | array de string | `["ficha:PG001A", "callejero_gcba_2026_06_02"]` | IDs de fichas de polo + capas base usadas; ver §correspondencia |
| `fecha_creacion` | date ISO | `2026-07-08` | Cuándo se trazó esta versión del polígono |
| `fecha_actualizacion` | date ISO | `2026-07-08` | Última edición (puede diferir de creación) |
| `autor` | string | "Diego / DGDGAS" o "Claude (asistido)" | Quién trazó/editó, no quién aprobó |
| `estado_revision` | enum | `"borrador"` | `borrador` / `revisado` / `aprobado_editorial` — ningún polígono con estado distinto de `aprobado_editorial` debería alimentar un informe institucional |
| `nivel_confianza` | enum | `"alta"` | `alta` (calles límite documentadas y trazadas), `media` (aproximado con criterio editorial, sin las 4 calles), `baja` (solo nombre de barrio o sin delimitación), `sin_geometria` |
| `version_capa` | string | `"v1"` | Ver Etapa Infra-5 (versionado) |
| `reemplaza_a` | string o null | `null` | `id` de la versión anterior de este mismo polígono, si cambió sustancialmente (changelog) |
| `contiene_semilla_ids` | array de string o null | `["Don Julio", "La Cabrera", …]` | Nombres/IDs de la semilla Fase 13 que este polígono debería contener — usado por el QA (Infra-6), no editado a mano |
| `observaciones` | string | "Incluye Distrito Arcos; límite este ajustado 2026-07-08 tras revisión visual" | Notas humanas libres |

## 3. Ejemplo (Palermo Soho, con datos reales de esta sesión)

```json
{
  "type": "Feature",
  "properties": {
    "id": "MZ_PALERMO_SOHO",
    "nombre": "Palermo Soho",
    "nivel": "subzona",
    "polo_id": "MZ_PALERMO",
    "es_contenedor_clustering": true,
    "tipo_geometria": "poligono_real",
    "metodo_construccion": "Poligono trazado con el callejero GCBA (fase15) usando las 4 calles limite documentadas en la ficha PG001A: Scalabrini Ortiz, Cordoba, Juan B. Justo y Santa Fe.",
    "calles_limite": ["Scalabrini Ortiz", "Cordoba", "Juan B. Justo", "Santa Fe"],
    "fuente": ["ficha:PG001A_PALERMO_SOHO", "callejero_gcba_2026_06_02"],
    "fecha_creacion": "2026-07-08",
    "fecha_actualizacion": "2026-07-08",
    "autor": "Claude (asistido) - pendiente de revision editorial de Diego",
    "estado_revision": "borrador",
    "nivel_confianza": "alta",
    "version_capa": "v1",
    "reemplaza_a": null,
    "contiene_semilla_ids": null,
    "observaciones": "Ver Etapa Infra-4 para el trazado experimental y su QA."
  },
  "geometry": { "type": "Polygon", "coordinates": [[ /* ... */ ]] }
}
```

## 4. Tabla de correspondencia (trazabilidad hacia atrás)

Un archivo compañero `correspondencia_fichas_macrozonas.csv` (no geoespacial) mapea:

| `id_macrozona` | `ficha_id` | `polo_v1_prototipo` | `subzona_editorial_fase16` |
|---|---|---|---|
| MZ_PALERMO_SOHO | PG001A | Palermo | Palermo Soho |
| MZ_PALERMO_HOLLYWOOD | PG001B | Palermo | Palermo Hollywood |
| MZ_COSTANERA_NORTE | PG009 | Costanera Norte | (sin equivalente) |

Esto permite migrar resultados existentes (el prototipo V1 clusterizó por "polo" en el
sentido amplio) sin perder el hilo, y saber qué capa vieja reemplaza cada polígono nuevo.

## 5. Por qué no reusar directamente `subzonas_editoriales_geometrias.geojson` (fase16)

Se decidió **no heredar el esquema de fase16** (campos `mapa`, `color_sugerido`,
`mostrar_en_mapa`, etc.) porque esos campos son de **presentación cartográfica** (cómo se
dibuja en un mapa de informe), no de **gobierno de datos** (quién la creó, con qué
confianza, qué versión). Son capas con propósitos distintos: fase16 puede seguir
existiendo para los mapas oficiales; esta capa nueva es el insumo del pipeline de
clustering. Si en el futuro se quiere que los mapas oficiales dibujen esta capa nueva en
vez de las elipses, un script de traducción simple genera el estilo de presentación a
partir de `macrozonas_editorial_vN.geojson` — no al revés.
