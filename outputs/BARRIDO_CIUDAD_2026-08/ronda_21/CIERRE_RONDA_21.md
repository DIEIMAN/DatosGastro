# Cierre · los seis repartos aplicados, la fusión verificada, y las calles para escribir 23 perímetros

Fecha de la medición: 10/08/2026. Todo se midió en EPSG:5347 y se guardó en EPSG:4326. La
contención se verificó por superficie perdida y nunca con `covers()`. Universo `anillo=nucleo &
apto_geometria`, 23.981 locales. Cero consultas a servicios pagos y ninguna fuente cerrada.

---

## 1 · Las cifras que cambian, de una

| qué | antes | ahora |
|---|---:|---:|
| Suma de los 41 por separado, locales | 12.105 | **11.403** |
| Unión de los 41, locales | 10.819 | **10.819** (no cambia) |
| Unión de los 41, hectáreas | 5.444,15 | **5.444,15** (no cambia) |
| Se cuentan de más, veces | 1.286 | **584** |
| Locales distintos en dos o más polos | 1.263 | **562** |
| Pares de polos que comparten superficie | 25 | **20** |
| Polos del atlas, con la fusión | 41 | **39** |
| Suma de los 39 por separado, locales | — | **11.119** |
| Se cuentan de más, con la fusión | — | **300 veces sobre 300 locales distintos** |
| Pares con solape, con la fusión | — | **12** |

**La unión no se mueve, y eso es lo que prueba que el reparto está bien hecho.** Repartir un
solape no agrega ni saca territorio: mueve de qué página es. Si la unión hubiera cambiado, algo se
habría perdido en el camino. Lo que baja —de 1.286 a 584 y después a 300— es **la cantidad de
veces que el atlas cuenta un mismo local dos veces**: el reparto se lleva el 55 % de la doble
cuenta y la fusión, el 49 % de lo que quedaba. Entre las dos, **el 77 %**.

---

## 2 · A · Los cinco repartos, y las dos cosas que no eran como estaban escritas

### Las cifras finales de las ocho páginas

| polo | página | publica hoy | después de repartir | cambia |
|---|---|---:|---:|---:|
| Z46 | Retiro | 467,14 ha · 715 | **414,98 ha · 414** | −52,16 ha · −301 |
| R12 | Centro y Microcentro | 184,12 ha · 1.084 | **153,72 ha · 875** | −30,40 ha · −209 |
| R02 | Avenida Corrientes | 49,67 ha · 354 | **49,67 ha · 354** | sin cambio |
| Z47 | Monserrat y Congreso | 13,77 ha · 133 | **13,77 ha · 133** | sin cambio |
| R13 | Abasto | 109,00 ha · 373 | **107,14 ha · 365** | −1,86 ha · −8 |
| Z37 | Almagro | 60,90 ha · 207 | **37,42 ha · 114** | −23,48 ha · −93 |
| R08 | Villa Crespo | 335,46 ha · 823 | **293,83 ha · 746** | −41,63 ha · −77 |
| R21 | La Paternal | 385,34 ha · 307 | **377,29 ha · 293** | −8,05 ha · −14 |

Los que ganan el solape no cambian de cifra: ya lo tenían adentro. **El reparto no le da nada a
nadie; le saca a la página que lo estaba contando de prestado.** Y el Microcentro entra en tres de
los cinco, así que su renglón hay que leerlo entero: conserva las 52,16 ha de Retiro y entrega las
21,72 de Corrientes y las 8,68 de Monserrat.

**Los 702 locales que cambian de página están uno por uno en `repartos_locales_que_cambian.csv`**,
con nombre, dirección, barrio, qué página deja de contarlos y cuál los sigue contando.

### A4 · Medrano · la orientación es la que decía el pedido, y hay un detalle del nomenclador

**Al este es Abasto, al oeste es Almagro.** Verificado, no supuesto:

