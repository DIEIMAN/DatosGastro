# HANDOFF · La densidad como atributo, la partición de los encadenados y las pruebas · 2026-08-06

Continúa `HANDOFF_BORRADOR_POLOS_CIUDAD_2026_08_06.md`, vigente en todo lo que no se contradiga acá.
Rama `mercados-gastronomicos-v2`. **Sin commit. Google Places: 0 requests. El total de agosto sigue
en 306.** Ninguna cifra publicada se tocó; el Atlas no se tocó; `CRITERIOS_LECTURA_POLIGONIZACION.md`
**no se editó a propósito**: es una pre-registración y editarla después de ver el mapa la anularía.

Ejecutadas las seis órdenes. Salidas en `outputs/BARRIDO_CIUDAD_2026-08/borrador_polos/`,
informe completo en `POLOS_ATRIBUTOS_Y_PRUEBAS.txt`. Script nuevo:
`scripts/barrido_ciudad/polos_atributos_clases.py`.

---

## Lo que cambió, en una línea

**La densidad dejó de ser compuerta: cada polo lleva ahora su densidad, su superficie, su clase y
la añada del Relevamiento que lo sostiene.** Y la partición de los encadenados salió cara: el mapa
quedó en 127 polos y el 47,9 % de los locales fuera de todo polo, contra 43,4 % antes.

---

## 1 · Densidad y superficie como atributos, con clases por cortes naturales

Método: Fisher–Jenks (óptimo exacto en una dimensión, por programación dinámica), con la regla
declarada de tomar el **k más chico con GVF ≥ 0,85**. Da k = 3, con cortes en **4,58 y 8,48
locales/ha**.

| clase | polos | locales | ha | rango |
|---|---:|---:|---:|---|
| A · concentración densa | 26 | 2.106 | 197 | 8,7 – 21,6 |
| B · concentración media | 50 | 5.231 | 831 | 4,7 – 8,4 |
| C · concentración extendida | 51 | 5.163 | 2.030 | 1,0 – 4,5 |

### El contraste con los huecos dio NEGATIVO, y es el dato

Se buscó el hueco antes de aceptar el número, como pide el §2 del criterio. **No hay hueco.** El
salto mediano entre dos polos consecutivos es 0,065 locales/ha y el mayor salto interior es 0,392:
la distribución es continua. El hueco de R07 existía porque R07 era un caso extremo —0,03 contra
15,6—; acá no hay nada parecido.

**Consecuencia declarada antes de usar las clases: los cortes son óptimos, no naturales.** La clase
hace el trabajo que se le pide —dejar de llamar igual a dos cosas con 16× de diferencia— pero no
puede fingir que su frontera es una frontera del territorio. Un polo a 4,5 y uno a 4,7 son
prácticamente lo mismo y caen en clases distintas. Por eso la densidad exacta viaja al lado de la
clase, en la tabla y en el pie del mapa.

### Y una advertencia de lectura que hay que dar antes que la tabla

Las 22 publicadas se midieron con la misma base y se clasificaron con los mismos cortes, de dos
maneras: por su perímetro publicado y por la envolvente cóncava de sus propios puntos (la
comparable). Medidas del modo que más las favorece, **19 de las 22 caen en la clase C**.

Eso **no** dice que las zonas del Atlas sean ralas. Un polo del borrador y una zona publicada no son
el mismo tipo de objeto: el polo es un **núcleo extraído por densidad** —el clustering descarta el
43 % de los puntos antes de dibujar— y la zona publicada es un **perímetro trazado sobre un área**.
Comparar sus densidades es comparar un barrio con su cuadra más cargada. Sirve para una sola cosa, y
es la que se le pidió: mostrar que un piso calibrado sobre los polos del borrador no se puede
trasladar a las zonas publicadas sin borrarlas casi todas.

## 2 · Sensibilidad del piso absoluto · informativa, no decide nada

