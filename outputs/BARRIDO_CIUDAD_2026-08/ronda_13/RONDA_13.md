# Ronda 13 · Registro y control · 2026-08-09

Tanda de registro, no de contenido. Sale de la auditoría de estado del 09/08 hecha desde Cowork.
**Google Places: 0 requests.** No se tocó el pipeline público, ni las láminas, ni las secciones.

Predicciones escritas antes de correr: `LECTURA_PREVIA_RONDA_13.md`. Dos acertaron y una acertó
a medias, exactamente como estaba escrito que podía pasar.

---

## 1 · Lo que estaba fuera de git ya está adentro

La auditoría lo tenía bien: **3 modificados y 98 sin rastrear**, con la ronda 12 entera afuera.
Se agregó todo, salvo lo que el guardrail 7 saca a propósito.

**Los dos archivos que la auditoría mandó mirar no eran el problema.**
`catalogo_pendientes_para_diego.csv` (52 filas) y `lista_places_prioridad.csv` (71) traen nombre
comercial y dirección, y nada más: ni teléfono, ni mail, ni CUIT. El repo ya versiona listados
idénticos —`bares_notables_caba.csv`, `direcciones_pizzerias_heladerias.csv`, la capa de 225
hitos—. Diego confirmó que van al repo. Van.

**El problema estaba en otros cuatro que la auditoría no revisó.** Barriendo los 117 archivos con
expresiones regulares de mail, teléfono, CUIT y DNI aparecieron teléfonos y correos de comercios
en `PARA_CHEQUEAR_DIEGO.csv`, `vigencia_tanda_A_centro.csv`, `vigencia_tanda_B_almagro_norte.csv`
y `vigencia_verificada_ronda_2.csv` —`+54 11 3647-7287`, `info@capiscibistrot.com`, `4342-4328`—.

El repo ya tenía escrita la regla para este caso exacto, en la entrada del ENTUR del `.gitignore`:

> *«es dato abierto CC-BY y son comercios, no personas, pero el guardrail 7 nombra emails y
> teléfonos sin esa distinción y no se la hacemos nosotros»* → se versiona la derivada
> `*_sin_contacto`.

Se hizo lo mismo: `ronda_13/sanitizar_contactos.py` produce las cuatro derivadas, los cuatro
originales van al `.gitignore` y se quedan en disco. **Se conservan a propósito los handles de
Instagram y las webs propias**: no son contacto de una persona, son el canal donde vive la
evidencia fechada, y todo el método de vigencia se apoya en «hay posteo fechado en @cuenta».

---

## 2 · La correspondencia de secciones · y no era un renumerado

`correspondencia_fase_documental.csv` y `INDICE.csv` existen. Los dos los nombraba el handoff
como si estuvieran.

**Pero la premisa de la auditoría estaba mal, y lo corrigió `DOS_PROYECTOS_DE_FICHA.md` cuatro
horas después.** La auditoría leyó dos numeraciones y las atribuyó a un renumerado. No lo son:
son **dos proyectos de documento**, cada uno coherente por dentro.

| | **A · las 124 fichas** (06/08) | **B · las 41 fichas** (08/08) |
|---|---|---|
| objeto | las 124 concentraciones detectadas | los 41 polos admitidos por las seis vías |
| agrupación | por comuna | por origen |
| el cuerpo es | sección **V** | sección **VII** |
| «qué no dice» | sección **VII** | sección **IX** |

Por eso la tabla tiene 13 filas y no 9: hay bloques que existen dos veces —«Qué es un polo» y
«Qué no dice»— y bloques que sólo existen en uno.

**Y aparecieron dos cosas que ni el handoff ni la auditoría tenían:**

**La tabla de numeración ya existía.** Está en la cabecera de `ATLAS_V3_SECCIONES_II_V_VI_IX.md`,
líneas 22 a 32. La auditoría dijo «ninguna tabla que los relacione» y la tabla estaba en el
archivo que estaba citando. Lo que faltaba no era la tabla: era la correspondencia contra la
numeración vieja, que la tabla no da.