- El tramo de Av. Medrano que cruza el solape corre a **7,0° · norte-sur**, así que «este» y
  «oeste» sí nombran sus dos flancos.
- El reparto da lo mismo a **200, 400, 800 y 1.600 metros y sin recorte**. No depende de cuánto
  contexto se mire.
- Al este quedan **23,48 ha y 93 locales** para el Abasto; al oeste, **1,86 ha y 8 locales** para
  Almagro.

Y el detalle que hay que saber antes de escribirlo: **el nomenclador pone «Almagro» a las dos
aceras de Medrano en todo el tramo que cruza el solape** —alturas 401 a 800—, y las dos mitades
caen 100 % dentro del barrio Almagro. Medrano no es ahí un límite de barrio: es una avenida
interior. El corte se sostiene igual, porque los polos no son barrios, pero la página no puede
decir que Medrano separa un barrio de otro.

**Lo que cuesta:** Almagro pierde 93 de sus 207 locales y se queda con 114. Es la página que más
se mueve de las ocho en proporción.

### A5 · Warnes · acá la orientación NO era la que estaba escrita, y hay dos lecturas

Tres cosas medidas, y las tres importan:

**1. Av. Warnes no corre norte-sur: corre a 112,5° · este-sudeste a oeste-noroeste.** Sus dos
flancos son **nornoreste y sudsudoeste**. La frase de la decisión —*«lo que queda al este es de
Villa Crespo»*— nombra un flanco que este eje no tiene.

**2. Warnes no es el límite entre Villa Crespo y La Paternal.** Los dos barrios comparten
**127,9 metros de borde y sólo 5 de ellos corren sobre Warnes: el 3,9 %.** Lo que el nomenclador
sí dice es que Warnes separa **La Paternal de Chacarita** entre las alturas 1452 y 1999, y que por
debajo del 1400 es interior a Villa Crespo con las dos aceras del mismo barrio. La matriz define a
R21 por San Martín y Warnes, y de ahí viene la frase; el bloque «Dónde está» de La Paternal no
nombra Warnes: nombra Beláustegui, Remedios de Escalada de San Martín, Paz Soldán, Rojas, Ávalos,
Espinosa y Terrero.

**3. El reparto medido, que también da igual a los cinco radios:**

| flanco | ha | locales | va a |
|---|---:|---:|---|
| nornoreste | 8,05 | 14 | **R08 Villa Crespo** |
| sudsudoeste | 41,63 | 77 | **R21 La Paternal** |

La regla es la misma para los dos cortes: cada flanco va a la página que tiene más masa propia de
ese lado, y acá La Paternal tiene 49,00 ha al sudsudoeste contra 41,15 de Villa Crespo dentro de
los 200 m del solape, y Villa Crespo tiene 20,87 al nornoreste contra 1,02. Es coherente con el
nomenclador: el flanco sudsudoeste es el que Warnes le da a La Paternal.

**Y la consecuencia que hay que ver antes de escribir la página:** de las 41,63 ha que se lleva La
Paternal, **el 69 % está adentro del barrio Villa Crespo** y el 14 % adentro de Caballito; sólo el
14 % está en Paternal. Del otro lado, de las 8,05 que se lleva Villa Crespo, el 28 % está en
Chacarita. No es un error del corte: es que el polígono de R21 mete 69 hectáreas dentro del barrio
Villa Crespo y 12 dentro de Caballito, y eso ya estaba así antes de esta ronda.

**Por eso va medida la variante espejo, y no adoptada.** Si el reparto se diera vuelta:

| | como se adoptó | espejo |
|---|---:|---:|
| R08 Villa Crespo | 293,83 ha · 746 locales | **327,40 ha · 809 locales** |
| R21 La Paternal | 377,29 ha · 293 locales | **343,71 ha · 230 locales** |

Con una firma tuya de un renglón se cambia. Lo dejo medido para que no cueste otra ronda.

