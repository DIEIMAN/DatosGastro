# HANDOFF · Partes nombrables, sonda de Places y material del método · 2026-08-06

Continúa `HANDOFF_POLOS_CIERRE_Y_DECISIONES_2026_08_06.md`. Rama `mercados-gastronomicos-v2`.
**Sin commit.** Ninguna cifra publicada tocada; el Atlas no se tocó.

**Google Places: 74 requests ejecutados de los 97 autorizados.** Total de agosto: 306 → **380**.

Scripts nuevos: `polos_partes_nombrables.py`, `places_sonda_barrios_flacos.py`,
`volcar_material_metodo.py`, `tests/test_normalizador_direcciones.py`.

---

## 1 · Partes nombrables · el hueco del método, medido

Barrido de continuidad de Belgrano sobre los 4 polos de 300+ locales, con su regla de aceptación
—no la de la partición—. La grilla se extendió a 20–300 m por una razón geométrica declarada: la
distancia típica entre vecinos escala con 1/√densidad, y a 8 loc/ha un piso de 40 m conecta todo
desde el primer valor.

| polo | locales | loc/ha | mejor tramo estable | cobertura | veredicto |
|---|---:|---:|---|---:|---|
| **P103** San Telmo | 342 | 7,21 | 2 partes en 55 y 70 m | 97,7 % | **PARTES ESTABLES** |
| **P078** Palermo | 585 | 5,70 | 3 partes en 40 y 55 m | **79,0 %** | **AL FILO** (falta 1,0 punto) |
| P091 Palermo | 728 | 7,88 | 2 partes en 35 y 40 m | 62,9 % | sin partes estables |
| P065 Palermo | 361 | 4,40 | 2 partes en 40 y 55 m | 53,5 % | sin partes estables |

### P078 es el hallazgo, y falla por un punto

Tres partes estables en dos umbrales consecutivos, con **79,0 % de cobertura contra un umbral de
80 %**. El umbral se fijó antes de correr y no lo moví. Muestro las partes igual, porque
esconderlas por un punto dejaría sin evidencia la única decisión que queda:

| parte | locales | loc/ha | barrios | zona publicada encima |
|---|---:|---:|---|---|
| S1 | 333 | 7,89 | Palermo (333) | R01 67 % |
| S2 | 88 | 8,50 | Palermo (72); Chacarita (13); Colegiales (3) | R01 46 %; R09 17 % |
| S3 | 41 | 10,67 | Palermo (40); Chacarita (1) | R01 66 %; R08 22 % |

Las tres caen dentro de R01 Palermo, que es respaldo documental para la condición 3. **Un criterio
editorial podría aceptarlas con el mismo derecho con que la regla las rechaza**, y esa decisión no
la toma un script.

### P091 no tiene partes, y eso responde la hipótesis original

P091 es el polo grande de Palermo y **no** se descompone: su mejor tramo estable llega al 62,9 % de
cobertura. Si Soho y Hollywood están en algún lado del borrador, están en P078 —el que queda al
filo—, no en P091.

### P103 pasa, con una salvedad de proporción

Las dos partes son 290 y 44 locales: la chica tiene el **15 %** de la grande. Belgrano dio 107 / 82
/ 23, partes comparables. Esto se parece más a «un cuerpo con un satélite» que a un polo de partes.
Pasa la regla igual y lo dejo anotado — si eso amerita publicarse como subzona es editorial.

## 2 · Places · sonda ejecutada

**74 requests de 97 autorizados. 29 de 29 celdas consultadas, ninguna saturó** (no hizo falta
refinar a 500 m). 427 puntos únicos.

> **Gasté 37 requests de más por un error mío**, y va escrito: la primera corrida leyó
> `primaryType` del JSON cuando el FieldMask pide `places.types`. La clave equivocada devuelve
> `None` en todas las filas sin que nada falle, así que la corrida terminó bien y sin rubro — o sea,
> sin poder distinguir un restaurante de un almacén, que era justamente lo que había que medir.
> Hubo que repetirla. **Ya está arreglado de raíz**: los crudos se guardan y `--solo-analisis`
> rehace el informe sin consultar nada, así que un cambio de lectura no vuelve a costar requests.

### Lo que trajo, y por qué el primer número no servía

Sobre todos los puntos, la fracción nueva daba 52,2 %. Pero la consulta «restaurantes bares y
cafés» trae también almacenes, vinotecas y delivery, que el proyecto **excluye por definición y no
por omisión**. Contarlos como faltante convertiría una diferencia de universo en un agujero de
cobertura.

```
de los 427 puntos:   246 núcleo · 178 excluidos · 3 fuera del universo
```

Sobre el universo comparable —sólo anillo núcleo, que es lo que la base mapea:

| barrio | Places núcleo | ya estaba | nuevos | % nuevos | base núcleo | nuevos / base |
|---|---:|---:|---:|---:|---:|---:|
| Villa Gral. Mitre | 43 | 16 | 27 | 62,8 % | 208 | 13,0 % |
| San Cristóbal | 50 | 23 | 27 | 54,0 % | 250 | 10,8 % |
| Villa Luro | 47 | 22 | 25 | 53,2 % | 207 | 12,1 % |
| Paternal | 42 | 23 | 19 | 45,2 % | 126 | 15,1 % |
| Villa del Parque | 64 | 41 | 23 | 35,9 % | 337 | 6,8 % |

**Fracción nueva: 49,2 % (121 de 246 puntos del núcleo). En términos de la base: 121 locales sobre
los 1.128 que tiene en esos cinco barrios, un 10,7 %.**

### La lectura, contra las dos escritas antes de correr

Salió la **ALTA**: hay faltante y queda localizado y con tamaño. Con dos calificaciones que van
pegadas al número:

- **Es una cota superior, no un promedio.** Los cinco barrios se eligieron por ser los peores según
  dos indicadores internos. No dice nada sobre Palermo ni sobre el centro.
- **No dice nada sobre vigencia.** Places descubre, no confirma. Un punto nuevo no es un local
  abierto: es una ficha que nosotros no teníamos.

Y lo que no cambia: **lo que trajo no entra a la base.** La licencia no es redistribuible. La
salida quedó en `outputs/analisis_interno/`, ignorada por Git.

## 3 · Las clases · redacción de convención

Reescrito en el informe: **4,58 locales/ha es una convención declarada, no una frontera
descubierta**, anclada a un pelo de la mediana de 5,03. Es la redacción que el §1 ya obligaba —no
hay hueco en la distribución— y con ella el refit deja de ser una amenaza: si decimos «elegimos
cortar en 4,58», un método que corta en otro lado no nos contradice, elige otra convención.

Las dos lecturas del Rand siguen escritas (0,814 con corte reescalado, 0,128 con refit de Jenks).

## 4 · Material bruto para el documento del método

`outputs/BARRIDO_CIUDAD_2026-08/material_metodo/` — **32 archivos, `INDICE.csv` y
`formulas_parejidad.csv`.** Sin prosa. El índice dice qué es cada archivo y de qué script salió; se
copian y no se enlazan, para que una corrida posterior no le cambie una tabla abajo al documento.

Cubre lo pedido: las curvas de continuidad (Belgrano como precedente, los seis, P065, los polos
grandes), las 39 uniones con su motivo de rechazo, las dos lecturas del Rand, la ablación con su
control aleatorio, el detector de lotes replicados con la prueba catastral por SMP, los factores de
captura contra las dos bases, y los dos indicadores de parejidad **con sus fórmulas y sus límites**
—porque una columna llamada `cobertura` no dice cómo se calculó—.

## 5 · Test de regresión del normalizador

`tests/test_normalizador_direcciones.py`, 7 casos, todos pasan. Incluye el bug original («Esquiu»),
la familia entera del mismo error, el caso positivo (`esq.` que sí es esquina), los rangos con
barras, las colas de país con y sin punto, y **un caso negativo que importa**: «Ciudad de la Paz»
es una calle de Belgrano y cortar por «Ciudad» a secas la decapitaría.

---

## Lo que espera decisión

1. **P078: aceptar o no sus tres partes**, que fallan por 1,0 punto de cobertura. Es la decisión
   editorial que el script no puede tomar.
2. **P103: si un cuerpo de 290 con un satélite de 44 amerita publicarse como polo con partes.**
3. **Qué se hace con los 121 locales que Places encontró y no tenemos.** No entran a la base; la
   pregunta es si eso cambia algo de lo que se afirma sobre cobertura, y si amerita campo.
4. Siguen de antes: R15 Devoto (perímetro a revisar en V3), R04 Puerto Madero, las tres zonas en
   E3, la cláusula ODbL, el visto de Patricia, Bares Notables contra la normativa, Foursquare.
5. **El documento extenso del método**, que lo escribe Diego con el material de §4.

## Trampas encontradas hoy

- **Leer la clave equivocada de un JSON no falla: devuelve `None` y parece un dato ausente.**
  `primaryType` en vez de `types` costó 37 requests y una corrida entera, y el síntoma era «Places
  no devuelve el rubro».
- **Adquisición y análisis tienen que estar separados cuando la adquisición cuesta plata.** La
  lección del punto anterior, aplicada: ahora los crudos se guardan y el informe se rehace gratis.
- **Un conteo de partes sin su cobertura no distingue estructura de fragmentación**, y ya lo había
  mostrado P065. Acá volvió a decidir: P091 tiene 2 partes en dos umbrales consecutivos y aun así
  no tiene estructura, porque esas partes se llevan sólo el 62,9 %.
- **Una fracción «nueva» sin filtrar por rubro mide la diferencia de universo, no el faltante.** El
  52,2 % inicial incluía almacenes y delivery que el proyecto excluye por definición.
- **Buscar el near-miss en la fila de máxima cobertura da distancias negativas.** Hay que buscarlo
  en el mejor tramo *estable*, porque son dos condiciones distintas y fallar una no es fallar la
  otra.