**La Nota metodológica no tiene lugar.** Está escrita y completa —en seis pasos, las cuatro
reglas, y qué se publica junto con el documento— y era la VIII de la numeración vieja. **La tabla
nueva va de I a IX y no la incluye.** Es la única fila de la correspondencia que no cierra. El
handoff la daba por faltante; no falta, falta decidir dónde va.

Y la sección VII ya no está vacía: `FICHAS_SECCION_VII_TANDA_1.md` trae **11 de las 41**, escritas
esta mañana. Faltan 30.

---

## 3 · El archivo de Palermo se llamaba mal, y ahora no

`ronda_10/palermo_los_407_por_zona.csv` → **`ronda_10/palermo_residuo_por_zona.csv`**, con
`git mv` para que conserve la historia. Devolvía 188 y prometía 407.

Corregido en `HANDOFF_ATLAS_V3_CONTEXTO.md`, que decía *«407 locales de R01 no están en ninguna
subzona»* y *«perdería 407 locales publicados»*. **El objeto estaba invertido.** Los 407 son los
de Soho ∪ Hollywood que caen **fuera** de R01. Los de R01 que no están en las subzonas son 398
contra dos y **188** contra las tres.

> **El veredicto no cambia y conviene decirlo: la opción B se sigue cayendo.** Sólo que pierde
> 188 locales publicados, no 407.

Las otras tres apariciones —dos en `LA_RONDA_QUE_ME_REFUTO.md`, una en
`NO_ERA_UN_CONTEO_MAL_ERA_OTRO_UNIVERSO.md`— son narrativas fechadas de su ronda y **no se
reescriben**: se corrigen por errata, que es la convención del proyecto. ERR-06 y ERR-07.

---

## 4 · La vía C de Almagro · la pregunta estaba mal planteada

`via_C_almagro.csv`, ocho pasos.

La pregunta era «¿mercado o feria itinerante?». **La respuesta es ninguna de las dos: no hay
objeto.**

Almagro es **la única fila abridora de todo el barrido que no nombra el objeto que le abre la
vía C.** Bonpland, Belgrano, del Progreso y el Patio Costanera Norte nombran el suyo; Almagro
dice «abre» y nada más.

**Y no hay mercado, medido:** de los 225 hitos de la capa, 11 son de tipo `Mercado/patio` y 8
tienen punto. **Cero caen dentro del polígono de Almagro.** El más cercano es el Mercado del
Progreso, a 1.237 m, que es de Caballito y ya le abre la vía C a R10.

Lo único que el corpus llega a nombrar cerca es **la feria itinerante de Plaza Almagro**, y
aparece en el campo `puerta_cerrada` —o sea, como fuente que no se pudo consultar: sus permisos
son internos y nunca se vieron.

**Y para esto no hace falta la decisión 23.** Una feria itinerante también falla su prueba —es
puesta en su entorno por permiso, días fijos, y se levanta—, pero **la decisión 1, del 07/08, ya
había resuelto la clase entera**: *«la vía C exige mercado, patio o galería EN ACTIVIDAD. La FIAB
suma como dato de contexto pero no abre.»*

> ### La vía C de Almagro NO ABRE. La lámina 4 dice **cinco**.
>
> Caen sólo la C. Almagro conserva A, B, D, E y F, con sus cinco Bares Notables verificados
> abiertos. **No pierde nada de lo que lo hace fuerte.**

### Dos cosas más que salieron de acá

**El «única zona que abre las seis vías» ya era falso cuando se escribió.** En el mismo
`seis_vias_ronda_2.csv`, Z40 Nueva Pompeya – Parque Patricios también marcaba seis, y la ronda 3
sumó Z43 Colegiales. **Eran tres, no una.** Es un error independiente del anterior. ERR-08.

