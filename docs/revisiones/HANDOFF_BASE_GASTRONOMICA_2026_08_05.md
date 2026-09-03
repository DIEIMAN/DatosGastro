# HANDOFF · La base gastronómica de la Ciudad · 2026-08-05 (segunda mitad del día)

Continúa `HANDOFF_BARRIDO_CIUDAD_2026_08_05.md`, que sigue vigente en todo lo que no se
contradiga acá. Rama `mercados-gastronomicos-v2`. **Sin commit.**

**El objetivo de la etapa cambió, y hacia arriba.** Ya no es medir si Places sirve para contar:
es **construir una BASE de la gastronomía de la Ciudad apoyada en todas las bases que existen**,
para que mañana se pueda trabajar mejor desde la Dirección y desde afuera. El Atlas pasa a ser un
producto **derivado** de esa base. Y el entregable final sigue siendo el mapa de polos
poligonizados de toda la Ciudad: la base es el medio.

---

## Lo que cambió el tablero, en una línea

**Places dejó de ser la columna vertebral, y está medido.** De los 81 puntos que Places trajo de
Villa Crespo, **Overture sola empareja 73 (90,1 %)** y la unión de las tres fuentes abiertas
empareja 74 (91,4 %). **Sólo 4 de 81 quedan sin identidad publicable.** El barrido de los 48
barrios compraría, sobre lo que ya hay, un descubrimiento marginal que además no se puede publicar.

---

## Estado

| paso | estado |
|---|---|
| **OSM (E05)** · Overpass, 33 consultas, capa por barrio | **HECHO.** 6.427 POI núcleo · 0,94× el padrón |
| **Overture (E06)** · GeoParquet en S3 con DuckDB | **HECHO.** 11.921 POI núcleo · **1,74× el padrón** |
| **All The Places (E07)** · corrida semanal completa | **HECHO.** 282 POI núcleo · sólo cadenas |
| **Foursquare** | **BLOQUEADA.** Cerró el acceso anónimo; ver abajo |
| **Seis datasets nuevos del GCBA** | **HECHO y perfilado.** Dos no traen las coordenadas que la ficha declara |
| **Barrido del catálogo de BA Data por API CKAN** | **HECHO.** 453 datasets, 241 georreferenciables |
| **Rescate: qué de Places se puede publicar** | **HECHO, 0 requests. 91,4 % rescatable** |
| **Solape entre fuentes en toda la Ciudad** | **HECHO, 0 requests** |
| **Esquema implementado: `local` + `local_fuente`** | **HECHO.** 27.729 locales · 5 de 5 controles en verde |
| **Cotejo de las 22 zonas contra la base** | **HECHO**, con las bandas escritas antes de correr |
| **Reescritura editorial: nombrar a Google** | **APLICADA.** La técnica reproduce su sellado con 0 diferencias |
| **Google Places** | **NO SE CORRIÓ. 0 requests.** Sigue en 306 en agosto |

---

## Las fuentes nuevas, y qué aporta cada una

| fuente | núcleo en la Ciudad | ÷ padrón | licencia | costo |
|---|---:|---:|---|---|
| **Overture Maps** (E06) | **11.921** | **1,74** | CDLA-Permissive-2.0 | 0 |
| Relevamiento de Usos del Suelo | 9.108 parcelas | 1,33 | CC-BY-2.5-AR | 0 |
| Padrón de habilitaciones (F02) | 6.861 direcciones | 1,00 | CC-BY-2.5-AR | 0 |
| OpenStreetMap (E05) | 6.427 | 0,94 | **ODbL** | 0 |
| All The Places (E07) | 282 | 0,04 | CC0 1.0 | 0 |

Las tres unidades son distintas —dirección, parcela, POI— y por eso las razones se leen como
factor de captura entre fuentes, nunca como corrección de una sobre otra.

### Overture es el hallazgo de la jornada

Es la primera fuente que supera al padrón, **es redistribuible con nombre y dirección**, cubre
mucho más parejo que Places (razón por barrio de 0,82 a 4,97, mediana 1,52, contra el 12 % de
Places) y sale gratis. El 97,6 % de sus POI gastronómicos trae dirección y el 100 % trae nombre.

**Y su composición corrige un supuesto del esquema.** El §3 advierte que Overture, Foursquare y
All The Places no son tres fuentes independientes. Es cierto, pero en la Ciudad el reparto es otro:

```
meta          108.946      Foursquare      4.046
Microsoft       1.521      AllThePlaces      522
PinMeTo             4      OSM                 0
```

