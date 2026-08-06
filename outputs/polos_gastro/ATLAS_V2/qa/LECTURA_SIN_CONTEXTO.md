# Lectura sin contexto — edición editable (.docx) del Atlas

Registro de la lectura completa del documento, hecha desde el lugar de quien lo recibe: una
persona con experiencia y criterio que no trabajó en esto, no conoce el proyecto, lo va a
leer una sola vez y no le va a preguntar nada a nadie.

En cada página se preguntó lo mismo: ¿entiendo esta frase sin releerla?, ¿sé qué me dicen y
para qué?, ¿hay alguna palabra que yo no usaría en una conversación?, ¿qué podría
malinterpretar?

**Regla de todas las correcciones:** cambia *cómo* se dice, nunca *qué* se dice. Ninguna
cifra se movió, ninguna salvedad desapareció, ninguna geometría se tocó. Lo verifican los
controles `diff_de_cifras_contra_conduccion` (0 diferencias sin declarar sobre 49 frases
reescritas) y `cifra_de_cada_zona_en_ficha_y_tabla` (22/22).

Las páginas que se citan son las del documento nuevo, de 62 páginas.

---

## Parte 1 · Las tres correcciones pedidas

| Id | Qué era | Qué se hizo |
|---|---|---|
| **C-01** | «absorba», en la lista de términos vigilados, dentro del texto de «Cómo se construyeron las zonas». | La frase quedó: «Donde dos zonas vecinas quedaban superpuestas, el área se repartió entre ambas para que ninguna quede contenida dentro de la otra, respetando las separaciones que la Dirección definió». Se vació la lista de excepciones declaradas del control: `vocabulario_conduccion` ya no informa OBSERVADO, informa **PASS, sin hallazgos sobre 29 términos vigilados**. El mecanismo de excepciones sigue en el código, vacío, por si la Dirección autoriza otra en el futuro. |
| **C-02** | `word/settings.xml` traía `<w:zoom w:val="bestFit"/>` sin `w:percent`, que el esquema declara requerido. Venía de la plantilla de `python-docx`. | Se completa con `w:percent="100"` al escribir el archivo (`corregir_settings`). Y se sumó al QA una **validación contra esquema XSD**, no sólo de orden: `esquema_xsd_ooxml`. Ver abajo. |
| **C-03** | La tabla «Las 22 zonas de un vistazo» decía «Cada fila remite a la ficha de su zona» y no había a qué remitir. | Frase eliminada. El subtítulo quedó en «Tabla de consulta rápida.» (El pie de la tabla sigue diciendo que la ficha de cada zona explica qué cuenta su número: eso es cierto y no promete una página.) |

### Sobre la validación XSD (C-02)

El control viejo, `xml_en_secuencia_ooxml`, sólo miraba el **orden** de los hijos de `w:tblPr`
y `w:tblBorders`. Por eso no vio el defecto: un atributo requerido que falta no es un
problema de orden.

El control nuevo valida cada parte XML del paquete contra los esquemas de `qa/esquema/`,
con el preproceso de compatibilidad (`mc:Ignorable`) que aplica cualquier lector conforme
antes de mirar el contenido. **16 partes válidas, 209 elementos distintos cubiertos.**

Dos aclaraciones que corresponde dejar por escrito:

- La distribución oficial de esquemas de ECMA-376 no está en esta máquina y el generador
  corre sin red, así que **el esquema es propio**, escrito para el subconjunto que este
  documento usa de verdad. Declara el contrato de atributos de cada elemento —cuáles
  admite, cuáles exige, de qué tipo son— y **lo que no está declarado no valida**: si el
  generador emitiera mañana un elemento o un atributo nuevo, el control falla, no lo ignora.
  El modelo de contenido usa `xs:choice`, así que valida *qué* hijos puede tener cada
  elemento y no en qué orden: el orden lo sigue cubriendo el control viejo, y los dos son
  complementarios a propósito.
- Quedan fuera del alcance dos partes, `word/theme/theme1.xml` (tema DrawingML) y
  `customXml/item1.xml` (XML propio, sin esquema declarado). Las dos llegan intactas desde
  la plantilla de `python-docx`, y el control **lo comprueba byte a byte**: la exclusión no
  esconde nada escrito por este generador.

