# HANDOFF · Cierre del borrador de polos y decisiones aplicadas · 2026-08-06

Continúa `HANDOFF_POLOS_PRECIO_ESTRUCTURA_ANADA_2026_08_06.md`. Rama `mercados-gastronomicos-v2`.
**Sin commit. Google Places: 0 requests; el total de agosto sigue en 306.** Ninguna cifra publicada
tocada; el Atlas no se tocó.

Scripts nuevos: `polos_p065_union_y_clases.py`, `dataset_bares_notables.py`,
`places_criterio_destino.py`, `documentar_inferencia_tipo2.py`.
Informe principal: `outputs/BARRIDO_CIUDAD_2026-08/borrador_polos/P065_UNION_Y_CLASES.txt`.

---

## 1 · P065 · se intentó rehacer y **no se pudo: queda entero**

Se le corrió la curva de continuidad de Belgrano con la regla declarada antes de mirar —el umbral
más alto que todavía deja dos partes nombrables—. Da 55 m, con dos partes de 104 y 89 locales.
**Y esa partición falla la verificación**, que se apoyaba en cosas que no intervinieron en elegir
el umbral:

- el bloque **S1 (70 locales, 5,96 loc/ha): 0 de 70 recapturados**;
- el bloque S2 (59): 42 de 59;
- las dos partes se llevan sólo el **53,5 %** de los locales, y el resto queda en **28 esquirlas**.

El diagnóstico es la columna que agregué al barrido, `pct_locales_en_esas_componentes`:
**P065 no se parte en dos lóbulos, estalla en muchos pedazos.** Es tejido continuo mirado con lupa.
La diferencia con Belgrano se ve en la tabla: allá las tres componentes se llevaban todos los
puntos. Y por eso S1 no aparece en ninguna parte — a 55 m ya está roto por debajo del mínimo.

Se aplica entonces la otra mitad de la instrucción: **P065 se revierte y queda entero.** No hay
estructura estable que lo divida, y ahora está medido en vez de supuesto.

> **Nota sobre Palermo, porque la expectativa era razonable.** Soho, Hollywood y Las Cañitas son
> estructura real, pero **no están en P065**. P065 tiene 361 locales a 4,40 loc/ha y se estira hacia
> Chacarita y Colegiales —por eso cubría R19—. Los polos de Palermo con la estructura nombrada son
> **P091** (728 locales, 7,88 loc/ha) y **P078** (585, 5,70), que nunca fueron candidatos a partir
> porque no son grandes ni ralos. Si hay que buscar esas tres, hay que buscarlas ahí.

**R19 volvió** (12,3 % → 28,5 %, encontrada) por el camino correcto: porque el polo no tenía que
haberse partido, no porque se lo remendara hasta que diera.

## 2 · El precio final

| etapa | polos | locales en polos | fuera de todo polo | ha | zonas encontradas |
|---|---:|---:|---:|---:|---:|
| 1 · sin partir | 118 | 13.564 | 43,4 % | 3.745 | 15 |
| 2 · `leaf` en los 10 | 127 | 12.500 | 47,9 % | 3.058 | 13 |
| **3 · P065 entero + unión 100 m** | **124** | **12.688** | **47,1 %** | **3.144** | **14** |

Control §5: 124 de 124 envolventes pasan. **R15 Devoto sigue sin encontrarse** (10,7 %) y eso es lo
esperado: es una pregunta sobre su perímetro, no sobre la partición. Anotada como **zona con
perímetro a revisar en la V3**.

## 3 · Las clases pasan de tres a dos, y esta vez la robustez pasa

`concentración extendida` (< 4,58 loc/ha) y `concentración` (el resto). **El corte no se
recalculó**: es el mismo que ya había aguantado la prueba.

| clase | polos | locales | ha | rango |
|---|---:|---:|---:|---|
| concentración | 71 | 7.034 | 995 | 4,70 – 21,64 |
| concentración extendida | 53 | 5.654 | 2.149 | 0,98 – 4,47 |

Corriendo la misma prueba que tumbó a las tres clases —recalcular sin el Relevamiento, el 41 % de
los puntos— con el corte reescalado por la mediana (4,58 → 2,79): **118 de 124 conservan clase
(95,2 %), Rand ajustado 0,814**, contra 0,391 de las tres clases. Pasa el umbral de 0,60 que las
tres no pasaban.

Reporto también la otra lectura, que da mal y no hay que taparla: **refiteando Jenks a k = 2 sobre
la escala nueva, el Rand cae a 0,128**, porque con cola larga Jenks pone el corte donde más
varianza saca y produce clases desbalanceadas (92/32). Es el **mismo defecto** que tumbó a las tres
clases, ahora sobre el único corte que queda. La lectura que decide es la del corte reescalado,
porque el esquema adoptado es un umbral fijo y no un refit — pero las dos están escritas.