Tres consecuencias: **Overture y OSM sí son independientes acá** (OSM no aporta un solo registro),
**bajar Foursquare por separado agregaría poco** (3,3 %), y la prudencia del esquema —contarlas
como un grupo— se mantiene, ahora sabiendo que cuesta casi nada.

### Foursquare quedó afuera, y no es grave

Cerró el acceso anónimo por S3: ahora se entrega por un portal propio con catálogo Iceberg y token
de cuenta, y el espejo de Hugging Face responde 401 porque el dataset está restringido. **Abrir una
cuenta es una decisión que no toma el repositorio.** El costo de no tenerla está medido: aporta el
3,3 % de Overture, ya viaja adentro, y seguiría contando como el mismo grupo de independencia.

---

## El número que decide el barrido de Places

`scripts/barrido_ciudad/cruzar_fuentes_abiertas.py`, cero requests, sobre los 81 puntos núcleo que
Places trajo de Villa Crespo el 5 de agosto:

| fuente abierta | empareja | % | criterios |
|---|---:|---:|---|
| **Overture** | **73** | **90,1** | 54 por dirección exacta, 16 por proximidad, 3 por proximidad y nombre |
| OSM | 51 | 63,0 | 15 por dirección exacta |
| All The Places | 1 | 1,2 | — |
| **unión de las tres** | **74** | **91,4** | |
| padrón (referencia) | 43 | 53,1 | |
| **sólo en Places** | **4** | **4,9** | |

Estable entre 20 y 100 m de radio de emparejamiento: el resultado no depende del corte.

**Traducido al esquema (§6):** 77 de los 81 pueden entrar como `abierto`, con nombre y dirección
tomados de la fuente abierta que los corrobora. 4 quedarían en `agregado`. Ése es el precio real de
la restricción de Google, medido en vez de supuesto.

### Solape entre fuentes en toda la Ciudad

Porcentaje de la fuente de la fila que encuentra pareja en la de la columna (no es simétrico):

| | OSM | OVERTURE | ATP | PADRÓN |
|---|---:|---:|---:|---:|
| **OSM** | 100,0 | 83,5 | 4,6 | 60,9 |
| **OVERTURE** | 64,5 | 100,0 | 5,3 | 58,0 |
| **ATP** | 67,2 | 86,4 | 100,0 | 40,9 |
| **PADRÓN** | 62,7 | 77,2 | 3,1 | 100,0 |

El complemento a 100 de cada fila es lo que esa fuente aporta y ninguna otra tiene. Ninguna
sobrepasa el 86 % contra otra: **cruzarlas agrega cobertura, no redundancia.**

---

## La base, implementada

`scripts/barrido_ciudad/build_base_gastronomica.py` · salida en `outputs/BARRIDO_CIUDAD_2026-08/base/`

- **27.727 locales** desde 42.342 registros de siete fuentes. Google Places **no está cargado**.
- **99,0 % aptos para el dibujo.** Los 288 no aptos son locales cuyas fuentes discrepan por más de
  40 m: ese punto no puede decidir la forma de un polígono.
- Corroboración: 81,4 % aparece en un solo grupo de independencia, 18,6 % en dos o más.
- Publicación: 50,3 % `abierto`, 49,7 % `punto`. Los `punto` son en su mayoría parcelas del
  Relevamiento, que dicen dónde hay uso gastronómico pero no cómo se llama el local.
- **5 de 5 controles del §8 en verde**, y la corrida **aborta sin escribir** si alguno falla.
- **`--check` corrido y verificado**: la base reproduce su referencia congelada, 48 barrios × 5
  columnas idénticas. La referencia es `base_referencia_agregada.csv`, el agregado por barrio —se
  congela el agregado y no las tablas completas porque `local.csv` lleva nombres y direcciones de
  terceros y no se versiona: una referencia sobre él sería un control que nadie puede correr en
  otra máquina.

Documentación de uso y advertencias: `outputs/BARRIDO_CIUDAD_2026-08/README_BASE_GASTRONOMICA.md`.

### Cuatro decisiones de diseño que conviene no perder

1. **La proximidad sola NO fusiona.** Fusionan `smp`, `usig_exacta` y `proximidad_y_nombre`. Los
   pares que sólo tienen cercanía van a `pares_pendientes_de_revision.csv`. La fusión es
   transitiva: sobre una avenida, una cadena de vecinos a menos de 40 m uno del otro terminaría
   siendo **un solo local de doscientos registros**, el total bajaría sin que nada avise y el mapa
   quedaría arruinado.
