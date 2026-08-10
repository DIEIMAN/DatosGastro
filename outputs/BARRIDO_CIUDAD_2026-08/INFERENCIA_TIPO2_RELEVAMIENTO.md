# Inferencia del vocabulario `TIPO2` del Relevamiento de Usos del Suelo

**Generado por `scripts/barrido_ciudad/documentar_inferencia_tipo2.py` desde el mapeo vivo
de `perfilar_usos_suelo.py`. No editar a mano: regenerar.**

## Por qué este documento es necesario

El Relevamiento **sostiene el mapa**: la ablación con control aleatorio midió que sin él la
corrida colapsa, y que sacar la misma cantidad de puntos al azar no la rompe ninguna de las
cinco veces. Y su documentación oficial **no publica el diccionario de códigos de `TIPO2`**.

Por la decisión de alcance del 2026-08-06 —sin pedidos fuera de la Dirección— **el
diccionario oficial no va a llegar**. La inferencia deja de ser provisoria: es lo que hay, y
por eso queda acá valor por valor.

> **Si esta clasificación está corrida, el mapa se mueve.** Un valor mal asignado al anillo
> núcleo agrega o saca parcelas de la fuente que sostiene la corrida. Esta advertencia viaja
> con el mapa, no sólo con este documento.

## Cómo se estableció

Por conteo sobre el archivo (471 valores distintos de `TIPO2`), con un criterio único:
**simetría con el mapeo de habilitaciones** (decisión de Diego, 2026-08-05). Cada valor va
al anillo donde ya cae su equivalente en `fact_habilitacion_gastronomica.csv`. El criterio
no es «qué nos parece que es» sino «dónde lo pusimos ya en la otra base», para que las dos
sigan siendo comparables.

Sólo se consideran parcelas con `TIPO1 = UNICOMERCIAL` y `ESTADO = ACTIVO`.

## Anillo núcleo · gastronomía de atención al público

| valor de `TIPO2` | anillo | categoría del proyecto | parcelas en la fuente |
|---|---|---|---:|
| `RESTAURANTE` | núcleo | Restaurante | 2715 |
| `SUSHI` | núcleo | Restaurante | 18 |
| `BAR` | núcleo | Bar | 904 |
| `CERVECERIA` | núcleo | Bar | 252 |
| `CAFÉ` | núcleo | Cafe | 1728 |
| `CAFÉ (VTA AL PASO)` | núcleo | Cafe | 89 |
| `PIZZERIA` | núcleo | Pizzeria | 1011 |
| `PARRILLA` | núcleo | Parrilla | 343 |
| `COMIDAS PARA LLEVAR` | núcleo | Comida al paso | 1157 |
| `COMIDA RAPIDA` | núcleo | Comida al paso | 465 |
| `EMPANADAS` | núcleo | Comida al paso | 390 |
| `ROTISERIA` | núcleo | Comida al paso | 310 |
| `SANDWICHERIA` | núcleo | Comida al paso | 88 |
| `HELADERIA` | núcleo | Heladeria | 797 |

### Las dos asignaciones que hubo que justificar

- **`CERVECERIA` → núcleo (Bar).** En el padrón, «despacho de bebidas», «wisquería» y
  «cervecería» caen todas en Bar. Se respeta esa simetría.
- **`SUSHI` → núcleo (Restaurante).** No tiene rubro propio en el padrón; su equivalente
  más cercano —«restaurante», «cantina»— está en Restaurante.

## Anillo ampliado · comercio de alimentos, fuera del universo principal

| valor de `TIPO2` | anillo | categoría del proyecto | parcelas en la fuente |
|---|---|---|---:|
| `PANADERIA` | ampliado | Panaderia | 1716 |
| `CONFITERIA` | ampliado | Pasteleria | 386 |

### La asignación discutible, declarada como tal y NO corregida

**`CONFITERIA` → ampliado (Pastelería).** Es discutible y se sabe: una confitería porteña es
un café con servicio de mesa, no una pastelería. Se mantiene porque el padrón la manda a
Pastelería (1.721 habilitaciones) y **corregirla de un solo lado rompería la comparación
entre las dos bases**. Si se cambia, se cambia en habilitaciones y en el Relevamiento en la
misma corrida, y se recalcula todo. Hoy no se toca — y queda escrito para que quien audite
sepa que es una decisión y no un descuido.

Es, además, la asignación con más impacto potencial: el anillo ampliado no entra a la
poligonización, así que mover `CONFITERIA` al núcleo cambiaría el universo del mapa.

## Valores que la búsqueda por palabra clave trae y NO son gastronomía

Descartados explícitamente. La lista importa tanto como la de arriba: son los falsos
positivos que una búsqueda ingenua por «café», «bar» o «gastronómico» habría incorporado.

| valor de `TIPO2` | por qué se descarta |
|---|---|
| `BARBERIA` | no es gastronomía; entra por parecido de cadena de texto |
| `ALIMENTOS PARA MASCOTAS` | comercio de alimentos, no atención al público gastronómica |
| `VINOS (VENTA)` | venta de bebidas para llevar, sin salón |
| `BEBIDAS ALCOHOLICAS` | venta para llevar, sin salón |
| `FABRICA DE PASTAS` | elaboración; además es el universo de otro subproyecto |
| `EQUIP. GASTRONOMICO` | venta de equipamiento, no gastronomía |
| `VENTA DE CAFÉ (PRODUCTOS)` | venta del producto, no cafetería |
| `REPARACION DE HELADERAS` | servicio técnico |
| `HELADERAS Y BALANZAS COMERCIALES (VTA)` | venta de equipamiento |
| `RESTAURACIONES` | restauración de bienes; falso positivo por «restaur-» |
| `INSTITUTO DE GASTRONOMIA` | enseñanza, no oferta gastronómica |
| `VENTA POR MAYOR DE ALIMENTOS Y BEBIDAS` | mayorista, sin atención al público |
| `GALERÍA BARRIAL` | contenedor de locales, no un local |

## Cómo auditar esto sin el diccionario oficial

1. Tomar una muestra de parcelas de cada valor de `TIPO2` del núcleo y mirar la dirección
   en la calle. Es lento y es el único control real disponible.
2. Contrastar el conteo por barrio contra el padrón de habilitaciones del mismo barrio: un
   valor mal asignado se ve como una discrepancia concentrada en un rubro.
3. Revisar primero `CONFITERIA`, `CERVECERIA` y `SUSHI`, que son las tres asignaciones que
   no salieron directas del padrón.

## Un defecto de codificación que hay que conocer

La fuente llega con doble codificación CP437/UTF-8 (`CAF├ë` por `CAFÉ`). No es cosmético:
**sin reparar, `CAFÉ` desaparece del vocabulario y se pierden 1.803 parcelas sin que ninguna
corrida falle.** El reparador y su control están en `perfilar_usos_suelo.py`.