El diagnóstico del Rand quedó completo en el informe anterior y repetido en éste: las dos hipótesis
descartadas (dependencia del Relevamiento, p = 0,51; cercanía al corte, p = 0,45) y la explicación
de Fisher–Jenks.

**En la ficha: densidad exacta primero, clase después.** Y la añada al lado de la clase, no en otra
tabla.

## 4 · Unión a 100 m · 2 aplicadas de 35 evaluadas

39 pares a menos de 100 m. **4 excluidos por ser piezas del mismo padre** (P072-4+P072-3,
P072-4+P072-5, P072-6+P072-7, P018-2+P018-1) y 35 evaluados.

> **Esa exclusión hay que señalarla porque no estaba pedida y cambia el resultado.** En la primera
> corrida la unión reunía piezas de P072 que la partición acababa de separar. El motivo es que la
> prueba de estabilidad de la unión corre `leaf` sobre los puntos de las dos piezas solas, mientras
> que la partición lo corrió sobre el padre entero, con sus 694 puntos de tejido incluidos. Son dos
> preguntas distintas sobre conjuntos distintos, y la del padre tenía la información completa. La
> unión sirve para juntar polos independientes que quedaron cerca, **no para re-litigar una
> partición ya resuelta con mejores datos**.

De los 35: **2 unen** (P090+P089 y P101+P099), 33 no. De los rechazos, **15 por continuidad** —a
100 m siguen siendo dos o más cuerpos— y **18 por estabilidad** —`leaf` los volvería a separar—.

La no-transitividad quedó demostrada en la columna `evaluado_como`: cuando un par tocaba un objeto
ya unido, lo que se evaluó fue el objeto entero (`P091+P090+P089`, `P087+P090+P089`), no el polo
suelto. Ninguno de esos pasó.

## 5 · Dataset de Bares Notables

`outputs/BARRIDO_CIUDAD_2026-08/dataset_bares_notables/` — CSV, GeoJSON y README.

**92 de los 95 geocodificados con USIG (96,8 %)**, 0 fuera de los 48 barrios. Los 3 sin resolver no
tienen dirección en Wikidata y quedan en el dataset sin punto. Reparto: San Nicolás 16, Monserrat
11, San Telmo 6, Recoleta 5, Retiro 5, Palermo 5.

Los **dos recaudos van en cada fila del CSV, en el GeoJSON y en el README**, no en una nota aparte:
el listado no es exhaustivo, y «Bar Notable» es una declaratoria —acto administrativo por valor
patrimonial— y **no una calificación de calidad**.

No se usaron las coordenadas de Wikidata (procedencia Wikipedia → Google Maps según el wiki de
OSM). Se geocodificó desde la dirección postal con el normalizador oficial de USIG, **filtrando
`cod_partido = caba`** para no traer homónimos del conurbano.

> Un bug que vale la pena registrar: la limpieza de direcciones convertía **«Esquiu 1393»** en
> « y iu 1393», porque el reemplazo de `esq.` / `esquina` por « y » no tenía límite de palabra. La
> fila salía «sin resolver» y parecía un problema del servicio. Con eso y dos casos más
> (rangos `1148/50/52`, colas sin punto) el resuelto pasó de 93,7 % a 96,8 %.

## 6 · Places · criterio propuesto y dry-run · **pendiente de autorización**

`outputs/BARRIDO_CIUDAD_2026-08/places_criterio_destino/` — **0 requests ejecutados.**

**El marco cambió, y con él para qué sirve la corrida.** Como no habrá denominador externo nunca, la
propuesta es que **Places ocupe ese lugar** con lo único que sabe hacer: sonda de descubrimiento en
los barrios donde la base está más flaca. Si aun ahí aparece poco, la cobertura queda acotada por
arriba con un número propio; si aparece mucho, el faltante queda localizado y medido. Hoy no
tenemos ninguna de las dos.

**Criterio, declarado antes de mirar qué barrios salían:** intersección del tercio más bajo de dos
indicadores internos — `aporte_otras_fuentes` (≤ 1,39) y `pct_padron` (≤ 24,7 %). Intersección y no
unión: flojo en un solo indicador puede ser una rareza de esa fuente; flojo en los dos significa
menos patas independientes.

| barrio | aporte | % padrón | locales núcleo | añada | requests |
|---|---:|---:|---:|---:|---:|
| Villa del Parque | 1,17 | 23,2 | 337 | 2022 | 30 |
| Villa Luro | 1,32 | 21,7 | 207 | 2022 | 22 |
| Villa Gral. Mitre | 1,36 | 23,6 | 208 | 2022 | 18 |
| San Cristóbal | 1,31 | 23,2 | 250 | 2024 | 18 |
| Paternal | 1,30 | 19,8 | 126 | 2023 | 9 |

```
barrios: 5 · celdas: 53 · REQUESTS: 97 (cota ×3: 291)
agosto quedaría en 403 de 5.000 (8,1 %) · peor caso ×3: 597 (11,9 %)
```

