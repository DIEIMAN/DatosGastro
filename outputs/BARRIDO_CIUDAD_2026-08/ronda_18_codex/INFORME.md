# Informe técnico de actualización territorial y establecimientos

Fecha de corte: 10/08/2026.

## Qué cambió de valor

La condición cuantitativa queda expresada como dos mediciones y no como un umbral de admisión: densidad en locales por hectárea y una curva de continuidad a 20, 40, 60, 80 y 120 metros. La tabla contiene 41 referencias; San Telmo da 2,80 locales por hectárea, por lo que la cifra ya no se interpreta como un veredicto aislado. Mataderos, Núñez, Retiro y Villa Santa Rita están identificados como mediciones sobre el barrio administrativo, no sobre un borde propio. Fuente: [densidad_y_continuidad_41.csv](densidad_y_continuidad_41.csv), cálculo reproducido el 10/08/2026 sobre `base/local.csv`, con universo `anillo = nucleo` y `apto_geometria = True`.

La curva publicada para Villa Pueyrredón se reproduce exactamente con la proporción de locales incluida en la componente conexa mayor: 2,5 %, 5,6 %, 11,6 %, 15,7 % y 31,3 %. La lectura literal “locales que tienen al menos otro local cerca” produce, sobre los mismos 198 puntos, 58,6 %, 77,3 %, 82,8 %, 85,9 % y 91,9 %. Para mantener compatibilidad con el modelo comprometido, la salida usa la primera definición y la declara en cada fila. Esta diferencia semántica debe corregirse en el texto público antes de citar la curva. Fuente: validación incluida en [generar_entrega.py](generar_entrega.py), ejecutada el 10/08/2026.

## 1. Densidad y continuidad

La superficie se calculó en EPSG:5347 y la densidad divide los locales del universo canónico por hectáreas del soporte. La continuidad arma un grafo distinto para cada distancia y divide el tamaño de su componente mayor por el total de locales del soporte. No se redondearon insumos; el archivo publica densidad con dos decimales y porcentajes con uno. Fuente y fecha: [generar_entrega.py](generar_entrega.py) y [soportes_41_usados.geojson](soportes_41_usados.geojson), 10/08/2026.

Los 37 bordes propios y los cuatro soportes administrativos quedan trazables en la columna `fuente_geometria`. La tabla no reemplaza el criterio de admisión y no compara la cifra administrativa de un barrio con la de un perímetro específico como si fueran objetos equivalentes. Fuente y fecha: [densidad_y_continuidad_41.csv](densidad_y_continuidad_41.csv), 10/08/2026.

## 2. Capa de establecimientos con reconocimiento

La capa conserva 215 entidades. Se normalizaron 33 nombres y 17 direcciones; cada cambio conserva `nombre_original` o `direccion_original`. La transformación es idempotente: una segunda ejecución no altera los originales. Fuente y fecha: [hitos_capa_2026.geojson](../hitos/hitos_capa_2026.geojson) y prueba automatizada del 10/08/2026.

Con tolerancia fija de 3 metros al borde quedaron 60 entidades fuera de todo soporte. Dos casos adicionales, a 0,2 y 2,3 metros, se trataron como contacto de borde y se publican por separado. Para ordenar la revisión —no para declarar un hecho territorial— se fijó antes del cálculo un corte de 250 metros: 41 casos quedan como posible borde incompleto y 19 como esperables en zonas sin referencia. La sensibilidad es 30/30 a 100 metros, 41/19 a 250 y 48/12 a 500. Fuente y fecha: [hitos_fuera_de_todo_polo.csv](hitos_fuera_de_todo_polo.csv), [hitos_contacto_borde_tolerancia.csv](hitos_contacto_borde_tolerancia.csv) y [hitos_fuera_sensibilidad.csv](hitos_fuera_sensibilidad.csv), 10/08/2026.

Ese inventario reproduce el cruce que originó los 60 casos usando la instantánea de soportes previa al cierre geométrico que se está produciendo en paralelo. No se mezclaron geometrías de una etapa todavía abierta. Cuando ese cierre se incorpore como fuente vigente única, corresponde volver a ejecutar distancias y clasificaciones; la tabla actual conserva valor como lista de auditoría del hallazgo recibido. Fuente y fecha: `geometria/soportes_41.geojson`, instantánea recibida y procesada el 10/08/2026.