Se verificó que el control detecta lo que tiene que detectar, inyectando defectos a mano:
`w:zoom` sin `w:percent` (el caso real), un atributo inventado, un elemento inventado,
`w:color` sin `w:val`, un color fuera de dominio, `w:pgMar` sin `w:gutter`. Los seis dan
error de validación.

---

## Parte 2 · Índice y números de página

Pedido posterior, incorporado a esta misma versión:

- **Número de página abajo a la derecha**, en todas las páginas menos la portada. Es un
  campo `PAGE` de Word con resultado en caché: Word lo recalcula al abrir y al imprimir, y
  mientras tanto se ve un número igual. La portada no lleva folio (primera página distinta).
- **Índice después de la portada**, en la página 2: las ocho secciones y las 22 zonas, con
  guía de puntos y la página de cada una. Los folios **no son texto puesto a mano**: la
  paginación se calcula, se arma el índice, se vuelve a paginar y se repite hasta que los
  números dejan de moverse. El control `indice_con_folios_reales` los verifica uno por uno
  contra la página donde el título está de verdad (30 de 30).

Esto cambia algo de lo dicho en C-03: ahora sí hay índice y hay folios. La frase de la
tabla no se repone igual, porque la tabla sigue sin números de página propios; quien busque
una zona la encuentra en el índice.

**Advertencia que conviene que Jefatura conozca:** el índice es texto fijo. Si alguien edita
el documento y la paginación se corre, los números del índice quedan viejos hasta que se
regenere el archivo, o hasta que se reemplace el índice por uno automático desde
*Referencias → Tabla de contenido* (los títulos llevan los estilos Título 1 y 2 de Word, así
que se genera solo). Por el mismo motivo, en el cuerpo del texto no se dejó ninguna
referencia del tipo «ver página 6».

---

## Parte 3 · Hallazgos de la lectura

49 frases reescritas, 70 apariciones en el documento. Agrupadas por hallazgo:

### Lo que no se entendía sin conocer el proyecto

