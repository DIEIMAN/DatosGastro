# Informe de auditoría QA territorial V3

**Rol:** `auditor_qa` independiente  
**Fecha:** 2026-07-11  
**Alcance:** `CORRIDA_TERRITORIAL_V3`, solo lectura  
**Política:** `POLITICA_OPERATIVA_DATAGASTRO` V1.1 con hotfix de empaquetado y trazabilidad V1.1.1  
**Handoff documental usado:** exclusivamente `HANDOFF_DOCUMENTAL_CARTOGRAFO_V1_1.md`  
**Estado auditado:** experimental; no constituye aprobación oficial

## Resumen ejecutivo

La corrida produce resultados territoriales coherentes y capas GeoJSON técnicamente válidas. Los KPI principales se recalcularon desde la asignación sanitizada y coinciden con el lock, las tablas y los documentos. Belgrano queda representado como un polo con tres centralidades y siete piezas topológicas; Recoleta como una unidad continua con nueve núcleos analíticos y cuatro huecos internos; Costanera Norte como cuatro componentes y cinco piezas topológicas, sin conectores.

La integración editorial directa no debe comenzar todavía. Las láminas de presentación conservan códigos técnicos, puntos, categorías de fuente, la marca interna DataGastro y el pie `EXPERIMENTAL / NO OFICIAL`. También falta el mapa general exigido por el contrato y no se entregaron de forma explícita la tabla de estilos, el bbox de render ni la declaración de fondo por lámina. Estas brechas son cartográficas y editoriales; no invalidan las geometrías ni requieren una nueva corrida analítica.

**Veredicto:** `APTO_CON_AJUSTES_CARTOGRAFICOS`.

## 1. Integridad del paquete

| Control independiente | Resultado |
| --- | --- |
| ZIP | Abre y `testzip` no detecta miembros corruptos |
| Tamaño | 9.339.428 bytes |
| SHA-256 | `e3c150905a546b0b363de03128a4afb332d9451a8a700b404c4b34bc3c038e86` |
| Miembros | 73, sin duplicados |
| Rutas | 0 absolutas, 0 travesías `..`, 0 separadores invertidos |
| Archivos temporales/secretos | 0 nombres sospechosos |
| Manifest interno | 70 filas; 70/70 archivos, tamaños y hashes verificados |
| Archivos fuera del manifest | El propio manifest, exclusión correcta; dos `CHECKSUMS_SHA256.txt`, exclusión no documentada |
| Extracción | Exitosa en directorio temporal y reverificada |
| Scripts | 4/4 compilables en memoria; sin rutas absolutas embebidas |
| UTF-8 | Nombres y textos estructurados leídos correctamente |

El checksum raíz del paquete cubre el manifest definitivo y los 70 archivos inventariados. El SHA-256 del ZIP protege además los dos archivos de checksums no inventariados. La omisión de estos dos miembros del manifest es una brecha de completitud literal, no evidencia de corrupción.

## 2. Reproducibilidad

Los 27 insumos del snapshot existen en el repositorio y sus hashes actuales coinciden con los esperados. La configuración fija semilla, CRS, parámetros y universos. Los scripts del repositorio y sus copias dentro del ZIP son idénticos por SHA-256 y no contienen rutas de máquina.

La reproducción es viable dentro de este checkout, con los baselines y el entorno existentes. El ZIP no es autocontenido para un tercero externo: no incluye los 27 insumos, el callejero ni versiones congeladas de dependencias Python. El README indica correctamente que debe ejecutarse desde la raíz del repositorio, pero no explicita esta limitación ni documenta versiones de `geopandas`, `shapely`, `scikit-learn`, `networkx`, `matplotlib`, `numpy`, `pandas`, `pyproj` y `Pillow`.

Clasificación: **reproducible en el repositorio actual; reproducibilidad externa parcial**.

## 3. Validación de métricas

Se recalcularon 1.536 referencias únicas desde `ASIGNACION_PUNTOS_TERRITORIAL_V3.csv`, sin duplicados. Los resultados centrales coinciden exactamente:

| Polo/modelo | Universo | Incluidos | Cobertura | Fuente externa | Estabilidad | Piezas |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Belgrano BEL-A | 697 | 248 | 35,58 % | 53,23 % | 0,765 | 7 |
| Recoleta REC-A | 767 | 602 | 78,49 % | 46,51 % | 0,626 | 1 |
| Costanera Norte CN-DEC10 | 72 | 71 | 98,61 % | 92,96 % | 0,770 | 5 |

