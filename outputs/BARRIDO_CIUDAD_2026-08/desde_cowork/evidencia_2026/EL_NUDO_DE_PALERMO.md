# El nudo de Palermo se desata con una resta

*8 de agosto de 2026 · la única decisión de delimitación que dejó abierta la auditoría de duplicados*

Datos en `palermo_delimitacion_propuesta.csv`.

---

## El problema, como estaba planteado

| | locales | superficie |
|---|---:|---:|
| Palermo Soho | 772 | |
| Palermo Hollywood | 595 | |
| Las Cañitas | 361 | |
| **suma de las tres subzonas** | **1.728** | **277 ha** |
| **R01 Palermo, referencia publicada** | **1.358** | **271,29 ha** |

**Las subzonas tienen más locales que la referencia que supuestamente las contiene.** La auditoría lo dejó como la única decisión nueva, con dos salidas: o R01 se amplía para contener a las tres, o las subzonas son las fichas y R01 deja de ser una fila.

**Hay una tercera, y la sugiere la aritmética.**

## La resta

$$772 + 595 = 1.367$$
$$\text{R01} = 1.358$$
$$\Delta = 9$$

$$1.728 - 1.358 = 370$$
$$\text{Las Cañitas} = 361$$
$$\Delta = 9$$

**Soho más Hollywood da los locales de R01, con nueve de diferencia. Y la diferencia entre la suma de las tres y R01 da Las Cañitas, con los mismos nueve.**

> **Hipótesis: R01 Palermo ya es, en los hechos, Soho ∪ Hollywood. Las Cañitas nunca estuvo adentro.**

Los mismos nueve locales aparecen en las dos restas, lo que apunta a un efecto de borde único —probablemente sobre el límite entre Soho y Hollywood, o sobre el filo del polígono publicado— y no a un desajuste distribuido.

**No es una coincidencia que se pueda dejar sin probar, y tampoco es una prueba.** Es una hipótesis con una predicción, escrita antes de que corra la geometría, según R1.

### Las tres predicciones, para que la corrida las confirme o las mate

1. **R01 ∩ (Soho ∪ Hollywood)** cubre casi toda el área y casi todos los locales de R01.
2. **R01 ∩ Las Cañitas ≈ 0.**
3. Los **9 locales** de residuo caen sobre un solo borde, no repartidos.

Si la 2 falla —si Cañitas sí está parcialmente adentro de R01— la hipótesis se cae y volvemos a las dos salidas de la auditoría. **Escrito antes, no después.**

---

## Y la evidencia documental dice lo mismo

Fui a buscar las delimitaciones publicadas de las tres, y encajan.

### El sitio oficial de turismo del GCBA delimita las tres, y con una línea divisoria clara

> **Palermo Hollywood** — *«entre Av. Santa Fe y Av. Córdoba»*, al **norte** de Juan B. Justo
> **Palermo Soho** — *«entre Juan B. Justo y Scalabrini Ortiz»*
> **Las Cañitas** — *«centrada en la calle Báez y las calles circundantes»*

**Av. Juan B. Justo es el borde entre Soho y Hollywood.** Las dos son contiguas y disjuntas, y juntas forman un bloque. Wikipedia coincide con el perímetro de Hollywood: **Av. Juan B. Justo, Av. Córdoba, Av. Dorrego y Av. Santa Fe**.

*(Nota de criterio: la comunicación del GCBA no computa como grupo de la vía E, por parte interesada. Acá no se usa como reconocimiento sino como **dato factual de delimitación** — qué llama la Ciudad Soho y qué llama Hollywood. Es el mismo tratamiento que se le da a una ficha oficial: no acredita vigencia, sí acredita dirección.)*

### Las Cañitas tiene delimitación propia, y es otro rectángulo

Info Gastronómica, con la delimitación más precisa que apareció:

> *«estas **veinte manzanas** delimitadas por las avenidas **Dorrego, Luis María Campos y del Libertador**»*, con el núcleo de mayor concentración en *«el rectángulo comprendido por las calles **Arce, Arévalo, Ortega y Gasset y Báez**»*

**Av. Dorrego es el borde compartido**: Hollywood queda de un lado, Cañitas del otro. Son **adyacentes, no anidadas** — que es exactamente lo que la resta predice.

---

## La salida que propongo, y es la misma figura de Chacagiales

**Palermo pasa a ser un sistema de subpolos con tres subzonas: Soho, Hollywood y Las Cañitas.**

Por qué esto resuelve las cuatro cosas a la vez:

**No redefine R01, la amplía.** R01 ya es Soho ∪ Hollywood; el polo con las tres subzonas **contiene** a R01. La regla de que las referencias publicadas sólo se amplían se cumple, y hay que verificarlo por superficie perdida y no por predicado —**R12**, la trampa de GEOS.

