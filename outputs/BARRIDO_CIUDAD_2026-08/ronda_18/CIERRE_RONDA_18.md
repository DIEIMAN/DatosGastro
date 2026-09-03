# Cierre · lo que cambió de valor y el control de anclas

Fecha de la medición: 10/08/2026. Todo se midió en EPSG:5347 y se guardó en EPSG:4326. Cero
consultas a servicios pagos. Los archivos citados están en esta misma carpeta.

---

## 1 · Lo que cambió de valor

| qué | antes | ahora |
|---|---|---|
| La Boca · Caminito | 1,27 ha · 16 locales | **4,15 ha · 37 locales** |
| Mataderos | sin ninguna geometría | **43,99 ha · 17 locales, borde tentativo** |
| Villa Ortúzar | dos opciones medidas | **34,39 ha · 69 locales**, opción B adoptada |
| Balvanera · Once | 19,18 ha · 74 locales | **dos lecturas medidas**, la decisión sigue abierta |
| Concentraciones dentro de algún polo | no se publicaba | **53 de 124** |
| Pares de polos que comparten superficie | no se publicaba | **25 pares · 1.263 locales en más de un polo** |
| Establecimientos con historia fuera del borde de su polo | no se medía | **42 filas · 32 establecimientos · 14 páginas** |

Y una cifra que **no** cambió aunque parezca que debería: los polos sin borde propio siguen
siendo **cuatro**. Mataderos recibe un borde tentativo, y un borde tentativo no es un borde
cerrado.

---

## 2 · El control de anclas · el resultado

Se midieron **292 anclas en 37 de los 41 polos**: los establecimientos que cada página nombra y
los que la capa de reconocimiento ubica dentro de la zona de la que ese polo se recorta. De ésas,
185 caen dentro del borde de su polo, 96 quedan afuera y 11 la página las nombra sin que el
repositorio sepa dónde están.

**La cifra que importa: 42 establecimientos con historia —Bar Notable, restaurante icónico,
pizzería emblemática, heladería histórica— sostienen la condición de su zona y quedan fuera del
borde de su polo, en 14 de las 37 páginas.** Son 32 establecimientos distintos: diez cuentan dos
veces porque hay tres zonas de las que se recortan dos polos cada una —La Boca, Barracas y Nueva
Pompeya—, y las dos páginas invocan la misma evidencia de la misma zona.

El caso de Balvanera no es raro. **Es el más común de los tres que ya conocíamos.**

### Las cinco páginas donde el borde no contiene ni uno

| página | con historia fuera | el más lejos |
|---|---|---|
| La Boca · Almirante Brown y Necochea | 8 | El Estaño 1880, a 926 m |
| Balvanera · Once | 3 | Café de los Angelitos, a 759 m |
| Liniers · Mercado Andino | 1 | El Ciervo, a 129 m |
| Nueva Pompeya y Parque Patricios | 1 | El Buzón, a 256 m |
| Nueva Pompeya · eje Av. Sáenz | 1 | El Buzón, a 256 m |

La Boca · Almirante Brown y Necochea es el caso más fuerte de todos y **no estaba en la lista**:
su página nombra cinco establecimientos con historia, la zona tiene ocho, y el borde publicado no
contiene ninguno. El más cercano, Banchero, está a 54 metros.

### Las otras nueve

Chacarita (1 fuera, 2 dentro) · Monte Castro (1 y 1) · Mataderos (3 y 1) · Almagro (3 y 5) ·
Colegiales (2 y 1) · Monserrat y Congreso (4 y 6) · Barracas · Av. Montes de Oca (3 y 2) ·
Barracas · Iriarte, California y Vieytes (4 y 1) · La Boca · Caminito (7 y 1).

### Qué significa y qué no

La condición se mide **sobre la zona y no sobre el recorte**: ésa es la regla que salió de
Almagro y esta tanda no la toca. Que un Bar Notable esté en la zona y no en el recorte **no
invalida la admisión del polo**. Lo que dice el control es otra cosa: hoy la mayoría de esas
páginas publica un polígono y una lista de establecimientos con historia sin decir que los
segundos no están dentro del primero. Un lector que mire el mapa y lea la lista va a suponer que
sí. Eso es lo que hay que escribir en la página, caso por caso.