---

## 3 · B · Chacagiales · la fusión verifica

**Las cinco pruebas pasan.** El modelo es el de Palermo: el total es la unión, las subzonas se
publican por separado y no se suman entre sí.

| | ha | locales | loc/ha |
|---|---:|---:|---:|
| **Chacagiales · el sistema** | **495,82** | **891** | 1,80 |
| · Chacarita | 94,81 | 202 | 2,13 |
| · Federico Lacroze | 303,28 | 532 | 1,75 |
| · Colegiales | 229,08 | 441 | 1,93 |

**Sumar las tres filas da 627,17 ha y 1.175 locales: cuenta 131,36 ha y 284 locales de más, sobre
279 locales distintos** que están en dos subzonas o en las tres.

### Las pruebas, una por una

**1 · Contención.** Las tres subzonas pierden 0,0 m² dentro del sistema.

**2 · Menos pedazos.** Por separado los tres vienen en **nueve piezas** —Chacarita ya viene en
seis— y la unión sale en **tres**: la fusión pega seis. La mayor se lleva el **90,2 %** de la
superficie (447,28 de 495,82 ha). Quedan sueltas 43,98 ha de Federico Lacroze **a 65,5 m** del
cuerpo y 4,55 ha de Chacarita **a 17,3 m**: el ancho de una calle. Exigir «una sola pieza» habría
sido una vara que ninguno de los tres pasa por su cuenta.

**3 · Continuidad.** La curva pedida, y después la prueba que la curva no contesta:

| | 20 m | 40 m | 60 m | 80 m | 120 m |
|---|---:|---:|---:|---:|---:|
| **Chacagiales** | **1,2 %** | **3,0 %** | **5,5 %** | **12,6 %** | **82,2 %** |
| · Chacarita | 5,4 % | 6,4 % | 15,3 % | 29,2 % | 51,5 % |
| · Federico Lacroze | 2,1 % | 4,9 % | 8,1 % | 11,8 % | 55,5 % |
| · Colegiales | 1,8 % | 6,1 % | 10,2 % | 25,4 % | 92,3 % |

> **Las tres últimas filas no se comparan con la primera.** El porcentaje es sobre el total de
> puntos de cada figura: Chacagiales tiene 891 locales y Colegiales 441, así que la unión puede
> tener una cadena del doble de largo y salir con un número menor. Comparar los cuatro porcentajes
> entre sí mide el tamaño del denominador, no la continuidad. Es la trampa que esta corrida evitó
> a último momento, y conviene que quede escrita.

Lo que sí contesta la pregunta de la fusión es **si la cadena más larga toca las tres subzonas**:

| umbral | cadenas | la mayor junta | Chacarita | F. Lacroze | Colegiales | |
|---:|---:|---:|---:|---:|---:|---|
| 20 m | 558 | 11 (1,2 %) | 11 | 11 | 0 | |
| 40 m | 298 | 27 (3,0 %) | 0 | 0 | 27 | |
| 60 m | 160 | 49 (5,5 %) | 7 | 43 | 4 | las tres |
| 80 m | 102 | 112 (12,6 %) | 0 | 0 | 112 | |
| **120 m** | **31** | **732 (82,2 %)** | **182** | **407** | **411** | **las tres** |

**A 120 metros hay una sola tira de 732 locales que atraviesa las tres.** Ésa es la evidencia
geométrica de que Chacagiales es un objeto y no tres manchas cerca. (Los conteos por subzona suman
más que la cadena porque un local que está en dos subzonas cuenta en las dos.)

**4 · Los tres solapes del nudo se cierran** —60,37 ha · 153 locales, 67,02 · 115 y 6,91 · 21— y
quedan cuatro con otras páginas, que hay que declarar: Palermo 33,15 ha · 111 locales, Villa
Ortúzar 15,93 · 25, Villa Crespo 6,36 · 1 y La Paternal 4,81 · 4.