2. **`n_fuentes` cuenta grupos de independencia**, no fuentes. Máximo observado: 5 grupos.
3. **`frescura` nunca es «abierto»**, y nunca es futura. Un permiso que vence en 2031 no es
   evidencia de 2031: la fecha de evidencia es la de la disposición. Se corrigió al detectarlo.
4. **Banda de borde de 50 m.** Un punto puede caer unos metros afuera del polígono de su barrio por
   error de geocodificación. Los 50 m no son a ojo: del lado de afuera hay 11 puntos a menos de
   50 m y después un salto a mediana 1,3 km. El corte cae en el hueco. Los 26 de All The Places que
   quedaron afuera son de Vicente López y Avellaneda, y se declaran.

---

## Los seis datasets del GCBA, y un aviso de método

Bajados y perfilados en `scripts/barrido_ciudad/bajar_fuentes_gcba.py`:

| fuente | filas | ubicación | qué aporta |
|---|---:|---|---|
| Permisos de área gastronómica | 509 | dirección | **135 vigentes hoy, con fecha de vencimiento** |
| Venta de alimentos en espacio público | 71 | sólo barrio | puestos y food trucks; 59 vigentes |
| Locales bailables | 321 | punto | nocturnidad, con capacidad y estado |
| Espacios culturales | 3.031 | punto | la subcategoría bares, con programación |
| Comercios con beneficios a ciclistas | 107 | punto | chico, con nombre y dirección abiertos |
| Calzada gastronómica (decks) | 23.304 tramos | tramo | **no estaba en la lista**; lo encontró el barrido CKAN |

**Los permisos aportan lo único que ninguna otra fuente tiene: una afirmación de vigencia con fecha
por delante.** 332 de los 509 engancharon por dirección a un local de la base; los 177 restantes no
crean local, porque sin punto no pueden dibujar.

### El aviso, y vale para todo el método

**La ficha de CKAN de los dos padrones de permisos declara columnas de coordenada que los archivos
publicados hoy no traen.** El gastronómico trae `Dirección` y `Altura` —geocodificable con USIG—;
el de alimentos trae un topónimo (`COSTANERA SUR`) y el barrio, y no se puede llevar a un punto.

No es un defecto de esas dos fuentes: el barrido del catálogo lee `attributesDescription`, que es
**metadato declarado, no el archivo**. Sirve para ordenar 453 datasets y decidir cuáles abrir; no
sirve para afirmar que un dataset tiene coordenadas. Eso se comprueba abriéndolo.

Y una trampa de unidad que costó encontrar: el «registro histórico acumulado» de locales bailables
son **54.771 filas que son 321 locales**, repetidos una vez por período. Sin colapsar, Palermo daba
14.080 locales bailables. Se nota en Palermo; no se habría notado en un barrio chico.

---

## El cotejo de las 22 zonas · 13 de 17 en banda

`scripts/barrido_ciudad/cotejar_22_zonas_base.py`. Las cifras publicadas se recalculan desde la
base recortando por las envolventes editoriales, con la precedencia que evita el doble conteo.
**Ninguna cifra publicada se toca.** Las bandas están escritas en el código **antes** de correr.

| familia de método | zonas | razón base ÷ publicada | en banda |
|---|---:|---|---:|
| relevamiento propio | 4 | 0,57 – 1,29 (med. 0,78) | 3 de 4 |
| directorio comercial (Places) | 4 | 2,83 – 3,60 (med. 3,09) | **4 de 4** |
| mínimo relevado | 7 | 0,48 – 1,52 (med. 1,20) | 4 de 7 |
| relevamiento anterior | 2 | 0,51 – 0,93 | 2 de 2 |

**Lo que el cotejo prueba es que la diferencia tiene explicación por familia de método**, que era
la condición para que las dos cifras convivan sin que una envejezca mal. Y confirma de otra manera
el hallazgo del día: las cuatro zonas cuya cifra salió sólo de Places son las cuatro donde la base
la supera tres veces.

### Las cuatro que quedaron fuera de banda, y ninguna se acomodó

- **R08 Villa Crespo · publicada 646, base 836 (1,29).** Es la zona mejor calibrada que hay y la
  única del grupo donde la base **supera** un conteo de campo. Hay que mirarlo: o el conteo a pie
  de julio se quedó corto, o la base está fusionando de menos y cuenta dos veces algún local. **Es
  el mejor caso de prueba que existe para auditar la regla de fusión**, porque hay un número
  independiente contra el cual medirse. No se tocó nada; queda anotado.