Hay un segundo grupo, con distinción contemporánea en vez de trayectoria —MICHELIN y rankings
internacionales—: sumándolo, las filas pasan de 42 a 55 y las páginas de 14 a 15. Se cuentan
aparte a propósito: abren la misma vía pero no dicen lo mismo.

### Cómo está medido

`dentro_del_borde` sale de `covers()` **de un punto contra un polígono**, que es lo correcto: la
regla que prohíbe `covers()` es la de contención de un polígono dentro de otro, que se verifica
por superficie perdida y así se hizo en las dos tablas de solapes. Para un punto, `contains`
devuelve falso a un establecimiento que está a cero metros sobre el borde, y la ronda anterior ya
se comió ese error una vez.

La ubicación de cada ancla sale, por orden: del punto de la capa de reconocimiento, que es una
coordenada real, para 216 de las 292; y de la altura de puerta contra el callejero oficial para
65, que devuelve el **centro de la cuadra** y no la puerta, con precisión de media cuadra. El
método va escrito en cada fila y no al pie. **Por eso el Café de los Angelitos aparece con dos
distancias y las dos son correctas**: 768 m si se lo ubica por la altura de puerta —el centro de
la cuadra de Av. Rivadavia 2001-2100— y 759 m con la coordenada de la capa. La diferencia es el
método, no la medición.

Las 11 anclas que la página nombra y el repositorio no puede ubicar no se descartan ni se ponen
en el centroide de nada: salen en la tabla con la distancia vacía. Son Sucre (Belgrano); Ay
Miranda, La Media Costilla y La Renaciente (Monte Castro); Vereda Adentro (Núñez); Antiche
Tentazioni, La Bici, La Fábrica del Taco y Niniveh (Colegiales); Fa Song Song y Saigon Noodle
Bar (Retiro). En diez de los once no hay dirección escrita en ninguna de las dos fuentes; en el
onceavo, Saigon Noodle Bar, la página escribe «M.T. de Alvear 818» y esa altura no resuelve
contra el callejero oficial.

Y cuatro polos no tienen ninguna ancla en ninguna de las dos fuentes: Donado-Holmberg, García del
Río, Villa Luro y Baek-ku.

**Archivo: `anclas_dentro_y_fuera.csv`**, 292 filas.

---

## 3 · Balvanera · Once · las dos lecturas

El Café de los Angelitos, Av. Rivadavia 2100, Bar Notable verificado abierto a junio de 2026, es
la evidencia con la que la regla admitió esta zona. El recorte adoptado lo deja afuera.

### Lectura 1 · el enclave, como está

Eje Tucumán 2379-2755 más la transversal de Paso 700-799, que salen de las cinco puertas que la
propia página lista.

**19,18 ha · 74 locales.** Café de los Angelitos afuera, a 768 m.

Establecimientos con reconocimiento que contiene: **ninguno**. Las cinco puertas del enclave
—Sucat David, El Jaial, Al Galope, Lalo Helueni y Yaffo Kosher— están las cinco adentro, pero
ninguna de las cinco está en la capa de reconocimiento: salen del padrón oficial de 2015, que la
propia página declara dudoso en bloque.

### Lectura 2 · extendida hasta contener el Café de los Angelitos

Lo anterior más la transversal de Pasteur entre Tucumán y Av. Rivadavia, y Av. Rivadavia
2001-2200.

**44,75 ha · 154 locales.** Café de los Angelitos adentro.

**Por dónde se extiende, y por qué por ahí.** Pasteur es la transversal que corta el eje de
Tucumán en el extremo sur del enclave —el bloque 2301-2400, que es el que contiene el 2379— y es,
de las cinco que llegan a Av. Rivadavia, la que llega más cerca del Café: su cruce con Rivadavia
cae a 325 m, contra 451 por Azcuénaga, 572 por Larrea, 713 por Paso y 956 por Av. Pueyrredón. Al
sur de Rivadavia, Pasteur se llama Pichincha.

