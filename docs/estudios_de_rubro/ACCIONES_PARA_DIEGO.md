# Lo que suma y depende de vos — actualizado 2026-08-28

Cosas que no puedo resolver desde el repo y que cambian la calidad de todos los estudios
de rubro, no la de uno. Ordenadas por cuánto mueven la aguja.

## 1. Conseguir habilitaciones posteriores a 2024 (bloqueante para "actualidad")

**Diagnóstico cerrado el 2026-08-27.** El portal sí publica recursos rotulados `2025` y
`2026`, pero los dos contienen un padrón histórico con disposiciones 2014-2020. El recurso
2026 es casi idéntico al 2025 y no aporta altas de 2025 ni de 2026. Incorporarlo como otro
año duplicaría establecimientos.

Por lo tanto, no falta descubrir ni descargar un archivo público: hace falta pedir a AGC
una serie anual correcta o un extracto operativo con fecha de alta, baja o vigencia para
2025-2026. El pedido debe mencionar expresamente la inconsistencia entre el nombre y el
contenido de los recursos públicos, para evitar una respuesta que sólo remita al portal.

Hasta recibir esa fuente, **F02 se usa como antecedente administrativo** y la actualidad se
resuelve con señales operativas separadas. No se interpretan las fechas de publicación de
los recursos como fechas de los datos.

## 2. Decidir si se regenera casas de pastas

Con el lector arreglado, el universo A del padrón oficial pasa de 10 a **159**
(reconfirmado el 2026-08-28 corriendo el build a una carpeta aparte).

**Precisión sobre el entregable**, porque la versión anterior de esta nota decía mal que el
informe publicaba 10: el informe y el PDF publican **254**, que es un padrón candidato
integrado (OSM + Google + revisión manual + AGC). Lo que está mal ahí es una fila de la
tabla de fuentes de la sección 2: dice que el registro oficial aporta **11** candidatos, y
con el lector arreglado aporta ~159. El total de 254 no es falso, pero está subestimado:
de las 153 filas geolocalizadas del padrón corregido, **97 no tienen correspondencia** en
el integrado (medido por proximidad, estable entre 25 y 75 m), así que el orden de magnitud
del entregable rehecho es **~350**, no 254.

No toqué el informe ni el PDF. Las opciones son regenerar y rehacer el entregable, o
dejarlo con una nota de corrección. Detalle y método del cruce en
`COMPARACION_PANADERIAS_CASAS_DE_PASTAS.md`.

**F1 ya está** (2026-08-28): contar por habilitación y no por inmueble vive en el módulo
compartido, así que pastas lo hereda y se puede regenerar cuando digas. Ojo con esto: el
159 sale de agrupar por partida, y con la clave nueva el número se mueve otra vez. Hay que
volver a sacarlo antes de publicarlo. Ver `COMPARACION_PANADERIAS_CASAS_DE_PASTAS.md`.

## 3. Geocodificación de las direcciones que faltan — HECHO (2026-08-27, tarde)

Corrida de USIG ejecutada. El universo A de panaderías pasó de 65,4 % a **99,1 %**
geolocalizado (1.165 de 1.176, hoy 1.203 de 1.219) y casas de pastas se benefició de
rebote por compartir la
caché (96,2 %).

Los puntos vienen marcados `sin_control_comuna`, así que se controlaron aparte
(`outputs/panaderias/analisis/d8_qa_geocodificacion.csv`): **0 puntos fuera del polígono de
CABA** sobre 1.632, y de los 118 casos con comuna declarada en la fuente **116 coinciden**.
Las 2 que discrepan están listadas; una tiene la firma de una calle homónima y conviene
mirarla a mano.

Quedan 34 direcciones únicas sin resolver, de las cuales **29 no tienen altura** (esquinas,
S/N): USIG no las resuelve solas y necesitan criterio humano. No es una corrida más, es una
lista corta para mirar.

Pendiente menor: correr lo mismo apuntado a casas de pastas cerraría sus 25 casos restantes.

## 4. Población por comuna y por barrio

La columna `panaderias_por_10000_hab` existe y sale **vacía** en todas las salidas: no hay
tabla de población en el proyecto. Con el censo 2022 por comuna y por barrio cargado una
sola vez, todos los estudios de rubro ganan el per cápita, que es la cifra que una jefatura
suele pedir primero. Es un CSV chico y de una vez.

## 5. Diccionario de códigos de rubro de la AGC

Hoy la clasificación se hace por el **texto** del rubro, que cambia de nomenclatura entre
años (2023 ya usa códigos tipo `1.4.2`). Con la tabla oficial código → descripción, la
clasificación pasa a ser por código: más estable, auditable y discutible con la AGC en sus
propios términos. Si la conseguís, la incorporo al módulo compartido.

## 6. Revisión humana de los casos de frontera

Panaderías dejó **559** registros marcados `requiere_revision_manual` (eran 898 antes de la
geocodificación, que resolvió la causa más numerosa). No es trabajo de máquina: es mirar una
lista. Si querés, la parto en tandas por comuna; el formato ya trae el motivo de cada caso,
así que se revisa sin abrir el crudo.

Hay además una lista más corta y más jugosa: los **81 domicilios** de
`outputs/panaderias/analisis/d9_renovaciones_candidatas.csv`, donde conviven dos
habilitaciones con el mismo rubro. Decidir si son dos panaderías pegadas o una sola
habilitada dos veces mueve hasta 83 establecimientos del universo A.

**Conviene esperar a F2** de `docs/panaderias/PLAN_DE_TRABAJO.md`, que cambia qué casos
quedan marcados. F1 ya está hecho.

## 6 bis. Decidir qué cifra de panaderías se publica

Del mismo padrón salen varios números. Hoy la cifra es **1.219**, contando por habilitación
—que ya está hecho, y que no dio los 1.280 anticipados porque el padrón 2025 republica
trámites viejos que se contaban dos veces—. La cota inferior es **1.136**, si las 83
renovaciones candidatas fueran todas el mismo local. Y falta descontar el pan que está
dentro de un supermercado o un kiosco (F2), que baja el número otra vez. Miden cosas
distintas y no se promedian: hay que elegir una y decir cuál es.

La medición está en `outputs/panaderias/analisis/HALLAZGOS_DIAGNOSTICO.md`. Esto bloquea
cualquier informe de panaderías.

## 7. Qué rubro sigue

La receta está escrita (`COMO_ABRIR_UN_RUBRO_NUEVO.md`) y el lector es compartido, así que
el próximo rubro arranca directamente por la definición de alcance. Lo que necesito de vos
para empezar es una sola cosa: **qué entra y qué no**, por escrito. Para pizzerías, por
ejemplo, la pregunta que decide el tamaño del universo es si entran las que sólo venden
por delivery y las que son pizza al paso dentro de otro rubro habilitado.