**5 · El reconocimiento, sin duplicar.** **Nueve establecimientos distintos** adentro del sistema.
Sumando los de cada subzona darían trece: cuatro de más. Los cuatro que caen en dos subzonas son
**Anchoíta**, **Albamonte Ristorante** y el **Café Palacio** (Chacarita y Federico Lacroze) y el
**Bar Conde** (Federico Lacroze y Colegiales). Los nueve, con dirección y subzona, en
`chacagiales_reconocimiento.csv`.

### El atlas queda en 39

41 − 3 + 1. La lista completa con superficie y locales está en `atlas_39_polos.csv`; Chacagiales
entra primero, con 495,82 ha, por delante de Devoto y Villa Urquiza.

---

## 4 · C · Los cuatro sin borde propio · cierran 3 piezas de 9

La regla fue estricta a propósito: **el borde se arma sólo con las calles que el bloque «Dónde
está» de esa página nombra.** Nada más. Si no cierra, la salida es qué calle falta escribir.

| página | cierra | de |
|---|---:|---:|
| Retiro | 2 | 3 |
| Núñez | 1 | 3 |
| Villa Santa Rita | 0 | 1 |
| Colegiales | 0 | 2 |

### Lo que cierra

- **Retiro · el núcleo coreano y asiático — 1,96 ha · 21 locales.** Maipú, Esmeralda, Paraguay y
  M. T. de Alvear se cruzan de a pares y encierran una cara. Es **la única pieza de las cuatro
  páginas que cierra sin agregar nada**, y el control de alturas 800–990 da sobre las cuatro calles.
- **Retiro · el corredor Arroyo — 9,57 ha · 23 locales.** Tramo de 323 m, cuatro manzanas
  frentistas. **Con una libertad declarada:** la página escribe «Plaza Carlos Pellegrini» y el
  borde usa la *calle* Carlos Pellegrini, que Arroyo sí cruza. Es la única de toda la corrida.
- **Núñez · el corredor de Crisólogo Larralde — 23,81 ha · 61 locales.** Tramo de 1.188 m entre
  Av. del Libertador y Av. Cabildo, 22 manzanas frentistas.

Juntas, las dos de Retiro dan **11,53 ha y 44 locales** contra las 467,14 ha que la página publica:
**cuarenta veces más chico, y el 6,2 % de los locales.** Núñez cierra 23,81 de 442,64: dieciocho
veces más chico y el 12,3 %.

### Lo que no cierra, y qué calle falta

| página | pieza | por qué | falta nombrar |
|---|---|---|---|
| Retiro | el núcleo institucional de Plaza San Martín y Florida | una sola calle y una plaza | las dos transversales que acotan el tramo de Florida |
| Núñez | el corredor bajo el viaducto Mitre | no nombra ninguna calle: el viaducto es una traza ferroviaria | las dos calles que flanquean el viaducto |
| Núñez | el núcleo de bistrós en Campos Salles, O'Higgins y Grecia | **O'Higgins y Grecia son paralelas** —corren a 34 m y no se cruzan— y Campos Salles las cruza a las dos: es una U abierta | la transversal que cierra el paño del otro lado de Campos Salles |
| Villa Santa Rita | los puntos dispersos con anclaje en Av. Álvarez Jonte | nombra **una sola calle** en todo el bloque, y encima es el borde del barrio | dos transversales y una paralela interior |
| Colegiales | el eje Concepción Arenal–Zapiola | las dos se cruzan: da una esquina, no una figura, y no escribe hasta dónde | las dos transversales que acotan el eje, o las alturas |
| Colegiales | el Polo Concepción y el Mercado de Pulgas | dos enclaves nombrados por nombre propio | las calles de cada enclave; para el Mercado alcanza con escribir Gral. E. Martínez 50 |