**Cuánto se extendió:** 1.083 m de eje nuevo, 832 sobre Pasteur y 251 sobre Av. Rivadavia; +25,56
ha y +80 locales. Es el mínimo que cierra: con Av. Rivadavia 2001-2100 —una sola cuadra— el Café
igual queda adentro, pero la figura se parte en dos piezas sueltas.

Establecimientos con reconocimiento que contiene: **el Café de los Angelitos**. Los otros dos que
la capa ubica en la zona —El Tropezón, Av. Callao 248, y Roma del Abasto, Anchorena 806— siguen
afuera, a 742 y 323 m.

### Mi lectura, en dos renglones

Adoptaría la lectura 2. El enclave kosher es una pieza del polo y está bien delimitada, pero un
polígono que no contiene ninguno de los establecimientos con reconocimiento de su zona, y menos
el que la hizo entrar, describe al enclave y no a la zona; y la lectura 1 se apoya entera en un
padrón de 2015 que la propia página llama dudoso, mientras que el Café es el único ancla de
Balvanera con vigencia verificada este año.

Contra: la extensión duplica la superficie y suma 80 locales que la página no relevó, y el tramo
de Pasteur lo elige esta corrida, no el texto. Si se adopta, el criterio tiene que ir escrito en
la página igual que en La Boca.

---

## 4 · La Boca · Caminito · decisión firmada, geometría entregada

**4,15 ha · 37 locales.** Caminito entero más las dos cuadras de Av. Don Pedro de Mendoza que
toca, 1871-1939.

Criterio escrito para la página: *el polo se extiende sobre Av. Don Pedro de Mendoza lo mínimo
necesario para contener La Perla de Caminito, que es el establecimiento sobre el que la zona se
apoya.*

La Perla de Caminito, Av. Don Pedro de Mendoza 1899, queda **adentro**; estaba a 26 m del borde
anterior.

Los otros dos que la página nombra siguen afuera, y las distancias se publican **contra el borde
nuevo**, que no son las de antes:

| establecimiento | distancia al borde nuevo | al borde anterior |
|---|---|---|
| Genovés (Brandsen 923) | **343 m** | 343 m |
| El Obrero (Caffarena 64) | **1.026 m** | 1.136 m |

Solape contra La Boca · Almirante Brown y Necochea: **ninguno.** Los dos polígonos no se tocan:
quedan a 369 m uno del otro (Z52 mide 6,14 ha; Z53, 4,15). El par no aparece en la tabla de solapes
porque no hay nada que declarar.

---

## 5 · Mataderos · borde tentativo

**43,99 ha · 17 locales · BORDE TENTATIVO.** Las manzanas frentistas del cruce de Av. Lisandro de
la Torre y Av. de los Corrales, con el entorno mínimo que cierra una figura sobre el callejero:
siete manzanas, 671 m de eje.

Va marcado como tentativo en los datos, en tres lugares: la columna `caracter` de
`perimetros_ronda_18.csv`, el campo `borde_tentativo` de `bordes_vigentes_41.geojson` y el mismo
campo en `anclas_dentro_y_fuera.csv` y `solapes_declarados.csv`.

**Un aviso que hay que dar antes de que alguien divida una cosa por la otra:** de las 43,99 ha,
**40,70 son una sola manzana** —el predio cerrado del cruce— y las otras seis suman 3,29. La
densidad por hectárea de esta zona no es comparable con la de las demás.

### La regla que no se pudo aplicar, y por qué

De los cuatro establecimientos que la página nombra, el borde contiene uno: **Bar Oviedo**, Av.
Lisandro de la Torre 2407, a 11 m del cruce. Los otros tres quedan afuera: 9 de Julio (Larrazábal
1276) a 888 m, El Cedrón (Av. Alberdi 6101) a 691 m y Bar del Glorias (Andalgalá 1982) a 667 m.

La regla decía «extendé sobre la avenida que corresponda». Medido: **ninguno de los tres está
sobre las dos avenidas del perímetro escrito**. Larrazábal y Andalgalá no son las avenidas que la
página nombra, y Andalgalá no es una avenida. La avenida que los tres tienen cerca es otra, Av.
Juan B. Alberdi —a 72 m del 9 de Julio, 83 m del Bar del Glorias y 0 m de El Cedrón— y llegar
hasta ella exige un brazo de un kilómetro por Av. Lisandro de la Torre.