No se detectó drift entre KPI lock, métricas, matriz de decisión y documentos. La cobertura baja de Belgrano está informada, pero conviene reforzar editorialmente que 449 de 697 puntos quedan fuera de BEL-A y que la delimitación caracteriza concentraciones, no toda la oferta de la macrozona.

Existe una diferencia explicable pero no documentada en el área de Belgrano: 0,3975 km² corresponde a la geometría de modelo previa a la simplificación; el GeoJSON de presentación exportado mide 0,385365 km², 3,05 % menos. El script simplifica a 12 m después de calcular la métrica. No es drift del KPI, pero el handoff debe distinguir ambas superficies.

## 4. Belgrano

BEL-A es preferible a BEL-C para la decisión vigente: conserva tres centralidades interpretables y evita presentar doce piezas crudas como jerarquías equivalentes. La capa de presentación contiene tres features y siete piezas topológicas; dos centralidades son multiparte. No existe hull común ni conexión artificial. El agregado de presentación es acotado y deriva de cierres locales, aunque la diferencia simétrica respecto de la analítica es 12,88 % del área analítica, por lo que debe conservarse la separación de capas.

Belgrano R se mantiene como `SECTOR_SECUNDARIO` en datos y documentos. En el mapa de presentación aparece solo como “Belgrano R”, sin expresar esa jerarquía. La etiqueta larga Barrio Chino–Belgrano C–Barrancas–Pasaje Echeverría se superpone con Bajo Belgrano y con los puntos. La lámina tampoco explica visualmente por qué tres centralidades producen siete piezas.

Resultado territorial: **APTO**. Mapa institucional: **AJUSTE_IMPORTANTE**.

## 5. Recoleta

REC-A es preferible a REC-B: cubre prácticamente el mismo universo, tiene estabilidad levemente mayor y evita introducir una partición adicional. La presentación incorpora solo 4,07 % de área fuera de la unión analítica, conserva cuatro huecos y deja 99,99999 % de su superficie dentro de Recoleta; la intersección numérica con Retiro es despreciable y atribuible al borde cartográfico. No se observa invasión material de Retiro ni una envolvente amplia sin apoyo.

La estabilidad 0,626 debe seguir calificándose como moderada. La etiqueta general está desplazada hacia el oeste y compite con la trama de puntos; la forma irregular y los huecos se leen, pero requieren simplificación editorial para media página.

Resultado territorial: **APTO**. Mapa institucional: **AJUSTE_IMPORTANTE**.

## 6. Costanera Norte

La capa analítica contiene exactamente `CN_C01`, `CN_C02`, `CN_C03` y `CN_C04`. `CN_C01` es multipolígono de dos partes; los otros tres componentes tienen una parte cada uno. Por eso cuatro componentes producen cinco piezas topológicas. La presentación es geométricamente idéntica a la analítica: 0 % de diferencia simétrica, 0 conectores y vacíos preservados.

Se concilian 72 registros: 71 incluidos y uno de borde sin asignación. `CN_C02` contiene 11 señales externas almacenadas y 0 F01/F02, sin inferencias regulatorias. La dependencia externa de 92,96 % está formulada como límite de fuente.

La lámina de presentación no identifica los cuatro componentes y ubica la única etiqueta junto al componente sur, lo que puede hacerla parecer local. El amplio espacio vacío es territorialmente coherente, pero la lectura en media página requiere jerarquía y rótulos editoriales o una clave externa. El comparativo cuadrado presenta solapamiento del pie y muestra `CN-DEC10`.

Resultado territorial: **APTO**. Mapa institucional: **AJUSTE_IMPORTANTE**.

## 7. QA de GeoJSON

Los ocho GeoJSON parsean, declaran CRS84 compatible con EPSG:4326, contienen geometrías válidas, no vacías y sin duplicados de sus identificadores naturales. No se detectaron propiedades de nombre comercial, domicilio, teléfono, email, CUIT, DNI o `place_id`.

Las capas de presentación no modificaron las analíticas: son archivos separados y mantienen los originales. Costanera conserva geometría exacta; Recoleta aplica el cierre documentado; Belgrano agrupa y cierra localmente. Detalle en `QA_GEOJSON_INDEPENDIENTE_V3.csv`.

