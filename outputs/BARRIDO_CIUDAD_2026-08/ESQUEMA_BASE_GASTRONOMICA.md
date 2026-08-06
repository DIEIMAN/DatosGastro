# Esquema de la base gastronómica de la Ciudad

**Diseño · 5 de agosto de 2026**
Es el insumo que bloquea la escritura de código. Define el modelo de registro, la procedencia,
el identificador, la vigencia, la aptitud geométrica y las reglas de publicación.

---

## 0 · El objetivo manda

**La base no es el entregable. El entregable sigue siendo el mapa de polos poligonizados a lo
largo y ancho de la Ciudad.** La base existe para que esos polígonos se puedan dibujar y
defender.

Eso decide tres cosas que un diseño genérico haría distinto:

1. **La calidad del punto pesa más que el nombre del local.** Un punto corrido 30 metros cambia
   la forma de un cluster. Un nombre mal escrito no.
2. **La cobertura pareja vale más que la completitud.** Una base con 12 % de captura uniforme en
   toda la Ciudad dibuja mejores polígonos que una con 80 % en Palermo y 5 % en Lugano. Lo
   segundo produce polos donde sólo hubo más consultas.
3. **No todo punto puede dibujar.** El Atlas ya tropezó con esto: ocho referencias sin puntos
   terminaron con envolventes derivadas de la geometría de consulta y no de la oferta. Se
   previene con un campo, no con cuidado.

---

## 1 · Dos tablas, y la separación es lo importante

### `local` — la entidad resuelta

Una fila por local. Es lo que el clustering consume.

| campo | qué es |
|---|---|
| `local_id` | identificador propio y estable. Ver §2 |
| `lon`, `lat` | punto de consenso. Ver §5 |
| `smp` | clave catastral (sección-manzana-parcela) cuando se pudo resolver |
| `direccion_norm` | dirección normalizada por USIG |
| `barrio`, `comuna` | asignados **por geometría**, nunca por campo de texto |
| `anillo` | `nucleo` \| `ampliado` \| `fuera` |
| `categoria` | categoría normalizada del proyecto |
| `n_fuentes` | en cuántas fuentes independientes aparece |
| `apto_geometria` | si este punto puede participar del dibujo. Ver §5 |
| `nivel_publicacion` | `abierto` \| `punto` \| `agregado`. Ver §6 |
| `frescura` | fecha de la evidencia positiva más reciente. Ver §4 |
| `corte` | fecha de construcción de esta versión de la base |

### `local_fuente` — lo que dice cada fuente

Una fila por (local, fuente, registro en esa fuente). **Muchas por local.**

| campo | qué es |
|---|---|
| `local_id` | |
| `fuente` | `F01` \| `F02` \| `RUS` \| `OSM` \| `OVERTURE` \| `FSQ` \| `ATP` \| `PLACES` \| `PERMISOS` \| … |
| `id_en_fuente` | el identificador de esa fuente, tal cual |
| `lon_fuente`, `lat_fuente` | el punto **como lo da la fuente**, sin corregir |
| `nombre_fuente`, `direccion_fuente`, `categoria_fuente` | crudos |
| `vigencia_fuente` | lo que esa fuente afirma sobre el estado |
| `fecha_corte_fuente` | de cuándo es ese dato |
| `criterio_match` | por qué se pegó a este `local_id`. Ver §7 |
| `score_match` | |
| `revisado` | `auto` \| `manual` \| `pendiente` |

**La regla dura: no se colapsan las fuentes a un registro «verdadero».** `local` es una vista de
consenso; `local_fuente` es el registro histórico. Si mañana alguien discute un local, la
respuesta está en `local_fuente`, no en una decisión que ya nadie puede reconstruir.

---

## 2 · Identificador estable

`local_id` es un surrogate propio, correlativo, con prefijo: `LOC000001`. **Nunca derivado de un
identificador externo ni de un hash de atributos.**

- Hash de dirección + categoría: se rompe cuando el local cambia de rubro, y colisiona en
  edificios con dos locales, que en CABA es lo normal.
- `place_id` de Google: además de inestable, no es redistribuible.