**Termina el doble conteo.** Hoy la matriz tiene a R01 y a sus tres subzonas como filas pares, y sumarlas cuenta Soho y Hollywood dos veces. Con la figura de sistema, R01 deja de ser una fila par de sus propias partes: es el padre, y las fichas son las tres.

**Le da a Palermo la forma que la evidencia le da.** Nadie describe Palermo gastronómico como un objeto único: la prensa, las guías y el propio sitio oficial nombran las tres por separado y con límites distintos. Publicar un solo polígono de 271 hectáreas llamado «Palermo» pierde toda esa información.

**Y es consistente con lo que ya decidimos.** Chacagiales se resolvió así hace un día, por el mismo motivo y con el mismo instrumento. Que la misma figura resuelva los dos nudos más grandes del mapa es un argumento a favor de la figura, no una casualidad.

---

## Un hallazgo que no buscaba, y que cambia una ficha

**Las Cañitas decayó, y la fuente lo dice sin rodeos.**

> *«La mayoría de los bares y restaurantes cerraron o se trasladaron hacia otros circuitos gastronómicos.»*
> *«Hoy Cañitas tiene otro perfil, más familiar y residencial. El día late más fuerte que la noche.»*

Es el polo que fue boom a fines de los noventa, y la nota lo describe como un circuito que perdió su función. De los quince o dieciséis establecimientos históricos que enumera —Novecento en Báez 199, Soul Café, Morelia, El Portugués, Santino, Voodoo Bar, entre otros— la mayoría ya no está.

**Con dos salvedades, y las dos importan:**

**La fuente es del 20 de febrero de 2022.** Tiene cuatro años y medio. Para una afirmación sobre el estado *actual* de una zona, está fuera de cualquier ventana que usemos. **No alcanza para publicar «Las Cañitas decayó» en 2026.**

**Y contrasta con nuestro propio dato:** la base le asigna **361 locales**. Un circuito que perdió sus bares emblemáticos y conserva trescientos sesenta locales no está vacío — está haciendo otra cosa.

Eso plantea una figura que el Atlas todavía no tiene y que probablemente necesite: **la mutación a escala de zona.** La capa de memoria tiene `mutado` para un local que sigue vivo y cambia lo que es. Las Cañitas parece ser exactamente eso a nivel de polo: **la oferta sigue, la identidad cambió.** No es `extinguido` ni es `activo`.

Y es la clase de cosa que a la Dirección le sirve más que un ranking: **un polo cuya reputación va veinte años atrasada respecto de su oferta.** Si es cierto, es información de política; si no lo es, es un rumor que conviene desmentir con datos propios.

**Recomiendo una ronda de vigencia sobre Las Cañitas antes de escribir su ficha**, con el eje Báez y el rectángulo Arce–Arévalo–Ortega y Gasset–Báez como universo. Es acotado —veinte manzanas— y es la única de las tres subzonas donde la evidencia sugiere que la reputación y el estado no coinciden.

---

## Lo que necesito para cerrar esto

**Uno.** Las tres verificaciones geométricas de la hipótesis, arriba. Un `intersection` decide.

**Dos.** **Qué son R08 y R21.** El solape de 49,7 hectáreas quedó como el mayor abierto después de Chacagiales, y no sé qué zonas son. Si alguna es del entorno de Palermo, entra en este mismo nudo y conviene resolverlo junto y no aparte. Con los dos nombres salgo a buscarles la evidencia documental, que es lo que funcionó con Colegiales.

**Tres.** **Las calles de la cola de R20**, que sigue pendiente del pedido anterior. Es el 53 % de los locales de esa referencia y no le puedo buscar evidencia sin saber de qué tramo se trata.

---

## Y una observación sobre las tres, que vale para el criterio

Soho, Hollywood y Cañitas **no son barrios ni figuras administrativas**. Son denominaciones de uso, nacidas del mercado inmobiliario y de la prensa, que el propio Estado terminó adoptando —el sitio oficial de turismo las usa y las delimita—.

Es el mejor ejemplo disponible de la cláusula de la definición que más peso tiene: **«un polo no está acotado administrativamente, y su delimitación responde a evidencia territorial y gastronómica, no a los límites de un barrio».** Palermo como barrio son unas mil quinientas hectáreas y no significa nada gastronómicamente. Palermo como sistema de tres subzonas con nombre de uso, delimitadas por avenidas que la gente reconoce, sí.

**Si el Atlas necesitaba un caso para justificar que sus polos no coincidan con los barrios, es éste** — y conviene que la sección II lo use, porque es el que cualquier lector porteño entiende sin explicación.