**Z47 Monserrat sigue diciendo «abre (DÉBIL)».** La decisión 1 ordenó explícitamente pasarla a NO
ABRE por ser sólo FIAB, y nunca se escribió de vuelta en el archivo. Es el mismo modo de falla
que la ronda 12 encontró con el IDECBA: **registrar el defecto no lo corrige si no llega al
archivo que se lee.** ERR-09. No cambia su veredicto: Monserrat entra con cuatro.

Y queda **señalado, no resuelto**: Z40 abre por «Mercado de Pompeya», que tampoco está en la capa
de 225. Mismo defecto que Almagro pero con objeto nombrado. No estaba en el alcance.

---

## 5 · Palermo · las tres subzonas que nadie midió

`palermo_seis_subzonas.csv` · `palermo_pieza_1_y_filtraciones.csv`

La ficha de R01 nombra **seis** subzonas. Las rondas 9 y 10 midieron contra **tres**. Se midieron
las otras tres.

```
R01 ∩ P073 Palermo Botánico     0,00 ha ·   0 locales
R01 ∩ P087 Palermo Pacífico     0,00 ha ·   0 locales
R01 ∩ P092 Villa Freud          0,00 ha ·   0 locales
```

**Cero. Las tres.** Y ninguna toca ninguna de las 8 piezas del residuo.

> **La hipótesis se cae: Palermo no se cierra.** Si la pieza 1 hubiera sido una de las tres, la
> ficha ya estaba escrita para recibirlo. No lo es. La pieza 1 sigue sin nombre.

**La corrida reprodujo la ronda 10 número por número** —1358, 772, 595, 361, 210, 188, y las ocho
piezas con sus 134 / 15 / 25 / 1 / 6 / 5 / 2 / 0—, que es lo que la vuelve creíble.

### Y encontró que el universo no estaba declarado en ningún lado

La primera corrida dio **1454** para R01 en vez de 1358, y **207** de residuo en vez de 188. Un
7 % arriba, parejo. El universo de las rondas 9 y 10 es
**`anillo == 'nucleo'` Y `apto_geometria == True`** —23.981 de los 27.727 de la base—, y **no
estaba escrito en ningún archivo**.

> **Lo peligroso es que las áreas coinciden exacto en los dos casos.** Una corrida sin el filtro
> reproduce la geometría al centímetro y parece validar, mientras cuenta otro universo. Ahora está
> declarado en el docstring de los dos scripts. ERR-10.

### Y de paso cierra los 728 contra 772 de Soho

`DOS_PROYECTOS_DE_FICHA.md` lo dejó abierto esta mañana: *«`POLOS_NOMBRADOS.csv` dice 728 locales.
La ronda 9 midió 772 para el mismo P091. No sé cuál es correcto y no lo elijo.»*

**Ninguno de los dos está mal: miden cosas distintas, y la resta cierra sola.**

```
728   locales asignados al cluster P091      (pertenencia_local_polo_v3.csv)
 − 8  asignados al cluster pero FUERA del polígono publicado
 +52  dentro del polígono publicado pero sin cluster asignado
─────
772   locales dentro del polígono publicado  (polos_publicables.geojson)
```

**728 es el clúster. 772 es el polígono.** La diferencia la produjo la poligonización: el polígono
publicado se suavizó y se hizo cóncavo, y al hacerlo se tragó 52 locales que nunca fueron del
clúster y dejó afuera 8 que sí.

> Para cualquier cosa cartográfica —y una ficha de subzona lo es— **el número que manda es 772**,
> porque es el que corresponde al polígono que el Atlas dibuja. 728 sirve para hablar del clúster.
> Con eso, la ficha de Palermo **sí puede citar el conteo de la subzona**, declarando cuál usa.

### Un nombre para la pieza 1

**40,17 ha · 134 locales · 1.196 m E-O × 1.102 m N-S · 100 % Palermo.** Calles dominantes, sobre
los 71 locales que traen dirección (el 53 %): **Paraguay 12 · Charcas 7 · Fray Justo Santa María
de Oro 7 · Soler 6 · Uriarte 5 · Jorge Luis Borges 5 · Guatemala 4 · Thames 4 · Godoy Cruz 4.**