| Id | Pág. | Qué no se entendía | Qué se cambió |
|---|---|---|---|
| L-01 | 1 | El subtítulo de tapa, «22 lecturas territoriales y cartográficas», no le dice nada a quien abre el documento por primera vez. | «22 zonas gastronómicas de la Ciudad, descriptas y mapeadas una por una». |
| L-02 | 1 | El rótulo «Lectura institucional» no anuncia nada, y debajo «Las categorías, cifras y métodos no se convierten en un ranking general» obliga a releer. | Rótulo: «Qué es este Atlas». Texto: «Son veintidós zonas distintas entre sí, reunidas en un mismo documento. Ni sus categorías ni sus cifras forman un ranking, y no son veintidós polos equivalentes». |
| L-03 | 1 | «Representación cartográfica analítica · no oficial», en naranja al pie de la tapa: la advertencia más visible del documento estaba escrita en el idioma del proyecto. | «Los mapas sirven para ubicar la oferta: no son planos oficiales». (También en las propiedades del archivo.) |
| L-04 | 1, 3 | «Fuente: relevamiento **propio** de la Dirección» — y tres páginas después el Atlas dice que en varias zonas se usó un directorio comercial en línea. Un lector atento ve la contradicción; uno desatento se lleva una atribución equivocada. | «Fuente: relevamiento de la Dirección General de Desarrollo Gastronómico, **con la información disponible para cada zona**». Es lo que ya dice la página 62 sobre el método. |
| L-05 | 3 | «Los números de un grupo no se pueden **poner al lado** de los de otro» decía dos cosas mal: el rodeo «poner al lado» (para esquivar una palabra vigilada), y que la restricción fuera entre grupos, cuando las páginas 4, 5, 61 y 62 dicen que no se comparan **entre zonas**, punto. | «Cada zona se relevó de una manera distinta, y los grupos reúnen a las que se relevaron parecido. Por eso un número más alto no significa más oferta que en otra zona, y los números no se suman entre sí». |
| L-06 | 3 | «Caballito 907 · Villa Crespo 646 · …»: números sin unidad. 907 ¿qué? | Se agrega «locales» al primero de cada línea. |
| L-07 | 3 | El grupo «Zonas sin conteo propio» listaba cinco zonas y en la nota aparecían dos más, con «697 y 72» al final sin decir cuál era de cuál. | «Están descriptas y ubicadas, sin un número propio. Belgrano y Costanera Norte tampoco tienen conteo propio: solo hay datos de un relevamiento anterior (Belgrano, 697 locales; Costanera Norte, 72)». |
| L-08 | 3 | «El mapa de la página 6 ubica las 22 zonas»: no había números de página impresos, así que no se podía seguir; y es un archivo editable, donde la paginación se corre. | «El mapa general, unas páginas más adelante, ubica las 22 zonas en la Ciudad». Es la única diferencia numérica declarada del diff de cifras: un número de navegación, no una cifra del Atlas. |
| L-09 | 4 | El título «Qué no dice este dato» — ¿cuál dato? | «Qué no dicen estos números». |
| L-10 | 6 | **Los códigos R01 a R22.** Encabezan cada ficha, cada mapa y cada fila de la tabla, y no se explicaban en ninguna parte. Para alguien de afuera son una sigla sin significado, y la numeración sugiere un orden de importancia que el Atlas niega en otras cinco páginas. | Una línea donde aparecen por primera vez: «Cada zona lleva además un código, de R01 a R22, para poder nombrarla y encontrarla: es una referencia, no un orden de importancia». Y en la tabla final, la columna «Ref.» pasó a llamarse «Código». |
| L-11 | 6 | **Los nombres de las familias.** Las cinco definiciones estaban escritas desde adentro del trabajo: «Concentración reconocible en torno de un área» (una concentración alrededor de un área no significa nada), «Un polo que se lee en partes separadas», «Un área que solo se puede leer por partes independientes entre sí», «Oferta presente y documentada, sin un centro único demostrado». | Definiciones nuevas: «Una concentración de oferta reconocible, con identidad propia»; «Un polo formado por partes separadas, que el Atlas muestra separadas porque así están en el territorio»; «No funciona como un solo lugar: son varias áreas vecinas que conviene mirar por separado»; «Hay oferta comprobada, pero repartida: no se encontró un centro que la organice». La de «eje o corredor» ya se entendía sola y no se tocó. |
| L-12 | 8–60 | **«Zona caracterizada, sin conteo propio»**, en el lugar donde las otras zonas muestran un número, en las cinco zonas sin cifra y en sus cinco filas de la tabla. «Caracterizada» no es una palabra de conversación, y la frase se lee como una excusa: dice primero lo que falta. | «Descripta y ubicada, sin conteo de locales». Dice primero lo que sí se hizo. |
| L-13 | 8–60 | «Trazo punteado: es el área **con que se consultó** la zona, no el contorno de la oferta encontrada», ocho veces en el documento. | «Trazo punteado: marca el área dentro de la cual se buscó, no la forma de la oferta encontrada». |
| L-14 | 16, 18, 19, 32, 34, 38, 43 | «**La lectura** no se extiende a…», usado como sujeto en seis zonas: es jerga interna disfrazada de castellano. El lector cree entender y en realidad se le nombra un objeto del proyecto. | «Esta zona no abarca…», «La zona no llega a…», «Parque Rivadavia quedó fuera de la zona». |
| L-15 | 20, 21 | Belgrano nombra sus tres centros de una manera en la ficha (Barrio Chino, Bajo Belgrano, Belgrano R) y el mapa de la página siguiente los rotula de otra (Barrio Chino–Belgrano C, Cabildo–Juramento, Belgrano R). Son los mismos tres lugares, con dos juegos de nombres en páginas enfrentadas. | La ficha dice los dos: «Barrio Chino (en el mapa, Barrio Chino–Belgrano C), Bajo Belgrano (Cabildo–Juramento) y Belgrano R». No se renombró nada: los dos nombres ya estaban en el corpus. |
| L-16 | 20 | «Los tres funcionan dentro de una misma zona y **con pesos distintos**». | «…y no todos con la misma importancia». |
| L-17 | 22 | «Un relevamiento anterior dejó **datos de trabajo** sobre Recoleta, pero no un número **publicable**». | «…dejó datos sobre Recoleta, pero no un número que pueda publicarse para toda la zona». |
| L-18 | 29–32 | «El mapa dibuja los dos focos, **que no cubren la totalidad de lo relevado**»: la frase es correcta y no se entiende de una lectura. | «El mapa dibuja los dos focos; parte de los locales relevados queda fuera de ellos». Igual para los dos núcleos de Caballito. |
| L-19 | 31 | «El Patio de los Lecheros se miró como **punto de control**» y «Parque Rivadavia salió de la **lectura vigente** y no se vuelve a usar». | «…se revisó y quedó fuera de la zona»; «Parque Rivadavia se descartó y ya no forma parte de esta zona». |
| L-20 | 33 | «47 de los locales quedaron a menos de 250 metros **del eje**: no la prueba de una avenida continua» — «el eje» no se nombró antes. | «47 de esos locales están a menos de 250 metros del boulevard: es una descripción, no la prueba de que la oferta sea continua». |
| L-21 | 35 | «Tribunales se lee aparte y con **menos respaldo** que las demás». | «Tribunales se mira aparte y con menos información que las demás». |
| L-22 | 47, 48 | «El mapa ubica el de Triunvirato, el único con **recorrido cerrado en el material disponible**». | «El mapa dibuja el de Triunvirato, el único del que se tiene el recorrido completo; Monroe y Congreso aparecen sólo como calles de referencia». |
| L-23 | 49, 50 | «La mayor cantidad de locales no está en el centro del círculo sino en las **bandas intermedias**». Y, peor: «El círculo de 400 metros es **el radio** con que se consultó la zona, **no un centro demostrado**» — la frase niega una cosa distinta de la que nombra: un radio no es un centro. | «La mayor cantidad de locales no está junto al cruce, sino entre 100 y 300 metros de distancia»; «El círculo de 400 metros marca hasta dónde se buscó alrededor del cruce; no significa que la zona tenga ahí su centro». |
| L-24 | 18, 19 | «sobre **dos frentes enfrentados**»; y en el pie del mapa, «descontado con cartografía pública **de acceso abierto** verificada contra la **capa oficial** de cuerpos de agua». | «sobre las dos orillas enfrentadas»; «El área deja afuera el agua de los cuatro diques, descontada con cartografía pública verificada contra el mapa oficial de cuerpos de agua de la Ciudad». |
| L-25 | 57 | «No hay un centro, un corredor ni **una red de puntos** demostrados». | «No se encontró un centro, un corredor ni un conjunto de puntos vinculados entre sí». |
| L-26 | 59, 60 | «El contorno del mapa es el **marco con que se relevó** el barrio». | «…es el recuadro dentro del cual se buscó en el barrio, no un área gastronómica». |
| L-27 | 3 | «No hay zonas identificadas en el **sur profundo** de la Ciudad». | «No se identificaron zonas en el extremo sur de la Ciudad». |