Se midió lo que costaría, en vez de adoptarlo en silencio: cruce + brazo + Av. Alberdi 5501-6499
da **92,18 ha y 91 locales** —el doble de superficie— alcanza tres de los cuatro, y aun así deja
al Bar del Glorias a 309 m. El brazo aporta 30 locales en 65 hectáreas. No se adopta.

### El eje comercial de Av. Alberdi, publicado aparte

**Av. Juan B. Alberdi 5501-6299: 24,27 ha · 55 locales.**

Relación con el borde tentativo: **son dos objetos separados.** Lo más cerca que pasan es 529 m y
no comparten ni una hectárea. El borde tentativo contiene uno de los cuatro establecimientos que
la página nombra (Bar Oviedo) y el eje comercial contiene dos (9 de Julio y El Cedrón); entre los
dos, tres de cuatro. El cuarto, el Bar del Glorias, no está en ninguno.

El eje es de otra fuente y mide otro objeto: es el eje comercial que releva la Ciudad. Adoptarlo
como perímetro le atribuiría al polo el recorte de esa fuente.

---

## 6 · Villa Ortúzar · el control del solape

La geometría no se rehizo: **34,39 ha · 69 locales**, las dos aceras de Av. Álvarez Thomas entre
el 600 y el 1700. Reparto por barrio: Colegiales 34,9 % · Chacarita 34,0 % · Villa Ortúzar 31,1 %.

**El solape verificado contra la geometría vigente: 15,93 ha y 25 locales compartidos con
Chacarita, Colegiales y Federico Lacroze. La cifra de la decisión coincide exacto.** Por polo:

| contra | ha | locales |
|---|---|---|
| Colegiales | 12,07 | 23 |
| Federico Lacroze | 3,46 | 2 |
| Chacarita | 1,86 | 9 |
| los tres juntos, sin contar dos veces lo que se pisan entre ellos | **15,93** | **25** |

---

## 7 · Todos los solapes, no sólo ése

**25 pares de polos comparten superficie.** Los cinco más grandes por locales compartidos:

| par | ha | locales |
|---|---|---|
| Centro y Microcentro + Retiro | 52,16 | 301 |
| Chacarita + Federico Lacroze | 60,37 | 153 |
| Avenida Corrientes + Centro y Microcentro | 21,72 | 133 |
| Federico Lacroze + Colegiales | 67,02 | 115 |
| Abasto + Almagro | 25,33 | 101 |

Lo que la tabla existe para impedir:

- la suma de los 41 polos por separado da **12.087 locales**;
- la unión de los 41 mide **10.801**;
- o sea que **1.286 se cuentan de más**, repartidos en **1.263 locales distintos** que están en
  dos o más polos.

Cinco de los 25 pares involucran un polo que publica el polígono de su barrio en vez del del
polo —Retiro, Núñez, Villa Santa Rita— y eso va marcado en la tabla: ese solape es una propiedad
de la capa administrativa, no del polo.

**Archivos: `solapes_declarados.csv`** (25 pares, con la lista de `local_id` compartidos) y
**`solapes_locales_detalle.csv`** (1.309 filas, un local por par). El detalle sale por `local_id`,
barrio y comuna; nombre y dirección de cada local están en `base/local.csv` por ese identificador
y no se copian acá.

---

## 8 · Las 124 concentraciones contra los bordes nuevos

Rehecho sobre la geometría vigente. La correspondencia anterior se había calculado contra la
geometría de la ronda 16 y ya no describía el conjunto.

| | concentraciones | locales | ha |
|---|---|---|---|
| contenidas o mayormente dentro de un polo | **53** | 6.800 | 1.355,42 |
| tocan un borde sin quedar mayormente dentro | 28 | 2.818 | 782,87 |
| fuera de todo polo | 43 | 2.902 | 1.005,26 |

**La cifra publicable: 53 de las 124 concentraciones caen dentro de algún polo y 71 no; las 71
suman 5.720 locales.**

Las más grandes de las 43 que quedan enteramente fuera: Palermo Botánico (207 locales), Congreso
(175), Palermo · Bustamante y Mario Bravo (154), Alto Palermo (141), Av. Cuenca en Villa del
Parque (135) y Av. Eva Perón entre Escalada y Castañares (132).