| piso | polos que sobreviven | % locales que caen | comunas que pierden todo | **zonas publicadas que caerían** |
|---:|---:|---:|---:|---:|
| 2,0 | 106 de 118 | 10,5 | 0 | **11** |
| 4,0 | 74 | 46,0 | 2 | **16** |
| 6,0 | 44 | 68,4 | 5 | **20** |

Ese es el tamaño de la pregunta: **el piso más bajo de los tres ya borra la mitad de las zonas que
la Dirección publicó.** Con 4,0 sobreviven seis (R01, R02, R03, R05, R06, R18); con 6,0 sobreviven
dos: R02 Corrientes y R18 Esmeralda–Paraguay.

## 3 · Los 10 encadenados, partidos con criterio declarado de antemano

- **Quiénes:** superficie > percentil 90 (75,4 ha) y densidad < mediana (5,03). Da los 10. El
  control declarado —¿algún polo que contiene entera una zona publicada quedó fuera de la
  población?— dio 0: P072 es el único que contiene una zona entera y está adentro de los 10.
- **Cómo:** se rehace el clustering sobre los puntos del propio polo con método `leaf` en vez de
  `eom`. Es el corte más profundo del **mismo árbol de densidad**; no introduce ningún parámetro
  nuevo ni ninguna distancia elegida a ojo. `min_cluster_size` y `min_samples` no se movieron.
- **Sobras:** no se rescatan. Se anotan.

### Resultado

**Se partieron 4 de 10** → 13 piezas. Los 6 que no se partieron (P046, P021, P027, P043, P004, P005)
no tienen dos núcleos de 40 adentro: `leaf` no los separa.

**Y lo que costó, que hay que ver antes que el resultado:** partir con `leaf` no recorta los bordes,
deshace la mancha y se queda con los núcleos. **1.064 locales dejaron de estar en un polo.**

| | antes | después |
|---|---:|---:|
| polos | 118 | 127 |
| locales en algún polo | 13.564 | 12.500 |
| **fuera de todo polo** | **43,4 %** | **47,9 %** |
| superficie | 3.745 ha | 3.058 ha |
| zonas publicadas encontradas | 15 | 13 |

R15 Devoto (39,3 % → 10,7) y R19 Federico Lacroze (38,9 % → 12,3) dejaron de estar encontradas. No
es un problema del cotejo: es el precio del criterio, y el criterio estaba declarado.

### El caso testigo: P072 sí hizo lo que se partió para hacer

P072 (1.314 locales, 440,7 ha, 2,98 loc/ha) se partió en 7 piezas. Las piezas juntas cubren el
**62,8 %** de R05 Belgrano —la mancha entera cubría 99,2 %—, y aparecieron dos núcleos más densos que
cualquier cosa de la corrida anterior: P072-7 a **21,6 loc/ha** y P072-6 a **18,9** (el máximo de los
118 era 15,2). Ya no hay ningún polo que contenga entera una zona publicada con otro perímetro.

## 4 · Las tres pruebas de artefacto sobre los 10 polos del sur

Se corrieron sobre los 127 para tener con qué comparar, y se reportan **polo por polo y prueba por
prueba** para los 10 de comunas 8 y 9 (1.000 locales).

```
4.1 fuente     10 de 10 pasan   ningún polo pasa del 70 % de un solo grupo; el máximo es 51 %
4.2 grilla     10 de 10 pasan   rectangularidad 0,30–0,46 (umbral 0,90); perímetro en ejes 0–28 %
                                (umbral 50); sobre borde interno de barrio 0–27,6 % (umbral 30)
4.3 cobertura   9 de 10 pasan   falla sólo P003 Villa Riachuelo, cobertura 2,02 contra p10 2,30
```

**Las tres juntas: 9 de 10.**

Tres cosas del diseño de la prueba que hay que saber para leerla:

- **4.2 no tenía grilla contra la cual cruzar.** Ninguna de las siete fuentes de la base se bajó por
  celdas: F01/F02 y el Relevamiento son volcados administrativos completos, y OSM, Overture y ATP se
  recortaron por el `bbox` de la Ciudad y después por barrios. Places, que sí se consulta por
  celdas, no está en la base. Así que la prueba se corre por la **firma geométrica** que una grilla
  dejaría igual, más el único borde de recorte que existe: el límite entre barrios.