### Lo que se podía malinterpretar

| Id | Pág. | Qué lectura equivocada admitía | Qué se cambió |
|---|---|---|---|
| **M-01** | 51, 52, 54, 57, 58, 59 | **La más importante.** «Al menos 254 locales» y, debajo, «Al momento del relevamiento, 242 estaban abiertos y 12 cerrados de forma temporaria»: 242 + 12 = 254 exactos. Leído de corrido, el detalle parece desmentir el «al menos» —si el número es un mínimo, ¿por qué el desglose cierra justo?—. Pasa en las cuatro zonas con estado de apertura: R19, R20, R21 y R22. | Se dice de quiénes es el desglose: «**De los locales relevados**, 242 estaban abiertos y 12 cerrados de forma temporaria al momento del relevamiento». El «al menos» sigue en pie y ningún número se movió. |
| **M-02** | 54 | García del Río lleva el rótulo **«Eje o corredor»** arriba de la página, y tres líneas más abajo dice «No alcanza para hablar de un corredor, un eje ni un polo». Para quien no leyó la página 6 con atención, es una contradicción en la misma página. | «No alcanza para hablar de un corredor, un eje ni un polo **consolidados**: la familia describe cómo se ordena la oferta, no su tamaño ni su importancia». La salvedad queda entera; se agrega la explicación que la página 6 ya da. |
| **M-03** | 3 | Ver L-05: el resumen sugería que dentro de un mismo grupo los números sí se comparan. | Corregido en L-05. |
| **M-04** | 1 | Ver L-04: la tapa atribuía todo a relevamiento propio. | Corregido en L-04. |

### Lo que se revisó y se dejó como estaba

