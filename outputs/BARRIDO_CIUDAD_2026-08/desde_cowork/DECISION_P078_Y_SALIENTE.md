# P078 y el saliente N–NE · decisión

**6 de agosto de 2026** · Responde al reporte del repositorio que midió la excepción de P078 y la
encontró del otro lado de la banda declarada.

---

## 1 · La excepción de P078 queda rechazada, y el motivo refutado se guarda

El motivo que escribí era: *el 21 % que queda afuera de las partes son los «tramos sin oferta»
que R01 documenta*. La medición lo refutó y la refutación es limpia:

| | partes de P078 | los 123 de afuera |
|---|---:|---:|
| entre dos partes | 69 % | **9 · 7,3 %** |
| colgando de una sola parte | 48 % | **114 · 92,7 %** |
| adentro de R01 | 51 % | **12 · 10 %** |

Y el argumento se contradecía solo: si un tramo no tiene oferta, no tiene locales que expliquen
el faltante. Medido por el otro extremo, el hueco entre S1 y S2 mide ~300 m y tiene 6 locales.
No es un tramo sin oferta.

**El motivo no se cambia. La excepción no se firma.** Queda registrada como refutada, con estos
números al lado. Ese registro es el producto: una excepción que se midió y cayó vale más que una
que nunca se puso a prueba.

## 2 · Por qué «P078 desborda R01» no sirve como motivo de reemplazo

La lectura que el repositorio ofrece —las partes son la zona publicada, el 21 % es lo que se
extiende más allá del perímetro— es probablemente cierta. Pero **no es un motivo para la
partición en tres**: es una afirmación sobre el perímetro de R01, no sobre la estructura interna
de P078. Sostiene otra conclusión, no la misma.

Usarla para firmar la excepción que ya cayó es exactamente lo que R3 prohíbe. El repositorio
tiene razón en no haberla firmado.

Donde sí vale es en otro lado: **R01 tiene 21 % de la actividad de su propio polo afuera del
perímetro publicado**. Eso es un hallazgo sobre la zona publicada y va a la conversación de la
V3, con su número, no a la justificación de una partición.

## 3 · Lo que sí se puede correr, y cómo se corre bien

La partición de P078 en tres nunca se probó contra la regla que este proyecto ya tiene escrita
—las tres pruebas de `CUANDO_DOS_POLOS_SON_UNO.md`, que salieron de Recoleta y de Belgrano—. Esa
regla es anterior a este caso y no se inventó para salvarlo, así que aplicarla no es cambiar el
motivo: es correr por primera vez la prueba que correspondía.

Con la lectura escrita antes, como en Belgrano:

```
Prueba 2 · estabilidad de la partición — barrido del umbral de continuidad
  el número de partes se mantiene en 3 en un rango ≥ 60 m  → la partición es estable, se sostiene
  el número cambia dentro de ±40 m del umbral elegido      → arbitraria, P078 va entero
  aparecen 4+ piezas de tamaño comparable                   → ni 3 ni 1: se reabre el caso

Prueba 3 · lectura — cada parte necesita las dos cosas
  nombre de uso corriente  +  respaldo documental propio
  (Belgrano R sobrevivió con 2 locales por el respaldo, no por el tamaño)
```

Si P078 son Soho, Hollywood y Cañitas, la prueba 3 la pasa de taquito. La que decide es la 2, y
es la que falta.

---

## 4 · El saliente N–NE: no es un polo, y no se toca el mínimo

108 locales, 88 % afuera de toda zona publicada, dirección firme al N–NE (R = 0,70, rumbo 36°).
Tres bloques: 35, 23 y 12. El más grande queda **5 locales por debajo del mínimo de 40**.

**El mínimo no se baja.** Está anclado en la zona publicada más chica del Atlas, se fijó para
todo el universo antes de mirar qué sobrevivía, y bajarlo a 35 para rescatar este caso es el
ejemplo de manual de R3. Un mínimo que se mueve una vez ya no es un mínimo para ninguno de los
otros 123 polos.

Pero *no es un polo* tampoco quiere decir *no hay nada ahí*, y esa es la distinción de R7:

> se escribe «no alcanza el mínimo declarado de 40 locales por 5», no «no se identificó actividad».

Tres cosas concretas, ninguna de las cuales requiere mover nada:

**a · Registro de candidatos bajo el mínimo.** Un CSV chico —`CANDIDATOS_BAJO_MINIMO.csv`— con
todos los conglomerados que quedaron entre, digamos, 25 y 39 locales, con su tamaño, su barrio y
su distancia al polo más cercano. Es el archivo que vuelve honesta cualquier frase del tipo «no
se identificaron polos en X»: el lector ve qué había y por qué no calificó. Y es el insumo de la
próxima corrida, cuando la cobertura mejore.

**b · La pregunta que sí es medible: ¿de quién es la cola?** El saliente apunta al N–NE, hacia
Chacarita y Colegiales. Hoy se lo está leyendo como cola de P078 porque de ahí salió, pero la
dirección sugiere lo contrario. Si hay un polo del otro lado, la separación entre el bloque de 35
y ese polo se mide con el mismo cálculo de envolventes de la tabla de uniones — y bajo 50 m es
una sola zona por precedente Recoleta, sin discusión y **sin tocar el mínimo**, porque unir no es
bajar un umbral.

Ese es el camino legítimo por el que el bloque de 35 puede terminar adentro de un polo: por
contigüidad con algo que ya califica, no por indulto.

**c · Si no es de nadie, es un hallazgo acotado.** 108 locales con dirección propia y 88 % afuera
del mapa publicado se reportan como tales en la conversación de la V3: *concentración lineal
detectada, no alcanza el criterio de polo, se deja registrada con su número*. Sin ascenderla y
sin borrarla.

---

## 5 · En una línea

La excepción cae y se guarda caída. La partición de P078 se decide con la prueba de estabilidad,
que es vieja y no se escribió para este caso. El mínimo no se mueve, y el saliente entra al mapa
sólo si alguien de al lado lo alcanza por contigüidad — si no, entra al registro de candidatos,
que es donde tiene que estar lo que medimos y no calificó.
