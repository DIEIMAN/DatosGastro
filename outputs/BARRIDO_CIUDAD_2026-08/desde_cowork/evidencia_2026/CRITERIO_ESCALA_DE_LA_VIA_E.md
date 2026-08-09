# La vía E no se mide por fila

*Decisión de criterio · 7 de agosto de 2026 · con la vía E ya asignada a las 94 filas*

Quedaba propagar la vía E de las 22 referencias al resto de la matriz. Al abrir las 94 filas apareció un problema de escala que hay que resolver antes de investigar nada más: **más de la mitad de las filas no son zonas.**

---

## Las 94 filas son tres cosas distintas

| familia | qué es | cuántas |
|---|---|---|
| `PG###` | las referencias publicadas, algunas partidas en subzonas (Palermo en tres, Belgrano en tres) | 26 |
| `PGF2_` | barrios administrativos completos | 6 |
| `PGR_P###` | fragmentos que produjo el clustering | 62 |

Un fragmento como `PGR_P058 · Flores`, de 53 locales, **no es un lugar del que alguien escriba**. No existe prensa sobre un polígono de 53 locales sin nombre. La vía E pregunta si alguien de afuera trató a un lugar como destino, y para eso el lugar tiene que ser nombrable. Un fragmento del clustering no lo es.

Salir a buscar la vía E de las 72 filas restantes, una por una, habría sido buscar algo que por construcción no existe. **Eso era el error que estaba a punto de cometer.**

---

## La regla

**La vía E se mide a nivel de zona y las filas la heredan.** Se agrega el campo `via_E_modo`:

| valor | qué significa |
|---|---|
| `propia` | la fila coincide con la zona que se midió |
| `heredada` | la fila es un fragmento o una subzona de una zona medida; hereda su resultado |
| `requiere_cruce` | el barrio de la fila tiene **más de una zona con resultados distintos**: no se puede heredar sin geometría |

**Un fragmento nunca abre la vía E por sí solo. Solo puede heredarla.**

Y de ahí sale la consecuencia práctica que importa: **la vía E se guarda como referencia a la zona, no como valor copiado.** Si se copia el valor y mañana se vuelve a correr el clustering, los 58 fragmentos quedan con un `sí` huérfano que ya no apunta a nada y nadie se entera. Guardando `zona_via_E` más `via_E_modo`, un cambio de geometría rompe visiblemente, que es lo que uno quiere que pase.

---

## Cómo quedaron las 94

| | filas |
|---|---|
| vía E **abierta** | 57 |
| vía E **cerrada** | 22 |
| `requiere_cruce` | 10 |
| pendientes de la ronda del sur | 4 |
| a revisar | 1 |

Por modo: **25 propias, 58 heredadas, 10 que requieren cruce geométrico, 1 a revisar.**

Archivo: `via_E_94_filas.csv`, con `zona_via_E`, `via_E_modo`, el resultado y la nota de asignación fila por fila.

---

## Las 10 que no se pueden heredar, y por qué eso está bien

Son fragmentos de dos barrios donde **las zonas medidas dan resultados opuestos**:

- **Flores tiene tres zonas.** Z23 casco histórico **no abre** (cero grupos). Z24 Avellaneda–Ruperto Godoy **abre con seis**, el número más alto del barrido. Z39 Bajo Flores / Baek-ku **abre con dos**. Seis fragmentos de Flores no pueden heredar hasta saber dentro de cuál caen.
- **Balvanera tiene dos.** Z35 Once **no abre**. Z36 Congreso **abre con dos**. Tres fragmentos en la misma situación.
- Más `PGR_P109 · San Nicolás`, que está entre R12 Centro y Z47 Monserrat. Acá el resultado no cambia —ninguna de las dos abre— pero conviene resolverlo igual, porque si mañana una de las dos abre, la fila queda mal asignada.

Estas diez **quedan pendientes por diseño, no por omisión**. Se resuelven con un cruce espacial, y la geometría está congelada. Cuando se descongele, se resuelven en una corrida.

Y hay algo que vale la pena decir sobre esto: que un barrio contenga a la vez la zona con más reconocimiento externo del barrido y una zona con cero es **exactamente** lo que la definición anticipaba cuando dice que la delimitación debe responder a evidencia territorial y no a los límites de los barrios. Flores es el caso de prueba. Si el Atlas trabajara por barrio, Flores tendría un solo valor de vía E y sería falso en dos de los tres casos.

---

## La fila que hay que decidir: PG018

`PG018_NUEVO_BAJO_EN_RETIRO_ESMERALDA_Y_PARAGUAY`, 318 locales.

Como R18, su vía E **no abre**: cero grupos para esa esquina. Pero **Z46 Retiro abre con cuatro grupos**, y su clúster coreano-asiático —Maipú, Esmeralda, Paraguay y M.T. de Alvear, alturas 800 a 990— cubre ese punto exacto.

No es que a R18 le falte evidencia. Es que **está recortada más chica que el objeto que la prensa describe**. Queda marcada `REVISAR` y la decisión es de delimitación: absorberla en Z46 o sostenerla como recorte propio sabiendo que ninguna fuente la nombra así.

---

## Las tres zonas que faltaban: ninguna abre

Con Monserrat, San Cristóbal y Villa Soldati queda medida la vía E de **toda** la Ciudad. Las tres cierran, y cada una por un motivo distinto que vale la pena distinguir.