Se asigna la primera vez que el local aparece y se persiste. La reasignación entre corridas se
resuelve por `local_fuente`: si un `id_en_fuente` ya está asociado a un `local_id`, se
mantiene. Los `local_id` nunca se reciclan; si un local se parte en dos, el original se retira
con `estado = superado_por` y se registran los dos nuevos.

---

## 3 · Corroboración: cuántas fuentes, y cuáles

`n_fuentes` cuenta **fuentes independientes**, no filas. Y no todas las fuentes son
independientes entre sí:

- **Overture incluye a Foursquare** como aportante. Overture + FSQ **no son dos**.
- **All The Places alimenta a Overture.** Idem.
- F01 y F02 son dos trámites distintos del mismo Gobierno, pero universos distintos: cuentan
  como dos.
- OSM, Places y el Relevamiento de Usos del Suelo sí son independientes entre sí.
- **Wikidata no forma grupo propio.** No es un relevamiento: es una transcripción de otras
  fuentes hecha por voluntarios. Un local corroborado «también por Wikidata» no está más
  corroborado. Entra como enriquecimiento y no suma a `n_fuentes`.

Definí un **grupo de independencia** por fuente y contá grupos, no fuentes. Si esto no se hace,
`n_fuentes` infla y la corroboración deja de significar nada.

---

## 4 · Vigencia: se guarda, no se resuelve

Ninguna fuente sabe qué está abierto hoy. En vez de inventar un veredicto, se guarda lo que cada
una afirma y se deriva un solo indicador honesto:

| fuente | qué afirma sobre vigencia |
|---|---|
| F02 | fecha de habilitación. **No registra bajas** |
| F01 | año del padrón |
| RUS | `ESTADO` activo/inactivo + año del relevamiento **de ese barrio** |
| OSM | fecha de última edición |
| Places | `businessStatus` + fecha de consulta |
| FSQ | `date_closed` y `date_refreshed` |
| Permisos | fecha de vencimiento de la disposición |

`frescura` = fecha de la **evidencia positiva más reciente**. Nunca se publica como «abierto»:
se publica como «última señal de actividad». La diferencia importa y hay que sostenerla en el
vocabulario.

---

## 5 · Aptitud geométrica — el campo que protege el mapa

`apto_geometria` decide si un punto participa del clustering y del dibujo de envolventes.

**No es apto** un punto que:
- viene de una geocodificación por calle sin altura, o por centroide de barrio o de manzana
- proviene sólo de una consulta radial y cae sospechosamente cerca del centro de consulta
- tiene sus fuentes en desacuerdo por más del umbral declarado

El punto de consenso de `local` se calcula por prioridad de precisión, no por promedio:
**parcela catastral (SMP) → USIG exacta calle+altura → punto de la fuente con mejor precisión
declarada → resto.** Promediar puntos de distinta precisión empeora el bueno.

Y un control obligatorio antes de dibujar: **una envolvente no puede derivarse mayoritariamente
de puntos no aptos.** Si pasa, el polígono se marca como derivado de la geometría de consulta y
no de la oferta, que es exactamente el defecto que ya tuvo el Atlas.

---

## 6 · Publicación en tres niveles

Es la restricción que decide si esta base sirve para lo que se quiere. Google Places no permite
redistribuir nombre, dirección ni `place_id`.

| nivel | qué se publica | cuándo |
|---|---|---|
| `abierto` | registro completo: nombre, dirección, punto, categoría | la identidad viene de una fuente redistribuible |
| `punto` | punto, categoría, zona — **sin nombre ni dirección** | la ubicación está corroborada por fuente abierta, la identidad no |
| `agregado` | sólo cuenta dentro de una celda o zona | el local existe únicamente en Places |

**Fuentes redistribuibles confirmadas:** F01, F02, RUS, Ferias y los permisos de espacio público
(CC-BY-2.5-AR), OSM (ODbL, con su propia obligación de atribución y share-alike), Overture
(CDLA-Permissive / Apache / CC0), Foursquare OS Places (Apache 2.0), All The Places (CC0).

**No redistribuibles:** Google Places, Guía Óleo, y toda guía privada.

