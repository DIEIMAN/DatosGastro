# De acá a un final entero

**11 de agosto de 2026.** Estado después del commit `7a5fa5f`. El documento tiene **166 páginas**, las
cifras verifican contra la geometría y los controles de forma dan cero. **Lo que falta no son errores:
son decisiones abiertas y profundidad de verificación.** Va ordenado por lo que realmente bloquea.

---

## Nivel 1 · Lo que bloquea llamarlo terminado

Son cuatro cosas y **ninguna es trabajo de medición: son decisiones**. Por eso están primero.

### 1 · Seis solapes declarados y sin repartir

| páginas | qué comparten |
|---|---|
| Abasto ↔ Almagro | 18,09 ha · 65 locales, sobre el corredor de Corrientes |
| Centro/Microcentro ↔ Monserrat | los Notables de Av. de Mayo |
| Chacarita ↔ Colegiales ↔ Villa Ortúzar | 15,93 ha · 25 locales, con La Mezzetta justo en el borde |
| Villa Crespo ↔ La Paternal | 49,7 ha · 91 locales |
| Núñez ↔ Federico Lacroze ↔ Belgrano | el viaducto y el tramo de Blanco Encalada a Monroe |
| Retiro ↔ Centro/Microcentro | 52,16 ha · 301 locales, el solape más grande del atlas |

El documento los declara y da la magnitud de cada uno, así que **no está mintiendo**. Pero mientras
estén sin repartir, cada página tiene que decir «esto no se suma con la de al lado», y esa frase
aparece seis veces. **Repartirlos es una decisión de conducción sobre a quién le corresponde cada
tramo. No hay medición que la reemplace.**

### 2 · La decisión de borde de La Boca sobre Almirante Brown

O el polo es más grande que el tramo de la obra pública, o los cinco establecimientos que quedan
afuera son del barrio y no del polo. Esta edición adoptó una extensión mínima —de 6,14 a 16,17
hectáreas— con una regla escrita: *se extiende cuando el establecimiento está sobre una calle que el
perímetro escrito ya nombra*. **Falta que la Dirección la confirme o la corrija**, porque es la
regla que va a gobernar los próximos casos.

### 3 · Cuatro polos sin borde propio dibujado

Retiro, Núñez y Villa Santa Rita publican las cifras de su barrio y lo declaran arriba de los
números. Colegiales tiene un borde que **es** el polígono administrativo del barrio: 229,08 hectáreas
contra 229,09. Son cuatro de cuarenta y uno.

Un atlas que define un polo como *un objeto delimitable* y deja cuatro sin delimitar tiene ahí su
grieta más visible. Hoy está declarada; **cerrarla es dibujar cuatro bordes.**

### 4 · Los treinta archivos con ruido de fin de línea

Del commit de anoche quedaron treinta archivos que git ve modificados y sólo cambiaron los saltos de
línea. No afecta a nada, pero ensucia cualquier `git status` de acá en adelante. Se limpia con un
`.gitattributes` y un `git add --renormalize .`

---

## Nivel 2 · Lo que le falta al método, no al texto

### 5 · El veredicto de «cantidad de locales» no se deduce de las cifras publicadas

Villa Urquiza lo cumple con 0,9 % de continuidad a veinte metros; San Telmo no lo cumple con 8,5 %.
La razón real es que se juzga sobre objetos de escalas muy distintas —hay contornos de cinco
hectáreas y de cuatrocientas—. **Esta edición lo declara en «Cómo leer estas páginas» en vez de
dejar que la comparación lo sugiera**, que era lo mínimo. Resolverlo es fijar una vara por familia
de polo, y es trabajo de la próxima edición.

### 6 · Veintitrés de cuarenta y una páginas no tienen perímetro reconstruible

Once páginas escriben un perímetro del que se puede rehacer el borde. Siete lo escriben a medias.
**Veintitrés no**: ocho no nombran ninguna calle y dos no escriben perímetro. El efecto práctico ya
se midió: de los veintiún establecimientos que están cerca del borde de una página sin calles, no se
resuelve ninguno — no por geometría, sino porque no hay texto contra el cual medirlos.

### 7 · La capa de reconocimiento que leen las páginas está atrasada

215 filas contra 225 en la canónica. **El impacto sobre el documento ya está corregido a mano** —los
dos casos que caían adentro de un borde eran el Café Roma de La Boca y el Bar Iberia del
Microcentro—, pero el insumo sigue viejo y la próxima regeneración de bloques lo va a volver a
meter. **Regenerarla es una tarea de pipeline, no de escritura.**

---

## Nivel 3 · Verificación de vigencia · es trabajo, no decisión

Es lo que más rinde por hora y lo único que envejece solo.

| estado | cuántos |
|---|---:|
| probablemente abierto | 9 |
| sin verificación individual | 7 |
| en conflicto entre dos fuentes | 3 |
| dudoso | 3 |
| **total de estados abiertos** | **22** |

Más los pendientes que las páginas nombran una por una: **dieciséis páginas piden verificar un
establecimiento concreto.**

Y dos bolsones que ya se atacaron y no cerraron:

- **Tres de seis históricos siguen sin pieza fechada individual**: Bar del Alvear Palace Hotel, Petit
  Colón y El Coleccionista. En los tres el catálogo confirma pertenencia y domicilio, y ninguno
  acredita operación.
- **Catorce de quince locales siguen sin prueba nueva**, y nueve de ellos son el registro kosher de
  Flores, cuya única prueba oficial es de **2015**. Es la evidencia más vieja que sostiene una
  condición en todo el atlas.

**Esto no se resuelve buscando más**: se agotaron las rutas documentales. Se resuelve con una
constatación en el lugar, y ésa es la única parte del atlas que no puede hacer nadie sentado.

---

## Quién hace qué

**Vos.** Las dos decisiones de conducción —el reparto de los seis solapes y la confirmación de la
regla de extensión de bordes— y las constataciones en el lugar. Nada más. Todo lo demás tiene dueño.

**Claude Code.** Los cuatro bordes que faltan, el reparto geométrico de los solapes una vez decidido,
la regeneración de la capa de reconocimiento y el `.gitattributes`.

**Codex.** Los veintidós estados abiertos de vigencia y los dieciséis pedidos página por página. Es
su tipo de trabajo y ya tiene el método armado.

**Yo.** La escritura de todo lo anterior, y la vara por familia de polo para la condición de cantidad
de locales, que es lo único de método que queda abierto.

---

## Lo que ya está cerrado, para no volver sobre eso

Las cuarenta y una divisiones de locales por hectárea. Las doscientas cifras de continuidad. La unión
de los 41 —5.444,15 hectáreas y 10.819 locales— y sus 1.286 repeticiones sobre 1.263 locales
distintos. El control de los 292 establecimientos contra los bordes. La distribución del catálogo de
notables. Las cifras de portada. Los treinta y ocho casos de establecimiento con historia fuera de su
borde, con nombre y distancia en las catorce páginas donde pasa. Y la base de 27.727 locales, que es
un producto aparte y ya está entregada.

**El documento no está mal medido, y ya no está mal terminado.** Lo que queda es más profundo que la
edición: son las decisiones que el atlas dejó explícitamente abiertas, y la evidencia que sólo se
consigue caminando.