> **Y para Villa Santa Rita la respuesta ya está medida en la parte E de esta misma tanda.** Su
> contorno dibujado corre el 100 % sobre calles y son cinco: Condarco, Av. Gaona, Joaquín V.
> González, Miranda y Av. Álvarez Jonte. La página nombra una de las cinco. Las otras cuatro no
> hay que decidirlas: hay que escribirlas.

---

## 5 · D · La capa de reconocimiento, regenerada

`hitos/hitos_capa_2026.geojson` pasa de **215 a 220 filas**, regenerada desde la canónica
`hitos_capa_2026_r11.csv`. La versión anterior queda entera en
`ronda_21/geometria/hitos_capa_2026_ANTES_DE_LA_RONDA_21.geojson`.

**Entran cinco** —Gran Café Gardel, Centro Asturiano, Centro Laurak Bat, Casal de Catalunya y el
**Bar Iberia**—, **no sale ninguno**, y **dos cambian de punto**: el Café Roma / Roma del Abasto,
que se corrige 6.142 metros, y La Academia, que se muda 278.

Las cinco filas nuevas no traen las cinco columnas de auditoría que la capa vieja tenía y la
canónica no. En vez de rellenarlas con «sin_conflicto_declarado» —que sería inventar un veredicto
que nadie dio— quedan marcadas **`no_auditado_en_r18`**.

`hitos/hitos_capa_2026.csv` **no se toca**: es la entrada de la cadena que produjo r3 → … → r11 y
pisarla con la salida de esa misma cadena la volvería irreproducible.

### Las cuentas · las dos correcciones a mano se confirman, y no hay más

Contra los bordes publicados hoy, **cambian tres páginas de 41**:

| polo | página | vieja | nueva | qué cambia |
|---|---|---:|---:|---|
| R12 | Centro y Microcentro | 21 | **22** | entra el Bar Iberia |
| Z47 | Monserrat y Congreso | 5 | **6** | entra el Bar Iberia |
| Z52 | La Boca · Almirante Brown y Necochea | 4 | **3** | sale el Café Roma duplicado |

> **Las dos que corregiste a mano dan exacto y no hay ninguna más.** La tercera es Monserrat, y
> es el mismo Bar Iberia: está en Av. de Mayo 1196, o sea adentro del solape que las dos páginas
> comparten. Hoy lo cuentan las dos.
>
> El total de lugares con reconocimiento adentro de algún borde **no se mueve: 137 antes y 137
> ahora.** Entra uno y sale uno, y son distintos.

### Y una advertencia para cuando apliques los repartos

**El «22» del Microcentro vale para el borde de hoy.** Con los cinco repartos y la fusión
aplicados, la misma capa da otra cosa, porque el Bar Iberia queda del lado de Monserrat:

| polo | página | hoy | después | qué se mueve |
|---|---|---:|---:|---|
| R12 | Centro y Microcentro | 22 | **14** | −8, entre ellos el Bar Iberia |
| Z46 | Retiro | 11 | **7** | −4 |
| Z37 | Almagro | 5 | **2** | −3 |

Ninguno de esos quince se pierde: los cuentan las páginas que se quedan con la superficie. Lo que
se termina es la doble cuenta.

---

## 6 · E · Las calles de los 23, listas para escribir

De cada contorno dibujado salen los tramos de calle **en orden de recorrido**, con el rango de
alturas de la cuadra donde empieza y donde termina. **2.279 tramos** en total, en
`calles_de_los_23.csv`. No escribí el texto: están las calles y las alturas.

**El número que decide si una página se puede escribir de corrido es cuánto del contorno corre
sobre alguna calle**, y va publicado:

| se escribe fácil (100 %, pocos tramos) | contorno | tramos |
|---|---:|---:|
| La Boca · Caminito y Vuelta de Rocha | 934 m | **5** |
| Villa Santa Rita | 5.759 m | **5** |
| Mataderos | 3.313 m | **9** |
| Colegiales | 6.376 m | **10** |
| Parque Avellaneda | 4.200 m | **13** |

