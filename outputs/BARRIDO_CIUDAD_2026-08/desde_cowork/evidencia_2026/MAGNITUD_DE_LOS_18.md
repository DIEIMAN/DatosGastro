# Los dieciocho sin perímetro dejan de no tener ninguna cifra

**9 de agosto de 2026** · datos en `magnitudes_sin_perimetro.csv`, reproducible con `magnitudes_18.py`

---

## El problema

Dieciocho de los cuarenta y un polos admitidos **no tienen perímetro trazado**. Su geometría en el
repositorio es el polígono administrativo del barrio que los contiene, que es un provisorio: **dibujar
el barrio y llamarlo polo diría que el polo de Almagro son las 405 hectáreas del barrio de Almagro**,
y eso es falso.

Por eso sus fichas no publican superficie ni cantidad de locales. **Correcto, y a la vez insatisfactorio:**
la primera pregunta que hace cualquier lector es «¿cuánto hay ahí?», y responder «no lo podemos decir
todavía» es exacto y no ayuda a nadie.

## Lo que sí se puede medir sin inventar un perímetro

**La masa gastronómica concentrada dentro del barrio que contiene al polo.** No es el polo, y se dice
que no lo es. Pero es una cifra medida sobre un objeto declarado, auditable y reproducible: las
concentraciones detectadas por densidad **cuya superficie cae en más de un 50 % dentro de ese barrio.**

| polo | dentro del barrio de | concentraciones | locales | ha concentradas | ha del barrio |
|---|---|---:|---:|---:|---:|
| **Z47** Monserrat y Congreso | Monserrat | 4 | **466** | 52,0 | 220,0 |
| **Z37** Almagro | Almagro | 4 | **455** | 118,0 | 405,3 |
| **Z35** Balvanera · Once | Balvanera | 4 | **425** | 83,5 | 434,4 |
| **Z32** Liniers · Mercado Andino | Liniers | 2 | **370** | 147,7 | 437,6 |
| **Z40** Nueva Pompeya y Parque Patricios | Pompeya y Parque Patricios | 3 | **333** | 172,0 | 870,1 |
| **Z54** Nueva Pompeya · eje Av. Sáenz | *el mismo* | 3 | *333* | *172,0* | *870,1* |
| **Z46** Retiro | Retiro | 2 | **201** | 18,2 | 466,6 |
| **Z33** Mataderos | Mataderos | 3 | **180** | 71,8 | 740,1 |
| **Z52** La Boca · Almirante Brown y Necochea | La Boca | 2 | **157** | 37,6 | 504,0 |
| **Z53** La Boca · Caminito y Vuelta de Rocha | *el mismo* | 2 | *157* | *37,6* | *504,0* |
| **Z44** Villa Ortúzar | Villa Ortúzar | 1 | **147** | 63,4 | 185,5 |
| **Z50** Barracas · Av. Montes de Oca | Barracas | 2 | **114** | 41,5 | 795,9 |
| **Z51** Barracas · Iriarte, California y Vieytes | *el mismo* | 2 | *114* | *41,5* | *795,9* |
| **Z31** Villa Luro | Villa Luro | 1 | **94** | 25,1 | 256,8 |
| **Z41** Núñez | Núñez | 2 | **92** | 12,4 | 449,9 |
| **Z28** Monte Castro | Monte Castro | 2 | **89** | 15,1 | 262,9 |
| **Z27** Villa Santa Rita | Villa Santa Rita | 1 | **54** | 10,5 | 215,5 |
| **Z39** Parque Avellaneda | Parque Avellaneda | 1 | **50** | 24,6 | 473,5 |

**Los dieciocho polos caen dentro de quince barrios, no dieciocho: tres barrios contienen dos polos
cada uno** — Barracas, La Boca y el par Pompeya–Parque Patricios. Sus filas están en cursiva porque
repiten la cifra del barrio, **y sumar la columna las contaría dos veces.**

**Deduplicado, el conjunto son 3.227 locales en 893,5 hectáreas concentradas**, repartidos en 38
concentraciones distintas.

---

## Las tres cosas que hay que decir con esta cifra, siempre

**No es la cifra del polo.** Es la del barrio. El polo va a ser más chico —a veces mucho más chico—
y sólo se sabrá cuánto cuando se trace el perímetro.

**No se suma a los 12.688.** Estas concentraciones **ya están adentro** de las 124 que producen esa
cifra. Sumarlas sería contar dos veces.

**Y la proporción concentrada varía tanto que es un dato en sí mismo.** En Villa Ortúzar y Liniers,
**un tercio del barrio está adentro de una concentración detectada**; en Núñez, el 2,8 %. **Un
porcentaje alto dice que el polo y el barrio casi coinciden y que trazar el perímetro va a cambiar
poco. Uno bajo dice lo contrario**, y avisa exactamente dónde el provisorio del barrio está mintiendo
más.

> **Ordenados por esa proporción, los que más urge delimitar son los de arriba de la lista por
> locales y abajo por porcentaje: Retiro (3,9 %), Núñez (2,8 %), Villa Santa Rita (4,9 %), Monte
> Castro (5,7 %) y las dos de Barracas (5,2 %).** Ahí el barrio no se parece al polo.

---

## Qué destraba esto

**Cada una de las dieciocho fichas pasa de no tener ninguna cifra a tener una cifra medida, con su
objeto declarado.** No reemplaza al perímetro: lo espera diciendo qué se sabe mientras tanto.

Y da una lista de prioridad al repositorio: **empezar por los barrios donde la proporción concentrada
es más baja**, porque son aquellos en los que el provisorio se aleja más de lo que se va a publicar.