Es **la franja noreste de Palermo Viejo, entre Guatemala/Soler y Av. Santa Fe**.

Y hay un polo del borrador adentro que la ficha de R01 **no nombra**:
**P090+P089 · «Palermo — eje Av. Santa Fe»**, 18,54 ha, del que **12,70 ha caen en la pieza 1**
—el 68,5 % del polo, el 31,6 % de la pieza— con **75 de los 134 locales, el 56 %**.

> **El núcleo denso de la pieza 1 ya tiene nombre de trabajo, y explica más de la mitad de sus
> locales en un tercio de su superficie.** Lo que no explica son 27,47 ha y 59 locales.
>
> **Propuesta, para firma:** la pieza 1 se declara subzona con el nombre **«Palermo — eje Av.
> Santa Fe»** extendido a su envolvente, y el perímetro declarado se escribe sobre las calles
> medidas. **Con la salvedad al lado:** el 47 % de sus locales no trae dirección, así que el
> ranking de ejes describe bien la franja pero no la agota.

### Las piezas que se filtran · dos son doble conteo y una es un artefacto

| pieza | ha | loc | barrio | contra la vecina |
|---|---:|---:|---|---|
| 3 | 11,07 | 25 | Villa Crespo | **NO solapa R08 · está a 6 m** |
| 5 | 6,71 | 6 | Colegiales | **SOLAPA Chacagiales · 6,54 ha · 5 locales** |
| 7 | 3,21 | 2 | Chacarita | **SOLAPA Chacagiales · 1,55 ha · 2 locales** |

**La pieza 3 no es una filtración: es un artefacto de borde.** R08 está a 6 m y no se tocan —lo
mismo que ya había medido la auditoría—. Seis metros es menos que una vereda. No hay nada que
repartir: hay un hueco que declarar.

**Las piezas 5 y 7 sí son doble conteo real: 8,09 ha y 7 locales están en R01 y en Chacagiales al
mismo tiempo.** Es chico y es concreto, y toca el nudo que ya estaba abierto.

---

## 6 · Control de arrastre · la decisión 23 está bien aplicada

Cuatro controles, los cuatro pasan:

| control | esperado | medido |
|---|---|---|
| vía C abierta · 94 filas | 2 | **2** · PG001B Palermo Hollywood, PG008 Caballito |
| vía C abierta · 22 zonas | 3 | **3** · R01 Bonpland, R05 Belgrano, R10 del Progreso |
| `PGR_P004` | ya no «si» | **`no`** |
| R07 y PG009 Costanera Norte | fuera | **`no`**, con la nota de la decisión 23 |

Y la cadena completa, que ninguna ronda había mirado de una sola vez:

```
r8  → 4 filas con vía C   (PG001B, PG008, PG009, PGR_P004)   ← acá vivía el arrastre
r10 → 3   (sale PGR_P004)
r12 → 2   (sale PG009 Costanera Norte, por la decisión 23)
```

**El arrastre de PGR_P004 lo había cerrado la ronda 10, no la 12.** La ronda 9 lo anotó sobre la
r8 y quedó la impresión de que seguía vivo.

---

## 7 · El IDECBA a nivel polo · y una sonda que casi me engaña

`idecba_x_polo.csv`

**Lo que la tarea pedía, primero.** Costanera Norte y Boulevard Caseros **no tienen eje relevado**,
y ahora la ficha puede declararlo en vez de omitirlo. Pero el negativo no se apoya en la sonda:
se verificó por el otro lado, cruzando las **calles** de los locales de cada referencia contra las
calles de los 80 tramos.

- **R07 Costanera Norte.** Sus 67 locales están sobre Costanera Rafael Obligado, Aeroparque y
  Sarmiento 4701. **Ninguna de esas calles figura en ningún tramo de los 48.** Negativo sólido.