- **R18 Esmeralda–Paraguay (0,48), R19 Federico Lacroze (0,89), R21 La Paternal (0,82).** Tres
  zonas donde la base queda por debajo de una cifra declarada como **mínimo**. Un mínimo que la
  base no alcanza es una señal de que a la base le falta cobertura ahí, no de que el mínimo esté
  mal. Son candidatas naturales para la primera tanda de Places, si se corre.

Las cinco zonas «sin conteo propio» —Palermo, Corrientes, San Telmo, Puerto Madero, Recoleta— no se
pueden cotejar, pero **la base sí las cuenta**: 1.380, 362, 72, 363 y 728 locales. Es información
que el Atlas no tenía.

Y falta una pieza para cerrarlo: la base todavía no tiene Places, y las zonas cuya cifra publicada
salió de Places son justamente las que más se van a mover. Ese cotejo se repite después de la
primera tanda, no antes.

---

## La reescritura editorial, aplicada

Decisión de Diego: se dice que la fuente es Google Places, aclarando que es información de Google.

**Aplicada en dos lugares:**

1. `contenido_conduccion.py` — los cuatro grupos pasan a nombrarse por **cuántas fuentes se
   cruzaron**, más el párrafo nuevo del cierre sobre el límite de las dos fuentes. Contesta los
   comentarios `[c]` y `[d]` de Patricia.
2. `build_atlas_v2.py` — las reglas de sustitución que ocultaban la fuente.

**El cuidado 2 que pediste era correcto y era el problema real: las sustituciones ESTABAN
compartidas con la edición técnica.** `sanitize_public_text` corre para las dos y no distinguía
cuál. Sacarlas habría cambiado la técnica, que está sellada. Ahora van por edición
(`FRASES_POR_EDICION` y `ORIGENES_POR_EDICION`) y la técnica conserva palabra por palabra lo que
decía.

**Verificado, no afirmado:** se reconstruyó el contenido público de las dos ediciones desde el
canon y se comparó contra sus JSON congelados.

- **técnica: 693 campos, 0 diferencias.**
- conducción: 701 campos, **17 diferencias, todas de nombre de fuente**. Ninguna cifra se movió.

Dos cosas más:

- **El pasaje 5 —«Cómo se construyeron las zonas»— NO se aplicó.** Está declarado como texto
  entregado por la Dirección y Patricia lo dejó abierto. La redacción propuesta quedó escrita en
  `build_atlas_docx.py` como `PRIMER_PASO_PROPUESTO`, sin enganchar a nada, lista para el visto.
- **Ningún PDF se regeneró.** El Atlas publicado y la edición técnica V2.1 siguen sellados; los
  cambios están en el generador y se materializan en la próxima corrida, que es una decisión aparte.

Encontrado al aplicarlo: `deduplicación` y `capas administrativas` están en la lista de términos
prohibidos de la conducción, así que las frases que los usaban se dicen en castellano llano.
Reemplazar un eufemismo por otro término vigilado habría hecho fallar el control de vocabulario.

**Queda un cabo suelto, anotado y no perseguido:** el código interno `E-PLACES` sigue apareciendo
crudo en el `denominador_metodo` de cuatro fichas. Es anterior a este cambio y no estaba en los
siete pasajes; conviene resolverlo con Diego antes de agregar una regla más.

---

## Lo que espera decisión o acción

1. **Correr o no la primera tanda de Places, y de qué tamaño.** La medición cambió la respuesta que
   estaba escrita ayer: Overture rescata el 90 % de lo que Places descubre y lo hace publicable. La
   recomendación es **reducir drásticamente el alcance**: en vez de los 48 barrios, una tanda chica
   sobre los barrios donde las fuentes abiertas estén más flacas, para medir si ahí el rescate
   también es del 90 % o cae. Sin ese dato, el barrido completo compra descubrimiento marginal no
   publicable.

   **Y el cotejo dejó los candidatos elegidos:** R18 Esmeralda–Paraguay, R19 Federico Lacroze y
   R21 La Paternal son las tres zonas donde la base no llega a una cifra declarada como mínimo. Si
   Places aporta en algún lado, es ahí. Con la grilla actual son unos pocos cientos de requests
   sobre los 4.694 disponibles del mes, y el dry-run va antes de pedir autorización.