- **El perímetro de la Ciudad se excluye del borde.** En el sur los polos tocan el Riachuelo y la
  General Paz, que son territorio real. Contarlos habría dado un falso positivo justo en los diez
  polos que se estaban examinando.
- **4.3 es de una cola, y así estaba escrito antes del mapa**: «un cluster en un barrio donde la
  base es notoriamente floja vale menos». Cobertura alta no es riesgo de artefacto. La primera
  corrida la implementó de dos colas y marcaba a P002 Villa Soldati por estar **mejor** cubierto que
  el p90 — un falso positivo puro. Se informan las dos lecturas (una cola: 111 de 127 pasan; dos
  colas: 101) para que se vea qué cambia.

## 5 · La añada del Relevamiento, polo por polo

Cada polo lleva `anada_relevamiento`, `anada_mixta`, la mezcla completa y
`pct_puntos_del_relevamiento`. Reparto: **12 polos sobre 2022, 53 sobre 2023, 62 sobre 2024**; 29 de
127 tienen añada mixta. Ningún polo depende del Relevamiento en más del 52 % de sus puntos (mediana
41 %).

**Y el mapa mostró algo que la tabla no:** la añada no está repartida al azar. El Relevamiento rota
por zonas, así que el año y el lugar viajan juntos — y con ellos la densidad:

| añada | C extendida | B media | A densa |
|---|---:|---:|---:|
| 2022 | 8 | 3 | 1 |
| 2023 | 26 | 20 | 7 |
| 2024 | 17 | 27 | 18 |

**Comparar el centro denso con la periferia extendida es, además, comparar 2024 contra 2023 y 2022.**
Los dos efectos están confundidos y con estos datos no se separan. No invalida el mapa; sí invalida
cualquier lectura del tipo «tal zona creció respecto de tal otra».

La advertencia va **adentro de las cuatro láminas**, en caja propia, no en el pie ni en el nombre del
archivo. Lámina nueva `borrador_polos_anada.png` con el gradiente geográfico a la vista.

## 6 · Las siete zonas, con su explicación

Evaluadas sobre el conjunto de la **etapa 1**, que es el cotejo que está sobre la mesa; lo que la
partición les hizo va en columna aparte.

La regla de E1 **no usa la densidad de la zona**: casi todas las publicadas caen en la clase baja
por su perímetro editorial, así que una regla por densidad les ponía E1 a las siete y no distinguía
nada. E1 se asigna cuando **la mayoría (≥ 50 %) de los locales de la zona sí está adentro de algún
polo** y esos polos ocupan menos de un cuarto de la superficie publicada.

| ref | zona | % locales en polo | % zona cubierta | explicación |
|---|---|---:|---:|---|
| R07 | Costanera Norte | 53,7 | 16,1 | **E1** perímetro más ancho que la concentración |
| R16 | Donado–Holmberg | 52,9 | 14,9 | **E1** |
| R22 | Villa Pueyrredón | 58,1 | 9,3 | **E1** |
| R21 | La Paternal | 45,7 | 13,2 | **E2** cobertura del barrio 2,30 = p10 |
| R20 | García del Río | 29,5 | 24,7 | **E3** queda como pregunta |
| R04 | Puerto Madero | 33,6 | 9,3 | **E3** |
| R11 | Boulevard Caseros | 31,7 | 5,5 | **E3** |

- **R20 anotado así y no rescatado:** quedó a **0,3 puntos** del umbral de 25 %. El umbral se fijó
  antes de correr y no se mueve para alcanzarla.
- **R04 sigue pendiente aparte:** el Relevamiento declara 52 parcelas comerciales activas en todo
  Puerto Madero. Verificar el Relevamiento ahí antes de concluir nada sobre la zona.