| Id | Pág. | Qué se miró | Por qué no se tocó |
|---|---|---|---|
| N-01 | 3, 4, 8–60 | **«Al menos»**, que era una de las dudas explícitas. | Está bien resuelto y no hacía falta cambiar nada. Se explica en su primera aparición (p. 3: «Zonas con un mínimo relevado (se leen con «al menos»)» + «Puede haber más locales, nunca menos»), otra vez en «Cómo se construyeron las zonas», otra en «Cómo leer el Atlas», y cada ficha que lo usa lleva debajo «Es un mínimo: puede haber más, no menos». Ninguna zona con «al menos» obliga a ir a buscar la explicación a otra página. |
| N-02 | 8–60 | **Los pies de los 31 mapas.** «Qué muestra este mapa / Qué mide la cifra / Qué no es» se repiten 31 veces cada uno. | No sobran las 31, pero tampoco aportan las 31 (ver la lista final). Sacar cualquiera de esas líneas es sacar una salvedad, y eso está fuera de lo permitido. Se mejoró la redacción de las que además eran confusas (L-13, L-18, L-22, L-23, L-24, L-26). |
| N-03 | 26 | **R08 Villa Crespo dice «646 locales relevados», sin «al menos»**, y tres líneas más abajo dice que «en tres puntos el relevamiento llegó a su tope y no pudo seguir contando: ahí puede haber más locales». Con la regla que el propio Atlas enseña en la página 4, ese número debería leerse como un mínimo. | Cambiar la frase de cifra de R08 es cambiar **qué** se dice, no cómo: es una decisión de método, no de redacción. La ficha ya avisa que en tres puntos puede haber más, y el mapa ampliado de la página 28 muestra dónde. Queda anotado como límite del documento. |
| N-04 | 38 | **R13 Abasto: los tres tramos «al menos 91, 115 y 108» suman exactamente 314**, que es el total de la zona. En R19, en cambio, los dos tramos explícitamente no se suman (comparten 39 locales). El lector que haga la cuenta en las dos zonas se encuentra con dos reglas distintas y ninguna explicación. | Decir por qué en un caso suman y en el otro no exige información que el documento no trae (si los tres tramos de Abasto comparten locales o no). Inventarla está prohibido. Queda anotado como límite del documento. |
| N-05 | 4, 5 | **El orden.** «Cómo se construyeron las zonas» (p. 4) y «Cómo leer el Atlas» (p. 5) dicen casi lo mismo, una atrás de la otra: que los números no se comparan, que las áreas no son límites oficiales, que el tamaño del área no mide cantidad de oferta. Y la página 62 lo dice una tercera vez. | Fusionar o mover secciones es cambiar la estructura, que está fuera de lo permitido. Al mapa de la Ciudad se llega en la página 7 de 62, que no es tarde; lo que pasa es que las páginas 4 y 5 se sienten más largas de lo que son porque repiten. Con el índice nuevo, además, se puede saltear. |
| N-06 | 42 | La ficha de Devoto no dice que su número salga de un directorio comercial en línea; eso sólo se sabe por el agrupamiento de la página 3. Lo mismo con las otras tres zonas de ese grupo. | Agregarlo ficha por ficha es agregar contenido, no cambiar redacción. El resumen y la página 62 lo dicen. |
| N-07 | 35, 61 | El nombre de la zona R12 es «Centro/Microcentro segmentado»: la barra y la palabra «segmentado» son de nuestro vocabulario, y en la tabla el nombre se parte en dos renglones. | Renombrar una zona es una decisión territorial, no de redacción. |
| N-08 | 8–60 | El espacio en blanco al pie de algunas páginas. | Indicado expresamente: no se toca. Es consecuencia de un elemento por página con mapas de proporciones distintas. |

---

## Las tres listas

### 1 · Qué mejoró

- **Los códigos R01–R22 ya se explican** la primera vez que aparecen, y dejan de sugerir un
  orden de importancia.
- **Las cinco familias tienen definiciones que se entienden solas**, escritas con lo que el
  propio Atlas dice en las fichas de cada una.
- **Desapareció la contradicción de García del Río** entre el rótulo de la zona y su
  salvedad, sin perder ni el rótulo ni la salvedad.
- **El desglose de abiertos y cerrados dejó de parecer que desmiente al «al menos»** en las
  cuatro zonas donde aparece.
- **La tapa dejó de atribuir todo a relevamiento propio**, que el propio documento
  desmentía tres páginas después.
- **Se fue la jerga que se había escapado de la lista vigilada**: «caracterizada»,
  «la lectura» como sujeto, «punto de control», «recorrido cerrado», «bandas intermedias»,
  «área con que se consultó», «marco con que se relevó», «datos de trabajo»,
  «número publicable», «menos respaldo», «pesos distintos», «red de puntos»,
  «frentes enfrentados», «sur profundo», «representación cartográfica analítica».