«Dentro» se resolvió por **superficie perdida** —`concentración.difference(polo).area`— y no con
un predicado. Una concentración cuenta como dentro si le queda menos del 1 % de su superficie
afuera, o si más de la mitad cae dentro de un polo.

**Archivo: `correspondencia_124_x_41.csv`**, 124 filas.

---

## 9 · Verificación de cifras

Se corrió al final, con el mismo código de la ronda anterior y las canónicas al día.

**Resultado: 5 cifras del texto no coinciden con su fuente, 12 sí y 20 todavía no se usan en
ningún documento.** Las 5 son las mismas de la tanda pasada y ninguna es nueva:

| cifra | dice el texto | dice la fuente |
|---|---|---|
| objetos territoriales disjuntos | 39 | **40** |
| superficie de la unión de las concentraciones | 3.128,5 ha | **3.143,53 ha** |
| polos sin borde propio | dieciocho | **4** |
| locales en los polos sin borde | 3.227 | **527** |
| hectáreas en los polos sin borde | 893,5 | **112,9** |

Las dos que el pedido marcaba están confirmadas y quedaron anotadas en la fuente para que nadie
las «corrija» al revés: **polos sin borde propio = 4** y **objetos disjuntos = 40**. La que está
vieja es la prosa.

Las 20 sin mención son casi todas de esta tanda: las que produjo esta ronda todavía no están
escritas en ningún documento. No es un error; es la lista de lo que falta redactar.

**Archivos: `cifras_canonicas.json`** (37 cifras, 19 nuevas o actualizadas) y
**`verificacion_cifras.json`**.

---

## 10 · Lo que queda abierto

1. **La decisión de Balvanera.** Las dos lecturas están medidas; la firma no es mía.
2. **Las 14 páginas del control de anclas.** Hay que escribir en cada una que la condición se
   mide sobre la zona. Las cinco donde el borde no contiene ninguno son las urgentes, y La Boca ·
   Almirante Brown y Necochea es la más urgente de las cinco.
3. **Mataderos sigue sin borde cerrado.** El tentativo es un lugar donde apoyar el mapa, no una
   delimitación. Lo que lo cerraría es el perímetro de ocupación de la Feria, que es un dato
   administrativo que este repositorio no tiene.
4. **Las 5 cifras que el documento publica viejas** siguen sin corregir en la prosa.
5. **Nada quedó commiteado.** El índice de git está trabado por un `.git/index.lock` de las 00:15
   de hoy: cualquier `git add` falla con «Another git process seems to be running». Por regla, no
   se toca ese archivo. Hay 640 cambios en el árbol —640 de antes de esta tanda, más los de acá—
   esperando. Hay que destrabarlo a mano antes de commitear.

---

## Archivos de esta carpeta

| archivo | qué es |
|---|---|
| `anclas_dentro_y_fuera.csv` | **el control de las anclas**, 292 filas |
| `solapes_declarados.csv` | los 25 pares de polos que comparten superficie |
| `solapes_locales_detalle.csv` | qué locales son, por `local_id` |
| `correspondencia_124_x_41.csv` | las 124 concentraciones contra los bordes nuevos |
| `perimetros_ronda_18.csv` | las cuatro zonas que esta ronda tocó |
| `geometria/perimetros_ronda_18.geojson` | las 6 piezas nuevas, EPSG:4326 |
| `geometria/bordes_vigentes_41.geojson` | la capa vigente completa, EPSG:4326 |
| `cifras_canonicas.json` · `verificacion_cifras.json` | las cifras y el texto contra ellas |
| `BORDES_RONDA_18.txt` · `ANCLAS_DENTRO_Y_FUERA.txt` · `SOLAPES_Y_CORRESPONDENCIA.txt` · `VERIFICACION_CIFRAS.txt` | la salida completa de cada corrida |
| `bordes_ronda_18.py` · `anclas_dentro_y_fuera.py` · `solapes_y_correspondencia.py` · `cifras_y_verificacion.py` · `geometria_vigente.py` | los scripts, en ese orden |
