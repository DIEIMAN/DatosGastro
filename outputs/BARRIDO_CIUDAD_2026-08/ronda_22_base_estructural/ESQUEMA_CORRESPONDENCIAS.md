# Correspondencias de esquema

| Requisito conceptual | Campo R22 / origen |
|---|---|
| ID estable | `establecimiento_uid`; `legacy_id` conserva el ID R11 |
| Nombre / normalización | `nombre`, `alias_nombre`, `nombre_normalizado` |
| Dirección y punto | `direccion`, `latitud`, `longitud`; no prueba operación |
| Barrio/comuna | cruce espacial con capas oficiales locales; se conserva `barrio_declarado` |
| Categoría / subcategoría | `categoria` R11 + `subcategoria` normalizada |
| Fuentes / familias / principal | `fuentes`, `familias_fuente`, `fuente_principal` |
| Frescura | `fecha_frescura_evidencia`; no se sustituye por fecha de metadato |
| Publicación | `nivel_publicacion` derivado de `citable_en_documento` |
| Vigencia | `estado_vigencia`, fecha, fuente y tipo de verificación; catálogo/POI no equivale a apertura |
| Referente / reconocimiento | `referente`, `tipo_referente`, `reconocimiento`, `reconocimiento_normativo` |
| Polo/ficha/sistema | `polo_ficha_sistema_asociado` + tabla explícita de relaciones |
| Punto instrumental | `punto_instrumental`; separado de existencia, vigencia y reconocimiento |

`EXISTE_EN_FUENTE`, `OPERATIVO`, `VIGENTE`, `REFERENTE`, `RECONOCIMIENTO_NORMATIVO` y `PUNTO_INSTRUMENTAL` son campos distintos y no se derivan uno de otro.