De ahí sale el principio operativo del barrido: **Places descubre; la identidad publicable tiene
que venir de otra fuente.** Cada emparejamiento de un descubrimiento de Places contra OSM,
Overture o Foursquare convierte un registro `agregado` en uno `abierto`. Eso vale más que sumar
llamadas.

> ⚠ La interpretación de licencias de esta sección es una lectura de trabajo, no un dictamen.
> Antes de publicar, que la confirme el área legal de la Dirección. La mezcla de ODbL de OSM con
> licencias permisivas en un mismo producto derivado tiene condiciones propias que conviene
> revisar con alguien que las conozca.

---

## 7 · Trazabilidad de la deduplicación

Cada fila de `local_fuente` guarda **por qué** se pegó a ese `local_id`:

| `criterio_match` | qué significa |
|---|---|
| `smp` | misma parcela catastral. El más fuerte |
| `usig_exacta` | misma dirección normalizada, calle y altura |
| `proximidad_Nm` | a menos de N metros, con N declarado |
| `proximidad_y_nombre` | proximidad más similitud de nombre por encima del umbral |
| `id_compartido` | las dos fuentes declaran el mismo identificador upstream |
| `manual` | resuelto por una persona, con nota |

Reglas:
- **La similitud de nombre nunca alcanza sola.** Siempre acompañada de proximidad.
- **Análisis de sensibilidad al umbral, obligatorio y publicado.** Como el de ±5/±10/±30 que ya
  se hizo: si el resultado depende del corte, el corte está mal elegido.
- Los dudosos van a `revisado = pendiente`, no a una decisión automática.
- Un merge sin `criterio_match` es un merge que en seis meses nadie va a poder auditar. No entra.

---

## 8 · Controles que cortan la corrida

Con el criterio que ya se estableció: control que falla, corrida que para.

1. **Codificación** — mojibake sin reparar corta. Ya está implementado.
2. **Vocabulario** — si una fuente deja de traer un valor que el mapeo declara, corta.
3. **Asignación territorial** — todo `local` con punto tiene barrio por geometría, o corta.
4. **Independencia** — `n_fuentes` nunca cuenta dos fuentes del mismo grupo.
5. **Publicabilidad** — ningún archivo del nivel `abierto` puede contener un campo cuyo único
   origen sea Places. Verificación por columna y por procedencia, no por nombre de archivo.
6. **Lotes replicados** — todo registro F02 que caiga en un lote replicado detectado va marcado.
   Son el 22,6 % del padrón georreferenciado.
7. **Aptitud geométrica** — ninguna envolvente se dibuja mayoritariamente con puntos no aptos.
8. **Reproducibilidad** — `--check` contra una referencia congelada, como el que ya existe.

---

## 9 · Lo que la base habilita, en orden

1. Puntos por barrio, con procedencia y corroboración.
2. Clustering sobre los puntos aptos → candidatos a polo, en toda la Ciudad.
3. Envolventes, con la maquinaria que ya existe (HDBSCAN, envolventes, reparto por Voronoi).
4. **Cotejo contra las 22 zonas publicadas**: recalcularlas desde la base y explicar dónde no
   coincidan. Si no se puede, hay dos verdades paralelas.
5. Extensión a las zonas nuevas con el mismo procedimiento, sin excepciones por zona.

---

## 10 · Lo que la base no hace, y hay que decirlo

- **No es un censo.** Un local sin trámite, sin ficha en ninguna plataforma y sin presencia en
  ningún padrón no aparece. Los carros de choripán de la Costanera son parte de la gastronomía de
  esa zona y no van a estar. Es un límite del trabajo, no una afirmación sobre esos locales.
