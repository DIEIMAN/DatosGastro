# QA — `macrozonas_v1_experimental.geojson` (Tarea 4)

**Fecha:** 2026-07-08 · Corrida con `qa_macrozonas_v1.py` (reusa gates/banderas de
`qa_capa_editorial.py` + controles nuevos de esta tarea: contención de entidades,
cercanía fuera, tamaño).

## Resultado

**Pasa los gates duros tras una corrección** (ver abajo). 6 banderas activas, ninguna
bloqueante, todas con explicación y acción sugerida.

## Gate duro encontrado y corregido

- **G1 — geometría inválida en `MZ_CABALLITO`** (autointersección). Causa: la
  reproyección de EPSG:5347 (métrico, donde se calculan las intersecciones) a EPSG:4326
  introdujo una autointersección de precisión numérica en un polígono con geometría
  compleja (barrio ∩ buffer de semilla). Se agregó una limpieza (`buffer(0)` /
  extracción de partes poligonales) **después** de reproyectar, no solo antes — el gate
  pasó a 0 errores tras la corrección. Documentado en el script y en
  `METODOLOGIA_MACROZONAS_V1.md` (ficha de Caballito) para que quede explícito que fue
  un problema de precisión de la construcción, no de los datos de origen.

## Banderas (no bloquean, quedan para revisión editorial)

| Bandera | Detalle | Severidad real |
|---|---|---|
| B1 | `MZ_PUERTO_MADERO`: 4 huecos interiores | **Esperada e intencional** — son los diques de agua dentro del barrio; no requiere acción. |
| B1 | `MZ_CABALLITO`: 1 hueco interior | A revisar: podría ser un hueco real del barrio oficial o un artefacto de la intersección con el buffer de semilla. |
| B2 | `MZ_PALERMO` × `MZ_COSTANERA_NORTE`: 67,8 % de solape | Bajo impacto operativo: `MZ_PALERMO` no es contenedor de clustering (`es_contenedor_clustering=false`), es contextual. No genera doble procesamiento. |
| B2 / SOLAPE | `MZ_AVENIDA_CORRIENTES` × `MZ_MICROCENTRO_Y_CENTRO`: 49,2 % de solape, **406 entidades en la zona compartida** | **Alto impacto operativo**: ambas SÍ son contenedores de clustering. Esas 406 entidades quedarían procesadas dos veces en una corrida sin resolver esta frontera. **Es el hallazgo más urgente de esta tarea.** |
| B3 | Cobertura de CABA por macrozonas nivel `polo`: 19,66 % | Esperado y ya documentado desde el inventario (Infra-1): los 12 polos no pretenden cubrir toda la ciudad; el resto es la capa diagnóstica de "zonas emergentes" del prototipo V1. |
| B4 | 14 de 14 features en `estado_revision = borrador` | Esperado: nada de esta versión fue aprobado todavía. Recordatorio automático de que no debe usarse en un informe institucional. |

## Contención de entidades y cercanía (`qa_contencion_entidades.csv`)

| Macrozona | Área (ha) | Entidades dentro | Densidad/ha | Cercanas fuera (≤150 m) |
|---|---|---|---|---|
| Palermo Soho | 154,9 | 373 | 2,41 | 173 |
| Palermo Hollywood | 88,5 | 213 | 2,41 | 51 |
| Palermo (contextual) | 1.585,6 | 1.360 | 0,86 | 159 |
| San Telmo | 123,2 | 171 | 1,39 | 71 |
| Belgrano | 202,0 | 273 | 1,35 | 83 |
| Chacarita | 311,7 | 116 | 0,37 | 86 |
| Villa Crespo | 160,5 | 179 | 1,12 | 68 |
| Puerto Madero | 503,2 | 85 | 0,17 | 30 |
| Recoleta | 245,8 | 404 | 1,64 | 147 |
| Caballito | 347,4 | 265 | 0,76 | 140 |
| Costanera Norte | 225,1 | 5 | 0,02 | 0 |
| Avenida Caseros/Barracas | 55,9 | 18 | 0,32 | 32 |
| Avenida Corrientes | 291,5 | 754 | 2,59 | 321 |
| Microcentro y Centro | 229,0 | 763 | 3,33 | 254 |

Lectura: **Costanera Norte tiene 0,02 entidades/ha** (225 ha con solo 5 entidades) — la
señal más clara de que esta macrozona necesita revisión antes de cualquier uso, más allá
de que técnicamente "pase" el QA de tamaño (no está fuera de los umbrales 40-600 ha
porque el área en sí no es ni muy grande ni muy chica; el problema es la falta de
evidencia, que el QA de tamaño no captura por diseño — lo captura la columna de
densidad). Puerto Madero (0,17/ha) es el segundo caso más flojo en este sentido.

## Gates de tamaño (600 ha máximo, 40 ha mínimo)

**0 activados.** Ninguna de las 12 macrozonas-contenedor quedó fuera de este rango
(la más chica es Caseros/Barracas con 55,9 ha; la más grande con clustering activo es
Puerto Madero con 503,2 ha). `MZ_PALERMO` (1.585,6 ha) no se evalúa contra este gate
porque no es un contenedor de clustering.

## Conclusión del QA

La capa es publicable en términos de validez geométrica y consistencia de atributos.
**Antes de usarla en una corrida real del pipeline hay que resolver el solapamiento
Corrientes/Microcentro** (406 entidades compartidas) — es una decisión editorial, no algo
que el QA pueda resolver solo. El resto de las banderas son documentación de
incertidumbre esperada (confianza baja/media declarada), no defectos ocultos.