**Pido autorización para ejecutar 97 requests de Text Search sobre esos 5 barrios.** Sin
autorización explícita no se ejecuta nada.

Las dos lecturas del resultado están escritas antes de correr, para que sea falsable: fracción
nueva baja → la base está más completa de lo que podíamos afirmar; fracción nueva alta → hay
faltante, localizado y con tamaño. Y el límite que no se relitiga: **Places aporta descubrimiento,
no vigencia.** El resultado no entra a la base sin una decisión aparte: su licencia no es
redistribuible y por eso la base se construyó sin él.

---

## Decisiones de Diego, registradas con fecha · 2026-08-06

Quedan asentadas acá para que no vuelvan a aparecer como preguntas abiertas.

1. **El uso de Google Places como fuente es decisión de Diego, tomada por él y vigente.**
2. **La edición técnica NO queda congelada.** Pasa a ser el documento extenso del método, que
   explica todo al pie de la letra, sin límite de extensión. Contenido comprometido: Places
   nombrado, el 22,6 % de asientos replicados con la prueba catastral, los factores de captura
   contra las dos bases, la parejidad de cobertura, el método de clustering con sus curvas, y los
   precedentes de unión y partición. **Pendiente de redacción.**
3. **El Atlas nombrará bares notables y establecimientos Michelin**, con dos recaudos escritos en el
   documento: el listado no es exhaustivo, y un bar notable es una declaratoria y no una
   calificación de calidad.
4. **«No se identificaron zonas en el extremo sur de la Ciudad» se corrige en la V3.** Textual de
   Diego: «creo que ni se buscó». El borrador encuentra 10 polos y 1.000 locales en comunas 8 y 9,
   9 de 10 pasando las tres pruebas de artefacto.
5. **La V3 reemplaza a la V2. No conviven.**
6. **Unión de polos: umbral 100 m**, no transitiva y con prueba de estabilidad sobre cada unión
   candidata evaluada sobre el resultado unido.
7. **Bares Notables se publican como dato abierto** (hecho, §5).
8. **Sin pedidos fuera de la Dirección.** Se caen APRA, AGIP, INDEC, Estadística y Censos, la
   consulta a la AGC y el convenio con plataformas.

### Las tres consecuencias, declaradas y no pendientes

- **Nunca habrá denominador externo de completitud.** Escrito en el **§10 del esquema** (reescrito) y
  **adentro de las cuatro láminas del mapa**, en caja propia. La parejidad queda apoyada sólo en dos
  proxies internos, y la conclusión se escribe siempre «con los indicadores disponibles», nunca «se
  verificó». El §11 quedó tachado con la nota de baja.
- **El diccionario de códigos del Relevamiento se sigue infiriendo.** Documentado valor por valor en
  `INFERENCIA_TIPO2_RELEVAMIENTO.md`, generado desde el mapeo vivo para que no se desincronice: 14
  valores al núcleo en 7 categorías con su frecuencia real, 2 al ampliado, 13 descartes explícitos
  con su motivo, las tres asignaciones que no salieron directas del padrón (`CONFITERIA`,
  `CERVECERIA`, `SUSHI`) y cómo auditarlo sin el diccionario.
- **La consulta a la AGC queda preparada y sin mandar**, con la nota de baja al principio del
  archivo. El 22,6 % de asientos replicados se sigue tratando con criterio propio, sin confirmación
  del organismo que los publica, y eso va escrito donde se use ese número.

## Lo que espera decisión

1. **Autorización de los 97 requests de Places** sobre los 5 barrios.
2. **R15 Devoto**, anotada como zona con perímetro a revisar en la V3.
3. **La redacción del documento extenso del método** (decisión 2), que no está empezada.
4. Siguen de antes: R04 Puerto Madero, las tres zonas en E3, la cláusula ODbL de OSM en legal, el
   visto de Patricia sobre el pasaje 5, la lista de Bares Notables contra la normativa, Foursquare.

## Trampas encontradas hoy

- **Una operación puede deshacer en silencio a la anterior.** La unión a 100 m reunía piezas que la
  partición acababa de separar, porque las dos pruebas corren sobre conjuntos de puntos distintos.
  Nada fallaba; el resultado simplemente volvía atrás.
- **Un conteo de componentes no distingue una partición de un estallido.** «Dos partes nombrables»
  parecía estructura en P065; con la fracción de locales que esas partes se llevan, era la mitad del
  polo repartida en 28 esquirlas.
- **Un `\b` que falta borra un dato y parece un problema del servicio.** `esq` matcheaba adentro de
  «Esquiu» y la fila salía sin geocodificar.
- **Cuando dos maneras de medir lo mismo dan resultados opuestos, van las dos.** El corte reescalado
  da Rand 0,814 y el refit de Jenks da 0,128. Publicar sólo la primera sería elegir la que conviene;
  publicar sólo la segunda sería medir el defecto de Jenks y llamarlo defecto de las clases.