### Monserrat · el caso puro de prestigio sin barrio

Es la zona **más rica en locales distinguidos y más pobre en tratamiento de zona** de todo el Atlas. Tiene el Tortoni, Los 36 Billares, El Imparcial (H. Yrigoyen 1201), El Globo (1199), La Puerto Rico, Plaza Asturias, el Centro Asturiano. Aparece en el *Washington Post*, en La Nación dos veces, en Infobae, en Time Out.

**Cada una de esas apariciones es por un local, nunca por el barrio.**

Frommer's y Fodor's, que sí organizan por barrio, no tienen sección Monserrat. Frommer's lo nombra una sola vez y en subordinada, para decir que ahí "se agrupan" los bares notables junto con Congreso, La Boca y San Telmo — y **las tres zonas con las que lo agrupa sí tienen entrada propia**.

Y hay una segunda vuelta de tuerca: la única pieza que trata al eje Av. de Mayo como conjunto —iProfesional, sobre el drama del Tortoni a 36 Billares— lo trata para contar su decadencia. **El único encuadre de zona disponible es negativo.** Lo mismo dice el dueño de Plaza Asturias en Infobae: quedan los viejos, nuevos no se han creado.

El prestigio de Monserrat lo capitalizan los locales, no el barrio. Ese es el hallazgo.

### San Cristóbal · leído como corredor de paso

Un solo grupo, y el hallazgo está en cómo se reparte. La única nota que trata a San Cristóbal lo hace **pegado a Boedo**, y Boedo se lleva alrededor del 80 % de la atención gastronómica de la pieza: Café Margot, El Faro de Vigo y Spiagge di Napoli quedan del lado de Boedo, contra un solo local para San Cristóbal. La búsqueda por el eje de Av. San Juan deriva sistemáticamente a Boedo y a San Telmo.

**El margen es de un solo grupo**, y hay una rendija honesta: la guía impresa Time Out Buenos Aires Restaurantes & Bares 2025 circula solo en papel y su índice por barrio no es accesible por web. Si San Cristóbal tuviera capítulo propio ahí, sería un segundo grupo e4 y la vía abriría. Sin acceso, no se computa.

### Villa Soldati · cero absoluto, buscado aparte

Ocho rutas propias. **Este cero no se heredó de los ceros de Villa Lugano y Villa Riachuelo**, se buscó por separado. Fodor's, Frommer's y Lonely Planet verificados en negativo: ninguno lo nombra en ninguna sección.

Y hay una fuente de prensa que sí mide la zona y la ubica en el fondo: La Nación, 2017, el agrupamiento "Villa Lugano–Villa Soldati" registra **253 locales gastronómicos habilitados**, el escalón más bajo del relevamiento, contra 2.507 de Monserrat–Retiro. Dato de nueve años y agrupado, así que sirve como orden de magnitud y nada más — pero incluso el dato negativo más sólido que existe **no distingue a Soldati de Lugano**, y conviene que la matriz lo diga así.

Advertencia inversa, para que nadie la complete de más: **no prestarle a Villa Soldati la evidencia del Barrio Charrúa.** El Charrúa tiene borde discutido entre Nueva Pompeya y Villa Soldati, y su medición ya cerrada dice comunidad y fiesta anual desde 1972 pero sin oferta comercial estable. Aun si el borde se resolviera a favor de Soldati, no aportaría vía E.

---

## Cuatro trampas de esta ronda que conviene tener anotadas

**Time Out asigna mal al menos tres direcciones.** Su listado de Bares Notables del 17/09/2024 pone La Ideal (Suipacha 384) en Monserrat cuando es San Nicolás, y Café de los Angelitos (Av. Rivadavia 2100) y Don Victoriano (Av. Corrientes 1669) en San Cristóbal cuando son Balvanera y San Nicolás. **Las tres asignaciones erradas van a parar justamente a las dos zonas que se estaban midiendo.** Computada tal como está escrita, San Cristóbal habría sumado dos bares ajenos y Monserrat uno.

**Ohlalá y La Nación publicaron la misma nota con el mismo identificador** (`nid21042022`). No es una réplica parecida: es literalmente el mismo archivo bajo dos dominios del mismo grupo. Aparentaban dos fuentes; es una.

**"San Cristóbal" tiene homónimo en Santiago de Chile.** La consulta por escena gastronómica nueva devuelve en primeros lugares "Terrazas San Cristóbal, el nuevo centro gastronómico que reúne 11 bares y restaurantes en Bellavista", que es el cerro San Cristóbal chileno. Cualquier relevamiento futuro de esta zona va a chocar con esto.

**El Bar Iberia, Av. de Mayo 1196, no se puede resolver.** Infobae, marzo de 2024, lo da por cerrado, y no de pasada: el dueño de Plaza Asturias lo enumera junto al Hotel Castelar entre los que ya no están, para explicar por qué el eje se vacía. En 2025 aparecen dos notas anunciando que reabrió, ambas con encuadre calcado y **ninguna con fuente primaria identificable**. No se puede afirmar ni que está abierto ni que está cerrado.

Y un ejemplo de manual de por qué existe la regla de vigencia: Canal 26 publicó el 17 de julio de 2026 una nota que nombra al Tortoni y al Hotel Castelar **como si estuvieran plenamente operativos**, citando Wikipedia al pie. Nota del mes pasado, dato sin verificar. **La fecha de la nota no dice nada sobre la fecha del dato.**
