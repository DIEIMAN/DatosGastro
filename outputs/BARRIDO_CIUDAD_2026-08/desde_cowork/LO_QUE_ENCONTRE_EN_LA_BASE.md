# La base gastronómica, revisada

**27.727 locales.** Dos cosas revisadas: cómo están puestas las categorías, y si hay repetidos.
Todo está en el Excel; esto es el resumen de qué apareció.

---

## 1 · Las categorías estaban en cuatro idiomas a la vez

**El campo de categoría tenía 140 etiquetas distintas para lo que son 21 rubros.** El problema no
es que estuvieran mal puestas: es que cada fuente escribe en su propio código y nadie las había
unificado.

| lo mismo, escrito de cuatro maneras | quién lo escribe así |
|---|---|
| `RESTAURANTE` | los padrones del GCBA |
| `Restaurante` | OpenStreetMap |
| `restaurant` | Overture |
| `argentine_restaurant`, `italian_restaurant`… | Overture y All The Places |

Pasaba con todos: `CAFE` / `CAFÉ` / `Cafe` / `cafe` / `coffee_shop` / `cafeteria` eran seis
etiquetas para cafetería. `PIZZERIA` / `Pizzeria` / `pizza_restaurant`, tres para pizzería.

**Quedaron 21 rubros**, y el diccionario completo —las 140 etiquetas, una por una, con a qué rubro
va cada una— está en el Excel y **se puede editar**. Si cambiás algo ahí, decime y vuelvo a correr
la base entera.

| rubro | locales | | rubro | locales |
|---|---:|---|---|---:|
| Restaurante | 6.259 | | Empanadas | 463 |
| Cafetería | 3.669 | | Pastelería | 461 |
| Comida al paso | 3.468 | | Confitería | 452 |
| Panadería | 3.287 | | Cervecería | 340 |
| Bar | 2.689 | | Rotisería | 337 |
| Pizzería | 2.499 | | Sandwichería | 119 |
| Heladería | 2.140 | | Pub | 96 |
| Parrilla | 1.086 | | Hamburguesería | 79 |
| | | | Vinería | 48 |
| | | | Catering y delivery | 35 |
| | | | **Bodegón** | **33** |
| | | | Casa de té | 18 |
| | | | Sin clasificar | 149 |

**Además del rubro quedaron dos columnas nuevas que antes estaban escondidas adentro de la
etiqueta en inglés:** *cocina* (peruana, japonesa, italiana, armenia…) y *atributos* (kosher, sin
TACC, vegetariana, food truck, tenedor libre). Eso ya se puede filtrar.

---

## 2 · Bodegón no existe en ninguna fuente

**Ninguna de las siete fuentes tiene el rubro bodegón.** Cero etiquetas. Los 33 que aparecen los
saqué del **nombre del local** —«A Mis Viejos Bodegón», «Bodegón Alvear», «Alma de Bodegón»—, y
las fuentes los tenían como Restaurante, Comida al paso o Bar.

Y hay **110 más** que el nombre sugiere sin decirlo: cantina, fonda, taberna, pulpería, almacén,
casa de comidas. **Ésos no los toqué** — están listados en su hoja para que los decidas vos, que es
la clase de decisión que ninguna fuente puede tomar.

> Si el bodegón va a ser una categoría del trabajo que viene, **hay que construirla**. No se puede
> importar: no está en ningún lado.

---

## 3 · Cuando el nombre y la fuente se contradicen, gané al nombre

**648 locales tenían un rubro en la etiqueta y otro en el nombre.** «Pizzería La Guitarrita»
etiquetada como *Comida al paso*, «Confitería Ideal» como *Bar*, «Rotisería La Nueva Salta» como
*Comida al paso*. En esos casos adopté el del nombre, y **cada fila dice cuál mandó**, así que se
puede revertir en bloque.

Los números: 26.241 rubros salen de la etiqueta, 689 de una etiqueta que coincide con el nombre,
648 del nombre contra la etiqueta, y 149 no tienen dato.

---

## 4 · Repetidos: menos de los que esperaba, y uno que no se puede resolver

| qué se buscó | grupos | locales | qué tan seguro |
|---|---:|---:|---|
| mismo nombre **y** misma dirección | 29 | 58 | **es el mismo local dos veces** |
| nombre casi igual a menos de 30 m | 60 | 120 | **casi seguro: es un error de tipeo** |
| mismo nombre a menos de 60 m | 25 | 50 | probable, salvo cadenas |
| misma dirección, distinto nombre | 331 | 1.195 | la mayoría **no** son repetidos |

Los del segundo grupo son los más lindos de ver, porque muestran de dónde viene el problema: **«Le
Molin de la Fleur», «Le Moulin de la Fleur» y «Le Maulin de la Fleur»**, tres registros a cuatro y
veinte metros, son una sola panadería mal tipeada en tres fuentes. Igual «Parrilla El Litorel» y
«El Litoral». «El Viejo Vulcano» y «El Viejo Volcano». «Almacén de Pizza» y «Almacén de Pizzas».

**En total, entre 100 y 230 locales repetidos sobre 27.727.** Es poco: el apareo funcionó bien.

### El que no se puede resolver desde el escritorio

**13.783 locales no tienen nombre**, y 10.890 de ésos son del Relevamiento de Usos del Suelo, que
trae parcela y punto y nada más. **Sin nombre ni dirección no hay con qué compararlos**, y por eso
ninguno de sus 10.890 registros se apareó nunca con otra fuente.

Lo medí: **2.524 de esos puntos caen a menos de 10 metros de un local con nombre.** No los marqué
como repetidos, y la razón es honesta — **a diez metros, en una cuadra comercial, también están dos
puertas contiguas**. Ese número acota por arriba un posible doble conteo; no lo demuestra.
Resolverlo es ir a la parcela. Quedan listados aparte, ordenados por distancia, por si algún día se
recorre.

---

## 5 · 148 que capaz no son gastronómicos

Aparecieron kioscos, fiambrerías, distribuidoras, una farmacia, un lavadero y un vivero. Algunos
llegaron con la etiqueta genérica de Overture, que mezcla gastronomía con comercio de alimentos:
«Distribuidora industria frigorífica», «MG Mayorista», «Mercado del Queso», «lashermanas_polleria».

**No saqué ninguno.** Están en su hoja con una columna para decidir, porque el borde entre
gastronomía y comercio de alimentos es una definición del trabajo, no un dato.

---

## Cómo seguir

El Excel tiene las celdas editables en amarillo. Lo más rendidor, en orden:

1. **El diccionario de rubros** — mirarlo entero es media hora y define todo lo demás.
2. **Los 60 pares con nombre casi igual** — es la lista más corta y la más segura de todas.
3. **Los 110 posibles bodegones** — si el rubro va a existir, esto es de dónde sale.
4. **Los 148 a revisar** — define qué entra y qué no en «gastronómico».

Y una que no está en el Excel porque no es una decisión de escritorio: **el 39 % de la base son
puntos sin nombre**. Todo lo que se quiera hacer por nombre, marca o rubro fino, se hace sobre los
13.944 que sí lo tienen.
