# Parte X · Los límites de la base

*Va entre los límites de la edición técnica. Ronda 10 · 8 de agosto de 2026.*

---

## X.1 · Casi la mitad de la base no se puede ubicar por dirección

**El 46,6 % del universo núcleo no tiene `direccion_norm`.** De los 23.981 locales que se usaron
para construir los 124 polos, **11.170 no traen dirección normalizada**: tienen coordenadas, tienen
categoría, tienen fuente, y no tienen calle ni altura utilizable.

No es un faltante marginal ni un problema de prolijidad. **Es una restricción sobre qué preguntas
se le pueden hacer a la base.**

### Qué se puede y qué no

| pregunta | ¿se puede? | por qué |
|---|---|---|
| ¿cuántos locales hay dentro de este polígono? | **sí** | es puramente geométrica: usa el punto |
| ¿cuál es la densidad de esta zona? | **sí** | ídem |
| ¿este polo contiene tal hito? | **sí** | ídem |
| **¿de qué calles se compone esta zona?** | **no directamente** | necesita la dirección |
| **¿cuántos locales hay sobre tal avenida?** | **no directamente** | ídem |
| ¿cuántos locales en tal altura de tal calle? | **no** | ídem |

**Toda asignación de locales a un objeto que no sea puramente geométrica está afectada.** El
agrupamiento por texto de dirección pierde, en promedio, cuatro de cada nueve puntos, y los pierde
**sin avisar**: la tabla sale, suma, y describe la mitad del territorio que dice describir.

### Cómo se descubrió, y qué se hizo

Al pedir «de qué calles se trata la cola de R20», el primer reparto —agrupando por
`direccion_norm`— atribuyó **22 de 54 locales** y dejó 40 sin calle. La tabla parecía completa: no
faltaba ninguna columna, ninguna celda estaba vacía, y las diez calles que listaba eran calles
reales de la cola.

El reparto se rehízo **por eje más cercano**: a cada punto se le busca el eje del callejero oficial
a menos de 120 m y se le atribuye ese nombre. Con eso se repartieron **31 de 31**. La misma
pregunta, dos métodos, y el primero contestaba con menos de la mitad del material sin declararlo.

> **La regla que queda:** cuando una pregunta necesita el nombre de la calle, el nombre se resuelve
> **por geometría contra el callejero oficial**, no por el texto de la dirección. Y si por algún
> motivo hay que usar el texto, **el porcentaje de puntos atribuidos se reporta en la misma tabla**.

### Por qué esto importa más que buena parte de lo demás

Las correcciones de esta semana —el anclaje de R20, la franja de Colegiales, el nudo de Palermo—
son cada una un objeto. Ésta es transversal: **afecta a cualquier tabla que reparta locales por
calle, por corredor o por eje comercial**, incluidas las que todavía no se escribieron. En
particular, condiciona el cruce con los 48 ejes comerciales del IDECBA, que están delimitados
exactamente así: por calle y altura.

**No se corrige geocodificando más.** Se corrige eligiendo el método correcto para la pregunta, y
declarando la cobertura cuando no queda otra.

---

## X.2 · El nombre oficial de una calle puede cambiar a lo largo de la calle

**67 corredores del callejero oficial están partidos en más de un nombre**, y en la mayoría el
reparto es muy desparejo:

| corredor | un nombre | el otro |
|---|---|---|
| Av. Córdoba | `CORDOBA` 286 m (3 %) | `CORDOBA AV` 7.877 m (97 %) |
| Av. Boedo | `BOEDO` 539 m (17 %) | `BOEDO AV` 2.582 m (83 %) |
| García del Río | `GARCIA DEL RIO` 1.631 m (50 %) | `GARCIA DEL RIO AV` 1.617 m (50 %) |
| Avellaneda | `AVELLANEDA` 2.211 m (37 %) | `AVELLANEDA AV` 3.836 m (63 %) |

Buscar una calle por su nombre devuelve **una de las dos mitades**, sin error y sin aviso. Tres
rondas distintas tropezaron con esto antes de que se lo reconociera como propiedad de la fuente y
no como bicho: el `esq` adentro de Esquiú, Independencia, y García del Río.

**Lo que produjo:** el «tramo Av. Cabildo–Av. Balbín» que define el núcleo documentado de R20 no
existía. García del Río no cruza Av. Cabildo —esa mitad se llama `GARCIA DEL RIO AV.`— y el
cortador de tramos ancló el extremo oeste **761 m fuera del eje** y devolvió un resultado. La cola
declarada pasó de 41 % de superficie y 53 % de locales a **47 % y 30 %**.

### Lo que se hizo

- `callejero_canonico.py` agrupa nombres por raíz **y** contacto geométrico. Las dos condiciones:
  sólo la raíz uniría Av. San Martín con la calle San Martín, que están a 6,6 km; sólo el contacto
  uniría cualquier par de calles que se cruzan.
- `test_callejero_canonico.py` — 14 pruebas, **con casos negativos**. Un test que sólo verificara
  que los tres casos conocidos se unen pasaría también con una función que une todo con todo.
- `tramo_entre()` **falla ruidoso**: un corte a más de 40 m del eje levanta `AnclaFueraDelEje` en
  vez de devolver un tramo inventado. Se verificó que Z23 Flores, que estaba bien, sigue dando los
  mismos 1.270 m.

> **La regla que queda:** todo eje se pide canonicalizado. Y una delimitación cuyo corte no toca el
> eje **no produce tramo** — se declara y se revisa, no se aproxima.