- **No dice qué está abierto hoy.** Dice cuándo fue la última señal de actividad.
- **No mide facturación, empleo ni superficie.**
- **No reemplaza ningún registro oficial.**
- **No va a tener nunca un denominador externo de completitud.** Es el límite más importante de
  esta lista y **ya no es un pendiente: es una limitación declarada.** Por decisión de alcance del
  2026-08-06 no se hacen pedidos fuera de la Dirección, así que se caen APRA, AGIP, INDEC,
  Estadística y Censos, la consulta a la AGC y el convenio con plataformas. No habrá una medición
  independiente contra la cual contrastar la base.

  Lo que sí hay, y con lo que se trabaja de acá en adelante, son **dos proxies internos**:

  1. `cobertura` = base ÷ Relevamiento de Usos del Suelo, por barrio. Su límite está declarado: el
     Relevamiento **está adentro de la base**, así que el cociente no puede bajar de 1 y lo que
     mide es cuánto agregan las otras seis fuentes sobre ese piso. Se reporta también sin el piso.
  2. `locales cada mil habitantes` (Censo 2022). Sirve para presentar y para ver el caso extremo;
     **no es un diagnóstico de cobertura**, porque la gastronomía se ubica donde hay oficinas y
     turismo y no donde hay camas.

  Con eso medido, la cobertura resultó **pareja** entre barrios (p90/p10 = 1,21) y el sur **no**
  está peor cubierto (2,50 contra 2,45). Esa conclusión se sostiene sobre proxies internos y así
  hay que escribirla, siempre: «con los indicadores disponibles», nunca «se verificó».

  **Esta limitación va también adentro del mapa**, no sólo acá.

- **Pero el error sí está medido donde la base es más flaca, y es del orden del 11 %.** Es la
  limitación que dejó de ser una incógnita, y conviene decirla en ese orden: no sabemos si la
  cobertura es pareja en toda la Ciudad, **y además medimos el techo del error donde somos más
  débiles.**

  La sonda de Google Places del 2026-08-06 consultó los **cinco barrios peor cubiertos** según los
  dos indicadores internos —Villa Gral. Mitre, San Cristóbal, Villa Luro, Paternal y Villa del
  Parque—. Sobre el universo comparable —sólo anillo núcleo, que es lo que la base mapea— encontró
  **121 locales que la base no tiene, sobre los 1.128 que tiene ahí: un 10,7 %.**

  Tres calificaciones van pegadas al número y ninguna es opcional:

  1. **Es una cota superior, no un promedio.** Los cinco barrios se eligieron *por ser los peores*,
     con un criterio declarado antes de mirar cuáles salían. El 11 % es el techo del faltante donde
     la base es más flaca, no el faltante típico de la Ciudad.
  2. **No dice nada sobre vigencia.** Places descubre, no confirma. Un punto nuevo no es un local
     abierto: es una ficha que nosotros no teníamos.
  3. **No se traslada al sur.** Los cinco barrios son del **oeste y el centro** —comunas 3, 10, 11
     y 15—. Ninguno es de las comunas 4, 8 ni 9. Afirmar el 11 % para el sur sería exactamente el
     error que la regla «no encontramos ≠ no existe» ataja, con el signo cambiado: extender una
     medición a un territorio donde no se midió. Si hace falta el número del sur, se mide ahí.

  Esto hace, parcialmente, el trabajo que iba a hacer el denominador externo, y por eso vive acá y
  no en una nota suelta. **Lo que no hace es entrar a la base:** la licencia de Places no es
  redistribuible, los 121 locales no se incorporan, y la salida quedó en `outputs/analisis_interno/`,
  ignorada por Git. El producto de esa corrida es un número de diagnóstico, no puntos.

---

## 11 · Enganches preparados · ~~las fuentes que están en gestión~~ · DADOS DE BAJA

> **Decisión de alcance del 2026-08-06: no se hacen pedidos fuera de la Dirección.** Se caen las
> cuatro fuentes de esta sección —APRA, AGIP, INDEC y Estadística y Censos—, más la consulta a la
> AGC y el convenio con plataformas. **Ninguna está en gestión y ninguna se va a pedir.**
>
> La sección se conserva, tachada y con esta nota, en vez de borrarse: describe dónde entraría cada
> una si alguna vez la decisión cambia, y ese diseño costó trabajo. Pero **hoy no hay que leerla
> como un plan**, y la consecuencia principal —que nunca habrá denominador externo de
> completitud— ya está declarada como limitación en el §10, no como pendiente.
>
> Dos consecuencias más, que también se declaran en vez de quedar esperando:
>
> - **El diccionario de códigos del Relevamiento se sigue infiriendo.** No va a llegar el oficial.
>   La inferencia queda documentada valor por valor en `INFERENCIA_TIPO2_RELEVAMIENTO.md`, para que
>   sea auditable sin él. Y como el mapa depende de esa fuente, si la inferencia está corrida el
>   mapa se mueve: eso viaja con el mapa.
> - **La consulta a la AGC queda preparada y sin mandar**, en `consulta_agc/`, con la nota de que
>   no se envió por decisión de alcance.