- **R11 Boulevard Caseros.** Acá sí hay cuatro calles compartidas, y ninguna solapa:

| calle | el eje relevado | la referencia la tiene en | |
|---|---|---|---|
| Defensa | Defensa **801-1499** | **1501**-1757 | **no solapa por 2 números** |
| Brasil | Constitución 1101-1299 | 359-780 | no solapa |
| Caseros | Parque Patricios 2601-2999 | 430-799 | no solapa |
| Montes de Oca | Montes de Oca 501-1199 | 95-101 | no solapa |
| Salta | Constitución 1601-1799 | 1998 | no solapa |

> **El eje Defensa termina en el 1499 y R11 empieza en el 1501.** Es el mismo patrón que la ronda
> 12 encontró con Plaza Bar —Florida 1005 contra un eje que termina en el 999, seis números
> afuera—. **Dos veces no es casualidad: los ejes del IDECBA y las referencias del Atlas se
> tocan sin superponerse, y conviene decirlo así en el documento.**

**Av. Corrientes queda pendiente a propósito.** Hay cinco ejes con locales dentro de R02 —Corrientes
y Callao, Lavalle, Libertad, Corrientes y Medrano—, y **no se atribuyen a mano**: el tramo de R02
no está fijado, y ésa es la condición previa. La fila sale como `PENDIENTE`, ni sí ni no.

### Y lo que casi publico mal

La primera versión de esta corrida reportaba **«21 de 48 desacuerdos entre la columna
`esta_en_el_atlas` y la medición»**. Sonaba a hallazgo grande. **Era un artefacto de la sonda.**

La sonda necesita que el nombre de calle del tramo normalice igual que el `direccion_norm` de la
base, y para 12 ejes no pasa: *Ramón Falcón* contra *Ramon L. Falcon*, *Lacroze* contra *Federico
Lacroze*, *A. M. De Justo* contra *Alicia Moreau De Justo*, *Alberdi* contra *Juan B. Alberdi*.
**Esos ejes matchean cero locales en toda la base**, antes de tocar geometría. Un negativo de un
instrumento ciego no es un negativo.

> Así que el CSV ya no reporta un agregado: reporta **la calibración caso por caso**, con los 12
> ejes que la sonda no puede ver nombrados uno por uno. **Sobre esos 12 esta corrida no dice nada,
> ni sí ni no.** Lo que lo resuelve es construir los 80 tramos como geometría, que es el pendiente
> 4 del handoff.

---

## 8 · Las verificaciones · lo prioritario cierra, el resto no

`verificaciones_seis_fichas_r13.csv`

**La ruta de TripAdvisor no me sirvió: devuelve HTTP 403 a cualquier pedido automático.** Lo digo
antes que nada porque era la ruta propuesta. Se trabajó con lo que el guardrail 6 sí habilita
—fuentes oficiales del GCBA, sitios propios y prensa fechada— y con la decisión 2 como vara:
**reporteo a nivel establecimiento o es v4.**

**Las tres fichas que dependían de uno o dos establecimientos:**

| zona | establecimiento | veredicto | fuente |
|---|---|---|---|
| **R08** | Café San Bernardo | **verificado_abierto v1** · 62 días | La Nación 08/06/2026, lo ubica en Corrientes 5436 y **cita a su dueña** |
| **R11** | Bar Británico | **verificado_abierto v1** · 113 días | Canal 26 18/04/2026 |
| **R07** | Patio Costanera Norte | verificado_abierto **sin fecha** | página oficial del GCBA con horarios vigentes |
| **R07** | Happening Costanera | **no cierra** | sitio propio con copyright 2026 y nada fechable |

