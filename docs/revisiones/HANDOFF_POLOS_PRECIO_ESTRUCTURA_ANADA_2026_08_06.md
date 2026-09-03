# HANDOFF · El precio de la partición, la estructura de los seis y la añada · 2026-08-06

Continúa `HANDOFF_POLOS_DENSIDAD_ATRIBUTO_2026_08_06.md`. Rama `mercados-gastronomicos-v2`.
**Sin commit. Google Places: 0 requests.** Ninguna cifra publicada tocada; el Atlas no se tocó.

Script: `scripts/barrido_ciudad/polos_particion_anada_estructura.py`.
Informe: `outputs/BARRIDO_CIUDAD_2026-08/borrador_polos/PARTICION_ESTRUCTURA_Y_ANADA.txt`.

---

## 1 · El precio de la partición: **la mitad se acepta, la otra mitad no**

Antes del desglose, un dato que ya estaba medido y cambia la pregunta: **ninguno de los 1.064
quedó suelto por caer bajo el mínimo.** `leaf` no produjo un solo fragmento por debajo de 40 en
los cuatro padres. Los 1.064 son puntos que el corte profundo etiquetó como **ruido**, no piezas
amputadas.

| padre | barrio | piezas | sueltos | % entre las piezas | dist. mediana a una pieza | bloques ≥ 40 |
|---|---|---:|---:|---:|---:|---:|
| P018 | Villa Devoto | 2 | 109 | 0,9 % | 570 m | **0** |
| P025 | Monte Castro | 2 | 73 | 12,3 % | 275 m | **0** |
| P065 | Palermo | 2 | 188 | 15,4 % | 187 m | **2** |
| P072 | Belgrano | 7 | 694 | 63,5 % | 140 m | **4** |

Los seis grupos de 40 o más, con su posición —que es lo que los separa en dos casos distintos:

| grupo | locales | loc/ha | centro entre las piezas | dist. a una pieza |
|---|---:|---:|---|---:|
| P072-S3 | 239 | 3,92 | **sí** | 127 m |
| P072-S4 | 80 | 5,36 | **sí** | 242 m |
| P072-S2 | 79 | 5,80 | **sí** | 133 m |
| P072-S1 | 68 | 4,14 | **sí** | 134 m |
| **P065-S1** | **70** | **5,96** | **no** | **292 m** |
| **P065-S2** | **59** | **5,39** | **no** | **165 m** |

**P018 y P025: tejido puro.** Cero grupos nombrables, sueltos dispersos a 275–570 m de las piezas.
La partición hizo lo correcto y esos 182 locales engrosan el «fuera de todo polo».

**P072: tejido también, aunque grande.** Los cuatro grupos tienen el centro ADENTRO de la cáscara
que envuelve a las siete piezas, entre el 34 % y el 100 % de sus puntos entre ellas. Es la matriz
de baja densidad que P072 venía encadenando: exactamente lo que la partición quiso sacar. Que el
mayor tenga 239 locales no lo convierte en polo — lo convierte en una mancha grande y rala, que
es lo que P072 era entero.

**P065 Palermo: ahí sí hay error de partición.** Sus dos grupos caen AFUERA de la cáscara, a 165 y
292 m, con **5,96 y 5,39 locales/ha — por encima de la densidad mediana de todos los polos (5,03)**.
No son tejido: son dos concentraciones que la partición dejó caer.

### Y las dos zonas perdidas: **ninguna es referencia dispersa**

| ref | zona | familia | registro | ha | quién la cubría | antes → después |
|---|---|---|---|---:|---|---|
| R15 | Devoto | **Polo** | observado | 479 | P018 | 39,3 % → 10,7 % |
| R19 | Federico Lacroze por tramos | **Eje o corredor** | declarado | 90 | **P065** | 38,9 % → 12,3 % |

Las dos tienen nombre e identidad documental, así que por el criterio que fijaste las dos obligan
a revisar la partición que las rompió. Pero **no son el mismo caso**:

- **R19 la rompió P065**, que es el mismo polo que perdió los dos bloques coherentes. Es un solo
  problema, no dos: la partición de P065 está mal y se lleva puesta la zona y los bloques juntos.
- **R15 la rompió P018**, cuya partición es limpia por el desglose. R15 es otra cosa: **479 ha
  declaradas como un único «Polo» cuyo soporte es «119 puntos observados E-PLACES (Z08)»** — un
  perímetro derivado de geometría de observación, no de oferta medida. Su densidad por perímetro
  es 0,88 loc/ha. Que un polo de 205 ha partido en dos ya no le cubra el 25 % de 479 ha no dice
  gran cosa sobre la partición; dice algo sobre el perímetro de R15, y eso no lo decide un borrador.

**Recomendación:** aceptar la partición de P018, P025 y P072; **revertir o rehacer la de P065**.
Con P065 entero vuelven sus 188 sueltos, vuelve R19 por encima del umbral, y el precio total baja
de 1.064 a 876 locales.

## 2 · Los seis: **curva plana, y el instrumento lo demuestra**

Barrido de continuidad, el mismo método con que se decidió Belgrano —unir puntos a menos de un
umbral, contar componentes conexas y tamaños—. Umbrales 40, 55, 70, 80, 120, 160, 200, 250, 300 m
(los seis últimos son los de la corrida territorial V3; los tres primeros se agregan porque aquel
barrido corría sobre clusters candidatos y éste sobre puntos sueltos).

Componentes de 40 locales o más, por umbral:

```
                 40   55   70   80  120  160  200  250  300
LOS SEIS
  P004  (141)     0    0    0    0    1    1    1    1    1
  P005  (100)     0    0    0    0    1    1    1    1    1
  P021  (262)     0    1    1    1    1    1    1    1    1
  P027  (189)     0    0    0    0    1    1    1    1    1
  P043  (161)     0    0    0    1    1    1    1    1    1
  P046  (291)     0    1    1    1    1    1    1    1    1
CONTROLES POSITIVOS (los que sí se partieron)
  P018  (244)     0    0    1    2    2    1    1    1    1
  P025  (162)     0    0    1    1    2    1    1    1    1
  P065  (361)     2    2    1    1    1    1    1    1    1
  P072 (1314)     2    5    2    2    1    1    1    1    1
```

**Los seis son planos: nunca aparece más de una parte nombrable, en ningún umbral.** Los cuatro
controles llegan a 2, 2, 2 y 5 en los mismos umbrales. El instrumento distingue estructura de
ausencia de estructura, así que la curva plana **no es «leaf no los partió»: es una medición de que
no tienen estructura interna.**

Los seis quedan enteros, clasificados como referencia dispersa / concentración extendida, con la
densidad declarada en la ficha.

## 3 · La añada contra la densidad: **no contamina, pero apareció otro problema**

Límite estructural, dicho antes que cualquier resultado: la añada está **anidada dentro del
barrio** —un barrio tiene una sola añada—, así que año y lugar no se pueden separar por diseño.
Por eso la prueba decisiva no compara años: saca la fuente rotativa entera y mira si el resultado
aguanta.

### 3.1 · La añada NO contamina las clases

- **eta² = 0,037**: la añada explica el 3,7 % de la varianza de la densidad. Sacando entero el
  Relevamiento —el 41 % de los puntos— baja a 3,2 %. El 96 % de la variación ocurre **dentro** de
  cada cohorte.
- **Las tres clases aparecen en las tres cohortes** (2022: 8 C / 3 B / 1 A · 2024: 17 / 27 / 18).
- **Los cortes propios de 2022 y 2024 caen a menos de medio local/ha de los globales** (2022:
  4,82 y 8,12 · 2024: 5,11 y 8,86 · globales: 4,58 y 8,48). Sólo 2023 se desvía, por un extremo
  de 21,6 que Jenks aísla.
