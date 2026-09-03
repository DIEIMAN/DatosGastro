# Alcance del subproyecto Panaderías

Decisión de Diego, 2026-08-27. No re-litigar sin decisión nueva.

En Casas de Pastas el corte fue "casas y fábricas de pastas, NO restaurantes italianos".
Acá el equivalente es dónde termina la panadería y empieza la confitería.

## Qué entra

**Universo A — núcleo: donde se elabora o se despacha pan.**

| Rubro F02 | Filas F02 |
|---|---|
| Elaboración de productos de panadería con venta directa al público | 502 |
| Com.Min. despacho de pan y productos afines | 242 |
| Elaboración industrial de productos de panadería, excluido galletitas y bizcochos | 64 |
| Elaboración de productos de panadería n.c.p. | 38 |

También entran por nombre "panificadora" y "fábrica de pan".

**Universo B — punto de cocción y frontera.**

| Rubro F02 | Filas F02 |
|---|---|
| Fabricación de masas y demás productos de pastelería y sandwiches. Cocción de productos de panadería cuando se reciba la masa ya elaborada | 767 |

Son panaderías en el uso corriente, pero no elaboran la masa. Se separan de A para poder
contar con y sin ellas: el número cambia según se las incluya, y esa diferencia tiene que
ser visible, no una decisión escondida en el clasificador.

También caen en B los establecimientos cuyo **nombre** dice panadería pero cuyo rubro no
es concluyente.

## Qué queda afuera

Con etiqueta propia, para poder recuperarlo si la decisión cambia. Conteos sobre filas
candidatas de F02 (una fila no es un establecimiento: el archivo está desnormalizado):

| Motivo | Etiqueta | Filas |
|---|---|---|
| Comercio sin elaboración | `sin_elaboracion` | 2.102 |
| Com.min. de masas, bombones, sandwiches (sin elaboración) | `masas_bombones_sin_elaboracion` | 1.737 |
| Confitería | `confiteria` | 1.418 |
| Pizza, fugazza, fainá, empanadas | `pizza_empanadas` | 1.301 |
| Elaboración de galletitas y bizcochos | `galletitas_y_bizcochos` | 58 |
| Fabricación de hornos (no gastronómico) | `fabricacion_de_hornos` | 27 |
| Churros y facturas fritas con venta directa | `churros_facturas_fritas` | 15 |

El detalle vive en `outputs/panaderias/panaderias_excluidos_por_motivo.csv`, y la lista
completa de filas en `outputs/panaderias/candidatos_f02_fuera_de_alcance.csv`.

**Nota sobre churros y facturas fritas (15 filas):** es el caso más discutible de la
lista. Elabora un producto de panadería y vende al público, pero el rubro no es de
panadería y quedó fuera junto con confitería. Moverlo a B es una línea en
`panaderias_patterns.py`. Queda anotado para que sea una decisión y no un olvido.

## La regla que ordena los casos ambiguos

**El rubro manda sobre el nombre.** Un local llamado "Panadería y Confitería Del Ángel"
con rubro *confitería* queda en C; un local llamado "Confitería La Vicentina S.R.L." con
rubro *elaboración de productos de panadería con venta directa* queda en A. Es la misma
regla que en pastas dejaba afuera a un restaurante llamado "La Pasta".

Consecuencia visible: hay entradas del universo A que se llaman "Confitería". Es correcto
según la regla, y conviene decirlo antes de que alguien lo lea como un error.