> **R08 se destraba entero y con holgura.** Su único Notable tiene reporteo propio de hace dos
> meses.
>
> **R11 cierra pero no con holgura.** Canal 26 ya fue desplazado como fuente en la ronda 10, y el
> Británico tiene historial de cierre y reapertura —justo el patrón que exige fecha reciente—.
> Conviene un segundo respaldo.
>
> **R07 no cierra.** El Patio resuelve la fila y no se cita, por la regla de la ronda 12. Y
> Happening es la fila más débil de las cuatro: **un copyright 2026 no es evidencia de actividad,
> se actualiza solo.**

**De las 14 restantes: una verificada (La Biela, La Nación 15/10/2025, v1 pero a 298 días), dos
intentadas sin cerrar (La Giralda y El Gato Negro: aparecen en programación de eventos, que por la
decisión 2 es v4 y no v1) y once no intentadas.** Están listadas una por una con eso escrito.

---

## 9 · La capa de memoria de Recoleta · y por qué no se carga como está

`capa_de_memoria_R06_recoleta.csv` · seis entradas nuevas, M032 a M037

R06 no tenía ninguna entrada y ahora tiene seis: **Lola** (cerró 2013, el que inicia la serie),
**Montana**, **San Babila**, **Buller**, **La Munich** (2017) y **Café Victoria**. Todas sobre
**Pdte. Roberto M. Ortiz al 1800, entre Quintana y Guido**.

**Pero el dato más importante es la fecha de la fuente.** La nota de La Nación que da título a
esto —*«la calle fantasma que perdió restaurantes icónicos»*— es del **11 de abril de 2017**,
actualizada en 2020.

> **Y el mismo diario publicó en septiembre de 2021 que la cuadra se está recuperando:** *«La
> emblemática cuadra de Recoleta que con nuevas aperturas gastronómicas busca recuperar su
> esplendor»*. Nombra a **La Parolaccia** —décima trattoria de la cadena, donde estaba el Café
> Victoria— y a **Club de la Birra**, en el local de La Munich, al que le atribuye haber traído
> público joven.
>
> **Cargar «calle fantasma» en presente sería repetir exactamente el error que el proyecto viene
> corrigiendo:** citar como actual algo que la propia fuente desmintió después. La ficha de R06
> puede nombrar las pérdidas —para eso está la capa— pero **en pasado y con el año al lado.**

Y hay un cruce que cierra solo: **`Ortiz 1801-1899` es uno de los cinco tramos del eje Recoleta
del IDECBA**, que hoy releva 95 locales con **89,5 % de ocupación y −3,2 pp interanual**. La cuadra
de la capa de memoria y el tramo relevado son la misma cuadra.

**Confianza declarada fila por fila, y baja donde corresponde:** Montana y San Babila quedan en
`baja` porque la nota los nombra en serie y sin año propio, y **Café Victoria también**, porque las
dos notas se contradicen —la de 2017 describe *«The Embers, que reemplazó a El Ombú y que a su vez
había suplantado a La Victoria»* y la de 2021 pone a La Parolaccia donde estaba *«el clásico Café
Victoria»*—. Puede ser el mismo local mal citado o dos distintos. **No se fusionan.**

---

## 10 · Lo que volvió del cierre del día · y el nombre de Palermo no se firma

Las decisiones del 09/08 dejaron dos cosas al repositorio. Las dos están hechas.

### ERR-09 escrita en el archivo, no sólo decidida

`seis_vias_Z47_Z48_Z49.csv`, fila Z47: la vía C pasa de `abre (DÉBIL, ver nota de criterio)` a
**`no abre`**, con la decisión 1 citada. Monserrat **entra igual**, ahora con cuatro vías.

> **Y el campo se reconcilia consigo mismo.** `n_vias` decía **«5 (4 robustas)»**. La débil era
> justamente la vía C. Al cerrarla, el recuento queda en **4** y coincide con lo que el propio
> campo venía diciendo hacía dos rondas.

### La medición que Diego pidió antes de firmar · y que dice que no firme

> *«NO se pide la firma hasta que el repositorio mida el perímetro en calles sobre la caja
> −58,43404 / −34,59232 a −58,42101 / −34,58240. Proponer perímetros sin medir ya falló dos veces.»*