La Boca · Caminito, entera y en orden: Gregorio Araoz de Lamadrid del 600 al 800 · Palos 800 ·
Av. Don Pedro de Mendoza del 1800 al 2000 · Rocha 800 · Garibaldi del 1400 al 1600.

Y el otro extremo, que es un hallazgo y no una falla del método:

> **Av. Corrientes tiene el 40 % del contorno sobre calles y sus 30 tramos miden todos entre 32 y
> 48 metros**, sobre treinta calles transversales distintas —Riobamba, Sarmiento, Lavalle,
> Callao, Rodríguez Peña, Montevideo, Paraná…—. Eso no es un perímetro de calles: es la firma
> geométrica de un corredor. Su contorno son las manzanas frentistas del eje, así que lo que lo
> bordea es **el fondo de las manzanas**, y las calles sólo aparecen donde el contorno cruza una
> bocacalle. **Esta página no se escribe listando calles: se escribe nombrando el eje y sus dos
> extremos**, que es justamente lo que su bloque declara pendiente —«el tramo exacto está por
> precisar»—.

El Microcentro es el segundo caso más bajo (55 %) y por el mismo motivo parcial. Las veintiuna
restantes están entre 65 y 100 %.

---

## 7 · F · El fin de línea

**`.gitattributes` escrito** en la raíz: `* text=auto`, el texto del proyecto declarado por
extensión, `.ps1/.bat/.cmd` con CRLF fijo, `.sh` con LF fijo, y **lo binario marcado a mano**
—png, pdf, docx, xlsx, shapefile, fuentes— en vez de confiar en la detección automática, porque un
`.docx` normalizado se corrompe y el daño no se ve hasta que alguien lo abre. Verificado con
`git check-attr`: el `.docx` del Atlas y el PDF salen `binary: set`, los `.py` y `.geojson` salen
`text: set`.

**El `git add --renormalize .` no se pudo correr.** Hay un `.git/index.lock` de las 22:32 y cuatro
procesos `git.exe` vivos. Borrar un lock mientras otro proceso escribe el índice lo corrompe, así
que no lo toqué. Cuando cierres lo que esté abierto:

```powershell
Remove-Item .git\index.lock -ErrorAction SilentlyContinue
git add --renormalize .
```

**Y una precisión sobre el diagnóstico:** en este momento no hay 30 archivos con sólo el fin de
línea cambiado. Hay **ocho archivos modificados**, y **siete tienen cambios de contenido reales**
—el ATLAS_V3_DOCUMENTO.md con 57 líneas nuevas y 28 borradas, el CRITERIO_DE_ADMISION con 28
nuevas, las dos secciones VII, el ANEXO_B, el `cuantos_y_juntos.csv` y el `.docx`—; el octavo es
la capa de reconocimiento que regeneré yo. El diff ignorando los CR da lo mismo que el diff normal
en los siete. **`--renormalize` implica `-u`, así que no va a agregar nada sin seguir, pero sí va
a dejar en el índice esos siete cambios de contenido.** Miralos antes de commitear.

Lo que sí es cierto es la causa: `core.autocrlf=true` sin `.gitattributes` es exactamente la
configuración que produce ese ruido. El archivo lo apaga de acá en adelante.

---

## 8 · Lo que no se pudo resolver, y por qué

1. **El `git add --renormalize .` quedó pendiente por el lock del índice.** Es lo único de la
   tanda que no corrió, y no corrió por prudencia, no por un error.
2. **La orientación de Warnes contradice la frase de la decisión.** «Al este es de Villa Crespo»
   nombra un flanco que un eje este-sudeste a oeste-noroeste no tiene. Apliqué el reparto que la
   masa propia de cada polo sostiene —y que da igual a cinco radios— y dejé **la variante espejo
   medida** para que la decisión cueste una firma y no una ronda.