- **Divergencia anotada porque no coincide:** la lectura previa daba por descontado que cuatro
  (R21, R22, R04, R16) eran perímetros más anchos que su concentración. Medido, E1 le toca a tres
  y no a esas cuatro. **La regla no se ajustó para reproducir la expectativa.**
- **Casos al filo, marcados:** R21 queda en E2 por 45,7 % contra un umbral de 50 % y por una
  cobertura que empata con el p10 en el segundo decimal. Un criterio editorial podría leerla del
  otro lado con el mismo derecho.

## 7 · El control aleatorio, ahora obligatorio en el script

Escrito en `borrador_polos_ciudad.py`, no en un documento: `SORTEOS_CONTROL` con guarda de mínimo 3,
`ablacion()` que no emite una tabla sin la columna de control, y `lectura_ablacion()` que **se niega
a redactar** la lectura de una fila que no traiga su control. No hay bandera para saltearlo; para
bajarlo hay que borrar el bloque a mano y dejar el rastro en el diff.

---

## Lo que espera decisión

1. **La partición, a la luz de su precio.** El criterio se cumplió, pero costó 1.064 locales,
   dos zonas publicadas encontradas y 4,5 puntos del ya alto porcentaje fuera de todo polo. Si ese
   precio es aceptable es decisión de Diego, no del script.
2. **Los 6 encadenados que `leaf` no partió**, entre ellos P046 (291 locales, 114,7 ha, 2,54) y
   P021 (262, 77,9, 3,36). Siguen siendo manchas grandes y flojas y el criterio declarado no los
   tocó.
3. **Las tres zonas en E3** (R20, R04, R11): quedan como preguntas para la Dirección, no como
   conclusiones del borrador.
4. **Puerto Madero:** verificar el Relevamiento antes de concluir nada sobre R04.
5. **Places sigue en pausa**, sin criterio de destino. Nada de esto lo cambió.
6. Siguen abiertos: la cláusula ODbL de OSM en legal, el visto de Patricia sobre el pasaje 5, la
   lista de Bares Notables contra la normativa, Foursquare, la nota a la AGC, y el **diccionario de
   códigos a Estadística y Censos**, que sube de prioridad: si la clasificación de `TIPO2` que
   inferimos está corrida, el mapa se mueve.

## Lo que no se tocó

Ninguna cifra publicada. Ningún PDF. Los JSON congelados de las dos ediciones. El pipeline público
F01–F05. `PROTECTED_SURFACES.yaml`. Las 22 envolventes editoriales (se leyeron, no se escribieron).
La base (`local.csv` no se regeneró). `CRITERIOS_LECTURA_POLIGONIZACION.md`, a propósito.
**Google Places: 0 requests.**

## Trampas encontradas hoy

- **Una regla de clasificación puede aplicarse a todos y no clasificar nada.** La primera versión de
  E1 usaba la densidad de la zona y le puso E1 a las nueve no encontradas. Una regla que nunca
  discrimina se lee como un resultado y no lo es.
- **Un umbral de dos colas cuenta como hallazgo el ancho de su propia banda.** Una banda p10–p90
  deja afuera al 20 % por construcción, así que «26 de 127 fallan» medía la banda, no el riesgo.
- **El borde de la Ciudad no es un borde de consulta.** La prueba de grilla habría marcado a los
  polos del sur por tocar el Riachuelo y la General Paz, que es exactamente donde no había que
  equivocarse.
- **Partir no recorta: deshace.** `leaf` sobre el mismo árbol no le saca los bordes a la mancha, se
  queda con los núcleos y manda el resto a disperso. El criterio era correcto y el efecto es enorme;
  las dos cosas a la vez.
- **Comparar la densidad de un núcleo extraído con la de un perímetro dibujado siempre da a favor
  del núcleo.** Sin decirlo, la tabla de clases parece un juicio sobre las zonas publicadas.
- **Una fuente rotativa confunde el tiempo con el espacio.** No basta con declarar la añada por
  polo: el Relevamiento rota por zonas, así que la añada está correlacionada con la densidad y con
  la comuna, y ninguna comparación entre polos es limpia.