Cuatro fuentes que Diego estaba gestionando fuera de este repositorio. **No están cargadas y no hay
cargador escrito**: lo que hay es el lugar donde habrían entrado, decidido de antemano.

### Las tres que entran como fuente en `local_fuente`

| fuente | organismo | grupo de independencia | por qué ese grupo |
|---|---|---|---|
| Certificados de Aptitud Ambiental | APRA | **`GCBA_AMBIENTAL`** — propio | trámite ambiental distinto del de habilitación, con su propio universo y su propia mora |
| Padrón de Ingresos Brutos con domicilio | AGIP | **`GCBA_TRIBUTARIO`** — propio | universo tributario, independiente del de habilitaciones: hay contribuyentes sin habilitación y viceversa |
| Diccionario de códigos del Relevamiento | DG Estadística y Censos | **ninguno: no es una fuente** | es el vocabulario del RUS, que ya está cargado. Entra corrigiendo la clasificación de `RUS`, no agregando filas |

Tres reglas que ya quedan fijadas para las dos primeras:

1. **Ni una ni otra convierte un registro en «local activo».** APRA certifica aptitud ambiental y
   AGIP registra inscripción tributaria. Ninguna de las dos afirma que haya un local abierto, y el
   guardarraíl 5 aplica igual que al padrón de habilitaciones.
2. **Ambas traen datos sensibles.** CUIT, titular y probablemente monto o categoría. Entran con
   lista permitida de columnas (`usecols` armado desde la ficha de la fuente), y el control 5 del
   §8 corta la corrida si una columna prohibida aparece en una salida. **Ningún monto ni
   categoría tributaria entra a la base, ni siquiera a las salidas internas.**
3. **Sin coordenadas, se geocodifica con USIG.** No con Nominatim: su política prohíbe el
   geocodificado en volumen y limita a un request por segundo.

### La cuarta no entra como filas: entra como denominador

**El tabulado especial del Censo Económico por comuna, rama 56 (INDEC), no aporta locales.**
Aporta lo que hoy falta para poder afirmar cualquier cosa sobre cobertura: un **conteo externo,
independiente y por comuna** contra el cual medir la completitud de la base.

```
completitud_comuna = locales de la base en la comuna ÷ locales del tabulado en la comuna
```

Por qué importa, y por qué no es una métrica más: hoy la base puede decir cuántos locales tiene
por comuna, pero **no puede distinguir una comuna con poca gastronomía de una comuna poco
cubierta**. Es exactamente el sesgo que el §0 declara como el peor riesgo del proyecto —«produce
polos donde sólo hubo más consultas»— y hasta que exista ese denominador, la afirmación «la
cobertura es pareja» no se puede hacer, en ningún informe.

Tres cuidados para cuando llegue:

- **la unidad no coincide.** El Censo Económico cuenta locales con actividad económica declarada;
  la base cuenta lo que siete fuentes afirman. La razón se lee como factor de captura, no como
  porcentaje de completitud verdadera;
- **la rama 56** es «servicios de comida y bebida» y no es exactamente el anillo núcleo del
  proyecto. La correspondencia se declara antes de calcular, no después de ver el número;
- **el denominador tiene fecha.** Un tabulado de 2020/21 contra una base de 2026 mide dos
  momentos, y la comparación se rotula con las dos fechas.

### Cómo se enganchan sin tocar nada

Las tres primeras entran por el mismo camino que las seis fuentes del GCBA que ya están: un
cargador propio en `bajar_*.py`, su fila en la tabla de fuentes con licencia y grupo, y su lista
permitida de columnas. **Ninguna requiere cambiar el esquema de `local` ni de `local_fuente`.** El
denominador del INDEC no toca ninguna de las dos tablas: vive en su propia tabla por comuna y se
usa en los informes.
