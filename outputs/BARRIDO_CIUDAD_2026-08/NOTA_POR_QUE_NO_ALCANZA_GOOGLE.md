# Por qué el Atlas no se puede hacer con Google

**Dirección General de Desarrollo Gastronómico · agosto de 2026**
Nota breve para responder tres preguntas que aparecen siempre.

---

## 1 · «¿Esto no se saca de Google?»

Se probó, se midió, y no alcanza. No por poco.

Se tomó **Villa Crespo**, que es una de las zonas donde la Dirección hizo su propio
relevamiento y sabemos cuántos locales hay: **646**.

Sobre esa misma zona se consultó la API oficial de Google Places con tres tipos de búsqueda
distintos, dividiendo el territorio en celdas cada vez más chicas hasta agotar el método.
Resultado: **81 locales**. El **12 %**.

Para descartar que hubiéramos consultado mal, se repitió la misma consulta media hora después.
De los locales encontrados, **62 fueron exactamente los mismos, y la segunda consulta agregó
uno solo**. Con eso se puede estimar cuántos locales Google llegaría a mostrarnos alguna vez en
esa zona, por más veces que preguntáramos: **alrededor de 77**.

Setenta y siete contra seiscientos cuarenta y seis. No es que preguntamos mal: es que Google no
tiene el resto, o no lo muestra.

**Por qué.** Google no es un padrón, es un buscador. Está hecho para responderle a una persona
que busca dónde comer, no para censar una zona. Devuelve una lista ordenada por relevancia y
cortada a cierta profundidad. Y sólo conoce lo que tiene presencia digital: un bodegón sin
ficha, una rotisería que nunca reclamó su perfil o un bar cuya página quedó sin actualizar,
para Google no existen.

**Qué sí aporta, y por eso no se descarta.** Los locales que sí encuentra vienen con el dato de
si están abiertos o cerrados **hoy**. Ninguna de nuestras fuentes oficiales tiene eso: el
padrón de habilitaciones no registra bajas, y el relevamiento de usos del suelo del Gobierno se
hace por turnos, un barrio por año. Google pasa entonces de ser una fuente para contar a ser
una **muestra de vigencia**: no dice cuántos locales hay, dice cuáles de los que conoce siguen
funcionando.

---

## 2 · «¿Cuánto nos falta de la Ciudad?»

El Atlas publicado cubre 22 zonas. Cruzando esas zonas contra los polígonos de barrio:
**16 barrios no reciben ni el 1 % de superficie de ninguna de ellas**, y 21 quedan por debajo
del 5 %.

Eso ya está resuelto a nivel documental. Aplicando una misma receta de conteo a dos fuentes
oficiales —el padrón de habilitaciones de la AGC y el Relevamiento de Usos del Suelo de
Estadística y Censos— **los 48 barrios de la Ciudad tienen dato y ninguno queda en cero**.

Entre lo que apareció:

- **Núñez** 121 direcciones gastronómicas · **La Boca** 55 · **Barracas** 103 ·
  **Parque Patricios** 87 · **Mataderos** 92
- Y el oeste, que no estaba en el plan y resultó más grande que el sur: **Flores** 248
  direcciones, más que Villa Urquiza, que sí tiene ficha propia en el Atlas.

---

## 3 · «¿Qué falta para completarlo?»

Falta lo mismo que hizo posibles las cuatro zonas mejor medidas del Atlas: **el relevamiento
propio de la Dirección**.

La razón es aritmética. Sobre una misma zona, con el mismo perímetro:

| fuente | recupera |
|---|---:|
| Relevamiento propio de la Dirección | 100 % (es la referencia) |
| Relevamiento de Usos del Suelo | 29 % |
| Padrón de habilitaciones | 18 % |
| Google Places | 12 % |

Ninguna fuente de escritorio se acerca. Cada una aporta algo distinto —cobertura pareja el
Relevamiento, respaldo oficial el padrón, vigencia Google— y por eso se usan las tres. Pero
para que una zona nueva quede al nivel de Caballito o Villa Crespo, hay que relevarla con el
método propio.

**Lo que se propone.** Los 20 barrios del oeste y el sur salen ahora como fichas documentales,
con la salvedad declarada y sin cifra comparable. **Núñez y La Boca** —las dos zonas que la
Dirección quiere incorporar con nivel de ficha completa— esperan relevamiento propio, y ya
tienen su piso documental calculado para poder controlar el resultado cuando llegue.

---

## Un hallazgo aparte, que conviene conocer

Al construir la base se detectó que **el 22,6 % del padrón público de habilitaciones de la AGC
son asientos replicados**: un mismo permiso figura contra cada número de puerta del frente del
inmueble. Un solo permiso llega a aparecer en 15 puertas, y una parcela reúne 75 números sobre
cuatro calles.

Está probado contra la partida catastral del propio archivo y no afecta ninguna cifra publicada
del Atlas, porque la regla de conteo ya excluía esos casos. Pero significa que **la cantidad de
trámites de un barrio no mide su volumen de oferta**, y que cualquier organismo o particular que
use ese dataset abierto contando por dirección está contando lo mismo mal. Se preparó una
consulta técnica a la AGC para confirmarlo.

---

*Todas las cifras de esta nota son reproducibles desde el repositorio del proyecto y están
documentadas en `outputs/BARRIDO_CIUDAD_2026-08/`.*