- **Belgrano nombra sus tres centros de una sola manera** en la ficha y en el mapa.
- **El documento se puede recorrer**: índice con las 30 entradas y su página, y folio abajo
  a la derecha en las 61 páginas que no son la portada.
- **El archivo quedó sin ninguna falla de validación**: cero términos vigilados, y el XML
  válido contra esquema, no sólo ordenado.

### 2 · Qué quedó igual porque no se podía arreglar sin inventar

- **R08 Villa Crespo publica 646 sin «al menos»** aunque su propia ficha diga que en tres
  puntos el relevamiento se cortó (N-03). Corregirlo es una decisión de método.
- **R13 Abasto: sus tres tramos suman el total exacto y R19 no.** Explicar la diferencia
  pide saber si los tramos de Abasto comparten locales, y el documento no lo dice (N-04).
- **Qué zonas salieron del directorio comercial en línea no se puede saber ficha por ficha**,
  sólo por el agrupamiento del resumen (N-06).
- **«Centro/Microcentro segmentado» sigue siendo un nombre nuestro** (N-07).
- **Las repeticiones de las páginas 4, 5 y 62** siguen ahí: sacarlas es sacar salvedades o
  cambiar la estructura (N-05).

### 3 · Qué sigue siendo difícil de entender aunque ya no se pueda mejorar desde el texto

Esta es la lista que conviene tener presente antes de que el documento llegue a destino.

1. **La advertencia se vuelve ruido, y es el riesgo más serio del documento.** «No es un
   límite oficial» aparece en la tapa, en «Cómo leer», en el cierre de cada una de las 22
   fichas, en el «Qué no es» de cada uno de los 31 mapas y en el descargo al pie de esos
   mismos 31 mapas: más de cincuenta veces, y dos veces en la misma página cada vez que hay
   un mapa. A partir de la tercera o cuarta zona el ojo la saltea entera — y con ella se
   saltea la parte específica de esa zona, que va pegada atrás en la misma línea. La
   salvedad más repetida del Atlas es, por repetida, la que menos se lee. No se puede
   arreglar quitando texto sin quitar salvedades; se arregla el día que se decida decirla
   una vez, fuerte, y no cincuenta veces flojas.
2. **Tres mapas seguidos de Palermo dicen casi lo mismo** (páginas 9, 10 y 11): mismo «Qué
   mide la cifra», y un «Qué no es» que sólo cambia el nombre de la parte. Es el punto donde
   el trío del pie se agota más rápido.
3. **Que los números no se comparen entre zonas es, para el lector, la afirmación más rara
   del documento**, y el documento la sostiene bien pero nunca la vuelve intuitiva: hay 22
   números en una misma tabla, ordenados uno debajo del otro, y decirle a alguien que no los
   mire juntos va contra lo que la tabla misma invita a hacer. Es un límite de la forma
   «tabla», no de la redacción.
4. **«Zona caracterizada» se arregló, pero cinco zonas siguen sin número.** Palermo, San
   Telmo, Puerto Madero, Recoleta y Corrientes son, para cualquiera, las zonas más obvias de
   la Ciudad, y son justo las que no traen cifra. El documento lo explica bien; aun así, la
   primera reacción de quien lo lea va a ser «¿y Palermo cuántos tiene?». Conviene tener la
   respuesta preparada para esa pregunta, porque va a llegar.
5. **El índice es texto fijo.** Es un documento pensado para editarse, y en cuanto se edite
   los folios del índice envejecen. Está explicado más arriba: o se regenera el archivo, o
   se reemplaza por una tabla de contenido automática de Word.
6. **La paginación del `.docx` se calculó, no se abrió en Word.** En esta máquina no hay
   Word ni LibreOffice. La prueba de paginación (`..._DOCX.pdf`) se dibuja desde el mismo
   modelo, con la misma tipografía y las mismas cajas, y cada página está delimitada por un
   salto explícito, así que no debería moverse. Aun así, conviene abrirlo una vez en Word
   antes de circularlo.

---

Generado por `scripts/build_atlas_docx.py`. Los controles automáticos están en
`qa/QA_EDICION_DOCX.csv` (22 controles, 22 PASS) y los esquemas de validación en
`qa/esquema/`.