Se revisaron los cinco conflictos cargados en la capa y el caso Marte, que no integra las 215 entidades. El Fortín y Banchero quedaron resueltos; Marte quedó resuelto en Crisólogo Larralde 2772 mediante una pieza individual del 29/05/2026. La Mezzetta, San Carlos y Saverio conservan el domicilio adoptado y declaran expresamente la discrepancia pendiente. Cada fila incluye fuentes públicas y fecha de revisión. Fuente: [conflictos_direccion.csv](conflictos_direccion.csv), 10/08/2026; para Marte, [pieza periodística del 29/05/2026](https://www.lanacion.com.ar/sabado/el-polo-gourmet-que-crece-en-la-frontera-norte-de-la-ciudad-nid29052026/).

## 3. Locales mencionados fuera de los catálogos

Se publicaron 37 filas: 23 para Flores y el pasaje, 3 para Parque Avellaneda, 5 para Donado–Holmberg y 6 para Villa Luro. El resultado es deliberadamente prudente: 7 acreditan atención a la fecha de su fuente, 6 quedan como probablemente abiertos, 19 acreditan existencia pero no vigencia, 3 presentan conflictos y 2 no pueden individualizarse. Ninguna etiqueta de apertura de un agregador se usó como verificación y la falta de evidencia no se convirtió en cierre. Fuente y fecha: [verificacion_locales_sin_catalogo.csv](verificacion_locales_sin_catalogo.csv), consultas públicas cerradas el 10/08/2026.

La nota sobre el pasaje acredita diez locales en junio de 2023 y la cobertura posterior permite actualizar parte del conjunto. Yugane alcanza v3 por participación operativa en una promoción pública de junio de 2026; Shabu Shabu 153 queda en conflicto porque dos fuentes secundarias discrepan. Fuente: [nota del 19/06/2023](https://www.lanacion.com.ar/sabado/pasaje-ruperto-godoy-el-patio-de-comidas-coreano-del-shopping-a-cielo-abierto-que-se-creo-alrededor-nid15062023/) y detalle fila por fila en el CSV, consulta al 10/08/2026.

El padrón oficial de 2015 permite identificar diez establecimientos gastronómicos o de abastecimiento en Flores. El texto vigente afirma doce sin nombrar los dos restantes; por eso se conservaron dos filas no individualizadas y no se inventaron nombres ni domicilios. Fuente: [padrón oficial de 2015](https://turismo.buenosaires.gob.ar/sites/turismo/files/establecimientos_KOSHER_2015_0.pdf), revisado el 10/08/2026.

En Parque Avellaneda, las tres existencias quedan documentadas por una guía de 2025; La Barra del Parque conserva conflicto de vigencia por una señal posterior de cierre que no es concluyente por sí sola. Fuente: [guía pública consultada el 10/08/2026](https://www.timeout.com/es/buenos-aires/que-hacer-parque-avellaneda-viejo-mercado-yiyo-el-zeneize-olivera) y detalle en el CSV.

En Donado–Holmberg, Cigaló alcanza v3 por participación operativa pública en mayo de 2026. Chicama queda en conflicto: una fuente informa mudanza desde Donado 1995 y otra publicación posterior conserva esa dirección. En Villa Luro, Alma y Fuego y Casa Tónica tienen señales fechadas de 2026; los otros cuatro locales sólo conservan existencia acreditada o no tienen una pieza posterior suficiente. Fuente y fechas: enlaces individualizados en [verificacion_locales_sin_catalogo.csv](verificacion_locales_sin_catalogo.csv), corte 10/08/2026.

## 4. Establecimientos históricos priorizados

El archivo heredado contiene 61 filas v1, aunque un párrafo de cierre anterior hablaba de 63. La priorización se rehízo sobre las 61 filas efectivas: primero las que caen dentro de una referencia y sostienen la condición de historia, ordenadas por la cantidad total de hitos reconocidos en ese soporte; después, las que quedan fuera. Fuente y fecha: [vigencia_historicos_priorizados.csv](vigencia_historicos_priorizados.csv) y archivo heredado `vigencia_90_hitos.csv`, auditados el 10/08/2026.

Siete de las 61 filas mejoraron: dos pasan a v3 y cinco a v2. Las primeras posiciones corresponden a soportes con uno, dos o tres hitos, donde una sola entidad pesa especialmente. Las 54 restantes conservan v1 y la indicación `pendiente_pieza_individual_fechada`; no se las promovió por una ficha sin fecha ni por el estado de un agregador. Fuente y fecha: [vigencia_historicos_priorizados.csv](vigencia_historicos_priorizados.csv), 10/08/2026.

## Pendientes explícitos

- Corregir en el texto público la definición verbal de continuidad: la curva modelo es componente conexa mayor y no proporción con cualquier vecino. Fuente: validación reproducible del 10/08/2026 en [generar_entrega.py](generar_entrega.py).
- Revisar territorialmente los 41 casos situados a 250 metros o menos de un borde. Esa etiqueta es una prioridad de inspección, no prueba de que el borde esté incompleto. Fuente: [hitos_fuera_de_todo_polo.csv](hitos_fuera_de_todo_polo.csv), 10/08/2026.
- Recalcular el inventario de distancias cuando se incorpore el cierre geométrico producido en paralelo; hasta entonces, los 60 casos pertenecen a la instantánea que originó el pedido. Fuente: `geometria/soportes_41.geojson`, procesada el 10/08/2026.
- Resolver con una fuente adicional las discrepancias de La Mezzetta, San Carlos y Saverio. Fuente: [conflictos_direccion.csv](conflictos_direccion.csv), revisión del 10/08/2026.
- Identificar los dos registros kosher que el texto cuenta pero no nombra; el padrón oficial legible permite reconstruir diez. Fuente: padrón de 2015, revisado el 10/08/2026.
- Resolver los tres conflictos de vigencia o domicilio y buscar piezas nuevas para los 19 locales cuya vigencia no se acreditó. Fuente: [verificacion_locales_sin_catalogo.csv](verificacion_locales_sin_catalogo.csv), corte 10/08/2026.
- Conseguir una pieza pública individual fechada para los 54 establecimientos históricos que siguen en v1. Fuente: [vigencia_historicos_priorizados.csv](vigencia_historicos_priorizados.csv), 10/08/2026.

## Integridad y privacidad

No se modificaron datos crudos, credenciales, fuentes originales de locales ni el pipeline general. La única capa existente editada fue `hitos_capa_2026.geojson`, por pedido explícito, y conserva los valores anteriores. No se versionaron teléfonos, correos, identificadores personales ni claves. Las fuentes comerciales privadas no se consultaron y los agregadores sólo se usaron como señales fechadas o como conflicto declarado, nunca como prueba autónoma de apertura. Control ejecutado el 10/08/2026.