- **Spearman entre la densidad con y sin Relevamiento: 0,975.** El orden de los polos aguanta.

**La clase C no es «relevada en 2022».**

### 3.2 · Pero las clases altas no son robustas, y no es por la añada

Con *k* fijo en 3, sólo 82 de 127 polos conservan clase (Rand ajustado 0,391 — el umbral declarado
era 0,60 y **falla**). El desglose es lo que importa:

- **clase C «concentración extendida» — 51 de 51 conservan la clase. ESTABLE.**
- clase B — 29 de 50. · **clase A «concentración densa» — 2 de 26. NO ESTABLE.**

Probé las tres explicaciones candidatas y las dos primeras no son:

- ¿los que cambian dependen más del Relevamiento? **No** — 40,9 % contra 40,8 %, Mann–Whitney
  p = 0,51. Todos los polos dependen de esa fuente en proporción parecida.
- ¿estaban pegados a una frontera? **No de manera decisiva** — 0,179 contra 0,228, p = 0,45.
- **La que sí es:** los que cambian son los densos (densidad mediana 8,84 contra 3,99), y todo el
  movimiento va hacia abajo. Fisher–Jenks minimiza varianza y la varianza la domina la cola alta;
  al sacar el 41 % de los puntos la cola se adelgaza y el corte superior se va de 1,59× la mediana
  a 3,29× la mediana. **La frontera entre las clases densas se mueve con la forma de la cola, no
  con el territorio.** Es la consecuencia concreta de que la distribución no tenga huecos.

### 3.3 · Consecuencia operativa, más acotada que «abandonar las clases»

- **«Concentración extendida» se puede usar.** Es el descriptor que aguanta el cambio de conjunto
  de puntos, y es justamente el que hace falta para los seis del §2 y para los polos del sur.
- **La frontera entre «media» y «densa» no se puede usar para decidir sobre un polo en
  particular.** En la ficha va la densidad exacta primero y la clase después.

---

## Lo que espera decisión

1. **P065.** Es el único error de partición del lote: dos bloques coherentes afuera de la cáscara
   y R19 rota. Revertir su partición o rehacerla con otro criterio.
2. **R15 Devoto.** Perímetro de 479 ha con soporte de 119 puntos de Places. No es una pregunta
   sobre la partición; es una pregunta sobre la zona, y no la decide un borrador.
3. **Si con P065 revertido se acepta el precio restante** (876 locales, todos tejido medido).
4. Sigue abierto de antes: Puerto Madero / R04, las tres zonas en E3, Places en pausa, el
   diccionario de códigos a Estadística y Censos, la cláusula ODbL, la nota a la AGC.

## Trampas encontradas hoy

- **Un conteo de bloques sin su posición se lee al revés.** «6 bloques coherentes perdidos» parecía
  seis polos perdidos; con la posición son cuatro de tejido y dos reales, y los dos reales están
  todos en el mismo padre.
- **Un veredicto compuesto puede fallar por la razón equivocada.** La primera versión de la prueba
  de añada exigía que la regla del GVF reeligiera el mismo *k*; sacar el 41 % de los puntos corre
  la escala, el *k* cambió, y el veredicto dijo «las clases no aguantan» cuando Spearman era 0,975.
  La comparación tiene que ir a *k* igual.
- **Un umbral que falla no autoriza a elegir otro: obliga a diagnosticar.** El Rand de 0,391 falló
  el umbral declarado, y las dos explicaciones intuitivas (dependencia de la fuente, cercanía al
  corte) resultaron falsas al medirlas. La verdadera —la cola gobierna el corte superior— es un
  defecto del método de corte, no de los datos, y sólo apareció porque el umbral falló.
- **«No lo partió» y «no tiene qué partir» son afirmaciones distintas**, y sólo se pueden separar
  con controles positivos. Sin las cuatro curvas escalonadas al lado, las seis planas no probaban
  nada.