Medido. **La respuesta es que la pieza 1 no tiene perímetro describible en calles**, y que el
nombre propuesto nombra una avenida que la pieza no toca.

**El perímetro mide 4.645 m. Sólo 709 corren sobre alguna calle: el 15 %.** El resto corta por
adentro de las manzanas, porque el borde de la pieza no es una calle — es lo que quedó al restarle
Soho y Hollywood a R01, y esos bordes son envolventes de clúster.

| la calle que más acompaña el borde | 203 m | Araoz — **el 4 % del perímetro** |
|---|---:|---|
| las seis que podrían ser lado | 709 m | Araoz · Honduras · Costa Rica · El Salvador · Scalabrini Ortiz · Gascón |
| las que **cruzan** la pieza | hasta 774 m | Paraguay 774 · Uriarte 464 · Godoy Cruz 461 · Soler 448 · Guatemala 441 |

Las calles largas la **atraviesan**. Las que la bordean lo hacen por cien metros y sueltan.

### Y la prueba directa del nombre

```
Av. Santa Fe dentro de la pieza 1        0 m
distancia de la pieza 1 a Av. Santa Fe   251 m
Av. Santa Fe dentro de P090+P089         191 m
```

> **«Palermo — eje Av. Santa Fe» nombra una avenida que está a 251 metros de la pieza y no le
> entra ni un metro.** El nombre es correcto para **P090+P089**, que sí la toca. Pero P090+P089
> está adentro de la pieza sólo en un 68,5 %, **y la parte que tiene Santa Fe es justamente la que
> queda afuera.**
>
> **Firmar ese nombre habría sido el tercer caso de la serie que Diego nombró**, después del
> perímetro imposible de Colegiales —Álvarez Thomas y Forest tocándose a 0 m— y del enclave de
> Liniers 900 números al oeste. **La condición que puso funcionó: la medición lo frenó.**

**Lo que sí se puede decir de la pieza 1, con la medición en la mano:** son 40,17 ha y 134 locales
en la franja delimitada por Araoz, Honduras, Costa Rica, El Salvador, Scalabrini Ortiz y Gascón
—entre Guatemala y Soler, sin llegar a Santa Fe—, atravesada por Paraguay, Uriarte, Godoy Cruz y
Thames. **No es un eje: es un paño.** Y esa es la razón por la que ninguna calle lo nombra.

---

## Lo que queda para Diego

1. **La lámina 4 pasa a decir cinco.** Es la única consecuencia de contenido de esta tanda.
2. **ERR-08 y ERR-09** esperan firma. Ninguna cambia un veredicto de admisión.
3. **El nombre de la pieza 1 de Palermo** y su perímetro declarado.
4. **Las 8,09 ha de doble conteo** entre R01 y Chacagiales.
5. **Dónde va la Nota metodológica**, que está escrita y no tiene número.
6. **Cuál de los dos proyectos de ficha es el cuerpo** —la pregunta de `DOS_PROYECTOS_DE_FICHA.md`,
   que es más grande que todo lo de esta tanda junto.
7. **Happening Costanera**, que es lo único que le falta a R07 y no cierra por escritorio:
   necesita un posteo fechado, una nota o una llamada.
8. **Las 14 verificaciones que quedaron.** La ruta de TripAdvisor no está disponible por acceso
   automático; la que sí funcionó es prensa fechada con reporteo a nivel establecimiento.
9. **Cómo se redacta la memoria de Recoleta**, que no puede ir en presente.
10. **El tramo de R02**, que es la condición previa para atribuirle sus ejes del IDECBA.
11. Señalado y no resuelto: **la vía C de Z40 Nueva Pompeya**, mismo defecto que Almagro.
12. Y para el pendiente 4 del handoff: **construir los 80 tramos como geometría** es lo que saca a
    12 de los 48 ejes del punto ciego en que están hoy.