2. **La cláusula de compartir-igual de la ODbL de OSM.** Está escrita en el README de la base, como
   pediste. **Antes de publicar cualquier capa abierta tiene que revisarla el área legal de la
   Dirección.** Hay salida técnica si complica: la base funciona sin OSM —Overture aporta casi el
   doble y es permisiva— y el generador guarda la procedencia registro por registro para poder
   construir una capa sin ODbL sin rehacer nada.
3. **Abrir o no cuenta en el portal de Foursquare.** Cuesta poco no tenerla (3,3 % de Overture).
4. **El visto de Patricia sobre el pasaje 5.**
5. **Regenerar o no los PDF del Atlas** con la reescritura aplicada.
6. **Mandar la nota a la AGC** — sigue pendiente del handoff anterior.

---

## Trampas encontradas hoy, para no repetirlas

- **Overpass no sirve la Ciudad en una sola consulta.** Los tres espejos devuelven 504, y el
  `out count` pasa igual: lo que ahoga al servidor no es la búsqueda sino armar la respuesta con
  geometría. Tag por tag entra cómoda y además deja la descarga reanudable, que es lo que
  corresponde con una infraestructura donada.
- **El rectángulo de la Ciudad no es la Ciudad.** El bbox entra en La Tablada, Avellaneda y Vicente
  López: el 10,8 % de lo que Overture devuelve en ese rectángulo cae afuera. El recorte fino es
  punto en polígono y va después del filtro barato que la consulta empuja al servidor.
- **`itertuples()` renombra las columnas que empiezan con guion bajo.** `sjoin_nearest` con
  `distance_col="_metros"` produce un campo que después no existe con ese nombre.
- **`sjoin` deja `index_right` pegado** y el siguiente `sjoin` falla. Se limpia en el que empareja,
  no en cada cargador.
- **Filtrar una tabla por una máscara y hacer `dropna()` por otro lado da largos distintos** en
  cuanto una fila tenga sólo una de las dos coordenadas. La máscara se calcula una vez y se aplica
  a las tres series.
- **Mover una regla de sustitución de lugar cambia la salida sin cambiar la lista de reglas.** El
  orden de `PLAIN_LANGUAGE` es significativo: las frases compuestas tienen que correr antes de las
  reglas generales. Comparar listas de reglas no prueba nada; hay que comparar salidas.
- **All The Places son 30,6 GB descomprimidos en 4.898 archivos.** Se recorre línea por línea con
  un filtro de bytes —una línea sin `-58.` no puede ser un punto de la Ciudad— y sólo las
  candidatas se parsean como JSON.
- **Indexar un GeoDataFrame por posición dentro de un bucle de 262.000 pares convierte una corrida
  de dos minutos en una de media hora.** Se pasan las columnas a listas y arrays antes del bucle.
  Lo mismo con la sensibilidad al radio: clasificar los pares una sola vez hasta el radio máximo y
  filtrar por distancia da el mismo resultado que tres pasadas y cuesta un tercio.
- **Emparejar por la primera palabra del método mezclaba familias opuestas.** «relevamiento
  propio» y «relevamiento anterior» empiezan igual: una es un conteo de campo y la otra una cifra
  de otra añada. Dos zonas quedaban evaluadas contra la banda equivocada.

---

## Privacidad

Cuatro de los datasets nuevos traen `titular`, `DNI_CUIT`, `nro_documento`, `TELEFONO`, `MAIL`.
**Ninguna de esas columnas se abrió**: cada fuente declara su lista permitida y el `usecols` se
arma desde ahí. Hay un control que corta la corrida si una columna prohibida aparece en una salida.

De OSM se descartan `user`, `uid` y `changeset` **antes de que nada toque el disco**, incluido el
crudo: son datos personales de quien mapeó. Se conservan `timestamp` y `version`, que son la fecha
de corte y no identifican a nadie.

---

## Lo que no se tocó

Ninguna cifra publicada del Atlas. Ningún PDF regenerado. El pipeline público F01-F05. La
referencia congelada de `build_capa_homogenea.py --check`. Las superficies de
`PROTECTED_SURFACES.yaml`. La nota a la AGC sigue preparada y sin mandar.

**Google Places: 0 requests hoy.** El total de agosto sigue siendo 306 de la franja de 5.000.

**Dependencia nueva:** se instaló `duckdb` en el `.venv`. Sólo lo necesita
`bajar_overture_places.py`; el resto de la cadena corre sin él.

**Sin commit.**