3. **La Paternal se queda con 34 hectáreas adentro del barrio Villa Crespo.** No es del corte: el
   polígono de R21 ya metía 69 ha en Villa Crespo y 12 en Caballito antes de esta ronda. El corte
   lo hace visible. Vale la pena decidir si el borde de R21 se revisa, y eso no es esta ronda.
4. **La cuenta del Microcentro cambia dos veces.** 21 → 22 por la capa regenerada, y 22 → 14 por
   los repartos. Las dos son correctas y son de momentos distintos; la página tiene que publicar
   la del borde que publique.
5. **Villa Santa Rita y Colegiales no cierran ninguna pieza con lo que sus páginas escriben.** Lo
   que falta está listado calle por calle, y para Villa Santa Rita las cuatro que faltan ya están
   medidas en la parte E.
6. **Ninguno de los tres bordes que sí cierran se adopta.** Están las dos superficies, los dos
   conteos y la procedencia de cada extensión; la firma no.
7. **Los 2.279 tramos de la parte E no son 23 perímetros escribibles.** Cuatro páginas salen con
   diez tramos o menos y se escriben de corrido; las otras diecinueve tienen contornos que doblan
   mucho, y R19 sale con 165 tramos. Para ésas la lista es material de trabajo, no un borrador de
   párrafo.
8. **`hitos/hitos_capa_2026.csv` sigue desfasado de la canónica.** Se declara y no se toca, por lo
   dicho arriba. Quien lo use tiene que saber que la capa buena es la r11 y la que leen las
   páginas es el `.geojson`.

---

## Archivos de esta carpeta

| archivo | qué es |
|---|---|
| `repartos_cifras_finales.csv` | **lo que va a las páginas**: las ocho, antes y después |
| `repartos_cifras.csv` | los cinco repartos, reparto por reparto |
| `repartos_locales_que_cambian.csv` | los 702 locales que cambian de página, uno por uno |
| `repartos_orientacion_de_los_cortes.csv` | los dos cortes: rumbo, nomenclador, barrios de cada mitad |
| `chacagiales_cifras.csv` · `chacagiales_reconocimiento.csv` | el sistema, sus tres subzonas y sus nueve establecimientos |
| `chacagiales_solapes_que_quedan.csv` | los cuatro solapes que quedan después de fundir |
| `atlas_39_polos.csv` | la lista completa del atlas después de la fusión |
| `bordes_de_los_cuatro.csv` | las 9 piezas: 3 que cierran y 6 con la calle que falta |
| `bordes_de_los_cuatro_calles.csv` | qué nombra cada página y cuáles son calles de verdad |
| `reconocimiento_cuentas.csv` · `reconocimiento_diff_de_la_capa.csv` | las cuentas de las 41 y el diff de la capa |
| `calles_de_los_23.csv` | los 2.279 tramos, en orden, con alturas |
| `calles_de_los_23_resumen.csv` | cuánto del contorno de cada página corre sobre calles |
| `geometria/bordes_repartidos_41.geojson` | la geometría después de los cinco repartos |
| `geometria/bordes_39.geojson` · `geometria/chacagiales.geojson` | el atlas fundido, y el sistema con sus subzonas |
| `geometria/bordes_de_los_cuatro.geojson` | las tres piezas que cierran |
| `geometria/hitos_capa_2026_ANTES_DE_LA_RONDA_21.geojson` | la capa de reconocimiento anterior, entera |
| `REPARTOS.txt` · `CHACAGIALES.txt` · `BORDES_DE_LOS_CUATRO.txt` · `CAPA_RECONOCIMIENTO.txt` · `CALLES_DE_LOS_23.txt` | la salida completa de cada corrida |
| `repartos_21.py` · `chacagiales_21.py` · `bordes_de_los_cuatro.py` · `capa_reconocimiento_21.py` · `calles_de_los_23.py` | los scripts, en ese orden |