## 8. QA visual

Se abrieron e inspeccionaron los 15 PNG; se contrastaron dimensiones, DPI y SVG. Todos los PNG son opacos, fondo blanco y aproximadamente 220 dpi. Las láminas técnicas son utilizables para revisión interna. Ninguna de las tres láminas `02_mapa_presentacion` está lista para inserción institucional sin edición.

Detalle por mapa en `QA_VISUAL_MAPAS_V3.csv`.

## 9. Compatibilidad editorial

El contrato existe y su SHA-256 actual coincide exactamente con el declarado: `9da6ca5e87112cdfc18a4d4cb93cdf8241abc6c17f20eb924a91df0abadd3630`. Por lo tanto, el estado real es **INCORPORADO**. La frase “al no existir contrato específico” del handoff es falsa y debe eliminarse o reemplazarse por una enumeración de brechas contra el contrato vigente.

Cumplen: GeoJSON analítico/presentación, CRS, métricas, cobertura, nombres post hoc, SHA-256, PNG/SVG y handoff. Cumplen parcialmente: QA cartográfico, privacidad, manifest y correspondencia entre áreas pre/post simplificación. No cumplen: mapa general; bbox de render por lámina; declaración explícita de fondo; tabla categoría→estilo; rótulos públicos sin códigos; separación de material técnico y publicable.

## 10. Privacidad

El CSV de asignación está sanitizado y no contiene coordenadas ni identificadores originales. Los GeoJSON territoriales no contienen establecimientos identificables. El archivo `PUNTOS_ASOCIADOS_SANITIZADOS_V3.geojson` sí contiene 1.536 coordenadas puntuales y referencias técnicas. No incluye nombres o domicilios, pero debe marcarse y separarse como insumo técnico interno; no debe integrar un paquete público o el PDF institucional.

Los SVG no muestran hallazgos de PII, credenciales, links privados o API keys. Los aparentes patrones telefónicos detectados por una búsqueda amplia correspondieron a secuencias numéricas de SVG/hashes y se descartaron manualmente.

## 11. Hallazgos y acciones

La matriz completa está en `MATRIZ_HALLAZGOS_QA_TERRITORIAL_V3.csv`.

Bloqueantes para iniciar la integración editorial directa:

1. Falta el mapa general exigido por el contrato.
2. Las láminas de presentación conservan contenido técnico y lenguaje de etapa experimental incompatibles con el uso institucional.
3. El handoff contiene una contradicción sobre la existencia del contrato.

Ningún bloqueante exige nueva corrida analítica. Las correcciones corresponden al `cartografo_territorial` y al `integrador_tecnico_editorial`, con QA independiente posterior.

## 12. Veredicto por nivel

| Nivel | Dictamen |
| --- | --- |
| Validez del resultado territorial | APTO |
| Capas analíticas | APTAS |
| Capas de presentación | APTAS COMO BASE GEOMÉTRICA; requieren ajuste editorial |
| Mapas para informe institucional | NO APTOS EN SU ESTADO ACTUAL |
| Veredicto general | `APTO_CON_AJUSTES_CARTOGRAFICOS` |

## 13. Superficies protegidas y Git

Se evaluaron los 15 patrones vigentes de `PROTECTED_SURFACES.yaml`: 476 archivos, 120.884.444 bytes. El digest agregado SHA-256 fue idéntico antes y después: `798d8e1da7673d43d16587ccb4232be3d6afc1f90dbe8a13570f6f8f9452b971`. Diferencias: 0.

`git diff --cached --name-only` estuvo vacío al inicio y al cierre. El working tree ya contenía numerosos cambios y carpetas untracked ajenos a esta tarea; las tres carpetas de la corrida auditada ya figuraban untracked antes de comenzar. Esta auditoría agregó únicamente las dos carpetas autorizadas `docs/polos_gastro/auditoria_qa_territorial_v3/` y `outputs/polos_gastro/auditoria_qa_territorial_v3/`, con nueve archivos. No se hizo staging, commit ni push.

No se modificaron archivos auditados, fuentes, baselines, evidencia, preintegración, PDFs, infraestructura ni pipeline. No se usaron APIs, Places, red, instalaciones, staging, commit o push.
